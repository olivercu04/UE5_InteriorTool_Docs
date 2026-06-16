# Kế hoạch UX Phase 2.1 — Tối ưu thao tác
**Phiên bản:** 1.1 | **Cập nhật:** 20/05/2026 | Project: Lighting_Mnger (UE5.5.4)

---

## Tổng quan

7 issues, chia 3 đợt:
- **Đợt A — Gizmo:** Rotate Gizmo (scale + direction), Translation Gizmo (chọn trục + slip)
- **Đợt B — Thao tác:** Copy/Paste Mesh, Arrow Key Move (Nudge)
- **Đợt C — Inventory:** History (Recent), Favorites

---

## Đợt A — Gizmo Fixes (làm TRƯỚC vì ảnh hưởng mọi thao tác)

### A1 — Rotate Gizmo: Scale theo distance từ camera

**Vấn đề:** Gizmo càng xa camera càng to → mất proportion, khó thao tác.

**Root cause:** Gizmo scale theo world space, không theo screen space.

**Fix:** Trong **BP_GizmoController → Event Tick**, sau khi gizmo active:
```
GET Camera Location
GET Gizmo Actor Location (SelectedFurnitureActor)
→ VectorLength(Camera - Gizmo) → Distance

GizmoScale = Distance × 0.03   ← tune hệ số này
SET RotationGizmoRef → SetActorScale3D(GizmoScale, GizmoScale, GizmoScale)
SET TranslationGizmoRef → SetActorScale3D(...)
SET ScaleGizmoRef → SetActorScale3D(...)
```
⚠️ Chỉ chạy khi bGizmoActive = True để tránh tốn Tick khi gizmo ẩn.
⚠️ Tune hệ số 0.03 sao cho ở khoảng cách 300cm gizmo vừa nhìn.

**Files:** BP_GizmoController
**Độ phức tạp:** ★★☆☆☆

---

### A2 — Rotate Gizmo: Hướng xoay bị ngược

**Vấn đề:** Kéo chuột sang phải → mesh xoay ngược chiều mong đợi.

**Fix:** Trong **BP_GizmoController**, tìm chỗ tính rotation delta:
```
AccumulatedRotation += MouseDeltaX × RotationSpeed
```
Đổi thành:
```
AccumulatedRotation += MouseDeltaX × RotationSpeed × (-1)
```
Hoặc negate RotationSpeed thành số âm.

⚠️ Cần test từng trục (X/Y/Z) — có thể chỉ 1 trục bị ngược.

**Files:** BP_GizmoController
**Độ phức tạp:** ★☆☆☆☆

---

### A3 — Translation Gizmo: Khó chọn trục + dễ trượt

**Vấn đề 1 — Khó chọn trục:**
Collision box axis arrow quá nhỏ → phải click rất chính xác.

**Fix:** Mở từng gizmo BP (BP_TranslationGizmo_Example) → tìm collision component của từng trục (X/Y/Z arrow) → **tăng kích thước collision box** (tăng gấp 1.5-2x theo chiều ngang trục).

⚠️ Tăng theo chiều ngang, không tăng dọc trục → tránh overlap giữa các trục.

**Vấn đề 2 — Dễ trượt sang trục khác khi kéo:**
Sau khi chọn được trục, chuột lệch nhẹ → trace hit trục khác → gizmo jump sang trục.

**Fix — "Axis Lock":** Trong **BP_GizmoController**, sau khi `OnMousePressed` chọn được trục:
```
SET LockedAxis = HitComponentName   ← lưu tên trục đang kéo
SET bAxisLocked = True
```

Trong **Event Tick** (phần xử lý movement):
```
Branch bAxisLocked:
  T → dùng LockedAxis, bỏ qua LineTrace chọn trục mới
  F → LineTrace chọn trục như bình thường
```

Trong **OnMouseReleased**:
```
SET bAxisLocked = False
SET LockedAxis = ""
```

**Variables cần thêm vào BP_GizmoController:**
```
bAxisLocked : Boolean
LockedAxis  : String
```

**Files:** BP_TranslationGizmo_Example, BP_GizmoController
**Độ phức tạp:** ★★★☆☆

---

## Đợt B — Thao tác Core

### B1 — Arrow Key Move (Nudge)

**Mục tiêu:** Arrow keys di chuyển mesh theo hướng camera, mỗi lần = 1 SnapStep.

**Logic nằm trong BP_FurnitureInputManager** (không phải BP_FoffPlayerController).
BP_FoffPlayerController chỉ route signal → gọi `NudgeMesh` trên InputManager.

