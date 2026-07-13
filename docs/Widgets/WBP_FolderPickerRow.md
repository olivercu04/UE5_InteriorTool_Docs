# WBP_FolderPickerRow
**Phiên bản:** 1.3 | **Tạo:** 11/07/2026 11:17 — C5.8 Task Card #2 (2a + 2b Part A) | **Sửa:** 13/07/2026 — 2d (rename host, `EditableLabel_Name`) + Card 1 (`SetCurrentTag`/`SetSelectedHighlight`), delta C5.8 13/07/2026

---

## Tổng quan
Row của picker cây folder (Lớp 3 UI theo plan C5.8 §4), thay `WBP_MoveFolderRow`. KHÔNG đục `WBP_TreeNode` (fork Y đã chốt).

## Layout
```
HB_Row
├── TXT_Guide         (TextBlock — guide glyphs │├└ dạng concatenated string, KHÔNG Image cột)
├── BTN_Arrow         (Button, bọc TXT_Arrow ▶/▼)
└── BTN_Name          (Button, bọc HB_Label [ EditableLabel_Name + TXT_Badge + TXT_CurrentTag ])
```
- Guide line render bằng **chuỗi ký tự Unicode nối sẵn** (deviation so plan gốc §4 "Image cột dọc/elbow" — lý do: `Create Widget` không instantiate native TextBlock dynamic; đã PASS 45+ folder). Ceiling: đủ tốt scale hiện tại; trigger: khi cần style guide line đậm/màu → chuyển Image.
- `TXT_Arrow` dùng Visibility **Hidden** (không Collapsed) khi `!HasChildren` — giữ căn lề.
- **13/07 (2d):** `TXT_Name` (TextBlock) → thay bằng `EditableLabel_Name` (`WBP_EditableLabel`, Is Variable=✓), vị trí giữ nguyên trong `HB_Label`, trước `TXT_Badge`.
- **13/07 (Card 1):** thêm `TXT_CurrentTag` (TextBlock, text="hiện tại", Collapsed mặc định) vào `HB_Label`, SAU `TXT_Badge`.

## Variables
| Tên | Kiểu | Ghi chú |
|---|---|---|
| `RowNode` | `S_FolderTreeNode` | SET trong `SetNode`, mọi Broadcast đọc từ đây |
| `Color Match` | Linear Color | Giai đoạn 2 (12/07) — (R=1.0, G=0.85, B=0.4, A=1.0), vàng nhạt, dùng trong `SetSearchHighlight` |
| `Color Default` | Linear Color | Giai đoạn 2 (12/07) — (R=1.0, G=1.0, B=1.0, A=1.0), trắng (màu gốc), dùng trong `SetSearchHighlight` |

## Event Dispatchers
```
OnRowExpandClicked(Path : String)
OnRowSelected(Path : String)
OnRowRenameCommitted(Path : String, NewName : String)   ← MỚI, 13/07 (2d, 1f)
```

## Functions

### `SetNode(Node : S_FolderTreeNode)` (2a, SỬA ở 2b, BUG FIX Giai đoạn 1 11/07)
⚠️ SUY LUẬN phần guide glyphs (chưa export) — phần còn lại đã confirm qua export K2Node 11/07:
```
▶ SET RowNode = Node                                  ← BUG FIX 11/07: dòng này ĐÃ THIẾU hoàn toàn ở bản build đầu — root cause bug #2 (RowNode/Path luôn rỗng)
▶ (dựng guide string từ Node.ContinuesAncestors[] + Node.bIsLast → SetText TXT_Guide)  ⚠️ SUY LUẬN chi tiết
▶ EditableLabel_Name.SetLabel(Node.DisplayLabel)      ← 13/07 (2d, 1b): thay Set Text(TXT_Name,...) sau khi đổi TXT_Name→EditableLabel_Name
▶ Set Visibility(TXT_Badge, Collapsed)                ← TRƯỚC Branch (cả 2 nhánh đều cần)
▶ Branch(Node.HasChildren)
   True  → Set Visibility(TXT_Arrow, Visible)
            Set Visibility(BTN_Arrow, Visible)         ← BUG FIX 11/07: thiếu ở bản đầu — nút bọc ngoài không đồng bộ Visibility với TXT_Arrow bên trong
   False → Set Visibility(TXT_Arrow, Hidden)
            Set Visibility(BTN_Arrow, Hidden)           ← BUG FIX 11/07 (Hidden, không Collapsed — giữ layout)
```

### `SetExpanded(bExpanded : Boolean)` (2b Part A, verify export XML)
```
▶ Set Text(TXT_Arrow, To Text( Select String(A="▼", B="▶", bPickA=bExpanded) ))
▶ Set Visibility(TXT_Badge, Collapsed)
▶ Branch( RowNode.HasChildren AND NOT bExpanded )
   True  → Set Visibility(TXT_Badge, Visible)
           Set Text(TXT_Badge, To Text( Concat("(", Concat(Conv_IntToString(RowNode.ChildCount), ")")) ))
   False → [dead-end hợp lệ]
```

### `SetSearchHighlight(bMatch : Boolean)` (Giai đoạn 2, DONE 12/07; sửa 13/07 sau khi đổi host sang EditableLabel_Name)
```
FunctionEntry(Match)
  ▶ Branch(Match)
       True  → EditableLabel_Name.SetLabelColor(GET Color Match)
       False → EditableLabel_Name.SetLabelColor(GET Color Default)
```
**13/07 (2d, P2 — chốt cách B, relay function, không đục thẳng widget con):** đổi từ gọi thẳng `f Set Color and Opacity(Target=TXT_Name,...)` sang gọi `EditableLabel_Name.SetLabelColor(...)` — xem `SetLabelColor` mới trên `WBP_EditableLabel.md` v1.1.

