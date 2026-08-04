# MERGE LOG — UE5 InteriorTool Docs
**Mục đích:** Reviewer chỉ cần đọc file này để biết file nào cần soi kỹ.
**Cập nhật:** 11/07/2026 13:14
**Cập nhật (tiếp) 02/08/2026:** thêm mục "HISTORICAL stamps 02/08/2026" (banner [HISTORICAL] cho 8 file plan/Sprint cũ).
**Cập nhật (tiếp) 02/08/2026 (b):** `Sprints/Sprint3/Regression_DualDispatcher_Log.md` — quyết định cuối KHÔNG đóng dấu (as-built phụ), thêm vào coverage như nguồn as-built phụ cho BP_FurnitureInputManager.md/BP_UndoManager.md.
**Cập nhật (tiếp) 02/08/2026 (c):** thêm mục "AS-BUILT lẫn trong Plans/Sprints — 02/08/2026" — 6 file đóng dấu `📌 [CHỨA AS-BUILT]` (không di chuyển/đổi tên).
**Cập nhật (tiếp) 02/08/2026 (d):** đóng 2 mục `[?]` — Q3 (`FindGroupData` không có Index, sửa chữ ký sai trong `BP_FurnitureInputManager.md` v2.9) và Q4 (layout `WBP_FurnitureInventory` = 512×1024, file đã đúng sẵn). Nguồn: `CrossCheck_PreGate2_02aug2026.md` MỤC 3. Q1/Q2/Q6 giữ nguyên treo (ngoài phạm vi).
**Cập nhật (tiếp) 02/08/2026 (e, Lô D):** viết doc `ResolveSelectedComboRoot()` vào `BP_FurnitureInputManager.md` (K2Node export thật). Q3 củng cố thêm bằng chứng độc lập thứ 2 + sửa thêm 2 file còn sót chữ ký sai (`BP_UndoManager.md` v1.13, `Blueprint_Logic_NodeFlow.md` v1.15). Ghi nhận `[DOC-DRIFT]` mới (`PrimarySelectedActor` vs `SelectedActors[0]`) vào `DEVIATIONS.md` — CHƯA đóng, chờ task card Save As/Save đè. **Chưa đụng** (còn sót chữ ký `FindGroupData` cũ, cần quyết định riêng có nên sửa log lịch sử hay không): `Sprints/Sprint4/Execution.md`, `Sprints/Sprint4/BugFix_Execution.md`, `Blueprints/BP_FurnitureInputManager_MERGED_v1.9.md` (file duplicate đã bị đánh dấu xóa từ 17/06, không sửa).
**Cập nhật (tiếp) 02/08/2026 (f, Lô E — ĐÓNG ĐỢT DỌN):** thêm dấu thứ 3 `⚠️ [AS-BUILT TẠI THỜI ĐIỂM SPRINT 4]` cho `Sprints/Sprint4/Execution.md` + `Sprints/Sprint4/BugFix_Execution.md` (KHÔNG sửa nội dung, chỉ banner). Thêm bảng "3 LOẠI DẤU DOC" (mục mới, trước "HISTORICAL stamps"). Xác nhận `BP_FurnitureInputManager_MERGED_v1.9.md` **vẫn còn tồn tại** trong repo dù đã đánh dấu xóa từ 17/06/2026 — báo cáo, không tự xóa. Tổng kết cả đợt: `00_Core/DocCleanup_Summary_02aug2026.md`. **Đợt dọn docs KẾT THÚC.**
**Cập nhật (tiếp) 02/08/2026 (g):** `BP_FurnitureInputManager_MERGED_v1.9.md` — quyết định cuhoang: **XÓA THẬT** (git rm). Cập nhật mọi tham chiếu sang canonical (`BP_FurnitureInputManager.md` dòng 11, mục coverage `BP_FurnitureInputManager.md` + `C4`, `00_INDEX.md` — xóa dòng index). Thêm mục "File đã xóa" (cuối file) để tra lại lý do/ngày nếu cần.
**Cập nhật (tiếp) 03/08/2026:** thêm `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` — plan Save As/Save đè combo (khung 5 task, task card T1 đầy đủ). File đang chạy, CHƯA có as-built — không đóng dấu banner nào. Đích tương lai (khi T1+ xong): `Blueprints/BP_FurnitureInputManager.md`, `Widgets/WBP_SaveComboDialog.md`, `Data/ComboSerializer_Reference.md`.
**Cập nhật (tiếp) 04/08/2026:** merge delta `DELTA_04-08-2026_T3_SaveComboDialog.md` — thêm mục `7b. TASK CARD T3` vào `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` (v1.0→v1.2, PLAN, chưa test). 2 entry backlog mới: `Bugs/Open_Bugs.md` (`Bug-SaveComboSilentBlock`), `DEVIATIONS.md` (`[ARCH-DEBT] AllComboViews_Combo sống ở widget`). **KHÔNG merge** mục A của delta (K2Node export `CB_SaveCombo_Handler` 04/08) vào `Blueprints/BP_FurnitureInputManager.md` — xung đột với section as-built đã có sẵn (khác cấu trúc guard + thiếu bước `ContextMenuRef.Hide`), ghi cả 2 bản vào `DEVIATIONS.md` mục `[CONFLICT] CB_SaveCombo_Handler — 2 bản không khớp — 04/08/2026`, chờ cuhoang xác nhận. `02_Current_Sprint.md`: chỉ đổi ô T3 → 🔄 Đang mở, KHÔNG đụng ô T2.
**Cập nhật (tiếp) 04/08/2026 (b):** cuhoang đối chiếu K2Node export → đóng `[CONFLICT] CB_SaveCombo_Handler` (KHÔNG phải xung đột thật, doc cũ 24/06 chỉ thiếu 2 bước) — đổi tên mục thành `[DOC-DEBT đã đóng]` trong `DEVIATIONS.md`. `Blueprints/BP_FurnitureInputManager.md` v3.0→v3.1: thay section `CB_SaveCombo_Handler` bằng bản ✓K2 04/08/2026, bù dòng lịch sử `3.0` bị thiếu từ trước.
**Cập nhật (tiếp) 04/08/2026 (c, Lô A):** merge delta `DELTA_04-08-2026_LoA_SaveCombo_Verify.md` (as-built, T0 của T4). `Blueprints/BP_ComboManager.md` v1.14→v1.15: `SaveComboFromSelection` re-export ✓K2 04/08 — additive (thêm Bước 0 param→class var + xác nhận Bước 5a/7), KHÔNG đổi hệ đánh số "Bước N" (tránh gãy cross-reference nhiều nơi trong file). `Data/ComboSerializer_Reference.md`: ✓SOURCE 04/08 xác nhận đúng 13 hàm public `UComboSerializer`, ghi nhận `LoadCombo` không tồn tại. `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` v1.2→v1.3: thêm mục 4.1 (quyết định kiến trúc T4 — Branch tại điểm sinh ComboID, chưa thực thi). 2 entry mới `Bugs/Open_Bugs.md` (`Bug-ComboCategoryHardcode`) + 2 entry `DEVIATIONS.md` (`[AS-BUILT] Broadcast OnComboLibraryChanged...`, `[DOC-DRIFT] Plan C7 dựa vào LoadCombo...`). `DocCleanup_Summary_02aug2026.md`: thêm mục 4.5 (xếp ưu tiên Lô B/C/D). KHÔNG đụng `02_Current_Sprint.md`/`PROGRESS.md` (delta không chứa kết quả thực thi task).

