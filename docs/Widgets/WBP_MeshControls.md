# WBP_MeshControls
**HỢP NHẤT TỪ 5 file:** v1.4 base (10/06) + v1.5_patch (11/06) → WBP_MeshControls.md merged (11/06) + v1.5_update (12/06) + v1.6_patch (15/06)
**Phiên bản:** 1.7 | **Cập nhật:** 17/06/2026 — Sprint D.T6 | Persistent Toolbar — luôn hiển thị trên màn hình

> **v1.7 (Sprint D.T6):** BTN_Info đọc `RowName` thay `DAPath→Load`. `UpdateDetailPopup` rewrite: bound vào `OnSelectionChanged`, nhận Primary → GET RowName → InitPopup(RowName). Event Construct: thêm bind `UpdateDetailPopup → OnSelectionChanged`. Fix stale popup bug (cũ: Mouse Left Pressed Step 11 đọc SelectedFurnitureActor trước khi selection resolve).
> **v1.6 (Sprint 4 Bug Fix F1):** Info bar OnSelectionChangedInfoBar Then 1 → dùng `GetSelectionUnitLabel` thay inline logic. Widget name mapping: plan dùng HB_SelectionInfo/TXT_SelectionInfo → thực tế UE5 là `Border_ET_SelectionCount`/`ET_SelectionCount`.
> **v1.5 update (12/06):** Thêm `BTN_ExitOneLevel` ("↑ Lên 1 cấp") vào HB_EditModeBar + OnClicked.
> **v1.5 (Sprint 4 T5):** BTN_EnterEdit, HB_EditModeBar (breadcrumb + ExitFull), bind OnEditModeChanged, Then 2 BTN_EnterEdit visibility.
> **v1.4 (Sprint 3 + Refactor):** Selection Info Bar (OnSelectionChanged → label group/rời/ẩn), BTN_Replace → StartReplaceMode(multi), XÓA MeshToReplace single.
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
Border_ET_SelectionCount : Border           ← container info bar, Collapsed khi single/none
ET_SelectionCount        : TextBlock        ← "📦 Nhóm N (count)" / "N vật thể"; ẩn khi < 2 đồ
```
> **Widget name mapping (v1.6 fix):** plan doc cũ gọi `HB_SelectionInfo` / `TXT_SelectionInfo` — tên thực tế trong UE5 Blueprint là `Border_ET_SelectionCount` / `ET_SelectionCount`. Mọi reference sau đây dùng tên thực tế.

### Edit Mode (v1.5 — Sprint 4 T5, cập nhật v1.5_update)
```
BTN_EnterEdit    : Button          ← "✏️ Chỉnh nhóm". Collapsed mặc định. Hiện khi Primary có GroupID.
HB_EditModeBar   : HorizontalBox   ← Collapsed mặc định. Hiện khi đang edit mode. RIÊNG với Border_ET_SelectionCount.
  TXT_EditBreadcrumb : TextBlock   ← "✏️ Đang chỉnh: Nhóm 1 › Nhóm 2"
  BTN_ExitOneLevel   : Button      ← "↑ Lên 1 cấp" → ExitEditModeOneLevel  ← v1.5_update
  BTN_ExitFull       : Button      ← "✖ Thoát" → ExitEditModeFull
