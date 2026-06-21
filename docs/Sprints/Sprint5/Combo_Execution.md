# SPRINT 5 — COMBO MESH (EXECUTION step-by-step)

> ⚠️ v2.0 (21/06/2026) — TÁI THIẾT KẾ DIỆN RỘNG. Đọc hết trước khi thực thi.
> Sprint 5 mở rộng từ "combo cơ bản" thành HỆ THỐNG COMBO LIBRARY đầy đủ:
> dialog lưu (tên/folder/thumbnail/tags/mô tả), folder tree, drag-drop,
> replace cả cụm, tích hợp group nhiều cấp, material RowName.
> Mọi quyết định cũ (D1–D4) bị thay bởi mục QUYẾT ĐỊNH v2.0 bên dưới.

**Phiên bản:** 2.1 | **Ngày:** 21/06/2026 | Lighting_Mnger UE5.5.4
**Tác giả:** Fable 5 (v1.0) + Q&A Sonnet 4.6 (v1.1) + Kiến trúc 21/06 (v2.0) + Review patch (v2.1)
**Đối tượng đọc:** model thực thi (Opus/Sonnet) + cuhoang. Tuân thủ `09_AI_Implementation_Rules.md`.
**Làm TỪNG TASK, mỗi task có test, xong báo cuhoang.**

> **Lịch sử thay đổi lớn:**
> - v1.1 (12/06): sửa T2 bước 3 selection-only, 8 class vars, guard double-click, trace 2 tầng.
> - v1.2 (19/06): tách BP_ComboManager khỏi InputManager (xem DEVIATIONS.md).
> - v2.0 (21/06): tái thiết kế diện rộng — nhóm cha SourceComboID, material RowName,
>   drag-drop tái dùng, replace cả cụm, dialog đầy đủ. T2 nested fix (C0). C++ mở rộng (C1).
> - v2.1 (21/06): patch review kiến trúc — C0→LCA (tránh lưu thừa cả room), C1 ghi nhận
>   ItemView+persist, C2→3-phase bắt buộc, C3 folder-create, C5 BuildFolderTree nguồn mới,
>   C8 DragOp_ComboCard+On Drop routing, C9 capture-after+rollback toast.

---

## 0. ĐIỀU KIỆN TIÊN QUYẾT
1. Gate 1 xong: B1 ĐÃ CHẾT, `bIsRestoring` hoạt động, `SpawnFurnitureCopy` = đường spawn DUY NHẤT.
2. Sprint D xong: `RowName` trên BP_FurnitureActor + S_FurniturePlacement; `BP_FurnitureItemView`; DisplayPage 2 mode; inventory single-instance.
3. Plugin biết compile C++ (đã qua D.T3).
**Nếu B1 còn sống: DỪNG.**

## 0b. PHẠM VI

| Tính năng | S5 | B3a | B3b | Sau |
|---|---|---|---|---|
| Lưu bộ đồ + thumbnail + tên/tags | ✅ | | | |
| Thư viện combo cá nhân, folder tree, search | ✅ | | | |
| Spawn combo, undo, save scene | ✅ | | | |
| Nested group trong combo | ✅ | | | |
| Drag-drop combo (ghost 1 đại diện) | ✅ | | | |
| Replace cả cụm combo | ✅ | | | |
| Đăng chợ, người khác tải | | ✅ | | |
| Giá tiền, mua, entitlement | | | ✅ | |
| Preview 3D, AI gợi ý | | | | backlog |
| Combo chứa đồ user import | schema chừa sourceType | | | Sprint G |

## QUYẾT ĐỊNH KIẾN TRÚC v2.0 (thay D1–D4 cũ)

**A. BP_ComboManager — Actor RIÊNG** chứa toàn bộ combo logic (tách từ 19/06).
   Nhận data qua PARAM, KHÔNG hard ref BP_FurnitureInputManager (R2).
   InputManager lo guard + tính Center + lấy SelectedActors → gọi ComboManager qua param.

**B. Cụm combo = 1 GROUP CHA** (bỏ ý tưởng ComboInstanceID).
   - `S_GroupData` thêm field `SourceComboID : String` (default "").
     Group user tạo tay → "". Group cha cụm combo → = ComboID gốc.
   - Spawn combo → wrap toàn cụm vào 1 group cha (SourceComboID=ComboID),
     chứa các group con remap bên trong.
   - Hệ quả: click 1 món chọn cả cụm, move/rotate cả cụm, edit nested —
     tất cả kế thừa miễn phí từ group system. Không viết mới.

**C. Save combo lưu NESTED ĐẦY ĐỦ** (sửa lỗi selection-only của T2 — xem C0).
   - T2 hiện gom group bằng ForEach SelectedActors→GET GroupID → chỉ bắt group LÁ,
     mất group cha trung gian → combo nested bị làm phẳng.
   - SỬA (C0): dùng LCA (group chung gần nhất của các actor được chọn) thay vì leo root tuyệt đối —
     tránh lưu thừa cả room khi chỉ chọn 1 nhánh. Chi tiết thuật toán xem C0.
     Đồ lẻ (GroupID=="") → groupToken="" (thuộc group cha combo khi spawn).

