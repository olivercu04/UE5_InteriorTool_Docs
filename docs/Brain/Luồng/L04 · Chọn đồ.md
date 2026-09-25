# L04 · Chọn đồ

> **Hành trình:** ← [[L03 · Kéo đồ vào phòng|L03 Kéo đồ vào phòng]] · **L04** · [[L05 · Di chuyển và xoay đồ|L05 Di chuyển và xoay đồ]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là bước ④ · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** nhấn chuột **chưa chọn gì** — chỉ ghi nhớ. **Thả chuột mới quyết**: chưa kéo quá 5px = click (chọn 1 món, cả nhóm của nó), kéo quá 5px = quét khung.

## Người dùng làm gì → thấy gì
| Làm | Thấy | Sổ lịch sử |
|---|---|---|
| Click 1 món | Viền trắng, gizmo hiện; món trong nhóm thì cả nhóm được chọn | `Select` |
| Ctrl + click | Cộng / bớt món (cả nhóm) vào lựa chọn | `Select` |
| Click nền trống | Bỏ chọn (và thoát chế độ thay đồ nếu đang bật) | `Deselect` |
| Kéo khung trên nền | Khung xanh, thả ra chọn mọi đồ có **tâm** trong khung | `BoxSelect` |
| Click 1 món khi tab Material mở | Chọn luôn vùng vật liệu (slot) dưới chuột | (cùng mốc `Select`) |

## Chạy thế nào — click
![[Architecture_Map#5a — Click chọn đồ trong viewport]]
> 🗺️ Bản làn bơi: [[5a - Click chọn đồ trong viewport.canvas|canvas 5a]]

## Chạy thế nào — quét khung
![[Architecture_Map#5j — Quét chọn nhiều món (box select)]]
> 🗺️ Bản làn bơi: [[5j - Quét chọn nhiều món (box select).canvas|canvas 5j]]

## Hình dung
**3 điểm chạm, 3 vai:**
```
Mouse Left Pressed  → chỉ GHI: điểm bắt đầu + món bị bấm (PendingClickActor)
Event Tick          → chỉ VẼ khung khi đã kéo > 5px (không chọn gì)
OnLMBReleased       → QUYẾT: click đơn (Then 2) hay chốt khung (Then 1), rồi ghi sổ
```
Giống **bấm chuông cửa**: nhấn chưa phải là mở cửa — người trong nhà đợi bạn buông tay mới biết bạn chỉ bấm hay đang giữ.

## Dễ hiểu sai
- **Tại sao không chọn ngay lúc nhấn?** Để phân biệt "click chọn" với "bắt đầu kéo khung từ trên 1 món".
- **Tại sao chốt ở OnLMBReleased mà không ở Tick?** Gọi `ActivateGizmo` trong Tick làm gizmo nháy 1 frame (race với plugin RuntimeTransformer). Input event chạy trước Tick.
- **Không dùng `Is Input Key Down(Left Mouse)`** — không tin được khi viewport giữ chuột → dùng cờ `bLMBHeld`.
- **Quét khung trúng 1 món trong nhóm = lấy cả nhóm** (`ExpandSelectionWithGroups`, ✓K2 25/09) — giống click đơn.
- **Quét khung chọn theo ĐIỂM GỐC của món**, không theo bounding box — đúng thiết kế. Toạ độ phải chia `Get Viewport Scale` (lệch DPI đã trả giá).
- **Tick còn đường dự phòng không lấy nhóm** (`SelectSingleActor` trực tiếp) khi thả chuột lọt giữa 2 frame — bug đang sống `Bug-TickFallback-GroupNotExpanded` ([[Open_Bugs]]).
- `SelectActors` báo tin `OnSelectionChanged` **đồng bộ** — kho vật liệu và info bar đổi ngay trong cùng lượt.

## Đường ngược (6A)
Click nền = bỏ chọn; Ctrl+click lần nữa = bớt khỏi lựa chọn; Ctrl+Z quay lại lựa chọn trước (mốc Select / Deselect / BoxSelect).

## Còn mở
- (không còn mục mở ở thân `FinishBoxSelect` — Bug-BoxSelectCtrl-MultiSnapshot fix 25/09)

## Nhảy tới code
| Hàm | Doc |
|---|---|
| TƯƠNG TÁC 3 ĐIỂM · `Mouse Left Pressed` · `Event Tick — Box Select branch` · `OnLMBReleased` · `FinishBoxSelect` · `ExpandSelectionWithGroups` · `SelectActors` · `ToggleActor` · `DeselectAll` | [[BP_FurnitureInputManager]] |
| `ShowBox` · `UpdateBox` · `HideBox` | [[WBP_BoxSelectOverlay]] |
| `ActivateGizmo` · `DeactivateGizmo` | [[BP_GizmoController]] |
| `OnSelectionChangedMaterial` · `OnMeshSelected` · `NotifyViewportSlotClick` | [[WBP_FurnitureInventory]] |
| `OnSelectionChangedInfoBar` | [[WBP_MeshControls]] |
