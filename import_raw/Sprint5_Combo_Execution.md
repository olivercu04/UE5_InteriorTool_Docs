# SPRINT 5 — COMBO MESH (EXECUTION step-by-step)
**Phiên bản:** 1.0 | **Ngày:** 12/06/2026 — Fable 5 (viết trước khi bàn giao 22/06) | Lighting_Mnger UE5.5.4
**Đối tượng đọc:** model thực thi (Opus/Sonnet) + cuhoang. Tuân thủ `09_AI_Implementation_Rules.md`. Làm TỪNG TASK, mỗi task có test, xong báo cuhoang.
**⚠ Doc này viết TRƯỚC khi Sprint D hoàn tất — nếu thực tế Sprint D lệch (tên hàm/biến khác), ưu tiên thực tế, ghi DEVIATIONS, KHÔNG bẻ thực tế theo doc.**

---

## 0. ĐIỀU KIỆN TIÊN QUYẾT (kiểm TRƯỚC khi bắt đầu — thiếu 1 = chưa vào Sprint 5)
1. ✅ Gate 1 xong: B1 ĐÃ CHẾT (undo lần 2 giữ group), `bIsRestoring` hoạt động, `SpawnFurnitureCopy` là đường spawn DUY NHẤT.
2. ✅ Sprint D xong: `RowName` trên BP_FurnitureActor + trong S_FurniturePlacement; `BP_FurnitureItemView`; DisplayPage 2 mode; inventory single-instance.
3. ✅ Plugin biết compile C++ (đã qua D.T3).
Nếu B1 còn sống: DỪNG — combo serialization xây trên group state, xây trên bug = debug 2 tầng.

## 0b. PHẠM VI & SO VỚI APP LỚN (chống scope creep)
Combo = "bộ nội thất xếp sẵn" (Coohom gọi design set, IKEA gọi room set, 3D Warehouse gọi collection). Bảng đối chiếu — cột S5 là việc CỦA SPRINT NÀY, còn lại đã có chỗ trong roadmap:

| Tính năng app lớn | S5 (local) | B3a (chợ free) | B3b (paid) | Sau nữa |
|---|---|---|---|---|
| Lưu bộ đồ + thumbnail + tên/mô tả/tags | ✅ | | | |
| Thư viện combo cá nhân, search, favorite, category | ✅ | | | |
| Spawn combo vào scene, undo, save scene | ✅ | | | |
| Combo lồng nhóm (phòng > góc sofa > bộ bàn) | ✅ (nested group có sẵn) | | | |
| Đăng lên chợ, người khác tải | | ✅ | | |
| Giá tiền, mua, entitlement | | | ✅ | |
| Preview 3D xoay trước khi tải, room template, AI gợi ý | | | | backlog |
| Combo chứa đồ user tự import | schema CHỪA SẴN (sourceType) | | | Sprint G |
**Quy tắc:** thấy mình đang làm cột ngoài S5 → DỪNG, ghi backlog.

**Quyết định mặc định (cuhoang chưa trả lời — đổi được trước T1):**
- D1: Combo lưu KÈM material overrides (bộ sofa đã chỉnh màu giữ nguyên màu) — mặc định CÓ.
- D2: Spawn combo đặt trên SÀN, yaw=0; xoay/di chuyển sau bằng gizmo như group thường.
- D3: Spawn combo khi đang Edit Mode → `ExitEditModeFull` trước (chốt từ Gate1 doc).
- D4: v1 KHÔNG drag-ghost N mesh (phức tạp) — click "Đặt vào scene" → spawn tại điểm trace giữa màn hình. Ghost multi = polish sau.

---

