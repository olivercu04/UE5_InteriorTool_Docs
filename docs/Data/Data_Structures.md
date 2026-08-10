# 05 — Data Structures
**Mục đích:** Tham chiếu đầy đủ struct, enum, variables.
**Cập nhật:** 14/07/2026 — đối chiếu C++ thật (`ComboTypes.h`/`ComboSerializer.h`), sửa mảng Combo lỗi thời (3+ tuần chưa cập nhật): `S_FolderTargetEntry`→`S_FolderTreeNode`, +`S_GroupData.SourceComboID`, `S_ComboMeshData`/`DT_ComboMeshCatalog`/`S_ComboJSONEntry` (planned, chưa từng xây) → `FComboData`/`FComboGroupData`/`FComboItemData` thật + JSON ví dụ, sửa vị trí function Combo (BP_ComboManager, không phải InputManager)

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
| SourceComboID | String | "" | MỚI — Sprint 5 (C1). Group cha của 1 cụm combo = ComboID gốc (root group khi spawn combo). Group user tự tạo tay = "". Xem `BP_ComboManager.md` §F_RegisterComboGroups (Case A/B). |

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

### S_FolderTreeNode — RENAME 08/07/2026 (C5.8 Task Card #1, trước là S_FolderTargetEntry)
Dùng cho `WBP_FolderTreePicker`/`WBP_FolderPickerRow` (Move + Save dialog) — thay list phẳng `S_FolderTargetEntry` cũ (C5.4). Sinh bởi `WBP_FurnitureInventory.BuildFolderTreeRecursive` → `BuildComboFolderTreeNodes`.
| Field | Kiểu | Ghi chú |
|---|---|---|
| Path | String | Path đầy đủ. "" = "(Gốc)" |
| DisplayLabel | String | Tên hiển thị (segment cuối hoặc "(Gốc)") |
| Depth | Integer | Cấp thụt lề — RENAME từ `IndentLevel` (C5.4) |
| HasChildren | Boolean | MỚI — có con hay không, quyết định hiện arrow/badge |
| ChildCount | Integer | MỚI — số con trực tiếp, hiện trong badge `(N)` khi collapsed |
| ContinuesAncestors | Array\<Boolean\> [?] | MỚI — cờ theo từng tổ tiên, dùng dựng guide line (│├└). Type suy luận từ cách gọi trong Blueprint (`WBP_FolderPickerRow.SetNode` ⚠️ SUY LUẬN — export K2Node đầy đủ chưa xác nhận riêng phần này) |
| bIsLast | Boolean | MỚI — node có phải con cuối cùng của cha không (quyết định └ vs ├ ở guide line) |

> ⚠️ `S_FolderTargetEntry` cũ (Path/DisplayLabel/IndentLevel — 3 field) KHÔNG còn tồn tại trong Blueprint, chỉ còn nhắc tới trong lịch sử/`WBP_MoveFolderRow.md` (nay `[SUPERSEDED]`, không xoá file).

### FComboData / FComboGroupData / FComboItemData — C++ USTRUCT thật (Sprint 5, `ComboTypes.h`, plugin FurnitureToolkit)

⚠️ **[CORRECTION 14/07/2026]** Struct/DataTable dưới đây (`S_ComboMeshData`, `DT_ComboMeshCatalog`, `S_ComboJSONEntry`) mô tả Ở BẢN NÀY TRƯỚC ĐÂY là kiến trúc **PLANNED, CHƯA BAO GIỜ ĐƯỢC XÂY**. Hệ thật KHÔNG dùng DataTable — mỗi combo lưu thành **1 file `.json` riêng** trong thư mục Combos (xem `GetCombosDir()`, `Data/ComboSerializer_Reference.md`). 3 struct thật (`FComboData`/`FComboGroupData`/`FComboItemData`) đối chiếu trực tiếp từ `ComboTypes.h` (cuhoang paste 14/07/2026):

#### FComboData
| Field | Kiểu C++ | Default | Ghi chú |
|---|---|---|---|
| Version | int32 | 1 | |
| ComboID | FString | — | "combo_"+GUID, xem `BP_ComboManager.SaveComboFromSelection` Bước 5a |
| Name | FString | — | Tên combo user nhập |
| Description | FString | — | |
| Tags | TArray\<FString\> | [] | |
| Category | FString | "" | Rỗng (fix 08/08/2026, `Bug-ComboCategoryHardcode`). Category thật nhập ở flow Publish — Phase B, chưa xây |
| CreatedAt | FString | — | UTC Now → string, set ở Blueprint |
| AppVersion | FString | — | "1.0.0" hardcode |
| FolderPath | FString | — | Sprint 5 C3a/C5 — path folder chứa combo |
| Items | TArray\<FComboItemData\> | [] | |
| Groups | TArray\<FComboGroupData\> | [] | |
| AuthorID | FString | "" | Chừa sẵn cho Phase B (chưa dùng) |
| Visibility | FString | "Private" | Chừa sẵn cho Phase B (Private/Public/Shared) |
| BoundingBoxExtent | FVector | (0,0,0) | C4 — `CalculateComboBoundingExtent`, dùng cho ghost/anchor lúc drag-drop combo |

