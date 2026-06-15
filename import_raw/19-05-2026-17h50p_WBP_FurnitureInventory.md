# WBP_FurnitureInventory
**Phiên bản:** 1.5 | **Cập nhật:** 19/05/2026 — 17:50 ICT
**Node flow chi tiết:** xem `Blueprint_Logic.md`

---

## Variables

| Tên | Kiểu | Mô tả |
|---|---|---|
| `FolderTree` | Map String→String | Active folder tree (swap khi switch mode) |
| `FurnitureFolderTree` | Map String→String | Cache tree Furniture (v1.1 UX) |
| `MaterialFolderTree` | Map String→String | Cache tree Material (v1.1 UX) |
| `ActiveLevel1Path` | String | Folder cấp 1 đang chọn |
| `CurrentDepth` | Integer | Độ sâu chip tag |
| `CurrentCategory` | Name | Category đang lọc |
| `CurrentSearchText` | String | Text search |
| `CurrentFolderPath` | String | Folder path đang chọn |
| `SearchTimerHandle` | Timer Handle | Debounce search |
| `CurrentPopup` | WBP_DetailPopup | Popup đang mở |
| `AllFurnitureItems` | Array of DA_FurnitureItem | Pre-loaded khi Event Construct |
| `FilteredItems` | Array of DA_FurnitureItem | Kết quả filter Furniture |
| `CurrentPage` | Integer | Trang hiện tại (0-based), dùng chung 2 mode |
| `PageSize` | Integer | = 48 |
| `bIsDragging` | Boolean | Đang kéo widget |
| `DragOffset` | Vector2D | Offset kéo |
| `InventoryPosition` | Vector2D | Vị trí widget |
| `bIsMinimized` | Boolean | Đang thu nhỏ |
| `bIsMaximized` | Boolean | Đang full screen |
| `MinimizedHeight` | Float | Chiều cao minimize |
| `OriginalSize` | Vector2D | Kích thước gốc |
| `OriginalPosition` | Vector2D | Vị trí gốc |
| `bIsReplaceMode` | Boolean | Đang ở chế độ replace mesh |
| **v1.1 — Material** | | |
| `CurrentInventoryMode` | E_InventoryMode | Furniture / Material |
| `TargetFurnitureActor` | BP_FurnitureActor | Actor đang chỉnh material — SET None ở Event Destruct |
| `SelectedSlotIndex` | Integer | Slot đang chọn, default -1 |
| `AllFilteredMaterialRows` | Array of Name | Cache RowNames sau FilterMaterialItems |
| `PendingMaterialPath` | String | MaterialPath đang chờ async load |
| `PendingRowName` | Name | RowName đang chờ apply (dùng cho thumbnail update) |
| `ApplyMaterialTimerHandle` | Timer Handle | Debounce CaptureSnapshot 0.5s |
| `UndoManagerRef` | BP_UndoManager | Cache singleton, set ở Event Construct |
| `PendingRestoredActor` | BP_FurnitureActor | Actor chờ restore sau timer 0.1s (v1.1 UX) |

---

## Layout

```
Canvas Panel
├── BTN_TitleBar (drag handle) + BTN_Minimize, BTN_Maximize, BTN_Close
├── BackgroundBlur_246
│   └── VerticalBox
│       ├── HB_TabBar (v1.1)
│       │   ├── BTN_Tab_Furniture
│       │   └── BTN_Tab_Material
│       └── HB_MainContent
│           ├── ScrollBox cột trái → VerticalBox_44 (tree folder)
│           └── VerticalBox cột phải
│               ├── HB_SlotSwatches (v1.1, Collapsed mặc định)
│               │   ├── HB_SwatchList
│               │   ├── BTN_MaterialEdit (Disabled — v1.2)
│               │   ├── BTN_ResetSlot
│               │   └── BTN_ResetAll
│               ├── ScrollBox: SearchBar_FurnitureItem, TB_Breadcrumb, VB_ChipTagArea
│               ├── [Horizontal Box] pagination
│               │   ├── BTN_PrevPage
│               │   ├── ET_PageDisplay
│               │   └── BTN_NextPage
│               └── SizeBox_281
│                   └── [Overlay]
│                       ├── CTV_FurnitureCard (120×120, Visible mặc định)
│                       └── CTV_MaterialCard  (120×120, Collapsed mặc định)
└── BTN_MinimizedIcon
```

---

## Widgets con quan trọng

### BP_MaterialItem (v1.1) — UObject wrapper cho CTV_MaterialCard
```
Parent: Object
Variables:
  RowName     : Name
  DisplayName : Text      ← EngName, refactor sang multilang khi sprint i18n
  ThumbnailMI : Soft Object Reference (Texture2D)
```

### WBP_MaterialCard (v1.1)
```
Interface: IUserObjectListEntry
Variables:
  MaterialItem : BP_MaterialItem  — SET None ở Event Destruct
  InventoryRef : WBP_FurnitureInventory — SET None ở Event Destruct
Layout: LazyImage_ThumbMI, Button_ChangeMaterial, Button_InforMaterial, Button_Favorite (Hidden)
```

