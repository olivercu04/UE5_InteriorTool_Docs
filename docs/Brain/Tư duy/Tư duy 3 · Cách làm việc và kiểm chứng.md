# Tư duy 3 · Cách làm việc và kiểm chứng

> ↑ [[Bản đồ não]] · Bộ Tư duy: [[Tư duy 1 · Sản phẩm và người dùng|1 Sản phẩm]] · [[Tư duy 2 · Kiến trúc và nguyên tắc code|2 Kiến trúc]] · **3 Cách làm việc** · [[Tư duy 4 · Cách viết tài liệu trong bộ não|4 Cách viết tài liệu]]
> Viết 25/09/2026. Tóm tắt + trỏ doc gốc: [[AI_Implementation_Rules]] (Q10 / Q9 / Q8, KP1–3) · [[Execution_Discipline]] · [[AI_Communication_Rules]] · [[Learning_System]] · [[Testing]].

**Dùng khi:** bắt đầu 1 phiên, nhận 1 task, gặp bug, sắp tick "xong".

---

## 1. Mở phiên — đọc đúng 3 thứ, theo thứ tự

1. [[01_Session_State]] — đang ở sprint / gate / task nào (dòng `Current:`).
2. Doc thực thi của gate đó (tên tra trong Session_State).
3. Chỉ khi cần node flow cũ: doc canonical của Blueprint liên quan ([[00_INDEX]] "Muốn sửa X").

Không đọc hết doc đầu phiên. Người mới muốn hiểu tổng thể → [[Bản đồ não]] (lộ trình tiếp nhận), không phải Session_State.

## 2. Phân vai (Senior – Intern)

| Ai | Làm gì |
|---|---|
| **Opus** (senior) | Kiến trúc, plan sprint, chạy Q10 + Q9, viết task card tự đủ (trích luật L liên quan + node được phép dùng) |
| **Sonnet** | Thực thi từng bước trong phiên hằng ngày; task card thiếu bảng Q9 / Q10 → từ chối, hỏi ngược |
| **Claude Code** | Phân phối doc, cross-check, liệt kê mâu thuẫn — **KHÔNG** tự sửa node flow / chữ ký hàm "cho khớp" khi không có ground truth |
| **cuhoang** | Quyết đánh đổi (thời gian, rủi ro, ưu tiên); verify bằng mắt / PIE; đưa K2 export khi cần |

Quyết định **kỹ thuật** → Claude quyết theo chuẩn ngành + công khai 1–2 dòng lý do. Quyết định **đánh đổi** → dịch sang tiếng đời ("hướng 1: 2 ngày chắc — hướng 2: 2 giờ, 30% làm lại") rồi cuhoang chọn.

## 3. Ba cổng trước khi code (khác tầng, không thay nhau)

```
 XÁC ĐỊNH PHẠM VI          LẬP TASK CARD                  VIẾT NODE
 ┌─────────────┐          ┌──────────────────────┐        ┌────────────────────────┐
 │ Q10         │   ──►    │ Q9  (nếu đụng        │  ──►   │ Q8  1 dòng VISIBLE:    │
 │ state này   │          │ SelectedActors)      │        │ Container | IsValid |  │
 │ ai GHI / ai │          │ bảng S0–S9 × X1–X10  │        │ L2 | No Latent | 6A    │
 │ ĐỌC khắp    │          │ ô trống = không hợp lệ│        │                        │
 │ project?    │          └──────────────────────┘        └────────────────────────┘
 └─────────────┘
```
- **Q10 bước 2:** mở [[Chỉ mục hàm & biến]] TRƯỚC (ai SET / GET biến, ở luồng nào, ✓K2 hay doc) → rồi search toàn project theo tên state (chỉ mục chỉ phủ luồng đã vẽ).
- **KP1** giả định tường minh (task có ≥2 cách hiểu → trình cả 2) · **KP2** không tự thêm feature / param ngoài yêu cầu · **KP3** sửa đúng chỗ, thấy rác thì báo, không tiện tay dọn.

## 4. Kiểm chứng — thấy tận mắt thắng suy luận

