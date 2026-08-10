# Current Sprint — Sprint 5: Combo Mesh (Save As / Save đè combo)
**Cập nhật:** 08/08/2026 — Save As/Save đè — **DONE (T1-T5 xong 08/08/2026)**. Task tiếp theo: **C11**.

---

## Đang chạy: Save As / Save đè combo

Nguồn duy nhất: `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md`.

| # | Nhiệm vụ | Đụng gì | Định nghĩa XONG | Trạng thái |
|---|---|---|---|---|
| **T1** | `ResolveActiveComboForSave()` — đọc trạng thái | `BP_FurnitureInputManager` (2 Function mới) | Print đúng 6 case, chưa có UI | ✅ DONE (test PASS 6/6) |
| **T2** | Guard edit-scope cho re-route replace (bug 2.9) | `WBP_FurnitureInventory.OnMeshSelected` | Replace mesh trong combo → inventory ở nguyên tab mesh | ✅ DONE (test PASS 6/6) |
| **T3** | 2 nút + trạng thái xám + tooltip + auto-fill | `WBP_SaveComboDialog` + `WBP_FurnitureInventory` + `BP_FurnitureInputManager` (scope rộng hơn — xem mục 7c plan) | Bấm nút chỉ Print, chưa ghi file | ✅ DONE (test PASS 6/6, 07/08 — chi tiết đã chuyển về `PROGRESS.md`) |
| **T4** | Ghi đè thật + xác nhận + chụp lại thumbnail | `BP_ComboManager.SaveComboFromSelection` + `WBP_SaveComboDialog.BTN_Overwrite` + `WBP_FurnitureInventory` | File `.json` đổi nội dung, `comboId` giữ nguyên | ✅ DONE (test PASS 6/6, 07/08) |
| **T5** | Regression + docs | KHÔNG viết node mới (regression + doc) + fix D1 (Tags ref) + D2 (Category hardcode) | Save As vẫn sinh ID mới; combo cũ load được; docs cập nhật | ✅ DONE (Khối A+B PASS toàn bộ, 08/08) |

T4.5 (auto-group scene sau ghi đè S8 — gộp mesh rời + group combo thành cụm chọn-1-lần) —
backlog riêng, **CHƯA mở**, xem `Bugs/Open_Bugs.md` mục `Task-T4.5-AutoGroupAfterOverwrite`.

Sau Save As/Save đè: **C11 (Export/Import) → C10 (Regression full) → Gate 2 (packaged build)**.

---

## Nguyên tắc đọc file này
File chỉ chứa sprint/task ĐANG chạy. Việc đã DONE → chuyển về `PROGRESS.md`. Không tích lũy
lịch sử ở đây.
