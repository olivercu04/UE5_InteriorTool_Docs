# WBP_ParamColorRow
**Version:** 1.0 | **Ngày:** 15/09/2026 | **Tạo mới — S7G7T2, đóng PASS**

## Vai trò
Row UMG cho 1 param Color trong Material Param Panel (S7G7T3 sẽ dựng danh sách row từ
`GetControlsForMaterial`). Nhúng `UInteriorColorPickerWidget` (xem `Widgets/InteriorColorPicker.md`)
+ ô Hex, chuẩn hóa vòng đời edit về đúng 3 dispatcher (`OnEditBegin`/`OnPreviewChanged`/
`OnEditCommitted`) giống `WBP_ParamScalarRow`.

## Hierarchy (đã dọn — xem D2 lý do bỏ Preset)
```
Border_RowRoot
└── VerticalBox_Main
    ├── HorizontalBox_Header
    │     TextBlock_Label "Màu sắc" · Spacer_Header
    │     SizeBox_ColorPreview → Border_ColorPreview
    │     SizeBox_Hex → EditableTextBox_Hex
    ├── Spacer_01
    └── SizeBox_CustomPicker → InteriorColorPicker (UInteriorColorPickerWidget)
```
> `[WrapBox_Presets]` + 8 `Button_Preset` — ĐÃ XÓA khỏi widget (quyết định D2 dưới, không phải
> thiếu sót).

## Variables + Event Dispatchers
```
ParamName : Name · CurrentColor : LinearColor       ← CurrentColor = nguồn sự thật DUY NHẤT
OnEditBegin() · OnPreviewChanged(Value:LinearColor) · OnEditCommitted(Value:LinearColor)
```

## Function `SyncCurrentColor(NewColor:LinearColor)` — hub đồng bộ duy nhất
```
SET CurrentColor = NewColor
▶→ Border_ColorPreview.SetBrushColor(CurrentColor)
▶→ EditableTextBox_Hex.SetText( Conv_StringToText( ToHex_LinearColor(CurrentColor) ) )
▶→ InteriorColorPicker.SetColor(CurrentColor)     ← an toàn: no-op nếu picker đang bIsInteracting
```
Mọi nguồn đổi màu (Picker kéo, Hex gõ, sau này Reset/Undo) đều PHẢI gọi qua hàm này — không đường
nào được ghi `CurrentColor` hay update UI con trực tiếp bên ngoài `SyncCurrentColor`.

## Function `Setup(InLabel:Text, InParamName:Name, InInitialColor:LinearColor)`
```
SET ParamName = InParamName
▶→ TextBlock_Label.SetText(InLabel)
▶→ Call SyncCurrentColor(InInitialColor)
```

## Event flow (xác nhận qua K2Node export thật — `OnColorChanged` + `Setup` + `OnTextCommitted`)
```
InteriorColorPicker.OnInteractionBegin ▶→ Call OnEditBegin

InteriorColorPicker.OnColorChanged(NewColor)
▶→ Call SyncCurrentColor(NewColor)
▶→ Call OnPreviewChanged(Value = GET CurrentColor)   ← GET lại, KHÔNG dùng output pin của SET
                                                         (2 lời gọi hàm tách biệt, không cùng chuỗi exec)

InteriorColorPicker.OnInteractionEnd(NewColor)
▶→ Call SyncCurrentColor(NewColor)
▶→ Call OnEditCommitted(Value = GET CurrentColor)

EditableTextBox_Hex.OnTextCommitted(Text, CommitMethod)
▶→ Conv_TextToString(Text) → HexToLinearColor(...) ●→ bSuccess, OutColor
▶→ Branch(bSuccess):
     True  ▶→ Call SyncCurrentColor(OutColor)
            ▶→ Call OnEditBegin ▶→ Call OnEditCommitted(Value = GET CurrentColor)
     False ▶→ EditableTextBox_Hex.SetText( Conv_StringToText( ToHex_LinearColor(GET CurrentColor) ) )
            ← REVERT LẶNG LẼ, KHÔNG bắn dispatcher nào (quyết định D3)
```
> `OnInteractionBegin`/`OnInteractionEnd` xác nhận qua **test PASS** (log Begin×1/Preview nhiều/
> Committed×1 đúng nhịp khi kéo wheel) — pattern giống `OnColorChanged` đã export, không lặp lại
> export riêng.

