# BP_FurnitureInputManager
**Phiên bản:** 1.7 (BẢN HỢP NHẤT — merge v1.6 + patch v1.7) | **Cập nhật:** 11/06/2026 | Actor riêng — input hub + multi-select + box-select + context-menu + group + edit mode hub

> **v1.7 (Sprint 4 T1-T5 — Edit Mode Slice 1):** thêm `EditModeStack`, dispatcher `OnEditModeChanged`, 7 helper (GetCurrentEditScope, GetChildGroups, GetGroupRoot, WalkUpUntilParent, GetAllDescendantActors đệ quy, GetGroupsInHierarchy đệ quy, ResolveSelectionUnit), GetEditBreadcrumb, 2 stub visual, EnterEditMode/ExitEditModeOneLevel/ExitEditModeFull/TryEnterEditFromSelection. `ExpandSelectionWithGroups` viết lại dùng ResolveSelectionUnit.
> **v1.6 (Sprint 3 Group + Refactor dispatcher):** hệ Group + HỢP NHẤT DISPATCHER (xóa OnMeshSelected/OnMeshDeselected, `OnSelectionChanged` duy nhất). Xóa MeshToReplace single.
> **⚠ CHƯA CÓ trong bản này (Sprint 4 T6-T8 đang chờ):** CreateGroup nested (set ParentGroupID), UngroupActors deep-tree, PruneEmptyGroups theo GetAllDescendantActors, ValidateEditMode. Xem `Sprint4_Execution_Opus.md` — merge vào đây khi T6-T8 PASS.

---

## Mục đích
Tách toàn bộ logic input furniture khỏi BP_FoffPlayerController (shared code). Chỉ cần spawn actor này vào level là hệ thống hoạt động — không đụng shared code.

---

## Variables

### Core (v1.2 → v1.6)
```
SelectedFurnitureActor : BP_FurnitureActor   ← single-select cũ, giữ đến S7.T9
CurrentMeshControls    : WBP_MeshControls
GizmoControllerRef     : BP_GizmoController
TransformerPawnRef     : BP_TransformerPawn
ActiveMode             : E_ActiveMode
LocalWasGizmoActive    : Boolean
DetailPopupRef         : WBP_DetailPopup
bIsReplaceMode         : Boolean
MeshesToReplace        : Array of BP_FurnitureActor   ← v1.6: thay MeshToReplace single (ĐÃ XÓA). CLEAR ở End Play
```

### Group (v1.6 — Sprint 3)
```
Groups   : Array of S_GroupData   ← nguồn sự thật in-memory (KHÔNG SaveGame; CLEAR ở End Play)
                                    BP_GroupsContainer giữ bản SaveGame, sync qua SyncGroupsToContainer
FoundIdx : Integer (default -1)   ← dùng trong UngroupActors; PHẢI SET -1 đầu hàm (class var không tự reset)
```

### Edit Mode (v1.7 — Sprint 4)
```
EditModeStack : Array<String>   ← stack GroupID đang edit. Rỗng = không edit. KHÔNG SaveGame. CLEAR ở End Play.
```

### Nudge (v1.2 — B1)
```
NudgeSnapshotTimerHandle : Timer Handle   ← debounce CaptureSnapshot 0.5s
NudgeSpeed               : Float (=150.0) ← cm/s, free mode (SnapStep=0)
```

### Multi-Select (v1.4 — Sprint 1 T1)
```
SelectedActors       : Array of BP_FurnitureActor
PrimarySelectedActor : BP_FurnitureActor            ← đồ chọn cuối (stencil 255)
GizmoPivotActor      : BP_PivotActor                ← pivot vô hình cho multi-gizmo
LastPivotTransform   : Transform
ClipboardActors      : Array of S_ClipboardEntry    ← clipboard multi
```

### Box Select (v1.5 — Sprint 2)
```
BoxSelectOverlayRef : WBP_BoxSelectOverlay   ← tạo ở BeginPlay
BoxStartPos         : Vector2D               ← vị trí chuột lúc bấm (logical/viewport coords)
bIsPendingBoxSelect : Boolean                ← đã bấm, chưa biết click hay kéo (chờ vượt 5px)
bIsBoxSelecting     : Boolean                ← đang kéo khung
bLMBHeld            : Boolean                ← cờ thủ công (True ở Mouse Left Pressed, False ở OnLMBReleased)
PendingClickActor   : BP_FurnitureActor      ← đồ bị bấm (defer select tới lúc thả)
```

