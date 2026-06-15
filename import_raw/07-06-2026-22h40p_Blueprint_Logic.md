# Blueprint Logic — Node Flow Reference
**Phiên bản:** 1.3 | **Cập nhật:** 07/06/2026 — 22:40 ICT
**Mục đích:** Ghi lại thứ tự node logic để không cần chụp ảnh lại Blueprint

---

## QUY ƯỚC GHI

```
→         : execution flow (dây trắng)
[var]     : GET variable
SET var   : SET variable
Branch X  : Branch node, Condition = X
  T:      : nhánh True
  F:      : nhánh False
ForEach A : For Each Loop với array A
  Body:   : Loop Body
  Done:   : Completed pin
Call F()  : gọi function/event F
```

---

## WBP_FurnitureInventory

### SwitchInventoryMode(NewMode)
```
SET CurrentPage = 0
SET CurrentInventoryMode = NewMode

GetAllActors(BP_FurnitureInputManager)[0]
→ GET SelectedFurnitureActor → SET TargetFurnitureActor
→ GET MeshPath → SET TargetMeshPath

SET Visibility(CTV_FurnitureCard, Collapsed)
SET Visibility(CTV_MaterialCard, Collapsed)  ← reset cả 2 trước

Branch NewMode == Material:
  T:
    SET Visibility(CTV_MaterialCard, Visible)
    Branch IsValid(TargetFurnitureActor):
      T: SET Visibility(HB_SlotSwatches, Visible)
      F: SET Visibility(HB_SlotSwatches, Collapsed)
    Call PopulateMaterialGrid
    Branch IsEmpty(MaterialFolderTree):
      T: Call BuildMaterialFolderTree
    SET FolderTree = MaterialFolderTree
    Call PopulateTreeColumn
    SET CurrentFolderPath = ""
    SET ActiveLevel1Path = ""
    ClearChildren(VB_ChipTagArea)
  F:
    SET Visibility(CTV_FurnitureCard, Visible)
    SET Visibility(HB_SlotSwatches, Collapsed)
    SET FolderTree = FurnitureFolderTree
    Call PopulateTreeColumn
    SET CurrentFolderPath = ""
    SET ActiveLevel1Path = ""
    ClearChildren(VB_ChipTagArea)
    Call FilterBySearch(CurrentSearchText, CurrentCategory)  ← v1.1 Fix#7: populate card ngay khi switch về
```

### BuildFolderTree (Furniture)
```
CLEAR FolderTree
GetAssetsByPath("/Game/cuong/UI/Data/FurnitureAssets") → AssetData
ForEach AssetData:
  Body:
    SET CurrentPath = ""
    GetAsset(ArrayElement) → Cast DA_FurnitureItem
    Replace(MeshFolderPath, "/Game/DatabaseProjectMaster/Model/Object_Model/", "") → RelativePath
    ParseIntoArray(RelativePath, "/") → Parts
    ForEach Parts:
      Body:
        SET ParentPath = CurrentPath
        SET ArrayElementFolderPath = ArrayElement
        Branch ArrayIndex == 0:
          T: SET CurrentPath = ArrayElementFolderPath
          F: SET CurrentPath = Append(CurrentPath, "/", ArrayElementFolderPath)
        MapContains(FolderTree, ParentPath):
          T: MapFind(FolderTree, ParentPath) → ExistingValue
             Contains(ExistingValue, ArrayElementFolderPath):
               T: (skip)
               F: MapAdd(FolderTree, ParentPath, Append(ExistingValue, ",", ArrayElementFolderPath))
          F: MapAdd(FolderTree, ParentPath, ArrayElementFolderPath)
Done: Keys(FolderTree) → Values(FolderTree)
```

