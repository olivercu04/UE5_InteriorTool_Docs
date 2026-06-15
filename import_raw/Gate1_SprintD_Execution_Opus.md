# GATE 1 + SPRINT D — Fix B1, Hợp nhất Spawn, Data Layer v2 (EXECUTION step-by-step)
**Phiên bản:** 1.0 | **Ngày:** 11/06/2026 — Fable 5 | Lighting_Mnger UE5.5.4
**Đối tượng đọc:** model thực thi (Sonnet/Opus). Tuân thủ `09_AI_Implementation_Rules.md` (Q1-Q7, L1-L10, bảng node). Làm **TỪNG TASK MỘT**, mỗi task có test riêng, làm xong **báo cuhoang** rồi mới qua task sau.
**Vị trí trong roadmap:** chạy SAU khi Sprint 4 hoàn tất (T6-T8 + test 14 case), TRƯỚC Sprint 5 Combo.

---

## 0. BỐI CẢNH & LÝ DO (đọc trước, đừng quên giữa chừng)

### Roadmap v3.1 (điều chỉnh so với Master Plan v3.0)

```
Sprint 4 (Edit Mode) — hoàn tất T6-T8 trước
   ↓
★ GATE 1 — STABILIZE (file này, phần I):
   fix B1 + cờ bIsRestoring + hợp nhất spawn path + dọn doc
   ↓
★ SPRINT D — DATA LAYER v2 (file này, phần II):
   Furniture mode chuyển sang kiến trúc DataTable+RowName (giống Material mode)
   ↓
Sprint 5 — Combo Mesh (xây trên nền data mới)
   ↓
Sprint 7 — Material Edit v1.2 (ĐẢO lên trước Sprint 6 — không dependency, nằm trong chuỗi giá trị combo)
   ↓
Sprint 6 — Polish UX (Align/Distribute/Lock — cắt được nếu cần ship sớm)
   ↓
★ GATE 2 — FIRST PACKAGED BUILD (phần III)
```

### Vì sao Sprint D phải TRƯỚC Sprint 5
1. Sprint 5 thêm category "🧩 Combo" + card mới vào inventory. Làm combo trên nền data cũ rồi refactor data sau = làm combo card 2 lần.
2. Combo lưu member bằng **RowName** (nguyên tắc R5). Sprint D biến RowName thành định danh chính thức của furniture — combo serialization xây thẳng lên đó.
3. Bức tường hiệu năng: `AllFurnitureItems` pre-load toàn bộ DA vào RAM ở Event Construct. ~2k DA hiện tại = chịu được; 20k = treo 10-30s mỗi lần mở; 200k (mục tiêu thương mại) = chết hẳn trên máy yếu. Sprint D giết bức tường này TRƯỚC khi đổ thêm data vào.

### Nguyên tắc chỉ đạo Sprint D
> **KHÔNG phát minh. NHÂN BẢN Material mode sang Furniture mode.**
Material mode (~2738 rows) đã chạy đúng kiến trúc: DataTable rows → C++ filter trả `Array of Name` → pagination 48/trang → object nhẹ per page → Lazy Image. Furniture mode chỉ cần copy luồng đó. Mọi mảnh ghép đã tồn tại và đã test bằng data thật.

### ⚠️ 3 CHỈNH SỬA KỸ THUẬT so với thảo luận trong chat (Fable 5 tự sửa — bắt buộc theo bản này)
1. **`S_FurnitureData` là Blueprint struct (UserDefinedStruct)** → C++ KHÔNG dùng được `reinterpret_cast<FS_FurnitureData*>`. Phải dùng reflection như `FilterMaterialItems` hiện có, nhưng **cache FProperty 1 lần TRƯỚC loop** (xem D.T3).
2. **`S_FurnitureData` chưa có field thumbnail soft** (chỉ có `PreviewIcon` hard ref chưa dùng). Cần task data prep D.T2 (thêm field + Python populate) trước khi card đọc được thumbnail từ DT.
3. **Box select guard (Sprint 2) check `Is In Viewport`** để biết inventory đang mở. D.T1 chuyển inventory sang single-instance toggle Visibility → guard phải đổi sang check Visibility (xem D.T1.3).

### LEARNINGS BẮT BUỘC (kế thừa từ Sprint 1-4 — áp dụng mọi task)
- IsValid trước MỌI Object access (L1). Tất cả nhánh Branch merge về cuối (L2).
- CLEAR class var persistent ở ĐẦU function (bài học TempSelectedIndices).
- Code chạy 1 lần → nối **Completed** của ForEach, KHÔNG Loop Body.
- Latent node (Async Load, Delay, Timer) chỉ trong Custom Event, KHÔNG trong Function (L8).
- `BP_FurnitureActor`: Cast → GET `FurnitureMesh` (L6).
- Impure function feeding data pin → gọi sớm → SET temp var → node đọc temp var (bài học TempGroups).
- KHÔNG thêm furniture variables vào `BP_FoffPlayerController`.
- Hard ref clear ở End Play (Actor) / Event Destruct (Widget) — R4.
- Async Load path: String → `Make Soft Object Path` → `To Soft Object Reference` → `Async Load Asset`. Path phải dạng full object path `Package.AssetName`.

---

# PHẦN I — GATE 1: STABILIZE (2-3 ngày)

---

## G1.T1 — Cờ `bIsRestoring` (fix B1, nghi phạm số 1) ⭐ LÀM ĐẦU TIÊN

### Bối cảnh bug B1
Triệu chứng: Undo lần 1 restore group ĐÚNG, Undo lần 2 → `Groups.Length=0`. Chữ ký của bug "trạng thái bị sửa TRONG quá trình restore lần 1".

