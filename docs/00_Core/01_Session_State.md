# Session State
**Nguồn:** `import_raw/Session_State_15jun2026.md` (bản mới nhất — 15/06/2026 20:30 ICT)
> Session_State.md (12/06/2026) là bản cũ hơn — đã merged vào đây.
**Phiên bản:** 20/07/2026 — **P1 Combo Thumbnail DONE về tính năng** (G0→G4, G5 VRAM deferred) — **P2 (Studio Thumbnail) Gate A+B+C DONE**, Gate D: Rim Light + VRAM EndPlay fix DONE, Source Size Key=500 chốt, sweep 5 combo 3/5 PASS — TẠM DỪNG (2 bug kiến trúc mới OPEN, chờ Fable/Opus quyết dome curvature + Ceiling ground-align, xem mục P2) | C5.8 (Folder Tree Picker Unify) CHÍNH THỨC DONE (13/07) | WBP_FurnitureInventory v3.11

---

## TRẠNG THÁI HIỆN TẠI

**Sprint D — HOÀN THÀNH ✅ (17/06/2026) + TreeNode/Chip Highlight ✅ (18/06/2026)**
**Sprint 5 — Combo Mesh 🔄 IN PROGRESS (21/06/2026)**

### Sprint 5 — Combo Library (21/06/2026 EOD)

| Task | Nội dung | Status |
|---|---|---|
| T1 | C++ structs FComboData/FComboGroupData/FComboItemData + ComboSerializer — schema v1, round-trip JSON PASS | ✅ DONE |
| T2 | BP_ComboManager tách riêng, SaveComboFromSelection, CB_SaveCombo context menu | ✅ DONE |
| T3 | BP_ComboItemView, LoadComboLibrary, bind OnComboLibraryChanged | ✅ DONE |
| C1 | FComboData.FolderPath (C++), FindMaterialRowNameByPath (C++), S_GroupData.SourceComboID (BP), FavoriteComboIDs/RecentComboIDs (UserPrefs) | ✅ DONE |
| C0 | SaveComboFromSelection nested — LCA (CalculateLCAList_Combo + GetGroupsInHierarchy) + MaterialOverrides → RowName | ✅ DONE (22/06) — 3 case A/B/C PASS + RowName fallback (đồ cũ parse MeshPath) |
| C2 | SpawnComboByID — Guard, F_LoadComboData, F_BuildTokenGUIDMap, F_RegisterComboGroups, F_ApplyMaterialOverrides, 4 sub-steps | ✅ DONE (22/06) — 7/7 PASS |
| C3a | Data layer: AuthorID+Visibility (C++), BP_ComboItemView.FolderPath, LoadComboLibrary wire FolderPath, SaveComboFromSelection mở rộng (FolderPath+Tags+AppVersion), GetExistingFolders+GetAllUsedTags (WBP_FurnitureInventory) | ✅ DONE (23/06) |
| C3b | WBP_SaveComboDialog: Expose on Spawn (ExistingFolders, TagVocabulary), bIsCreatingNewFolder, dispatcher OnDialogConfirmed/OnDialogCancelled, ValidateComboName, ParseTags, BTN_NewFolder toggle. CB_SaveCombo → OpenSaveComboDialog (inventory đóng băng selection + Set Input Mode UI). OnSaveComboConfirmed → SaveComboFromSelection → OnSaveComboDialogClosed (trả Game+UI). | ✅ DONE (24/06) |
| C4 | WBP_ComboCard + BP_DragDropOperation_ComboCard + BP_ComboGhostActor v1.1 + M_ComboGhost + CalculateComboAnchor + WBP_DragOverlay v1.8 (ghost offset Approach B FIXED) + CTV_ComboCard (19 combo PASS). | ✅ 100% DONE (25/06) |
| C8 | Drag-drop + surface-snap → **MERGED vào C4** | ✅ MERGED (24/06) |
| C5.1 | C++ 3 helper folder: UpdateComboFolder / RenameFolderPrefix / ClearFolderPrefix (ComboSerializer). Test PASS: UpdateComboFolder→true, Rename→1, Clear→1. JSON folderPath đổi đúng, tiếng Việt OK. | ✅ DONE (25/06) |
| C5.0 | Folder tree + filter browse: BuildComboFolderTree, PopulateComboTreeColumn (2 cấp + D9 guard), FilterComboByFolder, OnComboTreeNodeClicked (branch IndentLevel), OnComboChipTagClicked, OnComboTreeNodeRightClicked → WBP_LibraryContextMenu. WBP_TreeNode v1.2 (OnNodeRightClicked + On Mouse Button Down). Test end-to-end PASS 26/06. | ✅ DONE (26/06) |
| C5.2 | Inline rename folder: WBP_EditableLabel v1.0 (component Overlay+validate+EnterEditMode+ExitEditMode+OnEditBoxCommitted). WBP_TreeNode v1.3 (EditableLabel_Name + OnNodeRenameCommitted + EnterRenameMode). WBP_FurnitureInventory v3.3 (3 helpers ParentOf/LastSegmentOf/GetSiblingFolderNames; OnRequestRenameFolder implement; OnRenameFolderCommitted; CB_RenameFolder; 3 class vars). BUG FIX: RefreshComboFolderUI +PopulateComboTreeColumn (C5.0 thiếu nối). 6 test PASS. | ✅ DONE (27/06/2026) |
| C5.4 | Move Folder: S_FolderTargetEntry struct mới (Path/DisplayLabel/IndentLevel). WBP_MoveFolderRow (Horizontal Box + Spacer_Indent + Button_Row; SetRow/SetHighlight/OnRowClicked). WBP_MoveToFolderDialog (Canvas + Border_Dim full-screen + Border_Content; PopulateRows/HandleRowSelected; dispatcher OnMoveFolderConfirmed). WBP_FurnitureInventory v3.4: MovingFolderPath class var; CollectFolderTargets đệ quy + loại MovingPath+con cháu; BuildMoveFolderTargetList (wrap + entry "(Gốc)"); OnRequestMoveFolder implement; CB_MoveFolderClick implement; HandleMoveFolderConfirmed NEW (tính NewFullPrefix, guard no-op, cập nhật CurrentComboFolderPath, RenameFolderPrefix+RefreshComboFolderUI). BUG FIX D-C5.4-1 (Array_Append ngược) + D-C5.4-2 (dead-end nhánh True). | ✅ DONE (30/06/2026) |
| Issue 2 | Chip highlight on selection (combo side): UpdateComboFolderHighlights() NEW trong WBP_FurnitureInventory v3.5 — mirror UpdateFolderHighlights dùng CurrentComboFolderPath. Inline check (fp==Current OR Current StartsWith fp+"/") cho TreeNode + ChipTag. | ✅ DONE (01/07/2026 — trước session Move Combo) |
| C5.5 | Move Combo: WBP_ComboCard v1.1 (+InventoryRef lazy-init + On Mouse Button Down RMB→OnComboCardRightClicked). WBP_FurnitureInventory v3.5: 3 class var (MoveComboDialogRef/MovingComboID/MovingComboCurrentFolder); OnComboCardRightClicked NEW (tạo context menu Combo mode); CB_MoveCombo NEW (guard stacking + ForEachLoopWithBreak tìm folder hiện tại + tạo WBP_MoveToFolderDialog + bind HandleMoveComboConfirmed); HandleMoveComboConfirmed NEW (close dialog + guard no-op + UpdateComboFolder C++ + RefreshComboFolderUI). BUG FIX 4.1 (delimiter ",") + 4.2 (bỏ Map_Contains) + 4.3 (+UpdateComboFolderHighlights). | ✅ DONE (01/07/2026) |
| NF | New Folder — context menu part: C++ `GetEmptyFoldersFilePath`→`Folders.json` + `GetAllFolderPaths` tự ghi bổ sung folder path (kể cả cấp cha) — test PASS 6/6. `BuildComboFolderTree` đổi nguồn sang `GetAllFolderPaths` (1 nguồn duy nhất) — test PASS 4/4. WBP_FurnitureInventory v3.6: `GetChildFolderNames`/`GetUniqueNewFolderName`/`GetNewFolderParent` (helpers) + `OnRequestNewFolder` + `CB_CreateNewFolder` (menu item đầu chuỗi "Create New Folder", tạo CÙNG CẤP node bị right-click, tự vào rename mode qua `OnRequestRenameFolder`). Test PASS 9/9. | ✅ DONE (04/07/2026) |
| NF.G3 | Nút "+" đầu cột tree: `PopulateComboTreeColumn` +PlusNode (sentinel `__NEWFOLDER__`, đầu tiên) + `OnComboTreeNodeClicked` +guard đầu tiên → `OnRequestNewFolder(GetNewFolderParent())`. Không hàm mới — tái dùng NF context-menu (04/07). Test PASS 5/5. | ✅ DONE (06/07/2026) |
| C5.6 | Xóa folder: `WBP_ConfirmDialog` mới (generic Yes/No, dùng lại được). WBP_FurnitureInventory v3.7: class var `PendingDeleteFolderPath`; `OnRequestDeleteFolder` implement; `HandleDeleteFolderConfirmed` NEW (ClearFolderPrefix C++ + navigate); `CB_DeleteFolderClick` implement. Deviation D-C5.6-1 (nhảy về folder CHA thay vì `__ALL__`). Test PASS 6/6. | ✅ DONE (06/07/2026) |
| C5.7a | ChipTag right-click → context menu: WBP_ChipTag v1.2 (+dispatcher `OnChipRightClicked` + On Mouse Button Down override) bind → `OnComboTreeNodeRightClicked` (tái dùng, không logic mới). Test PASS 3/4 (rename từ chip = C5.7b, chưa làm). **Phát sinh:** `RebuildChipRowForPath` + `RefreshChipBreadcrumb` (gộp code ChipRow trùng lặp + fix chip area không tự refresh sau Move/Xóa/Rename) — 3 bug fix kèm theo. | ✅ DONE (06/07/2026) |
| C5.7b | Inline rename chip (WBP_EditableLabel embed) + fallback OnRequestRenameFolder tree→chip. BUG FIX CB_CreateNewFolder (dead SET node) + CB_RenameFolder (thiếu SET None). Test PASS full case. | ✅ DONE (06/07/2026) |

