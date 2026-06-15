# BP_FurnitureInputManager — PATCH v1.7
**Phiên bản:** 1.7 | **Cập nhật:** 11/06/2026 — 18:14 ICT
**Patch từ v1.6 → v1.7 (Sprint 4 T1–T5 — Edit Mode Slice 1)**
> Đọc kèm bản gốc v1.6. File này ghi ĐỦ những gì thêm/thay đổi.

---

## Variables MỚI (Sprint 4)
```
EditModeStack : Array<String>   ← stack GroupID đang edit. Rỗng = không edit. KHÔNG SaveGame. CLEAR ở End Play.
```
**End Play:** thêm `CLEAR EditModeStack` vào chuỗi clear hiện có (cạnh CLEAR Groups, MeshesToReplace).

---

## Event Dispatchers MỚI
```
OnEditModeChanged(bActive : Boolean, GroupID : String)
```

---

## Functions MỚI (Sprint 4 T1)

### `GetCurrentEditScope() → String`
Trả GroupID đang ở scope edit. Rỗng = không edit.
```
Branch(EditModeStack.Length > 0):
  True  → EditModeStack → Last Index → GET → Return
  False → Return ""
```

### `GetChildGroups(InGroupID : String) → Array<S_GroupData>`
Group con TRỰC TIẾP của InGroupID (dựa ParentGroupID).
```
CLEAR LocalChildren
ForEach Groups (g): Branch(g.ParentGroupID == InGroupID): True → ADD g
Completed → Return LocalChildren
```

### `GetGroupRoot(InGroupID : String) → String`
Leo ngược ParentGroupID đến gốc (ParentGroupID == ""). Depth guard 10.
```
SET Current = InGroupID
ForLoop(0..9):
  FindGroupData(Current) → (data, _, bFound)
  bFound==False → Return Current
  data.ParentGroupID=="" → Return Current
  Else → SET Current = data.ParentGroupID
Completed → Return Current
```

### `WalkUpUntilParent(InGroupID, TargetParent : String) → String`
Leo ngược tìm group là con trực tiếp của TargetParent trên đường đi từ InGroupID. Depth guard 10.
```
SET Current = InGroupID
ForLoop(0..9):
  FindGroupData(Current) → (data, _, bFound)
  bFound==False → Return ""
  data.ParentGroupID==TargetParent → Return Current   ← TÌM THẤY
  data.ParentGroupID=="" → Return ""                  ← lên hết gốc
  Else → SET Current = data.ParentGroupID
Completed → Return ""
```

### `GetAllDescendantActors(InGroupID : String) → Array<BP_FurnitureActor>` ⭐ ĐỆ QUY
Tất cả actor dưới cây (member trực tiếp + actor trong sub-groups đệ quy).
```
CLEAR LocalResult
GetGroupChildren(InGroupID) → ForEach_1: ADD Element → LocalResult
  Completed → GetChildGroups(InGroupID) → ForEach_2 (cg):
    GetAllDescendantActors(cg.GroupID) → ForEach_3: ADD Element → LocalResult
    Completed → (để trống)
  Completed → Return LocalResult
```
⚠️ Local var độc lập mỗi stack frame (đã verify OK). Fallback iterative nếu cần.

### `GetGroupsInHierarchy(InGroupID : String) → Array<S_GroupData>` ⭐ ĐỆ QUY (bridge Combo S5)
Toàn bộ group data trong cây (InGroupID + tất cả sub-groups đệ quy).
```
CLEAR LocalGroups
FindGroupData(InGroupID) → bFound: True → ADD data → LocalGroups; False → (tiếp)
(merge) → GetChildGroups(InGroupID) → ForEach_1 (cg):
  GetGroupsInHierarchy(cg.GroupID) → ForEach_2: ADD Element → LocalGroups
  Completed → (để trống)
Completed → Return LocalGroups
```

### `ResolveSelectionUnit(Actor, EditScope : String) → Array<BP_FurnitureActor>` ⭐ NÃO Sprint 4
Resolver tổng quát: click actor → trả đúng đơn vị chọn theo scope edit.
**THỨ TỰ NHÁNH BẮT BUỘC (Q9a: edit-scope trước đồ-loose):**
```
IsValid(Actor)==False → Return []
Cast → GET GroupID → gid

Branch(EditScope != ""):                         ← ĐANG EDIT — xét TRƯỚC
  True →
    gid==EditScope → Return [Actor]              ← member trực tiếp → cá nhân
    gid=="" → Return []                          ← đồ rời ngoài scope → bỏ qua
    WalkUpUntilParent(gid, EditScope) → ancestor
    ancestor!="" → Return GetAllDescendantActors(ancestor)   ← sub-group → cả sub-group
    ancestor=="" → Return []                     ← ngoài scope → bỏ qua

  False →                                        ← KHÔNG EDIT
    gid=="" → Return [Actor]                     ← đồ rời → chính nó
    GetGroupRoot(gid) → root → Return GetAllDescendantActors(root)   ← group → cả cây
```