**Giả thuyết xếp hạng:**
- **H1 (nghi phạm số 1):** `RestoreSnapshot` Step 5/6b gọi `SelectActors` để re-fire selection → nếu bất kỳ đường nào trong SelectActors hoặc listener của `OnSelectionChanged` gọi `CaptureSnapshot` (pattern ToggleActor Sprint 1 có capture sau toggle) → snapshot MỚI bị chèn vào history GIỮA restore → redo stack bị cắt + CurrentIndex lệch → Undo lần 2 trỏ sai snapshot.
- **H2:** snapshot đích của Undo lần 2 thật sự lưu Groups rỗng (capture còn hở 1 đường — vd nhánh fail của `GetGroupsForSnapshot`).
- **H3:** có thứ CLEAR `InputManager.Groups` SAU Step 5b (listener `OnRestoreCompleted` hoặc `SyncGroupsToContainer` chạy ngược chiều).

Cờ `bIsRestoring` giết H1 tận gốc và vô hại với H2/H3 — nên làm dù H nào đúng.

### 1.1 Variable
`BP_UndoManager` → tạo `bIsRestoring : Boolean` (default False, KHÔNG SaveGame).

### 1.2 RestoreSnapshot — 2 chỗ chèn
```
Ngay SAU Function Entry (TRƯỚC Step 1 DeselectAll):
  SET bIsRestoring = True

Ngay TRƯỚC Step 7 (Broadcast OnRestoreCompleted):
  SET bIsRestoring = False
```
> Lý do đặt False TRƯỚC Broadcast: mọi re-fire SelectActors ở Step 5/6b (nguồn H1) đều bị chặn; listener của OnRestoreCompleted nếu cần capture hợp lệ thì vẫn chạy được.

### 1.3 CaptureSnapshot — guard đầu hàm
```
Ngay SAU Function Entry, TRƯỚC CẢ Step 0 (CLEAR TempSelectedIndices):
  Branch (bIsRestoring == True):
    True  → Return (thoát hàm, không capture)
    False → tiếp tục Step 0 như cũ
```

### 1.4 Event End Play
Thêm `SET bIsRestoring = False` cạnh các CLEAR có sẵn (vệ sinh).

### 1.5 Diagnostic Print (đặt trên MAIN execution line, KHÔNG trong loop)
```
Đầu RestoreSnapshot (sau SET bIsRestoring=True):
  Print: "RST idx=" + IndexHistory + " act=" + Snapshot.ActionName
       + " ver=" + Snapshot.Version + " grp=" + Snapshot.Groups.Length
       + " hist=" + SnapshotHistory.Length

Cuối RestoreSnapshot (trước Step 7):
  Print: "RST-END mgr.Groups=" + InputManager.Groups.Length
       + " hist=" + SnapshotHistory.Length
```

### TEST G1.T1
```
Kịch bản B1 gốc: Select 3 đồ → Ctrl+G → Move cả group → Undo → Undo
1. Sau Undo lần 2: info bar hiện group, log "RST-END mgr.Groups" > 0  → B1 FIXED
2. "hist" đầu vs cuối MỖI lần restore phải BẰNG nhau
   (trước fix, nếu H1 đúng thì nó lệch — đây là bằng chứng chốt án)
3. Regression: Undo/Redo xen kẽ Select/Deselect (kịch bản bug v1.5) vẫn đúng
4. Redo sau 2 Undo → quay lại đúng trạng thái group + selection
```
**Nếu vẫn fail:** đọc 2 dòng print:
- `grp=0` ngay đầu → H2 (bug capture) → soi snapshot theo ActionName, kiểm tra nhánh fail của GetGroupsForSnapshot có Return rỗng đúng chỗ không.
- `grp>0` đầu nhưng `mgr.Groups=0` cuối → H3 → tìm thứ clear Groups sau Step 5b (nghi: listener OnRestoreCompleted, SyncGroupsToContainer chạy ngược).
- Fail 3 lần → STOP, báo cuhoang, không đoán mò (quy tắc file 10).

→ **Làm xong báo cuhoang + dán 2 dòng log.**

---

## G1.T2 — Hợp nhất spawn path: RestoreSnapshot gọi SpawnFurnitureCopy

### Vấn đề
RestoreSnapshot Step 4 hiện **tự spawn inline** (Spawn → Load Blocking → Set Mesh → restore material) — là BẢN SAO của logic trong `SpawnFurnitureCopy`. Hai bản sao của cùng hành vi = Sprint 7 thêm MaterialParams sẽ phải sửa CẢ HAI, quên một là bug chỉ xuất hiện ở 1 đường. Hợp nhất TRƯỚC khi Sprint 5/7 xây lên.

### 2.1 Kiểm tra signature hiện có (Q1 — đọc trước khi làm)
`SpawnFurnitureCopy(MeshPath, DAPath, Location, Rotation, Scale, MaterialOverrides, SurfaceType, bAutoSelect) → NewActor` (output NewActor + bAutoSelect thêm từ Sprint 1 T11). Mở Blueprint xác nhận đúng signature này trước khi sửa — nếu khác, báo cuhoang.

