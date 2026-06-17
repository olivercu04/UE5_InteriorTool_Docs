# DEVIATIONS — Lệch khỏi plan gốc (plan_v3)
**HỢP NHẤT TỪ 3 file:** 07-06_DEVIATIONS.md (Sprint 1+2) + DEVIATIONS.md (12/06, Sprint 3+4) + Sprint4BugFix_additions.md (15/06)
**Cập nhật:** 15/06/2026

> File này ghi mọi deviation so với plan gốc (plan_v3/04_Sprint_Details.md).
> Không phải tất cả deviation đều xấu — một số là fix đúng, một số là scope cut có chủ ý.

---

## CÁCH DÙNG

- **Lệch nhỏ** (tên biến, thứ tự node, vị trí widget) → KHÔNG cần ghi
- **Lệch về logic/kiến trúc/scope** → BẮT BUỘC ghi 1 dòng
- Ghi **NGAY lúc lệch**, không để cuối ngày (sẽ quên)
- Cuối mỗi sprint: đọc lại. Nếu 1 vùng có > 5 deviation → plan vùng đó sai → cập nhật plan_v3

**Phân loại lý do:**
- `[PLAN-SAI]` — plan sai, thực tế đúng hơn → cần sửa plan
- `[SCOPE]` — thu hẹp scope có chủ đích, dời sang sau
- `[NODE]` — node UE5 khác plan giả định
- `[PERF]` — đổi vì hiệu năng
- `[BUG]` — đổi để fix bug phát sinh

---

## SPRINT 1 — Multi-select

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| 03/06 | T3 | BP_PivotActor parent = Actor | Parent = StaticMeshActor | ActivateGizmo của RuntimeTransformer chỉ nhận StaticMeshActor | [NODE] |
| 03/06 | T3 | Tick check "Not Equal Transform" trước Apply | Bỏ check, chỉ dùng IsValid(AttachedActors[0]) guard | UE5 không có node "Not Equal (Transform)" tiện dùng; Transform Composition không tích lũy lỗi nên chạy mỗi frame vô hại | [NODE] |
| 03/06 | T5 | UpdateGizmo nhánh >=2 chỉ ActivateGizmo | Thêm DeactivateGizmo TRƯỚC ActivateGizmo | Plan bỏ sót — không deactivate trước thì gizmo cũ không nhả, gizmo mới không hiện | [PLAN-SAI] |
| 03/06 | T5 | ToggleActor remove khỏi SelectedActors | Thêm Set Render Custom Depth=False sau khi Remove | UpdateOutlineState không clear stencil của actor vừa bị remove → outline còn sót | [PLAN-SAI] |
| 03/06 | T7 | ToggleActor xong là đủ | Thêm CaptureSnapshot("Select") sau toggle | Không capture thì Undo mất trạng thái multi-select | [BUG] |
| 03/06 | T8 | ET_SelectionCount nằm trong T8 | Dời sang T14 (Selection Info Bar) | T14 là task đúng cho widget này, tránh trùng | [SCOPE] |
| 04/06 | T11 | DuplicateMesh select cả gốc + đồ mới | Chỉ select đồ MỚI (LocalSpawned), giống PasteMesh | Logic "gốc + mới" gây bug; chỉ select đồ mới là standard behavior (Blender/Illustrator). Feature gốc+mới dời sau | [SCOPE] |
| 04/06 | T11 | SpawnFurnitureCopy không return value | Thêm output `NewActor` + param `bAutoSelect` | Cần lấy reference đồ mới để build LocalSpawned; bAutoSelect=False để select thủ công ở cuối | [PLAN-SAI] |
| 04/06 | T13 | Ctrl+A Select All trong Sprint 1 | SKIP → dời Sprint 6 | Select All ít hữu dụng cho interior design (thường chọn nhóm/vùng, không phải tất cả) | [SCOPE] |
| 04/06 | T14 | Chỉ ET_SelectionCount | Thêm `OnSceneChanged` dispatcher | Chuẩn bị infrastructure cho Scene Manager Panel (Sprint 6) — bind auto-refresh | [SCOPE] |

---

