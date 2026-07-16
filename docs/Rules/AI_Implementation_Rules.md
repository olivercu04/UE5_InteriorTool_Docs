# 09 — Bộ Quy Tắc Thực Thi cho AI (Sonnet 4.6)
**Nguồn:** `import_raw/28-05-2026_09_AI_Implementation_Rules.md` (base v1.0) + `import_raw/09_AI_Implementation_Rules_patch_v2.md` (v2.0, 14/06/2026) + `import_raw/AI_Communication_Rules_update_15jun2026.md` (v2.1, 15/06/2026)
**Phiên bản:** 2.8 | **Cập nhật:** 15/07/2026 — thêm L12 (Function Return Value 100% exec path) + chuyển 3 node P1.G2-G4 vào bảng NODE CHÍNH XÁC
**Mục đích:** Guardrail để AI bám sát kế hoạch, đưa logic code chính xác, không hallucinate node UE5.5.

⚠️ **AI ĐỌC FILE NÀY ĐẦU TIÊN mỗi session thực thi, TRƯỚC khi làm bất kỳ task nào.**

---

## VAI TRÒ & BỐI CẢNH

Bạn (AI) đang giúp cuhoang **thực thi** kế hoạch đã được nghiên cứu kỹ trong thư mục `Planning/`. Kế hoạch này do Opus 4.7 xây dựng sau khi audit toàn bộ kiến trúc. **Không phải lúc để thiết kế lại — mà để thực hiện chính xác.**

- cuhoang: trình độ Blueprint trung bình, KHÔNG biết C++
- Ngôn ngữ: **Tiếng Việt thuần**. Giữ tên node/biến/class tiếng Anh. Từ kỹ thuật phổ biến (RAM, VRAM, async) giữ tiếng Anh.
- Engine: UE5.5.4
- Phong cách: hỏi từng bước, confirm trước khi tiếp tục, debug bằng Print String, ưu tiên máy yếu

---

## QUY TẮC TỐI CAO (KHÔNG VI PHẠM)

### Q1 — ĐỌC TRƯỚC KHI LÀM
Trước mỗi task, đọc theo thứ tự:
1. `Planning/04_Sprint_Details.md` — task cụ thể đang làm
2. `Planning/03_Code_Inheritance_Strategy.md` — function nào tái sử dụng được
3. `Data/Data_Structures.md` — struct/variable/signature chính xác
4. `Rules/Performance.md` — ràng buộc hiệu năng cho task đó

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
- Xem bảng inheritance trong `Planning/03_Code_Inheritance_Strategy.md`
- Tái sử dụng pattern: ForEach + IsValid, Sequence, Branch merge cuối
- KHÔNG tạo "MoveMulti" tách biệt "MoveSingle" — 1 function xử lý array

### Q5 — VERIFY TRƯỚC KHI PHẢN BÁC
cuhoang **thường đúng** về node UE5 cụ thể. Khi cuhoang nói khác:
1. KHÔNG bảo vệ ý mình ngay
2. Verify lại logic
3. Nếu cuhoang đúng → thừa nhận thẳng, sửa
4. Nếu vẫn nghĩ cuhoang nhầm → giải thích lý do cụ thể, không chung chung

### Q6 — MÁY YẾU LÀ ƯU TIÊN
Mọi logic mới đối chiếu `Rules/Performance.md`:
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
> **Ngoại lệ an toàn:** Branch False dead-end **TRONG Sequence.Then** là OK — Sequence tự kích hoạt Then tiếp theo. Branch False dead-end trong **Event chain** là FATAL.

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
> **Mở rộng (patch v2):** Trước khi bảo cuhoang "tạo Local Variable":
> - Nơi chứa là Function? → OK.
> - Nơi chứa là Event/Custom Event? → SAI. Event KHÔNG có Local Variable panel.
> - Dấu hiệu nhận biết Event: node màu đỏ, hoặc handler bind từ Dispatcher.

