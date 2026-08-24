# BP_FurnitureInputManager
**Phiên bản:** 3.5 | **Cập nhật:** 24/08/2026 — `OnRMBPressed`/`OnRMBReleased` (Right-click handler T4) re-export ✓K2 24/08/2026: cơ chế time-based + camera-rotation-delta thay mô tả cũ chưa từng verify; thêm biến `RMBPressTime`/`RMBPressCamRot`; `OnRightClick()` (callee) internals CHƯA verify đợt này, giữ mô tả cũ dạng `[⚠ suy luận]`. Ghi nhận `IA_RMBPress`/`IA_RMBRelease` chưa có trong bảng Input Action chính thức | Actor riêng — input hub + multi-select hub + box-select hub + context-menu hub + group hub + edit-mode hub

> **v2.8 (Replace UX Fix P0→P5, 02/08/2026):** biến `MeshToReplace` (single, dead code) XÓA HOÀN
> TOÀN (P4.4) — đính chính dòng Variables ghi sai đã "xóa từ v1.6". Node flow re-route (P2), card
> container (P1.3), clear đường thoát (P4.2), undo (P4.3) đều nằm ở `WBP_FurnitureInventory.md`
> (xem file đó, `ReplaceTarget`/`ResolveSelectedComboRoot`/`StartReplaceMode`/`StartReplaceComboMode`
> ở đây không đổi logic, chỉ được gọi từ route mới).

> **HỢP NHẤT TỪ:** base v1.6 + patch v1.7 + patch v1.8 + patch v1.9 (15/06/2026). Đây là bản đầy đủ, thay thế toàn bộ file gốc + patch trong import_raw.
> **File canonical.** `BP_FurnitureInputManager_MERGED_v1.9.md` là bản duplicate — đã bị xóa thật (cuhoang 02/08/2026, sau khi ở trạng thái "đánh dấu xóa" từ 17/06/2026 mà chưa ai xóa). Lịch sử nằm trong git. Chỉ đọc file này.
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
ReplaceTarget          : E_ReplaceTarget   ← [MIGRATE, C9.0c, xác nhận qua K2Node export 24/07/2026]
                                              thay `bIsReplaceMode` (Boolean) cũ — enum hỗ trợ
                                              nhiều loại replace target (None/Mesh/Combo — delta
                                              24/07 dẫn "DEVIATIONS.md §11", nhưng KHÔNG tìm thấy
                                              mục này trong file canonical hiện tại, có thể nằm ở
                                              doc khác chưa phân phối vào đây — cần cuhoang xác
                                              nhận nguồn thật). Migration xảy ra NGOÀI phiên Claude
                                              Code — doc trước đây không hề biết, chỉ ghi nhận lại
                                              qua export thật.
MeshesToReplace        : Array of BP_FurnitureActor   ← v1.6: thay MeshToReplace (single). CLEAR ở End Play
                                                        [ĐÍNH CHÍNH 02/08/2026] dòng cũ ghi "đã XÓA MeshToReplace
                                                        single" từ v1.6 (10/06/2026) — SAI, biến đó thật ra vẫn tồn
                                                        tại làm dead code (chỉ còn 1 chỗ SET rác ở BTN_Close,
                                                        WBP_FurnitureInventory.md) cho tới khi Replace UX Fix P4.4
                                                        (02/08/2026) mới xóa THẬT bằng Find References + compile
                                                        sạch. `MeshToReplace` (single) — XÓA HOÀN TOÀN 02/08/2026,
                                                        KHÔNG nhầm với `MeshesToReplace` (array, dòng này, vẫn dùng
                                                        thật, GIỮ NGUYÊN).
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
RMBPressTime         : Float (double)         ← [✓K2 24/08/2026] GetGameTimeInSeconds() lúc OnRMBPressed
RMBPressCamRot       : Rotator                ← [✓K2 24/08/2026] camera rotation lúc OnRMBPressed, CHỈ ĐỌC để so sánh lúc thả
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

## Event Tick — Box Select branch (v1.5, verified qua K2Node export 24/07/2026 — C9.0c)
> Đặt SAU nhánh nudge free-mode, dùng **Sequence** để không phá logic cũ.

⚠️ **Verified qua K2Node export thật 24/07/2026** (Ctrl+A → Ctrl+C → paste, không suy đoán qua
ảnh chụp). Không sửa logic (đã đúng sẵn từ trước migrate) — chỉ bổ sung 2 chỗ doc trước đây ghi
thiếu: (1) guard OR trước `HideBox` ở nhánh cleanup, (2) chuỗi thoát Replace Mode sau
`DeselectAll` trong Branch A (đã tồn tại thật trong Blueprint, chỉ chưa từng được ghi vào doc).

**⚠️ Bug đã trả giá — phải GUARD inventory:** Event Tick chạy MỌI frame, KHÔNG bị gate bởi Input Mapping Context (`LM_FurnitureInput`) như các Enhanced Input action khác. Nếu không guard, box select kích hoạt cả khi inventory đóng → sai context. Guard thủ công:
```
GetGameInstance → Cast Foff_GameInstance → GET FurnitureInventoryRef
→ nested Branch: IsValid(FurnitureInventoryRef)  [Branch ngoài]
     True → Is In Viewport(FurnitureInventoryRef) [Branch trong]   ← KHÔNG dùng AND (Blueprint AND không short-circuit → crash None)
            True → SET bInventoryOpen = True
     (mọi nhánh khác → SET bInventoryOpen = False)

Branch bInventoryOpen:
  False → Branch(bIsPendingBoxSelect OR bIsBoxSelecting):     ← THÊM vào doc 24/07 (logic đã có sẵn, chỉ ghi thiếu)
            True  → Branch(IsValid BoxSelectOverlayRef):
                      True  → Call HideBox → SET bIsBoxSelecting=False → SET bIsPendingBoxSelect=False
                      False → dead-end
            False → dead-end
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
                         → Branch(IsReplaceModeActive):        ← THÊM vào doc 24/07 (logic đã có sẵn)
                              True  → SET ReplaceTarget = E_ReplaceTarget::None
                                      → Clear Array(MeshesToReplace)
                                      → Cast Foff_GameInstance → ExitReplaceMode
                              False → dead-end
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

### FindGroupData(InGroupID) → (S_GroupData, bFound)
ForEach Groups → Break → so GroupID → match: trả data + true.

⚠️ **[ĐÍNH CHÍNH 02/08/2026 — MERGE_LOG Q3 đóng]** Chữ ký ở trên trước đây ghi thêm output
`Index` — SAI, hàm KHÔNG có output Index. Xác nhận qua K2Node export 24/07/2026
(`Plans/24-07-2026_C9_Execution_Plan.md` §V6) và khớp với bài học "đã trả giá" ghi ngay dưới
`UngroupActors` (dòng dưới: *"FindGroupData không có output Index → dùng rebuild pattern"*) —
2 nguồn độc lập trong chính file này trước đây tự mâu thuẫn nhau.

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
  FindGroupData(Current) → (data, bFound)
  bFound==False → Return Current
  data.ParentGroupID=="" → Return Current
  Else → SET Current = data.ParentGroupID
Completed → Return Current
```