## SPRINT 2 — Box Select + Context Menu

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| 06/06 | T2 | Select đồ ngay khi Mouse Pressed | DEFER: ghi PendingClickActor, chốt ở thả chuột | Phân biệt click-chọn-1-đồ vs bắt-đầu-kéo-box-từ-trên-mesh; select ngay thì không kéo box được | [PLAN-SAI] |
| 06/06 | T2 | Box select + ActivateGizmo trong Event Tick | Chuyển FinishBoxSelect/SelectSingleActor sang OnLMBReleased; Tick chỉ vẽ khung + fallback | ActivateGizmo trong Tick race với Tick RuntimeTransformer → gizmo nháy 1 frame | [BUG] |
| 06/06 | T2 | Dùng Is Input Key Down(LMB) phát hiện thả | Dùng cờ bool `bLMBHeld` (SET tay) | Is Input Key Down không tin cậy cho mouse button khi viewport capture → khung dính sau thả | [NODE] |
| 06/06 | T2 | So tọa độ mouse vs world-to-screen trực tiếp | Chia Project World To Screen cho Get Viewport Scale | DPI mismatch: mouse = logical coords, project = raw pixels → chọn nhầm đồ | [NODE] |
| 06/06 | T2 | (plan không nói) | Thêm guard inventory (IsValid + Is In Viewport) cho box trong Tick | Event Tick KHÔNG bị gate bởi LM_FurnitureInput context như Enhanced Input → box bật cả khi inventory đóng | [PLAN-SAI] |
| 07/06 | T2 | (plan không nói) | Thêm CLEAR TempSelectedIndices đầu hàm CaptureSnapshot | Bug Undo nhảy cóc khi xen kẽ Select/Deselect — class var giữ stale, nhánh deselect bypass đoạn build Step 4 | [BUG] |
| 06/06 | T6 | Delete dùng target mặc định | Destroy target = Array Element (đồ đang duyệt) | Để trống target = destroy chính InputManager (self) | [BUG] |
| 06/06 | T1/T7 | Esc-cancel box (T1), Cut Ctrl+X (T7) | Chưa làm → để optional cuối sprint | Ưu tiên core box select + context menu trước | [SCOPE] |
| 06/06 | T3-T4 | (thứ tự plan) | Làm Context Menu (T3-T4) TRƯỚC Box Select (T1-T2) | Theo "thứ tự thực thi đề xuất": context menu rủi ro thấp làm trước | [SCOPE] |
| 06/06 | T5 | (callback đầy đủ) | CB_ChangeMaterial + CB_Replace để STUB | Cần tra cách reuse WBP_MeshControls material mode/EnterReplaceMode — làm session sau | [SCOPE] |

---

## SPRINT 3 — GROUP CƠ BẢN

| # | Plan gốc nói | Thực tế | Lý do | Kết quả |
|---|---|---|---|---|
| D3-1 | Có WBP_GroupNameDialog (dialog đặt tên nhóm) | Bỏ hoàn toàn — auto-name "Nhóm N" | Đã chốt trước sprint (không cần dialog cho MVP) | ✅ Tốt hơn — ít friction, rename Sprint 6 |
| D3-2 | CaptureSnapshot gọi GetGroupsForSnapshot trực tiếp khi build Make S_SceneSnapshot | Dùng **TempGroups class var** làm buffer: SET TempGroups trước, Make đọc TempGroups | Bug impure-timing: GetGroupsForSnapshot không đảm bảo chạy xong trước Make | ✅ Fix đúng |
| D3-3 | UngroupActors: find index → remove → capture trong ForEach Loop Body | Chuyển toàn bộ sang **ForEach Completed** | Bug: trong Loop Body → 3 snapshot per ungroup + invalid-index warning | ✅ Fix đúng |
| D3-4 | Mouse Left Pressed Step 7: Branch IsCtrlDown → ToggleActor ngay | **Bỏ Branch Ctrl ở Step 7** — mọi click defer qua PendingClickActor; Ctrl phân giải ở OnLMBReleased | Ctrl+click group không cộng dồn được | ✅ Fix đúng, nhất quán hơn |
| D3-5 | Giữ dispatcher OnMeshSelected + OnMeshDeselected song song | **XÓA cả hai** — OnSelectionChanged là DUY NHẤT | Dual-dispatcher gây loạt bug khó trace | ✅ Refactor đúng |
| D3-6 | MeshToReplace : BP_FurnitureActor (single) | **XÓA** — chỉ còn MeshesToReplace (Array) | MeshToReplace dead variable, gây confusion | ✅ Dọn đúng |
| D3-7 | FoundIdx là local variable của UngroupActors | Đặt thành **class variable**, SET -1 đầu hàm | Blueprint function không có local Integer với default value dễ control | ✅ Acceptable workaround |
| D3-8 | Snapshot Version=3 trong plan | Thực tế vẫn Version=3 | Khớp plan | ✅ |
| D3-9 | Plan không nhắc PendingClickActor reset | Thêm **SET PendingClickActor = None** sau mỗi xử lý click | Bug: deselect click re-select đồ cũ vì PendingClickActor còn stale | ✅ Fix đúng |
| D3-10 | RestoreSnapshot: re-fire selection không xử lý empty case | Thêm nhánh **SelectedActors.Length==0 → DeselectAll + DeactivateGizmo** | Undo về snapshot deselect không tắt gizmo/outline | ✅ Fix đúng |

