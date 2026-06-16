# PROGRESS — Tiến độ Multi-Select / Group / Combo / Material v1.2
**Nguồn:** `import_raw/PROGRESS.md` (12/06/2026) + `import_raw/PROGRESS_Sprint4BugFix_update.md` (patch 15/06/2026)
**Cập nhật:** 15/06/2026 (Sprint 4 Bug Fix session)

---

## TỔNG QUAN

```
Sprint 1 — Multi-select       ███████████████ 15/15 SHIPPED ✅
Sprint 2 — Box + Context Menu ████████████████ 9/9  SHIPPED ✅
Sprint 3 — Group cơ bản       ████████████████ 12/12 SHIPPED ✅  (+10 bug fix)
Sprint 4 — Edit + Nested      ████████████████ 8/8  SHIPPED ✅  (+5 bug fix thêm)
Gate 1                        ░░░░░░░░         0/3  task (tiếp theo)
Sprint 5 — Combo Mesh         ░░░░░░░░         0/8  task
Sprint 6 — Polish UX          ░░░░░░░░░░░░░    0/14 task
Sprint 7 — Material v1.2      ░░░░░░░░░        0/9  task

TỔNG: 44/82 task
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

## GATE 1 + SPRINT D (kế hoạch chi tiết)

**Gate 1:** fix B1 (bIsRestoring guard) + hợp nhất spawn → Đọc `02_Current_Sprint.md`

**Sprint D:** Data Layer v2 (Furniture mode nhân bản kiến trúc Material mode)

---

## SPRINT 5-7 — Chưa bắt đầu
