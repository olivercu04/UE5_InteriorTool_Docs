# Execution Plan — Replace UX Fix (P0→P5)

> ⚠️ **[SUPERSEDED-by-canonical]** — 01/08/2026 (Claude Code, merge 3-file theo yêu cầu cuhoang).
> Thay bởi `docs/Plans/01-08-2026_ReplaceUX_Fix_Execution_Plan.md` (v2 → nay là bản canonical) —
> Phase 0 (mục PHASE 0 bên dưới) đã DONE 5/5, kết quả khác giả thuyết ở mục V0.2 (xem
> `01-08-2026_Phase0_Verify_Report_ReplaceUXFix.md`). File này KHÔNG xoá — giữ tham chiếu lịch
> sử (pattern giống `WBP_MoveFolderRow.md`), vì mục "1. BỐI CẢNH" bên dưới có 2 bảng (Bug lẻ,
> Bug tiềm ẩn P-1→P-5) liệt kê triệu chứng/bằng chứng gốc cho từng số bug mà bản canonical KHÔNG
> chép lại (chỉ tham chiếu số). Cần tra "bug #X là gì" → đọc file này.
> **KHÔNG dùng file này để lấy hướng thực thi P0-P5** — dùng bản canonical (đã tích hợp Phase 0
> + 2 quyết định kiến trúc Opus chốt sau report).

**Ngày:** 01/08/2026 | **Từ:** Opus (architect) | **Thực thi:** Sonnet (execution) + cuhoang (test/confirm)
**Vị trí trong roadmap:** chèn SAU C9 (Replace DONE 30/07), TRƯỚC Save As/Save đè.
**Nguồn:** phiên test tự do 31/07 (6 bug cuhoang báo) + Opus đọc code as-built (5 bug tiềm ẩn).

> ⚠️ **File này SELF-CONTAINED.** Sonnet không cần đọc lại C9 Execution Plan. Mọi bằng chứng
> as-built cần thiết đã trích vào đây. Nhưng mọi flow trong file là **định hướng do Opus đọc docs
> (lossy, có thể drift)** → PHASE 0 bắt buộc verify bằng K2Node export TRƯỚC khi động dao.

---

## 0. GIỚI HẠN NGUỒN — đọc trước

Opus lập plan này bằng `project_knowledge_search` (lossy) trên docs, KHÔNG phải K2Node export
thật. Docs dự án đã từng drift khỏi code (vụ `BTN_ChangeMesh` v1.1). Vì vậy:

- Mọi "as-built" trích trong file = **giả thuyết cần Sonnet xác nhận ở PHASE 0.**
- Nếu export thật KHÁC mô tả trong plan → Sonnet **STOP, báo Opus** trước khi code (đừng tự sửa
  theo plan sai — bên nhìn rõ thắng bên nhìn mờ).

---

## 1. BỐI CẢNH — 2 lớp gốc, không phải 6 bug rời

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
→ **KHÔNG có bước rebuild chiptag/chiprow** (chiptag chỉ dựng bởi `RebuildChipRowForPath`).

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

## 2. SCOPE (cuhoang chốt 31/07) — FULL

```
✅ P0→P5 (làm hết, gồm cả #2 polish indicator)
✅ Dọn MeshToReplace dead code (P-4) — trong đợt này
✅ DA legacy RowNotFound (P-5) — làm luôn, không dồn C10
```

---

## 3. ⚠️ RỦI RO NHỊP + ĐIỂM DỪNG AN TOÀN (Opus cảnh báo)

**Đây là 6 phase + 2 việc thêm ≠ KHÔNG phải 1 ngày.** Đừng ép xong sạch trong 1 buổi (đúng bẫy
plan-quá-tham mà Execution_Discipline cảnh báo). Cách chống vỡ:

- **Mỗi phase là 1 điểm dừng độc lập** → làm xong phase nào, cái đó tự chạy được, không treo nửa
  vời. Hết giờ ở giữa 2 phase là OK.
