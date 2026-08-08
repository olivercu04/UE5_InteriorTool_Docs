# Index — Toàn bộ tài liệu docs/
**Cập nhật:** 14/07/2026 (bổ sung docs/Data — 3+ tuần chưa cập nhật: `ComboSerializer_Reference.md` mới + 3 Blueprint Combo bị sót trước đó) | **Tổng số file:** 104 .md files (đếm thật `find docs -iname *.md`, 14/07/2026)
**Ghi chú:** File này là index điều hướng — không chứa nội dung kỹ thuật.

---

## Muốn sửa X → đọc file Y

| Muốn sửa / hiểu | File |
|---|---|
| Select / multi-select / box select / group / edit mode / clipboard / nudge | [Blueprints/BP_FurnitureInputManager.md](../Blueprints/BP_FurnitureInputManager.md) |
| Undo / Redo / snapshot / CaptureSnapshot / RestoreSnapshot | [Blueprints/BP_UndoManager.md](../Blueprints/BP_UndoManager.md) (Bug B1 + bIsRestoring: xem [02_Current_Sprint.md](02_Current_Sprint.md)) |
| Toolbar / info bar / breadcrumb / nút edit mode / snap fields | [Widgets/WBP_MeshControls.md](../Widgets/WBP_MeshControls.md) |
| Inventory / filter / search / folder tree / pagination / material grid / replace mode | [Widgets/WBP_FurnitureInventory.md](../Widgets/WBP_FurnitureInventory.md) |
| Drag-drop spawn / ghost preview / surface snap | [Widgets/WBP_DragOverlay_FurnitureCard.md](../Widgets/WBP_DragOverlay_FurnitureCard.md) |
| Popup chi tiết sản phẩm | [Widgets/WBP_DetailPopup.md](../Widgets/WBP_DetailPopup.md) |
| Resize window logic | [Widgets/WBP_ResizeWindow.md](../Widgets/WBP_ResizeWindow.md) |
| Box select overlay widget | [Widgets/WBP_BoxSelectOverlay.md](../Widgets/WBP_BoxSelectOverlay.md) |
| Gizmo movement / ray-plane / snap / rotation delta | [Blueprints/BP_GizmoController.md](../Blueprints/BP_GizmoController.md) |
| Pivot multi-select move/rotate/scale | [Blueprints/BP_PivotActor.md](../Blueprints/BP_PivotActor.md) |
| EMS Save/Load / spawn/destroy actor | [Blueprints/BP_FurnitureSceneManager.md](../Blueprints/BP_FurnitureSceneManager.md) + [Blueprints/BP_FurnitureActor.md](../Blueprints/BP_FurnitureActor.md) |
| Combo save/spawn/replace / thumbnail capture (P1) | [Blueprints/BP_ComboManager.md](../Blueprints/BP_ComboManager.md) |
| Combo C++ backend (save file/folder ops/thumbnail PNG) | [Data/ComboSerializer_Reference.md](../Data/ComboSerializer_Reference.md) |
| Combo struct thật (FComboData/Group/Item) | [Data/Data_Structures.md](../Data/Data_Structures.md) |
| Player controller (input routing) | [Blueprints/BP_FoffPlayerController.md](../Blueprints/BP_FoffPlayerController.md) |
| Filter logic chi tiết | [Data/FilterBySearch_Logic.md](../Data/FilterBySearch_Logic.md), [Data/FilterByCategory_Logic.md](../Data/FilterByCategory_Logic.md) |
| Node flow Sprint 1-4 tổng hợp | [Blueprints/Blueprint_Logic_NodeFlow.md](../Blueprints/Blueprint_Logic_NodeFlow.md) |
| Material editor / change material | [Features/ChangeMaterial.md](../Features/ChangeMaterial.md) |
| Copy/paste material | [Features/Material_CopyPaste.md](../Features/Material_CopyPaste.md) + [Blueprints/Flows/CopyPaste_Flow.md](../Blueprints/Flows/CopyPaste_Flow.md) |
| Nudge phím mũi tên | [Blueprints/Flows/Nudge_Flow.md](../Blueprints/Flows/Nudge_Flow.md) |
| Data structures / DataTable / DA / struct | [Data/Data_Structures.md](../Data/Data_Structures.md) |
| C++ filter library (FilterFurnitureRows, FilterMaterialItems) | [Data/FurnitureFilterLibrary_Reference.md](../Data/FurnitureFilterLibrary_Reference.md) |
| Python scripts pipeline | [Data/Python_Scripts.md](../Data/Python_Scripts.md) |
| Kiến trúc tổng / R1-R5 | [Planning/Architecture_Overview.md](../Planning/Architecture_Overview.md), [Planning/02_Target_Architecture.md](../Planning/02_Target_Architecture.md) |
| Hiệu năng / VRAM / budget | [Rules/Performance.md](../Rules/Performance.md), [Bugs/Bug_GPU_VRAM_Crash.md](../Bugs/Bug_GPU_VRAM_Crash.md) |
| Antipatterns đã trả giá | [Rules/Antipatterns.md](../Rules/Antipatterns.md) |
| Scale 1M assets | [Planning/Future_Architecture_1M_Assets.md](../Planning/Future_Architecture_1M_Assets.md) |
| Bugs đang mở | [Bugs/Open_Bugs.md](../Bugs/Open_Bugs.md) |
| Gate 1 + Sprint D execution plan | [00_Core/02_Current_Sprint.md](02_Current_Sprint.md) |

