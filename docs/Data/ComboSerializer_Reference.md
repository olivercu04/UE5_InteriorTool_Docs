# ComboSerializer / ComboThumbnail — C++ Blueprint Function Library Reference
**Nguồn:** `ComboSerializer.h`/`.cpp` + `ComboThumbnail.h` (cuhoang paste 14/07/2026 — source thật, không copy `.cpp` ComboThumbnail vì chưa có) + `ComboThumbnail.cpp` đoạn noise/SSAA (delta 19/07/2026, chưa phải full file paste)
**Tạo:** 14/07/2026 — bổ sung docs/Data (3+ tuần chưa cập nhật theo Sprint 5 Combo + P1 Thumbnail)
**Cập nhật:** 19/07/2026 — P2 Noise + Aliasing Fix: `AccumulateComboFrame`/`ResetComboAccumulation` mới, `BeginComboCapture`/`FinishComboCapture` đổi hành vi (SSAA 2× + temporal accumulation N=24)
21/07/2026 — P2 Gate F: Radius rotation-invariant (BeginComboCapture)

> File này là TÀI LIỆU THAM KHẢO — liệt kê function signature + hành vi thật từ source. Struct `FComboData`/`FComboGroupData`/`FComboItemData` xem `Data_Structures.md`.

---

## Class: UComboSerializer
**Plugin:** FurnitureToolkit | **Files:** `ComboSerializer.h` / `ComboSerializer.cpp` | Base: `UBlueprintFunctionLibrary`

### GetCombosDir() → FString (BlueprintPure)
```cpp
static FString GetCombosDir();
// return FPaths::ProjectSavedDir() / TEXT("Combos");
```
⚠️ **[PHÁT HIỆN 14/07/2026]** Trả về `<ProjectRoot>/Saved/Combos/` — KHÁC quyết định P4 đã chốt trong `DEVIATIONS.md` 23/06/2026 (dự định đổi sang `%LOCALAPPDATA%/InteriorFOFFTool/Combos` để combo sống qua rebuild packaged). Khớp đường dẫn thật quan sát được (`Saved/Combos/Folders.json`). Chưa rõ P4 bị revert hay chưa từng merge — cuhoang xác nhận nếu cần đổi lại.

### ComboToJson(Combo) → FString / JsonToCombo(Json, OutCombo) → bool
```cpp
static FString ComboToJson(const FComboData& Combo);
static bool JsonToCombo(const FString& Json, FComboData& OutCombo);
```
Wrap `FJsonObjectConverter::UStructToJsonObjectString`/`JsonObjectStringToUStruct` (CheckFlags=0, SkipFlags=0 — không filter field nào). **[CONFIRMED 14/07/2026 — đối chiếu file `.json` thật]** Field JSON là **camelCase** (`comboId`, `folderPath`, `relLocation`...), KHÔNG giữ nguyên PascalCase như suy đoán ban đầu — `FVector`/`FRotator` serialize thành object `{x,y,z}`/`{pitch,yaw,roll}` chữ thường. Ví dụ đầy đủ: `Data_Structures.md` mục "Combo JSON — ví dụ thật".

### SaveStringToFile / LoadStringFromFile
```cpp
static bool SaveStringToFile(const FString& FilePath, const FString& Content);
static bool LoadStringFromFile(const FString& FilePath, FString& OutContent);
```
`SaveStringToFile` ghi UTF-8 **KHÔNG BOM** (`ForceUTF8WithoutBOM`) — quan trọng cho tên/tag tiếng Việt.

### ListJsonFilesInDir(DirPath) → Array\<FString\>
```cpp
static TArray<FString> ListJsonFilesInDir(const FString& DirPath);
```
Trả **tên file** (không phải full path) — caller tự nối `GetCombosDir() + "/" + FileName`.

### DeleteFileAtPath(FilePath) → bool
```cpp
static bool DeleteFileAtPath(const FString& FilePath);
```