### Context Menu (v1.5)
```
ContextMenuRef : WBP_ContextMenu   ← tạo on-demand
```

### Clipboard cũ (v1.2) — GIỮ tạm, bỏ ở S7.T9
```
ClipboardMeshPath, ClipboardDAPath, ClipboardRotation, ClipboardScale, ClipboardMaterialOverrides
(không còn dùng — đã chuyển sang ClipboardActors)
```

---

## Event Dispatchers (v1.6 → v1.7)
```
OnSelectionChanged(Actors : Array<BP_FurnitureActor>, Primary : BP_FurnitureActor)  ← SELECTION DUY NHẤT
OnSceneChanged(AllActors : Array<BP_FurnitureActor>)        ← v1.4 T14 (Scene Manager Panel Sprint 6)
OnGroupCreated(GroupID : String)                            ← v1.6
OnGroupDestroyed(GroupID : String)                          ← v1.6
OnEditModeChanged(bActive : Boolean, GroupID : String)      ← v1.7 Sprint 4
```
> **ĐÃ XÓA (refactor 10/06):** `OnMeshSelected`, `OnMeshDeselected`. Mọi mutator selection fire `OnSelectionChanged`. Lý do: dual-dispatcher là gốc loạt regression — feature gắn lên dispatcher chết thì lặng lẽ ngừng update. Chi tiết: `Sprint3_Regression_DualDispatcher_Log.md`.

---

## ⭐⭐ TƯƠNG TÁC 3 ĐIỂM — Box Select / Single Click / Defer (đọc TRƯỚC khi sửa)

**1. Mouse Left Pressed (input event):** chỉ GHI NHẬN — KHÔNG select ngay. Ghi `BoxStartPos`, bật `bIsPendingBoxSelect`, bật `bLMBHeld`. Bấm trúng mesh → nhớ vào `PendingClickActor`. Defer toàn bộ quyết định tới lúc thả.

**2. Event Tick:** phát hiện kéo quá 5px → chuyển pending→box, vẽ khung. Tick KHÔNG select, chỉ VẼ + fallback.

**3. OnLMBReleased (input event):** chốt kết quả. Box → FinishBoxSelect. Click đơn → resolve PendingClickActor (qua group expansion). Nền → DeselectAll.

**Vì sao defer:** phân biệt click-chọn vs kéo-box-từ-trên-mesh.
**Vì sao chốt ở OnLMBReleased, KHÔNG ở Tick:** ActivateGizmo trong Tick race với Tick của RuntimeTransformer → gizmo NHÁY 1 frame. Input event chạy TRƯỚC world Tick → không nháy.
**Vì sao cờ `bLMBHeld` thay Is Input Key Down:** Is Input Key Down KHÔNG tin cậy cho mouse button khi viewport capture → khung dính sau thả.

---

## Event BeginPlay (v1.5)
```
Enable Input
SET CurrentMeshControls = None, SET SelectedFurnitureActor = None
Get All Actors Of Class(BP_TransformerPawn) → Get(0) → SET TransformerPawnRef
Create Widget(WBP_BoxSelectOverlay) → SET BoxSelectOverlayRef → Add to Viewport(Z-Order 100) → Call HideBox
```

---