---

## Bắt đầu từ đây

| File | Mô tả |
|---|---|
| [00_Core/01_Session_State.md](01_Session_State.md) | Trạng thái hiện tại của dự án — đọc đầu tiên |
| [00_Core/02_Current_Sprint.md](02_Current_Sprint.md) | Gate 1 + Sprint D — task đang chạy |
| [00_Core/PROGRESS.md](PROGRESS.md) | Tiến độ tổng thể theo Sprint |
| [00_Core/DEVIATIONS.md](DEVIATIONS.md) | Các lệch khỏi kế hoạch gốc, bug defer |
| [Bugs/Open_Bugs.md](../Bugs/Open_Bugs.md) | B1 🔴, B-gizmo 🟢, B-folder 🟢 — bugs đang mở |
| [Rules/AI_Implementation_Rules.md](../Rules/AI_Implementation_Rules.md) | Luật AI v2.1 — đọc trước khi implement |
| [Rules/Execution_Discipline.md](../Rules/Execution_Discipline.md) | CƠ CHẾ 6 (Luật 6A/6B) |

---

## 00_Core/

| File | Nội dung |
|---|---|
| [00_INDEX.md](00_INDEX.md) | File này — index toàn bộ docs/ |
| [01_Session_State.md](01_Session_State.md) | Kiến trúc v1.9, Sprint 4 BugFix COMPLETE, roadmap v3.1 |
| [02_Current_Sprint.md](02_Current_Sprint.md) | Gate 1 (G1.T1-G1.T3), Sprint D (D.T1-D.T9), Gate 2 notes |
| [DEVIATIONS.md](DEVIATIONS.md) | Lệch kế hoạch, bugs defer, quyết định kiến trúc |
| [MERGE_LOG.md](MERGE_LOG.md) | Log hợp nhất import_raw → docs/ (Lô A/B/C/D) |
| [PROGRESS.md](PROGRESS.md) | Overview bar, Sprint timeline, Sprint 4 BugFix section |
| [RAW_INVENTORY.md](RAW_INVENTORY.md) | Kiểm kê toàn bộ file import_raw/ |
| [README.md](README.md) | Mô tả thư mục 00_Core/ |
| [TARGET_STRUCTURE.md](TARGET_STRUCTURE.md) | Bản đồ 114 file của docs/, v2.0 07/08 |

