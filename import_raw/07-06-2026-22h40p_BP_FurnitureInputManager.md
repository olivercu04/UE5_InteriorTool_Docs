# BP_FurnitureInputManager
**Phiên bản:** 1.5 | **Cập nhật:** 07/06/2026 — 22:40 ICT | Actor riêng — input hub + multi-select hub + box-select hub + context-menu hub

---

## Mục đích
Tách toàn bộ logic input furniture khỏi BP_FoffPlayerController (shared code).
Chỉ cần spawn actor này vào level là hệ thống hoạt động — không đụng shared code.

**v1.4:** thêm hệ thống **Multi-Select** (Sprint 1 plan_v3). Giữ song song state cũ (`SelectedFurnitureActor`) và state mới (`SelectedActors` + `PrimarySelectedActor`) đến hết Sprint 7 (S7.T9 cleanup).

**v1.5 (Sprint 2 — Box Select + Context Menu):** thêm **Box Select** (kéo khung chọn nhiều đồ) và **Context Menu** (right-click). Đây là actor giữ NHIỀU code phức tạp nhất — đặc biệt là tương tác giữa Mouse Left Pressed (defer click), Event Tick (vẽ box, phát hiện kéo), và OnLMBReleased (chốt selection). Đọc kỹ mục "TƯƠNG TÁC 3 ĐIỂM" ở dưới trước khi sửa.

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

### Box Select (v1.5 — Sprint 2 T1-T2) ⭐
```
BoxSelectOverlayRef : WBP_BoxSelectOverlay   ← widget khung chọn, tạo ở BeginPlay
BoxStartPos         : Vector2D               ← vị trí chuột lúc bấm (logical/viewport coords)
bIsPendingBoxSelect : Boolean                ← ĐÃ bấm chuột, CHƯA biết là click hay kéo (chờ vượt ngưỡng 5px)
bIsBoxSelecting     : Boolean                ← ĐANG kéo khung (đã vượt 5px)
bLMBHeld            : Boolean                ← cờ thủ công: chuột trái đang giữ (SET True ở Mouse Left Pressed, False ở OnLMBReleased)
PendingClickActor   : BP_FurnitureActor      ← đồ bị bấm vào (defer select tới lúc thả, để phân biệt click-chọn vs kéo-box từ trên mesh)
```

### Context Menu (v1.5 — Sprint 2 T3-T4)
```
ContextMenuRef      : WBP_ContextMenu        ← menu chuột phải, tạo on-demand, clear ở Destruct của widget
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

## ⭐⭐ TƯƠNG TÁC 3 ĐIỂM — Box Select / Single Click / Defer (đọc TRƯỚC khi sửa)

Đây là phần dễ gây bug nhất. Box Select chạm vào 3 nơi cùng lúc; phải hiểu vì sao chia như vậy:

**1. Mouse Left Pressed (input event):** chỉ GHI NHẬN bấm — KHÔNG select ngay. Ghi `BoxStartPos`, bật `bIsPendingBoxSelect`, bật `bLMBHeld`. Nếu bấm trúng mesh thì nhớ mesh đó vào `PendingClickActor` (chưa select). → **defer toàn bộ quyết định tới lúc thả chuột.**

**2. Event Tick (mỗi frame):** phát hiện chuột đã kéo quá 5px chưa. Nếu rồi → chuyển `bIsPendingBoxSelect`→`bIsBoxSelecting`, vẽ khung. Tick KHÔNG select đồ, chỉ lo VẼ KHUNG + cập nhật kích thước khung.

**3. OnLMBReleased (input event):** chốt kết quả.
   - Nếu `bIsBoxSelecting` (đã kéo box) → `FinishBoxSelect` (chọn các đồ trong khung).
   - Nếu `bIsPendingBoxSelect` mà CHƯA kéo (click đơn thuần) → nếu có `PendingClickActor` thì `SelectSingleActor` đồ đó; nếu không (bấm vào nền) thì `DeselectAll`.

**TẠI SAO defer (PendingClickActor) thay vì select ngay ở Mouse Left Pressed?**
→ Để phân biệt **click-chọn-1-đồ** vs **bắt đầu-kéo-box-từ-trên-một-đồ**. Nếu select ngay lúc bấm thì vừa chạm mesh đã single-select, không kéo box được.

**TẠI SAO chốt selection ở OnLMBReleased mà KHÔNG ở Tick?**
→ **Bug đã trả giá (Sprint 2):** gọi `ActivateGizmo` trong Event Tick race với Tick nội bộ của plugin RuntimeTransformer → gizmo NHÁY 1 frame trước khi mesh hiện. Input event (OnLMBReleased) chạy TRƯỚC world Tick → không nháy. → **Mọi việc ActivateGizmo/SelectSingleActor/FinishBoxSelect đặt ở OnLMBReleased, KHÔNG ở Tick.** Tick chỉ giữ nhánh fallback cho trường hợp flick chuột cực nhanh giữa các frame.

**TẠI SAO dùng cờ `bLMBHeld` thay vì `Is Input Key Down(Left Mouse Button)`?**
→ **Bug đã trả giá:** `Is Input Key Down` KHÔNG đáng tin cho nút chuột khi viewport đang capture mouse → khung box dính lại sau khi thả. Dùng boolean SET tay (True lúc bấm, False lúc thả) thì chắc chắn.

---

## Event BeginPlay (v1.5)
```
Enable Input
SET CurrentMeshControls = None, SET SelectedFurnitureActor = None
Get All Actors Of Class(BP_TransformerPawn) → Get(0) → SET TransformerPawnRef
← v1.5 Box Select:
Create Widget(WBP_BoxSelectOverlay) → SET BoxSelectOverlayRef
  → Add to Viewport(Z-Order 100)
  → Call HideBox (ẩn ban đầu)
