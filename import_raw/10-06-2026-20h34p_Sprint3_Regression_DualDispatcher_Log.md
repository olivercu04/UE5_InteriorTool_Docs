# Sprint 3 — Regression Fixes + Refactor Dual-Dispatcher (Log chi tiết flow)
**Phiên bản:** 1.0 | **Cập nhật:** 10/06/2026 — 20:34 ICT | Lighting_Mnger UE5.5.4

> Ghi lại node-level flow của các function/event đã sửa trong đợt regression-fix sau Sprint 3, cộng refactor hợp nhất dispatcher selection. Dùng làm tham chiếu cập nhật `Blueprint_Logic.md`. Đọc kèm `Session_State.md`.

---

## 0. TÓM TẮT THAY ĐỔI

| Loại | Chi tiết |
|---|---|
| Dispatcher XÓA | `OnMeshSelected`, `OnMeshDeselected` (BP_FurnitureInputManager) |
| Dispatcher DUY NHẤT | `OnSelectionChanged(Actors : Array<BP_FurnitureActor>, Primary : BP_FurnitureActor)` |
| Biến XÓA | `MeshToReplace` (single) — chỉ còn `MeshesToReplace : Array` |
| Biến THÊM | `BP_UndoManager.TempGroups : Array<S_GroupData>` (no SaveGame) |
| Event handler XÓA | `WBP_FurnitureInventory.OnMeshDeselected` |
| Event handler THÊM | `WBP_FurnitureInventory.OnSelectionChangedMaterial(Actors, Primary)` |

---

## 1. BP_UndoManager

### 1.1 Biến mới
```
TempGroups : Array<S_GroupData>   (KHÔNG SaveGame)
```

### 1.2 CaptureSnapshot (sửa — bug Undo không restore Groups)
**Root cause:** `GetGroupsForSnapshot` là impure function (có exec pin). Output chỉ "đóng băng" giá trị tại thời điểm exec của nó chạy. Khi nối thẳng output → pin `Groups` của `Make S_SceneSnapshot`, nếu exec của GetGroupsForSnapshot chạy SAU node Make → Make đọc default (rỗng). Kết quả: snapshot lưu Groups=0 dù InputManager.Groups=1.

**Fix flow:**
```
[Đầu CaptureSnapshot — TRƯỚC Make]
  Call GetGroupsForSnapshot → SET TempGroups
...
Make S_SceneSnapshot:
  Version = 3
  Groups  = GET TempGroups          ← KHÔNG nối thẳng từ GetGroupsForSnapshot nữa
```

### 1.3 GetGroupsForSnapshot (giữ — đã đúng)
```
Get All Actors Of Class(BP_FurnitureInputManager) → Length → Branch >0
  True → Get(0) → IsValid → True → GET Groups → Return Groups
  (else) → Return (rỗng)
```

### 1.4 RestoreSnapshot — đoạn cuối (sửa — bug undo về deselect không tắt outline/gizmo)
**Root cause:** node re-fire cuối luôn gọi `SelectActors(InputManager.SelectedActors)`; khi snapshot deselect (SelectedActors rỗng) thì `SelectActors(rỗng)` không deselect → outline/gizmo cũ còn.

**Fix flow (sau SyncGroupsToContainer):**
```
Get All Actors Of Class(InputManager) → Get(0) → IsValid:
  True →
    Branch (InputManager.SelectedActors.Length > 0):
      True  → SelectActors(InputManager.SelectedActors) ─┐
      False → DeselectAll → DeactivateGizmo(GizmoController) ─┤
                                                              ├→ Call OnRestoreCompleted
```
> CẢ 2 nhánh merge về `Call OnRestoreCompleted` — không để nhánh False dead-end.

---

## 2. BP_FurnitureInputManager

### 2.1 UngroupActors (sửa — spam 3 snapshot + warning [0/0])
**Root cause:** toàn bộ chuỗi find-index → REMOVE INDEX → Sync → CaptureSnapshot bị nối vào **Loop Body** của ForEach children (3 child → chạy 3 lần). + FoundIdx là class var không reset.

