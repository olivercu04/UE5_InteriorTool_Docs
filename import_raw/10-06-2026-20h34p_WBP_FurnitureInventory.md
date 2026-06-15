# WBP_FurnitureInventory
**Phiên bản:** 2.4 | **Cập nhật:** 10/06/2026 — 20:34 ICT

> **v2.4 (Refactor dispatcher 10/06):** bind `OnSelectionChanged` thay cho `OnMeshSelected`/`OnMeshDeselected` (đã bị xóa ở InputManager). Thêm handler `OnSelectionChangedMaterial(Actors, Primary)` → gọi `OnMeshSelected(Primary)` (handler nội bộ tái dùng). `OnMeshSelected` (nội bộ): nhánh replace SET `MeshesToReplace` (array) thay `MeshToReplace` (single chết); nhánh material thêm guard `IsValid` (chống Accessed None khi deselect). Xóa handler `OnMeshDeselected`. `EnterReplaceMode` gọi `EnsureExpanded` đầu hàm. Đọc kèm `Sprint3_Regression_DualDispatcher_Log.md`.
Inventory duyệt & lọc nội thất + **Material Editor (v1.1 — HOÀN THÀNH)**

## 4B. WBP_FURNITURE INVENTORY

### Mục tiêu & Hiệu năng
- Duyệt, lọc, tìm kiếm, kéo thả sản phẩm vào scene
- Kho tối đa **100k-200k DA_FurnitureItem**, chạy runtime
- C++ UFurnitureFilterLibrary, Common Tile View + Common Lazy Image, Pagination 50 items/trang

### C++ — FurnitureFilterLibrary
```
File: Source/Lighting_Mnger/FurnitureFilterLibrary.h / .cpp
Build.cs: PrivateDependencyModuleNames += "Slate", "SlateCore"

static TArray<UPrimaryDataAsset*> FilterFurnitureItems(
    AllItems, SearchText, FolderPath, CategoryFilter, MaxResults=200
);
```
Dùng UE5 reflection (FindFProperty) — gọi từ Blueprint là 1 node "Filter Furniture Items".

### Paths
```
Mesh : /Game/DatabaseProjectMaster/Model/Object_Model/
DA_  : /Game/cuong/UI/Data/FurnitureAssets/
DT   : /Game/cuong/UI/Data/DT_FurnitureCatalog
```

### Pipeline Dữ Liệu
```
Google Sheets → CSV → Python script → DT_FurnitureCatalog reimport
→ EUW_CreateDataAssets → DA_FurnitureItem
Python script 1 → quét Asset Registry → populate BoundingSize
Python script 2 → quét Asset Registry → update MeshFolderPath
→ Chạy lại EUW_CreateDataAssets để sync vào DA_
```

**Lưu ý pipeline:**
- S_FurnitureData.StaticMesh → **Soft Object Reference** (đã đổi để tối ưu RAM)
- BoundingSize populate bằng Python script — RowName = tên file mesh trong Content Browser
- Mesh path = MeshFolderPath + "/" + RowName
- 15 rows không có BoundingSize = mesh chưa có trong project (bình thường)
- Xem chi tiết scripts trong **Python_Scripts.md**

### Game Instance
- Dùng **Foff_GameInstance** chung — đã thêm `FurnitureInventoryRef (WBP_FurnitureInventory)`
- **Khi tích hợp dự án tổng: báo đồng nghiệp về variable này**

