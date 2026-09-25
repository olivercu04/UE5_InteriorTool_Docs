# Hệ thống học UE5 — Cá nhân hóa
**Nguồn:** `import_raw/Learning_System.md`
**Phiên bản:** 1.7 | **Cập nhật:** 25/09/2026 — tick ✅ ForEach Loop Body vs Completed + Latent Wait For Operation (Q&A sau fix BoxSelectCtrl). Trước: 1.6 18/09/2026 — thêm "Điều chỉnh quy trình" phiên S7G7T4 (đoán sai giả định cơ chế qua undo 3 lượt; đọc ground truth sớm; cuhoang kéo lên tầng kiến trúc) | Mentor: Claude | Học viên: Cuhoang

---

## Triết lý

> Học qua dự án thực — không học lý thuyết rời rạc.
> Mỗi tính năng làm ra = 1 bài học hoàn chỉnh.

---

## Trình độ hiện tại

- Biết sơ Blueprint nhưng chưa hiểu bản chất các node
- Chưa biết C++
- Đang phát triển UE5 Interior Design Tool (furniture tool)

---

## Mục tiêu dài hạn

1. Phát triển furniture tool phục vụ công việc
2. Mở rộng sang UI/UX trong UE5
3. PCG Environment
4. Các mảng khác theo nhu cầu công việc

---

## Lộ trình học

### Giai đoạn 1 — Nền tảng Blueprint (đang ở đây)
Mục tiêu: hiểu bản chất từng node, không chỉ copy-paste.

Kiến thức cần nắm:
- [ ] Event flow (BeginPlay, Tick, Custom Event)
- [ ] Variables và References
- [ ] Branch / Sequence / Loop
- [ ] Cast — tại sao cần Cast
- [ ] Interface vs Direct Reference
- [ ] Dispatcher
- [ ] Array operations
- [ ] Function vs Custom Event

### Giai đoạn 2 — C++ cơ bản
Không học từ đầu — chỉ học khi Blueprint có giới hạn.
FurnitureFilterLibrary là bài học C++ đầu tiên đã hoàn thành.

### Giai đoạn 3 — UI/UX nâng cao
CommonUI, Widget Blueprint nâng cao, Animation UI.

### Giai đoạn 4 — PCG Environment
Mở rộng sau khi furniture tool ổn định.

---

## Quy tắc dạy học

### Claude phải làm:
1. **Giải thích tại sao** — mỗi khi hướng dẫn dùng node, phải giải thích bản chất node đó làm gì, không chỉ "đặt node này vào"
2. **Kiểm tra sau mỗi tính năng** — hỏi 1-2 câu ngắn để xác nhận học viên hiểu bài
3. **Ghi nhận tiến độ** — khi học viên trả lời đúng, tick vào checklist kiến thức
4. **Đơn giản hóa khi nản** — nếu học viên mơ hồ hoặc nản, lập tức đưa 1 bước nhỏ nhất có thể làm ngay
5. **Tiếp tục từ chỗ dang dở** — mỗi lần bắt đầu session mới, nhắc lại đang học gì, tiến độ đến đâu

### Claude không làm:
- Không giải thích lý thuyết dài dòng khi không được hỏi
- Không bỏ qua bước giải thích bản chất chỉ vì muốn làm nhanh
- Không để học viên copy-paste mà không hiểu

### Khi học viên nói mơ hồ hoặc nản:
1. Dừng lại
2. Hỏi "bạn đang mơ hồ ở điểm nào cụ thể?"
3. Đơn giản hóa xuống mức nhỏ nhất
4. Đưa 1 bước hành động rõ ràng nhất

---

## Cách kiểm tra tiến độ

Sau mỗi tính năng hoàn thành, Claude hỏi:
- "Node X trong tính năng này dùng để làm gì?"
- "Tại sao cần Cast ở bước Y?"
- "Nếu không có node Z thì chuyện gì xảy ra?"

Nếu trả lời được → ghi nhận, tiếp tục
Nếu không → giải thích lại bằng ví dụ thực tế từ dự án

