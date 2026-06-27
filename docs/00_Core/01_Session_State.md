# Session State
**Nguồn:** `import_raw/Session_State_15jun2026.md` (bản mới nhất — 15/06/2026 20:30 ICT)
> Session_State.md (12/06/2026) là bản cũ hơn — đã merged vào đây.
**Phiên bản:** 27/06/2026 — C5.2 ✅ DONE | WBP_EditableLabel v1.0 + WBP_TreeNode v1.3 + WBP_FurnitureInventory v3.3

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
**WBP_ComboCard** — TẠO MỚI (24/06): OnListItemObjectSet, OnDragDetected → spawn BP_ComboGhostActor + BP_DragDropOperation_ComboCard
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
**S_GroupData** — ✅ field `SourceComboID : String` (default "") đã thêm (C1 DONE). Group cha cụm combo = ComboID gốc; group user tạo tay = "". Đã add vào snapshot capture/restore.
**C++ FurnitureToolkit** — FComboData.FolderPath (field mới), FindMaterialRowNameByPath (function mới). Compile xanh. Full rebuild (Binaries/Intermediate xóa + rebuild) ✅

**Snapshot version history:**
- V1: single select (legacy)
- V2: multi-select (Sprint 1)
- V3: Groups (Sprint 3)
- V4: Groups + EditModeStackSnapshot (Sprint 4 Bug Fix, 15/06/2026)

---

## TIẾP THEO

**ĐẦU SESSION MỚI — Ưu tiên:**
1. 🔲 **C5.4 — Move folder** — Kéo folder tree node vào target → `ComboSerializer.UpdateComboFolder(OldPrefix, NewFolder)` → `RefreshComboFolderUI()`. WBP_ChipTag rename tái dùng WBP_EditableLabel.
2. ⏳ **C3 còn lại** — GetCombosDir → `%LOCALAPPDATA%\InteriorFOFFTool\Combos` (P4) + capture thumbnail sau SaveComboFromSelection (P1 hook).

**BUG OPEN (nhỏ, defer):**
- WBP_ChipTag right-click chưa có (C5.4+)
- Chip highlight chưa update khi select (Issue 2, polish sau)

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
  ⏳ Thumbnail System C++ (P1) — SaveRenderTargetToPNG + LoadTexture2DFromFile
  ⏳ C4 — WBP_ComboCard (thumbnail thật, badge ×N)
  ⏳ C5 — Folder tree tab 🧩 Combo
  ⏳ C6 — Favorite + Recent combo
  ⏳ C7 — WBP_ComboDetailPopup (thumbnail thật)
──── Giai đoạn 2 ────
  ⏳ WBP_Toast (K1) — TIÊN QUYẾT trước C8
  ⏳ C8 — Drag-drop + surface-snap kiểu khối (P2) + fix drop-anchor Lỗ14
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
