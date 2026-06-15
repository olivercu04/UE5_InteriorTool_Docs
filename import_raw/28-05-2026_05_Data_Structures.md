# 05 — Data Structures
**Mục đích:** Tham chiếu đầy đủ struct, enum, variables.

---

## STRUCTS

### S_FurniturePlacement (existing, mở rộng)

| Field | Kiểu | Default | Ghi chú |
|---|---|---|---|
| MeshPath | String | "" | Existing |
| DAPath | String | "" | Existing |
| Location | Vector | (0,0,0) | Existing |
| Rotation | Rotator | (0,0,0) | Existing |
| Scale | Vector | (1,1,1) | Existing |
| ActorTag | String | "" | Existing |
| UniqueID | String | "" | Existing, GetDisplayName |
| MaterialPaths | Array of String | [] | v1.1 |
| MaterialParams | Array of String | [] | v1.2 (Sprint 7) JSON per slot |
| SurfaceType | Name | "Floor" | v1.2 B1 |
| **GroupID** | **String** | **""** | **Sprint 3** |
| **bIsLocked** | **Boolean** | **False** | **Sprint 6** |
| **CustomName** | **String** | **""** | **Sprint 6** |

### S_GroupData (mới — Sprint 3)

| Field | Kiểu | Default | Ghi chú |
|---|---|---|---|
| GroupID | String | "" | Unique, "g_" prefix |
| GroupName | String | "Nhóm" | User-facing |
| ParentGroupID | String | "" | Empty = top-level |
| bIsLocked | Boolean | False | Khóa group |

### S_SceneSnapshot (mở rộng)

| Field | Kiểu | Default | Ghi chú |
|---|---|---|---|
| Version | Integer | 2 (sau S1), 3 (sau S3) | Mới Sprint 1 |
| ActionName | String | "" | Existing |
| Meshes | Array of S_FurniturePlacement | [] | Existing |
| SelectedMeshIndex | Integer | -1 | Existing (deprecated Version 2+) |
| SelectedMeshIndices | Array of Integer | [] | Mới Sprint 1 |
| Groups | Array of S_GroupData | [] | Mới Sprint 3 |
| EditingGroupID | String | "" | Mới Sprint 4 |
| ActiveMode | E_ActiveMode | Select | Existing |

### S_ClipboardEntry (mới — Sprint 1)

| Field | Kiểu | Default | Ghi chú |
|---|---|---|---|
| MeshPath | String | "" | |
| DAPath | String | "" | |
| RelativeLocation | Vector | (0,0,0) | So với clipboard center |
| Rotation | Rotator | (0,0,0) | |
| Scale | Vector | (1,1,1) | |
| MaterialOverrides | Array of String | [] | |
| SurfaceType | Name | "Floor" | |
| GroupID | String | "" | Sprint 3+ |

### S_ComboMeshData (mới — Sprint 5)

DataTable Row struct cho DT_ComboMeshCatalog.

| Field | Kiểu | Ghi chú |
|---|---|---|
| ComboName | String | "Bộ sofa Scandinavian" |
| Category | String | Phòng khách / Phòng ăn / ... |
| Style | String | Modern / Scandinavian / Industrial / ... |
| Tags | String | Pipe-separated: "bàn ăn|6 ghế|gỗ sồi" |
| ItemCount | Integer | Số mesh trong combo |
| ThumbnailPath | Soft Object Ref Texture2D | Auto-gen từ SceneCapture2D |
| ComboJSON | String | JSON serialized meshes + groups |

⚠️ **Dependency Sprint 5 ↔ Sprint 7:** Combo JSON schema có `materialParams` (cho Color/Roughness từ v1.2). Nếu Sprint 7 làm TRƯỚC khi user tạo combo → SaveCurrentGroupAsCombo phải serialize cả materialParams, SpawnCombo phải restore. Nếu Sprint 7 chưa xong → `materialParams` để mảng rỗng, không lỗi. **Khi làm Sprint 5: include field materialParams ngay cả khi để rỗng**, tránh phải sửa schema sau.

