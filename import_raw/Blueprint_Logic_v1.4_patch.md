# Blueprint Logic — Node Flow Reference — PATCH v1.4
**Phiên bản:** 1.4 | **Cập nhật:** 12/06/2026 — 15:04 ICT
**Patch từ v1.3 (07/06) → v1.4. Ghi node flow kể từ Sprint 3 (group, bản final sau regression) + toàn bộ Sprint 4 (Edit Mode + Nested).**
> File này bổ sung node flow MỚI. Phần Sprint 1-2 trong v1.3 giữ nguyên.

---

# ═══════════════ SPRINT 3 — GROUP (bản FINAL sau regression 10/06) ═══════════════

## ExpandSelectionWithGroups(InActors) — ⚠ ĐÃ VIẾT LẠI ở Sprint 4 T2
> Bản Sprint 3 (inline GetGroupChildren) đã bị thay bởi bản dùng ResolveSelectionUnit.
> Xem phần Sprint 4 T2 phía dưới cho flow hiện hành.

## GenerateGroupID() → String
`New Guid → To String → Append "g_" prefix` → "g_<GUID>".

## GetGroupChildren(InGroupID) → Array<BP_FurnitureActor>
```
CLEAR Children (đầu hàm)
Get All Actors With Tag("FurnitureSpawned") → ForEach:
  Cast → IsValid → Branch (GroupID == InGroupID): True → ADD to Children
  (Cast Failed KHÔNG nối Return)
Return Children
```

## FindGroupData(InGroupID) → (S_GroupData, Index, bFound)
ForEach Groups → Break → so GroupID → match: trả data + index + true.
> ⚠ KHÔNG có output Index ở 1 số call site Sprint 4 — đọc lại: FindGroupData TRẢ Index. Nhưng node "Find Group Data" trong vài chỗ chỉ expose (GroupData, Found). Khi cần Index dùng rebuild pattern thay Set Array Elem.

## CreateGroup() — Ctrl+G (⚠ T6 sửa ParentGroupID — xem Sprint 4 T6)
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

## SyncGroupsToContainer()
Get All Actors Of Class(BP_GroupsContainer)[0] → IsValid → SET Container.Groups = self.Groups.

## SNAPSHOT v3 (BP_UndoManager — Sprint 3, giữ nguyên Sprint 4)

### CaptureSnapshot — các điểm Sprint 3
```
Step 0  : CLEAR TempSelectedIndices (đầu hàm)
Step 0b : GetGroupsForSnapshot → SET TempGroups   ← fix impure-timing (gọi SỚM, SET temp var)
Step 1-2: build Meshes (mỗi placement)
Step 3  : mỗi placement capture GroupID = actor.GroupID
Make S_SceneSnapshot: Groups ← TempGroups (đọc temp var, KHÔNG đọc impure trực tiếp)
Version = 3
```

### RestoreSnapshot — các điểm Sprint 3 (+ Sprint 4 T8 chèn ValidateEditMode)
```
Step 1 : DeselectAll → Destroy "FurnitureSpawned" → CLEAR SpawnedActors
Step 4 : ForEach spawn actor + restore material + SET actor.GroupID = Placement.GroupID
Step 5 : Branch Version>=2 → restore SelectedMeshIndices → SelectActors(RestoredActors)
Step 5b: Branch Version>=3 → CLEAR Groups → ADD Snapshot.Groups → SyncGroupsToContainer
         ▶→ ValidateEditMode()              ← ⭐ Sprint 4 T8 — MỚI (xem Sprint 4 T8)
Step 6 : RefreshButtonState
Step 6b: Branch SelectedActors.Length > 0 → SelectActors / DeselectAll+DeactivateGizmo
Step 7 : Broadcast OnRestoreCompleted (dùng RestoredBPActor)
```

---

# ═══════════════ SPRINT 4 — EDIT MODE + NESTED GROUP ═══════════════

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

### GetChildGroups(InGroupID) → Array<S_GroupData>   (group con TRỰC TIẾP)
```
CLEAR LocalChildren
ForEach Groups (g):
  BREAK g → ParentGroupID
  Branch(g.ParentGroupID == InGroupID): True → ADD g → LocalChildren
Completed → Return LocalChildren
```

### GetGroupRoot(InGroupID) → String   (leo lên gốc, depth guard 10)
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

### WalkUpUntilParent(InGroupID, TargetParent) → String   (con trực tiếp của TargetParent trên đường lên)
```
SET Current = InGroupID
ForLoop(0..9):
  FindGroupData(Current) → (data, bFound)
  bFound==False → Return ""
  BREAK data → ParentGroupID
  ParentGroupID==TargetParent → Return Current      ← TÌM THẤY
  ParentGroupID=="" → Return ""                     ← lên hết gốc
  Else → SET Current = ParentGroupID
Completed → Return ""
```

