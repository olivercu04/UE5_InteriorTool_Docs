# Sprint 4 — Edit Mode + Nested Group (EXECUTION step-by-step — Opus 4.8)

> ⚠️ **[AS-BUILT TẠI THỜI ĐIỂM SPRINT 4]** — File ghi lại thực thi Sprint 4, KHÔNG cập nhật
> theo thay đổi sau đó. Một số chữ ký hàm đã đổi (vd `FindGroupData` nay chỉ có 2 output
> `(GroupData, bFound)` — xem `Blueprints/BP_FurnitureInputManager.md`). Đọc để hiểu Sprint 4
> đã làm gì; chữ ký/API hiện tại LUÔN tra doc canonical.

**Phiên bản:** 2.0 (execution) | **Ngày:** 11/06/2026 ICT | Lighting_Mnger UE5.5.4
**Thay thế phần thực thi của:** `Sprint4_Plan_Opus.md` v1.0 (giữ v1.0 làm reference triết lý).
**Đối tượng đọc:** model thực thi (Sonnet 4.6). Làm **TỪNG TASK MỘT**, mỗi task có test riêng, làm xong **báo cuhoang** rồi mới qua task sau.
**Tiền đề đã có (Sprint 3, v1.6):** `Groups` array, `BP_GroupsContainer`, `GetGroupChildren`, `FindGroupData` (trả `S_GroupData, Index, bFound`), `ExpandSelectionWithGroups`, `SyncGroupsToContainer`, `PruneEmptyGroups`, `GenerateGroupID`, `CreateGroup`, `UngroupActors`, snapshot v3 (`GroupID` per placement + `Groups` array). Dispatcher selection DUY NHẤT = `OnSelectionChanged`. Info bar nằm trong `WBP_MeshControls` (v1.4), Event Construct đã bind `OnSelectionChanged → OnSelectionChangedInfoBar`.

---

## 0. INSIGHT CỐT LÕI (đọc trước, đừng quên giữa chừng)

> **Edit Mode KHÔNG phải "chế độ" mới. Nó là một SELECTION SCOPE FILTER.**

- `EditModeStack` rỗng → click resolve ra **cả group** (hành vi Sprint 3 nguyên vẹn).
- `EditModeStack` có giá trị → click resolve ra **đơn vị con bên trong scope** (1 đồ hoặc 1 sub-group).
- Move/Rotate/Scale/Delete/Material **đã chạy sẵn** từ single-select (Sprint 1-2). Sprint 4 **KHÔNG viết code transform mới.**
- Nested group = **resolver đệ quy + ParentGroupID**. KHÔNG dùng AttachToActor.

Sprint 4 chỉ làm 3 việc: (1) resolver tổng quát biến click → đúng đơn vị theo scope, (2) quản lý scope (enter/exit, stack nested), (3) phản hồi hình ảnh (info bar; dim cắm hook làm sau).

---

## 1. QUYẾT ĐỊNH ĐÃ CHỐT (không bàn lại)

| # | Quyết định | Ghi chú thực thi |
|---|---|---|
| D1 | `ResolveSelectionUnit(Actor, EditScope)` dựng trên helper đệ quy | flat = case đặc biệt; không phá Sprint 3 |
| D2 | `EditModeStack : Array<String>` (stack, KHÔNG String đơn) | nested = stack |
| D3 | **Trigger = NÚT trên info bar** (MVP). Esc KHÔNG đụng (Esc = thoát PIE). Phím tắt Enter = TBD | logic tách rời phím; chỉ cần IA gọi function sau |
| D4 | MVP **không dim** nhưng cắm stub `ApplyEditModeVisual`/`RemoveEditModeVisual` + reserve Stencil 200 | sau chỉ đổ body |
| D5 | Nested LÀM LUÔN (Slice 2) | bắt buộc cho combo nested |
| D6 | **KHÔNG snapshot edit mode.** `ValidateEditMode` trong RestoreSnapshot. Snapshot giữ Version=3, KHÔNG bump | edit mode là view-state, không bẩn undo |
| Q9a | `ResolveSelectionUnit`: khi `EditScope != ""` → xét **edit-scope TRƯỚC** đồ-loose | đồ loose ngoài scope cũng trả empty → nhất quán |
| Q9b | Click ngoài scope khi edit → **CLEAR selection nhưng VẪN ở edit mode** (MVP). Không đụng caller | thoát edit chỉ bằng nút |
| Q3 | `ExitEditMode...` re-select bằng `GetAllDescendantActors(Exited)` **trực tiếp** (KHÔNG `Get(0)`→Expand) | chống fail với nested thuần |
| Q4 | `Exit...` PHẢI `DeselectAll` TRƯỚC `SelectActors` | SelectActors chỉ ADD, không clear |
| Q6 | `PruneEmptyGroups` keep theo `GetAllDescendantActors(g).Length > 0` | chống prune oan group cha nested |
| Q7 | `UngroupActors` → **deep ungroup cả cây** (GetGroupRoot + GetAllDescendantActors + GetGroupsInHierarchy) | chống orphan sub-group; flat = giống cũ |
| Q8 | Không có node "Last". Dùng `Last Index → Get`. Gói thành helper `GetCurrentEditScope()` | DRY, tránh off-by-one |
| Q13 | Spawn trong edit mode → `GroupID=""` (KHÔNG auto-assign) | không đụng SpawnFurnitureCopy/Paste |

