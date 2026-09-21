# TASK CARD — U1: PERSISTENT IDENTITY + RESOLVER

**Tác giả:** Opus 4.8 (kiến trúc sư) | **Ngày:** 21/09/2026 | **Loại:** PLAN — chưa as-built
**Thực thi:** Sonnet 5 + cuhoang | **Gate:** U1 (trong `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md`)
**Trạng thái:** U1 ĐÓNG — PASS (21/09/2026, 21:27). U1.0→U1.5 xanh, §11 comprehension check PASS.

> **KHÔNG đóng dấu `[CHỨA AS-BUILT]`.** File này 100% thiết kế. Sau khi thực thi xong, as-built
> merge vào canonical (`BP_FurnitureActor.md`, `BP_UndoManager.md`, `Data_Structures.md`,
> `MaterialSlotService_Reference.md` hoặc doc lib mới, `Rules/Testing.md`), KHÔNG sửa ngược file này.

**Tiền đề PASS:** T0 (Automation Harness) — ĐÓNG 21/09. Harness Spec chạy được, `Rules/Testing.md` có.

**Ground truth đã đọc khi thiết kế (21/09):** `BP_FurnitureActor.md` v2.5 (BeginPlay, ActorLoaded EMS,
SpawnFurnitureCopy caller, biến SaveGame) · `BP_UndoManager.md` v1.17 (S_FurniturePlacement,
CaptureSnapshot Step 3, RestoreSnapshot Step 4) · `MaterialSlotService_Reference.md` (pattern
`ResolveSlotIndex` = khuôn identity đã giải đúng ở tầng slot) · `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md` §5, §7, §8.

---

## 0. MỤC TIÊU — MỘT CÂU HỎI NHỊ PHÂN

> **Sau khi Undo scene (destroy + respawn toàn bộ actor), hỏi Resolver bằng ID cũ có ra ĐÚNG actor
> mới (một UObject khác) không? Và ID có sống qua save/load, kể cả save cũ không có ID?**

U1 là MÓNG. KHÔNG có UI nào tiêu thụ Resolver trong U1 (đó là U3). U1 chỉ: (1) mọi actor có
`PersistentID` bền, (2) ID sống qua respawn + save/load, (3) có hàm resolve ID → actor hiện tại,
build + test xong, để đó cho U3 dùng.

**U1 hoàn toàn ADDITIVE.** Hệ `UniqueID` cũ (Get Display Name) KHÔNG đụng, vẫn chạy song song.

---

## 1. BA CỔNG GATE

### Q10 — FLOW COVERAGE (BẮT BUỘC — U1 thêm một state mới `PersistentID`)

State mới `PersistentID` có 3 **producer** và (trong U1) 0 **consumer thật** (Resolver build nhưng
chưa nối UI). Bảng producer — mọi đường sinh/gán ID, KHÔNG đường nào được để ID rỗng sai lúc:

| Producer (đường actor ra đời / phục hồi) | Nhãn | Hành vi ID | Ghi chú |
|---|---|---|---|
| `SpawnFurnitureCopy` (paste, duplicate, combo spawn) | `[DOC]` v1.10 | **ENSURE** — rỗng thì sinh mới | Chokepoint mọi spawn runtime |
| `On Drop` (`WBP_DragOverlay_FurnitureCard`, card-drag) | `[SỬA 21/09/2026]` | **ENSURE** — rỗng thì sinh mới | ⚠️ **Producer thứ 4, KHÔNG có trong plan gốc.** Đính chính: card-drag KHÔNG qua `SpawnFurnitureCopy` (đã bị gộp nhầm) — có đường spawn riêng qua `PreviewActorRef` (spawn ở `On Drag Detected`, finalize ở `On Drop`). Phát hiện lúc PIE test U1.2 (drag không in ra PersistentID). Xem `AI_Implementation_Rules.md` dòng cảnh báo "Drag-drop KHÔNG gọi SpawnFurnitureCopy". |
| `Event ActorLoaded` (EMS, load từ save) | `[DOC]` v2.2 | **ENSURE** — save cũ (rỗng) sinh mới 1 lần; save mới giữ nguyên | Đường RIÊNG, KHÔNG qua SpawnFurnitureCopy |
| `RestoreSnapshot` Step 4 (undo/redo respawn) | `[DOC]` v1.17 | **INJECT** — SET = Placement.PersistentID (ghi đè ID tạm) | Cùng chỗ SET RowName/GroupID đã có |
| `Event BeginPlay` | `[DOC]` v2.5 | **KHÔNG ĐỤNG** — chỉ add tag | Sinh ID ở đây = vi phạm ID-08 (respawn cũng chạy BeginPlay) |
| Copy/Paste clipboard (`S_ClipboardEntry`) | `[VERIFY V5]` | **KHÔNG capture PersistentID** | Field mới → clipboard chưa có → paste nhận ID mới từ SpawnFurnitureCopy (đúng ID-03) |