### GetAllDescendantActors(InGroupID) → Array<BP_FurnitureActor>   ⭐ ĐỆ QUY
```
CLEAR LocalResult
GetGroupChildren(InGroupID) → ForEach_1: ADD Element → LocalResult
  Completed → GetChildGroups(InGroupID) → ForEach_2 (cg):
    BREAK cg → GroupID
    GetAllDescendantActors(cg.GroupID) → ForEach_3: ADD Element → LocalResult
    Completed → (để trống)
  Completed → Return LocalResult
```
> ForEach_3.Completed để TRỐNG (không nối vòng về). Local var độc lập mỗi stack frame (đã verify).

### GetGroupsInHierarchy(InGroupID) → Array<S_GroupData>   ⭐ ĐỆ QUY (bridge Combo S5)
```
CLEAR LocalGroups
FindGroupData(InGroupID) → (data, bFound)
Branch(bFound): True → ADD data → LocalGroups; False → (tiếp)
(merge) → GetChildGroups(InGroupID) → ForEach_1 (cg):
  BREAK cg → GroupID
  GetGroupsInHierarchy(cg.GroupID) → ForEach_2: ADD Element → LocalGroups
  Completed → (để trống)
Completed → Return LocalGroups
```
> Branch True/False của bFound đều MERGE về GetChildGroups (không dead-end).

### ResolveSelectionUnit(Actor, EditScope) → Array<BP_FurnitureActor>   ⭐ NÃO Sprint 4
> ⚠ THỨ TỰ NHÁNH BẮT BUỘC: EditScope != "" kiểm tra TRƯỚC gid == "" (Q9a).
```
IsValid(Actor)==False → Return []
Cast → GET GroupID → gid

Branch(EditScope != ""):                       ← ĐANG EDIT (xét trước)
  True →
    Branch(gid == EditScope): True → Return Make Array(Actor)   ← member trực tiếp → cá nhân
    Branch(gid == ""):        True → Return []                  ← đồ rời ngoài scope → bỏ qua
    WalkUpUntilParent(gid, EditScope) → ancestor
    Branch(ancestor != ""):   True → Return GetAllDescendantActors(ancestor)   ← sub-group → cả sub-group
                              False → Return []                 ← ngoài scope → bỏ qua
  False →                                      ← KHÔNG EDIT
    Branch(gid == ""):        True → Return Make Array(Actor)   ← đồ rời → chính nó
    GetGroupRoot(gid) → root → Return GetAllDescendantActors(root)   ← group → cả cây từ gốc
```

### ApplyEditModeVisual() / RemoveEditModeVisual() — STUB RỖNG (chỉ Entry, T9 đổ body, Stencil 200 reserved)

---

## ─── T2: ExpandSelectionWithGroups (VIẾT LẠI) ───
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
> Tick fallback (Event Tick Branch A) đổi từ SelectSingleActor → DeselectAll + ExpandSelectionWithGroups + SelectActors (nhất quán).

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
FindGroupData(InGroupID) → (_, bFound)
Branch(bFound == False) → True: Return
ADD InGroupID → EditModeStack
DeselectAll → ApplyEditModeVisual
Broadcast OnEditModeChanged(True, InGroupID)
```

### ExitEditModeOneLevel()   (nút "↑ Lên 1 cấp")
```
Branch(EditModeStack.Length == 0) → True: Return
GetCurrentEditScope() → SET Exited
EditModeStack → Last Index → REMOVE INDEX (POP)
Branch(EditModeStack.Length == 0):
  True (thoát hẳn) →
    RemoveEditModeVisual → DeselectAll
    GetAllDescendantActors(Exited) → SET LocalTree
    Branch(LocalTree.Length > 0): True → SelectActors(LocalTree)   (merge)
    Broadcast OnEditModeChanged(False, "")
  False (còn cha) →
    ApplyEditModeVisual → DeselectAll
    GetAllDescendantActors(Exited) → SET LocalTree
    Branch(LocalTree.Length > 0): True → SelectActors(LocalTree)   (merge)
    GetCurrentEditScope() → NewScope
    Broadcast OnEditModeChanged(True, NewScope)