- **Thứ tự bắt buộc:** P0 → P1 → P2 (P2 phụ thuộc P1) → P3/P4 (độc lập, đảo được) → P5 (cuối).
- **3-strike:** phase nào fail 3 lần cùng cách → STOP, escalate Opus, KHÔNG thử cách 4.
- Gợi ý nhịp: **Ngày 1** = P0+P1 (gốc lớp A, giá trị cao nhất). **Ngày 2** = P2+P3+P4. **Ngày 3**
  = P5 + regression. Không phải deadline — là nhắc đừng dồn.

---

## 4. KP3 — KHÔNG ĐƯỢC LÀM (surgical only)

- ❌ KHÔNG sửa `SwitchInventoryMode` (hàm dùng chung 3 mode). Giải pháp lớp A phải là **hàm mới bọc
  ngoài**, không đục vào hàm chung.
- ❌ KHÔNG refactor 3 nhánh trùng lặp `StartReplaceMode`/`StartReplaceComboMode` thành helper (đã
  ghi ceiling ở DEVIATIONS C9 — chỉ nâng khi có replace target thứ 3).
- ❌ KHÔNG đụng logic inline destroy/spawn trong `WBP_DragOverlay_FurnitureCard.BTN_ChangeMesh` /
  `F_ExecuteReplace`.
