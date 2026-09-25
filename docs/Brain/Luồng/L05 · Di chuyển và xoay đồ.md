# L05 · Di chuyển và xoay đồ

> **Hành trình:** ← [[L04 · Chọn đồ|L04 Chọn đồ]] · **L05** · [[L06 · Nhóm đồ và sửa nhóm|L06 Nhóm đồ và sửa nhóm]] →
> ↑ [[Bản đồ não]] · trên [[1 · Một buổi dựng phòng.canvas|Tổng quát 1]] là bước ④ · sơ đồ nhúng từ [[Architecture_Map]] Phần 5 (nguồn duy nhất — sửa ở đó). Mũi tên **liền** = ✓K2 · **đứt** = theo doc · `?` = chưa rõ.

**Một câu:** nhấn lên trục gizmo thì InputManager **nhường lượt** cho GizmoController; khi giữ chuột, **Event Tick của gizmo tự dời đồ mỗi frame**; thả chuột → ghi sổ `Move` / `Rotate` / `Scale` rồi mới hạ cờ kéo. Phím mũi tên là đường thứ hai, không qua gizmo.

## Người dùng làm gì → thấy gì
| Làm | Thấy | Sổ lịch sử |
|---|---|---|
| Bấm Move / Rotate / Scale (hoặc W / E / R) | Gizmo đổi kiểu | — |
| Nhấn giữ 1 trục, kéo | Đồ chạy theo chuột, bám lưới snap | — |
| Thả chuột | Đồ đứng yên ở chỗ mới | 1 mốc `Move` (hoặc `Rotate` / `Scale`) |
| Bấm phím mũi tên (giữ = lặp mỗi 0.1s) | Đồ nhích 1 bước lưới theo hướng nhìn | 1 mốc `Nudge` sau 0.5s ngừng bấm |

## Chạy thế nào — kéo gizmo
![[Architecture_Map#5f — Kéo gizmo Move (1 món · nhiều món qua Pivot)]]
> 🗺️ Bản làn bơi: [[5f - Kéo gizmo Move (1 món · nhiều món qua Pivot).canvas|canvas 5f]]

## Chạy thế nào — phím mũi tên
![[Architecture_Map#5k — Nhích đồ bằng phím mũi tên (Nudge)]]
> 🗺️ Bản làn bơi: [[5k - Nhích đồ bằng phím mũi tên (Nudge).canvas|canvas 5k]]

## Hình dung
```
1 món :  chuột ──kéo──► Gizmo ──Set Actor Location──► Ghế
≥2 món:  chuột ──kéo──► Gizmo ──Set Actor Location──► Pivot (vô hình, tâm nhóm)
                                                       │ Tick: ApplyTransformToChildren
                                                       ▼
                                             Ghế A · Ghế B · Bàn (mỗi món = vị trí tương đối × pivot mới)
```
Pivot giống **cái khay**: lúc bắt đầu kéo, ghi lại mỗi món đặt ở đâu trên khay (`RefreshOffsets`); sau đó chỉ cần dời khay, món nào cũng tự về đúng chỗ.

## Dễ hiểu sai
- **Nhấn lên trục mà không bị bỏ chọn / quét khung** — `Mouse Left Pressed` dừng ở Step 3 (`bIsDraggingGizmo == True`) trước khi bật cờ quét khung.
- **Chọn nhiều món thì gizmo kéo Pivot**, Pivot mới kéo từng món (công thức tuyệt đối mỗi frame → không cộng dồn sai số).
- **Thứ tự lúc thả là luật cứng:** `CaptureSnapshot` TRƯỚC, `SET bIsDraggingGizmo = False` SAU (✓K2 24/09).
- **Ctrl+Z giữa lúc kéo** từng làm kẹt cờ kéo + khoá xoay camera (tool "đơ") — **đã sửa 25/09**: trượt lớp chặn 1–2 mà đang kéo thì vẫn dọn cờ, không ghi sổ. Và từ 25/09 **Ctrl+Z / Ctrl+Shift+Z bị bỏ qua khi đang giữ chuột kéo gizmo** (`IsGizmoDragging` trong InputManager) — trước đó Undo chen giữa cú kéo làm gizmo kéo tiếp món mới sinh lại và ghi mốc "Move" thừa, mất Redo. Lỗi thứ 2 (chế độ Scale bị ghi mốc tên "Move" do 2 Branch cùng so `NewEnumerator2`) **đã sửa 25/09**, PIE PASS — [[BP_GizmoController]] v1.3.
- **Pivot không vào sổ** (tag `FurniturePivot`) — sổ chỉ ghi vị trí mới của từng món.
- **Nhích phím: hướng theo camera làm tròn 90°** và theo mặt đặt của món chính (đồ trên tường: lên / xuống = trục Z). `SnapStep = 0` thì Tick đọc phím liên tục, dừng ngay khi thả phím.
- Rotate / Scale dùng chung khung với Move — khác nhánh Tick và tên entry.

## Đường ngược (6A)
Ctrl+Z → entry `Move` / `Nudge` là Snapshot → dựng lại cảnh trước khi kéo ([[L13 · Hoàn tác và làm lại|L13]]). Nút reset xoay: menu chuột phải "Đặt lại xoay" ([[L07 · Menu chuột phải và phím tắt|L07]]).

## Còn mở
- `WBP_MeshControls` lấy tham chiếu GizmoController từ đâu (`?`) · `bIsDraggingGizmo` ở Step 3 thật ra là biến của ai (`?`) · thứ tự 2 handler lúc thả (`?`).
- K2 nên xin: InputManager `Mouse Left Pressed` Step 0–3 + `Mouse Left Released (gizmo)` · Gizmo `Event Tick` nhánh Move · `BTN_Move` OnClicked.

## Nhảy tới code
| Hàm | Doc |
|---|---|
| Pattern `BTN_Move` / `BTN_Rotate` / `BTN_Scale` · `ET_SnapStep` | [[WBP_MeshControls]] |
| `Mouse Left Pressed` · `Mouse Left Released (gizmo)` · `SpawnOrUpdatePivot` · `UpdateGizmo` · B1 Nudge | [[BP_FurnitureInputManager]] |
| `ActivateGizmo` · `DeactivateGizmo` · `OnMousePressed` · `OnMouseReleased` · Event Tick | [[BP_GizmoController]] |
| `RefreshOffsets` · `ApplyTransformToChildren` | [[BP_PivotActor]] |
| `NudgeMesh` · `CaptureNudgeSnapshot` · Event Tick free mode | [[Nudge_Flow]] |
