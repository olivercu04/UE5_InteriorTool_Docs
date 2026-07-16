# Current Sprint — Sprint 5: Combo Mesh (P1 — Combo Thumbnail)
**Cập nhật:** 15/07/2026 — P1 Gate G2+G3+G4 DONE, chuyển sang G5

---

## Đang chạy: P1 — Combo Thumbnail (Thumbnail System C++)

Gate G0-R → G4 ✅ DONE. Chi tiết đầy đủ (kiến trúc capture, 3 bug dead-end phát hiện+fix,
1 bug dead-end còn mở): xem `01_Session_State.md` mục P1.

**Đang làm: Gate G5** — regression VRAM. Console `stat rhi`, ghi Render target memory +
Texture memory tại 4 mốc (baseline / sau lưu 5 combo / sau thao tác folder / sau save-load
scene). Xem chi tiết đầy đủ: `docs/Plans/P1_ComboThumbnail_Execution.md` mục G5.

**Trước G5 — 2 việc cần làm:**
1. Fix bug dead-end ComboManagerRef trong WBP_FurnitureInventory.LoadComboLibrary (xem
   Session_State mục P1, "bug CÒN MỞ").
2. Xóa chuỗi debug phím T/Y trong BP_ComboManager (Enable Input, bDebugTestThumb,
   Cmb_CaptureHandle test-only wiring, IMG_Debug nếu còn).

---

## Sau P1 (chưa bắt đầu)
C9 — Replace (CalculateCenter trước destroy → SpawnComboByID → auto-rollback)
K1 — WBP_Toast global feedback widget
K3 — fix bAddToRecent bug trong SpawnFurnitureCopy
[MỚI] Delete Combo — chưa từng implement, cần task riêng (BTN_DeleteCombo có sẵn layout,
chưa bind handler + chưa gọi DeleteThumbnail/InvalidateThumbnail)
[BACKLOG] Fable review — exposure bug capture (ảnh tối ở cảnh backlit), xem note deferred
trong Session_State mục P1

---

## Nguyên tắc đọc file này
File chỉ chứa sprint/task ĐANG chạy. Việc đã DONE → chuyển về `PROGRESS.md`. Không tích lũy
lịch sử ở đây.