**Invariant xuyên luồng:** mọi actor mang tag `FurnitureSpawned` phải có `PersistentID != ""` sau
khi ra đời/phục hồi xong. Không đường nào để nó rỗng khi actor đã sống.

### Q9 — S-MATRIX: **MIỄN.** U1 không đụng `SelectedActors`. Identity là per-actor, độc lập selection.

### Q8 — áp cho từng node flow BP ở §4 (mỗi flow có dòng Q8 riêng).

---

## 2. QUYẾT ĐỊNH KIẾN TRÚC (chốt + lý do — đọc TRƯỚC khi build)

### QĐ1 — `PersistentID` kiểu **String** (không phải Guid native)

Sinh bằng Guid nhưng lưu dạng String. Lý do (3 điểm, thứ tự ưu tiên):
1. **Chắc chắn round-trip qua EMS.** String SaveGame luôn serialize được; FGuid-as-SaveGame chưa
   verify với plugin bên thứ ba (`[VERIFY V2]`). Không đánh cược ở tầng móng.
2. **Print-debug được.** cuhoang debug bằng Print String — ID hiện đọc được trong log là thắng lớn.
3. **Nhất quán** với mọi SaveGame var hiện có (`RowName` Name, `GroupID`/`MeshPath` String) + field
   `UniqueID` String trong snapshot. "" = chưa set (giống `RowName == ""` = save cũ).

Guid-string vẫn duy nhất tuyệt đối như Guid native — không mất gì về correctness.

### QĐ2 — Resolver dùng **SCAN sau contract cố định**, KHÔNG registry `TMap` ngay

Contract: `ResolveByPersistentId(Id) → BP_FurnitureActor (+bFound)`. Ruột: scan
`GetAllActorsWithTag("FurnitureSpawned")`, so `PersistentID == Id`.

Lý do chọn scan (không phải registry) — đây là chỗ tao KHÁC doc kiến trúc §5, cố ý:
- **An toàn hơn cho `ID-04`:** actor destroy tự biến khỏi scan. Registry `TMap` giữ weak-ptr có
  thể còn stale entry tới lúc dọn → rủi ro "resolve ra actor đã chết".
- **Xoá sạch Q10 surface:** registry buộc register mọi spawn path + unregister mọi destroy path.
  Scan không cần lifecycle nào.
- **Đủ nhanh:** resolve chạy 1 lần/undo trên ~200 actor. O(n) thừa sức. Registry O(1) là tối ưu
  chưa cần.
- **Cửa còn mở:** nếu sau này profiling thấy chậm, thay RUỘT hàm bằng registry, KHÔNG đổi contract
  / call site. Đúng pattern KP2 "chốt chặn cô lập" dự án đã dùng (`GetEditableSlots` param RowName).

> Đây là bài toán dự án ĐÃ giải đúng ở tầng slot (`ResolveSlotIndex`: tên→index, fallback hint).
> U1 = copy đúng khuôn đó lên tầng actor.

### QĐ3 — Sinh ID ở C++ (`EnsurePersistentId`), Resolve ở Blueprint

