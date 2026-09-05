# BP_FurnitureActor
**Tách từ:** `BP_FurnitureActor_SceneManager.md` (phần Actor)
**Phiên bản:** 2.1 | **Cập nhật:** 05/09/2026 — thêm biến `MaterialSlots` (S7.G2 Bước 0) | Parent: StaticMeshActor | Interface: EMSActorSaveInterface

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
MaterialSlots         : Array of FMaterialSlotRecord ← SaveGame (S7.G2 Bước 0, 05/09/2026) — kho ghi material theo tên slot (name-based), qua MaterialSlotService. Xem Data/MaterialSlotService_Reference.md
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

## Async Load Events (v2.0 — 19/06/2026)
Đặt trong BP_FurnitureActor, KHÔNG phải InputManager. Lý do: mỗi instance actor có node graph riêng → nhiều actor load song song không share class var, không aliasing.

### LoadMeshAsync(MeshPath : String) — Custom Event
```
Make Soft Object Path(MeshPath) → To Soft Object Reference → Async Load Asset

Completed:
  Cast Object → As Static Mesh
  Branch IsValid(As Static Mesh):
    True  → GET FurnitureMesh (Self) → Set Static Mesh(New Mesh = As Static Mesh)
    False → Print "LoadMeshAsync fail: " + MeshPath  [Development Only]
```
Self = actor tự set mesh của chính nó. Không cần TargetActor.

### LoadMaterialsAsync(Overrides : Array of String, Index : Integer) — Custom Event (đệ quy)
```
Branch: Index >= Overrides.Length → [dead-end, xong đệ quy]

False → Branch: Overrides[Index] != ""
  True  → Make Soft Object Path(Overrides[Index]) → Async Load Asset
            Completed:
              Cast → As Material Interface
              Branch IsValid(As Material Interface):
                True  → GET FurnitureMesh(Self) → Create Dynamic Material Instance(Element Index, Source=MI)
                        → Call LoadMaterialsAsync(Overrides, Index+1)
                False → Call LoadMaterialsAsync(Overrides, Index+1)
  False → Call LoadMaterialsAsync(Overrides, Index+1)
```
⚠️ Cả 2 nhánh True/False của IsValid đều phải gọi đệ quy Index+1 — không thì slot fail làm đứng đệ quy.

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 22/04/2026 | Logic gốc — BeginPlay SET FurnitureSpawned tag, ActorLoaded restore mesh |
| 1.1 | 22/05/2026 | Thêm MaterialOverrides + MaterialParams (SaveGame v1.1) |
| 1.2 | 17/06/2026 — Sprint D.T6 | Thêm RowName : Name (SaveGame) — key DT_FurnitureCatalog. DAPath giữ fallback save cũ. GroupID [?] giải quyết: String SaveGame (Sprint 3 T2). |
| 2.0 | 19/06/2026 — 19h ICT | Thêm LoadMeshAsync + LoadMaterialsAsync (async load tự quản lý trong actor, không gọi hộ từ InputManager) |
| 2.1 | 05/09/2026 | Thêm `MaterialSlots : Array<FMaterialSlotRecord>` (SaveGame) — S7.G2 Bước 0, kho ghi material mới (name-based) qua `MaterialSlotService` |
