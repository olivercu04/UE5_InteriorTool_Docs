# DEVIATIONS — Sprint 4 Bug Fix Session (15/06/2026)
> Thêm vào DEVIATIONS.md, section sau "SPRINT 4 — EDIT MODE + NESTED GROUP"

---

## SPRINT 4 BUG FIX SESSION (15/06/2026)

| # | Plan gốc nói | Thực tế | Lý do | Kết quả |
|---|---|---|---|---|
| D4BF-1 | D4-9: Spawn trong edit → GroupID="" (đồ rời) | **F4: Spawn tự động nhận GroupID = GetCurrentEditScope()** khi đang trong edit | Q13 approved deviation: UX consistency — đồ spawn trong edit phải thuộc scope đang chỉnh | ✅ Approved — ghi DEVIATIONS khi lệch |
| D4BF-2 | D4-6: S_SceneSnapshot không thêm field EditModeStack | **A12: Thêm EditModeStackSnapshot (Version=4)** vào S_SceneSnapshot, capture/restore trong CaptureSnapshot/RestoreSnapshot | Bug A12 root cause: undo không khôi phục edit state với group có sẵn. Quyết định kiến trúc lâu dài sau analysis Opus: EditModeStack cần vào snapshot để undo semantics đúng | ✅ Architectural improvement — không vá tạm |
| D4BF-3 | CreateGroup: guard `SelectedActors.Length < 2` đặt đầu hàm | **F3: ComputeSelectionUnits chạy TRƯỚC guard**; guard kiểm tra `GroupUnits.Length + LooseActors.Length < 2` | Bug: guard cũ không phân biệt "2 actors" vs "2 group units" — case 2 group chọn sẽ cho SelectedActors.Length=2 nhưng ComputeSelectionUnits mới xác định đúng số đơn vị | ✅ Fix đúng (Luật 6B) |
| D4BF-4 | GroupNameCounter trong BP_FurnitureInputManager | **F2: Chuyển sang BP_GroupsContainer** (SaveGame=True) | BP_FurnitureInputManager không implement EMS → counter reset về 1 sau Save/Load | ✅ Fix đúng — counter bây giờ persist |

---

## BUGS DEFERRED (cập nhật)

| Bug | Mô tả | Status |
|---|---|---|
| B3-gizmo | Gizmo ẩn sau undo trong edit mode (mode vẫn là Move) | **Pre-existing** — xác nhận 15/06, không phải regression Sprint 4. Known issue, chưa có timeline fix. |

---

## F4 SPAWN PATHS — Tổng kết (xác nhận 15/06)

| Con đường spawn | Xử lý F4 |
|---|---|
| Drag-drop card | WBP_DragOverlay On Drop — chèn GET Scope → Branch → SET GroupID (v1.5) |
| Paste / Cut-Paste / Duplicate | SpawnFurnitureCopy Sequence.Then 0 — chèn GET Scope → Branch → SET GroupID (v1.9) |
| Replace Mesh | ✅ Đã xử lý từ 12/06: SET NewActor.GroupID = OldActor.GroupID (GroupID kế thừa từ actor cũ) |
