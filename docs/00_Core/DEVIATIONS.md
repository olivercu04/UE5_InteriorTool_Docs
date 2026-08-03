# DEVIATIONS — Lệch khỏi plan gốc (plan_v3)
**HỢP NHẤT TỪ 3 file:** 07-06_DEVIATIONS.md (Sprint 1+2) + DEVIATIONS.md (12/06, Sprint 3+4) + Sprint4BugFix_additions.md (15/06)
**Cập nhật:** 02/08/2026

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

**Quy ước ceiling + trigger (thêm 04/07/2026 — từ ponytail-debt):**

Deviation loại shortcut CÓ CHỦ ĐÍCH ([SCOPE], giải pháp tạm, fallback, scope cut) ghi thêm 2 trường:
- **ceiling:** giới hạn của giải pháp tạm — chịu được đến đâu thì gãy.
- **trigger:** sự kiện nào xảy ra thì BẮT BUỘC quay lại nâng cấp hoặc xóa.

Thiếu trigger = rot risk: "để sau" thành vĩnh viễn. Deviation loại đổi-cách-làm
([PLAN-SAI], [NODE], [BUG→FIX]) không cần 2 trường này.
KHÔNG hồi tố entry cũ — chỉ áp cho entry mới từ 04/07/2026.

Ví dụ: fallback MeshPath cho save cũ — ceiling: chỉ cover save tạo trước RowName
migration. trigger: Gate 2 packaged build → không còn save cũ cần giữ thì xóa fallback.

---

## [22/06/2026] Sprint 5 C3 — mở rộng + thêm C11 [SCOPE]

**Lệch so với:** Combo_Execution.md v2.1 (21/06).

**Nội dung lệch:**
- **C3 tách thành C3a (data layer) + C3b (dialog UI)** — C3 cũ gánh cả hai, tách để test-and-confirm từng nửa, cô lập lỗi data vs UI.
- **Folder: dropdown (GetExistingFolders) + nút "Tạo mới"** — THAY "nhập text tự do" của plan v2.1. Lý do: chống phân mảnh folder ("LivingRoom" vs "Living Room" vs "phòng khách") với target user không rành kỹ thuật.
- **Tags: từ "chỉ decorative" → có data layer** (chuẩn hóa lowercase/dedupe + GetAllUsedTags) ở C3a. UI filter + autocomplete vẫn defer Sprint 6. Lý do: yêu cầu chuẩn bị sẵn code cho filter sau, gắn vào không phải sửa schema.
- **Thêm 2 field C++:** AuthorID + Visibility (String, default ""/"Private"). Chừa sẵn cho mô hình share lai Phase B (Private/Public/Shared). Category đã có sẵn (T1) — **bỏ ô Category khỏi dialog save v1**, nhập ở flow Publish Phase B (save private không cần metadata discovery).
- **Thêm C11 — Export/Import combo** (chia sẻ thủ công, không cần server). Đặt TRƯỚC C10.
- **Đường nối dialog:** mở dialog từ inventory (nắm AllComboViews/vocabulary) thay vì InputManager; ĐÓNG BĂNG SelectedActors+Center vào biến tạm trước khi mở (dialog async); khóa input UI-only khi mở.

**Lý do tổng:** chuẩn bị đón mô hình lai cloud + folder dropdown + share nhóm sớm — đúng tinh thần "chuẩn bị 1 lần thay vì 2" (như quyết định Sprint D trước Sprint 5).

**Ảnh hưởng:** task set thành C0–C11 (thêm C11 + tách C3→C3a/C3b). Deadline 25/06 trượt thêm — cần re-plan mốc thực tế.

**KHÔNG đổi:** logic C0 (LCA) chỉ nới Make node thêm pin; C2 (SpawnComboByID) không đụng — thêm field FComboData không phá parse/spawn (backward-compat 1 chiều đã verify).

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
| 17/06 | D.T9 | Regression trong plan gốc (9/9 PASS) | Phát hiện thêm 2 bug ngoài checklist: Bug-Pagination + Bug-Maximize — fix ngay cùng phiên | Bug phụ ngoài checklist gốc, fix ngay, không defer | [BUG] |
| 18/06 | PROGRESS.md | Checklist D.T1-D.T9 đúng label | Bị lệch nhãn giữa các task — phát hiện và sửa lại khi làm doc update 18/06 (xem PROGRESS.md mục Sprint D) | Lỗi ghép doc, không phải lỗi code | [PLAN-SAI] |
| 17-18/06 | TreeNode highlight | Phase 1: wire `==` trực tiếp cho cấp 1 | Kiến trúc tập trung `IsPathActive`/`UpdateFolderHighlights` — hỗ trợ cả chip cấp 2/3; dừng sửa từng phần | Bug học được: biến class trong loop gây tô sai tất cả → đổi sang đọc FolderPath của TỪNG widget | [BUG] |

---

## SPRINT D — 19/06/2026 — VRAM Fixes + Async Load

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| 19/06 | Fix 5.2 | Plan: async load trong Custom Event ở InputManager | Thực tế: chuyển sang Custom Event trong BP_FurnitureActor | Bug aliasing — nhiều actor share cùng latent context + class var → mesh set sai actor. Fix: actor tự load (mỗi instance có graph riêng) | [BUG→FIX] |
| 19/06 | Fix 5.2 | Plan: NewActorCopy là class var | Thực tế: đổi sang local var trong SpawnFurnitureCopy | Hệ quả của aliasing fix — local var mỗi lần gọi là bản riêng | [BUG→FIX] |
| 19/06 | VRAM | Ghi nhầm card là RTX 3060 12GB | Thực tế: RTX 3060 8GB | Budget UE = 7.26GB = 8GB - reserve, khớp crash log | [CORRECTION] |
| 19/06 | Fix 5.3 | ApplyMaterial: Add Recent Mesh parse từ DAPath | Thực tế: đổi sang MeshPath | DAPath rỗng với đồ Sprint D (không dùng DA_FurnitureItem nữa) | [BUG→FIX] |
| 19/06 | S5.T2 | Combo_Execution v1.1 đặt toàn bộ combo event trong BP_FurnitureInputManager, đọc trực tiếp class var (SelectedActors, Center) | Tách ra BP_ComboManager (Actor) riêng — combo event sống ở đây | Đồng nhất pattern "mỗi Actor một nhiệm vụ"; cô lập vùng combo sẽ sửa nhiều (thumbnail, B3 payment, share). ComboManager = dịch vụ thuần, nhận data qua param, KHÔNG hard ref InputManager (R2) | [SCOPE] |

---

## SPRINT 5 — 21/06/2026 — Kiến trúc Combo v2.0

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| 21/06 | S5.T2 | Combo lưu selection-only: ForEach SelectedActors → GET GroupID | Sửa C0: GetGroupRoot + GetGroupsInHierarchy gom cả cây (cha+con+cháu) | Selection-only mất group cha trung gian — nested combo bị làm phẳng thành group lá | [BUG] |
| 21/06 | S5 | D4: bấm nút spawn combo tại điểm giữa màn hình | Drag-drop tái dùng khung furniture (DragOperation/DragOverlay/On Drop); ghost = 1 mesh đại diện Items[0]; On Drop → SpawnComboByID(DropLocation) | UX nhất quán với drag furniture; bấm nút giữa màn hình = không tự nhiên | [SCOPE] |
| 21/06 | S5 | materialOverrides trong combo JSON lưu full path /Game/… | Đổi sang RowName (vd "MI_Blue_01") + C++ reverse helper FindMaterialRowNameByPath | Portable cloud (B3): path thay đổi giữa users, RowName = hợp đồng bền vững. Snapshot/EMS actor giữ path — không regression | [SCOPE] |
| 21/06 | S5 | Đánh dấu cụm combo bằng ComboInstanceID riêng | Group cha wrapping + field SourceComboID : String trên S_GroupData (default "") | Tận dụng toàn bộ group system (move, edit, select, undo) miễn phí. Không viết mới | [SCOPE] |
| 21/06 | S5 review | Plan v2.0 thiếu: ItemView task bị mất khi xóa T3, On Drop không phân biệt payload, C2 "2 vòng" gãy nested, V5 snapshot giả định | Patch v2.1: C0→LCA, ghi nhận ItemView đã xong, DragOp_ComboCard mới, C2→3-phase, C9 capture-after+toast, persist xác nhận thừa (V5 không cần) | Review kiến trúc bắt 10 điểm; 2 điểm (PreReplace snapshot, bump V5) phân tích thừa | [PLAN] |

---

## SPRINT 5 — 23/06/2026 — Quyết định Sprint5_Plan_v1.1 (11 quyết định + 3 điều chỉnh)

| Mục | Lệch so với plan | Lý do | Loại |
|---|---|---|---|
| P1 Thumbnail | Từ icon 🧩 fallback → C++ THẬT: `SaveRenderTargetToPNG` + `LoadTexture2DFromFile` + SceneCapture2D theo góc camera hiện tại | Đầu tư "làm 1 lần dùng 3 chỗ": combo / B4 user upload / nút chụp bìa. Gộp vào C3/C4 thay vì defer | [SCOPE] |
| P2 Surface snap | Thêm surface-snap KIỂU KHỐI: snap cả combo (1 khối) xuống sàn, giữ bố cục rigid; KHÔNG snap từng món riêng lên bề mặt của nó | Snap từng món PHÁ combo ("TV tường + kệ + thảm": snap riêng → TV trôi xa kệ, vỡ bố cục) | [SCOPE] |
| P3 Xoay combo | Thêm verify xoay combo cluster bằng gizmo + tùy chọn xoay-lúc-kéo (R/scroll) | Group rotation đã có Sprint 3/4 → xoay combo cluster bằng gizmo gần như miễn phí | [SCOPE] |
| P5 Material name-based | DỜI sang Sprint 7 (mở màn ngay sau Sprint 5) | Đổi "theo index" → "theo tên slot" đụng 3 hệ thống (material, EMS, undo snapshot) — nhét giữa Sprint 5 đang xây combo = rủi ro sập cả 3. Sprint 7 có regression đầy đủ. Combo file chừa sẵn slot name để Sprint 7 không phải migrate. | [SCOPE] |
| K1 WBP_Toast | Thêm widget toast TIÊN QUYẾT trước C8; dùng FText | Mọi toast (C8 spawn fail, C9 replace fail, C11 import rác, M11 thiếu mesh) đều cần 1 widget — build trước khi dùng | [SCOPE] |
| K3 bAddToRecent | SpawnFurnitureCopy thêm param `bAddToRecent : Boolean = True`; spawn combo truyền False; RestoreSnapshot truyền False | Spawn combo nhồi 20 mesh lẻ vào Recent; mỗi Undo cũng nhồi → Recent vô nghĩa. Bug có sẵn không chỉ ở combo | [BUG] |
| K5 Export C11 | Làm CẢ 2 hướng: file-save dialog (Desktop) TRƯỚC, nếu không chạy → fallback tự động copy thư mục cố định + báo path | Cả 2 hướng graceful — user luôn lấy được file; không phải "nếu có dialog thì dùng" | [SCOPE] |
| P4 Chỗ lưu | `GetCombosDir()`: `FPaths::ProjectSavedDir()/Combos` → `FPlatformProcess::UserSettingsDir()/"InteriorFOFFTool/Combos"` (= `%LOCALAPPDATA%\InteriorFOFFTool\Combos` Windows). Tạo dir nếu chưa có. Gộp vào C3. | Combo sống qua update app (ProjectSaved xóa khi rebuild packaged) | [SCOPE] |
| Scope + timeline | Sprint 5 phình to (P1+P2+P3 mới) → chia 3 giai đoạn: G1 (~25/06, C3→C7), G2 (Toast+C8+P3+C9), G3 (C11+C10). Deadline 25/06 chỉ xong G1. | 2 ngày không nhét hết P1+P2+P3+C8+C9+C11 — ép nhanh là cách chắc nhất để hỏng combo | [SCOPE] |

**Quyết định GIỮ NGUYÊN:** B1 ownership = combo chỉ local Sprint 5 (DEFAULT, không bật chợ tới khi rõ ownership). K4 cap nesting = 3 cấp (test C10). K2 verify EMS SourceComboID = đầu C9.

---

## SPRINT 5 — 24/06/2026 — C4/C8 Merge + Kiến trúc On Drop

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| 24/06 | C8 | Task riêng Giai đoạn 2: drag-drop + surface-snap + fix Lỗ14 | **MERGED vào C4** — OnDragDetected + ghost box + On Drop implement ngay trong C4 | Drag-drop là prerequisite để test C4; surface-snap logic (ghost follows cursor) đơn giản hơn dự kiến; không cần delay sang Giai đoạn 2 | [SCOPE] |
| 24/06 | On Drop combo | Plan: combo branch dùng Line Trace (screen pos → deproject → trace → bBlockingHit → HitLocation) | **Thực tế: KHÔNG trace**. On Drag Over đã `Set Actor Location` lên ghost mỗi frame → ghost ở đúng chỗ khi On Drop fire. On Drop chỉ cần `GetActorLocation(PreviewActorRef)` → SpawnComboByID — 1 đường thẳng | Plan copy nhầm pattern "trace trong On Drop" nhưng furniture On Drop CŨNG không trace (location đã set qua Drag Over). Bắt kịp từ Opus delta session. | [PLAN-SAI] |
| 24/06 | CalculateComboAnchor | Plan: CB_SaveCombo_Handler dùng CalculateCenter → Center làm SpawnLocation anchor | Tạo hàm mới **CalculateComboAnchor** (center XY + MinZ khi sàn / MaxZ khi all-ceiling). CalculateCenter giữ nguyên cho gizmo + copy/paste | CalculateCenter cho floor items → centroid z ≈ chiều cao / 2 → combo spawn nổi giữa không khí. Anchor bottom = z ≈ 0 → spawn đúng sàn | [BUG→FIX] |
| 24/06 | Ghost offset | InitGhost: `Set Relative Location Z=50` sau `Set Actor Scale 3D` để bù đáy cube lên sàn | **BUG OPEN**: ghost preview vẫn chìm — đáy cube dưới HitLocation. Z=50 chưa đủ / thứ tự node sai | Approach B (On Drag Over: set = HitLocation + (0,0,Extent.Z)) chưa thử — investigation pending | [BUG] |

---

## SPRINT 5 — 25/06/2026 — C5 Folder Management + Kiến trúc

| Ngày | Task | Plan nói | Thực tế làm | Lý do | Loại |
|------|------|----------|-------------|-------|------|
| 25/06 | C5 scope | Plan C5 = "Browse Combo Folder Tree" (browse-only, C5 gốc Combo_Execution) | C5 mở rộng thành full folder management: browse + move combo + tạo/rename/move/xóa folder (C5.0→C5.6) | Scope phình có chủ đích — thao tác folder là atomic unit, split thành nhiều sprint gây doc/code lộn xộn | [SCOPE] |
| 25/06 | D1 — AddFolderPathToTree dedup | `String Contains` để dedup tên con trong CSV | **Parse Into Array(",") + Array Contains** (exact match) | String Contains = substring → "Phòng" match "Phòng khách" = false positive dedup sai | [PLAN-SAI] |
| 25/06 | D2 — RefreshDisplay signature | `RefreshDisplay(FolderName, IndentLevel, bIsActive)` — 3 param | **RefreshDisplay chỉ nhận 1 param `bIsActive`**. FolderName + IndentLevel SET trực tiếp lên widget var TRƯỚC khi gọi RefreshDisplay | WBP_TreeNode.RefreshDisplay thực tế chỉ có 1 param (Sprint D). Plan ghi sai signature | [PLAN-SAI] |
| 25/06 | D3 — FilterComboByFolder render | Loop Add Item trực tiếp vào CTV_ComboCard | **Collect → local FilteredItems → Set List Items 1 lần** ở Completed | TileView render ổn định hơn với Set List Items (1 phát) so với N lần Add Item. Đang test fix B-C5-card | [BUG→FIX] |
| 25/06 | D4 — Tree layout | Hỏi C-1 về cột riêng/chung | **Dùng CHUNG VerticalBox_44** với furniture/material | C-1 xác nhận: combo dùng chung cột tree, switch tab clear + populate lại | [CONFIRM] |
| 25/06 | D5 — bHasUncategorized | Local var trong BuildComboFolderTree | **Class var** (sống xuyên 2 hàm BuildComboFolderTree → PopulateComboTreeColumn) | PopulateComboTreeColumn đọc nó SAU Build — local var chết ngay sau ForEach Completed | [SCOPE] |
| 25/06 | D6 — C5.0 tree depth | Plan: "cấp 1 phẳng, nested polish C5 sau" | **Render full 2 cấp ngay** (cấp 1 IndentLevel=0 + cấp 2 IndentLevel=1 lồng trong tree) + chip cấp 3+ qua OnComboChipTagClicked | UX nhất quán: 3-cấp folder cần browse ngay; defer nested = không bao giờ làm | [PLAN-SAI] |
| 25/06 | D7 — OnComboTreeNodeClicked | Plan: chỉ FilterComboByFolder + PopulateComboTreeColumn (đơn giản) | **REWRITE branch IndentLevel**: 0 → clear chip + filter + repopulate tree; 1 → filter + gen WBP_ChipRow cho cấp 3 con của SelectedPath | Cấp 2 click PHẢI sinh chip — không thể chỉ repopulate tree vì tree chỉ hiện 2 cấp | [SCOPE] |
| 25/06 | D8 — OnComboChipTagClicked | Không có trong plan | **NEW custom event, clone OnChipTagClicked furniture**: TRIM chip row sâu hơn IndentLevel click + filter + sinh chip cấp kế tiếp | Pattern chip navigation giống hệt furniture — clone + đổi data source ComboFolderTree | [SCOPE] |

## SPRINT 5 — 26/06/2026 — C5.0 Tree Nested + WBP_LibraryContextMenu

| Ngày | ID | Mô tả | Plan nói | Thực tế | Lý do | Loại |
|---|---|---|---|---|---|---|
| 26/06 | D9 | PopulateComboTreeColumn cấp 2 visibility | Render cấp 2 luôn trong ForEach | **Branch guard** `(CurrentPath==lvl1 OR StartsWith(lvl1+"/"))` trước Map Find; trong **Loop Body** (KHÔNG Completed) | UX: cấp 2 không nên hiện sẵn khi mở tab Combo. Bug Completed: lvl1=phần tử cuối, check sai cả tree | [PLAN-SAI] |
| 26/06 | D10 | Branch guard vị trí | Nối sau ForEach Lvl1Names (Completed pin) | Nối trong **Loop Body** của ForEach Lvl1Names | Completed → thoát loop → lvl1 stale = phần tử cuối → Branch check sai 1 lần duy nhất | [BUG→FIX] |
| 26/06 | D11 | WBP_LibraryContextMenu close mechanism | Plan: dùng Menu Anchor built-in (C5.2+) | Dùng **Btn_Background** (full screen, Z thấp, alpha=0) — clone từ WBP_ContextMenu | Đơn giản hơn, pattern đã tested, không cần Menu Anchor positioning logic | [PLAN-SAI] |
| 26/06 | D12 | Canvas Panel Z-order | Không đề cập | **Btn_Background index 0, Border_Menu index 1** (phải đúng thứ tự) | UMG render từ index 0 lên — index cao hơn nhận hit trước. Sai order → Btn_Background che Border_Menu → click nút menu không được | [NODE] |

## SPRINT 5 — 27/06/2026 — C5.2 Inline Rename Folder

| Ngày | ID | Mô tả | Plan nói | Thực tế | Lý do | Loại |
|---|---|---|---|---|---|---|
| 27/06 | D13 | C5.2 approach | WBP_RenameFolderDialog (dialog popup) | **WBP_EditableLabel** component inline: Overlay Label+EditBox+Border_Error | UX nhất quán Content Browser; tái dùng cho WBP_ChipTag C5.4+ | [SCOPE] |
| 27/06 | D14 | Validate timing | Validate sau Enter | ValidateName live trong OnTextChanged → Border_Error (feedback tức thì) | User thấy lỗi trước khi Enter, không bị reject sau | [SCOPE] |
| 27/06 | D15 | Click ngoài | Không rõ trong plan | `OnUserMovedFocus` = **revert** (không commit) | An toàn: không rename ngẫu nhiên khi focus out; Enter = confirm | [SCOPE] |
| 27/06 | D16 | Folder ops Undo | Không rõ | **KHÔNG CaptureSnapshot** cho rename/move/delete folder | Folder ops = metadata thư viện, không phải scene action (UX8). Confirm dialog C5.6 thay thế Undo | [SCOPE] |

