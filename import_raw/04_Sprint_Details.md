# 04 — Sprint Details (chi tiết từng task)
**Mục đích:** Phân rã từng sprint thành tasks nhỏ, mỗi task có thể làm trong 1-2 giờ.

---

## SPRINT 1 — MULTI-SELECT CORE (5-7 ngày, 15 tasks)

> ⚠️ **CHIẾN LƯỢC ƯU TIÊN MOVE-FIRST (quan trọng — đọc trước):**
> Toán Pivot Actor cho **Rotate/Scale** là phần KHÓ NHẤT sprint (xoay nhóm quanh pivot khi mỗi đồ giữ rotation riêng → dễ sinh shear, sai world/local).
> **Thứ tự làm đúng:**
> 1. Vertical slice: multi-select + **chỉ MOVE** (delta translation đơn giản: `NewLocation = OldLocation + DeltaMove`) → ship được ngay, validate Pivot cơ bản
> 2. Hoàn thiện T1-T14 cho Move
> 3. **Rotate/Scale = task riêng cuối sprint (S1.T15)**, hoặc dời sang sau nếu hết thời gian
> KHÔNG để toán Pivot rotate/scale block cả sprint. Move-only multi-select đã đủ giá trị demo.

### S1.T1 — Thêm variables vào BP_FurnitureInputManager (15 phút)
**Files:** BP_FurnitureInputManager
**Variables:**
```
SelectedActors        : Array of BP_FurnitureActor    ← MỚI
PrimarySelectedActor  : BP_FurnitureActor              ← MỚI
GizmoPivotActor       : BP_PivotActor                  ← MỚI (None default)
LastPivotTransform    : Transform                      ← MỚI (cho Tick sync)
ClipboardActors       : Array of S_ClipboardEntry      ← MỚI (thay 5 vars cũ)
```
**Giữ nguyên:** `SelectedFurnitureActor` (deprecated, đồng bộ với Primary)

**Test:** Compile pass.

---

### S1.T2 — Tạo S_ClipboardEntry struct (10 phút)
**Files:** Data
**Struct mới:**
```
S_ClipboardEntry:
  MeshPath          : String
  DAPath            : String
  RelativeLocation  : Vector
  Rotation          : Rotator
  Scale             : Vector
  MaterialOverrides : Array of String
  SurfaceType       : Name
```

---

### S1.T3 — Tạo BP_PivotActor (1 giờ)
**Files:** BP_PivotActor (mới)
**Parent:** Actor (không phải StaticMeshActor)
**Components:**
- DefaultSceneRoot (chỉ scene component, không visual)

**Variables:**
```
AttachedActors       : Array of BP_FurnitureActor
InitialOffsets       : Array of Vector
InitialChildScales   : Array of Vector
InitialChildRotations: Array of Rotator
LastPivotTransform   : Transform
```

**Event BeginPlay:**
```
GET Tags → ADD "FurniturePivot" → SET Tags
SET Mobility = Movable
```

**Function `RefreshOffsets`:**
```
CLEAR InitialOffsets, InitialChildScales, InitialChildRotations
ForEach AttachedActors:
  ADD (Actor.Location - Self.Location) to InitialOffsets
  ADD Actor.Scale3D to InitialChildScales
  ADD Actor.Rotation to InitialChildRotations
SET LastPivotTransform = GetActorTransform
```

**Function `ApplyTransformToChildren`:**

> ⚠️ **MOVE-FIRST:** Bản đầu chỉ làm MOVE (đơn giản, an toàn). Rotate/Scale làm ở S1.T15 sau.

**Bản MOVE-ONLY (làm trước):**
```
deltaMove = Self.Location - LastPivotTransform.Location
ForEach AttachedActors:
  Actor.SetActorLocation(Actor.GetActorLocation + deltaMove)
```
Đơn giản, không có toán xoay/scale → không sinh shear, không sai world/local.

**Bản ĐẦY ĐỦ (Rotate/Scale — để dành S1.T15):**
```
deltaRotation = Self.Rotation - InitialPivotRotation
scaleRatio    = Self.Scale3D / InitialPivotScale   ← component-wise, cẩn thận non-uniform

ForEach AttachedActors (Index, Actor):
  ← Xoay offset: dùng RotateVector của deltaRotation lên offset gốc
  rotatedOffset = deltaRotation.RotateVector(InitialOffsets[Index])
  scaledOffset  = rotatedOffset * scaleRatio
  newLocation   = Self.Location + scaledOffset
  newRotation   = InitialChildRotations[Index] + deltaRotation  ← Combine Rotators
  newScale      = InitialChildScales[Index] * scaleRatio

  Actor.SetActorLocation(newLocation)
  Actor.SetActorRotation(newRotation)
  Actor.SetActorScale3D(newScale)
```
⚠️ Test kỹ với: (a) non-uniform scale, (b) đồ đã xoay sẵn trước khi group, (c) rotate + scale cùng lúc.
Node đúng: `Rotator → Rotate Vector` (không có "RotateBy"). Combine rotation: `Combine Rotators` hoặc cộng trực tiếp (cẩn thận gimbal).
```
deltaRotation = Self.Rotation - InitialPivotRotation
scaleRatio    = Self.Scale / InitialPivotScale

ForEach AttachedActors (Index, Actor):
  newOffset = InitialOffsets[Index]
              → RotateBy(deltaRotation)
              → Multiply(scaleRatio)
  newLocation = Self.Location + newOffset
  newRotation = InitialChildRotations[Index] + deltaRotation
  newScale = InitialChildScales[Index] * scaleRatio

  Actor.SetActorLocation(newLocation)
  Actor.SetActorRotation(newRotation)
  Actor.SetActorScale3D(newScale)
```

