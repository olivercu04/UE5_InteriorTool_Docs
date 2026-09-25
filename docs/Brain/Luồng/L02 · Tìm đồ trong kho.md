# L02 · Tìm đồ trong kho

> **Hành trình:** ← [[L01 · Mở tool và kho đồ|L01 Mở tool và kho đồ]] · **L02** · [[L03 · Kéo đồ vào phòng|L03 Kéo đồ vào phòng]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là bước ② · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** mọi cách tìm (gõ chữ, bấm thư mục, loại) đổ về **1 hàm lọc** `FilterBySearch` → C++ lọc bảng dữ liệu `DT_FurnitureCatalog` → kho chỉ dựng **1 trang** thẻ. Riêng Gần đây / Yêu thích đi đường tắt, không qua C++.

## Người dùng làm gì → thấy gì
| Làm | Thấy |
|---|---|
| Gõ ô Search | Chờ ~0.3s rồi danh sách lọc lại; dưới 3 ký tự thì chưa lọc |
| Bấm thư mục cấp 1 trên cây | Danh sách lọc theo thư mục, cột cây dựng lại |
| Bấm thư mục cấp 2 | Hiện hàng chip thư mục con bên dưới |
| Bấm **Recent** / **Favorite** | Chỉ còn đồ đã dùng gần đây / đã thả tim; bấm lại để bỏ lọc |
| Đổi tab Furniture / Material / Combo | Cùng khung, nguồn dữ liệu khác |
| Lật trang | 48 thẻ mỗi trang |

Không ghi sổ lịch sử — tìm đồ không đổi cảnh.

## Chạy thế nào
![[Architecture_Map#5h — Tìm đồ trong kho (gõ tìm · thư mục · Gần đây · Yêu thích)]]
> 🗺️ Bản làn bơi: [[5h - Tìm đồ trong kho (gõ tìm · thư mục · Gần đây · Yêu thích).canvas|canvas 5h]]

## Hình dung
Giống **thủ thư tra mục lục**: không mang cả kho sách ra quầy — chỉ trả về **danh sách số hiệu** (RowName) khớp điều kiện, rồi lấy đúng 48 cuốn của trang đang xem. Mỗi thẻ trên màn hình chỉ cầm 1 số hiệu (`BP_FurnitureItemView`), tự tra ảnh khi được hiển thị; ListView tái dùng thẻ khi cuộn.

## Dễ hiểu sai
- **`FilterBySearch` đọc `CurrentCategory` (biến lớp), không đọc tham số `CategoryFilter`** — truyền tham số khác mà biến lớp chưa đổi thì kết quả không đổi ([[FilterBySearch_Logic]]).
- **Gần đây / Yêu thích không qua bộ lọc C++** — nên không kết hợp được với chữ tìm kiếm hay thư mục.
- **Tab Material không phải chỉ là "bộ lọc"** — nó còn là cổng của chế độ chỉnh vật liệu (dải slot chỉ hiện ở tab này, chọn đồ khi ở tab khác không đổi món đang chỉnh). Xem [[L09 · Đổi vật liệu|L09]].
- Tổng số trang tính bằng số nguyên `(Length + PageSize − 1) / PageSize` — dùng Ceil trên phép chia số nguyên sẽ thiếu 1 trang (Bug-Pagination đã trả giá).

## Đường ngược (6A)
Bỏ lọc: xoá chữ, bấm lại Recent / Favorite, bấm gốc cây ("All product").

## Còn mở
- Handler nút lật trang không ghi tên trong doc (chỉ có `DisplayPage`).
- Toàn luồng theo doc — chưa có K2.

## Nhảy tới code
| Hàm | Doc |
|---|---|
| `FilterBySearch` (flow đầy đủ + nơi gọi) | [[FilterBySearch_Logic]] |
| `FilterByCategory` · Recent / Favorite toggle | [[FilterByCategory_Logic]] |
| `SwitchInventoryMode` · `DisplayPage` · `OnTreeNodeClicked` · `OnChipTagClicked` · Pagination | [[WBP_FurnitureInventory]] |
| `FilterFurnitureRows` · `FilterMaterialItems` (C++) | [[FurnitureFilterLibrary_Reference]] |
| `OnListItemObjectSet` · `UpdateFavTint` | [[WBP_FurnitureCard]] |
| `OnNodeSelected` | [[WBP_TreeNode]] |
