# L10 · Chỉnh thông số vật liệu

> **Hành trình:** ← [[L09 · Đổi vật liệu|L09 Đổi vật liệu]] · **L10** · [[L11 · Combo|L11 Combo]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là bước ⑤ · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** kéo 1 thanh trượt / vòng màu trong bảng Material = **1 phiên chỉnh**: nhấn mở phiên (đọc giá trị Trước), kéo chỉ xem trước (không ghi sổ), thả tay chốt **đúng 1 entry** kiểu ParamCommand. Huỷ giữa chừng → về giá trị Trước, 0 entry.

## Người dùng làm gì → thấy gì
| Làm | Thấy | Sổ lịch sử |
|---|---|---|
| Bấm **MATERIAL EDIT** (đã chọn slot) | Bảng thông số của slot: độ nhám, màu… | — |
| Nhấn thanh trượt | — | mở phiên (chưa ghi) |
| Kéo | Mesh đổi theo tay, trăm lần / giây | — |
| Thả | Giá trị đứng lại | 1 entry `ParamCommand` |
| Đổi món / đổi slot / đóng bảng / Ctrl+Z khi đang kéo | Giá trị về như trước khi nhấn | 0 entry |
| Ctrl+Z sau khi thả | Đúng 1 thông số quay lại, **không sinh lại cảnh** | lùi 1 |

## Chạy thế nào
![[Architecture_Map#5b — Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session)]]
> 🗺️ Bản làn bơi: [[5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas|canvas 5b]]

## Kể bằng lời
1. **Mở bảng:** `RefreshParamPanel` đọc giá trị THẬT từng thông số qua `GetSlotScalarParam` / `GetSlotVectorParam` → tạo row → bind 3 dispatcher `OnEditBegin` · `OnPreviewChanged` · `OnEditCommitted`.
2. **Nhấn — mở phiên:** `Handle_ScalarBegin` → `BeginInteractiveEdit`: đang Restore thì thôi · phiên cũ còn thì chốt trước · tìm món bằng `ResolveByPersistentId` · đọc **Before từ mesh** (không từ slider).
3. **Kéo — xem trước:** `OnPreviewChanged` → `SetSlotScalarParam` áp live, 0 entry.
4. **Thả — chốt:** `CommitInteractiveEdit` đọc After · Before = After → không ghi · khác → `BuildSceneSnapshotBase` + gắn `ParamCmd` → `AppendEntry` → `OnHistoryChanged` → bảng làm mới.
5. **Huỷ:** `CancelInteractiveEdit` → `ApplyParamCommand(Before)`. 4 chỗ gọi: `OnMeshSelected` · `CloseMaterialInspector` · `NotifyViewportSlotClick` · `OnSlotSwatchClicked`.

## Hình dung
Entry ParamCommand = **phiếu sửa 1 dòng** (Before / After của 1 thông số) **kèm ảnh chụp cả kệ** (full scene) để dành cho entry Snapshot đứng sau nó.

## Dễ hiểu sai
- **Tìm món bằng `PersistentID`, không bằng con trỏ** — Undo Snapshot sinh lại cả cảnh, con trỏ cũ chết, ID thì sống.
- **Before đọc từ mesh**, không từ slider (slider có thể bị kẹp Min / Max).
- **Undo ParamCommand không respawn** → giữ slot + bảng; Undo Snapshot thì mất (U3).
- Row màu (`WBP_ParamColorRow` + `InteriorColorPicker`) đối xứng row số, dùng `Get/SetSlotVectorParam`.

## Đường ngược (6A)
Huỷ phiên (0 entry) · Ctrl+Z = áp Before của chính entry · Ctrl+Shift+Z = áp After · nút Reset thông số.

## Còn mở
- 2 handler Begin / Commit phía Inventory, `CancelInteractiveEdit`, broadcast `OnHistoryChanged` — PIE PASS, chưa K2.
- Chống "ghi mồ côi" dựa vào việc bảng dựng lại sau Undo — [[DEVIATIONS]] D-11.

## Nhảy tới code
| Hàm | Doc |
|---|---|
| `BeginInteractiveEdit` · `CommitInteractiveEdit` · `CancelInteractiveEdit` · `ApplyParamCommand` · `AppendEntry` | [[BP_UndoManager]] |
| `RefreshParamPanel` · 2 handler Begin · 4 delegate handler · `Handle_ResetParamsRequested` | [[WBP_FurnitureInventory]] |
| `OnEditBegin` / `OnPreviewChanged` / `OnEditCommitted` | [[WBP_ParamScalarRow]] · [[WBP_ParamColorRow]] |
| `ResolveByPersistentId` | [[BP_FurnitureSceneManager]] |
| `GetSlot*Param` · `SetSlot*Param` | [[MaterialSlotService_Reference]] |
| Khung bảng | [[WBP_MaterialInspector]] · [[WBP_MaterialParamPanel]] · [[InteriorColorPicker]] |
