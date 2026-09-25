# L12 · Lưu và mở cảnh

> **Hành trình:** ← [[L11 · Combo|L11 Combo]] · **L12** · [[L13 · Hoàn tác và làm lại|L13 Hoàn tác và làm lại]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là bước ⑦ · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** lưu / mở cảnh dùng plugin **Easy Multi Save (EMS)**: EMS ghi mọi actor có biến đánh dấu SaveGame. Mở cảnh = SceneManager **xoá hết đồ hiện có**, EMS nạp lại, rồi **mỗi món tự dựng lại** mesh + vật liệu trong `Event ActorLoaded`.

## Người dùng làm gì → thấy gì
| Làm | Thấy |
|---|---|
| Lưu cảnh (Ctrl+S theo danh sách phím tắt — `?`) | Không có phản hồi riêng trong tool |
| Bấm **Load** trong menu Save/Load của project | Phòng trống trong chốc lát rồi đồ hiện lại, vật liệu về sau vài frame |

Lưu cảnh **không ghi sổ lịch sử** (không đổi cảnh).

## Chạy thế nào
![[Architecture_Map#5t — Lưu cảnh và mở lại cảnh (EMS)]]
> 🗺️ Bản làn bơi: [[5t - Lưu cảnh và mở lại cảnh (EMS).canvas|canvas 5t]]

## Hình dung
EMS giống **chụp danh sách kiểm kê**: chỉ ghi các cột được đánh dấu SaveGame của từng món (MeshPath, RowName, mặt đặt, nhóm, ID, phiếu vật liệu) — không chụp hình. Mở lại = đọc danh sách, dựng từng món theo cột.

## Dễ hiểu sai
- **`DeselectMesh` phải chạy TRƯỚC khi xoá đồ** — tắt gizmo trước, không thì gizmo trỏ vào actor đã chết.
- **SceneManager bind lại nút Load mỗi Tick** khi menu Save/Load mới xuất hiện (menu thuộc project tổng, tạo lại mỗi lần mở).
- **Danh tính sinh trong `ActorLoaded`, không trong BeginPlay** — BeginPlay chạy trước khi EMS nạp xong field → sinh ID mới đè ID cũ đã lưu (ID-08).
- **Không SET Tags trực tiếp** — EMS dùng Tags để theo dõi; luôn GET → ADD → SET.
- `MeshPath` rỗng khi nạp → món tự huỷ. Nhóm được lưu qua `BP_GroupsContainer` (Groups, GroupNameCounter).

## Đường ngược (6A)
Mở lại bản lưu trước. Undo sau khi Load: chưa rõ sổ lịch sử được xoá hay giữ (`?`).

## Còn mở
- Phím / nút nào gọi `SaveFurnitureScene` / `LoadFurnitureScene` — doc không ghi.
- Sổ Undo sau khi Load — doc không ghi.
- `Event ActorLoaded` bản hiện hành (chèn `EnsurePersistentId` 21/09) chưa K2.

## Nhảy tới code
| Hàm | Doc |
|---|---|
| `SaveFurnitureScene` · `LoadFurnitureScene` · `OnLoadButtonClicked` · Event Tick | [[BP_FurnitureSceneManager]] |
| `Event ActorLoaded` · `RestoreMyMaterialSlots` · `Rst_LoadNextSlot` · Event BeginPlay | [[BP_FurnitureActor]] |
| `EnsurePersistentId` | [[EntityIdLibrary_Reference]] |
| Menu Save/Load của project | [[SaveGameMenu]] *(chưa có doc)* |
