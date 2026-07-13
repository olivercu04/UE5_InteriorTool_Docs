# WBP_FolderTreePicker
**Phiên bản:** 1.3 — ✅ DONE | **Tạo:** 11/07/2026 11:17 — C5.8 Task Card #2 Part B lần 1 | **Sửa:** 13/07/2026 — 2d Phần 2 (`BeginRenameOnPath`) + Card 1 (`ExpandToPath`, `CurrentPath`/`bShowCurrentTag`, `OnRequestCommitRename`) + bug fix `SetSelectedHighlight` so sai biến

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
| `CurrentSearchFolder` | String | "" | Giai đoạn 2 (12/07) — class var, thay Local `QueryStr` cũ (`RefreshVisibleRows` không tự query widget, đọc lại biến này) |
| `CurrentPath` | String | "" | MỚI 13/07 (Card 1) — path "hiện tại" (vd folder đang chứa combo đang move), dùng cho `SetCurrentTag` |
| `bShowCurrentTag` | Boolean | false | MỚI 13/07 (Card 1) — bật/tắt hiển thị tag "hiện tại" (Save dialog không cần, Move dialog cần) |

## Event Dispatcher
```
OnFolderSelected(Path : String)               ← đã có, xác nhận lại thật 13/07 (không còn ⚠️ SUY LUẬN)
OnRequestCommitRename(OldPath : String, NewName : String)   ← MỚI 13/07 (Card 1)
```

## Functions

### `IsPathVisible(Path : String) → Boolean` (DONE, K2Node export xác nhận — Giai đoạn 4, 12/07)
Local var: `Segments : Array<String>`, `n : Integer`, `bHidden : Boolean`, `CurrentPrefix : String`.
```
FunctionEntry(Path)
  ▶ SET Segments = ParseIntoArray(Path, Delimiter="/", CullEmptyStrings=true)
  ▶ SET n = Array_Length(Segments)
  ▶ SET bHidden = false
  ▶ Branch(n <= 1)
       True  → Return true                                    ← top-level/1-segment luôn visible
       False → SET CurrentPrefix = Segments[0]
               ▶ ForEachLoopWithBreak(Segments):
                    Branch(ArrayIndex >= n-1)
                       True  → Break                            ← bỏ qua segment cuối (chính node đang xét)
                       False → Branch(NOT Array_Contains(ExpandedFolders, CurrentPrefix))
                                  True  → SET bHidden = true → Break   ← tổ tiên chưa mở → ẩn, thoát sớm
                                  False → SET CurrentPrefix = CurrentPrefix + "/" + Segments[ArrayIndex+1]
                                          (loop tự next)
               Completed/Break → Return NOT bHidden
```
Loop dùng **ForEachLoopWithBreak** (không phải For Loop With Break thường) — thoát sớm ngay khi phát hiện 1 tổ tiên chưa mở, không cần duyệt hết mảng. `CurrentPrefix` build tích lũy theo từng segment (cùng pattern `AccumPath` trong `BuildSearchOverride`), chỉ kiểm tra CÁC TỔ TIÊN (bỏ qua segment cuối = chính node). Node hiện ⇔ mọi tổ tiên ∈ `ExpandedFolders`. Test Print PASS: top-level=True, tổ tiên chưa expand=False, nested-chain sâu đúng.

