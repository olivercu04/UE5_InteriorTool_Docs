# Session State — Lighting_Mnger Interior Design Tool
**Cập nhật:** 19/05/2026 — 17:50 ICT
**Đọc file này ĐẦU TIÊN** khi bắt đầu session mới.

---

## TRẠNG THÁI HIỆN TẠI

**Feature đang làm:** UX fixes cho Change Material v1.1
**Engine:** UE5.5.4

---

## ĐÃ HOÀN THÀNH

### Change Material v1.1 (18/05/2026)
- Tab Material/Furniture, SwitchInventoryMode, Slot Swatches, Material Grid
- Live Apply (Async Load → Create MID → Set Material → Debounce CaptureSnapshot)
- Reset Slot / Reset All, Undo/Redo (OnRestoreCompleted), Save/Load
- Folder Tree + Chip Tag cho Material (BuildMaterialFolderTree)
- C++ FilterMaterialItems fix (PropertyLink loop)

### UX Fixes đã xong
- ✅ Search text reset khi switch mode (logic OK, visual SearchBar không clear được — CommonSearchBox giới hạn)
- ✅ Tab highlight + mode switch (UpdateTabHighlight + Branch IsEmpty dead-end fix)
- ✅ Category/folder tree Material (BuildMaterialFolderTree + FilterBySearch branch Material)
- ✅ Highlight slot đang chọn (Image overlay trong WBP_SlotSwatch + SetSelected)
- ✅ Thumbnail swatch update sau apply material (UpdateThumbnail + DT lookup)
- ✅ Thumbnail swatch update sau Reset Slot (GetObjectName material gốc → DT lookup)
- ✅ Thumbnail swatch update sau Reset All (RefreshSlotSwatches)
- ✅ Deselect mesh → ẩn SlotSwatches (OnMeshDeselected Event Dispatcher)
- ✅ Select mesh khác → update SlotSwatches (OnMeshSelected Event Dispatcher)

---

## ĐANG LÀM

### Fix Undo/Redo SlotSwatches ẩn/hiện
- **Vấn đề:** Sau Undo/Redo, LeftMouseButton event trong BP_FurnitureInputManager fire DeselectMesh → OnMeshDeselected → ẩn SlotSwatches SAU OnSceneRestored đã hiện.
- **Fix đang implement:** Timer delay 0.1s trong OnSceneRestored → ApplyRestoredActor fire sau LeftMouseButton xong.
- **Trạng thái:** ApplyRestoredActor chạy cuối cùng (confirmed qua log). Cần test visual.
- **Debug prints còn trong code** — cần xóa.

---

## TODO TIẾP THEO

1. **Xóa Print Strings debug** → Compile → test visual Undo/Redo SlotSwatches
2. **Fix #6 — Loading feedback khi apply material** 
3. **Fix #7 — FilterByCategory branch theo mode Material**
4. **Cập nhật doc cuối cùng** khi tất cả UX fixes xong

---

## UX FIXES TRACKING

| # | Vấn đề | Status |
|---|---|---|
| 1 | Search text reset khi switch mode | ✅ (partial — visual SearchBar chưa clear) |
| 2 | Tên slot trong swatch | ⏭️ (chuyển sang Detail popup) |
| 3 | Highlight slot đang chọn | ✅ |
| 4 | Thumbnail swatch update sau apply/reset/undo | ✅ |
| 5 | Deselect/Select mesh → update SlotSwatches | ✅ (timer 0.1s approach) |
| 6 | Loading feedback khi apply | 🔲 |
| 7 | FilterByCategory branch theo mode | 🔲 |

---

## VARIABLES QUAN TRỌNG (WBP_FurnitureInventory)

```
CurrentInventoryMode  : E_InventoryMode (Furniture/Material)
TargetFurnitureActor  : BP_FurnitureActor
SelectedSlotIndex     : Integer (default -1)
AllFilteredMaterialRows : Array of Name
PendingMaterialPath   : String
PendingRowName        : Name  ← RowName đang chờ apply (dùng cho thumbnail update)
ApplyMaterialTimerHandle : Timer Handle
UndoManagerRef        : BP_UndoManager
PendingRestoredActor  : BP_FurnitureActor  ← actor chờ restore sau timer 0.1s
FolderTree            : Map String→String (active tree, swap khi switch mode)
FurnitureFolderTree   : Map String→String (cache Furniture)
MaterialFolderTree    : Map String→String (cache Material)
CurrentFolderPath, CurrentSearchText, CurrentPage(0-based), PageSize(=48)
```

---

## KEY BUGS & FIXES

| Bug | Fix |
|---|---|
| FilterMaterialItems FolderProp = NULL | PropertyLink loop + Contains (Blueprint struct GUID) |
| TargetFurnitureActor invalid sau Undo/Redo | OnRestoreCompleted Event Dispatcher |
| MaterialPath không resolve | Full object path: `/Game/.../MI_Name.MI_Name` |
| Dead-end branches → logic sau không chạy | Tất cả nhánh phải merge về cuối |
| Branch IsEmpty False → FolderTree không swap lần 2 | Nối False vào SET FolderTree |
| Set Background Color không work trên Button Tint A=0 | Dùng Image overlay + Set Color and Opacity |
| LeftMouseButton DeselectMesh fire sau Undo/Redo | Timer delay 0.1s trong ApplyRestoredActor |
| Accessed None TargetFurnitureActor trong ForEach | IsValid check trước mọi ForEach/ForLoop dùng Object |

---

## NGUYÊN TẮC

### Đầu session: đọc Session_State.md → Blueprint_Logic.md nếu cần
### Blueprint: luôn IsValid trước Object access. Tất cả nhánh merge về cuối.
### Cuối session: update Session_State.md + Blueprint_Logic.md
