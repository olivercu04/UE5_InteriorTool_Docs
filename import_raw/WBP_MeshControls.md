# WBP_MeshControls
**Phiên bản:** 1.5 (BẢN HỢP NHẤT — merge v1.4 + patch v1.5) | **Cập nhật:** 11/06/2026 | Persistent Toolbar — luôn hiển thị trên màn hình

> **v1.5 (Sprint 4 T5 — Edit Mode UI):** BTN_EnterEdit, HB_EditModeBar (breadcrumb + BTN_ExitFull), bind OnEditModeChanged.
> **v1.4 (Sprint 3 + Refactor):** Selection Info Bar đọc Groups (handler OnSelectionChanged → "📦 Nhóm N (count)" khi group, "N vật thể" khi multi, ẩn khi <2 đồ). BTN_Replace migrate sang StartReplaceMode(SelectedActors) multi — XÓA mọi tham chiếu MeshToReplace single.
> **v1.2 (T15):** BTN_Move/Rotate/Scale dùng GizmoPivotActor khi multi-select.

---

## Variables
```
ActiveModeButton     : Button (Object Ref)
In Color and Opacity : LinearColor (0.2, 0.6, 1.0, 1.0)
DetailPopupRef       : WBP_DetailPopup  ← đã chuyển sang BP_FurnitureInputManager
```

### Info Bar (v1.4 — Sprint 3 T10)
```
TXT_SelectionInfo : TextBlock        ← "📦 Nhóm N (count)" / "N vật thể"; ẩn khi < 2 đồ
HB_SelectionInfo  : HorizontalBox    ← container, Collapsed khi single/none
```

### Edit Mode (v1.5 — Sprint 4 T5)
```
BTN_EnterEdit    : Button         ← "✏️ Chỉnh nhóm". Collapsed mặc định. Hiện khi Primary có GroupID.
HB_EditModeBar   : HorizontalBox  ← Collapsed mặc định. Hiện khi đang edit mode. RIÊNG với HB_SelectionInfo
  TXT_EditBreadcrumb : TextBlock  ← "✏️ Đang chỉnh: Nhóm 1 › Nhóm 2"
  BTN_ExitFull       : Button     ← "✖ Thoát" → ExitEditModeFull
```
> ⚠ HB_EditModeBar KHÔNG dùng chung HB_SelectionInfo — edit mode có thể active khi chọn 0/1 đồ (info bar lúc đó Collapsed).
> Sprint4_Execution T5 còn nhắc `BTN_ExitOneLevel` ("↑" → ExitEditModeOneLevel) — patch v1.5 chỉ ghi BTN_ExitFull. **⚠ KIỂM TRA BP:** nếu có BTN_ExitOneLevel thì bổ sung dòng OnClicked tương ứng vào doc.

---

## Layout
```
[↖Select] [✛Move] [↺Rotate] [⊡Scale] | [🗑Delete] [ℹInfo] [↔Replace]
[TXT_SelectionInfo (HB_SelectionInfo)]  [BTN_EnterEdit ✏️]
[HB_EditModeBar: "✏️ Đang chỉnh: ..." | ✖ Thoát]
[── SnapStep ──]  [── SnapAngle ──]  [── SnapScale ──] ← luôn visible
```

---

## Event Construct (v1.4 + v1.5)
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → InputRef
→ SET ActiveMode = Select → RefreshButtonState(Select)
← v1.4: bind info bar
→ Bind Event to OnSelectionChanged (Target=InputRef) → OnSelectionChangedInfoBar
→ Set Visibility(HB_SelectionInfo, Collapsed)
← v1.5: bind edit mode
→ Bind Event to OnEditModeChanged (Target=InputRef) → OnEditModeChangedInfoBar
→ Set Visibility(HB_EditModeBar, Collapsed)
→ Set Visibility(BTN_EnterEdit, Collapsed)
```
⚠ Bind PHẢI ở Event Construct. Info bar dùng CHUNG dispatcher OnSelectionChanged — không tạo dispatcher riêng (single source of truth).

---

## Pattern BTN_Select
```
Branch ActiveModeButton == BTN_Select? (toggle off)
  True: white → SET None → Select → DeactivateGizmo
  False: Get All Actors Of Class(InputManager) → Get(0) → Cast
         SET BTN_Select active → SET ActiveMode = Select → DeactivateGizmo
