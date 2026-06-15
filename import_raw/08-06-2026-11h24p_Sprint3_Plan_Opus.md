# Sprint 3 — Group Cơ Bản (Plan chi tiết — Opus 4.8)
**Phiên bản:** 1.0 | **Ngày:** 08/06/2026 — 11:24 ICT | Lighting_Mnger UE5.5.4
**Thay thế:** phần Sprint 3 trong plan_v3/04_Sprint_Details.md (giữ file gốc làm reference)

---

## 0. NGUYÊN TẮC NỀN

> **Một group, khi đã chọn, CHÍNH LÀ một multi-selection.**

Sprint 3 = 3 thứ: (1) **data** nhớ đồ nào thuộc nhau, (2) **1 resolver** biến "1 đồ click" → "cả group", (3) **persistence** (EMS + snapshot). Transform/Copy/Delete/Nudge của group → tái dùng 100% từ Sprint 1 (Pivot + UpdateGizmo + SelectActors). KHÔNG viết code transform group mới.

### Quyết định kiến trúc đã chốt (từ 6 câu hỏi)
| # | Quyết định | Lý do |
|---|---|---|
| Q1 | 1 function `ExpandSelectionWithGroups` cho cả click + box | Không rải logic, future-proof nested |
| Q2 | Giữ BP_GroupsContainer, sync sau mỗi group-op (không mỗi frame) | Container chỉ chứa data → EMS-safe; InputManager giữ runtime ref → KHÔNG để EMS quản lý |
| Q3 | GroupID = `"g_" + GUID`; paste Sprint 3 = đồ rời | Collision-safe; ClipboardEntry không có GroupID |
| Q4 | BỎ dialog, auto-name `"Nhóm N"` | Ít thao tác; rename ở Scene Manager (Sprint 6) |
| Q5 | Transform group = tái dùng multi-select | Pivot Sprint 1 đã lo hết |
| Q6 | Box bao partial → chọn cả group | Nhất quán click; dùng lại resolver Q1 |

### Cắt khỏi plan gốc
- ❌ WBP_GroupNameDialog (Q4)
- ❌ MoveGroup/RotateGroup/ScaleGroup riêng (Q5 — dùng Pivot)
- ❌ Sync mỗi frame (Q2 — chỉ sync sau group-op)

---

## 1. LEARNINGS BẮT BUỘC ÁP DỤNG (đã trả giá trước đây)

- **Event không có Local Variable** → logic phức tạp đặt trong **Function**, Event chỉ gọi.
- **CaptureSnapshot SAU action** (assign GroupID xong → THEN snapshot). KHÔNG trong helper.
- **CLEAR array/temp ở ĐẦU function** nếu nó là class var hoặc tái dùng (chống stale — bài học TempSelectedIndices).
- **IsValid trước mọi Object access**; **tất cả nhánh Branch merge về cuối**.
- **Code chạy 1 lần → nối Completed của ForEach, KHÔNG Loop Body** (bài học DuplicateMesh).
- **Array pass-by-reference** → CLEAR + ForEach ADD nếu cần bản độc lập.
- **Latent node chỉ trong Custom Event**, KHÔNG trong Function.
- **GET Tags → ADD → SET** (EMS track state qua Tags).
- **Destroy Actor target = phần tử đang duyệt**, KHÔNG để trống.
- **BP_FurnitureActor: Cast → GET FurnitureMesh**, KHÔNG Get Static Mesh Component.
- **Toggle check / guard đặt đúng thứ tự** (bài học CB_Replace: toggle trước guard).
- **KHÔNG thêm var furniture vào BP_FoffPlayerController** — Ctrl+G/Ctrl+Shift+G qua IA trong furniture mapping context.

---

## 2. DATA STRUCTURES

### S_GroupData (struct mới)
```
GroupID       : String
GroupName     : String
ParentGroupID : String      ← "" ở Sprint 3 (nested để Sprint 4)
bIsLocked     : Boolean      ← False (lock để Sprint 6)
```

### BP_FurnitureActor — thêm field
```
GroupID : String   ← SaveGame, default ""
```

### S_FurniturePlacement — thêm field
```
GroupID : String   ← MỚI (snapshot lưu group của từng đồ)
```

### S_SceneSnapshot — mở rộng
```
Version : Integer = 3        ← bump từ 2
Groups  : Array<S_GroupData> ← MỚI
(EditingGroupID để Sprint 4)
```

---

## 3. VERTICAL SLICE — LÀM TRƯỚC TIÊN (kill EMS risk)

