# BP_PivotActor
**Phiên bản:** 1.1 | **Cập nhật:** 05/06/2026 — 20:00 ICT | Actor vô hình — pivot cho multi-gizmo (Sprint 1 T3 + T15)

> Blueprint tạo ở Sprint 1. Khi chọn ≥2 đồ, hệ thống spawn 1 pivot vô hình tại tâm nhóm; gizmo gắn vào pivot này; khi pivot di chuyển/xoay/scale → các đồ con theo. Cách này cho multi-gizmo mà KHÔNG phải sửa plugin RuntimeTransformer.
>
> **v1.1 (T15):** Nâng lên Transform Composition — hỗ trợ đầy đủ Move + Rotate + Scale. Viết lại `RefreshOffsets` + `ApplyTransformToChildren`. Thêm 2 biến `InitialRelativeTransforms` + `InitialPivotTransform`.

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
AttachedActors             : Array of BP_FurnitureActor   ← các đồ con của pivot

← T15 — Transform Composition:
InitialRelativeTransforms  : Array of Transform            ← transform của mỗi con tương đối với pivot (chụp lúc drag-start)
InitialPivotTransform      : Transform                     ← transform pivot lúc RefreshOffsets (mốc tính relative; chỉ dùng nội bộ RefreshOffsets)

← Cũ (T3) — GIỮ, chưa xóa (bỏ sau khi toàn bộ Sprint 1 test pass):
LastPivotTransform         : Transform
InitialOffsets             : Array of Vector
InitialChildScales         : Array of Vector
InitialChildRotations      : Array of Rotator
```

**Ghi chú:** `InitialPivotTransform` chỉ đọc trong RefreshOffsets. `ApplyTransformToChildren` KHÔNG đọc nó — chỉ dùng `currentPivotT` (GetActorTransform mỗi frame).

---

## Event BeginPlay
```
Set Mobility (Target = StaticMeshComponent, Movable)   ← cho phép di chuyển runtime
Set Actor Tick Enabled (False)                          ← Tick chỉ bật khi đang multi-select (UpdateGizmo bật)
```
Tag "FurniturePivot" đặt ở Class Defaults, KHÔNG set trong BeginPlay.

---

## Function `RefreshOffsets` — v1.1 (Transform Composition)
Gọi tại: SpawnOrUpdatePivot (selection đổi), sau Nudge, và drag-start (từ BP_GizmoController OnMousePressed). KHÔNG gọi mỗi frame.

```
SET InitialPivotTransform = GetActorTransform(Self)

Array Clear → [InitialRelativeTransforms]

ForEach AttachedActors (Actor):
  Branch IsValid(Actor):
    True →
      childT = GetActorTransform(Actor)
      relT = Make Relative Transform(
               A          = childT,
               Relative To = InitialPivotTransform
             )
      ADD relT → [InitialRelativeTransforms]
    False → (để trống)
```

**Bản chất:** `Make Relative Transform(childWorld, pivotWorld)` = transform của actor NẾU coi pivot là gốc tọa độ. Đây là "công thức cố định" của mỗi actor trong nhóm — lưu 1 lần lúc drag-start, dùng lại mỗi frame.

---

## Function `ApplyTransformToChildren` — v1.1 (Transform Composition)
Gọi mỗi frame trong Event Tick khi drag. Xử lý đầy đủ Move + Rotate + Scale.

```
currentPivotT = GetActorTransform(Self)

ForEach AttachedActors (Index, Actor):   ← dùng cả Array Index lẫn Array Element
  Branch IsValid(Actor):
    True →
      GET InitialRelativeTransforms[Index] (a copy) → relT
      newWorldT = Compose Transforms(
                    A = relT,
                    B = currentPivotT
                  )
      Set Actor Transform(
        Target        = Actor,
        New Transform = newWorldT,
        Sweep         = False,
        Teleport      = True   ← TeleportPhysics: set thẳng, không physics sweep
      )
    False → (để trống)