```

## Pattern BTN_Move (v1.2 — multi)
```
Branch ActiveModeButton == BTN_Move? (toggle off)
  True: white → SET None → Select → DeactivateGizmo
  False:
    SET BTN_Move active → SET ActiveMode = Move
    DeactivateGizmo  ← PHẢI trước ActivateGizmo (chống gizmo nhảy về đồ đơn khi đổi mode lúc multi)
    Branch (SelectedActors.Length >= 2):
      True  → ActivateGizmo(GizmoPivotActor, TransformerPawn, Translation)    ← multi → pivot
      False → ActivateGizmo(SelectedFurnitureActor, TransformerPawn, Translation)
```

## Pattern BTN_Rotate (v1.2 — multi)
```
Như BTN_Move, thay: SET ActiveMode = Rotate; ActivateGizmo(..., Rotation)
```

## Pattern BTN_Scale (v1.2 — multi)
```
Như BTN_Move, thay: SET ActiveMode = Scale; ActivateGizmo(..., Scale)
```

---

## ET_SnapStep / ET_SnapAngle / ET_SnapScale
```
Default = "10" / "15" / "0.1" | OnTextCommitted → Text To Float → SET SnapStep/SnapAngle/SnapScale (GizmoControllerRef)
0 = free
```

---

## BTN_Delete
```
IsValid(TargetActor):
  Destroy Actor              ← PHẢI trước CaptureSnapshot
  CaptureSnapshot("Delete")
  Get All Actors Of Class(InputManager) → Get(0) → Cast
  → GET DetailPopupRef → IsValid → Remove from Parent → SET None
  SET SelectedFurnitureActor = None → DeactivateGizmo → Remove from Parent (self)
```
> ⚠ KIỂM TRA BP: flow này là bản single (v1.1). Sau Sprint 1 multi-select, BTN_Delete nhiều khả năng đã trỏ về `DeleteSelected` (InputManager) như CB_Delete của context menu. Đối chiếu node graph thật rồi cập nhật mục này.

---

## BTN_Info OnClicked (legacy — Load Blocking)
```
Get All Actors Of Class(InputManager) → Get(0) → Cast → FurnitureInputRef
GET DetailPopupRef → IsValid → Remove from Parent
GET SelectedFurnitureActor → Cast → GET DAPath → Load Asset Blocking → Cast DA_FurnitureItem
Create WBP_DetailPopup → Add to Viewport → Set Position In Viewport(chuột + Y+10) + SET PopupPosition
SET DetailPopupRef = popup → Call InitPopup(DA, bFromScene=True)
```
> ⚠ SPRINT D: sau D.T8 đường này nên đọc qua RowName→DT thay DAPath (vi phạm R1/R5 hiện tại — legacy chấp nhận tạm).

---

## BTN_Replace OnClicked (v1.4)
```
Get All Actors Of Class(InputManager) → Get(0) → Cast → FurnitureInputRef
Branch bIsReplaceMode == True:
  True  → thoát Replace: SET bIsReplaceMode=False, CLEAR MeshesToReplace,
          GameInstance → FurnitureInventoryRef → IsValid → ExitReplaceMode → Return
  False → Call StartReplaceMode(SelectedActors) (InputManager — multi)
