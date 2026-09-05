# PROGRESS — Tiến độ Multi-Select / Group / Combo / Material v1.2
**Nguồn:** `import_raw/PROGRESS.md` (12/06/2026) + `import_raw/PROGRESS_Sprint4BugFix_update.md` (patch 15/06/2026)
**Cập nhật:** 31/07/2026 — C9.0c (Migrate E_ReplaceTarget) HOÀN TẤT, tiền đề cho C9 | K1 (WBP_Toast) DONE | C6 (Favorite + Recent combo) CHÍNH THỨC DONE HOÀN TOÀN | P2 Studio Thumbnail Gate F DONE, P2 HOÀN TẤT VỀ TÍNH NĂNG (Gate A→F) | P1 Combo Thumbnail DONE về tính năng | C5.8 CHÍNH THỨC DONE (13/07) | C9 (Replace Combo) DONE (30/07) — chuyển sang Save As/Save đè
**Cập nhật (tiếp) 02/08/2026:** Replace UX Fix (P0→P5) ĐÓNG HOÀN TOÀN (01-02/08) — 6 bug UX gốc trên C9 (#1/#3a/#3b/#4/#5/#6) rụng hết, đường ngược Luật 6A đóng đủ, dead code `MeshToReplace` xóa. Bug-fix round trên ô C9 đã tick — không đổi bar đếm Sprint 5 (16/22). Xem `01_Session_State.md`.
**Cập nhật (tiếp) 02/08/2026:** Luật Q9 (S-Matrix Gate) thiết lập + 3 bug mới xác nhận bằng test tay (Bug-MaterialPrimaryOnly/Bug-PasteVerticalCollapse/Bug-StaleSurfaceType), cả 3 dời sau Gate 2 — KHÔNG đổi thứ tự ưu tiên (Save As/Save đè → C11 → C10 → Gate 2). Xem `01_Session_State.md`.
**Cập nhật (tiếp) 07/08/2026:** Save As/Save đè T3 (`WBP_SaveComboDialog`) — ✅ DONE, test PASS 6/6. Đóng `Bug-SaveConfirm-EmptyName`. Bar Sprint 5 KHÔNG đổi (18/23, R-DOC-ATOMIC — tử số chỉ +1 khi T5 xong). Tiếp theo: T4. Xem `01_Session_State.md`.
**Cập nhật (tiếp) 07/08/2026 (T4 task card):** RECOUNT R-DOC-COUNT xác nhận bar Sprint 5 `18/23`
đúng — T3 đã tick (dòng trên), T4 CHƯA thực thi nên KHÔNG tick, chỉ phát hành task card (`Plans/
03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 7d). Không phát hiện ô checklist nào gộp nhiều
việc cần tách trong đợt này. Thêm entry backlog `Task-T4.5-AutoGroupAfterOverwrite` vào
`Bugs/Open_Bugs.md` (chưa mở, không tính vào mẫu số Sprint 5).
**Cập nhật (tiếp) 07/08/2026 (T4 DONE, 15:40):** Save As/Save đè T4 (Overwrite Flow) — ✅ ĐÓNG,
test PASS 6/6. Tick `[x]` sub-item T4. Bar Sprint 5 KHÔNG đổi (18/23, R-DOC-ATOMIC — tử số item
cha `[~]` chỉ +1 khi T5 xong). Tiếp theo: T5 (regression + docs closure). Xem `01_Session_State.md`.
**Cập nhật (tiếp) 08/08/2026 (T5 DONE — Sprint 5 bar 19/23):** Save As/Save đè (T1-T5) — ✅ ĐÓNG
HOÀN TOÀN. Tick `[x]` sub-item T5, tick `[x]` item cha "Save As/Save đè" (đủ điều kiện +1 tử số
theo R-DOC-ATOMIC — trước đó `[~]`). Bar Sprint 5: 18/23 → **19/23**. D1 (Khối D task T5) đóng
dạng N/A — giới hạn engine (Set of String không toggle được Pass-by-Reference), ghi chi tiết
DEVIATIONS.md. D2 (`Bug-ComboCategoryHardcode`) fix xong — xem Open_Bugs.md. Tiếp theo: C11
(Export/Import combo). Xem `01_Session_State.md`.
**Cập nhật (tiếp) 10/08/2026 (P4-early DONE):** `GetCombosDir()` đổi sang `%LOCALAPPDATA%/
InteriorFOFFTool/Combos` (P4, dời sớm trước C11). Migrate tay từ `Saved/Combos/*` thành công.
Verify 3/3 ô PASS. Tiếp theo: C11 (Export/Import). Nguồn: `DELTA_10-08-2026_C11_P4early.md`.
**Cập nhật (tiếp) 10/08/2026 (C11.1+C11.2 DONE):** `ComboSerializer` thêm 4 hàm
(`GetExportsDir`/`ExportCombo`/`ImportCombo`/`ImportAllFromExportsDir`), build success.
`CB_ExportCombo` (context menu combo card, item mới "📤 Xuất file…") — 3/3 test PASS: file
`.combojson` ra đúng `Exports/`, tên tiếng Việt giữ nguyên, thumbnailBase64 nhúng đúng. Bug Input
Mode phát hiện+fix lúc test (xem `DEVIATIONS.md`). Doc-drift `OnComboCardRightClicked`
(`MovingComboID` không tồn tại — SỬA thành `LibMenu.TargetComboID`) đã patch. Còn treo: C11.3
Import — quyết định UX (quét thư mục tự động vs dialog chọn file) chưa chốt, bàn tiếp phiên sau
với Opus. Nguồn: session 10/08/2026.
**Cập nhật (tiếp) 10/08/2026 (C11 DONE HOÀN TOÀN):** Export/Import combo qua thư mục `Exports/`
(P4-early áp trước, combo sống qua update app đóng gói). C++ +4 hàm
(`GetExportsDir`/`ExportCombo`/`ImportCombo`/`ImportAllFromExportsDir`). Export: context menu
ComboCard "📤 Xuất file…", 3/3 test PASS. Import: nút `BTN_ImportCombo` riêng (không context
menu — sai ngữ cảnh), 4/4 test PASS. 2 bug phát hiện+fix lúc test: (1) thiếu `Set Input Mode
Game and UI` ở `CB_ExportCombo` — camera bị khóa sau export; (2) `CallDelegate` Target phải là
`ComboManagerRef` không phải `self`. Doc-drift `CB_MoveCombo`/`OnComboCardRightClicked` cũng
được sửa trong phiên này (`MovingComboID` xác nhận vị trí SET đúng). Tiếp theo: C10 (Regression
full Sprint 5) → Gate 1.5 (Packaged Smoke). Nguồn: session 10/08/2026,
`DELTA_10-08-2026_C11_P4early.md` + patch UX Import.
**Cập nhật (tiếp) 17/08/2026 (Gate 1.5 — 2 blocker packaging bắt xong):** Cook `L_ToolSmokeTest`:
**1126 → 729 lỗi, tool sạch hoàn toàn** (cuong/ error = 0), 729 còn lại 100% content master.
2 mìn bắt được: **FIX-1** (179 file corrupt magic-header trong KitchenPro/Plus_Development/
Datasmith — quarantine `I:\_FoffCorruptQuarantine\`, KHÔNG file nào của tool). **FIX-2**
(`RuntimeTransformer` không package do `.uplugin` khai `EngineVersion: 4.27.0` + `Installed: true`
→ PluginManager bỏ qua bản packaged — sửa `.uplugin` + rebuild, verify PIE gizmo chạy). Blocker
còn lại: `Foff_GameInstance` (master) dính chặt qua 3 dây cast (Inventory/Input/Camera-Pawn) →
đổi hướng sang Interface Decoupling + migrate project sạch (task nhiều ngày). Xem
`01_Session_State.md` + `Plans/17-08-2026_Gate1.5_InterfaceDecoupling_Migrate_Plan_v1.md`.
Gate 1.5 — Phase B: 4/4 dây cắt xong (Pawn/Input/Inventory/Toast), test PIE PASS.
Gate 1.5 — Phase C: C1-C3 DONE. 7 coupling-point phát sinh, đã fix hết (xem DEVIATIONS).
                     PIE verify: 0 lỗi compile trong cuong/. C4 đang chạy.
Gate 1.5 — Phase C.C4: host standalone tối giản DONE (BP_StandaloneToolPC/GameMode,
                       ArchvizPCG_Camera + 4 deps, axis mappings tay). Xem DEVIATIONS.
Gate 1.5 — Phase C.C5: package DEVELOPMENT thành công, .exe chạy máy sạch (không cài UE).
                       Còn lỗi runtime packaged (chưa fix, dời đợt sau).
Gate 1.5 — ĐÓNG 20/08/2026. ⚠️ Development build, KHÔNG phải Gate 2 (Shipping).
Gate 1.5 — Sự cố engine binary giữa phiên (sửa code gốc UE → Verify Epic fix). Xem DEVIATIONS.
**Cập nhật (tiếp) 27/08/2026:** Sprint 7 — G0 DONE toàn phần (a/b/c/d), Q1 chốt "ÍT nhưng CÓ Ý
NGHĨA" (1,56% mesh trùng slot), Q2 chốt DYNAMIC (texture picker), hybrid click-to-select duyệt
(Fable). G1 task card phát hành (Việc 1 = vertical slice `TraceSlotUnderCursor`). Xem
`01_Session_State.md`, `Plans/Sprint7_MaterialEdit_Plan_v1.1.md` v1.4.
**Cập nhật (tiếp) 03/09/2026:** Sprint 7 — S7.G2 đang chạy: Bước 0 + Việc 1 (swatch tên +
selection) + Việc 2 (reroute apply — đường GHI Records) PASS. **Resequence G2↔G3**
(`DELTA_Opus_S7_Resequence`, cuhoang duyệt): đường khôi phục snapshot (`RestoreMyMaterialSlots`
on-actor + Capture/Restore chụp `MaterialSlots`) kéo từ G3 lên G2 = **Việc 2B** (GATE undo/redo,
PASS mới sang Việc 3); G3 co lại còn legacy branch + EMS + Combo + migration. Tên struct snapshot
chốt `S_FurniturePlacement` (trong `BP_UndoManager`) — `S_ActorSnapshotData` trong plan G3 cũ là
sai, đã sửa toàn doc. Bar Sprint 7 KHÔNG đổi (resequence không đóng G-task nào). Xem
`Plans/Sprint7_MaterialEdit_Plan_v1.1.md` v1.6, `Sprints/Sprint7/S7G2_Reroute_ExecutionPlan_27aug2026.md`,
`01_Session_State.md`, `DEVIATIONS.md` mục "SPRINT 7 — 03/09/2026".
**Cập nhật (tiếp) 04/09/2026:** Sprint 7 — S7.G2 **Việc 2B** (đường khôi phục snapshot:
`RestoreMyMaterialSlots` on-actor + Capture/Restore chụp `MaterialSlots` trên `S_FurniturePlacement`)
— ✅ PASS full 6 bước undo/redo + **bonus redo-stack case** (apply nhánh MỚI sau Undo → Redo đúng
nhánh mới, không lẫn state nhánh cũ đã cắt — `CaptureSnapshot` resize redo-stack đúng). Cặp Việc 2 +
2B (đường ghi + đường ngược) = xương sống G2 xác nhận đứng vững. Còn Việc 3 (multi-apply E1) · 4
(copy/paste) · 5 (reset) → Test tổng G2. Race warning `ResetAllSlotsToAssetDefault Mesh không hợp lệ`
mỗi lần restore (race LoadMeshAsync vs RestoreMyMaterialSlots) — vô hại luồng hiện tại (actor luôn
spawn mới), dời `Sprint7_MaterialEdit_Plan_v1.1.md` G3 test #10 soi. Bar Sprint 7 KHÔNG đổi. Xem
`Sprints/Sprint7/S7G2_Reroute_ExecutionPlan_27aug2026.md` (as-built Việc 2B).

---

## TỔNG QUAN

```
Sprint 1 — Multi-select       ███████████████ 15/15 SHIPPED ✅
Sprint 2 — Box + Context Menu ████████████████ 9/9  SHIPPED ✅
Sprint 3 — Group cơ bản       ████████████████ 12/12 SHIPPED ✅  (+10 bug fix)
Sprint 4 — Edit + Nested      ████████████████ 8/8  SHIPPED ✅  (+5 bug fix thêm)
Gate 1                        ████████████████ 3/3  DONE ✅ (16/06)
Sprint D — Data Layer v2      ████████████████ 9/9  DONE ✅ (17/06)
Sprint 5 — Combo Mesh         ███████████████████░░░  22/23 task, DONE (P3 defer)
                               ✅ DONE: T1/T2 core/C0/C1/C2/C3a/C3b/Fix K3/C4/C5 (Folder Management
                               đầy đủ)/C6/Delete Combo/Field Kích thước Card/WBP_Toast (K1)/C8/C9
                               (Replace Combo, 30/07)/P2 (Studio Thumbnail, 02/08)/P1 (Thumbnail
                               System C++, 02/08)/Save As/Save đè (T1-T5, 08/08)
                               ⏳ CÒN LẠI (4): C3 (P4 LOCALAPPDATA chưa áp)/Xoay combo (P3)/C11
                               (Export/Import)/C10 (Regression)
                               [03/08 R-DOC-ATOMIC: Save As/Save đè là tính năng RIÊNG (execution
                               plan riêng, T1→T5 riêng) — thêm 1 ô mẫu số 22→23 (`[~]`, KHÔNG tick
                               khống thành DONE). Tử số KHÔNG +1 máy móc — chỉ [x] khi T5 (regression
                               + docs closure) xong. Bar Sprint đếm theo tính năng, không đếm T2 rời.]
                               [31/07 Doc-Sync: đếm lại theo R-DOC-COUNT (số ô tick thật, không
                               nuôi tay) — xem `Rules/Execution_Discipline.md` mục R-DOC. C7 dời
                               sang mẫu số Sprint 6 (xem dưới); dòng "C5 — Folder tree tab" trùng
                               lặp/lỗi thời đã XÓA khỏi checklist]
                               [02/08 recount R-DOC-COUNT: Replace UX Fix (P0→P5, 01-02/08) là
                               bug-fix round trên ô C9 ĐÃ TICK (30/07), không phải task/ô checklist
                               mới → không đổi số lúc đó. Xem changelog 01/08 + 02/08 (Replace UX
                               Fix).]
                               [02/08 R-DOC-DONE (quyết định cuhoang): P2 (Studio Thumbnail) tick
                               DONE 16/22→17/22 — case Cao (Ceiling, Gate D) tách bug riêng
                               `Bugs/Open_Bugs.md` mục "Task-P2-SweepCao", không giữ task mở. P1
                               (Thumbnail System C++) tick DONE 17/22→18/22 — G5 VRAM regression
                               tách bug riêng cùng file mục "Task-P1-VRAMRegression". Luật mới
                               `R-DOC-DONE`: xem `Rules/Execution_Discipline.md`.]
                               [08/08 R-DOC-ATOMIC đóng: Save As/Save đè T5 PASS toàn bộ (Khối
                               A+B+C+D+E) → item cha `[~]` đủ điều kiện tick `[x]`, tử số +1
                               (18→19). Xem `01_Session_State.md` 08/08/2026.]
Sprint 6 — Polish UX          ░░░░░░░░░░░░░░░  0/15 task (+C7, dời từ Sprint 5 31/07)
Sprint 7 — Material v1.2      ░░░░░░░░░        0/9  task

TỔNG: 73/103 task
```

---

## SPRINT 1 — COMPLETE ✅ (15/15)

T1-T15 shipped. Chi tiết: `Blueprints/BP_FurnitureInputManager.md`, `Blueprints/BP_PivotActor.md`.

---

## SPRINT 2 — COMPLETE ✅ 9/9 (08/06/2026)

- [x] S2.T1 — WBP_BoxSelectOverlay
- [x] S2.T2 — Box Select logic (defer + Tick + Release)
- [x] S2.T3 — WBP_ContextMenu + ContextMenuItem + Separator
- [x] S2.T4 — Right-click handler
- [x] S2.T5 — Select Similar (MeshPath)
- [x] S2.T6 — Reset Rotation + Delete callback
- [x] S2.T7 — Cut Ctrl+X
- [x] S2.T8 — Sprint 2 final test — PASS
- [x] S2.T9 — CB_ChangeMaterial + CB_Replace multi

---

## SPRINT 3 — COMPLETE ✅ 12/12 (10/06/2026) + 10 bug fix + refactor

- [x] S3.VS — Vertical Slice: T1+T2+T3+T4 + EMS Save/Load test ✅
- [x] S3.T1 — Struct S_GroupData (GroupID, GroupName, ParentGroupID, bIsLocked)
- [x] S3.T2 — BP_FurnitureActor.GroupID (SaveGame)
- [x] S3.T3 — BP_GroupsContainer (EMS + singleton guard, TempTags GET→ADD→SET)
- [x] S3.T4 — Groups var + SyncGroupsToContainer (InputManager)
- [x] S3.T5 — Helpers: GetGroupChildren, FindGroupData, GenerateGroupID, ExpandSelectionWithGroups, PruneEmptyGroups
- [x] S3.T6 — CreateGroup (auto-name "Nhóm N") + Ctrl+G
- [x] S3.T7 — UngroupActors + Ctrl+Shift+G
- [x] S3.T8 — Click resolution → ExpandSelectionWithGroups
- [x] S3.T9 — Box select → ExpandSelectionWithGroups
- [x] S3.T10 — Selection Info Bar "📦 GroupName (N)"
- [x] S3.T11 — Snapshot v3 (GroupID per placement + Groups array)
- [x] S3.T12 — DeleteSelected + PruneEmptyGroups + Final test

**10 bug fix (chi tiết `Sprints/Sprint3/Regression_DualDispatcher_Log.md`):**
1. CaptureSnapshot impure timing → TempGroups class var
2. UngroupActors spam snapshot → tách ra ForEach Completed
3. FoundIdx warning → CLEAR -1 đầu hàm
4. Undo về deselect không tắt gizmo → DeselectAll+DeactivateGizmo
5. Ctrl+click group không cộng dồn → bỏ Branch Ctrl ở Mouse Pressed
6. Replace mesh liên tục → thiếu ADD LocalNewActors trong loop
7. Replace khi inventory minimize → EnsureExpanded đầu EnterReplaceMode
8. Replace sai mesh → OnMeshSelected SET nhầm MeshToReplace(dead)
9. Material/Replace folder không auto-update → chuyển từ OnMeshSelected sang OnSelectionChanged
10. Accessed None TargetFurnitureActor → thiếu IsValid guard

**Bug còn mở:** B1 — Undo lần 2 không restore group state → carry-over Gate 1.

---

## SPRINT 4 — COMPLETE ✅ 8/8 (12/06/2026) + 2 bug fix

### Slice 1 — Flat Edit Mode
- [x] S4.T1 — EditModeStack + 7 helper (GetCurrentEditScope, GetChildGroups, GetGroupRoot, WalkUpUntilParent, GetAllDescendantActors đệ quy, GetGroupsInHierarchy đệ quy, ResolveSelectionUnit) + 2 stub (ApplyEditModeVisual, RemoveEditModeVisual) + GetEditBreadcrumb
- [x] S4.T2 — ExpandSelectionWithGroups viết lại dùng ResolveSelectionUnit
- [x] S4.T3 — EnterEditMode / ExitEditModeOneLevel / ExitEditModeFull
- [x] S4.T4 — TryEnterEditFromSelection
- [x] S4.T5 — Info Bar: BTN_EnterEdit + HB_EditModeBar (TXT_EditBreadcrumb + BTN_ExitOneLevel + BTN_ExitFull) + bind OnEditModeChanged; Sequence.Then 2 visibility BTN_EnterEdit

### Slice 2 — Nested Group
- [x] S4.T6 — CreateGroup: ParentGroupID = GetCurrentEditScope() (1 dòng)
- [x] S4.T7 — PruneEmptyGroups (GetAllDescendantActors thay GetGroupChildren) + UngroupActors peel-one-level (WalkUpUntilParent, B1 actor→cha, B2 rebuild groups, B3 xóa target)

### Safety
- [x] S4.T8 — ValidateEditMode (BP_UndoManager) + chèn sau SyncGroupsToContainer trong RestoreSnapshot

### Polish
- [⏭] S4.T9 — Dimming stub — SKIP (optional MVP)

**2 bug fix (phát hiện trong Sprint 4):**
- Bug 2: GroupID lost sau Replace Mesh → SET NewActor.GroupID = OldActor.GroupID trong BTN_ChangeMesh loop (WBP_DragOverlay_FurnitureCard) ✅
- Bug: Branch(ancestor === "") nhầm thành anchor != "" → đổi lại đúng trong ResolveSelectionUnit ✅

**Bug còn mở (lên Gate 1):**
- B1: Undo lần 2 không restore group state → Gate 1
- Replace folder sai khi group nhiều mesh khác folder → deferred Sprint 5

---

## SPRINT 4 BUG FIX — COMPLETE ✅ (15/06/2026)

**5 bug fix bổ sung (session 15/06/2026):**

- [x] **F1** — Info bar hiển thị đúng unit name (GetSelectionUnitLabel trong BP_FurnitureInputManager v1.9)
- [x] **F2** — Group name counter monotonic (GroupNameCounter chuyển sang BP_GroupsContainer, SaveGame=True)
- [x] **F3** — CreateGroup bottom-up nesting (ComputeSelectionUnits + rewrite CreateGroup)
- [x] **F4** — Spawn auto-join edit scope (SpawnFurnitureCopy + WBP_DragOverlay On Drop)
- [x] **A12** — Edit mode bar ẩn sau Undo với group có sẵn (EditModeStack vào S_SceneSnapshot V=4)

**Full test suite PASS (15/06/2026):**
- Batch 1 (Group cơ bản A1-A4): ✅
- Batch 2 (Edit Mode flat B1-B5): ✅ (B3 gizmo = known pre-existing)
- Batch 3 (Nested C1-C4): ✅
- Batch 4 (Sub-group ungroup D1-D3 + Nesting cap): ✅
- Batch 5 (Info bar + Counter E1-E3): ✅
- Batch 6 (F4 confirm + Regression S1-S4): ✅

**Known issue (pre-existing, không phải regression):**
- B3-gizmo: Gizmo ẩn sau undo trong edit mode dù đang ở Move mode

---

## GATE 1 — COMPLETE ✅ (16/06/2026)

- [x] G1.1 — Fix B1: bIsRestoring flag trong BP_UndoManager. Verify: hist ổn định qua nhiều lần restore liên tiếp, info bar + scene state đúng tại mọi điểm kể cả ranh giới Ungroup/CreateGroup.
- [x] G1.2 — Hợp nhất spawn: RestoreSnapshot Step 4 gọi SpawnFurnitureCopy(bAutoSelect=False) qua cached ref (RestoreInputMgr), xóa code spawn inline cũ. Bug phát hiện trong test: bAutoSelect bị wire nhầm thành True → tất cả item bị select sau mọi lần restore → fix lại False. 5/5 test case PASS (case "crash khi tắt PIE sau Save/Load/Undo" — defer, nghi GPU/VRAM, verify ở Gate 2).
- [x] G1.3 — Dọn doc drift (cập nhật PROGRESS.md, DEVIATIONS.md, Session_State.md, BP_UndoManager.md v1.10).

→ Tiếp theo: Sprint D (Data Layer v2). Đọc `01_Session_State.md` khi bắt đầu.

---

## SPRINT D — Data Layer v2 (17/06/2026) ✅ HOÀN THÀNH

- [x] D.T1 — Single-instance inventory toggle Visibility + box-select guard
      (Is In Viewport → Get Visibility)
- [x] D.T2 — Data prep: S_FurnitureData +ThumbnailSoft (Soft Object Ref Texture2D)
      + Python populate
- [x] D.T3 — FilterFurnitureRows C++ (mirror FilterMaterialItems, cached FProperty
      reflection, KHÔNG reinterpret_cast vì S_FurnitureData là UserDefinedStruct)
      — verify PASS: rỗng → 2114 rows, "sofa" → 136 rows
- [x] D.T4 — BP_FurnitureItemView (Object class, 10 field: RowName/VieName/EngName/
      ThumbnailSoft/MeshSoft/MeshFolderPath/BoundingSize/Description/Link/Category)
- [x] D.T5 — FilterBySearch nhánh Furniture rewire: FilterFurnitureRows →
      AllFilteredFurnitureRows → DisplayPage. Recent/Favorite bypass C++ filter,
      build trực tiếp từ BP_FurnitureUserPrefsManager.
- [x] D.T6 — Bỏ FurnitureDA, Replace Mesh đọc RowName từ actor (17/06/2026) ✅
  - BP_FurnitureActor.md v1.2: thêm RowName SaveGame
  - WBP_DetailPopup.md v1.2: InitPopup(RowName), RowData
  - WBP_MeshControls.md v1.7: BTN_Info RowName, UpdateDetailPopup bound OnSelectionChanged
  - WBP_DragOverlay_FurnitureCard.md v1.6: CardRowName, RowData, PendingRowName
  - WBP_FurnitureCard.md v1.0: TẠO MỚI
  - WBP_FurnitureInventory.md v2.5: OnCardInfoClicked(RowName), OnMeshSelected RowName branch
  - FilterByCategory_Logic.md v1.3: Recent/Favorite DT direct
  - FilterBySearch_Logic.md v1.3: FilterFurnitureRows + DisplayPage
  - BP_FurnitureInputManager.md v1.10: StartReplaceMode doc + RowName branch
  - Fix B-folder + B-stale-popup
- [x] D.T7 — BuildFolderTree C++ source swap (DT_FurnitureCatalog thay
      AllFurnitureItems) + xóa preload AllFurnitureItems khỏi Event Construct
      Then 1. Bug phụ phát hiện & fix: substring/Contains sai khi tìm Folder
      "Table" (Map_Find.Value chứ không phải ReturnValue/Found).
- [x] D.T8 — WBP_FurnitureInventory dùng đầy đủ luồng DataTable+RowName (R5),
      tích hợp xong qua D.T5+D.T6+D.T7.
- [x] D.T9 — Regression toàn bộ (9/9 PASS) + dọn doc — xem mục D.T9 bên dưới.

**Lưu ý:** bảng D.T1-D.T9 ở bản trước bị lệch nhãn (vd dòng "D.T2" ghi nhầm nội
dung của D.T7, dòng "D.T5"/"D.T8" ghi nhầm nội dung D.T3) — bảng trên đã map lại
đúng theo định nghĩa gốc trong `02_Current_Sprint.md`.

### D.T9 — Regression 9 case (17/06/2026)

| # | Case | Kết quả |
|---|---|---|
| 1 | Browse: search "sofa", folder Table, pagination, tab Material↔Furniture, Recent/Favorite | PASS |
| 2 | Mở/đóng inventory 10 lần qua nút + BTN_Close, click trái chọn ngay lần đầu | PASS |
| 3 | Drag-drop spawn 1 mesh + nhiều mesh liên tiếp | PASS |
| 4 | Replace 1 mesh + multi-replace | PASS |
| 5 | Popup ⓘ — tên/category/description đúng | PASS |
| 6 | Save → Load → mesh đúng vị trí, RowName giữ nguyên | PASS |
| 7 | Undo/Redo sau spawn, replace, group, multi-select | PASS |
| 8 | Box select: đóng inventory không hiện khung; mở lại chạy bình thường | PASS |
| 9 | PIE liên tiếp 3 lần, không crash VRAM bất thường | PASS |

**2 bug phụ phát hiện trong lúc test case 1, đã fix:**

- **Bug-Pagination:** Furniture dừng ở "7/8" dù hiển thị ban đầu đúng "1/8".
  Root cause: `Ceil(LENGTH / PageSize)` ở nhánh check nút Next dùng Int Divide
  (337÷48=7, mất phần dư) trong khi `DisplayPage` dùng Float Divide (337/48=7.02
  → Ceil=8) — 2 chỗ tính `TotalPages` lệch nhau 1. Fix: chèn `Int to Float` giữa
  LENGTH và input A của node `÷`, ở CẢ 2 nhánh Material và Furniture (cấu trúc
  copy giống nhau). Verify: Next liên tục → đúng dừng ở "8/8".
- **Bug-Maximize:** `BTN_Maximize` chỉ nở ngang từ vị trí cũ, không nhảy lên
  góc trên-trái như Maximize chuẩn. Root cause: cả 2 nhánh Maximize/Restore chỉ
  gọi `Set Size` trên Canvas Slot của `VerticalBox_0`, thiếu `Set Position` trên
  CÙNG slot. Fix: thêm `Set Position` vào cùng node `Slot as Canvas Slot(VerticalBox_0)`,
  ở cả 2 nhánh — Maximize: Position=(0,0); Restore: Position=Original Position.
  Verify: Maximize đúng góc, Restore đúng vị trí/size cũ, drag sau Restore vẫn ổn.

---

## TÍNH NĂNG BỔ SUNG — TreeNode/Chip Active-Folder Highlight (18/06/2026) ✅

Không nằm trong scope Sprint D gốc — phát sinh từ yêu cầu UX: category/folder
đang chọn trong inventory phải đổi màu và giữ màu khi đi sâu vào folder con.

- `WBP_TreeNode.RefreshDisplay` thêm param `bIsActive` → SetBackgroundColor.
- `WBP_ChipTag` thêm Custom Event `SetHighlight(bIsActive)` tương tự.
- Function Pure mới `IsPathActive(ThisPath)` trong `WBP_FurnitureInventory`:
  `CurrentFolderPath==ThisPath OR CurrentFolderPath StartsWith(ThisPath+"/")`.
- Function `UpdateFolderHighlights` (impure): loop cây TreeNode + loop chip rows,
  gọi `IsPathActive` bằng FolderPath của TỪNG widget, set highlight tương ứng.
  3 điểm gọi: cuối `CreateChipTagsForPath`, trong `OnChipTagClicked` (2 nhánh
  merge), và SAU `FilterByFolderPath` ở cả 2 nhánh `OnTreeNodeClicked`.
- Fix kèm: `BTN_FavoriteCategory`/`BTN_RecentCategory` không ẩn chip cũ khi
  chuyển category đặc biệt — thêm `ClearChildren(VB_ChipTagArea)` +
  `SetVisibility(TB_Breadcrumb, Collapsed)` đầu function.
- Test full: chuyển tab, click cấp 1, vào sâu chip cấp 2/3, quay lại "All",
  Recent/Favorite — tất cả PASS.

Chi tiết kỹ thuật: `WBP_FurnitureInventory.md` v2.6 + `WBP_TreeNode.md` + `WBP_ChipTag.md`.

**Tiếp theo:** Sprint 5 — Combo Mesh, deadline 20/06/2026.

---

## GATE 1 + SPRINT D (kế hoạch chi tiết)

**Gate 1:** fix B1 (bIsRestoring guard) + hợp nhất spawn → ✅ DONE (16/06)

**Sprint D:** Data Layer v2 (Furniture mode nhân bản kiến trúc Material mode) → ✅ DONE (17/06)

---

## SPRINT 5 — Combo Mesh 🔄 IN PROGRESS (cập nhật 23/06/2026)

- [x] **T1** — C++ ComboTypes + ComboSerializer (schema v1, round-trip JSON PASS). Build.cs: Json + JsonUtilities. ✅ 21/06/2026
- [x] **T2 core** — SaveComboFromSelection + CB_SaveCombo trong BP_ComboManager (Actor riêng, spawn Level BP). ✅ 21/06/2026
- [x] **C0** — Sửa SaveComboFromSelection nested: LCA + GetGroupsInHierarchy gom cả cây. 3 case A/B/C PASS. ✅ 22/06/2026
- [x] **C1** — FComboData.FolderPath (C++), FindMaterialRowNameByPath (C++), S_GroupData.SourceComboID (BP), FavoriteComboIDs/RecentComboIDs (UserPrefs). ✅ 22/06/2026
- [x] **C2** — SpawnComboByID + group cha SourceComboID. 7/7 PASS. ✅ 22/06/2026
- [x] **C3a** — Data layer: 2 field C++ (AuthorID/Visibility), BP_ComboItemView.FolderPath, LoadComboLibrary wire, SaveComboFromSelection signature mở rộng, GetExistingFolders+GetAllUsedTags. ✅ 23/06/2026
- [x] **C3b** — WBP_SaveComboDialog (dialog async lưu combo: ExistingFolders dropdown + folder mới + tags + validate). CB_SaveCombo → OpenSaveComboDialog (inventory đóng băng selection + UI-only mode). ✅ 24/06/2026
- [x] **Fix K3** — SpawnFurnitureCopy thêm `bAddToRecent : Boolean = True`; spawn combo + RestoreSnapshot truyền False. ✅ RESOLVED (21/07/2026) — 2 call site pin `False`, 4 case test PASS. Xem `Bugs/Open_Bugs.md` mục K3.
──── **Giai đoạn 1 (~25/06): combo Tạo + Duyệt + Đặt qua nút** ────
- [ ] **C3** — 3 phần độc lập gộp chung 1 ô (xem DEVIATIONS "[DOC-DEBT] C3 gộp 3 việc"): (1) Save
      dialog → ĐÃ XONG qua C3b; (2) móc capture thumbnail sau `SaveComboFromSelection` thành công
      → ĐÃ XONG qua P2 Gate F (21/07); (3) P4 — `GetCombosDir` → `%LOCALAPPDATA%/InteriorFOFFTool/Combos`
      → **CHƯA LÀM, phần duy nhất còn lại của C3.**
- [x] **Thumbnail System C++ (P1)** — `SaveRenderTargetToPNG` + `LoadTexture2DFromFile`; SceneCapture2D theo góc camera → PNG. Gắn vào C3/C4. ✅ DONE (02/08/2026, R-DOC-DONE).
  - [x] P1.G0-R (đổi từ G0 gốc — kiến trúc latent) — DONE 14/07/2026. Ảnh capture đúng màu/sáng/GI, xác nhận bằng so sánh trực tiếp với viewport thật (screenshot đối chiếu). Event End Play dọn rác actor/RT đã thêm (R4).
  - [x] P1.G1 — LoadComboThumbnail: đọc PNG → Texture2D transient, IImageWrapper SetCompressed/GetRaw, optional resize FImageUtils::ImageResize xuống MaxSize. Build PASS, test phím Y (tách riêng khỏi phím T capture) → size=256 đúng.
  - [x] P1.G2 — auto-fit khung hình (FitRatio) + ẩn gizmo (Get All Actors Of Class(BaseGizmo))
        + outline lúc capture. Begin/Finish đổi signature (Finish +ComboActors param để
        restore Custom Depth đúng actor). 15/07/2026.
  - [x] P1.G3 — cache Cmb_ThumbnailCache (Map) trong BP_ComboManager. 🔴 Fix bug nghiêm trọng:
        Return Node thiếu ở nhánh False (Function có return type) → cross-combo thumbnail
        bleeding. 15/07/2026.
  - [x] P1.G4 — wire full vào Save/Load flow + hiển thị WBP_ComboCard/WBP_FurnitureInventory.
        3 bug dead-end phát hiện (2 fixed, 1 backlog — xem Session_State). Test case 1,2,3,5,6
        PASS (case 4 xóa combo N/A, tính năng chưa tồn tại). 15/07/2026.
  - [x] P1.G5 — regression VRAM — tách thành entry riêng trong `Bugs/Open_Bugs.md` mục
        "Task-P1-VRAMRegression" (02/08, R-DOC-DONE) — phương pháp đo bị nhiễu, cần
        RenderDoc/Nsight thay vì MemReport thô. Không chặn P1, không giữ task mở.
- [x] **Studio Thumbnail (P2)** — Remote Studio + H-B turntable + Key/Fill RectLight + Manual
      EV100. Plan: `docs/Plans/P2_StudioThumbnail_Execution.md`. ✅ DONE (02/08/2026, R-DOC-DONE).
  - [x] P2.Gate A — vertical slice: `SpawnComboForThumbnail` clone sạch + ground-align. TEST
        PASS 6/7 case (case 7 — tắt PIE giữa Delay — dời Gate F). 17/07/2026.
  - [x] P2.Gate B — dome: hình học + Material `M_StudioBackdrop`. Cast Shadow=False (quyết
        định kiến trúc quan trọng nhất). Màu dome S1 + faceting sphere dời đợt tối ưu cuối.
        17/07/2026 (cuối phiên).
  - [x] P2.Gate C — đèn Key/Fill qua `SpawnStudioLight` (Mobility=Movable, Attenuation
        Radius=8000) + Manual EV100 (Get/Set members in Post Process Settings) + camera H-B
        `bUseFixedAngle`. 12 bug/quyết định trong lúc làm — xem DEVIATIONS.md. Verify PASS:
        2 combo khác nhau → cùng góc + cùng độ sáng. 17/07/2026 (cuối phiên).
  - [x] P2.Gate D — bóng + sweep hình dáng (nhỏ/to/dẹt/cao/tường). Rim Light + VRAM EndPlay
        fix + Source Size Key=500 DONE (20/07). Sweep 3/5 PASS (Nhỏ/To/Tường) ban đầu, 2 bug
        kiến trúc mới phát hiện — TÁCH XỬ LÝ. ✅ DONE (02/08, R-DOC-DONE) — case Cao (Ceiling)
        tách thành entry riêng trong `Bugs/Open_Bugs.md` mục "Task-P2-SweepCao", không giữ task
        mở:
        - [x] Bug-CeilingGroundAlign FIXED 20/07/2026 (Nấc 1) — Function ResolveThumbAlign,
              surface-aware align + Wall-priority rule + margin fix. Test 6/6 PASS (Floor,
              Ceiling, bàn thờ Wall+Floor, Mixed, combo cũ thiếu field, Undo/Recent/EMS). Xem
              DEVIATIONS mục "P2 — 20/07/2026 (Nấc 1)".
        - [x] Bug-DomeCurvature FIXED 20/07/2026 — dome custom (cylinder đáy bo cong, vùng
              phẳng ~500 unit, Cast Shadow=True). Test PASS combo Dẹt + To. Xem DEVIATIONS mục
              "P2 — 20/07/2026 (Dome Custom)".
        - [x] Sweep Nhỏ/To/Dẹt/Tường — 4/5 loại PASS chính thức.
        - [x] Sweep Cao — PASS SƠ BỘ (stack dựng tay). Case Cao xem `Task-P2-SweepCao` trong
              `Bugs/Open_Bugs.md` (02/08, R-DOC-DONE — không giữ ô mở song song với bug đã tách).
              Không chặn việc khác. Xem DEVIATIONS mục "(Sweep 5 Loại)".
        - [ ] Nấc 2 (below-front key + camera from-below cho pure Ceiling/Wall) — backlog,
              Switch stub đã dựng sẵn trong chuỗi phím U.
        - [x] Gate D — ĐÃ ĐÓNG (02/08, R-DOC-DONE). Case Cao (Ceiling) tách thành entry riêng
              trong `Bugs/Open_Bugs.md` mục "Task-P2-SweepCao" — đóng khi có combo thật test bổ
              sung, không giữ task Gate D mở chờ.
  - [x] P2.Gate E — DOF. Mở rộng Post Process Settings node sẵn có (Focal Distance xấp xỉ qua
        Vector Distance, Aperture=2.8 chốt bằng test đối chứng f/1.0). DONE 20/07/2026.
  - [x] P2.Gate F — DONE 21/07/2026. Custom Event mới `BeginThumbnailCapture` +
        `SetPendingUserCamYaw`; Bước 7 SaveComboFromSelection gọi BeginThumbnailCapture
        (DeltaYaw=Cmb_StudioCamYaw−Cmb_PendingUserCamYaw) thay capture in-place P1 cũ; Broadcast
        dời sang Event Tick tail; fix framing Radius rotation-invariant (C++); debug phím U +
        Enable Input đã xóa. **P2 HOÀN TẤT VỀ TÍNH NĂNG (Gate A→F).** Xem DEVIATIONS mục
        "P2 — 21/07/2026 — Gate F".
- [x] **C4** — WBP_ComboCard + ghost + drag-drop + CalculateComboAnchor + CTV_ComboCard. Ghost offset FIXED (Approach B). ✅ 25/06/2026
- [x] **C5** ✅ DONE — 7 sub-task:
  - [x] C5.1 — C++ 3 helper (UpdateComboFolder/RenameFolderPrefix/ClearFolderPrefix) ✅ 25/06
  - [x] C5.0 — tree + filter browse ✅ DONE (26/06)
  - [x] WBP_LibraryContextMenu — Clone WBP_ContextMenu; Z-order fix D12 ✅ DONE (26/06)
  - [x] C5.2 — Inline rename folder: WBP_EditableLabel + WBP_TreeNode v1.3 + Inventory v3.3 ✅ DONE (27/06)
  - [x] C5.4 — Move Folder: WBP_MoveToFolderDialog + WBP_MoveFolderRow (mới) + S_FolderTargetEntry + WBP_FurnitureInventory v3.4 ✅ DONE (30/06)
  - [x] **Issue 2** — Chip highlight combo side: UpdateComboFolderHighlights() NEW (WBP_FurnitureInventory v3.5) ✅ DONE (01/07)
  - [x] **C5.5** — Move Combo: WBP_ComboCard v1.1 + WBP_FurnitureInventory v3.5 (OnComboCardRightClicked/CB_MoveCombo/HandleMoveComboConfirmed). BUG FIX 4.1/4.2/4.3. ✅ DONE (01/07)
  - [x] **NF** — Tạo folder mới: context menu action ✅ DONE (04/07) — C++ Folders.json+GetAllFolderPaths, WBP_FurnitureInventory v3.6 (helpers+OnRequestNewFolder+CB_CreateNewFolder). Nút "+" đầu cột tree (NF.G3) ✅ DONE (06/07) — sentinel `__NEWFOLDER__`, tái dùng OnRequestNewFolder.
  - [x] C5.6 — Xóa folder ✅ DONE (06/07) — WBP_ConfirmDialog mới + ClearFolderPrefix (đã có từ C5.1)
  - [x] C5.7 — ChipTag right-click + rename ✅ DONE — 7a (right-click+menu) DONE (06/07), 7b (inline rename, fallback tree→chip) DONE (06/07 tối). **C5 — FOLDER MANAGEMENT HOÀN TẤT.**
  - [x] **C5.8** — Folder Tree Picker Unify (Move Dialog + Save Dialog) ✅ DONE (13/07/2026) — 2d + Wire Move + Wire Save + REG (Khối A/B/C/D) toàn bộ DONE. 3 bug fix trong lúc build/test (BuildMoveFolderTargetList sót call site, SetSelectedHighlight sai biến, SetLabelColor type). 2 bug mới ghi Open_Bugs (ngoài scope, không sửa ở đây): Save dialog tên rỗng vẫn confirm được, Move Folder không check trùng tên đích. Plan: `docs/Sprints/Sprint5/C5.8_FolderTreePicker_Unify_Plan.md`.
    - [x] Task Card #1 (Data Layer) ✅ DONE (08/07) — rename `S_FolderTargetEntry`→`S_FolderTreeNode`, `BuildFolderTreeRecursive`+`GetFilteredChildren` mới, wrapper `BuildComboFolderTreeNodes` (tên đổi khác plan). Test Print PASS.
    - [x] Task Card #2 (UI component `WBP_FolderTreePicker`+`WBP_FolderPickerRow`, 2a→2d rename host) + Wire Move + Wire Save — build + test node-level ✅ DONE (13/07) — trả nợ test toàn bộ (M1-M6, S6a-c, 0.3, Phần 2 test 1-2).
    - [x] REG (Khối A/B/C/D, `C5.8_REG_TaskCard_11jul2026.md`) ✅ PASS (13/07) — chốt sổ C5.8.
- [x] **C6** — Favorite + Recent combo ✅ CHÍNH THỨC DONE HOÀN TOÀN (22/07/2026) — C6.1-C6.4
      (API/nút tim/hook Recent/tab hiển thị) test PASS bao gồm persist qua tắt/mở PIE (thực hiện
      trực tiếp trong UE5 Editor, không có node flow chi tiết trong doc). 2 bug fix: `AddRecentCombo`
      dead-end (`SaveUserPrefs` chỉ chạy khi Recent vượt cap 48, nhánh <48 dead-end — fix merge cả
      2 nhánh; cap thật=48 không phải 20 như `UX_Phase2_Plan.md`) + Recent hiển thị chỉ 1 card
      (`FilterByCategory` đổi `AddItem` loop → `Set List Items` batch). Ghi nhận backlog (không
      phải bug): duplicate `comboId` khi copy tay file JSON — xem `Bugs/Open_Bugs.md` mục
      "Note-DuplicateComboID". File mới: `Blueprints/BP_FurnitureUserPrefsManager.md`. Xem
      `01_Session_State.md` mục C6.
- [ ] **C7** — WBP_ComboDetailPopup (thumbnail thật) — **[DỜI → Sprint 6]** (31/07, theo
      `01_Session_State.md` 22/07 "C7 dời hẳn Sprint 6"). Loại khỏi mẫu số Sprint 5, tính vào
      Sprint 6.
- [x] **Field Kích thước Card** — DONE (22/07/2026)
- [x] **Delete Combo** — DONE (22/07/2026), 5/5 test PASS. `WBP_ComboCard.BTN_DeleteCombo` →
      `RequestDeleteCombo`/`HandleDeleteComboConfirmed`. (Ô mới thêm 31/07 — task đã DONE từ 22/07
      nhưng chưa từng có dòng checklist riêng.)
──── **Giai đoạn 2: đặt/thay combo mượt** ────
- [x] **WBP_Toast (K1)** — ✅ DONE (23/07/2026), 5/5 test PASS. `ShowToast`/`HideToast` + timer
      tự ẩn 2.5s + `Foff_GameInstance.ToastRef` global + `WBP_FurnitureInventory.ShowToastMsg`
      helper. 6 chỗ Print→Toast (folder/combo delete, move fail, create folder fail, spawn skip
      item). Xem `01_Session_State.md` mục K1.
- [x] **C8** — Drag-drop + surface-snap ✅ **MERGED vào C4** (24/06/2026)
- [ ] **Xoay combo (P3)** — verify gizmo group xoay cả cụm; tùy chọn xoay-lúc-kéo (R/scroll)
- [x] **C9** — Replace combo (+ verify K2 EMS SourceComboID + CalculateCenter chung + auto-rollback spawn-fail) — ✅ DONE (30/07/2026). Xem `01_Session_State.md` mục C9.
- [x] **Save As / Save đè combo** (T1-T5, xem `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md`) — ✅ ĐÓNG HOÀN TOÀN (08/08/2026, R-DOC-ATOMIC — T5 xong nên tử số +1, đủ điều kiện tick).
  - [x] T1 — `ResolveActiveComboForSave()` + `GetComboRootOfActor()` (`BP_FurnitureInputManager` v3.0). Test PASS 6/6. ✅ DONE (03/08/2026)
  - [x] T2 — Guard edit-scope cho re-route replace (`Bug-ReplaceInCombo-TabJump`). Test PASS 6/6. ✅ DONE (03/08/2026)
  - [x] T3 — 2 nút + trạng thái xám + tooltip (`WBP_SaveComboDialog`). Test PASS 6/6. ✅ DONE (07/08/2026)
  - [x] T4 — Ghi đè thật + xác nhận + thumbnail (`BP_ComboManager.SaveComboFromSelection` +2 param). Test PASS 6/6. ✅ DONE (07/08/2026)
  - [x] T5 — Regression + docs. Khối A (7 bước) + Khối B (S-Scan 12/12 ô) PASS toàn bộ. Khối D: D1 N/A (giới hạn engine), D2 fix xong. ✅ DONE (08/08/2026)
──── **Giai đoạn 3: share** ────
- [ ] **C11** — Export/Import cả 2 hướng (K5): file-save dialog TRƯỚC, fallback thư mục cố định
- [ ] **C10** — Regression (K4 nested-3 / P5-liên quan / VRAM stat rhi) + Docs
→ **Sprint 7** — Material name-based slot (P5 triệt để — mở màn)

**⚠️ Phiên 21/06:** Kiến trúc v2.0 chốt — scope mở rộng thành Combo Library đầy đủ.
**⚠️ Phiên 23/06:** P1(thumbnail C++)+P2(surface snap)+P3(xoay) làm scope phình → chia 3 giai đoạn. Deadline 25/06 chỉ xong Giai đoạn 1. Xem DEVIATIONS.md 23/06 + Sprint5_Plan_v1.1.
**Deviation:** xem DEVIATIONS.md Sprint 5 (21/06 + 23/06).

---

## SPRINT 6-7 — Chưa bắt đầu

---

## Lịch sử cập nhật

| Ngày | Nội dung |
|------|----------|
| 21/06/2026 | Sprint 5 T1+T2 DONE. Thêm entry Sprint 5. Phiên kiến trúc v2.0: thay T3-T8 bằng C0-C10, tổng Sprint 5 = 13 task, TỔNG 55/96 |
| 22/06/2026 | Sprint 5 C0 ✅ DONE — 3 case A/B/C PASS, RowName fallback xác nhận. |
| 23/06/2026 | Sprint 5 C1+C2 ✅ DONE. Chốt 11 quyết định + 3 điều chỉnh (Sprint5_Plan_v1.1). Thêm task: Fix K3, Thumbnail System C++, WBP_Toast, Xoay combo P3, C11 (trước C10). Chia 3 giai đoạn. TỔNG Sprint 5: 5/17. |
| 24/06/2026 | C3b ✅ DONE. C4 ⏳ 80%: WBP_ComboCard + ghost + drag-drop flow + CalculateComboAnchor + CTV_ComboCard (19 combo PASS). C8 ✅ MERGED vào C4. Bug OPEN: B-ghost-offset. TỔNG Sprint 5: 8/17 (C3a+C3b+C8 done). |
| 25/06/2026 | B-ghost-offset ✅ FIXED. C4 ✅ 100% DONE. C5.1 ✅: 3 C++ folder helpers. C5.0 ⏳ ~90%: tree PASS, card render bug open. TỔNG Sprint 5: 10/17 (C4+C5.1 done). |
| 26/06/2026 | C5.0 ✅ DONE: PopulateComboTreeColumn 2-cấp+D9 guard, OnComboTreeNodeRightClicked, WBP_LibraryContextMenu (Z-order D12). B-C5-card ✅ FIXED (Entry Widget Class verify). TỔNG Sprint 5: 12/17. |
| 27/06/2026 | C5.2 ✅ DONE: WBP_EditableLabel v1.0 (inline rename component). WBP_TreeNode v1.3 + WBP_FurnitureInventory v3.3. BUG FIX RefreshComboFolderUI +PopulateComboTreeColumn. 6 test PASS. TỔNG Sprint 5: 12/17 (task count unchanged — C5.0+WBP_LibraryContextMenu bundled). |
| 30/06/2026 | C5.4 ✅ DONE: Move Folder — WBP_MoveToFolderDialog + WBP_MoveFolderRow (mới). S_FolderTargetEntry struct mới. WBP_FurnitureInventory v3.4 (MovingFolderPath + CollectFolderTargets + BuildMoveFolderTargetList + OnRequestMoveFolder implement + CB_MoveFolderClick implement + HandleMoveFolderConfirmed NEW). BUG FIX D-C5.4-1 (Array_Append ngược) + D-C5.4-2 (dead-end nhánh True). Backlog reorder: Issue 2 → Move Combo → NewFolder → Xóa folder → ChipTag. TỔNG Sprint 5: 13/17. |
| 01/07/2026 | Issue 2 ✅ + C5.5 Move Combo ✅ DONE: UpdateComboFolderHighlights NEW (Issue 2). WBP_ComboCard v1.1 (InventoryRef + On Mouse Button Down). WBP_FurnitureInventory v3.5 (3 class var + OnComboCardRightClicked + CB_MoveCombo + HandleMoveComboConfirmed). BUG FIX 4.1/4.2/4.3. Learning_System v1.3. TỔNG Sprint 5: 15/19 (+2 backlog task). |
| 04/07/2026 | NF (New Folder) — context menu part ✅ DONE, nút "+" 🔲 CÒN NỢ: C++ GetEmptyFoldersFilePath→Folders.json + GetAllFolderPaths tự-ghi-bổ-sung (kể cả cấp cha) test PASS 6/6. BuildComboFolderTree đổi nguồn sang GetAllFolderPaths test PASS 4/4. WBP_FurnitureInventory v3.6: GetChildFolderNames/GetUniqueNewFolderName/GetNewFolderParent (helpers) + OnRequestNewFolder + CB_CreateNewFolder (tạo cùng cấp node right-click, tự vào rename mode) — test PASS 9/9. Deviation: dialog (NF.G2-G5 gốc) → SUPERSEDED bởi inline rename. TỔNG Sprint 5: 15/19 (NF chưa tính — còn nút "+"). |
| 06/07/2026 | NF.G3 ✅ + C5.6 ✅ + C5.7a ✅ DONE: nút "+" đầu cột tree (sentinel `__NEWFOLDER__`, test PASS 5/5). Xóa folder — WBP_ConfirmDialog mới (generic) + HandleDeleteFolderConfirmed + CB_DeleteFolderClick, Deviation D-C5.6-1 (nhảy về cha thay vì `__ALL__`), test PASS 6/6. ChipTag right-click — WBP_ChipTag v1.2 (+OnChipRightClicked + On Mouse Button Down) bind → OnComboTreeNodeRightClicked, test PASS 3/4 (rename = C5.7b, chưa làm). Refactor + bug fix phát sinh: RebuildChipRowForPath + RefreshChipBreadcrumb (gộp code trùng lặp + fix chip area không tự refresh) — 3 bug fix (dead-end 2/3 nhánh, delimiter sai, BooleanAND→OR); bug fix SelectedPath nhầm biến trong OnComboTreeNodeClicked. WBP_FurnitureInventory v3.7. TỔNG Sprint 5: 17/19 (NF.G3+C5.6 done, C5.7 partial — 7a done/7b nợ). |
| 06/07/2026 (tối) | C5.7b ✅ DONE — **C5 FOLDER MANAGEMENT HOÀN TẤT.** WBP_ChipTag v1.3 (EditLabel_ChipTag thay TextBlock, EnterRenameMode/HandleLabelCommitted, dispatcher OnChipRenameCommitted). WBP_FurnitureInventory v3.8 (RenameTargetChip + OnRequestRenameFolder fallback tree→chip + RebuildChipRowForPath bind). BUG FIX CB_CreateNewFolder (node SET thừa) + CB_RenameFolder (thiếu SET None). TỔNG Sprint 5: 19/19. |
| 07/07/2026 | **C5.8 — Folder Tree Picker Unify 🔲 PLANNED** (chưa tính vào task count): nhận delta kiến trúc v2 (Fable/Opus) — gộp lõi data (`BuildFolderTree`/`S_FolderTreeNode`) + component (`WBP_FolderTreePicker`/`WBP_FolderPickerRow`) dùng chung Move+Save dialog, thay `WBP_MoveFolderRow` + folder-field cũ Save. Slot chốt: NGAY SAU C5, TRƯỚC C9. Plan đầy đủ + 2 Task Card: `docs/Sprints/Sprint5/C5.8_FolderTreePicker_Unify_Plan.md`. Chưa thực thi. |
| 08/07/2026 | **C5.8 Task Card #1 (Data Layer) ✅ DONE** (chưa tính vào task count): rename `S_FolderTargetEntry`→`S_FolderTreeNode` (+4 field); `CollectFolderTargets`→`BuildFolderTreeRecursive` (depth guard=12) + `GetFilteredChildren` mới (Pure); wrapper `BuildComboFolderTreeNodes(ExcludePath)` — tên đổi khác plan gốc, log DEVIATIONS.md. Test Print PASS (8 combo, nested 3 tầng, tiếng Việt). WBP_FurnitureInventory v3.9. Tiếp theo: Task Card #2 (UI component). |
| 10-11/07/2026 | **C5.8 Task Card #2 (UI component)** (chưa tính vào task count): 2a `WBP_FolderPickerRow` (row tĩnh + guide line) ✅ PASS full data thật. 2b Part A (hierarchy BTN_Arrow/BTN_Name, dispatchers, `SetExpanded`) ✅ DONE. Part B lần 1 🔄 IN PROGRESS: Variables + toolbar + `SB_SearchFolder`, `IsPathVisible`, `RefreshVisibleRows`, `SetFolders` bug fix, 2 Custom Event handler DONE — **bug #2 OPEN** (test mục 2 FAIL, đang debug theo `docs/Sprints/Sprint5/C5.8_TaskCard2_FixPlan_11jul2026.md`). Doc mới: `WBP_FolderTreePicker.md` v0.9, `WBP_FolderPickerRow.md` v1.0. |
| 11/07/2026 13:14 | **C5.8 Task Card #2 Part B — Giai đoạn 1 ✅ DONE**: bug #2 root cause = `SetNode` thiếu `SET RowNode = Node` + `BTN_Arrow` không đồng bộ Visibility với `TXT_Arrow`. Fix xong (`WBP_FolderPickerRow.md` v1.1). Đính chính lần 2: as-built THẬT nối THẲNG `OnClicked→Call dispatcher`, KHÔNG Custom Event trung gian (đảo ngược [DOC-FIX] trước đó) — áp dụng cho cả BTN_Arrow/BTN_Name và 2 handler mới BTN_ExpandAll/BTN_CollapseAll (`WBP_FolderTreePicker.md` v1.0). Test mục 1-5 PASS. Tiếp theo: Giai đoạn 2 (search). |
| 12/07/2026 10:40 | **C5.8 Task Card #2 Part B — Giai đoạn 2 (Search) + Giai đoạn 3 (Select) ✅ DONE**: 3 Function mới trên `WBP_FolderTreePicker` (`PathMatchesQuery`/`BuildSearchOverride`/`GetParentPath`) + `RefreshVisibleRows` ghép xong nhánh search + wire `SB_SearchFolder.OnSearchTextChanged` (`WBP_FolderTreePicker.md` v1.1). `SetSearchHighlight(bMatch)` DONE trên `WBP_FolderPickerRow` (`WBP_FolderPickerRow.md` v1.2). Bug fix: `PathMatchesQuery` dùng nhầm `Path` đầy đủ thay `DisplayLabel`; arrow-click node đang match trong lúc search không lộ con (thêm `GetParentPath`). Test mục 1-10 PASS hết — **Task Card #2 Part B + 2c HOÀN TẤT.** Tiếp theo: Giai đoạn 4 (Chốt sổ — comprehension check còn nợ 2 câu) → 2d (rename host) → wire Move → wire Save + Create Folder → REG C5.8. |
| 13/07/2026 | **C5.8 Task Card #2 (2d rename host) + Wire Move + Wire Save — build + test node-level DONE** (chưa tính vào task count): `WBP_FolderPickerRow.md` v1.3 (`TXT_Name`→`EditableLabel_Name` + `EnterRenameMode`/`HandleLabelCommitted`/dispatcher `OnRowRenameCommitted`/`GetRowPath` (2d Phần 1); `TXT_CurrentTag`+`SetCurrentTag`/`SetSelectedHighlight` (Card 1)). `WBP_EditableLabel.md` v1.1 (`SetLabelColor`). `WBP_FolderTreePicker.md` v1.3 (`BeginRenameOnPath`/`ExpandToPath` (2d Phần 2); var `CurrentPath`/`bShowCurrentTag` + dispatcher `OnRequestCommitRename` (Card 1)). `WBP_MoveToFolderDialog.md` v2.0 + `WBP_SaveComboDialog.md` v2.0 — cả 2 chuyển hẳn sang dùng `WBP_FolderTreePicker` (xoá `WBP_MoveFolderRow`/`CMB_Folder` cũ, SUPERSEDED không xoá file). `WBP_FurnitureInventory.md` v3.11 — `OnRequestMoveFolder`/`CB_MoveCombo` gọi `Dialog.InitPicker`; `OpenSaveComboDialog` wire Picker + 2 Custom Event mới `HandleSaveDialogCreateFolder`/`HandleSavePickerRenameCommitted`; `BuildMoveFolderTargetList` xoá hẳn khỏi Blueprint. 3 bug fix phát hiện lúc test: `BuildMoveFolderTargetList` sót 2 call site (claim "Blueprint tự propagate" ở v3.9 SAI), `SetSelectedHighlight` so sai biến (CurrentPath thay SelectedPath), `SetLabelColor` type correction (Slate Color không phải Linear Color). Test PASS: M1-M6, S6a/S6c, 0.3, Phần 2 test 1-2. **REG C5.8 (regression cuối) CHƯA chạy — bước tiếp theo, sau đó mới cho phép sang C9.** |
| 13/07/2026 (REG) | **C5.8 — REG (Khối A/B/C/D) PASS — CHÍNH THỨC DONE.** A1-A7 PASS (A1 clarification wording task card), B1-B4 PASS (B4 scope note không live-sync), C1 SKIP (rủi ro thấp)/C2-C5 PASS (không VRAM leak), D5 comprehension check PASS. 2 bug mới ghi `Bugs/Open_Bugs.md` (ngoài scope, không sửa ở đây): Bug-SaveConfirm-EmptyName, Bug-MoveFolder-Collision. `WBP_MoveFolderRow.md` đánh dấu [SUPERSEDED]. **Roadmap: mở khóa C9 (Replace).** |
| 14/07/2026 | **P1 Combo Thumbnail — Gate G0-R DONE.** One-shot capture (G0 gốc) loại bỏ — ảnh xám phẳng do Lumen GI/TAA/auto-exposure chưa hội tụ đủ frame. Đổi kiến trúc: `BeginComboCapture`/`FinishComboCapture` + Custom Event `Delay` latent, thay hàm đồng bộ cũ (giữ `[LEGACY]`). Test debug phím T (`BP_ComboManager`) — chốt tạm Delay 3.0s. Checklist P1 mở rộng thành G0-R→G5, G0-R tick DONE. Xem `DEVIATIONS.md` [ARCH] 14/07/2026 + `01_Session_State.md` mục P1. |
| 14/07/2026 (P1 G1) | **P1 Combo Thumbnail — Gate G1 DONE.** `LoadComboThumbnail` thân hàm đầy đủ (PNG→IImageWrapper→GetRaw BGRA8→optional FImageUtils::ImageResize→UTexture2D::CreateTransient). Build PASS, test phím Y độc lập → size=256 đúng. Thêm module `ImageCore` (Build.cs) + include Engine/Texture2D.h, ImageUtils.h — không phải deviation (đúng plan gốc). Checklist P1.G1 tick DONE. Tiếp theo: G2 (auto-fit FitRatio + ẩn gizmo/outline + PostProcess). |
| 15/07/2026 | **P1 Combo Thumbnail — Gate G2+G3+G4 DONE.** Auto-fit + ẩn gizmo (G2). Cache thumbnail + fix bug nghiêm trọng "Function thiếu Return Node ở 1 nhánh → tái sử dụng output cũ, cross-combo thumbnail bleeding" (G3). Nối full vào Save/Load/Display flow, fix 2/3 bug dead-end phát hiện trong lúc wiring (G4). Delete combo xác nhận CHƯA implement (note cũ ghi nhầm C8). Xem `01_Session_State.md` mục P1 + `DEVIATIONS.md` 15/07/2026 cho chi tiết đầy đủ. |
| 16/07/2026 | **P2 plan v1.0 chốt** (Fable review ×2 vòng: 8 điểm mù M1-M8 + 4 lỗ hổng H1-H4). Kiến trúc: Remote Studio + H-B turntable + Key/Fill RectLight + Manual EV100. Gate A card v1.1 giao Sonnet. Plan: `docs/Plans/P2_StudioThumbnail_Execution.md`. |
| 17/07/2026 | **P2 Gate A DONE** — `SpawnComboForThumbnail(ComboID, DeltaYaw=0)` Custom Event mới (clone sạch: strip tag FurnitureSpawned, GroupID="", bAutoSelect/bAddToRecent=False) + chuỗi debug phím U (ground-align, BeginComboCapture/FinishComboCapture). `SpawnFurnitureCopy` +param `bAddToRecent`. Fix aliasing Add Actor World Offset (2 For Each Loop liên tiếp dùng nhầm Array Element). TEST PASS 6/7 case (case 7 dời Gate F). |
| 17/07/2026 (cuối phiên) | **P2 Gate B + Gate C DONE.** Gate B: dome hình học (`Cmb_StudioDomeRadius`) + Cast Shadow=False (quyết định kiến trúc quan trọng nhất — gỡ ràng buộc "đèn phải đứng trong dome"); màu dome S1 + faceting sphere dời đợt tối ưu cuối. Gate C: Function mới `SpawnStudioLight(AngleOffsetDeg, Intensity)` dùng chung cho Key/Fill RectLight (Mobility=Movable bắt buộc, Attenuation Radius=8000, elevation 45°); Manual EV100 qua `Get/Set members in Post Process Settings` (không dùng `Make`, tránh ghi đè Lumen override C++); camera H-B tick `bUseFixedAngle`. 12 bug/quyết định trong lúc làm Gate C (5 vòng đoán sai vị trí đèn trước khi Fable chỉ ra root cause = Cast Shadow) — chi tiết đầy đủ: `DEVIATIONS.md`. Verify PASS: 2 combo khác nhau → cùng góc + cùng độ sáng. Tiếp theo: Gate D (bóng + sweep hình dáng). |
| 19/07/2026 | **P2 Gate D prerequisite: Noise + Aliasing Fix DONE.** Ảnh thumbnail còn noise nặng sau lighting isolation (18/07) — `SceneCapture2D` không có temporal accumulation thực sự. Fix: `AccumulateComboFrame`/`ResetComboAccumulation` (C++ mới, `UComboThumbnail`) cộng dồn N=24 frame trong không gian linear color, mượn Event Tick `BP_ComboManager` (`Cmb_AccumFramesLeft`/`Cmb_AccumTargetFrames`); SSAA 2× supersample (RT 2048²) + box downscale, encode gamma đúng 1 lần cuối. Bug fix: sửa nhầm `CreateRenderTarget2D` bản [LEGACY]. Test: noise CONFIRM + aliasing/SSAA CONFIRM DONE. Task gốc Gate D (Source Size Key tune + sweep 5 combo) vẫn CHƯA bắt đầu. Chi tiết: `DEVIATIONS.md` mục "SPRINT 5 — 19/07/2026". |
| 20/07/2026 | **P2 Gate D: Rim Light + VRAM Fix DONE, sweep TẠM DỪNG.** Rim Light (3-point lighting, [SCOPE] mở rộng Gate C) qua `SpawnStudioLight` gọi lần 3 + biến mới `Cmb_StudioRimLight`; đổi `InVect`/SourceSize/AttenRadius cả 3 đèn + Post Process Exposure Compensation +6.0 — verify PASS ảnh combo To+Tường. Fix VRAM/GPU crash (EndPlay `BP_ComboManager`, 2 bug wiring: `Map_Clear` lồng sai nhánh Branch + thứ tự đọc/ghi `Cmb_CaptureHandle` khiến `ResetComboAccumulation` no-op) — verify bằng đọc code + export K2Node, CHƯA đo VRAM dài hạn. `Cmb_KeySourceSize`=500 chốt bằng mắt. Sweep 5 loại combo: 3/5 PASS (Nhỏ/To/Tường), phát hiện 2 bug kiến trúc MỚI — (1) dome cong nuốt chân đồ footprint rộng (sofa PASS thẩm mỹ nhưng lộ bug, thảm FAIL nặng); (2) combo "Cao" (Ceiling) dính lỗi ground-align giống Tường (H1) nhưng chưa từng ghi trong plan. **Gate D TẠM DỪNG — chờ Fable/Opus quyết kiến trúc** (đảo ngược 1 phần quyết định Gate B) trước khi tiếp tục. Chi tiết: `DEVIATIONS.md` mục "P2 — 20/07/2026", `Bugs/Open_Bugs.md` (2 bug mới), `Blueprints/Blueprint_Logic_NodeFlow.md` v1.11. |
| 21/07/2026 | P2 (Studio Thumbnail) — Gate F DONE, P2 hoàn tất về tính năng. Nối Studio pipeline vào SaveComboFromSelection thật (thay capture in-place P1): Custom Event mới BeginThumbnailCapture + SetPendingUserCamYaw; class var Cmb_StudioCamYaw(55)/Cmb_PendingUserCamYaw/Cmb_PendingCaptureComboID/Cmb_DebugLastCaptureDistance; Bước 7 gọi BeginThumbnailCapture(DeltaYaw=StudioCamYaw−PendingUserCamYaw); Broadcast dời sang Event Tick tail; bearing camera→combo (FindLookAtRotation) thay Camera Rotation thẳng. Fix framing: Radius bounding rotation-invariant (C++ BeginComboCapture, 235vs282→248vs263). Hệ quả phụ: Save thật hết bug ảnh 2048² thô. Debug phím U + Enable Input đã xóa. Backlog: VRAM regression SSAA 2048² + Feature-CanonicalStudioAngle (Sprint 6). Chi tiết: Delta_P2_GateF_21jul2026, BP_ComboManager v1.10, DEVIATIONS 21/07. |
| 22/07/2026 | **C6 (Favorite + Recent combo) — CHÍNH THỨC DONE HOÀN TOÀN.** C6.1-C6.4 (API/nút tim/hook Recent/tab hiển thị) test PASS bao gồm persist qua tắt/mở PIE (thực hiện trực tiếp trong UE5 Editor, ngoài phiên Claude Code — không có node flow chi tiết trong doc). 2 bug fix: (1) `AddRecentCombo` dead-end — `SaveUserPrefs` chỉ chạy khi Recent vượt cap 48 phần tử (nhánh `False` <48 không nối gì) → fix merge cả 2 nhánh; cap thật = 48, không phải 20 như `UX_Phase2_Plan.md` ghi (sai lệch tài liệu). (2) Recent hiển thị chỉ 1 card — `FilterByCategory` đổi `AddItem` loop → `Set List Items` batch (giống Favorite/All), bài học ghi vào skill `ue5-blueprint-rules` L12. Ghi nhận backlog (không phải bug): duplicate `comboId` khi copy tay file JSON — xử lý khi làm Save As/Save đè. File mới: `Blueprints/BP_FurnitureUserPrefsManager.md`. Chi tiết: `Bugs/Open_Bugs.md` mục "Note-DuplicateComboID", `01_Session_State.md` mục C6. Tiếp theo: **C7 — WBP_ComboDetailPopup**. |
| 23/07/2026 | **K1 (WBP_Toast) — DONE, 5/5 test PASS.** Widget mới `WBP_Toast` (`ShowToast`/`HideToast` + timer tự ẩn 2.5s) + `Foff_GameInstance.ToastRef` (global access) + `WBP_FurnitureInventory.ShowToastMsg` (helper, fallback Print). 6 chỗ Print→Toast: `CreateNewFolderFlow`, `HandleDeleteFolderConfirmed`, `HandleMoveComboConfirmed`, `HandleDeleteComboConfirmed` (×2 nhánh), `SpawnComboByID` Sub-step C (Row Not Found — mới thêm, trước dead-end trần trụi). Đính chính as-built: `OnRequestNewFolder` chỉ gọi Function riêng `CreateNewFolderFlow` (doc cũ mô tả sai); sửa 2 annotation `[gate bDebugMode]` sai/lỗi thời. Tiếp theo: **C9 (Replace Combo)**. Chi tiết: `01_Session_State.md` mục K1, `Widgets/WBP_Toast.md` (mới). |
| 24/07/2026 | **C9.0c (Migrate E_ReplaceTarget) — HOÀN TẤT, 5/5 test regression PASS, 6/6 file compile sạch.** Prereq cho C9 (Replace Combo) — không phải bản thân C9. Migrate `bIsReplaceMode`→`ReplaceTarget` (Enum None/Mesh/Combo) trên `BP_FurnitureInputManager` + `WBP_FurnitureInventory`, xảy ra ngoài phiên Claude Code, ghi nhận qua K2Node export thật. Pure Function mới `IsReplaceModeActive()`. 3 bug fix (CB_Replace Branch dư, WBP_DetailPopup.BTN_ChangeMesh SET nhầm biến dead + refactor gọi thẳng StartReplaceMode, WBP_FurnitureCard.Get_Button_ChangeMesh_Visibility binding đọc biến đã xóa) + dọn dead code trùng tên trên WBP_ComboCard. Tiếp theo: **C9 (Replace Combo, tính năng thật)**. Chi tiết: `01_Session_State.md` mục C9.0c. |
| 30/07/2026 | **C9 (Replace Combo) — DONE.** C9.b–C9.f + 3 bug fix (Bug B, Bug A2, folder-highlight/chip) — tất cả test pass. 1 test-debt: nhánh DA legacy (save cũ) chưa verify, dồn sang C10 (Regression). Tiếp theo: **Save As / Save đè combo** (UX chưa chốt). Chi tiết: `01_Session_State.md` mục C9, `Bugs/Open_Bugs.md`. |
| 31/07/2026 (Doc-Sync) | **Doc-Sync pass: sửa bar đếm trôi lệch từ 01/07, thiết lập R-DOC.** Bar TỔNG QUAN Sprint 5 đứng im ở `15/19` suốt từ 01/07 dù nhiều task đã DONE sau đó (C5.6/C5.7/C5.8/K1/C6/Field Kích thước Card/Delete Combo/C9) — đếm lại theo checklist thật: `16/22` (tick thêm Fix K3, C5 parent, C9; thêm ô mới "Delete Combo" chưa từng có checklist riêng dù DONE từ 22/07; gỡ nhãn "chưa tính vào task count"). **XÓA** dòng `C5` trùng lặp/lỗi thời ("Folder tree tab 🧩 Combo trong WBP_FurnitureInventory") khỏi checklist — tàn dư trước khi C5 tách C5.0-C5.8, không còn ý nghĩa. **C7** đánh dấu `[DỜI → Sprint 6]`, bỏ khỏi mẫu số Sprint 5, cộng vào Sprint 6 (`0/14`→`0/15`) — theo quyết định `01_Session_State.md` 22/07 (chưa từng phản ánh vào PROGRESS.md checklist). TỔNG: `62/96`→`72/102` (không đổi thêm ở bước C7 vì chuyển ngang mẫu số giữa 2 sprint). `DEVIATIONS.md` bổ sung entry thiếu "Bug B" (EnterReplaceMode) vào mục "C9 Replace — 30/07/2026" (Session_State đã ghi nhưng DEVIATIONS sót). Thiết lập luật `R-DOC-COUNT`/`R-DOC-OWNER`/`R-DOC-PASS` (+ dòng đơn vị đếm/dời sprint theo yêu cầu cuhoang) — `Rules/Execution_Discipline.md` v3.0. Nguồn: `Delta_DocSync_31jul2026.md`, chỉnh theo phản hồi cuhoang 31/07. |
| 01/08/2026 (Replace UX Fix) | **Replace UX Fix — bắt đầu.** Bug-fixing round trên **C9 (Replace Combo)** đã DONE 30/07 — dogfood sau khi ship phát hiện 6 bug UX (#1/#3a/#3b/#4/#5/#6). Phase 0 DONE 5/5. P1.2 (#3b — chiptag không rebuild/highlight đúng khi combo-replace) + P3.2 (#3a — inventory không tự mở lại từ minimize khi combo-replace) DONE, test PASS PIE. Không phải task mới trong checklist Sprint 5 — bug-fix round trên ô C9 đã tick, không đổi bar đếm. Chi tiết: `01_Session_State.md` (entry 01/08/2026). |
| 02/08/2026 (Replace UX Fix) | **Replace UX Fix (P0→P5) — ✅ ĐÓNG. C9 (Replace Combo) nay hoàn tất luôn phần UX.** P1.3 (#5 — card container theo mode), P2 (#4 — re-route Mesh↔Combo giữa chừng Replace; root cause thật: thiếu guard `IsValid(SelectedActor)` trong `OnMeshSelected`, không phải doc-drift như nghi ban đầu), P3.1 (#1 — `BTN_ChangeCombo` gate Visibility), P4 (đường ngược Luật 6A + xóa dead code `MeshToReplace` số ít) đều DONE. 6 bug gốc (#1/#3a/#3b/#4/#5/#6) rụng hết. P5.1 (#2 — chỉ báo Replace mode) dời Sprint 6; P5.2 (DA legacy path) gác lại — thiếu file save cũ để test. Không đổi task count Sprint 5 (bug-fix round trên C9, không phải task mới — xem ghi chú recount trong TỔNG QUAN). Chi tiết: `Widgets/WBP_FurnitureInventory.md` v3.19, `Blueprints/BP_FurnitureInputManager.md` v2.8, `DEVIATIONS.md` mục "Replace UX Fix — P0→P5 HOÀN TẤT — 02/08/2026", `Bugs/Open_Bugs.md`, `01_Session_State.md`. |
| 02/08/2026 (Q9 + 3 bug Surface) | **Luật Q9 (S-Matrix Gate) thiết lập** (`Rules/AI_Implementation_Rules.md` v2.14) + 3 bug mới xác nhận bằng test tay (Bug-MaterialPrimaryOnly, Bug-PasteVerticalCollapse, Bug-StaleSurfaceType — `Bugs/Open_Bugs.md`). Không đổi task count (không phải task Sprint 5, không backfill S-Scan cho task đã DONE). Cả 3 bug dời sau Gate 2, **KHÔNG đổi thứ tự ưu tiên: Save As/Save đè → C11 → C10 → Gate 2.** Chi tiết: `01_Session_State.md`, `DEVIATIONS.md` mục "Q9 S-Matrix Gate + 3 bug Surface — 02/08/2026". |
| 02/08/2026 (R-DOC-DONE) | **Luật mới `R-DOC-DONE` thiết lập + P2/P1 tick DONE, bar 16/22→18/22.** Quyết định cuhoang: P2 (Studio Thumbnail) = DONE — sửa mâu thuẫn nội bộ đã báo cáo (dòng checklist Gate D/Gate D-sub vs dòng "P2 HOÀN TẤT VỀ TÍNH NĂNG" cùng file). Case Cao (Ceiling, Gate D) tách thành `Bugs/Open_Bugs.md` mục "Task-P2-SweepCao" (🟢 Thấp, không chặn Gate 2), không giữ task Gate D mở. Áp cùng luật cho P1 (Thumbnail System C++): G0-G4 xong, chỉ G5 (VRAM regression) deferred → tick DONE, G5 tách `Bugs/Open_Bugs.md` mục "Task-P1-VRAMRegression". Dòng mồ côi "CHƯA bắt đầu." (cuối mô tả P2.Gate F) không xác định được thuộc mục nào → XÓA. Chi tiết: `Rules/Execution_Discipline.md` mục R-DOC-DONE, `DEVIATIONS.md` mục "[DOC-DEBT đã đóng] PROGRESS.md P2 self-contradiction — 02/08/2026". |
| 02/08/2026 (R-DOC-DONE tiếp) | **Chốt 2 câu hỏi từ VIỆC 5 (quét lan).** Sweep Cao (sub-item dưới `P2.Gate D`) tick `[x]` + trỏ sang `Task-P2-SweepCao` — bar KHÔNG đổi (sub-item, không phải task top-level, vẫn 18/22). `C3` KHÔNG tick — chỉ sửa TEXT mô tả tách rõ 3 phần độc lập đang gộp chung 1 ô: (1) Save dialog ĐÃ XONG qua C3b, (2) móc capture thumbnail sau save ĐÃ XONG qua P2 Gate F, (3) P4 LOCALAPPDATA CHƯA LÀM (phần duy nhất còn lại). Thêm luật mới `R-DOC-ATOMIC` (1 ô = 1 việc tick độc lập; ô gộp nhiều việc chỉ tách lúc recount mẫu số đầu sprint kế tiếp, không tách giữa sprint) — `Rules/Execution_Discipline.md`. Chi tiết: `DEVIATIONS.md` mục "[DOC-DEBT] C3 gộp 3 việc — 02/08/2026". |
| 02/08/2026 (Lô D — CrossCheck follow-up) | **Đóng các mục từ CrossCheck_PreGate2 có nguồn thật.** Viết doc `ResolveSelectedComboRoot()` vào `BP_FurnitureInputManager.md` (K2Node export thật, cuhoang cung cấp — đóng MỤC 4 báo cáo). Ghi `[DOC-DRIFT]` `PrimarySelectedActor` vs `SelectedActors[0]` vào `DEVIATIONS.md` — chưa đóng, chờ task card Save As/Save đè, KHÔNG sửa `Plans/24-07-2026_C9_Execution_Plan.md` (đã đóng dấu as-built). Củng cố đóng MERGE_LOG Q3 (`FindGroupData` không Index) bằng nguồn độc lập thứ 2 + sửa thêm `BP_UndoManager.md` v1.13, `Blueprint_Logic_NodeFlow.md` v1.15 (cả 2 tự mâu thuẫn nội bộ, sót từ lần sửa trước). Không đụng: 3 mục [?] còn treo, MỤC 5 canonical lạc hậu, 3 open item C9 khác (RowNotFound/guard Length==0/`bIsReplaceMode` dòng 276) — cần K2Node export riêng. Chi tiết: `00_Core/MERGE_LOG.md`, `00_Core/DEVIATIONS.md`. |
| 02/08/2026 (Lô E — ĐÓNG ĐỢT DỌN DOCS) | **Chốt Sprint 4 + tổng kết cả đợt (Lô A→E).** Đóng dấu thứ 3 `⚠️ [AS-BUILT TẠI THỜI ĐIỂM SPRINT 4]` cho `Sprints/Sprint4/Execution.md` + `Sprints/Sprint4/BugFix_Execution.md` — KHÔNG sửa chữ ký `FindGroupData` cũ bên trong (viết lại lịch sử = mất dấu vết quyết định gốc). Thêm bảng "3 LOẠI DẤU DOC" vào `MERGE_LOG.md` (phân biệt `[HISTORICAL]`/`[CHỨA AS-BUILT]`/`[AS-BUILT TẠI THỜI ĐIỂM X]`). Xác nhận `BP_FurnitureInputManager_MERGED_v1.9.md` **vẫn còn tồn tại** (đánh dấu xóa từ 17/06/2026, chưa ai xóa thật) — báo cáo, không tự xóa. Tạo `00_Core/DocCleanup_Summary_02aug2026.md` tổng kết toàn bộ: 4 luật mới (Q9/R-DOC-DONE/R-DOC-ATOMIC/R-DOC-ASBUILT), 3 loại dấu doc, danh sách còn treo (3 mục [?], MỤC 5 canonical lạc hậu ưu tiên `GetCombosDir`→C11, 3 open item C9, quyết định `ResolveSelectedComboRoot` chặn Save As/Save đè) — **không cái nào chặn Gate 2**. **Đợt dọn docs KẾT THÚC.** |
| 02/08/2026 (Lô E, tiếp) | **`BP_FurnitureInputManager_MERGED_v1.9.md` — XÓA THẬT** (quyết định cuhoang, sau khi entry trên báo cáo file vẫn còn tồn tại). Bản backup v1.9 vs canonical v2.9 chênh 10 phiên bản — rủi ro đọc nhầm cao hơn giá trị lưu trữ, lịch sử đã có trong git. Đã kiểm + sửa mọi link trỏ tới file sang canonical (`BP_FurnitureInputManager.md`, `MERGE_LOG.md`, `00_INDEX.md`). Chi tiết: `MERGE_LOG.md` mục "File đã xóa". |
| 07/08/2026 (T3 DONE) | **Save As/Save đè T3 (`WBP_SaveComboDialog`) — ✅ ĐÓNG.** Tick `[x]` sub-item T3 trong checklist Save As/Save đè. Bar Sprint 5 KHÔNG đổi (18/23 — R-DOC-ATOMIC, tử số item cha `[~]` chỉ +1 khi T5 xong). 4 việc chính (`RefreshButtonStates`/`ValidateComboName`/`Event Construct`/`BTN_Overwrite.OnClicked`, `WBP_SaveComboDialog` v2.1) + 1 việc phát sinh (Việc 5 — `Picker.SelectedPath`/`RefreshVisibleRows`, `WBP_FurnitureInventory` v3.21). Đóng `Bug-SaveConfirm-EmptyName`. Test PASS 6/6 case + 2 câu hiểu bài. ⚠️ Nhân tiện phát hiện + backfill hạ tầng 7b/7c (2 Function mới `GetComboViewByID`/`BuildSaveDialogPrefill`, 8 Expose-on-Spawn, `Border_OverwriteWrap`+`BTN_Overwrite`) CHƯA từng được phân phối vào doc canonical trước đợt này — xem cảnh báo mâu thuẫn trong `Widgets/WBP_FurnitureInventory.md` v3.21 + báo cáo merge 07/08/2026. Tiếp theo: **T4** (ghi đè thật). Chi tiết: `01_Session_State.md`, `Bugs/Open_Bugs.md`. |
| 07/08/2026 (T4 task card) | **Save As/Save đè T4 — task card phát hành, CHƯA thực thi.** Nguồn `DELTA_07-08-2026_T4_Overwrite.md` (Opus) → `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 7d (v1.6→1.7). Phạm vi: `BP_ComboManager.SaveComboFromSelection` (+2 param, Branch Bước 5a) · `WBP_SaveComboDialog.BTN_Overwrite` (dispatcher `OnDialogConfirmedOverwrite`) · `WBP_FurnitureInventory` (handler `HandleSaveComboOverwriteConfirmed` + toast). Q9 S-Scan+X-Check riêng cho T4 (không kế thừa T3) — bắt landmine S8 (Mix → nuốt hết mesh rời vào combo). RECOUNT R-DOC-COUNT: bar Sprint 5 vẫn đúng `18/23` (T4 chưa tick vì chưa thực thi). Thêm backlog `Task-T4.5-AutoGroupAfterOverwrite` (`Bugs/Open_Bugs.md`, chưa mở, không tính mẫu số). KHÔNG đụng `DEVIATIONS.md` (chưa có lệch thực thi — quyết định kiến trúc đã nằm sẵn trong task card 7d). Chi tiết: `01_Session_State.md`, `02_Current_Sprint.md`. |
| 07/08/2026 (T4 DONE) | **Save As/Save đè T4 (Overwrite Flow) — ✅ ĐÓNG.** Tick `[x]` sub-item T4. 3 Việc: `BP_ComboManager.SaveComboFromSelection` (+2 param, Branch 5a, `InvalidateThumbnail` Tick tail vô điều kiện) · `WBP_SaveComboDialog.BTN_Overwrite` (dispatcher `OnDialogConfirmedOverwrite`) · `WBP_FurnitureInventory` (`HandleSaveComboOverwriteConfirmed` + toast "Đã ghi đè combo"). Test PASS 6/6 case (bao gồm S8 mix combo+mesh rời) + 2 câu hiểu bài. Tiếp theo: T5. Chi tiết: `01_Session_State.md`. |
| 08/08/2026 (T5 DONE) | **Save As/Save đè T5 (Regression + Doc Closure) — ✅ ĐÓNG. Tính năng Save As/Save đè (T1-T5) CHÍNH THỨC DONE HOÀN TOÀN.** Tick `[x]` sub-item T5 + item cha (R-DOC-ATOMIC, tử số +1: 18→19). Khối A (regression 7 bước A1-A7) PASS toàn bộ — A1 xác nhận combo lưu trước Sprint 5 vẫn load được, A4+A5 xác nhận Save As luôn sinh `comboId` mới. Khối B (S-Scan S0-S9 + S8b + Q9-gap) PASS 12/12 ô đúng kỳ vọng — Q9 S-Matrix Gate cho tính năng này chính thức đóng. Khối C: đóng `Note-DuplicateComboID`. Khối D: D1 (bỏ Pass-by-Reference param `Tags`) **N/A — giới hạn engine** (`Tags` là Set of String, Blueprint khóa cứng không toggle được, không phải lỗi thao tác), ghi `DEVIATIONS.md`; D2 (`Bug-ComboCategoryHardcode`) FIX xong, verify `.json` ra `"category": ""`. `[CEILING]` combo root ("2 nơi cùng biết cách leo combo root") GIỮ NGUYÊN treo, trigger vẫn là C10. Tiếp theo: **C11** (Export/Import combo). Chi tiết: `01_Session_State.md`, `Sprints/Sprint5/Combo_Execution.md`, `Bugs/Open_Bugs.md`. |
| 10/08/2026 (P4-early + C11 DONE) | **P4-early DONE:** `GetCombosDir()` đổi sang `%LOCALAPPDATA%/InteriorFOFFTool/Combos` (combo sống qua update app đóng gói) — migrate tay từ `Saved/Combos/*` thành công, verify 3/3 ô PASS. **C11 (Export/Import combo) DONE HOÀN TOÀN:** qua thư mục `Exports/` (P4-early áp trước). C++ +4 hàm (`GetExportsDir`/`ExportCombo`/`ImportCombo`/`ImportAllFromExportsDir`). Export: context menu ComboCard "📤 Xuất file…", 3/3 test PASS. Import: nút `BTN_ImportCombo` riêng (không context menu — sai ngữ cảnh), 4/4 test PASS. 2 bug phát hiện+fix lúc test: (1) thiếu `Set Input Mode Game and UI` ở `CB_ExportCombo` — camera bị khóa sau export; (2) `CallDelegate` Target phải là `ComboManagerRef` không phải `self`. Doc-drift `CB_MoveCombo`/`OnComboCardRightClicked` cũng được sửa trong phiên này (`MovingComboID` xác nhận vị trí SET đúng). Tiếp theo: C10 (Regression full Sprint 5) → Gate 1.5 (Packaged Smoke). Nguồn: session 10/08/2026, `DELTA_10-08-2026_C11_P4early.md` + patch UX Import. |
| 14/08/2026 (C10 DONE) | C10 Regression tổng Sprint 5 — ✅ ĐÓNG. Khối A/B/C hoàn tất, xem 01_Session_State.md. Bar Sprint 5: 19/23 → 22/23. SPRINT 5 CHÍNH THỨC DONE (P3 Xoay combo defer sau Gate 1.5, không chặn). Tiếp theo: fix Bug-ComboRoot-MixedLooseGroup (đầu Sprint 6) → Gate 1.5 (Packaged Smoke). |
| 05/09/2026 | Sprint 7 S7.G2 ĐÓNG (Bước 0 + Việc 1-5, test tổng 7/7 PASS). Sang G3. |
