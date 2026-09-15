# MaterialSlotService — C++ Blueprint Function Library Reference
**Nguồn:** `DELTA 27/08/2026 — S7.G1 MaterialSlotService (Sonnet execution, Fable task card)`, task card `S7.G1 MaterialSlotService | Fable → Sonnet | 27/08/2026`. As-built thật — 5/5 Việc PASS, build xanh xuyên suốt, KHÔNG deviation so với API đóng băng trong `Plans/Sprint7_MaterialEdit_Plan_v1.1.md` mục S7.G1.
**Tạo:** 27/08/2026

> File này là TÀI LIỆU THAM KHẢO — liệt kê function signature + hành vi thật từ delta as-built.
> Struct đầy đủ xem bên dưới (chưa tách sang `Data_Structures.md` — cân nhắc khi có nhu cầu).

---

## Struct

### FMaterialSlotRecord (USTRUCT BlueprintType, 5 field, tất cả `SaveGame`)

| Field | Kiểu | Ý nghĩa |
|---|---|---|
| SlotName | FString | danh tính chính (D2) |
| SlotIndex | int32 | fallback khi tên rỗng/trùng (Q1) |
| MaterialRowName | FString | RowName trong `DT_MaterialInstancesCatalog` (R5) |
| MaterialPathFallback | FString | Đ4 (MID-on-demand) / save cũ |
| ParamsJson | FString | `{"scalar":{...},"vector":{...},"texture":{...}}` |

### FPanelSlotInfo (USTRUCT BlueprintType, 3 field, BlueprintReadOnly, KHÔNG SaveGame)

SlotName (FString) · SlotIndex (int32) · RowNameResolved (FString, rỗng nếu tra ngược fail).

---

## Class: UMaterialSlotService
**Plugin:** FurnitureToolkit | Base: `UBlueprintFunctionLibrary`
**Build.cs:** không đổi (`Json`/`JsonUtilities` đã có sẵn từ Sprint 5 qua `ComboSerializer`).

**Log category:** `LogMaterialSlot`. Mọi hàm trả `false` đều log 1 dòng format
`HàmTên|Actor|Slot|lý do` (hoặc `HàmTên|Actor|-|lý do` khi lỗi trước khi resolve được slot).

**Helper nội bộ (file-local, không expose Blueprint):** `DescribeOwner`, `FindOrAddRecord`,
`EnsureSlotMID` (MID-on-demand dùng chung 4 chỗ), `ParseParamsJson`/`StringifyParamsJson`/
`GetOrAddSubObject` (JSON nested scalar/vector/texture).

### TraceSlotUnderCursor(PC, TraceDistance, OutActor, OutSlotIndex, OutSlotName) → bool
```cpp
static bool TraceSlotUnderCursor(APlayerController* PC, float TraceDistance,
    AActor*& OutActor, int32& OutSlotIndex, FString& OutSlotName);
```
Channel `ECC_Camera`, tự set `bTraceComplex=true` + `bReturnFaceIndex=true` trong C++ (node BP
không làm được). Trả `false` nếu không hit / không phải StaticMesh.
Test: 4 vùng trace (`Bed_SplitHeadboard_Soft_17236`) đối chiếu Static Mesh Editor — PASS 4/4.

### ResolveSlotIndex(Mesh, SlotName, HintIndex) → int32
```cpp
static int32 ResolveSlotIndex(UStaticMeshComponent* Mesh, const FString& SlotName, int32 HintIndex);
```
Tên unique → index; rỗng/trùng → HintIndex hợp lệ; không → `-1` (Đ8).

### ApplyLoadedMaterialToSlot(Mesh, Records&, SlotName, HintIndex, LoadedMI, RowName, PathFallback) → bool
```cpp
static bool ApplyLoadedMaterialToSlot(UStaticMeshComponent* Mesh,
    UPARAM(ref) TArray<FMaterialSlotRecord>& Records,
    const FString& SlotName, int32 HintIndex,
    UMaterialInterface* LoadedMI, const FString& RowName, const FString& PathFallback);
```
Đ6: sửa record tại chỗ theo tên, không bao giờ Add trùng; đổi MI → clear `ParamsJson`.

### SetSlotScalarParam / SetSlotVectorParam / SetSlotTextureParam(Mesh, Records&, SlotName, HintIndex, ParamName, Value) → bool
```cpp
static bool SetSlotScalarParam (UStaticMeshComponent* Mesh, UPARAM(ref) TArray<FMaterialSlotRecord>& Records,
    const FString& SlotName, int32 HintIndex, FName ParamName, float Value);
static bool SetSlotVectorParam (…, FLinearColor Value);
static bool SetSlotTextureParam(…, UTexture* Value);
```
Đ4 MID-on-demand; kiểm `GetAllXParameterInfo` chứa `ParamName` trước khi set — không có → trả
`false` (trị tận gốc bẫy "slider kéo mesh đứng im").

