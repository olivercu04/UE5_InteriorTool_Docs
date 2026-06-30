# WBP_MoveFolderRow
**Phiên bản:** 1.0 | **Tạo:** 30/06/2026 — C5.4 Move Folder

---

## Tổng quan
1 dòng trong danh sách chọn folder đích của WBP_MoveToFolderDialog. Thụt lề theo cấp, click để chọn, highlight khi đang chọn. Pattern tương tự WBP_ContextMenuItem.

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
