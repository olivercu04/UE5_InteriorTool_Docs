# RAW INVENTORY — import_raw/

**Tạo:** 15/06/2026  
**Mục đích:** Kiểm kê toàn bộ 113 file raw trước khi merge vào docs/.  
**Trạng thái:** Chỉ đọc và phân loại — chưa merge nội dung.

---

## Tổng quan

| Nhóm | Logical files | Raw files |
|------|:---:|:---:|
| Rules | 3 | 5 |
| Blueprint | 6 | 24 |
| Widget | 7 | 20 |
| Sprint / Execution Plan | 14 | 16 |
| Session State | 1 | 12 |
| Bug / Debug | 2 | 2 |
| Data / Pipeline | 10 | 11 |
| Other | 13 | 23 |
| **TỔNG** | **56** | **113** |

---

## Quy ước đọc bảng

- **Canonical** = file mới nhất / version cao nhất của nhóm → đây là file cần merge vào docs/
- **Older** = số file cũ hơn trong cùng nhóm (chỉ giữ lại lịch sử, không cần merge riêng)
- **Đề xuất merge** = path trong docs/ nên chứa nội dung canonical

---

## 1. Rules

### AI_Communication_Rules

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `AI_Communication_Rules_update_15jun2026.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 15/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Cập nhật Q8 self-check gate và yêu cầu phân biệt L2 branch context; patch bổ sung vào bộ rules giao tiếp giữa AI và project. |
| **Đề xuất merge** | `docs/Rules/AI_Communication_Rules.md` |

---

### AI_Implementation_Rules

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `09_AI_Implementation_Rules_patch_v2.md` |
| **Phiên bản** | 2.0 |
| **Cập nhật** | 14/06/2026 |
| **Older versions** | 1 (`28-05-2026_09_AI_Implementation_Rules.md`) |
| **Chủ đề** | Quy tắc thực thi dành cho AI — tự kiểm tra logic blueprint trước khi output, ghi deviation nếu lệch plan. Patch v2 bổ sung self-check gate mechanism. |
| **Đề xuất merge** | `docs/Rules/09_AI_Implementation_Rules.md` |

---

### Execution_Discipline

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `10_Execution_Discipline_patch_v2.md` |
| **Phiên bản** | 2.0 |
| **Cập nhật** | 14/06/2026 |
| **Older versions** | 1 (`28-05-2026_10_Execution_Discipline.md`) |
| **Chủ đề** | Kỷ luật thực thi — ngăn scope drift, deviation logging, checkpoint system. Patch v2 thêm Luật 6A (symmetric operation: mọi tính năng phải có cả forward lẫn backward path). |
| **Đề xuất merge** | `docs/Rules/10_Execution_Discipline.md` |

---

## 2. Blueprint

### BP_FurnitureInputManager

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `BP_FurnitureInputManager_v1_9_patch.md` |
| **Phiên bản** | 1.9 |
| **Cập nhật** | 15/06/2026 — 20:30 ICT |
| **Older versions** | 8 (v1.1 → v1.4 → v1.5 → v1.6×2 → v1.7×2 → v1.8) |
| **Chủ đề** | Input hub actor trung tâm: quản lý SelectedActors, PrimarySelectedActor, edit mode stack, group system, 7 helper functions. Patch v1.9 fix 4 bug Sprint 4 + thêm GetSelectionUnitLabel. |
| **Đề xuất merge** | `docs/Blueprints/BP_FurnitureInputManager.md` |

Older files (không cần merge riêng):

| File | Version | Ngày |
|------|---------|------|
| `19-05-2026-17h50p_BP_FurnitureInputManager.md` | 1.1 | 19/05/2026 |
| `04-06-2026-15h30p_BP_FurnitureInputManager.md` | 1.4 | 04/06/2026 |
| `07-06-2026-22h40p_BP_FurnitureInputManager.md` | 1.5 | 07/06/2026 |
| `08-06-2026-11h24p_BP_FurnitureInputManager_v1.6_patch.md` | 1.6 | 08/06/2026 |
| `10-06-2026-20h34p_BP_FurnitureInputManager.md` | 1.6 | 10/06/2026 |
| `BP_FurnitureInputManager.md` | 1.7 | 11/06/2026 |
| `BP_FurnitureInputManager_v1.7_patch.md` | 1.7 | 11/06/2026 |
| `BP_FurnitureInputManager_v1.8_patch.md` | 1.8 | 12/06/2026 |

---

### BP_UndoManager

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `BP_UndoManager_v1_8_patch.md` |
| **Phiên bản** | 1.8 |
| **Cập nhật** | 15/06/2026 — 20:30 ICT |
| **Older versions** | 5 (v1.2 → v1.4 → v1.5 → v1.6 → v1.7) |
| **Chủ đề** | Undo/redo manager với snapshot versioning (v1→v4). Patch v1.8 thêm EditModeStack vào snapshot (Version 4) — fix bug undo không giữ trạng thái edit mode. |
| **Đề xuất merge** | `docs/Blueprints/BP_UndoManager.md` |

Older files:

| File | Version | Ngày |
|------|---------|------|
| `16-05-2026-14h08p_BP_UndoManager.md` | 1.2 | 16/05/2026 |
| `04-06-2026-15h30p_BP_UndoManager.md` | 1.4 | 04/06/2026 |
| `07-06-2026-22h40p_BP_UndoManager.md` | 1.5 | 07/06/2026 |
| `10-06-2026-20h34p_BP_UndoManager.md` | 1.6 | 10/06/2026 |
| `BP_UndoManager_v1.7_patch.md` | 1.7 | 12/06/2026 |

---

### BP_GizmoController

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `05-06-2026-20h00p_BP_GizmoController.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 05/06/2026 — 20:00 ICT |
| **Older versions** | 1 (`16-04-2026_BP_GizmoController_OnMouseReleased.md`) |
| **Chủ đề** | Gizmo controller xử lý drag translate/rotate/scale, axis lock, snap step. File cũ chỉ ghi OnMouseReleased event flow cho undo snapshot. |
| **Đề xuất merge** | `docs/Blueprints/BP_GizmoController.md` |