### `GetEditBreadcrumb() → String`
Breadcrumb dạng "Nhóm 1 › Nhóm 2" cho info bar.
```
SET Result = ""
ForEach EditModeStack (Element, ArrayIndex):
  FindGroupData(Element) → bFound:
    False → Return Result (early exit — data lỗi)
    True → ArrayIndex==0: SET Result = GroupName
           Else: SET Result = Append(Result, "›", GroupName)
Completed → Return Result
```

### `ApplyEditModeVisual()` — STUB RỖNG (T9 đổ body)
### `RemoveEditModeVisual()` — STUB RỖNG (T9 đổ body)

---

## Functions SỬA (Sprint 4 T2)

### `ExpandSelectionWithGroups(RawActors) → Array<BP_FurnitureActor>`
**Viết lại body** dùng ResolveSelectionUnit (thay logic inline Sprint 3):
```
SET ActorsCopy = RawActors; CLEAR LocalResult
GetCurrentEditScope() → Scope
ForEach ActorsCopy (Actor):
  ResolveSelectionUnit(Actor, Scope) → ForEach_inner (Unit):
    NOT Contains(LocalResult, Unit) → ADD Unit → LocalResult
Completed → Return LocalResult
```
> Tick fallback (Event Tick Branch A) cũng đổi từ SelectSingleActor → DeselectAll+ExpandSelectionWithGroups+SelectActors cho nhất quán.

---

## Functions MỚI (Sprint 4 T3–T4)

### `EnterEditMode(InGroupID : String)`
```
InGroupID=="" → Return
FindGroupData(InGroupID) → bFound==False → Return
ADD InGroupID → EditModeStack
DeselectAll → ApplyEditModeVisual
Broadcast OnEditModeChanged(True, InGroupID)
```

### `ExitEditModeOneLevel()`
```
EditModeStack.Length==0 → Return
GetCurrentEditScope() → SET Exited
EditModeStack → Last Index → REMOVE INDEX (POP)
Branch(EditModeStack.Length==0):
  True (thoát hẳn) →
    RemoveEditModeVisual → DeselectAll
    GetAllDescendantActors(Exited) → LocalTree
    LocalTree.Length>0 → SelectActors(LocalTree)   (merge về)
    Broadcast OnEditModeChanged(False, "")
  False (còn cấp cha) →
    ApplyEditModeVisual → DeselectAll
    GetAllDescendantActors(Exited) → LocalTree
    LocalTree.Length>0 → SelectActors(LocalTree)   (merge về)
    GetCurrentEditScope() → NewScope
    Broadcast OnEditModeChanged(True, NewScope)
```
> DeselectAll trước SelectActors (SelectActors chỉ ADD, không clear).
> GetAllDescendantActors (không phải GetGroupChildren) — chống fail nested thuần.

### `ExitEditModeFull()`
```
EditModeStack.Length==0 → Return
EditModeStack → GET[0] → SET RootScope
CLEAR EditModeStack → RemoveEditModeVisual → DeselectAll
GetAllDescendantActors(RootScope) → LocalTree
LocalTree.Length>0 → SelectActors(LocalTree)   (merge về)
Broadcast OnEditModeChanged(False, "")
```

### `TryEnterEditFromSelection()`
```
IsValid(PrimarySelectedActor)==False → Return
Cast → GET GroupID → gid; gid=="" → Return
EditModeStack.Length>=3 → Return   ← giới hạn 3 cấp
GetCurrentEditScope() → Scope
Scope=="" → EnterEditMode(GetGroupRoot(gid))
Else →
  WalkUpUntilParent(gid, Scope) → Sub
  Sub!="" → EnterEditMode(Sub)
  Sub=="" → Return (member trực tiếp hoặc ngoài scope → no-op)
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| ... | ... | (xem v1.6) |
| 1.7 | 11/06/2026 — 18:14 ICT | **Sprint 4 T1–T5 — Edit Mode Slice 1.** Var `EditModeStack`. Dispatcher `OnEditModeChanged`. 7 helper mới: `GetCurrentEditScope`, `GetChildGroups`, `GetGroupRoot`, `WalkUpUntilParent`, `GetAllDescendantActors`(đệ quy), `GetGroupsInHierarchy`(đệ quy bridge Combo), `ResolveSelectionUnit`(não Sprint 4). Hàm `GetEditBreadcrumb`. 2 stub: `ApplyEditModeVisual`, `RemoveEditModeVisual`. Sửa `ExpandSelectionWithGroups` dùng ResolveSelectionUnit. Thêm `EnterEditMode`, `ExitEditModeOneLevel`, `ExitEditModeFull`, `TryEnterEditFromSelection`. CLEAR EditModeStack ở End Play. |
