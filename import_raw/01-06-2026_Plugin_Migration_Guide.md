# Chuyển C++ thành Plugin FurnitureToolkit
**Phiên bản:** 1.0 | **Ngày:** 01/06/2026 | UE5.5.4
**Mục tiêu:** Đưa FurnitureFilterLibrary từ project module sang plugin riêng → integration sau này chỉ cần copy folder plugin.

---

## TỔNG QUAN

**Move:** chỉ `FurnitureFilterLibrary.h` + `.cpp`
**Plugin tên:** `FurnitureToolkit`
**Dependency:** Core, CoreUObject, Engine + **AssetRegistry** (KHÔNG RuntimeTransformer, KHÔNG Slate)
**Giữ nguyên trong project:** Lighting_Mnger.h/.cpp (module), MyClass.h/.cpp (rỗng, có thể xóa sau)

**Lợi ích:** Integration → master chỉ cần copy 2 folder plugin (RuntimeTransformer + FurnitureToolkit). Master giữ Blueprint-only, không cần tạo C++ module, không sửa Build.cs của master.

⚠️ **Rủi ro:** Blueprint node gọi FilterFurnitureItems/FilterMaterialItems có thể đứt reference khi class đổi module. → Dùng **CoreRedirect** (Bước 7) để chống đứt. Vẫn test kỹ.

---

## BƯỚC 0 — Backup (BẮT BUỘC)

Copy nguyên thư mục project, đặt tên rõ:
```
project_22042026/  →  backup_truoc_plugin_01_06/
```
Việc này có thể đụng C++ + Blueprint refs → phải có đường lùi.

---

## BƯỚC 1 — Tạo plugin qua Editor

1. Mở project trong UE5 (đảm bảo compile OK trước)
2. **Edit → Plugins**
3. Góc trên-trái cửa sổ Plugins → nút **+ Add** (hoặc "New Plugin")
4. Chọn template **Blank** (C++)
5. Tên: `FurnitureToolkit` → **Create Plugin**
6. UE5 tạo cấu trúc + compile plugin rỗng. Đợi xong.

Cấu trúc tạo ra:
```
Plugins/FurnitureToolkit/
  FurnitureToolkit.uplugin
  Source/FurnitureToolkit/
    FurnitureToolkit.Build.cs
    Public/FurnitureToolkit.h        (module header)
    Private/FurnitureToolkit.cpp     (module impl)
```

---

## BƯỚC 2 — Đóng UE5 + di chuyển file

**Đóng UE5 hoàn toàn trước khi move file.**

Move 2 file (dùng File Explorer):
```
TỪ: Source/Lighting_Mnger/FurnitureFilterLibrary.h
ĐẾN: Plugins/FurnitureToolkit/Source/FurnitureToolkit/Public/FurnitureFilterLibrary.h

TỪ: Source/Lighting_Mnger/FurnitureFilterLibrary.cpp
ĐẾN: Plugins/FurnitureToolkit/Source/FurnitureToolkit/Private/FurnitureFilterLibrary.cpp
```

