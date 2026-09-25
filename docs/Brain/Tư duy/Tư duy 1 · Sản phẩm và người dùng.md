# Tư duy 1 · Sản phẩm và người dùng

> ↑ [[Bản đồ não]] · Bộ Tư duy: **1 Sản phẩm** · [[Tư duy 2 · Kiến trúc và nguyên tắc code|2 Kiến trúc]] · [[Tư duy 3 · Cách làm việc và kiểm chứng|3 Cách làm việc]] · [[Tư duy 4 · Cách viết tài liệu trong bộ não|4 Cách viết tài liệu]]
> Viết 25/09/2026. Note này TÓM TẮT cách nghĩ và trỏ tới doc gốc — không thay doc gốc. Chốt khác đi thì sửa doc gốc trước, rồi sửa dòng tóm tắt ở đây.

**Dùng khi:** đề xuất / đánh giá 1 tính năng, đặt tên chữ trên giao diện, chọn làm gì trước, viết tiêu chí "xong".

---

## 1. Ai dùng tool (chốt 25/09/2026)

> **"Đại trà" = người có kỹ năng thiết kế và tư vấn nội thất tốt, dễ tiếp cận công nghệ.**
> KHÔNG phải người mù công nghệ · KHÔNG phải nhân viên FOFF — là người ngoài công ty: nhà thiết kế / tư vấn độc lập, studio nhỏ, người bán nội thất.

| Hệ quả | Nghĩa là |
|---|---|
| Giỏi nghề nội thất | Chữ trên giao diện nói bằng **ngôn ngữ nghề** (vật liệu, vùng vật liệu, bộ đồ, căn phòng) — không bằng ngôn ngữ engine (Actor, Slot index, Mesh path) |
| Dễ tiếp cận công nghệ | Chấp nhận phím tắt, kéo-thả, nhiều bảng — nhưng phải **tự khám phá được**, không cần học trước |
| Không phải dân Unreal | Mọi lỗi phải nói bằng hậu quả ("Chỉ áp vật liệu lên đồ nội thất"), không bằng log |
| Thường đã có máy chạy SketchUp / 3ds Max | Lo ngại phần cứng nhẹ hơn nhóm "người dùng bình thường" cũ — vẫn giữ [[Performance]] làm sàn |

> ⚠ [[Design]] mục "Đối tượng người dùng" và [[00_Master_Plan]] "Người dùng bình thường" được viết trước quyết định này — đã ghi chú đính chính ở đầu 2 doc đó.
> Persona giả thuyết P1/P2/P3, empathy map, 16 vấn đề F1–F16: [[25-09-2026_Product_UX_Review_Plan_v1]] (CHƯA kiểm chứng với người thật).

## 2. Họ "thuê" tool làm 3 việc (Jobs-to-be-done)

1. Khi khách còn phân vân → **cho khách THẤY** phương án khác trong 1 phút.
2. Khi khách chịu → **mang về** thứ gì đó: ảnh đẹp, danh sách đồ, giá.
3. Khi làm sai → **quay lại ngay**, không ai nhận ra (Undo tin được).

Tính năng nào không đẩy 1 trong 3 việc này → hỏi lại vì sao làm.

## 3. Soi 1 tính năng qua 5 góc nhìn (bắt buộc khi đề xuất / đánh giá)

| Góc nhìn | Câu hỏi phải trả lời |
|---|---|
| **Nghiên cứu người dùng** (persona, empathy map) | Ai dùng, lúc nào, đang nghĩ / sợ gì? Việc nào trong 3 việc trên? |
| **Phản biện khó tính** | Điều gì ta đang đoán mà chưa ai kiểm? Người ngoài team đã thử chưa? |
| **Tâm lý hành vi** | Vi phạm nguyên tắc nào ở mục 4? Người dùng sẽ hiểu sai ở đâu? |
| **PM / khách hàng khó tính** | Ai trả tiền cho cái này? Đo "thành công" bằng gì? Cái gì KHÔNG làm? |
| **Cộng sự ý tưởng** | Có cách nào rẻ hơn 10 lần mà được 80%? Xếp ICE (Impact × Confidence × Ease) |

