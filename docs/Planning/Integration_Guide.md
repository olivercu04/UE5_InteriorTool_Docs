# Hướng dẫn Tích hợp vào Project Tổng
**Phiên bản:** 1.3 | **Cập nhật:** 02/06/2026 — 11:44 ICT | Project: Lighting_Mnger (UE5.5.4)

---

## CHANGELOG

### v1.3 (02/06/2026) — Cập nhật sau integration thực tế
- **Bước 3-5 (C++ Module) → XÓA HOÀN TOÀN** — thay bằng plugin FurnitureToolkit
- **Bước 2** — copy CẢ 2 plugin: RuntimeTransformer + FurnitureToolkit
- **Bước 3 MỚI** — Pre-open checks cho plugin (API macro, Build.cs, CoreRedirect)
- **Bước 9** — WBP_FOFF_ToolDemo cần thêm variable TransformerPawnRef + Button_FurnitureInventory
- **Bước 10** — Spawn order: dùng Then pin CUỐI CÙNG trống (số Then tùy master)
- **Bước 11** — AddFurnitureInput: node Add Mapping Context hay để trống → phải chọn tay LM_FurnitureInput
- **Bước 15 MỚI** — Data pipeline sau integration (DT reimport + Python scripts + EUW)
- **Bảng lỗi** — thêm lỗi thực tế phát sinh
- **GPU crash** — Alt+P (Standalone) thay PIE để test trong master

### v1.2 (01/06/2026)
- Thêm Phase 2.1: Nudge, Copy/Paste, Recent/Favorite, Resize Window

### v1.1 (20/05/2026)
- Tích hợp Material v1.1

---

## Điều kiện tiên quyết

- Project tổng dùng cùng Engine version: **UE5.5.4**
- Project tổng đã có **DatabaseProjectMaster** (mesh, material)
- Project tổng đã có **Easy Multi Save (EMS)** plugin
- Máy có **Visual Studio** (để build plugin C++)

---

## GIAI ĐOẠN 1 — Trước khi mở UE5 (File Explorer + text editor)

### Bước 1 — Copy Content/cuong/

**Đóng cả 2 project trước.**

```
[WorkingCopy]/Content/cuong/  →  [Master]/Content/cuong/
```

⚠️ Nếu master đã có folder cuong/ cũ → backup trước khi đè.

---

### Bước 2 — Copy 2 Plugin

```
[WorkingCopy]/Plugins/RuntimeTransformer/  →  [Master]/Plugins/RuntimeTransformer/
[WorkingCopy]/Plugins/FurnitureToolkit/    →  [Master]/Plugins/FurnitureToolkit/
```

Tạo folder `Plugins/` nếu chưa có.

---

### Bước 3 — Verify Plugin FurnitureToolkit (text editor)

Mở từng file bằng Notepad/VS Code, kiểm tra:

**3a. API Macro**
File: `Plugins/FurnitureToolkit/Source/FurnitureToolkit/Public/FurnitureFilterLibrary.h`
```cpp
// ĐÚNG:
class FURNITURETOOLKIT_API UFurnitureFilterLibrary : public UBlueprintFunctionLibrary
// SAI (phải đổi):
class LIGHTING_MNGER_API UFurnitureFilterLibrary ...
```

**3b. Build.cs**
File: `Plugins/FurnitureToolkit/Source/FurnitureToolkit/FurnitureToolkit.Build.cs`
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
PrivateDependencyModuleNames.AddRange(new string[] { "AssetRegistry" });
```
⚠️ Phải có `AssetRegistry`. Không cần RuntimeTransformer, Slate, SlateCore.

**3c. .cpp Includes**
File: `Plugins/FurnitureToolkit/Source/FurnitureToolkit/Private/FurnitureFilterLibrary.cpp`
```cpp
#include "FurnitureFilterLibrary.h"
#include "Engine/DataAsset.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "AssetRegistry/IAssetRegistry.h"
```
Nếu có `#include "Lighting_Mnger.h"` → xóa dòng đó.