### Variables (WBP_FurnitureInventory)
| Tên | Kiểu | Mô tả |
|-----|------|-------|
| `FolderTree` | Map String→String | Active folder tree (swap khi switch mode) |
| `FurnitureFolderTree` | Map String→String | Cache tree Furniture ← v1.1 |
| `MaterialFolderTree` | Map String→String | Cache tree Material ← v1.1 |
| `ActiveLevel1Path` | String | Folder cấp 1 đang chọn |
| `CurrentDepth` | Integer | Độ sâu chip tag |
| `CurrentCategory` | Name | Category đang lọc |
| `CurrentSearchText` | String | Text search |
| `CurrentFolderPath` | String | Folder path đang chọn |
| `SearchTimerHandle` | Timer Handle | Debounce search |
| `CurrentPopup` | WBP_DetailPopup | Popup đang mở |
| `AllFurnitureItems` | Array of DA_FurnitureItem | Pre-loaded khi Event Construct |
| `FilteredItems` | Array of DA_FurnitureItem | Kết quả filter Furniture |
| `CurrentPage` | Integer | Trang hiện tại (0-based) — dùng chung 2 mode |
| `PageSize` | Integer | Số item/trang (= 48) |
| `bIsDragging` | Boolean | Đang kéo widget |
| `DragOffset` | Vector2D | Offset kéo |
| `InventoryPosition` | Vector2D | Vị trí widget |
| `bIsMinimized` | Boolean | Đang thu nhỏ |
| `bIsMaximized` | Boolean | Đang full screen |
| `MinimizedHeight` | Float | Chiều cao minimize |
| `OriginalSize` | Vector2D | Kích thước gốc |
| `OriginalPosition` | Vector2D | Vị trí gốc |
| `bIsReplaceMode` | Boolean | Đang ở chế độ replace mesh |
| **— v1.1 Material —** | | |
| `CurrentInventoryMode` | E_InventoryMode | Furniture / Material (default = Furniture) |
| `TargetFurnitureActor` | BP_FurnitureActor | Actor đang chỉnh material ← SET None ở Event Destruct |
| `SelectedSlotIndex` | Integer | Slot đang chọn, default -1 |
| `AllFilteredMaterialRows` | Array of Name | Cache RowNames sau FilterMaterialItems |
| `PendingMaterialPath` | String | MaterialPath đang chờ async load |
| `PendingRowName` | Name | RowName đang chờ apply (dùng cho thumbnail update) |
| `ApplyMaterialTimerHandle` | Timer Handle | Debounce CaptureSnapshot 0.5s |
| `UndoManagerRef` | BP_UndoManager | Cache singleton, set ở Event Construct |
| `PendingRestoredActor` | BP_FurnitureActor | Actor chờ restore sau timer 0.1s |
| **— v C2 Favorites —** | | |
| `ActiveSpecialCategory` | Name | "" = không active, "Recent" hoặc "Favorite" ← C2 |

⚠️ **VRAM leak:** TargetFurnitureActor + PendingRestoredActor là hard ref → SET None ở **Event Destruct**.

### Layout (WBP_FurnitureInventory 720x630)
```
Canvas Panel
├── HB_TitleBar (Is Variable)
│   ├── BTN_TitleBar (drag handle)
│   └── BTN_Minimize, BTN_Maximize, BTN_Close
├── BackgroundBlur_246 (anchor stretch, Top=~50)
│   └── VerticalBox
│       ├── HB_TabBar (v1.1)               ← TAB BAR
│       │   ├── BTN_Tab_Furniture
│       │   └── BTN_Tab_Material
│       ├── [Spacer]
│       ├── HB_Recent_Favorite (v C2)      ← RECENT + FAVORITE BAR
│       │   ├── BTN_RecentCategory  ("Recent")
│       │   └── BTN_FavoriteCategory ("Favorite")
│       └── HB_MainContent
│           ├── ScrollBox cột trái → VerticalBox_44 (folder tree)
│           └── VerticalBox cột phải
│               ├── HB_SlotSwatches (v1.1, Collapsed mặc định)
│               │   ├── HB_SwatchList (spawn WBP_SlotSwatch động)
│               │   ├── BTN_MaterialEdit (Disabled — placeholder v1.2)
│               │   ├── BTN_ResetSlot
│               │   └── BTN_ResetAll
│               ├── ScrollBox: SearchBar, TB_Breadcrumb, VB_ChipTagArea
│               ├── SizeBox → CTV_FurnitureCard (Furniture mode)
│               ├── SizeBox → CTV_MaterialCard (Material mode, v1.1)
│               └── HorizontalBox pagination
└── BTN_MinimizedIcon (Collapsed mặc định)
```

**WBP_SlotSwatch** (v1.1):
```
Variables: SlotIndex : Integer
Event Dispatcher: OnSwatchClicked(ClickedSlotIndex : Integer)
Functions: SetSelected(bSelected), UpdateThumbnail(NewThumbnail)
Layout: 48x48 tròn, Common Lazy Image (CLImg), Image overlay highlight
```

**WBP_MaterialCard** (v1.2):
```
Interface: IUserObjectListEntry
Variables: MaterialItem (BP_MaterialItem), InventoryRef
Layout: Canvas Panel → LazyImage_ThumbMI, Button_InforMaterial, Button_ChangeMaterial,
        Button_FavoriteMaterial (heart icon, anchor top-right, 32x32, Is Variable = true)
OnListItemObjectSet: SetBrushFromLazyTexture(LazyImage_ThumbMI, MaterialItem.ThumbnailMI)
                     → Call UpdateFavTint
Button_ChangeMaterial OnClicked: InventoryRef.ApplyMaterial(MaterialItem.RowName)
Button_FavoriteMaterial OnClicked:
  GET MaterialItem → GET RowName
  GET BP_FurnitureUserPrefsManager → Toggle Favorite Material(RowName)
  → Call UpdateFavTint
UpdateFavTint (Function):
  GET MaterialItem → GET RowName
  GET BP_FurnitureUserPrefsManager → Is Favorite Material(RowName)
  T → Set Color and Opacity(Button_FavoriteMaterial, R=1,G=0.3,B=0.3,A=1)
  F → Set Color and Opacity(Button_FavoriteMaterial, R=1,G=1,B=1,A=0.3)
Event Destruct: SET MaterialItem = None, SET InventoryRef = None
```

