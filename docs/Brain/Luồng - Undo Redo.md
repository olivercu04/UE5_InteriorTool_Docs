# Luồng — Undo / Redo (Ctrl+Z · Ctrl+Shift+Z)

> Viết 24/09/2026. Sơ đồ NHÚNG từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.
> ← [[Bản đồ não]] · Liên quan: [[Luồng U2 - Chỉnh thông số vật liệu và Undo]] · [[Luồng 3d - Save Undo khởi động]]

## Hình dung trước khi đọc sơ đồ
Sổ lịch sử = **mảng `SnapshotHistory`** + **con trỏ `CurrentIndex`** (luôn trỏ entry "hiện tại").
```
[0 Initial] [1 Spawn] [2 Select] [3 Move] [4 Chỉnh Roughness]      ← CurrentIndex = 4
Ctrl+Z  → đảo entry 4 → CurrentIndex = 3
Ctrl+Z  → đảo entry 3 (Move = Snapshot) → khôi phục ẢNH của entry 2 → CurrentIndex = 2
Ctrl+Shift+Z → CurrentIndex = 3 → áp lại entry 3 (ảnh của chính nó)
Làm thao tác MỚI khi CurrentIndex = 2 → entry 3, 4 bị CẮT (mất nhánh Redo) → thao tác mới thành entry 3
```
2 loại entry:
| Loại | Chứa gì | Undo làm gì | Có respawn? |
|---|---|---|---|
| **Snapshot** (Move, Select, Group, Combo, Reset…) | ảnh full scene | khôi phục ảnh của entry **N−1** | CÓ — xoá hết, spawn lại |
| **ParamCommand** (chỉnh thông số vật liệu, U2) | Before/After 1 thông số + ảnh full (để dành) | áp Before của **chính nó** | KHÔNG |

## 1. Tổng quan — bấm phím tới lúc xong
![[Architecture_Map#5c — Undo / Redo — tổng quan (dispatch theo EntryKind)]]
> 🗺️ Bản kéo/zoom được: [[5c - Undo - Redo — tổng quan (dispatch theo EntryKind).canvas|Canvas 5c]]

## 2. Sổ được ghi thế nào (mỗi thao tác → 1 entry)
![[Architecture_Map#5d — Ghi sổ lịch sử — 1 thao tác thành 1 entry (CaptureSnapshot)]]
> 🗺️ Bản kéo/zoom được: [[5d - Ghi sổ lịch sử — 1 thao tác thành 1 entry (CaptureSnapshot).canvas|Canvas 5d]]

## 3. Undo 1 entry Snapshot — bên trong RestoreSnapshot
![[Architecture_Map#5e — Undo 1 entry Snapshot — RestoreSnapshot (destroy + spawn lại)]]
> 🗺️ Bản kéo/zoom được: [[5e - Undo 1 entry Snapshot — RestoreSnapshot (destroy + spawn lại).canvas|Canvas 5e]]

## Những điều dễ hiểu sai
- **Undo Snapshot không "lùi 1 bước thao tác"** — nó **dựng lại cả scene** từ ảnh chụp của entry trước. Mọi actor là object MỚI → con trỏ cũ chết → mới cần PersistentID ([[EntityIdLibrary_Reference]]).
- **Sau Undo, trạng thái về theo 3 nhịp**: ngay lập tức (spawn, chọn, gizmo) → +0.1s (Inventory refresh qua Timer) → vài frame sau (vật liệu + thông số từng slot, async). Nhìn sớm quá tưởng lỗi.
- **`SelectActors` bị gọi 2 lần** trong RestoreSnapshot (bước 5 và 6b) — chính là nguồn gốc bug B-gizmo (đã fix 24/09 bằng Deactivate trước Activate).
- **Undo mất slot vật liệu đang chọn + Inspector về trống** khi undo thao tác Snapshot — do respawn. Undo chỉnh thông số thì KHÔNG mất. Đóng ở **U3** ([[Open_Bugs]] `Bug-ParamUndo-SlotContextLost`).
- **Ctrl+Shift+Z cũng làm Ctrl+Z "thỏa điều kiện"** — `IA_FurnitureUndo` check Shift để nhường cho Redo ([[BP_FoffPlayerController]]).

## Nhảy tới code
| Hàm | Doc |
|---|---|
| `UndoLastAction` · `RedoLastAction` · `CaptureSnapshot` · `BuildSceneSnapshotBase` · `AppendEntry` · `RestoreSnapshot` · `ApplyParamCommand` · `JumpToHistoryIndex` · `GetGroupsForSnapshot` | [[BP_UndoManager]] |
| `IA_FurnitureUndo` · `IA_FurnitureRedo` | [[BP_FoffPlayerController]] |
| `OnMouseReleased` (ghi Move/Rotate/Scale) | [[BP_GizmoController]] |
| `DeselectAll` · `SelectActors` · `SpawnFurnitureCopy` · `ValidateEditMode` (bên UM) · `UpdateGizmo` | [[BP_FurnitureInputManager]] |
| `LoadMeshAsync` · `RestoreMyMaterialSlots` · `Rst_LoadNextSlot` | [[BP_FurnitureActor]] |
| `OnSceneRestored` · `ApplyRestoredActor` · `RefreshParamPanel` | [[WBP_FurnitureInventory]] |
| `RefreshButtonState` | [[WBP_MeshControls]] |
| `ApplyLoadedMaterialToSlot` · `ApplyParamsJsonToSlot` | [[MaterialSlotService_Reference]] |
