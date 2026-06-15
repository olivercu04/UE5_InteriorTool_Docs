# WBP_MeshControls — UPDATE v1.5 (bổ sung BTN_ExitOneLevel)
**Phiên bản:** 1.5 (giữ nguyên) | **Cập nhật:** 12/06/2026 — 15:04 ICT
**Bổ sung vào bản hợp nhất v1.5 (11/06)**

---

## Xóa ghi chú ⚠ trong v1.5
Dòng sau đây trong v1.5 cần XÓA:
> ~~⚠ KIỂM TRA BP: nếu có BTN_ExitOneLevel thì bổ sung dòng OnClicked tương ứng vào doc.~~

---

## Widget Elements — CẬP NHẬT HB_EditModeBar

```
HB_EditModeBar : HorizontalBox ← Collapsed mặc định. Hiện khi edit mode active.
  TXT_EditBreadcrumb : TextBlock  ← "✏️ Đang chỉnh: Nhóm 1 › Nhóm 2"
  BTN_ExitOneLevel   : Button     ← "↑ Lên 1 cấp" → ExitEditModeOneLevel  ← ĐÃ THÊM
  BTN_ExitFull       : Button     ← "✖ Thoát" → ExitEditModeFull
```

---

## OnClicked — CẬP NHẬT (thêm BTN_ExitOneLevel)

```
BTN_EnterEdit.OnClicked    : Get All Actors Of Class(InputManager)[0] → TryEnterEditFromSelection
BTN_ExitOneLevel.OnClicked : Get All Actors Of Class(InputManager)[0] → ExitEditModeOneLevel   ← MỚI
BTN_ExitFull.OnClicked     : Get All Actors Of Class(InputManager)[0] → ExitEditModeFull
```

---

## Layout — CẬP NHẬT

```
[↖Select] [✛Move] [↺Rotate] [⊡Scale] | [🗑Delete] [ℹInfo] [↔Replace]
[TXT_SelectionInfo (HB_SelectionInfo)]  [BTN_EnterEdit ✏️ Chỉnh nhóm]
[HB_EditModeBar: "✏️ Đang chỉnh: ..." | ↑ Lên 1 cấp | ✖ Thoát]
[── SnapStep ──]  [── SnapAngle ──]  [── SnapScale ──]
```

---

## Ghi chú hành vi các nút Exit

| Nút | Function | Hành vi |
|---|---|---|
| ↑ Lên 1 cấp | ExitEditModeOneLevel | Pop 1 cấp: nếu còn cha → về scope cha, chọn lại sub-group vừa thoát như 1 unit; nếu hết → thoát edit, chọn lại root group |
| ✖ Thoát | ExitEditModeFull | Thoát hẳn tất cả cấp, CLEAR EditModeStack, chọn lại root group |

---

## Lịch sử cập nhật (bổ sung)

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.5 | 11/06/2026 | Sprint 4 T5: BTN_EnterEdit, HB_EditModeBar, bind OnEditModeChanged, Then 2 visibility. |
| 1.5 update | 12/06/2026 — 15:04 ICT | Bổ sung BTN_ExitOneLevel ("↑ Lên 1 cấp") vào HB_EditModeBar + OnClicked → ExitEditModeOneLevel. Xóa ⚠ marker. |