| Cách | Khi nào |
|---|---|
| **Test 1 phút bằng mắt / PIE** | Nghi 1 điều → nghĩ thao tác ngắn nhất trong editor để xác nhận, rồi mới kết luận |
| **K2 export** (chọn node → Ctrl+C → dán) | Logic rối, wire không rõ, cần nâng mũi tên đứt → liền. Dịch sang ▶→ / ●→ trong doc canonical, KHÔNG lưu raw |
| **Print String** trên đường exec chính | Debug giá trị, không đặt trong loop body |
| **Automation test C++** | Invariant quan trọng (Undo, ID) — xem [[18-09-2026_UndoArchitecture_Foundation_v1]] §6 |

Khi cả người lẫn AI cùng đoán mà chưa ai verify → **đi lấy bằng chứng**, không tranh luận ai đúng.

## 5. Gặp bug — quy trình

1. Hỏi triệu chứng cụ thể (lỗi gì, node nào, giá trị gì).
2. **Người debug đoán trước** ("mình nghĩ lỗi ở X vì Y") — sai cũng được, đối chiếu với bằng chứng.
3. Liệt kê 2–3 nguyên nhân khả dĩ, đối chiếu L1–L16 → đặt Print / xin K2 đúng đoạn nghi ngờ.
4. **Fail 3 lần → DỪNG**: chọn Plan B / thu hẹp phạm vi / gác lại. Không đoán mò lần 4.
5. Root cause + fix + test PASS → **đóng vòng**, không tự sinh nghi vấn mới khi chưa có triệu chứng mới.

## 6. "Xong" nghĩa là gì

- Chạy đúng cả **đường xuôi lẫn đường ngược** (6A) + regression các luồng dính state đó.
- Hỏi 1–2 câu **kiểm tra hiểu bài** sau mỗi tính năng — trả lời đúng mới tick [[Learning_System]].
- Cập nhật doc theo R-DOC: **ASBUILT** (kết quả thật vào doc canonical, không chỉ file plan) · **DONE** (tick khi chạy, bug còn treo tách entry [[Open_Bugs]]) · **ATOMIC** (1 ô = 1 việc) · **COUNT** (đếm lại, không tin số cũ).
- Lệch plan về logic / kiến trúc / phạm vi → ghi [[DEVIATIONS]] NGAY lúc lệch.
- Sơ đồ bị ảnh hưởng → sửa [[Architecture_Map]] rồi chạy `python Brain/_tools/build.py` (xem [[Tư duy 4 · Cách viết tài liệu trong bộ não|Tư duy 4]]).

### Nghi thức đóng task / đóng gate (R-DOC-CLOSE, 25/09/2026)
cuhoang chỉ nói **"đóng task"** hoặc **"đóng gate"** — AI tự chạy checklist, không bắt người nhớ.
```
"đóng task" → doc canonical as-built → Architecture_Map (5x + Phần 3) → Luồng Lxx
              → Open_Bugs / DEVIATIONS / Learning_System → build.py (❌⚠🔗 = 0) → báo file đổi → commit
"đóng gate" → + mở [[Kiểm tra bản đồ]] › 🧭 K2 cần xin khi đóng gate (chỉ Lxx gate đụng) → xin K2 → nâng liền
```
- K2 gửi lúc **xác nhận flow trong task** chính là bằng chứng ✓K2 — ghi ngay lúc đóng task, không đợi cuối gate.
- Nét liền chỉ khi có K2. PIE PASS vẫn là nét đứt.
- Lưới an toàn: git log (Blueprint đổi mà không có commit doc = lỗ hổng) · vòng 🧭 cuối gate · khi suy luận, phần "theo doc" là giả thuyết → xin K2 trước khi sửa code dựa trên nó.
- Chi tiết: [[Execution_Discipline]] mục R-DOC-CLOSE.

## 7. Giọng làm việc

Tiếng Việt, ngắn, bảng / gạch đầu dòng thay đoạn văn; tên node / class / biến giữ tiếng Anh; khái niệm mới kèm 1 ví dụ đời thường. Mỗi lượt 1 việc, kết bằng "làm xong báo" + cách test cụ thể. Chi tiết: [[AI_Communication_Rules]].

---
**Đọc tiếp:** [[Tư duy 4 · Cách viết tài liệu trong bộ não]] — ghi lại những gì đã làm sao cho người sau đọc được.
