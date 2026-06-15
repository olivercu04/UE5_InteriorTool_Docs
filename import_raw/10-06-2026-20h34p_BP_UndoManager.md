# BP_UndoManager
**Phiên bản:** 1.6 | **Cập nhật:** 10/06/2026 — 20:34 ICT | Actor riêng — quản lý toàn bộ Undo/Redo

> **v1.6 (Sprint 3 Group + fix Undo group):** snapshot lên **Version 3** (thêm GroupID per-placement + Groups array). Thêm var `TempGroups` (đệm capture, fix bug impure-timing). RestoreSnapshot: nhánh Version>=3 restore Groups; đoạn cuối branch theo SelectedActors.Length (rỗng → DeselectAll+DeactivateGizmo). Đọc kèm `Sprint3_Regression_DualDispatcher_Log.md`.

> **v1.5 (Sprint 2 — Fix bug stale TempSelectedIndices):** thêm **CLEAR TempSelectedIndices ngay ĐẦU hàm CaptureSnapshot** (trước Step 1). Fix bug Undo nhảy cóc khi xen kẽ Select/Deselect. Xem mục "⭐ BUG STALE" + Step 0.

> **v1.4 (Sprint 1 T12 — Multi-Snapshot):** snapshot lưu được NHIỀU đồ đang chọn (không chỉ 1). S_SceneSnapshot thêm `Version` + `SelectedMeshIndices` (Array). CaptureSnapshot build mảng index qua nested ForEach. RestoreSnapshot: `DeselectMesh → DeselectAll`, branch theo Version (Version 2 multi-restore qua SelectActors; Version 1 fallback single). Snapshot cũ (Version 1, hoặc field Version = 0/trống) vẫn restore được.

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
TempGroups          : Array of S_GroupData        ← đệm cho CaptureSnapshot (fix bug impure-timing). KHÔNG SaveGame
```

---

## S_SceneSnapshot struct (v1.6)
```
ActionName          : String
Meshes              : Array of S_FurniturePlacement
SelectedMeshIndex   : Integer            ← Version 1 (single), giữ tương thích
ActiveMode          : E_ActiveMode
SelectedMeshIndices : Array of Integer   ← v1.4 (Version 2 - nhiều đồ)
Version             : Integer            ← v1.6: 3 = group; 2 = multi; 0/1/trống = single cũ
Groups              : Array of S_GroupData   ← v1.6 (Version 3 — snapshot trạng thái group)
```

**S_FurniturePlacement** (v1.6 thêm `GroupID`): `UniqueID(String), MeshPath, DAPath, Location, Rotation, Scale, ActorTag, MaterialPaths(Array String), GroupID(String)`. GroupID để restore đúng đồ nào thuộc group nào.

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

**Quá trình debug (Print String trace):**
- Index logic UndoLastAction/RedoLastAction ĐÚNG.
- CaptureSnapshot gọi 1 lần/thao tác (cảnh báo "double capture" ban đầu là ẢO — print bị đặt trong vòng ForEach Step 3, in 1 lần/mesh nên trông như gọi nhiều lần). → **Bài học: print debug đặt trên MAIN execution line, KHÔNG trong loop body.**
- DeselectAll clear đúng (POST-DESEL=0). Chỉ 1 instance InputManager (count=1).

**Root cause:** Với thao tác **Deselect**, execution trong CaptureSnapshot đi qua **NHÁNH KHÁC** (bypass đoạn build TempSelectedIndices ở Step 4 — print "SEL-AT-CAP" KHÔNG fire cho deselect, chỉ fire cho select). → `TempSelectedIndices` còn GIÁ TRỊ CŨ (stale) từ lần Select trước (idx=1) → snapshot "Deselect1" lưu nhầm là mesh1-đang-chọn → trông giống "Select1" → Undo nhìn như nhảy cóc.

**Fix (đã verify OK):** thêm **CLEAR TempSelectedIndices ngay đầu hàm CaptureSnapshot** (Step 0, sau Function Entry, trước Step 1). Đảm bảo `TempSelectedIndices` luôn sạch trước khi build, dù execution đi nhánh nào. CLEAR cũ ở Step 4 GIỮ LẠI làm backup (không hại).

**Bài học chung:** **biến CLASS persistent giữ giá trị giữa các lần gọi hàm → CLEAR ngay đầu hàm để tránh stale.** (Nếu là Local variable thì tự reset mỗi call, nhưng TempSelectedIndices là class var nên cần CLEAR tay.)

---

## ⭐ BUG IMPURE-TIMING — Undo không restore Groups (fix v1.6 — Sprint 3)

**Triệu chứng:** Select 3 → Ctrl+G → ... → Undo về bước CreateGroup → info bar không hiện group; log `Restore: Groups.Length = 0`. Diagnostic `SNAPSHOT chua: 0` → snapshot CreateGroup lưu Groups rỗng, dù lúc tạo `InputManager.Groups = 1`.

**Root cause:** `GetGroupsForSnapshot` là **impure function (CÓ exec pin)**. Output của impure function chỉ "đóng băng" giá trị TẠI thời điểm exec của nó chạy. Khi nối THẲNG output `Groups` của nó vào pin `Groups` của `Make S_SceneSnapshot`: nếu exec của GetGroupsForSnapshot chạy SAU node Make trong chuỗi → Make đọc giá trị default (rỗng). Hàm vẫn chạy (in ra `GGS tra ve: 1`) nhưng đã quá muộn.

**Fix (đã verify):** dùng biến đệm `TempGroups`. Đầu CaptureSnapshot: `Call GetGroupsForSnapshot → SET TempGroups`. Make node đọc `GET TempGroups` (không nối thẳng từ function nữa). Vì SET chạy sớm trong chuỗi → giá trị sẵn sàng khi Make đọc.

**Bài học:** impure function feeding data pin → output chỉ valid sau exec của nó. An toàn nhất: gọi sớm → SET temp var → node đọc temp var. (Cùng họ với "CLEAR class var đầu hàm".)

### GetGroupsForSnapshot() → Array<S_GroupData>  (v1.6)
```
Get All Actors Of Class(BP_FurnitureInputManager) → Length → Branch > 0:
  True → Get(0) → IsValid → True → GET Groups → Return Groups
  (else) → Return (rỗng)