### Quyết định HOÃN (decide-when-reached)
- **Phím tắt Enter-edit:** chọn phím khi làm tới (đề xuất: KHÔNG Esc). MVP test bằng nút.
- **Q9b nâng cấp:** click-ngoài-scope = no-op (giữ nguyên selection) thay vì CLEAR — chỉ làm nếu test thấy CLEAR khó chịu (phải đụng caller defer mong manh).
- **Q11 layout nút:** vị trí `BTN_EnterEdit` / hàng breadcrumb / nút thoát — wiring đủ ở T5, vị trí cụ thể cuhoang chỉnh khi tới.
- **T9 dimming:** đổ body 2 stub — polish, làm cuối nếu còn thời gian.
- **Double-click để enter:** optional, chỉ cân nhắc nếu phím tắt không đủ tiện.

---

## 2. LEARNINGS BẮT BUỘC (đã trả giá — áp dụng mọi task)

- Event KHÔNG có Local Variable → logic phức tạp đặt trong **Function**, Event chỉ gọi.
- **Đệ quy PHẢI là Function thuần** (không latent: không Delay/Async/Timer bên trong).
- CLEAR array/temp ở **ĐẦU function** nếu là class var hoặc tái dùng (bài học `TempSelectedIndices`, `FoundIdx`).
- **IsValid trước MỌI Object access.** Handler nhận selection có thể rỗng → guard.
- **Tất cả nhánh Branch merge về cuối** — nhánh False/empty cũng phải tới điểm kết, KHÔNG dead-end.
- Code chạy 1 lần → nối **Completed** của ForEach, KHÔNG Loop Body.
- Array pass-by-ref → `SET ActorsCopy = Input` rồi mới iterate.
- `BP_FurnitureActor`: Cast → GET `FurnitureMesh` (KHÔNG `Get Static Mesh Component`).
- CaptureSnapshot **SAU** action. **Edit mode KHÔNG snapshot.**
- KHÔNG thêm var furniture vào `BP_FoffPlayerController`. Phím tắt (sau này) route qua IA trong `LM_FurnitureInput` → gọi function InputManager (pattern Copy/Paste).
- `SelectActors` chỉ Contains-check-ADD, **KHÔNG clear** → caller phải `DeselectAll` trước.

---

## 3. DATA STRUCTURES THÊM (làm trong T1)

### BP_FurnitureInputManager — biến mới
```
EditModeStack : Array<String>     ← stack GroupID đang edit. Rỗng = không edit. KHÔNG SaveGame. CLEAR ở End Play.
```

### Event Dispatcher mới (BP_FurnitureInputManager)
```
OnEditModeChanged(bActive : Boolean, GroupID : String)
```

### S_GroupData — KHÔNG đổi
`ParentGroupID` đã có sẵn (Sprint 3 để ""), Sprint 4 bắt đầu set giá trị thật khi tạo sub-group.

### S_SceneSnapshot — KHÔNG thêm field (D6). Version giữ = 3.

### Stencil reserve (ghi nhớ, dùng ở T9)
```
255 = Primary select (đang dùng)
254 = Secondary select (đang dùng)
200 = Đồ MỜ ngoài scope edit (RESERVE — chưa dùng, đừng lấy việc khác)
```

---

## 4. THỨ TỰ THỰC THI

```
SLICE 1 (flat edit mode — kill risk):  T1 → T2 → T3 → T4 → T5 → TEST SLICE 1
SLICE 2 (nested):                       T6 → T7 → TEST SLICE 2
SAFETY:                                 T8 → TEST 14 case + regression
POLISH (optional):                      T9 (dimming)
DOCS:                                   cập nhật cuối
```

---

# SLICE 1 — FLAT EDIT MODE

---

## T1 — EditModeStack + GetCurrentEditScope + 5 Helper đệ quy + ResolveSelectionUnit + 2 stub ⭐ KEYSTONE

> Đây là task lớn nhất, là não của cả sprint. Làm cẩn thận, test từng helper bằng Print String trước khi qua T2.

### 1.1 Biến + dispatcher
- Tạo var `EditModeStack : Array<String>` (KHÔNG SaveGame).
- Tạo Event Dispatcher `OnEditModeChanged(bActive : Boolean, GroupID : String)`.
- **Event End Play:** thêm `CLEAR EditModeStack` (cạnh CLEAR Groups / MeshesToReplace có sẵn).

### 1.2 Helper `GetCurrentEditScope() → String` (Pure được)
```
Branch (EditModeStack.Length > 0):
  True  → EditModeStack → Last Index → Get → Return (giá trị)
  False → Return ""
```
> Mọi nơi cần "scope hiện tại" đều gọi hàm này. KHÔNG đọc `Last(...)` rải rác.

### 1.3 `GetChildGroups(InGroupID : String) → Array<S_GroupData>`
```
CLEAR LocalChildren                                  ← local array S_GroupData, đầu hàm
ForEach Groups (g):
  Loop Body → Branch (g.ParentGroupID == InGroupID):
    True → ADD g → LocalChildren
Completed → Return LocalChildren
```

