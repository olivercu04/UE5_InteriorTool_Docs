# Open Bugs — Bugs đang mở
**Tạo từ:** `00_Core/DEVIATIONS.md` (mục BUGS DEFERRED) + `00_Core/01_Session_State.md` (BUG CÒN MỞ) + `00_Core/02_Current_Sprint.md` (bối cảnh Gate 1)
**Cập nhật:** 20/07/2026 — P2 Gate D sweep: 2 bug kiến trúc mới (dome curvature + Ceiling ground-align) — chờ Fable/Opus quyết

---

## Tổng quan

| # | Bug | Ưu tiên | Sprint/Gate xử lý |
|---|---|---|---|
| B1 | ✅ FIXED (16/06) — Undo lần 2 không restore group state | — | Đóng Gate 1, xem BP_UndoManager.md v1.9-1.10 |
| B-gizmo | Gizmo ẩn sau undo trong edit mode (pre-existing) | 🟢 Thấp | Known issue, chưa có timeline |
| B-folder | ✅ FIXED (17/06, D.T6) — Replace folder sai khi group nhiều mesh khác folder | — | OnMeshSelected nay đọc RowName→DT, không cần load DAPath. Xem WBP_FurnitureInventory.md v2.5 |
| B-stale-popup | ✅ FIXED (17/06, D.T6) — Popup hiển thị thông tin đồ cũ | — | Xem mục bên dưới |
| Bug-Pagination | ✅ FIXED (17/06, D.T9) — Furniture pagination dừng ở 7/8 thay vì 8/8 | — | Xem WBP_FurnitureInventory.md v2.6, mục Pagination |
| Bug-Maximize | ✅ FIXED (17/06, D.T9) — BTN_Maximize không nhảy về góc trên-trái | — | Xem WBP_ResizeWindow.md v1.1 |
| K3 | SpawnFurnitureCopy gọi AddRecentMesh unconditional → spawn combo nhồi 20 mesh lẻ vào Recent + mỗi Undo cũng nhồi | 🟡 Trung bình | Planned — Sprint 5, áp lúc đụng C2/RestoreSnapshot. Fix: param bAddToRecent |
| Bug-SaveConfirm-EmptyName | WBP_SaveComboDialog: BTN_Confirm không disable khi tên combo trống nếu user chưa gõ gì | 🟡 Trung bình-Thấp | Phát hiện REG C5.8 khối A6 (13/07) — ngoài scope C5.8, chưa fix |
| Bug-MoveFolder-Collision | Move Folder: không check trùng tên khi đích đã có con cùng tên với folder đang move | 🟡 Trung bình | Phát hiện REG C5.8 khối A7 (13/07) — backlog, task riêng ngoài scope C5.8 |
| Task-RegenThumbnails | Regenerate all thumbnails cho combo library cũ (sau P2.F) | 🟢 Thấp | Backlog 16/07 — combo lưu trước P2 vẫn có ảnh capture kiểu cũ (không phải Studio Look), cần công cụ batch regenerate sau khi P2 Gate F đóng |
| Bug-DomeCurvature-FootprintRong | ✅ FIXED (20/07) — dome custom (đồng nghiệp dựng) thay sphere engine, đáy phẳng bo cong bán kính ~500 unit | — | Test PASS combo Dẹt (thảm) + To (sofa 15 món, footprint lớn nhất từng có) trên dome mới. Xem DEVIATIONS mục "P2 — 20/07/2026 (Dome Custom)" |
| Bug-CeilingGroundAlign | Combo "Cao" (surfaceType Ceiling) bị ground-align kéo xuống sàn sai, giống lỗi Tường (H1) nhưng chưa từng ghi | 🔴 Cao | Chờ Fable/Opus quyết kiến trúc, gộp cùng H1 — phát hiện Gate D sweep 20/07 |

---

## B1 — Undo lần 2 không restore group state

**ID:** B1
**Phát hiện:** Sprint 3 (carry-over sang Gate 1)
**Ưu tiên:** 🔴 Cao