- ❌ KHÔNG thêm field mới vào `FComboData`/`S_GroupData`.
- ❌ KHÔNG chuẩn bị trước gì cho Save As/C11 (KP2).
- ⚠️ Ngoại lệ được duyệt: **dọn `MeshToReplace` dead code** (P-4) — đây KHÔNG phải "tiện tay", là
  việc cuhoang duyệt tường minh 31/07. Rác do chính C9 để lại → dọn (đúng KP3: "rác do mình tạo thì
  dọn").

---

# ═══════════════════════════════════════
# PHASE 0 — VERIFY AS-BUILT (không sửa gì)
# ═══════════════════════════════════════

**Mục tiêu:** xác nhận 5 điểm nghi bằng K2Node export thật. Opus đọc lossy — không tin docs 100%.

Sonnet export + đọc, cuhoang chạy PIE đối chiếu. Xác nhận từng dòng:

```
V0.1  StartReplaceComboMode (BP_FurnitureInputManager) — khối cuối CÓ/KHÔNG gọi rebuild chiptag?
        (giả thuyết: KHÔNG → gốc #3b)
V0.2  Nhánh mesh (StartReplaceMode → EnterReplaceMode) — CÓ bước đảm-bảo-inventory-mở không?
        StartReplaceComboMode — CÓ bước đó không? (giả thuyết: mesh CÓ, combo KHÔNG → gốc #3a)
V0.3  Đường auto-update-on-selection trong replace mode — hàm nào fire? xử mesh-only hay có
        nhánh combo? (giả thuyết: mesh-only → gốc #4)
V0.4  BTN_ChangeCombo (WBP_ComboCard) — binding Visibility đọc gì? có gate ReplaceTarget==Combo
        hay luôn Visible? (giả thuyết: thiếu gate → #1)
V0.5  chiptag/chiprow được dựng bởi hàm nào chính xác (RebuildChipRowForPath?), đọc folder từ
        biến nào (CurrentComboFolderPath?) — cần biết để P1 gọi đúng.
```

**ĐIỂM DỪNG P0:** nếu bất kỳ V0.x KHÁC giả thuyết → STOP, báo Opus. Plan P1→P5 có thể phải chỉnh.
**KHÔNG viết code ở phase này.**

---

# ═══════════════════════════════════════
# PHASE 1 — ⭐ GỐC LỚP A: gom chiptag + card về 1 nguồn
# ═══════════════════════════════════════

Rụng bug #3b, #5, #6.

**Quyết định kiến trúc (Opus):** KHÔNG viết 1 "hàm refresh toàn năng" gom cả 5 mảnh (đụng quá rộng,
chạm SwitchInventoryMode). Thay vào đó gom đúng **2 mảnh mồ côi** vào hàm riêng, mọi đường set
tab/tree gọi chúng:

### 1.1 Function mới: `RebuildChipRowForCurrentContext()` — WBP_FurnitureInventory

```
Q8 (Opus dự thảo — Sonnet Tự chạy lại sau khi có export V0.5):
Container=Function (no latent) → Local Var OK | IsValid không cần (đọc class var String) |
L2: Switch mode mỗi case có đích | No Latent | 6A: N/A (đây là refresh, đường ngược ở P4)
```

Định hướng (chốt tên/pin sau V0.5):
```
Function RebuildChipRowForCurrentContext()
▶→ Switch on CurrentInventoryMode (Furniture/Combo/Material)
     Combo    ▶→ RebuildChipRowForPath(CurrentComboFolderPath, <indent đúng>)
     Furniture▶→ RebuildChipRowForPath(<Furniture folder var>, <indent>)
     Material ▶→ (giữ hành vi hiện tại — không đụng nếu material không có bug)
```
- **L-liên quan:** L2 (Switch mỗi case có đích, không case nào dead-end nuốt logic).
- **Node cho phép:** không dùng node lạ; `RebuildChipRowForPath` là function nội bộ đã có.

### 1.2 Gọi `RebuildChipRowForCurrentContext()` ở mọi đường set tab/tree thiếu chiptag

Từ V0.1 xác nhận → thêm 1 dòng gọi vào cuối:
- `StartReplaceComboMode` khối cuối (sau `PopulateComboTreeColumn`) → **fix #3b**
- Đường click tab Combo (handler tab-switch phía widget, KHÔNG phải trong SwitchInventoryMode) →
  **fix #6**

### 1.3 Card container theo mode (fix #5)

Từ V0.3 — tại đường auto-update-on-selection: khi mode/target đổi, đảm bảo **card container hiển
thị (CTV_FurnitureCard vs CTV_ComboCard)** khớp mode hiện tại. Nếu card container do 1 biến/visibility
điều khiển → set nó cùng chỗ gọi 1.2.

**Test P1 (định nghĩa TRƯỚC khi code):**
```
T1.1 (#3b) combo-replace từ minimize → chiptag/chiprow HIỆN đúng của combo (không phải furniture)
T1.2 (#6)  ở furniture → click tab Combo → chiptag đổi sang combo
T1.3 (#5)  ở tab Combo → select 1 mesh → card container đổi về CTV_FurnitureCard (không kẹt Combo)
T1.4 (regression) 3 mode chuyển qua lại 5 lần → không mảnh nào kẹt
```

**ĐIỂM DỪNG P1:** T1.1→T1.4 PASS. Lớp A đóng. Đây là điểm dừng giá trị cao nhất — hết ngày ở đây
vẫn thắng lớn.

---

# ═══════════════════════════════════════
# PHASE 2 — LỚP B: re-route khi đổi loại target (fix #4)
# ═══════════════════════════════════════

**Phụ thuộc P1** (re-route sẽ gọi lại refresh của P1).

Từ V0.3 — tại đường auto-update-on-selection trong replace mode, thêm bước phân loại selection:

```
Q8 (dự thảo): Container=<theo V0.3> | IsValid Primary/RootGID → | L2: nhánh mesh/combo đều có
đích, merge | No Latent (nếu Event có latent thì tách) | 6A: đổi ngược loại cũng phải đúng
```

Định hướng:
```
— khi selection đổi TRONG replace mode:
▶→ ResolveSelectedComboRoot() → RootGID, OldComboID, bFound      (hàm đã có từ C9)
▶→ Branch(bFound)
     True (là combo)  ▶→ Branch(ReplaceTarget != Combo)
                            True ▶→ StartReplaceComboMode(RootGID, OldComboID)   → chuyển sang combo
                            False▶→ (đã combo → chỉ refresh folder theo combo mới)
     False (là mesh)  ▶→ Branch(ReplaceTarget != Mesh)
                            True ▶→ StartReplaceMode(SelectedActors)             → chuyển sang mesh
                            False▶→ (đã mesh → giữ đường update mesh hiện tại)
```
- **L-liên quan:** L2 (4 nhánh đều có đích); guard `!= target hiện tại` tránh gọi lặp mỗi lần select
  (P5 performance — debounce việc re-setup).
- **KP3:** tái dùng `ResolveSelectedComboRoot` + `StartReplaceMode`/`StartReplaceComboMode` có sẵn,
  KHÔNG viết logic phân loại mới.

**Test P2:**
```
T2.1 (#4) Replace Mesh mode → select sang combo → inventory chuyển combo (tab/tree/chiptag/card đúng)
T2.2      Replace Combo mode → select sang mesh → chuyển mesh đúng
T2.3      select qua lại mesh→combo→mesh 3 lần → mỗi lần đúng, không kẹt
T2.4 (perf) select liên tục 2 mesh cùng loại → KHÔNG re-setup thừa (guard != hoạt động)
```

**ĐIỂM DỪNG P2:** T2.1→T2.4 PASS. Cụm SYNC (lớp A+B) đóng hoàn toàn → 4 bug gốc rụng hết.

---

# ═══════════════════════════════════════
# PHASE 3 — BUG LẺ: #1 + #3a
# ═══════════════════════════════════════

Độc lập, đảo thứ tự với P4 được. Nhỏ, nhanh.

### 3.1 Fix #1 — gate Visibility `BTN_ChangeCombo`

Từ V0.4 — binding Visibility của `BTN_ChangeCombo` (WBP_ComboCard) phải đọc
`ReplaceTarget==Combo` (mirror cách `BTN_ChangeMesh` gate `ReplaceTarget==Mesh`).
- Nếu đang "luôn Visible" hoặc đọc sai biến → sửa binding về đúng gate.
- **L-liên quan:** none đặc biệt; đây là binding function thuần (pure, đọc ReplaceTarget qua
  InputManager ref).

### 3.2 Fix #3a — `StartReplaceComboMode` đảm bảo inventory mở

Từ V0.2 — nhánh mesh có khối "đảm-bảo-inventory-mở" (IsValid InvRef × IsInViewport → Create nếu
đóng). `StartReplaceComboMode` **as-built đã có khối 3 nhánh này** (theo doc C9 §7.2) — nhưng bug
#3a nói cửa sổ KHÔNG mở lại từ minimize.

⚠️ **Phân biệt "minimize" vs "đóng":** #3a nói inventory ở chế độ **minimize** (Visibility Collapsed
nhưng vẫn IsInViewport=True), KHÁC với "đóng" (không in viewport). Khối 3 nhánh hiện chỉ xử
IsInViewport → minimize lọt guard (in viewport = True → không làm gì → không un-collapse).
- Fix: thêm bước **SET Visibility = Visible** (un-minimize) trong nhánh "đã in viewport" của
  `StartReplaceComboMode`. Đối chiếu nhánh mesh xem nó un-minimize bằng node gì (bug #4 xác nhận
  mesh mở được từ minimize → mesh CÓ bước này, combo thiếu).
