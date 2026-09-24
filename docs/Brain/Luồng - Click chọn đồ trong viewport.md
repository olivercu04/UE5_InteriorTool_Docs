# Luồng — Click chọn đồ trong viewport

> Viết tay 24/09/2026 từ as-built [[BP_FurnitureInputManager]] (`OnLMBReleased` ✓K2 12/09) + [[WBP_FurnitureInventory]] + [[BP_UndoManager]].
> ← [[Bản đồ não]] · Luồng hệ thống: [[Luồng 3a - Chọn đồ Gizmo Nhóm]]

**Ý chính:** nhấn chuột KHÔNG chọn ngay — chỉ ghi lại đồ bị bấm (`PendingClickActor`). **Thả chuột** mới quyết: click đơn → chọn; kéo → box select. Vì thế mọi thứ bắt đầu ở `OnLMBReleased`.

> Nguồn DUY NHẤT: [[Architecture_Map]] Phần 5 (nhúng — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc.

![[Architecture_Map#5a — Click chọn đồ trong viewport]]
> 🗺️ Bản kéo/zoom được: [[5a - Click chọn đồ trong viewport.canvas|Canvas 5a]]

### Đọc sơ đồ theo 1 cú click
1. Nhấn chuột lên ghế → **Pressed** chỉ ghi nhớ "đã bấm vào ghế này".
2. Thả chuột, không kéo → **OnLMBReleased** nhánh click đơn.
3. `DeselectAll` → `ExpandSelectionWithGroups` (ghế nằm trong group thì kéo theo cả group) → `SelectActors`.
4. `SelectActors` làm 3 việc: tô viền (`UpdateOutlineState`), đặt gizmo (`UpdateGizmo`), **phát tin** `OnSelectionChanged`.
5. Ai nghe tin: Inventory (đổi đồ đang chỉnh vật liệu, hủy phiên chỉnh param nếu đang dở) và thanh info (`WBP_MeshControls`).
6. Quay lại `OnLMBReleased`: ghi sổ undo `CaptureSnapshot("Select")`, rồi nếu chỉ chọn 1 món → `NotifyViewportSlotClick` để chọn luôn slot vật liệu dưới chuột.

### Nhảy tới code
| Hàm | Doc |
|---|---|
| `OnLMBReleased` (mục "FULL FLOW") · `DeselectAll` · `SelectActors` · `ExpandSelectionWithGroups` · `ToggleActor` · `UpdateOutlineState` · `UpdateGizmo` | [[BP_FurnitureInputManager]] |
| `ActivateGizmo` · `DeactivateGizmo` | [[BP_GizmoController]] |
| `CaptureSnapshot` | [[BP_UndoManager]] |
| `OnSelectionChangedMaterial` · `OnMeshSelected` · `NotifyViewportSlotClick` | [[WBP_FurnitureInventory]] |
| `OnSelectionChangedInfoBar` | [[WBP_MeshControls]] |
