# Sprint 7 — Material Edit v1.2 (slot theo tên + từ điển param + save format v2)
**Version:** 1.5 | **Cập nhật:** 27/08/2026 (tiếp) — S7.G1 ĐÓNG: 5/5 Việc PASS, không deviation. Thêm section "ĐẦU RA S7.G1". Chi tiết đầy đủ: `Data/MaterialSlotService_Reference.md`
**Vị trí roadmap:** sau Sprint 5 DONE + Gate 1.5 Packaged Smoke. Trước Sprint 6 Polish.
**Đầu vào chờ:** kết quả test "P5-liên quan" trong C10 (Sprint 5) → đổ vào S7.G5.
**Thực thi:** Sonnet step-by-step. Mỗi gate = 1 lần test-and-confirm, PASS mới sang gate sau.

---

## 0. LUẬT THỰC THI (Sonnet ĐỌC TRƯỚC — cộng thêm Custom Instructions chung)

1. Tuần tự **S7.G0 → G8**. Mỗi bước dừng: "Làm xong báo tao" + test cụ thể.
2. C++ dán nguyên khối. Lỗi compile → dán error + số dòng, 3-strike → STOP.
3. **[VERIFY]** = soi Blueprint/C++ thật trước khi code, lệch → hỏi cuhoang.
4. **LUẬT RIÊNG SPRINT 7:**
   - **KHÔNG sửa bất kỳ master material nào** (asset đồng nghiệp + Fab, nợ merge). Họ nào thiếu param → không offer tính năng đó cho họ đó, chấm hết.
   - **Mọi lệnh ghi material đi qua MaterialSlotService (C++)** — BP không tự CreateDMI/SetParameter rải rác nữa (luật "1 hàm C++ gộp/ghi" trong Custom Instructions).
   - MI không có trong từ điển → panel chỉ hiện nút đổi vật liệu, KHÔNG hiện slider (chống set param mò — set sai tên là im lặng vô hiệu).
   - Trước G4 (migration): **đóng băng bộ mẫu save + combo định dạng cũ** — copy nguyên thư mục ra `_LegacySpecimens/`. Migrate xong dev-save là hết đường test lại migration.
5. Node mới ngoài danh sách xác nhận → hỏi cuhoang rồi thêm vào node reference.

---

## 1. QUYẾT ĐỊNH ĐÃ CHỐT (03/07/2026 — không bàn lại)

| # | Quyết định |
|---|---|
| D2 | Slot theo **TÊN** trên cả 3 hệ CÙNG LÚC: live apply + EMS + undo snapshot |
| M1 | Nguồn master "hỗn tạp" (RDMtiles ~7 master, 56 Fabric, TRLS, Generic, ±khác) → G0 kiểm kê bằng số, không đoán |
| M2 | User chỉnh: màu, nhám, bóng cơ bản + **bộ thông số gạch** (màu ron, cỡ, hư hại...) — tất cả qua từ điển, thêm 1 control = thêm 1 dòng DataTable. **Pattern gạch** = gate texture riêng (G7). "Đổi basecolor vải" = đổi MI (đã có v1.1), không xây trùng |
| M3 | **GỘP** RowName migration (path→RowName cho actor/EMS/snapshot/combo) vào cùng save format v2 — bổ dọc 1 lần, 1 migration, 1 regression |
| Đ1 | Master UE có param STATIC (nướng lúc compile, runtime bó tay) → G0 phân loại; pattern nếu static → Plan B: swap giữa MI biến thể |
| Đ2 | Slot name có thể rỗng/trùng/auto → G0 quét toàn catalog mesh; chính sách name-thuần vs name+index-fallback chốt bằng SỐ LIỆU |
| Đ3 | Combo phải lưu param chỉnh tay (schema thêm field, additive) — combo là hàng bán tiền |
| Đ4 | Chỉnh param trên slot NGUYÊN BẢN (chưa từng apply MI) → service **MID-on-demand**, lưu bằng PathFallback (pattern Copy/Paste sẵn có) |
| Đ5 | UMG không có color picker runtime → v1 = bảng màu preset + 3 slider; bánh xe màu = backlog |
| Đ6 | `ApplyLoadedMaterialToSlot`: tìm record theo SlotName → sửa tại chỗ, không có → Add (không bao giờ Add trùng). Đổi MI → **CLEAR ParamsJson** slot đó (param cũ vô nghĩa trên MI mới) |
| Đ7 | Factory reset ("Đặt lại vật liệu") **tách khỏi PathFallback**: hàm mới `ResetSlotToAssetDefault` đọc thẳng `GetStaticMesh()->GetStaticMaterials()[idx]`, SetMaterial về gốc + **xóa record**. PathFallback chỉ còn 1 nghĩa: Đ4 + save cũ |
| Đ8 | `ResolveSlotIndex == -1` khi: tên không tồn tại trên mesh hiện tại VÀ HintIndex ngoài range. Mọi hàm ghi return **false** khi -1 |
| Đ9 | **RestoreMyMaterialSlots = chuỗi tuần tự tự gọi**, KHÔNG ForEach + Async (ForEach macro không chờ latent; event param lưu per-actor không per-lần-gọi → aliasing L11 chắc chắn). 1 load bay/1 thời điểm |
| Đ10 | **Restore bước 0 = ResetAllSlotsToAssetDefault** trước khi apply records → idempotent + vá lỗ "undo về MaterialSlots rỗng mà mesh vẫn hiện MID cũ". Đánh đổi: nháy material gốc ~1 frame lúc restore async — chấp nhận v1 |
| Đ11 | `ApplyParamsJsonToSlot` cũng MID-on-demand (case Đ4 restore: slot nguyên bản chỉ có param, chưa có MID) |
| Đ12 | Texture param restore (load texture trong ApplyParamsJsonToSlot kiểu gì) → treo, quyết ở G7 cùng Q2 |
| — | Từ điển = THỰC ĐƠN (khai báo param nào hiện, nhãn Việt, min/max) — KHÔNG chứa giá trị. Giá trị sống trên MID + ParamsJson per slot |
| — | Group MI theo **GetBaseMaterial** (lần tới gốc), không phải parent trực tiếp |
| — | Multi-select: swatch hiện slot của Primary; apply theo tên skip actor thiếu slot + đếm báo |
| — | Replace mesh sang mesh slot trùng tên → **GIỮ material** (hành vi MỚI — v1.1 là reset; ghi DEVIATIONS) |
| — | Reset 2 mức: "Đặt lại thông số" (xóa param, giữ MI) / "Đặt lại vật liệu" (về gốc) |
| — | Texture param lưu object path trong ParamsJson — texture ship theo app, chấp nhận theo tinh thần R5 |
| — | Slider kéo → debounce CaptureSnapshot 0.5s sẵn có, 1 snapshot mỗi lần nhả |
| — | Duo (2 vật liệu trộn): v1 chỉ expose bộ chính A; bộ B = backlog |
| — | Substrate (UE 5.7+ production-ready, 5.8 đã ra 17/06/2026): project cũ nâng engine KHÔNG bị ép bật Substrate; material non-Substrate chạy nguyên. Kiến trúc param-based (service + từ điển) tương thích: master convert Substrate → chỉ cập nhật ParamName trong DT_MaterialParamMap, không refactor service. Không phải rủi ro của Sprint 7. |

