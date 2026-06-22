# Session State
**Cập nhật:** 22/06/2026 | BP_ComboManager v1.3

---

## TRẠNG THÁI HIỆN TẠI

**Sprint 5 — Combo System: IN PROGRESS**

| Task | Status | Ghi chú |
|---|---|---|
| C0 — SaveComboFromSelection (LCA + material RowName) | ✅ DONE | v1.2, 22/06/2026 |
| C2 — SpawnComboByID | ✅ DONE | v1.3, 7/7 PASS, 22/06/2026 |
| C3 — Thumbnail | ⏳ PENDING | |
| C4 — DeleteCombo | ⏳ PENDING | |
| C5 — ReplaceCombo | ⏳ PENDING | |

---

**Sprint 4 — Edit Mode + Nested Group: SHIPPED ✅ (12/06/2026)**

| Task | Status | Ghi chú |
|---|---|---|
| T1 — EditModeStack + 7 helper + ResolveSelectionUnit + 2 stub + GetEditBreadcrumb | ✅ PASS | Test: GetAllDescendantActors=3, GetGroupsInHierarchy=1, GetGroupRoot=gid, GetCurrentEditScope="" |
| T2 — ExpandSelectionWithGroups dùng ResolveSelectionUnit | ✅ PASS | Click group phẳng → cả group chọn |
| T3 — EnterEditMode / ExitEditModeOneLevel / ExitEditModeFull | ✅ PASS | Stack in/out đúng, re-select đúng |
| T4 — TryEnterEditFromSelection | ✅ PASS | Guard đồ rời, giới hạn 3 cấp |
| T5 — Info Bar: BTN_EnterEdit + HB_EditModeBar + BTN_ExitOneLevel + BTN_ExitFull + bind OnEditModeChanged | ✅ PASS | Breadcrumb đúng, nút hoạt động |
| T6 — CreateGroup nested (ParentGroupID = GetCurrentEditScope()) | ✅ PASS | Sub-group tạo đúng parent |
| T7 — PruneEmptyGroups (GetAllDescendantActors) + UngroupActors peel-one-level | ✅ PASS | Actor về cha, sub-groups tồn tại |
| T8 — ValidateEditMode trong RestoreSnapshot (BP_UndoManager) | ✅ PASS | Undo xóa sub-group → breadcrumb tự về cha |
| T9 — Dimming stub | ⏭ SKIP (optional MVP) | |
| Bug 2 — GroupID lost sau Replace Mesh | ✅ FIXED | SET NewActor.GroupID = OldActor.GroupID trong Replace loop |

**Bug còn mở:**
| # | Bug | Nguồn | Ưu tiên |
|---|---|---|---|
| B1 | Undo lần 2 không restore group state (Groups.Length=0) | Sprint 3 carry-over | 🟡 Trung |
| B2 | Replace folder sai khi group nhiều mesh khác folder | Sprint 4 phát hiện | 🟢 Thấp — deferred Sprint 5 combo |

---

## ĐÃ HOÀN THÀNH

- Change Material v1.1 (20/05/2026)
- UX Phase 2.1: Gizmo, Nudge, Copy/Paste, Recent/Favorite
- Resize Window 8 hướng
- Sprint 1 — Multi-select (15/15) ✅
- Sprint 2 — Box+Context Menu (9/9) ✅
- Sprint 3 — Group cơ bản (12/12 + 10 bug fix) ✅
- Sprint 4 — Edit Mode + Nested Group (T1-T8) ✅

---

## KIẾN TRÚC HIỆN TẠI

**BP_FurnitureInputManager v1.8** — input hub + multi-select + box-select + context-menu + group + edit mode hub
**BP_UndoManager v1.7** — snapshot v3 + ValidateEditMode trong RestoreSnapshot
**WBP_MeshControls v1.5** — toolbar + info bar + edit mode bar (BTN_ExitOneLevel + BTN_ExitFull)
**BP_GroupsContainer** — EMS save/load groups, singleton guard
**WBP_DragOverlay_FurnitureCard** — Replace Mesh: preserve GroupID (v fix 12/06)
**BP_ComboManager v1.3** — SaveComboFromSelection (C0) + SpawnComboByID (C2); 5 class var mới, 4 helper functions

**Dispatcher selection:** `OnSelectionChanged` — DUY NHẤT
**Dispatcher edit mode:** `OnEditModeChanged(bActive, GroupID)`

---

## TIẾP THEO

**Roadmap v3.1:** Gate 1 (fix B1 Undo + hợp nhất spawn) → Sprint D (Data Layer v2) → Sprint 5 Combo → Sprint 7 Material v1.2 → Sprint 6 Polish → Gate 2

**Gate 1 ưu tiên:** fix B1 (bIsRestoring guard trong BP_UndoManager). Đọc `Gate1_SprintD_Execution_Opus.md` khi bắt đầu.

---

## NGUYÊN TẮC ĐỌC DOC ĐẦU SESSION

1. Đọc `Session_State.md` TRƯỚC
2. Gate 1 / Sprint D → đọc `Gate1_SprintD_Execution_Opus.md` + `09_AI_Implementation_Rules.md`
3. Flow chi tiết Sprint 4 → `BP_FurnitureInputManager.md` v1.8
4. Flow Sprint 1-3 → `Blueprint_Logic.md`