**Event Tick:**
```
Branch IsValid(AttachedActors[0]) AND GetActorTransform != LastPivotTransform:
  T → ApplyTransformToChildren
       SET LastPivotTransform = GetActorTransform
```

**Test:** Spawn pivot, move/rotate → children theo đúng.

---

### S1.T4 — Function SpawnOrUpdatePivot trong BP_FurnitureInputManager (45 phút)
**Files:** BP_FurnitureInputManager

```
Function SpawnOrUpdatePivot:
  Branch SelectedActors.Length < 2: return

  center = CalculateCenter(SelectedActors)

  Branch NOT IsValid(GizmoPivotActor):
    T → Spawn BP_PivotActor at center → SET GizmoPivotActor
  Branch IsValid(GizmoPivotActor):
    SET GizmoPivotActor.Location = center
    SET GizmoPivotActor.Rotation = (0,0,0)
    SET GizmoPivotActor.Scale = (1,1,1)
    SET GizmoPivotActor.AttachedActors = SelectedActors
    Call GizmoPivotActor.RefreshOffsets

Function CalculateCenter(Actors) → Vector:
  Sum = (0,0,0)
  ForEach Actors: Sum += Actor.GetActorLocation
  Return Sum / Length

Function DestroyPivot:
  Branch IsValid(GizmoPivotActor):
    Destroy Actor(GizmoPivotActor)
    SET GizmoPivotActor = None
```

---

### S1.T5 — Helper Functions: Select/Deselect (1 giờ)
**Files:** BP_FurnitureInputManager

```
Function SelectSingleActor(Actor : BP_FurnitureActor):
  Call DeselectAll  ← clear hết cũ
  ADD Actor to SelectedActors
  SET PrimarySelectedActor = Actor
  SET SelectedFurnitureActor = Actor  ← compat
  Call UpdateOutlineState
  Call UpdateGizmo
  Broadcast OnSelectionChanged(SelectedActors, PrimarySelectedActor)
  Broadcast OnMeshSelected(Actor)  ← compat

Function ToggleActor(Actor : BP_FurnitureActor):
  Branch SelectedActors.Contains(Actor):
    T → SelectedActors.Remove(Actor)
        Branch SelectedActors.Length > 0:
          T → SET PrimarySelectedActor = SelectedActors.Last
          F → SET PrimarySelectedActor = None, SET SelectedFurnitureActor = None
    F → ADD Actor to SelectedActors
        SET PrimarySelectedActor = Actor
        SET SelectedFurnitureActor = Actor
  Call UpdateOutlineState
  Call UpdateGizmo
  Broadcast OnSelectionChanged

Function SelectActors(Actors : Array of BP_FurnitureActor):
  ForEach Actors (Actor):
    Branch NOT SelectedActors.Contains(Actor):
      ADD Actor to SelectedActors
  Branch Actors.Length > 0:
    SET PrimarySelectedActor = Actors.Last
    SET SelectedFurnitureActor = Actors.Last
  Call UpdateOutlineState
  Call UpdateGizmo
  Broadcast OnSelectionChanged

Function DeselectAll:
  ForEach SelectedActors (Actor):
    Cast → GET FurnitureMesh → Set Render Custom Depth = False
  CLEAR SelectedActors
  SET PrimarySelectedActor = None
  SET SelectedFurnitureActor = None
  DeactivateGizmo
  Call DestroyPivot
  Broadcast OnSelectionChanged([], None)
  Broadcast OnMeshDeselected  ← compat

Function UpdateOutlineState:
  ForEach SelectedActors (Actor):
    Cast → GET FurnitureMesh:
      Set Render Custom Depth = True
      Branch Actor == PrimarySelectedActor:
        T → Set Custom Depth Stencil = 255
        F → Set Custom Depth Stencil = 254

Function UpdateGizmo:
  Branch SelectedActors.Length:
    == 0 → DeactivateGizmo, DestroyPivot
    == 1 → DestroyPivot, ActivateGizmo on SelectedActors[0]
    >= 2 → Call SpawnOrUpdatePivot
            ActivateGizmo on GizmoPivotActor
```

**Test:** Compile pass. Đừng test runtime — chưa nối vào Mouse Left Pressed.

---

### S1.T6 — Event Dispatcher OnSelectionChanged (10 phút)
**Files:** BP_FurnitureInputManager

```
Event Dispatcher mới:
  OnSelectionChanged(
    Actors  : Array of BP_FurnitureActor,
    Primary : BP_FurnitureActor
  )
```

**Test:** Compile.

---

### S1.T7 — Refactor Mouse Left Pressed cho Multi-select (2 giờ)
**Files:** BP_FurnitureInputManager

⚠️ **Đây là task khó nhất Sprint 1.** Làm cẩn thận.

**Logic mới:**
```
Step 0-4: giữ nguyên (Input Mode + Hit Trace)

Step 5: Branch bHit == False:
  T:
    Branch IsCtrlDown:
      F → DeselectAll + CaptureSnapshot("Deselect") → STOP
      T → STOP (giữ selection)

Step 6: Branch HasTag("FurnitureSpawned") == False:
  T:
    Branch IsCtrlDown:
      F → DeselectAll → STOP
      T → STOP

Step 7: ← MỚI: handle Ctrl + Click
  Branch IsCtrlDown:
    T → Cast HitActor → ToggleActor → STOP   (chỉ toggle, không CaptureSnapshot)
    F → tiếp tục
  Cast HitActor → SelectSingleActor

Step 8-9: ← KHÔNG cần nữa, logic chuyển vào SelectSingleActor

Step 10: CaptureSnapshot("Select")

Step 11: Branch IsValid(CurrentMeshControls):
  Cast → Update WBP_MeshControls
```

