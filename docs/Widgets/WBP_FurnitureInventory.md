# WBP_FurnitureInventory
**HỢP NHẤT TỪ 4 file:** v2.2 + v2.3 Resize patch + v2.3 Inventory_Card patch (08/06) → WBP_FurnitureInventory.md (11/06) + v2.4 dispatcher refactor (10/06)
**Phiên bản:** 3.26 | **Cập nhật:** 05/09/2026 — 19:40 ICT — S7.G2 Việc 2+3 as-built: `LoadAndApplyMaterial` viết lại từ K2Node export thật (reroute `ApplyLoadedMaterialToSlot` + multi-apply Hướng B), thêm 3 class var `LoadApply_Selected`/`LoadApply_AllSame`/`LoadApply_SuccessCount`. Test PASS 5/5. Đóng `Bug-MaterialPrimaryOnly`.

**Phiên bản:** 3.25 | **Cập nhật:** 10/08/2026 — C11.3 (Import combo) DONE: Custom Event mới `CB_ImportCombo` (bound `BTN_ImportCombo.OnClicked`) — quét `Exports/`, nhập ALL, `CallDelegate ComboManagerRef.OnComboLibraryChanged` (Target PHẢI là `ComboManagerRef`, không phải `self`). Test PASS 4/4. **C11 (Export/Import combo) ĐÓNG HOÀN TOÀN.**

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
| `Folder Path` | String | [MỚI xác nhận 01/08/2026, K2Node export] Copy param `FolderPath` của `FilterByFolderPathWithUI` (full path gốc, TRƯỚC khi Split ra relative) — khác `CurrentFolderPath` (đã là relative, SET trong `FilterByFolderPath`) |
| `SearchTimerHandle` | Timer Handle | Debounce search |
| `CurrentPopup` | WBP_DetailPopup | Popup đang mở |
| `AllFurnitureItems` | Array of DA_FurnitureItem | Pre-load ở Construct ⚠ Sprint D XÓA |
| `FilteredItems` | Array of DA_FurnitureItem | Kết quả filter Furniture ⚠ Sprint D thay AllFilteredFurnitureRows |
| `CurrentPage` | Integer | Trang hiện tại (0-based), dùng chung 2 mode |
| `PageSize` | Integer | = 48 |
| `bIsDragging` / `DragOffset` / `InventoryPosition` | — | Drag window |
| `bIsMinimized` / `bIsMaximized` / `MinimizedHeight` / `OriginalSize` / `OriginalPosition` | — | Window state |
| `ReplaceTarget` | E_ReplaceTarget | [MIGRATE, C9.0c, 24/07/2026] Thay `bIsReplaceMode` (Boolean) cũ — enum None/Mesh/Combo. Migration xảy ra ngoài phiên Claude Code. Pure Function mới `IsReplaceModeActive() → Boolean` = `ReplaceTarget != None` (bản riêng, song song với bản cùng tên trên `BP_FurnitureInputManager`). |
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
| `LoadApply_Selected` | Array of Actor | [S7.G2 Việc 3, 05/09/2026] Snapshot `SelectedActors` từ `BP_FurnitureInputManager` lúc `LoadAndApplyMaterial` chạy — dùng cho multi-apply Hướng B |
| `LoadApply_AllSame` | Boolean, default true | [S7.G2 Việc 3, 05/09/2026] True nếu mọi actor trong `LoadApply_Selected` cùng `RowName` với `TargetFurnitureActor` |
| `LoadApply_SuccessCount` | Integer, default 0 | [S7.G2 Việc 3, 05/09/2026] Đếm actor phụ apply thành công (không tính Primary) — dùng build Toast |
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
| **— C5.2 Inline Rename —** | | |
| `RenameTargetNode` | WBP_TreeNode | Node đang được rename — SET None ở Event Destruct |
| `RenameTargetChip` | WBP_ChipTag | v3.8, C5.7b — Fallback target khi `OnRequestRenameFolder` không tìm thấy TreeNode khớp. Reset None đầu function, giống `RenameTargetNode`. |
| `NewFullPrefix` | String | Prefix mới sau rename: `ParentPath/NewName` hoặc `NewName` nếu root |
| `LibraryMenuRef` | WBP_LibraryContextMenu | Ref menu đang mở — SET None ở Event Destruct |
| **— C5.4 Move Folder —** | | |
| `MovingFolderPath` | String | Path folder đang được move — lưu để loại khỏi danh sách đích trong `BuildFolderTreeRecursive` (v3.9, trước là CollectFolderTargets) |
| **— C5.5 Move Combo —** | | |
| `MoveComboDialogRef` | WBP_MoveToFolderDialog | Ref dialog đang mở — SET None ở Event Destruct + HandleMoveComboConfirmed |
| `MovingComboID` | String | ComboID đang được move, lưu khi mở dialog |
| `MovingComboCurrentFolder` | String | FolderPath hiện tại của combo đang move — guard no-op nếu đã ở đúng folder |
| **— C5.6 Xóa Folder —** | | |
| `PendingDeleteFolderPath` | String | Path folder chờ xác nhận xóa — SET khi mở WBP_ConfirmDialog, đọc trong HandleDeleteFolderConfirmed, clear cuối hàm |
| **— C5.8 Wire Save —** | | |
| `SaveDlg_NewFolderPath` | String | Path folder rỗng mới tạo qua `BTN_AddFolder` — SET trong `HandleSaveDialogCreateFolder`, dùng để ExpandToPath + BeginRenameOnPath |
| **— G4 Combo Thumbnail —** | | |
| `ComboManagerRef` | BP_ComboManager | Set 1 lần ở Event Construct, clear ở Event Destruct (R4). Dùng làm Target cho `GetComboThumbnail` trong `LoadComboLibrary` (KHÔNG dùng self — self là Widget, không phải BP_ComboManager). |
| **— Delete Combo (MỚI, 22/07/2026) —** | | |
| `PendingDeleteComboID` | String | ComboID chờ xác nhận xóa — SET khi mở WBP_ConfirmDialog, đọc trong HandleDeleteComboConfirmed, clear cuối hàm. Cùng pattern `PendingDeleteFolderPath` (plain name). |

⚠️ **VRAM leak:** TargetFurnitureActor + PendingRestoredActor + SaveComboDialogRef + RenameTargetNode + LibraryMenuRef + MoveComboDialogRef + ComboManagerRef là hard ref → SET None ở Event Destruct.

---

## ShowToastMsg(Message : Text) — Function (MỚI, K1, 23/07/2026)

Helper dùng chung cho mọi chỗ trong widget này cần báo lỗi/kết quả cho user — thay dần các
`Print String` tạm trước đây. Toast thật render qua `WBP_Toast` (xem `Widgets/WBP_Toast.md`),
truy cập qua `Foff_GameInstance.ToastRef` (global, set 1 lần ở `WBP_FOFF_ToolDemo` Event
Construct).
```
Function ShowToastMsg(Message : Text)
▶→ Get Game Instance → Cast to Foff_GameInstance ●→ SET Local GI
▶→ IsValid(GI.ToastRef)
     True  ▶→ GI.ToastRef → ShowToast(Message, Duration=2.5)
     False ▶→ Print String(Message)   ← fallback (ToastRef chưa set, vd widget nào đó tạo sớm bất thường)
```
5 call site đổi từ `Print String` sang `ShowToastMsg` trong phiên K1 (23/07/2026):
`CreateNewFolderFlow`, `HandleDeleteFolderConfirmed`, `HandleMoveComboConfirmed`,
`HandleDeleteComboConfirmed` (×2 nhánh). Test 5/5 case PASS — xem `Blueprints/BP_ComboManager.md`
mục K1 cho chỗ thứ 6 (gọi thẳng `GameInstance.ToastRef.ShowToast`, không qua `ShowToastMsg`, vì
`BP_ComboManager` là Actor không có đường gọi Function riêng của Widget này).

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

### LoadAndApplyMaterial — v1.2 (Custom Event, async) — AS-BUILT 05/09/2026 (S7.G2 Việc 2 + Việc 3)

> As-built từ K2Node export thật + test PASS 5/5 (05/09/2026). Thay bản v1.1 cũ (3 node
> CreateDMI/SetMaterial/SetArrayElem(MaterialOverrides)) — nay đi qua service
> `ApplyLoadedMaterialToSlot` ghi `MaterialSlots` (Việc 2, reroute) + multi-apply Hướng B (Việc 3).
> Ký hiệu: `▶→` exec, `●→` data.

**Đầu event — Load + Cast:**
```
Event LoadAndApplyMaterial
▶→ Async Load Asset(Asset = Conv_SoftObjPathToSoftObjRef(MakeSoftObjectPath(PendingMaterialPath)))
   Completed ▶→ Cast To MaterialInterface(Object = LoadAsset.Object)
                 then ▶→ Branch(IsValid(AsMaterialInterface))
                        True ▶→ Branch(IsValid(TargetFurnitureActor))
                               True ▶→ [Primary apply — xem dưới]
                               False ▶→ [dead-end — actor không hợp lệ]
                        False ▶→ [dead-end — MI load fail]
                 CastFailed → [không nối — dead-end]
```
2 Branch IsValid liên tiếp trước khi chạm actor = đúng L1 — cả 2 nhánh False dead-end hợp lệ vì
đây là Custom Event chain thật, không có tác vụ nào bị bỏ lỡ khi input không hợp lệ.

**Primary apply + khởi tạo Việc 3:**
```
ApplyLoadedMaterialToSlot(
    Mesh      = TargetFurnitureActor.FurnitureMesh,
    Records   = TargetFurnitureActor.MaterialSlots,      [ref — tái dùng ở SerializeSlotRecords cuối]
    SlotName  = SelectedSlotName,
    HintIndex = SelectedSlotIndex,
    LoadedMI  = AsMaterialInterface,                       [từ Cast — không load lại]
    RowName   = Conv_NameToString(PendingRowName),
    PathFallback = "" )
▶→ SET LoadApply_AllSame = true
▶→ SET LoadApply_SuccessCount = 0
▶→ Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → GET SelectedActors
   ●→ SET LoadApply_Selected
▶→ Branch(Array_Length(LoadApply_Selected) > 1)
     False ▶→ [thẳng tới SerializeSlotRecords, KHÔNG qua Toast nào]
     True  ▶→ [Vòng 1 — kiểm cùng RowName]
```

**Vòng 1 — kiểm cùng RowName:**
```
ForEachLoop(LoadApply_Selected → A):
  Cast A → BP_FurnitureActor
    then       ▶→ Branch(CastedA.RowName != TargetFurnitureActor.RowName)
                    True  ▶→ SET LoadApply_AllSame = false   [dead-end]
                    False ▶→ [dead-end — cùng RowName, không làm gì]
    CastFailed ▶→ SET LoadApply_AllSame = false               [dead-end]
Completed ▶→ Branch(LoadApply_AllSame)
```
> **Lệch so với spec `DELTA_S7G2_Viec3_MultiApply_HuongB_04sep2026`:** spec yêu cầu dùng pin
> `bSuccess` (bool) + Branch để tránh rẽ exec qua `CastFailed`. As-built thật nối thẳng
> `CastFailed` → SET AllSame=false, không dùng `bSuccess`. Hai cách tương đương về hành vi (actor
> cast fail → coi là khác loại). Dead-end của `CastFailed` nằm trong thân ForEach nên vẫn hợp lệ
> theo L2 (không phải Event chain trực tiếp). Chấp nhận as-built, không sửa lại.

**Vòng 2 — apply cho actor phụ + 2 nhánh Toast:**
```
Branch(LoadApply_AllSame)
  True ▶→ ForEachLoop(LoadApply_Selected → A2):
            Branch(A2 != TargetFurnitureActor)
              True  ▶→ Cast A2 → BP_FurnitureActor
                       then ▶→ ApplyLoadedMaterialToSlot(
                                  Mesh = CastedA2.FurnitureMesh,
                                  Records = CastedA2.MaterialSlots,
                                  SlotName = SelectedSlotName,
                                  HintIndex = SelectedSlotIndex,
                                  LoadedMI = AsMaterialInterface,      [MI Primary tái dùng]
                                  RowName = Conv_NameToString(PendingRowName),
                                  PathFallback = "" ) ●→ bOK
                              → Branch(bOK)
                                  True  ▶→ SET LoadApply_SuccessCount += 1   [dead-end]
                                  False ▶→ [dead-end — actor thiếu slot]
                       CastFailed ▶→ [không nối — dead-end, bỏ qua actor]
              False ▶→ [dead-end — chính Primary]
          Completed ▶→ ShowToastMsg(Conv_StringToText(
                          "Áp cho " + ToString(LoadApply_SuccessCount + 1)
                          + "/" + ToString(LoadApply_Selected.Length) + " đồ"))
                        ▶→ [SerializeSlotRecords]
  False ▶→ ShowToastMsg(Conv_StringToText(
              "Chỉ áp cho món đang chọn — " + ToString(LoadApply_Selected.Length - 1)
              + " món khác loại chưa đổi"))
           ▶→ [SerializeSlotRecords]
```

**Điểm hội tụ — SerializeSlotRecords (đuôi cũ giữ nguyên):**

3 nguồn đổ vào cùng 1 điểm exec (`Branch(Length>1).False`, `ShowToastMsg thành công.then`,
`ShowToastMsg cảnh báo.then`):
```
▶→ SerializeSlotRecords(Records = TargetFurnitureActor.MaterialSlots)   [Primary's records — không đổi]
▶→ PrintString(Dev, "SerializeSlotRecords(...): " + Result)
▶→ GetDataTableRow(DT_MaterialInstancesCatalog, PendingRowName)
   Row Found ▶→ Cast → WBP_SlotSwatch → UpdateThumbnail(NewThumbnail = Row.ThumbnailMI)
▶→ ClearAndInvalidateTimerHandle(ApplyMaterialTimerHandle)
▶→ SetTimer("CaptureMaterialSnapshot", 0.5s) → SET ApplyMaterialTimerHandle
▶→ GetAllActorsOfClass(BP_FurnitureUserPrefsManager) → Get(0) → AddRecentMaterial(PendingRowName)
```

Test PASS 5/5 (05/09/2026): multi cùng RowName (2 gối giống hệt) → cả 2 đổi + Toast "N/N đồ";
trộn RowName (combo dị loại) → chỉ Primary đổi + Toast cảnh báo; single actor → hành vi như cũ,
không Toast; Undo sau case multi cùng loại → khôi phục đúng; Undo sau case trộn loại → khôi phục
đúng. Đóng `Bug-MaterialPrimaryOnly` (xem `Bugs/Open_Bugs.md`).

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

### OnMeshSelected(SelectedActor) — handler nội bộ — SỬA (Save As/Save đè T2, node-verified K2Node 03/08/2026)
> ⚠️ Custom event nội bộ của inventory — KHÁC dispatcher `OnMeshSelected` đã XÓA ở InputManager. Nay được trigger qua `OnSelectionChangedMaterial`.