### Triệu chứng
Undo lần 1 restore group ĐÚNG. Undo lần 2 → `Groups.Length = 0` — group biến mất.

### Bối cảnh kỹ thuật
Chữ ký của bug: "trạng thái bị sửa TRONG quá trình restore lần 1."

**Giả thuyết (từ Gate1_SprintD_Execution_Opus.md G1.T1):**
- **H1 (nghi phạm số 1):** `RestoreSnapshot` Step 5/6b gọi `SelectActors` để re-fire selection → listener của `OnSelectionChanged` gọi `CaptureSnapshot` → snapshot MỚI bị chèn vào history GIỮA restore → redo stack bị cắt + CurrentIndex lệch → Undo lần 2 trỏ sai snapshot.
- **H2:** snapshot đích của Undo lần 2 thật sự lưu Groups rỗng (capture còn hở 1 đường — vd nhánh fail của `GetGroupsForSnapshot`).
- **H3:** có thứ CLEAR `InputManager.Groups` SAU Step 5b (listener `OnRestoreCompleted` hoặc `SyncGroupsToContainer` chạy ngược chiều).

### Fix theo kế hoạch (Gate 1 G1.T1)

**Variable mới:** `BP_UndoManager.bIsRestoring : Boolean` (default False, KHÔNG SaveGame)

**RestoreSnapshot — 2 chỗ chèn:**
```
Ngay SAU Function Entry (TRƯỚC Step 1 DeselectAll):
  SET bIsRestoring = True

Ngay TRƯỚC Step 7 (Broadcast OnRestoreCompleted):
  SET bIsRestoring = False
```

**CaptureSnapshot — guard đầu hàm:**
```
TRƯỚC Step 0 (CLEAR TempSelectedIndices):
  Branch (bIsRestoring == True):
    True  → Return (thoát hàm, không capture)
    False → tiếp tục Step 0 như cũ
```

**Diagnostic Prints:**
```
Đầu RestoreSnapshot: "RST idx={IndexHistory} act={ActionName} ver={Version} grp={Groups.Length} hist={History.Length}"
Cuối RestoreSnapshot: "RST-END mgr.Groups={InputManager.Groups.Length} hist={History.Length}"
```

### Test B1
```
Select 3 đồ → Ctrl+G → Move cả group → Undo → Undo
1. Sau Undo lần 2: info bar hiện group, log "RST-END mgr.Groups" > 0  → FIXED
2. "hist" đầu vs cuối MỖI lần restore phải BẰNG nhau
3. Regression: Undo/Redo xen kẽ Select/Deselect vẫn đúng
4. Redo sau 2 Undo → quay lại đúng trạng thái
```

**Nếu vẫn fail sau fix bIsRestoring:**
- `grp=0` ngay đầu → H2 → soi snapshot theo ActionName, kiểm tra GetGroupsForSnapshot
- `grp>0` đầu nhưng `mgr.Groups=0` cuối → H3 → tìm thứ clear Groups sau Step 5b
- Fail 3 lần → STOP, báo cuhoang, không đoán mò

### Trạng thái
- **✅ RESOLVED — 16/06/2026.** Fix bằng bIsRestoring guard trong BP_UndoManager (xem BP_UndoManager.md v1.9) + hợp nhất spawn path qua SpawnFurnitureCopy (v1.10).

---

## B-gizmo — Gizmo ẩn sau undo trong edit mode (pre-existing)

**ID:** B-gizmo
**Phát hiện:** Sprint 4 Bug Fix session (15/06/2026) — xác nhận là **pre-existing**, không phải regression
**Ưu tiên:** 🟢 Thấp

### Triệu chứng
Khi đang ở Edit Mode (đang edit 1 group), thực hiện Undo → gizmo biến mất dù tool vẫn đang ở Move mode.

### Phân tích
- Sprint 4 Bug Fix xác nhận: đây là bug **PRE-EXISTING** có từ trước Sprint 4, không phải do Sprint 4 gây ra.
- Không phải regression của các fix F1-F4 hoặc A12.
- Cơ chế: ValidateEditMode trong RestoreSnapshot kiểm tra EditModeStack, nhưng gizmo visual state không được restore đúng sau Undo khi đang trong edit scope.

