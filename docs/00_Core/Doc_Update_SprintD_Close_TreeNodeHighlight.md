# Cập nhật Doc — Đóng Sprint D Furniture + TreeNode/Chip Highlight
**Phiên bản:** 1.0 | **Ngày:** 18/06/2026 — 09h53p ICT | Lighting_Mnger UE5.5.4
**Phạm vi:** Patch cho 6 file trong `docs/`. Đã đối chiếu lại lịch sử 3 phiên làm việc gần nhất (D.T1/D.T7/D.T9 regression, 2 bug phụ, TreeNode/Chip highlight) để chắt lọc flow logic ĐÚNG cuối cùng — không phải plan gốc, không phải các bản nháp bị sửa giữa đường.

---

## TÓM TẮT

Sprint D Furniture (D.T1-D.T9) đã đóng hoàn toàn từ 17/06 — checklist trong `PROGRESS.md` hiện ĐANG SAI (lệch số/trùng nhãn giữa các task), patch #1 sửa lại đúng. 2 bug phụ phát hiện trong lúc regression D.T9 đã fix xong. Sau đó, một tính năng mới (TreeNode/Chip active-folder highlight) được build thêm và đã hoàn thành + test PASS hôm nay (18/06). Sprint tiếp theo là **Sprint 5 — Combo Mesh, deadline 20/06**.

---

## 1. PATCH `docs/00_Core/PROGRESS.md`

### 1.1 Thay khối checklist Sprint D hiện tại (đang lệch số) bằng bảng đúng:

```markdown
## SPRINT D — Data Layer v2 (17/06/2026) ✅ HOÀN THÀNH

- [x] D.T1 — Single-instance inventory toggle Visibility + box-select guard
      (Is In Viewport → Get Visibility)
- [x] D.T2 — Data prep: S_FurnitureData +ThumbnailSoft (Soft Object Ref Texture2D)
      + Python populate
- [x] D.T3 — FilterFurnitureRows C++ (mirror FilterMaterialItems, cached FProperty
      reflection, KHÔNG reinterpret_cast vì S_FurnitureData là UserDefinedStruct)
      — verify PASS: rỗng → 2114 rows, "sofa" → 136 rows
- [x] D.T4 — BP_FurnitureItemView (Object class, 10 field: RowName/VieName/EngName/
      ThumbnailSoft/MeshSoft/MeshFolderPath/BoundingSize/Description/Link/Category)
- [x] D.T5 — FilterBySearch nhánh Furniture rewire: FilterFurnitureRows →
      AllFilteredFurnitureRows → DisplayPage. Recent/Favorite bypass C++ filter,
      build trực tiếp từ BP_FurnitureUserPrefsManager.
- [x] D.T6 — Bỏ FurnitureDA, Replace Mesh đọc RowName từ actor (17/06/2026) ✅
      [danh sách chi tiết 9 file/doc bị ảnh hưởng — giữ nguyên mục cũ phía dưới,
      không lặp lại ở đây]
- [x] D.T7 — BuildFolderTree C++ source swap (DT_FurnitureCatalog thay
      AllFurnitureItems) + xóa preload AllFurnitureItems khỏi Event Construct
      Then 1. Bug phụ phát hiện & fix trong lúc làm: substring/Contains sai khi
      tìm Folder "Table" (Map_Find.Value chứ không phải ReturnValue/Found).
- [x] D.T8 — WBP_FurnitureInventory dùng đầy đủ luồng DataTable+RowName (R5),
      tích hợp xong qua D.T5+D.T6+D.T7.
- [x] D.T9 — Regression toàn bộ (9/9 PASS) + dọn doc — xem mục 1.2 bên dưới.

**Lưu ý:** bảng D.T1-D.T9 ở bản trước bị lệch nhãn (vd dòng "D.T2" ghi nhầm nội
dung của D.T7, dòng "D.T5"/"D.T8" ghi nhầm nội dung D.T3) — bảng trên đã map lại
đúng theo định nghĩa gốc trong `02_Current_Sprint.md`.
```

### 1.2 Thêm mục — 2 bug phụ phát hiện trong D.T9 regression:

```markdown
### D.T9 — Regression 9 case (17/06/2026)

| # | Case | Kết quả |
|---|---|---|
| 1 | Browse: search "sofa", folder Table, pagination, tab Material↔Furniture, Recent/Favorite | PASS |
| 2 | Mở/đóng inventory 10 lần qua nút + BTN_Close, click trái chọn ngay lần đầu | PASS |
| 3 | Drag-drop spawn 1 mesh + nhiều mesh liên tiếp | PASS |
| 4 | Replace 1 mesh + multi-replace | PASS |
| 5 | Popup ⓘ — tên/category/description đúng | PASS |
| 6 | Save → Load → mesh đúng vị trí, RowName giữ nguyên | PASS |
| 7 | Undo/Redo sau spawn, replace, group, multi-select | PASS |
| 8 | Box select: đóng inventory không hiện khung; mở lại chạy bình thường | PASS |
| 9 | PIE liên tiếp 3 lần, không crash VRAM bất thường | PASS |

**2 bug phụ phát hiện trong lúc test case 1, đã fix:**

- **Bug-Pagination:** Furniture dừng ở "7/8" dù hiển thị ban đầu đúng "1/8".
  Root cause: `Ceil(LENGTH / PageSize)` ở nhánh check nút Next dùng Int Divide
  (337÷48=7, mất phần dư) trong khi `DisplayPage` dùng Float Divide (337/48=7.02
  → Ceil=8) — 2 chỗ tính `TotalPages` lệch nhau 1. Fix: chèn `Int to Float` giữa
  LENGTH và input A của node `÷`, ở CẢ 2 nhánh Material và Furniture (cấu trúc
  copy giống nhau). Verify: Next liên tục → đúng dừng ở "8/8".
- **Bug-Maximize:** `BTN_Maximize` chỉ nở ngang từ vị trí cũ, không nhảy lên
  góc trên-trái như Maximize chuẩn. Root cause: cả 2 nhánh Maximize/Restore chỉ
  gọi `Set Size` trên Canvas Slot của `VerticalBox_0`, thiếu `Set Position` trên
  CÙNG slot — `Set Position in Viewport(self,...)` không có tác dụng vì vị trí
  cửa sổ thật do Canvas Slot Position của `VerticalBox_0` điều khiển (theo logic
  drag title bar có từ trước). Fix: thêm `Set Position` vào cùng node
  `Slot as Canvas Slot(VerticalBox_0)` đang nuôi `Set Size`, ở cả 2 nhánh —
  Maximize: Position=(0,0); Restore: Position=Original Position. Verify:
  Maximize đúng góc, Restore đúng vị trí/size cũ, drag sau Restore vẫn ổn.
```

### 1.3 Thêm mục mới — tính năng bổ sung sau Sprint D (18/06/2026):

```markdown
## TÍNH NĂNG BỔ SUNG — TreeNode/Chip Active-Folder Highlight (18/06/2026) ✅

Không nằm trong scope Sprint D gốc — phát sinh từ yêu cầu UX: category/folder
đang chọn trong inventory phải đổi màu và giữ màu khi đi sâu vào folder con.

- `WBP_TreeNode.RefreshDisplay` thêm param `bIsActive` → SetBackgroundColor.
- `WBP_ChipTag` thêm Custom Event `SetHighlight(bIsActive)` tương tự.
- Function Pure mới `IsPathActive(ThisPath)` trong `WBP_FurnitureInventory`:
  `CurrentFolderPath==ThisPath OR CurrentFolderPath StartsWith(ThisPath+"/")`.
- Function `UpdateFolderHighlights` (impure): loop cây TreeNode + loop chip rows,
  gọi `IsPathActive` bằng FolderPath của TỪNG widget, set highlight tương ứng.
  3 điểm gọi: cuối `CreateChipTagsForPath`, trong `OnChipTagClicked` (2 nhánh
  merge), và SAU `FilterByFolderPath` ở cả 2 nhánh `OnTreeNodeClicked`.
- Fix kèm: `BTN_FavoriteCategory`/`BTN_RecentCategory` không ẩn chip cũ khi
  chuyển category đặc biệt — thêm `ClearChildren(VB_ChipTagArea)` +
  `SetVisibility(TB_Breadcrumb, Collapsed)` đầu function.
- Test full: chuyển tab, click cấp 1, vào sâu chip cấp 2/3, quay lại "All",
  Recent/Favorite — tất cả PASS.

Chi tiết kỹ thuật đầy đủ (bug đã gặp + fix) xem mục 5 và 6 bên dưới.

**Tiếp theo:** Sprint 5 — Combo Mesh, deadline 20/06/2026.
```

---

## 2. PATCH `docs/00_Core/01_Session_State.md`

Thay mục "TIẾP THEO" / trạng thái hiện tại bằng:

```markdown
## Trạng thái (18/06/2026)

Gate 1 ✅ DONE (16/06). Sprint D Furniture (D.T1-D.T9) ✅ DONE (17/06) — full
regression 9/9 PASS + 2 bug phụ fix (pagination Int/Float, Maximize Position).
TreeNode/Chip active-folder highlight ✅ DONE (18/06, tính năng bổ sung ngoài
scope gốc).

## BUG CÒN MỞ
(không có bug Sprint D nào còn mở — xem `Bugs/Open_Bugs.md` đã cập nhật)

## TIẾP THEO

**Sprint 5 — Combo Mesh** (hard deadline 20/06/2026, file thực thi
`Sprint5_Combo_Execution_v1_1.md` / `docs/Sprints/Sprint5/Combo_Execution.md`).
Sau đó: Sprint 7 Material v1.2 → Sprint 6 Polish → Gate 2 (packaged build).
```

---

## 3. PATCH `docs/00_Core/DEVIATIONS.md` (thêm dòng mới)

```markdown
| Ngày | Mục | Lệch / Quyết định |
|---|---|---|
| 17/06 | D.T9 | Phát hiện thêm 2 bug ngoài checklist gốc (pagination Int/Float, Maximize Position) — fix ngay trong cùng phiên, không defer. |
| 17/06 | PROGRESS.md | Checklist D.T1-D.T9 bị lệch nhãn giữa các task khi cập nhật — phát hiện và sửa lại lúc làm doc update 18/06 (xem PROGRESS.md mục Sprint D). |
| 17-18/06 | TreeNode highlight | Approach ban đầu (Phase 1: wire `==` trực tiếp giữa Array Element và ActiveLevel1Path vào RefreshDisplay.bIsActive cho riêng cấp 1) bị THAY THẾ bằng kiến trúc tập trung `IsPathActive`/`UpdateFolderHighlights` để hỗ trợ cả chip cấp 2/3 — không sửa từng phần nữa mà viết lại logic chung. Bug học được: `UpdateFolderHighlights` phải đọc FolderPath của TỪNG widget trong loop, không phải biến class — dùng nhầm biến class từng gây tô màu sai/tô tất cả khi click category. |
```

---

## 4. PATCH `docs/Bugs/Open_Bugs.md`

Thêm 2 dòng vào bảng tổng quan + 2 mục chi tiết, theo đúng format file hiện có:

```markdown
| Bug-Pagination | ✅ FIXED (17/06, D.T9) — Furniture pagination dừng ở 7/8 thay vì 8/8 | — | Xem WBP_FurnitureInventory.md, mục DisplayPage |
| Bug-Maximize | ✅ FIXED (17/06, D.T9) — BTN_Maximize không nhảy về góc trên-trái | — | Xem WBP_ResizeWindow.md |
```

(Nội dung chi tiết 2 bug đã viết đầy đủ ở mục 1.2 phía trên — copy nguyên vào đây dưới đúng heading `## Bug-Pagination` / `## Bug-Maximize` theo format các bug khác trong file.)

---

## 5. PATCH `docs/Widgets/WBP_FurnitureInventory.md` → bump version 2.6

```markdown
> **v2.6 (18/06/2026):** Thêm `IsPathActive` (Pure) + `UpdateFolderHighlights`
> cho tính năng active-folder highlight (xem chi tiết node flow mục dưới).
> `BTN_FavoriteCategory`/`BTN_RecentCategory` thêm ClearChildren+Collapse
> breadcrumb đầu function. Fix Bug-Pagination: Int to Float trước Ceil ở cả
> 2 nhánh Material/Furniture trong logic Next-page.

### IsPathActive(ThisPath: String) → ReturnValue: Boolean — Pure function
```
CurrentFolderPath ●→ ==.A
ThisPath ●→ ==.B
ThisPath ●→ Append.A("/" ●→ Append.B) ●→ StartsWith.InPrefix
CurrentFolderPath ●→ StartsWith.SourceString
==.ReturnValue ●→ OR.A
StartsWith.ReturnValue ●→ OR.B
OR ▶/●→ Return Node.ReturnValue
```
⚠ Pure function — KHÔNG được chèn node impure (Print String...) vào đây, sẽ phá
exec flow. Debug chỗ này phải đặt ở hàm GỌI nó (UpdateFolderHighlights), không
đặt trong chính IsPathActive.

### UpdateFolderHighlights() — impure Function
```
ForEach(VerticalBox_44.Children) → Cast WBP_TreeNode
  → GET FolderPath (CỦA NODE NÀY, không phải biến class)
  → IsPathActive(FolderPath) → RefreshDisplay(bIsActive=ReturnValue)