### BuildMaterialFolderTree
```
CLEAR MaterialFolderTree
GetDataTableRowNames(DT_MaterialInstancesCatalog) → AllRowNames
ForEach AllRowNames:
  Body:
    GetDataTableRow(DT_MaterialInstancesCatalog, ArrayElement) → OutRow
    Row Found:
      SET CurrentMaterialPath = ""
      Replace(OutRow.MaterialFolderPath,
        "/Game/DatabaseProjectMaster/Material/MaterialInstances/", "") → RelativePath
      ParseIntoArray(RelativePath, "/") → Parts
      ForEach Parts:
        Body:
          SET ParentPath = CurrentMaterialPath
          SET ArrayElementFolderPath = ArrayElement
          Branch ArrayIndex == 0:
            T: SET CurrentMaterialPath = ArrayElementFolderPath
            F: SET CurrentMaterialPath = Append(CurrentMaterialPath, "/", ArrayElementFolderPath)
          MapContains(MaterialFolderTree, ParentPath):
            T: MapFind(MaterialFolderTree, ParentPath) → ExistingValue
               Contains(ExistingValue, ArrayElementFolderPath):
                 T: (skip)
                 F: MapAdd(MaterialFolderTree, ParentPath,
                           Append(ExistingValue, ",", ArrayElementFolderPath))
            F: MapAdd(MaterialFolderTree, ParentPath, ArrayElementFolderPath)
```

### PopulateMaterialGrid
```
[Print: "PopulateMaterialGrid FolderPath: " + CurrentFolderPath]  ← xóa khi done debug
FilterMaterialItems(
  MaterialTable   = DT_MaterialInstancesCatalog,
  SearchText      = CurrentSearchText,
  TypeTags        = MakeArray(rỗng),
  SubFolderPath   = CurrentFolderPath,
  MaxResults      = 20000
) → FilteredRowNames
SET AllFilteredMaterialRows = FilteredRowNames
SET CurrentPage = 0
Call DisplayPage
```

### DisplayPage
```
Branch CurrentInventoryMode == Material:
  T:
    ClearListItems(CTV_MaterialCard)
    ForLoop(First = CurrentPage×PageSize,
            Last  = MIN(CurrentPage×PageSize+PageSize, Len(AllFilteredMaterialRows))-1):
      Body:
        GET AllFilteredMaterialRows[Index] → RowName
        GetDataTableRow(DT_MaterialInstancesCatalog, RowName) → OutRow
        Row Found:
          Call BuildMaterialItem(RowName, OutRow) → OutMaterialItem
          AddItem(CTV_MaterialCard, OutMaterialItem)
    Done:
      SetText(ET_PageDisplay, CurrentPage+1 + "/" + Ceil(Len(AllFilteredMaterialRows)/PageSize))
  F:
    ClearListItems(CTV_FurnitureCard)
    ForLoop(First = CurrentPage×PageSize,
            Last  = MIN(..., Len(FilteredItems))-1):
      Body: GET FilteredItems[Index] → AddItem(CTV_FurnitureCard)
    Done: SetText(ET_PageDisplay, ...)
```

### FilterBySearch(SearchText, CategoryFilter)
```
SET CategoryFilter, SET CurrentSearchText
Branch SearchText != "" AND Len < 3: T → Return
Branch CurrentInventoryMode == Material:
  T: Call PopulateMaterialGrid → Return
  F:
    ClearListItems(CTV_FurnitureCard)
    FilterFurnitureItems(C++, AllFurnitureItems, SearchText, CurrentFolderPath, CategoryFilter)
    ForEach → Cast DA_FurnitureItem → AddItem(CTV_FurnitureCard)
```

### BTN_NextPage OnClicked
```
Branch CurrentInventoryMode == Material:
  T: MaxPage = Ceil(Len(AllFilteredMaterialRows)/PageSize) - 1
  F: MaxPage = Ceil(Len(FilteredItems)/PageSize) - 1
Branch CurrentPage < MaxPage:
  T: SET CurrentPage = CurrentPage+1 → Call DisplayPage
```

### BTN_PrevPage OnClicked
```
Branch CurrentPage > 0:
  T: SET CurrentPage = CurrentPage-1 → Call DisplayPage
```

### BuildMaterialItem(MaterialRowName, MaterialRowData) → OutMaterialItem
```
ConstructObject(BP_MaterialItem) → NewItem
SET NewItem.RowName = MaterialRowName
SET NewItem.DisplayName = MaterialRowData.EngName
SET NewItem.ThumbnailMI = MaterialRowData.ThumbnailMI
SET OutMaterialItem = NewItem
```