### `RefreshVisibleRows()` (DONE — SINGLE SOURCE expand-mode + search-mode, Giai đoạn 2 ghép xong 12/07)
Local var thêm: `SearchBool : Boolean` (ngoài `bShow`/`Row`/`node` có sẵn). `QueryStr` cũ đã XÓA — đọc `CurrentSearchFolder` (class var, xem Variables) thay vì tự query `SB_SearchFolder`.
As-built export K2Node thật (cuhoang xác nhận PASS test mục 6-9 + bổ sung):
```
▶ Clear Children(SB_Rows)
▶ ForEachLoop(Folders):
     SET node = Array Element → Break S Folder Tree Node(node) → Path, DisplayLabel
     IsPathVisible(Path) → SearchBool_tmp1        ← (wire cũ, giữ nguyên vị trí gọi)
     PathMatchesQuery(Path=DisplayLabel, Query=CurrentSearchFolder) → MatchBool
     Array_Contains(SearchExpandOverride, Path) → InOverrideBool
     Array_Contains(ExpandedFolders, GetParentPath(Path)) → InManualExpandBool
     BooleanOR(MatchBool, InOverrideBool, InManualExpandBool) → SearchBool
     Select(Index=bIsSearching, Option False=IsPathVisible.ReturnValue, Option True=SearchBool) → SET bShow
     Branch(bShow) True →
        Create Widget(WBP_FolderPickerRow) → Row
        Row.SetNode(node)
        Row.SetCurrentTag( bShowCurrentTag AND (node.Path == CurrentPath) )       ← MỚI 13/07 (Card 1)
        Row.SetSelectedHighlight( node.Path == SelectedPath )   ← MỚI 13/07, [BUG-FIX] TÁCH RIÊNG so sánh
                                                                    (trước fix: dùng chung "===" với
                                                                    nhánh CurrentTag, so nhầm CurrentPath)
        Branch(bIsSearching):
           True  → Row.SetExpanded(Array_Contains(ExpandedFolders,Path)) → Row.SetSearchHighlight(MatchBool)
           False → Row.SetExpanded(Array_Contains(ExpandedFolders,Path)) → Row.SetSearchHighlight(False)   ← wire cũ, giữ nguyên
        Bind Row.OnRowExpandClicked → HandleRowExpandClicked
        Bind Row.OnRowSelected → HandleRowSelected
        Bind Row.OnRowRenameCommitted → HandleRowRenameCommitted   ← MỚI 13/07 (2d Phần 2), chỗ bind mỗi row đã có
        Add Child(SB_Rows, Row)
   Completed → hết hàm
```
⚠️ Điểm mấu chốt khác pseudocode gốc: `SetExpanded` ở CẢ 2 nhánh `bIsSearching` giờ dùng CHUNG công thức `Array_Contains(ExpandedFolders, Path)` — nhánh search KHÔNG còn hardcode `True` (bug 2.3). `bShow` khi search thêm điều kiện `InManualExpandBool` (qua `GetParentPath`) để lộ con khi user tự click arrow mở tổ tiên trong lúc đang search (bug 2.3/2.4).

### `PathMatchesQuery(Path : String, Query : String) → Boolean` (Pure, DONE Giai đoạn 2)
```
▶ Contains(Search In=Path, Substring=Query, Use Case=[trống — không phân biệt hoa thường], Search from End=[trống]) → Return Value
```
1 node duy nhất, Pure (không exec pin, không Branch). Gọi với `Path=node.DisplayLabel` (KHÔNG phải `node.Path` đầy đủ — bug 2.1: substring trên full path match nhầm cả con không liên quan).

### `BuildSearchOverride(Query : String)` (DONE Giai đoạn 2)
Local var: `Segments : Array<String>`, `AccumPath : String`.
```
▶ Array Clear(SearchExpandOverride)
▶ ForEachLoop(Folders):
     Break node → Path, DisplayLabel
     PathMatchesQuery(Path=DisplayLabel, Query) → Branch
        True → ParseIntoArray(Path, Delimiter="/", Cull Empty Strings=✓) → SET Segments
                SET AccumPath = ""
                ForLoop(First=0, Last=Segments.Length-2):
                   Branch(Index==0)
                      True  → AccumPath = GET(Segments, Index)
                      False → AccumPath = Append(AccumPath, "/", GET(Segments, Index))
                   [merge] → Array_AddUnique(SearchExpandOverride, AccumPath)
        False → (bỏ qua, outer loop tự next)
   Completed → hết hàm (không Return Node)
```
`Array_AddUnique` (không phải `Array_Add`) — tránh trùng khi nhiều node con cùng match kéo chung 1 tổ tiên. Top-level match (1 segment) → `Length-2=-1` → ForLoop không chạy vòng nào → không add gì (đúng, top-level luôn visible sẵn).

### `GetParentPath(Path : String) → String` (Pure, DONE Giai đoạn 2 — hỗ trợ bug 2.3)
```
▶ Find Substring(Search In=Path, Substring="/", Search from End=✓, Start Position=-1) → Index
▶ Branch(Index == -1)
     True  → Return ""
     False → Return Left(Path, Index)
```
Tìm dấu `/` CUỐI CÙNG (`Search from End=✓`, khác `Find` thường tìm từ đầu). Pure function vẫn dùng `Branch` — hợp lệ (không có exec pin ở Entry/Return, Branch chạy qua dependency chain của data pin).

### `BeginRenameOnPath(Path : String, Siblings : Array<String>)` — Function MỚI (13/07, 2d Phần 2)
Local: `Children`, `RowRef`, `bFound`
```
▶ SET Children = Get All Children(SB_Rows)
▶ SET bFound = False
▶ ForEachLoopWithBreak(Children):
     Cast Element → WBP_FolderPickerRow → RowRef
       Cast OK → Branch(RowRef.GetRowPath() == Path)
                    True  → RowRef.EnterRenameMode(Siblings) → SET bFound=True → Break
                    False → tiếp loop
       Cast Failed → tiếp loop
   Completed → Branch(NOT bFound) True → Print "không tìm thấy row" [DevelopmentOnly]
```

