# 10 — Kỷ Luật Thực Thi — PATCH v2
**Phiên bản:** 2.0 | **Cập nhật:** 14/06/2026 — (điền giờ:phút ICT khi apply)
**Patch từ bản gốc (10_Execution_Discipline.md). Bổ sung CƠ CHẾ 6 + cập nhật Definition of Done + checklist.**
> File này THÊM luật mới. Phần Cơ chế 1–5 và phần tâm lý giữ nguyên.

---

## ⭐ CƠ CHẾ 6 — ĐỐI XỨNG THAO TÁC (chống thiết kế một chiều)

**Vấn đề giải quyết:** Feature làm theo MỘT chiều thao tác, quên chiều còn lại. Đẻ ra cấu trúc/hành vi bất nhất mà người dùng tự nhiên sẽ vấp phải khi thao tác ngẫu nhiên.

Đây là loại lỗi nguy hiểm vì **nó không hiện ra trong test theo plan** — plan thường chỉ đi đúng con đường người code nghĩ tới. Người dùng thật đi con đường khác → ra kết quả khác → lỗi.

### LUẬT 6A — Cặp Forward + Backward bắt buộc

> Mỗi feature, Definition of Done phải gồm **cả chiều xuôi lẫn chiều ngược**.
> Không định nghĩa được đường ngược (làm sao gỡ / hoàn tác / tháo ra) thì feature **chưa xong**, không tính done.

Ví dụ cặp xuôi–ngược phải nghĩ đủ:
| Chiều xuôi | Chiều ngược phải có |
|---|---|
| Group nhiều đồ | Ungroup → đồ về đúng trạng thái trước |
| Enter edit mode | Exit edit → selection/visual phục hồi đúng |
| Spawn vào group đang edit | Xóa/undo → group không vỡ |
| Combo đóng gói nhánh cây | Mở combo → tái tạo đúng nhánh cây ban đầu |

> ⚠ Đây KHÔNG chỉ là undo/redo. Undo/redo là một dạng của chiều ngược. Nhưng "chiều ngược" rộng hơn: là mọi cách người dùng tháo/đảo/gỡ thao tác bằng chính các nút trong tool.

### LUẬT 6B — Đối xứng cấu trúc (nhiều đường, cùng kết quả)

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
Cùng cái cây mong muốn, hai cách làm, hai kết quả → **vi phạm đối xứng cấu trúc**.

**Root cause kiểu này:** function làm việc ở SAI cấp — gom *actor (lá)* thay vì gom *đơn vị chọn (group/actor rời)*. Khi nghi ngờ đối xứng, hỏi: *"Function này đang thao tác ở cấp lá hay cấp đơn vị?"*

### Cách kiểm khi làm feature cấu trúc (group/combo/nesting/parent-child)

Trước khi tick done, liệt kê **mọi đường người dùng có thể tạo ra cấu trúc X**, rồi chạy thử từng đường:
1. Top-down (tạo cha trước, thêm con vào trong)
2. Bottom-up (tạo con trước, gom lại thành cha)
3. Trộn (vài đơn vị đã nhóm + vài đồ rời, gom chung)
4. Trong edit scope vs ngoài edit scope

Tất cả đường phải ra **cùng cấu trúc**. Đường nào lệch = bug, fix trước khi done.

---

## CẬP NHẬT — DEFINITION OF DONE (Cơ chế 3)

Bổ sung điều kiện 4 và 5 vào checklist "task xong":
```
✅ Test trong 07_Testing_Strategy.md PASS
✅ Không vi phạm L1-L10 (file 09)
✅ Hard ref clear ở End Play/Destruct (nếu có tạo ref)
✅ [MỚI] Có đường NGƯỢC, đã test (Luật 6A)
✅ [MỚI] Nếu là feature cấu trúc: mọi đường thao tác cho cùng kết quả (Luật 6B)
```

---

## CẬP NHẬT — CHECKLIST KỶ LUẬT (mỗi task)

```
- [ ] Làm khác plan? → ghi DEVIATIONS.md
- [ ] Bug 3 lần? → STOP, chọn Plan B / thu hẹp / gác lại
- [ ] Có đường NGƯỢC chưa? (Luật 6A) → chưa có = chưa done
- [ ] Feature cấu trúc? → test đủ đường xuôi/ngược/trộn (Luật 6B)
- [ ] Task xong? → Test pass + L1-L10 OK + clear ref → tick PROGRESS.md
```

---

## CẬP NHẬT — TÓM TẮT TRIẾT LÝ (thêm 1 dòng)

> **Một feature chỉ xong khi cả chiều xuôi lẫn chiều ngược đều đúng,**
> **và mọi đường thao tác dẫn tới cùng cấu trúc đều cho cùng kết quả.**

---

## Lịch sử cập nhật (file 10)
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | (gốc) | 5 cơ chế chống đi lạc + chống bỏ cuộc |
| 2.0 | 14/06/2026 | **Cơ chế 6 — Đối xứng thao tác:** Luật 6A (cặp forward+backward bắt buộc trong DoD), Luật 6B (đối xứng cấu trúc — nhiều đường cùng kết quả). Cập nhật Definition of Done (+2 điều kiện), checklist mỗi-task, tóm tắt triết lý. Nguồn: bug CreateGroup bottom-up không nest (14/06). |
