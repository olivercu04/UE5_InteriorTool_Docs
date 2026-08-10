# DELTA — C11 Export/Import + P4-early — 10/08/2026

> **Loại:** plan đang chạy. **KHÔNG** đóng dấu `[HISTORICAL]` / `[CHỨA AS-BUILT]` — chưa có
> execution. As-built điền sau khi Sonnet chạy xong (delta riêng).
> **Nguồn patch cho:** `Plans/Post_C5_Execution_Plan_v1.md` (mục C11) + chèn task P4-early.
> **Ground truth kiến trúc:** `ComboSerializer.cpp` (cuhoang gửi 10/08) — mọi chữ ký/hành vi C++
> dưới đây đối chiếu file thật, không đoán.

---

## 0. QUYẾT ĐỊNH KIẾN TRÚC (Opus, 10/08 — phục vụ mục tiêu đóng gói app)

| # | Quyết định | Lý do |
|---|---|---|
| **QĐ1** | **P4 áp SỚM** (task P4-early) **TRƯỚC C11**, không đợi Gate 1.5 | `GetCombosDir()` thật = `ProjectSavedDir/Combos` — trong app đóng gói, update/cài lại app có thể xóa `Saved/` → **mất combo user**. Dời sang `%LOCALAPPDATA%` để combo sống qua update. Làm sớm = test đường path **1 lần** (C11 + C10 test luôn đường mới), không lặp. |
| **QĐ2** | **CẮT file dialog** (Save/Open) khỏi C11 v1 | `IDesktopPlatform` là module **editor-only** — chạy trong editor nhưng rủi ro rỗng/crash ở packaged (giống mìn Streamline). Đi ngược mục tiêu đóng gói. Dialog → backlog **sau Gate 2**. |
| **QĐ3** | **Import v1 = quét thư mục**, không picker | Export ra `Exports/`. Import quét `Exports/*.combojson`, nhập **tất cả**, move file thành công sang `Exports/Imported/` (bấm lại KHÔNG dup). Dùng `IFileManager` thuần — chắc chắn sống packaged. Không cần dựng picker widget (tránh scope creep). |
| **QĐ4** | `.combojson` **chỉ** là file export chia sẻ | Import ghi `<NewID>.json` vào `CombosDir` — library scan (`*.json`) nhặt được. **KHÔNG** bao giờ ghi `.combojson` vào `CombosDir`. Vá drift `Combo_Execution.md` (đang ghi `.json` cho file export — sửa thành `.combojson`). Chốt dùng **6 test case** (Post_C5), bỏ bản 4 case. |

Ghi chú thứ tự: **P4-early → C11 → C10 → Gate 2**. Gate 1.5 → G1.5.1 (P4) trong Post_C5 **đã dời
lên P4-early** — cập nhật G1.5.1 trỏ "đã làm ở P4-early", không làm lại.

---

## 1. TASK CARD — P4-early (làm TRƯỚC C11) — cho Sonnet

**Mục tiêu:** Dời tủ combo từ `Saved/Combos` → `%LOCALAPPDATA%/InteriorFOFFTool/Combos` để combo
sống qua update app. **KHÔNG** thêm tính năng. **KHÔNG** BP node flow — **không có Q8** (task C++ thuần).

**Đụng:** `ComboSerializer.cpp` — **CHỈ** thân hàm `GetCombosDir()`. KP3: không sửa hàm khác.

### Bước 1 — Swap thân `GetCombosDir()`
Thay:
```cpp
FString UComboSerializer::GetCombosDir()
{
    return FPaths::ProjectSavedDir() / TEXT("Combos");
}
```
bằng:
```cpp
FString UComboSerializer::GetCombosDir()
{
    // P4 (áp 10/08 qua P4-early): combo phải sống qua update app —
    // Saved/ có thể bị xóa khi rebuild/cài lại packaged.
    FString Base = FPlatformMisc::GetEnvironmentVariable(TEXT("LOCALAPPDATA"));
    if (Base.IsEmpty()) { Base = FPaths::ProjectSavedDir(); }  // fallback — rơi vào đây thì BÁO cuhoang
    FString Dir = Base / TEXT("InteriorFOFFTool") / TEXT("Combos");
    IFileManager::Get().MakeDirectory(*Dir, true);
    return Dir;
}
```
Thêm include (đầu file, cạnh các include HAL sẵn có):
```cpp
#include "HAL/PlatformMisc.h"
```
> Vì sao chỉ sửa 1 hàm là đủ: soát `ComboSerializer.cpp` — **mọi** hàm (`UpdateComboFolder`,
> `RenameFolderPrefix`, `ClearFolderPrefix`, `GetAllFolderPaths`, `GetEmptyFoldersFilePath`,
> `ListJsonFilesInDir` gián tiếp...) đều gọi `GetCombosDir()`, **không hardcode path**. `Folders.json`
> cũng theo (`GetEmptyFoldersFilePath = GetCombosDir()/Folders.json`). Đổi 1 câu trả lời = cả hệ trỏ theo.