**Cách lấy Ctrl state:**
```
Get Player Controller → Is Input Key Down(Left Control)
```

**Test:**
- Click 1 đồ → outline hiện
- Ctrl+Click đồ khác → 2 outline hiện
- Ctrl+Click đồ đầu → outline tắt (đồ đầu)
- Click đồ thứ 3 (không Ctrl) → chỉ đồ thứ 3 outline

---

### S1.T8 — Update WBP_MeshControls cho Multi-select (1 giờ)
**Files:** WBP_MeshControls

**Bind OnSelectionChanged event:**
```
Event Construct (thêm):
  Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
  Bind OnSelectionChanged → OnSelectionChangedHandler

Custom Event OnSelectionChangedHandler(Actors, Primary):
  Branch Actors.Length:
    == 0 → Hide / fade buttons
    == 1 → Enable buttons (giống cũ)
    >= 2 → Enable buttons, hiện text "✦ N vật thể"
  Update ET_SelectionCount text
```

**BTN_Delete update:**
```
Branch SelectedActors.Length:
  == 0 → return
  == 1 → Single delete (giống cũ)
  >= 2 → Branch Length > 3:
            T → Show confirmation dialog "Xóa N vật thể?"
            F → Direct delete

  Multi-delete logic:
    ForEach SelectedActors (Actor):
      Destroy Actor
    CLEAR SelectedActors
    SET Primary = None
    CaptureSnapshot("DeleteMulti")
```

**Hidden Info/Replace khi multi-select:**
```
Branch Actors.Length > 1:
  BTN_Info: Set Visibility = Hidden
  BTN_Replace: Set Visibility = Hidden
F → Visible (giống cũ)
```

**Test:** Multi-select → delete 5 đồ → ok. Confirmation dialog hiện.

---

### S1.T9 — Tạo S_FurnitureSelectionChangedPayload (5 phút)

(Bỏ qua nếu Event Dispatcher đã nhận Array trực tiếp.)

---

### S1.T10 — Multi-Nudge (1.5 giờ)
**Files:** BP_FurnitureInputManager

**Refactor NudgeMesh:**
```
Function NudgeMesh(Direction : Vector2D):
  Branch SelectedActors.Length == 0: return
  Branch SnapStep > 0:
    T:
      MoveOffset = CalculateNudgeOffset(Direction, PrimarySelectedActor)
      ForEach SelectedActors (Actor):
        Add Actor World Offset(Actor, MoveOffset, Sweep=False)
      ← Debounce snapshot
      Clear Timer (NudgeSnapshotTimerHandle)
      Set Timer("CaptureNudgeSnapshot", 0.5, Looping=False)

Function CalculateNudgeOffset(Direction, ReferenceActor) → Vector:
  Cast ReferenceActor → GET PlacementSurfaceType → SurfaceType
  Branch SurfaceType == "Wall":
    T:
      UpAxis = (0, 0, 1)
      Camera Yaw → snap 90 → SnappedRight
      MoveOffset = (SnappedRight × Direction.X + UpAxis × Direction.Y) × SnapStep
    F:
      Camera Yaw → snap 90 → SnappedForward, SnappedRight
      MoveOffset = (SnappedRight × Direction.X + SnappedForward × Direction.Y) × SnapStep
  Return MoveOffset
```

**Tick free mode (cuối Tick hiện tại):**
```
Branch SnapStep == 0 AND SelectedActors.Length > 0:
  bRight, bLeft, bUp, bDown = Is Input Key Down(...)
  Branch any key down:
    DirX = Select(bRight, 1, 0) + Select(bLeft, -1, 0)
    DirY = Select(bUp, 1, 0) + Select(bDown, -1, 0)
    MoveOffset = CalculateNudgeOffsetFree(DirX, DirY, PrimarySelectedActor, DeltaTime)
    ForEach SelectedActors:
      Add Actor World Offset(Actor, MoveOffset)
    Debounce snapshot
```

**Test:** Multi-select 5 đồ → arrow key → tất cả move cùng hướng đúng.

---

### S1.T11 — Multi-Copy/Paste/Duplicate (2 giờ)
**Files:** BP_FurnitureInputManager

**Refactor CopyMesh:**
```
Function CopyMesh:
  Branch SelectedActors.Length == 0: return
  CLEAR ClipboardActors
  center = CalculateCenter(SelectedActors)
  ForEach SelectedActors (Actor):
    Cast → GET MeshPath, DAPath, Rotation, Scale, MaterialOverrides, SurfaceType
    relLocation = Actor.Location - center
    Build S_ClipboardEntry → ADD to ClipboardActors
```

**Refactor PasteMesh:**
```
Function PasteMesh:
  Branch ClipboardActors.Length == 0: return

  ← Trace cursor → world
  Get Player Controller → Convert Mouse Location To World Space
  Line Trace → bHit, HitLocation, HitNormal
  Branch bHit:
    T → PasteCenter = HitLocation
    F → PasteCenter = Camera + Forward × 300

  ← Detect surface
  Branch HitNormal.Z > 0.5: PasteSurface = "Floor"
  ElseIf HitNormal.Z < -0.5: PasteSurface = "Ceiling"
  Else: PasteSurface = "Wall"

  ← Clear selection
  Call DeselectAll
  CLEAR LocalSpawned

  ForEach ClipboardActors (entry):
    actualLocation = PasteCenter + entry.RelativeLocation
    Call SpawnFurnitureCopy(
      MeshPath = entry.MeshPath,
      DAPath = entry.DAPath,
      Location = actualLocation,
      Rotation = entry.Rotation,
      Scale = entry.Scale,
      MaterialOverrides = entry.MaterialOverrides,
      SurfaceType = PasteSurface,
      bAutoSelect = False     ← KHÔNG select trong loop
    ) → newActor
    ADD newActor to LocalSpawned

  Call SelectActors(LocalSpawned)
  CaptureSnapshot("PasteMulti")
```