### ApplyMaterial(MaterialRowName)
```
Branch IsValid(TargetFurnitureActor):
  F:
    GetAllActorsWithTag("FurnitureSpawned") → ForEach with Break:
      Cast To BP_FurnitureActor
      Branch MeshPath == TargetMeshPath:
        T: SET TargetFurnitureActor = FurnitureRef → Break
Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0:
  T:
    GetDataTableRow(DT_MaterialInstancesCatalog, MaterialRowName) → OutRow
    Row Found:
      SET PendingMaterialPath = OutRow.MaterialPath
      Call LoadAndApplyMaterial (Custom Event)
```

### LoadAndApplyMaterial (Custom Event, Event Graph)
```
MakeSoftObjectPath(PendingMaterialPath)
→ ToSoftObjectReference
→ AsyncLoadAsset
  Completed:
    Cast Object To MaterialInterface → MI_Source
    Branch IsValid(MI_Source) AND IsValid(TargetFurnitureActor):
      T:
        CreateDynamicMaterialInstance(
          Target         = TargetFurnitureActor.FurnitureMesh
          ElementIndex   = SelectedSlotIndex
          SourceMaterial = MI_Source
        ) → MID
        SetMaterial(FurnitureMesh, SelectedSlotIndex, MID)
        SetArrayElem(
          TargetFurnitureActor.MaterialOverrides,
          SelectedSlotIndex,
          PendingMaterialPath,
          SizeToFit = True
        )
        ClearTimer(ApplyMaterialTimerHandle)
        SetTimerByFunctionName("CaptureMaterialSnapshot", 0.5s)
        → SET ApplyMaterialTimerHandle
```

### CaptureMaterialSnapshot (Custom Event)
```
GET UndoManagerRef → CaptureSnapshot("ChangeMaterial")
```

### OnSceneRestored(RestoredSelectedActor) (Custom Event)
```
← Bound từ UndoManagerRef.OnRestoreCompleted trong Event Construct
Branch CurrentInventoryMode == Material:
  T:
    SET TargetFurnitureActor = RestoredSelectedActor
    Branch IsValid(RestoredSelectedActor):
      T: SET Visibility(HB_SlotSwatches, Visible)
      F: SET Visibility(HB_SlotSwatches, Collapsed)
```

### BTN_ResetSlot OnClicked
```
Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0:
  T:
    TargetFurnitureActor.FurnitureMesh
    → GET StaticMesh
    → GET Material(SelectedSlotIndex) → OriginalMat
    SetMaterial(FurnitureMesh, SelectedSlotIndex, OriginalMat)
    SetArrayElem(MaterialOverrides, SelectedSlotIndex, "", SizeToFit)
    GET UndoManagerRef → CaptureSnapshot("ResetSlot")
```

### BTN_ResetAll OnClicked
```
Branch IsValid(TargetFurnitureActor):
  T:
    FurnitureMesh → GetNumMaterials → NumSlots
    ForLoop(0 → NumSlots-1):
      Body:
        StaticMesh → GET Material(Index) → OriginalMat
        SetMaterial(FurnitureMesh, Index, OriginalMat)
    Done:
      CLEAR TargetFurnitureActor.MaterialOverrides
      GET UndoManagerRef → CaptureSnapshot("ResetAll")
```

### Event Construct (Sequence)
```
Then 0: SetTimer(0.1s) → InitMinimizedHeight → SET CurrentCategory
Then 1: CLEAR AllFurnitureItems
        GetAllAssetsByPath → ForEach → Cast DA_FurnitureItem → ADD AllFurnitureItems
        → BindCategoryEvents → FilterBySearch
Then 2: BuildFolderTree
        SET FurnitureFolderTree = FolderTree  ← cache Furniture tree
        PopulateTreeColumn → FilterByFolderPath → UpdateTabHighlight
Then 3: GetAllActors(BP_UndoManager)[0] → SET UndoManagerRef
        Bind UndoManagerRef.OnRestoreCompleted → OnSceneRestored
```

---

## WBP_MaterialCard