**Nhánh REPLACE (SỬA 03/08/2026 — T2, đóng `Bug-ReplaceInCombo-TabJump`; thay nguồn dữ liệu route,
GIỮ NGUYÊN 2 node đích `StartReplaceComboMode`/`StartReplaceMode` và mọi node sau chúng — KP3):**
```
Branch
  Condition ●← IsReplaceModeActive()
  T →
    Branch(IsValid(SelectedActor))            ← ★ MỚI 02/08 (P2 bug-fix) — chặn Broadcast
                                                  deselect rỗng (Primary=None) từ DeselectAll()
                                                  (bước đệm bắt buộc trước SelectActors — xem
                                                  BP_FurnitureInputManager.md §SelectActors)
      False → [dead-end — không làm gì]
      True →
        Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → InputManagerRef
        → InputManagerRef.ShouldRouteReplaceToCombo(SelectedActor)     ← ★ SỬA 03/08 (T2) — thay
             ●→ bRouteToCombo, ComboID, RootGroupID                       ResolveSelectedComboRoot()
                                                                            cũ (mù edit-scope)
        → Branch(bRouteToCombo)
             True (là COMBO) →
               InputManagerRef.StartReplaceComboMode(RootGroupID, ComboID)
               ← gọi LUÔN, không guard `!= Combo`: hàm vừa route Mesh→Combo, vừa refresh đúng
                 combo mới khi đã ở Combo rồi mà đổi cụm khác (xử luôn dead-end kiểu cũ)
               [dead-end, xong]
             False (là MESH) →
               Branch(ReplaceTarget != E_ReplaceTarget::Mesh)   ← đọc ReplaceTarget của
                                                                    BP_FurnitureInputManager — xem
                                                                    cảnh báo Aliasing dưới
                 True  → InputManagerRef.StartReplaceMode(InputManagerRef.SelectedActors)
                         [dead-end, xong]
                 False → [ĐƯỜNG XỬ MESH CŨ — giữ nguyên từ trước P2]
                         SET MeshesToReplace = InputManagerRef.SelectedActors     ← v2.4: array
                         Branch IsValid(SelectedActor):
                           T →
                             SetVisibility(CTV_FurnitureCard, Visible)     ← ★ MỚI 02/08 (P1.3)
                             SetVisibility(CTV_ComboCard, Collapsed)       ← ★ MỚI 02/08 (P1.3)
                             ← v2.5 Sprint D.T6: Branch RowName thay DAPath→Load
                             Cast SelectedActor → GET RowName
                             Branch(RowName != ""):
                               True:
                                 Get Data Table Row(DT_FurnitureCatalog, RowName) → Row Found → GET MeshFolderPath
                                 → Branch MeshFolderPath != "" → FilterByFolderPathWithUI(MeshFolderPath)
                               False (save cũ RowName rỗng — fallback DAPath):
                                 Cast → GET DAPath → Load Asset Blocking → Cast DA_FurnitureItem → GET MeshFolderPath
                                 → Branch MeshFolderPath != "" → FilterByFolderPathWithUI(MeshFolderPath)
                           F → [dead-end, không đổi — nằm ngoài scope P1-P4]
  F → (tiếp tục nhánh material, không đổi)
```
> **[SUPERSEDED 02/08]** Guard `Branch(ReplaceTarget==Mesh)` (Bug A2, 30/07/2026) — bản cũ chỉ
> "bỏ qua, không nhảy tree" khi đang Combo replace mà chọn nhầm actor thuộc mesh. Nay thay hẳn
> bằng `ResolveSelectedComboRoot()` + route 2 chiều Mesh↔Combo (P2, xem `Plans/01-08-2026_
> ReplaceUX_Fix_Execution_Plan.md`) — vá đúng gốc (bug #4) thay vì chỉ chặn triệu chứng. Ghi chú
> lịch sử (không xóa): xem `DEVIATIONS.md` mục "C9 Replace — 30/07/2026" cho bối cảnh Bug A2 gốc,
> mục "Replace UX Fix P0→P5 — 02/08/2026" cho root cách thật của bug #4 (2 giả thuyết bị bác bỏ
> trước khi tìm ra: guard `IsValid(SelectedActor)` thiếu, không phải doc-drift hay thứ tự node).
>
> **[SUPERSEDED 03/08]** `ResolveSelectedComboRoot()` (P2, dòng trên) tự nó **mù edit-scope** —
> route sai khi đang edit trong combo (bug `Bug-ReplaceInCombo-TabJump`, xem `Bugs/Open_Bugs.md`).
> T2 (Save As/Save đè) thay bằng `InputManagerRef.ShouldRouteReplaceToCombo(SelectedActor)` —
> đọc `GetCurrentEditScope()` TRƯỚC, đang edit thì ép route MESH bất kể actor thuộc combo hay
> không. `ResolveSelectedComboRoot()` KHÔNG bị sửa, vẫn dùng ở call site khác (C9) — xem
> `Blueprints/BP_FurnitureInputManager.md` mục `ShouldRouteReplaceToCombo`.

> ⚠️ **Aliasing — biến `ReplaceTarget` tồn tại 2 bản riêng biệt, TRÙNG TÊN (xác nhận 02/08 bằng
> MemberGuid qua K2Node export, không suy đoán):**
> - `BP_FurnitureInputManager.ReplaceTarget` — SET bởi `StartReplaceMode`/`StartReplaceComboMode`,
>   dòng đầu hàm. Bản `OnMeshSelected` (trên) đọc để route Mesh/Combo.
> - `WBP_FurnitureInventory.ReplaceTarget` (chính class này) — SET bởi `EnterReplaceMode`, là
>   biến mà card (`WBP_FurnitureCard`/`WBP_ComboCard`) đọc để gate `BTN_ChangeMesh`/`BTN_ChangeCombo`.
> 2 biến này KHÔNG tự đồng bộ — `EnterReplaceMode`/`StartReplaceComboMode` phải chạy tới nơi thì
> bản Inventory mới SET đúng. Đọc nhầm bản khi sửa code là bẫy dễ gặp nhất trong cả 4 hàm liên
> quan tới Replace (`OnMeshSelected`, `OnSceneRestored`, `BTN_Close` — cả 3 dưới đây — và
> `WBP_ComboCard.OnListItemObjectSet`, xem file đó).

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

### EnterReplaceMode — v1.3 + v2.4 + C9.0c (24/07/2026) + bổ sung state 30/07/2026
```
Call EnsureExpanded (Target=self)   ← v2.4: bung inventory nếu đang minimize (fix replace lúc minimize không bung)
SET ReplaceTarget = E_ReplaceTarget::Mesh   ← [MIGRATE, C9.0c] trước là SET bIsReplaceMode = True
Regenerate All Entries(CTV_FurnitureCard)
← Dùng khi bật Replace VÀ không cần navigate folder (BTN_Replace toggle ON)
← KHÔNG dùng từ DetailPopup (vì FilterByFolderPathWithUI sẽ clear cards sau đó)
← THÊM 30/07/2026 (FUNCTION-LEVEL, chưa re-export node trong phiên này):
SET CurrentInventoryMode = Furniture
SetVisibility(CTV_ComboCard, Collapsed)
SetVisibility(CTV_FurnitureCard, Visible)
UpdateTabHighlight
```
> Set cứng `Mesh` — hàm này CHỈ dùng cho đường Mesh. Combo mode (`StartReplaceComboMode`, xem
> `Blueprints/BP_FurnitureInputManager.md`) set `ReplaceTarget=Combo` trực tiếp trên inventory
> ref, không đi qua `EnterReplaceMode`. 4 dòng thêm 30/07 đảm bảo tab/card đúng trạng thái
> Furniture khi vào Replace Mesh (trước đó dựa vào state có sẵn từ lúc mở inventory, có thể sai
> nếu user đang đứng ở tab Combo/Material lúc bấm Replace).

### ExitReplaceMode — v1.3 + C9.0c (24/07/2026)
```
SET ReplaceTarget = E_ReplaceTarget::None   ← [MIGRATE, C9.0c] trước là SET bIsReplaceMode = False
Regenerate All Entries(CTV_FurnitureCard)   ← force tất cả cards ẩn BTN_ChangeMesh
Regenerate All Entries(CTV_ComboCard)       ← [THÊM MỚI, C9.0c 24/07] đường thoát duy nhất cho cả 2 mode (Mesh/Combo)
```

### RefreshCardReplaceMode — v1.3
```
Regenerate All Entries(CTV_FurnitureCard)
← Gọi từ bên ngoài (DetailPopup) sau FilterByFolderPathWithUI populate xong
← Đảm bảo cards mới thấy ReplaceTarget đúng (Mesh) → hiện BTN_ChangeMesh
```

### RefreshComboCardReplaceMode() — Function (MỚI, C9.d, 30/07/2026)
```
▶→ Regenerate All Entries(CTV_ComboCard)
```
Bản mirror của `RefreshCardReplaceMode` cho phía Combo. Gọi từ `StartReplaceComboMode`
(`BP_FurnitureInputManager`) sau `FilterComboByFolder` — đảm bảo card combo mới thấy
`ReplaceTarget==Combo` → hiện `BTN_ChangeCombo` (xem `Widgets/WBP_ComboCard.md`).

### BTN_Close — OnClicked (EventGraph) — SỬA (Replace UX Fix P4.2+P4.4, 02/08/2026)
```
On Clicked (BTN_Close)
▶→ Get All Actors Of Class(BP_FurnitureInputManager) → Get(0)
▶→ SET InputManagerRef.ReplaceTarget = E_ReplaceTarget::None
▶→ Clear Array(InputManagerRef.MeshesToReplace)
▶→ SET InputManagerRef.ComboRootGroupIDToReplace = ""      ← ★ MỚI 02/08 (P4.2) — 1 trong 3 biến
                                                                bắt buộc clear ở mọi đường thoát
▶→ ExitReplaceMode (self)
▶→ SetVisibility(self, Collapsed)
▶→ Cast(GetPlayerController → BP_FoffPlayerController)
▶→ RemoveFurnitureInput()

← ĐÃ XÓA 02/08 (P4.4): `SET InputManagerRef.MeshToReplace = None` — biến `MeshToReplace`
  (single) bị xóa hoàn toàn khỏi `BP_FurnitureInputManager`, đây là chỗ SET rác cuối cùng còn
  sót. Xem `Blueprints/BP_FurnitureInputManager.md` mục Variables (Group).
```
**Xác nhận Find References (02/08):** `ComboRootGroupIDToReplace` SET ở đúng 4 chỗ hợp lệ sau
P4.2 — `StartReplaceComboMode` (entry), `ExecuteComboReplace` (re-resolve, ×2, có từ C9),
`CB_Replace`/`Event Tick`/`OnLMBReleased` (đã có từ trước, set `""` khi deselect), và `BTN_Close`
(mới thêm ở đây). `OnSceneRestored` clear qua đường riêng (xem mục trên).

### OnSceneRestored(RestoredSelectedActor) — v1.1 + SỬA (Replace UX Fix P4.3, 02/08/2026)
```
← Bound từ UndoManagerRef.OnRestoreCompleted
Branch CurrentInventoryMode == Material:
  T → SET PendingRestoredActor = RestoredSelectedActor
      SetTimerByFunctionName("ApplyRestoredActor", 0.1s)
      ← delay cho LeftMouseButton DeselectMesh chạy xong trước (race condition)

Branch(IsReplaceModeActive())            ← ★ MỚI 02/08 (P4.3) — nhánh SONG SONG với nhánh
                                             Material trên, KHÔNG lồng vào nhau
  T →
    Clear InputManagerRef.MeshesToReplace
    SET InputManagerRef.ComboRootGroupIDToReplace = ""
    ExitReplaceMode()
    ← ExitReplaceMode tự SET ReplaceTarget=None + Regenerate 2 CTV, không cần lặp lại tay
  F → [dead-end]
```
**Quyết định UX (a), chốt 02/08/2026:** Undo giữa Replace luôn **thoát Replace hẳn**, không giữ
mode + refresh theo actor restore. Lý do: undo thuộc lịch sử scene, actor được restore có thể
không còn liên quan gì tới target đang định thay — giữ mode dễ tạo trạng thái UI lệch scene thật
(kiểu aliasing dự án hay gặp). Xem `DEVIATIONS.md` mục "Replace UX Fix P0→P5 — 02/08/2026".

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

## T3 — Save As/Save Đè — 2 Function mới (Sự thật vs Chính sách)

⚠ [Nguồn: `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 7b.2/7b.3, ✓K2/✓ as-built theo
7c — hạ tầng dựng TRƯỚC phiên T3 07/08/2026, lần đầu phân phối vào file canonical này qua đợt
merge 07/08/2026. Đặt cạnh `GetExistingFolders`/`GetAllUsedTags` (cùng họ hàm đọc
`AllComboViews_Combo`).]

Tách đôi theo nguyên tắc T1 (`BP_FurnitureInputManager.ResolveActiveComboForSave`): **sự thật**
tách khỏi **chính sách**.
```
GetComboViewByID        → SỰ THẬT    "combo này còn trong thư viện không, metadata là gì"
BuildSaveDialogPrefill  → CHÍNH SÁCH "thế thì có cho ghi đè không, điền sẵn gì"
```

### GetComboViewByID(ComboID : String) → (View : BP_ComboItemView, bFound : Bool)
**Local:** `Found_View` (BP_ComboItemView) · `Found_bOK` (Bool)
```
Entry ▶→ SET Found_bOK = false
      ▶→ ForEachLoopWithBreak(AllComboViews_Combo)
           Loop Body ▶→ Branch(Element.ComboID == ComboID)
                          True  ▶→ SET Found_View = Element
                                 ▶→ SET Found_bOK = true
                                 ▶→ Break
                          False ▶→ (trống)
           Completed ▶→ Return(Found_View, Found_bOK)
```
> Pattern y hệt đoạn loop inline sẵn có trong `CB_MoveCombo` — không phải node lạ. KHÔNG
> refactor `CB_MoveCombo` để gọi hàm này (KP3).

### BuildSaveDialogPrefill(ComboID : String, bCanOverwrite : Bool, ReasonIn : String) → (PrefillName, PrefillFolder, PrefillDesc, PrefillTagsText : String, bOverwriteAllowed : Bool, ReasonOut : String)
**Local:** `Pre_Name` · `Pre_Folder` · `Pre_Desc` · `Pre_TagsText` · `Pre_Reason` (String) ·
`Pre_bAllow` (Bool) · `Pre_View` (BP_ComboItemView) · `Pre_bFound` (Bool)
```
Entry ▶→ SET Pre_Name = "" · Pre_Folder = "" · Pre_Desc = "" · Pre_TagsText = ""
      ▶→ SET Pre_bAllow = false · SET Pre_Reason = ReasonIn        ← default TRƯỚC mọi Branch
      ▶→ Branch(bCanOverwrite)
           False ▶→ (trống — giữ default; lý do đã là ReasonIn nguyên văn)
           True  ▶→ GetComboViewByID(ComboID) ─→ Pre_View, Pre_bFound
                 ▶→ Branch(Pre_bFound)
                      False ▶→ SET Pre_Reason =
                               "Combo gốc không còn trong thư viện — chỉ lưu được thành combo mới"
                      True  ▶→ SET Pre_bAllow = true
                             ▶→ SET Pre_Reason = ""
                             ▶→ SET Pre_Name     = Pre_View.ComboName
                             ▶→ SET Pre_Folder   = Pre_View.FolderPath
                             ▶→ SET Pre_Desc     = Pre_View.Description
                             ▶→ Join(Pre_View.Tags, ", ") ─→ SET Pre_TagsText
      (merge) ▶→ Return(Pre_Name, Pre_Folder, Pre_Desc, Pre_TagsText, Pre_bAllow, Pre_Reason)
```
> Lý do viết ở đây, không đẩy về `BP_FurnitureInputManager`: "combo còn trong thư viện không"
> thuộc miền dữ liệu của widget (`AllComboViews_Combo`); InputManager không biết gì về thư viện.

`BP_ComboItemView.Description : String` — field mới (Lô A, ⚠ cùng nguồn 7c như trên).

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

### LoadComboLibrary — mở rộng (G4, trong ForEach, sau build BP_ComboItemView)
```
Branch(IsValid(ComboManagerRef)):
  True  → GetComboThumbnail(Target=ComboManagerRef, ComboID=view.ComboID) → SET view.Thumbnail
  False → vẫn Array_Add(AllComboViews_Combo, view), bỏ qua bước SET Thumbnail
          ✅ FIXED 15/07/2026 (trước đó dead-end, xem DEVIATIONS 15/07/2026)
```

**Test PASS (24/06/2026):** 19 combo hiện đúng tên + badge ×N món.

### Event Construct (cập nhật C4 — thêm vào Sequence)
```
Then 5: Bind OnComboLibraryChanged → LoadComboLibrary
        LoadComboLibrary  ← gọi ngay lần đầu để populate CTV khi mở inventory
```

### Event Construct (cập nhật G4 — thêm vào Sequence)
```
Then 6: Get All Actors Of Class(BP_ComboManager) → Get(0) → SET ComboManagerRef
```

### Event Destruct (cập nhật G4 — thêm)
```
SET ComboManagerRef = None
```

---

## C3b — Save Combo Dialog Flow

### OpenSaveComboDialog(SelectedActors : Array BP_FurnitureActor, Center : Vector, ActiveComboID : String, bCanOverwrite : Bool, ReasonText : String) — Custom Event
⚠ **Chữ ký mở rộng +3 param** (`ActiveComboID`/`bCanOverwrite`/`ReasonText`) — [Nguồn:
`Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 7b.3, ✓ as-built theo 7c, hạ tầng dựng
TRƯỚC phiên T3, lần đầu phân phối vào file canonical này 07/08/2026]. 3 param nhận từ
`ResolveActiveComboForSave()` (`BP_FurnitureInputManager`) tại call site `CB_SaveCombo_Handler`
— **việc chèn `ResolveActiveComboForSave()` vào `CB_SaveCombo_Handler` CHƯA được phân phối vào
`BP_FurnitureInputManager.md`**, xem cảnh báo cuối file (báo cáo merge 07/08/2026).
```
SET PendingSelectedActors = SelectedActors
SET PendingCenter = Center
GetAllUsedTags() → TempTags
▶→ BuildSaveDialogPrefill(ActiveComboID, bCanOverwrite, ReasonText)
     ─→ PrefillName, PrefillFolder, PrefillDesc, PrefillTagsText, bOverwriteAllowed(=Pre_bAllow), ReasonOut
▶→ Create Widget(WBP_SaveComboDialog,
       TagVocabulary       = TempTags,
       bOverwriteAllowed   = Pre_bAllow,
       OverwriteComboID    = ActiveComboID,
       OverwriteName       = PrefillName,
       DisabledReason      = ReasonOut,
       PrefillName         = PrefillName,
       PrefillFolder       = PrefillFolder,
       PrefillDesc         = PrefillDesc,
       PrefillTagsText     = PrefillTagsText) → SET SaveComboDialogRef
Branch(IsValid(SaveComboDialogRef))
  True →
    BuildComboFolderTree()
    BuildComboFolderTreeNodes("") → Entries
    SaveComboDialogRef.Picker.SetFolders(Entries)
    SaveComboDialogRef.Picker.ExpandToPath(PrefillFolder)
    SET SaveComboDialogRef.Picker.SelectedPath = PrefillFolder    ← MỚI 07/08/2026 (T3, Việc 5)
    SaveComboDialogRef.Picker.RefreshVisibleRows()                ← MỚI 07/08/2026 (T3, Việc 5)
    SET SaveComboDialogRef.Picker.bShowCurrentTag = False
    Bind SaveComboDialogRef.OnRequestCreateFolder → HandleSaveDialogCreateFolder
    Bind SaveComboDialogRef.Picker.OnRequestCommitRename → HandleSavePickerRenameCommitted
  False → dead-end (guard có sẵn từ trước C5.8, không phải patch mới)
Add to Viewport(SaveComboDialogRef, ZOrder=99)
Bind OnDialogConfirmed(SaveComboDialogRef) → OnSaveComboConfirmed
Bind OnDialogConfirmedOverwrite(SaveComboDialogRef) → HandleSaveComboOverwriteConfirmed   ← MỚI 07/08/2026 (T4)
Bind OnDialogCancelled(SaveComboDialogRef) → OnSaveComboDialogClosed
Get Player Controller → Set Input Mode UI Only(InWidgetToFocus=SaveComboDialogRef)
```
> **13/07 (C5.8 Wire Save):** xoá dòng cũ `GetExistingFolders() → SET TempFolders` (đã orphan sau khi pin `ExistingFolders` bị xoá khỏi `WBP_SaveComboDialog` Expose on Spawn) + bỏ arg `ExistingFolders=TempFolders` khỏi `Create Widget`. Thêm Branch wire `Picker`/bind 2 dispatcher mới của dialog, chèn NGAY SAU `SET SaveComboDialogRef`, TRƯỚC `AddToViewport`.
> **✓TEST 07/08/2026 (T3, Việc 5 — MỚI, ground truth của đợt merge này):** `Picker.ExpandToPath`
> (định nghĩa `WBP_FolderTreePicker.md`) chỉ ghi `ExpandedFolders` (mở cây), KHÔNG tự set
> `SelectedPath` — thiết kế cố ý vì hàm dùng chung với `WBP_MoveToFolderDialog` (Move không được
> tự chọn sẵn đích). Save cần chọn sẵn combo gốc nên phải `SET Picker.SelectedPath` + gọi
> `RefreshVisibleRows()` thêm ở đây, ngay sau `ExpandToPath`.

