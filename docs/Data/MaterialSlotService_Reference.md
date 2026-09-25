# MaterialSlotService — C++ Blueprint Function Library Reference
**Nguồn:** `DELTA 27/08/2026 — S7.G1 MaterialSlotService (Sonnet execution, Fable task card)`, task card `S7.G1 MaterialSlotService | Fable → Sonnet | 27/08/2026`. As-built thật — 5/5 Việc PASS, build xanh xuyên suốt, KHÔNG deviation so với API đóng băng trong `Plans/Sprint7_MaterialEdit_Plan_v1.1.md` mục S7.G1.
**Tạo:** 27/08/2026
**Cập nhật:** 24/09/2026 16:10 — U2.5 fix: `GetSlotScalarParam`/`GetSlotVectorParam` đọc trên `UMaterialInterface` hiện tại của slot (MID nếu đã chỉnh, MI gốc nếu chưa) thay vì chỉ MID. Git `c23b585` (plugin `FurnitureToolkit`).
**Cập nhật:** 22/09/2026 — U2.1 (Undo Architecture): +`GetSlotScalarParam`/`GetSlotVectorParam` (reader Before) trên `UMaterialSlotService`; +class mới `UParamCommandLibrary` + struct `FMaterialParamCommand` (file reference này giờ phủ 3 class: `UMaterialSlotService`, `UMaterialParamMap`, `UParamCommandLibrary`).

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

### GetSlotScalarParam / GetSlotVectorParam(Mesh, SlotName, HintIndex, ParamName, OutValue&) → bool

> 📌 **[CHỨA AS-BUILT]** — U2.1 (22/09/2026), nguồn task card
> `Sprints/Sprint7/21-09-2026_U2_HistoryMutationBoundary_TaskCard.md` §3 QĐ3 + §5.1.

```cpp
static bool GetSlotScalarParam(UStaticMeshComponent* Mesh, const FString& SlotName,
    int32 HintIndex, FName ParamName, float& OutValue);
static bool GetSlotVectorParam(UStaticMeshComponent* Mesh, const FString& SlotName,
    int32 HintIndex, FName ParamName, FLinearColor& OutValue);
```
Reader cho Before/After của command undo (U2) VÀ seed của `RefreshParamPanel` (từ U2.5) — đối xứng
`Set*` nhưng **KHÔNG có side-effect**, **không gọi `EnsureSlotMID`** (không tự tạo MID chỉ vì đọc).

**As-built hiện tại (U2.5, 24/09/2026 — `c23b585`):**
```cpp
UMaterialInterface* Mat = Mesh->GetMaterial(Index);          // MID nếu đã chỉnh, MI gốc nếu chưa
if (!IsValid(Mat)) return false;                             // log Warning "Slot khong co material"
float Value = 0.f;                                           // (Vector: FLinearColor Value = White)
if (!Mat->GetScalarParameterValue(FHashedMaterialParameterInfo(ParamName), Value))
    return false;                                            // log Warning "Param '...' khong ton tai tren material"
OutValue = Value; return true;
```
`false` CHỈ còn khi Mesh/slot/material không hợp lệ hoặc param không tồn tại. Caller BP vẫn giữ
fallback hằng số (`MinValue`/trắng) cho đúng ca đó.

> **[HISTORICAL — U2.1, 22/09]** Bản đầu đọc CHỈ trên MID (`Cast<UMaterialInstanceDynamic>` +
> `GetAllScalarParameterInfo` + `K2_GetScalarParameterValue`); chưa có MID → `false` → caller fallback
> hằng số. **Sai** cho slot chưa từng chỉnh (chỉ có MI): Before của Undo = 0/trắng → Undo lần chỉnh ĐẦU
> TIÊN trả về sai giá trị; panel seed cũng hiện 0/FFFFFF. Lộ ở PIE U2.5 (Tint undo về FFFFFF). BP không
> đọc được param trên MI (xác nhận T3 18/09) nhưng C++ `UMaterialInterface::GetScalar/VectorParameterValue`
> đọc được mọi loại → đổi nguồn đọc. Test sau fix: F1–F4 PASS (seed đúng, undo lần đầu về đúng gốc).

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

### HexToLinearColor(HexString, OutColor) → bool (S7G7T2, 15/09/2026)
> Cùng class `UMaterialParamMap` (`MaterialParamMap.h/.cpp`), KHÔNG phải file C++ mới. Nguồn:
> `DELTA — S7G7T2 AS-BUILT` (Opus+Sonnet, 15/09/2026) Phần E. Dùng bởi `Widgets/WBP_ParamColorRow.md`
> (`EditableTextBox_Hex.OnTextCommitted`).

