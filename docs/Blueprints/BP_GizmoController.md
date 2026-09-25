# BP_GizmoController
**HỢP NHẤT TỪ 2 file:** v1.1 base (05/06) + OnMouseReleased fragment (16/04, v1.0 tham khảo)
**Phiên bản:** 1.5 | **Cập nhật:** 25/09/2026 09:10 ICT — F2 phần B đóng: InputManager bỏ qua Undo/Redo khi `bIsDraggingGizmo` (Function `IsGizmoDragging`), PIE PASS.
**Phiên bản:** 1.4 | **Cập nhật:** 25/09/2026 — 08:50 ICT — Sửa kẹt cờ khi Ctrl+Z giữa lúc kéo (F2): 2 nhánh False của lớp chặn 1–2 nối vào Branch MỚI `bIsDraggingGizmo` → True về khối dọn cờ (không ghi sổ). PIE PASS. Điểm treo 2 đóng phần A.
**Phiên bản:** 1.3 | **Cập nhật:** 25/09/2026 — 08:25 ICT — Sửa nhánh "Scale" của `OnMouseReleased` (Branch 2 so `== Scale`); PIE PASS 3/3 (Move / Rotate / Scale ghi đúng tên mốc). Đóng điểm treo 1.
**Phiên bản:** 1.2 | **Cập nhật:** 24/09/2026 — 20:25 ICT — `OnMouseReleased` ✓K2 export: đính chính khối dọn cờ (chỉ chạy sau CaptureSnapshot) + ⚠ 2 điểm treo | Actor riêng — xử lý toàn bộ gizmo movement logic
**Phiên bản:** 1.1 | **Cập nhật:** 05/06/2026 — 20:00 ICT

> **v1.1 (05/06 T15):** OnMousePressed thêm Cast → BP_PivotActor → RefreshOffsets (capture drag-start cho multi-select rotate/scale).
> **Lịch sử OnMouseReleased:** Fragment 16/04 dùng `Get Player Controller → Cast BP_FoffPlayerController`. Bản v1.1 (05/06) đổi sang `Get All Actors Of Class(BP_FurnitureInputManager)` — nhất quán với architecture (ActiveMode sống ở InputManager, không PlayerController).

---

## Variables
```
TransformerPawnRef    : BP_TransformerPawn
SelectedActor         : StaticMeshActor
bGizmoActive          : Boolean
bIsDraggingGizmo      : Boolean
ActiveAxis            : String
SnapStep              : Float (default=10, 0=tự do)  ← chỉ dùng cho Translation
SnapAngle             : Float (default=15, 0=tự do)  ← chỉ dùng cho Rotation
SnapScale             : Float (default=0.1, 0=tự do) ← chỉ dùng cho Scale
ScaleSpeed            : Float (default=0.01)
DragPlaneX/Y/Z        : Float
InitialHitPoint       : Vector
InitialActorLocation  : Vector
IgnoredActors         : Array of Actor  ← không còn dùng cho gizmo trace
PreviousMousePosition : Vector2D
RotationSpeed         : Float (default=0.3)
AccumulatedRotation   : Float
```

---

## ActivateGizmo(TargetActor, TransformerPawn, TransformType)
```
SET SelectedActor = TargetActor
SET TransformerPawnRef = TransformerPawn

Branch bGizmoActive:
  TRUE (toggle off):
    Deselect All (TransformerPawnRef)
    SET bGizmoActive = False

  FALSE (activate):
    Branch IsValid(SelectedActor) → True:
      Set Transformation Type = TransformType (TransformerPawnRef)
      Select Actor (TransformerPawnRef, SelectedActor)
      Set Actor Location (TransformerPawnRef, Get Actor Location(SelectedActor))
      SET bGizmoActive = True
      DISABLE COLLISION:
        Get All Actors Of Class(StaticMeshActor) → NOT HasTag("FurnitureSpawned") → No Collision
        ← KHÔNG disable collision BaseGizmo — dùng GizmoTrace channel riêng
```

---

## DeactivateGizmo
```
Branch bGizmoActive == True:
  Deselect All → SET bGizmoActive = False → SET SelectedActor = None

← Luôn chạy (cả True và False):
RESTORE COLLISION:
  StaticMeshActor NOT FurnitureSpawned → Query And Physics
```

---