### OnListItemObjectSet
```
Cast Object To BP_MaterialItem → SET MaterialItem
Branch IsValid(InventoryRef):
  F: GetGameInstance → Cast Foff_GameInstance → GET FurnitureInventoryRef → SET InventoryRef
SetBrushFromLazyTexture(LazyImage_ThumbMI, MaterialItem.ThumbnailMI)
```

### Button_ChangeMaterial OnClicked
```
Branch IsValid(InventoryRef) AND IsValid(MaterialItem):
  T: Call InventoryRef.ApplyMaterial(MaterialItem.RowName)
```

### Event Destruct
```
SET MaterialItem = None
SET InventoryRef = None
```

---

## BP_FurnitureInputManager — Box Select (v1.5, Sprint 2)

> Flow đầy đủ + lý do từng quyết định: **BP_FurnitureInputManager.md v1.5**. Đây là tóm tắt node-flow.

### Mouse Left Pressed (defer)
```
SET bLMBHeld = True
Set Input Mode Game And UI
SET LocalWasGizmoActive = GizmoControllerRef.bGizmoActive
GizmoController → OnMousePressed
Branch bIsDraggingGizmo → T: STOP
GetHitResultUnderCursorByChannel(CAMERA) → HitActor, ReturnValue
Branch ReturnValue:
  F → GetMousePosOnViewport → SET BoxStartPos → SET bIsPendingBoxSelect=True → STOP
Branch HasTag(HitActor,"FurnitureSpawned"):
  F → GetMousePosOnViewport → SET BoxStartPos → SET bIsPendingBoxSelect=True → STOP
Branch IsInputKeyDown(LeftCtrl):
  T → ToggleActor(HitActor) → CaptureSnapshot("Select") → STOP
  F → SET PendingClickActor=HitActor → SET BoxStartPos → SET bIsPendingBoxSelect=True → STOP
```

### Event Tick — box branch (sau nudge, trong Sequence)
```
[Guard inventory]: GetGameInstance→Cast→GET FurnitureInventoryRef→nested Branch IsValid + IsInViewport→SET bInventoryOpen
Branch bInventoryOpen:
  F → HideBox + reset cờ → STOP
  T:
   Branch bIsPendingBoxSelect:
     Branch bLMBHeld:
       T → dist=Length(MousePos-BoxStartPos) → Branch dist>5:
             T → SET bIsBoxSelecting=True, bIsPendingBoxSelect=False, ShowBox, UpdateBox
       F → SET bIsPendingBoxSelect=False → Branch IsValid(PendingClickActor):
             T → SelectSingleActor + CaptureSnapshot("Select") + SET None
             F → Branch Ctrl: F → DeselectAll + CaptureSnapshot("Deselect")
   Branch bIsBoxSelecting:
     Branch bLMBHeld:
       T → UpdateBox(BoxStartPos, MousePos)
       F → FinishBoxSelect(MousePos) → HideBox → SET bIsBoxSelecting=False → SET PendingClickActor=None
```

### OnLMBReleased (đường chính chốt selection)
```
SET bLMBHeld=False
Sequence:
  Then0: đóng context menu (IsValid ContextMenuRef → Remove → SET None)
  Then1: Branch bIsBoxSelecting:
           T → GetMousePos → FinishBoxSelect → IsValid(OverlayRef)→HideBox → SET bIsBoxSelecting=False → SET PendingClickActor=None
  Then2: Branch bIsPendingBoxSelect:
           T → SET bIsPendingBoxSelect=False → Branch IsValid(PendingClickActor):
                 T → SelectSingleActor + CaptureSnapshot("Select") + SET None
                 F → Branch Ctrl: F → DeselectAll + CaptureSnapshot("Deselect") → Branch bIsReplaceMode → exit replace
```

