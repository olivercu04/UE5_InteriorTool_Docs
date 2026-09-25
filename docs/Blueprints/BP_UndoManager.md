# BP_UndoManager
**HỢP NHẤT TỪ 6 file:** v1.2 (16/05) → v1.4 (04/06) → v1.5 (07/06) → **v1.6 base** (10/06) + v1.7_patch (12/06) + v1.8_patch (15/06)
**Phiên bản:** 1.22 | **Cập nhật:** 24/09/2026 16:40 (U2.6 History-UI — PASS) — `Broadcast OnHistoryChanged` phủ đủ: +cuối `AppendEntry` (→ Capture + Commit), +cuối nhánh Snapshot của Undo/Redo (sửa lại D-10). +mục §History-UI accessors: `JumpToHistoryIndex` **✓K2 export 24/09** (44 node, không lỗi); 4 accessor Get build từ U2.3. PIE HISTUI-01/02/03 PASS, panel không nháy khi thả slider.

**Phiên bản:** 1.21 | **Cập nhật:** 24/09/2026 16:10 (U2.4 + U2.5 — ĐÓNG, PASS) — Interactive Edit Session: +enum `E_ParamSessionPhase` (None|Previewing) · +3 session var `Sess_Active`/`Sess_Cmd`/`Sess_Phase` + var tạm `CommitEdit_Label` · `ApplyParamCommand` (thân đã có từ U2.3, D-4 K2-reviewed — U2.4 rà lại theo cùng spec; lần đầu CHẠY THẬT) · +`CommitInteractiveEdit`/`BeginInteractiveEdit`/`CancelInteractiveEdit` (Custom Event) · `UndoLastAction`/`RedoLastAction` +`CancelInteractiveEdit()` node đầu (SESS-07) +`Broadcast OnHistoryChanged` cuối nhánh Command · Event End Play +`SET Sess_Active=False`. **Câu hỏi nhị phân U2 = XANH:** undo param → đảo đúng giá trị, KHÔNG respawn, slot/Inspector/gizmo còn nguyên; redo áp lại đúng. **Mức bằng chứng:** build theo node flow Sonnet dẫn + cuhoang xác nhận compile xanh + PIE (log Print) — **CHƯA soi K2 export** phiên này. Deviations D-5..D-12 (`DEVIATIONS.md`). Task card §5.2–5.8, §8 U2.4/U2.5.

**Phiên bản:** 1.20 | **Cập nhật:** 24/09/2026 (U2.3 PARITY GATE — PASS) — tách `CaptureSnapshot` thành `BuildSceneSnapshotBase(ActionName)→S_SceneSnapshot` + `AppendEntry(Entry)`; `CaptureSnapshot` còn 2 node gọi 2 helper (chữ ký không đổi, 10 caller cũ nguyên). `UndoLastAction`/`RedoLastAction` +nhánh dispatch `EntryKind==ParamCommand` (nhánh command CHƯA chạy — chưa có caller sinh command entry, đúng thiết kế). Sửa doc gap: D-2 (Step 3 THẬT 2 tầng cast), D-3 (`RestoreSnapshot` +input `PreviousActor`). Redo ghi as-built GET-sau-SET. **W7 PASS** (`CurrentIndex=Len−1`, luôn trỏ entry hiện tại) + **REG-01..05 PASS toàn bộ** (parity thuần-snapshot y hệt v1.19). Deviations: `DEVIATIONS.md` D-1..D-4. Task card §5.1b/5.1c/5.7/5.8, §8 U2.3.

**Phiên bản:** 1.19 | **Cập nhật:** 22/09/2026 (U2.2, Undo Architecture) — `S_SceneSnapshot` +field `EntryKind:E_HistoryEntryKind` (default Snapshot) +field `ParamCmd:FMaterialParamCommand` (default rỗng); `Version` 4→5. Struct-only, KHÔNG đụng logic node (BuildSceneSnapshotBase/AppendEntry tách riêng ở U2.3). Compile sạch, smoke PIE (Move→Undo) PASS, không hồi quy. Xem `Sprints/Sprint7/21-09-2026_U2_HistoryMutationBoundary_TaskCard.md` §5.1b/§8 U2.2.

**Phiên bản:** 1.18 | **Cập nhật:** 21/09/2026 (U1.3, PersistentIdentity) — `S_FurniturePlacement` +field `PersistentID:String`; `CaptureSnapshot` Step 3 +capture; `RestoreSnapshot` Step 4 +inject có guard (`Placement.PersistentID != ""`, merge — không dead-end). PIE PASS ID-02 (ID sống qua Move+Undo). Regression Undo/Redo material PASS, không hồi quy. Xem `Sprints/Sprint7/21-09-2026_U1_PersistentIdentity_TaskCard.md`

**Phiên bản:** 1.17 | **Cập nhật:** 08/09/2026 | `RestoreSnapshot` Step 4 gỡ dòng `Call RestoreMyMaterialSlots` thừa (đóng nợ từ 07/09) — chỉ còn SET MaterialSlots, restore tự chạy qua `LoadMeshAsync.Completed`. Test regression Undo/Redo material PASS. `Bug-LoadMeshAsync-RestoreRace` đóng hoàn toàn

**Phiên bản:** 1.16 | **Cập nhật:** 07/09/2026 | Merge nợ từ G2/Việc 2B (03/09): `S_FurniturePlacement` +field `MaterialSlots : Array<FMaterialSlotRecord>` (đã code+test PASS từ 03/09, canonical doc chưa từng ghi). `RestoreSnapshot` Step 4 dòng `Call RestoreMyMaterialSlots` thừa VẪN CÒN TREO, chưa sửa trong phiên này

**Phiên bản:** 1.15 | **Cập nhật:** 04/08/2026 11:05 | Fix Bug-RowNameLostOnUndo: `S_FurniturePlacement` +field `RowName : Name` (✓K2 03/08), `CaptureSnapshot` Step 3 GET RowName (✓K2), `RestoreSnapshot` Step 4 SET NewActor.RowName (✓K2) — struct thiếu field này kể từ khi migrate RowName-based (Sprint D.T6, 17/06) mà chưa cập nhật theo

> **v1.12 (C9.c, 30/07/2026):** Custom Event mới `RestoreCurrentSnapshot()` (khôi phục snapshot hiện hành, không dịch con trỏ history) cho rollback của `ReplaceCombo` — Actor riêng, quản lý toàn bộ Undo/Redo

> **v1.8 (Sprint 4 Bug Fix A12):** `EditModeStack` vào snapshot (Version 4 = `EditModeStackSnapshot`). Thêm `TempEditModeStack` var. Fix: Undo restore đúng edit mode state.
> **v1.7 (Sprint 4 T8):** Thêm `ValidateEditMode()` — cắt `EditModeStack` từ group đã xoá sau Undo. Chèn vào RestoreSnapshot sau SyncGroupsToContainer.
> **v1.6 (Sprint 3):** Snapshot Version 3 + `Groups` array + `GroupID` per actor. `TempGroups` fix impure-timing. RestoreSnapshot: restore Groups + re-fire selection.
> **v1.5 (Sprint 2):** Fix stale `TempSelectedIndices` — CLEAR đầu hàm CaptureSnapshot.
> **v1.4 (Sprint 1 T12):** Multi-Snapshot: `SelectedMeshIndices` (array) + Version 2. Nested ForEach With Break.

---

## Variables

```
SnapshotHistory     : Array of S_SceneSnapshot
CurrentIndex        : Integer
MaxSteps            : Integer (50)
SelectedMeshIndex   : Integer                    ← single cũ (Version 1), giữ tương thích
TempMeshes          : Array of S_FurniturePlacement
SpawnedActors       : Array of StaticMeshActor   ← hard ref, clear ở EndPlay
FoundActor          : StaticMeshActor             ← hard ref, clear ở EndPlay
TargetUniqueID      : String
RestoredBPActor     : BP_FurnitureActor           ← hard ref, clear ở EndPlay (v1.3)

← v1.4 (T12 Multi-Snapshot):
TempSelectedIndices : Array of Integer            ← build lúc capture (index các đồ đang chọn)
RestoredActors      : Array of BP_FurnitureActor  ← build lúc restore, truyền vào SelectActors; hard ref, clear ở EndPlay

← v1.6 (Sprint 3 Group):
TempGroups          : Array of S_GroupData        ← đệm cho CaptureSnapshot (fix impure-timing). KHÔNG SaveGame

← v1.8 (A12 fix):
TempEditModeStack   : Array of String             ← đệm giống TempGroups, tránh impure-timing. KHÔNG SaveGame

← v1.10 (G1.T2):
RestoreInputMgr     : BP_FurnitureInputManager    ← cache 1 lần trước ForEach trong RestoreSnapshot Step 4, tránh Get All Actors Of Class lặp trong loop. Hard ref — ⚠️ KHÔNG thấy clear ở Event End Play (xem mục dưới), khác quy ước các hard ref khác trong file này — chưa xác nhận có phải thiếu sót hay không, ngoài phạm vi K3.

← v1.21 (U2.4, Interactive Edit Session — task card §5.1):
Sess_Active         : Boolean (default False)          ← có session chỉnh param đang mở không
Sess_Cmd            : FMaterialParamCommand (C++)      ← danh tính (EntityID/SlotName/SlotHintIndex/ParamName/Type) + Before điền lúc Begin, After điền lúc Commit
Sess_Phase          : E_ParamSessionPhase (default None) ← enum BP MỚI: None | Previewing
CommitEdit_Label    : String                           ← biến tạm CHỈ CommitInteractiveEdit dùng: gộp label từ 2 nhánh Scalar/Color về 1 pin
                                                          (Custom Event không có Local Var — L9; 1 pin input chỉ nhận 1 dây)
                                                          Không phải hard ref → không cần clear ở End Play.
```

---

## S_SceneSnapshot struct — v1.19: +EntryKind/ParamCmd (Version 5)

