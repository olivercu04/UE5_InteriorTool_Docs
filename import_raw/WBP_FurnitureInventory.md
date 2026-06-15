# WBP_FurnitureInventory
**Phiên bản:** 2.4 (BẢN HỢP NHẤT — merge v2.2 + patch v2.3 Resize + patch 08/06) | **Cập nhật:** 11/06/2026
Inventory duyệt & lọc nội thất + Material Editor (v1.1) + Resize Window + Replace multi

> **⚠ SPRINT D sắp thay đổi lớn file này:** Furniture mode chuyển sang DataTable+RowName (bỏ AllFurnitureItems preload), inventory single-instance, DisplayPage 2 mode. Xem `Gate1_SprintD_Execution_Opus.md`. Doc này = trạng thái TRƯỚC Sprint D.
> **⚠ REFACTOR DISPATCHER 10/06:** InputManager đã XÓA `OnMeshSelected`/`OnMeshDeselected` — chỉ còn `OnSelectionChanged(Actors, Primary)`. Các handler trong doc này (mục OnMeshSelected/OnMeshDeselected) giờ được gọi từ handler bind `OnSelectionChanged` (Primary valid → nhánh selected; Actors rỗng → nhánh deselected). Đối chiếu `Sprint3_Regression_DualDispatcher_Log.md` + node graph thật, cập nhật mục đó nếu lệch.

---

## Mục tiêu & Hiệu năng
- Duyệt, lọc, tìm kiếm, kéo thả sản phẩm vào scene
- Kho mục tiêu 100k-200k items, chạy runtime
- C++ UFurnitureFilterLibrary, Common Tile View + Common Lazy Image, Pagination 48/trang

## C++ — FurnitureFilterLibrary
```
File: FurnitureFilterLibrary.h/.cpp (đã migrate sang plugin FurnitureToolkit — CoreRedirect trong DefaultEngine.ini)
Build.cs: PrivateDependencyModuleNames += "Slate", "SlateCore"
static TArray<UPrimaryDataAsset*> FilterFurnitureItems(AllItems, SearchText, FolderPath, CategoryFilter, MaxResults=200);
static ... FilterMaterialItems(DT_MaterialInstancesCatalog, SearchText, TypeTags, FolderPath, MaxResults) → RowNames;
```
Reflection (FindFProperty). ⚠ Sprint D thêm `FilterFurnitureRows` (DT-based, trả Array of Name) — FilterFurnitureItems thành deprecated.

## Paths
```
Mesh : /Game/DatabaseProjectMaster/Model/Object_Model/
DA_  : /Game/cuong/UI/Data/FurnitureAssets/          ← legacy sau Sprint D
DT   : /Game/cuong/UI/Data/DT_FurnitureCatalog
MI   : /Game/DatabaseProjectMaster/Material/MaterialInstances/ (~2738 rows)
```

## Pipeline Dữ Liệu
```
Google Sheets → CSV → DT_FurnitureCatalog reimport → EUW_CreateDataAssets → DA_FurnitureItem
Python 1: populate BoundingSize | Python 2: update MeshFolderPath | (Sprint D: Python 7 ThumbnailSoft)
```
- S_FurnitureData.StaticMesh = Soft Object Reference. RowName = tên file mesh. Mesh path = MeshFolderPath + "/" + RowName.
- ⚠ Sau MỌI lần reimport CSV → chạy lại các Python script populate. Chi tiết: Python_Scripts.md.

## Game Instance
`Foff_GameInstance.FurnitureInventoryRef (WBP_FurnitureInventory)` — báo đồng nghiệp khi tích hợp.

---

