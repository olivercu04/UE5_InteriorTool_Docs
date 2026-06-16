# BP_GizmoController
**HỢP NHẤT TỪ 2 file:** v1.1 base (05/06) + OnMouseReleased fragment (16/04, v1.0 tham khảo)
**Phiên bản:** 1.1 | **Cập nhật:** 05/06/2026 — 20:00 ICT | Actor riêng — xử lý toàn bộ gizmo movement logic

> **v1.1 (05/06 T15):** OnMousePressed thêm Cast → BP_PivotActor → RefreshOffsets (capture drag-start cho multi-select rotate/scale).
> **Lịch sử OnMouseReleased:** Fragment 16/04 dùng `Get Player Controller → Cast BP_FoffPlayerController`. Bản v1.1 (05/06) đổi sang `Get All Actors Of Class(BP_FurnitureInputManager)` — nhất quán với architecture (ActiveMode sống ở InputManager, không PlayerController).

---

## Variables
```
TransformerPawnRef    : BP_TransformerPawn
SelectedActor         : StaticMeshActor
bGizmoActive          : Boolean
bIsDraggingGizmo      : Boolean
ActiveAxis            : String
SnapStep              : Float (default=10, 0=tự do)  ← chỉ dùng cho Translation
SnapAngle             : Float (default=15, 0=tự do)  ← chỉ dùng cho Rotation
SnapScale             : Float (default=0.1, 0=tự do) ← chỉ dùng cho Scale
ScaleSpeed            : Float (default=0.01)
DragPlaneX/Y/Z        : Float
InitialHitPoint       : Vector
InitialActorLocation  : Vector
IgnoredActors         : Array of Actor  ← không còn dùng cho gizmo trace
PreviousMousePosition : Vector2D
RotationSpeed         : Float (default=0.3)
AccumulatedRotation   : Float
```

---

## ActivateGizmo(TargetActor, TransformerPawn, TransformType)
```
SET SelectedActor = TargetActor
SET TransformerPawnRef = TransformerPawn

Branch bGizmoActive:
  TRUE (toggle off):
    Deselect All (TransformerPawnRef)
    SET bGizmoActive = False

  FALSE (activate):
    Branch IsValid(SelectedActor) → True:
      Set Transformation Type = TransformType (TransformerPawnRef)
      Select Actor (TransformerPawnRef, SelectedActor)
      Set Actor Location (TransformerPawnRef, Get Actor Location(SelectedActor))
      SET bGizmoActive = True
      DISABLE COLLISION:
        Get All Actors Of Class(StaticMeshActor) → NOT HasTag("FurnitureSpawned") → No Collision
        ← KHÔNG disable collision BaseGizmo — dùng GizmoTrace channel riêng
```

---

## DeactivateGizmo
```
Branch bGizmoActive == True:
  Deselect All → SET bGizmoActive = False → SET SelectedActor = None

← Luôn chạy (cả True và False):
RESTORE COLLISION:
  StaticMeshActor NOT FurnitureSpawned → Query And Physics
```

---

## OnMousePressed — v1.1 (T15: thêm RefreshOffsets cho Pivot)
```
1. LineTraceByChannel (GizmoTrace) → Hit Actor
   ← Dùng GizmoTrace channel — xuyên qua tất cả actors, chỉ hit gizmo
2. Cast Hit Actor → BaseGizmo:
   Failed → STOP
   Success:
     Get Hit Component Display Name → Split (In Str=".", From End) → Right S → SET ActiveAxis
     SET bIsDraggingGizmo = True
     Set Ignore Look Input = True
     GET Actor Location(SelectedActor) → SET InitialActorLocation
     Get Mouse Position → Make Vector2D → SET PreviousMousePosition
     Set DragPlane theo ActiveAxis:
       "XY Plane" → DragPlaneZ | "XZ Plane" → DragPlaneY | "YZ Plane" → DragPlaneX
       "X Axis Box" → DragPlaneY | "Y Axis Box" → DragPlaneX | "Z Axis Box" → DragPlaneX
       "XYZ_Sphere" → DragPlaneZ

     ← T15: capture relative transforms nếu đang drag Pivot (multi-select)
     Sequence → Then(cuối):
       Branch IsValid(SelectedActor):
         True →
           Cast SelectedActor To BP_PivotActor:
             Cast Success → Call RefreshOffsets (Target = As BP_PivotActor)
             Cast Failed  → (single actor, bỏ qua)
         False → (để trống)
```
> RefreshOffsets gọi ở đây là "chụp điểm tham chiếu" ngay trước khi pivot bắt đầu biến đổi. Idempotent — gọi khi không thực sự drag cũng vô hại.