---

## Cách đọc bảng coverage
- **GIỮ** = không đổi từ BASE
- **SỬA(patch)** = patch thay thế/mở rộng nội dung BASE
- **XÓA(patch)** = patch xóa hẳn mục này
- **MỚI(patch)** = patch thêm mới hoàn toàn (không có trong BASE)
- **[?]** = điểm chưa xác minh được từ source — cần Opus/cuhoang confirm

---

## ✅ BP_FurnitureInputManager.md
> ⚠️ Số version dưới đây là as-built TẠI THỜI ĐIỂM MERGE (snapshot lịch sử của lần merge từ
> `import_raw`), KHÔNG phải version hiện hành — tra version sống ở header file canonical
> (`docs/Blueprints/BP_FurnitureInputManager.md` dòng 2). (Ghi chú thêm 03/08/2026, không đổi số.)

**Đích:** `docs/Blueprints/BP_FurnitureInputManager.md` (move từ `BP_FurnitureInputManager_MERGED_v1.9.md` đã xong từ lâu; file nguồn đã XÓA THẬT 02/08/2026 — xem mục "File đã xóa" cuối MERGE_LOG.md)
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
**Ghi chú:** Move/copy — không có nội dung mới. File gốc _MERGED_v1.9.md từng giữ lại làm backup,
**đã XÓA THẬT 02/08/2026** (quyết định cuhoang — canonical đã v2.9, chênh 10 phiên bản, rủi ro đọc
nhầm cao hơn giá trị lưu trữ; lịch sử đã có trong git).
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
| Q3 | BP_UndoManager.md / BP_FurnitureInputManager.md | ✅ GIẢI QUYẾT (02/08/2026, qua `CrossCheck_PreGate2_02aug2026.md` MỤC 3, củng cố thêm 02/08 Lô D). **KHÔNG có pin Index — `FindGroupData(InGroupID) → (S_GroupData, bFound)`, đúng 2 output.** Bằng chứng (2 nguồn độc lập): (1) `Plans/24-07-2026_C9_Execution_Plan.md` dòng 42 (§V8: *"FindGroupData chỉ có 2 output: (Group Data, Found) — KHÔNG có Index"*, K2Node export 23/07) + dòng 689; (2) K2Node export `ResolveSelectedComboRoot` 02/08/2026 (cuhoang cung cấp, gọi `FindGroupData(RootGID) → bFound / GroupData`, đúng 2 output) — xem `BP_FurnitureInputManager.md` mục `ResolveSelectedComboRoot`. Đã sửa chữ ký sai ở **3 file**: `BP_FurnitureInputManager.md` v2.9 (định nghĩa hàm + 2 call site còn sót `(data, _, bFound)`), `BP_UndoManager.md` v1.13 (`ValidateEditMode`), `Blueprint_Logic_NodeFlow.md` v1.15 (header tự mâu thuẫn "KHÔNG có Index...TRẢ Index"). |
| Q4 | WBP_FurnitureInventory.md | ✅ GIẢI QUYẾT (02/08/2026, qua `CrossCheck_PreGate2_02aug2026.md` MỤC 3): **512×1024 là giá trị đúng hiện hành.** Bằng chứng: `Widgets/WBP_FurnitureInventory.md` dòng 144 (`## Layout (512×1024, resize 8 hướng)`) + dòng 1734 (`Set Size(512,1024)` ở Event Construct) — nhất quán, không hedge. `720×630` là giá trị LỊCH SỬ trước khi có Resize Window — còn thấy ở `Planning/UE5_InteriorTool_Overview.md` dòng 89 và `Sprints/Sprint0_UX/Resize_Window_Plan.md` (dòng 25, kích thước gốc trước khi resize) — cả 2 đều là doc cũ, KHÔNG sửa (ngoài phạm vi yêu cầu, giá trị đó đúng là lịch sử tại thời điểm viết). Không cần sửa `WBP_FurnitureInventory.md` — file đã đúng sẵn. |
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