**Trả lời 7 câu hỏi (05/07/2026):**
1. `MaterialRowName` String OK — FName so sánh case-insensitive, `FName(*Str)` tra DT an toàn. Giữ String cho JSON.
2. `FindMaterialRowNameByPath`: [VERIFY] signature thật đầu G1. Contract: miss → `MaterialRowName=""` + `MaterialPathFallback=path cũ` → restore đi đường fallback.
3. `MaterialSurvey` có compile vào shipping → guard đầu thân cả 3 hàm: `#if UE_BUILD_SHIPPING return false; #endif`.
4. **[CHỐT 27/08]** Ngưỡng Q1 5% chỉ là số tạm — thật ra 1,56% (40/2559 mesh) nhưng review tay xác nhận CÓ Ý NGHĨA (nhóm sofa/bàn trà/ghế đôn/ghế thư giãn, nhiều vùng vật liệu thật), không bỏ qua theo %. Xem "ĐẦU RA G0 — 27/08/2026" ở trên.
5. JSON casing không lẫn: JsonObjectConverter tự đổi PascalCase field → lowerCamel (kể cả struct lồng). Verify bằng mắt test G1.
6. **[CHỐT 27/08]** `DT_MaterialInstancesCatalog` KHÔNG cần thêm cột `PatternGroup` — Q2 ra DYNAMIC (không phải static), nhánh "thêm cột nhóm pattern" không áp dụng. Xem "ĐẦU RA G0 — 27/08/2026" ở trên.
7. Naming §9 áp cho widget có ≥2 event dùng chung class var (WBP_MaterialParamPanel → `MPP_`); row widget nhỏ tên trần.

**Sơ đồ kiến trúc:**
```
THỰC ĐƠN  DT_MaterialParamMap (C++ row struct — họ master → control nào, nhãn gì, min/max)
              ↓ panel đọc để TỰ DỰNG UI
UI        WBP_MaterialParamPanel (slider/color/texture rows) + slot swatches (theo TÊN)
              ↓ mọi thay đổi
LỚP GHI   MaterialSlotService (C++): apply-theo-tên, MID-on-demand, set param,
DUY NHẤT  serialize/parse JSON, migration từ dữ liệu cũ
              ↓ ghi vào
SỰ THẬT   MID trên mesh (live) + MaterialSlots : Array<FMaterialSlotRecord> trên BP_FurnitureActor
              ↓ cùng 1 mảng đó chảy vào 4 kho
KHO       EMS (SaveGame) | Snapshot (undo) | Combo JSON | (B4 upload sau này)
              ↓ khôi phục
1 ĐƯỜNG   RestoreMyMaterialSlots (custom event trên BP_FurnitureActor) — EMS/undo/combo ĐỀU gọi nó
```

---

## 2. SAVE FORMAT v2 (bổ dọc — M3)

**Struct C++ dùng chung (không mangle tên, BP và C++ cùng đọc):**
```
FMaterialSlotRecord {
  SlotName            : String   ← danh tính chính (D2)
  SlotIndex           : int32    ← fallback khi tên rỗng/trùng (chính sách chốt sau G0)
  MaterialRowName     : String   ← R5, nguồn chính
  MaterialPathFallback: String   ← save cũ / vật liệu gốc ngoài catalog (Đ4)
  ParamsJson          : String   ← {"scalar":{...},"vector":{...},"texture":{...}}
}
```

**Vị trí dữ liệu:**
- `BP_FurnitureActor` + var mới `MaterialSlots : Array<FMaterialSlotRecord>` (SaveGame). Var cũ `MaterialOverrides`/`MaterialParams` GIỮ NGUYÊN (legacy, chỉ để đọc save cũ — không ghi nữa).
- `S_ActorSnapshotData` + field `MaterialSlots` (additive — BP struct chứa được C++ struct).
- `FComboData` item + field `materialSlots` (additive — JsonObjectConverter tự xử; combo cũ thiếu field = mảng rỗng → đường legacy).
- EMS: SaveGame flag lo phần còn lại.

**Migration (1 chiều, lười — chỉ chạy khi gặp):** lúc load, `MaterialSlots` rỗng mà dữ liệu cũ có → `BuildRecordsFromLegacy` (index→tên qua mesh hiện tại; path→RowName qua `FindMaterialRowNameByPath` — hàm CÓ SẴN trong ComboSerializer). Lần save kế tiếp tự ra format mới.

---

# ═══════════════════════════════════════
# S7.G0 — KIỂM KÊ + KHẢO SÁT 3 MẶT (C++ chỉ-đọc, chạy sớm được — độc lập, không đụng code cũ)
# ═══════════════════════════════════════

Mục tiêu: thay "hỗn tạp" (M1) bằng 3 bảng số liệu. Kết quả quyết 2 quyết định treo: **(Q1)** name-thuần hay name+index-fallback; **(Q2)** pattern gạch dynamic hay static.

# S7.G0-prep — RÀ 3 GIẢ ĐỊNH NỀN (bằng mắt trong editor, KHÔNG code, ~15 phút)
Lý do: plan viết 05/07 — trước Gate 1.5 và trước integration project tổng tháng 6 (24/08).
3 giả định dưới nếu lệch thì code G0 sai property/sai hàm ngay bước đầu.

1. [VERIFY] `FindMaterialRowNameByPath` còn tồn tại trong ComboSerializer của project
   tổng tháng 6? Chữ ký còn đúng như plan G3 migration giả định? Lệch → báo, sửa G3 trước.
2. [VERIFY] `DT_MaterialInstancesCatalog`: tên field chứa path CHÍNH XÁC là gì, row struct
   là BP struct hay C++ struct? (BP struct → property mangle GUID → SurveyMasterFamilies
   phải dùng GetAuthoredName. Bài học C++ đọc BP struct đã có.)
3. [VERIFY] Quét sơ danh sách folder `Material/MasterMaterials/` của tháng 6 — đối chiếu
   con số cũ "RDMtiles ~7 master, 56 Fabric, TRLS, Generic" (05/07). Ghi chú sẵn:
   - `M_Glass_Master` từng fail cook (MF_UV → StaticSwitchParameter thiếu cả input A và B)
     → ứng viên diện loại-trừ ở G0.
   - G0 phải search RowName/parent `M_Glass_Master` + `MI_hood_grille_001` trong
     DT_MaterialInstancesCatalog: có trong catalog → loại trừ khỏi Sprint 7; không có →
     user không đụng tới, an toàn.