**C5 — FOLDER MANAGEMENT: TOÀN BỘ HOÀN TẤT.**

**C0:** 3 case A/B/C PASS (22/06). RowName fallback (đồ cũ parse MeshPath) xác nhận OK.
**C2:** 7/7 PASS (22/06). Group nesting: Case A (no groups→wrapper) / Case B (has groups→no wrapper, root nhận SourceComboID).
**Pending T2:** WBP_SaveComboDialog (dialog nhập tên) — dời sau T5, không chặn spawn
**Ghi chú kiến trúc:** BP_ComboManager đã spawn trong Level BP; InputManager guard (≥2 đồ, tính Center) → gọi ComboManager qua param (SelectedActors, Center, ComboName, Description)

---

### Sprint 4 Bug Fix (F1–F4 + A12) — ĐẦY ĐỦ PASS

| Fix | Nội dung | Status |
|---|---|---|
| F1 | Info bar hiển thị đúng unit name (GetSelectionUnitLabel) | ✅ PASS |
| F2 | Group name counter monotonic (GroupNameCounter → BP_GroupsContainer) | ✅ PASS |
| F3 | CreateGroup bottom-up nesting (ComputeSelectionUnits + rewrite) | ✅ PASS |
| F4 | Spawn auto-join edit scope (SpawnFurnitureCopy + DragOverlay On Drop) | ✅ PASS |
| A12 | Edit mode bar ẩn sau Undo (EditModeStack vào snapshot V=4) | ✅ PASS |

**Full test suite (30+ cases + Regression S1-S3) — ALL PASS ✅**

### Bugs đã giải quyết trong session này
- B3 (gizmo ẩn sau undo trong edit mode): xác nhận **pre-existing**, không phải regression Sprint 4. Ghi nhận known issue.
- A12 root cause: EditModeStack là runtime state, không nằm trong snapshot → undo không khôi phục edit state → fix bằng cách đưa EditModeStack vào S_SceneSnapshot (Version=4).

---

## BUG CÒN MỞ

| # | Bug | Ưu tiên | Xử lý |
|---|---|---|---|
| B1 | ✅ FIXED (16/06) — bIsRestoring guard + spawn merge | — | Đã đóng Gate 1, xem BP_UndoManager.md v1.9-1.10 |
| B-gizmo | Gizmo ẩn sau undo trong edit mode (pre-existing) | 🟢 Thấp | Known issue, chưa có timeline |
| B-folder | ✅ FIXED (17/06, D.T6) — Replace folder sai khi group nhiều mesh | — | OnMeshSelected RowName→DT, fallback DAPath save cũ |
| B-stale-popup | ✅ FIXED (17/06, D.T6) — Popup hiển thị đồ cũ | — | UpdateDetailPopup bound OnSelectionChanged |
| B-ghost-offset | ✅ FIXED (25/06) — Approach B: On Drag Over set ghost = HitLocation+(0,0,GhostExtentZ); On Drop trừ GhostExtentZ. BP_ComboGhostActor v1.1, WBP_DragOverlay v1.8. | — | Đã đóng. |
| B-C5-card | ✅ FIXED (26/06) — Card render PASS sau khi fix Set List Items + verify Entry Widget Class = WBP_ComboCard. | — | Đã đóng. |
| Bug-Pagination | ✅ FIXED (17/06, D.T9) — Furniture pagination dừng sớm 1 trang | — | Int to Float trước Ceil ở Next-page check |
| Bug-Maximize | ✅ FIXED (17/06, D.T9) — BTN_Maximize không nhảy về góc trên-trái | — | Set Position thêm vào Slot VerticalBox_0 |
| Fix-5.2-async | ✅ FIXED (19/06) — aliasing shared latent khi spawn nhiều actor dồn | — | LoadMeshAsync/LoadMaterialsAsync đặt trong BP_FurnitureActor thay InputManager; NewActorCopy → local var |

---

## ĐÃ HOÀN THÀNH

- Change Material v1.1 (20/05/2026)
- UX Phase 2.1: Gizmo, Nudge, Copy/Paste, Recent/Favorite
- Resize Window 8 hướng
- Sprint 1 — Multi-select (15/15) ✅
- Sprint 2 — Box+Context Menu (9/9) ✅
- Sprint 3 — Group cơ bản (12/12 + 10 bug fix) ✅
- Sprint 4 — Edit Mode + Nested Group (T1-T8 + 2 bug fix) ✅
- **Sprint 4 Bug Fix Session (F1-F4 + A12, 15/06/2026) ✅**
- **Gate 1 (G1.1-G1.3, 16/06/2026) ✅**
- **Sprint D — Data Layer v2 (D.T1-D.T9, 17/06/2026) ✅**
- **TreeNode/Chip active-folder highlight (18/06/2026, tính năng bổ sung) ✅**
- **Sprint 5 T1+T2+T3+C1 (21/06/2026) ✅** — ComboTypes C++, ComboSerializer, BP_ComboItemView, LoadComboLibrary, FolderPath, FindMaterialRowNameByPath, SourceComboID, Favorite/RecentComboIDs
- P2 Gate A (Studio Thumbnail vertical slice): Việc 1-4 DONE, TEST PASS 6/7 case (case 7 — tắt PIE giữa Delay — dời kiểm tra sang Gate F). Chi tiết: P2_StudioThumbnail_Execution.md.

### VRAM Fixes (19/06/2026)
- Giai đoạn 1: Xác nhận card là RTX 3060 8GB (không phải 12GB). Budget UE = 7.26GB. Workaround: dùng Standalone Game (Alt+P) thay PIE cho session dài — mỗi lần tắt OS reclaim VRAM sạch 100%. Peak VRAM lúc chạy = 7.2/8.0GB, không cộng dồn qua nhiều lần launch. ✅ PASS
- Fix 5.3: Material dedup trong ApplyMaterial (WBP_FurnitureInventory). Branch Is Valid Index + Equal String trước khi gọi LoadAndApplyMaterial — nếu material đã áp đúng slot thì bỏ qua, không fire Async Load lại. ✅ PASS
- Việc 1: Add Recent Mesh trong SpawnFurnitureCopy đổi nguồn parse từ DAPath (rỗng với đồ Sprint D) sang MeshPath — parse theo '/' lấy phần cuối, tách '.' lấy index 0 = RowName. ✅ PASS
- Fix 5.2: Async Load mesh + material trong SpawnFurnitureCopy. Chuyển từ Load Asset Blocking sang Custom Event LoadMeshAsync + LoadMaterialsAsync đặt TRONG BP_FurnitureActor (không phải InputManager). Mỗi actor tự load asset của chính nó — tránh aliasing shared class var/latent context khi nhiều actor spawn dồn. NewActorCopy đổi từ class var → local var trong SpawnFurnitureCopy. ✅ PASS

---

## KIẾN TRÚC HIỆN TẠI

