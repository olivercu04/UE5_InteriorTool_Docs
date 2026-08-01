# Execution Plan — Replace UX Fix (P0→P5)

**Ngày:** 01/08/2026 | **Từ:** Opus (architect) | **Thực thi:** Sonnet + cuhoang
**Trạng thái:** CANONICAL — bản hiện hành. Thay v1 (nay archived, xem cuối file) — đã tích hợp
Phase 0 Verify Report.
**Nguồn mới:** `01-08-2026_Phase0_Verify_Report_ReplaceUXFix.md` (Sonnet, K2Node export thật) —
giữ nguyên trong `Plans/` làm phụ lục chi tiết, xem mục "Tài liệu liên quan" cuối file.

> **Khác v1 ở đâu** (đọc trước): (1) Phase 0 = DONE, kết quả chốt ở §1. (2) Plan v1 SAI mục
> V0.2 + tên hàm — đã sửa. (3) 2 quyết định kiến trúc Opus chốt: P1.1 hướng (a), P3.2 điều-tra-
> trước. (4) P2 đổi file container. (5) Mảnh mồ côi thứ 6 (breadcrumb combo) — `[CHỜ CUHOANG CHỐT]`.
>
> **Nguyên tắc nguồn:** Phase 0 Report đọc bằng K2Node export thật — **thắng** mọi mô tả as-built
> trong plan. Chỗ nào report khác plan → theo report.

---

## 0. BỐI CẢNH — 2 lớp gốc + bảng bug (phụ lục, copy nguyên văn từ v1, 01/08 theo cuhoang chốt)

> Copy nguyên văn từ v1 (`docs/Archive/01-08-2026_ReplaceUX_Fix_Execution_Plan_v1_SUPERSEDED.md`
> mục "1. BỐI CẢNH") — không đổi nội dung. Cần vì §1-§8 bên dưới chỉ tham chiếu bug bằng số
> (#1, #3a, #3b, #4, #5, #6, P-1→P-5), không tự định nghĩa lại.

FurnitureInventory có **5 mảnh hiển thị**: `tab` · `folder tree` · `chiptag/chiprow` · `card
container (CTV)` · `folder highlight`. Khi context đổi (vào replace / đổi target mesh↔combo /
click tab / click tree / selection đổi), **mọi mảnh tự cập nhật qua đường riêng** → lệch pha.

Đây là cùng con bệnh PROGRESS.md (1 sự thật chép tay nhiều nơi → lệch), lần này ở UI state.

### Lớp A — mảnh UI mồ côi (không nằm chung 1 đường refresh)

**Bằng chứng as-built** — `StartReplaceComboMode` khối cuối:
```
SwitchInventoryMode(Combo)      → tab
FilterComboByFolder(FolderPath) → lọc card
PopulateComboTreeColumn()       → tree
UpdateComboFolderHighlights()   → highlight
RefreshComboCardReplaceMode()   → nút trên card
```
→ **KHÔNG có bước rebuild chiptag/chiprow** (chiptag chỉ dựng bởi `RebuildChipRowForPath`
— *[chú thích 01/08]: tên thật đã xác nhận là `CreateChipTagsForPath`, xem §1 dưới*).

| Bug | Triệu chứng | Mảnh mồ côi |
|---|---|---|
| #3b | combo-replace: tree/card đúng combo, chiptag vẫn Furniture | chiptag |
| #6 | click tab Combo: tab/tree/card đúng, chiptag vẫn Furniture | chiptag |
| #5 | ở tab Combo rồi select mesh: tree/chiptag→mesh, card vẫn ComboCard | card container |

### Lớp B — không đổi loại target giữa chừng replace

**Bug #4:** Đang Replace Mesh, select sang combo (group) → logic auto-update (Sprint 3 fix #9:
"Replace folder auto-update qua OnSelectionChanged") chỉ biết xử **mesh** → đọc mesh primary của
group, KHÔNG chuyển `ReplaceTarget`=Combo + chạy `StartReplaceComboMode`.

