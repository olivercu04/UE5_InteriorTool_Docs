# BP_ComboGhostActor
**Phiên bản:** 1.1 | **Cập nhật:** 25/06/2026 — ghost offset FIXED (Approach B) | **Parent:** Actor

Ghost actor tạm thời — hiển thị preview bounding box của combo trong lúc drag. Spawn bởi WBP_ComboCard.OnDragDetected, destroy khi drag kết thúc (On Drop hoặc Drag Cancelled).

---

## Components

| Component | Type | Settings |
|---|---|---|
| GhostMesh | Static Mesh Component | Mesh = BasicShapes/Cube; Collision = NoCollision; Material = M_ComboGhost |

GhostMesh là Root Component.

---

## Variables

| Tên | Type | Default | Ghi chú |
|---|---|---|---|
| GhostExtentZ | Float | 0.0 | Half-height của ghost trong world space = BoundingBoxExtent.Z. Đọc bởi On Drag Over và On Drop để bù Z. |

---

## Custom Events / Functions

### InitGhost(Extent : Vector) — Custom Event

Được gọi ngay sau Spawn Actor, trước khi widget set PreviewActorRef.

```
Entry (Extent)
  ▶→ Extent / 50.0 ●→ NewScale3D
  ▶→ Set Actor Scale 3D(Target=self, NewScale3D)
  ▶→ Break Vector(Extent) → Z ●→ SET GhostExtentZ
```

> **Giải thích GhostExtentZ:** BasicShapes/Cube = 100×100×100 local. Sau Set Actor Scale 3D(Extent/50.0):
> world half-height = 50 × (Extent.Z/50.0) = Extent.Z. Nên GhostExtentZ = Extent.Z.
>
> **Ghost offset fix (Approach B — 25/06/2026 ✅):** On Drag Over set ghost location =
> `HitLocation + (0,0,GhostExtentZ)` → đáy cube khớp sàn. On Drop trừ ngược lại →
> lấy đúng SpawnLocation floor. Cách này KHÔNG thay đổi InitGhost (không cần Set Relative Location).
> Xem WBP_DragOverlay_FurnitureCard.md v1.8.

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
     ← InitGhost lưu GhostExtentZ = Extent.Z
  ▶→ SET WBP_DragOverlay.PreviewActorRef = GhostActor

WBP_DragOverlay.On Drag Over (mỗi frame)
  ▶→ Line Trace → HitLocation
  ▶→ Set Actor Location(PreviewActorRef, HitLocation)  ← furniture ghost (BP_FurnitureActor)
  ▶→ [CastFailed BP_FurnitureActor → Cast BP_ComboGhostActor]
     ▶→ GET GhostExtentZ
     ▶→ Set Actor Location(PreviewActorRef, HitLocation + Make Vector(0,0,GhostExtentZ))
        ← OVERRIDE location để đáy cube nằm trên sàn (Approach B)

WBP_DragOverlay.On Drop
  ▶→ Cast To BP_DragDropOperation_ComboCard → GET ComboID
  ▶→ GetActorLocation(PreviewActorRef) → AnchorWithOffset
  ▶→ Cast To BP_ComboGhostActor → GET GhostExtentZ
  ▶→ AnchorWithOffset - Make Vector(0,0,GhostExtentZ) ●→ SpawnLocation
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
| 1.1 | 25/06/2026 | Ghost offset FIXED (Approach B). Thêm var GhostExtentZ = Extent.Z. InitGhost lưu GhostExtentZ (bỏ Set Relative Location Z=50 sai). On Drag Over + On Drop cập nhật ở WBP_DragOverlay v1.8. C4/C8 → 100% DONE. |
