# FurnitureFilterLibrary — C++ Blueprint Function Library Reference
**Nguồn:** `import_raw/FurnitureFilterLibrary.cpp` (source code — không copy, chỉ reference)
**Cập nhật:** (theo .cpp file hiện tại)

> File này là TÀI LIỆU THAM KHẢO — liệt kê function signatures và hành vi. Để thêm function mới (FilterFurnitureRows, GetDistinctFolderPaths cho Sprint D), xem `00_Core/02_Current_Sprint.md` mục D.T3 và D.T7.

---

## Class: UFurnitureFilterLibrary
**Plugin:** FurnitureToolkit
**Files:** `FurnitureFilterLibrary.h` / `FurnitureFilterLibrary.cpp`

---

## Hàm 1 — FilterFurnitureItems (Legacy DA-based)

```cpp
static TArray<UPrimaryDataAsset*> FilterFurnitureItems(
    const TArray<UPrimaryDataAsset*>& AllItems,
    const FString& SearchText,
    const FString& FolderPath,
    const FName& CategoryFilter,
    int32 MaxResults = 0);
```

**Blueprint node:** `FilterFurnitureItems`

**Params:**
| Param | Kiểu | Mô tả |
|---|---|---|
| AllItems | Array of PrimaryDataAsset | Toàn bộ DA đã load vào RAM (từ Event Construct) |
| SearchText | String | Tìm theo VieName (contains, IgnoreCase) |
| FolderPath | String | Lọc theo MeshFolderPath (contains) |
| CategoryFilter | Name | Lọc theo Category (exact match; "All" hoặc None = bỏ qua) |
| MaxResults | Int32 | Giới hạn kết quả; 0 = không giới hạn |

**Return:** Array of UPrimaryDataAsset*

**Logic:**
- Duyệt AllItems đã load trong RAM
- FindFProperty trực tiếp theo tên (VieName, MeshFolderPath, Category)
- ⚠️ Đọc property trực tiếp từ DA object → phải load DA vào RAM trước
- ⚠️ **DEPRECATED từ Sprint D** — sẽ bị thay bởi `FilterFurnitureRows` (DT-based)

---

## Hàm 2 — FilterFurnitureItemsFromRegistry (Asset Registry-based)

```cpp
static TArray<FSoftObjectPath> FilterFurnitureItemsFromRegistry(
    const FString& AssetPath,
    const FString& SearchText,
    const FString& FolderPath,
    const FName& CategoryFilter,
    int32 MaxResults = 0);
```

**Blueprint node:** `FilterFurnitureItemsFromRegistry`

**Params:**
| Param | Kiểu | Mô tả |
|---|---|---|
| AssetPath | String | Package path (vd "/Game/cuong/UI/Data/FurnitureAssets") |
| SearchText | String | Tìm theo VieName |
| FolderPath | String | Lọc theo PackagePath |
| CategoryFilter | Name | Lọc theo Category |
| MaxResults | Int32 | Giới hạn kết quả |

**Return:** Array of FSoftObjectPath

**Logic:**
- Dùng IAssetRegistry để tìm Blueprint assets theo path
- Load từng asset để đọc property → chậm hơn FilterFurnitureItems nếu đã có AllItems
- ⚠️ GetAsset() loads asset → blocking

---

## Hàm 3 — FilterMaterialItems (DT-based — ACTIVE)

```cpp
static TArray<FName> FilterMaterialItems(
    UDataTable* MaterialTable,
    const FString& SearchText,
    const TArray<FString>& TypeTags,
    const FString& SubFolderPath,
    int32 MaxResults = 0);
```

**Blueprint node:** `FilterMaterialItems`

**Params:**
| Param | Kiểu | Mô tả |
|---|---|---|
| MaterialTable | DataTable | DT_MaterialInstancesCatalog |
| SearchText | String | Tìm theo VieName hoặc EngName (contains, IgnoreCase) |
| TypeTags | Array of String | Lọc theo MaterialFolderPath (contains ANY tag) |
| SubFolderPath | String | Sub-folder drill-down (contains) |
| MaxResults | Int32 | Giới hạn kết quả |

**Return:** Array of FName (RowNames)

**Logic:**
- Đọc RowMap của DataTable — KHÔNG load asset
- Dùng PropertyLink để tìm property theo keyword (vì Blueprint struct có GUID append trong tên)
- Cache FStrProperty/FTextProperty NGOÀI loop → hiệu năng tốt
- Match VieName OR EngName cho search text
- Return RowNames nhẹ → Widget tự Get Data Table Row khi cần

**⭐ Pattern này là MẪUCHO FilterFurnitureRows (Sprint D, D.T3):**
- Mirror cách duyệt PropertyLink
- Dùng GetAuthoredName() thay Contains (xem D.T3 trong `00_Core/02_Current_Sprint.md`)

---

## Hàm 4 — LoadFurnitureItem

```cpp
static UPrimaryDataAsset* LoadFurnitureItem(const FSoftObjectPath& ItemPath);
```

**Blueprint node:** `LoadFurnitureItem`

**Logic:** TryLoad() → Cast to UPrimaryDataAsset. Blocking load — chỉ dùng cho resolve đơn lẻ.

---

## Hàm cần thêm (Sprint D)

| Hàm | Sprint | Mô tả |
|---|---|---|
| `FilterFurnitureRows` | D.T3 | DT-based filter (mirror FilterMaterialItems cho DT_FurnitureCatalog) |
| `GetDistinctFolderPaths` | D.T7 | Distinct MeshFolderPath values từ DT (cho BuildFolderTree) |

Xem spec đầy đủ trong `00_Core/02_Current_Sprint.md` mục D.T3 và D.T7.

---

## Lưu ý tích hợp

- Plugin: `FurnitureToolkit` — đảm bảo plugin enabled trong .uproject
- Include: `#include "FurnitureFilterLibrary.h"` (chỉ dùng nếu gọi từ C++ khác)
- Blueprint: node hiện trực tiếp sau khi compile plugin
- **Dependency:** FilterMaterialItems dùng `IAssetRegistry` (module `AssetRegistry`) — check Build.cs đã có
