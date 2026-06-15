# WBP_FurnitureCard — Drag & Drop + Replace Mesh
**Phiên bản:** 1.4 | **Cập nhật:** 10/06/2026 — 20:34 ICT

> **v1.4 (Sprint 2 multi + Regression-fix):** BTN_ChangeMesh OnClicked → gọi **F_ExecuteReplace** (Function — có local var). Replace MULTI: ForEach `MeshesToReplace` (array). Fix bug thiếu node ADD New Actor → LocalNewActors (mesh mới không được chọn). Cuối: SelectActors(LocalNewActors) + SET MeshesToReplace = LocalNewActors (replace tiếp được). Bỏ biến chết MeshToReplace (single). Đọc kèm `Sprint3_Regression_DualDispatcher_Log.md`.

⚠️ **Tên file doc này gây nhầm lẫn** — widget thực tế tên là `WBP_FurnitureCard`, không có widget `WBP_DragOverlay_FurnitureCard`. File này document cả `WBP_FurnitureCard` và `WBP_DragOverlay`.

---

## WBP_FurnitureCard

### Layout (Canvas Panel)
```
Canvas Panel
├── LazyImage_Thumb
├── Button_InforItem (+ Common Lazy Image)
├── Button_ChangeMesh (+ Common Lazy Image, Visibility = Hidden mặc định)
│   ← chỉ hiện khi bIsReplaceMode = True (check trong OnListItemObjectSet)
└── Button_FavoriteFurniture (+ Common Lazy Image — heart icon, anchor top-right, 32x32)
    ← v1.2: thêm mới, Is Variable = true
```

### Variables
```
FurnitureDA    : DA_FurnitureItem
InventoryRef   : WBP_FurnitureInventory
PreviewActor   : BP_FurnitureActor
DragOverlayRef : WBP_DragOverlay
```

---

### OnListItemObjectSet
```
Cast Item Object → DA_FurnitureItem → SET FurnitureDA
→ Set Brush from Lazy Texture (LazyImage_Thumb, DA.Thumbnail)

Branch IsValid(InventoryRef)?
  False:
    Get Game Instance → Cast Foff_GameInstance → GET FurnitureInventoryRef
    Branch IsValid(FurnitureInventoryRef)?
      True → SET InventoryRef = FurnitureInventoryRef

Branch IsValid(InventoryRef)?
  True:
    Branch InventoryRef.bIsReplaceMode == True?
      True → Set Visibility (Button_ChangeMesh, Visible)
      False → Set Visibility (Button_ChangeMesh, Hidden)
  False:
    Set Visibility (Button_ChangeMesh, Hidden)

← v1.2: update favorite tint sau khi set FurnitureDA
→ Call UpdateFavTint
```

---

### UpdateFavTint (Function) — v1.2

```
GET FurnitureDA → Get Object Name → String to Name → RowName

GET All Actors of Class(BP_FurnitureUserPrefsManager) → GET [0]
→ Is Favorite Mesh(RowName)
→ Branch:
  T → Set Color and Opacity(Button_FavoriteFurniture, R=1, G=0.3, B=0.3, A=1)   ← hồng
  F → Set Color and Opacity(Button_FavoriteFurniture, R=1, G=1, B=1, A=0.3)     ← mờ
```

---

### Button_FavoriteFurniture OnClicked — v1.2

```
GET FurnitureDA → Get Object Name → String to Name → RowName

GET All Actors of Class(BP_FurnitureUserPrefsManager) → GET [0]
→ Toggle Favorite Mesh(RowName)

→ Call UpdateFavTint
```

---

### BTN_ChangeMesh OnClicked — v1.4 (Replace MULTI) → Call F_ExecuteReplace

**Event:** `BTN_ChangeMesh OnClicked → Call F_ExecuteReplace` (Function vì cần local var `LocalNewActors`).

#### F_ExecuteReplace (Function)
```
Local: LocalNewActors : Array<BP_FurnitureActor>

Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → FurnitureInputRef
GET MeshesToReplace → Length → Branch > 0 → False: Return        ← guard

CLEAR LocalNewActors
ForEach MeshesToReplace (OldActor):     ← LOOP BODY
  Branch IsValid(OldActor):
    True:
      GET Actor Location(OldActor) → LocalLoc
      GET Actor Rotation(OldActor) → LocalRot
      Cast OldActor → GET PlacementSurfaceType → LocalSurfType
      Spawn BP_FurnitureActor(LocalLoc, LocalRot) → Cast → NewActor
      Load Asset Blocking(FurnitureDA.Mesh) → Cast StaticMesh → GET FurnitureMesh(NewActor) → Set Static Mesh
      SET MeshPath, SET DAPath = Get Object Path(FurnitureDA), SET PlacementSurfaceType = LocalSurfType
      GET Tags(NewActor) → ADD "FurnitureSpawned" → SET Tags
      ADD NewActor → LocalNewActors          ← ⭐ v1.4 FIX: thiếu node này → mesh mới không được chọn + không replace tiếp được
      Destroy Actor(OldActor)                ← target = Array Element

ForEach Completed (KHÔNG trong Loop Body):
  DeselectAll → SelectActors(LocalNewActors)     ← chọn lại các đồ mới
  Get All Actors Of Class(BP_UndoManager)[0] → CaptureSnapshot("Replace")
  GET All Actors(BP_FurnitureUserPrefsManager)[0] → AddRecentMesh(String to Name(Get Object Name(FurnitureDA)))
  SET MeshesToReplace = LocalNewActors           ← để replace TIẾP được (folder nav sẽ cập nhật MeshesToReplace = SelectedActors qua OnSelectionChanged)
  ← Inventory vẫn mở, giữ Replace mode active
```

