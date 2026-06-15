# BP_FurnitureInputManager — PATCH v1.9
**Phiên bản:** 1.9 | **Cập nhật:** 15/06/2026 — 20:30 ICT
**Patch từ v1.8 → v1.9 (Sprint 4 Bug Fix: F1, F2, F3, F4)**
> Đọc kèm bản v1.8. File này ghi ĐỦ những gì thêm/thay đổi so với v1.8.

---

## VARIABLES — CẬP NHẬT

### Xóa khỏi BP_FurnitureInputManager
```
GroupNameCounter : Integer   ← ĐÃ CHUYỂN sang BP_GroupsContainer (F2)
```
> Lý do: BP_FurnitureInputManager không implement EMS save interface → Save/Load reset counter về 1.
> GroupNameCounter giờ nằm trong BP_GroupsContainer (đã EMS-saved), đọc/ghi qua ContainerRef.

---

## FUNCTIONS MỚI

### `GetSelectionUnitLabel(Primary: BP_FurnitureActor, Count: Integer) → Label: String` (F1)

**Mục đích:** Trả về label cho info bar selection, phân biệt đồ rời vs group, xét cả scope edit.

```
GET GetCurrentEditScope() → scope

Branch(scope != ""):          ← đang trong edit
  True:
    GET Primary.GroupID → gid
    Branch(gid == "" OR gid == scope):   ← đồ rời hoặc trực tiếp trong scope
      True  → Return (Count + " vật thể")
      False → WalkUpUntilParent(gid, scope) → unitGID
              FindGroupData(unitGID) → (data, _, bFound)
              Branch(bFound):
                True  → Return "📦 " + data.GroupName + " (" + Count + ")"
                False → Return (Count + " vật thể")
  False:                        ← ngoài edit
    GET Primary.GroupID → gid
    Branch(gid == ""):
      True  → Return (Count + " vật thể")
      False → GetGroupRoot(gid) → rootGID
              FindGroupData(rootGID) → (data, _, bFound)
              Branch(bFound):
                True  → Return "📦 " + data.GroupName + " (" + Count + ")"
                False → Return (Count + " vật thể")
```

> Chỉ gọi khi `Actors.Length >= 2`. Single/none không hiện info bar.
> Caller (WBP_MeshControls OnSelectionChangedHandler.Then 1) lo guard >= 2.

---

### `ComputeSelectionUnits(InActors: Array<BP_FurnitureActor>) → (OutGroupUnits: Array<String>, OutLooseActors: Array<BP_FurnitureActor>)` (F3)

**Mục đích:** Phân tách mảng actors thành "đơn vị group" (top-level group IDs) và "đồ rời" để CreateGroup bottom-up.

```
Local (class var dùng làm buffer):
  TempGroupUnits  : Array<String>          ← CLEAR đầu hàm
  TempLooseActors : Array<BP_FurnitureActor> ← CLEAR đầu hàm

GET GetCurrentEditScope() → scope

GET ActorsCopy = InActors (copy để iterate an toàn)

ForEach ActorsCopy (actor):
  IsValid(actor) → False: skip (dead-end)
  True:
    GET actor.GroupID → gid
    Branch(gid == ""):
      True  → ADD actor → TempLooseActors
      False:
        Branch(scope == ""):
          True  → GetGroupRoot(gid) → unitGID
          False → WalkUpUntilParent(gid, scope) → unitGID
        Branch(unitGID != ""):
          True:
            Contains(TempGroupUnits, unitGID) → False → ADD unitGID → TempGroupUnits
          False → ADD actor → TempLooseActors   ← fallback nếu không tìm được unit

Completed:
  SET OutGroupUnits  = TempGroupUnits
  SET OutLooseActors = TempLooseActors
```

> ⚠️ Output pins của Function không thể CLEAR → dùng TempGroupUnits/TempLooseActors làm buffer, assign ở Completed.
> ⚠️ ForEach Completed phải nối vào SET outputs — không để dead-end.

---

## FUNCTIONS SỬA