#### FComboGroupData
| Field | Kiểu C++ | Ghi chú |
|---|---|---|
| Token | FString | Token tạm ("g0", "g1"...) — resolve thành GUID thật lúc spawn (`F_BuildTokenGUIDMap`) |
| Name | FString | GroupName hiển thị (Blueprint gọi local var là `CurGroupName` nhưng field JSON/C++ tên là `Name`) |
| ParentToken | FString | "" = root group (nhận `SourceComboID` khi spawn — xem `S_GroupData.SourceComboID` ở trên) |

#### FComboItemData
| Field | Kiểu C++ | Default | Ghi chú |
|---|---|---|---|
| RowName | FString | — | Khớp `DT_FurnitureCatalog` RowName |
| SourceType | FString | "catalog" | Chưa thấy nhánh khác "catalog" được dùng trong Blueprint hiện tại — chừa sẵn |
| RelLocation | FVector | (0,0,0) | Vị trí tương đối so với anchor combo |
| RelRotation | FRotator | (0,0,0) | |
| Scale | FVector | (1,1,1) | |
| SurfaceType | FString | "Floor" | |
| MaterialOverrides | TArray\<FString\> | [] | RowName vật liệu (KHÔNG phải path — resolve qua `FindMaterialRowNameByPath` lúc save, `Get Data Table Row(DT_Materials)` lúc spawn) |
| GroupToken | FString | — | "" = không thuộc group nào (Case B ungrouped) hoặc thuộc wrapper (Case A) — xem `BP_ComboManager.F_RegisterComboGroups` |

⚠️ **Dependency Sprint 5 ↔ Sprint 7 (vẫn treo, chưa làm):** `FComboItemData` **CHƯA có field `MaterialParams`** (Color/Roughness JSON cho Sprint 7 v1.2) — chỉ có `MaterialOverrides` (RowName). Nếu Sprint 7 cần persist material params qua combo save/load → phải thêm field mới vào `ComboTypes.h` (đụng schema, cần bump `Version`), KHÔNG tự có sẵn như plan gốc (23/06) từng giả định.

⚠️ **[PHÁT HIỆN 14/07/2026 — cần cuhoang xác nhận]** `GetCombosDir()` thật trong `ComboSerializer.cpp` trả về `FPaths::ProjectSavedDir() / "Combos"` (= `<ProjectRoot>/Saved/Combos/`) — **KHÁC** quyết định P4 đã ghi trong `DEVIATIONS.md` 23/06/2026 ("đổi sang `FPlatformProcess::UserSettingsDir()/InteriorFOFFTool/Combos`, tức `%LOCALAPPDATA%`"). Khớp với đường dẫn thật quan sát được (`Saved/Combos/Folders.json`). Không rõ P4 bị revert hay chưa từng merge — DEVIATIONS.md giữ nguyên bản ghi lịch sử (không sửa), chỉ note ở đây là hiện trạng code THẬT khác quyết định đã chốt.

### Combo JSON — ví dụ thật (đối chiếu 1 file `.json` thật cuhoang paste 14/07/2026, `Saved/Combos/combo_....json`)

⚠️ **[CONFIRMED 14/07/2026]** Key JSON thật là **camelCase** (KHÔNG phải PascalCase giữ nguyên tên C++ như suy đoán trước) — `FJsonObjectConverter::UStructToJsonObjectString` mặc định tự chuyển case. `FVector`/`FRotator` serialize thành object `{x,y,z}` / `{pitch,yaw,roll}` (chữ thường).

