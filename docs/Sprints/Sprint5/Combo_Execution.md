# SPRINT 5 — COMBO MESH (EXECUTION step-by-step)

> ⚠️ v2.0 (21/06/2026) — TÁI THIẾT KẾ DIỆN RỘNG. Đọc hết trước khi thực thi.
> Sprint 5 mở rộng từ "combo cơ bản" thành HỆ THỐNG COMBO LIBRARY đầy đủ:
> dialog lưu (tên/folder/thumbnail/tags/mô tả), folder tree, drag-drop,
> replace cả cụm, tích hợp group nhiều cấp, material RowName.
> Mọi quyết định cũ (D1–D4) bị thay bởi mục QUYẾT ĐỊNH v2.0 bên dưới.

**Phiên bản:** 2.4 | **Ngày:** 24/06/2026 | Lighting_Mnger UE5.5.4
**Tác giả:** Fable 5 (v1.0) + Q&A Sonnet 4.6 (v1.1) + Kiến trúc 21/06 (v2.0) + Review patch (v2.1) + Sprint5_Plan_v1.1 (v2.3)
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
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString FolderPath;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString AuthorID;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Visibility = TEXT("Private");
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FComboItemData>  Items;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FComboGroupData> Groups;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combo")
    FVector BoundingBoxExtent = FVector::ZeroVector;
};
```
> ✅ C1 (FolderPath, AuthorID, Visibility) + C3a (CreatedAt, AppVersion) ĐÃ THÊM. C4 thêm BoundingBoxExtent — recompile ComboTypes.h sau khi update.

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
    static FString GetCombosDir();   // C3 đổi → %LOCALAPPDATA%/InteriorFOFFTool/Combos (xem task C3a mục 0)

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
    // ⚠️ C3 (gộp P4): đổi sang FPlatformMisc::GetEnvironmentVariable("LOCALAPPDATA")/"InteriorFOFFTool/Combos"
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

**Thứ tự thực thi Sprint 5 (cập nhật 24/06/2026):**
`C0 → C1 → C2 → Fix K3 → C3 → Thumbnail System C++ → C4 [C8 gộp] → C5 → C6 → C7 → WBP_Toast → Xoay combo (P3 verify) → C9 → C11 → C10`
- C0/C1/C2 ✅ DONE
- Fix K3 ✅ DONE (bAddToRecent param)
- C3a/C3b ✅ DONE
- C4 ⏳ 80% — OnDragDetected + ghost box + On Drop combo branch xong. Còn lại: CTV_ComboCard setup trong WBP_FurnitureInventory + test PIE
- C8 ✅ MERGED vào C4 (xem DEVIATIONS trong mục C4)
- Thumbnail System C++ → C4 (còn 20%) → ... : G1 (~25/06)
- WBP_Toast → P3 → C9 : G2
- C11 → C10 : G3

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

### Fix K3 — bAddToRecent (áp cùng lúc với C2/RestoreSnapshot)
**Vấn đề:** `SpawnFurnitureCopy` gọi `AddRecentMesh` unconditional → spawn combo 5 món nhồi 5 mesh lẻ vào Recent; Undo cũng nhồi (RestoreSnapshot gọi SpawnFurnitureCopy). Bug có sẵn, không chỉ combo.
**Fix:**
- `SpawnFurnitureCopy` thêm param `bAddToRecent : Boolean = True`. Trong thân: `Branch(bAddToRecent)` → True: gọi AddRecentMesh; False: bỏ qua.
- Spawn combo (C2): truyền `bAddToRecent = False`.
- **Khuyến nghị kèm:** RestoreSnapshot cũng truyền `bAddToRecent = False` (Undo không nên đụng Recent — bug có sẵn).
- Paste/Duplicate giữ `True` (hành vi đúng).

---

### C3a — Nền data cho dialog (KHÔNG UI) + Gộp P4 + móc thumbnail
**Mục tiêu:** Chuẩn bị data layer. Đồng thời gộp P4 (đổi chỗ lưu combo) và móc thumbnail vào save flow.
**Các việc (thứ tự):**
0. **Gộp P4 — Đổi `GetCombosDir` (C++)** trong `ComboSerializer.cpp`:
   ```cpp
   FString UComboSerializer::GetCombosDir() {
       FString Base = FPlatformMisc::GetEnvironmentVariable(TEXT("LOCALAPPDATA"));
       FString Dir  = Base / TEXT("InteriorFOFFTool") / TEXT("Combos");
       IFileManager::Get().MakeDirectory(*Dir, true);
       return Dir;
   }
   ```
   ⚠️ Xác nhận `FPlatformMisc::GetEnvironmentVariable("LOCALAPPDATA")` trả đúng path Windows 11. Nếu rỗng → fallback `FPaths::ProjectSavedDir()/"Combos"` + báo cuhoang. Thêm `#include "HAL/PlatformMisc.h"` nếu chưa có.
   Thumbnail .png lưu cùng `<CombosDir>/` (không cần subfolder Thumbs).
