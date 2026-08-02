# 03 — Code Inheritance Strategy

> ⚠️ **[HISTORICAL]** — File này mô tả THIẾT KẾ tại thời điểm viết, KHÔNG phải as-built hiện
> tại. Nhiều quyết định đã bị override ở các sprint sau. Giữ lại để tra "vì sao đã quyết như
> vậy". **As-built hiện tại xem:** `Blueprints/BP_FurnitureInputManager.md` + `Blueprints/BP_UndoManager.md`.

**Mục đích:** Tận dụng tối đa code hiện có, tránh viết lại từ đầu.

---

## NGUYÊN TẮC

### Quy tắc 1 — Pattern Match Trước
Trước khi viết function mới, tìm function tương tự đang hoạt động. Khả năng 80% đã có pattern dùng được.

### Quy tắc 2 — Tách Tham Số Hóa
Nếu function cũ làm việc với 1 actor, tách logic ra thành **helper function nhận actor làm input**. Rồi cả single-mode lẫn multi-mode đều gọi helper.

```
// CŨ:
function NudgeMesh(Direction):
  // logic xử lý SelectedFurnitureActor

// MỚI:
function NudgeMesh(Direction):                          ← entry point, không đổi
  ForEach SelectedActors:
    Call NudgeSingleActor(Actor, Direction)

function NudgeSingleActor(Actor, Direction):            ← helper mới
  // logic giống NudgeMesh cũ, nhưng tham số hóa Actor
```

### Quy tắc 3 — Boolean Flag Khi Cần Switch Behavior
Khi cùng function phải xử lý 2 trường hợp (single vs multi), thêm flag:

```
function CaptureSnapshot(ActionName, bIncludeGroupData : Boolean = True):
  ...
```

### Quy tắc 4 — Mở Rộng Struct Bằng Cách Thêm Field
Không tạo struct mới khi có thể thêm field vào struct cũ. Lý do: tránh thay đổi flow code đọc/ghi struct.

```
// CŨ: S_FurniturePlacement có 7 field
// MỚI: thêm 3 field nữa = 10 field

// Code cũ đọc 7 field đầu vẫn chạy đúng.
// Code mới đọc thêm 3 field mới.
```

---

## INHERITANCE MAP — Từng Function

### A. Selection Logic

#### A1. SelectActors (MỚI) ← kế thừa từ Step 8-9 hiện tại

**Code cũ (Step 8-9 trong Mouse Left Pressed):**
```
Cast HitActor → BP_FurnitureActor → SET SelectedFurnitureActor
Broadcast OnMeshSelected
Cast → GET FurnitureMesh → Set Custom Depth True + Stencil 255
CaptureSnapshot("Select")
```

**Refactor strategy:**
1. Tách Step 8-9 ra thành function `SelectSingleActor(Actor)`
2. Tạo function mới `SelectActors(Array)` gọi `SelectSingleActor` trong ForEach
3. Tạo `ToggleActor(Actor)` cho Ctrl+Click
4. Tạo `DeselectAll` mở rộng từ `DeselectMesh` cũ

**Kế thừa:**
- Cast pattern ✅
- Custom Depth pattern ✅
- Broadcast pattern ✅
- CaptureSnapshot timing ✅

**Cần mới:**
- Logic ADD vs SET vs REMOVE từ array
- Stencil value khác nhau (255 Primary, 254 Secondary)

---

#### A2. DeselectAll ← mở rộng DeselectMesh cũ

**Code cũ:**
```
Cast SelectedFurnitureActor → GET FurnitureMesh → Set Render Custom Depth = False
SET SelectedFurnitureActor = None
DeactivateGizmo
Broadcast OnMeshDeselected
```

**Refactor:**
```
ForEach SelectedActors:
  Cast → GET FurnitureMesh → Set Render Custom Depth = False
CLEAR SelectedActors
SET PrimarySelectedActor = None
SET SelectedFurnitureActor = None  ← deprecated, vẫn set để compat
DeactivateGizmo
Destroy GizmoPivotActor (nếu valid)
Broadcast OnMeshDeselected (deprecated)
Broadcast OnSelectionChanged([], None)
```

**Kế thừa:** ~70% logic, chỉ wrap ForEach.

---

### B. Movement Logic

#### B1. NudgeMesh Multi-select ← extend NudgeMesh cũ