### FinishBoxSelect(EndPos) — Function
```
TopLeft/BottomRight = Min/Max(BoxStartPos, EndPos)
CLEAR LocalSelected
GetAllActorsWithTag("FurnitureSpawned") → ForEach (Actor):
  Branch (Actor != PendingClickActor):           ← loại mesh kéo-từ-đó
    Cast→IsValid→GetActorLocation→ProjectWorldToScreen→ScreenPos
    ScreenPosFixed = ScreenPos / GetViewportScale  ← ⚠️ DPI fix
    nested Branch (Fixed.X trong [TL.X,BR.X] AND Fixed.Y trong [TL.Y,BR.Y]):
      T → ADD Actor → LocalSelected
Completed → Branch Len(LocalSelected)>0:
  Branch IsInputKeyDown(Ctrl):
    T → ForEach LocalSelected → ToggleActor   ← cộng dồn
    F → DeselectAll → SelectActors(LocalSelected)
  → CaptureSnapshot("BoxSelect")
```

---

## BP_UndoManager

> ⚠️ **Flow dưới đây là bản v1.1 SINGLE-select (cũ).** Bản MULTI-select hiện hành (v1.5) — bao gồm TempSelectedIndices, Version field, và fix CLEAR đầu hàm — xem **BP_UndoManager.md** (authoritative). Tóm tắt fix mới nhất ngay dưới.

### ⭐ FIX v1.5 (07/06) — CLEAR TempSelectedIndices đầu hàm CaptureSnapshot
```
Function Entry → CLEAR TempSelectedIndices → [Step 1 cũ...]
```
Lý do: TempSelectedIndices là class var (giữ giá trị giữa các lần gọi). Thao tác Deselect đi nhánh bypass đoạn build → giá trị stale từ lần Select trước lọt vào snapshot → Undo nhảy cóc. CLEAR đầu hàm = phòng thủ chắc chắn. (Print debug từng đặt trong ForEach Step 3 → in 1 lần/mesh → ngỡ "double capture" — sai hướng. Print debug đặt main line, không trong loop.)

### CaptureSnapshot(ActionName) — v1.1 SINGLE (cũ, tham khảo)
```
Branch CurrentIndex < Len(History)-1:
  T: ArrayResize(SnapshotHistory, CurrentIndex+1)  ← xóa redo stack
CLEAR TempMeshes
GetAllActorsWithTag("FurnitureSpawned") → ForEach:
  Cast To BP_FurnitureActor → Build S_FurniturePlacement:
    UniqueID    = GetDisplayName(Actor)
    MeshPath, DAPath ← từ Cast BP_FurnitureActor
    Location, Rotation, Scale, ActorTag
    MaterialPaths = GET BP_FurnitureActor.MaterialOverrides  ← v1.1
  ADD to TempMeshes
SET SelectedMeshIndex = -1
GetAllActors(BP_FurnitureInputManager)[0] → Cast:
  Success → IsValid(SelectedFurnitureActor):
    T → HasTag("FurnitureSpawned"):
      T → ForEach TempMeshes: UniqueID == GetDisplayName(SelectedFurnitureActor)
            → SET SelectedMeshIndex = ArrayIndex
          → Branch Len >= MaxSteps
    F → Branch Len >= MaxSteps
  F → Branch Len >= MaxSteps
Branch Len >= MaxSteps → RemoveIndex(0) → CurrentIndex-1
Make S_SceneSnapshot(ActionName, TempMeshes, SelectedMeshIndex, ActiveMode)
→ ADD to SnapshotHistory → SET CurrentIndex = CurrentIndex+1
```

### RestoreSnapshot(IndexHistory)
```
GetAllActors(BP_FurnitureInputManager)[0] → Cast → DeselectMesh
DestroyAllActors(tag "FurnitureSpawned")
CLEAR SpawnedActors
ForEach Snapshot[IndexHistory].Meshes:
  Spawn BP_FurnitureActor → LoadAssetBlocking → SetStaticMesh
  SET MeshPath, SET DAPath
  GET Tags → ADD "FurnitureSpawned"
  ← Restore MaterialPaths (v1.1):
  ForEach Placement.MaterialPaths (Index, Path):
    Branch Path != "":
      LoadAssetBlocking(Path) → Cast MaterialInterface → MI_Source
      CreateDMI(FurnitureMesh, MI_Source, Index) → MID
      SetMaterial(FurnitureMesh, Index, MID)
  SET BP_FurnitureActor.MaterialOverrides = Placement.MaterialPaths
  ADD to SpawnedActors
Branch SelectedMeshIndex >= 0:
  T: FoundActor = SpawnedActors[SelectedMeshIndex]
     Cast To BP_FurnitureActor:
       Success → SET RestoredBPActor = As BP_FurnitureActor  ← v1.3
                 SET SelectedFurnitureActor, ActivateGizmo, SetCustomDepth(255)
       Failed  → SET RestoredBPActor = None                  ← v1.3
  F: SetCustomDepth(False), SET SelectedFurnitureActor = None, DeactivateGizmo
     SET RestoredBPActor = None                              ← v1.3
RefreshButtonState(Snapshot.ActiveMode)
← v1.3: Single broadcast point — không dùng Branch + SpawnedActors[SelectedMeshIndex] nữa
Broadcast OnRestoreCompleted(GET RestoredBPActor)
```