Rủi ro lớn nhất Sprint 3 (file 10): **EMS save group**. Validate trước khi xây tiếp.

```
Slice = T1 + T2 + T3 + T4 + CreateGroup tối giản (gán GroupID cho SelectedActors, auto-name, chưa cần Ctrl+G/snapshot)

TEST SLICE:
1. Spawn 2 đồ → multi-select → gọi CreateGroup (tạm trigger bằng 1 nút test/console)
2. Verify: 2 đồ có cùng GroupID, Groups array có 1 entry
3. Save scene → tắt PIE → mở lại → Load
4. Verify SAU LOAD:
   - Có ĐÚNG 1 BP_GroupsContainer (không nhân đôi)
   - Groups array khôi phục (GroupName đúng)
   - 2 đồ vẫn có GroupID đúng (từ SaveGame field của actor)
   - InputManager.Groups sync đúng từ container
```

Pass slice → mới đi tiếp T5+. Fail → xử lý singleton/sync trước (Plan B: nếu EMS nhân đôi container → singleton guard mạnh hơn, hoặc lưu Groups qua EMS custom-save thay actor).

---

## 4. TASK BREAKDOWN

### T1 — Struct S_GroupData (10 phút)
Tạo struct với 4 field như mục 2.

### T2 — BP_FurnitureActor + GroupID (10 phút)
Thêm `GroupID : String` (SaveGame, default ""). Compile.

### T3 — BP_GroupsContainer (45 phút)
```
Parent: Actor (KHÔNG StaticMeshActor — không cần mesh)
Interface: EMSActorSaveInterface
Variable: Groups : Array<S_GroupData>  (SaveGame)

Event BeginPlay:
  ← Singleton guard (chống nhân đôi khi EMS load):
  Get All Actors With Tag("FurnitureGroupsContainer") → Length
  Branch Length > 0:  (đã có container khác)
    True → Destroy Actor(Self) → return
    False → GET Tags → ADD "FurnitureGroupsContainer" → SET Tags

Event ActorLoaded (EMSActorSaveInterface):
  Wait For Save or Load Completed (Load Only) → On Completed:
    Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → IsValid
      True → SET FurnitureInputManager.Groups = Self.Groups   (sync vào in-memory truth)
```
Spawn 1 instance trong Level BP BeginPlay (thêm vào spawn order, SAU InputManager).

### T4 — Groups var + Sync trong BP_FurnitureInputManager (30 phút)
```
Variable: Groups : Array<S_GroupData>   ← in-memory source of truth

Function SyncGroupsToContainer():
  Get All Actors With Tag("FurnitureGroupsContainer") → Get(0) → IsValid
    True → Cast BP_GroupsContainer → SET Groups = Self.Groups
```
End Play: CLEAR Groups (chống stale giữa PIE).

### T5 — Helper Functions (1 giờ) ⭐ KEYSTONE
Tất cả là **Function** (không latent).

```
GenerateGroupID() → String:
  New Guid → To String → "g_" + result
  (nếu không có New Guid node: dùng Now→ToString + counter class var)

GetGroupChildren(InGroupID: String) → Array<BP_FurnitureActor>:
  CLEAR LocalChildren (local array)          ← clear đầu hàm
  Branch InGroupID == "": True → Return (empty)
  Get All Actors With Tag("FurnitureSpawned") → ForEach:
    Cast BP_FurnitureActor → IsValid →
      Branch GroupID == InGroupID: True → ADD LocalChildren
  Return LocalChildren

FindGroupData(InGroupID: String) → S_GroupData, bFound: Boolean:
  ForEach Groups: Branch GroupID == InGroupID → True: Return (entry, True)
  Return (default, False)

ExpandSelectionWithGroups(RawActors: Array<BP_FurnitureActor>) → Array<BP_FurnitureActor>:
  ← Biến danh sách đồ "thô" thành danh sách đã mở rộng theo group
  SET ActorsCopy = RawActors   (tránh pass-by-ref)
  CLEAR LocalResult (local array)             ← clear đầu hàm
  ForEach ActorsCopy (RawActor):
    IsValid(RawActor) →
      Cast → GET GroupID → LocalGID
      Branch LocalGID == "":
        True  → Branch NOT Contains(LocalResult, RawActor) → ADD RawActor
        False → GetGroupChildren(LocalGID) → ForEach (Child):
                  Branch NOT Contains(LocalResult, Child) → ADD Child
  Return LocalResult

PruneEmptyGroups():
  ← Xóa S_GroupData không còn member nào (sau delete group)
  CLEAR LocalKeep (local array S_GroupData)
  ForEach Groups (g):
    GetGroupChildren(g.GroupID) → Length
    Branch Length > 0: True → ADD g to LocalKeep
  SET Groups = LocalKeep
  SyncGroupsToContainer
```