---

## 3 LOẠI DẤU DOC — đọc bảng này TRƯỚC khi gặp bất kỳ banner nào trong docs/

Đợt dọn docs 02/08/2026 (Lô A→E) dùng 3 loại banner khác nhau — dễ nhầm nếu không tra bảng này.

| Dấu | Ý nghĩa | Đọc thế nào | Ví dụ file |
|---|---|---|---|
| `⚠️ [HISTORICAL]` | File mô tả **THIẾT KẾ tại thời điểm viết** (plan), nhiều quyết định đã bị **override** ở sprint sau. Toàn bộ file coi như "vì sao đã quyết vậy", KHÔNG phải trạng thái hiện tại. | Đọc để hiểu bối cảnh/lý do quyết định. **KHÔNG** lấy bất kỳ chi tiết kỹ thuật nào (tên hàm, chữ ký, node flow) làm sự thật hiện tại — luôn tra doc canonical (`As-built hiện tại xem:` ghi ngay trong banner). | `Planning/03_Code_Inheritance_Strategy.md`, `Sprints/Sprint2/Plan.md`, `Sprints/Sprint3/Plan.md`... (xem mục "HISTORICAL stamps" dưới) |
| `📌 [CHỨA AS-BUILT]` | File **bắt đầu là plan** nhưng bị ghi thêm **kết quả thực thi thật** (test PASS, K2Node export, changelog per-gate) thẳng vào thân. Banner ghi rõ phần nào là as-built. | Phần as-built được banner chỉ ra **ưu tiên cao hơn** doc canonical nếu 2 bên mâu thuẫn (đọc kỹ nhãn "Phần nào là as-built" trong banner). Phần còn lại của file (mô tả kế hoạch gốc) vẫn chỉ là plan — không tự động đúng. | `Plans/24-07-2026_C9_Execution_Plan.md`, `Plans/P2_StudioThumbnail_Execution.md`... (xem mục "AS-BUILT lẫn trong Plans/Sprints" dưới) |
| `⚠️ [AS-BUILT TẠI THỜI ĐIỂM X]` | File ghi lại **đúng những gì đã thực thi tại 1 mốc thời gian** (vd Sprint 4) — KHÔNG phải plan, nhưng cũng **KHÔNG được cập nhật** theo các thay đổi sau đó. Một số chữ ký/API mô tả trong file có thể đã đổi. | Đọc để hiểu **việc đã làm** ở mốc đó (lý do, node flow lúc bấy giờ). **KHÔNG** suy ra chữ ký/API hiện tại từ file này — luôn tra doc canonical hiện hành trước khi code. Khác `[HISTORICAL]` ở chỗ: đây không phải "plan bị override", mà là "log đúng lúc đó, đơn giản là cũ". | `Sprints/Sprint4/Execution.md`, `Sprints/Sprint4/BugFix_Execution.md` |