### 1.4 `GetGroupRoot(InGroupID : String) → String`  (đi NGƯỢC lên cha)
```
SET Current = InGroupID                              ← local String
ForLoop (First=0, Last=9):                           ← depth guard 10 chống vòng
  Loop Body:
    FindGroupData(Current) → (data, _, bFound)
    Branch (bFound == False):
      True → Return Current                          ← không tìm thấy → coi Current là gốc
      False → Branch (data.ParentGroupID == ""):
                True → Return Current                ← hết cha → đây là gốc
                False → SET Current = data.ParentGroupID   (lặp tiếp)
Completed → Return Current                           ← cạn guard → trả Current hiện có
```

### 1.5 `WalkUpUntilParent(InGroupID : String, TargetParent : String) → String`
> Đi lên tới group có `ParentGroupID == TargetParent` (= con trực tiếp của TargetParent trên đường đi).
```
SET Current = InGroupID                              ← local String
ForLoop (0..9):
  Loop Body:
    FindGroupData(Current) → (data, _, bFound)
    Branch (bFound == False):
      True → Return ""
      False → Branch (data.ParentGroupID == TargetParent):
                True → Return Current                ← tìm thấy con trực tiếp của Target
                False → Branch (data.ParentGroupID == ""):
                          True → Return ""           ← lên tới gốc mà không gặp Target
                          False → SET Current = data.ParentGroupID
Completed → Return ""
```

### 1.6 `GetAllDescendantActors(InGroupID : String) → Array<BP_FurnitureActor>`  (ĐỆ QUY)
```
CLEAR LocalResult                                    ← local array, đầu hàm
GetGroupChildren(InGroupID) → ForEach (child):       ← member TRỰC TIẾP
  Loop Body → ADD child → LocalResult
Completed →
  GetChildGroups(InGroupID) → ForEach (cg):          ← group con trực tiếp
    Loop Body →
      GetAllDescendantActors(cg.GroupID) → ForEach (descendant):   ← ĐỆ QUY
        Loop Body → ADD descendant → LocalResult
  Completed → Return LocalResult
```
> ⚠️ VERIFY: chạy đệ quy 2 cấp xong, in `GetAllDescendantActors.Length`. Nếu sai/treo → fallback iterative worklist (báo cuhoang trước khi đổi).

### 1.7 `GetGroupsInHierarchy(InGroupID : String) → Array<S_GroupData>`  (ĐỆ QUY — bridge combo S5)
```
CLEAR LocalGroups                                    ← local array S_GroupData
FindGroupData(InGroupID) → (data, _, bFound)
Branch (bFound): True → ADD data → LocalGroups       ← chính group này
GetChildGroups(InGroupID) → ForEach (cg):
  Loop Body →
    GetGroupsInHierarchy(cg.GroupID) → ForEach (g):  ← ĐỆ QUY
      Loop Body → ADD g → LocalGroups
Completed → Return LocalGroups
```

### 1.8 `ResolveSelectionUnit(Actor : BP_FurnitureActor, EditScope : String) → Array<BP_FurnitureActor>` ⭐ não
> **Q9a: khi EditScope != "" thì xét edit-scope TRƯỚC đồ-loose.** Thứ tự nhánh dưới đây là bắt buộc.
```
Branch IsValid(Actor) == False:
  True → Return (empty)                              ← guard

Cast Actor → BP_FurnitureActor → GET GroupID → gid

Branch (EditScope != ""):                            ← ĐANG EDIT  (xét TRƯỚC)
  True →
    Branch (gid == EditScope):
      True → Return Make Array(Actor)                ← member trực tiếp scope → cá nhân
      False →
        Branch (gid == ""):
          True → Return (empty)                      ← đồ loose ngoài scope → BỎ QUA (Q9a)
          False →
            WalkUpUntilParent(gid, EditScope) → ancestor
            Branch (ancestor != ""):
              True → Return GetAllDescendantActors(ancestor)   ← sub-group trong scope → cả sub-group
              False → Return (empty)                 ← thuộc group khác ngoài scope → BỎ QUA

  False →                                            ← KHÔNG EDIT
    Branch (gid == ""):
      True → Return Make Array(Actor)                ← đồ rời → chính nó
      False → Return GetAllDescendantActors( GetGroupRoot(gid) )   ← đồ trong group → cả cây từ gốc
```

### 1.9 Hai stub dimming (RỖNG — MVP no-op)
```
ApplyEditModeVisual()   : (rỗng — chỉ có Function Entry → Return)
RemoveEditModeVisual()  : (rỗng — chỉ có Function Entry → Return)
```
> Để T3/T8 gọi sẵn. T9 sẽ đổ body. Đừng để trống execution gây lỗi — tạo function thật, body rỗng.

### TEST T1 (Print String, chưa cần UI)
Tạm dùng 1 phím debug hoặc gọi từ console để test:
1. Group phẳng 3 đồ (Sprint 3) → `Print GetAllDescendantActors(gid).Length` = 3. `Print GetGroupsInHierarchy(gid).Length` = 1.
2. `Print GetGroupRoot(gid)` = chính gid (flat).
3. `Print GetCurrentEditScope()` = "" (chưa edit).
→ **Làm xong báo tao** + dán 3 con số Print.

