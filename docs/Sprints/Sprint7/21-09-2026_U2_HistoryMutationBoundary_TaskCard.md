# TASK CARD — U2: HISTORY ĐA HÌNH + MUTATION BOUNDARY + PARAM COMMAND

**Tác giả:** Opus 4.8 (kiến trúc sư) | **Ngày:** 21/09/2026 (tối thứ 2) | **Loại:** PLAN — chưa as-built
**Thực thi:** Sonnet 5 + cuhoang | **Gate:** U2 (trong `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md`)
**Trạng thái:** CHƯA BẮT ĐẦU. Tiền đề: T0 ĐÓNG, U1 ĐÓNG (21/09, 21:27).
**Review:** Sonnet 5, 21/09/2026 22:14 — 3 amendment trước khi execute, cuhoang đã duyệt hướng (a). Xem §0.1.

> **KHÔNG đóng dấu `[CHỨA AS-BUILT]`.** File 100% thiết kế. Thực thi xong, as-built merge vào
> canonical (`BP_UndoManager.md`, `MaterialSlotService_Reference.md`, `WBP_FurnitureInventory.md`,
> `Data_Structures.md`, `Rules/Testing.md`, `Architecture_Map.md`), KHÔNG sửa ngược file này.

**Ground truth đã đọc khi thiết kế (21/09, tối):** `BP_UndoManager.md` v1.18 (S_SceneSnapshot V4,
CaptureSnapshot/RestoreSnapshot/Undo/Redo, 3 bug lịch sử) · `MaterialSlotService_Reference.md`
(14 hàm G1: `SetSlot*Param`, `ResolveSlotIndex`, `ApplyParamsJsonToSlot` Đ12; `UMaterialParamMap`
`GetControlsForMaterial`; enum `EMaterialParamControl{Scalar,Color}`) · `EntityIdLibrary_Reference.md`
(`EnsurePersistentId`, Resolver `ResolveByPersistentId` U1) · `WBP_FurnitureInventory.md` v3.32
(`RefreshParamPanel`, 5 handler T4, seam #1-#6) · `WBP_ParamScalarRow.md`/`WBP_ParamColorRow.md` v1.1
(3 dispatcher `OnEditBegin`/`OnPreviewChanged`/`OnEditCommitted`) · `Plans/18-09-2026_...v1.md`
§2,§5,§7,§10 · `Rules/AI_Implementation_Rules.md` Q8/Q9/Q10 · `Rules/Testing.md` v1.1.

---

## 0.1 — REVIEW ADDENDUM (Sonnet, 21/09/2026 22:14 — cuhoang đã duyệt)

Sonnet review trước khi execute, phát hiện 3 chỗ cần sửa trước khi bắt tay U2.0. cuhoang chốt
hướng xử lý — card dưới đây đã cập nhật theo, KHÔNG cần đọc bản gốc song song.

1. **UI không refresh sau Undo/Redo command.** Gốc: `ApplyParamCommand` (§5.6) chỉ SET giá trị lên
   MID (mesh đổi đúng), nhưng không ai báo cho row `WBP_ParamScalarRow`/`ColorRow` cập nhật hiển
   thị → slider/swatch đứng yên dù giá trị thật đã đảo. **FIX:** `WBP_FurnitureInventory` bind
   thêm `OnHistoryChanged` (dispatcher đã có sẵn cho History-UI, §6) → gọi `RefreshParamPanel()`.
   Tận dụng dispatcher có sẵn, `BP_UndoManager` không cần biết gì về Inventory — xem seam #6 mới
   ở §5.10.
2. **`CommitInteractiveEdit` thiếu helper build full-state.** Gốc chỉ nói "Make S_SceneSnapshot
   đầy đủ" như có sẵn, nhưng phần build đó (ForEach quét actor) nằm rải trong `CaptureSnapshot` —
   nếu không tách riêng, phải chép tay 2 lần = nguồn bug mới khi sửa sau này. **FIX:** tách 2 hàm
   `BuildSceneSnapshotBase()` (quét scene, xây nội dung) + `AppendEntry()` (quản lý stack: resize/
   trim/ADD) — `CaptureSnapshot` VÀ `CommitInteractiveEdit` đều gọi chung. Xem §5.1b/§5.1c.
3. **`UNDO-SESS-06` gán nhầm tầng test** (§7 gốc ghi "U2.1 Spec + U2.5 PIE") — guard nằm trong
   Blueprint Custom Event, không phải C++, nên chỉ test được ở PIE. Đã sửa.

Không tạo file mới — sửa trực tiếp vào §4, §5.1b/5.1c (mới), §5.4, §5.10, §7, §12 bên dưới. Đúng
luật R-DOC-DONE (1 nguồn sự thật, không tách bản vá riêng).

---

## 0. MỤC TIÊU — MỘT CÂU HỎI NHỊ PHÂN

> **Kéo slider param → thả → Undo → giá trị đảo ĐÚNG, và actor KHÔNG bị destroy/respawn
> (selection + slot-highlight + Inspector còn nguyên); Redo → giá trị áp lại ĐÚNG.**

Phụ: mọi undo/redo CŨ (Move/Group/Combo/Reset...) KHÔNG hồi quy (parity tuyệt đối).

U2 là REFERENCE IMPLEMENTATION cho **đúng 1 loại command: Material Param (Scalar/Color)**. Không
migrate Transform/Group/Spawn/Delete (§10). Resolver U1 lần đầu có caller thật ở đây.

---

## 1. HƯỚNG THỰC THI — CHỐT B (additive hybrid), KHÔNG A (ép trụ E ngay)

Plan §2 vẽ end-state: stack đa hình + snapshot `{Before,After}` tự đảo (trụ E). Có 2 cách vào:

| | **A — ép trụ E ngay** | **B — additive hybrid (CHỐT)** |
|---|---|---|
| Snapshot entry | viết lại thành `{BeforeSnap, AfterSnap}` + buffer `CurrentSceneState` | **GIỮ NGUYÊN** (full state như hôm nay) |
| Command entry | delta thuần ~200B | delta `{Before,After}` **+ vẫn kèm full snapshot** (tag lên entry) |
| Undo command | apply Before targeted | apply Before targeted (y hệt) |
| Undo snapshot | restore `entry.BeforeSnap` | restore full state (y hệt hôm nay) |
| Parity với v1.18 | phải chứng minh lại | **tầm thường** (không đụng đường snapshot) |
| Rủi ro 3 bug core | CAO (viết lại RestoreSnapshot) | THẤP (chỉ THÊM nhánh dispatch) |
| RAM | giảm ngay | chưa giảm (command còn kèm full snap) |
| Ước lượng | ~2.5-3 buổi | **~1.5-2 buổi** |

**Lý do chốt B:** đúng luật migration của CHÍNH plan (`ADD → PARITY → LOCK → SUBTRACT`, §3). B =
bước ADD. Trụ E + RAM win = bước SUBTRACT làm SAU (post-U3 hoặc F-Migration), khi đã có regression
khóa. B trả lời trọn câu hỏi nhị phân (undo param targeted, không respawn) mà KHÔNG mở lại 3 bug
core. Không mâu thuẫn trụ E — chỉ **hoãn** nó đúng thứ tự.

> **Nếu cuhoang muốn ép trụ E ngay trong U2 (hướng A) → báo, tao viết lại card.** Mặc định đi B.

### 1.1 — Cơ chế B (ví dụ đời thường)

Sổ mượn sách = stack. Mỗi trang cũ là "ảnh chụp cả kệ" (snapshot). U2 thêm loại trang mới: "phiếu
sửa 1 dòng" (command) — ghi *dòng cũ → dòng mới* + số thẻ độc giả (`PersistentID`). Hoàn tác phiếu
sửa = tẩy dòng mới, viết lại dòng cũ, KHÔNG chép lại cả kệ (không mất kẹp đánh dấu = slot-highlight).
Phiếu sửa VẪN kèm 1 ảnh cả kệ ở mặt sau — để khi hoàn tác một thao tác *sau* nó (vốn cần "khôi phục
cả kệ về đúng lúc đó") vẫn có ảnh mà dùng. Ảnh thừa đó gỡ sau (bước SUBTRACT).

```
Ví dụ interleave (chứng minh B đúng):
  0: S_init        (snapshot full)
  1: C1  Roughness 0.3→0.61   (command, kèm full snap after-C1)
  2: S_move        (snapshot full, chụp lúc Roughness đang 0.61)

Undo S_move → restore full state ở entry 1 (đủ: pos gốc + Roughness 0.61). RESPAWN (đúng, Move là
              snapshot, không phải command — không vi phạm HIST-01).
Undo C1     → ResolveByPersistentId(C1.EntityID) → actor MỚI (U1 giữ ID qua respawn) → apply 0.3.
              KHÔNG respawn. Context giữ nguyên. ✓ ĐÂY là câu hỏi nhị phân.
Redo C1     → resolve → apply 0.61. Redo S_move → restore full state entry 2.
```

Parity: stack thuần-snapshot → nhánh command không bao giờ chạy → hành vi = v1.18 y hệt.

---

## 2. BA CỔNG GATE

### Q10 — CROSS-FLOW IMPACT AUDIT (BẮT BUỘC — U2 thêm undo-path mới cho state đã có consumer)

```
CROSS-FLOW IMPACT AUDIT — State #1: History stack (SnapshotHistory + CurrentIndex, BP_UndoManager)
Known producers (ghi entry):
  - CaptureSnapshot(name)  [DOC v1.18] ← ~10 caller: GizmoController(Move/Rotate/Scale),
      IM(Select/Deselect/BoxSelect/Group), ComboManager, Handle_ScalarCommit, Handle_ColorCommit,
      Handle_ResetSlot/ResetParams/ResetAll, BTN_ResetSlot/ResetAll
  - RestoreCurrentSnapshot() [DOC v1.12] ← ComboManager rollback
Known consumers (đọc/dịch cursor):
  - UndoLastAction / RedoLastAction [DOC] · RestoreSnapshot [DOC] · (MỚI) History accessors + JumpToHistoryIndex
Persistence: Snapshot in-memory (Kho 1). KHÔNG EMS, KHÔNG Recent, KHÔNG Combo JSON.
Impact decision:
  - CaptureSnapshot (mọi caller CŨ)          → NO CHANGE (vẫn tạo entry EntryKind=Snapshot; wrap trong suốt)
  - Handle_ScalarCommit / Handle_ColorCommit → UPDATE (đổi từ CaptureSnapshot thẳng → CommitInteractiveEdit)
  - UndoLastAction / RedoLastAction          → UPDATE (thêm dispatch: EntryKind==ParamCommand → targeted)
  - RestoreCurrentSnapshot                   → NO CHANGE (Combo rollback vẫn full snapshot)
  - Reset×3 (ResetSlot/ResetParams/ResetAll) → NO CHANGE ở U2 (giữ CaptureSnapshot full — KHÔNG migrate,
                                                xem §9; là discrete atomic, migrate sau khi ref-impl xanh)
Invariant xuyên luồng: mọi entry trong stack, dù Snapshot hay ParamCommand, PHẢI có Label != "" và
  đảo được đúng 1 chiều — Undo(entry) rồi Redo(entry) trả scene về đúng trạng thái trước Undo.
```

```
CROSS-FLOW IMPACT AUDIT — State #2: Param value (MID runtime + MaterialSlots[].ParamsJson)
Known producers: 5 handler T4 (Preview/Commit×2 + ResetParams), Reset×2 nút, ApplyLoadedMaterialToSlot,
  RestoreSnapshot Step4 (SET MaterialSlots), ApplyParamsJsonToSlot (Đ12: texture chỉ log)
Known consumers: RefreshParamPanel (seed row từ MID), EMS save (SerializeSlotRecords), snapshot capture
Impact decision:
  - Handle_ScalarPreview/ColorPreview  → UPDATE (đổi thành UpdateInteractiveEdit; vẫn SetSlot*Param LIVE)
  - Handle_ScalarBegin/ColorBegin      → NEW (bind OnEditBegin → BeginInteractiveEdit, đọc Before)
  - Handle_ScalarCommit/ColorCommit    → UPDATE (→ CommitInteractiveEdit thay CaptureSnapshot)
  - SetSlotScalarParam/VectorParam     → NO CHANGE (dùng lại nguyên) ; +NEW GetSlot*Param (reader Before)
  - Texture param                      → REFUSE: builder command trả Unsupported, CẤM commit (Đ12, §7.1 plan)
Invariant: giá trị áp lên MID lúc Preview = giá trị đọc lại được ở Commit (Before/After round-trip khớp).
```

```
CROSS-FLOW IMPACT AUDIT — State #3: Selection context (SelectedActors / TargetFurnitureActor / SelectedSlotIndex)
Known producers: OnMeshSelected, NotifyViewportSlotClick, OnSlotSwatchClicked, RestoreSnapshot
Known consumers: RefreshParamPanel, 5 handler (guard IsValid Target && idx>=0)
Impact decision (Edit Session termination):
  - OnMeshSelected (đổi selection)     → CANCEL active session (rollback Before) TRƯỚC khi đổi target
  - CloseMaterialInspector             → CANCEL active session
  - đổi slot (swatch click / viewport) → CANCEL active session
  - RestoreSnapshot (undo/redo)        → session KHÔNG được sống xuyên undo (Begin/Commit cùng 1 lượt drag)
Invariant: KHÔNG bao giờ tồn tại session "mồ côi" — mọi abnormal termination = Cancel + Rollback (plan §2.2).
```

### Q9 — S-MATRIX GATE (BẮT BUỘC — Edit Session react `SelectedActors`)

Param nhắm `TargetFurnitureActor` = Primary (single). Theo **luật riêng Material**: S2/S3/S4/S8 mặc
định `⚠`, KHÔNG được ghi `→S1`.

**TẦNG 1 — S-SCAN** (câu hỏi: *khi ĐANG có session param mở mà selection rơi vào trạng thái này thì sao*):

| ID | Trạng thái | Ô |
|---|---|---|
| S0 | Không chọn gì | `N/A: không có Target → không mở được session (guard IsValid Target fail)` |
| S1 | 1 mesh rời | `→ chuẩn`: Target=mesh đó, session chạy bình thường |
| S2 | N mesh rời | `⚠ session chỉ áp Primary; đổi Primary giữa drag = Cancel` |
| S3 | 1 group thường | `⚠ Target=Primary trong group; group không đổi ngữ nghĩa param, nhưng đổi selection = Cancel` |
| S4 | 1 combo | `⚠ như S3; combo root SourceComboID không ảnh hưởng param slot` |
| S5 | 1 mesh trong group (edit mode) | `→S1: Target là mesh đó, giống mesh rời về mặt param` |
| S6 | 1 mesh trong combo (edit mode) | `→S5` |
| S7 | sub-group nested | `N/A: không phải mesh lá → không có slot param → session không mở` |
| S8 | Mix (group/combo + mesh rời) | `⚠ Primary quyết Target; Ctrl-click đổi Primary giữa drag = Cancel` |
| S9 | Selection do máy sinh (sau RestoreSnapshot/SpawnFurnitureCopy) | `⚠ actor instance MỚI — session KHÔNG được sống xuyên restore; nếu đang preview mà Undo → Cancel preview TRƯỚC (SESS-07)` |

**TẦNG 2 — X-CHECK cho ô `⚠` (S2,S3,S4,S8,S9):**

| # | Hệ | Trả lời cho param session |
|---|---|---|
| X1 Undo | ⚠ ô: Begin KHÔNG snapshot; Commit tạo 1 command entry; Preview KHÔNG entry. `bIsRestoring` True → CẤM mở/commit session |
| X2 Persistence (4 kho) | Chỉ Kho 1 (history in-memory). KHÔNG Kho 2/3/4 |
| X4 Selection sau action | Commit KHÔNG đổi selection; Target/Primary giữ nguyên sau commit |
| X9 Material state | Target=Primary; `SelectedSlotIndex` phải >=0 mới mở session; đổi slot/selection giữa session = Cancel + rollback Before |
| — S9 riêng | Sau RestoreSnapshot: nếu có session đang mở (edge kéo dài) → đã Cancel ở bước Undo dispatch (SESS-07) trước khi restore chạy |

**Test cả ô N/A (S0,S7):** xác nhận guard `IsValid(Target) && SelectedSlotIndex>=0` chặn mở session
(không phải "vô tình không xảy ra").

### Q8 — áp cho từng node flow ở §5 (mỗi flow 1 dòng Q8 riêng, VISIBLE).

---

## 3. QUYẾT ĐỊNH KIẾN TRÚC (chốt + lý do — đọc TRƯỚC khi build)

### QĐ1 — Command payload = C++ USTRUCT `FMaterialParamCommand` (BlueprintType)

Nhúng vào BP struct `S_SceneSnapshot` được (tiền lệ: `S_FurniturePlacement` đã chứa
`Array<FMaterialSlotRecord>` C++). C++ để hàm build/refuse-texture Spec-test được (không cần PIE).

```cpp
UENUM(BlueprintType)
enum class EParamCmdType : uint8 { Scalar, Color };   // Texture: KHÔNG có → builder từ chối (Đ12)

USTRUCT(BlueprintType)
struct FMaterialParamCommand
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadWrite) FString  EntityID;       // PersistentID actor đích (U1)
    UPROPERTY(BlueprintReadWrite) FString  SlotName;
    UPROPERTY(BlueprintReadWrite) int32    SlotHintIndex = -1;
    UPROPERTY(BlueprintReadWrite) FName    ParamName;
    UPROPERTY(BlueprintReadWrite) EParamCmdType Type = EParamCmdType::Scalar;
    UPROPERTY(BlueprintReadWrite) float        BeforeScalar = 0.f;
    UPROPERTY(BlueprintReadWrite) float        AfterScalar  = 0.f;
    UPROPERTY(BlueprintReadWrite) FLinearColor BeforeColor  = FLinearColor::White;
    UPROPERTY(BlueprintReadWrite) FLinearColor AfterColor   = FLinearColor::White;
};
```

### QĐ2 — Envelope = THÊM FIELD vào `S_SceneSnapshot` (additive), KHÔNG struct wrapper mới

Đổi type `SnapshotHistory : Array<S_SceneSnapshot>` sang wrapper mới = phải sửa TOÀN BỘ code undo
core (nơi 3 bug sống) → rủi ro A. Thay vào đó **thêm 2 field vào S_SceneSnapshot** (đã làm 4 lần
an toàn: RowName/GroupID/MaterialSlots/PersistentID):

```
S_SceneSnapshot  (thêm, Version → 5):
  + EntryKind   : E_HistoryEntryKind  (Snapshot | ParamCommand)   default Snapshot
  + ParamCmd    : FMaterialParamCommand                            default rỗng
  (giữ nguyên toàn bộ field V4: ActionName, Meshes, SelectedMeshIndices, ActiveMode, Groups,
   EditModeStackSnapshot, Version...)
```

Entry Snapshot cũ: `EntryKind=Snapshot`, `ParamCmd` bỏ trống → mọi caller CŨ không đổi. Entry param
mới: `EntryKind=ParamCommand`, `ParamCmd` đầy + Meshes VẪN chụp full (đặc trưng hybrid B).

> Version=5 chỉ để đánh dấu; tương thích ngược: entry V<5 mặc định `EntryKind=Snapshot` (đúng).

### QĐ3 — Reader Before ở C++ (`GetSlot*Param`), Resolve/Apply ở Blueprint

- **Before đọc bởi CORE, KHÔNG từ widget** (plan §2.2). Thêm 2 C++ reader đối xứng với setter:
  `GetSlotScalarParam` / `GetSlotVectorParam` (đọc MID; false nếu chưa có MID → fallback
  Min/white như `RefreshParamPanel` seed).
- **Apply reversal ở Blueprint** (`ApplyParamCommand`): `ResolveByPersistentId` (BP, SceneManager)
  → GET mesh → `SetSlotScalarParam/VectorParam`. Đọc `PersistentID` (biến BP) → không cần C++
  reflection (tránh mangle tên).

### QĐ4 — Edit Session = state trên `BP_UndoManager`; state-machine THUẦN test C++

Session data (Before, phase) là class var trên UndoManager. Guard THUẦN (Before==After→no entry;
double-commit; update-after-end) test bằng C++ Spec (`UParamCommandLibrary`). Apply World-side test
bằng PIE. Chia đúng tầng Testing.md.

### QĐ5 — Begin session = LAZY trên `OnEditBegin` có sẵn (không dựng event mới)

Row đã bắn `OnEditBegin` lúc `OnMouseCaptureBegin`/`OnInteractionBegin` (hiện chưa bind). Bind nó →
`BeginInteractiveEdit`. **1 session đồng thời** (plan §2.2): Begin mới khi session cũ còn mở →
settle cũ trước (Commit nếu hợp lệ, không thì Cancel). Không `Map<SessionID>`.

### QĐ6 — U1 Resolver có caller đầu tiên ở U2 (DEVIATION có chủ đích so plan)

Plan ghi Resolver caller = U3. Nhưng undo command targeted BẮT BUỘC resolve actor bằng ID (không
được cầm con trỏ cũ — nguyên tắc #2). Nên U2 là chỗ Resolver cần thật. U3 chồng thêm ChangeSet +
giữ slot-context Inspector lên trên. Ghi DEVIATION khi as-built.

---

## 4. ASSET MỚI / SỬA — TÓM TẮT

**C++ (plugin FurnitureToolkit):**
| Asset | Loại | Nội dung |
|---|---|---|
| `FMaterialParamCommand` + `EParamCmdType` | USTRUCT/UENUM (file `ParamCommandTypes.h`) | §3 QĐ1 |
| `UParamCommandLibrary` | BlueprintFunctionLibrary mới | `BuildScalarCommand`/`BuildColorCommand`/`IsNoOpCommand`/`RefuseTexture` (PURE, Spec-test) |
| `GetSlotScalarParam` / `GetSlotVectorParam` | +2 hàm vào `UMaterialSlotService` | reader Before (đối xứng setter) |
| `Tests/ParamCommandTests.cpp` | Spec `FurnitureTool.Undo.U2_Command` | UNDO-HIST-03, SESS-04, Đ12-refuse |

**Blueprint:**
| Asset | Sửa |
|---|---|
| `S_SceneSnapshot` (UserDefinedStruct) | +`EntryKind`, +`ParamCmd`; Version→5 |
| `E_HistoryEntryKind` (enum mới) | `Snapshot`, `ParamCommand` |
| `BP_UndoManager` | +session vars; **+`BuildSceneSnapshotBase()` + `AppendEntry()`** (tách từ `CaptureSnapshot`, dùng chung — review #2); +`BeginInteractiveEdit`/`UpdateInteractiveEdit`/`CommitInteractiveEdit`/`CancelInteractiveEdit`; +`ApplyParamCommand`; sửa `UndoLastAction`/`RedoLastAction` (dispatch); +History accessors + `OnHistoryChanged` + `JumpToHistoryIndex` |
| `WBP_FurnitureInventory` | bind `OnEditBegin`→`Handle_*Begin` (mới); sửa 4 handler Preview/Commit → gọi session; +Cancel seam (OnMeshSelected/Close/đổi slot); **+bind `OnHistoryChanged`→`RefreshParamPanel()`** (seam #6, review #1) |

---

## 5. CHI TIẾT NODE FLOW (Q8 mỗi flow)

### 5.1 — `BP_UndoManager` session vars (class var)
```
Sess_Active   : Boolean (default False)
Sess_Cmd      : FMaterialParamCommand   ← Before điền lúc Begin, After điền lúc Commit
Sess_Phase    : E (None | Previewing)   ← state machine SESS
```
Clear ở Event End Play (Sess_Active=False).

### 5.1b — `BuildSceneSnapshotBase(ActionName)` → S_SceneSnapshot — Function (MỚI, review #2)
> Tách từ `CaptureSnapshot` hiện tại: gộp Step 0/0b/2/3/4/6(phần Make) — TOÀN BỘ "quét scene xây
> nội dung entry". KHÔNG đụng phần "quản lý stack" (xem `AppendEntry`, 5.1c). `CaptureSnapshot` VÀ
> `CommitInteractiveEdit` đều gọi hàm này — tránh chép tay ForEach-actor build 2 lần.
```
0.  CLEAR TempSelectedIndices
0b. Call GetGroupsForSnapshot → SET TempGroups
    GET InputManager.EditModeStack → SET TempEditModeStack
2.  CLEAR TempMeshes
3.  Get All Actors With Tag("FurnitureSpawned") → ForEach → build S_FurniturePlacement (Y HỆT
    CaptureSnapshot Step 3 hiện tại — đủ mọi field kể cả RowName/GroupID/MaterialSlots/PersistentID)
    → ADD to TempMeshes
4.  Build TempSelectedIndices (Y HỆT Step 4 hiện tại — nested ForEach With Break)
6.  GET ActiveMode
    → Make S_SceneSnapshot(ActionName, Meshes=TempMeshes, SelectedMeshIndex=-1,
       SelectedMeshIndices=TempSelectedIndices, ActiveMode, Version=5, Groups=TempGroups,
       EditModeStackSnapshot=TempEditModeStack, EntryKind=Snapshot [default], ParamCmd=[default rỗng])
    → Return Entry
```
`Q8:` Function | IsValid qua Cast trong ForEach (như CaptureSnapshot hiện tại) | mọi nhánh có đích | không latent | 6A: N/A (đọc thuần — build nội dung, không phải đường ngược).

### 5.1c — `AppendEntry(Entry: S_SceneSnapshot)` — Function (MỚI, review #2)
> Tách từ `CaptureSnapshot`: gộp Step 1 (resize redo stack) + Step 5 (trim MaxSteps) + ADD + tăng
> `CurrentIndex`. Độc lập biến với `BuildSceneSnapshotBase` (không đụng chung Temp*) → an toàn đổi
> thứ tự gọi so với `CaptureSnapshot` gốc (build trước, trim/add sau — ngược lại bản cũ trim trước).
> **KHÔNG giả định suông** — đây chính là lý do U2.3 PARITY GATE bắt buộc chạy đủ REG-01..05.
```
▶→ Branch(CurrentIndex < Length(SnapshotHistory) - 1)  True → Array Resize(CurrentIndex + 1)
▶→ Branch(Length(SnapshotHistory) >= MaxSteps)  True → Remove Index 0 → CurrentIndex - 1
▶→ ADD Entry to SnapshotHistory → CurrentIndex + 1
▶→ Broadcast OnHistoryChanged
```
`Q8:` Function | không cần IsValid (thao tác Array/Int thuần) | 2 Branch đều có đích tiếp | không latent | 6A: N/A.

**`CaptureSnapshot(ActionName)` SỬA còn lại (chữ ký + 10 caller cũ KHÔNG đổi):**
```
▶→ Entry = BuildSceneSnapshotBase(ActionName)     ← EntryKind=Snapshot mặc định, đúng ý nghĩa cũ
▶→ AppendEntry(Entry)
```

### 5.2 — `BeginInteractiveEdit(EntityID, SlotName, HintIndex, ParamName, Type)` — Custom Event
```
▶→ Branch(bIsRestoring)  True → Return (CẤM mở session giữa restore — X1)
▶→ Branch(Sess_Active)   True → CommitInteractiveEdit()  ← settle session cũ (QĐ5, 1 session)
▶→ Resolve mesh: SceneManager.ResolveByPersistentId(EntityID) → (Actor,bFound)
     bFound=False → Return (không mở)
▶→ đọc Before:
     Type==Scalar → GetSlotScalarParam(Mesh,Slot,Hint,ParamName, OutF,ok) → Sess_Cmd.BeforeScalar = OutF (ok=False→fallback đã lo trong C++)
     Type==Color  → GetSlotVectorParam(...) → Sess_Cmd.BeforeColor
▶→ SET Sess_Cmd.{EntityID,SlotName,SlotHintIndex,ParamName,Type} ; Sess_Phase=Previewing ; Sess_Active=True
```
`Q8:` Custom Event → class var OK | IsValid qua bFound guard | mọi Branch có đích (Return/tiếp) | không latent | 6A: Cancel là đường ngược, xem 5.5.

### 5.3 — `UpdateInteractiveEdit(Value)` — (không tạo history) — gọi TỪ Preview handler
> Thực chất preview vẫn do handler cũ `SetSlot*Param` LIVE. Update chỉ ghi giá trị chạy vào runtime;
> KHÔNG đụng Sess_Cmd.After (After chỉ chốt lúc Commit). Giữ handler Preview gần như cũ, chỉ thêm
> guard "chỉ chạy khi Sess_Active" để bỏ preview mồ côi.

### 5.4 — `CommitInteractiveEdit()` — Custom Event
```
▶→ Branch(Sess_Active AND Sess_Phase==Previewing)  False → Return (SESS-06: commit khi không có session → bỏ)
▶→ đọc After hiện tại: GetSlot*Param(...) → Sess_Cmd.AfterScalar / AfterColor
▶→ Branch( UParamCommandLibrary.IsNoOpCommand(Sess_Cmd) )       ← SESS-04
     True  → Sess_Active=False ; Sess_Phase=None ; Return (KHÔNG tạo entry)
     False ▶→ Entry = BuildSceneSnapshotBase(Label(Sess_Cmd))     ← dùng CHUNG helper với CaptureSnapshot (5.1b)
            SET Entry.EntryKind=ParamCommand ; Entry.ParamCmd=Sess_Cmd
            ▶→ AppendEntry(Entry)                                 ← tự lo resize/trim/ADD/Broadcast (5.1c)
            ▶→ Sess_Active=False ; Sess_Phase=None
```
> Label(cmd) = "Chỉnh "/"Đổi màu " + ParamName (giữ chuỗi cũ các handler đang dùng).
`Q8:` Custom Event | guard Sess_Active | mọi nhánh có đích | không latent | 6A: undo command xem 5.6.

### 5.5 — `CancelInteractiveEdit()` — Custom Event  (6A của session)
```
▶→ Branch(Sess_Active)  False → Return
▶→ apply Before về runtime: ApplyParamCommand(Sess_Cmd, bUseBefore=True)   ← rollback preview
▶→ Sess_Active=False ; Sess_Phase=None
   (KHÔNG tạo entry — SESS-05)
```

### 5.6 — `ApplyParamCommand(Cmd, bUseBefore)` — Function (đảo/áp 1 command; KHÔNG latent)
```
▶→ SceneManager.ResolveByPersistentId(Cmd.EntityID) → (Actor,bFound)
     bFound=False → Return False   (actor không còn — logical entity mất, U3 sẽ phân biệt tinh hơn)
▶→ GET Actor.FurnitureMesh
▶→ Select value = bUseBefore ? Before : After
▶→ Cmd.Type==Scalar → SetSlotScalarParam(Mesh, Actor.MaterialSlots[ref], Cmd.SlotName, Cmd.SlotHintIndex, Cmd.ParamName, value)
   Cmd.Type==Color  → SetSlotVectorParam(...)
▶→ Return ok
```
`Q8:` Function | IsValid qua bFound + Cast (Actor đã type BP_FurnitureActor) | nhánh Scalar/Color merge Return | không latent | 6A: chính hàm này LÀ đường ngược.

### 5.7 — `UndoLastAction` (Alt+Z) — SỬA: thêm dispatch
```
▶→ Branch(Sess_Active)  True ▶→ CancelInteractiveEdit()  ← SESS-07: hủy preview TRƯỚC, rồi mới undo entry cũ
▶→ Branch(CurrentIndex <= 0)  True → STOP
▶→ EntryToUndo = SnapshotHistory[CurrentIndex]
▶→ Branch(EntryToUndo.EntryKind == ParamCommand)
     True  ▶→ ApplyParamCommand(EntryToUndo.ParamCmd, bUseBefore=True)   ← TARGETED, KHÔNG respawn (HIST-01)
            ▶→ CurrentIndex - 1
     False ▶→ CurrentIndex - 1 → RestoreSnapshot(CurrentIndex)           ← Y HỆT v1.18 (HIST-02, parity)
▶→ Broadcast OnHistoryChanged
```
> ⚠️ Ghi chú cursor: nhánh Snapshot GIỮ nguyên semantics cũ (dịch cursor RỒI restore index mới).
> Nhánh Command đảo entry Ở CurrentIndex rồi mới lùi — vì command tự chứa Before/After, không cần
> "restore trạng thái index trước". Hai nhánh khác vi tế — Sonnet PHẢI test cả 2 (§7).
`Q8:` Function | guard CurrentIndex<=0 | 2 nhánh EntryKind đều có đích | không latent | 6A: đây là đường ngược, Redo là xuôi.

### 5.8 — `RedoLastAction` (Shift+Alt+Z) — SỬA đối xứng
```
▶→ Branch(Sess_Active) True → CancelInteractiveEdit()   (redo giữa preview: hủy preview trước)
▶→ Branch(CurrentIndex >= Length-1)  True → STOP
▶→ SET CurrentIndex = CurrentIndex + 1        ← dùng OUTPUT pin của SET (bug cũ v1.x)
▶→ EntryToRedo = SnapshotHistory[CurrentIndex (output pin)]
▶→ Branch(EntryToRedo.EntryKind == ParamCommand)
     True  ▶→ ApplyParamCommand(EntryToRedo.ParamCmd, bUseBefore=False)   ← apply After, KHÔNG respawn
     False ▶→ RestoreSnapshot(CurrentIndex output pin)                     ← Y HỆT v1.18
▶→ Broadcast OnHistoryChanged
```
`Q8:` như 5.7 | ⚠ dùng output pin của SET CurrentIndex (không GET lại).

### 5.9 — History accessors (History-UI readiness) — xem §6

### 5.10 — Rewire 5 handler trong `WBP_FurnitureInventory`
```
Bind (trong RefreshParamPanel, ForEach Controls, mỗi row):
  OnEditBegin      → Handle_ScalarBegin / Handle_ColorBegin       ← MỚI (row đã có sẵn dispatcher này)
  OnPreviewChanged → Handle_ScalarPreview / Handle_ColorPreview   ← GIỮ (thêm guard Sess_Active)
  OnEditCommitted  → Handle_ScalarCommit / Handle_ColorCommit     ← SỬA nội dung

Handle_ScalarBegin(ParamName)          ← Custom Event
▶→ Branch(IsValid(TargetFurnitureActor) AND SelectedSlotIndex>=0)
     True ▶→ UndoManagerRef.BeginInteractiveEdit(
                 TargetFurnitureActor.PersistentID, SelectedSlotName, SelectedSlotIndex, ParamName, Scalar)
     False → (dead-end)

Handle_ScalarPreview(ParamName, Value)  ← GIỮ SetSlotScalarParam LIVE (như T4), +không đổi
Handle_ScalarCommit(ParamName, Value)
▶→ Branch(IsValid Target AND idx>=0)
     True ▶→ GET Mesh ▶→ SetSlotScalarParam(...) ●→ ok        ← đảm bảo After đã áp lên MID
            ▶→ Branch(ok) True ▶→ UndoManagerRef.CommitInteractiveEdit()   ← thay CaptureSnapshot cũ
                          False → (dead-end)
     False → (dead-end)

(Color: đối xứng — Handle_ColorBegin/Preview/Commit, Type=Color, SetSlotVectorParam)
```
> **Đổi lớn:** Commit KHÔNG còn gọi `CaptureSnapshot("Chỉnh "+param)` (full snapshot). Giờ gọi
> `CommitInteractiveEdit()` — hàm này tự chốt After (đọc MID), so Before, tạo command entry. Before
> do `BeginInteractiveEdit` đọc lúc `OnEditBegin`.

**Cancel seam (Impact #3):**
```
OnMeshSelected (nhánh Material, ĐẦU) ▶→ UndoManagerRef.CancelInteractiveEdit()   ← trước khi đổi Target
CloseMaterialInspector (ĐẦU)          ▶→ UndoManagerRef.CancelInteractiveEdit()
OnSlotSwatchClicked / NotifyViewportSlotClick (khi đổi slot khác) ▶→ CancelInteractiveEdit() trước khi SET SelectedSlotIndex mới
```
`Q8` (mỗi Handle): Custom Event (L9 — Begin/Preview/Commit ở Event Graph) | guard IsValid Target && idx>=0 | dead-end nhánh False | không latent | 6A: Cancel seam lo đường ngược.

> ⚠️ **Watch-item (review, không sửa card thêm — để ý lúc PIE U2.4):** `SwitchInventoryMode` KHÔNG
> có trong danh sách Cancel seam trên. Mouse-capture (đang kéo slider) chặn được CLICK chuột đổi
> tab, nhưng nếu có PHÍM TẮT đổi tab thì keyboard không bị capture chặn → session có thể mồ côi
> giữa lúc đổi tab. Sonnet xác nhận bằng PIE thật ở U2.4 (thử đổi tab bằng phím tắt nếu tồn tại,
> giữa lúc đang kéo slider) — không đoán trước, không sửa card cho tới khi có bằng chứng thật.

**Seam #6 — History refresh (MỚI, review #1):**
```
Event Construct (APPEND, cạnh Bind OnCloseRequested/OnResetParamsRequested hiện có):
▶→ Bind UndoManagerRef.OnHistoryChanged → Handle_HistoryChanged

Handle_HistoryChanged()   ← Custom Event
▶→ RefreshParamPanel()    ← hàm tự guard IsInspectorVisible() ở đầu — gọi thừa lúc panel đóng vẫn an toàn (no-op)
```
> Phủ đủ 3 nguồn cần refresh: Undo/Redo nhánh Command (giá trị đảo qua `ApplyParamCommand`, row
> phải seed lại — ĐÂY LÀ FIX CHO REVIEW #1) + Undo/Redo nhánh Snapshot (đã có `OnRestoreCompleted`
> lo, gọi thêm ở đây dư nhưng vô hại) + `JumpToHistoryIndex` (§6, để dành cho widget History sau).
`Q8:` Custom Event | không cần IsValid (RefreshParamPanel tự guard) | không dead-end | không latent | 6A: N/A (đọc-refresh thuần).

---

## 6. HISTORY-UI READINESS — scaffolding cho cửa sổ History (Photoshop)

> **KHÔNG dựng widget trong U2.** Chỉ mở API để widget History sau này gọi. cuhoang muốn cửa sổ
> giống ảnh Photoshop (list state theo thời gian, icon theo loại, click 1 state → nhảy tới).

Ánh xạ Photoshop → U2 chuẩn bị gì:

| Photoshop History | U2 chuẩn bị | Để dành |
|---|---|---|
| List dòng theo thứ tự (Clone Stamp, Crop...) | `GetHistoryLabels()` (ActionName mỗi entry) — đã có Label mọi entry | — |
| Icon từng dòng (loại thao tác) | `GetHistoryKinds()` → `E_HistoryEntryKind` (Snapshot/ParamCommand) = icon hint thô | icon chi tiết hơn (category) sau |
| Dòng "current" sáng | `GetCurrentIndex()` | — |
| Click 1 dòng → nhảy tới đúng state | `JumpToHistoryIndex(Target)` | non-linear history |
| Panel tự refresh khi có thao tác | Dispatcher `OnHistoryChanged` (broadcast ở Capture/Commit/Undo/Redo/Jump) | — |
| Snapshot đặt tên (ảnh chụp riêng) | — | **để dành** (đừng trộn checkpoint với undo entry — plan §2.1) |

**Hàm mới trên `BP_UndoManager` (đọc-thuần, trừ Jump):**
```
GetHistoryCount()  → Int                 : Return Length(SnapshotHistory)
GetCurrentIndex()  → Int                 : Return CurrentIndex
GetHistoryLabels() → Array<String>       : ForEach SnapshotHistory → ADD .ActionName
GetHistoryKinds()  → Array<E_HistoryEntryKind> : ForEach → ADD .EntryKind
Dispatcher OnHistoryChanged()            : Broadcast cuối Capture/Commit/Undo/Redo/Jump

JumpToHistoryIndex(Target : Int)  — Function
▶→ Branch(bIsRestoring) True → Return                       (an toàn)
▶→ Clamp Target vào [0, Length-1]
▶→ While CurrentIndex > Target : UndoLastAction()           (nhưng KHÔNG broadcast mỗi bước — xem dưới)
▶→ While CurrentIndex < Target : RedoLastAction()
▶→ Broadcast OnHistoryChanged (1 lần cuối)
```
> ⚠️ **Đệ quy/loop:** dùng vòng lặp Blueprint thuần (While) + depth guard = Length (chống vô hạn nếu
> cursor kẹt). Vì `UndoLastAction`/`RedoLastAction` mỗi bước tự broadcast, cân nhắc tách nhân
> `UndoStep_NoBroadcast()`/`RedoStep_NoBroadcast()` để Jump gọi, tránh N lần broadcast (UI giật).
> **U2 chỉ cần `JumpToHistoryIndex` chạy đúng + test; tối ưu broadcast là nice-to-have.**

Invariant: `JumpToHistoryIndex(K)` cho scene y hệt như bấm Undo/Redo tuần tự tới K (HISTUI-02).

---

## 7. DANH MỤC INVARIANT `UNDO-*` → BẰNG CHỨNG

> Prefix `UNDO-` BẮT BUỘC (plan §5). Mỗi mã xuất hiện trong tên test.

### U2 — History / Mutation Boundary (từ plan §5)
| Mã | Invariant | Chứng ở | Tầng |
|---|---|---|---|
| `UNDO-HIST-01` | Undo command → KHÔNG destroy/respawn actor nào | U2.5 PIE (đếm actor trước/sau = nhau) | PIE |
| `UNDO-HIST-02` | Undo qua snapshot entry → KHÔNG replay command | U2.3 regression (parity v1.18) | PIE |
| `UNDO-HIST-03` | Command commit chỉ khi round-trip đủ state nó tuyên bố (apply After rồi Before = giá trị gốc) | U2.1 Spec | Spec |
| `UNDO-SESS-01` | Begin đọc+giữ Before trong core (không widget) | U2.4 PIE (Print Before) | PIE |
| `UNDO-SESS-02` | Preview update KHÔNG tạo entry | U2.5 PIE (kéo 100 khấc → count không đổi) | PIE |
| `UNDO-SESS-03` | Commit tạo ĐÚNG 1 entry (Before gốc + After cuối) | U2.5 PIE | PIE |
| `UNDO-SESS-04` | Before==After → KHÔNG tạo entry | U2.1 Spec (`IsNoOpCommand`) + U2.5 PIE | Spec+PIE |
| `UNDO-SESS-05` | Cancel → restore Before, KHÔNG entry | U2.5 PIE (đổi selection giữa drag) | PIE |
| `UNDO-SESS-06` | Update/Commit sau khi session kết thúc → bị từ chối | U2.5 PIE (guard nằm trong BP Custom Event, không test được ở Spec C++ — sửa review #3) | PIE |
| `UNDO-SESS-07` | Undo lúc previewing → cancel preview TRƯỚC, rồi undo entry cũ | U2.5 PIE | PIE |
| `UNDO-CMD-TEX` | Command texture → Unsupported, CẤM commit (Đ12) | U2.1 Spec (refuse) | Spec |

### U2 — History-UI readiness (mới, cho cửa sổ History)
| Mã | Invariant | Chứng ở |
|---|---|---|
| `UNDO-HISTUI-01` | `GetHistoryLabels().Length == GetHistoryCount()`, mọi label != "" | U2.6 PIE |
| `UNDO-HISTUI-02` | `JumpToHistoryIndex(K)` = Undo/Redo tuần tự tới K (scene + value khớp) | U2.6 PIE |
| `UNDO-HISTUI-03` | `OnHistoryChanged` bắn sau mọi Capture/Commit/Undo/Redo/Jump | U2.6 PIE (đếm broadcast) |

### Regression (parity B) — KHÔNG hồi quy
| Mã | Kiểm |
|---|---|
| `UNDO-REG-01` | Move/Rotate/Scale → Undo/Redo đúng (như v1.18) |
| `UNDO-REG-02` | Group/Ungroup + edit-mode bar → Undo đúng (bug A12/B1 không mở lại) |
| `UNDO-REG-03` | Combo spawn/replace + rollback (RestoreCurrentSnapshot) đúng |
| `UNDO-REG-04` | Select/Deselect xen kẽ → Undo không nhảy cóc (bug stale-index) |
| `UNDO-REG-05` | Reset×3 (ResetSlot/ResetParams/ResetAll) → Undo đúng (vẫn full snapshot) |

---

## 8. THỨ TỰ THỰC THI (mỗi bước 1 checkpoint nhị phân — LUẬT DỪNG cứng)

> **Ngân sách PIE** (`Rules/Testing.md` §2): U2.1 Spec KHÔNG tốn PIE. U2.3→U2.6 tốn PIE — gom cụm,
> restart editor mỗi 2-3 PIE (workaround GPU). **U2 không xanh ở bước nào → DỪNG, KHÔNG nối UI tiếp.**

### U2.0 — Backup (đường lùi, BẮT BUỘC trước khi đụng core)
```
[ ] Backup toàn project: Lighting_Mnger_BACKUP_21-09-2026_preU2  (GIỮ Content/Plugins/Source/Config/*.uproject; BỎ Saved/Intermediate/DDC/Binaries)
[ ] git commit repo plugin FurnitureToolkit (mốc sau U1)
```

### U2.1 — C++ types + reader + command lib + Spec (PURE, KHÔNG PIE)
```
[ ] ParamCommandTypes.h: FMaterialParamCommand + EParamCmdType (§3 QĐ1)
[ ] UMaterialSlotService: +GetSlotScalarParam / +GetSlotVectorParam (reader Before)
[ ] UParamCommandLibrary: BuildScalarCommand/BuildColorCommand/IsNoOpCommand (+ texture refuse)
[ ] Tests/ParamCommandTests.cpp — Spec FurnitureTool.Undo.U2_Command:
       [UNDO-HIST-03] build scalar → After rồi Before khớp gốc
       [UNDO-SESS-04] IsNoOpCommand(Before==After) == true
       [UNDO-CMD-TEX] không có builder texture → refuse path trả false
[ ] Compile sạch → 3 test XANH → NEGATIVE CONTROL (phá IsNoOpCommand thành luôn false → SESS-04 ĐỎ) → khôi phục XANH
```
CHECKPOINT: type + guard thuần đúng, test biết kêu. → U2.2

### U2.2 — Struct + enum (additive, ĐỤNG core struct — cẩn thận)
```
[ ] E_HistoryEntryKind (Snapshot|ParamCommand)
[ ] S_SceneSnapshot +EntryKind +ParamCmd; Version→5; recompile mọi BP dùng struct
[ ] Compile; mở PIE 1 lần smoke: thao tác cũ bất kỳ (Move) → Undo vẫn chạy (chưa đụng logic mới)
```
CHECKPOINT: struct mở rộng không vỡ compile/undo cũ. → U2.3

### U2.3 — Undo/Redo dispatch + 2 helper tách (PARITY GATE 🔴)
```
[ ] Tách BuildSceneSnapshotBase(ActionName) + AppendEntry(entry) từ CaptureSnapshot (§5.1b/5.1c)
[ ] CaptureSnapshot gọi 2 helper theo thứ tự MỚI (build trước, append sau — xem ghi chú thứ tự ở 5.1c)
[ ] UndoLastAction/RedoLastAction: thêm nhánh EntryKind==ParamCommand (§5.7/5.8) — nhưng CHƯA có
    command nào sinh ra (chưa rewire handler) → mọi entry vẫn Snapshot → nhánh command KHÔNG chạy
[ ] W7: xác nhận CurrentIndex semantics thật (Print qua vài lần Capture) TRƯỚC khi tin §5.7/5.8 đúng
[ ] PIE REGRESSION đầy đủ: UNDO-REG-01..05 (Move/Group/Combo/Select/Reset) → PASS TOÀN BỘ
```
CHECKPOINT PARITY: **stack thuần-snapshot chạy y hệt v1.18.** REG fail bất kỳ → DỪNG, báo cuhoang,
KHÔNG sang U2.4 (đây là lằn ranh an toàn — chưa migrate gì thì phải parity 100%).

### U2.4 — Session Begin/Cancel + reader wiring (PIE)
```
[ ] BP_UndoManager: session vars + BeginInteractiveEdit + CancelInteractiveEdit + ApplyParamCommand
[ ] WBP_FurnitureInventory: bind OnEditBegin→Handle_*Begin; +Cancel seam (OnMeshSelected/Close/đổi slot)
[ ] PIE: kéo slider (chưa commit) → Print Before đã đọc đúng (SESS-01); đổi selection giữa drag →
    giá trị ROLLBACK về Before (SESS-05), history count KHÔNG tăng
```
CHECKPOINT: Begin đọc Before đúng, Cancel rollback đúng. → U2.5

### U2.5 — Commit + dispatch command (PIE — CÂU HỎI NHỊ PHÂN)
```
[ ] CommitInteractiveEdit (§5.4); sửa Handle_*Commit → gọi Commit thay CaptureSnapshot
[ ] Seam #6 (§5.10): bind OnHistoryChanged → Handle_HistoryChanged → RefreshParamPanel (review #1)
[ ] PIE chuỗi (ghi lại count actor + value):
    - kéo Roughness 0.3→0.61 → thả → history +1 entry, EntryKind=ParamCommand (SESS-03)
    - Undo → Roughness về 0.3, ĐẾM ACTOR = trước (KHÔNG respawn, HIST-01), slot-highlight + Inspector CÒN,
      **SLIDER trong panel cũng hiện lại đúng 0.3** (KHÔNG chỉ mesh — xác nhận seam #6 chạy, review #1)
    - Redo → 0.61 lại, actor count vẫn nguyên, slider hiện đúng 0.61
    - kéo tới lui rồi thả về đúng giá trị cũ → Before==After → history KHÔNG tăng (SESS-04)
    - kéo Roughness → Move (snapshot) → Undo Move (respawn OK) → Undo param (targeted, resolve ID) → 0.3 đúng
    - đang preview kéo → bấm Ctrl+Z → preview hủy trước, rồi undo entry cũ (SESS-07)
```
CHECKPOINT: **câu hỏi nhị phân U2 = XANH.** Nếu param-undo còn respawn / mất context → DỪNG (đây là
lý do tồn tại của U2), KHÔNG sang U2.6.

### U2.6 — History-UI readiness (PIE nhẹ)
```
[ ] GetHistoryCount/CurrentIndex/Labels/Kinds + OnHistoryChanged + JumpToHistoryIndex (§6)
[ ] PIE: làm 4-5 thao tác trộn (param + move) → GetHistoryLabels đúng thứ tự + Length khớp (HISTUI-01)
    → JumpToHistoryIndex(1) cho scene y hệt Undo tuần tự tới 1 (HISTUI-02)
    → OnHistoryChanged đếm đúng số lần (HISTUI-03)
```
CHECKPOINT: scaffolding History-window sống. → U2.7

### U2.7 — Doc as-built (§10) + §11 comprehension check → mới ĐÓNG U2

---

## 9. CÁI **KHÔNG** LÀM TRONG U2

| Không làm | Vì sao |
|---|---|
| Viết lại snapshot thành `{Before,After}` + `CurrentSceneState` (trụ E) | Hướng A — rủi ro 3 bug core. Hoãn sang SUBTRACT sau U3 (§1) |
| Gỡ full snapshot khỏi command entry (RAM win) | Cần trụ E trước. Sau, khi có regression khóa |
| Migrate Reset×3 / Move / Group / Combo sang command | Material Param là REFERENCE. Action thứ 2 làm SAU khi U3 xanh (plan §10) |
| Multi-target (`Changes.Num()>1`) | U2 luôn 1 param. Representation để T5 dùng, KHÔNG implement (plan §7.1) |
| Nối Resolver vào Inspector giữ slot-context | Đó là U3 (ChangeSet). U2 chỉ đảm bảo undo command targeted |
| `Map<SessionID>` nhiều session | 1 session đồng thời (plan §2.2) |
| Dựng widget History | U2 chỉ mở API (§6). Widget là task riêng sau |
| Texture param command | Đ12 chưa hỗ trợ load texture → refuse, cấm commit |
| `FInstancedStruct` spike | 1 command type → struct tường minh đủ. Không cần (plan §10) |

---

## 10. AS-BUILT — GHI VÀO ĐÂU KHI XONG

| File | Ghi gì |
|---|---|
| `Data/MaterialSlotService_Reference.md` | +`GetSlotScalarParam`/`GetSlotVectorParam`; class mới `UParamCommandLibrary` + `FMaterialParamCommand` |
| `BP_UndoManager.md` | S_SceneSnapshot V5 (+EntryKind/ParamCmd); session vars; **BuildSceneSnapshotBase + AppendEntry** (tách từ CaptureSnapshot); Begin/Update/Commit/Cancel; ApplyParamCommand; Undo/Redo dispatch; History accessors + OnHistoryChanged + JumpToHistoryIndex; version bump |
| `WBP_FurnitureInventory.md` | bind OnEditBegin; 4 handler Preview/Commit sửa; Cancel seam; **seam #6 (bind OnHistoryChanged → RefreshParamPanel)**; version bump |
| `Data/Data_Structures.md` | S_SceneSnapshot V5 fields; FMaterialParamCommand |
| `Rules/AI_Implementation_Rules.md` | kết quả `[VERIFY]` §12; API mới vào mục "đã xác nhận"; **QĐ6 DEVIATION** (Resolver caller ở U2, không U3) |
| `Rules/Testing.md` | dòng lịch sử U2 (Spec `U2_Command` + protocol) |
| `Architecture_Map.md` | cạnh mới: INV→UndoManager (session), UndoManager→SceneManager (ResolveByPersistentId — caller ĐẦU TIÊN của Resolver), UndoManager→MSS (SetSlot*Param qua ApplyParamCommand) |
| `00_Core/01_Session_State.md` | Current/Next: U2 ĐÓNG → U3 |
| `00_Core/DEVIATIONS.md` | QĐ6 (Resolver caller sớm), hướng B (hoãn trụ E), Đ12 texture refuse |
| `Bugs/Open_Bugs.md` | `Bug-ParamUndo-SlotContextLost` GIỮ OPEN (đóng ở U3); `S7G7T4b` XOÁ (absorbed) |

---

## 11. KIỂM TRA HIỂU BÀI (cuhoang trả lời TRƯỚC khi tick U2)

1. Tại sao hướng B (command entry VẪN kèm full snapshot) không phá parity của undo cũ, trong khi
   hướng A (viết lại snapshot) thì phải chứng minh lại từ đầu?
2. Khi Undo một param command, vì sao BẮT BUỘC `ResolveByPersistentId` để tìm actor, mà KHÔNG cầm
   con trỏ `TargetFurnitureActor` sẵn có? (gợi ý: chuyện gì xảy ra nếu giữa lúc đó có 1 thao tác
   snapshot respawn?)
3. Vì sao `BeginInteractiveEdit` đọc Before từ MID (core) mà KHÔNG lấy giá trị đang hiện trên row
   widget — dù row rõ ràng "biết" giá trị đó?
4. Preview kéo 100 khấc/giây nhưng history chỉ +1 entry lúc thả. Cơ chế nào đảm bảo điều đó, và vì
   sao Cancel (đổi selection giữa drag) lại KHÔNG để lại entry nào?

---

## 12. DANH SÁCH `[VERIFY]` — Sonnet xác nhận trong editor, KHÔNG đoán

| Mã | Cần kiểm | Ảnh hưởng |
|---|---|---|
| W1 | BP struct (`S_SceneSnapshot`) chứa được C++ USTRUCT `FMaterialParamCommand` field? (tiền lệ FMaterialSlotRecord nói CÓ) | Nếu KHÔNG → làm `FMaterialParamCommand` thành BP UserDefinedStruct |
| W2 | `GetScalarParameterValue`/`GetVectorParameterValue` chỉ trên MID (không MI) — reader C++ phải Cast MID trước, false→fallback | Đọc Before đúng |
| W3 | `OnEditBegin` của 2 row bắn đúng lúc `OnMouseCaptureBegin`/`OnInteractionBegin` + hex/spinbox commit (doc nói có, chưa bind bao giờ) | Begin trigger |
| W4 | `bIsRestoring` accessible từ chỗ guard BeginInteractiveEdit (cùng UndoManager) | Chặn session giữa restore |
| W5 | `ResolveByPersistentId` (U1) trả actor MỚI sau respawn đúng — đã PASS U1.4, tái xác nhận trong chuỗi U2.5 | Undo command targeted |
| W6 | Sau `SetSlot*Param` LIVE ở Preview, `GetSlot*Param` ở Commit đọc lại đúng giá trị vừa áp (round-trip MID) | After đúng |
| W7 | `CurrentIndex` default/semantics thật: LUÔN trỏ entry hợp lệ = "trạng thái hiện tại" (tương đương bắt đầu từ -1, KHÔNG phải "next free slot") — trace tay qua vài lần Capture, Print xác nhận, KHÔNG đoán | Critical cho §5.7/5.8 dispatch mới (đọc `SnapshotHistory[CurrentIndex]` TRƯỚC khi giảm) — sai → lệch 1 index, undo/redo command trật entry |

---

## 13. LƯU Ý HANDOFF

- Task card này **self-contained** cho Sonnet: có Q10 block + Q9 S-Scan + Q8 mỗi flow → Sonnet đủ điều
  kiện execute, không phải hỏi ngược.
- Sonnet gặp trạng thái Selection ngoài S0-S9, hoặc producer/consumer ngoài Q10 block → **DỪNG, báo
  cuhoang** (KP1), không tự suy diễn.
- Thứ tự bất khả xâm phạm: **U2.3 PARITY GATE phải xanh trước khi rewire handler (U2.4+).** Chưa
  migrate gì mà đã hồi quy = lỗi nền, phải sửa trước.
- U2.5 là câu hỏi nhị phân. Không xanh → DỪNG, KHÔNG nối U2.6/U3.
