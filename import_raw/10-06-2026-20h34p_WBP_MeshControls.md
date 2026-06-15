# WBP_MeshControls
**Phiên bản:** 1.4 | **Cập nhật:** 10/06/2026 — 20:34 ICT | Persistent Toolbar — luôn hiển thị trên màn hình

> **v1.4 (Sprint 3 + Refactor):** thêm **Selection Info Bar** đọc Groups (handler `OnSelectionChanged` → "📦 Nhóm N (count)" khi group, "N vật thể" khi multi, ẩn khi < 2 đồ). **BTN_Replace** migrate `MeshToReplace`(single, ĐÃ XÓA) → gọi `StartReplaceMode(SelectedActors)` (multi). Đọc kèm `Sprint3_Regression_DualDispatcher_Log.md`.

> **v1.3 (Sprint 2 prep):** BTN_Replace trỏ về function chung `StartReplaceMode` trong InputManager (multi). v1.2 (T15 05/06): BTN_Move/Rotate/Scale dùng GizmoPivotActor khi multi-select.

---

## Variables
```
ActiveModeButton     : Button (Object Ref)
In Color and Opacity : LinearColor (0.2, 0.6, 1.0, 1.0)
DetailPopupRef       : WBP_DetailPopup  ← đã chuyển sang BP_FurnitureInputManager
```

### Info Bar (v1.4 — Sprint 3 T10)
```
TXT_SelectionInfo : TextBlock   ← hiện "📦 Nhóm N (count)" / "N vật thể"; ẩn khi < 2 đồ
HB_SelectionInfo  : HorizontalBox (hoặc Border)  ← container info bar, Collapsed khi single/none
```

---

## Layout
```
[↖Select] [✛Move] [↺Rotate] [⊡Scale] | [🗑Delete] [ℹInfo] [↔Replace]
[── SnapStep ──]  [── SnapAngle ──]  [── SnapScale ──] ← luôn visible
```

---

## Event Construct (v1.4)
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → InputRef
→ SET ActiveMode = Select → RefreshButtonState(Select)
← v1.4: bind info bar
→ Bind Event to OnSelectionChanged (Target=InputRef) → OnSelectionChangedInfoBar
→ Set Visibility(HB_SelectionInfo, Collapsed)   ← ẩn ban đầu (chưa chọn gì)
```
⚠️ Bind PHẢI ở Event Construct (chạy 1 lần lúc tạo widget). Info bar dùng CHUNG dispatcher `OnSelectionChanged` với inventory — không tạo dispatcher riêng (single source of truth).

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

## Pattern BTN_Move (v1.2 — T15 multi)
```
Branch ActiveModeButton == BTN_Move? (toggle off)
  True: white → SET None → Select → DeactivateGizmo
  False:
    SET BTN_Move active → SET ActiveMode = Move
    DeactivateGizmo  ← v1.2: PHẢI trước ActivateGizmo (chống gizmo nhảy về đồ đơn khi đổi mode lúc multi)
    ← v1.2: chọn target theo số lượng
    Branch (SelectedActors.Length >= 2):
      True  → ActivateGizmo(GizmoPivotActor, TransformerPawn, Translation)   ← multi → pivot
      False → ActivateGizmo(SelectedFurnitureActor, TransformerPawn, Translation)  ← single
```

---

## Pattern BTN_Rotate (v1.2 — T15 multi)
```
Branch ActiveModeButton == BTN_Rotate? (toggle off)
  True: white → SET None → Select → DeactivateGizmo
  False:
    SET BTN_Rotate active → SET ActiveMode = Rotate
    DeactivateGizmo  ← PHẢI trước ActivateGizmo
    Branch (SelectedActors.Length >= 2):
      True  → ActivateGizmo(GizmoPivotActor, TransformerPawn, Rotation)
      False → ActivateGizmo(SelectedFurnitureActor, TransformerPawn, Rotation)
```

---

## Pattern BTN_Scale (v1.2 — T15 multi)
```
Branch ActiveModeButton == BTN_Scale? (toggle off)
  True: white → SET None → Select → DeactivateGizmo
  False:
    SET BTN_Scale active → SET ActiveMode = Scale
    DeactivateGizmo  ← PHẢI trước ActivateGizmo
    Branch (SelectedActors.Length >= 2):
      True  → ActivateGizmo(GizmoPivotActor, TransformerPawn, Scale)
      False → ActivateGizmo(SelectedFurnitureActor, TransformerPawn, Scale)
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

