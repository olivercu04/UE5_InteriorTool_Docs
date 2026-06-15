# Sprint 2 — Box Select + Context Menu (Plan v2, đã review)

**Phiên bản:** 2.0 | **Ngày viết:** 05/06/2026 | **Người review:** Opus 4.8
**Trạng thái:** Planned (chưa thực thi) | **Ước tính:** 3-4 ngày, 7 tasks
**Tiền đề:** Sprint 1 COMPLETE (multi-select Move+Rotate+Scale đã ship)

> **Plan này thay thế phần Sprint 2 trong `04_Sprint_Details.md` (v cũ).** Đã sửa 4 lỗ hổng, cắt 2 task ít giá trị, thêm 3 cải tiến phù hợp phần mềm thiết kế nội thất.

---

## 0. TÓM TẮT 3 ĐIỂM SỐNG CÒN (đọc trước tiên)

1. **Phân biệt 3 loại mouse-down:** trên gizmo (kéo gizmo) → trên mesh (select) → vùng trống (box select). Box select CHỈ start khi cả GizmoTrace lẫn CAMERA trace đều miss. Đây là rủi ro R7 — sai chỗ này thì kéo gizmo cũng trigger box select.
2. **KHÔNG dùng Load Asset Blocking trong ForEach** (Select Similar). Chỉ so sánh `MeshPath` (String đã có sẵn trên actor). Tiêu chí cần load DA (Category/Folder) → CẮT khỏi v1 hoặc cache trước.
3. **Box select cần ngưỡng kéo tối thiểu (~5px).** Mouse-down rồi thả tại chỗ (di chuyển < 5px) = click deselect bình thường, KHÔNG phải box select. Không có ngưỡng → mọi click vùng trống tạo box 0px gây rối.

---

## 1. So sánh với plan cũ — đã thay đổi gì

| Mục | Plan cũ | Plan v2 | Lý do |
|---|---|---|---|
| Select Similar | 4 tiêu chí (Mesh/Category/Folder/Material), load DA mỗi actor | Chỉ "by Mesh" (so sánh MeshPath, không load) | R1: tránh freeze. Mesh-only đã cover use case chính (chọn tất cả ghế giống nhau) |
| Context Menu đóng | Tick check mouse ngoài bounds | Button trong suốt phủ full màn hình | Bỏ Tick polling (antipattern) |
| Box select detect | Project 1 điểm Actor.Location | Vertical slice point-based → nâng bounding box nếu cảm giác tệ | Pivot có thể ngoài mesh nhìn thấy |
| Ngưỡng kéo | (không có) | THÊM: drag > 5px mới là box | Tránh click thường tạo box rỗng |
| Esc cancel | (không có) | THÊM: Esc hủy box giữa drag | UX an toàn |
| Ctrl+I Invert | S2.T6 | CẮT → dời Sprint 6 | Ít giá trị cho nội thất |
| Reset Rotation | (không có) | THÊM vào context menu | Sửa nhanh đồ xoay lệch |
| Cut (Ctrl+X) | S2.T7 | Giữ, đánh dấu OPTIONAL | Rẻ (reuse Copy) nhưng nội thất ít dùng cut |

---

## 2. Quyết định kiến trúc (đã chốt)

### 2.1 Thứ tự ưu tiên mouse-down (R7 — quan trọng nhất)
Trong Mouse Left Pressed (đã có sẵn flow Sprint 1, xem `BP_FurnitureInputManager.md` Step 0-7):
```
Step 2: GizmoController.OnMousePressed (đã trace GizmoTrace)
Step 3: bIsDraggingGizmo == True → STOP   ← đang kéo gizmo, không làm gì khác
Step 4: GetHitResultUnderCursorByChannel(CAMERA) → bHit
Step 5: bHit == False (vùng trống):
          ← ĐÂY là chỗ thêm box select (thay vì DeselectAll ngay)
          Ghi nhớ StartPos, đánh dấu "pending box" — CHƯA spawn overlay vội
Step 6-7: (giữ nguyên — select/toggle khi hit mesh)
```
**Then:** quyết định box select hay deselect dời sang lúc chuột **di chuyển đủ xa** (Tick) hoặc lúc **thả** (Released), dựa trên ngưỡng kéo.

