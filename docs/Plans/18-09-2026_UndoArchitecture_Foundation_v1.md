# DELTA — UNDO ARCHITECTURE FOUNDATION (kiến trúc state toàn application)

**Tác giả:** Opus 5 (kiến trúc sư) | **Ngày:** 18/09/2026 | **Loại:** PLAN — chưa as-built
**Phiên bản:** 1.0

> **KHÔNG đóng dấu `[CHỨA AS-BUILT]`.** File này 100% là thiết kế. Mọi con số/API/hành vi trong
> đây chưa chạy lần nào. Khi thực thi xong, as-built merge vào canonical (`Blueprints/`,
> `Data/`, `Rules/`), KHÔNG sửa ngược vào file này — file này giữ nguyên để tra "vì sao đã
> quyết vậy".

**Nguồn:** phiên họp kiến trúc 3 bên 18/09/2026 (cuhoang ↔ Opus 5 ↔ ChatGPT, 5 vòng brief).
Bối cảnh bug gốc: `Bug-ParamUndo-SlotContextLost` (`Bugs/Open_Bugs.md`), `DEVIATIONS.md` mục
"Param-Undo slot-context" (18/09), `Blueprints/BP_UndoManager.md` v1.17.

**Ground truth đã đọc khi thiết kế:** `BP_UndoManager.md` v1.17 (`CaptureSnapshot`/`RestoreSnapshot`
đầy đủ) · `WBP_FurnitureInventory.md` v3.32 (5 handler T4 + `OnMeshSelected` Equal-guard) ·
`Data/MaterialSlotService_Reference.md` (14 hàm G1 + `UMaterialParamMap` T1/T2) ·
`00_Core/01_Session_State.md` (18/09 tiếp 2) · `DEVIATIONS.md` §Param-Undo.

**Ảnh hưởng doc canonical:** chưa có. Doc này là delta thuần — Claude Code merge SAU khi từng
gate as-built, không merge trước.

---

## 0. TÓM TẮT CHO NGƯỜI VỘI

| | |
|---|---|
| **Bug châm ngòi** | Undo chỉnh param vật liệu → giá trị đúng, nhưng mất slot-highlight + Inspector sập về placeholder |
| **Chẩn đoán** | Không phải thiếu dữ liệu. Snapshot ĐÃ chứa `ParamsJson` của mọi slot. Thiếu **đường khôi phục đủ mịn** |
| **Phát hiện lớn hơn** | Hệ Undo đang kiêm luôn session-state manager. Selection/ActiveMode/EditModeStack nằm trong document snapshot → mọi UI context mịn hơn "đang chọn actor nào" đều chết sau undo |
| **Quyết định** | KHÔNG vá triệu chứng. Xây móng state architecture, migrate dần từng action |
| **Phạm vi lần này** | `T0 → U1 → U2 → U3`. `F-Migration` khai báo nhưng KHÔNG làm |
| **Ước lượng** | 4–6 buổi tới hết U3 |
| **Điều kiện tiên quyết** | Đường lùi (backup toàn project + git plugin) — ĐÃ XONG 18/09 |

---

## 1. VẤN ĐỀ GỐC — VÀ VÌ SAO KHÔNG VÁ TRIỆU CHỨNG

### 1.1 Dữ liệu đã đủ, đường khôi phục quá thô

```
S_SceneSnapshot
  └ Meshes : Array<S_FurniturePlacement>
       └ MaterialSlots : Array<FMaterialSlotRecord>      ← v1.16 (07/09)
            └ ParamsJson : FString                        ← GIÁ TRỊ PARAM ĐÃ NẰM SẴN ĐÂY
```

Snapshot đã chứa đủ trạng thái param. Cái thiếu là đường khôi phục: muốn đảo 1 giá trị float,
hệ đi `DeselectAll → destroy TOÀN BỘ actor → respawn TOÀN BỘ`.

> **Ví dụ đời thường:** muốn sửa 1 chữ sai trong sổ mượn sách, nhưng quy trình duy nhất là đốt
> cả cuốn sổ rồi chép lại từ bản lưu. Nội dung chép lại thì đúng — nhưng cái kẹp giấy đang đánh
> dấu trang (slot-highlight) thì mất. Bản lưu không thiếu thông tin; thiếu thao tác "tẩy chữ đó,
> viết đè".

### 1.2 Ba vấn đề cấu trúc nằm dưới (chưa ai báo lỗi, nhưng đã có sẵn)

| # | Vấn đề | Bằng chứng trong doc |
|---|---|---|
| 1 | **Object identity** — định danh actor bằng `Get Display Name()`. Actor respawn có tên khác. Mọi thứ trỏ tới actor bằng con trỏ/tên đều đứt sau undo | `BP_UndoManager.md` Step 3 `UniqueID = Get Display Name`; `01_Session_State.md` §Mìn deploy: "UniqueID=GetDisplayName có thể khác hành vi editor/packaged" |
| 2 | **Granularity** — mỗi lần *click chọn* 1 món đồ cũng chụp full scene | `Blueprint_Logic_NodeFlow.md`: `CaptureSnapshot("Select")`, `("Deselect")`, `("BoxSelect")` |
| 3 | **Refresh model** — sau undo, UI không được báo "cái gì đã đổi", bị buộc rebuild qua `OnSelectionChanged` | `WBP_FurnitureInventory.md` v3.32 nhánh Material của `OnMeshSelected` |

### 1.3 Vì sao KHÔNG chọn đường vá nhanh

