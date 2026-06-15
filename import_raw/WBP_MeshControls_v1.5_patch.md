# WBP_MeshControls — PATCH v1.5
**Phiên bản:** 1.5 | **Cập nhật:** 11/06/2026 — 18:14 ICT
**Patch từ v1.4 → v1.5 (Sprint 4 T5 — Edit Mode Info Bar)**
> Đọc kèm bản gốc v1.4. File này ghi ĐỦ những gì thêm/thay đổi.

---

## Widget Elements MỚI

```
BTN_EnterEdit    : Button    ← "✏️ Chỉnh nhóm". Collapsed mặc định. Hiện khi Primary có GroupID.
HB_EditModeBar   : HorizontalBox (hoặc Border)  ← Collapsed mặc định. Hiện khi đang edit mode. RIÊNG với HB_SelectionInfo.
  TXT_EditBreadcrumb : TextBlock  ← "✏️ Đang chỉnh: Nhóm 1 › Nhóm 2"
  BTN_ExitFull       : Button     ← "✖ Thoát" → ExitEditModeFull
```
> ⚠️ `HB_EditModeBar` KHÔNG dùng chung với `HB_SelectionInfo`. Edit mode có thể active khi chọn 0/1 đồ.

---

## Event Construct — THÊM (sau bind OnSelectionChanged có sẵn)
```
(InputRef đã có từ bind cũ)
+ Bind Event to OnEditModeChanged (Target=InputRef) → OnEditModeChangedInfoBar
+ Set Visibility(HB_EditModeBar, Collapsed)
+ Set Visibility(BTN_EnterEdit, Collapsed)
```

---

## Handler MỚI: `OnEditModeChangedInfoBar(bActive, GroupID)`
```
Branch(bActive):
  True  →
    Set Visibility(HB_EditModeBar, Visible)
    GetAllActorsOfClass(BP_FurnitureInputManager)[0] → Call GetEditBreadcrumb → BreadStr
    SetText(TXT_EditBreadcrumb, "✏️ Đang chỉnh: " + BreadStr)
  False →
    Set Visibility(HB_EditModeBar, Collapsed)
```
> Lưu ý: False branch dead-end là OK (chỉ hide, không cần merge về đâu vì không có logic sau).

---

## OnSelectionChangedInfoBar — THÊM VÀO CUỐI (Sequence.Then 2)
Thêm `Then 2` vào Sequence node hiện có:
```
Sequence.Then 2 ▶→ Branch(IsValid(Primary)):
  True  → Cast Primary → BP_FurnitureActor → GET GroupID
           Branch(GroupID != ""):
             True  → Set Visibility(BTN_EnterEdit, Visible)
             False → Set Visibility(BTN_EnterEdit, Collapsed)
  False → Set Visibility(BTN_EnterEdit, Collapsed)
```
> Primary = parameter của event handler (pin từ OnSelectionChangedHandler), không phải class variable.

---

## OnClicked MỚI

```
BTN_EnterEdit.OnClicked:
  GetAllActorsOfClass(InputManager)[0] → Call TryEnterEditFromSelection

BTN_ExitFull.OnClicked:
  GetAllActorsOfClass(InputManager)[0] → Call ExitEditModeFull
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| ... | ... | (xem v1.4) |
| 1.5 | 11/06/2026 — 18:14 ICT | **Sprint 4 T5 — Edit Mode UI.** Thêm `BTN_EnterEdit` (Visible khi Primary có GroupID), `HB_EditModeBar` (breadcrumb + BTN_ExitFull). Event Construct bind `OnEditModeChanged → OnEditModeChangedInfoBar`. Handler hiện/ẩn HB_EditModeBar + set breadcrumb text. OnSelectionChangedInfoBar thêm Then 2 xử lý visibility BTN_EnterEdit. BTN_ExitFull gọi ExitEditModeFull. |