### 2.2 Ngưỡng kéo (drag threshold)
- Mouse-down vùng trống → SET `BoxStartPos`, SET `bPendingBox = True`. Chưa spawn overlay.
- Event Tick: nếu `bPendingBox` AND `Distance(CurrentPos, BoxStartPos) > 5px` → bây giờ mới spawn overlay, SET `bIsBoxSelecting = True`, SET `bPendingBox = False`.
- Mouse Released:
  - nếu `bIsBoxSelecting` → tính rect, chọn đồ trong khung.
  - nếu chỉ `bPendingBox` (chưa vượt ngưỡng) → đây là click thường → DeselectAll (nếu không giữ Ctrl).
  - reset cả 2 cờ.

### 2.3 Box select: point-based trước (vertical slice)
v1 dùng `Project World To Screen(Actor.GetActorLocation)` → check trong rect. Test ngay. Nếu cảm giác chọn sai nhiều (pivot ngoài mesh) → nâng cấp:
```
Nâng cấp bounding box:
  Get Actor Bounds(Actor) → Origin, BoxExtent
  Project 8 góc của box → screen → tính AABB screen-space
  Check AABB đó có overlap rect không (overlap = chọn, không cần nằm trọn)
```

### 2.4 Context Menu đóng bằng background button
`WBP_ContextMenu` root = Canvas Panel:
- Child 1 (dưới cùng): `BtnBackground` — Button trong suốt, full màn hình, Visibility = Visible, style alpha = 0. OnClicked → Hide menu.
- Child 2 (trên): Border + VerticalBox chứa các item.
→ Click bất kỳ đâu ngoài menu = trúng BtnBackground = đóng. KHÔNG dùng Tick.

---

## 3. TASK BREAKDOWN (7 tasks)

### S2.T1 — WBP_BoxSelectOverlay (1 giờ)
**File:** WBP_BoxSelectOverlay (mới)

Layout: Canvas Panel root + 1 Image (Tint = 0.2, 0.6, 1.0, 0.2; Hit Test = Not Hit Testable).

Variables: `StartPos : Vector2D`, `CurrentPos : Vector2D`.

Functions:
- `StartDrawing(StartScreenPos)`: SET StartPos = CurrentPos = input; Set Visibility = Visible.
- `UpdateDrawing(CurrentScreenPos)`:
  ```
  SET CurrentPos = input
  TopLeft = (min(Start.X,Cur.X), min(Start.Y,Cur.Y))
  Size    = (abs(Cur.X-Start.X), abs(Cur.Y-Start.Y))
  Slot as Canvas Slot(Image) → Set Position(TopLeft) + Set Size(Size)
  ```
- `StopDrawing → Returns (Min : Vector2D, Max : Vector2D)`:
  ```
  Min = (min X, min Y), Max = (max X, max Y)   ← chuẩn hóa để Min luôn < Max
  Set Visibility = Hidden
  Return Min, Max
  ```

**Test:** spawn thử widget, gọi StartDrawing + UpdateDrawing tay → thấy khung xanh vẽ đúng.

---

### S2.T2 — Box Select logic + ngưỡng kéo + Esc cancel (2.5 giờ)
**File:** BP_FurnitureInputManager (+ kiểm tra IA_Escape ở PC)

**Variables mới:**
```
BoxOverlayRef   : WBP_BoxSelectOverlay   (Soft hoặc hard ref — clear ở End Play)
BoxStartPos     : Vector2D
bPendingBox     : Boolean
bIsBoxSelecting : Boolean
```

**Mouse Left Pressed — sửa Step 5:**
```
Step 5: bHit == False:
  NOT IsCtrlDown:   ← (giữ Ctrl thì không deselect, để cộng dồn)
    GET Mouse Position on Viewport → SET BoxStartPos
    SET bPendingBox = True
    STOP   ← CHƯA deselect, CHƯA spawn overlay
  IsCtrlDown:
    GET Mouse Position on Viewport → SET BoxStartPos
    SET bPendingBox = True
    STOP
```
> Lưu ý: deselect dời sang Released (chỉ deselect nếu là click thường, không phải box).