```

---

## Mouse Left Pressed — FULL FLOW (v1.5)
```
Step 0 : SET bLMBHeld = True                              ← v1.5 (đầu tiên!)
Step 0b: Set Input Mode Game And UI
Step 1 : SET LocalWasGizmoActive = GizmoControllerRef.bGizmoActive
Step 2 : GizmoController → OnMousePressed
Step 3 : Branch bIsDraggingGizmo == True → True: STOP     ← đang cầm gizmo thì bỏ qua
Step 4 : GetHitResultUnderCursorByChannel(CAMERA) → Hit Actor, ReturnValue

Step 5 : Branch ReturnValue == True:
           False (bấm vào khoảng không) →
             Get Mouse Position on Viewport → SET BoxStartPos
             SET bIsPendingBoxSelect = True
             → STOP                                       ← KHÔNG check Ctrl lúc bấm; KHÔNG DeselectAll ngay (defer tới thả)

Step 6 : Branch ActorHasTag(Hit Actor, "FurnitureSpawned"):
           False (bấm trúng đồ KHÔNG phải furniture, vd tường) →
             Get Mouse Position on Viewport → SET BoxStartPos
             SET bIsPendingBoxSelect = True
             → STOP

Step 7 : Branch IsInputKeyDown(Left Ctrl):
           True  → ToggleActor(HitActor as BP_FurnitureActor) → CaptureSnapshot("Select") → STOP   ← Ctrl giữ nguyên hành vi cũ (toggle ngay)
           False → DEFER:                                                                          ← v1.5: KHÔNG SelectSingleActor ngay
                     SET PendingClickActor = (HitActor as BP_FurnitureActor)
                     Get Mouse Position on Viewport → SET BoxStartPos
                     SET bIsPendingBoxSelect = True
                     → STOP
```
**Khác v1.4:** Step 5/6/7-False trước đây select/deselect NGAY. Giờ chỉ ghi nhận + defer. Quyết định cuối ở OnLMBReleased.

---

## Event Tick — Box Select branch (v1.5)
> Đặt SAU nhánh nudge free-mode, dùng **Sequence** để không phá logic cũ.

**⚠️ Bug đã trả giá — phải GUARD inventory:** Event Tick chạy MỌI frame, KHÔNG bị gate bởi Input Mapping Context (`LM_FurnitureInput`) như các Enhanced Input action khác. Nếu không guard, box select kích hoạt cả khi inventory đóng → sai context. Guard thủ công:
```
GetGameInstance → Cast Foff_GameInstance → GET FurnitureInventoryRef
→ nested Branch: IsValid(FurnitureInventoryRef)  [Branch ngoài]
     True → Is In Viewport(FurnitureInventoryRef) [Branch trong]   ← KHÔNG dùng AND (Blueprint AND không short-circuit → crash None)
            True → SET bInventoryOpen = True
     (mọi nhánh khác → SET bInventoryOpen = False)