## Mouse Left Pressed — FULL FLOW (v1.6)
```
Step 0 : SET bLMBHeld = True                              ← đầu tiên!
Step 0b: Set Input Mode Game And UI
Step 1 : SET LocalWasGizmoActive = GizmoControllerRef.bGizmoActive
Step 2 : GizmoController → OnMousePressed
Step 3 : Branch bIsDraggingGizmo == True → True: STOP
Step 4 : GetHitResultUnderCursorByChannel(CAMERA) → Hit Actor, ReturnValue
Step 5 : Branch ReturnValue == True:
           False (khoảng không) → Get Mouse Position on Viewport → SET BoxStartPos
                                  → SET bIsPendingBoxSelect = True → STOP
Step 6 : Branch ActorHasTag(Hit Actor, "FurnitureSpawned"):
           False (trúng tường/đồ lạ) → như Step 5 False → STOP
Step 7 : DEFER cho MỌI click trúng furniture (v1.6 — bỏ nhánh Ctrl):
           SET PendingClickActor = (HitActor as BP_FurnitureActor)
           Get Mouse Position on Viewport → SET BoxStartPos
           SET bIsPendingBoxSelect = True → STOP
```
> **v1.6 fix Ctrl+click group:** Step 7 BỎ Branch IsInputKeyDown(Left Ctrl) + ToggleActor-ngay. Nhánh Ctrl cũ toggle 1 đồ rồi STOP → không tới OnLMBReleased (nơi expand group) → Ctrl+click group không cộng dồn. Giờ MỌI click defer; phân giải single/group/Ctrl ở OnLMBReleased Then 2.

---

## Event Tick — Box Select branch (v1.5 → v1.7)
> Đặt SAU nhánh nudge free-mode, dùng Sequence.

**⚠ GUARD inventory (bug đã trả giá):** Event Tick KHÔNG bị gate bởi Input Mapping Context. Không guard → box bật cả khi inventory đóng:
```
GetGameInstance → Cast Foff_GameInstance → GET FurnitureInventoryRef
→ nested Branch (KHÔNG dùng AND node — Blueprint AND không short-circuit, crash None):
  IsValid(FurnitureInventoryRef) [ngoài] → True → Is In Viewport [trong] → True → SET bInventoryOpen=True
  (mọi nhánh khác → SET bInventoryOpen=False)
Branch bInventoryOpen:
  False → HideBox + SET bIsPendingBoxSelect=False + SET bIsBoxSelecting=False → STOP
  True  → 2 branch dưới
```
> **⚠ SPRINT D (D.T1) sẽ đổi:** `Is In Viewport` → `Get Visibility == Visible` khi inventory thành single-instance.

**Branch A — PENDING (bIsPendingBoxSelect == True):**
```
Branch bLMBHeld:
  True → khoảng cách = VectorLength((Get Mouse Position on Viewport) - BoxStartPos)
         Branch > 5.0 → True: SET bIsBoxSelecting=True, SET bIsPendingBoxSelect=False, ShowBox, UpdateBox
  False (thả trước 5px — fallback nếu OnLMBReleased lỡ) →
     SET bIsPendingBoxSelect = False
     Branch IsValid(PendingClickActor):
       True  → DeselectAll → ExpandSelectionWithGroups([PendingClickActor]) → SelectActors(kết quả)
               → CaptureSnapshot("Select") → SET PendingClickActor=None      ← v1.7: đổi từ SelectSingleActor
       False → Branch IsInputKeyDown(Left Ctrl):
                 True → (giữ selection)
                 False → DeselectAll → CaptureSnapshot("Deselect")
```

**Branch B — KÉO BOX (bIsBoxSelecting == True):**
```
Branch bLMBHeld:
  True  → UpdateBox(BoxStartPos, Get Mouse Position on Viewport)
  False (fallback) → FinishBoxSelect(...) → HideBox → SET bIsBoxSelecting=False → SET PendingClickActor=None
```

---

## OnLMBReleased — FULL FLOW (v1.6) ⭐ đường chính chốt selection
```
SET bLMBHeld = False                                   ← đầu tiên!
Sequence:
  Then 0: đóng context menu (IsValid(ContextMenuRef) → Remove from Parent → SET None)

  Then 1: Branch bIsBoxSelecting == True:
            True → Get Mouse Position on Viewport → FinishBoxSelect(EndPos)
                   → IsValid(BoxSelectOverlayRef) → HideBox
                   → SET bIsBoxSelecting = False → SET PendingClickActor = None

  Then 2: Branch bIsPendingBoxSelect == True:           ← CLICK đơn
            True → SET bIsPendingBoxSelect = False
              Branch IsValid(PendingClickActor):
                True (v1.6 — group-aware) →
                  ExpandSelectionWithGroups([PendingClickActor]) → Expanded
                  Branch IsInputKeyDown(Left Ctrl):
                    True  → ForEach Expanded → ToggleActor       ← Ctrl cộng dồn cả unit
                    False → DeselectAll → SelectActors(Expanded)
                  → CaptureSnapshot("Select") → SET PendingClickActor = None
                False → Branch IsInputKeyDown(Left Ctrl):
                          True  → (giữ selection — Ctrl+click nền không deselect)
                          False → DeselectAll → CaptureSnapshot("Deselect")
                                  → Branch bIsReplaceMode → (exit replace mode chain)
```

