# WBP_TreeNode — Folder Tree Node
**Phiên bản:** 1.3 | **Tạo:** 27/05/2026 | **Cập nhật:** 27/06/2026 — C5.2 EditableLabel_Name + OnNodeRenameCommitted

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
OnNodeRightClicked(FolderPath: String)
OnNodeRenameCommitted(OldPath: String, NewName: String)
```
- `OnNodeSelected` — fire khi `Button_58.OnClicked`. Bind trong `WBP_FurnitureInventory.PopulateTreeColumn`.
- `OnNodeRightClicked` — fire khi right-click. Bind trong `PopulateComboTreeColumn` → `OnComboTreeNodeRightClicked`.
- `OnNodeRenameCommitted` — fire khi WBP_EditableLabel confirm rename. Bind trong `PopulateComboTreeColumn` → `OnRenameFolderCommitted`.

---

## Layout — v1.3

```
Button_58 (Button, root)
└── HorizontalBox
    ├── EditableLabel_Name   (WBP_EditableLabel) ← v1.3: thay TextBlock_71
    └── [...]
```
> Thay TextBlock_71 bằng WBP_EditableLabel — additive. Furniture/material tree KHÔNG bị ảnh hưởng (chỉ Combo mode gọi `EnterRenameMode`).

---

## RefreshDisplay(FolderName, IndentLevel, bIsActive: Boolean) — v1.1

v1.1 thêm param `bIsActive`. **v1.3:** `Set Text(TextBlock_71, FolderName)` đổi thành `EditableLabel_Name.SetLabel(FolderName)`. Sau logic SetLabel/SetPadding:

```
Branch(bIsActive):
  True  → SetBackgroundColor(Button_58, [màu highlight — R=0.2, G=0.4, B=1.0, A=0.4])
  False → SetBackgroundColor(Button_58, (R=1, G=1, B=1, A=1))
```

⚠ `bIsActive` được tính BÊN NGOÀI — từ `IsPathActive(FolderPath)` trong `UpdateFolderHighlights`.
WBP_TreeNode KHÔNG tự tính. KHÔNG chèn node impure (Print String...) vào RefreshDisplay
nếu không cần thiết — debug đặt ở `UpdateFolderHighlights` là caller.

---

## On Mouse Button Down (v1.2)

Override để bắt right-click. **Trả về Handled nếu right-click** để UMG không propagate lên parent.

```
On Mouse Button Down(MyGeometry, MouseEvent):
  Get Effecting Button(MouseEvent) → ReturnValue
  Branch(ReturnValue == Right Mouse Button)
    True  → Broadcast OnNodeRightClicked(GET FolderPath)
             Return Node ← Make Event Reply(Handled)
    False → Return Node ← Make Event Reply(Unhandled)
```

---

## EnterRenameMode(Siblings : Array\<String\>) — Custom Event (v1.3)

```
EditableLabel_Name.EnterEditMode(Siblings)
```

## Event Construct — v1.3 (binding thêm)

```
Bind EditableLabel_Name.OnLabelRenameCommitted → HandleLabelCommitted
```

### HandleLabelCommitted(NewName : String) — Local Custom Event
```
Broadcast OnNodeRenameCommitted(GET FolderPath, NewName)
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 27/05/2026 | Khởi tạo — FolderPath/FolderName/IndentLevel, Dispatcher OnNodeSelected(Path, Indent) |
| 1.1 | 18/06/2026 — TreeNode Highlight | `RefreshDisplay` thêm param `bIsActive: Boolean` → `SetBackgroundColor(Button_58)`. Phối hợp với `UpdateFolderHighlights` + `IsPathActive` trong `WBP_FurnitureInventory`. |
| 1.2 | 26/06/2026 — Right-click dispatcher | Thêm `OnNodeRightClicked(FolderPath: String)` dispatcher. Override `On Mouse Button Down`: branch Right Mouse Button → Broadcast dispatcher → Handled; False → Unhandled. |
| 1.3 | 27/06/2026 — C5.2 Inline Rename | TextBlock_71→`EditableLabel_Name` (WBP_EditableLabel). Dispatcher `OnNodeRenameCommitted(OldPath, NewName)`. Custom Event `EnterRenameMode(Siblings)` → relay vào `EditableLabel_Name.EnterEditMode`. Event Construct: Bind `EditableLabel_Name.OnLabelRenameCommitted` → `HandleLabelCommitted` → Broadcast `OnNodeRenameCommitted`. RefreshDisplay: `SetText(TextBlock_71)` → `EditableLabel_Name.SetLabel`. Additive — furniture/material unaffected. |
