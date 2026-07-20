# Current Sprint — Sprint 5: Combo Mesh (P2 — Studio Thumbnail)
**Cập nhật:** 20/07/2026 — P2 Gate D TẠM DỪNG: Rim Light + VRAM fix + Source Size=500 DONE,
sweep 3/5 PASS, 2 bug kiến trúc mới OPEN (dome curvature + Ceiling ground-align) — chờ
Fable/Opus quyết trước khi tiếp tục. Xem Session_State mục P2 + `DEVIATIONS.md` mục
"P2 — 20/07/2026".

---

## Đang chạy: P2 Gate D — bóng + sweep hình dáng (TẠM DỪNG)

Rim Light (3-point lighting) DONE, VRAM/GPU crash fix (EndPlay `BP_ComboManager`) DONE, Source
Size Key=500 chốt. Sweep 5 loại combo: 3/5 PASS (Nhỏ/To/Tường), 2/5 FAIL:
- Dome cong (sphere) nuốt chân đồ footprint rộng — combo To (sofa) lộ nhẹ, combo Dẹt (thảm)
  FAIL nặng.
- Combo "Cao" (surfaceType Ceiling) dính lỗi ground-align giống case Tường (H1) — chưa từng ghi
  trong plan gốc.

**Chờ Fable/Opus quyết kiến trúc** (đảo ngược 1 phần quyết định Gate B — bỏ sàn phẳng) trước khi
tiếp tục sweep. Xem `DEVIATIONS.md` mục "P2 — 20/07/2026", `Bugs/Open_Bugs.md`.

Ứng viên sau P2 (xem PROGRESS.md để chọn):
- Fix bug dead-end ComboManagerRef backlog (P1.G4) — [ĐÃ FIX 15/07, xem log trước]
- Dọn debug chain P1 (phím T/Y...) — [ĐÃ DỌN 15/07, xem log trước]
- C9 — Replace combo
- K1 — WBP_Toast
- K3 — fix bAddToRecent bug
- Delete Combo — task mới, chưa có plan

---

## Nguyên tắc đọc file này
File chỉ chứa sprint/task ĐANG chạy. Việc đã DONE → chuyển về `PROGRESS.md`. Không tích lũy
lịch sử ở đây.
