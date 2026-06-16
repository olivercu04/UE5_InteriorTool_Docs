# 10 — Kỷ Luật Thực Thi (Không bỏ cuộc, không đi lạc)
**Nguồn:** `import_raw/28-05-2026_10_Execution_Discipline.md` (base v1.0) + `import_raw/10_Execution_Discipline_patch_v2.md` (v2.0, 14/06/2026)
**Phiên bản:** 2.0 | **Cập nhật:** 14/06/2026
**Mục đích:** Cơ chế đảm bảo bám kế hoạch nhưng vẫn thích nghi được khi plan sai, không trôi dạt, không bỏ cuộc giữa chừng.

⚠️ Đọc file này cùng với `Rules/AI_Implementation_Rules.md`. File 09 = cách code đúng. File 10 = cách KHÔNG đi lạc trong quá trình code.

---

## TRIẾT LÝ NỀN TẢNG

> **Kế hoạch là giả thuyết, không phải hợp đồng.**

Plan chắc chắn sai ở vài chỗ — đó là bình thường. Mục tiêu KHÔNG phải làm theo plan từng chữ, mà là:
1. Biết khi nào đang lệch khỏi plan
2. Lệch có chủ đích (ghi lại), không lệch vô thức
3. Cập nhật plan khi thực tế chứng minh plan sai

**Giá trị của plan = tư duy nó ép làm trước, không phải làm theo y nguyên.**

---

## 6 CƠ CHẾ CHỐNG ĐI LẠC

### CƠ CHẾ 1 — DEVIATION LOG (quan trọng nhất)

**Vấn đề giải quyết:** Trôi dạt vô thức. Mỗi lần làm khác plan mà không ghi → sau 10 lần không còn biết đang ở đâu.

**Cách làm:** File `00_Core/DEVIATIONS.md`. Mỗi lần làm khác plan → ghi 1 dòng:

```
| Ngày | Task | Plan nói | Thực tế làm | Lý do |
|------|------|----------|-------------|-------|
| 28/05 | S1.T3 Pivot | Tick mỗi frame | Tick + disable khi không drag | Performance máy yếu |
```

**Quy tắc:**
- Lệch nhỏ (tên biến, thứ tự node) → KHÔNG cần ghi
- Lệch về **logic/kiến trúc/scope** → BẮT BUỘC ghi
- Ghi NGAY lúc lệch, không để cuối ngày (sẽ quên)

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
   → VALIDATE rủi ro lớn nhất NGAY
   Nếu OK → ngày 2-7 hoàn thiện từng task
   Nếu HỎNG → chuyển Plan B NGAY, chưa phí gì
```

**Nguyên tắc:** Chạm vào rủi ro lớn nhất sớm nhất.
- Sprint 1: Pivot Actor (gizmo multi-select)
- Sprint 3: EMS save group (BP_GroupsContainer)
- Sprint 5: Combo JSON serialize/deserialize round-trip

---

### CƠ CHẾ 3 — DEFINITION OF DONE (chống lược bớt)

**Vấn đề giải quyết:** Lược bớt để xong nhanh. "Để sau fix" → không bao giờ fix → nợ kỹ thuật.

**Cách làm:** 1 task chỉ "xong" khi đủ 5 điều kiện (v2.0):
```
✅ Test trong Planning/07_Testing_Strategy.md PASS
✅ Không vi phạm L1-L10 (AI_Implementation_Rules.md)
✅ Hard ref clear ở End Play/Destruct (nếu có tạo ref)
✅ [v2.0] Có đường NGƯỢC, đã test (Luật 6A)
✅ [v2.0] Nếu là feature cấu trúc: mọi đường thao tác cho cùng kết quả (Luật 6B)
```

**Phân biệt "lược bớt xấu" vs "thu hẹp scope tốt":**

| Lược bớt XẤU (cấm) | Thu hẹp scope TỐT (cho phép) |
|---|---|
| Bỏ IsValid check "cho nhanh" | Dời nested group sang v2 |
| Skip test "chắc ổn rồi" | Combo không auto-thumbnail, dùng icon generic |
| Không clear hard ref "lát nữa làm" | Smart Snap chỉ làm 2/5 loại trước |

⚠️ Mọi "thu hẹp scope" PHẢI ghi DEVIATIONS.md với lý do.

---

### CƠ CHẾ 4 — STUCK PROTOCOL (chống cố đấm + chống bỏ cuộc)

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
   a) Plan B trong Planning/06_Risk_Mitigation.md
   b) Thu hẹp scope task (ghi DEVIATIONS.md)
   c) Tạm gác task, làm task khác, quay lại sau
3. KHÔNG: thử cách 4, 5, 6 liên tục
```

---

### CƠ CHẾ 5 — SPRINT REVIEW (checkpoint định kỳ)

**Cuối mỗi sprint (15-30 phút), làm 4 việc:**
```
1. REGRESSION: chạy Core Regression Suite (07) → tính năng cũ còn nguyên?
2. DEVIATION REVIEW: đọc DEVIATIONS.md sprint này
   → Nếu > 5 deviation lớn ở 1 vùng → plan vùng đó sai → cập nhật plan
3. PLAN CHECK: sprint kế tiếp còn hợp lý không?
4. CẬP NHẬT: 00_Core/01_Session_State.md + doc liên quan
```

---

### ⭐ CƠ CHẾ 6 — ĐỐI XỨNG THAO TÁC (v2.0, chống thiết kế một chiều)

**Vấn đề giải quyết:** Feature làm theo MỘT chiều thao tác, quên chiều còn lại. Đây là loại lỗi nguy hiểm vì **nó không hiện ra trong test theo plan** — plan thường chỉ đi đúng con đường người code nghĩ tới.