Phương án vá (đã cân nhắc và loại): giữ nguyên hệ snapshot, thêm "fast path" chỉ đi tắt 1 bước
khi 2 entry liền kề chỉ khác nhau ở param. ~1,5 buổi, rủi ro thấp.

**Loại vì:** nó chỉ trị 1 manifestation. Tính năng kế tiếp cần `actor + sub-target + context`
(ví dụ: chọn 1 cạnh, 1 góc, 1 phần tử con) sẽ gặp lại đúng bug dưới tên khác. Bug này là bằng
chứng ĐẦU TIÊN rằng boundary hiện tại đã bị vượt qua, không phải một ca lẻ.

cuhoang chốt 18/09: chấp nhận thêm thời gian, làm móng.

---

## 2. SÁU TRỤ KIẾN TRÚC (A–F)

```
                    USER INPUT
                        │  Intent
                        ▼
              Interaction / Tool Layer          ← selection, active tool, slot đang chọn,
                        │                          drag session, panel đang mở
                        ▼
              ┌─────────────────────┐
              │  C. MUTATION        │  ├── Atomic Transaction        (click, nút bấm)
              │     BOUNDARY        │  └── Interactive Edit Session  (kéo slider, gizmo)
              └──────────┬──────────┘
                         ▼
              Scene / Document State
         actors · transform · material · param · group
                  │                    │
           A. Identity            B. History
              Resolver         (typed entries)
                  │                    │
                  └──────────┬─────────┘
                             ▼
                      D. ChangeSet
                             ▼
                    Presentation / UI
```

### Bảng trụ

| # | Trụ | Nội dung | Giải vấn đề nào |
|---|---|---|---|
| **A** | **Stable Identity + Resolver** | Mỗi entity mang `PersistentID` (GUID) cấp lúc sinh, sống xuyên destroy/respawn/save/load. `Map<PersistentID → Actor hiện tại>` do một manager giữ | §1.2 #1 |
| **B** | **Typed History Entry** | 1 stack duy nhất. Mỗi entry là Snapshot **hoặc** Command. Envelope thống nhất, payload theo domain | §1.2 #2 |
| **C** | **Mutation Boundary** | Mọi thay đổi document đi qua 1 trong 2 cổng: Atomic Transaction (discrete) hoặc Interactive Edit Session (continuous) | §1.1 |
| **D** | **ChangeSet** | Sau mutation, phát ra *cái gì đã đổi* + *phase* (Preview/Commit/Rollback). UI cập nhật đúng phần đó, không rebuild | §1.2 #3 |
| **E** | **Reversible Snapshot Entry** | Snapshot entry lưu `{Before, After}` → tự đảo được như mọi command. **KHÔNG replay, KHÔNG checkpoint** | mở khóa việc trộn 2 loại entry |
| **F** | **Interaction ≠ Document State** | Selection/ActiveMode/EditModeStack là Interaction State, không phải document truth | §1.2 #2, #3 |

### 2.1 Trụ E — điểm thanh lịch nhất, ghi rõ để khỏi bàn lại

Bản thiết kế đầu (Opus) định nghĩa undo qua snapshot là *"restore snapshot gần nhất phía trước
rồi replay các command nằm giữa"*. **SAI** — đó là event sourcing, phức tạp không cần thiết.

Định nghĩa đúng: snapshot entry cũng lưu 2 đầu.

```
Timeline:   C1 → C2 → S1 → C3          C = delta command · S = snapshot transaction

Undo C3  →  apply C3.Before
Undo S1  →  Restore S1.BeforeSnapshot
Undo C2  →  apply C2.Before
Undo C1  →  apply C1.Before

Redo S1  →  Restore S1.AfterSnapshot

KHÔNG replay · KHÔNG tìm checkpoint · KHÔNG reconstruct timeline
```

> Snapshot thôi là một loại lịch sử đặc biệt. Nó chỉ là **một command rất to, dùng Memento làm
> implementation**.

Checkpoint cho crash recovery / autosave là khái niệm KHÁC. **Không trộn `checkpoint` với
`undo entry`.**

### 2.2 Trụ C — Interactive Edit Session

Luồng thật của slider: kéo → hàng trăm lệnh áp giá trị **live**, cố ý không ghi history → thả →
mới ghi 1 entry. Nghĩa là document bị mutate liên tục *bên ngoài* mọi transaction.

Giải: thêm một primitive nằm GIỮA UI và History.

```
PointerDown ──► BeginInteractiveEdit(TargetPath)
                    ├─ Resolver xác nhận target
                    ├─ Core đọc Before          ← Before KHÔNG nằm trong widget
                    └─ trả SessionID

Drag (×N)   ──► UpdateInteractiveEdit(SessionID, NewValue)
                    ├─ apply preview lên runtime object
                    └─ Session.Current = NewValue          ← KHÔNG ghi history

PointerUp   ──► CommitInteractiveEdit(SessionID)
                    └─ tạo ĐÚNG 1 History Command {Before, Current}
```

**UI chỉ giữ `SessionID` — không giữ invariant nào.**

State machine (cực nhỏ, và chính nó là bộ test tốt):

```
        Begin
          ▼
      PREVIEWING
      /        \
  Commit      Cancel
    ▼            ▼
COMMITTED    CANCELLED

CẤM: commit 2 lần · update sau cancel · update SessionID lạ · cancel session đã commit
```

**Termination policy (cứng):**

> **Chỉ explicit Commit mới tạo document edit. Mọi abnormal termination đều Cancel + Rollback.**

Escape · widget destroyed · panel đóng giữa drag · target invalid · scene unload · đổi selection
→ `CancelInteractiveEdit` → `Apply(Target, Before)` → `ChangeSet{Phase=Rollback}`.

