# WBP_ParamColorRow
**Version:** 1.2 | **Cập nhật:** 24/09/2026 16:10 — **U2.4:** `OnEditBegin` +input `ParamName:Name` (đối xứng `WBP_ParamScalarRow` v1.2); 2 chỗ `Call OnEditBegin` nối `GET ParamName`. W3 bên Color XÁC NHẬN qua PIE: `OnInteractionBegin` → BEGIN bắn đúng 1 lần/lần chỉnh. + bánh xe màu nay khớp màu seed nhờ fix C++ `InteriorColorPicker.SetColor` (xem `InteriorColorPicker.md`) — row KHÔNG phải sửa gì cho fix đó.
**Version:** 1.1 | **Cập nhật:** 18/09/2026 — **S7G7T4:** dispatcher `OnPreviewChanged`/`OnEditCommitted` thêm `ParamName:Name` (như `WBP_ParamScalarRow` v1.1). **+ Bug B3 (bắt qua log):** lần đầu nối `GET ParamName` chỉ vào `OnEditCommitted`, SÓT node `OnPreviewChanged` trong `OnColorChanged` → preview broadcast `ParamName=None` → `SetSlotVectorParam(None)` fail im lặng → **live-preview màu hỏng ngầm** (mesh chỉ nhảy màu lúc thả, không đổi live). Fix: nối `GET ParamName` vào cả node preview + node hex-commit. Test PASS (màu + hex đều LIVE). Xem B3 dưới.
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
OnEditBegin(ParamName:Name) · OnPreviewChanged(ParamName:Name, Value:LinearColor) · OnEditCommitted(ParamName:Name, Value:LinearColor)
```
> **[v1.1 18/09]** `ParamName` là input MỚI (v1.0 chỉ có `Value`) — cùng lý do `WBP_ParamScalarRow` v1.1: 1 handler T4 chung cho mọi row Color.

## Function `SyncCurrentColor(NewColor:LinearColor)` — hub đồng bộ duy nhất
```
SET CurrentColor = NewColor
▶→ Border_ColorPreview.SetBrushColor(CurrentColor)
▶→ EditableTextBox_Hex.SetText( Conv_StringToText( ToHex_LinearColor(CurrentColor) ) )
▶→ InteriorColorPicker.SetColor(CurrentColor)     ← an toàn: no-op nếu picker đang bIsInteracting
```
> **[v1.2 — 24/09]** `Setup` gọi `SyncCurrentColor` → `SetColor` TRƯỚC khi row được `AddParamRow` (Slate picker chưa
> dựng). Trước fix C++ 24/09, `SetColor` lúc đó bị bỏ im lặng → bánh xe + thanh sáng đứng ở trắng dù ô màu/hex đúng
> (hex là TextBox UMG, tự giữ text dù chưa dựng). Từ khi seed luôn trắng thì lỗi bị che — lộ khi seed đọc đúng MI.
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
InteriorColorPicker.OnInteractionBegin ▶→ Call OnEditBegin(GET ParamName)     ← v1.2

InteriorColorPicker.OnColorChanged(NewColor)
▶→ Call SyncCurrentColor(NewColor)
▶→ Call OnPreviewChanged(GET ParamName, Value = GET CurrentColor)   ← v1.1: +GET ParamName (đây là node từng SÓT gây B3)
                                                         (GET lại, KHÔNG dùng output pin của SET — 2 lời gọi hàm tách biệt)

InteriorColorPicker.OnInteractionEnd(NewColor)
▶→ Call SyncCurrentColor(NewColor)
▶→ Call OnEditCommitted(GET ParamName, Value = GET CurrentColor)    ← v1.1: +GET ParamName

EditableTextBox_Hex.OnTextCommitted(Text, CommitMethod)
▶→ Conv_TextToString(Text) → HexToLinearColor(...) ●→ bSuccess, OutColor
▶→ Branch(bSuccess):
     True  ▶→ Call SyncCurrentColor(OutColor)
            ▶→ Call OnEditBegin(GET ParamName) ▶→ Call OnEditCommitted(GET ParamName, Value = GET CurrentColor)   ← v1.1: +GET ParamName
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

## Bug B3 — Live-preview màu hỏng ngầm do sót wire ParamName (18/09/2026, S7G7T4)
**Triệu chứng:** kéo bánh xe màu, mesh KHÔNG đổi màu live; chỉ nhảy màu đúng lúc thả tay.
**Log bắt được:**
```
Warning: SetSlotVectorParam|...|Param 'None' không tồn tại trên material   ← preview, FAIL
         SetSlotVectorParam|...|OK Tint                                     ← commit, OK
```
**Root cause:** khi nâng dispatcher lên 2 input (v1.1), đã nối `GET ParamName` vào node `OnEditCommitted`
nhưng SÓT node `OnPreviewChanged` (trong `OnColorChanged`) → pin `ParamName` rỗng → broadcast `None`
→ `SetSlotVectorParam(None)` guard-fail, no-op. Commit (Tint) đúng nên undo value vẫn chạy → dễ tưởng ổn.
**Cách phát hiện:** đọc log `Warning ... None` rồi `OK Tint` — suy ra commit-path OK, preview-path None →
đúng 1 node sót wire. KHÔNG đoán mò, khớp bằng chứng.
**Fix:** nối `GET ParamName` vào node `OnPreviewChanged` + node `OnEditCommitted` nhánh hex-commit. Test PASS.
**Bài học:** khi thêm pin vào dispatcher có NHIỀU điểm broadcast (Scalar 3, Color 3), phải audit ĐỦ mọi
node `Call` — sót 1 node = 1 đường im lặng hỏng. Cùng họ bug B2 (dead-end pin) của v1.0.

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
| 18/09/2026 | 1.1 | **S7G7T4:** dispatcher `OnPreviewChanged`/`OnEditCommitted` +`ParamName:Name`. Bug B3: sót wire ParamName ở node preview → live-preview màu hỏng ngầm (bắt qua log `Param 'None'`), fix nối đủ 3 chỗ. Test PASS (màu + hex LIVE + undo value đúng). |
| 24/09/2026 | 1.2 | **U2.4:** `OnEditBegin` +`ParamName:Name`, 2 chỗ Call nối `GET ParamName`. W3 Color PASS. Ghi chú thời điểm `SetColor` trong `Setup` (fix nằm ở C++ picker). |
