# Open Bugs — Bugs đang mở
**Tạo từ:** `00_Core/DEVIATIONS.md` (mục BUGS DEFERRED) + `00_Core/01_Session_State.md` (BUG CÒN MỞ) + `00_Core/02_Current_Sprint.md` (bối cảnh Gate 1)
**Cập nhật:** 02/08/2026 — Replace UX Fix P0→P5 HOÀN TẤT: #1/#3a/#3b/#4/#5/#6 đều FIXED. Bug mới
ghi nhận ngoài scope: Bug-EnterReplaceMode-MaterialPanel [OPEN, 🟢 Thấp]. P-5 (DA-legacy-path)
gác lại — thiếu file save cũ để test.
**Cập nhật (tiếp) 02/08/2026:** Thêm 3 bug xác nhận bằng test tay trong editor (phiên bàn kiến
trúc với Opus, luật Q9): Bug-MaterialPrimaryOnly, Bug-PasteVerticalCollapse, Bug-StaleSurfaceType
— cả 3 KHÔNG chặn Gate 2, dời sau Gate 2. Thêm mục "Ô nghi ngờ chưa verify" (N1-N14, rút từ đọc
docs, chưa chạy test).
**Cập nhật (tiếp) 02/08/2026 (R-DOC-DONE):** Thêm 2 entry tách từ PROGRESS.md khi tick DONE P2/P1
theo luật `R-DOC-DONE`: Task-P2-SweepCao (case Cao chưa test combo thật), Task-P1-VRAMRegression
(G5 VRAM chưa đo được) — cả 2 🟢 Thấp, không chặn Gate 2.

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
| K3 | ✅ RESOLVED (21/07) — pin `bAddToRecent=False` tại 2 call site còn thiếu: `RestoreSnapshot` (BP_UndoManager) + `SpawnComboByID` (BP_ComboManager) | — | Verify qua Blueprint Export Method (K2Node text) + screenshot thật. 4 case test PASS |
| Bug-SaveConfirm-EmptyName | WBP_SaveComboDialog: BTN_Confirm không disable khi tên combo trống nếu user chưa gõ gì | 🟡 Trung bình-Thấp | Phát hiện REG C5.8 khối A6 (13/07) — ngoài scope C5.8, chưa fix |
| Bug-MoveFolder-Collision | Move Folder: không check trùng tên khi đích đã có con cùng tên với folder đang move | 🟡 Trung bình | Phát hiện REG C5.8 khối A7 (13/07) — backlog, task riêng ngoài scope C5.8 |
| Task-RegenThumbnails | Regenerate all thumbnails cho combo library cũ (sau P2.F) | 🟢 Thấp | Backlog 16/07 — combo lưu trước P2 vẫn có ảnh capture kiểu cũ (không phải Studio Look), cần công cụ batch regenerate sau khi P2 Gate F đóng |
| Task-P2-SweepCao | Combo "Cao" (kệ/tủ cao) cho Studio Thumbnail chưa test bằng combo thật — chỉ PASS SƠ BỘ bằng stack dựng tay | 🟢 Thấp | Tách khỏi P2 Gate D (02/08, R-DOC-DONE — P2 đã tick DONE trong PROGRESS.md). Đóng khi có combo kệ/tủ cao thật để test lại. Không chặn Gate 2 |
| Task-P1-VRAMRegression | P1.G5 — regression VRAM cho Thumbnail System C++ chưa đo được (phương pháp đo bị nhiễu, cần RenderDoc/Nsight) | 🟢 Thấp | Tách khỏi P1 (02/08, R-DOC-DONE — P1 đã tick DONE trong PROGRESS.md). Không chặn Gate 2 |
| Feature-CanonicalStudioAngle | Thumbnail combo chụp theo góc user đặt+nhìn → không đồng bộ catalogue (sofa chữ U chụp trúng lưng, quạt chắn giữa). Cần "nắn về góc chuẩn" / user chọn mặt trước | 🟢 Thấp | Sprint 6 — Polish UX |
| Bug-DomeCurvature-FootprintRong | ✅ FIXED (20/07) — dome custom (đồng nghiệp dựng) thay sphere engine, đáy phẳng bo cong bán kính ~500 unit | — | Test PASS combo Dẹt (thảm) + To (sofa 15 món, footprint lớn nhất từng có) trên dome mới. Xem DEVIATIONS mục "P2 — 20/07/2026 (Dome Custom)" |
| Bug-CeilingGroundAlign | ✅ FIXED (20/07) — Function `ResolveThumbAlign` (Nấc 1) phân loại Floor/Ceiling/Wall/Other theo `PlacementSurfaceType`, thay công thức "neo xuống sàn" đơn nhất | — | Test 6/6 case PASS. Xem DEVIATIONS mục "P2 — 20/07/2026 (Nấc 1)" |
| Note-DuplicateComboID | Copy tay file `.json` trong Explorer rồi đổi tên → field `comboId` bên trong KHÔNG tự đổi theo tên file → 2 file khác tên nhưng cùng ID logic (Favorite/Recent coi là 1 combo) | 🟢 Thấp | KHÔNG phải bug, không sửa bây giờ — backlog cho tính năng Save As/Save đè combo (chưa có plan) |
| DA-legacy-path (P-5) | [OPEN] StartReplaceMode nhánh DA legacy (RowName=="None") — chưa verify `DA_FurnitureItem.MeshFolderPath` có chứa `"Object_Model/"` giống `DT_FurnitureCatalog` không. Nếu khác format, `Split` trong `FilterByFolderPathWithUI` cắt sai → tree/chip sai khi Replace trên save cũ dùng DA path | 🟢 Thấp | **Gác lại 02/08** (Replace UX Fix P5.2) — thiếu file save cũ thật để test, KHÔNG code mù. Xem mục chi tiết dưới |
| #3a (ComboReplace-Minimize) | ✅ FIXED (01/08) — combo-replace từ minimize: cửa sổ inventory không tự mở lại. `StartReplaceComboMode` thiếu bước un-minimize (nhánh mesh có qua `EnterReplaceMode→EnsureExpanded`, nhánh combo bỏ qua toàn bộ đường đó) | — | Fix: gọi `InventoryRef.EnsureExpanded()` trong `StartReplaceComboMode`. Test T3.3 PASS PIE. Xem `Blueprints/BP_FurnitureInputManager.md` v2.7 |
| #3b (ComboReplace-ChiptagSync) | ✅ FIXED (01/08) — combo-replace: chiptag không rebuild + không highlight đúng (tree/card đúng combo nhưng chiptag vẫn Furniture) | — | Fix: gọi `RefreshChipBreadcrumb()` (hàm có sẵn) NGAY TRƯỚC `UpdateComboFolderHighlights()` trong `StartReplaceComboMode`. Test T1.1 PASS PIE. Xem `Blueprints/BP_FurnitureInputManager.md` v2.7, `DEVIATIONS.md` mục "Replace UX Fix — P1.2" |
| #1, #4, #5, #6 | ✅ FIXED (02/08) — #1 BTN_ChangeCombo gate Visibility; #4 re-route Mesh↔Combo giữa chừng Replace; #5 card container theo mode; #6 chiptag đổi khi click tab Combo | — | Replace UX Fix P1.3/P2/P3.1 — node flow đầy đủ: `Widgets/WBP_FurnitureInventory.md` v3.19 (`OnMeshSelected`), `DEVIATIONS.md` mục "Replace UX Fix — P0→P5 HOÀN TẤT — 02/08/2026" |
| Bug-EnterReplaceMode-MaterialPanel | [OPEN, ngoài scope] Từ tab Material bấm CB_Replace vào Replace Mesh → `CTV_FurnitureCard` bật Visible nhưng `CTV_MaterialCard`/`HB_SlotSwatches` KHÔNG Collapse → 2 panel chồng nhau | 🟢 Thấp | Phát hiện 02/08 qua test P4/T4.1 (Case A). Gác — xem mục chi tiết dưới |
| Bug-MaterialPrimaryOnly | [OPEN] Đổi vật liệu khi chọn cả cụm combo chỉ áp cho 1 mesh (Primary), không toast báo — người dùng tưởng đã đổi cả cụm | 🟡 Trung bình | Test tay 02/08. Vá tạm: toast cảnh báo (~15 phút). Vá thật: gộp Sprint 7 Material Edit multi-apply (E1). Xem mục chi tiết dưới |
| Bug-PasteVerticalCollapse | [OPEN] Paste nhiều món chênh cao độ (đồ trần + đồ sàn) → TÂM nhóm bị neo vào bề mặt trace trúng thay vì từng món neo bề mặt riêng → đồ trần lơ lửng, đồ sàn chìm | 🔴 Cao | Test tay 02/08. KHÔNG chặn Gate 2. Backlog "Sprint Surface" sau Gate 2. Xem mục chi tiết dưới |
| Bug-StaleSurfaceType | [OPEN] Kéo đồ bằng gizmo sang bề mặt khác → `PlacementSurfaceType` không cập nhật lại (chỉ SET 1 lần lúc drag-drop) → nudge phím mũi tên đi sai trục | 🟡 Trung bình | Test tay 02/08. KHÔNG chặn Gate 2. Backlog "Sprint Surface" sau Gate 2. Xem mục chi tiết dưới |

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
- **✅ RESOLVED — 21/07/2026.** Audit đủ 2 call site còn thiếu, pin bằng Blueprint Export Method
  (K2Node text) + screenshot thật, không đoán qua doc:
  - `BP_UndoManager` → `RestoreSnapshot` (Step 4, trong ForEach): node `Spawn Furniture Copy` —
    `bAddToRecent` pin `False` (trước đó mặc định `True`, chưa pin). `bAutoSelect` đã đúng `False`
    từ G1.T2.
  - `BP_ComboManager` → `SpawnComboByID` (Phase 3, node `Spawn Furniture Copy`) — bỏ tick
    checkbox `Add to Recent` (trước đó có tick, chưa pin) → `False`.
  - Paste/Duplicate: KHÔNG đụng — giữ mặc định `True` (đúng hành vi, theo plan gốc).
  Test 4 case PASS: spawn combo 5 món → Recent không đổi; Undo/Redo → Recent không đổi; spawn 1
  furniture từ card → Recent vẫn cập nhật (hành vi cũ); copy/paste 1 actor → Recent vẫn cập nhật
  (hành vi cũ). Chi tiết node flow: `Blueprints/BP_UndoManager.md`, `Blueprints/BP_ComboManager.md`.

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

