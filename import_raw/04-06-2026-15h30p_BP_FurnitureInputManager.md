# BP_FurnitureInputManager
**Phiên bản:** 1.4 | **Cập nhật:** 04/06/2026 — 15:30 ICT | Actor riêng — input hub + multi-select hub

---

## Mục đích
Tách toàn bộ logic input furniture khỏi BP_FoffPlayerController (shared code).
Chỉ cần spawn actor này vào level là hệ thống hoạt động — không đụng shared code.

**v1.4:** thêm hệ thống **Multi-Select** (Sprint 1 plan_v3). Giữ song song state cũ (`SelectedFurnitureActor`) và state mới (`SelectedActors` + `PrimarySelectedActor`) đến hết Sprint 7 (S7.T9 cleanup).

---

## Variables

### Core (v1.2)
```
SelectedFurnitureActor : BP_FurnitureActor   ← single-select cũ, giữ đến S7.T9
CurrentMeshControls    : WBP_MeshControls
GizmoControllerRef     : BP_GizmoController
TransformerPawnRef     : BP_TransformerPawn
ActiveMode             : E_ActiveMode
LocalWasGizmoActive    : Boolean
DetailPopupRef         : WBP_DetailPopup
bIsReplaceMode         : Boolean
MeshToReplace          : BP_FurnitureActor
```

### Nudge (v1.2 — B1)
```
NudgeSnapshotTimerHandle : Timer Handle      ← debounce CaptureSnapshot 0.5s
NudgeSpeed               : Float (=150.0)     ← cm/s, free mode (SnapStep=0)
```

### Multi-Select (v1.4 — Sprint 1 T1)
```
SelectedActors      : Array of BP_FurnitureActor   ← danh sách đồ đang chọn
PrimarySelectedActor: BP_FurnitureActor            ← đồ chọn cuối (primary, stencil 255)
GizmoPivotActor     : BP_PivotActor                ← pivot vô hình cho multi-gizmo
LastPivotTransform  : Transform                    ← transform pivot lần gần nhất
ClipboardActors     : Array of S_ClipboardEntry    ← clipboard multi (thay 5 var cũ)
```

### Clipboard cũ (v1.2 — B2) — GIỮ tạm, bỏ ở S7.T9
```
ClipboardMeshPath, ClipboardDAPath, ClipboardRotation, ClipboardScale, ClipboardMaterialOverrides
(không còn dùng — CopyMesh/PasteMesh đã chuyển sang ClipboardActors)
```

---

## Event Dispatchers
```
OnMeshDeselected()                                  ← v1.1, fire cuối DeselectMesh
OnMeshSelected(SelectedActor : BP_FurnitureActor)    ← v1.1, fire sau SET SelectedFurnitureActor
OnSelectionChanged(Actors : Array<BP_FurnitureActor>, Primary : BP_FurnitureActor)  ← v1.4 T6
OnSceneChanged(AllActors : Array<BP_FurnitureActor>) ← v1.4 T14 (cho Scene Manager Panel Sprint 6; broadcast thêm sau)
```

---

## S_ClipboardEntry struct (T2)
```
MeshPath          : String
DAPath            : String
RelativeLocation  : Vector    ← vị trí tương đối so với center nhóm (cho paste/duplicate giữ formation)
Rotation          : Rotator
Scale             : Vector
MaterialOverrides : Array of String
SurfaceType       : Name
GroupID           : String    ← cho Sprint 3+
```

---

## MULTI-SELECT FUNCTIONS (v1.4 — T4, T5)

### CalculateCenter(Actors) → Vector (T4)
Tính trung bình vị trí các actor → tâm nhóm.

### SpawnOrUpdatePivot (T4)
```
Guard: LENGTH SelectedActors < 2 → return
CalculateCenter(SelectedActors) → Center
Branch NOT IsValid(GizmoPivotActor): True → Spawn BP_PivotActor → SET GizmoPivotActor
SET Actor Location(GizmoPivotActor, Center)
[T15 sẽ thêm: Set Rotation(0,0,0) + Set Scale 3D(1,1,1)]
SET GizmoPivotActor.AttachedActors = SelectedActors
Call RefreshOffsets(GizmoPivotActor)
```

### DestroyPivot (T4)
IsValid(GizmoPivotActor) → Destroy Actor → SET GizmoPivotActor = None

