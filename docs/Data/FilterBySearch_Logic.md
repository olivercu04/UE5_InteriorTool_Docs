# FilterBySearch — Node Flow Reference
**Phiên bản:** 1.3 | **Cập nhật:** 17/06/2026 — Sprint D.T5/D.T6 | WBP_FurnitureInventory

> **v1.3 (Sprint D.T5 + D.T6):** Furniture mode chuyển sang `FilterFurnitureRows` (C++) thay `FilterFurnitureItems`. Input: `DT_FurnitureCatalog` + filters. Output: `AllFilteredFurnitureRows : Array<Name>` → `DisplayPage` (không AddItem trực tiếp). `AllFurnitureItems` class var bị XÓA (Sprint D.T7).

---

## Signature
```
Function: FilterBySearch(SearchText : String, CategoryFilter : Name)
```

---

## Flow đầy đủ

```
FilterBySearch(SearchText, CategoryFilter):

← ĐỌC CurrentCategory (không dùng parameter trực tiếp):
SET CategoryFilter (class var) = GET CurrentCategory
SET CurrentSearchText = SearchText

← Early return nếu search text quá ngắn:
Branch SearchText != "" AND Length(SearchText) < 3:
  T → Return  ← tránh filter khi user chưa gõ đủ

← Branch theo inventory mode:
Branch CurrentInventoryMode == Material:
  T →
    Call PopulateMaterialGrid
    Return

  F →
    ← Furniture mode (v1.3 Sprint D.T5):
    FilterFurnitureRows(
      C++ UFurnitureFilterLibrary,
      DT_FurnitureCatalog,
      SearchText      = CurrentSearchText,
      FolderPath      = CurrentFolderPath,
      CategoryFilter  = CategoryFilter (class var),
      MaxResults      = 200
    ) → AllFilteredFurnitureRows : Array<Name>

    SET CurrentPage = 0
    Call DisplayPage    ← tạo BP_FurnitureItemView per page, AddItem tới CTV_FurnitureCard
```

---

## Nơi gọi FilterBySearch

| Caller | SearchText | CategoryFilter | Ghi chú |
|---|---|---|---|
| FilterByCategory (non-Recent) | CurrentSearchText | CurrentCategory | Sau khi SET CurrentCategory |
| SwitchInventoryMode (False branch) | CurrentSearchText | CurrentCategory | Khi switch về Furniture mode |
| FilterByFolderPath | CurrentSearchText | CurrentCategory | Khi đổi folder |
| BTN_AllCategory OnClicked | CurrentSearchText | "All" | Gọi trực tiếp, không qua FilterByCategory |
| CommonSearchBox OnTextChanged | SearchText mới | CurrentCategory | Debounce 0.3s |
| Event Construct (Then 1) | "" | "All" | Init lần đầu |

---

## Lưu ý quan trọng

### ⚠️ CategoryFilter Parameter vs Class Variable
FilterBySearch **KHÔNG dùng parameter CategoryFilter trực tiếp** để filter.
Thay vào đó, nó đọc từ `CurrentCategory` class variable:

```
SET CategoryFilter (class var) = GET CurrentCategory
```

Điều này có nghĩa: nếu gọi FilterBySearch trực tiếp với parameter "Sofa",
nhưng CurrentCategory vẫn là "All" → sẽ filter theo "All", không phải "Sofa".

→ **Luôn đảm bảo CurrentCategory được SET trước khi gọi FilterBySearch.**
→ **"Recent" được xử lý trong FilterByCategory**, không ở FilterBySearch — tránh vấn đề này.

### ⚠️ Material mode → PopulateMaterialGrid
Khi Material mode, FilterBySearch chỉ gọi PopulateMaterialGrid và return.
PopulateMaterialGrid tự xử lý CurrentSearchText và CurrentFolderPath nội bộ.

### ⚠️ ClearListItems trước AddItem
Luôn clear CTV_FurnitureCard trước ForEach — tránh cộng dồn items từ filter trước.

---

## Quan hệ với các function khác

```
FilterByCategory("Recent") ──→ [KHÔNG gọi FilterBySearch]
FilterByCategory(other)    ──→ SET CurrentCategory → FilterBySearch ✓
BTN_AllCategory            ──→ FilterBySearch trực tiếp (CurrentCategory phải đúng)
SwitchInventoryMode        ──→ FilterBySearch(CurrentSearchText, CurrentCategory)
FilterByFolderPath         ──→ FilterBySearch(CurrentSearchText, CurrentCategory)

FilterBySearch
  ├── Material mode → PopulateMaterialGrid
  └── Furniture mode → C++ FilterFurnitureRows → AllFilteredFurnitureRows → DisplayPage → CTV_FurnitureCard
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 22/04/2026 | Logic gốc: filter furniture + material mode branch |
| 1.1 | 20/05/2026 | Thêm ClearListItems trước ForEach, fix SwitchInventoryMode |
| 1.2 | 22/05/2026 | Document rõ CategoryFilter class var vs parameter issue. Recent branch đã chuyển sang FilterByCategory |
| 1.3 | 17/06/2026 — Sprint D.T5/D.T6 | Furniture mode: FilterFurnitureItems → FilterFurnitureRows(DT_FurnitureCatalog). Output: AllFilteredFurnitureRows → DisplayPage. AllFurnitureItems class var xóa (Sprint D.T7). |