### Bug lẻ (không thuộc 2 lớp — hỏng cục bộ)

| Bug | Triệu chứng | Gốc |
|---|---|---|
| #1 | `BTN_ChangeCombo` hiện cả khi chưa vào Replace mode | gate Visibility thiếu/sai điều kiện `ReplaceTarget==Combo` |
| #3a | combo-replace từ minimize: cửa sổ không tự mở lại | `StartReplaceComboMode` thiếu bước đảm-bảo-inventory-mở (nhánh mesh CÓ, xác nhận qua bug #4 mở được) |

### Bug tiềm ẩn Opus đọc code đoán (CHƯA test — PHASE 0/4 verify)

| # | Nghi vấn | Bằng chứng |
|---|---|---|
| P-1 | `ExitReplaceMode` chỉ SET None + Regenerate 2 CTV → KHÔNG dọn chiptag/tab. Thoát combo-replace → chiptag kẹt | ExitReplaceMode v1.3 as-built |
| P-2 | `OnSceneRestored` chỉ xử `Material` mode → undo giữa replace: mode/UI kẹt | OnSceneRestored v1.1 branch |
| P-3 | `ComboRootGroupIDToReplace` không clear ở mọi đường thoát (deselect) | doc C9 §8 tự cảnh báo "mìn" |
| P-4 | `MeshToReplace` (single) dead code còn sống, BTN_Close vẫn SET nó | BTN_Close as-built |
| P-5 | DA legacy `RowNotFound` → chiptag/tree sai khi mở save cũ + replace | Open_Bugs `[OPEN]` |

---

## 1. PHASE 0 — KẾT QUẢ (DONE 5/5, không code lại)

| Mục | Giả thuyết v1 | Kết quả thật | Tác động |
|---|---|---|---|
| V0.1 | combo không rebuild chiptag | ✅ ĐÚNG | gốc #3b xác nhận |
| V0.2 | mesh có khối mở, combo thiếu | ❌ **SAI** — cả 2 mirror giống nhau; combo bỏ qua TOÀN BỘ `EnterReplaceMode→FilterByFolderPathWithUI` (mesh làm 6 việc, combo 3/6) | thiếu **chiptag + breadcrumb** |
| V0.3 | mesh-only, dead-end nhánh combo | ✅ ĐÚNG — dead-end nhánh `False` của `Branch(ReplaceTarget==Mesh)` trong `WBP_FurnitureInventory.OnMeshSelected` | gốc #4; **P2 đổi file** |
| V0.4 | thiếu gate Visibility | ✅ ĐÚNG (tệ hơn) — `SetVisibility(BTN_ChangeCombo,"Visible")` **hardcode, không wire** | P3.1 đúng hướng |
| V0.5 | tên hàm `RebuildChipRowForPath` | ❌ tên thật **`CreateChipTagsForPath`**; combo **KHÔNG CÓ hàm tương đương** (gap §2) | P1.1 cần quyết |

**Doc-drift Sonnet đào ra (patch song song, KHÔNG chặn code):**
- Tên hàm `RebuildChipRowForPath` → `CreateChipTagsForPath` (sửa xuyên `Blueprint_Logic_NodeFlow.md`).
- `PopulateComboTreeColumn` thật là **accordion** (chỉ xoè nhánh active), doc v1.13 ghi sai "xoè phẳng".
- Doc thiếu: node "+ New", bind `OnNodeRightClicked`/`OnNodeRenameCommitted`, các `RefreshDisplay`.

---

## 2. QUYẾT ĐỊNH OPUS #1 — P1.1 gap chip-builder combo — **hướng (a)**

Combo KHÔNG có hàm "nhận path → dựng chiptag" gọn. Logic nằm inline trong `OnComboTreeNodeClicked`
+ `OnComboChipTagClicked` (làm kèm filter card + rebuild cả tree).

