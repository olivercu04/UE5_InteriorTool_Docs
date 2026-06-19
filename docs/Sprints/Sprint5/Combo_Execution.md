# SPRINT 5 — COMBO MESH (EXECUTION step-by-step)

> ⚠️ DEVIATION (19/06/2026) — ĐỌC TRƯỚC KHI THỰC THI
>
> Doc này (v1.1) viết với giả định MỌI combo event (SaveComboFromSelection,
> CaptureComboThumbnail, LoadComboLibrary, SpawnComboByID...) nằm TRONG
> BP_FurnitureInputManager và đọc trực tiếp class var của nó.
>
> THỰC TẾ TỪ 19/06: combo logic đã TÁCH sang Actor riêng BP_ComboManager.
> Khi thực thi, phải DỊCH từng bước theo các luật sau — KHÔNG copy nguyên văn doc:
>
> 1. Mọi event combo sống trong BP_ComboManager, KHÔNG phải BP_FurnitureInputManager.
> 2. ComboManager KHÔNG đọc class var của InputManager. Mọi data InputManager
>    cần đưa cho ComboManager phải truyền qua PARAM của event.
>    Ví dụ chữ ký mới:
>       SaveComboFromSelection(SelectedActors: Array<BP_FurnitureActor>,
>                              Center: Vector, ComboName: String, Description: String)
> 3. InputManager lo phần guard (≥2 đồ), tính Center, lấy SelectedActors,
>    rồi GỌI ComboManager với data đó.
> 4. Hàm dùng chung như FindGroupData: ComboManager gọi thẳng BP_GroupsContainer
>    qua Get All Actors Of Class → Get(0), KHÔNG qua InputManager.
> 5. ComboManager KHÔNG giữ hard ref InputManager (R2). Nếu cần báo ngược
>    (vd spawn xong cần select), dùng Event Dispatcher để InputManager lắng nghe.
> 6. Đặt tên biến theo quy ước mới — xem AI_Implementation_Rules.md mục "Quy ước đặt tên biến".
>
> Chỗ nào doc ghi "đọc SelectedActors / class var" → hiểu là "đọc param tương ứng".

**Phiên bản:** 1.1 | **Ngày:** 12/06/2026 | Lighting_Mnger UE5.5.4
**Tác giả:** Fable 5 (plan gốc v1.0) + Q&A Sonnet 4.6 review → hợp nhất thành v1.1
**Đối tượng đọc:** model thực thi (Opus/Sonnet) + cuhoang. Tuân thủ `09_AI_Implementation_Rules.md`.
**Làm TỪNG TASK, mỗi task có test, xong báo cuhoang.**

> **THAY ĐỔI so với v1.0:**
> - T2 bước 3: XÓA kéo-cả-cây. Thay bằng selection-only (Q2 + điểm kiến trúc LCA).
> - Variables: thêm 8 class vars cho async spawn (Q8).
> - SpawnComboByID: guard double-click đầu event (Q10), ValidItems array (Q7), trace 2 tầng (Q9).
> - Chốt: CTV_ComboCard riêng (Q5), CaptureComboThumbnail đồng bộ (Q3).
> - Path join: GetCombosDir + "/" + FileName tại caller (Q4).
> - Backlog thêm 2 dòng.

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
| Thư viện combo cá nhân, search | ✅ | | | |
| Spawn combo, undo, save scene | ✅ | | | |
| Nested group trong combo | ✅ | | | |
| Đăng chợ, người khác tải | | ✅ | | |
| Giá tiền, mua, entitlement | | | ✅ | |
| Preview 3D, AI gợi ý | | | | backlog |
| Combo chứa đồ user import | schema chừa sourceType | | | Sprint G |

**Quyết định mặc định (chốt — đổi được trước T1):**
- D1: Lưu KÈM material overrides.
- D2: Spawn yaw=0 tại điểm trace giữa màn hình; xoay sau bằng gizmo.
- D3: Spawn khi đang Edit Mode → ExitEditModeFull trước.
- D4: v1 KHÔNG drag-ghost N mesh — bấm nút → spawn ngay.

---

## 1. SCHEMA JSON v1

