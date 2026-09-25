# L07 · Menu chuột phải và phím tắt

> **Hành trình:** ← [[L06 · Nhóm đồ và sửa nhóm|L06 Nhóm đồ và sửa nhóm]] · **L07** · [[L08 · Thay đồ|L08 Thay đồ]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là "Bất cứ lúc nào" · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** chuột phải chỉ mở menu khi **bấm-thả nhanh (< 0.3s) và camera không xoay** — giữ chuột phải để xoay camera thì không mở. Mỗi dòng menu gọi 1 callback `CB_*` của InputManager; Ctrl+C / V / D là event Input Action ngay trong InputManager (từ Gate 1.5 B2), không qua menu.

## Người dùng làm gì → thấy gì
| Làm | Thấy | Sổ lịch sử |
|---|---|---|
| Chuột phải lên đồ | Menu 11 dòng tại chỗ chuột | — |
| **Sao chép** (Ctrl+C) | Không thấy gì (vào clipboard) | — |
| **Dán** (Ctrl+V) | Bản sao hiện tại chỗ chuột, giữ nguyên đội hình, được chọn | `PasteMulti` |
| **Nhân bản** (Ctrl+D) | Bản sao nằm sát bên phải nhóm gốc, được chọn | `DuplicateMulti` |
| **Xoá** | Đồ biến mất, bỏ chọn | `Delete` |
| Chọn tương tự · Đặt lại xoay | Chọn mọi món cùng mesh · xoay về 0 | `SelectSimilar` · `ResetRotation` |

Các dòng khác dẫn sang luồng khác: **Thay đồ** → [[L08 · Thay đồ|L08]] · **Lưu combo** → [[L11 · Combo|L11]] · **Undo / Redo** → [[L13 · Hoàn tác và làm lại|L13]].

## Chạy thế nào
![[Architecture_Map#5m — Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá)]]
> 🗺️ Bản làn bơi: [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|canvas 5m]]

## Hình dung
Clipboard lưu **công thức**, không lưu đồ: mỗi món là 1 dòng (RowName, mesh, vị trí **so với tâm nhóm**, xoay, scale, vật liệu từng slot). Dán = đọc công thức, sinh đồ mới quanh điểm chuột → đội hình giữ nguyên.

## Dễ hiểu sai
- **Clipboard phải mang đủ field** — thiếu `RowName` (bug 07/09) làm đổi vật liệu nhiều món chỉ đổi món chính; thiếu `MaterialSlots` (bug 15/09) làm bản sao mất vật liệu. Thêm field mới cho đồ → rà cả `S_ClipboardEntry`.
- **Nhân bản: phần sinh đồ nối `Completed` của vòng tính mép phải**, không nối `Loop Body` (nối nhầm = N×N món).
- **Xoá: `Destroy Actor` phải trỏ vào phần tử mảng** — để trống = tự xoá chính InputManager.
- **Ctrl+Shift+C / V là copy VẬT LIỆU** ([[Material_CopyPaste]]) — binding copy đồ tự bỏ qua khi đang giữ Shift.
- Dán / Nhân bản dùng `SpawnFurnitureCopy(bAutoSelect=False)` rồi chọn cả loạt 1 lần ở cuối — tránh chọn lặp từng món.

## Đường ngược (6A)
Ctrl+Z cho Dán / Nhân bản / Xoá / Chọn tương tự / Đặt lại xoay (đều là Snapshot). Menu đóng bằng click ra ngoài (`OnLMBReleased` Then 0) hoặc chuột phải-kéo.

## Còn mở
- Cách từng dòng menu gắn vào `CB_*` (bind trong `OnRightClick`) chưa K2 (`?`).
- Phím Delete: danh sách phím tắt ghi "Delete = xoá" nhưng doc không ghi handler; `IA_RMBPress` / `IA_RMBRelease` chưa vào bảng Input Action chính thức.

## Nhảy tới code
| Hàm | Doc |
|---|---|
| Right-click handler (`OnRMBPressed` / `OnRMBReleased` ✓K2) · Callbacks · `DeleteSelected` · `SelectSimilarMesh` · `ResetRotation` | [[BP_FurnitureInputManager]] |
| `CopyMesh` · `PasteMesh` · `DuplicateMesh` · `SpawnFurnitureCopy` (✓K2) | [[CopyPaste_Flow]] |
| Menu widget | [[WBP_ContextMenu]] · [[WBP_ContextMenuItem]] |
