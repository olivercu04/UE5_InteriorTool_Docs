# WBP_FOFF_ToolDemo

> ⚠ Thành phần CÓ trong Architecture_Map nhưng CHƯA có doc canonical. Note này chỉ để graph đủ mắt xích — xem các luồng bên dưới.

#chua-co-doc

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Có mặt trong thao tác:** [[L01 · Mở tool và kho đồ|L01]]

**Thuộc mảng kết nối:** [[Kết nối 3d - Save Undo khởi động]]

**Gọi / điều khiển →**
- [[BP_FurnitureInputManager]] — sinh ra + gán GizmoControllerRef, CurrentMeshControls [K2 2026-09-25] · Spawn (Event Construct Then 11) ✓K2
- [[BP_UndoManager]] — sinh ra [K2 2026-09-25] · Spawn ✓K2
- [[BP_ComboManager]] — sinh ra [K2 2026-09-25] · Spawn ✓K2
- [[BP_FurnitureSceneManager]] — sinh ra + gán ToastRef [K2 2026-09-25] · Spawn, SET SceneManager.ToastRef ✓K2
- [[BP_FurnitureUserPrefsManager]] — sinh ra [K2 2026-09-25] · Spawn ✓K2
- [[WBP_Toast]] — tạo toast [K2 2026-09-25] · Create Widget WBP_Toast + Add to Viewport (Z 100) ✓K2
- [[BP_UndoManager]] — lưu mốc đầu tiên [K2 2026-09-25] · CaptureSnapshot(Initial) ✓K2
- [[WBP_FurnitureInventory]] — mở inventory khi bấm nút · Open widget

<!-- BRAIN:END -->