### FindMaterialRowNameByPath(MaterialDT, Path) → FString
```cpp
static FString FindMaterialRowNameByPath(const UDataTable* MaterialDT, const FString& Path);
```
**Logic:** Reflection tìm property tên `"MaterialPath"` trong row struct (qua `TFieldIterator<FProperty>` + `GetAuthoredName()`), rồi duyệt toàn bộ `RowMap` so khớp giá trị path → trả `RowName` (Pair.Key.ToString()). Trả `""` nếu không tìm thấy DataTable/property/path. Dùng lúc save combo: convert `MaterialPath` đầy đủ (`/Game/...`) → RowName portable, ghi vào `FComboItemData.MaterialOverrides`.

---

## Combo|Folder — C5 Folder Management

### UpdateComboFolder(ComboID, NewFolderPath) → bool
```cpp
static bool UpdateComboFolder(const FString& ComboID, const FString& NewFolderPath);
```
Load `<ComboID>.json` → parse `FComboData` → SET `FolderPath` → ghi đè lại file. Trả `false` nếu load/parse fail.

### RenameFolderPrefix(OldPrefix, NewPrefix) → int32 (số combo bị đổi)
```cpp
static int32 RenameFolderPrefix(const FString& OldPrefix, const FString& NewPrefix);
```
**Logic:** Quét MỌI file `.json` trong `GetCombosDir()`. Với mỗi combo: match `FolderPath == OldPrefix` (rename đúng path) HOẶC `FolderPath StartsWith OldPrefix + "/"` (rename path con) → cập nhật + ghi lại. Đếm `Changed` = số combo thật sự bị sửa (KHÔNG tính path cascade trong `Folders.json`).
**Cascade C5.3:** sau khi rename combo xong, quét luôn `Folders.json` (`LoadEmptyFoldersInternal`) — path nào match cùng điều kiện cũng được rename, ghi lại nếu có thay đổi (`bManifestChanged`).
⚠️ **Return Value là số COMBO bị đổi, KHÔNG PHẢI tín hiệu OK/fail chung** — `Count=0` (rename 1 folder rỗng, không combo nào bên trong) vẫn hợp lệ vì cascade `Folders.json` chạy độc lập. Xem ghi chú tại `WBP_FurnitureInventory.md` §HandleSavePickerRenameCommitted — KHÔNG Branch theo Count để gate success/fail.

### ClearFolderPrefix(Prefix) → int32 (số combo bị đổi)
```cpp
static int32 ClearFolderPrefix(const FString& Prefix);
```
Cùng logic match (exact hoặc prefix `+"/"`) như `RenameFolderPrefix`, nhưng SET `FolderPath = ""` (combo về "Chưa phân loại") thay vì rename. Cascade: xoá khỏi `Folders.json` (`RemoveAll`) thay vì rename entry.

### CreateEmptyFolder(FolderPath) → bool
```cpp
static bool CreateEmptyFolder(const FString& FolderPath);
```
Thêm 1 path vào `Folders.json` nếu CHƯA tồn tại (case-insensitive). Trả `false` nếu path đã có (tránh trùng) — KHÔNG phải lỗi I/O.

### GetAllFolderPaths() → Array\<FString\>
```cpp
static TArray<FString> GetAllFolderPaths();
```
**Nguồn DUY NHẤT cho BP lấy toàn bộ folder tồn tại** — BP KHÔNG được tự loop `AllComboViews` + tự hợp với manifest (comment gốc trong `.h`, nhấn mạnh IN CAPS). Logic: đọc `Folders.json` làm registry gốc → quét MỌI file combo `.json`, với mỗi combo có `FolderPath` không rỗng → tách segment theo `/` → ghi bổ sung TỪNG CẤP CHA (`"A/B/C"` → add `"A"`, `"A/B"`, `"A/B/C"`, dùng `AddUnique`) vào registry nếu chưa có → nếu registry có thay đổi thì ghi lại `Folders.json` (tự-học, self-healing).

---

## Class: UComboThumbnail (P1, MỚI 14/07/2026 — Gate G0-R + G1 DONE; P2 19/07/2026 — Noise + Aliasing Fix)
**Plugin:** FurnitureToolkit | **Files:** `ComboThumbnail.h` / `.cpp` (đoạn noise/SSAA đã đối chiếu source thật 19/07/2026 — phần còn lại của `.cpp` vẫn chưa full-paste) | Base: `UBlueprintFunctionLibrary`
> Xem bối cảnh kiến trúc (vì sao tách Begin/Finish thay vì 1 hàm one-shot): `DEVIATIONS.md` [ARCH] 14/07/2026, node flow debug: `Blueprints/Blueprint_Logic_NodeFlow.md` §BP_ComboManager. Bối cảnh noise/SSAA (19/07): `DEVIATIONS.md` mục "SPRINT 5 — 19/07/2026 — P2 Noise + Aliasing Fix".