---

### BP_PivotActor

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `05-06-2026-20h00p_BP_PivotActor.md` |
| **Phiên bản** | 1.1 |
| **Cập nhật** | 05/06/2026 — 20:00 ICT |
| **Older versions** | 1 (`04-06-2026-15h30p_BP_PivotActor.md` v1.0) |
| **Chủ đề** | Invisible pivot actor trung gian cho multi-gizmo; v1.1 hỗ trợ đầy đủ rotate và scale qua relative transform composition. |
| **Đề xuất merge** | `docs/Blueprints/BP_PivotActor.md` |

---

### BP_FoffPlayerController

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `25-04-2026_BP_FoffPlayerController.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 25/04/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Player controller gốc — mapping input context và quản lý furniture input mode. Tài liệu tham khảo integration điểm đầu vào. |
| **Đề xuất merge** | `docs/Blueprints/BP_FoffPlayerController.md` |

---

### Blueprint_Logic (Node Flow Reference)

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `Blueprint_Logic_v1_5_patch.md` |
| **Phiên bản** | 1.5 |
| **Cập nhật** | 15/06/2026 — 20:30 ICT |
| **Older versions** | 3 (v1.1, v1.3, v1.4) |
| **Chủ đề** | Tài liệu node flow tham chiếu — ký hiệu notation, flow các function cốt lõi. Patch v1.5 bổ sung learning về branch False dead-end trong Sequence vs Event context. |
| **Đề xuất merge** | `docs/Blueprints/Blueprint_Logic_NodeFlow.md` |

Older files:

| File | Version | Ngày |
|------|---------|------|
| `19-05-2026-17h50p_Blueprint_Logic.md` | 1.1 | 19/05/2026 |
| `07-06-2026-22h40p_Blueprint_Logic.md` | 1.3 | 07/06/2026 |
| `Blueprint_Logic_v1.4_patch.md` | 1.4 | 12/06/2026 |

---

## 3. Widget

### WBP_MeshControls

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `WBP_MeshControls_v1_6_patch.md` |
| **Phiên bản** | 1.6 |
| **Cập nhật** | 15/06/2026 — 20:30 ICT |
| **Older versions** | 7 (v1.1 → v1.2×2 → v1.4 → v1.5×3) |
| **Chủ đề** | Toolbar widget: buttons transform mode, info bar selection count, edit mode bar với breadcrumb + Exit buttons. Patch v1.6 thay inline logic bằng GetSelectionUnitLabel (fix F1). |
| **Đề xuất merge** | `docs/Widgets/WBP_MeshControls.md` |

Older files:

| File | Version | Ngày |
|------|---------|------|
| `25-05-2026-17h29p_WBP_MeshControls.md` | 1.1 | 25/05/2026 |
| `04-06-2026-15h30p_WBP_MeshControls.md` | 1.2 | 04/06/2026 |
| `05-06-2026-20h00p_WBP_MeshControls.md` | 1.2 | 05/06/2026 |
| `10-06-2026-20h34p_WBP_MeshControls.md` | 1.4 | 10/06/2026 |
| `WBP_MeshControls.md` | 1.5 | 11/06/2026 |
| `WBP_MeshControls_v1.5_patch.md` | 1.5 | 11/06/2026 |
| `WBP_MeshControls_v1.5_update.md` | 1.5 update | 12/06/2026 |

---

### WBP_FurnitureInventory

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `WBP_FurnitureInventory.md` |
| **Phiên bản** | 2.4 |
| **Cập nhật** | 11/06/2026 |
| **Older versions** | 4 (v1.5, v2.2, v2.3, v2.4 pre-merge) |
| **Chủ đề** | Inventory widget — bản hợp nhất v2.4: material editor, C++ filter library, resize window, multi-replace, dispatcher refactoring (single OnSelectionChanged). |
| **Đề xuất merge** | `docs/Widgets/WBP_FurnitureInventory.md` |

Older files:

| File | Version | Ngày |
|------|---------|------|
| `19-05-2026-17h50p_WBP_FurnitureInventory.md` | 1.5 | 19/05/2026 |
| `25-05-2026-15h03p_WBP_FurnitureInventory.md` | 2.2 | 25/05/2026 |
| `27-05-2026-10h30p_WBP_FurnitureInventory_patch.md` | 2.3 | 27/05/2026 |
| `10-06-2026-20h34p_WBP_FurnitureInventory.md` | 2.4 | 10/06/2026 |

---

### WBP_DragOverlay_FurnitureCard

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `WBP_DragOverlay_FurnitureCard_v1_5_patch.md` |
| **Phiên bản** | 1.5 |
| **Cập nhật** | 15/06/2026 — 20:30 ICT |
| **Older versions** | 2 (v1.3, v1.4) |
| **Chủ đề** | Drag overlay widget xử lý thả furniture — multi-mesh replace mode, auto-join edit scope khi spawn. Patch v1.5 yêu cầu merge branch critical để spawn vào đúng edit scope. |
| **Đề xuất merge** | `docs/Widgets/WBP_DragOverlay_FurnitureCard.md` |

Older files:

| File | Version | Ngày |
|------|---------|------|
| `25-05-2026-17h29p_WBP_DragOverlay_FurnitureCard.md` | 1.3 | 25/05/2026 |
| `10-06-2026-20h34p_WBP_DragOverlay_FurnitureCard.md` | 1.4 | 10/06/2026 |

---

### WBP_BoxSelectOverlay

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `07-06-2026-22h40p_WBP_BoxSelectOverlay.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 07/06/2026 — 22:40 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Widget vẽ rubber-band box selection rectangle — transparent border, cập nhật size theo drag delta. |
| **Đề xuất merge** | `docs/Widgets/WBP_BoxSelectOverlay.md` |