### Bước 2 — Migrate tay 1 lần (Explorer, KHÔNG cần editor)
Copy **toàn bộ** nội dung:
```
<Project>/Saved/Combos/*    →    %LOCALAPPDATA%/InteriorFOFFTool/Combos/
```
Gồm: mọi `combo_*.json` + mọi `combo_*.png` + **`Folders.json`** (⚠ quên file này = mất folder rỗng đã tạo).
Làm **trước khi mở lại editor** để tab Combo không trống.

### Bước 3 — Verify (test bằng mắt, 1 phút)
Compile plugin → mở editor → tab Combo:
- [ ] Hiện đủ combo cũ (số lượng khớp trước migrate)
- [ ] Folder tree đủ (gồm folder rỗng)
- [ ] Thumbnail hiện
→ Đủ 3 = mọi đường đọc qua `GetCombosDir()` đúng, không BP nào hardcode lạc. **Fallback (bước 1) KHÔNG được kích** — nếu combo trống nhưng file đã migrate đúng chỗ → nghi fallback, dừng báo tao.

**3-strike:** kẹt compile 3 lần → dán nguyên error, STOP. **Làm xong 3 bước báo tao.** Rồi mới sang C11.

---

## 2. PATCH `Post_C5_Execution_Plan_v1.md` — mục C11 (9 điểm)

| # | Sửa gì trong C11 |
|---|---|
| ① | **Lô B ĐÓNG:** `GetCombosDir()` thật = `ProjectSavedDir/Combos` (P4 chưa merge). P4 **đã dời lên P4-early**, áp 10/08. Gỡ ghi chú "chưa rõ P4 revert hay chưa merge" — kết luận: **chưa từng merge**. |
| ② | **Extension:** `.combojson` = **chỉ** file export chia sẻ. Import ghi `<NewID>.json` vào `CombosDir`. **KHÔNG** ghi `.combojson` vào `CombosDir`. Chốt 6 test case (bỏ bản 4 case ở `Combo_Execution.md`). |
| ③ | **CẮT dialog (QĐ2):** bỏ toàn bộ nhánh `IDesktopPlatform`/`bDialogAvailable` trong C11.2 & C11.3. Export → thẳng Exports dir. Import → quét Exports dir. |
| ④ | **Import model (QĐ3):** thay `ImportCombo(Path)` gọi lẻ bằng `ImportAllFromExportsDir` (quét + move Imported/). `ImportCombo` giữ làm **worker** nội bộ. |
| ⑤ | **thumbnailBase64 (⑥ dưới):** `ExportCombo` **KHÔNG** tái dùng `ComboToJson()` (nó dùng `UStructToJsonObjectString` — không kèm field ngoài struct được). Build **object-level**. |
| ⑥ | **PNG = binary I/O:** `⚠ KHÔNG` dùng `SaveStringToFile`/`LoadStringFromFile` cho `.png`. Dùng `FFileHelper::LoadFileToArray` / `SaveArrayToFile`. |
| ⑦ | **ID format:** `"combo_" + FGuid::NewGuid().ToString(EGuidFormats::Digits)` (32 hex liền, khớp `combo_F8F7...` hiện có). Ghi tường minh. |
| ⑧ | **Q9 MIỄN:** C11 = library op, không đụng `SelectedActors` → chỉ X-Check. Ghi 1 dòng trong task card (chặn Sonnet từ chối vì thiếu bảng Q9). |
| ⑨ | **Field ID `[VERIFY]`:** JSON key thật là `comboId` (camelCase) → field C++ trong `FComboData` có thể là `ComboId` (không phải `ComboID`). Sonnet mở `ComboTypes.h` xác nhận tên đúng TRƯỚC khi SET. |

