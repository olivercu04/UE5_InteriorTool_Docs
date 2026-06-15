# BP_FurnitureInputManager — PATCH v1.8
**Phiên bản:** 1.8 | **Cập nhật:** 12/06/2026 — 15:04 ICT
**Patch từ v1.7 → v1.8 (Sprint 4 T6–T8 + Bug Fix Replace GroupID)**
> Đọc kèm bản hợp nhất v1.7. File này ghi ĐỦ những gì thêm/thay đổi so với v1.7.

---

## Xóa ghi chú ⚠ trong v1.7
Dòng sau đây trong v1.7 header cần XÓA (đã implement xong):
> ~~⚠ CHƯA CÓ trong bản này (Sprint 4 T6-T8 đang chờ): CreateGroup nested, UngroupActors deep-tree, PruneEmptyGroups theo GetAllDescendantActors, ValidateEditMode.~~

---

## Local Variables: UngroupActors — CẬP NHẬT

**Xóa** (không còn dùng): `FoundIdx` (class var, cũ từ Sprint 3), `Root` (String local), `LocalRemoveIDs` (Array String)
**Giữ/thêm mới:**
```
target          : String (local)              ← group cần ungroup (xác định qua WalkUpUntilParent)
parentGID       : String (local)              ← GroupID của cha target
scope           : String (local)              ← scope edit hiện tại
LocalNewGroups  : Array of S_GroupData (local) ← rebuild Groups với ParentGroupID đã sửa (B2)
LocalKeep       : Array of S_GroupData (local) ← Groups sau khi bỏ target (B3)
```

---

## Functions SỬA (Sprint 4 T6)

### `CreateGroup` — sửa 1 dòng
Trong node `Make S_GroupData`, đổi field `ParentGroupID`:
```
Cũ: ParentGroupID = ""
Mới: ParentGroupID = GetCurrentEditScope()
```
> Ngoài edit → GetCurrentEditScope()="" → group gốc (giống Sprint 3, không regression).
> Trong edit scope g_A → ParentGroupID="g_A" → sub-group của g_A.

---

## Functions SỬA (Sprint 4 T7)

### `PruneEmptyGroups` — đổi tiêu chí keep

```
CLEAR LocalKeep                              ← local Array S_GroupData
ForEach Groups (g):
  Loop Body →
    GetAllDescendantActors(g.GroupID) → Length   ← THAY GetGroupChildren (xét cả subtree)
    Branch(Length > 0):
      True  → ADD g → LocalKeep
      False → (để trống)
Completed →
  SET Groups = LocalKeep
  SyncGroupsToContainer
```
> GetGroupChildren (cũ) chỉ check direct members → prune oan group cha nested có sub-groups.
> GetAllDescendantActors nhìn cả cây → cascade đúng 1 pass (không mutate Groups giữa chừng).

---

### `UngroupActors(InGroupID : String)` — VIẾT LẠI hoàn toàn (peel-one-level)

> Semantic mới: ungroup đúng 1 cấp. Actor trực tiếp về cha. Sub-group đổi cha về cha. Chỉ xóa target.
> Flat group: WalkUpUntilParent(gid, "")=gid (scope rỗng) → giống Sprint 3, không regression.

```
Entry ▶→ Branch(InGroupID == ""):
           True  ▶→ Return
           False ▶→ GetCurrentEditScope → SET scope
                  ▶→ WalkUpUntilParent(InGroupID, scope) → SET target
                  ▶→ Branch(target == ""): True ▶→ Return
                  ▶→ FindGroupData(target) → (data, Found)
                  ▶→ Branch(Found == False): True ▶→ Return
                  ▶→ BREAK data → GET ParentGroupID → SET parentGID

       ← B1: actor con trực tiếp → về cha
       ▶→ GetGroupChildren(target) → ForEach_1(actor):
            LoopBody ▶→ Cast actor → BP_FurnitureActor → SET GroupID = parentGID
            Completed ▶→

       ← B2: rebuild Groups — sub-group con trực tiếp đổi ParentGroupID về cha
            CLEAR LocalNewGroups
            GET Groups → ForEach_2(g):
              LoopBody ▶→ BREAK g → GET g.ParentGroupID
                       ▶→ Branch(g.ParentGroupID == target):
                            True  ▶→ MAKE S_GroupData(
                                         GroupID      = g.GroupID,
                                         GroupName    = g.GroupName,
                                         ParentGroupID = parentGID,   ← đổi về cha của target
                                         bIsLocked    = g.bIsLocked)
                                   ▶→ ADD newStruct → LocalNewGroups
                            False ▶→ ADD g (nguyên gốc) → LocalNewGroups
              Completed ▶→ SET Groups = LocalNewGroups

       ← B3: xóa target khỏi Groups (rebuild, bỏ qua target)
            CLEAR LocalKeep
            ForEach_3 Groups (g2):
              LoopBody ▶→ Branch(g2.GroupID != target):
                             True  ▶→ ADD g2 → LocalKeep
                             False → (để trống)
              Completed ▶→ SET Groups = LocalKeep
                         ▶→ SyncGroupsToContainer
                         ▶→ CaptureSnapshot("Ungroup")     ← 1 lần duy nhất ở Completed
                         ▶→ SelectActors(SelectedActors)   ← re-fire info bar
                         ▶→ Broadcast OnGroupDestroyed(target)
```

> B1 Completed → B2 (CLEAR LocalNewGroups) → B2 Completed (SET Groups) → B3 (CLEAR LocalKeep) → B3 Completed (SET Groups + Sync + Capture + ...).
> CaptureSnapshot CHỈ ở ForEach_3.Completed, không bao giờ trong LoopBody.
> FindGroupData không có output Index — KHÔNG dùng Set Array Elem. Dùng rebuild pattern (B2/B3).

---

## Bug Fix (12/06/2026) — GroupID preserved khi Replace Mesh

**File:** `WBP_DragOverlay_FurnitureCard`, BTN_ChangeMesh OnClicked, trong ForEach MeshesToReplace.

Thêm sau khi spawn NewActor (trước Destroy OldActor):
```
Cast OldActor → BP_FurnitureActor → GET GroupID → OldGroupID
SET NewActor.GroupID = OldGroupID
```
> Đảm bảo actor mới kế thừa GroupID từ actor cũ → group structure không bị phá sau Replace.
> Phải đặt TRƯỚC Destroy Actor(OldActor).

---

## Lịch sử cập nhật (thêm vào bảng)

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.8 | 12/06/2026 — 15:04 ICT | **Sprint 4 T6-T8 + Bug Fix.** CreateGroup: ParentGroupID=GetCurrentEditScope(). PruneEmptyGroups: GetAllDescendantActors thay GetGroupChildren. UngroupActors: viết lại peel-one-level (scope→target→B1 actor về cha→B2 rebuild sub-groups→B3 xóa target). Local vars update (xóa FoundIdx/Root/LocalRemoveIDs, thêm target/parentGID/scope/LocalNewGroups/LocalKeep). Bug Fix: GroupID preserved trong Replace Mesh (WBP_DragOverlay_FurnitureCard). |