**3d. CoreRedirect**
File: `[Master]/Config/DefaultEngine.ini` → thêm vào cuối:
```ini
[CoreRedirects]
+ClassRedirects=(OldName="/Script/Lighting_Mnger.FurnitureFilterLibrary",NewName="/Script/FurnitureToolkit.FurnitureFilterLibrary")
```
Nếu `[CoreRedirects]` đã có → chỉ thêm dòng `+ClassRedirects=...` bên dưới.

---

## GIAI ĐOẠN 2 — Trong UE5

### Bước 4 — Mở Master + Build Plugin

Mở `[Master].uproject` → UE5 hỏi rebuild plugin → **Yes** → đợi compile xong.

Nếu không hỏi tự động: right-click `.uproject` → Generate VS project files → mở `.sln` → **Development Editor** → Build.

---

### Bước 5 — Fix Shared Code

**5a. Foff_GameInstance**
Mở `Foff_GameInstance` → Variables → **+ Add**:
```
Tên:  FurnitureInventoryRef
Kiểu: WBP_FurnitureInventory (Object Reference)
```
Compile + Save.

**5b. BP_FoffPlayerController**
Thêm 2 Custom Event:

**AddFurnitureInput:**
```
→ Get Enhanced Input Local Player Subsystem (target: self)
→ Is Valid?
  True:
    → Remove Mapping Context (LM_InputMapping)
    → Add Mapping Context (LM_FurnitureInput, Priority = 3)
```

**RemoveFurnitureInput:**
```
→ Get Enhanced Input Local Player Subsystem
→ Is Valid?
  True:
    → Remove Mapping Context (LM_FurnitureInput)
    → Add Mapping Context (LM_InputMapping, Priority = 2)
```

⚠️ **LỖI HAY GẶP:** Node "Add/Remove Mapping Context" hay để trống asset → phím không hoạt động. Phải click chọn đúng **LM_FurnitureInput** (trong `/Game/cuong/UI/Input/`) và **LM_InputMapping** (mapping context gốc của master).

Compile + Save.

---

### Bước 6 — GizmoTrace Collision Channel

`Project Settings → Engine → Collision → Trace Channels → New Trace Channel`
```
Name:             GizmoTrace
Default Response: Ignore
```
→ Accept.

Mở từng Gizmo Blueprint (trong RuntimeTransformer plugin) → từng component trục → Collision → **GizmoTrace = Block**.

---

### Bước 7 — Post Process + Custom Depth

**7a.** `Project Settings → Engine → Rendering → Postprocessing`
→ **Custom Depth-Stencil Pass = Enabled with Stencil**

⚠️ Có thể báo *"Error: Failed to add the configuration file"* — đây là lỗi cosmetic, setting vẫn apply. Không cần sửa tay DefaultEngine.ini.

**7b.** Trong level → Post Process Volume (hoặc tạo mới với Infinite Extent = True):
→ Post Process Materials → **+** → chọn `M_SelectionOutline`

---

### Bước 8 — Gizmo Material Emissive

`Content Browser → Show Plugin Content → RuntimeTransformer Content → Materials`

Mở từng material gizmo → tăng **Emissive × 1000** → Save.

---

### Bước 9 — WBP_FOFF_ToolDemo: Chuẩn bị

Mở **WBP_FOFF_ToolDemo**.

**9a. Thêm variable TransformerPawnRef:**
My Blueprint → Variables → **+ Add**:
```
Tên:  TransformerPawnRef
Kiểu: BP_TransformerPawn (Object Reference)
```

**9b. Thêm Button_FurnitureInventory trong Designer:**
Tab Designer → thêm **Button** → đặt Variable Name = `Button_FurnitureInventory`

Vị trí tùy layout master.

