# Tư duy 4 · Cách viết tài liệu trong bộ não

> ↑ [[Bản đồ não]] · Bộ Tư duy: [[Tư duy 1 · Sản phẩm và người dùng|1 Sản phẩm]] · [[Tư duy 2 · Kiến trúc và nguyên tắc code|2 Kiến trúc]] · [[Tư duy 3 · Cách làm việc và kiểm chứng|3 Cách làm việc]] · **4 Cách viết tài liệu**
> Viết 25/09/2026. Luật doc gốc: [[Execution_Discipline]] (R-DOC) · [[AI_Implementation_Rules]] (L-DOC, notation ▶→ ●→) · [[Architecture_Map]] (quy ước mũi tên).

**Dùng khi:** thêm / sửa sơ đồ, viết note luồng mới, không biết file nào được sửa tay.

---

## 1. Ba tầng — người đọc chỉ xuống sâu khi cần

```
 TẦNG 1 · TỔNG QUÁT (Brain/Tổng quát)      3 canvas có ảnh thật — người mới, người làm sản phẩm
      │  "bước ④ Chọn và sắp xếp" ↗
      ▼
 TẦNG 2 · LUỒNG (Brain/Luồng · L01…L13)    1 note = 1 việc người dùng làm, theo hành trình
      │  nhúng sơ đồ 5x ↗
      ▼
 TẦNG 3 · CHI TIẾT                          sequence 5x (Architecture_Map Phần 5) → canvas làn bơi →
                                            mục hàm trong doc canonical (▶→) → K2 export
```
Tầng 3 chủ yếu cho AI / người sửa code; AI được trỏ tới đúng lúc qua Q10, [[00_INDEX]], `CLAUDE.md` — không đọc đầu phiên.

## 2. Sáu nguyên tắc trình bày (tâm lý học trình bày)

1. **Bắt đầu từ cái người đọc đã biết** — ảnh màn hình, thao tác của người dùng; không bắt đầu từ tên Blueprint.
2. **Tiêu đề = thông điệp** ("Mọi thao tác chỉnh đồ đều đi đúng 4 bước"), không phải nhãn ("Sơ đồ logic").
3. **Một đường đọc đánh số** ① → ② → ③; mỗi trang có đúng 1 điểm vào và 1 "Đọc tiếp →".
4. **Chính to + có màu, phụ nhỏ + xám.** Không để mọi thứ ngang hàng (auto-layout làm việc này — tránh cho tầng tổng quát).
5. **Ít đường, không cắt nhau.** Sơ đồ rối thì tách, không nén.
6. **Cùng màu = cùng nghĩa ở mọi trang:** xanh = đường chính · cam = màn hình / UI · vàng = điểm hay nhầm · đỏ = số đánh dấu trên ảnh.

## 3. Luật bằng chứng trên sơ đồ

| Ký hiệu | Phần 3 (asset) | Phần 5 (sequence) | Nghĩa |
|---|---|---|---|
| liền | `==>` | `->>` | Doc ghi **✓K2** cho đúng lời gọi đó (có ngày) |
| đứt | `-.->` | `-->>` | Theo doc (as-built, PIE) — chưa K2 |
| `?` trong nhãn | có | có | Doc không nói (vd không ghi ai gọi) — thẻ canvas thành đỏ |
| mũi tên từ User | — | `->>` | Thao tác người dùng, không mang bằng chứng |

- Hai nguồn **mâu thuẫn** → ghi dòng `**CONFLICT:**` dưới sơ đồ và **giữ mức bằng chứng thấp hơn**.
- **Không tự phát minh quan hệ** doc không nhắc. Doc không nói → không vẽ, hoặc vẽ với `?` + ghi rõ thiếu gì.
- Mỗi mục 5x kết bằng dòng `**Kiểm chứng K2:**` và `Nguồn:` — build kiểm tra có đủ.

## 4. File nào sửa tay, file nào tự sinh