## Variables
| Tên | Kiểu | Mô tả |
|-----|------|-------|
| `FolderTree` | Map String→String | Active tree (swap khi switch mode) |
| `FurnitureFolderTree` / `MaterialFolderTree` | Map | Cache tree 2 mode (v1.1) |
| `ActiveLevel1Path` | String | Folder cấp 1 đang chọn |
| `CurrentDepth` | Integer | Độ sâu chip tag |
| `CurrentCategory` | Name | Category đang lọc |
| `CurrentSearchText` | String | Text search |
| `CurrentFolderPath` | String | Folder đang chọn |
| `SearchTimerHandle` | Timer Handle | Debounce search |
| `CurrentPopup` | WBP_DetailPopup | Popup đang mở |
| `AllFurnitureItems` | Array of DA_FurnitureItem | Pre-load ở Construct ⚠ Sprint D XÓA |
| `FilteredItems` | Array of DA_FurnitureItem | Kết quả filter Furniture ⚠ Sprint D thay AllFilteredFurnitureRows |
| `CurrentPage` | Integer | Trang hiện tại (0-based), dùng chung 2 mode |
| `PageSize` | Integer | = 48 |
| `bIsDragging` / `DragOffset` / `InventoryPosition` | — | Drag window |
| `bIsMinimized` / `bIsMaximized` / `MinimizedHeight` / `OriginalSize` / `OriginalPosition` | — | Window state |
| `bIsReplaceMode` | Boolean | Đang replace mesh |
| **— v1.2 Resize Window —** | | |
| `bIsResizing` | Boolean | Đang kéo resize viền |
| `ResizeDirection` | Integer | 0=None,1=Top,2=Bottom,3=Left,4=Right,5=TL,6=TR,7=BL,8=BR |
| `ResizeStartMousePos` / `ResizeStartSize` / `ResizeStartPosition` | Vector2D | State lúc bắt đầu kéo |
| **— v1.1 Material —** | | |
| `CurrentInventoryMode` | E_InventoryMode | Furniture/Material (default Furniture) |
| `TargetFurnitureActor` | BP_FurnitureActor | Actor đang chỉnh material ← SET None ở Event Destruct (R2/R4) |
| `SelectedSlotIndex` | Integer | Slot đang chọn, default -1 |
| `AllFilteredMaterialRows` | Array of Name | Cache RowNames sau FilterMaterialItems |
| `PendingMaterialPath` / `PendingRowName` | String/Name | Chờ async load/apply |
| `ApplyMaterialTimerHandle` | Timer Handle | Debounce snapshot 0.5s |
| `UndoManagerRef` | BP_UndoManager | Cache, set ở Construct |
| `PendingRestoredActor` | BP_FurnitureActor | Chờ restore sau timer 0.1s ← SET None ở Destruct |
| **— C2 Favorites —** | | |
| `ActiveSpecialCategory` | Name | "" / "Recent" / "Favorite" |

---

## Layout (512×1024, resize 8 hướng)
```
Canvas Panel (root = Not Hit-Testable Self Only)
├── HB_TitleBar: BTN_TitleBar (drag) + BTN_Minimize/Maximize/Close
├── BackgroundBlur_246 → VerticalBox
│   ├── HB_TabBar (v1.1): BTN_Tab_Furniture | BTN_Tab_Material
│   ├── HB_Recent_Favorite (C2): BTN_RecentCategory | BTN_FavoriteCategory
│   └── HB_MainContent
│       ├── ScrollBox trái → VerticalBox_44 (folder tree)
│       └── VerticalBox phải
│           ├── HB_SlotSwatches (v1.1, Collapsed mặc định): HB_SwatchList + BTN_MaterialEdit(disabled) + BTN_ResetSlot + BTN_ResetAll
│           ├── ScrollBox: SearchBar, TB_Breadcrumb, VB_ChipTagArea
│           ├── SizeBox → CTV_FurnitureCard | SizeBox → CTV_MaterialCard
│           └── Pagination
├── BTN_MinimizedIcon (Collapsed mặc định)
├── — v1.2 Resize handles (Z cao nhất, Style None, Visible, Is Variable) —
├── BTN_ResizeTop/Bottom (6px dày) | BTN_ResizeLeft/Right (6px rộng)
└── BTN_ResizeTL/TR/BL/BR (12×12 góc)
```

---

## Widgets con

### WBP_SlotSwatch (v1.1)
```
Variables: SlotIndex | Dispatcher: OnSwatchClicked(ClickedSlotIndex)
Functions: SetSelected(bSelected), UpdateThumbnail(NewThumbnail)
Layout: 48×48 tròn, Common Lazy Image, Image overlay highlight
```

