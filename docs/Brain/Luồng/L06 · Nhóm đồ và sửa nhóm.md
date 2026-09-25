# L06 · Nhóm đồ và sửa nhóm

> **Hành trình:** ← [[L05 · Di chuyển và xoay đồ|L05 Di chuyển và xoay đồ]] · **L06** · [[L07 · Menu chuột phải và phím tắt|L07 Menu chuột phải và phím tắt]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là bước ④ · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** nhóm = **gắn cùng 1 `GroupID` lên từng món** (không có actor "nhóm"); nhóm lồng nhau bằng `ParentGroupID`. "Vào nhóm" (edit mode) là **chế độ chọn** — cho click trúng từng thành viên thay vì cả nhóm.

## Người dùng làm gì → thấy gì
| Làm | Thấy | Sổ lịch sử |
|---|---|---|
| Chọn ≥2 món / nhóm → **Ctrl+G** | Info bar hiện "Nhóm N", click 1 món là chọn cả nhóm | `CreateGroup` |
| Bấm **Vào nhóm** | Thanh sửa nhóm (breadcrumb "Nhóm 1 › Nhóm 2"), click chọn từng món bên trong | — |
| Trong nhóm: kéo đồ mới vào / dán | Đồ mới tự thuộc nhóm đang sửa | `Spawn` / `PasteMulti` |
| **Lên 1 cấp** / **Thoát** | Ra ngoài, cả cây vừa sửa được chọn | — |
| **Ctrl+Shift+G** | Bóc đúng 1 lớp nhóm ngoài cùng | `Ungroup` |

## Chạy thế nào
![[Architecture_Map#5l — Nhóm đồ và vào / ra sửa nhóm]]
> 🗺️ Bản làn bơi: [[5l - Nhóm đồ và vào - ra sửa nhóm.canvas|canvas 5l]]

## Hình dung
Giống **nhãn dán trên hàng hoá** trong kho: nhóm không phải cái thùng chứa đồ, mà là cùng 1 nhãn dán lên từng món (`GroupID`). Nhóm lớn chứa nhóm nhỏ = nhãn nhỏ ghi "thuộc nhãn lớn nào" (`ParentGroupID`). Danh sách nhãn (tên, cha) nằm ở `Groups` và được chép sang `BP_GroupsContainer` để lưu cùng cảnh.
```
Groups:  g_A (Nhóm 1, cha "")   g_B (Nhóm 2, cha g_A)
Món:     Ghế1.GroupID = g_B   Ghế2.GroupID = g_B   Bàn.GroupID = g_A
Click Ghế1 (không sửa nhóm)  → leo tới gốc g_A → chọn Ghế1, Ghế2, Bàn
Vào g_A, click Ghế1          → con trực tiếp của g_A là g_B → chọn Ghế1, Ghế2
```

## Dễ hiểu sai
- **Ctrl+G gom theo đơn vị chọn, không theo từng món** (`ComputeSelectionUnits`) — chọn 2 nhóm con rồi Ctrl+G ra nhóm cha chứa 2 nhóm con, không làm phẳng (luật 6B, bug 14/06).
- **Vào / ra nhóm không ghi sổ** — `EditModeStack` đi kèm mọi snapshot khác; Undo có thể đưa bạn về đúng cấp đang sửa.
- **Giới hạn 3 cấp** khi vào nhóm (`TryEnterEditFromSelection`).
- **Tên "Nhóm N" đếm bằng `GroupNameCounter` trong `BP_GroupsContainer`** (lưu theo cảnh), không phải `Groups.Length + 1`.
- **Combo cũng là nhóm** (nhóm gốc có `SourceComboID`) — nên thay đồ / lưu combo phải hỏi "món này có nằm trong combo không" ([[L11 · Combo|L11]]).

## Đường ngược (6A)
Ctrl+Shift+G bóc 1 lớp · Lên 1 cấp / Thoát · Ctrl+Z (`CreateGroup`, `Ungroup`).

## Còn mở
- ~~Blueprint nào bắt Ctrl+G / Ctrl+Shift+G~~ → đã rõ 25/09: `IA_GroupCreate` và `IA_Ungroup` trong InputManager (thân event chưa K2).
- Toàn luồng theo doc (CreateGroup v1.9, UngroupActors v1.8) — chưa K2.

## Nhảy tới code
| Hàm | Doc |
|---|---|
| `CreateGroup` · `UngroupActors` · `ComputeSelectionUnits` · `SyncGroupsToContainer` · `PruneEmptyGroups` | [[BP_FurnitureInputManager]] |
| `EnterEditMode` · `ExitEditModeOneLevel` · `ExitEditModeFull` · `TryEnterEditFromSelection` · `ResolveSelectionUnit` · `GetCurrentEditScope` | [[BP_FurnitureInputManager]] |
| `BTN_EnterEdit` · `OnEditModeChangedInfoBar` · Hành vi các nút Exit | [[WBP_MeshControls]] |
| Caller Ctrl+Shift+G · node flow nhóm cũ | [[Blueprint_Logic_NodeFlow]] |