### 2.2 Sửa RestoreSnapshot Step 4
```
ForEach Snapshot.Meshes (Placement):
  Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → IsValid:
    True → Call SpawnFurnitureCopy(
             MeshPath        = Placement.MeshPath,
             DAPath          = Placement.DAPath,
             Location        = Placement.Location,
             Rotation        = Placement.Rotation,
             Scale           = Placement.Scale,
             MaterialOverrides = Placement.MaterialPaths,
             SurfaceType     = Placement.SurfaceType,
             bAutoSelect     = False)                ← KHÔNG tự select
           → NewActor (output):
             Cast To BP_FurnitureActor → SET GroupID = Placement.GroupID   ← v1.6 giữ nguyên
             ADD NewActor to SpawnedActors
```
> ⚠️ Cache InputManager ref 1 lần TRƯỚC ForEach (SET local/class var), KHÔNG Get All Actors trong loop body (Q6).
> ⚠️ `SpawnFurnitureCopy` có làm bước ADD tag "FurnitureSpawned" sẵn (Step 3 của nó) — xóa đoạn ADD tag inline cũ trong RestoreSnapshot, KHÔNG add 2 lần.
> ⚠️ Nếu SpawnFurnitureCopy có nhánh latent (Async) → ForEach sẽ không đợi. Kiểm tra: hiện tại nó dùng Load Asset Blocking (đồng bộ) → an toàn. NẾU phát hiện nó async → STOP, báo cuhoang (sẽ cần counter pattern, không tự chế).

### 2.3 Xóa code spawn inline cũ ở Step 4 (sau khi test pass — không xóa trước)

### TEST G1.T2 (regression nặng — Undo là xương sống)
```
1. Spawn 3 đồ + đổi material 1 đồ → Move → Undo → material + vị trí đúng
2. Delete 1 đồ → Undo → đồ quay lại đúng mesh + material + GroupID
3. Kịch bản B1 (group) chạy lại → vẫn PASS
4. Save → Load → Undo → không crash, không đồ ma
5. Spawn → Undo về "Initial" → scene trống
```
→ **Làm xong báo cuhoang + bảng PASS/FAIL 5 case.**

---

## G1.T3 — Dọn doc (30 phút, bắt buộc — chống doc drift)
1. `PROGRESS.md`: cập nhật Sprint 3 = SHIPPED, Sprint 4 = trạng thái thật, thêm mục Gate 1 + Sprint D.
2. `DEVIATIONS.md`: điền bảng Sprint 3 + Sprint 4 (mục 5 của Sprint4_Execution đã liệt kê sẵn 5 dòng Sprint 4).
3. `Session_State.md`: B1 status mới + roadmap v3.1.
4. `BP_UndoManager.md` → v1.7: bIsRestoring + spawn qua SpawnFurnitureCopy. Ghi version + ngày + giờ + phút.

→ **Làm xong báo cuhoang.**

---

# PHẦN II — SPRINT D: DATA LAYER v2 (4-6 ngày)

---

## Tổng quan kiến trúc Sprint D

```
TRƯỚC (Furniture mode):                      SAU (giống Material mode):
Event Construct:                             Event Construct:
  GetAllAssets → load TOÀN BỘ DA               (không load gì nặng)
  → AllFurnitureItems (RAM)                  Search/Filter:
Search/Filter:                                 C++ FilterFurnitureRows(DT)
  C++ filter trên mảng UObject                 → Array of Name (RowNames)
  → Array of UPrimaryDataAsset*                → DisplayPage: 48 rows/trang
  → đổ ≤200 obj vào Tile View                  → Create BP_FurnitureItemView nhẹ
                                               → Lazy Image per card
```

**Single Source of Truth mới:** `DT_FurnitureCatalog` là nguồn đọc DUY NHẤT của inventory. `DA_FurnitureItem` chuyển trạng thái legacy (không xóa — DAPath trong save cũ còn tham chiếu), inventory KHÔNG đọc DA nữa.

**Thứ tự thực thi:**
```
D.VS (vertical slice — kill risk): D.T2 → D.T3 → D.T4 → D.T5 → TEST BROWSE
SAU ĐÓ:                            D.T6 (drag-drop — rủi ro nhất) → D.T1 → D.T7 → D.T8
CUỐI:                              D.T9 regression + docs
```
> D.T1 (single instance) dời SAU D.VS vì nó độc lập và D.VS cần test mở/đóng inventory nhiều lần kiểu cũ trước. D.T6 là task rủi ro nhất — chỉ làm khi browse flow đã vững.

---

## D.T2 — Data prep: field ThumbnailSoft + Python populate ⭐ LÀM ĐẦU

### 2.1 Thêm field vào S_FurnitureData (Blueprint struct)
- Mở struct `S_FurnitureData` → thêm field `ThumbnailSoft : Soft Object Reference (Texture2D)`.
- ⚠️ **Backup project/commit TRƯỚC khi sửa struct** — sửa UserDefinedStruct đang được DataTable + nhiều BP dùng có thể dirty hàng loạt asset. Sửa xong: save all, restart editor nếu thấy compile lạ.
- ⚠️ KHÔNG xóa/đổi field cũ (PreviewIcon giữ nguyên dù không dùng — additive, không breaking).

### 2.2 Python script populate ThumbnailSoft
Chạy trong Output Log (Python). Mirror script 5 (ThumbnailPath của Material) — hỏi cuhoang **folder chứa thumbnail furniture** trước khi chạy (script dưới giả định, cuhoang sửa `thumb_path`):