## 1. SCHEMA COMBO JSON v1 (đóng băng sau T1 — đổi = bump version + converter)
```json
{
  "version": 1,
  "comboID": "c_7f3a...",           // GUID, cũng là tên file
  "name": "Bộ phòng khách Bắc Âu",
  "description": "...",
  "tags": ["sofa", "bắc âu"],
  "category": "LivingRoom",
  "createdAt": "2026-07-01T10:00:00Z",
  "appVersion": "1.1",
  "items": [{
      "rowName": "SM_Sofa_01",
      "sourceType": "catalog",       // catalog | imported (Sprint G dùng sau)
      "relLocation": {"x":0,"y":0,"z":0},   // so với Center, trục world lúc lưu
      "relRotation": {"pitch":0,"yaw":90,"roll":0},
      "scale": {"x":1,"y":1,"z":1},
      "surfaceType": "Floor",
      "materialOverrides": ["", "/Game/.../MI_Fabric_Blue", ""],
      "groupToken": "g1"             // token NỘI BỘ file, KHÔNG phải GroupID thật
  }],
  "groups": [
    {"token": "g1", "name": "Bộ sofa", "parentToken": ""},
    {"token": "g2", "name": "Bàn trà", "parentToken": "g1"}
  ]
}
```
**Vì sao token thay GroupID thật:** GroupID trong scene là GUID phiên đó — đem GUID thật vào file rồi spawn 2 lần sẽ trùng. Token chỉ có nghĩa TRONG file; lúc spawn, mỗi token sinh GroupID mới (mục T5 remap).
**Vì sao relLocation theo trục world lúc lưu (không xoay):** đơn giản hóa v1 — combo lưu ở tư thế "như đang đứng trong scene", spawn ra cũng tư thế đó, xoay sau bằng gizmo. Muốn lưu combo đã xoay đẹp thì user xoay trước khi lưu.
**Lưu file:** `<ProjectSavedDir>/Combos/<comboID>.json` (UTF-8) + thumbnail `Saved/Combos/Thumbs/<comboID>.png`. Tên file = comboID (GUID) → tên tiếng Việt có dấu/ký tự lạ KHÔNG bao giờ thành tên file (mìn M10).

---

## 2. TASKS (thứ tự bắt buộc; T1→T5 là vertical slice)

### S5.T1 — C++ ComboTypes + ComboSerializer ⭐ CODE ĐẦY ĐỦ (dán là chạy)
**Vì sao C++ struct mới thay BP struct:** né hẳn vụ mangled-name của BP struct; `FJsonObjectConverter` serialize USTRUCT tự động 2 chiều; struct này tái dùng cho cloud scene B1.

**File mới `ComboTypes.h`** (cạnh FurnitureFilterLibrary trong FurnitureToolkit/Source/.../Public):
```cpp
#pragma once
#include "CoreMinimal.h"
#include "ComboTypes.generated.h"

USTRUCT(BlueprintType)
struct FComboItemData {
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString RowName;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString SourceType = TEXT("catalog");
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FVector RelLocation = FVector::ZeroVector;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FRotator RelRotation = FRotator::ZeroRotator;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FVector Scale = FVector::OneVector;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString SurfaceType = TEXT("Floor");
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") TArray<FString> MaterialOverrides;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString GroupToken;
};

USTRUCT(BlueprintType)
struct FComboGroupData {
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString Token;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString Name;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString ParentToken;
};

USTRUCT(BlueprintType)
struct FComboData {
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") int32 Version = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString ComboID;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString Name;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString Description;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") TArray<FString> Tags;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString Category;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString CreatedAt;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") FString AppVersion;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") TArray<FComboItemData> Items;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combo") TArray<FComboGroupData> Groups;
};
```