**D. Material override lưu ROWNAME** (mức A — combo portable cho cloud B3).
   - Actor + snapshot + EMS GIỮ path (local, không đổi — tránh regression).
   - CHỈ combo file đổi: `materialOverrides` = array RowName (không phải path).
   - Cần C++ helper `FindMaterialRowNameByPath(Path)→RowName` (reverse lookup
     từ DT_MaterialInstancesCatalog). Save dùng reverse; spawn dùng forward
     (Get Data Table Row→path→apply, pattern ApplyMaterial sẵn có).
   - Edge case: material ngoài catalog → reverse fail → lưu "" → spawn skip slot.

**E. Drag-drop combo TÁI DÙNG khung furniture** (DragOperation→WBP_DragOverlay→
   On Drag Over snap→On Drop). Khác biệt DUY NHẤT: ghost = 1 mesh ĐẠI DIỆN
   (Items[0].RowName), KHÔNG ghost cả N mesh. On Drop → SpawnComboByID(ComboID,
   DropLocation). Đây THAY thế D4 cũ: drop tại cursor thay vì giữa màn hình.

**F. Replace combo = thay CẢ CỤM** (không phải 1 đổi 1 như replace mesh).
   Chọn 1 actor → leo group cha (SourceComboID!="") → đọc SourceComboID +
   FolderPath của combo → bật replace mode → folder tree combo navigate tới
   FolderPath đó (pattern StartReplaceMode mesh) → card hiện nút replace →
   click → destroy toàn member group cha → SpawnComboByID(comboMới, Center cũ).
   Rotation v1 reset 0 (giữ rotation cụm cũ = backlog).

---

## 1. SCHEMA JSON v1 (v2.0 — thêm folderPath, materialOverrides = RowName)

```json
{
  "version": 1,
  "comboID": "c_7f3a...",
  "name": "Bộ phòng khách Bắc Âu",
  "description": "...",
  "tags": ["sofa", "bắc âu"],
  "category": "LivingRoom",
  "folderPath": "LivingRoom/BacAu",
  "createdAt": "2026-07-01T10:00:00Z",
  "appVersion": "2.0",
  "items": [{
      "rowName": "SM_Sofa_01",
      "sourceType": "catalog",
      "relLocation": {"x":0,"y":0,"z":0},
      "relRotation": {"pitch":0,"yaw":90,"roll":0},
      "scale": {"x":1,"y":1,"z":1},
      "surfaceType": "Floor",
      "materialOverrides": ["", "MI_Blue_01", ""],
      "groupToken": "g1"
  }],
  "groups": [
    {"token":"g1","name":"Bộ sofa","parentToken":""},
    {"token":"g2","name":"Bàn trà","parentToken":"g1"}
  ]
}
```

**Quy tắc schema:**
- Token = định danh nội bộ file (g1, g2...). Spawn 2 lần → 2 bộ GroupID GUID mới → không dính nhau.
- `relLocation` = ActorLocation − Center, trục world, không xoay.
- `sourceType` chừa sẵn cho Sprint G (user import).
- Tên file = comboID GUID (không dùng Name — mìn M10 ký tự lạ).
- **`folderPath`** (v2.0): dùng cho folder tree combo + navigate khi replace (quyết định F).
- **`materialOverrides`** (v2.0): array **RowName** của material (vd `"MI_Blue_01"`), KHÔNG còn full path `/Game/...`.
  Lý do: portable cloud (quyết định D). Snapshot/EMS actor vẫn giữ path — chỉ combo file đổi.
  Material ngoài catalog → reverse lookup fail → lưu "" → spawn skip slot (không crash).
- Schema version: field mới thêm → file cũ load OK (FJsonObjectConverter ignore field thừa). Backward-compatible 1 chiều.
- Lưu: `<ProjectSavedDir>/Combos/<comboID>.json` | Thumb: `.../Combos/Thumbs/<comboID>.png`.

---

## 2. C++ STRUCTS & SERIALIZER — T1 ✅ DONE (21/06/2026)

### ✅ Q1 (macro API)
Mở FilterLibrary.h hiện có, copy macro ở dòng class declaration (dạng `FURNITURETOOLKIT_API`). Compile fail do macro sai: dán nguyên error cho cuhoang, không tự đoán. Gợi ý: macro = tên module trong `.Build.cs` (dòng `public class XXX`) + `_API`.

