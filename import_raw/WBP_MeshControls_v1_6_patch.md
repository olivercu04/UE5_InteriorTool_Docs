# WBP_MeshControls — PATCH v1.6
**Phiên bản:** 1.6 | **Cập nhật:** 15/06/2026 — 20:30 ICT
**Patch từ v1.5 → v1.6 (Sprint 4 Bug Fix F1 — Info bar dùng GetSelectionUnitLabel)**
> Đọc kèm WBP_MeshControls.md v1.5.

---

## OnSelectionChangedHandler — Sequence.Then 1 — SỬA (F1)

**Thay đổi:** Thay logic inline bằng call tới `GetSelectionUnitLabel` trên InputManager.

**Cũ (v1.5 inline):**
```
Branch (Actors.Length >= 2):
  False → Set Visibility(HB_SelectionInfo, Collapsed)
  True  →
    Set Visibility(HB_SelectionInfo, Visible)
    Cast Primary → BP_FurnitureActor → GET GroupID → LocalGID
    Branch (LocalGID != ""):
      True  → FindGroupData(LocalGID) → bFound
              Branch bFound:
                True  → SetText(ET_SelectionCount, "📦 " + GroupData.GroupName + " (" + Actors.Length + ")")
                False → SetText(ET_SelectionCount, Actors.Length + " vật thể")
      False → SetText(ET_SelectionCount, Actors.Length + " vật thể")
```

**Mới (v1.6 — dùng GetSelectionUnitLabel):**
```
Branch (Actors.Length >= 2):
  False → Set Visibility(Border_ET_SelectionCount, Collapsed)
  True  →
    Set Visibility(Border_ET_SelectionCount, Visible)
    Get All Actors Of Class(BP_FurnitureInputManager) → GET[0] → Cast → InputRef
    InputRef.GetSelectionUnitLabel(Primary=PrimarySelectedActor, Count=Actors.Length) → Label
    SetText(ET_SelectionCount, Label)
```

> **Widget name mapping (thực tế vs plan):**
> - Plan: `HB_SelectionInfo` → Thực tế: `Border_ET_SelectionCount`
> - Plan: `TXT_SelectionInfo` → Thực tế: `ET_SelectionCount`
>
> Logic xét scope edit, group unit, đồ rời nằm hoàn toàn trong GetSelectionUnitLabel (BP_FurnitureInputManager).
> WBP_MeshControls chỉ cần biết: >= 2 đồ → visible + gọi function → set text.

---

## Lịch sử cập nhật (thêm vào bảng)

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.6 | 15/06/2026 — 20:30 ICT | **F1: Info bar dùng GetSelectionUnitLabel.** Then 1 handler: thay inline label logic bằng call tới InputManager.GetSelectionUnitLabel. Widget name mapping: HB_SelectionInfo=Border_ET_SelectionCount, TXT_SelectionInfo=ET_SelectionCount. |