Lý do KHÔNG auto-commit khi widget chết: widget destruction là **lifecycle event**, không phải
user intent. Biến nó thành "user đã commit" = để UI implementation quyết định document semantics —
đúng thứ kiến trúc này đang loại bỏ.

**Version đầu: CHỈ 1 session đồng thời.** `ActiveInteractiveEdit : Optional<Session>`. Begin mới
khi session cũ còn mở → settle cái cũ trước. Không build `Map<SessionID, N sessions>`. Rất nhiều
edge case biến mất nhờ giới hạn này.

**Undo (Alt+Z) trong lúc đang kéo:** cancel preview đang chạy TRƯỚC, rồi mới undo entry trước đó.
Không biến preview chưa commit thành 1 entry rồi undo nó.

> **Invariant: History chỉ nhìn thấy committed actions.**

### 2.3 Hai dạng user action — generalization đủ lớn cho tương lai

```
DISCRETE                        CONTINUOUS
Click Reset                     PointerDown → Begin Session
→ Atomic Transaction            Drag…       → Preview × N
→ 1 Command                     PointerUp   → Commit → 1 Command

vd: BTN_ResetSlot               vd: slider param · color picker ·
    BTN_ResetAll                    Move/Rotate/Scale gizmo · numeric scrub
    Reset thông số
```

Đây là lý do giải bài toán này ở U2 thay vì vá riêng Material Param: **slider hôm nay, transform
gizmo ngày mai** dùng chung một primitive.

---

## 3. LUẬT MIGRATION (áp cho toàn dự án, không chỉ Undo)

```
ADD  ──►  VERIFY PARITY  ──►  LOCK WITH REGRESSION  ──►  REMOVE OLD PATH
additive      đường mới           test khóa hành vi        subtractive
              chạy song song      cũ lại
```

Dự án đã migrate thành công 2 lần theo đúng pattern này: `RowName` (Sprint D.T6 → v1.14),
`MaterialSlots` (G2/2B → v1.16). Cả hai đều thêm field song hành trước, gỡ đường cũ sprint sau.

**Hệ quả cụ thể cho lần này:** `SelectedIndices` / `ActiveMode` / `EditModeStack` **VẪN NẰM
TRONG SNAPSHOT** suốt U1–U3. Không gỡ.

Lý do (bằng chứng lịch sử — dự án đã trả giá 3 bug để đưa chúng VÀO):

| Bug | Triệu chứng | Fix | Ref |
|---|---|---|---|
| stale index | Undo nhảy cóc qua trạng thái Deselect | selection index vào snapshot + CLEAR đầu hàm | `BP_UndoManager.md` v1.5 |
| A12 | Undo xong thanh Edit Mode không tắt | `EditModeStack` vào snapshot (V4) | v1.8 |
| B1 | Undo lần 2 không restore group state | cờ `bIsRestoring` chặn capture đệ quy | v1.9 |

Gỡ chúng khi chưa có replacement = mở lại cả ba, cùng lúc, giữa sprint. Đúng nguyên tắc nhưng
sai thứ tự.

---

## 4. STATE OWNERSHIP — POLICY + 6 DÒNG BẮT BUỘC

### 4.1 Taxonomy (chốt trước, điền dần sau)

```
APPLICATION STATE
│
├── DOCUMENT DOMAIN
│   ├── Committed State        ← canonical · save · history dựa vào đây
│   └── Provisional / Pending  ← live preview trong Edit Session · KHÔNG save · KHÔNG history
│
├── INTERACTION STATE          ← selection · active tool · inspector target · focus
│
└── VIEW / WORKSPACE STATE     ← panel size · docking · scroll · filter · camera
```

**Hai điểm khóa:**

1. **Persistence KHÔNG quyết định lớp.** View State có thể được nhớ qua lần mở app sau, nhưng
   nó vẫn không phải Document State.
2. **Đang tác động lên runtime Actor cũng chưa chắc là committed Document State.** Live preview
   chứng minh điều đó: MID đã đổi thật, nhưng committed document chưa.

```
Committed:           Roughness = 0.30
Pending edit:        Roughness = 0.61
Runtime projection:  MID đang hiện 0.61      ← user nhìn thấy cái này

Commit  →  Committed = 0.61 · Pending = none
Cancel  →  Runtime projection về 0.30 · Committed VẪN = 0.30
```

### 4.2 Policy — KHÔNG audit toàn bộ

```
① DECLARATION GATE   feature MỚI khai báo state ownership — thêm 1 dòng vào Q9 đã có
                     (KHÔNG dựng hệ gate thứ 8)

② LAZY FILL          state CŨ chỉ canonicalize khi có task thật chạm tới
                     → mỗi dòng trong bảng đều được một task thật verify

③ FILL NOW           đúng 6 state mà U1–U3 / F-Migration đụng (bảng §4.3)
```

Lý do loại bỏ audit toàn bộ (25 state × 6 cột = 150 ô): một bảng làm trong 2 buổi sẽ có ~40 ô
verify thật và ~110 ô suy đoán — trình bày đẹp như nhau, không phân biệt được. Dự án đã có luật
cho đúng tình huống này (*Claude Code không có ground truth thì chỉ BÁO CÁO, không SỬA*).

> **Architecture on demand, theo một taxonomy đã chốt trước.**

### 4.3 Sáu dòng bắt buộc

> **Nhãn nguồn:** `[DOC]` = đọc từ canonical doc · `[VERIFY]` = cần xác nhận bằng K2/PIE trước
> khi tin. **KHÔNG ô nào được để trống.**

