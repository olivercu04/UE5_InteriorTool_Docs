# P1 — Combo Thumbnail System (C++ chụp / đọc / cache)
**Version:** 1.1 | **Cập nhật:** 04/07/2026
**Vị trí trong Sprint 5:** sau WBP_Toast (K1) + Fix K3, trước C9. Móng của C7 DetailPopup, C11 Export (base64), B3/B4 sau này.
**Thực thi:** Sonnet step-by-step. Mỗi gate = 1 lần test-and-confirm, PASS mới sang gate sau.

**Changelog v1.1 (04/07/2026 — sau review Fable 5, PASS không block):**

| # | Sửa | Gate |
|---|---|---|
| 1 | Debug trigger G0: BeginPlay → **Enable Input + phím T** (chọn phương án b) | G0 |
| 2 | Clamp `Distance = Max(công thức, Radius + 15)` — chống near clip với combo siêu nhỏ | G2 |
| 3 | V2 (ExtraHiddenActors refs) kéo từ G4 lên đầu G2 | G2 |
| 4 | Thêm V6 (GUID→String format 2 phía) + V7 (pin báo json OK) | G4 |
| 5 | Ghi chú GIỮ `GetExtent().Size()` — KHÔNG đổi sang `GetMax()` (under-fit → crop) | G2 |
| 6 | 4 node Map (Find/Add/Remove/Clear) → "Nodes chờ xác nhận", confirm TRƯỚC G3 | G3 |
| 7 | `ThumbnailCache` → `Cmb_ThumbnailCache` (naming §9) | G3 |
| 8 | Q8 của G3 viết đủ 5 điểm chuẩn format | G3 |
| 9 | DEVIATIONS thêm dòng sync load = lệch tinh thần R1 có chủ đích | Doc |

Giả định KP1: `bDebugTestThumb` GIỮ tên trần theo pattern `bDebugTestFolders` (var debug tạm, gỡ sau PASS) — cuhoang muốn prefix `Cmb_` thì báo Sonnet đổi lúc tạo.

---

## 0. LUẬT THỰC THI (Sonnet ĐỌC TRƯỚC)

1. Tuần tự **P1.G0 → G5**. Mỗi bước dừng lại: "Làm xong báo tao" + test cụ thể. KHÔNG đổ nhiều gate 1 lúc.
2. Node flow mô tả bằng lời (`▶→` exec, `●→` data). Tiếng Việt thuần, tên node/biến tiếng Anh.
3. C++ dán NGUYÊN KHỐI, không gõ tay. Lỗi compile → dán nguyên error + số dòng, 3-strike rồi STOP.
4. Print String trên MAIN line, gate `bDebugMode`. Lệch plan → DEVIATIONS.md ngay.
5. Mục **[VERIFY]** = soi Blueprint thật trước khi code, lệch thì hỏi cuhoang.
6. Compile warning deprecation (vd `ImageResize`) = KỆ, không fail build — KHÔNG "tiện tay sửa warning" (KP3).

---

## 1. QUYẾT ĐỊNH ĐÃ CHỐT (03/07/2026 — không bàn lại)

| # | Quyết định |
|---|---|
| T1 | **2 tầng độ phân giải:** PNG trên ổ **1024×1024** (~300KB, sẵn cho B3/B4 upload) → cache runtime thu nhỏ **256** cho card (0.25MB VRAM/ảnh) → C7 popup đọc bản 1024 từ ổ lúc mở, đóng thì thả |
| T2 | **Phương án B:** hướng nhìn = camera hiện tại lúc bấm lưu; **khoảng cách TỰ ĐỘNG** theo bounding box (combo chiếm ~85% khung — FitRatio). Đồng nhất về CỠ, không đồng nhất về GÓC |
| T3 | v1 chụp cảnh thật như mắt thấy. **Chuẩn bị sẵn cho B3** bằng tham số: `bIsolateCombo` (chỉ render combo), `bUseFixedAngle` + `FixedAngle` (góc studio), `FitRatio`, `Resolution` — có mặt trong API từ ngày đầu, default tắt |
| — | API theo ComboID, đường dẫn giấu trong C++: `<CombosDir>/<ComboID>.png` cạnh json |
| — | Cache đặt ở **BP_ComboManager** (actor sống bền), KHÔNG ở widget — view chỉ cầm Texture2D nhẹ (R2/R3) |
| — | Gizmo + PivotActor giấu bằng **HiddenActors** của SceneCapture; outline giấu bằng tắt tạm `bRenderCustomDepth` (C++ lưu & khôi phục) |
| — | Nén PNG 1024 lúc lưu khựng ~vài chục ms, 1 lần/lần lưu → chấp nhận v1, async encode = backlog |
| — | (v1.1) Fit theo **cầu bao** `GetExtent().Size()` — conservative, combo dẹt/dài hơi nhỏ trong khung nhưng KHÔNG bao giờ tràn. Chỉnh cỡ bằng FitRatio, KHÔNG đổi công thức |

