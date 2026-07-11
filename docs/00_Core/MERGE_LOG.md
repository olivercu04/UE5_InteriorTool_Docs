# MERGE LOG — UE5 InteriorTool Docs
**Mục đích:** Reviewer chỉ cần đọc file này để biết file nào cần soi kỹ.
**Cập nhật:** 11/07/2026 13:14

---

## Cách đọc bảng coverage
- **GIỮ** = không đổi từ BASE
- **SỬA(patch)** = patch thay thế/mở rộng nội dung BASE
- **XÓA(patch)** = patch xóa hẳn mục này
- **MỚI(patch)** = patch thêm mới hoàn toàn (không có trong BASE)
- **[?]** = điểm chưa xác minh được từ source — cần Opus/cuhoang confirm

---

## ✅ BP_FurnitureInputManager.md
**Đích:** `docs/Blueprints/BP_FurnitureInputManager.md` (hiện ở `docs/00_Core/BP_FurnitureInputManager_MERGED_v1.9.md` — chờ move Lô C)
**Version:** 1.9 | 15/06/2026 | **Mẫu chuẩn** (done trước session)
**Nguồn:** base v1.6 + patch v1.7 + patch v1.8 + patch v1.9

| Mục | Trạng thái |
|---|---|
| Variables (đầy đủ multi-select Sprint 1-4) | GIỮ |
| SpawnFurnitureCopy (bAutoSelect + NewActor output) | SỬA(v1.7) |
| SelectActors, DeselectAll, ToggleActor, ExpandSelectionWithGroups | SỬA(v1.8/v1.9 T2 viết lại) |
| CaptureSnapshot CLEAR TempSelectedIndices | SỬA(v1.7 fix v1.5) |
| Sprint 3 group functions (CreateGroup, GetGroupChildren, v.v.) | MỚI(v1.7) |
| Sprint 4 edit mode (EnterEdit, ExitEdit, ResolveSelectionUnit, v.v.) | MỚI(v1.8/v1.9) |
| ComputeSelectionUnits TRƯỚC guard (F3) | SỬA(v1.9) |
| SpawnFurnitureCopy + GroupID scope (F4 v1.9) | SỬA(v1.9) |

**Xung đột:** ExpandSelectionWithGroups Sprint 3 → thay bởi Sprint 4 T2 (v1.9) ✅
**[?]:** FindGroupData output pin có Index không — cần verify với BP_UndoManager (đã flag)
**Session_State khớp:** Y

---

## ✅ BP_UndoManager.md
**Đích:** `docs/Blueprints/BP_UndoManager.md`
**Version:** 1.8 | 15/06/2026
**Nguồn:** v1.2 + v1.4 + v1.5 + v1.6 (BASE) + v1.7_patch + v1.8_patch

| Mục BASE v1.6 | Trạng thái |
|---|---|
| Variables (TempSelectedIndices, RestoredActors, TempGroups) | GIỮ |
| S_SceneSnapshot (Version 3, Groups) | SỬA(v1.8): thêm EditModeStackSnapshot → Version 4 |
| S_FurniturePlacement (GroupID từ v1.6) | GIỮ |
| CaptureSnapshot Step 0 CLEAR TempSelectedIndices | GIỮ |
| CaptureSnapshot Step 0b SET TempGroups | GIỮ |
| CaptureSnapshot Step 0c SET TempEditModeStack | MỚI(v1.8) |
| Make S_SceneSnapshot: Groups=TempGroups | GIỮ; EditModeStackSnapshot=TempEditModeStack MỚI(v1.8) |
| RestoreSnapshot Step 5b SyncGroupsToContainer | GIỮ |
| RestoreSnapshot Step 5b SET EditModeStack | MỚI(v1.8) |
| RestoreSnapshot ValidateEditMode() | MỚI(v1.7) |
| ValidateEditMode (For Each With Break) | MỚI(v1.7) |
| Event End Play CLEAR TempGroups, CLEAR TempEditModeStack | GIỮ/MỚI(v1.8) |

**Xung đột:** Không
**[?]:** SyncGroupsToContainer signature cần cross-check; FindGroupData (_, _, bFound) output — xem trên
**Session_State khớp:** Y (A12 test Case 1+2 PASS)

---

## ✅ A1: WBP_MeshControls.md
**Đích:** `docs/Widgets/WBP_MeshControls.md`
**Version:** 1.6 | 15/06/2026
**Nguồn:** v1.4 base (10/06) + WBP_MeshControls.md merged (11/06, effective v1.5) + v1.5_update (12/06) + v1.6_patch (15/06)