### WalkUpUntilParent(InGroupID, TargetParent) → String — tìm con trực tiếp của TargetParent trên đường leo
```
SET Current = InGroupID
ForLoop(0..9):
  FindGroupData(Current) → (data, bFound)
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

### GetGroupRoot(InGroupID) → RootGroupID : String

**Ghi as-built K2Node export 03/08/2026 (Save As/Save đè T0).**

```
Local: Current (String)
Entry ▶→ SET Current = InGroupID
      ▶→ ForLoop (FirstIndex=0, LastIndex=9)        → cap 10 vòng
           LoopBody ▶→ FindGroupData(Current) ─→ GroupData, bFound
                    ▶→ Branch(bFound == false)
                         True  ▶→ Return Current
                         False ▶→ Branch(ParentGroupID == "")
                                    True  ▶→ Return Current      → đã là root
                                    False ▶→ SET Current = ParentGroupID
                                             (then bỏ trống → hợp lệ, ForLoop tự chạy vòng sau)
           Completed ▶→ Return Current                            → hết 10 vòng chưa tới root
```

3 điều doc chưa từng ghi trước đợt Save As/Save đè:
1. **Cap 10 tầng, không phải đệ quy.** Vượt 10 tầng lồng → trả về nửa chừng, KHÔNG báo lỗi.
2. **Không tìm thấy group → trả lại CHÍNH GID truyền vào, KHÔNG trả `""`.** ⚠ Chuỗi khác rỗng
   ở đây KHÔNG chứng minh group tồn tại — mọi caller phải tự `FindGroupData` lại để xác nhận.
3. **Vòng lặp cha-con quẩn (A→B→A) không bị phát hiện** — chỉ bị cap 10 chặn rồi trả kết quả sai.

Cả 3 không chặn bất kỳ caller hiện có (T1 Save As/Save đè, `ResolveSelectedComboRoot` C9). KHÔNG
sửa hàm (KP3). Xem `DEVIATIONS.md` mục "[DOC-DEBT] GetGroupRoot chưa từng có doc — 03/08/2026".

### GetComboRootOfActor(Actor : BP_FurnitureActor) → (RootGroupID, ComboID : String, bFound : Bool)

**Mới 03/08/2026 (Save As/Save đè T1).** Test PASS: actor trong combo đã save → `bFound=true` +
đúng `ComboID`; actor rời → `bFound=false`.

**Local:** `GCR_GID`, `GCR_RootGID`, `GCR_SCID` (String) · `GCR_Data` (S_GroupData) ·
`GCR_bDataFound` (Bool)

```
Entry
▶→ Branch(IsValid(Actor))
     False ▶→ Return ["", "", false]                     → ref chết
     True  ▶→ GET Actor.GroupID ─→ SET GCR_GID
▶→ Branch(GCR_GID == "")
     True  ▶→ Return ["", "", false]                     → đồ rời
     False ▶→ GetGroupRoot(GCR_GID) ─→ SET GCR_RootGID
▶→ FindGroupData(GCR_RootGID)
     ─→ GroupData ▶→ SET GCR_Data
     ─→ bFound    ▶→ SET GCR_bDataFound
▶→ Branch(GCR_bDataFound == false)
     True  ▶→ Return ["", "", false]                     → GetGroupRoot trả GID cũ, group không tồn tại
     False ▶→ Break GCR_Data ─→ SourceComboID ▶→ SET GCR_SCID
▶→ Branch(GCR_SCID == "")
     True  ▶→ Return ["", "", false]                     → group thường, chưa Save Combo
     False ▶→ Return [GCR_RootGID, GCR_SCID, true]
```

⚠️ **KHÔNG bỏ bước `FindGroupData` sau `GetGroupRoot`** — `GetGroupRoot` khi không tìm thấy group
trả lại CHÍNH GID truyền vào (không phải `""`); chuỗi khác rỗng không chứng minh group tồn tại.

**Ceiling:** hàm này KHÔNG đấu vào `ResolveSelectedComboRoot()` (C9) — 2 nơi cùng biết cách leo
combo root. Xem `DEVIATIONS.md` mục "[CEILING] Hai nơi cùng biết cách leo combo root — 03/08/2026".

### ResolveActiveComboForSave() → (ComboID, RootGroupID : String, ItemCount : Int, bCanOverwrite : Bool, ReasonText : String)

**Mới 03/08/2026 (Save As/Save đè T1).** Quét toàn bộ `SelectedActors`, đếm số combo root khác
nhau — KHÔNG dùng `PrimarySelectedActor` hay `SelectedActors[0]` (2 biến này lấy MỘT actor rồi leo
lên → kết quả phụ thuộc thứ tự Ctrl-click, xem `DEVIATIONS.md` mục DOC-DRIFT đóng 03/08/2026).

**Local:** `ResolveSave_ActorsCopy` (Array BP_FurnitureActor) · `ResolveSave_Roots`,
`ResolveSave_ComboIDs` (Array String) · `ResolveSave_Count` (Int) · `ResolveSave_Scope`,
`ResolveSave_Root`, `ResolveSave_CID` (String) · `ResolveSave_bFound` (Bool)

```
Entry
▶→ CLEAR ResolveSave_Roots · CLEAR ResolveSave_ComboIDs · SET ResolveSave_Count = 0
▶→ GetCurrentEditScope() ─→ SET ResolveSave_Scope
▶→ Branch(ResolveSave_Scope != "")
     True  ▶→ Return ["", "", 0, false,
                      "Đang sửa bên trong nhóm — thoát nhóm rồi mới ghi đè được"]
     False ▶→ SET ResolveSave_ActorsCopy = SelectedActors    → copy trước khi lặp (pass-by-ref)

▶→ ForEach ResolveSave_ActorsCopy (Actor)
     Loop Body:
       Branch(IsValid(Actor))
         False ▶→ (để trống — bỏ qua ref chết)
         True  ▶→ SET ResolveSave_Count = ResolveSave_Count + 1
                ▶→ GetComboRootOfActor(Actor)
                     ─→ RootGroupID ▶→ SET ResolveSave_Root
                     ─→ ComboID     ▶→ SET ResolveSave_CID
                     ─→ bFound      ▶→ SET ResolveSave_bFound
                ▶→ Branch(ResolveSave_bFound)
                     False ▶→ (để trống)
                     True  ▶→ Branch(NOT Contains(ResolveSave_Roots, ResolveSave_Root))
                                True  ▶→ ADD ResolveSave_Root → ResolveSave_Roots
                                       ▶→ ADD ResolveSave_CID  → ResolveSave_ComboIDs
                                False ▶→ (để trống — root đã có, không đếm 2 lần)

     Completed:
▶→ Branch(ResolveSave_Count == 0)
     True  ▶→ Return ["", "", 0, false, "Chưa chọn gì"]
     False ▶→ Branch(Array Length(ResolveSave_Roots) == 1)
                True  ▶→ Return [ResolveSave_ComboIDs[0], ResolveSave_Roots[0],
                                 ResolveSave_Count, true, ""]
                False ▶→ Branch(Array Length(ResolveSave_Roots) == 0)
                           True  ▶→ Return ["", "", ResolveSave_Count, false,
                                    "Chưa chọn combo nào có sẵn — chỉ lưu được thành combo mới"]
                           False ▶→ Return ["", "", ResolveSave_Count, false,
                                    "Đang chọn nhiều combo — chỉ lưu được thành combo mới"]
