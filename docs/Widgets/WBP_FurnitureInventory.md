# WBP_FurnitureInventory
**HỢP NHẤT TỪ 4 file:** v2.2 + v2.3 Resize patch + v2.3 Inventory_Card patch (08/06) → WBP_FurnitureInventory.md (11/06) + v2.4 dispatcher refactor (10/06)
**Phiên bản:** 3.0 | **Cập nhật:** 25/06/2026 — C5.0 Combo Folder Tree + Filter (tree hiển thị đúng, fix card render pending)

> **v2.6 (18/06/2026):** Thêm `IsPathActive` (Pure) + `UpdateFolderHighlights` cho
> tính năng active-folder highlight (xem chi tiết node flow mục dưới).
> `BTN_FavoriteCategory`/`BTN_RecentCategory` thêm ClearChildren+Collapse breadcrumb
> đầu function. Fix Bug-Pagination: Int to Float trước Ceil ở cả 2 nhánh
> Material/Furniture trong logic Next-page.

> **v2.5 (Sprint D.T6):** WBP_FurnitureCard section cập nhật: `OnListItemObjectSet` cast `BP_FurnitureItemView` thay `DA_FurnitureItem`; `Button_InforItem → OnCardInfoClicked(CardRowName)` thay FurnitureDA. `OnMeshSelected` nhánh REPLACE: Branch RowName != "" → DT lookup MeshFolderPath (fallback DAPath). `OnCardInfoClicked` handler: nhận RowName thay DA.
Inventory duyệt & lọc nội thất + Material Editor (v1.1) + Resize Window + Replace multi

> **⚠ SPRINT D sắp thay đổi lớn file này:** Furniture mode chuyển sang DataTable+RowName (bỏ AllFurnitureItems preload), inventory single-instance, DisplayPage 2 mode. Xem `Gate1_SprintD_Execution_Opus.md`. Doc này = trạng thái TRƯỚC Sprint D.
> **v2.4 (Refactor dispatcher 10/06):** Bind `OnSelectionChanged` thay `OnMeshSelected`/`OnMeshDeselected` (đã XÓA ở InputManager). Thêm `OnSelectionChangedMaterial(Actors, Primary)` → call `OnMeshSelected(Primary)`. `OnMeshSelected` (internal): replace branch SET `MeshesToReplace` (array) thay single; material branch thêm guard `IsValid`. XÓA `OnMeshDeselected`. `EnterReplaceMode` + `EnsureExpanded` đầu hàm. Đọc kèm `Sprint3_Regression_DualDispatcher_Log.md`.
> **v2.3 (08/06):** OpenMaterialModeForActor, EnsureExpanded, F_ExecuteReplace multi (WBP_FurnitureCard v1.4).
> **v2.2 (25/05):** Fix DisplayPage integer math, root Canvas Not Hit-Testable, Resize Window 8 hướng.

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
| `CurrentInventoryMode` | E_InventoryMode | Furniture/Material/Combo (default Furniture) ← C5.0 thêm value Combo |
| `TargetFurnitureActor` | BP_FurnitureActor | Actor đang chỉnh material ← SET None ở Event Destruct (R2/R4) |
| `SelectedSlotIndex` | Integer | Slot đang chọn, default -1 |
| `AllFilteredMaterialRows` | Array of Name | Cache RowNames sau FilterMaterialItems |
| `PendingMaterialPath` / `PendingRowName` | String/Name | Chờ async load/apply |
| `ApplyMaterialTimerHandle` | Timer Handle | Debounce snapshot 0.5s |
| `UndoManagerRef` | BP_UndoManager | Cache, set ở Construct |
| `PendingRestoredActor` | BP_FurnitureActor | Chờ restore sau timer 0.1s ← SET None ở Destruct |
| **— C2 Favorites —** | | |
| `ActiveSpecialCategory` | Name | "" / "Recent" / "Favorite" |
| **— C3b Combo Save Dialog —** | | |
| `PendingSelectedActors` | Array BP_FurnitureActor | Buffer đóng băng selection trước khi mở dialog async |
| `PendingCenter` | Vector | Buffer Center tương ứng với PendingSelectedActors |
| `SaveComboDialogRef` | WBP_SaveComboDialog | Ref dialog đang mở — SET None ở Event Destruct (R4) |
| **— C5.0 Combo Folder Tree —** | | |
| `CurrentComboFolderPath` | String | `__ALL__` = xem tất cả; `""` = Chưa phân loại; path thường = filter folder đó + con |
| `ComboFolderTree` | Map\<String, String\> | Cây folder combo: Key=path cha (hoặc ""), Value=CSV tên con cấp trực tiếp |
| `bHasUncategorized` | Boolean | false — có combo FolderPath="" → PopulateComboTreeColumn hiện node "Chưa phân loại" |

⚠️ **VRAM leak:** TargetFurnitureActor + PendingRestoredActor + SaveComboDialogRef là hard ref → SET None ở Event Destruct.

---