| State | Owner | Lifetime | Persist | Undoable? | Cần stable ID? | Khi target destroy/respawn |
|---|---|---|---|---|---|---|
| **Selection** (`SelectedActors`) | Interaction `[DOC]` | interaction session | không | **hiện CÓ** (legacy, trong snapshot) `[DOC]` | CÓ | hiện: reset. đích: resolve lại bằng ID |
| **ActiveMode** (`E_ActiveMode`) | Interaction `[DOC]` | application session | không `[VERIFY]` | **hiện CÓ** (legacy) `[DOC]` | không | giữ nguyên |
| **EditModeStack** | Interaction `[DOC]` | interaction session | không `[DOC]` | **hiện CÓ** (legacy V4) `[DOC]` | CÓ (GroupID) | hiện: `ValidateEditMode` cắt group đã mất |
| **Inspector Target** (`TargetFurnitureActor`) | Interaction `[DOC]` | interaction session | không | **KHÔNG** | **CÓ** ← gốc bug | hiện: reset (con trỏ chết). đích: giữ bằng ID |
| **Material Slot Target** (`SelectedSlotIndex`/`Name`) | Interaction `[DOC]` | interaction session | không | **KHÔNG** | **CÓ** ← gốc bug | hiện: reset về -1. đích: giữ bằng `TargetPath` |
| **Pending Edit** (preview đang kéo) | **Provisional Document** | 1 edit session | không | **KHÔNG** (chỉ Commit vào history) | CÓ | Cancel + rollback về Before |

**Đọc bảng này ra một câu:** 4/6 state cần stable identity, 2 trong đó chính là bug đang mở. Đó
là lý do trụ A đi trước mọi thứ.

---

## 5. DANH MỤC INVARIANT `UNDO-*`

> ⚠️ **Tiền tố `UNDO-` BẮT BUỘC, không rút gọn.** Dự án đã có 6 hệ mã ngắn đang chạy
> (`L1-L11` · `R1-R5` · `Q8/Q9/Q10` · `KP1-KP3` · `Đ1-Đ12` · `S7G7Tn`) và đã có luật sinh ra vì
> chuyện đụng mã: *"Mã ngắn hay đụng nhau giữa các hệ. Thấy mâu thuẫn ở mã ngắn → kiểm mã đó
> thuộc hệ nào TRƯỚC."* Viết `ID-01` thay `UNDO-ID-01` trong lúc vội = sinh drift mới.

Mỗi invariant nối được 4 nơi: **Requirement (doc này) ↔ Test (tên `It`) ↔ Implementation ↔ Bug**.

### T0 — Harness

| Mã | Invariant |
|---|---|
| `UNDO-T0-01` | Test harness chạy được một assertion đúng → XANH |
| `UNDO-T0-02` | Negative control: assertion cố ý sai → ĐỎ (harness biết kêu) |

### U1 — Identity

| Mã | Invariant |
|---|---|
| `UNDO-ID-01` | Entity mới sinh → nhận `PersistentID` hợp lệ, duy nhất |
| `UNDO-ID-02` | Snapshot restore (destroy + respawn) → **giữ nguyên** `PersistentID` |
| `UNDO-ID-03` | Duplicate / Copy-Paste → `PersistentID` **MỚI** (không dùng lại của bản gốc) |
| `UNDO-ID-04` | Entity đã xóa → ID biến khỏi Resolver, **không bao giờ tái sử dụng** cho entity khác |
| `UNDO-ID-05` | Resolver sau restore: `Resolve(X)` trả actor MỚI, và actor mới ≠ actor cũ (UObject khác) |
| `UNDO-ID-06` | **Save → Load cùng document → giữ nguyên ID** |
| `UNDO-ID-07` | **Load save CŨ (không có ID) → cấp ID một lần rồi ghi lại**; load lại lần nữa KHÔNG cấp ID khác |
| `UNDO-ID-08` | ID chỉ sinh tại "logical birth". Restore thì ID được **inject từ state**, không generate trong Construction Script / BeginPlay |

> `UNDO-ID-07` là đường mà cuộc họp suýt bỏ sót. Dự án **đã có save cũ đang tồn tại** (bằng
> chứng: fallback `MeshPath`/`DAPath` trong `BP_FurnitureActor.md`). Nếu mỗi lần load lại cấp ID
> mới, "bền vững" sẽ hỏng theo cách rất khó truy.

### U2 — History / Mutation Boundary

| Mã | Invariant |
|---|---|
| `UNDO-HIST-01` | Undo một delta command **không** destroy/respawn actor nào |
| `UNDO-HIST-02` | Undo qua một snapshot entry **không** cần replay command nào |
| `UNDO-HIST-03` | Command chỉ được commit khi **round-trip đầy đủ** state nó tuyên bố sở hữu |
| `UNDO-SESS-01` | Begin → đọc và giữ `Before` (trong core, không trong widget) |
| `UNDO-SESS-02` | Preview update **không** tạo history entry |
| `UNDO-SESS-03` | Commit tạo **đúng 1** entry, mang `Before` gốc và `After` cuối |
| `UNDO-SESS-04` | `Before == After` (mọi change) → **không** tạo entry |
| `UNDO-SESS-05` | Cancel → restore `Before`, **không** tạo entry |
| `UNDO-SESS-06` | Update sau khi session kết thúc → bị từ chối |
| `UNDO-SESS-07` | Undo trong lúc previewing → cancel preview TRƯỚC, rồi mới undo entry cũ |

### U3 — Context / ChangeSet