**Kiến trúc 2 chiều:**
```
CHIỀU CHỤP (1 lần, lúc SaveComboFromSelection thành công):
  máy ảnh phụ (SceneCapture2D tạm) đặt theo hướng nhìn hiện tại, lùi/tiến auto cho vừa khung
  → bấm 1 kiểu (CaptureScene, KHÔNG capture-every-frame)
  → rửa phim (ReadPixels GPU→RAM) → ép alpha đặc → nén PNG → <ComboID>.png
  → vứt máy ảnh + phim NGAY (Destroy + ReleaseRenderTarget2D)

CHIỀU ĐỌC (nhiều lần, lúc hiện card):
  BP_ComboManager.GetComboThumbnail(ComboID)
  → có trong album (Map cache) → lật album, KHÔNG đọc ổ lại
  → chưa có → LoadComboThumbnail(ComboID, 256): đọc PNG → giải nén → thu nhỏ 256 → Texture2D transient → cất album
  → EndPlay: Clear album (R4)
```

**Ngân sách VRAM (RTX 3060 8GB):** cache 256 = 0.25MB/ảnh → 50 combo = 12.5MB ✅. Popup 1024 = 4MB, mỗi lúc tối đa 1 tấm ✅. Lúc chụp: RT 1024 ~4MB sống vài frame rồi thả ✅.
Ghi chú v1.1: `CreateTransient` = 1 mip duy nhất, KHÔNG có mip chain → không có hệ số ×1.33, không cần tắt gì. LRU cache CHƯA cần v1 — backlog "LRU cap khi library > 300 combo".

---

# ═══════════════════════════════════════════════
# P1.G0 — C++ CHỤP THÔ (gate sinh tử — pipeline GPU→PNG)
# Chụp đúng vị trí camera hiện tại, CHƯA auto-fit, CHƯA tắt outline.
# ═══════════════════════════════════════════════

## Việc 1 — Build.cs
Mở `FurnitureToolkit.Build.cs` **[VERIFY tên file]**, thêm vào `PrivateDependencyModuleNames` (không có thì thêm vào Public):
```csharp
PrivateDependencyModuleNames.AddRange(new string[] { "ImageWrapper", "RenderCore", "RHI" });
```

## Việc 2 — tạo file `ComboThumbnail.h` (dán nguyên khối — .h chỉ đụng 1 LẦN, các gate sau chỉ sửa .cpp)

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ComboThumbnail.generated.h"

UCLASS()
class FURNITURETOOLKIT_API UComboThumbnail : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /** Chụp thumbnail combo → ghi <ComboID>.png cạnh json. Trả true nếu ghi file OK. */
    UFUNCTION(BlueprintCallable, Category="Combo|Thumbnail",
        meta=(WorldContext="WorldContextObject",
              AdvancedDisplay="bIsolateCombo,bUseFixedAngle,FixedAngle"))
    static bool CaptureComboThumbnail(UObject* WorldContextObject,
        const FString& ComboID,
        const TArray<AActor*>& ComboActors,
        const TArray<AActor*>& ExtraHiddenActors,
        int32 Resolution = 1024,
        float FitRatio = 0.85f,
        bool bIsolateCombo = false,
        bool bUseFixedAngle = false,
        FRotator FixedAngle = FRotator::ZeroRotator);

    /** Đọc PNG → Texture2D transient. MaxSize>0 = thu nhỏ về MaxSize; 0 = giữ nguyên 1024. */
    UFUNCTION(BlueprintCallable, Category="Combo|Thumbnail")
    static UTexture2D* LoadComboThumbnail(const FString& ComboID, int32 MaxSize = 256);

    UFUNCTION(BlueprintPure, Category="Combo|Thumbnail")
    static FString GetThumbnailPath(const FString& ComboID);

    UFUNCTION(BlueprintPure, Category="Combo|Thumbnail")
    static bool ThumbnailExists(const FString& ComboID);

    UFUNCTION(BlueprintCallable, Category="Combo|Thumbnail")
    static bool DeleteThumbnail(const FString& ComboID);
};
```

## Việc 3 — tạo file `ComboThumbnail.cpp` bản G0 (Load còn stub — G1 thay thân)

```cpp
#include "ComboThumbnail.h"
#include "ComboSerializer.h"

#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/SceneCapture2D.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Kismet/KismetRenderingLibrary.h"
#include "Kismet/GameplayStatics.h"
#include "Camera/PlayerCameraManager.h"

#include "IImageWrapper.h"
#include "IImageWrapperModule.h"
#include "Modules/ModuleManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"

FString UComboThumbnail::GetThumbnailPath(const FString& ComboID)
{
    return UComboSerializer::GetCombosDir() / (ComboID + TEXT(".png"));
}

bool UComboThumbnail::ThumbnailExists(const FString& ComboID)
{
    return FPaths::FileExists(GetThumbnailPath(ComboID));
}

bool UComboThumbnail::DeleteThumbnail(const FString& ComboID)
{
    // Delete(RequireExists=false): file không tồn tại → trả true (êm) — đúng ý combo cũ chưa có PNG
    return IFileManager::Get().Delete(*GetThumbnailPath(ComboID));
}

UTexture2D* UComboThumbnail::LoadComboThumbnail(const FString& ComboID, int32 MaxSize)
{
    // G1 thay thân hàm này
    return nullptr;
}

