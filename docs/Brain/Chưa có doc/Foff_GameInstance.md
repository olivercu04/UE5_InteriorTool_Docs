# Foff_GameInstance

> ⚠ Thành phần CÓ trong Architecture_Map nhưng CHƯA có doc canonical. Note này chỉ để graph đủ mắt xích — xem các luồng bên dưới.

#chua-co-doc

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Thuộc mảng kết nối:** [[Kết nối 3b - Combo lưu spawn thay combo]] · [[Kết nối 3c - Inventory + Cây thư mục]] · [[Kết nối 3d - Save Undo khởi động]]

**← Được gọi bởi**
- [[BP_ComboManager]] — hiện thông báo · GameInstance.ToastRef.ShowToast()
- [[WBP_ComboCard]] — đọc tham chiếu inventory · GameInstance.FurnitureInventoryRef
- [[WBP_FurnitureInventory]] — tự đăng ký + hiện thông báo · FurnitureInventoryRef, ToastRef.ShowToast()

<!-- BRAIN:END -->