| Mục BASE | Trạng thái |
|---|---|
| Variables, Layout, BTN_Move/Rotate/Scale (T15 multi) | GIỮ |
| Event Construct: bind OnSelectionChanged | GIỮ; bind OnEditModeChanged MỚI(v1.5) |
| OnSelectionChangedInfoBar Then 1: inline label | SỬA(v1.6): thay bằng GetSelectionUnitLabel |
| OnSelectionChangedInfoBar Then 2: BTN_EnterEdit visibility | MỚI(v1.5) |
| OnEditModeChangedInfoBar | MỚI(v1.5) |
| BTN_EnterEdit, HB_EditModeBar, BTN_ExitOneLevel | BTN_EnterEdit/HB MỚI(v1.5); BTN_ExitOneLevel MỚI(v1.5_update) |
| OnClicked BTN_ExitOneLevel | MỚI(v1.5_update) |
| Widget names (HB_SelectionInfo/TXT_SelectionInfo) | SỬA(v1.6): đổi sang Border_ET_SelectionCount/ET_SelectionCount |

**Xung đột:** OnSelectionChangedInfoBar — v1.5 gọi info bar "Then 0", v1.6 gọi "Then 1" → dùng v1.6
**[?]:** (1) Then 0 có nội dung gì không (v1.6 không đề cập). (2) BTN_Delete còn là single hay đã đổi sang DeleteSelected.
**Session_State khớp:** Y

---

## ✅ A2: Blueprint_Logic_NodeFlow.md
**Đích:** `docs/Blueprints/Blueprint_Logic_NodeFlow.md`
**Version:** 1.5 | 15/06/2026
**Nguồn:** v1.3 base (07/06) + v1.4_patch (12/06) + v1.5_patch (15/06)

| Mục BASE v1.3 | Trạng thái |
|---|---|
| QUY ƯỚC GHI | GIỮ |
| WBP_FurnitureInventory (11 functions) | GIỮ |
| WBP_MaterialCard | GIỮ |
| BP_FurnitureInputManager Box Select (4 flows) | GIỮ |
| BP_UndoManager v1.1 single (legacy note) | GIỮ (ghi rõ legacy, xem BP_UndoManager.md) |
| C++ FurnitureFilterLibrary | GIỮ |
| UX Issues table | GIỮ |
| Sprint 3 group functions | MỚI(v1.4) |
| Sprint 4: 7 helpers, Edit Mode, T2/T3/T4/T5/T6/T7/T8 | MỚI(v1.4) |
| Replace GroupID BugFix (12/06) | MỚI(v1.4) |
| 6 LEARNINGS (L-NEW-1 → L-NEW-6) | MỚI(v1.5) |
| NODE FLOW ĐÃ CONFIRM table | MỚI(v1.5) |

**Xung đột:** ExpandSelectionWithGroups Sprint 3 → thay bởi Sprint 4 T2 (v1.4) ✅
**[?]:** Không
**Session_State khớp:** Y

---

## ✅ A3: WBP_DragOverlay_FurnitureCard.md
**Đích:** `docs/Widgets/WBP_DragOverlay_FurnitureCard.md`
**Version:** 1.5 | 15/06/2026
**Nguồn:** v1.3 base (25/05) → v1.4 base (10/06) + BugFix GroupID (12/06, từ Blueprint_Logic v1.4) + v1.5_patch (15/06)

| Mục BASE v1.4 | Trạng thái |
|---|---|
| WBP_FurnitureCard: Layout, Variables, OnListItemObjectSet | GIỮ |
| UpdateFavTint, Button_FavoriteFurniture (v1.2) | GIỮ |
| F_ExecuteReplace (multi, v1.4) | SỬA(12/06 BugFix): thêm GET GroupID → SET NewActor.GroupID trước Destroy |
| Button_InforItem, On Drag Detected, On Drag Cancelled | GIỮ |
| WBP_DragOverlay: Variables, On Drag Over | GIỮ |
| WBP_DragOverlay: On Drop | SỬA(v1.5 F4): chèn GetCurrentEditScope → Branch → SET GroupID |
| BTN_ChangeMesh v1.3 single (từ base 25/05) | XÓA(v1.4): thay bởi F_ExecuteReplace multi |

**Xung đột:** BTN_ChangeMesh v1.3 vs v1.4 → giữ v1.4 ✅
**[?]:** Không
**Session_State khớp:** Y

---

## ✅ A4: WBP_FurnitureInventory.md
**Đích:** `docs/Widgets/WBP_FurnitureInventory.md`
**Version:** 2.4 | 10/06/2026
**Nguồn:** v2.2 + v2.3 Resize patch + v2.3 Inventory_Card patch (08/06) → WBP_FurnitureInventory.md merged (11/06) + v2.4 dispatcher refactor (10/06)