PASS G0-prep = 3 mục có câu trả lời ghi lại → mới sang G0 Việc 1.

## Việc 1 — Build.cs thêm module
```csharp
PrivateDependencyModuleNames.AddRange(new string[] { "AssetRegistry" });
```

## Việc 2 — file mới `MaterialSurvey.h` (dán nguyên khối)
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MaterialSurvey.generated.h"

/** Công cụ khảo sát Sprint 7 — chỉ ĐỌC, dev-only, giữ lại làm đồ nghề debug lâu dài. */
UCLASS()
class FURNITURETOOLKIT_API UMaterialSurvey : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /** G0a: quét MaterialDT → lần về master GỐC qua AssetRegistry (KHÔNG load asset)
     *  → đếm MI theo họ. Ghi Saved/MaterialSurvey/families.txt */
    UFUNCTION(BlueprintCallable, Category="Material|Survey")
    static bool SurveyMasterFamilies(UDataTable* MaterialDT,
        const FString& PathPropertyName, FString& OutSummary);

    /** G0b: dump toàn bộ param DYNAMIC (scalar/vector/texture) của 1 material.
     *  Param thấy trong editor mà KHÔNG có trong dump = STATIC → runtime không đổi được (Đ1).
     *  Append vào Saved/MaterialSurvey/params_dump.txt */
    UFUNCTION(BlueprintCallable, Category="Material|Survey")
    static bool DumpMaterialParams(UMaterialInterface* Material, FString& OutReport);

    /** G0c: quét slot name mesh trong FurnitureDT, lô [StartIndex, StartIndex+Count).
     *  Load sync theo lô + GC mỗi 30 (dev-only). Append Saved/MaterialSurvey/slots.txt */
    UFUNCTION(BlueprintCallable, Category="Material|Survey")
    static bool SurveyMeshSlotNames(UDataTable* FurnitureDT,
        const FString& MeshPathPropertyName, int32 StartIndex, int32 Count,
        FString& OutSummary);
};
```

## Việc 3 — file mới `MaterialSurvey.cpp` (dán nguyên khối)
```cpp
#include "MaterialSurvey.h"

#include "AssetRegistry/AssetRegistryModule.h"
#include "AssetRegistry/IAssetRegistry.h"
#include "Engine/DataTable.h"
#include "Engine/StaticMesh.h"
#include "Engine/Engine.h"
#include "Materials/Material.h"
#include "Materials/MaterialInterface.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/PackageName.h"
#include "HAL/FileManager.h"
#include "UObject/SoftObjectPath.h"

static FString SurveyDir()
{
    return FPaths::ProjectSavedDir() / TEXT("MaterialSurvey");
}

static FStrProperty* FindStrPropByAuthoredName(const UScriptStruct* RowStruct, const FString& Name)
{
    if (!RowStruct) return nullptr;
    for (TFieldIterator<FProperty> It(RowStruct); It; ++It)
    {
        if (It->GetAuthoredName() == Name)
        {
            return CastField<FStrProperty>(*It);
        }
    }
    return nullptr;
}

/** Lần theo tag "Parent" của AssetRegistry cho tới khi gặp Material gốc. Depth guard 8. */
static FString ResolveRootMaster(const FString& StartObjectPath, IAssetRegistry& AR)
{
    FString Cur = StartObjectPath;
    for (int32 Depth = 0; Depth < 8; ++Depth)
    {
        FAssetData AD = AR.GetAssetByObjectPath(FSoftObjectPath(Cur));
        if (!AD.IsValid()) return TEXT("");

        if (AD.AssetClassPath == UMaterial::StaticClass()->GetClassPathName())
        {
            return AD.AssetName.ToString(); // gặp master gốc
        }
        FString ParentStr;
        if (!AD.GetTagValue(TEXT("Parent"), ParentStr) || ParentStr.IsEmpty())
        {
            return TEXT(""); // Plan B: tag Parent trống → báo cuhoang, chuyển phương án load-theo-lô
        }
        Cur = FPackageName::ExportTextPathToObjectPath(ParentStr);
    }
    return TEXT("");
}