**Refactor DuplicateMesh:**
```
Function DuplicateMesh:
  Branch SelectedActors.Length == 0: return

  Call CopyMesh  ← fill ClipboardActors

  ← Calculate combined bounds offset
  bounds = CalculateCombinedBounds(SelectedActors)
  offset = (bounds.BoxExtent.X * 2 + 20, 0, 0)

  DeselectAll
  CLEAR LocalSpawned

  ForEach ClipboardActors (entry):
    actualLocation = (bounds.Center + offset) + entry.RelativeLocation
    Call SpawnFurnitureCopy(..., bAutoSelect = False) → newActor
    ADD to LocalSpawned

  SelectActors(LocalSpawned)
  CaptureSnapshot("DuplicateMulti")
```

**Refactor SpawnFurnitureCopy (thêm param bAutoSelect):**
```
Input: ..., bAutoSelect : Boolean = True

Step 1-4: giữ nguyên
Step 5: Branch bAutoSelect:
  T → DeselectMesh, SET SelectedFurnitureActor = newActor, SetCustomDepth, ActivateGizmo
  F → (skip)
Step 6: Branch bAutoSelect:
  T → Broadcast OnMeshSelected(newActor)
  F → (skip)
```

**Test:**
- Multi-select 3 đồ → Ctrl+C → Ctrl+V → 3 đồ mới spawn ở vị trí cursor
- Ctrl+D → 3 đồ nhân đôi cạnh nhóm gốc

---

### S1.T12 — Multi-Snapshot (S_SceneSnapshot mở rộng) (2 giờ)
**Files:** Data, BP_UndoManager

**S_SceneSnapshot thêm field:**
```
Version             : Integer (= 2)
SelectedMeshIndices : Array of Integer   ← MỚI
```
Giữ `SelectedMeshIndex` field để load snapshot cũ (Version 1).

**Refactor CaptureSnapshot:**
```
... (Build TempMeshes giữ nguyên)

CLEAR TempSelectedIndices
Get All Actors Of Class(BP_FurnitureInputManager) → Cast:
  ForEach SelectedActors (selectedActor):
    ForEach TempMeshes (Index, mesh):
      Branch mesh.UniqueID == GetDisplayName(selectedActor):
        ADD Index to TempSelectedIndices
        Break inner

← Cho compat với Version 1: vẫn set SelectedMeshIndex
SET TempSelectedMeshIndex = -1
Branch TempSelectedIndices.Length > 0:
  SET TempSelectedMeshIndex = TempSelectedIndices[0]

Make Snapshot:
  Version = 2
  Meshes = TempMeshes
  SelectedMeshIndices = TempSelectedIndices
  SelectedMeshIndex = TempSelectedMeshIndex  ← compat
  ActiveMode = ...
ADD to History
```

**Refactor RestoreSnapshot:**
```
... (spawn actors giữ nguyên)

← Multi-select restore
Branch Snapshot.Version >= 2:
  T:
    CLEAR TempRestoredActors
    ForEach Snapshot.SelectedMeshIndices (idx):
      actor = SpawnedActors[idx]
      Cast BP_FurnitureActor → ADD to TempRestoredActors
    Branch TempRestoredActors.Length > 0:
      Call SelectActors(TempRestoredActors) on BP_FurnitureInputManager
      SET RestoredBPActor = PrimarySelectedActor
    Else: SET RestoredBPActor = None
  F (Version 1 fallback):
    Branch SelectedMeshIndex >= 0:
      RestoredActor = SpawnedActors[SelectedMeshIndex]
      Cast → SelectSingleActor → SET RestoredBPActor
    Else: SET RestoredBPActor = None

Broadcast OnRestoreCompleted(RestoredBPActor)
```

**Test:**
- Multi-select 4 đồ → Move → Undo → 4 đồ về vị trí cũ
- Multi-select 4 đồ → Delete → Undo → 4 đồ spawn lại + reselected
- Load save cũ → vẫn hoạt động (Version 1 fallback)

---

### S1.T13 — Ctrl+A Select All (30 phút)
**Files:** LM_FurnitureInput, BP_FoffPlayerController, BP_FurnitureInputManager

**Input Action:**
```
IA_SelectAll  (Boolean)

LM_FurnitureInput mapping:
  Key: A, Trigger: Chord IA_Ctrl + Pressed
  Key: A, Trigger: (rỗng) — consume block
```

**BP_FoffPlayerController route:**
```
IA_SelectAll (Started):
  GET BP_FurnitureInputManager → Call SelectAllActors
```

**BP_FurnitureInputManager Function:**
```
Function SelectAllActors:
  Get All Actors With Tag("FurnitureSpawned") → AllActors
  ← Convert to BP_FurnitureActor array
  CLEAR LocalActors
  ForEach AllActors:
    Cast BP_FurnitureActor → IsValid → ADD to LocalActors
  Call SelectActors(LocalActors)
  CaptureSnapshot("SelectAll")
```

**Test:** Bày 10 đồ → Ctrl+A → tất cả outline → Delete → tất cả biến mất.

---

### S1.T14 — Selection Info Bar widget (1 giờ)
**Files:** WBP_MeshControls (extend)