## 4. 8 nguyên tắc tâm lý — kèm ví dụ ngay trong tool

| Mã | Nguyên tắc | Ví dụ đúng trong tool | Ví dụ còn nợ |
|---|---|---|---|
| **LA** | Sợ mất hơn thích được (loss aversion) | Undo 50 bước, Replace combo lỗi tự khôi phục cụm cũ | Chưa có autosave (F1) |
| **VS** | Luôn cho thấy hệ thống đang làm gì | Toast "Áp cho N/N đồ", viền trắng khi chọn | Lỗi âm thầm: Lưu combo khi < 2 món không báo gì (F4) |
| **RR** | Nhận ra dễ hơn nhớ lại | Thẻ có ảnh, ô slot có ảnh vật liệu | Thanh công cụ chỉ có icon (F12) |
| **HL** | Càng nhiều lựa chọn càng chậm quyết | Phân trang 48 thẻ, lọc theo thư mục | 4 nút Reset khác nhau (F9) |
| **FL** | Mục tiêu to + gần thì bấm nhanh | Kéo thẻ thẳng vào phòng | Cửa sổ che ~40% màn hình (F14) |
| **PE** | Người ta nhớ đỉnh và kết thúc | Thả chuột = 1 mốc, Ctrl+Z hoàn tác cả cú kéo | Chưa có "mang về" cuối buổi: ảnh / báo giá (F16) |
| **PS** | An toàn tâm lý = dám thử | Mọi thao tác đổi cảnh đều Undo được | Undo làm mất slot đang chọn (U3, F6) |
| **MM** | Khớp mô hình trong đầu người dùng | "Nhóm", "Combo", "Vào nhóm" giống phần mềm thiết kế quen thuộc | Header hiện `BP_FurnitureActor_C_0` (F11) |

## 5. Nguyên tắc UX / UI đã chốt

- Mọi thao tác **phản hồi ngay** (< 1 giây), xem trước trực tiếp, không nút Apply riêng — [[Design]].
- **1 state = 1 control chuẩn + nhiều hiển thị chỉ-đọc.** Ví dụ: dải swatch là control DUY NHẤT chọn slot; breadcrumb / highlight chỉ là hiển thị.
- **Bảng thuộc tính (property surface), không phải hộp thoại:** không OK/Cancel, sửa là thấy ngay, nút X chỉ đóng bảng (không mang nghĩa huỷ), luôn nói rõ "đang chỉnh cái gì", không tự đoán selection.
- **Không tự chọn hộ người dùng** (vd Inspector không tự chọn slot 0 — người dùng tưởng đang sửa cả món).
- **Hướng UI dài hạn: Docking Workspace** (kiểu Unreal Editor) — widget chỉ lo hiển thị, logic nằm ở controller; giao tiếp giữa bảng qua Function / Dispatcher, không đọc thẳng cây widget của nhau. Dựng docking để Polish sau; boundary phải sạch từ bây giờ.
- Ghost preview khi kéo, snap bật sẵn, reset luôn có sẵn, kích thước hiển thị bằng cm.

## 6. Chỉ số cho bản đầu (đề xuất, đo ở phase test người thật)

| Chỉ số | Mục tiêu |
|---|---|
| Mở tool → phòng có ≥5 món + 1 lần đổi vật liệu + lưu | ≤ 10 phút với người mới |
| Làm xong nhiệm vụ trong kịch bản test | ≥ 4/5 mỗi người |
| Ổn định | 0 crash, 0 lần "đơ" trong 30 phút |
| SUS | ≥ 68 |

## 7. Việc kinh doanh (bối cảnh, chưa chốt)

Tầm nhìn: furniture tool → thư viện cloud → **combo mesh (doanh thu chính)** → đồ tương tác. Thỏa thuận thương mại combo với đồng nghiệp **chưa chốt** — làm rõ trước khi tính kiếm tiền. Nguồn: [[00_Master_Plan]] "Triết lý thiết kế", [[25-09-2026_Product_UX_Review_Plan_v1]] mục 4–6.

---
**Đọc tiếp:** [[Tư duy 2 · Kiến trúc và nguyên tắc code]] — sản phẩm muốn vậy thì bên trong phải xây thế nào.