### WBP_MaterialCard (v1.2)
```
Interface: IUserObjectListEntry | Variables: MaterialItem (BP_MaterialItem), InventoryRef
Layout: LazyImage_ThumbMI, Button_InforMaterial, Button_ChangeMaterial, Button_FavoriteMaterial (heart, top-right 32×32)
OnListItemObjectSet: SetBrushFromLazyTexture(ThumbnailMI) → UpdateFavTint
Button_ChangeMaterial: InventoryRef.ApplyMaterial(MaterialItem.RowName)
Button_FavoriteMaterial: RowName → Toggle Favorite Material → UpdateFavTint
UpdateFavTint: Is Favorite Material(RowName) → T: đỏ (1,0.3,0.3,1) / F: trắng mờ (1,1,1,0.3)
Event Destruct: SET MaterialItem = None, InventoryRef = None   (R2/R4)
```

### WBP_TreeNode — FolderPath/FolderName/IndentLevel; Dispatcher OnNodeSelected(Path, Indent).
### WBP_ChipTag — FolderPath/FolderName/IndentLevel_ChipTag; Dispatcher OnChipSelected.
### WBP_ChipRow — ScrollBox Horizontal → HorizontalBox_ChipRow; RowIndentLevel.

### WBP_FurnitureCard (v1.4)
```
Interface: IUserObjectListEntry
Variables: FurnitureDA, InventoryRef, PreviewActor (BP_FurnitureActor), DragOverlayRef, FurnitureInputRef
Layout: LazyImage_Thumb, Button_InforItem, Button_ChangeMesh, Button_FavoriteFurniture (heart, top-right 32×32)

OnListItemObjectSet:
  Cast → DA_FurnitureItem → SET FurnitureDA → Set Brush from Lazy Texture
  Branch IsValid(InventoryRef): False → Get GameInstance → SET InventoryRef
  → UpdateFavTint
  ⚠ Sprint D (D.T6): chuyển sang BP_FurnitureItemView thay FurnitureDA

Button_InforItem: Call OnCardInfoClicked(FurnitureDA)
Button_FavoriteFurniture: FurnitureDA → Get Object Name → String to Name → RowName
  → Toggle Favorite Mesh(RowName) → UpdateFavTint
UpdateFavTint: Is Favorite Mesh(RowName) → tint đỏ/trắng mờ như MaterialCard
Drag-drop: ghost PreviewActor + surface snap — chi tiết WBP_DragOverlay_FurnitureCard.md
```

#### F_ExecuteReplace (v1.4 — BTN_ChangeMesh OnClicked, MULTI thay single v1.3)
```
Local: LocalNewActors : Array<BP_FurnitureActor>
Get All Actors Of Class(InputManager)[0] → Cast → SET FurnitureInputRef
GET MeshesToReplace → Length → Branch > 0: False → Return
CLEAR LocalNewActors
ForEach MeshesToReplace (OldActor):           ← Loop Body
  IsValid(OldActor) → True:
    GET Location/Rotation → LocalLoc/LocalRot
    Cast → GET PlacementSurfaceType → LocalSurfType
    Spawn BP_FurnitureActor(LocalLoc, LocalRot) → Cast → NewActor
    Load Asset Blocking(FurnitureDA.Mesh) → Cast StaticMesh → GET FurnitureMesh → Set Static Mesh
    SET MeshPath, DAPath (Get Object Path FurnitureDA), PlacementSurfaceType = LocalSurfType
    GET Tags → ADD "FurnitureSpawned" → SET Tags
    ADD NewActor → LocalNewActors
    Destroy Actor(OldActor)                   ← target = OldActor, KHÔNG để trống
ForEach Completed (KHÔNG trong Loop Body!):
  DeselectAll → SelectActors(LocalNewActors)  ← tự lo outline + gizmo
  Get All Actors(BP_UndoManager)[0] → CaptureSnapshot("Replace")   ← 1 lần
  UserPrefsManager → AddRecentMesh(RowName từ FurnitureDA)
  SET MeshesToReplace = LocalNewActors        ← replace tiếp được
```

### WBP_DetailPopup
```
SizeBox 400 → LazyImage_Thumbnail, TB_Name, TB_Category, TB_Description, BTN_BuyLink
Variables: FurnitureDA, bIsDragging, DragOffset, PopupPosition
BTN_XClosePopup: Remove from Parent | BTN_BuyLink: Launch URL(FurnitureDA.Link) | Drag via Tick
Chi tiết: WBP_DetailPopup.md
```