bool UMaterialSurvey::SurveyMasterFamilies(UDataTable* MaterialDT,
    const FString& PathPropertyName, FString& OutSummary)
{
    OutSummary.Empty();
    if (!MaterialDT) { OutSummary = TEXT("MaterialDT null"); return false; }

    FStrProperty* PathProp = FindStrPropByAuthoredName(MaterialDT->GetRowStruct(), PathPropertyName);
    if (!PathProp) { OutSummary = TEXT("Không thấy property: ") + PathPropertyName; return false; }

    IAssetRegistry& AR = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(
        TEXT("AssetRegistry")).Get();

    TMap<FString, int32> FamilyCount;
    int32 Total = 0, Unresolved = 0;

    for (const auto& Pair : MaterialDT->GetRowMap())
    {
        if (!Pair.Value) continue;
        ++Total;
        const FString Path = PathProp->GetPropertyValue_InContainer(Pair.Value);
        if (Path.IsEmpty()) { ++Unresolved; continue; }

        const FString Root = ResolveRootMaster(Path, AR);
        if (Root.IsEmpty()) { ++Unresolved; FamilyCount.FindOrAdd(TEXT("(KHONG_LAN_DUOC)")) += 1; }
        else                { FamilyCount.FindOrAdd(Root) += 1; }
    }

    FamilyCount.ValueSort([](int32 A, int32 B) { return A > B; });
    FString Report = FString::Printf(TEXT("== SURVEY MASTER FAMILIES == Total MI: %d | Unresolved: %d\n"),
        Total, Unresolved);
    for (const auto& F : FamilyCount)
    {
        Report += FString::Printf(TEXT("%5d  %s\n"), F.Value, *F.Key);
    }

    IFileManager::Get().MakeDirectory(*SurveyDir(), true);
    FFileHelper::SaveStringToFile(Report, *(SurveyDir() / TEXT("families.txt")),
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    OutSummary = Report;
    return true;
}

bool UMaterialSurvey::DumpMaterialParams(UMaterialInterface* Material, FString& OutReport)
{
    if (!Material) return false;

    FString R = TEXT("\n==== ") + Material->GetPathName() + TEXT("\n");
    TArray<FMaterialParameterInfo> Infos;
    TArray<FGuid> Ids;

    R += TEXT("-- SCALAR (dynamic — đổi được runtime)\n");
    Material->GetAllScalarParameterInfo(Infos, Ids);
    for (const FMaterialParameterInfo& I : Infos)
    {
        float V = 0.f;
        Material->GetScalarParameterValue(I, V);
        R += FString::Printf(TEXT("  %s | default=%.3f\n"), *I.Name.ToString(), V);
    }

    Infos.Reset(); Ids.Reset();
    R += TEXT("-- VECTOR/MÀU (dynamic)\n");
    Material->GetAllVectorParameterInfo(Infos, Ids);
    for (const FMaterialParameterInfo& I : Infos)
    {
        FLinearColor C = FLinearColor::Black;
        Material->GetVectorParameterValue(I, C);
        R += FString::Printf(TEXT("  %s | default=(%.2f, %.2f, %.2f)\n"),
            *I.Name.ToString(), C.R, C.G, C.B);
    }

    Infos.Reset(); Ids.Reset();
    R += TEXT("-- TEXTURE (dynamic)\n");
    Material->GetAllTextureParameterInfo(Infos, Ids);
    for (const FMaterialParameterInfo& I : Infos)
    {
        UTexture* T = nullptr;
        Material->GetTextureParameterValue(I, T);
        R += FString::Printf(TEXT("  %s | current=%s\n"),
            *I.Name.ToString(), T ? *T->GetName() : TEXT("None"));
    }
    R += TEXT("-- GHI CHÚ: param thấy trong editor mà KHÔNG có ở trên = STATIC (Đ1)\n");

    IFileManager::Get().MakeDirectory(*SurveyDir(), true);
    FFileHelper::SaveStringToFile(R, *(SurveyDir() / TEXT("params_dump.txt")),
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,
        &IFileManager::Get(), FILEWRITE_Append);
    OutReport = R;
    return true;
}

bool UMaterialSurvey::SurveyMeshSlotNames(UDataTable* FurnitureDT,
    const FString& MeshPathPropertyName, int32 StartIndex, int32 Count,
    FString& OutSummary)
{
    OutSummary.Empty();
    if (!FurnitureDT) { OutSummary = TEXT("FurnitureDT null"); return false; }

    FStrProperty* PathProp = FindStrPropByAuthoredName(FurnitureDT->GetRowStruct(), MeshPathPropertyName);
    if (!PathProp) { OutSummary = TEXT("Không thấy property: ") + MeshPathPropertyName; return false; }

    TArray<FName> RowNames = FurnitureDT->GetRowNames();
    const int32 End = FMath::Min(StartIndex + Count, RowNames.Num());
    if (StartIndex < 0 || StartIndex >= End)
    {
        OutSummary = FString::Printf(TEXT("Range sai (tổng %d rows)"), RowNames.Num());
        return false;
    }

    FString Report;
    int32 Scanned = 0, EmptyName = 0, AutoName = 0, MeshWithDup = 0;

    for (int32 i = StartIndex; i < End; ++i)
    {
        uint8* RowData = FurnitureDT->FindRowUnchecked(RowNames[i]);
        if (!RowData) continue;
        const FString MeshPath = PathProp->GetPropertyValue_InContainer(RowData);
        if (MeshPath.IsEmpty()) continue;

        UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *MeshPath); // sync — dev-only, theo lô
        if (!Mesh) { Report += RowNames[i].ToString() + TEXT(" | LOAD FAIL\n"); continue; }

        ++Scanned;
        TSet<FName> Seen;
        bool bDupInMesh = false;
        FString Line = RowNames[i].ToString() + TEXT(" | slots: ");
        for (const FStaticMaterial& SM : Mesh->GetStaticMaterials())
        {
            const FName SlotName = SM.MaterialSlotName;
            const FString S = SlotName.ToString();
            Line += S + TEXT(" ; ");
            if (SlotName.IsNone() || S.IsEmpty()) ++EmptyName;
            else if (S.StartsWith(TEXT("Material")) || S.StartsWith(TEXT("Element")) || S.IsNumeric())
                ++AutoName;
            if (Seen.Contains(SlotName)) bDupInMesh = true;
            Seen.Add(SlotName);
        }
        if (bDupInMesh) { ++MeshWithDup; Line += TEXT("  <<< TRÙNG TÊN TRONG MESH"); }
        Report += Line + TEXT("\n");

        if (Scanned % 30 == 0 && GEngine)
        {
            GEngine->ForceGarbageCollection(true); // pattern batch-30 + GC
        }
    }

    OutSummary = FString::Printf(
        TEXT("Lô [%d..%d): quét %d mesh | slot rỗng %d | tên auto %d | mesh có trùng tên %d"),
        StartIndex, End, Scanned, EmptyName, AutoName, MeshWithDup);
    Report = OutSummary + TEXT("\n") + Report;

    IFileManager::Get().MakeDirectory(*SurveyDir(), true);
    FFileHelper::SaveStringToFile(Report, *(SurveyDir() / TEXT("slots.txt")),
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,
        &IFileManager::Get(), FILEWRITE_Append);
    return true;
}
```

### G0a-0 — Smoke test (BẮT BUỘC trước khi chạy full DT)
1. Đầu `SurveyMasterFamilies` thêm check: `AR.IsLoadingAssets()` == true → prepend cảnh báo `"[WARN] AssetRegistry chưa scan xong — Unresolved có thể là false"` vào OutSummary (không chặn, chỉ báo).
2. Chạy `SurveyMasterFamilies` trên DataTable test 1 dòng (hoặc chấp nhận chạy full nhưng CHỈ đọc kết quả 1 MI RDMtiles biết trước master) → master ra đúng tên → mới tin số liệu full run. Ra `(KHONG_LAN_DUOC)` → tag `Parent` sai/thiếu → STOP, báo Fable, chuyển Plan B load-theo-lô.

### Ghi chú G0c (thêm cuối Việc 3)
`ForceGarbageCollection(true)` trong loop chỉ cắm cờ cho frame sau — trong 1 lần gọi GC KHÔNG nổ. Memory bound thực = batch size mỗi call → giữ `Count ≤ 100`, dòng GC in-loop vô hại nhưng không được tăng batch vì tin nó.

## Chạy khảo sát (chuỗi debug tạm, pattern bDebugTestFolders)
- G0a: `SurveyMasterFamilies(DT_MaterialInstancesCatalog, "MaterialPath")` **[VERIFY authored name property path trong S_MaterialInstancesData]** → mở `families.txt`, dán cho Fable.
- G0b: chọn **1 MI đại diện MỖI HỌ** từ families.txt (Std, Custom, Duo, vải, TRLS, Generic...) → Async Load từng cái (Custom Event) → `DumpMaterialParams` → dán `params_dump.txt`. Mở song song MI trong editor, ghi param nào THẤY trong editor mà THIẾU trong dump (= static, Đ1 — đặc biệt soi pattern gạch).
- G0c: `SurveyMeshSlotNames(DT_FurnitureCatalog, "MeshPath" [VERIFY], 0, 100)` → chạy lát cắt 100 rows/lần tới hết → dán dòng tổng kết các lô.

## ĐẦU RA G0 — 27/08/2026 (kết quả thật, thay 2 nhánh giả định ở trên)

### Q1 — Slot name rỗng/trùng
- Quét 2559/2577 mesh (18 row thiếu StaticMesh, bỏ qua)
- Rỗng: 0% | Trùng trong cùng mesh: 40 mesh (~1,56%)
- Review tay 40 mesh trùng: rơi nhiều vào sofa/bàn trà/ghế đôn/ghế thư giãn —
  đây là nhóm CÓ THẬT nhiều vùng vật liệu khác nhau (vải bọc ≠ khung ≠ mặt đá),
  không phải kiểu "4 chân cùng tên" vô hại.
- **CHỐT: Q1 = ÍT nhưng CÓ Ý NGHĨA** — không chỉ là % thấp bỏ qua được.
  → Kéo theo quyết định thiết kế UI mới, xem mục "Note gửi Opus" (⚠️ không có trong
  nguồn merge 27/08 — chưa được đính kèm, cần cuhoang bổ sung).

### Q2 — CustomTile Map UV+Distribution (pattern gạch)
- Dump 23/23 material đại diện (params_dump.txt)
- Verify chéo bằng mắt trên MI_FL_W_AC_4001_NWM (RDMtiles Custom_Grout):
  toàn bộ nhóm "CustomTile - Pattern Configuration" liên quan chọn mẫu gạch
  đều là Texture param dynamic — khớp dump.
- 2 static switch phụ tìm thấy (Use RandomRotation, Use RandomFlip) — không
  chặn mục tiêu chính "chọn mẫu gạch", ghi nhận backlog nếu sau cần điều khiển.
- **CHỐT: Q2 = DYNAMIC** → G7 dùng texture picker, không cần Plan B variant-MI.

### G0 Việc 1-3 (C++ inventory)
- MaterialSurvey.h/.cpp hoàn thành: SurveyMasterFamilies (G0a), DumpMaterialParams
  (G0b), SurveyMeshSlotNames (G0c) — cả 3 compile PASS trên project tổng tháng 6.
- G0a: 2767 MI / 23 master family (families.txt) — MM_GenericMaterial 54%,
  RM_FabricMaster 928.
- SurveyMeshSlotNames đọc field StaticMesh (Soft Object Reference) thay vì ghép
  MeshFolderPath+RowName — quyết định bền vững, không phụ thuộc RowName có
  mang ý nghĩa filename hay không (đề phòng tương lai đổi RowName thành ID số).

### G0d — khảo sát collision (27/08/2026)
- Quét 2559 mesh: 2555 CTF_USE_DEFAULT (project default = SIMPLE_AND_COMPLEX)
  + 4 CTF_USE_COMPLEX_AS_SIMPLE. **0 mesh SIMPLE_AS_COMPLEX** → FaceIndex trace
  khả thi trên 100% mesh load được. 18 LOAD FAIL = 18 row đã biết (mesh chưa có
  trong project). Chi tiết: `Saved/MaterialSurvey/collision.txt`
- **QUYẾT ĐỊNH CHỐT (Fable, 27/08):** G5 đổi sang hybrid — click-chọn-vùng trên
  mesh là đường chính (trace FaceIndex, KHÔNG per-poly collision đại trà);
  chips thumbnail-material làm đường phụ (slot che khuất/nhỏ + discoverability).
  Slot name = nội bộ 100%, không hiển thị UI.
- **CHƯA CHỐT:** cơ chế đánh dấu slot khóa (hướng LockedSlots blacklist trong DT
  là ứng viên, cuhoang chưa duyệt). Chốt chặn `GetEditableSlots` (G1) cô lập quyết
  định này — v1 trả tất cả slot.

→ **G0 ĐÓNG toàn phần (a/b/c/d). Sang G1.**

---

# ═══════════════════════════════════════
# S7.G1 — NỀN C++: FMaterialSlotRecord + MaterialSlotService
# ═══════════════════════════════════════

**VIỆC 1 TRƯỚC MỌI THỨ — vertical slice TraceSlotUnderCursor. FAIL → STOP sprint.**
API mới đóng băng thêm vào bề mặt G1:
```cpp
// Trace từ chuột → slot dưới con trỏ. bReturnFaceIndex=true + bTraceComplex=true
// → GetMaterialFromCollisionFaceIndex. Trả false nếu không hit/không phải StaticMesh.
static bool TraceSlotUnderCursor(APlayerController* PC, float TraceDistance,
    AActor*& OutActor, int32& OutSlotIndex, FString& OutSlotName);

