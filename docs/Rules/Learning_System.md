# Hệ thống học UE5 — Cá nhân hóa
**Nguồn:** `import_raw/Learning_System.md`
**Phiên bản:** 1.3 | **Cập nhật:** 01/07/2026 — thêm chuẩn định dạng giải thích (sơ đồ + ví dụ đời thường, tránh đoạn văn dài) | Mentor: Claude | Học viên: Cuhoang

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

## Tính năng tiếp theo cần học

- [ ] **C++ Subsystem** — AssetService trong Refactor Phase B
- [ ] **Event Bus pattern** — thay Get All Actors Of Class singleton
- [ ] **glTFRuntime** — runtime mesh import
- [ ] **PCG Environment** — giai đoạn 4
