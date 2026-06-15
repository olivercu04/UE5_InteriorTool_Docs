# 01 — Current Architecture Audit
**Mục đích:** Phân tích chi tiết kiến trúc hiện tại để biết chính xác cần thay đổi gì.

---

## TỔNG QUAN HỆ THỐNG

```
LEVEL BLUEPRINT BeginPlay
  ├── Spawn BP_UndoManager
  ├── Spawn BP_FurnitureSceneManager (EMS Save/Load)
  ├── Spawn BP_TransformerPawn (gizmo visual)
  ├── Spawn BP_GizmoController (gizmo logic)
  ├── Spawn BP_FurnitureInputManager (input hub)
  ├── Spawn BP_FurnitureUserPrefsManager (recent/favorite)
  ├── Create WBP_MeshControls (toolbar)
  └── CaptureSnapshot("Initial")
```

---

## SELECTION SYSTEM (BP_FurnitureInputManager)

### Trạng thái hiện tại

```
Variables:
  SelectedFurnitureActor : BP_FurnitureActor   ← SINGLE actor
  CurrentMeshControls    : WBP_MeshControls
  GizmoControllerRef     : BP_GizmoController
  TransformerPawnRef     : BP_TransformerPawn
  ActiveMode             : E_ActiveMode
  DetailPopupRef         : WBP_DetailPopup
  bIsReplaceMode         : Boolean
  MeshToReplace          : BP_FurnitureActor

Event Dispatchers:
  OnMeshDeselected()                              ← fire cuối DeselectMesh
  OnMeshSelected(BP_FurnitureActor)               ← fire sau Step 8
```

### Mouse Left Pressed Flow (12 step)

```
Step 0:  Set Input Mode Game And UI
Step 1:  LocalWasGizmoActive = GizmoControllerRef.bGizmoActive
Step 2:  GizmoController → OnMousePressed
Step 3:  Branch bIsDraggingGizmo == True → STOP
Step 4:  GetHitResultUnderCursorByChannel(CAMERA) → HitActor, bHit
Step 5:  Branch bHit == False → DeselectMesh + CaptureSnapshot("Deselect") → STOP
Step 6:  Branch HasTag("FurnitureSpawned") == False → DeselectMesh → STOP
Step 7:  Branch IsValid(SelectedFurnitureActor) → True:
            DeactivateGizmo
            Set Render Custom Depth = False (old selection)
Step 8:  Cast HitActor → SET SelectedFurnitureActor
         Broadcast OnMeshSelected(SelectedFurnitureActor)
Step 9:  Set Render Custom Depth = True, Stencil = 255
Step 10: CaptureSnapshot("Select")
Step 11: Update WBP_MeshControls
Step 12: Sequence Then 1: ActivateGizmo (nếu ActiveMode != Select)
```

### Điểm yếu hiện tại (cần fix cho Sprint 1)

| Bug tiềm ẩn | Mô tả |
|---|---|
| Single state | Tất cả logic chỉ làm việc với 1 actor |
| Step 7 disable old outline | Cần đổi sang ForEach disable all old outlines |
| Step 8 SET single | Cần đổi sang ADD/REMOVE từ array |
| Step 12 ActivateGizmo | Cần handle multi-select (pivot actor) |

### DeselectMesh Function

```
Cast SelectedFurnitureActor → BP_FurnitureActor
  → GET FurnitureMesh → Set Render Custom Depth = False
SET SelectedFurnitureActor = None
GizmoController → DeactivateGizmo
Broadcast OnMeshDeselected
```

⚠️ Cần đổi thành `DeselectAll` xử lý array.

---

## GIZMO SYSTEM (BP_GizmoController)

### Trạng thái hiện tại

```
Variables:
  SelectedActor         : StaticMeshActor   ← SINGLE
  bGizmoActive          : Boolean
  bIsDraggingGizmo      : Boolean
  ActiveAxis            : String ("X Axis Box", "Y Axis Box"...)
  InitialActorLocation  : Vector            ← capture trước drag

  SnapStep, SnapAngle, SnapScale
  RotationSpeed, ScaleSpeed
```

### ActivateGizmo Flow

```
Input: TargetActor, TransformerPawn, TransformType

SET SelectedActor = TargetActor
SET TransformerPawnRef = TransformerPawn

Branch bGizmoActive:
  True  → Deselect All (toggle off)
  False → Activate:
    TransformerPawn.SetTransformationType(TransformType)
    TransformerPawn.SelectActor(SelectedActor)
    TransformerPawn.SetActorLocation(SelectedActor.Location)
    bGizmoActive = True
    DISABLE COLLISION non-FurnitureSpawned actors
```

