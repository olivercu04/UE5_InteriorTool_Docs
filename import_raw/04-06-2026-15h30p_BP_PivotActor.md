# BP_PivotActor
**Phiên bản:** 1.0 | **Tạo:** 04/06/2026 — 15:30 ICT | Actor vô hình — pivot cho multi-gizmo (Sprint 1 T3)

> Blueprint MỚI tạo ở Sprint 1. Khi chọn ≥2 đồ, hệ thống spawn 1 pivot vô hình tại tâm nhóm; gizmo gắn vào pivot này; khi pivot di chuyển/xoay/scale → các đồ con theo. Cách này cho multi-gizmo mà KHÔNG phải sửa plugin RuntimeTransformer.
>
> **Trạng thái hiện tại:** MOVE-only (delta-based). T15 sẽ viết lại RefreshOffsets + ApplyTransformToChildren sang Transform Composition để thêm Rotate + Scale (xem `T15_Multi_Rotate_Scale_Plan.md`).

---

## Parent Class
**StaticMeshActor** (KHÔNG phải Actor).
**Lý do (DEVIATION T3):** `ActivateGizmo` của BP_GizmoController chỉ nhận StaticMeshActor. Pivot phải là StaticMeshActor để gizmo gắn vào được. Actor vẫn vô hình (không set static mesh nào).

---

## Class Defaults
```
Tags: ["FurniturePivot"]   ← set ở Class Defaults (KHÔNG dùng tag "FurnitureSpawned" → không bị EMS save, không bị CaptureSnapshot duyệt)
```

---

## Variables
```
AttachedActors        : Array of BP_FurnitureActor   ← các đồ con của pivot
LastPivotTransform    : Transform                     ← transform pivot frame trước (mốc tính delta cho Move)

← Capture lúc RefreshOffsets (Move-only hiện chưa dùng hết, chuẩn bị cho T15):
InitialOffsets        : Array of Vector               ← offset vị trí mỗi con so với pivot
InitialChildScales    : Array of Vector               ← scale gốc mỗi con
InitialChildRotations : Array of Rotator              ← rotation gốc mỗi con
```

**Ghi chú:** T15 sẽ thay 3 array Initial* bằng `InitialRelativeTransforms : Array of Transform` + `InitialPivotTransform : Transform` (Transform Composition). Hiện giữ 3 array, Move-only chủ yếu dùng `LastPivotTransform` để tính delta.

---

## Event BeginPlay
```
Set Mobility (Target = StaticMeshComponent, Movable)   ← cho phép di chuyển runtime
Set Actor Tick Enabled (False)                          ← Tick chỉ bật khi đang multi-select (UpdateGizmo bật)
```
**Lưu ý:** tag "FurniturePivot" đặt ở Class Defaults, KHÔNG set trong BeginPlay.

---

## Function `RefreshOffsets`
Gọi từ BP_FurnitureInputManager.SpawnOrUpdatePivot (khi selection đổi) và sau Nudge. KHÔNG gọi mỗi frame.

```
Array Clear → InitialOffsets, InitialChildScales, InitialChildRotations

ForEach AttachedActors (Actor):
  Branch IsValid(Actor):
    True →
      Get Actor Location(Actor) - Get Actor Location(Self) → offset → ADD to InitialOffsets
      Get Actor Scale 3D(Actor) → ADD to InitialChildScales
      Get Actor Rotation(Actor) → ADD to InitialChildRotations
    False → (để trống)

SET LastPivotTransform = Get Actor Transform(Self)
```

**Mục đích hiện tại:** chốt `LastPivotTransform` làm mốc delta cho ApplyTransformToChildren; lưu Initial* cho tương lai (T15).

---

## Function `ApplyTransformToChildren` — MOVE-only (delta-based, hiện tại)
Gọi mỗi frame trong Event Tick khi đang drag.

