# Phase 0 Verify Report — Replace UX Fix (sau C9)
**Ngày:** 01/08/2026 | **Từ:** Sonnet (execution) | **Gửi:** Opus (architect) — qua cuhoang
**Nguồn plan gốc:** v1 — `docs/Archive/01-08-2026_ReplaceUX_Fix_Execution_Plan_v1_SUPERSEDED.md`
(SUPERSEDED, giữ tham chiếu lịch sử — link cập nhật 01/08 khi archive, xem ghi chú cuối file).
**Plan canonical hiện hành (đã tích hợp report này):** `01-08-2026_ReplaceUX_Fix_Execution_Plan.md`
(cùng thư mục).

> Kết luận trước: **KHÔNG code P1 khi chưa đọc report này.** Cả 5/5 mục verify ĐÃ XONG.
> Còn 2 vấn đề chặn cứng cần Opus quyết trước khi code: gap kiến trúc chip-builder combo
> (mục 6.3, chặn P1.1) và câu hỏi treo cơ chế minimize (mục 7, chặn P3.2).

---

## 1. TÓM TẮT TRẠNG THÁI

| Mục | Trạng thái | Kết quả |
|---|---|---|
| V0.1 | ✅ VERIFIED | Khớp giả thuyết plan |
| V0.2 | ✅ VERIFIED | **KHÁC giả thuyết plan** — xem mục 3 |
| V0.3 | ✅ VERIFIED | Khớp giả thuyết plan — xem mục 4 |
| V0.4 | ✅ VERIFIED | Khớp, còn rõ hơn plan đoán — xem mục 5 |
| V0.5 | ✅ VERIFIED | Khớp nhưng phát sinh gap kiến trúc — xem mục 6 |
| Bonus | ✅ | 3 doc-drift + 1 câu hỏi treo (mục 7) |

**Trạng thái Phase 0: HOÀN TẤT 5/5 mục.** Còn 2 điểm cần Opus quyết trước khi code P1:
gap kiến trúc combo chip-builder (mục 6.3) và cơ chế minimize chưa xác định (mục 7).

---

## 2. V0.1 — StartReplaceComboMode khối cuối

**Giả thuyết:** không gọi rebuild chiptag. **Kết quả:** ĐÚNG.

```
PopulateComboTreeColumn() → UpdateComboFolderHighlights() → RefreshComboCardReplaceMode() → Return
```
Không có bước rebuild chiptag/chiprow nào. Gốc bug #3b xác nhận.

---

## 3. V0.2 — Đảm-bảo-inventory-mở, mesh vs combo