**Fix flow:**
```
UngroupActors(InGroupID):
  SET FoundIdx = -1                         ← reset đầu hàm (class var)
  Branch (InGroupID == "") → True: Return
  False:
    GetGroupChildren(InGroupID) → ForEach1 (child):
        Loop Body → Cast → SET child.GroupID = ""      ← CHỈ set, KẾT THÚC loop body ở đây
    ForEach1 Completed →                                ← các bước sau ra khỏi loop
        ForEach2 (Groups, Index): Break → Branch (GroupID == InGroupID) → SET FoundIdx = Index
        ForEach2 Completed →
          Branch (FoundIdx >= 0) → True: REMOVE INDEX(Groups, FoundIdx)
          → SyncGroupsToContainer
          → Get All Actors(BP_UndoManager)[0] → CaptureSnapshot("Ungroup")   ← 1 LẦN
          → SelectActors(SelectedActors)   (re-fire info bar)
          → Broadcast OnGroupDestroyed
```

### 2.2 SelectSingleActor (sửa — refactor dispatcher)
```
... [set state + outline + gizmo] ...
→ Call OnSelectionChanged(Make Array(actor), actor)
   ← ĐÃ XÓA: Call OnMeshSelected
```

### 2.3 SpawnFurnitureCopy — đoạn tail (sửa — refactor dispatcher + dùng SelectActors)
**Trước:** Deselect Mesh → SET SelectedFurnitureActor(single cũ) → Set Custom Depth Stencil(225) → Set Render Custom Depth → Branch→Select(ActiveMode)→ActivateGizmo → Call OnMeshSelected → Return.

**Sau (gọn):**
```
Branch True → Deselect Mesh → SelectActors(Make Array(New Actor Copy)) → Return Node(New Actor = copy)
Branch False → (merge) → Return Node
```
> `SelectActors` tự lo: clear-then-select, outline (Stencil **255** chuẩn — sửa luôn lỗi 225 cũ), gizmo theo ActiveMode, fire OnSelectionChanged. Bonus: MeshControls/info bar nay cập nhật khi spawn copy.

### 2.4 DeselectMesh (sửa — refactor dispatcher)
```
DeselectMesh:
  IsValid(SelectedFurnitureActor) → Set Render Custom Depth=false (bỏ outline)
  → SET SelectedFurnitureActor = None
  → IsValid(...) → Deactivate Gizmo
  ← ĐÃ XÓA: Call OnMeshDeselected   (giữ toàn bộ phần clear state)
```

### 2.5 DeselectAll (sửa — refactor dispatcher)
```
DeselectAll:
  ForEach(SelectedActors) → IsValid → Set Render Custom Depth=false (bỏ outline từng đồ)
  Completed → CLEAR SelectedActors
  → SET PrimarySelectedActor = None
  → SET SelectedFurnitureActor = None
  → Deactivate Gizmo
  → Destroy Pivot
  → Call OnSelectionChanged(Make Array(rỗng), None)
  ← ĐÃ XÓA: Call OnMeshDeselected   (giữ toàn bộ phần clear state)
```

### 2.6 Dispatchers
```
ĐÃ XÓA: OnMeshSelected
ĐÃ XÓA: OnMeshDeselected
GIỮ:    OnSelectionChanged(Actors : Array<BP_FurnitureActor>, Primary : BP_FurnitureActor)
```

### 2.7 Biến
```
ĐÃ XÓA: MeshToReplace : BP_FurnitureActor (single)
GIỮ:    MeshesToReplace : Array<BP_FurnitureActor>   (CLEAR ở End Play)
```

---

## 3. BP_FoffPlayerController / Mouse Left (Step 7 — Mouse Left Pressed)

### 3.1 (sửa — bug Ctrl+click group không cộng dồn)
**Root cause:** nhánh Ctrl trong Mouse Pressed gọi `ToggleActor(HitActor)` ngay (1 đồ đơn, không expand group) rồi STOP → không bao giờ tới OnLMBReleased (nơi có expand group).