## OnMousePressed — v1.1 (T15: thêm RefreshOffsets cho Pivot)
```
1. LineTraceByChannel (GizmoTrace) → Hit Actor
   ← Dùng GizmoTrace channel — xuyên qua tất cả actors, chỉ hit gizmo
2. Cast Hit Actor → BaseGizmo:
   Failed → STOP
   Success:
     Get Hit Component Display Name → Split (In Str=".", From End) → Right S → SET ActiveAxis
     SET bIsDraggingGizmo = True
     Set Ignore Look Input = True
     GET Actor Location(SelectedActor) → SET InitialActorLocation
     Get Mouse Position → Make Vector2D → SET PreviousMousePosition
     Set DragPlane theo ActiveAxis:
       "XY Plane" → DragPlaneZ | "XZ Plane" → DragPlaneY | "YZ Plane" → DragPlaneX
       "X Axis Box" → DragPlaneY | "Y Axis Box" → DragPlaneX | "Z Axis Box" → DragPlaneX
       "XYZ_Sphere" → DragPlaneZ

     ← T15: capture relative transforms nếu đang drag Pivot (multi-select)
     Sequence → Then(cuối):
       Branch IsValid(SelectedActor):
         True →
           Cast SelectedActor To BP_PivotActor:
             Cast Success → Call RefreshOffsets (Target = As BP_PivotActor)
             Cast Failed  → (single actor, bỏ qua)
         False → (để trống)
```
> RefreshOffsets gọi ở đây là "chụp điểm tham chiếu" ngay trước khi pivot bắt đầu biến đổi. Idempotent — gọi khi không thực sự drag cũng vô hại.

---

## OnMouseReleased — v1.2 ([✓K2 export 24/09/2026] — as-built, thay mô tả v1.1)

> **Đính chính 24/09/2026 (K2 export thật, 36 node, không lỗi compile):** v1.1 ghi khối dọn cờ "luôn chạy, nằm ngoài tất cả
> Branch" — **SAI**. Khối dọn cờ chỉ nối SAU 3 node `CaptureSnapshot`; nhánh False của cả 3 Branch gác là dead-end. Không có
> node `Cast` (mảng `Get All Actors Of Class` đã đúng kiểu → `Get(0).ActiveMode` đọc thẳng).

```
Custom Event OnMouseReleased
▶→ Branch( bGizmoActive )
     False ▶→ [A]                                      ← SỬA 25/09 (trước: dead-end)
     True ▶→ Branch( IsValid(SelectedActor) )
          False ▶→ [A]                                 ← SỬA 25/09 (trước: dead-end)
          True ▶→ Branch( bIsDraggingGizmo )
               False → (dead-end)
               True ▶→ Get All Actors Of Class(BP_FurnitureInputManager) → Get(0).ActiveMode
                    ▶→ Branch( ActiveMode == NewEnumerator2 )      ← NewEnumerator2 = Rotate (xác nhận Print 25/09)
                         True  ▶→ Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Rotate") ──┐
                         False ▶→ Get All Actors Of Class(BP_FurnitureInputManager) → Get(0).ActiveMode           │
                               ▶→ Branch( ActiveMode == Scale )            ← SỬA 25/09 (trước so nhầm NewEnumerator2) │
                                    True  ▶→ Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Scale") ─┤
                                    False ▶→ Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Move")  ─┤
                                                                                                                          ▼
                    [MERGE 3 nhánh + A.True] ▶→ SET bIsDraggingGizmo = False      ← SAU CaptureSnapshot ✓
                                    ▶→ SET ActiveAxis = ""
                                    ▶→ SET PreviousMousePosition = (0, 0)
                                    ▶→ SET AccumulatedRotation = 0.0
                                    ▶→ Set Ignore Look Input(Target = Get Player Controller(0), False)   ← node cuối
```
[A] Branch( bIsDraggingGizmo )   ← node MỚI 25/09 (không dùng lại lớp chặn 3)
      True  ▶→ SET bIsDraggingGizmo = False (đầu khối dọn cờ — KHÔNG CaptureSnapshot)
      False → (dead-end — không đang kéo thì không có gì để dọn)
```
> **Vì sao hỏi lại `bIsDraggingGizmo` ở [A]:** `Set Ignore Look Input` là BỘ ĐẾM (+1 / −1), không phải công tắc — gọi `False` khi chưa từng khoá sẽ trừ mất khoá của hệ thống khác. Chỉ dọn khi thật sự đã bắt đầu kéo.
```
> CaptureSnapshot duyệt tất cả actor tag "FurnitureSpawned" → tự động ghi đúng trạng thái mới của cả nhóm. Pivot (tag "FurniturePivot") KHÔNG bị lưu — đúng ý định.
> SET bIsDraggingGizmo PHẢI SAU CaptureSnapshot — nếu đảo ngược sẽ bug Undo. (✓K2 24/09: đúng thứ tự.)

