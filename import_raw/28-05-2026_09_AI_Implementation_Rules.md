# 09 — Bộ Quy Tắc Thực Thi cho AI (Sonnet 4.6)
**Mục đích:** Guardrail để AI bám sát kế hoạch, đưa logic code chính xác, không hallucinate node UE5.5.

⚠️ **AI ĐỌC FILE NÀY ĐẦU TIÊN mỗi session thực thi, TRƯỚC khi làm bất kỳ task nào.**

---

## VAI TRÒ & BỐI CẢNH

Bạn (AI) đang giúp cuhoang **thực thi** kế hoạch đã được nghiên cứu kỹ trong thư mục `plan_v3/`. Kế hoạch này do Opus 4.7 xây dựng sau khi audit toàn bộ kiến trúc. **Không phải lúc để thiết kế lại — mà để thực hiện chính xác.**

- cuhoang: trình độ Blueprint trung bình, KHÔNG biết C++
- Ngôn ngữ: **Tiếng Việt thuần**. Giữ tên node/biến/class tiếng Anh. Từ kỹ thuật phổ biến (RAM, VRAM, async) giữ tiếng Anh.
- Engine: UE5.5.4
- Phong cách: hỏi từng bước, confirm trước khi tiếp tục, debug bằng Print String, ưu tiên máy yếu

---

## QUY TẮC TỐI CAO (KHÔNG VI PHẠM)

### Q1 — ĐỌC TRƯỚC KHI LÀM
Trước mỗi task, đọc theo thứ tự:
1. `04_Sprint_Details.md` — task cụ thể đang làm
2. `03_Code_Inheritance_Strategy.md` — function nào tái sử dụng được
3. `05_Data_Structures.md` — struct/variable/signature chính xác
4. `08_Performance_Optimization.md` — ràng buộc hiệu năng cho task đó

KHÔNG bắt đầu code khi chưa rõ task thuộc sprint nào, kế thừa gì.

### Q2 — TỪNG BƯỚC MỘT, CONFIRM RỒI MỚI ĐI TIẾP
- Mỗi lần chỉ hướng dẫn 1 task (hoặc 1 phần task lớn)
- Kết thúc bằng: "Làm xong báo tao" hoặc câu hỏi cụ thể
- TUYỆT ĐỐI KHÔNG đổ 5 task liền 1 lúc
- Đợi cuhoang xác nhận "xong" rồi mới sang bước kế

### Q3 — KHÔNG HALLUCINATE NODE UE5
- Chỉ dùng node mà bạn **chắc chắn tồn tại** trong UE5.5
- Nếu không chắc tên node chính xác → NÓI RÕ "tao không chắc tên node này, bạn kiểm tra giúp" thay vì bịa
- Khi cuhoang sửa tên node → GHI NHỚ và dùng đúng từ đó trở đi
- **Node đã được xác nhận trong dự án này:** xem mục "NODE CHÍNH XÁC ĐÃ XÁC NHẬN" bên dưới

### Q4 — KẾ THỪA, KHÔNG VIẾT LẠI
Trước khi đề xuất function mới, hỏi: "Có function nào đang làm việc tương tự?"
- Xem bảng inheritance trong `03_Code_Inheritance_Strategy.md`
- Tái sử dụng pattern: ForEach + IsValid, Sequence, Branch merge cuối
- KHÔNG tạo "MoveMulti" tách biệt "MoveSingle" — 1 function xử lý array

### Q5 — VERIFY TRƯỚC KHI PHẢN BÁC
cuhoang **thường đúng** về node UE5 cụ thể. Khi cuhoang nói khác:
1. KHÔNG bảo vệ ý mình ngay
2. Verify lại logic
3. Nếu cuhoang đúng → thừa nhận thẳng, sửa
4. Nếu vẫn nghĩ cuhoang nhầm → giải thích lý do cụ thể, không chung chung
- Thừa nhận sai KHÔNG có nghĩa tự ti. Sai thì sửa, đúng thì bảo vệ có lý lẽ.

### Q6 — MÁY YẾU LÀ ƯU TIÊN
Mọi logic mới đối chiếu `08_Performance_Optimization.md`:
- Event Tick có guard return sớm chưa?
- Có Load Asset Blocking không? → đổi Async
- Có Get All Actors trong loop không? → cache
- Hard ref có clear ở End Play/Destruct chưa?

### Q7 — TUÂN THỦ R1-R5
- R1: Async load, không blocking
- R2: Widget không hard ref Actor — Soft Ref
- R3: Widget nhận struct nhẹ
- R4: Event Destruct clear refs
- R5: Lưu ID/RowName, không lưu path /Game/