```
deltaMove = Get Actor Location(Self) - LastPivotTransform.Location   ← Break Transform → Location

ForEach AttachedActors (Actor):
  Branch IsValid(Actor):
    True →
      NewLoc = Get Actor Location(Actor) + deltaMove
      Set Actor Location(Actor, NewLoc, Sweep=False)
    False → (để trống)

SET LastPivotTransform = Get Actor Transform(Self)   ← cập nhật mốc cho frame sau
```

**⚠️ Chỉ xử lý Move (translation).** Rotate/Scale của pivot hiện KHÔNG truyền xuống con. T15 sẽ viết lại bằng Transform Composition (`Make Relative Transform` + `Compose Transforms`) để xử lý cả 3.

---

## Event Tick
```
GET AttachedActors → Get(0) → IsValid → Branch:
  True  → Call ApplyTransformToChildren → SET LastPivotTransform (đã làm trong Apply)
  False → (để trống)
```

**DEVIATION T3:** plan gốc có check "Not Equal (Transform)" trước khi Apply (chỉ chạy khi pivot đổi). Đã BỎ — UE5 không có node so sánh Transform tiện dùng, và chỉ dùng guard `IsValid(AttachedActors[0])`. Move-only delta-based chạy mỗi frame: nếu pivot không đổi → deltaMove = 0 → SetActorLocation về chính vị trí cũ (vô hại, không tích lũy lỗi).

**Tick chỉ bật khi multi-select:** `UpdateGizmo` nhánh ≥2 gọi `Set Actor Tick Enabled(GizmoPivotActor, True)`; `DestroyPivot` hủy actor khi <2.

---

## Event End Play — VRAM Leak Prevention
```
Array Clear → AttachedActors
Array Clear → InitialOffsets, InitialChildScales, InitialChildRotations
```
Drop hard ref đến các BP_FurnitureActor con để GC giải phóng.

---

## Vòng đời (lifecycle)
```
Chọn đồ thứ 2 (UpdateGizmo Length>=2):
  SpawnOrUpdatePivot → Spawn BP_PivotActor (nếu chưa có) → SET Location = Center
  → SET AttachedActors = SelectedActors → RefreshOffsets
  → ActivateGizmo(GizmoPivotActor) → Set Actor Tick Enabled(True)

Drag gizmo → pivot di chuyển → Tick → ApplyTransformToChildren → con theo

Chọn còn 1 đồ / bỏ chọn hết (UpdateGizmo Length<2 hoặc 0):
  DestroyPivot → Destroy Actor → SET GizmoPivotActor = None
```

---

## Quan hệ với BP khác
- **BP_FurnitureInputManager** sở hữu `GizmoPivotActor : BP_PivotActor`. Spawn/destroy/cập nhật qua SpawnOrUpdatePivot/DestroyPivot. SET AttachedActors = SelectedActors trước khi RefreshOffsets.
- **BP_GizmoController** nhận pivot làm TargetActor trong ActivateGizmo khi multi-select. T15 sẽ thêm: OnMousePressed Cast SelectedActor → BP_PivotActor → RefreshOffsets (capture drag-start); OnMouseReleased → CaptureSnapshot.
- **Tag "FurniturePivot"** phân biệt với "FurnitureSpawned" → pivot không bị EMS save / CaptureSnapshot duyệt.

---

## Key Notes
- Parent = StaticMeshActor (ActivateGizmo yêu cầu), vô hình.
- Tag "FurniturePivot" ở Class Defaults.
- Tick mặc định False, chỉ bật khi multi-select.
- RefreshOffsets gọi lúc selection đổi + sau Nudge, KHÔNG mỗi frame.
- ApplyTransformToChildren hiện MOVE-only delta-based → T15 nâng lên Transform Composition (Move+Rotate+Scale).
- End Play clear AttachedActors + Initial* (chống VRAM leak).
- IsValid trước mọi access actor con (con có thể đã bị destroy).

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 04/06/2026 — 15:30 ICT | Tạo mới (Sprint 1 T3): pivot vô hình parent StaticMeshActor, tag FurniturePivot, RefreshOffsets + ApplyTransformToChildren MOVE-only delta-based, Event Tick guard IsValid, End Play clear |