### CaptureComboThumbnail(...) → bool — **[LEGACY], không gọi**
```cpp
static bool CaptureComboThumbnail(UObject* WorldContextObject,
    const FString& ComboID,
    const TArray<AActor*>& ComboActors,
    const TArray<AActor*>& ExtraHiddenActors,
    int32 Resolution = 1024,
    float FitRatio = 0.85f,
    bool bIsolateCombo = false,
    bool bUseFixedAngle = false,
    FRotator FixedAngle = FRotator::ZeroRotator);
```
One-shot capture (G0 gốc) — giữ nguyên trong code, đánh dấu `[LEGACY]`, KHÔNG xóa/gọi. Bị loại bỏ vì ảnh xám phẳng (Lumen GI/TAA/auto-exposure chưa hội tụ đủ frame — camera phụ chụp ngay 1 frame duy nhất). Thay bằng cặp `BeginComboCapture`/`FinishComboCapture` bên dưới.

### BeginComboCapture(WorldContextObject, ComboActors, ExtraHiddenActors, Resolution=1024,
FitRatio=0.85, bIsolateCombo=false, bUseFixedAngle=false, FixedAngle=(0,0,0)) → ASceneCapture2D
```cpp
static ASceneCapture2D* BeginComboCapture(UObject* WorldContextObject,
    const TArray<AActor*>& ComboActors,
    const TArray<AActor*>& ExtraHiddenActors,
    int32 Resolution = 1024,
    float FitRatio = 0.85f,
    bool bIsolateCombo = false,
    bool bUseFixedAngle = false,
    FRotator FixedAngle = FRotator::ZeroRotator);
```
**[UPDATED 15/07/2026, Gate G2]** Thêm 4 param mới so với G0-R: FitRatio (auto-fit theo
bounding box), bIsolateCombo/bUseFixedAngle/FixedAngle (chuẩn bị B3, chưa dùng thật). Vị trí
camera phụ tính từ Center - Dir*Distance (bounding box cầu bao + FitRatio), KHÔNG còn là vị
trí camera thật như bản G0-R.

Bước 1/2: spawn camera phụ, bật render liên tục (`bCaptureEveryFrame=true`, warm-up cho Lumen GI/TAA hội tụ). Trả về handle — caller (Blueprint) giữ trong class var, `Delay` một khoảng rồi gọi `FinishComboCapture`. Test debug (phím T, `BP_ComboManager`) chốt tạm `Delay(3.0)` — xem `01_Session_State.md` mục P1.

**[UPDATED 19/07/2026, P2 Noise + Aliasing Fix]** RenderTarget tạo ở `Resolution * ComboSSAAFactor`
(constexpr = 2, file-scope trong `.cpp`) thay vì `Resolution` thẳng — capture 2048² khi
`Resolution=1024`, downscale về `Resolution` xảy ra ở `FinishComboCapture` (box filter, xem
dưới). ⚠️ Gotcha: file có 2 chỗ gọi `CreateRenderTarget2D` gần giống hệt nhau
(`CaptureComboThumbnail` [LEGACY] vs `BeginComboCapture` thật) — phân biệt bằng
`bCaptureEveryFrame` (LEGACY=false, thật=true), sửa nhầm bản LEGACY vẫn build pass nhưng RT
thật không đổi kích thước.

**[UPDATED 21/07/2026, P2 Gate F — Radius rotation-invariant]** Công thức tính bán kính cầu bao
(`Radius`) đổi để bất biến với phép xoay combo:
- CŨ: `Radius = Bounds.GetExtent().Size()` — nửa đường chéo AABB world-space. Rotation-VARIANT:
  combo bất đối xứng xoay chéo → AABB phình → Radius to giả → camera lùi xa → cùng combo ra 2
  kích thước ảnh khác nhau tùy góc (đo Distance 235.77 vs 282.75, ~20%).