## Task-P2-SweepCao — Combo "Cao" chưa test bằng combo thật (P2 Gate D)

**ID:** Task-P2-SweepCao
**Phát hiện:** P2 Gate D sweep, 20/07/2026 — tách thành entry riêng 02/08/2026 (luật `R-DOC-DONE`,
P2 đã tick DONE trong `PROGRESS.md`)
**Ưu tiên:** 🟢 Thấp — KHÔNG chặn Gate 2

### Bối cảnh
Sweep 5 loại combo cho Studio Thumbnail: 4/5 loại (Nhỏ/To/Dẹt/Tường) PASS chính thức bằng combo
thật có sẵn trong thư viện. Loại "Cao" (kệ/tủ cao, item Ceiling/trên cao) chỉ PASS SƠ BỘ bằng
cách dựng stack tay (không phải combo tự nhiên có sẵn) — chưa có combo "Cao" thật trong thư viện
để test.

### Trạng thái
- **Open, không chặn gì.** P2 (Studio Thumbnail) đã tick DONE 02/08/2026 theo luật `R-DOC-DONE`
  — tính năng hoạt động, phần nghiệm thu còn treo (case Cao) tách ra đây thay vì giữ task Gate D
  mở. Xem `DEVIATIONS.md` mục "[DOC-DEBT đã đóng] PROGRESS.md P2 self-contradiction — 02/08/2026".