### ClearSlotParams(Mesh, Records&, SlotName, HintIndex) → bool
```cpp
static bool ClearSlotParams(UStaticMeshComponent* Mesh, UPARAM(ref) TArray<FMaterialSlotRecord>& Records,
    const FString& SlotName, int32 HintIndex);
```
Reset mức 1 — `ClearParameterValues` + xóa `ParamsJson`, GIỮ MI.

### ResetSlotToAssetDefault(Mesh, Records&, SlotName, HintIndex) → bool
```cpp
static bool ResetSlotToAssetDefault(UStaticMeshComponent* Mesh,
    UPARAM(ref) TArray<FMaterialSlotRecord>& Records,
    const FString& SlotName, int32 HintIndex);
```
Đ7 — factory reset, đọc default từ StaticMesh asset, xóa record. KHÔNG dùng PathFallback.

### ResetAllSlotsToAssetDefault(Mesh) → bool
```cpp
static bool ResetAllSlotsToAssetDefault(UStaticMeshComponent* Mesh);
```
Đ10 — reset TOÀN BỘ slot về default asset (bước 0 của restore). KHÔNG đụng Records.

### SerializeSlotRecords(Records) → FString / ParseSlotRecords(Json) → Records
```cpp
static FString SerializeSlotRecords(const TArray<FMaterialSlotRecord>& Records);
static TArray<FMaterialSlotRecord> ParseSlotRecords(const FString& Json);
```
JSON array phẳng (không wrapper key), field camelCase tự động qua `FJsonObjectConverter`.

### ApplyParamsJsonToSlot(Mesh, ParamsJson, SlotName, HintIndex) → bool
```cpp
static bool ApplyParamsJsonToSlot(UStaticMeshComponent* Mesh, const FString& ParamsJson,
    const FString& SlotName, int32 HintIndex);
```
Đ11 MID-on-demand như `SetSlotXParam`. Đ12: texture param trong `ParamsJson` **CHỈ ghi log,
chưa load** — cơ chế load texture lúc restore chốt ở G7.

### BuildRecordsFromLegacy(Mesh, OldOverridesByIndex, MaterialDT) → Records
```cpp
static TArray<FMaterialSlotRecord> BuildRecordsFromLegacy(UStaticMeshComponent* Mesh,
    const TArray<FString>& OldOverridesByIndex, UDataTable* MaterialDT);
```
M3 — migration 1 chiều: index cũ → tên qua mesh hiện tại; path → RowName qua
`UComboSerializer::FindMaterialRowNameByPath` (fail → rỗng, giữ nguyên PathFallback).

### GetEditableSlots(Mesh, RowName) → Array\<int32\>
```cpp
static TArray<int32> GetEditableSlots(UStaticMeshComponent* Mesh, const FString& RowName);
```
v1: trả TẤT CẢ slot. `RowName` chưa dùng — cơ chế lọc (LockedSlots blacklist trong DataTable là
ứng viên, **chưa chốt**, cuhoang chưa duyệt) để ngỏ tham số này (KP2 — chốt chặn cô lập ở đây,
mọi thay đổi tương lai chỉ sửa ruột hàm, không đổi chữ ký/call site).

### GetPanelSlots(Mesh, Records, MaterialDT) → Array\<FPanelSlotInfo\>
```cpp
static TArray<FPanelSlotInfo> GetPanelSlots(UStaticMeshComponent* Mesh,
    const TArray<FMaterialSlotRecord>& Records, UDataTable* MaterialDT);
```
Gộp `GetEditableSlots` + Records + tra ngược path→RowName cho panel chips. Chỉ trả slot nằm
trong `GetEditableSlots`. 1 slot lạ không giết cả panel (per-slot fail, không throw toàn hàm).

---

## Test G1 (5/5 Việc PASS toàn bộ, 27/08/2026)

| Việc | Nội dung | Test | Kết quả |
|---|---|---|---|
| 1 | `TraceSlotUnderCursor` (vertical slice, gate-trong-gate) | 4 vùng trace (`Bed_SplitHeadboard_Soft_17236`) đối chiếu Static Mesh Editor | PASS 4/4 |
| 2 | `FMaterialSlotRecord` + 10 hàm ghi (Resolve/Apply/SetScalar/SetVector/SetTexture/Clear/Reset×2/Serialize/Parse) | 7 mục TEST G1 (apply, scalar thật/bịa, serialize round-trip, dedupe, reset, MID-on-demand+PathFallback) | PASS 7/7 |
| 3 | `GetEditableSlots` v1 (trả tất cả slot) | Length khớp số dòng Materials tab thật | PASS (8/8) |
| 4 | `FPanelSlotInfo` + `GetPanelSlots` | 8/8 slot, RowName resolve đúng cả 2 nhánh (Records có sẵn + tra ngược qua `FindMaterialRowNameByPath`) | PASS 8/8 |
| 5 | Logging + tổng hợp | `LogMaterialSlot` phủ mọi hàm (Actor\|Slot\|lý do khi false) — không cần code thêm | PASS |

Build xanh xuyên suốt cả 4 lần thêm code (Việc 1→2→3→4), không strike nào, không compile error.
**Deviation so với plan v1.4: KHÔNG CÓ** — API surface đóng băng khớp 100% code thật đã build.

