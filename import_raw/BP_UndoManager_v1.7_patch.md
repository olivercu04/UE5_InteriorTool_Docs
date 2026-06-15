# BP_UndoManager — PATCH v1.7
**Phiên bản:** 1.7 | **Cập nhật:** 12/06/2026 — 15:04 ICT
**Patch từ v1.6 → v1.7 (Sprint 4 T8 — ValidateEditMode)**
> Đọc kèm bản gốc v1.6. File này ghi ĐỦ những gì thêm/thay đổi.

---

## Function MỚI: `ValidateEditMode()`

Gọi từ RestoreSnapshot sau khi restore Groups xong. Kiểm tra EditModeStack còn hợp lệ không — cắt bỏ từ group không còn tồn tại.

```
Entry ▶→ CLEAR LocalValid                              ← local Array of String
       ▶→ Get All Actors Of Class(BP_FurnitureInputManager) → GET[0] → Cast → InputRef
       ▶→ Branch(IsValid(InputRef)):
            False ▶→ Return
            True  ▶→ GET InputRef.EditModeStack
                   ▶→ For Each Loop with Break (gid):
                        LoopBody ▶→ Call InputRef.FindGroupData(gid) → (_, _, bFound)
                                 ▶→ Branch(bFound):
                                      True  ▶→ ADD gid → LocalValid   ← group còn tồn tại
                                      False ▶→ BREAK                   ← group mất → cắt từ đây (con cũng vô nghĩa)
                        Completed ▶→
                   ▶→ SET InputRef.EditModeStack = LocalValid
                   ▶→ Branch(InputRef.EditModeStack.Length == 0):
                        True  ▶→ Call InputRef.RemoveEditModeVisual
                               ▶→ Broadcast InputRef.OnEditModeChanged(bActive=False, GroupID="")
                        False ▶→ Call InputRef.ApplyEditModeVisual
                               ▶→ Call InputRef.GetCurrentEditScope → Scope
                               ▶→ Broadcast InputRef.OnEditModeChanged(bActive=True, GroupID=Scope)
```

> **For Each Loop with Break** (không phải For Each Loop thường) — để BREAK thoát sớm khi gặp group không tồn tại.
> BREAK đúng: group cha mất → các group con trong stack (cấp sâu hơn) cũng vô nghĩa → cắt hết từ đó.
> Cả 2 nhánh Branch cuối (Length==0 / >0) đều Broadcast OnEditModeChanged → WBP_MeshControls tự cập nhật breadcrumb/ẩn bar.

---

## RestoreSnapshot — Vị trí chèn ValidateEditMode

Chèn **sau Step 5b** (SyncGroupsToContainer), **trước Step 6b** (re-fire selection):

```
... Step 4 : ForEach Spawn actors, restore materials, SET actor.GroupID = Placement.GroupID
... Step 5 : Branch Version >= 2 → restore SelectedMeshIndices + SelectActors (RestoredActors)
... Step 5b: Branch Version >= 3 → CLEAR InputManager.Groups → ADD Snapshot.Groups → SyncGroupsToContainer
                                                                         ↓
+                                                          Call ValidateEditMode()     ← MỚI THÊM
                                                                         ↓
... Step 6b: Branch SelectedActors.Length > 0 → SelectActors / DeselectAll+DeactivateGizmo
... Step 7 : Broadcast OnRestoreCompleted
```

> ValidateEditMode đọc InputManager.Groups → phải SAU Step 5b (Groups đã restore).
> ValidateEditMode broadcast OnEditModeChanged → cập nhật info bar TRƯỚC Step 6b cập nhật selection count.
> Hai element UI (edit mode bar + selection count) độc lập nhau → thứ tự này là đúng.

---

## Lịch sử cập nhật (thêm vào bảng)

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.7 | 12/06/2026 — 15:04 ICT | **Sprint 4 T8 — ValidateEditMode.** Thêm function ValidateEditMode: For Each With Break duyệt EditModeStack, cắt từ group không tồn tại, broadcast OnEditModeChanged đúng state. Chèn vào RestoreSnapshot sau SyncGroupsToContainer (Step 5b), trước re-fire selection (Step 6b). |