```python
import unreal, json

dt = unreal.load_asset("/Game/cuong/UI/Data/DT_FurnitureCatalog")
thumb_path = "/Game/cuong/UI/Data/ThumbnailFurniture"   # ← cuhoang XÁC NHẬN path thật

ar = unreal.AssetRegistryHelpers.get_asset_registry()
ar.scan_paths_synchronous([thumb_path], True)   # bắt buộc — Content Browser != Asset Registry

f = unreal.ARFilter(class_names=["Texture2D"], recursive_paths=True, package_paths=[thumb_path])
thumb_map = {str(a.asset_name): str(a.package_name) for a in ar.get_assets(f)}
print(f"Textures found: {len(thumb_map)}")

rows = json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(dt))
updated, missing = 0, 0
for row in rows:
    name = row["Name"]
    if name in thumb_map:
        p = thumb_map[name]
        # Soft Object Reference cần full object path: /Game/.../T_Name.T_Name
        row["ThumbnailSoft"] = p + "." + p.split("/")[-1]
        updated += 1
    else:
        missing += 1

unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(dt, json.dumps(rows, ensure_ascii=False))
unreal.EditorAssetLibrary.save_asset("/Game/cuong/UI/Data/DT_FurnitureCatalog")
print(f"Updated: {updated} | Missing: {missing}")
```
> ⚠️ Tên thumbnail phải match RowName. Nếu naming khác (vd `T_<RowName>`), sửa key matching trong script — hỏi cuhoang naming convention thật.
> ⚠️ Ghi vào `Python_Scripts.md` (script số 7) sau khi chạy OK, kèm kết quả Updated/Missing.
> ⚠️ Pipeline note: sau MỌI lần reimport CSV từ Google Sheets → chạy lại script này (CSV reimport xóa field do Python populate). Thêm dòng nhắc vào mục "Lưu ý chung" của Python_Scripts.md.

### TEST D.T2
Mở DT_FurnitureCatalog → vài row bất kỳ có ThumbnailSoft trỏ đúng texture. Số Missing hợp lý (≈ số mesh chưa có thumbnail).
→ **Làm xong báo cuhoang + con số Updated/Missing.**

---

## D.T3 — C++ `FilterFurnitureRows` (FurnitureToolkit plugin)

> cuhoang KHÔNG biết C++ — đưa code ĐẦY ĐỦ, chỉ rõ file nào, dán vào đâu. TRƯỚC KHI VIẾT: mở `FurnitureFilterLibrary.h/.cpp` hiện có, đọc `FilterMaterialItems` để mirror đúng style include/namespace/macro của project. Code dưới là REFERENCE — align theo file thật.

### 3.1 Khai báo (FurnitureFilterLibrary.h, thêm vào class có sẵn)
```cpp
/** Lọc DT_FurnitureCatalog, trả RowNames. Không load DA, không load mesh. */
UFUNCTION(BlueprintCallable, Category = "Furniture")
static TArray<FName> FilterFurnitureRows(
    UDataTable* Catalog,
    const FString& SearchText,
    const FString& FolderPath,
    FName CategoryFilter,
    int32 MaxResults = 20000);
```

### 3.2 Định nghĩa (FurnitureFilterLibrary.cpp)
```cpp
TArray<FName> UFurnitureFilterLibrary::FilterFurnitureRows(
    UDataTable* Catalog, const FString& SearchText,
    const FString& FolderPath, FName CategoryFilter, int32 MaxResults)
{
    TArray<FName> Results;
    if (!Catalog) return Results;

    const UScriptStruct* RowStruct = Catalog->GetRowStruct();
    if (!RowStruct) return Results;

    // ⭐ S_FurnitureData là Blueprint struct → bắt buộc reflection.
    // Cache FProperty 1 LẦN trước loop — KHÔNG FindFProperty trong loop (200k rows).
    // ⚠️ BP struct property có tên mangled (vd "VieName_3_ABC123...") →
    //    KHÔNG dùng FindFProperty theo tên cứng. Duyệt PropertyLink,
    //    match bằng GetAuthoredName() (trả tên gốc "VieName").
    const FProperty* VieNameProp = nullptr;
    const FProperty* EngNameProp = nullptr;
    const FProperty* TagsProp = nullptr;
    const FProperty* FolderProp = nullptr;
    const FProperty* CategoryProp = nullptr;
    for (TFieldIterator<FProperty> It(RowStruct); It; ++It)
    {
        const FString AuthoredName = It->GetAuthoredName();
        if      (AuthoredName == TEXT("VieName"))        VieNameProp  = *It;
        else if (AuthoredName == TEXT("EngName"))        EngNameProp  = *It;
        else if (AuthoredName == TEXT("Tags"))           TagsProp     = *It;
        else if (AuthoredName == TEXT("MeshFolderPath")) FolderProp   = *It;
        else if (AuthoredName == TEXT("Category"))       CategoryProp = *It;
    }

    const bool bHasSearch = !SearchText.IsEmpty();
    const bool bHasCategory = !CategoryFilter.IsNone();

    for (const TPair<FName, uint8*>& Pair : Catalog->GetRowMap())
    {
        const uint8* RowData = Pair.Value;
        if (!RowData) continue;

        // --- Folder filter: Contains("",x)=true → node "All" hiện tất cả (giữ hành vi cũ)
        if (FolderProp)
        {
            FString FolderVal;
            FolderProp->ExportText_InContainer(0, FolderVal, RowData, RowData, nullptr, PPF_None);
            if (!FolderVal.Contains(FolderPath)) continue;
        }

        // --- Category filter
        if (bHasCategory && CategoryProp)
        {
            FString CatVal;
            CategoryProp->ExportText_InContainer(0, CatVal, RowData, RowData, nullptr, PPF_None);
            if (!CatVal.Equals(CategoryFilter.ToString(), ESearchCase::IgnoreCase)) continue;
        }

        // --- Search: match VieName / EngName / Tags / RowName, case-insensitive
        if (bHasSearch)
        {
            bool bMatch = Pair.Key.ToString().Contains(SearchText, ESearchCase::IgnoreCase);
            auto MatchProp = [&](const FProperty* P) -> bool {
                if (!P) return false;
                FString V;
                P->ExportText_InContainer(0, V, RowData, RowData, nullptr, PPF_None);
                return V.Contains(SearchText, ESearchCase::IgnoreCase);
            };
            if (!bMatch) bMatch = MatchProp(VieNameProp) || MatchProp(EngNameProp) || MatchProp(TagsProp);
            if (!bMatch) continue;
        }

        Results.Add(Pair.Key);
        if (Results.Num() >= MaxResults) break;
    }
    return Results;
}
```
> ⚠️ Nếu `FilterMaterialItems` hiện có dùng cách đọc property khác (vd FTextProperty cast trực tiếp) → MIRROR cách đó cho nhất quán, miễn là cache property ngoài loop. `ExportText_InContainer` chậm hơn typed-cast một chút nhưng an toàn với mọi kiểu field; ở 200k rows vẫn ~chục ms.
> ⚠️ Compile fail → dán nguyên error cho model thực thi, KHÔNG tự sửa mò.