**File mới `ComboSerializer.h`:**
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
    UFUNCTION(BlueprintCallable, Category="Combo") static FString ComboToJson(const FComboData& Combo);
    UFUNCTION(BlueprintCallable, Category="Combo") static bool JsonToCombo(const FString& Json, FComboData& OutCombo);
    UFUNCTION(BlueprintCallable, Category="Combo") static bool SaveStringToFile(const FString& FilePath, const FString& Content);
    UFUNCTION(BlueprintCallable, Category="Combo") static bool LoadStringFromFile(const FString& FilePath, FString& OutContent);
    UFUNCTION(BlueprintCallable, Category="Combo") static TArray<FString> ListJsonFilesInDir(const FString& DirPath);
    UFUNCTION(BlueprintPure,     Category="Combo") static FString GetCombosDir();   // <Saved>/Combos
    UFUNCTION(BlueprintCallable, Category="Combo") static bool DeleteFileAtPath(const FString& FilePath);
};
```
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
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);   // tiếng Việt OK
}
bool UComboSerializer::LoadStringFromFile(const FString& FilePath, FString& OutContent) {
    return FFileHelper::LoadFileToString(OutContent, *FilePath);
}
TArray<FString> UComboSerializer::ListJsonFilesInDir(const FString& DirPath) {
    TArray<FString> Files;
    IFileManager::Get().FindFiles(Files, *(DirPath / TEXT("*.json")), true, false);
    return Files;   // chỉ tên file, không kèm path
}
FString UComboSerializer::GetCombosDir() {
    return FPaths::ProjectSavedDir() / TEXT("Combos");
}
bool UComboSerializer::DeleteFileAtPath(const FString& FilePath) {
    return IFileManager::Get().Delete(*FilePath);
}
```
**Build.cs:** thêm `"Json", "JsonUtilities"` vào PrivateDependencyModuleNames. **`FURNITURETOOLKIT_API`** — thay đúng tên module API macro thật của plugin (mở file .h có sẵn của FilterLibrary xem macro nào, copy y hệt).

**Lỗi compile thường gặp (tra trước khi hỏi):**
| Error chứa | Nguyên nhân → Fix |
|---|---|
| `JsonObjectConverter.h: No such file` | Thiếu JsonUtilities trong Build.cs |
| `unresolved external ... FJsonObjectConverter` | Thiếu Json/JsonUtilities (link) |
| `GENERATED_BODY` đỏ lòm cả file | Chưa generate project files / thiếu `#include "...generated.h"` CUỐI danh sách include |
| `BlueprintType ... must be a USTRUCT` | Quên USTRUCT(BlueprintType) trước struct |

**TEST T1:** Blueprint test tạm: Make FComboData (điền tay 1 item) → ComboToJson → Print → JsonToCombo → Break → Print Name. Chuỗi in ra khớp 2 chiều, tên tiếng Việt có dấu không vỡ. → **Báo cuhoang.**

### S5.T2 — SaveComboFromSelection (BP_FurnitureInputManager, Custom Event)
**Entry:** context menu thêm `CB_SaveCombo "💾 Lưu thành Combo"` (chỉ enable khi SelectedActors.Length ≥ 2).
```
SaveComboFromSelection(ComboName, Description):
1. Guard SelectedActors.Length >= 2 → False: Return
2. CalculateCenter(SelectedActors) → Center            ← hàm có sẵn
3. THU THẬP GROUP THAM GIA:
   CLEAR LocalGroupIDs (Array<String>)
   ForEach SelectedActors → Cast → GET GroupID → != "" AND NOT Contains → ADD
   Completed → CLEAR LocalAllGroups (Array<S_GroupData>)
   ForEach LocalGroupIDs (gid):
     GetGroupRoot(gid) → root                          ← lấy CẢ CÂY, không chỉ group lá
     GetGroupsInHierarchy(root) → ForEach inner: NOT Contains(LocalAllGroups, theo GroupID) → ADD
   ← đây chính là lý do GetGroupsInHierarchy được build từ Sprint 4 (bridge)
4. GÁN TOKEN: CLEAR TokenMap (Map String→String)       ← GroupID thật → "g1","g2"...
   ForEach LocalAllGroups (g, idx): ADD TokenMap(g.GroupID, "g" + (idx+1))
5. BUILD FComboData:
   Make FComboData: Version=1, ComboID = "c_" + (NewGuid→ToString),
     Name/Description từ input, CreatedAt = Now→ToIso8601, Category = "MyCombo"
   ForEach LocalAllGroups → Make FComboGroupData:
     Token = TokenMap[GroupID], Name = GroupName,
     ParentToken = (ParentGroupID=="" ? "" : TokenMap.Find(ParentGroupID, found? value : ""))
     ← ParentGroupID NGOÀI bộ lưu (group cha không được chọn) → "" (cắt cây tại đó — đúng ý)
   ForEach SelectedActors → Cast → Make FComboItemData:
     RowName (D.T8), SourceType="catalog",
     RelLocation = ActorLocation - Center               ← trừ vector thuần, KHÔNG xoay (D2)
     RelRotation = ActorRotation, Scale = ActorScale3D,
     SurfaceType = PlacementSurfaceType→ToString,
     MaterialOverrides = copy mảng, GroupToken = (GroupID==""?"":TokenMap[GroupID])
6. ComboToJson → SaveStringToFile(GetCombosDir + "/" + ComboID + ".json")
7. CaptureComboThumbnail(ComboID)                       ← T2b
8. Toast "Đã lưu combo" + Broadcast OnComboLibraryChanged (dispatcher mới)
```
**T2b — Thumbnail:** TÁI DÙNG pipeline SceneCapture2D của material thumbnail (Capture Source = **Final Color (LDR) in RGB** — fix đen đã trả giá). Capture selection hiện tại → RenderTarget 256×256 → node Blueprint **Export Render Target** (đường dẫn GetCombosDir/Thumbs, file <ComboID>.png). ⚠ Node này xuất .png cho RT format RGBA8 — RT phải tạo RTF RGBA8. Nếu kết quả ra .hdr/lỗi → Plan B: bỏ thumbnail file, card hiện icon 🧩 + tên (KHÔNG để thumbnail chặn sprint — nó là polish).
**TEST T2:** lưu bộ 3 đồ có 1 group + 1 đồ lẻ → mở file .json bằng Notepad: items đủ 3, relLocation hợp lý (tổng ≈ 0), groups 1 dòng token g1, item lẻ groupToken="". Tên tiếng Việt không vỡ. → **Báo cuhoang + dán JSON.**

