# Bản đồ não — UE5 Interior Tool

> Trang chủ "bộ não thứ 2" trong Obsidian. Mục tiêu: nhìn **graph** là thấy **ai gọi ai**, click 1 node là vào doc thật.
> Tạo 24/09/2026. Link giữa các doc sinh tự động từ [[Architecture_Map]] — xem "Cập nhật" cuối trang.

## Bắt đầu từ đâu
- Đang ở đâu → [[01_Session_State]]
- Kiến trúc tổng (sơ đồ gốc) → [[Architecture_Map]]
- Bug đang mở → [[Open_Bugs]] · Vì sao làm khác plan → [[DEVIATIONS]]
- Luật Blueprint → [[AI_Implementation_Rules]] · Bài học → [[Learning_System]]

## 5 luồng hệ thống (tự sinh)
- [[Luồng 3a - Chọn đồ Gizmo Nhóm]] — click chọn, box select, gizmo, group
- [[Luồng 3b - Combo lưu spawn thay combo]] — lưu/spawn/thay combo, thumbnail
- [[Luồng 3c - Inventory + Cây thư mục]] — cửa sổ inventory, cây folder, kéo-thả
- [[Luồng 3d - Save Undo khởi động]] — khởi động tool, Save/Load, Undo/Redo
- [[Luồng 3e - Vật liệu Material]] — slot vật liệu, Inspector, param panel

## Luồng event / function (viết tay, có sơ đồ)
> Mức HÀM: mỗi note = 1 thao tác của user, NHÚNG `sequenceDiagram` từ [[Architecture_Map]] **Phần 5** (1 nguồn, theo skill
> `arch-map` + diagram-contract: liền = ✓K2, đứt = theo doc). Không đưa hàm vào graph (≈300 hàm, tự trích sẽ ra cạnh sai).
> Thêm luồng mới = thêm 1 mục 5x vào Architecture_Map (quy trình `/arch-map`), rồi tạo note nhúng ở đây.
- [[Luồng - Click chọn đồ trong viewport]] — nhấn/thả chuột → chọn → viền + gizmo + báo Inventory
- [[Luồng U2 - Chỉnh thông số vật liệu và Undo]] — nhấn slider → kéo → thả → Ctrl+Z
- [[Luồng - Undo Redo]] — Ctrl+Z / Ctrl+Shift+Z: ghi sổ, dispatch, RestoreSnapshot chi tiết
- [[Luồng - Kéo gizmo Move]] — bấm Move → nhấn trục → kéo → thả (1 món / nhiều món qua Pivot) → ghi sổ Undo

## Xem dạng Canvas — kéo, zoom, bấm vào tên doc (24/09)
> Cùng nội dung sơ đồ Phần 5, trình bày dạng **làn bơi**: mỗi cột = 1 BP/WBP/C++, mỗi thẻ = 1 bước, **đi theo mũi tên 1 → 2 → 3 = đi theo thời gian**.
> Mũi tên xanh lá + chữ `✓K2` = đã kiểm chứng K2 · xám = theo doc · đỏ + `?` = chưa rõ. Thẻ vàng = nhánh "ngược lại" / ghi chú.
> Chuột giữa kéo = di chuyển · `Ctrl` + cuộn = zoom · `Shift+1` = vừa khung · bấm tên `[[doc]]` ở đầu cột để mở doc.
- [[5a - Click chọn đồ trong viewport.canvas|5a — Click chọn đồ trong viewport]]
- [[5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas|5b — Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session)]]
- [[5c - Undo - Redo — tổng quan (dispatch theo EntryKind).canvas|5c — Undo - Redo — tổng quan (dispatch theo EntryKind)]]
- [[5d - Ghi sổ lịch sử — 1 thao tác thành 1 entry (CaptureSnapshot).canvas|5d — Ghi sổ lịch sử — 1 thao tác thành 1 entry (CaptureSnapshot)]]
- [[5e - Undo 1 entry Snapshot — RestoreSnapshot (destroy + spawn lại).canvas|5e — Undo 1 entry Snapshot — RestoreSnapshot (destroy + spawn lại)]]
- [[5f - Kéo gizmo Move (1 món · nhiều món qua Pivot).canvas|5f — Kéo gizmo Move (1 món · nhiều món qua Pivot)]]

## 3 nhân vật trung tâm (nhiều kết nối nhất)
- [[BP_FurnitureInputManager]] — não chọn đồ / thao tác
- [[WBP_FurnitureInventory]] — cửa sổ inventory + material
- [[BP_UndoManager]] — sổ lịch sử

---

## Graph đã cài sẵn (24/09)
Filter + 6 nhóm màu đã ghi thẳng vào `.obsidian/graph.json` của vault — đóng/mở lại Graph view là thấy.
Ẩn: Archive · import_raw · Sprints · Plans · Planning · 00_INDEX · README · CLAUDE. Bật mũi tên hướng gọi.

| Màu | Query | Là gì |
|---|---|---|
| xanh dương | `path:docs/Blueprints` | Blueprint Actor/Manager |
| cam | `path:docs/Widgets` | Widget UMG |
| xanh lá | `path:docs/Data` | C++ / dữ liệu |
| tím | `path:docs/Brain` | note luồng + trang chủ |
| xám | `path:"docs/Brain/Chưa có doc"` | mắt xích chưa có doc |
| vàng | `path:docs/00_Core` | trạng thái / kiến trúc |

**Cách dùng hay nhất — Local graph:** mở 1 doc (vd [[BP_UndoManager]]) → `Ctrl+P` → "Open local graph" → Depth 1 = hàng xóm trực tiếp, Depth 2 = hàng xóm của hàng xóm. Đây là "ai gọi ai" của đúng thành phần đó.

Mỗi doc canonical có mục **🧠 Kết nối** ở CUỐI file (Gọi → / ← Được gọi bởi / Thuộc luồng).

---

## Cập nhật
Link sinh từ `00_Core/Architecture_Map.md` Phần 3 (sơ đồ mermaid) bằng `Brain/_tools/gen_brain.py`:
1. Sửa/thêm cạnh trong [[Architecture_Map]] (đúng quy trình doc như mọi khi).
2. Nhờ Claude chạy lại script (hoặc tự chạy `python Brain/_tools/gen_brain.py` trong thư mục `docs`).
Canvas (`Brain/Canvas/*.canvas`) sinh từ [[Architecture_Map]] **Phần 5** bằng `Brain/_tools/gen_canvas.py` — sửa Phần 5 rồi chạy
`python Brain/_tools/gen_canvas.py`. Canvas bị **ghi đè** mỗi lần chạy: kéo thẻ để xem thoải mái, nhưng đừng sửa nội dung trong canvas.
Script CHỈ thay đoạn giữa `BRAIN:START` / `BRAIN:END` ở cuối doc + ghi đè note trong `Brain/` — không đụng nội dung doc.
**Không sửa tay** mục 🧠 Kết nối (lần chạy sau sẽ ghi đè). Trang này và note "Luồng U2" viết tay — script không đụng.