### Widgets Con

#### WBP_TreeNode
```
Variables: FolderPath, FolderName, IndentLevel
Root: HorizontalBox → Spacer + Button → TextBlock
Custom Event: RefreshDisplay
Dispatcher: OnNodeSelected(SelectedPath String, IndentLevel Integer)
```

#### WBP_ChipTag
```
Variables: FolderPath_ChipTag, FolderName_ChipTag, IndentLevel_ChipTag
OnClicked: CallOnChipSelected(FolderPath_ChipTag, IndentLevel_ChipTag)
Dispatcher: OnChipSelected(SelectedPath_ChipTag String, IndentLevel_ChipTag Integer)
```

#### WBP_ChipRow
```
Layout: ScrollBox Horizontal → HorizontalBox_ChipRow (Is Variable)
Variables: RowIndentLevel (Integer)
```

#### WBP_FurnitureCard
```
Interface: IUserObjectListEntry
Variables: FurnitureDA, InventoryRef, PreviewActor (BP_FurnitureActor), DragOverlayRef
Layout: Canvas Panel → LazyImage_Thumb, Button_InforItem, Button_ChangeMesh,
        Button_FavoriteFurniture (heart icon, anchor top-right, 32x32, Is Variable = true) ← v C2

OnListItemObjectSet:
  Cast → DA_FurnitureItem → Set FurnitureDA → Set Brush from Lazy Texture
  Branch IsValid(InventoryRef): False → Get GameInstance → Set InventoryRef
  → Call UpdateFavTint   ← v C2

Button_InforItem OnClicked: Call OnCardInfoClicked(FurnitureDA)
LazyImage_Thumb: Common Lazy Image

Button_FavoriteFurniture OnClicked (v C2):
  GET FurnitureDA → Get Object Name → String to Name → RowName
  GET BP_FurnitureUserPrefsManager → Toggle Favorite Mesh(RowName)
  → Call UpdateFavTint

UpdateFavTint Function (v C2):
  GET FurnitureDA → Get Object Name → String to Name → RowName
  GET BP_FurnitureUserPrefsManager → Is Favorite Mesh(RowName)
  T → Set Color and Opacity(Button_FavoriteFurniture, R=1,G=0.3,B=0.3,A=1)
  F → Set Color and Opacity(Button_FavoriteFurniture, R=1,G=1,B=1,A=0.3)
```

#### WBP_DetailPopup
```
Root: Canvas Panel → SizeBox (Width=400) → VerticalBox
LazyImage_Thumbnail, TB_Name, TB_Category, TB_Description, BTN_BuyLink
Variables: FurnitureDA, bIsDragging, DragOffset, PopupPosition
BTN_XClosePopup: Remove from Parent
BTN_BuyLink: Launch URL (FurnitureDA.Link)
Drag via Event Tick
```

### Functions

#### Event Construct (Sequence)
```
Then 0: Set Timer 0.1s → InitMinimizedHeight → SET CurrentCategory
Then 1: CLEAR AllFurnitureItems → GetAllAssets → ForEach → Cast DA_FurnitureItem → ADD
        → BindCategoryEvents → FilterBySearch
Then 2: BuildFolderTree → SET FurnitureFolderTree
        → PopulateTreeColumn → FilterByFolderPath → UpdateTabHighlight
Then 3: GetAllActors(BP_UndoManager)[0] → SET UndoManagerRef
        → Bind OnRestoreCompleted → OnSceneRestored
Then 4: GetAllActors(BP_FurnitureInputManager)[0]
        → Bind OnSelectionChanged → OnSelectionChangedMaterial   ← v2.4 (thay OnMeshSelected/OnMeshDeselected đã xóa)
```
> **v2.4:** ĐÃ XÓA `Bind OnMeshDeselected` + `Bind OnMeshSelected` (dispatcher không còn). Mọi phản ứng selection của inventory giờ qua `OnSelectionChanged`. **Bind PHẢI ở Event Construct** — đặt trong handler thì handler không fire sẽ không bao giờ bind (bug đã trả giá).

#### BuildFolderTree / BuildMaterialFolderTree
Đọc DA_ hoặc DT_MaterialInstancesCatalog → tách FolderPath → xây Map String→String.

#### PopulateTreeColumn
Clear VerticalBox_44 → tạo WBP_TreeNode từ FolderTree (active tree).

#### FilterByFolderPath(FolderPath)
```
SET CurrentFolderPath = FolderPath → Call FilterBySearch(CurrentSearchText, CurrentCategory)
```

#### FilterBySearch(SearchText, CategoryFilter)
```
SET CategoryFilter, SET CurrentSearchText
Branch SearchText != "" AND Len < 3 → Return
Branch CurrentInventoryMode == Material:
  T → Call PopulateMaterialGrid → Return
  F → FilterFurnitureItems(C++) → ForEach → AddItem(CTV_FurnitureCard)
```