### 3.3 Test node trong Blueprint (trước khi nối vào UI)
Tạo test tạm trong Level BP hoặc InputManager:
```
Phím T (test) → FilterFurnitureRows(DT_FurnitureCatalog, "", "", None, 20000)
  → Length → Print "Total rows: X"
→ FilterFurnitureRows(DT, "sofa", "", None, 20000) → Length → Print "Sofa: Y"
```
Kỳ vọng: X = tổng rows DT; Y > 0 nếu có sofa. Xóa test node sau khi pass.
→ **Làm xong báo cuhoang + 2 con số.**

---

## D.T4 — `BP_FurnitureItemView` (UObject nhẹ — clone BP_MaterialItem)

### 4.1 Tạo Blueprint Class, parent = **Object**, tên `BP_FurnitureItemView`
(KHÔNG đặt tên BP_FurnitureItem — tránh nhầm DA_FurnitureItem)

Variables (tất cả Instance Editable = false, chỉ SET runtime):
```
RowName        : Name
VieName        : Text
EngName        : Text
ThumbnailSoft  : Soft Object Reference (Texture2D)
MeshSoft       : Soft Object Reference (Static Mesh)
MeshFolderPath : String
BoundingSize   : Vector
Description    : String
Link           : String
Category       : Name
```
> Mirror đúng pattern BP_MaterialItem đang dùng với CTV_MaterialCard. Object nhẹ này CHÍNH LÀ "struct data nhẹ" của R3 — widget không bao giờ cầm DA/Actor nặng.

### TEST D.T4: compile sạch. → **Báo cuhoang, qua D.T5 luôn được (task nhỏ).**

---

## D.T5 — FilterBySearch nhánh Furniture → rows + DisplayPage hợp nhất

### 5.1 Variable mới (WBP_FurnitureInventory)
```
AllFilteredFurnitureRows : Array of Name   ← cache kết quả filter (mirror AllFilteredMaterialRows)
```

### 5.2 Sửa `FilterBySearch` nhánh Furniture (False branch của Branch Material)
```
CŨ:  FilterFurnitureItems(C++) → ForEach → AddItem(CTV_FurnitureCard)
MỚI: FilterFurnitureRows(DT_FurnitureCatalog, CurrentSearchText,
       CurrentFolderPath, CurrentCategory, MaxResults=20000)
     → SET AllFilteredFurnitureRows
     → SET CurrentPage = 0
     → Call DisplayPage
```
> Recent/Favorite (ActiveSpecialCategory != ""): nhánh đặc biệt KHÔNG gọi filter C++ — build AllFilteredFurnitureRows trực tiếp từ list RowName của BP_FurnitureUserPrefsManager (đã RowName-based sẵn), rồi DisplayPage. Đối chiếu logic Recent/Favorite hiện có trong FilterBySearch trước khi sửa — giữ nguyên hành vi, chỉ đổi đích ghi từ "đổ DA vào tile" sang "đổ RowName vào AllFilteredFurnitureRows".

### 5.3 Mở rộng `DisplayPage` cho 2 mode
```
ĐẦU HÀM: Branch CurrentInventoryMode:
  == Material  → (luồng cũ giữ nguyên) + ⭐ THÊM Clear List Items(CTV_MaterialCard)
                 TRƯỚC ForLoop nếu chưa có (fix bug tiềm ẩn dồn item khi lật trang)
  == Furniture →
    Clear List Items(CTV_FurnitureCard)
    Start = CurrentPage × PageSize
    End   = Min(Start + PageSize, Length(AllFilteredFurnitureRows)) - 1
    ForLoop Start → End (i):
      Get Data Table Row(DT_FurnitureCatalog, AllFilteredFurnitureRows[i]) → Row
      Construct Object from Class(BP_FurnitureItemView, Outer=Self)
        → SET RowName = AllFilteredFurnitureRows[i]
        → SET VieName/EngName/ThumbnailSoft/MeshSoft (từ Row.StaticMesh)/
              MeshFolderPath/BoundingSize/Description/Link/Category (từ Row)
      → Add Item(CTV_FurnitureCard, ItemView)
    Completed →
      TotalPages = (Length(AllFilteredFurnitureRows) + PageSize - 1) / PageSize
        ← integer math thuần, KHÔNG Ceil float (bài học v2.2)
      SET Text(ET_PageDisplay, (CurrentPage+1) + "/" + TotalPages)
```
> ⚠️ Node tạo object runtime: `Construct Object from Class` — node này tồn tại UE5.5, BP_MaterialItem đang được tạo bằng nó trong DisplayPage Material (xác nhận bằng cách mở xem). Nếu Material đang dùng node khác → dùng đúng node đó.
> ⚠️ Nút pagination Prev/Next hiện gọi DisplayPage — sau sửa sẽ tự chạy đúng cho cả 2 mode, kiểm tra không có chỗ nào hardcode Material.

