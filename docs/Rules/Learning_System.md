# Hệ thống học UE5 — Cá nhân hóa
**Nguồn:** `import_raw/Learning_System.md`
**Phiên bản:** 1.1 | **Cập nhật:** 20/05/2026 — 16:00 ICT | Mentor: Claude | Học viên: Cuhoang

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

---

## Tính năng tiếp theo cần học

- [ ] **C++ Subsystem** — AssetService trong Refactor Phase B
- [ ] **Event Bus pattern** — thay Get All Actors Of Class singleton
- [ ] **glTFRuntime** — runtime mesh import
- [ ] **PCG Environment** — giai đoạn 4
