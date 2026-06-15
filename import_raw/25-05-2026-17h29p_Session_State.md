
## REPLACE MODE UX (25/05/2026 — 17:29 ICT)

### Tính năng hoàn thành
- Inventory giữ mở sau khi replace mesh → thay vì Remove from Parent
- SET MeshToReplace = SelectedFurnitureActor sau mỗi replace (không reset None)
- 3 trigger thoát Replace mode:
  - Trigger 1: Deselect/click vùng trống → ExitReplaceMode
  - Trigger 2: BTN_Replace toggle (click lần 2 → OFF)
  - Trigger 3: Select mesh khác → update MeshToReplace + navigate folder

### Functions mới trong WBP_FurnitureInventory
- EnterReplaceMode: SET bIsReplaceMode=True + Regenerate All Entries
- ExitReplaceMode: SET bIsReplaceMode=False + Regenerate All Entries
- RefreshCardReplaceMode: chỉ Regenerate All Entries (gọi từ bên ngoài sau FilterByFolderPathWithUI)

### Key learning
- EnterReplaceMode từ DetailPopup KHÔNG work vì FilterByFolderPathWithUI clear cards sau đó → dùng SET trực tiếp + RefreshCardReplaceMode sau FilterByFolderPathWithUI
- Regenerate All Entries phải chạy SAU populate (FilterByFolderPathWithUI) mới có tác dụng
