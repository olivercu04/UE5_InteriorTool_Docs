# INDEX.md — Bản đồ documentation Lighting_Mnger
**Phiên bản:** 1.0 | **Cập nhật:** 11/06/2026 | Đọc file này NGAY SAU Session_State.md để định vị

> Quy tắc vàng: file .uasset là binary — AI không đọc được Blueprint. Các file .md dưới đây LÀ source code thay thế. **Doc lỗi thời = AI mù.** Patch chỉ sống 1 sprint: cuối sprint merge vào file gốc rồi XÓA patch.

---

## 1. ĐỌC ĐẦU MỖI SESSION (theo thứ tự)
| # | File | Khi nào |
|---|------|---------|
| 1 | `Session_State.md` | LUÔN LUÔN — trạng thái + TODO + bug mở |
| 2 | `INDEX.md` (file này) | Khi cần định vị file |
| 3 | `09_AI_Implementation_Rules.md` | TRƯỚC mọi session THỰC THI (Q1-Q7, L1-L10, bảng node) |
| 4 | `Gate1_SprintD_Execution_Opus.md` | Khi thực thi Gate 1 / Sprint D |
| 5 | `Sprint4_Execution_Opus.md` | Khi làm tiếp Sprint 4 T6-T8 |

---

## 2. MUỐN SỬA X → ĐỌC FILE Y (source of truth từng Blueprint)

| Muốn sửa / hiểu | Đọc file | Ghi chú |
|---|---|---|
| Select / multi-select / box select / context menu / group / edit mode / clipboard / nudge | `BP_FurnitureInputManager.md` (v1.7 hợp nhất) | Actor phức tạp nhất — đọc mục "TƯƠNG TÁC 3 ĐIỂM" trước khi sửa |
| Undo / Redo / snapshot / CaptureSnapshot / RestoreSnapshot | `BP_UndoManager.md` (v1.6) | Bug B1 + fix bIsRestoring: xem Gate1_SprintD file |
| Toolbar / info bar / breadcrumb / nút edit mode / snap fields | `WBP_MeshControls.md` (v1.5 hợp nhất) | |
| Inventory / filter / search / folder tree / pagination / material grid / replace mode / resize window | `WBP_FurnitureInventory.md` (v2.4 hợp nhất) | Sprint D sẽ sửa lớn file này |
| Drag-drop spawn / ghost preview / surface snap | `WBP_DragOverlay_FurnitureCard.md` | + mục FurnitureCard trong inventory doc |
| Popup chi tiết sản phẩm | `WBP_DetailPopup.md` | |
| Resize window logic chi tiết | `WBP_ResizeWindow.md` | |
| Box select overlay widget | `WBP_BoxSelectOverlay.md` | |
| Gizmo movement / ray-plane / snap / rotation delta | `BP_GizmoController.md` + `BP_GizmoController_OnMouseReleased.md` | |
| Pivot multi-select | `BP_PivotActor.md` | + `T15_Multi_Rotate_Scale_Plan.md` (toán rotate — nợ S1.T15) |
| EMS Save/Load / BP_FurnitureActor | `BP_FurnitureActor_SceneManager.md` | |
| Player controller (input routing — KHÔNG thêm var) | `BP_FoffPlayerController.md` | |
| Filter logic chi tiết | `FilterBySearch_Logic.md`, `FilterByCategory_Logic.md` | |
| Node flow Sprint 1-3 tổng hợp | `Blueprint_Logic.md` | |
| Material editor v1.1 context | `ChangeMaterial_Context_v1_1.md` | |
| Copy/paste material | `Material_CopyPaste_v0.md`, `B2_CopyPaste_Flow.md` | |
| Nudge phím mũi tên | `B1_Nudge_Flow.md` | |
| Data structures / DataTable / DA / struct | `Data.md`, `05_Data_Structures.md` | |
| Python scripts pipeline | `Python_Scripts.md` | Sau reimport CSV → chạy lại scripts |
| Kiến trúc tổng / R1-R5 | `architecture.md`, `02_Target_Architecture.md` | |
| Hiệu năng / VRAM / baseline | `performance.md`, `08_Performance_Optimization.md`, `Bug_GPU_VRAM_Crash.md` | |
| Antipatterns đã trả giá | `antipatterns.md` | |
| Kế hoạch scale 1M assets | `Future_Architecture_1M_Assets.md` | Ngưỡng: >50k → SQLite |
| Tích hợp vào master project | `Integration_Guide.md` | |

---

