# Kế hoạch Save As / Save đè combo — Execution Plan

**Phiên bản:** 1.0 — 03/08/2026
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