bool UComboThumbnail::CaptureComboThumbnail(UObject* WorldContextObject,
    const FString& ComboID, const TArray<AActor*>& ComboActors,
    const TArray<AActor*>& ExtraHiddenActors,
    int32 Resolution, float FitRatio,
    bool bIsolateCombo, bool bUseFixedAngle, FRotator FixedAngle)
{
    UWorld* World = GEngine ? GEngine->GetWorldFromContextObject(
        WorldContextObject, EGetWorldErrorMode::LogAndReturnNull) : nullptr;
    if (!World || ComboID.IsEmpty() || Resolution < 32) return false;

    // G0: chụp ĐÚNG vị trí + hướng camera hiện tại (auto-fit làm ở G2)
    APlayerCameraManager* Cam = UGameplayStatics::GetPlayerCameraManager(World, 0);
    if (!Cam) return false;
    const FVector  CamLoc = Cam->GetCameraLocation();
    const FRotator CamRot = Cam->GetCameraRotation();
    const float    FOV    = Cam->GetFOVAngle();

    // Tấm phim
    UTextureRenderTarget2D* RT = UKismetRenderingLibrary::CreateRenderTarget2D(
        World, Resolution, Resolution, RTF_RGBA8);
    if (!RT) return false;

    // Máy ảnh phụ tạm
    ASceneCapture2D* CapActor = World->SpawnActor<ASceneCapture2D>(CamLoc, CamRot);
    if (!CapActor)
    {
        UKismetRenderingLibrary::ReleaseRenderTarget2D(RT);
        return false;
    }
    USceneCaptureComponent2D* Cap = CapActor->GetCaptureComponent2D();
    Cap->TextureTarget = RT;
    Cap->CaptureSource = SCS_FinalColorLDR;      // fix "ảnh đen" — Integration_Guide
    Cap->FOVAngle = FOV;
    Cap->bCaptureEveryFrame = false;              // chụp 1 kiểu, không quay phim
    Cap->bCaptureOnMovement = false;
    Cap->bAlwaysPersistRenderingState = true;     // giữ exposure/PP state cho one-shot

    // Giấu gizmo / pivot / rác không muốn dính ảnh
    for (AActor* A : ExtraHiddenActors)
    {
        if (IsValid(A)) Cap->HiddenActors.Add(A);
    }

    // --- Plan B exposure: nếu ảnh TỐI/SÁNG bất thường → bỏ comment 3 dòng dưới ---
    // Cap->PostProcessSettings.bOverride_AutoExposureMinBrightness = true;
    // Cap->PostProcessSettings.bOverride_AutoExposureMaxBrightness = true;
    // Cap->PostProcessSettings.AutoExposureMinBrightness = Cap->PostProcessSettings.AutoExposureMaxBrightness = 1.0f;

    // Bấm chụp
    Cap->CaptureScene();

    // Rửa phim GPU → RAM (ReadPixels tự flush render commands — block game thread chờ GPU xong)
    TArray<FColor> Pixels;
    FRenderTarget* RTRes = RT->GameThread_GetRenderTargetResource();
    const bool bRead = (RTRes != nullptr) && RTRes->ReadPixels(Pixels);

    // Vứt máy ảnh + phim NGAY (chống rác VRAM)
    CapActor->Destroy();
    UKismetRenderingLibrary::ReleaseRenderTarget2D(RT);

    if (!bRead || Pixels.Num() != Resolution * Resolution) return false;

    // Ép alpha đặc (capture hay trả alpha lởm chởm → PNG loang lổ)
    for (FColor& C : Pixels) { C.A = 255; }

    // Nén PNG + ghi file (LoadModuleChecked: module đã load = tra map, rẻ — KHÔNG cần cache static)
    IImageWrapperModule& IWM =
        FModuleManager::LoadModuleChecked<IImageWrapperModule>(FName("ImageWrapper"));
    TSharedPtr<IImageWrapper> Png = IWM.CreateImageWrapper(EImageFormat::PNG);
    if (!Png.IsValid()) return false;
    if (!Png->SetRaw(Pixels.GetData(), Pixels.Num() * sizeof(FColor),
                     Resolution, Resolution, ERGBFormat::BGRA, 8)) return false;

    const TArray64<uint8>& PngData = Png->GetCompressed(100);
    return FFileHelper::SaveArrayToFile(PngData, *GetThumbnailPath(ComboID));
}
```

Compile plugin.

## TEST P1.G0 (chuỗi debug tạm — trigger bằng PHÍM T, KHÔNG bắn ở BeginPlay)

**Vì sao không BeginPlay (đổi ở v1.1):** capture bắn ngay lúc PIE start → chưa kịp xoay camera nhìn về đồ đạc → ảnh floor/void → dễ ngộ nhận "pipeline hỏng" → đốt 3-strike oan vào Plan B exposure trong khi code chạy đúng.

Trong BP_ComboManager:

1. Biến `bDebugTestThumb : Boolean = False` (pattern bDebugTestFolders — debug var tạm, gỡ sau PASS G4).
2. Event BeginPlay nối thêm:
```
▶→ Branch(bDebugTestThumb)
     True ▶→ Enable Input(Target=self, Player Controller ●← Get Player Controller(0))