**Event Tick — thêm:**
```
Branch bPendingBox:
  T:
    GET Mouse Position on Viewport → CurrentPos
    Distance(CurrentPos, BoxStartPos) > 5?
      T:
        Spawn WBP_BoxSelectOverlay → Add to Viewport (Z=50) → SET BoxOverlayRef
        BoxOverlayRef.StartDrawing(BoxStartPos)
        SET bIsBoxSelecting = True
        SET bPendingBox = False

Branch bIsBoxSelecting:
  T:
    GET Mouse Position on Viewport → CurrentPos
    BoxOverlayRef.UpdateDrawing(CurrentPos)
```

**Mouse Left Released — thêm:**
```
Branch bIsBoxSelecting:
  T:
    Min, Max = BoxOverlayRef.StopDrawing
    BoxOverlayRef.Remove from Parent → SET BoxOverlayRef = None

    CLEAR LocalActorsInBox
    Get All Actors With Tag("FurnitureSpawned"):
      ForEach Actor:
        IsValid(Actor)?
          T:
            Project World To Screen(Actor.GetActorLocation) → screenPos, bOnScreen
            Branch bOnScreen
                   AND screenPos.X >= Min.X AND screenPos.X <= Max.X
                   AND screenPos.Y >= Min.Y AND screenPos.Y <= Max.Y:
              T → Cast BP_FurnitureActor → ADD to LocalActorsInBox

    Branch IsCtrlDown:
      F → DeselectAll → SelectActors(LocalActorsInBox)
      T → SelectActors(LocalActorsInBox)   ← cộng dồn

    CaptureSnapshot("BoxSelect")
    SET bIsBoxSelecting = False

  F:   ← không box → kiểm tra pending (click thường vùng trống)
    Branch bPendingBox:
      T:
        NOT IsCtrlDown → DeselectAll   ← click thường = deselect
        SET bPendingBox = False
```

**Esc cancel (giữa drag):** trong handler IA_Escape (nếu chưa có thì thêm route ở PC → InputManager.CancelBoxSelect):
```
CancelBoxSelect:
  Branch bIsBoxSelecting OR bPendingBox:
    T:
      IsValid(BoxOverlayRef) → Remove from Parent → SET None
      SET bIsBoxSelecting = False
      SET bPendingBox = False
```

**End Play:** thêm `IsValid(BoxOverlayRef) → Remove from Parent → SET None` (chống VRAM leak — R4).

**Test:**
- Kéo khung > 5px vùng trống → đồ trong khung chọn.
- Click nhanh (< 5px) vùng trống → deselect, KHÔNG hiện khung.
- Ctrl + kéo khung → cộng vào selection cũ.
- Kéo chính xác trục gizmo → move, KHÔNG box select (R7).
- Đang kéo khung → Esc → khung biến mất, không chọn gì.

---

### S2.T3 — WBP_ContextMenu + WBP_ContextMenuItem (1.5 giờ)
**File:** WBP_ContextMenu (mới), WBP_ContextMenuItem (mới)

**WBP_ContextMenuItem:**
```
Layout: Horizontal Box: [Icon (optional)] [Label Text] [Spacer] [Shortcut Text]
        + Button overlay (Style: Normal/Hovered đổi màu nền nhẹ)
Variables: Label : Text, Shortcut : Text
Dispatcher: OnItemClicked()   ← parameterless
Button OnClicked → Broadcast OnItemClicked
ExposeOnSpawn: Label, Shortcut (để set khi Create Widget)
```

**WBP_ContextMenu:**
```
Layout: Canvas Panel root
  Child 1: BtnBackground (Button, full màn, alpha=0) → OnClicked → Hide
  Child 2: Border (nền tối + viền) → VerticalBox (MenuList) chứa các item

Function AddMenuItem(Label, Shortcut) → Returns WBP_ContextMenuItem:
  Create WBP_ContextMenuItem (ExposeOnSpawn Label, Shortcut)
  Add to MenuList
  Return item   ← caller tự bind OnItemClicked

Function AddSeparator: thêm 1 Image mảnh (1px, xám) vào MenuList

Function ShowAt(ScreenPos):
  Add to Viewport (Z Order = 99999)   ← R11
  Slot as Canvas Slot(Border) → Set Position(ScreenPos)
  ← clamp nếu menu tràn cạnh phải/dưới màn hình (optional)

Function Hide: Remove from Parent
```
> Không Tick. Click ngoài menu = trúng BtnBackground = Hide.