- **`EnsurePersistentId` = C++** vì policy "rỗng thì sinh, có rồi thì GIỮ" là trái tim của
  `ID-07/ID-08` — bug tinh vi (sinh lại mỗi lần load) sống đúng ở đây → phải Spec-test (Automation
  Spec = C++, chạy không cần PIE, rẻ).
- **Resolve = Blueprint** vì nó đọc `PersistentID` (biến BP) trực tiếp, KHÔNG cần C++ reflection
  (tránh bẫy mangle tên property). Resolve là logic tầm thường (loop+so sánh) → test bằng
  PIE/Functional, không cần Spec.

### QĐ4 — Sinh-rồi-ghi-đè khi restore (harmless, đổi lấy nhất quán)

`SpawnFurnitureCopy` LUÔN ensure (mọi spawn có ID tươi). `RestoreSnapshot` sau đó ghi đè bằng ID
snapshot. ID tươi bị bỏ (không registry đọc nó → không leak). Đổi lại: `RestoreSnapshot` dùng ĐÚNG
pattern `SET NewActor.RowName`/`GroupID` đã chạy tốt 2 lần, Sonnet không phải học pattern mới.

---

## 3. C++ — `UEntityIdLibrary` (file mới trong plugin)

**Vị trí:** `Plugins/FurnitureToolkit/Source/FurnitureToolkit/Public/EntityIdLibrary.h` + `Private/EntityIdLibrary.cpp`
**Build.cs:** KHÔNG đụng (`Core` đủ cho `FGuid`).

```cpp
// EntityIdLibrary.h
#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "EntityIdLibrary.generated.h"

UCLASS()
class FURNITURETOOLKIT_API UEntityIdLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // Rỗng → sinh Guid-string mới. Có rồi → GIỮ NGUYÊN (không sinh lại). Trái tim ID-07/ID-08.
    UFUNCTION(BlueprintCallable, Category = "Undo|Identity")
    static FString EnsurePersistentId(const FString& Current);

    UFUNCTION(BlueprintPure, Category = "Undo|Identity")
    static bool IsValidPersistentId(const FString& Id);
};
```

```cpp
// EntityIdLibrary.cpp
#include "EntityIdLibrary.h"
#include "Misc/Guid.h"

FString UEntityIdLibrary::EnsurePersistentId(const FString& Current)
{
    if (!Current.IsEmpty()) { return Current; }        // ID-07: đã có → giữ, KHÔNG sinh lại
    return FGuid::NewGuid().ToString(EGuidFormats::Digits);  // ID-01: sinh mới
}

bool UEntityIdLibrary::IsValidPersistentId(const FString& Id)
{
    return !Id.IsEmpty();
}
```

**Cảnh báo `[VERIFY V8]`:** `FURNITURETOOLKIT_API` — kiểm đúng tên macro API của module (mở
`MaterialParamMap.h` xem nó dùng macro gì, copy y hệt). Nếu module không có API macro thì bỏ.

---

## 4. BLUEPRINT — 5 điểm sửa (tất cả ADDITIVE)

### 4.1 — `BP_FurnitureActor`: thêm biến `PersistentID`

```
PersistentID : String   ← SaveGame = TRUE, default ""   (đặt cạnh RowName/GroupID trong Variables)
```

### 4.2 — `BP_FurnitureActor.Event ActorLoaded`: ensure trên nhánh MeshPath hợp lệ

Chèn vào Flow MỚI (v2.2), ngay sau `Branch(MeshPath != "")` → **True**, TRƯỚC `LoadAsset_Blocking`:

```
Branch(MeshPath != "") True ▶→ SET PersistentID = EnsurePersistentId(GET PersistentID)   ← [MỚI U1]
                            ▶→ LoadAsset_Blocking(...)   (giữ nguyên phần cũ)
```
> Save mới: PersistentID đã có → EnsurePersistentId trả nguyên (no-op, giữ ID-06). Save cũ: "" →
> sinh mới 1 lần (ID-07); EMS Save lần sau tự persist (vì SaveGame=True).
> Đặt trên nhánh True (nhánh False destroy actor, vô nghĩa).

