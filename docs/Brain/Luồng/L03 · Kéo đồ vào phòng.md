# L03 · Kéo đồ vào phòng

> **Hành trình:** ← [[L02 · Tìm đồ trong kho|L02 Tìm đồ trong kho]] · **L03** · [[L04 · Chọn đồ|L04 Chọn đồ]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là bước ③ · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** kéo 1 thẻ đồ ra khỏi kho là **sinh ngay 1 đồ bóng thật** trong phòng; lúc thả, đồ bóng được "đóng dấu" thành đồ thật (mesh, RowName, tag, ID, nhóm) và sổ ghi 1 mốc `Spawn`.

## Người dùng làm gì → thấy gì
| Làm | Thấy | Sổ lịch sử |
|---|---|---|
| Nhấn giữ + kéo thẻ | Gizmo cũ tắt, đồ bóng xuất hiện dưới chuột | — |
| Rê chuột | Bóng bám sàn / tường / trần, tự xoay đứng thẳng áp tường | — |
| Thả | Đồ ở lại đúng chỗ, vào mục **Recent** | 1 mốc `Spawn` |

## Chạy thế nào
![[Architecture_Map#5i — Kéo đồ từ kho thả vào phòng]]
> 🗺️ Bản làn bơi: [[5i - Kéo đồ từ kho thả vào phòng.canvas|canvas 5i]]

## Hình dung
Đồ bóng giống **mẫu trưng bày gắn bánh xe**: vẫn là đồ thật (`BP_FurnitureActor`), chỉ chưa được đăng ký vào kho hàng. Thả xuống = gắn tem (`FurnitureSpawned`), ghi số hiệu (`RowName`), cấp số seri (`PersistentID`) và vào sổ.

## Dễ hiểu sai
- **Đồ vừa thả KHÔNG tự được chọn** — muốn kéo gizmo phải click chọn ([[L04 · Chọn đồ|L04]]).
- **Mặt đặt được quyết lúc kéo, không phải lúc thả** — `PlacementSurfaceType` (Floor / Wall / Ceiling) SET trong On Drag Over theo pháp tuyến mặt chạm; Move bằng gizmo sau này KHÔNG bám mặt lại.
- **Đang sửa nhóm thì đồ mới tự vào nhóm đó** — nhánh `Scope != ""` phải merge về `CaptureSnapshot` (nhánh False cụt = On Drop không trả true → UMG coi như thả hỏng).
- **Đường này không đi qua `SpawnFurnitureCopy`** như Dán / Nhân bản / Undo → phải tự `EnsurePersistentId` (producer ID thứ 4, thêm 21/09). Sửa gì chung cho "mọi đường sinh đồ" nhớ rà cả đường này ([[AI_Implementation_Rules]] "SPAWN PATHS").
- Mesh nạp kiểu blocking khi bắt đầu kéo (nợ R1) — kho nhiều đồ nặng sẽ khựng nhẹ lúc bắt đầu kéo.

## Đường ngược (6A)
Ctrl+Z → entry `Spawn` là Snapshot → dựng lại cảnh trước khi thả ([[L13 · Hoàn tác và làm lại|L13]]). Kéo rồi bỏ (Esc / thả ra ngoài) → `On Drag Cancelled` của thẻ dọn overlay + đồ bóng.

## Còn mở
- **CONFLICT** On Drop có gọi `DeactivateGizmo` ở đầu không (G5.4 nói Cast là node đầu tiên).
- Thả hụt (tia không trúng gì): nhánh dead-end, chưa rõ ai dọn đồ bóng.
- Nhánh Furniture của On Drop nằm trong export 11/09 nhưng chưa có dòng chốt K2 riêng → xin K2 đoạn Cast → CaptureSnapshot("Spawn").

## Nhảy tới code
| Hàm | Doc |
|---|---|
| `On Drag Detected` · `On Drag Cancelled` | [[WBP_FurnitureCard]] |
| `On Drag Over` · `On Drop` (3 nhánh Furniture / Combo / Material) | [[WBP_DragOverlay_FurnitureCard]] |
| `EnsurePersistentId` | [[EntityIdLibrary_Reference]] |
| `GetCurrentEditScope` | [[BP_FurnitureInputManager]] |
| `AddRecentMesh` | [[BP_FurnitureUserPrefsManager]] |
