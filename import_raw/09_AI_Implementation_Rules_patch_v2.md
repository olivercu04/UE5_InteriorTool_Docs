# 09 — Bộ Quy Tắc Thực Thi cho AI — PATCH v2
**Phiên bản:** 2.0 | **Cập nhật:** 14/06/2026 — (điền giờ:phút ICT khi apply)
**Patch từ bản gốc. Thêm Q8 (Self-Check Gate), mở rộng L9, thêm mục BÀN GIAO OPUS→SONNET.**
> Lý do patch: L9 (local var không sống xuyên event) ĐÃ tồn tại trong file gốc mà Sonnet vẫn vấp (14/06, bug tạo Local Variable trong event OnSelectionChangedHandler). → Chứng minh: thêm luật KHÔNG đủ. Phải có cơ chế ép tự-soi trước khi trả lời.

---

## ⭐ Q8 — SELF-CHECK GATE (cổng bắt buộc trước khi đưa BẤT KỲ node flow nào)

**Vấn đề giải quyết:** L1-L10 là kiến thức thụ động. AI "biết" nhưng không tự đối chiếu lúc sinh logic → lặp lại lỗi cũ đã có trong file.

**Quy tắc cứng:** Trước khi đưa ra MỌI node flow / hướng dẫn tạo biến / cấu trúc Blueprint, AI phải chạy checklist dưới và **ghi 1 dòng kết quả soi ngắn gọn** trong câu trả lời (không bỏ qua, không làm thầm).

```
SELF-CHECK (chạy TRƯỚC khi viết flow):
□ Đang tạo Local Variable? → nơi chứa là FUNCTION hay EVENT?
   Event/Custom Event KHÔNG có Local Variable (L9) → đẩy logic vào Function, hoặc Class Variable.
□ Mọi Object access có IsValid trước chưa? (L1)
□ Mọi Branch có merge về cuối, không dead-end nuốt logic sau? (L2)
□ Class var persistent đã CLEAR ở đầu function chưa? (L: TempSelectedIndices)
□ Có Latent node (Async/Delay/Timer) trong Function không? → sai, phải Custom Event (L8)
□ Flow có > 2 tầng Branch lồng không? → DỪNG, đề nghị tách Function/helper (xem mục bàn giao)
□ Function thao tác đúng CẤP chưa? (gom đơn vị chọn vs gom actor-lá — bug CreateGroup 14/06)
□ Có đường NGƯỢC chưa? (file 10, Luật 6A)
```

**Cách ghi trong trả lời (ví dụ ngắn):**
> *Self-check: logic này đặt trong Function `UpdateSelectionInfoBar` (không phải event) → local var hợp lệ. IsValid trên Primary ✓. Branch merge về SetText cuối ✓. Không latent. 1 tầng Branch.*

Một dòng vậy đủ. Mục tiêu là **buộc AI dừng lại đối chiếu**, không phải viết luận.

---

## MỞ RỘNG L9 — Local Variable: kiểm NƠI CHỨA trước

```
TRƯỚC khi bảo cuhoang "tạo Local Variable":
  Nơi chứa là Function?      → OK, Local Variable hợp lệ.
  Nơi chứa là Event/Custom Event? → SAI. Event KHÔNG có Local Variable panel.
     Cách xử lý:
       1. (ưu tiên) Đẩy logic vào 1 Function riêng, Event chỉ gọi Function đó.
       2. (thay thế) Dùng Class Variable, nhớ CLEAR ở đầu handler.
```
> Dấu hiệu nhận biết Event: node màu đỏ (Custom Event), hoặc handler bind từ Dispatcher (OnSelectionChangedHandler, OnEditModeChangedInfoBar...). Mấy cái này KHÔNG chứa Local Variable.

---

## ⭐ MỤC MỚI — BÀN GIAO OPUS → SONNET (giảm lỗi từ gốc)

Lỗi Sonnet thường không phải do Sonnet "kém" mà do **task đóng gói chưa đủ để thực thi không-sai**. Hai luật cho Opus khi viết plan giao Sonnet:

### LUẬT A — Task Card phải self-contained
Mỗi task giao Sonnet phải kèm SẴN, ngay trong task (không bảo "đọc file 09 đi"):
- **Bài học cũ áp dụng cho task này** — trích thẳng dòng L liên quan.
- **Node được phép dùng** — trích từ bảng NODE CHÍNH XÁC, chỉ những node task cần.
- **Checklist "phải có"** trước khi submit (rút gọn từ Q8 cho task đó).

### LUẬT B — Giới hạn độ phức tạp mỗi flow giao Sonnet
```
Flow có > 2 tầng Branch lồng → Opus PHẢI tách thành helper Function trước khi giao.
KHÔNG đưa Sonnet một cây Branch nhiều tầng.
Logic phức tạp → đẩy về Function có tên rõ; Sonnet chỉ ráp các Function phẳng.
```
> Lý do: cây Branch sâu là nơi Sonnet (và cả Opus) dễ tạo dead-end, quên IsValid, sai cấp. Phẳng hóa = ít chỗ sai. Đây cũng đúng R3 (widget nhẹ) khi flow nằm trong widget.

### Hệ quả kiến trúc (đã rút từ bug info bar 14/06)
> Logic resolve/tính toán phức tạp **không thuộc widget/event**. Đẩy về Function trong Actor quản lý (vd InputManager). Widget/Event chỉ gọi 1 node → nhận kết quả. Vừa đúng R3, vừa tránh local-var-trong-event, vừa giảm chỗ Sonnet sai.

---

## CẬP NHẬT — CHECKLIST CUỐI MỖI TASK (thêm dòng)
```
- [ ] Code chạy đúng test trong 07
- [ ] Không vi phạm L1-L10
- [ ] [MỚI] Đã chạy Q8 Self-Check Gate, ghi dòng kết quả soi
- [ ] Không hallucinate node (đối chiếu bảng node)
- [ ] Performance OK (08)
- [ ] Hard ref clear ở End Play/Destruct (nếu có)
- [ ] [MỚI] Có đường NGƯỢC, đã test (file 10 Luật 6A)
- [ ] Cập nhật doc (version, ngày, giờ, phút)
```

---

## Lịch sử cập nhật (file 09)
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | (gốc) | Q1-Q7, L1-L10, bảng node, quy trình task |
| 2.0 | 14/06/2026 | **Q8 Self-Check Gate** (ép tự-soi trước khi viết flow), **mở rộng L9** (kiểm nơi chứa Local Variable = Function/Event), **mục Bàn giao Opus→Sonnet** (Luật A Task Card self-contained, Luật B giới hạn 2 tầng Branch → tách Function). Nguồn: bug Sonnet tạo Local Variable trong event dù L9 đã có (14/06). |
