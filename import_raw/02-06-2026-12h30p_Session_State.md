# Session State — Lighting_Mnger Interior Design Tool
**Cập nhật:** 02/06/2026 — 12:30 ICT
**Đọc file này ĐẦU TIÊN** khi bắt đầu session mới.

---

## TRẠNG THÁI HIỆN TẠI

**Giai đoạn:** Đã integrate vào master + Phase 0 xong. Sẵn sàng Phase 2 (MultiSelect).
**Đang làm trên:** PROJECT TỔNG (master) — không còn working copy riêng
**Engine:** UE5.5.4

---

## ROADMAP

```
✅ Phase 0: Material Copy/Paste (single-slot)        DONE 02/06
✅ Integration vào master                            DONE 02/06
⏭️ Phase 2: MultiSelect → Group → Combo → Mat v1.2   ← TIẾP THEO (plan_v3)
   Sau đó: Refactor Phase B → glTFRuntime → Supabase
```

---

## ĐÃ HOÀN THÀNH

### Change Material v1.1 (18–20/05/2026)
Tab Material/Furniture, Slot Swatches, Material Grid, Live Apply, Reset, Undo/Redo, Save/Load, Folder Tree, C++ FilterMaterialItems.

### UX Phase 2.1 (trước 25/05/2026)
Gizmo (rotate scale theo distance, axis lock), Nudge (Arrow + SurfaceType + snap 90°), Copy/Paste/Duplicate, Recent/Favorite.

### Resize Window — WBP_FurnitureInventory (27/05/2026)
8 hướng resize. Chi tiết: WBP_ResizeWindow.md.

### Plugin Migration — C++ → FurnitureToolkit (01–02/06/2026)
FurnitureFilterLibrary chuyển từ project module sang plugin `FurnitureToolkit`. Dependency: Core/CoreUObject/Engine + AssetRegistry. CoreRedirect chống đứt Blueprint ref. RuntimeTransformer vẫn là plugin riêng. Chi tiết: Plugin_Migration_Guide.md.

### Integration vào master (02/06/2026)
Đã tích hợp toàn bộ furniture tool vào project tổng. Chi tiết đầy đủ: Integration_Guide.md v1.3.
- Copy /cuong/ + 2 plugin (RuntimeTransformer + FurnitureToolkit)
- Shared code: Foff_GameInstance (+FurnitureInventoryRef), BP_FoffPlayerController (+AddFurnitureInput/RemoveFurnitureInput + 7 IA bindings)
- WBP_FOFF_ToolDemo: +TransformerPawnRef, +Button_FurnitureInventory, Spawn order (Then 11)
- GizmoTrace channel, Post Process + Custom Depth Stencil, Gizmo emissive
- DT_FurnitureCatalog reimport + MeshFolderPath + BoundingSize + EUW_CreateDataAssets
- Test pass (dùng Alt+P do GPU VRAM)

### Phase 0 — Material Copy/Paste single-slot (02/06/2026)
Copy vật liệu 1 slot → paste sang 1 slot khác (kể cả mesh khác). Trong WBP_FurnitureInventory:
- `ClipboardMaterialPath : String`
- `CopySlotMaterial` (Function) — đọc material tại slot đang chọn (override hoặc gốc qua Get Material → Get Object Path Name)
- `PasteSlotMaterial` (Custom Event) — Async Load → Create DMI → update thumbnail + AddRecentMaterial → debounce snapshot
- 2 nút BTN_CopySlotMaterial / BTN_PasteSlotMaterial
- Phím tắt Ctrl+Shift+C / Ctrl+Shift+V

---

## BACKLOG (làm sau, độc lập)

### Slot Material Highlight trên mesh (ghi 02/06/2026)
Khi chọn 1 material slot → phần mesh dùng slot đó "sáng lên" để người dùng thấy slot ứng với phần nào.
- **Cách làm:** tạo M_SlotHighlight (emissive) → swap vào slot đang chọn → restore khi bỏ chọn
- **Độ khó:** TRUNG BÌNH. Custom Depth Stencil không áp riêng material section được → phải swap material tạm
- **Bẫy chính:** highlight là visual tạm → KHÔNG được lọt vào MaterialOverrides/Save/Undo. Phải restore TRƯỚC CaptureSnapshot/Save
- **Khi làm:** sau Phase 2 (MultiSelect ưu tiên hơn)

---

## PHASE 2 — MULTISELECT (plan_v3) — TIẾP THEO

