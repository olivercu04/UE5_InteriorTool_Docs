# Foff_GameInstance

> ⚠ Thành phần CÓ trong Architecture_Map nhưng CHƯA có doc canonical. Note này chỉ để graph đủ mắt xích — xem các luồng bên dưới.

#chua-co-doc

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] v1.5 (Phần 3). ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Thuộc luồng:** [[Luồng 3b - Combo lưu spawn thay combo]] · [[Luồng 3c - Inventory + Cây thư mục]] · [[Luồng 3d - Save Undo khởi động]]

**← Được gọi bởi**
- [[BP_ComboManager]] — hiện thông báo · GameInstance.ToastRef.ShowToast()
- [[WBP_ComboCard]] — đọc tham chiếu inventory · GameInstance.FurnitureInventoryRef
- [[WBP_FurnitureInventory]] — tự đăng ký + hiện thông báo · FurnitureInventoryRef, ToastRef.ShowToast()

<!-- BRAIN:END -->