- **L-liên quan:** L2 (nhánh thêm không được dead-end).

**Test P3:**
```
T3.1 (#1)  chưa vào replace → mở tab Combo → BTN_ChangeCombo KHÔNG hiện trên card
T3.2 (#1)  vào combo-replace → BTN_ChangeCombo HIỆN
T3.3 (#3a) inventory minimize → select combo → chuột phải → replace → cửa sổ Tự mở (un-minimize)
```

**ĐIỂM DỪNG P3:** T3.1→T3.3 PASS.

---

# ═══════════════════════════════════════
# PHASE 4 — ĐƯỜNG NGƯỢC (Luật 6A) + dọn dead code
# ═══════════════════════════════════════

Dọn P-1/P-2/P-3/P-4. Đây là chiều ngược bắt buộc — feature chưa "done" nếu thiếu.

### 4.1 P-1 — `ExitReplaceMode` dọn đủ chiptag/card

Sau khi P1 có `RebuildChipRowForCurrentContext`, `ExitReplaceMode` phải trả UI về trạng thái sạch:
- Hiện tại: SET ReplaceTarget=None + Regenerate 2 CTV.
- Thêm: đảm bảo chiptag/card về đúng mode nền (không kẹt trạng thái replace).

### 4.2 P-3 — clear `ComboRootGroupIDToReplace` mọi đường thoát

