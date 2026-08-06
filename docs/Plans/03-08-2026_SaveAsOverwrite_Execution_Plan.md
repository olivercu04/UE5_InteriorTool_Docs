# Kế hoạch Save As / Save đè combo — Execution Plan

**Phiên bản:** 1.6 — 04/08/2026 (xem mục 9 — lịch sử cập nhật)
**Tác giả:** Opus (phiên lập kế hoạch 03/08/2026)
**Sprint:** 5 (Combo Mesh) — hạng mục kế tiếp sau C9 Replace Combo
**Vị trí trong hàng đợi:** **Save As/Save đè → C11 → C10 → Gate 2**
**Thay thế:** khung sơ bộ "C9.5" trong `Sprints/Sprint5/Combo_Execution.md` (UX chưa chốt) — mục
đó nay là `[HISTORICAL]`, nội dung chốt nằm ở file này.

---

## 0. FILE NÀY DÙNG THẾ NÀO

| Câu hỏi | Trả lời |
|---|---|
| Kế hoạch tổng thể nằm ở đâu | Mục 3 (khung 5 task) — file này |
| Task nào đã có kế hoạch chi tiết | **Chỉ T1** (mục 6) |
| Task sau lấy gì từ task trước | Mục 4 (bảng phụ thuộc) |
| Khi nào lên kế hoạch task sau | Mục 5 (Điều kiện mở task) |
| Task card chi tiết task sau ghi vào đâu | Mục 7 |
| Kết quả thực thi ghi vào đâu | Mục 7 |

> ⚠️ File này là **PLAN**, không phải as-built. Kết quả test / K2Node export / đính chính
> **KHÔNG** được ghi thẳng vào đây (luật `R-DOC-ASBUILT`). Nếu buộc phải ghi tạm → đóng banner
> `📌 [CHỨA AS-BUILT]` ngay lúc ghi.

---

## 1. ĐỊNH NGHĨA TÍNH NĂNG

User spawn combo có sẵn từ thư viện vào scene → chỉnh sửa (đổi vị trí món, thêm/bớt món, replace
mesh bên trong) → bấm Save Combo → chọn **ghi đè lên combo gốc** (giữ nguyên `comboId`) hoặc
**lưu thành combo mới** (sinh `comboId` mới).

Mô hình tham chiếu: **Save / Save As của phần mềm desktop** (Word, Photoshop). Không phát minh
khái niệm mới — user đã biết sẵn.

---

## 2. QUYẾT ĐỊNH ĐÃ CHỐT (phiên 03/08/2026 — KHÔNG bàn lại)

### 2.1 Kết quả test lớp dữ liệu — GroupID sống sót qua Replace ✅

Test tay 03/08/2026 (cuhoang thực hiện trong PIE):

```
1. Select 1 mesh trong group lồng 3 tầng (Group 1 > Group 2 > Group 3)
2. BTN_Replace trên WBP_MeshControls → inventory nhảy ĐÚNG folder mesh đang chọn
3. BTN_ChangeMesh trên FurnitureCard → mesh mới thay mesh cũ
4. Thoát edit mode → click vào cụm
→ KẾT QUẢ: chọn được toàn bộ cụm, CẢ món vừa replace
```

**Kết luận:** `F_ExecuteReplace` giữ ĐÚNG `GroupID` kể cả với group lồng nhiều tầng. Save đè
**không cần thiết kế đặc biệt** cho case "combo đã bị replace bên trong" — cứ đọc `GroupID` hiện
tại của actor là đủ.

### 2.2 UX — 2 nút, trạng thái quyết định nút nào sống

Đặt **trong `WBP_SaveComboDialog`** (không tạo widget hỏi-trước riêng):

```
Bấm Save Combo → dialog mở như cũ, field auto-fill theo combo gốc
    [ Ghi đè "<tên combo>" ]      → có bước xác nhận, KHÔNG hoàn tác được
    [ Lưu thành combo mới… ]      → luôn sống, mọi trạng thái
```

Bảng trạng thái nút **Ghi đè** (nút Lưu-mới LUÔN sống, không phụ thuộc bảng này):

| Selection | Ghi đè | Lý do |
|---|---|---|
| Đúng 1 combo root (± mesh rời kèm) | ✅ sống | Rõ đang ở "tài liệu" nào; mesh rời = thêm món vào combo đó |
| 0 combo root | ⬛ xám | Chưa có combo nào được chọn |
| ≥2 combo root | ⬛ xám | Từ chối đoán hộ user đè lên combo nào |
| Đang trong edit mode | ⬛ xám | Chống mất dữ liệu — xem 2.3 |

Nút xám **bắt buộc có tooltip nêu lý do**. Xám ở đây là "từ chối đoán", KHÔNG phải "cấm".

### 2.3 Vì sao chặn Save đè khi đang edit mode

Đang edit trong combo A, chọn 1 cái ghế, bấm Ghi đè → combo A trên đĩa bị ghi lại **chỉ còn 1 cái
ghế**. Mất dữ liệu âm thầm, `BP_UndoManager` không quản file trên đĩa → Ctrl+Z không cứu.

Muốn sửa nội dung combo: thoát edit mode → chọn cả cụm → ghi đè.

### 2.4 Sinh ID

- **Save As** → LUÔN sinh `comboId` mới (`combo_` + NewGuid). Đóng luôn `Note-DuplicateComboID`
  (`Bugs/Open_Bugs.md`).
- **Save đè** → giữ nguyên `comboId` cũ, chỉ cập nhật items + kích thước + thời gian + thumbnail.

### 2.5 Xác nhận trước khi ghi đè — hiện số món

```
Ghi đè "Sofa góc L"?
Nội dung mới: 12 món  (bản cũ: 7 món)
```

Số món là thứ duy nhất bảo vệ user khỏi bấm nhầm ở case "combo + mesh rời". Đếm bằng
`ForEach + IsValid`, **KHÔNG** dùng thẳng `Array Length(SelectedActors)` (mảng có thể chứa `None`
sau RestoreSnapshot/replace/delete).

Không cần lọc pivot/container: `GizmoPivotActor` là biến riêng, chưa bao giờ được ADD vào
`SelectedActors`; container không phải `BP_FurnitureActor` nên không lọt vào mảng theo kiểu dữ
liệu. → **Đúng là: không lọc, và KHÔNG cần lọc.**

### 2.6 Ghi đè xong phải chụp lại thumbnail

Nội dung đổi thì ảnh card phải đổi. Tái dùng `CaptureComboThumbnail` (P1/P2).

### 2.7 Giới hạn phải nói rõ với user

Ghi đè combo trong thư viện **KHÔNG** cập nhật các cụm đã spawn sẵn trong scene — chúng là actor
thật, không phải link tới file. Tính năng "cập nhật tất cả bản đã spawn" là feature riêng, KHÔNG
nhét vào đợt này.

### 2.8 Đóng `[DOC-DRIFT] ResolveSelectedComboRoot` — không dùng biến nào trong 2 biến đang tranh cãi

`DEVIATIONS.md` 02/08 treo câu hỏi: Save đè căn theo `PrimarySelectedActor` hay
`SelectedActors[0]`?

**Chốt: cả hai đều SAI cho Save As/Save đè.** Cả hai đều lấy MỘT actor rồi leo lên → kết quả phụ
thuộc thứ tự Ctrl-click của user; cùng một selection, click khác thứ tự ra kết quả khác. Không
giải thích được cho user, không test ổn định.

→ Save As/Save đè dùng hàm MỚI **quét toàn bộ `SelectedActors`**, đếm số combo root khác nhau
(mục 6). `ResolveSelectedComboRoot()` **giữ nguyên**, không sửa (KP3 — C9 vừa test xong 30/07,
đụng vào là kéo regression Replace).

**Ceiling / Trigger** (ghi `DEVIATIONS.md`):
```
[CEILING]  T1 để ResolveSelectedComboRoot giữ chain riêng, chưa gọi GetGroupRootOfActor
           → 2 nơi cùng biết cách leo combo root.
[TRIGGER]  C10 (regression full) — đấu lại + chạy 5 case C9 (bộ test đã bật sẵn, chi phí
           thêm ~0). Hoặc sớm hơn nếu có BẤT KỲ thay đổi nào về cách xác định combo root.
```

### 2.9 Bug UX gộp vào đợt này (không sửa riêng)

**Triệu chứng** (test 03/08): replace 1 mesh bên trong combo → xong thì cửa sổ inventory tự nhảy
sang **tab Combo** (foldertree/chiprow/chiptag/CTV_ComboCard đổi theo combo), trong khi breadcrumb
vẫn đứng ở path folder mesh.

**Chuỗi gây ra** (suy từ doc, CHƯA verify bằng Print):
```
F_ExecuteReplace (Completed)
  ▶→ DeselectAll        → Broadcast OnSelectionChanged(rỗng, None)
                          → OnMeshSelected → Branch(IsValid) False → dead-end (guard 02/08) →
  ▶→ SelectActors(mesh mới) → Broadcast OnSelectionChanged(mesh mới)
                          → WBP_FurnitureInventory.OnSelectionChangedMaterial
                          → OnMeshSelected
                          → IsReplaceModeActive() = True
                          → ResolveSelectedComboRoot() → bFound = TRUE
                          → StartReplaceComboMode()   → NHẢY TAB COMBO
```

**Giả thuyết gốc rễ:** `ResolveSelectedComboRoot()` **mù edit mode** — luôn `GetGroupRoot` leo tận
combo root, không nhận `EditScope`. So sánh với `ResolveSelectionUnit(Actor, EditScope)` (Sprint 4)
vốn CÓ nhận edit scope và trả về chính món đó khi đang edit.

→ Đây KHÔNG phải bug của re-route (P2 làm ĐÚNG theo dữ liệu nó nhận) mà là bug của **dữ liệu đầu
vào**.

**Hướng fix (T2, chưa chốt cho tới khi verify):** guard tại call site trong `OnMeshSelected` —
`GetCurrentEditScope() != ""` → ép đi nhánh mesh, không gọi resolve combo. KHÔNG sửa
`ResolveSelectedComboRoot`.