**Chốt (a): tách hàm mới `CreateComboChipTagsForPath(FolderPath : String)`** song song
`CreateChipTagsForPath`. (b) gọi thẳng `OnComboTreeNodeClicked` bị LOẠI (rebuild 3 lần/frame + dính
guard `__NEWFOLDER__` + side-effect).

**Ràng buộc bắt buộc:**
- Chỉ tạo hàm MỚI. **KHÔNG đụng** `OnComboTreeNodeClicked`/`OnComboChipTagClicked` (đã test pass —
  KP3, không đụng đường đã chạy).
- Tách theo **logic chiptag combo THẬT** (accordion), KHÔNG copy máy móc `CreateChipTagsForPath`.
- Đọc đúng biến combo: `ComboFolderTree` (Map) + biến breadcrumb combo (`CurrentComboFolderPath`),
  KHÔNG dùng biến furniture (`FolderTree`/`ActiveLevel1Path`).
- **DEVIATIONS (ghi ngay):** code chiptag combo tạm tồn 2 chỗ (hàm mới + inline 2 event).
  Ceiling = logic chip combo ổn định. Trigger dedupe = chip combo đổi lần nữa → lúc đó refactor 2
  event cũ gọi hàm mới.

> **[SUPERSEDED 01/08 — Sonnet export thật]** Quyết định (a) ở trên (viết hàm mới
> `CreateComboChipTagsForPath`) **KHÔNG CẦN THỰC HIỆN**. Export K2Node thật của
> `OnComboTreeNodeClicked` cho thấy nó gọi hàm có sẵn `RebuildChipRowForPath(Path,
> OwnIndentLevel)` — đã đọc đúng `ComboFolderTree`/`CurrentComboFolderPath`, không hardcode
> theo Furniture. Xa hơn: đã có sẵn `RefreshChipBreadcrumb()` (từ 06/07/2026, xem
> `WBP_FurnitureInventory.md` §Bug fix Chip area) — hàm này CHÍNH XÁC là thứ P1.1 định viết
> mới (đi từng cấp `CurrentComboFolderPath`, gọi lặp `RebuildChipRowForPath`). P1.1 rút gọn
> còn: gọi `RefreshChipBreadcrumb()` đúng chỗ + đúng thứ tự (xem P1.2 dưới) — không code mới,
> không phát sinh DEVIATIONS "code tồn 2 chỗ" như dự tính ban đầu.

---

## 3. QUYẾT ĐỊNH OPUS #2 — P3.2 minimize — **ĐIỀU TRA TRƯỚC, cấm code mù**

`EnterReplaceMode` không set Visibility cửa sổ chính (chỉ 2 CTV) → không quyết được bằng đọc tĩnh.

**Bước P3.2-INV (làm trước, không code fix):**
```
Nghịch lý: mesh Mở được từ minimize (bug #4 flow) | combo KHÔNG (#3a) | cả 2 KHÔNG set Visibility cửa sổ
→ khác biệt DUY NHẤT: mesh đi EnterReplaceMode→FilterByFolderPathWithUI ; combo đi SwitchInventoryMode
INV-1: so 2 đường trên (K2Node) → tìm node mesh un-minimize mà combo thiếu
INV-2: nếu INV-1 không ra → PIE + Print String tại mọi SetVisibility liên quan widget gốc
        WBP_FurnitureInventory → bấm minimize → xem node nào fire (tìm cơ chế minimize thật)
```
Có cơ chế rồi mới thiết kế fix #3a (thêm bước un-minimize vào đường combo). **Không đoán.**