**BP_FurnitureInputManager v2.1** — SpawnFurnitureCopy async load (LoadMeshAsync/LoadMaterialsAsync); NewActorCopy local var; Add Recent Mesh parse MeshPath
**BP_UndoManager v1.10** — bIsRestoring guard + SpawnFurnitureCopy merge
**BP_FurnitureActor v1.2** — RowName : Name (SaveGame), GroupID confirmed SaveGame
**WBP_DetailPopup v1.2** — InitPopup(RowName), RowData : S_FurnitureData
**WBP_MeshControls v1.7** — BTN_Info RowName, UpdateDetailPopup bound OnSelectionChanged
**WBP_FurnitureCard v1.0** — TẠO MỚI, CardRowName, BP_FurnitureItemView, DT lookup
**WBP_DragOverlay_FurnitureCard v1.6** — PendingRowName, F_ExecuteReplace RowData
**WBP_FurnitureInventory v2.5** — OnCardInfoClicked(RowName), OnMeshSelected RowName branch
**FilterByCategory_Logic v1.3** — Recent/Favorite DT direct (bỏ inner loop AllFurnitureItems)
**FilterBySearch_Logic v1.3** — FilterFurnitureRows + AllFilteredFurnitureRows → DisplayPage
**WBP_FurnitureInventory v2.6** — IsPathActive (Pure) + UpdateFolderHighlights + Fix Bug-Pagination
**WBP_TreeNode v1.1** — RefreshDisplay + bIsActive param → SetBackgroundColor
**WBP_ChipTag v1.1** — SetHighlight(bIsActive) custom event → SetBackgroundColor
**WBP_ResizeWindow v1.1** — Fix Bug-Maximize: Set Position thêm vào Slot VerticalBox_0
**BP_ComboManager v1.5** — SaveComboFromSelection (LCA path) + SpawnComboByID + CalculateComboBoundingExtent; spawn trong Level BP. [C0 ✅ + C2 ✅ + C4 ✅ (22-24/06)]
**BP_FurnitureInputManager v2.3** — CalculateComboAnchor (center-bottom sàn / center-top trần); CB_SaveCombo_Handler đổi từ CalculateCenter → CalculateComboAnchor
**BP_ComboItemView v1.1** — BoundingBoxExtent : Vector (C4)
**WBP_DragOverlay_FurnitureCard v1.7** — PreviewActorRef → Actor; On Drag Over Cast branch; On Drop combo = GetActorLocation(PreviewActorRef) → SpawnComboByID (không trace)
**WBP_FurnitureInventory v2.9** — CTV_ComboCard (TileView Collapsed); LoadComboLibrary + CTV wiring (24/06)
**WBP_ComboCard v1.1** — TẠO MỚI (24/06): OnListItemObjectSet, OnDragDetected → spawn BP_ComboGhostActor + BP_DragDropOperation_ComboCard. v1.1 (01/07): +InventoryRef (WBP_FurnitureInventory, lazy-init từ GameInstance.FurnitureInventoryRef trong OnListItemObjectSet); +On Mouse Button Down override (RMB → InventoryRef.OnComboCardRightClicked(ComboID) → return Handled; LMB → return Unhandled không phá drag-drop)
**BP_DragDropOperation_ComboCard** — TẠO MỚI (24/06): ComboID : String, ComboExtent : Vector
**BP_ComboGhostActor v1.1** — GhostExtentZ var; InitGhost lưu GhostExtentZ; ghost offset FIXED (Approach B, 25/06)
**M_ComboGhost** — TẠO MỚI (24/06): Translucent Unlit xanh trong
**WBP_DragOverlay_FurnitureCard v1.8** — On Drag Over: CastFailed→Cast ComboGhost→+GhostExtentZ; On Drop combo: −GhostExtentZ
**WBP_FurnitureInventory v3.0** — E_InventoryMode +Combo; C5.0 folder tree 6 functions; BTN_Tab_Combo
**WBP_FurnitureInventory v3.2** — C5.0 DONE: PopulateComboTreeColumn 2-cấp+D9 guard, OnComboTreeNodeClicked rewrite, OnComboChipTagClicked (params mới), OnComboTreeNodeRightClicked NEW, 3 stubs (C5.2/C5.4/C5.5)
**WBP_TreeNode v1.2** — OnNodeRightClicked dispatcher + On Mouse Button Down override (Handled/Unhandled)
**WBP_LibraryContextMenu v1.0** — TẠO MỚI (26/06): clone WBP_ContextMenu; 3 vars + 4 dispatchers; Btn_Background Z-order fix (index 0)
**WBP_EditableLabel v1.0** — TẠO MỚI (27/06): component inline rename. Overlay TextBlock_Label+EditBox+Border_Error. ValidateName (empty/slash/dupe). EnterEditMode+Delay(0.0). ExitEditMode guard bIsEditing. OnEditBoxCommitted Switch.Selection pin critical.
**WBP_TreeNode v1.3** — C5.2: TextBlock_71→EditableLabel_Name; OnNodeRenameCommitted dispatcher; EnterRenameMode; HandleLabelCommitted relay; RefreshDisplay SetText→SetLabel. Additive.
**WBP_FurnitureInventory v3.3** — C5.2: 3 helpers (ParentOf/LastSegmentOf/GetSiblingFolderNames); OnRequestRenameFolder implement; OnRenameFolderCommitted; CB_RenameFolder; class vars RenameTargetNode/NewFullPrefix/LibraryMenuRef. PopulateComboTreeColumn: bind OnNodeRenameCommitted. BUG FIX: RefreshComboFolderUI +PopulateComboTreeColumn.
**S_FolderTargetEntry** — TẠO MỚI struct: Path (String), DisplayLabel (String), IndentLevel (Integer). Dùng cho list chọn folder đích.
**WBP_MoveFolderRow** — TẠO MỚI (30/06): Horizontal Box [Spacer_Indent + Button_Row[TextBlock_Row]]. SetRow(Path, DisplayLabel, Indent) — indent = Indent×20px. SetHighlight(bSelected). Dispatcher OnRowClicked(TargetPath).
**WBP_MoveToFolderDialog** — TẠO MỚI (30/06): Canvas [Border_Dim full-screen + Border_Content center ~420×480 → Vertical Box[Title + ScrollBox_FolderList + Cancel/Confirm]]. PopulateRows(Entries) đổ WBP_MoveFolderRow vào ScrollBox. Chọn 1 dòng → highlight + enable Confirm. Dispatcher OnMoveFolderConfirmed(TargetParentPath). BTN_Cancel tự trả Input Mode Game+UI.
**WBP_FurnitureInventory v3.4** — class var mới: MovingFolderPath (String). Function mới: CollectFolderTargets(ParentPath, IndentLevel, MovingPath) — đệ quy, trả Array<S_FolderTargetEntry>, loại MovingPath + con cháu. BuildMoveFolderTargetList(MovingPath) — wrap CollectFolderTargets + thêm entry "(Gốc)" đầu list. OnRequestMoveFolder(FolderPath) — implement (đã STUB từ C5.0): build list → mở dialog → bind OnMoveFolderConfirmed → HandleMoveFolderConfirmed. CB_MoveFolderClick — implement (đã STUB): Hide menu → OnRequestMoveFolder. HandleMoveFolderConfirmed(TargetParentPath) — NEW: tính NewFullPrefix (tái dùng var có sẵn từ C5.2) → guard no-op → cập nhật CurrentComboFolderPath (2 nhánh: match đúng path / là con của path) → RenameFolderPrefix (C++) → RefreshComboFolderUI.
**WBP_FurnitureInventory v3.5** — 3 class var mới: MoveComboDialogRef/MovingComboID/MovingComboCurrentFolder. UpdateComboFolderHighlights() NEW (Issue 2). OnComboCardRightClicked(ComboID) NEW. CB_MoveCombo NEW. HandleMoveComboConfirmed(TargetParentPath) NEW: close dialog + guard no-op + UpdateComboFolder C++ + RefreshComboFolderUI. BUG FIX 4.1 (delimiter) + 4.2 (Map_Contains) + 4.3 (UpdateComboFolderHighlights call in RefreshComboFolderUI).
**WBP_FurnitureInventory v3.6** — NF context-menu: `GetChildFolderNames`/`GetUniqueNewFolderName`/`GetNewFolderParent` (Pure helpers); `OnRequestNewFolder(ParentPath)` NEW (GetUniqueNewFolderName → CreateEmptyFolder C++ → RefreshComboFolderUI → OnRequestRenameFolder, tái dùng rename phase C5.2); `CB_CreateNewFolder` NEW (cache TargetFolderPath trước Hide, ParentOf → OnRequestNewFolder); `OnComboTreeNodeRightClicked` thêm menu item "Create New Folder" đầu chuỗi. KHÔNG CaptureSnapshot, KHÔNG navigate (NF-C3).
**WBP_FurnitureInventory v3.7** (06/07) — NF.G3: `PopulateComboTreeColumn` +PlusNode (sentinel `__NEWFOLDER__`); `OnComboTreeNodeClicked` +guard đầu. C5.6: class var `PendingDeleteFolderPath`; `OnRequestDeleteFolder` implement + `HandleDeleteFolderConfirmed` NEW + `CB_DeleteFolderClick` implement (Deviation D-C5.6-1: nhảy về cha thay vì `__ALL__`). C5.7a: bind `WBP_ChipTag.OnChipRightClicked` → `OnComboTreeNodeRightClicked`. Refactor: `RebuildChipRowForPath` + `RefreshChipBreadcrumb` (hàm mới, gộp code ChipRow trùng lặp + fix chip area không tự refresh) — `RefreshComboFolderUI` gọi `RefreshChipBreadcrumb` sau `UpdateComboFolderHighlights` cả 3 nhánh.
**WBP_FurnitureInventory v3.8** (06/07 tối) — C5.7b: class var `RenameTargetChip`; `OnRequestRenameFolder` mở rộng fallback tree→chip (double-break qua Completed loop lồng khi không tìm thấy TreeNode khớp); `RebuildChipRowForPath` +bind `OnChipRenameCommitted`→`OnRenameFolderCommitted`. BUG FIX `CB_CreateNewFolder` (node SET thừa đè cache → luôn tạo root); BUG FIX `CB_RenameFolder` (thiếu SET LibraryMenuRef=None cuối chuỗi). **C5 HOÀN TẤT.**
**WBP_ChipTag v1.2** (06/07) — TẠO MỚI dispatcher `OnChipRightClicked(FolderPath)` + override `On Mouse Button Down` (pattern WBP_TreeNode, nhánh False trả Unhandled vì root là Horizontal Box).
**WBP_ChipTag v1.3** (06/07 tối) — `EditLabel_ChipTag` (WBP_EditableLabel) thay `TextBlock_ChipTag`; `EnterRenameMode`/`HandleLabelCommitted` NEW; dispatcher `OnChipRenameCommitted`.
**WBP_ConfirmDialog** — TẠO MỚI (06/07): dialog xác nhận generic (Yes/No), Expose on Spawn Message/ConfirmLabel, dispatcher OnConfirmed. Dùng đầu tiên cho C5.6 Xóa folder.
**S_GroupData** — ✅ field `SourceComboID : String` (default "") đã thêm (C1 DONE). Group cha cụm combo = ComboID gốc; group user tạo tay = "". Đã add vào snapshot capture/restore.
**C++ FurnitureToolkit** — FComboData.FolderPath (field mới), FindMaterialRowNameByPath (function mới). Compile xanh. Full rebuild (Binaries/Intermediate xóa + rebuild) ✅
**BP_FurnitureInputManager** — SpawnFurnitureCopy +param bAddToRecent : Bool = True (default, Branch bọc khối AddRecentMesh trong Sequence.Then_2, dead-end hợp lệ)
**BP_ComboManager** — SpawnComboForThumbnail(ComboID, DeltaYaw=0) Custom Event MỚI (P2 Gate A): guard Cmb_bThumbBusy → F_LoadComboData → ForEach Items → SpawnFurnitureCopy (bAutoSelect=False, bAddToRecent=False) → strip tag "FurnitureSpawned" → GroupID="" → Cmb_StudioClones. Biến mới: Cmb_StudioClones, Cmb_bThumbBusy, Cmb_StudioAnchor, Cmb_StudioFloor, Cmb_ThumbMinZ, Cmb_CaptureHandle (P1, tái dùng).
**BP_ComboManager** — chuỗi debug phím U (Input Event, gate bDebugMode + bDebugTestThumb ở BeginPlay EnableInput): SpawnComboForThumbnail → Delay(3.0, tạm — xem DEVIATIONS) → ground-align (ForEach tính Cmb_ThumbMinZ qua Get Actor Bounds, DeltaZ = Cmb_StudioAnchor.Z − Cmb_ThumbMinZ, ForEach Add Actor World Offset) → BeginComboCapture → Delay(3.0) → FinishComboCapture → ForEach Destroy → Clear.
**BeginPlay BP_ComboManager** — Spawn sàn tạm (StaticMeshActor, mesh Plane, scale 50×50×1, location=Cmb_StudioAnchor) chạy VÔ ĐIỀU KIỆN (KHÔNG nằm trong Branch bDebugTestThumb — quyết định 17/07, tránh coupling ẩn với ground-align).
**BP_ComboManager** — Gate B (dome, thay sàn plane Gate A): BeginPlay spawn `/Engine/BasicShapes/Sphere` R=`Cmb_StudioDomeRadius` (2000.0), Location Z = Cmb_StudioAnchor.Z + R, Scale = R/50 cả 3 trục (1 phép chia qua Make Vector). Material `M_StudioBackdrop` (Lit/Two-Sided/Roughness 0.9, màu CHƯA chốt — dời đợt tối ưu cuối). **Cast Shadow = False** trên dome (quyết định kiến trúc quan trọng nhất Gate B — dome chỉ nhận bóng, không chặn sáng đèn ngoài bán kính R). Receive Shadow giữ nguyên.
**BP_ComboManager** — Gate C: Function mới `SpawnStudioLight(AngleOffsetDeg, Intensity) → RectLight` (Q8 đầy đủ, Return Node cả 2 nhánh) — RotateAngleAxis((1500,0,1500), AngleOffsetDeg, Z-up) làm LightOffset, WorldLoc = Cmb_StudioAnchor + LightOffset, spawn RectLight Mobility=Movable (bắt buộc — Stationary phụ thuộc Lightmass bake, Remote Studio runtime chưa bake), FindLookAtRotation về anchor, Source Width/Height=150, Attenuation Radius=8000. Gọi 2 lần ở BeginPlay: `SpawnStudioLight(45.0, 5000000.0)` → Cmb_StudioKeyLight, `SpawnStudioLight(-45.0, 1666667.0)` → Cmb_StudioFillLight. Biến mới: Cmb_StudioDomeRadius (Float, 2000.0), Cmb_StudioKeyLight/Cmb_StudioFillLight (RectLight ref). Biến đã xoá (refactor thành Local trong function): KeyOffset, FillOffset.
**BP_ComboManager** — chuỗi debug phím U cập nhật Gate C: `Begin Combo Capture` tick `bUseFixedAngle=True`, `FixedAngle=(Pitch=-15, Yaw=0, Roll=0)` (trước đó bị bỏ sót); thêm `IsValid(Cmb_CaptureHandle)` guard ngay sau Begin (False → Print + SET Cmb_bThumbBusy=False, tránh kẹt "Thumb busy" vĩnh viễn); Manual EV100 set qua `Get Post Process Settings` (đọc struct hiện có từ Capture Component) → `Set members in Post Process Settings` (chỉ Metering Mode + Exposure Compensation) → `Set Post Process Settings` — KHÔNG dùng `Make Post Process Settings` (sẽ ghi đè mất 2 field Lumen override C++ đã set).

