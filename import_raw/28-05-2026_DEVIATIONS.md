# DEVIATIONS LOG — Lệch khỏi Plan v3
**Mục đích:** Ghi mọi lần làm KHÁC plan về logic/kiến trúc/scope. Biến trôi dạt vô thức thành thích nghi có kiểm soát.

---

## CÁCH DÙNG

- **Lệch nhỏ** (tên biến, thứ tự node, vị trí widget) → KHÔNG cần ghi
- **Lệch về logic/kiến trúc/scope** → BẮT BUỘC ghi 1 dòng
- Ghi **NGAY lúc lệch**, không để cuối ngày (sẽ quên)
- Cuối mỗi sprint: đọc lại. Nếu 1 vùng có > 5 deviation → plan vùng đó sai → cập nhật plan_v3

**Phân loại lý do:**
- `[PLAN-SAI]` — plan sai, thực tế đúng hơn → cần sửa plan
- `[SCOPE]` — thu hẹp scope có chủ đích, dời sang sau
- `[NODE]` — node UE5 khác plan giả định
- `[PERF]` — đổi vì hiệu năng
- `[BUG]` — đổi để fix bug phát sinh

---

## SPRINT 1 — Multi-select

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| | | | | | |

---

## SPRINT 2 — Box Select + Context Menu

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| | | | | | |

---

## SPRINT 3 — Group cơ bản

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| | | | | | |

---

## SPRINT 4 — Edit Mode + Nested

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| | | | | | |

---

## SPRINT 5 — Combo Mesh

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| | | | | | |

---

## SPRINT 6 — Polish UX

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| | | | | | |

---

## SPRINT 7 — Material Edit v1.2

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| | | | | | |

---

## TỔNG KẾT CUỐI SPRINT (điền sau mỗi sprint review)

### Sprint 1
- Số deviation: __
- Vùng nhiều deviation nhất: __
- Plan cần sửa: __

### Sprint 2
- Số deviation: __
- Plan cần sửa: __

(... các sprint sau tương tự)

---

## VÍ DỤ (xóa khi bắt đầu thật)

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| 28/05 | S1.T3 | Pivot Tick mỗi frame | Tick + disable khi không drag | Giảm tải máy yếu | [PERF] |
| 29/05 | S1.T7 | Ctrl check qua IA_Ctrl chord | Is Input Key Down(Left Ctrl) | IA_Ctrl chưa setup, dùng cách đơn giản hơn | [NODE] |
| 30/05 | S4 | Nested 3 cấp | Chỉ làm 1 cấp, dời nested v2 | Edit mode phức tạp, ưu tiên ship | [SCOPE] |