> ⚠ **Điểm treo từ export 24/09:**
> 1. ✅ **ĐÓNG 25/09** — Branch thứ 2 (nhánh "Scale") từng so lại `ActiveMode == NewEnumerator2` (= Rotate) y hệt Branch thứ
>    nhất → chế độ Scale bị ghi mốc tên **"Move"** (xác nhận bằng Print: `MODE: Scale` → `SNAP: Move`). Sửa: đổi pin B của
>    Branch 2 thành `Scale`. Test PIE 3/3: Scale → `SNAP: Scale`, Rotate → `SNAP: Rotate`, Move → `SNAP: Move`. Undo không bị
>    ảnh hưởng (mốc nào cũng chụp cả cảnh) — chỉ tên mốc sai. Chưa re-export K2 sau khi sửa.
> 2. ✅ **Phần A ĐÓNG 25/09** (xem [A] ở trên, PIE PASS: `REL active=false valid=false drag=true` → không MODE / SNAP → click chọn + xoay camera được). **Phần B ĐÓNG 25/09:** Ctrl+Z về mốc CÓ đồ đang chọn → Undo chọn lại + bật gizmo → lúc thả cả 3 lớp qua → ghi mốc "Move" thừa, cắt nhánh Redo (xác nhận Print). Sửa ở cửa vào: `BP_FurnitureInputManager.IsGizmoDragging` → IA Undo/Redo bỏ qua khi đang kéo. PIE PASS 3/3.
>    Mô tả gốc: thả chuột khi gizmo đã tắt / `SelectedActor` đã mất giữa lúc kéo (vd Ctrl+Z giữa chừng) → rơi vào dead-end → khối dọn
>    cờ KHÔNG chạy → nghi `bIsDraggingGizmo` kẹt True + Ignore Look Input kẹt → `Mouse Left Pressed` Step 3 (InputManager)
>    chặn click chọn đồ. Giả thuyết, chưa test.

---

## Event Tick — Hover Highlight
```
Branch IsValid(SelectedActor) → True:
  LineTrace (GizmoTrace, IgnoredActors=[SelectedActor])
  → Cast To BaseGizmo:
    Success → TransformerPawnRef → Trace by Channel
    Failed  → TransformerPawnRef → Clear Domain
```

---

## Event Tick — Movement
```
Branch IsValid(SelectedActor) AND bIsDraggingGizmo → True:
  Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → GET ActiveMode

  Sequence:
    Then 0 → Branch ActiveMode == Rotate?
      True → ROTATION LOGIC:
        CurrentPos - PreviousMousePosition → MouseDelta
        SET PreviousMousePosition = CurrentPos

        Switch ActiveAxis:
          "X Axis Box": MouseDelta.Y × Speed → AccumulatedRotation
            SnapAngle > 0 AND Abs(Acc) >= SnapAngle:
              Add World Rotation (Roll = Sign×SnapAngle) → AccumulatedRotation - SnapAmount
            Else: Add World Rotation (Roll = Acc) → Reset Acc = 0
          "Y Axis Box": MouseDelta.Y → Pitch (tương tự X)
          "Z Axis Box": MouseDelta.X → Yaw (tương tự X)

    Then 1 → Branch ActiveMode == Move?
      True → TRANSLATION LOGIC (ray-plane intersection):
        "X Axis Box": plane Y → compute HitX → Snap → Set Actor Location X
        "Y Axis Box": plane X → set Y
        "Z Axis Box": plane X → set Z
        "XY Plane": plane Z → set X+Y
        "XZ Plane": plane Y → set X+Z
        "YZ Plane": plane X → set Y+Z
        "XYZ_Sphere": plane Z → set X+Y

    Then 2 → Branch ActiveMode == Scale?
      True → SCALE LOGIC:
        CurrentPos - PreviousMousePosition → MouseDelta
        SET PreviousMousePosition = CurrentPos
        Get Actor Scale 3D (SelectedActor) → Break Vector → X, Y, Z

        Switch ActiveAxis:
          "X Axis Box": MouseDelta.X × ScaleSpeed + CurrentScale.X → RawScale
            SnapScale > 0: Round(Raw/Snap) × Snap → NewScale → Set Actor Scale3D (NewScale, Y, Z)
          "Y Axis Box": MouseDelta.X → Y axis (tương tự X)
          "Z Axis Box": MouseDelta.Y × -1 → Z axis (tương tự X)
          "XYZ_Sphere": Average(X,Y,Z) + MouseDelta.X × ScaleSpeed → RawScale → Snap → Set Actor Scale3D (New, New, New)
```

