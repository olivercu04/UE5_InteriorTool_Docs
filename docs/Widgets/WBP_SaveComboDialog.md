# WBP_SaveComboDialog — Dialog Lưu Combo
**Version:** 2.2 | **Ngày:** 24/06/2026 | **Sửa:** 13/07/2026 — C5.8 Wire Save: thay field Folder cũ bằng `WBP_FolderTreePicker` + `BTN_AddFolder` | 07/08/2026 — T3 Save As/Save Đè: nút `BTN_Overwrite` + `RefreshButtonStates()` + prefill | 07/08/2026 (T4) — `BTN_Overwrite` broadcast dispatcher thật `OnDialogConfirmedOverwrite`, thay Print tạm | **Widget BP — dialog async nhập tên/folder/tags khi lưu combo, hỗ trợ ghi đè combo gốc**

## Mục đích
Dialog nhập thông tin trước khi lưu combo. Thay hardcode "MyCombo" tạm (C3b). Async — đóng băng selection trước khi mở. Từ T3 (07/08): kiêm luôn UX Save As (lưu thành combo mới) / Save Đè (ghi đè combo gốc), 2 nút song song trong `HB_Buttons`.

## Expose on Spawn
| Tên | Kiểu | Vai trò |
|-----|------|---------|
| TagVocabulary | Array String | Tags đã dùng → nguồn gợi ý (autocomplete defer) |
| bOverwriteAllowed | Bool | ⚠ [Nguồn: `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 7b.4, ✓ as-built theo 7c — hạ tầng dựng trước phiên T3 07/08, CHƯA từng phân phối vào file này trước đợt merge này] Gate `BTN_Overwrite`: true → cho ghi đè |
| OverwriteComboID | String | ⚠ nt — ComboID sẽ bị ghi đè nếu user bấm `BTN_Overwrite` |
| OverwriteName | String | ⚠ nt — tên combo gốc, dùng dựng label `BTN_Overwrite` ở Event Construct |
| DisabledReason | String | ⚠ nt — lý do `BTN_Overwrite` bị xám, set làm ToolTipText của `Border_OverwriteWrap` |
| PrefillName | String | ⚠ nt — prefill `TextBox_ComboName` khi đang ở case ghi đè |
| PrefillFolder | String | ⚠ nt — prefill folder, dùng ở `WBP_FurnitureInventory.OpenSaveComboDialog` (`Picker.ExpandToPath`/`SelectedPath`), KHÔNG set trực tiếp trong Construct |
| PrefillDesc | String | ⚠ nt — prefill `TextBox_Description_MultiLine` |
| PrefillTagsText | String | ⚠ nt — prefill `TextBox_Tags` |

## Class Variables
| Tên | Kiểu | Vai trò |
|-----|------|---------|
| Picker | WBP_FolderTreePicker | Is Variable=✓ — picker compact chọn folder lưu |

## Event Dispatchers (public)
- `OnDialogConfirmed(ComboName : String, FolderPath : String, Description : String, Tags : Array String)` — broadcast khi BTN_Confirm, trước Remove from Parent.
- `OnDialogConfirmedOverwrite(ComboID : String, ComboName : String, FolderPath : String, Description : String, Tags : Array String)` — MỚI 07/08/2026 (T4) — broadcast khi `BTN_Overwrite` với `bOverwriteAllowed=true`, trước Remove from Parent.
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
                    ├── Border_OverwriteWrap ⚠ [Nguồn: 7b.4/7c, xem ghi chú Expose on Spawn] — bọc BTN_Overwrite, ToolTipText = DisabledReason
                    │   └── BTN_Overwrite (text "Ghi đè "<OverwriteName>"", đặt bên TRÁI BTN_Confirm)
                    └── BTN_Confirm (text "Lưu thành combo mới…", disabled mặc định)
```

## Event Construct
**✓TEST 07/08/2026 (T3)** — dựng lại toàn bộ: bản Construct cũ (13/07) đã bị xóa mất trong quá
trình làm việc trước phiên T3 mà không được ghi log; đoạn dưới đây là bản THẬT xác nhận qua
K2Node export + test tay 07/08/2026, thay hoàn toàn 2 dòng cũ (`Set Is Enabled(BTN_Confirm,
false)` đơn lẻ + bind rời).
```
Event Construct
▶→ SetText(TextBox_ComboName, Conv_StringToText(PrefillName))
▶→ SetText(TextBox_Description_MultiLine, Conv_StringToText(PrefillDesc))
▶→ SetText(TextBox_Tags, Conv_StringToText(PrefillTagsText))
▶→ SET Text(<TextBlock con của BTN_Overwrite>) =
     Conv_StringToText(Append("Ghi đè \"", OverwriteName, "\""))
▶→ RefreshButtonStates()
▶→ Bind Event to OnTextChanged (Target=TextBox_ComboName) → Event=ValidateComboName
```
> Folder prefill do `Picker` lo ở `WBP_FurnitureInventory.OpenSaveComboDialog` (Việc 5,
> `Picker.SelectedPath` + `Picker.RefreshVisibleRows()`), KHÔNG set trong Construct.
> Dòng `Bind OnTextChanged → ValidateComboName` là phần PHỤC HỒI — đã có từ v2.0 (24/06) nhưng
> bị mất trong lúc sửa trước phiên T3, dựng lại đúng nguyên bản.
> **13/07 (vẫn đúng, không đổi):** `CLEAR Options CMB_Folder` + `ForEach ExistingFolders → Add
> Option` đã xóa từ trước — `CMB_Folder` không còn tồn tại. Folder data nạp từ ngoài qua
> `Picker.SetFolders(Entries)`.

## Functions

### RefreshButtonStates() — MỚI 07/08/2026 (T3), nguồn DUY NHẤT quyết định trạng thái 2 nút
**✓TEST 07/08/2026** — Local var: `bNameOK` (Bool)
```
Entry
▶→ TextBox_ComboName.Text ●→ Conv_TextToString ●→ IsEmpty ●→ Not_PreBool ●→ SET bNameOK
▶→ Set Is Enabled(BTN_Confirm, bNameOK)
▶→ BooleanAND(bNameOK, bOverwriteAllowed) ●→ Set Is Enabled(BTN_Overwrite, <kết quả AND>)
▶→ Set Tool Tip Text(Border_OverwriteWrap, Conv_StringToText(DisabledReason))
▶→ Return
```
> Tên rỗng → **CẢ HAI** nút xám (không chỉ `BTN_Confirm` như thiết kế v2.0 cũ) — nếu chỉ gate
> `BTN_Confirm`, `BTN_Overwrite` sống lúc tên rỗng → ghi metadata rỗng đè lên combo thật.
> Ghi chú: `bNameOK` đọc lại qua Get riêng (không dùng Output_Get của node SET) — không phải bug,
> chỉ là cách nối khác; pure Get luôn ra cùng giá trị vì không ai SET lại giữa 2 lần đọc.

### ValidateComboName(Text : Text) — SỬA 07/08/2026 (T3), thay hoàn toàn thân hàm cũ
**✓TEST 07/08/2026**
```
Entry.then ▶→ RefreshButtonStates(Target=self) ▶→ Return Node
```
> Pin `Text` (input) không nối vào đâu — cố ý, `RefreshButtonStates` tự đọc lại
> `TextBox_ComboName.Text` bên trong nó. Luật 6B: 2 đường gọi (Event Construct và
> OnTextChanged) nay dẫn cùng 1 cấu trúc, cho cùng kết quả.

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

### BTN_Overwrite — OnClicked (MỚI 07/08/2026, T3 — SỬA 07/08/2026, T4 DONE)
**✓TEST 07/08/2026 (T4)** — thay Print tạm (T3) bằng broadcast dispatcher thật.
```
OnClicked
▶→ Branch(bOverwriteAllowed)
     True  ▶→ ParseTags(Conv_TextToString(TextBox_Tags.Text)) ●→ TempTags_Overwrite
           ▶→ CallDelegate OnDialogConfirmedOverwrite(
                 ComboID     = OverwriteComboID,
                 ComboName   = Conv_TextToString(TextBox_ComboName.Text),
                 FolderPath  = Picker.SelectedPath,
                 Description = Conv_TextToString(TextBox_Description_MultiLine.Text),
                 Tags        = TempTags_Overwrite)
           ▶→ Remove from Parent
     False ▶→ (bản COPY nguyên xi chuỗi hành vi của BTN_Confirm.OnClicked bên dưới:
                SET TempName/TempDesc/TempTags từ 3 ô nhập → ParseTags →
                SET TempFolder = Picker.SelectedPath →
                Broadcast OnDialogConfirmed(TempName, TempFolder, TempDesc, TempTags) →
                Remove from Parent)
```
> Nhánh `False` là **bản sao độc lập**, KHÔNG dùng chung hàm với `BTN_Confirm.OnClicked` (quyết
> định 7c — không tách hàm dùng chung, không refactor, KP3). Ngữ nghĩa: sửa tên trong ô rồi bấm
> **Ghi đè** = **đổi tên tại chỗ**, `comboId` GIỮ NGUYÊN — đúng mô hình Save của phần mềm desktop.
> KHÔNG phải bug.
> **07/08/2026 (T4 DONE):** Print debug `"T3-OVERWRITE"` đã XÓA. Nhánh `True` giờ broadcast
> `OnDialogConfirmedOverwrite` — `WBP_FurnitureInventory.HandleSaveComboOverwriteConfirmed` lắng
> nghe và gọi `SaveComboFromSelection(bOverwrite=true, OverwriteComboID=ComboID)` thật. Xem
> `Blueprints/BP_ComboManager.md` v1.16, `Widgets/WBP_FurnitureInventory.md` mục
> `HandleSaveComboOverwriteConfirmed`.

### BTN_Confirm — OnClicked
**Sửa 07/08/2026 (T3):** text đổi thành "Lưu thành combo mới…" (Designer), thân hàm KHÔNG đổi.
```
Local: TempName (String), TempDesc (String), TempFolder (String), TempTags (Array String)
GET Text(TextBox_ComboName) → ToString → SET TempName
GET Text(TextBox_Description_MultiLine) → ToString → SET TempDesc
GET Text(TextBox_Tags) → ToString → ParseTags → SET TempTags
GET Picker.SelectedPath → SET TempFolder            ← 13/07: thay nhánh Branch bIsCreatingNewFolder cũ
Broadcast OnDialogConfirmed(TempName, TempFolder, TempDesc, TempTags)
Remove from Parent
```

`TagVocabulary`, field Name/Description/Tags, `ParseTags` — giữ nguyên. `ValidateComboName` sửa
07/08/2026 (T3, xem mục Functions ở trên).

## Event Destruct
(Không có ref hard cần clear trực tiếp — R4 OK. Ref dialog giữ ở WBP_FurnitureInventory.SaveComboDialogRef, clear ở OnSaveComboDialogClosed.)

## Test PASS: S6a, S6c
## Test [SCOPE — không áp dụng]: S6b (context-menu rename không tồn tại theo thiết kế 2d)
## Test PASS (07/08/2026, T3): 6/6 case (`Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục
7c "TEST T3") + 2 câu hiểu bài PASS.
## Test PASS (07/08/2026, T4): 6/6 case (`Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục
7d.5) + 2 câu hiểu bài PASS.

