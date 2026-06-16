# S1.T15 — Multi-Rotate/Scale qua Pivot (Plan đầy đủ)

**Phiên bản:** 1.1 | **Ngày viết:** 04/06/2026
**Trạng thái:** Planned (chưa thực thi)
**Độ khó:** Cao (2-3 giờ) | **Rủi ro chính:** shear khi non-uniform scale + rotation

> **Changelog v1.1:** Sửa 6 lỗ hổng so với v1.0 — thêm CaptureSnapshot sau release (GAP 1), nhấn mạnh đổi RefreshOffsets + ApplyTransformToChildren đồng thời + test Move-only ngay (GAP 2), thêm reset pivot rotation/scale (GAP 3), chốt thứ tự Compose + cách verify (GAP 4), làm rõ idempotency của detection (GAP 5), ghi chú InitialPivotTransform (GAP 6).

---

## 0. TÓM TẮT 3 ĐIỂM SỐNG CÒN (đọc trước tiên)

1. **RefreshOffsets và ApplyTransformToChildren phải đổi CÙNG LÚC.** Đổi 1 cái → Move-only vỡ. Sau khi đổi xong CẢ HAI → test Move-only NGAY (chưa đụng rotate/scale) để chắc không regression.
2. **Phải có CaptureSnapshot sau khi thả chuột rotate/scale.** Không có → Undo không hoạt động cho rotate/scale.
3. **SpawnOrUpdatePivot phải reset pivot rotation=(0,0,0), scale=(1,1,1)** mỗi khi tái định vị cho selection mới → gizmo bắt đầu sạch.

---

## 1. Quyết định kiến trúc

### Vấn đề với cách cũ (delta-based)
ApplyTransformToChildren hiện tại tính `deltaMove = CurrentLocation - LastPivotTransform.Location` rồi cộng vào vị trí actor:
- OK cho Move (cộng delta vị trí)
- SAI cho Rotate/Scale: rotate quanh tâm cần vị trí TƯƠNG ĐỐI của mỗi actor so với pivot, không phải delta. Delta-based tích lũy lỗi qua từng frame.

### Cách mới — Transform Composition
Dùng hệ thống Transform của UE5 thay vì tự tính location/rotation/scale riêng:

1. **Lúc bắt đầu drag:** lưu transform của mỗi actor **tương đối** so với pivot (`InitialRelativeTransforms`).
2. **Mỗi frame khi drag:** lấy transform hiện tại của pivot, **dựng lại** world transform của mỗi actor = relative ∘ current pivot.

UE5 xử lý Move + Rotate + Scale trong 1 phép compose. Không tính tay → ít bug.

**2 node chính:**
- `Make Relative Transform (A, Relative To B)` → A biểu diễn trong không gian của B
- `Compose Transforms (A, B)` → dựng lại world từ relative

---

## 2. Thay đổi biến trong BP_PivotActor

### Thêm 2 biến mới
```
InitialRelativeTransforms : Array of Transform   ← MỚI (thay 3 array cũ về mặt chức năng)
InitialPivotTransform     : Transform            ← MỚI (chỉ dùng nội bộ RefreshOffsets)
```

**Ghi chú GAP 6:** `InitialPivotTransform` chỉ được đọc trong RefreshOffsets (làm mốc tính relative). ApplyTransformToChildren KHÔNG đọc nó (chỉ dùng `currentPivotT`). Có thể inline `GetActorTransform(Self)` trong RefreshOffsets thay vì lưu biến, nhưng giữ biến tiện debug — không bắt buộc.

### Biến cũ (T3)
3 biến `InitialOffsets`, `InitialChildScales`, `InitialChildRotations`: **giữ nguyên lúc làm T15** (đừng xóa), bỏ sau khi test pass toàn bộ. Lý do: tránh phá vỡ thứ gì còn tham chiếu chúng trong lúc chuyển đổi.

---