**Code cũ (rút gọn):**
```
NudgeMesh(Direction):
  Branch IsValid(SelectedFurnitureActor):
    Cast → GET PlacementSurfaceType
    Branch SurfaceType == "Wall":
      Wall logic (UpAxis = Z, Right = Camera Right)
    Branch Floor/Ceiling:
      Camera Yaw snap logic
    Calculate MoveOffset
    Add Actor World Offset(SelectedFurnitureActor, MoveOffset)
    Debounce snapshot
```

**Refactor:**
```
NudgeMesh(Direction):
  Branch SelectedActors.Length == 0: return

  ← Tách logic tính MoveOffset thành helper
  CalculateNudgeOffset(Direction, PrimarySelectedActor) → MoveOffset

  ← Apply cho TẤT CẢ
  ForEach SelectedActors:
    Add Actor World Offset(Actor, MoveOffset)

  Debounce snapshot (giữ nguyên)

CalculateNudgeOffset(Direction, ReferenceActor) → Vector:
  ← Toàn bộ logic Wall/Floor/Ceiling cũ
  ← Dùng ReferenceActor.PlacementSurfaceType
  Return MoveOffset
```

**Lý do dùng PrimarySelectedActor làm reference:**
- Nếu multi-select có cả wall + floor mesh, ưu tiên hướng theo Primary
- User thường chọn Primary trước, hướng nudge theo cảm giác Primary

**Kế thừa:** ~90% logic, chỉ wrap ForEach + tách helper.

---

#### B2. Multi-move qua Gizmo ← KHÔNG đổi BP_GizmoController

**Strategy:** Spawn `BP_PivotActor` ở center. Gizmo move Pivot. Pivot tự đồng bộ children.

```
Khi user click chọn 1 actor:
  BP_FurnitureInputManager.UpdateGizmo:
    Length == 1: ActivateGizmo(SelectedActors[0])  ← giống cũ
    Length >= 2: SpawnOrUpdatePivot → ActivateGizmo(PivotActor)
```

**BP_GizmoController không cần thay đổi** — nó vẫn chỉ làm việc với `SelectedActor` single. Chỉ khác là khi multi-select, `SelectedActor` là PivotActor thay vì FurnitureActor.

**Pivot Actor Event Tick logic:**
```
ChildrenSyncTick:
  GET CurrentTransform
  Branch LastSyncedTransform != CurrentTransform:
    ApplyTransformToChildren
    SET LastSyncedTransform = CurrentTransform
```

**Kế thừa:** 100% gizmo logic không đổi. Pivot là layer trung gian.

---

### C. Copy/Paste/Duplicate

#### C1. Multi-Copy ← mở rộng CopyMesh cũ

**Code cũ:**
```
CopyMesh:
  Branch IsValid(SelectedFurnitureActor):
    Cast → SET Clipboard fields (single)
```

**Refactor:**
```
CopyMesh:
  Branch SelectedActors.Length == 0: return
  CLEAR ClipboardActors (array)

  center = CalculateCenter(SelectedActors)

  ForEach SelectedActors:
    Cast → GET MeshPath, DAPath, Rotation, Scale, MaterialOverrides, SurfaceType
    relativeLocation = Actor.Location - center
    Build S_ClipboardEntry
    ADD to ClipboardActors
```

**Kế thừa:**
- Cast + GET fields pattern ✅
- Clipboard storage pattern ✅ (nhưng đổi từ single vars sang array of struct)

---

#### C2. Multi-Paste ← extend PasteMesh + tận dụng SpawnFurnitureCopy

**Code cũ:**
```
PasteMesh:
  Branch ClipboardMeshPath != "":
    Trace from cursor → PasteLocation
    Call SpawnFurnitureCopy(...)
    CaptureSnapshot("Paste")
```

**Refactor:**
```
PasteMesh:
  Branch ClipboardActors.Length == 0: return

  Trace from cursor → PasteLocation (center)
  detect SurfaceType từ HitNormal

  DeselectAll  ← clear current selection
  CLEAR SpawnedFromClipboard array

  ForEach ClipboardActors (entry):
    actualLocation = PasteLocation + entry.relativeLocation
    Call SpawnFurnitureCopy(
      MeshPath = entry.MeshPath, ...,
      Location = actualLocation,
      SurfaceType = detected SurfaceType
    ) → newActor
    ADD newActor to SpawnedFromClipboard

  ← Select tất cả mesh mới
  SelectActors(SpawnedFromClipboard)
  CaptureSnapshot("Paste")
```

