# Luồng U2 — Chỉnh thông số vật liệu và Undo

> Viết tay 24/09/2026 (U2 ĐÓNG). Kể theo **thời gian**: từ lúc nhấn slider tới lúc Ctrl+Z. As-built chi tiết: [[BP_UndoManager]] v1.22, [[WBP_FurnitureInventory]] v3.33.
> ← [[Bản đồ não]] · Luồng hệ thống liên quan: [[Luồng 3e - Vật liệu Material]], [[Luồng 3d - Save Undo khởi động]]

## Sơ đồ event / function

> Nguồn DUY NHẤT: [[Architecture_Map]] Phần 5 (nhúng bên dưới — sửa ở đó, note này tự cập nhật).
> Mũi tên **liền** = đã ✓K2 · **đứt** = theo doc (chưa K2). Đọc từ trên xuống theo thời gian.

![[Architecture_Map#5b — Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session)]]
> 🗺️ Bản kéo/zoom được: [[5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas|Canvas 5b]]

![[Architecture_Map#5c — Undo / Redo — tổng quan (dispatch theo EntryKind)]]
> 🗺️ Bản kéo/zoom được: [[5c - Undo - Redo — tổng quan (dispatch theo EntryKind).canvas|Canvas 5c]]

> Chi tiết Undo/Redo đầy đủ (ghi sổ, RestoreSnapshot): [[Luồng - Undo Redo]]

### Nhảy tới code (mở doc → `Ctrl+F` tên hàm, hoặc panel **Outline**)
| Hàm | Doc |
|---|---|
| `BeginInteractiveEdit` · `CommitInteractiveEdit` · `CancelInteractiveEdit` · `ApplyParamCommand` · `BuildSceneSnapshotBase` · `AppendEntry` · `UndoLastAction` · `RedoLastAction` · `RestoreSnapshot` · `JumpToHistoryIndex` | [[BP_UndoManager]] |
| `Handle_ScalarBegin` (mục "2 handler Begin") · `Handle_ScalarPreview`/`Commit` (mục "4 delegate handler") · `RefreshParamPanel` · `Handle_HistoryChanged` (mục "Event Construct — APPEND") · 4 Cancel seam | [[WBP_FurnitureInventory]] |
| `OnEditBegin` / `OnPreviewChanged` / `OnEditCommitted` (mục "Event flow") | [[WBP_ParamScalarRow]] · [[WBP_ParamColorRow]] |
| `ResolveByPersistentId` | [[BP_FurnitureSceneManager]] |
| `GetSlot*Param` · `SetSlot*Param` | [[MaterialSlotService_Reference]] |
| phím Undo/Redo | [[BP_FoffPlayerController]] |

## Kể bằng lời (chi tiết từng bước)

## 0. Mở panel
[[WBP_FurnitureInventory]] `RefreshParamPanel` → đọc giá trị THẬT từng thông số qua [[MaterialSlotService_Reference]] `GetSlotScalarParam`/`GetSlotVectorParam` (MID hoặc MI gốc) → tạo [[WBP_ParamScalarRow]] / [[WBP_ParamColorRow]] (row màu nhúng [[InteriorColorPicker]]) → bind 3 dispatcher: `OnEditBegin` · `OnPreviewChanged` · `OnEditCommitted`.

## 1. Nhấn chuột — MỞ phiên
```
Row.OnEditBegin(ParamName) → Inventory.Handle_ScalarBegin → UndoManager.BeginInteractiveEdit
   ├ bIsRestoring? → thôi
   ├ đang có phiên cũ? → CommitInteractiveEdit (chốt phiên cũ trước — 1 phiên 1 lúc)
   ├ SceneManager.ResolveByPersistentId(ID) → tìm ghế
   └ đọc Before từ MESH (không từ slider) → cất vào Sess_Cmd.BeforeScalar → Sess_Active = True
```
Ai: [[BP_UndoManager]] · [[BP_FurnitureSceneManager]] · [[MaterialSlotService_Reference]]

## 2. Kéo — XEM TRƯỚC (không ghi sổ)
`Row.OnPreviewChanged` → `Handle_ScalarPreview` → `SetSlotScalarParam` áp LIVE lên mesh. Cả trăm lần/giây, **0 entry** history.

## 3. Thả chuột — CHỐT
```
Row.OnEditCommitted → Handle_ScalarCommit → SetSlotScalarParam (giá trị cuối) → UndoManager.CommitInteractiveEdit
   ├ đọc After từ mesh
   ├ Before == After? (IsNoOpCommand) → không ghi gì
   └ khác → BuildSceneSnapshotBase (chụp full scene) + gắn EntryKind=ParamCommand, ParamCmd
          → AppendEntry → Broadcast OnHistoryChanged → Inventory refresh panel
```
Entry = **phiếu sửa 1 dòng** (Before/After) **kèm ảnh cả kệ** (full scene) để dành cho entry Snapshot đứng sau nó.

## 4. Hủy giữa chừng — ROLLBACK (không ghi sổ)
Đổi ghế / đổi slot / đóng Inspector / Ctrl+Z lúc đang kéo → `CancelInteractiveEdit` → `ApplyParamCommand(Before)` → mesh về giá trị cũ, **0 entry**.
4 chỗ gọi Cancel: `OnMeshSelected` · `CloseMaterialInspector` · `NotifyViewportSlotClick` · `OnSlotSwatchClicked`.

## 5. Ctrl+Z / Ctrl+Shift+Z
```
UndoLastAction → CancelInteractiveEdit (hủy phiên đang dở nếu có)
   → entry hiện tại là gì?
        ParamCommand → ApplyParamCommand(Before) — TÌM ghế theo ID, đổi đúng 1 thông số, KHÔNG respawn
        Snapshot     → RestoreSnapshot(entry TRƯỚC) — destroy + spawn lại toàn scene
   → Broadcast OnHistoryChanged
```
Quy tắc 1 dòng: **Undo snapshot N → dùng ảnh của N−1. Undo command → dùng Before của chính nó.**
Nhảy nhiều bước: `JumpToHistoryIndex(K)` = gọi Undo/Redo lặp tới K (test: console `ke * JumpToHistoryIndex K`).

## Vì sao thiết kế thế (1 dòng mỗi ý)
- Tìm ghế bằng **PersistentID**, không bằng con trỏ: undo snapshot respawn → con trỏ cũ chết, ID thì sống ([[EntityIdLibrary_Reference]]).
- Before đọc từ **mesh**, không từ slider: slider là bản sao hiển thị, có thể bị kẹp Min/Max hoặc sai.
- Command vẫn kèm **ảnh full**: để undo entry Snapshot đứng sau nó có ảnh mà khôi phục (hướng B, gỡ sau ở trụ E).

## Còn treo
- Undo **Move** (snapshot) vẫn mất slot + Inspector → **U3** đóng. [[Open_Bugs]] `Bug-ParamUndo-SlotContextLost`.
- Chống "ghi mồ côi" đang dựa vào việc panel rebuild sau Undo — [[DEVIATIONS]] D-11.