### TEST D.T5 (BROWSE — vertical slice checkpoint)
```
1. Mở inventory → grid furniture hiện, thumbnail load lazy (card mới hiện ảnh sau ~1 frame)
2. Search "sofa" → kết quả đúng, pagination "1/N" đúng
3. Click folder tree → filter đúng theo folder
4. Lật trang 1→2→3→1 → KHÔNG dồn item, card đúng 48/trang
5. Switch tab Material → Furniture → cả 2 grid đúng
6. Recent/Favorite tab → hiện đúng list
```
→ **Làm xong báo cuhoang + bảng PASS/FAIL. PASS hết mới qua D.T6.**

---

## D.T6 — WBP_FurnitureCard đọc ItemView + drag-drop/popup/replace ⭐ RỦI RO NHẤT

> Task này chạm 4 luồng: card display, DetailPopup, drag-drop spawn, Replace mode. Làm từng luồng, test từng luồng.

### 6.1 Card variables
`WBP_FurnitureCard`: thêm `ItemView : BP_FurnitureItemView`. GIỮ `FurnitureDA` tạm thời (additive — xóa ở D.T9 sau khi mọi đường chuyển xong).

### 6.2 OnListItemObjectSet
```
CŨ:  Cast → DA_FurnitureItem → SET FurnitureDA → Set Brush from Lazy Texture
MỚI: Cast → BP_FurnitureItemView → SET ItemView
     → Set Brush from Lazy Texture(LazyImage_Thumb, ItemView.ThumbnailSoft)
     → Branch IsValid(InventoryRef): False → Get GameInstance → SET InventoryRef (giữ nguyên)
     → Call UpdateFavTint
```

### 6.3 Favorite (đơn giản hóa — RowName có sẵn, bỏ Get Object Name)
```
Button_FavoriteFurniture OnClicked:
  GET ItemView → GET RowName → Toggle Favorite Mesh(RowName) → UpdateFavTint
UpdateFavTint: GET ItemView.RowName → Is Favorite Mesh(RowName) → tint như cũ
```

### 6.4 DetailPopup
`OnCardInfoClicked` đổi param từ DA sang ItemView (hoặc truyền từng field). `WBP_DetailPopup` đọc VieName/Description/Link/Thumbnail từ ItemView. BTN_BuyLink: Launch URL(ItemView.Link).
> Đối chiếu `WBP_DetailPopup.md` trước khi sửa — popup có nút BTN_ChangeMesh (Replace flow) đọc gì từ DA thì map sang ItemView tương ứng.

### 6.5 Drag-drop spawn (NHẠY NHẤT — đối chiếu WBP_DragOverlay_FurnitureCard.md trước)
Luồng cũ: drag card → ghost preview mesh → drop → spawn. Mesh lấy từ DA. Luồng mới:
```
On Drag Detected (hoặc nơi spawn ghost hiện tại):
  GET ItemView → GET MeshSoft → Async Load Asset (trong Custom Event — L8)
  → Completed: spawn/refresh PreviewActor với mesh đã load
  ← Async: ghost có thể xuất hiện trễ 1-2 frame so với trước (mesh chưa cache).
    Chấp nhận được. KHÔNG đổi sang Load Blocking (R1).
On Drop:
  MeshPath cho BP_FurnitureActor = Soft Object Reference → Get Asset Path/To String
  DAPath: GIỮ tương thích — build từ convention nếu code cũ cần, nhưng từ D.T8
  RowName là định danh chính. Đối chiếu code drop hiện tại: nó SET gì lên actor
  thì map đủ từng field, KHÔNG bỏ sót SurfaceType/Scale.
```
> ⚠️ Đây là chỗ dễ vỡ nhất Sprint D. Quy tắc: mở node graph cũ, liệt kê MỌI chỗ đọc `FurnitureDA.*`, map từng cái sang `ItemView.*` — làm checklist trước khi sửa, đưa cuhoang xem checklist đó.

### 6.6 Replace mode
`EnterReplaceMode/ExitReplaceMode/RefreshCardReplaceMode` dùng Regenerate All Entries — không đổi. `OnMeshSelected` Trigger 3 (Replace navigate folder) hiện `Load Asset Blocking(DAPath) → GET MeshFolderPath`: đổi sang đọc từ DT — `Cast actor → GET RowName (sau D.T8) → Get Data Table Row → MeshFolderPath`. NẾU actor cũ chưa có RowName (save cũ) → fallback đường DAPath cũ (Branch RowName == None). Tạm thời ở D.T6 GIỮ nguyên đường DAPath, chỉ ghi TODO — sửa hẳn ở D.T8.

### TEST D.T6
```
1. Drag card → ghost hiện → drop → spawn đúng mesh, đúng surface snap
2. Spawn xong: select/move/material/undo trên đồ mới — nguyên vẹn
3. Info popup: tên/mô tả/link đúng; BuyLink mở URL
4. Favorite toggle từ card → tab Favorite thấy
5. Replace mode: BTN_Replace → click đồ trong scene → navigate folder đúng → ChangeMesh hoạt động
6. Regression: spawn từ Material tab không hỏng
```
→ **Làm xong báo cuhoang + bảng PASS/FAIL.**

---

## D.T1 — Inventory single-instance (fix construct lặp lại) — làm SAU D.T6

