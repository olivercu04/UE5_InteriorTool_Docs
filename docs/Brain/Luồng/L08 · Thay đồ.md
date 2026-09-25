# L08 · Thay đồ

> **Hành trình:** ← [[L07 · Menu chuột phải và phím tắt|L07 Menu chuột phải và phím tắt]] · **L08** · [[L09 · Đổi vật liệu|L09 Đổi vật liệu]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là "Bất cứ lúc nào" · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** "Thay đồ" = bật **chế độ thay** (nhớ danh sách món cần thay + mở kho đúng thư mục của món) → bấm nút Thay trên thẻ khác → mỗi món cũ bị **thay bằng món mới cùng vị trí, xoay, mặt đặt, nhóm**. Chế độ thay vẫn bật để thử tiếp.

## Người dùng làm gì → thấy gì
| Làm | Thấy | Sổ lịch sử |
|---|---|---|
| Chọn đồ → chuột phải **Thay đồ** (hoặc nút Thay trên thanh công cụ / popup ℹ) | Kho mở đúng thư mục của món, mọi thẻ có nút Thay | — |
| Bấm **Thay** trên 1 thẻ | Món cũ đổi thành món mới tại chỗ, món mới được chọn | `Replace` |
| Bấm Thay trên thẻ khác | Thay tiếp (đang nhắm vào món vừa thay) | `Replace` |
| X đóng kho / click nền trống / Thay đồ lần nữa | Thoát chế độ thay, nút Thay biến mất | `Deselect` (nếu click nền) |

Món thuộc **combo** (không đang sửa bên trong) → tự chuyển sang **thay cả combo** ([[L11 · Combo|L11]], sơ đồ 5s).

## Chạy thế nào
![[Architecture_Map#5n — Thay đồ (Replace)]]
> 🗺️ Bản làn bơi: [[5n - Thay đồ (Replace).canvas|canvas 5n]]

## Hình dung
Giống **đổi mẫu tại showroom**: nhân viên ghi lại vị trí trưng bày (vị trí, hướng, kệ nào, thuộc bộ nào), cất mẫu cũ, đặt mẫu mới vào đúng chỗ đó. Danh sách "mẫu đang chờ đổi" (`MeshesToReplace`) được cập nhật thành các mẫu mới — để đổi tiếp.

## Dễ hiểu sai
- **Chế độ thay được đánh dấu bằng `ReplaceTarget` (None / Mesh / Combo)**, không còn `bIsReplaceMode` — thẻ đồ chỉ hiện nút Thay khi `== Mesh`, thẻ combo khi `== Combo`.
- **Mọi đường thoát phải xoá đủ 3 biến** `ReplaceTarget`, `MeshesToReplace`, `ComboRootGroupIDToReplace` (BTN_Close, click nền, Thay đồ lần 2).
- **Đọc `GroupID` TRƯỚC khi Destroy món cũ** (bug 12/06 — món mới rơi khỏi nhóm).
- **`CaptureSnapshot("Replace")` / `SelectActors` ở `Completed`** của vòng lặp, không trong thân (chạy N lần).
- `StartReplaceMode` có nhánh RowName rỗng (đồ cũ) → đọc `DAPath` legacy; RowName không còn trong DT → dead-end, kho không phản hồi (quan sát 1, chưa quyết sửa).
- Món mới nạp mesh blocking (nợ R1) và không qua `SpawnFurnitureCopy` → không tự có `PersistentID` mới ở bước này (`?` — rà khi làm U3).

## Đường ngược (6A)
Ctrl+Z → entry `Replace` (Snapshot) → món cũ quay lại. Thoát chế độ thay: X / click nền / Thay đồ lần 2.

## Còn mở
- Thân `F_ExecuteReplace` chưa K2 (doc v1.6) · 4 dòng thêm vào `EnterReplaceMode` 30/07 chưa re-export.

## Nhảy tới code
| Hàm | Doc |
|---|---|
| `CB_Replace` (✓K2 03/08) · `StartReplaceMode` (✓K2 24/07) · `IsReplaceModeActive` · `ShouldRouteReplaceToCombo` | [[BP_FurnitureInputManager]] |
| `EnterReplaceMode` · `ExitReplaceMode` · `FilterByFolderPathWithUI` · `BTN_Close` | [[WBP_FurnitureInventory]] |
| `F_ExecuteReplace` | [[WBP_DragOverlay_FurnitureCard]] |
| `BTN_ChangeMesh` · `Get_Button_ChangeMesh_Visibility` | [[WBP_FurnitureCard]] |
| `BTN_Replace` | [[WBP_MeshControls]] · popup: [[WBP_DetailPopup]] |
