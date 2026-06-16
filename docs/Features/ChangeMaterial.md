# Context — Tính năng Change Material v1.1
**Phiên bản:** 1.6 | **Cập nhật:** 18/05/2026 — 08:55 ICT | Project: Lighting_Mnger (UE5.5.4)

---

## ✅ Change Material v1.1 — HOÀN THÀNH (18/05/2026)

---

## Thứ tự build (v1.1)

| Bước | Nội dung | Trạng thái |
|------|----------|-----------|
| **Giai đoạn 1 — Data** | | |
| 1.1 | Tạo `S_MaterialInstancesData` struct | ✅ |
| 1.2 | Import CSV → `DT_MaterialInstancesCatalog` (2738 rows) | ✅ |
| 1.3 | Python populate MaterialFolderPath + MaterialPath | ✅ 2738 rows |
| 1.4 | Bake thumbnails → import UE5 | ✅ 2731 textures |
| 1.5 | Python populate ThumbnailMI (Soft Ref Texture2D) | ✅ 2738 updated |
| 1.6 | Python update MaterialPath → full object path | ✅ 2738 updated |
| **Giai đoạn 2 — Nền kỹ thuật** | | |
| 2.1 | `MaterialOverrides` + `MaterialParams` → `BP_FurnitureActor` | ✅ |
| 2.2 | `MaterialPaths` → `S_FurniturePlacement` | ✅ |
| 2.3 | `CaptureSnapshot` + `RestoreSnapshot` + `OnRestoreCompleted` | ✅ |
| 2.4 | `ActorLoaded` restore MaterialOverrides | ✅ |
| 2.5 | C++ `FilterMaterialItems()` trong `UFurnitureFilterLibrary` | ✅ |
| **Giai đoạn 3 — UI** | | |
| 3.1 | Tab Furniture/Material + `SwitchInventoryMode` + Tab Highlight | ✅ 09/05/2026 |
| 3.2 | Slot Swatches | ✅ 09/05/2026 |
| 3.3 | Material Grid | ✅ 13/05/2026 |
| 3.4 | Live Apply | ✅ 16/05/2026 |
| 3.5 | Reset Slot + Reset All | ✅ 16/05/2026 |
| 3.6 | SwitchInventoryMode lấy TargetFurnitureActor | ✅ 16/05/2026 |
| **Giai đoạn 4 — Hoàn thiện** | | |
| 4.1 | Test: đổi material → Save → Load → material đúng | ✅ 18/05/2026 |
| 4.2 | Test: Undo/Redo material đúng | ✅ 18/05/2026 |
| 4.3 | Test: Replace mesh → material reset đúng | ✅ 18/05/2026 |

---

## Flow hoàn chỉnh (v1.1)

```
1. User select mesh → click tab Material
2. SwitchInventoryMode(Material):
   - GET SelectedFurnitureActor → SET TargetFurnitureActor + TargetMeshPath
   - Hiện CTV_MaterialCard, HB_SlotSwatches
   - PopulateMaterialGrid (C++ filter → cache → DisplayPage)
3. User chọn SlotSwatch → SET SelectedSlotIndex
4. User duyệt grid → click Button_ChangeMaterial trên card
5. ApplyMaterial(RowName):
   - Branch IsValid(TargetFurnitureActor)? Nếu không → tìm lại bằng TargetMeshPath
   - Get Data Table Row → SET PendingMaterialPath → Call LoadAndApplyMaterial
6. LoadAndApplyMaterial (async):
   - Make Soft Object Path → To Soft Object Reference → Async Load Asset
   - Completed → Cast MaterialInterface → Create MID → Set Material → Set Array Elem
   - Debounce 0.5s → CaptureSnapshot("ChangeMaterial")
7. Undo/Redo:
   - RestoreSnapshot spawn actors mới → Broadcast OnRestoreCompleted(actor)
   - WBP_FurnitureInventory.OnSceneRestored → SET TargetFurnitureActor = actor mới
8. BTN_ResetSlot → restore slot về material gốc → CaptureSnapshot("ResetSlot")
9. BTN_ResetAll → restore tất cả slots → CaptureSnapshot("ResetAll")
10. Save → EMS lưu MaterialOverrides → Load → ActorLoaded restore MID từ MaterialPaths
```

---

## Bugs đã fix (v1.1)

| Bug | Nguyên nhân | Fix |
|---|---|---|
| Material không apply | MaterialPath thiếu `.AssetName` | Python script update 2738 rows → full object path |
| Redo không restore material | Load Asset Blocking với path sai | Cùng fix trên |
| Apply slot fail sau Undo/Redo | TargetFurnitureActor = actor đã destroy | OnRestoreCompleted Event Dispatcher + TargetMeshPath |
| OnRestoreCompleted không fire | Nhánh False/Cast Failed dead-end trong RestoreSnapshot | Nối tất cả nhánh về RefreshButtonState → Call OnRestoreCompleted |

---

## Key Learnings tổng hợp (v1.1)

**Data:**
- MaterialPath cần full object path `/Game/.../MI_Name.MI_Name` — Make Soft Object Path yêu cầu
- Python: dùng `export_data_table_to_json_string` + `fill_data_table_from_json_string`, không dùng `find_row`

**Blueprint Async:**
- Latent node (Async Load Asset) không dùng trong Function → Custom Event trong Event Graph
- Flow: String → Make Soft Object Path → To Soft Object Reference → Async Load Asset

**Undo/Redo:**
- UniqueID (GetDisplayName) thay đổi mỗi lần spawn → dùng MeshPath để track actor
- Event Dispatcher tốt hơn tìm kiếm — cập nhật reference ngay khi actor mới vừa spawn
- **Mọi nhánh execution (True/False/Cast Failed) phải merge về cuối** — nhánh dead-end khiến logic sau không chạy

**Debug:**
- Breakpoint UE5: F9 toggle, F10 step over, F11 step into, Alt+Shift+F10 continue
- "Not in scope" = giới hạn debugger, không có nghĩa null
- Đặt breakpoint nhiều điểm để tìm chỗ execution dừng

**Kiến trúc:**
- Technical debt: Widget gọi UndoManager trực tiếp → refactor Phase B
- Create Dynamic Material Instance → MID (không set MI trực tiếp) → v1.2 thêm param dễ dàng
- Set Array Elem Size to Fit thay For Loop resize

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0–1.2 | 08–12/05/2026 | Data pipeline, thumbnail |
| 1.3–1.4 | 13/05/2026 | Bước 3.3, i18n plan, thumbnail optimization |
| 1.5 | 16/05/2026 — 14:08 ICT | Bước 3.4+3.5+3.6 code xong, bugs documented |
| 1.6 | 18/05/2026 — 08:55 ICT | **v1.1 HOÀN THÀNH** — 4.1+4.2+4.3 pass, fix OnRestoreCompleted dead-end, key learnings |