// Chốt chặn hiển thị/tương tác slot. v1: trả tất cả. Cơ chế lọc chưa chốt —
// mọi thay đổi tương lai chỉ sửa ruột hàm này.
static TArray<int32> GetEditableSlots(UStaticMeshComponent* Mesh, const FString& RowName);

USTRUCT(BlueprintType) struct FPanelSlotInfo {
  UPROPERTY(BlueprintReadOnly) FString SlotName;
  UPROPERTY(BlueprintReadOnly) int32 SlotIndex = -1;
  UPROPERTY(BlueprintReadOnly) FString RowNameResolved; // rỗng nếu tra ngược fail
};
// 1 call cho panel chips: gộp slot mesh + Records + FindMaterialRowNameByPath.
// Chỉ trả slot nằm trong GetEditableSlots.
static TArray<FPanelSlotInfo> GetPanelSlots(UStaticMeshComponent* Mesh,
    const TArray<FMaterialSlotRecord>& Records, UDataTable* MaterialDT);
```
TEST G1 mở rộng: +trace 3 vùng sofa (nhóm 40-dup) ra đúng 3 slot; +GetEditableSlots
trả đủ N; +GetPanelSlots actor có 1 slot applied + 1 slot nguyên bản → cả 2 đúng RowName.
Q9: MIỄN S-Scan (C++ service, không đụng SelectedActors). Routing click (G5) mới cần Q9.

File mới `MaterialSlotService.h/.cpp`. Đây là **LỚP GHI DUY NHẤT** — thân hàm chi tiết Sonnet dán ở đầu gate lúc thực thi (sau khi Q1 chốt chính sách ResolveSlotIndex). Bề mặt API đóng băng từ bây giờ:

```cpp
USTRUCT(BlueprintType)
struct FMaterialSlotRecord { /* như mục 2 — 5 field, tất cả SaveGame */ };

UCLASS()
class FURNITURETOOLKIT_API UMaterialSlotService : public UBlueprintFunctionLibrary
{
public:
  // Tìm index từ tên theo chính sách Q1 (tên unique → index; rỗng/trùng → HintIndex hợp lệ; không → -1)
  // Đ8: -1 khi tên không có trên mesh hiện tại VÀ HintIndex ngoài range → caller ghi phải return false.
  static int32 ResolveSlotIndex(UStaticMeshComponent* Mesh, const FString& SlotName, int32 HintIndex);