### HandleSaveDialogCreateFolder(ParentPath : String) — Custom Event MỚI (13/07, C5.8 Wire Save)
Bound từ `SaveComboDialogRef.OnRequestCreateFolder` trong `OpenSaveComboDialog`.
```
GetUniqueNewFolderName(ParentPath) → NewName
Select(String)(Pick=ParentPath=="", A=NewName, B=Concat(ParentPath,"/",NewName)) → SET SaveDlg_NewFolderPath
CreateEmptyFolder(SaveDlg_NewFolderPath) → bOK
Branch(bOK)
  False → Print "CreateEmptyFolder failed: "+SaveDlg_NewFolderPath [DevelopmentOnly]
  True  →
    BuildComboFolderTree() → BuildComboFolderTreeNodes("") → Entries
    Branch(IsValid(SaveComboDialogRef))
      True →
        Picker.SetFolders(Entries)
        Picker.ExpandToPath(SaveDlg_NewFolderPath)
        Picker.RefreshVisibleRows()
        GetSiblingFolderNames(SaveDlg_NewFolderPath) → Siblings
        Picker.BeginRenameOnPath(SaveDlg_NewFolderPath, Siblings)
      False → dead-end
```
Var mới: `SaveDlg_NewFolderPath : String` (class var, prefix `SaveDlg_`).

### HandleSavePickerRenameCommitted(OldPath, NewName) — Custom Event MỚI (13/07, C5.8 Wire Save)
Bound từ `SaveComboDialogRef.Picker.OnRequestCommitRename` trong `OpenSaveComboDialog`.
```
ParentOf(OldPath) → ParentPath
Select(String) hoặc Branch(ParentPath=="") → NewFullPath
RenameFolderPrefix(OldPath, NewFullPath) → (Return Value KHÔNG dùng để gate — xem ghi chú)
BuildComboFolderTree() → BuildComboFolderTreeNodes("") → Entries
Branch(IsValid(SaveComboDialogRef))
  True →
    Picker.SetFolders(Entries)
    Picker.ExpandToPath(NewFullPath)
    SET Picker.SelectedPath = NewFullPath
    Picker.RefreshVisibleRows()
  False → dead-end
```
> **Ghi chú quan trọng — KHÔNG Branch theo `RenameFolderPrefix` Return Value (Integer, đếm combo bị đổi):**
> Verify code C++ thật (`ComboSerializer::RenameFolderPrefix`, có nhánh C5.3 cascade sang `Folders.json` manifest ĐỘC LẬP với count combo) — `Count=0` (rename folder rỗng) vẫn cập nhật registry đúng qua nhánh cascade. Gate theo `Count>0` sẽ sai (báo fail nhầm cho case phổ biến nhất — rename ngay sau khi tạo folder rỗng). Chạy thẳng không Branch, đúng spec gốc Wire_ExecutionPlan.
> Ghi chú as-built: biến `SaveDlg_RenamedPath` KHÔNG dùng — thực tế dùng `NewFullPrefix`/pattern tương tự `HandleMoveFolderConfirmed` cũ (xem export K2Node thật nếu cần chính xác tuyệt đối tên biến — Sonnet ghi theo mô tả logic đã verify qua screenshot, không phải export đầy đủ 100% cho hàm này).

### Test PASS (13/07, C5.8 Wire Save): S6a, S6c, M1-M6, Phần 2 test 1-2

### OnSaveComboConfirmed(ComboName, FolderPath, Description : String; Tags : Array String) — Custom Event
```
← Bound từ SaveComboDialogRef.OnDialogConfirmed
Get All Actors Of Class(BP_ComboManager) → Get(0) → Cast → ComboManagerRef
IsValid(ComboManagerRef):
  True → SaveComboFromSelection(PendingSelectedActors, PendingCenter, ComboName, Description, FolderPath, Tags)
  False → Print String "OnSaveComboConfirmed: ComboManager not found"
OnSaveComboDialogClosed    ← luôn đóng dialog, dù save fail
```

### HandleSaveComboOverwriteConfirmed(ComboID, ComboName, FolderPath, Description : String, Tags : Array String) — Custom Event MỚI (07/08/2026, T4 DONE)
**✓TEST 07/08/2026** — Bound từ `SaveComboDialogRef.OnDialogConfirmedOverwrite`.
```
▶→ ComboManagerRef.SaveComboFromSelection(
      SelectedActors = GET PendingSelectedActors, Center = GET PendingCenter,   ← ĐỌC TRƯỚC cleanup
      ComboName, Description, FolderPath, Tags,
      bOverwrite = true, OverwriteComboID = ComboID)
▶→ ShowToastMsg("Đã ghi đè combo")
▶→ Call OnSaveComboDialogClosed(self)
```
> Đọc `PendingSelectedActors`/`PendingCenter` TRƯỚC khi gọi `OnSaveComboDialogClosed` — hàm đó
> CLEAR cả 2 biến này (xem bên dưới). Dialog modal (Input Mode UI Only) → không có đường nào
> Undo/Destroy actor xen giữa lúc freeze selection và lúc confirm → an toàn (S9, xem 7d.4).
> Tái dùng đúng thứ tự dọn dẹp của `OnSaveComboConfirmed` (Save As) — KHÔNG viết cleanup riêng.

### OnSaveComboDialogClosed — Custom Event
```
← Bound từ SaveComboDialogRef.OnDialogCancelled + gọi cuối OnSaveComboConfirmed +
  HandleSaveComboOverwriteConfirmed (T4)
SET SaveComboDialogRef = None
SET PendingSelectedActors = []     (Make Array rỗng)
SET PendingCenter = (0, 0, 0)
Get Player Controller → Set Input Mode Game And UI
```

---

## C5.0 — Combo Folder Tree + Filter

> **Trạng thái 25/06/2026:** Tree 2 cấp + chip cấp 3+ đã implement (delta Round 3). Filter logic xong.
> **ĐANG FIX:** CTV_ComboCard không render card — đang thử Set List Items thay Add Item (deviation D3).

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

> **Known behavior (không phải bug, 30/06/2026):** Folder KHÔNG tồn tại độc lập —
> nó là cái bóng suy ra từ FolderPath của combo hiện có (BuildComboFolderTree quét
> AllComboViews mỗi lần). Move/xóa hết combo + folder con ra khỏi 1 folder cha →
> folder cha tự biến mất khỏi tree khi RefreshComboFolderUI build lại (không gì để
> suy ra nó tồn tại). Nhất quán với C5.6 (xóa folder cũng gây hiện tượng y hệt với
> con của nó). Persist folder rỗng độc lập = thay đổi kiến trúc lớn, ngoài scope C5.

### PopulateComboTreeColumn() — Function
Dựng WBP_TreeNode vào `VerticalBox_44` (cột tree CHUNG với furniture/material). Render 2 cấp: cấp 1 (IndentLevel=0) + cấp 2 (IndentLevel=1, chỉ khi cấp 1 đang active — D9).
```
Clear Children(VerticalBox_44)

// Node "+" — NF.G3 (06/07), LUÔN đứng ĐẦU, trước cả "Tất cả"
Create Widget(WBP_TreeNode) → PlusNode
  SET PlusNode.FolderPath = "__NEWFOLDER__"
  SET PlusNode.FolderName = "+ Tao folder"
  SET PlusNode.IndentLevel = 0
  RefreshDisplay(bIsActive = false)
  Add Child(VerticalBox_44, PlusNode)
  Bind OnNodeSelected(PlusNode) → OnComboTreeNodeClicked
  (KHÔNG bind OnNodeRightClicked — né context menu trên hàng "+")

// Node "Tất cả" (luôn có)
Create Widget(WBP_TreeNode) → AllNode
  SET AllNode.FolderPath = "__ALL__"
  SET AllNode.FolderName = "Tat ca"          ← D2: SET var trực tiếp TRƯỚC RefreshDisplay
  SET AllNode.IndentLevel = 0
  RefreshDisplay(bIsActive = (CurrentComboFolderPath == "__ALL__"))
  Add Child(VerticalBox_44, AllNode)
  Bind OnNodeSelected(AllNode) → Create Event → OnComboTreeNodeClicked(self)
  Bind OnNodeRightClicked(AllNode) → OnComboTreeNodeRightClicked   ← guard "__ALL__" ở receiver

// Node "Chưa phân loại" (nếu bHasUncategorized)
Branch(bHasUncategorized)
  True  → Create Widget(WBP_TreeNode) → UncatNode
           SET UncatNode.FolderPath = "" | FolderName = "Chua phan loai" | IndentLevel = 0
           RefreshDisplay(bIsActive = (CurrentComboFolderPath == ""))
           Add Child | Bind OnNodeSelected → OnComboTreeNodeClicked
           Bind OnNodeRightClicked(UncatNode) → OnComboTreeNodeRightClicked   ← guard "" ở receiver
  False → [dead-end]

// Cấp 1 từ Map[""] — IndentLevel = 0
Map Find(ComboFolderTree, Key="") → Lvl1CSV, bFound
Branch(bFound)
  False → [dead-end]
  True  → Parse Into Array(Lvl1CSV, ",") → Lvl1Names
           ForEach Lvl1Names (lvl1):
             Create Widget(WBP_TreeNode) → Node1
             SET Node1.FolderPath = lvl1 | FolderName = lvl1 | IndentLevel = 0
             RefreshDisplay(bIsActive = (CurrentComboFolderPath == lvl1))
             Add Child(VerticalBox_44, Node1) | Bind OnNodeSelected → OnComboTreeNodeClicked
             Bind OnNodeRightClicked(Node1) → OnComboTreeNodeRightClicked
             Bind OnNodeRenameCommitted(Node1) → OnRenameFolderCommitted
             // D9: cấp 2 CHỈ render khi lvl1 đang active — Guard trong Loop Body, KHÔNG Completed
             Branch( (CurrentComboFolderPath == lvl1) OR (CurrentComboFolderPath StartsWith (lvl1 + "/")) )
               False → [dead-end]
               True  → Map Find(ComboFolderTree, lvl1) → Lvl2CSV, bFound2
                        Branch(bFound2)
                          False → [dead-end]
                          True  → Parse Into Array(Lvl2CSV, ",") → Lvl2Names
                                   ForEach Lvl2Names (lvl2):
                                     FullPath2 = Append(lvl1, "/", lvl2)
                                     Create Widget(WBP_TreeNode) → Node2
                                     SET Node2.FolderPath = FullPath2 | FolderName = lvl2 | IndentLevel = 1
                                     RefreshDisplay(bIsActive = (CurrentComboFolderPath == FullPath2))
                                     Add Child(VerticalBox_44, Node2)
                                     Bind OnNodeSelected(Node2) → OnComboTreeNodeClicked
                                     Bind OnNodeRightClicked(Node2) → OnComboTreeNodeRightClicked
                                     Bind OnNodeRenameCommitted(Node2) → OnRenameFolderCommitted
                                   Completed: [dead-end]
           ForEach Lvl1Names Completed: [dead-end]
```
> **D9 (26/06):** Branch guard trong Loop Body — cấp 2 CHỈ hiện khi `CurrentComboFolderPath == lvl1 OR StartsWith(lvl1+"/")`. Guard PHẢI trong Loop Body (KHÔNG Completed) — bug Completed: lvl1=phần tử cuối, Branch chỉ check 1 lần sai.
> Tất cả 4 node bind thêm `OnNodeRightClicked → OnComboTreeNodeRightClicked`. Guard sentinel xử lý ở receiver.
> ⚠️ **BUG FIX 4.1 (01/07):** `ParseIntoArray` delimiter PHẢI là `","` (phẩy, không cách). `AddFolderPathToTree` viết với `","` (Map Add value = `Append(OldCSV, ",", child)`) → nếu `ParseIntoArray` đọc với `", "` (có cách sau phẩy) thì nhiều tên con bị gộp thành 1 token. Đảm bảo cả `Lvl1CSV` và `Lvl2CSV` đều dùng `","` — khớp với delimiter khi viết.
> **NF.G3 (06/07):** node "+" dùng sentinel `FolderPath = "__NEWFOLDER__"` — guard đọc ở đầu `OnComboTreeNodeClicked`. KHÔNG bind `OnNodeRightClicked` cho node này (không có context menu trên hàng "+").

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
> ✅ **FIXED (26/06):** Set List Items hoạt động đúng sau khi verify Entry Widget Class = WBP_ComboCard trong TileView settings (B-C5-card). Card render PASS.

### RefreshComboFolderUI() — Function (lớp refresh duy nhất cho C5.2→C5.7)
```
LoadComboLibrary
BuildComboFolderTree → PopulateComboTreeColumn
Branch(CurrentComboFolderPath == "__ALL__")
  True  → FilterComboByFolder("__ALL__")
  False → Branch(CurrentComboFolderPath == "")
            True  → FilterComboByFolder("")
            False → FilterComboByFolder(CurrentComboFolderPath)   ← luôn dùng path thật (BUG FIX 4.2)
[3 nhánh merge] → UpdateComboFolderHighlights()   ← BUG FIX 4.3
                → RefreshChipBreadcrumb()          ← THÊM 06/07, nối cả 3 nhánh (BUG FIX #1 mục dưới)
```
> Check `__ALL__` và `""` riêng vì 2 sentinel KHÔNG nằm trong ComboFolderTree.
> ⚠️ **BUG FIX C5.2 (27/06):** thiếu nối `PopulateComboTreeColumn` sau `BuildComboFolderTree` → tree không vẽ lại sau rename.
> ⚠️ **BUG FIX 4.2 (01/07):** Bỏ nhánh `Map_Contains(ComboFolderTree, CurrentComboFolderPath)`. Folder lá KHÔNG là key trong ComboFolderTree (key = path cha, value = CSV tên con) → `Map_Contains` trả False cho leaf → luôn nhảy về `__ALL__`. Fix: với path thật (không phải sentinel), gọi `FilterComboByFolder(CurrentComboFolderPath)` trực tiếp — `FilterComboByFolder` tự lọc đúng.
> ⚠️ **BUG FIX 4.3 (01/07):** Thêm `UpdateComboFolderHighlights()` sau merge 3 nhánh — thiếu call này → chip/tree node không sáng sau Move Combo.
> ⚠️ **BUG FIX #1 (06/07):** Bản đầu chỉ nối `RefreshChipBreadcrumb` ở nhánh path-thật (else-else) — 2 nhánh `__ALL__` và `""` dead-end sau `UpdateComboFolderHighlights`, phát hiện qua export K2Node. Đã nối cả 3 nhánh về 1 điểm chung (xem mục "Bug fix — Chip area không tự refresh" dưới).

