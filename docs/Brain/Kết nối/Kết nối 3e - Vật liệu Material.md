# Kết nối 3e - Vật liệu Material

> Tự sinh từ [[Architecture_Map]] mục **3e — Vật liệu (Material)**. Dấu ✓K2 = cạnh nét dày `==>` trên sơ đồ gốc (đã kiểm chứng K2, diagram-contract §2); không dấu = theo doc. Sửa bản đồ gốc rồi chạy lại script.

← [[Bản đồ não]] · Mức asset (ai nói chuyện với ai). Theo từng THAO TÁC của người dùng → note `L01…L13` trong `Brain/Luồng/`.

## Thành phần

- [[BP_ComboManager]]
- [[BP_FurnitureActor]]
- [[BP_FurnitureInputManager]]
- [[BP_FurnitureSceneManager]]
- [[BP_FurnitureUserPrefsManager]]
- [[BP_UndoManager]]
- [[FurnitureFilterLibrary_Reference]]
- [[InteriorColorPicker]]
- [[MaterialSlotService_Reference]]
- [[WBP_DetailPopup]]
- [[WBP_DragOverlay_FurnitureCard]]
- [[WBP_FurnitureInventory]]
- [[WBP_MaterialCard]]
- [[WBP_MaterialInspector]]
- [[WBP_MaterialParamPanel]]
- [[WBP_MeshControls]]
- [[WBP_ParamColorRow]]
- [[WBP_ParamScalarRow]]
- [[WBP_SlotSwatch]] *(chưa có doc)*

## Ai gọi ai