- Đóng khi nào: có combo kệ/tủ cao thật trong thư viện → chạy lại sweep test.

---

## Task-P1-VRAMRegression — Regression VRAM Thumbnail System C++ chưa đo được (P1.G5)

**ID:** Task-P1-VRAMRegression
**Phát hiện:** P1 Gate G5, 15/07/2026 — tách thành entry riêng 02/08/2026 (luật `R-DOC-DONE`, P1
đã tick DONE trong `PROGRESS.md`)
**Ưu tiên:** 🟢 Thấp — KHÔNG chặn Gate 2

### Bối cảnh
G5 (regression VRAM cho pipeline Thumbnail C++ P1) bị DEFERRED 15/07/2026 — phương pháp đo bằng
`stat rhi`/MemReport thô bị nhiễu bởi texture streaming theo camera, không tách được đóng góp
riêng của combo thumbnail. Cần RenderDoc hoặc Nsight để đo chính xác.

### Trạng thái
- **Open, không chặn gì.** P1 (Thumbnail System C++) đã tick DONE 02/08/2026 theo luật
  `R-DOC-DONE` — tính năng hoạt động (G0→G4), phần đo regression còn treo (G5) tách ra đây thay vì
  giữ task P1 mở.
- Đóng khi nào: có công cụ đo VRAM chính xác hơn (RenderDoc/Nsight) rảnh tay để chạy.

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
- **✅ FIXED 20/07/2026 (Gate D Nấc 1).** Function mới `ResolveThumbAlign(Clones) → DeltaZ,
  Category` phân loại Floor/Ceiling/Wall/Other theo `PlacementSurfaceType` thay vì áp 1 công
  thức "neo xuống sàn" đơn nhất cho mọi combo — combo Ceiling giờ neo đúng phía trên thay vì bị
  kéo chìm đáy dome. Gộp chung quyết định với case Wall (H1) như đề xuất ban đầu. Test 6/6 case
  PASS (Floor thuần, Ceiling thuần, bàn thờ Wall+Floor lẫn, Mixed, combo cũ thiếu field,
  Undo/Recent/EMS). Node flow: `Blueprints/BP_ComboManager.md` mục `ResolveThumbAlign`. Chi tiết
  kiến trúc + Wall-priority rule + margin fix: `DEVIATIONS.md` mục "P2 — 20/07/2026 (Nấc 1)".