### Trạng thái
- **Known issue.** Chưa có timeline fix.
- Không ảnh hưởng đến functionality cốt lõi (vẫn move được, chỉ gizmo không hiển thị).
- **Workaround:** click ra ngoài → click lại actor → gizmo hiện trở lại.
- Ghi nhận trong `00_Core/DEVIATIONS.md` mục BUGS DEFERRED (B3-gizmo).

---

## B-folder — Folder sai khi group nhiều mesh khác folder

**ID:** B-folder (Replace folder bug)
**Phát hiện:** Sprint 4 (12/06/2026)
**Ưu tiên:** 🟢 Thấp

### Triệu chứng
Khi Replace Mesh trên 1 actor thuộc group có nhiều mesh từ các folder khác nhau → WBP_FurnitureInventory navigate sai folder trong inventory (không nhảy đúng folder của mesh đang được replace).

### Root cause (từ DEVIATIONS.md)
`OnMeshSelected` Trigger 3 (Replace navigate folder): Load Asset Blocking(DAPath) → GET MeshFolderPath → navigate folder. Khi group có nhiều mesh từ nhiều folder khác nhau, path được dùng không phải của mesh cụ thể đang replace mà là primary actor hoặc mesh cuối cùng xử lý.

### Fix theo kế hoạch (Sprint D D.T6)
Từ Sprint D, thay đổi nguồn đọc folder:
```
CŨ: Load Asset Blocking(DAPath) → GET MeshFolderPath
MỚI: Cast actor → GET RowName → Get Data Table Row → MeshFolderPath
```
Nếu actor cũ chưa có RowName (save cũ) → fallback đường DAPath cũ (Branch RowName == None).

### Trạng thái
- **✅ RESOLVED — 17/06/2026 (Sprint D.T6).** `OnMeshSelected` Replace branch nay đọc `RowName` → `DT_FurnitureCatalog` → `MeshFolderPath` trực tiếp (không cần `Load Asset Blocking(DAPath)`). Fallback DAPath vẫn còn cho save cũ (Branch RowName == ""). Xem `WBP_FurnitureInventory.md` v2.5.

---

## B-stale-popup — Popup hiển thị đồ cũ sau click

**ID:** B-stale-popup
**Phát hiện:** Sprint D.T6 (17/06/2026)
**Ưu tiên:** 🟡 Trung bình (UX)

### Triệu chứng
Bấm vào một đồ → BTN_Info hoặc UpdateDetailPopup hiển thị popup với thông tin đồ **trước đó** (không phải đồ vừa chọn). Cụ thể: popup refresh trước khi selection thực sự xác nhận ở OnLMBReleased.

### Root Cause
`UpdateDetailPopup` được nối tạm vào **Mouse Left Pressed Step 11** (sau khi blueprint được thêm tính năng). Tại thời điểm đó, `SelectedFurnitureActor` chưa được SET (selection chốt ở `OnLMBReleased`, không phải `Mouse Left Pressed`) → popup đọc actor cũ.

### Fix (Sprint D.T6)
- **Xóa Step 11** khỏi Mouse Left Pressed.
- **`UpdateDetailPopup`** rewrite: Custom Event, bound to `OnSelectionChanged` trong WBP_MeshControls Event Construct. Nhận `Primary : BP_FurnitureActor` → GET RowName → InitPopup(RowName). Chỉ update nếu `DetailPopupRef` đang mở.
- **BTN_Info**: đọc `RowName` trực tiếp từ `SelectedFurnitureActor` (không load asset blocking nữa).

### Trạng thái
- **✅ RESOLVED — 17/06/2026 (Sprint D.T6).** Xem `WBP_MeshControls.md` v1.7 + `BP_FurnitureInputManager.md` v1.10.

---

## Bug-Pagination — Furniture pagination dừng sớm 1 trang