```
> ⚠ `HB_EditModeBar` KHÔNG dùng chung `Border_ET_SelectionCount` — edit mode có thể active khi chọn 0/1 đồ (info bar lúc đó Collapsed).

---

## Layout (v1.5_update)

```
[↖Select] [✛Move] [↺Rotate] [⊡Scale] | [🗑Delete] [ℹInfo] [↔Replace]
[Border_ET_SelectionCount: ET_SelectionCount]   [BTN_EnterEdit ✏️ Chỉnh nhóm]
[HB_EditModeBar: "✏️ Đang chỉnh: ..." | ↑ Lên 1 cấp | ✖ Thoát]
[── SnapStep ──]  [── SnapAngle ──]  [── SnapScale ──]  ← luôn visible
```

---

## Event Construct (v1.4 + v1.5)

```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → InputRef
→ SET ActiveMode = Select → RefreshButtonState(Select)
← v1.4: bind info bar
→ Bind Event to OnSelectionChanged (Target=InputRef) → OnSelectionChangedInfoBar
→ Bind Event to OnSelectionChanged (Target=InputRef) → UpdateDetailPopup   ← v1.7: bind popup update
→ Set Visibility(Border_ET_SelectionCount, Collapsed)
← v1.5: bind edit mode
→ Bind Event to OnEditModeChanged (Target=InputRef) → OnEditModeChangedInfoBar
→ Set Visibility(HB_EditModeBar, Collapsed)
→ Set Visibility(BTN_EnterEdit, Collapsed)
```
⚠ Bind PHẢI ở Event Construct (chạy 1 lần lúc tạo widget). Info bar dùng CHUNG dispatcher `OnSelectionChanged` — không tạo dispatcher riêng (single source of truth).

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
    DeactivateGizmo  ← PHẢI trước ActivateGizmo (chống gizmo nhảy về đồ đơn khi đổi mode lúc multi)
    Branch (SelectedActors.Length >= 2):
      True  → ActivateGizmo(GizmoPivotActor, TransformerPawn, Translation)    ← multi → pivot
      False → ActivateGizmo(SelectedFurnitureActor, TransformerPawn, Translation)
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

## ET_SnapStep / ET_SnapAngle / ET_SnapScale

```
Default = "10" / "15" / "0.1"
OnTextCommitted → Text To Float → SET SnapStep / SnapAngle / SnapScale (GizmoControllerRef)
0 = free (movement / rotation / scale)
```

---

## BTN_Delete

```
IsValid(TargetActor):
  Destroy Actor              ← PHẢI trước CaptureSnapshot
  CaptureSnapshot("Delete")
  Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
  → GET DetailPopupRef → IsValid → Remove from Parent → SET None
  SET SelectedFurnitureActor = None → DeactivateGizmo → Remove from Parent (self)
```
> **[?]** Flow này là bản single (v1.1 legacy). Sau Sprint 1 multi-select, BTN_Delete nhiều khả năng đã trỏ về `DeleteSelected` (InputManager) như CB_Delete của context menu. Cần đối chiếu node graph thật rồi cập nhật.

---

## BTN_Info OnClicked — v1.7 (Sprint D.T6)

```
Get All Actors Of Class(InputManager) → Get(0) → Cast → FurnitureInputRef
GET DetailPopupRef → IsValid → Remove from Parent
GET SelectedFurnitureActor → Branch IsValid:
  True:
    Cast → BP_FurnitureActor → GET RowName
    Branch RowName != "":
      True:
        Create WBP_DetailPopup → Add to Viewport
        Set Position In Viewport(chuột + Y+10) → SET PopupPosition
        SET DetailPopupRef = popup
        Call InitPopup(RowName, bFromScene=True)
      False: (save cũ chưa có RowName — popup không mở)
```
> ⚠ RowName == "" = save cũ. Popup silently bỏ qua — không fallback DAPath (cuhoang xác nhận: không cần fallback). Để hỗ trợ save cũ đầy đủ → đổi save file + re-import.

---

## BTN_Replace OnClicked (v1.4 — StartReplaceMode multi)

```
Get All Actors Of Class(InputManager) → Get(0) → Cast → FurnitureInputRef
Branch bIsReplaceMode == True:
  True  → thoát Replace: SET bIsReplaceMode=False, CLEAR MeshesToReplace,
          GameInstance → FurnitureInventoryRef → IsValid → ExitReplaceMode → Return
  False → Call StartReplaceMode(SelectedActors)  (InputManager — multi)
