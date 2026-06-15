# Session State
**Cập nhật:** 11/06/2026 — 18:14 ICT | Lighting_Mnger UE5.5.4

---

## TRẠNG THÁI HIỆN TẠI

### Sprint 4 — Edit Mode + Nested Group: ĐANG LÀM

**Slice 1 (flat edit mode) — ĐÃ HOÀN THÀNH T1–T5:**

| Task | Status | Ghi chú |
|---|---|---|
| T1 — EditModeStack + 7 helper + ResolveSelectionUnit + 2 stub | ✅ PASS | Test 4 helper OK (GetCurrentEditScope="", GetAllDescendantActors=3, GetGroupsInHierarchy=1, GetGroupRoot=gid) |
| T2 — ExpandSelectionWithGroups dùng ResolveSelectionUnit | ✅ PASS | Click group phẳng → cả group chọn |
| T3 — EnterEditMode / ExitEditModeOneLevel / ExitEditModeFull + GetEditBreadcrumb | ✅ PASS | F8 vào edit (Stack=1), click 1 đồ → 1 đồ chọn, F7 thoát (Stack=0) |
| T4 — TryEnterEditFromSelection | ✅ PASS | F8 → TryEnterEdit → Stack=1. Guard đồ rời OK |
| T5 — Info Bar: BTN_EnterEdit + HB_EditModeBar + bind OnEditModeChanged | ✅ (UI done) | BTN_EnterEdit hiện khi chọn group. Test full flow còn nợ confirm |

**Test Slice 1 nợ xác nhận:**
- Bấm ✏️ → breadcrumb "✏️ Đang chỉnh: [tên group]" hiện
- Click 1 đồ trong edit → chỉ 1 đồ chọn
- Click vùng trống khi edit → selection rớt, bar vẫn còn
- Bấm ✖ Thoát → bar ẩn, cả group chọn lại

**Tiếp theo:**
- TEST SLICE 1 đầy đủ (nếu chưa xong)
- T6 — CreateGroup nested (sửa 1 dòng ParentGroupID)
- T7 — PruneEmptyGroups + UngroupActors deep
- T8 — ValidateEditMode trong RestoreSnapshot
- T9 — Dimming stub (optional)

---

## BUG CÒN MỞ

| # | Bug | Nguồn | Ưu tiên |
|---|---|---|---|
| B1 | Undo lần 2 không restore group state (Groups.Length=0 sau restore) | Sprint 3 carry-over | 🟡 Trung |

---

## ĐÃ HOÀN THÀNH (trước Sprint 4)

- Change Material v1.1 (20/05/2026) — tất cả UX fixes done
- UX Phase 2.1: Gizmo, Nudge, Copy/Paste, Recent/Favorite
- Resize Window 8 hướng (WBP_FurnitureInventory)
- Sprint 3 Group cơ bản: S_GroupData, BP_GroupsContainer, CreateGroup (Ctrl+G), UngroupActors (Ctrl+Shift+G), ExpandSelectionWithGroups, snapshot v3, PruneEmptyGroups
- Sprint 4 Slice 1 (T1–T5): EditModeStack, 7 helper đệ quy, ResolveSelectionUnit, Enter/ExitEditMode, UI info bar

---

## KIẾN TRÚC HIỆN TẠI

**BP_FurnitureInputManager v1.7** — input hub + multi-select + box-select + context-menu + group + edit mode hub
**BP_UndoManager v1.6** — snapshot v3 (Groups + GroupID per placement)
**WBP_MeshControls v1.5** — persistent toolbar + selection info bar + edit mode bar
**BP_GroupsContainer** — EMS save/load groups, singleton guard

**Dispatcher selection:** `OnSelectionChanged` — DUY NHẤT
**Dispatcher edit mode:** `OnEditModeChanged(bActive, GroupID)` — MỚI Sprint 4

---

## NGUYÊN TẮC ĐỌC DOC ĐẦU SESSION

1. Đọc `Session_State.md` TRƯỚC
2. Đọc `Sprint4_Execution_Opus.md` khi làm Sprint 4
3. Đọc `BP_FurnitureInputManager_v1.7_patch.md` khi cần node flow chi tiết Sprint 4
4. Đọc `Blueprint_Logic.md` khi cần flow các hàm Sprint 1–3

---

## TIẾP THEO (sau Sprint 4)

- Sprint 5: Combo mesh serialization (dùng GetGroupsInHierarchy bridge)
- Refactor Phase B: AssetService, Event Bus, Command pattern Undo
- glTFRuntime → Supabase → Share → Combo → Interactive