---

## SPRINT 5 — 30/06/2026 — C5.4 Move Folder

### D-C5.4-1 — Array_Append nối ngược TargetArray/SourceArray (CollectFolderTargets)
**Phát hiện:** 30/06/2026, lúc test list move folder trả về thiếu entries con cháu (chỉ 1 entry/cấp).
**Nguyên nhân:** node Array_Append cuối Loop Body đệ quy bị nối: TargetArray=ChildEntries (sai), SourceArray=LocalResult (sai) — ngược hoàn toàn so với ý đồ (TargetArray=LocalResult, SourceArray=ChildEntries). Hệ quả: kết quả đệ quy bị append vào biến sẽ bị vứt, LocalResult thật không bao giờ nhận gì từ con.
**Bài học:** Array_Append(Target, Source) — luôn double-check chiều TargetArray là biến SỐNG SÓT sau hàm (LocalResult ở đây), không phải biến tạm.

### D-C5.4-2 — Dead-end thiếu merge ở 2 nhánh True (HandleMoveFolderConfirmed)
**Phát hiện:** 30/06/2026, lúc soát lại node flow qua text export.
**Nguyên nhân:** 2 Branch cập nhật CurrentComboFolderPath (match đúng path / StartsWith path con) có nhánh True dead-end (không nối tiếp sang RenameFolderPrefix) — chỉ nhánh False (qua reroute) mới tới được. Bug CHỈ lộ khi đang XEM ĐÚNG folder bị move lúc confirm — dễ lọt qua test nếu không cố tình test đúng kịch bản đó.
**Bài học:** mọi nhánh "cập nhật biến rồi tiếp tục logic chính" PHẢI merge về đúng 1 điểm tiếp theo — kể cả nhánh True, không chỉ nhánh False (luật cũ chỉ nhấn mạnh False, lần này lỗi nằm ở True).

### Learning_System — Quy trình dạy học bị bỏ qua (Sprint 5 deadline-rush)
| 30/06 | Learning_System | Quy tắc dạy học (file Rules/Learning_System.md) bị bỏ hoàn toàn trong giai đoạn deadline-rush Sprint 5 (21/06→30/06) — Claude tự đọc export/log, tự kết luận, tự sửa mà không giải thích/kiểm tra hiểu. Học viên tự nhận ra (cảm thấy "quá phụ thuộc"), yêu cầu khôi phục. Khắc phục: 3 điều chỉnh quy trình ghi trong Learning_System.md v1.2 + bảng "Nợ kiểm tra hiểu" liệt kê minh bạch phần đã bỏ qua, không tick khống. |

---

## SPRINT 5 — 01/07/2026 — C5.5 Move Combo (Bug fixes phát sinh)

### D-C5.5-1 — ParseIntoArray delimiter mismatch (PopulateComboTreeColumn) [BUG FIX 4.1]
**Phát hiện:** 01/07/2026, lúc test Move Combo thấy tree render sai sau refresh.
**Nguyên nhân:** `AddFolderPathToTree` viết CSV với `","` (không cách — `Append(OldCSV, ",", child)`), nhưng `ParseIntoArray` trong `PopulateComboTreeColumn` đọc lại với `", "` (có cách sau phẩy). Hệ quả: `"Phòng khách,Phòng ngủ"` được parse thành 1 phần tử `"Phòng khách,Phòng ngủ"` thay vì 2 phần tử riêng — nhiều tên con bị gộp thành 1 node.
**Fix:** Đổi delimiter trong `ParseIntoArray(Lvl1CSV, ",")` và `ParseIntoArray(Lvl2CSV, ",")` về `","` (không cách) — khớp 100% với delimiter viết.
**Bài học:** Delimiter phải khớp tuyệt đối giữa bên viết (AddFolderPathToTree) và bên đọc (PopulateComboTreeColumn). Kiểm tra bằng Print String giá trị CSV thô để confirm delimiter thực tế.

### D-C5.5-2 — Map_Contains sai với leaf folder (RefreshComboFolderUI) [BUG FIX 4.2]
**Phát hiện:** 01/07/2026, Move Combo xong nhưng refresh không hiện đúng folder.
**Nguyên nhân:** `ComboFolderTree` là `Map<ParentPath, ChildCSV>` — key là path CHA, không phải path lá. Folder lá (không có con trong tree) → `Map_Contains(path_lá)` trả False → fallback về `"__ALL__"` sai. VD: folder "Phòng khách/Sofa" (lá) không là key → Map_Contains = False → hiển thị tất cả thay vì filter đúng.
**Fix:** Bỏ nhánh `Map_Contains`, luôn gọi `FilterComboByFolder(CurrentComboFolderPath)` cho path thật (không phải sentinel). `FilterComboByFolder` tự lọc đúng bất kể path có là key hay không.
**Bài học:** Kiến trúc ComboFolderTree = key là cha. Mọi logic check "folder có tồn tại?" không nên dùng `Map_Contains` — dùng `FilterComboByFolder` và xem kết quả.

### D-C5.5-3 — Thiếu UpdateComboFolderHighlights sau RefreshComboFolderUI (RefreshComboFolderUI) [BUG FIX 4.3]
**Phát hiện:** 01/07/2026, sau Move Combo tree/chip không sáng đúng folder.
**Nguyên nhân:** `RefreshComboFolderUI` gọi `FilterComboByFolder` rồi kết thúc — không gọi `UpdateComboFolderHighlights()`. Sau refresh, tree re-render nhưng `RefreshDisplay` được gọi với param cũ từ `PopulateComboTreeColumn` (trước khi `CurrentComboFolderPath` có thể đã đổi bởi Move Combo).
**Fix:** Sau merge 3 nhánh (`__ALL__` / `""` / path thật), thêm `UpdateComboFolderHighlights()`.
**Bài học:** Mỗi lần `CurrentComboFolderPath` thay đổi hoặc tree re-render → phải gọi `UpdateComboFolderHighlights` để sync màu highlight. Không để highlight update phụ thuộc vào `PopulateComboTreeColumn` vì hàm đó chạy TRƯỚC khi path mới được set.

---

**Quyết định kiến trúc C5 (không bàn lại):**
- **Copy folder GÁC backlog** — phải nhân bản ComboID mới + copy PNG, lệch hẳn pattern chỉ-viết-text. Hiếm dùng.
- **Folder ops KHÔNG vào Undo (Alt+Z)** — metadata thư viện, không phải scene action. Confirm dialog (C5.6) thay thế Undo.
- **1 combo = 1 FolderPath** (không thuộc nhiều folder). Tags = multi-label nếu cần.
- **Context menu = Menu Anchor built-in** (C5.2+) — đóng tự động khi click ngoài, né mép màn hình.

---

## SPRINT 5 — 04/07/2026 — NF (New Folder, context-menu part)

### D-NF-1 — NF chuyển từ DIALOG sang INLINE RENAME (bỏ WBP_NewFolderDialog)
Plan v2 gốc (NF.G2–G5) thiết kế tạo folder qua popup dialog WBP_NewFolderDialog
(nhập tên trước rồi tạo). Thực thi ĐỔI HẲN sang UX kiểu Windows Explorer:
tạo folder rỗng NGAY với tên mặc định "New Folder" (GetUniqueNewFolderName tự
thêm hậu tố (2),(3)... nếu trùng), rồi tự vào rename mode tại chỗ bằng cách
gọi lại OnRequestRenameFolder có sẵn (tái dùng WBP_EditableLabel của C5.2).
**Lý do:** UX quen thuộc hơn, tái dùng 100% cơ chế inline rename đã build, KHÔNG
cần dựng widget dialog mới + validate riêng. **Hệ quả:** WBP_NewFolderDialog.md
KHÔNG tạo (hủy khỏi doc-update list của plan v2); các gate NF.G2–G5 gốc
(dialog wiring) không còn áp dụng. `[SCOPE]`

### D-NF-2 — Right-click "Tạo folder mới" = tạo CÙNG CẤP node bị click (không phải CON)
Thảo luận ban đầu (Entry Point 3) định là "tạo folder CON của node right-click".
Chốt lại (G3' #1): tạo CÙNG CẤP (sibling) kiểu Windows — ParentPath = ParentOf(node
bị right-click). **Lý do kỹ thuật:** node cùng cấp với node đang thấy LUÔN render trên
tree → OnRequestRenameFolder luôn tìm thấy node để vào rename mode. Tạo con của node
có thể rơi vào cấp chưa render (tree 2 cấp) → rename mode thất bại. Nút "+" (part còn
nợ) thì ngược lại: tạo TRONG folder đang xem (GetNewFolderParent), chấp nhận edge
cấp sâu bỏ qua auto-rename (sửa khi C5.7 xong). `[SCOPE]`

### D-NF-3 — Không cần dispatcher OnRequestNewFolder trên WBP_LibraryContextMenu
Ban đầu định thêm Event Dispatcher OnRequestNewFolder vào class WBP_LibraryContextMenu
(giống 4 dispatcher cũ). Bỏ: CB_CreateNewFolder gọi THẲNG Custom Event OnRequestNewFolder
nằm trong chính WBP_FurnitureInventory (đúng pattern CB_MoveFolderClick → OnRequestMoveFolder),
không qua Broadcast/dispatcher của context menu. WBP_LibraryContextMenu KHÔNG đổi (vẫn 3 var
+ 4 dispatcher cũ), chỉ thêm 1 menu item "Create New Folder" qua AddMenuItem() động. `[SCOPE]`

**Ghi chú:** NF.G0 (C++) + NF.G1 (Blueprint BuildComboFolderTree đổi nguồn sang GetAllFolderPaths)
đã DONE trước session này (không phải deviation — đúng plan). Chi tiết implementation: xem
`WBP_FurnitureInventory.md` v3.6 + `Combo_C5_FolderManagement_Plan.md`.

---

## SPRINT 5 — 06/07/2026 — NF.G3 + C5.6 + C5.7a

### D-C5.6-1 — HandleDeleteFolderConfirmed đổi hành vi navigate sau xóa folder
Spec gốc (test case 5, `Combo_C5_FolderManagement_Plan.md`) quy định "nhảy về `__ALL__`".
Đổi thành "nhảy về folder CHA trực tiếp" (`ParentOf`, có sẵn từ C5.2) — nếu cha là gốc mới
về `__ALL__`. Lý do: UX mượt hơn khi xóa folder lồng sâu, giữ ngữ cảnh thay vì bật về Tất
cả. cuhoang duyệt. `[SCOPE]`

### Bug fix RefreshComboFolderUI — 2/3 nhánh dead-end trước RefreshChipBreadcrumb
2/3 nhánh filter (`__ALL__`, `""`) dead-end sau `UpdateComboFolderHighlights`, không nối
tới `RefreshChipBreadcrumb` (hàm mới) → chip area không tự dọn khi navigate về
`__ALL__`/`""`. Phát hiện qua export K2Node, đã nối cả 3 nhánh. `[BUG]`

### Bug fix RefreshChipBreadcrumb — Delimiter gõ nhầm
`Parse Into Array` dùng Delimiter `"/ "` (có khoảng trắng) thay vì `"/"` → Segments không
tách được, chip area trống sau move/xóa folder con trong path ≥2 cấp. Đã sửa Delimiter.
Kèm sửa phụ: BooleanAND→BooleanOR ở guard đầu hàm (logic sai nhưng vô hại runtime, sửa
cho đúng ý định). `[BUG]`

**Ghi chú:** NF.G3 (nút "+") không phải deviation — đúng plan, tái dùng `GetNewFolderParent`/
`OnRequestNewFolder` có sẵn, không hàm mới. Bug fix "SelectedPath nhầm biến" (class var
trùng tên param trong `OnComboTreeNodeClicked`) ghi ở `WBP_FurnitureInventory.md` §OnComboTreeNodeClicked,
không lặp lại ở đây (không phải deviation kiến trúc, là lỗi wire cụ thể).

---

## SPRINT 5 — 08/07/2026 — C5.8 Task Card #1 (Data Layer)

### [RENAME] S_FolderTargetEntry → S_FolderTreeNode
Struct đổi tên (field `IndentLevel` → `Depth`) + thêm 4 field mới (`HasChildren`, `ChildCount`,
`ContinuesAncestors`, `bIsLast`) phục vụ guide line của `WBP_FolderTreePicker` (C5.8, chưa build —
xem `C5.8_FolderTreePicker_Unify_Plan.md`). 2 chỗ dùng struct này (`WBP_FurnitureInventory`,
`WBP_MoveToFolderDialog.PopulateRows`) — Blueprint tự propagate tên mới qua rename, không cần sửa
tay widget. `[SCOPE]` — đúng kế hoạch Task Card #1, không phải phát sinh ngoài ý muốn.

### [ARCH] Tên wrapper đổi khác plan gốc: BuildFolderTree → BuildComboFolderTreeNodes
Plan gốc (§3.3/§11) đặt tên wrapper build-cây là `BuildFolderTree`. Lúc thực thi phát hiện tên
này đã trùng với 1 hàm cũ phía Material/Furniture catalog (khác combo) → đổi thành
`BuildComboFolderTreeNodes(ExcludePath)` để tránh đụng độ tên. Recursive core giữ đúng tên plan
(`BuildFolderTreeRecursive`) + thêm 1 hàm phụ `GetFilteredChildren` (Pure, tách bước filter ra
khỏi recursive function — không có trong plan gốc nhưng cùng tinh thần, không đổi hành vi).
`[SCOPE]` — phát hiện lúc code, không phải lỗi kế hoạch.

---

## SPRINT 5 — 11/07/2026 — C5.8 Task Card #2 Part B lần 1 (as-built)

### [ARCH] ExpandedFolders: Array<String> thay Set<String>
Lý do: tránh node Set chưa xác nhận, project chưa dùng Set trong Blueprint. Ceiling: vài chục folder; trigger: scale nghìn folder → đổi Set.

### [SWAP] ETB_Search → SB_SearchFolder (Search Bar)
Lý do: tiền lệ Material search trong `WBP_FurnitureInventory` (có `OnSearchTextChanged` + pin Text), tránh bug CommonSearchBox cũ. Ceiling/trigger: n/a.

### [DOC-FIX] 2b Part A as-built dùng Custom Event trung gian HandleArrowClicked/HandleNameClicked
Ghi chú "nối THẲNG vào Call dispatcher (không Custom Event trung gian)" trong `C5.8_TaskCard2_PartB_2c_10jul2026.md` mục TIẾN ĐỘ là SAI so với code thật — đã sửa dòng đó trong task card (xem changelog file đó).

### [LESSON] SetFolders giữ thân cũ 2a khi build Part B
Sonnet quên nhắc sửa `SetFolders` theo bước 4e task card khi build Part B → breakpoint không fire (bug phát hiện + fix bởi cuhoang). Quy tắc mới đề xuất: sửa function CÓ SẴN phải diff thân cũ trước, không chỉ thêm mới (candidate vào AI_Implementation_Rules).

---

## SPRINT 5 — 11/07/2026 (tiếp) — C5.8 Task Card #2 Part B, Giai đoạn 1 (bug #2 fix)

### [BUG-FIX] WBP_FolderPickerRow.SetNode thiếu SET RowNode = Node
Root cause của cả bug #2 (Path rỗng khi broadcast) LẪN triệu chứng arrow không ăn click. 1 fix duy nhất giải quyết cả 2 nhánh nghi vấn (1-H1 + góc của 1-H2) từng liệt kê riêng trong FixPlan. Không có ceiling — fix triệt để.

### [BUG-FIX] BTN_Arrow không đồng bộ Visibility với TXT_Arrow trong SetNode
`BTN_Arrow` (nút bọc) không đồng bộ Visibility với `TXT_Arrow` (text bên trong) — leaf node vẫn hiện khung nút xám + vẫn hit-test được dù không có con. Fix: thêm `SetVisibility(BTN_Arrow,...)` clone theo `TXT_Arrow` ở cả 2 nhánh Branch. Ceiling: đủ tốt hiện tại; trigger: nếu sau này tách UI nút/text phức tạp hơn (icon riêng) thì rà lại toàn bộ cặp Visibility này.

### [DOC-FIX] C5.8_TaskCard2_FixPlan_11jul2026.md v1.1 đính chính SAI về Custom Event trung gian
Phần "ĐÍNH CHÍNH AS-BUILT" của FixPlan v1.1 khẳng định SAI rằng có Custom Event trung gian `HandleArrowClicked`/`HandleNameClicked`. Export K2Node thật (11/07, cuhoang gửi) xác nhận: `On Clicked(BTN_Arrow/BTN_Name)` nối THẲNG vào `Call On Row Expand Clicked`/`Call On Row Selected`, không qua lớp nào. Bản doc gốc `C5.8_TaskCard2_PartB_2c_10jul2026.md` ("nối thẳng") mới là ĐÚNG — FixPlan v1.1 đã "đính chính" nhầm theo hướng ngược lại. Không cần fix code — chỉ cần sửa doc. `WBP_FolderPickerRow.md` v1.1 đã cập nhật đúng.

---

## SPRINT 5 — 12/07/2026 — C5.8 Task Card #2 Giai đoạn 2+3

### [BUG] PathMatchesQuery dùng nhầm node.Path (full path) thay vì node.DisplayLabel
Test mục 6 (search "sofa") ban đầu FAIL: hiện luôn cả con của node "Sofa" (`Đồng Gia`, `New Folder`) vì `Contains` substring match trên toàn bộ path (`"Livingroom/Sofa/Đồng Gia"` chứa chữ trùng). Sửa: đổi input `Path` của `PathMatchesQuery` — ở CẢ 2 chỗ gọi (`BuildSearchOverride` và `RefreshVisibleRows`) — từ `Break Struct → Path` sang `Break Struct → DisplayLabel`. `Array_Contains` (exact match, cho `SearchExpandOverride`/`ExpandedFolders`) vẫn giữ nguyên dùng `Path` đầy đủ.

### [ARCH] CurrentSearchFolder: đổi từ Local Variable → Class Variable
Nguồn đọc text ban đầu sai: `RefreshVisibleRows` tự query `SB_SearchFolder → Get Initial Text` — trả rỗng luôn (property này không phản ánh text người dùng đang gõ). Sửa đúng: `OnSearchTextChanged` là nơi duy nhất có giá trị text chính xác (qua pin `Text` của delegate) → SET vào class var `CurrentSearchFolder` ngay đầu event; mọi nơi khác đọc lại từ class var thay vì tự query widget lần 2.

### [BUG] Arrow-click trong lúc search không lộ folder con
Test bổ sung: search "sofa" → click arrow của node "Sofa" (đang match) → không có gì xảy ra, con không hiện. Nguyên nhân kép: `bShow` nhánh search ban đầu chỉ xét match/`SearchExpandOverride` (search-driven), không biết đến `ExpandedFolders` do người dùng tự click mở thêm trong lúc đang search; `SetExpanded` nhánh search ban đầu hardcode `True` — không phản ánh trạng thái thật. Sửa: thêm Function mới `GetParentPath(Path) → String` (Pure); thêm điều kiện `OR Array_Contains(ExpandedFolders, GetParentPath(node.Path))` vào `bShow`; `SetExpanded` đổi từ hardcode `True` sang `Array_Contains(ExpandedFolders, node.Path)` — giống hệt công thức nhánh False, không hardcode nữa.

### [ARCH] GetParentPath — Function mới, không có trong plan gốc
Cần thiết để hỗ trợ "tổ tiên qua expand thủ công trong lúc search" — plan gốc §4d chỉ tính expand search-driven (qua `SearchExpandOverride`), chưa tính trường hợp người dùng tự mở thêm trong khi đang search. Không đổi kiến trúc tổng thể, chỉ bổ sung 1 pure function nhỏ trên `WBP_FolderTreePicker`.