---

## FinishBoxSelect(EndPos : Vector2D) — Function (v1.5 → v1.6)
```
Min/Max → TopLeft, BottomRight từ BoxStartPos & EndPos
CLEAR LocalSelected
Get All Actors With Tag("FurnitureSpawned") → ForEach (Actor):
  Branch (Actor != PendingClickActor):                 ← loại mesh bắt đầu kéo box từ trên nó
    True → Cast → IsValid → Get Actor Location → Project World To Screen → ScreenPos
      ⚠ FIX DPI: chia ScreenPos cho Get Viewport Scale = ScreenPosFixed
      Branch trong khung (nested Branch, không AND node) → True: ADD Actor → LocalSelected
Completed:
  Branch LENGTH(LocalSelected) > 0:
    True → ExpandSelectionWithGroups(LocalSelected) → Expanded     ← v1.6: box cũng expand group
      Branch IsInputKeyDown(Left Ctrl):
        True  → ForEach Expanded → ToggleActor
        False → DeselectAll → SelectActors(Expanded)
      → CaptureSnapshot("BoxSelect")
```
**⚠ DPI mismatch (bug đã trả giá):** Mouse Position on Viewport = LOGICAL; Project World To Screen = PIXEL THÔ. Phải chia Viewport Scale.
**Chủ đích (không phải bug):** chọn theo PIVOT/origin của đồ, không theo bounding box.

---

## MULTI-SELECT FUNCTIONS (v1.4)

### CalculateCenter(Actors) → Vector — trung bình vị trí → tâm nhóm.

### SpawnOrUpdatePivot
```
Guard LENGTH SelectedActors < 2 → return
CalculateCenter → Center
Branch NOT IsValid(GizmoPivotActor): True → Spawn BP_PivotActor → SET GizmoPivotActor
SET Actor Location(GizmoPivotActor, Center)
SET GizmoPivotActor.AttachedActors = SelectedActors → Call RefreshOffsets
```

### DestroyPivot — IsValid → Destroy → SET None.

### DeselectAll (v1.6)
```
ForEach SelectedActors → IsValid → GET FurnitureMesh → Set Render Custom Depth = False
CLEAR SelectedActors → SET PrimarySelectedActor = None → SET SelectedFurnitureActor = None
DeactivateGizmo → DestroyPivot
Broadcast OnSelectionChanged([], None)
⚠ KHÔNG CaptureSnapshot ở đây (infinite loop) — caller tự gọi sau
```

### SelectSingleActor(Actor) (v1.6)
```
DeselectAll → ADD Actor → SET Primary → UpdateOutlineState → UpdateGizmo
→ Broadcast OnSelectionChanged(SelectedActors, Primary)
⚠ KHÔNG CaptureSnapshot nội bộ
```

### SelectActors(Actors)
```
⚠ Actors pass-by-ref → SET ActorsCopy = Actors trước
ForEach ActorsCopy → Contains(SelectedActors, Actor) → NOT → True: ADD
Completed: Branch LENGTH > 0 → SET Primary = Last → SET SelectedFurnitureActor
  → UpdateOutlineState → UpdateGizmo → Broadcast OnSelectionChanged
⚠ Chỉ ADD không clear → caller phải DeselectAll trước
```

### ToggleActor(Actor)
```
Branch Contains(SelectedActors, Actor):
  True  → Remove → Set Render Custom Depth = False (clear stencil đồ bị remove)
  False → ADD
SET Primary → UpdateOutlineState → UpdateGizmo → Broadcast OnSelectionChanged
⚠ KHÔNG CaptureSnapshot nội bộ — caller gọi sau
```