**Layout thêm:**
```
[Select] [Move] [Rotate] [Scale] | [Delete] [Info] [Replace]
                           ↓
[ET_SelectionCount: "✦ 5 vật thể"]   [BTN_NhómNhanh (Sprint 3+)]
[SnapStep] [SnapAngle] [SnapScale]
```

**Visibility logic:**
```
Branch SelectedActors.Length:
  == 0 → ET_SelectionCount = Hidden
  == 1 → ET_SelectionCount = Hidden (single = không cần count)
  >= 2 → ET_SelectionCount = Visible, text = "✦ N vật thể"
```

**Test:** Click 1 đồ → không hiện. Ctrl+Click thêm → hiện "✦ 2 vật thể".

---

### S1.T15 — Multi-Rotate/Scale qua Pivot (2-3 giờ) ⚠️ KHÓ — làm CUỐI

**Chỉ làm sau khi Move-only đã chạy ổn định.** Nếu hết thời gian, dời sang đầu Sprint 2 — Move-only multi-select đã đủ ship.

**Bước 1 — Bật bản ĐẦY ĐỦ của ApplyTransformToChildren (xem S1.T3).**

**Bước 2 — Capture initial state khi bắt đầu drag:**
```
Khi gizmo bắt đầu drag Pivot (OnMousePressed gizmo, nếu SelectedActor == Pivot):
  Pivot.RefreshOffsets   ← lưu InitialOffsets, InitialChildScales, InitialChildRotations
  SET InitialPivotRotation = Pivot.Rotation
  SET InitialPivotScale = Pivot.Scale3D
```

**Bước 3 — Test riêng từng case (đừng gộp):**
- [ ] Rotate nhóm 2 đồ cùng rotation → cả 2 xoay quanh center, formation đúng
- [ ] Rotate nhóm có đồ đã xoay sẵn 45° → giữ rotation tương đối đúng
- [ ] Scale nhóm uniform 2x → khoảng cách + size tăng 2x
- [ ] Scale non-uniform (X=2, Y=1) → kiểm tra KHÔNG méo hình (shear)
- [ ] Rotate + Scale liên tiếp → không tích lũy lỗi

**Nếu gặp shear/méo (case non-uniform scale + rotation):**
→ Đây là giới hạn toán học cơ bản (non-uniform scale không giao hoán với rotation).
→ Plan B: chặn non-uniform scale cho multi-select (chỉ cho scale uniform khi >1 đồ).
→ Ghi DEVIATIONS.md nếu áp dụng Plan B.

---

### Sprint 1 Final Test (1 giờ)

- [ ] Click 1 đồ → chọn
- [ ] Ctrl+Click thêm 4 đồ → 5 đồ outline (1 đậm, 4 nhạt)
- [ ] Gizmo Move → 5 đồ di chuyển cùng nhau
- [ ] Gizmo Rotate → 5 đồ xoay quanh center
- [ ] Arrow keys nudge → 5 đồ nudge
- [ ] Ctrl+C → Ctrl+V → 5 đồ mới spawn ở cursor
- [ ] Ctrl+D → 5 đồ duplicate
- [ ] Delete → 5 đồ biến mất + xác nhận dialog
- [ ] Ctrl+A → tất cả đồ trong scene
- [ ] Esc → deselect all
- [ ] Undo nhiều bước → đúng thứ tự
- [ ] Save → Load → multi-select khôi phục

---

## SPRINT 2 — BOX SELECT + CONTEXT MENU (3-5 ngày, 8 tasks)

### S2.T1 — WBP_BoxSelectOverlay widget (1 giờ)
**Files:** WBP_BoxSelectOverlay (mới)

**Layout:**
- Canvas Panel root
- 1 Image: Tint = (0.2, 0.6, 1.0, 0.2), Hit Test = NotHitTestable

**Variables:**
```
StartPos       : Vector2D
CurrentPos     : Vector2D
bIsDrawing     : Boolean
```

**Function `StartDrawing(StartScreenPos)`:**
```
SET StartPos = StartScreenPos
SET CurrentPos = StartScreenPos
SET bIsDrawing = True
Set Visibility = Visible
```

**Function `UpdateDrawing(CurrentScreenPos)`:**
```
SET CurrentPos = CurrentScreenPos
← Update Image canvas slot:
TopLeft = (min(Start.X, Current.X), min(Start.Y, Current.Y))
Size = (abs(Current.X - Start.X), abs(Current.Y - Start.Y))
Slot as Canvas Slot(Image) → Set Position(TopLeft), Set Size(Size)
```

**Function `StopDrawing` → Returns Rectangle:**
```
SET bIsDrawing = False
Set Visibility = Hidden
Return (StartPos, CurrentPos)
```

---

### S2.T2 — Box Select trong Mouse Pressed (2 giờ)
**Files:** BP_FurnitureInputManager

**Thêm vào Mouse Left Pressed Step 4-6:**
```
Step 5: Branch bHit == False:
  T:
    ← MỚI: bắt đầu box select
    Spawn WBP_BoxSelectOverlay → Add to Viewport
    GET Mouse Position on Viewport → StartPos
    BoxOverlay.StartDrawing(StartPos)
    SET bIsBoxSelecting = True
    STOP
```

**Event Tick (cuối Tick hiện tại):**
```
Branch bIsBoxSelecting:
  T:
    GET Mouse Position on Viewport → CurrentPos
    BoxOverlay.UpdateDrawing(CurrentPos)
```