**Kế thừa:**
- SpawnFurnitureCopy 100% ✅ (gọi nhiều lần)
- Trace logic ✅
- CaptureSnapshot timing ✅
- DeselectMesh pattern → đổi sang DeselectAll

**Cần mới:**
- ForEach loop spawn
- Track new spawned actors để select sau

---

#### C3. Multi-Duplicate ← extend DuplicateMesh

**Code cũ:**
```
DuplicateMesh:
  GET PlacementSurfaceType
  Call CopyMesh
  Calculate offset = (BoxExtent.X * 2 + 20)
  Call SpawnFurnitureCopy(...)
  CaptureSnapshot("Duplicate")
```

**Refactor:**
```
DuplicateMesh:
  Branch SelectedActors.Length == 0: return

  Call CopyMesh  ← fill ClipboardActors

  ← Tính bounds chung của toàn bộ selection
  bounds = CalculateCombinedBounds(SelectedActors)
  offset = (bounds.X * 2 + 20, 0, 0)
  duplicateLocation = bounds.Center + offset

  DeselectAll
  CLEAR SpawnedFromDuplicate

  ForEach ClipboardActors (entry):
    actualLocation = duplicateLocation + entry.relativeLocation
    Call SpawnFurnitureCopy(..., Location = actualLocation) → newActor
    ADD newActor to SpawnedFromDuplicate

  SelectActors(SpawnedFromDuplicate)
  CaptureSnapshot("Duplicate")
```

**Kế thừa:** ~80%, chỉ thay tính location + ForEach.

---

### D. Snapshot / Undo / Redo

#### D1. CaptureSnapshot ← mở rộng struct

**Code cũ:**
```
CaptureSnapshot(ActionName):
  ForEach actors → Build S_FurniturePlacement → ADD TempMeshes
  Tìm SelectedFurnitureActor index → SET SelectedMeshIndex
  Make Snapshot → ADD History
```

**Refactor (Sprint 1):**
```
CaptureSnapshot(ActionName):
  ForEach actors → Build S_FurniturePlacement → ADD TempMeshes

  ← Thay vì 1 index, lưu mảng indices
  CLEAR TempSelectedIndices
  ForEach SelectedActors (selectedActor):
    ForEach TempMeshes (Index, mesh):
      Branch mesh.UniqueID == GetDisplayName(selectedActor):
        ADD Index to TempSelectedIndices

  Make S_SceneSnapshot:
    Version = 2
    Meshes = TempMeshes
    SelectedMeshIndices = TempSelectedIndices  ← MỚI
    Groups = (empty Sprint 1)
    ActiveMode = ...
    EditingGroupID = ""

  ADD to History
```

**Refactor (Sprint 3 — thêm Groups):**
```
CaptureSnapshot:
  ... (giữ nguyên)

  ← Thêm Groups
  Make S_SceneSnapshot:
    Version = 3
    Groups = BP_FurnitureInputManager.Groups   ← copy current state
    EditingGroupID = BP_FurnitureInputManager.CurrentEditingGroupID
    ...
```

**Kế thừa:** ~85% — chỉ thay SelectedMeshIndex single → array, và thêm Groups field.

---

#### D2. RestoreSnapshot ← extend

**Code cũ:**
```
RestoreSnapshot(Index):
  DeselectMesh
  Destroy all actors tag "FurnitureSpawned"
  ForEach Snapshot.Meshes: Spawn + restore materials
  Branch SelectedMeshIndex >= 0:
    Restore selection → ActivateGizmo
  Broadcast OnRestoreCompleted(RestoredBPActor)
```

**Refactor (Sprint 1):**
```
RestoreSnapshot(Index):
  DeselectAll  ← thay DeselectMesh
  Destroy all actors tag "FurnitureSpawned"
  CLEAR SpawnedActors

  ForEach Snapshot.Meshes:
    Spawn + restore (giữ nguyên)
    ADD to SpawnedActors

  ← Restore multi-select
  Branch Snapshot.Version >= 2 AND SelectedMeshIndices.Length > 0:
    T:
      CLEAR TempRestoredActors
      ForEach SelectedMeshIndices (idx):
        actor = SpawnedActors[idx]
        Cast BP_FurnitureActor → ADD to TempRestoredActors
      Call SelectActors(TempRestoredActors)
      SET RestoredBPActor = PrimarySelectedActor
    F (Version 1 fallback):
      Branch SelectedMeshIndex >= 0 (old field):
        SET RestoredBPActor = SpawnedActors[SelectedMeshIndex]
        Call SelectSingleActor(RestoredBPActor)

  Broadcast OnRestoreCompleted(RestoredBPActor)
```

