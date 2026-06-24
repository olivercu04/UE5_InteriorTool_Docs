# BP_ComboGhostActor
**Phiên bản:** 1.0 | **Tạo:** 24/06/2026 — C4 Combo Drag Preview | **Parent:** Actor

Ghost actor tạm thời — hiển thị preview bounding box của combo trong lúc drag. Spawn bởi WBP_ComboCard.OnDragDetected, destroy khi drag kết thúc (On Drop hoặc Drag Cancelled).

---

## Components

| Component | Type | Settings |
|---|---|---|
| GhostMesh | Static Mesh Component | Mesh = BasicShapes/Cube; Collision = NoCollision; Material = M_ComboGhost |

GhostMesh là Root Component.

---

## Variables

| Tên | Type | Ghi chú |
|---|---|---|
| *(không có extra var)* | — | Toàn bộ state nằm ở Extent được set qua InitGhost |

---

## Custom Events / Functions

### InitGhost(Extent : Vector) — Custom Event

Được gọi ngay sau Spawn Actor, trước khi widget set PreviewActorRef.

```
Entry (Extent)
  ▶→ Extent / 50.0 ●→ NewScale3D
  ▶→ Set Actor Scale 3D(Target=self, NewScale3D)
  ▶→ Set Relative Location(Target=GhostMesh, NewLocation=Make Vector(X=0, Y=0, Z=50))
```

> **⚠️ BUG OPEN (24/06/2026):** Ghost preview vẫn chìm dưới sàn — đáy cube sunk below floor.
> `Set Relative Location Z=50` chưa sửa được vấn đề này.
> **Nguyên nhân nghi ngờ:** Set Actor Scale 3D thay đổi pivot center → Z=50 bù chưa đúng.
> **Hướng fix tương lai (Approach B):** Thay vì bù Z trong InitGhost, bù ở On Drag Over:
> `Set Actor Location = HitLocation + Make Vector(0, 0, Extent.Z)` — Extent lấy từ BP_DragDropOperation_ComboCard.ComboExtent.
> **Status:** Investigation pending (C4 80% — ghost offset chưa pass).

---

## M_ComboGhost (Material)

| Property | Value |
|---|---|
| Blend Mode | Translucent |
| Shading Model | Unlit |
| Base Color | (0.2, 0.5, 1.0, 0.3) — xanh trong |
| Two Sided | True |

---

## Usage (lifecycle trong drag-drop)

```
WBP_ComboCard.OnDragDetected
  ▶→ Spawn Actor(BP_ComboGhostActor, Location=PlayerCamera hoặc origin tạm)
  ▶→ Cast To BP_ComboGhostActor → InitGhost(Extent=BoundingBoxExtent)
  ▶→ SET WBP_DragOverlay.PreviewActorRef = GhostActor

WBP_DragOverlay.On Drag Over (mỗi frame)
  ▶→ Line Trace → HitLocation
  ▶→ Set Actor Location(PreviewActorRef, HitLocation)  ← ghost theo chuột

WBP_DragOverlay.On Drop
  ▶→ GetActorLocation(PreviewActorRef) → SpawnLocation
  ▶→ SpawnComboByID(ComboID, SpawnLocation)
  ▶→ Destroy Actor(PreviewActorRef) → SET None

WBP_ComboCard.OnDragCancelled
  ▶→ Destroy Actor(PreviewActorRef) → SET None
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 24/06/2026 | Tạo mới — C4 combo drag preview. InitGhost(Extent). Bug ghost offset open. |
