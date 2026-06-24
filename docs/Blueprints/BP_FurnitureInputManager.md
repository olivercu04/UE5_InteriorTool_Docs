# BP_FurnitureInputManager
**Phiên bản:** 2.3 | **Cập nhật:** 24/06/2026 — CalculateComboAnchor (C4) | Actor riêng — input hub + multi-select hub + box-select hub + context-menu hub + group hub + edit-mode hub

> **HỢP NHẤT TỪ:** base v1.6 + patch v1.7 + patch v1.8 + patch v1.9 (15/06/2026). Đây là bản đầy đủ, thay thế toàn bộ file gốc + patch trong import_raw.
> **File canonical.** `BP_FurnitureInputManager_MERGED_v1.9.md` là bản duplicate — sẽ bị xóa (cuhoang 17/06/2026). Chỉ đọc file này.
>
> **v2.1 (19/06/2026):** `SpawnFurnitureCopy` — async load mesh + material qua `BP_FurnitureActor.LoadMeshAsync/LoadMaterialsAsync` (thay Load Asset Blocking). `NewActorCopy` đổi class var → local var. Add Recent Mesh parse `MeshPath` thay `DAPath`.
> **v1.10 (Sprint D.T6):** Thêm `StartReplaceMode(Actors)` — document lần đầu. Primary actor → Branch RowName != "" → DT lookup MeshFolderPath (fallback DAPath). Mouse Left Pressed: ghi nhận + XÓA Step 11 (UpdateDetailPopup → stale popup bug).
> **v1.9 (Sprint 4 Bug Fix F1-F4):** thêm `GetSelectionUnitLabel` (F1), `ComputeSelectionUnits` (F3); `CreateGroup` viết lại bottom-up (F3); `SpawnFurnitureCopy` auto-join edit scope (F4); `GroupNameCounter` chuyển sang `BP_GroupsContainer` (F2).
> **v1.8 (Sprint 4 T6-T8):** `UngroupActors` viết lại peel-one-level; `PruneEmptyGroups` dùng `GetAllDescendantActors`.
> **v1.7 (Sprint 4 T1-T5 — Edit Mode):** `EditModeStack`, dispatcher `OnEditModeChanged`, 7 helper đệ quy + Resolver, các hàm Enter/Exit edit mode; `ExpandSelectionWithGroups` viết lại dùng `ResolveSelectionUnit`.
> **v1.6 (Sprint 3 Group + Refactor dispatcher):** hệ Group; **HỢP NHẤT DISPATCHER:** `OnSelectionChanged` là dispatcher selection DUY NHẤT (xóa `OnMeshSelected`/`OnMeshDeselected`). Mouse Pressed Step 7 bỏ nhánh Ctrl. Đọc kèm `Sprint3_Regression_DualDispatcher_Log.md`.

---

## Mục đích
Tách toàn bộ logic input furniture khỏi BP_FoffPlayerController (shared code).
Chỉ cần spawn actor này vào level là hệ thống hoạt động — không đụng shared code.

**v1.4:** thêm hệ thống **Multi-Select** (Sprint 1 plan_v3). Giữ song song state cũ (`SelectedFurnitureActor`) và state mới (`SelectedActors` + `PrimarySelectedActor`) đến hết Sprint 7 (S7.T9 cleanup).

**v1.5 (Sprint 2 — Box Select + Context Menu):** thêm **Box Select** (kéo khung chọn nhiều đồ) và **Context Menu** (right-click). Đây là actor giữ NHIỀU code phức tạp nhất — đặc biệt là tương tác giữa Mouse Left Pressed (defer click), Event Tick (vẽ box, phát hiện kéo), và OnLMBReleased (chốt selection). Đọc kỹ mục "TƯƠNG TÁC 3 ĐIỂM" ở dưới trước khi sửa.

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
MeshesToReplace        : Array of BP_FurnitureActor   ← v1.6: thay MeshToReplace (single). CLEAR ở End Play
                                                        (đã XÓA MeshToReplace single — single source of truth)
```

### Group (v1.6 — Sprint 3)
```
Groups : Array of S_GroupData   ← nguồn sự thật in-memory cho group (KHÔNG SaveGame; CLEAR ở End Play)
                                  (BP_GroupsContainer giữ bản SaveGame, sync 2 chiều)
