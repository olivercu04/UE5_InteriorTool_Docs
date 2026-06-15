# Session State — Lighting_Mnger Interior Design Tool
**Cập nhật:** 07/06/2026 — 22:40 ICT
**Đọc file này ĐẦU TIÊN** khi bắt đầu session mới.

---

## TRẠNG THÁI HIỆN TẠI

**Giai đoạn:** Sprint 2 (Box Select + Context Menu) — **gần xong.**
**Đang làm trên:** PROJECT TỔNG (master)
**Engine:** UE5.5.4
**Tiếp theo trong Sprint 2:** implement 2 callback STUB (Change Material + Replace); test đầy đủ box select; (optional) Esc-cancel box, Cut.
**Sau Sprint 2:** Sprint 3 — Group cơ bản (theo plan_v3/04_Sprint_Details.md).

---

## ROADMAP

```
✅ Phase 0: Material Copy/Paste (single-slot)        DONE 02/06
✅ Integration vào master                            DONE 02/06
✅ Sprint 1: Multi-select                            15/15 COMPLETE (Move+Rotate+Scale shipped)
🔄 Sprint 2: Box Select + Context Menu               ~6/7 task (còn 2 callback stub + test)
⏭️ Sprint 3-7: Group → Edit → Combo → Polish → Mat v1.2
   Sau đó: Refactor Phase B → glTFRuntime → Supabase
```

---

## SPRINT 2 — BOX SELECT + CONTEXT MENU (06-07/06) — gần xong

### ĐÃ XONG
- **T1 — WBP_BoxSelectOverlay:** Canvas → Border (outer, control visibility) → Border_Box (con, fill xanh trong suốt). Functions ShowBox/HideBox/UpdateBox(StartPos,EndPos).
- **T2 — Box Select logic:** xuyên suốt Mouse Left Pressed (defer) + Event Tick (vẽ khung + ngưỡng 5px) + OnLMBReleased (chốt) + FinishBoxSelect. Chi tiết: **BP_FurnitureInputManager.md v1.5**.
- **T3 — WBP_ContextMenu + WBP_ContextMenuItem + WBP_MenuSeparator.**
- **T4 — Right-click handler** (time-based + check camera pan để không bật menu khi vừa pan xong).
- **T5 — SelectSimilarMesh** (so sánh MeshPath String, không load DA).
- **T6 — ResetRotation + DeleteSelected callback.**
- **FIX bug Undo nhảy cóc** (stale TempSelectedIndices) — xem KEY BUGS.

### CÒN LẠI
- **CB_ChangeMaterial + CB_Replace** từ context menu — hiện là STUB. Cần xem cách WBP_MeshControls trigger material mode / EnterReplaceMode để tái dùng.
- **Test đầy đủ box select:** (1) kéo khung vùng trống chọn nhiều, (2) khung trống không crash, (3) Ctrl+kéo cộng dồn, (4) click đơn deselect, (5) Undo sequence sau khi xóa debug.
- **(Optional)** Esc-cancel box select (T1 plan), Cut Ctrl+X (T7).
- **Xóa Print String debug** — đang làm (OLR-SELECT, OLR-DESELECT, POST-DESEL, SEL-AT-CAP, CAP, UpdateGizmo, IM count, LMB start, Step3, Tick pending, "Box starting").

### Kiến trúc Box Select (đã chốt & chạy)
- **DEFER click:** Mouse Left Pressed chỉ ghi nhận (BoxStartPos + cờ + PendingClickActor), KHÔNG select ngay → phân biệt click-chọn vs kéo-box-từ-mesh.
- **3 điểm tương tác:** Mouse Left Pressed (ghi nhận) → Event Tick (vẽ khung, ngưỡng 5px) → OnLMBReleased (chốt selection, đường chính).
- **Cờ `bLMBHeld`** thay `Is Input Key Down` (không tin cậy cho mouse trong viewport capture).
- **DPI fix:** FinishBoxSelect chia `Project World To Screen` cho `Get Viewport Scale` để cùng hệ với `Get Mouse Position on Viewport`.
- Chọn theo **PIVOT/origin** (1 điểm), không bounding box — đúng ý đồ.

---

## SPRINT 1 — MULTI-SELECT (03-05/06) — COMPLETE 15/15