## Layout (512×1024, resize 8 hướng)
```
Canvas Panel (root = Not Hit-Testable Self Only)
├── HB_TitleBar: BTN_TitleBar (drag) + BTN_Minimize/Maximize/Close
├── BackgroundBlur_246 → VerticalBox
│   ├── HB_TabBar: BTN_Tab_Furniture | BTN_Tab_Material | BTN_Tab_Combo ← C5.0 (OnClicked → SwitchInventoryMode(Combo))
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

## Widgets Con

### WBP_SlotSwatch (v1.1)
```
Variables: SlotIndex : Integer
Event Dispatcher: OnSwatchClicked(ClickedSlotIndex : Integer)
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

### WBP_FurnitureCard (v1.0 Sprint D.T6 — tách thành file riêng)
```
Interface: IUserObjectListEntry
Variables: CardRowName (Name), InventoryRef, PreviewActor (BP_FurnitureActor), DragOverlayRef
  ← XÓA FurnitureDA (Sprint D.T6). Xem WBP_FurnitureCard.md để biết đầy đủ.
Layout: LazyImage_Thumb, Button_InforItem, Button_ChangeMesh, Button_FavoriteFurniture (heart, top-right 32×32)

OnListItemObjectSet (v1.0 Sprint D):
  Cast → BP_FurnitureItemView → SET CardRowName = ItemView.RowName
  DT lookup ThumbnailSoft → Set Brush from Lazy Texture
  → UpdateFavTint

Button_InforItem: Call OnCardInfoClicked(CardRowName)    ← v1.0: truyền RowName thay FurnitureDA
Button_FavoriteFurniture: Toggle Favorite Mesh(CardRowName) → UpdateFavTint
UpdateFavTint: Is Favorite Mesh(CardRowName) → tint đỏ/trắng mờ như MaterialCard
Drag-drop: ghost PreviewActor + surface snap — chi tiết WBP_FurnitureCard.md + WBP_DragOverlay_FurnitureCard.md
```

#### F_ExecuteReplace (v1.4 + BugFix 12/06 GroupID — MULTI thay single v1.3)
```
Local: LocalNewActors : Array<BP_FurnitureActor>
Get All Actors Of Class(InputManager)[0] → Cast → SET FurnitureInputRef
GET MeshesToReplace → Length → Branch > 0: False → Return
CLEAR LocalNewActors
ForEach MeshesToReplace (OldActor):           ← Loop Body
  IsValid(OldActor) → True:
    GET Location/Rotation → LocalLoc/LocalRot
    Cast → GET PlacementSurfaceType → LocalSurfType
    Cast OldActor → GET GroupID → OldGroupID  ← [BugFix 12/06] TRƯỚC destroy
    Spawn BP_FurnitureActor(LocalLoc, LocalRot) → Cast → NewActor
    Load Asset Blocking(FurnitureDA.Mesh) → Cast StaticMesh → GET FurnitureMesh → Set Static Mesh
    SET MeshPath, DAPath (Get Object Path FurnitureDA), PlacementSurfaceType = LocalSurfType
    SET NewActor.GroupID = OldGroupID          ← [BugFix 12/06] TRƯỚC Destroy
    GET Tags → ADD "FurnitureSpawned" → SET Tags
    ADD NewActor → LocalNewActors
    Destroy Actor(OldActor)                    ← target = OldActor, KHÔNG để trống
ForEach Completed (KHÔNG trong Loop Body!):
  DeselectAll → SelectActors(LocalNewActors)  ← tự lo outline + gizmo
  Get All Actors(BP_UndoManager)[0] → CaptureSnapshot("Replace")   ← 1 lần
  UserPrefsManager → AddRecentMesh(CardRowName)    ← v1.0 Sprint D: trực tiếp
  SET MeshesToReplace = LocalNewActors        ← replace tiếp được
```
> Full doc: WBP_DragOverlay_FurnitureCard.md

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
Then 4: GetAllActors(BP_FurnitureInputManager)[0]
        → Bind OnSelectionChanged → OnSelectionChangedMaterial   ← v2.4 (XÓA OnMeshSelected + OnMeshDeselected)
```
> ⚠️ **v2.4:** KHÔNG còn `Bind OnMeshSelected` + `Bind OnMeshDeselected`. Mọi phản ứng selection của inventory đi qua `OnSelectionChanged`. **Bind PHẢI ở Event Construct** — đặt trong handler → handler không fire → không bao giờ bind (bug đã trả giá).

---

### BuildFolderTree / BuildMaterialFolderTree
Đọc DA_FurnitureItem / DT_MaterialInstancesCatalog → tách FolderPath → xây Map String→String. ⚠ Sprint D D.T7: đổi nguồn sang DT + C++ GetDistinctFolderPaths.

### PopulateTreeColumn
Clear VerticalBox_44 → tạo WBP_TreeNode từ FolderTree (active tree).

### FilterByFolderPath(FolderPath)
```
SET CurrentFolderPath = FolderPath → Call FilterBySearch(CurrentSearchText, CurrentCategory)
```

### FilterBySearch(SearchText, CategoryFilter)
```
SET CategoryFilter, SET CurrentSearchText
Branch SearchText != "" AND Len < 3 → Return
Branch CurrentInventoryMode == Material:
  T → Call PopulateMaterialGrid → Return
  F → FilterFurnitureItems(C++) → ForEach → AddItem(CTV_FurnitureCard)
      ⚠ Sprint D D.T5: đổi thành FilterFurnitureRows → AllFilteredFurnitureRows → DisplayPage
