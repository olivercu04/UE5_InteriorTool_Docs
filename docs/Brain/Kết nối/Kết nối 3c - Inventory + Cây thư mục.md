# Kết nối 3c - Inventory + Cây thư mục

> Tự sinh từ [[Architecture_Map]] mục **3c — Inventory + Cây thư mục**. Dấu ✓K2 = cạnh nét dày `==>` trên sơ đồ gốc (đã kiểm chứng K2, diagram-contract §2); không dấu = theo doc. Sửa bản đồ gốc rồi chạy lại script.

← [[Bản đồ não]] · Mức asset (ai nói chuyện với ai). Theo từng THAO TÁC của người dùng → note `L01…L13` trong `Brain/Luồng/`.

## Thành phần

- [[BP_DragDropOperation_FurnitureCard]] *(chưa có doc)*
- [[BP_FurnitureActor]]
- [[BP_FurnitureInputManager]]
- [[BP_FurnitureItemView]] *(chưa có doc)*
- [[BP_FurnitureUserPrefsManager]]
- [[BP_UndoManager]]
- [[EntityIdLibrary_Reference]]
- [[Foff_GameInstance]] *(chưa có doc)*
- [[FurnitureFilterLibrary_Reference]]
- [[WBP_ChipRow]] *(chưa có doc)*
- [[WBP_ChipTag]]
- [[WBP_ConfirmDialog]]
- [[WBP_DetailPopup]]
- [[WBP_DragOverlay_FurnitureCard]]
- [[WBP_EditableLabel]]
- [[WBP_FolderPickerRow]]
- [[WBP_FolderTreePicker]]
- [[WBP_FurnitureCard]]
- [[WBP_FurnitureInventory]]
- [[WBP_MoveToFolderDialog]]
- [[WBP_TreeNode]]

## Ai gọi ai

