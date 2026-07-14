# Current Sprint — Sprint 5: Combo Mesh (P1 — Combo Thumbnail)
**Cập nhật:** 14/07/2026 — P1 Gate G1 DONE (LoadComboThumbnail hoàn chỉnh), chuyển sang G2

---

## Đang chạy: P1 — Combo Thumbnail (Thumbnail System C++)

Gate G0-R ✅ DONE (14/07/2026): one-shot capture (G0 gốc) bị loại bỏ do ảnh xám phẳng (Lumen GI/TAA/auto-exposure chưa hội tụ đủ frame). Đổi kiến trúc sang `BeginComboCapture`/`FinishComboCapture` + Custom Event dùng `Delay` latent. Chi tiết: `docs/00_Core/DEVIATIONS.md` [ARCH] 14/07/2026, `docs/00_Core/01_Session_State.md` mục P1.

**Đang làm: Gate G2** — auto-fit khung hình theo bounding box combo (FitRatio đã có param sẵn từ đầu, chưa dùng) + ẩn gizmo/outline lúc capture (HiddenActors + tắt bRenderCustomDepth tạm thời) + tinh chỉnh sharpen/PostProcess.

Checklist đầy đủ P1.G0-R → G5: xem `docs/00_Core/PROGRESS.md`.

---

## Sau P1 (chưa bắt đầu)
```
P1.G3 — cache ảnh trong BP_ComboManager (node Map chưa xác nhận, cần cuhoang confirm)
P1.G4 — wire full vào Save/Load flow + 6 test case end-to-end + chốt số Delay warm-up chính xác
P1.G5 — regression VRAM (stat rhi 4 mốc)

C9 — Replace (CalculateCenter trước destroy → SpawnComboByID → auto-rollback)
K1 — WBP_Toast global feedback widget
K3 — fix bAddToRecent bug trong SpawnFurnitureCopy
```
Xem đầy đủ roadmap Giai đoạn 1/2/3 tại `docs/00_Core/01_Session_State.md` (mục Roadmap v3.3).

---

## Nguyên tắc đọc file này
File chỉ chứa sprint/task ĐANG chạy. Việc đã DONE → chuyển về `PROGRESS.md` (tiến độ tổng) hoặc file Sprint tương ứng trong `Sprints/`. Không tích lũy lịch sử ở đây.