```

### SwitchInventoryMode(NewMode) — v1.1 / C5.0 update
```
SET CurrentPage = 0, SET CurrentInventoryMode = NewMode
Collapse: CTV_FurnitureCard, CTV_MaterialCard, HB_SlotSwatches, CTV_ComboCard  ← C5.0 thêm CTV_ComboCard
Branch(NewMode == Combo):  ← C5.0: kiểm tra TRƯỚC nhánh Material
  True  → Visible CTV_ComboCard
           BuildComboFolderTree → PopulateComboTreeColumn → FilterComboByFolder("__ALL__")
  False → Branch NewMode == Material:
            T → Visible CTV_MaterialCard + SlotSwatches nếu có actor
                PopulateMaterialGrid; BuildMaterialFolderTree nếu chưa có
                SET FolderTree = MaterialFolderTree; PopulateTreeColumn
            F → Visible CTV_FurnitureCard; SET FolderTree = FurnitureFolderTree; PopulateTreeColumn
                Call FilterBySearch(CurrentSearchText, CurrentCategory)   ← BẮT BUỘC cuối
```

### PopulateMaterialGrid — v1.1
```
FilterMaterialItems(C++, DT_MaterialInstancesCatalog, CurrentSearchText,
  TypeTags=rỗng, CurrentFolderPath, MaxResults=20000)
→ SET AllFilteredMaterialRows → SET CurrentPage = 0 → Call DisplayPage
```

### DisplayPage — v1.1 (⚠ Sprint D mở rộng 2 mode)
```
Start = CurrentPage × PageSize
End   = Min(Start + PageSize, Length(AllFilteredMaterialRows))
ForLoop Start→End:
  GetDataTableRow(DT_MaterialInstancesCatalog, AllFilteredMaterialRows[i])
  → Create BP_MaterialItem → SET RowName, fields
  → AddItem(CTV_MaterialCard, MaterialItem)

← Tính TotalPages — integer math thuần (KHÔNG Ceil float):
TotalPages = (Length(AllFilteredMaterialRows) + PageSize - 1) / PageSize
SET Text(ET_PageDisplay, (CurrentPage+1) + "/" + TotalPages)
```
> TotalPages = `(Length + PageSize - 1) / PageSize` đúng mọi giá trị. Dùng Ceil(float) sai vì integer division trước Ceil → kết quả 0 khi Length < PageSize.

### ApplyMaterial(MaterialRowName) — v1.1
```
Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0:
  T → GetDataTableRow → SET PendingRowName, SET PendingMaterialPath → Call LoadAndApplyMaterial
```

### LoadAndApplyMaterial — v1.1 (Custom Event, async)
```
Async Load(PendingMaterialPath) → Cast MaterialInterface
→ CreateDMI(FurnitureMesh, MI_Source, SelectedSlotIndex) → SetMaterial
→ SetArrayElem(MaterialOverrides, SelectedSlotIndex, PendingMaterialPath)
→ Debounce 0.5s → CaptureSnapshot("ChangeMaterial")
→ GetDataTableRow(PendingRowName) → UpdateThumbnail swatch[SelectedSlotIndex]
```

### RefreshSlotSwatches — v1.1
```
ClearChildren(HB_SwatchList)
GET TargetFurnitureActor → FurnitureMesh → GetStaticMesh → GetMaterialSlotNames
ForLoop → Create WBP_SlotSwatch → Bind OnSwatchClicked → AddChild
```

---

## Selection Handlers — v2.4 (Dispatcher Refactor)

### OnSelectionChangedMaterial(Actors, Primary) — v2.4: MỚI
```
← Bound từ InputManager.OnSelectionChanged (dispatcher duy nhất sau refactor 10/06)
→ Call OnMeshSelected(Primary)    ← tái dùng handler nội bộ, không duplicate logic
```
> Cầu nối: OnSelectionChanged (mới) → OnMeshSelected (handler cũ giữ logic). Dispatcher `Primary` = None khi deselect → handler nội bộ sẽ xử lý nhánh False.

### OnMeshSelected(SelectedActor) — handler nội bộ — v2.4: VIẾT LẠI
> ⚠️ Custom event nội bộ của inventory — KHÁC dispatcher `OnMeshSelected` đã XÓA ở InputManager. Nay được trigger qua `OnSelectionChangedMaterial`.

**Nhánh REPLACE (v1.3 + v2.4 fix + v2.5 Sprint D.T6 RowName):**
```
Branch bIsReplaceMode == True:
  T →
    Get All Actors Of Class(BP_FurnitureInputManager)[0] → IsValid →
      SET MeshesToReplace = InputManager.SelectedActors     ← v2.4: array
    Branch IsValid(SelectedActor):                          ← guard folder nav (deselect → skip)
      T →
        ← v2.5 Sprint D.T6: Branch RowName thay DAPath→Load
        Cast SelectedActor → GET RowName
        Branch(RowName != ""):
          True:
            Get Data Table Row(DT_FurnitureCatalog, RowName) → Row Found → GET MeshFolderPath
            → Branch MeshFolderPath != "" → FilterByFolderPathWithUI(MeshFolderPath)
          False (save cũ RowName rỗng — fallback DAPath):
            Cast → GET DAPath → Load Asset Blocking → Cast DA_FurnitureItem → GET MeshFolderPath
            → Branch MeshFolderPath != "" → FilterByFolderPathWithUI(MeshFolderPath)
  F → (tiếp tục nhánh material)