```

---

## CaptureSnapshot(ActionName) — v1.5 MULTI
```
0. ← v1.5 FIX: CLEAR TempSelectedIndices   ← NGAY đầu hàm, trước mọi Branch (chống stale)
0b. ← v1.6 FIX: Call GetGroupsForSnapshot → SET TempGroups   ← đầu hàm, đệm group (chống impure-timing)

1. Branch CurrentIndex < Length(History) - 1:
   True → Array Resize(CurrentIndex + 1)   ← xóa redo stack

2. CLEAR TempMeshes
3. Get All Actors With Tag("FurnitureSpawned") → ForEach:
   Cast To BP_FurnitureActor (Array Element)
   Build S_FurniturePlacement:
     UniqueID = Get Display Name(Array Element)
     MeshPath, DAPath ← từ Cast BP_FurnitureActor
     Location, Rotation, Scale, ActorTag
     MaterialPaths = GET BP_FurnitureActor.MaterialOverrides
     GroupID = GET BP_FurnitureActor.GroupID         ← v1.6
   ADD to TempMeshes

4. ← v1.4: Build mảng index các đồ ĐANG CHỌN (thay vì 1 SelectedMeshIndex):
   CLEAR TempSelectedIndices                ← v1.5: giữ lại làm BACKUP (CLEAR chính ở Step 0)
   Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast:
     Failed → Branch(Length >= MaxSteps)
     Success → GET SelectedActors:
       ForEach SelectedActors (SelectedActor):                    ← OUTER
         ForEach Loop WITH BREAK [TempMeshes] (Index, Mesh):      ← INNER (có Break)
           Branch Mesh.UniqueID == Get Display Name(SelectedActor):
             True → ADD Index → TempSelectedIndices → BREAK (inner)
             False → (continue)
       Completed (outer) → Branch(Length >= MaxSteps)

   ⚠️ INNER ForEach PHẢI dùng "ForEach Loop WITH BREAK" và nối pin Break sau khi ADD →
      không break thì duyệt thừa, và đây từng là nghi phạm khi debug (thực ra bug ở nơi khác).
   ⚠️ Tất cả nhánh False/Failed đều nối vào Branch(Length >= MaxSteps) — không dead-end.

