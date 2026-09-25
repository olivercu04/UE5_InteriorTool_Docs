# Kết nối 3b - Combo lưu spawn thay combo

> Tự sinh từ [[Architecture_Map]] mục **3b — Combo (lưu / spawn / thay combo)**. Dấu ✓K2 = cạnh nét dày `==>` trên sơ đồ gốc (đã kiểm chứng K2, diagram-contract §2); không dấu = theo doc. Sửa bản đồ gốc rồi chạy lại script.

← [[Bản đồ não]] · Mức asset (ai nói chuyện với ai). Theo từng THAO TÁC của người dùng → note `L01…L13` trong `Brain/Luồng/`.

## Thành phần

- [[BP_ComboGhostActor]]
- [[BP_ComboItemView]]
- [[BP_ComboManager]]
- [[BP_DragDropOperation_ComboCard]] *(chưa có doc)*
- [[BP_FurnitureActor]]
- [[BP_FurnitureInputManager]]
- [[BP_FurnitureUserPrefsManager]]
- [[BP_UndoManager]]
- [[ComboSerializer_Reference]]
- [[Foff_GameInstance]] *(chưa có doc)*
- [[UComboThumbnail]] *(chưa có doc)*
- [[WBP_ComboCard]]
- [[WBP_ContextMenuItem]] *(chưa có doc)*
- [[WBP_DragOverlay_FurnitureCard]]
- [[WBP_FolderTreePicker]]
- [[WBP_FurnitureInventory]]
- [[WBP_LibraryContextMenu]]
- [[WBP_SaveComboDialog]]

## Ai gọi ai

- [[BP_FurnitureInputManager]] → [[BP_ComboManager]] — ra lệnh đổi combo · ExecuteComboReplace() → ReplaceCombo() ✓K2
- [[BP_ComboManager]] → [[BP_FurnitureInputManager]] — giữ tham chiếu + gọi huỷ cụm cũ · InputManagerRef, DestroyComboCluster()
- [[BP_ComboManager]] → [[BP_UndoManager]] — giữ tham chiếu + gọi quay lui · UndoManagerRef, RestoreCurrentSnapshot()
- [[BP_ComboManager]] → [[BP_FurnitureActor]] — gán vật liệu cho đồ · F_ApplyMaterialOverrides()
- [[BP_ComboManager]] → [[UComboThumbnail]] — chụp ảnh bìa combo · BeginComboCapture / FinishComboCapture ✓K2
- [[BP_ComboManager]] → [[ComboSerializer_Reference]] — ghi/đọc file + thư mục combo · save / load
- [[BP_ComboManager]] → [[Foff_GameInstance]] — hiện thông báo · GameInstance.ToastRef.ShowToast()
- [[BP_ComboManager]] → [[WBP_FurnitureInventory]] — báo tin: thư viện combo đổi · Broadcast OnComboLibraryChanged
- [[WBP_FurnitureInventory]] → [[BP_ComboManager]] — giữ tham chiếu + xin ảnh bìa · ComboManagerRef, GetComboThumbnail()
- [[WBP_FurnitureInventory]] → [[BP_ComboItemView]] — tạo 1 ô cho mỗi combo · Make BP_ComboItemView
- [[WBP_FurnitureInventory]] → [[ComboSerializer_Reference]] — đổi tên / xoá thư mục combo · folder ops
- [[WBP_FurnitureInventory]] → [[WBP_SaveComboDialog]] — mở + nghe dialog lưu combo · SaveComboDialogRef, Bind 4 sự kiện
- [[WBP_FurnitureInventory]] → [[WBP_LibraryContextMenu]] — mở + nghe menu chuột phải · LibraryMenuRef, Bind 4 sự kiện
- [[WBP_FurnitureInventory]] → [[BP_FurnitureUserPrefsManager]] — gọi bỏ combo khỏi Gần đây · RemoveRecentCombo()
- [[BP_ComboItemView]] → [[BP_ComboManager]] — dùng chung bộ nhớ ảnh bìa · Cmb_ThumbnailCache
- [[WBP_ComboCard]] → [[WBP_FurnitureInventory]] — giữ tham chiếu + gọi xoá / chuột phải · InventoryRef, RequestDeleteCombo()
- [[WBP_ComboCard]] → [[BP_FurnitureInputManager]] — gọi đổi combo · ExecuteComboReplace()
- [[WBP_ComboCard]] → [[BP_ComboItemView]] — nhận dữ liệu combo · IUserObjectListEntry
- [[WBP_ComboCard]] → [[BP_ComboGhostActor]] — tạo bóng preview lúc kéo · Spawn BP_ComboGhostActor
- [[WBP_ComboCard]] → [[BP_DragDropOperation_ComboCard]] — tạo gói kéo-thả mang ComboID · Create BP_DragDropOperation_ComboCard
- [[WBP_ComboCard]] → [[Foff_GameInstance]] — đọc tham chiếu inventory · GameInstance.FurnitureInventoryRef
- [[WBP_DragOverlay_FurnitureCard]] → [[BP_ComboGhostActor]] — nhận diện bóng combo lúc thả · Cast BP_ComboGhostActor
- [[WBP_DragOverlay_FurnitureCard]] → [[BP_DragDropOperation_ComboCard]] — đọc ComboID từ gói lúc thả · Cast BP_DragDropOperation_ComboCard
- [[WBP_SaveComboDialog]] → [[WBP_FolderTreePicker]] — nhúng cây thư mục · Picker, ExpandToPath()
- [[WBP_SaveComboDialog]] → [[WBP_FurnitureInventory]] — báo tin: bấm Lưu / Ghi đè / Huỷ · Broadcast
- [[WBP_LibraryContextMenu]] → [[WBP_ContextMenuItem]] — tạo từng dòng menu · Create WBP_ContextMenuItem
- [[BP_FurnitureInputManager]] → [[WBP_FurnitureInventory]] — mở hộp thoại lưu combo · OpenSaveComboDialog(SelectedActors, Center) ✓K2
- [[BP_FurnitureInputManager]] → [[WBP_FurnitureInventory]] — mở tab Combo ở chế độ thay · StartReplaceComboMode → SwitchInventoryMode(Combo) / FilterComboByFolder() / RefreshComboCardReplaceMode()
- [[WBP_FurnitureInventory]] → [[BP_ComboManager]] — lưu combo (mới / ghi đè) · SaveComboFromSelection()
- [[WBP_DragOverlay_FurnitureCard]] → [[BP_ComboManager]] — đặt combo khi thả · SpawnComboByID(ComboID, SpawnLocation)
- [[BP_ComboManager]] → [[BP_FurnitureInputManager]] — sinh từng món + chọn cả cụm · ExitEditModeFull() / SpawnFurnitureCopy() / SelectActors() / GetAllDescendantActors()
- [[BP_ComboManager]] → [[BP_UndoManager]] — ghi sổ khi đặt / thay combo · CaptureSnapshot(SpawnCombo / ReplaceCombo)