```json
{
  "version": 1,
  "comboID": "c_7f3a...",
  "name": "Bộ phòng khách Bắc Âu",
  "description": "...",
  "tags": ["sofa", "bắc âu"],
  "category": "LivingRoom",
  "createdAt": "2026-07-01T10:00:00Z",
  "appVersion": "1.1",
  "items": [{
      "rowName": "SM_Sofa_01",
      "sourceType": "catalog",
      "relLocation": {"x":0,"y":0,"z":0},
      "relRotation": {"pitch":0,"yaw":90,"roll":0},
      "scale": {"x":1,"y":1,"z":1},
      "surfaceType": "Floor",
      "materialOverrides": ["", "/Game/.../MI_Blue", ""],
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
- Schema version: field mới thêm → file cũ load OK (FJsonObjectConverter ignore field thừa). Field xóa → default value. Backward-compatible 1 chiều đủ cho v1.
- Lưu: `<ProjectSavedDir>/Combos/<comboID>.json` | Thumb: `.../Combos/Thumbs/<comboID>.png`.

---

## 2. C++ STRUCTS & SERIALIZER — T1

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
→ **Báo cuhoang.**

---

## 3. TASKS

### S5.T2 — SaveComboFromSelection (Custom Event, BP_FurnitureInputManager)

Entry: Context menu thêm `CB_SaveCombo "💾 Lưu thành Combo"` — enable khi SelectedActors ≥ 2. Mở dialog nhập tên → gọi `SaveComboFromSelection(ComboName, Description)`.

```
Bước 1 — Guard:
  SelectedActors.Length < 2 → Return

Bước 2 — Center:
  CalculateCenter(SelectedActors) → Center

