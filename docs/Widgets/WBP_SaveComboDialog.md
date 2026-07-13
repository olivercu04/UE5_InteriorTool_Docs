# WBP_SaveComboDialog — Dialog Lưu Combo
**Version:** 2.0 | **Ngày:** 24/06/2026 | **Sửa:** 13/07/2026 — C5.8 Wire Save: thay field Folder cũ bằng `WBP_FolderTreePicker` + `BTN_AddFolder` | **Widget BP — dialog async nhập tên/folder/tags khi lưu combo**

## Mục đích
Dialog nhập thông tin trước khi lưu combo. Thay hardcode "MyCombo" tạm (C3b). Async — đóng băng selection trước khi mở.

## Expose on Spawn
| Tên | Kiểu | Vai trò |
|-----|------|---------|
| TagVocabulary | Array String | Tags đã dùng → nguồn gợi ý (autocomplete defer) |

## Class Variables
| Tên | Kiểu | Vai trò |
|-----|------|---------|
| Picker | WBP_FolderTreePicker | Is Variable=✓ — picker compact chọn folder lưu |

## Event Dispatchers (public)
- `OnDialogConfirmed(ComboName : String, FolderPath : String, Description : String, Tags : Array String)` — broadcast khi BTN_Confirm, trước Remove from Parent.
- `OnDialogCancelled()` — broadcast khi BTN_Cancel.
- `OnRequestCreateFolder(ParentPath : String)` — MỚI 13/07 — broadcast khi BTN_AddFolder.OnClicked.

## Layout
```
CanvasPanel (root — Anchors Fill, Hit-Test Invisible để block click xuyên)
├── Border_backdrop (Anchors Fill, Opacity=0.6, màu đen — overlay backdrop)
└── Overlay_centerlayer (Anchors Center, Alignment 0.5/0.5)
    └── SizeBox (480×400)
        └── Border (bo góc, padding 20)
            └── VB_Content (VerticalBox, spacing 10)
                ├── TXT_Title (Text "Lưu Combo", Bold)
                ├── Spacer (8px)
                ├── VB_Field_ComboName
                │   ├── TextBlock "Tên combo *"
                │   └── TextBox_ComboName (placeholder "Nhập tên...")
                ├── VB_Field_Folder
                │   ├── TextBlock "Folder"
                │   ├── SizeBox (~180px cao) → Picker (WBP_FolderTreePicker, compact)
                │   └── BTN_AddFolder (text "+ Thư mục mới")
                ├── VB_Field_Description
                │   ├── TextBlock "Mô tả"
                │   └── TextBox_Description_MultiLine (multi-line, 3 dòng)
                ├── VB_Field_Tags
                │   ├── TextBlock "Tags (ngăn cách bởi dấu phẩy)"
                │   └── TextBox_Tags (placeholder "vd: hiện đại, văn phòng")
                ├── Spacer_fill (Fill)
                └── HB_Buttons
                    ├── Spacer_PushLeft (Fill)
                    ├── BTN_Cancel (text "Huỷ")
                    └── BTN_Confirm (text "Lưu", disabled mặc định)
```

## Event Construct
```
Set Is Enabled(BTN_Confirm, false)    ← tên rỗng → không confirm
Bind OnTextChanged(TextBox_ComboName) → ValidateComboName
```
> **13/07:** xoá đoạn cũ `CLEAR Options CMB_Folder` + `ForEach ExistingFolders → Add Option` — `CMB_Folder` không còn tồn tại. Folder data giờ nạp từ ngoài qua `Picker.SetFolders(Entries)` (gọi từ `WBP_FurnitureInventory.OpenSaveComboDialog`), không tự load trong Construct.

## Functions

### ValidateComboName(Text : Text)
```
Text ●→ ToString ●→ IsEmpty
Branch:
  True  → Set Is Enabled(BTN_Confirm, false)
  False → Set Is Enabled(BTN_Confirm, true)
Return
```

### ParseTags(RawText : String) → Tags : Array String
```
Local: ResultArray (Array String)
ParseIntoArray(RawText, Delimiter=",", CullEmpty=true) → TempArray
ForEach TempArray:
  Loop Body:
    Trim(ArrayElement) → ToLower → TempTag
    IsEmpty(TempTag) → Branch:
      True  → dead-end (skip)
      False → ADD TempTag → ResultArray
Completed → Return(Tags = ResultArray)
```

## Button Handlers

### BTN_AddFolder — OnClicked (MỚI 13/07, thay BTN_NewFolder cũ)
```
Broadcast OnRequestCreateFolder(Picker.SelectedPath)
```

### BTN_Cancel — OnClicked
```
Broadcast OnDialogCancelled
Remove from Parent
```

### BTN_Confirm — OnClicked
```
Local: TempName (String), TempDesc (String), TempFolder (String), TempTags (Array String)
GET Text(TextBox_ComboName) → ToString → SET TempName
GET Text(TextBox_Description_MultiLine) → ToString → SET TempDesc
GET Text(TextBox_Tags) → ToString → ParseTags → SET TempTags
GET Picker.SelectedPath → SET TempFolder            ← 13/07: thay nhánh Branch bIsCreatingNewFolder cũ
Broadcast OnDialogConfirmed(TempName, TempFolder, TempDesc, TempTags)
Remove from Parent
```

`TagVocabulary`, field Name/Description/Tags, `ValidateComboName`, `ParseTags` — giữ nguyên.

## Event Destruct
(Không có ref hard cần clear trực tiếp — R4 OK. Ref dialog giữ ở WBP_FurnitureInventory.SaveComboDialogRef, clear ở OnSaveComboDialogClosed.)

## Test PASS: S6a, S6c
## Test [SCOPE — không áp dụng]: S6b (context-menu rename không tồn tại theo thiết kế 2d)

## Lịch sử cập nhật
| Ngày | Version | Nội dung |
|------|---------|----------|
| 24/06/2026 | 1.0 | Tạo mới — C3b: dialog async lưu combo (ExistingFolders, TagVocabulary, bIsCreatingNewFolder, 2 dispatcher, ValidateComboName, ParseTags, BTN_NewFolder/Cancel/Confirm) |
| 13/07/2026 | 2.0 | **C5.8 Wire Save.** Xoá hẳn: `CMB_Folder`, `BTN_NewFolder`, `TextBox_FolderPath`, `HB_Folder_Row`, var `bIsCreatingNewFolder`, pin `ExistingFolders` (Expose on Spawn), đoạn Event Construct cũ (CLEAR Options + ForEach ExistingFolders). Thêm: var `Picker : WBP_FolderTreePicker` (SizeBox ~180px, compact); `BTN_AddFolder` (text "+ Thư mục mới"); dispatcher `OnRequestCreateFolder(ParentPath)`; `BTN_AddFolder.OnClicked` broadcast `OnRequestCreateFolder(Picker.SelectedPath)`; `BTN_Confirm` đổi nhánh folder sang `GET Picker.SelectedPath`. `TagVocabulary`/field Name-Description-Tags/`ValidateComboName`/`ParseTags` giữ nguyên. Test PASS: S6a, S6c. S6b [SCOPE — không áp dụng]. |
