# PROGRESS UPDATE — Sprint 4 Bug Fix Session (15/06/2026)
> Thêm vào PROGRESS.md, section Sprint 4.

---

## Cập nhật tổng quan

```
Sprint 4 — Edit + Nested      ████████████████ 8/8  SHIPPED ✅  (+5 bug fix thêm)
Gate 1                        ░░░░░░░░         0/3  task (tiếp theo)
```

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

## GATE 1 — tiếp theo

- [ ] G1.1 — Fix B1: thêm bIsRestoring flag trong BP_UndoManager
- [ ] G1.2 — Hợp nhất spawn: SpawnFurnitureCopy thay spawn inline trong RestoreSnapshot Step 4
- [ ] G1.3 — Dọn doc drift

Đọc `Gate1_SprintD_Execution_Opus.md` khi bắt đầu.