**Phân biệt nhanh:** `[HISTORICAL]` = "kế hoạch, không phải sự thật đã xảy ra". `[CHỨA AS-BUILT]` =
"kế hoạch + có 1 phần sự thật mới hơn canonical trộn lẫn vào". `[AS-BUILT TẠI THỜI ĐIỂM X]` =
"toàn bộ là sự thật đã xảy ra, nhưng là sự thật CŨ, có thể đã lỗi thời".

---

## HISTORICAL stamps 02/08/2026

**Mục đích:** đóng dấu banner `⚠️ [HISTORICAL]` ngay sau dòng H1 cho các file mô tả THIẾT KẾ tại
thời điểm viết (không phải as-built hiện tại), để người đọc không nhầm plan cũ với trạng thái
code thật. Chỉ chèn banner — KHÔNG sửa nội dung nào khác trong các file này.

| File đóng dấu | As-built hiện tại |
|---|---|
| `Planning/03_Code_Inheritance_Strategy.md` | `Blueprints/BP_FurnitureInputManager.md` + `Blueprints/BP_UndoManager.md` |
| `Planning/04_Sprint_Details.md` | `00_Core/PROGRESS.md` |
| `Planning/MultiSelect_Group_ComboMesh_Plan.md` | `Sprints/Sprint5/Combo_Execution.md` |
| `Sprints/Sprint2/Plan.md` | `Blueprints/BP_FurnitureInputManager.md` |
| `Sprints/Sprint2/ContextMenu_Prep.md` | `Blueprints/BP_FurnitureInputManager.md` (ghi chú KP3 nội bộ về §5.2 lỗi thời — GIỮ NGUYÊN) |
| `Sprints/Sprint3/Plan.md` | `Blueprints/BP_FurnitureInputManager.md` |
| `Sprints/Sprint4/Plan.md` | `Sprints/Sprint4/Execution.md` |
| `Sprints/Sprint0_UX/UX_Phase2_Plan.md` | `Blueprints/Flows/*.md` |

