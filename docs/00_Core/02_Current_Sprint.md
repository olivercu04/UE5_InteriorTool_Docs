# Current Sprint — Sprint 5: Combo Mesh (Save As / Save đè combo)
**Cập nhật:** 30/07/2026 — C9 (Replace Combo) DONE, chuyển sang Save As/Save đè.

---

## Đang chạy: Save As / Save đè combo

UX CHƯA CHỐT — bàn phương án trước khi lên task card thực thi. Khung sơ bộ đã có ở
`Sprints/Sprint5/Combo_Execution.md` mục "C9.5". Tái dùng `ResolveSelectedComboRoot()`
(viết trong C9, `BP_FurnitureInputManager`).

Bối cảnh cần giải quyết: `Note-DuplicateComboID` (`Bugs/Open_Bugs.md`) — copy tay file `.json`
không sinh `comboId` mới → Save As phải luôn sinh `comboId` MỚI (GUID), Save đè giữ nguyên.

Sau Save As/Save đè: **C11 (Export/Import) → C10 (Regression full) → Gate 2 (packaged build)**.

---

## Nguyên tắc đọc file này
File chỉ chứa sprint/task ĐANG chạy. Việc đã DONE → chuyển về `PROGRESS.md`. Không tích lũy
lịch sử ở đây.
