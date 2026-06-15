# Sprint 4 — BUG FIX & UX EXECUTION (cho Sonnet 4.6)
**Phiên bản:** 1.0 | **Tạo:** 14/06/2026 — (Opus 4.8) | **Đọc kèm:** 09 (v2), 10 (v2), Blueprint_Logic v1.4, BP_FurnitureInputManager v1.8
**Mục tiêu:** Đóng Sprint 4 — fix 4 lỗi + 1 feature + 1 bug undo, rồi chạy test suite. SAU đó mới sang Gate 1.

---

## ⚠️ ĐỌC TRƯỚC KHI BẮT ĐẦU (Sonnet)

1. File 09 v2 vừa cập nhật: **Q8 Self-Check Gate bắt buộc** — mỗi flow phải ghi 1 dòng kết quả soi trước khi đưa ra.
2. File 10 v2: **Luật 6A** (mỗi fix phải có đường ngược, đã test) + **Luật 6B** (đối xứng cấu trúc).
3. Làm **TỪNG TASK MỘT**, confirm "xong" rồi mới sang task kế. KHÔNG đổ nhiều task.
4. Thứ tự bắt buộc: **A12-chẩn đoán → F1 → F2 → F3 → F4 → A12-fix → TEST**.
   (A12 tách 2 pha vì pha fix phụ thuộc log từ pha chẩn đoán.)
5. cuhoang KHÔNG cần screenshot — mô tả node flow bằng lời, notation: `NodeA.Pin ●→ NodeB.Pin` (data), `NodeA ▶→ NodeB` (exec).

---

# ═══════════ A12 (PHA 1) — CHẨN ĐOÁN UNDO EDIT MODE ═══════════

**Triệu chứng:** Đang edit group G1 → Undo về trước khi tạo G1 → edit mode bị sai (chưa rõ hướng sai).

**Task pha này KHÔNG fix — chỉ thu log.** cuhoang đã được yêu cầu đặt 3 Print trong `ValidateEditMode` (BP_UndoManager). Nếu chưa đặt, hướng dẫn đặt:

- **Print 1** — sau `Branch(IsValid(InputRef))` nhánh True, trước For Each:
  `"VALIDATE START stack=" + InputRef.EditModeStack.Length`
- **Print 2** — sau `SET InputRef.EditModeStack = LocalValid`, trước Branch cuối:
  `"VALIDATE AFTER stack=" + InputRef.EditModeStack.Length`
- **Print 3a** — nhánh True (Length==0), SAU Broadcast: `"VALIDATE -> EXIT (broadcast False)"`
- **Print 3b** — nhánh False, SAU Broadcast: `"VALIDATE -> STAY (broadcast True)"`

**Setup test:** spawn 3 đồ → Ctrl+G tạo G1 → ✏️ enter edit G1 → Undo.

**Yêu cầu cuhoang trả về:**
1. Edit mode bar sau Undo: còn hiện hay ẩn?
2. 3 đồ sau Undo: đủ 3 không? vị trí đúng? mất/nhân đôi?
3. Có Accessed None (đỏ) trong log?
4. Dán nguyên văn 4 dòng Print.

→ **STOP. Báo cuhoang chạy test, gửi log. Pha fix (A12-fix) làm SAU, dựa trên log này.**

> Lý do chẩn đoán đầu tiên: nếu log lộ vấn đề sâu trong RestoreSnapshot/ValidateEditMode, các fix F3/F4 (đụng group structure) xây lên trên cần biết sớm.

---

# ═══════════ F1 — INFO BAR HIỆN ĐÚNG TÊN UNIT ═══════════

## Mục tiêu
Info bar (`TXT_SelectionInfo` trong WBP_MeshControls) hiện tên **đơn vị (unit) đang chọn**, không phải group con trực tiếp của Primary.

## Hành vi đúng (đã chốt với cuhoang)
| Tình huống | Info bar hiện |
|---|---|
| Ngoài edit, chọn đồ thuộc group | `📦 [tên ROOT] (N)` |
| Trong edit, chọn member trực tiếp của scope / đồ rời | `N vật thể` |
| Trong edit, chọn member của sub-group con | `📦 [tên sub-group] (N)` |
| Multi đồ rời (ngoài edit) | `N vật thể` |

## Đường xuôi + ngược (Luật 6A)
- Xuôi: chọn unit → info bar đúng tên.
- Ngược: deselect / chọn < 2 đồ → info bar Collapsed (đã có sẵn, giữ nguyên).

