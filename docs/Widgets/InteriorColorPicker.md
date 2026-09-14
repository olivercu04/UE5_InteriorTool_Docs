# InteriorColorPicker (plugin C++ Slate/UMG)
**Version:** 1.0 | **Ngày:** 14/09/2026 | **Tạo mới — G7.0a SpikeGate, đóng GO**

> 📌 **[CHỨA AS-BUILT]** — mục "Files" + "Flow code C++ chi tiết" dưới đây là kết quả thực thi
> thật (build PASS, PIE + packaged Dev/Shipping test), KHÔNG phải plan. Nguồn:
> `14-09-2026_G7.0_AsBuilt_Delta_FULL.md` (thay bản rút gọn `14-09-2026_G7.0_AsBuilt_Delta.md`).

## Vai trò
Plugin C++ độc lập (`Plugins/InteriorColorPicker/`), cung cấp 1 color picker (wheel H/S + slider
V dọc) cho Sprint 7 G7 (động cơ panel param material — slider/color). Compose từ 3 primitive Slate
sẵn có trong engine (`SColorWheel`, `SSimpleGradient`, `SSlider`) — không tự vẽ widget mới.

**Trạng thái G7.0a (SpikeGate):** ĐÓNG — GO (PASS). 3 widget xác nhận sống packaged Shipping
(10/10 case, PIE + packaged Development + packaged Shipping, build ExitCode=0). Fallback Đ5
(preset swatch) không dùng tới.

**Code thật hiện nằm ở project C++ standalone riêng (KHÔNG phải `Lighting_Mnger`) — xem mục
"Quyết định kiến trúc". CHƯA copy về `Lighting_Mnger`, chặn trước khi bắt đầu G7.1.**

## Files
Tất cả dưới `Plugins/InteriorColorPicker/Source/InteriorColorPicker/`.

| File | Trạng thái |
|---|---|
| `InteriorColorPicker.uplugin` | Có sẵn từ trước G7.0a |
| `InteriorColorPicker.Build.cs` | Có sẵn — G7.0a sửa: thêm `Engine` (xem Kiến trúc quyết định) |
| `Public/InteriorColorPicker.h` / `Private/InteriorColorPicker.cpp` | Có sẵn |
| `Public/InteriorHSVState.h` / `Private/InteriorHSVState.cpp` | Có sẵn — namespace convert (KHÔNG member struct) |
| `Public/SInteriorColorPicker.h` / `Private/SInteriorColorPicker.cpp` | **Mới (G7.0a)** — `SCompoundWidget` compose wheel + gradient + slider |
| `Public/InteriorColorPickerWidget.h` / `Private/InteriorColorPickerWidget.cpp` | **Mới (G7.0a)** — `UWidget` wrapper, API production |
| `Public/InteriorColorPickerSpikeWidget.h` / `Private/InteriorColorPickerSpikeWidget.cpp` | **Mới (G7.0a)** — `UUserWidget` test harness (chỉ spike, bỏ khi production) |
| `Public/InteriorColorPickerSpikeActor.h` / `Private/InteriorColorPickerSpikeActor.cpp` | **Mới (G7.0a)** — `AActor` spawn widget test harness |

Không có Blueprint node/WBP asset nào trong phiên G7.0a — toàn bộ C++ thuần (spike widget/actor
cũng dựng bằng `WidgetTree`, không K2Node).

## Convert layer — `InteriorHSVState` (namespace, PURE)
```
namespace InteriorColorPicker::
   UpdateHSVFromLinearColor(const FInteriorHSVState& CurrentState, const FLinearColor& NewColor)
       → trả FInteriorHSVState MỚI (không mutate in-place)
       rule: S_new > AchromaticSaturationThreshold(1e-4) ? update H : giữ H cũ
   HSVToLinearColor(const FInteriorHSVState& State) → FLinearColor
```
Gọi: `State = UpdateHSVFromLinearColor(State, Color);` (gán lại, KHÔNG method trên struct).