FoundIdx : Integer   ← ⚠️ v1.8: ĐÃ XÓA khỏi UngroupActors (chuyển sang local target/parentGID/scope). Giữ note để biết lịch sử.
```

### Edit Mode (v1.7 — Sprint 4)
```
EditModeStack : Array<String>   ← stack GroupID đang edit. Rỗng = không edit. KHÔNG SaveGame. CLEAR ở End Play.
```
> ⚠️ `GroupNameCounter` (v1.9 F2): KHÔNG nằm ở BP này — đã chuyển sang `BP_GroupsContainer` (default=1, SaveGame=TRUE). Lý do: BP_FurnitureInputManager không implement EMS → Save/Load reset counter về 1. Đọc/ghi qua ContainerRef.

### Nudge (v1.2 — B1)
```
NudgeSnapshotTimerHandle : Timer Handle      ← debounce CaptureSnapshot 0.5s
NudgeSpeed               : Float (=150.0)     ← cm/s, free mode (SnapStep=0)
```

### Multi-Select (v1.4 — Sprint 1 T1)
```
SelectedActors      : Array of BP_FurnitureActor   ← danh sách đồ đang chọn
PrimarySelectedActor: BP_FurnitureActor            ← đồ chọn cuối (primary, stencil 255)
GizmoPivotActor     : BP_PivotActor                ← pivot vô hình cho multi-gizmo
LastPivotTransform  : Transform                    ← transform pivot lần gần nhất
ClipboardActors     : Array of S_ClipboardEntry    ← clipboard multi (thay 5 var cũ)
```

### Box Select (v1.5 — Sprint 2 T1-T2) ⭐
```
BoxSelectOverlayRef : WBP_BoxSelectOverlay   ← widget khung chọn, tạo ở BeginPlay
BoxStartPos         : Vector2D               ← vị trí chuột lúc bấm (logical/viewport coords)
bIsPendingBoxSelect : Boolean                ← ĐÃ bấm chuột, CHƯA biết là click hay kéo (chờ vượt ngưỡng 5px)
bIsBoxSelecting     : Boolean                ← ĐANG kéo khung (đã vượt 5px)
bLMBHeld            : Boolean                ← cờ thủ công: chuột trái đang giữ (SET True ở Mouse Left Pressed, False ở OnLMBReleased)
PendingClickActor   : BP_FurnitureActor      ← đồ bị bấm vào (defer select tới lúc thả, để phân biệt click-chọn vs kéo-box từ trên mesh)
```

### Context Menu (v1.5 — Sprint 2 T3-T4)
```
ContextMenuRef      : WBP_ContextMenu        ← menu chuột phải, tạo on-demand, clear ở Destruct của widget
```

### Clipboard cũ (v1.2 — B2) — GIỮ tạm, bỏ ở S7.T9
```
ClipboardMeshPath, ClipboardDAPath, ClipboardRotation, ClipboardScale, ClipboardMaterialOverrides
(không còn dùng — CopyMesh/PasteMesh đã chuyển sang ClipboardActors)
```

---

## Event Dispatchers (v1.6 — sau refactor)
```
OnSelectionChanged(Actors : Array<BP_FurnitureActor>, Primary : BP_FurnitureActor)  ← DISPATCHER SELECTION DUY NHẤT
OnSceneChanged(AllActors : Array<BP_FurnitureActor>)   ← v1.4 T14 (Scene Manager Panel Sprint 6)
OnGroupCreated(GroupID : String)      ← v1.6 Sprint 3
OnGroupDestroyed(GroupID : String)    ← v1.6 Sprint 3
OnEditModeChanged(bActive : Boolean, GroupID : String)   ← v1.7 Sprint 4
```
> **ĐÃ XÓA (refactor 10/06):** `OnMeshSelected`, `OnMeshDeselected`. Mọi mutator selection (SelectActors/DeselectAll/ToggleActor/SelectSingleActor/SpawnFurnitureCopy) giờ fire `OnSelectionChanged`. Lý do: dual-dispatcher là gốc của loạt regression — feature gắn lên dispatcher chết thì lặng lẽ ngừng update. Chi tiết: `Sprint3_Regression_DualDispatcher_Log.md`.

---

## ⭐⭐ TƯƠNG TÁC 3 ĐIỂM — Box Select / Single Click / Defer (đọc TRƯỚC khi sửa)

Đây là phần dễ gây bug nhất. Box Select chạm vào 3 nơi cùng lúc; phải hiểu vì sao chia như vậy:

**1. Mouse Left Pressed (input event):** chỉ GHI NHẬN bấm — KHÔNG select ngay. Ghi `BoxStartPos`, bật `bIsPendingBoxSelect`, bật `bLMBHeld`. Nếu bấm trúng mesh thì nhớ mesh đó vào `PendingClickActor` (chưa select). → **defer toàn bộ quyết định tới lúc thả chuột.**

**2. Event Tick (mỗi frame):** phát hiện chuột đã kéo quá 5px chưa. Nếu rồi → chuyển `bIsPendingBoxSelect`→`bIsBoxSelecting`, vẽ khung. Tick KHÔNG select đồ, chỉ lo VẼ KHUNG + cập nhật kích thước khung.

**3. OnLMBReleased (input event):** chốt kết quả.
   - Nếu `bIsBoxSelecting` (đã kéo box) → `FinishBoxSelect` (chọn các đồ trong khung).
   - Nếu `bIsPendingBoxSelect` mà CHƯA kéo (click đơn thuần) → nếu có `PendingClickActor` thì `SelectSingleActor` đồ đó; nếu không (bấm vào nền) thì `DeselectAll`.

**TẠI SAO defer (PendingClickActor) thay vì select ngay ở Mouse Left Pressed?**
→ Để phân biệt **click-chọn-1-đồ** vs **bắt đầu-kéo-box-từ-trên-một-đồ**. Nếu select ngay lúc bấm thì vừa chạm mesh đã single-select, không kéo box được.

**TẠI SAO chốt selection ở OnLMBReleased mà KHÔNG ở Tick?**
→ **Bug đã trả giá (Sprint 2):** gọi `ActivateGizmo` trong Event Tick race với Tick nội bộ của plugin RuntimeTransformer → gizmo NHÁY 1 frame trước khi mesh hiện. Input event (OnLMBReleased) chạy TRƯỚC world Tick → không nháy. → **Mọi việc ActivateGizmo/SelectSingleActor/FinishBoxSelect đặt ở OnLMBReleased, KHÔNG ở Tick.** Tick chỉ giữ nhánh fallback cho trường hợp flick chuột cực nhanh giữa các frame.

**TẠI SAO dùng cờ `bLMBHeld` thay vì `Is Input Key Down(Left Mouse Button)`?**
→ **Bug đã trả giá:** `Is Input Key Down` KHÔNG đáng tin cho nút chuột khi viewport đang capture mouse → khung box dính lại sau khi thả. Dùng boolean SET tay (True lúc bấm, False lúc thả) thì chắc chắn.

---

## Event BeginPlay (v1.5)
```
Enable Input
SET CurrentMeshControls = None, SET SelectedFurnitureActor = None
Get All Actors Of Class(BP_TransformerPawn) → Get(0) → SET TransformerPawnRef
← v1.5 Box Select:
Create Widget(WBP_BoxSelectOverlay) → SET BoxSelectOverlayRef
  → Add to Viewport(Z-Order 100)
  → Call HideBox (ẩn ban đầu)
```

---

## Mouse Left Pressed — FULL FLOW (v1.5)
```
Step 0 : SET bLMBHeld = True                              ← v1.5 (đầu tiên!)
Step 0b: Set Input Mode Game And UI
Step 1 : SET LocalWasGizmoActive = GizmoControllerRef.bGizmoActive
Step 2 : GizmoController → OnMousePressed
Step 3 : Branch bIsDraggingGizmo == True → True: STOP     ← đang cầm gizmo thì bỏ qua
Step 4 : GetHitResultUnderCursorByChannel(CAMERA) → Hit Actor, ReturnValue

Step 5 : Branch ReturnValue == True:
           False (bấm vào khoảng không) →
             Get Mouse Position on Viewport → SET BoxStartPos
             SET bIsPendingBoxSelect = True
             → STOP                                       ← KHÔNG check Ctrl lúc bấm; KHÔNG DeselectAll ngay (defer tới thả)

Step 6 : Branch ActorHasTag(Hit Actor, "FurnitureSpawned"):
           False (bấm trúng đồ KHÔNG phải furniture, vd tường) →
             Get Mouse Position on Viewport → SET BoxStartPos
             SET bIsPendingBoxSelect = True
             → STOP

Step 7 : DEFER cho MỌI click trúng furniture (v1.6 — bỏ nhánh Ctrl):
           SET PendingClickActor = (HitActor as BP_FurnitureActor)
           Get Mouse Position on Viewport → SET BoxStartPos
           SET bIsPendingBoxSelect = True
           → STOP