---

## Functions

### Event Construct (Sequence)
```
Then 0: Set Timer 0.1s → InitMinimizedHeight → SET CurrentCategory
Then 1: CLEAR AllFurnitureItems → GetAllAssets → ForEach → Cast DA_FurnitureItem → ADD
        → BindCategoryEvents → FilterBySearch          ⚠ Sprint D D.T7 XÓA đoạn load
Then 2: BuildFolderTree → SET FurnitureFolderTree → PopulateTreeColumn → FilterByFolderPath → UpdateTabHighlight
Then 3: GetAllActors(BP_UndoManager)[0] → SET UndoManagerRef → Bind OnRestoreCompleted → OnSceneRestored
Then 4: GetAllActors(InputManager)[0] → Bind selection handler
        ⚠ REFACTOR 10/06: bind OnSelectionChanged (dispatcher cũ OnMeshSelected/Deselected ĐÃ XÓA) — đối chiếu BP
```

### BuildFolderTree / BuildMaterialFolderTree — đọc DA_ / DT_MaterialInstancesCatalog → tách FolderPath → Map String→String. ⚠ Sprint D D.T7: đổi nguồn sang DT + C++ GetDistinctFolderPaths.

### PopulateTreeColumn — Clear VerticalBox_44 → tạo WBP_TreeNode từ FolderTree.

### FilterByFolderPath(FolderPath) — SET CurrentFolderPath → FilterBySearch(CurrentSearchText, CurrentCategory).

### FilterBySearch(SearchText, CategoryFilter)
```
SET CategoryFilter, CurrentSearchText
Branch SearchText != "" AND Len < 3 → Return
Branch CurrentInventoryMode == Material:
  T → PopulateMaterialGrid → Return
  F → FilterFurnitureItems(C++) → ForEach → AddItem(CTV_FurnitureCard)
      ⚠ Sprint D D.T5: đổi thành FilterFurnitureRows → AllFilteredFurnitureRows → DisplayPage
```

### SwitchInventoryMode(NewMode) — v1.1
```
SET CurrentPage = 0, CurrentInventoryMode = NewMode
Branch == Material:
  T → Visible CTV_MaterialCard + SlotSwatches nếu có actor; PopulateMaterialGrid;
      BuildMaterialFolderTree nếu chưa có; SET FolderTree = MaterialFolderTree; PopulateTreeColumn
  F → Visible CTV_FurnitureCard; SET FolderTree = FurnitureFolderTree; PopulateTreeColumn
      → FilterBySearch(CurrentSearchText, CurrentCategory)   ← BẮT BUỘC cuối (populate ngay khi switch)
```

### PopulateMaterialGrid — FilterMaterialItems(C++, DT, SearchText, TypeTags rỗng, FolderPath, MaxResults=20000) → SET AllFilteredMaterialRows → CurrentPage=0 → DisplayPage.

### DisplayPage — v1.1 (Material; ⚠ Sprint D mở rộng 2 mode + Clear List Items)
```
Start = CurrentPage × PageSize | End = Min(Start + PageSize, Length(AllFilteredMaterialRows))
ForLoop Start→End: GetDataTableRow → Create BP_MaterialItem → SET RowName, fields → AddItem(CTV_MaterialCard)
TotalPages = (Length + PageSize - 1) / PageSize   ← integer math thuần, KHÔNG Ceil(float)
SET Text(ET_PageDisplay, (CurrentPage+1) + "/" + TotalPages)
```

### ApplyMaterial(MaterialRowName) — Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0 → GetDataTableRow → SET PendingRowName/PendingMaterialPath → Call LoadAndApplyMaterial.

### LoadAndApplyMaterial (Custom Event — async, R1)
```
Async Load(PendingMaterialPath) → Cast MaterialInterface
→ CreateDMI(FurnitureMesh, MI_Source, SelectedSlotIndex) → SetMaterial
→ SetArrayElem(MaterialOverrides, SelectedSlotIndex, PendingMaterialPath)
→ Debounce 0.5s → CaptureSnapshot("ChangeMaterial")
→ GetDataTableRow(PendingRowName) → UpdateThumbnail swatch[SelectedSlotIndex]
```

