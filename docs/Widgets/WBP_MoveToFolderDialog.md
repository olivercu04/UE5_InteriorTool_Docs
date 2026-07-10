# WBP_MoveToFolderDialog
**Phiên bản:** 1.0 | **Tạo:** 30/06/2026 — C5.4 Move Folder

---

## Tổng quan
Dialog modal chọn folder cha đích khi move folder. List phẳng indent ảo (build từ WBP_MoveFolderRow), không dùng ComboBox/drag-drop (xung đột C4 drag behavior).

> 🔲 **PLANNED (C5.8, chưa thực thi):** `ScrollBox_FolderList` (build từ `WBP_MoveFolderRow`) dự kiến thay bằng 1 `WBP_FolderTreePicker` full (guide line, search, expand/collapse) — `WBP_MoveFolderRow` superseded. Xem `docs/Sprints/Sprint5/C5.8_FolderTreePicker_Unify_Plan.md` §5. Code/doc dưới đây CHƯA đổi — vẫn đúng hiện trạng.

## Layout
```
Canvas Panel
├── Border_Dim       (full-screen, đen A=0.6)
└── Border_Content   (anchors center, ~420×480)
    └── Vertical Box
        ├── TextBlock_Title ("Chuyển vào folder")
        ├── ScrollBox_FolderList
        ├── Spacer
        └── Horizontal Box [BTN_Cancel, BTN_Confirm]
```

## Variables
| Tên | Kiểu | Ghi chú |
|---|---|---|
| SelectedTargetPath | String | Path đang chọn |
| bHasSelection | Boolean | False = chưa chọn gì, Confirm disabled |
| CurrentSelectedRow | WBP_MoveFolderRow | Hard ref dòng đang chọn — SET None ở Event Destruct (R4) |

## Event Dispatchers
```
OnMoveFolderConfirmed(TargetParentPath : String)
```

## Functions

### PopulateRows(Entries : Array\<S_FolderTreeNode\>)
> `S_FolderTreeNode` — v3.9 rename của `S_FolderTargetEntry` (WBP_FurnitureInventory, C5.8 Task Card #1, 08/07). Struct auto-propagate tên mới qua rename, chưa đổi logic/layout của dialog này (C5.8 §5 — chờ Task Card #2).
```
Clear Children(ScrollBox_FolderList)
SET CurrentSelectedRow = None | bHasSelection = False
Set Is Enabled(BTN_Confirm, False)
ForEach Entries:
  Create Widget(WBP_MoveFolderRow) → Row
  Row.SetRow(entry.Path, entry.DisplayLabel, entry.IndentLevel)
  Bind Row.OnRowClicked → HandleRowSelected
  Add Child(ScrollBox_FolderList, Row)
```

### HandleRowSelected(TargetPath : String, RowWidget : WBP_MoveFolderRow) — Custom Event
```
IsValid(CurrentSelectedRow) True → CurrentSelectedRow.SetHighlight(False)
[merge]
SET CurrentSelectedRow = RowWidget | SelectedTargetPath = TargetPath | bHasSelection = True
RowWidget.SetHighlight(True)
Set Is Enabled(BTN_Confirm, True)
```

### BTN_Cancel.OnClicked
```
Get Player Controller → Set Input Mode Game And UI
Remove from Parent
```

### BTN_Confirm.OnClicked
```
Branch(bHasSelection)
  True  → Broadcast OnMoveFolderConfirmed(SelectedTargetPath)
          → Get Player Controller → Set Input Mode Game And UI → Remove from Parent
  False → dead-end (guard, lý thuyết không xảy ra vì nút disabled)
```

### Event Destruct
```
SET CurrentSelectedRow = None
```

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 30/06/2026 | Khởi tạo — C5.4 Move Folder |