```
**Khác v1.4:** Step 5/6/7 trước đây select/deselect NGAY. Giờ chỉ ghi nhận + defer.
**Khác v1.5 (v1.6 fix Ctrl+click group):** Step 7 BỎ Branch `IsInputKeyDown(Left Ctrl)` + nhánh ToggleActor-ngay. Lý do: nhánh Ctrl cũ toggle 1 đồ đơn rồi STOP → không bao giờ tới OnLMBReleased (nơi expand group) → Ctrl+click group không cộng dồn. Giờ **MỌI click defer**; phân giải single/group/Ctrl chuyển hết về **OnLMBReleased Then2** (IsValid PendingClickActor → Ctrl? → ExpandSelectionWithGroups → ToggleActor / DeselectAll+SelectActors → CaptureSnapshot → SET PendingClickActor=None). Quyết định cuối ở OnLMBReleased.

> ⚠️ **v1.10 — Step 11 đã XÓA (Sprint D.T6):** `UpdateDetailPopup` (WBP_MeshControls) được nối tạm vào cuối Mouse Left Pressed (Step 11 không chính thức). Gây **stale popup bug**: chạy TRƯỚC khi `SelectedFurnitureActor` được set (selection chốt ở `OnLMBReleased`). Đã XÓA Step 11. `UpdateDetailPopup` nay **bind vào `OnSelectionChanged`** trong WBP_MeshControls Event Construct.

---

## Event Tick — Box Select branch (v1.5)
> Đặt SAU nhánh nudge free-mode, dùng **Sequence** để không phá logic cũ.

**⚠️ Bug đã trả giá — phải GUARD inventory:** Event Tick chạy MỌI frame, KHÔNG bị gate bởi Input Mapping Context (`LM_FurnitureInput`) như các Enhanced Input action khác. Nếu không guard, box select kích hoạt cả khi inventory đóng → sai context. Guard thủ công:
```
GetGameInstance → Cast Foff_GameInstance → GET FurnitureInventoryRef
→ nested Branch: IsValid(FurnitureInventoryRef)  [Branch ngoài]
     True → Is In Viewport(FurnitureInventoryRef) [Branch trong]   ← KHÔNG dùng AND (Blueprint AND không short-circuit → crash None)
            True → SET bInventoryOpen = True
     (mọi nhánh khác → SET bInventoryOpen = False)

Branch bInventoryOpen:
  False → cleanup: Call HideBox + SET bIsPendingBoxSelect=False + SET bIsBoxSelecting=False → STOP
  True  → chạy 2 branch box dưới đây
```

**Branch A — đang PENDING (bIsPendingBoxSelect == True):**
```
Branch bLMBHeld:
  True (vẫn giữ chuột) →
     khoảng cách = VectorLength( (Get Mouse Position on Viewport) - BoxStartPos )
     Branch khoảng cách > 5.0:
       True (đã kéo đủ xa → là KÉO BOX) →
         SET bIsBoxSelecting = True
         SET bIsPendingBoxSelect = False
         Call ShowBox
         Call UpdateBox(BoxStartPos, hiện tại)
  False (đã THẢ trước khi vượt 5px → là CLICK, fallback nếu OnLMBReleased lỡ) →
     SET bIsPendingBoxSelect = False
     Branch IsValid(PendingClickActor):
       True  → SelectSingleActor(PendingClickActor) → CaptureSnapshot("Select") → SET PendingClickActor=None
       False → Branch IsInputKeyDown(Left Ctrl):
                 True  → (dead-end, giữ selection)
                 False → DeselectAll → CaptureSnapshot("Deselect")
```

**Branch B — đang KÉO BOX (bIsBoxSelecting == True):**
```
Branch bLMBHeld:
  True  → Call UpdateBox(BoxStartPos, Get Mouse Position on Viewport)   ← cập nhật kích thước khung mỗi frame
  False (đã thả — fallback nếu OnLMBReleased lỡ) →
     Call FinishBoxSelect(Get Mouse Position on Viewport)
     Call HideBox
     SET bIsBoxSelecting = False
     SET PendingClickActor = None
```
> Tick là **fallback**. Đường chính chốt ở OnLMBReleased (input-event timing, không nháy gizmo).

---

## OnLMBReleased — FULL FLOW (v1.5) ⭐ đường chính chốt selection
```
SET bLMBHeld = False                                   ← đầu tiên!
Sequence:
  Then 0: đóng context menu nếu đang mở (IsValid(ContextMenuRef) → Remove from Parent → SET None)

  Then 1: Branch bIsBoxSelecting == True:               ← ĐANG kéo box, vừa thả
            True →
              Get Mouse Position on Viewport → EndPos
              Call FinishBoxSelect(EndPos)
              Branch IsValid(BoxSelectOverlayRef) → Call HideBox
              SET bIsBoxSelecting = False
              SET PendingClickActor = None

  Then 2: Branch bIsPendingBoxSelect == True:            ← CLICK đơn (chưa từng kéo)
            True →
              SET bIsPendingBoxSelect = False
              Branch IsValid(PendingClickActor):
                True  → SelectSingleActor(PendingClickActor) → CaptureSnapshot("Select") → SET PendingClickActor=None
                False → Branch IsInputKeyDown(Left Ctrl):
                          True  → (dead-end, giữ selection — Ctrl+click nền không deselect)
                          False → DeselectAll → CaptureSnapshot("Deselect")
                                  → Branch bIsReplaceMode → (exit replace mode chain nếu đang replace)
```
**Lưu ý timing:** OnLMBReleased (input event) chạy TRƯỚC world Tick cùng frame → ActivateGizmo gọi từ đây KHÔNG nháy. Tick chỉ dọn nốt edge case.

---

## FinishBoxSelect(EndPos : Vector2D) — Function (v1.5)
```
Min/Max → TopLeft = (Min X, Min Y), BottomRight = (Max X, Max Y) từ BoxStartPos & EndPos
CLEAR LocalSelected (local array)

Get All Actors With Tag("FurnitureSpawned") → ForEach (Actor):
  Branch (Actor != PendingClickActor):                 ← loại mesh mà ta bắt đầu kéo box TỪ TRÊN nó
    True →
      Cast To BP_FurnitureActor → IsValid →
      Get Actor Location → Project World To Screen → ScreenPos
      ← ⚠️ FIX DPI: chia ScreenPos cho Get Viewport Scale (Widget Layout Library) = ScreenPosFixed
      Branch (ScreenPosFixed.X >= TopLeft.X AND <= BottomRight.X)   [nested Branch, không dùng AND node]
        AND (ScreenPosFixed.Y >= TopLeft.Y AND <= BottomRight.Y):
          True → ADD Actor → LocalSelected

Completed:
  Branch LENGTH(LocalSelected) > 0:
    True →
      Branch IsInputKeyDown(Left Ctrl):
        True  → ForEach LocalSelected → ToggleActor   ← Ctrl: cộng dồn vào selection cũ
        False → DeselectAll → SelectActors(LocalSelected)
      → CaptureSnapshot("BoxSelect")
