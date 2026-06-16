# Open Bugs — Bugs đang mở
**Tạo từ:** `00_Core/DEVIATIONS.md` (mục BUGS DEFERRED) + `00_Core/01_Session_State.md` (BUG CÒN MỞ) + `00_Core/02_Current_Sprint.md` (bối cảnh Gate 1)
**Cập nhật:** 15/06/2026

---

## Tổng quan

| # | Bug | Ưu tiên | Sprint/Gate xử lý |
|---|---|---|---|
| B1 | ✅ FIXED (16/06) — Undo lần 2 không restore group state | — | Đóng Gate 1, xem BP_UndoManager.md v1.9-1.10 |
| B-gizmo | Gizmo ẩn sau undo trong edit mode (pre-existing) | 🟢 Thấp | Known issue, chưa có timeline |
| B-folder | Replace folder sai khi group nhiều mesh khác folder | 🟢 Thấp | Defer Sprint 5 |

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
- **Deferred đến Sprint 5/D.** Không block tính năng chính.
- Ghi nhận trong `00_Core/DEVIATIONS.md` mục BUGS DEFERRED (Replace folder).

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