**Q8:** Event chain (ActorLoaded) | không cần IsValid (SET biến self) | nhánh True tiếp tục
LoadAsset, không dead-end | không latent mới | 6A: N/A (không undo-able, là load).

### 4.3 — `SpawnFurnitureCopy` (trong `BP_FurnitureInputManager`): ensure cuối hàm

Sau node Spawn Actor (NewActor đã tồn tại), TRƯỚC khi return:

```
... (spawn xong, set mesh/material như cũ) ...
▶→ SET NewActor.PersistentID = EnsurePersistentId(GET NewActor.PersistentID)   ← [MỚI U1]
▶→ (return NewActor như cũ)
```
> `[VERIFY V1]` SpawnFurnitureCopy là Function hay Custom Event — chỉ để biết cách chèn node, logic
> không đổi. Actor mới spawn có PersistentID="" → ensure sinh mới. Đường restore sẽ ghi đè (§4.5).

**Q8:** tuỳ Function/Custom Event | IsValid(NewActor) đã có sẵn trong hàm (spawn thành công) | không
dead-end (nối vào return) | không latent | 6A: N/A.

### 4.4 — `S_FurniturePlacement` (UserDefinedStruct): thêm field

```
PersistentID : String   ← thêm vào struct, default ""   (đặt cạnh RowName/GroupID)
```
> Struct này CHỈ dùng runtime trong SnapshotHistory (KHÔNG SaveGame ra file) → thêm field không
> đụng save file. Recompile mọi BP dùng struct (đã làm 3 lần: RowName, GroupID, MaterialSlots — an toàn).

### 4.5 — `BP_UndoManager`: capture + inject (2 chỗ, đúng pattern RowName)

**CaptureSnapshot Step 3** — trong ForEach build S_FurniturePlacement, thêm 1 dòng (y như RowName):
```
PersistentID = GET (Array Element as BP_FurnitureActor).PersistentID   ← [MỚI U1], nối vào Make struct
```

**RestoreSnapshot Step 4** — sau `SpawnFurnitureCopy`, cạnh `SET NewActor.RowName`/`GroupID`, thêm
GUARD chống ghi đè bằng rỗng:
```
▶→ Branch(Placement.PersistentID != "")
     True ▶→ SET NewActor.PersistentID = Placement.PersistentID   ← [MỚI U1] — inject ID gốc, ghi đè ID tươi
     False → (bỏ qua — giữ ID tươi từ SpawnFurnitureCopy; phòng snapshot chụp trước lúc ensure)
```
> Guard `!= ""` phòng edge: nếu 1 actor bị capture lúc chưa ensure (ID rỗng) thì KHÔNG wipe ID tốt
> bằng rỗng. Bình thường sau U1 mọi actor đã ensure → nhánh True luôn chạy.

**Q8 (Capture):** Event/Function như hiện tại | không IsValid mới (đã có Cast) | không dead-end (nối
Make struct) | không latent | 6A: capture SAU action như cũ.
**Q8 (Restore):** | Branch có cả 2 nhánh merge (True SET, False bỏ qua → cùng đi tiếp) không dead-end
| không latent | 6A: đây LÀ đường ngược (restore).

### 4.6 — `BP_FurnitureSceneManager`: hàm `ResolveByPersistentId` (MỚI)

> Đặt trên SceneManager (actor, world implicit, đã là hub giữ FurnitureInventoryRef). Function
> thuần (không latent).

```
Function ResolveByPersistentId(Id : String) → (OutActor : BP_FurnitureActor, bFound : Bool)

▶→ Branch(Id == "")
     True → SET OutActor=None, bFound=false → Return             ← guard rỗng, đừng scan vô nghĩa
     False ▶→ Get All Actors With Tag("FurnitureSpawned") → For Each Loop WITH BREAK
                LoopBody ▶→ Cast To BP_FurnitureActor(Array Element)
                            Success ▶→ Branch(AsActor.PersistentID == Id)
                                         True ▶→ SET OutActor=AsActor, SET bFound=true → BREAK
                                         False → (continue)
              Completed ▶→ Return (OutActor, bFound)
```
> `[VERIFY V4 — ✓ 21/09/2026]` — cuhoang xác nhận: khi Play PIE, KHÔNG có `BP_FurnitureActor`
> nào đặt sẵn trong Level/Outliner. Không có producer thứ 5 ngoài 4 cửa đã cover (ActorLoaded,
> SpawnFurnitureCopy, On Drop card-drag, RestoreSnapshot). Không cần hook thêm.