**`ComboTypes.h`** (đặt cạnh FurnitureFilterLibrary trong Public/):
```cpp
#pragma once
#include "CoreMinimal.h"
#include "ComboTypes.generated.h"

USTRUCT(BlueprintType)
struct FComboItemData {
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString RowName;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString SourceType = TEXT("catalog");
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector  RelLocation  = FVector::ZeroVector;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FRotator RelRotation  = FRotator::ZeroRotator;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector  Scale        = FVector::OneVector;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString  SurfaceType  = TEXT("Floor");
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FString> MaterialOverrides;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString  GroupToken;
};

USTRUCT(BlueprintType)
struct FComboGroupData {
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Token;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Name;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString ParentToken;
};

USTRUCT(BlueprintType)
struct FComboData {
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32   Version = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString ComboID;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Name;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Description;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FString> Tags;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Category;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString CreatedAt;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString AppVersion;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FComboItemData>  Items;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FComboGroupData> Groups;
};
```
> ⚠️ C1 sẽ thêm `FolderPath` vào FComboData — recompile sau C1.

**`ComboSerializer.h`:**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ComboTypes.h"
#include "ComboSerializer.generated.h"

UCLASS()
class FURNITURETOOLKIT_API UComboSerializer : public UBlueprintFunctionLibrary {
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Combo")
    static FString ComboToJson(const FComboData& Combo);

    UFUNCTION(BlueprintCallable, Category="Combo")
    static bool JsonToCombo(const FString& Json, FComboData& OutCombo);

    UFUNCTION(BlueprintCallable, Category="Combo")
    static bool SaveStringToFile(const FString& FilePath, const FString& Content);

    UFUNCTION(BlueprintCallable, Category="Combo")
    static bool LoadStringFromFile(const FString& FilePath, FString& OutContent);

    // ⚠ Q4: Trả TÊN FILE, không kèm path. Caller nối: GetCombosDir + "/" + FileName
    UFUNCTION(BlueprintCallable, Category="Combo")
    static TArray<FString> ListJsonFilesInDir(const FString& DirPath);

    UFUNCTION(BlueprintPure, Category="Combo")
    static FString GetCombosDir();   // <ProjectSaved>/Combos

    UFUNCTION(BlueprintCallable, Category="Combo")
    static bool DeleteFileAtPath(const FString& FilePath);
};
```
> ⚠️ C1 sẽ thêm `FindMaterialRowNameByPath` vào ComboSerializer — recompile sau C1.

**`ComboSerializer.cpp`:**
```cpp
#include "ComboSerializer.h"
#include "JsonObjectConverter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"

FString UComboSerializer::ComboToJson(const FComboData& Combo) {
    FString Out;
    FJsonObjectConverter::UStructToJsonObjectString(Combo, Out, 0, 0);
    return Out;
}
bool UComboSerializer::JsonToCombo(const FString& Json, FComboData& OutCombo) {
    return FJsonObjectConverter::JsonObjectStringToUStruct(Json, &OutCombo, 0, 0);
}
bool UComboSerializer::SaveStringToFile(const FString& FilePath, const FString& Content) {
    return FFileHelper::SaveStringToFile(Content, *FilePath,
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);  // tiếng Việt OK
}
bool UComboSerializer::LoadStringFromFile(const FString& FilePath, FString& OutContent) {
    return FFileHelper::LoadFileToString(OutContent, *FilePath);
}
TArray<FString> UComboSerializer::ListJsonFilesInDir(const FString& DirPath) {
    TArray<FString> Files;
    IFileManager::Get().FindFiles(Files, *(DirPath / TEXT("*.json")), true, false);
    return Files;
}
FString UComboSerializer::GetCombosDir() {
    return FPaths::ProjectSavedDir() / TEXT("Combos");
}
bool UComboSerializer::DeleteFileAtPath(const FString& FilePath) {
    return IFileManager::Get().Delete(*FilePath);
}
```

**Build.cs:** thêm `"Json", "JsonUtilities"` vào PrivateDependencyModuleNames.

**Bảng lỗi compile thường gặp:**
| Error chứa | Fix |
|---|---|
| `JsonObjectConverter.h: No such file` | Thiếu JsonUtilities trong Build.cs |
| `unresolved external ... FJsonObjectConverter` | Thiếu Json + JsonUtilities (link step) |
| `GENERATED_BODY` đỏ cả file | Chưa generate project files / thiếu `#include "...generated.h"` CUỐI includes |
| `BlueprintType` error | Quên `USTRUCT(BlueprintType)` trước struct |
| Module API macro error | Copy macro sai — xem lại FilterLibrary.h |
Vẫn fail: dán nguyên error cho cuhoang, không đoán.

**TEST T1:** Level BP test tạm — `Make FComboData` (1 item, name="Bộ sofa") → `ComboToJson` → Print → `JsonToCombo` → Print Name. Kết quả: JSON đúng, tiếng Việt không vỡ, round-trip khớp. Xóa test node sau pass.
✅ DONE 21/06/2026

---

## 3. TASKS v2.0 — C0–C10