Dùng Find References → rà MỌI đường thoát replace (CB_Replace toggle-off, deselect ở
OnLMBReleased, BTN_Close, ExitReplaceMode). Mọi đường phải làm đủ:
```
▶→ SET ReplaceTarget = None
▶→ CLEAR MeshesToReplace
▶→ SET ComboRootGroupIDToReplace = ""
```
(doc C9 §8 đã cảnh báo đây là mìn — giờ đóng.)

### 4.3 P-2 — undo giữa replace

`OnSceneRestored` chỉ xử `Material`. Thêm nhánh: nếu restore khi `ReplaceTarget != None` → sau
restore, đưa UI/mode về trạng thái nhất quán (hoặc thoát replace sạch, hoặc refresh theo selection
mới được restore). **Quyết định UX cần cuhoang chốt tại chỗ:** undo giữa replace nên (a) thoát
replace hẳn, hay (b) giữ replace mode + refresh target theo actor restore? → Opus nghiêng (a) thoát
hẳn (đơn giản, ít mìn). Sonnet hỏi cuhoang trước khi code 4.3.

### 4.4 P-4 — dọn `MeshToReplace` (single) dead code

- Find References `MeshToReplace` → xác nhận CHỈ còn chỗ SET rác (BTN_Close SET None) + khai báo.
- Xóa biến + mọi node SET/GET còn lại. ⚠️ L-gotcha: xóa var UE5 silently remove SET/GET **cùng
  class**, nhưng cross-class ref → hard compile error. Sau xóa, **compile toàn bộ**, sửa chỗ đỏ.
- ⚠️ KHÔNG nhầm với `MeshesToReplace` (array, đang dùng thật) — chỉ xóa bản **single**.

**Test P4:**
```
T4.1 (P-1) combo-replace → thoát (nút Replace toggle-off) → chiptag/tab/card về sạch, không kẹt
T4.2 (P-3) replace → deselect giữa chừng → ComboRootGroupIDToReplace == "" (print verify)
T4.3 (P-2) replace 1 mesh → undo → mode/UI nhất quán (theo (a)/(b) cuhoang chốt)
T4.4 (P-4) sau xóa MeshToReplace → compile sạch 0 error + Replace Mesh vẫn hoạt động (regression)
T4.5 (6A) mọi đường thoát (CB toggle / deselect / BTN_Close) đều clear đủ 3 biến
```

**ĐIỂM DỪNG P4:** T4.1→T4.5 PASS. Đường ngược đóng, mìn dọn sạch.

---

# ═══════════════════════════════════════
# PHASE 5 — POLISH: chỉ báo Replace mode (#2) + DA legacy (P-5)
# ═══════════════════════════════════════

### 5.1 #2 — chỉ báo trực quan "đang ở Replace mode"

Bug #2: không có gì biểu thị đang trong replace. Cần chỉ báo bật/tắt rõ.
- **KP1 — Opus nêu giả định, cuhoang chốt kiểu chỉ báo:** đề xuất 1 banner/viền + đổi text nút
  Replace thành "Đang thay → bấm để huỷ" khi active (mirror cách EditMode có `HB_EditModeBar` +
  breadcrumb "✏️ Đang chỉnh"). Tái dùng pattern EditMode UI cho nhất quán.
- Bind vào đổi trạng thái `ReplaceTarget` (None ↔ Mesh/Combo). Show khi != None, hide khi None.
- **R-liên quan:** R4 (nếu banner giữ ref → clear ở Destruct).

### 5.2 P-5 — DA legacy RowNotFound

