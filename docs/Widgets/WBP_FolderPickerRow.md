# WBP_FolderPickerRow
**Phiên bản:** 1.1 | **Tạo:** 11/07/2026 11:17 — C5.8 Task Card #2 (2a + 2b Part A) | **Sửa:** 11/07/2026 13:14 — Giai đoạn 1 bug fix (xem `C5.8_TaskCard2_Delta_GiaiDoan1_11jul2026.md`)

---

## Tổng quan
Row của picker cây folder (Lớp 3 UI theo plan C5.8 §4), thay `WBP_MoveFolderRow`. KHÔNG đục `WBP_TreeNode` (fork Y đã chốt).

## Layout
```
HB_Row
├── TXT_Guide   (TextBlock — guide glyphs │├└ dạng concatenated string, KHÔNG Image cột)
├── BTN_Arrow   (Button, bọc TXT_Arrow ▶/▼)
└── BTN_Name    (Button, bọc HB_Label [ TXT_Name + TXT_Badge ])
```
- Guide line render bằng **chuỗi ký tự Unicode nối sẵn** (deviation so plan gốc §4 "Image cột dọc/elbow" — lý do: `Create Widget` không instantiate native TextBlock dynamic; đã PASS 45+ folder). Ceiling: đủ tốt scale hiện tại; trigger: khi cần style guide line đậm/màu → chuyển Image.
- `TXT_Arrow` dùng Visibility **Hidden** (không Collapsed) khi `!HasChildren` — giữ căn lề.

## Variables
| Tên | Kiểu | Ghi chú |
|---|---|---|
| `RowNode` | `S_FolderTreeNode` | SET trong `SetNode`, mọi Broadcast đọc từ đây |

## Event Dispatchers
```
OnRowExpandClicked(Path : String)
OnRowSelected(Path : String)
```

## Functions

### `SetNode(Node : S_FolderTreeNode)` (2a, SỬA ở 2b, BUG FIX Giai đoạn 1 11/07)
⚠️ SUY LUẬN phần guide glyphs (chưa export) — phần còn lại đã confirm qua export K2Node 11/07:
```
▶ SET RowNode = Node                                  ← BUG FIX 11/07: dòng này ĐÃ THIẾU hoàn toàn ở bản build đầu — root cause bug #2 (RowNode/Path luôn rỗng)
▶ (dựng guide string từ Node.ContinuesAncestors[] + Node.bIsLast → SetText TXT_Guide)  ⚠️ SUY LUẬN chi tiết
▶ Set Text(TXT_Name, To Text(Node.DisplayLabel))
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

### Button handlers (2b Part A — **ĐÍNH CHÍNH lần 2, 11/07 13:14**)
As-built THẬT, xác nhận qua export K2Node 11/07: nối **THẲNG**, KHÔNG có Custom Event trung gian:
```
On Clicked (BTN_Arrow) ▶→ Call On Row Expand Clicked(Target=self, Path=Break(RowNode).Path)
On Clicked (BTN_Name)  ▶→ Call On Row Selected(Target=self, Path=Break(RowNode).Path)
```
`Path` lấy qua `Break S_FolderTreeNode(RowNode)` — không hardcode, không qua param `Node`.

⚠️ Bản v1.0 file này từng ghi "Custom Event trung gian HandleArrowClicked/HandleNameClicked" — **SAI**, đã đính chính ngược lại lần nữa theo export K2Node thật. Xem `DEVIATIONS.md` [DOC-FIX] 11/07/2026 (mục Giai đoạn 1).

## Còn nợ (Task Card sau)
`SetSearchHighlight(bMatch)` (Part 2c — chưa build) · `EnterRenameMode`/host `WBP_EditableLabel` (2d).

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 11/07/2026 11:17 | Khởi tạo — C5.8 Task Card #2: 2a (row tĩnh + guide line, PASS full data thật) + 2b Part A (hierarchy BTN_Arrow/BTN_Name, dispatchers OnRowExpandClicked/OnRowSelected, SetExpanded, Custom Event trung gian HandleArrowClicked/HandleNameClicked). |
| 1.1 | 11/07/2026 13:14 | Giai đoạn 1 bug fix: `SetNode` thêm `SET RowNode = Node` (thiếu hoàn toàn ở bản đầu — root cause bug #2) + thêm `SetVisibility(BTN_Arrow,...)` song song `TXT_Arrow` ở cả 2 nhánh Branch. Đính chính lần 2 "Button handlers": as-built THẬT là nối THẲNG `OnClicked → Call dispatcher` (không Custom Event trung gian) — xác nhận qua export K2Node 11/07. |
