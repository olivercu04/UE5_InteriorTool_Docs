# WBP_MeshControls
**Phiên bản:** 1.2 | **Cập nhật:** 05/06/2026 — 20:00 ICT | Persistent Toolbar — luôn hiển thị trên màn hình

---

## Variables
```
ActiveModeButton     : Button (Object Ref)
In Color and Opacity : LinearColor (0.2, 0.6, 1.0, 1.0)
DetailPopupRef       : WBP_DetailPopup  ← đã chuyển sang BP_FurnitureInputManager
```

---

## Layout
```
[↖Select] [✛Move] [↺Rotate] [⊡Scale] | [🗑Delete] [ℹInfo] [↔Replace]
[── SnapStep ──]  [── SnapAngle ──]  [── SnapScale ──] ← luôn visible
```

---

## Event Construct
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
→ SET ActiveMode = Select → RefreshButtonState(Select)
```

---

## Pattern BTN_Select
```
Branch ActiveModeButton == BTN_Select? (toggle off)
  True: white → SET None → Select → DeactivateGizmo
  False:
    Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
    SET BTN_Select active → SET ActiveMode = Select → DeactivateGizmo
```

---

## Pattern BTN_Move — v1.2
```
Branch ActiveModeButton == BTN_Move? (toggle off)
  True: white → SET None → Select → DeactivateGizmo
  False:
    SET BTN_Move active → SET ActiveMode = Move

    Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → InputRef
    GET SelectedActors (InputRef) → LENGTH
    Branch Length >= 2?
      True  → TargetActor = GET GizmoPivotActor (InputRef)
      False → TargetActor = GET SelectedFurnitureActor (InputRef)

    ActivateGizmo(TargetActor, TransformerPawn, Translation)
```

---

## Pattern BTN_Rotate — v1.2
```
Branch ActiveModeButton == BTN_Rotate? (toggle off)
  True: white → SET None → Select → DeactivateGizmo
  False:
    SET BTN_Rotate active → SET ActiveMode = Rotate
    DeactivateGizmo  ← PHẢI trước ActivateGizmo

    Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → InputRef
    GET SelectedActors (InputRef) → LENGTH
    Branch Length >= 2?
      True  → TargetActor = GET GizmoPivotActor (InputRef)
      False → TargetActor = GET SelectedFurnitureActor (InputRef)

    ActivateGizmo(TargetActor, TransformerPawn, Rotation)
```

---

## Pattern BTN_Scale — v1.2
```
Branch ActiveModeButton == BTN_Scale? (toggle off)
  True: white → SET None → Select → DeactivateGizmo
  False:
    SET BTN_Scale active → SET ActiveMode = Scale
    DeactivateGizmo  ← PHẢI trước ActivateGizmo

    Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → InputRef
    GET SelectedActors (InputRef) → LENGTH
    Branch Length >= 2?
      True  → TargetActor = GET GizmoPivotActor (InputRef)
      False → TargetActor = GET SelectedFurnitureActor (InputRef)

    ActivateGizmo(TargetActor, TransformerPawn, Scale)
```

---

## ET_SnapStep
```
Default = "10" | OnTextCommitted → Text To Float → SET SnapStep (GizmoControllerRef)
0 = free movement
```

---

## ET_SnapAngle
```
Default = "15" | OnTextCommitted → Text To Float → SET SnapAngle (GizmoControllerRef)
0 = free rotation
```

---

## ET_SnapScale
```
Default = "0.1" | OnTextCommitted → Text To Float → SET SnapScale (GizmoControllerRef)
0 = free scale
```

---

## BTN_Delete
```
IsValid(TargetActor):
  Destroy Actor              ← PHẢI trước CaptureSnapshot
  CaptureSnapshot("Delete")
  Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
  → GET DetailPopupRef → Branch IsValid?
    True → Remove from Parent → SET DetailPopupRef = None
  SET SelectedFurnitureActor = None
  DeactivateGizmo
  Remove from Parent (WBP_MeshControls)
```

---

## BTN_Info OnClicked
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → FurnitureInputRef

GET DetailPopupRef (FurnitureInputRef)
Branch IsValid(DetailPopupRef)?
  True → Remove from Parent (DetailPopupRef)

GET SelectedFurnitureActor → Cast BP_FurnitureActor → GET DAPath
Load Asset Blocking → Cast To DA_FurnitureItem

Create WBP_DetailPopup → Add to Viewport
Get Player Controller → Get Mouse Position → Make Vector2D(X, Y+10)
Set Position In Viewport + SET PopupPosition (DetailPopup)

Cast FurnitureInputRef → SET DetailPopupRef = new popup
Call InitPopup (DA, bFromScene=True)
```

---

## BTN_Replace OnClicked — v1.1 (toggle + EnterReplaceMode)
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → FurnitureInputRef

← v1.1: Toggle — nếu đang Replace mode → thoát
Branch bIsReplaceMode == True (FurnitureInputRef):
  T → SET bIsReplaceMode = False (FurnitureInputRef)
      SET MeshToReplace = None (FurnitureInputRef)
      Get Game Instance → Cast Foff_GameInstance → GET FurnitureInventoryRef
      Branch IsValid(FurnitureInventoryRef)?
        True → Cast WBP_FurnitureInventory → Call ExitReplaceMode
      Return   ← thoát, không mở inventory

  F → (chưa ở Replace mode → bật lên)
      SET MeshToReplace = GET SelectedFurnitureActor (FurnitureInputRef)

      GET SelectedFurnitureActor → Cast BP_FurnitureActor → GET DAPath
      Load Asset Blocking → Cast To DA_FurnitureItem → GET MeshFolderPath

      Get Game Instance → Cast Foff_GameInstance → GET FurnitureInventoryRef
      Branch IsValid(FurnitureInventoryRef)?
        True:
          Branch IsValid(FurnitureInventoryRef)?
            True → Cast WBP_FurnitureInventory → Call EnterReplaceMode
                   → FilterByFolderPathWithUI(MeshFolderPath)
        False:
          Create WBP_FurnitureInventory → Add to Viewport
          Cast Foff_GameInstance → SET FurnitureInventoryRef
          Cast WBP_FurnitureInventory → Call EnterReplaceMode
          FilterByFolderPathWithUI(MeshFolderPath)

      ← v1.1: SET bIsReplaceMode = True đã nằm trong EnterReplaceMode
```

---

## UpdateDetailPopup (Custom Event)
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
→ GET DetailPopupRef
→ Branch IsValid(DetailPopupRef)?
  True:
    GET SelectedFurnitureActor → Branch IsValid?
      True → Cast BP_FurnitureActor → GET DAPath
              Load Asset Blocking → Cast To DA_FurnitureItem
              Call InitPopup (Target=DetailPopupRef, DA=..., bFromScene=True)
```

---

## RefreshButtonState(ActiveMode)
```
Switch on ActiveMode:
  Select → highlight BTN_Select, white others
  Move   → highlight BTN_Move, white others
  Rotate → highlight BTN_Rotate, white others
  Scale  → highlight BTN_Scale, white others
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 22/04/2026 | Logic gốc |
| 1.1 | 25/05/2026 — 17:29 ICT | BTN_Replace toggle + gọi EnterReplaceMode |
| 1.2 | 05/06/2026 — 20:00 ICT | T15: BTN_Move/Rotate/Scale kiểm tra `SelectedActors.Length >= 2` → dùng GizmoPivotActor khi multi-select, SelectedFurnitureActor khi single. Fix bug gizmo nhảy về đồ đơn khi chuyển mode trong multi-select. |