| Mã | Invariant |
|---|---|
| `UNDO-CTX-01` | Sau undo param: **cùng logical entity** vẫn là inspector target |
| `UNDO-CTX-02` | Sau undo param: **cùng slot** vẫn là target, highlight còn nguyên |
| `UNDO-CTX-03` | UI phân biệt được *"con trỏ actor chết"* với *"logical entity không còn tồn tại"*. Chỉ clear context khi vế sau đúng |
| `UNDO-CTX-04` | Undo Roughness **không** đổi: số lượng actor · transform · Tint · entity ID |

> `UNDO-CTX-04` là loại test quan trọng nhất cho hệ undo và dễ bị bỏ sót nhất: test không chỉ
> chứng minh *"đổi đúng"* mà cả *"không phá thứ khác"*.

---

## 6. VERIFICATION ARCHITECTURE

### 6.1 Ba tầng — cố ý rất nhỏ

```
                 MANUAL                    visual · UX feel · Shipping smoke
                    ▲
              FUNCTIONAL TEST              World + Actor + BP integration
                    ▲
           C++ AUTOMATION SPEC             domain / core — KHÔNG cần World
```

| Tầng | Dùng cho | Chạy ở |
|---|---|---|
| **Automation Spec** | ID lifecycle · history cursor · branch-after-undo · transaction state machine · command Before/After · snapshot entry semantics · ChangeSet contents · Resolver rules | Editor, **không cần PIE** |
| **Functional Test** | seam mà Spec không chứng minh được: actor lifecycle thật, spawn/destroy/restore end-to-end | **cần PIE** |
| **Manual** | highlight có đúng không · panel có nhảy không · drag có cảm giác đúng không · bản Shipping | mắt |

### 6.2 ⚠️ LUẬT NGÂN SÁCH PIE — ràng buộc môi trường, KHÔNG phải sở thích

Máy cuhoang có workaround đang hiệu lực (`ways-of-working`, §GPU): **GPU crash Streamline →
dùng Standalone Game thay PIE cho session dài, restart editor mỗi 2–3 PIE.**

Automation Spec chạy trong editor, **không tốn PIE**. Functional Test **tốn 1 PIE mỗi lần chạy**.

```
LUẬT:  ① Cái gì Spec test được thì KHÔNG được đẩy xuống Functional Test.
       ② Toàn bộ Functional Test nằm trong MỘT map duy nhất:
             L_Test_UndoArchitecture
          Chạy một lượt, không rải nhiều map.
```

Vi phạm luật này biến suite regression thành một buổi restart editor liên tục. Đây là lý do
**thật** đằng sau "một test map duy nhất" — không phải vì gọn gàng.

### 6.3 Protocol 5 bước cho MỌI test mới

```
1. CONTRACT           viết behavior bằng câu tiếng người + gán mã UNDO-*
2. RED                test FAIL vì behavior chưa tồn tại (hoặc bug cũ còn đó)
3. GREEN              implement tối thiểu → test PASS
4. NEGATIVE CONTROL   cố ý phá ĐÚNG behavior test bảo vệ → test phải ĐỎ vì ĐÚNG assertion
5. RESTORE            khôi phục implementation → test XANH lại
```

> **Test nào chưa từng ĐỎ thì chưa được tính là test.**

Với bug có sẵn, thứ tự đẹp nhất: bug xuất hiện → viết regression test → RED trên code hiện tại →
fix → GREEN. Mạnh hơn viết fix rồi mới viết test.

### 6.4 Bốn kỷ luật — vì chủ dự án không tự đọc code test

cuhoang nói thẳng sẽ gửi test cho AI đọc thay vì tự đọc. Nghĩa là **test sai sẽ tạo tự tin
sai — tệ hơn không có test.** Bốn kỷ luật bù lại:

| | Kỷ luật |
|---|---|
| **A** | Mỗi invariant có mã `UNDO-*`, và mã đó xuất hiện trong tên test: `It "[UNDO-ID-02] giữ nguyên ID qua snapshot restore"` |
| **B** | Test **observable behavior**, không test implementation. Không viết *"nó gọi Add trên map 1 lần"* khi contract thật là *"nó resolve đúng entity bằng ID gốc"* |
| **C** | Test chứng minh cả **"đổi đúng"** lẫn **"không phá thứ khác"** (xem `UNDO-CTX-04`) |
| **D** | Test **độc lập**: không giả định thứ tự chạy, dọn state sau mỗi test |

### 6.5 Ba thứ kiểm nhau — test KHÔNG thay documentation

```
Docs   =  Intent            ← vì sao muốn thế này
Tests  =  Executable Contract
Code   =  Implementation
```

Test vẫn drift được: nếu code và test cùng hiểu sai một yêu cầu thì cả hai cùng xanh. Doc kiến
trúc là cái neo thứ ba.

### 6.6 Release gate (dùng từ Gate 2, không cần dựng CI bây giờ)

```
CORE      Automation Spec                    →  PASS
RUNTIME   Functional Test / cooked Dev       →  PASS
RELEASE   Shipping smoke test                →  PASS       ← KHÔNG bỏ
```

Dự án này đã có tiền sử `"works PIE" ≠ "works packaged Shipping"`. **Automation xanh trong
editor không phải bằng chứng cho Shipping.**

---

## 7. GATE MAP

```
T0  ──►  U1  ──►  U2  ──►  U3  ──►  [F-MIGRATION]
                                      khai báo, KHÔNG làm lần này
```

