# WBP_FolderPickerRow
**Phiên bản:** 1.0 | **Tạo:** 11/07/2026 11:17 — C5.8 Task Card #2 (2a + 2b Part A)

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

### `SetNode(Node : S_FolderTreeNode)` (2a, SỬA ở 2b)
⚠️ SUY LUẬN phần đầu 2a (guide glyphs) — đoạn cuối as-built đã confirm trong chat:
```
▶ SET RowNode = Node                                  ← ⚠️ SUY LUẬN vị trí, confirm khi export
▶ (dựng guide string từ Node.ContinuesAncestors[] + Node.bIsLast → SetText TXT_Guide)  ⚠️ SUY LUẬN chi tiết
▶ Set Text(TXT_Name, To Text(Node.DisplayLabel))
▶ Set Visibility(TXT_Badge, Collapsed)                ← TRƯỚC Branch (cả 2 nhánh đều cần)
▶ Branch(Node.HasChildren)
   True  → Set Visibility(TXT_Arrow, Visible)
   False → Set Visibility(TXT_Arrow, Hidden)
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

### Button handlers (2b Part A — **ĐÍNH CHÍNH quan trọng**)
As-built dùng **Custom Event trung gian** (sinh từ Details panel "+"), KHÁC ghi chú TIẾN ĐỘ cũ trong `C5.8_TaskCard2_PartB_2c_10jul2026.md` ("nối THẲNG vào Call dispatcher") — xem `DEVIATIONS.md` [DOC-FIX] 11/07/2026:
```
BTN_Arrow.OnClicked → HandleArrowClicked (Custom Event)
   ▶ Broadcast OnRowExpandClicked(RowNode.Path)
BTN_Name.OnClicked  → HandleNameClicked (Custom Event)
   ▶ Broadcast OnRowSelected(RowNode.Path)
```

## Còn nợ (Task Card sau)
`SetSearchHighlight(bMatch)` (Part 2c — chưa build) · `EnterRenameMode`/host `WBP_EditableLabel` (2d).

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 11/07/2026 11:17 | Khởi tạo — C5.8 Task Card #2: 2a (row tĩnh + guide line, PASS full data thật) + 2b Part A (hierarchy BTN_Arrow/BTN_Name, dispatchers OnRowExpandClicked/OnRowSelected, SetExpanded, Custom Event trung gian HandleArrowClicked/HandleNameClicked). |