> **[DONE 01/08 — INV-1 ra kết quả, không cần INV-2/PIE]** Trace tĩnh K2Node
> `EnsureExpanded()` (hàm có sẵn, gọi từ đầu `EnterReplaceMode` bên nhánh mesh) xác nhận
> đây chính là cơ chế un-minimize toàn cửa sổ (SetVisibility `HB_MainContent`/
> `VerticalBox_0`/`HB_TitleBar`/8 nút resize + SET `bIsMinimized=False` +
> `SetPositionInViewport`). Combo bỏ qua vì không đi qua `EnterReplaceMode` (đã xác nhận
> V0.2). Fix: gọi `EnsureExpanded()` trong `StartReplaceComboMode`. Test T3.3 PASS.

---

## 4. CÁC PHASE (cập nhật theo Phase 0)

### PHASE 1 ⭐ — Gốc lớp A: gom chiptag (+card, +breadcrumb?) về 1 nguồn
Rụng #3b, #5, #6.

**1.1 — `CreateComboChipTagsForPath(FolderPath)`** (mới, WBP_FurnitureInventory) — theo §2.
```
Q8 (Sonnet chạy lại khi có export chi tiết):
Container=Function (no latent) → Local Var OK | IsValid Map lookup an toàn | L2: mọi nhánh
ForEach/Branch có đích, không dead-end nuốt Completed | No Latent | 6A: refresh, đường ngược ở P4
```
Node cho phép: `Clear Children`, `Map Find`, `Create Widget`, `Add Child`, `ForEach` — đều trong bảng.

**1.2 — Gọi refresh chiptag ở đường thiếu:**
- Cuối `StartReplaceComboMode` (sau `PopulateComboTreeColumn`) → `CreateComboChipTagsForPath(FolderPath)` → **fix #3b**
- Đường click tab Combo (handler widget, **KHÔNG** trong `SwitchInventoryMode` — KP3) → **fix #6**

**1.3 — Card container theo mode (fix #5):** khi mode/target đổi, set CTV hiển thị khớp mode (từ V0.3
đường `OnMeshSelected`).