### S5.T3 — Thư viện combo local + BP_ComboItemView
```
BP_ComboItemView (Object, mirror BP_FurnitureItemView):
  ComboID, Name : String | ThumbPath : String | ItemCount : Integer | Tags : Array<String>
LoadComboLibrary (WBP_FurnitureInventory, Custom Event):
  ListJsonFilesInDir(GetCombosDir) → ForEach:
    LoadStringFromFile → JsonToCombo → success:
      Construct BP_ComboItemView ← Name, ComboID, Items.Length, Tags, ThumbPath
      ADD → AllComboViews (Array, class var — CLEAR đầu hàm!)
  ⚠ JsonToCombo fail (file hỏng/version lạ) → SKIP + Print tên file, KHÔNG crash cả thư viện
```
**TEST T3:** tạo 2 combo ở T2 → LoadComboLibrary → Print Length = 2. Bỏ 1 file rác .json vào folder → vẫn ra 2 + 1 dòng warning. → **Báo cuhoang.**

### S5.T4 — Inventory: category 🧩 Combo + WBP_ComboCard
1. Thêm category "🧩 Combo" cạnh Recent/Favorite (cùng pattern ActiveSpecialCategory — nhánh đặc biệt trong FilterBySearch: SET nguồn = AllComboViews thay rows, đổ vào tile view riêng `CTV_ComboCard` HOẶC tái dùng CTV_FurnitureCard nếu generic — quyết định lúc làm, ưu tiên tile view RIÊNG cho sạch).
2. `WBP_ComboCard` (clone FurnitureCard): thumbnail (Async load PNG từ disk: **Import File as Texture2D** node của UE5 — ⚠ node mới, cuhoang xác nhận; fail → icon 🧩), tên, badge số món "×6", nút 🗑 xóa (DeleteFileAtPath + refresh), nút **"Đặt vào scene"** → gọi SpawnComboByID.
3. Search trong tab combo: lọc AllComboViews theo Name/Tags Contains (Blueprint thuần — thư viện cá nhân vài chục combo, không cần C++).
**TEST T4:** tab Combo hiện 2 card đúng tên + số món; xóa 1 → còn 1, file biến mất. → **Báo cuhoang.**