### RefreshSlotSwatches — ClearChildren(HB_SwatchList) → TargetFurnitureActor → FurnitureMesh → GetStaticMesh → GetMaterialSlotNames → ForLoop tạo WBP_SlotSwatch + Bind OnSwatchClicked.

### Selection handlers (⚠ sau refactor 10/06 gọi từ bind OnSelectionChanged)
**Nhánh "selected" (Primary valid):**
```
v1.3 Trigger 3 — Replace mode: Branch bIsReplaceMode:
  T → SET MeshesToReplace (InputManager; bản cũ ghi MeshToReplace single — ĐÃ đổi multi v1.6, đối chiếu BP)
      Cast actor → GET DAPath → Load Asset Blocking → GET MeshFolderPath
      ⚠ Sprint D D.T8: đổi sang RowName→DT, fallback DAPath
      MeshFolderPath != "" → FilterByFolderPathWithUI(MeshFolderPath)
v1.1 — Material mode: Branch == Material:
  T → SET TargetFurnitureActor = actor → Visible HB_SlotSwatches → SET SelectedSlotIndex=-1
      → RefreshSlotSwatches → update thumbnails từ MaterialOverrides
```
**Nhánh "deselected" (Actors rỗng):**
```
v1.3 Trigger 1: Branch bIsReplaceMode: T → SET bIsReplaceMode=False (self + InputManager)
  → CLEAR MeshesToReplace → ExitReplaceMode
v1.1: Branch == Material: T → Collapsed HB_SlotSwatches → SET TargetFurnitureActor=None, SelectedSlotIndex=-1
```

### OpenMaterialModeForActor(Actor) — v2.3 (entry cho CB_ChangeMaterial)
```
IsValid(Actor) → False: Return
SET TargetFurnitureActor = Actor → SET SelectedSlotIndex = -1
Visible HB_SlotSwatches → RefreshSlotSwatches [+ update thumbnail từ MaterialOverrides]
```

### EnsureExpanded — v2.3
```
Branch bIsMinimized: False → Return
True → Visible: HB_Main_Content, Background_Blur_246, HB_Title_Bar; Collapsed BTN_Minimized_Icon
  SET bIsMinimized=False → Set Position In Viewport(10,10, RemoveDPI=True) → SET InventoryPosition=(10,10)
  Visible cả 8 BTN_Resize → UpdateResizeHandles
```
**⚠ Phải match BTN_MinimizedIcon OnClicked node-for-node** — restore-state function phải khớp source event (bài học đã trả giá).

### EnterReplaceMode — SET bIsReplaceMode=True → Regenerate All Entries(CTV_FurnitureCard). (Không dùng từ DetailPopup.)
### ExitReplaceMode — SET False → Regenerate All Entries (force ẩn BTN_ChangeMesh).
### RefreshCardReplaceMode — Regenerate All Entries; gọi từ DetailPopup SAU FilterByFolderPathWithUI.

### OnSceneRestored(RestoredSelectedActor) — Branch Material → SET PendingRestoredActor → SetTimer("ApplyRestoredActor", 0.1s) ← delay cho DeselectMesh chạy xong (race condition).
### ApplyRestoredActor — Branch Material → SET TargetFurnitureActor = PendingRestoredActor → IsValid: T → Visible + SelectedSlotIndex=-1 + RefreshSlotSwatches / F → Collapsed.

---

## Events

### OnTreeNodeClicked(SelectedPath, IndentLevel)
```
Indent==0: ClearChildren(VB_ChipTagArea) → SET ActiveLevel1Path → PopulateTreeColumn
           → FilterByFolderPath → SetText(TB_Breadcrumb, ""=="All product")
Indent==1: ClearChildren → Create ChipRow → ForEach ParseIntoArray(FolderTree[Path], ","):
           Create ChipTag → Bind OnChipSelected → AddChild → AddChild(VB_ChipTagArea) → FilterByFolderPath
```