**9c. OnClicked (Button_FurnitureInventory):**
```
Branch IsValid(Get GameInstance → Cast → FurnitureInventoryRef)?
  True (đóng):
    Cast Player Controller → RemoveFurnitureInput
    Remove from Parent (FurnitureInventoryRef)
    SET FurnitureInventoryRef = None
  False (mở):
    Create WBP_FurnitureInventory → Add to Viewport
    Cast Player Controller → AddFurnitureInput
    SET FurnitureInventoryRef
```

---

### Bước 10 — Spawn Order trong WBP_FOFF_ToolDemo

Event Graph → Event Construct → tìm **Sequence node**.

Dùng **Then pin cuối cùng còn trống** (số Then tùy master — ví dụ Then 11 nếu master có Then 0-10).

Nối chuỗi spawn:
```
Then N
  → Spawn Actor (BP_UndoManager)          [Make Transform default]
  → Spawn Actor (BP_FurnitureSceneManager)
  → Spawn Actor (BP_TransformerPawn)
      Return Value → SET TransformerPawnRef (widget variable)
  → Spawn Actor (BP_GizmoController)
      Return Value → lưu local var GizmoRef
  → Spawn Actor (BP_FurnitureInputManager)
      Return Value → Cast BP_FurnitureInputManager
        → SET GizmoControllerRef = GizmoRef
  → Spawn Actor (BP_FurnitureUserPrefsManager)
  → Create Widget (WBP_MeshControls)
      Return Value → Add to Viewport
      → Get All Actors Of Class (BP_FurnitureInputManager) → Get(0)
        → Cast → SET CurrentMeshControls
  → Get All Actors Of Class (BP_UndoManager) → Get(0)
      → Cast → CaptureSnapshot("Initial")   ← CUỐI CÙNG
```

⚠️ CaptureSnapshot phải là node CUỐI. Spawn Actor cần Transform input → Make Transform (default 0,0,0).

Compile + Save.

---

### Bước 11 — Verify Enhanced Input Bindings

Mở **BP_FoffPlayerController** → kiểm tra có đủ 7 Enhanced Input Action events:

| Action | Trigger | Gọi |
|--------|---------|-----|
| IA_FurnitureUndo | Started | Branch Shift? → UndoLastAction |
| IA_FurnitureRedo | Started | RedoLastAction |
| IA_FurnitureDelete | Started | DeleteSelectedMesh |
| IA_FurnitureNudge | **Triggered** | NudgeMesh(ActionValue) |
| IA_FurnitureCopy | Started | CopyMesh |
| IA_FurniturePaste | Started | PasteMesh |
| IA_FurnitureDuplicate | Started | DuplicateMesh |

Nếu chưa có → thêm từng Enhanced Input Action event + nối logic.

---

### Bước 12 — Shared Code (báo đồng nghiệp)

| File | Thay đổi |
|------|---------|
| Foff_GameInstance | + FurnitureInventoryRef (WBP_FurnitureInventory) |
| BP_FoffPlayerController | + AddFurnitureInput, RemoveFurnitureInput, 7 IA_ bindings |
| WBP_FOFF_ToolDemo | + TransformerPawnRef, Button_FurnitureInventory, Spawn Order |
| Project Settings | + GizmoTrace channel, Custom Depth = Enabled with Stencil |

---

### Bước 13 — SaveGame Recent/Favorite

`BP_FurnitureUserPrefsManager` đã spawn ở Bước 10. Verify bằng cách test: mở inventory → spawn mesh → category **Recent** có hiện mesh vừa dùng.

---

### Bước 14 — Resize Window

Không cần setup riêng — migrate theo `/cuong/`. Verify: kéo cạnh/góc WBP_FurnitureInventory.

---

### Bước 15 — Data Pipeline (sau integration)

Sau khi reimport DT_FurnitureCatalog từ CSV mới:

**15a. Chạy Script 2 (MeshFolderPath)** trong UE5 Output Log → Python tab:
```python
import unreal, json
ar = unreal.AssetRegistryHelpers.get_asset_registry()
dt = unreal.load_asset("/Game/cuong/UI/Data/DT_FurnitureCatalog")
rows = json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(dt))
filter = unreal.ARFilter(class_names=["StaticMesh"], recursive_paths=True,
    package_paths=["/Game/DatabaseProjectMaster"])
all_assets = ar.get_assets(filter)
asset_map = {str(a.asset_name): str(a.package_name) for a in all_assets}
updated = 0
for row in rows:
    if row["Name"] in asset_map:
        pkg = asset_map[row["Name"]]
        row["MeshFolderPath"] = "/".join(pkg.split("/")[:-1])
        updated += 1
unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(dt,
    json.dumps(rows, ensure_ascii=False))
print(f"Updated MeshFolderPath: {updated} rows")
```

**15b. Chạy Script 1 (BoundingSize)** — xem Python_Scripts.md.
⚠️ Script này load nhiều mesh → **restart editor trước** để tránh GPU VRAM crash. Dùng batch size 30.

**15c. Chạy EUW_CreateDataAssets** để sync vào DA_FurnitureItem.

---

## Checklist kiểm tra sau tích hợp

**Plugin + Core:**
- [ ] Edit → Plugins → FurnitureToolkit: Enabled ✓
- [ ] WBP_FurnitureInventory → Filter Furniture Items node: không lỗi đỏ
- [ ] Nút Furniture Inventory → mở/đóng WBP_FurnitureInventory

**Furniture core:**
- [ ] Drag & Drop mesh từ inventory → mesh xuất hiện trong scene
- [ ] Click mesh → outline highlight xanh
- [ ] Gizmo hiện, Move/Rotate/Scale OK
- [ ] Ctrl+Z Undo / Ctrl+Shift+Z Redo
- [ ] Save / Load (EMS)

**Material v1.1:**
- [ ] Tab Material → SlotSwatches đúng slot
- [ ] Click material → apply ngay
- [ ] Reset Slot / Reset All
- [ ] Undo/Redo material

**Phase 2.1:**
- [ ] Arrow keys → nudge mesh đúng hướng
- [ ] Ctrl+C → Ctrl+V → paste tại cursor
- [ ] Ctrl+D → duplicate
- [ ] Phím D không di chuyển camera khi inventory mở
- [ ] Category Recent / Favorite hoạt động

**Resize Window:**
- [ ] Kéo 4 cạnh + 4 góc inventory → resize đúng

---

## Bảng lỗi hay gặp

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| Filter node đỏ trong WBP_FurnitureInventory | Plugin chưa build | Build FurnitureToolkit (Bước 4) |
| RemoveFurnitureInput not found | Chưa thêm Custom Event | Bước 5b |
| FurnitureInventoryRef not found | Chưa thêm variable | Bước 5a |
| TransformerPawnRef not found | Chưa thêm variable vào WBP_FOFF_ToolDemo | Bước 9a |
| Button_FurnitureInventory not found | Chưa thêm button trong Designer | Bước 9b |
| Phím không hoạt động (Ctrl+Z, arrow...) | Add Mapping Context node để trống | Bước 5b + 11: chọn LM_FurnitureInput |
| Màn hình nhiễu trắng | Custom Depth chưa enable | Bước 7a |
| Gizmo màu đen | Emissive thấp | Bước 8 |
| Không click được gizmo | GizmoTrace chưa setup | Bước 6 |
| "Failed to add configuration file" | Cosmetic error khi set Custom Depth | Bỏ qua — setting vẫn apply |
| GPU Crashed khi stop PIE | VRAM đầy (master project nặng) | Dùng Alt+P (Standalone Game) |
| GPU crash khi chạy Script 1 | Load quá nhiều mesh cùng lúc | Restart editor trước, dùng batch 30 |
| SceneCapture2D thumbnail đen | Capture Source sai | "Final Color (LDR) in RGB" |
| SlotSwatches không cập nhật sau Undo | RestoredBPActor chưa implement | BP_UndoManager.md fix |