1. **FComboData thêm 2 field C++** (`ComboTypes.h`):
   `UPROPERTY(EditAnywhere, BlueprintReadWrite) FString AuthorID;` (default "")
   `UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Visibility = TEXT("Private");`
   Recompile. **Category + FolderPath ĐÃ CÓ sẵn (T1/C1) — KHÔNG thêm lại.**
   ⚠️ Field discovery DỪNG ở đây. KHÔNG thêm rating/downloadCount/popularity — server-side state (Phase B).
2. **BP_ComboItemView thêm field** `FolderPath : String`.
3. **LoadComboLibrary**: đọc thêm `FolderPath` từ FComboData gán vào ComboItemView.
4. **SaveComboFromSelection (BP_ComboManager) mở rộng** — chỉ nới thêm, KHÔNG làm lại logic LCA:
   - Signature thêm 2 param: `FolderPath : String`, `Tags : Array<String>`.
   - Bước 5e Make FComboData: nối thêm FolderPath + Tags. Set `CreatedAt` = Now → ToIso8601 (xác nhận tên node), `AppVersion` = version hiện tại, `Visibility` = "Private", `AuthorID` = "".
   - ⚠️ KIỂM: CreatedAt/AppVersion hiện có set giá trị thật chưa. Nếu rỗng → set luôn.
   - **Móc thumbnail — PHẢI capture ngay sau `SaveStringToFile` thành công (lúc đồ còn trong scene):** → gọi capture thumbnail (xem mục "Thumbnail System C++" ngay bên dưới). KHÔNG defer — sau khi dialog đóng đồ có thể bị deselect hoặc xóa.
5. **WBP_FurnitureInventory thêm 2 function vocabulary** (dùng CHUNG: dropdown C3b + tree C5 + tag filter sau):
   - `GetExistingFolders() → Array<String>`: loop AllComboViews → gom FolderPath unique, bỏ rỗng. Chuẩn hóa: trim + "\\"→"/" + bỏ "/" thừa; so sánh case-insensitive.
   - `GetAllUsedTags() → Array<String>`: loop AllComboViews → gom mọi tag → chuẩn hóa (trim + lowercase + collapse space) → dedupe → bỏ rỗng.

**TEST C3a:** Lưu combo → file JSON ở `%LOCALAPPDATA%/InteriorFOFFTool/Combos/<comboID>.json` (Print path xác nhận). Có đủ folderPath/tags/createdAt/authorID/visibility. Thumbnail .png cùng thư mục. Reload → ComboItemView có FolderPath. GetExistingFolders + GetAllUsedTags đúng. Compile xanh.
→ **Báo cuhoang.**

---

### C3b — WBP_SaveComboDialog (UI) ✅ DONE (24/06/2026)
**Mục tiêu:** Dialog nhập thông tin combo, thay hardcode "MyCombo".
**Layout:** Border overlay (đen ~0.6 opacity) + Vertical Box (~480×400, anchored center). Trong Vertical Box:
- TXT_ComboName (EditableText) — **bắt buộc**.
- Folder: ComboBox String (nguồn = ExistingFolders truyền vào) + nút "+ Tạo mới" → hiện EditableText để gõ path mới.
- TXT_Description (EditableText, multi-line).
- TXT_Tags (EditableText) — "ngăn cách bởi dấu phẩy".
- Horizontal Box: BTN_Cancel + BTN_Confirm.
- ⚠️ **KHÔNG có ô Category** — Category nhập ở Phase B (flow Publish), vì save private không cần metadata discovery.

**Dispatcher:** `OnDialogConfirmed(ComboName, FolderPath, Description, Tags)`.
**Input data nhận vào (R3):** `ExistingFolders : Array<String>`, `TagVocabulary : Array<String>` (truyền lúc mở). Event Destruct clear ref (R4).
**Điểm mấu chốt:**
- Validate: tên rỗng → disable/chặn BTN_Confirm.
- Folder "Tạo mới": validate khi gõ — trim + "\\"→"/" + bỏ "/" thừa + chặn ký tự đặc biệt.
- Tags: parse dấu phẩy → chuẩn hóa (trim + lowercase + dedupe + bỏ rỗng) → Array trước khi broadcast.
- Autocomplete tag UI = **DEFER** (data đã chuẩn hóa, gắn sau không sửa schema). Filter-by-tag UI cũng defer (xem C5/C6).