| Gate | Xây gì | **Câu hỏi nhị phân** | Ước lượng |
|---|---|---|---|
| **T0** | Automation harness | *Project chạy được automated test đáng tin không?* | ~1 buổi |
| **U1** | `PersistentID` + Resolver, **song hành** `UniqueID` cũ | *Sau undo scene, `Resolve(ID cũ)` có ra đúng actor mới không?* | ~1–1,5 buổi |
| **U2** | History entry đa hình + Mutation Boundary + Edit Session + Param Command đầu tiên | *Kéo slider → undo → giá trị đảo, và actor KHÔNG bị destroy?* | ~2 buổi |
| **U3** | `TargetPath` + ChangeSet + Inspector giữ context | *Undo xong slot-highlight và Inspector còn nguyên?* | ~1 buổi |
| **F-Mig** | Gỡ Selection/ActiveMode/EditModeStack khỏi snapshot | — | **sau, task riêng** |

**Luật dừng (cứng):**

```
T0 không xanh đáng tin  →  DỪNG toàn bộ migration. Không xây kiến trúc trên harness không tin được.
U1 không xanh           →  KHÔNG xây U2.
U2 không xanh           →  KHÔNG nối UI.
U3 xanh                 →  Material Param thành reference implementation. Rồi mới migrate action thứ 2.
```

**Trước F-Migration, bắt buộc:** encode 3 regression lịch sử (stale-index · A12 · B1) thành
automated test TRƯỚC khi tháo. *Không tháo ba dây an toàn rồi mới xem chuyện gì xảy ra.*

### 7.1 Ghi chú thiết kế cho U2 (chưa làm, để khỏi khóa sai)

Payload command — hình dạng chốt:

```
FMaterialParamCommand
{
    Changes : Array<FMaterialParamChange>
}

FMaterialParamChange
{
    Target : { EntityID · SlotKey · ParamName · ParamType }
    Before : { Type · Scalar | Vector | Texture }
    After  : { … }
}
```

- **U2: `Changes.Num() == 1` LUÔN LUÔN.** Tuyệt đối không implement multi-target behavior.
  Representation chỉ để không chặn `S7G7T5` sau này.
- **`SlotKey` KHÔNG cần thiết kế mới** — dự án đã giải bài toán này ở tầng slot:
  `FMaterialSlotRecord{SlotName, SlotIndex}` + `ResolveSlotIndex(Mesh, SlotName, HintIndex)`
  (*tên unique → index; rỗng/trùng → hint; không ra → −1*), PASS từ G1.
  `SlotKey = {SlotName, HintIndex}`.

> **Nhận xét đáng giữ:** dự án đã làm **đúng** identity ở tầng material slot, và **sai** ở tầng
> actor. Cùng một bài toán, đã giải đúng một lần. U1 là copy đúng khuôn mẫu đó lên một tầng.

- **Per-property, KHÔNG whole-slot JSON.** Lý do là *semantic granularity*: user action là
  "Set Roughness" thì history cũng phải hiểu "Set Roughness", không phải "thay toàn bộ trạng
  thái slot". Whole-slot command sở hữu cả property mà thao tác không đụng → coupling giả.
- **Bẫy texture (Đ12) — xử ngay ở schema.** `ApplyParamsJsonToSlot` hiện **chỉ ghi log, chưa
  load texture** (`MaterialSlotService_Reference.md`). Nếu command dùng JSON làm payload, nó sẽ
  **im lặng nuốt texture**. Với per-property: tạo command cho texture khi chưa hỗ trợ →
  trả `Unsupported`, **không cho commit**.

```
CẤM tuyệt đối:   command hợp lệ → undo → texture branch log warning
                 → bỏ qua → history vẫn báo success
                 = silent corruption
```

JSON vẫn giữ nguyên giá trị cho Snapshot / Save-Load / Migration. **Không dùng serialization
format làm domain-command format.**

---

## 8. TASK CARD — `T0` AUTOMATION HARNESS GATE

> **Self-contained.** Giao thẳng cho Sonnet hoặc cuhoang tự làm. Không cần đọc file nào khác
> ngoài mục này.

### 8.0 Ba cổng gate

```
Q10 — FLOW COVERAGE    MIỄN.  T0 không đụng state nào đã tồn tại. Không có producer/consumer
                              nào bị ảnh hưởng. Không sửa 1 dòng code sản phẩm.
Q9  — S-MATRIX         MIỄN.  T0 không đụng `SelectedActors`.
Q8  — NODE SELF-CHECK  MIỄN.  T0 không có Blueprint node flow nào (bước 4 tuỳ chọn thì áp).
```

Ghi rõ lý do miễn ở đây để không ai phải hỏi lại — task card thiếu bảng Q9 mà không ghi lý do
miễn thì Sonnet phải từ chối execute (luật dự án).

### 8.1 Mục tiêu — MỘT câu hỏi nhị phân

> **Project này chạy được automated test đáng tin cậy không?**

Không xây gì thuộc kiến trúc Undo trong T0. Nếu harness không đáng tin, mọi thứ đứng trên nó
đều vô nghĩa.

### 8.2 Bước 0 — xác nhận đường lùi (ĐÃ XONG 18/09, chỉ tick lại)

```
[ ] Backup toàn project:  Lighting_Mnger_BACKUP_18-09-2026_preT0
    GIỮ: Content/ · Plugins/ · Source/ · Config/ · *.uproject
    BỎ:  Saved/ · Intermediate/ · DerivedDataCache/ · Binaries/
[ ] Backup ĐÃ TEST RESTORE một lần (mở lên, build lại Binaries, PIE chạy)
    → backup chưa từng restore KHÔNG PHẢI backup
[ ] Git private repo cho Plugins/FurnitureToolkit/ (text → git; binary asset → copy toàn project)
```

