# Session State — Lighting_Mnger Interior Design Tool
**Cập nhật:** 10/06/2026 — 20:34 ICT
**Đọc file này ĐẦU TIÊN** khi bắt đầu session mới.

---

## TRẠNG THÁI HIỆN TẠI

**Giai đoạn:** Sprint 3 (Group) — **HOÀN THÀNH** + đợt regression-fix & refactor dual-dispatcher — **HOÀN THÀNH**
**Đang làm trên:** PROJECT TỔNG (master)
**Engine:** UE5.5.4
**TIẾP THEO:** Sprint 4 — Edit Mode + Nested Group (đã lập kế hoạch chi tiết — đọc `Sprint4_Plan_Opus.md`)
**Chi tiết flow đã đổi trong đợt này:** đọc `Sprint3_Regression_DualDispatcher_Log.md`

---

## ROADMAP

```
✅ Phase 0: Material Copy/Paste (single-slot)        DONE 02/06
✅ Integration vào master                            DONE 02/06
✅ Sprint 1: Multi-select                            15/15 COMPLETE
✅ Sprint 2: Box Select + Context Menu               9/9 COMPLETE — SHIPPED 08/06
✅ Sprint 3: Group cơ bản                           COMPLETE 10/06 (gồm regression-fix + refactor dispatcher)
🔄 Sprint 4: Edit Mode + Nested Group               ĐÃ LẬP KẾ HOẠCH — BẮT ĐẦU NGAY
⏭️ Sprint 5-7: Combo → Polish → Mat v1.2
   Sau đó: Refactor Phase B → glTFRuntime → Supabase
```

---

## SPRINT 3 — GROUP CƠ BẢN — COMPLETE ✅ (10/06/2026)

12 task + vertical slice đã xong. Kiến trúc: một group = một multi-selection, tái dùng Sprint 1.

**Đã implement:**
- Struct `S_GroupData` (GroupID, GroupName, ParentGroupID, bIsLocked)
- `BP_FurnitureActor.GroupID` (String, SaveGame, default "")
- `BP_GroupsContainer` (Actor thuần, EMSActorSaveInterface, singleton guard tag `"FurnitureGroupsContainer"`, ActorLoaded sync Groups → InputManager)
- `BP_FurnitureInputManager.Groups : Array<S_GroupData>` (in-memory truth, KHÔNG SaveGame, CLEAR ở End Play)
- 5 helper: `GenerateGroupID`, `GetGroupChildren`, `FindGroupData`, `ExpandSelectionWithGroups`, `PruneEmptyGroups`
- `CreateGroup` (Ctrl+G, auto-name "Nhóm N"), `UngroupActors` (Ctrl+Shift+G)
- Click/box select → `ExpandSelectionWithGroups`
- Info bar (WBP_MeshControls) hiện "📦 GroupName (N)" khi chọn group
- Snapshot v3: `S_FurniturePlacement.GroupID` + `S_SceneSnapshot.Groups`, Version=3

**Spawn `BP_GroupsContainer`:** trong `WBP_FOFF_ToolDemo` Event Construct (KHÔNG Level BP), sau spawn InputManager.

---

## ĐỢT REGRESSION-FIX + REFACTOR DUAL-DISPATCHER (10/06/2026) ✅

Sau khi đụng selection system lúc làm Group, phát sinh loạt regression. Đã fix hết + refactor gốc rễ.

**10 bug đã fix** (chi tiết root-cause ở `Sprint3_Regression_DualDispatcher_Log.md`):
1. Undo không restore group state → CaptureSnapshot impure timing → dùng var `TempGroups`
2. UngroupActors spam 3 snapshot + warning → find/remove/capture bị nằm trong Loop Body → tách ra Completed
3. FoundIdx warning [0/0] → class var không reset → SET -1 đầu function
4. Undo về deselect không tắt outline/gizmo → nhánh empty gọi DeselectAll + DeactivateGizmo
5. Ctrl+click group không cộng dồn → Step 7 (Mouse Pressed) bỏ nhánh Ctrl, mọi click defer
6. Replace mesh không liên tục → thiếu node ADD New Actor → LocalNewActors trong loop
7. Replace lúc inventory minimize không bung → EnsureExpanded đầu EnterReplaceMode
8. Replace sai mesh (replace mesh 1 thay vì mesh đang chọn) → OnMeshSelected SET nhầm `MeshToReplace` (single chết) thay vì `MeshesToReplace` (array)
9. Material/Replace-folder không auto-update khi đổi selection → logic nằm trên `OnMeshSelected` (đã ngừng fire) → chuyển sang `OnSelectionChanged`
10. Accessed None `TargetFurnitureActor` → nhánh material thiếu guard IsValid (deselect fire empty)