**Snapshot version history:**
- V1: single select (legacy)
- V2: multi-select (Sprint 1)
- V3: Groups (Sprint 3)
- V4: Groups + EditModeStackSnapshot (Sprint 4 Bug Fix, 15/06/2026)

---

## TIẾP THEO

**ĐẦU SESSION MỚI — Ưu tiên (backlog C5, thứ tự đã chốt 30/06/2026 — cập nhật 06/07):**
1. ✅ **Issue 2 — Chip highlight on selection**: `UpdateComboFolderHighlights()` — DONE (01/07, trước session Move Combo).
2. ✅ **Move Combo** (right-click `WBP_ComboCard`): tái dùng `WBP_MoveToFolderDialog`, gọi `UpdateComboFolder(ComboID, path)` C++. WBP_ComboCard v1.1 + WBP_FurnitureInventory v3.5. DONE (01/07).
3. ✅ **Tạo folder mới — context menu part** (NF.G0/G1 + helpers + `OnRequestNewFolder`/`CB_CreateNewFolder`): tạo CÙNG CẤP node bị right-click, tên mặc định "New Folder" (auto hậu tố trùng), tự vào inline rename mode (tái dùng C5.2). WBP_FurnitureInventory v3.6. DONE (04/07). Deviation: UX đổi từ dialog (plan gốc NF.G2-G5) sang inline — xem DEVIATIONS.md 04/07.
4. ✅ **Nút "+" đầu cột tree** (NF.G3) — DONE (06/07): sentinel node `__NEWFOLDER__` trong `PopulateComboTreeColumn`, guard đầu `OnComboTreeNodeClicked` → `GetNewFolderParent` → `OnRequestNewFolder`. Khác context-menu: tạo TRONG folder đang xem (không phải cùng cấp node bị click).
5. ✅ **Xóa folder** (C5.6) — DONE (06/07): `WBP_ConfirmDialog` mới (generic Yes/No) + `HandleDeleteFolderConfirmed` (gọi `ClearFolderPrefix` C++ đã có từ C5.1). Deviation D-C5.6-1: nhảy về folder CHA thay vì `__ALL__`.
6. ✅ **ChipTag right-click + rename (C5.7)** — C5.7a DONE (06/07, right-click + context menu, tái dùng `OnComboTreeNodeRightClicked`). C5.7b DONE (06/07, inline rename trong chip, nhúng `WBP_EditableLabel` + fallback `OnRequestRenameFolder` tree→chip). **C5 — FOLDER MANAGEMENT: TOÀN BỘ HOÀN TẤT.**

→ **REG (regression 12 bước)** → C5 chốt sổ hoàn toàn → **C5.8 (Folder Tree Picker Unify)** → C6/C7 (defer) hoặc WBP_Toast → C9.

**C5.8 — Folder Tree Picker Unify** ✅ DONE (13/07/2026, REG PASS). Gộp lõi data+component cho `WBP_MoveToFolderDialog` + `WBP_SaveComboDialog` (tree picker có guide line/search/inline-create, thay `WBP_MoveFolderRow` + folder-field cũ của Save). Chi tiết đầy đủ + Task Card: `docs/Sprints/Sprint5/C5.8_FolderTreePicker_Unify_Plan.md`.
- ✅ **Task Card #1 (Data Layer)** — DONE (08/07): rename `S_FolderTargetEntry`→`S_FolderTreeNode` (+4 field mới); `CollectFolderTargets`→`BuildFolderTreeRecursive` (đệ quy, depth guard=12) + hàm mới `GetFilteredChildren`; wrapper `BuildComboFolderTreeNodes(ExcludePath)` (tên đổi khác plan gốc — trùng tên hàm cũ Material/Furniture catalog). Test Print PASS (8 combo, nested 3 tầng, tiếng Việt). WBP_FurnitureInventory v3.9.
- ✅ **Task Card #2 (UI component, 2a→2d rename host) + Wire Move + Wire Save** — DONE (13/07): build + test node-level xong, trả nợ test toàn bộ (M1-M6, S6a-c, 0.3, Phần 2 test 1-2). WBP_FurnitureInventory v3.11.
- ✅ **REG (Khối A/B/C/D)** — PASS (13/07/2026): A1-A7, B1-B4, C1 SKIP (rủi ro thấp)/C2-C5, D5 comprehension check. 2 bug mới ghi `Bugs/Open_Bugs.md` (ngoài scope C5.8): Bug-SaveConfirm-EmptyName, Bug-MoveFolder-Collision. Chi tiết: `PROGRESS.md`, `DEVIATIONS.md` 13/07/2026 (REG).

### P1 — Combo Thumbnail (Thumbnail System C++)

Gate G0-R: DONE (14/07/2026) — one-shot capture (G0 gốc) bị loại bỏ do ảnh xám phẳng (Lumen/TAA chưa hội tụ). Đổi kiến trúc sang Begin/Finish + Delay latent (xem `DEVIATIONS.md` [ARCH] 14/07/2026). Test debug bằng phím T trong `BP_ComboManager`, Delay warm-up thử 0.5s (chưa đủ, còn tối) → 3s/6s/10s (đẹp, khác biệt không đáng kể). Chốt tạm 3.0s cho gate này — số chính xác dời sang G4 (lúc wire thật vào UX Save Combo, đánh giá bằng cảm giác thật thay vì đoán).

Gate G1: DONE (14/07/2026) — `LoadComboThumbnail` thân hàm đầy đủ (đọc PNG từ đĩa → `IImageWrapper` `SetCompressed` → `GetRaw` BGRA8 → optional `FImageUtils::ImageResize` xuống `MaxSize` → `UTexture2D::CreateTransient` + memcpy vào Mip 0). Build PASS, test phím Y độc lập (tách khỏi phím T capture) → "G1 Load OK, size=256" đúng kỳ vọng.

Thêm dependency module `ImageCore` vào `FurnitureToolkit.Build.cs` (cần cho `FImageUtils::ImageResize`) + include mới trong `ComboThumbnail.cpp`: `"Engine/Texture2D.h"`, `"ImageUtils.h"`.

2 điểm đã quan sát, KHÔNG phải bug, xử ở gate sau:
- Ảnh hơi sharpen quá đà / chưa mịn — nghi do capture ở resolution native, không qua TSR như viewport chính. Xử ở G2 (tinh chỉnh PostProcessSettings) cùng lúc chỉnh khung hình.
- Góc chụp hiện là "camera lúc bấm nút", chưa auto-fit theo bounding box combo — đúng dự kiến G0, G2 mới thay bằng FitRatio.