---

## Tiến độ học (cập nhật 20/05/2026)

| Kiến thức | Trạng thái | Bài học từ tính năng |
|-----------|-----------|---------------------|
| Event BeginPlay | ✅ | Spawn actors trong Level Blueprint |
| Sequence node | ✅ | Spawn order furniture system |
| Cast | ✅ | Cast Player Controller, Cast Game Instance |
| Branch | ✅ | Logic toggle inventory, dead-end branch bug |
| Custom Event | ✅ | AddFurnitureInput / RemoveFurnitureInput |
| Array | ✅ | MaterialOverrides, SpawnedActors, AllFilteredMaterialRows |
| Dispatcher | ✅ | OnRestoreCompleted, OnMeshSelected, OnMeshDeselected |
| C++ Blueprint Function Library | ✅ | FurnitureFilterLibrary, FilterMaterialItems |
| Enhanced Input cơ bản | ✅ | LM_FurnitureInput, Add/Remove Mapping Context |
| Enhanced Input Chord Action | ✅ | IA_Ctrl, IA_Shift làm Chord cho Undo/Redo |
| Enhanced Input Trigger pins | ✅ | Triggered vs Started vs Pressed |
| Enhanced Input Consume Input | ✅ | 2 mapping Z để consume + chord trigger |
| Async Load Asset | ✅ | LoadAndApplyMaterial — String → SoftObjectPath → AsyncLoadAsset |
| Soft Object Reference | ✅ | ThumbnailMI lazy load, R2 principle |
| Timer (SetTimerByFunctionName) | ✅ | Debounce CaptureSnapshot 0.5s, delay 0.1s ApplyRestoredActor |
| Event Destruct | ✅ | Clear hard refs VRAM leak prevention |
| DataTable (GetDataTableRow) | ✅ | DT_MaterialInstancesCatalog — Row Found/Not Found pin |
| Dynamic Material Instance | ✅ | CreateDMI → SetMaterial để hỗ trợ param adjust sau |
| CommonUI (LazyImage, TileView) | ✅ | WBP_MaterialCard, WBP_SlotSwatch lazy load |
| String StartsWith + Prefix pattern (path cha-con) | ✅ | Bug `IsComboPathActive` (Issue 2 — Chip highlight, 30/06): Concat 3-pin ghép nhầm `Current+"/"+ThisPath` thay vì `ThisPath+"/"`. Kiểm tra hiểu qua Q&A: học viên tự ráp đúng ví dụ "Sofa"/"SofaBed" — xác nhận hiểu vì sao thiếu dấu "/" gây prefix giả mạo. |
| ForEach Loop Body vs Completed — exec-out trống trong Loop Body hợp lệ, việc chạy 1 lần nối Completed | ✅ | Bug `Bug-BoxSelectCtrl-MultiSnapshot` (25/09): `CaptureSnapshot` nằm trong Loop Body → N mốc. Kiểm tra hiểu qua Q&A 25/09: học viên tự giải thích Loop Body trống không phải dead-end vì macro tự chạy vòng kế rồi đi Completed — phân biệt đúng với L2 Branch trong Event chain. |
| Latent chờ việc async xong (EMS `Wait For Operation`) trước khi chụp trạng thái | ✅ | Fix `Bug-UndoAcrossLoad` (25/09). Q&A: học viên tự nêu bỏ Wait → chụp cảnh rỗng (sau Destroy, trước khi EMS nạp). Bổ sung đã giảng: Ctrl+Z NGAY sau Load chưa lộ lỗi (đang ở mốc 0) — lỗi nổ ở thao tác đầu tiên rồi Undo về mốc 0 = mất hết đồ. |

---

## Nợ kiểm tra hiểu — Sprint 5 (30/06/2026)

