# Luồng 3a - Chọn đồ Gizmo Nhóm

> Tự sinh từ [[Architecture_Map]] v1.5 mục **3a — Chọn đồ · Gizmo · Nhóm** (24/09/2026). Dấu ✓K2 = cạnh nét dày `==>` trên sơ đồ gốc (đã kiểm chứng K2, diagram-contract §2); không dấu = theo doc. Sửa bản đồ gốc rồi chạy lại script.

← [[Bản đồ não]]

## Thành phần

- [[BP_FoffPlayerController]]
- [[BP_FurnitureActor]]
- [[BP_FurnitureInputManager]]
- [[BP_FurnitureSceneManager]]
- [[BP_GizmoController]]
- [[BP_GroupsContainer]] *(chưa có doc)*
- [[BP_PivotActor]]
- [[BP_TransformerPawn]] *(chưa có doc)*
- [[BP_UndoManager]]
- [[WBP_BoxSelectOverlay]]
- [[WBP_ContextMenu]] *(chưa có doc)*
- [[WBP_ContextMenuItem]] *(chưa có doc)*
- [[WBP_FurnitureInventory]]
- [[WBP_MeshControls]]

## Ai gọi ai

- [[BP_FurnitureInputManager]] → [[WBP_ContextMenuItem]] — tạo 11 mục menu · Create Widget (OnRightClick) ✓K2
- [[BP_FurnitureInputManager]] → [[WBP_ContextMenu]] — tạo menu + gọi đóng · Create + Hide() ✓K2
- [[BP_FurnitureInputManager]] → [[WBP_BoxSelectOverlay]] — tạo + gọi ẩn khung · Create + HideBox() ✓K2
- [[BP_FurnitureInputManager]] → [[BP_UndoManager]] — chụp mốc Select/Deselect · CaptureSnapshot() ✓K2
- [[BP_FurnitureInputManager]] → [[BP_FurnitureSceneManager]] — tìm singleton, đọc tham chiếu inventory · GetAllActorsOfClass, GET FurnitureInventoryRef ✓K2
- [[BP_FurnitureSceneManager]] → [[WBP_FurnitureInventory]] — gọi thoát Replace Mode · .FurnitureInventoryRef.ExitReplaceMode() ✓K2
- [[BP_FurnitureInputManager]] → [[WBP_FurnitureInventory]] — báo click-vào-mesh chọn slot · NotifyViewportSlotClick(ClickedActor, ScreenPos) ✓K2
- [[BP_FurnitureInputManager]] → [[BP_GizmoController]] — gọi lúc bấm chuột + giữ tham chiếu · OnMousePressed(), GizmoControllerRef
- [[BP_FurnitureInputManager]] → [[BP_TransformerPawn]] — giữ tham chiếu · TransformerPawnRef
- [[BP_FurnitureInputManager]] → [[BP_GroupsContainer]] — đọc-ghi số đếm nhóm · GroupNameCounter, Groups
- [[BP_FurnitureInputManager]] → [[BP_PivotActor]] — tạo & huỷ trục xoay · SpawnOrUpdatePivot() / DestroyPivot()
- [[BP_FurnitureInputManager]] → [[BP_FurnitureActor]] — đọc đồ đang chọn · Cast + GET PrimarySelectedActor
- [[BP_FurnitureInputManager]] → [[WBP_MeshControls]] — giữ tham chiếu thanh công cụ · CurrentMeshControls
- [[BP_GizmoController]] → [[BP_TransformerPawn]] — giữ tham chiếu · TransformerPawnRef
- [[BP_GizmoController]] → [[BP_PivotActor]] — cập nhật trục lúc bấm · RefreshOffsets()
- [[BP_GizmoController]] → [[BP_FurnitureInputManager]] — hỏi chế độ hiện tại · GET ActiveMode
- [[BP_GizmoController]] → [[BP_UndoManager]] — chụp trạng thái khi kéo xong · CaptureSnapshot()
- [[BP_PivotActor]] → [[BP_FurnitureActor]] — kéo đồ con theo trục · ApplyTransformToChildren()
- [[WBP_MeshControls]] → [[BP_FurnitureInputManager]] — nghe chọn đồ / đổi chế độ + gọi hàm edit-mode · Bind OnSelectionChanged, OnEditModeChanged ✓K2
- [[WBP_MeshControls]] → [[BP_FurnitureActor]] — đọc mã đồ · Cast + GET RowName
- [[BP_FurnitureSceneManager]] → [[BP_FurnitureInputManager]] — yêu cầu bỏ chọn · DeselectMesh()
- [[BP_FoffPlayerController]] → [[BP_UndoManager]] — phím Undo / Redo · UndoLastAction() / RedoLastAction()
- [[BP_UndoManager]] → [[BP_FurnitureInputManager]] — chọn lại đồ sau khôi phục + báo tin · SelectActors(), Broadcast OnEditModeChanged