Gate G2: DONE (15/07/2026) — auto-fit khung hình theo bounding box combo (FitRatio) + ẩn
gizmo/outline lúc capture. BeginComboCapture/FinishComboCapture đổi signature: Begin thêm
FitRatio/bIsolateCombo/bUseFixedAngle/FixedAngle; Finish thêm param ComboActors (cần để khôi
phục Custom Depth đúng actor đã tắt ở Begin — không track state qua static function, đưa lại
CÙNG mảng ComboActors ở cả 2 lần gọi). Vị trí camera phụ giờ tính từ Center - Dir*Distance
(bounding box + FitRatio=0.85), không còn đúng vị trí camera thật như G0-R.

Ẩn gizmo: dùng Get All Actors Of Class(BaseGizmo) — class chung của RuntimeTransformer cho
cả 3 loại gizmo (Translation/Rotation/Scale), KHÔNG dùng BP_TransformerPawn/GizmoController.
TargetActor (dự kiến ban đầu) không ổn định lúc đứng yên — bỏ.

[DEFERRED] Exposure bug: ảnh capture tối hơn viewport thật ở cảnh có vùng sáng mạnh trong
khung (nghi ngược sáng/backlit). Đã thử 2 lần Auto-exposure Min/Max lock (1 lần cũ ghi
14/07, 1 lần lặp lại 15/07) — CẢ 2 ĐỀU FAIL, không dùng hướng này nữa. Cần Fable review kiến
trúc — việc đưa lên Fable dời sang session khác, không chặn G3/G4.

Gate G3: DONE (15/07/2026) — cache Cmb_ThumbnailCache : Map<String,Texture2D> trong
BP_ComboManager. GetComboThumbnail/InvalidateThumbnail + EndPlay Map Clear (R4). 4 node Map
Find/Add/Remove/Clear đã dùng thật, PASS test — chuyển vào bảng node chính thức
(AI_Implementation_Rules.md, xóa khỏi "Nodes chờ xác nhận").

🔴 BUG NGHIÊM TRỌNG phát hiện + fix trong G3: GetComboThumbnail (Function, có Return Value)
thiếu Return Node ở nhánh False của IfThenElse kiểm IsValid(LoadedTex) — khi LoadComboThumbnail
fail (file chưa tồn tại), hàm KHÔNG chạm Return Node nào → Blueprint runtime TÁI SỬ DỤNG giá
trị output CÒN SÓT LẠI từ lần gọi TRƯỚC (không tự động None như tưởng). Hậu quả: mọi combo
CHƯA CÓ thumbnail đều hiện NHẦM ảnh của combo có thumbnail load thành công gần nhất trong
cùng vòng lặp LoadComboLibrary. Fix: thêm Return Node tường minh ở nhánh False, Texture2D để
trống (None). BÀI HỌC: mọi Function có Return Value phải kiểm 100% exec path chạm Return Node
— "dead-end vô hại" KHÔNG áp dụng cho Function có return type, chỉ áp dụng cho Event/side-effect
thuần. Thêm rule này vào AI_Implementation_Rules.md L-series.

Gate G4: DONE (15/07/2026) — nối capture vào SaveComboFromSelection (Bước 7, đúng placeholder
có sẵn từ doc cũ), hiển thị thumbnail trong WBP_ComboCard + WBP_FurnitureInventory.

🔴 2 bug dead-end khác phát hiện + fix trong lúc nối Bước 7 (SaveComboFromSelection):
- IfThenElse kiểm Pivot found (Length>0 GetAllActorsWithTag) — nhánh False (KHÔNG có Pivot,
  TRƯỜNG HỢP PHỔ BIẾN NHẤT vì Pivot chỉ tồn tại lúc multi-select) dead-end thật → combo save
  im lặng KHÔNG capture, KHÔNG hiện trong inventory. Fix: nối thẳng vào Array_Add.
- IfThenElse kiểm bSaveOK (SaveStringToFile) — nhánh False (ghi JSON fail) dead-end thật →
  Broadcast OnComboLibraryChanged không chạy dù JSON fail thì vẫn nên broadcast bình thường
  (đúng thiết kế gốc). Fix: nối thẳng vào Call Delegate.

✅ Bug dead-end ComboManagerRef: FIXED (15/07/2026, thực hiện trực tiếp trong UE5 Editor,
ngoài phiên Claude Code này) — WBP_FurnitureInventory.LoadComboLibrary, IfThenElse kiểm
IsValid(ComboManagerRef), nhánh False nối vào Array_Add (bỏ qua bước gán Thumbnail) thay vì
dead-end. Không còn rủi ro combo bị rớt khỏi AllComboViews_Combo khi ComboManagerRef invalid.

✅ Debug chain phím T/Y: ĐÃ DỌN (15/07/2026, ngoài phiên Claude Code này) — theo điều kiện
PASS G4 đã ghi trong plan gốc.

Field ThumbnailPath (String) trong BP_ComboItemView — XÁC NHẬN dead field, không dùng ở đâu
trong BP_ComboManager. Giữ nguyên (KP3, dọn sau).

Delete combo: XÁC NHẬN CHƯA TỪNG IMPLEMENT. Note cũ ghi nhầm "C8 = delete combo" — thực ra
C8 = "Drag-drop + surface-snap", đã MERGED vào C4 (24/06). Tính năng xóa combo (BTN_DeleteCombo
có sẵn trong layout WBP_ComboCard từ C4 nhưng chưa bind handler) là task RIÊNG, chưa làm.

Test G4: case 1,2,3,5,6 PASS (case 4 xóa combo N/A — chưa có tính năng). Bug cross-combo
thumbnail phát hiện qua case thao tác folder (move combo) — đã fix (xem G3 bug ở trên).

Gate G5: DEFERRED (15/07/2026) — thử đo bằng stat rhi (lỗi thao tác console, không ra kết
quả) rồi MemReport -full (ra kết quả nhưng nhiễu nặng: baseline sau khi camera quét toàn
scene nội thất đầy đủ của đồng nghiệp làm VRAM tăng ~1421MB giữa 2 mốc đo do texture streaming
theo tầm nhìn camera, KHÔNG TÁCH ĐƯỢC phần đóng góp riêng của combo thumbnail). Cách đo "đứng
yên camera, không di chuyển" cho số liệu sạch nhưng xung đột với luồng tạo combo thật (phải
chọn đồ + xoay góc chụp tự nhiên). Quyết định: NỢ G5, cần nghĩ lại phương pháp đo (cân nhắc
RenderDoc/Nsight thay vì so sánh MemReport thô — xem docs/Bugs/Bug_GPU_VRAM_Crash.md mục
"Tools chuyên nghiệp") trước khi thử lại. KHÔNG CHẶN tiến độ — P1 coi như DONE về tính năng
(G0→G4 hoàn chỉnh, test PASS).

Lưu ý phụ: trong lúc thử stat rhi, gặp crash D3D12 PageFault 1 lần (Local Used 6517MB/Budget
7262MB) — KHỚP đúng bug đã biết Bug_GPU_VRAM_Crash.md (PIE tích lũy VRAM qua nhiều lần
Play/Stop liên tiếp trong cùng session Editor), KHÔNG liên quan riêng combo thumbnail.

### P2 (Studio Thumbnail) — plan v1.0 chốt (16/07/2026)

Plan v1.0 tại `Plans/P2_StudioThumbnail_Execution.md` — Gate A DONE (đầu phiên 17/07, PASS 6/7,
case 7 dời Gate F). Gate B DONE (dome hình học + Cast Shadow=False; màu dome S1 dời sang đợt
"tối ưu cuối"). Gate C DONE (đèn Key/Fill RectLight qua `SpawnStudioLight` + Manual EV100 +
camera H-B `bUseFixedAngle`; verify 2 combo khác nhau ra cùng góc + cùng độ sáng). Gate D
(bóng + sweep hình dáng): prerequisite fixes DONE — lighting isolation (18/07) + noise/aliasing
(19/07, temporal accumulation N=24 frame + SSAA 2× supersample). **20/07: Rim Light (3-point
lighting, [SCOPE] mở rộng Gate C) DONE + VRAM/GPU crash fix (EndPlay `BP_ComboManager`, 2 bug
wiring) DONE + Source Size Key=500 chốt. Sweep 5 loại combo: 3/5 PASS (Nhỏ/To/Tường), 2/5 FAIL —
phát hiện 2 bug kiến trúc MỚI chưa từng ghi trong plan: (1) dome cong (sphere) nuốt chân đồ
footprint rộng (sofa/thảm); (2) combo "Cao" (surfaceType Ceiling) dính lỗi ground-align giống
case Tường (H1) nhưng chưa từng ghi nhận. GATE D TẠM DỪNG — cần Fable/Opus quyết kiến trúc (đảo
ngược 1 phần quyết định Gate B) trước khi tiếp tục sweep.** Chi tiết bug/quyết định kiến trúc
Gate B/C: xem `DEVIATIONS.md` mục "P2 — 17/07/2026 (cuối phiên)"; Gate D prerequisite lighting
isolation: xem `DEVIATIONS.md` mục "P2 — 18/07/2026"; Gate D prerequisite noise/aliasing: xem
`DEVIATIONS.md` mục "SPRINT 5 — 19/07/2026 — P2 Noise + Aliasing Fix"; Gate D Rim Light + VRAM
fix + 2 bug kiến trúc mới: xem `DEVIATIONS.md` mục "P2 — 20/07/2026" và `Bugs/Open_Bugs.md`.
Thứ tự sau P2: K1 (có thể chen trước Gate F, quyết tại F) → K3 còn lại → C9 → C6
→ C7 → C11 → C10 → Gate 2.