```

**Vì sao KHÔNG trả tên combo:** tên hiển thị nằm trong file `.json`, không nằm trong `S_GroupData`.
T3/T4 tra tên qua `BP_ComboManager` (nguồn thật).

Test PASS 6/6 (03/08/2026, Print tạm trong `CB_SaveCombo_Handler`, đã xóa sau test):

| # | Case | Kết quả log |
|---|---|---|
| 1 | 2 mesh rời | `can=false n=2 id= why=Chưa chọn combo nào có sẵn…` |
| 2 | 1 combo cả cụm (S4) | `can=true n=21 id=combo_05EB1115… Root=8307B660…` |
| 3 | Combo A + 3 mesh rời (S8, hội tụ) | `can=true n=13 id=combo_3850A77C…` |
| 4 | Combo A + Combo B (S8, 2 root) | `can=false n=31 why=Đang chọn nhiều combo…` |
| 5 | Trong edit mode, chọn 1 món | `can=false n=0 why=Đang sửa bên trong nhóm…` |
| 6 | Sau Ctrl+Z vài lần, chọn lại cụm (S9) | `can=true n=21 id=combo_05EB1115…` — khớp case 2, không Accessed None |

Chi tiết plan gốc: `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 6.3, 6.4, 6.5.

### ShouldRouteReplaceToCombo(Actor : BP_FurnitureActor) → (bRouteToCombo : Bool, ComboID, RootGroupID : String)

**Mới 03/08/2026 (Save As/Save đè T2, đóng `Bug-ReplaceInCombo-TabJump`).** ✓K2 03/08/2026 —
input `Actor` là param sự kiện, output `bRouteToCombo` nối thẳng Condition, không lệch pin.

**Local:** `RRT_Scope`, `RRT_Root`, `RRT_CID` (String) · `RRT_bFound` (Bool)

Vì sao là Function trong `BP_FurnitureInputManager`, không phải Branch trực tiếp trong widget:
`OnMeshSelected` là Event (bind từ Dispatcher) → KHÔNG có Local Variable (L9). Viết thẳng trong
widget thì phải đẻ class var trong `WBP_FurnitureInventory` chỉ để giữ giá trị tạm — trái R2/R4
(widget ôm thêm state). Trả luôn `ComboID` + `RootGroupID` để widget không phải gọi thêm hàm thứ
hai lấy dữ liệu cho `StartReplaceComboMode`.

```
Q8: Container=Function (Local Var OK, no latent) | IsValid(Actor) đầu hàm ✓ |
L2: 4 nhánh đều chạm Return Node (L12) ✓ | No latent ✓ |
6A: đường ngược = thoát edit mode → route quay lại COMBO, có case test riêng (case 4, xem dưới) ✓
```

```
Entry (Actor)
▶→ Branch(IsValid(Actor))
     False ▶→ Return [false, "", ""]                    ← ref chết (S9)
     True  ▶→ GetCurrentEditScope() ●→ SET RRT_Scope
▶→ Branch(RRT_Scope != "")
     True  ▶→ Return [false, "", ""]        ← ĐANG EDIT: đơn vị thao tác là MESH, không phải combo
     False ▶→ GetComboRootOfActor(Actor)
                  ●→ RootGroupID ▶→ SET RRT_Root
                  ●→ ComboID     ▶→ SET RRT_CID
                  ●→ bFound      ▶→ SET RRT_bFound
▶→ Branch(RRT_bFound)
     True  ▶→ Return [true, RRT_CID, RRT_Root]          ← S4: route COMBO (hành vi đúng, giữ)
     False ▶→ Return [false, "", ""]                    ← S1/S3: route MESH
```

⚠️ **KHÔNG sửa `ResolveSelectedComboRoot()`.** Vẫn được gọi ở call site khác (C9,
`ExecuteComboReplace`). Ceiling "2 nơi cùng biết cách leo combo root" giữ nguyên, trigger vẫn là
C10 — xem `DEVIATIONS.md` 03/08.

**Nơi gọi (03/08/2026):** `WBP_FurnitureInventory.OnMeshSelected` (nhánh Replace) — xem
`Widgets/WBP_FurnitureInventory.md`. Thay thế lời gọi `ResolveSelectedComboRoot()` trước đây tại
call site này.

⚠️ **Call site thứ 2 (`CB_Replace`) — KHÔNG XÁC NHẬN ĐƯỢC, xem báo cáo mâu thuẫn cuối phiên merge
04/08/2026.** Section `CB_Replace` hiện tại trong file này (phía dưới) gọi thẳng
`StartReplaceMode(Actors = SelectedActors)`, KHÔNG hề gọi `ResolveSelectedComboRoot()` hay bất kỳ
hàm route combo nào — không có node nào để "thay thế". KHÔNG tự sửa `CB_Replace` cho khớp tuyên
bố "2 call site" khi không có ground truth (node flow/K2Node export) cho thay đổi đó.

Test PASS 6/6 (03/08/2026) — xem `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 6b.5.

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

### Right-click handler (T4) — [✓K2 24/08/2026]

**Input Actions:** `IA_RMBPress` / `IA_RMBRelease` (map Right Mouse Button, trong
`LM_FurnitureInput`). ⚠️ Không tìm thấy 2 action này trong bảng Input Action chính thức nào của
canonical docs hiện có — khả năng leftover chưa từng ghi chép. `IA_RMBRelease` bị chính
`IA_RMBPress` override trong Enhanced Input debug (2 action cùng `LM_FurnitureInput` tranh cùng
phím Right Mouse Button) — không ảnh hưởng chức năng (logic vẫn đúng qua Branch bên dưới), nhưng
đáng dọn nếu có dịp rà lại input list. Chưa thêm vào bảng "Node/Action chính xác" — cần cuhoang
xác nhận trước.

Biến liên quan: `RMBPressTime`/`RMBPressCamRot` (xem mục Variables → Context Menu).

```
Custom Event OnRMBPressed   [✓K2 24/08/2026]
▶→ SET RMBPressTime = GetGameTimeInSeconds()
▶→ SET RMBPressCamRot = GetPlayerController(0).PlayerCameraManager.GetCameraRotation()
   ← CHỈ ĐỌC, KHÔNG set lại camera. Ghi nhận rotation lúc bấm để so sánh lúc thả.
```

```
Custom Event OnRMBReleased   [✓K2 24/08/2026]
▶→ Branch(
     (GetGameTimeInSeconds() - RMBPressTime < 0.3)                    ← thả nhanh (<0.3s)
     AND (Abs(CurrentCamRot.Pitch - RMBPressCamRot.Pitch) < 0.5)      ← camera KHÔNG xoay
     AND (Abs(CurrentCamRot.Yaw   - RMBPressCamRot.Yaw)   < 0.5)
   )
     True  ▶→ Call OnRightClick()                    ← click thật → mở context menu
     False ▶→ Branch(IsValid(ContextMenuRef))
                True  ▶→ ContextMenuRef.Hide ▶→ SET ContextMenuRef = None
                False ▶→ (trống — L2 hợp lệ, cuối chain)
```

**Ý nghĩa cơ chế:** phân biệt "right-click thật" (bấm-thả nhanh, camera đứng yên trong ±0.5°)
với "giữ chuột phải kéo pan/xoay camera rồi thả ra" (camera đã xoay → không phải click, chỉ đóng
menu cũ nếu có, không mở menu mới). `GetCameraRotation()` chỉ dùng để SO SÁNH — không set ngược
lại camera.

**`OnRightClick()` (callee, boundary hợp lệ theo L-DOC — internals CHƯA verify trong đợt K2
24/08/2026 này):**
```
↳ Callee: BP_FurnitureInputManager.OnRightClick
   Canonical flow: [⚠ suy luận — mô tả cũ trước đợt 24/08, chưa từng verify bằng K2Node]
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