---

## Feature-CanonicalStudioAngle — Chuẩn hoá góc chụp thumbnail combo

**ID:** Feature-CanonicalStudioAngle
**Phát hiện:** P2 Gate F / optimize framing, 21/07/2026
**Ưu tiên:** 🟢 Thấp — KHÔNG chặn P2/Gate F. Để dành Sprint 6 (Polish UX).

### Bối cảnh
Thumbnail combo chụp theo góc PHỤ THUỘC KÉP: (1) hướng user đặt đồ trong phòng
(RelRotation lưu TUYỆT ĐỐI, không nắn — schema JSON v1) + (2) hướng user đứng nhìn
lúc Save (DeltaYaw = Cmb_StudioCamYaw − Cmb_PendingUserCamYaw). Hệ quả: cùng 1 combo,
user xoay khác nhau khi đặt → thumbnail ra góc khác → không đồng bộ catalogue (mục
tiêu gốc P2: "cảm giác UE Content Browser").

Bằng chứng trực quan (ảnh 21/07): combo phòng khách chụp ra quạt đồng chắn giữa che
sofa; combo khác ghế + minion quay lưng ra trước. Ảnh sản phẩm thật luôn chụp "mặt trước".

### Vì sao KHÔNG fix nhanh được
Máy không có dữ liệu để tự biết "mặt trước". Schema mỗi item chỉ có
RowName/RelLocation/RelRotation/SurfaceType — KHÔNG field nào chỉ hướng chính.
- Đoán bằng hình học (cạnh dài nhất quay ngang): sai với sofa chữ U / combo blob.
- Quy ước cứng theo trục combo: đồ lưu ở góc tùy ý user → trục vô nghĩa.
- → Cách đúng DUY NHẤT: user tự chọn "mặt trước" lúc Save (UI preview xoay + chốt góc).
  Mini-feature, cần plan riêng do Fable/Opus author — KHÔNG phải quick fix.

