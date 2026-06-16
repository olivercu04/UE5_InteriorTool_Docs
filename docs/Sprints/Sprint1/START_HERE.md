# 🚀 SPRINT 1 KICKOFF — Đọc đầu tiên (cho session Sonnet 4.6)
**Chuẩn bị:** 02/06/2026 | **Bắt đầu:** Phase 2 — MultiSelect Sprint 1

---

## DÀNH CHO AI: ĐỌC THEO THỨ TỰ NÀY TRƯỚC KHI LÀM BẤT KỲ GÌ

1. **09_AI_Implementation_Rules.md** ← QUAN TRỌNG NHẤT (7 quy tắc + L1-L10 + bảng node)
2. **10_Execution_Discipline.md** ← chống đi lạc, chống bỏ cuộc
3. **00_Master_Plan.md** ← 8 quyết định kiến trúc đã chốt
4. **04_Sprint_Details.md** (phần Sprint 1) ← 15 task cụ thể
5. **05_Data_Structures.md** ← struct/variable/signature chính xác
6. **08_Performance_Optimization.md** ← ràng buộc máy yếu

Đọc xong, XÁC NHẬN với cuhoang là đã hiểu rồi mới bắt đầu.

---

## TRẠNG THÁI DỰ ÁN (tính đến 02/06/2026)

- Đã integrate toàn bộ furniture tool vào **master project** (không còn working copy riêng)
- Phase 0 (Material Copy/Paste single-slot) đã XONG
- C++ đã thành plugin FurnitureToolkit
- Đang bắt đầu **Phase 2 — MultiSelect** (plan_v3 Sprint 1)
- Test bằng **Alt+P (Standalone)** do master nặng, PIE dễ GPU crash

---

## ⚠️ TRƯỚC KHI VIẾT CODE — BẮT BUỘC

**BACKUP project** (copy thư mục, ghi ngày). Sprint 1 đụng 3 file lõi:
- BP_FurnitureInputManager (refactor Mouse Left Pressed — S1.T7 khó nhất)
- BP_GizmoController
- BP_UndoManager

Nếu hỏng mà không backup → mất công integration cả ngày 02/06.

---

## CÁCH LÀM SPRINT 1 — MOVE-FIRST

**KHÔNG làm tuần tự T1→T15.** Làm vertical slice trước:

### Vertical Slice (ngày 1) — validate rủi ro lớn nhất
```
Mục tiêu tối thiểu: chọn 2 đồ (Ctrl+Click) → MOVE qua Pivot Actor → Undo

Chạm tối thiểu vào: S1.T1 (variables) + S1.T3 (BP_PivotActor MOVE-only)
                    + S1.T5 (helper select) + S1.T7 (Mouse Pressed tối thiểu)

VALIDATE 2 rủi ro:
  - Pivot Actor MOVE hoạt động? (R2)
  - Gizmo có bắt được Pivot không, hay bị disable collision? (R5b)

→ Nếu OK: tiếp tục hoàn thiện T1-T14
→ Nếu Pivot/gizmo hỏng: chuyển Plan B (06_Risk_Mitigation.md) NGAY
```

### Sau vertical slice
- Hoàn thiện T1-T14 (Move + multi-select đầy đủ)
- **Rotate/Scale = S1.T15 LÀM CUỐI** (toán Pivot khó, dễ shear — đừng để block sprint)
- Move-only multi-select đã đủ giá trị demo

---

## KỶ LUẬT (file 10)

- Ghi **DEVIATIONS.md** mỗi khi làm khác plan về logic/scope
- Tick **PROGRESS.md** mỗi task xong
- Bug fail 3 lần → STOP, chọn Plan B / thu hẹp / gác lại
- Plan có thể sai vài chỗ — bình thường. Đừng cố làm theo plan sai vì tiếc công.

---

## NHẮC AI VỀ PHONG CÁCH (cuhoang)

- **Tiếng Việt thuần.** Giữ tên node/biến/class tiếng Anh.
- **Hỏi từng bước, confirm rồi mới đi tiếp.** KHÔNG đổ nhiều task 1 lúc. Kết thúc bằng "Làm xong báo tao" + test cụ thể.
- Mô tả node flow bằng lời: `NodeA → [pin] → NodeB`. cuhoang KHÔNG cần screenshot.
- Dùng đúng tên node UE5.5 (bảng trong file 09). KHÔNG hallucinate — không chắc thì nói "tao không chắc, bạn kiểm tra".
- **Verify trước khi phản bác** — cuhoang thường đúng về node UE5 cụ thể. Sai thì thừa nhận, đúng thì bảo vệ có lý lẽ.
- Debug bằng Print String. Ưu tiên máy yếu.

---

## TASK ĐẦU TIÊN (S1.T1 — sau khi đọc + backup)

Thêm variables vào BP_FurnitureInputManager:
```
SelectedActors        : Array of BP_FurnitureActor
PrimarySelectedActor  : BP_FurnitureActor
GizmoPivotActor       : BP_PivotActor (None default)
LastPivotTransform    : Transform
```
Giữ `SelectedFurnitureActor` (deprecated, đồng bộ với Primary — gỡ ở S7.T9).

Chi tiết: 04_Sprint_Details.md → S1.T1.

---

## CONTEXT KỸ THUẬT NHANH (khỏi phải hỏi lại)

- **Selection hiện tại:** single `SelectedFurnitureActor` trong BP_FurnitureInputManager
- **Outline:** Custom Depth Stencil = 255. Multi-select thêm 254 (secondary)
- **Gizmo:** RuntimeTransformer plugin, chỉ làm việc 1 actor → dùng Pivot Actor cho multi
- **Tag:** "FurnitureSpawned" (mesh đã đặt). Thêm "FurniturePivot" (Sprint 1)
- **Snapshot:** S_SceneSnapshot + S_FurniturePlacement. Thêm Version + SelectedMeshIndices
- **Spawn managers:** từ WBP_FOFF_ToolDemo Event Construct (Then 11)
- **KHÔNG** thêm furniture vars vào BP_FoffPlayerController (shared)