Thư mục plan_v3/ (13 file). Khi bắt đầu:
1. Đọc 09_AI_Implementation_Rules.md + 10_Execution_Discipline.md TRƯỚC
2. Mở PROGRESS.md → bắt đầu Sprint 1 vertical slice
3. Vertical slice Sprint 1: chọn 2 đồ → MOVE qua Pivot → validate Pivot Actor + gizmo collision (R5b)
4. Move-first: Rotate/Scale làm cuối (S1.T15)
5. Ghi DEVIATIONS.md mỗi khi lệch plan

⚠️ Backup project trước khi bắt đầu Sprint 1 (đụng 3 file lõi).

---

## KEY BUGS & FIXES (tích lũy)

| Bug | Fix |
|---|---|
| FilterMaterialItems FolderProp NULL | PropertyLink loop + Contains |
| TargetFurnitureActor invalid sau Undo/Redo | OnRestoreCompleted Event Dispatcher |
| MaterialPath không resolve | Full path `/Game/.../MI_Name.MI_Name` |
| Dead-end branches | Tất cả nhánh merge về cuối |
| Set Background Color không work (Tint A=0) | Image overlay + Set Color and Opacity |
| Accessed None trong ForEach | IsValid trước mọi Object access |
| Broadcast OnRestoreCompleted sai actor | RestoredBPActor var |
| Recent/Favorite không cập nhật số trang | SET FilteredItems + CurrentPage=0 + DisplayPage trước Return |
| Resize button không kéo được | Default trước Sequence, False branch trống |
| Window nhảy khi drag sau resize | Drag + resize cùng Slot as Canvas Slot |
| Plugin: Blueprint ref đứt khi đổi module | CoreRedirect trong DefaultEngine.ini |
| Integration: phím không hoạt động | Add Mapping Context node để trống → chọn LM_FurnitureInput |
| Integration: "Failed to add config file" | Cosmetic — Custom Depth setting vẫn apply |
| GPU crash khi stop PIE (master nặng) | Dùng Alt+P (Standalone Game) |
| GPU crash khi chạy Python BoundingSize | Restart editor + batch 30 + collect_garbage |
| Ctrl+Shift+V trigger paste mesh thay vì material | Shift check trong IA_FurniturePaste/Copy binding (KHÔNG cần block mapping) |

---

## LEARNINGS QUAN TRỌNG

### Phân biệt phím tắt có Shift — dùng Shift check, KHÔNG block mapping
Ctrl+Z vs Ctrl+Shift+Z, Ctrl+C vs Ctrl+Shift+C, Ctrl+V vs Ctrl+Shift+V:
- Trong binding của action KHÔNG có Shift → thêm `Branch Is Input Key Down(Shift)` → True thì return
- KHÔNG cần thêm dòng "phím không trigger" để block trong Mapping Context (thừa)

### Plugin migration — CoreRedirect là chìa khóa
Khi chuyển C++ class sang module mới → `[CoreRedirects] +ClassRedirects=...` trong DefaultEngine.ini giữ Blueprint reference không đứt.

### Master project nặng → GPU VRAM
Dùng Alt+P (Standalone) thay PIE. Python script load nhiều asset → batch + collect_garbage + restart editor.

---

## NGUYÊN TẮC

- Đầu session: đọc Session_State.md → plan_v3/ khi làm MultiSelect
- Blueprint: IsValid trước Object access. Tất cả nhánh Branch merge về cuối.
- Latent node (Async, Delay, Timer) chỉ trong Custom Event, KHÔNG trong Function
- Custom Event tạo trong Event Graph (right-click), KHÔNG trong panel Functions
- Node đúng: "Slot as Canvas Slot", "Get Object Path Name", Create Dynamic Material Instance (Target=PrimitiveComponent: vừa tạo DMI vừa set)
- R1-R5 cho code mới. Hard ref clear ở End Play/Destruct (chống VRAM leak)
- Cuối session: update Session_State.md + doc liên quan (version + ngày + giờ + phút)

---

## VARIABLES QUAN TRỌNG (WBP_FurnitureInventory)

```
CurrentInventoryMode    : E_InventoryMode
TargetFurnitureActor    : BP_FurnitureActor
SelectedSlotIndex       : Integer (-1)
ClipboardMaterialPath   : String              ← Phase 0
FilteredItems           : Array of DA_FurnitureItem
PendingMaterialPath, PendingRowName
CurrentPage(0-based), PageSize(48)
ActiveSpecialCategory   : Name ("" / "Recent" / "Favorite")
bIsResizing, ResizeDirection(0-8), ResizeStart...
```