---

## T2 — ExpandSelectionWithGroups dùng ResolveSelectionUnit (KHÔNG sửa caller)

> Chỉ viết lại **body** của `ExpandSelectionWithGroups`. Caller (OnLMBReleased Then2, FinishBoxSelect) đã gọi hàm này → tự ăn logic mới.

### 2.1 Viết lại body
```
SET ActorsCopy = RawActors                           ← tránh pass-by-ref
CLEAR LocalResult                                    ← local array
GetCurrentEditScope() → Scope                        ← "" nếu không edit
ForEach ActorsCopy (Actor):
  Loop Body →
    ResolveSelectionUnit(Actor, Scope) → ForEach (Unit):
      Loop Body → Branch NOT Contains(LocalResult, Unit):
        True → ADD Unit → LocalResult
Completed → Return LocalResult
```

### 2.2 Đồng bộ Tick fallback (1 dòng — chống edge case)
Trong **Event Tick → Branch A** (nhánh `bIsPendingBoxSelect=True, bLMBHeld=False`, fallback khi OnLMBReleased lỡ): chỗ đang gọi `SelectSingleActor(PendingClickActor)` → đổi thành cùng đường resolve cho nhất quán nested/edit:
```
Hiện tại: IsValid(PendingClickActor) → True → SelectSingleActor(PendingClickActor) → CaptureSnapshot("Select")
Mới:      IsValid(PendingClickActor) → True →
            DeselectAll → ExpandSelectionWithGroups(Make Array(PendingClickActor)) → SelectActors(result)
            → CaptureSnapshot("Select") → SET PendingClickActor=None
```
> Đây là path hiếm (flick chuột cực nhanh). Đổi để khỏi lệch hành vi khi click group qua fallback.

### TEST T2
1. Không edit: click 1 đồ trong group phẳng → CẢ group chọn (giống Sprint 3, không regression).
2. Không edit: click đồ rời → chỉ 1 đồ.
3. Không edit: box bao 2/N đồ của group → cả group.
→ **Làm xong báo tao.**

---

## T3 — EnterEditMode / ExitEditModeOneLevel / ExitEditModeFull + GetEditBreadcrumb

> Tất cả là **Function** (không latent). Đây là phần quản lý scope.

### 3.1 `GetEditBreadcrumb() → String` (cho info bar đọc — R3 widget nhẹ)
```
SET Result = ""                                      ← local String
ForEach EditModeStack (Index, gid):
  Loop Body →
    FindGroupData(gid) → (data, _, bFound)
    Branch (bFound):
      True → Branch (Index == 0):
               True  → SET Result = data.GroupName
               False → SET Result = Result + " › " + data.GroupName
Completed → Return Result
```

### 3.2 `EnterEditMode(InGroupID : String)`
```
Branch (InGroupID == ""): True → Return
FindGroupData(InGroupID) → (_, _, bFound)
Branch (bFound == False): True → Return              ← group không tồn tại → bỏ
ADD InGroupID → EditModeStack                        ← PUSH
DeselectAll                                          ← vào edit = bắt đầu sạch
ApplyEditModeVisual                                  ← stub no-op
Broadcast OnEditModeChanged(True, InGroupID)
```

### 3.3 `ExitEditModeOneLevel()`  ← nút "↑ Lên 1 cấp" / phím tắt sau này
```
Branch (EditModeStack.Length == 0): True → Return    ← không edit → no-op
GetCurrentEditScope() → Exited                       ← = group đang đứng (trước khi pop)
EditModeStack → Last Index → REMOVE INDEX            ← POP

Branch (EditModeStack.Length == 0):
  True (đã thoát hẳn) →
    RemoveEditModeVisual
    DeselectAll                                      ← Q4
    GetAllDescendantActors(Exited) → LocalTree       ← Q3: cả cây vừa thoát
    Branch (LocalTree.Length > 0): True → SelectActors(LocalTree)   ← chọn lại cả group
    Broadcast OnEditModeChanged(False, "")           ← (cả nhánh Length==0 của LocalTree cũng merge về đây)
  False (còn cấp cha) →
    ApplyEditModeVisual                              ← cập nhật visual scope cha
    DeselectAll                                      ← Q4
    GetAllDescendantActors(Exited) → LocalTree2      ← chọn lại sub-group vừa thoát như 1 unit
    Branch (LocalTree2.Length > 0): True → SelectActors(LocalTree2)
    GetCurrentEditScope() → NewScope
    Broadcast OnEditModeChanged(True, NewScope)
```
> ⚠️ Cả nhánh `LocalTree.Length == 0` (False) cũng phải chạy tiếp tới Broadcast — KHÔNG dead-end.

### 3.4 `ExitEditModeFull()`  ← nút "✖ Thoát chỉnh"
```
Branch (EditModeStack.Length == 0): True → Return
EditModeStack → Get(0) → RootScope                   ← group ngoài cùng (luôn là gốc)
CLEAR EditModeStack
RemoveEditModeVisual
DeselectAll                                          ← Q4
GetAllDescendantActors(RootScope) → LocalTree
Branch (LocalTree.Length > 0): True → SelectActors(LocalTree)   ← chọn lại cả group gốc
Broadcast OnEditModeChanged(False, "")
```