## 3. Function RefreshOffsets (viết lại)

⚠️ **Phải viết lại CÙNG LÚC với ApplyTransformToChildren (Mục 4) — đừng compile giữa chừng chỉ với 1 cái.**

Gọi tại các thời điểm: SpawnOrUpdatePivot (selection đổi), Nudge xong, và drag-start. KHÔNG gọi mỗi frame.

```
RefreshOffsets:
  SET InitialPivotTransform = GetActorTransform (Self)

  Array Clear → [InitialRelativeTransforms]

  ForEach AttachedActors (Actor):
    Branch IsValid(Actor):
      True →
        childT = GetActorTransform (Actor)
        relT = Make Relative Transform (
                 A          = childT,
                 RelativeTo = InitialPivotTransform
               )
        ADD relT → [InitialRelativeTransforms]
      False → (để trống)
```

**Giải thích:** `Make Relative Transform(childWorld, pivotWorld)` = transform của actor NẾU coi pivot là gốc tọa độ. Đây là "công thức cố định" của mỗi actor trong nhóm.

---

## 4. Function ApplyTransformToChildren (viết lại — FULL)

Gọi mỗi frame trong Tick khi drag.

```
ApplyTransformToChildren:
  currentPivotT = GetActorTransform (Self)

  ForEach AttachedActors (Index, Actor):
    Branch IsValid(Actor):
      True →
        GET InitialRelativeTransforms [Index] → relT
        newWorldT = Compose Transforms (
                      A = relT,
                      B = currentPivotT
                    )
        Set Actor Transform (
          Target        = Actor,
          New Transform = newWorldT,
          Sweep         = False,
          Teleport      = TeleportPhysics
        )
      False → (để trống)
```

### Thứ tự Compose — CHỐT (GAP 4)
Pattern chuẩn UE5 để dựng lại world từ relative + parent:
```
relT   = MakeRelativeTransform(childWorld, pivotWorld)   ← trong RefreshOffsets
newWorld = ComposeTransforms(relT, currentPivot)         ← trong Apply, A=relT, B=currentPivot
```
Đây là phép nghịch đảo của nhau. Khi `currentPivot == InitialPivotTransform` (pivot chưa di chuyển), `newWorld == childWorld` (identity) → actor đứng yên.

**Cách verify (làm ở test case 1):** Multi-select 2 đồ, KHÔNG đụng gizmo, để yên 1-2 giây. Nếu đồ đứng yên → thứ tự ĐÚNG. Nếu đồ tự nhảy/dịch khi chưa làm gì → thứ tự SAI → **đảo A và B** (đổi thành `A=currentPivotT, B=relT`).

---

## 5. Cơ chế detect "drag bắt đầu trên Pivot"

RefreshOffsets phải được gọi NGAY TRƯỚC khi gizmo bắt đầu biến đổi pivot.

### Chỗ đặt: BP_GizmoController, trong OnMousePressed

```
OnMousePressed (sau khi xác nhận bắt đầu drag gizmo):
  Branch IsValid(SelectedActor):
    True →
      Cast SelectedActor To BP_PivotActor:
        Cast Success →
          Call RefreshOffsets (Target = As BP_PivotActor)
        Cast Failed → (single actor, bỏ qua)
    False → (để trống)
```

**Lý do:** `SelectedActor` của GizmoController = actor đang bị gizmo điều khiển. Multi-select → đó là GizmoPivotActor. Cast thành công = đang drag pivot → capture initial state trước khi biến đổi.

### Làm rõ idempotency (GAP 5)
OnMousePressed fire MỌI cú click trái, không chỉ lúc grab gizmo. Gọi RefreshOffsets khi KHÔNG thực sự drag là **vô hại** — nó chỉ re-capture relative transforms ở trạng thái hiện tại (pivot chưa đổi → relative không đổi). Không cần thêm guard phức tạp. Quan trọng: OnMousePressed fire TRƯỚC khi pivot dịch chuyển frame đầu → timing đúng.

