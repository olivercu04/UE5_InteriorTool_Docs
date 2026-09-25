# Tư duy 2 · Kiến trúc và nguyên tắc code

> ↑ [[Bản đồ não]] · Bộ Tư duy: [[Tư duy 1 · Sản phẩm và người dùng|1 Sản phẩm]] · **2 Kiến trúc** · [[Tư duy 3 · Cách làm việc và kiểm chứng|3 Cách làm việc]] · [[Tư duy 4 · Cách viết tài liệu trong bộ não|4 Cách viết tài liệu]]
> Viết 25/09/2026. Tóm tắt + trỏ doc gốc. Luật đầy đủ: [[AI_Implementation_Rules]] · [[Execution_Discipline]] · [[Performance]] · [[00_Master_Plan]] · [[18-09-2026_UndoArchitecture_Foundation_v1]].

**Dùng khi:** thiết kế tính năng mới, chọn chỗ đặt logic, review 1 node flow, hiểu vì sao code "vòng vèo" như vậy.

---

## 1. Hình dạng hệ thống trong 1 hình

```
 Người dùng
    │ click · kéo · phím
    ▼
 WIDGET (WBP_*)  ── chỉ hiển thị + chuyển lệnh ──┐
    │                                            │ Dispatcher (báo tin) ngược lên widget
    ▼                                            │
 MANAGER (BP_*Manager, 1 bản duy nhất)  ─────────┤  InputManager = não chọn / thao tác
    │  sửa                                       │  UndoManager  = sổ lịch sử
    ▼                                            │  ComboManager · SceneManager · UserPrefs
 CẢNH: BP_FurnitureActor (mỗi món 1 actor)  ─────┘
    │  dữ liệu bền: RowName · GroupID · PersistentID · MaterialSlots   (SaveGame → EMS)
    ▼
 DỊCH VỤ C++ (thuần, không giữ state): lọc DT · đọc/ghi vật liệu theo slot · sinh ID · file combo
```
Ví dụ đời thường: widget = quầy lễ tân (nhận yêu cầu, không tự nấu), manager = bếp trưởng, actor = món ăn trên bàn, dịch vụ C++ = dụng cụ bếp.
Bức tranh bằng ảnh: [[2 · Phía sau màn hình.canvas|Tổng quát 2 · Phía sau màn hình]].

## 2. Nguyên tắc nền (không đổi theo sprint)

| Nguyên tắc | Một câu | Vì sao |
|---|---|---|
| **Single source of truth** | Mỗi dữ liệu có đúng 1 nơi gốc: selection → `InputManager.SelectedActors` · nhóm → `FurnitureActor.GroupID` · danh mục → `DT_FurnitureCatalog` | 2 nơi gốc = chắc chắn lệch |
| **Kế thừa, không viết lại** | Có hàm làm việc tương tự thì mở rộng nó (vd mọi đường sinh đồ dùng `SpawnFurnitureCopy`) | Sửa 1 chỗ, mọi đường hưởng |
| **Additive, không breaking** | Thêm field / biến mới song song cái cũ, bỏ cũ khi mọi nơi đã chuyển (vd `RowName` + fallback `MeshPath` cho save cũ) | Save cũ không chết |
| **Logic phức tạp → Function trong manager** | Widget / event chỉ gọi 1 node nhận kết quả (vd thẻ combo chỉ gọi `ExecuteComboReplace`) | Widget dễ thay, logic không nhân bản |
| **Nhiều lớp ghi → đúng 1 hàm C++** | Gộp / ghi nhiều nguồn (combo JSON + sổ) do 1 hàm làm | BP tự tổng hợp nhiều nguồn = drift |
| **C++ đọc struct BP** | `GetAuthoredName` + cache `FProperty` trước loop — KHÔNG `reinterpret_cast`, KHÔNG tìm theo tên cứng | Tên property BP bị mangle GUID |

## 3. R1–R5 — bắt buộc cho code mới

| | Luật | Ví dụ |
|---|---|---|
| R1 | Tải async, không thêm `Load Asset Blocking` mới | `LoadMeshAsync`, `ApplyMaterialByRowName` |
| R2 | Widget không giữ hard ref Actor lâu dài — Soft ref, SET None ở Destruct | `DragOverlayRef` dọn ở Drag Cancelled |
| R3 | Widget nhận data nhẹ (RowName, struct), không nhận object nặng | Thẻ đồ nhận `BP_FurnitureItemView` chỉ chứa RowName |
| R4 | Destruct / End Play xoá mọi reference | chống VRAM leak |
| R5 | Lưu ID / RowName / GroupID, không lưu full path `/Game/…` | `S_FurniturePlacement.RowName` |