**Roadmap v3.3 (chia 3 giai đoạn — scope phình to sau 23/06):**
```
Gate 1 (fix B1 bIsRestoring + hợp nhất spawn)   ✅ DONE (16/06)
Sprint D (D.T1-D.T9, Furniture Data Layer v2)    ✅ DONE (17/06)
TreeNode/Chip active-folder highlight            ✅ DONE (18/06, bổ sung)
Sprint 5 — COMBO LIBRARY ĐẦY ĐỦ 🔄 IN PROGRESS (21/06, v2.0)
  ⚠️ 23/06: P1+P2+P3 làm scope phình → chia 3 giai đoạn. Deadline 25/06 chỉ xong G1.
  ✅ T1 — C++ ComboTypes + ComboSerializer (schema v1, round-trip PASS)
  ✅ T2 core — SaveComboFromSelection + CB_SaveCombo (hệ thống cơ bản)
  ✅ C0 — 3 case A/B/C PASS + RowName fallback (22/06)
  ✅ C1 — FolderPath C++, FindMaterialRowNameByPath C++, SourceComboID BP, Fav/Recent prefs
  ✅ C2 — SpawnComboByID 7/7 PASS (22/06)
  ⚠️ Fix K3 — SpawnFurnitureCopy bAddToRecent param (áp lúc đụng C2/RestoreSnapshot) — planned
──── Giai đoạn 1 (~25/06) ────
  ⏳ C3 — Save dialog + P4 (GetCombosDir→LOCALAPPDATA) + capture thumbnail sau save
  🔄 Thumbnail System C++ (P1) — ĐANG LÀM: Gate G0-R ✅ DONE (14/07, xem mục P1 trên), G1-G5 còn lại
  ✅ C4 — WBP_ComboCard (thumbnail thật, badge ×N) — DONE (25/06)
  ✅ C5 — Folder Management đầy đủ (browse/tree/move/rename/xóa/chip) — TOÀN BỘ HOÀN TẤT (06/07)
  ✅ C5.8 — Folder Tree Picker Unify (Move Dialog + Save Dialog) — DONE (13/07/2026, REG PASS), xem C5.8_FolderTreePicker_Unify_Plan.md
  ⏳ C6 — Favorite + Recent combo
  ⏳ C7 — WBP_ComboDetailPopup (thumbnail thật)
──── Giai đoạn 2 ────
  ⏳ WBP_Toast (K1) — TIÊN QUYẾT trước C8
  ✅ C8 — Drag-drop + surface-snap kiểu khối (P2) — DONE, MERGED vào C4 (24/06/2026)
  ⏳ Xoay combo (P3) — verify gizmo group + tùy chọn xoay-lúc-kéo
  ⏳ C9 — Replace (+ verify K2 + CalculateCenter chung + auto-rollback)
──── Giai đoạn 3 ────
  ⏳ C11 — Export/Import cả 2 hướng (K5)
  ⏳ C10 — Regression (K4/P5-liên quan/VRAM) + Docs
→ Sprint 7 Material v1.2 (P5 material name-based — mở màn)
→ Sprint 6 Polish
→ Gate 2 (first packaged build)
```

---

## NGUYÊN TẮC ĐỌC DOC ĐẦU SESSION

1. Đọc `01_Session_State.md` TRƯỚC
2. Gate 1 → đọc `02_Current_Sprint.md` + `Rules/AI_Implementation_Rules.md`
3. Sprint D → đọc `02_Current_Sprint.md` phần Sprint D
4. Flow chi tiết → `Blueprints/BP_FurnitureInputManager.md` v2.1 + `Blueprints/BP_UndoManager.md` v1.10
5. Flow Sprint 1-3 → `Blueprints/Blueprint_Logic_NodeFlow.md`

---

## Lịch sử cập nhật