---

## 6. CaptureSnapshot sau khi rotate/scale (GAP 1 — BẮT BUỘC)

Không có bước này → Undo KHÔNG hoạt động cho rotate/scale.

### Chỗ đặt: BP_GizmoController, trong OnMouseReleased (kết thúc drag)

Kiểm tra xem OnMouseReleased hiện đã gọi CaptureSnapshot cho Move chưa. Nếu rồi → đảm bảo nó CŨNG fire khi SelectedActor là Pivot. Nếu chưa → thêm:

```
OnMouseReleased (khi kết thúc drag gizmo):
  ... (logic Move hiện có) ...

  ← Đảm bảo capture cho cả trường hợp Pivot:
  Get All Actors Of Class (BP_UndoManager) → GET[0]
  → CaptureSnapshot ("MultiTransform")
```

**Quan trọng:** CaptureSnapshot duyệt tất cả actor tag "FurnitureSpawned" và lưu Location/Rotation/Scale của từng cái (S_FurniturePlacement đã có đủ 3 trường). Nên chỉ cần gọi 1 lần sau release → tự động ghi đúng trạng thái mới của cả nhóm. Pivot (tag "FurniturePivot") KHÔNG bị lưu vì khác tag.

**Lưu ý không double-capture:** Nếu OnMouseReleased đã có CaptureSnapshot cho Move rồi thì KHÔNG thêm cái thứ 2 — chỉ cần chắc nó chạy cho mọi trường hợp (cả single lẫn pivot). Tránh tạo 2 snapshot cho 1 thao tác.

---

## 7. Reset pivot rotation/scale cho selection mới (GAP 3 — BẮT BUỘC)

Sau khi rotate nhóm tới 45° rồi thả, pivot giữ 45°. Khi bắt đầu selection MỚI (Ctrl+Click thêm đồ → SpawnOrUpdatePivot chạy lại), nếu không reset → gizmo hiện sai góc 45° cho nhóm mới.

### Sửa SpawnOrUpdatePivot
Tại đoạn tái định vị pivot (sau khi spawn/lấy GizmoPivotActor, trước RefreshOffsets), thêm:

```
SET Actor Location (GizmoPivotActor, Center)
Set Actor Rotation (GizmoPivotActor, Rotator(0,0,0))   ← THÊM
Set Actor Scale 3D (GizmoPivotActor, Vector(1,1,1))    ← THÊM
Call RefreshOffsets (GizmoPivotActor)
```

**Lý do toán học vẫn đúng:** RefreshOffsets sau reset sẽ capture relative transforms tương đối với pivot identity (rotation 0, scale 1). Các actor con giữ nguyên world transform của chúng (reset pivot KHÔNG đụng con, vì con chưa attach). Khi drag gizmo, mọi thứ tính từ mốc identity sạch.

---

## 8. Đồng bộ với Tick + Nudge

- **Tick guard:** giữ `IsValid(AttachedActors[0])`. ApplyTransformToChildren mới chạy mỗi frame khi Tick bật — vì dùng Transform Composition tuyệt đối (relative ∘ current), KHÔNG tích lũy lỗi.
- **Nudge (T10):** code Nudge gọi RefreshOffsets sau khi nudge xong để resync. Giữ nguyên — RefreshOffsets mới resync đúng. Đây là path bàn phím riêng, không xung đột với gizmo drag.
- **KHÔNG gọi RefreshOffsets mỗi frame trong lúc drag** — chỉ tại drag-start (Mục 5). Nếu lỡ gọi mỗi frame → mất điểm tham chiếu, rotate/scale sẽ đứng yên.

---

## 9. Test cases (làm RIÊNG từng case, đừng gộp)