### TEST T3 (gọi tạm bằng debug key, UI làm ở T5)
1. Group phẳng → click chọn cả group → gọi `EnterEditMode(GetGroupRoot(gid))` → `Print EditModeStack.Length` = 1, selection rỗng.
2. Click 1 đồ → chỉ 1 đồ chọn (vì `GetCurrentEditScope` != "" → ResolveSelectionUnit CASE member trực tiếp).
3. Gọi `ExitEditModeFull()` → `Print EditModeStack.Length` = 0, cả group chọn lại.
→ **Làm xong báo tao.**

---

## T4 — Trigger Enter từ selection (button-based MVP) + route

> MVP: trigger bằng NÚT (T5 dựng nút, gọi function ở đây). Phím tắt = TBD (KHÔNG Esc). Function dưới đây là cửa vào edit DUY NHẤT — nút và (sau này) phím đều gọi nó.

### 4.1 `TryEnterEditFromSelection()`
```
Branch IsValid(PrimarySelectedActor) == False: True → Return
Cast PrimarySelectedActor → GET GroupID → gid
Branch (gid == ""): True → Return                    ← đồ rời, không có group để vào
Branch (EditModeStack.Length >= 3): True → Return    ← giới hạn 3 cấp (UX)
GetCurrentEditScope() → Scope
Branch (Scope == ""):
  True → EnterEditMode( GetGroupRoot(gid) )          ← chưa edit → vào gốc của cây
  False →
    WalkUpUntilParent(gid, Scope) → Sub
    Branch (Sub != ""): True → EnterEditMode(Sub)    ← vào sub-group con trực tiếp của scope
    (else: đang chọn member trực tiếp / ngoài scope → không vào sâu hơn → no-op)
```
> Verify: ở cấp sâu nhất (chọn member trực tiếp), `Sub` = "" → no-op (đúng, không có gì để vào).

### 4.2 (HOÃN) Phím tắt
Khi mày quyết phím (KHÔNG Esc): tạo `IA_EditModeEnter` + `IA_EditModeExit` trong `LM_FurnitureInput`, route ở `BP_FoffPlayerController` (pattern Undo/Redo):
```
IA_EditModeEnter (Started) → GetAllActorsOfClass(InputManager)[0] → TryEnterEditFromSelection
IA_EditModeExit  (Started) → GetAllActorsOfClass(InputManager)[0] →
   Branch (EditModeStack.Length > 0): True → ExitEditModeOneLevel; False → (no-op / để cho deselect cũ)
```
> Verify phím Enter không bị search box / snap EditableText nuốt khi đang focus.

### TEST T4
Gọi `TryEnterEditFromSelection` từ debug key:
1. Chọn group → gọi → vào edit (Stack=1).
2. Chọn đồ rời → gọi → KHÔNG vào (guard gid=="").
→ **Làm xong báo tao.**

---

## T5 — Info Bar: nút Enter + hàng breadcrumb + nút Thoát + bind OnEditModeChanged

> Trong `WBP_MeshControls`. Layout cụ thể (Q11) mày tùy chỉnh; dưới đây là **wiring bắt buộc**.

### 5.1 Thêm widget
- `BTN_EnterEdit` (nút "✏️ Chỉnh nhóm") — đặt cạnh `HB_SelectionInfo`. Visible khi đang chọn group.
- `HB_EditModeBar` (HorizontalBox/Border, **Collapsed mặc định**) — hàng riêng, chứa:
  - `TXT_EditBreadcrumb` (TextBlock) — "✏️ Đang chỉnh: A › B"
  - `BTN_ExitOneLevel` (nút "↑") — gọi `ExitEditModeOneLevel`
  - `BTN_ExitFull` (nút "✖ Thoát") — gọi `ExitEditModeFull`

> ⚠️ `HB_EditModeBar` PHẢI là element RIÊNG, KHÔNG dùng chung `HB_SelectionInfo` (cái đó chỉ hiện khi ≥2 đồ; edit mode có thể active lúc chọn 0/1 đồ).

### 5.2 Event Construct — thêm bind (cạnh bind OnSelectionChanged có sẵn)
```
GetAllActorsOfClass(BP_FurnitureInputManager)[0] → Cast → InputRef
... (giữ nguyên bind OnSelectionChanged → OnSelectionChangedInfoBar) ...
+ Bind Event to OnEditModeChanged (Target=InputRef) → OnEditModeChangedInfoBar
+ Set Visibility(HB_EditModeBar, Collapsed)          ← ẩn ban đầu
```

### 5.3 Handler `OnEditModeChangedInfoBar(bActive, GroupID)`
```
Branch (bActive):
  True →
    Set Visibility(HB_EditModeBar, Visible)
    GetAllActorsOfClass(InputManager)[0] → Call GetEditBreadcrumb → BreadStr
    SET Text(TXT_EditBreadcrumb, "✏️ Đang chỉnh: " + BreadStr)
  False →
    Set Visibility(HB_EditModeBar, Collapsed)
```