### Event Tick — Movement Logic (rút gọn)

```
Branch IsValid(SelectedActor) AND bIsDraggingGizmo:
  GET ActiveMode (BP_FurnitureInputManager)

  Sequence:
    Then 0: ROTATE — accumulate rotation delta from mouse, apply to SelectedActor
    Then 1: MOVE — ray-plane intersection, apply position to SelectedActor
    Then 2: SCALE — apply scale to SelectedActor
```

### Điểm yếu (cần thay đổi cho Sprint 1)

| Vấn đề | Solution |
|---|---|
| SelectedActor là single | Sprint 1: dùng Pivot Actor |
| Apply transform vào 1 actor | Sprint 1: Pivot tính delta → ForEach apply |
| Initial position capture chỉ 1 actor | Sprint 1: capture mảng InitialLocations |

### OnMouseReleased

```
Branch bGizmoActive AND IsValid(SelectedActor) AND bIsDraggingGizmo:
  Switch ActiveMode:
    Rotate → CaptureSnapshot("Rotate")
    Scale  → CaptureSnapshot("Scale")
    Move   → CaptureSnapshot("Move")

SET bIsDraggingGizmo = False
SET ActiveAxis = ""
SET PreviousMousePosition = (0,0)
SET AccumulatedRotation = 0
```

---

## UNDO/REDO SYSTEM (BP_UndoManager)

### Trạng thái hiện tại

```
Variables:
  SnapshotHistory   : Array of S_SceneSnapshot
  CurrentIndex      : Integer
  MaxSteps          : Integer (50)
  SelectedMeshIndex : Integer (-1 = none)
  TempMeshes        : Array of S_FurniturePlacement
  SpawnedActors     : Array of StaticMeshActor
  RestoredBPActor   : BP_FurnitureActor  ← v1.3 fix

Event Dispatcher:
  OnRestoreCompleted(BP_FurnitureActor)
```

### S_SceneSnapshot

```
ActionName        : String
Meshes            : Array of S_FurniturePlacement
SelectedMeshIndex : Integer (-1 = none)   ← SINGLE
ActiveMode        : E_ActiveMode
```

### S_FurniturePlacement

```
MeshPath, DAPath, Location, Rotation, Scale, ActorTag, UniqueID
MaterialPaths : Array of String    ← v1.1
SurfaceType   : Name                ← v1.2 B1
```

### CaptureSnapshot Flow

```
1. Resize history nếu CurrentIndex < Length - 1 (xóa redo stack)
2. CLEAR TempMeshes
3. Get All Actors With Tag("FurnitureSpawned") → ForEach:
   Cast BP_FurnitureActor → Build S_FurniturePlacement → ADD TempMeshes
4. SET SelectedMeshIndex = -1
   Tìm SelectedFurnitureActor trong TempMeshes → SET SelectedMeshIndex
5. Branch Length >= MaxSteps → Remove Index 0 → CurrentIndex - 1
6. Make Snapshot → ADD History → CurrentIndex + 1
```

### RestoreSnapshot Flow

```
1. DeselectMesh (BP_FurnitureInputManager)
2. Destroy all actors tag "FurnitureSpawned"
3. CLEAR SpawnedActors
4. ForEach Snapshot.Meshes:
     Spawn BP_FurnitureActor → SET MeshPath/DAPath → Load mesh
     ADD "FurnitureSpawned" tag
     Restore MaterialPaths (Load Asset Blocking + DMI)
     ADD to SpawnedActors
5. Branch SelectedMeshIndex >= 0:
     True: Restore selection → SET RestoredBPActor → ActivateGizmo
     False: SET RestoredBPActor = None
6. Broadcast OnRestoreCompleted(RestoredBPActor)
```

### Điểm yếu (cần thay đổi)

| Vấn đề | Sprint cần fix |
|---|---|
| SelectedMeshIndex single | Sprint 1: thêm `SelectedMeshIndices : Array of Integer` |
| S_SceneSnapshot không lưu group | Sprint 3: thêm `Groups : Array of S_GroupData` |
| RestoreSnapshot không rebuild group | Sprint 3: thêm bước rebuild groups |
| Snapshot không có Version | Sprint 1: thêm `Version : Integer` |

---

## BP_FurnitureActor

### Trạng thái hiện tại

```
Parent: StaticMeshActor
Interface: EMSActorSaveInterface

Variables (SaveGame):
  MeshPath, DAPath
  MaterialOverrides    : Array of String  ← v1.1
  MaterialParams       : Array of String  ← v1.1 placeholder cho v1.2
  PlacementSurfaceType : Name             ← v1.2 B1

Components:
  FurnitureMesh : StaticMeshComponent (Movable)
```