---

### WBP_DetailPopup

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `25-05-2026-17h29p_WBP_DetailPopup.md` |
| **Phiên bản** | 1.1 |
| **Cập nhật** | 25/05/2026 — 17:29 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Popup hiển thị thông tin sản phẩm: drag support, scale editor cho kích thước furniture. |
| **Đề xuất merge** | `docs/Widgets/WBP_DetailPopup.md` |

---

### WBP_ResizeWindow

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `27-05-2026-10h30p_WBP_ResizeWindow.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 27/05/2026 — 10:30 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Resize window với 8-direction drag, minimum size constraints, variable tracking cho WBP_FurnitureInventory. |
| **Đề xuất merge** | `docs/Widgets/WBP_ResizeWindow.md` |

---

### WBP_Inventory_Card (patch)

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `08-06-2026-11h24p_WBP_Inventory_Card_v2.3_v1.4_patch.md` |
| **Phiên bản** | 2.3 / 1.4 |
| **Cập nhật** | 08/06/2026 — 11:24 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Patch notes cho WBP_FurnitureInventory v2.3 và WBP_FurnitureCard v1.4 — Sprint 2 context menu support và multi-replace handling. |
| **Đề xuất merge** | Hợp vào `docs/Widgets/WBP_FurnitureInventory.md` (section patch notes) |

---

## 4. Sprint / Execution Plan

### MultiSelect_Group_ComboMesh_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `26-05-2026_09h40p_MultiSelect_Group_ComboMesh_Plan_v2.md` |
| **Phiên bản** | 2.0 |
| **Cập nhật** | 26/05/2026 — 09:40 ICT |
| **Older versions** | 1 (v1.0 — 08h51) |
| **Chủ đề** | Plan tổng thể cho toàn bộ 7 sprints: multi-select → group → combo mesh. Keyboard shortcuts, architectural overview, user story. |
| **Đề xuất merge** | `docs/00_Core/Master_Roadmap.md` hoặc `docs/Sprints/00_Overview_Plan.md` |

---

### Sprint1_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `02-06-2026_START_HERE_Sprint1.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 02/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Kickoff Sprint 1: thứ tự đọc tài liệu bắt buộc, project status cho Sonnet 4.6 bắt đầu implement multi-select. |
| **Đề xuất merge** | `docs/Sprints/Sprint1/00_START_HERE.md` |