```
ActionName              : String
Meshes                  : Array of S_FurniturePlacement
SelectedMeshIndex       : Integer              ← Version 1 (single), giữ tương thích
ActiveMode              : E_ActiveMode
SelectedMeshIndices     : Array of Integer     ← v1.4 (Version 2 — nhiều đồ)
Version                 : Integer              ← v1.19: 5 = +EntryKind/ParamCmd; 4 = groups+editmode; 3 = group; 2 = multi; 0/1 = single cũ
Groups                  : Array of S_GroupData ← v1.6 (Version 3)
EditModeStackSnapshot   : Array of String      ← v1.8 (Version 4): stack GroupID tại thời điểm snapshot. Default = [] cho V<4.
EntryKind               : E_HistoryEntryKind   ← v1.19 (Version 5): Snapshot | ParamCommand. Default Snapshot — entry cũ (V<5) đọc ra mặc định Snapshot, đúng ý nghĩa cũ.
ParamCmd                : FMaterialParamCommand ← v1.19 (Version 5): C++ USTRUCT (BlueprintType, `ParamCommandTypes.h`, U2.1). Default rỗng (default-construct). Chỉ có nội dung khi EntryKind==ParamCommand (từ U2.3 trở đi — U2.2 struct-only, chưa có caller nào set field này).
```

**Version history:**
- V1: single select (legacy)
- V2: multi-select (Sprint 1 T12)
- V3: Groups (Sprint 3)
- V4: Groups + EditModeStackSnapshot (Sprint 4 Bug Fix A12, 15/06/2026)
- **V5: +EntryKind (E_HistoryEntryKind) + ParamCmd (FMaterialParamCommand) — Undo Architecture U2.2, 22/09/2026. Additive (QĐ2, task card U2 §3) — mọi caller CŨ của `CaptureSnapshot` không đổi (field mới để default, "wrap trong suốt").**

**S_FurniturePlacement** (v1.6 thêm `GroupID`; v1.14 thêm `RowName`; v1.16 thêm `MaterialSlots`; v1.18 thêm `PersistentID`):
`UniqueID(String), MeshPath, DAPath, Location, Rotation, Scale, ActorTag, MaterialPaths(Array<String>), GroupID(String), RowName(Name), MaterialSlots(Array<FMaterialSlotRecord>), PersistentID(String)`.
`PersistentID` (v1.18, 21/09/2026, U1.3) — mang GUID-string qua respawn Undo/Redo. Default "" (snapshot cũ
trước U1 không có field này, tương thích ngược — `RestoreSnapshot` guard `!= ""` trước khi inject).
✓K2 03/08/2026 — export Make/Break struct thật xác nhận field `RowName` kiểu **Name** (khớp
`BP_FurnitureActor.RowName : Name`, xem `Blueprints/BP_FurnitureActor.md`).

⚠️ **Nợ merge từ G2/Việc 2B (03/09/2026), đóng 07/09/2026:** field `MaterialSlots` đã code+test
PASS từ 03/09 (song hành `MaterialPaths` cũ, xem `Sprints/Sprint7/S7G2_Reroute_ExecutionPlan_27aug2026.md`
mục 2B.0/2B.2/2B.3) nhưng canonical doc đứng ở v1.15 chưa từng ghi field này — merge lần đầu ở
đây. `CaptureSnapshot` Step 3 GET `(Actor).MaterialSlots` → SET vào field này; `RestoreSnapshot`
Step 4 `SET NewActor.MaterialSlots = placement.MaterialSlots` (đã có sẵn từ 2B, node flow đầy đủ
xem mục `RestoreSnapshot` bên dưới). ✅ **FIXED (08/09/2026).** `RestoreSnapshot` Step 4 gỡ dòng `Call NewActor.RestoreMyMaterialSlots`
thừa — chỉ còn `SET NewActor.MaterialSlots = placement.MaterialSlots`, restore tự chạy qua
`LoadMeshAsync.Completed` bên trong actor (cùng pattern đã áp cho Combo, xem `BP_FurnitureActor.md`
v2.2). Test regression Undo/Redo material PASS, không hồi quy.

**S_GroupData**: `GroupID(String), GroupName(String), ParentGroupID(String), bIsLocked(Boolean)`.

---

## Event Dispatcher

```
OnRestoreCompleted(RestoredSelectedActor : BP_FurnitureActor)
  ← Broadcast cuối RestoreSnapshot, sau khi spawn actors xong
  ← WBP_FurnitureInventory bind để update TargetFurnitureActor
  ← Multi-restore: truyền PrimarySelectedActor (đồ primary trong nhóm)

OnHistoryChanged()                                   ← v1.21 (U2.5, seam #6) — 0 input
  ← Broadcast (v1.22): cuối AppendEntry (Capture + Commit), cuối CẢ 2 nhánh Undo/Redo, cuối JumpToHistoryIndex
  ← WBP_FurnitureInventory bind ở Event Construct → Handle_HistoryChanged → RefreshParamPanel
```

---

## ⭐ BUG STALE TempSelectedIndices (fix v1.5 — Sprint 2)

**Triệu chứng:** Select mesh1 → Deselect → Select mesh2 → Deselect → Undo → ra Sel2 (đúng) → Undo lần nữa → **nhảy thẳng về Sel1, bỏ qua trạng thái Deselect ở giữa.**

**Root cause:** Với thao tác **Deselect**, execution trong CaptureSnapshot đi qua **NHÁNH KHÁC** (bypass đoạn build TempSelectedIndices ở Step 4). `TempSelectedIndices` còn GIÁ TRỊ CŨ (stale) từ lần Select trước → snapshot "Deselect1" lưu nhầm là mesh1-đang-chọn.

**Debug lesson:** Print trong ForEach Step 3 in 1 lần/mesh → ngỡ "double capture" (thực ra gọi 1 lần). → **Print debug đặt MAIN execution line, KHÔNG trong loop body.**

**Fix (v1.5):** `CLEAR TempSelectedIndices` ngay đầu hàm CaptureSnapshot (Step 0), trước mọi Branch. CLEAR cũ ở Step 4 GIỮ LẠI làm backup.

---

## ⭐ BUG IMPURE-TIMING — Undo không restore Groups (fix v1.6 — Sprint 3)

**Triệu chứng:** Undo về bước CreateGroup → info bar không hiện group; log `Restore: Groups.Length = 0`. Diagnostic `SNAPSHOT chua: 0` → snapshot CreateGroup lưu Groups rỗng.

**Root cause:** `GetGroupsForSnapshot` là **impure function (có exec pin)**. Nối thẳng output vào `Make S_SceneSnapshot` → nếu exec của function chạy SAU node Make → Make đọc giá trị default (rỗng).

**Fix (v1.6):** Dùng biến đệm `TempGroups`. Đầu CaptureSnapshot: `Call GetGroupsForSnapshot → SET TempGroups`. Make node đọc `GET TempGroups`.

**Lesson:** Impure function feeding data pin → output chỉ valid sau exec của nó. An toàn nhất: gọi sớm → SET temp var → node đọc temp var.

---

## ⭐ BUG A12 — Undo không tắt Edit Mode bar (fix v1.8 — Sprint 4)

**Triệu chứng:** Đang trong edit mode group có sẵn → Ctrl+Z → Edit mode bar vẫn hiện.

**Root cause:** `EditModeStack` là runtime state (`KHÔNG SaveGame`), không nằm trong `S_SceneSnapshot`. Khi Undo restore snapshot: ValidateEditMode kiểm tra stack — group vẫn tồn tại → stack hợp lệ → broadcast `OnEditModeChanged(True)` → bar giữ nguyên.

**Fix (v1.8):** Đưa `EditModeStack` vào snapshot (`EditModeStackSnapshot`). Restore stack trước `ValidateEditMode` → ValidateEditMode validate trên stack đã khôi phục đúng.

---

## GetGroupsForSnapshot() → Array\<S_GroupData\> (v1.6)

```
Get All Actors Of Class(BP_FurnitureInputManager) → Length → Branch > 0:
  True → Get(0) → IsValid → True → GET Groups → Return Groups
  (else) → Return (rỗng)
```

---

## BuildSceneSnapshotBase(ActionName) → S_SceneSnapshot — Function MỚI (U2.3, 24/09/2026)

> **U2.3:** tách toàn bộ phần "quét scene → dựng nội dung 1 entry" khỏi `CaptureSnapshot`.
> `CaptureSnapshot` VÀ `CommitInteractiveEdit` (U2.5, chưa build) đều gọi hàm này — 1 nguồn build
> entry, không chép tay ForEach-actor 2 lần. KHÔNG đụng phần "quản lý stack" (xem `AppendEntry`).
> **Chữ ký:** Input `ActionName : String` · Return `SceneSnapshot : S_SceneSnapshot` · Local var
> `FurnitureInputManagerLocalVar : BP_FurnitureInputManager`.