### Event BeginPlay

```
GET Tags → ADD "FurnitureSpawned" → SET Tags
```

### Event ActorLoaded (EMS callback)

```
Wait For Save or Load Completed → On Completed:
  Branch MeshPath != "":
    True: Load mesh, ADD "FurnitureSpawned" tag
    False: Destroy Actor
```

### Cần thêm cho Sprint 3 (Group)

```
GroupID : String (SaveGame, default "")
  ← Empty string = không thuộc group nào
```

### Cần thêm cho Sprint 6 (Lock)

```
bIsLocked  : Boolean (SaveGame, default False)
CustomName : String (SaveGame, default "")
```

---

## SHARED FUNCTIONS — Tiềm năng tái sử dụng

### SpawnFurnitureCopy (BP_FurnitureInputManager)

```
Input: MeshPath, DAPath, Location, Rotation, Scale,
       MaterialOverrides, SurfaceType

Step 1: Spawn BP_FurnitureActor at (Location, Rotation)
Step 2: Load mesh + SET MeshPath/DAPath/Scale/SurfaceType
Step 3: ADD "FurnitureSpawned" tag
Step 4: Restore materials (Load + Create DMI + Set Material)
Step 5: Select mesh (DeselectMesh, SET SelectedFurnitureActor)
Step 6: Broadcast OnMeshSelected
```

**Đánh giá tái sử dụng:**
- Sprint 5 (Combo Spawn): TÁI SỬ DỤNG được, cần gọi nhiều lần trong ForEach
- Sprint 1 (Multi-select Paste): cần extend để hỗ trợ multi-paste
- Step 5 (Select mesh) cần tách ra: spawn xong KHÔNG tự select trong combo

### NudgeMesh (BP_FurnitureInputManager — B1)

```
Input: Direction (Vector2D)

Branch IsValid(SelectedFurnitureActor):
  T → Branch SnapStep > 0:
    Cast → GET PlacementSurfaceType
    Branch SurfaceType == "Wall":
      T: Wall logic (Up/Down = Z, Left/Right = camera right)
      F: Floor/Ceiling logic (snap yaw 90°)
    Calculate MoveOffset → Add Actor World Offset
    Debounce snapshot timer 0.5s
```

**Đánh giá tái sử dụng:**
- Sprint 1 (Multi-nudge): tách logic tính MoveOffset thành function riêng, ForEach apply

### CopyMesh / PasteMesh / DuplicateMesh (B2)

```
Clipboard: ClipboardMeshPath, ClipboardDAPath,
           ClipboardRotation, ClipboardScale,
           ClipboardMaterialOverrides

CopyMesh: Save selected actor → clipboard
PasteMesh: Trace from cursor → spawn at hit
DuplicateMesh: Spawn at offset = BoxExtent.X*2 + 20
```

**Đánh giá tái sử dụng:**
- Sprint 1: cần đổi clipboard thành `Array of ClipboardData` để hỗ trợ multi-copy
- Sprint 5: tận dụng pattern cho combo spawn

---

## WIDGET ARCHITECTURE

### WBP_MeshControls (Toolbar luôn hiện)

```
Layout:
  [Select] [Move] [Rotate] [Scale] | [Delete] [Info] [Replace]
  [SnapStep] [SnapAngle] [SnapScale]

Logic:
  Branch chọn mesh → enable buttons
  Branch không chọn → disable buttons (visible nhưng faded)
```

**Cần thêm cho Sprint 1:**
- Selection count text "✦ N vật thể"
- Nút "Nhóm" (Sprint 3 mới active)
- Nút "Xóa tất cả"

**Cần thêm cho Sprint 6:**
- 6 nút Align + 2 nút Distribute (chỉ hiện khi >= 2 selected)
- Nút Lock toggle

### WBP_FurnitureInventory

```
Tabs: [Furniture] [Material]
Categories: All | Furniture | Home_Decor | ... | Recent | Favorite

Folder Tree (left column)
Search bar (top)
Grid card (center) — 48 items/page
Pagination
```

**Cần thêm cho Sprint 5:**
- Category mới "🧩 Combo"
- Sub-categories: Phòng khách / Phòng ăn / Phòng ngủ / Tự tạo
- WBP_ComboCard (hoặc reuse WBP_FurnitureCard với badge)

---

## SAVE/LOAD SYSTEM (EMS)

### Hiện tại

