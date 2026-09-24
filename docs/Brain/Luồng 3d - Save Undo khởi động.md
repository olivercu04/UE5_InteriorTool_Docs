# Luồng 3d - Save Undo khởi động

> Tự sinh từ [[Architecture_Map]] v1.5 mục **3d — Save · Undo · khởi động** (24/09/2026). Dấu ✓K2 = cạnh nét dày `==>` trên sơ đồ gốc (đã kiểm chứng K2, diagram-contract §2); không dấu = theo doc. Sửa bản đồ gốc rồi chạy lại script.

← [[Bản đồ não]]

## Thành phần

- [[BP_ComboManager]]
- [[BP_FoffPlayerController]]
- [[BP_FurnitureActor]]
- [[BP_FurnitureInputManager]]
- [[BP_FurnitureSceneManager]]
- [[BP_FurnitureUserPrefsManager]]
- [[BP_GizmoController]]
- [[BP_GroupsContainer]] *(chưa có doc)*
- [[BP_UndoManager]]
- [[BP_UserPreferencesSave]] *(chưa có doc)*
- [[EntityIdLibrary_Reference]]
- [[Foff_GameInstance]] *(chưa có doc)*
- [[MaterialSlotService_Reference]]
- [[SaveGameMenu]] *(chưa có doc)*
- [[WBP_FOFF_ToolDemo]] *(chưa có doc)*
- [[WBP_FurnitureInventory]]
- [[WBP_Toast]]

## Ai gọi ai

- [[WBP_FOFF_ToolDemo]] → [[BP_FurnitureInputManager]] — sinh ra các manager · Spawn (Event Construct, Then 0..13)
- [[WBP_FOFF_ToolDemo]] → [[BP_UndoManager]] — sinh ra · Spawn
- [[WBP_FOFF_ToolDemo]] → [[BP_ComboManager]] — sinh ra (⚠ doc còn ghi Level BP) · Spawn
- [[WBP_FOFF_ToolDemo]] → [[BP_FurnitureSceneManager]] — sinh ra · Spawn
- [[WBP_FOFF_ToolDemo]] → [[BP_FurnitureUserPrefsManager]] — sinh ra · Spawn
- [[WBP_FOFF_ToolDemo]] → [[WBP_Toast]] — tạo toast + gắn vào GameInstance · Create + SET GI.ToastRef
- [[WBP_FOFF_ToolDemo]] → [[BP_UndoManager]] — lưu mốc đầu tiên · CaptureSnapshot(Initial)
- [[WBP_FOFF_ToolDemo]] → [[WBP_FurnitureInventory]] — mở inventory khi bấm nút · Open widget
- [[BP_UndoManager]] → [[BP_FurnitureActor]] — tạo lại đồ khi Undo + đặt lại mã + giữ nguyên PersistentID (guard) · SpawnFurnitureCopy(), SET RowName, SET PersistentID
- [[BP_UndoManager]] → [[BP_FurnitureInputManager]] — chọn lại / bỏ chọn sau khôi phục · SelectActors() / DeselectAll()
- [[BP_FurnitureActor]] → [[EntityIdLibrary_Reference]] — sinh/giữ ID lúc actor tải xong (Event ActorLoaded) · EnsurePersistentId()
- [[BP_FurnitureInputManager]] → [[EntityIdLibrary_Reference]] — sinh ID cho đồ mới (Duplicate/Paste) · SpawnFurnitureCopy: EnsurePersistentId()
- [[BP_UndoManager]] → [[WBP_FurnitureInventory]] — báo tin: khôi phục xong · Broadcast OnRestoreCompleted
- [[BP_ComboManager]] → [[BP_UndoManager]] — quay lui khi đổi combo lỗi · RestoreCurrentSnapshot()
- [[BP_GizmoController]] → [[BP_UndoManager]] — lưu mốc sau khi kéo · CaptureSnapshot(Move/Rotate/Scale)
- [[BP_FoffPlayerController]] → [[BP_UndoManager]] — phím Undo / Redo · UndoLastAction() / RedoLastAction()
- [[WBP_FurnitureInventory]] → [[BP_UndoManager]] — nghe khôi phục xong · Bind OnRestoreCompleted
- [[BP_FurnitureSceneManager]] → [[BP_FurnitureActor]] — sinh / xoá đồ theo danh mục · Spawn / Destroy
- [[BP_FurnitureSceneManager]] → [[SaveGameMenu]] — giữ tham chiếu menu Save · SaveGameMenuRef
- [[BP_FurnitureSceneManager]] → [[BP_FurnitureInputManager]] — yêu cầu bỏ chọn · DeselectMesh()
- [[BP_FurnitureUserPrefsManager]] → [[BP_UserPreferencesSave]] — ghi/đọc danh sách combo Gần đây · RecentComboIDs (SaveGame)
- [[BP_FurnitureInputManager]] → [[BP_GroupsContainer]] — ghi số đếm nhóm để lưu · GroupNameCounter, Groups
- [[WBP_FurnitureInventory]] → [[BP_UndoManager]] — mở / chốt / hủy phiên chỉnh param (U2.4-2.5) · BeginInteractiveEdit() / CommitInteractiveEdit() / CancelInteractiveEdit()
- [[BP_UndoManager]] → [[BP_FurnitureSceneManager]] — tìm lại đồ theo ID khi undo/chốt param — caller đầu tiên của Resolver · ResolveByPersistentId()
- [[BP_UndoManager]] → [[MaterialSlotService_Reference]] — đọc giá trị trước/sau + đảo 1 thông số · GetSlot*Param() / SetSlot*Param() (qua ApplyParamCommand)
- [[BP_UndoManager]] → [[WBP_FurnitureInventory]] — báo lịch sử vừa đổi (undo/redo param) · Broadcast OnHistoryChanged
- [[WBP_FurnitureInventory]] → [[BP_UndoManager]] — nghe lịch sử đổi → refresh panel · Bind OnHistoryChanged → RefreshParamPanel()