```
0.  Array_Clear(TempSelectedIndices)                          ← v1.5: chống stale
0b. Call GetGroupsForSnapshot → SET TempGroups                ← v1.6: chống impure-timing
    Get All Actors Of Class(BP_FurnitureInputManager) → Get(0)
      → SET FurnitureInputManagerLocalVar                     ← D-1 (U2.3): cache InputManager 1 LẦN,
                                                                 thay Get-All-Actors-Of-Class→Get(0) lặp của
                                                                 bản gốc; dùng lại ×3 chỗ (0b / 4 / 6)
    GET FurnitureInputManagerLocalVar.EditModeStack → SET TempEditModeStack   ← v1.8

2.  Array_Clear(TempMeshes)

3.  Get All Actors With Tag("FurnitureSpawned") → ForEach:
    LoopBody:
      Cast To StaticMeshActor(Array Element)                  ← D-2 (U2.3): Step 3 THẬT có 2 TẦNG cast
        → Cast To BP_FurnitureActor(AsStaticMeshActor)           (canonical cũ ghi 1 tầng — doc sai từ trước, sửa theo thật)
      Make S_FurniturePlacement:
        UniqueID     = Get Display Name(Array Element)
        MeshPath, DAPath, Location, Rotation, Scale, ActorTag ← từ Cast BP_FurnitureActor
        MaterialPaths = GET BP_FurnitureActor.MaterialOverrides
        MaterialSlots = GET BP_FurnitureActor.MaterialSlots   ← v1.17
        GroupID       = GET BP_FurnitureActor.GroupID         ← v1.6
        RowName       = GET BP_FurnitureActor.RowName         ← v1.14
        PersistentID  = GET BP_FurnitureActor.PersistentID    ← v1.18
      Array_ADD to TempMeshes
    CastFailed: để trống — ForEach tự chạy element kế (as-built gốc)
    Completed → Step 4

4.  Array_Clear(TempSelectedIndices)                          ← v1.5: backup (GIỮ 2 chỗ CLEAR)
    GET FurnitureInputManagerLocalVar.SelectedActors → ForEach (OUTER, SelectedActor):
      ForEach Loop WITH BREAK [TempMeshes] (Index, Mesh):     ← INNER (có Break)
        Branch Mesh.UniqueID == Get Display Name(SelectedActor):
          True → ADD Index → TempSelectedIndices → BREAK (inner)
      outer Completed → Step 6

    ⚠️ INNER PHẢI "ForEach Loop WITH BREAK". Mọi nhánh False đều đi tiếp Step 6 — không dead-end.

6.  GET FurnitureInputManagerLocalVar.ActiveMode
    Make S_SceneSnapshot(
      ActionName            = input pin hàm (KHÔNG phải biến),
      Meshes                = GET TempMeshes,
      SelectedMeshIndex     = -1,
      SelectedMeshIndices   = GET TempSelectedIndices,        ← v1.4
      ActiveMode,
      Version               = 5,                              ← v1.19 (U2.2)
      Groups                = GET TempGroups,                 ← v1.6
      EditModeStackSnapshot = GET TempEditModeStack,          ← v1.8
      EntryKind, ParamCmd   = KHÔNG wire (default: Snapshot / rỗng — QĐ2 "wrap trong suốt")
    )
    → Return(SceneSnapshot)
```
> **Mức bằng chứng (U2.3):** K2 export soi ~40% đầu (đến Step 3) + cuhoang xác nhận 3 gạch (Make pins ·
> 2 wire đổi đích · CastFailed Step 3 để trống) + local var dùng ×3 chỗ (0b / 4 / 6). Nửa sau (Step 4
> nested loop + Step 6 Make) chưa soi export riêng — REG-01..05 PASS bao phủ hành vi.

---

## AppendEntry(Entry : S_SceneSnapshot) — Function MỚI (U2.3, 24/09/2026)

> **U2.3:** gộp phần "quản lý stack" cũ: resize redo-stack (Step 1 cũ) + trim MaxSteps (Step 5 cũ) + ADD +
> tăng `CurrentIndex`. Độc lập biến với `BuildSceneSnapshotBase` (không đụng Temp*). Thứ tự **build trước,
> trim/add sau** — NGƯỢC bản cũ (trim trước). Đây chính là lý do U2.3 PARITY GATE bắt buộc chạy đủ REG-01..05.

```
Entry ▶→ Branch[CurrentIndex < Array_Length(SnapshotHistory) − 1]
           True  → Array_Resize(SnapshotHistory, CurrentIndex + 1)   ← xóa redo stack
           False → (bỏ qua)
       [cả 2 merge] ▶→ Branch[Array_Length(SnapshotHistory) ≥ MaxSteps]
           True  → Array_RemoveIndex(SnapshotHistory, 0) → SET CurrentIndex = CurrentIndex − 1
           False → (bỏ qua)
       [cả 2 merge] ▶→ Array_ADD(SnapshotHistory, Entry)
       ▶→ SET CurrentIndex = CurrentIndex + 1
       ▶→ Broadcast OnHistoryChanged                                 ← v1.22 (U2.6) — node CUỐI; phủ CaptureSnapshot + CommitInteractiveEdit
```
> v1.20 chưa broadcast (hoãn U2.6). v1.22 thêm — hệ quả: `RefreshParamPanel` chạy cả sau mỗi Capture/Commit (thừa nhưng
> vô hại; H5 xác nhận panel không nháy khi thả slider).

---

## CaptureSnapshot(ActionName) — v1.20: VIẾT LẠI còn 2 node (U2.3)

```
Custom Event CaptureSnapshot(ActionName) ▶→
  BuildSceneSnapshotBase(ActionName) ●SceneSnapshot→ AppendEntry(Entry = ●)
```
> Chữ ký KHÔNG đổi → 10 caller cũ không đụng. EntryKind mặc định Snapshot ở mọi entry → parity 100% với
> v1.19 (đã chứng qua REG-01..05, xem changelog v1.20).

---

## E_ParamSessionPhase (enum BP MỚI, v1.21 — U2.4)
`None` | `Previewing`. Tách riêng khỏi `E_HistoryEntryKind` (loại entry ≠ trạng thái session).
> Gotcha lúc tạo: thêm var `Sess_Phase` (kiểu enum này) ngay sau `Sess_Cmd` (struct C++) → compile báo
> `Can't parse default value '(EntityID=...)' ... Property: Sess_Phase` (chuỗi default là của STRUCT, không phải enum
> — cache default lệch 1 property). Fix: xóa `Sess_Phase` → tạo lại → xanh. Lỗi editor tạm, KHÔNG phải sai thiết kế.

---

## ApplyParamCommand(Cmd, bUseBefore) → ok — Function (thân build U2.3 — D-4; lần đầu chạy thật ở U2.5)
> Đảo/áp 1 command. Là đường ngược của command (undo = `bUseBefore=True`, redo = `False`) và là đường rollback của
> `CancelInteractiveEdit`. Thân build sớm ở U2.3 (D-4, K2 export đối chiếu §5.6 — đúng). ⚠ Phiên 24/09 Sonnet KHÔNG đọc D-4
> trước, tưởng là stub và giao "Việc 2 — build thân" — cuhoang báo "xong"; flow dưới = spec §5.6, trùng bản U2.3. Nếu
> lần đó có dựng lại thì phải khớp flow này; nghi ngờ → soi K2.
> **Inputs:** `Cmd : FMaterialParamCommand` · `bUseBefore : Boolean` · **Output:** `ok : Boolean` · Local var: không.
```
Entry ▶→ Get All Actors Of Class(BP_FurnitureSceneManager) → Get(0)      ← KHÔNG Cast (pin tự type theo class)
         → Call .ResolveByPersistentId(Cmd.EntityID) → (Actor, bFound)    ← caller THẬT đầu tiên của Resolver U1 (QĐ6)
     ▶→ Branch(bFound)
          False → Return(ok = False)
          True  ▶→ GET Actor.FurnitureMesh → Mesh
                 ▶→ Branch(Cmd.Type == Scalar)      [Equal Enum]
                      True  ▶→ Select Float(bUseBefore ? Cmd.BeforeScalar : Cmd.AfterScalar) → V
                             ▶→ SetSlotScalarParam(Mesh, Actor.MaterialSlots [ref], Cmd.SlotName,
                                                     Cmd.SlotHintIndex, Cmd.ParamName, V) ●→ ok
                             ▶→ Return(ok)
                      False ▶→ Select LinearColor(bUseBefore ? Cmd.BeforeColor : Cmd.AfterColor) → VC
                             ▶→ SetSlotVectorParam(Mesh, Actor.MaterialSlots [ref], ...VC) ●→ ok
                             ▶→ Return(ok)
```
`Q8:` Function | IsValid qua bFound | 2 nhánh có Return riêng | không latent | 6A: chính nó là đường ngược.

---

## CommitInteractiveEdit() — Custom Event (v1.21, U2.4 build / U2.5 nối UI) — **[✓K2 export 24/09/2026, sau khi dọn Print]**
> Chốt session: đọc After, so Before, tạo ĐÚNG 1 entry `ParamCommand` (hoặc không tạo nếu no-op).
> **Gap task card §5.4 (D-7):** card không nói lấy Mesh từ đâu → tự Resolve lại bằng `Sess_Cmd.EntityID` y hệt Begin
> (Custom Event trên UndoManager không có `TargetFurnitureActor` của widget — đúng QĐ3 "đọc từ core").
```
Custom Event CommitInteractiveEdit() ▶→
  Branch( Sess_Active AND (Sess_Phase == Previewing) )
     False → Return                                                  ← SESS-06
     True  ▶→ Get All Actors Of Class(BP_FurnitureSceneManager) → Get(0) → .ResolveByPersistentId(Sess_Cmd.EntityID) → (Actor,bFound)
           ▶→ Branch(bFound)
                False ▶→ SET Sess_Active=False ▶→ SET Sess_Phase=None   ← actor mất giữa session → hủy an toàn, không entry
                True  ▶→ GET Actor.FurnitureMesh → Mesh
                       ▶→ Branch(Sess_Cmd.Type == Scalar)
                            True  ▶→ GetSlotScalarParam(Mesh, Sess_Cmd.SlotName, Sess_Cmd.SlotHintIndex, Sess_Cmd.ParamName) ●→ OutValue
                                   ▶→ GET Sess_Cmd → Set members in MaterialParamCommand(AfterScalar = OutValue) → SET Sess_Cmd
                                   ▶→ SET CommitEdit_Label = "Chỉnh " + Conv_NameToString(Sess_Cmd.ParamName)
                            False ▶→ GetSlotVectorParam(...) ●→ OutValue
                                   ▶→ GET Sess_Cmd → Set members in(AfterColor = OutValue) → SET Sess_Cmd
                                   ▶→ SET CommitEdit_Label = "Đổi màu " + Conv_NameToString(Sess_Cmd.ParamName)
                       [2 nhánh merge exec] ▶→ Branch( Is No Op Command(Sess_Cmd) )   ← Pure C++ (UParamCommandLibrary)
                            True  ▶→ [Print tạm "COMMIT NOOP"] ▶→ SET Sess_Active=False ▶→ SET Sess_Phase=None      ← SESS-04
                            False ▶→ BuildSceneSnapshotBase(CommitEdit_Label) ●SceneSnapshot→
                                     Set members in S_SceneSnapshot(EntryKind = ParamCommand, ParamCmd = GET Sess_Cmd) ●→
                                     AppendEntry(Entry = ●)                   ← dùng CHUNG helper với CaptureSnapshot (hybrid B: kèm full snapshot)
                                     ▶→ [Print tạm "COMMIT CMD"] ▶→ SET Sess_Active=False ▶→ SET Sess_Phase=None
```
`Q8:` Custom Event → class var OK | IsValid qua bFound | mọi nhánh có đích | không latent | 6A: đường ngược = `ApplyParamCommand`.
> **As-built K2 (24/09) — khớp flow trên, 3 chi tiết thật:**
> 1. **KHÔNG có node `SET Sess_Cmd`.** Pin `Struct Ref` của `Set members in` là THAM CHIẾU → `GET Sess_Cmd ●→ Set members in
>    (AfterScalar/AfterColor)` sửa THẲNG biến class. Flow trên ghi "→ SET Sess_Cmd" là thừa — thực tế không cần.
> 2. **`Entry` đi 2 dây từ cùng pin output `BuildSceneSnapshotBase.Entry`:** 1 dây vào `Set members in S_SceneSnapshot.Struct Ref`
>    (EntryKind=ParamCommand, ParamCmd=GET Sess_Cmd), 1 dây (qua reroute) vào `AppendEntry.Entry`. Output `Struct Out` của node
>    Set members KHÔNG nối. Chạy đúng vì Struct Ref sửa tại chỗ biến tạm chứa output của hàm, `AppendEntry` đọc lại chính biến
>    đó — PIE chứng (UNDO CMD chạy = EntryKind đã đổi; giá trị undo đúng = ParamCmd đã gắn). Ổn nhưng khó thấy khi đọc graph;
>    sửa lại cho rõ (nối `Struct Out → AppendEntry`) là tùy chọn, KHÔNG bắt buộc.
> 3. `Sess_Cmd` được `Break` 1 lần đầu hàm (EntityID/SlotName/SlotHintIndex/ParamName/Type) dùng cho Resolve, 2 reader, 2 label.
>    Print tạm đã dọn (U2.7). Không lỗi compile, không pin mồ côi.

