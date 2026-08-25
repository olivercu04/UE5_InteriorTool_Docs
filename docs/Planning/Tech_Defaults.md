# Tech Defaults — Giá trị mặc định kỹ thuật
**Phiên bản:** 1.2 | **Dự án:** Lighting_Mnger | **Cập nhật:** 24/08/2026 — Selection Outline: Post Process Component (gắn BP_FurnitureSceneManager) thay PostProcessVolume actor, verify PASS Editor

---

## Engine & Tools

- **Engine:** UE5.5.4
- **IDE:** Visual Studio 2022
- **Plugin:** RuntimeTransformer (UE4 port, fix UE5: HitResult.Actor → HitResult.GetActor())
- **Save/Load:** Easy Multi Save (EMS), dùng chung slot với project tổng

---

## Snap Defaults

| | Default | Ý nghĩa |
|---|---|---|
| SnapStep (Move) | 10 | 10cm mỗi bước |
| SnapAngle (Rotate) | 15 | 15° mỗi bước |
| RotationSpeed | 0.3 | Nhân với mouse delta |
| 0 = tự do | — | Không snap |

---

## Gizmo

- **Translation Gizmo:** BP_TranslationGizmo_Example
- **Rotation Gizmo:** BP_Rotation_Gizmo_Example — Collision phải đổi thành Query Only
- **Scale Gizmo:** BP_Scale_Gizmo_Example — Collision phải đổi thành Query Only
- **ETransformationType:** None / Translation / Rotation / Scale (plugin enum)

---

## Collision

- **FurnitureSpawned:** Query And Physics (mặc định)
- **Non-FurnitureSpawned khi Gizmo active:** No Collision
- **BaseGizmo components khi Gizmo active:** No Collision
- **Restore:** luôn chạy trong DeactivateGizmo (cả True và False branch)

---

## Selection Outline

- Custom Depth Stencil Pass = Enabled with Stencil
- Stencil Value = 255
- Post Process Component (gắn trên BP_FurnitureSceneManager, KHÔNG dùng PostProcessVolume actor riêng
  — Volume actor cần brush hình học, không spawn/subclass được qua Blueprint picker ở nhiều project):
  Unbound = True, Post Process Materials += M_SelectionOutline
- M_SelectionOutline: Domain=PostProcess, Blendable=Translucency After DOF

---

## Undo/Redo

- MaxSteps = 50
- UniqueID = Get Display Name(Actor)
- S_SceneSnapshot: ActionName, Meshes, SelectedMeshIndex, ActiveMode
- RestoredBPActor: class var trên BP_UndoManager — clear ở EndPlay (v1.1)

---

## Paths

- Mesh: `/Game/DatabaseProjectMaster/Model/Object_Model/`
- Material Instances: `/Game/DatabaseProjectMaster/Material/MaterialInstances/`
- DA_: `/Game/cuong/UI/Data/FurnitureAssets/`
- DT Furniture: `/Game/cuong/UI/Data/DT_FurnitureCatalog`
- DT Material: `/Game/cuong/UI/Data/DT_MaterialInstancesCatalog`
- Thumbnails Material: `/Game/cuong/UI/Data/ThumbnailMaterialInstances/`

---

## Tags

- Mesh đã spawn: `"FurnitureSpawned"`
- Tags pipe-separated trong DA_: `"tag1|tag2|tag3"`

---

## Material v1.1

- **Apply flow:** Async Load → Create Dynamic Material Instance → Set Material → Debounce 0.5s → CaptureSnapshot
- **Debounce:** ApplyMaterialTimerHandle, 0.5s → CaptureMaterialSnapshot
- **Restore delay:** Timer 0.1s trong OnSceneRestored → ApplyRestoredActor (sau LeftMouseButton)
- **Thumbnail:** Texture2D 256x256, Texture Group UI, LOD Bias 2, ~50KB/file
- **SceneCapture2D:** Capture Source = "Final Color (LDR) in RGB" (fix black output)

---

## Drag & Drop Surface Rotation

- Floor (Normal.Z > 0.5): Rotator 0,0,0
- Ceiling (Normal.Z < -0.5): Rotator 0,0,0
- Wall: Make Rot from X(Normal) → Yaw - 90
- bTraceComplex = True cho Line Trace

---

## Engine & Tools

- **Engine:** UE5.5.4
- **IDE:** Visual Studio 2022
- **Plugin:** RuntimeTransformer (UE4 port, fix UE5: HitResult.Actor → HitResult.GetActor())
- **Save/Load:** Easy Multi Save (EMS), dùng chung slot với project tổng

---

## Snap Defaults

| | Default | Ý nghĩa |
|---|---|---|
| SnapStep (Move) | 10 | 10cm mỗi bước |
| SnapAngle (Rotate) | 15 | 15° mỗi bước |
| RotationSpeed | 0.3 | Nhân với mouse delta |
| 0 = tự do | — | Không snap |

---

## Gizmo

- **Translation Gizmo:** BP_TranslationGizmo_Example
- **Rotation Gizmo:** BP_Rotation_Gizmo_Example — Collision phải đổi thành Query Only
- **Scale Gizmo:** BP_Scale_Gizmo_Example — Collision phải đổi thành Query Only
- **ETransformationType:** None / Translation / Rotation / Scale (plugin enum)

---

## Collision

- **FurnitureSpawned:** Query And Physics (mặc định)
- **Non-FurnitureSpawned khi Gizmo active:** No Collision
- **BaseGizmo components khi Gizmo active:** No Collision
- **Restore:** luôn chạy trong DeactivateGizmo (cả True và False branch)

---

## Selection Outline

- Custom Depth Stencil Pass = Enabled with Stencil
- Stencil Value = 255
- Post Process Component (gắn trên BP_FurnitureSceneManager, KHÔNG dùng PostProcessVolume actor riêng
  — Volume actor cần brush hình học, không spawn/subclass được qua Blueprint picker ở nhiều project):
  Unbound = True, Post Process Materials += M_SelectionOutline
- M_SelectionOutline: Domain=PostProcess, Blendable=Translucency After DOF

---

## Undo/Redo

- MaxSteps = 50
- UniqueID = Get Display Name(Actor)
- S_SceneSnapshot: ActionName, Meshes, SelectedMeshIndex, ActiveMode

---

## Paths

- Mesh: `/Game/DatabaseProjectMaster/Model/Object_Model/`
- DA_: `/Game/cuong/UI/Data/FurnitureAssets/`
- DataTable: `/Game/cuong/UI/Data/DT_FurnitureCatalog`

---

## Tags

- Mesh đã spawn: `"FurnitureSpawned"`
- Tags pipe-separated trong DA_: `"tag1|tag2|tag3"`

---

## Drag & Drop Surface Rotation

- Floor (Normal.Z > 0.5): Rotator 0,0,0
- Ceiling (Normal.Z < -0.5): Rotator 0,0,0
- Wall: Make Rot from X(Normal) → Yaw - 90
- bTraceComplex = True cho Line Trace