---

## 3. TASK CARD — C11 Export/Import combo (scope cuối) — cho Sonnet

> **Thực thi SAU khi P4-early PASS.** C11 build trên đường `%LOCALAPPDATA%`.
> **Q9:** MIỄN (library op, không đụng `SelectedActors`) — **X-Check only**.
> **L-rules áp:** L1 (IsValid trước object access), L2 (nhánh có đích), L8 (C++ call sync — không latent).
> **M-rules áp:** M7 (UTF8 — `SaveStringToFile` đã `ForceUTF8WithoutBOM`), M11 (thiếu mesh — spawn skip+toast, đã có ở spawn path), M14 (import rác — parse fail → toast, không crash).
> **KP3:** chỉ THÊM 3 hàm C++ mới. KHÔNG đụng hàm cũ trong `ComboSerializer.cpp`.

### C11.1 — C++ (THÊM 3 hàm vào ComboSerializer)

Include thêm: `#include "Misc/Base64.h"` · `#include "Dom/JsonObject.h"` (cho `FJsonObject`/`SetStringField`).

**`GetExportsDir()`** — helper, Exports là anh em của Combos (tự theo P4):
```cpp
FString UComboSerializer::GetExportsDir()
{
    FString Dir = GetCombosDir() / TEXT("..") / TEXT("Exports");
    FPaths::CollapseRelativeDirectories(Dir);
    IFileManager::Get().MakeDirectory(*Dir, true);
    return Dir;
}
```

**`ExportCombo(ComboID, OutExportedPath)`** — build JSON **object-level** + nhúng thumbnail base64:
```cpp
bool UComboSerializer::ExportCombo(const FString& ComboID, FString& OutExportedPath)
{
    const FString CombosDir = GetCombosDir();
    FString RawJson;
    if (!FFileHelper::LoadFileToString(RawJson, *(CombosDir / (ComboID + TEXT(".json")))))
        return false;

    FComboData Combo;
    if (!FJsonObjectConverter::JsonObjectStringToUStruct(RawJson, &Combo, 0, 0))
        return false;

    // object-level để CÓ THỂ thêm field ngoài struct (ComboToJson dùng ...String — KHÔNG làm được)
    TSharedPtr<FJsonObject> Obj = MakeShared<FJsonObject>();
    if (!FJsonObjectConverter::UStructToJsonObject(FComboData::StaticStruct(), &Combo, Obj.ToSharedRef(), 0, 0))
        return false;

    // thumbnail: BINARY I/O — KHÔNG dùng String helper
    TArray<uint8> PngBytes;
    if (FFileHelper::LoadFileToArray(PngBytes, *(CombosDir / (ComboID + TEXT(".png")))))
        Obj->SetStringField(TEXT("thumbnailBase64"), FBase64::Encode(PngBytes));
    // (không có .png → bỏ field, export vẫn chạy — xem test case 7)

    FString OutStr;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutStr);
    FJsonSerializer::Serialize(Obj.ToSharedRef(), Writer);

    // dest = Exports/<tên sạch>.combojson  (dấu tiếng Việt hợp lệ NTFS — giữ, M7)
    FString SafeName = Combo.Name;
    const FString Illegal = TEXT("\\/:*?\"<>|");
    for (int32 i = 0; i < Illegal.Len(); ++i) SafeName.ReplaceCharInline(Illegal[i], TEXT('_'));
    if (SafeName.IsEmpty()) SafeName = ComboID;

    OutExportedPath = GetExportsDir() / (SafeName + TEXT(".combojson"));
    return FFileHelper::SaveStringToFile(OutStr, *OutExportedPath,
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}
```