**Test:** tạo menu tay với 3 item + 1 separator → ShowAt(mouse) → click item thấy log → click vùng ngoài thấy menu đóng.

---

### S2.T4 — Right-click handler (1.5 giờ)
**File:** BP_FurnitureInputManager, BP_FoffPlayerController (chỉ thêm route, KHÔNG thêm biến furniture)

**Input:** IA_RightClick (Boolean), map Right Mouse Button → Started.
**PC route:** IA_RightClick Started → Get All Actors Of Class(InputManager) → Get(0) → OnRightClick.

**Event OnRightClick (InputManager):**
```
IsValid(ContextMenuRef) → Hide → SET None   ← đóng menu cũ nếu còn

GetHitResultUnderCursorByChannel(CAMERA) → HitActor, bHit
Branch bHit AND HasTag(HitActor, "FurnitureSpawned"):
  T:   ← right-click trên đồ
    Cast HitActor → BP_FurnitureActor → bp
    Branch SelectedActors.Contains(bp):
      F → SelectSingleActor(bp)   ← nếu right-click đồ chưa chọn → chọn nó
    Create WBP_ContextMenu → SET ContextMenuRef
    item_Copy      = AddMenuItem("Sao chép", "Ctrl+C")   → bind CopyMesh
    item_Duplicate = AddMenuItem("Nhân đôi", "Ctrl+D")   → bind DuplicateMesh
    AddSeparator
    item_Material  = AddMenuItem("Đổi vật liệu", "")     → bind (mở material panel)
    item_Replace   = AddMenuItem("Thay thế", "")         → bind (EnterReplaceMode)
    item_ResetRot  = AddMenuItem("Reset xoay", "")       → bind ResetRotation   ← THÊM
    item_SelSim    = AddMenuItem("Chọn đồ giống", "")    → bind SelectSimilarMesh
    AddSeparator
    item_Delete    = AddMenuItem("Xóa", "Delete")        → bind DeleteSelected
    ShowAt(MousePos)
  F:   ← right-click vùng trống
    Create WBP_ContextMenu → SET ContextMenuRef
    item_Paste = AddMenuItem("Dán", "Ctrl+V")            → bind PasteMesh
    item_Undo  = AddMenuItem("Hoàn tác", "Ctrl+Z")       → bind Undo
    item_Redo  = AddMenuItem("Làm lại", "Ctrl+Shift+Z")  → bind Redo
    ShowAt(MousePos)
```
**Mỗi callback:** bind xong phải gọi `ContextMenuRef.Hide` SAU action (item callback → action → Hide menu).

**Variables mới:** `ContextMenuRef : WBP_ContextMenu` (clear ở End Play).

**Test:** right-click đồ → menu hiện tại cursor. Click "Nhân đôi" → đồ duplicate + menu đóng. Right-click vùng trống → menu Paste/Undo/Redo.

---

### S2.T5 — Select Similar by Mesh (45 phút) — ĐÃ ĐƠN GIẢN HÓA
**File:** BP_FurnitureInputManager

```
Function SelectSimilarMesh(ReferenceActor : BP_FurnitureActor):
  IsValid(ReferenceActor)? F → return
  refMeshPath = ReferenceActor.MeshPath   ← String, KHÔNG load gì

  CLEAR LocalSimilar
  Get All Actors With Tag("FurnitureSpawned"):
    ForEach actor:
      IsValid(actor)?
        T → Cast BP_FurnitureActor → GET MeshPath
            == refMeshPath? → ADD to LocalSimilar

  DeselectAll → SelectActors(LocalSimilar)
  CaptureSnapshot("SelectSimilar")
```
> CHỈ so sánh MeshPath (đã có sẵn trên actor). KHÔNG Load Asset Blocking → không freeze.
> Category/Folder/Material: nếu sau này muốn → phải cache CachedCategory trên BP_FurnitureActor lúc đặt đồ (DA đã load lúc đó). Để Sprint sau.

**Test:** bày 6 ghế giống + 3 bàn → right-click 1 ghế → "Chọn đồ giống" → 6 ghế chọn, 3 bàn không.

---

### S2.T6 — Reset Rotation + Delete callback (30 phút)
**File:** BP_FurnitureInputManager