5. Branch Length >= MaxSteps → Remove Index 0 → CurrentIndex - 1

6. GET ActiveMode (từ BP_FurnitureInputManager)
   Make S_SceneSnapshot(
     ActionName,
     Meshes              = TempMeshes,
     SelectedMeshIndex   = -1,                  ← Version 2+ không dùng field này
     SelectedMeshIndices = TempSelectedIndices, ← v1.4
     ActiveMode,
     Version             = 3,                    ← v1.6 (group)
     Groups              = GET TempGroups        ← v1.6: đọc TempGroups, KHÔNG nối thẳng GetGroupsForSnapshot
   )
   → ADD to SnapshotHistory → CurrentIndex + 1
```

---

## UndoLastAction (Alt+Z)
```
Branch CurrentIndex <= 0 → False: CurrentIndex - 1 → RestoreSnapshot(CurrentIndex)
```

## RedoLastAction (Shift+Alt+Z)
```
Branch CurrentIndex >= Length - 1 → STOP
False: SET CurrentIndex = CurrentIndex + 1 → RestoreSnapshot(output pin của SET)
⚠️ PHẢI dùng output pin của SET, không GET riêng
```

---

## RestoreSnapshot(IndexHistory) — v1.4 MULTI
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
     [giữ nguyên — single restore]

5b. ← v1.6: Branch Snapshot.Version >= 3 (restore Groups):
     Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → IsValid:
       True → CLEAR InputManager.Groups
              ForEach Snapshot.Groups → ADD to InputManager.Groups
              Call SyncGroupsToContainer
     (Version < 3 → bỏ qua, Groups giữ nguyên rỗng/cũ)

6. RefreshButtonState(Snapshot.ActiveMode)

6b. ← v1.6: RE-FIRE selection để info bar + listener cập nhật SAU khi Groups đã restore:
    Get All Actors Of Class(InputManager) → Get(0) → IsValid:
      True → Branch (InputManager.SelectedActors.Length > 0):
               True  → Call SelectActors(InputManager.SelectedActors)   ← có chọn → re-fire OnSelectionChanged (info bar group)
               False → Call DeselectAll → DeactivateGizmo(GizmoController)  ← rỗng (snapshot deselect) → tắt outline + gizmo
    ⚠️ CẢ 2 nhánh merge về Step 7 (Broadcast) — không dead-end

7. Broadcast OnRestoreCompleted(GET RestoredBPActor)   ← single point
   ⚠️ Dùng RestoredBPActor (từ Cast output đúng snapshot), KHÔNG dùng SpawnedActors[class var SelectedMeshIndex]
```

**⚠️ Bug đã trả giá (v1.6):**
- **Undo về deselect không tắt outline/gizmo:** Step 6b — nhánh rỗng phải gọi DeselectAll + DeactivateGizmo (trước đây luôn SelectActors(rỗng) → không deselect).
- **Restore Groups phải SAU restore GroupID per actor** (Step 4) — để ExpandSelectionWithGroups (qua SelectActors re-fire ở 6b) thấy đúng quan hệ.

**⚠️ Tương thích ngược:** snapshot tạo trước v1.4 có `Version` = 0 (hoặc trống) → đi nhánh False (single fallback) → vẫn restore đúng 1 đồ. Snapshot mới Version=2 → multi.

---

## Event End Play — VRAM Leak Prevention
```
Event End Play →
  [Clear] SpawnedActors        ← drop array hard refs
  SET FoundActor = None
  [Clear] TempMeshes
  SET RestoredBPActor = None   ← v1.3
  [Clear] RestoredActors       ← v1.4: drop array hard refs
  [Clear] TempGroups           ← v1.6
```

---

## Key Learnings