## SInteriorColorPicker (SCompoundWidget)
State: `FInteriorHSVState State` + `bool bIsInteracting`.
```
Construct():
  State = UpdateHSVFromLinearColor(FInteriorHSVState(), InArgs._InitialColor)
  lưu 3 delegate (Begin / ColorChanged / InteractionEnd)
  ChildSlot:
    SHorizontalBox
    ├─ SBox(200x200) → SColorWheel
    │     .SelectedColor      = TAttribute → GetWheelColor()
    │     .OnMouseCaptureBegin/OnValueChanged/OnMouseCaptureEnd → Handle*
    └─ SBox(32x200) → SOverlay
          ├─ SSimpleGradient
          │     .StartColor  = TAttribute → GetGradientEndColor()  [màu sáng, LÊN TRÊN]
          │     .EndColor    = Black                                [xuống dưới]
          │     .Orientation = Orient_Horizontal   [ra dải DỌC — xem gotcha, ngược trực giác]
          └─ SSlider
                .Orientation = Orient_Vertical
                .Value       = TAttribute → GetSliderValue() (= State.V)
                .OnMouseCaptureBegin/OnValueChanged/OnMouseCaptureEnd → Handle*

Wheel: chỉ set State.H = NewValue.R, State.S = NewValue.G (KHÔNG chạm V)
Slider: set State.V trực tiếp
Begin → OnInteractionBegin · Changed → apply + OnColorChanged(GetColor()) · End → OnInteractionEnd(GetColor())
GetColor() = HSVToLinearColor(State)
SetColorSilent(Color): if bIsInteracting return; State = UpdateHSVFromLinearColor(State, Color); KHÔNG broadcast
GetGradientEndColor(): tmp=State; tmp.V=1; return HSVToLinearColor(tmp)
```

## UInteriorColorPickerWidget (UWidget wrapper — API production, BẤT BIẾN)
```
SetColor(FLinearColor) [BlueprintCallable] → MyColorPicker->SetColorSilent (nếu IsValid)
GetColor() → FLinearColor
Event OnInteractionBegin / OnColorChanged(FLinearColor) / OnInteractionEnd(FLinearColor) [BlueprintAssignable]
InitialColor [EditAnywhere]

RebuildWidget(): SNew(SInteriorColorPicker) + bind 3 handler qua FSimpleDelegate/CreateUObject → return ToSharedRef()
ReleaseSlateResources(): Super:: + MyColorPicker.Reset()   [chống VRAM leak — SWidget không tự chết theo UWidget]
```
Binding dùng `CreateUObject` (không phải `this,&Func` — UWidget là UObject, khác SCompoundWidget).

## Test harness (spike only, bỏ khi production)
`InteriorColorPickerSpikeWidget` (UUserWidget, build tree trong `Initialize()` — KHÔNG
`NativeConstruct`, tree phải có trước RebuildWidget đầu) + `InteriorColorPickerSpikeActor`
(AActor, `BeginPlay` spawn widget + `SetInputMode(FInputModeUIOnly())` + `SetShowMouseCursor(true)`
— bắt buộc, thiếu = chuột không tới widget).

## Quyết định kiến trúc — package ở project standalone
Spike package ở **project C++ standalone MỚI** (rỗng, chỉ chứa plugin `InteriorColorPicker`),
KHÔNG package trên `Lighting_Mnger`.

**Lý do:** `Lighting_Mnger` là bản copy project tổng → ~67 plugin marketplace precompiled →
package dính "missing precompiled manifest" hàng loạt (lộ `DLSSMoviePipelineSupport`, y hệt Gate
1.5). `InteriorColorPicker` không coupling `Foff_GameInstance`/`WBP_FOFF_ToolDemo` → tách sạch,
build từ source (không dính precompiled manifest).

**Ghi nhớ cho G7.1:** code panel param quay về `Lighting_Mnger` thật. Project standalone chỉ là
bàn thử spike, bỏ sau. Packaged-viability của 3 widget đã chứng minh riêng — G7.1 không cần test
lại tầng đó, chỉ test integration.

