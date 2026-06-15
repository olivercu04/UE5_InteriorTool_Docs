# Session State — Lighting_Mnger Interior Design Tool
**Cập nhật:** 04/06/2026 — 15:30 ICT
**Đọc file này ĐẦU TIÊN** khi bắt đầu session mới.

---

## TRẠNG THÁI HIỆN TẠI

**Giai đoạn:** Sprint 1 (Multi-select) — 12/15 task. **Move-only multi-select đã SHIP.**
**Đang làm trên:** PROJECT TỔNG (master)
**Engine:** UE5.5.4
**Tiếp theo:** S1.T15 (Multi-Rotate/Scale qua Pivot) — đã có plan đầy đủ `T15_Multi_Rotate_Scale_Plan.md` v1.1 + prompt thực thi.

---

## ROADMAP

```
✅ Phase 0: Material Copy/Paste (single-slot)        DONE 02/06
✅ Integration vào master                            DONE 02/06
🔄 Sprint 1: Multi-select                            12/15 (Move-only shipped, còn T15)
⏭️ Sprint 2-7: Box → Group → Edit → Combo → Polish → Mat v1.2
   Sau đó: Refactor Phase B → glTFRuntime → Supabase
```

---

## SPRINT 1 — MULTI-SELECT (đã làm 03-04/06)

**Xong (12):** T1 variables, T2 S_ClipboardEntry, T3 BP_PivotActor, T4 SpawnOrUpdatePivot, T5 helper functions, T6 OnSelectionChanged, T7 Mouse Left Pressed refactor (Ctrl toggle), T8 WBP_MeshControls multi, T10 multi-Nudge, T11 multi-Copy/Paste/Duplicate, T12 multi-Snapshot, T14 Selection Info Bar + OnSceneChanged dispatcher.

**Skip:** T9 (payload struct), T13 (Ctrl+A → dời Sprint 6).

**Còn lại:** T15 Multi-Rotate/Scale. Có plan v1.1 riêng (Transform Composition). Move-only đã đủ ship → T15 là bổ sung.

**Kiến trúc multi-select (đã chốt & chạy):**
- `SelectedActors` (Array) + `PrimarySelectedActor` + `GizmoPivotActor` (BP_PivotActor)
- Pivot Actor pattern cho multi-gizmo (không sửa RuntimeTransformer)
- 2 stencil: 255 primary, 254 secondary
- Giữ song song state cũ `SelectedFurnitureActor` đến S7.T9 cleanup
- Chi tiết function: **BP_FurnitureInputManager.md v1.4**

---

## ĐÃ HOÀN THÀNH (trước Sprint 1)

### Change Material v1.1 (18–20/05) | UX Phase 2.1 (trước 25/05) | Resize Window (27/05)
### Plugin Migration C++ → FurnitureToolkit (01–02/06) — chi tiết Plugin_Migration_Guide.md
### Integration vào master (02/06) — chi tiết Integration_Guide.md v1.3
### Phase 0 — Material Copy/Paste single-slot (02/06)

---

## BACKLOG

### Scene Manager Panel (Photoshop-style layer panel) — Sprint 6 ⭐ (ghi 04/06)
Bảng danh sách mesh đã đặt, click select, group/ungroup, đổi tên, ẩn/hiện.
- **Infrastructure đã chuẩn bị:** `OnSceneChanged(AllActors)` dispatcher (T14). Broadcast thêm tại 3 chỗ (sau Spawn/Delete/RestoreSnapshot) khi làm.
- Có thể gộp với WBP_SceneOutliner (Sprint 6 T5-T7).

### Slot Material Highlight trên mesh (ghi 02/06)
M_SlotHighlight emissive swap vào slot đang chọn → restore TRƯỚC CaptureSnapshot/Save. Làm sau.

### DuplicateMesh select cả gốc + đồ mới (ghi 04/06)
Hiện chỉ select đồ mới (standard). Nếu muốn gốc+mới: build mảng độc lập (element-by-element), tránh aliasing + nesting. Optional.

---

## KEY BUGS & FIXES (tích lũy)