| Mục BASE 11/06 | Trạng thái |
|---|---|
| Variables, Layout (512×1024, resize 8 hướng), C++, Paths, Pipeline | GIỮ |
| Widgets con (SlotSwatch, MaterialCard, TreeNode, FurnitureCard, DetailPopup) | GIỮ |
| F_ExecuteReplace trong FurnitureCard sub-section | SỬA: thêm GroupID BugFix (12/06) |
| Event Construct Then 0-3 | GIỮ; Then 4: SỬA(v2.4): bind OnSelectionChanged (xóa OnMeshSelected/Deselected) |
| OnMeshSelected / OnMeshDeselected (pre-2.4) | SỬA(v2.4): OnMeshSelected rewrite + OnMeshDeselected XÓA |
| OnSelectionChangedMaterial | MỚI(v2.4) |
| EnterReplaceMode | SỬA(v2.4): + EnsureExpanded đầu hàm |
| OpenMaterialModeForActor, EnsureExpanded | GIỮ (đã có từ 08/06 patch trong 11/06 base) |
| FilterByFolderPathWithUI, CreateChipTagsForPath | GIỮ |
| Key Learnings, Window Controls, Level BP, Phase plan | GIỮ |

**Xung đột:** OnMeshSelected dispatcher (pre-2.4) vs v2.4 internal handler → giữ v2.4 ✅
**[?]:** Layout size 512×1024 (11/06) vs 720×630 (10/06 file) — cần kiểm lại kích thước thực tế trong UE5
**Session_State khớp:** Y

---

## ✅ B1: BP_GizmoController.md
**Đích:** `docs/Blueprints/BP_GizmoController.md`
**Version:** 1.1 | 05/06/2026
**Nguồn:** v1.1 base (05/06) + OnMouseReleased fragment (16/04, v1.0 tham khảo)

| Mục | Trạng thái |
|---|---|
| Variables, ActivateGizmo, DeactivateGizmo | GIỮ |
| OnMousePressed (v1.1 + T15 RefreshOffsets) | GIỮ |
| OnMouseReleased (đầy đủ trong v1.1 base) | GIỮ; fragment 16/04 là OLDER version |
| Event Tick Hover, Event Tick Movement | GIỮ |
| Lưu ý tích hợp | GIỮ |

**Xung đột:** OnMouseReleased 16/04 dùng `Get Player Controller → Cast BP_FoffPlayerController` vs v1.1 base dùng `Get All Actors Of Class(BP_FurnitureInputManager)` → giữ v1.1 (mới hơn, consistent với architecture)
**[?]:** Không
**Session_State khớp:** Y

---

## ✅ B2: BP_FurnitureActor.md + BP_FurnitureSceneManager.md
**Đích:** `docs/Blueprints/BP_FurnitureActor.md` + `docs/Blueprints/BP_FurnitureSceneManager.md`
**Version:** 1.1 | 22/05/2026 (Actor); 05/05/2026 (SceneManager)
**Nguồn:** Tách từ `BP_FurnitureActor_SceneManager.md` (1 file gốc gộp 2 BP)

| Mục BP_FurnitureActor | Trạng thái |
|---|---|
| Variables (MeshPath, DAPath, MaterialOverrides, v.v.) | GIỮ |
| Event BeginPlay (SET Tags) | GIỮ |
| Event ActorLoaded (EMS) | GIỮ |

| Mục BP_FurnitureSceneManager | Trạng thái |
|---|---|
| Variables (SaveGameMenuRef) | GIỮ |
| Event Tick (rebind SaveGameMenu) | GIỮ |
| OnLoadButtonClicked | GIỮ |
| SaveFurnitureScene / LoadFurnitureScene | GIỮ |

**Xung đột:** Không (chỉ tách, không merge)
**[?]:** BP_FurnitureActor v1.1 cũ — chưa có GroupID variable (được SET từ F_ExecuteReplace/On Drop). GroupID chỉ sống trong Blueprint runtime var, không có trong doc này. Cần thêm GroupID vào Variables section. ĐÁNH DẤU [?].
**Session_State khớp:** Y (cấu trúc cơ bản đúng)

---

## ✅ B3: DEVIATIONS.md
**Đích:** `docs/00_Core/DEVIATIONS.md`
**Version:** cuối | 15/06/2026
**Nguồn:** 07/06 (Sprint 1+2) + DEVIATIONS.md 12/06 (Sprint 3+4 master) + Sprint4BugFix addendum (15/06)

