# Bản đồ não — UE5 Interior Tool

> Trang chủ "bộ não thứ 2" (Obsidian, vault = gốc repo). Người mới — hoặc AI mới vào dự án — **đi theo lộ trình bên dưới từ trên xuống**; mỗi trang đều có link "Đọc tiếp →".
> Tạo 24/09/2026 · cấu trúc lại thành lộ trình tiếp nhận 25/09/2026. Sơ đồ + link sinh từ [[Architecture_Map]] — xem mục "Cập nhật" cuối trang.

## 🧭 Lộ trình tiếp nhận — 4 chặng, ~2 giờ

| Chặng                            | Đọc                                                                                                                                                                                                  | Để biết                                                                                    | Thời gian |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | --------- |
| **1 · Nhìn tổng thể**            | [[1 · Một buổi dựng phòng.canvas\|Tổng quát 1]] → [[2 · Phía sau màn hình.canvas\|2]] → [[3 · Khuôn 4 bước.canvas\|3]]                                                                               | Người dùng làm gì, trên màn hình nào · bên trong gồm khối nào · mọi thao tác đi 4 bước nào | 15 phút   |
| **2 · Cách nghĩ của dự án**      | [[Tư duy 1 · Sản phẩm và người dùng\|Tư duy 1]] → [[Tư duy 2 · Kiến trúc và nguyên tắc code\|2]] → [[Tư duy 3 · Cách làm việc và kiểm chứng\|3]] → [[Tư duy 4 · Cách viết tài liệu trong bộ não\|4]] | Làm cho ai · xây thế nào · làm việc thế nào · ghi chép thế nào                             | 30 phút   |
| **3 · Từng việc người dùng làm** | 13 note luồng bên dưới, theo thứ tự                                                                                                                                                                  | Mỗi thao tác chạy qua hàm nào, bằng chứng tới đâu, chỗ nào dễ sai                          | 60 phút   |
| **4 · Bắt tay vào việc**         | [[01_Session_State]] → [[00_INDEX]] "Muốn sửa X"                                                                                                                                                     | Đang ở sprint / gate nào, task nào                                                         | 10 phút   |

## Chặng 3 — 13 luồng theo hành trình một buổi dựng phòng

| # | Luồng | Người dùng làm | Sơ đồ |
|---|---|---|---|
| ① | [[L01 · Mở tool và kho đồ]] | mở kho, đóng kho | 5g |
| ② | [[L02 · Tìm đồ trong kho]] | gõ tìm, bấm thư mục, Gần đây / Yêu thích | 5h |
| ③ | [[L03 · Kéo đồ vào phòng]] | kéo thẻ, thả vào phòng | 5i |
| ④ | [[L04 · Chọn đồ]] | click, Ctrl+click, quét khung | 5a · 5j |
| ④ | [[L05 · Di chuyển và xoay đồ]] | kéo gizmo, phím mũi tên | 5f · 5k |
| ④ | [[L06 · Nhóm đồ và sửa nhóm]] | Ctrl+G, vào / ra nhóm, bỏ nhóm | 5l |
| ✦ | [[L07 · Menu chuột phải và phím tắt]] | copy, dán, nhân bản, xoá | 5m |
| ✦ | [[L08 · Thay đồ]] | thay món bằng món khác cùng chỗ | 5n |
| ⑤ | [[L09 · Đổi vật liệu]] | bấm / kéo thẻ vật liệu | 5o · 5p |
| ⑤ | [[L10 · Chỉnh thông số vật liệu]] | kéo thanh trượt, vòng màu | 5b |
| ⑥ | [[L11 · Combo]] | lưu, đặt, thay cả cụm | 5q · 5r · 5s |
| ⑦ | [[L12 · Lưu và mở cảnh]] | Save / Load | 5t |
| ✦ | [[L13 · Hoàn tác và làm lại]] | Ctrl+Z, Ctrl+Shift+Z | 5c · 5d · 5e |

> ①…⑦ = số bước trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] · ✦ = dùng được bất cứ lúc nào.

## Khi cần tra nhanh