---

### Sprint1_T15_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `04-06-2026_T15_Multi_Rotate_Scale_Plan.md` |
| **Phiên bản** | 1.1 |
| **Cập nhật** | 04/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Plan chi tiết task T15: multi-rotate/scale qua pivot actor dùng relative transform composition. |
| **Đề xuất merge** | `docs/Sprints/Sprint1/T15_Rotate_Scale_Plan.md` |

---

### Sprint2_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `05-06-2026_Sprint2_Plan_v2.md` |
| **Phiên bản** | 2.0 |
| **Cập nhật** | 05/06/2026 |
| **Older versions** | 0 (addendum: `07-06-2026-23h30p_Sprint2_ContextMenu_ChangeMaterial_Replace_Prep.md`) |
| **Chủ đề** | Sprint 2 plan: box select và context menu, 7 tasks. Giải quyết gizmo trace priority và tránh asset loading performance issues. |
| **Đề xuất merge** | `docs/Sprints/Sprint2/00_Plan.md` |

---

### Sprint2_ContextMenu_Prep

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `07-06-2026-23h30p_Sprint2_ContextMenu_ChangeMaterial_Replace_Prep.md` |
| **Phiên bản** | 1.1 |
| **Cập nhật** | 07/06/2026 — 23:30 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Prep doc cho Sprint 2 context menu callbacks: material picker integration và multi-mesh replacement logic. |
| **Đề xuất merge** | `docs/Sprints/Sprint2/ContextMenu_Prep.md` |

---

### Sprint3_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `08-06-2026-11h24p_Sprint3_Plan_Opus.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 08/06/2026 — 11:24 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Sprint 3 plan: group system — data structure, resolver function, persistence strategy. Các quyết định kiến trúc cốt lõi. |
| **Đề xuất merge** | `docs/Sprints/Sprint3/00_Plan.md` |

---

### Sprint4_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `08-06-2026_Sprint4_Plan_Opus.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 08/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Sprint 4 plan: edit mode và nested groups — selection scope filtering, resolver design, architectural decisions. |
| **Đề xuất merge** | `docs/Sprints/Sprint4/00_Plan.md` |

---

### Sprint4_Execution

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `Sprint4_Execution_Opus.md` |
| **Phiên bản** | 2.0 |
| **Cập nhật** | 11/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Execution guide Sprint 4: edit mode insights, prerequisite architecture validation, task-by-task implementation steps. |
| **Đề xuất merge** | `docs/Sprints/Sprint4/Execution.md` |

---

### Sprint4_BugFix_Execution

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `Sprint4_BugFix_Execution_Opus.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 14/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Execution plan Sprint 4 bug fix: root cause analysis và fixes cho 5 bugs — edit mode bar persistence, spawn scope, GroupNameCounter. |
| **Đề xuất merge** | `docs/Sprints/Sprint4/BugFix_Execution.md` |

---

### Gate1_SprintD_Execution

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `Gate1_SprintD_Execution_Opus.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 11/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Execution plan Gate 1 và Sprint D: bug fixes, spawn path consolidation, data layer architecture migration (Supabase). |
| **Đề xuất merge** | `docs/Sprints/SprintD/Gate1_Execution.md` |

---