```

**Nhánh MATERIAL (v1.1 + v2.4 guard):**
```
Branch CurrentInventoryMode == Material:
  T →
    Branch IsValid(SelectedActor):                          ← v2.4: guard (OnSelectionChanged fire None khi deselect)
      T → SET TargetFurnitureActor = SelectedActor
          → Visible HB_SlotSwatches → SET SelectedSlotIndex = -1
          → RefreshSlotSwatches → Update thumbnails từ MaterialOverrides
      F → SET TargetFurnitureActor = None                  ← thay thế handler OnMeshDeselected cũ
          → Collapsed HB_SlotSwatches → SET SelectedSlotIndex = -1
```

### OnMeshDeselected — ĐÃ XÓA (v2.4)
> Logic collapse material giờ ở nhánh material False (IsValid=False) của `OnMeshSelected`, kích hoạt qua `OnSelectionChanged` khi Primary = None.

---

### OpenMaterialModeForActor(Actor) — v2.3 (entry cho CB_ChangeMaterial)
```
Branch IsValid(Actor): False → Return
SET TargetFurnitureActor = Actor → SET SelectedSlotIndex = -1
Visible HB_SlotSwatches → RefreshSlotSwatches [+ update thumbnail từ MaterialOverrides]
```

### EnsureExpanded — v2.3
```
Branch bIsMinimized:
  False → Return  (đang mở bình thường — no-op)
  True:
    Set Visibility(HB_Main_Content, Visible)   ← QUAN TRỌNG — thiếu → expand không hoạt động
    Set Visibility(Background_Blur_246, Visible)
    Set Visibility(HB_Title_Bar, Visible)
    Set Visibility(BTN_Minimized_Icon, Collapsed)
    SET bIsMinimized = False
    Set Position In Viewport(self, X=10, Y=10, Remove DPI Scale=True)
    SET Inventory Position = (10, 10)
    Set Visibility(BTN_Resize_Bottom/Left/Right/TR/TL/BR/BL/Top, Visible)
    Call UpdateResizeHandles
```
> ⚠️ Phải match BTN_MinimizedIcon OnClicked node-for-node. Thiếu 1 widget → expand không hoạt động. Bài học: restore-state function phải khớp source event.

### EnterReplaceMode — v1.3 + v2.4
```
Call EnsureExpanded (Target=self)   ← v2.4: bung inventory nếu đang minimize (fix replace lúc minimize không bung)
SET bIsReplaceMode = True
Regenerate All Entries(CTV_FurnitureCard)
← Dùng khi bật Replace VÀ không cần navigate folder (BTN_Replace toggle ON)
← KHÔNG dùng từ DetailPopup (vì FilterByFolderPathWithUI sẽ clear cards sau đó)
```

### ExitReplaceMode — v1.3
```
SET bIsReplaceMode = False
Regenerate All Entries(CTV_FurnitureCard)   ← force tất cả cards ẩn BTN_ChangeMesh
```

### RefreshCardReplaceMode — v1.3
```
Regenerate All Entries(CTV_FurnitureCard)
← Gọi từ bên ngoài (DetailPopup) sau FilterByFolderPathWithUI populate xong
← Đảm bảo cards mới thấy bIsReplaceMode=True → hiện BTN_ChangeMesh
```

### OnSceneRestored(RestoredSelectedActor) — v1.1
```
← Bound từ UndoManagerRef.OnRestoreCompleted
Branch CurrentInventoryMode == Material:
  T → SET PendingRestoredActor = RestoredSelectedActor
      SetTimerByFunctionName("ApplyRestoredActor", 0.1s)
      ← delay cho LeftMouseButton DeselectMesh chạy xong trước (race condition)
```

### ApplyRestoredActor — v1.1
```
Branch CurrentInventoryMode == Material:
  T → SET TargetFurnitureActor = PendingRestoredActor
      Branch IsValid:
        T → Visible + SET SelectedSlotIndex=-1 + RefreshSlotSwatches + Update thumbnails MaterialOverrides
        F → Collapsed