---

## Blueprints/

| File | Nội dung |
|---|---|
| [BP_ComboGhostActor.md](../Blueprints/BP_ComboGhostActor.md) | Ghost actor tạm thời — preview bounding box combo lúc drag, spawn bởi WBP_ComboCard.OnDragDetected |
| [BP_ComboItemView.md](../Blueprints/BP_ComboItemView.md) | Object class bọc FComboData — dùng cho CTV_ComboCard (TileView tab 🧩 Combo) |
| [BP_ComboManager.md](../Blueprints/BP_ComboManager.md) | Actor xử lý combo logic (save/spawn/replace) — Sprint 5, nhận data qua param, không hard ref InputManager (R2) |
| [BP_FoffPlayerController.md](../Blueprints/BP_FoffPlayerController.md) | Player Controller gốc — 04/2026 |
| [BP_FurnitureActor.md](../Blueprints/BP_FurnitureActor.md) | Actor từng đồ nội thất — SaveGame vars, Sprint D RowName |
| [BP_FurnitureInputManager.md](../Blueprints/BP_FurnitureInputManager.md) | **⭐ Core** — Selection, Gizmo, Group, Clipboard, v1.9 |
| [BP_FurnitureSceneManager.md](../Blueprints/BP_FurnitureSceneManager.md) | Scene spawn + catalog — Sprint D DataTable flow |
| [BP_GizmoController.md](../Blueprints/BP_GizmoController.md) | Gizmo controller (TransformMode, axis drag) |
| [BP_PivotActor.md](../Blueprints/BP_PivotActor.md) | Pivot actor cho multi-select move/rotate/scale |
| [BP_UndoManager.md](../Blueprints/BP_UndoManager.md) | Undo/Redo stack — S_SceneSnapshot V4, mẫu chuẩn |
| [Blueprint_Logic_NodeFlow.md](../Blueprints/Blueprint_Logic_NodeFlow.md) | Notation guide — đọc node flow dạng text |
| [Flows/CopyPaste_Flow.md](../Blueprints/Flows/CopyPaste_Flow.md) | Node flow chi tiết Copy+Paste |
| [Flows/Nudge_Flow.md](../Blueprints/Flows/Nudge_Flow.md) | Node flow chi tiết Nudge (arrow keys) |
| [README.md](../Blueprints/README.md) | Mô tả thư mục Blueprints/ |

---

## Bugs/

| File | Nội dung |
|---|---|
| [Bug_GPU_VRAM_Crash.md](../Bugs/Bug_GPU_VRAM_Crash.md) | VRAM crash (budget ~7.26GB) — giải pháp hard ref clear |
| [Open_Bugs.md](../Bugs/Open_Bugs.md) | B1 (bIsRestoring), B-gizmo (pre-existing), B-folder (defer) |
| [README.md](../Bugs/README.md) | Mô tả thư mục Bugs/ |

---

## Data/

| File | Nội dung |
|---|---|
| [ComboSerializer_Reference.md](../Data/ComboSerializer_Reference.md) | C++ `UComboSerializer` (save/load/folder ops) + `UComboThumbnail` (capture/load PNG, P1) — Sprint 5 |
| [Data_Structures.md](../Data/Data_Structures.md) | S_SceneSnapshot V4, S_FurniturePlacement, S_GroupEntry, FComboData/Group/Item (Sprint 5) |
| [FilterByCategory_Logic.md](../Data/FilterByCategory_Logic.md) | Logic lọc theo category trong WBP_FurnitureInventory |
| [FilterBySearch_Logic.md](../Data/FilterBySearch_Logic.md) | Logic tìm kiếm text trong inventory |
| [FurnitureFilterLibrary_Reference.md](../Data/FurnitureFilterLibrary_Reference.md) | C++ UFurnitureFilterLibrary — 4 hàm, pattern Sprint D |
| [Python_Scripts.md](../Data/Python_Scripts.md) | Scripts xử lý DataTable/asset ngoài UE5 |
| [README.md](../Data/README.md) | Mô tả thư mục Data/ |