```
**⚠️ Bug đã trả giá — DPI mismatch:** `Get Mouse Position on Viewport` trả tọa độ LOGICAL (đã chia DPI); `Project World To Screen` trả PIXEL THÔ. So sánh trực tiếp → chọn nhầm/lệch đồ. Phải chia `Project World To Screen` cho `Get Viewport Scale` để cùng hệ tọa độ với mouse.

**Lưu ý chủ đích (KHÔNG phải bug):** chọn theo **PIVOT/origin** của đồ (1 điểm), không theo bounding box. Đồ chỉ "vào khung" khi điểm gốc nằm trong khung. Đúng ý đồ thiết kế.

---

## MULTI-SELECT FUNCTIONS (v1.4 — T4, T5)

### CalculateCenter(Actors) → Vector (T4)
Tính trung bình vị trí các actor → tâm nhóm.

### CalculateComboAnchor(InActors : Array\<BP_FurnitureActor\>) → Vector (C4)
Anchor điểm đặt combo: center XY + anchorZ. Dùng thay CalculateCenter trong CB_SaveCombo_Handler.
anchorZ = MinZ khi có đồ Floor/Wall; MaxZ khi ALL đồ là Ceiling.
**Local vars:** ActorsCopy, SumX, SumY (Float=0), MinZ (Float=99999999), MaxZ (Float=-99999999), Count (Integer=0), bAllCeiling (Boolean=true)
```
Entry
  ▶→ Branch(Length(InActors) == 0)
       True  ▶→ Make Vector(0,0,0) → Return
       False ▶→ SET ActorsCopy=InActors, SumX=0, SumY=0, MinZ=99999999, MaxZ=-99999999, Count=0, bAllCeiling=true
             ▶→ ForEach(ActorsCopy)

Loop Body (actor):
  Branch(IsValid(actor))
    False ▶→ dead-end
    True  ▶→ GetActorLocation → Break Vector → X, Y, Z
          ▶→ SET SumX = SumX+X
          ▶→ SET SumY = SumY+Y
          ▶→ SET MinZ = Min(float)(MinZ, Z)
          ▶→ SET MaxZ = Max(float)(MaxZ, Z)
          ▶→ SET Count = Count+1
          ▶→ GET actor.PlacementSurfaceType → st
          ▶→ Branch(st == "Ceiling")
                False ▶→ SET bAllCeiling=false ▶→ dead-end
                True  ▶→ dead-end

Completed:
  ▶→ avgX = SumX / ToFloat(Count)
  ▶→ avgY = SumY / ToFloat(Count)
  ▶→ Select(Pick=bAllCeiling, True=MaxZ, False=MinZ) ●→ anchorZ
  ▶→ Make Vector(avgX, avgY, anchorZ) ●→ ReturnVec → Return
```
> **Bài học C4:** anchor center-bottom (sàn) / center-top (trần) → relLocation.z ≈ 0 cho đồ đặt trên sàn → spawn đúng chỗ. CalculateCenter (centroid) dùng cho gizmo multi-select + copy/paste — giữ nguyên.

### SpawnOrUpdatePivot (T4)
```
Guard: LENGTH SelectedActors < 2 → return
CalculateCenter(SelectedActors) → Center
Branch NOT IsValid(GizmoPivotActor): True → Spawn BP_PivotActor → SET GizmoPivotActor
SET Actor Location(GizmoPivotActor, Center)
SET GizmoPivotActor.AttachedActors = SelectedActors
Call RefreshOffsets(GizmoPivotActor)
```

### DestroyPivot (T4)
IsValid(GizmoPivotActor) → Destroy Actor → SET GizmoPivotActor = None

### DeselectAll (T5 → v1.6)
```
ForEach SelectedActors (Actor):
  Branch IsValid(Actor): True → GET FurnitureMesh → Set Render Custom Depth = False
CLEAR SelectedActors
SET PrimarySelectedActor = None
SET SelectedFurnitureActor = None
DeactivateGizmo
DestroyPivot
Broadcast OnSelectionChanged([], None)
⚠️ v1.6: ĐÃ XÓA Broadcast OnMeshDeselected (giữ nguyên phần clear state)
⚠️ KHÔNG gọi CaptureSnapshot ở đây (infinite loop)
⚠️ IsValid trước mọi Object access (chống crash "pending kill")
⚠️ KHÔNG có CaptureSnapshot nội bộ — caller tự gọi sau
```

### SelectSingleActor(Actor) (T5 → v1.6)
```
DeselectAll → ADD Actor → SelectedActors → SET Primary → UpdateOutlineState → UpdateGizmo
→ Broadcast OnSelectionChanged(SelectedActors, Primary)
⚠️ KHÔNG có CaptureSnapshot nội bộ — caller tự gọi sau (xác nhận 07/06)
⚠️ v1.6: ĐÃ XÓA Broadcast OnMeshSelected (chỉ còn OnSelectionChanged)
```

### SelectActors(Actors) (T5)
```
⚠️ Actors là Pass-by-Reference → KHÔNG iterate trực tiếp
SET ActorsCopy = Actors  (bản copy)
ForEach ActorsCopy (Actor):
  Contains(SelectedActors, Actor) → NOT → Branch True → ADD to SelectedActors
ForEach Completed:
  Branch LENGTH > 0 → SET Primary = Last → SET SelectedFurnitureActor
  → UpdateOutlineState → UpdateGizmo → Broadcast OnSelectionChanged
```
**Lưu ý:** caller (Paste/Duplicate/Restore/BoxSelect) phải DeselectAll trước khi gọi (SelectedActors rỗng) → vòng Contains không trùng.

---

## GROUP FUNCTIONS (v1.6 — Sprint 3)

### GenerateGroupID() → String
`New Guid → To String → Append "g_" prefix` → "g_<GUID>".

### GetGroupChildren(InGroupID) → Array<BP_FurnitureActor>
```
CLEAR Children (đầu hàm)
Get All Actors With Tag("FurnitureSpawned") → ForEach:
  Cast → IsValid → Branch (GroupID == InGroupID): True → ADD to Children
  (Cast Failed KHÔNG nối Return)
Return Children
```

### FindGroupData(InGroupID) → (S_GroupData, Index, bFound)
ForEach Groups → Break → so GroupID → match: trả data + index + true.

### ExpandSelectionWithGroups(RawActors) → Array<BP_FurnitureActor>  ⭐ keystone
**v1.7: VIẾT LẠI** dùng ResolveSelectionUnit (thay logic inline Sprint 3):
```
SET ActorsCopy = RawActors; CLEAR LocalResult
GetCurrentEditScope() → Scope
ForEach ActorsCopy (Actor):
  ResolveSelectionUnit(Actor, Scope) → ForEach_inner (Unit):
    NOT Contains(LocalResult, Unit) → ADD Unit → LocalResult
