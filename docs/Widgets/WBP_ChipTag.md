# WBP_ChipTag — Chip Tag (folder navigation)
**Phiên bản:** 1.3 | **Tạo:** 27/05/2026 | **Cập nhật:** 06/07/2026 — 23:40 ICT — C5.7b Inline Rename

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
| `EditLabel_ChipTag` | WBP_EditableLabel | v1.3 — thay `TextBlock_ChipTag` cũ, giữ nguyên vị trí/padding trong Horizontal Box |

---

## Event Dispatchers

```
OnChipSelected(Selected Path Chip Tag: String, Indent Level Chip Tag: Integer)
```
Fire khi `Button_ChipTag.OnClicked`. Bind trong WBP_FurnitureInventory khi tạo chip
(trong `CreateChipTagsForPath` và `OnChipTagClicked`).

```
OnChipRightClicked(FolderPath : String)
```
**Mới (v1.2, C5.7a — 06/07/2026).** Fire khi RMB (Right Mouse Button) trên chip. Bind trong
`WBP_FurnitureInventory.RebuildChipRowForPath` → `OnComboTreeNodeRightClicked` (tái dùng
handler context-menu của tree node, signature khớp `FolderPath : String`, không cần logic mới).

```
OnChipRenameCommitted(OldPath : String, NewName : String)
```
**Mới (v1.3, C5.7b — 06/07/2026).** Fire từ `HandleLabelCommitted` khi `EditLabel_ChipTag.OnLabelRenameCommitted`
bắn. `OldPath` đọc từ `FolderPath_ChipTag` của chính chip.

---

## On Mouse Button Down(MyGeometry, MouseEvent) — override (v1.2, C5.7a)

```
Get Effecting Button(MouseEvent) → ReturnValue
Branch(ReturnValue == Right Mouse Button)
  True  → Broadcast OnChipRightClicked(GET FolderPath_ChipTag)
           Return Node ← Make Event Reply(Handled)
  False → Return Node ← Make Event Reply(Unhandled)   ← cho Button_ChipTag xử lý OnClicked bình thường
```

> Pattern copy y hệt `WBP_TreeNode.On Mouse Button Down` (v1.2). Khác biệt: root của
> `WBP_ChipTag` là `Horizontal Box` (chứa `Button_ChipTag` con), không phải chính node là
> Button như `WBP_TreeNode` — nên nhánh `False` PHẢI trả `Unhandled` (không có ở TreeNode
> vì root nó chính là Button).

---

## EnterRenameMode(Siblings : Array\<String\>) — Custom Event (mới, v1.3)

```
▶→ EditLabel_ChipTag.EnterEditMode(Siblings)
```
Relay 1 node xuống `WBP_EditableLabel` (đã tự lo Delay(0.0) + validate bên trong — xem `WBP_EditableLabel.md`).

## HandleLabelCommitted(NewName : String) — Custom Event (mới, v1.3)

Bound từ `EditLabel_ChipTag.OnLabelRenameCommitted`.
```
▶→ Broadcast OnChipRenameCommitted(GET FolderPath_ChipTag, NewName)
```

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
| 1.2 | 06/07/2026 — C5.7a Right-click | Thêm Dispatcher `OnChipRightClicked(FolderPath : String)` + override `On Mouse Button Down` (pattern copy `WBP_TreeNode` v1.2, nhánh False trả Unhandled vì root là Horizontal Box không phải Button). Bind trong `WBP_FurnitureInventory.RebuildChipRowForPath` → tái dùng `OnComboTreeNodeRightClicked`. |
| 1.3 | 06/07/2026 — C5.7b Inline Rename | Thay `TextBlock_ChipTag` → `EditLabel_ChipTag` (WBP_EditableLabel). Thêm `EnterRenameMode` (relay EnterEditMode) + `HandleLabelCommitted` + dispatcher `OnChipRenameCommitted`. Test PASS full case (rename chip cấp giữa khi đang xem folder con). |