### T6 — CreateGroup + Ctrl+G (45 phút)
```
Function CreateGroup() → String (GroupID):     ← KHÔNG nhận tên (auto)
  Branch SelectedActors.Length < 2: True → Return ""

  newGID = GenerateGroupID()
  autoName = "Nhóm " + (Groups.Length + 1)     ← auto-name
  Make S_GroupData{newGID, autoName, "", False} → ADD to Groups
  SyncGroupsToContainer

  SET ActorsCopy = SelectedActors              ← tránh pass-by-ref
  ForEach ActorsCopy: Cast → SET GroupID = newGID

  CaptureSnapshot("CreateGroup")               ← SAU khi gán xong
  Broadcast OnGroupCreated(newGID)
  Return newGID

IA_GroupCreate (Ctrl+G) — bind trong BP_FurnitureInputManager (furniture context):
  Branch SelectedActors.Length >= 2 → True: Call CreateGroup
```

### T7 — UngroupActors + Ctrl+Shift+G (45 phút)
```
Function UngroupActors(InGroupID: String):
  Branch InGroupID == "": True → Return
  GetGroupChildren(InGroupID) → ForEach: Cast → SET GroupID = ""   ← Sprint 3 phẳng; ParentGroupID để Sprint 4
  ← Xóa entry
  ForEach Groups (Index, g): Branch g.GroupID == InGroupID → SET FoundIdx = Index
  Branch FoundIdx >= 0: REMOVE INDEX(Groups, FoundIdx)
  SyncGroupsToContainer
  CaptureSnapshot("Ungroup")                   ← SAU khi xóa
  Broadcast OnGroupDestroyed(InGroupID)

IA_Ungroup (Ctrl+Shift+G):
  Branch IsValid(PrimarySelectedActor) → Cast → GET GroupID → Branch != "":
    True → Call UngroupActors(GroupID)
```
> ⚠️ Ctrl+Shift kiểm tra như Ctrl+Shift+V trước đây (Shift check trong IA binding) để không xung đột Ctrl+G.

### T8 — Group Click Resolution (45 phút)
Sửa đoạn resolve click trong **OnLMBReleased** (chỗ hiện gọi SelectSingleActor từ PendingClickActor):
```
Hiện tại: PendingClickActor → SelectSingleActor(PendingClickActor)

Mới:
  Branch IsCtrlDown:
    False → DeselectAll
            ExpandSelectionWithGroups([PendingClickActor]) → SelectActors(result)
    True  → ExpandSelectionWithGroups([PendingClickActor]) → SelectActors(result)  (cộng dồn)
```
> SelectActors đã tự lo outline + Pivot + gizmo + broadcast. Click đồ rời → result = [đồ đó] → hành vi y như cũ. Click đồ trong group → result = cả group.

### T9 — Box Select Group Expansion (30 phút)
Trong **FinishBoxSelect**, sau khi gom được raw actors trong khung, trước khi SelectActors:
```
Hiện tại: ... → SelectActors(LocalInBox)
Mới:      ... → ExpandSelectionWithGroups(LocalInBox) → SelectActors(result)
```

### T10 — Dispatchers + Selection Info Bar (30 phút)
```
Event Dispatchers (BP_FurnitureInputManager):
  OnGroupCreated(GroupID: String)
  OnGroupDestroyed(GroupID: String)

Selection Info Bar (WBP_MeshControls hoặc WBP_SelectionInfoBar):
  Trong handler OnSelectionChanged:
    Branch PrimarySelectedActor.GroupID != "":
      True → FindGroupData(GroupID) → "📦 " + GroupName + " (" + SelectedActors.Length + ")"
      False → giữ text count cũ "N vật thể"
```

