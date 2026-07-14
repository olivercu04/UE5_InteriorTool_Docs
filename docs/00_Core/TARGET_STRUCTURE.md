# TARGET_STRUCTURE — Bản đồ chuẩn docs/ (UE5_InteriorTool_Docs)
**Mục đích:** nguồn duy nhất quy định mỗi file raw đi đâu, đặt tên gì, merge với file nào.
Claude Code đọc file này TRƯỚC khi merge. KHÔNG tự suy diễn path khác.

---

## 1. QUY ƯỚC ĐẶT TÊN (code-standard)

- Tên file docs = **đúng tên asset trong UE5** (BP_*, WBP_*, S_*, DT_*, E_*). Không thêm date, không thêm version vào tên file.
- Date + version sống trong: (a) header file, (b) import_raw, (c) git history. KHÔNG nhồi vào tên file docs.
- Một logical asset = một file docs duy nhất. Không có file "_patch", "_update", "_v1_x" trong docs/.
- Prefix số (00_, 01_) chỉ dùng ở 00_Core/ và các bộ tài liệu có thứ tự đọc (Planning 00→07).
- Mỗi file docs hợp nhất phải có header: `**HỢP NHẤT TỪ N file:** ...` (provenance) + bảng "Lịch sử cập nhật" đầy đủ ở cuối.

---

## 2. CÂY THƯ MỤC

```
docs/
├── 00_Core/                  ← đọc mỗi đầu session
│   ├── 00_INDEX.md
│   ├── 01_Session_State.md
│   ├── 02_Current_Sprint.md
│   ├── PROGRESS.md
│   └── DEVIATIONS.md
├── Rules/
│   ├── Workflow.md
│   ├── Project_Instructions.md
│   ├── AI_Communication_Rules.md
│   ├── AI_Implementation_Rules.md
│   ├── Execution_Discipline.md
│   ├── Design.md
│   ├── Antipatterns.md
│   ├── Performance.md
│   └── Learning_System.md
├── Blueprints/
│   ├── BP_FurnitureInputManager.md
│   ├── BP_UndoManager.md
│   ├── BP_GizmoController.md
│   ├── BP_PivotActor.md
│   ├── BP_FurnitureActor.md
│   ├── BP_FurnitureSceneManager.md
│   ├── BP_FoffPlayerController.md
│   ├── BP_ComboManager.md                 ← Sprint 5 (T2/C0-C2) — save/spawn/replace combo logic
│   ├── BP_ComboItemView.md                ← Sprint 5 (C3a/C4) — Object class bọc FComboData cho CTV_ComboCard
│   ├── BP_ComboGhostActor.md              ← Sprint 5 (C4) — ghost preview bounding box lúc drag combo
│   ├── Blueprint_Logic_NodeFlow.md
│   └── Flows/
│       ├── Nudge_Flow.md
│       └── CopyPaste_Flow.md
├── Widgets/
│   ├── WBP_FurnitureInventory.md
│   ├── WBP_MeshControls.md
│   ├── WBP_DragOverlay_FurnitureCard.md
│   ├── WBP_BoxSelectOverlay.md
│   ├── WBP_DetailPopup.md
│   ├── WBP_ResizeWindow.md
│   ├── WBP_TreeNode.md                    ← Sprint 5 (C5.0)
│   ├── WBP_ChipTag.md                     ← Sprint 5 (C5.0)
│   ├── WBP_LibraryContextMenu.md          ← Sprint 5 (C5.0)
│   ├── WBP_EditableLabel.md               ← Sprint 5 (C5.2)
│   ├── WBP_ComboCard.md                   ← Sprint 5 (C4) — [CHƯA TÁCH FILE] nội dung hiện nằm rải rác:
│   │                                          tham chiếu trong WBP_FurnitureInventory.md (Entry Widget Class,
│   │                                          OnComboCardRightClicked) + tóm tắt trong 01_Session_State.md
│   │                                          mục KIẾN TRÚC HIỆN TẠI (OnListItemObjectSet/OnDragDetected/
│   │                                          On Mouse Button Down). Chưa có file .md đầy đủ riêng.
│   ├── WBP_DragOverlay_ComboCard.md       ← Sprint 5 (C4, nếu tách riêng file)
│   ├── WBP_SaveComboDialog.md             ← Sprint 5 (C3b)
│   ├── WBP_MoveToFolderDialog.md          ← Sprint 5 (C5.4) — MỚI 30/06
│   ├── WBP_MoveFolderRow.md               ← Sprint 5 (C5.4) — MỚI 30/06
│   ├── WBP_FolderTreePicker.md            ← Sprint 5 (C5.8)
│   └── WBP_FolderPickerRow.md             ← Sprint 5 (C5.8)
├── Data/
│   ├── Data_Structures.md
│   ├── Data_Overview.md
│   ├── FilterByCategory_Logic.md
│   ├── FilterBySearch_Logic.md
│   ├── FurnitureFilterLibrary_Reference.md
│   ├── ComboSerializer_Reference.md       ← Sprint 5 (C++ UComboSerializer/UComboThumbnail) — MỚI 14/07
│   └── Python_Scripts.md
├── Features/
│   ├── ChangeMaterial.md
│   └── Material_CopyPaste.md
├── Planning/
│   ├── 00_Master_Plan.md
│   ├── 01_Current_Architecture_Audit.md
│   ├── 02_Target_Architecture.md
│   ├── 03_Code_Inheritance_Strategy.md
│   ├── 04_Sprint_Details.md
│   ├── 06_Risk_Mitigation.md
│   ├── 07_Testing_Strategy.md
│   ├── Architecture_Overview.md
│   ├── Tech_Defaults.md
│   ├── Master_Roadmap.md
│   ├── Future_Architecture_1M_Assets.md
│   ├── Backend_Plan.md
│   ├── Integration_Guide.md
│   ├── Plugin_Migration_Guide.md
│   ├── i18n_Plan.md
│   └── UE5_InteriorTool_Overview.md
├── Sprints/
│   ├── Sprint0_UX/   (UX_Phase2_Plan, Resize_Window_Plan)
│   ├── Sprint1/      (START_HERE, T15_Rotate_Scale_Plan)
│   ├── Sprint2/      (Plan, ContextMenu_Prep)
│   ├── Sprint3/      (Plan, Regression_DualDispatcher_Log)
│   ├── Sprint4/      (Plan, Execution, BugFix_Execution)
│   ├── SprintD/      (Gate1_Execution)
│   └── Sprint5/      (Combo_Execution + Combo_C5_FolderManagement_Plan — đang thực thi, xem 00_Core/02_Current_Sprint.md để biết task hiện tại)
└── Bugs/
    ├── Open_Bugs.md          ← TẠO MỚI (extract từ Session_State)
    └── Bug_GPU_VRAM_Crash.md
```

---

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
