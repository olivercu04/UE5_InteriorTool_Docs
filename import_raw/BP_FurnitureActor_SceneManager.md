# BP_FurnitureActor
**Phiên bản:** 1.1 | **Cập nhật:** 22/05/2026 | Parent: StaticMeshActor | Interface: EMSActorSaveInterface

---

## Variables
```
MeshPath              : String    ← SaveGame
DAPath                : String    ← SaveGame
MaterialOverrides     : Array of String ← SaveGame (v1.1) — package path MI theo slot index
MaterialParams        : Array of String ← SaveGame (v1.1 placeholder — JSON per slot cho v1.2)
PlacementSurfaceType  : Name      ← SaveGame (v1.2 UX) — "Floor" | "Wall" | "Ceiling", default="Floor"
FurnitureMesh         : StaticMeshComponent (Mobility = Movable)
```

---

## Event BeginPlay
```
GET Tags (Self) → SET TempTags → ADD "FurnitureSpawned" → SET Tags (Self)
⚠️ KHÔNG dùng SET Tags trực tiếp — EMS dùng Tags để track state
```

---

## Event ActorLoaded (EMSActorSaveInterface)
```
Wait For Save or Load Completed (Load Only) → On Completed:
  Branch MeshPath != ""?
    True:
      Make Soft Object Path (MeshPath) → Load Asset Blocking → Cast To StaticMesh
      → Set Static Mesh (FurnitureMesh)
      GET Tags → ADD "FurnitureSpawned" → SET Tags
    False:
      Destroy Actor (Self)
```

---

---

# BP_FurnitureSceneManager
**Cập nhật:** 05/05/2026 | Actor riêng — quản lý EMS Save/Load

---

## Variables
```
SaveGameMenuRef : SaveGameMenu (Object Reference)
```

---

## Event Tick
```
Get All Widgets Of Class(SaveGameMenu) → FoundWidgets
Branch Length(FoundWidgets) > 0?  ← PHẢI check trước GET(0)
  True → GET(0) → IsValid?
    True:
      Branch SaveGameMenuRef != Get(0)?
        True:
          SET SaveGameMenuRef = Get(0)
          Bind OnLoadButtonClicked
```

---

## OnLoadButtonClicked
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → DeselectMesh
← PHẢI trước Destroy — deactivate gizmo trước khi actors bị destroy

Get All Actors With Tag("FurnitureSpawned") → For Each → Destroy Actor
```

---

## SaveFurnitureScene
```
Get Current Save Slot → Set Current Save Slot → Save Game Actors (Level Only)
```

---

## LoadFurnitureScene
```
Get Current Save Slot → Set Current Save Slot → Load Game Actors (Level Only, Full Reload = True)
```
