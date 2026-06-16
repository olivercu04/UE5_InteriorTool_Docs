# BP_FoffPlayerController — Furniture Tool Integration
**Cập nhật:** 25/04/2026 | Project: project_22042026 (UE5.5.4)
 
---
 
## Vai trò
 
`BP_FoffPlayerController` là Player Controller chính của project tổng. Furniture tool tận dụng controller này để:
- Quản lý Add/Remove `LM_FurnitureInput` Mapping Context
- Bind Enhanced Input cho Undo/Redo
---
 
## Custom Events đã thêm
 
### AddFurnitureInput
 
Gọi khi `WBP_FurnitureInventory` được mở. Swap input context:
 
```
Enhanced Input Local Player Subsystem → Is Valid 
→ Add Mapping Context (LM_FurnitureInput, Priority=3)
→ Remove Mapping Context (LM_InputMapping)
```
 
### RemoveFurnitureInput
 
Gọi khi `WBP_FurnitureInventory` đóng hoàn toàn (không phải minimize). Khôi phục input context của project tổng:
 
```
Enhanced Input Local Player Subsystem → Is Valid 
→ Remove Mapping Context (LM_FurnitureInput)
→ Add Mapping Context (LM_InputMapping, Priority=2)
```
 
---
 
## Enhanced Input Actions đã bind
 
### IA_FurnitureUndo (Started)
 
```
Branch (Is Input Key Down Left Shift OR Right Shift)?
  False → Get All Actors Of Class(BP_UndoManager) → Get(0) → UndoLastAction
  True  → không làm gì (đang Redo)
```
 
**Lý do dùng `Started`:** chỉ fire 1 lần khi action bắt đầu, không fire mỗi frame như Triggered → tránh Undo liên tục.
 
**Lý do check Shift:** khi nhấn Ctrl+Shift+Z, cả `IA_FurnitureUndo` và `IA_FurnitureRedo` đều thỏa điều kiện Chord Action (Ctrl đang Down). Check Shift để loại trường hợp này — nếu Shift đang giữ → đang là Redo, bỏ qua.
 
### IA_FurnitureRedo (Started)
 
```
Get All Actors Of Class(BP_UndoManager) → Get(0) → RedoLastAction
```
 
Không cần check vì Chord Action `IA_Ctrl + IA_Shift + Pressed` đã đảm bảo chỉ fire khi đúng tổ hợp Ctrl+Shift+Z.
 
---
 
## Caller Diagram
 
```
WBP_FOFF_ToolDemo (BTN_FurnitureInventory OnClicked)
  ├─ Mở:  → AddFurnitureInput
  └─ Đóng: → RemoveFurnitureInput
 
WBP_FurnitureInventory (BTN_Close OnClicked)
  └─ Đóng: → RemoveFurnitureInput
 
Enhanced Input (khi LM_FurnitureInput active)
  ├─ Ctrl+Z       → IA_FurnitureUndo (Started)  → UndoLastAction
  └─ Ctrl+Shift+Z → IA_FurnitureRedo (Started)  → RedoLastAction
```
 
---
 
## Lưu ý cho Developer khác
 
- **2 Custom Event** trên là interface giữa furniture tool và project tổng. Không xóa, không đổi tên.
- **Approach swap context** (Add LM_Furniture + Remove LM_InputMapping) hiện đang tắt camera control khi inventory mở. Đây là giải pháp prototype, cần cân nhắc lại cho production — có thể dùng priority + Consume Input thay thế nhưng cần test kỹ với các phím tắt khác.
- Khi project tổng cập nhật `LM_InputMapping`, cần kiểm tra lại 2 Custom Event `AddFurnitureInput`/`RemoveFurnitureInput` xem reference còn đúng không.
---
 
## Lỗi đã gặp và cách fix
 
| Lỗi | Nguyên nhân | Cách fix |
|-----|-------------|----------|
| Z đơn vẫn trigger IA_FOV khi inventory mở | LM_FurnitureInput chưa consume phím Z | Thêm 2 mapping Z cho `IA_FurnitureUndo` và `IA_FurnitureRedo` (1 với trigger, 1 không trigger để consume) |
| Ctrl+Z chạy liên tục mỗi frame khi giữ | Dùng pin `Triggered` | Đổi sang pin `Started` |
| Ctrl+Shift+Z trigger cả Undo và Redo | Chord Action `IA_Ctrl` thỏa cho cả 2 | Trong `IA_FurnitureUndo` Started, check Shift Down → bỏ qua |
| Was Input Key Just Pressed(Z) luôn = false | Mapping Z đơn fire trước, consume Z | Bỏ Was Input Key Just Pressed, dùng Started |
 