### CB_SaveCombo_Handler (C3b 24/06/2026 · C4 CalculateComboAnchor · ✓K2 04/08/2026)
```
CB_SaveCombo_Handler  (Custom Event)   ✓K2 04/08/2026
▶→ Branch( Array_Length(SelectedActors) >= 2 )
     False ▶→ (TRỐNG — chặn im lặng, không toast/log)
     True  ▶→ CalculateComboAnchor(InActors=SelectedActors) ─→ ReturnVec
           ▶→ GetAllWidgetsOfClass(WBP_FurnitureInventory) ─→ FoundWidgets
           ▶→ Branch( IsValid( FoundWidgets[0] ) )
                False ▶→ Print "CB_SaveCombo: Inventory ref not found" [DevelopmentOnly]
                True  ▶→ Inventory.OpenSaveComboDialog(SelectedActors, Center=ReturnVec)
                      ▶→ Branch( IsValid(ContextMenuRef) )
                           True  ▶→ ContextMenuRef.Hide ▶→ SET ContextMenuRef = None
                           False ▶→ (trống — cuối chain, L2 hợp lệ)
```

3 điều doc bản 24/06/2026 chưa từng ghi:
1. Guard là `Array_Length >= 2` (GreaterEqual_IntInt, B=2) — chặn S0/S1 TRƯỚC khi mở dialog.
2. Nhánh False **trống hoàn toàn** — chặn im lặng, user không nhận phản hồi nào (xem
   `Bugs/Open_Bugs.md` mục `Bug-SaveComboSilentBlock`).
3. `SelectedActors` được đọc **live 3 lần** trong cùng event (Length / CalculateComboAnchor /
   truyền vào OpenSaveComboDialog) — cùng frame, không có kẽ hở async.

⚠️ **Không có biến `InventoryRef` hay node `Cast` trung gian trên đường này** (khác mô tả doc
24/06/2026 cũ "Get(0) → IsValid → Cast → InventoryRef"). `GetAllWidgetsOfClass` trả mảng đã đúng
kiểu `WBP_FurnitureInventory_C`; phần tử `FoundWidgets[0]` cắm thẳng vào `IsValid` và qua Knot vào
self pin của `OpenSaveComboDialog`. Ai tìm biến `InventoryRef` ở hàm này sẽ không thấy — đừng tự
tạo biến trùng vai (cùng loại drift với ca `ReplaceTarget` 2 bản trùng tên, xem mục
`ResolveSelectedComboRoot`/Aliasing trong `Widgets/WBP_FurnitureInventory.md`).

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

## StartReplaceMode(Actors : Array<BP_FurnitureActor>) — v2.4, verified qua K2Node export (24/07/2026)

⚠️ **Thay toàn bộ nội dung v1.10 cũ** (mô tả dùng `bIsReplaceMode`, một guard `LENGTH==0`, và
navigate folder theo `Actors[0]` khi `LENGTH==1`) — đã lỗi thời từ khi migrate sang
`E_ReplaceTarget` (C9.0c, migrate ngoài phiên Claude Code). Nội dung dưới đây đối chiếu trực
tiếp K2Node text export (Ctrl+A → Ctrl+C → paste), KHÔNG suy đoán qua ảnh chụp.

Gọi từ `BTN_Replace` (WBP_MeshControls) khi `ReplaceTarget == E_ReplaceTarget::None`.

```
FunctionEntry.then
▶→ SET MeshesToReplace = Actors
▶→ SET ReplaceTarget = E_ReplaceTarget::Mesh          ← FIX 24/07 (trước đó dangling, không SET)
▶→ Branch(IsValid PrimarySelectedActor)
     True ▶→ Branch(RowName != "")                     ← RowName đọc từ PrimarySelectedActor
          True ▶→ GetDataTableRow(DT_FurnitureCatalog, RowName)
               Row Found ▶→ SET LocalFolderPath ●← BreakStruct.MeshFolderPath
                    ▶→ [merge điểm A]
               RowNotFound ▶→ [dead-end — xem Quan sát 1]
          False ▶→ SET LocalDAPath ●← SelectedFurnitureActor.DAPath   ← đọc từ SelectedFurnitureActor,
                                                                          KHÔNG phải PrimarySelectedActor
               ▶→ MakeSoftObjectPath → Conv to SoftObjRef → LoadAsset_Blocking
               ▶→ Cast DA_FurnitureItem
                    then ▶→ SET LocalFolderPath ●← DA.MeshFolderPath
                         ▶→ [merge điểm A]
                    CastFailed ▶→ [dead-end]
     False ▶→ [dead-end — không navigate, không mở inventory nếu Primary invalid]

[điểm A — merge cả 2 nhánh trên]
▶→ Get Game Instance → Cast Foff_GameInstance
     then ▶→ SET LocalInvRef ●← GameInstance.FurnitureInventoryRef
          ▶→ Branch(IsValid LocalInvRef)
               True ▶→ Branch(IsInViewport LocalInvRef)
                    True  ▶→ EnterReplaceMode(LocalInvRef) ▶→ FilterByFolderPathWithUI(LocalFolderPath)
                    False ▶→ [khối B — CreateWidget lặp lại]
               False ▶→ [khối B — CreateWidget lặp lại, bản sao thứ 2]
     CastFailed ▶→ [dead-end]

[khối B — pattern lặp 3 lần trong graph, cùng nội dung]
Create WBP_FurnitureInventory ▶→ SET LocalInvRef
▶→ AddToViewport
▶→ Get Player Controller → SET bShowMouseCursor=True
▶→ Cast Game Instance → SET GameInstance.FurnitureInventoryRef = LocalInvRef
▶→ Cast LocalInvRef → WBP_FurnitureInventory
▶→ EnterReplaceMode ▶→ FilterByFolderPathWithUI(LocalFolderPath)
```

**Behavior chốt (30/07/2026 — xác nhận qua delta "C9 Replace: Folder Highlight + Chip Fix &
C9.b–C9.f"):** `DT_FurnitureCatalog.MeshFolderPath` lưu **FULL path** (vd
`/Game/DatabaseProjectMaster/Model/Object_Model/Furniture/Table/Side_Table`). `LocalFolderPath`
giữ NGUYÊN full path này khi truyền sang `FilterByFolderPathWithUI` — **KHÔNG strip ở đây**. Việc
chuyển full→relative (cắt tại `"Object_Model/"`) làm BÊN TRONG `FilterByFolderPathWithUI` (xem
`Widgets/WBP_FurnitureInventory.md` mục `Split.RightS`) — strip sớm ở `StartReplaceMode` sẽ làm
`Split` bên trong hỏng.

**Quan sát 1 (chưa sửa, ghi nhận — cuhoang chưa quyết định có cần fix không):**
`GetDataTableRow.RowNotFound` là dead-end — nếu `RowName` tồn tại trên actor nhưng không tìm
thấy row trong `DT_FurnitureCatalog` (dữ liệu stale), toàn bộ phần còn lại của function
(navigate folder + mở inventory + `EnterReplaceMode`) **không chạy**. `MeshesToReplace`/
`ReplaceTarget` vẫn được SET đúng, nhưng UI không phản hồi gì. Ngoài scope C9 hiện tại.

**Quan sát 2 (không xác nhận được, khác doc cũ — chưa quyết định thêm lại hay bỏ qua):** Guard
`Branch LENGTH(Actors)==0 → Return` mà doc trước đây mô tả **không xuất hiện** trong export hiện
tại. Không rõ đã từng có rồi mất, hay doc mô tả sai từ đầu.