```

---

## Combo Vocabulary Functions (C3a)

### GetExistingFolders() → FolderResult: Array\<String\>
**Local vars:** LocalFolders (Array String), TempFolder (String)

CLEAR LocalFolders

ForEach AllComboViews_Combo:

Loop Body:
- GET ArrayElement.FolderPath ●→ SET TempFolder
- Branch(TempFolder == ""): True → dead-end (skip)
- False → Replace(TempFolder, "\\" → "/") ●→ SET TempFolder
  - Branch Contains(LocalFolders, TempFolder): True → dead-end (skip)
  - False → ADD TempFolder ●→ LocalFolders

Completed → Return(FolderResult = LocalFolders)

### GetAllUsedTags() → TagsResult: Array\<String\>
**Local vars:** LocalTags (Array String), TempTagArray (Array String), TempTag (String)

CLEAR LocalTags

ForEach AllComboViews_Combo (outer):

Loop Body:
- GET ArrayElement.Tags ●→ SET TempTagArray
- ForEach TempTagArray (inner):
  - Loop Body:
    - ToLower(ArrayElement_inner) ●→ SET TempTag
    - Branch(TempTag == ""): True → dead-end (skip)
    - False → Branch Contains(LocalTags, TempTag): True → dead-end (skip)
    - False → ADD TempTag ●→ LocalTags
  - Completed → (trống)
- Completed → (trống)

Completed → Return(TagsResult = LocalTags)

⚠ Cả 2 hàm dùng `AllComboViews_Combo` — class var Array\<BP_ComboItemView\> được populate bởi LoadComboLibrary. Gọi sau khi library load xong.

---

## C4 — CTV_ComboCard + LoadComboLibrary

### Widget Variable (thêm vào designer)
```
CTV_ComboCard : Tile View
  Is Variable = True
  Entry Widget Class = WBP_ComboCard
  Visibility = Collapsed  ← mặc định; C5 show khi switch sang tab 🧩
```

### LoadComboLibrary — Custom Event (cập nhật C4)
Bound tới `OnComboLibraryChanged` + gọi trực tiếp từ Event Construct.

Cuối hàm (sau khi populate `AllComboViews_Combo`) thêm:
```
CTV_ComboCard.Clear List Items
ForEach AllComboViews_Combo:
  Loop Body: CTV_ComboCard.Add Item(ArrayElement)
```

**Test PASS (24/06/2026):** 19 combo hiện đúng tên + badge ×N món.

### Event Construct (cập nhật C4 — thêm vào Sequence)
```
Then 5: Bind OnComboLibraryChanged → LoadComboLibrary
        LoadComboLibrary  ← gọi ngay lần đầu để populate CTV khi mở inventory
```

---

## C3b — Save Combo Dialog Flow

### OpenSaveComboDialog(SelectedActors : Array BP_FurnitureActor, Center : Vector) — Custom Event
```
SET PendingSelectedActors = SelectedActors
SET PendingCenter = Center
GetExistingFolders() → TempFolders
GetAllUsedTags() → TempTags
Create Widget(WBP_SaveComboDialog, ExistingFolders=TempFolders, TagVocabulary=TempTags) → SET SaveComboDialogRef
Add to Viewport(SaveComboDialogRef, ZOrder=99)
Bind OnDialogConfirmed(SaveComboDialogRef) → OnSaveComboConfirmed
Bind OnDialogCancelled(SaveComboDialogRef) → OnSaveComboDialogClosed
Get Player Controller → Set Input Mode UI Only(InWidgetToFocus=SaveComboDialogRef)
```

### OnSaveComboConfirmed(ComboName, FolderPath, Description : String; Tags : Array String) — Custom Event
```
← Bound từ SaveComboDialogRef.OnDialogConfirmed
Get All Actors Of Class(BP_ComboManager) → Get(0) → Cast → ComboManagerRef
IsValid(ComboManagerRef):
  True → SaveComboFromSelection(PendingSelectedActors, PendingCenter, ComboName, Description, FolderPath, Tags)
  False → Print String "OnSaveComboConfirmed: ComboManager not found"
OnSaveComboDialogClosed    ← luôn đóng dialog, dù save fail
```

### OnSaveComboDialogClosed — Custom Event
```
← Bound từ SaveComboDialogRef.OnDialogCancelled + gọi cuối OnSaveComboConfirmed
SET SaveComboDialogRef = None
SET PendingSelectedActors = []     (Make Array rỗng)
SET PendingCenter = (0, 0, 0)
Get Player Controller → Set Input Mode Game And UI
```

---

## C5.0 — Combo Folder Tree + Filter

> **Trạng thái 25/06/2026:** Tree hiển thị đúng (All / Chưa phân loại / folder cấp 1 phẳng).
> Filter logic xong. **ĐANG FIX:** CTV_ComboCard không render card — đang thử Set List Items thay Add Item (deviation D3).

### AddFolderPathToTree(FullPath : String) — Function
Tách path đa cấp → add cặp cha→con vào `ComboFolderTree`.
**Local vars:** ParentPath (String, ""), CurrentPath (String, "")
```
Parse Into Array(FullPath, "/") → Segments
ForEach Segments (element):
  Branch(CurrentPath == "")
    True  → SET CurrentPath = element
    False → SET CurrentPath = CurrentPath + "/" + element
  Map Find(ComboFolderTree, Key=ParentPath) → Value, bFound
  Branch(bFound)
    True  → Parse Into Array(Value, ",") → CSV_Array
             Branch( NOT Array Contains(CSV_Array, element) )   ← exact match (KHÔNG String Contains)
               True  → Map Add(Key=ParentPath, Value=Value + "," + element)
               False → [dead-end]
    False → Map Add(Key=ParentPath, Value=element)
  SET ParentPath = CurrentPath   ← 3 nhánh exec merge vào 1 SET node
