# 10 — Kỷ Luật Thực Thi (Không bỏ cuộc, không đi lạc)
**Mục đích:** Cơ chế đảm bảo bám kế hoạch nhưng vẫn thích nghi được khi plan sai, không trôi dạt, không bỏ cuộc giữa chừng.

⚠️ Đọc file này cùng với 09. File 09 = cách code đúng. File 10 = cách KHÔNG đi lạc trong quá trình code.

---

## TRIẾT LÝ NỀN TẢNG

> **Kế hoạch là giả thuyết, không phải hợp đồng.**

Plan_v3 chắc chắn sai ở vài chỗ — đó là bình thường. Mục tiêu KHÔNG phải làm theo plan từng chữ, mà là:
1. Biết khi nào đang lệch khỏi plan
2. Lệch có chủ đích (ghi lại), không lệch vô thức
3. Cập nhật plan khi thực tế chứng minh plan sai

**Giá trị của plan = tư duy nó ép làm trước, không phải làm theo y nguyên.**

---

## 5 CƠ CHẾ CHỐNG ĐI LẠC

### CƠ CHẾ 1 — DEVIATION LOG (quan trọng nhất)

**Vấn đề giải quyết:** Trôi dạt vô thức. Mỗi lần làm khác plan mà không ghi → sau 10 lần không còn biết đang ở đâu.

**Cách làm:** Tạo file `DEVIATIONS.md` trong project. Mỗi lần làm khác plan → ghi 1 dòng:

```
| Ngày | Task | Plan nói | Thực tế làm | Lý do |
|------|------|----------|-------------|-------|
| 28/05 | S1.T3 Pivot | Tick mỗi frame | Tick + disable khi không drag | Performance máy yếu |
| 29/05 | S1.T7 | Ctrl check qua IA_Ctrl | Is Input Key Down(Ctrl) | IA_Ctrl chưa setup |
```

**Quy tắc:**
- Lệch nhỏ (tên biến, thứ tự node) → KHÔNG cần ghi
- Lệch về **logic/kiến trúc/scope** → BẮT BUỘC ghi
- Ghi NGAY lúc lệch, không để cuối ngày (sẽ quên)

**Lợi ích kép:**
- Cuối sprint nhìn lại: nếu 10+ deviation → plan phần đó sai → cập nhật plan
- Khi debug sau này: biết chỗ nào đã làm khác plan

---

### CƠ CHẾ 2 — VERTICAL SLICE TRƯỚC (Walking Skeleton)

**Vấn đề giải quyết:** Đi sai hướng quá xa. Xây 14 task hoàn hảo rồi mới phát hiện kiến trúc sai từ task 1.

**Cách làm:** Đầu mỗi sprint, làm **lát cắt dọc tối thiểu** chạy end-to-end TRƯỚC, rồi mới hoàn thiện.

**Ví dụ Sprint 1:**
```
❌ SAI: làm tuần tự T1→T14, mỗi cái hoàn hảo
   → đến T7 mới biết Pivot Actor không hoạt động → phí 6 task

✅ ĐÚNG: Vertical slice trước
   Ngày 1: Chọn 2 đồ (Ctrl+Click) → Move qua Pivot → Undo
            = chạm vào T1, T3, T4, T5, T7, T12 ở mức TỐI THIỂU
            → VALIDATE rủi ro lớn nhất (Pivot Actor) NGAY
   Nếu Pivot OK → ngày 2-7 hoàn thiện từng task
   Nếu Pivot HỎNG → chuyển Plan B (Risk doc) NGAY, chưa phí gì
```

**Nguyên tắc:** Chạm vào rủi ro lớn nhất sớm nhất. Rủi ro lớn nhất mỗi sprint:
- Sprint 1: Pivot Actor (gizmo multi-select)
- Sprint 3: EMS save group (BP_GroupsContainer)
- Sprint 5: Combo JSON serialize/deserialize round-trip