```
Enable Input = "xin phép nghe bàn phím" — Actor thường KHÔNG tự nhận key event; thiếu node này bấm T sẽ im lặng không có gì xảy ra. bDebugTestThumb=False → không Enable Input → key event chết luôn, không cần Branch lần 2 trong key event.
3. Keyboard Event **T** (Pressed):
```
▶→ Get All Actors With Tag "FurnitureSpawned" ●→ Actors   ← cần ≥1 furniture đã spawn trong scene
▶→ CaptureComboThumbnail(ComboID="TestThumb", ComboActors=Actors,
     ExtraHiddenActors=[mảng rỗng], Resolution=1024) ●→ bOK
▶→ Print "G0 Capture = " + bOK
```
**[VERIFY: phím T chưa bị tool / RuntimeTransformer / Enhanced Input mapping nào dùng — trùng thì đổi phím khác, TRÁNH F8 (eject PIE).]**

Test:
1. PIE → bay/xoay camera **nhìn về phía đồ đạc** → bấm **T** → Print **true**.
2. Mở `Saved/Combos/TestThumb.png` bằng Windows Photos: ảnh **KHÔNG đen**, đúng cảnh đang nhìn, 1024×1024, màu gần giống màn hình (lệch nhẹ chấp nhận, G1 soi kỹ).
3. Ảnh dính outline xanh/gizmo = ĐÚNG dự kiến ở G0 (G2 xử).
4. Đen thui → bỏ comment khối Plan B exposure → bấm T chụp lại. Vẫn đen → STOP báo cuhoang (3-strike).

→ **Làm xong báo tao + mô tả ảnh (hoặc chụp màn hình file PNG).**

---

# ═══════════════════════════════════════════════
# P1.G1 — C++ ĐỌC PNG → TEXTURE (dán thay thân LoadComboThumbnail)
# ═══════════════════════════════════════════════

## Việc 1 — thêm 2 include vào ĐẦU ComboThumbnail.cpp (dưới các include sẵn có)
```cpp
#include "ImageUtils.h"
#include "Engine/Texture2D.h"
```

## Việc 2 — dán thay nguyên hàm `LoadComboThumbnail`

```cpp
UTexture2D* UComboThumbnail::LoadComboThumbnail(const FString& ComboID, int32 MaxSize)
{
    TArray<uint8> FileData;
    if (!FFileHelper::LoadFileToArray(FileData, *GetThumbnailPath(ComboID)))
    {
        return nullptr; // chưa có ảnh — card giữ fallback, KHÔNG phải lỗi
    }

    IImageWrapperModule& IWM =
        FModuleManager::LoadModuleChecked<IImageWrapperModule>(FName("ImageWrapper"));
    TSharedPtr<IImageWrapper> Png = IWM.CreateImageWrapper(EImageFormat::PNG);
    if (!Png.IsValid() || !Png->SetCompressed(FileData.GetData(), FileData.Num()))
        return nullptr;

    TArray<uint8> Raw;
    if (!Png->GetRaw(ERGBFormat::BGRA, 8, Raw)) return nullptr;

    const int32 W = Png->GetWidth();
    const int32 H = Png->GetHeight();
    if (W <= 0 || H <= 0 || Raw.Num() != W * H * 4) return nullptr;

    TArray<FColor> Src;
    Src.SetNumUninitialized(W * H);
    FMemory::Memcpy(Src.GetData(), Raw.GetData(), Raw.Num());

    // Thu nhỏ về MaxSize (nguồn luôn vuông vì capture vuông)
    TArray<FColor> Final;
    int32 OutW = W, OutH = H;
    if (MaxSize > 0 && (W > MaxSize || H > MaxSize))
    {
        OutW = MaxSize; OutH = MaxSize;
        FImageUtils::ImageResize(W, H, Src, OutW, OutH, Final, /*bLinearSpace*/ false);
        // Nếu compile báo thiếu tham số: thêm ", true" vào cuối call (bForceOpaqueOutput)
        // Deprecation WARNING (engine dồn về ImageCore) = kệ, không fail build, KHÔNG sửa (KP3)
    }
    else
    {
        Final = MoveTemp(Src);
    }

    UTexture2D* Tex = UTexture2D::CreateTransient(OutW, OutH, PF_B8G8R8A8);
    if (!Tex) return nullptr;
    void* Mip = Tex->GetPlatformData()->Mips[0].BulkData.Lock(LOCK_READ_WRITE);
    FMemory::Memcpy(Mip, Final.GetData(), Final.Num() * sizeof(FColor));
    Tex->GetPlatformData()->Mips[0].BulkData.Unlock();
    Tex->SRGB = true;
    Tex->UpdateResource();
    return Tex;
}
```

## TEST P1.G1
Nối tiếp chuỗi debug G0 (sau Print G0, CÙNG chain phím T — bấm T là chạy cả chụp lẫn load):
```
▶→ LoadComboThumbnail("TestThumb", 256) ●→ SET local TexTest
▶→ Print "G1 Load valid = " + IsValid(TexTest)
▶→ Set Brush from Texture(IMG_Debug, TexTest)   ← Image tạm đặt góc WBP_MeshControls, xóa sau PASS
```
`Set Brush from Texture` chưa có trong file 09 → **cuhoang xác nhận node** rồi thêm vào bảng.
1. Print true; ảnh hiện trên IMG_Debug đúng màu — KHÔNG nhạt bệch, KHÔNG tối xỉn (sai gamma → báo, nghi SRGB).
2. Gọi Load với ComboID không tồn tại → Print false, không crash.

→ **Làm xong báo tao.**

---

# ═══════════════════════════════════════════════
# P1.G2 — CHẤT LƯỢNG CHỤP: auto-fit + tắt outline + tham số B3
# ═══════════════════════════════════════════════

## [VERIFY — V2, kéo lên từ G4 (v1.1)] soi TRƯỚC khi làm G2:
Ref `BP_TransformerPawn` + `BP_PivotActor` lấy từ đâu để làm ExtraHiddenActors — biến sẵn có trong BP_ComboManager? `Get All Actors With Tag "FurniturePivot"`? `Get All Actors Of Class`? Không thấy → hỏi cuhoang.
PivotActor vắng mặt lúc chụp (chưa select group) → mảng rỗng = **vô hại** — C++ đã IsValid từng phần tử, loop không chạy.

## Việc 1 — thêm include (đầu .cpp): `#include "Components/PrimitiveComponent.h"`