ForEach Completed: [dead-end]
```
> **D1:** dùng Parse Into Array + Array Contains (exact), KHÔNG String Contains (substring match sai).

### BuildComboFolderTree() — Function
```
Map Clear(ComboFolderTree)
SET bHasUncategorized = false
Local: LocalViews = AllComboViews_Combo
ForEach LocalViews (element):
  IsValid(element) Branch
    False → [dead-end]
    True  → GET element.FolderPath → fp
             Branch(fp == "")
               True  → SET bHasUncategorized = true → [dead-end]
               False → AddFolderPathToTree(fp)
ForEach Completed: [dead-end]
```

### PopulateComboTreeColumn() — Function
Dựng WBP_TreeNode vào `VerticalBox_44` (cột tree CHUNG với furniture/material).
```
Clear Children(VerticalBox_44)

// Node "Tất cả" (luôn có)
Create Widget(WBP_TreeNode) → AllNode
  SET AllNode.FolderPath = "__ALL__"
  SET AllNode.FolderName = "Tat ca"          ← D2: SET var trực tiếp TRƯỚC RefreshDisplay
  SET AllNode.IndentLevel = 0
  RefreshDisplay(bIsActive = (CurrentComboFolderPath == "__ALL__"))
  Add Child(VerticalBox_44, AllNode)
  Bind OnNodeSelected(AllNode) → Create Event → OnComboTreeNodeClicked(self)

// Node "Chưa phân loại" (nếu bHasUncategorized)
Branch(bHasUncategorized)
  True  → Create Widget(WBP_TreeNode) → UncatNode
           SET UncatNode.FolderPath = "" | FolderName = "Chua phan loai" | IndentLevel = 0
           RefreshDisplay(bIsActive = (CurrentComboFolderPath == ""))
           Add Child | Bind OnNodeSelected → OnComboTreeNodeClicked
  False → [dead-end]

// Folder cấp 1 từ Map[""]
Map Find(ComboFolderTree, Key="") → Value, bFound
Branch(bFound)
  False → [dead-end]
  True  → Parse Into Array(Value, ",") → FolderNames
           ForEach FolderNames (element):
             Create Widget(WBP_TreeNode) → FolderNode
             SET FolderNode.FolderPath = element | FolderName = element | IndentLevel = 1
             RefreshDisplay(bIsActive = (CurrentComboFolderPath == element))
             Add Child | Bind OnNodeSelected → OnComboTreeNodeClicked
           Completed: [dead-end]
```
> Tree TỐI GIẢN: chỉ render cấp 1 phẳng + filter cha-hiện-con (nested folder vẫn lọc đúng qua StartsWith). Expand cấp 2/3 trong tree = polish C5 sau.

### FilterComboByFolder(FolderPath : String) — Function
```
SET CurrentComboFolderPath = FolderPath
Clear List Items(CTV_ComboCard)                    ← D3: Clear trước
Local: LocalViews = AllComboViews_Combo
Local: FilteredItems (Array<BP_ComboItemView>)
ForEach LocalViews (element):
  IsValid(element) Branch
    False → [dead-end]
    True  → GET element.FolderPath → fp
             Branch(FolderPath == "__ALL__")
               True  → Add FilteredItems(element)
               False → Branch(FolderPath == "")
                         True  → Branch(fp == "") → True: Add FilteredItems(element)
                         False → Branch( (fp == FolderPath) OR (fp StartsWith FolderPath+"/") )
                                   True → Add FilteredItems(element)
ForEach Completed:
  Set List Items(CTV_ComboCard, FilteredItems)     ← D3: 1 lần, stable render
```
> ⚠️ **ĐANG FIX (25/06):** Set List Items chưa hiện card — investigation pending. Thử thay bằng Clear + ForEach Add Item xem có khác không.

### RefreshComboFolderUI() — Function (lớp refresh duy nhất cho C5.2→C5.6)
```
LoadComboLibrary
BuildComboFolderTree → PopulateComboTreeColumn
Branch(CurrentComboFolderPath == "__ALL__")
  True  → FilterComboByFolder("__ALL__")
  False → Branch(CurrentComboFolderPath == "")
            True  → FilterComboByFolder("")
            False → Map Contains(ComboFolderTree, CurrentComboFolderPath) → bExists
                    Branch(bExists) True → FilterComboByFolder(CurrentComboFolderPath)
                                   False → FilterComboByFolder("__ALL__")  ← folder xóa rồi