**REFACTOR LỚN — dual-dispatcher → single source of truth:**
- **XÓA** dispatcher `OnMeshSelected` + `OnMeshDeselected`
- **`OnSelectionChanged(Actors, Primary)` = dispatcher selection DUY NHẤT**
- `SelectSingleActor`: bỏ broadcast OnMeshSelected (giữ OnSelectionChanged)
- `SpawnFurnitureCopy`: thay cụm select thủ công bằng `SelectActors(Make Array(copy))` (tự lo outline 255 + gizmo + OnSelectionChanged)
- `DeselectMesh` / `DeselectAll`: bỏ broadcast OnMeshDeselected (giữ phần clear state)
- Inventory: bind `OnSelectionChanged` → `OnSelectionChangedMaterial` → gọi handler `OnMeshSelected(Primary)`; gỡ bind OnMeshSelected + OnMeshDeselected + handler OnMeshDeselected
- **XÓA** biến chết `MeshToReplace` (single) — chỉ còn `MeshesToReplace` (array)

**Regression test 6 case cuối: PASS HẾT.**

---

## ĐÃ HOÀN THÀNH (trước Sprint 3)

Change Material v1.1 (18–20/05) | UX Phase 2.1 | Resize Window (27/05) | Plugin Migration C++ (01–02/06) | Integration master (02/06) | Phase 0 Material Copy/Paste | Sprint 1 Multi-select (15 task) | Sprint 2 Box+Context (9 task)

---

## KEY BUGS & FIXES (tích lũy)

| Bug | Fix |
|---|---|
| EnsureExpanded không expand | Thiếu HB_Main_Content — phải match BTN_MinimizedIcon OnClicked đầy đủ |
| CB_Replace không toggle off | Toggle check bIsReplaceMode TRƯỚC guard |
| Event không có local var | Tạo Function riêng (F_ExecuteReplace, F_OpenMaterialMode) |
| Undo nhảy cóc | CLEAR TempSelectedIndices đầu CaptureSnapshot |
| Delete destroy InputManager | Target = Array Element, KHÔNG để trống |
| Box: chọn lệch | DPI — chia Project World To Screen cho Get Viewport Scale |
| Box: click-drag mesh → single select ngay | Defer PendingClickActor + ngưỡng 5px |
| Ctrl+Shift+V trigger paste nhầm | Shift check trong IA binding (áp dụng luôn cho Ctrl+X) |
| Multi-select gizmo không hiện | UpdateGizmo nhánh >=2: DeactivateGizmo TRƯỚC ActivateGizmo |
| **Undo không restore Groups** | **CaptureSnapshot: Call GetGroupsForSnapshot → SET TempGroups → Make node đọc TempGroups (impure output chỉ valid sau exec của nó)** |
| **UngroupActors 3 snapshot + warning [0/0]** | **find/remove/capture phải ở ForEach Completed, KHÔNG Loop Body** |
| **FoundIdx warning [0/0]** | **SET FoundIdx = -1 đầu function (class var không tự reset theo default)** |
| **Undo về deselect không tắt outline/gizmo** | **RestoreSnapshot nhánh SelectedActors.Length==0 → DeselectAll + DeactivateGizmo, merge về OnRestoreCompleted** |
| **Ctrl+click group không cộng dồn** | **Mouse Pressed Step 7: bỏ nhánh Ctrl, MỌI click defer qua PendingClickActor; Ctrl resolve ở OnLMBReleased (ExpandSelectionWithGroups → ToggleActor)** |
| **Replace mesh không liên tục** | **Thiếu node ADD New Actor → LocalNewActors trong Loop Body của F_ExecuteReplace** |
| **Replace lúc minimize không bung** | **Call EnsureExpanded đầu EnterReplaceMode (minimize vẫn IsValid+InViewport nên StartReplaceMode "dùng luôn" mà không bung)** |
| **Replace sai mesh** | **OnMeshSelected nhánh replace: SET MeshesToReplace (array) = InputManager.SelectedActors, KHÔNG SET MeshToReplace (single chết)** |
| **Material/Replace-folder không auto-update** | **Chuyển trigger từ OnMeshSelected (đã chết) sang OnSelectionChanged → OnSelectionChangedMaterial → OnMeshSelected(Primary)** |
| **Accessed None TargetFurnitureActor** | **Nhánh material thêm Branch IsValid(SelectedActor): True→refresh, False→SET None+collapse+SelectedSlotIndex=-1 (deselect fire OnSelectionChanged rỗng)** |
| **Double-fire handler / dual dispatcher** | **Hợp nhất về 1 dispatcher OnSelectionChanged, xóa OnMeshSelected + OnMeshDeselected** |

---

## LEARNINGS QUAN TRỌNG