## Lịch sử cập nhật
| Ngày | Version | Nội dung |
|------|---------|----------|
| 24/06/2026 | 1.0 | Tạo mới — C3b: dialog async lưu combo (ExistingFolders, TagVocabulary, bIsCreatingNewFolder, 2 dispatcher, ValidateComboName, ParseTags, BTN_NewFolder/Cancel/Confirm) |
| 13/07/2026 | 2.0 | **C5.8 Wire Save.** Xoá hẳn: `CMB_Folder`, `BTN_NewFolder`, `TextBox_FolderPath`, `HB_Folder_Row`, var `bIsCreatingNewFolder`, pin `ExistingFolders` (Expose on Spawn), đoạn Event Construct cũ (CLEAR Options + ForEach ExistingFolders). Thêm: var `Picker : WBP_FolderTreePicker` (SizeBox ~180px, compact); `BTN_AddFolder` (text "+ Thư mục mới"); dispatcher `OnRequestCreateFolder(ParentPath)`; `BTN_AddFolder.OnClicked` broadcast `OnRequestCreateFolder(Picker.SelectedPath)`; `BTN_Confirm` đổi nhánh folder sang `GET Picker.SelectedPath`. `TagVocabulary`/field Name-Description-Tags/`ValidateComboName`/`ParseTags` giữ nguyên. Test PASS: S6a, S6c. S6b [SCOPE — không áp dụng]. |
| 07/08/2026 | 2.1 | **T3 Save As/Save Đè — ĐÓNG.** Thêm 8 Expose on Spawn (`bOverwriteAllowed`/`OverwriteComboID`/`OverwriteName`/`DisabledReason`/`PrefillName`/`PrefillFolder`/`PrefillDesc`/`PrefillTagsText` — ⚠ hạ tầng dựng từ trước phiên T3 theo 7b.4/7c, lần đầu phân phối vào file này); `Border_OverwriteWrap`+`BTN_Overwrite` (Layout); `BTN_Confirm` đổi text → "Lưu thành combo mới…". Function mới `RefreshButtonStates()` (nguồn duy nhất quyết định 2 nút, cả 2 xám khi tên rỗng). `ValidateComboName` thay thân hoàn toàn → gọi `RefreshButtonStates`. `Event Construct` dựng lại toàn bộ (bản 13/07 bị mất không ghi log) — prefill 3 ô + label `BTN_Overwrite` + `RefreshButtonStates()` + bind `OnTextChanged`. `BTN_Overwrite.OnClicked` mới — Branch `bOverwriteAllowed`: True→Print debug (T4 mở dispatcher thật); False→bản copy độc lập luồng `BTN_Confirm` (Save As), KHÔNG dùng chung hàm (KP3). Đóng `Bug-SaveConfirm-EmptyName` (`Bugs/Open_Bugs.md`). Test PASS 6/6 case + 2 câu hiểu bài. Nguồn: command block 07/08/2026, K2Node export + test tay. |
| 07/08/2026 (15:40) | 2.2 | **T4 Overwrite Flow — ĐÓNG.** Dispatcher mới `OnDialogConfirmedOverwrite(ComboID, ComboName, FolderPath, Description, Tags)`. `BTN_Overwrite.OnClicked` nhánh `True`: XÓA Print debug `"T3-OVERWRITE"`, thay bằng `ParseTags` + `CallDelegate OnDialogConfirmedOverwrite(...)` + `Remove from Parent` — cấu trúc nhánh `False` (Save As, KHÔNG dùng chung hàm với `BTN_Confirm`) giữ nguyên. Test PASS 6/6 case (`Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 7d.5, bao gồm S8 mix combo+mesh rời) + 2 câu hiểu bài. Nguồn: `DELTA_07-08-2026_T4_Overwrite.md` (Opus). |