```
> Check `__ALL__` và `""` riêng vì 2 sentinel KHÔNG nằm trong ComboFolderTree (Map Contains = False → sẽ nhầm về __ALL__).

### OnComboTreeNodeClicked(SelectedPath : String, IndentLevel : Integer) — Custom Event
Bound từ mọi WBP_TreeNode trong PopulateComboTreeColumn.
```
FilterComboByFolder(FolderPath = SelectedPath)
PopulateComboTreeColumn   ← SAU Filter → CurrentComboFolderPath đúng → highlight đúng
```

---

## Events

### OnCardInfoClicked(RowName : Name) — v2.5 Sprint D.T6 (thay DA DA_FurnitureItem)
```
← Bound từ WBP_FurnitureCard.Button_InforItem (truyền CardRowName)
GET CurrentPopup → IsValid → Remove from Parent → SET CurrentPopup = None
Create WBP_DetailPopup → Add to Viewport
Set Position In Viewport(chuột + Y+10) → SET PopupPosition
SET CurrentPopup = popup
Call InitPopup(RowName, bFromScene=False)
```
> Cũ (v2.4): `OnCardInfoClicked(DA : DA_FurnitureItem)` → `InitPopup(DA, False)`. Sprint D.T6: bỏ DA, dùng RowName.

---

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

## Window Controls (v2.3 Resize)
```
Drag (BTN_TitleBar):
  OnPressed: bIsDragging=True; Slot as Canvas Slot(VerticalBox_0) → Get Position → CurrentPos
             DragOffset = MousePos on Viewport - CurrentPos
  OnReleased: bIsDragging=False
  Tick: NewPos = MousePos - DragOffset → Slot as Canvas Slot → Set Position(NewPos)
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

## Replace Mode — Navigate

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
Gọi từ: BTN_Replace (MeshControls), BTN_ChangeMesh (DetailPopup), selection handler Replace branch.

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

### IsPathActive(ThisPath: String) → ReturnValue: Boolean — Pure function

```
CurrentFolderPath ●→ ==.A
ThisPath ●→ ==.B
ThisPath ●→ Append.A("/" ●→ Append.B) ●→ StartsWith.InPrefix
CurrentFolderPath ●→ StartsWith.SourceString
==.ReturnValue ●→ OR.A
StartsWith.ReturnValue ●→ OR.B
OR ▶/●→ Return Node.ReturnValue
```

⚠ Pure function — KHÔNG được chèn node impure (Print String...) vào đây, sẽ phá
exec flow. Debug chỗ này phải đặt ở hàm GỌI nó (UpdateFolderHighlights), không
đặt trong chính IsPathActive.

### UpdateFolderHighlights() — impure Function

```
ForEach(VerticalBox_44.Children) → Cast WBP_TreeNode
  → GET FolderPath (CỦA NODE NÀY, không phải biến class)
  → IsPathActive(FolderPath) → RefreshDisplay(bIsActive=ReturnValue)
ForEach(VB_ChipTagArea.Children) → Cast WBP_ChipRow
  → ForEach(HorizontalBox_ChipRow.Children) → Cast WBP_ChipTag
    → GET FolderPath_ChipTag → IsPathActive(...) → SetHighlight(bIsActive=...)
```

**3 điểm gọi `UpdateFolderHighlights`:**
1. Cuối `CreateChipTagsForPath` — gắn vào `Completed` của ForEachLoopWithBreak
   ngoài cùng (trước đây dead-end).
2. Trong `OnChipTagClicked` — gắn vào `then` của `AddChild` (thêm ChipRow vào
   VB_ChipTagArea, KHÔNG phải AddChild thêm ChipTag vào HorizontalBox_ChipRow)
   VÀ nhánh False của `Map_Find(FolderTree, SelectedPath)` (case leaf) — merge
   2 dây exec vào 1 node gọi.
3. Trong `OnTreeNodeClicked` — SAU `FilterByFolderPath`, ở CẢ 2 nhánh
   (IndentLevel==0 true/false). ⚠ KHÔNG gọi trong `PopulateTreeColumn` —
   PopulateTreeColumn chạy TRƯỚC khi CurrentFolderPath kịp set bởi
   FilterByFolderPath, gây bug "All sáng lần đầu, đổi category không sáng gì,
   click lại All thì TẤT CẢ category khác sáng lên" (do StartsWith với chuỗi
   rỗng trả True cho mọi chuỗi khi CurrentFolderPath chưa set).

### Pagination — Fix Bug-Pagination (D.T9)

```
CŨ:  LENGTH(AllFilteredFurnitureRows) ●→ ÷.A (Int) | PageSize ●→ ÷.B (Int) → Ceil
MỚI: LENGTH ●→ Int to Float ●→ ÷.A (Float) | PageSize ●→ ÷.B → Ceil
```
Áp dụng ở CẢ 2 nhánh Material và Furniture (cấu trúc bị copy giống nhau).
Lỗi: Int Divide rồi Ceil → mất phần dư → TotalPages thấp hơn thực tế 1 đơn vị.

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
- Recent/Favorite: SET FilteredItems + CurrentPage=0 + DisplayPage (không AddItem trực tiếp) — pagination đúng

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
- TotalPages = (Length + PageSize - 1) / PageSize — integer thuần, KHÔNG Ceil(float)
- Root Canvas = Not Hit-Testable (Self Only) — không block WBP_MeshControls
- Bind PHẢI ở Event Construct — đặt trong handler thì handler không fire sẽ không bao giờ bind (dispatcher bug)