### Trạng thái hiện tại (chấp nhận tạm)
Sau patch Radius rotation-invariant (21/07) framing đã ổn định (Distance chênh
235→282 giảm còn ~3-6%, mắt thường khó phân biệt). Phần "zoom" đã đủ tốt. Phần "góc
chụp thấy mặt/lưng" (canonical angle) để Sprint 6.

### Hướng làm khi vào Sprint 6 (chưa chốt)
Cách 2 — user chọn mặt trước lúc Save: preview combo trong studio, cho xoay
(phím/scroll), bấm "chụp từ góc này". Cần plan riêng.

> **[MỞ RỘNG PHẠM VI 22/07/2026]** Cùng gốc vấn đề với giới hạn OBB của
> `CalculateComboBoundingExtent` (xem `Blueprints/BP_ComboManager.md` mục Dimension Fix,
> 22/07/2026): Card Dimension hiện tính AABB theo trục THẾ GIỚI nên kích thước dao động theo
> hướng đặt combo trong phòng (đo thực tế: 6.0m² vs 8.2m² cùng 1 combo, chỉ khác hướng xoay).
>
> Cả 2 vấn đề (thumbnail chụp sai góc + Card dimension dao động) đều thiếu ĐÚNG 1 miếng dữ liệu:
> **`ReferenceYaw`** — góc tham chiếu "hướng chuẩn" của combo, chưa từng lưu trong schema.
>
> Khi làm feature này ở Sprint 6 (UI cho user chọn "mặt trước" lúc Save, xoay preview + chốt góc
> — xem "Hướng làm khi vào Sprint 6" ở trên), field `ReferenceYaw` sinh ra lúc đó PHẢI dùng lại
> cho CẢ 2 mục đích:
> 1. Thumbnail: góc camera chuẩn (thay `DeltaYaw` tính từ hướng user đứng nhìn ngẫu nhiên hiện
>    tại).
> 2. Card Dimension: xoay ngược toàn bộ điểm actor quanh `ReferenceYaw` trước khi tính Min/Max
>    (Oriented Bounding Box theo trục combo, thay AABB theo trục thế giới) — L/W/H bất biến theo
>    hướng đặt combo trong phòng.
>
> KHÔNG làm OBB tạm bợ riêng cho Card (vd dùng Yaw món neo) trước khi feature này chốt — tránh
> làm 2 lần, có thể ra 2 hướng tham chiếu khác nhau gây rối.

Mức ưu tiên giữ nguyên 🟢 Thấp / Sprint 6 — không đổi mức ưu tiên, chỉ mở rộng mô tả.

---

## Note-DuplicateComboID — Copy tay file JSON → duplicate comboId

**ID:** Note-DuplicateComboID
**Phát hiện:** C6 testing, 22/07/2026
**Ưu tiên:** 🟢 Thấp — KHÔNG phải bug, ghi nhận làm backlog.

### Bối cảnh
Test bằng cách copy tay file `.json` combo trong Windows Explorer rồi đổi tên file → nội dung
field `comboId` bên trong KHÔNG tự đổi theo tên file → 2 file khác tên nhưng cùng ID logic →
Favorite/Recent (và mọi thứ định danh theo ComboID) coi 2 combo là 1.

### Vì sao KHÔNG sửa bây giờ
Đây là hệ quả tự nhiên của thao tác copy tay ngoài luồng app (không đi qua bất kỳ code path nào
của tool) — không có bug logic cần fix ngay. Cần xử lý đúng lúc làm tính năng **Save As / Save
đè (overwrite)** cho combo — bất kể tính năng đó rơi vào C-item nào (C9 Replace hay 1 mục mới):
- Save As phải luôn sinh `comboId` MỚI (GUID mới).
- Save đè giữ nguyên `comboId` cũ.

### Trạng thái
- **Backlog.** Chưa có plan riêng — ghi lại làm note kèm theo khi task Save As/Save đè được lên
  kế hoạch.

---

## Bug-EnterReplaceMode-MaterialPanel — EnterReplaceMode thiếu Collapse CTV_MaterialCard/HB_SlotSwatches

