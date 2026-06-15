# Sprint 4 — Edit Mode + Nested Group (Plan chi tiết — Opus 4.8)
**Phiên bản:** 1.0 | **Ngày:** 08/06/2026 ICT | Lighting_Mnger UE5.5.4
**Thay thế:** phần Sprint 4 trong plan_v3/04_Sprint_Details.md + MultiSelect_Group_ComboMesh_Plan_v2.md (giữ làm reference)
**Tiền đề:** Sprint 3 (Group cơ bản) đã xong — Groups array, BP_GroupsContainer, ExpandSelectionWithGroups, GetGroupChildren, FindGroupData, SyncGroupsToContainer, snapshot v3.
**Đích cuối định hướng:** group mesh → **tạo Combo Mesh asset runtime** → lưu local/server → spawn combo runtime. Sprint 4 là NỀN cho combo (nested bắt buộc để combo chứa cấu trúc lồng).

---

## 0. NGUYÊN TẮC NỀN (insight cốt lõi)

> **Edit Mode KHÔNG phải một "chế độ" mới. Nó chỉ là một SELECTION SCOPE FILTER.**

Khi `EditModeStack` rỗng → click resolve ra **cả group** (hành vi Sprint 3).
Khi `EditModeStack` có giá trị → click resolve ra **đơn vị con bên trong scope đó** (1 đồ hoặc 1 sub-group).

Mọi thao tác chỉnh từng đồ (move/rotate/scale/delete/material) **đã chạy sẵn** từ single-select machinery (Sprint 1-2). Sprint 4 KHÔNG viết code transform/delete mới. Chỉ làm 3 thứ:
1. **Resolver tổng quát** (`ResolveSelectionUnit`) biến click → đúng đơn vị theo scope.
2. **Quản lý scope** (enter/exit, stack cho nested).
3. **Phản hồi hình ảnh** (info bar; dim cắm hook, làm sau).