**Đường nối + đóng băng selection (CRITICAL — dialog là async):**
- Chuyển điểm mở dialog về **WBP_FurnitureInventory** (vì nó nắm AllComboViews + vocabulary). CB_SaveCombo (InputManager) forward SelectedActors + Center sang inventory.
- ⚠️ Xác nhận InputManager đã có ref tới inventory chưa — nếu chưa, thêm đường nối (ref sẵn có hoặc Get All Widgets Of Class).
- Inventory **ĐÓNG BĂNG SelectedActors + Center vào biến tạm TRƯỚC khi mở dialog** — vì dialog async, selection/Center có thể đổi lúc user đang gõ.
- Inventory tính ExistingFolders + TagVocabulary → truyền vào dialog → mở.
- **Khóa input UI-only khi dialog mở; trả Game+UI khi đóng** — chặn click xuyên dialog xuống scene (deselect/chọn nhầm đồ).
- OnDialogConfirmed → inventory gọi `ComboManager.SaveComboFromSelection(SelectedActors_tạm, Center_tạm, ComboName, Description, FolderPath, Tags)` → đóng dialog → trả input mode.
- BTN_Cancel → đóng + trả input mode, không lưu.

**TEST C3b:** right-click ≥2 đồ → dialog mở, dropdown hiện folder đã có + nút tạo mới → nhập tên+folder+tags → confirm → JSON đúng tên/folderPath/tags. Tên rỗng → không confirm được. Trong lúc dialog mở, click ra ngoài KHÔNG deselect. Cancel → không lưu.
→ **Báo cuhoang.**

---

### Thumbnail System (C++ THẬT — P1) — xây cùng C4, capture nối vào C3
**Đây là khoản đầu tư "làm 1 lần dùng 3 chỗ": combo / B4 user upload / nút chụp bìa tùy chỉnh.**
**C++ trong FurnitureToolkit, 2 hàm lá (thêm vào `ComboSerializer.h/.cpp`):**
- `SaveRenderTargetToPNG(UTextureRenderTarget2D* RT, const FString& FilePath) → bool`
  Logic: dùng `FImageUtils` hoặc `IImageWrapperModule` để encode RT buffer thành PNG và ghi file.
  ⚠️ Tên hàm chính xác cần xác nhận tại C4 — xem "Nodes chờ xác nhận" trong `AI_Implementation_Rules.md`.
- `LoadTexture2DFromFile(const FString& FilePath) → UTexture2D*`
  Logic: runtime PNG decode bằng `IImageWrapperModule` → tạo `UTexture2D` trong memory.
  Lý do dùng C++ thay node "Import File as Texture2D": node BP chỉ chạy trong editor, không packaged.

**Capture flow (gọi từ C3a bước 4 sau SaveStringToFile):**
1. Tính bounding box của tất cả selection actors.
2. Lấy hướng nhìn camera hiện tại của người dùng (PlayerCameraManager → GetCameraLocation + GetCameraRotation).
3. Đặt `SceneCapture2D` actor tạm (hoặc dùng actor có sẵn) tại vị trí lùi ra đủ xa theo hướng camera để bounding box vừa khung.
4. Capture vào `UTextureRenderTarget2D` (chuẩn hóa size + padding cho ảnh đẹp nhất quán).
5. Gọi `SaveRenderTargetToPNG(RT, CombosDir + "/" + ComboID + ".png")`.
6. Dọn SceneCapture2D tạm nếu đã spawn.

**Display (C4/C7):** `LoadTexture2DFromFile(ThumbPath)` → set lên Image widget. Bỏ fallback icon 🧩.

⚠️ SceneCapture2D + UTextureRenderTarget2D: cần xác nhận node/class setup tại C4 — CHƯA có trong bảng node chính thức. Xem mục "Nodes chờ xác nhận" trong `docs/Rules/AI_Implementation_Rules.md`.

---

### C4 — WBP_ComboCard + Drag-drop combo (gộp C8)

> **DEVIATIONS (24/06/2026):**
> | Ngày | Điều chỉnh | Plan gốc | Thực tế | Lý do |
> |---|---|---|---|---|
> | 24/06/2026 | C4+C8 gộp | Plan tách C4/C8 riêng | Gộp C8 vào C4 | BTN_SpawnCombo = throwaway code; drag-drop là UX chính. Tiết kiệm thời gian, không phá plan |
> | 24/06/2026 | BoundingBoxExtent | Combo cũ = ZeroVector | Ghost tàng hình với combo cũ | Migration Phase B: SchemaVersion + re-save khi spawn lần đầu |
> | 24/06/2026 | WBP_DragOverlay branch | Tạo WBP_ComboDragOverlay riêng | Branch trong WBP_DragOverlay existing | Ít file hơn, tái dùng On Drag Over surface trace |

**Mục tiêu:** Card combo trong tile view với drag-drop ghost + spawn tại cursor.

---