```

### ExitEditModeFull()   (nút "✖ Thoát")
```
Branch(EditModeStack.Length == 0) → True: Return
EditModeStack → GET[0] → SET RootScope
CLEAR EditModeStack → RemoveEditModeVisual → DeselectAll
GetAllDescendantActors(RootScope) → SET LocalTree
Branch(LocalTree.Length > 0): True → SelectActors(LocalTree)   (merge)
Broadcast OnEditModeChanged(False, "")
```

---

## ─── T4: TryEnterEditFromSelection ───
```
Branch(IsValid(PrimarySelectedActor) == False) → True: Return
Cast → GET GroupID → gid
Branch(gid == "") → True: Return                    ← đồ rời
Branch(EditModeStack.Length >= 3) → True: Return    ← giới hạn 3 cấp
GetCurrentEditScope() → Scope
Branch(Scope == ""):
  True  → EnterEditMode(GetGroupRoot(gid))          ← chưa edit → vào gốc
  False → WalkUpUntilParent(gid, Scope) → SET Sub
          Branch(Sub != ""): True → EnterEditMode(Sub)   ← vào sub-group con trực tiếp
          (Sub=="" → no-op: member trực tiếp / ngoài scope)
```

---

## ─── T5: WBP_MeshControls — Edit Mode UI ───

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
          Get All Actors Of Class(InputManager)[0] → GetEditBreadcrumb → BreadStr
          SetText(TXT_EditBreadcrumb, "✏️ Đang chỉnh: " + BreadStr)
  False → Set Visibility(HB_EditModeBar, Collapsed)
```
> False dead-end OK (chỉ hide).

### OnSelectionChangedInfoBar — thêm Sequence.Then 2 (visibility BTN_EnterEdit)
```
Then 2 ▶→ Branch(IsValid(Primary)):
  True  → Cast → GET GroupID → Branch(GroupID != ""):
            True  → Set Visibility(BTN_EnterEdit, Visible)
            False → Set Visibility(BTN_EnterEdit, Collapsed)
  False → Set Visibility(BTN_EnterEdit, Collapsed)
```
> Primary = parameter của event handler (không dùng class var).

### OnClicked
```
BTN_EnterEdit    → Get All Actors Of Class(InputManager)[0] → TryEnterEditFromSelection
BTN_ExitOneLevel → Get All Actors Of Class(InputManager)[0] → ExitEditModeOneLevel
BTN_ExitFull     → Get All Actors Of Class(InputManager)[0] → ExitEditModeFull
```

---

## ─── T6: CreateGroup nested ───
Sửa node Make S_GroupData trong CreateGroup: `ParentGroupID = GetCurrentEditScope()` (thay ""). Ngoài edit → ""; trong edit → sub-group. (Đã ghi gộp trong CreateGroup phần Sprint 3 ở trên.)

---

## ─── T7: PruneEmptyGroups + UngroupActors (peel-one-level) ───

### PruneEmptyGroups()   (đổi tiêu chí keep)
```
CLEAR LocalKeep
ForEach Groups (g):
  GetAllDescendantActors(g.GroupID) → Length        ← THAY GetGroupChildren (cả subtree)
  Branch(Length > 0): True → ADD g → LocalKeep
Completed → SET Groups = LocalKeep → SyncGroupsToContainer
```
> GetGroupChildren chỉ check direct members → prune oan group cha nested. GetAllDescendantActors xét cả cây → cascade đúng 1 pass.

### UngroupActors(InGroupID)   — PEEL-ONE-LEVEL (viết lại, thay deep-ungroup)
> Local vars: target, parentGID, scope (String); LocalNewGroups, LocalKeep (Array S_GroupData).
```
Entry ▶→ Branch(InGroupID == "") → True: Return
       ▶→ GetCurrentEditScope → SET scope
       ▶→ WalkUpUntilParent(InGroupID, scope) → SET target    ← ngoài edit = leo tới root; trong edit = sub-group đang chọn
       ▶→ Branch(target == "") → True: Return
       ▶→ FindGroupData(target) → (data, Found)
       ▶→ Branch(Found == False) → True: Return
       ▶→ BREAK data → SET parentGID = data.ParentGroupID

B1: actor con TRỰC TIẾP → về cha
       ▶→ GetGroupChildren(target) → ForEach_1(actor):
            LoopBody → Cast → SET GroupID = parentGID
            Completed →

B2: rebuild Groups — sub-group con trực tiếp đổi ParentGroupID về cha
            CLEAR LocalNewGroups
            GET Groups → ForEach_2(g):
              LoopBody → BREAK g → ParentGroupID
                         Branch(g.ParentGroupID == target):
                           True  → MAKE S_GroupData(g.GroupID, g.GroupName, parentGID, g.bIsLocked) → ADD LocalNewGroups
                           False → ADD g (gốc) → ADD LocalNewGroups
              Completed → SET Groups = LocalNewGroups

B3: xóa target khỏi Groups (rebuild bỏ target)
            CLEAR LocalKeep
            ForEach_3 Groups (g2):
              LoopBody → Branch(g2.GroupID != target): True → ADD g2 → LocalKeep
              Completed → SET Groups = LocalKeep
                        → SyncGroupsToContainer
                        → CaptureSnapshot("Ungroup")     ← 1 lần, ở Completed
                        → SelectActors(SelectedActors)
                        → Broadcast OnGroupDestroyed(target)
```
> Semantic: ungroup đúng 1 cấp. Ví dụ ungroup Group con 2-1 → 4 actor về Group con 2; sub-groups khác giữ nguyên.
> Flat group: WalkUpUntilParent(gid,"")=root=gid → giống Sprint 3 (actor về "", không sub-group).
> FindGroupData không có Index → KHÔNG dùng Set Array Elem; dùng rebuild (B2/B3).
> CaptureSnapshot CHỈ ở ForEach_3.Completed (bài học spam snapshot).