**ID:** Bug-Pagination
**Phát hiện:** Sprint D.T9 regression (17/06/2026) — test case 1
**Ưu tiên:** 🟡 Trung bình (UX)

### Triệu chứng
Furniture: browse 337 item, PageSize=48 → kỳ vọng "8/8" trang. Thực tế: Next nút đúng 7 lần rồi dừng tại "7/8" — không qua trang 8 được.

### Root Cause
2 chỗ tính `TotalPages` dùng công thức khác nhau:
- `DisplayPage`: `Int to Float → ÷ → Ceil` (Float divide, đúng): 337/48 = 7.02 → Ceil = 8
- Next-page check: Int Divide trực tiếp (sai): 337÷48 = 7 (mất phần dư)

2 chỗ lệch nhau 1 → Next bị block ở trang 7, DisplayPage hiển thị "8/8" nhưng Next không hoạt động.

### Fix (Sprint D.T9)
Chèn `Int to Float` giữa LENGTH và input A của node `÷` ở nhánh Next-page check,
ở CẢ 2 nhánh Material và Furniture (cấu trúc copy giống nhau).

```
CŨ:  LENGTH ●→ ÷.A (Int) | PageSize ●→ ÷.B → Ceil
MỚI: LENGTH ●→ Int to Float ●→ ÷.A (Float) | PageSize ●→ ÷.B → Ceil
```

### Trạng thái
- **✅ RESOLVED — 17/06/2026 (Sprint D.T9).** Xem `WBP_FurnitureInventory.md` v2.6 mục Pagination.

---

## Bug-Maximize — BTN_Maximize không nhảy về góc trên-trái

**ID:** Bug-Maximize
**Phát hiện:** Sprint D.T9 regression (17/06/2026) — test case 1
**Ưu tiên:** 🟡 Trung bình (UX)

### Triệu chứng
Bấm BTN_Maximize → cửa sổ nở đúng size nhưng vẫn ở vị trí cũ (không nhảy về góc trên-trái (0,0)).

### Root Cause
Cả 2 nhánh Maximize/Restore chỉ gọi `Set Size` trên Canvas Slot của `VerticalBox_0`.
`Set Position in Viewport(self, ...)` không có tác dụng vì vị trí cửa sổ thật được điều
khiển qua Canvas Slot Position của `VerticalBox_0` (theo logic drag title bar có từ trước).

### Fix (Sprint D.T9)
Thêm `Set Position` vào cùng node `Slot as Canvas Slot(VerticalBox_0)` đang nuôi `Set Size`:
- Nhánh Maximize (True): Position = (0,0)
- Nhánh Restore (False): Position = Original Position

`Set Position in Viewport(self,...)` giữ nguyên — không xóa, không ảnh hưởng.

### Trạng thái
- **✅ RESOLVED — 17/06/2026 (Sprint D.T9).** Xem `WBP_ResizeWindow.md` v1.1.

---

## K3 — SpawnFurnitureCopy nhồi Recent khi spawn combo + Undo

**ID:** K3 (bAddToRecent)
**Phát hiện:** 23/06/2026 — phân tích C2 SpawnComboByID
**Ưu tiên:** 🟡 Trung bình (UX)

### Triệu chứng
1. Spawn combo 5 món → Recent bị nhồi 5 mesh lẻ thành phần (không phải entry "combo", chỉ là các mesh con).
2. Undo → Recent lại bị nhồi thêm (RestoreSnapshot gọi SpawnFurnitureCopy → AddRecentMesh).

### Root Cause
`SpawnFurnitureCopy` gọi `AddRecentMesh` unconditional. Không có gate để bỏ qua khi spawn trong context không cần Recent (combo spawn, Undo restore). Bug tồn tại từ trước Sprint 5, không chỉ ở combo.