## Việc 2 — dán thay nguyên hàm `CaptureComboThumbnail` (bản đầy đủ, thay bản G0)

```cpp
bool UComboThumbnail::CaptureComboThumbnail(UObject* WorldContextObject,
    const FString& ComboID, const TArray<AActor*>& ComboActors,
    const TArray<AActor*>& ExtraHiddenActors,
    int32 Resolution, float FitRatio,
    bool bIsolateCombo, bool bUseFixedAngle, FRotator FixedAngle)
{
    UWorld* World = GEngine ? GEngine->GetWorldFromContextObject(
        WorldContextObject, EGetWorldErrorMode::LogAndReturnNull) : nullptr;
    if (!World || ComboID.IsEmpty() || Resolution < 32 || ComboActors.Num() == 0)
        return false;

    // 1) Bounding box gộp của cả cụm
    FBox Bounds(ForceInit);
    for (AActor* A : ComboActors)
    {
        if (IsValid(A)) Bounds += A->GetComponentsBoundingBox(true);
    }
    if (!Bounds.IsValid) return false;
    const FVector Center = Bounds.GetCenter();
    // Radius = GetExtent().Size() = bán kính CẦU BAO quanh hộp — GIỮ NGUYÊN.
    // KHÔNG đổi sang GetExtent().GetMax(): under-fit → nhìn chéo góc đỉnh hộp lòi khung (crop).
    const float   Radius = FMath::Max(Bounds.GetExtent().Size(), 1.0f);

    // 2) Hướng nhìn: camera hiện tại (T2-B) hoặc góc cố định (B3)
    APlayerCameraManager* Cam = UGameplayStatics::GetPlayerCameraManager(World, 0);
    if (!Cam) return false;
    const float    FOV     = Cam->GetFOVAngle();
    const FRotator ViewRot = bUseFixedAngle ? FixedAngle : Cam->GetCameraRotation();
    const FVector  Dir     = ViewRot.Vector();

    // 3) Khoảng cách TỰ ĐỘNG cho combo chiếm ~FitRatio khung
    //    RT vuông → FOV dọc = FOV ngang, công thức đối xứng 2 trục.
    const float HalfFOVRad = FMath::DegreesToRadians(FMath::Max(FOV, 10.0f) * 0.5f);
    const float BaseDist   = (Radius / FMath::Tan(HalfFOVRad))
                             / FMath::Clamp(FitRatio, 0.1f, 1.0f);
    // (v1.1) Clamp tối thiểu: không chui vào trong combo / dưới near clip (~10cm)
    // — combo siêu nhỏ (Radius ~1) sẽ cho Distance ~1-2cm → mesh bị near plane cắt nếu không clamp.
    const float Distance   = FMath::Max(BaseDist, Radius + 15.0f);
    const FVector CamLoc   = Center - Dir * Distance;

    // 4) Phim + máy ảnh
    UTextureRenderTarget2D* RT = UKismetRenderingLibrary::CreateRenderTarget2D(
        World, Resolution, Resolution, RTF_RGBA8);
    if (!RT) return false;
    ASceneCapture2D* CapActor = World->SpawnActor<ASceneCapture2D>(CamLoc, ViewRot);
    if (!CapActor)
    {
        UKismetRenderingLibrary::ReleaseRenderTarget2D(RT);
        return false;
    }
    USceneCaptureComponent2D* Cap = CapActor->GetCaptureComponent2D();
    Cap->TextureTarget = RT;
    Cap->CaptureSource = SCS_FinalColorLDR;
    Cap->FOVAngle = FOV;
    Cap->bCaptureEveryFrame = false;
    Cap->bCaptureOnMovement = false;
    Cap->bAlwaysPersistRenderingState = true;

    for (AActor* A : ExtraHiddenActors)
    {
        if (IsValid(A)) Cap->HiddenActors.Add(A);
    }

    // Chuẩn bị B3: chỉ render combo, giấu cả thế giới
    if (bIsolateCombo)
    {
        Cap->PrimitiveRenderMode = ESceneCapturePrimitiveRenderMode::PRM_UseShowOnlyList;
        for (AActor* A : ComboActors)
        {
            if (IsValid(A)) Cap->ShowOnlyActors.Add(A);
        }
    }

    // --- Plan B exposure: ảnh tối/sáng bất thường → bỏ comment ---
    // Cap->PostProcessSettings.bOverride_AutoExposureMinBrightness = true;
    // Cap->PostProcessSettings.bOverride_AutoExposureMaxBrightness = true;
    // Cap->PostProcessSettings.AutoExposureMinBrightness = Cap->PostProcessSettings.AutoExposureMaxBrightness = 1.0f;

    // 5) Tắt tạm outline (Custom Depth) của combo — lưu để khôi phục
    TArray<UPrimitiveComponent*> DepthOn;
    for (AActor* A : ComboActors)
    {
        if (!IsValid(A)) continue;
        TInlineComponentArray<UPrimitiveComponent*> Prims;
        A->GetComponents(Prims);
        for (UPrimitiveComponent* P : Prims)
        {
            if (P && P->bRenderCustomDepth)
            {
                DepthOn.Add(P);
                P->SetRenderCustomDepth(false);
            }
        }
    }

    // 6) Bấm chụp + rửa phim
    Cap->CaptureScene();
    TArray<FColor> Pixels;
    FRenderTarget* RTRes = RT->GameThread_GetRenderTargetResource();
    const bool bRead = (RTRes != nullptr) && RTRes->ReadPixels(Pixels);

    // 7) Khôi phục outline NGAY (kể cả khi đọc fail)
    for (UPrimitiveComponent* P : DepthOn)
    {
        if (IsValid(P)) P->SetRenderCustomDepth(true);
    }

    CapActor->Destroy();
    UKismetRenderingLibrary::ReleaseRenderTarget2D(RT);

    if (!bRead || Pixels.Num() != Resolution * Resolution) return false;

    for (FColor& C : Pixels) { C.A = 255; }

    IImageWrapperModule& IWM =
        FModuleManager::LoadModuleChecked<IImageWrapperModule>(FName("ImageWrapper"));
    TSharedPtr<IImageWrapper> Png = IWM.CreateImageWrapper(EImageFormat::PNG);
    if (!Png.IsValid()) return false;
    if (!Png->SetRaw(Pixels.GetData(), Pixels.Num() * sizeof(FColor),
                     Resolution, Resolution, ERGBFormat::BGRA, 8)) return false;

    const TArray64<uint8>& PngData = Png->GetCompressed(100);
    return FFileHelper::SaveArrayToFile(PngData, *GetThumbnailPath(ComboID));
}
```