```
Function ResetRotation:
  Branch SelectedActors.Length == 0 → return
  ForEach SelectedActors (Actor):
    IsValid(Actor)? T → Set Actor Rotation(Actor, Rotator(0,0,0))
  ← nếu đang multi-select: RefreshOffsets(GizmoPivotActor) để gizmo sync
  CaptureSnapshot("ResetRotation")

Function DeleteSelected:   ← gom logic xóa cho context menu (reuse nếu đã có)
  Branch SelectedActors.Length == 0 → return
  ForEach SelectedActors (Actor): IsValid → Destroy Actor
  CLEAR SelectedActors → SET Primary = None → DeactivateGizmo → DestroyPivot
  Broadcast OnSelectionChanged([], None)
  CaptureSnapshot("DeleteMulti")
```

**Test:** xoay 1 đồ lệch → right-click → "Reset xoay" → về 0°. Right-click → "Xóa" → đồ biến mất, Undo được.

---

### S2.T7 — Cut (Ctrl+X) — OPTIONAL (15 phút)
**File:** LM, PC, BP_FurnitureInputManager
```
Function CutMesh:
  Branch SelectedActors.Length == 0 → return
  Call CopyMesh                       ← copy TRƯỚC khi destroy
  Call DeleteSelected                 ← reuse T6
  ← (đã CaptureSnapshot trong DeleteSelected; đổi tên thành "Cut" nếu muốn)
```
> Đánh dấu OPTIONAL: dân thiết kế nội thất hiếm cut/paste, thường kéo trực tiếp. Làm nếu còn thời gian.

---

## 4. ĐÃ CẮT khỏi Sprint 2 (ghi DEVIATIONS.md)
- **Ctrl+I Invert Selection** → dời Sprint 6 (Polish). Lý do: ít giá trị cho thiết kế nội thất.
- **Select Similar by Category / Folder / Material** → để sau, cần cache metadata để tránh R1.

---

## 5. Test cases tổng (làm riêng từng cái)

| # | Case | Kỳ vọng |
|---|---|---|
| 1 | Kéo khung > 5px vùng trống | Đồ trong khung chọn |
| 2 | Click nhanh (< 5px) vùng trống | Deselect, không hiện khung |
| 3 | Ctrl + kéo khung | Cộng vào selection cũ |
| 4 | Kéo chính xác trục gizmo | Move, KHÔNG box select (R7) |
| 5 | Esc giữa lúc kéo khung | Khung biến mất, không chọn |
| 6 | Box select trên màn 4K (DPI 150%) | Khung trùng cursor (R8) |
| 7 | Right-click đồ đang chọn | Menu hiện tại cursor |
| 8 | Right-click đồ CHƯA chọn | Chọn nó + menu hiện |
| 9 | Click item menu | Action chạy + menu đóng |
| 10 | Click ngoài menu | Menu đóng (không cần Tick) |
| 11 | Right-click vùng trống | Menu Paste/Undo/Redo |
| 12 | Select Similar (6 ghế + 3 bàn) | 6 ghế chọn |
| 13 | Reset Rotation đồ xoay lệch | Về 0°, Undo được |
| 14 | Cut → Paste (nếu làm T7) | Đồ cắt rồi dán lại được |

---

## 6. Rollback nếu fail
- Box select fail (R7/R8 không giải được sau 3 lần) → giữ click-select + Ctrl+click (Sprint 1 đã đủ). Box select dời sau.
- Context menu fail → giữ toolbar WBP_MeshControls + phím tắt (đã có). Context menu là bổ sung.
- Mỗi cái độc lập — fail cái này không kéo cái kia.

---

## 7. Thứ tự thực thi đề xuất
1. S2.T3 + S2.T4 (Context Menu) TRƯỚC — rủi ro thấp, không đụng gizmo, thấy kết quả nhanh.
2. S2.T5 + S2.T6 (Select Similar + Reset/Delete callback) — nối vào context menu.
3. S2.T1 + S2.T2 (Box Select) — rủi ro cao nhất (R7/R8), làm sau khi đã quen nhịp.
4. S2.T7 (Cut) nếu còn thời gian.
5. Test tổng + cập nhật doc + DEVIATIONS.

> Đảo thứ tự so với plan cũ: làm phần dễ (context menu) trước để lấy đà, để rủi ro box-select cuối.