### WBP_SlotSwatch (v1.1 UX)
```
Layout:
  Size Box → Overlay
    ├── Border → CLImg_SlotThumb
    ├── Image_430 (selection overlay, default Hidden)
    └── BTN_Swatch
Variables: SlotIndex : Integer
Event Dispatcher: OnSwatchClicked(ClickedSlotIndex : Integer)
Functions: SetSelected(bSelected), UpdateThumbnail(NewThumbnail)
```

---

## Event Construct (Sequence)
```
Then 0: Bind OnCategorySelected(BTN_AllCategory)
        → FilterByCategory(CategoryFilter=All)

Then 1: BuildFolderTree → SET FurnitureFolderTree = FolderTree
        → PopulateTreeColumn → FilterByFolderPath → UpdateTabHighlight

Then 2: GetAllActors(BP_UndoManager)[0] → SET UndoManagerRef
        → Bind OnRestoreCompleted → OnSceneRestored

Then 3: GetAllActors(BP_FurnitureInputManager)[0]
        → Bind OnMeshDeselected → OnMeshDeselected
        → Bind OnMeshSelected → OnMeshSelected
```

---

## Functions & Events

Node flow chi tiết: xem **`Blueprint_Logic.md`**

| Function/Event | Mô tả |
|---|---|
| `SwitchInventoryMode(NewMode)` | Switch Furniture/Material, swap FolderTree, UpdateTabHighlight, clear search |
| `BuildMaterialFolderTree` | Xây MaterialFolderTree từ DT, strip prefix, dùng Replace + ParseIntoArray |
| `PopulateMaterialGrid` | FilterMaterialItems C++ → SET AllFilteredMaterialRows → DisplayPage |
| `FilterBySearch(SearchText, CategoryFilter)` | Branch Material → PopulateMaterialGrid / Furniture logic |
| `DisplayPage` | Branch Material/Furniture → clear + populate CTV |
| `ApplyMaterial(MaterialRowName)` | SET PendingRowName + PendingMaterialPath → Call LoadAndApplyMaterial |
| `LoadAndApplyMaterial` | Async Load → Create MID → Set Material → debounce CaptureSnapshot + update thumbnail |
| `CaptureMaterialSnapshot` | Timer 0.5s → CaptureSnapshot("ChangeMaterial") |
| `OnSceneRestored(RestoredSelectedActor)` | SET PendingRestoredActor → Timer 0.1s → ApplyRestoredActor |
| `ApplyRestoredActor` | SET TargetFurnitureActor → Visible → RefreshSlotSwatches → update thumbnails |
| `OnMeshDeselected` | Ẩn SlotSwatches, SET TargetFurnitureActor = None, SelectedSlotIndex = -1 |
| `OnMeshSelected(SelectedActor)` | SET TargetFurnitureActor → Visible → RefreshSlotSwatches → update thumbnails |
| `RefreshSlotSwatches` | ClearChildren → ForLoop GetMaterialSlotNames → Create WBP_SlotSwatch |
| `OnSlotSwatchClicked(ClickedSlotIndex)` | SET SelectedSlotIndex → ForEach SetSelected |
| `BTN_ResetSlot` | SetMaterial gốc → CaptureSnapshot → update thumbnail slot |
| `BTN_ResetAll` | ForLoop SetMaterial gốc → CLEAR MaterialOverrides → CaptureSnapshot → RefreshSlotSwatches |

---

## Thumbnail Settings
```
Path: /Game/cuong/UI/Data/ThumbnailMaterialInstances/
Texture Group: UI, LOD Bias: 2, ~50KB/file
Tổng: 2731 textures
```

---

## Key Learnings

**Furniture Inventory:**
- Blueprint loop 1852+ items → dùng C++ UFurnitureFilterLibrary
- Get All Widgets of Class trong OnListItemObjectSet nặng → dùng GameInstance
- FilterByFolderPath phải gọi FilterBySearch ở cuối

**Material v1.1:**
- MaterialPath cần full object path `/Game/.../MI_Name.MI_Name`
- Async Load: String → Make Soft Object Path → To Soft Object Reference → Async Load Asset
- Latent node không dùng trong Function → Custom Event
- Set Array Elem Size to Fit thay For Loop resize
- ResetSlot/ResetAll: GET Static Mesh → GET Material để lấy material gốc

**UX v1.1:**
- CommonSearchBox không expose Set Text trong Blueprint
- Set Background Color không work trên Button Tint A=0 → dùng Image overlay + Set Color and Opacity
- Timer delay 0.1s trong OnSceneRestored để ApplyRestoredActor fire SAU LeftMouseButton DeselectMesh
- Luôn IsValid check trước mọi ForEach/ForLoop dùng Object Reference
- Branch IsEmpty False nhánh phải merge → dead-end = lần sau FolderTree không swap
- Breakpoint UE5: F9 toggle, F10 step over, F11 step into, Alt+Shift+F10 continue

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0–1.2 | 22/04–09/05/2026 | Furniture inventory cơ bản |
| 1.3 | 13/05/2026 | Material Grid, i18n plan, thumbnail |
| 1.4 | 16/05/2026 | Live Apply, Reset, SwitchMode, OnRestoreCompleted |
| 1.5 | 19/05/2026 — 17:50 ICT | UX fixes: FolderTree swap, highlight slot, thumbnail update, OnMeshDeselected/Selected, ApplyRestoredActor, FilterBySearch branch |