## TEST P1.G2 (dùng lại chuỗi debug phím T, ComboID="TestThumb2")
1. Select 2–3 furniture (đang có outline) → bấm T chạy chụp với `ExtraHiddenActors = [TransformerPawn, PivotActor nếu có]` (refs theo V2 đã verify ở đầu gate) → ảnh: cụm đồ **giữa khung, ~85% chiều khung, KHÔNG outline, KHÔNG gizmo**.
2. Combo nhỏ (1 ghế) và combo to (giường + tủ + bàn) → 2 ảnh cùng CỠ tương đối trong khung (đồng nhất cỡ — băn khoăn T2 giải quyết ở đây).
3. Chỉnh nếu lệch: combo nhỏ quá trong khung → tăng FitRatio 0.85 → 0.95; sát mép → giảm 0.75. Chốt số → ghi DEVIATIONS. (Combo dẹt/dài hơi nhỏ = đặc tính cầu bao, chỉnh bằng FitRatio, KHÔNG đổi công thức.)
4. Thử `bIsolateCombo=true` 1 lần cho biết (ảnh chỉ có combo, nền đen/trời) — chỉ smoke-test tham số B3, không cần đẹp.
5. Camera auto lùi xuyên tường → ảnh dính mặt trong tường: GHI NHẬN tần suất, chưa fix (backlog line-trace clamp).

→ **Làm xong báo tao + nhận xét 2 ảnh to/nhỏ.**

---

# ═══════════════════════════════════════════════
# P1.G3 — CACHE TRONG BP_ComboManager (album ảnh)
# ═══════════════════════════════════════════════

## [Nodes chờ xác nhận — làm TRƯỚC khi nối G3 (v1.1)]
4 node **Map Find / Map Add / Map Remove / Map Clear** chưa có trong bảng NODE CHÍNH XÁC (lần đầu project dùng BP Map). Ghi vào mục "Nodes chờ xác nhận" của AI_Implementation_Rules.md → cuhoang confirm trong project 1 lần → mới dùng trong flow. PASS G4 thì chuyển 4 node vào bảng chính.

## Q8 self-check
```
Q8: Function thuần (GetComboThumbnail — Load C++ sync, không latent) | IsValid(LoadedTex) trước Map Add ✓ | L2: mọi nhánh có Return, không dead-end ✓ | No Latent ✓ | 6A: đường ngược = InvalidateThumbnail (chụp lại/xóa) + DeleteThumbnail (xóa file) + EndPlay Map Clear (R4) ✓
```
- Impure call → SET local trước khi dùng (bài học TempGroups).