### `CreateGroup` — VIẾT LẠI (F3 — bottom-up nesting)

**Thay đổi chính:** Gọi ComputeSelectionUnits TRƯỚC guard; guard kiểm tra tổng số units.

```
Entry ▶→
  ComputeSelectionUnits(SelectedActors) → (GroupUnits, LooseActors)

  ← Guard: cần ít nhất 2 đơn vị
  (GroupUnits.Length + LooseActors.Length) → Sum
  Branch(Sum < 2): True → Return

  GenerateGroupID() → NewGID
  GET ContainerRef → GroupNameCounter → "Nhóm " + Counter → GroupName
  ContainerRef.GroupNameCounter + 1      ← increment SAU khi đã dùng

  ← Rebuild Groups: sub-groups trong selection đổi ParentGroupID = NewGID
  CLEAR LocalNewGroups
  ForEach_1 Groups (g):
    Branch(Contains(GroupUnits, g.GroupID)):
      True  → MAKE S_GroupData(GroupID=g.GroupID, GroupName=g.GroupName,
                                ParentGroupID=NewGID, bIsLocked=g.bIsLocked)
              → ADD newStruct → LocalNewGroups
      False → ADD g (nguyên gốc) → LocalNewGroups
  Completed_1 → SET Groups = LocalNewGroups

  ← Đồ rời: SET GroupID = NewGID
  ForEach_2 LooseActors (actor):
    IsValid(actor) → True → SET actor.GroupID = NewGID
  Completed_2:

  ← ADD group mới vào Groups
  MAKE S_GroupData(GroupID=NewGID, GroupName=GroupName,
                   ParentGroupID=GetCurrentEditScope(), bIsLocked=False)
  → ADD → Groups

  SyncGroupsToContainer
  CaptureSnapshot("CreateGroup")
  SelectActors([NewGID actors])    ← re-select để info bar update
  Broadcast OnGroupCreated(NewGID)
```

> ⚠️ Luật 6B (structural symmetry): ComputeSelectionUnits phải chạy TRƯỚC guard — nếu guard dùng SelectedActors.Length sẽ sai với case đã chọn toàn groups.
> ⚠️ GroupNameCounter đọc từ ContainerRef (BP_GroupsContainer), ghi lại ngay sau khi dùng.

---

### `SpawnFurnitureCopy` — SỬA (F4 — auto-join edit scope)

Trong **Sequence.Then 0**, ngay SAU `ADD "FurnitureSpawned" → SET Tags`, TRƯỚC khi Sequence tiếp tục Then 1:

```
[After SET Tags (ADD FurnitureSpawned)]

GetCurrentEditScope() ●→ Scope
Branch(Scope Not Equal (String) ""):
  True  ▶→ SET NewActorCopy.GroupID = Scope
  False ▶→ (dead-end — hợp lệ trong Sequence context)

[Sequence tự động kích hoạt Then 1, 2, 3...]
```

> ✅ Dead-end nhánh False HỢP LỆ vì đây là trong Sequence.Then 0: Sequence tự fire Then 1 tiếp theo không cần merge.
> ⚠️ Nếu không phải Sequence mà là Event bình thường → phải merge (bài học L2 WBP_DragOverlay).

---

## VARIABLES MỚI trong BP_GroupsContainer

```
GroupNameCounter : Integer    (default=1, SaveGame=TRUE)
```
> Monotonic counter, KHÔNG reset khi ungroup/delete. Chỉ tăng, không giảm.
> Ghi qua EMS cùng slot Groups → survives Save/Load.

---

## Lịch sử cập nhật (thêm vào bảng)

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.9 | 15/06/2026 — 20:30 ICT | **Sprint 4 Bug Fix F1-F4.** Thêm GetSelectionUnitLabel (F1), ComputeSelectionUnits (F3). Chuyển GroupNameCounter sang BP_GroupsContainer (F2). CreateGroup viết lại bottom-up (F3). SpawnFurnitureCopy thêm auto-join edit scope (F4). |