## ⭐ Kiến trúc: TÁCH FUNCTION (Luật B + R3)
Logic resolve tên unit **không đặt trong widget/event** — đẩy về **Function trong BP_FurnitureInputManager** (nơi đã có sẵn GetGroupRoot/WalkUpUntilParent/FindGroupData). Widget chỉ gọi 1 node.

### BƯỚC 1 — Tạo Function `GetSelectionUnitLabel` trong BP_FurnitureInputManager
**Inputs:** `Primary` (BP_FurnitureActor), `Count` (Integer)
**Output:** `Label` (String)
**Local vars** (hợp lệ vì đây là FUNCTION): `gid`, `scope`, `subUnit`, `rootGID` (String); `data` (S_GroupData); `bFound` (Bool)

```
Entry:
IsValid(Primary)==False ▶→ Return (Count + " vật thể")
Cast Primary → BP_FurnitureActor:
   Cast Failed ▶→ Return (Count + " vật thể")
   Success: .GroupID ●→ SET gid
GetCurrentEditScope() ●→ SET scope

Branch(scope != ""):                              ← TRONG EDIT
  True:
    Branch(gid == "" OR gid == scope):            ← member trực tiếp / đồ rời
      True  ▶→ Return (Count + " vật thể")
      False ▶→ WalkUpUntilParent(gid, scope) ●→ SET subUnit
              Branch(subUnit == ""):
                True  ▶→ Return (Count + " vật thể")
                False ▶→ FindGroupData(subUnit) → (data, _, bFound)
                        Branch(bFound):
                          True  ▶→ Return ("📦 " + data.GroupName + " (" + Count + ")")
                          False ▶→ Return (Count + " vật thể")
  False:                                          ← NGOÀI EDIT
    Branch(gid == ""):
      True  ▶→ Return (Count + " vật thể")
      False ▶→ GetGroupRoot(gid) ●→ SET rootGID
              FindGroupData(rootGID) → (data, _, bFound)
              Branch(bFound):
                True  ▶→ Return ("📦 " + data.GroupName + " (" + Count + ")")
                False ▶→ Return (Count + " vật thể")
```
> Mỗi nhánh **Return ngay** (early return) → không tích lũy độ sâu thật, không dead-end. Đây là ngoại lệ hợp lệ của Luật B (Function thuần early-return, không phải widget graph).

### BƯỚC 2 — Sửa `OnSelectionChangedHandler` (event) trong WBP_MeshControls
Đây là **EVENT** (custom event, bind từ OnSelectionChanged) → KHÔNG tạo Local Variable ở đây (L9). Gọi Function inline, không cần SET vào local var.

Trong `Sequence.Then 1` (phần info bar), thay toàn bộ logic cũ:
```
Sequence.Then 1 ▶→ Branch(Actors.Length >= 2):
  False ▶→ SetVisibility(HB_SelectionInfo, Collapsed)
  True  ▶→ SetVisibility(HB_SelectionInfo, Visible)
        ▶→ GetAllActorsOfClass(BP_FurnitureInputManager) ●→ Get(0) ●→ Cast
            ●→ GetSelectionUnitLabel(Primary, Actors.Length) ●→ ReturnValue
            ●→ SetText(TXT_SelectionInfo, ReturnValue)
```
> `Then 2` (BTN_EnterEdit visibility) GIỮ NGUYÊN. `Actors.Length` đọc trực tiếp từ pin event, không cần temp var.

## Self-check (Q8) — Sonnet ghi khi trình bày
`Function GetSelectionUnitLabel → local var hợp lệ. IsValid(Primary) ✓. Mỗi Branch early-return, không dead-end. Không latent. Event chỉ gọi inline, không local var (L9 ✓).`

## Bài học áp dụng
- L1 (IsValid Primary), L9 (event không local var → đẩy Function), R3 (widget nhẹ).

## Test F1
1. Ngoài edit, click đồ trong Root group → `📦 [Root] (N)`.
2. Trong edit Root, click member trực tiếp → `N vật thể`.
3. Trong edit Root, click member của sub-group → `📦 [sub-group] (N)`.
4. Deselect → info bar ẩn.

→ **Làm xong báo tao. Test 4 case trên.**

---

# ═══════════ F2 — TÊN GROUP COUNTER MONOTONIC ═══════════

## Mục tiêu
Đổi tên group từ `"Nhóm " + (Groups.Length+1)` (loạn khi xóa group) sang **biến đếm chỉ-tăng**.