### UpdateOutlineState
```
ForEach SelectedActors → IsValid → GET FurnitureMesh → Set Render Custom Depth=True
  Branch Actor == PrimarySelectedActor: True → Stencil 255 / False → Stencil 254
```

### UpdateGizmo
```
GET LENGTH SelectedActors:
  == 0 → DeactivateGizmo + DestroyPivot
  == 1 → DestroyPivot → ActivateGizmo(SelectedActors[0])
  >= 2 → DeactivateGizmo (TRƯỚC!) → SpawnOrUpdatePivot → ActivateGizmo(GizmoPivotActor)
         → SetActorTickEnabled(GizmoPivotActor, True)
```

---

## GROUP FUNCTIONS (v1.6 — Sprint 3)

### GenerateGroupID() → String — `New Guid → To String → "g_" prefix`.

### GetGroupChildren(InGroupID) → Array<BP_FurnitureActor>
```
CLEAR Children (đầu hàm)
Get All Actors With Tag("FurnitureSpawned") → ForEach:
  Cast → IsValid → Branch (GroupID == InGroupID): True → ADD
Return Children
```

### FindGroupData(InGroupID) → (S_GroupData, Index, bFound)
ForEach Groups → Break → so GroupID → match: trả data + index + true.

### CreateGroup() — Ctrl+G
```
Guard SelectedActors.Length >= 2
GenerateGroupID → NewGID | Auto-name = "Nhóm " + (Groups.Length + 1)
Make S_GroupData(NewGID, name, ParentGroupID="", bIsLocked=false) → ADD Groups
SyncGroupsToContainer
ForEach SelectedActors → Cast → SET GroupID = NewGID
CaptureSnapshot("CreateGroup") → Broadcast OnGroupCreated(NewGID)
SelectActors(SelectedActors)   ← re-fire OnSelectionChanged (info bar)
```
> ⚠ T6 (chưa làm) sẽ sửa: ParentGroupID = GetCurrentEditScope() khi tạo trong edit mode (nested).

### UngroupActors(InGroupID) — Ctrl+Shift+G (bản FLAT v1.6)
```
SET FoundIdx = -1                              ← reset class var ĐẦU hàm
Branch (InGroupID == "") → True: Return
GetGroupChildren(InGroupID) → ForEach1 (child):
   Loop Body → Cast → SET child.GroupID = ""
ForEach1 Completed →                            ← find/remove/capture Ở COMPLETED, KHÔNG Loop Body
   ForEach2 (Groups, Index) → Break → so GroupID == InGroupID → SET FoundIdx = Index
   ForEach2 Completed →
     Branch (FoundIdx >= 0) → True: REMOVE INDEX(Groups, FoundIdx)
     → SyncGroupsToContainer → CaptureSnapshot("Ungroup")
     → SelectActors(SelectedActors) → Broadcast OnGroupDestroyed(InGroupID)
```
**⚠ 2 bug đã trả giá:** (1) chuỗi find/remove/capture trong Loop Body → chạy N lần (spam snapshot) — PHẢI ở Completed. (2) FoundIdx class var → SET -1 đầu hàm mỗi lần gọi.
> ⚠ T7 (chưa làm) sẽ thay bằng deep ungroup cả cây (GetGroupRoot + descendants + hierarchy) — xem Sprint4_Execution_Opus.md mục 7.

### SyncGroupsToContainer() — Get All Actors(BP_GroupsContainer)[0] → IsValid → SET Container.Groups = self.Groups.

### PruneEmptyGroups() — quét Groups, GetGroupChildren.Length==0 → loại. Gọi trong DeleteSelected.
> ⚠ T7 sẽ đổi tiêu chí keep = GetAllDescendantActors(g).Length > 0 (chống prune oan group cha nested).

---

## EDIT MODE (v1.7 — Sprint 4 T1-T4)

### GetCurrentEditScope() → String (Pure được)
```
Branch(EditModeStack.Length > 0):
  True  → EditModeStack → Last Index → GET → Return
  False → Return ""
```