---

## BeginInteractiveEdit(EntityID, SlotName, HintIndex, ParamName, Type) — Custom Event (v1.21, U2.4) — **[✓K2 export 24/09/2026, sau khi dọn Print]**
> Mở session, đọc Before TỪ CORE (MID/MI qua C++), không lấy từ widget. Inputs: `EntityID:String · SlotName:String ·
> HintIndex:Integer · ParamName:Name · Type:EParamCmdType`.
```
Entry ▶→ Branch(bIsRestoring)
       True  → Return                                              ← X1: cấm mở session giữa restore
       False ▶→ Branch(Sess_Active)
                    True  ▶→ CommitInteractiveEdit()                ← settle session cũ (QĐ5 — 1 session đồng thời)
                    False → (đi thẳng)
               [merge] ▶→ Get All Actors Of Class(BP_FurnitureSceneManager) → Get(0) → .ResolveByPersistentId(EntityID) → (Actor,bFound)
             ▶→ Branch(bFound)
                    False → Return
                    True  ▶→ GET Actor.FurnitureMesh → Mesh
                           ▶→ GET Sess_Cmd → Set members in MaterialParamCommand(EntityID, SlotName, SlotHintIndex=HintIndex,
                                  ParamName, Type) → SET Sess_Cmd                         ← 5 field "danh tính" 1 lần trước branch
                           ▶→ Branch(Type == Scalar)
                                True  ▶→ GetSlotScalarParam(Mesh, SlotName, HintIndex, ParamName) ●→ OutValue
                                       ▶→ GET Sess_Cmd → Set members in(BeforeScalar = OutValue) → SET Sess_Cmd
                                False ▶→ GetSlotVectorParam(...) ●→ OutValue
                                       ▶→ GET Sess_Cmd → Set members in(BeforeColor = OutValue) → SET Sess_Cmd
                           [merge] ▶→ SET Sess_Phase = Previewing ▶→ SET Sess_Active = True
                                   ▶→ [Print tạm "BEGIN | ParamName | S= | C= | Hist="]
```
`Q8:` Custom Event → class var OK | IsValid qua bFound | mọi Branch có đích | không latent | 6A: `CancelInteractiveEdit`.
> **As-built K2 (24/09) — khớp flow trên.** Chi tiết thật: (1) `bIsRestoring` True và `bFound` False đều là exec-out bỏ trống
> = kết thúc event (không có node Return riêng — hợp lệ ở Custom Event, không có logic nào phía sau bị bỏ). (2) Sau khi ghi 5
> field danh tính, flow dùng `SET Sess_Cmd.Output_Get → Break MaterialParamCommand` để lấy SlotName/SlotHintIndex/ParamName/Type
> cho 2 reader + Branch Type (thay vì dùng thẳng input event — cùng giá trị). (3) Ở đây CÓ node `SET Sess_Cmd` sau mỗi `Set
> members in` (nối `Struct Out → SET`) — khác `CommitInteractiveEdit` (không SET, dựa Struct Ref tham chiếu). Cả 2 cách đều đúng.
> Print tạm đã dọn. Không lỗi compile, không pin mồ côi.
> Phụ thuộc: gọi `CommitInteractiveEdit` → phải build Commit TRƯỚC Begin (task card xếp Commit ở U2.5 — lệch thứ tự
> build, D-5). Before đúng cho slot CHƯA chỉnh nhờ reader C++ đọc MI gốc (fix U2.5, `MaterialSlotService_Reference.md`).

---

## CancelInteractiveEdit() — Custom Event (v1.21, U2.4) — 6A của session
```
Entry ▶→ Branch(Sess_Active)
       False → Return
       True  ▶→ ApplyParamCommand(Cmd = Sess_Cmd, bUseBefore = True)   ← rollback preview về Before
              ▶→ [Print tạm "CANCEL | ok | Hist"]
              ▶→ SET Sess_Active = False ▶→ SET Sess_Phase = None      ← KHÔNG AppendEntry (SESS-05)
```
`Q8:` Custom Event | guard Sess_Active | 2 nhánh có đích | không latent | 6A: chính nó.
> Caller: `UndoLastAction`/`RedoLastAction` (node đầu) + 4 seam ở `WBP_FurnitureInventory` (OnMeshSelected nhánh Material,
> CloseMaterialInspector, NotifyViewportSlotClick, OnSlotSwatchClicked).
> **Chống ghi mồ côi (U6b PASS):** Cancel qua bàn phím lúc đang giữ slider → Undo → `OnHistoryChanged` → `RefreshParamPanel`
> xóa row đang giữ → mọi thao tác chuột sau đó rơi vào widget đã hủy → không ghi gì. Bảo vệ này DỰA VÀO rebuild panel —
> nếu sau này có đường Cancel KHÔNG rebuild panel (vd phím tắt đổi tab) → phải thêm guard `Sess_Active` vào 4 handler (D-11).

> **Print tạm** (BEGIN/COMMIT/CANCEL/UNDO/REDO + probe `Action=/Idx/Len` từ U2.3) — ĐÃ DỌN ở U2.7 (24/09), smoke PASS. Các dòng `[Print tạm …]` trong flow trên là lịch sử, node không còn.

---

## History-UI accessors (task card §6) — build U2.3, PIE U2.6 PASS

> 4 hàm Get (build U2.3, review K2 lúc đó — chưa từng vào canonical; ghi theo spec §6):
> `GetHistoryCount() → Length(SnapshotHistory)` · `GetCurrentIndex() → CurrentIndex` ·
> `GetHistoryLabels() → ForEach → ADD .ActionName` · `GetHistoryKinds() → ForEach → ADD .EntryKind`.

### JumpToHistoryIndex(Target : Int) — Function **[✓K2 export 24/09/2026]**
Local: `TargetLocalVar : Int` · `JumpGuard : Int`
```
Entry ▶→ SET TargetLocalVar = Target                           ← thừa (bị ghi đè dưới), vô hại — không sửa (KP3)
      ▶→ Branch(bIsRestoring)
           True  → Return
           False ▶→ SET TargetLocalVar = Clamp(Target, 0, Length(SnapshotHistory) − 1)
                  ▶→ SET JumpGuard = 0
                  ▶→ WhileLoop( CurrentIndex > TargetLocalVar AND JumpGuard < Length(SnapshotHistory) )
                        LoopBody  ▶→ UndoLastAction() ▶→ SET JumpGuard = JumpGuard + 1
                        Completed ▶→ WhileLoop( CurrentIndex < TargetLocalVar AND JumpGuard < Length(SnapshotHistory) )
                                        LoopBody  ▶→ RedoLastAction() ▶→ SET JumpGuard = JumpGuard + 1
                                        Completed ▶→ Broadcast OnHistoryChanged      ← hết hàm (return ngầm)
```
- 2 vòng dùng chung `JumpGuard` (depth guard chống kẹt) — mỗi lần nhảy chỉ 1 vòng thật sự chạy.
- `CurrentIndex` là GET đọc lại mỗi vòng (L14) → vòng tự dừng đúng.
- Undo/Redo tự broadcast (v1.22) → nhảy N bước = N+1 broadcast. Card chấp nhận (tối ưu = nice-to-have).
- **Test gọi Jump không cần code:** console PIE/Standalone `ke * JumpToHistoryIndex <K>`.
- **PIE U2.6:** HISTUI-01 (labels đúng thứ tự, `kinds`=`n`), HISTUI-02 (`Jump 2` = undo tay về 2; `Jump 99` clamp về cuối),
  HISTUI-03 (mọi Capture/Commit/Undo/Redo/Jump đều bắn) — PASS.

---

## UndoLastAction (Ctrl+Z) — v1.20: +dispatch EntryKind (U2.3)