> Format: mục tiêu + I/O + điểm mấu chốt. Chi tiết node sinh khi execute từng task, không ghi sẵn.

---

### C0 — Sửa SaveComboFromSelection: lưu nested đúng via LCA (BP_ComboManager)
**Mục tiêu:** Bước 3 hiện chỉ gom group lá → nested bị phẳng. Patch dùng LCA (group chung gần nhất).
**I/O:** Input = SelectedActors (param). Output = FComboData với Groups đúng cây (không thừa, không thiếu).

**Thuật toán LCA (thay selection-only):**
```
CLEAR SaveCombo_LeafIDs; CLEAR SaveCombo_ComboGroups

// Bước 1: thu leafGroupIDs duy nhất từ selection
ForEach SelectedActors → GET GroupID → GroupID != "" → unique ADD SaveCombo_LeafIDs
← đồ lẻ (GroupID=="") → lưu item với groupToken="" (thuộc group cha combo khi spawn, không mất)

// Bước 2: tính LCA của tập leafGroupIDs
// Nếu 1 leaf → LCA = leaf đó.
// Nếu nhiều leaf → WalkUpUntilParent từng leaf → build path-to-root cho mỗi leaf
//   → LCA = group sâu nhất có mặt trên PATH-LÊN-ROOT của MỌI leaf.
// Nhiều cây không chung ancestor → nhiều LCA riêng (parentToken="" trong combo).
// ⚠️ Helper LCA N-node cần viết mới. Chi tiết node sinh lúc execute C0.
// ⚠️ +1 buổi code/test so với ROOT approach — đã chấp nhận (đúng ngữ nghĩa "lưu cái được chọn").

// Bước 3: với mỗi LCA-root → GetGroupsInHierarchy(lcaID) gom subtree
ForEach lcaRoots → GetGroupsInHierarchy(lcaID) → ForEach g:
    NOT Contains(SaveCombo_ComboGroups) → ADD (tránh trùng)
// Chỉ lấy subtree từ LCA XUỐNG, không leo thêm.
// parentToken của LCA-root = "" (gốc trong combo). Các group con giữ quan hệ cha-con thực.
```
> Dùng `GetGroupsInHierarchy` + `WalkUpUntilParent` (Sprint 4 §9 — đã build sẵn, KHÔNG viết lại). Chỉ viết thêm helper tính LCA.

**MaterialOverrides** (cùng task C0): thay `copy array` bằng:
```
ForEach MaterialOverrides slot (path):
  FindMaterialRowNameByPath(path) → RowName → ADD (rỗng nếu fail → skip khi spawn)
```
> ⚠️ C1 phải xong TRƯỚC C0 để có node `FindMaterialRowNameByPath`.

**TEST C0 (3 case — PASS hết mới tiếp):**
- Case A: chọn actor trong 1 sub-group của room lớn → JSON groups = sub-group đó + con của nó (KHÔNG lấy root cả room).
- Case B: chọn actor từ 2 nhánh khác nhau cùng root → LCA = group gần nhất chứa cả 2 nhánh.
- Case C: combo nested 3 cấp (root→sub→leaf) → JSON groups đủ 3 entry, parentToken đúng cây.
→ **Báo cuhoang + dán JSON cả 3 case.**

---

### C1 — Nền data + C++ mở rộng
**Mục tiêu:** Chuẩn bị data foundation cho toàn bộ sprint.

> ✅ **ĐÃ XONG (old T3 — KHÔNG làm lại):** BP_ComboItemView (Object, 5 var: ComboID/Name/
> ThumbPath/ItemCount/Tags), AllComboViews array trong WBP_FurnitureInventory,
> LoadComboLibrary (Custom Event, đã chạy "Loaded: 3 combos"), bind OnComboLibraryChanged.
> C4/C5/C6 dùng lại trực tiếp — không tạo mới.

**Các việc (thứ tự bắt buộc):**

1. **FComboData thêm FolderPath** — mở `ComboTypes.h`, thêm:
   `UPROPERTY(EditAnywhere, BlueprintReadWrite) FString FolderPath;`
   Recompile. Backward-compat: file cũ không có field → default "".

2. **FindMaterialRowNameByPath** — thêm vào `ComboSerializer.h/.cpp`:
   ```
   UFUNCTION(BlueprintCallable, Category="Combo")
   static FString FindMaterialRowNameByPath(const UDataTable* MaterialDT,
                                             const FString& Path);
   ```
   Logic: loop DT_MaterialInstancesCatalog, tìm row có MaterialPath==Path → return RowName.
   Không tìm thấy → return "". ⚠️ Xác nhận tên field thực tế trong DT trước khi code.