T1-T15 xong (skip T9 payload, T13 Ctrl+A dời Sprint 6). Multi-select Move+Rotate+Scale qua Pivot (Transform Composition) shipped. Chi tiết: BP_FurnitureInputManager.md, BP_PivotActor.md, T15_Multi_Rotate_Scale_Plan.md.

---

## ĐÃ HOÀN THÀNH (trước Sprint 1)
Change Material v1.1 (18–20/05) | UX Phase 2.1 (trước 25/05) | Resize Window (27/05) | Plugin Migration C++ → FurnitureToolkit (01–02/06) | Integration vào master (02/06) | Phase 0 Material Copy/Paste single-slot (02/06).

---

## BACKLOG

### Scene Manager Panel (Photoshop-style layer panel) — Sprint 6 ⭐
Bảng danh sách mesh đã đặt, click select, group/ungroup, đổi tên, ẩn/hiện. Infrastructure: `OnSceneChanged(AllActors)` dispatcher (T14) — broadcast thêm 3 chỗ (sau Spawn/Delete/RestoreSnapshot) khi làm.

### Slot Material Highlight trên mesh (ghi 02/06)
M_SlotHighlight emissive swap vào slot đang chọn → restore TRƯỚC CaptureSnapshot/Save.

### DuplicateMesh select cả gốc + đồ mới (ghi 04/06) — Optional.

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
| Multi-select: gizmo không hiện khi chọn 2 đồ | UpdateGizmo nhánh >=2 DeactivateGizmo TRƯỚC ActivateGizmo |
| Ctrl+Click bỏ chọn không tắt outline | ToggleActor: Set Render Custom Depth=False sau Remove |
| Undo multi-select chỉ restore 1 đồ | T12 multi-snapshot + CaptureSnapshot sau ToggleActor |
| DeselectAll crash "pending kill" | IsValid trong ForEach trước access |
| SpawnFurnitureCopy trả None (bAutoSelect=False) | Return Node nối NewActorCopy ở CẢ 2 nhánh True/False |
| DuplicateMesh infinite loop + spawn N×N | Phần spawn nối nhầm Loop Body → chuyển sang COMPLETED |
| Chuyển mode khi multi-select → gizmo về đồ đơn | WBP_MeshControls kiểm tra SelectedActors.Length>=2 → dùng GizmoPivotActor |
| **Box: khung không render** | Guard inventory (Tick không bị gate bởi LM_FurnitureInput) — IsValid + Is In Viewport nested Branch |
| **Box: khung dính sau khi thả** | Dùng cờ `bLMBHeld` thay `Is Input Key Down` (không tin cậy cho mouse trong capture) |
| **Box/single: gizmo nháy 1 frame trước mesh** | Chuyển ActivateGizmo/FinishBoxSelect/SelectSingleActor sang OnLMBReleased (input-event timing, chạy trước world Tick) |
| **Box: chọn nhầm/lệch đồ** | DPI mismatch — chia Project World To Screen cho Get Viewport Scale |
| **Box: click-drag trên mesh → single-select ngay** | Defer bằng PendingClickActor + ngưỡng 5px |
| **Delete destroy chính InputManager** | Target của Destroy = Array Element, KHÔNG để trống (mặc định self) |
| **⭐ Undo nhảy cóc khi xen kẽ Select/Deselect** | CLEAR TempSelectedIndices ngay ĐẦU hàm CaptureSnapshot (class var giữ stale; nhánh deselect bypass đoạn build Step 4) |

---

## LEARNINGS QUAN TRỌNG

### ⭐ Stale class variable — bài học lớn nhất session 07/06
`TempSelectedIndices` (class var) giữ giá trị giữa các lần gọi CaptureSnapshot. Khi execution đi nhánh deselect bypass đoạn build → giá trị cũ lọt vào snapshot → Undo nhảy cóc. → **CLEAR class var ở ĐẦU hàm.** Phụ: print debug đặt trong ForEach Step 3 in 1 lần/mesh → ngỡ "double capture" (sai hướng). → **Print debug trên MAIN execution line, không trong loop body.**

### ⭐ Timing input event vs world Tick — Box Select
ActivateGizmo gọi từ **Event Tick** race với Tick nội bộ RuntimeTransformer → gizmo nháy. Gọi từ **input event** (OnLMBReleased) chạy TRƯỚC world Tick → không nháy. → **Việc làm-1-lần liên quan gizmo/select đặt ở input event, KHÔNG ở Tick.**

