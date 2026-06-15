# Blueprint Logic — Node Flow Reference
**Phiên bản:** 1.1 | **Cập nhật:** 19/05/2026 — 17:50 ICT
**Mục đích:** Ghi lại thứ tự node logic để không cần chụp ảnh Blueprint

---

## QUY ƯỚC GHI

```
→         : execution flow
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

## BP_FurnitureInputManager

### Event Dispatchers
```
OnMeshDeselected()                               ← v1.1 UX
OnMeshSelected(SelectedActor : BP_FurnitureActor) ← v1.1 UX
```

### DeselectMesh
```
Branch IsValid(SelectedFurnitureActor):
  T:
    Set Render Custom Depth(FurnitureMesh, False)
    SET SelectedFurnitureActor = None
Branch IsValid(CurrentMeshControls):
  T: DeactivateGizmo(GizmoControllerRef)
Broadcast OnMeshDeselected  ← v1.1 UX, cuối function
```

### LeftMouseButton — Step 7-8 (Select Mesh)
```
Step 7: Branch IsValid(SelectedFurnitureActor)?
  T: DeactivateGizmo, Set Custom Depth False
  F: (thẳng xuống)
Step 8: Cast HitActor → BP_FurnitureActor
  → SET SelectedFurnitureActor
  → Broadcast OnMeshSelected(SelectedFurnitureActor)  ← v1.1 UX
```

---

## WBP_FurnitureInventory

### Event Construct (Sequence)
```
Then 0: Bind Event to OnCategorySelected(BTN_AllCategory)
        → OnCategorySelected_Event → FilterByCategory(CategoryFilter=All)

Then 1: BuildFolderTree
        → SET FurnitureFolderTree = FolderTree
        → PopulateTreeColumn → FilterByFolderPath → UpdateTabHighlight

Then 2: GetAllActors(BP_UndoManager)[0] → SET UndoManagerRef
        → Bind OnRestoreCompleted → OnSceneRestored

Then 3: GetAllActors(BP_FurnitureInputManager)[0]
        → Bind OnMeshDeselected → OnMeshDeselected
        → Bind OnMeshSelected → OnMeshSelected
```

### SwitchInventoryMode(NewMode)
```
SET CurrentSearchText = ""  ← v1.1 UX clear search
SET CurrentPage = 0
SET CurrentInventoryMode = NewMode
Call UpdateTabHighlight  ← v1.1 UX

GetAllActors(BP_FurnitureInputManager)[0]
→ GET SelectedFurnitureActor → SET TargetFurnitureActor

Branch NewMode == Material:
  T:
    SET Visibility(CTV_FurnitureCard, Collapsed)
    SET Visibility(CTV_MaterialCard, Visible)
    Branch IsValid(TargetFurnitureActor):
      T: SET Visibility(HB_SlotSwatches, Visible)
      F: SET Visibility(HB_SlotSwatches, Collapsed)
    Branch IsEmpty(MaterialFolderTree):
      T: Call BuildMaterialFolderTree
      F: (merge ↓)
    SET FolderTree = MaterialFolderTree  ← cả True+False nối vào đây
    Call PopulateTreeColumn
    SET CurrentFolderPath = ""
    SET ActiveLevel1Path = ""
    ClearChildren(VB_ChipTagArea)
    Call PopulateMaterialGrid
  F:
    SET Visibility(CTV_FurnitureCard, Visible)
    SET Visibility(CTV_MaterialCard, Collapsed)
    SET Visibility(HB_SlotSwatches, Collapsed)
    SET FolderTree = FurnitureFolderTree
    Call PopulateTreeColumn
    SET CurrentFolderPath = ""
    SET ActiveLevel1Path = ""
    ClearChildren(VB_ChipTagArea)
    Call FilterBySearch("", CurrentCategory)
```

### BuildMaterialFolderTree
```
CLEAR MaterialFolderTree
GetDataTableRowNames(DT_MaterialInstancesCatalog) → AllRowNames
ForEach AllRowNames:
  Body:
    GetDataTableRow(DT, ArrayElement) → OutRow
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
            T: MapFind → ExistingValue
               Contains(ExistingValue, ArrayElementFolderPath):
                 T: (skip)
                 F: MapAdd(ParentPath, Append(ExistingValue, ",", ArrayElementFolderPath))
            F: MapAdd(ParentPath, ArrayElementFolderPath)
```

### FilterBySearch(SearchText, CategoryFilter)
```
SET CategoryFilter, SET CurrentSearchText
Branch SearchText != "" AND Len < 3: T → Return
Branch CurrentInventoryMode == Material:
  T: Call PopulateMaterialGrid → Return
  F:
    ClearListItems(CTV_FurnitureCard)
    FilterFurnitureItems(C++) → ForEach → AddItem(CTV_FurnitureCard)