**Giả thuyết plan:** mesh CÓ khối 3 nhánh (IsValid × IsInViewport), combo THIẾU.
**Kết quả:** SAI — 2 nhánh **cấu trúc giống hệt nhau** (mirror cố ý, đúng doc
`BP_FurnitureInputManager.md`: *"StartReplaceComboMode — Mirror cấu trúc 3 nhánh của
StartReplaceMode... cố ý KHÔNG gộp helper dùng chung"*).

**Khác biệt thật tìm được** (không phải cái plan đoán):

```
StartReplaceMode (mesh):
  Branch(IsInViewport)
    True  ▶→ EnterReplaceMode → FilterByFolderPathWithUI → ...
    False ▶→ Create Widget → ... → EnterReplaceMode → FilterByFolderPathWithUI → ...

StartReplaceComboMode (combo):
  Branch(IsInViewport)
    True  ▶→ SwitchInventoryMode(Combo)   → KHÔNG qua EnterReplaceMode/FilterByFolderPathWithUI
    False ▶→ Create Widget → ... → SwitchInventoryMode(Combo)   → cũng KHÔNG qua
```

→ Combo bỏ qua **toàn bộ** `EnterReplaceMode` → `FilterByFolderPathWithUI`, không phải
thiếu 1 node lẻ. Đây là gốc sâu hơn plan nghĩ, giải thích chung cho #3b (mục 2) — nhưng
**KHÔNG giải thích được #3a (minimize)** — xem mục 7, EnterReplaceMode không hề set
Visibility cho cả cửa sổ, chỉ set Visibility 2 CTV card container bên trong.

**Tác động lên plan:** P1.2 ("thêm 1 dòng gọi RebuildChipRowForCurrentContext vào cuối
StartReplaceComboMode") vẫn đúng hướng, nhưng cần biết thêm: `FilterByFolderPathWithUI`
(mesh) làm 5 việc (breadcrumb Lvl1, PopulateTreeColumn, CreateChipTagsForPath,
FilterByFolderPath, UpdateFolderHighlights, SetText breadcrumb) — combo hiện chỉ làm 3/6
việc tương đương (SwitchInventoryMode gồm PopulateComboTreeColumn +
UpdateComboFolderHighlights, cộng FilterComboByFolder). Thiếu: chiptag, breadcrumb text.

---

## 4. V0.3 — Auto-update-on-selection trong replace mode

**Giả thuyết plan:** mesh-only, không có nhánh combo. **Kết quả:** ĐÚNG, khớp hoàn toàn.

Hàm thật: `OnMeshSelected(SelectedActor)` — Custom Event nội bộ trong
**`WBP_FurnitureInventory`** (KHÔNG phải `BP_FurnitureInputManager` như dự đoán ban đầu),
trigger qua dispatcher `OnSelectionChangedMaterial`. Doc `WBP_FurnitureInventory.md`
(merge C9.0c + Bug A2 30/07) ghi node flow đầy đủ và đáng tin (đã qua test regression):

```
Nhánh REPLACE trong OnMeshSelected:
Branch(IsReplaceModeActive())
  True →
    Branch(ReplaceTarget == E_ReplaceTarget::Mesh)   ← guard thêm 30/07 (Bug A2 fix)
      True →
        SET MeshesToReplace = InputManager.SelectedActors
        Branch(IsValid(SelectedActor)):
          True → Cast → GET RowName → Branch(RowName != "")
                   True:  DT lookup MeshFolderPath → FilterByFolderPathWithUI(MeshFolderPath)
                   False: fallback DAPath → Load Asset → MeshFolderPath → FilterByFolderPathWithUI
      False ▶→ dead-end — KHÔNG LÀM GÌ CẢ   ← ĐÂY LÀ GỐC BUG #4
  False → (tiếp nhánh Material, không liên quan)
```

**Xác nhận gốc bug #4:** khi `ReplaceTarget == Combo` mà select 1 mesh (hoặc ngược lại),
nhánh `False` của `Branch(ReplaceTarget==Mesh)` dead-end hoàn toàn — không gọi
`ResolveSelectedComboRoot`, không route sang combo. Plan P2 (mục Phase 2 gốc) đã thiết kế
đúng hướng — chỉ cần lấp đúng vào chỗ dead-end này, KHÔNG cần chỉnh hướng thiết kế.

**Lưu ý vị trí:** P2 sẽ sửa trong `WBP_FurnitureInventory.OnMeshSelected`, không phải
`BP_FurnitureInputManager` như dự đoán — cần Opus cập nhật container/Q8 cho đúng file.

---

## 5. V0.4 — BTN_ChangeCombo Visibility (WBP_ComboCard.OnListItemObjectSet)

**Giả thuyết plan:** luôn Visible, không gate theo `ReplaceTarget`. **Kết quả:** ĐÚNG,
còn tệ hơn — không đọc biến nào cả (hardcode).

```
OnListItemObjectSet:
Cast ListItemObject → BP_ComboItemView → SET ComboItem
▶→ Branch(IsValid(InventoryRef)) → (cả 2 nhánh đều dẫn tiếp, không rẽ nhánh thật)
▶→ Branch(IsValid(ComboItem))
     True  ▶→ SetText(TextBlock_ComboName) → SetText(TextBlock_Badge, "×{Count} món")
             → SetVisibility(BTN_ChangeCombo, "Visible")   ← HARDCODE, KHÔNG WIRE GÌ VÀO
             → Combo_Dimensions() → UpdateFavTint() → ...
     False ▶→ PrintString debug (dead-end)
```

`SetVisibility` node có `InVisibility` pin chỉ mang `DefaultValue="Visible"`, **không có
dây nối vào từ bất kỳ biến nào** — nghĩa là hiện tại code chưa từng cố ý đọc `ReplaceTarget`,
không phải đọc sai biến. P3.1 chỉ cần thêm ĐÚNG 1 Branch đọc
`InventoryRef.ReplaceTarget==Combo` trước node `SetVisibility` này. Thiết kế P3.1 trong
plan gốc đúng hướng, không cần chỉnh.

---

## 6. V0.5 — Chiptag builder: xác nhận + GAP KIẾN TRÚC MỚI

### 6.1 Doc-drift xác nhận
Plan gốc ghi tên hàm là `RebuildChipRowForPath` — **SAI**. Tên thật:
**`CreateChipTagsForPath`** (trace K2Node xác nhận, doc `Blueprint_Logic_NodeFlow.md`
cũng ghi sai tên này ở 1 số chỗ dù nội dung node flow đúng — cần sửa tên hàm xuyên suốt
file).

### 6.2 CreateChipTagsForPath (Furniture) — node flow xác nhận
```
ClearChildren(VB_ChipTagArea)
▶→ ForEachLoopWithBreak(ParseIntoArray(ShortPath, "/")):
     CurrentPath = ghép dần
     Branch(CurrentPath == ActiveLevel1Path) → True: skip (dead-end trong Loop Body)
     Branch(Map_Find(FolderTree, CurrentPath).bFound)   ← đọc biến "FolderTree" HARDCODE
       True → CreateWidget ChipRow → ForEach → CreateWidget ChipTag → Bind → AddChild
   Completed ▶→ UpdateFolderHighlights()
```
**Input param:** chỉ `ShortPath : String`. Đọc cứng biến class `FolderTree` (Map của
Furniture) + `ActiveLevel1Path` (breadcrumb state của Furniture).

### 6.3 ⚠️ GAP KIẾN TRÚC — bên Combo KHÔNG có hàm tương đương

Trace `PopulateComboTreeColumn` (đầy đủ, K2Node export 01/08) xác nhận: **không tồn tại
hàm độc lập kiểu "nhận 1 path → dựng chiptag combo"**. Logic dựng chiptag combo nằm
**inline** trong 2 Custom Event khác:

```
OnComboTreeNodeClicked(SelectedPath, IndentLevel):
  ... FilterComboByFolder → Map Find(ComboFolderTree, SelectedPath) → bFound
      True → Create ChipRow → ForEach → Create ChipTag → Bind OnComboChipTagClicked
             → AddChild(VB_ChipTagArea)
      → PopulateComboTreeColumn()   ← LUÔN rebuild lại cả cây, không chỉ chiptag

OnComboChipTagClicked(SelectedPath_ChipTag, IndentLevel_ChipTag):
  ... RemoveChildAt loop (xóa chip cũ) → FilterComboByFolder → Map Find(...) → tương tự
```

→ 2 hàm này làm NHIỀU việc hơn "chỉ dựng chiptag" (kèm filter card, kèm
rebuild toàn bộ tree). **Không thể gọi thẳng như 1 chip-builder gọn** kiểu
`CreateChipTagsForPath(ShortPath)`.

**Việc P1.1 (RebuildChipRowForCurrentContext) cần Opus quyết định 1 trong 3 hướng:**
- (a) Trích xuất phần dựng-chiptag-thuần từ `OnComboTreeNodeClicked` thành hàm mới
  `CreateComboChipTagsForPath(FolderPath)` — song song `CreateChipTagsForPath`, KHÔNG
  đụng 2 event cũ (an toàn, đúng KP3 nhưng thêm code trùng lặp có kiểm soát).
- (b) Gọi thẳng phần liên quan của `OnComboTreeNodeClicked` (rebuild luôn cả tree, hơi
  thừa nhưng không cần code mới).
- (c) Khác — Opus đề xuất.

### 6.4 Bonus — PopulateComboTreeColumn có accordion-gate, doc cũ ghi SAI thành xoè phẳng

```
ForEach lvl1:
  Create FolderNode → RefreshDisplay(bIsActive = CurrentComboFolderPath==lvl1) → AddChild
  → Bind OnNodeSelected + OnNodeRightClicked + OnNodeRenameCommitted
  → Branch( (lvl1==CurrentComboFolderPath) OR StartsWith(CurrentComboFolderPath, lvl1+"/") )
       True  → Branch(Map_Find(ComboFolderTree, lvl1) bFound2)
                True → ForEach lvl2 → Create SubFolderNode → RefreshDisplay(bIsActive=...)
                       → AddChild → Bind 3 delegate
       False → dead-end (lvl1 không active → KHÔNG xoè lvl2)
```
Doc v1.13 (`Blueprint_Logic_NodeFlow.md`) mô tả sai — ghi lvl2 luôn dựng cho mọi lvl1
(chỉ gate `bFound2`). Thực tế cây combo là **accordion** (chỉ xoè nhánh đang active),
không phải xoè phẳng cả 2 cấp cùng lúc như Furniture. Doc cũng thiếu hoàn toàn: node
"+ New" (`then_0`), bind `OnNodeRightClicked`/`OnNodeRenameCommitted` trên cả 4 loại
node, và mọi `RefreshDisplay(bIsActive=...)`.

> **Cập nhật 01/08 (Claude Code):** cả 2 doc-drift (§6.1 tên hàm, §6.4 accordion) đã được patch
> vào `Blueprint_Logic_NodeFlow.md` (v1.14) sau report này — xem changelog file đó. Report giữ
> nguyên văn bản gốc lúc phát hiện, không sửa lại theo trạng thái đã-vá.

---

## 7. CÂU HỎI TREO — cơ chế "minimize" (chặn P3.2)

Đã hỏi cuhoang 2 lần trong phiên, chưa có câu trả lời. `EnterReplaceMode` (đã trace, xem
`WBP_FurnitureInventory.md`) chỉ set Visibility cho `CTV_ComboCard`/`CTV_FurnitureCard`
(card container BÊN TRONG) — **không có node nào set Visibility cho cả cửa sổ chính**.
Vậy chưa rõ:
- Node/hàm nào SET cả cửa sổ inventory thành Collapsed khi "minimize"?
- Chỗ nào (nếu có) SET ngược lại thành Visible?

Nếu không tìm được, P3.2 (#3a) không thể thiết kế đúng — sẽ phải genuine investigate
thêm bằng cách test PIE + Print String tại `SetVisibility` calls liên quan tới widget
gốc `WBP_FurnitureInventory`, thay vì đoán từ K2Node export tĩnh.

---

## 8. ĐỀ XUẤT CHO OPUS

**Phase 0 đã xong 5/5 mục.** P2 và P3.1 xác nhận đúng hướng thiết kế gốc, không cần
chỉnh — chỉ 1 chi tiết cần sửa (P2 nằm trong `WBP_FurnitureInventory`, không phải
`BP_FurnitureInputManager` như dự đoán). Còn lại đúng **2 việc chặn code thật sự**:

1. **P1.1 — chặn bởi gap kiến trúc (mục 6.3).** Bên combo không có hàm chip-builder gọn
   như `CreateChipTagsForPath`. Cần Opus chọn hướng (a) tách hàm mới
   `CreateComboChipTagsForPath` song song, (b) gọi thẳng `OnComboTreeNodeClicked` (nặng
   hơn), hay (c) hướng khác — trước khi viết `RebuildChipRowForCurrentContext`.
2. **P3.2 — chặn bởi câu hỏi treo cơ chế minimize (mục 7).** Không tìm được node nào
   set Collapsed cho cả cửa sổ qua đọc tĩnh K2Node — cần cuhoang xác định qua test
   runtime (Print String tại các `SetVisibility` liên quan widget gốc
   `WBP_FurnitureInventory`) trước khi thiết kế fix #3a.

**Có thể tiến hành ngay, không cần chờ Opus quyết thêm:**
- P1.2 (thêm dòng gọi rebuild vào cuối `StartReplaceComboMode`) — chỉ cần chốt 6.3 trước.
- P2 — thiết kế đã đúng, chỉ sửa đúng file/container (`WBP_FurnitureInventory`).
- P3.1 — thiết kế đã đúng, làm được ngay.
- P4, P5 — không phụ thuộc 2 điểm chặn trên, làm song song nếu Opus duyệt thứ tự.

**Doc cần patch** (2 command block đã soạn trong phiên — `PopulateComboTreeColumn` và
`CreateChipTagsForPath` trong `Blueprint_Logic_NodeFlow.md`) — làm song song, không
chặn code, nhưng nên xong trước Gate 2 review.

**Trạng thái Phase 0: HOÀN TẤT 5/5 mục.** Chỉ còn 2 quyết định kiến trúc/runtime cần Opus
+ cuhoang trước khi an toàn bắt tay P1.1 và P3.2. P1.2, P2, P3.1 có thể làm ngay.

---

## Ghi chú merge (Claude Code, 01/08/2026)

File này giữ NGUYÊN VĂN nội dung gốc (không sửa quyết định/kết luận nào — KP3). Chỉ 2 thay đổi
tổ chức: (1) header "Nguồn plan gốc" cập nhật path trỏ tới v1 đã archive (trước đây trỏ tên file
cũ `01-08-2026_ReplaceUX_Fix_Execution_Plan.md`, nay path đó thuộc bản archived — cập nhật để
không dangling link) + thêm dòng trỏ tới plan canonical hiện hành; (2) 1 ghi chú nhỏ cuối mục 6.4
xác nhận 2 doc-drift đã được patch sau report này (không sửa nội dung mục 6.4 gốc, chỉ thêm ghi
chú trạng thái). Xem `01-08-2026_ReplaceUX_Fix_Execution_Plan.md` (canonical) mục "Ghi chú merge"
cho danh sách đầy đủ điểm cần cuhoang xác nhận khi gộp 3 file.
