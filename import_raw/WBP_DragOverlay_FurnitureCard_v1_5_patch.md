# WBP_DragOverlay_FurnitureCard — PATCH v1.5
**Phiên bản:** 1.5 | **Cập nhật:** 15/06/2026 — 20:30 ICT
**Patch từ v1.4 → v1.5 (Sprint 4 Bug Fix F4 — Spawn auto-join edit scope)**
> Đọc kèm WBP_DragOverlay_FurnitureCard.md v1.4.

---

## On Drop — SỬA (F4)

**Vị trí chèn:** Sau `ADD "FurnitureSpawned"` (Step 7), TRƯỚC `Get All Actors Of Class(BP_UndoManager)` → CaptureSnapshot (Step 8).

**Đoạn mới chèn:**
```
[After ADD "FurnitureSpawned"]

Get All Actors Of Class(BP_FurnitureInputManager) → GET[0] → Cast → InputRef
InputRef → GetCurrentEditScope() → Scope

Branch(Scope Not Equal (String) ""):
  True  ▶→ GET PreviewActorRef → SET GroupID = Scope ▶→ [merge]
  False ▶→                                               [merge]   ← BẮT BUỘC merge

[merge] ▶→ Get All Actors Of Class(BP_UndoManager) → CaptureSnapshot("Spawn")
```

> ⚠️ **L2 CRITICAL:** Nhánh False PHẢI merge với True trước CaptureSnapshot.
> False dead-end → OnDrop không reach Return Node → trả về false → UMG gọi OnDragCancelled → Destroy PreviewActorRef → mesh biến mất (bug N5 đã trả giá 15/06).
> `PreviewActorRef` là `BP_FurnitureActor` — SET GroupID KHÔNG cần Cast thêm.

---

## On Drop — Exec flow đầy đủ (tham khảo)

Trace từ Blueprint export (15/06/2026):
```
Entry
→ Get All Actors Of Class(BP_FurnitureInputManager) → GET[0] → GizmoControllerRef → DeactivateGizmo
→ Cast Operation → BP_DragDropOperation_FurnitureCard → SET PendingFurnitureDA
→ Line Trace Single (screen pos, ignore PreviewActorRef)
→ Branch(Hit):
    True →
      Cast PreviewActorRef [⚠ warning: unnecessary cast, đã là BP_FurnitureActor]
      → Load Asset Blocking(FurnitureDA.Mesh) → Cast StaticMesh → Set Static Mesh
      → SET MeshPath
      → SET DAPath
      → ADD "FurnitureSpawned" (Tags)
      ← [F4 INSERT — 15/06/2026]:
        Get All Actors Of Class(InputManager) → GET[0] → Cast → InputRef
        InputRef.GetCurrentEditScope() → Scope
        Branch(Scope != ""):
          True  → SET PreviewActorRef.GroupID = Scope → merge
          False → merge
      → Get All Actors Of Class(BP_UndoManager) → GET[0] → CaptureSnapshot("Spawn")
      → Get All Actors Of Class(BP_FurnitureUserPrefsManager) → GET[0] → AddRecentMesh
      → Remove From Parent
      → Return(true)
    False → dead-end
```

---

## Lịch sử cập nhật (thêm vào bảng)

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.5 | 15/06/2026 — 20:30 ICT | **F4: On Drop auto-join edit scope.** Sau ADD "FurnitureSpawned": get InputManager → GetCurrentEditScope → Branch → SET PreviewActorRef.GroupID nếu trong edit. Merge cả 2 nhánh về CaptureSnapshot (L2 fix: False dead-end gây mesh biến mất). |