**Mouse Left Released:**
```
Branch bIsBoxSelecting:
  T:
    rect = BoxOverlay.StopDrawing
    BoxOverlay.Remove from Parent

    ← Tìm actors trong rectangle
    CLEAR LocalActorsInBox
    Get All Actors With Tag("FurnitureSpawned"):
      ForEach Actor:
        Project Actor.Location to Screen → screenPos, bSuccess
        Branch bSuccess AND screenPos.X >= rect.Min.X AND screenPos.X <= rect.Max.X
                       AND screenPos.Y >= rect.Min.Y AND screenPos.Y <= rect.Max.Y:
          Cast BP_FurnitureActor → ADD to LocalActorsInBox

    Branch IsCtrlDown:
      F → DeselectAll → SelectActors(LocalActorsInBox)
      T → SelectActors(LocalActorsInBox)  ← add to existing

    CaptureSnapshot("BoxSelect")
    SET bIsBoxSelecting = False
```

**Test:** Kéo khung từ vùng trống → đồ trong khung được chọn.

---

### S2.T3 — WBP_ContextMenu widget (1.5 giờ)
**Files:** WBP_ContextMenu (mới), WBP_ContextMenuItem (mới)

**WBP_ContextMenuItem:**
```
Layout:
  Horizontal Box:
    [Icon image] [Label text] [Shortcut text]

Variables:
  Label    : Text
  Shortcut : Text
  Icon     : Texture2D (Soft)
  OnClicked : Event Dispatcher (parameterless)

Button overlay → OnClicked → Broadcast OnClicked
```

**WBP_ContextMenu:**
```
Layout:
  Vertical Box (chứa các WBP_ContextMenuItem)
  Border outline + background

Function `AddMenuItem(Label, Shortcut, Icon, Callback : Delegate)`:
  Create WBP_ContextMenuItem → AddChild
  Set Label, Shortcut, Icon
  Bind OnClicked → Callback

Function `ShowAtMousePosition`:
  Get Player Controller → Get Mouse Position → screenPos
  Add to Viewport
  Set Position In Viewport(screenPos)

Function `Hide`:
  Remove from Parent

Event OnAnyClick (Tick check):
  Branch Mouse Left Pressed AND mouse outside menu bounds:
    T → Hide
```

---

### S2.T4 — Right-click handler (1.5 giờ)
**Files:** BP_FurnitureInputManager, BP_FoffPlayerController

**Input action:**
```
IA_RightClick (Boolean)
LM mapping: Right Mouse Button → Pressed
```

**BP_FoffPlayerController route:**
```
IA_RightClick (Started):
  GET BP_FurnitureInputManager → OnRightClick
```

**BP_FurnitureInputManager Event `OnRightClick`:**
```
GetHitResultUnderCursorByChannel(CAMERA) → HitActor, bHit

Branch bHit AND HasTag("FurnitureSpawned"):
  T:
    ← Đảm bảo actor đó đang chọn
    Cast HitActor → BP_FurnitureActor
    Branch SelectedActors.Contains(BP_FurnitureActor):
      F → SelectSingleActor(BP_FurnitureActor)  ← thay vì menu trên actor không chọn

    Spawn WBP_ContextMenu
    Add menu items (Cut, Copy, Duplicate, Delete, Info, Material, Replace, Lock)
    Bind callbacks
    ShowAtMousePosition

  F:
    ← Click phải vùng trống
    Spawn WBP_ContextMenu
    Add items (Paste, Undo, Redo, Select All, Unlock All)
    ShowAtMousePosition
```

**Test:** Right-click trên đồ → menu hiện. Click item → action chạy.

---

### S2.T5 — Select Similar logic (1 giờ)
**Files:** BP_FurnitureInputManager

**Function `SelectSimilar(Criteria : Name, ReferenceActor : BP_FurnitureActor)`:**

```
CLEAR LocalSimilar
Branch Criteria:
  == "Mesh":
    refMeshPath = ReferenceActor.MeshPath
    Get All Actors With Tag("FurnitureSpawned"):
      ForEach actor → Cast → if MeshPath == refMeshPath: ADD to LocalSimilar

  == "Category":
    refDAPath = ReferenceActor.DAPath
    Load Asset Blocking(refDAPath) → Cast DA_FurnitureItem → refCategory
    Get All Actors With Tag("FurnitureSpawned"):
      ForEach actor → Cast → GET DAPath → Load → Cast → GET Category
                   → if Category == refCategory: ADD to LocalSimilar

  == "Folder":
    refDAPath = ReferenceActor.DAPath
    Load → GET MeshFolderPath → refFolder
    ForEach actor: GET Folder → if == refFolder: ADD

  == "Material":
    Branch ReferenceActor.MaterialOverrides.Length > 0:
      refMat = ReferenceActor.MaterialOverrides[0]
      ForEach actor: if MaterialOverrides[0] == refMat: ADD

Branch IsCtrlDown:
  F → DeselectAll → SelectActors(LocalSimilar)
  T → SelectActors(LocalSimilar)
```

**Context menu submenu cho Select Similar:** mở submenu list 4 criteria.

**Test:** Right-click ghế → Select Similar → Same Mesh → tất cả ghế cùng model được chọn.

---

### S2.T6 — Ctrl+I Invert Selection (30 phút)
**Files:** LM, PC, BP_FurnitureInputManager

```
IA_InvertSelection (Boolean) — Ctrl+I

Function InvertSelection:
  Get All Actors With Tag("FurnitureSpawned") → AllActors
  CLEAR Inverted
  ForEach AllActors:
    Cast BP_FurnitureActor → bp
    Branch NOT SelectedActors.Contains(bp): ADD to Inverted
  DeselectAll
  SelectActors(Inverted)
  CaptureSnapshot("InvertSelection")
```

---