---

## Lưu ý khi tích hợp project tổng
- **GizmoTrace Channel** — custom trace channel chỉ gizmo block, tất cả actors khác ignore
- Không cần IgnoredActors list nữa — GizmoTrace xuyên qua tất cả
- Gizmo collision KHÔNG bị disable/enable trong ActivateGizmo/DeactivateGizmo
- Gizmo material cần tăng **Emissive x1000** nếu project dùng Lumen

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 23/04/2026 | Logic gốc (fragment 16/04 — OnMouseReleased dùng PlayerController cast) |
| 1.1 | 05/06/2026 — 20:00 ICT | T15: OnMousePressed thêm Cast → BP_PivotActor → RefreshOffsets. OnMouseReleased đổi sang Get All Actors(InputManager) → Cast → GET ActiveMode (thay Get Player Controller → BP_FoffPlayerController). |
| 1.5 | 25/09/2026 09:10 ICT | F2 phần B: guard `IsGizmoDragging` trong IA Undo/Redo (InputManager) — không còn mốc "Move" thừa sau Ctrl+Z giữa lúc kéo. PIE PASS. |
| 1.4 | 25/09/2026 — 08:50 ICT | F2 phần A: lớp chặn 1–2 nhánh False → Branch MỚI `bIsDraggingGizmo` → True về khối dọn cờ, không ghi sổ. Xác nhận nguyên nhân bằng Print `REL` (Ctrl+Z giữa lúc kéo → `active=false valid=false drag=true`). PIE PASS (log sạch, click + xoay camera OK). Phần B (mốc "Move" thừa khi Undo về mốc có selection) còn mở. |
| 1.3 | 25/09/2026 — 08:25 ICT | Sửa `OnMouseReleased` Branch 2: `ActiveMode == Scale` (trước so nhầm `NewEnumerator2` = Rotate → Scale ghi mốc "Move"). Xác nhận bằng Print String + PIE 3/3 PASS. Đóng điểm treo 1; điểm 2 (kẹt cờ khi Ctrl+Z giữa lúc kéo) còn chờ test. |
| 1.2 | 24/09/2026 — 20:25 ICT | `OnMouseReleased` ✓K2 export (36 node): khối dọn cờ chỉ chạy SAU `CaptureSnapshot` (v1.1 ghi "luôn chạy" — sai); 3 Branch gác nhánh False = dead-end; không có Cast. ⚠ 2 Branch chọn tên entry cùng so `NewEnumerator2`; ⚠ nghi kẹt `bIsDraggingGizmo` nếu thả chuột sau khi gizmo tắt giữa chừng — chờ test. |

---

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Có mặt trong thao tác:** [[L04 · Chọn đồ|L04]] · [[L05 · Di chuyển và xoay đồ|L05]] · [[L13 · Hoàn tác và làm lại|L13]]

**Thuộc mảng kết nối:** [[Kết nối 3a - Chọn đồ Gizmo Nhóm]] · [[Kết nối 3d - Save Undo khởi động]]

**Gọi / điều khiển →**
- [[BP_TransformerPawn]] — giữ tham chiếu · TransformerPawnRef
- [[BP_PivotActor]] — cập nhật trục lúc bấm + dời pivot khi kéo · RefreshOffsets(), Set Actor Location
- [[BP_FurnitureActor]] — dời món khi kéo (1 món) · Set Actor Location(SelectedActor)
- [[BP_FurnitureInputManager]] — hỏi chế độ hiện tại · GET ActiveMode ✓K2
- [[BP_UndoManager]] — chụp trạng thái khi kéo xong · CaptureSnapshot() ✓K2
- [[BP_UndoManager]] — lưu mốc sau khi kéo · CaptureSnapshot(Move/Rotate/Scale) ✓K2

**← Được gọi bởi**
- [[BP_FurnitureInputManager]] — gọi lúc bấm chuột + giữ tham chiếu · OnMousePressed(), GizmoControllerRef
- [[WBP_MeshControls]] — tắt rồi bật gizmo khi đổi chế độ · DeactivateGizmo() / ActivateGizmo() — lấy tham chiếu từ đâu ?

<!-- BRAIN:END -->
