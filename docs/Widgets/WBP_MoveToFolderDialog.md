# WBP_MoveToFolderDialog
**Phiên bản:** 2.0 | **Tạo:** 30/06/2026 — C5.4 Move Folder | **Sửa:** 13/07/2026 — C5.8 Wire Move: thay `ScrollBox_FolderList`/`WBP_MoveFolderRow` bằng `WBP_FolderTreePicker`

---

## Tổng quan
Dialog modal chọn folder cha đích khi move folder. Dùng `WBP_FolderTreePicker` (guide line, search, expand/collapse, inline rename) — thay `WBP_MoveFolderRow` (SUPERSEDED, không xoá file, đánh dấu tương tự pattern DA_FurnitureItem) + list phẳng `ScrollBox_FolderList` cũ.

## Layout
```
Canvas Panel
├── Border_Dim       (full-screen, đen A=0.6)
└── Border_Content   (anchors center, ~420×480)
    └── Vertical Box
        ├── TextBlock_Title ("Chuyển vào folder")
        ├── Picker (WBP_FolderTreePicker)
        ├── Spacer
        └── Horizontal Box [BTN_Cancel, BTN_Confirm]
```

## Variables
| Tên | Kiểu | Ghi chú |
|---|---|---|
| Picker | WBP_FolderTreePicker | Is Variable=✓ |
| SelectedTargetPath | String | Path đang chọn |
| bHasSelection | Boolean | False = chưa chọn gì, Confirm disabled |

## Event Dispatchers
```
OnMoveFolderConfirmed(TargetParentPath : String)
```

## Functions

### InitPicker(Entries : Array\<S_FolderTreeNode\>, InCurrentPath : String, bInShowTag : Boolean)
```
SET Picker.CurrentPath = InCurrentPath
SET Picker.bShowCurrentTag = bInShowTag
Picker.ExpandToPath(InCurrentPath)
Picker.SetFolders(Entries)
SET SelectedTargetPath = "" | bHasSelection = False
Set Is Enabled(BTN_Confirm, False)
Bind Picker.OnFolderSelected → HandlePickerFolderSelected
```
> **[CEILING]** Bind đặt trong `InitPicker` (không phải Event Construct) — giả định 1 lần/instance. An toàn CHỈ KHI mỗi lần mở dialog là 1 instance mới (Create Widget mới, đúng hiện trạng). **trigger:** nếu sau này đổi sang tái dùng instance (gọi `InitPicker` nhiều lần/1 instance) → Bind sẽ chồng (double-fire) → phải dời sang Event Construct lúc đó. Xem `DEVIATIONS.md` 13/07/2026.

### HandlePickerFolderSelected(Path : String) — Custom Event
```
SET SelectedTargetPath = Path | bHasSelection = True
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
`BTN_Confirm`/`BTN_Cancel` — giữ nguyên 100% so với v1.0.

### Event Destruct
(Không còn hard ref cần clear — `CurrentSelectedRow` đã xoá cùng `ScrollBox_FolderList`/`WBP_MoveFolderRow` cũ.)

---

## Test PASS
M1-M6 (Wire Move full flow, mirror REG A1-A2) — chi tiết xem `WBP_FolderTreePicker.md` §Test status.

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 30/06/2026 | Khởi tạo — C5.4 Move Folder |
| 2.0 | 13/07/2026 | **C5.8 Wire Move.** Xoá hẳn: `ScrollBox_FolderList`, `WBP_MoveFolderRow` reference, `PopulateRows`, `HandleRowSelected` (bản cũ của Dialog), var `CurrentSelectedRow`. Thêm: var `Picker : WBP_FolderTreePicker`; `InitPicker(Entries, InCurrentPath, bInShowTag)` (SET CurrentPath/bShowCurrentTag → ExpandToPath → SetFolders → reset selection → Bind OnFolderSelected); `HandlePickerFolderSelected` (Custom Event, thay `HandleRowSelected` cũ). `BTN_Confirm`/`BTN_Cancel` giữ nguyên 100%. `WBP_MoveFolderRow` SUPERSEDED (không xoá file). Test PASS: M1-M6. |
