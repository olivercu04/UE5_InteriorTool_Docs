# BP_ComboItemView — Combo Card View Object
**Version:** 1.3 | **Ngày:** 15/07/2026 | **Object class, không Actor — dùng cho CTV_ComboCard**

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
| ThumbnailPath | String | Đường dẫn file .png thumbnail tuyệt đối (C3/C4). XÁC NHẬN 15/07/2026: dead field, không dùng ở đâu trong code hiện tại. Giữ nguyên, dọn sau (KP3). |
| ItemCount | Integer | Số món trong combo (badge ×N) |
| CreatedAt | String | Thời gian tạo (UTC string) |
| BoundingBoxExtent | Vector | Bounding box half-extent tính từ CalculateComboBoundingExtent khi save (C4) |
| Thumbnail | Texture2D | MỚI 15/07/2026 (G4) — texture cache dùng chung với BP_ComboManager.Cmb_ThumbnailCache, KHÔNG copy (R3) |

## Tạo từ
`LoadComboLibrary` trong WBP_FurnitureInventory — ForEach file .json trong Combos dir → F_LoadComboData → Make BP_ComboItemView → AddItem(CTV_ComboCard).

## Lịch sử cập nhật
| Ngày | Version | Nội dung |
|------|---------|----------|
| 21/06/2026 | 1.0 | Tạo mới — ComboID, ComboName, ItemCount (C1 load library) |
| 23/06/2026 | 1.1 | Thêm FolderPath (C3a), Description, Tags, ThumbnailPath, CreatedAt |
| 24/06/2026 | 1.2 | Thêm BoundingBoxExtent (C4 — tính từ CalculateComboBoundingExtent khi save, dùng cho ghost size trong OnDragDetected) |
| 15/07/2026 | 1.3 | Thêm Thumbnail : Texture2D (G4 — dùng chung cache với BP_ComboManager, KHÔNG copy). Xác nhận ThumbnailPath là dead field, không dùng ở đâu — giữ nguyên (KP3, dọn sau). |