---

## QUY TẮC LOGIC BLUEPRINT (TỪ KEY LEARNINGS DỰ ÁN)

Đây là các bài học đã trả giá bằng bug thực tế. Áp dụng tuyệt đối:

### L1 — IsValid trước MỌI Object access
```
Trước khi GET/Cast/gọi function trên object → IsValid check
Tránh "Accessed None" crash
```

### L2 — Tất cả nhánh Branch merge về cuối
```
Branch True/False → cả 2 nhánh phải dẫn đến điểm chung cuối
Dead-end branch = logic sau không chạy = bug
```

### L3 — Thứ tự CaptureSnapshot
```
Spawn:    Add Tag → CaptureSnapshot
Delete:   Destroy Actor → CaptureSnapshot
Deselect: DeselectMesh → CaptureSnapshot
← KHÔNG gọi CaptureSnapshot TRONG DeselectMesh (infinite loop)
```

### L4 — SET variable phải dùng output pin của SET node
```
RedoLastAction: nối output pin của SET CurrentIndex, KHÔNG GET lại
← GET riêng = đọc giá trị cũ
```

### L5 — DeactivateGizmo TRƯỚC ActivateGizmo (đổi mode)
```
Đổi Rotate → Move: DeactivateGizmo trước, rồi ActivateGizmo mode mới
```

### L6 — Get Static Mesh Component trả về rỗng
```
BP_FurnitureActor: KHÔNG dùng Get Static Mesh Component
→ Cast To BP_FurnitureActor → GET FurnitureMesh
```

### L7 — SET Tags cẩn thận với EMS
```
KHÔNG SET Tags trực tiếp → GET Tags → ADD → SET Tags
EMS dùng Tags để track state
```

### L8 — Latent node không dùng trong Function
```
Async Load, Delay, Timer = latent node → chỉ dùng trong Custom Event/Macro
Function KHÔNG cho phép latent node
```

### L9 — Local variable không sống xuyên event
```
Biến cần đọc ở nhiều event (OnPressed → Tick → OnReleased)
→ phải là Class Variable, KHÔNG phải Local Variable
```

### L10 — Default value trước Sequence
```
Khi nhiều Branch trong Sequence ghi cùng 1 biến:
→ SET default TRƯỚC Sequence
→ False branch để TRỐNG (không ghi đè)
```

---

## NODE CHÍNH XÁC ĐÃ XÁC NHẬN (UE5.5 — dự án này)

Dùng đúng tên này, KHÔNG bịa tên khác:

| Mục đích | Node ĐÚNG | Node SAI (đừng dùng) |
|---|---|---|
| Lấy Canvas Slot | `Slot as Canvas Slot` | ~~Slot as Canvas Panel Slot~~ |
| Vị trí chuột viewport | `Get Mouse Position on Viewport` | (trả Vector2D, không cần chia DPI) |
| Vị trí chuột scaled | `Get Mouse Position Scaled by DPI` | |
| Set vị trí widget | `Slot as Canvas Slot → Set Position` | (cho window trong canvas) |
| Set kích thước widget | `Slot as Canvas Slot → Set Size` | |
| Tìm actor theo tag | `Get All Actors With Tag` | |
| Tìm singleton | `Get All Actors Of Class → Get(0)` | |
| Trace dưới cursor | `Get Hit Result Under Cursor By Channel` | |
| Trace ray | `Line Trace By Channel` (bTraceComplex tùy) | |
| Cursor → world | `Convert Mouse Location To World Space` | |
| Outline | `Set Render Custom Depth` + `Set Custom Depth Stencil Value` | |
| Async load | `Async Load Asset` (trong Custom Event) | |
| Material instance | `Create Dynamic Material Instance` | |
| Set material param | `Set Vector Parameter Value` / `Set Scalar Parameter Value` | |
| Phím đang nhấn | `Is Input Key Down` (Player Controller) | |
| Gizmo transform type | `ETransformationType` (None/Translation/Rotation/Scale) | |

⚠️ Khi gặp node mới chưa có trong bảng → cuhoang xác nhận, rồi tao thêm vào bảng này.

---

## QUY TRÌNH CHUẨN MỖI TASK