Nested group = resolver đệ quy + ParentGroupID. KHÔNG AttachToActor (giữ antipattern #2: transform world-relative).

### 6 quyết định kiến trúc đã chốt
| # | Quyết định | Lý do |
|---|---|---|
| D1 | 1 hàm `ResolveSelectionUnit(Actor, EditScope)` dựng trên helper đệ quy | Tổng quát; flat = case đặc biệt; không phá Sprint 3 |
| D2 | `EditModeStack : Array<String>` (không phải String đơn) | Nested navigation là stack; tránh refactor |
| D3 | Trigger = nút info bar + Enter trước; double-click hỏi lại khi làm tới T4 | Không đụng hệ defer click mong manh |
| D4 | MVP không dim nhưng **cắm sẵn hook** (stub function + reserve stencil 200) | Ưu tiên máy yếu; sau chỉ đổ body |
| D5 | Nested LÀM LUÔN (slice 2) — bắt buộc cho combo nested | Combo chỉ phẳng nếu thiếu nested |
| D6 | KHÔNG snapshot edit mode; ValidateEditMode trong RestoreSnapshot | Không bẩn undo history; chống edit group ma |

### Cắt khỏi plan gốc
- ❌ Overlay widget toàn viewport (sai bản chất — widget 2D đè 3D, không dim chọn lọc)
- ❌ Snapshot CurrentEditingGroupID (view state)
- ❌ Sub-group transform inheritance qua attach (dùng resolver đệ quy)
- ❌ Kéo đồ ra/vào group bằng bounding box (hoãn Sprint 6 — drag tree node Outliner)

---

## 1. LEARNINGS BẮT BUỘC (đã trả giá)

- Event không có Local Variable → logic phức tạp đặt trong **Function**, Event chỉ gọi.
- CaptureSnapshot SAU action, KHÔNG trong helper. Edit mode KHÔNG snapshot.
- CLEAR array/temp ở ĐẦU function nếu class var / tái dùng (TempSelectedIndices).
- IsValid trước mọi Object access; tất cả nhánh Branch merge về cuối.
- Code 1 lần → Completed của ForEach, KHÔNG Loop Body (DuplicateMesh / box-spawn).
- Array pass-by-ref → SET vào copy + CLEAR + ForEach ADD nếu cần bản độc lập.
- Latent node chỉ trong Custom Event (đệ quy phải là Function thuần).
- Destroy Actor target = phần tử đang duyệt, KHÔNG để trống.
- BP_FurnitureActor: Cast → GET FurnitureMesh, KHÔNG Get Static Mesh Component.
- Toggle/guard đúng thứ tự (CB_Replace).
- KHÔNG thêm var furniture vào BP_FoffPlayerController — Enter/Esc qua IA trong LM_FurnitureInput; PC route sang InputManager (pattern Copy/Paste).
- Event Tick PHẢI guard inventory/context (box-select). Double-click timing nếu dùng Tick phải guard.
- R2: widget info bar dùng dispatcher/struct nhẹ, KHÔNG hard ref actor; Event Destruct clear.
- R5: combo JSON sau theo AssetID/RowName, không path /Game/. Sprint 4 không làm tệ hơn.

---

## 2. DATA STRUCTURES

### BP_FurnitureInputManager — thêm
```
EditModeStack : Array<String>      ← stack GroupID đang edit (rỗng = không edit). KHÔNG SaveGame.
```
`CurrentEditScope` (logic) = EditModeStack rỗng ? "" : Last(EditModeStack).

### S_GroupData — KHÔNG đổi (ParentGroupID đã có, bắt đầu set giá trị thật khi tạo sub-group)
### S_SceneSnapshot — KHÔNG thêm field (edit mode không vào snapshot)

### Event Dispatcher mới
```
OnEditModeChanged(bActive : Boolean, GroupID : String)
```

### Stencil reserve (cập nhật)
```
255 = Primary select (đã dùng)
254 = Secondary select (đã dùng)
200 = Đồ MỜ ngoài scope edit (RESERVE cho dimming — chưa dùng, đừng lấy việc khác)
```

---

## 3. HELPER ĐỆ QUY (keystone — Edit Mode + Combo S5 + Outliner S6)

Tất cả là **Function** (không latent). Depth guard max 10 chống data lỗi tạo vòng.

```
GetGroupRoot(InGroupID) → String          ← đi NGƯỢC lên ParentGroupID tới group cao nhất
  Local Current = InGroupID
  Loop 0..10: FindGroupData(Current)→(data,bFound)
    bFound==False → Return Current
    data.ParentGroupID=="" → Return Current
    SET Current = data.ParentGroupID
  Return Current
  ★ click resolution, Combo save, Outliner

GetChildGroups(InGroupID) → Array<S_GroupData>     ← group con TRỰC TIẾP
  CLEAR LocalChildren
  ForEach Groups (g): g.ParentGroupID==InGroupID → ADD
  Return LocalChildren
  ★ GetAllDescendantActors, GetGroupsInHierarchy, Outliner tree

GetAllDescendantActors(InGroupID) → Array<BP_FurnitureActor>    ← TẤT CẢ actor dưới cây, đệ quy
  CLEAR LocalResult
  GetGroupChildren(InGroupID) → ForEach → ADD          ← member trực tiếp
  GetChildGroups(InGroupID) → ForEach (cg):
    GetAllDescendantActors(cg.GroupID) → ForEach → ADD  ← RECURSE
  Return LocalResult
  ⚠️ VERIFY local var độc lập mỗi stack frame; sai → fallback iterative worklist
  ★ nested selection, dimming scope, Combo members, lock cây

GetGroupsInHierarchy(InGroupID) → Array<S_GroupData>    ← THÊM cho combo: TẤT CẢ group data trong cây
  CLEAR LocalGroups
  FindGroupData(InGroupID)→(data,bFound); bFound → ADD data    ← chính group này
  GetChildGroups(InGroupID) → ForEach (cg):
    GetGroupsInHierarchy(cg.GroupID) → ForEach → ADD    ← RECURSE
  Return LocalGroups
  ★ Combo serialize cấu trúc group, Outliner tree

WalkUpUntilParent(InGroupID, TargetParent) → String     ← lên tới group có ParentGroupID==TargetParent
  Local Current = InGroupID
  Loop 0..10: FindGroupData(Current)→(data,bFound)
    bFound==False → Return ""
    data.ParentGroupID==TargetParent → Return Current
    data.ParentGroupID=="" → Return ""
    SET Current = data.ParentGroupID
  Return ""
```

> **Tương thích Sprint 3:** flat → GetGroupRoot=gid, GetAllDescendantActors=GetGroupChildren, GetGroupsInHierarchy=[nó]. Không regression.

---

## 4. RESOLVER — `ResolveSelectionUnit` (não Sprint 4)

```
ResolveSelectionUnit(Actor, EditScope) → Array<BP_FurnitureActor>
  Guard IsValid(Actor)→False: Return empty
  GET gid = Actor.GroupID

  CASE 1 — đồ rời (gid==""): Return [Actor]
  CASE 2 — KHÔNG edit (EditScope==""):
    Return GetAllDescendantActors(GetGroupRoot(gid))
  CASE 3 — đang edit (EditScope!=""):
    gid==EditScope → Return [Actor]              ← member trực tiếp → cá nhân
    else:
      ancestor = WalkUpUntilParent(gid, EditScope)
      ancestor!="" → Return GetAllDescendantActors(ancestor)   ← chọn cả sub-group
      else → Return empty                        ← ngoài scope → bỏ qua
```

**ExpandSelectionWithGroups (sửa từ Sprint 3):**
```
  SET ActorsCopy = RawActors; CLEAR LocalResult
  SET EditScope = (EditModeStack rỗng ? "" : Last)
  ForEach ActorsCopy: ResolveSelectionUnit(_, EditScope) → ForEach Unit:
    NOT Contains(LocalResult, Unit) → ADD
  Return LocalResult
```
> Click (T8) + box (T9) Sprint 3 đều gọi hàm này → tự đúng nested + edit mode, KHÔNG sửa T8/T9.

---

## 5. VERTICAL SLICE 1 — FLAT EDIT MODE (kill risk)

```
Slice 1 = T1+T2+T3+T4+T5 (ResolveSelectionUnit CASE 1+2+3-True; nested 3-False test slice 2)

TEST:
1. Group 3 đồ → click → cả 3 chọn
2. Enter → vào edit (info bar "✏️ Đang chỉnh: Nhóm 1")
3. Click 1 đồ → CHỈ đồ đó (gizmo 1 đồ)
4. Move đồ đó → chỉ nó di chuyển
5. Click đồ khác trong group → chuyển chọn cá nhân
6. Esc → thoát → click → lại cả group
7. Regression: đồ rời + box đồ rời OK
```

---

## 6. TASK BREAKDOWN

### T1 — EditModeStack + 6 Helper + 2 stub dimming (1.5 giờ) ⭐
- Var `EditModeStack` (KHÔNG SaveGame).
- 6 Function: GetGroupRoot, GetChildGroups, GetAllDescendantActors, GetGroupsInHierarchy, WalkUpUntilParent, ResolveSelectionUnit.
- 2 stub RỖNG: `ApplyEditModeVisual()`, `RemoveEditModeVisual()` (no-op MVP, T3 gọi sẵn).
- End Play: CLEAR EditModeStack.
- Test: Print GetAllDescendantActors(root).Length flat = số member; GetGroupsInHierarchy(root).Length flat = 1.

### T2 — ExpandSelectionWithGroups dùng ResolveSelectionUnit (30 phút)
Thay logic inline; KHÔNG sửa T8/T9. Test: click group → cả group còn nguyên.

### T3 — EnterEditMode / ExitEditMode (1 giờ)
```
EnterEditMode(InGroupID):
  InGroupID=="" → Return; FindGroupData→bFound False → Return
  ADD InGroupID to EditModeStack (PUSH); DeselectAll
  ApplyEditModeVisual; Broadcast OnEditModeChanged(True, InGroupID)

ExitEditModeOneLevel():  ← Esc
  EditModeStack.Length==0 → Return
  Local Exited = Last; REMOVE INDEX(Length-1) (POP)
  Length==0:
    True → RemoveEditModeVisual; GetGroupChildren(Exited)→Get(0)(guard)→ExpandSelectionWithGroups→SelectActors; Broadcast(False,"")
    False→ ApplyEditModeVisual; Broadcast(True, Last)

ExitEditModeFull():  ← nút Thoát
  Length==0 → Return; CLEAR EditModeStack; RemoveEditModeVisual; Broadcast(False,"")
```

### T4 — Trigger Enter + Esc + nút (45 phút) [D3 — hỏi lại double-click ở đây]
IA_EditModeEnter (Enter), IA_EditModeExit (Esc) trong LM_FurnitureInput. PC route:
```
TryEnterEditFromSelection():
  IsValid(PrimarySelectedActor) False → Return
  gid = PrimarySelectedActor.GroupID; gid=="" → Return
  EditModeStack.Length>=3 → Return        ← giới hạn 3 cấp
  Scope = (rỗng?"":Last)
  Scope=="" → EnterEditMode(GetGroupRoot(gid))
  else → sub=WalkUpUntilParent(gid,Scope); sub!="" → EnterEditMode(sub)

IA_EditModeExit (Started):
  EditModeStack.Length>0 → ExitEditModeOneLevel; else → DeselectAll
```
> Verify Enter không bị nuốt khi search box focus; Esc hiện bind gì.

### T5 — Info Bar mở rộng (45 phút)
Bind OnEditModeChanged: True → "✏️ Đang chỉnh: "+GroupName + BTN_ExitEdit + breadcrumb nếu Stack>1; False → text count cũ. R2/R3 nhẹ, Event Destruct clear.

### --- HẾT SLICE 1. TEST. PASS → tiếp. ---

### T6 — SLICE 2: Nested (1.5 giờ)
Sửa CreateGroup 1 dòng: `ParentGroupID = (EditModeStack rỗng ? "" : Last)`.
```
TEST: Group cha → Enter → Ctrl+G sub (ParentGroupID đúng) → Esc → click chọn cả cây
      → Enter cha → click sub member chọn cả sub → Enter sub → click chỉ 1 đồ → cấp 4 chặn
```

### T7 — (POLISH, hoãn) Dimming — đổ body 2 stub
```
ApplyEditModeVisual: scope=GetAllDescendantActors(CurrentEditScope)
  ForEach Tag("FurnitureSpawned"): NOT Contains(scope) → Render Custom Depth=True + Stencil=200
  M_SelectionOutline thêm nhánh Stencil==200 → desaturate/tối
RemoveEditModeVisual: ForEach ngoài-scope → Render Custom Depth=False (KHÔNG đụng 255/254)
```

### T8 — RestoreSnapshot safety + Final test (45 phút)
```
ValidateEditMode():  ← cuối RestoreSnapshot (sau restore Groups)
  CLEAR LocalValid
  ForEach EditModeStack (gid): FindGroupData→bFound
    bFound → ADD gid; NOT bFound → BREAK
  SET EditModeStack = LocalValid
  Length==0 → RemoveEditModeVisual+Broadcast(False,""); else → ApplyEditModeVisual+Broadcast(True,Last)
```

### (Double-click — OPTIONAL, quyết T4)
OnLMBReleased sau resolve PendingClick → Now-LastClickTime<0.3 AND LastClickActor==Pending → TryEnterEditFromSelection. Vỡ defer/box → bỏ, giữ Enter+nút.

---

## 7. TEST CASES

| # | Case | Kỳ vọng |
|---|---|---|
| 1 | Group 3 đồ → Enter | Vào edit, info bar đúng |
| 2 | Trong edit, click 1 đồ | Chỉ 1 đồ |
| 3 | Trong edit, move 1 đồ | Chỉ nó di chuyển |
| 4 | Esc | Thoát, click → lại cả group |
| 5 | Đồ rời, Enter | Không vào (guard) |
| 6 | Nested Ctrl+G trong edit | Sub ParentGroupID đúng |
| 7 | Ngoài edit click đồ trong sub | Chọn cả root |
| 8 | Enter root → click sub member | Chọn cả sub (1 đơn vị) |
| 9 | Enter root → Enter sub → click | Chỉ 1 đồ; breadcrumb 2 cấp |
| 10 | Cấp 4 | Bị chặn |
| 11 | Undo qua CreateGroup khi đang edit | Tự thoát (ValidateEditMode) |
| 12 | Save → Load → click | Group/nested khôi phục |
| 13 | Regression S1-S3 | Nguyên vẹn |
| 14 | GetGroupsInHierarchy nested 2 cấp | Đủ số group (combo readiness) |

---

## 8. THỨ TỰ THỰC THI

```
SLICE 1: T1→T2→T3→T4→T5 → TEST
SLICE 2: T6 → TEST
SAFETY: T8 → final 14 cases + regression
POLISH (optional): T7 dim → double-click
DOCS: Session_State, Blueprint_Logic, BP_FurnitureInputManager v1.7, DEVIATIONS
```

---

## 9. KẾ THỪA & BRIDGE TỚI COMBO (S5)

| Function | Từ | Tương lai |
|---|---|---|
| ResolveSelectionUnit | mới | mọi selection |
| GetGroupRoot | mới | Combo save, Outliner |
| GetChildGroups | mới | hierarchy, Outliner tree |
| GetAllDescendantActors | mới (đệ quy) | **Combo members**, dimming, lock cây |
| GetGroupsInHierarchy | mới (đệ quy) | **Combo cấu trúc group** |
| EnterEditMode scope filter | mới | Lock/Visibility filter (S6) |
| 2 stub dimming | mới (rỗng) | đổ body khi làm dim |

### Luồng Combo (xác nhận readiness)
```
SAVE(rootGID):
  members=GetAllDescendantActors(rootGID)   ← S4
  groups =GetGroupsInHierarchy(rootGID)     ← S4 (mới)
  center =CalculateCenter(members)          ← S1
  remap={old GroupID → "grp_i"}
  JSON.groups=groups.map(g→{token,name,parent=remap[ParentGroupID]})
  JSON.meshes=members.map(a→{assetID,relLoc=Loc-center,rot,scale,materials,surface,group=remap[a.GroupID]})
  → DT_ComboMeshCatalog (local) / Supabase (server)

SPAWN(row,worldLoc):
  newIDmap={token → GenerateGroupID()}      ← S3
  ForEach JSON.groups → Make S_GroupData{newID,name,ParentGroupID=newIDmap[parent]} → ADD Groups
  SyncGroupsToContainer                      ← S3
  ForEach JSON.meshes → SpawnFurnitureCopy(assetID,worldLoc+relLoc) → actor.GroupID=newIDmap[group]  ← S1
  CaptureSnapshot("SpawnCombo")
```
> **Sprint 4 nested = bắt buộc để combo chứa cấu trúc lồng.** Sau S4, group tree fully serializable.

**Single source of truth:** EditModeStack (in-memory, không snapshot). Mọi "click resolve ra gì" → 1 cửa ResolveSelectionUnit. Nested = data + đệ quy, KHÔNG attach.

---

## 10. RỦI RO / VERIFY

- Đệ quy BP Function local var độc lập mỗi frame (GetAllDescendantActors/GetGroupsInHierarchy); sai → iterative worklist.
- Esc đụng độ Deselect → route theo EditModeStack.
- Enter bị search box nuốt → guard widget focus.
- Stencil 200 vs 255/254 khi làm T7.
- Depth guard max 10 chống ParentGroupID vòng.
- R5 combo cloud: AssetID/RowName, để Phase B (glTFRuntime + AssetService).
