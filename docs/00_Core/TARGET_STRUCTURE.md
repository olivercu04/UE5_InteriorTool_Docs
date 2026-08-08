# TARGET_STRUCTURE — Bản đồ chuẩn docs/ (UE5_InteriorTool_Docs)
**Version:** 2.0 — 07/08/2026 (xem Changelog cuối file) | thay v1.x (~06/2026, drift nặng)
**Mục đích:** nguồn duy nhất quy định mọi file docs đặt ở đâu, tên gì. Claude Code đọc file này
TRƯỚC khi merge/tạo file. KHÔNG tự suy diễn path khác.
**Nền dữ liệu:** `git ls-files docs/` (07/08/2026, 114 file) — cây mục 2 = 100% cây đĩa thật.

---

## 1. QUY ƯỚC ĐẶT TÊN

- **Canonical asset docs** (`Blueprints/` `Widgets/` `Data/` `Rules/`): tên file = **đúng tên asset UE5** (BP_*, WBP_*, S_*, DT_*) hoặc tên khái niệm. **KHÔNG** date/version trong tên. Một logical asset = một file docs duy nhất. Không có "_patch"/"_update"/"_v1_x".
- **Tài liệu theo-thời-điểm** (`Plans/` `Sprints/`): **ĐƯỢC** dùng ngày/mã task trong tên (`03-08-2026_...`, `C5.8_..._11jul2026`) — bản chất là mốc thời gian, không phải asset. Đây là **ngoại lệ có chủ đích** so với gạch đầu dòng trên (sửa 07/08: v1.x cấm date mọi nơi — mâu thuẫn thực tế).
- Date + version của canonical asset docs sống trong: (a) header file, (b) bảng "Lịch sử cập nhật" cuối file, (c) git history.
- Prefix số (00_, 01_) chỉ ở `00_Core/` và bộ có thứ tự đọc (`Planning/` 00→07).
- **`README.md` cấp thư mục hợp lệ** ở mọi nhánh (mô tả thư mục đó) — không tính là trùng logical name.
- File hợp nhất từ nhiều nguồn: header `**HỢP NHẤT TỪ N file:** ...` + bảng "Lịch sử cập nhật".

---

## 2. CÂY THƯ MỤC (114 file — as-of 07/08/2026)