  // Apply MI đã load vào slot theo TÊN: CreateDMI + Set + cập nhật Records (UPARAM(ref))
  // Đ6: record theo SlotName — sửa tại chỗ hoặc Add, không Add trùng. Đổi MI → clear ParamsJson của slot.
  static bool ApplyLoadedMaterialToSlot(UStaticMeshComponent* Mesh,
      UPARAM(ref) TArray<FMaterialSlotRecord>& Records,
      const FString& SlotName, int32 HintIndex,
      UMaterialInterface* LoadedMI, const FString& RowName, const FString& PathFallback);

  // MID-on-demand (Đ4): slot chưa có MID → tạo từ material hiện tại + ghi PathFallback vào record
  static bool SetSlotScalarParam (UStaticMeshComponent* Mesh, UPARAM(ref) TArray<FMaterialSlotRecord>& Records,
      const FString& SlotName, int32 HintIndex, FName ParamName, float Value);
  static bool SetSlotVectorParam (…, FLinearColor Value);
  static bool SetSlotTextureParam(…, UTexture* Value);

  // Reset mức 1: xóa mọi param override, GIỮ MI (ClearParameterValues + xóa ParamsJson trong record)
  static bool ClearSlotParams(UStaticMeshComponent* Mesh, UPARAM(ref) TArray<FMaterialSlotRecord>& Records,
      const FString& SlotName, int32 HintIndex);

  // Đ7: factory reset — đọc default từ StaticMesh asset, xóa record. KHÔNG dùng PathFallback.
  static bool ResetSlotToAssetDefault(UStaticMeshComponent* Mesh,
      UPARAM(ref) TArray<FMaterialSlotRecord>& Records,
      const FString& SlotName, int32 HintIndex);

  // Đ10: reset TOÀN BỘ slot về default asset (bước 0 của restore). Không đụng Records.
  static bool ResetAllSlotsToAssetDefault(UStaticMeshComponent* Mesh);

  // Kho ↔ chuỗi
  static FString SerializeSlotRecords(const TArray<FMaterialSlotRecord>& Records);
  static TArray<FMaterialSlotRecord> ParseSlotRecords(const FString& Json);

  // Restore: MI load ở BP (async, R1) rồi gọi 2 hàm này
  // Đ11: MID-on-demand như SetSlotXParam. Đ12: texture param — cách load chốt ở G7.
  static bool ApplyParamsJsonToSlot(UStaticMeshComponent* Mesh, const FString& ParamsJson,
      const FString& SlotName, int32 HintIndex);

  // Migration (M3): dữ liệu cũ theo index → records theo tên; path → RowName qua FindMaterialRowNameByPath
  static TArray<FMaterialSlotRecord> BuildRecordsFromLegacy(UStaticMeshComponent* Mesh,
      const TArray<FString>& OldOverridesByIndex, UDataTable* MaterialDT);
};
```

Ghi chú thiết kế đã chốt: Records truyền **UPARAM(ref)** — BP_FurnitureActor giữ biến, C++ sửa tại chỗ, không reflection mò tên biến BP. Set param sẽ **kiểm param tồn tại trước khi set** (GetAllXParameterInfo chứa tên đó không) → trả false thay vì im lặng vô hiệu — trị tận gốc bẫy "slider kéo mesh đứng im".

- Logging: UE_LOG category riêng `LogMaterialSlot`. Mỗi lệnh ghi (apply/set param/reset/
  restore) log: Actor label + SlotName + kết quả resolve/apply (true/false + lý do ngắn).
  KHÔNG xây telemetry thêm — tool desktop, log local đủ.

TEST G1 (chuỗi debug, chưa UI): apply MI theo tên vào 1 actor → đúng slot; SetScalar param có thật → đổi trên mesh; param bịa → trả **false**; slot nguyên bản chưa MID → SetVector vẫn ăn (MID-on-demand) + record có PathFallback; Serialize → Print JSON đọc được; Parse ngược → so khớp; **(v1.1)** Apply MI lần 2 cùng slot → Records vẫn 1 record/slot (không trùng) + ParamsJson đã clear; **(v1.1)** ResetSlotToAssetDefault → material về gốc + record biến mất.

## ĐẦU RA S7.G1 — 27/08/2026 (5/5 Việc PASS, không deviation)

| Việc | Nội dung | Test | Kết quả |
|---|---|---|---|
| 1 | `TraceSlotUnderCursor` (vertical slice, gate-trong-gate) | 4 vùng trace (`Bed_SplitHeadboard_Soft_17236`) đối chiếu Static Mesh Editor | PASS 4/4 |
| 2 | `FMaterialSlotRecord` + 10 hàm ghi (Resolve/Apply/SetScalar/SetVector/SetTexture/Clear/Reset×2/Serialize/Parse) | 7 mục TEST G1 (apply, scalar thật/bịa, serialize round-trip, dedupe, reset, MID-on-demand+PathFallback) | PASS 7/7 |
| 3 | `GetEditableSlots` v1 (trả tất cả slot) | Length khớp số dòng Materials tab thật | PASS (8/8) |
| 4 | `FPanelSlotInfo` + `GetPanelSlots` | 8/8 slot, RowName resolve đúng cả 2 nhánh (Records có sẵn + tra ngược qua `FindMaterialRowNameByPath`) | PASS 8/8 |
| 5 | Logging + tổng hợp | `LogMaterialSlot` phủ mọi hàm (Actor\|Slot\|lý do khi false) — không cần code thêm | PASS |

Build xanh xuyên suốt cả 4 lần thêm code (Việc 1→2→3→4), không strike nào, không compile error.
**Deviation so với plan v1.4: KHÔNG CÓ** — API surface đóng băng khớp 100% code thật đã build,
không phát sinh field/hàm ngoài kế hoạch (KP2 tuân thủ). Chi tiết struct + 14 hàm đầy đủ:
`Data/MaterialSlotService_Reference.md`. Bài học node flow: `Blueprint_Logic_NodeFlow.md`
mục L-NEW-7.

→ **G1 ĐÓNG (27/08/2026). Sang G2.**

---

# ═══════════════════════════════════════
# S7.G2 — REROUTE ĐƯỜNG LIVE (inventory đi qua service)
# ═══════════════════════════════════════

**[VERIFY]** trước khi sửa: `WBP_SlotSwatch` variables hiện có; `LoadAndApplyMaterial` bản mới nhất (doc v1.1 vs thực tế); chỗ Copy/Paste material.

1. `RefreshSlotSwatches`: đã đọc `GetMaterialSlotNames` sẵn → thêm SET `SlotName` vào từng swatch; chọn swatch SET cả `SelectedSlotName` + `SelectedSlotIndex` (Hint).
2. `LoadAndApplyMaterial` (Custom Event, async giữ nguyên): Completed → Cast MI → **`ApplyLoadedMaterialToSlot(FurnitureMesh, TargetActor.MaterialSlots, SelectedSlotName, SelectedSlotIndex, MI, PendingRowName, "")`** → debounce CaptureSnapshot như cũ. Bỏ CreateDMI/SetArrayElem rời rạc.
3. Multi-apply (E1): ForEach SelectedActors → gọi service theo TÊN — actor thiếu slot → service trả false → đếm; xong Print "Áp cho X/Y đồ".
4. Copy/Paste material: paste đổi sang gọi service (copy giữ nguyên).
5. Reset Slot/Reset All đổi sang: mức 2 = `ResetSlotToAssetDefault` (Đ7 — đọc StaticMesh asset, KHÔNG đụng PathFallback), mức 1 = `ClearSlotParams` (nút mới chưa cần UI — G5).

TEST G2: toàn bộ test Change Material v1.1 cũ chạy lại PASS (apply, swatch thumbnail, multi 3 đồ, copy/paste) + `MaterialSlots` trên actor nhìn thấy record đúng (debug Print JSON).

→ **Làm xong báo tao.**

---

# ═══════════════════════════════════════
# S7.G3 — MỘT ĐƯỜNG RESTORE + 4 KHO (EMS, snapshot, combo) + MIGRATION
# ═══════════════════════════════════════

**ĐÓNG BĂNG MẪU TRƯỚC:** copy `Saved/SaveGames` + `Saved/Combos` → `_LegacySpecimens/` (Explorer). Chưa copy → KHÔNG được đi tiếp.

**[VERIFY]:** flow `ActorLoaded` hiện tại (restore MaterialOverrides thế nào); `S_ActorSnapshotData` fields; `FComboData` item struct + `F_ApplyMaterialOverrides`; chỗ CaptureSnapshot đọc material.

```
Q8: 2 Custom Event chuỗi | IsValid Mesh + IsValid loaded asset ✓ |
L2: mọi nhánh (kể cả load fail) đều tới idx++ → chain không kẹt ✓ |
Latent trong Custom Event ✓ (không Function) |
6A: reset-trước-apply → idempotent, gọi lại nhiều lần (EMS+snapshot+combo) không cộng dồn,
    undo về Records rỗng vẫn trả mesh về nguyên bản ✓