---

## SPRINT 4 — EDIT MODE + NESTED GROUP (SHIPPED 12/06/2026)

| # | Plan gốc nói | Thực tế | Lý do | Kết quả |
|---|---|---|---|---|
| D4-1 | Trigger = nút info bar + Enter key (D3: hỏi lại khi làm T4) | **MVP: nút info bar ONLY**. Esc KHÔNG dùng (= thoát PIE). Phím tắt TBD | Esc đang là system key trong UE5 editor | 🟡 Acceptable MVP |
| D4-2 | ExitEditModeOneLevel re-select: `GetGroupChildren(Exited)→Get(0)→ExpandSelectionWithGroups` | `GetAllDescendantActors(Exited)` **trực tiếp** → SelectActors | GetGroupChildren rỗng với nested thuần (actor ở sub-group, không có GroupID=Exited) | ✅ Fix đúng, gọn hơn |
| D4-3 | ResolveSelectionUnit: CASE 1 (đồ rời) kiểm tra trước CASE 3 (edit scope) | **Đảo thứ tự: edit scope kiểm tra TRƯỚC** | Q9a: đồ rời ngoài scope phải bị bỏ qua khi đang edit | ✅ Fix đúng |
| D4-4 | Click ngoài scope khi edit → behavior chưa định | **CLEAR selection, VẪN ở edit mode** | Tránh đụng caller defer mong manh cho MVP | 🟡 Acceptable MVP |
| D4-5 | GetGroupsInHierarchy đặt trong helper list chính | Implement đầy đủ ngay T1 | Bridge cho Combo S5 — bắt buộc | ✅ |
| D4-6 | 03_Code_Inheritance_Strategy.md ghi EditingGroupID trong snapshot | **Không snapshot EditModeStack** (D6 giữ nguyên lúc đó) | File 03 viết trước D6; BP_UndoManager v1.6 không có field này | ✅ File 03 là outdated — đã fix trong A12 (xem D4BF-2) |
| D4-7 | PruneEmptyGroups dùng GetGroupChildren.Length==0 | Đổi sang **GetAllDescendantActors.Length==0** | GetGroupChildren chỉ check direct members → prune oan group cha có sub-groups | ✅ DONE T7 |
| D4-8 | UngroupActors → deep ungroup cả cây | **Peel-one-level** (WalkUpUntilParent+B1+B2+B3) | Deep ungroup phá toàn bộ cây — sai UX. Peel-one-level đúng semantic hơn | ✅ DONE T7 |
| D4-9 | Spawn trong edit mode → GroupID="" (đồ rời) | **D4-9 là plan gốc** — đã OVERRIDE bởi D4BF-1 (F4) | Xem Sprint 4 Bug Fix bên dưới | → |
| D4-10 | WBP_MeshControls T5: BTN_ExitOneLevel trong HB_EditModeBar | **Patch v1.5 không include BTN_ExitOneLevel** — thêm sau khi user phát hiện thiếu | Sót trong hướng dẫn bước 5.1 | ✅ Đã thêm |

**Bug fix trong Sprint 4:**
- Bug 2: GroupID lost sau Replace Mesh → **FIXED** (12/06): SET NewActor.GroupID = OldActor.GroupID trong BTN_ChangeMesh ForEach loop (WBP_DragOverlay_FurnitureCard)
- Bug: Branch condition nhầm ancestor === "" thành ancestor !== "" trong ResolveSelectionUnit → **FIXED**

---

## SPRINT 4 BUG FIX SESSION (15/06/2026)