#### Input
Thêm vào `LM_FurnitureInput`:
```
IA_FurnitureNudge  | Up Arrow    | Pressed
IA_FurnitureNudge  | Down Arrow  | Pressed
IA_FurnitureNudge  | Left Arrow  | Pressed
IA_FurnitureNudge  | Right Arrow | Pressed
```
Dùng 4 mapping riêng, mỗi cái ActionValue = Vector2D khác nhau thông qua Modifier.

#### BP_FoffPlayerController (chỉ route)
```
EnhancedInputAction IA_FurnitureNudge (Started):
  GET BP_FurnitureInputManager → Call NudgeMesh(ActionValue.XY)
```
PlayerController không chứa logic, chỉ forward signal.

#### BP_FurnitureInputManager — Custom Event `NudgeMesh(Direction: Vector2D)`
```
Branch IsValid(SelectedFurnitureActor):
  T → GET PlayerCamera → GetForwardVector, GetRightVector
      Project to horizontal: Forward.Z=0, Right.Z=0 → Normalize

      Offset = (Right × Direction.X + Forward × Direction.Y) × SnapStep
      AddActorWorldOffset(SelectedFurnitureActor, Offset, bSweep=False)

      ClearTimer(NudgeSnapshotTimer)
      SetTimerByFunctionName("CaptureNudgeSnapshot", 0.5s)  ← debounce
```

#### BP_FurnitureInputManager — Custom Event `CaptureNudgeSnapshot`
```
CaptureSnapshot("Nudge")
```

⚠️ **Debounce 0.5s:** nhấn liên tục nhiều lần chỉ tạo 1 snapshot khi dừng → history không bị đầy.

**Variables thêm vào BP_FurnitureInputManager:**
```
NudgeSnapshotTimerHandle : Timer Handle
```

**Files:** LM_FurnitureInput, BP_FoffPlayerController (3 dòng), BP_FurnitureInputManager
**Độ phức tạp:** ★★☆☆☆

---

### B2 — Copy/Paste Mesh

**Mục tiêu:**
- Ctrl+C: copy mesh đang chọn (transform + material)
- Ctrl+V: paste tại vị trí chuột (trace xuống bề mặt, giống drag & drop)

#### Clipboard Variables (thêm vào BP_FurnitureInputManager)
```
ClipboardMeshPath          : String
ClipboardDAPath            : String
ClipboardRotation          : Rotator
ClipboardScale             : Vector
ClipboardMaterialOverrides : Array of String
```
Primitive types → không hard ref → không cần clear EndPlay.

#### Input
Thêm vào `LM_FurnitureInput`:
```
IA_FurnitureCopy   | C | Chord IA_Ctrl + Pressed
IA_FurnitureCopy   | C | (no trigger — consume block C)
IA_FurniturePaste  | V | Chord IA_Ctrl + Pressed
IA_FurniturePaste  | V | (no trigger — consume block V)
```

#### BP_FoffPlayerController — chỉ route
```
IA_FurnitureCopy (Started)  → GET BP_FurnitureInputManager → Call CopyMesh
IA_FurniturePaste (Started) → GET BP_FurnitureInputManager → Call PasteMesh
```

#### BP_FurnitureInputManager — Custom Event `CopyMesh`
```
Branch IsValid(SelectedFurnitureActor):
  T → Cast BP_FurnitureActor
      SET ClipboardMeshPath = MeshPath
      SET ClipboardDAPath = DAPath
      SET ClipboardRotation = GetActorRotation
      SET ClipboardScale = GetActorScale3D
      SET ClipboardMaterialOverrides = MaterialOverrides
      ← Optional: flash UI feedback (highlight border copy?)
```

#### BP_FurnitureInputManager — Custom Event `PasteMesh`
```
Branch ClipboardMeshPath != "":
  T → ← Vị trí paste: trace từ chuột xuống bề mặt
        GET Player Controller → GET Mouse Position (X, Y)
        DeprojectScreenToWorld → WorldOrigin, WorldDirection
        LineTrace (WorldOrigin, WorldOrigin + WorldDirection × 5000)
          Channel = Camera, bTraceComplex = True
        Branch Hit:
          T → PasteLocation = HitResult.Location
          F → PasteLocation = Camera + Forward × 300  ← fallback

      SpawnActor(BP_FurnitureActor, PasteLocation, ClipboardRotation)
      Load Asset Blocking(ClipboardMeshPath) → SetStaticMesh
      SET MeshPath = ClipboardMeshPath
      SET DAPath = ClipboardDAPath
      SetActorScale3D(ClipboardScale)
      GET Tags → ADD "FurnitureSpawned"

      ← Restore materials:
      For Each ClipboardMaterialOverrides (Index, Path):
        Branch Path != "":
          Load Asset Blocking → Cast MaterialInterface
          Create DMI(FurnitureMesh, MI, Index) → SetMaterial(Index)
      SET MaterialOverrides = ClipboardMaterialOverrides

      ← Select mesh mới:
      DeselectMesh
      SET SelectedFurnitureActor = SpawnedActor
      Cast BP_FurnitureActor → SET SelectedFurnitureActor (InputManager)
      SetCustomDepth(True, 255)
      Branch ActiveMode != Select → ActivateGizmo

      CaptureSnapshot("Paste")
```

