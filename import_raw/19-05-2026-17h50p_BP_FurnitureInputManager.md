# BP_FurnitureInputManager
**Phiên bản:** 1.1 | **Cập nhật:** 19/05/2026 — 17:50 ICT | Actor riêng — xử lý toàn bộ input furniture system

---

## Mục đích
Tách toàn bộ logic input furniture khỏi BP_FoffPlayerController (shared code).
Chỉ cần spawn actor này vào level là hệ thống hoạt động — không đụng shared code.

---

## Variables
```
SelectedFurnitureActor : BP_FurnitureActor
CurrentMeshControls    : WBP_MeshControls
GizmoControllerRef     : BP_GizmoController
TransformerPawnRef     : BP_TransformerPawn
ActiveMode             : E_ActiveMode
LocalWasGizmoActive    : Boolean
DetailPopupRef         : WBP_DetailPopup  ← quản lý popup thông tin sản phẩm
bIsReplaceMode         : Boolean          ← True khi đang ở chế độ replace mesh
MeshToReplace          : BP_FurnitureActor ← mesh cần được replace
```

---

## Event Dispatchers (v1.1 UX)
```
OnMeshDeselected()                                ← fire cuối DeselectMesh
OnMeshSelected(SelectedActor : BP_FurnitureActor)  ← fire sau Step 8 (SET SelectedFurnitureActor)
```

---

## Event BeginPlay
```
Enable Input (Player Controller = Get Player Controller)
SET CurrentMeshControls = None
SET SelectedFurnitureActor = None
Get All Actors Of Class(BP_TransformerPawn) → Get(0) → SET TransformerPawnRef
```

---

## Mouse Left Pressed — FULL FLOW
```
Step 0: Set Input Mode Game And UI
        ← PHẢI đặt đầu tiên — fix lỗi input mode sau khi đóng SaveGameMenu

Step 1: SET LocalWasGizmoActive = GizmoControllerRef.bGizmoActive

Step 2: GizmoController → OnMousePressed

Step 3: Branch GizmoControllerRef.bIsDraggingGizmo == True?
          True → STOP
          False → tiếp tục

Step 4: GetHitResultUnderCursorByChannel (TraceChannel = CAMERA)
        → Break Hit Result → Hit Actor, ReturnValue(bool)

Step 5: Branch ReturnValue == True?
          False →
            Branch IsValid(SelectedFurnitureActor)?
              True → DeselectMesh → CaptureSnapshot("Deselect") → STOP
              False → DeselectMesh → STOP
          True → tiếp tục

Step 6: Branch ActorHasTag(Hit Actor, "FurnitureSpawned")?
          False →
            Branch IsValid(SelectedFurnitureActor)?
              True → DeselectMesh → CaptureSnapshot("Deselect") → STOP
              False → DeselectMesh → STOP
          True → tiếp tục

Step 7: Branch IsValid(SelectedFurnitureActor)?
          True:
            DeactivateGizmo
            Cast To BP_FurnitureActor (SelectedFurnitureActor)
            → Get FurnitureMesh → Set Render Custom Depth = False
          False: (thẳng xuống)

Step 8: Cast HitActor → BP_FurnitureActor → SET SelectedFurnitureActor
        → Broadcast OnMeshSelected(SelectedFurnitureActor)  ← v1.1 UX

Step 9: Cast To BP_FurnitureActor (SelectedFurnitureActor)
        → Get FurnitureMesh → Set Render Custom Depth = True
        → Set Custom Depth Stencil Value = 255

Step 10: Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Select")

Step 11: Branch IsValid(CurrentMeshControls)?
           True → Cast To WBP_MeshControls → Call UpdateDetailPopup

Step 12: Sequence Then 1:
           Branch ActiveMode != Select?
             True:
               Select node (Index = ActiveMode):
                 Select/Move → Translation
                 Rotate → Rotation
                 Scale → Scale
               Cast TransformerPawnRef → BP_TransformerPawn
               → ActivateGizmo(SelectedFurnitureActor, AsBP_TransformerPawn, TransformType)
```

---

## Mouse Left Released
```
GizmoController → OnMouseReleased
```

---

## DeselectMesh (Function)
```
Cast To BP_FurnitureActor (SelectedFurnitureActor)
→ Get FurnitureMesh → Set Render Custom Depth = False
SET SelectedFurnitureActor = None
GizmoControllerRef → DeactivateGizmo
Broadcast OnMeshDeselected  ← v1.1 UX, cuối function

⚠️ KHÔNG gọi CaptureSnapshot trong DeselectMesh — gây infinite loop
⚠️ KHÔNG SET CurrentMeshControls = None trong DeselectMesh
CaptureSnapshot("Deselect") chỉ gọi từ Mouse Left Pressed Step 5, 6
```

---

## Event End Play
```
IsValid(CurrentMeshControls) → Remove from Parent
IsValid(SelectedFurnitureActor) → Set Render Custom Depth = False
```

---

## Cách các BP khác lấy reference
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast To BP_FurnitureInputManager
→ GET/SET variables
```

⚠️ KHÔNG dùng Get Player Controller → Cast BP_FoffPlayerController nữa

---

## Level Blueprint — Spawn Order
```
1. BP_UndoManager
2. BP_FurnitureSceneManager
3. BP_TransformerPawn
4. BP_GizmoController
5. BP_FurnitureInputManager → Cast → SET GizmoControllerRef
6. WBP_MeshControls → Add to Viewport → Cast BP_FurnitureInputManager → SET CurrentMeshControls
7. CaptureSnapshot("Initial")
```

---

## Phím I — Toggle WBP_FurnitureInventory (Level Blueprint)
```
Keyboard I Pressed:
Branch IsValid(FurnitureInventoryRef)?
  True → Remove from Parent
          Cast Foff_GameInstance → SET FurnitureInventoryRef = None
          GET BP_FurnitureInputManager → SET bIsReplaceMode = False
  False → Create WBP_FurnitureInventory → Add to Viewport
          Cast Foff_GameInstance → SET FurnitureInventoryRef
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 21/04/2026 — 16:46 ICT | Tạo mới |
| 1.1 | 19/05/2026 — 17:50 ICT | Thêm Event Dispatchers OnMeshDeselected + OnMeshSelected, Broadcast trong DeselectMesh và Step 8 |