- **DeselectAll (v1.4) thay DeselectMesh** trong RestoreSnapshot → dọn sạch multi-select trước khi spawn lại.
- **Version field** cho tương thích tiến/lùi: snapshot cũ (Version 0/1) → single fallback; mới (Version 2) → multi.
- **Nested ForEach With Break** trong CaptureSnapshot: outer = SelectedActors, inner = TempMeshes; match UniqueID → ADD index → BREAK inner.
- **SelectActors trong multi-restore** nhận RestoredActors (mảng build element-by-element → độc lập, không alias) → tự lo outline + gizmo.
- **KHÔNG gọi CaptureSnapshot trong DeselectMesh/DeselectAll** → infinite loop.
- **RedoLastAction dùng output pin của SET** CurrentIndex.
- **OnRestoreCompleted dùng RestoredBPActor** (Cast output đúng snapshot), không SpawnedActors[class var].
- **CaptureSnapshot("Initial")** gọi cuối Level Blueprint BeginPlay.
- **Load Asset Blocking trong RestoreSnapshot** — technical debt, refactor Async ở Phase B.
- **⭐ CLEAR biến class persistent ở ĐẦU hàm (v1.5):** `TempSelectedIndices` là class var → giữ giá trị giữa các lần gọi CaptureSnapshot. Nếu execution đi nhánh bypass đoạn build → giá trị cũ (stale) lọt vào snapshot. CLEAR đầu hàm là cách phòng thủ chắc chắn nhất.
- **⭐ Print debug đặt MAIN line, không trong loop:** print trong ForEach Step 3 in 1 lần/mesh → ngỡ "double capture" (thực ra gọi 1 lần). Mất thời gian debug sai hướng.
- **⭐ Impure function feeding data pin (v1.6):** output chỉ valid SAU exec của function. Nối thẳng vào Make node có thể đọc default nếu exec chạy sau. Fix: gọi sớm → SET temp var (TempGroups) → Make đọc temp var.
- **⭐ Re-fire selection SAU khi restore Groups (v1.6):** info bar đọc Groups, nên phải restore Groups (Step 5b) TRƯỚC khi re-fire OnSelectionChanged (Step 6b). Nhánh selection rỗng → DeselectAll + DeactivateGizmo (không SelectActors rỗng).
- **⭐ Diagnostic print phân biệt capture vs restore (v1.6):** in `SNAPSHOT chua: N` (đọc Groups TRONG snapshot tại RestoreSnapshot) để biết bug ở capture (snapshot lưu rỗng) hay restore (snapshot có nhưng không đổ vào). Chốt nhanh thay vì đoán.

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|-----------|------|----------|
| 1.0 | 21/04/2026 | Tài liệu đầu tiên |
| 1.1 | 09/05/2026 | Event End Play cleanup (Fix 5.1 VRAM leak) |
| 1.2 | 16/05/2026 | v1.1 Material: MaterialPaths capture/restore, OnRestoreCompleted |
| 1.3 | 20/05/2026 | Fix broadcast bug: RestoredBPActor var → single broadcast point |
| 1.4 | 04/06/2026 — 15:30 ICT | Multi-Snapshot (T12): S_SceneSnapshot +Version +SelectedMeshIndices; CaptureSnapshot build TempSelectedIndices (nested ForEach With Break); RestoreSnapshot DeselectAll + branch Version; +RestoredActors var + End Play clear |
| 1.5 | 07/06/2026 — 22:40 ICT | **Fix bug stale TempSelectedIndices:** thêm CLEAR ở Step 0 (đầu hàm CaptureSnapshot). Bug Undo nhảy cóc khi xen kẽ Select/Deselect do TempSelectedIndices giữ giá trị cũ khi execution đi nhánh deselect bypass đoạn build. Bài học: CLEAR class var đầu hàm; print debug đặt main line không trong loop. |
| 1.6 | 10/06/2026 — 20:34 ICT | **Sprint 3 Group + fix Undo group.** Struct: S_SceneSnapshot +Groups, Version=3; S_FurniturePlacement +GroupID. Var +TempGroups. CaptureSnapshot: Step 0b SET TempGroups (fix impure-timing), Step 3 capture GroupID, Make đọc TempGroups. RestoreSnapshot: Step 4 restore GroupID, Step 5b restore Groups (Version>=3) + Sync, Step 6b re-fire selection (rỗng→DeselectAll+DeactivateGizmo). +GetGroupsForSnapshot. End Play clear TempGroups. Fix: undo về deselect không tắt outline/gizmo; impure-timing snapshot Groups rỗng. |
