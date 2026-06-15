# BP_UndoManager — PATCH v1.8
**Phiên bản:** 1.8 | **Cập nhật:** 15/06/2026 — 20:30 ICT
**Patch từ v1.7 → v1.8 (Sprint 4 Bug Fix A12 — EditModeStack vào Undo)**
> Đọc kèm BP_UndoManager.md v1.7.

---

## Root cause A12

**Triệu chứng:** Đang trong edit mode group có sẵn (không tạo mới trong session) → Ctrl+Z → Edit mode bar vẫn hiện.

**Nguyên nhân:** `EditModeStack` là runtime state (`KHÔNG SaveGame`), không nằm trong `S_SceneSnapshot`. Khi Undo restore snapshot:
- Snapshot không có EditModeStack → stack không được khôi phục
- ValidateEditMode kiểm tra stack: các group vẫn tồn tại → stack hợp lệ → broadcast `OnEditModeChanged(True)` → bar giữ nguyên

**Fix:** Đưa `EditModeStack` vào snapshot (field `EditModeStackSnapshot`). Restore trước `ValidateEditMode` → ValidateEditMode validate trên stack đã khôi phục đúng.

---

## S_SceneSnapshot — CẬP NHẬT (Version = 4)

Thêm field mới (cuối struct, additive — backward compatible):
```
EditModeStackSnapshot : Array<String>    ← stack GroupID tại thời điểm snapshot. Default = [] cho V<4.
```

**Version history:**
- V1: single select (legacy)
- V2: multi-select
- V3: Groups (Sprint 3)
- **V4: Groups + EditModeStackSnapshot (15/06/2026)**

---

## Variables — THÊM MỚI

```
TempEditModeStack : Array<String>    (KHÔNG SaveGame — pattern giống TempGroups)
```
> Buffer để tránh impure-timing khi đọc InputManager.EditModeStack trong CaptureSnapshot (Custom Event).
> CLEAR ở Event End Play.

---

## CaptureSnapshot — CẬP NHẬT

**Step 0b** (đang có: `GetGroupsForSnapshot → SET TempGroups`), THÊM ngay sau:
```
GET InputManager.EditModeStack ●→ SET TempEditModeStack
```
> Reuse InputManager ref đang sẵn trong exec chain. Không get mới.

**Node `Make S_SceneSnapshot`** — THÊM pin:
```
EditModeStackSnapshot = GET TempEditModeStack
Version              = 4                         ← bump từ 3
```

---

## RestoreSnapshot — CẬP NHẬT

**Vị trí:** Trong Step 5b (nhánh Version >= 3 → IsValid True), ngay sau `SyncGroupsToContainer`, TRƯỚC `ValidateEditMode`.

**Cắt wire hiện tại:** `SyncGroupsToContainer.then → ValidateEditMode.execute`

**Chèn vào giữa:**
```
SyncGroupsToContainer ▶→

GET Snapshot.EditModeStackSnapshot ●→ SET InputManager.EditModeStack

▶→ ValidateEditMode
```

**Refs có sẵn, không cần get mới:**
- Target InputManager: Knot chain từ `GetArrayItem_22.Output → Knot_114 → Knot_115` (đang dùng cho SyncGroupsToContainer.self)
- Snapshot.EditModeStackSnapshot: pin `EditModeStackSnapshot` trên `Break S_SceneSnapshot` node (NodePosX≈12320) — pin đã hiện, chưa nối trước khi fix

**Tại sao SET trước ValidateEditMode:**
ValidateEditMode đọc InputManager.EditModeStack để validate. Phải SET đúng trước để nó validate trên stack đã khôi phục, không phải stack runtime cũ.

---

## Event End Play — CẬP NHẬT

Thêm vào chuỗi CLEAR:
```
CLEAR TempEditModeStack    ← cạnh CLEAR TempGroups đang có
```

---

## Backward Compatibility

- Snapshot V1/V2/V3: `EditModeStackSnapshot` = [] (default)
- Restore V1/V2/V3: SET EditModeStack = [] → ValidateEditMode → stack rỗng → broadcast False → bar ẩn
- Hành vi: safe — không biết edit state tại snapshot V<4 → thoát edit là đúng nhất
- Không vỡ save file EMS (UndoHistory là runtime, không persist)

---

## Test kết quả

| Case | Scenario | Kết quả |
|---|---|---|
| Case 1 (flat) | Tạo G1 → Enter edit → Undo xóa G1 → bar ẩn | ✅ PASS |
| Case 2 (nested, group có sẵn) | Edit G3>G1 → Ctrl+Z từng bước → breadcrumb cập nhật đúng từng bước | ✅ PASS |

---

## Lịch sử cập nhật (thêm vào bảng)

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.8 | 15/06/2026 — 20:30 ICT | **A12 fix: EditModeStack vào Undo.** S_SceneSnapshot +EditModeStackSnapshot (V=4). +TempEditModeStack class var. CaptureSnapshot Step 0b: SET TempEditModeStack; Make thêm EditModeStackSnapshot. RestoreSnapshot Step 5b: SET InputManager.EditModeStack trước ValidateEditMode. Event End Play: CLEAR TempEditModeStack. |
