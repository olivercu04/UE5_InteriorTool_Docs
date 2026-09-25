# Kiểm tra bản đồ (tự sinh)

> Sinh bằng `Brain/_tools/build.py` từ [[Architecture_Map]] — ĐỪNG sửa tay. Mục ❌, ⚠ và 🔗 phải về 0 thì bản đồ mới khớp và dùng được.
> ← [[Bản đồ não]] · [[Chỉ mục hàm & biến]]

**Tóm tắt:** ❌ thiếu cạnh 0 · ⚠ Phần 3 tụt bằng chứng 0 · 🔗 link gãy 0 · ℹ Phần 5 có thể tụt 1 · ? tồn đọng 17 · thẻ chưa có link 29 · mục 5x chưa thuộc luồng 0 · luồng thiếu dòng Kiểm chứng/Nguồn 0

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
- [[5g - Mở tool và mở kho đồ.canvas|5g]]: 1 mũi tên có `?` · 1 dòng **?** dưới sơ đồ
- [[5i - Kéo đồ từ kho thả vào phòng.canvas|5i]]: 1 mũi tên có `?` · 1 dòng **?** dưới sơ đồ
- [[5l - Nhóm đồ và vào - ra sửa nhóm.canvas|5l]]: 2 mũi tên có `?` · 1 dòng **?** dưới sơ đồ
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m]]: 1 mũi tên có `?` · 1 dòng **?** dưới sơ đồ
- [[5q - Lưu combo (lưu mới · ghi đè).canvas|5q]]: 1 mũi tên có `?` · 0 dòng **?** dưới sơ đồ
- [[5r - Đặt combo từ thư viện vào phòng.canvas|5r]]: 0 mũi tên có `?` · 1 dòng **?** dưới sơ đồ
- [[5t - Lưu cảnh và mở lại cảnh (EMS).canvas|5t]]: 1 mũi tên có `?` · 1 dòng **?** dưới sơ đồ

## 🎯 K2 đáng xin nhất — mũi tên đứt dùng ở nhiều luồng nhất
> 1 export nâng được nhiều mũi tên nhất. Export đúng hàm ở cột "Hàm / biến".

| Luồng | Từ → Tới | Hàm / biến |
|---|---|---|
| 4: 5j, 5k, 5l, 5m | `BP_FurnitureInputManager` → `BP_UndoManager` | `CaptureSnapshot` |
| 3: 5e, 5p, 5t | `BP_FurnitureActor` → `MaterialSlotService_Reference` | `ApplyLoadedMaterialToSlot` |
| 3: 5b, 5c, 5d | `BP_UndoManager` → `WBP_FurnitureInventory` | `RefreshParamPanel` |
| 2: 5a, 5e | `BP_FurnitureInputManager` → `WBP_FurnitureInventory` | `OnSelectionChanged` |
| 1: 5r | `BP_ComboManager` → `BP_FurnitureInputManager` | `DeselectAll` |
| 1: 5r | `BP_ComboManager` → `BP_FurnitureInputManager` | `ExitEditModeFull` |
| 1: 5s | `BP_ComboManager` → `BP_FurnitureInputManager` | `GetAllDescendantActors` |
| 1: 5r | `BP_ComboManager` → `BP_FurnitureInputManager` | `SpawnFurnitureCopy` |
| 1: 5r | `BP_ComboManager` → `BP_UndoManager` | `CaptureSnapshot` |
| 1: 5s | `BP_ComboManager` → `BP_UndoManager` | `RestoreCurrentSnapshot` |

## Thẻ Canvas có tên hàm nhưng chưa tìm được mục trong doc (29)
> Doc chưa có heading cho hàm này (hoặc tên lệch) → thẻ không có link ↗.