### L10 — Default value trước Sequence
```
Khi nhiều Branch trong Sequence ghi cùng 1 biến:
→ SET default TRƯỚC Sequence
→ False branch để TRỐNG (không ghi đè)
```

### L11 — Latent Load — Aliasing qua shared class var (19/06/2026)
BÀI HỌC: latent node (Async Load Asset) đặt trong Custom Event của InputManager → khi nhiều actor cùng load song song, các lần Completed chia sẻ CÙNG node graph → class var trung gian (MeshAsset, MID cache...) bị đè nhau → mesh/material set lên sai actor.

FIX ĐÚNG: đặt Custom Event trong chính actor sở hữu asset (BP_FurnitureActor). Mỗi instance có graph riêng → Completed của actor nào set cho actor đó, không share.

TỔNG QUÁT: Manager gọi hộ + latent + nhiều target đồng thời = aliasing. Giải pháp: "actor tự lo asset của nó".

### L12 — Function CÓ Return Value phải kiểm 100% exec path chạm Return Node (15/07/2026)
```
"Dead-end chấp nhận được" (L2 ngoại lệ trong Sequence.Then) CHỈ áp dụng cho Event/Custom
Event side-effect thuần (không có return type). Với Function có return type: dead-end
KHÔNG tự động trả None — Blueprint runtime TÁI SỬ DỤNG giá trị output từ lần gọi hàm
TRƯỚC ĐÓ trong cùng frame/vòng lặp.
```
Bài học từ bug 15/07/2026 (`BP_ComboManager.GetComboThumbnail`): nhánh False của
IfThenElse kiểm IsValid(LoadedTex) dead-end → khi gọi liên tục trong ForEach
(LoadComboLibrary), combo chưa có thumbnail hiện NHẦM ảnh của combo trước đó trong vòng
lặp. Q8 self-check L2 khi audit Function có Return Value: liệt kê ĐỦ từng nhánh, xác nhận
mỗi nhánh có Return Node riêng.

---

## ⭐ Q8 — SELF-CHECK GATE (cổng bắt buộc trước khi đưa BẤT KỲ node flow nào)

**Vấn đề giải quyết:** L1-L10 là kiến thức thụ động. AI "biết" nhưng không tự đối chiếu lúc sinh logic → lặp lại lỗi cũ đã có trong file.

**Quy tắc cứng (v2.1):** Trước khi đưa ra MỌI node flow, AI phải viết 1 dòng self-check VISIBLE, gồm ĐỦ 5 điểm:

```
Q8: [Container=Function/Event] | [IsValid guards] | [L2: mọi nhánh có đích] | [No Latent] | [6A: reverse path]
```

Ví dụ viết đúng:
```
Q8: Custom Event → class var OK | IsValid InputManager ✓ | L2: False branch merge về CaptureSnapshot ✓ | No latent ✓ | 6A: Undo khôi phục đúng ✓
```

**Không được viết:** "Tao đã check Q8" mà không liệt kê cụ thể.

Checklist đầy đủ (v2.0):
```
SELF-CHECK (chạy TRƯỚC khi viết flow):
□ Đang tạo Local Variable? → nơi chứa là FUNCTION hay EVENT?
   Event/Custom Event KHÔNG có Local Variable (L9) → đẩy logic vào Function, hoặc Class Variable.
□ Mọi Object access có IsValid trước chưa? (L1)
□ Mọi Branch có merge về cuối, không dead-end nuốt logic sau? (L2)
□ Class var persistent đã CLEAR ở đầu function chưa?
□ Có Latent node (Async/Delay/Timer) trong Function không? → sai, phải Custom Event (L8)
□ Flow có > 2 tầng Branch lồng không? → DỪNG, đề nghị tách Function/helper
□ Function thao tác đúng CẤP chưa? (gom đơn vị chọn vs gom actor-lá)
□ Có đường NGƯỢC chưa? (file 10, Luật 6A)
```

---

## L2 CHECK — PHÂN BIỆT SEQUENCE vs EVENT