---

## Features/

| File | Nội dung |
|---|---|
| [ChangeMaterial.md](../Features/ChangeMaterial.md) | Tính năng thay material — Context menu flow v1.1 |
| [Material_CopyPaste.md](../Features/Material_CopyPaste.md) | Copy/paste material giữa các actor |

---

## Planning/

| File | Nội dung |
|---|---|
| [00_Master_Plan.md](../Planning/00_Master_Plan.md) | Kế hoạch tổng thể dự án |
| [01_Current_Architecture_Audit.md](../Planning/01_Current_Architecture_Audit.md) | Kiểm tra kiến trúc hiện tại (28/05/2026) |
| [02_Target_Architecture.md](../Planning/02_Target_Architecture.md) | Kiến trúc target dài hạn |
| [03_Code_Inheritance_Strategy.md](../Planning/03_Code_Inheritance_Strategy.md) | Chiến lược kế thừa code |
| [04_Sprint_Details.md](../Planning/04_Sprint_Details.md) | Chi tiết từng Sprint (Sprint 0–7, 1208 dòng) |
| [06_Risk_Mitigation.md](../Planning/06_Risk_Mitigation.md) | Rủi ro và biện pháp giảm thiểu |
| [07_Testing_Strategy.md](../Planning/07_Testing_Strategy.md) | Chiến lược testing toàn dự án |
| [Architecture_Overview.md](../Planning/Architecture_Overview.md) | Sơ đồ kiến trúc tổng thể |
| [Backend_Plan.md](../Planning/Backend_Plan.md) | Kế hoạch backend (server/API) |
| [Future_Architecture_1M_Assets.md](../Planning/Future_Architecture_1M_Assets.md) | Kiến trúc scale 1M+ asset (13/05/2026) |
| [Integration_Guide.md](../Planning/Integration_Guide.md) | Hướng dẫn tích hợp plugin/module |
| [MultiSelect_Group_ComboMesh_Plan.md](../Planning/MultiSelect_Group_ComboMesh_Plan.md) | Kế hoạch Multi-select + Group + Combo v2 |
| [Plugin_Migration_Guide.md](../Planning/Plugin_Migration_Guide.md) | Migration guide khi chuyển plugin |
| [Tech_Defaults.md](../Planning/Tech_Defaults.md) | Defaults kỹ thuật (UE version, plugin list) |
| [UE5_InteriorTool_Overview.md](../Planning/UE5_InteriorTool_Overview.md) | Tổng quan dự án UE5 Interior Tool |
| [i18n_Plan.md](../Planning/i18n_Plan.md) | Kế hoạch đa ngôn ngữ |

---

## Rules/

| File | Nội dung |
|---|---|
| [AI_Communication_Rules.md](../Rules/AI_Communication_Rules.md) | Q8 SELF-CHECK (5 điểm), L2 CHECK, Blueprint Export, Spawn Paths |
| [AI_Implementation_Rules.md](../Rules/AI_Implementation_Rules.md) | **⭐** Luật implement AI v2.1 — Q8 gate, L9, Bàn giao Opus→Sonnet |
| [Antipatterns.md](../Rules/Antipatterns.md) | Những gì KHÔNG được làm + lý do |
| [Design.md](../Rules/Design.md) | Quy tắc thiết kế UX/UI (Tab system, Material v1.1) |
| [Execution_Discipline.md](../Rules/Execution_Discipline.md) | **⭐** CƠ CHẾ 6 — Luật 6A (forward+backward), Luật 6B (structural) |
| [Learning_System.md](../Rules/Learning_System.md) | Hệ thống học UE5 cá nhân hóa (Cuhoang+Claude) |
| [Performance.md](../Rules/Performance.md) | Tối ưu hiệu năng — budget table, P1-P5, VRAM management |
| [Project_Instructions.md](../Rules/Project_Instructions.md) | Hướng dẫn dự án cho AI session mới |
| [README.md](../Rules/README.md) | Mô tả thư mục Rules/ |
| [Workflow.md](../Rules/Workflow.md) | Workflow làm việc giữa Cuhoang và Claude |