**`ImportCombo(Src, OutNewComboID, OutError)`** — worker 1 file (parse 2 lớp cùng 1 chuỗi):
```cpp
bool UComboSerializer::ImportCombo(const FString& SrcFilePath, FString& OutNewComboID, FString& OutError)
{
    FString Raw;
    if (!FFileHelper::LoadFileToString(Raw, *SrcFilePath)) { OutError = TEXT("read"); return false; }

    // lớp (a): struct sạch — converter tự bỏ field lạ "thumbnailBase64"
    FComboData Combo;
    if (!FJsonObjectConverter::JsonObjectStringToUStruct(Raw, &Combo, 0, 0)) { OutError = TEXT("parse"); return false; }

    // ID mới — format khớp file cũ (Digits, no-dash)
    OutNewComboID = TEXT("combo_") + FGuid::NewGuid().ToString(EGuidFormats::Digits);
    // [VERIFY] tên field ID trong FComboData (JSON "comboId" → field C++ có thể = ComboId). Mở ComboTypes.h.
    Combo.ComboId = OutNewComboID;   // ← sửa đúng tên field sau khi verify

    const FString CombosDir = GetCombosDir();
    FString OutJson;
    FJsonObjectConverter::UStructToJsonObjectString(Combo, OutJson, 0, 0);
    if (!FFileHelper::SaveStringToFile(OutJson, *(CombosDir / (OutNewComboID + TEXT(".json"))),
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    { OutError = TEXT("write"); return false; }

    // lớp (b): parse RAW riêng lấy base64 — BINARY write .png
    TSharedPtr<FJsonObject> Obj;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Raw);
    if (FJsonSerializer::Deserialize(Reader, Obj) && Obj.IsValid())
    {
        FString B64;
        if (Obj->TryGetStringField(TEXT("thumbnailBase64"), B64))
        {
            TArray<uint8> PngBytes;
            if (FBase64::Decode(B64, PngBytes))
                FFileHelper::SaveArrayToFile(PngBytes, *(CombosDir / (OutNewComboID + TEXT(".png"))));
        }
    }
    return true;
}
```

**`ImportAllFromExportsDir(OutImported, OutFailed)`** — quét + move (QĐ3):
```cpp
void UComboSerializer::ImportAllFromExportsDir(int32& OutImported, int32& OutFailed)
{
    OutImported = 0; OutFailed = 0;
    const FString ExportsDir = GetExportsDir();
    TArray<FString> Files;
    IFileManager::Get().FindFiles(Files, *(ExportsDir / TEXT("*.combojson")), true, false);

    const FString ImportedDir = ExportsDir / TEXT("Imported");
    for (const FString& FileName : Files)
    {
        FString NewID, Err;
        if (ImportCombo(ExportsDir / FileName, NewID, Err))
        {
            IFileManager::Get().MakeDirectory(*ImportedDir, true);
            IFileManager::Get().Move(*(ImportedDir / FileName), *(ExportsDir / FileName)); // bấm lại không dup
            ++OutImported;
        }
        else ++OutFailed;
    }
}
```
Khai UFUNCTION `BlueprintCallable` cho cả 3 (+ `ImportCombo`) trong `.h`. Compile. Lỗi → dán nguyên error, ≤3 lần (M12).

### C11.2 — Export flow (BP) — context menu ComboCard

```
Q8: Custom Event | IsValid ComboID (cache trước Hide menu) | L2: 2 nhánh bExported đều ra toast | no latent (C++ sync) | 6A: export không đổi state library — không cần reverse
```
```
CB_ExportCombo (context menu item "📤 Xuất file…"):
  ▶→ SET SaveCombo_ExportID = card ComboID  (cache trước khi đóng menu)
  ▶→ Hide context menu
  ▶→ ExportCombo(SaveCombo_ExportID) ──→ OutExportedPath, Return(bExported)
  ▶→ Branch(bExported)
       True  ▶→ ShowToast("Đã xuất: " + OutExportedPath)
       False ▶→ ShowToast("Xuất thất bại")
```

### C11.3 — Import flow (BP) — nút `BTN_ImportCombo` (cạnh tab Combo)

```
Q8: Custom Event | (không object ref cần guard) | L2: 2 nhánh count đều ra toast, success nhánh Broadcast | no latent | 6A: import thêm combo — reverse = xóa combo (flow xóa đã có), không cần undo riêng
```
```
CB_ImportCombo (BTN_ImportCombo.OnClicked):
  ▶→ ImportAllFromExportsDir ──→ OutImported, OutFailed
  ▶→ Branch(OutImported > 0)
       True  ▶→ Broadcast OnComboLibraryChanged   (tab tự refresh — bind sẵn từ C4)
              ▶→ ShowToast("Đã nhập " + OutImported + " combo" + (OutFailed>0 ? " (" + OutFailed + " lỗi)" : ""))
       False ▶→ Branch(OutFailed > 0)
                  True  ▶→ ShowToast("File combo không hợp lệ")   (M14)
                  False ▶→ ShowToast("Không có file .combojson trong thư mục Nhập: " + GetExportsDir())
```