ForEach(VB_ChipTagArea.Children) → Cast WBP_ChipRow
  → ForEach(HorizontalBox_ChipRow.Children) → Cast WBP_ChipTag
    → GET FolderPath_ChipTag → IsPathActive(...) → SetHighlight(bIsActive=...)
```

**3 điểm gọi `UpdateFolderHighlights`:**
1. Cuối `CreateChipTagsForPath` — gắn vào `Completed` của ForEachLoopWithBreak
   ngoài cùng (trước đây dead-end).
2. Trong `OnChipTagClicked` — gắn vào `then` của `AddChild` (thêm ChipRow vào
   VB_ChipTagArea, KHÔNG phải AddChild thêm ChipTag vào HorizontalBox_ChipRow)
   VÀ nhánh False của `Map_Find(FolderTree, SelectedPath)` (case leaf) — merge
   2 dây exec vào 1 node gọi.
3. Trong `OnTreeNodeClicked` — SAU `FilterByFolderPath`, ở CẢ 2 nhánh
   (IndentLevel==0 true/false). ⚠ KHÔNG gọi trong `PopulateTreeColumn` —
   PopulateTreeColumn chạy TRƯỚC khi CurrentFolderPath kịp set bởi
   FilterByFolderPath, gây bug "All sáng lần đầu, đổi category không sáng gì,
   click lại All thì TẤT CẢ category khác sáng lên" (do StartsWith với chuỗi
   rỗng trả True cho mọi chuỗi khi CurrentFolderPath chưa set).

### Pagination — fix Bug-Pagination
```
CŨ:  LENGTH(AllFilteredFurnitureRows) ●→ ÷.A (Int) | PageSize ●→ ÷.B (Int) → Ceil
MỚI: LENGTH ●→ Int to Float ●→ ÷.A (Float) | PageSize ●→ ÷.B → Ceil
```
Áp dụng ở CẢ 2 nhánh Material và Furniture (cấu trúc bị copy giống nhau).
```

---

## 6. NỘI DUNG MỚI cho `docs/Widgets/WBP_TreeNode.md` và `WBP_ChipTag.md`
(tạo file mới nếu chưa có, hoặc gộp vào WBP_FurnitureInventory.md tùy cuhoang)

```markdown
### WBP_TreeNode.RefreshDisplay — v1.1 (18/06/2026)
Thêm param `bIsActive: Boolean`. Sau logic SetText/SetSize hiện có:
```
Branch(bIsActive)
  True  → SetBackgroundColor(Button_58, [màu highlight])
  False → SetBackgroundColor(Button_58, (1,1,1,1))
```

### WBP_ChipTag — Custom Event mới `SetHighlight(bIsActive: Boolean)`
Cùng pattern Branch→SetBackgroundColor, áp lên `Button_ChipTag`. Vars có sẵn:
`FolderPath_ChipTag`, `FolderName_ChipTag`, `IndentLevel_ChipTag`,
`Button_ChipTag`, `TextBlock_ChipTag`. Dispatcher `OnChipSelected` fires
`Selected Path Chip Tag`/`Indent Level Chip Tag` trên `Button_ChipTag.OnClicked`.
```

---

## 7. PATCH `docs/Widgets/WBP_ResizeWindow.md`

```markdown
> **Fix Bug-Maximize (17/06/2026):** Maximize/Restore branch thiếu `Set Position`
> trên Canvas Slot của `VerticalBox_0` (chỉ có `Set Size`) → cửa sổ nở size đúng
> nhưng không di chuyển, vẫn dính vị trí cũ. Thêm `Set Position` vào CÙNG node
> `Slot as Canvas Slot(VerticalBox_0)`:
> - Maximize (True): Position = (0,0)
> - Restore (False): Position = Original Position
> `Set Position in Viewport` gọi trên `self` giữ nguyên không xóa — không ảnh
> hưởng, vị trí cửa sổ thật điều khiển qua Canvas Slot Position của
> `VerticalBox_0` (theo logic drag title bar gốc).
```

---

## Việc còn lại (không gấp)
- Tạo file riêng `WBP_TreeNode.md`/`WBP_ChipTag.md` nếu muốn tách khỏi
  WBP_FurnitureInventory.md (hiện 2 widget này có thể chưa có doc riêng).
- Xác nhận `Open_Bugs.md` format chính xác 2 mục Bug-Pagination/Bug-Maximize
  khớp style các bug khác trong file (chưa xem được full file gốc).