#### SwitchInventoryMode(NewMode) — v1.1
```
SET CurrentPage = 0, SET CurrentInventoryMode = NewMode
Branch NewMode == Material:
  T → Visible CTV_MaterialCard, SlotSwatches nếu có actor
      PopulateMaterialGrid, BuildMaterialFolderTree nếu chưa có
      SET FolderTree = MaterialFolderTree, PopulateTreeColumn
  F → Visible CTV_FurnitureCard
      SET FolderTree = FurnitureFolderTree, PopulateTreeColumn
      Call FilterBySearch(CurrentSearchText, CurrentCategory)  ← populate card ngay
```

#### PopulateMaterialGrid — v1.1
```
FilterMaterialItems(C++, DT_MaterialInstancesCatalog, CurrentSearchText,
  TypeTags=rỗng, CurrentFolderPath, MaxResults=20000)
→ SET AllFilteredMaterialRows → SET CurrentPage = 0 → Call DisplayPage
```

#### DisplayPage — v1.1
```
← Hiện trang hiện tại từ AllFilteredMaterialRows (pagination Material mode)

Start = CurrentPage × PageSize
End   = Min(Start + PageSize, Length(AllFilteredMaterialRows))

ForLoop Start→End:
  GetDataTableRow(DT_MaterialInstancesCatalog, AllFilteredMaterialRows[i])
  → Create BP_MaterialItem → SET RowName, fields
  → AddItem(CTV_MaterialCard, MaterialItem)

← Tính TotalPages — dùng integer math thuần (⚠️ KHÔNG dùng float/Ceil):
TotalPages = (Length(AllFilteredMaterialRows) + PageSize - 1) / PageSize
← Công thức này cho kết quả đúng với mọi giá trị:
←   (41 + 47) / 48 = 1 ✓  |  (165 + 47) / 48 = 4 ✓  |  (1728 + 47) / 48 = 36 ✓
← Dùng Ceil(float) bị sai vì integer division xảy ra TRƯỚC Ceil → kết quả luôn = 0 khi Length < PageSize

SET Text(ET_PageDisplay, (CurrentPage+1) + "/" + TotalPages)
```

#### ApplyMaterial(MaterialRowName) — v1.1
```
Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0:
  T → GetDataTableRow → SET PendingRowName, SET PendingMaterialPath
      → Call LoadAndApplyMaterial (Custom Event, async)
```

#### LoadAndApplyMaterial — v1.1
```
Async Load(PendingMaterialPath) → Cast MaterialInterface
→ CreateDMI(FurnitureMesh, MI_Source, SelectedSlotIndex) → SetMaterial
→ SetArrayElem(MaterialOverrides, SelectedSlotIndex, PendingMaterialPath)
→ Debounce 0.5s → CaptureSnapshot("ChangeMaterial")
→ GetDataTableRow(DT, PendingRowName) → UpdateThumbnail swatch[SelectedSlotIndex]
```

#### RefreshSlotSwatches — v1.1
```
ClearChildren(HB_SwatchList)
GET TargetFurnitureActor → FurnitureMesh → GetStaticMesh → GetMaterialSlotNames
ForLoop → Create WBP_SlotSwatch → Bind OnSwatchClicked → AddChild
```

#### OnSelectionChangedMaterial(Actors, Primary) — v2.4 (MỚI)
```
← Bound từ InputManager.OnSelectionChanged (dispatcher selection duy nhất)
→ Call OnMeshSelected(Primary)    ← tái dùng handler nội bộ, KHÔNG duplicate logic
```
> Đây là cầu nối: OnSelectionChanged (mới) → OnMeshSelected (handler cũ). Giữ handler OnMeshSelected làm nơi chứa logic replace + material; chỉ đổi nguồn kích hoạt.

#### OnMeshSelected(SelectedActor) — handler nội bộ (v2.4)
> ⚠️ Đây là **custom event handler nội bộ của inventory**, KHÁC dispatcher `OnMeshSelected` đã bị xóa ở InputManager. Nay được gọi qua `OnSelectionChangedMaterial`.
```
← Nhánh REPLACE (v1.3 + v2.4 fix)
Branch bIsReplaceMode == True:
  T →
    Get All Actors Of Class(BP_FurnitureInputManager) → GET[0] → IsValid →
      SET MeshesToReplace = InputManager.SelectedActors     ← v2.4: array (KHÔNG MeshToReplace single chết)
    Branch IsValid(SelectedActor):                          ← guard folder nav (deselect → skip)
      T → Cast → GET DAPath → Load Asset Blocking → Cast DA_FurnitureItem → GET MeshFolderPath
          → Branch MeshFolderPath != "" → FilterByFolderPathWithUI(MeshFolderPath)
  F → (tiếp tục)

← Nhánh MATERIAL (v1.1 + v2.4 fix Accessed None)
Branch CurrentInventoryMode == Material:
  T →
    Branch IsValid(SelectedActor):                          ← v2.4: guard (OnSelectionChanged fire rỗng khi deselect)
      T → SET TargetFurnitureActor = SelectedActor
          → Visible HB_SlotSwatches → SET SelectedSlotIndex = -1
          → RefreshSlotSwatches → Update thumbnails từ MaterialOverrides
      F → SET TargetFurnitureActor = None
          → Collapsed HB_SlotSwatches → SET SelectedSlotIndex = -1   ← thay thế handler OnMeshDeselected cũ
```