### Fix kế hoạch
`SpawnFurnitureCopy` thêm param `bAddToRecent : Boolean = True`:
- Trong thân: `Branch(bAddToRecent)` → True: gọi AddRecentMesh; False: bỏ qua.
- Spawn combo (C2): truyền `bAddToRecent = False`.
- RestoreSnapshot: truyền `bAddToRecent = False` (Undo không nên đụng Recent).
- Paste/Duplicate: giữ `True` (hành vi đúng).

### Trạng thái
- **Planned.** Áp lúc đụng C2/RestoreSnapshot trong Sprint 5.
- **[16/07/2026]** Hạ tầng param `bAddToRecent` ĐÃ CÓ từ P2 Gate A Việc 1 (`docs/Plans/P2_StudioThumbnail_Execution.md`) — thêm param + Branch bọc Add Recent Mesh. Còn lại: các call site `SpawnFurnitureCopy` KHÁC (ngoài combo thumbnail) cân nhắc truyền `bAddToRecent` phù hợp (vd RestoreSnapshot → False). Chưa audit hết call site.

---

## Bug-SaveConfirm-EmptyName — BTN_Confirm Save dialog không disable khi tên trống chưa gõ gì

**ID:** Bug-SaveConfirm-EmptyName
**Phát hiện:** REG C5.8 khối A6, 13/07/2026
**Ưu tiên:** 🟡 Trung bình-Thấp

### Triệu chứng
`WBP_SaveComboDialog`: nếu user CHƯA gõ gì vào ô tên combo (chỉ để trống từ đầu), `BTN_Confirm` vẫn Enabled — save được combo không tên.

### Root Cause
`ValidateComboName` chỉ bind vào `OnTextChanged(TextBox_ComboName)` — không tự chạy ở Event Construct. Nếu user không gõ gì, hàm chưa từng được gọi → `BTN_Confirm` giữ trạng thái mặc định Designer (Enabled=True).

Bug có sẵn từ C3b (24/06/2026) — KHÔNG phải do Wire Save C5.8, chỉ mới lộ ra lúc test REG.

### Fix đề xuất
Gọi `ValidateComboName` (hoặc `Set Is Enabled(BTN_Confirm, false)` trực tiếp) ngay trong Event Construct, không chỉ chờ `OnTextChanged`.

### Trạng thái
- **Open.** Ngoài scope C5.8 — không sửa trong đợt này.

---

## Bug-MoveFolder-Collision — Move Folder không check trùng tên khi đích đã có con cùng tên

**ID:** Bug-MoveFolder-Collision
**Phát hiện:** REG C5.8 khối A7, 13/07/2026
**Ưu tiên:** 🟡 Trung bình

### Triệu chứng
Move folder tới đích mà đích đã có sẵn 1 con cùng tên với folder đang move — không có cảnh báo/chặn.

### Root Cause
`RenameFolderPrefix` (C++) không validate collision trước khi ghi path mới — nếu 2 path cuối cùng trùng nhau sau move, dữ liệu combo/folder có thể chồng lẫn trong `Folders.json` / file combo `.json` (chưa rõ mức độ hỏng — cần điều tra thêm nếu ưu tiên làm sớm).

### Fix đề xuất (backlog, task riêng)
Validate collision (ở Blueprint trước khi gọi `RenameFolderPrefix`, hoặc thêm check trong chính hàm C++) + UX báo lỗi cho user (toast "đã tồn tại folder cùng tên" hoặc auto-merge). Ngoài scope C5.8 — component chỉ hiển thị/chọn, không có logic validate move.

### Trạng thái
- **Open / Backlog.** Data integrity risk nhưng case hiếm (cần cùng tên folder ở 2 nhánh khác nhau của cây). Ngoài scope C5.8.

---

## Task-RegenThumbnails — Regenerate all thumbnails cho combo library cũ

**ID:** Task-RegenThumbnails
**Phát hiện:** 16/07/2026 — chốt plan P2 Studio Thumbnail
**Ưu tiên:** 🟢 Thấp