## BƯỚC 1 — Thêm Class Variable trong BP_FurnitureInputManager
`GroupNameCounter` : Integer | Default = 1 | **SaveGame = TRUE** (R5: lưu để không reset)

## BƯỚC 2 — Sửa CreateGroup (đoạn auto-name)
```
Auto-name = "Nhóm " + GroupNameCounter           ← thay (Groups.Length+1)
... (tạo group xong) ...
SET GroupNameCounter = GroupNameCounter + 1       ← tăng SAU khi đặt tên, dùng output pin của SET (L4)
```
> Xóa/ungroup group **KHÔNG** đụng GroupNameCounter → "Nhóm 5" mãi là Nhóm 5, không trùng.

## Đường xuôi + ngược (Luật 6A)
- Xuôi: tạo group → tên tăng dần, không trùng.
- Ngược: ungroup → counter giữ nguyên (không giảm). Đúng — không bao giờ tái dùng số.

## Self-check (Q8)
`SET GroupNameCounter dùng output pin của SET (L4). SaveGame=true (R5). Không Branch lồng.`

## Test F2
1. Tạo Nhóm 1, 2, 3 → ungroup Nhóm 2 → tạo group mới → phải là **Nhóm 4** (không phải Nhóm 3 trùng).
2. Save → Load → tạo group mới → số tiếp tục, không reset về 1.

→ **Làm xong báo tao. Test 2 case.**

---

# ═══════════ F3 — CREATEGROUP BOTTOM-UP NEST (⚠ RỦI RO CAO NHẤT) ═══════════

## Mục tiêu (Luật 6B — đối xứng cấu trúc)
Chọn nhiều **group** rồi Create Group → group mới thành **CHA** của các group đó (nest), KHÔNG flatten thành phẳng.

## Root cause hiện tại
`CreateGroup` gom **actor-lá** (`ForEach SelectedActors → SET GroupID = NewGID`) → xóa cấu trúc sub-group. Phải gom **đơn vị chọn** (group/actor rời).

## ⚠ VERTICAL SLICE TRƯỚC (Cơ chế 2) — làm slice này validate rủi ro NGAY
> Trước khi code đầy đủ: tạo 3 group A-1/A-2/A-3 (mỗi cái 2 đồ) → chọn cả 3 → Create Group → kiểm cây ra: A chứa 3 sub-group? Nếu slice OK → hoàn thiện. Nếu fail → STOP, báo cuhoang (3-Strike Protocol).

## BƯỚC 1 — Tạo Function `ComputeSelectionUnits` trong BP_FurnitureInputManager
**Inputs:** `InActors` (Array<BP_FurnitureActor>)
**Outputs:** `OutGroupUnits` (Array<String> — GroupID các group-đơn-vị), `OutLooseActors` (Array<BP_FurnitureActor>)
**Local vars:** `scope` (String), `gid` (String), `unitGID` (String), `ActorsCopy` (Array — copy InActors, L: array pass-by-ref)

```
SET ActorsCopy = InActors                          ← copy local (array pass-by-ref)
CLEAR OutGroupUnits ; CLEAR OutLooseActors          ← clear đầu hàm (L: persistent var)
GetCurrentEditScope() ●→ SET scope

ForEach ActorsCopy (Actor):
  IsValid(Actor)==False → (skip, không nối Return)
  Cast Actor → BP_FurnitureActor → .GroupID ●→ SET gid

  Branch(gid == ""):                                ← actor rời
    True → Branch NOT Contains(OutLooseActors, Actor):
              True → ADD Actor → OutLooseActors
    False →
      Branch(scope == ""):                          ← ngoài edit
        True → GetGroupRoot(gid) ●→ SET unitGID
        False → Branch(gid == scope):               ← trong edit
                  True → (member trực tiếp scope) → coi như loose:
                         Branch NOT Contains(OutLooseActors, Actor): True → ADD Actor → OutLooseActors
                         → (continue loop, KHÔNG set unitGID)
                  False → WalkUpUntilParent(gid, scope) ●→ SET unitGID
      (nếu có unitGID hợp lệ) Branch(unitGID != "" AND NOT Contains(OutGroupUnits, unitGID)):
              True → ADD unitGID → OutGroupUnits
Completed → (return 2 mảng qua output pin)
```
> ⚠ Đây là Function với 3 tầng Branch — đúng ra Luật B đòi tách. Nhưng đây là logic phân loại tuyến tính trong loop (không phải execution lồng tích lũy). Sonnet: nếu thấy khó ráp, BÁO cuhoang để tách nhỏ hơn, đừng cố nhồi.