**Files:** LM_FurnitureInput, BP_FoffPlayerController (2 dòng), BP_FurnitureInputManager
**Độ phức tạp:** ★★★☆☆

---

## Đợt C — Inventory UX (History + Favorites)

### Thiết kế Data — SaveGame riêng cho User Preferences

**Vì global user (không gắn scene)** → cần file SaveGame riêng, không dùng BP_FurnitureSceneManager.

#### Tạo mới: `BP_UserPreferencesSave` (SaveGame Object)
```
RecentMeshes      : Array of Name   ← max 20, RowName DA_FurnitureItem
RecentMaterials   : Array of Name   ← max 20, RowName DT_MaterialInstancesCatalog
FavoriteMeshes    : Array of Name   ← không giới hạn
FavoriteMaterials : Array of Name   ← không giới hạn
```

⚠️ Tất cả là `Name` (RowName) theo R5 — không lưu path, không lưu object ref.

#### Tạo mới: `BP_FurnitureUserPrefsManager` (Actor)
Singleton quản lý load/save user prefs, spawn cùng các manager khác.
```
Variables:
  UserPrefs : BP_UserPreferencesSave   ← reference tới save object

Functions:
  LoadUserPrefs  → EMS Load slot "FurnitureUserPrefs"
  SaveUserPrefs  → EMS Save slot "FurnitureUserPrefs"
  AddRecentMesh(RowName)      → INSERT front, remove dup, cap 20 → Save
  AddRecentMaterial(RowName)  → INSERT front, remove dup, cap 20 → Save
  ToggleFavoriteMesh(RowName)     → ADD nếu chưa có / REMOVE nếu đã có → Save
  ToggleFavoriteMaterial(RowName) → tương tự
  IsFavoriteMesh(RowName)     → CONTAINS → return bool
  IsFavoriteMaterial(RowName) → tương tự
```

#### Spawn order
Thêm vào WBP_FOFF_ToolDemo Event Construct (Then 7):
```
Spawn BP_FurnitureUserPrefsManager → Call LoadUserPrefs
```

---

### C1 — History (Recently Used)

**Khi ghi history:**
- Sau Drag&Drop spawn thành công → `GET BP_FurnitureUserPrefsManager → AddRecentMesh(DARowName)`
- Sau PasteMesh thành công → `AddRecentMesh(ClipboardDAPath → extract RowName)`
- Sau ApplyMaterial thành công → `AddRecentMaterial(PendingRowName)`

**UI — Category "Recent":**
Trong WBP_FurnitureInventory, thêm button "Recent" vào category bar:
```
Category bar: [All] [Recent] [★] [Surface] [Stone] [Fabric]...
```

`FilterBySearch` nhận `CategoryFilter = "Recent"`:
```
Branch CategoryFilter == "Recent":
  Furniture → GET BP_FurnitureUserPrefsManager → RecentMeshes
              ForEach RowName → GetDataTableRow(DA_) → Populate CTV_FurnitureCard
  Material  → GET BP_FurnitureUserPrefsManager → RecentMaterials
              ForEach RowName → GetDataTableRow(DT_MI) → Populate CTV_MaterialCard
```

**Files:** BP_FurnitureUserPrefsManager (tạo mới), WBP_FurnitureInventory, WBP_DragOverlay, Spawn Order
**Độ phức tạp:** ★★★☆☆

---

### C2 — Favorites

**UI — Nút ⭐ trên Card:**

`WBP_FurnitureCard` — thêm `BTN_Favorite` (⭐ nhỏ, góc phải trên card):
```
On Construct:
  IsFavoriteMesh(RowName) → SET BTN_Favorite Tint (sáng/mờ)

OnClicked(BTN_Favorite):
  GET BP_FurnitureUserPrefsManager → ToggleFavoriteMesh(RowName)
  IsFavoriteMesh(RowName) → SET BTN_Favorite Tint
```