### 1.1 Level Blueprint
```
CŨ:  InputAction OpenFurnitureInventory → FlipFlop A: Create+Add / B: Remove from Parent
MỚI: InputAction OpenFurnitureInventory →
  Cast Foff_GameInstance → GET FurnitureInventoryRef → IsValid:
    False → Create WBP_FurnitureInventory → Add to Viewport
            → SET FurnitureInventoryRef (GameInstance) → Show Mouse Cursor
    True  → Branch (Get Visibility == Visible):
              True  → Set Visibility(Collapsed)
              False → Set Visibility(Visible) → Show Mouse Cursor
```
> Event Construct giờ chạy 1 LẦN/level → toàn bộ BuildFolderTree/bind chỉ trả giá 1 lần.

### 1.2 ⭐ Sửa box-select guard (BẮT BUỘC — nếu quên, box select bật cả khi inventory đóng)
Sprint 2 guard trong `BP_FurnitureInputManager` Tick: `IsValid(InventoryRef) AND Is In Viewport`. Với single instance, widget LUÔN in viewport → guard mất tác dụng.
```
ĐỔI: IsValid(InventoryRef) AND (Get Visibility(InventoryRef) == Visible)
```
Tìm MỌI chỗ khác check "Is In Viewport" trên inventory (search node) — đổi cùng cách. Liệt kê các chỗ đã đổi cho cuhoang.

### 1.3 Ghi chú VRAM
Event Destruct của inventory giờ chỉ fire khi end level — vẫn đúng R4. Khi Collapsed, `TargetFurnitureActor` có thể còn ref → đã có sẵn logic OnMeshDeselected clear; không cần thêm.

### TEST D.T1
```
1. Mở/đóng inventory 10 lần → lần 2+ mở TỨC THÌ (không hitch load)
2. Đóng inventory → kéo box select NGOÀI scene → box KHÔNG xuất hiện (guard mới)
3. Mở inventory → box select trong viewport vẫn hoạt động như cũ
4. Search text + folder đang chọn GIỮ NGUYÊN sau đóng/mở (bonus của single instance)
5. PIE 2-3 lần liên tiếp → không crash VRAM bất thường hơn baseline
```
→ **Làm xong báo cuhoang.**

---

## D.T7 — BuildFolderTree từ DT + XÓA AllFurnitureItems preload

### 7.1 BuildFolderTree
Hiện đọc DA_ để xây Map. Đổi nguồn: `Get Data Table Row Names(DT_FurnitureCatalog)` → cần MeshFolderPath per row → 200k rows duyệt trong Blueprint = CHẾT (execution limit ~1852).
**Giải pháp: thêm hàm C++** (cùng file FurnitureFilterLibrary):
```cpp
/** Trả danh sách MeshFolderPath duy nhất (distinct) — Blueprint xây tree từ đây. */
UFUNCTION(BlueprintCallable, Category = "Furniture")
static TArray<FString> GetDistinctFolderPaths(UDataTable* Catalog);
// Implement: loop RowMap (reflection cached như D.T3), TSet<FString> dedupe, return array.
// Số folder distinct thường vài trăm → Blueprint xây Map từ đây thoải mái.
```
Blueprint: `GetDistinctFolderPaths → ForEach → tách path xây FolderTree Map` (logic tách giữ từ BuildFolderTree cũ — chỉ đổi nguồn input).

### 7.2 Event Construct — xóa preload
```
Then 1 CŨ: CLEAR AllFurnitureItems → GetAllAssets → ForEach Cast → ADD → Bind → FilterBySearch
Then 1 MỚI: BindCategoryEvents → FilterBySearch   ← bỏ hẳn đoạn load
```
Variable `AllFurnitureItems`: chưa xóa — đánh dấu deprecated, xóa ở D.T9 sau khi search toàn project không còn ai đọc.

### TEST D.T7
```
1. Mở inventory LẦN ĐẦU sau PIE start → đo cảm quan: nhanh hơn rõ rệt
2. Folder tree đầy đủ, click các cấp filter đúng
3. Search + category + Recent/Favorite — tất cả hoạt động (giờ 100% từ DT)
```
→ **Làm xong báo cuhoang.**

---

## D.T8 — R5 cho save: BP_FurnitureActor.RowName (additive)

### 8.1
`BP_FurnitureActor` thêm `RowName : Name (SaveGame, default None)`.

### 8.2 Mọi điểm spawn SET RowName
Chỉ còn 1 đường spawn sau G1.T2 = `SpawnFurnitureCopy`. Thêm input param `RowName : Name` (default None) → trong hàm SET lên actor. Caller: drag-drop (D.T6 — có ItemView.RowName), PasteMesh/DuplicateMesh (lấy từ actor gốc), RestoreSnapshot (từ Placement — cần 8.3).

### 8.3 Snapshot mang RowName
`S_FurniturePlacement` thêm `RowName : Name`. CaptureSnapshot Step 3 ghi từ actor. RestoreSnapshot truyền vào SpawnFurnitureCopy. Snapshot Version GIỮ 3 (field mới default None = vô hại với snapshot cũ trong RAM; snapshot không persist qua session nên không cần bump).

### 8.4 Resolve khi load (EMS) — Event ActorLoaded
```
Branch (RowName != None):
  True  → Get Data Table Row(DT, RowName) → MeshFolderPath + "/" + RowName = mesh path → load
  False → fallback MeshPath cũ (save cũ vẫn sống — additive, không breaking)
```
> Từ đây: đồng nghiệp đổi tên folder mesh → chạy Python script 2 (update MeshFolderPath) → mọi save MỚI tự lành. Save cũ theo đường MeshPath vẫn đọc được như trước.