```

**Thứ tự Compose — CHỐT:** `A = relT, B = currentPivot`. Đây là nghịch đảo của `Make Relative Transform`. Khi pivot chưa di chuyển → `newWorld == childWorld` → đồ đứng yên (verify ở test case 1).

**Teleport = True:** ApplyTransformToChildren chạy 60fps, set transform tuyệt đối mỗi frame → phải Teleport=True. Nếu False → physics sweep mỗi frame → giật.

---

## Event Tick
```
GET AttachedActors → Get(0) → IsValid → Branch:
  True  → Call ApplyTransformToChildren
  False → (để trống)
```

Tick chỉ bật khi multi-select: `UpdateGizmo` nhánh ≥2 gọi `Set Actor Tick Enabled(True)`; `DestroyPivot` hủy actor khi <2.

---

## Event End Play — VRAM Leak Prevention
```
Array Clear → AttachedActors
Array Clear → InitialRelativeTransforms
Array Clear → InitialOffsets, InitialChildScales, InitialChildRotations   ← biến cũ, giữ đến khi dọn
```

---

## Vòng đời (lifecycle)
```
Chọn đồ thứ 2 (UpdateGizmo Length>=2):
  SpawnOrUpdatePivot → Spawn BP_PivotActor (nếu chưa có) → SET Location = Center
  → Set Actor Rotation(0,0,0) + Set Actor Scale 3D(1,1,1)   ← reset sạch cho selection mới
  → SET AttachedActors = SelectedActors → RefreshOffsets
  → ActivateGizmo(GizmoPivotActor) → Set Actor Tick Enabled(True)

Bắt đầu drag gizmo (OnMousePressed trong GizmoController):
  Cast SelectedActor → BP_PivotActor → RefreshOffsets   ← chụp lại relative transforms

Drag gizmo → pivot di chuyển/xoay/scale → Tick → ApplyTransformToChildren → con theo

Chọn còn 1 đồ / bỏ chọn hết:
  DestroyPivot → Destroy Actor → SET GizmoPivotActor = None
```

---

## Quan hệ với BP khác
- **BP_FurnitureInputManager** sở hữu `GizmoPivotActor`. Spawn/destroy/cập nhật qua SpawnOrUpdatePivot/DestroyPivot. Reset rotation/scale trước RefreshOffsets.
- **BP_GizmoController** nhận pivot làm TargetActor trong ActivateGizmo khi multi-select. OnMousePressed Cast → BP_PivotActor → RefreshOffsets (capture drag-start). OnMouseReleased đã có CaptureSnapshot cho Rotate/Scale/Move (không phân biệt loại actor).
- **WBP_MeshControls** kiểm tra `SelectedActors.Length >= 2` trước ActivateGizmo → dùng GizmoPivotActor khi multi-select.
- **Tag "FurniturePivot"** phân biệt với "FurnitureSpawned" → pivot không bị EMS save / CaptureSnapshot duyệt.

---

## Key Notes
- Parent = StaticMeshActor (ActivateGizmo yêu cầu), vô hình.
- Tag "FurniturePivot" ở Class Defaults.
- Tick mặc định False, chỉ bật khi multi-select.
- **RefreshOffsets gọi 2 chỗ:** SpawnOrUpdatePivot (selection đổi) + OnMousePressed (drag-start). KHÔNG mỗi frame.
- **ApplyTransformToChildren:** Transform Composition tuyệt đối — không tích lũy lỗi dù chạy 60fps.
- **SpawnOrUpdatePivot reset pivot rotation/scale** trước RefreshOffsets → gizmo nhóm mới bắt đầu sạch.
- IsValid trước mọi access actor con (con có thể đã bị destroy).
- End Play clear tất cả arrays (chống VRAM leak).

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 04/06/2026 — 15:30 ICT | Tạo mới (Sprint 1 T3): pivot vô hình, tag FurniturePivot, RefreshOffsets + ApplyTransformToChildren MOVE-only delta-based, Event Tick guard IsValid, End Play clear |
| 1.1 | 05/06/2026 — 20:00 ICT | T15: nâng lên Transform Composition (Move+Rotate+Scale). Thêm InitialRelativeTransforms + InitialPivotTransform. Viết lại RefreshOffsets + ApplyTransformToChildren. SpawnOrUpdatePivot reset rotation/scale. RefreshOffsets thêm trigger tại drag-start (GizmoController OnMousePressed). |