## Build.cs delta
`PublicDependencyModuleNames` thêm `Engine` (từ `{Core, CoreUObject, UMG, Slate, SlateCore}`) —
`AInteriorColorPickerSpikeActor` cần `AActor`/`APlayerController`/`UGameplayStatics`/
`FInputModeUIOnly`. Chỉ phục vụ spike harness; production `UInteriorColorPickerWidget` không đụng
Engine. Xem `DEVIATIONS.md` mục SPRINT 7 14/09/2026.

## Gotcha kỹ thuật (G7.0a)
1. Compile pass ≠ đúng ngữ nghĩa — `.Orientation(Orient_Vertical)` compile được nhưng vô tác
   dụng nếu trùng default; A/B đổi giá trị ngược mới biết tham số có tác dụng thật.
2. `SSimpleGradient.Orientation` ngược trực giác: `Orient_Horizontal` cho ra dải màu chạy DỌC —
   tham số mô tả hướng các dải màu, không phải trục widget.
3. Forward-declare ≠ dùng được: `UUserWidget.h` chỉ forward-declare `UWidgetTree` → phải tự
   `#include "Blueprint/WidgetTree.h"`.
4. 2 tầng lỗi build: compile (thiếu header) vs link (thiếu module trong Build.cs) — 225
   `unresolved external` toàn `AActor::*` = thiếu module `Engine`, không phải thiếu include.
5. Cascade Slate (`SNew(...).Arg(...)[...]`) — 1 arg sai kiểu vỡ cả chuỗi; tìm dòng
   `no overloaded function`/`does not name a type` ĐẦU TIÊN trong log.
6. Delegate 0-param vs 1-param: `OnMouseCaptureBegin/End` = 0 param; `OnValueChanged` = 1 param.
   Handler End không nhận param — State đã được Changed cập nhật sống lúc kéo rồi.
7. 2 hệ vòng đời độc lập: UObject theo GC, SWidget theo refcount SharedPtr — `CreateUObject` tự
   hủy binding khi GC; `ReleaseSlateResources → Reset()` vẫn bắt buộc.
8. Live Coding chặn Build qua VS ("Unable to build while Live Coding is active") — đóng Editor
   hoặc Ctrl+Alt+F11 khi cần build sạch cho gate.
9. Source plugin package sạch, marketplace precompiled thì không — tách plugin độc lập sang
   project rỗng để package = né "missing precompiled manifest" của project tổng.

## Test G7.0a — 10/10 case PASS (14/09/2026)
| Tầng | Kết quả |
|---|---|
| PIE (`Lighting_Mnger`) | Case tương tác #1–#8 PASS |
| Packaged Development `.exe` | 10/10 case PASS · 3 widget render + tương tác đúng |
| Packaged Shipping `.exe` | Build SUCCESSFUL (ExitCode=0) · 10/10 case PASS · không symbol bị strip |

Case #9 (regression guard SetColor achromatic) sửa so với task card gốc v1.0 — đã áp vào
`Sprints/Sprint7/14-09-2026_G7.0_SpikeGate_TaskCard.md` v1.1, xem `DEVIATIONS.md` mục SPRINT 7
14/09/2026.

## Việc còn treo
1. **Copy 5+ file plugin ngược về `Lighting_Mnger`** — code thật đang ở project standalone. Làm
   trước khi bắt đầu G7.1.
2. Trả lại packaging settings ở `Lighting_Mnger` nếu phiên nào đụng (List of Maps / Game Default Map).
3. G7.0b compat (5.6/5.7/5.8) chưa chạy — tách entry backlog, không chặn G7.1.

---

## Lịch sử cập nhật

| Ngày | Version | Nội dung |
|------|---------|----------|
| 14/09/2026 | 1.0 | Tạo mới. G7.0a SpikeGate ĐÓNG — GO (PASS). 3 primitive Slate sống packaged Shipping, 10/10 case. Package ở project standalone riêng (né precompiled-manifest lỗi kiểu Gate 1.5). Build.cs +Engine. Chi tiết: `01_Session_State.md`, `DEVIATIONS.md`, `PROGRESS.md`. |