| Nguồn | Nội dung | Trạng thái |
|---|---|---|
| 07/06 | Sprint 1 table (10 entries) | GIỮ |
| 07/06 | Sprint 2 table (10 entries) | GIỮ |
| 07/06 | Sprint summaries Sprint 1+2 | GIỮ |
| DEVIATIONS.md 12/06 | Sprint 3 table (10 entries) | GIỮ |
| DEVIATIONS.md 12/06 | Sprint 4 table (10 entries) | GIỮ |
| DEVIATIONS.md 12/06 | BUGS DEFERRED, QUYẾT ĐỊNH HOÃN, NGUYÊN TẮC GHI | GIỮ |
| Addendum 15/06 | Sprint 4 Bug Fix section (4 entries) | MỚI |
| Addendum 15/06 | BUGS DEFERRED update (B3-gizmo pre-existing) | SỬA |
| Addendum 15/06 | F4 SPAWN PATHS table | MỚI |

**Xung đột:** Không
**[?]:** Không
**Session_State khớp:** Y

---

## ✅ B4: FilterByCategory_Logic.md
**Đích:** `docs/Data/FilterByCategory_Logic.md`
**Version:** 1.2 | 25/05/2026
**Nguồn:** v1.2 (25/05) mới hơn v1.1 (22/05) → dùng v1.2

| Mục v1.2 | Trạng thái |
|---|---|
| Signature, Flow đầy đủ | GIỮ (newer version) |
| Recent branch (v1.1) | GIỮ trong v1.2 |
| Favorite branch | MỚI trong v1.2 so với v1.1 |
| Toggle logic BTN_Recent/Favorite | MỚI(v1.2) |
| UpdateSpecialHighlight | MỚI(v1.2) |
| Persist khi switch mode | MỚI(v1.2) |
| Nơi gọi, Lưu ý quan trọng | GIỮ/MỚI(v1.2) |

**Xung đột:** v1.1 vs v1.2 → giữ v1.2 hoàn toàn ✅
**[?]:** Không
**Session_State khớp:** Y

---

---

## ✅ C1: 00_Core/01_Session_State.md
**Đích:** `docs/00_Core/01_Session_State.md`
**Nguồn:** `import_raw/Session_State_15jun2026.md` (15/06 20:30) wins over `import_raw/Session_State.md` (12/06)

| Mục | Trạng thái |
|---|---|
| Kiến trúc v1.9 (Sprint 4 BugFix complete, F1-F4+A12) | GIỮ (từ nguồn mới) |
| BUG CÒN MỞ (B1 bIsRestoring, B-gizmo, Replace folder) | GIỮ (từ nguồn mới) |
| Roadmap v3.1, Gate 1 tasks, Sprint D plan | GIỮ (từ nguồn mới) |

**Xung đột:** Session_State.md (12/06) vs Session_State_15jun2026.md (15/06) → giữ 15/06 hoàn toàn (cập nhật nhất)
**[?]:** Không
**Session_State khớp:** Y (chính là file nguồn)

---

## ✅ C2: 00_Core/PROGRESS.md
**Đích:** `docs/00_Core/PROGRESS.md`
**Nguồn:** `import_raw/PROGRESS.md` (base 12/06) + `import_raw/PROGRESS_Sprint4BugFix_update.md` (patch 15/06)

| Mục BASE PROGRESS.md | Trạng thái |
|---|---|
| Overview bar (Sprint 0–7) | SỬA(patch): cập nhật Sprint 4 BugFix → ✅ COMPLETE |
| Sprint 0–3 sections | GIỮ |
| Sprint 4 section | SỬA(patch): thêm BugFix subsection (F1-F4+A12, test PASS) |
| Gate 1 section | MỚI(patch): added from patch file |

**Xung đột:** Không
**[?]:** Không
**Session_State khớp:** Y

---

## ✅ C3: 00_Core/02_Current_Sprint.md
**Đích:** `docs/00_Core/02_Current_Sprint.md`
**Nguồn:** `import_raw/Gate1_SprintD_Execution_Opus.md` (full 666 dòng, 1-source)

Coverage: Gate 1 (G1.T1 bIsRestoring guard, G1.T2 spawn merge, G1.T3 docs) + Sprint D (D.T1-D.T9 Data Layer v2) + Gate 2 notes + Sprint 5 warnings — GIỮ nguyên
**[?]:** Không
**Session_State khớp:** Y (Gate 1 tasks match 01_Session_State.md)

---

## ✅ C4: Blueprints/BP_FurnitureInputManager.md
**Đích:** `docs/Blueprints/BP_FurnitureInputManager.md`
**Nguồn:** `docs/Blueprints/BP_FurnitureInputManager_MERGED_v1.9.md` (826 dòng, đã merge từ session trước)
**Ghi chú:** Move/copy — không có nội dung mới. File gốc _MERGED_v1.9.md giữ nguyên làm backup.
**[?]:** Không
**Session_State khớp:** Y (version 1.9 khớp kiến trúc v1.9)

---

