# Blueprint Logic — Node Flow Reference
**HỢP NHẤT TỪ 3 file:** v1.3 base (07/06) + v1.4_patch (12/06) + v1.5_patch (15/06)
**Phiên bản:** 1.10 | **Cập nhật:** 19/07/2026 — BP_ComboManager Gate D: Noise + Aliasing Fix (Event Tick mượn cho temporal accumulation, EndPlay mở rộng)
**Mục đích:** Ghi lại thứ tự node logic để không cần chụp ảnh lại Blueprint. Full flows sống trong file BP_*.md / WBP_*.md tương ứng — file này ghi node-by-node diff và cross-BP flows.

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
    Call FilterBySearch(CurrentSearchText, CurrentCategory)  ← Fix#7: populate card ngay khi switch về
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
          T: MapFind → ExistingValue → Contains(ExistingValue, ArrayElementFolderPath):
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
      Replace(OutRow.MaterialFolderPath, "/Game/DatabaseProjectMaster/Material/MaterialInstances/", "") → RelativePath
      ParseIntoArray(RelativePath, "/") → Parts
      ForEach Parts:
        Body:
          [giống BuildFolderTree nhưng dùng MaterialFolderTree và CurrentMaterialPath]
```

### PopulateMaterialGrid
```
FilterMaterialItems(
  MaterialTable = DT_MaterialInstancesCatalog,
  SearchText    = CurrentSearchText,
  TypeTags      = MakeArray(rỗng),
  SubFolderPath = CurrentFolderPath,
  MaxResults    = 20000
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
    ForLoop(First = CurrentPage×PageSize, Last = MIN(CurrentPage×PageSize+PageSize, Len(AllFilteredMaterialRows))-1):
      Body: GET AllFilteredMaterialRows[Index] → GetDataTableRow → BuildMaterialItem → AddItem(CTV_MaterialCard)
    Done: SetText(ET_PageDisplay, CurrentPage+1 + "/" + Ceil(Len(AllFilteredMaterialRows)/PageSize))
  F:
    ClearListItems(CTV_FurnitureCard)
    ForLoop(..., Len(FilteredItems)-1):
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

### BTN_NextPage / BTN_PrevPage OnClicked
```
NextPage:
  Branch CurrentInventoryMode == Material:
    T: MaxPage = Ceil(Len(AllFilteredMaterialRows)/PageSize) - 1
    F: MaxPage = Ceil(Len(FilteredItems)/PageSize) - 1
  Branch CurrentPage < MaxPage: T → SET CurrentPage+1 → DisplayPage

PrevPage:
  Branch CurrentPage > 0: T → SET CurrentPage-1 → DisplayPage
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
      Cast → Branch MeshPath == TargetMeshPath: T → SET TargetFurnitureActor → Break
Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0:
  T:
    GetDataTableRow(DT_MaterialInstancesCatalog, MaterialRowName) → OutRow
    Row Found → SET PendingMaterialPath = OutRow.MaterialPath → Call LoadAndApplyMaterial
```

### LoadAndApplyMaterial (Custom Event, Event Graph)
```
MakeSoftObjectPath(PendingMaterialPath) → ToSoftObjectReference → AsyncLoadAsset
  Completed:
    Cast Object To MaterialInterface → MI_Source
    Branch IsValid(MI_Source) AND IsValid(TargetFurnitureActor):
      T:
        CreateDynamicMaterialInstance(TargetFurnitureActor.FurnitureMesh, SelectedSlotIndex, MI_Source) → MID
        SetMaterial(FurnitureMesh, SelectedSlotIndex, MID)
        SetArrayElem(TargetFurnitureActor.MaterialOverrides, SelectedSlotIndex, PendingMaterialPath, SizeToFit=True)
        ClearTimer(ApplyMaterialTimerHandle)
        SetTimerByFunctionName("CaptureMaterialSnapshot", 0.5s) → SET ApplyMaterialTimerHandle
```

### CaptureMaterialSnapshot / OnSceneRestored / BTN_ResetSlot / BTN_ResetAll
```
CaptureMaterialSnapshot: GET UndoManagerRef → CaptureSnapshot("ChangeMaterial")

OnSceneRestored(RestoredSelectedActor):
  ← Bound từ UndoManagerRef.OnRestoreCompleted trong Event Construct
  Branch CurrentInventoryMode == Material:
    T: SET TargetFurnitureActor = RestoredSelectedActor
       Branch IsValid → SET Visibility(HB_SlotSwatches, Visible/Collapsed)

BTN_ResetSlot:
  Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0:
    T: StaticMesh → GET Material(SelectedSlotIndex) → OriginalMat
       SetMaterial(FurnitureMesh, SelectedSlotIndex, OriginalMat)
       SetArrayElem(MaterialOverrides, SelectedSlotIndex, "", SizeToFit)
       CaptureSnapshot("ResetSlot")

BTN_ResetAll:
  Branch IsValid(TargetFurnitureActor):
    T: NumSlots → ForLoop → GET Material(Index) → SetMaterial(...)
       Done: CLEAR MaterialOverrides → CaptureSnapshot("ResetAll")
```

### Event Construct (Sequence)
```
Then 0: SetTimer(0.1s) → InitMinimizedHeight → SET CurrentCategory
Then 1: CLEAR AllFurnitureItems → GetAllAssets → ForEach → Cast DA_FurnitureItem → ADD
        → BindCategoryEvents → FilterBySearch
Then 2: BuildFolderTree → SET FurnitureFolderTree = FolderTree → PopulateTreeColumn → FilterByFolderPath → UpdateTabHighlight
Then 3: GetAllActors(BP_UndoManager)[0] → SET UndoManagerRef → Bind OnRestoreCompleted → OnSceneRestored
```

### C5.0 — Combo Folder Tree + Chip Nav (v3.1 — 25/06/2026)

> Full doc: **WBP_FurnitureInventory.md §C5.0**. Đây là tóm tắt node-flow để tra cứu nhanh.

#### PopulateComboTreeColumn() — Function
```
Clear Children(VerticalBox_44)
// "Tat ca" (IndentLevel=0) | "Chua phan loai" (IndentLevel=0, if bHasUncategorized)
// Cấp 1 từ Map[""] → IndentLevel=0
Map Find(ComboFolderTree, "") → Lvl1CSV, bFound
Branch bFound:
  True → ForEach ParseIntoArray(Lvl1CSV, ",") (lvl1):
           Create WBP_TreeNode Node1 (FolderPath=lvl1, FolderName=lvl1, IndentLevel=0)
           Add Child | Bind OnNodeSelected → OnComboTreeNodeClicked
           // Cấp 2 từ Map[lvl1] → IndentLevel=1 (lồng ngay sau Node1)
           Map Find(ComboFolderTree, lvl1) → Lvl2CSV, bFound2
           Branch bFound2:
             True → ForEach ParseIntoArray(Lvl2CSV, ",") (lvl2):
                      FullPath2 = lvl1 + "/" + lvl2
                      Create WBP_TreeNode Node2 (FolderPath=FullPath2, FolderName=lvl2, IndentLevel=1)
                      Add Child | Bind → OnComboTreeNodeClicked
```

#### OnComboTreeNodeClicked(SelectedPath, IndentLevel) — Custom Event
```
SET CurrentComboFolderPath = SelectedPath
Branch(IndentLevel == 0):
  True  → ClearChildren(VB_ChipTagArea) → FilterComboByFolder(SelectedPath) → PopulateComboTreeColumn()
  False → ClearChildren(VB_ChipTagArea) → FilterComboByFolder(SelectedPath)
           Map Find(ComboFolderTree, SelectedPath) → ChildCSV, bFound
           Branch bFound:
             False → [merge] → PopulateComboTreeColumn()   ← leaf folder, không gen chip
             True  → Create WBP_ChipRow(RowIndentLevel=2)
                      ForEach ParseIntoArray(ChildCSV, ",") (element):
                        Create WBP_ChipTag (FolderPath=SelectedPath+"/"+element, IndentLevel=2)
                        Bind OnChipSelected → OnComboChipTagClicked | AddChild(Row.HBox_ChipRow)
                      Completed: AddChild(VB_ChipTagArea, Row)
           PopulateComboTreeColumn()
```

#### OnComboChipTagClicked(SelectedPath_ChipTag, IndentLevel_ChipTag) — Custom Event (clone OnChipTagClicked)
```
SET CurrentComboFolderPath = SelectedPath_ChipTag
SET RowCount = GetChildrenCount(VB_ChipTagArea)
ForLoop(0, RowCount - IndentLevel_ChipTag - 1):
  RemoveChildAt(VB_ChipTagArea, RowCount - 1 - Index)   ← xóa từ dưới lên
Completed → FilterComboByFolder(SelectedPath_ChipTag)
Map Find(ComboFolderTree, SelectedPath_ChipTag) → ChildCSV, bFound
Branch bFound:
  False → dead-end
  True  → Create WBP_ChipRow(RowIndentLevel=IndentLevel_ChipTag+1)
           ForEach ParseIntoArray(ChildCSV, ",") (element):
             Create WBP_ChipTag (FolderPath=Append(SelectedPath_ChipTag,"/",element), IndentLevel=IndentLevel_ChipTag+1)
             Bind OnChipSelected → OnComboChipTagClicked | AddChild(Row.HorizontalBox_ChipRow)
           Completed: AddChild(VB_ChipTagArea, Row)
```

#### OnComboTreeNodeRightClicked(FolderPath) — Custom Event
```
Print String("RightClick: " + FolderPath)   [DEBUG]
Branch(FolderPath == "__ALL__" OR FolderPath == ""):
  True  → dead-end   ← sentinel guard
  False → Create WBP_LibraryContextMenu → LibMenu
           SET LibMenu.MenuMode="Folder" | TargetFolderPath=FolderPath
           Bind OnRequestRenameFolder/MoveFolder/DeleteFolder → stubs
           AddMenuItem("✏️ Đổi tên","") | AddMenuItem("📁 Chuyển vào…","") | AddMenuItem("🗑️ Xóa","")
           Set Input Mode UI Only | LibMenu.ShowAt(Get Mouse Position on Viewport)
```

### NF — New Folder (context menu, 04/07/2026)

> Full doc: **WBP_FurnitureInventory.md §NF**. Tóm tắt node-flow tra cứu nhanh.
> Context-menu part DONE. Nút "+" đầu cột tree (dùng `GetNewFolderParent`) còn nợ.

#### GetChildFolderNames(ParentPath) → Array\<String\> — Pure
```
Map Find(ComboFolderTree, ParentPath) → CSV, bFound
Branch bFound:
  True  → Parse Into Array(CSV, ",") → Return
  False → Return Make Array (rỗng)
```

#### GetUniqueNewFolderName(ParentPath) → String — Function
```
SET Existing = GetChildFolderNames(ParentPath)
SET Candidate = "New Folder" | SET Counter = 2
Branch Array_Contains(Existing, Candidate)==false:
  True  → Return Candidate
  False → While[Array_Contains(Existing, Candidate)]:
            Body: SET Candidate = "New Folder (" + IntToString(Counter) + ")" → SET Counter+1
            Completed: Return Candidate
```

#### GetNewFolderParent() → String — Pure
```
Branch(CurrentComboFolderPath=="" OR StartsWith("__")):
  True  → Return ""
  False → Return CurrentComboFolderPath
```

#### OnRequestNewFolder(ParentPath) — Custom Event
```
GetUniqueNewFolderName(ParentPath) → NewName
Branch(ParentPath==""): True → FullPath=NewName | False → FullPath=ParentPath+"/"+NewName
[merge] → ComboSerializer::CreateEmptyFolder(FullPath) → bOK
Branch bOK:
  True  → RefreshComboFolderUI() → OnRequestRenameFolder(FullPath)   ← tái dùng C5.2 rename phase
  False → Print "Không tạo được: "+FullPath
```
> KHÔNG CaptureSnapshot, KHÔNG đổi CurrentComboFolderPath (no-navigate).

#### CB_CreateNewFolder — Custom Event (bound Item0.OnItemClicked, đầu chuỗi menu trong OnComboTreeNodeRightClicked)
```
IsValid(LibraryMenuRef):
  True → SET LocalTargetPath = LibraryMenuRef.TargetFolderPath   ← cache TRƯỚC Hide
       → LibraryMenuRef.Hide → SET LibraryMenuRef = None
       → ParentOf(LocalTargetPath) → ParentPath   ← CÙNG CẤP, không phải con
       → OnRequestNewFolder(ParentPath)
  False → [dead-end]
```
> OnComboTreeNodeRightClicked thêm `AddMenuItem("Create New Folder")` ĐẦU chuỗi (trước "Đổi tên"), nối tiếp — KHÔNG 2 nhánh song song từ Entry.

### NF.G3 — Nút "+" đầu cột tree (06/07/2026, DONE)

> Full doc: **WBP_FurnitureInventory.md §PopulateComboTreeColumn / §OnComboTreeNodeClicked**. Không hàm mới — tái dùng `GetNewFolderParent`/`OnRequestNewFolder` ở trên.

```
PopulateComboTreeColumn(): thêm khối ĐẦU TIÊN (trước node "Tất cả")
  Create Widget(WBP_TreeNode) → PlusNode
  SET FolderPath="__NEWFOLDER__" | FolderName="+ Tao folder" | IndentLevel=0
  RefreshDisplay(bIsActive=false) → Add Child → Bind OnNodeSelected → OnComboTreeNodeClicked
  (KHÔNG bind OnNodeRightClicked)

OnComboTreeNodeClicked(SelectedPath, IndentLevel): thêm guard ĐẦU TIÊN
  Entry → Branch(SelectedPath == "__NEWFOLDER__")
       True  → OnRequestNewFolder(GetNewFolderParent())   ← KẾT THÚC
       False → ...logic cũ giữ nguyên...
```
> Khác biệt hành vi so với context-menu "Create New Folder": nút "+" tạo TRONG folder đang xem (`GetNewFolderParent`), context-menu tạo CÙNG CẤP node bị right-click (`ParentOf`). Test PASS 5/5.

### RebuildChipRowForPath + RefreshChipBreadcrumb (06/07/2026, bug fix chip area không tự refresh)

> Full doc: **WBP_FurnitureInventory.md §Bug fix — Chip area không tự refresh**. Gộp code tạo ChipRow trùng lặp từ `OnComboTreeNodeClicked` + `OnComboChipTagClicked` thành 1 hàm dùng chung, và thêm hàm tự-vẽ-lại-toàn-bộ gọi từ `RefreshComboFolderUI` (fix chip area không tự refresh sau Move/Xóa/Rename folder).

```
RebuildChipRowForPath(Path, OwnIndentLevel) — Function:
  Map Find(ComboFolderTree, Path) → ChildCSV, bFound
  Branch bFound:
    False → return
    True  → Create WBP_ChipRow(RowIndentLevel=OwnIndentLevel+1)
             ForEach ParseIntoArray(ChildCSV, ",") (element):
               Create WBP_ChipTag (FolderPath=Path+"/"+element, IndentLevel=OwnIndentLevel+1)
               Bind OnChipSelected → OnComboChipTagClicked
               Bind OnChipRightClicked → OnComboTreeNodeRightClicked   ← C5.7a
               AddChild(Row.HorizontalBox_ChipRow)
             Completed: AddChild(VB_ChipTagArea, Row)

RefreshChipBreadcrumb() — Function, gọi từ RefreshComboFolderUI SAU UpdateComboFolderHighlights (cả 3 nhánh):
  ClearChildren(VB_ChipTagArea)
  Branch(CurrentComboFolderPath=="__ALL__" OR ==""): True → return
  ParseIntoArray(CurrentComboFolderPath, "/") → Segments   ← delimiter "/" (1 ký tự)
  Branch(Segments.Length <= 1): True → return   ← cấp 1, tree tự vẽ cấp 2 lồng
  BuildPath = Segments[0]+"/"+Segments[1] | Lvl = 1
  RebuildChipRowForPath(BuildPath, Lvl)          ← luôn vẽ hàng đầu
  Branch(Segments.Length > 2):
    True → ForLoop(2, Segments.Length-1):
             BuildPath += "/"+Segments[Index] | Lvl += 1
             RebuildChipRowForPath(BuildPath, Lvl)
```
> 3 bug tìm & fix trong lúc build 2 hàm này: (#1) RefreshComboFolderUI chỉ nối RefreshChipBreadcrumb ở 1/3 nhánh — 2 nhánh còn dead-end; (#2) ParseIntoArray delimiter gõ nhầm `"/ "` thay vì `"/"` → Segments không tách được; (#3) guard đầu hàm dùng nhầm BooleanAND thay BooleanOR (vô hại vì Branch sau vô tình bắt được). Chi tiết: WBP_FurnitureInventory.md.

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

## BP_FurnitureInputManager — Box Select (Sprint 2)

> Full flow + lý do từng quyết định: **BP_FurnitureInputManager.md**. Đây là tóm tắt node-flow.

### Mouse Left Pressed (defer)
```
SET bLMBHeld = True → Set Input Mode Game And UI
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
[Guard inventory]: GetGameInstance→Cast→GET FurnitureInventoryRef→IsValid+IsInViewport→SET bInventoryOpen
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
  Then 0: đóng context menu (IsValid ContextMenuRef → Remove → SET None)
  Then 1: Branch bIsBoxSelecting:
           T → GetMousePos → FinishBoxSelect → IsValid(OverlayRef)→HideBox → SET bIsBoxSelecting=False → SET PendingClickActor=None
  Then 2: Branch bIsPendingBoxSelect:
           T → SET bIsPendingBoxSelect=False → Branch IsValid(PendingClickActor):
                 T → SelectSingleActor + CaptureSnapshot("Select") + SET None
                 F → Branch Ctrl: F → DeselectAll + CaptureSnapshot("Deselect") → Branch bIsReplaceMode → exit replace
```

### FinishBoxSelect(EndPos)
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

## BP_UndoManager — Tóm tắt (Full flow → BP_UndoManager.md v1.8)

> ⚠️ Flow CaptureSnapshot v1.1 single ở đây là **LEGACY (cũ)**. Bản multi-select v1.8 (TempSelectedIndices, Version 4, EditModeStackSnapshot) — xem **BP_UndoManager.md** (authoritative).

### ⭐ FIX v1.5 — CLEAR TempSelectedIndices đầu hàm CaptureSnapshot
```
Function Entry → CLEAR TempSelectedIndices → [Step 1...]
```
Lý do: TempSelectedIndices là class var → stale qua các lần gọi. Thao tác Deselect đi nhánh bypass đoạn build → giá trị cũ lọt vào snapshot → Undo nhảy cóc. CLEAR đầu hàm = phòng thủ. (Print debug trong ForEach → in 1 lần/mesh → ngỡ "double capture" — sai hướng.)

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
for (FProperty* Prop = RowStruct->PropertyLink; Prop; Prop = Prop->PropertyLinkNext)
{
    FString PropName = Prop->GetName();
    if (!FolderProp  && PropName.Contains(TEXT("MaterialFolderPath")))
        FolderProp  = CastField<FStrProperty>(Prop);
    else if (!VieNameProp && PropName.Contains(TEXT("VieName")))
        VieNameProp = CastField<FTextProperty>(Prop);
    else if (!EngNameProp && PropName.Contains(TEXT("EngName")))
        EngNameProp = CastField<FTextProperty>(Prop);
}
```

### Filter logic
```
bFilterBySubFolder = !SubFolderPath.IsEmpty()
bFilterByType      = TypeTags.Num() > 0
bFilterBySearch    = !SearchText.IsEmpty()

For each row:
  if bFilterByType      → FolderValue.Contains(any Tag)    → skip nếu không match
  if bFilterBySubFolder → FolderValue.Contains(SubFolderPath) → skip nếu không match
  if bFilterBySearch    → VieName/EngName.Contains(SearchText) → skip nếu không match
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

# ═══════════════ SPRINT 3 — GROUP (v1.4 — bản FINAL sau regression 10/06) ═══════════════

## GenerateGroupID() → String
```
New Guid → To String → Append "g_" prefix → "g_<GUID>"
```

## GetGroupChildren(InGroupID) → Array\<BP_FurnitureActor\>
```
CLEAR Children (đầu hàm)
Get All Actors With Tag("FurnitureSpawned") → ForEach:
  Cast → IsValid → Branch (GroupID == InGroupID): True → ADD to Children
  (Cast Failed KHÔNG nối Return)
Return Children
```

## FindGroupData(InGroupID) → (S_GroupData, Index, bFound)
```
ForEach Groups → For Each With Break → so GroupID → match: trả data + index + true
```
> ⚠ KHÔNG có output Index ở 1 số call site Sprint 4 — `FindGroupData` TRẢ Index. Khi cần Index dùng rebuild pattern thay Set Array Elem.

## CreateGroup() — Ctrl+G (v1.4 — nested, Sprint 4 T6 sửa ParentGroupID)
```
Guard SelectedActors.Length >= 2
GenerateGroupID → NewGID
Auto-name = "Nhóm " + (Groups.Length + 1)
Make S_GroupData(NewGID, name, ParentGroupID=GetCurrentEditScope(), bIsLocked=false) → ADD to Groups
SyncGroupsToContainer
ForEach SelectedActors → Cast → SET GroupID = NewGID
CaptureSnapshot("CreateGroup")
Broadcast OnGroupCreated(NewGID)
SelectActors(SelectedActors)   ← re-fire OnSelectionChanged để info bar update
```
> T6 Sprint 4 sửa: `ParentGroupID = GetCurrentEditScope()` thay "". Ngoài edit → ""; trong edit → sub-group.

## SyncGroupsToContainer()
```
Get All Actors Of Class(BP_GroupsContainer)[0] → IsValid → SET Container.Groups = self.Groups
```

## SNAPSHOT v3 (BP_UndoManager Sprint 3 — full flow xem BP_UndoManager.md)

### CaptureSnapshot — các điểm Sprint 3
```
Step 0  : CLEAR TempSelectedIndices (đầu hàm)
Step 0b : GetGroupsForSnapshot → SET TempGroups   ← fix impure-timing (gọi SỚM, SET temp var)
Step 3  : mỗi placement capture GroupID = actor.GroupID
Make S_SceneSnapshot: Groups = TempGroups (đọc temp var), Version = 3
```

### RestoreSnapshot — các điểm Sprint 3 (+ Sprint 4 T8 chèn ValidateEditMode)
```
Step 4 : ForEach spawn + restore material + SET actor.GroupID = Placement.GroupID
Step 5b: Branch Version>=3 → CLEAR Groups → ADD Snapshot.Groups → SyncGroupsToContainer
         SET InputManager.EditModeStack = Snapshot.EditModeStackSnapshot  ← Sprint 4 A12
         ValidateEditMode()                                                ← Sprint 4 T8
Step 6b: Branch SelectedActors.Length > 0 → SelectActors / DeselectAll+DeactivateGizmo
Step 7 : Broadcast OnRestoreCompleted (dùng RestoredBPActor)
```

---

# ═══════════════ SPRINT 4 — EDIT MODE + NESTED GROUP (v1.4) ═══════════════

## Variables mới (BP_FurnitureInputManager)
```
EditModeStack : Array<String>   ← stack GroupID đang edit. Rỗng = không edit. KHÔNG SaveGame. CLEAR ở End Play.
```

## Dispatcher mới
```
OnEditModeChanged(bActive : Boolean, GroupID : String)
```

---

## ─── T1: HELPER FUNCTIONS ───

### GetCurrentEditScope() → String
```
Branch(EditModeStack.Length > 0):
  True  → EditModeStack → Last Index → Get → Return
  False → Return ""
```

### GetChildGroups(InGroupID) → Array\<S_GroupData\>  (group con TRỰC TIẾP)
```
CLEAR LocalChildren
ForEach Groups (g):
  BREAK g → ParentGroupID
  Branch(g.ParentGroupID == InGroupID): True → ADD g → LocalChildren
Completed → Return LocalChildren
```

### GetGroupRoot(InGroupID) → String  (leo lên gốc, depth guard 10)
```
SET Current = InGroupID
ForLoop(0..9):
  FindGroupData(Current) → (data, bFound)
  bFound==False → Return Current
  BREAK data → ParentGroupID
  ParentGroupID=="" → Return Current
  Else → SET Current = ParentGroupID
Completed → Return Current
```

### WalkUpUntilParent(InGroupID, TargetParent) → String  (con trực tiếp của TargetParent trên đường lên)
```
SET Current = InGroupID
ForLoop(0..9):
  FindGroupData(Current) → (data, bFound)
  bFound==False → Return ""
  BREAK data → ParentGroupID
  ParentGroupID==TargetParent → Return Current    ← TÌM THẤY
  ParentGroupID=="" → Return ""                   ← lên hết gốc
  Else → SET Current = ParentGroupID
Completed → Return ""
```

### GetAllDescendantActors(InGroupID) → Array\<BP_FurnitureActor\>  ⭐ ĐỆ QUY
```
CLEAR LocalResult
GetGroupChildren(InGroupID) → ForEach_1: ADD Element → LocalResult
  Completed → GetChildGroups(InGroupID) → ForEach_2 (cg):
    BREAK cg → GroupID
    GetAllDescendantActors(cg.GroupID) → ForEach_3: ADD Element → LocalResult
    Completed → (để TRỐNG — không nối vòng về)
  Completed → Return LocalResult
```
> ForEach_3.Completed để TRỐNG (không nối vòng về). Local var độc lập mỗi stack frame (đã verify).

### GetGroupsInHierarchy(InGroupID) → Array\<S_GroupData\>  ⭐ ĐỆ QUY (bridge Combo S5)
```
CLEAR LocalGroups
FindGroupData(InGroupID) → (data, bFound)
Branch(bFound): True → ADD data → LocalGroups; False → (tiếp)
(merge) → GetChildGroups(InGroupID) → ForEach_1 (cg):
  BREAK cg → GroupID
  GetGroupsInHierarchy(cg.GroupID) → ForEach_2: ADD Element → LocalGroups
  Completed → (để TRỐNG)
Completed → Return LocalGroups
```
> Branch True/False của bFound đều MERGE về GetChildGroups (không dead-end).

### ResolveSelectionUnit(Actor, EditScope) → Array\<BP_FurnitureActor\>  ⭐ NÃO Sprint 4
> ⚠ THỨ TỰ NHÁNH BẮT BUỘC: EditScope != "" kiểm tra TRƯỚC gid == "" (Q9a).
```
IsValid(Actor)==False → Return []
Cast → GET GroupID → gid

Branch(EditScope != ""):                       ← ĐANG EDIT (xét trước)
  True →
    Branch(gid == EditScope): True → Return Make Array(Actor)               ← member trực tiếp
    Branch(gid == ""):        True → Return []                               ← đồ rời ngoài scope
    WalkUpUntilParent(gid, EditScope) → ancestor
    Branch(ancestor != ""):   True → Return GetAllDescendantActors(ancestor) ← sub-group
                              False → Return []                              ← ngoài scope
  False →                                     ← KHÔNG EDIT
    Branch(gid == ""):        True → Return Make Array(Actor)               ← đồ rời → chính nó
    GetGroupRoot(gid) → root → Return GetAllDescendantActors(root)          ← group → cả cây
```

### ApplyEditModeVisual() / RemoveEditModeVisual() — STUB RỖNG
> Chỉ Entry, T9 đổ body, Stencil 200 reserved.

---

## ─── T2: ExpandSelectionWithGroups (VIẾT LẠI — thay bản Sprint 3 inline) ───
```
SET ActorsCopy = RawActors
CLEAR LocalResult
GetCurrentEditScope() → Scope
ForEach ActorsCopy (Actor):
  ResolveSelectionUnit(Actor, Scope) → ForEach_inner (Unit):
    Branch NOT Contains(LocalResult, Unit): True → ADD Unit → LocalResult
Completed → Return LocalResult
```
> Caller (OnLMBReleased Then2, FinishBoxSelect) KHÔNG đổi — tự ăn logic mới.
> Tick fallback đổi từ SelectSingleActor → DeselectAll + ExpandSelectionWithGroups + SelectActors.

---

## ─── T3: ENTER / EXIT EDIT MODE ───

### GetEditBreadcrumb() → String
```
SET Result = ""
ForEach EditModeStack (Element, ArrayIndex):
  FindGroupData(Element) → (data, bFound)
  Branch(bFound):
    False → Return Result (early exit)
    True  → Branch(ArrayIndex == 0):
              True  → SET Result = data.GroupName
              False → SET Result = Append(Result, "›", data.GroupName)
Completed → Return Result
```

### EnterEditMode(InGroupID)
```
Branch(InGroupID == "") → True: Return
FindGroupData(InGroupID) → (_, bFound) → Branch(bFound==False) → True: Return
ADD InGroupID → EditModeStack
DeselectAll → ApplyEditModeVisual
Broadcast OnEditModeChanged(True, InGroupID)
```

### ExitEditModeOneLevel()  (nút "↑ Lên 1 cấp")
```
Branch(EditModeStack.Length == 0) → True: Return
GetCurrentEditScope() → SET Exited
EditModeStack → Last Index → REMOVE INDEX (POP)
Branch(EditModeStack.Length == 0):
  True (thoát hẳn) →
    RemoveEditModeVisual → DeselectAll
    GetAllDescendantActors(Exited) → SET LocalTree
    Branch(LocalTree.Length > 0): True → SelectActors(LocalTree)
    Broadcast OnEditModeChanged(False, "")
  False (còn cha) →
    ApplyEditModeVisual → DeselectAll
    GetAllDescendantActors(Exited) → SET LocalTree
    Branch(LocalTree.Length > 0): True → SelectActors(LocalTree)
    GetCurrentEditScope() → NewScope
    Broadcast OnEditModeChanged(True, NewScope)
```

### ExitEditModeFull()  (nút "✖ Thoát")
```
Branch(EditModeStack.Length == 0) → True: Return
EditModeStack → GET[0] → SET RootScope
CLEAR EditModeStack → RemoveEditModeVisual → DeselectAll
GetAllDescendantActors(RootScope) → SET LocalTree
Branch(LocalTree.Length > 0): True → SelectActors(LocalTree)
Broadcast OnEditModeChanged(False, "")
```

---

## ─── T4: TryEnterEditFromSelection ───
```
Branch(IsValid(PrimarySelectedActor)==False) → True: Return
Cast → GET GroupID → gid
Branch(gid=="") → True: Return                   ← đồ rời
Branch(EditModeStack.Length >= 3) → True: Return ← giới hạn 3 cấp
GetCurrentEditScope() → Scope
Branch(Scope == ""):
  True  → EnterEditMode(GetGroupRoot(gid))        ← chưa edit → vào gốc
  False → WalkUpUntilParent(gid, Scope) → SET Sub
          Branch(Sub != ""): True → EnterEditMode(Sub)  ← vào sub-group con trực tiếp
```

---

## ─── T5: WBP_MeshControls — Edit Mode UI (xem WBP_MeshControls.md v1.6 — canonical) ───

### Event Construct (thêm sau bind OnSelectionChanged)
```
Bind Event to OnEditModeChanged (Target=InputRef) → OnEditModeChangedInfoBar
Set Visibility(HB_EditModeBar, Collapsed)
Set Visibility(BTN_EnterEdit, Collapsed)
```

### OnEditModeChangedInfoBar(bActive, GroupID)
```
Branch(bActive):
  True  → Set Visibility(HB_EditModeBar, Visible)
          InputManager[0] → GetEditBreadcrumb → SetText(TXT_EditBreadcrumb, "✏️ Đang chỉnh: " + BreadStr)
  False → Set Visibility(HB_EditModeBar, Collapsed)
```

### OnSelectionChangedInfoBar — Sequence.Then 2
```
Branch(IsValid(Primary)):
  True  → Cast → GET GroupID → Branch(GroupID != ""):
            True  → Set Visibility(BTN_EnterEdit, Visible)
            False → Set Visibility(BTN_EnterEdit, Collapsed)
  False → Set Visibility(BTN_EnterEdit, Collapsed)
```

### OnClicked
```
BTN_EnterEdit    → InputManager[0] → TryEnterEditFromSelection
BTN_ExitOneLevel → InputManager[0] → ExitEditModeOneLevel
BTN_ExitFull     → InputManager[0] → ExitEditModeFull
```

---

## ─── T7: PruneEmptyGroups + UngroupActors ───

### PruneEmptyGroups()
```
CLEAR LocalKeep
ForEach Groups (g):
  GetAllDescendantActors(g.GroupID) → Length  ← PHẢI dùng GetAllDescendantActors (không GetGroupChildren — xét cả subtree)
  Branch(Length > 0): True → ADD g → LocalKeep
Completed → SET Groups = LocalKeep → SyncGroupsToContainer
```

### UngroupActors(InGroupID) — PEEL-ONE-LEVEL
```
Entry → Branch(InGroupID=="") → True: Return
       → GetCurrentEditScope → SET scope
       → WalkUpUntilParent(InGroupID, scope) → SET target
       → Branch(target=="") → True: Return
       → FindGroupData(target) → (data, Found) → Branch(Found==False) → True: Return
       → BREAK data → SET parentGID = data.ParentGroupID

B1: actor con TRỰC TIẾP → về cha
    GetGroupChildren(target) → ForEach_1(actor): Cast → SET GroupID = parentGID
    Completed →

B2: sub-group con trực tiếp đổi ParentGroupID về cha
    CLEAR LocalNewGroups
    GET Groups → ForEach_2(g):
      BREAK g → ParentGroupID
      Branch(g.ParentGroupID == target):
        True  → MAKE S_GroupData(g.GroupID, g.GroupName, parentGID, g.bIsLocked) → ADD LocalNewGroups
        False → ADD g → LocalNewGroups
    Completed → SET Groups = LocalNewGroups

B3: xóa target khỏi Groups
    CLEAR LocalKeep
    ForEach_3 Groups (g2):
      Branch(g2.GroupID != target): True → ADD g2 → LocalKeep
      Completed → SET Groups = LocalKeep
                → SyncGroupsToContainer
                → CaptureSnapshot("Ungroup")    ← 1 lần, ở B3.Completed
                → SelectActors(SelectedActors)
                → Broadcast OnGroupDestroyed(target)
```
> Caller (Ctrl+Shift+G): `IsValid(PrimarySelectedActor) → GET GroupID → Branch!="" → UngroupActors(GroupID)`.
> FindGroupData không trả Index dùng được → dùng rebuild pattern (B2/B3). CaptureSnapshot 1 lần ở B3 (tránh spam).

---

## ─── T8: ValidateEditMode (trong BP_UndoManager) ───
```
CLEAR LocalValid (Array<String>)
Get All Actors Of Class(BP_FurnitureInputManager)[0] → Cast → InputRef
Branch(IsValid(InputRef)) → False: Return
GET InputRef.EditModeStack → For Each Loop WITH BREAK (gid):
  LoopBody → InputRef.FindGroupData(gid) → (_, bFound)
           → Branch(bFound):
               True  → ADD gid → LocalValid
               False → BREAK              ← group mất → cắt từ đây lên (con cũng vô nghĩa)
  Completed →
SET InputRef.EditModeStack = LocalValid
Branch(InputRef.EditModeStack.Length == 0):
  True  → InputRef.RemoveEditModeVisual → Broadcast OnEditModeChanged(False, "")
  False → InputRef.ApplyEditModeVisual → GetCurrentEditScope → Scope → Broadcast OnEditModeChanged(True, Scope)
```
**Vị trí:** RestoreSnapshot: sau SyncGroupsToContainer (Step 5b) + sau SET EditModeStack (A12), trước Step 6b re-fire selection. Lý do: ValidateEditMode đọc Groups + EditModeStack → phải SAU cả hai.

---

## ─── BUG FIX (12/06) — Replace Mesh preserve GroupID ───

**File:** WBP_DragOverlay_FurnitureCard — BTN_ChangeMesh OnClicked — trong ForEach MeshesToReplace.
```
(sau spawn NewActor, TRƯỚC Destroy OldActor):
  Cast OldActor → BP_FurnitureActor → GET GroupID → OldGroupID
  SET NewActor.GroupID = OldGroupID
```
> PHẢI đặt TRƯỚC Destroy Actor(OldActor) — sau destroy không đọc được GroupID nữa.

---

## ─── LƯU Ý QUAN TRỌNG SPRINT 4 ───

- **ResolveSelectionUnit:** thứ tự `EditScope!=""` TRƯỚC `gid==""` là BẮT BUỘC (Q9a).
- **Đệ quy BP Function** (GetAllDescendantActors, GetGroupsInHierarchy): local var stack-độc-lập, ForEach inner Completed để TRỐNG.
- **Return trong ForLoop Body** (GetGroupRoot/WalkUpUntilParent): thoát hàm ngay — đúng.
- **UngroupActors B1→B2→B3** nối tuần tự qua Completed. CaptureSnapshot 1 lần ở B3.Completed.
- **Click ngoài scope khi edit** → CLEAR selection nhưng VẪN ở edit mode (MVP — D4-4).

---

# ═══════════════ LEARNINGS (v1.5 — Sprint 4 Bug Fix 15/06) ═══════════════

### L-NEW-1: Branch False dead-end — Sequence vs Event (BÀI HỌC ĐẮT GIÁ)

```
TRONG SEQUENCE NODE (Then 0, Then 1...):
  Branch False → dead-end → OK ✅
  Sequence tự kích hoạt Then tiếp theo, không cần merge.

TRONG EVENT bình thường (không Sequence):
  Branch False → dead-end → FATAL ❌
  Logic sau Branch KHÔNG chạy.
  Ví dụ OnDrop: Return Node không reach → return false → UMG gọi OnDragCancelled → Destroy PreviewActorRef → mesh biến mất.
```

**Quy tắc:** Trước khi viết Branch bất kỳ, xác định context:
- Trong `Sequence.Then`: False dead-end OK.
- Trong Event/Custom Event chain: mọi nhánh phải reach exec endpoint.

---

### L-NEW-2: Function output pins không thể CLEAR — dùng Temp Array buffer

```
Entry: CLEAR TempGroupUnits (class var), CLEAR TempLooseActors (class var)
ForEach:
  LoopBody → ADD vào TempGroupUnits / TempLooseActors  (không ADD vào output pin trực tiếp)
Completed:
  SET OutGroupUnits  = TempGroupUnits
  SET OutLooseActors = TempLooseActors
```
> Pattern tương tự TempGroups (Sprint 3) và TempEditModeStack (Sprint 4 A12). Xem L-NEW-5.

---

### L-NEW-3: ComputeSelectionUnits phải chạy TRƯỚC guard

**Sai:** Guard `SelectedActors.Length < 2 → Return` TRƯỚC ComputeSelectionUnits — Length tính theo actor, không theo unit.

**Đúng:**
```
ComputeSelectionUnits(SelectedActors) → (GroupUnits, LooseActors)
(GroupUnits.Length + LooseActors.Length) < 2 → Return
```

---

### L-NEW-4: Truy cập Blueprint export text thay vì screenshot

**Phương pháp:** User copy-paste K2Node text từ Blueprint graph editor (Edit → Copy). AI đọc pin `LinkedTo` để trace exec flow và data connections chính xác.

**Phát hiện được qua LinkedTo:**
- ForEach Completed không nối (dead-end)
- Not Equal vs Equal nhầm (DefaultValue)
- Output pin swapped (LinkedTo trỏ sai node)
- Unnecessary cast (ErrorMsg)

---

### L-NEW-5: EditModeStack là runtime state — không persist qua Undo nếu không snapshot

**Nguyên tắc:** Mọi state cần undo-able phải nằm trong S_SceneSnapshot. Runtime-only vars không được restore.

**Checklist khi thêm state mới:**
1. State này có cần undo-able không?
2. Nếu có → thêm field vào S_SceneSnapshot + SET trong CaptureSnapshot + SET trong RestoreSnapshot
3. Thứ tự restore: SET state → ValidateEditMode (nếu có) → broadcast → re-fire selection

---

### L-NEW-6: ValidateEditMode đọc Groups + EditModeStack — restore cả hai trước khi gọi

**Thứ tự bắt buộc trong RestoreSnapshot:**
```
1. SyncGroupsToContainer                                        ← Groups ready
2. SET InputManager.EditModeStack = Snapshot.EditModeStackSnapshot ← Stack ready
3. ValidateEditMode()                                           ← đọc cả hai → kết quả đúng
4. [Step 6b selection re-fire...]
```

---

## BP_ComboManager — Debug capture thumbnail (phím T)

Biến: `Cmb_CaptureHandle` (Scene Capture 2D, Object Reference, default None). Biến debug `bDebugTestThumb` (Boolean, default False) dùng chung với Enable Input ở BeginPlay — gỡ cả 2 sau khi G4 PASS.

Event BeginPlay:
```
▶→ Branch(bDebugTestThumb)
     True ▶→ Enable Input(Target=self,
               Player Controller ●← Get Player Controller(0))
```

Keyboard Event T (Pressed):
```
▶→ Branch(IsValid(Cmb_CaptureHandle))
     True  ▶→ [dead-end — chặn double-trigger, đang chụp dở]
     False ▶→ Get All Actors with Tag("FurnitureSpawned") ●→ Actors
              ▶→ Begin Combo Capture(Combo Actors=Actors,
                   Extra Hidden Actors=[mảng rỗng], Resolution=1024)
                   ●→ SET Cmb_CaptureHandle
              ▶→ Delay(Duration=3.0)
              ▶→ Finish Combo Capture(
                   Capture Handle=Get Cmb_CaptureHandle,
                   Combo ID="TestThumb") ●→ bOK
              ▶→ SET Cmb_CaptureHandle (= None)
              ▶→ Print String("G0R Capture = " + bOK)
                   [Development Only]
```

Event End Play (R4 — dọn nếu tắt PIE giữa lúc Delay):
```
▶→ Branch(IsValid(Cmb_CaptureHandle))
     True ▶→ Destroy Actor(Target=Get Cmb_CaptureHandle)
           ▶→ SET Cmb_CaptureHandle (= None)
```

Q8: Keyboard Event, latent Delay hợp lệ (nằm trong Event, không Function) | IsValid: guard handle đầu chain (chặn double-trigger) + Finish tự guard nội bộ + EndPlay guard | L2: nhánh True của guard đầu là dead-end chấp nhận được (pattern nuốt lệnh khi đang bận) — còn lại mọi nhánh merge về Print | Latent nằm trong Event, không Function | 6A: Finish tự dọn actor+RT kể cả đọc fail; EndPlay dọn nếu tắt PIE giữa Delay.

> Full context kiến trúc (BeginComboCapture/FinishComboCapture, đổi từ one-shot): xem `DEVIATIONS.md` [ARCH] 14/07/2026 + `01_Session_State.md` mục P1.

---

## BP_ComboManager — Gate D prerequisite: Lighting Channels isolation (18/07/2026)

Diff trên các function đã có (full flow sống trong `BP_ComboManager.md` — file đó hiện CHƯA
đồng bộ với các diff Gate B/C/D, xem ghi chú cuối các lần phân phối P2 trước). Bối cảnh đầy đủ
(root cause Distance Field self-occlusion, quyết định không đụng
`Alpha_BP_Master_LightManager_EV` của đồng nghiệp, 2 ceiling packaged-build): xem `DEVIATIONS.md`
mục "P2 — 18/07/2026 — Gate D prerequisite: lighting isolation".

### SpawnStudioLight — sửa offset value + thêm Lighting Channels
```
RotateAngleAxis(InVect=(1500.0, 0.0, 1200.0), Axis=(0,0,1))
  ← SỬA: doc trước ghi nhầm Z=1500, giá trị THẬT xác nhận qua export K2Node = Z=1200
...(giữ nguyên từ Gate C: WorldLoc = Anchor + LightOffset, Mobility=Movable,
    FindLookAtRotation về anchor, Source Width/Height=150, Attenuation Radius=8000)...
▶→ Set Lighting Channels(Target=Light Component, Channel1=True)   ← MỚI, cuối chuỗi function
```

### Spawn dome (BeginPlay) — thêm Movable + Lighting Channels + đổi mesh
⚠️ Vị trí graph chính xác CHƯA export đầy đủ (phiên 18/07 chỉ có screenshot node rời) — cần
cuhoang xác nhận lại tên hàm/node thật trước khi coi đoạn dưới là chuẩn:
```
Set Static Mesh(New Mesh = SM_StudioDome)   ← ĐỔI, trước là /Engine/BasicShapes/Sphere
Set Cast Shadow=True                          (giữ nguyên, Gate C)
▶→ Set Mobility(Movable)                     ← MỚI (bắt buộc để Lighting Channels hoạt động)
▶→ Set Lighting Channels(Target=Static Mesh Component, Channel1=True)   ← MỚI
```

### SpawnComboForThumbnail — thêm Lighting Channels cho furniture clone
```
...Array_RemoveItem(Tags,"FurnitureSpawned") → Set GroupID=""...
▶→ NewActor → Get FurnitureMesh
     (biến riêng BP_FurnitureActor — KHÔNG dùng Get Static Mesh Component, trả rỗng)
▶→ Set Lighting Channels(Target=Primitive Component, Channel1=True)   ← MỚI
▶→ Array_Add(Cmb_StudioClones, NewActor)   (giữ nguyên vị trí cũ)
```

### BeginComboCapture — thêm Set Show Flag Settings (SkyLighting=False)
```
Branch(IsValid(Cmb_CaptureHandle))
  True ▶→ Cmb_CaptureHandle → Get Capture Component 2D                       ← MỚI
          ▶→ Make Engine Show Flags Setting(ShowFlagName="SkyLighting",
               Enabled=False) → Make Array (1 phần tử)
          ▶→ Set Show Flag Settings(Target=Capture Component 2D vừa lấy)     ← MỚI
          ▶→ Delay(3.0)   (giữ nguyên vị trí — chuỗi cũ tiếp tục sau đây)
```

Q8: 5 node mới ở trên đều CHỜ XÁC NHẬN (`Set Lighting Channels` ×2 Target khác nhau,
`Get Capture Component 2D`, `Set Show Flag Settings`, `Make Engine Show Flags Setting`) — xem
`AI_Implementation_Rules.md` mục "Nodes chờ xác nhận" trước khi coi là chuẩn chính thức.

---

## BP_ComboManager — P2 Gate D: Noise + Aliasing Fix (19/07/2026)

⚠️ Mô tả theo hướng dẫn session, cuhoang xác nhận test PASS — CHƯA có export K2Node để đối
chiếu node-by-node. **Ghi đè lên mô tả `BeginComboCapture` phía trên (18/07):** dòng
"`Delay(3.0)` → chuỗi cũ tiếp tục sau đây" (ý nói `FinishComboCapture` gọi thẳng sau Delay) nay
KHÔNG còn đúng — `FinishComboCapture` tách khỏi `Delay`, nối lại ở cuối Event Tick mới bên dưới.
Full context (7 giả thuyết đã loại, root cause SceneCapture2D không temporal thật): xem
`DEVIATIONS.md` mục "SPRINT 5 — 19/07/2026 — P2 Noise + Aliasing Fix".

Biến mới: `Cmb_AccumFramesLeft` (Integer, default 0), `Cmb_AccumTargetFrames` (Integer,
default 24, tunable Class Defaults).

### Sửa chuỗi sau Delay(3.0) warmup
```
Delay(3.0) hoàn tất
▶→ ResetComboAccumulation(Cmb_CaptureHandle)
▶→ SET Cmb_AccumFramesLeft = Cmb_AccumTargetFrames
▶→ Set Actor Tick Enabled(Target=self, bEnabled=true)
```

### Event Tick (self) — mới
```
Event Tick
▶→ Branch(Cmb_AccumFramesLeft <= 0)
     True  ▶→ dead-end (không accumulate → không làm gì, rẻ)
     False ▶→ AccumulateComboFrame(Cmb_CaptureHandle)
           ▶→ SET Cmb_AccumFramesLeft = Cmb_AccumFramesLeft - 1
           ▶→ Branch(Cmb_AccumFramesLeft <= 0)
                True  ▶→ Set Actor Tick Enabled(self, false)
                      ▶→ FinishComboCapture(Cmb_CaptureHandle, ComboID, ComboActors)
                False ▶→ dead-end (chờ frame sau)
```

### Event End Play — mở rộng bắt buộc
```
▶→ Set Actor Tick Enabled(self, false)
▶→ ResetComboAccumulation(Cmb_CaptureHandle)
```
Không thêm = leak buffer C++ nếu PIE tắt giữa lúc accumulate — cùng loại bug với
`Bugs/Bug_GPU_VRAM_Crash.md`, lần này RAM chứ không VRAM.

Q8: Event Tick (self) — không phải Custom Event/Function nên dead-end tính khác | IsValid:
`AccumulateComboFrame`/`ResetComboAccumulation` tự IsValid(CaptureHandle) trong C++ | L2:
dead-end nhánh "chưa đủ frame" HỢP LỆ — giống Sequence.Then, Tick tự gọi lại mỗi frame |
No Latent ✓ | 6A: EndPlay đã mở rộng ✓ | `Set Actor Tick Enabled` CHỜ XÁC NHẬN — xem
`AI_Implementation_Rules.md` mục "Nodes chờ xác nhận".

Test: noise (temporal N=24) ✅ CONFIRM. Aliasing/SSAA ✅ CONFIRM DONE (cuhoang tự chạy lại
checklist test đầy đủ).

---

## NODE FLOW ĐÃ CONFIRM

| Node display name | Ghi chú |
|---|---|
| `ComputeSelectionUnits` | Function trong BP_FurnitureInputManager (custom) |
| `GetSelectionUnitLabel` | Function trong BP_FurnitureInputManager (custom) |
| `SET [VariableName]` (trên object khác) | Target = object ref, Value = data → SET variable của đối tượng đó |

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|-----------|------|----------|
| 1.0 | 18/05/2026 — 08:55 ICT | Tạo mới — full node flow WBP_FurnitureInventory, BP_UndoManager, C++ |
| 1.1 | 20/05/2026 — 15:30 ICT | Fix RestoreSnapshot broadcast: RestoredBPActor single point |
| 1.2 | 20/05/2026 — 16:00 ICT | Fix #7 SwitchInventoryMode: FilterBySearch khi switch về Furniture mode |
| 1.3 | 07/06/2026 — 22:40 ICT | **Sprint 2:** Box Select flows (Mouse Pressed defer, Tick, OnLMBReleased, FinishBoxSelect); ghi fix CLEAR TempSelectedIndices đầu CaptureSnapshot; đánh dấu flow cũ là v1.1 single |
| 1.4 | 12/06/2026 — 15:04 ICT | **Sprint 3 group final + Sprint 4 đầy đủ:** Sprint 3 flows (GenerateGroupID, GetGroupChildren, FindGroupData, CreateGroup, SyncGroupsToContainer, Snapshot v3). Sprint 4: 7 helpers, GetEditBreadcrumb, Enter/Exit edit, TryEnterEdit, WBP_MeshControls T5, CreateGroup nested T6, PruneEmptyGroups + UngroupActors peel-one-level T7, ValidateEditMode T8, Replace GroupID fix, LƯU Ý quan trọng. |
| 1.5 | 15/06/2026 — 20:30 ICT | **Sprint 4 Bug Fix Learnings:** L-NEW-1 (Branch dead-end Sequence vs Event), L-NEW-2 (output pins + Temp buffer), L-NEW-3 (ComputeSelectionUnits trước guard), L-NEW-4 (Blueprint export text debug), L-NEW-5 (EditModeStack runtime → snapshot), L-NEW-6 (ValidateEditMode restore order). NODE FLOW ĐÃ CONFIRM table. |
| 1.6 | 04/07/2026 — 22:10 ICT | **NF — New Folder (context menu, dưới §C5.0 combo):** node flow GetChildFolderNames, GetUniqueNewFolderName, GetNewFolderParent, OnRequestNewFolder, CB_CreateNewFolder + ghi chú OnComboTreeNodeRightClicked thêm menu item đầu chuỗi. Full doc: WBP_FurnitureInventory.md v3.6. |
| 1.7 | 06/07/2026 — 21:15 ICT | **NF.G3 (nút "+")** node flow: PopulateComboTreeColumn +PlusNode, OnComboTreeNodeClicked +guard đầu tiên. **RebuildChipRowForPath + RefreshChipBreadcrumb** node flow (gộp code ChipRow trùng lặp + tự vẽ lại chip breadcrumb sau Move/Xóa/Rename folder) + tóm tắt 3 bug fix (dead-end 2/3 nhánh, delimiter sai, BooleanAND→OR). Full doc: WBP_FurnitureInventory.md v3.7. |
| 1.8 | 14/07/2026 | **BP_ComboManager — Debug capture thumbnail (phím T)**, P1 Gate G0-R: BeginPlay (Enable Input theo `bDebugTestThumb`), Keyboard Event T (guard double-trigger qua `Cmb_CaptureHandle` → `BeginComboCapture` → `Delay(3.0)` → `FinishComboCapture` → Print debug), Event End Play (R4, dọn actor nếu tắt PIE giữa Delay). Xem `DEVIATIONS.md` [ARCH] 14/07/2026 cho bối cảnh kiến trúc Begin/Finish. |
| 1.9 | 18/07/2026 | **BP_ComboManager — Gate D prerequisite: Lighting Channels isolation.** `SpawnStudioLight`: sửa offset value (Z=1200, không phải 1500) + thêm `Set Lighting Channels` (Target=Light Component). Spawn dome: thêm `Set Mobility(Movable)` + `Set Lighting Channels` (Target=Static Mesh Component) + đổi mesh sang `SM_StudioDome` (⚠️ vị trí graph chưa export đầy đủ, cần cuhoang xác nhận). `SpawnComboForThumbnail`: thêm `Set Lighting Channels` (Target=Primitive Component) trên `FurnitureMesh` clone. `BeginComboCapture`: thêm `Get Capture Component 2D` → `Set Show Flag Settings(SkyLighting=False)` trước Delay warmup. 5 node mới đều chờ xác nhận — xem `AI_Implementation_Rules.md`. Bối cảnh đầy đủ: `DEVIATIONS.md` 18/07/2026. |
| 1.10 | 19/07/2026 | **BP_ComboManager — Gate D: Noise + Aliasing Fix.** Class var mới `Cmb_AccumFramesLeft`/`Cmb_AccumTargetFrames` (default 24). `FinishComboCapture` tách khỏi `Delay(3.0)` — nối lại cuối Event Tick mới (mượn Tick cho temporal accumulation: `AccumulateComboFrame` mỗi frame + `Set Actor Tick Enabled` bật/tắt, node chờ xác nhận). Event End Play mở rộng: `Set Actor Tick Enabled(false)` + `ResetComboAccumulation`. ⚠️ Chưa có export K2Node đối chiếu — mô tả theo hướng dẫn session, cuhoang xác nhận test PASS (noise CONFIRM, aliasing/SSAA CONFIRM DONE). Ghi đè mô tả "Delay→chuỗi cũ" ở entry 1.9. Bối cảnh đầy đủ: `DEVIATIONS.md` 19/07/2026, `Data/ComboSerializer_Reference.md`. |