**Refactor (Sprint 3 — thêm Groups):**
```
RestoreSnapshot:
  ... (spawn actors, giữ nguyên)

  ← Restore GroupID trên actors
  ForEach Snapshot.Meshes (mesh):
    actor = SpawnedActors[index]
    SET actor.GroupID = mesh.GroupID

  ← Restore Groups data
  Branch Snapshot.Version >= 3:
    CLEAR BP_FurnitureInputManager.Groups
    ForEach Snapshot.Groups: ADD to InputManager.Groups
    SET InputManager.CurrentEditingGroupID = Snapshot.EditingGroupID
```

**Kế thừa:** ~75% — thêm Groups restore + multi-select restore.

---

### E. Material System

#### E1. Material Apply Multi ← mở rộng ApplyMaterial

**Code cũ (Sprint 1.1):**
```
ApplyMaterial(RowName):
  Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0:
    GetDataTableRow → SET PendingRowName, PendingMaterialPath
    Call LoadAndApplyMaterial (async)

LoadAndApplyMaterial:
  Async Load → CreateDMI → SetMaterial
  → SET MaterialOverrides[SlotIndex] = path
  → Debounce CaptureSnapshot
```

**Refactor (Sprint 7 — Multi-apply):**
```
ApplyMaterial(RowName):
  Branch SelectedActors.Length == 0 OR SelectedSlotIndex < 0: return
  GetDataTableRow → SET PendingRowName, PendingMaterialPath
  Call LoadAndApplyMaterial_Multi (async)

LoadAndApplyMaterial_Multi:
  Async Load PendingMaterialPath → MI_Source
  ForEach SelectedActors (Actor):
    GET FurnitureMesh
    Branch SelectedSlotIndex < GetNumMaterials:
      CreateDMI(FurnitureMesh, MI_Source, SelectedSlotIndex) → MID
      SetMaterial(FurnitureMesh, SelectedSlotIndex, MID)
      SetArrayElem(Actor.MaterialOverrides, SlotIndex, PendingMaterialPath)
  Debounce CaptureSnapshot("ChangeMaterial")
```

**Kế thừa:** ~80% — wrap ForEach quanh DMI creation, async load chỉ 1 lần.

---

#### E2. Material Param Edit (Sprint 7) ← tận dụng MID đã có

**MID đã được create ở Sprint 1.1 khi user apply material.** Param edit chỉ cần Set Parameter trên MID có sẵn.

```
SetMaterialColor(Color):
  Branch SelectedActors.Length == 0: return
  ForEach SelectedActors:
    GET FurnitureMesh → Get Material(SelectedSlotIndex) → Cast MID
    Branch IsValid(MID):
      Set Vector Parameter Value("Tint", Color)
  Debounce CaptureSnapshot("EditMaterialColor")
```

**Tương tự cho Roughness, Metallic:**
```
SetMaterialRoughness(Value):
  ForEach SelectedActors:
    GET FurnitureMesh → Get Material(SlotIndex) → Cast MID:
      Set Scalar Parameter Value("Roughness", Value)
```

**Lưu MaterialParams:**
```
SetMaterialParamsJSON(Actor, SlotIndex, ParamsJSON):
  SetArrayElem(Actor.MaterialParams, SlotIndex, ParamsJSON)
```

**Kế thừa:**
- MID đã có (Sprint 1.1) ✅
- MaterialParams field đã có placeholder ✅
- Async load pattern ✅

---

### F. Spawn Functions

#### F1. SpawnFurnitureCopy (giữ nguyên hoàn toàn — Sprint 5 dùng)

**Code cũ là perfect candidate cho reuse:**
- Có đầy đủ params (MeshPath, DAPath, Location, Rotation, Scale, Materials, Surface)
- Đã handle DMI creation
- Đã handle tag adding
- Đã handle selection sau spawn