## 3. PLAN & EXECUTION (thư mục plan_v3 + execution)
| File | Vai trò | Trạng thái |
|---|---|---|
| `00_Master_Plan.md` | Roadmap tổng (⚠ v3.1 đổi thứ tự: xem Gate1_SprintD file) | Active |
| `01_Current_Architecture_Audit.md` → `08_...` | Audit / target / inheritance / sprint details / data / risk / test / perf | Tham khảo |
| `09_AI_Implementation_Rules.md` | Luật cho model thực thi | **BẮT BUỘC mỗi session thực thi** |
| `10_Execution_Discipline.md` | Kỷ luật: deviation, fail-3-stop, vertical slice | Active |
| `Sprint4_Plan_Opus.md` + `Sprint4_Execution_Opus.md` | Sprint 4 Edit Mode (T6-T8 còn lại) | **ĐANG CHẠY** |
| `Gate1_SprintD_Execution_Opus.md` | Gate 1 (fix B1) + Sprint D (Data Layer v2) | **KẾ TIẾP** |
| `PROGRESS.md` / `DEVIATIONS.md` | Tiến độ thật / lệch plan | Cập nhật cuối mỗi task |

---

## 4. FILE ĐÃ HỢP NHẤT — XÓA PATCH (11/06/2026)
Các patch sau ĐÃ merge vào file gốc (bản hợp nhất 11/06) → **xóa khỏi project knowledge** để tránh retrieval nhiễu:
- ~~`BP_FurnitureInputManager_v1_7_patch.md`~~ → merged vào `BP_FurnitureInputManager.md` v1.7
- ~~`WBP_MeshControls_v1_5_patch.md`~~ → merged vào `WBP_MeshControls.md` v1.5
- ~~`WBP_FurnitureInventory_patch.md`~~ + ~~`WBP_Inventory_Card_v2_3_v1_4_patch.md`~~ → merged vào `WBP_FurnitureInventory.md` v2.4

## 5. FILE NÊN ARCHIVE (đã ship / deprecated — chuyển folder _archive hoặc gỡ khỏi project knowledge)
| File | Lý do |
|---|---|
| `MultiSelect_Group_ComboMesh_Plan_v2.md` | Deprecated 28/05 — thay bởi plan_v3 |
| `Sprint2_Plan_v2.md`, `Sprint2_ContextMenu_ChangeMaterial_Replace_Prep.md` | Sprint 2 đã ship, nội dung sống đã vào Blueprint_Logic + InputManager doc |
| `Sprint3_Plan_Opus.md` | Sprint 3 đã ship — giữ `Sprint3_Regression_DualDispatcher_Log.md` (bài học refactor còn giá trị) |
| `START_HERE_Sprint1.md` | Sprint 1 đã ship |
| `UX_Phase2_Plan.md` | Phase 2.1 đã ship |
| `Session_State.md` bản cũ | Khi đã có `Session_State_11jun2026.md` — chỉ giữ 1 bản, đặt tên cố định `Session_State.md` |
| `Project_Instructions_Updated.md` | Thay bởi Project_Instructions_v2 |
⚠ Lý do archive ≠ xóa kiến thức: project_knowledge_search lấy chunk theo độ liên quan — file chứa quyết định ĐÃ LẬT có thể được retrieve và model thực thi làm theo plan chết.

## 6. ⚠ ĐIỂM CẦN ĐỐI CHIẾU BP (đánh dấu trong các bản hợp nhất 11/06)
1. `WBP_MeshControls`: BTN_Delete còn flow single hay đã trỏ DeleteSelected? | BTN_ExitOneLevel có tồn tại? | Sequence handler info bar: Then 1 chứa gì?
2. `WBP_FurnitureInventory`: handler selection sau refactor dispatcher 10/06 — bind OnSelectionChanged thế nào (đối chiếu `Sprint3_Regression_DualDispatcher_Log.md`).
3. `DisplayPage`: có Clear List Items đầu hàm chưa? (nghi thiếu — fix trong Sprint D D.T5).
→ Khi đối chiếu xong: sửa doc, xóa marker ⚠, nâng version.

## 7. QUY ƯỚC DUY TRÌ
1. **1 Blueprint = 1 file .md** = source of truth. Mỗi lần sửa BP → sửa doc CÙNG task (DONE = code + doc).
2. **Version + ngày giờ phút** ở header + bảng lịch sử cuối file.
3. **Patch chỉ trong sprint** — cuối sprint merge + xóa patch.
4. **Node mới** → cuhoang xác nhận → thêm bảng node file 09.
5. **bp_exports/ (optional):** function lõi phức tạp → Ctrl+A trong graph → Ctrl+C → paste vào .txt (`BP_X__FunctionY.txt`). KHÔNG đưa vào project knowledge — chỉ paste vào chat khi cần mổ xẻ chính xác. Ứng viên: CaptureSnapshot, RestoreSnapshot, SelectActors, ResolveSelectionUnit, Mouse Left Pressed, OnLMBReleased.
6. **Session mới > chat dài.** Kết thúc chat = cập nhật Session_State.md ("save game").