**ID:** Bug-EnterReplaceMode-MaterialPanel
**Phát hiện:** 02/08/2026, qua test P4/T4.1 (Case A — Replace UX Fix)
**Ưu tiên:** 🟢 Thấp — ngoài scope 6 bug gốc đợt Replace UX Fix.

### Triệu chứng
Từ tab Material bấm `CB_Replace` (vào Replace Mesh) → `CTV_FurnitureCard` bật Visible nhưng
`CTV_MaterialCard` KHÔNG bị Collapse → 2 panel chồng lên nhau → nhìn như tab không đổi (thực
ra `CurrentInventoryMode` đã đổi đúng, chỉ là UI không dọn panel cũ).

### Root cause
`EnterReplaceMode` (`WBP_FurnitureInventory`) chỉ có:
```
SetVisibility(CTV_ComboCard, Collapsed)
SetVisibility(CTV_FurnitureCard, Visible)
```
— không có case cho `CTV_MaterialCard`/`HB_SlotSwatches`.

### Trạng thái
- **Open, gác lại** — không thuộc 6 bug gốc đợt Replace UX Fix. cuhoang chọn gác (option Y,
  không đụng ngay).

### Fix đề xuất (chưa làm)
Thêm 2 dòng `SetVisibility` Collapsed cho `CTV_MaterialCard` + `HB_SlotSwatches` vào
`EnterReplaceMode`, cùng khối `SetVisibility` có sẵn (chèn sau dòng Collapsed `CTV_ComboCard`,
trước dòng Visible `CTV_FurnitureCard` hoặc song song — không ảnh hưởng thứ tự exec hiện có).

---

## DA-legacy-path (P-5) — DA legacy RowNotFound

**ID:** DA-legacy-path / P-5
**Phát hiện:** C9 Replace 30/07/2026, elaborate thêm trong Replace UX Fix P5.2 (02/08/2026)
**Ưu tiên:** 🟢 Thấp

### Nghi vấn
`MeshFolderPath` format khác nhau giữa `DA_FurnitureItem` (cũ, trước Sprint D) và
`DT_FurnitureCatalog` (mới) → `FilterByFolderPathWithUI` cắt path sai (`Split.RightS`) khi
Replace 1 actor từ save cũ (RowName=="None", đi nhánh fallback DAPath trong `StartReplaceMode`).

### Trạng thái
- **Chưa test được** (02/08) — không có file save cũ (tạo trước Sprint D, actor RowName=None)
  để tái hiện. Không code mù.

### Điều kiện mở lại
Khi có save cũ thật, hoặc khi gặp báo lỗi thật từ người dùng dùng save cũ.

### Fix dự kiến (nếu tái hiện)
Normalize path tại `Split.RightS` trong `FilterByFolderPathWithUI` làm nguồn duy nhất. Ceiling:
prefix `"Object_Model/"` hardcode (phương án đã chốt trong `DEVIATIONS.md` `[CLEANUP]` từ trước
đợt Replace UX Fix).

---

## Bug-MaterialPrimaryOnly — Đổi vật liệu cả cụm combo chỉ ăn 1 món

**ID:** Bug-MaterialPrimaryOnly
**Phát hiện:** Test tay 02/08/2026 (xác nhận qua editor thật, không phải suy đoán từ doc)
**Ưu tiên:** 🟡 Trung bình — KHÔNG chặn Gate 2

### Triệu chứng
```
Spawn combo → chọn CẢ cụm → tab Material
→ swatch hiện ra là slot của MỘT mesh trong combo (không phải cả cụm)
→ chọn swatch → click vật liệu
→ chỉ 1 món đổi màu
```

### Root cause
`ApplyMaterial` nhắm `TargetFurnitureActor` = `PrimarySelectedActor` (single), trong khi
`SelectedActors` là multi. Bất đối xứng có từ Change Material v1.1, chưa từng được xem là vấn đề
vì lúc đó chưa có combo.

Nghiêm trọng ở chỗ: không có toast, không có lỗi — người dùng tưởng đã đổi cả cụm.