3. **S_GroupData thêm SourceComboID** — xác nhận S_GroupData là BP struct hay C++ struct.
   Nếu BP struct: mở editor thêm field String `SourceComboID` default "".
   Nếu C++: thêm UPROPERTY tương ứng + recompile.
   **Persistence SourceComboID:**
   - Runtime undo/redo: SourceComboID tự đi theo Groups (snapshot copy cả struct S_GroupData) → KHÔNG cần bump snapshot version. Không làm gì thêm.
   - EMS disk: VERIFY load save cũ (không có field) → SourceComboID default "" không crash. Chỉ thêm migration NẾU test thấy mất dữ liệu — không assume trước.

4. **BP_UserPreferencesSave thêm 2 array:**
   `FavoriteComboIDs : Array<String>` | `RecentComboIDs : Array<String>` (SaveGame).

**TEST C1:** Make FComboData với FolderPath="Test/Abc" → ToJson → FromJson → Print FolderPath = "Test/Abc". S_GroupData có SourceComboID field trong editor. Load save cũ → không crash, SourceComboID="". Compile xanh.
→ **Báo cuhoang.**

---

### C2 — SpawnComboByID(ComboID, SpawnLocation) ⭐ TRÁI TIM SPRINT
**Mục tiêu:** Custom Event trong BP_ComboManager. Spawn toàn cụm thành group cha.
**I/O:** Input = ComboID (String), SpawnLocation (Vector). Output = dispatch OnComboSpawned(Array<BP_FurnitureActor>).
**Điểm mấu chốt:**
- Guard `Cmb_bSpawnInFlight` đầu event (double-click).
- Bước 0b: EditModeStack.Length > 0 → ExitEditModeFull.
- **3 PHASE bắt buộc — KHÔNG gộp Phase 1+2 (gộp = cha chưa có GUID khi con cần ParentGroupID → remap sai cây nested):**
  - **Phase 1 (map GUIDs):** ForEach token trong Groups → GenerateGroupID → build FULL map `TokenToNewGUID`. PHẢI hoàn tất trước Phase 2.
  - **Phase 2 (build groups):** GenerateGroupID → ParentGroupGUID (group cha combo, SourceComboID=ComboID, ParentGroupID=""). ForEach group: Make S_GroupData (ParentGroupID = map[parentToken]; group cấp cao nhất → ParentGroupGUID) → ADD Groups. SyncGroupsToContainer.
  - **Phase 3 (spawn actors):** ForEach item → SpawnFurnitureCopy (ĐƯỜNG SPAWN DUY NHẤT). GroupID = map[groupToken]; đồ lẻ (groupToken="") → GroupID = ParentGroupGUID. Material: Get Data Table Row(DT_MaterialInstancesCatalog, RowName) → path → apply.
- Warm async cache TRƯỚC spawn (pattern T5 v1.1, giữ nguyên).
- Sau spawn: dispatch `OnComboSpawned(SpawnedActors)` → InputManager lắng nghe → SelectActors + CaptureSnapshot("SpawnCombo").
- Class vars BẮT BUỘC với prefix `Cmb_`. CLEAR đầu event + End Play (R4).

**TEST C2 (bộ test chặt — PASS hết mới tiếp):**
```
1. Spawn combo 5 món nested 2 cấp → group cha tồn tại, SourceComboID = ComboID gốc
2. Spawn combo lần 2 → 2 cụm ĐỘC LẬP: move cụm 1, cụm 2 đứng yên. Print GroupID → khác
3. Undo → cả cụm biến 1 lần. Redo → quay lại đủ + group cha nguyên
4. Spawn khi Edit Mode → tự thoát rồi spawn
5. RowName bậy trong JSON → spawn N-1 + toast. Không crash
6. Save EMS → Load → combo + group cha + SourceComboID nguyên vẹn
7. Spawn 20 món → không khựng quá 0.5s
```
→ **Báo cuhoang + bảng PASS/FAIL 7 case.**

---

### C3 — WBP_SaveComboDialog
**Mục tiêu:** Dialog nhập thông tin combo trước khi lưu. Thay hardcode "MyCombo" hiện tại.
**I/O:** Output = (ComboName, FolderPath, Description, Tags) qua dispatcher OnDialogConfirmed.
**Các thành phần:**
- TXT_ComboName (EditableText), TXT_Description (EditableText), TXT_Tags
- **Folder path — bắt buộc hỗ trợ cả 2 chế độ:**
  (a) Nhập text tự do (vd "LivingRoom/BacAu") — bắt buộc vì lần đầu lưu cây combo còn trống.
  (b) Chọn từ dropdown/picker cây combo hiện có — khi thư viện đã có folder.
  Validate: trim whitespace, chuẩn hóa "\\" → "/", không cho ký tự đặc biệt.

- Thumbnail preview: chụp runtime (CaptureComboThumbnail sau khi confirm) hoặc import file.
  Search node "Import File as Texture2D" TRƯỚC. Không có → Plan B: chỉ chụp runtime, ghi DEVIATIONS.
