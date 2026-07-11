# Current Sprint — Sprint 5: Combo Mesh (C5.8 Folder Tree Picker Unify)
**Cập nhật:** 11/07/2026 — Task Card #2 Part B, Giai đoạn 1 DONE

---

## Đang chạy: C5.8 — Folder Tree Picker Unify

Gộp lõi data+component cho `WBP_MoveToFolderDialog` + `WBP_SaveComboDialog`
(tree picker: guide line, search, expand/collapse, inline create), thay
`WBP_MoveFolderRow` + folder-field cũ của Save.

Plan đầy đủ: `docs/Sprints/Sprint5/C5.8_FolderTreePicker_Unify_Plan.md`

### Task Card #1 — Data Layer ✅ DONE (08/07)
Rename `S_FolderTargetEntry`→`S_FolderTreeNode` (+4 field), `BuildFolderTreeRecursive`,
`GetFilteredChildren`, `BuildComboFolderTreeNodes`. Test Print PASS data thật.

### Task Card #2 — UI component (`WBP_FolderTreePicker` + `WBP_FolderPickerRow`)
Kế hoạch chi tiết: `docs/Sprints/Sprint5/C5.8_TaskCard2_FixPlan_11jul2026.md`

| Giai đoạn | Nội dung | Trạng thái |
|---|---|---|
| 0 | Phân loại bug #2 (click ▶ không hiện gì) | ✅ DONE (11/07) |
| 1 | Fix bug (`SetNode` thiếu `SET RowNode`, `BTN_Arrow` visibility) + test mục 1-5 | ✅ DONE (11/07) |
| 2 | Search — `PathMatchesQuery`, `BuildSearchOverride`, wire `SB_SearchFolder`, `SetSearchHighlight`, test mục 6-9 | ⏳ TIẾP THEO |
| 3 | Select — test mục 10 | ⏳ chưa tới |
| 4 | Chốt sổ — DEVIATIONS, delta note, comprehension check (2 câu hỏi) | ⏳ chưa tới |

**Sau Task Card #2:** 2d (rename host) → wire Move (§7.3 plan) → wire Save + Create Folder (§6/§7.4) — thứ tự đã khoá, không đảo.

---

## Kế tiếp sau C5.8 (chưa bắt đầu)
```
C9 — Replace (CalculateCenter trước destroy → SpawnComboByID → auto-rollback)
K1 — WBP_Toast global feedback widget
K3 — fix bAddToRecent bug trong SpawnFurnitureCopy
```
Xem đầy đủ roadmap Giai đoạn 2/3 tại `docs/00_Core/01_Session_State.md` (mục Roadmap v3.3).

---

## Nguyên tắc đọc file này
File chỉ chứa sprint/task ĐANG chạy. Việc đã DONE → chuyển về `PROGRESS.md` (tiến độ tổng) hoặc file Sprint tương ứng trong `Sprints/`. Không tích lũy lịch sử ở đây.