**1.5 — breadcrumb text combo (mảnh mồ côi #6) — CHỐT: task liền kề, có điều kiện verify.**
> Opus chốt (01/08): KHÔNG gộp vào P1 core. Lý do: breadcrumb không nằm trong 6 bug cuhoang báo
> (Sonnet đào ra) → ưu tiên thấp hơn; và chưa verify combo CÓ ô breadcrumb hay không (làm ngay =
> code mù). Cách làm:
> - **P1.5-INV:** verify combo có widget breadcrumb (tương đương mesh) không.
> - Có → làm LIỀN sau P1 core (tay còn ở đúng đường vào combo, khỏi mở lại lần 2): thêm bước set
>   breadcrumb combo cạnh 1.2. Test + tick RIÊNG (không trộn vào T1.1→T1.4).
> - KHÔNG có → bỏ, ghi nhận "combo không breadcrumb by design, không phải bug". Hết.
> - KP2: đây là scope ngoài 6 bug gốc, cuhoang đã duyệt cách xử lý này (01/08).

**Test P1:**
```
T1.1(#3b) combo-replace từ minimize → chiptag HIỆN đúng combo
T1.2(#6)  furniture → click tab Combo → chiptag đổi sang combo
T1.3(#5)  tab Combo → select mesh → card container về CTV_FurnitureCard
T1.4(reg) 3 mode qua lại 5 lần → không mảnh nào kẹt
[nếu 1.4 gộp] T1.5 breadcrumb combo đúng ở mọi đường vào combo
```
**ĐIỂM DỪNG P1** — giá trị cao nhất, hết ngày ở đây vẫn thắng lớn.

---

### PHASE 2 — Lớp B: re-route đổi loại target (fix #4)
Phụ thuộc P1. **File đúng: `WBP_FurnitureInventory.OnMeshSelected`** (không phải InputManager — sửa từ v1).

Gốc xác nhận (V0.3): nhánh `False` của `Branch(ReplaceTarget==Mesh)` **dead-end** (L2 fatal).

**Thiết kế:** đưa `ResolveSelectedComboRoot` LÊN TRƯỚC `Branch(ReplaceTarget==Mesh)`, route theo
(loại selection thật) × (target hiện tại):
```
Q8: Container=Custom Event (OnMeshSelected) → KHÔNG Local Var, dùng class var/param | IsValid
Primary + RootGID → | L2: 4 nhánh đều có đích, lấp dead-end cũ | No Latent | 6A: đổi ngược loại đúng

Branch(IsReplaceModeActive())
  True →
    ResolveSelectedComboRoot() → RootGID, OldComboID, bFound
    Branch(bFound):
      True (combo)  → Branch(ReplaceTarget != Combo) True → StartReplaceComboMode(RootGID,OldComboID)
                                                     False→ refresh theo combo mới
      False (mesh)  → Branch(ReplaceTarget != Mesh)  True → StartReplaceMode(SelectedActors)
                                                     False→ [đường xử mesh CŨ, giữ nguyên]
  False → (Material, giữ nguyên)
```
- ⚠️ **Bước xác nhận trước khi code:** group-select fire event nào? Nếu group vào `OnMeshSelected`
  với primary mesh → thiết kế trên lấp đủ. Nếu group đi đường khác → báo Opus, có thể cần điểm 2.
- KP3: tái dùng `ResolveSelectedComboRoot` + 2 hàm Start có sẵn; giữ đường xử mesh cũ nguyên.
- Guard `!= target hiện tại` chống re-setup lặp mỗi lần select (perf).

**Test P2:** T2.1 mesh→combo chuyển đúng | T2.2 combo→mesh | T2.3 qua lại 3 lần | T2.4 select 2 mesh
cùng loại KHÔNG re-setup thừa.
**ĐIỂM DỪNG P2** — cụm SYNC (A+B) đóng, 4 bug gốc rụng.

---

### PHASE 3 — Bug lẻ
**3.1 (#1)** — thêm `Branch(InventoryRef.ReplaceTarget==Combo)` TRƯỚC node `SetVisibility(BTN_ChangeCombo)`
hardcode (V0.4). Chỉ hiện khi combo-replace. Mirror cách BTN_ChangeMesh gate. Đúng hướng v1.

**3.2 (#3a)** — **P3.2-INV trước** (§3), có cơ chế minimize rồi mới thêm bước un-minimize vào đường
combo.

**Test P3:** T3.1 chưa replace → BTN_ChangeCombo ẩn | T3.2 combo-replace → hiện | T3.3 minimize →
select combo → replace → cửa sổ tự mở *(chỉ khi P3.2-INV xong)*.
**ĐIỂM DỪNG P3.**

---

### PHASE 4 — Đường ngược (6A) + dọn dead code
Giữ nguyên thiết kế v1, xác nhận lại theo Phase 0:

**4.1 (P-1)** ExitReplaceMode dọn chiptag/card về sạch (giờ dùng được `CreateComboChipTagsForPath`).
**4.2 (P-3)** Find References → clear đủ 3 biến (`ReplaceTarget`/`MeshesToReplace`/`ComboRootGroupIDToReplace`)
ở MỌI đường thoát (CB_Replace toggle, deselect OnLMBReleased, BTN_Close, ExitReplaceMode).
**4.3 (P-2)** undo giữa replace — `OnSceneRestored` chỉ xử Material — thêm nhánh Replace.
> **cuhoang chốt tại chỗ:** (a) undo → thoát replace hẳn *(Opus nghiêng, đơn giản)* / (b) giữ mode
> + refresh theo actor restore. Sonnet hỏi trước khi code 4.3.
**4.4 (P-4)** XÓA `MeshToReplace` (single) dead code. Find References → xóa var + node còn lại →
compile toàn bộ → sửa chỗ đỏ. ⚠️ KHÔNG nhầm với `MeshesToReplace` (array, dùng thật).

**Test P4:** T4.1 thoát combo-replace → UI sạch | T4.2 deselect → ComboRoot=="" | T4.3 undo → nhất
quán theo (a)/(b) | T4.4 sau xóa → compile sạch + Replace Mesh vẫn chạy | T4.5 mọi đường thoát clear
đủ 3 biến.
**ĐIỂM DỪNG P4** — đường ngược đóng, mìn dọn.

---

### PHASE 5 — Polish + DA legacy
**5.1 (#2)** chỉ báo Replace mode. KP1 — Opus đề xuất mirror pattern EditMode (`HB_EditModeBar` +
breadcrumb "✏️"): banner/viền + text nút "Đang thay → bấm huỷ" khi `ReplaceTarget != None`. cuhoang
chốt kiểu chỉ báo. R4: clear ref ở Destruct.
**5.2 (P-5)** DA legacy `RowNotFound`. **Cần save cũ thật (RowName="None") → cuhoang chuẩn bị TRƯỚC.**
Không có file → gác, ghi DEVIATIONS, KHÔNG code mù. Fix (nếu tái hiện): normalize path tại
`Split.RightS` trong `FilterByFolderPathWithUI` (phương án đã chốt DEVIATIONS `[CLEANUP]`).

**Test P5:** T5.1 chỉ báo bật/tắt cả 2 nhánh | T5.2 save cũ → replace → tree/chip đúng *(hoặc gác)*.
**ĐIỂM DỪNG P5** — đóng đợt.

---

## 5. NHỊP + ĐIỂM DỪNG (giữ v1)
6 phase + 2 việc thêm ≠ 1 ngày. Mỗi phase 1 điểm dừng độc lập. Thứ tự: P0→P1→P2(cần P1)→P3/P4(đảo
được)→P5. 3-strike → STOP escalate Opus. Gợi ý: Ngày 1 P1, Ngày 2 P2+P3+P4, Ngày 3 P5+regression.

**Làm được NGAY (không chờ Opus thêm):** P1.2, P2 (đúng file), P3.1, P4, P5.
**Có bước verify/chốt riêng:** P1.5 breadcrumb (P1.5-INV verify combo có ô breadcrumb → làm liền
hoặc bỏ), P3.2 (P3.2-INV trước), P4.3 (cuhoang chọn a/b lúc code), P5.2 (cần file save cũ).

## 6. KP3 — KHÔNG ĐƯỢC LÀM (giữ v1)
Không sửa `SwitchInventoryMode`; không refactor mirror `StartReplace*`; không đụng inline
destroy/spawn `F_ExecuteReplace`; không thêm field `FComboData`/`S_GroupData`; không prep Save
As/C11. **Không đụng `OnComboTreeNodeClicked`/`OnComboChipTagClicked`** (thêm ở v2, theo §2 ceiling).

## 7. DEVIATIONS dự kiến
| Lệch | Ceiling | Trigger |
|---|---|---|
| `CreateComboChipTagsForPath` mới, chip combo tồn 2 chỗ (§2) | logic chip combo ổn định | chip combo đổi → refactor 2 event cũ gọi hàm mới |
| `RebuildChipRowForCurrentContext` gom riêng chiptag/card | 3 mode | mode thứ 4 → hàm refresh trung tâm |
| Guard `ReplaceTarget != <loại>` chống re-setup lặp | select-đổi-loại không thường xuyên | thấy giật → debounce |
| Undo-giữa-replace chọn (a) thoát hẳn | UX chấp nhận | user phàn nàn mất mode → làm (b) |

## 8. DOC CẬP NHẬT KHI MERGE (Claude Code, sau đợt)
`WBP_FurnitureInventory.md` (CreateComboChipTagsForPath mới, OnMeshSelected route, ExitReplaceMode
mở rộng) · `BP_FurnitureInputManager.md` (clear ComboRoot mọi đường thoát, XÓA MeshToReplace) ·
`WBP_ComboCard.md` (gate BTN_ChangeCombo) · nơi chứa chỉ báo (#2) · `Blueprint_Logic_NodeFlow.md`
(**patch 3 doc-drift**: tên hàm CreateChipTagsForPath, accordion, node thiếu) · `Open_Bugs.md`
(#1→6 + P-5 → RESOLVED) · `DEVIATIONS.md` (§7) · `01_Session_State.md` + `PROGRESS.md` (đợt DONE →
Save As/Save đè).

## 9. GHI CHÚ HỌC (cuhoang)
Cụm SYNC = **denormalization** — y hệt bug PROGRESS.md: 1 sự thật ("đang xem context nào") nhét vào
nhiều mảnh qua nhiều đường → lệch. Chữa: gom về 1 đường refresh (P1). Phase 0 còn dạy thêm 1 bài:
**tao đọc docs lossy đoán V0.2 sai — Sonnet export thật bắt được.** Đó là lý do mình luôn verify
trước khi code: bên nhìn rõ (K2Node) thắng bên nhìn mờ (search). Giống hệt vụ Claude Code đếm số.

---

## Tài liệu liên quan

- **Phase 0 Verify Report (phụ lục chi tiết, ĐỪNG bỏ):** `01-08-2026_Phase0_Verify_Report_ReplaceUXFix.md`
  (cùng thư mục `Plans/`) — giữ nguyên bằng chứng K2Node trace đầy đủ (V0.1-V0.5), 3 doc-drift,
  gap kiến trúc §6.3, câu hỏi treo minimize §7. Bản plan này (§1) chỉ tóm tắt kết quả; muốn xem
  bằng chứng thật/trace chi tiết → đọc report.
- **v1 (SUPERSEDED, lịch sử):** `docs/Archive/01-08-2026_ReplaceUX_Fix_Execution_Plan_v1_SUPERSEDED.md`
  — giả thuyết ban đầu trước khi Phase 0 chạy, chỉ giá trị lịch sử. Bảng bug gốc của v1 (mục
  "BỐI CẢNH") đã copy nguyên văn vào **§0 của file này** (01/08, theo cuhoang chốt phương án (b)
  ở mục "Ghi chú merge") — không cần mở v1 để tra "bug #X là gì" nữa.

---

## Ghi chú merge (Claude Code, 01/08/2026)

Gộp từ 3 file nguồn (`_v2` xương sống, `_v1` archived, Phase0 Report giữ nguyên) theo yêu cầu
cuhoang. Chỉ sắp xếp/đặt tên/thêm liên kết chéo — **không sửa nội dung quyết định nào** trong cả
3 file gốc (KP3).

**⚠️ Điểm mâu thuẫn/gap phát hiện khi gộp:**

1. **[RESOLVED 01/08]** v1 có bảng "bối cảnh bug" (§1) mà v2/canonical không chép lại — cuhoang
   chốt phương án (b): đã copy nguyên văn toàn bộ mục "1. BỐI CẢNH" của v1 (Lớp A + bảng, Lớp B,
   bảng Bug lẻ, bảng Bug tiềm ẩn P-1→P-5) vào **§0** đầu file này, không đổi nội dung. Bug số nào
   cũng tra được ngay tại đây, không cần mở v1 archived nữa.
2. **[Ghi nhận, không cần sửa]** v1 §3 (rủi ro nhịp) và §4 (KP3) chi tiết hơn v2's "(giữ v1)". v2 tự nhận "giữ v1" ở §5/§6
   nhưng thực tế chỉ chép rút gọn — v1 bản gốc có thêm câu giải thích (vd lý do ngoại lệ dọn
   `MeshToReplace` dead code, cảnh báo cụ thể về "bẫy plan-quá-tham" từ Execution_Discipline).
   Không mất thông tin quyết định (nội dung cốt lõi khớp), chỉ mất phần diễn giải — đánh giá rủi
   ro thấp, không chặn, nhưng ghi lại để cuhoang biết.

Không tự sửa 2 điểm trên — chờ cuhoang chốt hướng ở lượt sau nếu cần.