| Muốn biết | Mở |
|---|---|
| Hàm / biến Y dính luồng nào, ai GHI ai ĐỌC (đầu vào Q10) | [[Chỉ mục hàm & biến]] *(tự sinh)* |
| Bản đồ có khớp không, nên xin K2 nào, link nào gãy | [[Kiểm tra bản đồ]] *(tự sinh)* |
| Thành phần X nói chuyện với ai (mức asset) | mục 🧠 Kết nối cuối doc X · 5 mảng: [[Kết nối 3a - Chọn đồ Gizmo Nhóm\|3a Chọn đồ]] · [[Kết nối 3b - Combo lưu spawn thay combo\|3b Combo]] · [[Kết nối 3c - Inventory + Cây thư mục\|3c Kho]] · [[Kết nối 3d - Save Undo khởi động\|3d Save / Undo]] · [[Kết nối 3e - Vật liệu Material\|3e Vật liệu]] |
| Node thật bên trong 1 hàm | doc canonical (khối ▶→) — thẻ canvas có dòng `↗ Doc › Hàm` nhảy thẳng tới mục |
| Bug đang mở · vì sao làm khác plan | [[Open_Bugs]] · [[DEVIATIONS]] |
| Luật Blueprint · bài học | [[AI_Implementation_Rules]] · [[Learning_System]] |
| Review sản phẩm / UX | [[25-09-2026_Product_UX_Review_Plan_v1]] |

## 🔧 Chi tiết — Canvas làn bơi (tự sinh, 1 canvas cho mỗi sơ đồ 5x)
> Cùng nội dung sơ đồ Phần 5, dạng **làn bơi**: mỗi cột = 1 BP / WBP / C++, mỗi thẻ = 1 bước, đi theo mũi tên = đi theo thời gian.
> Xanh lá + `✓K2` = đã kiểm chứng K2 · xám = theo doc · đỏ + `?` = chưa rõ · vàng = nhánh "ngược lại" / ghi chú.
> Chuột giữa kéo = di chuyển · `Ctrl` + cuộn = zoom · `Shift+1` = vừa khung. Dòng `↗ Doc › Hàm` trên thẻ nhảy tới mục của hàm trong doc.
> Mở từ note luồng (mỗi sơ đồ có link "Bản làn bơi") — hoặc thư mục `Brain/Canvas` trong File explorer.

## 3 nhân vật trung tâm (nhiều kết nối nhất)
- [[BP_FurnitureInputManager]] — não chọn đồ / thao tác
- [[WBP_FurnitureInventory]] — cửa sổ kho + vật liệu
- [[BP_UndoManager]] — sổ lịch sử

---

## Graph
Filter + 6 nhóm màu đã ghi trong `.obsidian/graph.json` của vault. Ẩn: Archive · import_raw · Sprints · Plans · Planning · 00_INDEX · README · CLAUDE.

| Màu | Query | Là gì |
|---|---|---|
| xanh dương | `path:docs/Blueprints` | Blueprint Actor / Manager |
| cam | `path:docs/Widgets` | Widget UMG |
| xanh lá | `path:docs/Data` | C++ / dữ liệu |
| tím | `path:docs/Brain` | note luồng, tư duy, trang chủ |
| xám | `path:"docs/Brain/Chưa có doc"` | mắt xích chưa có doc |
| vàng | `path:docs/00_Core` | trạng thái / kiến trúc |

**Local graph** là cách xem hay nhất: mở 1 doc (vd [[BP_UndoManager]]) → `Ctrl+P` → "Open local graph" → Depth 1 = hàng xóm trực tiếp. Cuối mỗi doc canonical có mục **🧠 Kết nối** (Có mặt trong thao tác · Gọi → · ← Được gọi bởi).

---

## Cập nhật
**1 lệnh dựng lại tất cả** — sửa [[Architecture_Map]] (đúng quy trình doc) → chạy trong thư mục `docs`:
```
python Brain/_tools/build.py
```
| Sinh ra | Từ | Script |
|---|---|---|
| Mục 🧠 Kết nối cuối mỗi doc + `Brain/Kết nối/*` + `Brain/Chưa có doc/*` | Phần 3 + note `Brain/Luồng/Lxx` | `gen_brain.py` |
| Canvas làn bơi `Brain/Canvas/*.canvas` | Phần 5 | `gen_canvas.py` |
| 3 canvas `Brain/Tổng quát/*` | nội dung trong script | `gen_tong_quat.py` |
| [[Kiểm tra bản đồ]] — lệch Phần 3 ↔ 5, `?`, K2 đáng xin, link gãy, mục 5x chưa thuộc luồng | Phần 3 + 5 + Brain | `build.py` |
| [[Chỉ mục hàm & biến]] | Phần 5 | `build.py` |

Sau mỗi lần chạy: mở [[Kiểm tra bản đồ]] — ❌, ⚠, 🔗 phải bằng 0. File sinh ra không ghi ngày → chạy lại khi nguồn không đổi thì git không đổi.
**Viết tay (script không đụng):** trang này · `Brain/Tư duy/*` · `Brain/Luồng/*`. **Tự sinh (không sửa tay):** mọi thứ còn lại trong `Brain/`. Quy trình thêm 1 luồng mới: [[Tư duy 4 · Cách viết tài liệu trong bộ não|Tư duy 4]] mục 5.