- BTN_Confirm → Broadcast OnDialogConfirmed → đóng dialog → BP_ComboManager.SaveComboFromSelection(params)
- BTN_Cancel → đóng

**TEST C3:** mở dialog, nhập tên + folder + tags, confirm → file JSON có đúng tên + folderPath + tags.
→ **Báo cuhoang.**

---

### C4 — WBP_ComboCard
**Mục tiêu:** Card combo trong tile view, layout riêng với badge số món.
**Interface:** IUserObjectListEntry. Variables: `ComboItem (BP_ComboItemView)`, `InventoryRef`.
**Điểm mấu chốt:**
- Thumbnail: search "Import File as Texture2D" trước. Không có → icon 🧩. Ghi DEVIATIONS.
- BTN_SpawnCombo "📥 Đặt vào scene": gọi C2 tại điểm giữa màn hình (fallback khi không drag).
- BTN_Info ℹ: mở WBP_ComboDetailPopup (C7).
- BTN_Delete 🗑: xóa file json + thumb → LoadComboLibrary → refresh tab.
- Badge "×N món" hiển thị ItemCount.
- `CTV_ComboCard` riêng (KHÔNG tái dùng CTV_FurnitureCard) — lý do xem DEVIATIONS.md 19/06 [SCOPE].

**TEST C4:** 2 card đúng tên + số món. Xóa 1 → còn 1, file biến. Nút đặt → spawn đúng vị trí.
→ **Báo cuhoang.**

---

### C5 — Folder tree tab Combo
**Mục tiêu:** Browse combo theo FolderPath, tái dùng WBP_TreeNode + WBP_ChipTag.
**I/O:** Input = AllComboViews (list đã load). Output = FilteredComboViews theo folder chọn.
**Điểm mấu chốt:**
- Build folder tree từ FolderPath của AllComboViews. **KHÔNG dùng BuildFolderTree furniture** (nó đọc DT_FurnitureCatalog, không đọc combo array). Cần: overload C++ nhận `Array<FString> FolderPaths` → build tree, HOẶC build BP-level từ AllComboViews. Quyết định lúc C5 sau khi xem signature hàm cũ.
- Tái dùng WBP_TreeNode + WBP_ChipTag (đã có IsPathActive + UpdateFolderHighlights từ Sprint D).
- Filter combo theo CurrentFolderPath (pattern FilterByFolderPath furniture).
- BTN_Tab_Combo cạnh BTN_Tab_Material trong WBP_FurnitureInventory.
- Bind OnComboLibraryChanged → LoadComboLibrary ở Event Construct.

**TEST C5:** 3 combo ở 2 folder khác nhau → click folder → chỉ thấy combo đó. Highlight folder đúng.
→ **Báo cuhoang.**

---

### C6 — Favorite + Recent combo
**Mục tiêu:** Clone pattern furniture. Dùng ComboID thay MeshPath.
**I/O:** FavoriteComboIDs + RecentComboIDs từ BP_UserPreferencesSave (C1 đã thêm).
**Điểm mấu chốt:**
- BTN_Favorite trên WBP_ComboCard: toggle ComboID trong FavoriteComboIDs.
- Recent: thêm vào RecentComboIDs khi spawn (trong OnComboSpawned listener của InputManager).
- Tab Recent/Favorite combo: filter AllComboViews theo array IDs.

**TEST C6:** favorite 1 combo → reload → vẫn favorite. Spawn → xuất hiện trong Recent.
→ **Báo cuhoang.**

---

### C7 — WBP_ComboDetailPopup + Info button
**Mục tiêu:** Popup hiển thị chi tiết combo (tên/số món/tags/mô tả/thumbnail/list món).
**Điểm mấu chốt:**
- Widget riêng, KHÔNG tái dùng WBP_DetailPopup (combo khác field hoàn toàn).
- Hiển thị danh sách Items: ListView hoặc VerticalBox động với tên từng món (DT lookup VieName).
- Thumbnail hiển thị tương tự WBP_ComboCard (Plan B: icon 🧩).

**TEST C7:** click Info trên card → popup đúng tên/tags/số món/danh sách.
→ **Báo cuhoang.**

---

### C8 — Drag-drop combo
**Mục tiêu:** Kéo card combo ra scene, ghost 1 mesh đại diện, thả → spawn tại cursor (quyết định E).
**Điểm mấu chốt:**
- **DragDropOperation_ComboCard MỚI** (KHÔNG extend FurnitureCard — tránh đụng furniture đang chạy). Chứa field `ComboID : String`.
- **WBP_DragOverlay.On Drop — thêm branch routing:**
  - Cast to `DragDropOperation_ComboCard` → True: SpawnComboByID(ComboID, DropLocation).
  - Cast to `DragDropOperation_FurnitureCard` → True: đường furniture cũ (giữ nguyên).
  - ⚠️ Hiện On Drop chỉ có nhánh FurnitureCard — thả ComboCard mà không thêm branch = crash hoặc spawn sai.