Completed → Return LocalResult
```
> Tick fallback (Event Tick Branch A) cũng đổi từ SelectSingleActor → DeselectAll+ExpandSelectionWithGroups+SelectActors cho nhất quán.
Dùng ở: click resolution (OnLMBReleased), box select (FinishBoxSelect), và (Sprint 4) nested.

### CreateGroup() — Ctrl+G — **v1.9: VIẾT LẠI bottom-up nesting (F3)**
> Thay đổi chính: gọi `ComputeSelectionUnits` TRƯỚC guard; guard kiểm tra tổng số units (không dùng SelectedActors.Length — Luật 6B structural symmetry). `GroupNameCounter` đọc/ghi qua ContainerRef.
```
Entry →
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

### UngroupActors(InGroupID) — Ctrl+Shift+G — **v1.8: VIẾT LẠI peel-one-level**
> Semantic mới: ungroup đúng 1 cấp. Actor trực tiếp về cha. Sub-group đổi cha về cha. Chỉ xóa target.
> Flat group: WalkUpUntilParent(gid,"")=gid (scope rỗng) → giống Sprint 3, không regression.
> **Local vars (v1.8):** `target`, `parentGID`, `scope` (String); `LocalNewGroups`, `LocalKeep` (Array S_GroupData). ĐÃ XÓA `FoundIdx`/`Root`/`LocalRemoveIDs` cũ.
```
Entry → Branch(InGroupID == ""):
          True  → Return
          False → GetCurrentEditScope → SET scope
                → WalkUpUntilParent(InGroupID, scope) → SET target
                → Branch(target == ""): True → Return
                → FindGroupData(target) → (data, Found)
                → Branch(Found == False): True → Return
                → BREAK data → GET ParentGroupID → SET parentGID

       ← B1: actor con trực tiếp → về cha
       → GetGroupChildren(target) → ForEach_1(actor):
            LoopBody → Cast → SET GroupID = parentGID
            Completed →

       ← B2: rebuild Groups — sub-group con trực tiếp đổi ParentGroupID về cha
            CLEAR LocalNewGroups
            ForEach_2 Groups (g):
              LoopBody → Branch(g.ParentGroupID == target):
                           True  → MAKE S_GroupData(GroupID=g.GroupID, GroupName=g.GroupName,
                                       ParentGroupID=parentGID, bIsLocked=g.bIsLocked)
                                 → ADD → LocalNewGroups
                           False → ADD g (nguyên gốc) → LocalNewGroups
              Completed → SET Groups = LocalNewGroups

       ← B3: xóa target khỏi Groups (rebuild, bỏ qua target)
            CLEAR LocalKeep
            ForEach_3 Groups (g2):
              LoopBody → Branch(g2.GroupID != target):
                           True  → ADD g2 → LocalKeep
                           False → (để trống)
              Completed → SET Groups = LocalKeep
                        → SyncGroupsToContainer
                        → CaptureSnapshot("Ungroup")     ← 1 lần duy nhất ở Completed
                        → SelectActors(SelectedActors)   ← re-fire info bar
                        → Broadcast OnGroupDestroyed(target)
```
**⚠️ Bug đã trả giá:** CaptureSnapshot CHỈ ở ForEach_3.Completed (không trong LoopBody → spam). FindGroupData không có output Index → dùng rebuild pattern (B2/B3), KHÔNG Set Array Elem.

### SyncGroupsToContainer()
Get All Actors Of Class(BP_GroupsContainer) → Get(0) → IsValid → SET Container.Groups = self.Groups (đẩy bản in-memory xuống container để EMS save).

### PruneEmptyGroups() — **v1.8: đổi tiêu chí keep**
```
CLEAR LocalKeep                              ← local Array S_GroupData
ForEach Groups (g):
  Loop Body →
    GetAllDescendantActors(g.GroupID) → Length   ← THAY GetGroupChildren (xét cả subtree)
    Branch(Length > 0):
      True  → ADD g → LocalKeep
      False → (để trống)
Completed → SET Groups = LocalKeep → SyncGroupsToContainer
```
> GetGroupChildren (cũ) chỉ check direct members → prune oan group cha nested có sub-groups. GetAllDescendantActors nhìn cả cây → cascade đúng 1 pass. Gọi trong DeleteSelected.

---

## EDIT MODE FUNCTIONS (v1.7 — Sprint 4 T1-T4)

### GetCurrentEditScope() → String
```
Branch(EditModeStack.Length > 0):
  True  → EditModeStack → Last Index → GET → Return
  False → Return ""
```

### GetChildGroups(InGroupID) → Array<S_GroupData> — group con TRỰC TIẾP (dựa ParentGroupID)
```
CLEAR LocalChildren
ForEach Groups (g): Branch(g.ParentGroupID == InGroupID): True → ADD g
Completed → Return LocalChildren
```

### GetGroupRoot(InGroupID) → String — leo ngược tới gốc, depth guard 10
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
⚠️ Local var độc lập mỗi stack frame (đã verify). Fallback iterative nếu cần.

### GetGroupsInHierarchy(InGroupID) → Array<S_GroupData> ⭐ ĐỆ QUY (bridge Combo S5)
```
CLEAR LocalGroups
FindGroupData(InGroupID) → bFound: True → ADD data → LocalGroups
(merge) → GetChildGroups(InGroupID) → ForEach_1 (cg):
  GetGroupsInHierarchy(cg.GroupID) → ForEach_2: ADD Element → LocalGroups
  Completed → (để trống)
Completed → Return LocalGroups
```

### ResolveSelectionUnit(Actor, EditScope) → Array<BP_FurnitureActor> ⭐ NÃO Sprint 4
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
    ancestor=="" → Return []
  False →                                        ← KHÔNG EDIT
    gid=="" → Return [Actor]                     ← đồ rời → chính nó
    GetGroupRoot(gid) → root → Return GetAllDescendantActors(root)   ← group → cả cây
```

### GetEditBreadcrumb() → String — "Nhóm 1 › Nhóm 2" cho info bar
```
SET Result = ""
ForEach EditModeStack (Element, ArrayIndex):
  FindGroupData(Element) → bFound:
    False → Return Result (early exit — data lỗi)
    True → ArrayIndex==0: SET Result = GroupName
           Else: SET Result = Append(Result, "›", GroupName)
Completed → Return Result
```

### ApplyEditModeVisual() / RemoveEditModeVisual() — STUB RỖNG (T9 đổ body, dim Stencil 200)

### EnterEditMode(InGroupID)
```
InGroupID=="" → Return
FindGroupData(InGroupID) → bFound==False → Return
ADD InGroupID → EditModeStack
DeselectAll → ApplyEditModeVisual
Broadcast OnEditModeChanged(True, InGroupID)
```

### ExitEditModeOneLevel() — nút "↑ Lên 1 cấp"
```
EditModeStack.Length==0 → Return
GetCurrentEditScope() → SET Exited
EditModeStack → Last Index → REMOVE INDEX (POP)
Branch(EditModeStack.Length==0):
  True (thoát hẳn) →
    RemoveEditModeVisual → DeselectAll
    GetAllDescendantActors(Exited) → LocalTree
    LocalTree.Length>0 → SelectActors(LocalTree)   (cả 2 nhánh merge về Broadcast)
    Broadcast OnEditModeChanged(False, "")
  False (còn cấp cha) →
    ApplyEditModeVisual → DeselectAll
    GetAllDescendantActors(Exited) → LocalTree
    LocalTree.Length>0 → SelectActors(LocalTree)
    GetCurrentEditScope() → NewScope
    Broadcast OnEditModeChanged(True, NewScope)