| Bug | Fix |
|---|---|
| FilterMaterialItems FolderProp NULL | PropertyLink loop + Contains |
| Dead-end branches | Tất cả nhánh merge về cuối |
| Accessed None trong ForEach | IsValid trước mọi Object access |
| Recent/Favorite không cập nhật trang | SET FilteredItems + CurrentPage=0 + DisplayPage trước Return |
| Plugin: Blueprint ref đứt | CoreRedirect trong DefaultEngine.ini |
| GPU crash khi stop PIE (master nặng) | Dùng Alt+P (Standalone Game) |
| Ctrl+Shift+V trigger paste mesh | Shift check trong IA binding |
| **Multi-select: gizmo không hiện khi chọn 2 đồ** | UpdateGizmo nhánh >=2 thêm DeactivateGizmo TRƯỚC ActivateGizmo |
| **Ctrl+Click bỏ chọn không tắt outline** | ToggleActor: Set Render Custom Depth=False sau Remove |
| **Undo multi-select chỉ restore 1 đồ** | T12 multi-snapshot + CaptureSnapshot sau ToggleActor |
| **DeselectAll crash "pending kill"** | IsValid trong ForEach trước access |
| **SpawnFurnitureCopy trả về None (bAutoSelect=False)** | Return Node phải nối NewActorCopy ở CẢ 2 nhánh True/False của Branch bAutoSelect |
| **DuplicateMesh infinite loop + spawn N×N đồ** | Phần spawn nối nhầm Loop Body của ForEach MaxRightEdge → chuyển sang COMPLETED. (KHÔNG phải aliasing) |

---

## LEARNINGS QUAN TRỌNG

### ⭐ Nesting bug — bài học lớn nhất session 03-04/06
Code chạy **1 lần** phải nối vào **Completed** của ForEach, KHÔNG nối Loop Body. Bug DuplicateMesh (infinite loop + spawn thừa N×N) do phần spawn nằm trong Loop Body của ForEach MaxRightEdge. Mất nhiều giờ debug sai hướng (nghi aliasing array).
→ **Khi gặp infinite loop / số lượng nhân lên: kiểm tra NESTING (Loop Body vs Completed) TRƯỚC khi nghi aliasing.**

### Multi-select gizmo lifecycle
Đổi target gizmo: luôn DeactivateGizmo TRƯỚC ActivateGizmo. Length 0/1/>=2 xử lý riêng trong UpdateGizmo.

### Array pass-by-reference
Function param Array thường pass-by-reference. SET LocalVar = param có thể không copy thật. ForEach một array trong khi ADD vào nó (hoặc array alias) → infinite loop. Build array bằng CLEAR + ForEach ADD element-by-element nếu cần độc lập. Dùng For Loop với captured length nếu nghi loop.

### SpawnFurnitureCopy với bAutoSelect
Cả 2 nhánh True/False của Branch bAutoSelect phải nối tới Return Node, nếu không nhánh False trả về None.

### Phân biệt phím Shift — Shift check, KHÔNG block mapping
Ctrl+Z vs Ctrl+Shift+Z...: `Branch Is Input Key Down(Shift)` → True return. Không cần dòng block trong Mapping Context.

### Plugin migration — CoreRedirect là chìa khóa
### Master project nặng → dùng Alt+P (Standalone) thay PIE

---

## NGUYÊN TẮC

- Đầu session: đọc Session_State.md → plan_v3/ khi làm MultiSelect/Group/Combo
- Blueprint: IsValid trước Object access. Tất cả nhánh Branch merge về cuối.
- Code chạy 1 lần → nối Completed của ForEach, KHÔNG Loop Body
- Latent node (Async, Delay, Timer) chỉ trong Custom Event, KHÔNG trong Function
- CaptureSnapshot SAU action, KHÔNG trong DeselectAll/DeselectMesh (infinite loop), KHÔNG mỗi frame
- BP_FurnitureActor: Cast → GET FurnitureMesh (KHÔNG dùng Get Static Mesh Component)
- R1-R5 cho code mới. Hard ref clear ở End Play/Destruct (chống VRAM leak)
- Cuối session: update Session_State.md + doc liên quan (version + ngày + giờ + phút)

---

## VARIABLES QUAN TRỌNG

### BP_FurnitureInputManager (v1.4) — xem BP_FurnitureInputManager.md
```
Multi-select: SelectedActors (Array), PrimarySelectedActor, GizmoPivotActor (BP_PivotActor), LastPivotTransform, ClipboardActors (Array S_ClipboardEntry)
Single cũ (bỏ S7.T9): SelectedFurnitureActor
Dispatchers: OnMeshSelected, OnMeshDeselected, OnSelectionChanged, OnSceneChanged
```

### WBP_FurnitureInventory
```
CurrentInventoryMode, TargetFurnitureActor, SelectedSlotIndex(-1), ClipboardMaterialPath
FilteredItems, CurrentPage(0), PageSize(48), ActiveSpecialCategory
bIsResizing, ResizeDirection(0-8)
```
