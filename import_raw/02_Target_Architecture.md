# 02 — Target Architecture
**Mục đích:** Mô tả chính xác kiến trúc sau khi hoàn thành 7 sprint.

---

## TỔNG QUAN HỆ THỐNG SAU

```
LEVEL BLUEPRINT BeginPlay
  ├── Spawn BP_UndoManager
  ├── Spawn BP_FurnitureSceneManager
  ├── Spawn BP_TransformerPawn
  ├── Spawn BP_GizmoController
  ├── Spawn BP_FurnitureInputManager
  ├── Spawn BP_FurnitureUserPrefsManager
  ├── Spawn BP_GroupsContainer       ← Sprint 3 (chứa Groups data cho EMS)
  ├── Create WBP_MeshControls
  └── CaptureSnapshot("Initial")
```

---

## SELECTION SYSTEM — Sau Sprint 1

```
BP_FurnitureInputManager Variables:

  ← Multi-select state
  SelectedActors        : Array of BP_FurnitureActor   ← MỚI
  PrimarySelectedActor  : BP_FurnitureActor             ← MỚI (anchor for Align)

  ← Pivot Actor cho gizmo multi-select
  GizmoPivotActor       : BP_PivotActor                 ← MỚI (spawn khi cần)

  ← Group state (Sprint 3+)
  Groups                : Array of S_GroupData          ← MỚI Sprint 3
  CurrentEditingGroupID : String                        ← MỚI Sprint 4 (empty = no edit)

  ← Clipboard multi (Sprint 1)
  ClipboardActors       : Array of S_ClipboardEntry     ← thay clipboard cũ

  ← Replace mode (giữ nguyên)
  bIsReplaceMode        : Boolean
  MeshToReplace         : BP_FurnitureActor

  ← Deprecated nhưng giữ để compat
  SelectedFurnitureActor : BP_FurnitureActor
    ← Đồng bộ với PrimarySelectedActor (deprecated, gỡ ở Sprint 7)

Event Dispatchers (MỚI):
  OnSelectionChanged(Actors : Array of BP_FurnitureActor,
                      Primary : BP_FurnitureActor)
    ← Fire mỗi khi selection thay đổi

  OnGroupCreated(GroupID : String)
  OnGroupDestroyed(GroupID : String)
  OnGroupModeChanged(IsEditMode : Boolean, EditingGroupID : String)

Event Dispatchers (deprecated, vẫn fire để compat):
  OnMeshSelected(BP_FurnitureActor) — fire khi Primary thay đổi
  OnMeshDeselected() — fire khi SelectedActors empty
```

---

## MOUSE LEFT PRESSED — Sau Sprint 1

```
Step 0: Set Input Mode Game And UI
Step 1: LocalWasGizmoActive = GizmoControllerRef.bGizmoActive
Step 2: GizmoController → OnMousePressed
Step 3: Branch bIsDraggingGizmo → STOP

Step 4: GetHitResultUnderCursorByChannel(CAMERA) → HitActor, bHit
Step 5: Branch bHit == False:
          IsCtrlDown == False:
            DeselectAll → CaptureSnapshot("Deselect") → STOP
          IsCtrlDown == True:
            STOP (giữ selection, không deselect)

Step 6: Branch HasTag("FurnitureSpawned") == False:
          IsCtrlDown == False:
            DeselectAll → STOP
          IsCtrlDown == True:
            STOP

Step 7: ← Xác định Cast actor có thuộc group nào không (Sprint 3)
        Cast HitActor → BP_FurnitureActor → GET GroupID

        Branch GroupID != "" AND IsEditMode == False:
          ← Click vào đồ trong group → chọn cả group
          GET Groups → find by GroupID → GET ChildActors
          IsCtrlDown:
            False → DeselectAll → SelectActors(ChildActors)
            True  → ToggleActors(ChildActors)
          STOP

        ← Không thuộc group hoặc đang trong Edit mode:
        Branch IsCtrlDown:
          False → DeselectAll → SelectSingleActor(HitActor)
          True  → ToggleActor(HitActor)

Step 8: ← Multi outline update
        DisableOutlineAll(OldSelection)
        EnableOutlineAll(NewSelection)
        ← Primary actor: Stencil = 255
        ← Secondary actors: Stencil = 254

Step 9: ← Pivot Actor cho gizmo
        Branch SelectedActors.Length > 0:
          T → Branch SelectedActors.Length == 1:
                T → ActivateGizmo on single actor (giống cũ)
                F → Spawn/Update GizmoPivotActor at center → ActivateGizmo on pivot
          F → DeactivateGizmo + Destroy GizmoPivotActor

Step 10: CaptureSnapshot("Select")
Step 11: Broadcast OnSelectionChanged(SelectedActors, Primary)
Step 12: Update WBP_MeshControls (count, button states)
```