## Biến mới (BP_ComboManager)
`Cmb_ThumbnailCache : Map<String, Texture2D>` (default rỗng)
— prefix `Cmb_` theo naming §9: class var dùng chung ≥3 event/function (GetComboThumbnail / InvalidateThumbnail / EndPlay).
— BP variable = UPROPERTY dưới nắp → tự chặn GC cho texture transient. **KHÔNG AddToRoot** (sống xuyên PIE = leak, phá R4).

## Function `GetComboThumbnail(ComboID : String) → Texture2D`
```
▶→ Map Find(Cmb_ThumbnailCache, ComboID) ●→ CachedTex, bFound
▶→ Branch(bFound)
     True  ▶→ Return CachedTex                          ← lật album
     False ▶→ LoadComboThumbnail(ComboID, MaxSize=256) ●→ SET Local LoadedTex
            ▶→ Branch(IsValid(LoadedTex))
                 True  ▶→ Map Add(Cmb_ThumbnailCache, ComboID, LoadedTex) ▶→ Return LoadedTex
                 False ▶→ Return None                    ← chưa có ảnh, card giữ 🧩
```

## Function `InvalidateThumbnail(ComboID : String)`
```
▶→ Map Remove(Cmb_ThumbnailCache, ComboID)     ← gọi khi chụp lại / xóa / import đè
```

## Event End Play (BP_ComboManager) — nối thêm
```
▶→ Map Clear(Cmb_ThumbnailCache)               ← R4, chống VRAM leak qua PIE
```

## TEST P1.G3
Debug: gọi GetComboThumbnail("TestThumb2") 3 lần liền + Print IsValid — lần 1 đọc ổ, lần 2–3 tức thì (không thấy khựng). ComboID rác → None êm.

→ **Làm xong báo tao.**

---

# ═══════════════════════════════════════════════
# P1.G4 — NỐI DÂY VÀO FLOW THẬT (save / hiển thị / xóa)
# ═══════════════════════════════════════════════

**[VERIFY] 6 điểm trước khi nối (soi BP, báo lại):**
- V1: trong `SaveComboFromSelection` — tên mảng actors đang dùng + vị trí Broadcast `OnComboLibraryChanged`.
- V2: → **đã verify ở đầu G2** (kéo lên v1.1), dùng lại kết quả.
- V3: `BP_ComboItemView` — thêm biến `Thumbnail : Texture2D` (view cầm CON TRỎ tới texture shared với cache, không copy — R3 vẫn thỏa).
- V4: chỗ WBP_ComboCard đang set fallback 🧩 (OnListItemObjectSet?).
- V5: flow xóa combo (C8) — chỗ gọi DeleteFileAtPath.
- **V6 (MỚI v1.1): GUID→String format 2 phía phải khớp.** Path PNG khóa theo ComboID string. Node convert GUID→String lúc CHỤP (Nối 1) và giá trị `view.ComboID` lúc ĐỌC (Nối 2) phải cùng nguồn / cùng format (Digits vs DigitsWithHyphens...). Lệch format → thumbnail KHÔNG BAO GIỜ tìm thấy, fail ÊM không error — soi node conversion cả 2 phía, tốt nhất lấy đúng string đã ghi vào json.
- **V7 (MỚI v1.1): tín hiệu "ghi json thành công".** SaveComboFromSelection có pin/bool nào báo ghi file OK? Nối 1 cắm SAU tín hiệu đó — không có thì hỏi cuhoang chỗ nối, KHÔNG tự đoán (KP1).

## Nối 1 — chụp lúc lưu (BP_ComboManager.SaveComboFromSelection)
Sau khi ghi json thành công (pin theo V7), **TRƯỚC** Broadcast OnComboLibraryChanged:
```
▶→ CaptureComboThumbnail(WorldContext=self, ComboID=<GUID vừa tạo, string theo V6>,
     ComboActors=<mảng V1>, ExtraHiddenActors=<V2>, Resolution=1024) ●→ SET Local bThumbOK
▶→ Print "Thumb capture = " + bThumbOK        [gate bDebugMode]
▶→ (tiếp Broadcast như cũ)                    ← chụp fail KHÔNG chặn lưu combo
```

## Nối 2 — hiển thị (LoadComboLibrary, chỗ build từng BP_ComboItemView)
```
▶→ GetComboThumbnail(view.ComboID) ●→ SET view.Thumbnail
```
WBP_ComboCard (chỗ V4):
```
▶→ Branch(IsValid(Item.Thumbnail))
     True  ▶→ Set Brush from Texture(IMG_Thumb, Item.Thumbnail)
     False ▶→ (giữ fallback 🧩 như cũ)
```

## Nối 3 — xóa combo (chỗ V5)
```
▶→ DeleteThumbnail(ComboID) ▶→ InvalidateThumbnail(ComboID)   ← nối sau DeleteFileAtPath
```

