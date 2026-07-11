# WBP_FolderTreePicker
**Phiên bản:** 1.0 — 🔄 IN PROGRESS | **Tạo:** 11/07/2026 11:17 — C5.8 Task Card #2 Part B lần 1 | **Sửa:** 11/07/2026 13:14 — Giai đoạn 1 DONE (xem `C5.8_TaskCard2_Delta_GiaiDoan1_11jul2026.md`)

---

## Tổng quan
Lớp 2 SHARED component (plan C5.8 §4), nhúng vào 2 vỏ Move/Save (chưa wire — §7.3/7.4 sau).

## Layout
```
VB_Picker
├── HB_Toolbar
│   ├── BTN_ExpandAll   → TextBlock "Mở tất cả"
│   └── BTN_CollapseAll → TextBlock "Thu gọn"
├── SB_SearchFolder     ← Search Bar, FULL-WIDTH hàng riêng (đúng §4 plan gốc)
└── SB_Rows             (ScrollBox chứa WBP_FolderPickerRow)
```

## Variables
| Tên | Kiểu | Default | Ghi chú |
|---|---|---|---|
| `Folders` | Array\<S_FolderTreeNode\> | rỗng | push từ ngoài qua `SetFolders` (F3a — picker KHÔNG tự đọc storage) |
| `ExpandedFolders` | **Array\<String\>** | rỗng | deviation `[ARCH]` — Array thay Set (plan gốc ghi Set) |
| `SelectedPath` | String | "" | chưa dùng highlight |
| `bIsSearching` | Boolean | false | |
| `SearchExpandOverride` | Array\<String\> | rỗng | tập force-expand lúc search, KHÔNG đụng ExpandedFolders |

## Event Dispatcher
```
OnFolderSelected(Path : String)
```

## Functions

### `IsPathVisible(Path : String) → Boolean` (DONE, trace tay export XML khớp 100%)
Node hiện ⇔ mọi tổ tiên ∈ `ExpandedFolders`. Top-level / "(Gốc)" luôn True.
⚠️ Chi tiết loop as-built (ForEachLoopWithBreak hay For Loop With Break) — lấy theo K2Node export khi cuhoang gửi; kết quả Print test đã PASS (top-level=True, tổ tiên chưa expand=False, nested-chain sâu đúng).

### `RefreshVisibleRows()` (DONE — SINGLE SOURCE expand-mode + search-mode)
⚠️ SUY LUẬN theo §4d task card (nhánh search hiện để `bIsSearching=False` mặc định, chưa ghép search):
```
▶ SET QueryStr = Get Text(SB_SearchFolder) → ToString
▶ Clear Children(SB_Rows)
▶ ForEachLoop(Folders):
     Branch(bIsSearching)
        True  → bShow = Array_Contains(SearchExpandOverride, node.Path) OR PathMatchesQuery(...)
        False → bShow = IsPathVisible(node.Path)
     Branch(bShow) True →
        Create Widget(WBP_FolderPickerRow) → Row
        Row.SetNode(node)
        Branch(bIsSearching): True → SetExpanded(True)+SetSearchHighlight(match)
                              False → SetExpanded(Array_Contains(ExpandedFolders,node.Path))+SetSearchHighlight(False)*
        Bind Row.OnRowExpandClicked → HandleRowExpandClicked
        Bind Row.OnRowSelected → HandleRowSelected
        Add Child(SB_Rows, Row)
   Completed → hết hàm
```
(*) `SetSearchHighlight` chưa tồn tại ở lần build 1 — nhánh này chưa có node đó.

### `SetFolders(Nodes)` — SỬA (bug đã fix, ghi lesson)
Thân 2a cũ (tự loop tạo row) → thay bằng:
```
▶ SET Folders = Nodes
▶ RefreshVisibleRows()
```
**Bug lesson:** Sonnet quên nhắc sửa theo bước 4e task card → breakpoint không fire. Phát hiện + fix bởi cuhoang, verify Print `IsPathVisible` PASS.

## Custom Events (DONE, ⚠️ SUY LUẬN theo §5 task card)
```
HandleRowExpandClicked(Path): Branch(Array_Contains(ExpandedFolders,Path))
   True→Remove Item · False→Add Unique · [merge] → RefreshVisibleRows()
HandleRowSelected(Path): SET SelectedPath=Path → Broadcast OnFolderSelected(Path)
```

## Events — BTN_ExpandAll / BTN_CollapseAll (DONE, Giai đoạn 1, 11/07)
Nối thẳng từ `OnClicked`, cùng pattern với `WBP_FolderPickerRow` (không qua Custom Event trung gian):
```
On Clicked (BTN_ExpandAll)
   ▶ CLEAR ExpandedFolders
   ▶ ForEachLoop(Folders):
        Branch(node.HasChildren) True → Array_AddUnique(ExpandedFolders, node.Path)
      Completed → RefreshVisibleRows()

On Clicked (BTN_CollapseAll)
   ▶ CLEAR ExpandedFolders
   ▶ RefreshVisibleRows()
```

## Chưa build (Part 2c còn lại)
`PathMatchesQuery` · `BuildSearchOverride` · nhánh search trong Refresh · `SB_SearchFolder.OnSearchTextChanged`.

## Test status
Mục 1-5 PASS (Giai đoạn 1 task card HOÀN TẤT — expand/collapse đơn lẻ + Mở tất cả/Thu gọn + nhớ state con cháu sau collapse/expand lại, xác nhận 6A).
Mục 6-10 chưa chạy (Giai đoạn 2 — search — chưa làm).

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 0.9 | 11/07/2026 11:17 | Khởi tạo (IN PROGRESS) — C5.8 Task Card #2 Part B lần 1: Layout (HB_Toolbar + SB_SearchFolder) + Variables (Folders/ExpandedFolders/SelectedPath/bIsSearching/SearchExpandOverride) + `IsPathVisible` DONE + `RefreshVisibleRows` DONE (nhánh search ⚠️ SUY LUẬN, chưa ghép) + `SetFolders` bug fix + 2 Custom Event handler DONE. Test mục 1 PASS, mục 2 FAIL (bug #2 đang debug). |
| 1.0 | 11/07/2026 13:14 | Giai đoạn 1 DONE — thêm 2 handler mới `BTN_ExpandAll`/`BTN_CollapseAll.OnClicked` (nối thẳng, không Custom Event trung gian). Cập nhật "Chưa build" (bỏ ExpandAll/CollapseAll — đã DONE). Test status: mục 1-5 PASS (expand/collapse + Mở tất cả/Thu gọn + nhớ state con cháu, 6A xác nhận); mục 6-10 chưa chạy (Giai đoạn 2 — search). |