Làm 1 lát cắt nhỏ chứng minh rủi ro đó giải quyết được → rồi mới xây tiếp.

---

### CƠ CHẾ 3 — DEFINITION OF DONE (chống lược bớt)

**Vấn đề giải quyết:** Lược bớt để xong nhanh. "Để sau fix" → không bao giờ fix → nợ kỹ thuật chồng chất.

**Cách làm:** 1 task chỉ "xong" khi đủ 3 điều kiện:
```
✅ Test trong 07_Testing_Strategy.md PASS
✅ Không vi phạm L1-L10 (file 09)
✅ Hard ref clear ở End Play/Destruct (nếu có tạo ref)
```

**Phân biệt "lược bớt xấu" vs "thu hẹp scope tốt":**

| Lược bớt XẤU (cấm) | Thu hẹp scope TỐT (cho phép) |
|---|---|
| Bỏ IsValid check "cho nhanh" | Dời nested group sang v2 |
| Skip test "chắc ổn rồi" | Combo không auto-thumbnail, dùng icon generic |
| Không clear hard ref "lát nữa làm" | Smart Snap chỉ làm 2/5 loại trước |
| Hardcode path thay vì RowName | Bỏ Mirror Group, làm sau |

**Khác biệt:** Thu hẹp scope tốt = **quyết định có ý thức, ghi vào DEVIATIONS.md**. Lược bớt xấu = bỏ chất lượng lõi để xong cho nhanh.

⚠️ Mọi "thu hẹp scope" PHẢI ghi DEVIATIONS.md với lý do. Không ghi = lược bớt xấu.

---

### CƠ CHẾ 4 — STUCK PROTOCOL (chống cố đấm + chống bỏ cuộc)

**Vấn đề giải quyết:** Vừa chống "cố đấm ăn xôi 2 ngày 1 bug", vừa chống "bỏ cuộc khi khó".

**Quy tắc 3 lần:**
```
Bug/khó khăn:
  Thử cách 1 → fail
  Thử cách 2 → fail
  Thử cách 3 → fail
  → STOP. KHÔNG thử cách 4 ngay.
```

Khi chạm giới hạn 3 lần:
```
1. Ghi lại đã thử gì (tránh lặp)
2. Chọn 1 trong 3 hướng:
   a) Plan B trong 06_Risk_Mitigation.md (đã chuẩn bị sẵn)
   b) Thu hẹp scope task (ghi DEVIATIONS.md)
   c) Tạm gác task, làm task khác, quay lại sau (đầu óc tươi hơn)
3. KHÔNG: thử cách 4, 5, 6 liên tục → đó là đường dẫn tới bỏ cuộc
```

**Tại sao 3 lần:** Cố đấm sinh ra từ "thêm 1 lần nữa thôi" lặp vô hạn. Giới hạn cứng phá vòng lặp đó. Mỗi lần fail nghiêm túc tốn nhiều năng lượng — 3 lần là đủ để biết cách tiếp cận hiện tại sai, cần đổi hướng chứ không phải đổi chi tiết.

---

### CƠ CHẾ 5 — SPRINT REVIEW (checkpoint định kỳ)

**Vấn đề giải quyết:** Đi quá xa trước khi nhận ra lạc hướng.

**Cuối mỗi sprint (15-30 phút), làm 4 việc:**
```
1. REGRESSION: chạy Core Regression Suite (07) → tính năng cũ còn nguyên?
2. DEVIATION REVIEW: đọc DEVIATIONS.md sprint này
   → Nếu > 5 deviation lớn ở 1 vùng → plan vùng đó sai → cập nhật plan
3. PLAN CHECK: sprint kế tiếp còn hợp lý không?
   → Kiến trúc thực tế có khác giả định plan không?
   → Nếu có → sửa plan sprint kế TRƯỚC khi bắt đầu
4. CẬP NHẬT: Session_State.md + doc liên quan
```

