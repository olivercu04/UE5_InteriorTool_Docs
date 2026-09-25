# WBP_ContextMenuItem

> ⚠ Thành phần CÓ trong Architecture_Map nhưng CHƯA có doc canonical. Note này chỉ để graph đủ mắt xích — xem các luồng bên dưới.

#chua-co-doc

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Có mặt trong thao tác:** [[L07 · Menu chuột phải và phím tắt|L07]]

**Thuộc mảng kết nối:** [[Kết nối 3a - Chọn đồ Gizmo Nhóm]] · [[Kết nối 3b - Combo lưu spawn thay combo]]

**Gọi / điều khiển →**
- [[BP_FurnitureInputManager]] — dòng menu được bấm → callback của IM · CB_Copy / CB_Paste / CB_Duplicate / CB_Delete … — bind trong OnRightClick ?

**← Được gọi bởi**
- [[BP_FurnitureInputManager]] — tạo 11 mục menu · Create Widget (OnRightClick) ✓K2
- [[WBP_LibraryContextMenu]] — tạo từng dòng menu · Create WBP_ContextMenuItem

<!-- BRAIN:END -->