## TEST P1.G4 (end-to-end)
1. Select cụm → Save combo "SofaTV" → card hiện ẢNH THẬT ngay (không cần restart).
2. Ảnh sạch: không outline, không gizmo, không dialog (SceneCapture không chụp UI — kỳ vọng đúng).
3. Combo cũ (chưa PNG) vẫn 🧩 êm, không lỗi.
4. Xóa combo → PNG biến mất khỏi `Saved/Combos/`, card gone.
5. Thao tác folder liên tục (move/rename ×5) → ảnh card KHÔNG nháy load lại (cache ăn), không khựng.
6. Restart PIE → card vẫn ảnh thật (đọc từ ổ qua cache).

→ **Làm xong báo tao + bảng 6 case. PASS = xóa chuỗi debug G0–G3 (gồm Enable Input + Key T + IMG_Debug + bDebugTestThumb).**

---

# ═══════════════════════════════════════════════
# P1.G5 — REGRESSION VRAM (bắt buộc — vết thương cũ)
# ═══════════════════════════════════════════════

Console `stat rhi`, ghi số **Render target memory + Texture memory** tại 4 mốc:
1. Baseline sau khi vào PIE.
2. Sau khi lưu 5 combo liên tiếp (5 lần chụp 1024).
3. Sau mở/đóng inventory tab Combo ×5 + thao tác folder ×10.
4. Sau Alt+Z / Save / Load scene vài vòng (thumbnail không dính EMS/undo — số không đổi).

Kỳ vọng: mốc 2 ≈ baseline + (0.25MB × số combo hiển thị) — KHÔNG tăng theo SỐ LẦN chụp (RT đã release); mốc 3 = mốc 2 (cache, không load lại); chênh lệch bất thường >20MB → STOP, nghi leak, báo cuhoang. Ghi 4 số vào DEVIATIONS.

→ **PASS = P1 DONE.**

---

## RỦI RO & PLAN B

| Triệu chứng | Plan B (theo thứ tự, 3-strike) |
|---|---|
| Ảnh đen | Đã phòng sẵn: SCS_FinalColorLDR + bAlwaysPersistRenderingState. Còn đen → bỏ comment khối khóa exposure → vẫn đen → chụp lùi 1 frame (Delay 0.0 trong Custom Event trước Capture — hỏi Fable) |
| Bấm T không có gì xảy ra | Quên Enable Input ở BeginPlay, hoặc bDebugTestThumb=False, hoặc phím T bị mapping khác nuốt → đổi phím |
| Ảnh tối/sáng bất thường | Khối khóa exposure (comment sẵn trong code) |
| Compile: ImageResize sai số tham số | Thêm `, true` cuối call (bForceOpaqueOutput). Deprecation WARNING = kệ (KP3) |
| Combo nhỏ xíu/tràn khung | Chỉnh FitRatio (0.75–0.95), chốt số ghi DEVIATIONS. KHÔNG đổi Size()→GetMax() |
| Combo hiện 🧩 dù đã chụp OK | Nghi V6: GUID→String lệch format 2 phía → so string path file trên ổ với ComboID trong ItemView |
| Camera auto lùi xuyên tường | Ghi nhận v1; backlog: line trace từ Center ngược Dir, clamp Distance |
| Khựng lúc lưu (encode 1024) | Chấp nhận v1 (1 lần/lưu); backlog: AsyncTask encode |
| Mở tab 20+ combo khựng | Backlog: rải GetComboThumbnail qua nhiều frame |

## SẴN SÀNG CHO TƯƠNG LAI (đã cài trong API, không cần đập lại)
- **B3 trang bán:** nút "Chụp lại bìa" = gọi lại Capture với `bUseFixedAngle` + `bIsolateCombo` → InvalidateThumbnail → **PHẢI Broadcast OnComboLibraryChanged** để rebuild views (view cũ vẫn cầm con trỏ texture CŨ — không broadcast thì card hiện ảnh cũ tới khi list regenerate).
- **C7 popup:** `LoadComboThumbnail(ComboID, 0)` → bản 1024 — gọi TRỰC TIẾP, KHÔNG đi qua GetComboThumbnail (đừng nhét bản 4MB vào cache 256); Event Destruct SET None (R4).
- **C11 export:** đọc file PNG (path từ `GetThumbnailPath`) → base64 nhúng json; import ngược → ghi PNG + InvalidateThumbnail.
- **B4 upload:** file 1024 nằm sẵn trên ổ, upload thẳng.
- **LRU cache:** chưa cần — cân nhắc khi library > 300 combo (~75MB).

## DOC UPDATES SAU KHI PASS
`Session_State` + `PROGRESS` (P1 DONE + 4 số VRAM); `DEVIATIONS` (FitRatio chốt, tần suất xuyên tường, **sync PNG load/encode chấp nhận v1 — lệch tinh thần R1 có chủ đích, backlog async**, lệch phát sinh); tạo `ComboThumbnail_Reference.md` (API + 2 tầng độ phân giải + sơ đồ 2 chiều); `BP_ComboManager.md` bump (cache + 2 function); `WBP_ComboCard.md` bump; file 09 thêm `Set Brush from Texture` + 4 node Map (sau khi cuhoang xác nhận) + note module ImageWrapper trong Build.cs.