**Khớp với deviation đã ghi nhận (⚠️ chưa xác minh được nguồn):** delta 24/07 nói khối B lặp 3
lần khớp với ghi chú "StartReplaceComboMode mirror 3 nhánh trùng lặp của StartReplaceMode |
ceiling: 2 replace target" tại `DEVIATIONS.md` §11 — nhưng grep file canonical hiện tại KHÔNG
tìm thấy đoạn này. Có thể nằm trong 1 doc khác chưa phân phối vào repo, hoặc tham chiếu sai. Dù
vậy khối B lặp 3 lần trong export là sự thật quan sát trực tiếp (không phụ thuộc việc xác minh
được deviation cũ hay không) — không coi là bug mới, chỉ chưa xác nhận được lịch sử ghi chép.

**Lưu ý 03/08:** nhánh False (`RowName` rỗng → `LoadAsset DAPath`) từng dead-end vì actor sau
Undo có `RowName=None` — gốc rễ ở `BP_UndoManager` (`Bug-RowNameLostOnUndo`), không phải lỗi tại
đây. Xem `BP_UndoManager.md` mục `S_FurniturePlacement`.

---

## IsReplaceModeActive() → Boolean — Pure Function (MỚI, C9.0c, 24/07/2026)

```
Return (ReplaceTarget != E_ReplaceTarget::None)
```
Cùng tên + cùng logic tồn tại SONG SONG trên cả `BP_FurnitureInputManager` (đây) và
`WBP_FurnitureInventory` (2 bản riêng, không phải 1 hàm dùng chung — xem
`Widgets/WBP_FurnitureInventory.md`). Quy ước dùng: nơi chỉ cần biết "có đang replace hay không"
(bất kể Mesh/Combo) → gọi `IsReplaceModeActive()`. Nơi cần biết đúng loại "đang replace Mesh" (để
hiện/ẩn nút riêng cho furniture card) → so sánh trực tiếp `ReplaceTarget == E_ReplaceTarget::Mesh`
(xem `Widgets/WBP_FurnitureCard.md`).

---

## CB_Replace — Custom Event (EventGraph, verified qua K2Node export 03/08/2026 — Save As/Save đè T2)

⚠️ [SUPERSEDED 03/08/2026] Bản mô tả ✓K2 24/07/2026 dưới đây KHÔNG có nhánh route combo
(`ShouldRouteReplaceToCombo`) — do đọc lúc đó CHƯA re-export sau T2, không phải vì code thật
thiếu nhánh này. Giữ lại làm lịch sử, KHÔNG dùng làm nguồn hiện hành — xem bản ✓K2 03/08 ngay
dưới đây.

```
[BẢN CŨ ✓K2 24/07/2026 — SUPERSEDED, giữ lịch sử]
CB_Replace.then
▶→ Branch(IsValid ContextMenuRef)
     True ▶→ Remove from Parent(ContextMenuRef)
          ▶→ SET ContextMenuRef = None
          ▶→ Branch(IsReplaceModeActive)
               True (đang active — tắt) ▶→
                    SET ReplaceTarget = E_ReplaceTarget::None
                    ▶→ Clear Array(MeshesToReplace)
                    ▶→ Get Game Instance → Cast Foff_GameInstance
                         ▶→ Branch(IsValid FurnitureInventoryRef)
                              True ▶→ Branch(IsInViewport)
                                   True ▶→ ExitReplaceMode
                                   False ▶→ [dead-end]
                              False ▶→ [dead-end]
               False (chưa active — bật) ▶→
                    Branch(IsValid PrimarySelectedActor)
                         True ▶→ Branch(SelectedActors.Length > 0)
                              True ▶→ StartReplaceMode(Actors = SelectedActors)
                              False ▶→ [dead-end]
                         False ▶→ [dead-end]
     False ▶→ [dead-end]
```
**Bug đã fix trong phiên 24/07/2026:** trước đây có 1 `Branch` dư ngay sau
`SET ContextMenuRef=None`, Condition không nối gì (literal mặc định = `true`) → nhánh dẫn tới
`StartReplaceMode` không bao giờ chạy được. Đã xóa Branch dư, nối thẳng vào
`Branch(IsReplaceModeActive)`. Verify: mọi pin `then`/`execute` khớp `LinkedTo` 2 chiều, không
còn node dư. Bản mirror ở `Sprints/Sprint2/ContextMenu_Prep.md` §4.2 (doc prep gốc, giữ đồng bộ)
— **doc prep đó cũng chưa phản ánh nhánh route combo 03/08, đọc cẩn thận nếu tham chiếu.**

### ✓K2 03/08/2026 — bản hiện hành

```
CB_Replace.then
▶→ Branch(IsValid ContextMenuRef)
     True ▶→ Remove from Parent(ContextMenuRef)
          ▶→ SET ContextMenuRef = None
          ▶→ Branch(IsReplaceModeActive)
               True (đang active — tắt) ▶→
                    SET ReplaceTarget = E_ReplaceTarget::None
                    ▶→ Clear Array(MeshesToReplace)
                    ▶→ SET ComboRootGroupIDToReplace = ""        ← MỚI 03/08 (T2) — thiếu ở bản cũ
                    ▶→ Get Game Instance → Cast Foff_GameInstance
                         ▶→ Branch(IsValid FurnitureInventoryRef)
                              True ▶→ Branch(IsInViewport)
                                   True ▶→ ExitReplaceMode
                                   False ▶→ [dead-end]
                              False ▶→ [dead-end]
               False (chưa active — bật) ▶→
                    Branch(IsValid PrimarySelectedActor)
                         True ▶→ Branch(SelectedActors.Length > 0)
                              True ▶→ ShouldRouteReplaceToCombo(Actor = PrimarySelectedActor)   ← MỚI 03/08 (T2)
                                     ●→ bRouteToCombo, ComboID, RootGroupID
                                     ▶→ Branch(bRouteToCombo)
                                          True  ▶→ StartReplaceComboMode(RootGroupID, ComboID)   ← MỚI 03/08 (T2)
                                          False ▶→ StartReplaceMode(Actors = SelectedActors)      ← node CŨ, giữ nguyên
                              False ▶→ [dead-end]
                         False ▶→ [dead-end]
     False ▶→ [dead-end]
```

**Xác nhận 03/08/2026:** đây CHÍNH XÁC là call site thứ 2 đã fix trong T2 (cùng với
`OnMeshSelected`, xem `Widgets/WBP_FurnitureInventory.md` v3.20). Test 2 trial chuột phải PASS
(đang edit trong combo → chuột phải Replace → giữ tab Furniture; thoát edit → chuột phải Replace
cả cụm → giữ tab Combo). KHÔNG có `ResolveSelectedComboRoot()` trong đoạn này — claim trước đó về
"không tìm thấy node để thay" là do đọc bản doc CHƯA re-export (✓K2 24/07), không phải code thật
thiếu nhánh. Đóng caveat ghi ở `Bugs/Open_Bugs.md` mục `Bug-ReplaceInCombo-TabJump` và
`Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 6b.5.

Bug fix Branch dư (24/07, xem bản cũ ở trên) vẫn còn nguyên trong bản 03/08 — không bị cuốn lại
khi thêm nhánh route combo.

---

## ComboRootGroupIDToReplace : String (default "") — biến MỚI (C9.d, 30/07/2026)

---

## DestroyComboCluster(RootGroupID : String) — Function (MỚI, C9.b, 30/07/2026)

**Local:** DestroyCombo_Actors (Array\<BP_FurnitureActor\>)
```
Entry
▶→ Branch(RootGroupID == "") True ▶→ Return
▶→ GetAllDescendantActors(RootGroupID) ●→ SET DestroyCombo_Actors   ← copy local (array pass-by-ref)
▶→ ForEach DestroyCombo_Actors (a):
     Loop Body ▶→ Branch(IsValid(a)) True ▶→ Destroy Actor(Target = a)
     Completed ▶→ DeselectAll()            ← 🔴 bắt buộc, xem ghi chú
               ▶→ PruneEmptyGroups()
