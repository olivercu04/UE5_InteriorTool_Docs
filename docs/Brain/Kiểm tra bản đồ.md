# Kiểm tra bản đồ (tự sinh)

> Sinh bằng `Brain/_tools/build.py` từ [[Architecture_Map]] — ĐỪNG sửa tay. Mục ❌, ⚠ và 🔗 phải về 0 thì bản đồ mới khớp và dùng được.
> ← [[Bản đồ não]] · [[Chỉ mục hàm & biến]]

**Tóm tắt:** ❌ thiếu cạnh 0 · ⚠ Phần 3 tụt bằng chứng 0 · 🔗 link gãy 0 · ℹ Phần 5 có thể tụt 1 · ? tồn đọng 12 · thẻ chưa có link 31 · mục 5x chưa thuộc luồng 0 · luồng thiếu dòng Kiểm chứng/Nguồn 0

## ❌ Cặp gọi nhau ở Phần 5 nhưng Phần 3 không có cạnh (0)
> Thêm cạnh vào sơ đồ 3x phù hợp (nét đứt nếu chỉ theo doc), rồi chạy lại.

- (không có)

## ⚠ Phần 3 tụt bằng chứng — Phần 5 đã ✓K2 mà Phần 3 còn đứt (0)
> Nâng cạnh Phần 3 lên `==>` + nhãn ngày K2 (hoặc tách cạnh nếu nhãn trộn nhiều hàm).

- (không có)

## 🔗 Link gãy trong Brain/ và Architecture_Map (0)
> Tên file / mục (heading) không còn — thường do đổi tên. Sửa link ở file nguồn (file tự sinh thì sửa script).

- (không có)

## ℹ Phần 5 có thể tụt — mũi tên đứt nhưng Phần 3 đã ✓K2 đúng hàm này (1)
> Xem lại: có thể hợp lệ (Phần 3 chỉ K2 1 phần nhãn), hoặc Phần 5 quên nâng.

- [[5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas|5b b15]] `BP_UndoManager→MaterialSlotService_Reference` về Before, 0 entry · `ApplyParamCommand() → SetSlotScalarParam()`  ← Phần 3: 3d "đọc giá trị trước/sau + đảo 1 thông số · GetSlot*Param() / SetSlot*Param() (qua ApplyParamCommand)"

## ? tồn đọng theo luồng

- [[5e - Undo 1 entry Snapshot — RestoreSnapshot (destroy + spawn lại).canvas|5e]]: 1 mũi tên có `?` · 1 dòng **?** dưới sơ đồ
- [[5f - Kéo gizmo Move (1 món · nhiều món qua Pivot).canvas|5f]]: 1 mũi tên có `?` · 1 dòng **?** dưới sơ đồ
- [[5g - Mở tool và mở kho đồ.canvas|5g]]: 0 mũi tên có `?` · 2 dòng **?** dưới sơ đồ
- [[5i - Kéo đồ từ kho thả vào phòng.canvas|5i]]: 1 mũi tên có `?` · 1 dòng **?** dưới sơ đồ
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m]]: 1 mũi tên có `?` · 1 dòng **?** dưới sơ đồ
- [[5r - Đặt combo từ thư viện vào phòng.canvas|5r]]: 0 mũi tên có `?` · 1 dòng **?** dưới sơ đồ
- [[5t - Lưu cảnh và mở lại cảnh (EMS).canvas|5t]]: 0 mũi tên có `?` · 1 dòng **?** dưới sơ đồ

## 🎯 K2 đáng xin nhất — mũi tên đứt dùng ở nhiều luồng nhất
> 1 export nâng được nhiều mũi tên nhất. Export đúng hàm ở cột "Hàm / biến".