### [SCOPE] Select (Giai đoạn 3, mục 10) không cần sửa gì
`HandleRowSelected` build từ Part A đã đúng hành vi ngay từ đầu — chỉ verify test, không phát sinh bug/deviation.

### [SCOPE] Bỏ Print debug gate bằng bDebugMode (Giai đoạn 4, 12/07 tiếp)
FixPlan mục 1 định thêm biến `bDebugMode` + wire Branch gate cho từng Print debug. Thực tế: bỏ hẳn, dùng breakpoint/watch pin (công cụ debug sẵn có UE5) thay thế khi cần. Lý do: thêm biến + wire Branch riêng cho từng Print là thừa so với lợi ích ở quy mô hiện tại.

---

## SPRINT 5 — 13/07/2026 — C5.8 2d (rename host) + Wire Move + Wire Save

### [BUG-FIX] OnRequestMoveFolder + CB_MoveCombo vẫn gọi BuildMoveFolderTargetList
Rename Task Card #1 (08/07) từ `BuildMoveFolderTargetList` → `BuildComboFolderTreeNodes` KHÔNG propagate hết 2 call site (claim "Blueprint tự propagate qua rename" trong `WBP_FurnitureInventory.md` v3.9 SAI). Hệ quả: `HasChildren`/`ChildCount` luôn False/0 cho MỌI node trong Move dialog (hàm cũ sinh trước khi 2 field này tồn tại trong struct) → không hiện arrow/badge dù folder có con thật. Fix: `OnRequestMoveFolder` + `CB_MoveCombo` đổi sang gọi `BuildComboFolderTreeNodes`. `BuildMoveFolderTargetList` xoá hẳn (mồ côi sau fix, không giữ [LEGACY] — bản thiếu field, giữ lại chỉ gây nhầm lẫn).

### [BUG-FIX] SetSelectedHighlight dùng nhầm biến so sánh
`RefreshVisibleRows` (`WBP_FolderTreePicker`): dòng gọi `Row.SetSelectedHighlight()` dùng CHUNG kết quả so sánh "===" với nhánh Set Current Tag (`Break(Node).Path == CurrentPath`) thay vì so với `SelectedPath` (biến riêng, đổi mỗi lần user click chọn). Hệ quả: click chọn folder → Confirm bấm được (`SelectedTargetPath` ở Dialog đúng) nhưng KHÔNG thấy highlight xanh (vì Picker so sai biến) — trừ khi trùng ngẫu nhiên `CurrentPath`. Fix: tách node so sánh riêng (`Break(Node).Path == SelectedPath`) cho nhánh `SetSelectedHighlight`, không dùng chung với nhánh tag "hiện tại".

### [CORRECTION] SetLabelColor nhận Slate Color, không phải Linear Color
`WBP_EditableLabel.SetLabelColor(InColor)` — patch P2 (Card 0) giả định Linear Color vì suy loại theo Image widget. Thực tế `Set Color and Opacity` trên TextBlock (built-in UMG) nhận `FSlateColor` (struct bọc ngoài Linear Color). Không phải bug — Blueprint tự convert khi nối Linear Color var vào pin — chỉ sửa lại type khai báo param cho đúng bản chất API.

### [SCOPE] Rename qua context-menu trong picker KHÔNG tồn tại
Test S6b (REG khối A) kỳ vọng right-click row → "Đổi tên" trong Move/Save dialog. Xác nhận: 2d (Task Card 2d) chỉ xây `BeginRenameOnPath` như hàm được GỌI TỪ CODE (trigger duy nhất: nút "+ Thư mục mới" ở Save dialog, sau khi `CreateEmptyFolder`). KHÔNG có UI right-click-để-rename trên row picker — đúng phạm vi 2d ban đầu, không phải thiếu sót. Nếu cần trigger này trong tương lai, cần task card riêng (ngoài C5.8).

