# WBP_MoveFolderRow
**Phiên bản:** 1.0 | **Tạo:** 30/06/2026 — C5.4 Move Folder | **[SUPERSEDED]** 13/07/2026 — thay bởi `WBP_FolderPickerRow` (C5.8)

---

> ⚠️ **[SUPERSEDED]** — Xác nhận 13/07/2026 (REG C5.8 mục 7): không còn `Create Widget(WBP_MoveFolderRow)` ở đâu trong `WBP_FurnitureInventory` (`BuildMoveFolderTargetList` — nơi duy nhất từng dùng — đã xoá hẳn). `WBP_MoveToFolderDialog` nay dùng `WBP_FolderTreePicker`. File này KHÔNG xoá (giữ tham chiếu lịch sử, pattern giống DA_FurnitureItem).

## Tổng quan
1 dòng trong danh sách chọn folder đích của WBP_MoveToFolderDialog (bản CŨ, trước C5.8). Thụt lề theo cấp, click để chọn, highlight khi đang chọn. Pattern tương tự WBP_ContextMenuItem.

## Layout
```
[Root] Horizontal Box
├── Spacer_Indent   (Spacer, Size mặc định X=0)
└── Button_Row      (Button — nền đổi màu khi chọn)
    └── TextBlock_Row
```

## Variables
| Tên | Kiểu | Ghi chú |
|---|---|---|
| TargetPath | String | Path folder dòng này đại diện. "" = "(Gốc)" |

## Event Dispatchers
```
OnRowClicked(TargetPath : String)
```

## Functions

### SetRow(Path : String, DisplayLabel : String, Indent : Integer)
```
SET TargetPath = Path
Set Text(TextBlock_Row, To Text(DisplayLabel))
Spacer_Indent → Set Size(X = Indent × 20, Y = 1)
```

### SetHighlight(bSelected : Boolean)
```
Branch(bSelected)
  True  → Set Background Color(Button_Row, R=0.2 G=0.4 B=1.0 A=0.4)
  False → Set Background Color(Button_Row, R=1 G=1 B=1 A=1)
```

### On Clicked (Button_Row) → HandleRowClicked → Broadcast OnRowClicked(TargetPath)

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 30/06/2026 | Khởi tạo — C5.4 Move Folder |
| — | 13/07/2026 | [SUPERSEDED] — không xoá file. Xác nhận qua REG C5.8: không còn call site nào dùng widget này. |
