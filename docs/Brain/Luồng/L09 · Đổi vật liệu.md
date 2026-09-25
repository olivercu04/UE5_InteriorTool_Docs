# L09 · Đổi vật liệu

> **Hành trình:** ← [[L08 · Thay đồ|L08 Thay đồ]] · **L09** · [[L10 · Chỉnh thông số vật liệu|L10 Chỉnh thông số vật liệu]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là bước ⑤ · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** vật liệu gắn theo **vùng (slot)** của từng món. Có 2 cách đổi: **bấm thẻ** (áp cho slot đang chọn, nhiều món cùng loại thì áp hết) và **kéo thẻ thả lên đồ** (slot = vùng dưới điểm thả). Cả 2 đều ghi vào `MaterialSlots` qua dịch vụ C++.

## Người dùng làm gì → thấy gì
| Làm | Thấy | Sổ lịch sử |
|---|---|---|
| Chọn đồ → tab **Material** | Dải slot (quả cầu) của món, lưới vật liệu | — |
| Bấm 1 quả cầu, hoặc click thẳng lên vùng trên mesh | Slot đó sáng lên | — |
| Bấm 1 thẻ vật liệu | Slot đổi ngay; chọn nhiều món cùng loại → cả loạt đổi + Toast "Áp cho N/N đồ" | `ChangeMaterial` (sau 0.5s) |
| Kéo thẻ thả lên 1 vùng của món bất kỳ | Vùng đó đổi, slot đó được chọn trong panel | `ApplyMaterial` |
| Thả trúng tường | Toast "Chỉ áp vật liệu lên đồ nội thất" | — |
| Reset slot / Reset tất cả | Về vật liệu gốc của mesh | `ResetSlot` / `ResetAll` |
| Ctrl+Shift+C / V (hoặc nút Copy / Paste slot) | Chép / dán vật liệu 1 slot sang món khác | `PasteMaterial` (khi dán) |

## Chạy thế nào — bấm thẻ
![[Architecture_Map#5o — Đổi vật liệu bằng cách bấm thẻ (1 hoặc nhiều món)]]
> 🗺️ Bản làn bơi: [[5o - Đổi vật liệu bằng cách bấm thẻ (1 hoặc nhiều món).canvas|canvas 5o]]

## Chạy thế nào — kéo thả lên đồ
![[Architecture_Map#5p — Đổi vật liệu bằng cách kéo thẻ thả lên đồ]]
> 🗺️ Bản làn bơi: [[5p - Đổi vật liệu bằng cách kéo thẻ thả lên đồ.canvas|canvas 5p]]

## Hình dung
Mỗi món như **tủ có nhiều ngăn** (slot): mặt bàn, chân bàn… `MaterialSlots` là **phiếu ghi ngăn nào đang lót vật liệu gì** (+ thông số chỉnh tay). Dịch vụ C++ `MaterialSlotService` là người thợ duy nhất được thay lót — ghi phiếu và đổi vật liệu cùng lúc, nên Undo / Lưu / Copy chỉ cần mang theo phiếu.

## Dễ hiểu sai
- **Bấm thẻ nhắm vào `TargetFurnitureActor` (món chính)**, còn selection có thể nhiều món → áp hết chỉ khi **mọi món cùng RowName** ("Hướng B"); khác loại → chỉ món chính + Toast cảnh báo.
- **Kéo-thả không cần chọn trước** — slot và món lấy từ điểm thả (`TraceSlotUnderCursor`), việc đổi do **chính món đó** làm (`ApplyMaterialByRowName`, luật L11 — không để manager làm hộ nhiều món async).
- **Bấm liên tục chỉ ghi sổ 1 lần** — timer 0.5s `CaptureMaterialSnapshot` (debounce P5).
- **Tab Material là cổng của chế độ chỉnh vật liệu**: rời tab thì dải slot ẩn và click đồ khác không đổi món đang chỉnh.
- Sau khi đổi, panel phải **chọn lại đúng slot + tô sáng + làm mới thông số** — thứ tự `RefreshSlotSwatches` → `HighlightSwatchByIndex` (rebuild xoá highlight nếu làm ngược).
- Combo cũ lưu vật liệu kiểu `MaterialOverrides` (RowName) — combo mới lưu `MaterialSlots`; khi đặt combo cũ đi đường legacy `F_ApplyMaterialOverrides`.

## Đường ngược (6A)
Ctrl+Z (`ChangeMaterial` / `ApplyMaterial` là Snapshot → dựng lại cảnh, vật liệu về sau vài frame — [[L13 · Hoàn tác và làm lại|L13]]) · nút Reset slot / Reset tất cả.

## Còn mở
- `Button_ChangeMaterial → ApplyMaterial` và thân `ApplyMaterialByRowName` chưa K2.
- Undo đổi vật liệu làm mất slot đang chọn + Inspector về trống — đóng ở U3 (`Bug-ParamUndo-SlotContextLost`, [[Open_Bugs]]).

## Nhảy tới code
| Hàm | Doc |
|---|---|
| `ApplyMaterial` · `LoadAndApplyMaterial` (✓K2 05/09) · `RefreshSlotSwatches` · `HighlightSwatchByIndex` · `NotifyViewportSlotClick` · `BTN_ResetSlot` / `BTN_ResetAll` | [[WBP_FurnitureInventory]] |
| `Button_ChangeMaterial` · `OnDragDetected` · `BP_DragDropOperation_Material` | [[WBP_MaterialCard]] |
| `On Drop` nhánh Material (✓K2 11/09) | [[WBP_DragOverlay_FurnitureCard]] |
| `ApplyMaterialByRowName` · `RestoreMyMaterialSlots` | [[BP_FurnitureActor]] |
| `ApplyLoadedMaterialToSlot` · `TraceSlotUnderCursor` · `ResetSlotToAssetDefault` | [[MaterialSlotService_Reference]] |
| Multi-apply Hướng B · Copy / paste vật liệu | [[ChangeMaterial]] · [[Material_CopyPaste]] |
