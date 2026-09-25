# WBP_MaterialInspector
**Version:** 1.0 | **Ngày:** 17/09/2026 | **Tạo mới — S7G7T3.2, đóng PASS 7/7**

## Vai trò
Panel bên phải, chứa header (tên/breadcrumb đang chỉnh) + `WBP_MaterialParamPanel` (danh sách row
param) + footer (2 nút Reset). Không tự build danh sách param — chỉ forward qua `ParamPanelRef`.
Caller (`WBP_FurnitureInventory`, xem `RefreshParamPanel` — ĐANG XÂY, xem file đó) chịu trách nhiệm
build nội dung + toggle hiển thị qua `IsInspectorVisible()`.

⚠️ As-built xác nhận qua Hierarchy panel thật (screenshot 17/09/2026) — ghi ĐÚNG tên đã build,
KHÔNG đổi theo tên trong plan gốc nếu lệch (vd `TextBlock_Title` = "MATERIAL", KHÔNG phải "Chỉnh
sửa vật liệu" như plan gốc `Sprints/Sprint7/17-09-2026_S7G7_T3-T5_TaskCards_v6.md` ghi).

## Hierarchy
```
[WBP_MaterialInspector]
└── CanvasPanel_Root (Self Hit Test Invisible — verify PASS: click/xoay camera vùng ngoài
    │                  Border_InspectorRoot xuyên qua bình thường, không bị chặn)
    └── Border_InspectorRoot (Anchor phải, width ~360)
        └── VerticalBox_Root
            ├── Border_Header
            │   └── HB_Header
            │       ├── SizeBox_BTN_Close → BTN_Close → TextBlock_CloseIcon "×"
            │       ├── Spacer
            │       └── TextBlock_Title "MATERIAL" ← as-built (KHÁC plan gốc "Chỉnh sửa vật liệu")
            ├── Border_Context
            │   └── VerticalBox_Context
            │       ├── TextBlock_ContextLabel "ĐANG CHỈNH" ← label TĨNH, KHÔNG do Function nào set
            │       └── TextBlock_Breadcrumb "Sofa 01 · Sea.."
            ├── Separator_Context
            ├── ScrollBox_Content
            │   └── SizeBox_ContentPadding
            │       └── VerticalBox_Content
            │           └── ParamPanelRef : WBP_MaterialParamPanel
            ├── Separator_Footer
            └── Border_Footer
                └── HB_Footer
                    ├── BTN_ResetParams → Text "Đặt lại thông..."
                    ├── Spacer_FooterButtons
                    └── BTN_ResetSlot → Text "Đặt lại vật l..."
```

## Event Dispatchers
```
OnCloseRequested()
OnResetParamsRequested()
OnResetSlotRequested()
```

## Functions
```
SetHeader(Breadcrumb:Text)               → TextBlock_Breadcrumb.SetText(Breadcrumb)
ClearParamRows()                         → ParamPanelRef.ClearRows()
AddParamRow(Row:UserWidget)              → ParamPanelRef.AddRow(Row)
ShowParamEmptyState(bEmpty, Message)     → ParamPanelRef.ShowEmptyState(bEmpty, Message)
SetResetEnabled(bEnabled:Boolean)        → BTN_ResetParams.SetIsEnabled(bEnabled)
                                            BTN_ResetSlot.SetIsEnabled(bEnabled)
```
Toàn bộ là **pass-through** xuống `ParamPanelRef` (`Widgets/WBP_MaterialParamPanel.md`) — inspector
không tự giữ state param nào.

## Button bindings
```
BTN_Close.OnClicked        → Call OnCloseRequested()
BTN_ResetParams.OnClicked  → Call OnResetParamsRequested()
BTN_ResetSlot.OnClicked    → Call OnResetSlotRequested()
```

## Test — 7/7 PASS (17/09/2026)
1. `SetHeader` — breadcrumb hiện đúng text.
2. `AddParamRow`/`ClearParamRows` — thêm/xóa row đúng qua `ParamPanelRef`.
3. `ShowParamEmptyState` — 2 case (True/False) hiện đúng.
4. `SetResetEnabled` — 2 trạng thái (enable/disable) cả 2 nút đúng.
5. 3 dispatcher (`OnCloseRequested`/`OnResetParamsRequested`/`OnResetSlotRequested`) bắn đúng khi
   click nút tương ứng.
6. Footer đứng yên khi cuộn `ScrollBox_Content` (chỉ content cuộn, header/footer cố định).
7. `CanvasPanel_Root` (Self Hit Test Invisible) — click/xoay camera vùng ngoài
   `Border_InspectorRoot` xuyên qua bình thường, không bị chặn.

Q9: MIỄN (widget chưa nối `SelectedActors` — chỉ display/dispatcher, wiring thật ở
`WBP_FurnitureInventory.RefreshParamPanel`, xem file đó cho trạng thái Q9 của phần tích hợp).

---

## Lịch sử cập nhật

| Ngày | Version | Nội dung |
|------|---------|----------|
| 17/09/2026 | 1.0 | Tạo mới — S7G7T3.2. Hierarchy + 3 dispatcher + 5 function pass-through (nhúng `WBP_MaterialParamPanel` qua `ParamPanelRef`). Test 7/7 PASS. Nguồn: `GỬI CLAUDE CODE — Phân phối as-built S7G7T3` (17/09/2026), task card gốc `Sprints/Sprint7/17-09-2026_S7G7_T3-T5_TaskCards_v6.md`. |

---

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Thuộc mảng kết nối:** [[Kết nối 3e - Vật liệu Material]]

**Gọi / điều khiển →**
- [[WBP_MaterialParamPanel]] — forward 5 hàm xuống panel con · SetHeader/ClearParamRows/AddParamRow/ShowParamEmptyState/SetResetEnabled → ParamPanelRef

**← Được gọi bởi**
- [[WBP_FurnitureInventory]] — build/xóa danh sách row + empty-state · ClearParamRows()/AddParamRow()/ShowParamEmptyState(), SetVisibility ✓K2

<!-- BRAIN:END -->
