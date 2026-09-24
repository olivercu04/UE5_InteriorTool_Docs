# Luồng 3e - Vật liệu Material

> Tự sinh từ [[Architecture_Map]] v1.5 mục **3e — Vật liệu (Material)** (24/09/2026). Dấu ✓K2 = cạnh nét dày `==>` trên sơ đồ gốc (đã kiểm chứng K2, diagram-contract §2); không dấu = theo doc. Sửa bản đồ gốc rồi chạy lại script.

← [[Bản đồ não]]

## Thành phần

- [[BP_ComboManager]]
- [[BP_FurnitureActor]]
- [[BP_FurnitureInputManager]]
- [[BP_UndoManager]]
- [[FurnitureFilterLibrary_Reference]]
- [[InteriorColorPicker]]
- [[MaterialSlotService_Reference]]
- [[WBP_DetailPopup]]
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
- [[WBP_ParamScalarRow]] → [[WBP_FurnitureInventory]] — báo bắt đầu / đang kéo / thả · OnEditBegin(ParamName) → Handle_ScalarBegin, OnPreviewChanged, OnEditCommitted
- [[WBP_ParamColorRow]] → [[WBP_FurnitureInventory]] — báo bắt đầu / đang chỉnh / thả · OnEditBegin(ParamName) → Handle_ColorBegin, OnPreviewChanged, OnEditCommitted
- [[WBP_FurnitureInventory]] → [[BP_UndoManager]] — mở/chốt/hủy phiên chỉnh (chi tiết ở 3d) · Begin/Commit/CancelInteractiveEdit()
- [[BP_FurnitureActor]] → [[WBP_FurnitureInventory]] — đồng bộ slot chọn + highlight + refresh panel sau kéo-thả · SET SelectedSlotIndex/Name, HighlightSwatchByIndex(), RefreshParamPanel()