### UpdateComboFolderHighlights() — Function (Issue 2 — v3.5)
Mirror của `UpdateFolderHighlights` cho combo side. KHÔNG dùng `IsPathActive()` (function đó đọc `CurrentFolderPath` của furniture side) — inline check trực tiếp với `CurrentComboFolderPath`.
```
ForEach(VerticalBox_44.Children):
  Cast WBP_TreeNode → IsValid:
    True → GET node.FolderPath → fp
            bActive = (fp == CurrentComboFolderPath) OR
                      (CurrentComboFolderPath StartsWith Append(fp, "/"))
            RefreshDisplay(bIsActive=bActive)
ForEach(VB_ChipTagArea.Children):
  Cast WBP_ChipRow → IsValid:
    True → ForEach(HorizontalBox_ChipRow.Children):
             Cast WBP_ChipTag → IsValid:
               True → GET chip.FolderPath_ChipTag → cfp
                       bActive2 = (cfp == CurrentComboFolderPath) OR
                                  (CurrentComboFolderPath StartsWith Append(cfp, "/"))
                       SetHighlight(bIsActive=bActive2)
```
> **3 call sites:** (1) cuối `RefreshComboFolderUI` (BUG FIX 4.3). (2) cuối `HandleMoveComboConfirmed` bOK=True. (3) cuối `OnComboTreeNodeClicked` sau FilterComboByFolder.

### OnComboTreeNodeClicked(SelectedPath : String, IndentLevel : Integer) — Custom Event
Bound từ mọi WBP_TreeNode trong PopulateComboTreeColumn (kể cả node "+"). Branch theo IndentLevel.
```
Entry → Branch(SelectedPath == "__NEWFOLDER__")            ← NF.G3 guard (06/07), ĐẦU TIÊN
     True  → OnRequestNewFolder( GetNewFolderParent() )      ← KẾT THÚC lần gọi
     False → ClearChildren(VB_ChipTagArea)
              → Branch(IndentLevel == 0):
                   True  → FilterComboByFolder(SelectedPath)
                            PopulateComboTreeColumn()
                   False → FilterComboByFolder(SelectedPath)
                            RebuildChipRowForPath(SelectedPath, 1)   ← thay khối tạo ChipRow trùng lặp (06/07, xem mục Bug fix Chip area)
                            PopulateComboTreeColumn()
```
> ⚠️ **BUG FIX (06/07 — SelectedPath nhầm biến):** lúc nối `RebuildChipRowForPath(?, 1)`, Blueprint đã tự auto-wire nhầm vào **GET class var `SelectedPath`** (biến cũ cùng tên từ `PopulateTreeColumn` phía Furniture/Material) thay vì đúng **pin `SelectedPath` của param Custom Event** này — hậu quả: chip con hiện sai, ra toàn bộ danh sách folder cấp gốc thay vì đúng children của node vừa click. Fix: kéo lại dây từ đúng pin `Selected Path` trên node Entry, không đổi tên biến nào. Cảnh giác khi Custom Event có param trùng tên 1 class var đã tồn tại — auto-suggest dễ nối nhầm.

### OnComboChipTagClicked(SelectedPath_ChipTag : String, IndentLevel_ChipTag : Integer) — Custom Event
Clone của `OnChipTagClicked` (furniture). Bound từ WBP_ChipTag trong VB_ChipTagArea (combo tree).
**Local vars:** RowCount (Int)
```
Entry → SET CurrentComboFolderPath = SelectedPath_ChipTag
→ SET RowCount = GetChildrenCount(VB_ChipTagArea)
→ ForLoop(0, RowCount - IndentLevel_ChipTag - 1):
     Loop Body: RemoveChildAt(VB_ChipTagArea, RowCount - 1 - Index)   ← xóa từ dưới lên
   Completed →
→ FilterComboByFolder(SelectedPath_ChipTag)
→ RebuildChipRowForPath(SelectedPath_ChipTag, IndentLevel_ChipTag)   ← thay khối tạo ChipRow trùng lặp (06/07, xem mục Bug fix Chip area)
```
> `RebuildChipRowForPath` tự set `RowIndentLevel`/`IndentLevel_ChipTag` chip con = `OwnIndentLevel + 1` (khớp hành vi cũ).

### ParentOf(Path : String) → ParentPath : String — Pure
```
Find Substring(Path, "/", SearchFromEnd=True) → idx
Branch(idx == -1):
  True  → return ""
  False → return Left(Path, idx)
```

### LastSegmentOf(Path : String) → Segment : String — Pure
```
Find Substring(Path, "/", SearchFromEnd=True) → idx
Branch(idx == -1):
  True  → return Path
  False → return RightChop(Path, idx + 1)
```

### GetSiblingFolderNames(FolderPath : String) → SiblingNames : Array\<String\> — Pure
```
ParentOf(FolderPath) → ParentPath
Map Find(ComboFolderTree, ParentPath) → CSV, bFound
Branch(bFound):
  False → return Make Array (empty — KHÔNG phải [""])
  True  → Parse Into Array(CSV, ",") → AllSiblings
           Remove Item(AllSiblings, LastSegmentOf(FolderPath))
           return AllSiblings
```

### OnComboTreeNodeRightClicked(FolderPath : String) — Custom Event
Bound từ tất cả WBP_TreeNode qua `OnNodeRightClicked` dispatcher. Guard sentinel ở đây.
```
Entry → Branch(FolderPath == "__ALL__" OR FolderPath == "")
     True  → dead-end   ← AllNode + UncatNode: không có context menu
     False → Create Widget(WBP_LibraryContextMenu) → LibMenu
              SET LibMenu.MenuMode = "Folder"
              SET LibMenu.TargetFolderPath = FolderPath
              Bind LibMenu.OnRequestMoveFolder → OnRequestMoveFolder   [STUB C5.4]
              Bind LibMenu.OnRequestDeleteFolder → OnRequestDeleteFolder   [C5.6]
              LibMenu.AddMenuItem("Create New Folder", "") → Item0 → Bind Item0.OnItemClicked → CB_CreateNewFolder   ← NF, ĐẦU chuỗi
              LibMenu.AddMenuItem("✏️ Đổi tên", "") → Item1 → Bind Item1.OnItemClicked → CB_RenameFolder
              LibMenu.AddMenuItem("📁 Chuyển vào…", "") → Item2 → Bind Item2.OnItemClicked → CB_MoveFolderClick [STUB C5.4]
              LibMenu.AddMenuItem("🗑️ Xóa", "") → Item3 → Bind Item3.OnItemClicked → CB_DeleteFolderClick [C5.6]
              SET LibraryMenuRef = LibMenu
              Get Player Controller → Set Input Mode UI Only
              LibMenu.ShowAt(Get Mouse Position on Viewport)
```
> **NF (04/07):** thêm `Item0 = AddMenuItem("Create New Folder")` TRƯỚC "Đổi tên" — chuỗi AddMenuItem nối tiếp nhau, KHÔNG tạo 2 nhánh song song từ Entry.

### OnRequestRenameFolder(FolderPath : String) — Custom Event (SỬA — v3.8, C5.7b)
Mở rộng: không tìm thấy TreeNode khớp (node cấp 3+ chỉ tồn tại dạng chip, không có trên tree) → fallback loop `VB_ChipTagArea` tìm chip khớp `FolderPath_ChipTag`.
```
SET RenameTargetNode = None
SET RenameTargetChip = None                          ← reset đầu, tránh dính giá trị phiên trước
ForEachLoopWithBreak(GetAllChildren(VerticalBox_44)):
  Body → Cast WBP_TreeNode → IsValid
            True  → Branch(node.FolderPath == FolderPath)
                       True  → SET RenameTargetNode = node → Break
                       False → [dead-end]
            False → [dead-end]
Completed: Branch(IsValid(RenameTargetNode)):
  True  → GetSiblingFolderNames(FolderPath) → Siblings
           RenameTargetNode.EnterRenameMode(Siblings)
  False → ForEachLoopWithBreak(VB_ChipTagArea.GetAllChildren) → Cast WBP_ChipRow      ← vòng NGOÀI
             Body → ForEachLoopWithBreak(HorizontalBox_ChipRow.GetAllChildren) → Cast WBP_ChipTag  ← vòng TRONG
                       Body → Branch(chip.FolderPath_ChipTag == FolderPath)
                                True  → SET RenameTargetChip = chip → Break
                                False → [dead-end]
                       Completed(vòng trong) → Branch(IsValid(RenameTargetChip)) → True → Break(vòng ngoài)
           Completed(vòng ngoài) → Branch(IsValid(RenameTargetChip)):
             True  → GetSiblingFolderNames(FolderPath) → Siblings
                      RenameTargetChip.EnterRenameMode(Siblings)
             False → dead-end (no-op hợp lệ)
```
> **Double-break pattern:** Break trong vòng trong chỉ thoát vòng trong (tự kích `Completed` của nó). Muốn thoát cả vòng ngoài phải kiểm tra `IsValid(RenameTargetChip)` ở `Completed` của vòng trong rồi mới `Break` vòng ngoài — Break KHÔNG xuyên qua 2 tầng loop trực tiếp.

### S_FolderTreeNode — Struct (RENAME v3.9, C5.8 Task Card #1 — trước là `S_FolderTargetEntry`)
```
Path                String            (có sẵn)
DisplayLabel        String            (có sẵn)
Depth               Integer           ← RENAME từ IndentLevel (= Length(ContinuesAncestors))
HasChildren         Boolean           MỚI — arrow hiện/ẩn ở picker
ChildCount          Integer           MỚI — badge số con (đếm sau exclusion)
ContinuesAncestors  Array<Boolean>    MỚI — cột tổ tiên "còn em bên dưới" → vẽ │ hay trống
bIsLast             Boolean           MỚI — con út của cha (sau exclusion) → └ hay ├
```
> `[RENAME]` — log ở DEVIATIONS.md 08/07. 2 chỗ dùng struct này (`WBP_FurnitureInventory`, `WBP_MoveToFolderDialog.PopulateRows`) — Blueprint tự propagate tên mới qua rename, không cần sửa tay widget.

### GetFilteredChildren(ParentPath : String, ExcludePath : String) → Array\<String\> — Pure Function (MỚI, C5.8 Task Card #1, không đệ quy)
**Local var:** LocalResult (Array\<String\>), CSV (String), FullPath (String), child (String)
```
▶ Map Find(Self.ComboFolderTree, Key=ParentPath) ●→ Value(CSV), ReturnValue(bFound)
▶ SET CSV = Value
▶ Branch(bFound == False)
   True  ▶→ Return Node(LocalResult)   ← nối thẳng Make Array (0 input, rỗng)
   False ▶→ Parse Into Array(SourceString=CSV, Delimiter=",") ●→ RawChildren
          ▶ ForEachLoop(RawChildren) — Array Element = child
             SET child = Array Element
             FullPath = Select String(
                Pick = Equal(ParentPath, ""),
                A = child,
                B = Concat(Concat(ParentPath, "/"), child) )
             SET FullPath = (kết quả Select)
             ▶ IfThenElse( OR(
                  Equal(FullPath, ExcludePath),
                  StartsWith(FullPath, Concat(ExcludePath, "/")) ) )
                True  ▶→ (dead-end trong LoopBody — hợp lệ, không phải Event chain)
                False ▶→ Array_Add(LocalResult, child) ▶→ (dead-end, hợp lệ, cuối loop body)
          ▶ Completed ▶→ Return Node(LocalResult)
```
> Q8: Container=Function (Pure) | IsValid: Map Find bFound guard ✓ | L2: True nhánh dead-end trong LoopBody = hợp lệ (không phải Event chain), False nhánh qua Completed→Return ✓ | No latent ✓ | 6A: n/a — pure reader

### BuildFolderTreeRecursive(ParentPath : String, ExcludePath : String, AncestorsContinue : Array\<Boolean\>) → Array\<S_FolderTreeNode\> — Function (Đệ quy, depth guard=12 — RENAME v3.9, trước là `CollectFolderTargets`)
**Local var:** LocalResult (Array\<S_FolderTreeNode\>), ChildAncestors (Array\<Boolean\>), FilteredChildren (Array\<String\>), Count (Int), child (String), FullPath (String), GrandChildren (Array\<String\>), HasChildren (Bool), ChildCount (Int), isLast (Bool)
```
▶ Branch( Array_Length(AncestorsContinue) >= 12 )
   True  ▶→ Return Node( Make Array(0 input, rỗng) )   ← depth guard, folder path acyclic, chỉ bảo hiểm
   False ▶→ SET FilteredChildren = GetFilteredChildren(Self.ParentPath, Self.ExcludePath)
          SET Count = Array_Length(FilteredChildren)
          ▶ ForEachLoop(FilteredChildren) — Array Element = child
             SET child = Array Element

             FullPath = Select String(
                Pick = Equal(ParentPath, ""),
                A = child,
                B = Concat(Concat(ParentPath, "/"), child) )
             SET FullPath = (kết quả Select)

             isLast = Equal(Int)( Array Index, Count - 1 )
             SET isLast

             GrandChildren = GetFilteredChildren(FullPath, ExcludePath)   ← 1 lần duy nhất, dùng cho cả 2 field dưới
             SET GrandChildren
             SET ChildCount = Array_Length(GrandChildren)
             SET HasChildren = ( ChildCount > 0 )

             MakeStruct S_FolderTreeNode(
                Path = FullPath,
                DisplayLabel = child,
                Depth = Array_Length(AncestorsContinue),
                HasChildren = HasChildren,
                ChildCount = ChildCount,
                ContinuesAncestors = AncestorsContinue,   ← param GỐC, chưa mutate
                bIsLast = isLast )
             ▶ Array_Add(LocalResult, [struct trên])

             SET ChildAncestors = AncestorsContinue        ← copy value-type từ param
             ▶ Array_Add(ChildAncestors, NOT isLast)

             ▶ BuildFolderTreeRecursive(FullPath, ExcludePath, ChildAncestors) ●→ ReturnValue(Sub)
             ▶ Array_Append(TargetArray=LocalResult, SourceArray=Sub)   ← LocalResult là accumulator
          ▶ Completed ▶→ Return Node(LocalResult)
```
> ⚠️ **D-C5.4-1:** `Array_Append(TargetArray, SourceArray)` — TargetArray là array NHẬN vào (tích lũy), SourceArray là array phụ. Chiều NGƯỢC thì LocalResult trống sau mỗi đệ quy.
> Q8: Container=Function (đệ quy, có Return) | IsValid: n/a | L2: True nhánh Return trực tiếp, False chảy hết loop→Completed→Return, không dead-end lửng nào khác | No latent ✓ | 6A: n/a — pure builder, không mutate `AncestorsContinue` param gốc

### BuildComboFolderTreeNodes(ExcludePath : String) → Array\<S_FolderTreeNode\> — Function (wrapper, không đệ quy — RENAME v3.9, C5.8 Task Card #1, trước là `BuildMoveFolderTargetList`)
> ⚠️ **[RENAME khác plan gốc]** Plan §3.3/§11 gốc đặt tên wrapper là `BuildFolderTree` — ĐỔI thành `BuildComboFolderTreeNodes` lúc thực thi vì tên đó đã trùng với hàm cũ phía Material/Furniture catalog (không phải combo). Log DEVIATIONS.md 08/07.
**Local var:** RootEntry (Array\<S_FolderTreeNode\>)
```
▶ MakeStruct S_FolderTreeNode(
     Path = "", DisplayLabel = "(Gốc)", Depth = 0,
     HasChildren = False, ChildCount = 0,
     ContinuesAncestors = Make Array(0 input, rỗng),
     bIsLast = False )
▶ Make Array(1 input = struct trên) ●→ SET RootEntry

▶ BuildFolderTreeRecursive(ParentPath="", ExcludePath=Self.ExcludePath, AncestorsContinue=Make Array(0 input, rỗng))
   ●→ ReturnValue(TreeNodes)

▶ Array_Append(TargetArray=RootEntry, SourceArray=TreeNodes)
▶ Return Node(RootEntry)
```
> Q8: Container=Function (không đệ quy, có Return) | IsValid: n/a | L2: 1 nhánh thẳng, không Branch | No latent ✓ | 6A: n/a — pure builder
> Gọi thay `BuildMoveFolderTargetList(MovingPath)` cũ — cùng chữ ký 1 tham số String (nay gọi là `ExcludePath` thay `MovingPath`).
> ⚠️ **[CORRECTION 13/07]** Dòng "call site `OnRequestMoveFolder`/`CB_MoveCombo` không cần sửa tay (Blueprint tự theo tên hàm đã rename)" ở trên — SAI. Thực tế 2 call site VẪN gọi hàm cũ `BuildMoveFolderTargetList` cho tới khi fix thủ công 13/07 (hàm cũ sinh trước khi `HasChildren`/`ChildCount` tồn tại trong struct → arrow/badge không hiện dù folder có con thật). Xem `DEVIATIONS.md` 13/07/2026 [BUG-FIX]. `BuildMoveFolderTargetList` nay đã xoá hẳn khỏi Blueprint.
> **Test PASS (08/07):** Print trên data thật (8 combo, nested 3 tầng, tiếng Việt, cả 2 case `ExcludePath=""` và `ExcludePath="Livingroom/Sofa"`) — Depth/HasChildren/ChildCount/ContinuesAncestors.Length/bIsLast khớp 100% kỳ vọng, không warning. Node flow xác nhận từ export K2Node thật (không còn suy luận).