```
Custom Event UndoLastAction ▶→
  CancelInteractiveEdit()                     ← v1.21 (U2.4, SESS-07): hủy preview đang dở TRƯỚC — tự guard Sess_Active bên trong,
                                                 KHÔNG bọc thêm Branch(Sess_Active) như task card §5.7 vẽ (D-9)
  ▶→ Branch CurrentIndex <= 0 → True: STOP
  False ▶→ GET SnapshotHistory[CurrentIndex]   (GET CurrentIndex — pull TRƯỚC SET) → Break S_SceneSnapshot
         ▶→ Branch(EntryKind == ParamCommand)   (Equal Enum, B = ParamCommand)
              True  ▶→ ApplyParamCommand(Cmd = Break.ParamCmd, bUseBefore = True)   ← TARGETED, KHÔNG respawn (HIST-01)
                     ▶→ SET CurrentIndex = CurrentIndex − 1
                     ▶→ Broadcast OnHistoryChanged            ← v1.21 (U2.5, seam #6) — node cuối
              False ▶→ SET CurrentIndex = CurrentIndex − 1
                     ▶→ Get All Actors Of Class(InputManager) → Get(0) → GET SelectedFurnitureActor
                     ▶→ RestoreSnapshot(
                          IndexHistory  = GET CurrentIndex     (pull SAU SET → giá trị MỚI đã giảm),
                          PreviousActor = GET SelectedFurnitureActor
                        )                                      ← Y HỆT v1.18 (HIST-02, parity)
                     ▶→ Broadcast OnHistoryChanged            ← v1.22 (U2.6)
```
> ⚠️ **HAI node GET CurrentIndex riêng biệt** — 1 pull TRƯỚC SET (chọn entry đang undo, cho dispatch
> EntryKind), 1 pull SAU SET (index mới, cho RestoreSnapshot). ĐỪNG gộp thành 1 GET.
> **v1.21:** guard session = `CancelInteractiveEdit()` node đầu. **v1.22:** Broadcast ở CẢ 2 nhánh. (v1.21 bỏ nhánh Snapshot
> vì tưởng `RestoreSnapshot` trả về trước khi xong — sai: nó chạy tuần tự tới Step 7 `OnRestoreCompleted` rồi mới trả; chỉ
> phần load mesh/param bên trong actor là async. Broadcast sau nó = refresh thừa 1 lần, vô hại. D-10 cập nhật.)
> **PASS U2.5:** U2 (HIST-01: UNDO CMD, không respawn, slider/swatch/Inspector/gizmo còn), U5 interleave (UNDO SNAP rồi
> UNDO CMD resolve đúng actor MỚI qua PersistentID), U6/U6b (SESS-07: CANCEL in trước UNDO).
> ⚠️ **Lỗi phiên U2.3 đã fix:** bản dựng đầu đọc entry SAU khi giảm CurrentIndex → trượt 1 entry (undo
> `S_move` lại đảo `C1`, vd stack `S_init/C1/S_move`). Phát hiện qua review K2 export. As-built ĐÍCH là
> bản trên (đọc entry Ở cursor TRƯỚC khi giảm).

---

## RedoLastAction (Ctrl+Shift+Z) — v1.20: +dispatch EntryKind (U2.3)

```
Custom Event RedoLastAction ▶→
  CancelInteractiveEdit()                     ← v1.21 (U2.4): như Undo
  ▶→ Branch CurrentIndex >= Array_Length(SnapshotHistory) − 1 → True: STOP
  False ▶→ SET CurrentIndex = CurrentIndex + 1
         ▶→ GET SnapshotHistory[CurrentIndex]   (GET CurrentIndex — pull SAU SET → index MỚI) → Break S_SceneSnapshot
         ▶→ Branch(EntryKind == ParamCommand)
              True  ▶→ ApplyParamCommand(Cmd = Break.ParamCmd, bUseBefore = False)   ← apply After, KHÔNG chạm RestoreSnapshot
                     ▶→ Broadcast OnHistoryChanged            ← v1.21 (U2.5, seam #6)
              False ▶→ RestoreSnapshot(
                          IndexHistory  = GET CurrentIndex,
                          PreviousActor = GET InputManager.SelectedFurnitureActor
                        )                                      ← Y HỆT v1.18
                     ▶→ Broadcast OnHistoryChanged            ← v1.22 (U2.6)
```
> **As-built (U2.3):** Redo dùng **GET CurrentIndex (pure, pull SAU SET)** thay "output pin của SET" mà doc
> cũ khuyến cáo. Trong chuỗi exec tuyến tính (SET đã chạy TRƯỚC khi pin được pull) → 2 cách cho CÙNG giá
> trị. Test PASS → ghi as-built này vào canonical thay vì bắt đổi (xem Key Learnings, mục Redo đã cập nhật).

---

## ValidateEditMode() — v1.7: MỚI

Gọi từ RestoreSnapshot sau khi restore Groups xong. Kiểm tra EditModeStack còn hợp lệ không — cắt bỏ từ group không còn tồn tại.

```
Entry ▶→ CLEAR LocalValid                              ← local Array of String
       ▶→ Get All Actors Of Class(BP_FurnitureInputManager) → GET[0] → Cast → InputRef
       ▶→ Branch(IsValid(InputRef)):
            False ▶→ Return
            True  ▶→ GET InputRef.EditModeStack
                   ▶→ For Each Loop with Break (gid):
                        LoopBody ▶→ Call InputRef.FindGroupData(gid) → (_, bFound)   ← ĐÍNH CHÍNH
                                    02/08/2026: hàm chỉ có 2 output (S_GroupData, bFound), KHÔNG
                                    có Index — xem MERGE_LOG Q3, `BP_FurnitureInputManager.md`
                                 ▶→ Branch(bFound):
                                      True  ▶→ ADD gid → LocalValid   ← group còn tồn tại
                                      False ▶→ BREAK                   ← group mất → cắt từ đây (con cũng vô nghĩa)
                        Completed ▶→
                   ▶→ SET InputRef.EditModeStack = LocalValid
                   ▶→ Branch(InputRef.EditModeStack.Length == 0):
                        True  ▶→ Call InputRef.RemoveEditModeVisual
                               ▶→ Broadcast InputRef.OnEditModeChanged(bActive=False, GroupID="")
                        False ▶→ Call InputRef.ApplyEditModeVisual
                               ▶→ Call InputRef.GetCurrentEditScope → Scope
                               ▶→ Broadcast InputRef.OnEditModeChanged(bActive=True, GroupID=Scope)
```

> **For Each Loop with Break** — BREAK khi gặp group không tồn tại: group cha mất → các group con trong stack cũng vô nghĩa → cắt hết từ đó.
> Cả 2 nhánh Branch cuối đều Broadcast OnEditModeChanged → WBP_MeshControls tự cập nhật breadcrumb/ẩn bar.

---

## RestoreSnapshot(IndexHistory, PreviousActor) — v1.10: hợp nhất spawn path qua SpawnFurnitureCopy

> **D-3 (U2.3, 24/09/2026) — sửa gap chữ ký:** hàm THẬT có input thứ 2 `PreviousActor : BP_FurnitureActor`
> (canonical trước chỉ ghi `RestoreSnapshot(IndexHistory)` — thiếu). `Undo`/`Redo` nhánh Snapshot truyền
> `PreviousActor = GET InputManager.SelectedFurnitureActor` (xem §UndoLastAction / §RedoLastAction). Điểm
> tiêu thụ chính xác trong THÂN hàm chưa soi K2 export riêng — chỉ bổ sung chữ ký, thân giữ nguyên (§13:
> không có ground truth thì báo, không sửa). ⚠️ `Data/Data_Structures.md` mục "BP_UndoManager Functions"
> vẫn ghi `RestoreSnapshot(IndexHistory : Integer)` (1 param) — mâu thuẫn cùng gốc, chưa sửa (ngoài phạm vi
> delta U2.3, để cuhoang quyết).

⚠️ **Đính chính 21/07/2026 (K3):** đoạn Step 4 dưới đây trước ghi "v1.8: VIẾT LẠI" nhưng thực ra
là bản CŨ (spawn inline `Spawn BP_FurnitureActor → Load Asset Blocking → Set Static Mesh...`) —
mâu thuẫn với changelog v1.10 (16/06) đã ghi đúng là gọi qua `SpawnFurnitureCopy`. Đối chiếu
export K2Node thật (21/07/2026) xác nhận **changelog v1.10 đúng, đoạn body cũ chưa từng được
xóa** — sửa lại cho khớp thực tế bên dưới.