### `ExpandToPath(Path : String)` — Function MỚI (13/07, Card 1)
Local: `Segments`, `AccumPath`
```
▶ ParseIntoArray(Path, "/", CullEmpty=✓) → SET Segments
▶ SET AccumPath = ""
▶ ForLoop(0 → Segments.LastIndex):        ← chạy TỚI HẾT (khác BuildSearchOverride n-2, chủ đích)
     Branch(Index==0) True→ AccumPath=Segments[0]
                      False→ AccumPath=Concat(AccumPath,"/",Segments[Index])
     [merge] → Array_AddUnique(ExpandedFolders, AccumPath)
Completed → hết (KHÔNG tự gọi RefreshVisibleRows — caller quyết định)
```

### `SetFolders(Nodes)` — SỬA (bug đã fix, ghi lesson)
Thân 2a cũ (tự loop tạo row) → thay bằng:
```
▶ SET Folders = Nodes
▶ RefreshVisibleRows()
```
**Bug lesson:** Sonnet quên nhắc sửa theo bước 4e task card → breakpoint không fire. Phát hiện + fix bởi cuhoang, verify Print `IsPathVisible` PASS.

## Custom Events
```
HandleRowExpandClicked(Path): Branch(Array_Contains(ExpandedFolders,Path))    ⚠️ SUY LUẬN theo §5 task card
   True→Remove Item · False→Add Unique · [merge] → RefreshVisibleRows()

HandleRowSelected(Path) — xác nhận thật 13/07, xoá cờ ⚠️ SUY LUẬN:
  ▶ SET SelectedPath = Path
  ▶ RefreshVisibleRows()
  ▶ Broadcast OnFolderSelected(Path)
```
Thứ tự bắt buộc: `RefreshVisibleRows` TRƯỚC `Broadcast` — caller nhận event khi UI đã render highlight xong.

### `HandleRowRenameCommitted(Path, NewName)` — Custom Event MỚI (bound, 13/07, 2d Phần 2)
```
▶ Broadcast OnRequestCommitRename(Path, NewName)
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

## Events — SB_SearchFolder.OnSearchTextChanged (DONE, Giai đoạn 2, 12/07)
`ComponentBoundEvent` trên `SB_SearchFolder`:
```
BoundEvent(Text)
   ▶ SET CurrentSearchFolder = Conv_TextToString(Text)     ← class var, MỚI (thay Local QueryStr cũ)
   ▶ Trim(Conv_TextToString(Text)) → Len → EqualEqual(0)
   ▶ IfThenElse(Len==0)
        True  → SET bIsSearching = False → Array_Clear(SearchExpandOverride)
        False → SET bIsSearching = True  → BuildSearchOverride(CurrentSearchFolder)
        [merge] → RefreshVisibleRows()
```
Ghi chú as-built: `Conv_TextToString(Text)` gọi 2 lần độc lập (1 cho `SET CurrentSearchFolder`, 1 cho `Trim`) — cùng input `Text` từ delegate pin, không phải bug, chỉ 2 pure node riêng thay vì dùng chung 1 local var trung gian. Không ảnh hưởng hành vi.

## Chưa build
(Không còn — `2d — rename host` DONE 13/07: `BeginRenameOnPath` + `ExpandToPath` + Card 1. `PathMatchesQuery` · `BuildSearchOverride` · nhánh search trong `RefreshVisibleRows` · `SB_SearchFolder.OnSearchTextChanged` · `GetParentPath` — đều đã DONE (Giai đoạn 2).)

## Test status
Mục 1-5 PASS (Giai đoạn 1, xác nhận 11/07).
Mục 6 (search "sofa" → chỉ đường Livingroom→Sofa hiện, Sofa highlight vàng), 7 (search "com" → mọi đường tới node khớp hiện, mỗi match highlight riêng), 8/6A (xóa query → về đúng state expand trước search), 9 (search "zzz" → SB_Rows trống, không crash) — PASS (Giai đoạn 2, 12/07).
Bổ sung: click arrow node đang match trong lúc search → lộ con — PASS (sau fix bug 2.3/2.4).
Mục 10 (click tên → SelectedPath đúng, UI PHẢI đổi highlight xanh — [SCOPE] kỳ vọng test cũ "UI không đổi" SUPERSEDED sau Card 1; click arrow → không fire OnFolderSelected) — PASS (Giai đoạn 3, 12/07 + xác nhận lại 13/07).

**13/07 (2d + Card 1):**
```
Phần 2 test 1, 2 (BeginRenameOnPath tìm đúng row + commit qua Picker)   ✅
Test 6 (path không tồn tại) — CHƯA TEST, rủi ro thấp, defer
M1-M6 (Wire Move full flow, mirror REG A1-A2)                            ✅ tất cả PASS
  M3 lúc đầu FAIL (highlight sai biến) → fix → PASS lần 2
