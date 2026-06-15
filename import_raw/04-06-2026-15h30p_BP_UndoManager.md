# BP_UndoManager
**Phiên bản:** 1.4 | **Cập nhật:** 04/06/2026 — 15:30 ICT | Actor riêng — quản lý toàn bộ Undo/Redo

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
```

---

## S_SceneSnapshot struct (v1.4)
```
ActionName          : String
Meshes              : Array of S_FurniturePlacement
SelectedMeshIndex   : Integer            ← Version 1 (single), giữ tương thích
ActiveMode          : E_ActiveMode
SelectedMeshIndices : Array of Integer   ← v1.4 (Version 2 - nhiều đồ)
Version             : Integer            ← v1.4: 2 = multi; 0/1/trống = single cũ
```

**S_FurniturePlacement** (không đổi): `UniqueID(String), MeshPath, DAPath, Location, Rotation, Scale, ActorTag, MaterialPaths(Array String)`. Đã có đủ Location/Rotation/Scale → snapshot ghi được cả rotate/scale.

---

## Event Dispatcher
```
OnRestoreCompleted(RestoredSelectedActor : BP_FurnitureActor)
  ← Broadcast cuối RestoreSnapshot, sau khi spawn actors xong
  ← WBP_FurnitureInventory bind để update TargetFurnitureActor
  ← Multi-restore: truyền PrimarySelectedActor (đồ primary trong nhóm)
```

---

## CaptureSnapshot(ActionName) — v1.4 MULTI
```
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
   ADD to TempMeshes

4. ← v1.4: Build mảng index các đồ ĐANG CHỌN (thay vì 1 SelectedMeshIndex):
   CLEAR TempSelectedIndices
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
     SelectedMeshIndex   = -1,                  ← Version 2 không dùng field này
     SelectedMeshIndices = TempSelectedIndices, ← v1.4
     ActiveMode,
     Version             = 2                     ← v1.4
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

6. RefreshButtonState(Snapshot.ActiveMode)

7. Broadcast OnRestoreCompleted(GET RestoredBPActor)   ← single point, no branch
   ⚠️ Dùng RestoredBPActor (từ Cast output đúng snapshot), KHÔNG dùng SpawnedActors[class var SelectedMeshIndex]
```

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

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|-----------|------|----------|
| 1.0 | 21/04/2026 | Tài liệu đầu tiên |
| 1.1 | 09/05/2026 | Event End Play cleanup (Fix 5.1 VRAM leak) |
| 1.2 | 16/05/2026 | v1.1 Material: MaterialPaths capture/restore, OnRestoreCompleted |
| 1.3 | 20/05/2026 | Fix broadcast bug: RestoredBPActor var → single broadcast point |
| 1.4 | 04/06/2026 — 15:30 ICT | **Multi-Snapshot (T12):** S_SceneSnapshot +Version +SelectedMeshIndices; CaptureSnapshot build TempSelectedIndices (nested ForEach With Break); RestoreSnapshot DeselectAll + branch Version (multi via SelectActors / single fallback); +RestoredActors var + End Play clear |