```

1. **RestoreMyMaterialSlots** (Custom Event trên BP_FurnitureActor — MỘT đường duy nhất, chuỗi TUẦN TỰ Đ9):
```
RestoreMyMaterialSlots ▶→
  Branch(MaterialSlots.Length == 0 AND MaterialOverrides cũ có dữ liệu)   ← đường LEGACY
    True ▶→ BuildRecordsFromLegacy(...) ●→ SET MaterialSlots
  (merge)
  ▶→ ResetAllSlotsToAssetDefault(FurnitureMesh)        ← Đ10, bước 0
  ▶→ SET Rst_SlotIdx = 0
  ▶→ Rst_LoadNextSlot

Rst_LoadNextSlot (Custom Event) ▶→
  Branch(Rst_SlotIdx >= MaterialSlots.Length)
    True → [xong]
    False ▶→ MaterialSlots Get(Rst_SlotIdx) ●→ SET Rst_CurRecord   ← temp var, không đọc pure 2 lần
      ▶→ RowName != "" → tra DT lấy path; rỗng → PathFallback
      ▶→ Async Load Asset → Completed
        ▶→ Branch(IsValid loaded asset)                 ← load fail KHÔNG được kẹt chain
          True ▶→ ApplyLoadedMaterialToSlot ▶→ ApplyParamsJsonToSlot
        (merge) ▶→ SET Rst_SlotIdx = Rst_SlotIdx + 1 ▶→ Rst_LoadNextSlot   ← tự gọi