### OnRequestMoveFolder(FolderPath : String) — Custom Event [C5.4]
```
SET MovingFolderPath = FolderPath

// Guard: dialog đã mở
// (không có MoveComboDialogRef ở đây — đây là Move Folder, không phải Move Combo)

BuildComboFolderTreeNodes(FolderPath) → Entries   ← [BUG-FIX 13/07] call site thật đã fix về hàm này, thay BuildMoveFolderTargetList (xem CORRECTION ở §BuildComboFolderTreeNodes)

Create Widget(WBP_MoveToFolderDialog) → Dialog
Dialog.InitPicker(Entries, ParentOf(FolderPath), True)   ← 13/07: thay PopulateRows(Dialog, Entries) sau khi Dialog đổi sang WBP_FolderTreePicker
Bind Dialog.OnMoveFolderConfirmed → HandleMoveFolderConfirmed
Dialog.AddToViewport
Get Player Controller → Set Input Mode UI Only
```

### OnRequestDeleteFolder(FolderPath : String) — Custom Event [C5.6]
```
SET PendingDeleteFolderPath = FolderPath
Create Widget(WBP_ConfirmDialog) → Dialog
  Message = "Xóa folder '" + LastSegmentOf(FolderPath)
          + "'? Combo bên trong sẽ chuyển về Chưa phân loại (không bị xóa)."
  ConfirmLabel = "Xóa"
Bind Dialog.OnConfirmed → HandleDeleteFolderConfirmed
Add to Viewport
Get Player Controller → Set Input Mode UI Only
```

### HandleDeleteFolderConfirmed() — Custom Event [C5.6]
Bound từ `WBP_ConfirmDialog.OnConfirmed` trong `OnRequestDeleteFolder`.
```
Get Player Controller → Set Input Mode Game and UI
Branch( CurrentComboFolderPath == PendingDeleteFolderPath
        OR CurrentComboFolderPath StartsWith (PendingDeleteFolderPath + "/") )
     True  → ParentOf(PendingDeleteFolderPath) → ParentPath
            → Branch(ParentPath == "")
                 True  → SET CurrentComboFolderPath = "__ALL__"
                 False → SET CurrentComboFolderPath = ParentPath
     False → (merge, không đổi)
→ UComboSerializer::ClearFolderPrefix(PendingDeleteFolderPath) → ChangedCount
→ RefreshComboFolderUI()
→ ShowToastMsg("Đã xóa folder, " + ChangedCount + " combo về Chưa phân loại")   ← [SỬA K1, 23/07] trước là Print String
→ SET PendingDeleteFolderPath = ""
```
> ⚠️ **[ĐÍNH CHÍNH annotation, K1 delta 23/07/2026]** Annotation `[gate bDebugMode]` ở dòng Print
> cũ SAI/lỗi thời — Print đó thực tế chạy KHÔNG điều kiện (không có Branch(bDebugMode) nào bọc
> ngoài). Xác nhận qua Blueprint Export Method lúc làm K1.3. Nay đã đổi hẳn sang `ShowToastMsg`.
>
> **[DEVIATION D-C5.6-1]** Spec gốc (`Combo_C5_FolderManagement_Plan.md`, test case 5) quy định "nhảy về `__ALL__`" khi xóa folder đang xem/cha của đang xem. Đổi thành **"nhảy về folder CHA trực tiếp"** (dùng `ParentOf` có sẵn từ C5.2) — nếu cha là gốc (`""`) thì mới về `__ALL__`. Lý do: UX mượt hơn khi xóa folder lồng sâu — giữ ngữ cảnh thay vì bật về Tất cả mỗi lần xóa. Xem DEVIATIONS.md 06/07.

### CB_DeleteFolderClick — Custom Event (bound từ Item3.OnItemClicked trong OnComboTreeNodeRightClicked) [C5.6]
```
GET LibraryMenuRef → IsValid →
  LibraryMenuRef.Hide
  → OnRequestDeleteFolder(LibraryMenuRef.TargetFolderPath)   ← đọc TRƯỚC khi None
  → SET LibraryMenuRef = None                                ← cuối chuỗi, khớp pattern CB_CreateNewFolder/CB_MoveFolderClick
```
> ⚠️ **BUG FIX (thứ tự exec, 06/07):** Lúc đầu code SET `LibraryMenuRef = None` TRƯỚC khi đọc `TargetFolderPath` → Accessed None runtime error. Đã sửa: đọc property trước, SET None sau cùng.
> ✅ **Đã dọn (06/07):** `CB_RenameFolder` trước đây là ca lẻ loi thiếu `SET LibraryMenuRef = None` sau `Hide` — xem BUG FIX ở §CB_RenameFolder. Nay khớp pattern với 4/4 CB_ còn lại.

### RequestDeleteCombo(ComboID, ComboName : String) — Custom Event (MỚI, Delete Combo, 22/07/2026)
Mirror y hệt `OnRequestDeleteFolder` (Luật 6B structural symmetry). Gọi từ `WBP_ComboCard.BTN_DeleteCombo.OnClicked`.
```
SET PendingDeleteComboID = ComboID
Create Widget(WBP_ConfirmDialog) → Dialog
  Message = "Xóa combo '" + ComboName + "'? Không thể hoàn tác."
  ConfirmLabel = "Xóa"
Bind Dialog.OnConfirmed → HandleDeleteComboConfirmed
Add to Viewport
Get Player Controller → Set Input Mode UI Only
```

### HandleDeleteComboConfirmed() — Custom Event (MỚI, Delete Combo, 22/07/2026)
Bound từ `WBP_ConfirmDialog.OnConfirmed` trong `RequestDeleteCombo`.
```
Get Player Controller → Set Input Mode Game and UI
▶→ GetCombosDir() ●→ + "/" + PendingDeleteComboID + ".json" ●→ SET Local FilePath
▶→ DeleteFileAtPath(FilePath) ●→ SET Local bDeleted
▶→ Branch(bDeleted)
     True  ▶→ DeleteThumbnail(PendingDeleteComboID)
            ▶→ Branch(IsValid(ComboManagerRef))
                 True  ▶→ ComboManagerRef.InvalidateThumbnail(PendingDeleteComboID)
                 False ▶→ (merge)
            ▶→ Get All Actors Of Class(BP_FurnitureUserPrefsManager) → Get(0) ●→ SET Local PrefsRef
            ▶→ Branch(IsValid(PrefsRef))
                 True  ▶→ PrefsRef.IsFavoriteCombo(PendingDeleteComboID) ●→ SET Local bIsFav
                        ▶→ Branch(bIsFav)
                             True  ▶→ PrefsRef.ToggleFavoriteCombo(PendingDeleteComboID)
                             False ▶→ (merge)
                        ▶→ PrefsRef.RemoveRecentCombo(PendingDeleteComboID)
                 False ▶→ (merge)
            ▶→ Broadcast OnComboLibraryChanged
            ▶→ ShowToastMsg("Đã xóa combo")            ← [SỬA K1, 23/07] trước là Print String [TẠM]
     False ▶→ ShowToastMsg("Xóa combo thất bại")        ← [SỬA K1, 23/07] trước là Print String [TẠM]
▶→ SET PendingDeleteComboID = ""
```
> ✅ **[K1 DONE, 23/07/2026]** `Print String [TẠM]` (ghi 22/07, chờ K1) nay đã thay bằng
> `ShowToastMsg` thật — xem Function `ShowToastMsg` mới + `Widgets/WBP_Toast.md`.

Test 5/5 case PASS (22/07/2026):
1. Xóa combo thường → card biến mất, file `.json`+`.png` biến mất khỏi `Saved/Combos/`.
2. Xóa combo đang Favorite → biến mất khỏi cả tab Favorite.
3. Xóa combo có trong Recent → biến mất khỏi tab Recent.
4. Bấm Xóa → Hủy → combo còn nguyên.
5. Xóa xong → tắt/mở PIE → không sống lại, Favorite/Recent sạch.

### OnRenameFolderCommitted(OldPath : String, NewName : String) — Custom Event
Bound từ `WBP_TreeNode.OnNodeRenameCommitted` trong `PopulateComboTreeColumn` (mỗi node cấp 1+2).
```
ParentOf(OldPath) → ParentPath
Branch(ParentPath == ""):
  True  → SET NewFullPrefix = NewName
  False → SET NewFullPrefix = Append(ParentPath, "/", NewName)

Branch(CurrentComboFolderPath == OldPath):
  True  → SET CurrentComboFolderPath = NewFullPrefix
  [False flows down — KHÔNG dead-end]

Branch(String Starts With(CurrentComboFolderPath, Append(OldPath, "/"))):
  True  → Tail = RightChop(CurrentComboFolderPath, String Length(OldPath))
           SET CurrentComboFolderPath = Append(NewFullPrefix, Tail)
  [False flows down — KHÔNG dead-end]

→ UComboSerializer::RenameFolderPrefix(OldPath, NewFullPrefix)
→ RefreshComboFolderUI()
```
> ⚠️ Cả 2 nhánh Branch.False PHẢI merge xuống `RenameFolderPrefix` — KHÔNG dead-end. Nếu dead-end → rename JSON không được gọi khi user không đang xem folder vừa đổi tên.

### CB_RenameFolder — Custom Event (bound từ Item1.OnItemClicked trong OnComboTreeNodeRightClicked)
```
GET LibraryMenuRef → IsValid →
  LibraryMenuRef.Hide   ← đóng menu TRƯỚC
  → OnRequestRenameFolder(LibraryMenuRef.TargetFolderPath)
  → SET LibraryMenuRef = None                                ← BUG FIX 06/07, cuối chuỗi
```
> Sau khi Hide: `OnRequestRenameFolder` → `EnterRenameMode` → `EnterEditMode` → `Delay(0.0)` → SetKeyboardFocus. Menu đã Hide trước Delay nên không steal focus.
> ⚠️ **BUG FIX (06/07):** Bổ sung `SET LibraryMenuRef = None` cuối chuỗi — trước đây là "ca lẻ loi" thiếu dòng này so với `CB_DeleteFolderClick`/`CB_MoveFolderClick`/`CB_CreateNewFolder`. Thứ tự: `Hide` → đọc `TargetFolderPath` tại `OnRequestRenameFolder(...)` (LibraryMenuRef còn sống, chỉ ẩn chưa null) → `SET None` sau cùng.

### CB_MoveFolderClick — Custom Event (bound từ Item2.OnItemClicked trong OnComboTreeNodeRightClicked) [C5.4]
```
GET LibraryMenuRef → IsValid →
  LibraryMenuRef.Hide
  SET LibraryMenuRef = None
  → OnRequestMoveFolder(LibraryMenuRef.TargetFolderPath)
```

### HandleMoveFolderConfirmed(TargetParentPath : String) — Custom Event [C5.4]
Bound từ `WBP_MoveToFolderDialog.OnMoveFolderConfirmed` trong `OnRequestMoveFolder`.
```
// Tính prefix mới: LastSegmentOf(MovingFolderPath) ghép vào TargetParentPath
Branch(TargetParentPath == ""):
  True  → SET NewFullPrefix = LastSegmentOf(MovingFolderPath)
  False → SET NewFullPrefix = Append(TargetParentPath, "/", LastSegmentOf(MovingFolderPath))

// Guard no-op
Branch(NewFullPrefix == MovingFolderPath) → True: dead-end

// Cập nhật CurrentComboFolderPath nếu đang xem folder bị move (2 nhánh cascade)
Branch(CurrentComboFolderPath == MovingFolderPath):
  True  → SET CurrentComboFolderPath = NewFullPrefix
  [False flows down — KHÔNG dead-end]

Branch(CurrentComboFolderPath StartsWith Append(MovingFolderPath, "/")):
  True  → Tail = RightChop(CurrentComboFolderPath, StringLength(MovingFolderPath))
           SET CurrentComboFolderPath = Append(NewFullPrefix, Tail)
  [False flows down — KHÔNG dead-end]

→ UComboSerializer::RenameFolderPrefix(MovingFolderPath, NewFullPrefix)
→ RefreshComboFolderUI()
```
> ⚠️ **D-C5.4-2:** Cả 2 nhánh Branch.False PHẢI merge xuống `RenameFolderPrefix` — KHÔNG dead-end. Bug chỉ lộ khi đang xem ĐÚNG folder bị move (nhánh True) rồi thoát sai sau đó.
> ⚠️ Tái dùng biến `NewFullPrefix` từ C5.2 (OnRenameFolderCommitted) — không tạo biến mới.

### OnComboCardRightClicked(ComboID : String) — Custom Event [C5.5]
Gọi từ `WBP_ComboCard.On Mouse Button Down` khi RMB.
```
// Đóng menu cũ nếu có
GET LibraryMenuRef → IsValid → LibraryMenuRef.Hide
[merge] → SET LibraryMenuRef = None

Create Widget(WBP_LibraryContextMenu) → LibMenu
SET LibMenu.MenuMode = "Combo"
SET LibMenu.TargetComboID = ComboID   ← [SỬA 10/08] thay cho "SET MovingComboID = ComboID" cũ
                                          (đã SAI, không tồn tại trong code thật — xem ghi chú)
LibMenu.AddMenuItem("📁 Chuyển vào folder…", "") → Item1 → Bind Item1.OnItemClicked → CB_MoveCombo
LibMenu.AddMenuItem("📤 Xuất file…", "") → Item2 → Bind Item2.OnItemClicked → CB_ExportCombo   [MỚI — C11.2]
SET LibraryMenuRef = LibMenu
Get Player Controller → Set Input Mode UI Only
LibMenu.ShowAt(Get Mouse Position on Viewport)
```
> ⚠️ **DOC-DRIFT FIX (10/08/2026):** bản trước ghi "SET MovingComboID = ComboID" — xác nhận
> SAI qua K2Node export thật. ComboID lưu vào `LibMenu.TargetComboID` (field của widget menu),
> không qua biến `MovingComboID` (biến đó chỉ `CB_MoveCombo` dùng, đọc lại từ chính
> `LibraryMenuRef` khi cần — không phải biến trung gian ComboID chung). Nguồn: cuhoang paste
> K2Node export, đối chiếu Claude (Sonnet) 10/08/2026.

### CB_MoveCombo — Custom Event (bound từ Item1.OnItemClicked trong OnComboCardRightClicked) [C5.5]
**✓K2 10/08/2026** — sửa lại theo K2Node export thật (xem ghi chú xác nhận dưới).
```
GET LibraryMenuRef → IsValid →
LibraryMenuRef.Hide
SET MovingComboID = LibraryMenuRef.TargetComboID   ← [XÁC NHẬN 10/08] SET này nằm Ở ĐÂY,
                                                       KHÔNG ở OnComboCardRightClicked (doc cũ
                                                       ghi sai vị trí — xem ghi chú dưới)

// Guard: dialog đã mở → không mở chồng
Branch(IsValid MoveComboDialogRef):
  True  → RemoveFromParent(MoveComboDialogRef) → SET MoveComboDialogRef = None → [merge]
  False → [merge]

// Tìm FolderPath hiện tại của combo này
BuildComboFolderTreeNodes(ExcludePath="") → Entries
ForEachLoopWithBreak(AllComboViews_Combo):
  Body → IsValid(item):
           True  → Branch(item.ComboID == LibraryMenuRef.TargetComboID):
                      True  → SET MovingComboCurrentFolder = item.FolderPath → Break
                      False → [dead-end, next iteration]
           False → [dead-end, next iteration]
Completed →
Create Widget(WBP_MoveToFolderDialog) → Dialog
SET MoveComboDialogRef = Dialog
Dialog.InitPicker(Entries, MovingComboCurrentFolder, bInShowTag=True)
Bind Dialog.OnMoveFolderConfirmed → HandleMoveComboConfirmed
Dialog.AddToViewport
Get Player Controller → Set Input Mode Game and UI Ex (InWidgetToFocus = Dialog)
```
> **QUY TẮC (từ bài học Sprint 1):** `ForEachLoopWithBreak` — code chạy 1 lần sau vòng lặp PHẢI nối `Completed`, KHÔNG `Loop Body`.

> ⚠️ **XÁC NHẬN 10/08/2026 (giải quyết mâu thuẫn Claude Code tự phát hiện ở lượt merge trước):**
> `MovingComboID` **KHÔNG chết** — vẫn được SET, nhưng vị trí đúng là **đầu `CB_MoveCombo`**
> (đọc từ `LibraryMenuRef.TargetComboID`), không phải trong `OnComboCardRightClicked` như bản
> doc trước 10/08 ghi. `OnComboCardRightClicked` chỉ SET `LibMenu.TargetComboID`, không đụng
> `MovingComboID`. Loop tìm folder hiện tại (bên trong `CB_MoveCombo`) đọc lại
> `LibraryMenuRef.TargetComboID` trực tiếp (không qua `MovingComboID`) để so sánh — 2 nguồn
> đọc cùng giá trị nhưng qua 2 đường khác nhau, không phải bug, chỉ là cách viết.
> `HandleMoveComboConfirmed` (event riêng, chạy sau khi dialog xác nhận) đọc lại biến class
> `MovingComboID` để gọi `UpdateComboFolder` + dựng thông báo lỗi — đây là lý do `MovingComboID`
> phải là biến CLASS (sống qua nhiều event), không phải biến cục bộ.
> Nguồn: K2Node export CB_MoveCombo, cuhoang paste 10/08/2026, đối chiếu Claude (Sonnet).