### Resize Window (v2.3)
- Slot as Canvas Slot Get Size = (0,0) nếu chưa Set Size explicit → Set Size(512,1024) ở Construct
- Drag + Resize cùng hệ tọa độ Slot as Canvas Slot — lẫn lộn → window nhảy
- Resize button 6px → OnReleased fire khi rời button → dùng Is Mouse Button Down trong ResizeWindow
- False branch trong Sequence để trống — SET lại sẽ overwrite Then trước
- Tên đúng: "Slot as Canvas Slot" (KHÔNG "Slot as Canvas Panel Slot")

### Drag & Drop — Surface Snap
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
| 2.2 | 25/05/2026 | Fix DisplayPage integer math; root Not Hit-Testable; Resize Window 8 hướng |
| 2.3 | 08/06/2026 — 11:24 ICT | OpenMaterialModeForActor + EnsureExpanded; WBP_FurnitureCard v1.4 F_ExecuteReplace multi (thay single v1.3); Replace mode navigate (FilterByFolderPathWithUI, CreateChipTagsForPath) |
| 2.4 | 10/06/2026 — 20:34 ICT | **Refactor dispatcher.** Event Construct Then 4: bind `OnSelectionChanged` → `OnSelectionChangedMaterial` (XÓA bind OnMeshSelected + OnMeshDeselected). Thêm `OnSelectionChangedMaterial(Actors, Primary)` → Call OnMeshSelected(Primary). OnMeshSelected (internal): replace branch SET `MeshesToReplace` (array) thay MeshToReplace (single đã xóa); material branch thêm guard IsValid(SelectedActor) với False → collapse + None + SlotIndex=-1 (thay OnMeshDeselected). XÓA handler OnMeshDeselected. EnterReplaceMode: + Call EnsureExpanded đầu hàm (fix replace lúc minimize). |
| 2.4 HỢP NHẤT | 11/06/2026 | **Merged doc** — tổng hợp v2.2 + v2.3 Resize patch + v2.3 Inventory_Card patch + notes về v2.4. File này incorporate đầy đủ v2.4 dispatcher changes. |
| 2.5 | 17/06/2026 — Sprint D.T6 | WBP_FurnitureCard section: OnListItemObjectSet → BP_FurnitureItemView; Button_InforItem → OnCardInfoClicked(CardRowName). OnCardInfoClicked handler: nhận RowName thay DA. OnMeshSelected Replace branch: Branch RowName != "" → DT lookup MeshFolderPath (fallback DAPath save cũ). |
| 2.6 | 18/06/2026 — TreeNode/Chip Highlight | Thêm `IsPathActive` (Pure function) + `UpdateFolderHighlights` (impure). 3 call sites: cuối CreateChipTagsForPath, OnChipTagClicked (2 nhánh merge), OnTreeNodeClicked sau FilterByFolderPath (cả 2 nhánh). BTN_FavoriteCategory/RecentCategory: thêm ClearChildren(VB_ChipTagArea) + Collapse TB_Breadcrumb đầu function. Fix Bug-Pagination: Int to Float trước Ceil (cả 2 nhánh Material/Furniture). |
| 2.7 | 23/06/2026 — Combo Vocabulary Functions (C3a) | Thêm `GetExistingFolders()` + `GetAllUsedTags()` — 2 hàm vocabulary cho dialog lưu combo (C3b): dedup folder paths + dedup tags lowercase từ AllComboViews_Combo. |
| 2.8 | 24/06/2026 — Save Combo Dialog flow (C3b) | Thêm 3 class var (PendingSelectedActors/PendingCenter/SaveComboDialogRef). Thêm 3 custom event: OpenSaveComboDialog (đóng băng selection, tạo WBP_SaveComboDialog, Set Input Mode UI Only), OnSaveComboConfirmed (gọi ComboManager.SaveComboFromSelection), OnSaveComboDialogClosed (clear buffer + trả Game+UI). Cập nhật VRAM note: +SaveComboDialogRef. |
| 2.9 | 24/06/2026 — CTV_ComboCard + LoadComboLibrary (C4) | Thêm CTV_ComboCard (TileView, Visibility=Collapsed). LoadComboLibrary cập nhật: cuối hàm Clear List Items + ForEach AddItem. Event Construct Then 5: bind OnComboLibraryChanged + gọi LoadComboLibrary. Test PASS: 19 combo hiển thị đúng. |
| 3.0 | 25/06/2026 — C5.0 Combo Folder Tree + Filter | E_InventoryMode +Combo; 3 class var C5 (CurrentComboFolderPath/ComboFolderTree/bHasUncategorized); BTN_Tab_Combo; SwitchInventoryMode +nhánh Combo (TRƯỚC Material); 6 function mới: AddFolderPathToTree, BuildComboFolderTree, PopulateComboTreeColumn, FilterComboByFolder, RefreshComboFolderUI, OnComboTreeNodeClicked. Tree PASS. Card render ⏳ đang fix. |