```json
{
  "version": 1,
  "comboId": "combo_F8F7513C46921F3E383484A4E7BA489E",
  "name": "Bàn học cho bé gái",
  "description": "",
  "tags": ["bàn học", "bé gái", "trẻ em"],
  "category": "",
  "createdAt": "Year=2026 Month=7 Day=13 Hour=7 Minute=41 Second=46 Millisecond=816",
  "appVersion": "1.0.0",
  "folderPath": "Phòng làm việc/bàn học",
  "items": [
    {
      "rowName": "StudyDesk_Adjustable_900",
      "sourceType": "catalog",
      "relLocation": {"x": -1.36, "y": -1.11, "z": 0},
      "relRotation": {"pitch": 0, "yaw": -90.0, "roll": 0},
      "scale": {"x": 1, "y": 1, "z": 1},
      "surfaceType": "Floor",
      "materialOverrides": [],
      "groupToken": ""
    }
  ],
  "groups": [],
  "authorId": "",
  "visibility": "Private",
  "boundingBoxExtent": {"x": 34, "y": 45.0, "z": 47.79}
}
```
> **`createdAt`** — KHÔNG phải ISO8601 như đoán trước. Format thật là `FDateTime::ToString()` mặc định của UE (`Year=... Month=... Day=... Hour=... Minute=... Second=... Millisecond=...`) — literal string, không parse lại thành `FDateTime` ở đâu trong code hiện tại (chỉ hiển thị/lưu trữ).
> `groups: []` + mọi `groupToken: ""` khi combo không có group con (item rời, chưa `Ctrl+G` trước khi save) — khớp Case B (ungrouped) trong `BP_ComboManager.F_RegisterComboGroups`.
> File gốc cuhoang paste bị mojibake (UTF-8 hiển thị nhầm Latin-1) lúc copy — bản thân file trên đĩa đúng UTF-8 không BOM (`SaveStringToFile` dùng `ForceUTF8WithoutBOM`), không phải bug. Đã decode lại tiếng Việt đúng ở ví dụ trên.
> `"category": ""` — cập nhật 08/08/2026 sau fix `Bug-ComboCategoryHardcode` (T5 D2). Combo lưu
> TRƯỚC ngày này trong dữ liệu thật vẫn còn giá trị cũ `"MyCombo"` (không có migration script,
> field chưa ai đọc nên không cần).

### Folders.json — manifest folder (registry, `ComboSerializer.cpp GetAllFolderPaths`/`CreateEmptyFolder`)
```json
["Livingroom", "Livingroom/Sofa", "Bedroom"]
```
Mảng phẳng `TArray<FString>` các path folder đã biết (kể cả cấp cha — `GetAllFolderPaths` tự ghi bổ sung cấp cha khi quét combo). Sống cạnh các file combo `.json` trong cùng `GetCombosDir()`, tên cố định `Folders.json`. Field thật ra là "empty folder registry" (tên hàm `GetEmptyFoldersFilePath`/`LoadEmptyFoldersInternal`) nhưng từ 03/07/2026 đã trở thành **nguồn sự thật DUY NHẤT cho MỌI folder** (kể cả folder có combo) — xem comment `B1, 03/07/2026` trong `ComboSerializer.cpp`.

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

### DT_ComboMeshCatalog — [CORRECTION 14/07/2026] KHÔNG TỒN TẠI
Plan gốc Sprint 5 dự kiến DataTable này. Thực tế combo lưu file-based (`FComboData` → JSON, 1 file/combo trong `GetCombosDir()`), KHÔNG qua DataTable. Xem `FComboData`/`FComboGroupData`/`FComboItemData` ở mục STRUCTS trên + `Data/ComboSerializer_Reference.md`.

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
| WBP_ComboCard | ComboID (String, safe) — [CORRECTION 14/07/2026] tên field cũ ghi "ComboRowName (Name)" SAI kiểu, thật là `ComboID : String` (khớp `BP_ComboItemView.ComboID`). InventoryRef (WBP_FurnitureInventory, lazy-init) cũng cần clear — xem `01_Session_State.md` mục KIẾN TRÚC HIỆN TẠI |
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

### BP_ComboManager Functions — [CORRECTION 14/07/2026] đúng vị trí thật (KHÔNG nằm trên BP_FurnitureInputManager)
Actor riêng, tách khỏi InputManager (R2 — không hard ref). Signature Custom Event thật (xem `Blueprints/BP_ComboManager.md`):
```
SaveComboFromSelection(SelectedActors : Array<BP_FurnitureActor>, Center : Vector,
  ComboName : String, Description : String, FolderPath : String, Tags : Array<String>)
SpawnComboByID(ComboID : String, SpawnLocation : Vector)
```
Thumbnail (P1, C++ `UComboThumbnail` — xem `Data/ComboSerializer_Reference.md`):
```
BeginComboCapture(ComboActors, ExtraHiddenActors, Resolution) → ASceneCapture2D (handle)
FinishComboCapture(CaptureHandle, ComboID) → bool
LoadComboThumbnail(ComboID, MaxSize) → UTexture2D
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