- MỚI: `Radius = max( Dist(actor→Center) + actor.BoundsExtent.Size() )` over ComboActors.
  Euclidean distance tới Center bất biến khi xoay quanh Center → Radius ổn định. Sau fix: 248 vs
  263 (~6% dư, do Center vẫn = Bounds.GetCenter() hơi trôi — chấp nhận, xem
  Feature-CanonicalStudioAngle Sprint 6).
- KHÔNG đụng chữ ký hàm, KHÔNG đụng Blueprint call sites — thuần đổi công thức nội bộ.

### AccumulateComboFrame(CaptureHandle) — MỚI 19/07/2026, P2 Noise Fix
```cpp
static void AccumulateComboFrame(ASceneCapture2D* CaptureHandle);
```
Đọc 1 frame hiện tại của `CaptureHandle`, cộng dồn vào buffer nội bộ không gian linear
(`FLinearColor`, tự giải mã sRGB→linear khi đọc từ `FColor`). Gọi 1 lần MỖI FRAME (Event Tick,
`BP_ComboManager`) trong lúc accumulate — N=24 frame mặc định (`Cmb_AccumTargetFrames`, tunable
Class Defaults). Buffer sống ở C++ file-scope static (`TMap<ASceneCapture2D*, FComboAccumState>`,
anonymous namespace, KHÔNG khai báo `.h`, KHÔNG lên Blueprint — BP loop 1M phần tử ở 2048² sẽ
treo máy). IsValid(CaptureHandle) tự guard trong thân hàm.

### ResetComboAccumulation(CaptureHandle) — MỚI 19/07/2026, P2 Noise Fix
```cpp
static void ResetComboAccumulation(ASceneCapture2D* CaptureHandle);
```
Xoá buffer cộng dồn cũ của `CaptureHandle` này (nếu có). Gọi TRƯỚC khi bắt đầu 1 đợt accumulate
mới, VÀ bắt buộc gọi ở `Event End Play` (cleanup/cancel giữa chừng) — không gọi = leak ~16MB RAM
(1024²) hoặc ~64MB (2048² sau SSAA) mỗi lần treo giữa chừng, cùng loại bug với
`Bugs/Bug_GPU_VRAM_Crash.md` nhưng RAM chứ không VRAM.

### FinishComboCapture(CaptureHandle, ComboID, ComboActors) → bool
```cpp
static bool FinishComboCapture(ASceneCapture2D* CaptureHandle, const FString& ComboID,
    const TArray<AActor*>& ComboActors);
```
**[UPDATED 15/07/2026, Gate G2]** Thêm param ComboActors (Array<AActor*>) — dùng để khôi phục
Custom Depth (outline) đúng actor đã tắt lúc BeginComboCapture. PHẢI đưa CÙNG mảng
ComboActors ở cả Begin và Finish (không track state qua static function — đơn giản hơn bản
DepthOn array của legacy CaptureComboThumbnail).

Bước 2/2: đọc frame đã hội tụ → ghi `<ComboID>.png` cạnh file combo `.json` (cùng `GetCombosDir()`) → tự dọn actor + RenderTarget, **kể cả khi đọc/ghi fail** (R4-style cleanup). Trả `false` nếu ghi file thất bại — Blueprint KHÔNG gate Save Combo theo giá trị này (combo vẫn lưu OK, card fallback icon 🧩 nếu capture fail).

**[UPDATED 19/07/2026, P2 Noise + Aliasing Fix]** Đoạn đọc pixel đổi hoàn toàn: nếu buffer
accumulate của `CaptureHandle` tồn tại (`FrameCount > 0`) → (1) trung bình temporal trong không
gian linear (`Sum / FrameCount`, CHƯA encode `FColor`) → (2) downscale spatial box-filter
`ComboSSAAFactor × ComboSSAAFactor` (vẫn linear) → encode `FColor` (`.ToFColor(true)`, áp gamma
sRGB) **ĐÚNG 1 LẦN** ở bước cuối — cộng thẳng giá trị 8-bit rồi chia trung bình sẽ lệch sáng
(gamma không cộng tuyến tính), rõ nhất ở vùng tối/bóng đổ. Không có buffer (quên gọi
`AccumulateComboFrame`) → fallback `ReadPixels` 1 frame ở kích thước RT thật (2048² sau SSAA,
KHÔNG downscale) — ảnh ra sai kích thước, dấu hiệu dễ nhận. `GComboAccumStates.Remove(CaptureHandle)`
luôn chạy ở cuối, kể cả RT null.