## ✅ C5: Rules/AI_Implementation_Rules.md
**Đích:** `docs/Rules/AI_Implementation_Rules.md`
**Version:** 2.1 | 15/06/2026
**Nguồn:** `import_raw/28-05-2026_09_AI_Implementation_Rules.md` (base v1.0) + `import_raw/09_AI_Implementation_Rules_patch_v2.md` (patch v2.0, 14/06) + `import_raw/AI_Communication_Rules_update_15jun2026.md` (patch v2.1, 15/06)

| Mục BASE v1.0 | Trạng thái |
|---|---|
| L1-L8 (luật gốc) | GIỮ |
| L9 (section gốc ngắn) | SỬA(v2.0): mở rộng đáng kể |
| Q8 SELF-CHECK GATE (4-point) | MỚI(v2.0) |
| BÀN GIAO OPUS→SONNET | MỚI(v2.0) |
| Q8 mở rộng 5-point (Container, IsValid, L2, No Latent, 6A reverse) | SỬA(v2.1) |
| L2 CHECK section | MỚI(v2.1, từ communication update) |
| Blueprint Export Method | MỚI(v2.1) |
| Spawn Paths checklist | MỚI(v2.1) |
| Runtime State vs Snapshot State | MỚI(v2.1) |

**Xung đột:** Q8 4-point (v2.0) vs Q8 5-point (v2.1) → giữ v2.1 (mới hơn, superset)
**[?]:** Không
**Session_State khớp:** Y

---

## ✅ C6: Rules/Execution_Discipline.md
**Đích:** `docs/Rules/Execution_Discipline.md`
**Version:** 2.0 | 14/06/2026
**Nguồn:** `import_raw/28-05-2026_10_Execution_Discipline.md` (base v1.0) + `import_raw/10_Execution_Discipline_patch_v2.md` (patch v2.0, 14/06)

| Mục BASE v1.0 | Trạng thái |
|---|---|
| CƠ CHẾ 1–5 | GIỮ |
| CƠ CHẾ 6 (Luật 6A + Luật 6B) | MỚI(v2.0) |
| Definition of Done (+2 điều kiện mới) | SỬA(v2.0) |
| Checklist cuối task (2 điều kiện thêm) | SỬA(v2.0) |

**Xung đột:** Không
**[?]:** Không
**Session_State khớp:** Y (Luật 6A/6B active từ Gate 1)

---

## ✅ C7: Rules/AI_Communication_Rules.md
**Đích:** `docs/Rules/AI_Communication_Rules.md`
**Nguồn:** `import_raw/AI_Communication_Rules_update_15jun2026.md` (standalone)
**Ghi chú:** Header file gốc nói "Thêm vào 09_AI_Implementation_Rules.md" nhưng TARGET_STRUCTURE có entry riêng → tạo standalone. Nội dung cũng đã merge vào AI_Implementation_Rules.md v2.1 (C5).
**[?]:** Không
**Session_State khớp:** Y

---

## ✅ C8–C13: Rules/ (6 files 1-source)

| File | Nguồn | Ghi chú |
|---|---|---|
| Rules/Workflow.md | `import_raw/24-04-2026_Workflow.md` | 1-source, 55 dòng |
| Rules/Project_Instructions.md | `import_raw/Project_Instructions_Updated.md` | 1-source, 147 dòng; cập nhật paths → docs/ |
| Rules/Design.md | `import_raw/Design.md` | Xử lý nội dung trùng: giữ v1.1 (với Tab system), bỏ phần cũ |
| Rules/Antipatterns.md | `import_raw/antipatterns.md` | 1-source, 99 dòng |
| Rules/Performance.md | `import_raw/28-05-2026_08_Performance_Optimization.md` | 1-source, 278 dòng |
| Rules/Learning_System.md | `import_raw/Learning_System.md` | 1-source, 122 dòng |

**[?] Design.md:** File gốc có 2 phần — v1.1 (có Tab system, pagination=48) và phần cũ (không có Tab, pagination=50). Đã giữ v1.1. Nếu phần cũ có thông tin khác → cần kiểm lại.

---

## ✅ C14–C29: Planning/ (16 files 1-source)