```
1. ← v1.4: DeselectAll (thay DeselectMesh):
   Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → Call DeselectAll
   ← KHÔNG gọi CaptureSnapshot ở đây (infinite loop)

2. Destroy All Actors tag "FurnitureSpawned"

3. CLEAR SpawnedActors
   ← v1.10 (G1.T2): cache RestoreInputMgr (class var) = Get All Actors Of Class
     (BP_FurnitureInputManager) → Get(0) → Cast, 1 LẦN TRƯỚC ForEach — tránh Get All Actors Of
     Class lặp lại trong loop.

4. ForEach Snapshot.Meshes (Placement):
   SpawnFurnitureCopy(
     self = RestoreInputMgr,
     MeshPath = Placement.MeshPath, DAPath = Placement.DAPath,
     SpawnLocation = Placement.Location, SpawnRotation = Placement.Rotation,
     SpawnScale = Placement.Scale, MaterialOverrides = Placement.MaterialPaths,
     bAutoSelect = False,     ← v1.10 (G1.T2) — bug phát hiện lúc test: từng wire nhầm True,
                                 khiến mọi lần restore chọn hết tất cả item trong scene
     bAddToRecent = False     ← v1.11 (K3, 21/07/2026) — Undo không nên nhồi Recent
   ) ●→ NewActor              (output đã type BP_FurnitureActor sẵn — KHÔNG Cast thừa so plan gốc)
   SET NewActor.RowName = Placement.RowName    ← v1.14 (03/08/2026) ✓K2 — RowName KHÔNG nằm
                                                  trong param SpawnFurnitureCopy, phải SET riêng
                                                  sau khi actor đã spawn, TRƯỚC SET GroupID
   SET NewActor.GroupID = Placement.GroupID    ← v1.6 (restore quan hệ group)
   Branch(Placement.PersistentID != "")        ← v1.18 (21/09/2026, U1.3) — guard tương thích ngược
     True  ▶→ SET NewActor.PersistentID = Placement.PersistentID
     False → [merge, KHÔNG dead-end — snapshot cũ trước U1 không có field này, NewActor giữ ID
               tươi mà SpawnFurnitureCopy vừa Ensure-sinh cho nó (không rác/leak — String value,
               không phải Object Reference, ghi đè bình thường)]
   [merge] → ADD NewActor to SpawnedActors
   ← SpawnFurnitureCopy tự lo toàn bộ: Spawn Actor, Load Mesh/Material Async, ADD tag
     "FurnitureSpawned", áp MaterialOverrides — KHÔNG còn code inline riêng (Spawn Actor From
     Class / Load Asset Blocking / Set Static Mesh / ForEach MaterialPaths thủ công đã XÓA, xem
     `BP_FurnitureInputManager.md` cho thân SpawnFurnitureCopy).

5. ← v1.4: Branch Snapshot.Version >= 2:

   ══ True (MULTI restore) ══
     CLEAR RestoredActors
     ForEach Snapshot.SelectedMeshIndices (idx):
       Branch IsValid(SpawnedActors[idx]):
         True → Cast To BP_FurnitureActor(SpawnedActors[idx]) → ADD to RestoredActors
     ForEach Completed →
       Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → Call SelectActors(RestoredActors)
       ← SelectActors tự lo outline (255/254) + gizmo (single/pivot) + Broadcast OnSelectionChanged
       SET RestoredBPActor = (RestoredActors LAST, hoặc Get(0)) ← cho OnRestoreCompleted

   ══ False (Version 1 fallback — SINGLE, snapshot cũ) ══
     Branch Snapshot.SelectedMeshIndex >= 0:
       True:
         FoundActor = SpawnedActors[SelectedMeshIndex]
         Cast → SET SelectedFurnitureActor + SET RestoredBPActor
         DeactivateGizmo → Set Custom Depth True + Stencil 255
         Branch ActiveMode != Select → ActivateGizmo(FoundActor, ...)
       False:
         Set Custom Depth False → SET SelectedFurnitureActor = None → DeactivateGizmo
         SET RestoredBPActor = None

5b. ← v1.6: Branch Snapshot.Version >= 3 (restore Groups):
     Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → IsValid:
       True → CLEAR InputManager.Groups
              ForEach Snapshot.Groups → ADD to InputManager.Groups
              Call SyncGroupsToContainer
                ↓
              ← v1.8: SET InputManager.EditModeStack = Snapshot.EditModeStackSnapshot
                       (Refs có sẵn: InputManager knot chain + pin EditModeStackSnapshot trên Break node)
                ↓
              ← v1.7: Call ValidateEditMode()
     (Version < 3 → bỏ qua)

6.  RefreshButtonState(Snapshot.ActiveMode)

6b. ← v1.6: RE-FIRE selection để info bar + listener cập nhật SAU khi Groups đã restore:
    Get All Actors Of Class(InputManager) → Get(0) → IsValid:
      True → Branch (InputManager.SelectedActors.Length > 0):
               True  → Call SelectActors(InputManager.SelectedActors)   ← re-fire OnSelectionChanged (info bar group)
               False → Call DeselectAll → DeactivateGizmo(GizmoController)
    ⚠️ CẢ 2 nhánh merge về Step 7 (Broadcast) — không dead-end

7. Broadcast OnRestoreCompleted(GET RestoredBPActor)   ← single point, no branch
   ⚠️ Dùng RestoredBPActor (từ Cast output đúng snapshot), KHÔNG dùng SpawnedActors[class var SelectedMeshIndex]
```

**⚠️ Tương thích ngược:**
- V0/V1: đi nhánh False (single fallback) → restore đúng 1 đồ
- V2: multi-select, không có Groups → Step 5b bỏ qua → EditModeStack = [] → bar ẩn (safe)
- V3: có Groups, không có EditModeStackSnapshot (default []) → SET EditModeStack = [] → bar ẩn (safe)
- **V4:** đầy đủ restore

**⚠️ Bug đã trả giá (v1.6):**
- Undo về deselect không tắt outline/gizmo: Step 6b nhánh rỗng phải gọi DeselectAll + DeactivateGizmo.
- Restore Groups phải SAU restore GroupID per actor (Step 4) để ExpandSelectionWithGroups thấy đúng quan hệ.

---

## RestoreCurrentSnapshot() — Custom Event (MỚI, C9.c, 30/07/2026)

Khôi phục snapshot HIỆN HÀNH (theo `CurrentIndex`) — dùng cho rollback của
`BP_ComboManager.ReplaceCombo` khi `SpawnComboByID` fail. KHÔNG dời con trỏ history (khác
`Undo`/`Redo` vốn dịch `CurrentIndex` TRƯỚC khi gọi — V3 ghi ở `24-07-2026_C9_Execution_Plan.md`
§0).

```
Custom Event RestoreCurrentSnapshot()
▶→ Is Valid Index(SnapshotHistory, CurrentIndex) ●→ Branch
     True  ▶→ RestoreSnapshot(IndexHistory = CurrentIndex)
     False ▶→ dead-end (không có gì để khôi phục)
```

Guard `Is Valid Index` bắt buộc: `CurrentIndex` sai (history rỗng, hoặc bị trừ quá tay ở nhánh
`Length >= MaxSteps` trong `CaptureSnapshot`) → truy cập mảng ngoài phạm vi. Tách hàm 1 node
thay vì mở public `CurrentIndex` ra ngoài: ngữ nghĩa rõ ("khôi phục trạng thái hiện tại, KHÔNG
dịch con trỏ") — khác `Undo`/`Redo`. Dùng lại được cho mọi rollback sau này (không chỉ Replace
Combo).

---

## Event End Play — VRAM Leak Prevention — v1.8: CẬP NHẬT

```
Event End Play →
  [Clear] SpawnedActors          ← drop array hard refs
  SET FoundActor = None
  [Clear] TempMeshes
  SET RestoredBPActor = None     ← v1.3
  [Clear] RestoredActors         ← v1.4: drop array hard refs
  [Clear] TempGroups             ← v1.6
  [Clear] TempEditModeStack      ← v1.8
  SET Sess_Active = False        ← v1.21 (U2.4): không để session "mồ côi" sang lượt PIE sau
```

---

## Test kết quả A12 (v1.8)

| Case | Scenario | Kết quả |
|---|---|---|
| Case 1 (flat) | Tạo G1 → Enter edit → Undo xóa G1 → bar ẩn | ✅ PASS |
| Case 2 (nested, group có sẵn) | Edit G3>G1 → Ctrl+Z từng bước → breadcrumb cập nhật đúng từng bước | ✅ PASS |

---

## Key Learnings

- **DeselectAll (v1.4) thay DeselectMesh** trong RestoreSnapshot → dọn sạch multi-select trước khi spawn lại.
- **Version field** cho tương thích tiến/lùi: V0/V1 → single; V2 → multi; V3 → groups; V4 → groups+editmode.
- **Nested ForEach With Break** trong CaptureSnapshot: outer = SelectedActors, inner = TempMeshes; match UniqueID → ADD index → BREAK inner.
- **SelectActors trong multi-restore** nhận RestoredActors (mảng build element-by-element → độc lập, không alias) → tự lo outline + gizmo.
- **KHÔNG gọi CaptureSnapshot trong DeselectMesh/DeselectAll** → infinite loop.
- **RedoLastAction — GET CurrentIndex pull SAU SET (U2.3):** as-built dùng GET (pure) pull sau khi SET
  CurrentIndex đã chạy, KHÔNG dùng output pin của SET. Trong exec tuyến tính (SET chạy trước khi pin được
  pull) → cùng giá trị, test PASS. [Trước v1.20 doc khuyến cáo "PHẢI dùng output pin" — nay ghi as-built
  thật.] L4 chỉ áp khi pure node bị pull TRƯỚC khi SET kịp chạy (race ngoài thứ tự exec) — không phải case này.