**Đây là điểm bắt buộc dừng lại nhìn toàn cảnh.** Không có checkpoint = lao đầu 7 sprint rồi mới biết Sprint 3 đã lệch.

---

## CHỐNG BỎ CUỘC (yếu tố tâm lý)

Bỏ cuộc thường KHÔNG phải vì task quá khó, mà vì **mất động lực**. 3 cơ chế giữ động lực:

### M1 — Mỗi task = 1 chiến thắng nhỏ
Plan chia 79 task nhỏ có lý do: mỗi checkbox tick = cảm giác tiến bộ. Đừng gộp task lớn — chia nhỏ để thắng thường xuyên.

### M2 — Tiến độ nhìn thấy được
Giữ 1 file `PROGRESS.md` đơn giản:
```
Sprint 1: ████████░░ 8/14 task
Sprint 2: ░░░░░░░░░░ 0/8
...
```
Nhìn thanh tiến độ đầy dần = động lực.

### M3 — Nhịp bền vững, không sprint kiệt sức
- Làm 1-2 task/session, không ép 14 task 1 ngày
- Solo dev burnout là nguyên nhân #1 bỏ dự án giữa chừng
- Thà chậm mà đều, còn hơn nhanh rồi bỏ

---

## QUY TRÌNH KHI PLAN SAI (sẽ xảy ra)

```
Phát hiện plan sai ở task X:
  ↓
1. Dừng. Đừng làm theo plan sai cho "đúng kế hoạch"
  ↓
2. Đánh giá: sai nhỏ (1 task) hay sai hệ thống (nhiều task)?
  ↓
3a. Sai nhỏ → sửa cách làm, ghi DEVIATIONS.md, tiếp tục
3b. Sai hệ thống → STOP sprint, họp lại với AI:
    - Phần nào của plan còn đúng?
    - Phần nào cần thiết kế lại?
    - Cập nhật file plan_v3 liên quan
    - Rồi mới tiếp tục
  ↓
4. KHÔNG: cố làm theo plan sai vì "đã lên kế hoạch rồi"
   (sai lầm sunk-cost — plan là công cụ, không phải mục tiêu)
```

---

## FILE CẦN TẠO TRONG PROJECT

Ngoài plan_v3 (read-only reference), tạo 3 file sống:

| File | Vai trò | Cập nhật khi |
|---|---|---|
| `DEVIATIONS.md` | Ghi mọi lệch khỏi plan | Ngay lúc lệch |
| `PROGRESS.md` | Thanh tiến độ task | Cuối mỗi task |
| `Session_State.md` | Trạng thái + bug (đã có) | Cuối mỗi session |

---

## CHECKLIST KỶ LUẬT — DÁN TRƯỚC MẶT

**Mỗi session:**
- [ ] Đọc Session_State.md + task hiện tại trong 04
- [ ] Làm vertical slice trước nếu đầu sprint

**Mỗi task:**
- [ ] Làm khác plan? → ghi DEVIATIONS.md
- [ ] Bug 3 lần? → STOP, chọn Plan B / thu hẹp / gác lại
- [ ] Task xong? → Test pass + L1-L10 OK + clear ref → tick PROGRESS.md

**Mỗi sprint:**
- [ ] Regression suite pass?
- [ ] Đọc DEVIATIONS — plan có cần sửa không?
- [ ] Sprint kế còn hợp lý không?
- [ ] Cập nhật Session_State + doc

---

## TÓM TẮT TRIẾT LÝ

> **Plan để nghĩ trước, không để theo mù quáng.**
> **Lệch thì ghi (DEVIATIONS), khó thì giới hạn (3 lần), xa thì checkpoint (sprint review).**
> **Thắng nhỏ thường xuyên (79 task), nhịp bền vững (không kiệt sức).**
> **Sai lầm lớn nhất không phải plan sai — mà là làm theo plan sai vì tiếc công đã lập plan.**
