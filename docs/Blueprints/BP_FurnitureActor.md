# BP_FurnitureActor
**Tách từ:** `BP_FurnitureActor_SceneManager.md` (phần Actor)
**Phiên bản:** 1.1 | **Cập nhật:** 22/05/2026 | Parent: StaticMeshActor | Interface: EMSActorSaveInterface

> **[?] Q5:** GroupID variable cần thêm vào Variables section. GroupID được SET runtime từ F_ExecuteReplace (WBP_DragOverlay_FurnitureCard), On Drop (WBP_DragOverlay), và CreateGroup (BP_FurnitureInputManager). Chưa verify kiểu dữ liệu chính xác từ Blueprint. Tạm ghi String.

---

## Variables
```
MeshPath              : String    ← SaveGame
DAPath                : String    ← SaveGame
MaterialOverrides     : Array of String ← SaveGame (v1.1) — package path MI theo slot index
MaterialParams        : Array of String ← SaveGame (v1.1 placeholder — JSON per slot cho v1.2)
PlacementSurfaceType  : Name      ← SaveGame (v1.2 UX) — "Floor" | "Wall" | "Ceiling", default="Floor"
FurnitureMesh         : StaticMeshComponent (Mobility = Movable)
GroupID               : String    ← [?] runtime var — ID của group chứa actor này; "" = đồ rời. Cần verify SaveGame hay không.
```

---

## Event BeginPlay
```
GET Tags (Self) → SET TempTags → ADD "FurnitureSpawned" → SET Tags (Self)
```
> ⚠️ KHÔNG dùng SET Tags trực tiếp — EMS dùng Tags để track state.

---

## Event ActorLoaded (EMSActorSaveInterface)
```
Wait For Save or Load Completed (Load Only) → On Completed:
  Branch MeshPath != "":
    True:
      Make Soft Object Path (MeshPath) → Load Asset Blocking → Cast To StaticMesh
      → Set Static Mesh (FurnitureMesh)
      GET Tags → ADD "FurnitureSpawned" → SET Tags
    False:
      Destroy Actor (Self)
```

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 22/04/2026 | Logic gốc — BeginPlay SET FurnitureSpawned tag, ActorLoaded restore mesh |
| 1.1 | 22/05/2026 | Thêm MaterialOverrides + MaterialParams (SaveGame v1.1) |