```
docs/
├── 00_Core/                              ← đọc mỗi đầu session
│   ├── 00_INDEX.md
│   ├── 01_Session_State.md               ← đọc TRƯỚC TIÊN mỗi session
│   ├── 02_Current_Sprint.md
│   ├── PROGRESS.md
│   ├── DEVIATIONS.md
│   ├── MERGE_LOG.md                      ← log hợp nhất + 3 loại dấu doc (HISTORICAL/AS-BUILT)
│   ├── RAW_INVENTORY.md                  ← kiểm kê import_raw/
│   ├── TARGET_STRUCTURE.md               ← (file này)
│   ├── README.md
│   ├── CrossCheck_PreGate2_02aug2026.md          ← report 1 lần — ứng viên Archive sau Gate 2
│   ├── DocCleanup_Summary_02aug2026.md            ← report 1 lần — ứng viên Archive sau Gate 2
│   └── Doc_Update_SprintD_Close_TreeNodeHighlight.md ← report 1 lần — ứng viên Archive sau Gate 2
├── Rules/                                ← canonical, KHÔNG date trong tên
│   ├── Workflow.md
│   ├── Project_Instructions.md
│   ├── AI_Communication_Rules.md
│   ├── AI_Implementation_Rules.md        ← Q8/Q9 + L1-L11 + bảng node
│   ├── Execution_Discipline.md           ← 6A/6B + R-DOC-*
│   ├── Learning_System.md
│   ├── Design.md
│   ├── Antipatterns.md
│   ├── Performance.md
│   └── README.md
├── Blueprints/                           ← canonical, 1 asset = 1 file
│   ├── BP_FurnitureInputManager.md       ← ⭐ Core: Selection/Gizmo/Group/Clipboard
│   ├── BP_UndoManager.md
│   ├── BP_GizmoController.md
│   ├── BP_PivotActor.md
│   ├── BP_FurnitureActor.md
│   ├── BP_FurnitureSceneManager.md
│   ├── BP_FoffPlayerController.md
│   ├── BP_ComboManager.md                ← Sprint 5 — save/spawn/replace combo
│   ├── BP_ComboItemView.md               ← Sprint 5 — Object bọc FComboData cho CTV_ComboCard
│   ├── BP_ComboGhostActor.md             ← Sprint 5 — ghost preview lúc drag combo
│   ├── BP_FurnitureUserPrefsManager.md   ← Sprint 5 (C6) — Favorite/Recent [THÊM 07/08]
│   ├── Blueprint_Logic_NodeFlow.md       ← notation guide đọc node flow
│   ├── README.md
│   └── Flows/
│       ├── Nudge_Flow.md
│       └── CopyPaste_Flow.md
├── Widgets/                              ← canonical, 1 asset = 1 file
│   ├── WBP_FurnitureInventory.md         ← ⭐ Core UI
│   ├── WBP_MeshControls.md
│   ├── WBP_DragOverlay_FurnitureCard.md
│   ├── WBP_BoxSelectOverlay.md
│   ├── WBP_DetailPopup.md
│   ├── WBP_ResizeWindow.md
│   ├── WBP_FurnitureCard.md              ← [THÊM 07/08]
│   ├── WBP_TreeNode.md                   ← Sprint 5 (C5.0)
│   ├── WBP_ChipTag.md                    ← Sprint 5 (C5.0)
│   ├── WBP_LibraryContextMenu.md         ← Sprint 5 (C5.0)
│   ├── WBP_EditableLabel.md              ← Sprint 5 (C5.2)
│   ├── WBP_ComboCard.md                  ← Sprint 5 (C4) [đã tách file — gỡ nhãn CHƯA TÁCH cũ 07/08]
│   ├── WBP_FolderTreePicker.md           ← Sprint 5 (C5.8)
│   ├── WBP_FolderPickerRow.md            ← Sprint 5 (C5.8)
│   ├── WBP_MoveToFolderDialog.md         ← Sprint 5
│   ├── WBP_MoveFolderRow.md              ← [SUPERSEDED] bởi WBP_FolderPickerRow — giữ, không xóa
│   ├── WBP_SaveComboDialog.md            ← Sprint 5 — dialog Save As/Save đè
│   ├── WBP_ConfirmDialog.md              ← [THÊM 07/08]
│   ├── WBP_Toast.md                      ← [THÊM 07/08] — toast thông báo
│   └── README.md
├── Data/                                 ← canonical concept/reference docs
│   ├── Data_Overview.md                  ← [THÊM 07/08 — diff cũ bỏ sót]
│   ├── Data_Structures.md                ← FComboData/FComboGroupData/S_* struct
│   ├── ComboSerializer_Reference.md      ← Sprint 5 — GetCombosDir, ComboToJson/JsonToCombo
│   ├── FurnitureFilterLibrary_Reference.md ← C++ plugin — vị trí file thật + signatures
│   ├── FilterByCategory_Logic.md
│   ├── FilterBySearch_Logic.md           ← [THÊM 07/08 — diff cũ bỏ sót]
│   ├── Python_Scripts.md                 ← [THÊM 07/08 — diff cũ bỏ sót] — thumbnail/catalog scripts
│   └── README.md
├── Features/                             ← [THÊM 07/08 — cả thư mục vắng khỏi cây cũ] tài liệu tính năng
│   ├── ChangeMaterial.md
│   └── Material_CopyPaste.md
├── Bugs/
│   ├── Open_Bugs.md                      ← bug/deferred-task đang treo
│   ├── Bug_GPU_VRAM_Crash.md
│   └── README.md
├── Plans/                                ← [THÊM 07/08 — cả thư mục vắng khỏi cây cũ] plan theo-thời-điểm
│   ├── 03-08-2026_SaveAsOverwrite_Execution_Plan.md ← ĐANG CHẠY (Sprint 5, T1-T5+T4.5)
│   ├── 24-07-2026_C9_Execution_Plan.md              ← 📌 [CHỨA AS-BUILT]
│   ├── P1_ComboThumbnail_Execution.md               ← 📌 [CHỨA AS-BUILT]
│   ├── P2_StudioThumbnail_Execution.md              ← 📌 [CHỨA AS-BUILT]
│   ├── 01-08-2026_Phase0_Verify_Report_ReplaceUXFix.md ← 📌 [CHỨA AS-BUILT]
│   ├── 01-08-2026_ReplaceUX_Fix_Execution_Plan.md   ← canonical ReplaceUX (v1 ở Archive/)
│   ├── Post_C5_Execution_Plan_v1.md
│   └── Sprint7_MaterialEdit_Plan_v1.1.md            ← plan Sprint 7 (chưa mở)
├── Planning/                             ← tài liệu kiến trúc nền (nhiều file [HISTORICAL])
│   ├── 00_Master_Plan.md
│   ├── 01_Current_Architecture_Audit.md
│   ├── 02_Target_Architecture.md
│   ├── 03_Code_Inheritance_Strategy.md   ← ⚠️ [HISTORICAL]
│   ├── 04_Sprint_Details.md              ← ⚠️ [HISTORICAL]
│   ├── 06_Risk_Mitigation.md
│   ├── 07_Testing_Strategy.md
│   ├── Architecture_Overview.md
│   ├── Backend_Plan.md                   ← Supabase + R2, Phase B
│   ├── Future_Architecture_1M_Assets.md
│   ├── Integration_Guide.md
│   ├── MultiSelect_Group_ComboMesh_Plan.md ← ⚠️ [HISTORICAL] as-built=Sprints/Sprint5/Combo_Execution.md [đóng [?] treo MERGE_LOG 07/08]
│   ├── Plugin_Migration_Guide.md
│   ├── Tech_Defaults.md
│   ├── UE5_InteriorTool_Overview.md
│   └── i18n_Plan.md
├── Sprints/                              ← log/plan theo sprint (ĐƯỢC date/mã task trong tên)
│   ├── Sprint0_UX/
│   │   ├── UX_Phase2_Plan.md             ← ⚠️ [HISTORICAL]
│   │   └── Resize_Window_Plan.md
│   ├── Sprint1/
│   │   ├── START_HERE.md
│   │   └── T15_Rotate_Scale_Plan.md
│   ├── Sprint2/
│   │   ├── Plan.md                       ← ⚠️ [HISTORICAL]
│   │   └── ContextMenu_Prep.md           ← ⚠️ [HISTORICAL]
│   ├── Sprint3/
│   │   ├── Plan.md                       ← ⚠️ [HISTORICAL]
│   │   └── Regression_DualDispatcher_Log.md ← as-built phụ (KHÔNG đóng dấu — xem MERGE_LOG)
│   ├── Sprint4/
│   │   ├── Plan.md                       ← ⚠️ [HISTORICAL]
│   │   ├── Execution.md                  ← ⚠️ [AS-BUILT TẠI THỜI ĐIỂM SPRINT 4]
│   │   └── BugFix_Execution.md           ← ⚠️ [AS-BUILT TẠI THỜI ĐIỂM SPRINT 4]
│   └── Sprint5/
│       ├── Combo_Execution.md            ← as-built chính combo Sprint 5
│       ├── Combo_C5_FolderManagement_Plan.md ← [THÊM 07/08 — diff cũ bỏ sót]
│       ├── C5.8_FolderTreePicker_Unify_Plan.md
│       ├── C5.8_TaskCard2_FixPlan_11jul2026.md   ← 📌 [CHỨA AS-BUILT]
│       ├── C5.8_TaskCard_2d_11jul2026.md
│       ├── C5.8_Wire_ExecutionPlan_12jul2026.md
│       └── C5.8_REG_TaskCard_11jul2026.md        ← 📌 [CHỨA AS-BUILT]
└── Archive/                              ← [THÊM 07/08] file đã bị supersede, giữ để tra
    ├── 01-08-2026_ReplaceUX_Fix_Execution_Plan_v1_SUPERSEDED.md
    └── README.md
```

