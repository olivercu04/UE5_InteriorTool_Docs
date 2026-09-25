# WBP_MaterialParamPanel
**Version:** 1.0 | **Ngày:** 17/09/2026 | **Tạo mới — S7G7T3.1, đóng PASS**

> Xác nhận cuhoang (17/09/2026): panel này **chưa từng build trước phiên này** — chữ "CẬP NHẬT"
> trong delta nguồn chỉ nói tới chữ ký `ShowEmptyState`, không ngụ ý có base cũ khác. Nội dung dưới
> đây là TOÀN BỘ những gì đã build cho panel tới thời điểm này.

## Vai trò
Panel con nhúng trong `WBP_MaterialInspector` (`ParamPanelRef`) — chứa danh sách row param
(`WBP_ParamScalarRow`/`WBP_ParamColorRow`, xem `Widgets/WBP_ParamScalarRow.md`,
`Widgets/WBP_ParamColorRow.md`) và empty-state khi MI ngoài từ điển. Panel KHÔNG tự build row từ
`GetControlsForMaterial` — chỉ expose `ClearRows`/`AddRow`/`ShowEmptyState` cho caller
(`WBP_FurnitureInventory.RefreshParamPanel` — xem `Widgets/WBP_FurnitureInventory.md` mục "S7G7T3",
**ĐANG XÂY**) gọi vào.

## Hierarchy con đã biết
```
VB_ParamRows   ← self-owned, bound Designer của chính panel (KHÔNG cần IsValid, xem L1 refine)
TextBlock_Empty
```
Hierarchy đầy đủ (container ngoài, layout) — chưa có chi tiết trong delta, chỉ 2 widget con trên
được xác nhận qua các function dưới.

## Function `ShowEmptyState(bEmpty : Boolean, Message : Text)`
```
True  → TextBlock_Empty.SetText(Message)
        → Collapsed VB_ParamRows
        → Visible TextBlock_Empty
False → (ngược lại — hiện VB_ParamRows, ẩn TextBlock_Empty)
```
Test PASS 2/2 (2 message khác nhau hiện đúng, false→ẩn đúng).

## Function `ClearRows()`
```
ClearRows()
▶→ ClearChildren(VB_ParamRows)
```
KHÔNG IsValid — `VB_ParamRows` self-owned, bound Designer của chính panel (xem `L1` refine trong
`Rules/AI_Implementation_Rules.md`).

## Function `AddRow(Row : UserWidget)`
```
AddRow(Row)
▶→ Branch(IsValid(Row))
     True  ▶→ AddChild(VB_ParamRows, Row)
     False → dead-end an toàn
```
CÓ IsValid — `Row` là tham số truyền từ ngoài (caller có thể truyền None).

Test PASS 3/3 (`ClearRows`+`AddRow`): add row hợp lệ, add None không lỗi, clear sạch.

Q9: MIỄN — cả 3 function trên standalone, không tự đụng `SelectedActors` (wiring thật với slot đang
chọn nằm ở `WBP_FurnitureInventory.RefreshParamPanel`, xem Q9 của phần đó khi T3.3 xong).

---

## Lịch sử cập nhật

| Ngày | Version | Nội dung |
|------|---------|----------|
| 17/09/2026 | 1.0 | Tạo mới — S7G7T3.1. `ShowEmptyState(bEmpty, Message)`, `ClearRows()`, `AddRow(Row)`. Test PASS (2/2 + 3/3). Nguồn: `GỬI CLAUDE CODE — Phân phối as-built S7G7T3` (17/09/2026), xác nhận cuhoang panel chưa từng build trước đó. |

---

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Thuộc mảng kết nối:** [[Kết nối 3e - Vật liệu Material]]

**← Được gọi bởi**
- [[WBP_MaterialInspector]] — forward 5 hàm xuống panel con · SetHeader/ClearParamRows/AddParamRow/ShowParamEmptyState/SetResetEnabled → ParamPanelRef

<!-- BRAIN:END -->