| File | Nguồn |
|---|---|
| Planning/00_Master_Plan.md | `import_raw/28-05-2026_00_Master_Plan.md` |
| Planning/01_Current_Architecture_Audit.md | `import_raw/28-05-2026_01_Current_Architecture_Audit.md` |
| Planning/02_Target_Architecture.md | `import_raw/02_Target_Architecture.md` |
| Planning/03_Code_Inheritance_Strategy.md | `import_raw/28-05-2026_03_Code_Inheritance_Strategy.md` |
| Planning/04_Sprint_Details.md | `import_raw/04_Sprint_Details.md` (1208 dòng; undated = dated version, identical) |
| Planning/06_Risk_Mitigation.md | `import_raw/06_Risk_Mitigation.md` |
| Planning/07_Testing_Strategy.md | `import_raw/28-05-2026_07_Testing_Strategy.md` |
| Planning/Architecture_Overview.md | `import_raw/architecture.md` |
| Planning/Backend_Plan.md | `import_raw/Backend_Plan_v1.md` |
| Planning/Future_Architecture_1M_Assets.md | `import_raw/13-05-2026-22h30p_Future_Architecture_1M_Assets.md` |
| Planning/Integration_Guide.md | `import_raw/02-06-2026-11h44p_Integration_Guide.md` |
| Planning/MultiSelect_Group_ComboMesh_Plan.md | `import_raw/26-05-2026_09h40p_MultiSelect_Group_ComboMesh_Plan_v2.md` (v2 > v1) |
| Planning/Plugin_Migration_Guide.md | `import_raw/01-06-2026_Plugin_Migration_Guide.md` |
| Planning/Tech_Defaults.md | `import_raw/tech-defaults.md` |
| Planning/UE5_InteriorTool_Overview.md | `import_raw/UE5_InteriorTool_Doc.md` |
| Planning/i18n_Plan.md | `import_raw/13-05-2026-00h00p_i18n_plan.md` |

**Xung đột Planning:** MultiSelect_Group_ComboMesh_Plan có v1 và v2 → giữ v2 (mới hơn) ✅
**[?]:** Không

---

## ✅ C30–C41: Sprints/ (12 files 1-source)

| File | Nguồn |
|---|---|
| Sprints/Sprint0_UX/UX_Phase2_Plan.md | `import_raw/20-05-2026_UX_Phase2_Plan.md` |
| Sprints/Sprint0_UX/Resize_Window_Plan.md | `import_raw/26-05-2026_Resize_Window_Plan.md` |
| Sprints/Sprint1/START_HERE.md | `import_raw/02-06-2026_START_HERE_Sprint1.md` |
| Sprints/Sprint1/T15_Rotate_Scale_Plan.md | `import_raw/04-06-2026_T15_Multi_Rotate_Scale_Plan.md` |
| Sprints/Sprint2/Plan.md | `import_raw/05-06-2026_Sprint2_Plan_v2.md` |
| Sprints/Sprint2/ContextMenu_Prep.md | `import_raw/07-06-2026-23h30p_Sprint2_ContextMenu_ChangeMaterial_Replace_Prep.md` |
| Sprints/Sprint3/Plan.md | `import_raw/08-06-2026-11h24p_Sprint3_Plan_Opus.md` |
| Sprints/Sprint3/Regression_DualDispatcher_Log.md | `import_raw/10-06-2026-20h34p_Sprint3_Regression_DualDispatcher_Log.md` |
| Sprints/Sprint4/Plan.md | `import_raw/08-06-2026_Sprint4_Plan_Opus.md` |
| Sprints/Sprint4/Execution.md | `import_raw/Sprint4_Execution_Opus.md` |
| Sprints/Sprint4/BugFix_Execution.md | `import_raw/Sprint4_BugFix_Execution_Opus.md` |
| Sprints/Sprint5/Combo_Execution.md | `import_raw/Sprint5_Combo_Execution.md` |

**[?]:** Không

---

## ✅ C42–C44: Data/ (3 files 1-source)

| File | Nguồn |
|---|---|
| Data/Data_Structures.md | `import_raw/28-05-2026_05_Data_Structures.md` |
| Data/FilterBySearch_Logic.md | `import_raw/22-05-2026_FilterBySearch_Logic.md` |
| Data/Python_Scripts.md | `import_raw/16-05-2026-14h08_Python_Scripts.md` |

---

## ✅ C45: Data/FurnitureFilterLibrary_Reference.md
**Đích:** `docs/Data/FurnitureFilterLibrary_Reference.md`
**Nguồn:** `import_raw/FurnitureFilterLibrary.cpp` (source C++ — không copy, chỉ reference doc)
**Ghi chú:** Tạo tài liệu reference từ source code — 4 hàm (FilterFurnitureItems, FilterFurnitureItemsFromRegistry, FilterMaterialItems, LoadFurnitureItem). Lưu ý pattern PropertyLink cho Sprint D.
**[?]:** Không

---

## ✅ C46–C47: Features/ (2 files 1-source)

| File | Nguồn |
|---|---|
| Features/ChangeMaterial.md | `import_raw/18-05-2026-08h55p_ChangeMaterial_Context_v1_1.md` |
| Features/Material_CopyPaste.md | `import_raw/02-06-2026-12h30p_Material_CopyPaste_v0.md` |