### T11 — Snapshot v3 (45 phút)
```
S_FurniturePlacement: thêm GroupID (String)
S_SceneSnapshot: Version=3, thêm Groups (Array<S_GroupData>)

CaptureSnapshot (mở rộng):
  ForEach actor build placement → thêm: placement.GroupID = actor.GroupID
  Sau khi build TempMeshes:
    SET Snapshot.Version = 3
    SET Snapshot.Groups = Groups   (copy current InputManager.Groups)

RestoreSnapshot (mở rộng):
  ... spawn actors (giữ nguyên) ...
  ForEach Snapshot.Meshes (Index, mesh):
    SpawnedActors[Index] → Cast → SET GroupID = mesh.GroupID
  Branch Snapshot.Version >= 3:
    CLEAR Groups → ForEach Snapshot.Groups: ADD to Groups
    SyncGroupsToContainer
```
> Tái dùng ~80% snapshot Sprint 1. Chỉ thêm 1 field per placement + 1 array + restore tương ứng.

### T12 — Delete Group + Final Test (30 phút)
Delete group tái dùng `DeleteSelected` (đã có — chọn group = chọn cả members → xóa hết). Chỉ thêm prune:
```
DeleteSelected (cuối, sau Destroy ForEach, TRƯỚC CaptureSnapshot):
  ... Destroy ForEach ... → DeselectAll → PruneEmptyGroups → CaptureSnapshot("Delete")
```

---

## 5. TEST CASES (cuối sprint)

| # | Case | Kỳ vọng |
|---|---|---|
| 1 | Multi-select 6 đồ → Ctrl+G | Group tạo, 6 đồ cùng GroupID, auto-name "Nhóm 1" |
| 2 | Click 1 đồ trong group | Cả 6 chọn, info bar "📦 Nhóm 1 (6)" |
| 3 | Move/Rotate/Scale group | 6 đồ biến đổi qua Pivot (tái dùng Sprint 1) |
| 4 | Box bao 2/6 đồ trong group | Cả 6 được chọn |
| 5 | Ctrl+Shift+G | Ungroup, 6 đồ GroupID = "" |
| 6 | Click đồ rời (không group) | Chỉ 1 đồ chọn (hành vi cũ nguyên vẹn) |
| 7 | Delete group | 6 đồ xóa + entry group bị prune |
| 8 | Undo CreateGroup | Group hủy, đồ về rời |
| 9 | Undo Ungroup | Group khôi phục |
| 10 | **Save → Load** | Group khôi phục, click 1 đồ → cả group, đúng 1 container |
| 11 | Ctrl + click đồ group khác | Cộng dồn 2 group |
| 12 | Regression: single-select, box select đồ rời, replace, change material | Còn nguyên |

---

## 6. THỨ TỰ THỰC THI

```
1. VERTICAL SLICE: T1+T2+T3+T4 + CreateGroup tối giản → test Save/Load (kill EMS risk)
2. T5 (helpers — keystone) → T11 (snapshot) → T6 (CreateGroup đầy đủ + Ctrl+G)
3. T8 (click) + T9 (box) → test selection
4. T7 (ungroup) → T12 (delete + prune)
5. T10 (UI info bar + dispatchers)
6. Final test 12 cases + regression + update docs + DEVIATIONS
```

---

## 7. NODE MỚI / RỦI RO CẦN VERIFY KHI CODE

- `New Guid → To String` — verify node tồn tại UE5.5; nếu không, fallback Now+counter.
- EMS `ActorLoaded` + `Wait For Save or Load Completed (Load Only)` cho container — verify giống BP_FurnitureActor.
- EMS Full Reload có nhân đôi container không → **singleton guard** trong BeginPlay là phòng tuyến.
- `Get All Actors With Tag("FurnitureSpawned")` trong GetGroupChildren — chạy mỗi lần click; scene nhỏ (20-50 actor) OK, nếu lag thì cache sau.

---

## 8. KẾ THỪA & TỔNG QUÁT HÓA (cho tương lai)

| Function | Tái dùng từ | Dùng lại ở tương lai |
|---|---|---|
| `ExpandSelectionWithGroups` | mới | Nested group (S4), Combo spawn (S5), Outliner (S6) |
| `GetGroupChildren` | mới | Mọi nơi cần query member |
| Transform group | Pivot Sprint 1 | Edit mode (S4) |
| Snapshot Groups | CaptureSnapshot Sprint 1 | Edit mode EditingGroupID (S4) |
| `SyncGroupsToContainer` | pattern EMS BP_FurnitureActor | Combo save (S5) |
| `PruneEmptyGroups` | mới | Edit mode delete (S4) |

**Single source of truth:** `BP_FurnitureInputManager.Groups` (in-memory). Container = mirror cho EMS. Actor.GroupID = denormalized cho query nhanh + per-actor save. 3 nơi nhưng đồng bộ qua các điểm rõ ràng (CreateGroup/Ungroup/Delete/Restore/Load).