| Ngày | Nội dung |
|------|----------|
| 21/06/2026 | Sprint 5 T1+T2 DONE (sáng). |
| 21/06/2026 EOD | Sprint 5 T3+C1 DONE. C0 impl xong chưa test (LCA nested + MaterialOverrides). BP_ComboManager → v1.1 (GetPathToRoot_Combo, FindLCA_TwoGroups_Combo, CalculateLCAList_Combo, LeafGroupIDs/LCARoots/MaterialOverrides_SaveCombo). C++ FurnitureToolkit: FComboData.FolderPath + FindMaterialRowNameByPath. Full rebuild xanh. TIẾP THEO: test C0 (3 case) → C2 SpawnComboByID. |
| 22/06/2026 | C0 DONE — 3 case A/B/C PASS. RowName fallback (đồ cũ parse MeshPath) xác nhận OK. BP_ComboManager → v1.2 (thêm ItemRowName_SaveCombo). TIẾP THEO: C2 SpawnComboByID. |
| 22/06/2026 | C2 SpawnComboByID DONE — 7/7 PASS. BP_ComboManager → v1.3 (5 class var mới, 4 functions: F_LoadComboData/F_BuildTokenGUIDMap/F_RegisterComboGroups/F_ApplyMaterialOverrides, Custom Event SpawnComboByID 4 sub-steps). Group nesting fix: Case A (no groups→wrapper) / Case B (has groups→no wrapper). TIẾP THEO: C3 WBP_SaveComboDialog. |
| 23/06/2026 | Chốt 11 quyết định + 3 điều chỉnh (Sprint5_Plan_v1.1): P1 thumbnail C++ thật, P2 surface-snap khối, P3 xoay combo, P4 lưu LOCALAPPDATA, P5 dời Sprint7, K1 WBP_Toast, K3 bAddToRecent (planned), K5 export cả 2 hướng. Scope phình to → chia 3 giai đoạn. Roadmap v3.3. Việc kế = C3. |
| 24/06/2026 | C3b ✅ DONE (WBP_SaveComboDialog + OpenSaveComboDialog flow). C4 ⏳ 80%: WBP_ComboCard + BP_DragDropOperation_ComboCard + BP_ComboGhostActor + M_ComboGhost; CalculateComboAnchor (InputManager v2.3); CTV_ComboCard (Inventory v2.9) — 19 combo PASS. C8 ✅ MERGED vào C4. BUG OPEN: B-ghost-offset (đáy cube chìm sàn, Z=50 chưa fix). |
| 25/06/2026 | B-ghost-offset ✅ FIXED (Approach B, BP_ComboGhostActor v1.1, DragOverlay v1.8). C4/C8 ✅ 100% DONE. C5.1 ✅ DONE: 3 C++ folder helpers (ComboSerializer). C5.0 ⏳ ~90%: tree PASS, card render BUG OPEN (B-C5-card). |
| 26/06/2026 | C5.0 ✅ DONE: B-C5-card FIXED, tree 2 cấp + D9 guard, OnComboChipTagClicked, OnComboTreeNodeRightClicked, 3 stubs. WBP_LibraryContextMenu v1.0 ✅: clone ContextMenu, Btn_Background Z-order (D12), test PASS. WBP_TreeNode v1.2: OnNodeRightClicked dispatcher + On Mouse Button Down. WBP_FurnitureInventory v3.2. TIẾP THEO: C5.2 Rename folder. |
| 30/06/2026 | C5.4 ✅ DONE — Move Folder: S_FolderTargetEntry struct mới. WBP_MoveFolderRow v1.0 (Spacer_Indent indent ảo, SetRow/SetHighlight/OnRowClicked). WBP_MoveToFolderDialog v1.0 (PopulateRows/HandleRowSelected/OnMoveFolderConfirmed). WBP_FurnitureInventory v3.4: MovingFolderPath; CollectFolderTargets đệ quy (loại moving+con cháu); BuildMoveFolderTargetList; OnRequestMoveFolder implement; CB_MoveFolderClick implement; HandleMoveFolderConfirmed NEW. BUG FIX D-C5.4-1 (Array_Append ngược) + D-C5.4-2 (dead-end nhánh True thiếu merge). Backlog reorder: Issue 2 → Move Combo → NewFolder → Xóa folder → ChipTag right-click. |
| 01/07/2026 | Issue 2 ✅ + C5.5 Move Combo ✅ DONE — WBP_ComboCard v1.1: InventoryRef lazy-init + On Mouse Button Down override (RMB→OnComboCardRightClicked). WBP_FurnitureInventory v3.5: 3 class var (MoveComboDialogRef/MovingComboID/MovingComboCurrentFolder); UpdateComboFolderHighlights NEW; OnComboCardRightClicked NEW; CB_MoveCombo NEW (guard stacking + ForEachLoopWithBreak); HandleMoveComboConfirmed NEW. BUG FIX 4.1 (ParseIntoArray delimiter) + 4.2 (bỏ Map_Contains leaf folder) + 4.3 (+UpdateComboFolderHighlights call RefreshComboFolderUI). Learning_System v1.3 (định dạng giải thích: sơ đồ + ví dụ đời thường). Tiếp theo: Tạo folder mới. |
| 04/07/2026 | NF (New Folder) — context menu part ✅ DONE, nút "+" 🔲 CÒN NỢ. C++ NF.G0: `GetEmptyFoldersFilePath`→`Folders.json`; `GetAllFolderPaths` tự-ghi-bổ-sung path mới kể cả cấp cha — test PASS 6/6. Blueprint NF.G1: `BuildComboFolderTree` đổi nguồn sang `GetAllFolderPaths` (1 nguồn duy nhất, bỏ vòng tự-gộp AllComboViews) — test PASS 4/4. WBP_FurnitureInventory v3.6: `GetChildFolderNames`/`GetUniqueNewFolderName`/`GetNewFolderParent` (helpers); `OnRequestNewFolder`/`CB_CreateNewFolder` NEW (tạo cùng cấp node right-click, tự vào rename mode qua C5.2); `OnComboTreeNodeRightClicked` +1 menu item đầu chuỗi. Test PASS 9/9. Deviation: dialog (NF.G2-G5 gốc) → SUPERSEDED bởi inline rename (UX Explorer-style). Tiếp theo: nút "+" đầu cột tree → C5.6 (Xóa folder) → C5.7 (ChipTag rename). |
| 06/07/2026 | NF.G3 ✅ + C5.6 ✅ + C5.7a ✅ DONE — WBP_FurnitureInventory v3.7: `PopulateComboTreeColumn` +PlusNode (nút "+", sentinel `__NEWFOLDER__`) + `OnComboTreeNodeClicked` +guard; class var `PendingDeleteFolderPath`; `OnRequestDeleteFolder`/`HandleDeleteFolderConfirmed`/`CB_DeleteFolderClick` (Xóa folder, Deviation D-C5.6-1 nhảy về cha thay vì `__ALL__`); `RebuildChipRowForPath`+`RefreshChipBreadcrumb` NEW (gộp code ChipRow trùng lặp + fix chip area không tự refresh sau Move/Xóa/Rename — 3 bug fix: dead-end 2/3 nhánh, delimiter "/ " sai, BooleanAND→OR); bug fix SelectedPath nhầm biến (class var trùng tên param) trong OnComboTreeNodeClicked. WBP_ChipTag v1.2: +dispatcher OnChipRightClicked + On Mouse Button Down override. WBP_ConfirmDialog TẠO MỚI (generic Yes/No). Tiếp theo: C5.7b (inline rename trong chip) → REG → C5 HOÀN TẤT. |
| 06/07/2026 (tối) | C5.7b ✅ DONE — **C5 FOLDER MANAGEMENT HOÀN TẤT.** WBP_ChipTag v1.3: `EditLabel_ChipTag` (WBP_EditableLabel) thay `TextBlock_ChipTag`; `EnterRenameMode`/`HandleLabelCommitted` NEW; dispatcher `OnChipRenameCommitted`. WBP_FurnitureInventory v3.8: class var `RenameTargetChip`; `OnRequestRenameFolder` mở rộng fallback tree→chip (double-break qua Completed loop lồng); `RebuildChipRowForPath` +bind `OnChipRenameCommitted`→`OnRenameFolderCommitted`. BUG FIX `CB_CreateNewFolder` (node SET thừa đè cache → luôn tạo root); BUG FIX `CB_RenameFolder` (thiếu SET LibraryMenuRef=None cuối chuỗi). Test PASS full case. Tiếp theo: REG (regression 12 bước) → C6/C7 (defer) hoặc WBP_Toast → C9. |
| 07/07/2026 | **C5.8 (Folder Tree Picker Unify) 🔲 PLANNED** — nhận delta kiến trúc v2 (Fable/Opus) gộp lõi data+component cho `WBP_MoveToFolderDialog`+`WBP_SaveComboDialog` (tree picker: guide line, search, expand/collapse, inline create). Slot chốt: NGAY SAU C5, TRƯỚC C9 (cuhoang chốt). Plan đầy đủ + 2 Task Card: `docs/Sprints/Sprint5/C5.8_FolderTreePicker_Unify_Plan.md`. CHƯA thực thi — việc kế tiếp là Task Card #1 (Data Layer: rename `S_FolderTargetEntry`→`S_FolderTreeNode`, `BuildFolderTree`, verify Print trước UI). |
| 08/07/2026 | **C5.8 Task Card #1 (Data Layer) ✅ DONE** — rename `S_FolderTargetEntry`→`S_FolderTreeNode` (+4 field: HasChildren/ChildCount/ContinuesAncestors/bIsLast); `CollectFolderTargets`→`BuildFolderTreeRecursive` (đệ quy, depth guard=12) + hàm mới `GetFilteredChildren` (Pure); wrapper `BuildComboFolderTreeNodes(ExcludePath)` — tên đổi khác plan gốc (`BuildFolderTree` trùng tên hàm cũ Material/Furniture catalog), log DEVIATIONS.md. Test Print PASS data thật (8 combo, nested 3 tầng, tiếng Việt) — không lệch. WBP_FurnitureInventory v3.9. Tiếp theo: Task Card #2 (`WBP_FolderTreePicker` UI component, §11b). |
| 11/07/2026 | **C5.8 Task Card #2 Part B — Giai đoạn 1 ✅ DONE** — bug #2 xác định root cause: `SetNode` thiếu `SET RowNode = Node` (gây cả Path rỗng lẫn Arrow không đồng bộ Visibility với BTN_Arrow). Fix 2 chỗ trong `SetNode` (WBP_FolderPickerRow v1.1). Đính chính quan trọng: FixPlan v1.1 SAI về Custom Event trung gian — thực tế binding nối THẲNG OnClicked→Call dispatcher (không lớp trung gian) cho cả BTN_Arrow/BTN_Name VÀ 2 handler mới BTN_ExpandAll/BTN_CollapseAll (WBP_FolderTreePicker v1.0). Test mục 1→5 task card PASS (expand/collapse đơn + Mở tất cả/Thu gọn + nhớ state con cháu — 6A xác nhận). TIẾP THEO: Giai đoạn 2 — search (`PathMatchesQuery`/`BuildSearchOverride`/wire `SB_SearchFolder`/`SetSearchHighlight`), xem `C5.8_TaskCard2_FixPlan_11jul2026.md` Giai đoạn 2. |
| 12/07/2026 10:40 | **C5.8 Task Card #2 Part B — Giai đoạn 2 (Search) + Giai đoạn 3 (Select) ✅ DONE** — 3 Function mới trên `WBP_FolderTreePicker`: `PathMatchesQuery` (Pure, Contains không phân biệt hoa thường), `BuildSearchOverride` (build `SearchExpandOverride` từ tổ tiên các node match), `GetParentPath` (Pure, hỗ trợ bug arrow-click trong lúc search). `RefreshVisibleRows` ghép xong nhánh search thật (không còn ⚠️ SUY LUẬN) + wire `SB_SearchFolder.OnSearchTextChanged` → class var `CurrentSearchFolder` (thay Local `QueryStr`). `SetSearchHighlight(bMatch)` DONE trên `WBP_FolderPickerRow` (2 class var màu `Color Match`/`Color Default`). Bug fix: `PathMatchesQuery` dùng nhầm `Path` đầy đủ thay `DisplayLabel` (substring match nhầm con); arrow-click node đang match trong lúc search không lộ con (`GetParentPath` + sửa `bShow`/`SetExpanded` bỏ hardcode). Test mục 1-10 PASS hết — Task Card #2 Part B + 2c HOÀN TẤT. TIẾP THEO: Giai đoạn 4 (Chốt sổ — comprehension check còn nợ 2 câu, cuhoang đang trả lời) → 2d (rename host) → wire Move → wire Save + Create Folder → REG C5.8 (thứ tự đã khoá). |
| 13/07/2026 | **C5.8 — 2d + Wire Move + Wire Save build + test DONE**. 3 bug fix: (1) OnRequestMoveFolder/CB_MoveCombo sót gọi BuildMoveFolderTargetList (hàm cũ, thiếu HasChildren/ChildCount) — đổi sang BuildComboFolderTreeNodes, xoá hàm cũ; (2) SetSelectedHighlight so sai biến (CurrentPath thay SelectedPath) — tách so sánh riêng; (3) SetLabelColor type Slate Color không phải Linear Color. Test PASS: Phần 2 (1,2), 0.3, M1-M6, S6a/S6c. S6b [SCOPE] không áp dụng (context-menu rename không tồn tại theo thiết kế 2d). Version bump: WBP_FolderPickerRow v1.3, WBP_FolderTreePicker v1.3, WBP_EditableLabel v1.1, WBP_MoveToFolderDialog v2.0, WBP_SaveComboDialog v2.0, WBP_FurnitureInventory v3.11. TIẾP THEO: REG C5.8 (task card chốt sổ, khối A/B/C) → sau đó mới cho phép sang C9. |
| 13/07/2026 (REG) | **C5.8 (Folder Tree Picker Unify) — CHÍNH THỨC DONE.** REG (task card `C5.8_REG_TaskCard_11jul2026.md`) chạy đủ Khối A/B/C/D: A1-A7 PASS (A1 kèm clarification wording task card — xem DEVIATIONS), B1-B4 PASS (B4 kèm scope note không live-sync 2 cây), C1 SKIP (rủi ro thấp)/C2-C5 PASS (không VRAM leak). D5 comprehension check PASS. 2 bug mới phát hiện qua REG — GHI Open_Bugs.md, KHÔNG sửa trong C5.8 (ngoài scope): (1) BTN_Confirm Save dialog không disable khi tên trống chưa gõ gì (bug có sẵn từ C3b, không phải do C5.8); (2) Move Folder không check trùng tên đích (backlog, cần task riêng). **Roadmap: mở khóa C9 (Replace).** |
| 14/07/2026 | **P1 Combo Thumbnail — Gate G0-R DONE.** One-shot capture (G0 gốc) loại bỏ do ảnh xám phẳng — Lumen GI/TAA/auto-exposure cần nhiều frame thật mới hội tụ, camera phụ vừa spawn chụp 1 frame không đủ. Đổi kiến trúc: `BeginComboCapture`/`FinishComboCapture` bọc bởi Custom Event dùng `Delay` latent (L8), thay `CaptureComboThumbnail` đồng bộ cũ (giữ `[LEGACY]`, không xóa/gọi). Test debug phím T trong `BP_ComboManager` — Delay warm-up 0.5s chưa đủ, 3s/6s/10s đều đẹp, chốt tạm 3.0s (số chính xác dời G4). Ảnh hưởng: Save Combo có thêm độ trễ latent, Broadcast dời xuống SAU FinishComboCapture, capture fail vẫn Broadcast (fallback icon 🧩). `.h` bị đụng lần 2 (chấp nhận). Tiếp theo: G1 (đọc PNG→Texture2D, thay stub `LoadComboThumbnail`). |
| 14/07/2026 (dọn nợ) | **Dọn stale content C5.8 trong `## TIẾP THEO`** (đã báo 2 lần ở các lần phân phối trước, cuhoang xác nhận gộp dọn cùng lúc P1, KHÔNG thuộc nội dung delta P1 gốc): block prose "C5.8 — Folder Tree Picker Unify" (dòng cạnh mục P1) và dòng trong Roadmap v3.3 ASCII (Giai đoạn 2) sửa từ 🔄 IN PROGRESS (mô tả trạng thái 11/07, đã lỗi thời) → ✅ DONE (13/07/2026, REG PASS) — khớp với changelog 13/07/2026 (REG) đã ghi trước đó. |
| 14/07/2026 (roadmap reorder) | **Sửa thứ tự + trạng thái Roadmap v3.3** (theo yêu cầu cuhoang): C4 và C8 sửa ⏳→✅ DONE (đã xong từ 25/06 và 24/06, marker cũ sai/lỗi thời). Dòng "C5 — Folder tree tab 🧩 Combo" viết lại thành "C5 — Folder Management đầy đủ... TOÀN BỘ HOÀN TẤT" (khớp phát biểu C5 đã dùng ở mục TIẾP THEO). **Dời C5.8** từ cuối Giai đoạn 2 → ngay sau C5 trong Giai đoạn 1 — khớp đúng ghi chú gốc "chốt slot NGAY SAU C5, TRƯỚC C9" (trước đó bị đặt sai chỗ, nằm sau cả WBP_Toast/C8/Xoay combo). Thumbnail System (P1) gắn nhãn "ĐANG LÀM" khớp `02_Current_Sprint.md`. |
| 14/07/2026 (P1 G1) | **P1 Combo Thumbnail — Gate G1 DONE.** `LoadComboThumbnail` thân hàm đầy đủ: đọc PNG từ đĩa → `IImageWrapper` `SetCompressed`/`GetRaw` BGRA8 → optional `FImageUtils::ImageResize` xuống `MaxSize` → `UTexture2D::CreateTransient` + memcpy Mip 0. Build PASS, test phím Y (tách riêng khỏi phím T capture) → "G1 Load OK, size=256" đúng kỳ vọng. Thêm module `ImageCore` vào `FurnitureToolkit.Build.cs` + include `Engine/Texture2D.h`/`ImageUtils.h` trong `ComboThumbnail.cpp` — bắt buộc để build, KHÔNG phải deviation kiến trúc (đúng plan gốc). Tiếp theo: G2 (auto-fit FitRatio + ẩn gizmo/outline lúc capture + tinh chỉnh sharpen/PostProcess). |
| 17/07/2026 | **P2 (Studio Thumbnail) — Gate A DONE.** Việc 1-4 hoàn tất, TEST PASS 6/7 case (case 7 — tắt PIE giữa Delay — dời kiểm tra sang Gate F). BP_ComboManager: `SpawnComboForThumbnail(ComboID, DeltaYaw=0)` Custom Event mới + chuỗi debug phím U (ground-align, BeginComboCapture/FinishComboCapture). BP_FurnitureInputManager: `SpawnFurnitureCopy` +param `bAddToRecent`. Fix aliasing `Add Actor World Offset` dùng nhầm Array Element giữa 2 For Each Loop liên tiếp. Delay(0.5→3.0) ceiling tạm cho LoadMeshAsync — xem DEVIATIONS. Chi tiết: `P2_StudioThumbnail_Execution.md`. Tiếp theo: Gate B (dome). |
| 17/07/2026 (cuối phiên) | **P2 (Studio Thumbnail) — Gate B + Gate C DONE.** Gate B: dome hình học (`Cmb_StudioDomeRadius`, Scale=R/50) + `M_StudioBackdrop`; **Cast Shadow=False** trên dome (quyết định kiến trúc quan trọng nhất — dome chỉ nhận bóng, không chặn sáng đèn ngoài bán kính R); màu dome S1 dời sang đợt "tối ưu cuối" cùng cove mesh custom (nếu faceting xác nhận là vấn đề thật). Gate C: Function mới `SpawnStudioLight(AngleOffsetDeg, Intensity)` dùng chung cho Key/Fill RectLight (Mobility=Movable bắt buộc, Attenuation Radius=8000, elevation 45°); Manual EV100 qua `Get/Set members in Post Process Settings` (không dùng `Make`, tránh ghi đè Lumen override C++); camera H-B tick `bUseFixedAngle`. 12 bug/quyết định trong lúc làm Gate C (chi tiết đầy đủ: `DEVIATIONS.md` mục "P2 — 17/07/2026 (cuối phiên)") — đáng chú ý nhất: dịch số vị trí đèn sai hướng 5 lần liên tiếp trước khi Fable chỉ ra root cause thật là Cast Shadow, bài học "3 lần sai cùng chỗ → STOP hỏi Fable" bị áp dụng trễ. Verify PASS: 2 combo khác nhau → cùng góc + cùng độ sáng. Tiếp theo: Gate D (bóng + sweep hình dáng). |
| 18/07/2026 | **P2 (Studio Thumbnail) — Gate D prerequisite: lighting isolation.** Task gốc Gate D (Source Size Key tune + sweep 5 combo) chưa chạm — capture đầu tiên lỗi nặng (cháy sáng, vệt đen, bóng cứng, tông đổi theo giờ UDS), toàn phiên dành điều tra + fix 3 nguyên nhân gốc chặn: [CORRECTION] RectLight offset Z thật = 1200 (không phải 1500), đèn thật ra nằm TRONG dome (~1700 < R=2000) — loại giả thuyết "đèn ngoài bán kính"; [BUG-FIX] Distance Field khối đặc của Sphere engine tự triệt tiêu RectLight khi Cast Shadow=True → duplicate asset riêng `SM_StudioDome` + Two-Sided Distance Field Generation; [ARCH] `Set Lighting Channels` cô lập dome+đèn+furniture clone khỏi Sun/UDS (Channel 1); [ARCH] `Set Show Flag Settings(SkyLighting=False)` trên Capture Component riêng, không đụng LightManager của đồng nghiệp. Dải đen viền khung hình còn lại — [SUY LUẬN chưa verify], dời xử lý sang đúng task Gate D. Chi tiết đầy đủ: `DEVIATIONS.md` mục "P2 — 18/07/2026". Tiếp theo: tune Source Size Key + sweep 5 combo (task gốc Gate D). |
| 19/07/2026 | **P2 (Studio Thumbnail) — Gate D prerequisite: Noise + Aliasing Fix, DONE.** Vẫn chưa chạm task gốc Gate D — ảnh thumbnail còn noise nặng (đốm blotchy nền dome + bóng mềm) sau lighting isolation 18/07, đã loại 7 giả thuyết trước khi xác định `SceneCapture2D` không có temporal accumulation thực sự (khác viewport chính). Fix: `AccumulateComboFrame`/`ResetComboAccumulation` (C++ mới, `UComboThumbnail`) cộng dồn N=24 frame trong không gian linear color, mượn Event Tick của `BP_ComboManager` (biến mới `Cmb_AccumFramesLeft`/`Cmb_AccumTargetFrames`) thay vì subclass SceneCapture2D; SSAA 2× supersample (RT 2048² khi Resolution=1024) + box downscale, encode gamma sRGB đúng 1 lần cuối. Bug fix trong lúc code: sửa nhầm `CreateRenderTarget2D` bản [LEGACY] thay vì bản thật (2 hàm cùng signature, phân biệt qua `bCaptureEveryFrame`). Test: noise CONFIRM (mịn hơn, không giật) + aliasing/SSAA CONFIRM DONE (cuhoang tự chạy lại checklist đầy đủ — kích thước ảnh đúng, không giật thêm). Chi tiết đầy đủ: `DEVIATIONS.md` mục "SPRINT 5 — 19/07/2026 — P2 Noise + Aliasing Fix", `Data/ComboSerializer_Reference.md`. Tiếp theo: tune Source Size Key + sweep 5 combo (task gốc Gate D, vẫn CHƯA bắt đầu). |
| 20/07/2026 | **P2 (Studio Thumbnail) — Gate D: Rim Light + VRAM Fix DONE, Source Size=500 chốt, sweep 3/5 PASS — TẠM DỪNG.** Rim Light (3-point lighting, [SCOPE] mở rộng Gate C) qua `SpawnStudioLight` gọi lần 3 + biến mới `Cmb_StudioRimLight`; đổi `InVect`/SourceSize/AttenRadius cả 3 đèn + Post Process Exposure Compensation +6.0 — verify PASS ảnh combo To+Tường. Fix VRAM/GPU crash (EndPlay `BP_ComboManager`, 2 bug wiring: `Map_Clear` lồng sai nhánh Branch + thứ tự đọc/ghi `Cmb_CaptureHandle` khiến `ResetComboAccumulation` no-op) — verify bằng đọc code + export K2Node, CHƯA đo VRAM dài hạn. Sweep 5 loại combo: 3/5 PASS (Nhỏ/To/Tường), phát hiện 2 bug kiến trúc MỚI — (1) dome cong nuốt chân đồ footprint rộng (sofa lộ nhẹ, thảm FAIL nặng); (2) combo "Cao" (Ceiling) dính lỗi ground-align giống Tường (H1) nhưng chưa từng ghi trong plan. **Gate D TẠM DỪNG — chờ Fable/Opus quyết kiến trúc** (đảo ngược 1 phần quyết định Gate B) trước khi tiếp tục. Chi tiết: `DEVIATIONS.md` mục "P2 — 20/07/2026", `Bugs/Open_Bugs.md`, `Blueprints/Blueprint_Logic_NodeFlow.md` v1.11. |
