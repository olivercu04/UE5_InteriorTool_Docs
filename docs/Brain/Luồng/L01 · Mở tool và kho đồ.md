# L01 · Mở tool và kho đồ

> **Hành trình:** ← [[Tư duy 4 · Cách viết tài liệu trong bộ não|Tư duy 4]] · **L01** · [[L02 · Tìm đồ trong kho|L02 Tìm đồ trong kho]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là bước ① · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** lúc khởi động, InputManager **bật bộ phím nội thất 1 lần và giữ suốt phiên**; bấm nút Kho đồ chỉ mở / ẩn cửa sổ Furniture Warehouse — kho tạo 1 lần, các lần sau chỉ ẩn / hiện, phím tắt không đổi theo kho.

## Người dùng làm gì → thấy gì
| Làm | Thấy | Sổ lịch sử |
|---|---|---|
| Mở tool | Thanh công cụ, phòng 3D trống | mốc đầu tiên `Initial` |
| Bấm **Inventory** (hoặc phím I) | Cửa sổ kho mở ở tab Furniture, cây thư mục bên trái | — |
| Bấm **X** trên kho | Kho ẩn; phím tắt nội thất (Ctrl+Z, Ctrl+C…) vẫn chạy | — |

## Chạy thế nào
![[Architecture_Map#5g — Mở tool và mở kho đồ]]
> 🗺️ Bản làn bơi: [[5g - Mở tool và mở kho đồ.canvas|canvas 5g]]

## Hình dung
Bộ phím giống **chùm chìa khoá đeo sẵn từ lúc vào làm**: InputManager đeo chùm `LM_FurnitureInput` (Ctrl+Z, Ctrl+C, mũi tên…) ngay ở BeginPlay (ưu tiên 5, trên bộ phím project tổng) và không tháo ra — từ Gate 1.5 B2 tool tự lo bộ phím, không nhờ PlayerController của project tổng.

## Dễ hiểu sai
- **Đóng kho ≠ huỷ kho.** `BTN_Close` chỉ `SetVisibility(Collapsed)` — mọi biến trong kho còn nguyên (Sprint D đổi sang 1 bản duy nhất). Vì thế chặn quét khung dùng `Get Visibility == Visible`, không dùng `Is In Viewport`.
- **Đóng kho cũng thoát chế độ thay đồ** — `BTN_Close` xoá 3 biến `ReplaceTarget`, `MeshesToReplace`, `ComboRootGroupIDToReplace` (thiếu 1 biến = lần sau mở kho còn kẹt ở chế độ thay).
- Tham chiếu tới kho có 2 đường: `Foff_GameInstance.FurnitureInventoryRef` (code cũ) và `BP_FurnitureSceneManager.FurnitureInventoryRef` (đã xác nhận K2 11/09 và 12/09 cho các đường mới) — cùng trỏ 1 widget.

## Đường ngược (6A)
Mở kho ↔ đóng kho (X / phím I): chế độ thay đồ được thoát; bộ phím giữ nguyên. Khởi động không có đường ngược trong tool.

## Còn mở
- **CONFLICT** ai sinh các manager: Phần 3d ghi `WBP_FOFF_ToolDemo` Event Construct, doc InputManager ghi Level Blueprint. Cần K2 `WBP_FOFF_ToolDemo` Event Construct.
- `WBP_FOFF_ToolDemo` chưa có doc canonical.

## Nhảy tới code
| Hàm / sự kiện | Doc |
|---|---|
| Event BeginPlay (`AddMappingContext` ✓K2 25/09) · Enhanced Input Actions | [[BP_FurnitureInputManager]] |
| `AddFurnitureInput` / `RemoveFurnitureInput` — **mô tả cũ, lỗi thời từ Gate 1.5 B2** | [[BP_FoffPlayerController]] |
| Event Construct · `BTN_Close` · Level Blueprint · Keyboard Shortcuts | [[WBP_FurnitureInventory]] |
| Level Blueprint — Spawn Order · Cách BP khác lấy reference | [[BP_FurnitureInputManager]] |
| Tham chiếu `ToastRef` / `FurnitureInventoryRef` | [[BP_FurnitureSceneManager]] |