Giai đoạn chạy deadline Sprint 5 (C4 → C5.4 → Issue 2), quy tắc dạy học bị bỏ qua —
nhiều node/pattern được dùng nhưng KHÔNG qua bước hỏi-xác-nhận. Liệt kê đây để
KHÔNG tick ✅ khống — chỉ tick khi thật sự hỏi lại và học viên tự giải thích được,
giống cách làm với StartsWith ở trên.

| Kiến thức dùng nhưng chưa verify | Xuất hiện ở | Trạng thái |
|---|---|---|
| Dynamic Cast trong ForEach loop (lọc đúng kiểu widget) | UpdateComboFolderHighlights, CollectFolderTargets | ⏳ chưa hỏi |
| Pure function — nhiều dây ra từ 1 lần gọi không re-evaluate | IsComboPathActive gọi 2 lần (Print + RefreshDisplay) | ⏳ chưa hỏi |
| Đệ quy Function (gọi lại chính nó) + base case dừng | CollectFolderTargets | ⏳ chưa hỏi |
| Bind Event / AddDelegate — vì sao phải "+Add Custom Event matching signature" thay vì tự khai tay | HandleRowSelected, HandleMoveFolderConfirmed | ⏳ chưa hỏi (đã sửa lỗi 1 lần nhưng chưa hỏi lại nguyên nhân) |
| Array_Append(Target, Source) — chiều nào "ăn" vào chiều nào | CollectFolderTargets (bug D-C5.4-1) | ⏳ chưa hỏi |
| Reroute/Knot node — chỉ để dây gọn, không đổi logic | rải khắp Sprint 5 | ⏳ chưa hỏi (thấp ưu tiên, ít quan trọng) |

**Quy tắc xử lý nợ này:** không dồn hỏi 1 lần — mỗi lần 1 trong các dòng trên XUẤT
HIỆN LẠI tự nhiên trong tính năng tiếp theo (Move Combo, Tạo folder mới, Xóa folder,
ChipTag right-click), dừng lại hỏi 1 câu ngắn đúng lúc đó, không tách riêng buổi học.

---

## Điều chỉnh quy trình — 30/06/2026