- **OnRestoreCompleted dùng RestoredBPActor** (Cast output đúng snapshot), không SpawnedActors[class var].
- **CaptureSnapshot("Initial")** gọi cuối Level Blueprint BeginPlay.
- **Load Asset Blocking trong RestoreSnapshot** — technical debt, refactor Async ở Phase B.
- **⭐ CLEAR biến class persistent ở ĐẦU hàm (v1.5):** `TempSelectedIndices` là class var → stale nếu execution bypass đoạn build. CLEAR Step 0 là cách phòng thủ chắc nhất.
- **⭐ Print debug đặt MAIN line, không trong loop (v1.5):** print trong ForEach in 1 lần/mesh → ngỡ double capture.
- **⭐ Impure function feeding data pin (v1.6):** output chỉ valid sau exec của nó → gọi sớm → SET temp var (TempGroups / TempEditModeStack) → node đọc temp var.
- **⭐ Re-fire selection SAU khi restore Groups (v1.6):** restore Groups (Step 5b) → ValidateEditMode (v1.7) → re-fire selection (6b). Nhánh rỗng → DeselectAll + DeactivateGizmo.
- **⭐ Diagnostic print phân biệt capture vs restore (v1.6):** `SNAPSHOT chua: N` để chốt bug ở capture hay restore.
- **⭐ EditModeStack phải nằm trong snapshot (v1.8):** runtime state không persist qua Undo → ValidateEditMode validate trên stack cũ → bar không tắt. Fix: đưa vào snapshot, restore trước ValidateEditMode.
- **⭐ ValidateEditMode với For Each With Break (v1.7):** BREAK khi gặp group không tồn tại — group cha mất → con trong stack cũng vô nghĩa. Không cần tiếp tục duyệt.

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|-----------|------|----------|
| 1.0 | 21/04/2026 | Tài liệu đầu tiên |
| 1.1 | 09/05/2026 | Event End Play cleanup (Fix 5.1 VRAM leak) |
| 1.2 | 16/05/2026 — 14:08 ICT | v1.1 Material: MaterialPaths capture/restore, OnRestoreCompleted dispatcher |
| 1.3 | 20/05/2026 | Fix broadcast bug: RestoredBPActor var → single broadcast point |
| 1.4 | 04/06/2026 — 15:30 ICT | **Multi-Snapshot (T12):** S_SceneSnapshot +Version +SelectedMeshIndices; CaptureSnapshot build TempSelectedIndices (nested ForEach With Break); RestoreSnapshot DeselectAll + branch Version (multi via SelectActors / single fallback); +RestoredActors var + End Play clear |
| 1.5 | 07/06/2026 — 22:40 ICT | **Fix stale TempSelectedIndices:** CLEAR Step 0 đầu hàm CaptureSnapshot. Bug Undo nhảy cóc khi xen kẽ Select/Deselect. |
| 1.6 | 10/06/2026 — 20:34 ICT | **Sprint 3 Group:** S_SceneSnapshot +Groups (V3); S_FurniturePlacement +GroupID; +TempGroups var. CaptureSnapshot: Step 0b SET TempGroups, capture GroupID. RestoreSnapshot: restore GroupID (Step 4), restore Groups + SyncGroupsToContainer (Step 5b), re-fire selection (6b). +GetGroupsForSnapshot. End Play clear TempGroups. |
| 1.7 | 12/06/2026 — 15:04 ICT | **Sprint 4 T8 — ValidateEditMode:** thêm function ValidateEditMode (For Each With Break duyệt EditModeStack, cắt group không tồn tại, broadcast OnEditModeChanged). Chèn vào RestoreSnapshot sau SyncGroupsToContainer, trước re-fire selection. |
| 1.8 | 15/06/2026 — 20:30 ICT | **A12 fix — EditModeStack vào Undo:** S_SceneSnapshot +EditModeStackSnapshot (V4); +TempEditModeStack var. CaptureSnapshot Step 0b: SET TempEditModeStack; Make thêm EditModeStackSnapshot + Version=4. RestoreSnapshot Step 5b: SET InputManager.EditModeStack trước ValidateEditMode. End Play: CLEAR TempEditModeStack. |
| 1.9 | 16/06/2026 — 14:10 ICT | G1.T1 — Fix B1 (Undo lần 2 không restore group state): +bIsRestoring (Boolean, KHÔNG SaveGame). RestoreSnapshot: SET True đầu hàm, SET False SAU Step 6b (merge) TRƯỚC Broadcast — vị trí bắt buộc SAU re-fire selection để chặn H1 (capture lén qua SelectActors). CaptureSnapshot: guard đầu hàm Branch(bIsRestoring) True→dead-end. Event End Play: SET False (vệ sinh session crash giữa restore). Verify: hist ổn định 16 qua 5 lần restore liên tiếp, scene/info bar đúng tại mọi điểm kể cả ranh giới Ungroup/CreateGroup. |
| 1.10 | 16/06/2026 — 16h11p ICT | G1.T2 — Hợp nhất spawn path: RestoreSnapshot Step 4 không tự spawn inline nữa, gọi SpawnFurnitureCopy(bAutoSelect=False) qua reference cached 1 lần trước ForEach (class var RestoreInputMgr, tránh Get All Actors Of Class lặp trong loop). NewActor output đã type BP_FurnitureActor sẵn — bỏ Cast thừa so với plan gốc. Xóa toàn bộ code spawn inline cũ (Spawn Actor From Class, Load Asset Blocking, Set Static Mesh, ADD tag, restore material loop) — SpawnFurnitureCopy tự lo các bước này. Bug phát hiện trong test: bAutoSelect bị wire nhầm True → mọi lần restore chọn hết tất cả item trong scene → fix lại False. Test 5 case PASS (case crash khi tắt PIE sau Save/Load/Undo — defer Gate 2, nghi GPU/VRAM không liên quan thay đổi này). |
| 1.11 | 21/07/2026 | **K3 (bAddToRecent) DONE.** RestoreSnapshot: pin `bAddToRecent=False` tại node SpawnFurnitureCopy (Step 4) — verify qua Blueprint Export Method (K2Node text) + screenshot thật. Test 4 case PASS (spawn combo, Undo/Redo, spawn furniture từ card, copy/paste — Recent behavior đúng cho từng case). Kèm sửa doc: đoạn body Step 4 trước ghi nhãn "v1.8: VIẾT LẠI" nhưng vẫn mô tả spawn inline cũ (mâu thuẫn với changelog v1.10 đã đúng) — đối chiếu export K2Node thật, viết lại khớp thực tế. Thêm class var `RestoreInputMgr` vào mục Variables (sót từ v1.10). Chi tiết: `DEVIATIONS.md`, `Bugs/Open_Bugs.md` mục K3. |
| 1.12 | 30/07/2026 | **C9.c DONE (delta "C9 Replace: Folder Highlight + Chip Fix & C9.b–C9.f").** Custom Event mới `RestoreCurrentSnapshot()` — guard `Is Valid Index(SnapshotHistory, CurrentIndex)` → `RestoreSnapshot(CurrentIndex)`, KHÔNG dịch con trỏ history (khác Undo/Redo). Dùng cho rollback của `BP_ComboManager.ReplaceCombo` khi spawn combo thay thế fail. Chi tiết: `Blueprints/BP_ComboManager.md` v1.14. |
| 1.13 | 02/08/2026 | **MERGE_LOG Q3 đóng.** `ValidateEditMode`: đính chính `Call InputRef.FindGroupData(gid) → (_, _, bFound)` (3 output, tự mâu thuẫn với chữ ký thật) → `(_, bFound)` (2 output). Bằng chứng: K2Node export `ResolveSelectedComboRoot` 02/08/2026 + `Plans/24-07-2026_C9_Execution_Plan.md` §V8 xác nhận `FindGroupData` chỉ có `(S_GroupData, bFound)`. Không đổi node flow thật — chỉ sửa mô tả cho khớp as-built. Chi tiết: `Blueprints/BP_FurnitureInputManager.md` v2.9, `00_Core/MERGE_LOG.md`. |
| 1.14 | 04/08/2026 | **RowName preservation qua Undo (phát hiện lúc verify case 6, T2 Save As/Save đè).** `S_FurniturePlacement` +field `RowName`. `CaptureSnapshot` Step 3: `RowName = GET BP_FurnitureActor.RowName` nối vào Make struct. `RestoreSnapshot` Step 4: THÊM `SET NewActor.RowName = Placement.RowName` ngay sau `SpawnFurnitureCopy`, TRƯỚC `SET NewActor.GroupID` — `RowName` KHÔNG nằm trong param `SpawnFurnitureCopy`, phải SET riêng. ✓TEST 03/08/2026: Print xác nhận `RowName=CLAMP_table_karkas_005` (không còn `None`) sau chuỗi Replace→Move→Undo→Replace lại. Trước fix này, actor respawn qua Undo mất `RowName` → nghi vấn cùng lỗ hổng có thể lan sang `S_ClipboardEntry` (Copy/Paste/Duplicate) — xem `Bugs/Open_Bugs.md` mục `Bug-RowName-MissingInClipboard` (chưa verify). |
| 1.15 | 04/08/2026 11:05 | **Fix Bug-RowNameLostOnUndo (03/08)** — struct `S_FurniturePlacement` thiếu field `RowName` kể từ khi migrate RowName-based (Sprint D.T6, 17/06) — chỉ `CaptureSnapshot`/`RestoreSnapshot` dùng struct này chưa được cập nhật theo. Nâng dấu 3 chỗ (struct field, Step 3, Step 4) từ "chốt theo lời cuhoang" lên `✓K2 03/08/2026` (export Make/Break struct thật xác nhận). Đính chính type: `RowName` là **Name** (khớp `BP_FurnitureActor.RowName`), không phải `String` như ghi nhầm ở v1.14. |
| 1.16 | 07/09/2026 | **Merge nợ từ S7.G2/Việc 2B (03/09/2026, chưa merge từ trước).** `S_FurniturePlacement` +field `MaterialSlots : Array<FMaterialSlotRecord>` — đã code+test PASS 03/09, canonical doc đứng ở v1.15 chưa từng ghi field này. ⚠️ `RestoreSnapshot` Step 4 dòng `Call NewActor.RestoreMyMaterialSlots` (nghi dính race giống `LoadMeshAsync` đã fix ở `BP_FurnitureActor.md` 07/09) — CHƯA SỬA trong phiên này, vẫn còn treo. Nguồn: `07-09-2026_S7G3_Item1-4_Delta.md` mục B2. |
| 1.17 | 08/09/2026 | **Đóng nợ từ v1.16.** `RestoreSnapshot` Step 4 gỡ dòng `Call NewActor.RestoreMyMaterialSlots` thừa — chỉ còn `SET NewActor.MaterialSlots`, restore tự chạy qua `LoadMeshAsync.Completed` (cùng pattern Combo). Test regression Undo/Redo material PASS. `Bug-LoadMeshAsync-RestoreRace` đóng hoàn toàn (Combo + Undo/Redo). |

