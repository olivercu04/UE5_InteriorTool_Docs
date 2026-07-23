# WBP_Toast
**Version:** 1.0 | **Ngày:** 23/07/2026 | **Tạo mới — K1, toast báo lỗi/kết quả dùng chung toàn app**

## Vai trò
Widget toast global — hiện 1 dòng thông báo ngắn ở đáy màn hình, tự ẩn sau N giây. Thay thế
`Print String` tạm ở nhiều chỗ (Delete Folder/Combo, Move Combo fail, Create Folder fail,
SpawnComboByID skip item...) bằng feedback user-facing thật. Truy cập global qua
`Foff_GameInstance.ToastRef` — xem `Widgets/WBP_FurnitureInventory.md` mục `ShowToastMsg` và
`Blueprints/BP_ComboManager.md` mục K1 cho các call site.

## Layout
```
Canvas Panel (root, Not Hit-Testable — Self Only)
└─ Border_Toast (anchor bottom-center, offset Y ≈ -120, padding 12/8, bo góc,
   nền đen alpha 0.75, Visibility=Collapsed mặc định)
   └─ TXT_Message (Text, trắng, Auto Wrap, max width ~480)
```

⚠️ **Lưu ý dropdown UE5.5:** "Hit Test Invisible" trong tài liệu cũ = **"Not Hit-Testable (Self
& All Children)"** trong Editor thật — tên hiển thị đổi giữa các bản UE, ghi chú lại cho các doc
sau tránh nhầm khi tra dropdown Visibility.

## Variables
```
HideTimerHandle : Timer Handle
```

## Custom Event ShowToast(Message : Text, Duration : Float = 2.5)
```
ShowToast(Message, Duration)
▶→ Clear and Invalidate Timer by Handle(HideTimerHandle)
▶→ Set Text(TXT_Message, Message)
▶→ Set Visibility(Border_Toast, "Not Hit-Testable (Self & All Children)")
▶→ Set Timer by Event(HideToast, Time=Duration, Looping=False) ●→ SET HideTimerHandle
```
`Clear and Invalidate Timer by Handle` đầu chuỗi đảm bảo gọi `ShowToast` lần 2 trong lúc toast
cũ còn hiện → hủy timer ẩn cũ, đếm lại từ đầu với message mới (toast mới đè toast cũ, không xếp
hàng).

## Custom Event HideToast()
```
HideToast()
▶→ Set Visibility(Border_Toast, Collapsed)
```

## Global access (K1.2)
- `Foff_GameInstance` thêm var `ToastRef : WBP_Toast (Object Reference)` — xem
  `Planning/Architecture_Overview.md` mục Shared Code.
- `WBP_FOFF_ToolDemo` Event Construct — chèn vào cuối chuỗi Then hiện có, TRƯỚC
  `Get All Actors Of Class(BP_UndoManager) → CaptureSnapshot("Initial")`:
```
Create Widget(WBP_Toast) → Add to Viewport(ZOrder=100)
→ Get Game Instance → Cast to Foff_GameInstance
→ SET Toast Ref (Target = GameInstance từ Cast, KHÔNG phải Self)
→ [nối tiếp vào Get All Actors Of Class(BP_UndoManager) như cũ]
```
- Widget khác muốn dùng toast: qua Function helper riêng (vd `WBP_FurnitureInventory.ShowToastMsg`)
  hoặc gọi thẳng `GameInstance.ToastRef.ShowToast(...)` nếu là Actor (không có đường Function
  Widget) — xem `Blueprints/BP_ComboManager.md` mục K1.

## Test K1 — 5/5 PASS (23/07/2026)
1. `ShowToastMsg` từ nút debug → toast hiện đáy giữa, tự ẩn ~2.5s. ✅
2. Gọi 2 lần cách nhau 1s → toast 2 đè toast 1, đếm lại từ đầu. ✅
3. Toast hiện → click xuyên qua được (Not Hit-Testable). ✅
4. Xóa folder → toast "Đã xóa folder..." thay Print. ✅
5. Spawn combo có RowName bậy → toast skip hiện. ✅

---

## Lịch sử cập nhật

| Ngày | Version | Nội dung |
|------|---------|----------|
| 23/07/2026 | 1.0 | Tạo mới. Widget toast global (K1) — `ShowToast`/`HideToast`, `Foff_GameInstance.ToastRef`. Thay 6 chỗ `Print String` tạm trong `WBP_FurnitureInventory`/`BP_ComboManager` bằng toast thật. Test 5/5 case PASS. Chi tiết: `01_Session_State.md` mục K1, `DEVIATIONS.md`. |
