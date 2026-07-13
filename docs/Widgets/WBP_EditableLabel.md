# WBP_EditableLabel — Inline Rename Label
**Phiên bản:** 1.1 | **Tạo:** 27/06/2026 | **Sửa:** 13/07/2026 — thêm `SetLabelColor` (C5.8 2d) | **Dùng bởi:** WBP_TreeNode (C5.2), WBP_ChipTag (C5.4+), WBP_FolderPickerRow (C5.8)

---

## Tổng quan

Component tái dùng cho inline rename (Content Browser style). Overlay gồm TextBlock_Label (hiển thị) và EditBox (chỉnh sửa) + Border_Error (feedback lỗi). Trigger: caller gọi `EnterEditMode(SiblingNames)`. Kết thúc: Enter / focus out.

---

## Layout (Overlay)

```
Root: Overlay
├── TextBlock_Label          (Text Block)
├── EditBox                  (Editable Text Box, Collapsed, Select All Text When Focused=True)
└── Border_Error             (Collapsed, Overlay Slot Horizontal=Right)
    └── TextBlock_ErrorMsg
```

---

## Variables

| Tên | Kiểu | Default | Ghi chú |
|---|---|---|---|
| `OriginalText` | String | "" | Lưu text trước khi edit — dùng cho revert |
| `SiblingNames` | Array\<String\> | [] | Danh sách tên anh chị em — dùng để validate trùng |
| `bIsEditing` | Boolean | false | Guard reentrancy khi ExitEditMode fire OnTextCommitted lần 2 |

---

## Event Dispatchers

```
OnLabelRenameCommitted(NewName : String)
```

---

## Functions / Events

### SetLabel(NewText : String)
```
Set Text(TextBlock_Label, To Text(NewText))
```

### SetLabelColor(InColor : Slate Color) — MỚI 13/07/2026
```
▶ Set Color and Opacity(Target=TextBlock_Label, In Color and Opacity=InColor)
```
> `[CORRECTION]`: param type đúng là **Slate Color**, không phải Linear Color như patch gốc ghi — do `Set Color and Opacity` trên TextBlock (built-in UMG) khác API so với Image widget. Blueprint tự convert khi nối Linear Color var vào, không ảnh hưởng runtime.

### ValidateName(Candidate : String) → (bIsValid : Boolean, ErrorMsg : String) — Pure
```
Trim(Candidate) → Trimmed
Branch(Trimmed == "") → True: return (False, "Tên không được để trống")
Branch(String Contains(Trimmed, "/")) → True: return (False, "Tên không chứa ký tự /")
Branch(Array Contains(SiblingNames, Trimmed)) → True: return (False, "Tên đã tồn tại")
→ return (True, "")
```

### EnterEditMode(Siblings : Array\<String\>)
```
SET SiblingNames = Siblings
SET OriginalText = Get Text(TextBlock_Label) → To String
SET bIsEditing = True
Collapse(TextBlock_Label)
Collapse(Border_Error)
Visible(EditBox)
Set Text(EditBox, To Text(OriginalText))
Delay(0.0) → Set Keyboard Focus(EditBox)
```
> ⚠️ **Delay(0.0) bắt buộc** khi EnterEditMode được gọi từ luồng có Hide menu cùng frame — menu Hide steal focus trước khi EditBox nhận được. Delay(0.0) defer SetKeyboardFocus sang frame kế.

### ExitEditMode(bRevert : Boolean)
```
SET bIsEditing = False   ← PHẢI LÀ NODE ĐẦU TIÊN (guard reentrancy)
Collapse(EditBox)
Collapse(Border_Error)
Visible(TextBlock_Label)
Branch(bRevert):
  True  → Set Text(TextBlock_Label, To Text(OriginalText))
  False → (không đổi — caller đã pass validated name vào Broadcast)
```
> ⚠️ SET bIsEditing=False PHẢI TRƯỚC tất cả. Collapse EditBox → OnTextCommitted fire lần 2 → bIsEditing=False chặn reentrancy.

### OnEditBoxTextChanged(Text : String) — Bound từ EditBox.OnTextChanged
```
ValidateName(To String(Text)) → bIsValid, ErrorMsg
Branch(bIsValid):
  True  → Collapse(Border_Error)
  False → Set Text(TextBlock_ErrorMsg, To Text(ErrorMsg))
           Visible(Border_Error)
```

### OnEditBoxCommitted(Text : String, CommitMethod : ETextCommit) — Bound từ EditBox.OnTextCommitted
```
Branch(bIsEditing):
  False → dead-end   ← guard reentrancy
  True  →
    Switch on ETextCommit (Selection = CommitMethod):   ← PHẢI nối Selection pin = CommitMethod
      OnEnter →
        ValidateName(To String(Text)) → bIsValid, ErrorMsg
        Branch(bIsValid):
          False → Visible(Border_Error) → dead-end
          True  → ExitEditMode(False)
                   Broadcast OnLabelRenameCommitted(Trim(To String(Text)))   ← SAU ExitEditMode
      OnUserMovedFocus → ExitEditMode(True)
      OnCleared        → ExitEditMode(True)
      Default          → dead-end
```

> ⚠️ **CRITICAL — Switch.Selection pin:** Nếu Selection pin không kết nối CommitMethod → tất cả commit đi vào Default → rename không bao giờ fire.
>
> ⚠️ **Thứ tự Broadcast:** ExitEditMode TRƯỚC Broadcast. Broadcast → RefreshComboFolderUI → có thể destroy widget → node sau Broadcast không chạy.

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 27/06/2026 | Khởi tạo — C5.2 Inline Rename. Layout Overlay 3 con. ValidateName (empty/slash/dupe). EnterEditMode + Delay(0.0) focus. ExitEditMode guard bIsEditing. OnEditBoxCommitted Switch on ETextCommit. 3 bugs documented: Switch.Selection pin, Delay 0.0, Broadcast order. |
| 1.1 | 13/07/2026 | C5.8 2d — thêm `SetLabelColor(InColor : Slate Color)` (relay cho `WBP_FolderPickerRow.SetSearchHighlight`, cách B: không đục thẳng widget con). `[CORRECTION]`: type đúng là Slate Color, không phải Linear Color như patch gốc giả định. |