Branch bInventoryOpen:
  False → cleanup: Call HideBox + SET bIsPendingBoxSelect=False + SET bIsBoxSelecting=False → STOP
  True  → chạy 2 branch box dưới đây
```

**Branch A — đang PENDING (bIsPendingBoxSelect == True):**
```
Branch bLMBHeld:
  True (vẫn giữ chuột) →
     khoảng cách = VectorLength( (Get Mouse Position on Viewport) - BoxStartPos )
     Branch khoảng cách > 5.0:
       True (đã kéo đủ xa → là KÉO BOX) →
         SET bIsBoxSelecting = True
         SET bIsPendingBoxSelect = False
         Call ShowBox
         Call UpdateBox(BoxStartPos, hiện tại)
  False (đã THẢ trước khi vượt 5px → là CLICK, fallback nếu OnLMBReleased lỡ) →
     SET bIsPendingBoxSelect = False
     Branch IsValid(PendingClickActor):
       True  → SelectSingleActor(PendingClickActor) → CaptureSnapshot("Select") → SET PendingClickActor=None
       False → Branch IsInputKeyDown(Left Ctrl):
                 True  → (dead-end, giữ selection)
                 False → DeselectAll → CaptureSnapshot("Deselect")
```

**Branch B — đang KÉO BOX (bIsBoxSelecting == True):**
```
Branch bLMBHeld:
  True  → Call UpdateBox(BoxStartPos, Get Mouse Position on Viewport)   ← cập nhật kích thước khung mỗi frame
  False (đã thả — fallback nếu OnLMBReleased lỡ) →
     Call FinishBoxSelect(Get Mouse Position on Viewport)
     Call HideBox
     SET bIsBoxSelecting = False
     SET PendingClickActor = None
```
> Tick là **fallback**. Đường chính chốt ở OnLMBReleased (input-event timing, không nháy gizmo).

---

## OnLMBReleased — FULL FLOW (v1.5) ⭐ đường chính chốt selection
```
SET bLMBHeld = False                                   ← đầu tiên!
Sequence:
  Then 0: đóng context menu nếu đang mở (IsValid(ContextMenuRef) → Remove from Parent → SET None)

  Then 1: Branch bIsBoxSelecting == True:               ← ĐANG kéo box, vừa thả
            True →
              Get Mouse Position on Viewport → EndPos
              Call FinishBoxSelect(EndPos)
              Branch IsValid(BoxSelectOverlayRef) → Call HideBox
              SET bIsBoxSelecting = False
              SET PendingClickActor = None

  Then 2: Branch bIsPendingBoxSelect == True:            ← CLICK đơn (chưa từng kéo)
            True →
              SET bIsPendingBoxSelect = False
              Branch IsValid(PendingClickActor):
                True  → SelectSingleActor(PendingClickActor) → CaptureSnapshot("Select") → SET PendingClickActor=None
                False → Branch IsInputKeyDown(Left Ctrl):
                          True  → (dead-end, giữ selection — Ctrl+click nền không deselect)
                          False → DeselectAll → CaptureSnapshot("Deselect")
                                  → Branch bIsReplaceMode → (exit replace mode chain nếu đang replace)
```
**Lưu ý timing:** OnLMBReleased (input event) chạy TRƯỚC world Tick cùng frame → ActivateGizmo gọi từ đây KHÔNG nháy. Tick chỉ dọn nốt edge case.

---

## FinishBoxSelect(EndPos : Vector2D) — Function (v1.5)
```
Min/Max → TopLeft = (Min X, Min Y), BottomRight = (Max X, Max Y) từ BoxStartPos & EndPos
CLEAR LocalSelected (local array)

Get All Actors With Tag("FurnitureSpawned") → ForEach (Actor):
  Branch (Actor != PendingClickActor):                 ← loại mesh mà ta bắt đầu kéo box TỪ TRÊN nó
    True →
      Cast To BP_FurnitureActor → IsValid →
      Get Actor Location → Project World To Screen → ScreenPos
      ← ⚠️ FIX DPI: chia ScreenPos cho Get Viewport Scale (Widget Layout Library) = ScreenPosFixed
      Branch (ScreenPosFixed.X >= TopLeft.X AND <= BottomRight.X)   [nested Branch, không dùng AND node]
        AND (ScreenPosFixed.Y >= TopLeft.Y AND <= BottomRight.Y):
          True → ADD Actor → LocalSelected

