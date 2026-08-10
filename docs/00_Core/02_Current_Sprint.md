# Current Sprint — Sprint 5: Combo Mesh (C11 Export/Import + P4-early)
**Cập nhật:** 10/08/2026 — Save As/Save đè (T1-T5) DONE 08/08/2026, P4-early DONE, C11 DONE
(chi tiết → `PROGRESS.md`). Tiếp theo: **C10 (Regression full)**.

---

## Đang chạy: P4-early → C11 (Export/Import combo)

Nguồn duy nhất: `Plans/DELTA_10-08-2026_C11_P4early.md` (task card đầy đủ) +
`Plans/Post_C5_Execution_Plan_v1.md` mục C11/G1.5.1 (đã patch 10/08).

| # | Nhiệm vụ | Đụng gì | Định nghĩa XONG | Trạng thái |
|---|---|---|---|---|
| **P4-early** | Dời `GetCombosDir()` sang `%LOCALAPPDATA%/InteriorFOFFTool/Combos` (combo sống qua update app đóng gói) | `ComboSerializer.cpp` — CHỈ thân hàm `GetCombosDir()` | Migrate tay xong, tab Combo hiện đủ combo/folder/thumbnail cũ qua đường mới | ✅ DONE (verify PASS 3/3 ô: số lượng combo, folder tree, thumbnail) |
| **C11** | Export/Import combo qua thư mục `Exports/` (quét-thư-mục, KHÔNG dialog) | `ComboSerializer.cpp` (+3 hàm mới) + BP context menu ComboCard + `BTN_ImportCombo` | 6/7 test case PASS (xem task card) | ✅ DONE 10/08/2026 — C11.1 (C++, 4 hàm) + C11.2 (Export, 3/3 test) + C11.3 (Import, 4/4 test) đều PASS. Export/Import combo qua thư mục `Exports/` (quét-thư-mục, không dialog — QĐ2/QĐ3). Tiếp theo: **C10 (Regression full)**. |

Thứ tự: **P4-early → C11 → C10 (Regression full) → Gate 2 (packaged build)**.

---

## Nguyên tắc đọc file này
File chỉ chứa sprint/task ĐANG chạy. Việc đã DONE → chuyển về `PROGRESS.md`. Không tích lũy
lịch sử ở đây.