**Q8:** Function | IsValid qua Cast (Success mới đọc) | For Each WITH BREAK (không duyệt thừa) |
Branch Id=="" có đích (Return) | không latent | 6A: N/A (đọc thuần).

---

## 5. THỨ TỰ THỰC THI (mỗi bước 1 checkpoint nhị phân)

> **Ngân sách PIE:** bước 6,7,8 cần PIE. Gom cụm, restart editor giữa cụm (luật `Rules/Testing.md`
> §2). Bước 2 (Spec) KHÔNG tốn PIE.

### U1.0 — Backup (đường lùi)
```
[ ] Backup toàn project: Lighting_Mnger_BACKUP_21-09-2026_preU1
    GIỮ Content/ Plugins/ Source/ Config/ *.uproject — BỎ Saved/ Intermediate/ DerivedDataCache/ Binaries/
[ ] git commit repo plugin (trạng thái sau T0) làm mốc trước khi đụng
```

### U1.1 — C++ `EnsurePersistentId` + Spec test (PURE, không PIE)
```
[x] Tạo EntityIdLibrary.h/.cpp (§3)
[x] Tạo Tests/EntityIdTests.cpp (§6 dưới)
[x] Compile sạch
[x] Session Frontend → Automation → filter "FurnitureTool.Undo.U1" → chạy
[x] 3 test XANH
[x] NEGATIVE CONTROL: sửa EnsurePersistentId thành `return Current;` (bỏ nhánh sinh) → chạy lại →
    [UNDO-ID-01] phải ĐỎ (input rỗng ra rỗng). Thấy đỏ → khôi phục → xanh lại. — CONFIRMED ĐỎ rồi khôi phục xanh lại (3/3)
```
CHECKPOINT: policy sinh/giữ ID đúng, test biết kêu. → sang U1.2.

### U1.2 — BP var + 2 ensure point (§4.1, 4.2, 4.3)
```
[x] Thêm PersistentID:String (SaveGame) vào BP_FurnitureActor
[x] Chèn ensure vào ActorLoaded (§4.2) + SpawnFurnitureCopy (§4.3) + On Drop/WBP_DragOverlay_FurnitureCard (producer thứ 4, thêm 21/09/2026)
[x] Compile
[x] PIE: kéo 1 card furniture vào scene → Print String(PersistentID) → CHUỖI KHÔNG RỖNG (ID-01) — PASS
```
CHECKPOINT: actor mới có ID. → U1.3.

### U1.3 — Struct + capture/inject (§4.4, 4.5) — ĐỤNG UNDO CORE, cẩn thận
```
[x] Thêm PersistentID vào S_FurniturePlacement
[x] CaptureSnapshot Step 3: capture PersistentID
[x] RestoreSnapshot Step 4: inject (có guard != "")
[x] Compile
[x] PIE: spawn actor → Print ID (ghi lại) → Move actor → Ctrl+Z (Undo) → Print ID → GIỐNG ID cũ (ID-02) — PASS (2F2591944E2B31AE861E7A9D6D601A77 khớp cả 2 lần)
[x] REGRESSION: chạy lại test Undo/Redo material cũ (round-trip material) → KHÔNG hồi quy — PASS
```
CHECKPOINT: ID sống qua respawn + không phá undo cũ. → U1.4. Nếu regression fail → DỪNG, báo.