#### LUẬT 6A — Cặp Forward + Backward bắt buộc

> Mỗi feature, Definition of Done phải gồm **cả chiều xuôi lẫn chiều ngược**.
> Không định nghĩa được đường ngược (làm sao gỡ / hoàn tác / tháo ra) thì feature **chưa xong**, không tính done.

Ví dụ cặp xuôi–ngược phải nghĩ đủ:
| Chiều xuôi | Chiều ngược phải có |
|---|---|
| Group nhiều đồ | Ungroup → đồ về đúng trạng thái trước |
| Enter edit mode | Exit edit → selection/visual phục hồi đúng |
| Spawn vào group đang edit | Xóa/undo → group không vỡ |
| Combo đóng gói nhánh cây | Mở combo → tái tạo đúng nhánh cây ban đầu |

> ⚠️ "Chiều ngược" rộng hơn undo/redo: là mọi cách người dùng tháo/đảo/gỡ thao tác bằng chính các nút trong tool.

#### LUẬT 6B — Đối xứng cấu trúc (nhiều đường, cùng kết quả)

> Mọi đường thao tác dẫn tới **cùng một cấu trúc mong muốn** phải cho **cùng một kết quả**.

**Ví dụ kinh điển (bug 14/06 — CreateGroup bottom-up):**
```
Đường xuôi (top-down):
  A (10 đồ) → enter edit → tạo A-1, A-2, A-3 bên trong
  → A chứa 3 sub-group ✓

Đường ngược (bottom-up):
  Tạo A-1, A-2, A-3 trước → chọn cả 3 → Create Group
  → KỲ VỌNG: A chứa 3 sub-group
  → THỰC TẾ (lỗi): A phẳng, 10 đồ, không sub-group ✗
```

**Root cause kiểu này:** function làm việc ở SAI cấp — gom *actor (lá)* thay vì gom *đơn vị chọn (group/actor rời)*.

**Cách kiểm khi làm feature cấu trúc (group/combo/nesting/parent-child):**

Trước khi tick done, liệt kê **mọi đường người dùng có thể tạo ra cấu trúc X**, rồi chạy thử từng đường:
1. Top-down (tạo cha trước, thêm con vào trong)
2. Bottom-up (tạo con trước, gom lại thành cha)
3. Trộn (vài đơn vị đã nhóm + vài đồ rời, gom chung)
4. Trong edit scope vs ngoài edit scope

---

## CHỐNG BỎ CUỘC (yếu tố tâm lý)

### M1 — Mỗi task = 1 chiến thắng nhỏ
Plan chia task nhỏ có lý do: mỗi checkbox tick = cảm giác tiến bộ.

### M2 — Tiến độ nhìn thấy được
Giữ `00_Core/PROGRESS.md` với thanh tiến độ.

### M3 — Nhịp bền vững, không sprint kiệt sức
- Làm 1-2 task/session, không ép 14 task 1 ngày
- Solo dev burnout là nguyên nhân #1 bỏ dự án giữa chừng

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
    - Cập nhật file Planning/ liên quan
  ↓
4. KHÔNG: cố làm theo plan sai vì "đã lên kế hoạch rồi" (sunk-cost)
```

---

## FILE CẦN TẠO TRONG PROJECT

| File | Vai trò | Cập nhật khi |
|---|---|---|
| `00_Core/DEVIATIONS.md` | Ghi mọi lệch khỏi plan | Ngay lúc lệch |
| `00_Core/PROGRESS.md` | Thanh tiến độ task | Cuối mỗi task |
| `00_Core/01_Session_State.md` | Trạng thái + bug | Cuối mỗi session |

---

## CHECKLIST KỶ LUẬT

**Mỗi session:**
- [ ] Đọc `00_Core/01_Session_State.md` + task hiện tại trong Planning/04
- [ ] Làm vertical slice trước nếu đầu sprint

**Mỗi task:**
- [ ] Làm khác plan? → ghi `00_Core/DEVIATIONS.md`
- [ ] Bug 3 lần? → STOP, chọn Plan B / thu hẹp / gác lại
- [ ] Có đường NGƯỢC chưa? (Luật 6A) → chưa có = chưa done
- [ ] Feature cấu trúc? → test đủ đường xuôi/ngược/trộn (Luật 6B)
- [ ] Task xong? → Test pass + L1-L10 OK + clear ref → tick `00_Core/PROGRESS.md`

**Mỗi sprint:**
- [ ] Regression suite pass?
- [ ] Đọc DEVIATIONS — plan có cần sửa không?
- [ ] Sprint kế còn hợp lý không?
- [ ] Cập nhật Session_State + doc

---

## TÓM TẮT TRIẾT LÝ

> **Plan để nghĩ trước, không để theo mù quáng.**
> **Lệch thì ghi (DEVIATIONS), khó thì giới hạn (3 lần), xa thì checkpoint (sprint review).**
> **Thắng nhỏ thường xuyên, nhịp bền vững (không kiệt sức).**
> **Một feature chỉ xong khi cả chiều xuôi lẫn chiều ngược đều đúng,**
> **và mọi đường thao tác dẫn tới cùng cấu trúc đều cho cùng kết quả.**

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 28/05/2026 | 5 cơ chế chống đi lạc + chống bỏ cuộc |
| 2.0 | 14/06/2026 | Cơ chế 6 — Đối xứng thao tác: Luật 6A (forward+backward), Luật 6B (đối xứng cấu trúc). Definition of Done +2 điều kiện. Nguồn: bug CreateGroup bottom-up không nest (14/06). |