- **Event không có Local Variable** → tách Function (F_ExecuteReplace, F_OpenMaterialMode)
- **Toggle check TRƯỚC guard** trong callback mode (CB_Replace)
- **EnsureExpanded phải match source event chính xác** — thiếu widget nào là fail
- **CLEAR/SET class var đầu hàm** nếu persistent (TempSelectedIndices, FoundIdx, TempGroups) — default chỉ áp dụng lúc construct, KHÔNG reset mỗi lần gọi
- **Code 1 lần → Completed, KHÔNG Loop Body** — không chỉ snapshot mà cả cụm find/remove/broadcast
- **CaptureSnapshot SAU action**
- **Impure function (có exec pin): output chỉ "đóng băng" giá trị TẠI exec của nó.** Nếu node đọc chạy trước exec → đọc default. Fix: gọi sớm → SET temp var → node đọc temp var (TempGroups)
- **Destroy target = element đang duyệt**, không để trống
- **IsValid trước MỌI Object access** — đặc biệt handler nhận selection có thể rỗng (deselect fire OnSelectionChanged với Primary invalid)
- **Tất cả nhánh Branch merge về cuối** (cả nhánh empty/False phải về Broadcast/OnRestoreCompleted)
- **Latent node chỉ trong Custom Event**
- **Bind dispatcher PHẢI ở Event Construct**, KHÔNG đặt trong handler (handler không fire thì bind không chạy)
- **Single source of truth**: 1 dispatcher selection (OnSelectionChanged), 1 biến replace (MeshesToReplace). Dual-dispatcher / dual-var là gốc của loạt regression — feature gắn lên dispatcher chết thì lặng lẽ ngừng update
- **Kỷ luật debug**: dùng print QUYẾT ĐỊNH (phân biệt capture vs restore; đếm số lần gọi; in ActionName + sel count) thay vì đoán mò. Mỗi lần đoán sai tốn 1 vòng — print 1 lần là xong
- **Mọi click trên đồ đều defer** qua PendingClickActor (Mouse Pressed); phân giải single/group/Ctrl ở OnLMBReleased — không xử lý ngay ở Pressed

---

## KIẾN TRÚC SELECTION (sau refactor 10/06)

```
Mutators (BP_FurnitureInputManager):
  SelectActors / DeselectAll / ToggleActor / SelectSingleActor / SpawnFurnitureCopy
      → tất cả fire OnSelectionChanged(Actors, Primary)   ← DISPATCHER DUY NHẤT

Listeners:
  WBP_MeshControls   → info bar (>= 2 đồ)
  WBP_FurnitureInventory → OnSelectionChangedMaterial → OnMeshSelected(Primary)
                            (replace folder nav + material swatch refresh)

ĐÃ XÓA: OnMeshSelected, OnMeshDeselected (dispatcher)
ĐÃ XÓA: MeshToReplace (single) — chỉ còn MeshesToReplace (array)
```

---

## BIẾN / DISPATCHER THAY ĐỔI (đợt này)

| Nơi | Thay đổi |
|---|---|
| BP_UndoManager | **+ `TempGroups : Array<S_GroupData>`** (no SaveGame) — đệm cho CaptureSnapshot |
| BP_FurnitureInputManager | **− dispatcher `OnMeshSelected`** (xóa) |
| BP_FurnitureInputManager | **− dispatcher `OnMeshDeselected`** (xóa) |
| BP_FurnitureInputManager | **− `MeshToReplace`** (single, xóa) — dùng `MeshesToReplace` (array) |
| WBP_FurnitureInventory | **− custom event handler `OnMeshDeselected`** (xóa); **+ `OnSelectionChangedMaterial`** |

---

## TIẾP THEO — SPRINT 4 (Edit Mode + Nested Group)

**Plan:** `Sprint4_Plan_Opus.md`. Insight: Edit Mode = SELECTION SCOPE FILTER (không phải mode mới).
- Keystone: `ResolveSelectionUnit(Actor, EditScope)` + helper đệ quy (`GetGroupRoot`, `GetChildGroups`, `GetAllDescendantActors`, `GetGroupsInHierarchy`, `WalkUpUntilParent`)
- `EditModeStack : Array<String>`
- Nested group LÀM LUÔN (bắt buộc cho combo)
- MVP không dim nhưng cắm hook (stub `ApplyEditModeVisual`/`RemoveEditModeVisual`, reserve Stencil 200)
- `GetGroupsInHierarchy` = bridge cho Sprint 5 combo serialize

---

## NGUYÊN TẮC

- Đầu session: đọc Session_State.md → Sprint4_Plan_Opus.md khi làm Edit/Nested
- R1-R5 cho code mới. Hard ref clear ở End Play/Destruct
- Cuối session: update Session_State.md + doc liên quan (version + ngày + giờ + phút)
- Single source of truth: 1 dispatcher selection, tránh dual-var/dual-dispatcher
- Print quyết định khi debug, không đoán mò