### [SCOPE] Test mục 10 TC#2 gốc SUPERSEDED
"Click tên → UI không đổi" (TC#2 cũ) không còn đúng sau Card 1 — click chọn giờ PHẢI đổi UI (highlight xanh). Hành vi mới đúng ý, chỉ ghi nhận thay đổi kỳ vọng test.

### [CEILING] Bind OnFolderSelected trong InitPicker giả định 1 lần/instance
`WBP_MoveToFolderDialog.InitPicker` Bind `Picker.OnFolderSelected` → `HandlePickerFolderSelected` ngay trong hàm `InitPicker` (không phải Event Construct). An toàn CHỈ KHI mỗi lần mở dialog là 1 instance mới (Create Widget mới, đúng hiện trạng). Nếu sau này đổi sang tái dùng instance (gọi `InitPicker` nhiều lần/1 instance) → Bind sẽ chồng (double-fire) → phải dời sang Event Construct lúc đó.

### [SCOPE] 6A của Create Folder (Save dialog)
User tạo folder mới rồi ESC/blur trước khi đặt tên → `WBP_EditableLabel` tự revert về "New Folder (N)" (đã có sẵn cơ chế). Folder rỗng tên auto này vẫn tồn tại trong `Folders.json` — CHẤP NHẬN, giống hành vi NF (New Folder qua context-menu tree chính) đã có từ trước. Không phải bug, không cần cleanup ở C5.8 — nếu cần dọn folder rỗng tên tự động sau này thì đưa vào C10 (regression tổng).

### [CLEANUP] Print debug ở HandleSaveDialogCreateFolder/HandleSavePickerRenameCommitted
Dùng `EnabledState=DevelopmentOnly` (property node, tự strip khỏi Shipping build) thay vì gate bằng biến `bDebugMode` như quy ước project. Quyết định giữ nguyên (đơn giản hơn, đủ hiệu quả) — không đổi. Ghi nhận khác biệt cơ chế: `DevelopmentOnly` cắt theo LOẠI BUILD, `bDebugMode` cắt theo RUNTIME TOGGLE (bật/tắt không cần rebuild).

---

## SPRINT 5 — 13/07/2026 (REG) — C5.8 Chốt sổ (Khối A/B/C/D)

### [CLARIFICATION] A1 (REG Task Card gốc) mô tả nhầm case
Task card gốc viết A1 = "right-click combo → folder chứa nó bị loại khỏi cây" — đây thực ra là mô tả hành vi của MOVE FOLDER (`OnRequestMoveFolder`), không phải MOVE COMBO (`CB_MoveCombo`). 2 nhánh khác nhau theo đúng thiết kế Wire Move đã build: Move FOLDER — `ExcludePath` = chính nó+con cháu → BỊ LOẠI, tag "hiện tại" → trên CHA. Move COMBO — `ExcludePath` = "" → KHÔNG loại gì, tag "hiện tại" → trên chính folder đang chứa combo đó. Test bằng right-click combo cho kết quả ĐÚNG theo nhánh Move Combo (không loại + tag đúng vị trí). Nhánh Move Folder đã verify đúng ở lần test khác trong session (di chuyển "New Folder(2)"). Không sửa code — chỉ đính chính wording task card.

### [SCOPE] Save dialog không live-sync sang cây inventory đang mở phía sau
Tạo/rename folder trong Save dialog KHÔNG tự đẩy cập nhật sang cây inventory chính nếu đang mở đồng thời (bị dialog che) — ĐÚNG THEO THIẾT KẾ (Wire_ExecutionPlan Bước 4/5: "KHÔNG gọi `RefreshComboFolderUI` ở 2 handler — nó refresh cây inventory đang bị che, không phải picker"). Cây inventory tự đồng bộ ở lần load/refresh tự nhiên tiếp theo (đổi tab, mở lại app). Phát hiện REG khối B4, 13/07/2026 — không phải bug. Nếu cần live-sync 2 chiều sau này → task riêng, ngoài scope C5.8.

---

## SPRINT 5 — 14/07/2026 — P1 Combo Thumbnail: đổi kiến trúc capture

### [ARCH] Đổi kiến trúc capture: one-shot → Begin/Finish latent
Plan gốc (`P1_ComboThumbnail_Execution.md`, G0): 1 hàm C++ đồng bộ `CaptureComboThumbnail` — spawn `SceneCapture2D`, `CaptureScene()` 1 phát, `ReadPixels`, Destroy ngay trong cùng 1 lần gọi.

Thực tế: one-shot capture cho ảnh xám phẳng, thiếu bounce light, sai màu rõ rệt so với viewport thật. Lý do: Lumen GI + TAA + auto-exposure là hệ tích lũy qua NHIỀU FRAME THẬT mới hội tụ — camera chính đã chạy hàng nghìn frame nên luôn nhìn cảnh hội tụ, camera phụ vừa spawn chụp NGAY 1 frame duy nhất thì không bao giờ đủ.

Đã thử và loại 2 giả thuyết sai trước khi tìm ra nguyên nhân thật:
1. Auto-exposure lock (ép EV cố định) — SAI, làm ảnh tối hơn.
2. Override Lumen GI/Reflection Method — đúng hướng nhưng không đủ, ảnh vẫn xám (thiếu do chưa đủ FRAME, không phải thiếu METHOD).
3. **[ĐÚNG]** Multi-frame warm-up — xác nhận qua đối chiếu plugin Easy Multi Save đã có sẵn trong project (component `ThumbnailCapture` gắn cố định dưới `FollowCamera`, sống suốt session; nút Save của EMS có độ trễ ~5-7s bất thường — nghi cố ý giữ capture hội tụ).

Quyết định kiến trúc (Fable review 14/07): tách `CaptureComboThumbnail` thành cặp `BeginComboCapture` (spawn, bật `bCaptureEveryFrame=true`) + `FinishComboCapture` (tắt cờ, `ReadPixels`, ghi PNG, Destroy — dọn kể cả khi đọc fail). Bọc bởi Custom Event Blueprint dùng `Delay` (latent hợp lệ theo L8 vì nằm trong Event, không phải Function). Hàm `CaptureComboThumbnail` cũ giữ nguyên, đánh dấu `[LEGACY]`, không xóa, không gọi.

**Ảnh hưởng:** "Nối 1" trong plan gốc (gọi capture đồng bộ ngay trong `SaveComboFromSelection`) phải đổi thành latent — Save Combo sẽ có độ trễ thêm (giá trị Delay warm-up, xem `01_Session_State.md` mục P1) trước khi Broadcast hoàn tất. Broadcast dời xuống SAU `FinishComboCapture`; capture fail vẫn Broadcast bình thường (combo lưu OK, card fallback icon 🧩).

`.h` bị đụng lần 2 (thêm 2 khai báo hàm + forward declare `class ASceneCapture2D;`) — phá lời hứa "chỉ đụng 1 lần" của kế hoạch gốc P1 v1.1. Chấp nhận vì đổi kiến trúc là ngoại lệ hợp lý.

---

## SPRINT 5 — 15/07/2026 — P1 G2/G3/G4: bug dead-end Return Node + wiring

### [BUG-FIX, NGHIÊM TRỌNG] Function thiếu Return Node ở 1 nhánh → output tái sử dụng giá trị cũ
`BP_ComboManager.GetComboThumbnail` — nhánh False của IfThenElse kiểm IsValid(LoadedTex) không
nối Return Node nào (dead-end). Ngộ nhận trước đó (G0 review) "dead-end vô hại với Function" —
SAI với Function CÓ RETURN VALUE: Blueprint không tự trả None, mà GIỮ NGUYÊN output từ lần
gọi hàm TRƯỚC ĐÓ trong cùng frame/vòng lặp. Hậu quả thực tế: LoadComboLibrary gọi
GetComboThumbnail liên tục trong ForEach — combo đầu tiên load thumbnail thành công, MỌI
combo sau đó (chưa có PNG, LoadComboThumbnail trả fail) đều hiện NHẦM đúng ảnh của combo đầu
tiên. Phát hiện qua Print String debug 2 điểm (LoadComboLibrary + OnListItemObjectSet) sau
khi soát tĩnh 3 lớp code (LoadComboLibrary/WBP_ComboCard/GetComboThumbnail) đều "đúng" mà bug
vẫn còn — bài học: đọc code tĩnh có giới hạn, cần runtime Print khi đã loại hết giả thuyết
static. Fix: thêm Return Node tường minh ở nhánh False, Texture2D để trống (None).
**Quy tắc mới thêm AI_Implementation_Rules.md:** mọi Function có Return Value → Q8 L2 phải
kiểm 100% exec path chạm Return Node, không có ngoại lệ "dead-end chấp nhận được" như với
Event/Custom Event.

### [BUG-FIX] 2 dead-end trong SaveComboFromSelection Bước 7 (P1.G4 wiring)
- Nhánh False "không có Pivot" (trường hợp phổ biến nhất) dead-end → combo save nhưng KHÔNG
  capture thumbnail, im lặng không báo lỗi. Fix: nối vào Array_Add (Pivot=None vô hại,
  IsValid tự guard trong C++).
- Nhánh False "ghi JSON fail" (bSaveOK) dead-end → Broadcast OnComboLibraryChanged không
  chạy dù thiết kế gốc yêu cầu luôn broadcast bất kể capture/save thumbnail có fail hay không.
  Fix: nối vào Call Delegate.

### [BUG-FIX] Dead-end ComboManagerRef trong LoadComboLibrary
Nhánh False của IsValid(ComboManagerRef) dead-end → combo đó bị loại khỏi AllComboViews_Combo
hoàn toàn (không chỉ thiếu thumbnail). Rủi ro thấp, chưa quan sát thực tế xảy ra khi phát hiện
(ghi backlog cùng ngày). FIXED 15/07/2026 (thực hiện trực tiếp trong UE5 Editor, ngoài phiên
Claude Code) — nối False vào Array_Add, bỏ qua bước gán Thumbnail.

### [CORRECTION] Delete combo KHÔNG PHẢI = C8
Plan gốc (`P1_ComboThumbnail_Execution.md` V5) ghi nhầm "flow xóa combo (C8)". Thực tế C8 =
"Drag-drop + surface-snap", đã MERGED vào C4 (24/06/2026) — không liên quan xóa combo. Tính
năng xóa combo (BTN_DeleteCombo có layout từ C4, chưa bind handler) CHƯA TỪNG được implement.
Nối 3 (DeleteThumbnail/InvalidateThumbnail khi xóa combo) trong plan G4 gốc BỊ BỎ QUA có chủ
đích trong session 15/07 vì tính năng nền (xóa combo) chưa tồn tại — cần làm khi có task
riêng cho delete combo.

### [ARCH — đã note trước, xác nhận lại] Exposure bug — 2 lần thử Auto-exposure lock đều fail
Lần 2 (15/07, retry sau khi G0-R warmup đã fix vấn đề "ảnh xám phẳng") — VẪN fail, xác nhận
đây là vấn đề KHÁC (nghi ngược sáng/backlit khi khung hình chứa vùng cực sáng), không phải
thiếu warm-up. Deferred, cần Fable review kiến trúc — KHÔNG thử lại Auto-exposure Min/Max
lock lần 3 nếu chưa có hướng mới từ Fable.

---

## P2 — 16/07/2026 — Quyết định kiến trúc Studio Thumbnail

- **[ARCH]** S8 (bật bIsolateCombo) thay bằng Remote Studio — mục tiêu giữ nguyên (hết chữ đỏ
  BP_Khung + background lộn xộn), cơ chế đổi: studio cách ly thay vì isolation trong capture.
  Đã được cuhoang duyệt 16/07.
- **[ARCH]** Exposure bug DEFERRED (14-15/07, 2 lần Auto-exposure lock fail) — GỘP vào P2 Gate C:
  ánh sáng studio chuẩn hóa làm Manual EV100 khả thi lần đầu. Không review riêng nữa.
- **[SCOPE]** SpawnComboByID KHÔNG tái dùng trực tiếp cho thumbnail — trace K2Node 16/07 xác nhận
  5 side effects (ExitEditModeFull, Register groups, Deselect/Select, CaptureSnapshot,
  Cmb_SpawnedActors clear cuối event). Thay bằng Custom Event mới SpawnComboForThumbnail.
- **[CLEANUP backlog]** Node Delay mồ côi trong SpawnComboByID Step D (CallFunction_32, execute
  không nối, Duration=0) — nghi rác thử nghiệm cũ, dọn khi có dịp đụng event này.

---

## P2 — 17/07/2026 — Gate A DONE: Delay ceiling + bug fix aliasing

### [SCOPE] Delay(0.5) → Delay(3.0) hardcode trong SpawnComboForThumbnail
Delay(0.5) sau SpawnComboForThumbnail không đủ cho LoadMeshAsync hoàn tất với combo nhiều món
(bàn/ghế/kệ) → actor tồn tại nhưng mesh rỗng (vô hình, không phải lỗi material đỏ) → Extent tính
thiếu, đồ nhỏ trên bàn lơ lửng giữa trời (bàn invisible bên dưới). Fix tạm: Delay(0.5) → Delay(3.0).
Verify bằng ảnh chụp thật: đủ đồ, ground-align đúng.
Ceiling: chỉ đúng với combo hiện tại (7-8 món, asset resident từ session). Combo nặng hơn / máy
chậm hơn / cold-start asset → có thể vẫn thiếu đồ, fail êm không báo lỗi.
Trigger: trước Gate F (nối dây thật vào SaveComboFromSelection) — bắt buộc thay bằng dispatcher
OnMeshLoaded (BP_FurnitureActor) hoặc cơ chế đếm N asset load xong, thay vì đoán thời gian cố
định. Quyết định kiến trúc dispatcher cần Fable/Opus — đụng BP_FurnitureActor dùng chung toàn
hệ thống (không riêng P2), không tự quyết ở cấp Sonnet.

### [BUG-FIX] Add Actor World Offset dùng nhầm Array Element giữa 2 For Each Loop liên tiếp
Root cause: 2 For Each Loop liên tiếp (Loop 1 tính Cmb_ThumbMinZ, Loop 2 áp DeltaZ qua Add Actor
World Offset) — dây Target của Add Actor World Offset bị kéo nhầm từ Array Element của Loop 1
(qua chuỗi Knot reroute) thay vì Array Element của Loop 2. TypeCheck vẫn pass (cùng kiểu
BP_FurnitureActor) → không lỗi compile, chỉ lộ khi test bằng mắt: 1 actor (cuối Loop 1) bị dịch
chuyển N lần cộng dồn, các actor còn lại đứng yên (lơ lửng). Fix: nối lại Target = Array Element
của chính Loop 2 (MacroInstance_10), không qua Knot cũ của Loop 1.
Bài học: Reroute (Knot) node cho object reference dễ gây aliasing câm khi có ≥2 For Each Loop
liên tiếp cùng thao tác trên actor cùng kiểu — luôn verify Target/nguồn dữ liệu trỏ đúng Loop
đang đứng, không suy luận theo vị trí node trên canvas.

---

## P2 — 17/07/2026 (cuối phiên) — Gate B + Gate C DONE

- **[ARCH]** Cast Shadow=False trên dome (Gate B) — quyết định kiến trúc quan trọng nhất phiên:
  dome đặc chặn hoàn toàn ánh sáng nếu đèn đứng ngoài bán kính R (ràng buộc hình học không thể
  đồng thời thỏa "đèn trong dome" và "góc chiếu đúng theo ảnh sản phẩm chuẩn"). Tắt Cast Shadow
  biến dome thành "chỉ nhận bóng, không chặn sáng" — đúng bản chất backdrop vải/giấy thật, không
  phải vật cản. Receive Shadow giữ nguyên. Root cause thật của chuỗi bug đèn bên dưới — Fable chỉ
  ra sau khi Sonnet loay hoay dịch số vị trí đèn nhiều vòng.
- **[SCOPE]** Màu dome S1 (3 tông #F5F5F5/#EAE8E4/#E8EDF2) dời từ Gate B sang đợt "tối ưu cuối"
  (gộp cùng sofa/mesh/màu) — lúc Gate B chưa có đèn để soi màu đúng, cuhoang quyết định gộp.
- **[BACKLOG]** Faceting/horizon line của sphere dome — quan sát ban đầu nghi có vấn đề (blur do
  đứng sát camera Editor) nhưng chưa xác nhận (chưa test Wireframe). Dời kiểm tra kỹ + custom
  cove mesh (nếu cần) sang đợt tối ưu cuối.
- **[BUG-FIX]** `Rotate Vector Around Axis` InVect.X = 150 thay vì 1500 — gõ tay thiếu 1 số 0 lúc
  refactor Key/Fill sang Function `SpawnStudioLight`. Sửa lại 1500.0.
- **[BUG-FIX]** RectLight Mobility mặc định = Stationary — phụ thuộc Lightmass bake, Remote
  Studio spawn runtime chưa từng bake → gần như không chiếu sáng lên actor động. Fix:
  `Set Mobility(Movable)` ngay sau spawn, trước IsValid.
- **[ARCH]** `Cmb_StudioAnchor` Default Value thực tế = (0,0,0), không phải (500000,500000,Z)
  như plan gốc định — biến khai đúng comment nhưng số thật chưa từng gõ vào Default Value. Sửa
  Default Value → X=500000, Y=500000, Z=0 (Z=0 hợp lệ vì X/Y đã đưa studio ra xa, không còn "sàn
  phòng thật" nào gần để khớp).
- **[CORRECTION]** Nghĩ sai: cộng `+DomeRadius` vào Z đèn để "nằm trong dome" — nhầm ràng buộc
  hình học (quên rằng combo đứng gần ĐÁY dome/gần anchor, không phải giữa dome); cộng DomeRadius
  đẩy đèn lên góc chiếu quá dốc (gần thẳng đứng), sáng lướt qua mặt trước combo. Revert, quay về
  `WorldLoc = Anchor + LightOffset` thuần.
- **[ARCH]** Xung đột hình học: Distance=1500 cố định + Height thấp (250) → đèn lọt RA NGOÀI
  dome, không thể đồng thời thỏa "đèn trong dome" và "góc chiếu đúng" nếu dome là khối cầu đặc
  chặn sáng. Leo thang Fable — giải quyết bằng Cast Shadow=False (xem [ARCH] ở trên), không phải
  bằng dịch số vị trí đèn.
- **[BUG-FIX]** Sau khi Cast Shadow=False, Attenuation Radius mặc định 4000 hụt tầm (đèn cách
  tâm dome ~1920, điểm xa nhất mặt cầu = 3920, sát nút 4000) → góc dome vẫn tối. Tăng lên 8000.0.
- **[ARCH]** HeightOffset=250 tạo góc chiếu quá dốc (elevation ~9° từ Distance=1500) → mặt trước
  combo tối dù nền sáng — nhầm lẫn giữa "đủ thấp để chiếu trực diện" và số liệu thực tế. Đổi
  HeightOffset (Z trong `RotateAngleAxis` InVect) từ 250 → 1500, tạo elevation 45°.
- **[ARCH]** Đề xuất cuối cùng (tưởng đúng nhất): đổi sang Directional Light — Fable bác bỏ vì
  Directional chiếu toàn world (phá phòng thật của đồng nghiệp) + vẫn bị dome chặn (không giải
  quyết gì). Giữ RectLight, dùng Cast Shadow=False làm giải pháp đúng.
- **[BUG-FIX]** `bUseFixedAngle` chưa từng được tick trên node `Begin Combo Capture` trong chuỗi
  debug phím U — việc tick bị bỏ sót giữa các lượt làm, chuỗi U thực ra spawn xong không capture
  đúng góc cố định (tưởng nhầm là đang test fixed-angle). Tick `Use Fixed Angle=True`,
  `Fixed Angle=(Pitch=-15, Yaw=0, Roll=0)`.
- **[BUG-FIX]** `Set Post Process Settings` (Manual EV100) dùng node `Make Post Process Settings`
  — struct MỚI, ghi đè xoá 4 field Lumen override (`DynamicGlobalIlluminationMethod`,
  `ReflectionMethod`) mà C++ `BeginComboCapture` đã set. Không phân biệt "Make" (tạo struct mới,
  mất field khác) và "Set members in struct" (đọc struct hiện có, sửa tại chỗ). Fix:
  `Get Post Process Settings` → `Set members in Post Process Settings` (chỉ sửa Metering Mode +
  Exposure Compensation) → `Set Post Process Settings`.
- **[BUG-FIX]** Thiếu `IsValid(Cmb_CaptureHandle)` sau `BeginComboCapture` trong chuỗi U — nếu
  Begin trả None (Bounds invalid...) → Accessed None, và `Cmb_bThumbBusy` không bao giờ về False
  → kẹt "Thumb busy" vĩnh viễn, cần restart PIE. Thêm IsValid guard: True→chuỗi cũ, False→Print +
  SET bThumbBusy=False.
- **[LESSON]** Bài học quy trình (không phải bug code): nhiều lần đoán sai liên tiếp quanh cùng 1
  vị trí đèn (các bug [ARCH]/[CORRECTION] phía trên) — đúng lúc nên leo thang theo luật "3 lần
  sai cùng chỗ → STOP, hỏi Fable" nhưng bị trễ. Fable review chỉ đúng nguyên nhân gốc (Cast
  Shadow) mà Sonnet không nhìn ra vì cứ cố sửa bằng cách dịch chuyển số vị trí đèn thay vì xét
  lại ràng buộc kiến trúc.

**Verify cuối Gate C — PASS:** bấm phím U với 2 Combo ID khác nhau (sofa trắng, bàn trang điểm
gỗ tối) → cùng góc camera, cùng mức sáng nền.

**Ghi chú vặt cần dọn (không chặn Gate D):**
- `ComboID` spawn (`combo_0BDBFB18...`) vs `ComboID` ghi file `FinishComboCapture`
  (`Combo_0BDBFB18..._studio`, khác hoa/thường + suffix `_studio`) — chỉ ảnh hưởng debug, dọn ở
  Gate F khi bỏ hẳn suffix theo plan.
- Node mới cần xác nhận vào bảng chính thức `AI_Implementation_Rules.md`: `Set Mobility`,
  `Set members in [Struct]` (dùng cho Post Process Settings, có thể dùng lại chỗ khác).

---

## P2 — 18/07/2026 — Gate D prerequisite: lighting isolation

Bối cảnh: Gate D bắt đầu với task "Source Size Key tune bóng mềm khớp ảnh IKEA" — ảnh capture
đầu tiên bị lỗi nặng (cháy sáng, vệt đen, bóng cứng, tông ấm/lạnh đổi theo giờ UDS), không đáng
tin để tune bằng mắt. Toàn phiên dành để điều tra + fix 3 nguyên nhân gốc chặn (blocking); task
gốc Gate D (tune Source Size + sweep 5 combo) CHƯA bắt đầu.

### [CORRECTION] RectLight offset vector — sửa giá trị sai trong trí nhớ/doc cũ
Giá trị THẬT xác nhận qua export K2Node: `RotateAngleAxis(InVect=(1500.0, 0.0, 1200.0),
Axis=(0,0,1))`. Doc cũ ghi `(1500, 0, 1500)` là sai (Z=1200, không phải 1500). Anchor spawn
dome lệch tâm dome đúng 1 Dome Radius theo Z (`Dome Location = Anchor + (0,0,Radius)`) — Anchor
nằm ở ĐÁY dome, không phải tâm. Khoảng cách đèn → TÂM dome = `√(1500² + (1200−Radius)²)`. Với
Radius=2000 hiện tại ⇒ ≈ 1700 < 2000 → đèn nằm SÂU TRONG dome ~300 unit, không đứng ngoài như
nghi ngờ ban đầu — giả thuyết "đèn ngoài bán kính" (xem entry [ARCH] "Xung đột hình học" 17/07)
đã bị LOẠI, không phải nguyên nhân thật.

### [BUG-FIX] Distance Field của mesh Sphere gây tự triệt tiêu RectLight khi Cast Shadow=True
Triệu chứng: Cast Shadow=True trên dome → capture đen 100% dù RectLight nằm trong dome. Cast
Shadow=False → sáng nhưng lẫn ánh sáng ngoài (Sun/SkyLight xuyên qua). Nguyên nhân:
`Engine/BasicShapes/Sphere` build Distance Field dạng khối ĐẶC (tài liệu Epic: mọi điểm trong
mesh lưu khoảng cách ÂM, tức "trong khối đặc") — camera/RectLight/furniture đứng bên trong dome
bị Lumen/DF-shadow coi là nằm trong khối đặc → self-occlusion toàn phần. Fix: Duplicate
`Engine/BasicShapes/Sphere` → asset riêng project `SM_StudioDome` (không sửa Engine gốc — KP3).
Static Mesh Editor → Build Settings → bật **Two-Sided Distance Field Generation**. Đổi
`New Mesh` trong node `Set Static Mesh` của dome sang `SM_StudioDome`.
Ceiling: tài liệu Epic cảnh báo Two-Sided DF tốn ray-marching cost cao hơn — chưa đo tác động
hiệu năng thật. Trigger: verify performance ở Gate 2 (packaged build).

### [ARCH] Lighting Channels cô lập Directional Light (Sun/UDS) khỏi Remote Studio
Thêm node `Set Lighting Channels(Channel0=False, Channel1=True)` cho: `SM_StudioDome` (Static
Mesh Component, sau `Set Cast Shadow=True`, cùng chỗ vừa thêm `Set Mobility=Movable`); RectLight
Key + Fill trong `SpawnStudioLight` (Target=**Light Component**, không phải Primitive Component
— 2 node khác nhau cùng tên "Set Lighting Channels", chọn sai Target type sẽ không compile);
furniture clone `FurnitureMesh` (biến riêng `BP_FurnitureActor`, KHÔNG dùng
`Get Static Mesh Component` — trả rỗng, gotcha đã biết) trong `SpawnComboForThumbnail`. Điều
kiện bắt buộc đã verify: Lighting Channels chỉ hoạt động động (dynamic) khi Mobility=Movable cho
CẢ actor/component VÀ light — dome phải đổi Static→Movable mới (mặc định SpawnActor Static Mesh
Actor ra Static); RectLight và `FurnitureMesh` vốn đã Movable sẵn. Sun (Directional Light UDS)
giữ nguyên Channel 0 mặc định — không đụng, vẫn chiếu sáng phòng thật của user bình thường.
Domain fact (tài liệu Epic): Lighting Channels chỉ áp dụng cho *direct lighting* của dynamic
light (Directional/Point/Spot/Rect) — KHÔNG áp dụng cho SkyLight (ambient/IBL). Giải quyết được
1/2 vấn đề, cần thêm entry dưới.

### [ARCH] Show Flag Settings chặn SkyLight ambient — không đụng biến/actor của đồng nghiệp
Trong `BeginComboCapture`: ngay sau nhánh `Is Valid(Cmb_CaptureHandle) → True`, TRƯỚC Delay
warmup 3.0s, thêm: `Cmb_CaptureHandle` → `Get Capture Component 2D` (bắt buộc lấy Component —
`Cmb_CaptureHandle` là kiểu Actor `SceneCapture2D`, không compatible thẳng với Target của
`Set Show Flag Settings`) → `Make Engine Show Flags Setting(ShowFlagName="SkyLighting",
Enabled=False)` → `Make Array` (1 phần tử) → gán vào pin `Show Flag Settings` của
`Set Show Flag Settings` (Target = Capture Component 2D vừa lấy). Lý do chọn hướng này thay vì
set/restore `Alpha_BP_Master_LightManager_EV.Sky Light Intensity` (biến của đồng nghiệp, quản
lý ánh sáng CẢ LEVEL): không đụng code/actor không thuộc quyền sở hữu combo system; zero ảnh
hưởng lên viewport chính lúc bấm Save combo (set-tạm-rồi-restore sẽ làm cả phòng tối đi ~4s,
thấy được); không có rủi ro race condition (capture fail giữa chừng không làm kẹt biến đồng
nghiệp ở giá trị sai). Kết quả verify: 2 ảnh cùng combo, Time Of Day=960 và Time Of Day=0
(chênh lệch tối đa), Sky Light Intensity giữ nguyên gốc — ra gần như giống hệt nhau. Xác nhận
cô lập hoàn toàn khỏi trạng thái UDS.
Ceiling: có báo cáo cũ trên forum Epic là Show Flags trên Scene Capture có thể bị ignore sau khi
package (chưa rõ còn đúng ở UE5.5.4). Trigger: bắt buộc verify lại ở Gate 2 checklist deploy.

### [CEILING / ⚠️ SUY LUẬN — chưa verify bằng test] Dải đen viền trên khung hình
Vẫn xuất hiện trong mọi ảnh test gần đây, không đổi theo Time Of Day/Sky Light Intensity — độc
lập với 3 fix trên. Giải thích của cuhoang (CHƯA kiểm chứng bằng test hình học cụ thể): là vùng
dome nằm ngoài phạm vi chiếu của RectLight Key/Fill (RectLight là nguồn 1 hướng, có "mặt cắt
zero" ngoài góc lệch — 2 đèn hiện tại lệch ±45° quanh anchor, để lại 1 cung không được chiếu
trực tiếp). Chưa xử lý — để dành cho đúng task Gate D gốc (tune Source Size + sweep 5 combo),
lúc đó mới quyết định có cần mở góc phủ / thêm nguồn sáng nền hay không.

**Việc chờ xác nhận/mở, chưa xử lý trong phiên này:**
- Tên hàm/vị trí chính xác của logic spawn dome (cần export K2Node đầy đủ, phiên này chỉ có
  screenshot node rời).
- Verify Two-Sided DF Generation + Set Show Flag Settings hoạt động đúng trong PACKAGED BUILD
  (2 ceiling ở trên — thêm vào checklist Gate 2).
- Test hình học xác nhận dải đen viền trên khung hình — chưa làm, để dành lúc sweep Gate D.
- Task gốc Gate D (Source Size Key tune, sweep 5 combo) — CHƯA bắt đầu, làm tiếp ở phiên sau.

---

## SPRINT 5 — 19/07/2026 — P2 Noise + Aliasing Fix

Bối cảnh: sau Gate D prerequisite (18/07, lighting isolation), ảnh thumbnail vẫn còn noise nặng
(đốm blotchy ở nền dome + bóng mềm) — đã loại 7 giả thuyết (Delay warmup, Lumen quality
override, TAA showflag, RectLight size, console var temporal, TAA toàn cục, per-component AA —
không compile). Chẩn đoán: `SceneCapture2D` không có temporal accumulation thực sự (TSR không
hỗ trợ scene capture, TAA history không hoạt động dù đủ flags) — khác viewport chính (có
temporal thật, ảnh sạch).

### [ARCH] Mượn Event Tick của BP_ComboManager thay vì subclass/FTickableGameObject cho temporal accumulation
`UComboThumbnail` là `UBlueprintFunctionLibrary` (static function) → không có Tick sẵn trong
C++. Chọn mượn Tick có sẵn của `BP_ComboManager` (đã là Actor, đã có `Cmb_CaptureHandle`, đã có
`EndPlay` cleanup) thay vì subclass `ASceneCapture2D` hoặc dùng `FTickableGameObject`. Lý do:
tối thiểu concept C++ mới cho cuhoang (đang học C++ qua sửa code thật), tái dùng nguyên
`EndPlay` cleanup mechanism sẵn có thay vì phải xây thêm 1 lifecycle riêng. Buffer cộng dồn
(`TArray<FLinearColor>`, ~1M phần tử ở 2048²) sống ở C++ file-scope static
(`TMap<ASceneCapture2D*, FComboAccumState>`, anonymous namespace trong `.cpp`, KHÔNG khai báo
`.h`) — key theo con trỏ `CaptureHandle` (mỗi lần capture = actor mới, không đụng nhau). KHÔNG
đưa buffer lên Blueprint — BP loop qua 1M phần tử sẽ treo máy (VM overhead).

### [ARCH] Cộng dồn temporal + downscale spatial đều làm ở không gian linear color
Cộng dồn temporal (chia N frame, N=24 mặc định qua `Cmb_AccumTargetFrames`) VÀ downscale
spatial (SSAA box filter 2×2, `ComboSSAAFactor` constexpr) đều làm ở `FLinearColor` — chỉ
encode về `FColor` (`.ToFColor(true)`, áp lại gamma sRGB) ĐÚNG 1 LẦN ở cuối cùng.
`FLinearColor(FColor)` tự giải mã sRGB→linear lúc đọc vào. Lý do bắt buộc: gamma không cộng
tuyến tính — cộng thẳng giá trị 8-bit rồi chia trung bình sẽ lệch sáng, rõ nhất ở vùng
tối/bóng đổ (đúng chỗ noise nặng nhất). SSAA factor cố định = 2: RT capture ở
`Resolution × 2` (2048 khi `Resolution=1024`), downscale còn `Resolution` trước khi encode PNG.

### [BUG-FIX] Sửa nhầm hàm CreateRenderTarget2D LEGACY khi áp SSAA factor
File có 2 chỗ gọi `CreateRenderTarget2D` với signature gần giống hệt nhau —
`CaptureComboThumbnail` ([LEGACY], không gọi) và `BeginComboCapture` (hàm thật, có
`bCaptureEveryFrame=true`). Trong session đã từng sửa nhầm vào bản LEGACY trước — build pass
(không báo lỗi vì code hợp lệ) nhưng ảnh ra sai kích thước (512×512 thay vì 1024×1024) vì RT
thật không đổi. Fix: xác nhận đang sửa đúng hàm bằng cách nhìn `bCaptureEveryFrame` — LEGACY
set `false`, thật set `true`. **Bài học ghi lại cho lần sau:** 2 hàm cùng signature gần giống
hệt nhau trong cùng file rất dễ gây sửa nhầm — luôn xác nhận qua 1 field/behavior khác biệt
(ở đây là `bCaptureEveryFrame`) trước khi sửa, không suy luận theo vị trí/thứ tự hàm trong file.

**Test kết quả:**
- Noise (temporal accumulation, N=24): ✅ CONFIRM — "mịn hơn rõ và không giật lúc chụp" (cuhoang
  test trực tiếp, sau khi build pass Bước 1+2 C++ + wiring Bước 3 BP).
- Aliasing/SSAA: ✅ CONFIRM DONE — cuhoang xác nhận đã tự chạy lại checklist test đầy đủ (kích
  thước ảnh ra đúng, không giật thêm so với bản chỉ-noise-fix dù RT giờ 2048²).

Gán vào Gate D (tiếp nối prerequisite 18/07 — lighting isolation) theo quyết định cuhoang lúc
merge delta này; task gốc Gate D (Source Size Key tune + sweep 5 combo) vẫn CHƯA bắt đầu.

**Backlog / chưa làm:**
- Gate G5-style regression VRAM/RAM riêng cho buffer SSAA 2048² — chưa đo.
- Nếu máy yếu giật khi test thật: hạ `Cmb_AccumTargetFrames` (24→16) TRƯỚC, rồi mới hạ
  `ComboSSAAFactor` (2→1) — không đổi 2 biến cùng lúc.
- Dòng code cũ comment lại (`//if (RT) {...}` bản trước SSAA) trong `FinishComboCapture` — còn
  sót lại trong file, dọn khi có dịp (không gấp).

---

## P2 — 20/07/2026 — Gate D: Rim Light + VRAM Fix + Source Size chốt + 2 bug kiến trúc mới (OPEN)

### [SCOPE] Rim Light — 3-point lighting, mở rộng ngoài phạm vi Gate C
Gate C chỉ định nghĩa 2 đèn Key/Fill. `SpawnStudioLight(AngleOffsetDeg, Intensity)` (có từ Gate
C) gọi thêm lần thứ 3: `SpawnStudioLight(180.0, 2500000.0)` → `Cmb_StudioRimLight` (biến mới,
RectLight Object Reference). Đã duyệt trước khi làm (KP2 — prep có chủ đích, không phải lệch
âm thầm).

Bộ số cuối cùng — chốt sau kiểm chứng ảnh thật, đổi cả `InVect` dùng chung 3 đèn so với Gate C
gốc:

| Thông số | Gate C gốc | Chốt 20/07 |
|---|---|---|
| InVect (offset đèn, RotateAngleAxis) | (1500, 0, 1200) | (1200, 0, 1500) |
| Key SourceSize/Intensity/AttenRadius | 150 / 5,000,000 / 8000 | 150 / 5,000,000 / 3000 |
| Fill SourceSize/Intensity/AttenRadius | 150 / 1,666,667 / 8000 | 150 / 1,666,667 / 3000 |
| Rim SourceSize/Intensity/AttenRadius | (chưa có) | 150 / 2,500,000 / 3000 |
| Post Process Exposure Compensation | 0.0 | +6.0 |

Verify PASS: ảnh combo To (sofa) + Tường (bàn thờ) — bóng mềm, không hotspot, tông sáng nhất
quán. Node flow đầy đủ: `Blueprints/Blueprint_Logic_NodeFlow.md`.

Lưu ý xử lý sai lầm trong lúc tune: ban đầu nghi Fill Intensity gõ nhầm 16,666,667 (thừa 1 số
0) — cuhoang xác nhận đây chỉ là lỗi đọc số của Sonnet lúc trình bày lại, giá trị thật luôn đúng
1,666,667. Không phải bug thật, ghi lại để tránh nhầm lần sau khi đọc log cũ.

### [BUG-FIX] ×2 — VRAM/GPU crash, EndPlay BP_ComboManager wiring sai
Triệu chứng: GPU Crashed/D3D Device Removed sau ~10 lần PIE liên tiếp, crash cả lúc Alt+P
Standalone. Root cause xác nhận qua đọc `ComboThumbnail.cpp` + export K2Node EndPlay (không
phải bug C++):
1. `Map_Clear(Cmb_ThumbnailCache)` nằm lồng trong nhánh True của
   `Branch(IsValid(Cmb_CaptureHandle))` — chỉ chạy nếu đang capture dở dang lúc tắt PIE (hiếm).
   90% lần tắt PIE bình thường → cache thumbnail KHÔNG BAO GIỜ được dọn, tích lũy VRAM qua
   session.
2. Thứ tự đọc/ghi biến sai: `SET Cmb_CaptureHandle = None` chạy TRƯỚC
   `ResetComboAccumulation(GET Cmb_CaptureHandle)` — hàm nhận None, no-op. Buffer C++
   (`TMap<ASceneCapture2D*, FComboAccumState>`) không được Remove, mồ côi vĩnh viễn nếu PIE tắt
   giữa lúc accumulate.

Fix: chỉ sắp xếp lại node có sẵn (Blueprint), KHÔNG đụng C++/.h — xem node flow đầy đủ trong
`Blueprints/Blueprint_Logic_NodeFlow.md`. Verify: đọc code + đối chiếu export K2Node — CHƯA đo
VRAM dài hạn bằng `stat rhi` (cuhoang không có thời gian chạy loop đo, theo dõi tự nhiên trong
lúc làm việc). Node mới cần thêm vào bảng "Nodes chờ xác nhận": `Get Texture Target`.

Ceiling: margin VRAM còn mỏng (đo 1 lần trong phiên — Editor rảnh 5.6GB, Alt+P Standalone →
7.6GB, RTX 3060 8GB chỉ còn ~400MB đệm) — giới hạn kiến trúc nền (PIE chia sẻ GPU device, đã ghi
`Bugs/Bug_GPU_VRAM_Crash.md`), fix hôm nay giảm 1 nguồn leak lớn nhưng không đổi giới hạn
hardware. Trigger: nếu vẫn crash sau fix này → cần RenderDoc/Nsight đo sâu hơn (cùng nợ kỹ thuật
với P1 Gate G5).

### [CORRECTION] Source Size Key = 500 — chốt bằng duyệt mắt, không phải gõ nhầm
`Cmb_KeySourceSize` = 500 (default cũ 150) — cao hơn nhiều range gợi ý ban đầu (100-300); cuhoang
xác nhận đây là lựa chọn thẩm mỹ có chủ đích sau khi so sánh trực tiếp với ảnh IKEA tham chiếu
(cuhoang gửi 15/07).

### [ARCH — OPEN, chờ Fable/Opus] Bug #1 — Dome cong (sphere) nuốt chân đồ footprint rộng
Root cause xác định qua đọc code + suy luận hình học: dome là sphere R=2000,
`Location.Z = Anchor.Z + R` → mặt trong sphere càng dâng cao hơn Anchor theo bán kính ngang `r`
(`ΔZ = R − √(R² − r²)`). Ground-align hiện tại tính 1 `DeltaZ` duy nhất cho CẢ combo (coi "sàn"
là mặt phẳng) — nhưng mặt dome không phẳng. Combo sofa (footprint bán kính ~210) → `ΔZ ≈ 11
unit`, đủ để dome che chân/đế ở rìa. Combo Dẹt (thảm, footprint ~204) — FAIL nặng hơn nhiều,
nghi cùng root cause nhưng CHƯA xác nhận bằng số (chưa loại trừ khả năng item lạc đàn kéo giãn
Bounds bất thường).

Nguồn gốc kiến trúc: Gate A có sàn phẳng tạm (StaticMeshActor Plane); Gate B (17/07) bỏ hẳn
plane này, dùng đáy dome làm sàn — hợp lý cho combo nhỏ/gọn nhưng vỡ trận với combo footprint
rộng. Review Fable (16/07) diễn ra TRƯỚC quyết định Gate B (17/07) — root cause chưa tồn tại lúc
review, không phải Fable bỏ sót.

3 phương án đề xuất (chưa chọn — đảo ngược 1 phần quyết định [ARCH] Gate B đã DONE, cần
Fable/Opus quyết):
1. Thêm lại đĩa sàn phẳng nhỏ (khôi phục kiến trúc Gate A đã bỏ), bán kính đủ bao combo lớn
   nhất thư viện, material khớp màu dome.
2. Tăng `Cmb_StudioDomeRadius` lớn hơn nhiều (2000→5000+) — giảm độ cong tại cùng bán kính
   footprint, không giải quyết tận gốc cho combo cực rộng tương lai.
3. Chấp nhận known-limitation cho nhóm combo rộng — không khuyến nghị (sofa là loại phổ biến
   nhất).

Cần xác nhận thêm (chưa làm — đề xuất bước tiếp theo): Print `Radius`/`Distance` trong
`BeginComboCapture` khi chụp lại combo Dẹt, để xác nhận có cùng root cause với sofa hay là bug
khác. Bug ghi tại `Bugs/Open_Bugs.md`.

### [ARCH — OPEN, chờ Fable/Opus] Bug #2 — Combo "Cao" (Ceiling) dính lỗi ground-align với "Tường" (H1), chưa từng ghi nhận
Combo test "Cao" (3 item `surfaceType: "Ceiling"` — quạt trần, điều hòa âm trần): ground-align
hiện tại kéo CẢ cụm xuống chạm "sàn" (đáy dome) — sai hoàn toàn với đồ gắn trần. Plan gốc (H1)
chỉ ghi known-limitation cho `surfaceType: "Wall"`, chưa từng nhắc `"Ceiling"` dù chung 1 lỗi
kiến trúc. Ảnh chụp thực tế còn cho dấu hiệu các item trong cùng combo không cùng mặt phẳng sau
ground-align (bóng đổ tách rời) — CHƯA điều tra sâu.

Đề xuất: gộp quyết định H1 (Wall) và bug này (Ceiling) cùng lúc — vd bỏ qua ground-align nếu
TOÀN BỘ item trong combo có `surfaceType` khác `"Floor"`. Bug ghi tại `Bugs/Open_Bugs.md`.

---

### [ARCH] P2 — 20/07/2026 (Nấc 1) — Surface-Aware Ground-Align, Bug-CeilingGroundAlign FIXED

**Bối cảnh:** Bug-CeilingGroundAlign (combo trần bị chôn xuống sàn, phát hiện Gate D sweep sáng
20/07) đã fix qua Function mới `ResolveThumbAlign` — thay khối align inline đơn nhất (1 DeltaZ
cho cả combo) bằng phân loại theo `PlacementSurfaceType`. Node flow đầy đủ: xem
`Blueprints/BP_ComboManager.md` mục ResolveThumbAlign.

**[SCOPE] Nấc 1 vs Nấc 2 (quyết định 20/07):** chỉ làm surface-aware align (đổi công thức
DeltaZ + category), KHÔNG làm rig-trần (below-front key light, camera from-below cho pure
Ceiling/Wall) — đó là Nấc 2, backlog, chờ combo trần đủ quan trọng mới làm. Bar PASS Nấc 1 cho
combo trần: không chôn sàn + gọn trong khung + đọc được món — KHÔNG đòi hero-from-below.

**[ARCH — MỞ RỘNG NGOÀI SCOPE BAN ĐẦU, KP2 đã duyệt] Wall-priority rule:** Test combo bàn thờ
thật (`combo_C470030D...`, 1 item Wall + 14 item Floor) lộ ra thiết kế Nấc 1 gốc (HasFloor luôn
thắng tuyệt đối) sai — bàn thờ bị kéo chìm dome dù có mount Wall, vì đa số item mang tag Floor
(đồ đặt trên kệ, không phải đứng sàn thật). Thêm `WallMinZ` + so sánh `FloorMinZ < WallMinZ`:
Floor "tựa" trên Wall (bàn thờ) → Wall thắng; Floor đứng độc lập thấp hơn Wall (sofa+tranh
tường) → Floor vẫn thắng như cũ. Verify: cả 2 case test PASS, không ảnh hưởng combo Mixed
(sofa+quạt trần, không có Wall) đã PASS trước đó.

**[ARCH — MỞ RỘNG NGOÀI SCOPE BAN ĐẦU, KP2 đã duyệt] Margin fix cho nhóm non-Floor:** Công thức
gốc "center bounds vào Anchor.Z" (đã duyệt lúc thiết kế Nấc 1) vỡ khi combo extent Z lớn — bàn
thờ (extent=43.8) có nửa dưới bounds xuyên qua mặt dome thật (Anchor.Z = điểm tiếp xúc vật lý
đáy dome), gây chìm/khuất sau mesh dù Category đã đúng Wall. Sửa: `DeltaZ = AnchorZ − AllMinZ +
10` (đáy combo luôn nổi TRÊN Anchor.Z, margin cố định 10 unit) thay vì center vào Anchor.Z.
Verify bằng ảnh capture combo bàn thờ trước/sau fix — trước: chìm nặng, sau: đầy đủ toàn bộ đồ
trên kệ, không cắt/khuất.

**[LESSON]** Cả 2 mở rộng trên đều phát hiện qua test bằng **combo thật** (không phải combo dựng
tay đơn giản) — combo bàn thờ (đồ thật + mount tường thật) lộ ra 2 lỗi thiết kế mà test case đơn
giản (Floor thuần/Ceiling thuần/Mixed) không chạm tới. Bài học: ưu tiên test bằng data thư viện
thật khi có sẵn, trước khi coi 1 nhánh logic là "đã đủ test".

**[DỌN] Xóa `Cmb_ThumbMinZ`:** class var của align inline cũ (Gate A), dead sau khi thay bằng
Function `ResolveThumbAlign`. Verify không còn tham chiếu (compile sạch sau xóa). Xóa 20/07/2026.

**Test 6/6 case PASS:**
| # | Combo | Category | Kết quả |
|---|---|---|---|
| 1 | Floor thuần (`combo_9706EBDF...`) | Floor | ✅ regression |
| 2 | Ceiling thuần (`combo_057470B1...`) | Ceiling | ✅ |
| 3 | Bàn thờ Wall+Floor lẫn (`combo_C470030D...`) | Wall | ✅ (sau 2 lần mở rộng) |
| 4 | Mixed sofa+quạt trần (`combo_EB8A2889...`) | Floor | ✅ không đổi bởi Wall-priority |
| 5 | Combo cũ thiếu field surfaceType (`banan01`/`combo_9ED326F2...`) | Floor | ✅ fallback đúng |
| 6 | Undo/Recent/EMS Save→Load | — | ✅ sạch |

**Ceiling/trigger:** margin=10 unit chốt bằng test 1 combo (bàn thờ). Ceiling: đủ cho combo hiện
có trong thư viện. Trigger: nếu xuất hiện combo non-Floor có extent Z lớn hơn đáng kể — tăng
margin hoặc tính margin theo % extent thay vì hằng số.

**Việc còn Open (không thuộc Nấc 1):**
- Bug-DomeCurvature (dome cong nuốt chân đồ Floor footprint rộng) — đồng nghiệp đang dựng dome
  custom, báo khi xong.
- Task gốc Gate D (Source Size Key tune + sweep 5 combo hình dáng) — chưa bắt đầu, chờ dome
  custom xong mới tiếp tục (độc lập với Nấc 1, có thể chạy song song).
- Nấc 2 (below-front key + camera from-below cho pure Ceiling/Wall) — backlog, Switch stub đã
  dựng sẵn 4 pin trong chuỗi phím U, chờ quyết làm khi combo trần đủ quan trọng.
- Triệu chứng "item combo trần không cùng mặt phẳng / bóng tách rời" (ghi nhận Gate D sweep sáng
  20/07) — điều tra sơ bộ qua JSON `combo_057470B1...`: 3 item đều relLocation.Z≈0, combo được
  thiết kế đặt dàn trải X/Y (mô phỏng bố trí thiết bị trần thật trong phòng, không phải 1 cụm
  khít nhau) — không phải bug từ ResolveThumbAlign. Đóng, không cần xử thêm.

---

### [ARCH] P2 — 20/07/2026 (Dome Custom) — Bug-DomeCurvature FIXED, Sweep 4/5 Loại

**Bối cảnh:** Bug-DomeCurvature (dome sphere cong nuốt chân đồ combo footprint rộng — sofa/thảm,
phát hiện Gate D sweep sáng 20/07) đã fix qua dome custom do đồng nghiệp dựng, thay thế hoàn
toàn quyết định [ARCH] Gate B (17/07) dùng `/Engine/BasicShapes/Sphere`.

**Kiến trúc dome mới:**
- Asset riêng: khối cylinder kín, đáy bo cong (không phải sphere đặc toàn phần).
- Size gốc mesh: approx 501×501×501 unit.
- Spawn: `New Scale 3D = Make Vector(Cmb_StudioDomeRadius/320.0, .../320.0, .../320.0)` — đổi
  từ công thức cũ `R/50` (do đổi mesh gốc, không đổi ý nghĩa `Cmb_StudioDomeRadius` = 2000.0).
- Location Z vẫn `Cmb_StudioAnchor.Z + ...` theo pattern cũ (không đổi biến `Cmb_StudioAnchor`).
- **Vùng đáy phẳng tuyệt đối trong bán kính ~500 unit quanh tâm** — đủ bao mọi combo Floor hiện
  có trong thư viện (combo To vừa test có bán kính footprint ~193-270 unit, vẫn nằm trong vùng
  phẳng, không chạm phần bo cong).

**[ARCH — ĐẢO NGƯỢC quyết định Gate B 17/07] Cast Shadow = True:** Dome cũ (sphere engine) chốt
`Cast Shadow=False` vì lo sphere đặc chặn hoàn toàn ánh sáng đèn Key/Fill đứng ngoài bán kính R.
Dome mới chạy `Cast Shadow=True` và verify KHÔNG có vệt tối/chặn sáng bất thường — kể cả với
combo trải rộng nhất (sofa 15 món, item xa tâm nhất ở X≈±148, Y≈-65÷142). Giả thuyết: hình học
mới (đáy phẳng bo cong, không phải cầu đặc bao quanh mọi phía) đủ khác để vấn đề chặn sáng gốc
không còn xảy ra — Cast Shadow=True giờ an toàn, và cho bóng đổ tự nhiên hơn (contact shadow
thật của dome lên chính nó/vật thể).

**Test verify (2 combo worst-case, chọn vì bán kính footprint lớn nhất từng có trong thư viện):**
| Combo | boundingBoxExtent (X,Y) | Kết quả |
|---|---|---|
| Dẹt — thảm tròn 3200mm (`combo_83D018984B2BAE3C346F3D8ED705480F`) | — (tròn, R≈160cm mesh gốc) | ✅ PASS — thảm hiện đầy đủ 4 cạnh, phẳng lì, đồ trên thảm không chìm |
| To — sofa Đồng Gia 15 món (`combo_E1C979FA45360AEC3BC83C8F512FF78F`) | 192.9 / 186.2 | ✅ PASS — chân sofa 3 phần + đôn + thảm tròn đều chạm sàn phẳng mọi góc, bóng đổ tự nhiên, không vệt tối bất thường |

**Trạng thái:** ✅ FIXED. `Bugs/Open_Bugs.md` cập nhật đồng thời.

---

### [SCOPE] P2 — 20/07/2026 (Sweep 5 Loại) — 4/5 PASS chính thức, "Cao" PASS sơ bộ (chờ data thật)

Sau khi dome custom FIXED, chạy lại/tổng kết sweep 5 loại combo (task gốc Gate D, tạm dừng từ
sáng 20/07):

| Loại | Combo test | Kết quả | Ghi chú |
|---|---|---|---|
| Nhỏ | (test lần đầu, trước dome fix — không phụ thuộc bug curvature) | ✅ PASS | Regression, không cần test lại |
| To | `combo_E1C979FA...` (sofa 15 món) | ✅ PASS | Trên dome mới, xem mục Dome Custom ở trên |
| Dẹt | `combo_83D018984B...` (thảm tròn) | ✅ PASS | Trên dome mới, worst-case cũ đã fail, nay pass sạch |
| Tường | `combo_C470030D...` (bàn thờ, qua Nấc 1 Wall-priority) | ✅ PASS | Xem DEVIATIONS mục "P2 — 20/07/2026 (Nấc 1)" |
| Cao | Stack dựng tay (bàn tròn + ghế + đèn bàn + tượng gỗ, chồng thủ công) | ⚠️ PASS SƠ BỘ | Xem chi tiết bên dưới |

**[QUYẾT ĐỊNH — Lựa chọn B, 20/07] Case "Cao" — PASS sơ bộ, chưa đóng hẳn:**
Test bằng cách chồng tay 4 món rời (bàn tròn đáy → ghế → đèn bàn (lamp) → tượng gỗ trên cùng) để
tạo 1 "combo" cao bất thường, không phải combo tự nhiên nào trong thư viện. Kết quả kỹ thuật
PASS: toàn bộ stack nằm gọn trong khung (auto-fit đúng dù tỷ lệ cao bất thường), bàn đáy chạm
sàn phẳng tốt, ánh sáng đều dọc suốt chiều cao không tối dần lên đỉnh.

**Giới hạn của kết quả này:** stack dựng tay không đại diện đúng trải nghiệm thật với 1 combo
kệ/tủ cao liền khối (trọng tâm, footprint, silhouette khác hẳn tháp đồ rời rạc). Quyết định
20/07 (Lựa chọn B): giữ kết quả này làm **bằng chứng sơ bộ đã PASS** (không phải regression risk
— hệ thống render đúng vật lý với input bất thường), nhưng **chưa coi case "Cao" đã đóng hoàn
toàn**. Cần test bổ sung bằng 1 combo kệ/tủ cao thật khi có sẵn trong thư viện, trước khi tuyên
bố Gate D sweep DONE 5/5.

**Trạng thái Gate D tổng thể:** 4/5 loại đóng chính thức. 1/5 (Cao) mở treo — chờ combo thật,
KHÔNG chặn các việc khác (Nấc 2, tối ưu cuối, Sprint kế tiếp).

---

### [ARCH] P2 — 20/07/2026 (Gate E) — Depth of Field DONE

**Node:** mở rộng "Set members in Post Process Settings" (Gate C, dùng chung với Manual EV100)
— tick thêm 2 field trong panel Pin Options: `Lens | Depth of Field → Focal Distance` và
`Aperture (F-stop)`. Không tạo node Set mới.

**[VERIFY — phát hiện, không phải bug] Plan gốc sai giả định:** §7 Gate E ghi "FocalDistance =
Distance auto-fit (số có sẵn trong Begin)" — thực tế biến `Distance` chỉ tồn tại CỤC BỘ bên
trong C++ `BeginComboCapture`, KHÔNG xuất ra output pin nào cho Blueprint đọc. Xử lý: xấp xỉ
bằng `Vector Distance(GetActorLocation(Cmb_CaptureHandle), Cmb_StudioAnchor)` — không cần sửa
C++. Ceiling: đủ chính xác cho mọi combo hiện có (tọa độ tương đối cân quanh gốc). Trigger: nếu
sau này có combo relLocation lệch tâm rất xa (design bất thường) → sai số FocalDistance tăng,
cân nhắc thêm out-param `Distance` thật vào `BeginComboCapture` (C++, .h chạm thêm 1 lần).

**Aperture (F-stop) = 2.8 — chốt bằng test đối chứng:**
- f/2.8 (giá trị chọn): blur rất nhẹ trên combo hiện có (Nhỏ/To/Dẹt — độ sâu Z-spread nông) —
  ban đầu cuhoang thấy "không rõ nét để phân biệt trước/sau".
- Test chẩn đoán f/1.0 (tạm thời, phóng đại lỗi để loại trừ khả năng pipeline không chạy): blur
  mạnh rõ rệt → xác nhận pipeline HOẠT ĐỘNG ĐÚNG, không phải bug. Kết luận: combo hiện có không
  đủ độ sâu để f/2.8 tạo blur rõ mắt — đây là hành vi đúng vật lý, không phải thiếu sót.
- Quyết định giữ 2.8: khớp gu ảnh tham chiếu IKEA (catalog sản phẩm sắc nét gần như toàn bộ,
  DOF chỉ tách nhẹ khỏi nền, không tạo hiệu ứng "chụp máy ảnh chuyên nghiệp" rõ rệt).

**Trạng thái:** ✅ DONE. Gate F là bước tiếp theo (nối dây thật + closure), không phụ thuộc
Gate E ngoài việc field DOF đã có sẵn trong Post Process Settings, tự động áp dụng khi Save
Combo thật chạy qua cùng pipeline.

---

## P2 — 21/07/2026 — Gate F: nối Save flow thật + fix framing rotation-invariant

**[ARCH] Radius bounding rotation-invariant** (`BeginComboCapture`, ComboThumbnail.cpp)
Cũ `Bounds.GetExtent().Size()` (nửa đường chéo AABB) rotation-VARIANT → cùng combo xoay khác ra
zoom khác (Distance 235.77 vs 282.75, ~20%). Mới `max(Dist(actor→Center)+actor.BoundsExtent.Size())`
— bất biến xoay quanh Center. Sau: 248 vs 263 (~6% dư, Center vẫn hơi trôi).
- **Ceiling:** đủ dùng tới khi cần góc chụp chuẩn hoá hoàn toàn (Sprint 6).
- **Trigger nâng cấp:** làm Feature-CanonicalStudioAngle → Center có thể đổi sang
  Cmb_StudioAnchor (tâm xoay cố định thật) → về 0% chênh.
- **Không đụng:** chữ ký hàm, BP call sites.

**[ARCH] Broadcast dời khỏi Bước 7 sang Event Tick tail**
Bắt buộc, không phải lựa chọn: pipeline giờ async qua Tick (N=24), Bước 7 gọi
`BeginThumbnailCapture` xong kết thúc ngay (không đợi được). Nếu Broadcast ở lại Bước 7 → chạy
TRƯỚC khi ảnh chụp xong → card không có ảnh mới. Dời Broadcast vào Tick tail (chạy sau Finish
thật). Nhánh False (JSON fail) vẫn Broadcast trực tiếp ở Bước 7.

**[CORRECTION] FixedAngle.Yaw thật = 55, không phải 0**
Doc cũ (BP_ComboManager §Việc 4, Blueprint_Logic_NodeFlow) ghi `FixedAngle=(Pitch=-15,Yaw=0,Roll=0)`.
Đối chiếu export K2Node THẬT 21/07: Yaw=55. Promote thành class var `Cmb_StudioCamYaw`
(default 55) — 1 nguồn sự thật cho cả FixedAngle lẫn công thức DeltaYaw Bước 7.

**[BUG tồn tại, tự đóng nhờ Gate F] Save thật ra ảnh 2048² thô**
Trước Gate F, Bước 7 chụp actor thật `Begin→Delay→Finish` KHÔNG qua accumulate → buffer rỗng →
C++ fallback ReadPixels 1 frame ở RT thật 2048² (không downscale, còn noise). Không ai báo vì
code chạy hợp lệ (không crash). Gate F chuyển Save qua pipeline Studio (Tick N=24 + SSAA
downscale) → tự hết. Không cần task riêng.

---

## C6 — 22/07/2026 — Favorite + Recent combo DONE + 2 bug fix

C6.1-C6.4 (API/nút tim/hook Recent/tab hiển thị) thực hiện trực tiếp trong UE5 Editor, ngoài
phiên Claude Code — không có deviation ghi ở đây cho phần đó (không đối chiếu được node flow).
2 bug fix dưới đây phát hiện trong lúc test C6, verify qua export K2Node thật.

**[BUG-FIX] `AddRecentCombo` — `SaveUserPrefs` dead-end khi Recent < 48 phần tử**
`Call SaveUserPrefs` nằm trong nhánh `True` của `Branch(Array Length(RecentComboIDs) > 48)`
(bước trim cap) — nhánh `False` (< 48 combo, MỌI test thực tế) không nối gì, dead-end. RAM luôn
đúng (Print tối 21/07 ra count tăng dần đúng) nhưng chỉ ghi xuống đĩa khi Recent vượt cap 48 →
spawn combo mới, tắt PIE, mở lại → Recent mất combo vừa spawn. Fix: rút `SaveUserPrefs` ra khỏi
nhánh `True`, merge cả 2 nhánh cùng trỏ vào. Ghi chú phụ: cap thật = 48, không phải 20 như
`UX_Phase2_Plan.md` ghi trước đây — sai lệch tài liệu, không phải bug. Node flow:
`Blueprints/BP_FurnitureUserPrefsManager.md`.

**[BUG-FIX] Recent hiển thị chỉ 1 card (fix tối 21/07, xác nhận lại sáng 22/07)**
`FilterByCategory` nhánh Combo/Recent dùng `ClearListItems + ForEach + AddItem` (loop) — gọi
`AddItem` nhiều lần liên tiếp trong TileView không refresh đúng từng lần, chỉ hiện 1 card cuối.
Fix: đổi sang `Set List Items(CTV_ComboCard, OrderedViews)` (batch 1 lần, giống Favorite/All).
Bài học tổng quát (không riêng Combo — áp dụng mọi TileView/ListView) đã ghi vào skill
`ue5-blueprint-rules` mục **L12** (21/07).

**[OBSERVATION, không phải bug] Duplicate `comboId` khi copy tay file JSON**
Copy tay file `.json` trong Explorer rồi đổi tên → field `comboId` bên trong KHÔNG tự đổi theo
tên file → 2 file khác tên nhưng cùng ID logic → Favorite/Recent coi là 1 combo. Không sửa bây
giờ — xử lý khi làm tính năng Save As/Save đè (Save As phải sinh `comboId` MỚI). Ghi
`Bugs/Open_Bugs.md` mục "Note-DuplicateComboID".

---

## C9 Replace — 30/07/2026 — Folder Highlight Fix + C9.b–C9.f

**[BUG-FIX] Folder Highlight — `FilterByFolderPathWithUI` ăn nhầm full path**
Bước gọi `FilterByFolderPath` bên trong `FilterByFolderPathWithUI` (`WBP_FurnitureInventory`)
truyền `FolderPath` FULL path thay vì relative → `CurrentFolderPath` bị SET sai format →
`IsPathActive` chỉ match được node gốc rỗng ("All") → vào Replace bằng code (không qua
`OnTreeNodeClicked`/`OnChipTagClicked`) chỉ "All" sáng, tree/chip không sáng đúng node. Fix: đổi
input pin sang `Split.RightS` (relative, cùng nguồn dùng chung chip/breadcrumb) + chèn
`UpdateFolderHighlights()` sau `FilterByFolderPath`. Xem `Widgets/WBP_FurnitureInventory.md` v3.16.

**[BUG-FIX] Bug A2 — `OnMeshSelected` nhảy tree về Furniture giữa combo replace**
`OnMeshSelected` (`WBP_FurnitureInventory`) trước đây chạy nhánh mesh vô điều kiện khi
`IsReplaceModeActive()==True`, không phân biệt `ReplaceTarget` Mesh/Combo — chọn actor thuộc cụm
combo (qua `ResolveSelectedComboRoot`) vô tình trigger navigate-folder mesh, nhảy tree về tab
Furniture giữa lúc đang Combo replace. Fix: thêm guard `Branch(ReplaceTarget==Mesh)` bên trong.

**[BUG-FIX] Bug B — `EnterReplaceMode` thiếu SET `CurrentInventoryMode` + visibility CTV + `UpdateTabHighlight`**
`EnterReplaceMode` (`WBP_FurnitureInventory`) chuyển sang Combo replace nhưng thiếu 3 bước: SET
`CurrentInventoryMode` đúng mode Mesh/Combo, toggle visibility `CTV` tương ứng, gọi
`UpdateTabHighlight` — tab/nội dung hiển thị sai khi vào Replace combo. Fix: bổ sung đủ 3 bước
trong `EnterReplaceMode`. Xem `Widgets/WBP_FurnitureInventory.md` v3.16.

**[OPEN, chưa verify] StartReplaceMode nhánh DA legacy (RowName=="None")**
Chưa verify format `DA_FurnitureItem.MeshFolderPath` (đường DA legacy, save cũ) có chứa
`"Object_Model/"` hay không giống `DT_FurnitureCatalog`. Nếu DA lưu path khác format, `Split`
trong `FilterByFolderPathWithUI` có thể cắt sai → tree/chip sai khi mở save cũ + Replace. Cần
test riêng với 1 save cũ thật. Ceiling: prefix `"Object_Model/"` hardcode trong `Split`.

**[CLEANUP] Chốt phương án normalize path — Split.RightS làm nguồn duy nhất**
Phương án chọn: normalize full→relative tại `Split.RightS` trong `FilterByFolderPathWithUI`, dùng
chung cho tree + chip + breadcrumb + `FilterByFolderPath`. KHÔNG strip prefix ở nguồn
`StartReplaceMode` (`BP_FurnitureInputManager`) — giữ full path ở đó, xem
`Blueprints/BP_FurnitureInputManager.md` mục `StartReplaceMode`.

**[CEILING] `Split` In-Str = `"Object_Model/"` hardcode**
Trigger nâng cấp: nếu mesh root đổi chỗ trong cấu trúc thư mục, HOẶC làm chuẩn hóa = DataTable
lưu sẵn relative path / 1 hàm normalize path dùng chung cho cả tree-builder lẫn replace path.

**[SCOPE] `SwitchInventoryMode(Combo)` gọi `FilterComboByFolder` 2 lần trong 1 frame**
`StartReplaceComboMode` (`BP_FurnitureInputManager`) gọi `SwitchInventoryMode(Combo)` (đã tự
`FilterComboByFolder("__ALL__")` bên trong) rồi gọi lại `FilterComboByFolder(FolderPath thật)` —
build 2 lần/frame. Chấp nhận (kết quả cuối đúng, không thấy nháy UI khi test). Ceiling: không
thấy nháy UI. Trigger: thấy nháy/giật → thêm param `bSkipInitialFilter` cho `SwitchInventoryMode`.

**[PLAN-SAI, deviation so với Execution Plan] `Cmb_ReplaceCenter`→`Cmb_ReplaceAnchor`**
`docs/Plans/24-07-2026_C9_Execution_Plan.md` §5.1/§6 đặt tên `Cmb_ReplaceCenter` (tính bằng
`CalculateCenter`, centroid thuần). As-built đổi thành `Cmb_ReplaceAnchor` (tính bằng
`CalculateComboAnchor` — center XY + anchorZ theo Floor/Ceiling) để fix bug anchor-vs-center
mismatch khi spawn cụm thay thế. Xem `Blueprints/BP_ComboManager.md` v1.14.

---

## Replace UX Fix — P1.2 (01/08/2026) — Lỗi thứ tự tiềm ẩn trong RefreshComboFolderUI

**Phát hiện:** Khi implement P1.2, ban đầu đặt `RefreshChipBreadcrumb()` SAU
`UpdateComboFolderHighlights()` trong `StartReplaceComboMode` (theo đúng thứ tự ghi trong
doc cho `RefreshComboFolderUI`: *"RefreshChipBreadcrumb() gọi từ RefreshComboFolderUI SAU
UpdateComboFolderHighlights"*) → chip mới dựng ra không được highlight (vì
`UpdateComboFolderHighlights` chạy khi `VB_ChipTagArea` còn rỗng). Sửa bằng cách ĐẢO
NGƯỢC thứ tự trong `StartReplaceComboMode` — khớp đúng pattern đã chạy pass trong
`OnComboTreeNodeClicked` (dựng chip trước, highlight sau).

**Suy ra:** `RefreshComboFolderUI` (hàm khác, KHÔNG sửa trong đợt P1 này) có khả năng
mang CÙNG lỗi thứ tự — nhưng chưa lộ ra vì hàm này thường được gọi khi
`CurrentComboFolderPath` là `"__ALL__"`/`""` (`RefreshChipBreadcrumb` return sớm ở 2
trường hợp đó, không có chip để highlight sai). Nếu sau này có đường gọi
`RefreshComboFolderUI` với path sâu sẵn có (tương tự cách `StartReplaceComboMode` dùng),
bug tương tự sẽ lộ.

**Ceiling:** không sửa `RefreshComboFolderUI` trong đợt Replace UX Fix (ngoài scope, KP3).
**Trigger fix:** nếu phát hiện chip không highlight đúng ở đường gọi `RefreshComboFolderUI`
khác (VD sau Move/Rename combo với path sâu) → đảo thứ tự y hệt cách đã fix ở
`StartReplaceComboMode`.

Chi tiết đầy đủ P1.2 + P3.2: `Blueprints/BP_FurnitureInputManager.md` v2.7 mục
`StartReplaceComboMode`, `Plans/01-08-2026_ReplaceUX_Fix_Execution_Plan.md`.

---

## Replace UX Fix — P0→P5 HOÀN TẤT — 02/08/2026

Toàn bộ P0→P5 đóng. 6 bug gốc (#1, #3a, #3b, #4, #5, #6) rụng hết. Đường ngược (Luật 6A) đóng
đủ. Dead code `MeshToReplace` (single) đã xóa. Chi tiết đầy đủ node flow: `Widgets/
WBP_FurnitureInventory.md` v3.19, `Blueprints/BP_FurnitureInputManager.md` v2.8.

**[CORRECTION]** P1.1 — gap kiến trúc chip-builder combo (Phase0 §6.3) tự giải quyết bằng 2 hàm
có sẵn `RebuildChipRowForPath`/`RefreshChipBreadcrumb`, không cần hàm mới
`CreateComboChipTagsForPath` như Opus dự thảo. P1.2 build trên hướng này ngay từ đầu, không
cần rework.

**[BUG-FIX]** P2 — `OnMeshSelected` (`WBP_FurnitureInventory`) phản ứng nhầm với Broadcast
deselect rỗng (Primary=None) từ `DeselectAll()` (bước đệm bắt buộc trước `SelectActors()` theo
contract có sẵn, doc `BP_FurnitureInputManager.md` §SelectActors) → gọi `StartReplaceMode(mảng
rỗng)` → dead-end tại `IsValid(PrimarySelectedActor)`. Fix: thêm guard `IsValid(SelectedActor)`
đầu khối REPLACE trong `OnMeshSelected`, trước `ResolveSelectedComboRoot()`. Root cause xác nhận
bằng Print String tại 3 điểm (route branch, `PrimarySelectedActor` validity, `InventoryRef`
identity) — không phải doc-drift, không phải thứ tự node sai (2 giả thuyết trước đó bị bác bỏ
bằng K2Node export thật).

**[SCOPE]** Undo-giữa-replace (P4.3/P-2) chọn phương án (a): thoát Replace hẳn khi Undo (không
giữ mode + refresh theo actor restore). Lý do: undo thuộc lịch sử scene, không thuộc "phiên
Replace" — actor được restore có thể không còn liên quan gì đến target đang định thay, giữ
mode dễ tạo trạng thái UI lệch scene thật (kiểu Aliasing dự án hay gặp).

**[OBSERVATION]** P-1 — `ExitReplaceMode` chỉ SET `ReplaceTarget=None` + Regenerate 2 CTV,
không đụng tab/chiptag. Test thực tế (Case B, T4.1): thoát combo-replace không để lại trạng
thái kẹt/lỗi nào. Không sửa — khớp nguyên tắc "trạng thái browsing độc lập với Replace" (xem
thêm quan sát T4.3.1: tree/chiptag không tự đồng bộ theo selection khi NGOÀI Replace mode —
hành vi có sẵn từ trước, không phải bug, chấp nhận giữ nguyên).

**[CLEANUP]** P4.4 — xóa biến `MeshToReplace` (single, dead code) khỏi `BP_FurnitureInputManager`.
Chỉ còn 1 chỗ SET rác trong `BTN_Close` (`WBP_FurnitureInventory`), đã xóa cùng lúc lồng ghép
với P4.2. Compile sạch 0 error sau xóa — không có cross-class reference nào khác dùng biến
này. KHÔNG nhầm với `MeshesToReplace` (array, vẫn dùng thật, giữ nguyên).

**[SCOPE]** P5.1 (#2 chỉ báo Replace mode) — đẩy khỏi đợt Replace UX Fix, gộp vào Sprint 6
Polish UX (Feature-CanonicalStudioAngle, OBB dimension, C7 ComboDetailPopup). Lý do: kiểu chỉ
báo (KP1 — banner/đổi text nút/cả hai) chưa chốt, không chặn functionality — an toàn để dành
làm cùng đợt polish UX khác.

**[GHI CHÚ CLAUDE CODE, 02/08]** `WBP_ComboCard.md` v1.6 (30/07/2026, mục P3.1/`BTN_ChangeCombo`)
**đã ghi sẵn đúng logic gate** `Branch(ReplaceTarget==Combo)` trước khi đợt Replace UX Fix này
bắt đầu — trong khi Phase 0 Verify Report (01/08) lại xác nhận qua K2Node export rằng thời điểm
đó code THẬT là hardcode, không gate gì. Hai nguồn mâu thuẫn nhau về thời điểm 30/07→01/08.
Không tìm ra lý do chênh lệch (có thể doc v1.6 ghi từ ghi chú/dự định chưa merge thật, xem cảnh
báo nguồn ở đầu `WBP_ComboCard.md`). Vì nội dung SAU P3.1 (02/08) trùng khớp 100% với nội dung
ĐANG có trong doc — không sửa gì `WBP_ComboCard.md` (không có gì để đổi), chỉ ghi nhận nghi vấn
ở đây. Không chặn gì, không cần cuhoang quyết ngay — nêu để biết nếu sau này thấy `BTN_ChangeCombo`
cư xử khác mô tả.

---

## Q9 S-Matrix Gate + 3 bug Surface (deferred) — 02/08/2026

Nguồn: phiên bàn kiến trúc với Opus, phát hiện qua bug thật C9 Replace Combo (chọn mesh đơn
trong combo → Replace → Inventory không nhảy folder gốc). Luật Q9 mới:
`Rules/AI_Implementation_Rules.md` mục "Q9 — S-MATRIX GATE" (v2.14). 3 bug xác nhận tay:
`Bugs/Open_Bugs.md` (Bug-MaterialPrimaryOnly, Bug-PasteVerticalCollapse, Bug-StaleSurfaceType).

| Lệch | Ceiling | Upgrade trigger |
|---|---|---|
| Q9 chỉ có 1 trục thành hàng (trục A); B/C/D/E là câu hỏi trong X-Check | Bảng còn đọc được trong 1 màn hình | Có ≥3 ca miss liên tiếp cùng rơi vào 1 trục ẩn → nâng trục đó thành hàng riêng |
| 3 bug xác nhận 02/08 KHÔNG sửa ngay, dời sau Gate 2 | Gate 2 = packaged build chạy được, không đòi hoàn hảo | Bug-PasteVerticalCollapse gây mất dữ liệu người dùng thật (không chỉ sai vị trí) → kéo lên trước Gate 2 |
| Bug-MaterialPrimaryOnly vá tạm bằng toast, không sửa hành vi | Người dùng không bị lừa | Sprint 7 Material Edit multi-apply làm tới → gỡ toast, sửa thật |

---

## [DOC-DEBT đã đóng] PROGRESS.md P2 self-contradiction — 02/08/2026

**Phát hiện:** rà bar đếm Sprint 5 theo yêu cầu cuhoang, đối chiếu `docs/00_Core/PROGRESS.md`
dòng checklist P2 (Studio Thumbnail) với chính nó.

`PROGRESS.md` tự mâu thuẫn về trạng thái P2: dòng 281 (top-level `- [ ]`), dòng 292 (`P2.Gate D`
đánh dấu `[~]`) và dòng 307 (`Gate D — CHƯA đóng, còn treo case Cao`) đều nói P2 **CHƯA xong**,
trong khi dòng 314 (ngay trong mô tả `P2.Gate F`, cùng file) viết **"P2 HOÀN TẤT VỀ TÍNH NĂNG
(Gate A→F)"**. Gốc rễ: checklist chỉ có 2 trạng thái (`[x]`/`[ ]`, cộng `[~]` không định nghĩa rõ)
— không diễn tả được ca thực tế "tính năng đã chạy xong, chỉ còn 1 nhánh nghiệm thu phụ (case
Cao/Ceiling) chưa test bằng combo thật".

**Fix (quyết định cuhoang 02/08/2026):**
- P2 (Studio Thumbnail) = **DONE**. Case Cao (Ceiling, `P2.Gate D`) tách thành entry riêng
  `Bugs/Open_Bugs.md` mục "Task-P2-SweepCao" (🟢 Thấp, không chặn Gate 2), không giữ task Gate D
  mở nữa.
- Áp cùng luật cho P1 (Thumbnail System C++) — G0→G4 xong, chỉ G5 (VRAM regression) deferred →
  tick DONE, G5 tách entry riêng `Bugs/Open_Bugs.md` mục "Task-P1-VRAMRegression".
- Bar TỔNG QUAN Sprint 5: `16/22` → `18/22` (P2 + P1).
- Dòng mồ côi `"CHƯA bắt đầu."` (nằm lạc ngay sau mô tả `P2.Gate F`, dòng 316 cũ) — không xác
  định được thuộc mục nào (không khớp ngữ cảnh Gate F vừa mô tả xong, không khớp mục kế `C4`) →
  **XÓA**, không giữ lại phỏng đoán.
- Thiết lập luật mới **`R-DOC-DONE`** (`Rules/Execution_Discipline.md` v3.1) để chặn tái diễn:
  task tick `[x]` khi tính năng chạy xong, nghiệm thu/sweep/regression còn treo → tách
  `Open_Bugs.md`, không giữ checklist mở chờ.

**Trạng thái:** ✅ Đã đóng — `PROGRESS.md`, `Bugs/Open_Bugs.md`, `Rules/Execution_Discipline.md`
đã cập nhật cùng lượt.

---

## [DOC-DEBT] C3 gộp 3 việc — 02/08/2026

**Phát hiện:** VIỆC 5 quét lan (rà bar đếm Sprint 5) — mô tả checklist `C3` trong `PROGRESS.md`
gộp chung 1 ô `[ ]` cho 3 việc độc lập, trong đó 2 việc thực ra đã xong ở chỗ khác.

**Lệch:** ô checklist `C3` ("Save dialog + gộp P4 LOCALAPPDATA + móc capture thumbnail sau
`SaveComboFromSelection`") gộp 3 việc độc lập → 2 xong (Save dialog qua C3b; móc capture
thumbnail qua P2 Gate F 21/07), 1 chưa (P4 — path LOCALAPPDATA) — không diễn tả được bằng 1 ô
`[ ]`/`[x]` duy nhất.

**Quyết định cuhoang:** KHÔNG tick, KHÔNG tách C3 thành nhiều ô ngay (tách = đổi mẫu số Sprint 5,
phải recount toàn bộ). Chỉ sửa TEXT mô tả ghi rõ từng phần (ĐÃ XONG / CHƯA LÀM) để hết overlap
gây hiểu nhầm.

**Ceiling:** mô tả text đã ghi rõ từng phần, đủ để không hiểu nhầm trong Sprint 5.
**Upgrade trigger:** sang Sprint 6 → tách `C3` thành các ô riêng khi recount mẫu số đầu sprint.

**Trạng thái:** ✅ Đã đóng (text-only fix) — xem `PROGRESS.md` dòng `C3`. Kèm luật mới
`R-DOC-ATOMIC` (`Rules/Execution_Discipline.md`) để chặn tái diễn ô gộp nhiều việc.

---

## [DOC-DEBT] AS-BUILT lẫn trong Plans/Sprints — 02/08/2026

**Phát hiện:** VIỆC 3 quét lan (Lô B, đóng dấu HISTORICAL) — 6 file mang tên "Plan"/"Task Card"
trong `Plans/` và `Sprints/` bị ghi thẳng kết quả thực thi thật (test PASS, K2Node export,
changelog per-gate) vào thân file, thay vì đưa về doc canonical trong `Blueprints/`/`Widgets/`.

**Lệch:** kết quả thực thi được ghi thẳng vào file plan → as-built nằm rải rác trong file mang
tên "Plan", trong khi doc canonical trong `Blueprints/` có thể cũ hơn hoặc thiếu chi tiết đó.

**Ceiling:** 6 file đã đánh dấu banner `📌 [CHỨA AS-BUILT]` (xem `MERGE_LOG.md` mục "AS-BUILT
lẫn trong Plans/Sprints — 02/08/2026"), đủ để không bỏ sót khi đọc.

**Upgrade trigger:** sau Gate 2 → gom phần as-built về doc canonical tương ứng, hoặc lập thư mục
riêng cho execution report, tách khỏi `Plans/`.

**Trạng thái:** ✅ Đã đóng (banner-only fix) — không di chuyển/đổi tên file (quyết định cuhoang,
tránh gãy đường dẫn chéo giữa lúc chuẩn bị Lô C + Save As). Kèm luật mới `R-DOC-ASBUILT`
(`Rules/Execution_Discipline.md`).

---

## [DOC-DRIFT] ResolveSelectedComboRoot — PrimarySelectedActor vs SelectedActors[0] — 02/08/2026

**Phát hiện:** viết doc `ResolveSelectedComboRoot()` vào `BP_FurnitureInputManager.md` (Lô D,
nguồn K2Node export thật cuhoang cung cấp 02/08/2026).

**Lệch:** `Plans/24-07-2026_C9_Execution_Plan.md` mục V7 ghi hàm `ResolveSelectedComboRoot`
*"dùng `PrimarySelectedActor`"*; as-built thật (K2Node export 02/08/2026) dùng
`SelectedActors[0]` (`Cast SelectedActors[0] → BP_FurnitureActor`). Hai giá trị này **khác nhau
khi selection là multi** — `ToggleActor` SET `PrimarySelectedActor` = actor vừa được thêm/click
gần nhất, còn `SelectedActors[0]` = actor được thêm ĐẦU TIÊN vào mảng (thứ tự khác nhau tùy cách
user Ctrl-click).

**Ceiling:** chưa gây lỗi trong C9 — Replace Combo hiện chỉ chạy với selection = 1 cụm combo
(mọi actor trong cụm cùng `GroupID` → `GetGroupRoot` ra cùng 1 kết quả bất kể lấy phần tử nào
của mảng), nên `PrimarySelectedActor` và `SelectedActors[0]` cho cùng kết quả trong mọi test case
C9 đã chạy.

**Upgrade trigger:** khi lên task card **Save As/Save đè** — tính năng này phải xử lý selection
MIX (combo + mesh rời lẫn nhau), lúc đó `PrimarySelectedActor` và `SelectedActors[0]` có thể trỏ
tới 2 actor khác hẳn nhau (1 trong combo, 1 mesh rời) → hành vi resolve combo root sẽ khác nhau
tùy chọn dùng biến nào. **CHƯA QUYẾT hành vi đúng cho case mix — không tự chọn, phải chốt lúc lên
task card Save As/Save đè.**

**KHÔNG sửa** `Plans/24-07-2026_C9_Execution_Plan.md` mục V7 — file đã đóng dấu `📌 [CHỨA
AS-BUILT]` (Lô B), sửa nội dung sẽ làm mất dấu vết quyết định/mô tả gốc lúc C9 được build. Ghi
nhận drift ở đây + trong `BP_FurnitureInputManager.md` (mục `ResolveSelectedComboRoot`) thay vì
sửa nguồn.

**Trạng thái:** ✅ ĐÃ QUYẾT 03/08/2026 — Save As/Save đè KHÔNG dùng biến nào trong 2 biến này. Cả hai đều
lấy MỘT actor rồi leo lên → kết quả phụ thuộc thứ tự Ctrl-click. Tính năng mới dùng hàm
riêng `ResolveActiveComboForSave()` quét TOÀN BỘ SelectedActors, đếm số combo root khác
nhau. `ResolveSelectedComboRoot()` giữ nguyên, KHÔNG sửa (KP3 — C9 vừa test PASS 30/07).
Xem `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 2.8.

---

## [CEILING] Hai nơi cùng biết cách leo combo root — 03/08/2026

**Lệch:** T1 tạo `GetComboRootOfActor()` làm hàm nguyên thủy, nhưng KHÔNG đấu lại
`ResolveSelectedComboRoot()` (C9) vào nó → 2 nơi cùng biết cách leo combo root.

**Vì sao:** `ResolveSelectedComboRoot` nằm giữa đường Replace vừa test PASS 02/08; sửa lúc
này kéo theo regression C9 giữa lúc làm tính năng khác.

**Ceiling:** chấp nhận tới hết đợt Save As/Save đè.

**Trigger:** C10 (regression full) — đấu lại + chạy 5 case C9 (bộ test đã bật sẵn, chi phí
thêm ~0). Hoặc SỚM HƠN nếu có bất kỳ thay đổi nào về cách xác định combo root.

---

## [DOC-DEBT] GetGroupRoot chưa từng có doc — phát hiện 03/08/2026

Hàm dùng ở 6+ chỗ nhưng chưa có mục doc riêng ở bất kỳ file nào — chỉ được nhắc tên trong
flow của hàm khác. K2Node export 03/08 lộ 3 hành vi chưa ai ghi:
- (1) cap 10 tầng (ForLoop LastIndex=9), vượt → trả nửa chừng, KHÔNG báo lỗi;
- (2) không tìm thấy group → trả lại CHÍNH GID truyền vào, KHÔNG trả "";
- (3) vòng cha-con quẩn (A→B→A) không bị phát hiện.

Cả 3 không chặn T1. KHÔNG sửa hàm (KP3).

**Trigger:** (1) và (3) nâng lên bug thật nếu combo lồng vượt 3 tầng được cho phép.

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

---

## Lịch sử cập nhật

| Ngày | Nội dung |
|------|----------|
| 19/06/2026 | Thêm section "SPRINT D — 19/06/2026": 4 dòng VRAM Fixes + Async Load. Thêm dòng S5.T2 BP_ComboManager tách riêng khỏi InputManager |
| 21/06/2026 | Thêm section "SPRINT 5 — 21/06/2026": 4 dòng kiến trúc Combo v2.0 (C0 nested fix, drag-drop→cursor, materialOverrides→RowName, SourceComboID group cha) + 1 dòng patch review v2.1 |
| 23/06/2026 | Thêm section "SPRINT 5 — 23/06/2026": 9 dòng quyết định Sprint5_Plan_v1.1 (P1 thumbnail C++ thật, P2 surface-snap khối, P3 xoay combo, P5 dời Sprint7, K1 WBP_Toast, K3 bAddToRecent, K5 cả 2 hướng export, P4 lưu LOCALAPPDATA, scope chia 3 giai đoạn) |
| 24/06/2026 | Thêm section "SPRINT 5 — 24/06/2026": C8 MERGED vào C4; On Drop combo KHÔNG trace (ghost location); CalculateComboAnchor fix anchor z; ghost offset BUG OPEN |
| 25/06/2026 | Thêm section "SPRINT 5 — 25/06/2026": C5 scope mở rộng full folder management; D1-D5 (dedup exact/signature/Set List Items/cột chung/class var); quyết định kiến trúc C5. Round 3: thêm D6-D8 (tree 2 cấp, OnComboTreeNodeClicked rewrite, OnComboChipTagClicked new). |
| 26/06/2026 | Thêm section "SPRINT 5 — 26/06/2026": D9 Branch guard cấp 2 (UX + bug Loop Body/Completed); D10 bug guard position; D11 WBP_LibraryContextMenu clone Btn_Background thay Menu Anchor; D12 Canvas Panel Z-order. |
| 27/06/2026 | Thêm section "SPRINT 5 — 27/06/2026 — C5.2 Inline Rename Folder": D13 WBP_EditableLabel component inline (thay dialog popup); D14 validate live OnTextChanged; D15 click ngoài = revert; D16 folder ops KHÔNG vào Undo. |
| 30/06/2026 | Thêm section "SPRINT 5 — 30/06/2026 — C5.4 Move Folder": D-C5.4-1 Array_Append ngược TargetArray/SourceArray trong CollectFolderTargets (kết quả đệ quy không tích lũy được); D-C5.4-2 dead-end thiếu merge nhánh True trong HandleMoveFolderConfirmed (bug CHỈ lộ khi đang xem đúng folder bị move). Thêm note Learning_System: quy trình dạy học bị bỏ qua giai đoạn deadline-rush 21/06→30/06, đã khôi phục trong v1.2. |
| 01/07/2026 | Thêm section "SPRINT 5 — 01/07/2026 — C5.5 Move Combo": D-C5.5-1 ParseIntoArray delimiter mismatch "," vs ", " (nhiều tên con gộp 1 node); D-C5.5-2 Map_Contains sai với leaf folder (không là key trong ComboFolderTree → fallback sai __ALL__); D-C5.5-3 thiếu UpdateComboFolderHighlights call sau RefreshComboFolderUI (highlight không sync sau Move Combo). |
| 04/07/2026 | Thêm section "SPRINT 5 — 04/07/2026 — NF (New Folder, context-menu part)": D-NF-1 dialog (NF.G2-G5 gốc) → SUPERSEDED bởi inline rename (UX Explorer-style, tái dùng WBP_EditableLabel C5.2); D-NF-2 right-click tạo CÙNG CẤP (sibling) node bị click, không phải CON (lý do: sibling luôn render trên tree 2 cấp → rename mode luôn tìm thấy node); D-NF-3 không cần dispatcher riêng trên WBP_LibraryContextMenu — CB_CreateNewFolder gọi thẳng Custom Event trong WBP_FurnitureInventory. |
| 06/07/2026 | Thêm section "SPRINT 5 — 06/07/2026 — NF.G3 + C5.6 + C5.7a": D-C5.6-1 HandleDeleteFolderConfirmed nhảy về folder CHA thay vì `__ALL__` sau xóa; bug fix RefreshComboFolderUI 2/3 nhánh dead-end trước RefreshChipBreadcrumb (hàm mới); bug fix RefreshChipBreadcrumb delimiter gõ nhầm "/ " thay vì "/" (kèm BooleanAND→OR vô hại). |
| 08/07/2026 | Thêm section "SPRINT 5 — 08/07/2026 — C5.8 Task Card #1 (Data Layer)": [RENAME] `S_FolderTargetEntry`→`S_FolderTreeNode` (Depth thay IndentLevel, +4 field mới cho guide line picker); [ARCH] tên wrapper đổi khác plan gốc `BuildFolderTree`→`BuildComboFolderTreeNodes` (trùng tên hàm cũ Material/Furniture catalog) + hàm phụ `GetFilteredChildren` mới. |
| 04/07/2026 | Thêm quy ước ceiling + trigger cho deviation loại shortcut có chủ đích (mục CÁCH DÙNG) — từ ponytail-debt |
| 11/07/2026 | Thêm section "SPRINT 5 — 11/07/2026 — C5.8 Task Card #2 Part B lần 1 (as-built)": [ARCH] ExpandedFolders Array thay Set; [SWAP] ETB_Search→SB_SearchFolder; [DOC-FIX] as-built dùng Custom Event trung gian HandleArrowClicked/HandleNameClicked (sửa dòng TIẾN ĐỘ sai trong task card); [LESSON] SetFolders giữ thân cũ 2a khi build Part B — quy tắc đề xuất diff thân cũ trước khi sửa function có sẵn. |
| 11/07/2026 13:14 | Thêm section "SPRINT 5 — 11/07/2026 (tiếp) — C5.8 Task Card #2 Part B, Giai đoạn 1": [BUG-FIX] `SetNode` thiếu `SET RowNode = Node` (root cause bug #2); [BUG-FIX] `BTN_Arrow` không đồng bộ Visibility với `TXT_Arrow`; [DOC-FIX] FixPlan v1.1 đính chính SAI về Custom Event trung gian — export K2Node thật xác nhận nối THẲNG (đảo ngược lại entry [DOC-FIX] 11/07/2026 trước đó). |
| 12/07/2026 10:40 | Thêm section "SPRINT 5 — 12/07/2026 — C5.8 Task Card #2 Giai đoạn 2+3": [BUG] `PathMatchesQuery` dùng nhầm `node.Path` thay vì `node.DisplayLabel` (substring match nhầm con); [ARCH] `CurrentSearchFolder` đổi Local→Class Variable (`Get Initial Text` trả rỗng); [BUG] arrow-click trong lúc search không lộ con — thêm `GetParentPath` + điều kiện `bShow` + bỏ hardcode `SetExpanded`; [ARCH] `GetParentPath` function mới ngoài plan gốc; [SCOPE] Select (mục 10) không cần sửa gì, chỉ verify. |
| 12/07/2026 15:30 | Thêm dòng vào section "SPRINT 5 — 12/07/2026 — C5.8 Task Card #2 Giai đoạn 2+3": [SCOPE] Bỏ Print debug gate bằng `bDebugMode` (FixPlan mục 1) — dùng breakpoint/watch pin (UE5 built-in) thay thế, thêm biến+Branch riêng cho từng Print là thừa so với lợi ích ở quy mô hiện tại. |
| 13/07/2026 | Thêm section "SPRINT 5 — 13/07/2026 — C5.8 2d (rename host) + Wire Move + Wire Save": 8 entry (2 [BUG-FIX] BuildMoveFolderTargetList sót call site + SetSelectedHighlight sai biến, 1 [CORRECTION] SetLabelColor Slate Color, 3 [SCOPE] rename context-menu không tồn tại/test TC#2 SUPERSEDED/6A Create Folder chấp nhận, 1 [CEILING] Bind OnFolderSelected 1 lần/instance, 1 [CLEANUP] Print debug DevelopmentOnly). |
| 13/07/2026 (REG) | Thêm section "SPRINT 5 — 13/07/2026 (REG) — C5.8 Chốt sổ (Khối A/B/C/D)": [CLARIFICATION] A1 REG Task Card mô tả nhầm case Move Folder/Move Combo (không sửa code, chỉ đính chính wording); [SCOPE] Save dialog không live-sync sang cây inventory đang mở phía sau (đúng thiết kế, không phải bug). REG PASS toàn bộ Khối A/B/C, D5 comprehension check PASS — **C5.8 CHÍNH THỨC DONE**, mở khóa C9. |
| 14/07/2026 | Thêm section "SPRINT 5 — 14/07/2026 — P1 Combo Thumbnail: đổi kiến trúc capture": [ARCH] one-shot `CaptureComboThumbnail` (plan gốc G0) loại bỏ do ảnh xám phẳng (Lumen/TAA/auto-exposure chưa hội tụ qua đủ frame) — đổi sang cặp `BeginComboCapture`/`FinishComboCapture` bọc bởi Custom Event dùng `Delay` latent (L8). Hàm cũ giữ `[LEGACY]`, không xóa. `.h` bị đụng lần 2 (chấp nhận, đổi kiến trúc là ngoại lệ). |
| 15/07/2026 | Thêm section "SPRINT 5 — 15/07/2026 — P1 G2/G3/G4: bug dead-end Return Node + wiring": [BUG-FIX, NGHIÊM TRỌNG] `GetComboThumbnail` thiếu Return Node ở nhánh False → cross-combo thumbnail bleeding (đọc lại rule L2 — ngoại lệ "dead-end vô hại" KHÔNG áp dụng cho Function có return type); [BUG-FIX] 2 dead-end trong SaveComboFromSelection Bước 7 (Pivot not-found + bSaveOK fail); [BACKLOG] dead-end ComboManagerRef trong LoadComboLibrary chưa fix; [CORRECTION] Delete combo KHÔNG PHẢI = C8 (C8 = Drag-drop/surface-snap); [ARCH] exposure bug retry lần 2 vẫn fail, xác nhận không phải warm-up issue. |
| 15/07/2026 (G5 + reconcile) | P1 Gate G5 (regression VRAM) DEFERRED — phương pháp đo (stat rhi lỗi, MemReport nhiễu bởi texture streaming theo camera) không tách được đóng góp riêng của combo thumbnail; cần RenderDoc/Nsight. Không chặn P1 (coi DONE về tính năng, G0→G4). Cập nhật mục "[BACKLOG — chưa fix] Dead-end ComboManagerRef" ở trên → FIXED 15/07/2026 (xác nhận cuhoang: fix trực tiếp trong UE5 Editor, ngoài phiên Claude Code). |
| 16/07/2026 | Thêm section "P2 — 16/07/2026 — Quyết định kiến trúc Studio Thumbnail": [ARCH] S8 isolation → Remote Studio (duyệt 16/07); [ARCH] exposure bug deferred GỘP vào P2 Gate C (Manual EV100 thay Auto-exposure lock); [SCOPE] SpawnComboByID không tái dùng cho thumbnail (5 side effects xác nhận qua trace K2Node) → Custom Event mới SpawnComboForThumbnail; [CLEANUP backlog] node Delay mồ côi trong SpawnComboByID Step D, dọn khi có dịp. Plan đầy đủ: `docs/Plans/P2_StudioThumbnail_Execution.md` v1.0. |
| 17/07/2026 | Thêm section "P2 — 17/07/2026 — Gate A DONE: Delay ceiling + bug fix aliasing": [SCOPE] Delay(0.5)→Delay(3.0) hardcode trong SpawnComboForThumbnail (LoadMeshAsync chưa kịp với combo nhiều món), ceiling = combo 7-8 món/asset resident, trigger = trước Gate F thay bằng dispatcher OnMeshLoaded (quyết định cần Fable/Opus); [BUG-FIX] Add Actor World Offset dùng nhầm Array Element của Loop 1 (qua Knot reroute) thay vì Loop 2 trong chuỗi ground-align — 1 actor bị dịch chuyển cộng dồn, còn lại đứng yên. Gate A: TEST PASS 6/7 case (case 7 dời Gate F). |
| 17/07/2026 (cuối phiên) | Thêm section "P2 — 17/07/2026 (cuối phiên) — Gate B + Gate C DONE": Gate B [ARCH] Cast Shadow=False trên dome (quyết định quan trọng nhất, gỡ ràng buộc "đèn phải trong dome") + [SCOPE] màu dome S1 dời tối ưu cuối + [BACKLOG] faceting sphere chưa xác nhận. Gate C — 12 bug/quyết định trong `SpawnStudioLight` (Key/Fill RectLight): [BUG-FIX] InVect.X 150→1500, Mobility Stationary→Movable, Attenuation Radius 4000→8000, `bUseFixedAngle` chưa tick, `Make`→`Get/Set members in` Post Process Settings (tránh xoá Lumen override C++), thiếu IsValid(Cmb_CaptureHandle) guard; [ARCH] Cmb_StudioAnchor Default Value (0,0,0)→(500000,500000,0), HeightOffset 250→1500 (elevation 45°), đề xuất Directional Light bị Fable bác bỏ; [CORRECTION] nhầm cộng +DomeRadius vào Z đèn; [LESSON] 3-lần-sai-cùng-chỗ→STOP-hỏi-Fable bị áp dụng trễ. Verify PASS: 2 combo khác nhau → cùng góc + cùng độ sáng. |
| 18/07/2026 | Thêm section "P2 — 18/07/2026 — Gate D prerequisite: lighting isolation": [CORRECTION] RectLight offset Z thật = 1200 (không phải 1500 như ghi trước) + tính lại khoảng cách đèn→tâm dome (~1700 < Radius 2000, đèn nằm TRONG dome, loại giả thuyết "đèn ngoài bán kính"); [BUG-FIX] Distance Field khối đặc của Sphere engine tự triệt tiêu RectLight khi Cast Shadow=True → fix bằng `SM_StudioDome` (duplicate asset riêng) + Two-Sided Distance Field Generation; [ARCH] `Set Lighting Channels` cô lập dome+đèn+furniture clone khỏi Sun/UDS (Channel 1, yêu cầu Mobility=Movable); [ARCH] `Set Show Flag Settings(SkyLighting=False)` trên Capture Component riêng — không đụng biến LightManager của đồng nghiệp; [CEILING/SUY LUẬN chưa verify] dải đen viền khung hình, dời xử lý sang đúng task Gate D. Task gốc Gate D (Source Size Key tune + sweep 5 combo) CHƯA bắt đầu. |
| 19/07/2026 | Thêm section "SPRINT 5 — 19/07/2026 — P2 Noise + Aliasing Fix": [ARCH] mượn Event Tick của BP_ComboManager cho temporal accumulation (N=24 frame) thay vì subclass SceneCapture2D/FTickableGameObject — buffer `TMap<ASceneCapture2D*, FComboAccumState>` file-scope static, không lên Blueprint; [ARCH] cộng dồn temporal + downscale SSAA 2× đều ở không gian linear color, encode FColor đúng 1 lần cuối (tránh lệch sáng do gamma không cộng tuyến tính); [BUG-FIX] sửa nhầm `CreateRenderTarget2D` bản LEGACY thay vì bản thật khi áp SSAA factor (build pass nhưng ảnh sai kích thước) — bài học: 2 hàm cùng signature cần phân biệt qua field khác (`bCaptureEveryFrame`), không suy luận theo vị trí trong file. Test: noise CONFIRM, aliasing/SSAA CONFIRM DONE (cuhoang tự chạy lại checklist đầy đủ). Gán vào Gate D (tiếp nối prerequisite 18/07). |
| 20/07/2026 | Thêm section "P2 — 20/07/2026 — Gate D: Rim Light + VRAM Fix + Source Size chốt + 2 bug kiến trúc mới (OPEN)": [SCOPE] Rim Light 3-point lighting (`Cmb_StudioRimLight` mới) + đổi InVect/SourceSize/AttenRadius cả 3 đèn + Exposure Compensation +6.0; [BUG-FIX] ×2 VRAM/GPU crash EndPlay `BP_ComboManager` (`Map_Clear` lồng sai nhánh Branch + thứ tự đọc/ghi `Cmb_CaptureHandle` khiến `ResetComboAccumulation` no-op); [CORRECTION] `Cmb_KeySourceSize`=500 chốt bằng mắt; [ARCH — OPEN] bug #1 dome cong nuốt chân đồ footprint rộng (đảo ngược 1 phần Gate B, 3 phương án chờ Fable/Opus quyết); [ARCH — OPEN] bug #2 combo Ceiling dính lỗi ground-align giống Tường (H1), chưa từng ghi trong plan — đề xuất gộp quyết định cùng H1. Gate D sweep TẠM DỪNG chờ hướng đi kiến trúc. 2 bug mới ghi `Bugs/Open_Bugs.md`. |
| 20/07/2026 (Nấc 1) | Thêm section "P2 — 20/07/2026 (Nấc 1) — Surface-Aware Ground-Align, Bug-CeilingGroundAlign FIXED": [ARCH] Function mới `ResolveThumbAlign(Clones) → DeltaZ, Category` thay khối align inline đơn nhất, phân loại Floor/Ceiling/Wall/Other theo `PlacementSurfaceType`; [SCOPE] chốt ranh giới Nấc 1 (surface-aware align) vs Nấc 2 (rig-trần below-front, backlog); [ARCH — mở rộng ngoài scope, KP2 duyệt] Wall-priority rule (so `FloorMinZ`/`WallMinZ`, phát hiện qua test combo bàn thờ thật) + margin fix (đáy non-Floor nổi trên Anchor.Z +10, không center); [DỌN] xóa `Cmb_ThumbMinZ` dead var. Test 6/6 case PASS. Bug-CeilingGroundAlign đóng — Bug-DomeCurvature vẫn Open (đồng nghiệp dựng dome custom riêng), độc lập với Nấc 1. |
| 20/07/2026 (Dome Custom) | Thêm 2 section: "P2 — 20/07/2026 (Dome Custom) — Bug-DomeCurvature FIXED, Sweep 4/5 Loại" — [ARCH] dome custom (cylinder kín, đáy bo cong, ~500 unit vùng phẳng) thay `/Engine/BasicShapes/Sphere` (đảo ngược Gate B); [ARCH — đảo ngược Gate B] Cast Shadow=True verify an toàn trên dome mới (khác sphere cũ). Test PASS combo Dẹt (thảm) + To (sofa 15 món, worst-case footprint). "P2 — 20/07/2026 (Sweep 5 Loại)" — [SCOPE] 4/5 loại (Nhỏ/To/Dẹt/Tường) PASS chính thức; case Cao PASS sơ bộ bằng stack dựng tay (không phải combo tự nhiên) — quyết định Lựa chọn B: giữ làm bằng chứng sơ bộ, chờ combo kệ/tủ cao thật để đóng hẳn, không chặn việc khác. Bug-DomeCurvature cập nhật đồng thời `Bugs/Open_Bugs.md`. |
| 20/07/2026 (Gate E) | Thêm section "P2 — 20/07/2026 (Gate E) — Depth of Field DONE": mở rộng node "Set members in Post Process Settings" sẵn có (Gate C) thêm Focal Distance + Aperture (F-stop), không tạo node mới; [VERIFY] plan gốc sai giả định — biến `Distance` C++ không xuất Blueprint, xấp xỉ bằng `Vector Distance(CaptureHandle, Cmb_StudioAnchor)`; Aperture=2.8 chốt sau test đối chứng f/1.0 (xác nhận pipeline chạy đúng, combo hiện có Z-spread nông nên f/2.8 blur khó thấy — đúng vật lý, không phải bug), khớp gu ảnh tham chiếu IKEA. Gate E DONE — tiếp theo Gate F (nối dây thật + closure). |
| 21/07/2026 (Gate F) | Thêm section "P2 — 21/07/2026 — Gate F: nối Save flow thật + fix framing rotation-invariant": [ARCH] Radius bounding rotation-invariant (`max(Dist(actor→Center)+BoundsExtent.Size())` thay `Bounds.GetExtent().Size()` AABB) — zoom lệch ~20% giữa các góc xoay giảm còn ~6%; [ARCH] Broadcast dời từ Bước 7 sang Event Tick tail (bắt buộc do pipeline async N=24, không phải lựa chọn); [CORRECTION] FixedAngle.Yaw thật = 55 (không phải 0 như doc cũ), promote thành `Cmb_StudioCamYaw`; [BUG tự đóng] Save thật từng ra ảnh 2048² thô do không qua accumulate — Gate F chuyển qua đúng pipeline Studio nên tự hết. Node flow đầy đủ: `BP_ComboManager.md` v1.10, `Blueprint_Logic_NodeFlow.md`. |
| 30/07/2026 | Thêm section "C9 Replace — 30/07/2026 — Folder Highlight Fix + C9.b–C9.f": 3 [BUG-FIX] (Folder Highlight ăn nhầm full path; Bug A2 OnMeshSelected nhảy tree Furniture giữa combo replace; Bug B EnterReplaceMode thiếu SET CurrentInventoryMode + visibility CTV + UpdateTabHighlight — bổ sung 31/07, sót lần merge trước); 1 [OPEN] chưa verify (StartReplaceMode nhánh DA legacy, format MeshFolderPath); 1 [CLEANUP] chốt normalize path tại Split.RightS; 1 [CEILING] Split hardcode "Object_Model/"; 1 [SCOPE] FilterComboByFolder build 2 lần/frame trong StartReplaceComboMode; 1 [PLAN-SAI] Cmb_ReplaceCenter→Cmb_ReplaceAnchor (CalculateCenter→CalculateComboAnchor, fix anchor-vs-center mismatch). |
| 22/07/2026 (C6) | Thêm section "C6 — 22/07/2026 — Favorite + Recent combo DONE + 2 bug fix": [BUG-FIX] `AddRecentCombo` — `SaveUserPrefs` dead-end trong nhánh `False` của `Branch(RecentComboIDs.Length > 48)` (chỉ save khi vượt cap, mọi test thực tế <48 không bao giờ ghi đĩa) — merge cả 2 nhánh; cap thật=48 không phải 20 (`UX_Phase2_Plan.md` sai); [BUG-FIX] Recent hiển thị chỉ 1 card — `FilterByCategory` đổi `AddItem` loop → `Set List Items` batch, bài học ghi skill `ue5-blueprint-rules` L12; [OBSERVATION] duplicate `comboId` khi copy tay JSON — không phải bug, backlog cho Save As/Save đè. File mới: `Blueprints/BP_FurnitureUserPrefsManager.md`. |
| 01/08/2026 (Replace UX Fix P1.2) | Thêm section "Replace UX Fix — P1.2 (01/08/2026) — Lỗi thứ tự tiềm ẩn trong RefreshComboFolderUI": phát hiện lúc implement fix #3b — đặt `RefreshChipBreadcrumb()` SAU `UpdateComboFolderHighlights()` (đúng thứ tự tài liệu ghi cho `RefreshComboFolderUI`) khiến chip mới dựng không được highlight; sửa bằng ĐẢO NGƯỢC thứ tự trong `StartReplaceComboMode`. Suy ra `RefreshComboFolderUI` (không sửa trong đợt này) có khả năng mang cùng lỗi thứ tự nhưng chưa lộ — ghi ceiling/trigger, không tự sửa (KP3). |
| 02/08/2026 (Replace UX Fix P0→P5) | Thêm section "Replace UX Fix — P0→P5 HOÀN TẤT — 02/08/2026": 6 bug gốc rụng hết (#1/#3a/#3b/#4/#5/#6). [CORRECTION] P1.1 gap tự giải quyết, không cần hàm mới `CreateComboChipTagsForPath`. [BUG-FIX] P2 root cause thật = thiếu guard `IsValid(SelectedActor)` trong `OnMeshSelected` (2 giả thuyết trước bị bác bỏ bằng K2Node export). [SCOPE] Undo-giữa-replace chọn (a) thoát hẳn. [OBSERVATION] P-1 `ExitReplaceMode` không đụng tab/chiptag — chấp nhận, không phải bug. [CLEANUP] P4.4 xóa hẳn `MeshToReplace` (single) — đính chính luôn dòng Variables `BP_FurnitureInputManager.md` ghi sai "đã xóa từ v1.6". [SCOPE] P5.1 dời Sprint 6, P5.2 gác (thiếu file test). [GHI CHÚ] phát hiện `WBP_ComboCard.md` v1.6 đã có sẵn logic gate `BTN_ChangeCombo` đúng TRƯỚC khi P3.1 chạy — mâu thuẫn với Phase0 Verify Report (01/08) báo hardcode — không sửa gì (nội dung sau P3.1 trùng khớp), chỉ ghi nhận nghi vấn. |
| 02/08/2026 (Q9 + 3 bug Surface) | Thêm section "Q9 S-Matrix Gate + 3 bug Surface (deferred) — 02/08/2026": luật Q9 mới trong `Rules/AI_Implementation_Rules.md` v2.14 (S-Scan 10 trạng thái + X-Check 10 hệ thống), phát hiện qua bug thật C9 Replace Combo (thiếu ca sử dụng, không phải bug code). 3 bug xác nhận tay ghi vào `Bugs/Open_Bugs.md`: Bug-MaterialPrimaryOnly, Bug-PasteVerticalCollapse, Bug-StaleSurfaceType — cả 3 dời sau Gate 2, kèm bảng ceiling/trigger. |
| 02/08/2026 (DOC-DEBT P2) | Thêm section "[DOC-DEBT đã đóng] PROGRESS.md P2 self-contradiction — 02/08/2026": PROGRESS.md tự mâu thuẫn về trạng thái P2 (dòng checklist Gate D/sub-item vs dòng "P2 HOÀN TẤT VỀ TÍNH NĂNG" cùng file) — do checklist không diễn tả được "xong tính năng, treo nghiệm thu phụ". Fix: quyết định cuhoang P2=DONE + P1=DONE (cùng lý do), tách case Cao + G5 VRAM ra `Bugs/Open_Bugs.md`, xóa dòng mồ côi "CHƯA bắt đầu.", thiết lập luật mới `R-DOC-DONE` (`Rules/Execution_Discipline.md` v3.1). |
| 02/08/2026 (DOC-DEBT C3) | Thêm section "[DOC-DEBT] C3 gộp 3 việc — 02/08/2026": ô checklist `C3` gộp 3 việc độc lập (Save dialog/móc capture thumbnail/P4 LOCALAPPDATA) — 2 xong 1 chưa, không diễn tả được bằng 1 ô. Quyết định cuhoang: KHÔNG tick, KHÔNG tách giữa sprint — chỉ sửa text mô tả rõ từng phần. Ceiling: text đủ rõ cho Sprint 5. Trigger: tách C3 thành ô riêng khi recount đầu Sprint 6. Thêm luật mới `R-DOC-ATOMIC` (`Rules/Execution_Discipline.md` v3.2). |
| 02/08/2026 (DOC-DEBT AS-BUILT) | Thêm section "[DOC-DEBT] AS-BUILT lẫn trong Plans/Sprints — 02/08/2026": 6 file "Plan"/"Task Card" bị ghi thẳng kết quả thực thi thật (test PASS/K2Node export/changelog per-gate) vào thân, doc canonical `Blueprints/`/`Widgets/` có thể cũ hơn. Quyết định cuhoang: KHÔNG di chuyển/đổi tên — chỉ đóng dấu banner `📌 [CHỨA AS-BUILT]` (xem `MERGE_LOG.md`). Trigger: gom về canonical hoặc tách thư mục riêng sau Gate 2. Thêm luật mới `R-DOC-ASBUILT` (`Rules/Execution_Discipline.md` v3.3). |
| 02/08/2026 (Lô D) | **Viết doc `ResolveSelectedComboRoot()` vào `BP_FurnitureInputManager.md`** (nguồn K2Node export thật cuhoang cung cấp — đóng MỤC 4 CrossCheck). Thêm section "[DOC-DRIFT] ResolveSelectedComboRoot — PrimarySelectedActor vs SelectedActors[0] — 02/08/2026": `Plans/24-07-2026_C9_Execution_Plan.md` §V7 ghi dùng `PrimarySelectedActor`, as-built thật dùng `SelectedActors[0]` — khác nhau khi selection multi. Chưa gây lỗi (C9 chỉ chạy selection 1 cụm) — ceiling giữ tới khi lên task card Save As/Save đè (phải xử lý selection mix). KHÔNG sửa file Plans (đã đóng dấu [CHỨA AS-BUILT]). Đóng thêm MERGE_LOG Q3 (`FindGroupData` không có Index) — sửa 3 file: `BP_FurnitureInputManager.md` v2.9, `BP_UndoManager.md` v1.13, `Blueprint_Logic_NodeFlow.md` v1.15 (đều tự mâu thuẫn nội bộ trước đó). |
