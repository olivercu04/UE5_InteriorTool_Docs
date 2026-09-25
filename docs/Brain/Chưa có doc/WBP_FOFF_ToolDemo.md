# WBP_FOFF_ToolDemo

> ⚠ Thành phần CÓ trong Architecture_Map nhưng CHƯA có doc canonical. Note này chỉ để graph đủ mắt xích — xem các luồng bên dưới.

#chua-co-doc

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Có mặt trong thao tác:** [[L01 · Mở tool và kho đồ|L01]]

**Thuộc mảng kết nối:** [[Kết nối 3d - Save Undo khởi động]]

**Gọi / điều khiển →**
- [[BP_FurnitureInputManager]] — sinh ra các manager · Spawn (Event Construct, Then 0..13)
- [[BP_UndoManager]] — sinh ra · Spawn
- [[BP_ComboManager]] — sinh ra (⚠ doc còn ghi Level BP) · Spawn
- [[BP_FurnitureSceneManager]] — sinh ra · Spawn
- [[BP_FurnitureUserPrefsManager]] — sinh ra · Spawn
- [[WBP_Toast]] — tạo toast + gắn vào GameInstance · Create + SET GI.ToastRef
- [[BP_UndoManager]] — lưu mốc đầu tiên · CaptureSnapshot(Initial)
- [[WBP_FurnitureInventory]] — mở inventory khi bấm nút · Open widget
- [[BP_FoffPlayerController]] — đổi bộ phím khi mở / đóng kho · AddFurnitureInput() / RemoveFurnitureInput()

<!-- BRAIN:END -->