---

## OnMouseReleased — v1.1
```
Branch bGizmoActive == True:
  True:
    Branch IsValid(SelectedActor):
      True:
        Branch bIsDraggingGizmo == True:
          True:
            Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → GET ActiveMode
            Branch ActiveMode == Rotate?
              True → Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Rotate")
              False →
                Branch ActiveMode == Scale?
                  True  → Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Scale")
                  False → Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Move")

← Luôn chạy (nằm ngoài tất cả Branch):
SET bIsDraggingGizmo = False  ← PHẢI sau CaptureSnapshot
SET ActiveAxis = ""
SET PreviousMousePosition = (0, 0)
SET AccumulatedRotation = 0
Set Ignore Look Input = False
```
> CaptureSnapshot duyệt tất cả actor tag "FurnitureSpawned" → tự động ghi đúng trạng thái mới của cả nhóm. Pivot (tag "FurniturePivot") KHÔNG bị lưu — đúng ý định.
> SET bIsDraggingGizmo PHẢI SAU CaptureSnapshot — nếu đảo ngược sẽ bug Undo.

---

## Event Tick — Hover Highlight
```
Branch IsValid(SelectedActor) → True:
  LineTrace (GizmoTrace, IgnoredActors=[SelectedActor])
  → Cast To BaseGizmo:
    Success → TransformerPawnRef → Trace by Channel
    Failed  → TransformerPawnRef → Clear Domain
```

---

## Event Tick — Movement
```
Branch IsValid(SelectedActor) AND bIsDraggingGizmo → True:
  Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → GET ActiveMode

  Sequence:
    Then 0 → Branch ActiveMode == Rotate?
      True → ROTATION LOGIC:
        CurrentPos - PreviousMousePosition → MouseDelta
        SET PreviousMousePosition = CurrentPos

        Switch ActiveAxis:
          "X Axis Box": MouseDelta.Y × Speed → AccumulatedRotation
            SnapAngle > 0 AND Abs(Acc) >= SnapAngle:
              Add World Rotation (Roll = Sign×SnapAngle) → AccumulatedRotation - SnapAmount
            Else: Add World Rotation (Roll = Acc) → Reset Acc = 0
          "Y Axis Box": MouseDelta.Y → Pitch (tương tự X)
          "Z Axis Box": MouseDelta.X → Yaw (tương tự X)

    Then 1 → Branch ActiveMode == Move?
      True → TRANSLATION LOGIC (ray-plane intersection):
        "X Axis Box": plane Y → compute HitX → Snap → Set Actor Location X
        "Y Axis Box": plane X → set Y
        "Z Axis Box": plane X → set Z
        "XY Plane": plane Z → set X+Y
        "XZ Plane": plane Y → set X+Z
        "YZ Plane": plane X → set Y+Z
        "XYZ_Sphere": plane Z → set X+Y

    Then 2 → Branch ActiveMode == Scale?
      True → SCALE LOGIC:
        CurrentPos - PreviousMousePosition → MouseDelta
        SET PreviousMousePosition = CurrentPos
        Get Actor Scale 3D (SelectedActor) → Break Vector → X, Y, Z

        Switch ActiveAxis:
          "X Axis Box": MouseDelta.X × ScaleSpeed + CurrentScale.X → RawScale
            SnapScale > 0: Round(Raw/Snap) × Snap → NewScale → Set Actor Scale3D (NewScale, Y, Z)
          "Y Axis Box": MouseDelta.X → Y axis (tương tự X)
          "Z Axis Box": MouseDelta.Y × -1 → Z axis (tương tự X)
          "XYZ_Sphere": Average(X,Y,Z) + MouseDelta.X × ScaleSpeed → RawScale → Snap → Set Actor Scale3D (New, New, New)
```

---

## Lưu ý khi tích hợp project tổng
- **GizmoTrace Channel** — custom trace channel chỉ gizmo block, tất cả actors khác ignore
- Không cần IgnoredActors list nữa — GizmoTrace xuyên qua tất cả
- Gizmo collision KHÔNG bị disable/enable trong ActivateGizmo/DeactivateGizmo
- Gizmo material cần tăng **Emissive x1000** nếu project dùng Lumen

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 23/04/2026 | Logic gốc (fragment 16/04 — OnMouseReleased dùng PlayerController cast) |
| 1.1 | 05/06/2026 — 20:00 ICT | T15: OnMousePressed thêm Cast → BP_PivotActor → RefreshOffsets. OnMouseReleased đổi sang Get All Actors(InputManager) → Cast → GET ActiveMode (thay Get Player Controller → BP_FoffPlayerController). |