**Fix:** bỏ Branch Ctrl, MỌI click đều defer:
```
Mouse Left Pressed (đã hit furniture):
  Cast To BP_FurnitureActor
  → SET PendingClickActor = HitActor
  → Get Mouse Position on Viewport → SET BoxStartPos
  → SET bIsPendingBoxSelect = True
  ← ĐÃ XÓA: Branch IsInputKeyDown(LeftCtrl) + nhánh ToggleActor + CaptureSnapshot
```
> Phân giải single / group / Ctrl chuyển hết về **OnLMBReleased Then2** (IsValid PendingClickActor → Ctrl? → ExpandSelectionWithGroups → ToggleActor/SelectActors). Nhớ `SET PendingClickActor = None` cuối xử lý.

---

## 4. WBP_FurnitureInventory

### 4.1 Event Construct (sửa — bind dispatcher)
```
+ Bind Event to OnSelectionChanged (Target=InputManager) → OnSelectionChangedMaterial
− Bind Event to OnMeshSelected     (XÓA — dispatcher đã chết)
− Bind Event to OnMeshDeselected   (XÓA — dispatcher đã chết)
```

### 4.2 OnSelectionChangedMaterial(Actors, Primary) — custom event MỚI
```
OnSelectionChangedMaterial(Actors, Primary):
  → Call OnMeshSelected(Primary)     ← tái dùng handler cũ (không duplicate logic)
```
> `OnMeshSelected` ở đây là **custom event handler nội bộ của inventory** (KHÁC dispatcher đã xóa). Giờ nó được kích hoạt qua OnSelectionChanged.

### 4.3 OnMeshSelected (handler nội bộ — sửa nhánh replace + thêm guard material)
```
OnMeshSelected(SelectedActor):

  ← Nhánh REPLACE
  Branch (bIsReplaceMode == True):
    True →
      Get All Actors(InputManager)[0] → IsValid →
        SET MeshesToReplace = InputManager.SelectedActors     ← SỬA: array, KHÔNG phải MeshToReplace single
      Branch IsValid(SelectedActor):                          ← guard sẵn (folder nav an toàn khi deselect)
        True → Cast → GET DAPath → Load Asset Blocking → Cast DA_FurnitureItem
               → GET MeshFolderPath → Branch (!= "") → FilterByFolderPathWithUI

  ← Nhánh MATERIAL (sửa — bug Accessed None)
  Branch (CurrentInventoryMode == Material):
    True →
      Branch IsValid(SelectedActor):                          ← THÊM guard
        True  → SET TargetFurnitureActor = SelectedActor
                → Set Visibility(HB_SlotSwatches, Visible)
                → SET SelectedSlotIndex = -1
                → RefreshSlotSwatches → Update Swatch Thumbnails
        False → SET TargetFurnitureActor = None
                → Set Visibility(HB_SlotSwatches, Collapsed)
                → SET SelectedSlotIndex = -1                  ← khớp việc OnMeshDeselected cũ làm
```
> Nhánh material False thay thế hoàn toàn handler `OnMeshDeselected` (đã xóa): khi OnSelectionChanged fire rỗng (deselect) → Primary invalid → collapse + reset.

### 4.4 OnMeshDeselected (handler) — ĐÃ XÓA
Logic collapse material giờ nằm ở nhánh material False của OnMeshSelected (4.3), kích hoạt qua OnSelectionChanged rỗng.

### 4.5 EnterReplaceMode (sửa — bug replace lúc minimize không bung)
```
EnterReplaceMode:
  Call EnsureExpanded (Target=self)    ← THÊM đầu hàm (bung nếu đang minimize; no-op nếu đang mở)
  → SET bIsReplaceMode = True
  → Regenerate All Entries(CTV_FurnitureCard)
```

---

## 5. WBP_DragOverlay_FurnitureCard / F_ExecuteReplace

### 5.1 (sửa — bug replace mesh không liên tục)
**Root cause:** thiếu node ADD New Actor vào LocalNewActors trong Loop Body → LocalNewActors rỗng → SelectActors(rỗng) + SET MeshesToReplace(rỗng) → mesh mới không được chọn, không replace tiếp được.