### GetChildGroups(InGroupID : String) → Array<S_GroupData>
```
CLEAR LocalChildren
ForEach Groups (g): Branch(g.ParentGroupID == InGroupID): True → ADD g
Completed → Return LocalChildren
```

### GetGroupRoot(InGroupID : String) → String — leo ngược tới gốc, depth guard 10
```
SET Current = InGroupID
ForLoop(0..9):
  FindGroupData(Current) → (data, _, bFound)
  bFound==False → Return Current
  data.ParentGroupID=="" → Return Current
  Else → SET Current = data.ParentGroupID
Completed → Return Current
```

### WalkUpUntilParent(InGroupID, TargetParent) → String — tìm con trực tiếp của TargetParent trên đường leo
```
SET Current = InGroupID
ForLoop(0..9):
  FindGroupData(Current) → (data, _, bFound)
  bFound==False → Return ""
  data.ParentGroupID==TargetParent → Return Current
  data.ParentGroupID=="" → Return ""
  Else → SET Current = data.ParentGroupID
Completed → Return ""
```

### GetAllDescendantActors(InGroupID) → Array<BP_FurnitureActor> ⭐ ĐỆ QUY
```
CLEAR LocalResult
GetGroupChildren(InGroupID) → ForEach_1: ADD Element → LocalResult
  Completed → GetChildGroups(InGroupID) → ForEach_2 (cg):
    GetAllDescendantActors(cg.GroupID) → ForEach_3: ADD Element → LocalResult
    Completed → (để trống)
  Completed → Return LocalResult
```
⚠ Local var độc lập mỗi stack frame (verified). Fallback iterative nếu cần.

### GetGroupsInHierarchy(InGroupID) → Array<S_GroupData> ⭐ ĐỆ QUY (bridge Combo S5)
```
CLEAR LocalGroups
FindGroupData(InGroupID) → bFound True: ADD data
(merge) → GetChildGroups(InGroupID) → ForEach_1 (cg):
  GetGroupsInHierarchy(cg.GroupID) → ForEach_2: ADD Element
  Completed → (để trống)
Completed → Return LocalGroups
```

### ResolveSelectionUnit(Actor, EditScope : String) → Array<BP_FurnitureActor> ⭐ NÃO Sprint 4
**THỨ TỰ NHÁNH BẮT BUỘC (Q9a: edit-scope TRƯỚC đồ-loose):**
```
IsValid(Actor)==False → Return []
Cast → GET GroupID → gid
Branch(EditScope != ""):                         ← ĐANG EDIT
  True →
    gid==EditScope → Return [Actor]              ← member trực tiếp → cá nhân
    gid==""        → Return []                   ← đồ rời ngoài scope → bỏ qua
    WalkUpUntilParent(gid, EditScope) → ancestor
    ancestor!="" → Return GetAllDescendantActors(ancestor)   ← sub-group → cả sub
    ancestor=="" → Return []
  False →                                        ← KHÔNG EDIT
    gid=="" → Return [Actor]
    GetGroupRoot(gid) → root → Return GetAllDescendantActors(root)
```

### ExpandSelectionWithGroups(RawActors) — VIẾT LẠI v1.7 (thay logic inline Sprint 3)
```
SET ActorsCopy = RawActors; CLEAR LocalResult
GetCurrentEditScope() → Scope
ForEach ActorsCopy (Actor):
  ResolveSelectionUnit(Actor, Scope) → ForEach_inner (Unit):
    NOT Contains(LocalResult, Unit) → ADD Unit
Completed → Return LocalResult
```
Dùng ở: OnLMBReleased Then 2, FinishBoxSelect, Tick Branch A fallback.

### EnterEditMode(InGroupID)
```
InGroupID=="" → Return
FindGroupData → bFound==False → Return
ADD InGroupID → EditModeStack
DeselectAll → ApplyEditModeVisual
Broadcast OnEditModeChanged(True, InGroupID)
```