```
> v1.4 XÓA mọi tham chiếu `MeshToReplace` (single). Flow chi tiết StartReplaceMode: xem BP_FurnitureInputManager / Blueprint_Logic (Sprint 2 T9).

---

## UpdateDetailPopup (Custom Event, bound to OnSelectionChanged) — v1.7

```
← Signature: (Actors: Array<BP_FurnitureActor>, Primary: BP_FurnitureActor)
← Bound từ Event Construct: Bind OnSelectionChanged → UpdateDetailPopup

GET DetailPopupRef → Branch IsValid:
  True → (popup đang mở — update)
    Branch IsValid(Primary):
      True:
        Cast Primary → BP_FurnitureActor → GET RowName
        Branch RowName != "":
          True  → Call InitPopup(RowName, bFromScene=True)
          False → Remove from Parent(DetailPopupRef) → SET DetailPopupRef = None
      False → (deselect — đóng popup)
        Remove from Parent(DetailPopupRef) → SET DetailPopupRef = None
  False → (popup chưa mở — no-op)
```
> ⚠ Bind phải ở Event Construct — không ở handler (handler không fire thì không bao giờ bind). Fix bug stale: trước đây UpdateDetailPopup được gọi tại Mouse Left Pressed Step 11 → đọc SelectedFurnitureActor TRƯỚC khi selection resolve ở OnLMBReleased → popup hiện đồ cũ. Nay chạy SAU OnSelectionChanged fire → đúng actor.

---

## RefreshButtonState(ActiveMode)

```
Switch on ActiveMode: Select / Move / Rotate / Scale
  → highlight nút tương ứng, white các nút khác
```

---

## OnSelectionChangedInfoBar(Actors, Primary) — v1.6: VIẾT LẠI Then 1

> Bound từ `InputManager.OnSelectionChanged`. Dùng Sequence. Primary = PARAMETER của handler, không phải class variable.

**Then 1 — info bar label (v1.6: VIẾT LẠI — thay inline bằng GetSelectionUnitLabel):**
```
Branch (Actors.Length >= 2):                       ← CHỈ hiện khi >= 2 đồ
  False → Set Visibility(Border_ET_SelectionCount, Collapsed)
  True  →
    Set Visibility(Border_ET_SelectionCount, Visible)
    Get All Actors Of Class(BP_FurnitureInputManager) → GET[0] → Cast → InputRef
    Call InputRef.GetSelectionUnitLabel(Primary=PrimarySelectedActor, Count=Actors.Length) → Label
    SetText(ET_SelectionCount, Label)
```
> Logic xét scope edit / group unit / đồ rời nằm hoàn toàn trong `GetSelectionUnitLabel` (BP_FurnitureInputManager). WBP_MeshControls chỉ: >= 2 đồ → visible → gọi → set text.

> **[?]** Sequence có "Then 1" (info bar) và "Then 2" (BTN_EnterEdit) — không rõ "Then 0" (nếu tồn tại) có nội dung gì trong node graph thật.

**Then 2 — BTN_EnterEdit visibility (v1.5: THÊM MỚI):**
```
Branch IsValid(Primary):
  True  → Cast → GET GroupID → Branch (GroupID != ""):
            True  → Set Visibility(BTN_EnterEdit, Visible)
            False → Set Visibility(BTN_EnterEdit, Collapsed)
  False → Set Visibility(BTN_EnterEdit, Collapsed)
```

> ⚠ Info bar KHÔNG hiện khi single — chỉ >= 2 đồ. Single/none → Collapsed.

---

## OnEditModeChangedInfoBar(bActive, GroupID) — v1.5: MỚI

```
Branch(bActive):
  True  →
    Set Visibility(HB_EditModeBar, Visible)
    Get All Actors Of Class(InputManager)[0] → Call GetEditBreadcrumb → BreadStr
    SetText(TXT_EditBreadcrumb, "✏️ Đang chỉnh: " + BreadStr)
  False →
    Set Visibility(HB_EditModeBar, Collapsed)