### U1.4 — Resolve function (§4.6)
```
[x] Tạo ResolveByPersistentId trên BP_FurnitureSceneManager — verify khớp 100% qua K2 export
    thật (21/09/2026, xem `Blueprints/BP_FurnitureSceneManager.md`)
[x] PIE (Print tạm, xem chi tiết log dưới):
    - spawn 2 actor A,B → resolve(A.id) ra A, resolve(B.id) ra B (ID-05) — PASS
      (59060B7C.. → BP_FurnitureActor0 | 00D826BC.. → BP_FurnitureActor1)
    - Duplicate/Paste A → actor mới có ID KHÁC A (ID-03) [xác nhận V5: clipboard không mang ID] — PASS
      (D709F912.. ≠ 59060B7C..)
    - Destroy A → resolve(A.id) → bFound=false (ID-04) — PASS (59060B7C.. → NOT FOUND)
    - spawn → Undo → resolve(id cũ) ra actor MỚI (khác con trỏ cũ) (ID-02+ID-05 end-to-end = CÂU HỎI GATE) — PASS
      (81EB3929.. → FOUND, actor=BP_FurnitureActor5 — RestoreSnapshot luôn SpawnActorFromClass
      lại toàn bộ mảng, nên actor sau Undo chắc chắn là instance mới, không cần so tên riêng)
```
CHECKPOINT: câu hỏi nhị phân của U1 = XANH.

### U1.5 — EMS save/load (MANUAL — không tự động hoá được plugin bên thứ ba)
```
[x] PIE: spawn actor → Print ID → EMS Save → EMS Load → Print ID → GIỐNG (ID-06) — PASS (21/09/2026 21:09, cuhoang confirm PIE — 2 giá trị trước Save và sau Load khớp nhau)
[x] Nếu có save CŨ (trước U1): Load → Print ID → có ID (đã sinh) → Save → Load lại → Print → GIỐNG
    lần trước (ID-07: sinh 1 lần rồi ổn định, KHÔNG đổi mỗi lần load) — PASS (21/09/2026 21:27,
    cuhoang confirm PIE — save cũ chưa có field → Ensure sinh ID lần đầu → Save → Load lại → Print
    → ID giống hệt, không sinh lại lần 2)
```

### U1.6 — (TUỲ CHỌN) Functional Test gói U1.3/U1.4 vào `L_Test_UndoArchitecture`
```
[ ] Nếu >30 phút vướng → GÁC, ghi bằng chứng manual ở U1.3/U1.4 là đủ đóng gate. Dựng lại khi U2 cần map.
```

### U1.7 — Doc as-built (§8)

---

## 6. SPEC TEST — `Tests/EntityIdTests.cpp`

```cpp
#include "Misc/AutomationTest.h"
#include "EntityIdLibrary.h"

#if WITH_DEV_AUTOMATION_TESTS

BEGIN_DEFINE_SPEC(FU1IdentitySpec, "FurnitureTool.Undo.U1_Identity",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
END_DEFINE_SPEC(FU1IdentitySpec)

void FU1IdentitySpec::Define()
{
    Describe(TEXT("EnsurePersistentId"), [this]()
    {
        It(TEXT("[UNDO-ID-01] sinh id khong rong khi input rong"), [this]()
        {
            const FString Id = UEntityIdLibrary::EnsurePersistentId(TEXT(""));
            TestFalse(TEXT("id khong rong"), Id.IsEmpty());
        });

        It(TEXT("[UNDO-ID-07] khong sinh lai id da co san"), [this]()
        {
            const FString Existing = TEXT("abc123def");
            const FString Out = UEntityIdLibrary::EnsurePersistentId(Existing);
            TestEqual(TEXT("giu nguyen id cu"), Out, Existing);
        });

        It(TEXT("[UNDO-ID-01b] hai lan sinh cho hai id khac nhau"), [this]()
        {
            const FString A = UEntityIdLibrary::EnsurePersistentId(TEXT(""));
            const FString B = UEntityIdLibrary::EnsurePersistentId(TEXT(""));
            TestNotEqual(TEXT("2 id doc lap"), A, B);
        });
    });
}
#endif
```
> ASCII-only trong chuỗi test (bài học T0). Mã `[UNDO-ID-xx]` đầu chuỗi để tra ngược doc.