### ExitEditModeOneLevel()
```
EditModeStack.Length==0 → Return
GetCurrentEditScope() → SET Exited
EditModeStack → Last Index → REMOVE INDEX (POP)
Branch(EditModeStack.Length==0):
  True  → RemoveEditModeVisual → DeselectAll
          GetAllDescendantActors(Exited) → LocalTree
          LocalTree.Length>0 → SelectActors(LocalTree)
          Broadcast OnEditModeChanged(False, "")
  False → ApplyEditModeVisual → DeselectAll
          GetAllDescendantActors(Exited) → LocalTree
          LocalTree.Length>0 → SelectActors(LocalTree)
          GetCurrentEditScope() → NewScope
          Broadcast OnEditModeChanged(True, NewScope)
```
> DeselectAll TRƯỚC SelectActors. GetAllDescendantActors (KHÔNG GetGroupChildren) — chống fail nested thuần.

### ExitEditModeFull()
```
EditModeStack.Length==0 → Return
EditModeStack → GET[0] → SET RootScope
CLEAR EditModeStack → RemoveEditModeVisual → DeselectAll
GetAllDescendantActors(RootScope) → LocalTree
LocalTree.Length>0 → SelectActors(LocalTree)
Broadcast OnEditModeChanged(False, "")
```

### TryEnterEditFromSelection()
```
IsValid(PrimarySelectedActor)==False → Return
Cast → GET GroupID → gid; gid=="" → Return
EditModeStack.Length>=3 → Return   ← giới hạn 3 cấp
GetCurrentEditScope() → Scope
Scope=="" → EnterEditMode(GetGroupRoot(gid))
Else → WalkUpUntilParent(gid, Scope) → Sub
  Sub!="" → EnterEditMode(Sub)
  Sub=="" → Return (member trực tiếp hoặc ngoài scope → no-op)
```

### GetEditBreadcrumb() → String
```
SET Result = ""
ForEach EditModeStack (Element, ArrayIndex):
  FindGroupData(Element) → bFound:
    False → Return Result (early exit)
    True  → ArrayIndex==0: SET Result = GroupName / Else: Append(Result, "›", GroupName)
Completed → Return Result
```

### ApplyEditModeVisual() / RemoveEditModeVisual() — STUB RỖNG (T9 đổ body, Stencil 200 reserved)

---

## CONTEXT MENU (v1.5 — Sprint 2)
**Widget:** WBP_ContextMenu + WBP_ContextMenuItem + WBP_MenuSeparator.

### Right-click handler
```
Phát hiện right-click: time-based + check camera xoay/pan
→ click thật: IsValid(ContextMenuRef) → Remove cũ → SET None
   Create Widget(WBP_ContextMenu) → SET ref → Add to Viewport → Set Position In Viewport(chuột) → Bind callbacks
```
> Menu đóng bằng background button + OnLMBReleased Then 0.

### Callbacks
```
CB_Copy → CopyMesh | CB_Duplicate → DuplicateMesh | CB_Paste → PasteMesh
CB_ResetRotation → ResetRotation | CB_SelectSimilar → SelectSimilarMesh | CB_Delete → DeleteSelected
CB_Undo/CB_Redo → UndoManager | CB_ChangeMaterial → OpenMaterialModeForActor (S2.T9)
CB_Replace → StartReplaceMode multi (S2.T9)
```

### SelectSimilarMesh
```
Guard IsValid(PrimarySelectedActor) → GET MeshPath → TargetPath
DeselectAll → Get All Actors With Tag("FurnitureSpawned") → ForEach:
  Cast → IsValid → Branch (MeshPath == TargetPath) → True: ADD LocalSimilar   ← so STRING, KHÔNG load DA
Completed → SelectActors(LocalSimilar) → CaptureSnapshot("SelectSimilar")
```

### ResetRotation — ForEach SelectedActors → IsValid → Set Actor Rotation(0,0,0) → CaptureSnapshot("ResetRotation").

### DeleteSelected
```
ForEach SelectedActors → IsValid → Destroy Actor(Actor)   ← target = Array Element, KHÔNG để trống (= destroy self!)
Completed → DeselectAll → PruneEmptyGroups (v1.6) → CaptureSnapshot("Delete")
```

---

## Keyboard Manipulation (v1.2 UX Phase 2.1, multi từ v1.4)