---

## ✅ C48–C50: Widgets/ bổ sung (3 files 1-source)

| File | Nguồn |
|---|---|
| Widgets/WBP_BoxSelectOverlay.md | `import_raw/07-06-2026-22h40p_WBP_BoxSelectOverlay.md` |
| Widgets/WBP_DetailPopup.md | `import_raw/25-05-2026-17h29p_WBP_DetailPopup.md` |
| Widgets/WBP_ResizeWindow.md | `import_raw/27-05-2026-10h30p_WBP_ResizeWindow.md` |

---

## ✅ C51–C54: Blueprints/ bổ sung (4 files 1-source)

| File | Nguồn | Ghi chú |
|---|---|---|
| Blueprints/BP_PivotActor.md | `import_raw/05-06-2026-20h00p_BP_PivotActor.md` | Dùng 05/06 > 04/06 (mới hơn) |
| Blueprints/BP_FoffPlayerController.md | `import_raw/25-04-2026_BP_FoffPlayerController.md` | 1-source |
| Blueprints/Flows/Nudge_Flow.md | `import_raw/04-06-2026-15h30p_B1_Nudge_Flow.md` | 1-source |
| Blueprints/Flows/CopyPaste_Flow.md | `import_raw/04-06-2026-15h30p_B2_CopyPaste_Flow.md` | 1-source |

---

## ✅ C55: Bugs/Bug_GPU_VRAM_Crash.md
**Nguồn:** `import_raw/09-05-2026-08h30p_Bug_GPU_VRAM_Crash.md` (1-source)

---

## ✅ D1: Bugs/Open_Bugs.md
**Đích:** `docs/Bugs/Open_Bugs.md`
**Nguồn:** Tổng hợp từ `docs/00_Core/01_Session_State.md` (BUG CÒN MỞ) + `docs/00_Core/DEVIATIONS.md` (BUGS DEFERRED) + `docs/00_Core/02_Current_Sprint.md` (G1.T1 fix plan)

| Bug | Ưu tiên | Trạng thái trong doc |
|---|---|---|
| B1 — Undo lần 2 không restore group state | 🔴 Cao | Có đủ: triệu chứng, H1/H2/H3, fix plan, test cases |
| B-gizmo — Gizmo ẩn sau undo edit mode | 🟢 Thấp | Có: pre-existing, workaround, chưa có timeline |
| B-folder — Replace folder sai group | 🟢 Thấp | Có: root cause, fix Sprint D D.T6 plan |
| Closed Bugs (Bug2, Bug3, F1-F4, A12) | — | Reference table |

**[?]:** Không
**Session_State khớp:** Y (B1/B-gizmo/B-folder khớp 01_Session_State.md)

---

## ✅ D2: 00_Core/00_INDEX.md
**Đích:** `docs/00_Core/00_INDEX.md`
**Nguồn:** Directory listing từ `find docs -name "*.md"` (76 files, 15/06/2026)
**Ghi chú:** Index điều hướng — không chứa nội dung kỹ thuật. Cần update khi thêm file mới.
**[?]:** Không

---

## Tổng kết trạng thái — Lô A + B + C + D (COMPLETE)

### Lô A + B
| File | Version | Đích | Status |
|---|---|---|---|
| BP_FurnitureInputManager.md | 1.9 | Blueprints/ | ✅ |
| BP_UndoManager.md | 1.8 | Blueprints/ | ✅ |
| WBP_MeshControls.md | 1.6 | Widgets/ | ✅ |
| Blueprint_Logic_NodeFlow.md | 1.5 | Blueprints/ | ✅ |
| WBP_DragOverlay_FurnitureCard.md | 1.5 | Widgets/ | ✅ |
| WBP_FurnitureInventory.md | 2.4 | Widgets/ | ✅ |
| BP_GizmoController.md | 1.1 | Blueprints/ | ✅ |
| BP_FurnitureActor.md | 1.1 | Blueprints/ | ✅ |
| BP_FurnitureSceneManager.md | — | Blueprints/ | ✅ |
| DEVIATIONS.md | cuối 15/06 | 00_Core/ | ✅ |
| FilterByCategory_Logic.md | 1.2 | Data/ | ✅ |