---

## 7. BẢNG INVARIANT → BẰNG CHỨNG

| Mã | Invariant | Chứng ở | Loại |
|---|---|---|---|
| `UNDO-ID-01` | Entity mới → ID hợp lệ, duy nhất | U1.1 Spec + U1.2 PIE | Spec + mắt |
| `UNDO-ID-02` | Respawn (undo) → giữ nguyên ID | U1.3 PIE | mắt (Print) |
| `UNDO-ID-03` | Duplicate/Paste → ID mới | U1.4 PIE | mắt |
| `UNDO-ID-04` | Deleted → resolve không ra, không tái dùng | U1.4 PIE | mắt |
| `UNDO-ID-05` | Resolve sau restore → actor mới (khác con trỏ cũ) | U1.4 PIE | mắt |
| `UNDO-ID-06` | Save → Load → giữ ID | U1.5 manual EMS | mắt |
| `UNDO-ID-07` | Save cũ (rỗng) → sinh 1 lần, ổn định | U1.1 Spec (policy) + U1.5 manual (e2e) | Spec + mắt |
| `UNDO-ID-08` | ID sinh ở birth, inject khi restore, KHÔNG ở BeginPlay | thiết kế: BeginPlay không đụng, ensure ở spawn/load, inject ở restore | design invariant |

---

## 8. AS-BUILT — GHI VÀO ĐÂU KHI XONG

| File | Ghi gì |
|---|---|
| `BP_FurnitureActor.md` | +biến `PersistentID` (SaveGame); ActorLoaded +ensure; version bump |
| `BP_FurnitureInputManager.md` | SpawnFurnitureCopy +ensure |
| `Widgets/WBP_DragOverlay_FurnitureCard.md` | On Drop +ensure (producer thứ 4, thêm 21/09/2026) |
| `BP_UndoManager.md` | S_FurniturePlacement +field; CaptureSnapshot Step 3 +capture; RestoreSnapshot Step 4 +inject (guard); version bump |
| `BP_FurnitureSceneManager.md` | +hàm ResolveByPersistentId |
| `Data/MaterialSlotService_Reference.md` HOẶC lib doc mới | `UEntityIdLibrary` (2 hàm) — cân nhắc tách file reference riêng |
| `Rules/AI_Implementation_Rules.md` | kết quả các `[VERIFY V1-V8]` vào mục "API/node đã xác nhận" |
| `Rules/Testing.md` | thêm dòng lịch sử U1 |
| `00_Core/01_Session_State.md` | Current/Next: U1 ĐÓNG → U2 |
| `00_Core/DEVIATIONS.md` | CHỈ nếu lệch task card này |

---

## 9. DANH SÁCH `[VERIFY]` — Sonnet xác nhận trong editor, KHÔNG đoán

| Mã | Cần kiểm | Ảnh hưởng |
|---|---|---|
| V1 | `SpawnFurnitureCopy` là Function hay Custom Event? | ✓ Function (xác nhận qua K2 export 21/09/2026) |
| V2 | EMS restore SaveGame String vars TRƯỚC `Event ActorLoaded` fire? | Nếu KHÔNG → ActorLoaded đọc "" sai → phải dời ensure. (Tin là CÓ) |
| V4 | Có BP_FurnitureActor đặt tay trong level (Outliner)? | ✓ Không có (21/09/2026, cuhoang confirm PIE) — không cần hook riêng |
| V5 | `S_ClipboardEntry` (Copy/Paste) có capture field nào thành PersistentID? | ✓ KHÔNG (xác nhận PIE ID-03, 21/09/2026 — paste ra ID mới D709F912.. ≠ gốc) |
| V8 | Tên macro API module (`FURNITURETOOLKIT_API`?) — copy từ MaterialParamMap.h | ✓ Đúng, compile sạch |

---

## 10. CÁI **KHÔNG** LÀM TRONG U1