#### OnMeshDeselected — ĐÃ XÓA (v2.4)
> Logic collapse material giờ nằm ở nhánh material False (IsValid=False) của OnMeshSelected, kích hoạt qua OnSelectionChanged khi selection rỗng. Phần "thoát replace mode khi deselect" của v1.3 không còn cần (replace exit xử lý qua BTN_Replace toggle + StartReplaceMode).

#### EnterReplaceMode (Function) — v1.3 + v2.4
```
Call EnsureExpanded (Target=self)   ← v2.4: bung nếu đang minimize (no-op nếu đang mở) — fix replace lúc minimize không bung
SET bIsReplaceMode = True
Regenerate All Entries(CTV_FurnitureCard)
← Dùng khi bật Replace mode VÀ không cần navigate folder (BTN_Replace toggle ON)
← KHÔNG dùng từ DetailPopup (vì FilterByFolderPathWithUI sẽ clear cards sau đó)
```

#### ExitReplaceMode (Function) — v1.3
```
SET bIsReplaceMode = False
Regenerate All Entries(CTV_FurnitureCard)
← Force tất cả cards ẩn BTN_ChangeMesh
```

#### RefreshCardReplaceMode (Function) — v1.3
```
Regenerate All Entries(CTV_FurnitureCard)
← Gọi từ bên ngoài (DetailPopup) sau khi FilterByFolderPathWithUI populate xong
← Đảm bảo cards mới thấy bIsReplaceMode = True → hiện BTN_ChangeMesh
```

#### OnSceneRestored(RestoredSelectedActor) — v1.1
```
← Bound từ UndoManagerRef.OnRestoreCompleted
Branch CurrentInventoryMode == Material:
  T → SET PendingRestoredActor = RestoredSelectedActor
      SetTimerByFunctionName("ApplyRestoredActor", 0.1s)
      ← delay cho LeftMouseButton DeselectMesh chạy xong trước
```

#### ApplyRestoredActor — v1.1
```
Branch CurrentInventoryMode == Material:
  T → SET TargetFurnitureActor = PendingRestoredActor
      Branch IsValid:
        T → Visible, SET SelectedSlotIndex = -1
            Call RefreshSlotSwatches → Update thumbnails từ MaterialOverrides
        F → Collapsed
```

### Events

#### OnTreeNodeClicked(SelectedPath, IndentLevel)
```
Branch IndentLevel == 0:
  ClearChildren(VB_ChipTagArea) → Set ActiveLevel1Path → PopulateTreeColumn
  FilterByFolderPath(SelectedPath)
  SetText(TB_Breadcrumb, SelectedPath == "" ? "All product" : SelectedPath)

Branch IndentLevel == 1:
  ClearChildren(VB_ChipTagArea)
  Create WBP_ChipRow → ForEach ParseIntoArray(FolderTree[SelectedPath], ","):
    Create WBP_ChipTag → Bind OnChipSelected → AddChild
  AddChild(VB_ChipTagArea, WBP_ChipRow)
  FilterByFolderPath(SelectedPath)
```

#### OnChipTagClicked(SelectedPath_ChipTag, IndentLevel_ChipTag)
```
Set CurrentDepth = GetChildrenCount(VB_ChipTagArea) - IndentLevel_ChipTag + 1
ForLoop → RemoveChildAt từ cuối
FilterByFolderPath(SelectedPath_ChipTag)
Map_Find(FolderTree, SelectedPath_ChipTag):
  True → Create WBP_ChipRow → tạo chip tags → AddChild(VB_ChipTagArea)
```

### Window Controls
```
Drag (BTN_TitleBar):
  OnPressed: bIsDragging=True, DragOffset = MousePos - InventoryPosition
  OnReleased: bIsDragging=False
  Tick: Set Position = MousePos - DragOffset / ViewportScale

Minimize: Collapse BackgroundBlur + HB_TitleBar → Show BTN_MinimizedIcon
Maximize: toggle — True: Set Position(0,0), Size=ViewportSize/Scale
                   False: restore OriginalPosition, OriginalSize
BTN_MinimizedIcon: Show HB_TitleBar + BackgroundBlur → Set Position(100,100)
```