### Lô C (55 files)
| Nhóm | Files | Status |
|---|---|---|
| 00_Core/ | 01_Session_State.md (15/06), PROGRESS.md (merged), 02_Current_Sprint.md | ✅ |
| Blueprints/ | BP_FurnitureInputManager.md (move), BP_PivotActor.md, BP_FoffPlayerController.md | ✅ |
| Blueprints/Flows/ | Nudge_Flow.md, CopyPaste_Flow.md | ✅ |
| Rules/ (10 files) | AI_Implementation_Rules v2.1 (3-source), Execution_Discipline v2.0 (2-source), AI_Communication_Rules, Workflow, Project_Instructions, Design, Antipatterns, Performance, Learning_System | ✅ |
| Planning/ (16 files) | 00_Master_Plan → i18n_Plan | ✅ |
| Sprints/ (12 files) | Sprint0_UX(2), Sprint1(2), Sprint2(2), Sprint3(2), Sprint4(3), Sprint5(1) | ✅ |
| Data/ | Data_Structures, FilterBySearch_Logic, Python_Scripts, FurnitureFilterLibrary_Reference (từ .cpp) | ✅ |
| Features/ | ChangeMaterial, Material_CopyPaste | ✅ |
| Widgets/ | WBP_BoxSelectOverlay, WBP_DetailPopup, WBP_ResizeWindow | ✅ |
| Bugs/ | Bug_GPU_VRAM_Crash | ✅ |

### Lô D
| File | Nguồn | Status |
|---|---|---|
| Bugs/Open_Bugs.md | Tổng hợp 3 nguồn (Session_State + DEVIATIONS + 02_Current_Sprint) | ✅ |
| 00_Core/00_INDEX.md | Directory listing 76 files | ✅ |

---

## Mục [?] cần Opus/cuhoang xác minh

| # | File | Vấn đề |
|---|---|---|
| Q1 | WBP_MeshControls.md | Then 0 của Sequence OnSelectionChangedInfoBar có nội dung gì không? |
| Q2 | WBP_MeshControls.md | BTN_Delete còn là single hay đã đổi sang DeleteSelected (multi)? |
| Q3 | BP_UndoManager.md / BP_FurnitureInputManager.md | FindGroupData output pins: có pin Index không? |
| Q4 | WBP_FurnitureInventory.md | Layout kích thước: 512×1024 hay 720×630? |
| Q5 | BP_FurnitureActor.md | ✅ GIẢI QUYẾT (17/06, D.T6): GroupID : String SaveGame (xác nhận Sprint 3 T2). Đã thêm vào v1.2. |
| Q6 | Rules/Design.md | Phần cũ bị drop (pagination=50) có thông tin nào khác v1.1 không? |
| Q7 | Planning/Master_Roadmap.md | ✅ GIẢI QUYẾT (17/06): ALIAS của Planning/00_Master_Plan.md (import_raw/28-05-2026_00_Master_Plan.md = C14-C29). KHÔNG tạo file mới. TODO: content lỗi thời (28/05), refresh khi làm Planning sprint. |
| Q8 | Data/Data_Overview.md | ✅ GIẢI QUYẾT (17/06): GAP thật — ĐÃ TẠO Data/Data_Overview.md (cuhoang cung cấp content, kiến trúc D.T6). |

---

## Ghi chú bổ sung sau hoàn thành Lô C + D

### import_raw/INDEX.md (11/06/2026)
- **Đã xử lý:** Không copy nguyên. Nội dung cốt lõi ("Muốn sửa X → đọc Y") đã chuyển sang `docs/00_Core/00_INDEX.md` với paths mới. Phần "Điểm cần đối chiếu BP" → tương đương với [?] list trong MERGE_LOG này.
- **Trạng thái:** Superseded bởi `00_Core/00_INDEX.md` ✅

### import_raw/performance.md (v1.1, 20/05/2026)
- **Đã xử lý:** File cũ hơn `08_Performance_Optimization.md` (28/05). Nội dung chính đã được cover bởi file 28/05.
- **Unique content đã merge:** Section "Đã apply" VRAM (BP_UndoManager, WBP_FurnitureInventory, WBP_MaterialCard) + Workaround restart → đã thêm vào `Rules/Performance.md` VRAM section.
- **Trạng thái:** ✅

### Planning/MultiSelect_Group_ComboMesh_Plan.md
- **Ghi chú:** File này tồn tại trong docs/ nhưng KHÔNG có trong TARGET_STRUCTURE tree. Không vi phạm quy tắc (không có _patch/_update suffix). Để nguyên vì nội dung vẫn hữu ích.
- **[?]:** Cần thêm vào TARGET_STRUCTURE hay move sang Archive/?

---

## ✅ [MỚI — không qua merge] Widgets/WBP_FolderTreePicker.md + WBP_FolderPickerRow.md
Tạo trực tiếp 11/07/2026, C5.8 Task Card #2 — **không có nguồn import_raw**, viết thẳng từ task card + export K2Node (không qua bước merge base+patch như các file Lô A-D ở trên). WBP_FolderPickerRow.md v1.1, WBP_FolderTreePicker.md v1.0 (11/07 13:14, sau Giai đoạn 1 bug fix).