### 5.4 BTN_EnterEdit OnClicked
```
GetAllActorsOfClass(InputManager)[0] → Call TryEnterEditFromSelection
```

### 5.5 BTN_ExitOneLevel / BTN_ExitFull OnClicked
```
BTN_ExitOneLevel → InputManager → ExitEditModeOneLevel
BTN_ExitFull     → InputManager → ExitEditModeFull
```

### 5.6 BTN_EnterEdit visibility — gắn vào handler selection có sẵn
Trong `OnSelectionChangedInfoBar` (đã có), sau khi tính `Primary.GroupID`:
```
Branch IsValid(Primary):
  True → Cast → GET GroupID → Branch (GroupID != ""):
           True  → Set Visibility(BTN_EnterEdit, Visible)
           False → Set Visibility(BTN_EnterEdit, Collapsed)
  False → Set Visibility(BTN_EnterEdit, Collapsed)
```
> MVP: nút hiện khi Primary có group. Bấm lúc ở cấp sâu nhất → `TryEnterEditFromSelection` no-op (chấp nhận). Tinh chỉnh sau nếu cần.

### 5.7 R2/R4 — Event Destruct
`HB_EditModeBar` / `TXT_EditBreadcrumb` là widget con, không hard ref actor → không cần clear đặc biệt. Giữ Event Destruct hiện có.

### TEST T5 — đây là test SLICE 1 đầy đủ ↓

---

## ✅ TEST SLICE 1 (flat edit mode) — PASS hết mới qua Slice 2

```
1. Group 3 đồ → click → cả 3 chọn → info bar "📦 Nhóm 1 (3)" + nút ✏️ hiện
2. Bấm ✏️ → vào edit → HB_EditModeBar hiện "✏️ Đang chỉnh: Nhóm 1", selection rỗng (HB_SelectionInfo ẩn)
3. Click 1 đồ trong group → CHỈ đồ đó chọn (gizmo 1 đồ)
4. Move đồ đó (Move mode) → chỉ nó di chuyển
5. Click đồ khác trong group → chuyển sang đồ đó (single)
6. Click chỗ trống / đồ ngoài group → selection rớt NHƯNG vẫn còn HB_EditModeBar (vẫn ở edit) [Q9b CLEAR]
7. Bấm ✖ Thoát → HB_EditModeBar ẩn → cả group chọn lại
8. REGRESSION: ngoài edit, đồ rời + box đồ rời + click group → OK như Sprint 3
```
→ **Làm xong báo tao + xác nhận từng case.**

---

# SLICE 2 — NESTED GROUP

---

## T6 — CreateGroup nhỗ trợ nested (sửa 1 dòng) + test nested

### 6.1 Sửa CreateGroup
Tại node `Make S_GroupData`, đổi `ParentGroupID`:
```
Hiện tại: Make S_GroupData(NewGID, name, ParentGroupID="", bIsLocked=false)
Mới:      Make S_GroupData(NewGID, name, ParentGroupID = GetCurrentEditScope(), bIsLocked=false)
```
> Ngoài edit → `GetCurrentEditScope()=""` → group gốc (như cũ). Trong edit g_A → ParentGroupID="g_A" → sub-group. KHÔNG đổi gì khác trong CreateGroup.

### TEST T6
```
1. Group cha (3 đồ) → bấm ✏️ vào edit g_A
2. Trong edit, chọn 2 đồ → Ctrl+G → tạo sub-group g_B (ParentGroupID="g_A")
   → Print: 2 đồ đó GroupID="g_B"; FindGroupData("g_B").ParentGroupID == "g_A"
3. Bấm ✖ Thoát → click 1 đồ bất kỳ → CẢ cây chọn (cả 3, qua GetGroupRoot→GetAllDescendantActors)
4. Bấm ✏️ vào g_A → click 1 đồ thuộc g_B → cả g_B chọn (1 unit, qua WalkUpUntilParent)
5. Bấm ✏️ lần nữa (đang chọn g_B) → vào g_B (Stack=[g_A,g_B], breadcrumb "Nhóm 1 › Nhóm 2")
6. Trong g_B, click 1 đồ → CHỈ 1 đồ
7. Thử vào cấp 4 → bị chặn (Stack>=3 guard)
8. ↑ Lên 1 cấp → về g_A (Stack=[g_A]), g_B chọn lại như 1 unit
```
→ **Làm xong báo tao + xác nhận.**

---

## T7 — Cleanup đúng cho nested: PruneEmptyGroups + UngroupActors deep

> 2 hàm Sprint 3 sẽ sai với nested. Sửa cả hai. Flat = giữ nguyên hành vi (no regression).

### 7.1 Sửa `PruneEmptyGroups` (Q6)
```
CLEAR LocalKeep                                      ← local array S_GroupData
ForEach Groups (g):
  Loop Body →
    GetAllDescendantActors(g.GroupID) → Length        ← THAY GetGroupChildren (xét cả subtree)
    Branch (Length > 0): True → ADD g → LocalKeep
Completed →
  SET Groups = LocalKeep
  SyncGroupsToContainer
```
> Lý do: group cha nested có 0 direct member nhưng subtree còn actor → phải GIỮ. `GetAllDescendantActors` nhìn cả cây nên cascade tự đúng 1 pass (vì build LocalKeep, không mutate Groups giữa chừng).