### DeselectAll (T5)
```
ForEach SelectedActors (Actor):
  Branch IsValid(Actor): True → GET FurnitureMesh → Set Render Custom Depth = False
CLEAR SelectedActors
SET PrimarySelectedActor = None
SET SelectedFurnitureActor = None
DeactivateGizmo
DestroyPivot
Broadcast OnSelectionChanged([], None) + OnMeshDeselected
⚠️ KHÔNG gọi CaptureSnapshot ở đây (infinite loop)
⚠️ IsValid trước mọi Object access (chống crash "pending kill")
```

### SelectSingleActor(Actor) (T5)
DeselectAll → ADD Actor → SelectedActors → SET Primary → UpdateOutlineState → UpdateGizmo → Broadcast OnSelectionChanged

### SelectActors(Actors) (T5)
```
⚠️ Actors là Pass-by-Reference → KHÔNG iterate trực tiếp
SET ActorsCopy = Actors  (bản copy)
ForEach ActorsCopy (Actor):
  Contains(SelectedActors, Actor) → NOT → Branch True → ADD to SelectedActors
ForEach Completed:
  Branch LENGTH > 0 → SET Primary = Last → SET SelectedFurnitureActor
  → UpdateOutlineState → UpdateGizmo → Broadcast OnSelectionChanged
```
**Lưu ý:** caller (Paste/Duplicate/Restore) phải DeselectAll trước khi gọi (SelectedActors rỗng) → vòng Contains không trùng.

### ToggleActor(Actor) (T5, T7)
```
Branch Contains(SelectedActors, Actor):
  True  → Remove from SelectedActors → Set Render Custom Depth=False (clear stencil)
  False → ADD to SelectedActors
SET Primary = (last actor còn lại / Actor vừa thêm)
UpdateOutlineState → UpdateGizmo → Broadcast OnSelectionChanged
→ CaptureSnapshot("Select")   ← T7 deviation: giữ multi-select state cho Undo
```

### UpdateOutlineState (T5)
```
ForEach SelectedActors (Actor):
  IsValid → GET FurnitureMesh → Set Render Custom Depth=True
  Branch Actor == PrimarySelectedActor:
    True  → Set Custom Depth Stencil Value = 255  (primary)
    False → Set Custom Depth Stencil Value = 254  (secondary)
```

### UpdateGizmo (T5)
```
GET LENGTH SelectedActors:
  == 0 → DeactivateGizmo + DestroyPivot
  == 1 → DestroyPivot → ActivateGizmo(SelectedActors[0])
  >= 2 → DeactivateGizmo (TRƯỚC!) → SpawnOrUpdatePivot → ActivateGizmo(GizmoPivotActor) → SetActorTickEnabled(GizmoPivotActor, True)
```
**Deviation:** nhánh >=2 phải DeactivateGizmo trước ActivateGizmo (plan bỏ sót).

---

## Mouse Left Pressed — FULL FLOW (v1.4 refactor T7)
```
Step 0: Set Input Mode Game And UI
Step 1: SET LocalWasGizmoActive = GizmoControllerRef.bGizmoActive
Step 2: GizmoController → OnMousePressed
Step 3: Branch bIsDraggingGizmo == True → True: STOP
Step 4: GetHitResultUnderCursorByChannel (CAMERA) → Hit Actor, ReturnValue
Step 5: Branch ReturnValue == True:
          False → NOT(IsCtrlDown) → DeselectAll → STOP
Step 6: Branch ActorHasTag(Hit Actor, "FurnitureSpawned"):
          False → NOT(IsCtrlDown) → DeselectAll → STOP
Step 7: Branch IsInputKeyDown(Left Ctrl):
          True  → ToggleActor(HitActor as BP_FurnitureActor) → CaptureSnapshot("Select") → STOP
          False → SelectSingleActor(HitActor as BP_FurnitureActor)
                  → (UpdateDetailPopup nếu IsValid CurrentMeshControls)
                  → CaptureSnapshot("Select")
(đã xóa Step 8/9/12 cũ — gộp vào SelectSingleActor/SelectActors)
```

---

## Mouse Left Released
```
GizmoController → OnMouseReleased
[T15 sẽ thêm: CaptureSnapshot khi SelectedActor là Pivot]
```

---

## v1.2 — Keyboard Manipulation (UX Phase 2.1)