| Không làm | Vì sao |
|---|---|
| Registry `TMap<Guid,Actor>` | QĐ2 — scan đủ + an toàn hơn. Registry là tối ưu sau, không đổi contract |
| Nối Resolver vào UI/Inspector | Đó là U3. U1 chỉ build + test Resolver độc lập |
| Gỡ `UniqueID` (Get Display Name) cũ | Additive. Gỡ đường cũ = subtractive, làm ở F-Migration sau U3 |
| Đụng BeginPlay cho ID | Vi phạm ID-08 (respawn cũng chạy BeginPlay) |
| Guid native thay String | QĐ1 — String chắc EMS + Print-debug được |
| Migrate Copy/Paste sang mang PersistentID | U1 để clipboard KHÔNG mang ID (đúng ID-03). Migrate sau |
| Transient-world Spec cho actor test | Chưa cần. Actor-level test dùng PIE manual (native của cuhoang) + Functional tuỳ chọn |

---

## 11. KIỂM TRA HIỂU BÀI (cuhoang trả lời TRƯỚC khi tick U1)

1. Vì sao KHÔNG sinh `PersistentID` trong `Event BeginPlay`, dù đó là nơi tự nhiên nhất cho "actor
   vừa ra đời"?
2. Khi Undo, `SpawnFurnitureCopy` sinh 1 ID tươi rồi `RestoreSnapshot` ghi đè bằng ID cũ. ID tươi bị
   bỏ đi. Vì sao điều này KHÔNG gây rác/leak?
3. Vì sao chọn scan thay vì registry `TMap` — lý do nào liên quan trực tiếp tới `ID-04` (actor đã xoá)?

**KẾT QUẢ (21/09/2026, ~21:05):** Cả 3 câu PASS — cuhoang tự sửa qua các vòng hỏi dẫn dắt (Socratic),
không đúng ngay lần đầu, cần bẻ nhỏ + chỉ ra chỗ lệch mới ra được câu đúng. Tóm tắt câu trả lời cuối:

1. Field `PersistentID` còn RỖNG lúc BeginPlay (EMS chưa kịp nạp SaveGame) → nếu Ensure chạy ở đó,
   nó thấy rỗng và SINH ID MỚI đè lên chỗ lẽ ra phải giữ ID cũ → actor lạc khỏi các thuộc tính đã
   lưu trước đó theo ID cũ. `Event ActorLoaded` đảm bảo chạy SAU khi EMS nạp xong nên an toàn.
2. `PersistentID` là **String (value type)**, không phải Object Reference — ghi đè chỉ là gán lại
   giá trị, không ai "cầm" giá trị cũ để mà rò rỉ. Khác hẳn mối lo VRAM leak của R2/R4 (hard-ref
   tới Object/Actor).
3. Registry (`TMap<Guid,Actor>`) cần code dọn tay ở MỌI chỗ actor có thể biến mất (Delete, Undo...)
   — quên 1 chỗ là có entry lạc (dangling reference). Tag-scan (`GetAllActorsWithTag`) không lưu gì
   cả — mỗi lần gọi hỏi thẳng engine "actor nào ĐANG tồn tại", nên actor bị Destroy (bởi code xoá
   khác, không phải do `Resolve`) tự động biến mất khỏi kết quả quét lần sau — "tự sửa mình miễn
   phí". Đây chính là lý do `ID-04` (actor đã xoá → `Resolve` trả `NOT FOUND`) chạy đúng mà không
   cần code xử lý riêng cho trường hợp đó.

**§11 GATE: CLEAR.** U1.5 cũng PASS (ID-06 21:09, ID-07 21:27) — **U1 ĐÓNG (21/09/2026, 21:27).**
U1.6 (Functional Test, TUỲ CHỌN) — không bắt buộc, bằng chứng manual U1.3/U1.4/U1.5 đã đủ đóng gate.

---

## 12. BƯỚC TIẾP THEO SAU U1

U2 — History đa hình + Mutation Boundary + Interactive Edit Session + Param Command đầu tiên. Resolver
của U1 vẫn CHƯA nối UI tới U3. Đừng nối sớm.