```
> False branch dead-end OK (chỉ hide, không có logic sau).

---

## OnClicked — v1.5_update: CẬP NHẬT

```
BTN_EnterEdit.OnClicked    : Get All Actors Of Class(InputManager)[0] → TryEnterEditFromSelection
BTN_ExitOneLevel.OnClicked : Get All Actors Of Class(InputManager)[0] → ExitEditModeOneLevel   ← v1.5_update
BTN_ExitFull.OnClicked     : Get All Actors Of Class(InputManager)[0] → ExitEditModeFull
```

---

## Hành vi các nút Exit (v1.5_update)

| Nút | Function | Hành vi |
|---|---|---|
| ↑ Lên 1 cấp | ExitEditModeOneLevel | Pop 1 cấp: nếu còn cha → về scope cha, chọn lại sub-group vừa thoát như 1 unit; nếu hết → thoát edit, chọn lại root group |
| ✖ Thoát | ExitEditModeFull | Thoát hẳn tất cả cấp, CLEAR EditModeStack, chọn lại root group |

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|-----------|------|----------|
| 1.0 | 22/04/2026 | Logic gốc |
| 1.1 | 25/05/2026 | BTN_Replace toggle + gọi EnterReplaceMode |
| 1.2 | 05/06/2026 — 20:00 ICT | T15: BTN_Move/Rotate/Scale check Length>=2 → GizmoPivotActor khi multi-select. Fix gizmo nhảy về đồ đơn khi đổi mode. |
| 1.3 | 08/06/2026 | Sprint 2 prep: BTN_Replace → StartReplaceMode (multi) trong InputManager |
| 1.4 | 10/06/2026 — 20:34 ICT | **Sprint 3 + Refactor.** Thêm vars info bar (Border_ET_SelectionCount / ET_SelectionCount). Event Construct bind OnSelectionChanged → OnSelectionChangedInfoBar. Handler: label "📦 GroupName (N)" / "N vật thể" / Collapsed. BTN_Replace → StartReplaceMode(SelectedActors), XÓA MeshToReplace single. |
| 1.5 | 11/06/2026 — 18:14 ICT | **Sprint 4 T5 — Edit Mode UI.** Vars: BTN_EnterEdit, HB_EditModeBar (TXT_EditBreadcrumb, BTN_ExitFull). Event Construct bind OnEditModeChanged → OnEditModeChangedInfoBar + ẩn edit bar ban đầu. Handler OnEditModeChangedInfoBar: hiện/ẩn bar + set breadcrumb. OnSelectionChangedInfoBar Then 2: BTN_EnterEdit visibility. OnClicked: BTN_EnterEdit, BTN_ExitFull. |
| 1.5 update | 12/06/2026 — 15:04 ICT | Thêm BTN_ExitOneLevel ("↑ Lên 1 cấp") vào HB_EditModeBar + OnClicked → ExitEditModeOneLevel. Cập nhật Layout. Thêm bảng hành vi Exit buttons. |
| 1.6 | 15/06/2026 — 20:30 ICT | **F1: Info bar dùng GetSelectionUnitLabel.** OnSelectionChangedInfoBar Then 1: thay inline label logic bằng call InputManager.GetSelectionUnitLabel(Primary, Count). Widget name fix: HB_SelectionInfo → Border_ET_SelectionCount, TXT_SelectionInfo → ET_SelectionCount (tên thực tế trong UE5 Blueprint). |
| 1.7 | 17/06/2026 — Sprint D.T6 | BTN_Info: đọc RowName thay DAPath→Load. UpdateDetailPopup rewrite: bound OnSelectionChanged, nhận Primary → RowName → InitPopup(RowName). Event Construct: thêm bind UpdateDetailPopup. Fix stale popup bug (cũ: Step 11 Mouse Left Pressed đọc actor trước selection resolve). |