---

## NEW HELPER FUNCTIONS — Sprint 1

### SelectActors(Array of BP_FurnitureActor)
```
ForEach Actors:
  Branch NOT Contains(SelectedActors, Actor):
    T → ADD to SelectedActors
SET PrimarySelectedActor = Last element of Actors
UpdateOutlineState
UpdateGizmo
Broadcast OnSelectionChanged
```

### SelectSingleActor(BP_FurnitureActor)
```
DeselectAll
ADD Actor to SelectedActors
SET PrimarySelectedActor = Actor
UpdateOutlineState
UpdateGizmo
Broadcast OnSelectionChanged
```

### ToggleActor(BP_FurnitureActor)
```
Branch Contains(SelectedActors, Actor):
  T → REMOVE from SelectedActors
       SET PrimarySelectedActor = Last(SelectedActors) (or None if empty)
  F → ADD to SelectedActors
       SET PrimarySelectedActor = Actor
UpdateOutlineState
UpdateGizmo
Broadcast OnSelectionChanged
```

### ToggleActors(Array of BP_FurnitureActor)
```
ForEach Actor: ToggleActor(Actor)
```

### DeselectAll
```
ForEach SelectedActors:
  Cast → GET FurnitureMesh → Set Render Custom Depth = False
CLEAR SelectedActors
SET PrimarySelectedActor = None
DeactivateGizmo
Destroy GizmoPivotActor (if exists)
Broadcast OnSelectionChanged([], None)
```

### UpdateOutlineState
```
ForEach SelectedActors (Index, Actor):
  Cast → GET FurnitureMesh:
    Set Render Custom Depth = True
    Branch Actor == PrimarySelectedActor:
      T → Set Custom Depth Stencil Value = 255
      F → Set Custom Depth Stencil Value = 254
```

### UpdateGizmo
```
Branch SelectedActors.Length:
  == 0 → DeactivateGizmo, Destroy Pivot
  == 1 → DeactivateGizmo, Destroy Pivot, ActivateGizmo(SelectedActors[0])
  >= 2 → SpawnOrUpdatePivot, ActivateGizmo(GizmoPivotActor)
```

### SpawnOrUpdatePivot
```
Branch IsValid(GizmoPivotActor):
  False → Spawn BP_PivotActor at CalculateCenter(SelectedActors) → SET GizmoPivotActor
  True  → Set Actor Location(GizmoPivotActor, CalculateCenter(SelectedActors))

  ForEach SelectedActors:
    InitialOffset = Actor.Location - Pivot.Location
    SET Actor.PivotOffset = InitialOffset   ← lưu offset relative
```

### CalculateCenter(Actors) → Vector
```
Sum = (0,0,0)
ForEach Actors: Sum += Actor.GetActorLocation
Return Sum / Actors.Length
```

---

## PIVOT ACTOR (BP_PivotActor)

```
Parent: Actor (không phải StaticMeshActor — không cần mesh)
Tag: "FurniturePivot" (NOT "FurnitureSpawned" — tránh EMS save)

Variables:
  AttachedActors : Array of BP_FurnitureActor
  InitialOffsets : Array of Vector   ← position offsets relative to pivot

Components:
  Scene Component (root, không visual)

Functions:
  RefreshOffsets():
    CLEAR InitialOffsets
    ForEach AttachedActors:
      Offset = Actor.Location - Self.Location
      ADD to InitialOffsets

  ApplyTransformToChildren():
    ForEach AttachedActors (Index):
      NewLocation = Self.Location + InitialOffsets[Index].RotateBy(Self.Rotation - InitialPivotRotation)
      NewLocation *= Self.Scale / InitialPivotScale
      Actor.SetActorLocation(NewLocation)
      Actor.AddActorWorldRotation(Self.Rotation - LastPivotRotation)
      Actor.SetActorScale3D(InitialChildScales[Index] * Self.Scale / InitialPivotScale)
```