★ Bước 3 — Thu thập groups (v1.1 — SELECTION-ONLY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NGUYÊN TẮC "chọn gì lưu nấy" (Q2):
  (a) Góc người dùng: UX bất biến của Figma/Blender/Coohom —
      bấm Lưu Combo mà file chứa thêm group cha không chọn = phản trực giác.
  (b) Góc người bán: combo là sản phẩm — phải kiểm soát chính xác
      món gì trong gói. "Chọn gì bán nấy" dễ giải thích.
  (c) Góc kiến trúc: đơn giản hơn LCA, đúng trong mọi ca thực tế
      vì ResolveSelectionUnit đã nở selection đúng scope trước khi tới đây.
  KHÔNG GetGroupRoot, KHÔNG GetGroupsInHierarchy, KHÔNG leo cây.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CLEAR LocalGroupIDs (Array<String>)
  ForEach SelectedActors → Cast → GET GroupID
    GroupID != "" AND NOT Contains(LocalGroupIDs, GroupID) → ADD
  Completed:
  CLEAR LocalComboGroups (Array<S_GroupData>)
  ForEach LocalGroupIDs (gid):
    FindGroupData(gid) → bFound True → ADD data
  ← Chỉ group của actors được chọn.
    Group cha không được chọn → cắt tại đó, thành root trong combo.

Bước 4 — Token:
  CLEAR TokenMap (Map<String,String>)
  ForEach LocalComboGroups (g, idx): ADD TokenMap(g.GroupID, "g" + (idx+1))

Bước 5 — Build FComboData:
  ComboID = "c_" + (NewGuid → ToString)
  Make FComboData: Version=1, ComboID, Name, Description,
    CreatedAt=(Now→ToIsoString), Category="MyCombo"

  ForEach LocalComboGroups → Make FComboGroupData:
    Token       = TokenMap[g.GroupID]
    Name        = g.GroupName
    ParentToken = g.ParentGroupID=="" ? ""
                  : Map_Find(TokenMap, g.ParentGroupID, Found) ? Found_Value : ""
                  ← Cha ngoài bộ lưu → "" → thành root trong combo
    ADD → ComboData.Groups

  ForEach SelectedActors → Cast → Make FComboItemData:
    RowName           = Actor.RowName (D.T8)
    SourceType        = "catalog"
    RelLocation       = ActorLocation − Center
    RelRotation       = ActorRotation
    Scale             = ActorScale3D
    SurfaceType       = PlacementSurfaceType → ToString
    MaterialOverrides = copy array
    GroupToken        = GroupID=="" ? "" : TokenMap[GroupID]
    ADD → ComboData.Items

Bước 6 — Lưu:
  ComboDir = GetCombosDir → CreateDirectory(ComboDir) nếu chưa có
  FilePath = ComboDir + "/" + ComboID + ".json"
  ComboToJson → SaveStringToFile(FilePath, Json)

Bước 7 — Thumbnail (Q3 — ĐỒNG BỘ, gọi khi SelectedActors còn nguyên):
  CaptureComboThumbnail(ComboID)

Bước 8 — Kết thúc:
  Toast "✅ Đã lưu combo"
  Broadcast OnComboLibraryChanged   ← dispatcher mới trên InputManager
```

**T2b — CaptureComboThumbnail(ComboID) — Custom Event (Q3):**
```
⚠ ĐỒNG BỘ — không latent. CaptureScene() và Export Render Target đều đồng bộ.
  Gọi ngay sau SaveStringToFile khi SelectedActors còn là bộ đồ vừa lưu → không có race.

CalculateCenter(SelectedActors) → Center
MaxBound = max BoundingSize của các actors → fallback 200
CamOffset = Center + Vector(−MaxBound×1.5, −MaxBound×1.5, MaxBound×1.2)
SET SceneCapture2D Location = CamOffset
SET SceneCapture2D Rotation = FindLookAtRotation(CamOffset, Center)
bCaptureEveryFrame = False → CaptureScene()
ThumbDir = GetCombosDir + "/Thumbs" → CreateDirectory(ThumbDir)
Export Render Target(RT_ComboThumb 256×256 RGBA8, ThumbDir + "/" + ComboID + ".png")

─── Plan B (nếu Export Render Target fail — M5) ───
SKIP thumbnail. Card hiện icon 🧩 + tên. Ghi DEVIATIONS 1 dòng. KHÔNG để thumbnail chặn sprint.
```
> SceneCapture2D spawn sẵn ở BeginPlay — tái dùng actor đó (giống pipeline material thumb).
> Capture Source = **"Final Color (LDR) in RGB"** — fix đen đã trả giá.
> RT format = RTF RGBA8 (Export node yêu cầu). Nếu ra .hdr → đổi format RT.

**TEST T2:** lưu bộ 3 đồ có 1 group + 1 đồ lẻ → mở .json: items đủ 3, relLocation tổng ≈ 0, groups 1 entry, item lẻ groupToken="". Tiếng Việt không vỡ. File .png xuất hiện (hoặc DEVIATIONS).
→ **Báo cuhoang + dán JSON.**

---

### S5.T3 — LoadComboLibrary + BP_ComboItemView

**BP_ComboItemView** (Object, mirror BP_FurnitureItemView):
```
Variables: ComboID (String), Name (String), ThumbPath (String),
           ItemCount (Integer), Tags (Array<String>)
```

**LoadComboLibrary (Custom Event, WBP_FurnitureInventory):**
```
CLEAR AllComboViews   ← class var, CLEAR ĐẦU HÀM

ListJsonFilesInDir(GetCombosDir) → FileNames   ← chỉ tên file
ForEach FileNames (FileName):
  FullPath = GetCombosDir + "/" + FileName      ← Q4: nối path tại đây, không trong C++
  LoadStringFromFile(FullPath) → success:
    True  → JsonToCombo → success:
              True  → Construct BP_ComboItemView
                       → SET ComboID, Name, Tags, ItemCount=Items.Length
                       → ThumbPath = GetCombosDir + "/Thumbs/" + ComboID + ".png"
                       → ADD → AllComboViews
              False → Print "File lỗi/version lạ: " + FileName   (SKIP, không crash)
    False → Print "Không đọc được: " + FileName

⚠ JsonToCombo version lạ (vd version=2 tương lai):
  FJsonObjectConverter đọc field biết, ignore field lạ → forward-compatible.
  Chính sách: "không xóa field cũ khi bump schema version" — ghi vào Data.md.
```

**TEST T3:** 2 combo từ T2 → Length = 2. Bỏ 1 file rác .json → 2 + 1 warning, không crash.
→ **Báo cuhoang.**

---

### S5.T4 — Inventory tab 🧩 Combo + WBP_ComboCard

**Chốt: CTV_ComboCard RIÊNG (Q5):**
- Người dùng: card combo có badge "×6 món" khác biệt rõ với furniture card.
- Người bán: B3 cần gắn giá/trạng thái published lên card này — riêng thì gắn sạch.
- Kiến trúc: Replace mode + Favorite-mesh logic của FurnitureCard không áp dụng cho combo.

**WBP_ComboCard:**
```
Interface: IUserObjectListEntry
Variables: ComboItem (BP_ComboItemView), InventoryRef

OnListItemObjectSet:
  Cast → BP_ComboItemView → SET ComboItem
  ⚠ Q6 — "Import File as Texture2D" node:
    Search node trong editor TRƯỚC.
    Thấy → load ThumbPath → Set Brush (xác nhận vào bảng 09).
    Không thấy → Plan B: icon 🧩 cứng. Ghi DEVIATIONS. Backlog C++ load PNG (FImageUtils).
  SET TXT_ComboName = ComboItem.Name
  SET TXT_ItemCount = "×" + ComboItem.ItemCount + " món"

BTN_SpawnCombo "📥 Đặt vào scene" OnClicked:
  GET InventoryRef → SpawnComboByID(ComboItem.ComboID)

BTN_DeleteCombo 🗑 OnClicked:
  DeleteFileAtPath(GetCombosDir + "/" + ComboItem.ComboID + ".json")
  DeleteFileAtPath(GetCombosDir + "/Thumbs/" + ComboItem.ComboID + ".png")
  GET InventoryRef → LoadComboLibrary → RefreshComboTab
```

**Inventory — thêm tab Combo:**
- BTN_Tab_Combo cạnh BTN_Tab_Material.
- FilterBySearch nhánh Combo (ActiveSpecialCategory == "Combo"):
  Lọc AllComboViews theo Name/Tags Contains SearchText (Blueprint thuần).
  Clear List Items(CTV_ComboCard) → ForEach kết quả → Add Item.
- Bind OnComboLibraryChanged → LoadComboLibrary ở Event Construct.

**TEST T4:** 2 card đúng tên + số món. Xóa 1 → còn 1, file biến. Search "sofa" → lọc đúng.
→ **Báo cuhoang.**

---

### S5.T5 — SpawnComboByID ⭐ TRÁI TIM SPRINT (Custom Event, BP_FurnitureInputManager)

**★ Variables mới — class vars (Q8):**
```
⚠ BẮT BUỘC là class vars vì Custom Event không có local variable,
  và async callback cắt ngang luồng — state phải sống ở class level.
  Tất cả CLEAR đầu event + Event End Play (R4).

bComboSpawnInFlight : Boolean        (default False)
PendingLoadCount    : Integer
LoadedCount         : Integer
PendingComboData    : FComboData     ← sống từ bước 1 tới bước 6
PendingSpawnCenter  : Vector
PendingValidItems   : Array<FComboItemData>
TokenToNewID        : Map<String,String>
SpawnedComboActors  : Array<BP_FurnitureActor>
```

```
SpawnComboByID(ComboID : String):

★ Bước 0 — Guard double-click + reset (Q10):
  Branch bComboSpawnInFlight == True → Return   ← chặn double-click khi đang spawn
  ⚠ Blueprint game thread đơn → async callback TUẦN TỰ, không song song.
    LoadedCount tăng dần không có race. Guard này chặn LOGIC-RACE (double-click),
    không phải thread-race.
  CLEAR PendingValidItems, SpawnedComboActors, TokenToNewID
  SET LoadedCount=0, PendingLoadCount=0, bComboSpawnInFlight=False

Bước 0b — Thoát Edit Mode (D3):
  EditModeStack.Length > 0 → ExitEditModeFull

Bước 1 — Load:
  FullPath = GetCombosDir + "/" + ComboID + ".json"
  LoadStringFromFile → False: toast "Không tìm thấy combo", Return
  JsonToCombo → SET PendingComboData → False: toast "File combo lỗi", Return

★ Bước 2 — Điểm đặt (Q9 — trace 2 tầng vì cursor đang trên UI):
  GetPlayerCameraManager → GetCameraLocation → CamLoc
  GetPlayerCameraManager → GetCameraRotation → CamRot
  Get Forward Vector(CamRot) → Fwd        ← xác nhận node vào bảng 09
  ─ Tầng 1 ─
  LineTraceByChannel(Visibility, CamLoc, CamLoc + Fwd×1500)
    Hit  → SET PendingSpawnCenter = HitLocation
    Miss → ─ Tầng 2 (thả xuống từ điểm trước camera) ─
             Mid = CamLoc + Fwd×500
             LineTraceByChannel(Visibility, Mid+(0,0,1000), Mid−(0,0,5000))
               Hit  → SET PendingSpawnCenter = HitLocation
               Miss → SET PendingSpawnCenter = Mid   ← fallback tuyệt đối

★ Bước 3 — Kiểm item + build ValidItems (Q7):
  CLEAR PendingValidItems; CLEAR LocalMissing
  ForEach PendingComboData.Items (item):
    GetDataTableRow(DT_FurnitureCatalog, item.RowName) → found:
      True  → ADD item → PendingValidItems
      False → ADD item.RowName → LocalMissing
  LocalMissing.Length == PendingComboData.Items.Length → toast "Combo không dùng được", Return
  LocalMissing.Length  > 0 → toast "Thiếu " + LocalMissing.Length + " món"
  SET PendingLoadCount = PendingValidItems.Length

Bước 4 — Warm async cache (R1):
  SET bComboSpawnInFlight = True
  ForEach PendingValidItems (item):
    GetDataTableRow → MeshPath = Row.MeshFolderPath + "/" + item.RowName
    MakeSoftObjectPath → AsyncLoadAsset:
      Completed →
        SET LoadedCount = LoadedCount + 1   ← OUTPUT PIN của SET
        Branch (LoadedCount >= PendingLoadCount) AND bComboSpawnInFlight:
          True → SET bComboSpawnInFlight = False → gọi Custom Event DoSpawnCombo
          ← AND guard: chặn double-fire nếu 2 callback chạy sát nhau

★ DoSpawnCombo (Custom Event riêng — tách để rõ ràng):

Bước 5 — Remap GroupID (HAI VÒNG RIÊNG — Q giải thích tại sao):
  ⚠ Vòng 1 sinh ĐỦ ID trước, vòng 2 mới nối cha-con.
    Gộp 1 vòng: cha đứng sau con trong mảng → ParentToken chưa có → cây gãy.

  Vòng 1 — sinh ID:
  ForEach PendingComboData.Groups (g):
    GenerateGroupID → NewID → ADD TokenToNewID(g.Token, NewID)

  Vòng 2 — nối cây + thêm vào Groups:
  ForEach PendingComboData.Groups (g):
    Make S_GroupData:
      GroupID       = TokenToNewID[g.Token]
      GroupName     = g.Name
      ParentGroupID = g.ParentToken=="" ? ""
                      : Map_Find(TokenToNewID, g.ParentToken, Found) ? Found_Value : ""
      bIsLocked     = False
    ADD → InputManager.Groups
  SyncGroupsToContainer

Bước 6 — Spawn:
  DeselectAll
  ForEach PendingValidItems (item):
    GetDataTableRow → MeshPath = Row.MeshFolderPath + "/" + item.RowName
    SpawnFurnitureCopy(MeshPath, DAPath="",
      Location        = PendingSpawnCenter + item.RelLocation,
      Rotation        = item.RelRotation,
      Scale           = item.Scale,
      MaterialOverrides = item.MaterialOverrides,
      SurfaceType     = item.SurfaceType → Enum,
      bAutoSelect     = False,
      RowName         = item.RowName) → NewActor
    IsValid(NewActor) → Cast → SET GroupID = item.GroupToken=="" ? ""
                                             : TokenToNewID[item.GroupToken]
    ADD NewActor → SpawnedComboActors
  ← Mesh đã cache bước 4 → Load Blocking trong SpawnFurnitureCopy trúng cache

Bước 7 — Kết thúc:
  SelectActors(SpawnedComboActors)
  CaptureSnapshot("SpawnCombo")   ← 1 snapshot duy nhất
  Toast "✅ Đã đặt: " + PendingComboData.Name
  CLEAR SpawnedComboActors, PendingValidItems, TokenToNewID
```

**TEST T5 (PASS HẾT mới làm T6):**
```
1. Spawn combo 5 món có group → đủ 5, hình dạng đúng, select cả cụm, info bar hiện group
2. ⭐ Spawn CÙNG combo LẦN 2 → 2 cụm ĐỘC LẬP: move cụm 1, cụm 2 đứng yên. Print GroupID → khác
3. Undo → cả cụm biến 1 lần. Redo → quay lại đủ + group nguyên
4. Spawn khi Edit Mode → tự thoát rồi spawn
5. Sửa tay RowName trong .json thành tên bậy → spawn N-1 món + toast
6. Save EMS → Load → combo quay lại đúng
7. Spawn 20 món → không khựng quá 0.5s
```
→ **Báo cuhoang + bảng PASS/FAIL 7 case.**

---

### S5.T6 — TOÁN XOAY QUANH PIVOT (trả nợ T15)

**⚠ ĐỌC TRƯỚC KHI CODE (Q11, Q12):**
- Mở `BP_PivotActor.md` + `T15_Multi_Rotate_Scale_Plan.md` + node graph thật.
- Xác định: (a) actors đã attach vào pivot (UE tự orbit → T6 chỉ verify) hay (b) offset thủ công (→ cần code dưới).
- Tên biến thật chứa danh sách actors trên BP_PivotActor (doc gọi AttachedActors — đối chiếu thực tế).
- Node **RotateVector, CombineRotators**: search editor → cuhoang xác nhận → thêm bảng 09 TRƯỚC khi dùng (Q12).

**Công thức (giải sẵn):**
```
Với mỗi actor i, pivot P, delta rotation R:
  NewLoc_i = P + RotateVector(R, OldLoc_i − P)
  NewRot_i = CombineRotators(OldRot_i, R)

⚠ THỨ TỰ CombineRotators: OldRot TRƯỚC, Delta SAU.
  Ngược lại: đồ chưa xoay trông đúng, đồ có rotation sẵn ≠ 0 sẽ "trôi". Test case 3 bắt lỗi này.
```

**Code nếu cần (trường hợp b):**
```
Function ApplyPivotRotationDelta(DeltaRot : Rotator)
  P = GizmoPivotActor.GetActorLocation
  ForEach [TÊN BIẾN THẬT] (actor): IsValid →
    NewLoc = P + RotateVector(DeltaRot, GetActorLocation(actor) − P)
    NewRot = CombineRotators(GetActorRotation(actor), DeltaRot)
    SetActorLocation(actor, NewLoc)
    SetActorRotation(actor, NewRot)
  → RefreshOffsets (nếu cần)
Gọi từ: BP_GizmoController, chỗ đang áp rotation delta mỗi frame (cùng chỗ SnapAngle).
```

**TEST T6:**
```
1. 2 đồ 2 bên pivot, rotate 90° → đổi chỗ, mặt hướng đúng
2. Snap 15° mượt, không giật
3. ⭐ Đồ có rotation sẵn 45° → xoay tiếp 90° → ra đúng 135° + vị trí đúng
4. Undo sau xoay → về đúng
```
→ **Báo cuhoang.**

---

### S5.T7 — Tương tác hệ thống (kiểm, ít code mới)
1. Replace mode với combo-group: MeshesToReplace multi đã có → TEST.
2. Delete combo trong scene: DeleteSelected + PruneEmptyGroups → TEST.
3. RestoreSnapshot scene chứa combo: spawn combo → move → đổi material → Undo ×3 → Redo ×3.
4. Box select nửa combo → ExpandSelectionWithGroups nở cả cụm → TEST.
→ **Báo cuhoang + bảng PASS/FAIL 4 case.**

---

### S5.T8 — Regression + Docs
Regression: R1-R8 Sprint D + 7 case T5 + 4 case T6 + 4 case T7.

Docs (version + ngày + giờ + phút):
- `BP_FurnitureInputManager.md` → v1.8: 8 vars mới, SaveComboFromSelection, SpawnComboByID, DoSpawnCombo, OnComboLibraryChanged, ApplyPivotRotationDelta.
- `WBP_FurnitureInventory.md` → v2.5: AllComboViews, LoadComboLibrary, tab Combo, WBP_ComboCard.
- File mới `Combo_System.md`: schema v1, quy tắc naming, backward-compat, RowName là hợp đồng.
- `09_AI_Implementation_Rules.md`: thêm node đã dùng thật (RotateVector, CombineRotators, Get Forward Vector, Export Render Target, CreateDirectory — cuhoang xác nhận từng node).
- Session_State, PROGRESS, DEVIATIONS.
→ **Báo cuhoang. SPRINT 5 HOÀN TẤT.**

---

## 4. SỔ RỦI RO (12 tình huống + Plan B)
| # | Tình huống | Triệu chứng | Plan B |
|---|---|---|---|
| M1 | CombineRotators sai thứ tự | Đồ rotation sẵn xoay xong trôi | Đảo 2 input — chỉ có 2 khả năng |
| M2 | Async double-fire | Spawn gấp đôi | Guard bComboSpawnInFlight + AND callback |
| M3 | Remap 1 vòng | Cây nested gãy | Tách 2 vòng như bước 5 |
| M4 | 2 lần spawn dính | Move cụm 1, cụm 2 chạy | Kiểm SET GroupID có qua TokenToNewID không |
| M5 | Export Render Target fail | Không có .png | Icon 🧩 + tên. Ghi DEVIATIONS |
| M6 | Import File as Texture2D không tồn tại | Node không thấy | Icon 🧩. Backlog C++ FImageUtils |
| M7 | JSON tiếng Việt vỡ | Tên "???" | ForceUTF8WithoutBOM đã có. Kiểm app đọc encoding |
| M8 | Trace miss hoàn toàn | Combo lơ lửng | Fallback 2 tầng đã có bước 2 |
| M9 | Combo 50 món khựng | Đứng hình | Warm cache bước 4. Vẫn khựng → limit ≤30 món ở T2 |
| M10 | Tên combo ký tự lạ | File không tạo | Tên file = GUID. Đã xử lý |
| M11 | Catalog đổi RowName sau lưu | Item thiếu | Bước 3 skip + toast. RowName = hợp đồng — ghi Data.md |
| M12 | Kẹt C++ không có Fable | Compile error lạ | Tra bảng T1 → fail 3 lần: gác, gom hỏi Opus 1 lần với error+file+dòng |

---

## 5. ĐỊNH NGHĨA DONE
✅ Lưu combo (nested group + material) → card tab 🧩 → spawn 2 lần độc lập → xoay pivot đúng toán → undo/redo/save/load nguyên vẹn → regression PASS → docs cập nhật.
❌ Marketplace / giá tiền / đăng tải = B3, không thuộc Sprint 5.

---

## 6. BACKLOG
- "Chụp lại bìa combo" — nút cho phép set thumbnail từ góc camera tự chọn (B3 page người bán).
- "Recent combo" — tab Recent hiện combo vừa spawn.
- Ghost preview N mesh khi drag card (D4 defer).
- Limit ≤30 món validate khi lưu (nếu M9 xảy ra).
- C++ load PNG runtime FImageUtils (nếu M6 xảy ra).

---

## Lịch sử
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 12/06/2026 | Fable 5: schema v1, C++ đầy đủ, toán pivot, remap 2 vòng, 12 rủi ro |
| 1.1 | 12/06/2026 | Hợp nhất Q&A Sonnet 4.6: sửa T2 bước 3 (selection-only), 8 class vars, guard double-click, trace 2 tầng, CTV riêng, thumbnail đồng bộ, path join Q4, giải thích Q10 race |
| 1.2 | 19/06/2026 | Thêm DEVIATION block đầu file: BP_ComboManager tách riêng khỏi InputManager; luật dịch 6 điểm |