### B1 — Arrow Key Nudge (MULTI v1.4 — T10)
**Chi tiết:** `B1_Nudge_Flow.md`
- `NudgeMesh(Direction)` — guard `SelectedActors.LENGTH==0 → return`; direction tính từ `PrimarySelectedActor.PlacementSurfaceType`; **ForEach SelectedActors → Add Actor World Offset**; sau ForEach: CalculateCenter → SetActorLocation(Pivot) → RefreshOffsets (gizmo theo nhóm).
- `CaptureNudgeSnapshot` — debounce 0.5s.
- **Event Tick free mode** — `SnapStep==0 AND SelectedActors.LENGTH>0` → ForEach SelectedActors di chuyển × DeltaTime × NudgeSpeed → cập nhật Pivot.

### B2 — Copy/Paste/Duplicate (MULTI v1.4 — T11)
**Chi tiết:** `B2_CopyPaste_Flow.md`
- `CopyMesh` — CLEAR ClipboardActors → CalculateCenter → ForEach SelectedActors build S_ClipboardEntry (RelativeLocation = ActorLoc - Center) → ADD.
- `PasteMesh` — trace surface → DeselectAll → CLEAR LocalSpawned → ForEach ClipboardActors spawn (actualLoc = PasteCenter + RelativeLocation, bAutoSelect=False) → SelectActors(LocalSpawned) → CaptureSnapshot.
- `DuplicateMesh` — CopyMesh → ForEach SelectedActors tính MaxRightEdge (**phần spawn nối vào COMPLETED, KHÔNG Loop Body**) → DeselectAll → CLEAR LocalSpawned → ForEach ClipboardActors spawn (actualLoc = GroupCenter + DuplicateOffset + RelativeLocation, bAutoSelect=False) → SelectActors(LocalSpawned) → CaptureSnapshot.
- `SpawnFurnitureCopy(MeshPath, DAPath, SpawnLocation, SpawnRotation, SpawnScale, MaterialOverrides, SurfaceType, **bAutoSelect**) → **NewActor**` — spawn + LoadMesh + SetMaterial + Tag + SET SurfaceType. Branch bAutoSelect: True→select+gizmo+broadcast | False→skip. **Return Node phải nối NewActorCopy ở CẢ True và False branch**.

---

## Event BeginPlay
```
Enable Input
SET CurrentMeshControls = None, SET SelectedFurnitureActor = None
Get All Actors Of Class(BP_TransformerPawn) → Get(0) → SET TransformerPawnRef
```

## Event End Play (chống VRAM leak)
```
IsValid(CurrentMeshControls) → Remove from Parent
IsValid(SelectedFurnitureActor) → Set Render Custom Depth = False
ForEach SelectedActors → IsValid → Set Render Custom Depth = False
CLEAR SelectedActors
SET PrimarySelectedActor = None, GizmoPivotActor = None
```

---

## DeselectMesh (Function — single, cũ)
```
Cast SelectedFurnitureActor → GET FurnitureMesh → Set Render Custom Depth = False
SET SelectedFurnitureActor = None → DeactivateGizmo → Broadcast OnMeshDeselected
⚠️ KHÔNG CaptureSnapshot ở đây (infinite loop)
```

---

## Cách BP khác lấy reference
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
```
⚠️ KHÔNG dùng Get Player Controller → Cast BP_FoffPlayerController

---

## Level Blueprint — Spawn Order
```
1. BP_UndoManager   2. BP_FurnitureSceneManager   3. BP_TransformerPawn
4. BP_GizmoController   5. BP_FurnitureInputManager (SET GizmoControllerRef)
6. WBP_MeshControls (SET CurrentMeshControls)   7. CaptureSnapshot("Initial")
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 21/04/2026 | Tạo mới |
| 1.1 | 19/05/2026 | Event Dispatchers OnMeshDeselected + OnMeshSelected |
| 1.2 | 21/05/2026 | UX Phase 2.1: B1 Nudge + B2 Copy/Paste/Duplicate |
| 1.3 | 22/05/2026 | PlacementSurfaceType support |
| 1.4 | 04/06/2026 — 15:30 ICT | **Multi-Select (Sprint 1 T1-T14):** SelectedActors/PrimarySelectedActor/GizmoPivotActor/ClipboardActors vars; OnSelectionChanged + OnSceneChanged dispatchers; CalculateCenter/SpawnOrUpdatePivot/DestroyPivot/DeselectAll/SelectActors/SelectSingleActor/ToggleActor/UpdateOutlineState/UpdateGizmo; Mouse Left Pressed refactor (Ctrl toggle); Multi Nudge/Copy/Paste/Duplicate; SpawnFurnitureCopy +bAutoSelect +NewActor |