**Pivot Actor Tick:** check nếu Transform thay đổi → ApplyTransformToChildren

---

## GIZMO SYSTEM — Sau Sprint 1

```
BP_GizmoController Variables:
  SelectedActor : StaticMeshActor (Single — có thể là Pivot)
  bGizmoActive  : Boolean
  ...

Multi-select behavior:
  - 1 actor: ActivateGizmo(actor) — giống cũ
  - >= 2 actors: ActivateGizmo(PivotActor) → Pivot tự đồng bộ children
```

**Không sửa BP_GizmoController logic chính** — chỉ thay đổi caller (BP_FurnitureInputManager) để pass đúng actor (single hoặc pivot).

---

## DATA STRUCTURES SAU 7 SPRINT

### S_FurniturePlacement (mở rộng)
```
MeshPath, DAPath, Location, Rotation, Scale, ActorTag, UniqueID
MaterialPaths     : Array of String    ← v1.1
MaterialParams    : Array of String    ← v1.2 (Sprint 7) — JSON per slot
SurfaceType       : Name                ← v1.2 B1
GroupID           : String              ← MỚI Sprint 3
bIsLocked         : Boolean             ← MỚI Sprint 6
CustomName        : String              ← MỚI Sprint 6
```

### S_GroupData (MỚI — Sprint 3)
```
GroupID       : String          ← unique, auto-gen
GroupName     : String          ← user-facing
ParentGroupID : String          ← rỗng nếu top-level
bIsLocked     : Boolean
```

⚠️ KHÔNG lưu ChildActors trong S_GroupData — dùng GroupID trên BP_FurnitureActor để truy ngược.

### S_SceneSnapshot (mở rộng)
```
Version             : Integer (= 2 sau Sprint 1, = 3 sau Sprint 3)
ActionName          : String
Meshes              : Array of S_FurniturePlacement
SelectedMeshIndices : Array of Integer   ← MỚI Sprint 1 (thay SelectedMeshIndex)
Groups              : Array of S_GroupData   ← MỚI Sprint 3
ActiveMode          : E_ActiveMode
EditingGroupID      : String             ← MỚI Sprint 4
```

### S_ClipboardEntry (MỚI — Sprint 1)
```
MeshPath, DAPath
RelativeLocation : Vector       ← so với clipboard center
Rotation         : Rotator
Scale            : Vector
MaterialOverrides : Array of String
SurfaceType      : Name
```

### S_ComboMeshData (DataTable row — Sprint 5)
```
ComboName     : String
Category      : String          ← Phòng khách / Phòng ăn / ...
Style         : String          ← Modern / Scandinavian / ...
Tags          : String          ← pipe-separated
ItemCount     : Integer
ThumbnailPath : Soft Object Reference Texture2D
ComboJSON     : String          ← JSON: meshes + groups (relative positions)
```

---

## GROUP SYSTEM — Sau Sprint 3

### Cách tổ chức group (DATA-ONLY, KHÔNG có Actor)

```
BP_FurnitureActor.GroupID    = "g_abc123"   ← lưu trên actor
BP_FurnitureActor.GroupID    = "g_abc123"   ← actor khác cùng group
BP_FurnitureActor.GroupID    = ""           ← actor không thuộc group

BP_FurnitureInputManager.Groups = [
  { GroupID: "g_abc123", GroupName: "Bộ sofa", ParentGroupID: "", bIsLocked: false },
  { GroupID: "g_def456", GroupName: "Bộ bàn ăn", ParentGroupID: "", bIsLocked: false },
]

← Nested group:
  ParentGroupID = "g_root"  ← nested under another group
```

### Query Group Members
```
GetGroupChildren(GroupID) → Array of BP_FurnitureActor:
  Get All Actors With Tag("FurnitureSpawned")
  Filter: Cast → GET GroupID == InputGroupID
```

### Tạo Group
```
CreateGroup(Name, Actors):
  GroupID = "g_" + GenerateUUID()
  ADD S_GroupData{GroupID, Name, "", False} to Groups
  ForEach Actors: SET Actor.GroupID = GroupID
  Broadcast OnGroupCreated(GroupID)
  CaptureSnapshot("CreateGroup")
```