`WBP_MaterialCard` — tương tự với ToggleFavoriteMaterial.

**UI — Category "★":**
Button ★ trong category bar → `FilterByCategory("Favorite")`:
```
Branch CategoryFilter == "Favorite":
  Furniture → FavoriteMeshes → populate card
  Material  → FavoriteMaterials → populate card
```

**Files:** WBP_FurnitureCard, WBP_MaterialCard, WBP_FurnitureInventory
**Độ phức tạp:** ★★★☆☆

---

## Thứ tự triển khai

```
Đợt A — Gizmo ✅ HOÀN THÀNH
  A1. Rotate Gizmo scale theo distance              ✅
  A2. Rotate Gizmo hướng xoay                       ✅
  A3. Translation Gizmo collision + Axis Lock        ✅
  Bonus: Xóa disable collision ActivateGizmo         ✅

Đợt B — Thao tác core ✅ HOÀN THÀNH
  B1. Arrow Key Nudge                               ✅
      + PlacementSurfaceType (wall/floor/ceiling)   ✅
      + Snap 90° wall và floor branch               ✅
  B2. Copy/Paste/Duplicate                          ✅
      + IA_Block_C/V/D                              ✅
      + PlacementSurfaceType trong SpawnFurnitureCopy ✅

Đợt C — Inventory UX ✅ HOÀN THÀNH
  C0. BP_FurnitureUserPrefsManager (data layer)     ✅
  C1. History (Recent category)                     ✅
  C2. Favorites (⭐ button + Favorites category)     ✅
```

---

## Files bị ảnh hưởng — Tổng hợp

| File | Đợt | Thay đổi |
|---|---|---|
| BP_GizmoController | A1, A2, A3 | Scale Tick, negate delta, Axis Lock vars, xóa disable collision |
| BP_TranslationGizmo_Example | A3 | Tăng collision box |
| LM_FurnitureInput | B1, B2 | IA_FurnitureNudge, Copy, Paste, Duplicate, IA_Block_C/V/D |
| BP_FoffPlayerController | B1, B2 | Route actions → InputManager |
| BP_FurnitureInputManager | B1, B2 | NudgeMesh (wall/floor), CopyMesh, PasteMesh, DuplicateMesh, SpawnFurnitureCopy(+SurfaceType), Tick wall/floor |
| BP_FurnitureActor | B1 | PlacementSurfaceType : Name (SaveGame) |
| S_FurniturePlacement | B1 | SurfaceType : Name field |
| BP_UndoManager | B1 | CaptureSnapshot lưu SurfaceType, RestoreSnapshot restore |
| WBP_DragOverlay | B1 | On Drag Over SET PlacementSurfaceType từ HitNormal |
| WBP_DragOverlay_FurnitureCard | B2 | BTN_ChangeMesh copy PlacementSurfaceType |
| BP_FurnitureUserPrefsManager | C0 | Tạo mới |
| BP_UserPreferencesSave | C0 | Tạo mới (SaveGame Object) |
| WBP_FOFF_ToolDemo | C0 | Spawn PrefsManager |
| WBP_FurnitureInventory | C1, C2 | Category Recent + Favorites |
| WBP_FurnitureCard | C2 | Nút ⭐ |
| WBP_MaterialCard | C2 | Nút ⭐ |
| WBP_DragOverlay | C1 | AddRecentMesh sau spawn |

---

## Nguyên tắc áp dụng

- **R2:** Không hard ref mới trong Widget (⭐ button gọi qua function, không giữ ref)
- **R4:** WBP_FurnitureCard/MaterialCard Event Destruct clear RowName (Name type = không cần clear, primitive)
- **R5:** Tất cả lưu RowName (Name), không lưu path
- **CaptureSnapshot:** Paste → immediate. Nudge → debounce 0.5s.
- **Axis Lock:** bAxisLocked SET False ở OnMouseReleased — bắt buộc, không thì gizmo bị kẹt.

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 20/05/2026 | Tạo mới — plan ban đầu 5 features |
| 1.1 | 20/05/2026 | Update theo feedback: Gizmo fixes (scale+direction+axis lock), Arrow key route qua InputManager, Paste tại chuột, History+Favorites global SaveGame riêng |
| 1.2 | 25/05/2026 — 15:03 ICT | Đợt C hoàn thành: C0+C1+C2 ✅. Thêm toggle logic Recent/Favorite, persist khi switch mode, UpdateSpecialHighlight, AddRecentMesh sau Replace |