- [[WBP_FurnitureInventory]] → [[FurnitureFilterLibrary_Reference]] — lọc vật liệu · FilterMaterialItems() (C++)
- [[WBP_FurnitureInventory]] → [[MaterialSlotService_Reference]] — reset param / reset về mặc định · ResetSlotToAssetDefault() / ResetAllSlotsToAssetDefault() ✓K2
- [[WBP_FurnitureInventory]] → [[MaterialSlotService_Reference]] — gán vật liệu vào slot (kéo-thả G5) · ApplyLoadedMaterialToSlot() → LoadAndApplyMaterial ✓K2
- [[WBP_FurnitureInventory]] → [[BP_FurnitureActor]] — gán MI theo slot cho đồ · TargetFurnitureActor
- [[WBP_FurnitureInventory]] → [[WBP_MaterialCard]] — đổ thẻ vật liệu vào lưới · TileView entry
- [[WBP_FurnitureInventory]] → [[WBP_SlotSwatch]] — tạo + nghe ô màu slot · Create WBP_SlotSwatch, Bind OnSwatchClicked
- [[WBP_MeshControls]] → [[WBP_DetailPopup]] — tạo popup chi tiết khi bấm Info · Create WBP_DetailPopup
- [[WBP_DetailPopup]] → [[BP_FurnitureInputManager]] — vào chế độ thay đồ · StartReplaceMode() ✓K2
- [[WBP_DetailPopup]] → [[BP_UndoManager]] — lưu mốc khi khoá / reset scale · CaptureSnapshot(Scale)
- [[WBP_DetailPopup]] → [[BP_FurnitureActor]] — chỉnh scale đồ đang chọn · SelectedFurnitureActor
- [[BP_ComboManager]] → [[BP_FurnitureActor]] — gán vật liệu khi spawn combo · F_ApplyMaterialOverrides()
- [[WBP_MaterialInspector]] → [[WBP_MaterialParamPanel]] — forward 5 hàm xuống panel con · SetHeader/ClearParamRows/AddParamRow/ShowParamEmptyState/SetResetEnabled → ParamPanelRef
- [[WBP_ParamColorRow]] → [[InteriorColorPicker]] — nhúng picker, gọi SetColor/GetColor + nghe 3 dispatcher · InteriorColorPicker (UInteriorColorPickerWidget)
- [[WBP_ParamColorRow]] → [[MaterialSlotService_Reference]] — parse hex khi commit ô Hex · HexToLinearColor()
- [[WBP_FurnitureInventory]] → [[MaterialSlotService_Reference]] — tra từ điển param theo material · GetControlsForMaterial(SlotMaterial, DT_ParamMap) ✓K2
- [[WBP_FurnitureInventory]] → [[WBP_MaterialInspector]] — build/xóa danh sách row + empty-state · ClearParamRows()/AddParamRow()/ShowParamEmptyState(), SetVisibility ✓K2
- [[WBP_FurnitureInventory]] → [[WBP_ParamScalarRow]] — tạo row Scalar · Create WBP_ParamScalarRow → Setup() ✓K2
- [[WBP_FurnitureInventory]] → [[WBP_ParamColorRow]] — tạo row Color · Create WBP_ParamColorRow → Setup() ✓K2
- [[WBP_FurnitureInventory]] → [[MaterialSlotService_Reference]] — seed giá trị row = giá trị THẬT trên MID/MI (U2.5, thay Cast MID+fallback) · GetSlotScalarParam() / GetSlotVectorParam()
- [[WBP_ParamScalarRow]] → [[WBP_FurnitureInventory]] — báo đang kéo · OnPreviewChanged(ParamName, Value) ✓K2
- [[WBP_ParamScalarRow]] → [[WBP_FurnitureInventory]] — báo bắt đầu / thả · OnEditBegin(ParamName) → Handle_ScalarBegin, OnEditCommitted
- [[WBP_ParamColorRow]] → [[WBP_FurnitureInventory]] — báo đang chỉnh · OnPreviewChanged(ParamName, Value) ✓K2
- [[WBP_ParamColorRow]] → [[WBP_FurnitureInventory]] — báo bắt đầu / thả · OnEditBegin(ParamName) → Handle_ColorBegin, OnEditCommitted
- [[WBP_FurnitureInventory]] → [[BP_UndoManager]] — mở/chốt/hủy phiên chỉnh (chi tiết ở 3d) · Begin/Commit/CancelInteractiveEdit()
- [[BP_FurnitureActor]] → [[WBP_FurnitureInventory]] — đồng bộ slot chọn + highlight + refresh panel sau kéo-thả · SET SelectedSlotIndex/Name, HighlightSwatchByIndex(), RefreshParamPanel()
- [[BP_FurnitureActor]] → [[MaterialSlotService_Reference]] — gắn lại vật liệu + thông số từng slot sau khi tải mesh (Undo) · ApplyLoadedMaterialToSlot() → ApplyParamsJsonToSlot()
- [[WBP_MaterialCard]] → [[WBP_FurnitureInventory]] — bấm thẻ → áp cho món đang mở panel · ApplyMaterial(RowName)
- [[WBP_MaterialCard]] → [[WBP_DragOverlay_FurnitureCard]] — kéo thẻ → phủ lớp kéo-thả mang RowName · Create WBP_DragOverlay + BP_DragDropOperation_Material
- [[WBP_FurnitureInventory]] → [[BP_FurnitureUserPrefsManager]] — thêm vật liệu vào Gần đây · AddRecentMaterial() ✓K2
- [[WBP_DragOverlay_FurnitureCard]] → [[MaterialSlotService_Reference]] — tìm món + slot dưới điểm thả · TraceSlotUnderCursor() ✓K2
- [[WBP_DragOverlay_FurnitureCard]] → [[BP_FurnitureActor]] — giao việc đổi vật liệu cho món bị thả trúng · ApplyMaterialByRowName() ✓K2
- [[WBP_DragOverlay_FurnitureCard]] → [[BP_FurnitureSceneManager]] — báo thả trúng kiến trúc · ToastRef.ShowToast() ✓K2
- [[BP_FurnitureActor]] → [[BP_UndoManager]] — ghi sổ sau khi đổi vật liệu · CaptureSnapshot(ApplyMaterial)
- [[BP_FurnitureActor]] → [[BP_FurnitureUserPrefsManager]] — thêm vật liệu vào Gần đây · AddRecentMaterial()