| Loại | File | Sửa ở đâu |
|---|---|---|
| **Nguồn duy nhất** của mọi sơ đồ | [[Architecture_Map]] Phần 3 + Phần 5 | sửa tay, đúng quy trình doc |
| Viết tay | [[Bản đồ não]] · `Brain/Tư duy/*` · `Brain/Luồng/L01…L13` | sửa tay |
| Tự sinh | mục 🧠 Kết nối cuối mỗi doc · `Brain/Kết nối/*` · `Brain/Canvas/*` · `Brain/Chưa có doc/*` · [[Kiểm tra bản đồ]] · [[Chỉ mục hàm & biến]] | **không sửa tay** — sửa nguồn rồi chạy build |
| Tự sinh từ script | `Brain/Tổng quát/*.canvas` | sửa nội dung trong `Brain/_tools/gen_tong_quat.py` |

Một lệnh dựng lại tất cả (trong thư mục `docs`): `python Brain/_tools/build.py` → mở [[Kiểm tra bản đồ]]: mục ❌ (thiếu cạnh), ⚠ (Phần 3 tụt bằng chứng), 🔗 (link gãy) phải = 0. File sinh ra không ghi ngày → chạy lại khi nguồn không đổi thì git không đổi.

## 5. Thêm 1 luồng mới — 5 bước

1. Đọc doc canonical của mọi Blueprint dính luồng; ghi lại từng lời gọi + bằng chứng (✓K2 ngày nào / doc / không rõ).
2. Viết mục `### 5x — Tiêu đề` vào [[Architecture_Map]] Phần 5: `participant ID as TênAsset` (đúng tên doc) · nhãn `câu tiếng Việt · TênHàm()` · liền chỉ khi ✓K2 · kết bằng `Kiểm chứng K2:` + `Nguồn:`.
3. Render thử (mermaid-cli hoặc Obsidian). Lưu ý: không đặt ID participant là từ khoá Mermaid (`box`, `end`, `loop`…), không dùng `;` hay `#` trong nhãn.
4. Chạy `build.py` → thêm cạnh Phần 3 cho các cặp ❌, nâng / tách cạnh cho các dòng ⚠ → chạy lại tới khi = 0.
5. Nhúng mục vào đúng 1 note `Brain/Luồng/Lxx` (dòng `![[Architecture_Map#5x — Tiêu đề]]`). Build báo "Mục 5x chưa thuộc luồng" nếu quên.

## 6. Khuôn 1 note luồng (Lxx)

```
# Lxx · Tên việc người dùng làm
> Hành trình: ← Lxx-1 · Lxx · Lxx+1 →  ·  ↑ Bản đồ não · bước n trên Tổng quát 1
**Một câu:** việc này là gì, điểm mấu chốt kỹ thuật là gì.
## Người dùng làm gì → thấy gì        (bảng: Làm | Thấy | Sổ lịch sử)
## Chạy thế nào                         (nhúng 5x + link canvas)
## Hình dung                            (ví dụ đời thường / ASCII — chỉ khi cần)
## Dễ hiểu sai                          (từ "Bug đã trả giá", ⚠ trong doc)
## Đường ngược (6A)
## Còn mở                               (? · CONFLICT · K2 nên xin)
## Nhảy tới code                        (bảng hàm → doc)
```
Giọng viết: trung tính (người đọc có thể là nhân viên mới), tiếng Việt, tên hàm giữ tiếng Anh, bảng / gạch đầu dòng thay đoạn văn.

## 7. Đặt tên

- Note luồng: `Lxx · Việc người dùng làm` (số theo hành trình, không theo thứ tự viết).
- Mục sequence: `5x` (chữ cái kế tiếp — thứ tự viết), nằm trong đúng 1 note Lxx.
- Note kết nối asset: `Kết nối 3x - …` (tự sinh). Canvas làn bơi: `5x - Tiêu đề.canvas` (tự sinh).
- Doc canonical giữ tên asset (`BP_…`, `WBP_…`, `…_Reference`) — script tra mục hàm theo tên này.

---
**Hết bộ Tư duy.** Quay lại [[Bản đồ não]] → lộ trình tiếp nhận bước tiếp theo: các note luồng L01…L13.
