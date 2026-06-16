# B1 — Arrow Key Nudge Flow
**Phiên bản:** 1.2 | **Cập nhật:** 04/06/2026 — 15:30 ICT | Multi-Select (Sprint 1 T10)

> **v1.2:** chuyển từ single (`SelectedFurnitureActor`) sang **multi** (`SelectedActors`). Di chuyển cả nhóm + cập nhật Pivot. Direction tính từ `PrimarySelectedActor`.

---

## Input Action Setup

**IA_FurnitureNudge** — Value Type: Axis2D (Vector2D)
Path: `/Game/cuong/UI/Input/IA_FurnitureNudge`

**LM_FurnitureInput — 8 mappings (4 hướng × 2 triggers):**

| Key | Trigger 1 | Trigger 2 | Modifiers | Kết quả |
|---|---|---|---|---|
| Right | Pressed | Pulse (interval=0.1, TriggerOnStart=false) | — | Direction=(1,0) |
| Left  | Pressed | Pulse (interval=0.1, TriggerOnStart=false) | Negate | Direction=(-1,0) |
| Up    | Pressed | Pulse (interval=0.1, TriggerOnStart=false) | Swizzle YXZ | Direction=(0,1) |
| Down  | Pressed | Pulse (interval=0.1, TriggerOnStart=false) | Swizzle YXZ + Negate | Direction=(0,-1) |

⚠️ Pressed = bước ngay. Pulse = giữ phím di chuyển liên tục mỗi 0.1s (chỉ SnapStep > 0).

---

## BP_FoffPlayerController — Routing

```
EnhancedInputAction IA_FurnitureNudge (Triggered):   ← dùng Triggered (cả Pressed + Pulse)
  Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
  → Call NudgeMesh(Direction = ActionValue.XY)
```

---

## PlacementSurfaceType — Detect surface

**BP_FurnitureActor variable:** `PlacementSurfaceType : Name (SaveGame, Default="Floor")`
**Values:** `"Floor"` | `"Wall"` | `"Ceiling"`

**Set trong WBP_DragOverlay → On Drag Over** (HitNormal.Z):
```
Normal.Z > 0.5  → "Floor"   |   Normal.Z < -0.5 → "Ceiling"   |   Else → "Wall"
```
Saved trong `S_FurniturePlacement.SurfaceType` → persist qua Undo/Redo/Save/Load.

---

## Custom Event `NudgeMesh(Direction: Vector2D)` — MULTI (v1.2)

```
Branch SelectedActors.LENGTH == 0:
  True → Return Node
  False ↓

Branch SnapStep > 0:
  F → return (Tick lo phần free mode)
  T ↓

  ← Direction tính từ PrimarySelectedActor:
  Cast PrimarySelectedActor → BP_FurnitureActor → GET PlacementSurfaceType → SurfaceType

  Branch SurfaceType == "Wall":
    T →  ← Up/Down = world Z, Left/Right = snap camera yaw
      UpAxis = Make Vector(0,0,1)
      Get Camera Rotation → Yaw → ÷90 → Round → ×90 → SnappedYaw
      Make Rotator(0, SnappedYaw, 0) → Get Right Vector → SnappedRight
      MoveOffset = (SnappedRight × Direction.X + UpAxis × Direction.Y) × SnapStep
      ← ForEach di chuyển nhóm (xem dưới)
    F →  ← Floor/Ceiling: snap yaw horizontal
      Get Camera Rotation → Yaw → ÷90 → Round → ×90 → SnappedYaw
      Make Rotator(0, SnappedYaw, 0) → Get Forward Vector → SnappedForward; Get Right Vector → SnappedRight
      MoveOffset = (SnappedRight × Direction.X + SnappedForward × Direction.Y) × SnapStep
      ← ForEach di chuyển nhóm (xem dưới)

  ← DI CHUYỂN CẢ NHÓM (cả 2 nhánh đều có ForEach này với MoveOffset riêng):
  ForEach SelectedActors (Actor):
    Branch IsValid(Actor):
      True → Add Actor World Offset(Actor, MoveOffset, Sweep=False)
  ForEach Completed →
    ← Cập nhật Pivot theo nhóm:
    Branch IsValid(GizmoPivotActor):
      True →
        CalculateCenter(SelectedActors) → NewCenter
        Set Actor Location(GizmoPivotActor, NewCenter, Sweep=False)
        Call RefreshOffsets(GizmoPivotActor)
    ← Debounce snapshot 0.5s:
    Clear and Invalidate Timer by Handle(NudgeSnapshotTimerHandle)
    Set Timer by Function Name("CaptureNudgeSnapshot", 0.5, Looping=False) Object=self → SET NudgeSnapshotTimerHandle
```