| # | Plan gốc nói | Thực tế | Lý do | Kết quả |
|---|---|---|---|---|
| D4BF-1 | D4-9: Spawn trong edit → GroupID="" (đồ rời) | **F4: Spawn tự động nhận GroupID = GetCurrentEditScope()** khi đang trong edit | Q13 approved: UX consistency — đồ spawn trong edit phải thuộc scope đang chỉnh | ✅ Approved |
| D4BF-2 | D4-6: S_SceneSnapshot không thêm field EditModeStack | **A12: Thêm EditModeStackSnapshot (Version=4)** vào S_SceneSnapshot, capture/restore | Bug A12 root cause: undo không khôi phục edit state. Architectural decision: EditModeStack phải vào snapshot | ✅ Architectural improvement |
| D4BF-3 | CreateGroup: guard `SelectedActors.Length < 2` đặt đầu hàm | **F3: ComputeSelectionUnits chạy TRƯỚC guard**; guard kiểm tra `GroupUnits.Length + LooseActors.Length < 2` | Guard cũ không phân biệt "2 actors" vs "2 group units" | ✅ Fix đúng (Luật 6B) |
| D4BF-4 | GroupNameCounter trong BP_FurnitureInputManager | **F2: Chuyển sang BP_GroupsContainer** (SaveGame=True) | BP_FurnitureInputManager không implement EMS → counter reset về 1 sau Save/Load | ✅ Fix đúng |

**F4 SPAWN PATHS — Tổng kết (xác nhận 15/06):**
| Con đường spawn | Xử lý F4 |
|---|---|
| Drag-drop card | WBP_DragOverlay On Drop — chèn GET Scope → Branch → SET GroupID (v1.5) |
| Paste / Cut-Paste / Duplicate | SpawnFurnitureCopy Sequence.Then 0 — chèn GET Scope → Branch → SET GroupID (v1.9) |

---

## GATE 1 (16/06/2026)

| Ngày | Task | Plan nói | Thực tế làm | Lý do |
|------|------|----------|-------------|-------|
| 16/06 | G1.T2 Hợp nhất spawn | bAutoSelect=False khi gọi SpawnFurnitureCopy trong RestoreSnapshot | Wire ban đầu bị để True (không tick) → tất cả item bị select sau mọi lần restore | Lỗi wire khi implement, phát hiện qua test case 1/2/5 — đã fix lại False, lưu ý cho lần sau gọi SpawnFurnitureCopy trong loop luôn kiểm tra lại pin này |

---

## SPRINT D — D.T6 (17/06/2026) — Bỏ FurnitureDA

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| 17/06 | D.T6 | Bỏ FurnitureDA khỏi WBP_FurnitureCard + WBP_DragOverlay | DAPath giữ nguyên trên BP_FurnitureActor làm fallback cho save cũ | Backward compat: actor save cũ chưa có RowName → Branch RowName == "" → fallback DAPath | [SCOPE] |
| 17/06 | D.T6 | WBP_MaterialCard không cần tạo file mới | Skip (file không tồn tại trước D.T6, dead code xóa không cần doc) | FurnitureDA trên MaterialCard = dead code, đã xóa trong Blueprint, không có file tài liệu cần update | [SCOPE] |
| 17/06 | D.T6 | UpdateDetailPopup gọi từ BTN_Info | UpdateDetailPopup nay là Event bound to OnSelectionChanged; BTN_Info tạo popup mới, không update | Tách rõ: BTN_Info = MỞ popup mới; UpdateDetailPopup = CẬP NHẬT popup đang mở theo selection | [PLAN-SAI] |
| 17/06 | D.T6 | BTN_Info RowName == "" → không mở popup | Không fallback DAPath cho BTN_Info (cuhoang xác nhận) | Save cũ yêu cầu re-import → không đáng fallback thêm code path | [SCOPE] |
| 17/06 | D.T6 | On Drag Detected: Set Operation.FurnitureDA | Set Operation.RowName = CardRowName | DA đã xóa; DragDropOperation_FurnitureCard giờ chứa RowName | [NODE] |
| 17/06 | D.T6 | F_ExecuteReplace: Load mesh từ FurnitureDA.Mesh | Load từ RowData.Mesh (SoftObjectRef trong S_FurnitureData) + SET NewActor.RowName | DA không còn tồn tại; DT row có field Mesh (SoftObjectPath) | [NODE] |
| 17/06 | D.T6 | FilterByCategory Recent/Favorite dùng inner loop AllFurnitureItems | DT lookup trực tiếp per RowName → Create BP_FurnitureItemView | AllFurnitureItems bị xóa trong Sprint D.T7; DT lookup O(1) thay O(n×m) | [PERF] |
| 17/06 | D.T6 | FilterBySearch dùng FilterFurnitureItems(AllFurnitureItems) | FilterFurnitureRows(DT_FurnitureCatalog) → AllFilteredFurnitureRows → DisplayPage | AllFurnitureItems xóa; C++ function mới nhận DT làm input | [NODE] |
| 17/06 | D.T6 | StartReplaceMode: navigate folder dùng DAPath | Branch RowName != "" → DT lookup; False → fallback DAPath (save cũ) | Thống nhất với kiến trúc D: ưu tiên RowName, fallback DAPath | [PLAN-SAI] |
| 17/06 | D.T6 | WBP_FurnitureCard document trong WBP_DragOverlay_FurnitureCard.md | Tạo file riêng WBP_FurnitureCard.md | Widget có đủ logic riêng để xứng đáng có file riêng | [SCOPE] |
| 17/06 | D.T6 | Stale popup: UpdateDetailPopup ở Mouse Left Pressed | Step 11 xóa; UpdateDetailPopup bind OnSelectionChanged WBP_MeshControls | Bug phát hiện trong D.T6 — selection không resolve ở Mouse Pressed | [BUG] |

