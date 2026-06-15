# Python Scripts — UE5 Data Pipeline
# Chạy trong Output Log của UE5 Editor (Python tab)
# Cập nhật: 16/05/2026 — 14:08 ICT

---

## 1. Populate BoundingSize
**Dùng khi:** Thêm mesh mới vào project, hoặc chạy lại để fill BoundingSize cho toàn bộ DataTable.

```python
import unreal, json

ar = unreal.AssetRegistryHelpers.get_asset_registry()
dt = unreal.load_asset("/Game/cuong/UI/Data/DT_FurnitureCatalog")
rows = json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(dt))

filter = unreal.ARFilter(
    class_names=["StaticMesh"],
    recursive_paths=True,
    package_paths=["/Game/DatabaseProjectMaster"]
)
all_assets = ar.get_assets(filter)
asset_map = {str(a.asset_name): str(a.package_name) for a in all_assets}
print(f"Total meshes in registry: {len(asset_map)}")

success = 0
failed = 0

for row in rows:
    row_name = row["Name"]
    if row_name not in asset_map:
        failed += 1
        continue
    mesh = unreal.load_asset(asset_map[row_name])
    if not mesh:
        failed += 1
        continue
    bounds = mesh.get_bounds()
    size = bounds.box_extent * 2
    row["BoundingSize"] = f"(X={size.x:.6f},Y={size.y:.6f},Z={size.z:.6f})"
    success += 1

json_out = json.dumps(rows, ensure_ascii=False)
unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(dt, json_out)
print(f"Done! Success: {success}, Failed: {failed}")
```

**Sau khi chạy:** Chạy lại EUW_CreateDataAssets để sync BoundingSize vào DA_FurnitureItem.

---

## 2. Update MeshFolderPath
**Dùng khi:** Mesh bị di chuyển folder, hoặc MeshFolderPath bị sai/rỗng.

```python
import unreal, json

ar = unreal.AssetRegistryHelpers.get_asset_registry()
dt = unreal.load_asset("/Game/cuong/UI/Data/DT_FurnitureCatalog")
rows = json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(dt))

filter = unreal.ARFilter(
    class_names=["StaticMesh"],
    recursive_paths=True,
    package_paths=["/Game/DatabaseProjectMaster"]
)
all_assets = ar.get_assets(filter)
asset_map = {str(a.asset_name): str(a.package_name) for a in all_assets}

updated = 0
for row in rows:
    row_name = row["Name"]
    if row_name in asset_map:
        package_path = asset_map[row_name]
        folder = "/".join(package_path.split("/")[:-1])
        row["MeshFolderPath"] = folder
        updated += 1

json_out = json.dumps(rows, ensure_ascii=False)
unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(dt, json_out)
print(f"Updated MeshFolderPath: {updated} rows")
```

**Sau khi chạy:** Chạy lại EUW_CreateDataAssets để sync MeshFolderPath vào DA_FurnitureItem.

---

## 3. Kiểm tra Data Quality
**Dùng khi:** Verify data sau khi chạy scripts trên, hoặc debug data thiếu.

```python
import unreal, json

dt = unreal.load_asset("/Game/cuong/UI/Data/DT_FurnitureCatalog")
rows = json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(dt))

has_bounds = [r for r in rows if r["BoundingSize"] != "(X=0.000000,Y=0.000000,Z=0.000000)"]
no_bounds = [r for r in rows if r["BoundingSize"] == "(X=0.000000,Y=0.000000,Z=0.000000)"]
no_folder = [r for r in rows if not r["MeshFolderPath"]]

print(f"Total rows: {len(rows)}")
print(f"Có BoundingSize: {len(has_bounds)}")
print(f"Không có BoundingSize: {len(no_bounds)}")
print(f"Không có MeshFolderPath: {len(no_folder)}")

if no_bounds:
    print(f"Rows thiếu BoundingSize: {[r['Name'] for r in no_bounds[:5]]}")
if no_folder:
    print(f"Rows thiếu MeshFolderPath: {[r['Name'] for r in no_folder[:5]]}")
```

---

## 4. Test Load Mesh + Bounds (Debug)
**Dùng khi:** Debug 1 row cụ thể, kiểm tra mesh path và kích thước.