**⚠️ Quan trọng:** ForEach di chuyển phải có ở **CẢ 2 nhánh** Wall True/False (MoveOffset khác nhau, cách apply giống nhau). Pin `Add Actor World Offset` target = **Array Element của ForEach**, KHÔNG phải PrimarySelectedActor.

---

## Custom Event `CaptureNudgeSnapshot`
```
Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Nudge")
```

---

## Event Tick — Free Mode (SnapStep = 0) — MULTI (v1.2)

```
Branch SnapStep == 0 AND SelectedActors.LENGTH > 0:
  T →
    Get Player Controller → Is Input Key Down(Right/Left/Up/Down) → bRight/bLeft/bUp/bDown
    DirX = Select(bRight,1,0) + Select(bLeft,-1,0)
    DirY = Select(bUp,1,0) + Select(bDown,-1,0)

    Branch DirX != 0 OR DirY != 0:
      T →
        Cast PrimarySelectedActor → GET PlacementSurfaceType → SurfaceType
        Branch SurfaceType == "Wall":
          T → UpAxis=(0,0,1); snap yaw → SnappedRight
              MoveOffset = (SnappedRight × DirX + UpAxis × DirY) × NudgeSpeed × GetWorldDeltaSeconds
          F → snap yaw → SnappedForward/SnappedRight
              MoveOffset = (SnappedRight × DirX + SnappedForward × DirY) × NudgeSpeed × GetWorldDeltaSeconds

        ← DI CHUYỂN NHÓM (cả 2 nhánh):
        ForEach SelectedActors (Actor):
          Branch IsValid(Actor): True → Add Actor World Offset(Actor, MoveOffset, Sweep=False)
        ForEach Completed →
          Branch IsValid(GizmoPivotActor):
            True → CalculateCenter(SelectedActors) → SetActorLocation(GizmoPivotActor) → RefreshOffsets(GizmoPivotActor)
          Clear+Set Timer("CaptureNudgeSnapshot", 0.5) → SET NudgeSnapshotTimerHandle
      F → (không di chuyển)
  F → (không làm gì)
```

---

## Key Notes

- **MULTI:** guard `SelectedActors.LENGTH` thay `IsValid(SelectedFurnitureActor)`; direction từ `PrimarySelectedActor`; ForEach di chuyển từng actor.
- **Cập nhật Pivot sau di chuyển:** CalculateCenter → SetActorLocation(Pivot) → RefreshOffsets → gizmo nhóm theo đồ. Thiếu bước này → gizmo đứng yên khi nudge.
- **PlacementSurfaceType** thay Actor Tag — persist qua Undo/Redo/Save/Load.
- **Snap yaw 90°** (`Round(Yaw/90)×90`) cho cả wall + floor → di chuyển theo world axis sạch dù camera nhìn chéo.
- **Wall:** Up/Down = world Z, Left/Right = snapped camera right. **Floor/Ceiling:** Up/Down = snapped forward, Left/Right = snapped right.
- **SnapStep > 0:** Pulse-based, debounce 0.5s. **SnapStep = 0:** Tick-based, dừng ngay khi thả phím (IsInputKeyDown=false).
- **Không dùng CurrentNudgeDirection** — IsInputKeyDown trực tiếp trong Tick tránh stale state.

---

## Lịch sử
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0-1.1 | 22/05/2026 | Single nudge + PlacementSurfaceType wall/floor |
| 1.2 | 04/06/2026 | Multi: ForEach SelectedActors, direction từ PrimarySelectedActor, cập nhật Pivot sau di chuyển |