```cpp
// Parse hex "RRGGBB" hoặc "RRGGBBAA" (có/không dấu #) → LinearColor.
// Validate hex hợp lệ TRƯỚC khi gọi FColor::FromHex (hàm gốc không an toàn với input rác).
UFUNCTION(BlueprintPure, Category = "Material|ParamMap")
static bool HexToLinearColor(const FString& HexString, FLinearColor& OutColor);
```
```cpp
bool UMaterialParamMap::HexToLinearColor(const FString& HexString, FLinearColor& OutColor)
{
    FString Clean = HexString.TrimStartAndEnd();
    if (Clean.StartsWith(TEXT("#"))) { Clean = Clean.RightChop(1); }
    if (Clean.Len() != 6 && Clean.Len() != 8) { return false; }
    for (const TCHAR C : Clean) { if (!FChar::IsHexDigit(C)) { return false; } }
    const FColor Parsed = FColor::FromHex(Clean);
    OutColor = FLinearColor(Parsed);
    return true;
}
```

**Test cô lập — 4/4 PASS:** `FF0000`→true đỏ đúng · `#00FF00FF`→true xanh đúng · `zzz`→false ·
`12345` (sai độ dài)→false.

**Node UE sẵn dùng (verify, thêm vào bảng node được phép nếu chưa có):** `To Hex` /
`ToHex_LinearColor` (`KismetMathLibrary`, format `RRGGBBAA`, nhận thẳng `LinearColor`).

---

## FMaterialParamCommand + UParamCommandLibrary (U2.1, 22/09/2026)

> 📌 **[CHỨA AS-BUILT]** — Nguồn: task card `Sprints/Sprint7/21-09-2026_U2_HistoryMutationBoundary_TaskCard.md`
> §3 QĐ1/QĐ4, §5.1. **U2.1 ĐÓNG — PASS.** Class RIÊNG (`ParamCommandLibrary.h/.cpp`) + struct
> RIÊNG (`ParamCommandTypes.h`), KHÔNG nhét vào `MaterialSlotService`. Compile sạch, 4/4 Spec test
> xanh, negative control PASS (xem Test bên dưới). Git: `feat(U2.1)` commit `3fd1b2a`.

### EParamCmdType (UENUM BlueprintType)
```cpp
enum class EParamCmdType : uint8 { Scalar, Color };   // Texture: KHÔNG có case (Đ12)
```

### FMaterialParamCommand (USTRUCT BlueprintType) — 9 field
| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `EntityID` | `FString` | PersistentID (U1) của actor đích — KHÔNG cầm con trỏ actor, resolve lại lúc Undo/Redo qua `ResolveByPersistentId` |
| `SlotName` | `FString` | Danh tính slot chính |
| `SlotHintIndex` | `int32` (default -1) | Fallback resolve slot, đối xứng `HintIndex` của `MaterialSlotService` |
| `ParamName` | `FName` | Tên param trên material |
| `Type` | `EParamCmdType` (default `Scalar`) | Chọn field Before/After nào có nghĩa |
| `BeforeScalar` / `AfterScalar` | `float` | Dùng khi `Type=Scalar` |
| `BeforeColor` / `AfterColor` | `FLinearColor` (default White) | Dùng khi `Type=Color` |

Nhúng vào `S_SceneSnapshot.ParamCmd` (BP struct, +U2.2) khi `EntryKind=ParamCommand`. Đây là
payload "command", KHÔNG phải "snapshot" — hướng B (additive hybrid) vẫn chụp full `Meshes` kèm
theo (xem `BP_UndoManager.md` mục U2 khi as-built §5.1b/5.1c).

### BuildScalarCommand / BuildColorCommand(EntityID, SlotName, SlotHintIndex, ParamName, Before, After) → FMaterialParamCommand
```cpp
// class UParamCommandLibrary : public UBlueprintFunctionLibrary
static FMaterialParamCommand BuildScalarCommand(const FString& EntityID, const FString& SlotName,
    int32 SlotHintIndex, FName ParamName, float Before, float After);
static FMaterialParamCommand BuildColorCommand(const FString& EntityID, const FString& SlotName,
    int32 SlotHintIndex, FName ParamName, FLinearColor Before, FLinearColor After);
```
`BlueprintPure`, PURE hoàn toàn (không đụng World) — chỉ gói field vào struct + set đúng `Type`.

