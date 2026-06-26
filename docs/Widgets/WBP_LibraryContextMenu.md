# WBP_LibraryContextMenu
**Phiên bản:** 1.0 | **Tạo:** 26/06/2026 | **Clone từ:** WBP_ContextMenu

---

## Tổng quan

Context menu cho Combo Library — hiện khi right-click WBP_TreeNode (folder) hoặc WBP_ComboCard (combo, C5.4+).
Dùng lại toàn bộ cơ chế đóng/mở của WBP_ContextMenu: `Btn_Background` full-screen alpha=0 + `ShowAt` + `Hide`.

---

## Layout (Canvas Panel)

```
Canvas Panel
  ├── Btn_Background  ← index 0 (Z thấp, full screen, alpha=0, Transparent)
  └── Border_Menu     ← index 1 (Z cao, nền tối opacity ~0.85)
      └── MenuList (Vertical Box)
          └── [WBP_ContextMenuItem items thêm qua AddMenuItem()]
```

> ⚠️ **CRITICAL — Z-order:** `Btn_Background` PHẢI là **index 0** trong Canvas Panel. Nếu index cao hơn `Border_Menu` → `Btn_Background` render trên menu → click vào nút menu KHÔNG được. Bug này từng gây "click ngoài không đóng menu" (26/06). UMG render từ index 0 lên → index cao hơn nhận click trước (D12).

---

## Variables

| Tên | Kiểu | Ghi chú |
|---|---|---|
| `TargetFolderPath` | String | Path folder đang right-click (MenuMode="Folder") |
| `TargetComboID` | String | ComboID đang right-click (MenuMode="Combo", C5.4+) |
| `MenuMode` | String | `"Folder"` (default) / `"Combo"` — điều khiển dispatchers bind ở caller |

---

## Event Dispatchers

```
OnRequestRenameFolder(FolderPath : String)   ← C5.2
OnRequestMoveFolder(FolderPath : String)     ← C5.4
OnRequestDeleteFolder(FolderPath : String)   ← C5.5
OnRequestMoveCombo(ComboID : String)         ← C5.4
```

---

## Functions / Events (tái dùng từ WBP_ContextMenu)

### AddMenuItem(Label : String, Shortcut : String) → WBP_ContextMenuItem
```
Create Widget(WBP_ContextMenuItem) → Item
SET Item.LabelText = Label
SET Item.ShortcutText = Shortcut
Add Child(MenuList, Item)
Return Item
```

### ShowAt(ScreenPos : Vector2D)
```
Add to Viewport(ZOrder=99999)
Set Position In Viewport(ScreenPos, bRemoveDPIScale=False)
```

### Hide
```
Get Player Controller → Set Input Mode Game And UI
Remove from Parent
```

### Btn_Background.OnClicked
```
→ Hide
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 26/06/2026 | Khởi tạo — clone WBP_ContextMenu. 3 variables (TargetFolderPath/TargetComboID/MenuMode) + 4 dispatchers. Btn_Background Z-order fix (index 0). Test: right-click folder → menu hiện; click ngoài → đóng; sentinel guard PASS. |