## BƯỚC 2 — Viết lại đoạn gán trong CreateGroup
Thay `ForEach SelectedActors → SET GroupID = NewGID` bằng:
```
(sau khi đã Make S_GroupData NewGID + ADD Groups + SyncGroupsToContainer)

ComputeSelectionUnits(SelectedActors) → (GroupUnits, LooseActors)

ForEach GroupUnits (childGID):                      ← reparent GROUP (giữ con bên trong)
  FindGroupData(childGID) → (data, idx, bFound)     ← cần rebuild vì FindGroupData không expose Index ổn định
  → rebuild Groups: group nào GroupID==childGID → MAKE S_GroupData(childGID, data.GroupName, NewGID, data.bIsLocked); else giữ nguyên
  (dùng pattern rebuild B2 như trong UngroupActors — KHÔNG Set Array Elem)

ForEach LooseActors (Actor):                        ← reparent ACTOR rời
  Cast → SET GroupID = NewGID

→ SyncGroupsToContainer
→ CaptureSnapshot("CreateGroup")                    ← 1 lần, SAU khi xong (L3)
→ Broadcast OnGroupCreated(NewGID)
→ SelectActors(SelectedActors)
```

## BƯỚC 3 — Đổi guard
```
Guard cũ: SelectedActors.Length >= 2
Guard mới: (GroupUnits.Length + LooseActors.Length) >= 2     ← ≥ 2 ĐƠN VỊ, không phải 2 actor
```
> Chọn 1 group 10 đồ = 1 đơn vị → KHÔNG tạo nhóm lồng vô nghĩa.
> ⚠ Guard mới cần ComputeSelectionUnits chạy TRƯỚC guard → gọi sớm, SET temp, guard đọc temp (L: impure timing).

## Đường xuôi + ngược (Luật 6A)
- Xuôi (bottom-up): chọn 3 group → A chứa 3 sub-group.
- Ngược: Ctrl+Shift+G trên A → peel 1 cấp → A-1/A-2/A-3 về trạng thái trước (đã có UngroupActors peel-one-level, kiểm regression).

## Self-check (Q8) — Sonnet ghi
`ComputeSelectionUnits là Function (local var OK). ActorsCopy = copy InActors (array ref). CLEAR output đầu hàm. Contains-guard chống trùng. Reparent group dùng rebuild (không Set Array Elem). CaptureSnapshot 1 lần SAU (L3). Guard đọc temp từ ComputeSelectionUnits.`

## Bài học áp dụng
- Luật 6B (gom đơn vị, không gom lá), L3 (CaptureSnapshot sau, 1 lần), array pass-by-ref (copy local), rebuild thay Set Array Elem, impure timing (gọi sớm SET temp).

## Test F3 (đủ ĐƯỜNG — Luật 6B)
1. **Bottom-up:** 3 group riêng A-1/A-2/A-3 → chọn → Create Group → **A chứa 3 sub-group** ✓
2. **Top-down (regression):** A(10) → enter edit → tạo sub → vẫn đúng ✓
3. **Trộn:** 2 group + 3 đồ rời → Create Group → A chứa 2 sub-group + 3 đồ trực tiếp ✓
4. **1 đơn vị:** chọn 1 group 10 đồ → Create Group → KHÔNG tạo nhóm lồng (guard chặn) ✓
5. **Ngược:** Ctrl+Shift+G trên A → peel đúng 1 cấp ✓

→ **Làm slice trước (case 1). Slice OK → hoàn thiện + test 5 case. Slice fail → STOP báo tao.**

---

# ═══════════ F4 — SPAWN TRONG EDIT → TỰ JOIN SCOPE ═══════════

## Mục tiêu (deviation Q13 — GHI DEVIATIONS.md NGAY)
Đang edit group → spawn đồ mới (drag card / copy-paste / duplicate / cut-paste) → đồ mới `GroupID = GetCurrentEditScope()`.

> ⚠ DEVIATIONS.md: `14/06 | F4 | Q13 nói spawn-in-edit GroupID="" | đổi: spawn-in-edit GroupID=scope | cuhoang yêu cầu UX nhất quán`