#### WBP_ComboCard — Layout (duplicate từ WBP_FurnitureCard, v1.0)
```
Canvas Panel
├── Overlay
│   ├── Image_Thumbnail (fill, tạm xám)
│   ├── VB_Info (anchor bottom, fill ngang)
│   │   ├── TextBlock_ComboName (font 13, AutoWrap=True)
│   │   └── TextBlock_Badge (font 11)
│   └── HB_Buttons (anchor top-right)
│       ├── BTN_DeleteCombo
│       ├── BTN_InforCombo
│       ├── BTN_ChangeCombo
│       └── BTN_FavoriteCombo
├── LazyImage_ThumbCombo
└── Overlay
    ├── LazyImage_favorite
    └── BTN_FavoriteCombo
```

**Variables:**
```
ComboItem      : BP_ComboItemView (Object Ref)
PreviewActor   : Actor (Object Ref)  ← generic Actor, KHÔNG phải BP_FurnitureActor
DragOverlayRef : WBP_DragOverlay (Object Ref)
```
**Interface:** IUserObjectListEntry

---

#### OnListItemObjectSet
```
Event OnListItemObjectSet (List Item Object)
  ▶→ Cast To BP_ComboItemView
        CastFailed  ▶→ Print "ComboCard: Cast fail" ▶→ dead-end
        CastSuccess ▶→ SET ComboItem (output pin từ cast node)
                    ▶→ Branch(IsValid(ComboItem))
                          False ▶→ dead-end
                          True
                            ▶→ SET TextBlock_ComboName.Text = To Text(ComboItem.ComboName)
                            ▶→ SET TextBlock_Badge.Text = Format Text("×{Count} món",
                                                           Count=ComboItem.ItemCount)
```

#### Event Destruct
```
▶→ SET ComboItem = None
▶→ SET PreviewActor = None
▶→ SET DragOverlayRef = None
```

---

#### OnDragDetected
```
Entry
  ▶→ Create Widget(WBP_DragVisual) → SET Visibility=HitTestInvisible
  ▶→ Create BP_DragDropOperation_ComboCard
        DefaultDragVisual = WBP_DragVisual output
        Pivot = MouseDown
  ▶→ SET ComboID (target=Operation) = GET ComboItem.ComboID
  ▶→ SET ComboExtent (target=Operation) = GET ComboItem.BoundingBoxExtent
  ▶→ Get All Actors Of Class(BP_FurnitureInputManager) → GET[0]
        → GET GizmoControllerRef → DeactivateGizmo
  ▶→ Spawn Actor(BP_ComboGhostActor, Location=0,0,0)
  ▶→ Call InitGhost(Target=SpawnActor output, Extent=ComboItem.BoundingBoxExtent)
  ▶→ SET PreviewActor = SpawnActor output
  ▶→ Create Widget(WBP_DragOverlay) → Add to Viewport
  ▶→ SET DragOverlayRef = WBP_DragOverlay output
  ▶→ SET WBP_DragOverlay.PreviewActorRef = PreviewActor
  ▶→ Return Node (Operation = BP_DragDropOperation_ComboCard output)
```

#### On Drag Cancelled
```
▶→ IsValid(DragOverlayRef) → Remove From Parent → SET None
▶→ IsValid(PreviewActor)   → Destroy Actor      → SET None
```

---

#### WBP_FurnitureInventory — LoadComboLibrary (thêm 1 dây — C4)
Sau khi gán các field khác của ComboItemView, thêm:
```
GET FComboData.BoundingBoxExtent ●→ SET ComboItemView.BoundingBoxExtent
```

---

#### BP_DragDropOperation_ComboCard — class mới
Parent: DragDropOperation
Variables:
```
ComboID     : String
ComboExtent : Vector (default 0,0,0)
```

---

#### BP_ComboGhostActor — class mới
Parent: Actor
Components:
```
GhostMesh : Static Mesh Component
  Static Mesh = /Engine/BasicShapes/Cube
  Collision   = NoCollision
  Material[0] = M_ComboGhost
```

Custom Event `InitGhost(Extent : Vector)`:
```
▶→ Set Actor Scale 3D(Target=self, NewScale3D = Extent / 50.0)
```
> ⚠️ Cube BasicShape = 100×100×100 unit → Scale = Extent/50 → actor size = Extent×2 = full bounding box. BoundingBoxExtent=ZeroVector (combo cũ) → ghost tàng hình, không crash.

---

#### M_ComboGhost — Material mới
```
Blend Mode    = Translucent
Shading Model = Unlit
Constant3Vector(0.2, 0.6, 1.0) ●→ Emissive Color
Constant(0.3)                   ●→ Opacity
```

---