### CB_ExportCombo — Custom Event [C11.2] (bound từ Item2.OnItemClicked trong OnComboCardRightClicked)
```
GET LibraryMenuRef → IsValid →
LibraryMenuRef.Hide
→ UComboSerializer::ExportCombo(ComboID = LibraryMenuRef.TargetComboID) ●→ OutExportedPath, Return(bExported)
→ SET LibraryMenuRef = None
→ Get Player Controller → Set Input Mode Game and UI ← [BUG FIX 10/08, xem DEVIATIONS]
→ Branch(bExported):
    True → ShowToastMsg("Đã xuất: " + OutExportedPath)
    False → ShowToastMsg("Xuất thất bại")
False → [dead-end]
```
> Không cần biến tạm lưu ComboID — đọc thẳng `LibraryMenuRef.TargetComboID` vào pin `ExportCombo`,
> dùng ngay lập tức trong cùng event, không cần nhớ lại ở event khác (khác `CB_MoveCombo`, vốn cần
> giữ ComboID qua tới `HandleMoveComboConfirmed` chạy sau khi dialog đóng).
> Test PASS 3/3 case (export ra file đúng path + tên tiếng Việt giữ nguyên (M7) + thumbnailBase64
> nhúng đúng khi combo có .png + export 2 lần đè file cũ, không lỗi). Nguồn:
> `DELTA_10-08-2026_C11_P4early.md` + test tay 10/08/2026.

### CB_ImportCombo — Custom Event [C11.3] (bound từ BTN_ImportCombo.OnClicked)
> Quyết định UX (10/08): Import KHÔNG dùng context menu combo card (sai ngữ cảnh — Import
> không thao tác lên combo cụ thể nào). Dùng NÚT RIÊNG (`BTN_ImportCombo`), pattern gọn như
> Export (không IsValid guard nào cần — không object nào cần kiểm; không Set Input Mode nào
> cần trả — nút bấm thường không mở UI Only nào để phải trả lại).
```
CB_ImportCombo:
▶→ ImportAllFromExportsDir ●→ OutImported, OutFailed
▶→ Branch(OutImported > 0):
     True  ▶→ CallDelegate ComboManagerRef.OnComboLibraryChanged
           ▶→ RefreshComboFolderUI()
           ▶→ Branch(OutFailed > 0):
                True  ▶→ ShowToastMsg("Đã nhập " + IntToString(OutImported) + " combo (" + IntToString(OutFailed) + " lỗi)")
                False ▶→ ShowToastMsg("Đã nhập " + IntToString(OutImported) + " combo")
     False ▶→ Branch(OutFailed > 0):
                True  ▶→ ShowToastMsg("File combo không hợp lệ")
                False ▶→ ShowToastMsg("Không có file .combojson trong thư mục Exports")
```
> `Target` của `CallDelegate` PHẢI là `ComboManagerRef` (biến class, kiểu `BP_ComboManager`) —
> KHÔNG phải `self`. `self` ở `WBP_FurnitureInventory` không phải `BP_ComboManager`, gây lỗi
> compile "Target must have a connection". Bài học ghi vào `DEVIATIONS.md`.
> Test PASS 4/4 case (10/08/2026): (1) xóa combo → Nhập lại → quay về ID mới; (2) file gốc
> dọn sang `Exports/Imported/`; (3) Nhập file đã tồn tại combo cùng nội dung → 2 combo ID khác
> nhau; (4) file rác (.txt đổi .combojson) → toast lỗi, không crash, file rác KHÔNG bị move.

### HandleMoveComboConfirmed(TargetParentPath : String) — Custom Event [C5.5]
Bound từ `WBP_MoveToFolderDialog.OnMoveFolderConfirmed` trong `CB_MoveCombo`.
```
GET MoveComboDialogRef → IsValid → MoveComboDialogRef.RemoveFromParent
SET MoveComboDialogRef = None
Get Player Controller → Set Input Mode Game and UI

// Guard no-op
Branch(MovingComboCurrentFolder == TargetParentPath) → True: dead-end

// Gọi C++ cập nhật JSON
UComboSerializer::UpdateComboFolder(MovingComboID, TargetParentPath) → bOK
Branch(bOK):
  True  → RefreshComboFolderUI()
  False → ShowToastMsg("UpdateComboFolder failed — ComboID: " + MovingComboID)   ← [SỬA K1, 23/07] trước là Print String
```

---

## NF — New Folder (context menu part, 04/07/2026)

> Context-menu part DONE + test PASS. Nút "+" đầu cột tree (NF-C1/NF-C2, tạo TRONG folder
> đang xem qua `GetNewFolderParent`) CÒN NỢ — xem `01_Session_State.md` TIẾP THEO.
> Deviation: dialog (plan gốc NF.G2-G5) → SUPERSEDED bởi inline rename. Xem DEVIATIONS.md 04/07.

### GetChildFolderNames(ParentPath : String) → Array\<String\> — Pure
```
Map Find(ComboFolderTree, Key=ParentPath) → CSV, bFound
Branch(bFound):
  True  → Parse Into Array(CSV, ",") → Return    ← delimiter "," (khớp AddFolderPathToTree)
  False → Return Make Array (rỗng)
```

### GetUniqueNewFolderName(ParentPath : String) → String — Function (While Loop)
**Local vars:** Existing (Array\<String\>), Candidate (String), Counter (Int)
```
SET Existing = GetChildFolderNames(ParentPath)
SET Candidate = "New Folder"
SET Counter = 2
Branch(Array_Contains(Existing, Candidate) == false):
  True  → Return Candidate
  False → While Loop [Condition = Array_Contains(Existing, Candidate)]:
            Body: SET Candidate = "New Folder (" + Conv_IntToString(Counter) + ")"
                  SET Counter = Counter + 1
            Completed: Return Candidate
```
> Pure `Array_Contains` re-evaluate mỗi vòng While = ĐÚNG Ý (Candidate đổi liên tục).

### GetNewFolderParent() → String — Pure
```
Branch(CurrentComboFolderPath == "" OR CurrentComboFolderPath StartsWith "__"):
  True  → Return ""                       ← Tất cả / Chưa phân loại / sentinel → tạo gốc
  False → Return CurrentComboFolderPath   ← tạo trong folder đang xem (nút "+", NF-C2)
```

### OnRequestNewFolder(ParentPath : String) — Custom Event
> ⚠️ **[ĐÍNH CHÍNH as-built, K1 delta 23/07/2026]** Doc trước đây mô tả toàn bộ logic
> (GetUniqueNewFolderName → Branch → CreateEmptyFolder → Branch → Refresh/Rename hoặc Print) nằm
> THẲNG trong `OnRequestNewFolder` — SAI. Thực tế `OnRequestNewFolder` chỉ gọi 1 lệnh sang
> Function riêng `CreateNewFolderFlow` (Target=self); toàn bộ logic thật nằm trong function đó.
> Xác nhận qua Blueprint Export Method (K2Node text) lúc làm K1.3.
```
OnRequestNewFolder(ParentPath)
▶→ CreateNewFolderFlow(ParentPath)   ← Target=self, xem Function riêng bên dưới
```

### CreateNewFolderFlow(ParentPath : String) — Function (MỚI đưa vào doc, K1 delta 23/07/2026)
```
GetUniqueNewFolderName(ParentPath) → SET NewName
Branch(ParentPath == ""):
  True  → SET FullPath = NewName
  False → SET FullPath = ParentPath + "/" + NewName
[merge] → UComboSerializer::CreateEmptyFolder(FullPath) → bOK
Branch(bOK):
  True  → RefreshComboFolderUI()
           → OnRequestRenameFolder(FullPath)    ← tái dùng "Request" phase C5.2 → vào rename mode
  False → ShowToastMsg("Không tạo được folder: " + FullPath)   ← [SỬA K1, 23/07] trước là Print String, tái dùng nguyên node Concat có sẵn
```
> **[ĐÍNH CHÍNH annotation, K1 delta 23/07/2026]** Print gốc ở nhánh `bOK=False` KHÔNG gate bằng
> `Branch(bDebugMode)` như annotation cũ ghi — annotation đó SAI/lỗi thời. Thực tế gate bằng
> thuộc tính node **`EnabledState = Development Only`** (tự strip khỏi Shipping build, không qua
> Branch thủ công). Nay đổi hẳn sang `ShowToastMsg` nên điểm này không còn áp dụng, ghi lại để
> tránh nhầm khi đọc log cũ.
>
> KHÔNG CaptureSnapshot (folder ops ngoài Undo, D16). KHÔNG đổi CurrentComboFolderPath (NF-C3 no-navigate).

### CB_CreateNewFolder — Custom Event (bound từ Item0.OnItemClicked, AddMenuItem("Create New Folder") đặt ĐẦU chuỗi trong OnComboTreeNodeRightClicked)
**Local var:** LocalTargetPath (String)
```
IsValid(LibraryMenuRef):
  True  → SET LocalTargetPath = LibraryMenuRef.TargetFolderPath   ← cache TRƯỚC Hide (chống Accessed None)
           → LibraryMenuRef.Hide
           → SET LibraryMenuRef = None
           → ParentOf(LocalTargetPath) → ParentPath   ← tạo CÙNG CẤP (bỏ segment cuối, D-NF-2)
           → OnRequestNewFolder(ParentPath)
  False → [dead-end]
```

> ⚠️ **BUG FIX (06/07, phát hiện lúc test C5.7b):** Node `SET Local Target Path = ""` (Default Value để trống) đè mất giá trị vừa cache từ `LibraryMenuRef.TargetFolderPath` → `ParentOf("")` luôn trả `""` → folder mới LUÔN tạo ở root bất kể right-click sâu đến đâu. **Đã xóa node thừa** — `Local Target Path` giờ chỉ bị ghi 1 lần duy nhất (cache) đúng như pseudocode trên, `ParentOf` đọc lại đúng giá trị đã cache từ `LibraryMenuRef.TargetFolderPath`.

> **NF.G3 (06/07) — DONE:** nút "+" đầu cột tree implement — xem `PopulateComboTreeColumn` (PlusNode) + `OnComboTreeNodeClicked` (guard `__NEWFOLDER__`) ở trên. Không tạo hàm mới — tái dùng `GetNewFolderParent()` + `OnRequestNewFolder(ParentPath)` đã có. Khác biệt so với context-menu "Create New Folder": nút "+" tạo folder TRONG folder đang xem (`GetNewFolderParent`), context-menu tạo CÙNG CẤP node bị right-click (`ParentOf`). Test PASS 5/5.

---

## C5.7a — ChipTag right-click → context menu (06/07/2026)

Tái dùng `OnComboTreeNodeRightClicked` cho cả tree node lẫn chip — không cần logic menu mới. Đầy đủ ở phía `WBP_ChipTag` (dispatcher `OnChipRightClicked` + `On Mouse Button Down` override) — xem `WBP_ChipTag.md`. Bind ở `RebuildChipRowForPath` (mục dưới) — 1 điểm bind DUY NHẤT, dùng chung cho mọi chip được tạo:
```
Bind OnChipRightClicked(NewChip) → OnComboTreeNodeRightClicked   ← tái dùng handler tree, signature khớp (FolderPath : String)
```

**Test PASS 3/4 case ban đầu:** right-click chip mở menu đúng path, move/xóa từ chip chạy đúng, click trái chip vẫn chọn folder bình thường. Rename từ chip → **FAIL theo dự kiến** (thuộc C5.7b — `OnRequestRenameFolder` chưa biết tìm node trong `VB_ChipTagArea`, chưa làm — CÒN NỢ).

---

## Bug fix — Chip area không tự refresh sau Move/Xóa/Rename folder (06/07/2026)

**Phát hiện lúc test C5.7a case 3** (move combo từ chip → chip area không tự vẽ lại, phải chuyển folder khác rồi quay lại). **Nguyên nhân gốc:** `RefreshComboFolderUI()` chỉ vẽ lại `VerticalBox_44` (tree) — không có gì chủ động vẽ lại `VB_ChipTagArea` khi dữ liệu đổi từ nguồn khác (move/rename/xóa), cột chip trước đó chỉ được dựng tại thời điểm click.

### RebuildChipRowForPath(Path : String, OwnIndentLevel : Integer) — Function (SỬA — v3.8)
Tách logic dựng 1 hàng chip (trước đây lặp lại 2 lần trong `OnComboTreeNodeClicked` và `OnComboChipTagClicked`) thành hàm dùng chung — CẢ 2 nơi gọi hàm này thay vì tự dựng ChipRow.
```
Map Find(ComboFolderTree, Path) → ChildCSV, bFound
Branch(bFound):
  False → return (không có gì để vẽ)
  True  → Create Widget(WBP_ChipRow) → Row
           SET Row.RowIndentLevel = OwnIndentLevel + 1
           Parse Into Array(ChildCSV, ",") → ChildNames
           ForEach ChildNames (element):
             Create Widget(WBP_ChipTag) → NewChip
             SET NewChip.FolderPath_ChipTag = Append(Path, "/", element)
             SET NewChip.FolderName_ChipTag = element
             SET NewChip.IndentLevel_ChipTag = OwnIndentLevel + 1
             Bind OnChipSelected(NewChip) → OnComboChipTagClicked
             Bind OnChipRightClicked(NewChip) → OnComboTreeNodeRightClicked   ← C5.7a
             Bind NewChip.OnChipRenameCommitted → OnRenameFolderCommitted   ← v3.8, C5.7b, tái dùng nguyên không logic mới
             AddChild(Row.HorizontalBox_ChipRow, NewChip)
           Completed → AddChild(VB_ChipTagArea, Row)
```

### RefreshChipBreadcrumb() — Function
Dựng lại TOÀN BỘ chuỗi hàng chip từ `CurrentComboFolderPath`. Gọi từ `RefreshComboFolderUI` sau `UpdateComboFolderHighlights` (cả 3 nhánh filter).
```
ClearChildren(VB_ChipTagArea)
Branch(CurrentComboFolderPath == "__ALL__" OR CurrentComboFolderPath == ""):
  True → return
Parse Into Array(CurrentComboFolderPath, "/") → Segments   ← Delimiter PHẢI là "/" (1 ký tự)
Branch(Segments.Length <= 1):
  True → return          ← cấp 1 (root) — tree tự vẽ cấp 2 lồng, không cần chip

Local: BuildPath = Append(Segments[0], "/", Segments[1])   ← path cấp 2
Local: Lvl = 1
RebuildChipRowForPath(BuildPath, Lvl)                       ← LUÔN vẽ hàng đầu

Branch(Segments.Length > 2):
  False → return
  True  → ForLoop(2, Segments.Length - 1):
            SET BuildPath = Append(BuildPath, "/", Segments[Index])
            SET Lvl = Lvl + 1
            RebuildChipRowForPath(BuildPath, Lvl)
          Completed → end
```

> ⚠️ **BUG FIX #2 (Delimiter sai):** `Parse Into Array` trong `RefreshChipBreadcrumb` có `Delimiter = "/ "` (gạch chéo + khoảng trắng) thay vì `"/"` — gõ nhầm lúc tạo node. Vì `CurrentComboFolderPath` không chứa chuỗi `"/ "`, `ParseIntoArray` không tách được gì, trả mảng 1 phần tử → `Segments.Length <= 1` luôn True → hàm return sớm, chip area trống dù đáng lẽ phải vẽ. Đã sửa Delimiter về `"/"` (1 ký tự).
> ⚠️ **BUG FIX #3 (logic sai vô hại):** node điều kiện đầu (check `__ALL__`/`""`) dùng nhầm `BooleanAND` thay vì `BooleanOR` — về lý thuyết sai (1 chuỗi không thể vừa bằng 2 giá trị khác nhau cùng lúc, nhánh True không bao giờ chạy được), nhưng KHÔNG gây triệu chứng vì `Branch(Segments.Length <= 1)` phía sau vô tình bắt được cả 2 case đó. Đã sửa `AND` → `OR` cho đúng ý định logic, dù hành vi runtime không đổi.

