# BP_GizmoController — OnMouseReleased
**Cập nhật:** 16/04/2026 — 21:00:14 ICT
 
---
 
## OnMouseReleased — Full Flow
 
```
OnMouseReleased:
 
Branch bGizmoActive == True:
  True:
    Branch IsValid(SelectedActor):
      True:
        Branch bIsDraggingGizmo == True:
          True:
            Get Player Controller → Cast BP_FoffPlayerController → GET ActiveMode
            Branch ActiveMode == Rotate?
              True:
                Get All Actors Of Class(BP_UndoManager) → Get(0)
                → CaptureSnapshot("Rotate")
              False:
                Branch ActiveMode == Scale?
                  True:
                    Get All Actors Of Class(BP_UndoManager) → Get(0)
                    → CaptureSnapshot("Scale")
                  False:
                    Get All Actors Of Class(BP_UndoManager) → Get(0)
                    → CaptureSnapshot("Move")
 
← Luôn chạy (nằm ngoài tất cả Branch — chạy dù bGizmoActive True hay False):
SET bIsDraggingGizmo = False  ← PHẢI sau CaptureSnapshot
SET ActiveAxis = ""
SET PreviousMousePosition = (0, 0)
SET AccumulatedRotation = 0
Set Ignore Look Input = False
```
 
---
 
## Lưu ý quan trọng
 
- **CaptureSnapshot TRƯỚC SET bIsDraggingGizmo = False** — nếu đảo ngược sẽ bug Undo
- **SET nodes luôn chạy** — không nằm trong bất kỳ branch nào
- **Branch IsValid(SelectedActor)** — tránh crash khi actor bị destroy trước khi thả chuột
- **Get All Actors Of Class(BP_UndoManager) → Get(0)** — gọi trước mỗi CaptureSnapshot
 