### Button handlers (2b Part A — **ĐÍNH CHÍNH lần 2, 11/07 13:14**)
As-built THẬT, xác nhận qua export K2Node 11/07: nối **THẲNG**, KHÔNG có Custom Event trung gian:
```
On Clicked (BTN_Arrow) ▶→ Call On Row Expand Clicked(Target=self, Path=Break(RowNode).Path)
On Clicked (BTN_Name)  ▶→ Call On Row Selected(Target=self, Path=Break(RowNode).Path)
```
`Path` lấy qua `Break S_FolderTreeNode(RowNode)` — không hardcode, không qua param `Node`.

⚠️ Bản v1.0 file này từng ghi "Custom Event trung gian HandleArrowClicked/HandleNameClicked" — **SAI**, đã đính chính ngược lại lần nữa theo export K2Node thật. Xem `DEVIATIONS.md` [DOC-FIX] 11/07/2026 (mục Giai đoạn 1).

### `EnterRenameMode(Siblings : Array<String>)` — Custom Event (relay, MỚI 13/07, 2d 1c)
```
▶ EditableLabel_Name.EnterEditMode(Siblings)
```

### Event Construct (MỚI 13/07, 2d 1d)
```
Bind EditableLabel_Name.OnLabelRenameCommitted → HandleLabelCommitted
```

### `HandleLabelCommitted(NewName : String)` — Custom Event (bound, MỚI 13/07, 2d 1e)
```
▶ Broadcast OnRowRenameCommitted(RowNode.Path, NewName)
```

### `GetRowPath() → String` (Pure, MỚI 13/07, 2d P3)
```
▶ Return = GET RowNode → Break → Path
```
Xác nhận qua export K2Node (screenshot cuhoang) — khớp spec, exec pin Entry→Return bình thường dù Pure (chỉ ẩn ở node GỌI từ ngoài).

### `SetCurrentTag(bVisible : Boolean)` — Custom Event (MỚI 13/07, Card 1)
```
Branch(bVisible) True→ Set Visibility(TXT_CurrentTag, Visible)
                 False→ Set Visibility(TXT_CurrentTag, Collapsed)
```

### `SetSelectedHighlight(bSelected : Boolean)` — Custom Event (MỚI 13/07, Card 1)
```
Branch(bSelected) True→ Set Background Color(BTN_Name, R=0.2 G=0.4 B=1.0 A=0.4)
                  False→ Set Background Color(BTN_Name, R=1 G=1 B=1 A=1)
```

## Test PASS (Task Card 2d Phần 1, 13/07 — xác nhận trực tiếp qua thao tác row + qua Move dialog thật)
```
1. EnterRenameMode → text bôi đen, EditBox nhận focus         ✅
2. Gõ tên hợp lệ + Enter → OnRowRenameCommitted fire đúng      ✅
3-4. Validate tên trùng/ký tự "/" (relay từ WBP_EditableLabel) — kế thừa, không test riêng
5. Click ra ngoài → revert, không fire commit (6A)             ✅ (kế thừa từ WBP_EditableLabel)
6. Tên tiếng Việt có dấu → commit đúng                          ✅
0.2 Hồi quy search: SetLabelColor (Slate Color) không vỡ highlight vàng  ✅
0.3 Hồi quy hiển thị: expand/collapse không vỡ tên/badge/arrow  ✅ (test trong Move/Save dialog, xác nhận 13/07)
```

## Còn nợ
(Không còn — `EnterRenameMode`/host `WBP_EditableLabel` DONE 13/07, xem trên.)

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 11/07/2026 11:17 | Khởi tạo — C5.8 Task Card #2: 2a (row tĩnh + guide line, PASS full data thật) + 2b Part A (hierarchy BTN_Arrow/BTN_Name, dispatchers OnRowExpandClicked/OnRowSelected, SetExpanded, Custom Event trung gian HandleArrowClicked/HandleNameClicked). |
| 1.1 | 11/07/2026 13:14 | Giai đoạn 1 bug fix: `SetNode` thêm `SET RowNode = Node` (thiếu hoàn toàn ở bản đầu — root cause bug #2) + thêm `SetVisibility(BTN_Arrow,...)` song song `TXT_Arrow` ở cả 2 nhánh Branch. Đính chính lần 2 "Button handlers": as-built THẬT là nối THẲNG `OnClicked → Call dispatcher` (không Custom Event trung gian) — xác nhận qua export K2Node 11/07. |
| 1.2 | 12/07/2026 10:40 | `SetSearchHighlight(bMatch)` DONE (Giai đoạn 2) — 2 class var mới `Color Match`/`Color Default` + hàm dùng `f Set Color and Opacity` set màu `TXT_Name`. Xóa khỏi "Còn nợ". |
| 1.3 | 13/07/2026 | **2d Phần 1 (rename host) + Card 1** — `TXT_Name`→`EditableLabel_Name` (`WBP_EditableLabel`); `SetNode`/`SetSearchHighlight` relay qua `EditableLabel_Name.SetLabel`/`SetLabelColor` (không đục thẳng widget con). Thêm `EnterRenameMode` (relay), `Event Construct` bind `OnLabelRenameCommitted`→`HandleLabelCommitted`, `HandleLabelCommitted` broadcast `OnRowRenameCommitted`, dispatcher `OnRowRenameCommitted` mới, getter `GetRowPath()` (Pure). Card 1: thêm `TXT_CurrentTag` + 2 Custom Event `SetCurrentTag`/`SetSelectedHighlight`. Test PASS Task Card 2d Phần 1 (1,2,5,6,0.2,0.3). Xóa "Còn nợ". |