---

## BUGS DEFERRED (ghi nhận, xử lý sprint sau)

| Bug | Mô tả | Deferred đến |
|---|---|---|
| B1 | Undo lần 2 không restore group state (Groups.Length=0) | ✅ FIXED Gate 1 (16/06) |
| Replace folder sai | ✅ FIXED Sprint D.T6 (17/06) — RowName→DT thay DAPath. Xem WBP_FurnitureInventory v2.5 | — |
| B3-gizmo | Gizmo ẩn sau undo trong edit mode (mode vẫn là Move) | **Pre-existing** — xác nhận 15/06, không phải regression Sprint 4. Known issue, chưa có timeline fix. |

---

## QUYẾT ĐỊNH HOÃN (Decide-When-Reached)

| Mục | Lý do hoãn | Sprint/task dự kiến |
|---|---|---|
| Phím tắt Enter để vào Edit Mode | Chưa verify conflict với search box / snap inputs | Sau test UI nút stable |
| Click ngoài scope = no-op (giữ selection) | Phải đụng caller defer mong manh | Sau Slice 1 test nếu CLEAR khó chịu |
| T9 dimming (ApplyEditModeVisual body + M_SelectionOutline Stencil 200) | MVP không cần dim | Sprint 6 Polish |
| Double-click để enter edit | Cần track LastClickTime/LastClickActor | Sau phím tắt Enter stable |
| Edit Mode UX polish (breadcrumb nổi bật, dim đồ ngoài scope) | Sprint 6 Polish | S6 |

---

## TỔNG KẾT CUỐI SPRINT

### Sprint 1
- Số deviation: 10 (tính cả 2 SKIP)
- Vùng nhiều deviation: T5 (UpdateGizmo/ToggleActor — plan bỏ sót gizmo lifecycle + outline cleanup) và T11 (DuplicateMesh)
- **BÀI HỌC LỚN NHẤT:** Bug DuplicateMesh (infinite loop + spawn N×N) KHÔNG phải aliasing array — mà do spawn nối nhầm vào **Loop Body** thay vì **Completed**. → Quy tắc: code chạy 1 lần PHẢI nối Completed. Khi infinite loop, kiểm tra nesting TRƯỚC khi nghi aliasing.

### Sprint 2
- Số deviation: 10 (1 SKIP/optional, 2 đổi thứ tự/scope)
- Vùng nhiều deviation: **T2 Box Select** (5 deviation — defer click, timing, bLMBHeld, DPI fix, guard inventory)
- **BÀI HỌC LỚN NHẤT:** Bug Undo "nhảy cóc" KHÔNG phải double-capture — mà do TempSelectedIndices stale khi nhánh deselect bypass đoạn build. → Print debug đặt main line không trong loop; CLEAR class var đầu hàm.

---

## NGUYÊN TẮC GHI DEVIATION

- Ghi ngay khi lệch, không đợi cuối sprint
- Ghi cả "deviation tốt" (fix đúng) lẫn "deviation tạm" (scope cut)
- Sau mỗi sprint: đọc lại, xem plan sprint sau có cần điều chỉnh không