▶→ Return
```
🔴 `DeselectAll` KHÔNG được bỏ. Cụm bị thay đang được SELECT (đó là cách `ResolveSelectedComboRoot`
tìm ra nó) — Destroy xong mà không deselect thì `SelectedActors`/`PrimarySelectedActor` vẫn giữ
con trỏ tới actor vừa chết, khiến `SpawnComboByID` Sub-step D (gọi ngay sau từ `ReplaceCombo`)
`DeselectAll`+`SelectActors` trên đống rác đó. Thứ tự `DeselectAll` TRƯỚC `PruneEmptyGroups`:
deselect còn đụng gizmo/pivot, dọn xong mới prune group. `Destroy Actor` PHẢI nối Target = Array
Element (để trống = self = destroy chính InputManager). CỐ Ý KHÔNG `CaptureSnapshot` ở đây —
`ReplaceCombo` (`BP_ComboManager`) kiểm soát để đảm bảo đúng 1 snapshot cho cả thao tác replace.
KHÔNG tái dùng `DeleteSelected` (chạy trên `SelectedActors` + tự capture "Delete" → dư 1 snapshot
rác). Test orphan group: replace 3 lần liên tiếp → `Groups.Length` ổn định, không tăng dần.

---

## StartReplaceComboMode(RootGroupID : String, ComboID : String) — Function (MỚI, C9.d, 30/07/2026) — SỬA (Replace UX Fix P1.2+P3.2, 01/08/2026)

Mirror cấu trúc 3 nhánh của `StartReplaceMode` (IsValid InvRef × IsInViewport) — cố ý KHÔNG gộp
helper dùng chung (KP3). Node flow đầy đủ sau 2 fix 01/08 (fix #3a + fix #3b):
```
Cast Foff_GameInstance → SET SRC Inv Ref (Furniture Inventory Ref)
▶→ Branch(IsValid(SRC Inv Ref))
     True  ▶→ Branch(IsInViewport)
     False ▶→ Create WBP Furniture Inventory Widget → SET SRC Inv Ref ─┐
                Branch(IsInViewport) [trên widget mới]                │
                                                                        ▼
     (merge cả các nhánh IsInViewport — cùng cấu trúc 3 nhánh StartReplaceMode)