**Combo Spawn (Sprint 5):**
```
SpawnCombo(RowName, WorldLocation):
  GetDataTableRow → comboData
  Parse JSON → meshes array, groups array

  newGroupIDMap = {}
  ForEach groups: newGroupIDMap[oldGroupID] = "g_" + GenerateUUID()

  DeselectAll
  CLEAR SpawnedFromCombo

  ForEach meshes (mesh):
    actualLocation = WorldLocation + mesh.relativeLocation
    Call SpawnFurnitureCopy(
      MeshPath = mesh.meshPath,
      DAPath = mesh.dapath,
      Location = actualLocation,
      Rotation = mesh.rotation,
      Scale = mesh.scale,
      MaterialOverrides = mesh.materialOverrides,
      SurfaceType = mesh.surfaceType
    ) → newActor

    ← Override default selection of SpawnFurnitureCopy (multi-select sẽ select sau)
    DeselectActor(newActor)  ← bug: SpawnFurnitureCopy tự select cuối cùng

    ← Map old GroupID → new GroupID
    Branch mesh.GroupID != "":
      SET newActor.GroupID = newGroupIDMap[mesh.GroupID]

    ADD to SpawnedFromCombo

  ForEach groups (group):
    new_group = S_GroupData{
      GroupID: newGroupIDMap[group.GroupID],
      GroupName: group.GroupName,
      ParentGroupID: newGroupIDMap[group.ParentGroupID] (or ""),
      bIsLocked: False
    }
    ADD to BP_FurnitureInputManager.Groups

  SelectActors(SpawnedFromCombo)
  CaptureSnapshot("SpawnCombo")
```

**Issue cần fix:** SpawnFurnitureCopy hiện tại tự select actor cuối. Cần thêm parameter `bAutoSelect` (default True để backward compat, False khi gọi trong loop).

**Refactor SpawnFurnitureCopy:**
```
SpawnFurnitureCopy(..., bAutoSelect : Boolean = True):
  Step 1-4: spawn + setup (giữ nguyên)
  Step 5: Branch bAutoSelect:
    T → DeselectMesh, SET SelectedFurnitureActor, SetCustomDepth, ActivateGizmo
    F → (skip selection)
  Step 6: Branch bAutoSelect:
    T → Broadcast OnMeshSelected
    F → (skip broadcast)
```

**Kế thừa:** 100% — chỉ thêm 1 boolean parameter.

---

## INHERITANCE SUMMARY

| Component | Tái sử dụng (%) | Thay đổi mới (%) |
|---|---|---|
| Mouse Left Pressed flow | 60% | 40% (Ctrl logic + Group click) |
| DeselectMesh → DeselectAll | 70% | 30% (ForEach + Pivot destroy) |
| Gizmo logic (BP_GizmoController) | 100% | 0% (Pivot là layer trung gian) |
| NudgeMesh | 90% | 10% (ForEach wrap + Calculate helper) |
| CopyMesh | 60% | 40% (Array of struct) |
| PasteMesh | 75% | 25% (ForEach SpawnFurnitureCopy) |
| DuplicateMesh | 80% | 20% (Combined bounds) |
| CaptureSnapshot | 85% | 15% (Indices array + Groups) |
| RestoreSnapshot | 75% | 25% (Multi-select + Groups restore) |
| ApplyMaterial | 80% | 20% (ForEach DMI) |
| SpawnFurnitureCopy | 95% | 5% (bAutoSelect param) |

**Trung bình: ~80% kế thừa, ~20% mới.**

---

## ANTI-PATTERNS — TRÁNH LÀM

### 1. ❌ Tạo function "MoveMulti" tách biệt với "MoveSingle"
Sai: 2 function khác nhau → bug fix 1 chỗ phải nhớ fix chỗ kia.
Đúng: 1 function `Move` xử lý array `SelectedActors`. Single = array length 1.

### 2. ❌ Lưu Group là Actor hierarchy AttachToActor
Sai: AttachToActor làm transforms phụ thuộc parent. Save/Load phức tạp.
Đúng: Logical grouping qua GroupID string. Transform luôn world-relative.

### 3. ❌ Modify RuntimeTransformer plugin để hỗ trợ multi
Sai: Plugin third-party, modify khó maintain.
Đúng: Pivot Actor pattern — plugin vẫn làm việc với 1 actor.

### 4. ❌ Multi-Outline bằng cách thay Stencil = 255 cho tất cả
Sai: Không phân biệt được Primary vs Secondary.
Đúng: 255 cho Primary, 254 cho Secondary. Material outline check 2 values.

### 5. ❌ EMS save groups bằng cách iterate qua tất cả actors mỗi save
Sai: Performance kém, code phức tạp.
Đúng: 1 BP_GroupsContainer actor mang Groups data. EMS save 1 actor = save groups.

### 6. ❌ Snapshot lưu reference đến actor
Sai: Hard ref → snapshot giữ chuỗi actor → memory leak.
Đúng: Snapshot lưu UniqueID (string). Restore tìm actor theo UniqueID.