| 1.18 | 21/09/2026 | U1.3 (PersistentIdentity) — `S_FurniturePlacement` +field `PersistentID`. `CaptureSnapshot` Step 3 +capture. `RestoreSnapshot` Step 4 +inject (guard != "", merge False — không dead-end). PIE PASS ID-02. Regression material PASS. |
| 1.19 | 22/09/2026 | **U2.2 (Undo Architecture Foundation) — struct-only.** `S_SceneSnapshot` +`EntryKind:E_HistoryEntryKind` (mới, Snapshot|ParamCommand, default Snapshot) +`ParamCmd:FMaterialParamCommand` (C++ USTRUCT từ `ParamCommandTypes.h`, U2.1, default rỗng). Version 4→5. `CaptureSnapshot` Make node: chỉ bump Version=5, KHÔNG wire 2 field mới (để default → wrap trong suốt, 10 caller cũ không đổi). CHƯA đụng logic Undo/Redo dispatch (đó là U2.3). Compile sạch (W1 xác nhận: `FMaterialParamCommand` hiện trong Struct picker bình thường). Smoke PIE: chọn actor → Move → Undo → chạy y hệt trước giờ, không phát hiện lỗi. Task card: `Sprints/Sprint7/21-09-2026_U2_HistoryMutationBoundary_TaskCard.md` §5.1b/§8 U2.2. |
| 1.20 | 24/09/2026 | **U2.3 PARITY GATE — PASS.** Tách `CaptureSnapshot` → `BuildSceneSnapshotBase(ActionName)→S_SceneSnapshot` (quét scene, build 1 entry; Local var `FurnitureInputManagerLocalVar` cache InputManager ×3, D-1; Step 3 THẬT 2 tầng cast StaticMeshActor→BP_FurnitureActor, D-2) + `AppendEntry(Entry)` (resize→trim→ADD→CurrentIndex+1, KHÔNG Broadcast — hoãn U2.6). `CaptureSnapshot` còn 2 node gọi 2 helper (chữ ký giữ nguyên, 10 caller cũ không đụng). `UndoLastAction`/`RedoLastAction` +nhánh `EntryKind==ParamCommand` → `ApplyParamCommand` (Undo bUseBefore=True, Redo=False; KHÔNG respawn) / nhánh Snapshot y hệt v1.18 — nhánh command CHƯA CHẠY vì chưa có caller sinh command entry (đúng thiết kế PARITY). D-3: `RestoreSnapshot` +input `PreviousActor` (gap chữ ký, bổ sung). Redo as-built dùng GET-sau-SET (không output pin) — exec tuyến tính nên cùng giá trị, PASS. Lỗi phiên đã fix: bản Undo đầu đọc entry SAU khi giảm index → trượt 1, sửa (đọc TRƯỚC khi giảm). **Bằng chứng:** W7 6/6 log `Idx=Len−1`; REG-01..05 (Move/Group/Combo/Select/Reset) PASS toàn bộ; trim MaxSteps=6 đúng số học. Deviations `DEVIATIONS.md` D-1..D-4; bài học async-restore `Learning_System.md`. Task card §5.1b/5.1c/5.7/5.8, §8 U2.3. |
| 1.21 | 24/09/2026 16:10 | **U2.4 + U2.5 ĐÓNG — PASS (câu hỏi nhị phân U2 XANH).** +enum `E_ParamSessionPhase`; +var `Sess_Active`/`Sess_Cmd`/`Sess_Phase`/`CommitEdit_Label`; `ApplyParamCommand` (có từ U2.3, lần đầu chạy thật); +`CommitInteractiveEdit`/`BeginInteractiveEdit`/`CancelInteractiveEdit`; Undo/Redo +`CancelInteractiveEdit()` đầu + `Broadcast OnHistoryChanged` cuối nhánh Command; +dispatcher `OnHistoryChanged`; End Play +`SET Sess_Active=False`. Build theo thứ tự phụ thuộc Apply→Commit→Begin→Cancel (D-5). PIE: SESS-01/03/04/05/07, HIST-01, interleave, U6b chống ghi mồ côi, Color W3 PASS. Chưa soi K2 export. Print tạm dọn ở U2.7. D-5..D-12. |
| 1.22 | 24/09/2026 16:40 | **U2.6 PASS.** Broadcast `OnHistoryChanged` +cuối `AppendEntry` +cuối nhánh Snapshot Undo/Redo (D-10 sửa lại). +mục History-UI accessors, `JumpToHistoryIndex` ✓K2. HISTUI-01/02/03 PASS. |
| 1.22 (tiếp) | 24/09/2026 17:40 | **U2.7 — U2 ĐÓNG.** Dọn toàn bộ Print tạm (+ probe W7 U2.3), smoke PASS. ✓K2 `CommitInteractiveEdit` + `BeginInteractiveEdit` (ghi as-built: Struct Ref tham chiếu). §11 PASS 7/7. |
| 1.22 (tiếp 2) | 24/09/2026 19:15 | Sửa phím tắt ở 2 heading: Undo = **Ctrl+Z**, Redo = **Ctrl+Shift+Z** (trước ghi nhầm Alt+Z — nguồn đúng `BP_FoffPlayerController.md` IA_FurnitureUndo/Redo, cuhoang xác nhận). |

---

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Có mặt trong thao tác:** [[L01 · Mở tool và kho đồ|L01]] · [[L03 · Kéo đồ vào phòng|L03]] · [[L04 · Chọn đồ|L04]] · [[L05 · Di chuyển và xoay đồ|L05]] · [[L06 · Nhóm đồ và sửa nhóm|L06]] · [[L07 · Menu chuột phải và phím tắt|L07]] · [[L08 · Thay đồ|L08]] · [[L09 · Đổi vật liệu|L09]] · [[L10 · Chỉnh thông số vật liệu|L10]] · [[L11 · Combo|L11]] · [[L13 · Hoàn tác và làm lại|L13]]

**Thuộc mảng kết nối:** [[Kết nối 3a - Chọn đồ Gizmo Nhóm]] · [[Kết nối 3b - Combo lưu spawn thay combo]] · [[Kết nối 3c - Inventory + Cây thư mục]] · [[Kết nối 3d - Save Undo khởi động]] · [[Kết nối 3e - Vật liệu Material]]

**Gọi / điều khiển →**
- [[BP_FurnitureInputManager]] — chọn lại đồ sau khôi phục + báo tin · SelectActors(), Broadcast OnEditModeChanged
- [[WBP_MeshControls]] — đặt nút mode theo ảnh sau khôi phục · RefreshButtonState(ActiveMode) — lấy tham chiếu từ đâu ?
- [[BP_FurnitureInputManager]] — spawn lại đồ khi Undo, không tự chọn, không nhồi Recent · SpawnFurnitureCopy(bAutoSelect=False, bAddToRecent=False) ✓K2
- [[BP_FurnitureActor]] — đặt lại mã đồ sau spawn lại · SET RowName ✓K2
- [[BP_FurnitureActor]] — giữ nguyên danh tính + nhóm + slot vật liệu · SET PersistentID (guard), GroupID, MaterialSlots
- [[BP_FurnitureInputManager]] — chọn lại / bỏ chọn sau khôi phục · SelectActors() / DeselectAll()
- [[WBP_FurnitureInventory]] — báo tin: khôi phục xong · Broadcast OnRestoreCompleted
- [[BP_FurnitureSceneManager]] — tìm lại đồ theo ID khi undo/chốt param — caller đầu tiên của Resolver · ResolveByPersistentId() ✓K2
- [[MaterialSlotService_Reference]] — đọc giá trị trước/sau + đảo 1 thông số · GetSlot*Param() / SetSlot*Param() (qua ApplyParamCommand) ✓K2
- [[WBP_FurnitureInventory]] — báo lịch sử vừa đổi (undo/redo param) · Broadcast OnHistoryChanged

**← Được gọi bởi**
- [[BP_FurnitureInputManager]] — chụp mốc Select/Deselect · CaptureSnapshot(Select / Deselect) ✓K2
- [[BP_GizmoController]] — chụp trạng thái khi kéo xong · CaptureSnapshot() ✓K2
- [[BP_FurnitureInputManager]] — phím Undo / Redo (bỏ qua khi đang kéo gizmo) · IsGizmoDragging() → UndoLastAction() / RedoLastAction()
- [[BP_FurnitureInputManager]] — chụp mốc các thao tác khác · CaptureSnapshot(BoxSelect / CreateGroup / Ungroup / PasteMulti / DuplicateMulti / Delete / Nudge / SelectSimilar / ResetRotation)
- [[BP_ComboManager]] — giữ tham chiếu + gọi quay lui · UndoManagerRef, RestoreCurrentSnapshot()
- [[BP_ComboManager]] — ghi sổ khi đặt / thay combo · CaptureSnapshot(SpawnCombo / ReplaceCombo)
- [[WBP_FurnitureInventory]] — giữ tham chiếu + nghe khôi phục + chụp trạng thái · UndoManagerRef, Bind OnRestoreCompleted
- [[WBP_FurnitureCard]] — chụp trạng thái khi thay đồ · CaptureSnapshot(Replace)
- [[WBP_DragOverlay_FurnitureCard]] — ghi sổ khi thả đồ · CaptureSnapshot(Spawn)
- [[WBP_FOFF_ToolDemo]] — sinh ra · Spawn
- [[WBP_FOFF_ToolDemo]] — lưu mốc đầu tiên · CaptureSnapshot(Initial)
- [[BP_ComboManager]] — quay lui khi đổi combo lỗi · RestoreCurrentSnapshot()
- [[BP_GizmoController]] — lưu mốc sau khi kéo · CaptureSnapshot(Move/Rotate/Scale) ✓K2
- [[WBP_FurnitureInventory]] — nghe khôi phục xong · Bind OnRestoreCompleted
- [[WBP_FurnitureInventory]] — mở / chốt / hủy phiên chỉnh param (U2.4-2.5) · BeginInteractiveEdit() / CommitInteractiveEdit() / CancelInteractiveEdit()
- [[WBP_FurnitureInventory]] — nghe lịch sử đổi → refresh panel · Bind OnHistoryChanged → RefreshParamPanel()
- [[WBP_DetailPopup]] — lưu mốc khi khoá / reset scale · CaptureSnapshot(Scale)
- [[WBP_FurnitureInventory]] — mở/chốt/hủy phiên chỉnh (chi tiết ở 3d) · Begin/Commit/CancelInteractiveEdit()
- [[BP_FurnitureActor]] — ghi sổ sau khi đổi vật liệu · CaptureSnapshot(ApplyMaterial)

<!-- BRAIN:END -->
