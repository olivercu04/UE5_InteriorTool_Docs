# WBP_SaveComboDialog — Dialog Lưu Combo
**Version:** 1.0 | **Ngày:** 24/06/2026 | **Widget BP — dialog async nhập tên/folder/tags khi lưu combo**

## Mục đích
Dialog nhập thông tin trước khi lưu combo. Thay hardcode "MyCombo" tạm (C3b). Async — đóng băng selection trước khi mở.

## Expose on Spawn
| Tên | Kiểu | Vai trò |
|-----|------|---------|
| ExistingFolders | Array String | Folder có sẵn → nguồn cho CMB_Folder |
| TagVocabulary | Array String | Tags đã dùng → nguồn gợi ý (autocomplete defer) |

## Class Variables
| Tên | Kiểu | Vai trò |
|-----|------|---------|
| bIsCreatingNewFolder | Boolean | True khi user đang nhập folder mới thay chọn dropdown |

## Event Dispatchers (public)
- `OnDialogConfirmed(ComboName : String, FolderPath : String, Description : String, Tags : Array String)` — broadcast khi BTN_Confirm, trước Remove from Parent.
- `OnDialogCancelled()` — broadcast khi BTN_Cancel.

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
                │   └── HB_Folder_Row
                │       ├── CMB_Folder (ComboBox String, chiếm không gian còn lại)
                │       └── BTN_NewFolder (text TXT_NewFolderBtn = "+ Tạo mới")
                │   └── TextBox_FolderPath (Collapsed mặc định, placeholder "vd: Phòng khách/Ghế")
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
CLEAR Options CMB_Folder
ForEach ExistingFolders:
  Loop Body → Add Option(CMB_Folder, ArrayElement)
Completed:
  Set Is Enabled(BTN_Confirm, false)    ← tên rỗng → không confirm
  Bind OnTextChanged(TextBox_ComboName) → ValidateComboName
```

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

### BTN_NewFolder — OnClicked
```
SET bIsCreatingNewFolder = NOT bIsCreatingNewFolder
Branch bIsCreatingNewFolder:
  True:
    Set Visibility(CMB_Folder, Collapsed)
    Set Visibility(TextBox_FolderPath, Visible)
    Set Text(TextBox_FolderPath, "")
    Set Text(TXT_NewFolderBtn, "✕ Huỷ")
  False:
    Set Visibility(CMB_Folder, Visible)
    Set Visibility(TextBox_FolderPath, Collapsed)
    Set Text(TXT_NewFolderBtn, "+ Tạo mới")
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
Branch bIsCreatingNewFolder:
  True  → GET Text(TextBox_FolderPath) → ToString → Trim → SET TempFolder
  False → Get Selected Option(CMB_Folder) → SET TempFolder
Broadcast OnDialogConfirmed(TempName, TempFolder, TempDesc, TempTags)
Remove from Parent
```

## Event Destruct
(Không có ref hard cần clear trực tiếp — R4 OK. Ref dialog giữ ở WBP_FurnitureInventory.SaveComboDialogRef, clear ở OnSaveComboDialogClosed.)

## Lịch sử cập nhật
| Ngày | Version | Nội dung |
|------|---------|----------|
| 24/06/2026 | 1.0 | Tạo mới — C3b: dialog async lưu combo (ExistingFolders, TagVocabulary, bIsCreatingNewFolder, 2 dispatcher, ValidateComboName, ParseTags, BTN_NewFolder/Cancel/Confirm) |