### Hủy Group (Ungroup)
```
UngroupActors(GroupID, RecursiveAll):
  GET children = GetGroupChildren(GroupID)
  ForEach children:
    Branch RecursiveAll AND child có sub-group:
      T → UngroupActors(child.GroupID, True) recursive
    SET child.GroupID = "" (hoặc ParentGroupID nếu có)
  REMOVE S_GroupData where GroupID == InputGroupID
  Broadcast OnGroupDestroyed(GroupID)
  CaptureSnapshot("Ungroup")
```

### Save/Load Group qua EMS

**BP_GroupsContainer** (Actor mới, tag "FurnitureGroupsContainer"):
```
Variables (SaveGame):
  Groups : Array of S_GroupData

Implements EMSActorSaveInterface.
EMS save/load actor này như các BP_FurnitureActor khác.
1 và chỉ 1 instance trong scene.

Event BeginPlay:
  GET Tags → ADD "FurnitureGroupsContainer" → SET Tags

Event ActorLoaded:
  Sync data sang BP_FurnitureInputManager.Groups
```

**Lý do dùng Actor riêng:** EMS chỉ save Actors. Lưu Groups vào 1 actor riêng = đảm bảo persistence không phải sửa EMS.

---

## EDIT MODE SYSTEM — Sau Sprint 4

```
BP_FurnitureInputManager.CurrentEditingGroupID : String

Khi == "" : bình thường, click vào đồ trong group sẽ chọn CẢ group
Khi != "" : edit mode, click vào đồ trong group sẽ chọn TỪNG đồ

EnterEditMode(GroupID):
  SET CurrentEditingGroupID = GroupID
  ApplyDimmingOverlay (đồ không thuộc group bị mờ)
  Broadcast OnGroupModeChanged(True, GroupID)

ExitEditMode():
  SET CurrentEditingGroupID = ""
  RemoveDimmingOverlay
  Broadcast OnGroupModeChanged(False, "")
```

### Dimming overlay implementation

**Cách đơn giản:** Post Process Volume + Material Function check stencil
- Đồ trong edit group: render bình thường
- Đồ ngoài: dim qua post process

**Cách dễ hơn (recommended cho Sprint 4):** Overlay Widget toàn viewport
- Spawn WBP_EditModeOverlay (semi-transparent black, anchor stretch)
- Z Order thấp hơn các widget khác nhưng cao hơn viewport
- Edit mode group members render qua Custom Depth + Material Outline (override z order)

---

## COMBO MESH SYSTEM — Sau Sprint 5

```
DT_ComboMeshCatalog (DataTable):
  Row 1: "Bộ sofa 3 món Scandinavian" {...}
  Row 2: "Bộ bàn ăn 6 ghế" {...}
  ...
```

### Lưu Combo
```
SaveCurrentGroupAsCombo(GroupID, ComboName, Category, Style, Tags):
  GET children = GetGroupChildren(GroupID)
  center = CalculateCenter(children)

  comboJSON = {
    meshes: children.Map(actor → {
      meshPath, dapath, rotation, scale, materialOverrides,
      relativeLocation = actor.Location - center
    }),
    groups: GetGroupsInHierarchy(GroupID)  ← nested groups
  }

  thumbnail = GenerateComboThumbnail(children)   ← SceneCapture2D
  ADD row to DT_ComboMeshCatalog
```

### Spawn Combo
```
SpawnCombo(RowName, WorldLocation):
  GetDataTableRow → comboData
  Parse comboData.ComboJSON → meshes, groups

  newGroupIDMap = {}   ← map old GroupID → new GroupID
  ForEach groups: newGroupIDMap[oldID] = "g_" + GenerateUUID()

  ForEach meshes (mesh):
    actualLocation = WorldLocation + mesh.relativeLocation
    SpawnFurnitureCopy(
      MeshPath = mesh.meshPath, ...,
      Location = actualLocation
    )
    Branch mesh has GroupID:
      SET newActor.GroupID = newGroupIDMap[mesh.GroupID]

  ForEach groups: ADD S_GroupData with new GroupID to InputManager.Groups
```

---

## EVENT FLOW DIAGRAMS

### Mouse Click → Selection Update

