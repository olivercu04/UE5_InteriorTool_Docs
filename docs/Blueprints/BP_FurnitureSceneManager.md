# BP_FurnitureSceneManager
**Tách từ:** `BP_FurnitureActor_SceneManager.md` (phần SceneManager)
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
Branch Length(FoundWidgets) > 0:   ← PHẢI check trước GET(0)
  True → GET(0) → IsValid:
    True:
      Branch SaveGameMenuRef != Get(0):
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

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 05/05/2026 | Logic gốc — Event Tick rebind SaveGameMenu, OnLoadButtonClicked destroy + reload, Save/Load functions |