### GetComboThumbnail(ComboID) → Texture2D [BP_ComboManager, không phải C++]
**[MỚI 15/07/2026, Gate G3]** Cache qua Cmb_ThumbnailCache (Map<String,Texture2D>). Lật album
nếu đã cache, LoadComboThumbnail(256) nếu chưa. 🔴 Có bug Return Node đã fix — xem DEVIATIONS
15/07/2026 nếu cần đối chiếu lịch sử.

### LoadComboThumbnail(ComboID, MaxSize) → UTexture2D*
```cpp
static UTexture2D* LoadComboThumbnail(const FString& ComboID, int32 MaxSize = 256);
```
Đọc PNG → `Texture2D` transient. `MaxSize>0` = thu nhỏ về `MaxSize`; `0` = giữ nguyên 1024 (resolution capture gốc). **[DONE 14/07/2026 — Gate P1.G1]** Thân hàm đầy đủ: đọc PNG từ đĩa → `IImageWrapper` `SetCompressed` → `GetRaw` BGRA8 → optional `FImageUtils::ImageResize` xuống `MaxSize` → `UTexture2D::CreateTransient` + memcpy vào Mip 0. Build PASS, test phím Y (`BP_ComboManager`, tách riêng khỏi phím T capture) → "G1 Load OK, size=256" đúng kỳ vọng.

### GetThumbnailPath(ComboID) → FString (BlueprintPure) / ThumbnailExists(ComboID) → bool (BlueprintPure) / DeleteThumbnail(ComboID) → bool
```cpp
static FString GetThumbnailPath(const FString& ComboID);
static bool ThumbnailExists(const FString& ComboID);
static bool DeleteThumbnail(const FString& ComboID);
```
Helper path/tồn tại/xóa — suy đoán hợp lý từ tên hàm + Category, CHƯA đối chiếu thân hàm thật (không có `.cpp`). [?]

---

## Hàm cần thêm / còn thiếu (P1 roadmap)

| Hàm | Gate | Mô tả |
|---|---|---|
| Auto-fit khung hình (FitRatio dùng thật) | P1.G2 | `CaptureComboThumbnail` có param `FitRatio` nhưng `BeginComboCapture` KHÔNG có — cần xác nhận field này còn áp dụng ở đâu trong pipeline mới |
| Cache ảnh trong BP_ComboManager | P1.G3 | Node Map — chưa xác nhận, xem `Rules/AI_Implementation_Rules.md` mục "Nodes chờ xác nhận" |

Xem checklist đầy đủ: `00_Core/PROGRESS.md` mục P1.

---

## Lưu ý tích hợp

- Plugin: `FurnitureToolkit` — cùng plugin với `FurnitureFilterLibrary`, `UComboSerializer`, `UComboThumbnail`.
- `ComboThumbnail.h` include forward-declare `class ASceneCapture2D;` — không include full header `SceneCapture2D.h` ở `.h` (giữ nhẹ), thật ra include ở `.cpp` (chưa có để đối chiếu).
- Dependency: `FJsonObjectConverter` (module `JsonUtilities`) cho `ComboSerializer`. `ComboThumbnail` — **[CONFIRMED 14/07/2026, Gate G1]** module `ImageCore` thêm vào `FurnitureToolkit.Build.cs` (cần cho `FImageUtils::ImageResize`) + include `"Engine/Texture2D.h"`, `"ImageUtils.h"` trong `ComboThumbnail.cpp`. Chưa xác nhận module cho phần đọc PNG (`IImageWrapper` — thường cần module `ImageWrapper`, chưa thấy nhắc trong delta G1) và phần capture/RenderTarget (G0-R, `.cpp` vẫn chưa có để đối chiếu).