> Dấu doc (`[HISTORICAL]` / `📌 [CHỨA AS-BUILT]` / `[AS-BUILT TẠI THỜI ĐIỂM X]`): định nghĩa đầy
> đủ ở `MERGE_LOG.md` mục "3 LOẠI DẤU DOC". Chú thích trong cây trên chỉ là con trỏ nhanh.

---

## 3. KHÔNG ĐƯỢC

- Tạo file docs trùng logical name (trừ `README.md` cấp thư mục).
- Để file "_patch"/"_update"/"_vN" sót lại trong canonical (`Blueprints/` `Widgets/` `Data/` `Rules/`).
- Xóa file trong `import_raw/` hay `Archive/` (kho lịch sử).
- Ghi as-built THẲNG vào `Plans/`/`Sprints/` mà không đóng banner `📌 [CHỨA AS-BUILT]` (R-DOC-ASBUILT).
- Tự thêm/bỏ file khỏi cây này khi không chắc — đánh dấu `[?]`, báo cuhoang.

---

## [HISTORICAL] Quy trình merge import_raw → docs/ (một lần, xong 06/2026)
> Giữ để tra "vì sao file X đặt ở Y". KHÔNG phải quy trình hiện hành. Chi tiết đầy đủ: MERGE_LOG.md.