```
> DeselectAll trước SelectActors (SelectActors chỉ ADD). GetAllDescendantActors (không phải GetGroupChildren) — chống fail nested thuần.

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
Else →
  WalkUpUntilParent(gid, Scope) → Sub
  Sub!="" → EnterEditMode(Sub)
  Sub=="" → Return
```

---

## SELECTION LABEL / UNIT FUNCTIONS (v1.9 — Sprint 4 Bug Fix)

### GetSelectionUnitLabel(Primary, Count) → String (F1) — label info bar, phân biệt đồ rời vs group
```
GetCurrentEditScope() → scope
Branch(scope != ""):          ← đang edit
  True:
    GET Primary.GroupID → gid
    Branch(gid=="" OR gid==scope):
      True  → Return (Count + " vật thể")
      False → WalkUpUntilParent(gid, scope) → unitGID → FindGroupData → bFound:
                True  → Return "📦 " + GroupName + " (" + Count + ")"
                False → Return (Count + " vật thể")
  False:                        ← ngoài edit
    GET Primary.GroupID → gid
    Branch(gid==""):
      True  → Return (Count + " vật thể")
      False → GetGroupRoot(gid) → rootGID → FindGroupData → bFound:
                True  → Return "📦 " + GroupName + " (" + Count + ")"
                False → Return (Count + " vật thể")
```
> Chỉ gọi khi Actors.Length >= 2. Caller (WBP_MeshControls) lo guard.

### ComputeSelectionUnits(InActors) → (OutGroupUnits: Array<String>, OutLooseActors: Array<BP_FurnitureActor>) (F3)
> Phân tách actors thành "đơn vị group" (top-level group IDs) + "đồ rời" cho CreateGroup bottom-up.
```
Buffer (class var): TempGroupUnits (Array String), TempLooseActors (Array BP_FurnitureActor) — CLEAR đầu hàm
GetCurrentEditScope() → scope
SET ActorsCopy = InActors
ForEach ActorsCopy (actor):
  IsValid(actor)==False → skip
  True:
    GET actor.GroupID → gid
    Branch(gid==""):
      True  → ADD actor → TempLooseActors
      False:
        Branch(scope==""): True → GetGroupRoot(gid) → unitGID
                           False → WalkUpUntilParent(gid, scope) → unitGID
        Branch(unitGID!=""):
          True  → Contains(TempGroupUnits, unitGID)==False → ADD unitGID → TempGroupUnits
          False → ADD actor → TempLooseActors   ← fallback
Completed:
  SET OutGroupUnits = TempGroupUnits
  SET OutLooseActors = TempLooseActors
```
> ⚠️ Output pin Function không CLEAR được → dùng Temp buffer, assign ở Completed. ForEach Completed phải nối SET outputs — không dead-end.

---

### ToggleActor(Actor) (T5, T7)
```
Branch Contains(SelectedActors, Actor):
  True  → Remove from SelectedActors → Set Render Custom Depth=False (clear stencil)
  False → ADD to SelectedActors
SET Primary = (last actor còn lại / Actor vừa thêm)
UpdateOutlineState → UpdateGizmo → Broadcast OnSelectionChanged
⚠️ KHÔNG có CaptureSnapshot nội bộ — caller gọi sau toggle
```

### UpdateOutlineState (T5)
```
ForEach SelectedActors (Actor):
  IsValid → GET FurnitureMesh → Set Render Custom Depth=True
  Branch Actor == PrimarySelectedActor:
    True  → Set Custom Depth Stencil Value = 255  (primary)
    False → Set Custom Depth Stencil Value = 254  (secondary)
```

### UpdateGizmo (T5)
```
GET LENGTH SelectedActors:
  == 0 → DeactivateGizmo + DestroyPivot
  == 1 → DestroyPivot → ActivateGizmo(SelectedActors[0])
  >= 2 → DeactivateGizmo (TRƯỚC!) → SpawnOrUpdatePivot → ActivateGizmo(GizmoPivotActor) → SetActorTickEnabled(GizmoPivotActor, True)
```
**Deviation:** nhánh >=2 phải DeactivateGizmo trước ActivateGizmo (plan bỏ sót).

---

## CONTEXT MENU FUNCTIONS (v1.5 — Sprint 2 T3-T6)
**Widget:** WBP_ContextMenu (container) + WBP_ContextMenuItem (mỗi dòng) + WBP_MenuSeparator.

### Right-click handler (T4)
```
Phát hiện right-click: dùng time-based + check camera đang xoay/pan (cursor bị lock khi pan)
→ nếu là click thật (không phải kết thúc pan):
   IsValid(ContextMenuRef) → Remove cũ → SET None    (chỉ 1 menu cùng lúc)
   Create Widget(WBP_ContextMenu) → SET ContextMenuRef → Add to Viewport
   Set Position In Viewport(vị trí chuột)
   Bind callback các item
```
> Menu đóng bằng background button (full-screen invisible button phía sau menu) + đóng ở OnLMBReleased Then 0.

### Callbacks (T5-T6)
```
CB_Copy       → CopyMesh
CB_Duplicate  → DuplicateMesh
CB_Paste      → PasteMesh
CB_ResetRotation → ResetRotation
CB_SelectSimilar → SelectSimilarMesh
CB_Delete     → DeleteSelected
CB_Undo       → UndoManager.UndoLastAction
CB_Redo       → UndoManager.RedoLastAction
CB_ChangeMaterial → [STUB — TODO, làm tiếp session sau]
CB_Replace        → [STUB — TODO, làm tiếp session sau]
CB_SaveCombo      → CB_SaveCombo_Handler
```

### CB_SaveCombo_Handler (C3b — 24/06/2026; C4: CalculateComboAnchor)
```
Guard LENGTH(SelectedActors) < 2 → dead-end
CalculateComboAnchor(SelectedActors) → Center  ← C4: đổi từ CalculateCenter để anchor z≈0
Get All Widgets Of Class(WBP_FurnitureInventory) → Get(0) → IsValid → Cast → InventoryRef
Branch IsValid(InventoryRef):
  True  → InventoryRef.OpenSaveComboDialog(SelectedActors=SelectedActors, Center=Center)
  False → Print String "CB_SaveCombo: Inventory ref not found"
```
> Không gọi SaveComboFromSelection trực tiếp — delegate sang inventory để inventory đóng băng selection + quản lý dialog async.