### S5.T5 — SpawnCombo ⭐ TRÁI TIM SPRINT (Custom Event — có async)
```
SpawnComboByID(ComboID):
0. Branch EditModeStack.Length > 0 → True: ExitEditModeFull   (D3)
1. LoadStringFromFile → JsonToCombo → fail: toast lỗi, Return
2. ĐIỂM ĐẶT: GetHitResultUnderCursorByChannel? KHÔNG — nút bấm từ UI:
   trace từ camera giữa màn hình xuống sàn (LineTrace channel Visibility, start=camera, 
   end=camera+forward*1500, fallback: vị trí trước camera 500, Z giữ nguyên) → SpawnCenter
3. KIỂM ITEM THIẾU (catalog đổi sau khi lưu combo):
   CLEAR LocalMissing; ForEach Items: GetDataTableRow(DT, RowName) fail → ADD RowName→LocalMissing
   LocalMissing.Length == Items.Length → toast "Combo không còn dùng được", Return
   > 0 → toast "Thiếu N món, spawn phần còn lại" (vẫn tiếp tục)
4. WARM CACHE (R1 — async trước, spawn sau):
   SET PendingLoadCount = số item hợp lệ; SET LoadedCount = 0; SET bComboSpawnInFlight = True
   ForEach item hợp lệ: RowName → DT → mesh path → MakeSoftObjectPath → AsyncLoadAsset
     mỗi Completed → LoadedCount += 1 (dùng OUTPUT pin của SET)
     → Branch LoadedCount >= PendingLoadCount AND bComboSpawnInFlight:
         True → SET bComboSpawnInFlight = False → gọi bước 5 (guard chống double-fire — mìn M2)
5. REMAP GROUP (chạy TRƯỚC spawn):
   CLEAR TokenToNewID (Map String→String)
   ForEach Combo.Groups (g):
     GenerateGroupID → NewID → ADD TokenToNewID(g.Token, NewID)
   ForEach Combo.Groups (g):                      ← vòng 2 — cha có thể đứng sau con trong mảng
     Make S_GroupData: GroupID = TokenToNewID[g.Token], GroupName = g.Name,
       ParentGroupID = (g.ParentToken=="" ? "" : TokenToNewID[g.ParentToken]), bIsLocked=false
     ADD → InputManager.Groups
   SyncGroupsToContainer
   ← 2 VÒNG RIÊNG là bắt buộc: vòng 1 sinh đủ ID, vòng 2 mới nối cha-con. Gộp 1 vòng = mìn M3.
6. SPAWN: DeselectAll → CLEAR LocalSpawned
   ForEach item hợp lệ:
     SpawnFurnitureCopy(MeshPath từ DT, DAPath="", 
       Location = SpawnCenter + item.RelLocation,      ← cộng thuần (D2, yaw=0)
       Rotation = item.RelRotation, Scale = item.Scale,
       MaterialOverrides = item.MaterialOverrides, SurfaceType, bAutoSelect=False,
       RowName = item.RowName) → NewActor
     → Cast → SET GroupID = (item.GroupToken=="" ? "" : TokenToNewID[item.GroupToken])
     → ADD LocalSpawned
   ← load đã warm ở bước 4 → Load Blocking bên trong SpawnFurnitureCopy trúng cache, không hitch
7. Completed → SelectActors(LocalSpawned) → CaptureSnapshot("SpawnCombo")   ← 1 snapshot duy nhất
   → AddRecentMesh? KHÔNG (combo không phải mesh) — backlog "recent combo"
```
**TEST T5 (bộ test quyết định sprint):**
```
1. Spawn combo 5 món có group → đủ 5, đúng hình dạng tương đối, cả cụm được select, info bar hiện group
2. ⭐ SPAWN CÙNG COMBO LẦN 2 → 2 cụm ĐỘC LẬP: move cụm 1, cụm 2 đứng yên; GroupID khác nhau (Print)
3. Undo sau spawn → cả cụm biến mất TRONG 1 LẦN undo; Redo → quay lại đủ + group nguyên
4. Spawn khi đang edit mode → tự thoát edit rồi spawn
5. Combo thiếu 1 RowName (sửa tay file json thành tên bậy) → spawn N-1 món + toast
6. Save scene (EMS) → Load → combo spawn từ trước quay lại đúng group
7. Spawn combo 20 món → không khựng quá ~0.5s sau khi ấn nút
```
→ **Báo cuhoang + bảng PASS/FAIL 7 case. Đây là vertical slice — PASS hết mới làm T6.**

