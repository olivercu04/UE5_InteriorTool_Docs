# Blueprint_Logic — PATCH v1.5
**Phiên bản:** 1.5 | **Cập nhật:** 15/06/2026 — 20:30 ICT
**Patch từ v1.4 → v1.5 (Sprint 4 Bug Fix — Learnings mới)**
> Bổ sung vào Blueprint_Logic.md v1.4. Không thay thế.

---

## LEARNINGS MỚI (Sprint 4 Bug Fix Session — 15/06/2026)

---

### L-NEW-1: Branch False dead-end — Sequence vs Event (BÀI HỌC ĐẮT GIÁ)

**Ngữ cảnh:** WBP_DragOverlay On Drop — F4 insert Branch(Scope != "") trước CaptureSnapshot.

**Sự khác biệt:**
```
TRONG SEQUENCE NODE (Then 0, Then 1...):
  Branch False → dead-end → OK ✅
  Sequence tự động kích hoạt Then tiếp theo, không cần merge.
  Ví dụ: SpawnFurnitureCopy.Then 0: False dead-end hợp lệ.

TRONG EVENT bình thường (không Sequence):
  Branch False → dead-end → FATAL ❌
  Logic sau Branch (CaptureSnapshot, RemoveFromParent, Return Node) KHÔNG chạy.
  OnDrop: Return Node không reach → return false (default) → UMG gọi OnDragCancelled
  → Destroy PreviewActorRef → mesh biến mất.
```

**Quy tắc:** Trước khi viết Branch bất kỳ, xác định context:
- Trong Sequence.Then: False dead-end OK.
- Trong Event/Custom Event chain: mọi nhánh phải reach exec endpoint.

---

### L-NEW-2: Function output pins không thể CLEAR — dùng Temp Array buffer

**Ngữ cảnh:** ComputeSelectionUnits — output pins `OutGroupUnits`, `OutLooseActors`.

**Vấn đề:** Trong Blueprint Function, output pins (Array) không có node CLEAR. Nếu nối thẳng từ loop vào output pin, có thể nhận giá trị không xác định.

**Pattern đúng:**
```
Entry: CLEAR TempGroupUnits (class var), CLEAR TempLooseActors (class var)
ForEach:
  LoopBody → ADD vào TempGroupUnits / TempLooseActors
  (KHÔNG ADD vào output pin trực tiếp)
Completed:
  SET OutGroupUnits  = TempGroupUnits
  SET OutLooseActors = TempLooseActors
```

> Pattern tương tự TempGroups (Sprint 3) và TempEditModeStack (Sprint 4 A12).

---

### L-NEW-3: ComputeSelectionUnits phải chạy TRƯỚC guard

**Ngữ cảnh:** CreateGroup rewrite (F3).

**Sai:** Guard `SelectedActors.Length < 2 → Return` TRƯỚC ComputeSelectionUnits.
- Nếu chọn 2 groups (mỗi group 5 đồ), SelectedActors.Length = 2 → pass guard.
- Nhưng ComputeSelectionUnits sau guard mới biết đó là 2 group units.
- Vô hại trong case này nhưng logic không rõ ràng.

**Đúng:** Guard phải kiểm tra KẾT QUẢ của ComputeSelectionUnits:
```
ComputeSelectionUnits(SelectedActors) → (GroupUnits, LooseActors)
(GroupUnits.Length + LooseActors.Length) < 2 → Return
```
> Luật 6B (structural symmetry): mọi path đến cùng CreateGroup phải xét đúng số đơn vị thực tế.

---

### L-NEW-4: Truy cập Blueprint export text thay vì screenshot

**Ngữ cảnh:** Debug F3 ComputeSelectionUnits — 5 bugs tìm được qua pin LinkedTo data.

**Phương pháp mới:** User copy-paste K2Node text từ Blueprint graph editor (Edit → Copy) vào chat. AI đọc pin `LinkedTo` để trace exec flow và data connections chính xác.

**Ưu điểm:** Phát hiện được bugs không nhìn thấy trong screenshot:
- ForEach Completed không nối (dead-end)
- Not Equal vs Equal nhầm (pin DefaultValue)
- Output pin swapped (LinkedTo trỏ sai node)
- Unnecessary cast với warning (ErrorMsg)

**Khi dùng:** Debug logic phức tạp, khi screenshot không đủ rõ wire routing.

---

### L-NEW-5: EditModeStack là runtime state — không persist qua Undo nếu không snapshot

**Ngữ cảnh:** A12 fix.

**Nguyên tắc:** Mọi state cần khôi phục qua Undo phải nằm trong S_SceneSnapshot. Runtime-only vars không được restore tự động.

**Checklist khi thêm state mới vào hệ thống:**
- State này có cần undo-able không?
- Nếu có → thêm field vào S_SceneSnapshot + CaptureSnapshot SET + RestoreSnapshot SET
- Thứ tự restore: SET state → ValidateEditMode (nếu có) → broadcast → re-fire selection

---

### L-NEW-6: ValidateEditMode đọc Groups + EditModeStack — restore cả hai trước khi gọi

**Ngữ cảnh:** RestoreSnapshot Step 5b.

**Thứ tự bắt buộc:**
```
1. SyncGroupsToContainer     ← Groups đã ready
2. SET InputManager.EditModeStack = Snapshot.EditModeStackSnapshot   ← Stack đã ready
3. ValidateEditMode()        ← Đọc cả Groups lẫn Stack → kết quả đúng
4. [Step 6b selection...]
```

> ValidateEditMode dùng `FindGroupData` (đọc Groups) và iterate EditModeStack. Nếu đặt sau Step 6b hoặc trước SyncGroupsToContainer → kết quả sai.

---

## NODE FLOW ĐÃ CONFIRM (thêm vào bảng file 09)

| Node display name | Ghi chú |
|---|---|
| `ComputeSelectionUnits` | Function trong BP_FurnitureInputManager (custom) |
| `GetSelectionUnitLabel` | Function trong BP_FurnitureInputManager (custom) |
| `SET [VariableName]` (trên object khác) | Target = object ref, Value = data → SET variable của đối tượng đó |
