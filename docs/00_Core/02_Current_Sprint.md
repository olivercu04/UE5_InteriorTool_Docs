# Current Sprint — Sprint 5: Combo Mesh (Save As / Save đè combo)
**Cập nhật:** 04/08/2026 — T1 DONE, T2 DONE (test PASS 6/6), T3 đang mở.

---

## Đang chạy: Save As / Save đè combo

Nguồn duy nhất: `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md`.

| # | Nhiệm vụ | Đụng gì | Định nghĩa XONG | Trạng thái |
|---|---|---|---|---|
| **T1** | `ResolveActiveComboForSave()` — đọc trạng thái | `BP_FurnitureInputManager` (2 Function mới) | Print đúng 6 case, chưa có UI | ✅ DONE (test PASS 6/6) |
| **T2** | Guard edit-scope cho re-route replace (bug 2.9) | `WBP_FurnitureInventory.OnMeshSelected` | Replace mesh trong combo → inventory ở nguyên tab mesh | ✅ DONE (test PASS 6/6) |
| **T3** | 2 nút + trạng thái xám + tooltip + auto-fill | `WBP_SaveComboDialog` + `WBP_FurnitureInventory` + `BP_FurnitureInputManager` (scope rộng hơn — xem mục 7b plan) | Bấm nút chỉ Print, chưa ghi file | 🔄 Đang mở (task card 04/08) |
| **T4** | Ghi đè thật + xác nhận + chụp lại thumbnail | C++ `ComboSerializer` + `BP_ComboManager` | File `.json` đổi nội dung, `comboId` giữ nguyên | ⏳ Chưa mở |
| **T5** | Regression + docs | — | Save As vẫn sinh ID mới; combo cũ load được; docs cập nhật | ⏳ Chưa mở |

Sau Save As/Save đè: **C11 (Export/Import) → C10 (Regression full) → Gate 2 (packaged build)**.

---

## Nguyên tắc đọc file này
File chỉ chứa sprint/task ĐANG chạy. Việc đã DONE → chuyển về `PROGRESS.md`. Không tích lũy
lịch sử ở đây.
