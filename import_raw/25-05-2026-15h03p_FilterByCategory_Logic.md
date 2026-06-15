# FilterByCategory — Node Flow Reference
**Phiên bản:** 1.2 | **Cập nhật:** 25/05/2026 — 15:03 ICT | WBP_FurnitureInventory

---

## Signature
```
Function: FilterByCategory(CategoryFilter : Name)
```

---

## Flow đầy đủ

```
FilterByCategory(CategoryFilter):

← BƯỚC ĐẦU: Print debug (xóa sau khi ổn định)

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
              String to Name( Get Object Name(DA) ) == RowName   ← Name == Name
              Branch True:
                Add Item(CTV_FurnitureCard, DA)   ← ⚠️ phải nối Item pin vào DA
                → Break inner ForEach
              Branch False:
                (để trống — loop tự tiếp tục)
          Completed: tiếp outer loop

        Return   ← thoát hẳn, không gọi FilterBySearch

  F →
    ← v1.2: Favorite xử lý riêng, KHÔNG đi qua FilterBySearch
    Branch CategoryFilter == "Favorite":
      T →
        Branch CurrentInventoryMode == Material:
          T →
            GET BP_FurnitureUserPrefsManager → GET UserPrefs → GET FavoriteMaterials
            SET AllFilteredMaterialRows = FavoriteMaterials
            SET CurrentPage = 0
            Call DisplayPage
            Return

          F →
            Clear List Items(CTV_FurnitureCard)
            GET BP_FurnitureUserPrefsManager → GET UserPrefs → GET FavoriteMeshes → FavArray

            ← Thu thập DA match vào array trước, rồi Set List Items 1 lần
            Local: MatchedFavDA : Array of Object

            ForEach FavArray (RowName):              ← outer loop
              ForEach AllFurnitureItems (DA):        ← inner loop with Break
                Loop Body:
                  String to Name( Get Object Name(DA) ) == RowName
                  Branch True:
                    ADD(MatchedFavDA, DA)   ← ⚠️ nối Item pin vào DA
                    → Break inner ForEach
                  Branch False:
                    (để trống)
              Completed: tiếp outer loop

            Set List Items(CTV_FurnitureCard, MatchedFavDA)
            Return

      F →
        ← Logic gốc (non-Recent, non-Favorite categories):
        SET ActiveSpecialCategory = ""   ← reset khi user chọn category thường
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
| BTN_RecentCategory OnClicked | toggle "Recent" hoặc FilterBySearch | v1.1 — toggle logic, xem bên dưới |
| BTN_FavoriteCategory OnClicked | toggle "Favorite" hoặc FilterBySearch | v1.2 — toggle logic, xem bên dưới |
| BindCategoryEvents → các folder/category buttons | Tên category cụ thể | Bind trong Event Construct |
| FilterByFolderPath | CurrentCategory | Giữ category khi đổi folder |
| BTN_Tab_Furniture OnClicked | ActiveSpecialCategory | Sau SwitchInventoryMode nếu special active |
| BTN_Tab_Material OnClicked | ActiveSpecialCategory | Sau SwitchInventoryMode nếu special active |

---

## Toggle Logic — BTN_RecentCategory / BTN_FavoriteCategory

### BTN_RecentCategory OnClicked
```
Branch ActiveSpecialCategory == "Recent":
  T → (đang chọn → deselect)
      SET ActiveSpecialCategory = ""
      FilterBySearch(CurrentSearchText, CurrentCategory)   ← restore trạng thái trước
  │
  F → (chưa chọn → select)
      Branch ActiveSpecialCategory == "":
        T → (không có special nào active)
            ← CurrentCategory/FolderPath/SearchText tự nhiên preserve, không cần save
        F → (special khác đang active, switch sang Recent)
      SET ActiveSpecialCategory = "Recent"
      FilterByCategory("Recent")
  │
  └── merge → Call UpdateSpecialHighlight
