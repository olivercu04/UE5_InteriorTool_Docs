# ComboSerializer / ComboThumbnail — C++ Blueprint Function Library Reference
**Nguồn:** `ComboSerializer.h`/`.cpp` + `ComboThumbnail.h` (cuhoang paste 14/07/2026 — source thật, không copy `.cpp` ComboThumbnail vì chưa có)
**Tạo:** 14/07/2026 — bổ sung docs/Data (3+ tuần chưa cập nhật theo Sprint 5 Combo + P1 Thumbnail)

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

## Class: UComboThumbnail (P1, MỚI 14/07/2026 — Gate G0-R)
**Plugin:** FurnitureToolkit | **Files:** `ComboThumbnail.h` (chưa có `.cpp`) | Base: `UBlueprintFunctionLibrary`
> Xem bối cảnh kiến trúc (vì sao tách Begin/Finish thay vì 1 hàm one-shot): `DEVIATIONS.md` [ARCH] 14/07/2026, node flow debug: `Blueprints/Blueprint_Logic_NodeFlow.md` §BP_ComboManager.

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

### BeginComboCapture(...) → ASceneCapture2D* (handle)
```cpp
static ASceneCapture2D* BeginComboCapture(UObject* WorldContextObject,
    const TArray<AActor*>& ComboActors,
    const TArray<AActor*>& ExtraHiddenActors,
    int32 Resolution = 1024);
```
Bước 1/2: spawn camera phụ tại vị trí camera hiện hành, bật render liên tục (`bCaptureEveryFrame=true`, warm-up cho Lumen GI/TAA hội tụ). Trả về handle — caller (Blueprint) giữ trong class var, `Delay` một khoảng rồi gọi `FinishComboCapture`. Test debug (phím T, `BP_ComboManager`) chốt tạm `Delay(3.0)` — xem `01_Session_State.md` mục P1.

### FinishComboCapture(CaptureHandle, ComboID) → bool
```cpp
static bool FinishComboCapture(ASceneCapture2D* CaptureHandle, const FString& ComboID);
```
Bước 2/2: đọc frame đã hội tụ → ghi `<ComboID>.png` cạnh file combo `.json` (cùng `GetCombosDir()`) → tự dọn actor + RenderTarget, **kể cả khi đọc/ghi fail** (R4-style cleanup). Trả `false` nếu ghi file thất bại — Blueprint KHÔNG gate Save Combo theo giá trị này (combo vẫn lưu OK, card fallback icon 🧩 nếu capture fail).

### LoadComboThumbnail(ComboID, MaxSize) → UTexture2D*
```cpp
static UTexture2D* LoadComboThumbnail(const FString& ComboID, int32 MaxSize = 256);
```
Đọc PNG → `Texture2D` transient. `MaxSize>0` = thu nhỏ về `MaxSize`; `0` = giữ nguyên 1024 (resolution capture gốc). **Hiện đang STUB `return nullptr`** — đây chính là Gate P1.G1 (đọc PNG→Texture2D), chưa implement thân hàm thật.

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
| `LoadComboThumbnail` thân thật | P1.G1 | Đang stub `return nullptr` |
| Auto-fit khung hình (FitRatio dùng thật) | P1.G2 | `CaptureComboThumbnail` có param `FitRatio` nhưng `BeginComboCapture` KHÔNG có — cần xác nhận field này còn áp dụng ở đâu trong pipeline mới |
| Cache ảnh trong BP_ComboManager | P1.G3 | Node Map — chưa xác nhận, xem `Rules/AI_Implementation_Rules.md` mục "Nodes chờ xác nhận" |

Xem checklist đầy đủ: `00_Core/PROGRESS.md` mục P1.

---

## Lưu ý tích hợp

- Plugin: `FurnitureToolkit` — cùng plugin với `FurnitureFilterLibrary`, `UComboSerializer`, `UComboThumbnail`.
- `ComboThumbnail.h` include forward-declare `class ASceneCapture2D;` — không include full header `SceneCapture2D.h` ở `.h` (giữ nhẹ), thật ra include ở `.cpp` (chưa có để đối chiếu).
- Dependency: `FJsonObjectConverter` (module `JsonUtilities`) cho `ComboSerializer`; `.cpp` `ComboThumbnail` chắc chắn cần `ImageWrapper`/`ImageUtils` (PNG I/O) — chưa xác nhận Build.cs vì chưa có `.cpp`.