### S2.T7 — Cut (Ctrl+X) (15 phút)
**Files:** LM, PC, BP_FurnitureInputManager

```
Function CutMesh:
  Branch SelectedActors.Length == 0: return
  Call CopyMesh
  ForEach SelectedActors (Actor):
    Destroy Actor
  CLEAR SelectedActors
  SET Primary = None
  DeactivateGizmo
  Broadcast OnSelectionChanged([], None)
  CaptureSnapshot("CutMulti")
```

---

### Sprint 2 Final Test
- [ ] Drag khung trên vùng trống → đồ trong khung chọn
- [ ] Ctrl + drag khung → thêm vào selection
- [ ] Right-click trên đồ → menu hiện 8 mục
- [ ] Right-click vùng trống → menu hiện 5 mục
- [ ] Click ngoài menu → menu đóng
- [ ] Select Similar (Mesh) → 6 ghế giống được chọn
- [ ] Ctrl+I → đảo selection
- [ ] Ctrl+X → cắt mesh, có thể paste lại

---

## SPRINT 3 — GROUP CƠ BẢN (5-7 ngày, 10 tasks)

### S3.T1 — Struct S_GroupData (10 phút)
**Files:** Data

```
S_GroupData:
  GroupID       : String
  GroupName     : String
  ParentGroupID : String
  bIsLocked     : Boolean
```

### S3.T2 — BP_FurnitureActor thêm GroupID (10 phút)
```
GroupID : String (SaveGame, default "")
```

### S3.T3 — BP_GroupsContainer actor (45 phút)
**Files:** BP_GroupsContainer (mới)
```
Parent: Actor
Tag: "FurnitureGroupsContainer"
Interface: EMSActorSaveInterface

Variables (SaveGame):
  Groups : Array of S_GroupData

Event BeginPlay:
  ADD "FurnitureGroupsContainer" to Tags

Event ActorLoaded:
  Get All Actors Of Class(BP_FurnitureInputManager) → Cast
  SET BP_FurnitureInputManager.Groups = Self.Groups
```

Spawn 1 instance trong Level Blueprint BeginPlay.

### S3.T4 — Groups variable + sync trong BP_FurnitureInputManager (30 phút)
```
Variables thêm:
  Groups : Array of S_GroupData

Function SyncGroupsToContainer:
  Get All Actors With Tag("FurnitureGroupsContainer") → Get(0)
  → SET Groups = Self.Groups
```

Gọi `SyncGroupsToContainer` sau mỗi thay đổi group.

### S3.T5 — WBP_GroupNameDialog widget (45 phút)
```
Layout:
  Title: "Đặt tên nhóm"
  Editable Text Box: default = "Nhóm N"
  Buttons: [Hủy] [OK]

Event Dispatcher:
  OnConfirmed(GroupName : String)
```

### S3.T6 — Function CreateGroup (1 giờ)
**Files:** BP_FurnitureInputManager

```
Function CreateGroup(GroupName : String):
  Branch SelectedActors.Length < 2: return ""

  ← Generate unique GroupID
  newGroupID = "g_" + Generate UUID (String)

  ← Tạo group data
  newGroup = S_GroupData{
    GroupID = newGroupID,
    GroupName = GroupName,
    ParentGroupID = "",
    bIsLocked = False
  }
  ADD newGroup to Groups
  Call SyncGroupsToContainer

  ← Gán GroupID cho actors
  ForEach SelectedActors:
    Cast → SET GroupID = newGroupID

  CaptureSnapshot("CreateGroup")
  Broadcast OnGroupCreated(newGroupID)
  Return newGroupID
```

### S3.T7 — Ctrl+G handler (30 phút)
```
IA_GroupCreate (Boolean) — Ctrl+G

OnIA_GroupCreate:
  Branch SelectedActors.Length < 2: return
  Spawn WBP_GroupNameDialog → Set default name "Nhóm N"
  Bind OnConfirmed → Lambda:
    Call CreateGroup(GroupName)
```

### S3.T8 — Function UngroupActors (45 phút)
```
Function UngroupActors(GroupID : String, bRecursiveAll : Boolean):
  Branch GroupID == "": return

  ← Find children
  Get All Actors With Tag("FurnitureSpawned"):
    ForEach actor → Cast → if GroupID == InputGroupID: ADD to children

  ForEach children:
    Branch bRecursiveAll AND actor có sub-group:
      T → UngroupActors(child.GroupID, True) recursive
    SET actor.GroupID = ""  ← (or ParentGroupID if exists)

  ← Remove S_GroupData
  Find Index(Groups where GroupID == InputGroupID) → idx
  Branch idx >= 0: REMOVE INDEX(Groups, idx)
  Call SyncGroupsToContainer

  CaptureSnapshot("Ungroup")
  Broadcast OnGroupDestroyed(GroupID)
```

### S3.T9 — Group Click Behavior (refactor Mouse Left Pressed) (1 giờ)

Refactor Step 7 trong Mouse Left Pressed:
```
Step 7: Cast HitActor → GET GroupID

  Branch GroupID != "" AND CurrentEditingGroupID == "":
    ← Click vào đồ trong group → chọn cả group
    Get All Actors With Tag("FurnitureSpawned"):
      ForEach → if GroupID matches → ADD to groupChildren

    Branch IsCtrlDown:
      F → DeselectAll → SelectActors(groupChildren)
      T → SelectActors(groupChildren)  ← add to existing
    STOP

  Branch IsCtrlDown:
    T → ToggleActor → STOP
    F → SelectSingleActor(HitActor) → STOP
```

### S3.T10 — Multi-Snapshot Groups (45 phút)
**Files:** Data, BP_UndoManager