- **Ghost mesh:** async load mesh `Items[0].RowName` lúc drag bắt đầu (trễ 1-2 frame — chấp nhận). Nếu test tệ (giật/laggy trên máy yếu) → fallback thumbnail 2D làm ghost. KHÔNG preload trước (48 item/trang = nặng). Quyết sau khi sờ thực tế.
- KHÔNG cần trace 2 tầng (C2 dùng DropLocation trực tiếp).

**TEST C8:** kéo card combo → ghost xuất hiện → thả → combo spawn đúng chỗ thả. Kéo FurnitureCard vẫn hoạt động bình thường (regression).
→ **Báo cuhoang.**

---

### C9 — Replace combo
**Mục tiêu:** Thay cả cụm combo bằng combo khác (quyết định F).
**Điểm mấu chốt:**
- Entry: right-click actor thuộc cụm combo → CB_ReplaceCombo (enable khi actor có GroupID với SourceComboID!="").
- Leo group cha: GetGroupRoot(actor.GroupID) → RootGID → FindGroupData(RootGID) → SourceComboID + FolderPath.
- Mở replace mode combo: navigate folder tree combo tới FolderPath.
- **Sequence thực thi (thứ tự BẮT BUỘC):**
  1. Guard `Cmb_bSpawnInFlight` đầu event.
  2. CalculateCenter(GetAllDescendantActors(RootGID)) → lưu `Center` (TRƯỚC khi destroy).
  3. Destroy GetAllDescendantActors(RootGID) + RootGID group.
  4. SpawnComboByID(newComboID, Center) → đợi OnComboSpawned callback.
  5. **Spawn thành công:** CaptureSnapshot("ReplaceCombo"). Recent tự cập nhật (OnComboSpawned → C6 listener).
  6. **Spawn thất bại** (JSON lỗi / RowName không tồn tại): KHÔNG capture + toast "Thay thế thất bại — Undo để khôi phục" (Undo restore combo cũ từ history qua RestoreSnapshot destroy+respawn).
- Rotation v1 reset 0 (giữ rotation = backlog).
- ⚠️ KHÔNG capture "PreReplace" riêng — state cũ đã ở history trước bước destroy.

**TEST C9:**
- Case A: spawn combo A → replace bằng B → cụm A biến, B ở Center cũ → Undo → A quay lại.
- Case B: replace với combo có RowName bậy → toast, scene không có lỗ trống.
→ **Báo cuhoang.**

---

### C10 — Regression + Docs
**Mục tiêu:** Verify toàn hệ thống + cập nhật tài liệu.
**Regression:**
- R1-R8 Sprint D
- 7 case C2 + 4 case C8 + 2 case C9
- Scene save/load: group + SourceComboID nguyên vẹn sau restart
- T6 pivot rotation: verify có TRÙNG group transform không — nếu trùng → bỏ T6, ghi DEVIATIONS

**Docs (version + ngày + giờ + phút):**
- `BP_ComboManager.md` (tạo mới): vars Cmb_, events C0/C2, dispatchers
- `BP_FurnitureInputManager.md` → v2.2: guard CB_SaveCombo, listen OnComboSpawned
- `WBP_FurnitureInventory.md` → v2.7: tab Combo, C5 folder tree, C6 Fav/Recent
- `09_AI_Implementation_Rules.md`: thêm node xác nhận thật (RotateVector, CombineRotators, FindLookAtRotation...)
- `Session_State.md`, `PROGRESS.md`, `DEVIATIONS.md`
→ **Báo cuhoang. SPRINT 5 HOÀN TẤT.**

---

## 4. TÍCH HỢP HỆ THỐNG CŨ

**NHÓM A — tự động (combo=group+actor thường):**
Box select, edit mode nested, replace mesh từng đồ, gizmo/nudge cả nhóm.
Không viết gì — kế thừa miễn phí vì combo dùng group system.

**NHÓM B — C2 lo:**
- Undo/redo: CaptureSnapshot sau mỗi thao tác; snapshot đã lưu Groups+GroupID+MaterialPaths. SourceComboID tự vào snapshot (field của S_GroupData).
- Material apply: qua SpawnFurnitureCopy.
Không sửa hệ thống undo/material.

**NHÓM C — nợ/quyết:**
- Material RowName chỉ combo (mức A): snapshot/EMS giữ path, combo file đổi sang RowName — tránh regression actor thường.
- Copy/paste cả cụm mất group: clipboard không lưu GroupID — v1 để vậy, backlog.
- Scene save group persistence: verify C10.
- T6 pivot: có thể thừa nếu group transform xử lý đủ — verify C10 rồi quyết.

---