### SelectSimilarMesh (T5)
```
Guard IsValid(PrimarySelectedActor)
GET PrimarySelectedActor.MeshPath → TargetPath (String)
DeselectAll
Get All Actors With Tag("FurnitureSpawned") → ForEach:
  Cast → IsValid → Branch (MeshPath == TargetPath):   ← so SÁNH STRING, KHÔNG load DA (nhẹ)
    True → ADD to LocalSimilar
Completed → SelectActors(LocalSimilar) → CaptureSnapshot("SelectSimilar")
```

### ResetRotation (T6)
ForEach SelectedActors → IsValid → Set Actor Rotation(0,0,0) → CaptureSnapshot("ResetRotation").

### DeleteSelected (T6)
```
ForEach SelectedActors (Actor):
  IsValid → Destroy Actor(Actor)        ← target = Array Element, KHÔNG phải self
Completed → DeselectAll → CaptureSnapshot("Delete")
```
**⚠️ Bug đã trả giá:** target của Destroy phải là Array Element (đồ đang duyệt), KHÔNG để trống (mặc định self = destroy chính InputManager).

---

## Mouse Left Released (gizmo) — v1.4
```
GizmoController → OnMouseReleased
[T15: CaptureSnapshot khi SelectedActor là Pivot — đã làm]
```

---

## v1.2 — Keyboard Manipulation (UX Phase 2.1)

### B1 — Arrow Key Nudge (MULTI v1.4 — T10)
**Chi tiết:** `B1_Nudge_Flow.md`
- `NudgeMesh(Direction)` — guard `SelectedActors.LENGTH==0 → return`; direction tính từ `PrimarySelectedActor.PlacementSurfaceType`; **ForEach SelectedActors → Add Actor World Offset**; sau ForEach: CalculateCenter → SetActorLocation(Pivot) → RefreshOffsets.
- `CaptureNudgeSnapshot` — debounce 0.5s.
- **Event Tick free mode** — `SnapStep==0 AND SelectedActors.LENGTH>0` → ForEach SelectedActors di chuyển × DeltaTime × NudgeSpeed → cập nhật Pivot.

### B2 — Copy/Paste/Duplicate (MULTI v1.4 — T11)
**Chi tiết:** `B2_CopyPaste_Flow.md`
- `CopyMesh` — CLEAR ClipboardActors → CalculateCenter → ForEach SelectedActors build S_ClipboardEntry (RelativeLocation = ActorLoc - Center) → ADD.
- `PasteMesh` — trace surface → DeselectAll → CLEAR LocalSpawned → ForEach ClipboardActors spawn (bAutoSelect=False) → SelectActors(LocalSpawned) → CaptureSnapshot.
- `DuplicateMesh` — CopyMesh → ForEach SelectedActors tính MaxRightEdge (**phần spawn nối COMPLETED, KHÔNG Loop Body**) → DeselectAll → CLEAR LocalSpawned → ForEach ClipboardActors spawn (bAutoSelect=False) → SelectActors(LocalSpawned) → CaptureSnapshot.
- `SpawnFurnitureCopy(...) → NewActor` — **v1.6:** đoạn tail thay cụm select thủ công (SET SelectedFurnitureActor + Set Custom Depth Stencil + Set Render Custom Depth + Select/ActivateGizmo + Call OnMeshSelected) bằng `Deselect Mesh → SelectActors(Make Array(NewActorCopy)) → Return`. SelectActors tự lo outline (Stencil **255** chuẩn) + gizmo + fire OnSelectionChanged. Return Node nối NewActorCopy ở CẢ True và False branch.
  **v1.9 (F4 — auto-join edit scope):** trong **Sequence.Then 0**, ngay SAU `ADD "FurnitureSpawned" → SET Tags`: `GetCurrentEditScope() → Scope`; `Branch(Scope != "")`: True → `SET NewActorCopy.GroupID = Scope`; False → dead-end (HỢP LỆ vì trong Sequence.Then 0, Sequence tự fire Then 1). → đồ spawn khi đang edit group tự nhận GroupID của scope.
  **v2.1 (19/06/2026 — async load):**
  - Step 2: `Call NewActorCopy.LoadMeshAsync(MeshPath)` [thay Load Asset Blocking mesh]
  - Step 4: `SET NewActorCopy.MaterialOverrides = MaterialOverrides` [giữ] → `Call NewActorCopy.LoadMaterialsAsync(Overrides=MaterialOverrides, Index=0)` [thay ForEach Load Asset Blocking material]
  - **NewActorCopy:** local variable (không phải class var từ v2.1) — tránh aliasing khi RestoreSnapshot gọi SpawnFurnitureCopy trong ForEach
  - **Add Recent Mesh:** parse MeshPath (không phải DAPath) — DAPath rỗng với đồ Sprint D

---

## Event End Play (chống VRAM leak) — v1.5
```
IsValid(CurrentMeshControls) → Remove from Parent
IsValid(SelectedFurnitureActor) → Set Render Custom Depth = False
ForEach SelectedActors → IsValid → Set Render Custom Depth = False
CLEAR SelectedActors
SET PrimarySelectedActor = None, GizmoPivotActor = None
← v1.5:
IsValid(BoxSelectOverlayRef) → Remove from Parent → SET None
IsValid(ContextMenuRef) → Remove from Parent → SET None
SET PendingClickActor = None
← v1.6:
CLEAR Groups
CLEAR MeshesToReplace
← v1.7:
CLEAR EditModeStack
```

---

## DeselectMesh (Function — single, cũ → v1.6)
```
Cast SelectedFurnitureActor → GET FurnitureMesh → Set Render Custom Depth = False
SET SelectedFurnitureActor = None → DeactivateGizmo
⚠️ v1.6: ĐÃ XÓA Broadcast OnMeshDeselected (giữ phần clear state)
⚠️ KHÔNG CaptureSnapshot ở đây (infinite loop)
⚠️ Chỉ còn được Call trong SpawnFurnitureCopy (clear trước SelectActors)
```

---

## Cách BP khác lấy reference
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
```
⚠️ KHÔNG dùng Get Player Controller → Cast BP_FoffPlayerController
⚠️ Chỉ có 1 instance (đã verify count=1 trong session 07/06)

---

## Level Blueprint — Spawn Order
```
1. BP_UndoManager   2. BP_FurnitureSceneManager   3. BP_TransformerPawn
4. BP_GizmoController   5. BP_FurnitureInputManager (SET GizmoControllerRef)
6. WBP_MeshControls (SET CurrentMeshControls)   7. CaptureSnapshot("Initial")
```

---

## StartReplaceMode(Actors : Array<BP_FurnitureActor>) — v1.4 + v1.10 update
> Document lần đầu v1.10 (đã có trong Blueprint từ v1.4). Gọi từ BTN_Replace (WBP_MeshControls) khi bIsReplaceMode == False.

```
Branch LENGTH(Actors) == 0: True → Return