### S5.T6 — TOÁN XOAY QUANH PIVOT (trả nợ T15) ⭐ GIẢI SẴN
**Bài toán:** xoay N actor quanh pivot P một góc delta R (gizmo rotate khi multi-select / combo vừa spawn).
**Công thức (đúng cho mọi trục, dùng yaw là chính):**
```
Với mỗi actor i:
  NewLocation_i = P + RotateVector(R, OldLocation_i − P)
  NewRotation_i = CombineRotators(OldRotation_i, R)
```
- `RotateVector(Rotator R, Vector V)` — node BP có sẵn tên **RotateVector** (⚠ node mới với project — cuhoang xác nhận, thêm bảng 09; tương tự **UnrotateVector**, **CombineRotators**).
- `CombineRotators(A, B)` = áp A rồi áp B (world). Thứ tự đúng là `CombineRotators(OldRot, Delta)` — NGƯỢC LẠI sẽ sai khi actor có rotation sẵn ≠ 0. Test case 3 dưới bắt lỗi này.
- Scale quanh pivot (nếu làm): `NewLoc = P + Offset × Factor; NewScale = OldScale × Factor` — CHỈ uniform. Non-uniform quanh pivot với actor đã xoay = méo hình, KHÔNG làm.

**Nơi cắm — ĐỐI CHIẾU THỰC TẾ TRƯỚC (Q1):** mở `BP_PivotActor.md` + `T15_Multi_Rotate_Scale_Plan.md` + node graph thật, xác định hiện trạng: (a) actors ATTACH vào pivot (UE tự orbit — có khi đã chạy đúng, T6 chỉ còn verify), hay (b) pivot giữ offset thủ công qua RefreshOffsets (→ cần hàm mới). Nếu (b):
```
Function ApplyPivotRotationDelta(DeltaRot : Rotator)   — trong BP_PivotActor hoặc InputManager
  P = GizmoPivotActor.GetActorLocation
  ForEach AttachedActors (IsValid guard):
    Offset = ActorLocation − P
    SetActorLocation(P + RotateVector(DeltaRot, Offset))
    SetActorRotation(CombineRotators(ActorRotation, DeltaRot))
  → RefreshOffsets
Gọi từ: BP_GizmoController chỗ tính rotation delta mỗi frame kéo (cùng chỗ đang xoay pivot) —
  delta = rotation áp cho pivot frame đó (đã qua SnapAngle). Pivot xoay → actors orbit theo cùng delta.
```
**TEST T6:** (1) 2 đồ 2 bên pivot, kéo rotate 90° → đổi chỗ cho nhau, mặt hướng đúng; (2) snap 15° vẫn mượt; (3) ⭐ đồ có rotation sẵn 45° xoay tiếp 90° → ra đúng 135° và vị trí đúng (bắt lỗi thứ tự CombineRotators); (4) undo sau xoay → về đúng. → **Báo cuhoang.**

### S5.T7 — Tương tác hệ thống (rà soát, ít code)
1. Replace mode khi selection là combo-group: hành vi như group thường (MeshesToReplace đã multi) — TEST không cần code.
2. Delete combo trong scene = DeleteSelected + PruneEmptyGroups dọn group — TEST.
3. ⭐ RestoreSnapshot với scene chứa combo: nhờ G1.T2 (spawn hợp nhất) + B1 chết, tự chạy — TEST kịch bản: spawn combo → move → đổi material 1 món → undo ×3 → redo ×3.
4. Box select quét nửa combo → ExpandSelectionWithGroups tự nở thành cả cụm — TEST.