**Test PASS sau fix:** click __ALL__ dọn sạch chip / xóa folder cha đang xem con → về cha, con còn lại hiện đủ ngay / regression case 2-4 segment path đều đúng.

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
Entry
  ▶→ SET "Selected Path" = SelectedPath          (class var)
  ▶→ SET "Indent Level" = IndentLevel            (class var)
  ▶→ SetText(TB_Breadcrumb, To Text(SelectedPath))
  ▶→ Branch( IndentLevel == 0 )                  ← IfThenElse_3
       True  → SET ActiveLevel1Path = "Selected Path"
                ▶→ ClearChildren(VB_ChipTagArea)
                ▶→ PopulateTreeColumn()
                ▶→ FilterByFolderPath("Selected Path")
                ▶→ UpdateFolderHighlights()
                ▶→ Branch( "Selected Path" == "" )  ← IfThenElse_1 (set breadcrumb)
                     True  → SetText(TB_Breadcrumb, "All product")
                     False → SetText(TB_Breadcrumb, To Text("Selected Path"))
       False → Branch( IndentLevel == 1 )         ← IfThenElse_4
                 True → ClearChildren(VB_ChipTagArea)
                        ▶→ SetText(TB_Breadcrumb, To Text("Selected Path"))
                        ▶→ Map Find(FolderTree, Key="Selected Path") → Value
                        ▶→ ParseIntoArray(Value, Delimiter=",") → ChildArray
                        ▶→ Create Widget(WBP_ChipRow) → NewRow
                            SET NewRow.RowIndentLevel = (Indent Level)
                        ▶→ ForEach ChildArray (element):
                             Create Widget(WBP_ChipTag) → NewChip
                             SET NewChip.FolderPath_ChipTag = "Selected Path" + "/" + element
                             SET NewChip.FolderName_ChipTag = element
                             SET NewChip.IndentLevel_ChipTag = 2   ← (default pin = 2)
                             Bind NewChip.OnChipSelected → OnChipTagClicked
                             AddChild(NewChip → NewRow.HorizontalBox_ChipRow)
                           Completed → AddChild(NewRow → VB_ChipTagArea)
                 False → [dead-end]
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

### FilterByFolderPathWithUI(FolderPath) — Custom Event — SỬA 30/07/2026 (Folder Highlight Fix) + SỬA 01/08/2026 (node-verified qua K2Node export)
```
1. SET "Folder Path" (class var) = FolderPath (param)   ← ★ MỚI xác nhận 01/08 — chưa từng ghi
2. Map Find(FolderTree, "") → Parse(",") → Level1Array → ForEach:
   FolderPath Contains Element → True: SET ActiveLevel1Path
   False → (dead-end trong Loop Body — hợp lệ, L2)      ← ★ SỬA 01/08 — KHÔNG phải ForEachLoopWithBreak
3. PopulateTreeColumn
4. Split(GET "Folder Path", "Object_Model/") → Right S = ShortPath   ← ★ SỬA 01/08 — đọc qua GET
   class var (bước 1), KHÔNG phải trực tiếp trên param
5. Clear Children(VB_ChipTagArea) → Visible
6. CreateChipTagsForPath(ShortPath)
7. FilterByFolderPath(ShortPath)         ← ★ SỬA 30/07 — trước đó truyền FolderPath (FULL path)
8. UpdateFolderHighlights()              ← ★ MỚI 30/07 — chèn TRƯỚC bước 9
9. SetText(TB_Breadcrumb, ShortPath)
```
Gọi từ: BTN_Replace (MeshControls), BTN_ChangeMesh (DetailPopup), selection handler Replace branch.

**Đính chính 01/08/2026:** doc trước đây (v3.16) không ghi bước 1 (class var `Folder Path`) và ghi
sai loop ở bước 2 là `ForEachLoopWithBreak` — export K2Node thật xác nhận đây là `ForEachLoop`
thường, nhánh `False` dead-end trong Loop Body (hợp lệ theo L2, không cần nối gì). Hàm dựng
chiptag ở bước 6 (`CreateChipTagsForPath`) đã đúng tên từ trước — có báo cáo nghi ngờ doc ghi nhầm
thành `RebuildChipRowForPath` nhưng rà lại toàn bộ docs KHÔNG tìm thấy vị trí ghi sai này (file
này đã đúng `CreateChipTagsForPath` từ v3.16); `RebuildChipRowForPath` là hàm THẬT khác, dựng 1
chip ROW đơn lẻ khi click tree/chip (xem mục `RebuildChipRowForPath` dưới) — không liên quan
`FilterByFolderPathWithUI`.

**Root cause đã fix (30/07/2026):** bước 6 trước đây ăn `FolderPath` FULL path (vd
`/Game/.../Object_Model/Furniture/Table/Side_Table`) → `CurrentFolderPath` (class var, xem
`FilterByFolderPath` bên dưới) bị SET thành full path → `IsPathActive` (so `StartsWith`) chỉ
match được node gốc rỗng ("All") → chỉ "All" sáng trên tree/chip, không node nào khác từng sáng
khi vào Replace bằng code (khác đường click tay, đi qua `OnTreeNodeClicked`/`OnChipTagClicked`
riêng — vốn đã tự truyền relative path, không dính bug này). Fix: đổi input pin của
`FilterByFolderPath` sang `ShortPath` (= `Split.RightS`, cùng nguồn relative dùng chung cho
`CreateChipTagsForPath`/breadcrumb) — 1 nguồn duy nhất cho cả 3 chỗ dùng. Đồng thời chèn
`UpdateFolderHighlights()` ngay sau `FilterByFolderPath` — cần vì luồng vào bằng code (replace)
KHÔNG đi qua `OnTreeNodeClicked`/`OnChipTagClicked` (nơi vốn tự gọi highlight refresh) nên phải
tự refresh ở đây.