```

### BTN_FavoriteCategory OnClicked
```
Branch ActiveSpecialCategory == "Favorite":
  T → SET ActiveSpecialCategory = ""
      FilterBySearch(CurrentSearchText, CurrentCategory)
  │
  F →
      Branch ActiveSpecialCategory == "":
        T → (không cần làm gì thêm)
        F → (skip)
      SET ActiveSpecialCategory = "Favorite"
      FilterByCategory("Favorite")
  │
  └── merge → Call UpdateSpecialHighlight
```

⚠️ **Không cần PreviousCategory** — CurrentCategory/CurrentFolderPath/CurrentSearchText không bao giờ bị thay đổi khi FilterByCategory("Recent"/"Favorite") chạy (vì cả 2 Return sớm). FilterBySearch(CurrentSearchText, CurrentCategory) tự restore đúng trạng thái.

---

## UpdateSpecialHighlight (Function)

```
Branch ActiveSpecialCategory == "Recent":
  T → Set Background Color(BTN_RecentCategory, ColorButtonChoose)
       Set Background Color(BTN_FavoriteCategory, ColorButtonDefault)
  F →
    Branch ActiveSpecialCategory == "Favorite":
      T → Set Background Color(BTN_FavoriteCategory, ColorButtonChoose)
           Set Background Color(BTN_RecentCategory, ColorButtonDefault)
      F → Set Background Color(BTN_RecentCategory, ColorButtonDefault)
           Set Background Color(BTN_FavoriteCategory, ColorButtonDefault)
```

Gọi từ: cuối BTN_RecentCategory OnClicked và BTN_FavoriteCategory OnClicked (sau merge 2 nhánh).

---

## Persist khi Switch Mode (BTN_Tab_Furniture / BTN_Tab_Material)

```
BTN_Tab_Furniture OnClicked:
  Call SwitchInventoryMode(Furniture)
  → Branch ActiveSpecialCategory != "":
      T → FilterByCategory(ActiveSpecialCategory)   ← wire từ GET ActiveSpecialCategory
      F → (không làm gì — SwitchInventoryMode đã gọi FilterBySearch)

BTN_Tab_Material OnClicked:
  Call SwitchInventoryMode(Material)
  → Branch ActiveSpecialCategory != "":
      T → FilterByCategory(ActiveSpecialCategory)
      F → (không làm gì)
```

⚠️ **KHÔNG sửa bên trong SwitchInventoryMode** — xử lý ở Tab button OnClicked sau khi SwitchInventoryMode hoàn tất → CurrentInventoryMode đã được SET đúng.

---

## Variables mới (WBP_FurnitureInventory)

| Tên | Kiểu | Default | Mô tả |
|---|---|---|---|
| `ActiveSpecialCategory` | Name | "" (None) | "Recent", "Favorite", hoặc "" = không active |

---

## Lưu ý quan trọng

- **"Recent" và "Favorite" KHÔNG gọi FilterBySearch** — xử lý hoàn toàn trong FilterByCategory để tránh CategoryFilter class variable pollution
- **ForEach False branch để trống** — không nối vào Break, Blueprint tự tiếp tục iteration
- **Add Item / Set List Items — Item pin phải được nối vào DA (Array Element)** — nếu không nối, Add Item chạy nhưng không add gì
- **String to Name( Get Object Name(DA) ) == RowName** — so sánh Name với Name, không dùng Name to String (dễ bị type mismatch)
- **CategoryFilter parameter vs class variable** — trong FilterByCategory, LUÔN dùng wire từ input pin của function, không dùng GET node riêng (GET node riêng đọc class variable, không phải parameter)
- **FilterByCategory(ActiveSpecialCategory) trong Tab button** — Category Filter pin phải được wire từ GET ActiveSpecialCategory, không gõ literal "ActiveSpecialCategory" vào ô

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 20/05/2026 | Logic gốc: SET CategoryFilter + CurrentCategory, Branch Is Empty search text, gọi FilterBySearch |
| 1.1 | 22/05/2026 | Thêm Recent branch ở đầu — xử lý Recent trực tiếp, bypass FilterBySearch |
| 1.2 | 25/05/2026 — 15:03 ICT | Thêm Favorite branch. Toggle logic cho Recent/Favorite. UpdateSpecialHighlight. Persist khi switch mode. Fix: String to Name comparison, Item pin Add Item, parameter vs class variable bug |
