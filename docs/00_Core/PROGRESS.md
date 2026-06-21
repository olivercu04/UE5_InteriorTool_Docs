# PROGRESS — Tiến độ Multi-Select / Group / Combo / Material v1.2
**Nguồn:** `import_raw/PROGRESS.md` (12/06/2026) + `import_raw/PROGRESS_Sprint4BugFix_update.md` (patch 15/06/2026)
**Cập nhật:** 21/06/2026 (Sprint 5 S5.T1 + S5.T2 DONE)

---

## TỔNG QUAN

```
Sprint 1 — Multi-select       ███████████████ 15/15 SHIPPED ✅
Sprint 2 — Box + Context Menu ████████████████ 9/9  SHIPPED ✅
Sprint 3 — Group cơ bản       ████████████████ 12/12 SHIPPED ✅  (+10 bug fix)
Sprint 4 — Edit + Nested      ████████████████ 8/8  SHIPPED ✅  (+5 bug fix thêm)
Gate 1                        ████████████████ 3/3  DONE ✅ (16/06)
Sprint D — Data Layer v2      ████████████████ 9/9  DONE ✅ (17/06)
Sprint 5 — Combo Mesh         ██░░░░░░░░░░░    2/13 task (T1✅ T2✅ core; C0–C10 ⏳)
Sprint 6 — Polish UX          ░░░░░░░░░░░░░    0/14 task
Sprint 7 — Material v1.2      ░░░░░░░░░        0/9  task

TỔNG: 55/96 task
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

## SPRINT 5 — Combo Mesh 🔄 IN PROGRESS (21/06/2026)

- [x] **T1** — C++ ComboTypes + ComboSerializer (schema v1, round-trip JSON PASS). Build.cs: Json + JsonUtilities. ✅ 21/06/2026
- [x] **T2 core** — SaveComboFromSelection + CaptureComboThumbnail trong **BP_ComboManager** (Actor riêng, spawn Level BP). CB_SaveCombo hoạt động trong context menu right-click. ✅ 21/06/2026
  - ⏳ WBP_SaveComboDialog (dialog nhập tên/folder/tags) — dời C3, không chặn flow
- [ ] **C0** — Sửa SaveComboFromSelection nested: GetGroupRoot+GetGroupsInHierarchy gom cả cây (patch T2 selection-only)
- [ ] **C1** — Nền data C++: FComboData.FolderPath, FindMaterialRowNameByPath, S_GroupData.SourceComboID, prefs favorites/recent
- [ ] **C2** — SpawnComboByID + group cha SourceComboID ⭐ (trái tim sprint)
- [ ] **C3** — WBP_SaveComboDialog (tên, folder, tags, mô tả, thumbnail)
- [ ] **C4** — WBP_ComboCard (thumbnail, badge ×N món, Info/Delete/Spawn)
- [ ] **C5** — Folder tree tab 🧩 Combo trong WBP_FurnitureInventory
- [ ] **C6** — Favorite + Recent combo
- [ ] **C7** — WBP_ComboDetailPopup
- [ ] **C8** — Drag-drop combo (ghost 1 mesh đại diện Items[0], spawn tại cursor)
- [ ] **C9** — Replace combo cả cụm (leo SourceComboID → destroy → respawn)
- [ ] **C10** — Regression + Docs

**⚠️ Phiên 21/06:** Kiến trúc v2.0 chốt — scope mở rộng thành Combo Library đầy đủ (C0-C10). T3-T8 cũ thay bởi C0-C10. Tổng task tăng 8→13. Deadline 25/06 sẽ trượt.
**Deviation:** combo event tách sang BP_ComboManager (19/06, [SCOPE]). SourceComboID group cha, RowName material, drag-drop (21/06, xem DEVIATIONS.md).

---

## SPRINT 6-7 — Chưa bắt đầu

---

## Lịch sử cập nhật

| Ngày | Nội dung |
|------|----------|
| 21/06/2026 | Sprint 5 T1+T2 DONE. Thêm entry Sprint 5. Phiên kiến trúc v2.0: thay T3-T8 bằng C0-C10, tổng Sprint 5 = 13 task, TỔNG 55/96 |