### 7.2 Viết lại `UngroupActors(InGroupID)` → deep ungroup cả cây (Q7)
```
Branch (InGroupID == ""): True → Return
GetGroupRoot(InGroupID) → Root                       ← luôn ungroup từ gốc cây

← B1: xả GroupID toàn bộ actor trong cây
GetAllDescendantActors(Root) → ForEach (actor):
  Loop Body → Cast → SET GroupID = ""
Completed →
  ← B2: gom ID mọi group trong cây cần xóa
  GetGroupsInHierarchy(Root) → ForEach (g):           ← build mảng String removeIDs
    Loop Body → ADD g.GroupID → LocalRemoveIDs
  Completed →
    ← B3: giữ lại các group KHÔNG nằm trong cây
    CLEAR LocalKeep
    ForEach Groups (g2):
      Loop Body → Branch NOT Contains(LocalRemoveIDs, g2.GroupID):
        True → ADD g2 → LocalKeep
    Completed →
      SET Groups = LocalKeep
      SyncGroupsToContainer
      CaptureSnapshot("Ungroup")                      ← SAU khi xóa, chạy 1 LẦN (ở Completed)
      SelectActors(SelectedActors)                    ← re-fire info bar
      Broadcast OnGroupDestroyed(Root)
```
> ⚠️ Reset đầu hàm: KHÔNG còn dùng `FoundIdx` (đã thay bằng build LocalKeep). CLEAR `LocalRemoveIDs` + `LocalKeep` đầu hàm.
> ⚠️ Toàn bộ B2/B3/capture nằm ở **Completed** của ForEach trước, KHÔNG Loop Body (bài học spam snapshot).
> Flat: `Root=gid`, `GetAllDescendantActors=GetGroupChildren`, `GetGroupsInHierarchy=[gid]` → giống hệt Sprint 3.

### 7.3 Caller `UngroupActors` (Ctrl+Shift+G) — KHÔNG đổi
Vẫn `IsValid(PrimarySelectedActor) → GET GroupID → Branch != "" → UngroupActors(GroupID)`. Hàm tự `GetGroupRoot` để lên gốc.

### TEST T7
```
1. Nested g_A{ g_B{3 đồ} } → chọn cả cây → Ctrl+Shift+G → 3 đồ GroupID="", Groups rỗng (cả g_A+g_B xóa), KHÔNG orphan
2. Nested → Delete 1 phần → các group rỗng-toàn-cây bị prune, group còn actor được giữ
3. FLAT regression: group phẳng → Ctrl+Shift+G → như Sprint 3; Delete group → prune đúng
```
→ **Làm xong báo tao.**

---

## ✅ TEST SLICE 2 — PASS mới qua Safety

Chạy lại T6 + T7 test. Xác nhận nested tạo/chọn/thoát/ungroup/prune đều đúng + flat không regression.

---

# SAFETY

---

## T8 — ValidateEditMode trong RestoreSnapshot

> Edit mode KHÔNG snapshot (D6). Sau Undo/Redo/Load, `EditModeStack` in-memory có thể trỏ tới group đã biến mất → phải validate.

### 8.1 `ValidateEditMode()` (Function)
```
CLEAR LocalValid                                     ← local array String
ForEach Loop WITH BREAK EditModeStack (gid):
  Loop Body →
    FindGroupData(gid) → (_, _, bFound)
    Branch (bFound):
      True  → ADD gid → LocalValid
      False → BREAK                                   ← group này mất → cắt từ đây lên (con cũng vô nghĩa)
Completed →
  SET EditModeStack = LocalValid
  Branch (EditModeStack.Length == 0):
    True  → RemoveEditModeVisual → Broadcast OnEditModeChanged(False, "")
    False → ApplyEditModeVisual  → Broadcast OnEditModeChanged(True, GetCurrentEditScope())
```

### 8.2 Chèn vào RestoreSnapshot
Vị trí: **SAU Step 5b** (Groups đã restore + SyncGroupsToContainer), **TRƯỚC Step 6b** (re-fire selection).
```
... Step 5b: CLEAR Groups → ADD Snapshot.Groups → SyncGroupsToContainer ...
+   ValidateEditMode()                               ← MỚI: sửa stack + broadcast edit state
... Step 6b: Branch SelectedActors.Length>0 → SelectActors / DeselectAll+DeactivateGizmo ...
... Step 7 : Broadcast OnRestoreCompleted ...
```
> Lý do thứ tự: ValidateEditMode đọc `Groups` → phải sau 5b. Nó tự broadcast OnEditModeChanged (cập nhật breadcrumb) trước khi 6b cập nhật count bar — 2 element UI độc lập.

