# BP_UndoManager
**Phiên bản:** 1.2 | **Cập nhật:** 16/05/2026 — 14:08 ICT | Actor riêng — quản lý toàn bộ Undo/Redo

---

## Variables
```
SnapshotHistory   : Array of S_SceneSnapshot
CurrentIndex      : Integer
MaxSteps          : Integer (50)
SelectedMeshIndex : Integer
TempMeshes        : Array of S_FurniturePlacement
SpawnedActors     : Array of StaticMeshActor   ← hard ref, clear ở EndPlay
FoundActor        : StaticMeshActor             ← hard ref, clear ở EndPlay
TargetUniqueID    : String
```

---

## Event Dispatcher
```
OnRestoreCompleted(RestoredSelectedActor : BP_FurnitureActor)
  ← Broadcast cuối RestoreSnapshot, sau khi spawn actors xong
  ← WBP_FurnitureInventory bind để update TargetFurnitureActor
```

---

## CaptureSnapshot(ActionName)
```
1. Branch CurrentIndex < Length(History) - 1:
   True → Array Resize (CurrentIndex + 1)  ← xóa redo stack

2. CLEAR TempMeshes
3. Get All Actors With Tag("FurnitureSpawned") → For Each:
   Cast To BP_FurnitureActor (Array Element)
   Build S_FurniturePlacement:
     UniqueID    = Get Display Name(Array Element)
     MeshPath, DAPath ← PHẢI lấy từ Cast BP_FurnitureActor
     Location, Rotation, Scale, ActorTag
     MaterialPaths = GET BP_FurnitureActor.MaterialOverrides  ← v1.1
   ADD to TempMeshes

4. SET SelectedMeshIndex = -1  ← reset trước mọi branch
   Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast:
     Failed → Branch(Length >= MaxSteps)
     Success:
       IsValid(SelectedFurnitureActor)?
         False → Branch(Length >= MaxSteps)
         True:
           HasTag("FurnitureSpawned")?
             False → Branch(Length >= MaxSteps)
             True:
               For Each TempMeshes → UniqueID == Get Display Name(SelectedFurnitureActor)
               → SET SelectedMeshIndex = Array Index
               Completed → Branch(Length >= MaxSteps)

⚠️ Tất cả nhánh False đều nối vào Branch(Length >= MaxSteps) — không dừng!

5. Branch Length >= MaxSteps → Remove Index 0 → CurrentIndex - 1

6. GET ActiveMode (từ BP_FurnitureInputManager)
   Make S_SceneSnapshot(ActionName, TempMeshes, SelectedMeshIndex, ActiveMode)
   → ADD to SnapshotHistory → CurrentIndex + 1
```

---

## UndoLastAction (Alt+Z)
```
Branch CurrentIndex <= 0 → False:
  CurrentIndex - 1 → RestoreSnapshot(CurrentIndex)
```

---

## RedoLastAction (Shift+Alt+Z)
```
Branch CurrentIndex >= Length - 1 → STOP
False:
  SET CurrentIndex = CurrentIndex + 1
  RestoreSnapshot(output pin của SET)
  ← PHẢI dùng output pin của SET, không GET riêng
```

---

## RestoreSnapshot(IndexHistory)
```
1. Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → DeselectMesh
   ← KHÔNG gọi CaptureSnapshot ở đây

2. Destroy All Actors tag "FurnitureSpawned"

3. CLEAR SpawnedActors

4. For Each Snapshot.Meshes (Placement):
   Spawn BP_FurnitureActor → Load Asset Blocking → Set Static Mesh
   SET MeshPath, SET DAPath
   GET Tags → ADD "FurnitureSpawned"  ← KHÔNG SET Tags lại
   ADD to SpawnedActors

   ← v1.1: Restore MaterialPaths
   For Each Placement.MaterialPaths (Index, Path):
     Branch Path != "":
       Load Asset Blocking(Path) → Cast To MaterialInterface → MI_Source
       Create Dynamic Material Instance(FurnitureMesh, MI_Source, Index) → MID
       Set Material(FurnitureMesh, Index, MID)
   SET BP_FurnitureActor.MaterialOverrides = Placement.MaterialPaths

5. Branch SelectedMeshIndex >= 0:
   True:
     FoundActor = SpawnedActors[SelectedMeshIndex]
     Cast To BP_FurnitureActor(FoundActor) → SET SelectedFurnitureActor (BP_FurnitureInputManager)
     DeactivateGizmo
     Set Custom Depth True + Stencil 255
     Branch ActiveMode != Select:
       ActivateGizmo(FoundActor, TransformerPawn,
         Select node: Move→Translation, Rotate→Rotation, Scale→Scale)
   False:
     Set Custom Depth False
     SET SelectedFurnitureActor = None (BP_FurnitureInputManager)
     DeactivateGizmo

6. RefreshButtonState(Snapshot.ActiveMode)

7. ← v1.1: Broadcast OnRestoreCompleted
   Branch SelectedMeshIndex >= 0:
     True  → Broadcast OnRestoreCompleted(SpawnedActors[SelectedMeshIndex])
     False → Broadcast OnRestoreCompleted(None)
```

---

## Event End Play — VRAM Leak Prevention (Fix 5.1)

**Mục đích:** Drop hard references đến UObject để Garbage Collector có thể destroy actors → free render data trong VRAM.

**Implementation:**
```
Event End Play
   │
   ▼
[Clear] SpawnedActors    ← drop array of hard refs
   │
   ▼
SET FoundActor = None    ← drop single hard ref
   │
   ▼
[Clear] TempMeshes       ← cleanup struct array
```

---

## Key Learnings

- **DeselectMesh trước, CaptureSnapshot sau** — KHÔNG gọi CaptureSnapshot trong DeselectMesh → infinite loop
- **RedoLastAction dùng output pin của SET** CurrentIndex, không GET riêng
- **CaptureSnapshot("Initial")** gọi cuối Level Blueprint BeginPlay
- **MaterialPaths trong S_FurniturePlacement** capture GET MaterialOverrides từ BP_FurnitureActor → restore qua Load Asset Blocking + Create MID + Set Material
- **OnRestoreCompleted broadcast** cuối RestoreSnapshot để WBP_FurnitureInventory update TargetFurnitureActor
- **Load Asset Blocking trong RestoreSnapshot** — technical debt, refactor sang Async khi Phase B

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|-----------|------|----------|
| 1.0 | 21/04/2026 — 16:46 ICT | Tài liệu đầu tiên |
| 1.1 | 09/05/2026 — 09:15 ICT | Thêm Event End Play cleanup (Fix 5.1 VRAM leak) |
| 1.2 | 16/05/2026 — 14:08 ICT | v1.1 Material: thêm MaterialPaths capture/restore, Event Dispatcher OnRestoreCompleted |
