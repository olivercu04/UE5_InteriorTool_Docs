# Combo C5 — Folder Management Plan
**Phiên bản:** 1.0 | **Tạo:** 30/06/2026

> File này ghi kế hoạch và thứ tự thực thi các sub-task C5 (Folder Management) trong Sprint 5.
> Xem `Combo_Execution.md` để biết chi tiết node-flow từng task.

---

## 1. TỔNG QUAN C5

C5 mở rộng từ "browse folder tree" thành full folder management:
- C5.0 — Tree + Filter (browse-only) ✅ DONE 26/06
- C5.1 — C++ 3 helper (UpdateComboFolder/RenameFolderPrefix/ClearFolderPrefix) ✅ DONE 25/06
- C5.2 — Inline Rename Folder (WBP_EditableLabel) ✅ DONE 27/06
- C5.4 — Move Folder (WBP_MoveToFolderDialog + WBP_MoveFolderRow) ✅ DONE 30/06
- Tiếp theo: xem mục 2

---

## 2. THỨ TỰ THỰC THI (cập nhật 30/06/2026 — map đúng theo thực thi)

| # | Tên task (thực thi) | Tương đương plan gốc | Trạng thái |
|---|---|---|---|
| 1 | C++ 3 helper (UpdateComboFolder/RenameFolderPrefix/ClearFolderPrefix) | C5.1 gốc | ✅ DONE |
| 2 | Tree + Filter (browse-only) | C5.0 gốc | ✅ DONE |
| 3 | WBP_LibraryContextMenu | — (hạ tầng chung) | ✅ DONE |
| 4 | Inline Rename Folder (WBP_EditableLabel) | "Rename folder" gốc | ✅ DONE (27/06) |
| 5 | Move Folder (WBP_MoveToFolderDialog + WBP_MoveFolderRow) | "Move folder" gốc | ✅ DONE (30/06) |
| 6 | Chip highlight on selection (Issue 2 từ C5.0) | — (polish, ngoài plan gốc) | 🔲 KẾ TIẾP |
| 7 | Move Combo (right-click card → "Chuyển vào folder…") | "Move combo" gốc | 🔲 chờ (tái dùng WBP_MoveToFolderDialog) |
| 8 | Tạo folder mới (NewFolder action trong context menu) | "Tạo folder mới" gốc, nhưng đổi route: context menu riêng thay vì nhánh trong dialog move | 🔲 chờ |
| 9 | Xóa folder (WBP_ConfirmDialog mới + ClearFolderPrefix) | "Xóa folder" gốc | 🔲 chờ |
| 10 | ChipTag right-click + embed WBP_EditableLabel | — (ngoài plan gốc, phát sinh từ C5.0) | 🔲 chờ (nặng nhất, để cuối) |

→ Sau #10: C5 HOÀN TẤT → C6/C7 (defer) hoặc WBP_Toast → C9.

**Lý do reorder (#7 lên trước #8/#9, 30/06/2026):** Move Combo tái dùng gần 100%
`WBP_MoveToFolderDialog` vừa build cho Move Folder (chỉ khác: build list không cần
loại con cháu vì combo không có khái niệm con; gọi `UpdateComboFolder(ComboID, path)`
C++ thay vì `RenameFolderPrefix`). Làm ngay trong khi pattern còn nóng nhanh hơn để
nguội rồi quay lại. Tạo folder mới (#8) nhẹ nhất, đẩy sau Move Combo. Xóa folder (#9)
cần widget mới (`WBP_ConfirmDialog`), độ phức tạp ngang Move Folder.

**Ghi chú về numbering lệch:** Numbering thực thi đã LỆCH so với numbering gốc trong plan
ngay từ đầu (C5.2 thực thi = "Inline Rename Folder", không phải "Move Combo" như ghi ban đầu;
C5.4 thực thi = "Move Folder", không phải "Rename folder"). Bảng trên là map chính xác
cuối cùng — dùng thay cho bảng cũ, không đối chiếu ngược lại số gốc nữa.

---

## 3. BUG VÀ DEVIATION ĐÃ GHI NHẬN

- **D-C5.4-1:** Array_Append nối ngược TargetArray/SourceArray trong CollectFolderTargets — xem DEVIATIONS.md
- **D-C5.4-2:** Dead-end thiếu merge ở nhánh True trong HandleMoveFolderConfirmed — xem DEVIATIONS.md

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 30/06/2026 | Khởi tạo — C5.4 DONE, reorder backlog, section 2 cập nhật |
