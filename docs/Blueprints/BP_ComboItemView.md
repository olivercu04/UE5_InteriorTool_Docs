# BP_ComboItemView — Combo Card View Object
**Version:** 1.2 | **Ngày:** 24/06/2026 | **Object class, không Actor — dùng cho CTV_ComboCard**

## Vai trò
Bọc FComboData thành UObject để TileView/ListView display combo card trong tab 🧩 Combo (WBP_FurnitureInventory). Mỗi combo trong thư viện = 1 BP_ComboItemView instance.

## Variables
| Tên | Kiểu | Vai trò |
|-----|------|---------|
| ComboID | String | ID duy nhất (combo_+GUID) |
| ComboName | String | Tên hiển thị |
| Description | String | Mô tả ngắn |
| Tags | Array String | Tags tìm kiếm (lowercase, dedupe — C3a) |
| FolderPath | String | Folder path của combo (C3a) |
| ThumbnailPath | String | Đường dẫn file .png thumbnail tuyệt đối (C3/C4) |
| ItemCount | Integer | Số món trong combo (badge ×N) |
| CreatedAt | String | Thời gian tạo (UTC string) |
| BoundingBoxExtent | Vector | Bounding box half-extent tính từ CalculateComboBoundingExtent khi save (C4) |

## Tạo từ
`LoadComboLibrary` trong WBP_FurnitureInventory — ForEach file .json trong Combos dir → F_LoadComboData → Make BP_ComboItemView → AddItem(CTV_ComboCard).

## Lịch sử cập nhật
| Ngày | Version | Nội dung |
|------|---------|----------|
| 21/06/2026 | 1.0 | Tạo mới — ComboID, ComboName, ItemCount (C1 load library) |
| 23/06/2026 | 1.1 | Thêm FolderPath (C3a), Description, Tags, ThumbnailPath, CreatedAt |
| 24/06/2026 | 1.2 | Thêm BoundingBoxExtent (C4 — tính từ CalculateComboBoundingExtent khi save, dùng cho ghost size trong OnDragDetected) |