0.3 hồi quy hiển thị (ExpandAll/CollapseAll + expand/collapse lẻ)       ✅
```

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 0.9 | 11/07/2026 11:17 | Khởi tạo (IN PROGRESS) — C5.8 Task Card #2 Part B lần 1: Layout (HB_Toolbar + SB_SearchFolder) + Variables (Folders/ExpandedFolders/SelectedPath/bIsSearching/SearchExpandOverride) + `IsPathVisible` DONE + `RefreshVisibleRows` DONE (nhánh search ⚠️ SUY LUẬN, chưa ghép) + `SetFolders` bug fix + 2 Custom Event handler DONE. Test mục 1 PASS, mục 2 FAIL (bug #2 đang debug). |
| 1.0 | 11/07/2026 13:14 | Giai đoạn 1 DONE — thêm 2 handler mới `BTN_ExpandAll`/`BTN_CollapseAll.OnClicked` (nối thẳng, không Custom Event trung gian). Cập nhật "Chưa build" (bỏ ExpandAll/CollapseAll — đã DONE). Test status: mục 1-5 PASS (expand/collapse + Mở tất cả/Thu gọn + nhớ state con cháu, 6A xác nhận); mục 6-10 chưa chạy (Giai đoạn 2 — search). |
| 1.1 | 12/07/2026 10:40 | Giai đoạn 2 (Search) + Giai đoạn 3 (Select) DONE. Thêm 3 Function mới: `PathMatchesQuery` (Pure), `BuildSearchOverride`, `GetParentPath` (Pure, hỗ trợ bug 2.3). `RefreshVisibleRows` ghép xong nhánh search (as-built thật, không còn ⚠️ SUY LUẬN) — `SetExpanded` bỏ hardcode `True`, dùng chung công thức `Array_Contains(ExpandedFolders,Path)` cả 2 nhánh. Thêm Event `SB_SearchFolder.OnSearchTextChanged`. Thêm class var `CurrentSearchFolder` (thay Local `QueryStr`). Bug fix: 2.1 (`PathMatchesQuery` dùng `DisplayLabel` thay `Path` đầy đủ), 2.3 (`bShow` thêm điều kiện qua `GetParentPath` để lộ con khi manual-expand trong lúc search). Test mục 1-10 PASS hết. |
| 1.2 | 12/07/2026 16:03 | Giai đoạn 4 (Chốt sổ) — gỡ cờ ⚠️ SUY LUẬN của `IsPathVisible`: thay bằng node flow as-built đầy đủ (K2Node export xác nhận). Loop = `ForEachLoopWithBreak` (thoát sớm khi gặp tổ tiên chưa mở), `CurrentPrefix` build tích lũy qua từng segment, bỏ qua segment cuối (chính node). Không đổi hành vi — chỉ hoàn thiện tài liệu. |
| 1.3 | 13/07/2026 | **2d Phần 2 (rename host) + Card 1 (current tag/select) DONE.** Var mới `CurrentPath`/`bShowCurrentTag`. Dispatcher mới `OnRequestCommitRename`; `OnFolderSelected` xác nhận thật (gỡ cờ SUY LUẬN). Function mới `BeginRenameOnPath` (tìm row qua `GetRowPath()`, gọi `EnterRenameMode`) + `ExpandToPath` (Card 1, chạy hết mảng — khác `BuildSearchOverride`). `RefreshVisibleRows`: thêm `Row.SetCurrentTag`/`Row.SetSelectedHighlight` ngay sau `SetNode`, thêm bind `Row.OnRowRenameCommitted`→`HandleRowRenameCommitted`. `HandleRowSelected`: xác nhận thật + thêm `RefreshVisibleRows()` TRƯỚC `Broadcast`. Custom Event mới `HandleRowRenameCommitted` (relay `OnRequestCommitRename`). [BUG-FIX] `SetSelectedHighlight` trước đó so sai biến (dùng chung so sánh với nhánh CurrentTag) — tách riêng so với `SelectedPath`. Test PASS: Phần 2 (1,2), M1-M6, 0.3. Xóa "Chưa build". |