---

## C++ — FurnitureFilterLibrary

### FilterMaterialItems signature
```cpp
TArray<FName> FilterMaterialItems(
    UDataTable* MaterialTable,
    const FString& SearchText,
    const TArray<FString>& TypeTags,
    const FString& SubFolderPath,
    int32 MaxResults
)
```

### Key fix — Blueprint struct property lookup
```cpp
// KHÔNG dùng FindFProperty trực tiếp (Blueprint struct có GUID trong property name)
// DÙNG PropertyLink loop + Contains:
FStrProperty* FolderProp = nullptr;
FTextProperty* VieNameProp = nullptr;
FTextProperty* EngNameProp = nullptr;
for (FProperty* Prop = RowStruct->PropertyLink; Prop; Prop = Prop->PropertyLinkNext)
{
    FString PropName = Prop->GetName();
    if (!FolderProp && PropName.Contains(TEXT("MaterialFolderPath")))
        FolderProp = CastField<FStrProperty>(Prop);
    else if (!VieNameProp && PropName.Contains(TEXT("VieName")))
        VieNameProp = CastField<FTextProperty>(Prop);
    else if (!EngNameProp && PropName.Contains(TEXT("EngName")))
        EngNameProp = CastField<FTextProperty>(Prop);
}
```

### Filter logic
```
bFilterBySubFolder = !SubFolderPath.IsEmpty()
bFilterByType = TypeTags.Num() > 0
bFilterBySearch = !SearchText.IsEmpty()

For each row:
  if bFilterByType → FolderValue.Contains(any Tag) → skip nếu không match
  if bFilterBySubFolder → FolderValue.Contains(SubFolderPath) → skip nếu không match
  if bFilterBySearch → VieName/EngName.Contains(SearchText) → skip nếu không match
  → Add RowName to Results
```

---

## UX Issues còn lại (20/05/2026)

| # | Vấn đề | Status |
|---|---|---|
| 1 | Search text reset khi switch mode | ✅ (partial — visual SearchBar chưa clear) |
| 2 | Tên slot trong swatch | ⏭️ (chuyển sang Detail popup) |
| 3 | Highlight slot đang chọn | ✅ |
| 4 | Thumbnail swatch update sau apply/reset/undo | ✅ |
| 5 | Deselect/Select mesh + Undo/Redo → SlotSwatches | ✅ |
| 6 | Loading feedback khi apply | ⏭️ (skip — async load <100ms, revisit khi packaged build) |
| 7 | FilterByCategory branch theo mode | ✅ |

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 18/05/2026 — 08:55 ICT | Tạo mới — full node flow WBP_FurnitureInventory, BP_UndoManager, C++ |
| 1.1 | 20/05/2026 — 15:30 ICT | Fix RestoreSnapshot broadcast: RestoredBPActor single point |
| 1.2 | 20/05/2026 — 16:00 ICT | Fix #7: SwitchInventoryMode False branch thêm FilterBySearch; tất cả UX fixes hoàn thành |
| 1.3 | 07/06/2026 — 22:40 ICT | **Sprint 2:** thêm section Box Select (Mouse Left Pressed defer / Event Tick / OnLMBReleased / FinishBoxSelect); ghi fix CLEAR TempSelectedIndices đầu CaptureSnapshot; đánh dấu flow CaptureSnapshot cũ là v1.1 single (authoritative ở BP_UndoManager.md v1.5) |