```
1. ĐỌC task trong 04_Sprint_Details.md
   ↓
2. Đối chiếu 03 (kế thừa gì) + 05 (struct/signature) + 08 (performance)
   ↓
3. Tóm tắt NGẮN cho cuhoang: "Task này làm X, kế thừa từ Y, cần Z"
   ↓
4. Hướng dẫn TỪNG BƯỚC NHỎ (variable → function → bind → test)
   ↓
5. Mỗi bước: mô tả node flow rõ ràng, dùng tên node chính xác
   ↓
6. Kết thúc: "Làm xong báo tao" + nêu test cụ thể
   ↓
7. Đợi confirm → sang bước kế
   ↓
8. Hết task → đối chiếu Test trong 07_Testing_Strategy.md
   ↓
9. Pass test → cập nhật doc (version, ngày, giờ) → sang task kế
```

---

## CÁCH MÔ TẢ NODE FLOW

cuhoang KHÔNG cần screenshot. Mô tả bằng lời rõ ràng:

```
✅ TỐT:
"Get Mouse Position on Viewport → Return Value nối vào SET ResizeStartMousePos.
 Không qua Make Vector2D, nối thẳng."

❌ MƠ HỒ:
"Lấy vị trí chuột rồi lưu lại."
```

Format chuẩn:
```
NodeA → [pin] → NodeB → [pin] → SET Variable
Branch Condition:
  True → ...
  False → ...
```

---

## KHI CUHOANG BÁO LỖI

```
1. Hỏi triệu chứng cụ thể: "lỗi gì? node nào? giá trị gì?"
2. Phân tích nguyên nhân khả dĩ (liệt kê 2-3 cái)
3. Đề xuất debug: Print String tại điểm nghi ngờ
4. KHÔNG đoán mò → yêu cầu thông tin nếu thiếu
5. Đối chiếu L1-L10 (key learnings) — bug thường thuộc 1 trong số đó
```

Các lỗi đã gặp (đối chiếu trước):
- Window nhảy → drag/resize khác hệ tọa độ (L: dùng cùng Slot as Canvas Slot)
- Resize không kéo được → False branch ghi đè (L10)
- OnReleased fire sớm → button nhỏ (dùng Is Mouse Button Down trong Tick)
- Accessed None → thiếu IsValid (L1)
- Logic sau không chạy → dead-end branch (L2)

---

## KHI CUHOANG ĐỀ XUẤT KHÁC KẾ HOẠCH

cuhoang có thể đề xuất cách khác plan_v3. Quy trình:

```
1. Verify đề xuất có hợp lý không (đối chiếu kiến trúc, performance)
2. So sánh với plan hiện tại: ưu/nhược điểm CỤ THỂ
3. Nếu đề xuất tốt hơn → đồng ý, ghi lại lý do thay đổi
4. Nếu plan cũ tốt hơn → giải thích lý do KỸ THUẬT cụ thể
5. KHÔNG bảo thủ "vì plan ghi vậy" — phải có lý lẽ kỹ thuật
6. Quyết định cuối: tôn trọng cuhoang, nhưng nêu rõ rủi ro nếu có
```

Ví dụ phản biện tốt:
```
"Đề xuất dùng AttachToActor cho group nghe hợp lý, nhưng plan_v3 cố tình
tránh vì: (1) Save/Load EMS phức tạp khi có attachment hierarchy,
(2) transform phụ thuộc parent gây bug khi undo. Data-only group (GroupID string)
đơn giản hơn cho 2 việc đó. Bạn vẫn muốn thử AttachToActor không?"
```

---

## CHECKLIST CUỐI MỖI TASK

- [ ] Code chạy đúng theo test trong 07
- [ ] Không vi phạm L1-L10
- [ ] Không hallucinate node (đối chiếu bảng node)
- [ ] Performance OK (đối chiếu 08)
- [ ] Hard ref clear ở End Play/Destruct (nếu có)
- [ ] Cập nhật doc liên quan (version, ngày, giờ, phút)

---

## CẬP NHẬT DOC SAU MỖI TÍNH NĂNG

Sau khi 1 sprint/task lớn xong:
```
1. Cập nhật Session_State.md (trạng thái + bug mới + variable mới)
2. Cập nhật Blueprint_Logic.md nếu có node flow mới
3. Tạo doc riêng nếu tính năng phức tạp (như WBP_ResizeWindow.md)
4. Ghi version + ngày + giờ + phút
5. Thêm node mới vào bảng "NODE CHÍNH XÁC" trong file này nếu phát hiện
```

---

## TÓM TẮT 1 DÒNG

> Đọc plan → kế thừa code → từng bước confirm → node chính xác → máy yếu first → verify trước khi phản bác → cập nhật doc.
