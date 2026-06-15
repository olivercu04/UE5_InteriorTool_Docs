# WBP_MeshControls
**Phiên bản:** 1.2 | **Cập nhật:** 04/06/2026 — 15:30 ICT | Persistent Toolbar — luôn hiển thị

> **v1.2 (Sprint 1 T8 + T14 — Multi-Select):** bind `OnSelectionChanged` → ẩn BTN_Info/BTN_Replace khi chọn ≥2 đồ; BTN_Delete hỗ trợ multi-delete; thêm `ET_SelectionCount` hiện "✦ N vật thể". Toolbar KHÔNG tự ẩn sau delete (persistent).

---

## Variables
```
ActiveModeButton     : Button (Object Ref)
In Color and Opacity : LinearColor (0.2, 0.6, 1.0, 1.0)
DetailPopupRef       : WBP_DetailPopup   ← đã chuyển sang BP_FurnitureInputManager
```

---

## Layout
```
[↖Select] [✛Move] [↺Rotate] [⊡Scale] | [🗑Delete] [ℹInfo] [↔Replace]   [✦ N vật thể]  ← ET_SelectionCount (Collapsed mặc định)
[── SnapStep ──]  [── SnapAngle ──]  [── SnapScale ──]
```

---

## Event Construct — v1.2
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → InputRef
→ SET ActiveMode = Select → RefreshButtonState(Select)

← v1.2: bind multi-select:
InputRef → Bind Event to OnSelectionChanged → Event = OnSelectionChangedHandler
```

---

## OnSelectionChangedHandler (Custom Event) — v1.2 (T8 + T14)
**Inputs:** `Actors : Array of BP_FurnitureActor`, `Primary : BP_FurnitureActor`

```
GET LENGTH Actors →

← T8: ẩn/hiện BTN_Info + BTN_Replace (mỗi Set Visibility 1 target):
Branch Length > 1:
  True (multi)  → Set Visibility(BTN_Info, Hidden)  → Set Visibility(BTN_Replace, Hidden)
  False (0/1)   → Set Visibility(BTN_Info, Visible) → Set Visibility(BTN_Replace, Visible)

← T14: ET_SelectionCount:
Branch Length >= 2:
  True →
    Set Visibility(ET_SelectionCount, Visible)
    "✦ " + ToString(Length) + " vật thể" → ToText → Set Text(ET_SelectionCount)
  False →
    Set Visibility(ET_SelectionCount, Collapsed)
```

**Lưu ý:** mỗi node `Set Visibility` chỉ nhận 1 Target → cần 2 node riêng cho BTN_Info và BTN_Replace ở mỗi nhánh.

---

## Mode Buttons (BTN_Select / Move / Rotate / Scale) — v1.1 (không đổi)
Pattern chung: toggle off nếu đang active; nếu không → SET ActiveMode + DeactivateGizmo (TRƯỚC) + ActivateGizmo.
```
BTN_Select → SET Select → DeactivateGizmo
BTN_Move   → SET Move   → ActivateGizmo(SelectedFurnitureActor, TransformerPawn, Translation)
BTN_Rotate → SET Rotate → DeactivateGizmo → ActivateGizmo(..., Rotation)
BTN_Scale  → SET Scale  → DeactivateGizmo → ActivateGizmo(..., Scale)
```
**⚠️ Lưu ý multi-select:** mode buttons hiện gọi ActivateGizmo với `SelectedFurnitureActor` (= primary). Khi đang chọn ≥2 đồ, đổi mode sẽ gắn gizmo lên primary đơn lẻ, không phải pivot. Nếu cần đổi mode giữ multi-gizmo → gọi `UpdateGizmo` của InputManager thay vì ActivateGizmo trực tiếp (cân nhắc khi làm T15 / Sprint sau).

---

## ET_SnapStep / ET_SnapAngle / ET_SnapScale (không đổi)
```
ET_SnapStep  Default="10"  → Text To Float → SET SnapStep (GizmoControllerRef)   | 0 = free
ET_SnapAngle Default="15"  → Text To Float → SET SnapAngle (GizmoControllerRef)  | 0 = free
ET_SnapScale Default="0.1" → Text To Float → SET SnapScale (GizmoControllerRef)  | 0 = free
```

---

## BTN_Delete OnClicked — v1.2 MULTI
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → InputRef

GET SelectedActors → LENGTH →

Branch Length == 0:
  True → Return (không làm gì)
  False ↓

Branch Length == 1:
  True (single — giữ logic cũ):
    Destroy Actor(SelectedFurnitureActor)   ← TRƯỚC CaptureSnapshot
    CaptureSnapshot("Delete")
    GET DetailPopupRef → IsValid → Remove from Parent → SET DetailPopupRef = None
    SET SelectedFurnitureActor = None → DeactivateGizmo
  False (multi — Length >= 2):
    ForEach SelectedActors (Actor):
      Branch IsValid(Actor): True → Destroy Actor(Actor)
    ForEach Completed →
      Call DeselectAll (InputRef)
      Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("DeleteMulti")
```

