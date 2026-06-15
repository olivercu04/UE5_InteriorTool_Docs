# Session State — Lighting_Mnger Interior Design Tool
**Cập nhật:** 27/05/2026 — 10:30 ICT
**Đọc file này ĐẦU TIÊN** khi bắt đầu session mới.

---

## TRẠNG THÁI HIỆN TẠI

**Feature:** UI/UX Fixes + Resize Window — **HOÀN THÀNH**
**Engine:** UE5.5.4

---

## ĐÃ HOÀN THÀNH

### Change Material v1.1 (18–20/05/2026)
- Tab Material/Furniture, SwitchInventoryMode, Slot Swatches, Material Grid
- Live Apply (Async Load → Create MID → Set Material → Debounce CaptureSnapshot)
- Reset Slot / Reset All, Undo/Redo (OnRestoreCompleted), Save/Load
- Folder Tree + Chip Tag cho Material (BuildMaterialFolderTree)
- C++ FilterMaterialItems fix (PropertyLink loop)

### UX Phase 2.1 Đợt A — Gizmo (hoàn thành trước 22/05/2026)
- A1. Rotate Gizmo scale theo distance ✅
- A2. Rotate Gizmo hướng xoay ✅
- A3. Translation Gizmo collision + Axis Lock ✅

### UX Phase 2.1 Đợt B — Thao tác (hoàn thành trước 22/05/2026)
- B1. Arrow Key Nudge + PlacementSurfaceType + Snap 90° ✅
- B2. Copy/Paste/Duplicate + IA_Block_C/V/D ✅

### UX Phase 2.1 Đợt C — Inventory UX (25/05/2026)
- C0. BP_UserPreferencesSave + BP_FurnitureUserPrefsManager ✅
- C1. History (Recent category) + AddRecentMesh/Material dedup fix ✅
- C2. Favorites (⭐ button + Favorites category + toggle + persist khi switch mode) ✅

### UI/UX Fixes (27/05/2026)
- Fix AddRecentMesh không ghi nhận mesh sử dụng gần đây ✅
- Fix DisplayPage không cập nhật số trang cho Furniture Recent + Favorite ✅
  → Thêm SET FilteredItems + SET CurrentPage = 0 + Call DisplayPage trước Return
- Fix Recent Furniture: đổi từ Add Item trực tiếp sang collect array → DisplayPage ✅

### Resize Window — WBP_FurnitureInventory (27/05/2026)
- 8 hướng resize: 4 cạnh + 4 góc ✅
- 5 class variables: bIsResizing, ResizeDirection, ResizeStartMousePos/Size/Position ✅
- Function ResizeWindow (Sequence + 4 boolean hướng + clamp min) ✅
- Function UpdateResizeHandles (reposition 8 BTN handle theo window size) ✅
- Custom Event StartResize ✅
- Tích hợp Maximize/Minimize (ẩn/hiện handle) ✅
- Fix drag sau resize: đổi từ Set Position in Viewport sang Slot as Canvas Slot ✅
- Chi tiết: xem WBP_ResizeWindow.md

---

## TODO TIẾP THEO

1. **Group Mesh / Multi-select** — theo kế hoạch MultiSelect_Group_ComboMesh_Plan_v2.md
2. **Material Edit v1.2** — Color Picker, Roughness, Metallic slider
3. **Refactor Phase B** — AssetService C++ Subsystem, Event Bus, async pipeline
4. **glTFRuntime** — runtime asset import
5. **Thumbnail Generation Pipeline** — pre-baked 3D thumbnails

---

## KEY BUGS & FIXES (tích lũy)

| Bug | Fix |
|---|---|
| FilterMaterialItems FolderProp = NULL | PropertyLink loop + Contains |
| TargetFurnitureActor invalid sau Undo/Redo | OnRestoreCompleted Event Dispatcher |
| MaterialPath không resolve | Full object path `/Game/.../MI_Name.MI_Name` |
| Dead-end branches | Tất cả nhánh merge về cuối |
| Branch IsEmpty False → FolderTree không swap | Nối False vào SET FolderTree |
| Set Background Color không work (Tint A=0) | Image overlay + Set Color and Opacity |
| LeftMouseButton fire sau Undo/Redo | Timer delay 0.1s trong ApplyRestoredActor |
| Accessed None trong ForEach | IsValid check trước mọi Object access |
| Broadcast OnRestoreCompleted sai actor | RestoredBPActor var thay SpawnedActors[class var] |
| Switch về Furniture → card trống | FilterBySearch cuối SwitchInventoryMode False branch |
| Add Item nested ForEach không hiện card | Item pin phải wire vào DA (Array Element) |
| FilterByCategory parameter đọc class variable | Dùng wire từ input pin function |
| CategoryFilter = "Favorite" literal | Wire GET ActiveSpecialCategory vào pin |
| ForEach False branch nối vào Break | False branch để trống |
| Recent/Favorite duplicate | AddRecentMesh/Material: remove dup trước INSERT front |
| Replace Mesh không ghi Recent | AddRecentMesh sau CaptureSnapshot("Replace") |
| Pagination hiện "1/0" | (Length + PageSize - 1) / PageSize — integer math |
| Root Canvas Panel block click | Not Hit-Testable (Self Only) |
| Recent/Favorite không cập nhật số trang | SET FilteredItems + CurrentPage=0 + DisplayPage trước Return |
| Resize BTN_ResizeRight không kéo được | False branch Sequence SET lại NewW → overwrite Then trước. Fix: default trước Sequence, False branch để trống |
| Window nhảy khỏi cursor khi drag sau resize | Drag và resize dùng 2 hệ tọa độ khác nhau. Fix: đổi drag sang Slot as Canvas Slot |
| Resize button nhỏ → OnReleased fire sớm | Dùng Is Mouse Button Down trong ResizeWindow thay OnReleased |
| Slot as Canvas Slot Get Size trả về (0,0) | Gọi Set Size explicit trong Event Construct |

---

## VARIABLES QUAN TRỌNG (WBP_FurnitureInventory)

```
CurrentInventoryMode       : E_InventoryMode (Furniture/Material)
TargetFurnitureActor       : BP_FurnitureActor
SelectedSlotIndex          : Integer (default -1)
AllFilteredMaterialRows    : Array of Name
FilteredItems              : Array of DA_FurnitureItem
PendingMaterialPath        : String
PendingRowName             : Name
ApplyMaterialTimerHandle   : Timer Handle
UndoManagerRef             : BP_UndoManager
PendingRestoredActor       : BP_FurnitureActor
FolderTree                 : Map String→String
FurnitureFolderTree        : Map String→String
MaterialFolderTree         : Map String→String
CurrentFolderPath, CurrentSearchText, CurrentPage(0-based), PageSize(=48)
ActiveSpecialCategory      : Name  ← "" / "Recent" / "Favorite"
— Resize Window —
bIsResizing                : Boolean
ResizeDirection            : Integer (0-8)
ResizeStartMousePos        : Vector2D
ResizeStartSize            : Vector2D
ResizeStartPosition        : Vector2D
```

---

## NGUYÊN TẮC

### Đầu session: đọc Session_State.md → Blueprint_Logic.md nếu cần
### Blueprint: luôn IsValid trước Object access. Tất cả nhánh merge về cuối.
### Cuối session: update Session_State.md + Blueprint_Logic.md
### Resize: xem WBP_ResizeWindow.md để biết chi tiết variables + logic