---

## Sprints/

### Sprint0_UX/
| File | Nội dung |
|---|---|
| [Resize_Window_Plan.md](../Sprints/Sprint0_UX/Resize_Window_Plan.md) | Kế hoạch resize window (26/05/2026) |
| [UX_Phase2_Plan.md](../Sprints/Sprint0_UX/UX_Phase2_Plan.md) | Kế hoạch UX Phase 2 (20/05/2026) |

### Sprint1/ — Multi-select
| File | Nội dung |
|---|---|
| [START_HERE.md](../Sprints/Sprint1/START_HERE.md) | Điểm bắt đầu Sprint 1 (02/06/2026) |
| [T15_Rotate_Scale_Plan.md](../Sprints/Sprint1/T15_Rotate_Scale_Plan.md) | T15: Multi Rotate+Scale plan |

### Sprint2/ — Box Select + Context Menu
| File | Nội dung |
|---|---|
| [ContextMenu_Prep.md](../Sprints/Sprint2/ContextMenu_Prep.md) | Chuẩn bị Context Menu + Replace (07/06/2026) |
| [Plan.md](../Sprints/Sprint2/Plan.md) | Sprint 2 plan v2 (05/06/2026) |

### Sprint3/ — Groups
| File | Nội dung |
|---|---|
| [Plan.md](../Sprints/Sprint3/Plan.md) | Sprint 3 plan (08/06/2026) |
| [Regression_DualDispatcher_Log.md](../Sprints/Sprint3/Regression_DualDispatcher_Log.md) | Log regression DualDispatcher → fix OnSelectionChanged đơn |

### Sprint4/ — Edit Mode + Nested
| File | Nội dung |
|---|---|
| [BugFix_Execution.md](../Sprints/Sprint4/BugFix_Execution.md) | Sprint 4 BugFix — F1-F4+A12 COMPLETE |
| [Execution.md](../Sprints/Sprint4/Execution.md) | Sprint 4 execution log |
| [Plan.md](../Sprints/Sprint4/Plan.md) | Sprint 4 plan (08/06/2026) |

### Sprint5/ — Combo Mesh
| File | Nội dung |
|---|---|
| [Combo_Execution.md](../Sprints/Sprint5/Combo_Execution.md) | Sprint 5 Combo Mesh execution plan |

---

## Widgets/