```
> v1.4 XÓA mọi tham chiếu MeshToReplace single. Flow chi tiết StartReplaceMode: xem BP_FurnitureInputManager / Blueprint_Logic (Sprint 2 T9).

---

## UpdateDetailPopup (Custom Event)
```
Get All Actors Of Class(InputManager) → Get(0) → Cast → GET DetailPopupRef → IsValid:
  True → GET SelectedFurnitureActor → IsValid → Cast → GET DAPath
         → Load Asset Blocking → Cast DA_FurnitureItem → InitPopup(DetailPopupRef, DA, bFromScene=True)
```

---

## RefreshButtonState(ActiveMode)
```
Switch on ActiveMode: Select/Move/Rotate/Scale → highlight nút tương ứng, white các nút khác
```

---

## OnSelectionChangedInfoBar(Actors, Primary) — handler (v1.4 + v1.5)
> Dùng Sequence. Primary = PARAMETER của handler, không phải class variable.

**Then 0 — info bar text (v1.4):**
```
Branch (Actors.Length >= 2):                          ← CHỈ hiện khi >= 2 đồ
  False → Set Visibility(HB_SelectionInfo, Collapsed)
  True  →
    Set Visibility(HB_SelectionInfo, Visible)
    Branch IsValid(Primary):
      True →
        Cast Primary → GET GroupID → LocalGID
        Branch (LocalGID != ""):
          True  → Get All Actors Of Class(InputManager)[0] → FindGroupData(LocalGID) → bFound:
                    True  → SET Text(TXT_SelectionInfo, "📦 " + GroupName + " (" + Actors.Length + ")")
                    False → SET Text(TXT_SelectionInfo, Actors.Length + " vật thể")
          False → SET Text(TXT_SelectionInfo, Actors.Length + " vật thể")
```
**Lưu ý:** info bar KHÔNG hiện khi single — chỉ >= 2 đồ (từng nhầm).

**Then 2 — BTN_EnterEdit visibility (v1.5):**
```
Branch IsValid(Primary):
  True  → Cast → GET GroupID → Branch (GroupID != ""):
            True  → Set Visibility(BTN_EnterEdit, Visible)
            False → Set Visibility(BTN_EnterEdit, Collapsed)
  False → Set Visibility(BTN_EnterEdit, Collapsed)
```
> ⚠ KIỂM TRA BP: patch ghi "Then 2" — xác nhận Then 1 có nội dung gì (hoặc trống) trong node graph thật, ghi bổ sung nếu có.

---

## OnEditModeChangedInfoBar(bActive, GroupID) — handler (v1.5)
```
Branch(bActive):
  True  → Set Visibility(HB_EditModeBar, Visible)
          Get All Actors Of Class(InputManager)[0] → GetEditBreadcrumb → BreadStr
          SetText(TXT_EditBreadcrumb, "✏️ Đang chỉnh: " + BreadStr)
  False → Set Visibility(HB_EditModeBar, Collapsed)
```
> False branch dead-end OK (chỉ hide, không có logic sau).

---

## OnClicked (v1.5)
```
BTN_EnterEdit.OnClicked: Get All Actors Of Class(InputManager)[0] → TryEnterEditFromSelection
BTN_ExitFull.OnClicked : Get All Actors Of Class(InputManager)[0] → ExitEditModeFull
```

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 22/04/2026 | Logic gốc |
| 1.1 | 25/05/2026 | BTN_Replace toggle + EnterReplaceMode |
| 1.2 | 05/06/2026 | T15: Move/Rotate/Scale check Length>=2 → GizmoPivotActor khi multi |
| 1.3 | 08/06/2026 | Sprint 2 prep: BTN_Replace → StartReplaceMode (multi) |
| 1.4 | 10/06/2026 | Sprint 3 + Refactor: Info bar (TXT/HB_SelectionInfo, handler OnSelectionChangedInfoBar), XÓA MeshToReplace |
| 1.5 | 11/06/2026 | Sprint 4 T5: BTN_EnterEdit, HB_EditModeBar (breadcrumb + ExitFull), bind OnEditModeChanged, Then 2 visibility. **BẢN HỢP NHẤT** — đã merge patch, file patch có thể xóa. |
