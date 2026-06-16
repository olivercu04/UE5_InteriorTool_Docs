# BP_UndoManager
**HỢP NHẤT TỪ 6 file:** v1.2 (16/05) → v1.4 (04/06) → v1.5 (07/06) → **v1.6 base** (10/06) + v1.7_patch (12/06) + v1.8_patch (15/06)
**Phiên bản:** 1.8 | **Cập nhật:** 15/06/2026 — 20:30 ICT | Actor riêng — quản lý toàn bộ Undo/Redo

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
```

---

## S_SceneSnapshot struct — v1.8: VIẾT LẠI (Version 4)

```
ActionName              : String
Meshes                  : Array of S_FurniturePlacement
SelectedMeshIndex       : Integer              ← Version 1 (single), giữ tương thích
ActiveMode              : E_ActiveMode
SelectedMeshIndices     : Array of Integer     ← v1.4 (Version 2 — nhiều đồ)
Version                 : Integer              ← v1.8: 4 = groups+editmode; 3 = group; 2 = multi; 0/1 = single cũ
Groups                  : Array of S_GroupData ← v1.6 (Version 3)
EditModeStackSnapshot   : Array of String      ← v1.8 (Version 4): stack GroupID tại thời điểm snapshot. Default = [] cho V<4.
```

**Version history:**
- V1: single select (legacy)
- V2: multi-select (Sprint 1 T12)
- V3: Groups (Sprint 3)
- **V4: Groups + EditModeStackSnapshot (Sprint 4 Bug Fix A12, 15/06/2026)**

**S_FurniturePlacement** (v1.6 thêm `GroupID`):
`UniqueID(String), MeshPath, DAPath, Location, Rotation, Scale, ActorTag, MaterialPaths(Array<String>), GroupID(String)`.

**S_GroupData**: `GroupID(String), GroupName(String), ParentGroupID(String), bIsLocked(Boolean)`.

---

## Event Dispatcher

```
OnRestoreCompleted(RestoredSelectedActor : BP_FurnitureActor)
  ← Broadcast cuối RestoreSnapshot, sau khi spawn actors xong
  ← WBP_FurnitureInventory bind để update TargetFurnitureActor
  ← Multi-restore: truyền PrimarySelectedActor (đồ primary trong nhóm)
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

## CaptureSnapshot(ActionName) — v1.8: VIẾT LẠI

```
0.  ← v1.5 FIX: CLEAR TempSelectedIndices       ← NGAY đầu hàm, trước mọi Branch (chống stale)

0b. ← v1.6 FIX: Call GetGroupsForSnapshot → SET TempGroups   ← đệm group (chống impure-timing)
    ← v1.8 FIX: GET InputManager.EditModeStack → SET TempEditModeStack
                 (reuse InputManager ref đang sẵn trong exec chain)

1.  Branch CurrentIndex < Length(History) - 1:
    True → Array Resize(CurrentIndex + 1)   ← xóa redo stack

2.  CLEAR TempMeshes

3.  Get All Actors With Tag("FurnitureSpawned") → ForEach:
    Cast To BP_FurnitureActor (Array Element)
    Build S_FurniturePlacement:
      UniqueID    = Get Display Name(Array Element)
      MeshPath, DAPath ← từ Cast BP_FurnitureActor
      Location, Rotation, Scale, ActorTag
      MaterialPaths = GET BP_FurnitureActor.MaterialOverrides
      GroupID       = GET BP_FurnitureActor.GroupID          ← v1.6
    ADD to TempMeshes

4.  ← v1.4: Build mảng index các đồ ĐANG CHỌN:
    CLEAR TempSelectedIndices                ← v1.5: backup (CLEAR chính ở Step 0)
    Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast:
      Failed → Branch(Length >= MaxSteps)
      Success → GET SelectedActors:
        ForEach SelectedActors (SelectedActor):                    ← OUTER
          ForEach Loop WITH BREAK [TempMeshes] (Index, Mesh):      ← INNER (có Break)
            Branch Mesh.UniqueID == Get Display Name(SelectedActor):
              True → ADD Index → TempSelectedIndices → BREAK (inner)
              False → (continue)
        Completed (outer) → Branch(Length >= MaxSteps)

    ⚠️ INNER ForEach PHẢI dùng "ForEach Loop WITH BREAK" — không break thì duyệt thừa.
    ⚠️ Tất cả nhánh False/Failed đều nối vào Branch(Length >= MaxSteps) — không dead-end.

5.  Branch Length >= MaxSteps → Remove Index 0 → CurrentIndex - 1

6.  GET ActiveMode (từ BP_FurnitureInputManager)
    Make S_SceneSnapshot(
      ActionName,
      Meshes                = TempMeshes,
      SelectedMeshIndex     = -1,                      ← Version 2+ không dùng field này
      SelectedMeshIndices   = TempSelectedIndices,     ← v1.4
      ActiveMode,
      Version               = 4,                       ← v1.8 (bump từ 3)
      Groups                = GET TempGroups,          ← v1.6: đọc TempGroups, KHÔNG nối thẳng GetGroupsForSnapshot
      EditModeStackSnapshot = GET TempEditModeStack    ← v1.8
    )
    → ADD to SnapshotHistory → CurrentIndex + 1
```

---

## UndoLastAction (Alt+Z)

```
Branch CurrentIndex <= 0 → STOP
False: CurrentIndex - 1 → RestoreSnapshot(CurrentIndex)
```

---

## RedoLastAction (Shift+Alt+Z)

```
Branch CurrentIndex >= Length - 1 → STOP
False: SET CurrentIndex = CurrentIndex + 1 → RestoreSnapshot(output pin của SET)
⚠️ PHẢI dùng output pin của SET, không GET riêng
```

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
                        LoopBody ▶→ Call InputRef.FindGroupData(gid) → (_, _, bFound)
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

## RestoreSnapshot(IndexHistory) — v1.8: VIẾT LẠI

```
1. ← v1.4: DeselectAll (thay DeselectMesh):
   Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → Call DeselectAll
   ← KHÔNG gọi CaptureSnapshot ở đây (infinite loop)

2. Destroy All Actors tag "FurnitureSpawned"

3. CLEAR SpawnedActors

4. ForEach Snapshot.Meshes (Placement):
   Spawn BP_FurnitureActor → Load Asset Blocking → Set Static Mesh
   SET MeshPath, SET DAPath
   SET BP_FurnitureActor.GroupID = Placement.GroupID    ← v1.6 (restore quan hệ group)
   GET Tags → ADD "FurnitureSpawned"   ← KHÔNG SET Tags lại
   ADD to SpawnedActors
   ← Restore MaterialPaths:
   ForEach Placement.MaterialPaths (Index, Path):
     Branch Path != "":
       Load Asset Blocking → Cast MaterialInterface → Create DMI(FurnitureMesh, Index) → Set Material
   SET BP_FurnitureActor.MaterialOverrides = Placement.MaterialPaths

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
- **RedoLastAction dùng output pin của SET** CurrentIndex, không GET riêng.
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