**S_SceneSnapshot:**
```
Version = 3 (sau khi thêm Groups)
Groups : Array of S_GroupData   ← MỚI
```

**S_FurniturePlacement:**
```
GroupID : String   ← MỚI
```

**CaptureSnapshot thêm:**
```
ForEach actor: Build placement với GroupID = actor.GroupID

GET BP_FurnitureInputManager.Groups → SET Snapshot.Groups
```

**RestoreSnapshot thêm:**
```
ForEach Snapshot.Meshes (mesh):
  spawnedActor.GroupID = mesh.GroupID

CLEAR BP_FurnitureInputManager.Groups
ForEach Snapshot.Groups: ADD to InputManager.Groups
SyncGroupsToContainer
```

### Sprint 3 Final Test
- [ ] Multi-select 6 đồ → Ctrl+G → dialog "Đặt tên" → OK
- [ ] Group visible: click 1 đồ → cả 6 chọn
- [ ] Move group → 6 đồ di chuyển cùng
- [ ] Rotate group → 6 đồ xoay quanh pivot
- [ ] Delete group → cả 6 đồ xóa
- [ ] Ctrl+Shift+G → ungroup → 6 đồ thành riêng lẻ
- [ ] Save → Load → group khôi phục đúng
- [ ] Undo/Redo create group → đúng

---

## SPRINT 4 — EDIT MODE + NESTED GROUP (5-7 ngày)

### Tasks tổng quan:
- T1: WBP_EditModeOverlay (dim background)
- T2: EnterEditMode / ExitEditMode functions
- T3: Double-click detection (DoubleClick interval < 0.3s)
- T4: Nested group support (ParentGroupID logic)
- T5: Group hierarchy navigation (Esc đi lên 1 cấp)
- T6: WBP_EditModeIndicator (top bar "Đang chỉnh: Bộ sofa")
- T7: Nested group: sub-group inherits parent transform khi cha move
- T8: Snapshot CurrentEditingGroupID

Chi tiết để dành cho khi triển khai — sẽ break down thêm khi vào Sprint 4.

---

## SPRINT 5 — COMBO MESH (5-7 ngày)

### Tasks tổng quan:
- T1: S_ComboMeshData struct + DT_ComboMeshCatalog
- T2: WBP_SaveComboDialog
- T3: Function SaveCurrentGroupAsCombo → serialize JSON
- T4: Combo Thumbnail generation (SceneCapture2D)
- T5: WBP_FurnitureInventory category "Combo"
- T6: WBP_ComboCard widget
- T7: Function SpawnCombo → parse JSON + ForEach SpawnFurnitureCopy
- T8: Ghost preview multi-mesh when dragging combo

---

## SPRINT 6 — POLISH UX (5-7 ngày)

### Tasks tổng quan:
- T1-T2: Lock/Unlock (bIsLocked field, input filter, visual indicator)
- T3-T4: Align & Distribute (6 + 2 buttons trên toolbar)
- T5-T7: WBP_SceneOutliner (tree view của toàn scene)
- T8: Toggle Visibility
- T9: Focus (F key)
- T10-T11: Smart Snap (5 loại snap, guidelines)
- T12: Array/Pattern (nhân theo hàng/lưới)
- T13: Mirror Group

---

## SPRINT 7 — MATERIAL EDIT v1.2 (3-5 ngày)

### Tasks tổng quan:
- T1: WBP_MaterialEditPanel layout
- T2: Color Picker integration
- T3: Roughness/Metallic sliders
- T4: SetMaterial Color/Roughness/Metallic functions
- T5: Multi-select apply (ForEach DMI)
- T6: Serialize to MaterialParams JSON
- T7: Undo/Redo material params
- T8: UV Scale/Rotation (optional)
- **T9: CLEANUP — Xóa dual state (BẮT BUỘC, đừng quên)**

### S7.T9 — Cleanup dual state SelectedFurnitureActor (1 giờ)

⚠️ **Task này dễ bị quên — nhưng quan trọng.** Suốt Sprint 1-6 ta giữ song song `SelectedFurnitureActor` (cũ) + `PrimarySelectedActor` (mới) "cho compat". Đây là vi phạm Single Source of Truth có chủ đích, giờ là lúc dọn.

**Bước 1 — Tìm mọi nơi đọc/ghi SelectedFurnitureActor:**
```
Right-click SelectedFurnitureActor variable → Find References
→ Liệt kê tất cả node đọc/ghi
```

**Bước 2 — Thay từng reference:**
```
GET SelectedFurnitureActor → GET PrimarySelectedActor
SET SelectedFurnitureActor → xóa (PrimarySelectedActor đã được set ở helper functions)
```

**Bước 3 — Kiểm tra các widget bind:**
- WBP_FurnitureInventory: OnMeshSelected vẫn fire? → đổi sang OnSelectionChanged nếu chưa
- WBP_MeshControls: dùng Primary chưa?
- WBP_DetailPopup: nhận Primary chưa?

**Bước 4 — Xóa biến + deprecated dispatchers:**
```
Sau khi Find References = 0:
  Xóa variable SelectedFurnitureActor
  Cân nhắc xóa OnMeshSelected/OnMeshDeselected (nếu đã chuyển hết sang OnSelectionChanged)
```

**Bước 5 — Regression test toàn bộ** (07 Core Regression Suite) → đảm bảo không gãy gì.

⚠️ Nếu Find References còn nhiều và rủi ro → có thể GIỮ dual state, ghi DEVIATIONS.md "không cleanup vì rủi ro cao". Nhưng phải là quyết định có ý thức, không phải quên.