`HexToLinearColor` — hàm C++ mới, xem `Data/MaterialSlotService_Reference.md` mục
"UMaterialParamMap" (cùng class `UMaterialParamMap`, không phải file mới).

## 3 quyết định kiến trúc chốt trong phiên (khác task card gốc)

**D1 — `CurrentColor` single-source-of-truth pattern.** Task card gốc không đặc tả rõ; cuhoang chủ
động chốt: mọi UI con (Border/Hex/Picker) đọc từ 1 biến `CurrentColor` DUY NHẤT, đồng bộ qua 1 hàm
hub `SyncCurrentColor` — không cho phép state rải rác nhiều nơi dễ lệch nhau. **Giữ pattern này làm
mẫu cho mọi widget multi-display sau này trong G7 (và G8/G9).**

**D2 — Bỏ 8 `Button_Preset` khỏi `WBP_ParamColorRow` v1 (không phải quên, là quyết định có chủ
đích).** cuhoang phân biệt 3 nhu cầu UX khác nhau của "swatch màu":
  - **Color Picker** — "tôi muốn tìm màu mới" (đã có, wheel+hex).
  - **Project Palette** (chưa làm) — "tôi muốn dùng lại màu đang có trong thiết kế".
  - **Recent Colors** (chưa làm) — "tôi vừa dùng màu này, lấy lại nhanh".
  Preset tĩnh 8 màu cố định không phục vụ đúng nhu cầu nào trong 3 cái trên — dồn việc dựng swatch
  UI lại khi Project Palette/Recent Colors có dữ liệu thật để suggest (sau G7, chưa có ETA).
  **Ghi backlog UX** (`DEVIATIONS.md`), không phải nợ kỹ thuật.

**D3 — Lỗi hex sai → CHỈ revert, KHÔNG đỏ chữ + Timer.** Thu hẹp so với task card gốc ("inline
error + revert"). Lý do: revert (chữ rác biến mất, giá trị đúng quay lại) tự nó đã là tín hiệu đủ
rõ; thêm Timer kéo theo latent + state màu-chữ cho lợi ích nhỏ. Không latent = đúng luật L8 (Latent
chỉ trong Custom Event, ở đây tránh hẳn không cần).

## Test — PASS toàn bộ (15/09/2026)
- Đường Picker cô lập: spawn màu Green → Border/Hex/Wheel đồng bộ đúng ngay · kéo wheel → Border
  đổi LIVE + hex chạy theo + Begin×1/Preview nhiều/Committed×1.
- `HexToLinearColor` cô lập: 4/4 (hex hợp lệ có/không `#`, hex rác, sai độ dài).
- Tích hợp đầy đủ: hex hợp lệ commit đúng · hex rác revert lặng lẽ không dispatcher · 6 và 8 ký tự
  đều nhận · xen kẽ wheel/hex nhiều lần không lệch nhau · spawn lại từ đầu đúng ngay lập tức.

Q9: MIỄN (standalone, không đụng `SelectedActors`).

## Nợ nhẹ (chưa sửa, không chặn T3)
`HexToLinearColor` trong `OnTextCommitted` bị đọc pin 2 lần (`ReturnValue` cho Branch, `OutColor`
cho `SyncCurrentColor`) → UE chạy lại toàn bộ chuỗi `Conv_TextToString→HexToLinearColor` 2 lần. Vô
hại ở đây (hàm rẻ). cuhoang chọn giữ nguyên — nợ nhẹ, cân nhắc SET-vào-var nếu chạm lại file này ở
G8/G9.

---

## Lịch sử cập nhật

| Ngày | Version | Nội dung |
|------|---------|----------|
| 15/09/2026 | 1.0 | Tạo mới — S7G7T2. `SyncCurrentColor` hub duy nhất + `Setup` + event flow (Picker/Hex → 3 dispatcher chuẩn hóa). 3 quyết định kiến trúc: D1 single-source-of-truth, D2 bỏ preset tĩnh (backlog Project Palette/Recent Colors), D3 hex-error chỉ revert không Timer. Test PASS toàn bộ. Nguồn: `DELTA — S7G7T2 AS-BUILT` (Opus+Sonnet, 15/09/2026). |