### Level Blueprint
```
InputAction OpenFurnitureInventory → FlipFlop
  A: Create WBP_FurnitureInventory → Add to Viewport → Show Mouse Cursor
     → Cast Foff_GameInstance → Set FurnitureInventoryRef
  B: Remove from Parent
```

### Key Learnings — Inventory
- **Blueprint loop 1852+ items → hit execution limit** → dùng C++ UFurnitureFilterLibrary
- **Get All Widgets of Class trong OnListItemObjectSet** nặng → dùng Foff_GameInstance
- **DA_FurnitureItem cần implement IUserObjectListEntry** → OnListItemObjectSet fire
- **DPI Scale** ảnh hưởng Set Position → chia Get Viewport Scale
- **Get Desired Size = 0 trong Event Construct** → delay 0.1s
- **FilterByFolderPath phải gọi FilterBySearch ở cuối** → search text vẫn hoạt động khi đổi folder
- **Contains("", anything) = true** → node "All" hiện tất cả
- **MeshFolderPath** populate bằng Python script quét Asset Registry

### Key Learnings — Material v1.1
- **Get Static Mesh Component trả về rỗng** → phải Cast To BP_FurnitureActor → GET FurnitureMesh
- **CommonSearchBox không expose Set Text** → visual clear bị giới hạn
- **Set Background Color không work (Button Tint A=0)** → dùng Image overlay + Set Color and Opacity
- **Timer delay 0.1s trong OnSceneRestored** → ApplyRestoredActor fire SAU LeftMouseButton DeselectMesh
- **IsValid check** bắt buộc trước mọi ForEach/ForLoop dùng Object Reference
- **Branch IsEmpty False dead-end** → logic sau không chạy → phải nối False vào SET FolderTree
- **Broadcast OnRestoreCompleted** phải dùng RestoredBPActor (từ Cast output Branch gizmo), không dùng SpawnedActors[class var SelectedMeshIndex] → class var = last CaptureSnapshot, không phải snapshot đang restore
- **SwitchInventoryMode False branch** phải gọi FilterBySearch cuối → populate CTV_FurnitureCard ngay khi switch về
- **Async Load**: String → MakeSoftObjectPath → ToSoftObjectReference → AsyncLoadAsset
- **Latent node** không dùng trong Function → dùng Custom Event
- **SetArrayElem Size to Fit** thay For Loop resize array
- **SceneCapture2D Capture Source** = "Final Color (LDR) in RGB" → fix black output

- **Pagination TotalPages** = `(Length + PageSize - 1) / PageSize` — integer math thuần. KHÔNG dùng `Ceil(float(Length)/float(PageSize))` vì integer division xảy ra trước Ceil cho kết quả 0 khi Length < PageSize.
- **Root Canvas Panel WBP_FurnitureInventory** = `Not Hit-Testable (Self Only)` — fill screen nhưng không block click vào WBP_MeshControls phía sau.

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|-----------|------|----------|
| 1.0 | 22/04/2026 | Furniture inventory cơ bản — filter, drag drop, folder tree |
| 2.0 | 20/05/2026 — 16:00 ICT | Thêm toàn bộ v1.1 Material: variables, layout, functions, events, key learnings |
| 2.1 | 25/05/2026 — 15:03 ICT | Đợt C: HB_Recent_Favorite layout, ActiveSpecialCategory variable, WBP_FurnitureCard + WBP_MaterialCard Button_Favorite + UpdateFavTint, toggle Recent/Favorite, persist khi switch mode |
| 2.2 | 25/05/2026 — 15:03 ICT | Fix DisplayPage TotalPages: dùng integer formula thay Ceil. Fix root Canvas Panel Not Hit-Testable (Self Only). Thêm DisplayPage function doc |
| 2.3 | 08/06/2026 | Sprint 2: OpenMaterialModeForActor, EnsureExpanded (match BTN_MinimizedIcon), F_ExecuteReplace multi |
| 2.4 | 10/06/2026 — 20:34 ICT | **Refactor dispatcher.** Event Construct Then 4: bind `OnSelectionChanged` → `OnSelectionChangedMaterial` (XÓA bind OnMeshSelected + OnMeshDeselected). Thêm handler `OnSelectionChangedMaterial(Actors, Primary)` → Call OnMeshSelected(Primary). OnMeshSelected nội bộ: nhánh replace SET `MeshesToReplace`(array) thay MeshToReplace(single); nhánh material thêm guard IsValid(SelectedActor) (False→collapse+None+SlotIndex=-1, fix Accessed None). XÓA handler OnMeshDeselected. EnterReplaceMode +Call EnsureExpanded đầu hàm (fix replace lúc minimize). |

---

## 5. KẾ HOẠCH PHÁT TRIỂN

