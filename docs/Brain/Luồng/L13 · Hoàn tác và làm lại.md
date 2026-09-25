# L13 · Hoàn tác và làm lại

> **Hành trình:** ← [[L12 · Lưu và mở cảnh|L12 Lưu và mở cảnh]] · **L13** · [[Bản đồ não|hết hành trình — về Bản đồ não]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là "Bất cứ lúc nào" · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** sổ lịch sử là **1 mảng entry + 1 con trỏ**. Có 2 loại entry: **Snapshot** (ảnh cả cảnh — Undo = dựng lại cả cảnh từ ảnh trước) và **ParamCommand** (1 thông số vật liệu — Undo = đảo đúng thông số đó, không dựng lại).

## Người dùng làm gì → thấy gì
| Làm | Thấy |
|---|---|
| Ctrl+Z | Thao tác gần nhất bị hoàn tác; lựa chọn + gizmo về như trước |
| Ctrl+Shift+Z | Làm lại |
| Làm thao tác mới sau khi Undo | Nhánh Redo bị cắt |
| Undo quá 50 bước | Entry cũ nhất đã bị bỏ |

## Hình dung
```
[0 Initial] [1 Spawn] [2 Select] [3 Move] [4 Chỉnh Roughness]      ← CurrentIndex = 4
Ctrl+Z  → đảo entry 4 (ParamCommand) → CurrentIndex = 3
Ctrl+Z  → đảo entry 3 (Move = Snapshot) → khôi phục ẢNH của entry 2 → CurrentIndex = 2
Ctrl+Shift+Z → CurrentIndex = 3 → áp lại entry 3 (ảnh của chính nó)
Thao tác MỚI khi CurrentIndex = 2 → entry 3, 4 bị CẮT → thao tác mới thành entry 3
```
| Loại | Chứa gì | Undo làm gì | Sinh lại cảnh? |
|---|---|---|---|
| **Snapshot** (Move, Select, Spawn, Group, Combo, Replace, vật liệu…) | ảnh full cảnh | khôi phục ảnh của entry **N−1** | CÓ |
| **ParamCommand** (chỉnh thông số, [[L10 · Chỉnh thông số vật liệu|L10]]) | Before / After 1 thông số + ảnh full để dành | áp Before của **chính nó** | KHÔNG |

Quy tắc 1 dòng: **Undo Snapshot N → dùng ảnh của N−1. Undo Command → dùng Before của chính nó.**

## Chạy thế nào — tổng quan
![[Architecture_Map#5c — Undo / Redo — tổng quan (dispatch theo EntryKind)]]
> 🗺️ Bản làn bơi: [[5c - Undo - Redo — tổng quan (dispatch theo EntryKind).canvas|canvas 5c]]

## Chạy thế nào — ghi sổ (mỗi thao tác → 1 entry)
![[Architecture_Map#5d — Ghi sổ lịch sử — 1 thao tác thành 1 entry (CaptureSnapshot)]]
> 🗺️ Bản làn bơi: [[5d - Ghi sổ lịch sử — 1 thao tác thành 1 entry (CaptureSnapshot).canvas|canvas 5d]]

## Chạy thế nào — Undo 1 entry Snapshot
![[Architecture_Map#5e — Undo 1 entry Snapshot — RestoreSnapshot (destroy + spawn lại)]]
> 🗺️ Bản làn bơi: [[5e - Undo 1 entry Snapshot — RestoreSnapshot (destroy + spawn lại).canvas|canvas 5e]]

## Dễ hiểu sai
- **Undo Snapshot không "lùi 1 bước thao tác"** — nó **dựng lại cả cảnh** từ ảnh của entry trước. Mọi actor là object MỚI → con trỏ cũ chết → cần `PersistentID` ([[EntityIdLibrary_Reference]]).
- **Sau Undo, trạng thái về theo 3 nhịp:** ngay (sinh lại, chọn, gizmo) → +0.1s (kho làm mới qua Timer) → vài frame sau (vật liệu từng slot, async). Nhìn sớm quá tưởng lỗi.
- **`SelectActors` bị gọi 2 lần** trong `RestoreSnapshot` (bước 5 và 6b) — nguồn gốc bug B-gizmo (đã sửa 24/09 bằng Deactivate trước Activate).
- **Undo Snapshot làm mất slot đang chọn + Inspector về trống**; Undo ParamCommand thì không — đóng ở U3 (`Bug-ParamUndo-SlotContextLost`).
- **Ctrl+Shift+Z cũng thỏa điều kiện Ctrl+Z** — `IA_FurnitureUndo` kiểm Shift để nhường Redo.
- Nguồn ghi sổ: InputManager (Select / Deselect / BoxSelect / Group / Paste / Duplicate / Delete / Nudge), Gizmo (Move / Rotate / Scale), lớp kéo-thả (Spawn), thẻ đồ (Replace), món đồ (ApplyMaterial), kho (ChangeMaterial, ResetSlot / ResetAll, PasteMaterial), ComboManager (SpawnCombo / ReplaceCombo), phiên chỉnh thông số (ParamCommand).

## Đường ngược (6A)
Chính là luồng này. Redo đảo lại Undo; thao tác mới cắt nhánh Redo.

## Còn mở
- `RefreshButtonState` được UndoManager gọi nhưng doc không ghi lấy tham chiếu MeshControls từ đâu (`?`).
- Thân `RestoreSnapshot` Step 1/2/5/5b/6/6b/7 chưa K2 riêng · Step 4 `SET MaterialSlots` lệch changelog.
- K2 đáng xin nhất cho cả bộ não: đuôi `AppendEntry` (Broadcast) + chỗ kho bind `OnHistoryChanged` — xem [[Kiểm tra bản đồ]].

## Nhảy tới code
| Hàm | Doc |
|---|---|
| `UndoLastAction` · `RedoLastAction` · `CaptureSnapshot` · `BuildSceneSnapshotBase` · `AppendEntry` · `RestoreSnapshot` · `RestoreCurrentSnapshot` · `ApplyParamCommand` · `JumpToHistoryIndex` | [[BP_UndoManager]] |
| `IA_FurnitureUndo` · `IA_FurnitureRedo` | [[BP_FoffPlayerController]] |
| `OnMouseReleased` (ghi Move / Rotate / Scale) | [[BP_GizmoController]] |
| `SpawnFurnitureCopy` · `SelectActors` · `DeselectAll` | [[BP_FurnitureInputManager]] |
| `LoadMeshAsync` · `RestoreMyMaterialSlots` | [[BP_FurnitureActor]] |
| `OnSceneRestored` · `ApplyRestoredActor` · `RefreshParamPanel` | [[WBP_FurnitureInventory]] |
| Kiến trúc 6 trụ A–F | [[18-09-2026_UndoArchitecture_Foundation_v1]] · [[Tư duy 2 · Kiến trúc và nguyên tắc code|Tư duy 2]] mục 6 |
