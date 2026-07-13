# PROGRESS — Tiến độ Multi-Select / Group / Combo / Material v1.2
**Nguồn:** `import_raw/PROGRESS.md` (12/06/2026) + `import_raw/PROGRESS_Sprint4BugFix_update.md` (patch 15/06/2026)
**Cập nhật:** 13/07/2026 (C5.8 Task Card #2 — 2d rename host + Wire Move + Wire Save, build+test node-level DONE)

---

## TỔNG QUAN

```
Sprint 1 — Multi-select       ███████████████ 15/15 SHIPPED ✅
Sprint 2 — Box + Context Menu ████████████████ 9/9  SHIPPED ✅
Sprint 3 — Group cơ bản       ████████████████ 12/12 SHIPPED ✅  (+10 bug fix)
Sprint 4 — Edit + Nested      ████████████████ 8/8  SHIPPED ✅  (+5 bug fix thêm)
Gate 1                        ████████████████ 3/3  DONE ✅ (16/06)
Sprint D — Data Layer v2      ████████████████ 9/9  DONE ✅ (17/06)
Sprint 5 — Combo Mesh         █████████████░  15/19 task (T1/T2/C0/C1/C2/C3a/C3b/C4/C8/C5.1/C5.0/C5.2/C5.4/Issue2/C5.5 ✅; 4 còn lại — +2 task backlog thêm 30/06)
                               (NF — New Folder: context-menu part ✅ DONE 04/07 + nút "+" (NF.G3) ✅ DONE 06/07)
                               (C5.6 Xóa folder ✅ DONE 06/07; C5.7 ChipTag right-click+rename ✅ DONE 06/07 — C5 HOÀN TẤT)
                               (C5.8 — Folder Tree Picker Unify: Task Card #1 Data Layer ✅ DONE 08/07, Task Card #2 UI Part B — Giai đoạn 1 ✅ DONE (11/07, bug #2 fixed + test 1-5 PASS), Giai đoạn 2 (search) chưa làm, chưa tính vào task count — xem C5.8_FolderTreePicker_Unify_Plan.md)
Sprint 6 — Polish UX          ░░░░░░░░░░░░░    0/14 task
Sprint 7 — Material v1.2      ░░░░░░░░░        0/9  task

TỔNG: 62/96 task
```

---

## SPRINT 1 — COMPLETE ✅ (15/15)

T1-T15 shipped. Chi tiết: `Blueprints/BP_FurnitureInputManager.md`, `Blueprints/BP_PivotActor.md`.

---

## SPRINT 2 — COMPLETE ✅ 9/9 (08/06/2026)

- [x] S2.T1 — WBP_BoxSelectOverlay
- [x] S2.T2 — Box Select logic (defer + Tick + Release)
- [x] S2.T3 — WBP_ContextMenu + ContextMenuItem + Separator
- [x] S2.T4 — Right-click handler
- [x] S2.T5 — Select Similar (MeshPath)
- [x] S2.T6 — Reset Rotation + Delete callback
- [x] S2.T7 — Cut Ctrl+X
- [x] S2.T8 — Sprint 2 final test — PASS
- [x] S2.T9 — CB_ChangeMaterial + CB_Replace multi

---

## SPRINT 3 — COMPLETE ✅ 12/12 (10/06/2026) + 10 bug fix + refactor

- [x] S3.VS — Vertical Slice: T1+T2+T3+T4 + EMS Save/Load test ✅
- [x] S3.T1 — Struct S_GroupData (GroupID, GroupName, ParentGroupID, bIsLocked)
- [x] S3.T2 — BP_FurnitureActor.GroupID (SaveGame)
- [x] S3.T3 — BP_GroupsContainer (EMS + singleton guard, TempTags GET→ADD→SET)
- [x] S3.T4 — Groups var + SyncGroupsToContainer (InputManager)
- [x] S3.T5 — Helpers: GetGroupChildren, FindGroupData, GenerateGroupID, ExpandSelectionWithGroups, PruneEmptyGroups
- [x] S3.T6 — CreateGroup (auto-name "Nhóm N") + Ctrl+G
- [x] S3.T7 — UngroupActors + Ctrl+Shift+G
- [x] S3.T8 — Click resolution → ExpandSelectionWithGroups
- [x] S3.T9 — Box select → ExpandSelectionWithGroups
- [x] S3.T10 — Selection Info Bar "📦 GroupName (N)"
- [x] S3.T11 — Snapshot v3 (GroupID per placement + Groups array)
- [x] S3.T12 — DeleteSelected + PruneEmptyGroups + Final test

**10 bug fix (chi tiết `Sprints/Sprint3/Regression_DualDispatcher_Log.md`):**
1. CaptureSnapshot impure timing → TempGroups class var
2. UngroupActors spam snapshot → tách ra ForEach Completed
3. FoundIdx warning → CLEAR -1 đầu hàm
4. Undo về deselect không tắt gizmo → DeselectAll+DeactivateGizmo
5. Ctrl+click group không cộng dồn → bỏ Branch Ctrl ở Mouse Pressed
6. Replace mesh liên tục → thiếu ADD LocalNewActors trong loop
7. Replace khi inventory minimize → EnsureExpanded đầu EnterReplaceMode
8. Replace sai mesh → OnMeshSelected SET nhầm MeshToReplace(dead)
9. Material/Replace folder không auto-update → chuyển từ OnMeshSelected sang OnSelectionChanged
10. Accessed None TargetFurnitureActor → thiếu IsValid guard

**Bug còn mở:** B1 — Undo lần 2 không restore group state → carry-over Gate 1.

---

## SPRINT 4 — COMPLETE ✅ 8/8 (12/06/2026) + 2 bug fix

### Slice 1 — Flat Edit Mode
- [x] S4.T1 — EditModeStack + 7 helper (GetCurrentEditScope, GetChildGroups, GetGroupRoot, WalkUpUntilParent, GetAllDescendantActors đệ quy, GetGroupsInHierarchy đệ quy, ResolveSelectionUnit) + 2 stub (ApplyEditModeVisual, RemoveEditModeVisual) + GetEditBreadcrumb
- [x] S4.T2 — ExpandSelectionWithGroups viết lại dùng ResolveSelectionUnit
- [x] S4.T3 — EnterEditMode / ExitEditModeOneLevel / ExitEditModeFull
- [x] S4.T4 — TryEnterEditFromSelection
- [x] S4.T5 — Info Bar: BTN_EnterEdit + HB_EditModeBar (TXT_EditBreadcrumb + BTN_ExitOneLevel + BTN_ExitFull) + bind OnEditModeChanged; Sequence.Then 2 visibility BTN_EnterEdit

### Slice 2 — Nested Group
- [x] S4.T6 — CreateGroup: ParentGroupID = GetCurrentEditScope() (1 dòng)
- [x] S4.T7 — PruneEmptyGroups (GetAllDescendantActors thay GetGroupChildren) + UngroupActors peel-one-level (WalkUpUntilParent, B1 actor→cha, B2 rebuild groups, B3 xóa target)

### Safety
- [x] S4.T8 — ValidateEditMode (BP_UndoManager) + chèn sau SyncGroupsToContainer trong RestoreSnapshot

### Polish
- [⏭] S4.T9 — Dimming stub — SKIP (optional MVP)

**2 bug fix (phát hiện trong Sprint 4):**
- Bug 2: GroupID lost sau Replace Mesh → SET NewActor.GroupID = OldActor.GroupID trong BTN_ChangeMesh loop (WBP_DragOverlay_FurnitureCard) ✅
- Bug: Branch(ancestor === "") nhầm thành anchor != "" → đổi lại đúng trong ResolveSelectionUnit ✅

**Bug còn mở (lên Gate 1):**
- B1: Undo lần 2 không restore group state → Gate 1
- Replace folder sai khi group nhiều mesh khác folder → deferred Sprint 5

---

## SPRINT 4 BUG FIX — COMPLETE ✅ (15/06/2026)

**5 bug fix bổ sung (session 15/06/2026):**

- [x] **F1** — Info bar hiển thị đúng unit name (GetSelectionUnitLabel trong BP_FurnitureInputManager v1.9)
- [x] **F2** — Group name counter monotonic (GroupNameCounter chuyển sang BP_GroupsContainer, SaveGame=True)
- [x] **F3** — CreateGroup bottom-up nesting (ComputeSelectionUnits + rewrite CreateGroup)
- [x] **F4** — Spawn auto-join edit scope (SpawnFurnitureCopy + WBP_DragOverlay On Drop)
- [x] **A12** — Edit mode bar ẩn sau Undo với group có sẵn (EditModeStack vào S_SceneSnapshot V=4)

**Full test suite PASS (15/06/2026):**
- Batch 1 (Group cơ bản A1-A4): ✅
- Batch 2 (Edit Mode flat B1-B5): ✅ (B3 gizmo = known pre-existing)
- Batch 3 (Nested C1-C4): ✅
- Batch 4 (Sub-group ungroup D1-D3 + Nesting cap): ✅
- Batch 5 (Info bar + Counter E1-E3): ✅
- Batch 6 (F4 confirm + Regression S1-S4): ✅

**Known issue (pre-existing, không phải regression):**
- B3-gizmo: Gizmo ẩn sau undo trong edit mode dù đang ở Move mode

---

## GATE 1 — COMPLETE ✅ (16/06/2026)

- [x] G1.1 — Fix B1: bIsRestoring flag trong BP_UndoManager. Verify: hist ổn định qua nhiều lần restore liên tiếp, info bar + scene state đúng tại mọi điểm kể cả ranh giới Ungroup/CreateGroup.
- [x] G1.2 — Hợp nhất spawn: RestoreSnapshot Step 4 gọi SpawnFurnitureCopy(bAutoSelect=False) qua cached ref (RestoreInputMgr), xóa code spawn inline cũ. Bug phát hiện trong test: bAutoSelect bị wire nhầm thành True → tất cả item bị select sau mọi lần restore → fix lại False. 5/5 test case PASS (case "crash khi tắt PIE sau Save/Load/Undo" — defer, nghi GPU/VRAM, verify ở Gate 2).
- [x] G1.3 — Dọn doc drift (cập nhật PROGRESS.md, DEVIATIONS.md, Session_State.md, BP_UndoManager.md v1.10).

→ Tiếp theo: Sprint D (Data Layer v2). Đọc `02_Current_Sprint.md` phần Sprint D khi bắt đầu.

---

## SPRINT D — Data Layer v2 (17/06/2026) ✅ HOÀN THÀNH

- [x] D.T1 — Single-instance inventory toggle Visibility + box-select guard
      (Is In Viewport → Get Visibility)
- [x] D.T2 — Data prep: S_FurnitureData +ThumbnailSoft (Soft Object Ref Texture2D)
      + Python populate
- [x] D.T3 — FilterFurnitureRows C++ (mirror FilterMaterialItems, cached FProperty
      reflection, KHÔNG reinterpret_cast vì S_FurnitureData là UserDefinedStruct)
      — verify PASS: rỗng → 2114 rows, "sofa" → 136 rows
- [x] D.T4 — BP_FurnitureItemView (Object class, 10 field: RowName/VieName/EngName/
      ThumbnailSoft/MeshSoft/MeshFolderPath/BoundingSize/Description/Link/Category)
- [x] D.T5 — FilterBySearch nhánh Furniture rewire: FilterFurnitureRows →
      AllFilteredFurnitureRows → DisplayPage. Recent/Favorite bypass C++ filter,
      build trực tiếp từ BP_FurnitureUserPrefsManager.
- [x] D.T6 — Bỏ FurnitureDA, Replace Mesh đọc RowName từ actor (17/06/2026) ✅
  - BP_FurnitureActor.md v1.2: thêm RowName SaveGame
  - WBP_DetailPopup.md v1.2: InitPopup(RowName), RowData
  - WBP_MeshControls.md v1.7: BTN_Info RowName, UpdateDetailPopup bound OnSelectionChanged
  - WBP_DragOverlay_FurnitureCard.md v1.6: CardRowName, RowData, PendingRowName
  - WBP_FurnitureCard.md v1.0: TẠO MỚI
  - WBP_FurnitureInventory.md v2.5: OnCardInfoClicked(RowName), OnMeshSelected RowName branch
  - FilterByCategory_Logic.md v1.3: Recent/Favorite DT direct
  - FilterBySearch_Logic.md v1.3: FilterFurnitureRows + DisplayPage
  - BP_FurnitureInputManager.md v1.10: StartReplaceMode doc + RowName branch
  - Fix B-folder + B-stale-popup
- [x] D.T7 — BuildFolderTree C++ source swap (DT_FurnitureCatalog thay
      AllFurnitureItems) + xóa preload AllFurnitureItems khỏi Event Construct
      Then 1. Bug phụ phát hiện & fix: substring/Contains sai khi tìm Folder
      "Table" (Map_Find.Value chứ không phải ReturnValue/Found).
- [x] D.T8 — WBP_FurnitureInventory dùng đầy đủ luồng DataTable+RowName (R5),
      tích hợp xong qua D.T5+D.T6+D.T7.
- [x] D.T9 — Regression toàn bộ (9/9 PASS) + dọn doc — xem mục D.T9 bên dưới.

**Lưu ý:** bảng D.T1-D.T9 ở bản trước bị lệch nhãn (vd dòng "D.T2" ghi nhầm nội
dung của D.T7, dòng "D.T5"/"D.T8" ghi nhầm nội dung D.T3) — bảng trên đã map lại
đúng theo định nghĩa gốc trong `02_Current_Sprint.md`.

### D.T9 — Regression 9 case (17/06/2026)

| # | Case | Kết quả |
|---|---|---|
| 1 | Browse: search "sofa", folder Table, pagination, tab Material↔Furniture, Recent/Favorite | PASS |
| 2 | Mở/đóng inventory 10 lần qua nút + BTN_Close, click trái chọn ngay lần đầu | PASS |
| 3 | Drag-drop spawn 1 mesh + nhiều mesh liên tiếp | PASS |
| 4 | Replace 1 mesh + multi-replace | PASS |
| 5 | Popup ⓘ — tên/category/description đúng | PASS |
| 6 | Save → Load → mesh đúng vị trí, RowName giữ nguyên | PASS |
| 7 | Undo/Redo sau spawn, replace, group, multi-select | PASS |
| 8 | Box select: đóng inventory không hiện khung; mở lại chạy bình thường | PASS |
| 9 | PIE liên tiếp 3 lần, không crash VRAM bất thường | PASS |

**2 bug phụ phát hiện trong lúc test case 1, đã fix:**

- **Bug-Pagination:** Furniture dừng ở "7/8" dù hiển thị ban đầu đúng "1/8".
  Root cause: `Ceil(LENGTH / PageSize)` ở nhánh check nút Next dùng Int Divide
  (337÷48=7, mất phần dư) trong khi `DisplayPage` dùng Float Divide (337/48=7.02
  → Ceil=8) — 2 chỗ tính `TotalPages` lệch nhau 1. Fix: chèn `Int to Float` giữa
  LENGTH và input A của node `÷`, ở CẢ 2 nhánh Material và Furniture (cấu trúc
  copy giống nhau). Verify: Next liên tục → đúng dừng ở "8/8".
- **Bug-Maximize:** `BTN_Maximize` chỉ nở ngang từ vị trí cũ, không nhảy lên
  góc trên-trái như Maximize chuẩn. Root cause: cả 2 nhánh Maximize/Restore chỉ
  gọi `Set Size` trên Canvas Slot của `VerticalBox_0`, thiếu `Set Position` trên
  CÙNG slot. Fix: thêm `Set Position` vào cùng node `Slot as Canvas Slot(VerticalBox_0)`,
  ở cả 2 nhánh — Maximize: Position=(0,0); Restore: Position=Original Position.
  Verify: Maximize đúng góc, Restore đúng vị trí/size cũ, drag sau Restore vẫn ổn.

---

## TÍNH NĂNG BỔ SUNG — TreeNode/Chip Active-Folder Highlight (18/06/2026) ✅

Không nằm trong scope Sprint D gốc — phát sinh từ yêu cầu UX: category/folder
đang chọn trong inventory phải đổi màu và giữ màu khi đi sâu vào folder con.

- `WBP_TreeNode.RefreshDisplay` thêm param `bIsActive` → SetBackgroundColor.
- `WBP_ChipTag` thêm Custom Event `SetHighlight(bIsActive)` tương tự.
- Function Pure mới `IsPathActive(ThisPath)` trong `WBP_FurnitureInventory`:
  `CurrentFolderPath==ThisPath OR CurrentFolderPath StartsWith(ThisPath+"/")`.
- Function `UpdateFolderHighlights` (impure): loop cây TreeNode + loop chip rows,
  gọi `IsPathActive` bằng FolderPath của TỪNG widget, set highlight tương ứng.
  3 điểm gọi: cuối `CreateChipTagsForPath`, trong `OnChipTagClicked` (2 nhánh
  merge), và SAU `FilterByFolderPath` ở cả 2 nhánh `OnTreeNodeClicked`.
- Fix kèm: `BTN_FavoriteCategory`/`BTN_RecentCategory` không ẩn chip cũ khi
  chuyển category đặc biệt — thêm `ClearChildren(VB_ChipTagArea)` +
  `SetVisibility(TB_Breadcrumb, Collapsed)` đầu function.
- Test full: chuyển tab, click cấp 1, vào sâu chip cấp 2/3, quay lại "All",
  Recent/Favorite — tất cả PASS.

Chi tiết kỹ thuật: `WBP_FurnitureInventory.md` v2.6 + `WBP_TreeNode.md` + `WBP_ChipTag.md`.

**Tiếp theo:** Sprint 5 — Combo Mesh, deadline 20/06/2026.

---

## GATE 1 + SPRINT D (kế hoạch chi tiết)

**Gate 1:** fix B1 (bIsRestoring guard) + hợp nhất spawn → ✅ DONE (16/06)

**Sprint D:** Data Layer v2 (Furniture mode nhân bản kiến trúc Material mode) → ✅ DONE (17/06)

---

## SPRINT 5 — Combo Mesh 🔄 IN PROGRESS (cập nhật 23/06/2026)

- [x] **T1** — C++ ComboTypes + ComboSerializer (schema v1, round-trip JSON PASS). Build.cs: Json + JsonUtilities. ✅ 21/06/2026
- [x] **T2 core** — SaveComboFromSelection + CB_SaveCombo trong BP_ComboManager (Actor riêng, spawn Level BP). ✅ 21/06/2026
- [x] **C0** — Sửa SaveComboFromSelection nested: LCA + GetGroupsInHierarchy gom cả cây. 3 case A/B/C PASS. ✅ 22/06/2026
- [x] **C1** — FComboData.FolderPath (C++), FindMaterialRowNameByPath (C++), S_GroupData.SourceComboID (BP), FavoriteComboIDs/RecentComboIDs (UserPrefs). ✅ 22/06/2026
- [x] **C2** — SpawnComboByID + group cha SourceComboID. 7/7 PASS. ✅ 22/06/2026
- [x] **C3a** — Data layer: 2 field C++ (AuthorID/Visibility), BP_ComboItemView.FolderPath, LoadComboLibrary wire, SaveComboFromSelection signature mở rộng, GetExistingFolders+GetAllUsedTags. ✅ 23/06/2026
- [x] **C3b** — WBP_SaveComboDialog (dialog async lưu combo: ExistingFolders dropdown + folder mới + tags + validate). CB_SaveCombo → OpenSaveComboDialog (inventory đóng băng selection + UI-only mode). ✅ 24/06/2026
- [ ] **Fix K3** — SpawnFurnitureCopy thêm `bAddToRecent : Boolean = True`; spawn combo + RestoreSnapshot truyền False. (Áp lúc đụng C2/RestoreSnapshot)
──── **Giai đoạn 1 (~25/06): combo Tạo + Duyệt + Đặt qua nút** ────
- [ ] **C3** — Save dialog + gộp P4 (GetCombosDir → `%LOCALAPPDATA%/InteriorFOFFTool/Combos`) + móc capture thumbnail sau SaveComboFromSelection thành công
- [ ] **Thumbnail System C++ (P1)** — `SaveRenderTargetToPNG` + `LoadTexture2DFromFile`; SceneCapture2D theo góc camera → PNG. Gắn vào C3/C4.
- [x] **C4** — WBP_ComboCard + ghost + drag-drop + CalculateComboAnchor + CTV_ComboCard. Ghost offset FIXED (Approach B). ✅ 25/06/2026
- [ ] **C5** ⏳ IN PROGRESS — 7 sub-task:
  - [x] C5.1 — C++ 3 helper (UpdateComboFolder/RenameFolderPrefix/ClearFolderPrefix) ✅ 25/06
  - [x] C5.0 — tree + filter browse ✅ DONE (26/06)
  - [x] WBP_LibraryContextMenu — Clone WBP_ContextMenu; Z-order fix D12 ✅ DONE (26/06)
  - [x] C5.2 — Inline rename folder: WBP_EditableLabel + WBP_TreeNode v1.3 + Inventory v3.3 ✅ DONE (27/06)
  - [x] C5.4 — Move Folder: WBP_MoveToFolderDialog + WBP_MoveFolderRow (mới) + S_FolderTargetEntry + WBP_FurnitureInventory v3.4 ✅ DONE (30/06)
  - [x] **Issue 2** — Chip highlight combo side: UpdateComboFolderHighlights() NEW (WBP_FurnitureInventory v3.5) ✅ DONE (01/07)
  - [x] **C5.5** — Move Combo: WBP_ComboCard v1.1 + WBP_FurnitureInventory v3.5 (OnComboCardRightClicked/CB_MoveCombo/HandleMoveComboConfirmed). BUG FIX 4.1/4.2/4.3. ✅ DONE (01/07)
  - [x] **NF** — Tạo folder mới: context menu action ✅ DONE (04/07) — C++ Folders.json+GetAllFolderPaths, WBP_FurnitureInventory v3.6 (helpers+OnRequestNewFolder+CB_CreateNewFolder). Nút "+" đầu cột tree (NF.G3) ✅ DONE (06/07) — sentinel `__NEWFOLDER__`, tái dùng OnRequestNewFolder.
  - [x] C5.6 — Xóa folder ✅ DONE (06/07) — WBP_ConfirmDialog mới + ClearFolderPrefix (đã có từ C5.1)
  - [x] C5.7 — ChipTag right-click + rename ✅ DONE — 7a (right-click+menu) DONE (06/07), 7b (inline rename, fallback tree→chip) DONE (06/07 tối). **C5 — FOLDER MANAGEMENT HOÀN TẤT.**
  - [~] **C5.8** — Folder Tree Picker Unify (Move Dialog + Save Dialog) 🔄 IN PROGRESS — gộp lõi data (`BuildComboFolderTreeNodes`/`S_FolderTreeNode`) + component (`WBP_FolderTreePicker`/`WBP_FolderPickerRow`) dùng chung cho Move+Save, thay `WBP_MoveFolderRow` + folder-field cũ của Save. Slot chốt: NGAY SAU C5, TRƯỚC C9. Plan: `docs/Sprints/Sprint5/C5.8_FolderTreePicker_Unify_Plan.md`.
    - [x] Task Card #1 (Data Layer) ✅ DONE (08/07) — rename `S_FolderTargetEntry`→`S_FolderTreeNode`, `BuildFolderTreeRecursive`+`GetFilteredChildren` mới, wrapper `BuildComboFolderTreeNodes` (tên đổi khác plan). Test Print PASS.
    - [x] Task Card #2 (UI component `WBP_FolderTreePicker`+`WBP_FolderPickerRow`, 2a→2d rename host) + Wire Move + Wire Save — build + test node-level ✅ DONE (13/07) — trả nợ test toàn bộ (M1-M6, S6a-c, 0.3, Phần 2 test 1-2). 3 bug fix phát hiện lúc test (`BuildMoveFolderTargetList` sót 2 call site, `SetSelectedHighlight` sai biến, `SetLabelColor` type correction). REG C5.8 (regression cuối) 🔲 CHƯA chạy — bước tiếp theo.
- [ ] **C5** — Folder tree tab 🧩 Combo trong WBP_FurnitureInventory
- [ ] **C6** — Favorite + Recent combo
- [ ] **C7** — WBP_ComboDetailPopup (thumbnail thật)
──── **Giai đoạn 2: đặt/thay combo mượt** ────
- [ ] **WBP_Toast (K1)** — TIÊN QUYẾT trước C8: text + tự ẩn 2-3s, FText
- [x] **C8** — Drag-drop + surface-snap ✅ **MERGED vào C4** (24/06/2026)
- [ ] **Xoay combo (P3)** — verify gizmo group xoay cả cụm; tùy chọn xoay-lúc-kéo (R/scroll)
- [ ] **C9** — Replace combo (+ verify K2 EMS SourceComboID + CalculateCenter chung + auto-rollback spawn-fail)
──── **Giai đoạn 3: share** ────
- [ ] **C11** — Export/Import cả 2 hướng (K5): file-save dialog TRƯỚC, fallback thư mục cố định
- [ ] **C10** — Regression (K4 nested-3 / P5-liên quan / VRAM stat rhi) + Docs
→ **Sprint 7** — Material name-based slot (P5 triệt để — mở màn)

**⚠️ Phiên 21/06:** Kiến trúc v2.0 chốt — scope mở rộng thành Combo Library đầy đủ.
**⚠️ Phiên 23/06:** P1(thumbnail C++)+P2(surface snap)+P3(xoay) làm scope phình → chia 3 giai đoạn. Deadline 25/06 chỉ xong Giai đoạn 1. Xem DEVIATIONS.md 23/06 + Sprint5_Plan_v1.1.
**Deviation:** xem DEVIATIONS.md Sprint 5 (21/06 + 23/06).

---

## SPRINT 6-7 — Chưa bắt đầu

---

## Lịch sử cập nhật

| Ngày | Nội dung |
|------|----------|
| 21/06/2026 | Sprint 5 T1+T2 DONE. Thêm entry Sprint 5. Phiên kiến trúc v2.0: thay T3-T8 bằng C0-C10, tổng Sprint 5 = 13 task, TỔNG 55/96 |
| 22/06/2026 | Sprint 5 C0 ✅ DONE — 3 case A/B/C PASS, RowName fallback xác nhận. |
| 23/06/2026 | Sprint 5 C1+C2 ✅ DONE. Chốt 11 quyết định + 3 điều chỉnh (Sprint5_Plan_v1.1). Thêm task: Fix K3, Thumbnail System C++, WBP_Toast, Xoay combo P3, C11 (trước C10). Chia 3 giai đoạn. TỔNG Sprint 5: 5/17. |
| 24/06/2026 | C3b ✅ DONE. C4 ⏳ 80%: WBP_ComboCard + ghost + drag-drop flow + CalculateComboAnchor + CTV_ComboCard (19 combo PASS). C8 ✅ MERGED vào C4. Bug OPEN: B-ghost-offset. TỔNG Sprint 5: 8/17 (C3a+C3b+C8 done). |
| 25/06/2026 | B-ghost-offset ✅ FIXED. C4 ✅ 100% DONE. C5.1 ✅: 3 C++ folder helpers. C5.0 ⏳ ~90%: tree PASS, card render bug open. TỔNG Sprint 5: 10/17 (C4+C5.1 done). |
| 26/06/2026 | C5.0 ✅ DONE: PopulateComboTreeColumn 2-cấp+D9 guard, OnComboTreeNodeRightClicked, WBP_LibraryContextMenu (Z-order D12). B-C5-card ✅ FIXED (Entry Widget Class verify). TỔNG Sprint 5: 12/17. |
| 27/06/2026 | C5.2 ✅ DONE: WBP_EditableLabel v1.0 (inline rename component). WBP_TreeNode v1.3 + WBP_FurnitureInventory v3.3. BUG FIX RefreshComboFolderUI +PopulateComboTreeColumn. 6 test PASS. TỔNG Sprint 5: 12/17 (task count unchanged — C5.0+WBP_LibraryContextMenu bundled). |
| 30/06/2026 | C5.4 ✅ DONE: Move Folder — WBP_MoveToFolderDialog + WBP_MoveFolderRow (mới). S_FolderTargetEntry struct mới. WBP_FurnitureInventory v3.4 (MovingFolderPath + CollectFolderTargets + BuildMoveFolderTargetList + OnRequestMoveFolder implement + CB_MoveFolderClick implement + HandleMoveFolderConfirmed NEW). BUG FIX D-C5.4-1 (Array_Append ngược) + D-C5.4-2 (dead-end nhánh True). Backlog reorder: Issue 2 → Move Combo → NewFolder → Xóa folder → ChipTag. TỔNG Sprint 5: 13/17. |
| 01/07/2026 | Issue 2 ✅ + C5.5 Move Combo ✅ DONE: UpdateComboFolderHighlights NEW (Issue 2). WBP_ComboCard v1.1 (InventoryRef + On Mouse Button Down). WBP_FurnitureInventory v3.5 (3 class var + OnComboCardRightClicked + CB_MoveCombo + HandleMoveComboConfirmed). BUG FIX 4.1/4.2/4.3. Learning_System v1.3. TỔNG Sprint 5: 15/19 (+2 backlog task). |
| 04/07/2026 | NF (New Folder) — context menu part ✅ DONE, nút "+" 🔲 CÒN NỢ: C++ GetEmptyFoldersFilePath→Folders.json + GetAllFolderPaths tự-ghi-bổ-sung (kể cả cấp cha) test PASS 6/6. BuildComboFolderTree đổi nguồn sang GetAllFolderPaths test PASS 4/4. WBP_FurnitureInventory v3.6: GetChildFolderNames/GetUniqueNewFolderName/GetNewFolderParent (helpers) + OnRequestNewFolder + CB_CreateNewFolder (tạo cùng cấp node right-click, tự vào rename mode) — test PASS 9/9. Deviation: dialog (NF.G2-G5 gốc) → SUPERSEDED bởi inline rename. TỔNG Sprint 5: 15/19 (NF chưa tính — còn nút "+"). |
| 06/07/2026 | NF.G3 ✅ + C5.6 ✅ + C5.7a ✅ DONE: nút "+" đầu cột tree (sentinel `__NEWFOLDER__`, test PASS 5/5). Xóa folder — WBP_ConfirmDialog mới (generic) + HandleDeleteFolderConfirmed + CB_DeleteFolderClick, Deviation D-C5.6-1 (nhảy về cha thay vì `__ALL__`), test PASS 6/6. ChipTag right-click — WBP_ChipTag v1.2 (+OnChipRightClicked + On Mouse Button Down) bind → OnComboTreeNodeRightClicked, test PASS 3/4 (rename = C5.7b, chưa làm). Refactor + bug fix phát sinh: RebuildChipRowForPath + RefreshChipBreadcrumb (gộp code trùng lặp + fix chip area không tự refresh) — 3 bug fix (dead-end 2/3 nhánh, delimiter sai, BooleanAND→OR); bug fix SelectedPath nhầm biến trong OnComboTreeNodeClicked. WBP_FurnitureInventory v3.7. TỔNG Sprint 5: 17/19 (NF.G3+C5.6 done, C5.7 partial — 7a done/7b nợ). |
| 06/07/2026 (tối) | C5.7b ✅ DONE — **C5 FOLDER MANAGEMENT HOÀN TẤT.** WBP_ChipTag v1.3 (EditLabel_ChipTag thay TextBlock, EnterRenameMode/HandleLabelCommitted, dispatcher OnChipRenameCommitted). WBP_FurnitureInventory v3.8 (RenameTargetChip + OnRequestRenameFolder fallback tree→chip + RebuildChipRowForPath bind). BUG FIX CB_CreateNewFolder (node SET thừa) + CB_RenameFolder (thiếu SET None). TỔNG Sprint 5: 19/19. |
| 07/07/2026 | **C5.8 — Folder Tree Picker Unify 🔲 PLANNED** (chưa tính vào task count): nhận delta kiến trúc v2 (Fable/Opus) — gộp lõi data (`BuildFolderTree`/`S_FolderTreeNode`) + component (`WBP_FolderTreePicker`/`WBP_FolderPickerRow`) dùng chung Move+Save dialog, thay `WBP_MoveFolderRow` + folder-field cũ Save. Slot chốt: NGAY SAU C5, TRƯỚC C9. Plan đầy đủ + 2 Task Card: `docs/Sprints/Sprint5/C5.8_FolderTreePicker_Unify_Plan.md`. Chưa thực thi. |
| 08/07/2026 | **C5.8 Task Card #1 (Data Layer) ✅ DONE** (chưa tính vào task count): rename `S_FolderTargetEntry`→`S_FolderTreeNode` (+4 field); `CollectFolderTargets`→`BuildFolderTreeRecursive` (depth guard=12) + `GetFilteredChildren` mới (Pure); wrapper `BuildComboFolderTreeNodes(ExcludePath)` — tên đổi khác plan gốc, log DEVIATIONS.md. Test Print PASS (8 combo, nested 3 tầng, tiếng Việt). WBP_FurnitureInventory v3.9. Tiếp theo: Task Card #2 (UI component). |
| 10-11/07/2026 | **C5.8 Task Card #2 (UI component)** (chưa tính vào task count): 2a `WBP_FolderPickerRow` (row tĩnh + guide line) ✅ PASS full data thật. 2b Part A (hierarchy BTN_Arrow/BTN_Name, dispatchers, `SetExpanded`) ✅ DONE. Part B lần 1 🔄 IN PROGRESS: Variables + toolbar + `SB_SearchFolder`, `IsPathVisible`, `RefreshVisibleRows`, `SetFolders` bug fix, 2 Custom Event handler DONE — **bug #2 OPEN** (test mục 2 FAIL, đang debug theo `docs/Sprints/Sprint5/C5.8_TaskCard2_FixPlan_11jul2026.md`). Doc mới: `WBP_FolderTreePicker.md` v0.9, `WBP_FolderPickerRow.md` v1.0. |
| 11/07/2026 13:14 | **C5.8 Task Card #2 Part B — Giai đoạn 1 ✅ DONE**: bug #2 root cause = `SetNode` thiếu `SET RowNode = Node` + `BTN_Arrow` không đồng bộ Visibility với `TXT_Arrow`. Fix xong (`WBP_FolderPickerRow.md` v1.1). Đính chính lần 2: as-built THẬT nối THẲNG `OnClicked→Call dispatcher`, KHÔNG Custom Event trung gian (đảo ngược [DOC-FIX] trước đó) — áp dụng cho cả BTN_Arrow/BTN_Name và 2 handler mới BTN_ExpandAll/BTN_CollapseAll (`WBP_FolderTreePicker.md` v1.0). Test mục 1-5 PASS. Tiếp theo: Giai đoạn 2 (search). |
| 12/07/2026 10:40 | **C5.8 Task Card #2 Part B — Giai đoạn 2 (Search) + Giai đoạn 3 (Select) ✅ DONE**: 3 Function mới trên `WBP_FolderTreePicker` (`PathMatchesQuery`/`BuildSearchOverride`/`GetParentPath`) + `RefreshVisibleRows` ghép xong nhánh search + wire `SB_SearchFolder.OnSearchTextChanged` (`WBP_FolderTreePicker.md` v1.1). `SetSearchHighlight(bMatch)` DONE trên `WBP_FolderPickerRow` (`WBP_FolderPickerRow.md` v1.2). Bug fix: `PathMatchesQuery` dùng nhầm `Path` đầy đủ thay `DisplayLabel`; arrow-click node đang match trong lúc search không lộ con (thêm `GetParentPath`). Test mục 1-10 PASS hết — **Task Card #2 Part B + 2c HOÀN TẤT.** Tiếp theo: Giai đoạn 4 (Chốt sổ — comprehension check còn nợ 2 câu) → 2d (rename host) → wire Move → wire Save + Create Folder → REG C5.8. |
| 13/07/2026 | **C5.8 Task Card #2 (2d rename host) + Wire Move + Wire Save — build + test node-level DONE** (chưa tính vào task count): `WBP_FolderPickerRow.md` v1.3 (`TXT_Name`→`EditableLabel_Name` + `EnterRenameMode`/`HandleLabelCommitted`/dispatcher `OnRowRenameCommitted`/`GetRowPath` (2d Phần 1); `TXT_CurrentTag`+`SetCurrentTag`/`SetSelectedHighlight` (Card 1)). `WBP_EditableLabel.md` v1.1 (`SetLabelColor`). `WBP_FolderTreePicker.md` v1.3 (`BeginRenameOnPath`/`ExpandToPath` (2d Phần 2); var `CurrentPath`/`bShowCurrentTag` + dispatcher `OnRequestCommitRename` (Card 1)). `WBP_MoveToFolderDialog.md` v2.0 + `WBP_SaveComboDialog.md` v2.0 — cả 2 chuyển hẳn sang dùng `WBP_FolderTreePicker` (xoá `WBP_MoveFolderRow`/`CMB_Folder` cũ, SUPERSEDED không xoá file). `WBP_FurnitureInventory.md` v3.11 — `OnRequestMoveFolder`/`CB_MoveCombo` gọi `Dialog.InitPicker`; `OpenSaveComboDialog` wire Picker + 2 Custom Event mới `HandleSaveDialogCreateFolder`/`HandleSavePickerRenameCommitted`; `BuildMoveFolderTargetList` xoá hẳn khỏi Blueprint. 3 bug fix phát hiện lúc test: `BuildMoveFolderTargetList` sót 2 call site (claim "Blueprint tự propagate" ở v3.9 SAI), `SetSelectedHighlight` so sai biến (CurrentPath thay SelectedPath), `SetLabelColor` type correction (Slate Color không phải Linear Color). Test PASS: M1-M6, S6a/S6c, 0.3, Phần 2 test 1-2. **REG C5.8 (regression cuối) CHƯA chạy — bước tiếp theo, sau đó mới cho phép sang C9.** |