```
BP_FurnitureSceneManager (Actor):
  Event Tick → check WBP_SaveGameMenu, bind buttons
  OnSaveButtonClicked: SaveFurnitureScene (EMS Save Game Actors)
  OnLoadButtonClicked:
    1. DeselectMesh
    2. Destroy all actors tag "FurnitureSpawned"
    3. LoadFurnitureScene (EMS Load Game Actors)
```

### Mỗi BP_FurnitureActor implement EMSActorSaveInterface

- Variables SaveGame tự động lưu/load qua EMS
- Event ActorLoaded callback rebuild mesh từ MeshPath

### Cần thay đổi cho Sprint 3 (Group)

EMS không lưu được "logical concepts" như group. Cần:
1. Lưu Groups data riêng vào file SaveGame phụ (tương tự BP_UserPreferencesSave)
2. Hoặc: lưu GroupsJSON như 1 string trong Game Instance / WBP_FurnitureInventory

**Đề xuất:** Sử dụng cùng SaveGame file của EMS, thêm `S_GroupsContainer` actor mang tag "FurnitureGroupsContainer" để EMS save/load.

---

## EVENTS BUS / DISPATCHER ECOSYSTEM

| Event | Dispatched bởi | Bind bởi |
|---|---|---|
| OnMeshSelected(BP_FurnitureActor) | BP_FurnitureInputManager | WBP_FurnitureInventory, WBP_MeshControls |
| OnMeshDeselected() | BP_FurnitureInputManager | WBP_FurnitureInventory |
| OnRestoreCompleted(BP_FurnitureActor) | BP_UndoManager | WBP_FurnitureInventory |

**Cần thêm cho Sprint 1:**
```
OnSelectionChanged(Array of BP_FurnitureActor, Primary : BP_FurnitureActor)
  ← thay thế OnMeshSelected + OnMeshDeselected
  ← fire mỗi khi selection thay đổi (chọn thêm, bỏ chọn, deselect all)
```

**Cần thêm cho Sprint 3:**
```
OnGroupCreated(GroupID : String)
OnGroupDestroyed(GroupID : String)
OnGroupModeChanged(IsEditMode : Boolean, EditingGroupID : String)
```

---

## PERFORMANCE BASELINE

| Metric | Hiện tại | Note |
|---|---|---|
| Scene typical | 20-50 actors | Furniture meshes |
| Event Tick cost | ~0.5ms | Mouse hover + gizmo scale |
| Get All Actors Of Class | ~0.1ms / call | Đang dùng nhiều — pattern OK với scene nhỏ |
| Custom Depth render | ~0.2ms / actor | Outline shader |
| Snapshot capture | ~5ms / call | ForEach 50 actors + struct build |

**Targets sau Sprint 1-7:**

| Metric | Target |
|---|---|
| Multi-select 20 actors | Outline update < 5ms |
| Multi-move 20 actors | Tick cost < 2ms |
| CaptureSnapshot with groups | < 10ms |
| Combo spawn 10 meshes | < 1s (async) |

---

## CRITICAL FILES — Sẽ bị động đến

**HIGH IMPACT (refactor lớn):**
- BP_FurnitureInputManager — toàn bộ Mouse Left Pressed, Nudge, Copy/Paste/Duplicate
- BP_GizmoController — multi-select support
- BP_UndoManager — snapshot with multi-select + groups
- BP_FurnitureActor — thêm GroupID, bIsLocked, CustomName
- S_FurniturePlacement struct — thêm GroupID
- S_SceneSnapshot struct — thêm Version, SelectedMeshIndices, Groups

**MEDIUM IMPACT (thêm features):**
- WBP_MeshControls — selection info bar, Align toolbar, Lock button
- WBP_FurnitureInventory — Combo category, ghost preview multi
- BP_FurnitureUserPrefsManager — recent groups, favorite combos

**LOW IMPACT (thêm widget mới):**
- WBP_BoxSelectOverlay (mới)
- WBP_ContextMenu (mới)
- WBP_SelectionInfoBar (mới)
- WBP_GroupNameDialog (mới)
- WBP_SaveComboDialog (mới)
- WBP_ComboCard (mới)
- WBP_SceneOutliner (mới — Sprint 6)
- WBP_MaterialEditPanel (mới — Sprint 7)

**NOT TOUCHED:**
- BP_FurnitureSceneManager (EMS Save/Load wrapper)
- BP_TransformerPawn (gizmo visual)
- BP_FurnitureUserPrefsManager (recent/favorite — chỉ thêm comboFavorite)
- C++ FurnitureFilterLibrary
- DA_FurnitureItem
