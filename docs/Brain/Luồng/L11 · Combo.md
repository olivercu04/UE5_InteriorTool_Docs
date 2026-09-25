# L11 · Combo

> **Hành trình:** ← [[L10 · Chỉnh thông số vật liệu|L10 Chỉnh thông số vật liệu]] · **L11** · [[L12 · Lưu và mở cảnh|L12 Lưu và mở cảnh]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là bước ⑥ · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** combo = **1 cụm đồ lưu thành file JSON** (từng món: RowName, vị trí so với điểm neo, vật liệu, nhóm con). Lưu combo không đổi cảnh (không ghi sổ); đặt combo sinh lại cả cụm thành **1 nhóm mới**; thay combo = xoá cụm cũ + đặt cụm mới đúng điểm neo, lỗi thì tự khôi phục.

## Người dùng làm gì → thấy gì
| Làm | Thấy | Sổ lịch sử |
|---|---|---|
| Chọn ≥2 món → chuột phải **Lưu combo** | Hộp thoại: tên, thư mục, mô tả, tag · **Lưu mới / Ghi đè / Huỷ** | — |
| Lưu | Tab Combo có thẻ mới + ảnh bìa chụp ở studio ảo | — |
| Tab Combo → kéo thẻ vào phòng | Khối bóng đúng kích thước, thả ra thành cả cụm, được chọn | `SpawnCombo` |
| Chuột phải món thuộc combo → **Thay đồ** → bấm Thay trên thẻ combo khác | Cụm cũ biến, cụm mới đứng đúng chỗ | `ReplaceCombo` |
| Thay lỗi (JSON hỏng / 0 món) | Cụm cũ quay lại + Toast "Thay thế thất bại" | không đổi |

## Chạy thế nào — lưu
![[Architecture_Map#5q — Lưu combo (lưu mới · ghi đè)]]
> 🗺️ Bản làn bơi: [[5q - Lưu combo (lưu mới · ghi đè).canvas|canvas 5q]]

## Chạy thế nào — đặt vào phòng
![[Architecture_Map#5r — Đặt combo từ thư viện vào phòng]]
> 🗺️ Bản làn bơi: [[5r - Đặt combo từ thư viện vào phòng.canvas|canvas 5r]]

## Chạy thế nào — thay cả combo
![[Architecture_Map#5s — Thay cả combo]]
> 🗺️ Bản làn bơi: [[5s - Thay cả combo.canvas|canvas 5s]]

## Hình dung
Combo giống **công thức xếp bàn tiệc**: không lưu chiếc bàn thật mà lưu "bàn loại X ở giữa, 4 ghế loại Y cách 60 cm, khăn màu Z". Đặt combo = xếp lại theo công thức ở chỗ mới; nhóm con được cấp **mã mới** (token `g0, g1…` → GUID mới) nên đặt 2 lần ra 2 cụm độc lập.

## Dễ hiểu sai
- **Lưu combo khi < 2 món bị chặn im lặng** (không báo gì) — `Bug-SaveComboSilentBlock` ([[Open_Bugs]]).
- **Hộp thoại đóng băng danh sách đồ** (`PendingSelectedActors`) và khoá input (UI Only) — Undo không xen vào giữa được.
- **Ảnh bìa chụp xong mới báo "thư viện đổi"** (`OnComboLibraryChanged` ở cuối Event Tick chụp) — thẻ mới xuất hiện trễ vài giây là bình thường.
- **Custom Event không có giá trị mặc định cho tham số** → `SpawnComboByID` dùng node `Select` để tên entry rỗng thành `SpawnCombo`.
- **`Cmb_LastSpawnSucceeded` phải reset ở dòng đầu** — không thì thay combo tưởng thành công, không rollback, cảnh bị lỗ.
- **Thay combo không chạm cờ `Cmb_bSpawnInFlight`** — chỉ đọc; SET ở đây sẽ tự chặn lệnh sinh phía sau.
- Món có RowName không còn trong DT → bỏ qua + Toast, vẫn tính thành công.

## Đường ngược (6A)
Ctrl+Z xoá cụm vừa đặt / trả cụm cũ sau thay (1 entry cho cả cụm) · lỗi thay → `RestoreCurrentSnapshot` tự khôi phục · xoá combo khỏi thư viện: nút Xoá trên thẻ combo → hộp xác nhận ("Không thể hoàn tác" — xoá file, không vào sổ lịch sử).

## Còn mở
- **CONFLICT** `ResolveActiveComboForSave` (cho phép Ghi đè) đã chèn vào `CB_SaveCombo_Handler` theo doc Inventory nhưng không có trong K2 04/08.
- Ai tạo lớp kéo-thả khi kéo thẻ combo — doc thẻ combo không ghi.
- Thỏa thuận thương mại combo với đồng nghiệp chưa chốt ([[Tư duy 1 · Sản phẩm và người dùng|Tư duy 1]] mục 7).

## Nhảy tới code
| Hàm | Doc |
|---|---|
| `SaveComboFromSelection` · `SpawnComboByID` · `F_LoadComboData` · `F_RegisterComboGroups` · `ReplaceCombo` · `BeginThumbnailCapture` | [[BP_ComboManager]] |
| `CB_SaveCombo_Handler` (✓K2 04/08) · `ResolveActiveComboForSave` · `StartReplaceComboMode` · `ExecuteComboReplace` · `DestroyComboCluster` | [[BP_FurnitureInputManager]] |
| `OpenSaveComboDialog` · `OnSaveComboConfirmed` · `HandleSaveComboOverwriteConfirmed` · `LoadComboLibrary` · `RequestDeleteCombo` | [[WBP_FurnitureInventory]] |
| Hộp thoại · thẻ · bóng | [[WBP_SaveComboDialog]] · [[WBP_ComboCard]] · [[BP_ComboGhostActor]] |
| Định dạng JSON · đọc / ghi file | [[ComboSerializer_Reference]] · [[Data_Structures]] |