Lặp lại bước 0 **trước mỗi gate** (U1, U2, U3) với hậu tố `_preU1`, `_preU2`, `_preU3`.

### 8.3 Bước 1 — file test đầu tiên

**Vị trí:**
```
Plugins/FurnitureToolkit/Source/FurnitureToolkit/Private/Tests/FurnitureToolkitTests.cpp
```

**Build.cs:** KHÔNG đụng. `FAutomationSpecBase` nằm trong module `Core` (`Misc/AutomationTest.h`),
đã là dependency sẵn có. `[VERIFY]` — nếu link lỗi, kiểm `PublicDependencyModuleNames` có `Core`.

**Nội dung:**

```cpp
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS        // ← macro này = 0 trong Shipping → test KHÔNG lọt bản ship

BEGIN_DEFINE_SPEC(FUndoArchHarnessSpec,
    "FurnitureTool.Undo.T0_Harness",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
END_DEFINE_SPEC(FUndoArchHarnessSpec)

void FUndoArchHarnessSpec::Define()
{
    Describe(TEXT("Test harness"), [this]()
    {
        It(TEXT("[UNDO-T0-01] chay duoc mot assertion dung"), [this]()
        {
            TestEqual(TEXT("1 + 1"), 1 + 1, 2);
        });

        It(TEXT("[UNDO-T0-02] NEGATIVE CONTROL - phai DO o lan chay dau"), [this]()
        {
            TestEqual(TEXT("co y sai"), 1 + 1, 3);      // ← ĐỎ. Bước 3 mới sửa thành 2.
        });
    });
}

#endif
```

> `[VERIFY]` **`EAutomationTestFlags`** — UE5.5 có đổi cách đặt tên flag ở một số bản
> (`ApplicationContextMask`). Nếu compile lỗi ở dòng flag: thử
> `EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::EngineFilter`.
> Ghi kết quả thật vào `Rules/AI_Implementation_Rules.md` mục **"Nodes / API chờ xác nhận"**.

> **Không dấu tiếng Việt trong chuỗi test** — tên test hiển thị trong Session Frontend, an toàn
> nhất là ASCII.

### 8.4 Bước 2 — chạy test

```
Editor → Window → Developer Tools → Session Frontend
       → tab Automation
       → ô Filter gõ:  FurnitureTool.Undo
       → tick group  →  Start Tests
```

`[VERIFY]` — đường menu có thể khác chút ở 5.5 (một số bản: `Tools → Session Frontend`). Ghi
đường thật vào doc as-built.

**Kết quả BẮT BUỘC ở lần chạy đầu:**

```
[UNDO-T0-01]  ✅ XANH
[UNDO-T0-02]  ❌ ĐỎ        ← đây là KẾT QUẢ ĐÚNG, không phải lỗi
```

**Nếu cả 2 đều xanh → HARNESS HỎNG.** Nghĩa là test không thật sự chạy (thường do filter sai,
module không build, hoặc `WITH_DEV_AUTOMATION_TESTS` = 0). **DỪNG, báo cuhoang.** Đây chính là
lý do T0 tồn tại: một suite rỗng cũng "xanh".

### 8.5 Bước 3 — RESTORE

Sửa `1 + 1, 3` → `1 + 1, 2`. Chạy lại. Cả 2 XANH.

### 8.6 Bước 4 — Functional Test (TUỲ CHỌN, chỉ làm nếu bước 1–3 mượt)

```
[ ] Tạo map:  L_Test_UndoArchitecture     (map TEST duy nhất, xem luật §6.2)
[ ] Đặt 1 Actor kế thừa AFunctionalTest
[ ] Test tối thiểu: spawn 1 BP_FurnitureActor → assert IsValid → FinishTest(Succeeded)
[ ] Chạy qua Session Frontend, xác nhận XANH
```

Nếu bước 4 vướng >30 phút → **gác lại, KHÔNG cố**. T0 vẫn tính PASS với bước 1–3. Functional
Test có thể dựng ở đầu U1 khi đã có thứ đáng test end-to-end.

### 8.7 Điều kiện đóng T0

```
PASS  =  [UNDO-T0-01] xanh
      ∧  [UNDO-T0-02] ĐÃ TỪNG ĐỎ vì đúng assertion, rồi sửa thành xanh
      ∧  cuhoang tự chạy lại được suite mà không cần hỏi đường bấm
```

Điều kiện thứ ba quan trọng ngang hai điều kiện đầu: nếu chỉ AI chạy được thì harness không
dùng được trong thực tế.

### 8.8 Ghi lại sau khi xong

| File | Ghi gì |
|---|---|
| `00_Core/01_Session_State.md` | dòng `Current:` → T0 ĐÓNG / đang chạy |
| `Rules/AI_Implementation_Rules.md` | mục "API chờ xác nhận": kết quả thật của `EAutomationTestFlags` + đường menu Session Frontend |
| `00_Core/DEVIATIONS.md` | chỉ khi có lệch so với task card này |
| doc mới `Rules/Testing.md` | **chỉ tạo khi T0 PASS** — chứa §6 của file này + đường bấm thật |

### 8.9 Câu hỏi kiểm tra hiểu bài (trả lời TRƯỚC khi tick T0)

1. Vì sao `[UNDO-T0-02]` phải ĐỎ ở lần chạy đầu, mà không viết luôn cho nó xanh?
2. Vì sao Automation Spec được ưu tiên hơn Functional Test trong dự án NÀY — lý do liên quan
   gì tới cái máy?