### Caller UngroupActors (Ctrl+Shift+G) — KHÔNG đổi
`IsValid(PrimarySelectedActor) → GET GroupID → Branch != "" → UngroupActors(GroupID)`. Hàm tự WalkUpUntilParent để tìm target theo scope.

---

## ─── T8: ValidateEditMode (BP_UndoManager) ───
```
CLEAR LocalValid (Array String)
Get All Actors Of Class(BP_FurnitureInputManager)[0] → Cast → InputRef
Branch(IsValid(InputRef)) → False: Return
GET InputRef.EditModeStack → For Each Loop WITH BREAK (gid):
  LoopBody → InputRef.FindGroupData(gid) → (_, bFound)
           → Branch(bFound):
               True  → ADD gid → LocalValid
               False → BREAK                     ← group mất → cắt từ đây lên
  Completed →
SET InputRef.EditModeStack = LocalValid
Branch(InputRef.EditModeStack.Length == 0):
  True  → InputRef.RemoveEditModeVisual → Broadcast OnEditModeChanged(False, "")
  False → InputRef.ApplyEditModeVisual → GetCurrentEditScope → Scope → Broadcast OnEditModeChanged(True, Scope)
```
**Chèn vào RestoreSnapshot:** sau Step 5b (SyncGroupsToContainer), trước Step 6b (re-fire selection). Lý do: ValidateEditMode đọc Groups (phải sau 5b), broadcast OnEditModeChanged (cập nhật breadcrumb) trước khi 6b cập nhật selection count.

---

## ─── BUG FIX (12/06) — Replace Mesh preserve GroupID ───
**File:** WBP_DragOverlay_FurnitureCard, BTN_ChangeMesh OnClicked, trong ForEach MeshesToReplace.
```
(sau spawn NewActor, TRƯỚC Destroy OldActor):
  Cast OldActor → BP_FurnitureActor → GET GroupID → OldGroupID
  SET NewActor.GroupID = OldGroupID
```
> Phải đặt trước Destroy Actor(OldActor) (sau destroy không đọc được GroupID). Giữ group structure sau Replace.

---

## ─── LƯU Ý QUAN TRỌNG SPRINT 4 ───
- ResolveSelectionUnit: thứ tự nhánh EditScope!="" TRƯỚC gid=="" là BẮT BUỘC (Q9a).
- Đệ quy BP Function (GetAllDescendantActors, GetGroupsInHierarchy): local var stack-độc-lập, ForEach_3/_2 inner Completed để TRỐNG.
- Return trong ForLoop Body của GetGroupRoot/WalkUpUntilParent thoát hàm ngay (đúng).
- UngroupActors peel-one-level: B1→B2→B3 nối tuần tự qua Completed; CaptureSnapshot 1 lần ở B3.Completed.
- Click ngoài scope khi edit → CLEAR selection nhưng VẪN ở edit mode (MVP — D4-4).

---

## Lịch sử cập nhật (Blueprint_Logic)
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.3 | 07/06/2026 — 22:40 | Sprint 2: Mouse Pressed defer, Tick box branch, OnLMBReleased, FinishBoxSelect, Context Menu |
| 1.4 | 12/06/2026 — 15:04 | **Sprint 3 group final (ExpandSelectionWithGroups, snapshot v3) + Sprint 4 đầy đủ:** 7 helper (GetCurrentEditScope, GetChildGroups, GetGroupRoot, WalkUpUntilParent, GetAllDescendantActors, GetGroupsInHierarchy, ResolveSelectionUnit), GetEditBreadcrumb, Enter/Exit edit, TryEnterEdit, WBP_MeshControls edit UI, CreateGroup nested, PruneEmptyGroups + UngroupActors peel-one-level, ValidateEditMode, Replace GroupID fix. |