## BTN_Replace OnClicked — v1.4 (StartReplaceMode multi)
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → InputRef
→ Call StartReplaceMode (Target=InputRef, TargetActors = InputRef.SelectedActors)
```
> **v1.4:** thay toàn bộ logic toggle/inline cũ bằng 1 call `StartReplaceMode(SelectedActors)`. Function này (trong BP_FurnitureInputManager) tự xử lý:
> - **Toggle OFF** (đang ở replace mode): SET bIsReplaceMode=False + **CLEAR MeshesToReplace** + ExitReplaceMode.
> - **Toggle ON**: SET MeshesToReplace = TargetActors (array), folder nav theo PrimarySelectedActor → EnterReplaceMode + FilterByFolderPathWithUI.
>
> **ĐÃ XÓA:** mọi tham chiếu `MeshToReplace` (single) — biến này đã bị xóa hẳn. Replace giờ MULTI: chọn nhiều đồ (hoặc Select Similar / group) → Replace → đổi mesh tất cả đồ đang chọn.

**Lý do gom về StartReplaceMode:** trước đây BTN_Replace (MeshControls), CB_Replace (context menu), BTN_ChangeMesh (DetailPopup) mỗi nơi tự SET state replace → dễ lệch. Gom 1 function = single source of truth, sửa 1 chỗ áp dụng cả 3 call site.

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

## OnSelectionChangedInfoBar(Actors, Primary) — v1.4 (Sprint 3 T10)
> Bound từ `InputManager.OnSelectionChanged` (dispatcher selection duy nhất). Cập nhật info bar theo selection + group.
```
Branch (Actors.Length >= 2):                          ← info bar CHỈ hiện khi >= 2 đồ
  False → Set Visibility(HB_SelectionInfo, Collapsed)  ← single/none → ẩn
  True  →
    Set Visibility(HB_SelectionInfo, Visible)
    ← kiểm tra Primary có thuộc group không
    Branch IsValid(Primary):                            ← guard (Primary có thể None khi rỗng — nhưng đã chặn bởi Length>=2)
      True →
        Cast Primary → BP_FurnitureActor → GET GroupID → LocalGID
        Branch (LocalGID != ""):
          True (đang chọn group) →
            Get All Actors Of Class(InputManager) → Get(0) → Call FindGroupData(LocalGID) → (S_GroupData, _, bFound)
            Branch bFound:
              True → SET Text(TXT_SelectionInfo, "📦 " + GroupData.GroupName + " (" + Actors.Length + ")")
              False → SET Text(TXT_SelectionInfo, Actors.Length + " vật thể")
          False (multi đồ rời) →
            SET Text(TXT_SelectionInfo, Actors.Length + " vật thể")
```
**Lưu ý:** Claude từng nhầm tưởng info bar hiện cả khi single — KHÔNG. Chỉ hiện khi **>= 2 đồ**. Single/none → Collapsed.
**Debug đã dọn:** print `InfoBar: GroupID` + `InfoBar: Groups.Length` từng dùng trace bug undo group, đã xóa sau khi fix.

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 22/04/2026 | Logic gốc |
| 1.1 | 25/05/2026 — 17:29 ICT | BTN_Replace toggle (Trigger 2 thoát Replace mode) + gọi EnterReplaceMode thay SET trực tiếp |
| 1.2 | 05/06/2026 — 20:00 ICT | T15: BTN_Move/Rotate/Scale kiểm tra `SelectedActors.Length >= 2` → dùng GizmoPivotActor khi multi-select, SelectedFurnitureActor khi single. Fix gizmo nhảy về đồ đơn khi đổi mode trong multi-select. |
| 1.3 | 08/06/2026 | Sprint 2 prep: BTN_Replace trỏ về function chung StartReplaceMode (multi) trong InputManager. |
| 1.4 | 10/06/2026 — 20:34 ICT | **Sprint 3 + Refactor.** Vars info bar (TXT_SelectionInfo, HB_SelectionInfo). Event Construct bind `OnSelectionChanged` → `OnSelectionChangedInfoBar` + ẩn info bar ban đầu. Handler info bar: hiện "📦 GroupName (N)" khi group (FindGroupData), "N vật thể" khi multi rời, Collapsed khi < 2 đồ. BTN_Replace gom hẳn về `StartReplaceMode(SelectedActors)`, XÓA mọi tham chiếu MeshToReplace (single đã xóa). |
