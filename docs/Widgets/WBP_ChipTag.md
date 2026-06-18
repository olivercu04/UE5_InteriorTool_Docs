# WBP_ChipTag — Chip Tag (folder navigation)
**Phiên bản:** 1.1 | **Tạo:** 27/05/2026 | **Cập nhật:** 18/06/2026 — Chip highlight

---

## Tổng quan

WBP_ChipTag là 1 chip nhỏ đại diện 1 folder con trong chip breadcrumb area
(`VB_ChipTagArea`). Chips được tạo bởi `CreateChipTagsForPath` và `OnChipTagClicked`
trong WBP_FurnitureInventory. Từ v1.1: hỗ trợ highlight chip đang active.

Chứa trong WBP_ChipRow (HorizontalBox_ChipRow). Mỗi cấp có 1 ChipRow.

---

## Variables

| Tên | Kiểu | Ghi chú |
|---|---|---|
| `FolderPath_ChipTag` | String | Path đầy đủ của folder này — đọc bởi `UpdateFolderHighlights` để tính `IsPathActive` |
| `FolderName_ChipTag` | String | Tên hiển thị trên chip |
| `IndentLevel_ChipTag` | Integer | Cấp thụt lề |
| `Button_ChipTag` | Button | Widget button nhận click + target của SetBackgroundColor |
| `TextBlock_ChipTag` | TextBlock | Hiển thị FolderName_ChipTag |

---

## Event Dispatchers

```
OnChipSelected(Selected Path Chip Tag: String, Indent Level Chip Tag: Integer)
```
Fire khi `Button_ChipTag.OnClicked`. Bind trong WBP_FurnitureInventory khi tạo chip
(trong `CreateChipTagsForPath` và `OnChipTagClicked`).

---

## SetHighlight(bIsActive: Boolean) — Custom Event (v1.1)

```
Branch(bIsActive):
  True  → SetBackgroundColor(Button_ChipTag, [màu highlight — R=0.2, G=0.4, B=1.0, A=0.4])
  False → SetBackgroundColor(Button_ChipTag, (R=1, G=1, B=1, A=1))
```

⚠ `bIsActive` được tính BÊN NGOÀI — từ `IsPathActive(FolderPath_ChipTag)` trong
`UpdateFolderHighlights`. WBP_ChipTag KHÔNG tự tính.

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 27/05/2026 | Khởi tạo — FolderPath/FolderName/IndentLevel, Dispatcher OnChipSelected(Path, Indent) |
| 1.1 | 18/06/2026 — Chip Highlight | Thêm Custom Event `SetHighlight(bIsActive: Boolean)` → `SetBackgroundColor(Button_ChipTag)`. Phối hợp với `UpdateFolderHighlights` + `IsPathActive` trong `WBP_FurnitureInventory`. |