#### WBP_DragOverlay v1.7 — Thay đổi đi kèm C4
Xem [WBP_DragOverlay_FurnitureCard.md](../../Widgets/WBP_DragOverlay_FurnitureCard.md) v1.7:
- `PreviewActorRef` đổi từ `BP_FurnitureActor` → `Actor` (tương thích BP_ComboGhostActor)
- On Drag Over: Cast To BP_FurnitureActor sau Set Actor Location — combo ghost skip PlacementSurfaceType
- On Drop: thêm CastFailed → Cast To BP_DragDropOperation_ComboCard → `GetActorLocation(PreviewActorRef)` → SpawnComboByID (KHÔNG trace lại — ghost đã ở đúng chỗ)

---

**TEST C4:**
- OnListItemObjectSet: 2 card hiện đúng tên + số món.
- Kéo combo card → ghost box xanh (BP_ComboGhostActor) xuất hiện đúng kích thước.
- Thả lên sàn → combo spawn tại cursor (đúng Out Hit.Location).
- Kéo FurnitureCard vẫn hoạt động bình thường (regression).
- Combo BoundingBoxExtent=ZeroVector (combo cũ) → ghost tàng hình (không crash).
- On Drag Cancelled: ghost + overlay destroy đúng.
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
- Tree dựng từ **FolderPath** (folder user tự tạo), KHÔNG phải Category. (Phase B: tab thư viện chung sẽ duyệt theo Category taxonomy chuẩn — nguồn data KHÁC, nhưng tái dùng cùng widget WBP_TreeNode.)
- Nguồn folder = **GetExistingFolders** (CHUNG với C3a) — KHÔNG viết hàm gom folder riêng, tránh dropdown (C3b) và tree (C5) lệch nhau.
- Combo có **FolderPath rỗng → gom nhóm "Chưa phân loại" đặt ĐẦU tree** (combo cũ + combo user không chọn folder rơi vào đây — nếu không có nhóm này chúng biến mất khỏi tree).

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
- Thumbnail hiển thị thật: `LoadTexture2DFromFile(ThumbPath)` → set lên Image widget (giống C4). Bỏ fallback icon 🧩.
- Thêm 1 dòng hiển thị **Category** — SetVisibility = Collapsed khi Category == "" (v1 luôn rỗng nên ẩn; Phase B có giá trị thì hiện). Chừa sẵn chỗ cho discovery.

**TEST C7:** click Info trên card → popup đúng tên/tags/số món/danh sách. Thumbnail thật hiện đúng.
→ **Báo cuhoang.**

---

### WBP_Toast (K1 — TIÊN QUYẾT trước C8)
**Mục tiêu:** Widget toast thông báo đơn giản; mọi chỗ báo lỗi/thành công trong Sprint 5 đều trỏ vào đây.
**Thiết kế:**
- 1 Text block + animation tự ẩn sau 2-3s.
- Dùng `FText` (chuẩn bị i18n sau).
- Custom Event `ShowToast(Message : FText, Duration : Float = 2.5)`: Set Text → Add to Viewport → Delay(Duration) → RemoveFromParent.
- Spawn từ HUD hoặc viewport (không cần parent cụ thể). IsValid guard trước khi RemoveFromParent.
- Mọi chỗ ghi "toast" trong Sprint 5 (C8 spawn fail, C9 replace fail, C11 import rác, M11 thiếu mesh) → gọi ShowToast này.

**TEST WBP_Toast:** gọi ShowToast("Kiểm tra 🧩") từ Level BP → text hiện, tự ẩn sau ~2.5s. Không crash. Gọi 2 lần liên tiếp → không kẹt.
→ **Báo cuhoang. XONG mới làm C8.**

---

### C8 — ✅ MERGED VÀO C4 (24/06/2026)
> Toàn bộ drag-drop combo (BP_DragDropOperation_ComboCard, BP_ComboGhostActor, M_ComboGhost, WBP_DragOverlay On Drop routing) đã thực hiện trong C4. Xem mục C4 ở trên.
> Spec gốc giữ lại bên dưới để tham chiếu — không thực thi lại.