```
Class var mới trên BP_FurnitureActor: `Rst_SlotIdx : int`, `Rst_CurRecord : FMaterialSlotRecord` (KHÔNG SaveGame).
Ghi chú: nếu test 6A lộ double-apply do 2 lần gọi chồng nhau giữa chừng → thêm `Rst_Generation` counter (mỗi lần gọi ++, Completed check khớp mới chạy tiếp). Chỉ thêm KHI test fail, không thêm trước (KP2).

2. EMS `ActorLoaded` → gọi RestoreMyMaterialSlots (thay code restore cũ).
3. Snapshot: `S_ActorSnapshotData` + field MaterialSlots; Capture copy từ actor; Restore sau khi spawn+mesh load → gọi RestoreMyMaterialSlots.
4. Combo: `FComboData` item + `materialSlots`; SaveComboFromSelection điền từ actor; SpawnCombo → RestoreMyMaterialSlots (F_ApplyMaterialOverrides cũ thành legacy bên trong nó).

TEST G3 — ma trận:
| # | Case | Kỳ vọng |
|---|---|---|
| 1 | Save MỚI (đổi MI + chỉnh param) → Load | đúng MI + đúng param |
| 2 | Save CŨ (specimen) → Load | material đúng như trước (migration êm) |
| 3 | Case 2 → Save lại → Load lại | giờ là format mới, vẫn đúng |
| 4 | Chỉnh param → Undo → Redo | param nhảy đúng theo snapshot |
| 5 | Combo CŨ (specimen) spawn | material đúng đường legacy |
| 6 | Đổi MI + nhuộm màu → lưu combo → spawn | **màu giữ nguyên** (Đ3 — lỗ đã vá) |
| 7 | Slot nguyên bản chỉnh param → save/load/undo | PathFallback sống đúng (Đ4) |
| 8 | Apply MI → CaptureSnapshot → **Undo** | mesh về material NGUYÊN BẢN (Đ10 — lỗ đã vá) |
| 9 | Actor ≥2 slot khác material → save/load | CẢ HAI slot đúng, không slot cuối "thắng" |
| 10 | Stress restore chồng nhau: spam Undo trong lúc EMS ActorLoaded còn đang restore; spawn combo rồi Undo ngay lập tức | Không crash, không material lệch, không cộng dồn record. Nếu FAIL → mới thêm generation guard (Rst_Generation) — KP2, không thêm trước |

**Hợp đồng với G5:** highlight flash tạm (click-chọn vùng) không được lọt vào snapshot —
G5 guard phía nó (flash trả material xong mới cho capture). G3 không code gì thêm; G8
regression thêm case kiểm hợp đồng này.

→ **Làm xong báo tao + bảng 10 case.**

---

# ═══════════════════════════════════════
# S7.G4 — REGRESSION NỀN P5 (mục tiêu gốc của slot-theo-tên)
# ═══════════════════════════════════════

1. Re-import 1 mesh test đổi thứ tự/tên slot **[VERIFY cách re-import an toàn — hỏi cuhoang mesh nào]** → actor cũ trong save load lại: material bám đúng slot theo TÊN (trước đây theo index là lệch).
2. Replace mesh A→B: slot trùng tên → **GIỮ material** (hành vi mới, ghi DEVIATIONS); slot không trùng → nguyên bản của B.
3. Đối chiếu dữ liệu C10 ("P5-liên quan") — case nào C10 ghi fail giờ phải PASS.
4. Multi-select mesh khác chủng loại → apply theo tên → skip + đếm đúng.

→ **PASS = nền xong. Từ đây trở đi chỉ là UI + dữ liệu.**

---

# ═══════════════════════════════════════
# S7.G5 — ĐỘNG CƠ PANEL TỪ ĐIỂN (UI engine)
# ═══════════════════════════════════════

1. **DT_MaterialParamMap** — row struct C++ `FMaterialParamMapRow` (không mangle):
```
MasterKey (String — tên master gốc từ G0a) | ControlType (Scalar/Color/Texture)
ParamName (Name — tên THẬT từ G0b) | LabelVN | MinValue | MaxValue | SortOrder | bAdvanced
```
2. C++ helper: `GetControlsForMaterial(ParamMapDT, MaterialInterface)` — GetBaseMaterial → match MasterKey → trả mảng row (sorted).
3. Widgets: `WBP_ParamSliderRow` (label + Slider + số); `WBP_ParamColorRow` (label + 8 swatch preset + 3 slider R/G/B — Đ5). Cả hai: OnValueChanged → dispatcher → panel → **service SetSlotParam** → debounce capture (1 snapshot/lần nhả).
4. `WBP_MaterialParamPanel`: nhận (TargetActor soft ref, SlotName) — R2/R3; build rows từ helper; **material không match từ điển → panel trống + dòng "Vật liệu này chỉ đổi được mẫu"**; 2 nút Reset ("Đặt lại thông số" / "Đặt lại vật liệu"); Event Destruct clear refs (R4).
5. Gắn vào tab Material dưới slot swatches **[VERIFY layout chỗ đặt]**.

TEST G5 (từ điển tạm 2 dòng test): slider đổi mesh live; kéo giữ → 1 snapshot lúc nhả; MI ngoài từ điển → panel trống đúng; multi-select → param áp cả cụm theo tên.

→ **Làm xong báo tao.**

---

# ═══════════════════════════════════════
# S7.G6 — ĐIỀN TỪ ĐIỂN (dữ liệu thật từ G0) + BỘ TEST T7
# ═══════════════════════════════════════

Điền DT_MaterialParamMap theo `params_dump.txt`: mọi họ (màu chính, nhám/độ bóng nếu có param dynamic); RDMtiles (màu ron, cỡ gạch, bevel, độ hư — đúng tên thật, M2); vải (color/fuzz/normal strength/UV scale); Duo chỉ bộ A. Nhãn tiếng Việt do cuhoang duyệt từng dòng (bảng gửi trước khi nhập).

Chạy bộ test sẵn **T7.1–T7.5** (07_Testing_Strategy): color live | slider roughness | multi 3 đồ | reset | param save/load/undo qua UI.

→ **Làm xong báo tao + bảng T7.**

---

# ═══════════════════════════════════════
# S7.G7 — PATTERN GẠCH (texture control) — gate TÁCH ĐƯỢC, trễ dời không vỡ
# ═══════════════════════════════════════

Theo Q2 từ G0b:
- **Dynamic** → `DT_TilePatterns` {tên, texture soft ref, thumbnail} + `WBP_TexturePickerRow` (grid ~40 mẫu, Lazy Image) → `SetSlotTextureParam`. Lưu path texture trong ParamsJson (đã chốt).
- **Static** → Plan B: pattern = **swap giữa MI biến thể** (UI giống hệt — grid mẫu, hành động = ApplyMaterial MI khác); hoặc defer sang backlog nếu số MI biến thể chưa đủ.

→ **Làm xong báo tao.**

---

# ═══════════════════════════════════════
# S7.G8 — REGRESSION TỔNG + VRAM + DOCS
# ═══════════════════════════════════════

- Chuỗi 12 bước: apply → param → multi → combo save/spawn → EMS save/load → undo ×5 → replace mesh → reset 2 mức → save cũ load → reload.
- `stat rhi` 4 mốc (baseline / sau 20 lần đổi MI / sau 50 lần kéo slider / sau undo chuỗi) — MID không phình theo số lần chỉnh (mỗi slot 1 MID tái dùng, không tạo mới mỗi kéo). Ghi số vào DEVIATIONS.
- Thêm đo (v1.1): chuỗi undo ×5 trên actor có MID — reset-rồi-áp tạo MID mới mỗi restore, MID cũ phải được GC (không tích lũy). Ghi số vào DEVIATIONS.
- Specimen cũ chạy lại lần cuối.

## DOC UPDATES SAU SPRINT
`Session_State` + `PROGRESS` (S7 DONE); `DEVIATIONS` — 4 dòng soạn sẵn: (1) *Replace mesh đổi hành vi: giữ material khi slot trùng tên (P5) — v1.1 là reset*; (2) *Save format v2 MaterialSlots additive, fields cũ thành legacy read-only*; (3) *Q1/Q2 chốt theo số liệu G0: ...*; (4) *RestoreMyMaterialSlots đổi từ ForEach+Async (plan v1.0) sang chuỗi tuần tự + reset bước 0 (Đ9/Đ10) — lý do: aliasing L11 + lỗ undo-về-rỗng*; tạo `MaterialSlotService_Reference.md` + `MaterialSurvey_Reference.md`; bump `ChangeMaterial.md` → v2.0, `WBP_FurnitureInventory.md`, `BP_FurnitureActor.md`, snapshot/EMS docs, `Combo` schema doc; node reference thêm node mới phát sinh (cuhoang xác nhận từng cái).

## BACKLOG SAU SPRINT 7
Bánh xe màu HSV | Duo bộ B | chế độ Advanced (bAdvanced=true) | slot highlight trên mesh (backlog cũ Material_CopyPaste) | async encode texture list | pattern picker polish.

**Thêm 26/08/2026 (nguồn: khảo sát Quiet Runtime Editor, Fab):**
| Bánh xe màu runtime: khả thi (QRE đã build bằng UMG) — v1 giữ preset + 3 slider (Đ5) |
| Undo history persist ra file (undo sống qua session): ghi nhận, không làm — đắt (file
  phình + migration), chưa có nhu cầu user |
| Router pattern (các manager nói chuyện qua trung gian GameplayTag): cân nhắc ở phase
  Refactor NẾU coupling bắt đầu đau — không refactor giữa sprint |
