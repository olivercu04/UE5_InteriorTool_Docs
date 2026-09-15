# WBP_ParamScalarRow
**Version:** 1.0 | **Ngày:** 15/09/2026 | **Tạo mới — S7G7T2, đóng PASS 4/4**

## Vai trò
Row UMG cho 1 param Scalar trong Material Param Panel (S7G7T3 sẽ dựng danh sách row từ
`GetControlsForMaterial`, xem `Data/MaterialSlotService_Reference.md`). Chuẩn hóa vòng đời edit về
đúng 3 dispatcher (`OnEditBegin`/`OnPreviewChanged`/`OnEditCommitted`) để caller (panel, T3/T4)
không cần biết nguồn edit là Slider hay SpinBox.

## Hierarchy
```
Border_RowRoot
└── (layout tự do) → TextBlock_Label · Slider_Value · SpinBox_Value
```
`Slider_Value`: Min Value = 0, Max Value = 1 (CỐ ĐỊNH — range thật nằm ở `MinValue`/`MaxValue`
của widget, KHÔNG đổi range native của Slider).

## Variables + Event Dispatchers
```
ParamName : Name · MinValue : Float · MaxValue : Float
OnEditBegin() · OnPreviewChanged(Value:Float) · OnEditCommitted(Value:Float)
```

## Function `Setup(InLabel:Text, InParamName:Name, InMin:Float, InMax:Float, InInitialValue:Float)`
```
SET ParamName = InParamName
SET MinValue = InMin
SET MaxValue = InMax
TextBlock_Label.SetText(InLabel)
Slider_Value.SetValue( MapRangeClamped(InInitialValue, MinValue, MaxValue, 0, 1) )
SpinBox_Value.SetValue(InInitialValue)          ← xem Bug B1
```

## Event flow (xác nhận qua K2Node export thật — `Slider_Value.OnValueChanged`, PASS test)
```
Slider_Value.OnMouseCaptureBegin ▶→ Call OnEditBegin

Slider_Value.OnValueChanged(Value:Float)
▶→ SET RealVal = MapRangeClamped(Value, 0, 1, MinValue, MaxValue)
▶→ SpinBox_Value.SetValue(RealVal)
▶→ Call OnPreviewChanged(RealVal)               ← xem Bug B2

Slider_Value.OnMouseCaptureEnd
▶→ SET RealVal = MapRangeClamped(Slider_Value.GetValue(), 0, 1, MinValue, MaxValue)
▶→ Call OnEditCommitted(RealVal)

SpinBox_Value.OnValueCommitted(NewValue, CommitMethod)
▶→ SET ClampedVal = Clamp(NewValue, MinValue, MaxValue)
▶→ Slider_Value.SetValue( MapRangeClamped(ClampedVal, MinValue, MaxValue, 0, 1) )
▶→ Call OnEditBegin ▶→ Call OnPreviewChanged(ClampedVal) ▶→ Call OnEditCommitted(ClampedVal)
```
> `OnMouseCaptureBegin/End` + `SpinBox.OnValueCommitted` xác nhận đúng qua **test PASS** (không có
> K2Node export riêng gửi cho phần này) — hành vi đã kiểm chứng, không phải suy đoán.

## 2 bug gặp trong phiên (đã fix, verify bằng test)

**B1 — `SpinBox_Value` hiện `0` thay vì giá trị khởi tạo lúc spawn.**
Nguyên nhân: quên nối pin `InInitialValue` vào `SpinBox_Value.SetValue(...)` trong `Setup` — node
tồn tại nhưng input để trống. Fix: nối đúng pin. Bài học: thiếu-wire không luôn báo lỗi compile
(Set với default value trống vẫn qua được với 1 số kiểu), phải verify bằng mắt lúc spawn.

**B2 — `OnPreviewChanged` không bắn dù kéo slider chạy được (SpinBox vẫn đồng bộ theo).**
Nguyên nhân: pin `then` (exec output) của `SpinBox_Value.SetValue(...)` bên trong
`Slider_Value.OnValueChanged` bị bỏ trống (`LinkedTo=()`) — dead-end thật, không phải lỗi remap.
Phát hiện qua đọc K2Node export (`then` rỗng nhìn thấy rõ trong text export, khó thấy trên canvas
nếu không zoom kỹ). Fix: nối `Call OnPreviewChanged` vào đúng chỗ trống đó.

## Test — 4/4 PASS (15/09/2026)
1. Remap non-trivial (Min=0,Max=10, cố ý khác [0,1]) — Preview chạy đúng dải, Committed khớp.
2. SpinBox gõ tay → Begin+Preview+Committed đồng thời, slider tự đồng bộ.
3. Kéo slider xong → SpinBox hiển thị đúng theo, log Preview liên tục đúng dải.
4. Spawn với `InInitialValue` giữa dải → cả Slider lẫn SpinBox hiện đúng ngay lúc `Setup`.

Q9: MIỄN (standalone, không đụng `SelectedActors`).

---

## Lịch sử cập nhật

| Ngày | Version | Nội dung |
|------|---------|----------|
| 15/09/2026 | 1.0 | Tạo mới — S7G7T2. `Setup` + event flow (Slider/SpinBox → 3 dispatcher chuẩn hóa). 2 bug phát hiện+fix trong phiên (B1 thiếu wire InInitialValue, B2 dead-end pin OnPreviewChanged). Test 4/4 PASS. Nguồn: `DELTA — S7G7T2 AS-BUILT` (Opus+Sonnet, 15/09/2026). |