**⚠️ Bug đã trả giá (v1.4):**
- **Thiếu ADD New Actor → LocalNewActors** trong Loop Body → LocalNewActors rỗng → SelectActors(rỗng) (mesh mới không được chọn) + SET MeshesToReplace(rỗng) (không replace tiếp được). Phải có node ADD.
- **CaptureSnapshot/SelectActors phải ở Completed, KHÔNG Loop Body** (nếu không sẽ chạy N lần).
- Dùng **MeshesToReplace (array)**, KHÔNG dùng MeshToReplace (single — đã xóa).

---

### Button_InforItem OnClicked
```
Call OnCardInfoClicked(FurnitureDA)
```

---

### On Drag Detected
```
1. DeactivateGizmo  ← PHẢI đầu tiên — restore collision trước khi spawn preview
2. Create WBP_DragVisual → Not Hit-Testable
3. Create BP_DragDropOperation_FurnitureCard → SET FurnitureDA
4. Spawn BP_FurnitureActor (0,0,0) → Load Mesh → Set Static Mesh
   ← KHÔNG set ghost material — dùng material gốc
5. SET PreviewActor
6. Create WBP_DragOverlay → Add to Viewport → SET PreviewActorRef
7. Return Operation
```

---

### On Drag Cancelled
```
IsValid(DragOverlayRef) → Remove from Parent → SET None
IsValid(PreviewActor) → Destroy Actor → SET None
```

---

---

# WBP_DragOverlay
**Cập nhật:** 21/04/2026 — 16:46:18 ICT | Widget trong suốt phủ toàn màn hình

---

## Variables
```
PreviewActorRef    : BP_FurnitureActor
PendingFurnitureDA : DA_FurnitureItem
```

---

## On Drag Over
```
1. Get Screen Space Position - WindowOffset → Deproject
   → Line Trace (Visibility, bTraceComplex=True, IgnoredActors=[PreviewActorRef])
   → Hit Location, Hit Normal, ReturnValue

2. Branch ReturnValue == True AND IsValid(PreviewActorRef):
   Set Actor Location = Hit Location

   SURFACE ROTATION + PlacementSurfaceType (v1.2):
   Break Normal → Normal.Z
   Normal.Z < -0.5 (ceiling) → Rotator 0,0,0
                               SET PlacementSurfaceType = "Ceiling"
   Normal.Z > 0.5 (floor)   → Rotator 0,0,0
                               SET PlacementSurfaceType = "Floor"
   Wall → Make Rot from X(Normal) → Break → Make Rotator(Roll, Pitch, Yaw-90)
          SET PlacementSurfaceType = "Wall"
```

---

## On Drop
```
1. Cast Operation → GET FurnitureDA → SET PendingFurnitureDA
2. Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → GET GizmoControllerRef → DeactivateGizmo
3. Line Trace → Hit Location
4. GET PreviewActorRef (dùng lại, không spawn mới)
5. Load Asset Blocking → Set Static Mesh
6. SET MeshPath, SET DAPath
7. GET Tags → ADD "FurnitureSpawned"  ← KHÔNG SET Tags sau ADD
8. CaptureSnapshot("Spawn")
9. Remove DragOverlay

← C1: AddRecentMesh sau spawn thành công
GET All Actors of Class(BP_FurnitureUserPrefsManager) → GET [0]
→ AddRecentMesh( String to Name( Get Object Name(PendingFurnitureDA) ) )
```

---

## Key Notes
- **Floor/Ceiling:** Rotator 0,0,0 — giữ pivot gốc
- **Wall:** Make Rot from X + Yaw-90 — mesh đứng thẳng áp tường
- **bTraceComplex = True** — trace geometry không có collision box
- **Move mode KHÔNG snap surface** — snap chỉ khi drag & drop lần đầu
- **Pivot mesh = điểm lắp đặt thực tế** — không cần offset

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 22/04/2026 | Logic gốc: DragDrop, Replace Mesh, DragOverlay |
| 1.1 | 22/05/2026 | Thêm PlacementSurfaceType copy trong BTN_ChangeMesh |
| 1.2 | 25/05/2026 — 15:03 ICT | Thêm Button_FavoriteFurniture + UpdateFavTint. AddRecentMesh sau Replace và sau Drag&Drop. Sửa tên file: widget thực là WBP_FurnitureCard |
| 1.3 | 25/05/2026 — 17:29 ICT | Replace Mode UX: giữ inventory mở sau replace, SET MeshToReplace = SelectedFurnitureActor thay vì None, xóa Remove from Parent |
| 1.4 | 10/06/2026 — 20:34 ICT | Replace MULTI: BTN_ChangeMesh → F_ExecuteReplace (ForEach MeshesToReplace). Fix thiếu ADD New Actor → LocalNewActors. Cuối Completed: DeselectAll + SelectActors(LocalNewActors) + CaptureSnapshot + AddRecentMesh + SET MeshesToReplace = LocalNewActors. Bỏ biến chết MeshToReplace (single). |