### Phase 1 — Nền tảng
| Feature | Trạng thái |
|---------|-----------|
| Single click select + outline | ✅ Xong |
| BTN_Select + BTN_Move highlight | ✅ Xong |
| BTN_Move (7 trục + snap) | ✅ Xong |
| Switch mesh khi đang Move | ✅ Xong |
| Click vùng trống → Deselect | ✅ Xong |
| Undo (Alt+Z) | ✅ Xong |
| Redo (Shift+Alt+Z) | ✅ Xong |
| Save/Load (EMS) | ✅ Xong |
| BP_FurnitureActor | ✅ Xong |
| Drag & Drop spawn mesh | ✅ Xong |
| Ghost preview mesh khi drag | ✅ Xong |
| Snap to surface (sàn/tường/trần) | ✅ Xong |
| Surface rotation theo normal | ✅ Xong |
| Fix spawn khi gizmo active | ✅ Xong |
| Undo/Redo restore đúng mesh + mode | ✅ Xong |
| Deselect lưu snapshot đúng (-1) | ✅ Xong |
| Save/Load redesign | 🔲 Cần làm |

### Phase 2 — Core features
| Feature | Trạng thái |
|---------|-----------|
| BTN_Rotate | ✅ Xong (cần polish gizmo visual) |
| BTN_Scale | ✅ Xong |
| Material Editor (Change Material v1.1) | ✅ Xong (20/05/2026) |
| Copy/Paste (Ctrl+C/V) | 🔲 Chưa làm |
| Delete key shortcut | 🔲 Chưa làm |
| Focus on selected (F) | 🔲 Chưa làm |

### Phase 3 — UX nâng cao
| Feature | Trạng thái |
|---------|-----------|
| Scene Outliner | 🔲 Chưa làm |
| Auto-save | 🔲 Chưa làm |

### Keyboard Shortcuts
| Phím | Chức năng |
|------|-----------|
| Q | Select mode |
| W | Move mode |
| E | Rotate mode |
| R | Scale mode |
| Delete | Xóa mesh |
| Alt+Z | Undo |
| Shift+Alt+Z | Redo |
| Ctrl+S | Save |
| Ctrl+O | Load |
| I | Mở/đóng Inventory |
| Esc | Deselect |

---

## 6. KEY LEARNINGS

### Deselect + CaptureSnapshot
- **DeselectMesh trước, CaptureSnapshot("Deselect") sau**
- **KHÔNG gọi CaptureSnapshot trong DeselectMesh** — gây infinite loop
- **CaptureSnapshot("Deselect")** chỉ gọi từ Mouse Left Pressed Step 5 và 6

### CaptureSnapshot — Flow nhánh tìm SelectedMeshIndex
- **SET SelectedMeshIndex = -1 ở đầu** trước mọi Branch
- **Tất cả nhánh False** nối vào `Branch(Length >= MaxSteps)` — không dừng

### Undo/Redo
- **UniqueID** = Get Display Name(Actor) → phân biệt mesh cùng MeshPath
- **RedoLastAction:** nối output pin của SET CurrentIndex vào IndexHistory
- **CaptureSnapshot("Initial")** gọi cuối Level Blueprint BeginPlay

### Thứ tự CaptureSnapshot so với action
- **Spawn:** Add Tag → CaptureSnapshot
- **Delete:** Destroy Actor → CaptureSnapshot
- **Deselect:** DeselectMesh → CaptureSnapshot

### Collision Management khi Gizmo Active
- **ActivateGizmo**: tắt collision NOT FurnitureSpawned + tắt BaseGizmo components
- **DeactivateGizmo**: restore tất cả — luôn chạy (cả True và False branch)

### Drag & Drop — Surface Snap
- **DeactivateGizmo trong On Drag Detected** — fix lỗi Line Trace không hit sàn khi đang Move mode
- **Floor/Ceiling:** Rotator 0,0,0 — giữ nguyên pivot mesh
- **Wall:** Make Rot from X(Normal) → Yaw - 90 — mesh đứng thẳng áp tường
- **bTraceComplex = True** → trace geometry thực, bắt được tường/trần không có collision box
- **ActorsToIgnore = [PreviewActorRef]** → tránh mesh ghost block trace chính nó
- **On Drop dùng PreviewActorRef** thay vì spawn mới
- **Move mode KHÔNG snap surface** — snap chỉ trong drag & drop ban đầu
- **Pivot mesh = điểm lắp đặt thực tế** → không cần offset bounds

### EMS Save/Load
- **BP_FurnitureActor** kế thừa StaticMeshActor
- **KHÔNG dùng SET Tags** sau GET→ADD — EMS dùng Tags để track state
- **MeshPath rỗng** → Destroy Actor trong ActorLoaded
- **SaveGameMenu rebind mỗi lần tạo mới** → dùng Event Tick check widget mới
- **Destroy FurnitureSpawned trước EMS load** → OnLoadButtonClicked
- **Set Input Mode Game And UI** đặt đầu Mouse Left Pressed