---

## 9. ẢNH HƯỞNG BACKLOG

| Mục | Trạng thái mới | Lý do |
|---|---|---|
| **`S7G7T4b`** (coalescing undo + `EndParamSession`) | **XOÁ — absorbed by architecture** | Interactive Edit Session sinh đúng 1 command lúc Commit → coalescing là hệ quả tự nhiên. `EndParamSession` ≡ `CommitInteractiveEdit`. **Không để lại như task phải implement lần hai** |
| **`S7G7T5`** (multi-select apply) | GIỮ, thêm ghi chú | `FMaterialParamCommand.Changes` là array từ U2 → T5 không bị chặn về representation. **U2 KHÔNG implement multi-target** |
| **`Bug-ParamUndo-SlotContextLost`** | GIỮ OPEN, gắn `UNDO-CTX-01/02` | Đóng khi U3 PASS |
| **Đ12** (texture trong `ParamsJson` chỉ log) | GIỮ, nâng mức | Từ "nợ kỹ thuật" thành **ràng buộc schema**: command texture chưa hỗ trợ → `Unsupported`, cấm commit (§7.1) |
| **G8 / G9 / G10** | KHÔNG đổi, bị hoãn | Sprint 7 tạm dừng ở G7 trong suốt T0→U3 |
| **`Q9` S-Matrix** | +1 dòng | Declaration gate: feature mới khai báo state ownership (§4.2 ①) |
| **Git toàn project** (`.gitignore` UE + LFS) | backlog mới | ~nửa buổi. Làm **sau Gate 2**. Hiện đủ với: git cho plugin + copy toàn project trước mỗi gate |

---

## 10. CÁI **KHÔNG** LÀM TRONG VÒNG NÀY

> Ghi ra để lần sau khỏi bàn lại. Mỗi mục đều đã được cân nhắc và **cố ý loại**.

| Không làm | Vì sao |
|---|---|
| **Gỡ Selection / ActiveMode / EditModeStack khỏi snapshot** | Đúng nguyên tắc, sai thứ tự. 3 bug lịch sử sẽ mở lại cùng lúc. → F-Migration, sau U3, có regression khóa trước |
| **State Ownership Audit toàn project** (25 state × 6 cột) | ~110/150 ô sẽ là suy đoán không verify. → declaration gate + lazy fill (§4.2) |
| **Migrate Select/Deselect sang Command** | Câu hỏi thật là *"selection có nên nằm trong history không"*, không phải *"lưu nó kiểu gì"*. Trả lời sau F-Migration |
| **Migrate Transform / Group / Spawn / Delete sang Command** | Material Param là reference implementation. Action thứ hai làm **sau khi** U3 xanh |
| **UObject command hierarchy** (`UCommandBase → UParamCommand…`) | Sạch hơn về OO nhưng thêm lifetime/GC/debug complexity, không đáng với dự án Blueprint-heavy giai đoạn này |
| **Spike `FInstancedStruct` như một gate riêng** | Nếu History nằm sau C++ public API thì Blueprint **không cần biết** payload dùng `FInstancedStruct` hay tagged union. Đó là implementation detail → spike nhỏ **bên trong** U2 nếu cần, không phải gate |
| **Screenshot-comparison testing** | Layer sau, không phải requirement của Undo architecture |
| **CI / build farm** | Chưa cần. Release gate 3 dòng (§6.6) chạy tay là đủ tới Gate 2 |
| **Multi-target Edit Session** (nhiều pending edit đồng thời) | 1 session đồng thời làm rất nhiều edge case biến mất. Mở khi T5 thật sự cần |
| **Đổi `MaxSteps` hay tối ưu RAM history** | Ước tính: hôm nay ~10MB (50 entry × full snapshot); sau migrate ~6MB (15 snapshot × 2 + 35 command × ~200B). Kiến trúc mới **giảm** RAM dù mỗi snapshot entry nặng gấp đôi. Không cần động vào |

---

## 11. NORTH STAR

```
UI gửi INTENT
        ↓
Mutation Boundary
   ├─ Atomic Transaction          (discrete)
   └─ Interactive Edit Session    (continuous)
        ↓
Document mutation
        ↓
History ghi CHỈ committed semantic action
        ↓
ChangeSet thông báo WHAT CHANGED
        ↓
UI giữ CONTEXT bằng stable identity
        ↓
Resolver tìm runtime object hiện tại
```

Bảy nguyên tắc rút ra, đề xuất nâng thành luật dự án khi U3 đóng:

1. **UI giữ context bằng logical identity, không bằng UObject lifetime.**
2. **UObject pointer không phải identity.**
3. **History lưu semantic user action ở granularity nhỏ nhất có nghĩa**, không mặc định lưu toàn scene.
4. **Snapshot là một reversible command lớn**, không phải một timeline system thứ hai.
5. **Undo không quản lý UI state.**
6. **Interaction State migrate khỏi Document State theo** `additive → parity → regression → subtractive`.
7. **Một test chưa từng ĐỎ vì đúng invariant thì chưa phải guardrail.**

Khi đạt được, chuyện actor bị destroy/respawn không còn là sự kiện kiến trúc cấp application —
nó chỉ là implementation detail của Scene Reconstruction.

---

## 12. BƯỚC TIẾP THEO

**Không phải thiết kế thêm. Là `T0`.**

```
T0 §8.2 bước 0  →  §8.3 viết file  →  §8.4 chạy (1 xanh 1 ĐỎ)  →  §8.5 sửa  →  §8.9 trả lời 2 câu
```