- [[WBP_FurnitureInventory]] → [[FurnitureFilterLibrary_Reference]] — lọc đồ / vật liệu · FilterFurnitureRows() (C++)
- [[WBP_FurnitureInventory]] → [[BP_FurnitureInputManager]] — vào chế độ thay đồ · StartReplaceMode() / ShouldRouteReplaceToCombo() ✓K2
- [[WBP_FurnitureInventory]] → [[BP_UndoManager]] — giữ tham chiếu + nghe khôi phục + chụp trạng thái · UndoManagerRef, Bind OnRestoreCompleted
- [[WBP_FurnitureInventory]] → [[Foff_GameInstance]] — tự đăng ký + hiện thông báo · FurnitureInventoryRef, ToastRef.ShowToast()
- [[WBP_FurnitureInventory]] → [[WBP_FurnitureCard]] — đổ đồ vào ListView · ListView entry WBP_FurnitureCard
- [[WBP_FurnitureInventory]] → [[BP_FurnitureItemView]] — tạo 1 ô cho mỗi hàng lọc · Make BP_FurnitureItemView
- [[WBP_FurnitureInventory]] → [[WBP_TreeNode]] — tạo + nghe cây folder · Create + Bind OnNodeSelected / RightClicked / Rename
- [[WBP_FurnitureInventory]] → [[WBP_ChipTag]] — tạo + nghe chip đường dẫn · Create + Bind OnChip…
- [[WBP_FurnitureInventory]] → [[WBP_ChipRow]] — tạo hàng chip cho mỗi cấp · Create WBP_ChipRow
- [[WBP_FurnitureInventory]] → [[WBP_DetailPopup]] — mở popup chi tiết · CurrentPopup
- [[WBP_FurnitureInventory]] → [[WBP_MoveToFolderDialog]] — mở + nghe dialog di chuyển · MoveComboDialogRef, Bind OnMoveFolderConfirmed
- [[WBP_FurnitureInventory]] → [[WBP_ConfirmDialog]] — mở + nghe hộp xác nhận · Bind OnConfirmed
- [[WBP_FurnitureCard]] → [[WBP_FurnitureInventory]] — giữ tham chiếu + đọc chế độ thay đồ · InventoryRef, ReplaceTarget ✓K2
- [[WBP_FurnitureCard]] → [[BP_FurnitureItemView]] — đọc mã đồ từ ô · Cast BP_FurnitureItemView → RowName
- [[WBP_FurnitureCard]] → [[BP_FurnitureUserPrefsManager]] — gọi thêm Gần đây / Yêu thích · AddRecentMesh()
- [[WBP_FurnitureCard]] → [[BP_FurnitureActor]] — tạo đồ bóng lúc kéo · Spawn BP_FurnitureActor
- [[WBP_FurnitureCard]] → [[WBP_DragOverlay_FurnitureCard]] — tạo lớp kéo-thả · Create WBP_DragOverlay
- [[WBP_FurnitureCard]] → [[BP_DragDropOperation_FurnitureCard]] — tạo gói kéo-thả mang RowName · Create BP_DragDropOperation_FurnitureCard
- [[WBP_DragOverlay_FurnitureCard]] → [[BP_DragDropOperation_FurnitureCard]] — đọc RowName từ gói lúc thả · Cast BP_DragDropOperation_FurnitureCard
- [[WBP_FurnitureCard]] → [[BP_UndoManager]] — chụp trạng thái khi thay đồ · CaptureSnapshot(Replace)
- [[WBP_FurnitureCard]] → [[BP_FurnitureInputManager]] — lấy tham chiếu manager · GetAllActorsOfClass (F_ExecuteReplace) ✓K2
- [[WBP_DragOverlay_FurnitureCard]] → [[BP_FurnitureActor]] — đặt loại bề mặt cho đồ · Cast + SET PlacementSurfaceType
- [[WBP_DragOverlay_FurnitureCard]] → [[BP_FurnitureInputManager]] — tắt gizmo khi thả · GizmoControllerRef.DeactivateGizmo()
- [[WBP_DragOverlay_FurnitureCard]] → [[EntityIdLibrary_Reference]] — sinh ID cho đồ kéo-thả (producer thứ 4, U1.2 21/09) · EnsurePersistentId()
- [[WBP_TreeNode]] → [[WBP_EditableLabel]] — nhúng + nghe nhãn sửa tên · EditableLabel_Name, Bind OnLabelRenameCommitted
- [[WBP_ChipTag]] → [[WBP_EditableLabel]] — nhúng nhãn sửa tên · EditLabel_ChipTag
- [[WBP_FolderTreePicker]] → [[WBP_FolderPickerRow]] — tạo + nghe từng hàng folder · Create WBP_FolderPickerRow, Bind OnRow… ✓K2
- [[WBP_FolderPickerRow]] → [[WBP_EditableLabel]] — nhúng + đổi màu nhãn · EditableLabel_Name, SetLabelColor() ✓K2
- [[WBP_MoveToFolderDialog]] → [[WBP_FolderTreePicker]] — nhúng + nghe cây thư mục · Picker, Bind OnFolderSelected
- [[WBP_TreeNode]] → [[WBP_FurnitureInventory]] — báo tin bấm thư mục · OnNodeSelected → OnTreeNodeClicked()
- [[WBP_FurnitureInventory]] → [[BP_FurnitureUserPrefsManager]] — đọc danh sách Gần đây / Yêu thích · GET UserPrefs → RecentMeshes / FavoriteMeshes
- [[BP_FurnitureInputManager]] → [[WBP_FurnitureInventory]] — mở kho ở chế độ thay đồ · EnterReplaceMode() → FilterByFolderPathWithUI() ✓K2
- [[WBP_DragOverlay_FurnitureCard]] → [[BP_UndoManager]] — ghi sổ khi thả đồ · CaptureSnapshot(Spawn)
- [[WBP_DragOverlay_FurnitureCard]] → [[BP_FurnitureUserPrefsManager]] — thêm đồ vừa thả vào Gần đây · AddRecentMesh()