## 5. SỔ RỦI RO (12 tình huống + Plan B)
| # | Tình huống | Triệu chứng | Plan B |
|---|---|---|---|
| M1 | CombineRotators sai thứ tự | Đồ rotation sẵn xoay xong trôi | Đảo 2 input — chỉ có 2 khả năng |
| M2 | Async double-fire | Spawn gấp đôi | Guard Cmb_bSpawnInFlight + AND callback |
| M3 | Phase 1+2 gộp thành 1 vòng | Cây nested gãy (cha chưa có GUID khi con cần ParentGroupID) | Tách 3 phase như C2 — Phase 1 PHẢI xong trước Phase 2 |
| M4 | 2 lần spawn dính | Move cụm 1, cụm 2 chạy | Kiểm SET GroupID có qua TokenToNewID không |
| M5 | Export Render Target fail | Không có .png | Icon 🧩 + tên. Ghi DEVIATIONS |
| M6 | Import File as Texture2D không tồn tại | Node không thấy | Icon 🧩. Backlog C++ FImageUtils |
| M7 | JSON tiếng Việt vỡ | Tên "???" | ForceUTF8WithoutBOM đã có. Kiểm app đọc encoding |
| M8 | Trace miss (fallback nút spawn) | Combo lơ lửng | Fallback 2 tầng trong C2 bước điểm đặt |
| M9 | Combo 50 món khựng | Đứng hình | Warm cache bước 4. Vẫn khựng → limit ≤30 món ở C0 |
| M10 | Tên combo ký tự lạ | File không tạo | Tên file = GUID. Đã xử lý |
| M11 | Catalog đổi RowName sau lưu | Item thiếu | C2 bước 3 skip + toast. RowName = hợp đồng — ghi Data.md |
| M12 | Kẹt C++ không có Fable | Compile error lạ | Tra bảng T1 → fail 3 lần: gác, gom hỏi Opus 1 lần với error+file+dòng |
| M13 | SourceComboID mất sau Undo/Load | Replace không nhận ra cụm | Verify S_GroupData trong snapshot capture/restore; xem C10 |

---

## 6. ĐỊNH NGHĨA DONE SPRINT 5 v2.0
✅ Lưu combo (nested group đầy đủ + material RowName) → dialog tên/folder → card tab 🧩 → folder tree → spawn 2 lần độc lập với group cha SourceComboID → drag-drop tại cursor → replace cả cụm → undo/redo/save/load nguyên vẹn → regression PASS → docs cập nhật.
❌ Marketplace / giá tiền / đăng tải = B3, không thuộc Sprint 5.

---

## 7. BACKLOG

**Deferred v1 (chốt 21/06 — không làm Sprint 5):**
- Filter-by-tag: tags v1 chỉ decorative (hiện info popup). Filter theo tag = deferred Sprint 6.
- Giữ rotation cụm cũ khi replace (C9 v1 reset 0 — giữ rotation = backlog).
- Copy/paste cả cụm giữ group (clipboard không lưu GroupID — v1 để vậy).
- Material RowName cho actor/snapshot/EMS (v1 chỉ combo file đổi; snapshot/EMS giữ path — tránh regression).

**Backlog kỹ thuật:**
- "Chụp lại bìa combo" — nút set thumbnail từ góc camera tự chọn (B3 page người bán).
- Ghost preview N mesh khi drag (C8 ghost 1 đại diện — full N ghost = backlog).
- Limit ≤30 món validate khi lưu (nếu M9 xảy ra trong test).
- C++ load PNG runtime FImageUtils (nếu M6 xảy ra — Import File as Texture2D không tồn tại).

---

## Lịch sử
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 12/06/2026 | Fable 5: schema v1, C++ đầy đủ, toán pivot, remap 2 vòng, 12 rủi ro |
| 1.1 | 12/06/2026 | Hợp nhất Q&A Sonnet 4.6: sửa T2 bước 3 (selection-only), 8 class vars, guard double-click, trace 2 tầng, CTV riêng, thumbnail đồng bộ, path join Q4, giải thích Q10 race |
| 1.2 | 19/06/2026 | Thêm DEVIATION block đầu file: BP_ComboManager tách riêng khỏi InputManager; luật dịch 6 điểm |
| 2.0 | 21/06/2026 | Tái thiết kế diện rộng: QUYẾT ĐỊNH v2.0 (A-F), schema thêm folderPath + materialOverrides→RowName, TASKS đổi C0–C10, thêm TÍCH HỢP HỆ THỐNG CŨ, group cha SourceComboID, C++ mở rộng C1, drag-drop C8, replace cả cụm C9 |
| 2.1 | 21/06/2026 | Patch review kiến trúc: C0→LCA (tránh lưu thừa cả room), C1 ghi nhận ItemView+LoadComboLibrary đã xong+persist note, C2→3-phase bắt buộc, C3 folder-create mode, C5 BuildFolderTree nguồn mới, C8 DragOp_ComboCard+On Drop routing+ghost decision, C9 sequence+capture-after+rollback toast, BACKLOG deferred v1, M3 cập nhật |