```
User Click
  ↓
BP_FurnitureInputManager.MouseLeftPressed
  ↓
  Determine: Single / Toggle / Group click
  ↓
  Call SelectActors / SelectSingleActor / ToggleActor
  ↓
  UpdateOutlineState (ForEach apply Custom Depth)
  ↓
  UpdateGizmo (Pivot Actor or single gizmo)
  ↓
  Broadcast OnSelectionChanged
       ↓
       ├── WBP_MeshControls.OnSelectionChanged → update button states + count
       ├── WBP_FurnitureInventory.OnSelectionChanged → update Material panel
       └── (other listeners)
```

### Group Creation Flow

```
User: Multi-select 5 đồ → Ctrl+G
  ↓
Open WBP_GroupNameDialog → Type "Bộ bàn ăn" → OK
  ↓
BP_FurnitureInputManager.CreateGroup("Bộ bàn ăn", SelectedActors)
  ↓
  Generate GroupID
  ADD S_GroupData to Groups
  ForEach SelectedActors: SET GroupID
  Sync to BP_GroupsContainer for save
  ↓
  Broadcast OnGroupCreated
  CaptureSnapshot("CreateGroup")
```

### Undo Flow

```
User: Ctrl+Z
  ↓
BP_UndoManager.UndoLastAction
  ↓
  CurrentIndex - 1 → RestoreSnapshot(CurrentIndex)
  ↓
  DeselectAll (BP_FurnitureInputManager)
  Destroy all actors tag "FurnitureSpawned"
  Spawn actors from snapshot.Meshes
  ForEach: SET GroupID, MaterialOverrides, bIsLocked, ...

  Sync BP_FurnitureInputManager.Groups = snapshot.Groups
  Sync BP_GroupsContainer.Groups = snapshot.Groups

  Restore SelectedMeshIndices → reselect actors
  ↓
  Broadcast OnRestoreCompleted
```

---

## R1-R5 COMPLIANCE CHECKLIST

| Component | R1 (Async) | R2 (Soft Ref) | R3 (Light Data) | R4 (Destruct Clear) | R5 (No Path) |
|---|---|---|---|---|---|
| BP_PivotActor | N/A | N/A | N/A | N/A | N/A |
| BP_GroupsContainer | N/A | N/A | N/A | N/A | Lưu GroupID |
| S_GroupData | N/A | N/A | Struct nhẹ | N/A | Lưu GroupID, ParentID |
| WBP_SceneOutliner | Async load thumbnail | Soft Ref đến Actor | Nhận GroupID | Event Destruct clear | Lưu GroupID |
| WBP_ComboCard | Async load thumbnail | Soft Ref combo data | Nhận RowName | Event Destruct clear | Lưu RowName |
| WBP_MaterialEditPanel | Async load MID | Soft Ref FurnitureMesh | Nhận MaterialPath | Event Destruct clear | Lưu RowName |
| Combo JSON | N/A | N/A | Strings only | N/A | Lưu MeshPath (string) |

---

## PERFORMANCE TARGETS

| Operation | Target | Đo bằng |
|---|---|---|
| Click chọn 1 actor | < 10ms | Stat unit |
| Ctrl+Click thêm vào selection | < 5ms | |
| Move 20 actors qua gizmo | < 2ms/frame | |
| CaptureSnapshot 50 actors + 5 groups | < 15ms | |
| Spawn combo 10 meshes (async) | < 1s total | |
| Box select 30 actors | < 50ms | |
| RestoreSnapshot 50 actors | < 200ms | Existing baseline |

---

## TÍCH HỢP VỚI PROJECT TỔNG

Khi merge vào project chính:
- **Variables thêm vào shared code:**
  - Foff_GameInstance: không thêm gì mới (đã có FurnitureInventoryRef)
  - BP_FoffPlayerController: không thêm gì (input route qua BP_FurnitureInputManager)

- **Actor classes mới:**
  - BP_PivotActor (Sprint 1)
  - BP_GroupsContainer (Sprint 3)

- **DataTable mới:**
  - DT_ComboMeshCatalog (Sprint 5)

- **Báo đồng nghiệp:**
  - Custom Depth Stencil values 254 (secondary selection) — đảm bảo material outline không conflict
  - "FurniturePivot" tag — đảm bảo logic khác không động đến actor này
  - "FurnitureGroupsContainer" tag — đảm bảo EMS save bao gồm
