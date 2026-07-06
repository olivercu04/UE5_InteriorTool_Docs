# WBP_ConfirmDialog
**Phiên bản:** 1.0 | **Tạo:** 06/07/2026 — C5.6 Xóa Folder

---

## Tổng quan
Dialog xác nhận generic (Yes/No) — dùng lại được cho mọi hành động cần confirm trước khi thực thi (đầu tiên dùng cho C5.6 Xóa folder). KHÔNG chứa logic nghiệp vụ riêng — caller truyền `Message`/`ConfirmLabel` qua Expose on Spawn, nghe `OnConfirmed` để tự xử lý hành động thật.

## Layout
```
Root Overlay
└─ Border_Backdrop (full-screen, đen alpha ~0.4)
   └─ Border_Panel (center, ~380×160)
      └─ VerticalBox
         ├─ TXT_Message (multi-line)
         └─ HorizontalBox [BTN_Cancel "Hủy"] [BTN_Confirm]
```

## Variables (Expose on Spawn)
| Tên | Kiểu | Ghi chú |
|---|---|---|
| `Message` | Text | Nội dung cảnh báo, set vào `TXT_Message` |
| `ConfirmLabel` | Text | Nhãn nút Confirm (vd "Xóa") — set vào TextBlock con của `BTN_Confirm` |

## Event Dispatchers
```
OnConfirmed()   ← không param, caller tự biết đang confirm hành động gì qua context đã lưu (vd PendingDeleteFolderPath)
```

## Functions

### Event Construct
```
SetText(TXT_Message, Message)
SetText(BTN_Confirm's TextBlock, ConfirmLabel)
Set Keyboard Focus(self)
```
> ⚠️ **BUG FIX (Class Defaults):** `bIsFocusable` phải TICK = true trên WBP_ConfirmDialog, nếu không `Set Keyboard Focus(self)` không có tác dụng — UMG mặc định `bIsFocusable = false`, gây warning "does not support focus" và Esc không hoạt động. Áp dụng cho MỌI widget dùng `Set Keyboard Focus(self)` ở cấp UserWidget (không áp dụng cho widget native con như EditableTextBox — tự nó đã focusable).

### BTN_Confirm.OnClicked
```
Broadcast OnConfirmed
Remove from Parent
```

### BTN_Cancel.OnClicked
```
Remove from Parent
```

### OnKeyDown — override
```
Branch(Key == Escape):
  True  → Remove from Parent → Return Handled
  False → Return Unhandled
```

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 06/07/2026 | Khởi tạo — C5.6 Xóa Folder (widget generic, dùng lại được cho mọi confirm dialog sau này) |