### TEST C11 (6 case Post_C5 + 1 case thumbnail thiếu)
```
1. Export combo A → file .combojson xuất hiện trong Exports/ → mở Notepad thấy "thumbnailBase64".
2. Xóa A khỏi thư viện (xóa .json tay) → bấm Nhập → A quay lại, ComboID MỚI, .png tái tạo, card có ảnh,
   file nguồn move sang Exports/Imported/.
3. Export A 2 lần rồi Nhập (drop lại file lần 2 vào Exports) → 2 combo, ID khác nhau.
4. Bỏ file rác (.txt đổi đuôi .combojson) vào Exports → Nhập → toast lỗi, KHÔNG crash, thư viện không đổi,
   file rác KHÔNG bị move (còn ở Exports).
5. Combo tên tiếng Việt có dấu → export/import tên không vỡ (M7); file .combojson giữ dấu.
6. Import combo chứa RowName không có trong catalog máy này → import OK; spawn → skip mesh thiếu + toast (M11).
7. Export combo CHƯA có thumbnail (.png thiếu) → export chạy, .combojson không có field thumbnailBase64,
   import OK, card hiện icon 🧩 (M5/M6), KHÔNG crash.
```
**Fail 3 lần cùng 1 chỗ → STOP, quay Opus.** **Làm xong báo cuhoang + bảng 7 case.**

### Hiểu bài (sau C11 PASS — 2 câu)
1. Vì sao `ExportCombo` phải build JSON **object-level** thay vì gọi `ComboToJson()` có sẵn? (gợi ý: field `thumbnailBase64` sống ở đâu so với `FComboData`?)
2. `ImportAllFromExportsDir` move file thành công sang `Imported/`. Bỏ bước move đi thì test case nào gãy, gãy kiểu gì?

---

## 4. DEVIATIONS.md — entries mới (10/08/2026)

```
[LÔ B — ĐÓNG 10/08/2026] GetCombosDir()
  Ground truth (ComboSerializer.cpp cuhoang gửi 10/08): return ProjectSavedDir()/Combos.
  → P4 (LOCALAPPDATA, chốt 23/06) CHƯA TỪNG MERGE (không phải revert).
  → Áp qua task P4-early 10/08 (dời lên trước C11, không đợi Gate 1.5).
  → Resolve note 14/07 trong Data/Data_Structures.md.
  → Gate 1.5 G1.5.1 (P4) trong Post_C5: cập nhật "đã làm ở P4-early", không lặp.

[QĐ2 — 10/08] Cắt file dialog khỏi C11 v1.
  IDesktopPlatform = editor-only module — rủi ro packaged. Export/Import v1 dùng thư mục Exports
  (IFileManager thuần). Dialog "user tự chọn nơi lưu/mở" → backlog SAU Gate 2.

[QĐ3 — 10/08] Import v1 = quét Exports dir, nhập ALL *.combojson, move success → Exports/Imported/.
  Thay cho model "chọn 1 file qua dialog" của Post_C5. Chống dup khi bấm Nhập lại.
```

---

## 5. DOC UPDATE — cho Claude Code (canonical)

- `Plans/Post_C5_Execution_Plan_v1.md`: áp 9 điểm mục 2 vào phần C11; cập nhật G1.5.1 (P4 → "làm ở P4-early").
- `00_Core/DEVIATIONS.md`: chèn 3 entry mục 4.
- `00_Core/01_Session_State.md`: changelog 10/08 — "C11 lập kế hoạch xong; chèn task P4-early (dời P4 lên trước C11); thứ tự P4-early→C11→C10→Gate 2; cắt dialog (QĐ2); import model quét-thư-mục (QĐ3). Nguồn: DELTA_10-08-2026_C11_P4early.md." Bump dòng `Phiên bản`.
- `00_Core/02_Current_Sprint.md`: thêm 2 dòng task **P4-early** (đang chạy) + **C11** (chưa mở, sau P4-early).
- `Data/Data_Structures.md`: resolve note 14/07 GetCombosDir (P4 áp 10/08).
- **KHÔNG** đụng `Blueprints/`/`Widgets/` canonical (chưa có as-built — chờ Sonnet chạy xong).