### S5.T8 — Regression + cập nhật doc
Chạy lại R1-R8 của Sprint D (D.T9) + 7 case T5 + 4 case T6. Docs: `BP_FurnitureInputManager.md` →v1.8 (SaveCombo/SpawnCombo/ApplyPivotRotationDelta), `WBP_FurnitureInventory.md` →v2.5 (tab Combo), file mới `Combo_System.md` (schema + flow — nguồn sự thật combo), Session_State, PROGRESS, DEVIATIONS, bảng node file 09 (RotateVector, UnrotateVector, CombineRotators, Export Render Target, Import File as Texture2D — node nào dùng thật mới thêm).

---

## 3. SỔ RỦI RO — DỰ ĐOÁN TRƯỚC + PLAN B (đọc khi kẹt, TRƯỚC khi đoán mò)
| # | Rủi ro | Triệu chứng | Plan B (đã duyệt sẵn — cứ làm) |
|---|---|---|---|
| M1 | Toán xoay sai thứ tự CombineRotators | Đồ có rotation sẵn xoay xong "trôi" vị trí/hướng | Đảo 2 input node CombineRotators — chỉ có 2 cách, cách kia là đúng |
| M2 | Async counter double-fire | Spawn combo ra GẤP ĐÔI số món | Guard bComboSpawnInFlight (đã cài T5.4); kiểm SET dùng output pin |
| M3 | Remap gộp 1 vòng | ParentGroupID trỏ token chưa sinh → cây gãy, edit mode loạn | Tách 2 vòng như T5.5 — đây là lý do nó được viết 2 vòng |
| M4 | Spawn combo ×2 dính nhau | Move cụm 1, cụm 2 chạy theo | Token chưa remap đủ — soi chỗ SET GroupID actor có qua TokenToNewID không |
| M5 | Export Render Target không ra PNG | File .hdr/đen/không có | Bỏ thumbnail (icon 🧩 + tên) — KHÔNG để polish chặn sprint |
| M6 | Import File as Texture2D không tồn tại/khác tên UE5.5 | Compile node fail | Card không ảnh; backlog "C++ load PNG runtime (FImageUtils)" — 30 phút C++ khi rảnh |
| M7 | JSON tiếng Việt vỡ | Tên combo thành "???" | Đã ForceUTF8WithoutBOM ở T1 — nếu vẫn vỡ: kiểm app đọc (Notepad encoding), không phải file |
| M8 | Trace điểm đặt rơi vào tường/hư không | Combo spawn lơ lửng | Fallback đã ghi T5.2 (trước camera 500, giữ Z); backlog: ghost preview |
| M9 | Combo 50 món khựng | Đứng hình lúc bấm | Warm cache đã là giải pháp; vẫn khựng → giới hạn combo ≤ 30 món (validate lúc LƯU) |
| M10 | Tên combo ký tự lạ phá tên file | File không tạo được | Đã né: tên file = ComboID GUID, không bao giờ là Name |
| M11 | Catalog đổi RowName sau khi lưu combo | Item thiếu | Đã xử lý T5.3 (skip + toast); chính sách dài hạn: RowName là HỢP ĐỒNG — không đổi tên row đã phát hành (ghi vào Data.md) |
| M12 | Kẹt C++ không có Fable | Compile error lạ | Bảng lỗi T1 → search nguyên văn error → fail 3 lần: gác phần C++ đó, làm task khác, gom hỏi Opus 1 lần với đầy đủ: error + file + dòng |

## 4. ĐỊNH NGHĨA DONE SPRINT 5
Lưu combo từ selection (kèm group lồng + material) → thấy trong tab 🧩 → spawn 2 lần độc lập → xoay cả cụm quanh pivot đúng → undo/redo/save/load nguyên vẹn → regression R1-R8 PASS → docs cập nhật. Marketplace/giá tiền/đăng tải = B3, KHÔNG nằm ở đây.

## Lịch sử
| 1.0 | 12/06/2026 | Fable 5 — viết trước bàn giao: schema v1, C++ đầy đủ, toán pivot giải sẵn, remap 2 vòng, 12 rủi ro + Plan B. |