### Fix đề xuất
- **Vá rẻ (15 phút, không đụng kiến trúc):** thêm toast "Chỉ áp cho món đang chọn chính" khi
  `SelectedActors.Length > 1`. Không sửa hành vi, chỉ hết lừa người dùng.
- **Vá thật:** Sprint 7 Material Edit đã có sẵn plan multi-apply (E1 — ForEach `SelectedActors`
  trong `LoadAndApplyMaterial`). Gộp vào đó, không làm lẻ.

### Trạng thái
- **Open.** Chưa fix trong đợt này (KP3 — chỉ ghi nhận). Xem `DEVIATIONS.md` mục "Q9 S-Matrix
  Gate + 3 bug Surface — 02/08/2026". Xem thêm ghi chú "Gốc chung 3 bug Surface" bên dưới.

---

## Bug-PasteVerticalCollapse — Paste nhiều món làm sai cao độ TẤT CẢ các món

**ID:** Bug-PasteVerticalCollapse
**Phát hiện:** Test tay 02/08/2026 (xác nhận qua editor thật, không phải suy đoán từ doc)
**Ưu tiên:** 🔴 Cao — nhưng KHÔNG chặn Gate 2 (Copy/Paste vẫn dùng được với đồ cùng cao độ)

### Triệu chứng
```
Đặt 1 đồ trần (quạt/điều hòa) + 1 đồ sàn → chọn cả 2 → Ctrl+C
→ Ctrl+V, trace xuống nền nhà
→ Kết quả: TÂM của nhóm bị đặt xuống sàn
   → đồ trần lơ lửng giữa sàn và trần
   → đồ sàn CHÌM xuống dưới nền
```

### Root cause
```
CopyMesh:  RelativeLocation = ActorLocation − tâm nhóm
PasteMesh: PasteCenter = điểm trace trúng SÀN
           actualLocation = PasteCenter + RelativeLocation
           → TÂM nhóm bị neo vào sàn, không phải từng món neo vào bề mặt của nó
```

Phạm vi rộng hơn tên gọi: không riêng đồ trần. Áp cho **mọi** paste nhiều món có chênh cao độ
(đồ trên bàn + đồ dưới sàn, tranh tường + sofa...).

Bất đối xứng kèm theo: `PasteMesh` detect **một** `SurfaceType` từ HitNormal rồi áp **chung cả
nhóm**, trong khi `DuplicateMesh` giữ `SurfaceType` riêng từng món. Hai đường xử lý lệch nhau.

### Trạng thái
- **Open.** KHÔNG chặn Gate 2. Đề xuất mở "Sprint Surface" SAU Gate 2, gộp chung với
  Bug-StaleSurfaceType (xem ghi chú "Gốc chung" bên dưới). Xem `DEVIATIONS.md` mục "Q9 S-Matrix
  Gate + 3 bug Surface — 02/08/2026".

---

## Bug-StaleSurfaceType — Kéo đồ đi chỗ khác, PlacementSurfaceType không cập nhật

**ID:** Bug-StaleSurfaceType
**Phát hiện:** Test tay 02/08/2026 (xác nhận qua editor thật, không phải suy đoán từ doc)
**Ưu tiên:** 🟡 Trung bình — KHÔNG chặn Gate 2

### Triệu chứng
```
Đặt 1 tranh lên tường → dùng gizmo kéo ra giữa phòng → bấm phím mũi tên
→ nó nhích theo kiểu ĐỒ TƯỜNG (sai trục)
```

### Root cause
`PlacementSurfaceType` chỉ được SET một lần trong `WBP_DragOverlay.On Drag Over` lúc drag-drop lần
đầu. Move mode KHÔNG snap surface, KHÔNG cập nhật lại (đã ghi trong Key Notes
`WBP_DragOverlay_FurnitureCard.md` như một quyết định thiết kế, nhưng hệ quả chưa từng được đánh
giá).

Lan sang đâu: Nudge chạy sai nhánh; thumbnail `ResolveThumbAlign` phân loại sai; combo lưu sai
`surfaceType` vào JSON.

