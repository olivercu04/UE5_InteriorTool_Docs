# WBP_TreeNode — Folder Tree Node
**Phiên bản:** 1.1 | **Tạo:** 27/05/2026 | **Cập nhật:** 18/06/2026 — TreeNode highlight

---

## Tổng quan

Mỗi WBP_TreeNode đại diện 1 folder cấp trong cây folder của WBP_FurnitureInventory.
Khi click → fire dispatcher `OnNodeSelected` lên inventory. Từ v1.1: hỗ trợ highlight
folder đang active (phối hợp với `IsPathActive`/`UpdateFolderHighlights`).

---

## Variables

| Tên | Kiểu | Ghi chú |
|---|---|---|
| `FolderPath` | String | Path đầy đủ của folder này — đọc bởi `UpdateFolderHighlights` để tính `IsPathActive` |
| `FolderName` | String | Tên hiển thị |
| `IndentLevel` | Integer | Cấp thụt lề (0=root, 1=sub, ...) |

---

## Event Dispatchers

```
OnNodeSelected(SelectedPath: String, IndentLevel: Integer)
```
Fire khi `Button_58.OnClicked`. Bind trong `WBP_FurnitureInventory.PopulateTreeColumn`.

---

## RefreshDisplay(FolderName, IndentLevel, bIsActive: Boolean) — v1.1

v1.1 thêm param `bIsActive`. Sau logic SetText/SetPadding hiện có:

```
Branch(bIsActive):
  True  → SetBackgroundColor(Button_58, [màu highlight — R=0.2, G=0.4, B=1.0, A=0.4])
  False → SetBackgroundColor(Button_58, (R=1, G=1, B=1, A=1))
```

⚠ `bIsActive` được tính BÊN NGOÀI — từ `IsPathActive(FolderPath)` trong `UpdateFolderHighlights`.
WBP_TreeNode KHÔNG tự tính. KHÔNG chèn node impure (Print String...) vào RefreshDisplay
nếu không cần thiết — debug đặt ở `UpdateFolderHighlights` là caller.

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 27/05/2026 | Khởi tạo — FolderPath/FolderName/IndentLevel, Dispatcher OnNodeSelected(Path, Indent) |
| 1.1 | 18/06/2026 — TreeNode Highlight | `RefreshDisplay` thêm param `bIsActive: Boolean` → `SetBackgroundColor(Button_58)`. Phối hợp với `UpdateFolderHighlights` + `IsPathActive` trong `WBP_FurnitureInventory`. |