## ⚠ Q3 — CẦN cuhoang XÁC NHẬN TRƯỚC
Sonnet KHÔNG bịa tên function spawn. Hỏi cuhoang liệt kê **các điểm actor được tạo**:
- Drag furniture card → function nào? (vd SpawnFurnitureCopy?)
- Copy-Paste → function nào?
- Duplicate → function nào? (memory ghi `DuplicateMesh`)
- Cut-Paste → function nào?
Và **nơi chính xác** actor vừa spawn có ref (sau Add Tag "FurnitureSpawned").

## Pattern chèn (áp cho TỪNG điểm spawn, sau khi có tên thật)
```
(sau khi spawn NewActor + Add Tag "FurnitureSpawned", TRƯỚC khi select)
GetCurrentEditScope() ●→ Scope
Branch(Scope != ""):
  True → Cast NewActor → BP_FurnitureActor → SET GroupID = Scope
  False → (để trống — giữ GroupID="" như cũ)
```

## Đường xuôi + ngược (Luật 6A)
- Xuôi: spawn trong edit → đồ thuộc scope.
- Ngược: Undo spawn → đồ biến mất, group không vỡ (kiểm N6).

## Self-check (Q8)
`IsValid/Cast NewActor trước SET (L1, L6). Branch False để trống đúng (L10-style, không ghi đè). GetCurrentEditScope đọc tươi mỗi spawn.`

## Test F4 (N1–N8)
1. N1 drag card trong edit G1 → đồ mới GroupID=G1.
2. N2 copy-paste trong edit → GroupID=G1.
3. N3 duplicate trong edit → GroupID=G1.
4. N4 cut-paste trong edit → GroupID=G1.
5. N5 ngoài edit spawn → GroupID="" (cũ giữ nguyên).
6. N6 Undo spawn-in-edit → đồ mất, G1 còn.
7. N7 spawn trong G1 → thoát edit → click đồ mới → chọn cả G1.
8. N8 nested: edit Sub1 → spawn → GroupID=Sub1 (không phải Root).

→ **Hỏi cuhoang tên function trước. Có tên rồi → chèn từng điểm → test N1–N8.**

---

# ═══════════ A12 (PHA 2) — FIX UNDO EDIT MODE ═══════════
> Pha này CHỈ làm sau khi có log từ A12-Pha-1. Hướng fix tùy log:
- Nếu **stack không clear** (Print 2 vẫn còn G1): lỗi ở vòng For Each ValidateEditMode — FindGroupData trả nhầm bFound=True dù G1 đã xóa → kiểm Groups đã CLEAR + ADD Snapshot.Groups TRƯỚC ValidateEditMode chưa (thứ tự Step 5b → ValidateEditMode).
- Nếu **stack clear nhưng bar vẫn hiện** (Print 3a chạy mà UI không ẩn): lỗi ở handler OnEditModeChangedInfoBar hoặc RemoveEditModeVisual.
- Nếu **Accessed None**: thiếu IsValid đâu đó trong ValidateEditMode/RestoreSnapshot.

→ Opus sẽ thiết kế fix cụ thể khi có log. Sonnet KHÔNG đoán mò (3-Strike).

---

# ═══════════ TEST SUITE CUỐI — ĐÓNG SPRINT 4 ═══════════
Chạy đủ trước khi tuyên bố Sprint 4 done. Nhóm A–F (30 case) + bổ sung:
- **Nesting cap đầy đủ:** Root→Sub1→Sub2→Sub3, kiểm enter tới cấp 3 bị chặn, breadcrumb đúng từng cấp, ↑1cấp / ✖Thoát đúng.
- **Sub-sub-group ungroup (D3):** ungroup SubA chứa SubSubA → SubSubA.ParentGroupID về cha (không orphan).
- **F1–F4 test cases** ở trên.

Sau khi PASS hết:
- Cập nhật: Session_State, PROGRESS, DEVIATIONS, WBP_MeshControls (v1.6), BP_FurnitureInputManager (v1.9), Blueprint_Logic (v1.5).
- Ghi version + ngày + giờ + phút.

---

## TÓM TẮT THỨ TỰ THỰC THI
```
A12-chẩn đoán (thu log, STOP báo)
  → F1 Info bar (Function GetSelectionUnitLabel)
  → F2 Tên group counter
  → F3 CreateGroup bottom-up (slice trước! rủi ro cao)
  → F4 Spawn join scope (hỏi tên function trước)
  → A12-fix (dựa log)
  → TEST SUITE → đóng Sprint 4
```