⚠️ `.h` vào **Public/**, `.cpp` vào **Private/**.

---

## BƯỚC 3 — Sửa API macro trong FurnitureFilterLibrary.h

Mở `Plugins/FurnitureToolkit/Source/FurnitureToolkit/Public/FurnitureFilterLibrary.h` bằng text editor.

Tìm dòng khai báo class, có macro `LIGHTING_MNGER_API`:
```cpp
class LIGHTING_MNGER_API UFurnitureFilterLibrary : public UBlueprintFunctionLibrary
```

Đổi thành `FURNITURETOOLKIT_API`:
```cpp
class FURNITURETOOLKIT_API UFurnitureFilterLibrary : public UBlueprintFunctionLibrary
```

⚠️ Macro API = `{TÊN_MODULE_VIẾT_HOA}_API`. Sai macro → linker error.

Các `#include` trong .h (CoreMinimal, BlueprintFunctionLibrary, .generated.h) **giữ nguyên** — đều đúng.

---

## BƯỚC 4 — Sửa Build.cs của plugin

Mở `Plugins/FurnitureToolkit/Source/FurnitureToolkit/FurnitureToolkit.Build.cs`.

Thay phần dependency thành:
```csharp
using UnrealBuildTool;

public class FurnitureToolkit : ModuleRules
{
    public FurnitureToolkit(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core", "CoreUObject", "Engine"
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "AssetRegistry"
        });
    }
}
```

⚠️ `AssetRegistry` bắt buộc (FurnitureFilterLibrary dùng AssetRegistryModule + IAssetRegistry).

---

## BƯỚC 5 — Revert Build.cs của project

Mở `Source/Lighting_Mnger/Lighting_Mnger.Build.cs`.

Đưa về mặc định (bỏ dependency thừa đã thêm cho furniture):
```csharp
using UnrealBuildTool;

public class Lighting_Mnger : ModuleRules
{
    public Lighting_Mnger(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core", "CoreUObject", "Engine", "InputCore"
        });
    }
}
```

⚠️ Bỏ "RuntimeTransformer", "Slate", "SlateCore" — project module không còn dùng (FurnitureFilterLibrary đã chuyển đi).

---

## BƯỚC 6 — Kiểm tra #include trong FurnitureFilterLibrary.cpp

Mở `Plugins/FurnitureToolkit/Source/FurnitureToolkit/Private/FurnitureFilterLibrary.cpp`.

Đảm bảo include đầu file đúng (đã xác nhận từ trước):
```cpp
#include "FurnitureFilterLibrary.h"
#include "Engine/DataAsset.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "AssetRegistry/IAssetRegistry.h"
```

Nếu có dòng `#include "Lighting_Mnger.h"` (PCH của project) → **xóa** (plugin không dùng PCH project). Nếu không có thì bỏ qua.

---

## BƯỚC 7 — CoreRedirect (chống đứt Blueprint reference)

Mở `Config/DefaultEngine.ini` bằng text editor. Thêm vào cuối file:

```ini
[CoreRedirects]
+ClassRedirects=(OldName="/Script/Lighting_Mnger.FurnitureFilterLibrary",NewName="/Script/FurnitureToolkit.FurnitureFilterLibrary")
```

⚠️ Dòng này báo UE: "class FurnitureFilterLibrary đã chuyển từ module Lighting_Mnger sang FurnitureToolkit". Blueprint node sẽ tự resolve sang module mới, không đứt reference.

Nếu `[CoreRedirects]` đã tồn tại trong file → chỉ thêm dòng `+ClassRedirects=...` vào dưới nó.

---

## BƯỚC 8 — Regenerate + Build

1. Đóng UE5 (nếu đang mở)
2. Right-click `Lighting_Mnger.uproject` → **Generate Visual Studio project files**
3. Mở file `.sln`
4. Configuration → **Development Editor**
5. Solution Explorer → **Games → Lighting_Mnger** → right-click → **Build**
6. Build thành công → mở lại UE5

⚠️ Build configuration phải **Development Editor**. Đóng UE5 trước khi Build (Live Coding conflict).

Nếu build lỗi → copy log gửi tao.

---

## BƯỚC 9 — Verify trong UE5

1. UE5 mở → kiểm tra **Edit → Plugins** → FurnitureToolkit có trong list, Enabled ✓
2. Mở `WBP_FurnitureInventory` → tìm node **Filter Furniture Items**
   - Node hiển thị bình thường (không báo lỗi đỏ)? → CoreRedirect work ✓
   - Node báo lỗi/đỏ? → right-click → **Refresh Node**. Vẫn lỗi → xóa node, kéo lại từ palette (`Filter Furniture Items`)
3. Làm tương tự kiểm tra node **Filter Material Items** (nếu có ở widget khác)

---

## BƯỚC 10 — Test chức năng

PIE → mở Inventory:
- [ ] Filter furniture theo category/search → ra kết quả đúng (C++ FilterFurnitureItems chạy)
- [ ] Filter material theo folder/search → đúng (FilterMaterialItems chạy)
- [ ] Mọi thứ khác (spawn, gizmo, material) vẫn chạy

Nếu filter ra kết quả đúng → plugin migration THÀNH CÔNG.

---

## BƯỚC 11 — Dọn dẹp (tùy chọn)

- Xóa `MyClass.h` + `MyClass.cpp` trong `Source/Lighting_Mnger/` (class rỗng vô dụng). Build lại sau khi xóa.
- KHÔNG xóa `Lighting_Mnger.h/.cpp` (module entry, cần giữ).

---

## SAU KHI XONG — Cập nhật Integration Guide

Integration Guide v1.2 cần sửa:
- **Bước 2:** copy CẢ 2 plugin: `RuntimeTransformer/` + `FurnitureToolkit/`
- **Bước 3-5 (C++ module setup):** XÓA — không cần nữa. Master nhận plugin tự build.
- Thêm: master mở project → UE5 phát hiện plugin C++ → prompt build → Yes (cần Visual Studio trên máy)

→ Integration đơn giản đi rất nhiều.

---

## CHECKLIST TỔNG

- [ ] Backup project
- [ ] Tạo plugin FurnitureToolkit (Blank C++)
- [ ] Move FurnitureFilterLibrary.h → Public/, .cpp → Private/
- [ ] Sửa API macro LIGHTING_MNGER_API → FURNITURETOOLKIT_API
- [ ] Plugin Build.cs: + AssetRegistry
- [ ] Project Build.cs: revert default (bỏ RuntimeTransformer/Slate)
- [ ] Check .cpp includes (xóa PCH project nếu có)
- [ ] CoreRedirect trong DefaultEngine.ini
- [ ] Generate VS files + Build (Development Editor)
- [ ] Verify node Filter Furniture/Material Items
- [ ] Test PIE filter chạy đúng
- [ ] (Tùy chọn) xóa MyClass
- [ ] Cập nhật Integration Guide