SET MeshesToReplace = Actors
SET bIsReplaceMode = True

Get Game Instance → GET FurnitureInventoryRef → IsValid:
  True  → EnsureExpanded → EnterReplaceMode
  False → Create WBP_FurnitureInventory → Add to Viewport → SET FurnitureInventoryRef

← v1.10: navigate folder cho Primary actor dùng RowName (fallback DAPath cho save cũ)
Branch LENGTH(Actors) == 1:
  True:
    Cast Actors[0] → GET RowName
    Branch(RowName != ""):
      True  → GetDataTableRow(DT_FurnitureCatalog, RowName) → MeshFolderPath → FilterByFolderPathWithUI
      False → GET DAPath → Load Blocking → Cast DA → MeshFolderPath → FilterByFolderPathWithUI
  False: (multi → không navigate)
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 21/04/2026 | Tạo mới |
| 1.1 | 19/05/2026 | Event Dispatchers OnMeshDeselected + OnMeshSelected |
| 1.2 | 21/05/2026 | UX Phase 2.1: B1 Nudge + B2 Copy/Paste/Duplicate |
| 1.3 | 22/05/2026 | PlacementSurfaceType support |
| 1.4 | 04/06/2026 — 15:30 ICT | Multi-Select (Sprint 1 T1-T14) |
| 1.5 | 07/06/2026 — 22:40 ICT | **Sprint 2 — Box Select + Context Menu.** Vars Box Select (BoxSelectOverlayRef, BoxStartPos, bIsPendingBoxSelect, bIsBoxSelecting, bLMBHeld, PendingClickActor) + ContextMenuRef. BeginPlay tạo WBP_BoxSelectOverlay. **Mouse Left Pressed refactor → DEFER** (PendingClickActor, không select ngay). **Event Tick** box branch (guard inventory + ngưỡng 5px + vẽ khung). **OnLMBReleased** = đường chính chốt selection. **FinishBoxSelect** (DPI fix chia Get Viewport Scale). Context Menu callbacks (Copy/Duplicate/Paste/ResetRotation/SelectSimilar/Delete/Undo/Redo; ChangeMaterial+Replace còn STUB). Xác nhận SelectSingleActor/DeselectAll/ToggleActor KHÔNG chứa CaptureSnapshot nội bộ. |
| 1.6 | 10/06/2026 — 20:34 ICT | **Sprint 3 Group + Regression-fix + Refactor dispatcher.** Vars: `Groups` (Array S_GroupData), `FoundIdx` (-1); đổi `MeshToReplace`(single)→**XÓA**, dùng `MeshesToReplace`(array). **Dispatchers: XÓA `OnMeshSelected` + `OnMeshDeselected`** → `OnSelectionChanged` là duy nhất; thêm `OnGroupCreated`/`OnGroupDestroyed`. Group functions (GenerateGroupID, GetGroupChildren, FindGroupData, ExpandSelectionWithGroups, CreateGroup Ctrl+G, UngroupActors Ctrl+Shift+G, SyncGroupsToContainer, PruneEmptyGroups). Mouse Pressed Step 7 bỏ nhánh Ctrl (mọi click defer). SelectSingleActor/DeselectMesh/DeselectAll bỏ broadcast cũ. SpawnFurnitureCopy tail dùng SelectActors. UngroupActors: find/remove/capture ở Completed + SET FoundIdx=-1 đầu hàm. End Play CLEAR Groups + MeshesToReplace. |
| 1.7 | 11/06/2026 — 18:14 ICT | **Sprint 4 T1–T5 — Edit Mode Slice 1.** Var `EditModeStack`. Dispatcher `OnEditModeChanged`. 7 helper: GetCurrentEditScope, GetChildGroups, GetGroupRoot, WalkUpUntilParent, GetAllDescendantActors (đệ quy), GetGroupsInHierarchy (đệ quy bridge Combo), ResolveSelectionUnit (não Sprint 4). GetEditBreadcrumb. 2 stub ApplyEditModeVisual/RemoveEditModeVisual. **ExpandSelectionWithGroups viết lại** dùng ResolveSelectionUnit. EnterEditMode/ExitEditModeOneLevel/ExitEditModeFull/TryEnterEditFromSelection. CLEAR EditModeStack ở End Play. |
| 1.8 | 12/06/2026 — 15:04 ICT | **Sprint 4 T6-T8 + Bug Fix.** **CreateGroup:** ParentGroupID=GetCurrentEditScope() (sau bị v1.9 thay). **PruneEmptyGroups viết lại** dùng GetAllDescendantActors. **UngroupActors viết lại peel-one-level** (scope→target→B1 actor về cha→B2 rebuild sub-groups→B3 xóa target). Local vars update (xóa FoundIdx/Root/LocalRemoveIDs, thêm target/parentGID/scope/LocalNewGroups/LocalKeep). Bug Fix cross-ref: GroupID preserved trong Replace Mesh (WBP_DragOverlay_FurnitureCard — Cast OldActor → GET GroupID → SET NewActor.GroupID TRƯỚC Destroy). |
| 1.9 | 15/06/2026 — 20:30 ICT | **Sprint 4 Bug Fix F1-F4.** Thêm `GetSelectionUnitLabel` (F1), `ComputeSelectionUnits` (F3). `GroupNameCounter` chuyển sang BP_GroupsContainer (F2, default=1 SaveGame). **CreateGroup viết lại bottom-up** (F3 — ComputeSelectionUnits trước guard, Luật 6B). **SpawnFurnitureCopy** auto-join edit scope (F4). |
| 1.10 | 17/06/2026 — Sprint D.T6 | Document `StartReplaceMode` + v1.10 update RowName branch. Ghi nhận + XÓA Step 11 Mouse Left Pressed (stale popup bug). |
| 2.1 | 19/06/2026 — 19h ICT | Load mesh+material async qua BP_FurnitureActor.LoadMeshAsync/LoadMaterialsAsync; NewActorCopy đổi class var → local var; Add Recent Mesh parse MeshPath thay DAPath |
| 2.2 | 24/06/2026 | C3b: CB_SaveCombo đổi luồng — KHÔNG gọi SaveComboFromSelection trực tiếp nữa. Guard ≥2 đồ → CalculateCenter → Get All Widgets WBP_FurnitureInventory → OpenSaveComboDialog (delegate sang inventory). |
| 2.3 | 24/06/2026 | C4: Thêm `CalculateComboAnchor` — center XY + anchorZ (MinZ sàn / MaxZ trần). CB_SaveCombo_Handler: đổi `CalculateCenter` → `CalculateComboAnchor`. |