- [[5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas|5b b2]] `WBP_ParamScalarRow→WBP_FurnitureInventory` báo tin · `OnEditBegin(ParamName) → Handle_ScalarBegin` — tìm: OnEditBegin
- [[5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas|5b b7]] `WBP_ParamScalarRow→WBP_FurnitureInventory` báo tin · `OnPreviewChanged(ParamName, Value)` — tìm: OnPreviewChanged
- [[5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas|5b b9]] `WBP_ParamScalarRow→WBP_FurnitureInventory` báo tin · `OnEditCommitted → Handle_ScalarCommit` — tìm: OnEditCommitted
- [[5h - Tìm đồ trong kho (gõ tìm · thư mục · Gần đây · Yêu thích).canvas|5h b1]] `User→WBP_FurnitureInventory` gõ chữ · `CommonSearchBox OnTextChanged (chờ 0.3s mới lọc)` — tìm: OnTextChanged
- [[5h - Tìm đồ trong kho (gõ tìm · thư mục · Gần đây · Yêu thích).canvas|5h b6]] `User→WBP_FurnitureInventory` BTN_RecentCategory / BTN_FavoriteCategory → FilterByCategory("Recent" / "Favorite") · `` — tìm: FilterByCategory
- [[5h - Tìm đồ trong kho (gõ tìm · thư mục · Gần đây · Yêu thích).canvas|5h b8]] `WBP_FurnitureInventory→FurnitureFilterLibrary_Reference` lọc DT_FurnitureCatalog theo chữ + thư mục + loại (tối đa 200) · `FilterFurnitureRows() → AllFilteredFurnitureRows` — tìm: FilterFurnitureRows
- [[5h - Tìm đồ trong kho (gõ tìm · thư mục · Gần đây · Yêu thích).canvas|5h b10]] `WBP_FurnitureInventory→WBP_FurnitureCard` mỗi ô chỉ mang RowName, ListView tái dùng thẻ · `Make BP_FurnitureItemView → AddItem(CTV_FurnitureCard)` — tìm: AddItem
- [[5i - Kéo đồ từ kho thả vào phòng.canvas|5i b2]] `WBP_FurnitureCard→WBP_FurnitureCard` tắt gizmo trước tiên · `DeactivateGizmo()` — tìm: DeactivateGizmo
- [[5i - Kéo đồ từ kho thả vào phòng.canvas|5i b8]] `WBP_DragOverlay_FurnitureCard→BP_FurnitureInputManager` tắt gizmo · `GizmoControllerRef.DeactivateGizmo() ?` — tìm: DeactivateGizmo
- [[5i - Kéo đồ từ kho thả vào phòng.canvas|5i b13]] `WBP_DragOverlay_FurnitureCard→BP_FurnitureUserPrefsManager` thêm vào Gần đây · `AddRecentMesh(RowName)` — tìm: AddRecentMesh
- [[5k - Nhích đồ bằng phím mũi tên (Nudge).canvas|5k b1]] `User→BP_FoffPlayerController` bấm phím mũi tên (giữ = lặp mỗi 0.1s) · `IA_FurnitureNudge (Triggered)` — tìm: IA_FurnitureNudge
- [[5k - Nhích đồ bằng phím mũi tên (Nudge).canvas|5k b2]] `BP_FoffPlayerController→BP_FurnitureInputManager` chuyển hướng bấm · `NudgeMesh(Direction)` — tìm: NudgeMesh
- [[5l - Nhóm đồ và vào - ra sửa nhóm.canvas|5l b11]] `BP_FurnitureInputManager→WBP_MeshControls` báo tin đang sửa nhóm → hiện thanh sửa nhóm · `Broadcast OnEditModeChanged(True, GroupID)` — tìm: OnEditModeChanged
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b1]] `User→BP_FurnitureInputManager` bấm rồi thả chuột phải · `IA_RMBPress → OnRMBPressed, IA_RMBRelease → OnRMBReleased` — tìm: IA_RMBPress, OnRMBPressed, IA_RMBRelease, OnRMBReleased
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b2]] `BP_FurnitureInputManager→BP_FurnitureInputManager` thả nhanh dưới 0.3s VÀ camera không xoay → mới là click · `OnRMBReleased → OnRightClick()` — tìm: OnRightClick, OnRMBReleased
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b3]] `BP_FurnitureInputManager→WBP_ContextMenu` dựng menu tại chỗ chuột · `OnRightClick → Create WBP_ContextMenu` — tìm: OnRightClick
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b4]] `BP_FurnitureInputManager→WBP_ContextMenuItem` tạo 11 dòng menu · `Create Widget (OnRightClick)` — tìm: OnRightClick
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b8]] `BP_FoffPlayerController→BP_FurnitureInputManager` chuyển thẳng · `IA_FurnitureCopy / Paste / Duplicate → CopyMesh() / PasteMesh() / DuplicateMesh()` — tìm: CopyMesh, PasteMesh, DuplicateMesh, IA_FurnitureCopy
- [[5m - Menu chuột phải và phím tắt (copy · dán · nhân bản · xoá).canvas|5m b9]] `BP_FurnitureInputManager→BP_FurnitureInputManager` chép vị trí so với tâm nhóm + RowName + MaterialSlots · `CopyMesh() → ClipboardActors` — tìm: CopyMesh
- [[5n - Thay đồ (Replace).canvas|5n b12]] `WBP_FurnitureCard→BP_FurnitureUserPrefsManager` thêm vào Gần đây · `AddRecentMesh(CardRowName)` — tìm: AddRecentMesh
- [[5o - Đổi vật liệu bằng cách bấm thẻ (1 hoặc nhiều món).canvas|5o b10]] `WBP_FurnitureInventory→WBP_FurnitureInventory` hẹn ghi sổ 0.5s, bấm liên tục chỉ ghi 1 lần · `SetTimer("CaptureMaterialSnapshot", 0.5)` — tìm: SetTimer
- [[5o - Đổi vật liệu bằng cách bấm thẻ (1 hoặc nhiều món).canvas|5o b11]] `WBP_FurnitureInventory→BP_FurnitureUserPrefsManager` thêm vào Gần đây · `AddRecentMaterial(PendingRowName)` — tìm: AddRecentMaterial
- [[5p - Đổi vật liệu bằng cách kéo thẻ thả lên đồ.canvas|5p b6]] `WBP_DragOverlay_FurnitureCard→BP_FurnitureSceneManager` báo lỗi nhẹ · `ToastRef.ShowToast("Chỉ áp vật liệu lên đồ nội thất")` — tìm: ShowToast
- [[5p - Đổi vật liệu bằng cách kéo thẻ thả lên đồ.canvas|5p b11]] `BP_FurnitureActor→BP_FurnitureUserPrefsManager` thêm vào Gần đây · `AddRecentMaterial(Apply_PendingRowName)` — tìm: AddRecentMaterial
- [[5q - Lưu combo (lưu mới · ghi đè).canvas|5q b6]] `WBP_FurnitureInventory→WBP_SaveComboDialog` tạo hộp thoại điền sẵn tên / thư mục / tag, gắn 3 nút · `Create WBP_SaveComboDialog → Bind OnDialogConfirmed, OnDialogConfirmedOverwrite, OnDialogCancelled` — tìm: OnDialogConfirmed, OnDialogConfirmedOverwrite, OnDialogCancelled
- [[5q - Lưu combo (lưu mới · ghi đè).canvas|5q b8]] `WBP_SaveComboDialog→WBP_FurnitureInventory` báo tin nút đã bấm · `Broadcast OnDialogConfirmed / OnDialogConfirmedOverwrite / OnDialogCancelled` — tìm: OnDialogConfirmed, OnDialogConfirmedOverwrite, OnDialogCancelled
- [[5q - Lưu combo (lưu mới · ghi đè).canvas|5q b13]] `BP_ComboManager→WBP_FurnitureInventory` chụp xong mới báo tin → tab Combo nạp lại · `Broadcast OnComboLibraryChanged` — tìm: OnComboLibraryChanged
- [[5t - Lưu cảnh và mở lại cảnh (EMS).canvas|5t b6]] `BP_FurnitureActor→BP_FurnitureActor` chờ EMS nạp xong biến SaveGame, MeshPath rỗng thì tự huỷ · `Event ActorLoaded → AsyncWaitForOperation(CT_Load)` — tìm: AsyncWaitForOperation
- [[5t - Lưu cảnh và mở lại cảnh (EMS).canvas|5t b8]] `BP_FurnitureActor→BP_FurnitureActor` nạp mesh (đồng bộ) · `LoadAsset_Blocking(MeshPath) → SetStaticMesh` — tìm: LoadAsset_Blocking

## Mục 5x chưa thuộc note luồng nào (0)
> Mỗi mục 5x phải được nhúng trong đúng 1 note `Brain/Luồng/Lxx` — không thì người đọc theo hành trình sẽ không gặp nó.

- (không có)

## Mục 5x thiếu dòng "Kiểm chứng K2:" hoặc "Nguồn:" (0)

- (không có)