### TEST D.T8
```
1. Spawn mới → Save → đóng PIE → Load → đồ về đúng (đường RowName — Print xác nhận nhánh True)
2. Load save CŨ (trước D.T8) → vẫn về đúng (nhánh fallback)
3. Copy/Paste/Duplicate/Undo → RowName theo đồ (Print kiểm tra)
```
→ **Làm xong báo cuhoang.**

---

## D.T9 — Tổng kết: regression + dọn + docs

### 9.1 Regression toàn tuyến (chạy hết, bảng PASS/FAIL)
```
R1. Single select / multi select / box select / context menu
R2. Group: Ctrl+G, ungroup, edit mode (Sprint 4), nested
R3. Undo/Redo: kịch bản B1 + xen kẽ select/deselect + material + group
R4. Save/Load EMS: save mới + save cũ
R5. Material tab: filter, apply, favorite, pagination
R6. Furniture tab: browse, search, folder, drag-drop spawn, replace, popup
R7. Recent/Favorite cả 2 tab
R8. Mở/đóng inventory 10 lần + PIE 3 lần — VRAM ổn
```

### 9.2 Dọn (chỉ sau khi R PASS hết)
- Xóa variable `AllFurnitureItems` + mọi node đọc nó.
- Xóa `FurnitureDA` khỏi WBP_FurnitureCard nếu không còn ai đọc (search trước).
- Hàm C++ `FilterFurnitureItems` cũ: GIỮ (DA-based, có thể nơi khác gọi) — đánh dấu deprecated trong comment.

### 9.3 Docs (version + ngày + giờ + phút)
- `WBP_FurnitureInventory.md` → v3.0: luồng row-based, DisplayPage 2 mode, single instance.
- `Data.md`: S_FurnitureData +ThumbnailSoft; S_FurniturePlacement +RowName; BP_FurnitureActor +RowName; DA_FurnitureItem đánh dấu legacy.
- `Python_Scripts.md`: script 7 + nhắc reimport CSV.
- `performance.md`: gạch mục TECHNICAL DEBT AllFurnitureItems (đã xử lý), ghi kết quả đo.
- `09_AI_Implementation_Rules.md`: thêm node mới vào bảng (Construct Object from Class, Get Data Table Row Names, Clear List Items, Get Visibility — node nào cuhoang xác nhận thì thêm).
- `Session_State.md` + `PROGRESS.md` + `DEVIATIONS.md`.

→ **Làm xong báo cuhoang. SPRINT D HOÀN TẤT — sẵn sàng Sprint 5.**

---

# PHẦN III — GHI CHÚ CHO TƯƠNG LAI (không thực thi bây giờ)

## Cảnh báo bug Sprint 5 (Combo) — đọc khi lập plan Sprint 5
1. **GroupID remap:** spawn combo phải remap CẢ GroupID lẫn ParentGroupID của mọi sub-group. Test bắt buộc: spawn cùng 1 combo 2 LẦN trong 1 scene — nếu remap thiếu, 2 bản "dính" nhau qua ID trùng.
2. **Spawn combo khi đang Edit Mode:** chưa định nghĩa. Đề xuất chốt: spawn combo → ExitEditModeFull trước (đơn giản nhất).
3. **Toán rotate quanh pivot cho paste-combo-xoay:** nợ từ S1.T15 — dành thời gian riêng, đừng để bất ngờ.
4. **Async spawn N mesh + select:** cần counter "loaded N/N" rồi mới SelectActors — không select actor chưa có mesh.
5. Combo member list dùng **RowName** (đã có từ D.T8) — KHÔNG dùng MeshPath.

## Gate 2 — First Packaged Build (sau Sprint 5, trước khi đầu tư Sprint 7/6)
1. Build packaged lần đầu. Smoke test: spawn/select/move/group/undo/save/load.
2. **Verify P1:** `UniqueID = Get Display Name` trong CaptureSnapshot — hành vi khác giữa editor/packaged. Nếu Undo selection sai trong build → thay bằng GUID: BP_FurnitureActor thêm `ActorGUID : String (SaveGame)`, SET = `New Guid → To String` trong SpawnFurnitureCopy; CaptureSnapshot match bằng ActorGUID thay Display Name.
3. **Verify P4:** GPU VRAM crash (Streamline) có theo vào packaged không. Nếu có → tắt/loại plugin Streamline cho build ship.
4. Debug Print String: gate bằng biến `bDebugMode` (1 chỗ tắt), KHÔNG xóa tay.
5. Phím tắt: rà phím trùng editor (F8 = eject PIE) — packaged không sao, nhưng quyết định binding cuối trước khi dạy user.

## Ngưỡng scale tiếp theo (đối chiếu Future_Architecture_1M_Assets.md)
| Quy mô thật | Hành động |
|---|---|
| ≤50k rows | Sprint D là ĐỦ — đừng làm gì thêm |
| >50k hoặc cần full-text tiếng Việt | Phase v2: SQLite metadata |
| User upload / cloud | Phase v3-v4: blob store + glTFRuntime |

---

## TÓM TẮT THỨ TỰ CHO MODEL THỰC THI

```
G1.T1 (bIsRestoring + test B1) → G1.T2 (hợp nhất spawn) → G1.T3 (docs)
→ D.T2 (data prep) → D.T3 (C++ filter) → D.T4 (ItemView) → D.T5 (DisplayPage) [TEST BROWSE]
→ D.T6 (card/drag-drop — rủi ro nhất) → D.T1 (single instance + guard)
→ D.T7 (folder tree + xóa preload) → D.T8 (RowName R5) → D.T9 (regression + docs)
```
Mỗi task: làm xong báo cuhoang + test PASS/FAIL. Bug fail 3 lần → STOP, báo, không đoán mò.
