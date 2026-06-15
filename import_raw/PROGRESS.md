# PROGRESS — Tiến độ Multi-Select / Group / Combo / Material v1.2
**Cập nhật:** 12/06/2026 — 15:04 ICT

---

## TỔNG QUAN

```
Sprint 1 — Multi-select       ███████████████ 15/15 SHIPPED ✅
Sprint 2 — Box + Context Menu ████████████████ 9/9  SHIPPED ✅
Sprint 3 — Group cơ bản       ████████████████ 12/12 SHIPPED ✅  (+10 bug fix)
Sprint 4 — Edit + Nested      ████████         8/8  SHIPPED ✅  (+2 bug fix)
Sprint 5 — Combo Mesh         ░░░░░░░░         0/8  task
Sprint 6 — Polish UX          ░░░░░░░░░░░░░    0/14 task
Sprint 7 — Material v1.2      ░░░░░░░░░        0/9  task

TỔNG: 44/82 task
```

---

## SPRINT 1 — COMPLETE ✅ (15/15)

T1-T15 shipped. Chi tiết: BP_FurnitureInputManager.md, BP_PivotActor.md.

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

**10 bug fix (chi tiết Sprint3_Regression_DualDispatcher_Log.md):**
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

**Bug còn mở:**
- B1: Undo lần 2 không restore group state → Gate 1
- Replace folder sai khi group nhiều mesh khác folder → deferred Sprint 5

---

## GATE 1 + SPRINT D (tiếp theo)

**Gate 1:** fix B1 (bIsRestoring guard) + hợp nhất spawn → Đọc Gate1_SprintD_Execution_Opus.md

**Sprint D:** Data Layer v2 (Furniture mode nhân bản kiến trúc Material mode)

---

## SPRINT 5-7 — Chưa bắt đầu