### Sprint5_Execution

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `Sprint5_Combo_Execution.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 12/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Sprint 5 combo mesh execution plan: prerequisite validation, scope definition, decision points. |
| **Đề xuất merge** | `docs/Sprints/Sprint5/Execution.md` |

---

### UX_Phase2_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `20-05-2026_UX_Phase2_Plan.md` |
| **Phiên bản** | 1.1 |
| **Cập nhật** | 20/05/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Plan UX Phase 2: gizmo scaling, rotation direction fixes, arrow key nudge, copy/paste, inventory features. |
| **Đề xuất merge** | `docs/Sprints/Sprint1/UX_Phase2_Plan.md` |

---

### Resize_Window_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `26-05-2026_Resize_Window_Plan.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 26/05/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Plan implement resize window 8-direction với minimum size constraints. |
| **Đề xuất merge** | `docs/Sprints/Sprint1/Resize_Window_Plan.md` |

---

### i18n_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `13-05-2026-00h00p_i18n_plan.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 13/05/2026 — 00:00 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Plan i18n hybrid: UE5 localization system cho UI labels + multi-column DataTable cho content. |
| **Đề xuất merge** | `docs/00_Core/i18n_Plan.md` |

---

### Future_Architecture_1M_Assets

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `13-05-2026-22h30p_Future_Architecture_1M_Assets.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 13/05/2026 — 22:30 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Kiến trúc tương lai cho 1 triệu assets: bypass UE asset pipeline để đạt scalability. |
| **Đề xuất merge** | `docs/00_Core/Future_Architecture.md` |

---

## 5. Session State

### Session_State

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `Session_State_15jun2026.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 15/06/2026 — 20:30 ICT |
| **Older versions** | 11 |
| **Chủ đề** | Trạng thái project cuối phiên làm việc: Sprint 4 bug fix hoàn tất, 5 fixes pass full regression test suite, sẵn sàng cho Gate 1 / Sprint D. |
| **Đề xuất merge** | `docs/00_Core/Session_State_Current.md` (giữ canonical); các bản cũ → Archive |

Older files theo thứ tự thời gian:

| File | Ngày |
|------|------|
| `19-05-2026-17h50p_Session_State.md` | 19/05/2026 |
| `25-05-2026-17h29p_Session_State.md` | 25/05/2026 |
| `27-05-2026-10h30p_Session_State_updated.md` | 27/05/2026 |
| `02-06-2026-12h30p_Session_State.md` | 02/06/2026 |
| `04-06-2026-15h30p_Session_State.md` | 04/06/2026 |
| `05-06-2026-20h00p_Session_State.md` | 05/06/2026 |
| `07-06-2026-22h40p_Session_State.md` | 07/06/2026 |
| `08-06-2026-13h30p_Session_State.md` | 08/06/2026 |
| `10-06-2026-20h34p_Session_State.md` | 10/06/2026 |
| `Session_State_11jun2026.md` | 11/06/2026 |
| `Session_State.md` | 12/06/2026 |

---

## 6. Bug / Debug

### Bug_GPU_VRAM_Crash

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `09-05-2026-08h30p_Bug_GPU_VRAM_Crash.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 09/05/2026 — 08:30 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Bug report GPU VRAM crash: D3D device removal sau nhiều PIE sessions, ~7.26GB budget exceeded. Root cause và workaround. |
| **Đề xuất merge** | `docs/Bugs/Bug_GPU_VRAM_Crash.md` |

---

### Sprint3_Regression_DualDispatcher_Log

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `10-06-2026-20h34p_Sprint3_Regression_DualDispatcher_Log.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 10/06/2026 — 20:34 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Log chi tiết regression fixes Sprint 3: refactoring dispatcher consolidation từ dual → single OnSelectionChanged. |
| **Đề xuất merge** | `docs/Bugs/Sprint3_Regression_Log.md` |

---

## 7. Data / Pipeline

### FilterByCategory_Logic

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `25-05-2026-15h03p_FilterByCategory_Logic.md` |
| **Phiên bản** | 1.2 |
| **Cập nhật** | 25/05/2026 — 15:03 ICT |
| **Older versions** | 1 (`22-05-2026_FilterByCategory_Logic.md` v1.1) |
| **Chủ đề** | FilterByCategory function: xử lý Recent category riêng, branching logic qua search pipeline. |
| **Đề xuất merge** | `docs/Data/FilterByCategory_Logic.md` |

---

