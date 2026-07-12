# DEVIATIONS — Lệch khỏi plan gốc (plan_v3)
**HỢP NHẤT TỪ 3 file:** 07-06_DEVIATIONS.md (Sprint 1+2) + DEVIATIONS.md (12/06, Sprint 3+4) + Sprint4BugFix_additions.md (15/06)
**Cập nhật:** 11/07/2026 13:14

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