Từ Open_Bugs `[OPEN]`: save cũ `RowName=="None"` → đi đường DA → `MeshFolderPath` format có thể
KHÔNG chứa `"Object_Model/"` như DT → `Split` trong `FilterByFolderPathWithUI` cắt sai → tree/chip
sai.
- **Test trước (TDD):** cần 1 **save cũ thật** có actor RowName=="None". cuhoang chuẩn bị file save
  này TRƯỚC. Không có file → không test được → gác lại (đừng code mù).
- Fix (nếu tái hiện): normalize path tại `Split.RightS` trong `FilterByFolderPathWithUI` làm nguồn
  duy nhất (đã chốt phương án ở DEVIATIONS `[CLEANUP]`). Ceiling: prefix `"Object_Model/"` hardcode.

**Test P5:**
```
T5.1 (#2) vào replace → chỉ báo HIỆN; thoát → chỉ báo TẮT; cả 2 nhánh mesh/combo
T5.2 (P-5) mở save cũ (RowName=None) → select → replace → tree/chip đúng, không lệch
           [nếu không có save cũ để test → gác P-5, ghi DEVIATIONS, KHÔNG code mù]
```

**ĐIỂM DỪNG P5:** đóng đợt. Chạy regression Replace end-to-end.

---

## 5. REGRESSION cuối đợt (trước khi tick done)

```
R1  Replace Mesh multi (select similar → replace) → vẫn đúng như C9
R2  Replace Combo → vẫn đúng như C9 (30/07 test pass)
R3  Undo/redo sau mọi loại replace
R4  Save → Load scene sau replace → trạng thái đúng
R5  5 mảnh UI đồng bộ ở MỌI đường (tab/tree/select/replace-in/replace-out)
```

---

## 6. DEVIATIONS dự kiến (ghi khi lệch)

| Lệch có thể xảy ra | Ceiling | Trigger nâng cấp |
|---|---|---|
| `RebuildChipRowForCurrentContext` là hàm gom riêng, không gom toàn bộ 5 mảnh | 3 mode hiện tại | Thêm mode thứ 4 → cân nhắc hàm refresh trung tâm thật |
| Guard `ReplaceTarget != <loại>` chống re-setup lặp (P2) | select-đổi-loại không thường xuyên | Thấy giật khi select nhanh → debounce |
| Undo-giữa-replace chọn (a) thoát hẳn | UX chấp nhận thoát | User phàn nàn mất mode sau undo → làm (b) giữ mode |

---

## 7. DOC CẬP NHẬT KHI MERGE (Claude Code, sau khi đợt xong)

- `Widgets/WBP_FurnitureInventory.md` — `RebuildChipRowForCurrentContext` (mới), ExitReplaceMode
  mở rộng, card container theo mode.
- `Blueprints/BP_FurnitureInputManager.md` — re-route on-selection (P2), clear ComboRoot mọi đường
  thoát (P3), XÓA `MeshToReplace` (P4).
- `Widgets/WBP_ComboCard.md` — gate Visibility BTN_ChangeCombo (P3.1).
- `Widgets/WBP_MeshControls.md` (hoặc nơi chứa chỉ báo) — indicator Replace mode (P5.1).
- `Bugs/Open_Bugs.md` — #1→#6 → RESOLVED; P-5 DA legacy → RESOLVED hoặc cập nhật ceiling.
- `00_Core/DEVIATIONS.md` — mục §6.
- `00_Core/01_Session_State.md` + `PROGRESS.md` — đợt Replace UX Fix DONE, tiếp theo Save As/Save đè.

---

## 8. GHI CHÚ HỌC (cuhoang)

Cụm SYNC (#3b/4/5/6) = **denormalization** — y hệt bug PROGRESS.md hôm nay: 1 sự thật ("đang xem
context nào") nhét vào nhiều mảnh qua nhiều đường, không nguồn gốc chung → lệch. Cách chữa cùng
kiểu: **gom về 1 đường refresh** (P1). Khác chỗ: doc thì gom số về checklist, UI thì gom chiptag/card
về 1 hàm. Cùng nguyên lý "1 nguồn sự thật".