Khi viết Branch bất kỳ, xác định context trước:

### Trong Sequence.Then:
```
Branch False → dead-end → ✅ HỢP LỆ
Sequence tự kích hoạt Then tiếp theo.
```

### Trong Event/Custom Event chain (KHÔNG trong Sequence):
```
Branch False → dead-end → ❌ FATAL
Logic sau Branch (nodes tiếp theo) sẽ KHÔNG chạy.
```

**Test nhanh:** "Nếu exec dừng ở đây, node nào sau Branch sẽ không chạy?"
- Nếu có node quan trọng (CaptureSnapshot, RemoveFromParent, Return Node...) → phải merge.
- Nếu không có gì sau → dead-end OK.

**Bài học 15/06:** False dead-end trong OnDrop (Event) → OnDrop return false → UMG destroy PreviewActorRef → mesh biến mất.

---

## NODE CHÍNH XÁC ĐÃ XÁC NHẬN (UE5.5 — dự án này)

Dùng đúng tên này, KHÔNG bịa tên khác:

| Mục đích | Node ĐÚNG | Node SAI (đừng dùng) |
|---|---|---|
| Lấy Canvas Slot | `Slot as Canvas Slot` | ~~Slot as Canvas Panel Slot~~ |
| Vị trí chuột viewport | `Get Mouse Position on Viewport` | (trả Vector2D, không cần chia DPI) |
| Vị trí chuột scaled | `Get Mouse Position Scaled by DPI` | |
| Set vị trí widget | `Slot as Canvas Slot → Set Position` | |
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
| Tạo object runtime | `Construct Object from Class` | |
| Is Valid Index | Array → kiểm tra index có hợp lệ không (không out of bounds). Input: Array + Index. Return: bool. Dùng thay thế cho Branch Array.Length > Index. ✅ xác nhận 19/06/2026 | |
| String → Array | `Parse Into Array(SourceString, Delimiter)` → Array\<String\>. Chia chuỗi theo separator. ✅ C5 25/06 | |
| Array exact match | `Array Contains(Array, Item)` — so sánh EXACT STRING. **KHÁC** `String Contains` (substring). Dùng để dedup CSV array. ✅ C5 25/06 | `String Contains` (substring match sai) |
| Map thao tác | `Map Clear(Map)` · `Map Find(Map, Key → Value, bFound)` · `Map Add(Map, Key, Value)` · `Map Contains(Map, Key → bool)` · `Map Remove(Map, Key)`. ✅ C5 25/06, Map Remove ✅ P1.G3 15/07 | |
| Ẩn gizmo lúc capture | `Get All Actors Of Class(BaseGizmo)` — class chung của RuntimeTransformer cho cả 3 loại gizmo (Translation/Rotation/Scale). ✅ P1.G2 15/07 | ~~BP_TransformerPawn/GizmoController~~ (không ổn định lúc đứng yên) |
| Brush trên Image/CommonLazyImage | `Set Brush` / `Get Brush` (property trực tiếp) · `SetBrushFromTexture` (nhận Texture2D* thẳng). ✅ P1.G4 15/07 | `SetBrushFromLazyTexture` (chỉ cho Soft Object Reference tới UAsset thật, không áp dụng texture runtime CreateTransient) |
| TileView bulk set | `Set List Items(TileView, Array)` — set toàn bộ 1 lần (stable render, thay N lần Add Item). ✅ C5 25/06 | Add Item lặp nhiều lần |
| String prefix check | `String Starts With(SourceString, InPrefix)` → bool. ✅ C5 25/06 | |
| Bind TreeNode event | `Bind Event to On Node Selected(Widget)` + `Create Event(HandlerFunc, self)` — binding dispatch từ WBP_TreeNode lên inventory. ✅ C5 25/06 | |
| `Find Substring (SearchFromEnd=True)` | Tìm vị trí ký tự từ cuối chuỗi → idx. idx==-1 nếu không tìm thấy. Dùng để parse "/" cuối trong path. ✅ C5.2 27/06 | |
| `Left(String, Count)` | Lấy Count ký tự đầu chuỗi. Dùng cùng FindSubstring để cắt phần trước "/". ✅ C5.2 27/06 | |
| `RightChop(String, Count)` | Bỏ Count ký tự đầu → lấy phần còn lại. Dùng cùng FindSubstring để cắt phần sau "/". ✅ C5.2 27/06 | |
| `Trim` | Bỏ khoảng trắng đầu/cuối chuỗi. Bắt buộc validate trước khi dùng làm tên folder. ✅ C5.2 27/06 | |
| `Select All Text When Focused` | Property trên EditableTextBox (KHÔNG phải node riêng) — set trong Details panel. ✅ C5.2 27/06 | |
| `Set Keyboard Focus(Widget)` | Force focus về EditBox sau Delay(0.0). Phải dùng với Delay(0.0) khi Hide menu cùng frame. ✅ C5.2 27/06 | `Focus Widget` (sai tên) |
| `Switch on ETextCommit` | Branch theo enum ETextCommit. **Selection pin PHẢI nối CommitMethod** — không nối → mọi commit vào Default → event không fire. ✅ C5.2 27/06 | Default pin (nếu Selection không nối) |
| `ForEachLoopWithBreak` | ForEach có thêm Break output pin để thoát sớm. Dùng để tìm node theo FolderPath. ✅ C5.2 27/06 | ForEach (thiếu Break) |
| `Remove Item(Array, Item)` | Xóa 1 element khỏi array theo value. Dùng để loại self ra khỏi SiblingNames. ✅ C5.2 27/06 | |