### CreateChipTagsForPath(ShortPath)
```
Local: CurrentPath="" | CurrentIndentLevel=2
Clear Children(VB_ChipTagArea)
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
| 3.0 | 25/06/2026 — C5.0 Combo Folder Tree + Filter | E_InventoryMode +Combo; 3 class var C5 (CurrentComboFolderPath/ComboFolderTree/bHasUncategorized); BTN_Tab_Combo; SwitchInventoryMode +nhánh Combo (TRƯỚC Material); 6 function mới: AddFolderPathToTree, BuildComboFolderTree, PopulateComboTreeColumn (cấp 1 phẳng), FilterComboByFolder, RefreshComboFolderUI, OnComboTreeNodeClicked (đơn giản). Superseded bởi v3.1 cùng ngày. |
| 3.1 | 25/06/2026 — C5.0 Tree 2 cấp + Chip Nav (Round 3 delta) | PopulateComboTreeColumn: render 2 cấp (cấp 1 IndentLevel=0, cấp 2 IndentLevel=1 lồng). OnComboTreeNodeClicked: REWRITE branch IndentLevel (0→clear+filter+repopulate; 1→filter+gen WBP_ChipRow cấp 3). OnComboChipTagClicked: NEW. Superseded bởi v3.2 (26/06). |
| 3.2 | 26/06/2026 — C5.0 Tree Nested + Right-click + WBP_LibraryContextMenu | PopulateComboTreeColumn: D9 Branch guard (cấp 2 CHỈ hiện khi active) + Bind OnNodeRightClicked 4 node. OnComboTreeNodeClicked: rewrite (ClearChildren chung trước Branch, Append(), HorizontalBox_ChipRow). OnComboChipTagClicked: đổi params (SelectedPath_ChipTag/IndentLevel_ChipTag), fix ForLoop formula. OnComboTreeNodeRightClicked: NEW (spawn WBP_LibraryContextMenu, guard sentinel). OnRequestRenameFolder/MoveFolder/DeleteFolder: STUB C5.2/C5.4/C5.5. Test end-to-end PASS 26/06. |
| 3.3 | 27/06/2026 — C5.2 Inline Rename Folder | 3 Pure helpers (ParentOf/LastSegmentOf/GetSiblingFolderNames). OnRequestRenameFolder: implement (ForEachLoopWithBreak tìm node + EnterRenameMode). OnRenameFolderCommitted: NEW (cascade CurrentComboFolderPath + RenameFolderPrefix + RefreshComboFolderUI). CB_RenameFolder: NEW (Hide menu → OnRequestRenameFolder). OnComboTreeNodeRightClicked: AddMenuItem → capture return → bind OnItemClicked → CB_X; SET LibraryMenuRef; xóa Print String debug. PopulateComboTreeColumn: bind OnNodeRenameCommitted → OnRenameFolderCommitted (Node1+Node2). Class vars: RenameTargetNode/NewFullPrefix/LibraryMenuRef. BUG FIX: RefreshComboFolderUI confirmed PopulateComboTreeColumn. FilterComboByFolder ⚠️→✅ FIXED. |
| 3.4 | 30/06/2026 — C5.4 Move Folder | Class var MovingFolderPath (String). CollectFolderTargets(ParentPath, IndentLevel, MovingPath) — đệ quy, trả Array<S_FolderTargetEntry>, loại MovingPath + con cháu (Branch StartsWith). BuildMoveFolderTargetList(MovingPath) — wrap + thêm entry "(Gốc)". OnRequestMoveFolder implement (đã STUB từ C5.0). CB_MoveFolderClick implement (đã STUB). HandleMoveFolderConfirmed NEW — tính NewFullPrefix (tái dùng var C5.2), guard no-op, cập nhật CurrentComboFolderPath, gọi RenameFolderPrefix + RefreshComboFolderUI. BUG FIX D-C5.4-1 (Array_Append ngược Target/Source), D-C5.4-2 (dead-end thiếu merge nhánh True). |
| 3.5 | 01/07/2026 — C5.5 Move Combo + BUG FIX 4.1/4.2/4.3 | Class var: MoveComboDialogRef/MovingComboID/MovingComboCurrentFolder. UpdateComboFolderHighlights() NEW (Issue 2): mirror UpdateFolderHighlights cho combo side, dùng CurrentComboFolderPath. OnComboCardRightClicked(ComboID) NEW: tạo context menu "Combo" mode từ RMB trên WBP_ComboCard, bind CB_MoveCombo. CB_MoveCombo NEW: guard stacking, ForEachLoopWithBreak tìm FolderPath hiện tại, tạo WBP_MoveToFolderDialog, bind HandleMoveComboConfirmed. HandleMoveComboConfirmed NEW: close dialog, guard no-op, UpdateComboFolder C++, RefreshComboFolderUI. WBP_ComboCard +InventoryRef class var + On Mouse Button Down override. BUG FIX 4.1 (ParseIntoArray delimiter phải "," không cách). BUG FIX 4.2 (RefreshComboFolderUI bỏ Map_Contains — leaf folder không là key). BUG FIX 4.3 (RefreshComboFolderUI thêm UpdateComboFolderHighlights sau merge 3 nhánh). |
| 3.6 | 04/07/2026 — NF (New Folder) context-menu part | 3 Pure helpers mới: GetChildFolderNames(ParentPath) (Map Find + Parse Into Array), GetUniqueNewFolderName(ParentPath) (While Loop sinh "New Folder"/"New Folder (2)"...), GetNewFolderParent() (rỗng nếu Tất cả/Chưa phân loại/sentinel, ngược lại CurrentComboFolderPath — dùng cho nút "+" còn nợ). OnRequestNewFolder(ParentPath) NEW: CreateEmptyFolder C++ → RefreshComboFolderUI → OnRequestRenameFolder (tái dùng rename phase C5.2), KHÔNG CaptureSnapshot, KHÔNG đổi CurrentComboFolderPath. CB_CreateNewFolder NEW: cache TargetFolderPath trước Hide, ParentOf → tạo CÙNG CẤP node bị right-click (D-NF-2). OnComboTreeNodeRightClicked: +1 menu item "Create New Folder" đầu chuỗi AddMenuItem. Test PASS 9/9. Deviation: dialog (NF.G2-G5 gốc) SUPERSEDED bởi inline rename (D-NF-1); không dispatcher riêng trên WBP_LibraryContextMenu (D-NF-3). Còn nợ: nút "+" đầu cột tree. |
| 3.7 | 06/07/2026 — NF.G3 (nút "+") + C5.6 (Xóa folder) + C5.7a (ChipTag right-click) | **NF.G3:** PopulateComboTreeColumn +PlusNode (sentinel `__NEWFOLDER__`, đầu tiên); OnComboTreeNodeClicked +guard đầu tiên → OnRequestNewFolder(GetNewFolderParent()). Không hàm mới. Test PASS 5/5. **C5.6:** class var PendingDeleteFolderPath; OnRequestDeleteFolder implement (mở WBP_ConfirmDialog mới); HandleDeleteFolderConfirmed NEW (ClearFolderPrefix C++ + navigate về cha); CB_DeleteFolderClick implement. Deviation D-C5.6-1 (nhảy về cha thay vì __ALL__). BUG FIX thứ tự exec (đọc TargetFolderPath trước SET None). Test PASS 6/6. **C5.7a:** WBP_ChipTag +dispatcher OnChipRightClicked + On Mouse Button Down override (xem WBP_ChipTag.md v1.2); bind → OnComboTreeNodeRightClicked (tái dùng, không logic mới). Test PASS 3/4 (rename từ chip = C5.7b, chưa làm). **Refactor + bug fix phát sinh:** RebuildChipRowForPath (hàm mới, gộp code tạo ChipRow trùng lặp) + RefreshChipBreadcrumb (hàm mới, tự vẽ lại toàn bộ chip breadcrumb) — RefreshComboFolderUI gọi RefreshChipBreadcrumb sau UpdateComboFolderHighlights ở cả 3 nhánh. BUG FIX #1 (2/3 nhánh dead-end trước khi nối), #2 (delimiter "/ " sai lẽ ra "/"), #3 (BooleanAND→OR vô hại). Bug fix SelectedPath nhầm biến (class var trùng tên param) trong OnComboTreeNodeClicked. |
| 3.8 | 06/07/2026 — C5.7b (Inline Rename chip) + 2 bug fix — **C5 HOÀN TẤT** | Class var mới `RenameTargetChip` (WBP_ChipTag). `OnRequestRenameFolder` mở rộng fallback tree→chip khi không tìm thấy TreeNode khớp (double-break qua Completed loop lồng). `RebuildChipRowForPath` +bind `OnChipRenameCommitted`→`OnRenameFolderCommitted` (tái dùng nguyên). BUG FIX `CB_CreateNewFolder`: node `SET Local Target Path=""` thừa đè mất cache → luôn tạo root bất kể right-click sâu đến đâu — đã xóa node thừa. BUG FIX `CB_RenameFolder`: bổ sung `SET LibraryMenuRef=None` cuối chuỗi (ca lẻ loi thiếu dòng này so với 3 CB_ khác). Test PASS full case rename chip + Create New Folder từ chip sâu. |
| 3.9 | 08/07/2026 — C5.8 Task Card #1 (Data Layer) DONE | RENAME struct `S_FolderTargetEntry`→`S_FolderTreeNode` (Depth thay IndentLevel, +HasChildren/ChildCount/ContinuesAncestors/bIsLast). RENAME function `CollectFolderTargets`→`BuildFolderTreeRecursive` (đệ quy, depth guard=12, dùng `AncestorsContinue` thay IndentLevel). Hàm mới `GetFilteredChildren` (Pure, tách filter exclusion ra khỏi recursive function). Wrapper `BuildMoveFolderTargetList`→`BuildComboFolderTreeNodes(ExcludePath)` — **tên đổi so với plan gốc** (plan ghi "BuildFolderTree", trùng tên hàm cũ phía Material/Furniture catalog → đổi). Call site `OnRequestMoveFolder`/`CB_MoveCombo` cập nhật theo tên mới (Blueprint tự propagate qua rename). Test Print PASS trên data thật (8 combo, nested 3 tầng, tiếng Việt) — không lệch. Việc kế tiếp: Task Card #2 (`WBP_FolderTreePicker` UI component). Xem `docs/Sprints/Sprint5/C5.8_FolderTreePicker_Unify_Plan.md`. |
| 3.10 | 08/07/2026 (bổ sung) | Thay node flow "ghi theo suy luận" (v3.9) của `GetFilteredChildren`/`BuildFolderTreeRecursive`/`BuildComboFolderTreeNodes` bằng node flow THẬT (export K2Node) — kèm Local var đầy đủ + Q8 self-check mỗi hàm. Khác biệt nhỏ so với bản suy luận: `GetFilteredChildren` gọi 1 lần/child trong `BuildFolderTreeRecursive` (dùng chung cho `ChildCount`+`HasChildren`, không gọi 2 lần); node "(Gốc)" trong `BuildComboFolderTreeNodes` có `bIsLast=False` (không phải True như suy đoán trước). Test PASS thêm case `ExcludePath="Livingroom/Sofa"`, khớp 100%. Không đổi hành vi/kết luận đã ghi ở v3.9. |
| 3.11 | 13/07/2026 — C5.8 Wire Move + Wire Save | `OnRequestMoveFolder`: `Dialog.InitPicker(Entries, ParentOf(FolderPath), True)` thay `PopulateRows`. `CB_MoveCombo`: `Dialog.InitPicker(Entries, MovingComboCurrentFolder, True)` thay `PopulateRows`. [BUG-FIX] cả 2 call site thực tế vẫn gọi `BuildMoveFolderTargetList` cũ (claim "Blueprint tự propagate" ở v3.9 SAI) — đã fix về `BuildComboFolderTreeNodes`, `BuildMoveFolderTargetList` xoá hẳn khỏi Blueprint. `OpenSaveComboDialog`: xoá `GetExistingFolders`/pin `ExistingFolders`; thêm Branch wire `Picker.SetFolders`/`bShowCurrentTag`/bind `OnRequestCreateFolder`→`HandleSaveDialogCreateFolder`+`Picker.OnRequestCommitRename`→`HandleSavePickerRenameCommitted`. 2 Custom Event mới: `HandleSaveDialogCreateFolder` (tạo folder rỗng qua `CreateEmptyFolder` → expand + `BeginRenameOnPath`), `HandleSavePickerRenameCommitted` (rename qua `RenameFolderPrefix`, KHÔNG gate theo Return Value — xem ghi chú C++). Var mới `SaveDlg_NewFolderPath`. Test PASS: S6a, S6c, M1-M6, Phần 2 test 1-2. |
| 3.12 | 15/07/2026 — P1.G4 wire thumbnail hiển thị | Class var mới `ComboManagerRef` (BP_ComboManager) — set Event Construct (Then 6, Get All Actors Of Class→Get(0)), clear Event Destruct (R4). `LoadComboLibrary` mở rộng: trong ForEach sau build BP_ComboItemView, Branch IsValid(ComboManagerRef) → GetComboThumbnail(Target=ComboManagerRef) → SET view.Thumbnail; nhánh False vẫn Array_Add nhưng bỏ qua SET Thumbnail. ✅ Bug dead-end nhánh False FIXED 15/07/2026 (xem DEVIATIONS 15/07/2026 + Session_State mục P1). |
| 3.13 | 22/07/2026 — Delete Combo | Class var mới `PendingDeleteComboID`. Custom Event mới `RequestDeleteCombo(ComboID, ComboName)` + `HandleDeleteComboConfirmed()` — mirror y hệt `OnRequestDeleteFolder`/`HandleDeleteFolderConfirmed` (Luật 6B). Xóa file `.json`+PNG, `InvalidateThumbnail`, gỡ khỏi Favorite nếu đang favorite, `RemoveRecentCombo` (function mới `BP_FurnitureUserPrefsManager`), Broadcast `OnComboLibraryChanged`. Test 5/5 case PASS. Đính chính: K1 (`WBP_Toast`) CHƯA DONE — `Print String` tạm thay `ShowToastMsg`, thay lại khi K1 xong. |
| 3.14 | 23/07/2026 — K1 (WBP_Toast) DONE | Function mới `ShowToastMsg(Message)` (Get Game Instance → Cast Foff_GameInstance → IsValid(ToastRef) → ShowToast / fallback Print String). 5 call site đổi Print→Toast: `CreateNewFolderFlow` (bOK=False), `HandleDeleteFolderConfirmed`, `HandleMoveComboConfirmed` (bOK=False), `HandleDeleteComboConfirmed` (×2 nhánh — gỡ 2 dòng `[TẠM 22/07]`). **Đính chính as-built quan trọng:** `OnRequestNewFolder` KHÔNG chứa logic trực tiếp như doc cũ mô tả — thực tế chỉ gọi Function riêng `CreateNewFolderFlow` (Target=self), nơi chứa toàn bộ logic thật. Viết lại đúng kiến trúc, tách `OnRequestNewFolder` (wrapper mỏng) và `CreateNewFolderFlow` (Function mới đưa vào doc) thành 2 mục riêng. Sửa 2 annotation `[gate bDebugMode]` sai/lỗi thời (`CreateNewFolderFlow`, `HandleDeleteFolderConfirmed`) — Print gốc thực chạy không điều kiện (gate thật là `EnabledState=Development Only`, không phải Branch). Test K1 5/5 case PASS. Chi tiết: `Widgets/WBP_Toast.md` (mới), `Blueprints/BP_ComboManager.md` (chỗ #6). |
| 3.16 | 30/07/2026 — Folder Highlight Fix + Bug A2 + C9.d (delta "C9 Replace: Folder Highlight + Chip Fix & C9.b–C9.f") | **NODE-VERIFIED:** `FilterByFolderPathWithUI` bước 6 đổi input `FilterByFolderPath` từ `FolderPath` (FULL path) → `ShortPath` (relative, = `Split.RightS`, cùng nguồn dùng chung với chip/breadcrumb) — root cause bug "chỉ node All sáng khi vào Replace bằng code". Chèn `UpdateFolderHighlights()` sau `FilterByFolderPath`, trước `SetText(Breadcrumb)` (luồng code không qua `OnTreeNodeClicked`/`OnChipTagClicked` nên phải tự refresh). **Bug A2:** `OnMeshSelected` nhánh Replace thêm guard `Branch(ReplaceTarget==Mesh)` bên trong `IsReplaceModeActive()==True` — fix tree nhảy về tab Furniture khi đang combo replace (chọn actor thuộc cụm qua `ResolveSelectedComboRoot` trước đó vô tình trigger nhánh mesh). **FUNCTION-LEVEL (chưa re-export node):** `EnterReplaceMode` +4 dòng (`SET CurrentInventoryMode=Furniture`, Collapse `CTV_ComboCard`, Visible `CTV_FurnitureCard`, `UpdateTabHighlight`); Function mới `RefreshComboCardReplaceMode()` (Regenerate `CTV_ComboCard`, mirror `RefreshCardReplaceMode`), gọi từ `StartReplaceComboMode` (`BP_FurnitureInputManager`). Chi tiết: `Blueprints/BP_FurnitureInputManager.md` v2.6, `DEVIATIONS.md`. |
| 3.17 | 01/08/2026 — `FilterByFolderPathWithUI` node-verified | Export K2Node thật xác nhận doc v3.16 thiếu 1 bước + ghi sai loại loop. Thêm bước 1 `SET "Folder Path" (class var) = FolderPath (param)` — chưa từng ghi trước đây. Sửa bước ForEach (nay bước 2): thực tế là `ForEachLoop` thường (nhánh `False` dead-end hợp lệ trong Loop Body, L2), KHÔNG phải `ForEachLoopWithBreak` như doc cũ ghi. Sửa bước Split (nay bước 4): đọc qua `GET "Folder Path"` (class var bước 1), không phải trực tiếp trên param. Verify lại nghi vấn "hàm dựng chiptag ghi nhầm `RebuildChipRowForPath`" — rà toàn bộ docs, KHÔNG tìm thấy vị trí ghi sai, file này đã đúng `CreateChipTagsForPath` từ v3.16. Thêm class var `Folder Path` vào bảng Variables. |
| 3.18 | 01/08/2026 — `CreateChipTagsForPath` sửa nhỏ | Bỏ `→ Visible` thừa sau `Clear Children(VB_ChipTagArea)` (dòng đầu hàm) — câu chữ bị dính nhầm từ đoạn `FilterByFolderPathWithUI` (nơi thật sự có `Clear Children(VB_ChipTagArea) → Visible` ở bước 5) lúc viết doc v3.16, export K2Node thật của `CreateChipTagsForPath` không có node `SetVisibility` nào ở đây. |
| 3.19 | 02/08/2026 — Replace UX Fix P0→P5 HOÀN TẤT | Node-verified qua K2Node export thật (không suy từ doc cũ). `OnMeshSelected`: viết lại hoàn toàn nhánh REPLACE — thêm guard `IsValid(SelectedActor)` (P2, chặn Broadcast deselect rỗng từ `DeselectAll()`), thêm `ResolveSelectedComboRoot()` + route 2 chiều Mesh↔Combo qua `StartReplaceComboMode`/`StartReplaceMode` (P2, thay hẳn guard Bug A2 cũ `Branch(ReplaceTarget==Mesh)` — vá gốc bug #4 thay vì chặn triệu chứng); thêm `SetVisibility(CTV_FurnitureCard/CTV_ComboCard)` ở nhánh mesh cũ (P1.3, fix #5 card container). `OnSceneRestored`: +nhánh song song `Branch(IsReplaceModeActive())` (P4.3) — undo giữa Replace luôn thoát Replace hẳn (quyết định UX (a) cuhoang chốt). `BTN_Close`: +`SET ComboRootGroupIDToReplace=""` (P4.2, đủ 3 biến clear mọi đường thoát), −dòng `SET MeshToReplace=None` (P4.4, biến dead code đã xóa khỏi `BP_FurnitureInputManager`). Thêm cảnh báo Aliasing: `ReplaceTarget` tồn tại 2 bản riêng biệt trùng tên (`BP_FurnitureInputManager` vs `WBP_FurnitureInventory`, xác nhận qua MemberGuid) — không tự đồng bộ. `WBP_ComboCard.OnListItemObjectSet` (gate `BTN_ChangeCombo`, P3.1) — nội dung hiện có trong `WBP_ComboCard.md` v1.6 đã khớp as-built cuối, không cần sửa (xem ghi chú Claude Code). Nguồn: `01-08-2026_ReplaceUX_Fix_Execution_Plan.md`, delta 02/08/2026 (Sonnet). |
| 3.20 | 04/08/2026 12:00 — Save As/Save đè T2 DONE | Đóng `Bug-ReplaceInCombo-TabJump` (gốc rễ: `ResolveSelectedComboRoot()` mù edit-scope). `OnMeshSelected` nhánh REPLACE: đổi ĐÚNG 1 node nguồn dữ liệu — `InputManagerRef.ResolveSelectedComboRoot()` → `InputManagerRef.ShouldRouteReplaceToCombo(SelectedActor)` (hàm mới, ✓K2 03/08, xem `BP_FurnitureInputManager.md` v3.3). GIỮ NGUYÊN 2 node đích `StartReplaceComboMode`/`StartReplaceMode` và mọi node sau chúng (KP3). `ResolveSelectedComboRoot()` KHÔNG bị sửa, vẫn dùng ở C9. Test PASS 6/6 case (`Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 6b.5) — case 4 (thoát edit → chọn cả cụm → Replace) xác nhận hành vi P2 (route Mesh↔Combo) không bị regress. |
| 3.15 | 24/07/2026 — C9.0c HOÀN TẤT | Migrate `bIsReplaceMode` (Boolean) → `ReplaceTarget` (Enum `E_ReplaceTarget`, None/Mesh/Combo) — migration xảy ra ngoài phiên Claude Code, doc trước đây không biết. Pure Function mới `IsReplaceModeActive() → Boolean` (bản riêng, song song với `BP_FurnitureInputManager`). `OnMeshSelected` nhánh Replace: Condition đổi sang `IsReplaceModeActive()` — bug fix (trước là literal EqualEqual đọc biến đã xóa, luôn sai). `EnterReplaceMode`: `SET ReplaceTarget=Mesh` (set cứng Mesh, Combo mode đi đường khác không qua hàm này). `ExitReplaceMode`: `SET ReplaceTarget=None` + THÊM `Regenerate All Entries(CTV_ComboCard)` (đường thoát duy nhất cho cả 2 mode). `BTN_Close` đưa vào doc lần đầu (chưa từng được ghi trước đây). Verify qua K2Node export thật, không suy đoán. Test regression 5/5 PASS. Chi tiết: `Blueprints/BP_FurnitureInputManager.md` v2.5, `Widgets/WBP_MeshControls.md`, `Widgets/WBP_DetailPopup.md`, `Widgets/WBP_FurnitureCard.md`, `Widgets/WBP_ComboCard.md`. |
| 3.21 | 07/08/2026 — Save As/Save đè T3 DONE | **Phần đúng scope command block 07/08:** `OpenSaveComboDialog` — Việc 5 MỚI: sau `Picker.ExpandToPath(PrefillFolder)` thêm `SET Picker.SelectedPath = PrefillFolder` + `Picker.RefreshVisibleRows()` (`ExpandToPath` dùng chung với Move không tự set `SelectedPath`). **Phần backfill hạ tầng 7b/7c (⚠ chưa từng phân phối trước đây, nguồn `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 7b.2/7b.3, ✓K2/✓as-built 05/08):** thêm mục "T3 — Save As/Save Đè — 2 Function mới" (`GetComboViewByID`, `BuildSaveDialogPrefill`); `OpenSaveComboDialog` mở rộng chữ ký +3 param (`ActiveComboID`/`bCanOverwrite`/`ReasonText`) + gọi `BuildSaveDialogPrefill` + `Create Widget` nối thêm 8 pin Expose-on-Spawn của `WBP_SaveComboDialog` v2.1; `BP_ComboItemView.Description` field mới. **CHƯA phân phối** (ngoài scope command block này): việc chèn `ResolveActiveComboForSave()` vào `CB_SaveCombo_Handler` (`BP_FurnitureInputManager`) — xem cảnh báo mục `OpenSaveComboDialog`. Test PASS 6/6 case + 2 câu hiểu bài (`Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 7c). |
| 3.22 | 07/08/2026 (15:40) — Save As/Save đè T4 DONE | `OpenSaveComboDialog`: thêm `Bind SaveComboDialogRef.OnDialogConfirmedOverwrite → HandleSaveComboOverwriteConfirmed`, cạnh bind `OnDialogConfirmed` có sẵn. Custom Event mới `HandleSaveComboOverwriteConfirmed(ComboID, ComboName, FolderPath, Description, Tags)` — đọc `PendingSelectedActors`/`PendingCenter` TRƯỚC cleanup → `ComboManagerRef.SaveComboFromSelection(bOverwrite=true, OverwriteComboID=ComboID)` → `ShowToastMsg("Đã ghi đè combo")` → `OnSaveComboDialogClosed` (tái dùng nguyên vẹn, không viết cleanup riêng). `OnSaveComboDialogClosed` — cập nhật comment nguồn gọi (+ `HandleSaveComboOverwriteConfirmed`), thân hàm không đổi. Test PASS 6/6 case (`Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 7d.5, bao gồm S8 mix combo+mesh rời) + 2 câu hiểu bài. Nguồn: `DELTA_07-08-2026_T4_Overwrite.md` (Opus). |
| 3.23 | 10/08/2026 — C11.2 (Export combo) DONE + DOC-DRIFT FIX | **DOC-DRIFT:** `OnComboCardRightClicked` — bản trước ghi `SET MovingComboID = ComboID`, xác nhận SAI qua K2Node export thật (10/08); code thật ghi thẳng `LibMenu.TargetComboID = ComboID`, không qua `MovingComboID`. **MỚI:** `LibMenu.AddMenuItem("📤 Xuất file…")` → `Item2` → bind `CB_ExportCombo`. Custom Event mới `CB_ExportCombo` — `LibraryMenuRef.Hide` → `UComboSerializer::ExportCombo(LibraryMenuRef.TargetComboID)` → toast kết quả; KHÔNG cần biến tạm lưu ComboID (đọc thẳng `TargetComboID`, dùng ngay trong cùng event — khác `CB_MoveCombo` cần giữ qua tới dialog đóng). Test PASS 3/3 case (path đúng, tên tiếng Việt giữ nguyên M7, thumbnailBase64 nhúng đúng). Kèm bug fix Input Mode phát hiện lúc test — xem `DEVIATIONS.md` mục "[C11.2 — BUG THIẾT KẾ]". Nguồn: `Plans/DELTA_10-08-2026_C11_P4early.md` + test tay 10/08/2026. |
| 3.24 | 10/08/2026 — `CB_MoveCombo` re-export ✓K2, đóng mâu thuẫn `MovingComboID` | Mâu thuẫn tự phát hiện ở v3.23 (`CB_MoveCombo` đọc `MovingComboID` nhưng không nơi nào SET) nay đóng: K2Node export thật xác nhận `SET MovingComboID = LibraryMenuRef.TargetComboID` nằm Ở ĐẦU `CB_MoveCombo`, KHÔNG phải trong `OnComboCardRightClicked` như doc trước 10/08 từng ghi nhầm vị trí. Sửa thêm theo export thật: guard dialog đã mở đổi từ dead-end sang `RemoveFromParent` + `SET MoveComboDialogRef = None` trước khi mở dialog mới; loop tìm folder thêm `IsValid(item)` guard + so sánh trực tiếp `LibraryMenuRef.TargetComboID` (không qua `MovingComboID`); `BuildComboFolderTreeNodes` gọi qua named param `ExcludePath=""`; `Dialog.InitPicker` dùng named param `bInShowTag=True`; cuối hàm đổi `Set Input Mode UI Only` → `Set Input Mode Game and UI Ex (InWidgetToFocus=Dialog)`. `HandleMoveComboConfirmed` không đổi — vẫn đọc `MovingComboID` (nay đã có nguồn SET hợp lệ). Nguồn: K2Node export `CB_MoveCombo`, cuhoang paste 10/08/2026. |
| 3.25 | 10/08/2026 — C11.3 (Import combo) DONE, C11 ĐÓNG HOÀN TOÀN | Custom Event mới `CB_ImportCombo` (bound `BTN_ImportCombo.OnClicked`) — quyết định UX: nút riêng, KHÔNG gắn context menu combo card (Import không thao tác lên 1 combo cụ thể, sai ngữ cảnh nếu gắn menu chuột-phải-trên-combo). Gọi `ImportAllFromExportsDir` → `OutImported`/`OutFailed` → nếu có combo mới: `CallDelegate ComboManagerRef.OnComboLibraryChanged` (⚠ Target PHẢI là `ComboManagerRef`, KHÔNG phải `self` — lỗi compile "Target must have a connection" nếu để `self`, xem `DEVIATIONS.md`) + `RefreshComboFolderUI()` + toast theo 4 nhánh (có lỗi/không lỗi × có nhập được/không). Test PASS 4/4 case (xóa+nhập lại ID mới, file dọn sang `Imported/`, nhập trùng nội dung → 2 ID khác nhau, file rác → toast lỗi không crash không move). Nguồn: session 10/08/2026. |