**Điểm chưa khớp, phải verify bằng Print ở T2, KHÔNG kết luận vội:**
`StartReplaceComboMode` CÓ gọi `RefreshChipBreadcrumb()` (fix #3b, 01/08) — vậy mà breadcrumb quan
sát được vẫn đứng ở path mesh. Hoặc hàm đó không đổi breadcrumb thật, hoặc bị ghi đè sau.

---

## 3. KHUNG TỔNG THỂ — 5 TASK

| # | Nhiệm vụ | Đụng gì | Định nghĩa XONG |
|---|---|---|---|
| **T1** | `ResolveActiveComboForSave()` — đọc trạng thái | `BP_FurnitureInputManager` (2 Function mới) | Print đúng 6 case, chưa có UI |
| **T2** | Guard edit-scope cho re-route replace (bug 2.9) | `WBP_FurnitureInventory.OnMeshSelected` | Replace mesh trong combo → inventory ở nguyên tab mesh |
| **T3** | 2 nút + trạng thái xám + tooltip + auto-fill | `WBP_SaveComboDialog` | Bấm nút chỉ Print, chưa ghi file |
| **T4** | Ghi đè thật + xác nhận + chụp lại thumbnail | C++ `ComboSerializer` + `BP_ComboManager` | File `.json` đổi nội dung, `comboId` giữ nguyên |
| **T5** | Regression + docs | — | Save As vẫn sinh ID mới; combo cũ load được; docs cập nhật |

> **Ghi chú scope T3 (thêm 04/08/2026, xem mục 7b):** cột "Đụng gì" ở trên chỉ ghi
> `WBP_SaveComboDialog`, nhưng scope thật rộng hơn — T3 đụng **3 asset**: `WBP_SaveComboDialog`
> (UI) + `WBP_FurnitureInventory` (2 Function mới + `OpenSaveComboDialog` mở rộng) +
> `BP_FurnitureInputManager` (1 node chèn vào `CB_SaveCombo_Handler`). Auto-fill không sống
> trong dialog được vì dialog không giữ `AllComboViews_Combo` — plumbing bắt buộc, không phải
> feature thêm (KP2, đã trình cuhoang duyệt).

**Xương sống: T1 → T3 → T4.** T1 trả lời "đang ở cửa sổ nào", T3 hỏi user "muốn gì", T4 thi hành.

**T2 chen giữa** vì: cùng vùng code, nhỏ (1 Branch), và làm sớm thì lúc test T3/T4 không bỏ nhiều
bởi cửa sổ tự nhảy tab.

**T4 đứng cuối xương sống** vì nó là chỗ dễ chết nhất (ghi đè file thật, không có undo). Lúc chạm
vào, T1/T3 đã chốt đúng trạng thái và đúng ý user — không phải vừa mò logic vừa nghịch file trên
đĩa.

---

## 4. PHỤ THUỘC — TASK SAU CẦN GÌ Ở TASK TRƯỚC

```
T1 ───┬───► T3 ───► T4 ───► T5
      │         ▲
T2 ───┴─────────┘
```

| Task | Cần gì từ trước | Vì sao |
|---|---|---|
| **T1** | (không) | Thuần đọc, không phụ thuộc gì. Đã đóng T0 (`GetGroupRoot` verified 03/08) |
| **T2** | (không) — độc lập T1 | Chạm `WBP_FurnitureInventory`, không chạm 2 hàm mới |
| **T3** | `ResolveActiveComboForSave()` chạy đúng + **văn bản `ReasonText` thật** đã thấy qua Print | Tooltip nút xám lấy nguyên văn `ReasonText`. Viết T3 trước = viết mù |
| **T3** | T2 xong | Tránh nhiễu: tab tự nhảy làm khó phân biệt lỗi UI của T3 |
| **T4** | T3 xong: biết chính xác user bấm nút nào, dialog trả về gì | Ghi file phải biết ghi cái gì, đè lên ID nào |
| **T4** | Tên combo tra được qua `BP_ComboManager` | T1 KHÔNG trả tên (xem 6.4) |
| **T5** | T1→T4 xong | Regression cần đủ đường để chạy |

### 4.1 — Quyết định kiến trúc cho T4 (chốt 04/08/2026, verify Lô A — CHƯA thực thi)

> Nguồn: `DELTA_04-08-2026_LoA_SaveCombo_Verify.md` mục B.2. Đây là **quyết định kiến trúc**,
> KHÔNG phải task card — chưa viết node, chưa test. Task card T4 thật sẽ mở sau khi T3 đóng
> (mục 5, luật "mỗi lần chỉ mở 1 task").

Verify Lô A xác nhận (`Data/ComboSerializer_Reference.md`): `UComboSerializer` **không có**
primitive C++ "ghi đè combo" (không có `SaveCombo(ComboID, Data)`/`OverwriteCombo`;
`UpdateComboFolder` chỉ sửa 1 field). Ghi đè cả struct phải ghép ở tầng BP:
`ComboToJson` → `SaveStringToFile` — đúng cặp hàm `SaveComboFromSelection` đã dùng sẵn.

**Quyết định:** nối `SaveComboFromSelection` (`BP_ComboManager`) bằng 1 Branch tại đúng điểm sinh
`ComboID` (Bước 5a, xem `Blueprints/BP_ComboManager.md` v1.15) — **KHÔNG** viết primitive C++ mới:

```
Thêm 2 param: bOverwrite (Bool, default false) · OverwriteComboID (String, default "")

Tại Bước 5a, thay node SET đơn bằng:
  Branch(bOverwrite)
    True  ▶→ SET SaveCombo_ComboID = OverwriteComboID       ← nhánh MỚI
    False ▶→ SET SaveCombo_ComboID = "combo_" + NewGuid()   ← node CŨ, giữ nguyên
```

Caller cũ truyền `bOverwrite=false` → hành vi không đổi (additive, không phá C3b/C9).

**Vì sao chọn Branch tại chỗ thay vì hàm C++ mới:** điểm sinh `ComboID` là **chốt duy nhất**
mọi thứ phía sau khóa theo (path `.json`, thumbnail) — xem ghi chú Bước 5a trong
`BP_ComboManager.md`. Thêm Branch ở đây là surgical nhất; viết primitive C++ mới phải đụng
`.h`/`.cpp` + rebuild plugin, rủi ro cao hơn cho lợi ích tương đương.

---

## 5. KHI NÀO LÊN KẾ HOẠCH TASK SAU

**Luật:** mỗi lần chỉ mở kế hoạch chi tiết cho **1 task**.

Điều kiện mở task kế tiếp — phải đủ **cả 3**:
1. Task hiện tại test **PASS** đủ số case ghi trong task card.
2. cuhoang trả lời xong **câu kiểm tra hiểu bài** của task đó (mục DẠY).
3. Kết quả + deviation của task hiện tại đã ghi vào doc (mục 7).

**Trước khi viết task card mới, bắt buộc chạy T0 của chính task đó:** liệt kê mọi hàm/biến task
mới **dựa vào**, kèm dấu nguồn tin cậy. Còn ô `⚠ DOC-ONLY` mà thiết kế đè lên nó → cuhoang export
K2Node đoạn đó (5–15 node) trước, rồi mới viết tiếp.

**Ngoại lệ được phép gộp:** nếu T1 xong mà T2 đúng y giả thuyết ở 2.9 (1 Branch, không bất ngờ) →
gộp card T2+T3 làm một, ghi lý do gộp vào `DEVIATIONS.md`.

---

## 6. TASK CARD T1 — `ResolveActiveComboForSave()`

**Người chạy:** Sonnet | **Phạm vi:** `BP_FurnitureInputManager`, 2 Function mới
**KHÔNG** đụng UI, **KHÔNG** ghi file, **KHÔNG** CaptureSnapshot.

### 6.0 T0 — Bảng dấu nguồn tin cậy (đã đóng 03/08)

| Dựa vào | Dấu |
|---|---|
| `GetGroupRoot` | ✅K2 03/08/2026 |
| `FindGroupData` | ✅K2 24/07/2026 |
| `S_GroupData.SourceComboID` | ✅K2 24/07/2026 |
| `GetCurrentEditScope` | ✅K2 24/07/2026 |
| `SelectedActors` không chứa pivot/container | ✅ suy từ kiểu dữ liệu + tag |

Không còn ô `⚠` — được phép viết node.

#### Ghi chú as-built `GetGroupRoot` (K2Node export 03/08/2026) — 3 điều doc chưa từng ghi

```
Local: Current (String)
Entry ▶→ SET Current = InGroupID
      ▶→ ForLoop (FirstIndex=0, LastIndex=9)        → cap 10 vòng
           LoopBody ▶→ FindGroupData(Current) ─→ GroupData, bFound
                    ▶→ Branch(bFound == false)
                         True  ▶→ Return Current
                         False ▶→ Branch(ParentGroupID == "")
                                    True  ▶→ Return Current      → đã là root
                                    False ▶→ SET Current = ParentGroupID
                                             (then bỏ trống → hợp lệ, ForLoop tự chạy vòng sau)
           Completed ▶→ Return Current                            → hết 10 vòng chưa tới root
```

1. **Cap 10 tầng, không phải đệ quy.** Vượt 10 tầng lồng → trả về nửa chừng, KHÔNG báo lỗi.
2. **Không tìm thấy group → trả lại CHÍNH GID truyền vào, KHÔNG trả `""`.** ⚠ Chuỗi khác rỗng
   ở đây KHÔNG chứng minh group tồn tại.
3. **Vòng lặp cha-con quẩn (A→B→A) không bị phát hiện** — chỉ bị cap 10 chặn rồi trả kết quả sai.

Cả 3 **không chặn T1**, hàm dùng được. Ghi lại làm hiện trạng, KHÔNG sửa (KP3).

### 6.1 Q9 — TẦNG 1: S-SCAN

| ID | Trạng thái | Kết quả |
|---|---|---|
| S0 | Không chọn gì | `bCanOverwrite=false`, lý do "Chưa chọn gì" |
| S1 | 1 mesh rời | 0 combo root → false |
| S2 | N mesh rời | `≡S1` |
| S3 | 1 group thường | `SourceComboID==""` → không tính là combo root → `≡S1` |
| S4 | 1 combo cả cụm | **1 combo root → `bCanOverwrite=true`** — đường chính |
| S5 | 1 mesh trong group thường (edit) | `N/A: chặn bằng guard EditScope` |
| S6 | 1 mesh trong combo (edit) | `N/A: chặn bằng guard EditScope` — ⚠ ca mất dữ liệu nguy hiểm nhất |
| S7 | Sub-group nested (đang edit) | `N/A: chặn bằng guard EditScope` |
| S8 | Mix (combo + mesh rời) | `⚠` Đếm số combo root: ==1 → cho; ≥2 → chặn kèm lý do |
| S9 | Selection do máy sinh | `⚠` `SelectedActors` có thể chứa `None` — IsValid từng phần tử |

### 6.2 Q9 — TẦNG 2: X-CHECK (chạy cho ô `⚠` + ô `N/A`)

| # | Hệ thống | Kết luận |
|---|---|---|
| X1 | Undo | **Không** CaptureSnapshot — hàm thuần đọc |
| X2 | Persistence (4 kho) | **Không ghi kho nào** |
| X3 | Inventory UI | Không đụng |
| X4 | Selection sau action | Không đổi |
| X5 | Gizmo / Pivot | Không đụng |
| X6 | Group data | Chỉ ĐỌC `Groups` |
| X7 | Toast | Không (T3 lo phần hiển thị) |
| X8 | EditModeStack | **Đọc** — là điều kiện chặn của S5/S6/S7 |
| X9 | Material state | N/A |
| X10 | Placement & Anchor | N/A |

> T1 không ghi vào đâu cả → X1/X2 sạch. Đây là lý do T1 đứng đầu: rủi ro gần bằng 0.

### 6.3 Hàm 1 — `GetComboRootOfActor(Actor : BP_FurnitureActor)`

**Outputs:** `RootGroupID : String` · `ComboID : String` · `bFound : Bool`
**Local:** `GCR_GID`, `GCR_RootGID`, `GCR_SCID` (String) · `GCR_Data` (S_GroupData) ·
`GCR_bDataFound` (Bool)

```
Q8: Container=Function (Local Var OK, no latent) | IsValid(Actor) đầu hàm ✓ |
L2: 5 nhánh đều chạm Return Node (L12) ✓ | No latent ✓ | 6A: hàm thuần đọc, không có đường ngược ✓
```

```
Entry
▶→ Branch(IsValid(Actor))
     False ▶→ Return ["", "", false]                     → ref chết (S9)
     True  ▶→ GET Actor.GroupID ─→ SET GCR_GID
▶→ Branch(GCR_GID == "")
     True  ▶→ Return ["", "", false]                     → đồ rời
     False ▶→ GetGroupRoot(GCR_GID) ─→ SET GCR_RootGID
▶→ FindGroupData(GCR_RootGID)
     ─→ GroupData ▶→ SET GCR_Data
     ─→ bFound    ▶→ SET GCR_bDataFound
▶→ Branch(GCR_bDataFound == false)
     True  ▶→ Return ["", "", false]                     → ⚠ BẮT BUỘC, xem dưới
     False ▶→ Break GCR_Data ─→ SourceComboID ▶→ SET GCR_SCID
▶→ Branch(GCR_SCID == "")
     True  ▶→ Return ["", "", false]                     → group thường, không phải combo
     False ▶→ Return [GCR_RootGID, GCR_SCID, true]
```

⚠️ **KHÔNG được bỏ bước `FindGroupData` sau `GetGroupRoot`** — xem 6.0 điểm 2. `GetGroupRoot` khi
không tìm thấy group trả lại chính GID truyền vào; chuỗi khác rỗng KHÔNG chứng minh group tồn tại.

### 6.4 Hàm 2 — `ResolveActiveComboForSave()`

**Outputs:** `ComboID : String` · `RootGroupID : String` · `ItemCount : Int` ·
`bCanOverwrite : Bool` · `ReasonText : String`

**Local:** `ResolveSave_ActorsCopy` (Array BP_FurnitureActor) · `ResolveSave_Roots`,
`ResolveSave_ComboIDs` (Array String) · `ResolveSave_Count` (Int) · `ResolveSave_Scope`,
`ResolveSave_Root`, `ResolveSave_CID` (String) · `ResolveSave_bFound` (Bool)

> Đặt tên theo quy ước Sprint 5: biến tạm phục vụ 1 function → prefix tên function
> (`ResolveSave_`).

```
Q8: Container=Function (Local Var OK, no latent) | IsValid từng Actor trong loop ✓ |
L2: mọi nhánh chạm Return; dead-end trong Loop Body hợp lệ (macro tự chạy vòng sau) ✓ |
No latent ✓ | 6A: thuần đọc ✓
```

```
Entry
▶→ CLEAR ResolveSave_Roots · CLEAR ResolveSave_ComboIDs · SET ResolveSave_Count = 0
▶→ GetCurrentEditScope() ─→ SET ResolveSave_Scope
▶→ Branch(ResolveSave_Scope != "")
     True  ▶→ Return ["", "", 0, false,
                      "Đang sửa bên trong nhóm — thoát nhóm rồi mới ghi đè được"]
     False ▶→ SET ResolveSave_ActorsCopy = SelectedActors    → pass-by-ref, copy trước khi lặp

▶→ ForEach ResolveSave_ActorsCopy (Actor)
     Loop Body:
       Branch(IsValid(Actor))
         False ▶→ (để trống — bỏ qua ref chết)
         True  ▶→ SET ResolveSave_Count = ResolveSave_Count + 1
                ▶→ GetComboRootOfActor(Actor)
                     ─→ RootGroupID ▶→ SET ResolveSave_Root
                     ─→ ComboID     ▶→ SET ResolveSave_CID
                     ─→ bFound      ▶→ SET ResolveSave_bFound
                ▶→ Branch(ResolveSave_bFound)
                     False ▶→ (để trống)
                     True  ▶→ Branch(NOT Contains(ResolveSave_Roots, ResolveSave_Root))
                                True  ▶→ ADD ResolveSave_Root → ResolveSave_Roots
                                       ▶→ ADD ResolveSave_CID  → ResolveSave_ComboIDs
                                False ▶→ (để trống — root đã có, không đếm 2 lần)

     Completed:
▶→ Branch(ResolveSave_Count == 0)
     True  ▶→ Return ["", "", 0, false, "Chưa chọn gì"]
     False ▶→ Branch(Array Length(ResolveSave_Roots) == 1)
                True  ▶→ Return [ResolveSave_ComboIDs[0], ResolveSave_Roots[0],
                                 ResolveSave_Count, true, ""]
                False ▶→ Branch(Array Length(ResolveSave_Roots) == 0)
                           True  ▶→ Return ["", "", ResolveSave_Count, false,
                                    "Chưa chọn combo nào có sẵn — chỉ lưu được thành combo mới"]
                           False ▶→ Return ["", "", ResolveSave_Count, false,
                                    "Đang chọn nhiều combo — chỉ lưu được thành combo mới"]
```

**Vì sao KHÔNG trả tên combo:** tên hiển thị nằm trong file `.json`, không nằm trong `S_GroupData`.
`GroupName` của group cha CÓ THỂ trùng tên combo nhưng **chưa ai verify** — không dựa vào thứ chưa
xác nhận. T3/T4 tra tên qua `BP_ComboManager` (nguồn thật).

### 6.5 TEST T1 — Print String, không đổi hành vi

Chèn **tạm** ở đầu `CB_SaveCombo_Handler` (`BP_FurnitureInputManager`), TRƯỚC guard `LENGTH < 2`:

```
▶→ ResolveActiveComboForSave() ─→ CID, Root, Count, bCan, Reason
▶→ Print String: "SAVE-T1 | can=" + bCan + " | n=" + Count + " | id=" + CID + " | why=" + Reason
▶→ (nối tiếp vào node cũ — KHÔNG cắt luồng hiện tại)
```

| # | Thao tác | Kỳ vọng | Bắt trạng thái |
|---|---|---|---|
| 1 | Chọn 2 mesh rời → Save Combo | `can=false n=2 id= why=Chưa chọn combo nào…` | S2 |
| 2 | Spawn 1 combo → chọn cả cụm → Save | `can=true n=<số món> id=combo_xxx why=` | S4 |
| 3 | Combo A + 3 mesh rời | `can=true n=<món A + 3> id=combo_A` | S8 |
| 4 | Combo A + combo B | `can=false why=Đang chọn nhiều combo…` | S8 |
| 5 | Vào edit mode trong combo → chọn 1 món | `can=false why=Đang sửa bên trong nhóm…` | S6 |
| 6 | Combo A → Ctrl+Z vài lần → chọn lại cụm | `can=true`, `n` khớp số món nhìn thấy, không Accessed None | S9 |

> **Case 6 đắt nhất** — bắt cả S9 lẫn bẫy `GetGroupRoot` trả GID chết (6.0 điểm 2).

**PASS = 6/6** → xóa Print tạm → hỏi 2 câu kiểm tra hiểu bài (6.6) → mở task card T2.

### 6.6 MỤC DẠY (thử nghiệm lần 1 — chưa ghi thành luật)

> Luật này đang chạy thử. Sau T1, đánh giá có giữ không rồi mới sửa `Rules/Learning_System.md`.

**Khái niệm mới: hàm trả về *lý do*, không chỉ trả *kết luận*.**

Ví dụ ngoài UE5 (nghiệp vụ thư viện): bạn đọc đưa thẻ mượn, hệ thống báo "không mượn được". Bạn
đọc hỏi vì sao — nhân viên phải mở tra lại từ đầu. Phiếu từ chối ghi sẵn lý do ("sách đang có
người mượn" / "thẻ quá hạn") thì trả lời được ngay — và **lý do do nơi ra quyết định viết**, không
phải nơi hiển thị đoán lại.

Ở đây: `bCanOverwrite` = kết luận, `ReasonText` = phiếu. Nếu T1 chỉ trả `true/false` thì T3
(widget) phải tự đoán lý do để viết tooltip — hai nơi cùng suy luận về một chuyện — lệch nhau là
chuyện sớm muộn.

**Vì sao 2 hàm nằm ở `BP_FurnitureInputManager`, không nằm trong widget:**

```
InputManager  giữ SelectedActors + EditModeStack + Groups   → SỰ THẬT
Widget        chỉ hiển thị                                   → BỀ MẶT
```

Sự thật đặt ở nơi giữ dữ liệu; widget hỏi và nhận câu trả lời. Nhét logic vào widget → mai có
widget thứ hai cần cùng câu trả lời (ví dụ phím tắt Ctrl+S) → phải chép luật sang chỗ thứ hai.

**Vì sao tách 2 hàm chứ không gộp 1:**

```
GetComboRootOfActor        → SỰ THẬT     "món này thuộc combo nào"
ResolveActiveComboForSave  → CHÍNH SÁCH  "thế thì có cho ghi đè không"
```

Chính sách đổi → sửa hàm 2. Sự thật giữ nguyên. Gộp theo *hình dạng giống nhau* thay vì theo *câu
hỏi nó trả lời* là đường dẫn tới hàm 5 tham số bool không ai dám sửa.

**2 câu kiểm tra hiểu bài — hỏi SAU khi test 6/6 PASS:**
1. Vì sao sau `GetGroupRoot` vẫn phải gọi `FindGroupData` lần nữa, dù `GetGroupRoot` bên trong đã
   gọi rồi?
2. Nếu bỏ `SET ResolveSave_ActorsCopy = SelectedActors` mà lặp thẳng trên `SelectedActors` thì
   hỏng ở đâu?

---

## 6b. TASK CARD T2 — Guard edit-scope cho re-route Replace — ✅ DONE 03/08/2026

**Bug:** `Bug-ReplaceInCombo-TabJump` (`Bugs/Open_Bugs.md`, phát hiện 03/08/2026, ✅ ĐÃ SỬA đủ 2
call site `OnMeshSelected` + `CB_Replace`)
**Người chạy:** Sonnet | **Phạm vi:** `BP_FurnitureInputManager` (1 Function mới) +
`WBP_FurnitureInventory.OnMeshSelected` (đổi 1 call site)

**KHÔNG** đụng: `CB_SaveCombo_Handler`, `WBP_SaveComboDialog`, Toast (K1), `ComboSerializer`,
`ResolveActiveComboForSave()`. T2 độc lập hoàn toàn với luồng Save — xem mục 4 (bảng phụ thuộc).

### 6b.0 T0 — Bảng dấu nguồn tin cậy (PHẢI ĐÓNG TRƯỚC KHI VIẾT NODE)

| Dựa vào | Dấu | Ghi chú |
|---|---|---|
| `GetComboRootOfActor` | ✓TEST 03/08 (T1, 6/6 PASS) | Dùng lại nguyên vẹn |
| `GetCurrentEditScope` | ✓K2 24/07 | |
| `GetGroupRoot` | ✓K2 03/08 | Gián tiếp qua `GetComboRootOfActor` |
| `OnMeshSelected` — cấu trúc nhánh | **⚠ DOC-ONLY** | Cần biết chèn Branch vào ĐÚNG chỗ nào |
| `StartReplaceComboMode` — có đổi breadcrumb không | **⚠ DOC-ONLY** | Doc ghi CÓ gọi `RefreshChipBreadcrumb` (fix #3b, 01/08); quan sát thực tế 03/08 thấy breadcrumb KHÔNG đổi |

**T0 gồm 2 việc, làm TRƯỚC khi sửa bất cứ node nào:**

**T0.a — Export K2Node** `WBP_FurnitureInventory.OnMeshSelected` (toàn bộ event, ước ~15–25 node)
→ cuhoang paste vào chat → Opus/Sonnet đối chiếu, xác định điểm chèn Branch chính xác.

**T0.b — Print xác nhận giả thuyết gốc rễ.** Chèn tạm 2 Print, KHÔNG sửa logic:

```
Print A — đầu OnMeshSelected:
  "T2-A | scope=" + GetCurrentEditScope() + " | replaceMode=" + IsReplaceModeActive()

Print B — ngay TRƯỚC node StartReplaceComboMode:
  "T2-B | vao nhanh combo | breadcrumb hien tai=" + <text đang hiển thị của TB_Breadcrumb>
```

Thao tác: edit mode trong combo → chọn 1 mesh → Replace → ChangeMesh.

| Kết quả Print | Kết luận |
|---|---|
| A in `scope=<gid> replaceMode=true`, B CÓ in | ✅ Giả thuyết 2.9 ĐÚNG → làm tiếp 6b.3 |
| A in `scope=""` | ❌ Edit scope đã bị xoá trước đó → **DỪNG, báo cuhoang**, thiết kế khác |
| B KHÔNG in mà tab vẫn nhảy | ❌ Thủ phạm là đường khác → **DỪNG, báo cuhoang** |

> ⚠️ Đây là 3-strike rule đặt trước: giả thuyết sai → KHÔNG tự mò tiếp, dừng và báo.

**Câu hỏi breadcrumb** (mục 2.9): sau khi có Print B, ghi lại quan sát vào `DEVIATIONS.md`.
**KHÔNG sửa breadcrumb trong T2** — ngoài scope (KP3). Chỉ ghi nhận.

### 6b.1 Q9 — TẦNG 1: S-SCAN

Trạng thái xét: actor được truyền vào `OnMeshSelected` khi đang ở Replace mode.

| ID | Trạng thái | Kết quả sau T2 |
|---|---|---|
| S0 | Không chọn gì | `N/A: chặn bằng Branch(IsValid) có sẵn từ 02/08` — T2 không đổi |
| S1 | 1 mesh rời | `→` route MESH (giữ nguyên hành vi hiện tại) |
| S2 | N mesh rời | `→S1` — Replace nhắm Primary, không đổi |
| S3 | 1 group thường | `→` route MESH (`SourceComboID==""` → không phải combo) |
| S4 | 1 combo cả cụm (KHÔNG edit) | `→` route COMBO — **giữ nguyên**, đây là hành vi đúng của P2 |
| S5 | 1 mesh trong group thường (edit) | `→` route MESH (trước & sau đều mesh — không đổi) |
| S6 | 1 mesh trong combo (edit) | **⚠ ĐỔI: trước = route COMBO (sai) → sau = route MESH** ← chính là bug |
| S7 | Sub-group nested (đang edit) | `→S6` — cùng điều kiện `EditScope != ""` |
| S8 | Mix | `N/A: Replace chỉ nhắm Primary`, T2 không đổi hành vi mix |
| S9 | Selection do máy sinh | `⚠` actor mới spawn từ `F_ExecuteReplace` — ref hợp lệ nhưng là instance MỚI |

> **Ô đổi hành vi duy nhất: S6 (+S7 kéo theo).** Mọi hàng khác giữ nguyên → rủi ro regression
> khoanh vào đúng 1 ca.

### 6b.2 Q9 — TẦNG 2: X-CHECK (ô `⚠` + ô `N/A`)

| # | Hệ thống | Kết luận |
|---|---|---|
| X1 | Undo | Không CaptureSnapshot. `F_ExecuteReplace` đã capture "Replace" ở đường riêng — T2 không chạm |
| X2 | Persistence (4 kho) | Không ghi kho nào. ⚠ Kiểm: `AddRecentMesh` nằm ở `F_ExecuteReplace`, KHÔNG nằm ở `OnMeshSelected` → T2 không ảnh hưởng kho 3 |
| X3 | Inventory UI | **Trọng tâm.** S6 sau fix: giữ tab Furniture, giữ folder mesh, KHÔNG rebuild chip/foldertree sang combo |
| X4 | Selection sau action | Không đổi — T2 chỉ đọc, không SET `SelectedActors`/`PrimarySelectedActor` |
| X5 | Gizmo / Pivot | Không đụng |
| X6 | Group data | Chỉ ĐỌC qua `GetComboRootOfActor` |
| X7 | Toast | **Không bắn toast.** Route đúng tab là hành vi thầm lặng, không phải sự kiện cần báo |
| X8 | EditModeStack | **ĐỌC** — là điều kiện của toàn bộ fix. Không SET, không pop |
| X9 | Material state | `N/A`: `OnMeshSelected` là nhánh Furniture; nhánh Material đi `OnSelectionChangedMaterial` riêng |
| X10 | Placement & Anchor | `N/A`: T2 không spawn/di chuyển gì |

### 6b.3 Hàm mới — `ShouldRouteReplaceToCombo(Actor : BP_FurnitureActor)`

**Đặt tại:** `BP_FurnitureInputManager`
**Outputs:** `bRouteToCombo : Bool` · `ComboID : String` · `RootGroupID : String`
**Local:** `RRT_Scope`, `RRT_Root`, `RRT_CID` (String) · `RRT_bFound` (Bool)

> **Vì sao là Function trong InputManager, không phải Branch trực tiếp trong widget:**
> `OnMeshSelected` là Event (bind từ Dispatcher) → **KHÔNG có Local Variable** (L9). Viết thẳng
> trong widget thì phải đẻ class var trong `WBP_FurnitureInventory` chỉ để giữ giá trị tạm — trái
> R2/R4 (widget ôm thêm state) và trái nguyên tắc "sự thật đặt ở nơi giữ dữ liệu". Widget gọi 1
> node, nhận 3 pin, hết.

> **Trả luôn `ComboID` + `RootGroupID`** để widget không phải gọi thêm hàm thứ hai lấy dữ liệu
> cho `StartReplaceComboMode`. Đây KHÔNG phải prep ngoài scope (KP2): đó là dữ liệu chính call
> site hiện tại đang cần.

```
Q8: Container=Function (Local Var OK, no latent) | IsValid(Actor) đầu hàm ✓ |
L2: 4 nhánh đều chạm Return Node (L12) ✓ | No latent ✓ |
6A: đường ngược = thoát edit mode → route quay lại COMBO, có case test riêng (6b.5 case 4) ✓
```

```
Entry (Actor)
▶→ Branch(IsValid(Actor))
     False ▶→ Return [false, "", ""]                    ← ref chết (S9)
     True  ▶→ GetCurrentEditScope() ●→ SET RRT_Scope
▶→ Branch(RRT_Scope != "")
     True  ▶→ Return [false, "", ""]        ← ĐANG EDIT: đơn vị thao tác là MESH, không phải combo
     False ▶→ GetComboRootOfActor(Actor)
                  ●→ RootGroupID ▶→ SET RRT_Root
                  ●→ ComboID     ▶→ SET RRT_CID
                  ●→ bFound      ▶→ SET RRT_bFound
▶→ Branch(RRT_bFound)
     True  ▶→ Return [true, RRT_CID, RRT_Root]          ← S4: route COMBO (hành vi đúng, giữ)
     False ▶→ Return [false, "", ""]                    ← S1/S3: route MESH
```

### 6b.4 Sửa call site — `WBP_FurnitureInventory.OnMeshSelected`

**Đổi đúng 1 chỗ.** Điểm chèn chính xác chốt sau T0.a (K2Node export).

```
TRƯỚC:
  ▶→ ResolveSelectedComboRoot() ●→ bFound, ComboID, RootGID
  ▶→ Branch(bFound)
       True  ▶→ StartReplaceComboMode(ComboID, RootGID)
       False ▶→ <nhánh mesh có sẵn>

SAU:
  ▶→ ShouldRouteReplaceToCombo(SelectedActor) ●→ bRouteToCombo, ComboID, RootGroupID
  ▶→ Branch(bRouteToCombo)
       True  ▶→ StartReplaceComboMode(ComboID, RootGroupID)     ← giữ nguyên node đích
       False ▶→ <nhánh mesh có sẵn>                             ← giữ nguyên node đích
```

**Ràng buộc KP3 — chỉ đổi node NGUỒN dữ liệu, giữ nguyên 2 node ĐÍCH và mọi node sau chúng.**

⚠️ **KHÔNG sửa `ResolveSelectedComboRoot()`.** Nó vẫn được gọi ở nơi khác (C9). Ceiling "2 nơi
cùng biết cách leo combo root" giữ nguyên, trigger vẫn là C10 — xem `DEVIATIONS.md` 03/08.

⚠️ **Khác biệt cần biết:** `ResolveSelectedComboRoot` đọc `SelectedActors[0]`;
`ShouldRouteReplaceToCombo` đọc **actor được truyền vào event**. Trong Replace mode hai giá trị
này thường trùng, nhưng bản mới đúng hơn về ngữ nghĩa (dùng đúng actor mà event đang nói tới).
Nếu case test 5 lộ khác biệt → ghi `DEVIATIONS.md`, không tự "sửa cho khớp" bản cũ.

### 6b.5 TEST T2

Xóa Print T0.b trước khi test chính thức.

| # | Thao tác | Kỳ vọng | Bắt | Kết quả thật (03/08) |
|---|---|---|---|---|
| 1 | Edit mode trong combo → chọn 1 mesh → Replace → ChangeMesh | Inventory **ở nguyên tab Furniture**, nguyên folder mesh; mesh mới thay đúng chỗ | **S6 — bug gốc** | ✅ PASS — Furniture, folder đúng |
| 2 | Như case 1, group lồng 3 tầng | Y hệt case 1 | S7 | ✅ PASS — Furniture, folder đúng |
| 3 | Edit mode trong **group thường** (không combo) → Replace | Ở nguyên tab Furniture (không đổi so với trước) | S5 | ✅ PASS — Furniture |
| 4 | **Thoát edit mode** → chọn cả cụm combo → Replace | Nhảy sang tab Combo như cũ — **hành vi P2 còn nguyên** | S4 · **6A đường ngược** | ✅ PASS — tab Combo, P2 không regress ⭐ |
| 5 | Chọn 1 mesh rời (ngoài mọi group) → Replace | Ở tab Furniture, folder đúng mesh đó | S1 | ✅ PASS — Furniture, folder đúng |
| 6 | Case 1 → Ctrl+Z → chọn lại mesh trong combo → Replace | Y hệt case 1, không Accessed None | S9 | ✅ PASS — RowName restore đúng, log `CLAMP_table_karkas_005`, không Accessed None |

**Case 4 là case chống regression quan trọng nhất** — nếu nó hỏng thì T2 đã phá tính năng P2 vừa
đóng 02/08. **PASS.**

📌 [CHỨA AS-BUILT — 04/08/2026] **PASS = 6/6 — T2 ĐÓNG.** Case 6 dùng chung bằng chứng với fix
`Bug-RowNameLostOnUndo` (`RestoreSnapshot` SET `NewActor.RowName` sau Undo — xem
`Blueprints/BP_UndoManager.md` v1.15) — 2 fix độc lập nhưng case 6 xác nhận cả hai cùng lúc.
2 câu hiểu bài (6b.6): PASS. Node flow as-built: `Blueprints/BP_FurnitureInputManager.md` v3.3
(`ShouldRouteReplaceToCombo`) + v3.4 (`CB_Replace` re-export), `Widgets/WBP_FurnitureInventory.md`
v3.20 (`OnMeshSelected`).

✅ **Đủ 2 call site đã xác nhận (04/08/2026):** `OnMeshSelected` (test 6/6) + `CB_Replace`
(2 trial chuột phải PASS 03/08). Caveat trước đó ("chưa xác nhận được call site `CB_Replace`") đã
đóng — `CB_Replace` được re-export ✓K2 03/08, bản mô tả 24/07 cũ đọc lúc chưa re-export nên chưa
từng ghi nhánh route combo, không phải code thật thiếu nhánh.

**Mở task card T3 tiếp theo** (đã phát hành, mục 7b).

### 6b.6 MỤC DẠY (thử nghiệm lần 2)

**Khái niệm: cùng một câu hỏi, hai *đơn vị* trả lời khác nhau.**

Ví dụ ngoài UE5 (nghiệp vụ thư viện): độc giả cầm 1 cuốn trong bộ *Tuyển tập Nguyễn Du, 5 tập*.
Hỏi "cái này là cái gì?" — trả lời thế nào tuỳ **ngữ cảnh nghiệp vụ**:

```
Ở quầy mượn (mượn cả bộ)     → "bộ Tuyển tập Nguyễn Du"     ← đơn vị = BỘ
Trong kho (kiểm kê từng cuốn) → "tập 3, mã kho XYZ"          ← đơn vị = CUỐN
```

Không phải một câu đúng một câu sai — **cùng vật thể, khác đơn vị thao tác**.

Bug này y hệt: đang edit trong combo, đơn vị thao tác của người dùng là **món lẻ**, nhưng
`ResolveSelectedComboRoot` luôn trả lời theo đơn vị **cả cụm**. Hàm không sai — nó bị hỏi trong
ngữ cảnh nó không biết.

Đó cũng là lý do fix **không** đụng vào `ResolveSelectedComboRoot`: chữa cái trả lời sẽ làm hỏng
những nơi thật sự cần đơn vị "cả cụm". Chỗ phải chữa là **nơi đặt câu hỏi** — nó mới là nơi biết
đang ở ngữ cảnh nào.

`ResolveSelectionUnit(Actor, EditScope)` của Sprint 4 đã học bài này trước rồi: nó **nhận
EditScope làm tham số**. C9 sinh sau nhưng không kế thừa. Đây là bài học lặp lại, không phải mới.

**2 câu kiểm tra hiểu bài — hỏi SAU khi test 6/6 PASS:**
1. Vì sao fix đặt ở `OnMeshSelected` mà không sửa thẳng `ResolveSelectedComboRoot` cho nó nhận
   `EditScope`? Nêu 1 hậu quả cụ thể nếu sửa hàm cũ.
2. Case test 4 (thoát edit → chọn cả cụm → Replace) kiểm tra điều gì mà 5 case kia không kiểm
   được?

---

## 7. GHI KẾT QUẢ Ở ĐÂU (bắt buộc, theo `R-DOC-ASBUILT`)

### 7.1 Task card chi tiết của task SAU

Ghi **nối tiếp vào chính file này**, thành mục mới `## 6b. TASK CARD T2 — …` (giữ đánh số tăng
dần). KHÔNG tạo file plan mới cho từng task — 1 tính năng = 1 file plan.

### 7.2 Kết quả thực thi (test PASS, K2Node export, đính chính)

| Loại kết quả | Ghi vào |
|---|---|
| Node flow as-built 2 hàm mới | `Blueprints/BP_FurnitureInputManager.md` (bump version + ngày giờ phút) |
| Node flow as-built `WBP_SaveComboDialog` (T3) | `Widgets/WBP_SaveComboDialog.md` |
| Hàm C++ mới (T4) | `Data/ComboSerializer_Reference.md` |
| Bảng kết quả test từng case | `Sprints/Sprint5/` — mục Save As/Save đè |
| Lệch plan / ceiling / trigger | `00_Core/DEVIATIONS.md` |
| Bug phát sinh ngoài scope | `Bugs/Open_Bugs.md` |
| Trạng thái sprint + việc kế tiếp | `00_Core/01_Session_State.md` + `00_Core/02_Current_Sprint.md` |
| Bar đếm | `00_Core/PROGRESS.md` (Đếm lại theo checklist thật — `R-DOC-COUNT`) |

⚠️ **KHÔNG** ghi kết quả test thẳng vào file plan này. Buộc phải ghi tạm → đóng banner
`📌 [CHỨA AS-BUILT]` ngay lúc ghi.

### 7.3 Doc còn thiếu, phải viết mới khi T1 xong

`GetGroupRoot` **chưa có mục doc riêng ở bất kỳ file nào** — chỉ được nhắc tên trong flow của hàm
khác, dù được dùng ở 6+ chỗ. Khi phân phối delta T1: thêm mục `GetGroupRoot()` vào
`Blueprints/BP_FurnitureInputManager.md`, nội dung lấy từ 6.0 file này (kèm đủ 3 ghi chú).

---

## 7b. TASK CARD T3 — Dialog 2 nút Save As / Save đè

> Nguồn: `DELTA_04-08-2026_T3_SaveComboDialog.md` (Opus, 04/08/2026). **PLAN — chưa thực thi,
> chưa test.** Đánh số `7b` (không phải `## 8`) để tránh đụng số mục `## 8. COMMAND BLOCK` đã có
> sẵn trong file — theo đúng pattern `6b` dùng cho task card T2.

**Người chạy:** Sonnet
**Phạm vi:** `BP_FurnitureInputManager` (1 node chèn) · `WBP_FurnitureInventory` (2 Function mới
+ 1 Custom Event mở rộng) · `WBP_SaveComboDialog` (UI + 1 Function + sửa 1 Function)
**KHÔNG:** ghi file · KHÔNG `CaptureSnapshot` · KHÔNG đụng `SaveComboFromSelection`.

> ⚠️ **Scope thật rộng hơn dòng khung mục 3** ("Đụng gì: `WBP_SaveComboDialog`"). Auto-fill
> không sống trong dialog được — dialog không giữ `AllComboViews_Combo` (R3). Dữ liệu phải chảy
> qua inventory. Đây là plumbing bắt buộc, KHÔNG phải feature thêm (KP2 — đã trình cuhoang duyệt
> 04/08/2026).

### 7b.0 — T0: bảng dấu nguồn tin cậy

| Dựa vào | Dấu |
|---|---|
| `CB_SaveCombo_Handler` guard `>=2` + chuỗi exec | ✓K2 04/08/2026 — ⚠️ XEM CẢNH BÁO XUNG ĐỘT: mục này KHÔNG được merge vào `BP_FurnitureInputManager.md` trong đợt này, xem báo cáo cuối |
| `ResolveActiveComboForSave` — 5 output | ✓TEST 6/6 03/08/2026 |
| `AllComboViews_Combo` (Array `BP_ComboItemView`) | ✓ as-built |
| `BP_ComboItemView`: ComboName · FolderPath · Description · Tags | ✓ as-built (v1.3) |
| `OpenSaveComboDialog` + freeze `PendingSelectedActors` | ✓ as-built (C3b) |
| `ValidateComboName` gate `BTN_Confirm` | ✓ as-built |
| **Tooltip hiện được trên Button đã `SetIsEnabled(false)`** | ⚠ **CHƯA VERIFY — xem 7b.5** |

⚠ duy nhất nằm ở 7b.5 và phải test TRƯỚC khi code phần UI.

### 7b.1 — Chèn resolve (`BP_FurnitureInputManager.CB_SaveCombo_Handler`)

```
Q8: Container=Custom Event (KHÔNG Local Var — wire thẳng output pin, né L9) |
IsValid: giữ nguyên 2 guard sẵn có ✓ | L2: chèn nối tiếp, không đẻ nhánh mới ✓ |
No latent ✓ | 6A: thuần đọc; đường ngược = BTN_Cancel dialog (sẵn có) ✓
```

```
Branch(Length >= 2).True
  ▶→ ResolveActiveComboForSave()            ← CHÈN MỚI, đứng ĐẦU nhánh True
       ─→ ComboID · bCanOverwrite · ReasonText     (3 pin wire thẳng xuống 7b.3)
  ▶→ CalculateComboAnchor(...)              ← giữ nguyên
  ▶→ GetAllWidgetsOfClass(...)              ← giữ nguyên
  ▶→ Branch(IsValid(FoundWidgets[0]))       ← giữ nguyên
       True ▶→ OpenSaveComboDialog(SelectedActors, Center, +3 pin mới)
```

- Resolve chạy **ĐÚNG 1 lần**, cùng frame với freeze selection — không lệch (chặn ca S9).
- `ItemCount` / `RootGroupID` **KHÔNG truyền** — T3 chưa dùng; thêm pin thừa = speculative (KP2).
- Output pin node impure đã latch — không cần biến trung gian.

⚠️ **Ghi chú vị trí chèn:** node flow ở trên mô tả theo bản K2Node export 04/08 (mục A của delta
nguồn), nhưng bản export đó XUNG ĐỘT với section `CB_SaveCombo_Handler` hiện có trong
`BP_FurnitureInputManager.md` (khác cấu trúc guard + có thêm bước `ContextMenuRef.Hide` chưa từng
ghi). Khi thực thi T3 thật, PHẢI đối chiếu lại với bản as-built THẬT SỰ đang nằm trong doc canonical
lúc đó (có thể đã khác cả 2 bản này), không giả định bản nào đúng — xem báo cáo mâu thuẫn cuối
delta gốc.

### 7b.2 — Hai Function mới trong `WBP_FurnitureInventory`

Tách đôi theo nguyên tắc T1: **sự thật** tách khỏi **chính sách**.

```
GetComboViewByID        → SỰ THẬT    "combo này còn trong thư viện không, metadata là gì"
BuildSaveDialogPrefill  → CHÍNH SÁCH "thế thì có cho ghi đè không, điền sẵn gì"
```

**Vị trí:** đặt cạnh `GetExistingFolders` / `GetAllUsedTags` (cùng họ hàm đọc
`AllComboViews_Combo`).

> **[ARCH-DEBT]** Nơi tối ưu LÂU DÀI của `GetComboViewByID` là `BP_ComboManager`. Không dời bây
> giờ vì `AllComboViews_Combo` đang sống trong widget — đặt hàm ở manager sẽ khiến manager (tầng
> dữ liệu) phụ thuộc ngược vào widget (tầng bề mặt), sai chiều nặng hơn. Xem entry backlog
> `DEVIATIONS.md` mục "[ARCH-DEBT] AllComboViews_Combo sống ở widget".

#### `GetComboViewByID(ComboID : String) → (View : BP_ComboItemView, bFound : Bool)`

```
Q8: Container=Function (Local Var OK) | Branch match trước khi SET View ✓ |
L2: dead-end trong Loop Body hợp lệ (macro tự chạy vòng sau); Completed có Return ✓ |
No latent ✓ | 6A: thuần đọc ✓
```

**Local:** `Found_View` (BP_ComboItemView) · `Found_bOK` (Bool)

```
Entry ▶→ SET Found_bOK = false                    ← CLEAR đầu function
      ▶→ ForEachLoopWithBreak(AllComboViews_Combo)
           Loop Body ▶→ Branch(Element.ComboID == ComboID)
                          True  ▶→ SET Found_View = Element
                                 ▶→ SET Found_bOK = true
                                 ▶→ Break
                          False ▶→ (trống)
           Completed ▶→ Return(Found_View, Found_bOK)
```

> Pattern y hệt đoạn loop inline sẵn có trong `CB_MoveCombo` (đã chạy tốt) — không phải node lạ.
> **KHÔNG refactor `CB_MoveCombo` cho gọi hàm mới** (KP3 — chỉ ghi nhận, không tiện tay sửa).

#### `BuildSaveDialogPrefill(ComboID : String, bCanOverwrite : Bool, ReasonIn : String) → (PrefillName, PrefillFolder, PrefillDesc, PrefillTagsText : String, bOverwriteAllowed : Bool, ReasonOut : String)`

```
Q8: Container=Function (Local Var OK) | chỉ đọc View trong nhánh bFound=true ✓ |
L2: SET default TRƯỚC Branch, nhánh False để trống (L10) ✓ | No latent ✓ | 6A: thuần đọc ✓
```

**Local:** `Pre_Name` · `Pre_Folder` · `Pre_Desc` · `Pre_TagsText` · `Pre_Reason` (String) ·
`Pre_bAllow` (Bool) · `Pre_View` (BP_ComboItemView) · `Pre_bFound` (Bool)

```
Entry ▶→ SET Pre_Name = "" · Pre_Folder = "" · Pre_Desc = "" · Pre_TagsText = ""
      ▶→ SET Pre_bAllow = false · SET Pre_Reason = ReasonIn        ← default TRƯỚC mọi Branch
      ▶→ Branch(bCanOverwrite)
           False ▶→ (trống — giữ default; lý do đã là ReasonIn nguyên văn từ T1)
           True  ▶→ GetComboViewByID(ComboID) ─→ Pre_View, Pre_bFound
                 ▶→ Branch(Pre_bFound)
                      False ▶→ SET Pre_Reason =
                               "Combo gốc không còn trong thư viện — chỉ lưu được thành combo mới"
                      True  ▶→ SET Pre_bAllow = true
                             ▶→ SET Pre_Reason = ""
                             ▶→ SET Pre_Name     = Pre_View.ComboName
                             ▶→ SET Pre_Folder   = Pre_View.FolderPath
                             ▶→ SET Pre_Desc     = Pre_View.Description
                             ▶→ Join(Pre_View.Tags, ", ") ─→ SET Pre_TagsText
      (merge) ▶→ Return(Pre_Name, Pre_Folder, Pre_Desc, Pre_TagsText, Pre_bAllow, Pre_Reason)
```

**Vì sao lý do MỚI này viết ở widget, không đẩy về T1:** "combo còn trong thư viện không" thuộc
miền dữ liệu của widget (`AllComboViews_Combo`); `BP_FurnitureInputManager` không biết gì về thư
viện. Nơi ra quyết định là nơi viết lý do — nhất quán với bài học "phiếu từ chối" ở T1, không mâu
thuẫn.

### 7b.3 — `OpenSaveComboDialog` mở rộng (`WBP_FurnitureInventory`)

Signature thêm 3 param: `ActiveComboID : String` · `bCanOverwrite : Bool` · `ReasonText : String`.

```
Q8: Container=Custom Event (đã latent-free) | Branch IsValid(SaveComboDialogRef) sẵn có ✓ |
L2: chèn TRƯỚC Create Widget, không đẻ nhánh mới ✓ | No latent ✓ |
6A: OnDialogCancelled sẵn có ✓
```

```
SET PendingSelectedActors / PendingCenter          ← giữ nguyên (freeze C3b)
GetAllUsedTags() → TempTags                        ← giữ nguyên
▶→ BuildSaveDialogPrefill(ActiveComboID, bCanOverwrite, ReasonText)   ← CHÈN, trước Create Widget
     ─→ 6 output wire thẳng vào Create Widget
▶→ Create Widget(WBP_SaveComboDialog,
       TagVocabulary       = TempTags,             ← pin cũ
       bOverwriteAllowed   = Pre_bAllow,           ←
       OverwriteComboID    = ActiveComboID,        ←
       OverwriteName       = PrefillName,          ←
       DisabledReason      = ReasonOut,            ← 8 pin Expose on Spawn MỚI
       PrefillName         = PrefillName,          ←
       PrefillFolder       = PrefillFolder,        ←
       PrefillDesc         = PrefillDesc,          ←
       PrefillTagsText     = PrefillTagsText)      ←
(phần còn lại giữ nguyên: Branch IsValid → BuildComboFolderTree → Picker.SetFolders →
 bind 2 dispatcher → AddToViewport → Set Input Mode UI Only)
```

Sau `Picker.SetFolders(Entries)` nối thêm:
```
▶→ Picker.ExpandToPath(PrefillFolder)      ← dùng lại đúng cặp node của HandleSaveDialogCreateFolder
```
> ⚠ Cách set SelectedPath của Picker chưa verify trong đợt này — nếu `ExpandToPath` không tự
> chọn path, **DỪNG, báo cuhoang** (KP1), không tự đoán API của `WBP_FolderTreePicker`.

### 7b.4 — `WBP_SaveComboDialog`

#### Designer (surgical)

- **GIỮ `BTN_Confirm`**, chỉ đổi Text → `"Lưu thành combo mới…"`.
  KHÔNG rename biến (rename = gãy `ValidateComboName` + binding sẵn có).
- **THÊM `Border_OverwriteWrap`** trong `HB_Buttons`, đặt **bên trái** `BTN_Confirm`;
  bên trong chứa `BTN_Overwrite`.
  → `ToolTipText` đặt trên **Border**, KHÔNG trên Button (lý do: 7b.5).

#### Expose on Spawn (8 biến mới)
`bOverwriteAllowed : Bool` · `OverwriteComboID : String` · `OverwriteName : String` ·
`DisabledReason : String` · `PrefillName : String` · `PrefillFolder : String` ·
`PrefillDesc : String` · `PrefillTagsText : String`

#### Function mới `RefreshButtonStates()` — nguồn DUY NHẤT quyết định 2 nút

```
Q8: Container=Function (Local Var OK) | không object access ngoài widget con ✓ |
L2: 1 đường thẳng, SET đủ cả 2 nút ✓ | No latent ✓ |
6A: gõ lại tên → gọi lại hàm này, trạng thái tự đảo ✓
```

**Local:** `bNameOK` (Bool)

```
▶→ GET Text(TextBox_ComboName) → ToString → IsEmpty → NOT ─→ SET bNameOK
▶→ Set Is Enabled(BTN_Confirm, bNameOK)
▶→ AND(bNameOK, bOverwriteAllowed) ─→ Set Is Enabled(BTN_Overwrite, <kết quả AND>)
▶→ Set Tool Tip Text(Border_OverwriteWrap, DisabledReason)
```

> Tên rỗng → **CẢ HAI** nút xám. Nếu chỉ gate `BTN_Confirm` như hiện tại thì Overwrite sống lúc
> tên rỗng → T4 sẽ ghi metadata rỗng đè lên combo thật.

#### Sửa `ValidateComboName(Text)`

Thay 2 nhánh `Set Is Enabled(BTN_Confirm, …)` bằng **1 node gọi `RefreshButtonStates`**.
→ Luật 6B: hai đường (Event Construct và OnTextChanged) dẫn tới cùng cấu trúc phải cho cùng kết quả.

#### Event Construct — nối thêm SAU đoạn cũ

```
▶→ SetText(TextBox_ComboName, PrefillName)
▶→ SetText(TextBox_Description_MultiLine, PrefillDesc)
▶→ SetText(TextBox_Tags, PrefillTagsText)
▶→ SetText(<TextBlock trong BTN_Overwrite>, "Ghi đè \"" + OverwriteName + "\"")
▶→ RefreshButtonStates()                          ← thay dòng Set Is Enabled(BTN_Confirm,false) cũ
```
> Folder prefill do `Picker` lo ở 7b.3, không set trong Construct.

#### `BTN_Overwrite.OnClicked` — T3 CHỈ Print

```
Print String: "T3-OVERWRITE | id=" + OverwriteComboID + " | name=" + TextBox_ComboName
              [DevelopmentOnly]
```
KHÔNG broadcast, KHÔNG `Remove from Parent`. Dispatcher là mặt cắt của T4 (mục 7b.6).

#### Ngữ nghĩa đã chốt
Sửa tên trong ô rồi bấm **Ghi đè** = **đổi tên tại chỗ**, `comboId` GIỮ NGUYÊN.
Đúng mô hình Save của phần mềm desktop. KHÔNG phải bug.

### 7c — T3 SCOPE THU GỌN (CHỐT 05/08/2026 — ĐÈ thiết kế 7b ở các điểm ghi dưới)

Sau khi phân tích luồng người dùng (05/08/2026), UX chốt lại đơn giản hơn 7b:

NGỮ NGHĨA:
- bOverwriteAllowed=true  → nút Save = ghi đè combo gốc (T4).
- bOverwriteAllowed=false (MỌI lý do, kể cả đang edit mode) → nút Save rơi về
  luồng Save As (lưu selection thành combo mới). KHÔNG đặc biệt hóa edit mode.

CẮT khỏi 7b (KHÔNG làm trong T3):
- KHÔNG thêm output bIsEditGroup vào ResolveActiveComboForSave.
- KHÔNG làm nhánh cảnh báo Edit Group (3 nút).
- KHÔNG thêm dispatcher OnRequestExitEditAndSave + handler InputManager.
- KHÔNG tách Function dùng chung trong CB_SaveCombo_Handler.
- Ca Q9 "bCanOverwrite vs bFound" (7b.6): GIỮ nguyên trong BuildSaveDialogPrefill
  (đã code, đã ✓K2) — vẫn đúng, không cắt.

CÒN LẠI trong T3 (4 việc, đều trong WBP_SaveComboDialog):
1. RefreshButtonStates() — Function: cả 2 nút chỉ xám theo tên rỗng (bNameOK);
   set tooltip DisabledReason lên Border_OverwriteWrap; nhãn/logic nút Save theo
   bOverwriteAllowed.
2. Sửa ValidateComboName → gọi RefreshButtonStates (Luật 6B).
3. Event Construct: set text các ô prefill + gọi RefreshButtonStates.
4. BTN_Overwrite.OnClicked — Branch(bOverwriteAllowed): True→Print "ghi đè";
   False→chạy đúng luồng BTN_Confirm hiện có (Save As).

ĐÃ HOÀN THÀNH TRƯỚC MỤC NÀY (ghi nhận as-built, chi tiết node flow ở doc canonical
khi phân phối sau):
- GetComboViewByID, BuildSaveDialogPrefill (Function mới, WBP_FurnitureInventory) — ✓K2.
- BP_ComboItemView thêm field Description + nối LoadComboLibrary.
- 8 biến Expose on Spawn trong WBP_SaveComboDialog.
- OpenSaveComboDialog mở rộng (+3 param, gọi BuildSaveDialogPrefill, nối 8 pin,
  Picker.ExpandToPath).
- Chèn ResolveActiveComboForSave vào CB_SaveCombo_Handler (BP_FurnitureInputManager).
- Designer: Border_OverwriteWrap + BTN_Overwrite; đổi text BTN_Confirm="Lưu dưới
  dạng…", BTN_Overwrite="Lưu".

TEST T3 (6 case):
1. 2 mesh rời → Save → nút Save="Lưu dưới dạng…", form trống.
2. Spawn combo → chọn cả cụm → Save → nút="Lưu" (ghi đè), nhãn combo đúng, 4 field
   prefill, Picker đúng folder.
3. Combo A + 3 mesh rời → Save → như case 2, id= là combo A.
4. Combo A + Combo B → Save → nút Save As, tooltip "Đang chọn nhiều combo…".
5. Đang edit mode → chọn món → Save → nút Save As (KHÔNG chặn), tooltip lý do edit.
6. Xóa trắng ô tên (ở case 2) → cả 2 nút xám.
PASS 6/6 → xóa Print → 2 câu hiểu bài → mở T4.

---

### 7b.5 — ⚠ BẪY UMG — TEST TRƯỚC KHI CODE PHẦN UI

**Button đã `SetIsEnabled(false)` thường KHÔNG nhận hover event — tooltip có thể không hiện.**
Toàn bộ thiết kế "nút xám + tooltip nêu lý do" (quyết định 2.2, mục 2 plan gốc) đứng hay sập ở đây.

**Test 1 phút, làm TRƯỚC mọi việc khác trong T3:**
dựng tạm 1 Border có `ToolTipText`, nhét 1 Button `IsEnabled=false` vào, PIE, rê chuột lên.

| Kết quả | Hành động |
|---|---|
| Tooltip hiện | Theo đúng card này |
| Tooltip KHÔNG hiện | **DỪNG, báo cuhoang.** Plan B: hiện lý do bằng 1 TextBlock nhỏ ngay dưới hàng nút (luôn thấy, không cần hover) |

### 7b.6 — Q9 S-MATRIX GATE

Trạng thái xét: selection tại thời điểm bấm **Save Combo** (dialog phản chiếu đúng snapshot đó).

#### Tầng 1 — S-Scan

| ID | Trạng thái | Kết quả T3 |
|---|---|---|
| S0 | Không chọn gì | `N/A: guard Array_Length >= 2 chặn trước khi mở dialog` (✓K2 mục 7b.0) |
| S1 | 1 mesh rời | `N/A: cùng guard >= 2` |
| S2 | N mesh rời (≥2) | `⚠` Overwrite xám (ReasonText T1 "Chưa chọn combo nào…"), Save-new sống |
| S3 | 1 group thường | `≡S2` — `SourceComboID == ""` → T1 trả `bCanOverwrite=false` |
| S4 | 1 combo cả cụm | `⚠` **Đường chính** — prefill + gap `bFound` (xem X-Check) |
| S5 | mesh trong group thường (edit) | `N/A: T1 guard EditScope → xám + lý do` |
| S6 | mesh trong combo (edit) | `N/A: T1 guard EditScope → xám + lý do` — ca mất dữ liệu nguy hiểm nhất |
| S7 | sub-group nested (edit) | `≡S6` — cùng điều kiện `EditScope != ""` |
| S8 | Mix (combo + mesh rời) | `⚠` 1 combo root → như S4; ≥2 → xám (T1) |
| S9 | Selection do máy sinh | `⚠` instance mới sau undo/spawn — resolve chạy cùng frame với freeze (7b.1) |

#### Tầng 2 — X-Check (ô `⚠` + ô `N/A`)

| # | Hệ thống | Kết luận |
|---|---|---|
| X1 | Undo | KHÔNG `CaptureSnapshot` — T3 chỉ hiển thị + Print |
| X2 | Persistence (4 kho) | **Ghi 0/4 kho.** Kho 4 (combo JSON + PNG) là việc của T4 |
| X3 | Inventory UI | Dialog là overlay modal — KHÔNG đổi tab/folder nền. Prefill chỉ set Picker BÊN TRONG dialog |
| X4 | Selection sau action | KHÔNG SET `SelectedActors`. Freeze `PendingSelectedActors` sẵn có (C3b) |
| X5 | Gizmo / Pivot | Không đụng |
| X6 | Group data | Chỉ ĐỌC qua `ResolveActiveComboForSave` |
| X7 | Toast | Không bắn toast trong T3 |
| X8 | EditModeStack | **ĐỌC** — là gate của S5/S6/S7 (qua T1) |
| X9 | Material state | N/A |
| X10 | Placement & Anchor | N/A — `CalculateComboAnchor` giữ nguyên, T3 không đụng |

**Trục ngữ cảnh:** B (EditModeStack) — đã là gate qua T1. D (CurrentInventoryMode) — prefill đọc
`AllComboViews_Combo` bất kể tab đang mở, ghi nhận, không thành vấn đề. C / E: N/A.

#### ⭐ Ca Q9 bắt được — hai nguồn sự thật lệch nhau

```
bCanOverwrite  → nguồn: Groups        (group root có SourceComboID)
bFound         → nguồn: thư viện      (combo .json còn trong AllComboViews_Combo)
```

Hai cái này **KHÔNG cùng nguồn**. Ca hở: spawn combo vào scene → xoá combo đó trong tab thư viện
(actor trong scene vẫn giữ `SourceComboID`) → bấm Save Combo:
- T1 trả `bCanOverwrite = true`
- `GetComboViewByID` trả `bFound = false`
- → nhãn nút thành `Ghi đè ""`, prefill rỗng, và **T4 sẽ định ghi đè lên file không còn tồn tại**

**Fix (đã đưa vào 7b.2):** nút Overwrite sống = `bCanOverwrite AND bFound`.
Nếu bỏ qua Q9, ca này lọt tới T4 mới nổ — đúng lúc đang thao tác file trên đĩa.

### 7b.7 — TEST T3 (8 case, map thẳng S-Scan)

| # | Thao tác | Kỳ vọng | S |
|---|---|---|---|
| 1 | Chọn 1 món → Save Combo | Không mở dialog, không crash (ghi nhận: chặn im lặng) | S0/S1 |
| 2 | 2 mesh rời → Save | Dialog mở; Overwrite XÁM + tooltip "Chưa chọn combo nào…"; 4 field trống | S2 |
| 3 | Spawn combo → chọn cả cụm → Save | Overwrite SỐNG; nhãn `Ghi đè "<tên>"`; 4 field prefill đúng; Picker ở đúng folder | S4 |
| 4 | Combo A + 3 mesh rời → Save | Như case 3; `id=` in ra là combo A | S8 |
| 5 | Combo A + combo B → Save | Overwrite xám; tooltip "Đang chọn nhiều combo…" | S8 |
| 6 | Vào edit mode → chọn 2 món → Save | Overwrite xám; tooltip "Đang sửa bên trong nhóm…" | S6 |
| 7 | Spawn combo → **xoá combo đó trong tab thư viện** → chọn cụm → Save | Overwrite xám; tooltip "Combo gốc không còn trong thư viện…" | ca Q9 |
| 8 | Xoá trắng ô tên (ở case 3) | **CẢ HAI** nút xám | — |

**PASS = 8/8** → xoá Print tạm → hỏi 2 câu kiểm tra hiểu bài → mở task card T4.

### 7b.8 — MỤC DẠY (2 câu hỏi SAU khi test 8/8 PASS)

1. Vì sao `bCanOverwrite` (từ T1) và `bFound` (từ `GetComboViewByID`) phải **cùng đúng** thì nút
   Ghi đè mới sống — trong khi cả hai nghe như đang trả lời cùng một câu hỏi "combo này có tồn
   tại không"?
2. Vì sao lý do "Combo gốc không còn trong thư viện" viết ở **widget**, còn 4 lý do kia
   ("Chưa chọn gì" / "Chưa chọn combo nào" / "Đang chọn nhiều combo" / "Đang sửa bên trong nhóm")
   viết ở **InputManager** — mà vẫn coi là nhất quán, không phải hai nơi cùng suy luận?

---

### 7b.9 — Mặt cắt bàn giao T4 / T5 (chưa phải task card — chỉ hợp đồng)

```
T3 kết thúc bằng 2 đường ra:

BTN_Confirm    → OnDialogConfirmed(Name, Folder, Desc, Tags)          → đường CŨ, KHÔNG đụng
                 → T4: SaveComboFromSelection(...) sinh comboId MỚI

BTN_Overwrite  → OnDialogConfirmedOverwrite(ComboID, Name, Folder, Desc, Tags)   → T4 tạo
                 → T4: GIỮ comboId, ghi đè .json, InvalidateThumbnail + chụp lại
                 → dùng PendingSelectedActors (mảng đã đóng băng),
                   KHÔNG đọc lại SelectedActors
```

T5 nhận: bảng S-Scan T3 (test kết quả thật cho **từng ô**, kể cả ô `N/A`) + đóng
`Note-DuplicateComboID`.

#### T0 sơ bộ cho T4 (chỉ liệt kê phụ thuộc — KHÔNG viết node)

Chạy trước để biết T4 có ép T3 đổi mặt cắt không. Ô `⚠` phải gỡ bằng export/đọc `.h` trước khi
viết task card T4.

| T4 dựa vào | Dấu |
|---|---|
| `SaveComboFromSelection` — có nhận ComboID từ ngoài, hay luôn tự sinh GUID? | ⚠ DOC-ONLY |
| Tín hiệu "ghi json thành công" là pin nào? (V7 treo từ P1.G4) | ⚠ DOC-ONLY |
| Hàm load 1 combo (`LoadCombo`?) — tên chưa xác nhận | ⚠ tên chưa verify |
| `InvalidateThumbnail` + `BeginComboCapture`/`FinishComboCapture` | ✓ as-built |
| `PendingSelectedActors` freeze | ✓ as-built |

> **KHÔNG viết task card T4/T5 lúc này** (luật mục 5: mỗi lần chỉ mở kế hoạch chi tiết 1 task).
> Lý do cụ thể: 3 ô ⚠ trên chỉ gỡ được bằng đọc code/export thật; thumbnail re-capture là cặp
> 2 pha chạy qua Event Tick (24 frame), thiết kế mà chưa nhìn flow thật = đoán. Riêng T5 về bản
> chất không lên trước được — nội dung nó là regression + đọc `DEVIATIONS.md`, mà deviation chưa
> xảy ra.

---

## 8. COMMAND BLOCK — GIAO CLAUDE CODE

```
=== COMMAND BLOCK: phân phối delta Save As/Save đè — 03/08/2026 ===

FILE NGUỒN: 03-08-2026_SaveAsOverwrite_Execution_Plan.md

GIỚI HẠN BẮT BUỘC (đọc trước khi làm):
- Claude Code KHÔNG truy cập project UE5, KHÔNG đọc được Blueprint graph.
- ĐƯỢC: merge delta, đóng dấu, cross-check, LIỆT KÊ mâu thuẫn.
- KHÔNG ĐƯỢC: tự sửa mô tả node flow / chữ ký hàm / tên biến "cho khớp".
  Không có ground truth thì chỉ BÁO CÁO, không SỬA.
- KP3: chỉ đụng đúng các file liệt kê dưới. Thấy chỗ đáng sửa ngoài danh sách → báo, không sửa.

────────────────────────────────────────────
VIỆC 1 — Thêm file plan vào repo
────────────────────────────────────────────
- Copy file nguồn vào: docs/Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md
- KHÔNG đóng dấu [HISTORICAL] hay [CHỨA AS-BUILT] — đây là plan đang chạy, chưa có as-built.
- Thêm dòng vào docs/00_Core/MERGE_LOG.md phần coverage.

────────────────────────────────────────────
VIỆC 2 — docs/00_Core/01_Session_State.md
────────────────────────────────────────────
Thêm vào changelog, ngày 03/08/2026:

"Save As/Save đè — LẬP KẾ HOẠCH XONG (khung 5 task), task card T1 đã phát hành.
Kế hoạch đầy đủ: `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md`.
UX chốt: 2 nút trong WBP_SaveComboDialog (Ghi đè / Lưu thành combo mới), nút Ghi đè xám khi
0 hoặc ≥2 combo root, hoặc đang trong edit mode. Test lớp dữ liệu 03/08 PASS: GroupID sống
sót qua Replace kể cả group lồng 3 tầng → Save đè không cần thiết kế đặc biệt.
Bug UX 'replace trong combo → inventory nhảy tab Combo' GỘP vào đợt này làm T2.
Tiếp theo: T1 (2 Function mới trong BP_FurnitureInputManager)."

Cập nhật dòng 'Phiên bản' đầu file cho khớp.

────────────────────────────────────────────
VIỆC 3 — docs/00_Core/02_Current_Sprint.md
────────────────────────────────────────────
Thay toàn bộ mục "Đang chạy: Save As / Save đè combo" bằng:
- Bỏ dòng "UX CHƯA CHỐT — bàn phương án trước khi lên task card thực thi".
- Trỏ tới Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md làm nguồn duy nhất.
- Chép bảng khung 5 task (mục 3 file nguồn) + trạng thái: T1 đang chạy, T2-T5 chưa mở.
- Giữ nguyên dòng "Sau Save As/Save đè: C11 → C10 → Gate 2".

────────────────────────────────────────────
VIỆC 4 — docs/00_Core/DEVIATIONS.md
────────────────────────────────────────────
4a. Mục "[DOC-DRIFT] ResolveSelectedComboRoot — PrimarySelectedActor vs SelectedActors[0] —
    02/08/2026": đổi Trạng thái từ "Ghi nhận, CHƯA đóng — chờ quyết định khi lên task card
    Save As/Save đè" thành:

    "✅ ĐÃ QUYẾT 03/08/2026 — Save As/Save đè KHÔNG dùng biến nào trong 2 biến này. Cả hai đều
    lấy MỘT actor rồi leo lên → kết quả phụ thuộc thứ tự Ctrl-click. Tính năng mới dùng hàm
    riêng `ResolveActiveComboForSave()` quét TOÀN BỘ SelectedActors, đếm số combo root khác
    nhau. `ResolveSelectedComboRoot()` giữ nguyên, KHÔNG sửa (KP3 — C9 vừa test PASS 30/07).
    Xem `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 2.8."

4b. Thêm section mới "[CEILING] Hai nơi cùng biết cách leo combo root — 03/08/2026":

    Lệch:    T1 tạo `GetComboRootOfActor()` làm hàm nguyên thủy, nhưng KHÔNG đấu lại
             `ResolveSelectedComboRoot()` (C9) vào nó → 2 nơi cùng biết cách leo combo root.
    Vì sao:  `ResolveSelectedComboRoot` nằm giữa đường Replace vừa test PASS 02/08; sửa lúc
             này kéo theo regression C9 giữa lúc làm tính năng khác.
    Ceiling: chấp nhận tới hết đợt Save As/Save đè.
    Trigger: C10 (regression full) — đấu lại + chạy 5 case C9 (bộ test đã bật sẵn, chi phí
             thêm ~0). Hoặc SỚM HƠN nếu có bất kỳ thay đổi nào về cách xác định combo root.

4c. Thêm section mới "[DOC-DEBT] GetGroupRoot chưa từng có doc — phát hiện 03/08/2026":

    Hàm dùng ở 6+ chỗ nhưng chưa có mục doc riêng ở bất kỳ file nào — chỉ được nhắc tên trong
    flow của hàm khác. K2Node export 03/08 lộ 3 hành vi chưa ai ghi:
      (1) cap 10 tầng (ForLoop LastIndex=9), vượt → trả nửa chừng, KHÔNG báo lỗi;
      (2) không tìm thấy group → trả lại CHÍNH GID truyền vào, KHÔNG trả "";
      (3) vòng cha-con quẩn (A→B→A) không bị phát hiện.
    Cả 3 không chặn T1. KHÔNG sửa hàm (KP3).
    Trigger: (1) và (3) nâng lên bug thật nếu combo lồng vượt 3 tầng được cho phép.

────────────────────────────────────────────
VIỆC 5 — docs/Sprints/Sprint5/Combo_Execution.md
────────────────────────────────────────────
Mục "C9.5 — Save As / Save đè combo (MỚI, thêm 22/07/2026 — ⚠️ UX CHƯA CHỐT)":
- Đóng dấu ⚠️ [HISTORICAL] ngay đầu mục.
- Thêm dòng ngay dưới dấu:
  "SUPERSEDED 03/08/2026 — UX đã chốt, KHÔNG theo Phương án A/B mô tả bên dưới. Nguồn duy
   nhất: `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md`. Giữ mục này để tra 'vì sao đã
   từng cân nhắc 2 phương án'."
- KHÔNG xóa nội dung Phương án A/B.

────────────────────────────────────────────
VIỆC 6 — docs/Bugs/Open_Bugs.md
────────────────────────────────────────────
6a. Mục "Note-DuplicateComboID": đổi Trạng thái thành
    "Backlog → ĐÃ CÓ PLAN 03/08/2026. Save As sinh comboId mới, Save đè giữ nguyên — chốt tại
     `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 2.4. Đóng khi T4 xong."

6b. Thêm entry mới vào bảng tổng + mục chi tiết:
    ID:        Bug-ReplaceInCombo-TabJump
    Phát hiện: 03/08/2026 (test tay verify lớp dữ liệu, phiên lập kế hoạch Save As)
    Ưu tiên:   🟡 Trung bình — KHÔNG chặn Gate 2
    Triệu chứng: Replace 1 mesh bên trong combo (đang edit mode) → xong thì inventory tự nhảy
                 sang tab Combo (foldertree/chiprow/chiptag/CTV_ComboCard đổi theo combo),
                 breadcrumb vẫn đứng ở path folder mesh.
    Giả thuyết gốc (CHƯA verify bằng Print): `ResolveSelectedComboRoot()` mù edit mode — luôn
                 GetGroupRoot leo tận combo root, không nhận EditScope (khác
                 `ResolveSelectionUnit(Actor, EditScope)` của Sprint 4). Không phải bug của
                 re-route P2.
    Trạng thái:  ĐÃ CÓ PLAN — là T2 của đợt Save As/Save đè.
    ⚠ KHÔNG ghi hướng fix như đã chốt — chưa verify.

────────────────────────────────────────────
VIỆC 7 — KHÔNG LÀM (ghi để khỏi hiểu nhầm)
────────────────────────────────────────────
- KHÔNG thêm mục `GetGroupRoot()` vào Blueprints/BP_FurnitureInputManager.md ở lượt này.
  Chờ T1 test PASS rồi phân phối cùng delta as-built T1 (xem mục 7.3 file nguồn).
- KHÔNG sửa Rules/Learning_System.md. Mục DẠY đang chạy thử lần 1, chưa thành luật.
- KHÔNG đổi bar đếm PROGRESS.md — chưa có ô nào tick (mới lập kế hoạch, chưa thực thi).
- KHÔNG sửa Plans/24-07-2026_C9_Execution_Plan.md (đã đóng dấu 📌 [CHỨA AS-BUILT]).

────────────────────────────────────────────
BÁO CÁO SAU KHI XONG
────────────────────────────────────────────
- Liệt kê file đã sửa + số dòng thay đổi mỗi file.
- Liệt kê MỌI mâu thuẫn phát hiện trong lúc merge — chỉ LIỆT KÊ, không tự sửa.
- Xác nhận không đụng file nào ngoài danh sách.
=== HẾT COMMAND BLOCK ===
```

---

## 9. LỊCH SỬ CẬP NHẬT

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 03/08/2026 | Tạo mới. Chốt UX (2 nút, bảng trạng thái nút Ghi đè), đóng `[DOC-DRIFT] ResolveSelectedComboRoot`, gộp bug `Bug-ReplaceInCombo-TabJump` làm T2, khung 5 task, task card T1 đầy đủ (Q9 S-Scan + X-Check, 2 Function, 6 case test, mục DẠY thử nghiệm lần 1), ghi nhận as-built `GetGroupRoot` từ K2Node export 03/08. |
| 1.1 | 03/08/2026 | Phát hành task card T2 (mục 6b) — guard edit-scope cho re-route Replace (`Bug-ReplaceInCombo-TabJump`). T0 2 việc (K2Node export `OnMeshSelected` + Print xác nhận giả thuyết, 3-strike rule), Q9 S-Scan+X-Check, hàm mới `ShouldRouteReplaceToCombo()`, đổi đúng 1 call site trong `OnMeshSelected`, 6 case test (case 4 = chống regression P2), mục DẠY thử nghiệm lần 2. **CHƯA test — task card mới phát hành, chờ T0 + 6/6 PASS.** |
| 1.2 | 04/08/2026 | Phát hành task card T3 (mục 7b, đánh số `7b` để né mục `## 8. COMMAND BLOCK` sẵn có) — dialog 2 nút Save As/Save đè. Scope thật rộng hơn dòng khung mục 3 (3 asset, không chỉ `WBP_SaveComboDialog`) — thêm ghi chú dưới bảng mục 3. 2 Function mới (`GetComboViewByID`, `BuildSaveDialogPrefill`), Q9 bắt ca "2 nguồn sự thật lệch nhau" (`bCanOverwrite` vs `bFound`), bẫy UMG tooltip-trên-button-disabled (7b.5, phải test trước khi code UI), 8 case test, mặt cắt bàn giao T4/T5 + T0 sơ bộ T4. **CHƯA test — task card mới phát hành.** ⚠️ Mục A của delta nguồn (K2Node export `CB_SaveCombo_Handler` 04/08) KHÔNG merge vào `BP_FurnitureInputManager.md` — xung đột với section as-built đã có (khác cấu trúc guard + thiếu bước `ContextMenuRef.Hide`), báo cáo cả 2 bản, chờ cuhoang chọn — xem `DEVIATIONS.md` mục "[CONFLICT] CB_SaveCombo_Handler — 2 bản không khớp — 04/08/2026". *(Đóng sau đó cùng ngày — xem `DEVIATIONS.md` mục "[DOC-DEBT đã đóng]": không phải xung đột thật, doc cũ chỉ thiếu 2 bước.)* |
| 1.3 | 04/08/2026 | Thêm mục 4.1 — quyết định kiến trúc cho T4 (verify Lô A, `DELTA_04-08-2026_LoA_SaveCombo_Verify.md`): nối `SaveComboFromSelection` bằng 1 Branch tại điểm sinh `ComboID` (2 param mới `bOverwrite`/`OverwriteComboID`), KHÔNG viết primitive C++ mới. **CHƯA thực thi, không phải task card.** Nguồn xác nhận: `UComboSerializer` không có hàm ghi-đè-combo/`LoadCombo` — xem `Data/ComboSerializer_Reference.md`. |
| 1.4 | 04/08/2026 | Mục 6b.5 (test T2) case 6 — thêm banner `📌 [CHỨA AS-BUILT]`: bằng chứng Print thật (`RowName=CLAMP_table_karkas_005`, không còn `None`) sau Replace→Move→Undo→Replace lại, đến từ fix `RestoreSnapshot.RowName` (xem `Blueprints/BP_UndoManager.md` v1.14) — KHÔNG phải từ T0 của chính T2. **T2 vẫn CHƯA đóng** — 5/6 case + T0 (K2Node export `OnMeshSelected`) chưa có bằng chứng. Bug mới `Bug-RowName-MissingInClipboard` (chưa verify) ghi vào `Bugs/Open_Bugs.md`. |
| 1.5 | 04/08/2026 | **T2 ĐÓNG (mục 6b).** 6/6 case test PASS, điền bảng kết quả thật. `ShouldRouteReplaceToCombo()` (✓K2 03/08) merge as-built vào `BP_FurnitureInputManager.md` v3.3; `OnMeshSelected` merge as-built vào `WBP_FurnitureInventory.md` v3.20 (đổi đúng 1 node nguồn, giữ nguyên 2 node đích). Đóng `Bug-ReplaceInCombo-TabJump` cho call site `OnMeshSelected`. ⚠️ **KHÔNG xác nhận được** claim "call site thứ 2 = `CB_Replace`" — section `CB_Replace` hiện tại không có node route-combo nào để thay, không có ground truth cho 1 thay đổi ở đó — ghi nhận mâu thuẫn ở cả `BP_FurnitureInputManager.md` v3.3 lẫn `Bugs/Open_Bugs.md`, không tự sửa. Mở task card T3 tiếp theo (đã phát hành từ trước, mục 7b). |
| 1.6 | 04/08/2026 | **Đóng caveat v1.5 — `CB_Replace` re-export ✓K2 03/08/2026.** Amendment cuhoang: bản mô tả 24/07 cũ đọc lúc CHƯA re-export sau T2, không phải code thật thiếu nhánh route combo. `CB_Replace` merge as-built vào `BP_FurnitureInputManager.md` v3.4 — bản 24/07 đánh `[SUPERSEDED]` giữ lịch sử, không xóa. Xác nhận đủ 2 call site T2, test 2 trial chuột phải PASS 03/08. `Bugs/Open_Bugs.md` mục `Bug-ReplaceInCombo-TabJump`: gỡ caveat, đóng hoàn toàn. |