### OnChipTagClicked(Path, Indent)
```
CurrentDepth = GetChildrenCount(VB_ChipTagArea) - Indent + 1 → ForLoop RemoveChildAt từ cuối
FilterByFolderPath → Map_Find(FolderTree, Path) True → tạo ChipRow + chips → AddChild
```

---

## Window Controls (v2.3)
```
Drag (BTN_TitleBar):
  OnPressed: bIsDragging=True; Slot as Canvas Slot(VerticalBox_0) → Get Position → CurrentPos
             DragOffset = MousePos on Viewport - CurrentPos
  OnReleased: bIsDragging=False
  Tick: NewPos = MousePos - DragOffset → Slot as Canvas Slot(VerticalBox_0) → Set Position(NewPos)
        → SET InventoryPosition → Call UpdateResizeHandles
  ← v2.3: drag + resize CÙNG hệ tọa độ Slot as Canvas Slot (lẫn Viewport → window nhảy)

Resize (8 BTN): OnPressed → StartResize(Direction). OnReleased KHÔNG cần — ResizeWindow tự check mouse button.
Maximize toggle: T → Position(0,0), Size=Viewport/Scale, 8 BTN_Resize Collapsed
                 F → restore Original, 8 BTN Visible + UpdateResizeHandles
Minimize: Collapse Blur + TitleBar → Show BTN_MinimizedIcon → 8 BTN Collapsed
BTN_MinimizedIcon: Show lại → Position(100,100) → 8 BTN Visible → UpdateResizeHandles
```

### StartResize(Direction) — SET bIsResizing, ResizeDirection, ResizeStartMousePos/Size/Position.
### UpdateResizeHandles — tính Position+Size 8 BTN theo VerticalBox_0 Canvas Slot.
### ResizeWindow — check mouse button, delta, 4 boolean hướng, clamp min, apply. **Chi tiết: WBP_ResizeWindow.md.**

---

## Level Blueprint
```
InputAction OpenFurnitureInventory → FlipFlop
  A: Create WBP_FurnitureInventory → Add to Viewport → Show Mouse Cursor → SET FurnitureInventoryRef (GameInstance)
  B: Remove from Parent
⚠ Sprint D D.T1: đổi sang single-instance toggle Visibility + đổi box-select guard Is In Viewport → Get Visibility
```

---

## 4C. REPLACE MODE — Navigate

### FilterByFolderPathWithUI(FolderPath) — Custom Event
```
1. Map Find(FolderTree, "") → Parse(",") → Level1Array → ForEach Break:
   FolderPath Contains Element → True: SET ActiveLevel1Path → Break
2. PopulateTreeColumn
3. Split(FolderPath, "Object_Model/") → Right S = ShortPath
4. Clear Children(VB_ChipTagArea) → Visible
5. CreateChipTagsForPath(ShortPath)
6. FilterByFolderPath(FolderPath)
7. SetText(TB_Breadcrumb, ShortPath)
```
Gọi từ: BTN_Replace (MeshControls), BTN_ChangeMesh (DetailPopup), selection handler Trigger 3.

### CreateChipTagsForPath(ShortPath)
```
Local: CurrentPath="" | CurrentIndentLevel=2
Clear Children(VB_ChipTagArea) → Visible
Parse(ShortPath, "/") → ForEach Break:
  CurrentPath = (rỗng? Element : CurrentPath + "/" + Element)
  CurrentPath == ActiveLevel1Path → skip (cấp 1)
  Map Find(FolderTree, CurrentPath) True:
    Create ChipRow (RowIndentLevel=CurrentIndentLevel) → Parse(Value, ",") → ForEach:
      Create ChipTag (Path = CurrentPath+"/"+Element, Indent=CurrentIndentLevel) → Bind → AddChild
    Completed → AddChild(VB_ChipTagArea) → CurrentIndentLevel += 1
```
- CurrentIndentLevel bắt đầu = 2 (khớp OnTreeNodeClicked). Clear Children NGOÀI loop.

---

## Keyboard Shortcuts
Q/W/E/R = Select/Move/Rotate/Scale | Delete = xóa | Alt+Z / Shift+Alt+Z = Undo/Redo | Ctrl+S/O = Save/Load | I = Inventory | Esc = Deselect | Ctrl+G / Ctrl+Shift+G = Group/Ungroup (Sprint 3)