### S_ComboJSONEntry (struct nội bộ — không phải UE struct, JSON format)

```json
{
  "meshes": [
    {
      "meshPath": "/Game/.../SM_Chair.SM_Chair",
      "dapath": "/Game/.../DA_Chair.DA_Chair",
      "relativeLocation": {"x": 100, "y": 50, "z": 0},
      "rotation": {"pitch": 0, "yaw": 45, "roll": 0},
      "scale": {"x": 1, "y": 1, "z": 1},
      "materialOverrides": ["/Game/.../MI_Fabric.MI_Fabric"],
      "materialParams": ["{\"Tint\":[0.2,0.3,0.5,1],\"Roughness\":0.7}"],
      "surfaceType": "Floor",
      "groupID": "g_inner_1"
    }
  ],
  "groups": [
    {
      "groupID": "g_outer",
      "groupName": "Bộ sofa",
      "parentGroupID": ""
    },
    {
      "groupID": "g_inner_1",
      "groupName": "Cụm gối",
      "parentGroupID": "g_outer"
    }
  ]
}
```

---

## ENUMS

### E_ActiveMode (existing)
- Select | Move | Rotate | Scale

### E_InventoryMode (existing)
- Furniture | Material

### E_SelectSimilarCriteria (mới — Sprint 2)
- Mesh | Category | Folder | Material

### E_AlignDirection (mới — Sprint 6)
- Left | CenterH | Right | Top | CenterV | Bottom

### E_DistributeDirection (mới — Sprint 6)
- Horizontal | Vertical

### E_AlignReference (mới — Sprint 6)
- BoundingBox | Primary

---

## VARIABLES — BP_FurnitureInputManager (FINAL — sau Sprint 7)

### Selection
```
SelectedActors        : Array of BP_FurnitureActor
PrimarySelectedActor  : BP_FurnitureActor
SelectedFurnitureActor : BP_FurnitureActor (deprecated — = PrimarySelectedActor)
GizmoPivotActor       : BP_PivotActor (None khi single-select)
```

### Group (Sprint 3+)
```
Groups                : Array of S_GroupData
CurrentEditingGroupID : String (empty = không edit mode)
```

### Existing
```
CurrentMeshControls    : WBP_MeshControls
GizmoControllerRef     : BP_GizmoController
TransformerPawnRef     : BP_TransformerPawn
ActiveMode             : E_ActiveMode
LocalWasGizmoActive    : Boolean
DetailPopupRef         : WBP_DetailPopup
bIsReplaceMode         : Boolean
MeshToReplace          : BP_FurnitureActor
```

### Clipboard (refactored — Sprint 1)
```
ClipboardActors : Array of S_ClipboardEntry
```

### Nudge (existing)
```
NudgeSnapshotTimerHandle : Timer Handle
NudgeSpeed               : Float (150.0)
```

### Box Select (Sprint 2)
```
bIsBoxSelecting       : Boolean
BoxSelectOverlayRef   : WBP_BoxSelectOverlay
```

### Context Menu (Sprint 2)
```
CurrentContextMenu    : WBP_ContextMenu
```

---

## VARIABLES — BP_FurnitureActor (FINAL)

```
MeshPath              : String (SaveGame)
DAPath                : String (SaveGame)
MaterialOverrides     : Array of String (SaveGame) — v1.1
MaterialParams        : Array of String (SaveGame) — v1.1 placeholder, v1.2 active
PlacementSurfaceType  : Name (SaveGame) — v1.2 B1
GroupID               : String (SaveGame) — Sprint 3
bIsLocked             : Boolean (SaveGame) — Sprint 6
CustomName            : String (SaveGame) — Sprint 6
FurnitureMesh         : StaticMeshComponent
```

---

## EVENT DISPATCHERS — BP_FurnitureInputManager (FINAL)

### Active (Sprint 1+)
```
OnSelectionChanged(
  Actors  : Array of BP_FurnitureActor,
  Primary : BP_FurnitureActor
)
```