| # | Case | Kỳ vọng | Pass? |
|---|------|---------|-------|
| 0 | **Regression: Move-only** (ngay sau khi viết lại Mục 3+4) | Multi-select 2-3 đồ, gizmo Move → di chuyển cùng nhau đúng như trước | ☐ |
| 1 | **Verify Compose order:** multi-select 2 đồ, để yên không đụng | Đồ đứng yên (không tự nhảy) | ☐ |
| 2 | Rotate nhóm 2 đồ chưa xoay | Cả 2 xoay quanh center, khoảng cách giữ nguyên | ☐ |
| 3 | Rotate nhóm có 1 đồ xoay sẵn 45° | Đồ đó giữ +45° tương đối khi nhóm xoay | ☐ |
| 4 | Scale uniform 2x | Khoảng cách giữa các đồ ×2, size mỗi đồ ×2 | ☐ |
| 5 | Scale non-uniform (X=2, Y=1) | KHÔNG méo hình (shear) — case dễ fail | ☐ |
| 6 | Rotate rồi Scale liên tiếp | Không tích lũy lỗi, formation đúng | ☐ |
| 7 | Move + Rotate + Scale 3 đồ rồi Undo/Redo | Về đúng vị trí/xoay/scale từng bước | ☐ |
| 8 | Rotate nhóm → thả → Ctrl+Click thêm đồ thứ 3 | Gizmo nhóm mới bắt đầu ở góc 0 (không kế thừa 45°) | ☐ |

---

## 10. Plan B — nếu gặp shear ở case 5

**Nguyên nhân:** Non-uniform scale (X≠Y≠Z) không giao hoán với rotation. Pivot scale non-uniform + actor con đã xoay → méo (shear). Đây là **giới hạn toán học cơ bản**, không phải bug.

**Giải pháp:** Chặn non-uniform scale khi multi-select. Chỉ cho scale uniform (XYZ cùng tỉ lệ) khi >1 đồ.

### Cách chặn
Trong GizmoController, khi SelectedActor là Pivot và mode = Scale:
- Ưu tiên: dùng setting của RuntimeTransformer để khóa về uniform scale axis (nếu plugin expose).
- Nếu plugin không cho: ép trong ApplyTransformToChildren — lấy trung bình 3 trục scale của `currentPivotT` làm scale uniform trước khi Compose.

**Ghi DEVIATIONS.md nếu áp dụng Plan B.**

---

## 11. Thứ tự thực thi (đã sửa GAP 2 — regression test lên sớm)

1. Thêm 2 biến mới vào BP_PivotActor (Mục 2)
2. Viết lại RefreshOffsets (Mục 3) **VÀ** ApplyTransformToChildren (Mục 4) — cùng lúc, chưa compile giữa chừng
3. Sửa SpawnOrUpdatePivot: thêm reset rotation/scale (Mục 7)
4. Compile → **TEST CASE 0 (Move-only regression) + CASE 1 (verify Compose order)** — nếu Move-only vỡ hoặc đồ tự nhảy, DỪNG và sửa trước khi đi tiếp
5. Thêm detection drag-start trong GizmoController (Mục 5)
6. Thêm CaptureSnapshot sau release (Mục 6)
7. Test case 2-4 (Rotate + uniform Scale)
8. Test case 5 (non-uniform) — nếu shear → Plan B (Mục 10)
9. Test case 6-8 (kết hợp + Undo + selection mới)
10. Cập nhật doc + DEVIATIONS

---

## 12. Rollback nếu fail

Nếu sau 3 lần thử vẫn shear/sai nghiêm trọng:
- Giữ Move-only multi-select (đã shipped)
- Rotate/Scale: chỉ cho single-select (như cũ, không qua Pivot)
- Multi Rotate/Scale: dời sang phiên bản sau, hoặc Plan B (uniform-only)
- Ghi rõ DEVIATIONS.md

Move-only multi-select đã đủ giá trị để ship. Đừng hy sinh sự ổn định vì Rotate/Scale.