Completed:
  Branch LENGTH(LocalSelected) > 0:
    True →
      Branch IsInputKeyDown(Left Ctrl):
        True  → ForEach LocalSelected → ToggleActor   ← Ctrl: cộng dồn vào selection cũ
        False → DeselectAll → SelectActors(LocalSelected)
      → CaptureSnapshot("BoxSelect")
```
**⚠️ Bug đã trả giá — DPI mismatch:** `Get Mouse Position on Viewport` trả tọa độ LOGICAL (đã chia DPI); `Project World To Screen` trả PIXEL THÔ. So sánh trực tiếp → chọn nhầm/lệch đồ. Phải chia `Project World To Screen` cho `Get Viewport Scale` để cùng hệ tọa độ với mouse.

**Lưu ý chủ đích (KHÔNG phải bug):** chọn theo **PIVOT/origin** của đồ (1 điểm), không theo bounding box. Đồ chỉ "vào khung" khi điểm gốc nằm trong khung. Đúng ý đồ thiết kế.

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
⚠️ KHÔNG có CaptureSnapshot nội bộ — caller tự gọi sau (xác nhận lại trong session 07/06 khi debug double-capture)
```

### SelectSingleActor(Actor) (T5)
```
DeselectAll → ADD Actor → SelectedActors → SET Primary → UpdateOutlineState → UpdateGizmo → Broadcast OnSelectionChanged
⚠️ KHÔNG có CaptureSnapshot nội bộ — caller (Mouse/OnLMBReleased) tự gọi sau (xác nhận 07/06)
```

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
**Lưu ý:** caller (Paste/Duplicate/Restore/BoxSelect) phải DeselectAll trước khi gọi (SelectedActors rỗng) → vòng Contains không trùng.

### ToggleActor(Actor) (T5, T7)
```
Branch Contains(SelectedActors, Actor):
  True  → Remove from SelectedActors → Set Render Custom Depth=False (clear stencil)
  False → ADD to SelectedActors
SET Primary = (last actor còn lại / Actor vừa thêm)
UpdateOutlineState → UpdateGizmo → Broadcast OnSelectionChanged
⚠️ KHÔNG có CaptureSnapshot nội bộ — caller gọi sau toggle
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

## CONTEXT MENU FUNCTIONS (v1.5 — Sprint 2 T3-T6)
**Widget:** WBP_ContextMenu (container) + WBP_ContextMenuItem (mỗi dòng) + WBP_MenuSeparator.

### Right-click handler (T4)
```
Phát hiện right-click: dùng time-based + check camera đang xoay/pan (cursor bị lock khi pan)
→ nếu là click thật (không phải kết thúc pan):
   IsValid(ContextMenuRef) → Remove cũ → SET None    (chỉ 1 menu cùng lúc)
   Create Widget(WBP_ContextMenu) → SET ContextMenuRef → Add to Viewport
   Set Position In Viewport(vị trí chuột)
   Bind callback các item
```
> Menu đóng bằng background button (full-screen invisible button phía sau menu) + đóng ở OnLMBReleased Then 0.

### Callbacks (T5-T6)
```
CB_Copy       → CopyMesh
CB_Duplicate  → DuplicateMesh
CB_Paste      → PasteMesh
CB_ResetRotation → ResetRotation
CB_SelectSimilar → SelectSimilarMesh
CB_Delete     → DeleteSelected
CB_Undo       → UndoManager.UndoLastAction
CB_Redo       → UndoManager.RedoLastAction
CB_ChangeMaterial → [STUB — TODO, làm tiếp session sau]
CB_Replace        → [STUB — TODO, làm tiếp session sau]
```

### SelectSimilarMesh (T5)
```
Guard IsValid(PrimarySelectedActor)
GET PrimarySelectedActor.MeshPath → TargetPath (String)
DeselectAll
Get All Actors With Tag("FurnitureSpawned") → ForEach:
  Cast → IsValid → Branch (MeshPath == TargetPath):   ← so SÁNH STRING, KHÔNG load DA (nhẹ)
    True → ADD to LocalSimilar