### Bối cảnh
P2 (`docs/Plans/P2_StudioThumbnail_Execution.md`) đổi kiến trúc capture sang "Studio Look"
(Remote Studio, đèn chuẩn hóa, Manual EV100). Combo đã lưu TRƯỚC khi P2 xong (Gate F đóng)
vẫn giữ PNG capture kiểu cũ (P1, chụp tại vị trí thật trong phòng) — không đồng bộ hình ảnh
với combo mới.

### Việc cần làm (chưa có plan chi tiết)
Công cụ/flow batch: với mỗi combo cũ trong `Saved/Combos/`, gọi lại
`SpawnComboForThumbnail` + capture pipeline mới, ghi đè PNG, `InvalidateThumbnail` cache.

### Trạng thái
- **Backlog.** Chỉ làm SAU khi P2 Gate F đóng (pipeline Studio Look ổn định). Task riêng,
  chưa có execution plan.

---

## Bug-DomeCurvature-FootprintRong — Dome cong nuốt chân đồ combo footprint rộng

**ID:** Bug-DomeCurvature-FootprintRong
**Phát hiện:** P2 Gate D sweep, 20/07/2026
**Ưu tiên:** 🔴 Cao

### Triệu chứng
Combo To (sofa, footprint bán kính ~210 unit) — phần chân/đế sofa ở rìa xa tâm bị dome "nuốt"
(che khuất bởi mặt cong dome). Combo Dẹt (thảm, footprint ~204) — lỗi nặng hơn nhiều, gần như
mất toàn bộ hình ảnh vật thể (nghi cùng root cause, mức độ khác do tỉ lệ Radius/kích thước vật
thể — CHƯA xác nhận bằng số).

### Root cause
Dome là sphere R=2000, `Location.Z = Anchor.Z + R` → Anchor chỉ trùng đáy dome tại ĐÚNG 1 điểm
(tâm trục X/Y=0). Càng ra xa tâm theo bán kính ngang `r`, mặt trong sphere càng dâng cao hơn:
`ΔZ = R − √(R² − r²)`. Ground-align hiện tại (`SpawnComboForThumbnail`) chỉ tính 1 `DeltaZ` duy
nhất cho CẢ combo (dựa trên điểm thấp nhất), coi "sàn" là mặt phẳng — nhưng mặt dome không
phẳng. Với combo sofa: `ΔZ ≈ 11 unit` — đủ để dome che chân/đế ở rìa.

Nguồn gốc kiến trúc: Gate A có sàn phẳng tạm (StaticMeshActor Plane). Gate B (17/07) bỏ hẳn
plane này, dùng đáy dome làm sàn — hợp lý cho combo nhỏ/gọn, vỡ trận với combo footprint rộng.
Review Fable (16/07) diễn ra TRƯỚC quyết định Gate B (17/07) — không phải Fable bỏ sót.

### Đề xuất (chưa chọn — cần Fable/Opus quyết)
1. Thêm lại đĩa sàn phẳng nhỏ (khôi phục Gate A), bán kính đủ bao combo lớn nhất thư viện,
   material khớp màu dome.
2. Tăng `Cmb_StudioDomeRadius` (2000→5000+) — giảm độ cong tại cùng bán kính footprint, không
   giải quyết tận gốc cho combo cực rộng tương lai.
3. Chấp nhận known-limitation cho nhóm combo rộng — không khuyến nghị (sofa phổ biến nhất).

Cần xác nhận thêm: Print `Radius`/`Distance` trong `BeginComboCapture` khi chụp lại combo Dẹt,
để xác nhận có cùng root cause với sofa hay là bug khác.

### Trạng thái
- **✅ FIXED 20/07/2026.** Đồng nghiệp dựng dome custom (cylinder kín, đáy bo cong, thay
  `/Engine/BasicShapes/Sphere` cũ). Vùng đáy phẳng tuyệt đối trong bán kính ~500 unit — đủ bao
  mọi combo Floor hiện có trong thư viện. Test PASS: combo Dẹt (thảm tròn 3200mm, fail nặng nhất
  lần trước) + combo To (sofa 15 món, boundingBoxExtent X/Y ≈ 193/186 — trải rộng nhất từng
  test). Cả 2 chân/đế chạm sàn phẳng, không hở/chìm ở bất kỳ góc nào. Chi tiết kiến trúc + verify
  Cast Shadow: `DEVIATIONS.md` mục "P2 — 20/07/2026 (Dome Custom)".

