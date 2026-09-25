# Kết nối 3a - Chọn đồ Gizmo Nhóm

> Tự sinh từ [[Architecture_Map]] mục **3a — Chọn đồ · Gizmo · Nhóm**. Dấu ✓K2 = cạnh nét dày `==>` trên sơ đồ gốc (đã kiểm chứng K2, diagram-contract §2); không dấu = theo doc. Sửa bản đồ gốc rồi chạy lại script.

← [[Bản đồ não]] · Mức asset (ai nói chuyện với ai). Theo từng THAO TÁC của người dùng → note `L01…L13` trong `Brain/Luồng/`.

## Thành phần

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
- [[BP_FurnitureInputManager]] → [[WBP_BoxSelectOverlay]] — tạo + hiện / vẽ / ẩn khung · Create + ShowBox() / UpdateBox() / HideBox() ✓K2
- [[BP_FurnitureInputManager]] → [[BP_UndoManager]] — chụp mốc Select/Deselect · CaptureSnapshot(Select / Deselect) ✓K2
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
- [[BP_GizmoController]] → [[BP_PivotActor]] — cập nhật trục lúc bấm + dời pivot khi kéo · RefreshOffsets(), Set Actor Location
- [[BP_GizmoController]] → [[BP_FurnitureActor]] — dời món khi kéo (1 món) · Set Actor Location(SelectedActor)
- [[BP_GizmoController]] → [[BP_FurnitureInputManager]] — hỏi chế độ hiện tại · GET ActiveMode ✓K2
- [[BP_GizmoController]] → [[BP_UndoManager]] — chụp trạng thái khi kéo xong · CaptureSnapshot() ✓K2
- [[BP_PivotActor]] → [[BP_FurnitureActor]] — kéo đồ con theo trục · ApplyTransformToChildren()
- [[WBP_MeshControls]] → [[BP_FurnitureInputManager]] — nghe chọn đồ / đổi chế độ + gọi hàm edit-mode · Bind OnSelectionChanged, OnEditModeChanged ✓K2
- [[WBP_MeshControls]] → [[BP_FurnitureActor]] — đọc mã đồ · Cast + GET RowName
- [[WBP_MeshControls]] → [[BP_FurnitureInputManager]] — đặt chế độ Move / Rotate / Scale / Select · SET ActiveMode
- [[WBP_MeshControls]] → [[BP_GizmoController]] — tắt rồi bật gizmo khi đổi chế độ · DeactivateGizmo() / ActivateGizmo() — lấy tham chiếu từ đâu ?
- [[BP_FurnitureSceneManager]] → [[BP_FurnitureInputManager]] — yêu cầu bỏ chọn · DeselectMesh()
- [[BP_FurnitureInputManager]] → [[BP_UndoManager]] — phím Undo / Redo (bỏ qua khi đang kéo gizmo) · IsGizmoDragging() → UndoLastAction() / RedoLastAction()
- [[BP_UndoManager]] → [[BP_FurnitureInputManager]] — chọn lại đồ sau khôi phục + báo tin · SelectActors(), Broadcast OnEditModeChanged
- [[BP_UndoManager]] → [[WBP_MeshControls]] — đặt nút mode theo ảnh sau khôi phục · RefreshButtonState(ActiveMode) — lấy tham chiếu từ đâu ?
- [[BP_FurnitureInputManager]] → [[BP_UndoManager]] — chụp mốc các thao tác khác · CaptureSnapshot(BoxSelect / CreateGroup / Ungroup / PasteMulti / DuplicateMulti / Delete / Nudge / SelectSimilar / ResetRotation)
- [[BP_FurnitureInputManager]] → [[BP_FurnitureActor]] — dời / gán nhóm / xoá đồ đang chọn · Add Actor World Offset (NudgeMesh), SET GroupID (CreateGroup), Destroy Actor (DeleteSelected)
- [[BP_FurnitureInputManager]] → [[BP_PivotActor]] — dời pivot theo nhóm khi nhích phím · Set Actor Location → RefreshOffsets()
- [[WBP_ContextMenuItem]] → [[BP_FurnitureInputManager]] — dòng menu được bấm → callback của IM · CB_Copy / CB_Paste / CB_Duplicate / CB_Delete … — bind trong OnRightClick ?
- [[WBP_MeshControls]] → [[BP_FurnitureInputManager]] — bật / tắt thay đồ · BTN_Replace → StartReplaceMode(SelectedActors), IsReplaceModeActive() ✓K2
- [[WBP_MeshControls]] → [[BP_FurnitureInputManager]] — vào / ra sửa nhóm · TryEnterEditFromSelection() / ExitEditModeOneLevel() / ExitEditModeFull()