**Thay đổi v1.2:**
- Branch theo LENGTH SelectedActors (0 / 1 / ≥2).
- Multi: ForEach Destroy (IsValid guard) → DeselectAll → CaptureSnapshot("DeleteMulti").
- **KHÔNG còn `Remove from Parent (WBP_MeshControls)`** — toolbar persistent, không tự ẩn sau delete (quyết định 04/06).
- Confirmation dialog cho >3 đồ: chưa làm (T14 đơn giản hóa, để Sprint sau nếu cần).

---

## BTN_Info OnClicked (v1.1 — không đổi)
```
Cast InputManager → GET DetailPopupRef → IsValid → Remove from Parent
GET SelectedFurnitureActor → Cast → GET DAPath → Load Asset Blocking → Cast DA_FurnitureItem
Create WBP_DetailPopup → Add to Viewport → Set Position (mouse + offset)
SET DetailPopupRef = new popup → Call InitPopup(DA, bFromScene=True)
```
**Lưu ý:** BTN_Info ẩn khi multi-select (OnSelectionChangedHandler) → chỉ dùng khi chọn 1 đồ.

---

## BTN_Replace OnClicked (v1.1 — không đổi)
Toggle Replace mode. Trigger 1: SET MeshToReplace = SelectedFurnitureActor → EnterReplaceMode → FilterByFolderPathWithUI. Trigger 2 (đang Replace): ExitReplaceMode.
**Lưu ý:** ẩn khi multi-select → chỉ dùng khi chọn 1 đồ.

---

## UpdateDetailPopup (Custom Event — v1.1, không đổi)
```
Cast InputManager → GET DetailPopupRef → IsValid →
  GET SelectedFurnitureActor → IsValid → Cast → GET DAPath → Load Asset Blocking → DA
  → Call InitPopup(DetailPopupRef, DA, bFromScene=True)
```

---

## RefreshButtonState(ActiveMode) (không đổi)
Switch on ActiveMode → highlight nút tương ứng, white các nút khác.

---

## Key Notes (v1.2)
- **OnSelectionChanged bind ở Event Construct** → OnSelectionChangedHandler tự cập nhật khi selection đổi.
- **BTN_Info + BTN_Replace ẩn khi ≥2 đồ** (chỉ thao tác được trên 1 đồ).
- **ET_SelectionCount** hiện "✦ N vật thể" khi ≥2, Collapsed khi 0/1.
- **BTN_Delete** xử lý cả single (logic cũ) lẫn multi (ForEach Destroy + DeselectAll).
- **Toolbar persistent** — không tự Remove sau delete.
- **Mode buttons** vẫn dùng SelectedFurnitureActor (primary) — xem cảnh báo multi-select ở mục Mode Buttons.

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 22/04/2026 | Logic gốc |
| 1.1 | 25/05/2026 — 17:29 ICT | BTN_Replace toggle + gọi EnterReplaceMode |
| 1.2 | 04/06/2026 — 15:30 ICT | **Multi-Select (T8 + T14):** bind OnSelectionChanged + OnSelectionChangedHandler (ẩn BTN_Info/Replace khi ≥2); BTN_Delete multi (ForEach Destroy + DeselectAll); ET_SelectionCount "✦ N vật thể"; bỏ Remove from Parent sau delete |