### FilterBySearch_Logic

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `22-05-2026_FilterBySearch_Logic.md` |
| **Phiên bản** | 1.2 |
| **Cập nhật** | 22/05/2026 |
| **Older versions** | 0 |
| **Chủ đề** | FilterBySearch function: minimum text length check, mode-specific population branches. |
| **Đề xuất merge** | `docs/Data/FilterBySearch_Logic.md` |

---

### FurnitureFilterLibrary (C++)

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `FurnitureFilterLibrary.cpp` |
| **Phiên bản** | N/A |
| **Cập nhật** | N/A |
| **Older versions** | 0 |
| **Chủ đề** | C++ implementation của FurnitureFilterLibrary — filter furniture và material dùng reflection-based property matching. Source code thực tế. |
| **Đề xuất merge** | `docs/Data/FurnitureFilterLibrary_Reference.md` (ghi reference, không copy source) |

---

### Data_Structures

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `28-05-2026_05_Data_Structures.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 28/05/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Reference đầy đủ các data structure: S_FurniturePlacement, S_GroupData, snapshot version evolution (v1→v4). |
| **Đề xuất merge** | `docs/Data/05_Data_Structures.md` |

---

### ChangeMaterial_Context

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `18-05-2026-08h55p_ChangeMaterial_Context_v1_1.md` |
| **Phiên bản** | 1.6 |
| **Cập nhật** | 18/05/2026 — 08:55 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Feature tài liệu material change v1.1: material instance DataTable, live apply, undo/redo, folder tree filtering. |
| **Đề xuất merge** | `docs/Data/ChangeMaterial_Feature.md` |

---

### Material_CopyPaste

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `02-06-2026-12h30p_Material_CopyPaste_v0.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 02/06/2026 — 12:30 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Single-slot material copy/paste: copy material từ mesh slot này sang slot khác, keyboard shortcuts, button controls. |
| **Đề xuất merge** | `docs/Data/Material_CopyPaste.md` |

---

### Python_Scripts

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `16-05-2026-14h08_Python_Scripts.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 16/05/2026 — 14:08 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Python utility scripts cho UE5 data pipeline: populate bounding size, update material paths dùng reflection. |
| **Đề xuất merge** | `docs/Data/Python_Scripts.md` |

---

### Backend_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `Backend_Plan_v1.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 11/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Backend architecture plan: Supabase, offline-first principle — full functionality không cần network. |
| **Đề xuất merge** | `docs/Data/Backend_Plan.md` |

---

### Integration_Guide

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `02-06-2026-11h44p_Integration_Guide.md` |
| **Phiên bản** | 1.3 |
| **Cập nhật** | 02/06/2026 — 11:44 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Integration guide vào master project: plugin setup, C++ module configuration, plugin dependency cho UE5.5.4. |
| **Đề xuất merge** | `docs/00_Core/Integration_Guide.md` |

---

### Plugin_Migration_Guide

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `01-06-2026_Plugin_Migration_Guide.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 01/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Guide chuyển C++ FurnitureFilterLibrary từ project module sang standalone plugin FurnitureToolkit. |
| **Đề xuất merge** | `docs/00_Core/Plugin_Migration_Guide.md` |

---

## 8. Other

### Master_Plan

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `28-05-2026_00_Master_Plan.md` |
| **Phiên bản** | 3.0 |
| **Cập nhật** | 28/05/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Master plan overview: 7-sprint roadmap, document structure, design philosophy, architectural decisions. |
| **Đề xuất merge** | `docs/00_Core/00_Master_Plan.md` |

---

### Current_Architecture_Audit

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `28-05-2026_01_Current_Architecture_Audit.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 28/05/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Audit kiến trúc hiện tại: actor relationships, input handling, selection system implementation. |
| **Đề xuất merge** | `docs/00_Core/01_Current_Architecture.md` |

---

### Target_Architecture

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `02_Target_Architecture.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | N/A |
| **Older versions** | 0 |
| **Chủ đề** | Target system architecture sau 7 sprints: BeginPlay setup, selection system design, component relationships. |
| **Đề xuất merge** | `docs/00_Core/02_Target_Architecture.md` |

---

### Code_Inheritance_Strategy

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `28-05-2026_03_Code_Inheritance_Strategy.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 28/05/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Code reuse strategy: pattern matching, parameterization, flag-based behavior switching. |
| **Đề xuất merge** | `docs/00_Core/03_Code_Inheritance_Strategy.md` |

---