### ⭐ DEFER pattern (PendingClickActor + ngưỡng 5px)
Để phân biệt click-chọn-1-đồ vs bắt-đầu-kéo-box: KHÔNG select lúc bấm, chỉ ghi nhận; chốt lúc thả/khi vượt ngưỡng. Tái dùng được cho mọi gesture click-vs-drag.

### ⭐ Tick không bị gate bởi Input Mapping Context
Enhanced Input action tự tắt khi gỡ context (inventory đóng), nhưng **Event Tick chạy mọi frame bất kể context** → phải guard thủ công (IsValid + Is In Viewport).

### ⭐ Nesting bug (session 03-04/06)
Code chạy 1 lần PHẢI nối **Completed** của ForEach, KHÔNG Loop Body. Khi infinite loop / số lượng nhân lên → kiểm tra NESTING trước khi nghi aliasing.

### ⭐ Transform Composition — T15
Multi-rotate/scale qua Pivot: `Make Relative Transform` lúc drag-start → `Compose Transforms` mỗi frame. RefreshOffsets gọi tại drag-start, KHÔNG mỗi frame.

### Khác
- Array pass-by-reference → CLEAR + ForEach ADD element-by-element nếu cần độc lập.
- Set Actor Transform mỗi frame → Teleport=True (tránh physics sweep giật).
- Blueprint AND KHÔNG short-circuit → nested Branch guard None.
- Master project nặng → Alt+P (Standalone) thay PIE.

---

## NGUYÊN TẮC

- Đầu session: đọc Session_State.md → plan_v3/ khi làm Group/Combo/Material v1.2
- Blueprint: IsValid trước Object access. Tất cả nhánh Branch merge về cuối
- Code chạy 1 lần → nối Completed của ForEach, KHÔNG Loop Body
- Latent node (Async, Delay, Timer) chỉ trong Custom Event, KHÔNG trong Function
- CaptureSnapshot SAU action; KHÔNG trong DeselectAll/DeselectMesh/ToggleActor (caller tự gọi); KHÔNG mỗi frame
- **CLEAR class var ở đầu hàm nếu nó persistent giữa các lần gọi (chống stale)**
- **Việc làm-1-lần liên quan gizmo/select → đặt input event, không Tick (chống nháy)**
- Print debug đặt main execution line, KHÔNG trong loop body
- BP_FurnitureActor: Cast → GET FurnitureMesh (KHÔNG dùng Get Static Mesh Component)
- Destroy Actor: target = đồ cần xóa (Array Element), KHÔNG để trống
- R1-R5 cho code mới. Hard ref clear ở End Play/Destruct (chống VRAM leak)
- Cuối session: update Session_State.md + doc liên quan (version + ngày + giờ + phút)

---

## VARIABLES QUAN TRỌNG

### BP_FurnitureInputManager (v1.5) — xem BP_FurnitureInputManager.md
```
Multi-select: SelectedActors (Array), PrimarySelectedActor, GizmoPivotActor (BP_PivotActor), LastPivotTransform, ClipboardActors (Array S_ClipboardEntry)
Box Select:   BoxSelectOverlayRef, BoxStartPos (Vector2D), bIsPendingBoxSelect, bIsBoxSelecting, bLMBHeld, PendingClickActor
Context Menu: ContextMenuRef
Single cũ (bỏ S7.T9): SelectedFurnitureActor
Dispatchers: OnMeshSelected, OnMeshDeselected, OnSelectionChanged, OnSceneChanged
```

### BP_UndoManager (v1.5)
```
SnapshotHistory (Array S_SceneSnapshot), CurrentIndex, MaxSteps(50)
TempMeshes, TempSelectedIndices (CLEAR đầu hàm CaptureSnapshot!), RestoredActors
SpawnedActors, FoundActor, RestoredBPActor (hard ref — clear ở End Play)
```

### WBP_FurnitureInventory
```
CurrentInventoryMode, TargetFurnitureActor, SelectedSlotIndex(-1), ClipboardMaterialPath
FilteredItems, CurrentPage(0), PageSize(48), ActiveSpecialCategory
bIsResizing, ResizeDirection(0-8)
```