⚠️ Khi gặp node mới chưa có trong bảng → cuhoang xác nhận, rồi thêm vào bảng này.

---

## QUY TRÌNH CHUẨN MỖI TASK

```
1. ĐỌC task trong Planning/04_Sprint_Details.md
   ↓
2. Đối chiếu 03 (kế thừa gì) + Data_Structures (struct/signature) + Performance (performance)
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
8. Hết task → đối chiếu Test trong Planning/07_Testing_Strategy.md
   ↓
9. Pass test → cập nhật doc (version, ngày, giờ, phút) → sang task kế
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

cuhoang có thể đề xuất cách khác plan. Quy trình:

```
1. Verify đề xuất có hợp lý không (đối chiếu kiến trúc, performance)
2. So sánh với plan hiện tại: ưu/nhược điểm CỤ THỂ
3. Nếu đề xuất tốt hơn → đồng ý, ghi lại lý do thay đổi
4. Nếu plan cũ tốt hơn → giải thích lý do KỸ THUẬT cụ thể
5. KHÔNG bảo thủ "vì plan ghi vậy" — phải có lý lẽ kỹ thuật
6. Quyết định cuối: tôn trọng cuhoang, nhưng nêu rõ rủi ro nếu có
```

---

## ⭐ MỤC MỚI — BÀN GIAO OPUS → SONNET (giảm lỗi từ gốc)

Lỗi Sonnet thường không phải do Sonnet "kém" mà do **task đóng gói chưa đủ để thực thi không-sai**.

### LUẬT A — Task Card phải self-contained
Mỗi task giao Sonnet phải kèm SẴN, ngay trong task:
- **Bài học cũ áp dụng cho task này** — trích thẳng dòng L liên quan.
- **Node được phép dùng** — trích từ bảng NODE CHÍNH XÁC, chỉ những node task cần.
- **Checklist "phải có"** trước khi submit (rút gọn từ Q8 cho task đó).

### LUẬT B — Giới hạn độ phức tạp mỗi flow giao Sonnet
```
Flow có > 2 tầng Branch lồng → Opus PHẢI tách thành helper Function trước khi giao.
KHÔNG đưa Sonnet một cây Branch nhiều tầng.
Logic phức tạp → đẩy về Function có tên rõ; Sonnet chỉ ráp các Function phẳng.
```
> Logic resolve/tính toán phức tạp **không thuộc widget/event**. Đẩy về Function trong Actor quản lý (vd InputManager). Widget/Event chỉ gọi 1 node → nhận kết quả.

---

## NGUYÊN TẮC KP — 3 mảnh từ Karpathy guidelines (thêm 04/07/2026)

Nguồn: repo multica-ai/andrej-karpathy-skills (4 nguyên tắc chống lỗi LLM coding của Karpathy).
Chỉ lấy 3 mảnh hệ rules chưa có. Prefix KP để không đụng task ID K1/K3 trong roadmap.

### KP1 — Giả định tường minh
- Task/plan có chỗ mơ hồ → NÊU giả định đang dùng trước khi làm ("tao giả định X vì Y").
- Có ≥ 2 cách hiểu hợp lý → trình cả 2 kèm khác biệt, để cuhoang chọn. KHÔNG tự chọn im lặng.
- Bí/kẹt → dừng, nói rõ kẹt chỗ nào, hỏi.
- Mở rộng luật "không đoán mò" từ khâu debug sang cả khâu HIỂU TASK.
- Áp cho: nhận task card, đọc plan, viết node flow, sửa C++, distribute doc.

### KP2 — Speculative prep phải được duyệt
- KHÔNG tự thêm feature / param / field / "flexibility" ngoài yêu cầu task.
- Văn hóa "chuẩn bị 1 lần thay vì 2" (chừa field đón backend, parameterize API đón B3...)
  VẪN hợp lệ — nhưng phải nêu tường minh đây là prep + cuhoang duyệt TRƯỚC khi làm.
  Duyệt rồi → ghi plan/DEVIATIONS như lệ.
- Test nhanh: "200 dòng mà 50 dòng làm được → viết lại" / "senior engineer nhìn vào
  có bảo overcomplicated không?"
- Với Blueprint: flow > 2 tầng Branch lồng → tách Function (Luật B, nhắc lại cho đủ bộ).
- Shortcut/giải pháp tạm ĐƯỢC DUYỆT → ghi DEVIATIONS.md kèm **ceiling** (chịu được
  đến đâu thì gãy) + **trigger** (sự kiện nào thì bắt buộc nâng cấp/xóa). Thiếu
  trigger = shortcut thành vĩnh viễn. (Quy ước từ ponytail-debt — mẫu trong DEVIATIONS.md.)

### KP3 — Surgical changes: đụng đúng chỗ
- Mỗi dòng thay đổi phải truy được về yêu cầu của task.
- KHÔNG "tiện tay": refactor, đổi format/style, sửa comment, xóa dead code CÓ SẴN.
- Thấy dead code / chỗ đáng sửa NGOÀI task → ghi chú báo cuhoang, không tự sửa.
- Rác do CHÍNH thay đổi của mình tạo ra (biến/hàm/import thành mồ côi) → dọn.
  Rác có sẵn → để nguyên trừ khi được yêu cầu.
- Áp mạnh nhất ở 3 chỗ:
  1. Claude Code distribute doc — chỉ đụng file + section delta chỉ định.
  2. Sửa C++ FurnitureFilterLibrary / code kế thừa từ master project đồng nghiệp.
  3. Sửa BP đang chạy ổn — không "nhân tiện" đổi flow ngoài scope.

---

## BLUEPRINT EXPORT METHOD (phương pháp debug mới)

**Khi nào dùng:** Debug logic phức tạp (nhiều node, wire routing không rõ từ screenshot).

**Cách làm:**
1. Select nodes cần debug trong Blueprint Editor
2. Edit → Copy (Ctrl+C)
3. Paste vào chat (K2Node text)
4. AI đọc pin `LinkedTo` để trace exec + data connections

**Ưu điểm phát hiện được:**
- `LinkedTo=()` (empty) = dead-end exec
- `DefaultValue="false"` trên condition = bug logic
- `LinkedTo=(WrongNode ...)` = data wire sai
- Hai nodes cùng `LinkedTo` vào 1 exec pin = merge point

**Chú ý:** AI sẽ gọi node bằng **display name** (UE5 UI), không phải internal class name.

---

## SPAWN PATHS — Checklist F4-style

Khi thêm logic "sau khi spawn actor", phải audit ĐỦ các con đường spawn:

| Con đường | Widget/Function | Ghi chú |
|---|---|---|
| Drag-drop card | WBP_DragOverlay → On Drop | Dùng PreviewActorRef (đã spawn từ On Drag Detected) |
| Paste / Cut-Paste / Duplicate | SpawnFurnitureCopy (BP_FurnitureInputManager) | PasteMesh → ForEach → SpawnFurnitureCopy |
| Replace Mesh | WBP_DragOverlay_FurnitureCard → F_ExecuteReplace | Spawn mới, kế thừa từ OldActor |

> ⚠️ Drag-drop KHÔNG gọi SpawnFurnitureCopy — đây là lỗi assumption phổ biến.
> Luôn kiểm tra `Widgets/WBP_DragOverlay_FurnitureCard.md` khi cần can thiệp vào spawn.

---

## RUNTIME STATE vs SNAPSHOT STATE

**Nguyên tắc (rút ra từ A12):** Mọi state cần khôi phục qua Undo phải nằm trong `S_SceneSnapshot`.

**Checklist khi thêm state mới:**
- [ ] State này có cần undo-able không?
- [ ] Nếu có → thêm field vào `S_SceneSnapshot` + CaptureSnapshot capture + RestoreSnapshot restore
- [ ] Restore TRƯỚC bất kỳ function nào đọc state đó
- [ ] Bump `Version` nếu field mới ảnh hưởng restore behavior

**Ví dụ:**
- `Groups` → ✅ Trong snapshot V3
- `EditModeStack` → ✅ Trong snapshot V4 (15/06/2026)
- `bIsReplaceMode` → ❌ Không cần undo

---

## CHECKLIST CUỐI MỖI TASK

```
- [ ] Code chạy đúng theo test trong Planning/07
- [ ] Không vi phạm L1-L10
- [ ] Đã chạy Q8 Self-Check Gate, ghi dòng kết quả soi
- [ ] Không hallucinate node (đối chiếu bảng node)
- [ ] Performance OK (đối chiếu Rules/Performance.md)
- [ ] Hard ref clear ở End Play/Destruct (nếu có)
- [ ] Có đường NGƯỢC, đã test (Luật 6A trong Rules/Execution_Discipline.md)
- [ ] Cập nhật doc liên quan (version, ngày, giờ, phút)
```

---

## CẬP NHẬT DOC SAU MỖI TÍNH NĂNG

Sau khi 1 sprint/task lớn xong:
```
1. Cập nhật 00_Core/01_Session_State.md (trạng thái + bug mới + variable mới)
2. Cập nhật Blueprints/Blueprint_Logic_NodeFlow.md nếu có node flow mới
3. Tạo doc riêng nếu tính năng phức tạp
4. Ghi version + ngày + giờ + phút
5. Thêm node mới vào bảng "NODE CHÍNH XÁC" trong file này nếu phát hiện
```

---

## TÓM TẮT 1 DÒNG

> Đọc plan → kế thừa code → từng bước confirm → node chính xác → máy yếu first → verify trước khi phản bác → cập nhật doc.

---

## Quy ước đặt tên biến (từ Sprint 5, 19/06/2026)
- Class var dùng chung nhiều event trong 1 Actor → prefix viết tắt Actor đó.
  Vd BP_ComboManager → `Cmb_` (Cmb_PendingComboData, Cmb_SpawnedComboActors...)
- Biến tạm chỉ phục vụ 1 function/event → prefix = tên function/event đó.
  Vd SaveComboFromSelection → `SaveCombo_` (SaveCombo_GroupIDs, SaveCombo_TokenMap...)
- Param input của event/function → tên trần, không prefix (SelectedActors, ComboName, Center)

---

## Nodes chờ xác nhận (Thumbnail System — xác nhận tại C4)

⚠️ Các node/class dưới đây CHƯA được xác nhận trong project. KHÔNG thêm vào bảng "NODE CHÍNH XÁC ĐÃ XÁC NHẬN" cho đến khi cuhoang xác nhận tại C4.

| Node/Class | Dùng cho | Trạng thái |
|---|---|---|
| `SceneCapture2D` (Actor) | Capture thumbnail combo theo góc camera | ⏳ Cần xác nhận setup + cách đặt tại bounding box selection (C4) |
| `Texture Render Target 2D` | RenderTarget cho SceneCapture2D | ⏳ Cần xác nhận cách tạo runtime (C4) |
| `SaveRenderTargetToPNG` | C++ FurnitureToolkit — lưu RT→PNG (FImageUtils / FImageWrapperModule) | ⏳ Tên hàm xác nhận khi code C++ tại C4 |
| `LoadTexture2DFromFile` | C++ FurnitureToolkit — load PNG→Texture2D runtime (IImageWrapperModule) | ⏳ Tên hàm xác nhận khi code C++ tại C4 |
| `Delay` (node engine chuẩn, dùng trong Custom Event/Keyboard Event để chờ warm-up capture — P1.G0-R, 14/07/2026) | Chờ N giây trước khi `FinishComboCapture` (multi-frame warm-up cho Lumen GI/TAA hội tụ) | ⏳ Chờ cuhoang confirm trong project rồi chuyển vào bảng NODE CHÍNH XÁC chính thức |

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 28/05/2026 | Q1-Q7, L1-L10, bảng node, quy trình task |
| 2.0 | 14/06/2026 | Q8 Self-Check Gate; mở rộng L9; mục Bàn giao Opus→Sonnet; checklist cập nhật |
| 2.1 | 15/06/2026 | Q8 extended format (5 điểm visible); L2 CHECK (Sequence vs Event); Blueprint Export Method; Spawn Paths checklist; Runtime State vs Snapshot State |
| 2.2 | 19/06/2026 | Thêm Is Valid Index vào bảng node; thêm key learning L11 latent aliasing |
| 2.3 | 19/06/2026 | Thêm mục Quy ước đặt tên biến (Sprint 5 — BP_ComboManager prefix Cmb_, SaveCombo_) |
| 2.4 | 23/06/2026 | Thêm mục "Nodes chờ xác nhận" cho Thumbnail System (SceneCapture2D, Texture Render Target 2D, SaveRenderTargetToPNG, LoadTexture2DFromFile) — chờ xác nhận tại C4, chưa vào bảng node chính thức |
| 2.5 | 04/07/2026 | Thêm mục NGUYÊN TẮC KP (KP1 giả định tường minh, KP2 prep-phải-duyệt, KP3 surgical) — cherry-pick từ karpathy-guidelines |
| 2.6 | 04/07/2026 | KP2 bổ sung quy ước ceiling + trigger cho shortcut được duyệt (từ ponytail-debt) |
| 2.7 | 14/07/2026 | Thêm `Delay` vào mục "Nodes chờ xác nhận" (Thumbnail System) — dùng trong Custom Event/Keyboard Event để chờ warm-up capture, P1.G0-R. Chờ cuhoang confirm trước khi chuyển vào bảng NODE CHÍNH XÁC chính thức. |
| 2.8 | 15/07/2026 | Thêm **L12** — Function có Return Value phải kiểm 100% exec path chạm Return Node (bài học bug `GetComboThumbnail` cross-combo thumbnail bleeding, P1.G3). Chuyển vào bảng NODE CHÍNH XÁC: `Map Remove` (bổ sung dòng Map thao tác), `Get All Actors Of Class(BaseGizmo)` (ẩn gizmo lúc capture, P1.G2), `Set Brush`/`Get Brush`/`SetBrushFromTexture` (P1.G4). |