---

## Lưu ý tích hợp

- Plugin: `FurnitureToolkit` — cùng plugin với `FurnitureFilterLibrary`, `UComboSerializer`, `UComboThumbnail`.
- Migration path (`BuildRecordsFromLegacy`) dùng lại `UComboSerializer::FindMaterialRowNameByPath` có sẵn — không viết lại reflection lookup.
- Chưa có Blueprint debug chain nào được K2Node-export verify chính thức — xem
  `Blueprint_Logic_NodeFlow.md` mục L-NEW-7 cho bài học rút ra, KHÔNG phải node flow verified.

---

## UMaterialParamMap (S7G7T1, 15/09/2026)

> 📌 **[CHỨA AS-BUILT]** — Nguồn: delta `DELTA — S7G7T1 AS-BUILT + Backlog Static Switch`
> (Opus, 15/09/2026), plan gốc `Sprints/Sprint7/15-09-2026_S7G7_T1-T5_ExecutionPlan.md` mục 2.
> **S7G7T1 ĐÓNG — PASS 4/4.** Class RIÊNG (`MaterialParamMap.h/.cpp`), KHÔNG nhét vào
> `MaterialSlotService` — file reference này giờ phủ 2 class.

### EMaterialParamControl (UENUM BlueprintType)
```cpp
enum class EMaterialParamControl : uint8 { Scalar, Color };   // Texture để G9 thêm
```

### FMaterialParamControlRow (USTRUCT BlueprintType : FTableRowBase) — 6 field
| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `BaseMaterial` | `TSoftObjectPtr<UMaterialInterface>` | Khóa tra — so bằng CON TRỎ sau `LoadSynchronous`, KHÔNG bằng path string (xem lý do dưới) |
| `ParamName` | `FName` | Phải trùng tên param thật trên master. T1 KHÔNG kiểm tên — sai tên lộ ở T4 (`SetSlotScalarParam` trả `false`) |
| `ControlType` | `EMaterialParamControl` | Mặc định `Scalar` |
| `LabelVI` | `FText` | Nhãn tiếng Việt hiển thị trên row |
| `MinValue` | `float` (default 0) | Scalar dùng, Color bỏ qua |
| `MaxValue` | `float` (default 1) | Scalar dùng, Color bỏ qua |

### GetControlsForMaterial(SlotMaterial, ParamMapDT) → Array\<FMaterialParamControlRow\>
```cpp
// class UMaterialParamMap : public UBlueprintFunctionLibrary
static TArray<FMaterialParamControlRow> GetControlsForMaterial(
    UMaterialInterface* SlotMaterial, UDataTable* ParamMapDT);
```
Gom mọi row trong `ParamMapDT` có `BaseMaterial` khớp `SlotMaterial->GetBaseMaterial()`. MI ngoài
từ điển → mảng rỗng.

**Cách so sánh chốt — CON TRỎ UObject, KHÔNG path string:**
```cpp
UMaterial* SlotBase = SlotMaterial->GetBaseMaterial();
UMaterial* RowBase = Cast<UMaterial>(Row->BaseMaterial.LoadSynchronous());
if (RowBase == SlotBase) OutRows.Add(*Row);
```
Lý do (bằng chứng thật): bản đầu so `GetPathName()` string → FAIL với MID (MID bọc quanh MI có
path KHÁC path MI gốc). So con trỏ sau `LoadSynchronous` → cả MI tĩnh lẫn MID đều resolve về CÙNG
1 `UMaterial` base → `==` đúng. Cả 2 option string (path lẫn `GetFName()`) đều bị loại.

**Nợ nhẹ (không chặn T2):** gọi `LoadSynchronous` mỗi row trong loop — vô hại với từ điển 2 dòng.
G8 (từ điển đầy 23 master × N param) + panel build thường xuyên → cân nhắc cache nếu thấy chậm.

### DataTable `DT_MaterialParamMap`
Vị trí: `/Game/cuong/UI/Data/DT_MaterialParamMap`. RowStruct = `MaterialParamControlRow` (C++).
Row Name tùy ý — hàm tra bằng field `BaseMaterial`, KHÔNG bằng Row Name. Từ điển tạm 2 dòng
(Scalar `Roughness Max` + Color `Tint`, cùng `MM_GenericMaterial`) — từ điển THẬT là G8.

### Test S7G7T1 — 4/4 PASS (15/09/2026)
| Case | Input | Kỳ vọng | Kết quả |
|---|---|---|---|
| 1 | MI thuộc `MM_GenericMaterial` | 2 row | ✅ |
| 2 | MI ngoài từ điển | 0 row | ✅ |
| 3 | **MID** tạo từ đúng MI Case 1 | 2 row | ✅ (chứng minh so con trỏ không bị MID đánh lừa) |
| 4 | đọc field 2 row | LabelVI+ParamName đúng | ✅ |

Q9: MIỄN (C++ thuần, không đụng `SelectedActors`).