Nguyên nhân: deadline Sprint 5 khiến quy tắc dạy học (đặc biệt "kiểm tra sau mỗi
tính năng") bị bỏ hoàn toàn trong ~10 ngày (21/06 → 30/06). Học viên tự nhận ra
và yêu cầu khôi phục.

3 điều chỉnh áp dụng từ đây:
1. **Trước khi tự đọc export/log kết luận bug** — hỏi học viên đoán thử trước
   ("tao nghĩ lỗi ở chỗ X vì Y"), dù sai cũng được. Đối chiếu đoán với bằng chứng
   thay vì Claude tự phán từ đầu.
2. **Sau mỗi tính năng xong** — hỏi 1-2 câu ngắn đúng tinh thần mục "Cách kiểm tra
   tiến độ" gốc của file này, KHÔNG bỏ qua dù đang gấp.
3. **Định kỳ (không cố định lịch)** — dừng lại hỏi học viên tóm tắt bằng lời luồng
   vừa làm, không phải để thi mà để tự học viên thấy mình có theo kịp không.

Không hồi tố tick ✅ cho phần đã bỏ qua (xem bảng "Nợ kiểm tra hiểu" ở trên) — xử lý
dần khi kiến thức đó tự nhiên xuất hiện lại, không dồn 1 buổi.

---

## Điều chỉnh quy trình — 01/07/2026 (định dạng giải thích)

3 điều chỉnh 30/06 vẫn giữ nguyên. Thay đổi thêm từ đây: CÁCH trình bày, không đổi TẦN SUẤT.

1. **Ưu tiên sơ đồ thay đoạn văn** — khi giải thích một luồng có nhiều bước hoặc một khái niệm
   có quan hệ nhiều chiều (A → B → C, hoặc A gây ra B và C), dùng ASCII/bảng/gạch đầu dòng ngắn.
   Đoạn văn xuôi chỉ dùng khi số bước ≤ 2 và không có nhánh.

2. **Kèm ví dụ đời thường cho khái niệm trừu tượng** — mỗi lần giải thích node/pattern lần
   đầu, thêm 1 ví dụ ngoài UE5:
   - Object Reference = "tờ giấy ghi địa chỉ nhà" (không phải cái nhà, chỉ là địa chỉ)
   - Bind Event = "hẹn người giao hàng gọi khi đến" (không chờ ngồi đó, chỉ đăng ký callback)
   - ForEachLoopWithBreak Completed pin = "chạy xong hàng → tính tiền" (Loop Body = đang tính
     từng món, Completed = sau khi xong tất cả)

3. **Không hồi tố** — 3 điều chỉnh 30/06 + 2 điều chỉnh trên áp từ 01/07 trở đi. Không
   thay đổi cách giải thích các phần đã giải thích trước đó trừ khi học viên hỏi lại.

---

## Điều chỉnh quy trình — 20/08/2026 (debug lạc hướng — engine incident)

Bối cảnh: phiên debug sự cố engine binary, Claude lạc hướng 3 lần liên tiếp trước khi
tìm đúng gốc — dựng chuỗi giả thuyết (Sequence corrupt → rớt dây → CategoryList rỗng),
mỗi lần cuhoang verify lại lật. Nguyên nhân lạc: Claude suy diễn tiếp khi bằng chứng
chưa khớp, thay vì dừng xác minh mình đang đứng ở đâu.

Bài học rút ra (áp dụng từ đây):

1. **F10 mà thấy mâu thuẫn → HỎI NGAY "đang đứng ở Blueprint nào", không suy diễn tiếp.**
   Điểm mù lớn nhất phiên này: Claude đọc "Create Widget WBP_FurnitureInventory" trong lúc
   cuhoang F10, không nhận ra cuhoang đang ở graph WBP_MeshControls (caller), chứ không phải
   WBP_FurnitureInventory. Lỡ mất mấy lượt vì tự quy 2 graph làm 1. Một Event Construct
   KHÔNG THỂ tự Create Widget chính nó — chi tiết mâu thuẫn kiểu này là tín hiệu "đang soi
   nhầm file", phải hỏi thẳng.

2. **Lỗi lan nhiều nơi + compile xanh + vô lý → nghi ENGINE/môi trường TRƯỚC graph.**
   Claude bám giả thuyết "graph corruption" quá lâu. Đúng ra: khi lỗi không tập trung 1 file
   và không có Error cụ thể, khả năng môi trường (engine binary, plugin, registry) cao hơn
   lỗi logic. Verify engine là phép thử rẻ nên làm sớm.

3. **Luật Mất Phương Hướng đã cứu (giữ tiếp):** tới lần lạc thứ 3 Claude tuyên bố "tao đang
   mất phương hướng", quay về gốc (vấn đề gốc / bằng chứng chắc / cái chưa biết) — đó là
   thời điểm bắt đầu đi đúng. Xác nhận cơ chế này hiệu quả, không bỏ.

4. **cuhoang đẩy nhịp đúng (ghi nhận):** khi Claude hỏi lại mấy thứ cơ bản đã confirm
   ("đã Play lại chưa"), cuhoang phản hồi thẳng → Claude bỏ ngay, không lặp. Giữ nhịp
   ngang hàng này: cuhoang chắc chỗ nào thì Claude tin, không hỏi thừa để "phòng xa".

---

## Điều chỉnh quy trình — 14/09/2026 (phiên G7.0a SpikeGate, C++ Slate)

Bối cảnh: phiên spike C++ thuần đầu tiên đụng Slate (`SColorWheel`/`SSimpleGradient`/`SSlider`),
khác hẳn nhịp Blueprint quen thuộc. Ghi lại pattern quy trình xác nhận đúng (giữ), không phải bug.

1. **Claude đoán sai chữ ký nhiều lần** (`InteriorHSVState` member vs namespace,
   `SSimpleGradient.Orientation`) — mỗi lần đều đã cảnh báo trước "nhớ từ API, chưa đọc header
   máy mày". Khi sai, đọc header thật thay vì đoán tiếp — pattern đúng, giữ nguyên.
2. **cuhoang bắt lỗi bằng mắt nhanh hơn Claude suy từ doc** (gradient chạy ngang/dọc, chiều
   sáng/tối) — xác nhận lại nguyên tắc "test 1 phút bằng mắt thắng suy luận dài" (xem `C1` trong
   `AI_Implementation_Rules.md`).
3. **Kiểm hiểu bài sau mỗi bước KHÔNG skip dù đang chuỗi dài.** cuhoang tick đúng phần lớn; 1 câu
   sai (case wheel/slider vì sao khác) là do gợi ý Claude đưa SAI hướng — Claude nhận lỗi, giảng
   lại, không tick khống. Giữ nhịp kiểm tra này kể cả khi task đang chạy nhanh.

---

## Điều chỉnh quy trình — 17/09/2026 (phiên S7G7T3, nhầm lẫn thứ tự Scalar/Color)

Bối cảnh: build `RefreshParamPanel` (`WBP_FurnitureInventory`) gồm nhiều bước con liên tiếp
(nhánh Scalar rồi nhánh Color của cùng 1 Switch). Có 1 lần nhầm lẫn thứ tự: cuhoang báo "xong" khi
đang nói tới nhánh Color trong lúc thực tế còn đang dở nhánh Scalar (Switch chưa build hết).

**Bài học phối hợp (ca cụ thể, không phải rule mới):** khi 1 chỉ thị gồm nhiều bước con liên tiếp
(vd Scalar rồi Color), và người dùng báo "xong rồi" mà không nêu rõ đang nói tới bước nào / kết quả
test cụ thể → PHẢI hỏi lại xác nhận phạm vi trước khi coi là hoàn thành bước đó, không suy đoán
theo thứ tự dự kiến của mình. Rule nền "Xong rồi mà chưa rõ → hỏi lại" đã có sẵn — đây chỉ là ví dụ
cụ thể để nhớ khi task có nhiều sub-step cùng tên loại (switch/branch nhiều nhánh).

Hệ quả trực tiếp trong phiên: `S7G7T3` phải ghi rõ trạng thái "ĐANG DỞ" thay vì "xong" — xem
`01_Session_State.md`, `Widgets/WBP_FurnitureInventory.md` mục "S7G7T3".

---

## Điều chỉnh quy trình — 18/09/2026 (phiên S7G7T4, đoán sai cơ chế undo)

Bối cảnh: sau khi T4 chạy, undo/redo chỉnh param mất slot-highlight. Claude dựng **3 fix liên tiếp**
(guard `Equal(Object)` ở `OnMeshSelected`, rồi `ApplyRestoredActor`, rồi thêm `SelectedSlotName`) —
**cả 3 đều dựa trên giả định "actor KHÔNG đổi qua undo"** mà CHƯA đọc `BP_UndoManager` để verify cơ
chế. Đọc ra mới biết: Undo = **destroy + respawn actor** (con trỏ mới) → mọi fix so-con-trỏ vô hiệu.

**Bài học chính (áp dụng từ đây):**

1. **Vấn đề chạm cơ chế mình CHƯA đọc trong phiên → đọc ground truth TRƯỚC khi dựng fix, không dựng
   fix trên giả định về cơ chế.** Lẽ ra đọc `BP_UndoManager.RestoreSnapshot` ngay lượt đầu (nó là
   "code hiện tại chạy sao" — canonical thắng), không phải sau 3 lượt patch. Dấu hiệu nhận biết:
   fix dựa trên 1 câu "chắc là X hoạt động thế này" mà chưa mở file X ra xem → DỪNG, đọc X trước.
   Đây là biến thể của luật "test 1 phút bằng mắt / đi lấy bằng chứng" — ở đây bằng chứng là 1 file
   canonical, không phải editor.

2. **Debug-guess-first giữ tốt (không đổi):** mỗi lượt Claude đều mời cuhoang đoán trước + dùng
   Print String tại điểm nghi ngờ (`Equal(Object)`, `SelectedSlotIndex` tại các mốc) rồi mới kết
   luận. Nhờ đó lượt 3 log lật thẳng giả thuyết (`Equal:false` + `sel=4`) — bằng chứng cứu, không cãi.

3. **cuhoang kéo lên tầng kiến trúc đúng lúc (ghi nhận nhịp phối hợp mới):** khi Claude sa vào
   patch-từng-node, cuhoang nói thẳng "tao nghĩ đến tầng thiết kế kiến trúc còn thiếu" + nhắc lại
   chính câu Claude từng nói (`SelectedSlotIndex` không nằm trong snapshot). Đó là điểm bẻ lái đúng.
   → Khi 1 vấn đề đã sửa ≥2 lượt không trúng, TỰ Claude phải nghi "đây là tầng kiến trúc, không phải
   bug node" và lùi lại — không đợi cuhoang kéo. Đúng tinh thần "tái đánh giá bản chất vấn đề bằng
   toàn bộ context" (Custom Instructions mục 2).

4. **Q10 (rule lập sáng cùng ngày) validate 2 lần trong 1 phiên** — bug dispatcher thiếu `ParamName`
   (producer contract không phủ consumer T4) + bug undo cross-flow đều đúng loại Q10 bắt. Rule mới
   dùng được ngay, không phải lý thuyết suông.

**Nợ kiểm tra hiểu (KHÔNG tick khống):** phiên này chạy nhanh để đóng T4 GATE, Claude KHÔNG dừng hỏi
1-2 câu kiểm hiểu bài sau mỗi handler (vi phạm nhẹ rule dạy học, giống bài học Sprint 5). Kiến thức
xuất hiện đáng verify khi gặp lại: (a) **Dispatcher payload** — vì sao `ParamName` phải đi trong
payload chứ không bind sẵn được (liên quan mục ⏳ "Bind Event matching signature" trong bảng Nợ
Sprint 5, phiên này cuhoang ĐÃ tự tạo 4 custom event từ bind signature — thực hành đúng nhưng CHƯA
hỏi lại nguyên nhân); (b) **Live vs Commit** — vì sao preview KHÔNG snapshot, commit mới snapshot;
(c) **Undo = respawn** — vì sao widget-state không sống qua undo. Hỏi 1 câu đúng lúc khi 3 chủ đề này
tái xuất ở phiên redesign undo / T4b.

---

## Phiên U2.3 PARITY GATE (24/09/2026) — bài học

1. **Quan sát trong cửa sổ async 2 pha của `RestoreSnapshot` → suýt kết luận FAIL oan.** REG-05 (Reset
   sau replace+tint) ban đầu NGỠ FAIL: nhìn mesh/tint chưa đúng ngay sau Undo. Thực ra `RestoreSnapshot`
   restore async 2 pha (material trước, `ParamsJson` sau qua `LoadMeshAsync.Completed`) — quan sát quá
   sớm thấy trạng thái trung gian, chưa phải kết quả cuối. Probe định vị (log entry `Đổi màu Tint` Idx=4
   + mesh CÓ tint + panel đúng) xác nhận restore ĐÚNG, chỉ là mắt bắt sai thời điểm. → **Với thao tác có
   async/latent (restore, load mesh), đợi trễ hoặc đọc Output Log trước khi chốt PASS/FAIL — đừng chốt
   bằng frame đầu tiên.** (Biến thể của "test 1 phút bằng mắt": mắt phải đợi async xong.)

2. **Debug-guess-first + Print giữ tốt (không đổi):** W7 (`CurrentIndex` semantics) chốt bằng 6 dòng log
   `Idx=Len−1` thay vì suy luận từ doc — bằng chứng thẳng. Bug Undo (đọc entry SAU khi giảm index →
   trượt 1) bắt được qua review K2 export, không phải đoán.

---

## Phiên U2.4 + U2.5 (24/09/2026) — bài học + cách phối hợp

**Kết quả:** U2.4 + U2.5 ĐÓNG (câu hỏi nhị phân U2 xanh) + đóng B-gizmo (treo 3 tháng) + 2 bug nền phát hiện dọc đường.

### Bài học kỹ thuật
1. **Bug che bug — gặp 3 lần trong 1 phiên.** (a) Seed panel luôn trắng → che lỗi bánh xe màu không nhận `SetColor`
   (trùng hợp đúng); (b) SlotContextLost (undo Move reset slot=-1) → che nghi vấn ghi mồ côi ở U6; (c) seed 0/trắng →
   che luôn lỗi Before của Undo. → **Sửa xong 1 lỗi NỀN (nguồn dữ liệu, thời điểm) thì chạy lại test của mọi thứ đọc
   nguồn đó** — cái "đang đúng" có thể chỉ đúng nhờ lỗi cũ.
2. **Hàm công tắc (toggle) gọi 2 lần = tắt.** B-gizmo: `ActivateGizmo` đảo trạng thái; `RestoreSnapshot` gọi `SelectActors`
   2 lần → bật rồi tắt. Test đối chứng 1 ghế vs 2 ghế (2 nhánh code khác nhau) chốt root cause trong 1 phút. Quy tắc:
   `AI_Implementation_Rules.md` L15.
3. **Setter C++ UWidget phải lưu vào biến TRƯỚC khi đẩy xuống Slate.** Gọi trước lúc widget được gắn (Setup trước
   AddChild) thì Slate chưa tồn tại → bỏ im lặng. Quy ước engine (`USlider::SetValue`). `AI_Implementation_Rules.md` C10.
4. **Dispatcher bind không chọn được handler → soi signature dispatcher trước.** UE5 ẩn Custom Event lệch signature khỏi
   danh sách, không báo lỗi. cuhoang tự đoán đúng hướng ("do ParamName nên không nhận") — chỉ cần 1 bước verify.
5. **Blueprint không có "SET 1 field của struct"** → `GET → Set members in <Struct> → SET`. Pin output của hàm thì nối
   thẳng vào `Set members in`, không cần Get/SET. (Mới với cuhoang — đã hỏi lại 2 lần trong phiên, bình thường.)

### Claude tự sửa mình (ghi để không lặp)
- **Giao nhầm "build thân `ApplyParamCommand`"** — thật ra đã build + K2-review ở U2.3 (`DEVIATIONS.md` D-4). Nguyên nhân:
  đầu phiên đọc Session_State + task card + canonical nhưng BỎ QUA bước "scoped DEVIATIONS" trong route pilot. → **Trước khi
  giao việc trên 1 hàm đã có tên, grep tên đó trong `DEVIATIONS.md` + canonical.** (Bằng chứng cho pilot route: bước
  scoped DEVIATIONS KHÔNG thừa.)
- **Task card xếp `Commit` sau `Begin` mà `Begin` gọi `Commit`** → phát hiện trước khi cuhoang dựng (không để cuhoang
  đâm vào lỗi compile). → Trước khi đưa thứ tự build, kiểm phụ thuộc gọi hàm giữa các bước.
- **Nghi "ghi mồ côi" ở U6 → test U6b bác bỏ → KHÔNG vá.** Đúng quy trình: nghi thì thiết kế test, không vá phòng hờ.
  Ghi ceiling + trigger vào DEVIATIONS D-11 thay vì thêm code.

### Cách phối hợp — giữ / đổi
- **Giữ:** mời cuhoang đoán trước rồi đưa test 1 phút đối chứng (B-gizmo: cuhoang đoán "công tắc" → test 1 vs 2 ghế →
  khớp → mới sửa). Mẫu tốt nhất của phiên.
- **Giữ:** cuhoang trả "không biết" → đổi câu hỏi suy luận thành câu hỏi SỰ KIỆN trả lời được ngay ("tạo biến theo thứ tự
  nào, có compile giữa chừng không?") — tiến được 1 bước thay vì đưa đáp án.
- **Giữ:** báo trước "trạng thái trung gian" trước PIE (U2.4 session chưa đóng khi thả chuột) — khi cuhoang thắc mắc,
  giải thích bằng quy trình user thật + ví dụ thủ thư đóng dấu → hiểu ngay.
- **Đổi:** câu hỏi quan trọng nhét cuối bảng test dài → cuhoang bỏ sót (U6 phải hỏi 3 lần, W3 Color 2 lần). → Câu hỏi
  cần trả lời: tách riêng, đặt ĐẦU, nói luôn vì sao quan trọng.
- **Ghi nhận:** cuhoang tự đề xuất hướng "trao đổi 2 chiều" cho lỗi bánh xe màu — sai root cause (thời điểm) nhưng đúng
  nửa kia của fix (user kéo → lưu lại). Ý tưởng có giá trị → phản hồi rõ phần đúng, phần sai.
- **Kỹ thuật bridge:** git trong folder đã kết nối cần quyền XÓA (file `.git/index.lock`) — xin quyền xóa đúng folder plugin
  trước khi chạy git, nếu không sẽ kẹt lock.

### §11 kiểm tra hiểu U2 — PASS 7/7 (24/09/2026 17:38, hỏi từng câu, sửa tại chỗ khi lệch)
| # | Câu | Kết quả |
|---|---|---|
| 1 | Vì sao Undo command phải `ResolveByPersistentId`, không dùng `TargetFurnitureActor` | ✓ "undo = destroy+respawn". Bổ sung: con trỏ cũ = tham chiếu CHẾT; PersistentID sống qua respawn (địa chỉ nhà vs số CCCD) |
| 2 | Vì sao Before đọc từ core, không lấy số trên slider | ✓ nối được với bug seed 0/trắng. Bổ sung nguyên tắc: widget = bản sao hiển thị (có thể bị kẹp Min/Max), mesh = bản gốc |
| 3 | 100 preview → 1 entry; Cancel không để entry mà vẫn về giá trị cũ | ✓ sau 1 vòng dẫn: tách `BuildSceneSnapshotBase` (dựng) vs `AppendEntry` (đưa vào sổ); Before cất ở `Sess_Cmd.BeforeScalar` lúc Begin, Cancel áp lại qua `ApplyParamCommand(bUseBefore)` |
| 4 | Vì sao command entry vẫn kèm ảnh full (hướng B) | ✓ sau 3 vòng: "Undo snapshot N → ảnh của N−1" — ảnh full trong command entry là để DÀNH cho entry snapshot đứng sau nó. **Nợ nhẹ:** lần đầu nói undo command "dùng entry trước" — đúng là dùng Before của CHÍNH nó. Hỏi lại khi gặp ở U3 |
| 5 | Bỏ nhánh `Sess_Active→Commit` trong Begin thì sao | ✓ lần chỉnh trước mất dấu khỏi history. Bổ sung: Before cũ bị ghi đè → cũng không Cancel được = ghi mồ côi |
| 6 | Undo command không respawn vs Undo Move respawn | ✓ tính qua câu 1 + 4 |
| 7 | Vì sao Deactivate-trước-Activate an toàn với mọi số lần gọi | ✓ + giới thiệu khái niệm **idempotent** |

**Quan sát cách học:** câu có ví dụ từ CHÍNH test chiều đó (U5, bug seed) trả lời nhanh và đúng ngay; câu thuần khái niệm (hướng B/ảnh full) cần quy tắc tường minh + bảng điền `?` mới vỡ ra. → Với khái niệm trừu tượng, đưa QUY TẮC dạng 1 dòng + bài tập điền chỗ trống sớm hơn, đừng chỉ gợi ý.

---

## Tính năng tiếp theo cần học

- [ ] **C++ Subsystem** — AssetService trong Refactor Phase B
- [ ] **Event Bus pattern** — thay Get All Actors Of Class singleton
- [ ] **glTFRuntime** — runtime mesh import
- [ ] **PCG Environment** — giai đoạn 4
