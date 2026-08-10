# Current Sprint — Sprint 5: Combo Mesh (C11 Export/Import + P4-early)
**Cập nhật:** 10/08/2026 — Save As/Save đè (T1-T5) DONE 08/08/2026 (chi tiết → `PROGRESS.md`).
Đang chạy: **P4-early** (lập kế hoạch xong, chưa thực thi) → **C11** (chưa mở, sau P4-early).

---

## Đang chạy: P4-early → C11 (Export/Import combo)

Nguồn duy nhất: `Plans/DELTA_10-08-2026_C11_P4early.md` (task card đầy đủ) +
`Plans/Post_C5_Execution_Plan_v1.md` mục C11/G1.5.1 (đã patch 10/08).

| # | Nhiệm vụ | Đụng gì | Định nghĩa XONG | Trạng thái |
|---|---|---|---|---|
| **P4-early** | Dời `GetCombosDir()` sang `%LOCALAPPDATA%/InteriorFOFFTool/Combos` (combo sống qua update app đóng gói) | `ComboSerializer.cpp` — CHỈ thân hàm `GetCombosDir()` | Migrate tay xong, tab Combo hiện đủ combo/folder/thumbnail cũ qua đường mới | 🔄 Lập kế hoạch xong, CHƯA thực thi |
| **C11** | Export/Import combo qua thư mục `Exports/` (quét-thư-mục, KHÔNG dialog) | `ComboSerializer.cpp` (+3 hàm mới) + BP context menu ComboCard + `BTN_ImportCombo` | 6/7 test case PASS (xem task card) | ⏳ Chưa mở — chạy SAU P4-early PASS |

Thứ tự: **P4-early → C11 → C10 (Regression full) → Gate 2 (packaged build)**.

---

## Nguyên tắc đọc file này
File chỉ chứa sprint/task ĐANG chạy. Việc đã DONE → chuyển về `PROGRESS.md`. Không tích lũy
lịch sử ở đây.