## 3. NHÓM MERGE NHIỀU PHIÊN BẢN (rủi ro cao — phải ráp base+patch)

| Đích | Base đầy đủ mới nhất | Patch áp lên (thứ tự) | Version đích |
|---|---|---|---|
| Blueprints/BP_FurnitureInputManager.md | base v1.6 | v1.7 → v1.8 → v1.9 | 1.9 ✅ ĐÃ LÀM (mẫu) |
| Blueprints/BP_UndoManager.md | base v1.6 | v1.7 → v1.8 | 1.8 ✅ ĐÃ LÀM |
| Widgets/WBP_MeshControls.md | base | v1.5_patch → v1.5_update → v1.6_patch | 1.6 |
| Blueprints/Blueprint_Logic_NodeFlow.md | base | v1.4_patch → v1.5_patch | 1.5 |
| Widgets/WBP_FurnitureInventory.md | base v2.4 | WBP_Inventory_Card patch | — |
| Widgets/WBP_DragOverlay_FurnitureCard.md | base | v1.5_patch | 1.5 |

> ⚠️ `WBP_MeshControls_v1_5_update` KHÔNG phải base — là delta, xử lý như patch (áp SAU v1.5_patch, TRƯỚC v1.6_patch).
> ⚠️ Xung đột (một function nhiều patch sửa) → lấy patch mới nhất, ghi chú bản cũ bị thay.

---

## 4. NHÓM GỘP 2 NGUỒN (rủi ro vừa)

| Đích | Nguồn | Ghi chú |
|---|---|---|
| Blueprints/BP_GizmoController.md | BP_GizmoController + BP_GizmoController_OnMouseReleased + BP_GizmoController_OnMouseReleased fragment | OnMouseReleased là EVENT FLOW RIÊNG — PHẢI giữ, đừng vứt |
| Blueprints/BP_FurnitureActor.md | tách từ BP_FurnitureActor_SceneManager (phần Actor) | 1 file gốc gộp 2 BP → tách 2 |
| Blueprints/BP_FurnitureSceneManager.md | tách từ BP_FurnitureActor_SceneManager (phần SceneManager) | |
| 00_Core/DEVIATIONS.md | DEVIATIONS master + addendum Sprint4BugFix | merge addendum vào master |
| Data/FilterByCategory_Logic.md | 2 version | lấy mới nhất theo "Cập nhật" |

