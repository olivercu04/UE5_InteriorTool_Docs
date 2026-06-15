# Patch Notes — WBP_FurnitureInventory v2.3 + WBP_FurnitureCard v1.4
**Cập nhật:** 08/06/2026 — 11:24 ICT

---

## WBP_FurnitureInventory — v2.3

### Functions mới thêm (Sprint 2 — 08/06)

#### OpenMaterialModeForActor(Actor: BP_FurnitureActor) — v2.3
```
Branch IsValid(Actor): False → Return

SET TargetFurnitureActor = Actor
SET SelectedSlotIndex = -1
Set Visibility(HB_SlotSwatches, Visible)
Call RefreshSlotSwatches
[+ các node update thumbnail từ MaterialOverrides nếu có]
```
**Mục đích:** Entry point cho bên ngoài (CB_ChangeMaterial) setup material mode cho 1 actor cụ thể. Tránh duplicate logic với OnMeshSelected.

#### EnsureExpanded — v2.3
```
Branch bIsMinimized:
  False → Return  (đang mở bình thường)
  True:
    Set Visibility(HB_Main_Content, Visible)      ← QUAN TRỌNG — thiếu cái này expand không hoạt động
    Set Visibility(Background_Blur_246, Visible)
    Set Visibility(HB_Title_Bar, Visible)
    Set Visibility(BTN_Minimized_Icon, Collapsed)
    SET bIsMinimized = False
    Set Position In Viewport(self, X=10, Y=10, Remove DPI Scale=True)
    SET Inventory Position = (10, 10)
    Set Visibility(BTN_Resize_Bottom, Visible)
    Set Visibility(BTN_Resize_Left, Visible)
    Set Visibility(BTN_Resize_Right, Visible)
    Set Visibility(BTN_Resize_TR, Visible)
    Set Visibility(BTN_Resize_TL, Visible)
    Set Visibility(BTN_Resize_BR, Visible)
    Set Visibility(BTN_Resize_BL, Visible)
    Set Visibility(BTN_Resize_Top, Visible)
    Call UpdateResizeHandles
```
**⚠️ Phải match BTN_MinimizedIcon OnClicked chính xác.** Thiếu bất kỳ widget nào → expand không hoạt động. Luôn so sánh với event gốc khi viết hàm "restore state".

---

## WBP_FurnitureCard — v1.4

### BTN_ChangeMesh — NÂNG CẤP MULTI (v1.4, thay thế single v1.3)

**Event:** BTN_ChangeMesh OnClicked → Call **F_ExecuteReplace**

#### F_ExecuteReplace (Function — v1.4)
```
Local Variables:
  LocalNewActors : Array<BP_FurnitureActor>

// Setup
Get All Actors Of Class(BP_FurnitureInputManager)[0] → Cast → SET FurnitureInputRef (class var)

// Guard
GET MeshesToReplace (FurnitureInputRef) → Length
Branch Length > 0: False → Return

// Loop
CLEAR LocalNewActors
ForEach MeshesToReplace (OldActor):  ← Loop Body
  Branch IsValid(OldActor):
    False → (skip)
    True:
      GET Actor Location(OldActor) → LocalLoc
      GET Actor Rotation(OldActor) → LocalRot
      Cast OldActor → BP_FurnitureActor → GET PlacementSurfaceType → LocalSurfType
      Spawn BP_FurnitureActor(LocalLoc, LocalRot) → Cast → NewActor
      Load Asset Blocking(FurnitureDA.Mesh) → Cast StaticMesh → GET FurnitureMesh(NewActor) → Set Static Mesh
      SET MeshPath, DAPath (Get Object Path FurnitureDA), PlacementSurfaceType = LocalSurfType
      GET Tags(NewActor) → ADD "FurnitureSpawned" → SET Tags
      ADD NewActor → LocalNewActors
      Destroy Actor(OldActor)    ← target = OldActor, KHÔNG để trống

// Completed (KHÔNG trong Loop Body!)
ForEach Completed:
  Cast FurnitureInputRef → DeselectAll
  Cast FurnitureInputRef → SelectActors(LocalNewActors)   ← tự lo outline + gizmo
  Get All Actors Of Class(BP_UndoManager)[0] → CaptureSnapshot("Replace")   ← 1 lần duy nhất
  GET BP_FurnitureUserPrefsManager[0] → AddRecentMesh(String to Name(Get Object Name(FurnitureDA)))
  Cast FurnitureInputRef → SET MeshesToReplace = LocalNewActors   ← replace tiếp được
```

**So với v1.3 (single):**
- Bỏ: manual stencil/gizmo (SelectActors lo hết)
- Bỏ: SET MeshToReplace ở cuối (dùng MeshesToReplace thay)
- Thêm: ForEach loop + LocalNewActors
- CaptureSnapshot + AddRecentMesh chuyển ra Completed (1 lần thay vì trong loop)

---

## Lịch sử cập nhật

| File | Phiên bản | Ngày | Nội dung |
|---|---|---|---|
| WBP_FurnitureInventory | 2.3 | 08/06/2026 — 11:24 ICT | Thêm OpenMaterialModeForActor + EnsureExpanded |
| WBP_FurnitureCard | 1.4 | 08/06/2026 — 11:24 ICT | BTN_ChangeMesh → F_ExecuteReplace (ForEach multi thay single) |