> Nợ cũ còn sống (biết để khỏi bắt chước): kéo đồ từ kho vẫn `Load Asset Blocking` ([[L03 · Kéo đồ vào phòng|L03]]), `Event ActorLoaded` nạp mesh blocking ([[L12 · Lưu và mở cảnh|L12]]).

## 4. Luật Blueprint hay dính (đầy đủ L1–L16 trong [[AI_Implementation_Rules]])

- **L1** IsValid trước MỌI truy cập object · **L2** nhánh Branch cụt trong chuỗi Event = lỗi chết (trong `Sequence.Then` thì hợp lệ).
- **L3** `CaptureSnapshot` SAU thao tác, không trong Deselect, không khi `bIsRestoring` · **L5 / L15** Deactivate TRƯỚC Activate (hàm dạng công tắc).
- **L8** Latent (Async / Delay / Timer) chỉ trong Custom Event · **L9** Event không có Local Variable → Function hoặc class var có prefix.
- **L11** Manager gọi hộ + latent + nhiều đích cùng lúc = aliasing → **mỗi actor tự lo asset của nó** (vì thế `ApplyMaterialByRowName` nằm trên actor).
- **L14** Pure node chạy lại mỗi lần đọc pin → cần 1 giá trị nhiều chỗ thì SET vào biến.
- Kết quả dạng tập không đảm bảo thứ tự → `Contains`, không `Get(0)`. Code chạy 1 lần → nối `Completed` của ForEach, không `Loop Body`.

## 5. Đối xứng thao tác — luật 6A / 6B ([[Execution_Discipline]])

- **6A:** tính năng chỉ "xong" khi có cả **đường xuôi và đường ngược** (undo / bỏ chọn / đóng / thoát / khôi phục). Mỗi note luồng L01–L13 có mục "Đường ngược".
- **6B:** nhiều đường tới cùng 1 cấu trúc phải cho cùng kết quả (nhóm top-down vs bottom-up → vì thế `CreateGroup` gom theo **đơn vị chọn**, không theo từng món).

## 6. Kiến trúc Undo — 6 trụ A–F ([[18-09-2026_UndoArchitecture_Foundation_v1]])

| Trụ | Ý | Đã có trong code |
|---|---|---|
| A | **Danh tính bền + Resolver** — mỗi món có `PersistentID`, tìm lại món bằng ID chứ không bằng con trỏ | `EnsurePersistentId`, `ResolveByPersistentId` (U1) |
| B | **Sổ có loại entry** — Snapshot hoặc Command trong 1 sổ | `EntryKind` Snapshot / ParamCommand (U2) |
| C | **Cổng thay đổi** — Atomic (click) hoặc Interactive Edit Session (kéo) | `Begin/Commit/CancelInteractiveEdit` (U2) |
| D | **ChangeSet** — báo "cái gì đã đổi" để UI cập nhật đúng phần | mới có `OnHistoryChanged` (thô) |
| E | **Snapshot đảo được** — lưu Before/After, không replay | chưa |
| F | **Tương tác ≠ dữ liệu cảnh** — selection / mode / slot đang chọn không phải "sự thật của bản vẽ" | U3 đang xử lý (mất slot sau Undo) |

Hệ quả phải nhớ: Undo 1 entry Snapshot **huỷ và sinh lại cả cảnh** → mọi con trỏ cũ chết; thứ gì sống qua Undo phải đi bằng ID ([[L13 · Hoàn tác và làm lại|L13]]).

## 7. Hiệu năng P1–P5 ([[Performance]])

P1 không Tick khi không cần · P2 cache thay vì query lặp · P3 async không blocking · P4 gom lô thay vì từng món · P5 **debounce** thao tác lặp (tìm kiếm 0.3s, nhích phím 0.5s, bấm vật liệu 0.5s). Máy đích vẫn tính máy tầm trung.

## 8. Bằng chứng: tin cái gì bao nhiêu

`K2 export` (graph thật) **>** doc as-built + test PASS **>** báo cáo / mô tả **>** plan. Plan là giả thuyết, không phải hợp đồng. Trong bộ não: mũi tên liền = ✓K2, đứt = theo doc, `?` = chưa rõ ([[Tư duy 4 · Cách viết tài liệu trong bộ não|Tư duy 4]]).

---
**Đọc tiếp:** [[Tư duy 3 · Cách làm việc và kiểm chứng]] — làm việc hằng ngày theo các luật này thế nào.