~~**Mục tiêu:** Kéo card combo ra scene, ghost 1 mesh đại diện, thả → spawn tại cursor đúng chỗ (quyết định E + điều chỉnh #2).~~
**TIÊN QUYẾT:** WBP_Toast phải DONE trước C8 (toast "Spawn thất bại" dùng ở đây).
**Điểm mấu chốt:**
- **DragDropOperation_ComboCard MỚI** (KHÔNG extend FurnitureCard). Chứa:
  - `ComboID : String`
  - `RelLocation_Representative : Vector` — offset của món đại diện (Items[0]) so với Center, tính và cache lúc bắt đầu drag.
- **WBP_DragOverlay.On Drop — thêm branch routing:**
  - Cast to `DragDropOperation_ComboCard` → True: tính SpawnLocation (xem surface-snap dưới) → SpawnComboByID(ComboID, SpawnLocation). Branch này phải Return(true) + Remove From Parent.
  - Cast to `DragDropOperation_FurnitureCard` → True: đường furniture cũ (giữ nguyên).
  - ⚠️ Hiện On Drop chỉ có nhánh FurnitureCard — thêm branch ComboCard hoặc = crash/spawn sai.
- **Surface-snap kiểu khối (điều chỉnh #2):**
  - Trace sàn tại điểm chuột → lấy `DropPoint` (điểm chuột trên sàn, `ECC_WorldStatic` hoặc channel sàn).
  - Lọc trace CHỈ ăn sàn (không trace vào mặt bàn, kệ — tránh snap cả combo trôi lên mặt bàn).
  - `SpawnLocation = DropPoint − RelLocation_Representative` → đặt Center sao cho món đại diện (ghost) đáp đúng điểm chuột (fix Lỗ14 combo nhảy chỗ).
  - Snap CẢ combo như 1 khối rigid xuống sàn: tất cả món giữ nguyên offset tương đối với Center — KHÔNG snap từng món riêng.
  - Món loại Wall/Ceiling giữ offset tương đối so với neo sàn — KHÔNG tự tìm bề mặt mới.
- **Ghost mesh:** async load mesh `Items[0].RowName` lúc drag bắt đầu. Nếu test tệ → fallback thumbnail 2D làm ghost. KHÔNG preload trước (48 item/trang = nặng). Quyết sau khi sờ thực tế.

**TEST C8:** kéo card combo → ghost xuất hiện → thả → combo spawn đúng chỗ thả (ghost đáp đúng điểm chuột). Kéo FurnitureCard vẫn hoạt động bình thường (regression). Thả lên mặt bàn → combo KHÔNG nhảy lên bàn (lọc trace).
→ **Báo cuhoang.**

---

### Xoay combo (P3) — verify + tùy chọn
**Mục tiêu:** Đảm bảo xoay được combo cluster sau khi đặt vào scene.
**Chính — verify (gần như chắc chắn chạy sẵn):**
- Spawn combo → chọn combo cluster → mở gizmo Rotate → xoay. Combo spawn ra là 1 group cha (SourceComboID!="") → group rotation đã có từ Sprint 3/4 → xoay group = xoay cả cụm.
- Nếu OK → P3 coi như xong, không cần code mới.
- Nếu KHÔNG OK → báo cuhoang, mô tả triệu chứng, đừng tự sửa.

**Tùy chọn (polish — làm sau nếu muốn):** Xoay NGAY LÚC KÉO (ghost xoay bằng phím R / scroll wheel trước khi thả) — feature mới. Toán pivot:
```
NewLoc = Center + RotateVector(R, OldLoc − Center)
NewRot = CombineRotators(OldRot, R)
```
⚠️ `RotateVector` và `CombineRotators` — tên node cần xác nhận tại thời điểm làm (xem bảng node AI_Implementation_Rules.md).

**TEST Xoay combo:** chọn combo cluster đã đặt → gizmo Rotate → xoay cả cụm, bố cục bên trong không vỡ. TV vẫn đúng vị trí tương đối với kệ sau khi xoay.
→ **Báo cuhoang kết quả verify (OK / KHÔNG OK).**

---

### C9 — Replace combo
**Mục tiêu:** Thay cả cụm combo bằng combo khác (quyết định F).
**⚠️ BẮT BUỘC verify EMS trước khi code C9:** spawn combo, save scene, load lại → Print SourceComboID của group root → phải còn đúng giá trị. Nếu mất → báo cuhoang ngay, KHÔNG code tiếp.
**Điểm mấu chốt:**
- Entry: right-click actor thuộc cụm combo → CB_ReplaceCombo (enable khi actor có GroupID với SourceComboID!="").
- Leo group cha: GetGroupRoot(actor.GroupID) → RootGID → FindGroupData(RootGID) → SourceComboID + FolderPath.
- Mở replace mode combo: navigate folder tree combo tới FolderPath.
- **CalculateCenter** = hàm CHUNG dùng cả C3 (save) lẫn C9 (replace). Input: mảng actors của group; loại trừ pivot dummy và container actor trước khi tính average. Nếu chưa tồn tại hàm này → tạo 1 lần, dùng lại.
- **Sequence thực thi (thứ tự BẮT BUỘC):**
  1. Guard `Cmb_bSpawnInFlight` đầu event.
  2. CalculateCenter(GetAllDescendantActors(RootGID)) → lưu `Center` (TRƯỚC khi destroy).
  3. Destroy GetAllDescendantActors(RootGID) + RootGID group.
  4. SpawnComboByID(newComboID, Center) → đợi OnComboSpawned callback.
  5. **Spawn thành công:** CaptureSnapshot("ReplaceCombo"). Recent tự cập nhật (OnComboSpawned → C6 listener).
  6. **Spawn thất bại** (JSON lỗi / RowName không tồn tại): TỰ ĐỘNG gọi RestoreSnapshot(đỉnh stack) để khôi phục combo cũ → sau đó ShowToast("Combo cũ đã khôi phục — thay thế thất bại"). KHÔNG dùng "Undo tay". KHÔNG capture.
- Rotation v1 reset 0 (giữ rotation = backlog).
- ⚠️ KHÔNG capture "PreReplace" riêng — state cũ đã ở history trước bước destroy.

**TEST C9:**
- Case A: spawn combo A → replace bằng B → cụm A biến, B ở Center cũ → Undo → A quay lại.
- Case B: replace với combo có RowName bậy → RestoreSnapshot TỰ ĐỘNG chạy → combo A quay lại, scene không có lỗ trống → toast hiện.
→ **Báo cuhoang.**

---

### C11 — Export / Import combo (chia sẻ thủ công) — CẢ 2 hướng
**Mục tiêu:** Share nhóm KHÔNG cần server — export file JSON gửi đi (Zalo/USB/Drive), import vào thư viện máy khác.
**⚠️ Thứ tự thực thi:** C9 → **C11** → C10. C11 là feature mới nên phải chạy TRƯỚC C10 để regression test bao luôn.
**Điểm mấu chốt:**
- **Export — CẢ 2 hướng graceful (K5):**
  - Thử **hướng 1**: mở file-save dialog (Desktop platform) cho user chọn nơi lưu → copy `<comboID>.json` đến đó.
  - Không chạy được (node không tồn tại / platform không hỗ trợ) → **tự động fallback hướng 2**: copy ra thư mục Export cố định (`%LOCALAPPDATA%/InteriorFOFFTool/Exports/`) → ShowToast("Đã xuất ra: [path]") để user biết chỗ lấy file.
  - KHÔNG bắt user phải chọn tay xem hướng nào được dùng. KHÔNG hiện 2 nút. Ghi DEVIATIONS hướng nào thực sự chạy được.
- **Import:** chọn file JSON ngoài → LoadStringFromFile → JsonToCombo validate (bParseOK):
  - Parse fail → toast "File combo không hợp lệ", bỏ. KHÔNG crash.
  - OK → **sinh ComboID MỚI** (`combo_` + NewGuid) ghi đè field comboID (tránh đè combo cũ; trùng tên hiển thị thì user tự xóa) → SaveStringToFile vào Combos dir → Broadcast OnComboLibraryChanged → refresh tab.
- **Ràng buộc:** combo chỉ dùng được khi máy đích CÙNG asset pool (RowName resolve được). Thiếu mesh → spawn skip + toast (như M11). Ghi rõ giới hạn này trong UI/doc.

**TEST C11:** export combo A → file .json xuất hiện (dialog HOẶC auto-path). Xóa A khỏi thư viện → import file đó → A quay lại với ComboID mới. Import 2 lần cùng file → 2 combo (ID khác nhau). Import file rác → toast, không crash.
→ **Báo cuhoang.**

---

### C10 — Regression + Docs
**Mục tiêu:** Verify toàn hệ thống + cập nhật tài liệu.
**Regression:**
- R1-R8 Sprint D
- 7 case C2 + 4 case C8 + 2 case C9
- Scene save/load: group + SourceComboID nguyên vẹn sau restart
- T6 pivot rotation: verify có TRÙNG group transform không — nếu trùng → bỏ T6, ghi DEVIATIONS
- C3 mới: dropdown folder hiện đúng list; tag chuẩn hóa (lowercase + dedupe); combo 2 field rỗng (AuthorID/Visibility) load không crash; combo FolderPath rỗng vào nhóm "Chưa phân loại"
- 2 case C11: export → file đúng; import file → combo quay lại với ID mới (round-trip)
- **K4 nested-3 (cap):** spawn combo A → enter-edit A → spawn combo B bên trong → enter-edit B → spawn combo C bên trong → thử enter-edit C → phải bị chặn (cap = 3 cấp). Giao diện không crash.
- **P5-liên quan (material slot — xác nhận giới hạn):** re-import mesh đổi tên material slot → spawn combo chứa mesh đó → check mesh vẫn nhận đúng material hay bị reset. Ghi kết quả vào DEVIATIONS (P5 gác Sprint 7 nhưng cần biết impact thực tế ngay Sprint 5).
- **VRAM (stat rhi):** spawn combo + undo 10 lần liên tiếp → mở `stat rhi` → VRAM không tăng bất thường (không leak RenderTarget sau Thumbnail). Số cụ thể ghi vào DEVIATIONS để so sánh Sprint 7.

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
| M14 | Import file lỗi / trùng / thiếu mesh | Crash khi parse, đè combo cũ, hoặc spawn lỗ trống | Validate JsonToCombo trước khi nhận; import LUÔN sinh ComboID mới (không ghi đè); thiếu mesh skip + toast (như M11) |

---

## 6. ĐỊNH NGHĨA DONE SPRINT 5 v2.0
✅ Lưu combo (nested group đầy đủ + material RowName) → dialog tên/folder → card tab 🧩 → folder tree → spawn 2 lần độc lập với group cha SourceComboID → drag-drop tại cursor → replace cả cụm → undo/redo/save/load nguyên vẹn → regression PASS → docs cập nhật.
❌ Marketplace / giá tiền / đăng tải = B3, không thuộc Sprint 5.

**Context Phase B (KHÔNG làm Sprint 5 — ghi để định hướng):**
- **Mô hình share lai:** v1 chỉ Private (lưu local). Public (thư viện chung) + Shared (share online) + Auth/AuthorID có nghĩa + sync cloud = Phase B. Schema đã chừa AuthorID/Visibility/Category. "Publish" = đổi Visibility Private→Public + điền Category/Tags discovery, KHÔNG copy combo.
- **Chỗ lưu:** v1 `<ProjectSavedDir>/Combos`. Gate 2 cân nhắc `%LOCALAPPDATA%/[App]/Combos` cho bản packaged (sống qua update app). Phase B: thư viện thật ở R2, local thành cache.
- **Category taxonomy:** code ở Phase B. Phác thảo nội dung dần — mượn cấu trúc ngành (trục phòng: Living/Bed/Kitchen/Bath/Dining/Office/Outdoor; trục loại đồ: Seating/Table/Storage/Lighting/Decor). FolderPath = tổ chức cá nhân; Category = discovery công khai — hai trục khác mục đích.

---

## 7. BACKLOG

**Deferred v1 (chốt 21/06 — không làm Sprint 5):**
- Filter-by-tag UI + autocomplete UI: defer Sprint 6. NHƯNG data layer chuẩn bị SẴN ở C3a (chuẩn hóa tag lowercase/dedupe + GetAllUsedTags). Tags KHÔNG còn "chỉ decorative" — có nền data để gắn filter + autocomplete sau mà không phải sửa schema.
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
| 2.2 | 22/06/2026 | Phiên bàn kế hoạch C3: tách C3a (data)+C3b (dialog UI); folder dropdown (GetExistingFolders)+nút tạo mới thay nhập text tự do; tags có data layer (chuẩn hóa+GetAllUsedTags), UI filter/autocomplete defer; thêm field C++ AuthorID+Visibility; bỏ ô Category khỏi dialog save (→Phase B Publish); thêm C11 export/import đặt trước C10; M14; đóng băng selection+khóa input dialog; mở dialog qua inventory; nhóm "Chưa phân loại"; context Phase B (mô hình lai/chỗ lưu/taxonomy) |
| 2.3 | 23/06/2026 10:30 | Sprint5_Plan_v1.1: gộp P4 vào C3a (GetCombosDir → %LOCALAPPDATA%); P1 Thumbnail System C++ (SaveRenderTargetToPNG + LoadTexture2DFromFile, node ⏳ chờ xác nhận C4); Fix K3 (bAddToRecent param + SpawnComboByID False); WBP_Toast (K1 tiên quyết C8); C8 surface-snap kiểu khối + fix Lỗ14 (SpawnLocation=DropPoint−RelLocation_Representative) + DragDropOperation_ComboCard mới; Xoay combo P3 (verify gizmo group + tùy chọn xoay-kéo); C9 thêm EMS verify SourceComboID đầu task + CalculateCenter hàm chung + spawn-fail → TỰ ĐỘNG RestoreSnapshot; C11 CẢ 2 hướng graceful (dialog TRƯỚC, auto-fallback); C10 thêm K4 nested-3 + P5 material-slot check + VRAM stat rhi; thứ tự thực thi G1/G2/G3; P5 material gác Sprint 7 ghi DEVIATIONS |
| 2.4 | 24/06/2026 | C4 gộp C8: WBP_ComboCard đầy đủ spec (layout/vars/OnListItemObjectSet/EventDestruct/OnDragDetected/OnDragCancelled); BP_DragDropOperation_ComboCard + BP_ComboGhostActor + M_ComboGhost; FComboData thêm FolderPath/AuthorID/Visibility (C1/C3a retroactive) + BoundingBoxExtent (C4); LoadComboLibrary thêm BoundingBoxExtent; WBP_DragOverlay v1.7 (PreviewActorRef→Actor, On Drag Over Cast branch, On Drop combo routing); C8 MERGED; DEVIATIONS ghi inline C4; thứ tự thực thi cập nhật 24/06 |