| Luồng | Từ → Tới | Hàm / biến |
|---|---|---|
| 3: 5e, 5p, 5t | `BP_FurnitureActor` → `MaterialSlotService_Reference` | `ApplyLoadedMaterialToSlot` |
| 3: 5k, 5l, 5m | `BP_FurnitureInputManager` → `BP_UndoManager` | `CaptureSnapshot` |
| 2: 5a, 5e | `BP_FurnitureInputManager` → `WBP_FurnitureInventory` | `OnSelectionChanged` |
| 1: 5r | `BP_ComboManager` → `BP_FurnitureInputManager` | `DeselectAll` |
| 1: 5r | `BP_ComboManager` → `BP_FurnitureInputManager` | `ExitEditModeFull` |
| 1: 5s | `BP_ComboManager` → `BP_FurnitureInputManager` | `GetAllDescendantActors` |
| 1: 5r | `BP_ComboManager` → `BP_FurnitureInputManager` | `SpawnFurnitureCopy` |
| 1: 5r | `BP_ComboManager` → `BP_UndoManager` | `CaptureSnapshot` |
| 1: 5s | `BP_ComboManager` → `BP_UndoManager` | `RestoreCurrentSnapshot` |
| 1: 5q | `BP_ComboManager` → `ComboSerializer_Reference` | `ComboToJson` |

## 🧭 K2 cần xin khi đóng gate — theo thao tác (Lxx)
> Đóng gate: mở đúng các Lxx gate đã đụng → xin K2 các hàm dưới (ưu tiên hàm lặp nhiều mũi tên). K2 gửi lúc xác nhận flow trong task đã nâng liền rồi thì không còn ở đây.
> Đếm = số mũi tên đứt (không tính bước của User). `?` = mũi tên còn dấu hỏi.

- [[L01 · Mở tool và kho đồ]] (5g): 6 đứt → `ExitReplaceMode` (WBP_FurnitureInventory) · `FilterByFolderPath` (WBP_FurnitureInventory) · `OnRestoreCompleted` (BP_UndoManager) · `OnSceneRestored` (BP_UndoManager) · `OnSelectionChanged` (BP_FurnitureInputManager) · `OnSelectionChangedMaterial` (BP_FurnitureInputManager)
- [[L02 · Tìm đồ trong kho]] (5h): 8 đứt → `FilterBySearch` (WBP_FurnitureInventory ×2) · `AddItem` (WBP_FurnitureCard) · `DisplayPage` (WBP_FurnitureInventory) · `FilterByFolderPath` (WBP_FurnitureInventory) · `FilterFurnitureRows` (FurnitureFilterLibrary_Reference) · `OnListItemObjectSet` (WBP_FurnitureCard)
- [[L03 · Kéo đồ vào phòng]] (5i): 12 đứt · 1 `?` → `AddRecentMesh` (BP_FurnitureUserPrefsManager) · `CaptureSnapshot` (BP_UndoManager) · `DeactivateGizmo` (WBP_FurnitureCard) · `DeactivateGizmo` (BP_FurnitureInputManager) · `EnsurePersistentId` (EntityIdLibrary_Reference) · `GetCurrentEditScope` (BP_FurnitureInputManager)
- [[L04 · Chọn đồ]] (5a, 5j): 4 đứt → `ActivateGizmo` (BP_GizmoController) · `DeactivateGizmo` (BP_GizmoController) · `OnMeshSelected` (WBP_FurnitureInventory) · `OnSelectionChanged` (WBP_FurnitureInventory) · `OnSelectionChanged` (WBP_MeshControls) · `OnSelectionChangedInfoBar` (WBP_MeshControls)
- [[L05 · Di chuyển và xoay đồ]] (5f, 5k): 15 đứt · 1 `?` → `RefreshOffsets` (BP_PivotActor ×2) · `ActivateGizmo` (BP_GizmoController) · `ApplyTransformToChildren` (BP_FurnitureActor) · `CaptureSnapshot` (BP_UndoManager) · `DeactivateGizmo` (BP_GizmoController) · `Event Tick đọc phím mỗi frame, cùng đuôi` (BP_FurnitureInputManager)
- [[L06 · Nhóm đồ và sửa nhóm]] (5l): 11 đứt → `CaptureSnapshot` (BP_UndoManager ×2) · `ComputeSelectionUnits` (BP_FurnitureInputManager) · `EnterEditMode` (BP_FurnitureInputManager) · `ExitEditModeFull` (BP_FurnitureInputManager) · `ExitEditModeOneLevel` (BP_FurnitureInputManager) · `GenerateGroupID` (BP_FurnitureInputManager)
- [[L07 · Menu chuột phải và phím tắt]] (5m): 8 đứt · 1 `?` → `CaptureSnapshot` (BP_UndoManager ×3) · `CopyMesh` (BP_FurnitureInputManager ×2) · `SpawnFurnitureCopy` (BP_FurnitureInputManager ×2) · `DeleteSelected` (BP_FurnitureActor) · `DeselectAll` (BP_UndoManager) · `DuplicateMesh` (BP_FurnitureInputManager)
- [[L08 · Thay đồ]] (5n): 7 đứt → `AddRecentMesh` (BP_FurnitureUserPrefsManager) · `CaptureSnapshot` (BP_UndoManager) · `DeselectAll` (BP_FurnitureInputManager) · `ExitReplaceMode` (BP_FurnitureInputManager) · `SelectActors` (BP_FurnitureInputManager) · `mọi thẻ hiện nút Thay` (WBP_FurnitureCard)
- [[L09 · Đổi vật liệu]] (5o, 5p): 9 đứt → `CaptureSnapshot` (BP_UndoManager ×2) · `AddRecentMaterial` (BP_FurnitureUserPrefsManager) · `ApplyLoadedMaterialToSlot` (MaterialSlotService_Reference) · `ApplyMaterial` (WBP_FurnitureInventory) · `BP_DragDropOperation_Material` (WBP_DragOverlay_FurnitureCard) · `HighlightSwatchByIndex` (WBP_FurnitureInventory)
- [[L10 · Chỉnh thông số vật liệu]] (5b): 7 đứt → `SetSlotScalarParam` (MaterialSlotService_Reference ×2) · `ApplyParamCommand` (MaterialSlotService_Reference) · `BeginInteractiveEdit` (BP_UndoManager) · `CancelInteractiveEdit` (BP_UndoManager) · `CommitInteractiveEdit` (BP_UndoManager) · `OnEditBegin` (WBP_FurnitureInventory)
- [[L11 · Combo]] (5q, 5r, 5s): 24 đứt → `SpawnComboByID` (BP_ComboManager ×2) · `CalculateComboAnchor` (BP_FurnitureInputManager) · `CaptureSnapshot` (BP_UndoManager) · `ComboToJson` (ComboSerializer_Reference) · `DeselectAll` (BP_FurnitureInputManager) · `DestroyComboCluster` (BP_FurnitureInputManager)
- [[L12 · Lưu và mở cảnh]] (5t): 9 đứt → `ApplyLoadedMaterialToSlot` (MaterialSlotService_Reference) · `ApplyParamsJsonToSlot` (MaterialSlotService_Reference) · `AsyncWaitForOperation` (BP_FurnitureActor) · `DeselectMesh` (BP_FurnitureInputManager) · `EnsurePersistentId` (EntityIdLibrary_Reference) · `LoadAsset_Blocking` (BP_FurnitureActor)
- [[L13 · Hoàn tác và làm lại]] (5c, 5d, 5e): 19 đứt · 1 `?` → `RefreshParamPanel` (WBP_FurnitureInventory ×2) · `SelectActors` (BP_FurnitureInputManager ×2) · `2. xoá hết đồ` (BP_UndoManager) · `ApplyLoadedMaterialToSlot` (MaterialSlotService_Reference) · `ApplyParamsJsonToSlot` (MaterialSlotService_Reference) · `ApplyRestoredActor` (WBP_FurnitureInventory)