### Group (Sprint 3+)
```
OnGroupCreated(GroupID : String)
OnGroupDestroyed(GroupID : String)
OnGroupModeChanged(
  bIsEditMode    : Boolean,
  EditingGroupID : String
)
```

### Deprecated (vẫn fire để compat)
```
OnMeshSelected(BP_FurnitureActor)   — fire khi PrimarySelectedActor thay đổi
OnMeshDeselected()                   — fire khi SelectedActors empty
```

---

## TAGS

| Tag | Actor | Mục đích |
|---|---|---|
| "FurnitureSpawned" | BP_FurnitureActor | EMS save target, query với Get All Actors With Tag |
| "FurniturePivot" | BP_PivotActor | KHÔNG save bởi EMS, query để tránh nhầm với mesh |
| "FurnitureGroupsContainer" | BP_GroupsContainer | EMS save data Groups |

---

## CUSTOM DEPTH STENCIL VALUES

| Value | Mục đích |
|---|---|
| 255 | Primary selected actor (outline đậm) |
| 254 | Secondary selected actor (outline nhạt) |
| 0 | Không outline |

⚠️ M_SelectionOutline cần update để check 2 stencil values.

---

## INPUT ACTIONS — Tổng hợp

### Existing
```
IA_FurnitureNudge       (Axis2D)
IA_FurnitureCopy        (Boolean) — Ctrl+C
IA_FurniturePaste       (Boolean) — Ctrl+V
IA_FurnitureDuplicate   (Boolean) — Ctrl+D
IA_Ctrl                 (Boolean) — Modifier chord
```

### Mới — Sprint 1
```
IA_SelectAll            (Boolean) — Ctrl+A
```

### Mới — Sprint 2
```
IA_FurnitureCut         (Boolean) — Ctrl+X
IA_InvertSelection      (Boolean) — Ctrl+I
IA_RightClick           (Boolean) — Right Mouse Button
```

### Mới — Sprint 3
```
IA_GroupCreate          (Boolean) — Ctrl+G
IA_GroupUngroup         (Boolean) — Ctrl+Shift+G
```

### Mới — Sprint 6
```
IA_ToggleLock           (Boolean) — Ctrl+L
IA_ToggleOutliner       (Boolean) — O
IA_FocusSelected        (Boolean) — F
```

---

## DATATABLES

### DT_FurnitureCatalog (existing)
- Row struct: S_FurnitureData
- ~200k rows tiềm năng
- Path: /Game/cuong/UI/Data/DT_FurnitureCatalog

### DT_MaterialInstancesCatalog (existing v1.1)
- Row struct: S_MaterialInstancesData
- ~2738 rows
- Path: /Game/cuong/UI/Data/DT_MaterialInstancesCatalog

### DT_ComboMeshCatalog (mới — Sprint 5)
- Row struct: S_ComboMeshData
- Path: /Game/cuong/UI/Data/DT_ComboMeshCatalog

---

## SAVE GAMES

### BP_UserPreferencesSave (existing C0)
```
RecentMeshes      : Array of Name
RecentMaterials   : Array of Name
FavoriteMeshes    : Array of Name
FavoriteMaterials : Array of Name
FavoriteCombos    : Array of Name   ← Sprint 5 thêm
```

### EMS SaveGame Slot (existing)
- Save tất cả actors có tag "FurnitureSpawned"
- Save thêm actor có tag "FurnitureGroupsContainer" (Sprint 3+)

---

## WIDGET REFERENCES — Hard Refs Cần Clear ở Event Destruct

Tuân thủ R4:

| Widget | Cần clear refs |
|---|---|
| WBP_FurnitureInventory | TargetFurnitureActor, AllFurnitureItems, FilteredItems |
| WBP_FurnitureCard | DA reference, InventoryRef |
| WBP_MaterialCard | MaterialItem, InventoryRef |
| WBP_SlotSwatch | (existing) |
| WBP_DetailPopup | TargetActor, DA |
| WBP_MeshControls | ActiveModeButton (UI ref, không actor) |
| WBP_BoxSelectOverlay | (no actor refs) |
| WBP_ContextMenu | Callback delegates |
| WBP_GroupNameDialog | (no actor refs) |
| WBP_SaveComboDialog | TargetGroupID (string, safe) |
| WBP_ComboCard | ComboRowName (Name, safe) |
| WBP_SceneOutliner | OutlinerRows hard refs to actors → clear |
| WBP_OutlinerRow | TargetActor, GroupRef |
| WBP_MaterialEditPanel | TargetActors array (multi) |
| WBP_EditModeOverlay | (no refs) |

---

## FUNCTION SIGNATURES — Tổng hợp

### BP_FurnitureInputManager Functions (FINAL)

```
// Selection (Sprint 1)
SelectSingleActor(Actor : BP_FurnitureActor)
SelectActors(Actors : Array of BP_FurnitureActor)
ToggleActor(Actor : BP_FurnitureActor)
ToggleActors(Actors : Array of BP_FurnitureActor)
DeselectAll()
SelectAllActors()
SelectSimilar(Criteria : E_SelectSimilarCriteria, Reference : BP_FurnitureActor)
InvertSelection()

// Outline + Gizmo (Sprint 1)
UpdateOutlineState()
UpdateGizmo()
SpawnOrUpdatePivot()
DestroyPivot()
CalculateCenter(Actors) → Vector
CalculateCombinedBounds(Actors) → Vector (BoxExtent)

// Movement (Sprint 1)
NudgeMesh(Direction : Vector2D)
CalculateNudgeOffset(Direction, Reference) → Vector

// Clipboard (Sprint 1)
CopyMesh()
PasteMesh()
DuplicateMesh()
CutMesh()
SpawnFurnitureCopy(..., bAutoSelect : Boolean = True) → BP_FurnitureActor

// Group (Sprint 3)
CreateGroup(GroupName : String) → String (GroupID)
UngroupActors(GroupID, bRecursiveAll : Boolean)
GetGroupChildren(GroupID) → Array of BP_FurnitureActor
SyncGroupsToContainer()
FindGroupData(GroupID) → S_GroupData (or default if not found)

// Edit Mode (Sprint 4)
EnterEditMode(GroupID)
ExitEditMode()

// Lock (Sprint 6)
ToggleLock()
LockActors(Actors)
UnlockAll()

// Align (Sprint 6)
AlignActors(Direction : E_AlignDirection, Reference : E_AlignReference)
DistributeActors(Direction : E_DistributeDirection)

// Outliner (Sprint 6)
GetSceneOutlinerData() → ...
RenameActor(Actor, NewName : String)
SetActorVisibility(Actor, bVisible : Boolean)

// Combo (Sprint 5)
SaveCurrentGroupAsCombo(GroupID, ComboName, Category, Style, Tags)
SpawnCombo(RowName : Name, WorldLocation : Vector)
GenerateComboThumbnail(Actors) → Texture2D

// Material Edit (Sprint 7)
SetMaterialColor(Color : LinearColor)
SetMaterialRoughness(Value : Float)
SetMaterialMetallic(Value : Float)
SetMaterialUVScale(Value : Float)
SetMaterialUVRotation(Value : Float)
ResetMaterialParams()
SerializeMaterialParams(Actor, SlotIndex) → String (JSON)
ApplySerializedMaterialParams(Actor, SlotIndex, JSON)
```

### BP_UndoManager Functions (updated)

```
CaptureSnapshot(ActionName : String)
RestoreSnapshot(IndexHistory : Integer)
UndoLastAction()
RedoLastAction()
```

### BP_PivotActor Functions

```
RefreshOffsets()
ApplyTransformToChildren()
```

### BP_GroupsContainer Functions

```
// (Implements EMSActorSaveInterface — auto save/load)
SyncFromInputManager()
SyncToInputManager()
```
