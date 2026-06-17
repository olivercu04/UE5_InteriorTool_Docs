# Data — Overview
**Tạo:** 17/06/2026 — Sprint D.T6 | Kiến trúc data layer sau D.T6

---

## 2 nguồn dữ liệu chính

| DataTable | Số row | Path |
|---|---|---|
| `DT_FurnitureCatalog` | ~2114 row | /Game/cuong/UI/Data/ |
| `DT_MaterialInstancesCatalog` | ~2738 row | /Game/DatabaseProjectMaster/Material/MaterialInstances/ |

---

## S_FurnitureData — field chính

```
VieName          : String
EngName          : String
Category         : Name
Description      : String
BoundingSize     : Vector
MeshFolderPath   : String
ThumbnailSoft    : TSoftObjectPtr<UTexture2D>
Mesh             : TSoftObjectPtr<UStaticMesh>  ← populate 17/06/2026 qua D.T6
Link             : String
```

> Load mesh: `Break S_FurnitureData → Static Mesh ●→ Load Asset Blocking .Asset → Return Value`
> Chi tiết field đầy đủ: `Data_Structures.md`

---

## Kiến trúc đọc data (sau D.T6, 17/06/2026)

`DT_FurnitureCatalog` là **NGUỒN ĐỌC DUY NHẤT** cho Furniture inventory.

`DA_FurnitureItem` là **LEGACY** — chỉ giữ vì save cũ còn `DAPath` trên `BP_FurnitureActor`. Không còn được inventory đọc. Pattern fallback: `Branch RowName == "" → True: load DAPath cũ`.

`C++ FilterFurnitureRows` trả `Array<Name>` (RowName), không trả object.

---

## BP_FurnitureItemView (object nhẹ feed Tile View)

Object wrapper tạo per row để truyền vào `CTV_FurnitureCard` (ListView/TileView).

```
RowName          : Name
VieName          : String
EngName          : String
ThumbnailSoft    : TSoftObjectPtr<UTexture2D>
MeshSoft         : TSoftObjectPtr<UStaticMesh>
MeshFolderPath   : String
BoundingSize     : Vector
Description      : String
Link             : String
Category         : Name
```

---

## Search / Filter

| File | Trạng thái |
|---|---|
| `FilterBySearch_Logic.md` | v1.3 (D.T6) — cập nhật `FilterFurnitureRows` + `DisplayPage` |
| `FilterByCategory_Logic.md` | v1.3 (D.T6) — Recent/Favorite đọc DT trực tiếp |
| `FurnitureFilterLibrary_Reference.md` | C++ static functions |

---

## Python population scripts

`Python_Scripts.md` — script populate:
- `ThumbnailPath` / `MaterialFolderPath` / `ThumbnailMI`
- `ThumbnailSoft` / `Mesh` (field `Mesh` / `Static Mesh` mới thêm 17/06/2026, D.T6 data fix)
- 2101/2114 row đã update; 13 row Hafele/Clara/import-ID deferred (edge case path pattern)

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 17/06/2026 — Sprint D.T6 | Tạo mới — tổng hợp kiến trúc Data layer sau D.T6. GAP trước đó không có file overview. |