---

## KEY LEARNINGS

### Inventory
- Blueprint loop 1852+ items → hit execution limit → C++ UFurnitureFilterLibrary
- Get All Widgets of Class trong OnListItemObjectSet nặng → Foff_GameInstance
- DA cần implement IUserObjectListEntry → OnListItemObjectSet fire
- DPI Scale ảnh hưởng Set Position → chia Get Viewport Scale
- Get Desired Size = 0 trong Event Construct → delay 0.1s
- FilterByFolderPath phải gọi FilterBySearch ở cuối → search vẫn hoạt động khi đổi folder
- Contains("", anything) = true → node "All" hiện tất cả
- Recent/Favorite cần SET FilteredItems + CurrentPage=0 + DisplayPage (không AddItem trực tiếp) — pagination đúng

### Material v1.1
- Get Static Mesh Component rỗng → Cast BP_FurnitureActor → GET FurnitureMesh
- CommonSearchBox không expose Set Text
- Set Background Color không work (Tint A=0) → Image overlay + Set Color and Opacity
- Timer 0.1s OnSceneRestored → ApplyRestoredActor fire SAU DeselectMesh
- Branch IsEmpty False dead-end → nối False vào SET FolderTree
- Broadcast OnRestoreCompleted dùng RestoredBPActor (Cast output), KHÔNG SpawnedActors[class var]
- SwitchInventoryMode False branch gọi FilterBySearch cuối
- Async Load: String → MakeSoftObjectPath → ToSoftObjectRef → AsyncLoadAsset; latent chỉ trong Custom Event
- SetArrayElem Size to Fit thay ForLoop resize
- SceneCapture2D Capture Source = "Final Color (LDR) in RGB" → fix black output
- TotalPages = (Length + PageSize - 1) / PageSize — integer thuần
- Root Canvas = Not Hit-Testable (Self Only) — không block WBP_MeshControls

### Resize Window (v2.3)
- Slot as Canvas Slot Get Size = (0,0) nếu chưa Set Size explicit → Set Size(512,1024) ở Construct
- Drag + Resize cùng hệ tọa độ Slot as Canvas Slot — lẫn lộn → window nhảy
- Resize button 6px → OnReleased fire khi rời button → dùng Is Mouse Button Down trong ResizeWindow
- False branch trong Sequence để trống — SET lại sẽ overwrite Then trước
- Tên đúng: "Slot as Canvas Slot" (KHÔNG "Slot as Canvas Panel Slot")

### Drag & Drop — Surface Snap (gốc)
- DeactivateGizmo trong On Drag Detected — fix trace không hit sàn khi Move mode
- Floor/Ceiling: Rotator 0,0,0 | Wall: Make Rot from X(Normal) → Yaw-90
- bTraceComplex=True; ActorsToIgnore=[PreviewActorRef]; On Drop dùng PreviewActorRef
- Move mode KHÔNG snap surface; pivot mesh = điểm lắp đặt thực tế

### EMS
- KHÔNG SET Tags trực tiếp — GET→ADD→SET (EMS track state qua Tags)
- MeshPath rỗng → Destroy trong ActorLoaded; Destroy FurnitureSpawned TRƯỚC EMS load

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|-----------|------|----------|
| 1.0 | 22/04/2026 | Inventory cơ bản — filter, drag drop, folder tree |
| 2.0 | 20/05/2026 | Material v1.1 đầy đủ |
| 2.1 | 25/05/2026 | Đợt C: Recent/Favorite bar + UpdateFavTint + persist switch mode |
| 2.2 | 25/05/2026 | Fix DisplayPage integer math; root Not Hit-Testable; doc DisplayPage |
| 2.3 | 27/05 + 08/06/2026 | Resize Window 8 hướng + drag Slot as Canvas Slot; OpenMaterialModeForActor + EnsureExpanded; WBP_FurnitureCard v1.4 F_ExecuteReplace (multi) |
| 2.4 | 11/06/2026 | **BẢN HỢP NHẤT** — merge v2.2 + 2 patch; thêm cảnh báo refactor dispatcher 10/06 + ghi chú Sprint D. File patch có thể xóa. |
