# WBP_FurnitureCard (+ WBP_DragOverlay) — Drag & Drop + Replace Mesh
**HỢP NHẤT TỪ 3 file:** v1.3 base (25/05) → v1.4 base (10/06) + Blueprint_Logic GroupID fix (12/06) + v1.5_patch (15/06)
**Phiên bản:** 1.5 | **Cập nhật:** 15/06/2026 — 20:30 ICT

> ⚠️ **Tên file gây nhầm lẫn:** Widget thực tế tên là `WBP_FurnitureCard`; không có widget `WBP_DragOverlay_FurnitureCard`. File này document cả `WBP_FurnitureCard` và `WBP_DragOverlay`.

> **v1.5 (Sprint 4 Bug Fix F4):** On Drop auto-join edit scope — sau ADD "FurnitureSpawned", check GetCurrentEditScope → SET GroupID nếu đang trong edit (L2: merge cả 2 nhánh, tránh dead-end gây mesh biến mất).
> **v1.4 BugFix (12/06):** F_ExecuteReplace preserve GroupID — GET GroupID từ OldActor → SET NewActor.GroupID TRƯỚC Destroy.
> **v1.4 (Sprint 2 multi + regression-fix):** BTN_ChangeMesh → F_ExecuteReplace (Function, local var). ForEach MeshesToReplace. Fix ADD New Actor → LocalNewActors. Bỏ biến chết MeshToReplace (single).
> **v1.2:** Button_FavoriteFurniture + UpdateFavTint. AddRecentMesh sau Replace và Drag&Drop.

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
      True  → Set Visibility(Button_ChangeMesh, Visible)
      False → Set Visibility(Button_ChangeMesh, Hidden)
  False:
    Set Visibility(Button_ChangeMesh, Hidden)

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

### BTN_ChangeMesh OnClicked — v1.4 (Replace MULTI)

**Event:** `BTN_ChangeMesh OnClicked → Call F_ExecuteReplace` (Function vì cần local var `LocalNewActors`).

#### F_ExecuteReplace (Function) — v1.4 + BugFix GroupID (12/06)
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
      Cast OldActor → BP_FurnitureActor → GET PlacementSurfaceType → LocalSurfType
      ← [BugFix 12/06] GET GroupID từ OldActor TRƯỚC khi destroy:
      Cast OldActor → BP_FurnitureActor → GET GroupID → OldGroupID
      Spawn BP_FurnitureActor(LocalLoc, LocalRot) → Cast → NewActor
      Load Asset Blocking(FurnitureDA.Mesh) → Cast StaticMesh → GET FurnitureMesh(NewActor) → Set Static Mesh
      SET MeshPath, SET DAPath = Get Object Path(FurnitureDA), SET PlacementSurfaceType = LocalSurfType
      ← [BugFix 12/06] SET GroupID = OldGroupID (TRƯỚC Destroy):
      SET NewActor.GroupID = OldGroupID
      GET Tags(NewActor) → ADD "FurnitureSpawned" → SET Tags
      ADD NewActor → LocalNewActors          ← ⭐ v1.4 FIX: thiếu node này → mesh mới không được chọn + không replace tiếp được
      Destroy Actor(OldActor)               ← target = Array Element

ForEach Completed (KHÔNG trong Loop Body):
  DeselectAll → SelectActors(LocalNewActors)     ← chọn lại các đồ mới
  Get All Actors Of Class(BP_UndoManager)[0] → CaptureSnapshot("Replace")
  GET All Actors(BP_FurnitureUserPrefsManager)[0] → AddRecentMesh(String to Name(Get Object Name(FurnitureDA)))
  SET MeshesToReplace = LocalNewActors           ← để replace TIẾP được (folder nav sẽ cập nhật MeshesToReplace = SelectedActors qua OnSelectionChanged)
  ← Inventory vẫn mở, giữ Replace mode active
```

**⚠️ Bug đã trả giá:**
- **[v1.4 fix]** Thiếu `ADD New Actor → LocalNewActors` trong Loop Body → LocalNewActors rỗng → SelectActors(rỗng) + SET MeshesToReplace(rỗng) → không replace tiếp được.
- **[12/06 fix]** GET GroupID PHẢI TRƯỚC Destroy Actor(OldActor) — sau destroy không đọc được nữa.
- CaptureSnapshot/SelectActors ở Completed, KHÔNG Loop Body (nếu không sẽ chạy N lần).
- Dùng MeshesToReplace (array), KHÔNG dùng MeshToReplace (single — đã xóa từ v1.4).

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
Widget trong suốt phủ toàn màn hình

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

## On Drop — v1.5: THÊM F4 auto-join edit scope

**Exec flow đầy đủ (trace từ Blueprint export 15/06/2026):**
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

      ← [v1.5 F4 INSERT — 15/06/2026]:
        Get All Actors Of Class(InputManager) → GET[0] → Cast → InputRef
        InputRef.GetCurrentEditScope() → Scope
        Branch(Scope != ""):
          True  → SET PreviewActorRef.GroupID = Scope → [merge]
          False →                                        [merge]   ← PHẢI merge — không dead-end
        [merge] →

      → Get All Actors Of Class(BP_UndoManager) → GET[0] → CaptureSnapshot("Spawn")
      → Get All Actors Of Class(BP_FurnitureUserPrefsManager) → GET[0] → AddRecentMesh
      → Remove From Parent
      → Return(true)
    False → dead-end
```

> ⚠️ **L2 CRITICAL:** Nhánh False của Branch(Scope != "") PHẢI merge về CaptureSnapshot — KHÔNG dead-end. False dead-end → On Drop không reach Return Node → trả false → UMG gọi On Drag Cancelled → Destroy PreviewActorRef → mesh biến mất (bug N5 trả giá 15/06).

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
| 1.2 | 25/05/2026 — 15:03 ICT | Thêm Button_FavoriteFurniture + UpdateFavTint. AddRecentMesh sau Replace và Drag&Drop. Sửa tên: widget thực là WBP_FurnitureCard |
| 1.3 | 25/05/2026 — 17:29 ICT | Replace Mode UX: giữ inventory mở sau replace, SET MeshToReplace = SelectedFurnitureActor, xóa Remove from Parent |
| 1.4 | 10/06/2026 — 20:34 ICT | **Replace MULTI:** BTN_ChangeMesh → F_ExecuteReplace (ForEach MeshesToReplace). Fix ADD New Actor → LocalNewActors. Completed: DeselectAll + SelectActors(LocalNewActors) + CaptureSnapshot + AddRecentMesh + SET MeshesToReplace = LocalNewActors. Bỏ biến chết MeshToReplace (single). |
| 1.4b | 12/06/2026 | **BugFix GroupID:** F_ExecuteReplace: GET OldActor.GroupID → SET NewActor.GroupID TRƯỚC Destroy OldActor (từ Blueprint_Logic v1.4 BugFix). |
| 1.5 | 15/06/2026 — 20:30 ICT | **F4: On Drop auto-join edit scope.** Sau ADD "FurnitureSpawned": get InputManager → GetCurrentEditScope → Branch(Scope!="") → SET PreviewActorRef.GroupID. Merge cả 2 nhánh về CaptureSnapshot (L2: False dead-end gây mesh biến mất — bug N5). |