**Fix — Loop Body (bổ sung):**
```
ForEach MeshesToReplace (OldActor):
  ... Spawn → setup NewActor (MeshPath/DAPath/PlacementSurfaceType/Tags) ...
  → ADD New Actor → LocalNewActors      ← THÊM
  → Destroy Actor(OldActor)

Completed:
  DeselectAll → SelectActors(LocalNewActors)
  → CaptureSnapshot("Replace")
  → AddRecentMesh
  → SET MeshesToReplace = LocalNewActors    (replace tiếp được)
```

---

## 6. ĐÚC KẾT KINH NGHIỆM (đợt này)

1. **Impure function + data pin:** output chỉ valid SAU khi exec của function chạy. Nối thẳng vào node đọc trước đó → đọc default. → gọi sớm, SET temp var, node đọc temp var. (TempGroups)
2. **"Code 1 lần → Completed":** không chỉ snapshot — cả cụm find/remove/broadcast nếu lỡ nằm trong Loop Body sẽ nhân theo số vòng. Kiểm tra exec ra khỏi loop trước khi nghi chỗ khác.
3. **Class var reset đầu hàm:** default value chỉ set lúc construct, KHÔNG reset mỗi lần gọi. Hàm gọi nhiều lần → SET lại đầu hàm (FoundIdx = -1).
4. **Mọi nhánh Branch merge về cuối:** nhánh empty/False của restore cũng phải tới Broadcast (OnRestoreCompleted), không dead-end.
5. **Handler nhận selection phải guard IsValid:** OnSelectionChanged fire cả lúc rỗng (deselect, hoặc DeselectAll trước SelectActors khi click). Không guard → Accessed None.
6. **Bind dispatcher ở Event Construct**, không trong handler — handler không fire thì bind không bao giờ chạy (lỗi material không update lần đầu).
7. **Single source of truth:** dual-dispatcher (OnMeshSelected + OnSelectionChanged) và dual-var (MeshToReplace + MeshesToReplace) là GỐC của cả loạt regression. Feature gắn lên dispatcher/biến chết thì lặng lẽ ngừng hoạt động khi đường còn lại đổi. → hợp nhất, xóa cái chết.
8. **Defer mọi click:** Mouse Pressed chỉ SET PendingClickActor + BoxStart; phân giải single/group/Ctrl/box ở Mouse Released. Xử lý ngay ở Pressed (như Ctrl cũ) làm rẽ nhánh sớm, bỏ qua group expansion.
9. **Kỷ luật debug — print QUYẾT ĐỊNH:** thay vì đoán, in 1 thông tin phân biệt được giả thuyết:
   - capture vs restore: in giá trị TRONG snapshot (`SNAPSHOT chua: N`) tại RestoreSnapshot
   - hàm chạy mấy lần: in `ENTRY` đầu hàm, đếm dòng
   - undo restore gì: in `ActionName + sel.Length`
   Mỗi lần đoán sai tốn 1 vòng; print 1 lần là chốt.
10. **Verify trước khi cắt (refactor):** map đủ broadcaster + listener của dispatcher trước khi xóa. Thứ tự cắt phải đảm bảo UI luôn còn 1 đường nhận tín hiệu (đổi nguồn fire → repoint listener → gỡ bind cũ → xóa dispatcher).

---

## 7. CHECKLIST KIẾN TRÚC (áp dụng từ giờ)

- [ ] 1 dispatcher cho 1 khái niệm (selection = OnSelectionChanged). Không tạo dispatcher song song.
- [ ] 1 biến cho 1 trạng thái (replace = MeshesToReplace). Không dual-var.
- [ ] Handler selection: guard IsValid(Primary) ngay đầu.
- [ ] Bind ở Event Construct.
- [ ] Class var dùng trong hàm gọi nhiều lần: SET lại đầu hàm.
- [ ] Cụm "chạy 1 lần" sau loop: nối vào Completed.
- [ ] Mọi nhánh Branch merge về cuối.