```python
import unreal, json

dt = unreal.load_asset("/Game/cuong/UI/Data/DT_FurnitureCatalog")
rows = json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(dt))
row = rows[0]  # Đổi index để test row khác

mesh_path = row["MeshFolderPath"] + "/" + row["Name"]
print(f"Row: {row['Name']}")
print(f"Mesh path: {mesh_path}")

mesh = unreal.load_asset(mesh_path)
if mesh:
    bounds = mesh.get_bounds()
    size = bounds.box_extent * 2
    print(f"SizeX: {size.x:.1f}cm  SizeY: {size.y:.1f}cm  SizeZ: {size.z:.1f}cm")
else:
    print("FAILED: mesh not found")
```

---

## 5. Populate ThumbnailPath cho DT_MaterialInstancesCatalog
**Dùng khi:** Sau khi import thumbnail material vào UE5, cần điền ThumbnailPath vào DataTable.

```python
import unreal, json

dt = unreal.load_asset("/Game/cuong/UI/Data/DT_MaterialInstancesCatalog")
thumb_path = "/Game/cuong/UI/Data/ThumbnailMaterialInstances"

ar = unreal.AssetRegistryHelpers.get_asset_registry()
ar.scan_paths_synchronous([thumb_path], True)

filter = unreal.ARFilter(
    class_names=["Texture2D"],
    recursive_paths=True,
    package_paths=[thumb_path]
)
all_thumbs = ar.get_assets(filter)
thumb_map = {str(a.asset_name): str(a.package_name) for a in all_thumbs}
print(f"Textures found: {len(thumb_map)}")

rows = json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(dt))

updated, missing = 0, 0
for row in rows:
    name = row["Name"]
    if name in thumb_map:
        row["ThumbnailPath"] = thumb_map[name]
        updated += 1
    else:
        missing += 1

unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(dt, json.dumps(rows, ensure_ascii=False))
print(f"Updated: {updated} | Missing: {missing}")
```

**Kết quả thực tế (08/05/2026):** Updated: 2731 | Missing: 36

⚠️ `scan_paths_synchronous` bắt buộc gọi trước khi query — Content Browser ≠ Asset Registry.

---

## 6. Update MaterialPath sang Full Object Path
**Dùng khi:** `DT_MaterialInstancesCatalog.MaterialPath` đang lưu dạng `/Game/.../MI_Name` (thiếu `.MI_Name` ở cuối) → cần đổi sang full object path `/Game/.../MI_Name.MI_Name` để `Make Soft Object Path` và `Load Asset` hoạt động đúng.

**Đã chạy:** 16/05/2026 — kết quả 2738 rows updated, 0 skipped.

```python
import unreal, json

dt = unreal.load_asset("/Game/cuong/UI/Data/DT_MaterialInstancesCatalog")
json_str = unreal.DataTableFunctionLibrary.export_data_table_to_json_string(dt)
rows = json.loads(json_str)

updated = 0
for row in rows:
    path = row.get("MaterialPath", "")
    if path and "." not in path:
        asset_name = path.split("/")[-1]
        row["MaterialPath"] = path + "." + asset_name
        updated += 1

unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(dt, json.dumps(rows, ensure_ascii=False))
unreal.EditorAssetLibrary.save_asset("/Game/cuong/UI/Data/DT_MaterialInstancesCatalog")
print(f"Updated {updated} rows")
```

**Tại sao cần:** `Make Soft Object Path` trong Blueprint cần format `PackagePath.AssetName` (ví dụ `/Game/.../MI_Stone.MI_Stone`). Nếu chỉ có `/Game/.../MI_Stone`, node không resolve được asset → `Async Load Asset` không fire Completed → material không apply được.

**Sau khi chạy:** Không cần append `.AssetName` thủ công trong Blueprint nữa — dùng `MaterialPath` trực tiếp làm input cho `Make Soft Object Path`.

---

## Lưu ý chung
- Sau khi chạy script 1 hoặc 2 → **luôn chạy lại EUW_CreateDataAssets** để sync vào DA_
- RowName trong DataTable = tên file mesh trong Content Browser
- Mesh path = MeshFolderPath + "/" + RowName
- 15 rows không có BoundingSize = mesh chưa có trong project (bình thường)
