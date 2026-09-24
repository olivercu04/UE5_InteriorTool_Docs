# WBP_ParamScalarRow
**Version:** 1.2 | **Cập nhật:** 24/09/2026 16:10 — **U2.4:** dispatcher `OnEditBegin` +input `ParamName:Name` (trước: 0 input). Lý do y hệt v1.1: 1 handler `Handle_ScalarBegin` chung cho mọi row → payload phải mang param identity; bản 0-input khiến `Bind OnEditBegin` KHÔNG chọn được handler có `ParamName` (sai signature). 2 chỗ `Call OnEditBegin` nối `GET ParamName`. `OnEditBegin` trước đó chưa ai bind → thêm input không phá gì. PIE PASS (1 dòng BEGIN/lần kéo).
**Version:** 1.1 | **Cập nhật:** 18/09/2026 — **S7G7T4:** dispatcher `OnPreviewChanged`/`OnEditCommitted` thêm input `ParamName:Name` (đứng trước `Value`). Lý do: T4 handler dùng chung 1 `Handle_ScalarPreview`/`Handle_ScalarCommit` cho MỌI row → phải biết Value thuộc param nào; row đã lưu sẵn `ParamName` (từ `Setup`) nên broadcast kèm. 3 chỗ `Call` nối thêm `GET ParamName`. Test PASS (roughness live + undo/redo value đúng). Đây là bug loại Q10 (producer contract không phủ consumer mới) — xem `Rules/AI_Implementation_Rules.md` Q10.
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
OnEditBegin(ParamName:Name) · OnPreviewChanged(ParamName:Name, Value:Float) · OnEditCommitted(ParamName:Name, Value:Float)
```
> **[v1.1 18/09]** `ParamName` là input MỚI (trước v1.0 chỉ có `Value`). Bắt buộc vì 1 handler T4 phục vụ mọi row Scalar — không có `ParamName` trong payload thì handler mù, không biết Value thuộc param nào (lộ khi material ≥2 param Scalar ở G8).

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
Slider_Value.OnMouseCaptureBegin ▶→ Call OnEditBegin(GET ParamName)     ← v1.2: +GET ParamName

Slider_Value.OnValueChanged(Value:Float)
▶→ SET RealVal = MapRangeClamped(Value, 0, 1, MinValue, MaxValue)
▶→ SpinBox_Value.SetValue(RealVal)
▶→ Call OnPreviewChanged(GET ParamName, RealVal)    ← v1.1: +GET ParamName (xem Bug B2)

Slider_Value.OnMouseCaptureEnd
▶→ SET RealVal = MapRangeClamped(Slider_Value.GetValue(), 0, 1, MinValue, MaxValue)
▶→ Call OnEditCommitted(GET ParamName, RealVal)     ← v1.1: +GET ParamName

SpinBox_Value.OnValueCommitted(NewValue, CommitMethod)
▶→ SET ClampedVal = Clamp(NewValue, MinValue, MaxValue)
▶→ Slider_Value.SetValue( MapRangeClamped(ClampedVal, MinValue, MaxValue, 0, 1) )
▶→ Call OnEditBegin(GET ParamName) ▶→ Call OnPreviewChanged(GET ParamName, ClampedVal) ▶→ Call OnEditCommitted(GET ParamName, ClampedVal)   ← v1.1: cả 2 +GET ParamName
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
| 18/09/2026 | 1.1 | **S7G7T4:** dispatcher `OnPreviewChanged`/`OnEditCommitted` thêm `ParamName:Name` (input đầu). 3 chỗ `Call` nối `GET ParamName`. Cần thiết vì T4 dùng 1 handler chung cho mọi row — payload phải mang param identity. Test PASS. Bug loại Q10 (contract producer không phủ consumer T4). |
| 24/09/2026 | 1.2 | **U2.4:** `OnEditBegin` +`ParamName:Name`; 2 chỗ `Call OnEditBegin` nối `GET ParamName`. Cùng loại bug Q10 như v1.1 (lần này lộ khi U2.4 lần đầu bind `OnEditBegin`). PIE PASS. |