### TEST T8 + TEST CUỐI 14 CASE
| # | Case | Kỳ vọng |
|---|---|---|
| 1 | Group 3 đồ → ✏️ | Vào edit, breadcrumb đúng |
| 2 | Trong edit, click 1 đồ | Chỉ 1 đồ |
| 3 | Trong edit, move 1 đồ | Chỉ nó di chuyển |
| 4 | Click ngoài scope khi edit | Selection rớt, VẪN ở edit (Q9b) |
| 5 | ✖ Thoát | Cả group chọn lại |
| 6 | Đồ rời → ✏️ (bấm) | Không vào (guard) |
| 7 | Nested Ctrl+G trong edit | Sub ParentGroupID đúng |
| 8 | Ngoài edit, click đồ trong sub | Chọn cả root (cả cây) |
| 9 | Enter root → click sub member | Chọn cả sub (1 unit) |
| 10 | Enter root → enter sub → click | Chỉ 1 đồ; breadcrumb 2 cấp |
| 11 | Vào cấp 4 | Bị chặn |
| 12 | Undo qua CreateGroup khi đang edit group đó | Tự thoát edit (ValidateEditMode) |
| 13 | Save → Load → click | Group/nested khôi phục, edit mode tự reset hợp lệ |
| 14 | Ungroup nested | Cả cây xả, không orphan |
| R | Regression S1–S3 | Single/box/group/replace/material nguyên vẹn |
→ **Làm xong báo tao + bảng PASS/FAIL.**

---

# POLISH (optional — chỉ làm nếu còn thời gian, báo cuhoang trước)

## T9 — Dimming: đổ body 2 stub
```
ApplyEditModeVisual():
  GetCurrentEditScope() → Scope
  Branch (Scope == ""): True → Return
  GetAllDescendantActors(Scope) → InScope            ← đồ TRONG scope
  GetAllActorsWithTag("FurnitureSpawned") → ForEach (a):
    Branch NOT Contains(InScope, a):                 ← đồ NGOÀI scope
      True → Cast → GET FurnitureMesh
             → Set Render Custom Depth = True
             → Set Custom Depth Stencil Value = 200  ← reserve
  → (M_SelectionOutline thêm nhánh Stencil==200 → desaturate/tối)

RemoveEditModeVisual():
  GetAllActorsWithTag("FurnitureSpawned") → ForEach (a):
    ← chỉ tắt đồ đang ở Stencil 200, KHÔNG đụng 255/254
    Cast → GET FurnitureMesh → GET Custom Depth Stencil Value
    Branch (== 200): True → Set Render Custom Depth = False
```
> Cần sửa material `M_SelectionOutline` thêm nhánh Stencil 200. Test kỹ máy yếu trước khi ship.

---

## 5. DEVIATIONS cần ghi (file DEVIATIONS.md)

| Mục | Plan v1.0 nói | Thực tế | Lý do |
|---|---|---|---|
| Trigger | Enter key + nút | NÚT-only cho MVP, phím TBD (KHÔNG Esc) | Esc đang là thoát PIE |
| ExitEditMode re-select | GetGroupChildren→Get(0)→Expand | GetAllDescendantActors(Exited) trực tiếp | GetGroupChildren rỗng với nested thuần |
| Q9b | (chưa định) | CLEAR selection (giữ edit), không no-op | tránh đụng caller defer mong manh |
| PruneEmptyGroups | GetGroupChildren | GetAllDescendantActors (cả subtree) | chống prune oan group cha nested |
| UngroupActors | xóa 1 group | deep ungroup cả cây | chống orphan sub-group |

---

## 6. BRIDGE COMBO (Sprint 5) — readiness sau T1–T8

Sau Sprint 4, group tree fully serializable. Combo save dùng:
- `GetAllDescendantActors(rootGID)` → members
- `GetGroupsInHierarchy(rootGID)` → cấu trúc group lồng
- `CalculateCenter` (S1) → relLoc
- remap GroupID → token khi save; `GenerateGroupID` (S3) khi spawn
KHÔNG cần thêm helper mới cho combo structure ở S5.

---

## 7. DOCS CẬP NHẬT CUỐI SPRINT (version + ngày + giờ + phút)
- `Session_State.md` — trạng thái Sprint 4 done + bug nếu có.
- `BP_FurnitureInputManager.md` → v1.7 (EditModeStack, 6 helper, ResolveSelectionUnit, Enter/Exit, sửa PruneEmptyGroups/UngroupActors, dispatcher OnEditModeChanged).
- `BP_UndoManager.md` → ValidateEditMode trong RestoreSnapshot.
- `WBP_MeshControls.md` → v1.5 (BTN_EnterEdit, HB_EditModeBar, bind OnEditModeChanged).
- `Blueprint_Logic.md` — node flow ResolveSelectionUnit + Enter/Exit.
- `DEVIATIONS.md` — mục 5 ở trên.
- `09_AI_Implementation_Rules.md` — thêm node mới (ForEach With Break cho ValidateEditMode, Last Index→Get).

---

## 8. RỦI RO / VERIFY KHI CODE
- Đệ quy BP Function (`GetAllDescendantActors`, `GetGroupsInHierarchy`) — verify local var độc lập mỗi frame; sai → iterative worklist (báo cuhoang).
- `ForLoop 0..9` + Return node trong Loop Body — verify Return thoát hàm ngay (đúng) chứ không chỉ break loop.
- `WalkUpUntilParent` với data lỗi (ParentGroupID vòng) — depth guard 10 chặn.
- Bug fail 3 lần → STOP, báo cuhoang, thu hẹp scope.