▶→ InventoryRef.EnsureExpanded()                          ← MỚI 01/08 (fix #3a)
▶→ SET ComboRootGroupIDToReplace = RootGroupID
▶→ CLEAR MeshesToReplace                    ← mode này xóa payload của mode kia
▶→ SET ReplaceTarget = E_ReplaceTarget::Combo

← đọc FolderPath combo GỐC (F_LoadComboData trên BP_ComboManager) để navigate đúng thư mục;
  load fail → FolderPath = "__ALL__" (vẫn mở inventory, không chết giữa chừng)

[KHỐI CUỐI]
  InvRef.SwitchInventoryMode(Combo)
  → SET InvRef.ReplaceTarget = Combo
  → InvRef.FilterComboByFolder(FolderPath)
  → InvRef.PopulateComboTreeColumn()
  → InvRef.RefreshChipBreadcrumb()            ← MỚI 01/08 (fix #3b) — hàm CÓ SẴN (06/07), không
                                                  phải code mới. ĐẶT TRƯỚC UpdateComboFolderHighlights
                                                  (đảo ngược thứ tự mô tả trong WBP_FurnitureInventory.md
                                                  cho RefreshComboFolderUI — xem DEVIATIONS 01/08)
  → InvRef.UpdateComboFolderHighlights()
  → InvRef.RefreshComboCardReplaceMode()
```
⚠️ `SwitchInventoryMode(Combo)` bên trong đã tự gọi `FilterComboByFolder("__ALL__")` → gọi lại
lần 2 với FolderPath thật = build 2 lần trong 1 frame. Chấp nhận (kết quả cuối đúng, không thấy
nháy UI) — xem `DEVIATIONS.md` mục "C9 Replace — 30/07/2026". `FolderPath == ""` là giá trị HỢP
LỆ ("Chưa phân loại") — chỉ dùng `"__ALL__"` khi load combo gốc THẤT BẠI.

**Fix #3a (01/08):** cửa sổ không tự mở khi combo-replace từ minimize — `EnsureExpanded()` gọi
tại điểm hợp lưu 3 nhánh `Branch(IsInViewport)`, TRƯỚC `SwitchInventoryMode(Combo)`. Mirror đúng
vị trí `EnterReplaceMode` gọi nó bên nhánh mesh (xem `Widgets/WBP_FurnitureInventory.md` mục
`EnterReplaceMode`/`EnsureExpanded`). Test T3.3 PASS PIE.

**Fix #3b (01/08):** chiptag không rebuild + không highlight đúng khi combo-replace — thêm gọi
`RefreshChipBreadcrumb()` (hàm có sẵn từ 06/07, xem `WBP_FurnitureInventory.md` §Bug fix Chip
area) NGAY TRƯỚC `UpdateComboFolderHighlights()`. Không cần viết hàm mới
`CreateComboChipTagsForPath` như dự kiến ban đầu ở `Plans/01-08-2026_ReplaceUX_Fix_Execution_Plan.md`
§2 (Quyết định Opus #1) — xem SUPERSEDED note tại đó. Test T1.1 PASS PIE.

---

## ResolveSelectedComboRoot() → RootGroupID:String, ComboID:String, bFound:Bool — Function (ghi nhận 02/08/2026, K2Node export thật cuhoang cung cấp)

**Local:** ResolveCombo_GID, ResolveCombo_RootGID, ResolveCombo_Data (S_GroupData),
ResolveCombo_bDataFound, ResolveCombo_SCID

Flow (6 Return node, mọi nhánh có đích — KHÔNG dead-end):
```
Entry
▶→ Branch(Array_Length(SelectedActors) == 0)
     True  ▶→ Return ["", "", false]                    ← không chọn gì
     False ▶→ Cast SelectedActors[0] → BP_FurnitureActor
              CastFailed ▶→ Return ["", "", false]        ← null guard (xem ⚠ dưới)
              Success ●→ GroupID ▶→ SET ResolveCombo_GID
▶→ Branch(ResolveCombo_GID == "")
     True  ▶→ Return ["", "", false]                    ← đồ rời, không thuộc group
     False ▶→ GetGroupRoot(ResolveCombo_GID) ●→ SET ResolveCombo_RootGID
▶→ FindGroupData(ResolveCombo_RootGID)
     ●→ bFound     ▶→ SET ResolveCombo_bDataFound
     ●→ GroupData  ▶→ SET ResolveCombo_Data
▶→ Branch(ResolveCombo_bDataFound == false)
     True  ▶→ Return ["", "", false]                    ← group data hỏng/không tìm thấy
     False ▶→ Break ResolveCombo_Data ●→ SourceComboID ▶→ SET ResolveCombo_SCID
▶→ Branch(ResolveCombo_SCID == "")
     True  ▶→ Return ["", "", false]                    ← group thường, KHÔNG phải combo
     False ▶→ Return [ResolveCombo_RootGID, ResolveCombo_SCID, true]
```

⚠️ **GHI CHÚ BẮT BUỘC (chống "dọn warning" làm mất guard):** Node `Cast To BP_FurnitureActor` có
compiler warning *"'Item' is already a 'BP Furniture Actor', you don't need Cast"*. **KHÔNG ĐƯỢC
XÓA.** Nếu `SelectedActors[0]` là `None` (actor đã Destroy, ref chết — case sau
`RestoreSnapshot`), Cast fail → nhánh CastFailed → trả not-found an toàn. Hàm này không có node
`IsValid` nào khác — xóa cast = mất null guard duy nhất.

**Nơi gọi:** `WBP_FurnitureInventory.OnMeshSelected` (nhánh Replace) và `ExecuteComboReplace`
(mục ngay dưới, đoạn re-resolve sau `ReplaceCombo`) — xem thêm các call site khác đã ghi trong
`Widgets/WBP_FurnitureInventory.md`.

⚠️ **[DOC-DRIFT — xem `DEVIATIONS.md`]** `Plans/24-07-2026_C9_Execution_Plan.md` mục V7 ghi hàm
này "dùng `PrimarySelectedActor`" — **as-built thật dùng `SelectedActors[0]`** (không phải
`PrimarySelectedActor`). Hai giá trị khác nhau khi selection là multi. Chưa gây lỗi trong C9
(Replace Combo chỉ chạy với selection 1 cụm) nhưng **PHẢI chốt trước khi lên task card Save
As/Save đè** (selection có thể mix combo + mesh rời). Không tự sửa Blueprint ở đây.

---

## ExecuteComboReplace(NewComboID : String) — Function (MỚI, C9.f, 30/07/2026)

**Local:** ECR_RootGID2, ECR_ComboID2 (String), ECR_bFound2 (Boolean)
```
▶→ Branch(ReplaceTarget != E_ReplaceTarget::Combo) True ▶→ Return
▶→ Branch(ComboRootGroupIDToReplace == "") True ▶→ Return
▶→ Branch(NewComboID == "") True ▶→ Return
▶→ Get All Actors Of Class(BP_ComboManager) → Get(0) → IsValid
     False ▶→ Return
     True  ▶→ ComboManager.ReplaceCombo(ComboRootGroupIDToReplace, NewComboID)   ← Custom Event,
                                                                                    xem `Blueprints/BP_ComboManager.md`

← cập nhật target để replace TIẾP được (đối xứng mesh — Luật 6B)
▶→ ResolveSelectedComboRoot() ●→ ECR_RootGID2, ECR_ComboID2, ECR_bFound2
▶→ Branch(ECR_bFound2)
     True  ▶→ SET ComboRootGroupIDToReplace = ECR_RootGID2
     False ▶→ SET ComboRootGroupIDToReplace = ""
▶→ Return
```
Đoạn re-resolve chạy đúng cho CẢ 2 kết cục: success → cụm mới đang được select (`SpawnComboByID`
tự `SelectActors`) → lấy `RootGID` mới; fail → `RestoreCurrentSnapshot` (xem
`Blueprints/BP_UndoManager.md`) đã khôi phục cụm cũ với đúng `GroupID` cũ → lấy lại chính nó. Gọi
từ `WBP_ComboCard.BTN_ChangeCombo` (xem `Widgets/WBP_ComboCard.md`).

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
| 2.4 | 24/07/2026 | **C9.0c — StartReplaceMode viết lại theo K2Node export thật.** Var `bIsReplaceMode` (Boolean) → `ReplaceTarget` (Enum `E_ReplaceTarget`) — migration xảy ra ngoài phiên Claude Code, doc trước đây không biết. `StartReplaceMode` doc v1.10 cũ (mô tả `bIsReplaceMode`, guard `LENGTH==0`, navigate theo `Actors[0]`) đã lỗi thời — thay bằng flow đối chiếu K2Node export: Primary actor RowName→DT lookup (fallback SelectedFurnitureActor.DAPath), merge điểm A → mở/dùng inventory (khối B lặp 3 lần trong graph). Fix 1 chỗ: `SET ReplaceTarget = E_ReplaceTarget::Mesh` trước đó dangling (không SET). Quan sát 1 (RowNotFound dead-end, chưa fix) + Quan sát 2 (guard LENGTH==0 không còn tồn tại trong export, khác doc cũ) — ghi nhận, KHÔNG tự fix. Chi tiết: `Sprints/Sprint2/ContextMenu_Prep.md` §4.2 (CB_Replace), `Blueprints/Blueprint_Logic_NodeFlow.md` §Event Tick. |
| 2.5 | 24/07/2026 (tiếp) | **C9.0c HOÀN TẤT — 5/5 test regression PASS, 6/6 file compile sạch.** Pure Function mới `IsReplaceModeActive() → Boolean` (= `ReplaceTarget != None`), tồn tại song song trên cả `BP_FurnitureInputManager` và `WBP_FurnitureInventory` (2 bản riêng). `CB_Replace` (Custom Event) đưa vào doc canonical lần đầu — bug fix Branch dư literal=true chặn đường tới `StartReplaceMode`. `Event Tick — Box Select branch` (v1.5 canonical, KHÔNG phải bản tóm tắt ở `Blueprint_Logic_NodeFlow.md`) bổ sung 2 đoạn doc trước đây ghi thiếu (logic Blueprint đã có sẵn, chỉ chưa từng viết vào doc): guard `Branch(bIsPendingBoxSelect OR bIsBoxSelecting)` trước `HideBox`, và chuỗi thoát Replace Mode (`SET ReplaceTarget=None` + `Clear MeshesToReplace` + `ExitReplaceMode`) sau `DeselectAll` trong Branch A. Không sửa logic — verify K2Node export xác nhận đúng. Chi tiết đầy đủ 6 file liên quan: `Widgets/WBP_FurnitureInventory.md`, `Widgets/WBP_MeshControls.md`, `Widgets/WBP_DetailPopup.md`, `Widgets/WBP_FurnitureCard.md`, `Widgets/WBP_ComboCard.md`. |
| 2.6 | 30/07/2026 | **C9.b/C9.d/C9.f DONE (delta "C9 Replace: Folder Highlight + Chip Fix & C9.b–C9.f").** 3 function mới: `DestroyComboCluster(RootGroupID)` (hủy cụm combo cũ, 🔴 `DeselectAll` bắt buộc trước `PruneEmptyGroups`); `StartReplaceComboMode(RootGroupID, ComboID)` (mirror `StartReplaceMode`, khối cuối as-built THÊM `PopulateComboTreeColumn`+`UpdateComboFolderHighlights` so với plan gốc); `ExecuteComboReplace(NewComboID)` (gọi `BP_ComboManager.ReplaceCombo`, re-resolve `ComboRootGroupIDToReplace` sau replace — Luật 6B). Biến mới `ComboRootGroupIDToReplace`. `StartReplaceMode` bổ sung ghi chú behavior: `MeshFolderPath` là full path, không strip (strip xảy ra trong `FilterByFolderPathWithUI`). Chi tiết đầy đủ: `Blueprints/BP_ComboManager.md` (`ReplaceCombo`, `SpawnComboByID` sửa), `Blueprints/BP_UndoManager.md` (`RestoreCurrentSnapshot`), `Widgets/WBP_FurnitureInventory.md` (`OnMeshSelected` guard Bug A2, `EnterReplaceMode`, `RefreshComboCardReplaceMode`, fix `FilterByFolderPathWithUI`), `Widgets/WBP_ComboCard.md` (`BTN_ChangeCombo` wired). |
| 2.7 | 01/08/2026 | **StartReplaceComboMode — 2 fix sau Phase 0 verify (Replace UX Fix P1.2+P3.2).** (1) Fix #3a: thêm `InventoryRef.EnsureExpanded()` tại điểm hợp lưu `Branch(IsInViewport)`, TRƯỚC `SwitchInventoryMode(Combo)` — mirror vị trí gọi bên nhánh mesh (`EnterReplaceMode`). (2) Fix #3b: khối cuối đổi thứ tự — thêm gọi `RefreshChipBreadcrumb()` (hàm có sẵn từ 06/07, KHÔNG viết mới) NGAY TRƯỚC `UpdateComboFolderHighlights()` (đảo ngược thứ tự cũ — xem `DEVIATIONS.md` mục "Replace UX Fix — 01/08/2026"). Huỷ quyết định Opus #1 (viết hàm `CreateComboChipTagsForPath` mới) — không cần, `RefreshChipBreadcrumb` có sẵn làm đúng việc. Test PASS PIE: T1.1 (chiptag đúng combo, highlight đúng), T3.3 (minimize → tự mở lại). Chi tiết: `Plans/01-08-2026_ReplaceUX_Fix_Execution_Plan.md`, `Plans/01-08-2026_Phase0_Verify_Report_ReplaceUXFix.md`. |
| 2.9 | 02/08/2026 (tiếp) | **MERGE_LOG Q3 đóng — `FindGroupData` đính chính chữ ký.** Header hàm trước ghi `(S_GroupData, Index, bFound)` — SAI, tự mâu thuẫn với ghi chú "đã trả giá" ngay dưới `UngroupActors` trong cùng file (*"FindGroupData không có output Index"*). Sửa lại đúng `(S_GroupData, bFound)`. Bằng chứng: K2Node export 24/07/2026 (`Plans/24-07-2026_C9_Execution_Plan.md` §V6, dòng 40 + 689) xác nhận không có Index. Phát hiện qua `CrossCheck_PreGate2_02aug2026.md` MỤC 3. Không đổi node flow thật nào — chỉ sửa mô tả chữ ký cho khớp as-built. |
| 2.8 | 02/08/2026 | **Replace UX Fix P0→P5 HOÀN TẤT.** File này không đổi node flow (route mới P2 gọi các hàm có sẵn `ResolveSelectedComboRoot`/`StartReplaceMode`/`StartReplaceComboMode` không đổi — logic thay đổi nằm ở phía gọi, `WBP_FurnitureInventory.OnMeshSelected`, xem file đó v3.19). Chỉ 1 thay đổi thật ở đây: biến `MeshToReplace` (single, dead code) XÓA HOÀN TOÀN (P4.4) — Find References xác nhận chỉ còn 1 chỗ SET rác (`BTN_Close`), xóa cả 2 (biến + node) → compile sạch 0 error, không cross-class reference nào khác. Đính chính dòng Variables (mục Group) ghi sai "đã xóa từ v1.6, 10/06/2026" — biến thật ra vẫn tồn tại tới hôm nay. KHÔNG nhầm với `MeshesToReplace` (array, dùng thật, giữ nguyên). Chi tiết đầy đủ: `DEVIATIONS.md` mục "Replace UX Fix P0→P5 — 02/08/2026", `Widgets/WBP_FurnitureInventory.md` v3.19. |
| 3.0 | 03/08/2026 20:45 | **Save As/Save đè T1.** Thêm mục `GetGroupRoot()` (doc lần đầu, as-built K2Node 03/08) + 2 hàm mới `GetComboRootOfActor()` + `ResolveActiveComboForSave()`, test PASS 6/6. Chi tiết: `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 6.3/6.4/6.5. *(Ghi bổ sung 04/08/2026 — bảng lịch sử trước đó thiếu dòng này dù header đã bump lên 3.0.)* |
| 3.1 | 04/08/2026 10:20 | **Save As/Save đè T3 (as-built mục A) — đóng `[CONFLICT] CB_SaveCombo_Handler`.** Re-export `CB_SaveCombo_Handler` theo K2Node 04/08/2026, thay bản mô tả cũ (24/06/2026). Kết luận cuhoang (đối chiếu export thật): KHÔNG phải xung đột — bản cũ chỉ THIẾU 2 điều: (1) bước `ContextMenuRef.Hide` + `SET ContextMenuRef=None` sau khi mở dialog, (2) đường thật KHÔNG có biến `InventoryRef`/node `Cast` trung gian — `GetAllWidgetsOfClass` trả đúng kiểu sẵn, cắm thẳng qua Knot vào self pin của `OpenSaveComboDialog`. Guard "LENGTH<2→dead-end" (cũ) và "Branch(>=2), False trống" (mới) là CÙNG 1 Branch, chỉ phát biểu ngược chiều. Giữ nguyên dòng ghi chú kiến trúc cuối section (delegate sang inventory) — export không chứa dòng này, không được mất. Xem `DEVIATIONS.md` mục "[DOC-DEBT đã đóng] CB_SaveCombo_Handler — doc cũ thiếu 2 bước — 04/08/2026". |
| 3.2 | 04/08/2026 11:05 | **`StartReplaceMode` — thêm 1 dòng chú, KHÔNG sửa node flow.** Nhánh False (`RowName` rỗng → `LoadAsset DAPath`) từng dead-end vì actor sau Undo có `RowName=None` — gốc rễ ở `BP_UndoManager` (`Bug-RowNameLostOnUndo`, fix 03/08, xem `BP_UndoManager.md` v1.15 — `S_FurniturePlacement` thiếu field `RowName` từ khi migrate RowName-based Sprint D.T6 17/06), không phải lỗi tại `StartReplaceMode`. |
| 3.3 | 04/08/2026 12:00 | **Save As/Save đè T2 DONE.** Thêm `ShouldRouteReplaceToCombo(Actor)` (✓K2 03/08/2026) — guard `EditScope` trước khi hỏi `GetComboRootOfActor`, đóng `Bug-ReplaceInCombo-TabJump`. Call site xác nhận: `WBP_FurnitureInventory.OnMeshSelected` (thay `ResolveSelectedComboRoot()` cũ). Test PASS 6/6 (`Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 6b.5). ⚠️ **KHÔNG xác nhận được** claim "call site thứ 2 = `CB_Replace`" — section `CB_Replace` hiện tại (không đổi trong lượt này) gọi thẳng `StartReplaceMode` không qua bất kỳ hàm route combo nào; không có node flow/K2Node export nào cho 1 thay đổi ở đó — ghi nhận mâu thuẫn, không tự sửa. Xem ghi chú trong mục hàm. |
| 3.4 | 04/08/2026 13:15 | **`CB_Replace` re-export ✓K2 03/08/2026 — đóng caveat v3.3.** Bản mô tả cũ (✓K2 24/07) đọc lúc CHƯA re-export sau T2 — SUPERSEDED, giữ lại làm lịch sử (không xóa). Bản mới: nhánh BẬT thêm `ShouldRouteReplaceToCombo(Actor=PrimarySelectedActor)` → `Branch(bRouteToCombo)` → `StartReplaceComboMode`/`StartReplaceMode` (node CŨ giữ nguyên ở nhánh False); nhánh TẮT thêm `SET ComboRootGroupIDToReplace=""` (thiếu ở bản cũ). Xác nhận: đủ 2 call site T2 (`OnMeshSelected` + `CB_Replace`), test 2 trial chuột phải PASS 03/08. Bug fix Branch dư (24/07) không bị cuốn lại. |