### IsNoOpCommand(Command) → bool
```cpp
static bool IsNoOpCommand(const FMaterialParamCommand& Command);
```
`Before==After` (theo đúng `Type`, dùng `FMath::IsNearlyEqual` cho Scalar và `FLinearColor::Equals`
cho Color — dung sai nhỏ, không phải `==` cứng) → `true`. Dùng chặn `UNDO-SESS-04` (không tạo
entry rỗng khi kéo rồi thả lại đúng giá trị cũ). `Type` lạ (không nên xảy ra) → coi như no-op, an
toàn hơn tạo entry rác.

### RefuseTexture() → bool
```cpp
static bool RefuseTexture();
```
Đ12 — texture param KHÔNG có builder command, hàm này LUÔN trả `false`. Tồn tại để BP có 1 điểm
gọi tường minh nếu lỡ định làm texture command, thay vì im lặng bỏ qua.

### Test U2.1 — Spec `FurnitureTool.Undo.U2_Command` (4/4 PASS, 22/09/2026)
| Test | Nội dung | Kết quả |
|---|---|---|
| `[UNDO-HIST-03]` | Build scalar command → `BeforeScalar`/`AfterScalar` khớp đúng giá trị truyền vào | ✅ |
| `[UNDO-SESS-04]` | `IsNoOpCommand(Before==After)` → `true` | ✅ |
| (không mã) | `IsNoOpCommand(Before!=After)` → `false` (kiểm chứng không luôn trả `true`) | ✅ |
| `[UNDO-CMD-TEX]` | `RefuseTexture()` → luôn `false` | ✅ |

**Negative control (bắt buộc, đã chạy):** sửa tạm nhánh `Scalar` trong `IsNoOpCommand` thành
`return false;` → case `UNDO-SESS-04` (Before==After) chuyển ĐỎ đúng như kỳ vọng → xác nhận test
biết kêu khi logic sai → khôi phục nguyên bản → chạy lại 4/4 xanh.

**Bài học nhỏ trong phiên:** lần đầu thử negative control bằng cách chèn `return true;` sớm phía
trên `switch` trong `IsNoOpCommand` → project này bật warnings-as-errors, cảnh báo "unreachable
code" (do dead code dưới `switch`) bị nâng thành lỗi biên dịch, build fail (exit code 6). Đổi
cách: sửa TRỰC TIẾP 1 nhánh return có sẵn (không tạo dead code) — sạch, không vướng warning.

Q9: MIỄN (C++ thuần, không đụng `SelectedActors`). Q10: N/A (type/function mới, chưa có consumer
nào khác ngoài U2 đang xây).

---

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Có mặt trong thao tác:** [[L09 · Đổi vật liệu|L09]] · [[L10 · Chỉnh thông số vật liệu|L10]] · [[L12 · Lưu và mở cảnh|L12]] · [[L13 · Hoàn tác và làm lại|L13]]

**Thuộc mảng kết nối:** [[Kết nối 3d - Save Undo khởi động]] · [[Kết nối 3e - Vật liệu Material]]

**← Được gọi bởi**
- [[BP_UndoManager]] — đọc giá trị trước/sau + đảo 1 thông số · GetSlot*Param() / SetSlot*Param() (qua ApplyParamCommand) ✓K2
- [[WBP_FurnitureInventory]] — reset param / reset về mặc định · ResetSlotToAssetDefault() / ResetAllSlotsToAssetDefault() ✓K2
- [[WBP_FurnitureInventory]] — gán vật liệu vào slot (kéo-thả G5) · ApplyLoadedMaterialToSlot() → LoadAndApplyMaterial ✓K2
- [[WBP_ParamColorRow]] — parse hex khi commit ô Hex · HexToLinearColor()
- [[WBP_FurnitureInventory]] — tra từ điển param theo material · GetControlsForMaterial(SlotMaterial, DT_ParamMap) ✓K2
- [[WBP_FurnitureInventory]] — seed giá trị row = giá trị THẬT trên MID/MI (U2.5, thay Cast MID+fallback) · GetSlotScalarParam() / GetSlotVectorParam()
- [[BP_FurnitureActor]] — gắn lại vật liệu + thông số từng slot sau khi tải mesh (Undo) · ApplyLoadedMaterialToSlot() → ApplyParamsJsonToSlot()
- [[WBP_DragOverlay_FurnitureCard]] — tìm món + slot dưới điểm thả · TraceSlotUnderCursor() ✓K2

<!-- BRAIN:END -->