### Trạng thái
- **Open.** KHÔNG chặn Gate 2. Đề xuất mở "Sprint Surface" SAU Gate 2, gộp chung với
  Bug-PasteVerticalCollapse (xem ghi chú "Gốc chung" bên dưới). Xem `DEVIATIONS.md` mục "Q9
  S-Matrix Gate + 3 bug Surface — 02/08/2026".

---

## Ghi chú — Gốc chung 3 bug Surface

**Phát hiện:** 02/08/2026, cùng phiên xác nhận Bug-MaterialPrimaryOnly / Bug-PasteVerticalCollapse
/ Bug-StaleSurfaceType.

```
Sự thật nằm ở ĐÂU?

Bug-MaterialPrimaryOnly:      ở PRIMARY,     đáng lẽ ở CẢ NHÓM
Bug-PasteVerticalCollapse:    ở TÂM nhóm,    đáng lẽ ở TỪNG MÓN so với bề mặt của nó
Bug-StaleSurfaceType:         ở LÚC SPAWN,   đáng lẽ ở VỊ TRÍ HIỆN TẠI
```

Cùng một loại lỗi: chọn sai điểm neo cho sự thật. Đề xuất: mở "Sprint Surface" SAU Gate 2, gộp cả
3 — sửa chung rẻ hơn sửa lẻ.

---

## Ô nghi ngờ chưa verify

> Rút từ đọc docs, CHƯA chạy test. Không được coi là kết luận. Ưu tiên verify khi chạm vào vùng
> liên quan. Nguồn: phiên bàn kiến trúc với Opus, 02/08/2026.

| # | Nghi ngờ | Cơ sở trong doc |
|---|---|---|
| N1 | `SelectSimilarMesh` không đi qua `ExpandSelectionWithGroups` — dùng thẳng `Get All Actors With Tag`. Đang edit mode mà bấm "Chọn đồ giống" có chọn cả đồ ngoài scope không? | Sprint 2 T5 + BP_FurnitureInputManager v1.5 |
| N2 | Replace Mesh khi selection = combo root (S4): `MeshesToReplace = SelectedActors` = toàn bộ member → cả cụm biến thành N bản cùng 1 mesh? | ContextMenu_Prep §2.1 |
| N3 | Delete / Duplicate 1 món **trong** combo → cụm thiếu/thừa món nhưng `SourceComboID` vẫn nguyên → Save đè sẽ ghi đè combo gốc bằng bản đã méo | F4 spawn auto-join scope + C9.5 |
| N4 | `UngroupActors` peel-one-level trên combo root → `SourceComboID` đi đâu? | Sprint 4 D4-8 |
| N5 | Copy/Paste cả cụm: clipboard không lưu GroupID → paste ra N mesh rời, mất combo | Combo_Execution backlog |
| N7 | **2 kho material lệch nhau:** actor/snapshot/EMS lưu **full path**, combo JSON lưu **RowName**. Đổi material 1 món trong combo rồi Save đè → material ngoài catalog reverse lookup fail → lưu `""` → **mất im lặng**, không toast, không crash | Combo_Execution §1 + backlog |
| N9 | Copy/Paste material slot khi `TargetFurnitureActor` là mesh trong combo (S6) — có làm bẩn `SourceComboID` không | Material_CopyPaste v0 |
| N12 | Combo ghost align **đáy cube vào sàn** (`GhostExtentZ`) → không có đường nào drop combo Ceiling/Wall đúng chỗ | WBP_DragOverlay v1.8 |
| N13 | Replace Combo spawn tại Center cũ, **rotation reset 0** → combo áp tường mất hướng, đâm xuyên tường | Combo_Execution C9 |
| N14 | `CalculateCenter` as-built không loại pivot/container (doc cũ mô tả sai) → anchor lệch nếu mảng lẫn actor khác | C9_Execution_Plan §11 |

> N6 / N10 / N11 đã verify → chuyển thành 3 bug: xem `Bug-MaterialPrimaryOnly`,
> `Bug-PasteVerticalCollapse`, `Bug-StaleSurfaceType` ở trên.

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
