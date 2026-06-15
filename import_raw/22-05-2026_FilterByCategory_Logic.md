# FilterByCategory — Node Flow Reference
**Phiên bản:** 1.1 | **Tạo:** 22/05/2026 | WBP_FurnitureInventory

---

## Signature
```
Function: FilterByCategory(CategoryFilter : Name)
```

---

## Flow đầy đủ

```
FilterByCategory(CategoryFilter):

← v1.1: Recent xử lý riêng, KHÔNG đi qua FilterBySearch
Branch CategoryFilter == "Recent":
  T →
    Branch CurrentInventoryMode == Material:
      T →
        GET BP_FurnitureUserPrefsManager → GET UserPrefs → GET RecentMaterials
        SET AllFilteredMaterialRows = RecentMaterials
        SET CurrentPage = 0
        Call DisplayPage
        Return

      F →
        Clear List Items(CTV_FurnitureCard)
        GET BP_FurnitureUserPrefsManager → GET UserPrefs → GET RecentMeshes → RecentArray

        ForEach RecentArray (RowName):         ← outer loop: giữ thứ tự Recent
          ForEach AllFurnitureItems (DA):      ← inner loop with Break: tìm DA match
            Loop Body:
              Get Object Name(DA) == Name to String(RowName):
              Branch True:
                Add Item(CTV_FurnitureCard, DA)
                → Break inner ForEach
              Branch False:
                tiếp tục loop
          Completed: tiếp outer loop

        Return   ← thoát hẳn, không gọi FilterBySearch

  F →
    ← Logic gốc (non-Recent categories):
    SET CategoryFilter (class var) = CategoryFilter (parameter)
    SET CurrentCategory = CategoryFilter (parameter)

    Branch Is Empty(CurrentSearchText as Text):
      True (không có search text):
        Get Assets by Path("/Game/cuong/UI/Data/FurnitureAssets")
        → Get Asset Registry
        → FilterBySearch(CurrentSearchText, CurrentCategory)

      False (có search text):
        → FilterBySearch(CurrentSearchText, CurrentCategory)
```

---

## Nơi gọi FilterByCategory

| Caller | CategoryFilter | Ghi chú |
|---|---|---|
| BTN_AllCategory OnClicked | "All" | Hiện tất cả |
| BTN_RecentCategory OnClicked | "Recent" | v1.1 — Hiện lịch sử gần đây |
| BindCategoryEvents → các folder/category buttons | Tên category cụ thể | Bind trong Event Construct |
| FilterByFolderPath | CurrentCategory | Giữ category khi đổi folder |

---

## Lưu ý quan trọng

- **"Recent" KHÔNG gọi FilterBySearch** — xử lý hoàn toàn trong FilterByCategory để tránh CategoryFilter class variable pollution
- **BTN_AllCategory và các category khác gọi FilterBySearch trực tiếp** (không qua FilterByCategory) → CurrentCategory không được update khi gọi FilterBySearch trực tiếp
- **ForEach outer loop giữ thứ tự Recent** — item mới nhất hiện trước, đúng với thứ tự trong RecentMeshes array
- **ForEach with Break** trong inner loop → tránh duplicate khi DA xuất hiện nhiều lần
- **Get Object Name(DA)** phải dùng nhất quán với cách lưu RowName (cũng dùng Get Object Name khi AddRecentMesh)

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 20/05/2026 | Logic gốc: SET CategoryFilter + CurrentCategory, Branch Is Empty search text, gọi FilterBySearch |
| 1.1 | 22/05/2026 | Thêm Recent branch ở đầu — xử lý Recent trực tiếp, bypass FilterBySearch |