### BTN_Rotate — Rotation Gizmo
- **BP_Rotation_Gizmo_Example** kế thừa `ABaseGizmo` → Cast BaseGizmo vẫn đúng
- **Collision mặc định = NoCollision** trong BP_Rotation_Gizmo_Example → phải đổi thành Query Only
- **Get Hit Component Display Name** trả về `"ActorName.ComponentName"` → dùng **Split (From End, ".")** lấy Right S → ActiveAxis đúng
- **PreviousMousePosition phải SET trong OnMousePressed** — nếu không, frame đầu Tick tính delta = tọa độ màn hình (~885px)
- **AccumulatedRotation reset = 0 trong OnMouseReleased** — tránh giá trị cũ ảnh hưởng lần drag sau
- **RotationSpeed = 0.3** — đủ nhạy mà không quá nhanh
- **SnapAngle tách biệt SnapStep** — SnapStep cho Translation, SnapAngle cho Rotation
- **Snap logic:** tích lũy delta → khi Abs(Accumulated) >= SnapAngle → xoay Sign×SnapAngle → trừ SnapAmount khỏi Accumulated
- **Gizmo xoay theo mesh** là behavior của plugin — world axis vs local axis cần quyết định tiếp
- **ETransformationType** — enum của RuntimeTransformer plugin (None/Translation/Rotation/Scale)
- **ActivateGizmo nhận TransformType param** → BTN_Move=Translation, BTN_Rotate=Rotation, BTN_Scale=Scale
- **Mouse Left Pressed Step 11 + RestoreSnapshot** dùng **Select node** (Index=E_ActiveMode) để map sang ETransformationType


- **KHÔNG Possess TransformerPawn** → mất camera
- **SET bIsDraggingGizmo = False** phải SAU CaptureSnapshot
- **Thêm vào pin node có sẵn** — không xẻ code cũ

---

## 4C. WBP_FURNITURE INVENTORY — REPLACE MODE

### Variables thêm vào WBP_FurnitureInventory
```
bIsReplaceMode : Boolean  ← True khi đang ở chế độ replace mesh
```

### FilterByFolderPathWithUI(FolderPath String) — Custom Event
```
1. Map Find (FolderTree, "") → Parse Into Array (Value, ",") → Level1Array
   For Each Level1Array with Break:
     Branch FolderPath Contains ArrayElement?
       True → SET ActiveLevel1Path = ArrayElement → Break

2. PopulateTreeColumn  ← cập nhật cây folder trái

3. Split (FolderPath, "Object_Model/") → Right S = ShortPath

4. Clear Children (VB_ChipTagArea)
   Set Visibility (VB_ChipTagArea, Visible)

5. CreateChipTagsForPath(ShortPath)  ← tạo tất cả hàng chip tags

6. FilterByFolderPath(FolderPath)  ← filter grid

7. SET Text (TB_Breadcrumb, ShortPath)
```

### CreateChipTagsForPath(ShortPath String) — Function
```
Local Variables:
  CurrentPath : String (default = "")
  CurrentIndentLevel : Integer (default = 2)

Clear Children (VB_ChipTagArea)
Set Visibility (VB_ChipTagArea, Visible)

Parse Into Array (ShortPath, "/") → LevelArray

For Each LevelArray with Break:
  Loop Body:
    Branch CurrentPath == ""?
      True → SET CurrentPath = ArrayElement
      False → SET CurrentPath = CurrentPath + "/" + ArrayElement

    Branch CurrentPath == ActiveLevel1Path?
      True → tiếp tục loop (skip cấp 1)
      False:
        Map Find (FolderTree, CurrentPath)?
          True:
            Create WBP_ChipRow → Cast To WBP_ChipRow
            SET RowIndentLevel = CurrentIndentLevel
            Parse Into Array (Value, ",") → For Each:
              Create WBP_ChipTag
              SET FolderPath_ChipTag = CurrentPath + "/" + ArrayElement
              SET FolderName_ChipTag = ArrayElement
              SET IndentLevel_ChipTag = CurrentIndentLevel
              Bind OnChipSelected → OnChipTagClicked
              AddChild (HorizontalBox_ChipRow)
            Completed → AddChild (VB_ChipTagArea, ChipRow)
            SET CurrentIndentLevel = CurrentIndentLevel + 1
          False → tiếp tục loop
```

### Lưu ý
- **CurrentIndentLevel bắt đầu = 2** — khớp với IndentLevel_ChipTag từ OnTreeNodeClicked
- **Clear Children ở ngoài loop** — không Clear bên trong For Each
- **FilterByFolderPathWithUI** gọi từ BTN_Replace (WBP_MeshControls) và BTN_ChangeMesh (WBP_DetailPopup)
- **FilterByFolderPath** vẫn dùng cho filter thông thường khi click tree/chip