---

## Bug-CeilingGroundAlign — Combo "Cao" (Ceiling) dính lỗi ground-align giống "Tường" (H1)

**ID:** Bug-CeilingGroundAlign
**Phát hiện:** P2 Gate D sweep, 20/07/2026
**Ưu tiên:** 🔴 Cao

### Triệu chứng
Combo test "Cao" (`combo_057470B142B9C11BF66D2CBC23EFEE31` — 3 item `surfaceType: "Ceiling"`:
quạt trần, điều hòa âm trần) — ground-align hiện tại kéo CẢ cụm xuống chạm "sàn" (đáy dome), sai
hoàn toàn với đồ gắn trần (đáng lẽ neo phía TRÊN). Ảnh chụp thực tế còn cho dấu hiệu các item
trong cùng combo KHÔNG cùng mặt phẳng sau ground-align (bóng đổ tách rời) — CHƯA điều tra sâu.

### Root cause
Ground-align không phân biệt `surfaceType` — áp dụng chung 1 công thức "neo xuống sàn" cho mọi
combo. Plan gốc (H1) chỉ ghi known-limitation cho case `surfaceType: "Wall"`, case `"Ceiling"`
chưa từng được nhắc tới dù chung 1 lỗi kiến trúc.

### Đề xuất
Gộp quyết định H1 (Wall) và bug này (Ceiling) cùng lúc — vd bỏ qua ground-align nếu TOÀN BỘ item
trong combo có `surfaceType` khác `"Floor"`.

### Trạng thái
- **Open.** Chờ Fable/Opus quyết kiến trúc, gộp cùng lúc với H1. Gate D sweep tạm dừng chờ
  hướng đi. Xem `DEVIATIONS.md` mục "P2 — 20/07/2026".

---

## Closed Bugs (reference nhanh)

| # | Bug | Sprint | Fix |
|---|---|---|---|
| Bug 2 | GroupID lost sau Replace Mesh | Sprint 4 | SET NewActor.GroupID = OldActor.GroupID trong Replace loop |
| Bug 3 | Branch anchor != "" nhầm thành ancestor === "" | Sprint 4 | Sửa trong ResolveSelectionUnit |
| F1 | Info bar hiển thị sai unit name | Sprint 4 BugFix | GetSelectionUnitLabel trong BP_FurnitureInputManager v1.9 |
| F2 | Group name counter không monotonic | Sprint 4 BugFix | GroupNameCounter → BP_GroupsContainer (SaveGame=True) |
| F3 | CreateGroup không nested bottom-up | Sprint 4 BugFix | ComputeSelectionUnits + rewrite CreateGroup |
| F4 | Spawn không auto-join edit scope | Sprint 4 BugFix | SpawnFurnitureCopy + WBP_DragOverlay On Drop |
| A12 | Edit mode bar ẩn sau Undo | Sprint 4 BugFix | EditModeStack vào S_SceneSnapshot V=4 |
| B-folder | Replace folder sai khi group nhiều mesh khác folder | Sprint D.T6 | OnMeshSelected RowName→DT thay DAPath. WBP_FurnitureInventory v2.5 |
| B-stale-popup | Popup hiển thị đồ cũ sau click | Sprint D.T6 | UpdateDetailPopup bound to OnSelectionChanged. WBP_MeshControls v1.7 |
| Bug-Pagination | Furniture pagination dừng sớm 1 trang (7/8 thay vì 8/8) | Sprint D.T9 | Int to Float trước Ceil ở Next-page check. WBP_FurnitureInventory v2.6 |
| Bug-Maximize | BTN_Maximize không nhảy về góc trên-trái | Sprint D.T9 | Set Position thêm vào Slot VerticalBox_0. WBP_ResizeWindow v1.1 |