---

## 5. NHÓM 1 NGUỒN (đổi tên + move, không ráp)

- Session_State (12 bản) → 00_Core/01_Session_State.md (CHỈ giữ bản "Cập nhật" mới nhất)
- PROGRESS (nhiều bản) → 00_Core/PROGRESS.md (bản mới nhất)
- INDEX → 00_Core/00_INDEX.md
- Gate1_SprintD_Execution → 00_Core/02_Current_Sprint.md (active)
- Các Rules/Planning/Sprint plan/Data 1-bản → theo cây mục 2

---

## 6. XỬ LÝ ĐẶC BIỆT

- **FurnitureFilterLibrary.cpp** → KHÔNG copy source vào docs. Tạo Data/FurnitureFilterLibrary_Reference.md ghi: vị trí file thật, danh sách function + signature + mục đích. Source thật sống trong plugin.
- **Sprint5_Combo_Execution** → Sprints/Sprint5/. UPCOMING, chưa làm. Khi Gate 1 xong sẽ promote nội dung lên 00_Core/02_Current_Sprint.md.
- **ChangeMaterial** → kiểm version mâu thuẫn (tên v1.1, nội dung ghi 1.6). Đọc kỹ, lấy nội dung mới nhất.
- **Bugs/Open_Bugs.md** → tạo mới: extract B1 (bIsRestoring), bug gizmo pre-existing, Replace folder mixed (defer Sprint 5) từ Session_State.

---

## 7. KHÔNG ĐƯỢC

- Xóa bất kỳ file nào trong import_raw (kho lịch sử).
- Tạo file docs trùng logical name.
- Để file "_patch"/"_update" sót lại trong docs/.
- Tự thêm/bỏ function khi không chắc → đánh dấu [?] và báo.

---

## Changelog

**v2.0 — 07/08/2026 (Opus):** viết lại từ `git ls-files docs/` thật (114 file). Cụ thể:
- **THÊM vào cây** (có trên đĩa, cây v1.x thiếu): cả `Plans/` (8), `Archive/` (2), `Features/` (2),
  6 file `00_Core/` (MERGE_LOG, RAW_INVENTORY, README, TARGET_STRUCTURE, 3 report 02aug),
  5 README thư mục, `BP_FurnitureUserPrefsManager`, 3 file `Data/` (Data_Overview, FilterBySearch,
  Python_Scripts — diff cũ bỏ sót), 5 `Sprints/Sprint5/C5.8_*` + `Combo_C5_FolderManagement_Plan`,
  `Widgets/` (WBP_ConfirmDialog, WBP_FurnitureCard, WBP_Toast, WBP_FolderTreePicker/PickerRow/
  MoveToFolderDialog/MoveFolderRow/SaveComboDialog).
- **Gỡ khỏi cây** (trong cây v1.x, không còn/chưa từng có trên đĩa): `Planning/Master_Roadmap.md`
  (dangling), `Sprints/SprintD/` (đã fold vào 02_Current_Sprint.md), `Widgets/WBP_DragOverlay_ComboCard.md`
  (chưa từng tách).
- **Gỡ nhãn lỗi thời:** `WBP_ComboCard.md` bỏ chú thích "[CHƯA TÁCH FILE]" — file đã tồn tại thật.
- **Đóng [?]:** `Planning/MultiSelect_Group_ComboMesh_Plan.md` (treo từ MERGE_LOG) — giữ, nhãn [HISTORICAL].
- **Sửa mục 1:** tách quy ước tên canonical (không date) vs Plans/Sprints (được date) — v1.x cấm date
  mọi nơi, mâu thuẫn thực tế.
- **Cấu trúc:** mục 3–7 cũ (công thức merge import_raw) gộp xuống `[HISTORICAL]`, giữ nguyên văn.