### B1 — Nudge (chi tiết: Blueprint_Logic.md / B1_Nudge_Flow)
- `NudgeMesh(Direction)` — guard SelectedActors rỗng; direction từ Primary.PlacementSurfaceType; ForEach SelectedActors → Add Actor World Offset; sau ForEach: CalculateCenter → SetActorLocation(Pivot) → RefreshOffsets. Debounce snapshot 0.5s.
- Tick free mode (SnapStep==0): ForEach × DeltaTime × NudgeSpeed → cập nhật Pivot.

### B2 — Copy/Paste/Duplicate
- `CopyMesh` — CLEAR ClipboardActors → CalculateCenter → ForEach build S_ClipboardEntry (RelativeLocation = ActorLoc - Center).
- `PasteMesh` — trace surface → DeselectAll → CLEAR LocalSpawned → ForEach ClipboardActors spawn (bAutoSelect=False) → SelectActors(LocalSpawned) → CaptureSnapshot.
- `DuplicateMesh` — CopyMesh → tính MaxRightEdge (**spawn nối COMPLETED, KHÔNG Loop Body** — bug đã trả giá) → spawn như Paste.
- `SpawnFurnitureCopy(MeshPath, DAPath, Location, Rotation, Scale, MaterialOverrides, SurfaceType, bAutoSelect) → NewActor` — v1.6: tail dùng `DeselectMesh → SelectActors(Make Array(NewActor))` thay select thủ công. Return ở CẢ True/False branch.
  > ⚠ GATE 1 (G1.T2) sẽ làm hàm này thành ĐƯỜNG SPAWN DUY NHẤT (RestoreSnapshot gọi nó). SPRINT D (D.T8) thêm param RowName.

---

## Event End Play (chống VRAM leak) — v1.7
```
IsValid(CurrentMeshControls) → Remove from Parent
IsValid(SelectedFurnitureActor) → Set Render Custom Depth = False
ForEach SelectedActors → IsValid → Set Render Custom Depth = False
CLEAR SelectedActors | SET PrimarySelectedActor = None, GizmoPivotActor = None
IsValid(BoxSelectOverlayRef) → Remove from Parent → SET None
IsValid(ContextMenuRef) → Remove from Parent → SET None
SET PendingClickActor = None
CLEAR Groups | CLEAR MeshesToReplace
CLEAR EditModeStack                                    ← v1.7
```

---

## DeselectMesh (Function — single, legacy)
```
Cast SelectedFurnitureActor → GET FurnitureMesh → Set Render Custom Depth = False
SET SelectedFurnitureActor = None → DeactivateGizmo
⚠ KHÔNG CaptureSnapshot. Chỉ còn được Call trong SpawnFurnitureCopy.
```

---

## Cách BP khác lấy reference
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
```
⚠ KHÔNG dùng Get Player Controller → Cast BP_FoffPlayerController. Chỉ 1 instance (verified 07/06).

## Level Blueprint — Spawn Order
```
1. BP_UndoManager  2. BP_FurnitureSceneManager  3. BP_TransformerPawn
4. BP_GizmoController  5. BP_FurnitureInputManager (SET GizmoControllerRef)
6. WBP_MeshControls (SET CurrentMeshControls)  7. CaptureSnapshot("Initial")
```

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0-1.3 | 21/04→22/05/2026 | Gốc → Dispatchers → UX 2.1 (Nudge, Copy/Paste) → SurfaceType |
| 1.4 | 04/06/2026 | Multi-Select Sprint 1 T1-T14 |
| 1.5 | 07/06/2026 | Sprint 2: Box Select (defer, bLMBHeld, DPI fix, guard inventory) + Context Menu |
| 1.6 | 10/06/2026 | Sprint 3: Group + hợp nhất dispatcher (OnSelectionChanged duy nhất) + MeshesToReplace |
| 1.7 | 11/06/2026 | Sprint 4 T1-T5: EditModeStack, OnEditModeChanged, 7 helper, ResolveSelectionUnit, Enter/Exit edit, breadcrumb, 2 stub. ExpandSelectionWithGroups viết lại. **BẢN HỢP NHẤT** — đã merge patch, file patch có thể xóa. |