**KHÔNG đóng dấu (loại trừ tường minh):**
- `Sprints/Sprint4/Execution.md` — vẫn là nguồn as-built của Sprint 4, không phải plan.
- Mọi file trong `Rules/`, `Blueprints/`, `Widgets/`, `Data/`, `Bugs/`, `00_Core/`.

**Sprint3/* — rà trước khi đóng dấu (theo yêu cầu riêng):** thư mục có 2 file —
`Sprints/Sprint3/Plan.md` (đã đóng dấu, đúng là plan) và
`Sprints/Sprint3/Regression_DualDispatcher_Log.md` — **QUYẾT ĐỊNH CUỐI (cuhoang, 02/08/2026):
KHÔNG đóng dấu — as-built phụ, không phải plan.** Lý do: file ghi node flow của các function ĐÃ
SỬA THẬT (as-built) trong đợt regression-fix Sprint 3, không phải plan thiết kế; đóng dấu
[HISTORICAL] sẽ khiến session sau bỏ qua một nguồn as-built đúng. Xem mục coverage riêng bên
dưới ("Regression_DualDispatcher_Log.md — nguồn as-built phụ").

---

## 📌 Sprints/Sprint3/Regression_DualDispatcher_Log.md — nguồn as-built phụ

**Đích chính:** `Blueprints/BP_FurnitureInputManager.md` + `Blueprints/BP_UndoManager.md`
**Vai trò:** KHÔNG phải plan, KHÔNG đóng dấu HISTORICAL — nguồn tham chiếu node flow cho các
function ĐÃ SỬA THẬT trong đợt regression-fix + refactor dual-dispatcher sau Sprint 3 (10/06/2026):
`CaptureSnapshot`, `RestoreSnapshot` (BP_UndoManager); hợp nhất dispatcher chọn lựa thành
`OnSelectionChanged` duy nhất (xóa `OnMeshSelected`/`OnMeshDeselected`), xóa biến
`MeshToReplace` (single) (BP_FurnitureInputManager).

**Dùng khi nào:** `Blueprint_Logic_NodeFlow.md`/`BP_FurnitureInputManager.md`/`BP_UndoManager.md`
thiếu chi tiết hoặc mâu thuẫn về node flow của các function trên — đối chiếu ngược lại file này
trước khi hỏi cuhoang, vì đây là log chi tiết ghi tại thời điểm fix thật (không phải suy diễn).

---

## AS-BUILT lẫn trong Plans/Sprints — 02/08/2026

**Bối cảnh:** VIỆC 3 quét lan (02/08) phát hiện 6 file mang tên "Plan"/"Task Card" nhưng bị ghi
thêm kết quả thực thi thật (test PASS, K2Node export, changelog per-gate) thẳng vào thân file,
thay vì đưa về doc canonical trong `Blueprints/`/`Widgets/`. Quyết định cuhoang: KHÔNG di
chuyển/đổi tên (tránh gãy đường dẫn chéo giữa lúc chuẩn bị Lô C + Save As) — chỉ đóng dấu banner
`📌 [CHỨA AS-BUILT]` ngay sau H1 của cả 6 file.

| File | Phần nào là as-built | Đối chiếu doc canonical nào |
|---|---|---|
| `Plans/01-08-2026_Phase0_Verify_Report_ReplaceUXFix.md` | Toàn bộ file — báo cáo verify 5/5 mục bằng K2Node export thật | `Blueprints/BP_FurnitureInputManager.md`, `Widgets/WBP_FurnitureInventory.md` |
| `Plans/P2_StudioThumbnail_Execution.md` | Mục Gate A–F (kết quả test từng Gate nối vào thân plan) | `Blueprints/BP_ComboManager.md` |
| `Plans/P1_ComboThumbnail_Execution.md` | Bảng Changelog v1.1 (Sửa/Gate) + kết quả Gate G0→G4 | `Blueprints/BP_ComboManager.md` |
| `Plans/24-07-2026_C9_Execution_Plan.md` | Ghi chú v1.1 (audit sửa 2 lỗi nghiêm trọng) + §10 kết quả test case | `Blueprints/BP_FurnitureInputManager.md`, `Blueprints/BP_ComboManager.md`, `Blueprints/BP_UndoManager.md` |
| `Sprints/Sprint5/C5.8_TaskCard2_FixPlan_11jul2026.md` | Dòng "As-built binding" (K2Node 11/07) + "Test mục 1-5 PASS" | `Widgets/WBP_FolderPickerRow.md`, `Widgets/WBP_FolderTreePicker.md` |
| `Sprints/Sprint5/C5.8_REG_TaskCard_11jul2026.md` | Bảng kết quả cuối file "✅ Khối A/B/C PASS" (regression C5.8, 13/07) | `Widgets/WBP_FolderTreePicker.md`, `Widgets/WBP_MoveToFolderDialog.md`, `Widgets/WBP_SaveComboDialog.md` |

**Upgrade trigger:** sau Gate 2 → gom phần as-built về đúng doc canonical, hoặc lập thư mục riêng
cho execution report, tách khỏi `Plans/`. Xem `DEVIATIONS.md` mục "[DOC-DEBT] AS-BUILT lẫn trong
Plans/Sprints — 02/08/2026" + luật mới `R-DOC-ASBUILT` (`Rules/Execution_Discipline.md`).

---

## `[AS-BUILT TẠI THỜI ĐIỂM SPRINT 4]` stamps — 02/08/2026

Khác 2 loại dấu trên (xem bảng "3 LOẠI DẤU DOC" phía trên) — 2 file dưới đây **KHÔNG phải
plan**, mà là log thực thi THẬT của Sprint 4, nhưng chưa được cập nhật theo các thay đổi sau đó
(vd `FindGroupData` đổi chữ ký ở MERGE_LOG Q3, 02/08/2026).

| File đóng dấu | Vì sao KHÔNG sửa nội dung |
|---|---|
| `Sprints/Sprint4/Execution.md` | Ghi lại thực thi Sprint 4 (11/06/2026) — vẫn là nguồn as-built chính thức của Sprint 4 (không đóng dấu `[HISTORICAL]`). Sửa chữ ký `FindGroupData` trong này = viết lại lịch sử, mất dấu vết chữ ký lúc đó thật sự là gì. |
| `Sprints/Sprint4/BugFix_Execution.md` | Cùng lý do — log bug-fix session 14/06/2026, giữ nguyên như lúc viết. |

**Quyết định cuhoang (02/08/2026):** chỉ đóng dấu banner, KHÔNG sửa nội dung 2 file này dù chúng
còn giữ chữ ký `FindGroupData` cũ (`(data, _, bFound)` — 3 output, đã xác nhận sai ở MERGE_LOG
Q3). Nếu cần đọc lại Sprint 4 để hiểu logic lúc đó → vẫn dùng được, chỉ đừng lấy chữ ký hàm/API
trong đây làm chuẩn hiện tại.

---

## File đã xóa

| File | Ngày xóa | Lý do | Ghi chú |
|---|---|---|---|
| `Blueprints/BP_FurnitureInputManager_MERGED_v1.9.md` | 02/08/2026 | Quyết định cuhoang: bản backup v1.9, canonical (`BP_FurnitureInputManager.md`) đã v2.9 — chênh 10 phiên bản, rủi ro đọc nhầm cao hơn giá trị lưu trữ. Đã "đánh dấu xóa" từ 17/06/2026 nhưng chưa ai xóa thật cho tới lúc này. | Lịch sử đầy đủ vẫn còn trong git (`git log --follow`/`git show <commit>:<path>` nếu cần tra lại). Đã kiểm mọi tham chiếu trong `docs/` — cập nhật link/ghi chú sang canonical, không còn chỗ nào trỏ tới file đã xóa (xem `BP_FurnitureInputManager.md` dòng 11, `00_Core/00_INDEX.md`, và 2 mục coverage phía trên). |

---