```

### PopulateMaterialGrid
```
FilterMaterialItems(
  DT_MaterialInstancesCatalog, CurrentSearchText,
  MakeArray(rỗng), CurrentFolderPath, 20000
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
    ForLoop(CurrentPage×PageSize → MIN(..., Len(AllFilteredMaterialRows))-1):
      Body: GET RowName → GetDataTableRow → BuildMaterialItem → AddItem(CTV_MaterialCard)
    Done: SetText(ET_PageDisplay, page info)
  F:
    ClearListItems(CTV_FurnitureCard)
    ForLoop → AddItem(CTV_FurnitureCard)
    Done: SetText
```

### ApplyMaterial(MaterialRowName)
```
Branch IsValid(TargetFurnitureActor): F → (fallback search by tag, skip)
Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0:
  T:
    GetDataTableRow(DT, MaterialRowName) → Row Found:
      SET PendingRowName = MaterialRowName  ← v1.1 UX
      SET PendingMaterialPath = OutRow.MaterialPath
      Call LoadAndApplyMaterial
```

### LoadAndApplyMaterial (Custom Event)
```
MakeSoftObjectPath(PendingMaterialPath) → ToSoftObjectRef → AsyncLoadAsset
  Completed:
    Cast MaterialInterface → MI_Source
    Branch IsValid(MI_Source) AND IsValid(TargetFurnitureActor):
      T:
        CreateDMI(FurnitureMesh, MI_Source, SelectedSlotIndex) → MID
        SetMaterial(FurnitureMesh, SelectedSlotIndex, MID)
        SetArrayElem(MaterialOverrides, SelectedSlotIndex, PendingMaterialPath, SizeToFit)
        ClearTimer(ApplyMaterialTimerHandle)
        SetTimerByFunctionName("CaptureMaterialSnapshot", 0.5s) → SET Handle

        ← v1.1 UX: Update swatch thumbnail
        GetDataTableRow(DT, PendingRowName) → Row Found:
          GetAllChildren(HB_SwatchList)[SelectedSlotIndex]
          → Cast WBP_SlotSwatch → UpdateThumbnail(OutRow.ThumbnailMI)
```

### OnSceneRestored(RestoredSelectedActor) — Custom Event
```
← Bound từ UndoManagerRef.OnRestoreCompleted
SET PendingRestoredActor = RestoredSelectedActor
SetTimerByFunctionName("ApplyRestoredActor", 0.1s)  ← delay cho LeftMouseButton xong
```

### ApplyRestoredActor — Custom Event
```
Branch CurrentInventoryMode == Material:
  T:
    SET TargetFurnitureActor = PendingRestoredActor
    Branch IsValid(PendingRestoredActor):
      T:
        SET Visibility(HB_SlotSwatches, Visible)
        SET SelectedSlotIndex = -1
        Call RefreshSlotSwatches
        ← "Update Swatch Thumbnails from Material Overrides":
        Branch IsValid(TargetFurnitureActor):
          T:
            ForEach TargetFurnitureActor.MaterialOverrides (Path, Index):
              Branch NOT IsEmpty(Path):
                T:
                  ParseIntoArray(Path, ".") → Parts
                  GET Parts[LastIndex] → RowName
                  GetDataTableRow(DT, RowName) → Row Found:
                    GetAllChildren(HB_SwatchList)[ArrayIndex]
                    → Cast WBP_SlotSwatch → UpdateThumbnail(ThumbnailMI)
      F: SET Visibility(HB_SlotSwatches, Collapsed)
```

### OnMeshDeselected — Custom Event
```
← Bound từ BP_FurnitureInputManager.OnMeshDeselected
Branch CurrentInventoryMode == Material:
  T:
    SET Visibility(HB_SlotSwatches, Collapsed)
    SET TargetFurnitureActor = None
    SET SelectedSlotIndex = -1
```

### OnMeshSelected(SelectedActor) — Custom Event
```
← Bound từ BP_FurnitureInputManager.OnMeshSelected
Branch CurrentInventoryMode == Material:
  T:
    SET TargetFurnitureActor = SelectedActor
    SET Visibility(HB_SlotSwatches, Visible)
    SET SelectedSlotIndex = -1
    Call RefreshSlotSwatches
    ← "Update Swatch Thumbnails from Material Overrides":
    Branch IsValid(TargetFurnitureActor):
      T:
        ForEach TargetFurnitureActor.MaterialOverrides (Path, Index):
          Branch NOT IsEmpty(Path):
            T: ParseIntoArray(Path, ".") → Parts → GET[LastIndex] → RowName
               GetDataTableRow(DT, RowName) → Row Found:
                 GetAllChildren(HB_SwatchList)[Index]
                 → Cast WBP_SlotSwatch → UpdateThumbnail(ThumbnailMI)
```

### RefreshSlotSwatches — Custom Event
```
ClearChildren(HB_SwatchList)
GetMaterialSlotNames(TargetFurnitureActor.FurnitureMesh) → SlotNames
ForLoop(0 → Length(SlotNames)-1):
  Body: CreateWidget(WBP_SlotSwatch) → SET SlotIndex → AddChild(HB_SwatchList)
```

### OnSlotSwatchClicked(ClickedSlotIndex) — Custom Event
```
SET SelectedSlotIndex = ClickedSlotIndex
GetAllChildren(HB_SwatchList) → ForEach:
  Cast WBP_SlotSwatch → SetSelected(ArrayIndex == SelectedSlotIndex)
```

### BTN_ResetSlot OnClicked
```
Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0:
  T:
    FurnitureMesh → GET StaticMesh → GET Material(SelectedSlotIndex) → OriginalMat
    SetMaterial(FurnitureMesh, SelectedSlotIndex, OriginalMat)
    SetArrayElem(MaterialOverrides, SelectedSlotIndex, "", SizeToFit)
    UndoManagerRef → CaptureSnapshot("ResetSlot")
    ← v1.1 UX: Update swatch thumbnail to original
    GetObjectName(OriginalMat) → RowName
    GetDataTableRow(DT, RowName) → Row Found:
      GetAllChildren(HB_SwatchList)[SelectedSlotIndex]
      → Cast WBP_SlotSwatch → UpdateThumbnail(ThumbnailMI)
```

### BTN_ResetAll OnClicked
```
Branch IsValid(TargetFurnitureActor):
  T:
    FurnitureMesh → GetNumMaterials → NumSlots
    ForLoop(0 → NumSlots-1):
      StaticMesh → GET Material(Index) → SetMaterial(FurnitureMesh, Index, OriginalMat)
    Done:
      CLEAR MaterialOverrides
      UndoManagerRef → CaptureSnapshot("ResetAll")
      Call RefreshSlotSwatches
```

---

## WBP_SlotSwatch

### Layout
```
[WBP_SlotSwatch]
└── Size Box
    └── Overlay
        ├── Border → CLImg_SlotThumb
        ├── Image_430 (selection overlay, default Hidden)
        └── BTN_Swatch
```

### Variables
```
SlotIndex : Integer
```

### Event Dispatcher
```
OnSwatchClicked(ClickedSlotIndex : Integer)
```

### BTN_Swatch OnClicked
```
Call OnSwatchClicked(ClickedSlotIndex = SlotIndex)
```

### SetSelected(bSelected : bool)
```
Branch bSelected:
  T: SetVisibility(Image_430, Visible) + SetColorAndOpacity(Image_430, White A=0.4)
  F: SetVisibility(Image_430, Hidden) + SetColorAndOpacity(Image_430, Transparent A=0)
```

### UpdateThumbnail(NewThumbnail : SoftObjectRef Texture2D)
```
SetBrushFromLazyTexture(CLImg_SlotThumb, NewThumbnail)
```

---

## WBP_MaterialCard

### OnListItemObjectSet
```
Cast To BP_MaterialItem → SET MaterialItem
Branch IsValid(InventoryRef):
  F: GetGameInstance → Cast → GET FurnitureInventoryRef → SET InventoryRef
SetBrushFromLazyTexture(LazyImage_ThumbMI, MaterialItem.ThumbnailMI)
```

### Button_ChangeMaterial OnClicked
```
Branch IsValid(InventoryRef) AND IsValid(MaterialItem):
  T: Call InventoryRef.ApplyMaterial(MaterialItem.RowName)
```

### Event Destruct
```
SET MaterialItem = None, SET InventoryRef = None
```

---

## BP_UndoManager

### Event Dispatcher
```
OnRestoreCompleted(RestoredSelectedActor : BP_FurnitureActor)
```

### RestoreSnapshot(IndexHistory)
```
1. DeselectMesh (BP_FurnitureInputManager)
2. DestroyAllActors tag "FurnitureSpawned"
3. CLEAR SpawnedActors
4. ForEach Snapshot.Meshes → Spawn + LoadAsset + SetStaticMesh + Tags + MaterialPaths restore
5. Branch SelectedMeshIndex >= 0:
   T: SET SelectedFurnitureActor, ActivateGizmo, CustomDepth
   F: SET None, DeactivateGizmo
6. RefreshButtonState
7. Branch SelectedMeshIndex >= 0:
   T: Broadcast OnRestoreCompleted(SpawnedActors[SelectedMeshIndex])
   F: Broadcast OnRestoreCompleted(None)
[Tất cả nhánh merge về RefreshButtonState → Broadcast]
```

---

## C++ — FurnitureFilterLibrary

### FilterMaterialItems — PropertyLink fix
```cpp
// Blueprint struct có GUID trong property name → dùng PropertyLink loop
for (FProperty* Prop = RowStruct->PropertyLink; Prop; Prop = Prop->PropertyLinkNext)
{
    FString PropName = Prop->GetName();
    if (PropName.Contains("MaterialFolderPath")) FolderProp = CastField<FStrProperty>(Prop);
    else if (PropName.Contains("VieName"))       VieNameProp = CastField<FTextProperty>(Prop);
    else if (PropName.Contains("EngName"))        EngNameProp = CastField<FTextProperty>(Prop);
}
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 18/05/2026 | Tạo mới |
| 1.1 | 19/05/2026 — 17:50 ICT | UX fixes: SlotSwatch (SetSelected, UpdateThumbnail), OnMeshDeselected/Selected, ApplyRestoredActor, BuildMaterialFolderTree, FilterBySearch branch, SwitchInventoryMode updates |