Completed → SelectActors(LocalSimilar) → CaptureSnapshot("SelectSimilar")
```

### ResetRotation (T6)
ForEach SelectedActors → IsValid → Set Actor Rotation(0,0,0) → CaptureSnapshot("ResetRotation").

### DeleteSelected (T6)
```
ForEach SelectedActors (Actor):
  IsValid → Destroy Actor(Actor)        ← target = Array Element, KHÔNG phải self
Completed → DeselectAll → CaptureSnapshot("Delete")
```
**⚠️ Bug đã trả giá:** target của Destroy phải là Array Element (đồ đang duyệt), KHÔNG để trống (mặc định self = destroy chính InputManager).

---

## Mouse Left Released (gizmo) — v1.4
```
GizmoController → OnMouseReleased
[T15: CaptureSnapshot khi SelectedActor là Pivot — đã làm]
```

---

## v1.2 — Keyboard Manipulation (UX Phase 2.1)

### B1 — Arrow Key Nudge (MULTI v1.4 — T10)
**Chi tiết:** `B1_Nudge_Flow.md`
- `NudgeMesh(Direction)` — guard `SelectedActors.LENGTH==0 → return`; direction tính từ `PrimarySelectedActor.PlacementSurfaceType`; **ForEach SelectedActors → Add Actor World Offset**; sau ForEach: CalculateCenter → SetActorLocation(Pivot) → RefreshOffsets.
- `CaptureNudgeSnapshot` — debounce 0.5s.
- **Event Tick free mode** — `SnapStep==0 AND SelectedActors.LENGTH>0` → ForEach SelectedActors di chuyển × DeltaTime × NudgeSpeed → cập nhật Pivot.

### B2 — Copy/Paste/Duplicate (MULTI v1.4 — T11)
**Chi tiết:** `B2_CopyPaste_Flow.md`
- `CopyMesh` — CLEAR ClipboardActors → CalculateCenter → ForEach SelectedActors build S_ClipboardEntry (RelativeLocation = ActorLoc - Center) → ADD.
- `PasteMesh` — trace surface → DeselectAll → CLEAR LocalSpawned → ForEach ClipboardActors spawn (bAutoSelect=False) → SelectActors(LocalSpawned) → CaptureSnapshot.
- `DuplicateMesh` — CopyMesh → ForEach SelectedActors tính MaxRightEdge (**phần spawn nối COMPLETED, KHÔNG Loop Body**) → DeselectAll → CLEAR LocalSpawned → ForEach ClipboardActors spawn (bAutoSelect=False) → SelectActors(LocalSpawned) → CaptureSnapshot.
- `SpawnFurnitureCopy(..., bAutoSelect) → NewActor` — Return Node nối NewActorCopy ở CẢ True và False branch.

---

## Event End Play (chống VRAM leak) — v1.5
```
IsValid(CurrentMeshControls) → Remove from Parent
IsValid(SelectedFurnitureActor) → Set Render Custom Depth = False
ForEach SelectedActors → IsValid → Set Render Custom Depth = False
CLEAR SelectedActors
SET PrimarySelectedActor = None, GizmoPivotActor = None
← v1.5:
IsValid(BoxSelectOverlayRef) → Remove from Parent → SET None
IsValid(ContextMenuRef) → Remove from Parent → SET None
SET PendingClickActor = None
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
⚠️ Chỉ có 1 instance (đã verify count=1 trong session 07/06)

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
| 1.4 | 04/06/2026 — 15:30 ICT | Multi-Select (Sprint 1 T1-T14) |
| 1.5 | 07/06/2026 — 22:40 ICT | **Sprint 2 — Box Select + Context Menu.** Vars Box Select (BoxSelectOverlayRef, BoxStartPos, bIsPendingBoxSelect, bIsBoxSelecting, bLMBHeld, PendingClickActor) + ContextMenuRef. BeginPlay tạo WBP_BoxSelectOverlay. **Mouse Left Pressed refactor → DEFER** (PendingClickActor, không select ngay). **Event Tick** box branch (guard inventory + ngưỡng 5px + vẽ khung). **OnLMBReleased** = đường chính chốt selection. **FinishBoxSelect** (DPI fix chia Get Viewport Scale). Context Menu callbacks (Copy/Duplicate/Paste/ResetRotation/SelectSimilar/Delete/Undo/Redo; ChangeMaterial+Replace còn STUB). Xác nhận SelectSingleActor/DeselectAll/ToggleActor KHÔNG chứa CaptureSnapshot nội bộ. |