| File | Nội dung |
|---|---|
| [WBP_BoxSelectOverlay.md](../Widgets/WBP_BoxSelectOverlay.md) | Widget overlay box select (07/06/2026) |
| [WBP_ChipTag.md](../Widgets/WBP_ChipTag.md) | Chip đại diện 1 folder con trong breadcrumb area — click navigate + highlight active (C5.7b inline rename) |
| [WBP_ConfirmDialog.md](../Widgets/WBP_ConfirmDialog.md) | Dialog xác nhận generic Yes/No, tái dùng cho mọi hành động cần confirm (đầu tiên: C5.6 Xóa folder) |
| [WBP_DetailPopup.md](../Widgets/WBP_DetailPopup.md) | Widget popup detail (25/05/2026) |
| [WBP_DragOverlay_FurnitureCard.md](../Widgets/WBP_DragOverlay_FurnitureCard.md) | Widget drag card — On Drop auto-join edit scope |
| [WBP_EditableLabel.md](../Widgets/WBP_EditableLabel.md) | Component inline rename tái dùng (Content Browser style) — dùng bởi WBP_TreeNode (C5.2), WBP_ChipTag (C5.4+) |
| [WBP_FolderPickerRow.md](../Widgets/WBP_FolderPickerRow.md) | Row của WBP_FolderTreePicker — C5.8 |
| [WBP_FolderTreePicker.md](../Widgets/WBP_FolderTreePicker.md) | Tree picker component dùng chung Move/Save dialog — C5.8 |
| [WBP_FurnitureCard.md](../Widgets/WBP_FurnitureCard.md) | Card hiển thị 1 mặt hàng nội thất trong inventory (IUserObjectListEntry, Sprint D.T6) |
| [WBP_FurnitureInventory.md](../Widgets/WBP_FurnitureInventory.md) | Inventory widget — filter, scroll, folder nav |
| [WBP_LibraryContextMenu.md](../Widgets/WBP_LibraryContextMenu.md) | Context menu Combo Library — right-click WBP_TreeNode/WBP_ComboCard, clone WBP_ContextMenu |
| [WBP_MeshControls.md](../Widgets/WBP_MeshControls.md) | Controls panel (Move/Rotate/Scale/Delete) |
| [WBP_MoveFolderRow.md](../Widgets/WBP_MoveFolderRow.md) | 1 dòng trong list chọn folder đích của WBP_MoveToFolderDialog (C5.4) — superseded-candidate bởi WBP_FolderPickerRow, C5.8 |
| [WBP_MoveToFolderDialog.md](../Widgets/WBP_MoveToFolderDialog.md) | Dialog modal chọn folder cha đích khi move folder (C5.4) — field list dự kiến thay bằng WBP_FolderTreePicker, C5.8 |
| [WBP_ResizeWindow.md](../Widgets/WBP_ResizeWindow.md) | Widget resize cửa sổ tool (27/05/2026) |
| [WBP_SaveComboDialog.md](../Widgets/WBP_SaveComboDialog.md) | Dialog async nhập tên/folder/tags khi lưu combo (C3b) — field Folder dự kiến thay bằng WBP_FolderTreePicker, C5.8 |
| [WBP_TreeNode.md](../Widgets/WBP_TreeNode.md) | Node cây folder trong WBP_FurnitureInventory — click → OnNodeSelected + active highlight |
| [README.md](../Widgets/README.md) | Mô tả thư mục Widgets/ |

---

## Archive/

| File | Nội dung |
|---|---|
| [README.md](../Archive/README.md) | Mô tả — tài liệu cũ không còn áp dụng |

---

## Quick Reference

### Flow hiện tại (Gate 1 → Sprint D)
```
[Gate 1] G1.T1 bIsRestoring guard (B1 bug fix)
         G1.T2 hợp nhất spawn path
         G1.T3 update docs
    ↓
[Sprint D] D.T1 S_FurniturePlacement thêm RowName
           D.T2 BP_FurnitureActor lưu RowName khi spawn
           D.T3 FilterFurnitureRows C++ (mirror FilterMaterialItems)
           D.T4 BP_FurnitureSceneManager dùng RowName
           D.T5 CaptureSnapshot tương thích ngược
           D.T6 Replace Mesh đọc RowName từ actor
           D.T7 GetDistinctFolderPaths C++
           D.T8 WBP_FurnitureInventory dùng DT flow
           D.T9 Test + regression
```

### Kiến trúc cốt lõi (v1.9)
```
BP_FurnitureInputManager (v1.9) ← điều phối tất cả
  → BP_UndoManager (S_SceneSnapshot V4 + EditModeStack)
  → BP_GroupsContainer (SaveGame, GroupNameCounter)
  → BP_GizmoController (TransformMode, axis)
  → BP_PivotActor (multi-move, disable Tick khi idle)
  → Dispatcher: OnSelectionChanged (1 dispatcher duy nhất)
```

### S_SceneSnapshot versions
```
V1 — single select
V2 — multi select (SelectedActorIndices Array)
V3 — groups (GroupEntries Array)
V4 — groups + EditModeStack  ← CURRENT
```