### Risk_Mitigation

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `06_Risk_Mitigation.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | N/A |
| **Older versions** | 0 |
| **Chủ đề** | Risk assessment: stencil outline rendering và group data persistence — critical và medium-level risks. |
| **Đề xuất merge** | `docs/00_Core/06_Risk_Mitigation.md` |

---

### Testing_Strategy

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `28-05-2026_07_Testing_Strategy.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 28/05/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Testing strategy: regression suite cho single-select, material operations, performance trên weak hardware. |
| **Đề xuất merge** | `docs/00_Core/07_Testing_Strategy.md` |

---

### Performance_Optimization

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `28-05-2026_08_Performance_Optimization.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 28/05/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Performance guidelines: VRAM constraints, Tick optimization, scene scaling limits cho weak machines. |
| **Đề xuất merge** | `docs/00_Core/08_Performance_Optimization.md` |

---

### PROGRESS

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `PROGRESS_Sprint4BugFix_update.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 15/06/2026 |
| **Older versions** | 5 |
| **Chủ đề** | Progress tracker tổng: 44/82 tasks complete qua Sprint 1-4, Ship status. Update cuối: 5 bug fixes Sprint 4 hoàn tất + full test suite pass. |
| **Đề xuất merge** | `docs/00_Core/PROGRESS.md` |

Older files:

| File | Ngày |
|------|------|
| `28-05-2026_PROGRESS.md` | 28/05/2026 |
| `04-06-2026-15h30p_PROGRESS.md` | 04/06/2026 |
| `07-06-2026-22h40p_PROGRESS.md` | 07/06/2026 |
| `08-06-2026-13h30p_PROGRESS.md` | 08/06/2026 |
| `PROGRESS.md` | 12/06/2026 |

---

### DEVIATIONS

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `DEVIATIONS.md` (master) + `DEVIATIONS_Sprint4BugFix_additions.md` (addendum) |
| **Phiên bản** | N/A |
| **Cập nhật** | Master: 12/06/2026 — 15:04 ICT; Addendum: 15/06/2026 |
| **Older versions** | 3 |
| **Chủ đề** | Deviation tracking master: 10 Sprint 3 deviations + 4 Sprint 4 bug fix deviations với architectural impact. Addendum ghi thêm 4 approved deviations từ Sprint 4 bug fix. |
| **Đề xuất merge** | `docs/00_Core/DEVIATIONS.md` (merge addendum vào master) |

Older files:

| File | Ngày |
|------|------|
| `28-05-2026_DEVIATIONS.md` | 28/05/2026 |
| `04-06-2026-15h30p_DEVIATIONS.md` | 04/06/2026 |
| `07-06-2026-22h40p_DEVIATIONS.md` | 07/06/2026 |

---

### INDEX

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `INDEX.md` |
| **Phiên bản** | 1.0 |
| **Cập nhật** | 11/06/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Documentation index: mapping blueprint modifications → source files, source-of-truth guidance, reading priority. |
| **Đề xuất merge** | `docs/00_Core/INDEX.md` |

---

### Workflow

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `24-04-2026_Workflow.md` |
| **Phiên bản** | N/A |
| **Cập nhật** | 24/04/2026 |
| **Older versions** | 0 |
| **Chủ đề** | Project workflow guidelines: development practices, step-by-step collaboration model trên master project. |
| **Đề xuất merge** | `docs/00_Core/Workflow.md` |

---

### B1_Nudge_Flow

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `04-06-2026-15h30p_B1_Nudge_Flow.md` |
| **Phiên bản** | 1.2 |
| **Cập nhật** | 04/06/2026 — 15:30 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Arrow key nudge flow: Axis2D input, pulse trigger cho continuous movement, snap step support cho multi-select. |
| **Đề xuất merge** | `docs/Blueprints/Flows/B1_Nudge_Flow.md` |

---

### B2_CopyPaste_Flow

| Trường | Nội dung |
|--------|----------|
| **Canonical** | `04-06-2026-15h30p_B2_CopyPaste_Flow.md` |
| **Phiên bản** | 2.0 |
| **Cập nhật** | 04/06/2026 — 15:30 ICT |
| **Older versions** | 0 |
| **Chủ đề** | Copy/paste/duplicate multi-select flow: clipboard array structure duy trì formation relative to group center. |
| **Đề xuất merge** | `docs/Blueprints/Flows/B2_CopyPaste_Flow.md` |

---

*RAW_INVENTORY.md — Tạo tự động từ 113 file trong import_raw/. Không có nội dung nào được merge.*
