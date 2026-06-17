# BP_FurnitureActor
**Tách từ:** `BP_FurnitureActor_SceneManager.md` (phần Actor)
**Phiên bản:** 1.2 | **Cập nhật:** 17/06/2026 — Sprint D.T6 | Parent: StaticMeshActor | Interface: EMSActorSaveInterface

> **v1.2 (Sprint D.T6):** Thêm `RowName : Name (SaveGame)` — nguồn sự thật mới thay DA_FurnitureItem. DAPath giữ lại làm fallback cho save cũ chưa có RowName.

---

## Variables
```
MeshPath              : String    ← SaveGame
DAPath                : String    ← SaveGame (giữ làm fallback cho save cũ — xem Branch RowName == "" trong load path)
RowName               : Name      ← SaveGame (v1.2 Sprint D) — khóa tra DT_FurnitureCatalog; "" = chưa set (save cũ)
MaterialOverrides     : Array of String ← SaveGame (v1.1) — package path MI theo slot index
MaterialParams        : Array of String ← SaveGame (v1.1 placeholder — JSON per slot cho v1.2)
PlacementSurfaceType  : Name      ← SaveGame — "Floor" | "Wall" | "Ceiling", default="Floor"
FurnitureMesh         : StaticMeshComponent (Mobility = Movable)
GroupID               : String    ← SaveGame (xác nhận Sprint 3 T2) — ID của group chứa actor; "" = đồ rời
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
| 1.2 | 17/06/2026 — Sprint D.T6 | Thêm RowName : Name (SaveGame) — key DT_FurnitureCatalog. DAPath giữ fallback save cũ. GroupID [?] giải quyết: String SaveGame (Sprint 3 T2). |