## Thẻ Canvas có tên hàm nhưng chưa tìm được mục trong doc (31)
> Doc chưa có heading cho hàm này (hoặc tên lệch) → thẻ không có link ↗.

- [[5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas|5b b2]] `WBP_ParamScalarRow→WBP_FurnitureInventory` báo tin · `OnEditBegin(ParamName) → Handle_ScalarBegin` — tìm: OnEditBegin
- [[5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas|5b b7]] `WBP_ParamScalarRow→WBP_FurnitureInventory` báo tin · `OnPreviewChanged(ParamName, Value)` — tìm: OnPreviewChanged
- [[5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas|5b b9]] `WBP_ParamScalarRow→WBP_FurnitureInventory` báo tin · `OnEditCommitted → Handle_ScalarCommit` — tìm: OnEditCommitted
- [[5g - Mở tool và mở kho đồ.canvas|5g b2]] `BP_FurnitureInputManager→BP_FurnitureInputManager` bật bộ phím nội thất 1 lần, giữ suốt phiên · `BeginPlay → EnableInput → AddMappingContext(LM_FurnitureInput, Priority 5)` — tìm: AddMappingContext
- [[5h - Tìm đồ trong kho (gõ tìm · thư mục · Gần đây · Yêu thích).canvas|5h b1]] `User→WBP_FurnitureInventory` gõ chữ · `CommonSearchBox OnTextChanged (chờ 0.3s mới lọc)` — tìm: OnTextChanged
- [[5h - Tìm đồ trong kho (gõ tìm · thư mục · Gần đây · Yêu thích).canvas|5h b6]] `User→WBP_FurnitureInventory` BTN_RecentCategory / BTN_FavoriteCategory → FilterByCategory("Recent" / "Favorite") · `` — tìm: FilterByCategory
- [[5h - Tìm đồ trong kho (gõ tìm · thư mục · Gần đây · Yêu thích).canvas|5h b8]] `WBP_FurnitureInventory→FurnitureFilterLibrary_Reference` lọc DT_FurnitureCatalog theo chữ + thư mục + loại (tối đa 200) · `FilterFurnitureRows() → AllFilteredFurnitureRows` — tìm: FilterFurnitureRows
- [[5h - Tìm đồ trong kho (gõ tìm · thư mục · Gần đây · Yêu thích).canvas|5h b10]] `WBP_FurnitureInventory→WBP_FurnitureCard` mỗi ô chỉ mang RowName, ListView tái dùng thẻ · `Make BP_FurnitureItemView → AddItem(CTV_FurnitureCard)` — tìm: AddItem
- [[5i - Kéo đồ từ kho thả vào phòng.canvas|5i b2]] `WBP_FurnitureCard→WBP_FurnitureCard` tắt gizmo trước tiên · `DeactivateGizmo()` — tìm: DeactivateGizmo
- [[5i - Kéo đồ từ kho thả vào phòng.canvas|5i b8]] `WBP_DragOverlay_FurnitureCard→BP_FurnitureInputManager` tắt gizmo · `GizmoControllerRef.DeactivateGizmo() ?` — tìm: DeactivateGizmo
- [[5i - Kéo đồ từ kho thả vào phòng.canvas|5i b13]] `WBP_DragOverlay_FurnitureCard→BP_FurnitureUserPrefsManager` thêm vào Gần đây · `AddRecentMesh(RowName)` — tìm: AddRecentMesh
- [[5k - Nhích đồ bằng phím mũi tên (Nudge).canvas|5k b1]] `User→BP_FurnitureInputManager` bấm phím mũi tên (giữ = lặp mỗi 0.1s) · `IA_FurnitureNudge (Triggered) → NudgeMesh(Direction)` — tìm: NudgeMesh, IA_FurnitureNudge
- [[5l - Nhóm đồ và vào - ra sửa nhóm.canvas|5l b11]] `BP_FurnitureInputManager→WBP_MeshControls` báo tin đang sửa nhóm → hiện thanh sửa nhóm · `Broadcast OnEditModeChanged(True, GroupID)` — tìm: OnEditModeChanged
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b1]] `User→BP_FurnitureInputManager` bấm rồi thả chuột phải · `IA_RMBPress → OnRMBPressed, IA_RMBRelease → OnRMBReleased` — tìm: IA_RMBPress, OnRMBPressed, IA_RMBRelease, OnRMBReleased
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b2]] `BP_FurnitureInputManager→BP_FurnitureInputManager` thả nhanh dưới 0.3s VÀ camera không xoay → mới là click · `OnRMBReleased → OnRightClick()` — tìm: OnRightClick, OnRMBReleased
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b3]] `BP_FurnitureInputManager→WBP_ContextMenu` dựng menu tại chỗ chuột · `OnRightClick → Create WBP_ContextMenu` — tìm: OnRightClick
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b4]] `BP_FurnitureInputManager→WBP_ContextMenuItem` tạo 11 dòng menu · `Create Widget (OnRightClick)` — tìm: OnRightClick
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b7]] `User→BP_FurnitureInputManager` Ctrl+C / Ctrl+V / Ctrl+D · `IA_FurnitureCopy / Paste / Duplicate → CopyMesh() / PasteMesh() / DuplicateMesh()` — tìm: CopyMesh, PasteMesh, DuplicateMesh, IA_FurnitureCopy
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b8]] `BP_FurnitureInputManager→BP_FurnitureInputManager` chép vị trí so với tâm nhóm + RowName + MaterialSlots · `CopyMesh() → ClipboardActors` — tìm: CopyMesh
- [[5n - Thay đồ (Replace).canvas|5n b12]] `WBP_FurnitureCard→BP_FurnitureUserPrefsManager` thêm vào Gần đây · `AddRecentMesh(CardRowName)` — tìm: AddRecentMesh
- [[5o - Đổi vật liệu bằng cách bấm thẻ (1 hoặc nhiều món).canvas|5o b10]] `WBP_FurnitureInventory→WBP_FurnitureInventory` hẹn ghi sổ 0.5s, bấm liên tục chỉ ghi 1 lần · `SetTimer("CaptureMaterialSnapshot", 0.5)` — tìm: SetTimer
- [[5o - Đổi vật liệu bằng cách bấm thẻ (1 hoặc nhiều món).canvas|5o b11]] `WBP_FurnitureInventory→BP_FurnitureUserPrefsManager` thêm vào Gần đây · `AddRecentMaterial(PendingRowName)` — tìm: AddRecentMaterial
- [[5p - Đổi vật liệu bằng cách kéo thẻ thả lên đồ.canvas|5p b6]] `WBP_DragOverlay_FurnitureCard→BP_FurnitureSceneManager` báo lỗi nhẹ · `ToastRef.ShowToast("Chỉ áp vật liệu lên đồ nội thất")` — tìm: ShowToast
- [[5p - Đổi vật liệu bằng cách kéo thẻ thả lên đồ.canvas|5p b11]] `BP_FurnitureActor→BP_FurnitureUserPrefsManager` thêm vào Gần đây · `AddRecentMaterial(Apply_PendingRowName)` — tìm: AddRecentMaterial
- [[5q - Lưu combo (lưu mới · ghi đè).canvas|5q b4]] `BP_FurnitureInputManager→BP_FurnitureInputManager` tìm kho đồ, không có thì chỉ in log · `GetAllWidgetsOfClass(WBP_FurnitureInventory) → IsValid` — tìm: GetAllWidgetsOfClass
- [[5q - Lưu combo (lưu mới · ghi đè).canvas|5q b7]] `BP_FurnitureInputManager→BP_FurnitureInputManager` đóng menu chuột phải · `ContextMenuRef.Hide() → SET ContextMenuRef = None` — tìm: Hide
- [[5q - Lưu combo (lưu mới · ghi đè).canvas|5q b8]] `WBP_FurnitureInventory→WBP_SaveComboDialog` tạo hộp thoại điền sẵn tên / thư mục / tag, gắn 3 nút · `Create WBP_SaveComboDialog → Bind OnDialogConfirmed, OnDialogConfirmedOverwrite, OnDialogCancelled` — tìm: OnDialogConfirmed, OnDialogConfirmedOverwrite, OnDialogCancelled
- [[5q - Lưu combo (lưu mới · ghi đè).canvas|5q b10]] `WBP_SaveComboDialog→WBP_FurnitureInventory` báo tin nút đã bấm · `Broadcast OnDialogConfirmed / OnDialogConfirmedOverwrite / OnDialogCancelled` — tìm: OnDialogConfirmed, OnDialogConfirmedOverwrite, OnDialogCancelled
- [[5q - Lưu combo (lưu mới · ghi đè).canvas|5q b15]] `BP_ComboManager→WBP_FurnitureInventory` chụp xong mới báo tin → tab Combo nạp lại · `Broadcast OnComboLibraryChanged` — tìm: OnComboLibraryChanged
- [[5t - Lưu cảnh và mở lại cảnh (EMS).canvas|5t b6]] `BP_FurnitureActor→BP_FurnitureActor` chờ EMS nạp xong biến SaveGame, MeshPath rỗng thì tự huỷ · `Event ActorLoaded → AsyncWaitForOperation(CT_Load)` — tìm: AsyncWaitForOperation
- [[5t - Lưu cảnh và mở lại cảnh (EMS).canvas|5t b8]] `BP_FurnitureActor→BP_FurnitureActor` nạp mesh (đồng bộ) · `LoadAsset_Blocking(MeshPath) → SetStaticMesh` — tìm: LoadAsset_Blocking

## Mục 5x chưa thuộc note luồng nào (0)
> Mỗi mục 5x phải được nhúng trong đúng 1 note `Brain/Luồng/Lxx` — không thì người đọc theo hành trình sẽ không gặp nó.

- (không có)

## Mục 5x thiếu dòng "Kiểm chứng K2:" hoặc "Nguồn:" (0)

- (không có)
