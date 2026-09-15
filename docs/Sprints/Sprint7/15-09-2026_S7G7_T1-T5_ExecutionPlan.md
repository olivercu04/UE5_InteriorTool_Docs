# DELTA — S7.G7 T1–T5 EXECUTION PLAN (Material Param Panel)

**Tác giả:** Opus (senior) | **Ngày:** 15/09/2026 | **Loại:** PLAN — chưa as-built
> KHÔNG đóng dấu `[CHỨA AS-BUILT]`. Kết quả thực thi từng task cập nhật vào canonical
> (`Blueprints/` `Widgets/` `Data/`) khi as-built, KHÔNG ghi ngược file này.

**Nguồn thiết kế:** `14-09-2026_G7.0_SpikeGate_TaskCard.md` mục 9 · quyết định Đ1–Đ12 trong
`Plans/Sprint7_MaterialEdit_Plan_v1.1.md` · as-built G1 (`Data/MaterialSlotService_Reference.md`),
G2, G6 (`Widgets/WBP_FurnitureInventory.md`).

**Tiền đề:** G7.0a ĐÓNG — **GO**. Plugin `InteriorColorPicker` đã copy về `Lighting_Mnger`,
build compile sạch, plugin enabled, widget spike kéo lên PIE được (xác nhận 15/09/2026).

---

## 0. ĐỌC TRƯỚC — 2 điều định hình cả gate

### (a) Đ5 bị OVERRIDE bởi kết quả G7.0a
Đ5 gốc: *"UMG không có color picker runtime → v1 = preset + 3 slider; bánh xe màu = backlog."*
G7.0a chứng minh 3 primitive Slate (`SColorWheel`+`SSimpleGradient`+`SSlider`) sống packaged
Shipping → **bánh xe màu LÀ control màu chính của G7, không còn fallback**. Preset swatch tụt
xuống đường phụ (tùy chọn, không bắt buộc v1). → **Đánh dấu Đ5 `[HISTORICAL]` khi merge.**

### (b) Hình dạng thật: 1 task C++, 4 task wiring
`UMaterialSlotService` (14 hàm, G1 PASS) ĐÃ chứa sẵn mọi lệnh ghi param + đường undo. **T2–T5
KHÔNG viết C++ mới** — chỉ dựng UMG + nối dây vào hàm có sẵn. Bản đồ tái dùng:

| Đã có sẵn (G1/G2/G6) | Task xài |
|---|---|
| `SetSlotScalarParam` / `SetSlotVectorParam` — MID-on-demand + kiểm param tồn tại → `false` nếu sai tên (trị tận gốc bẫy "kéo slider mesh đứng im") | **T4** |
| `ClearSlotParams` — reset mức 1: xóa param, GIỮ MI | **T3** (nút "Đặt lại thông số") |
| `ResetSlotToAssetDefault` — reset mức 2, đã nối `BTN_ResetSlot` từ G2 Việc 5 | **T3** (nút "Đặt lại vật liệu" — có sẵn, không làm lại) |
| `MaterialSlots` (records, có `ParamsJson`) chụp trong `S_FurniturePlacement` + `RestoreMyMaterialSlots` gọi `ApplyParamsJsonToSlot` (Đ11) | **T4 undo = 0 dòng code undo mới** |
| `CaptureSnapshot` (Custom Event, debounce sẵn) | **T4** trigger 1 snapshot/lần nhả |
| Seam selection: `OnSlotSwatchClicked` + `NotifyViewportSlotClick`→`HighlightSwatchByIndex` (G6) | **T3** hook refresh panel |
| Picker public API: `SetColor`/`GetColor` + `OnInteractionBegin`/`OnColorChanged`/`OnInteractionEnd` | **T2** |

→ Rủi ro lớn nhất (picker sống packaged) đã đóng ở T0. Rủi ro còn lại = **tích hợp**, dồn ở **T4**.

---

## 1. BOUNDARY — cái gì KHÔNG thuộc T1–T5 (chống scope creep)

- Từ điển param THẬT (23 master family) → **G8**. T1–T5 dùng từ điển tạm **2 dòng**.
- Texture param + pattern gạch + đóng **Đ12** → **G9**. T1–T5 chỉ **Scalar + Color**.
- Compat UE 5.6/5.7/5.8 (**G7.0b**) → backlog riêng, không chặn.
- Substrate → không phải rủi ro Sprint 7 (master convert chỉ đổi `ParamName` trong DT).
- Slot khóa (`GetEditableSlots` lọc) — chưa chốt, `GetEditableSlots` v1 trả tất cả. KHÔNG mở lại ở G7.

---

## 2. T1 — `DT_MaterialParamMap` + `GetControlsForMaterial`  ⭐ TASK DUY NHẤT CÓ C++ MỚI

**Mục tiêu:** từ điển = THỰC ĐƠN (khai param nào hiện + nhãn Việt + min/max), KHÔNG chứa giá trị.
Giá trị sống trên MID + `ParamsJson` per slot (đã vậy từ G1).

**Xây (C++, thêm vào `FurnitureToolkit`):**

```cpp
UENUM(BlueprintType)
enum class EMaterialParamControl : uint8 { Scalar, Color };   // Texture để G9 thêm

USTRUCT(BlueprintType)
struct FMaterialParamControlRow : public FTableRowBase
{
    TSoftObjectPtr<UMaterialInterface> BaseMaterial;  // KHÓA tra: match theo GetBaseMaterial
    FName    ParamName;        // PHẢI trùng tên param thật trên master (service tự kiểm khi set)
    EMaterialParamControl ControlType;
    FText    LabelVI;          // nhãn tiếng Việt hiển thị trên row
    float    MinValue = 0.f;   // Scalar dùng; Color bỏ qua
    float    MaxValue = 1.f;
};

// Helper: slot MI → GetBaseMaterial → gom mọi row khớp. Ngoài từ điển → mảng rỗng.
static TArray<FMaterialParamControlRow> GetControlsForMaterial(
    UMaterialInterface* SlotMaterial, UDataTable* ParamMapDT);
```

- 1 param = 1 row. 1 master có 3 param chỉnh được = 3 row cùng `BaseMaterial`. Row-name (khóa
  DataTable) tùy ý, unique — tra bằng field `BaseMaterial`, không bằng row-name.
- Group theo **`GetBaseMaterial()`** (lần tới gốc), KHÔNG parent trực tiếp — quyết định Đ đã chốt.
- `[VERIFY T1]` chốt khóa tra là `TSoftObjectPtr` (so path) — nếu so bằng path lỗi khi MI vs
  MID khác path, đổi sang so `GetBaseMaterial()->GetFName()`. Test bằng mắt, không đoán.

**Q9:** MIỄN S-Scan (C++, không đụng `SelectedActors`) → chỉ **X-Check**. Giống G1.

**Test T1 (debug, chưa UI):** tạo `DT_MaterialParamMap` 2 dòng thật (1 scalar Roughness + 1 color
BaseColor, cùng 1 master hay dùng — vd `RM_FabricMaster`) → gọi `GetControlsForMaterial(MI_đó)`
Print ra đúng 2 row · gọi với MI ngoài từ điển → mảng rỗng · gọi với slot dùng MID (đã apply
param) → vẫn ra đúng 2 row (base material không đổi khi bọc MID).

---

## 3. T2 — `WBP_ParamScalarRow` + `WBP_ParamColorRow`

**Mục tiêu:** 2 loại row, mỗi row **chuẩn hóa vòng đời edit về đúng 3 event** để T3/T4 không cần
biết nguồn edit là wheel/slider/preset/hex:

```
OnEditBegin()                 // user bắt đầu chạm
OnPreviewChanged(FLinearColor / float)   // đang kéo — LIVE, KHÔNG snapshot
OnEditCommitted(FLinearColor / float)    // nhả — chốt 1 lần → T4 snapshot
```

**`WBP_ParamColorRow`** — nhúng `UInteriorColorPickerWidget`. Map thẳng event picker:
```
picker.OnInteractionBegin   → OnEditBegin
picker.OnColorChanged(c)    → OnPreviewChanged(c)
picker.OnInteractionEnd(c)  → OnEditCommitted(c)
```
+ ô Hex (tùy chọn) + preset swatch (đường phụ, Đ5 giáng cấp):
- Hex commit → parse: **valid** → `picker.SetColor()` (silent) + phát `OnEditBegin`→`OnEditCommitted`
  (1 thay đổi rời rạc = 1 snapshot); **fail** → **KHÔNG phát event** + inline error đỏ + revert text
  về `picker.GetColor()`. (Không event khi fail = không làm bẩn undo stack.)
- Preset click → `SetColor()` + phát committed (rời rạc, 1 snapshot).

**`WBP_ParamScalarRow`** — UMG Slider native (KHÔNG cần plugin) + SpinBox số (tùy chọn nhập chính xác):
```
Slider.OnMouseCaptureBegin → OnEditBegin
Slider.OnValueChanged(v)   → OnPreviewChanged(v)   (remap [0..1] ↔ [Min..Max])
Slider.OnMouseCaptureEnd   → OnEditCommitted(v)
SpinBox.OnValueCommitted   → Begin→Committed rời rạc
```

**Q9:** MIỄN (row standalone, không đụng `SelectedActors`) → X-Check.
**R4:** Event Destruct clear ref (nhất là ref tới panel/service). Picker wrapper tự
`ReleaseSlateResources()` (đã lo trong plugin).

**Test T2 (isolation — thả row lên 1 canvas test, chưa cần actor):** kéo wheel → thấy Begin ×1 ·
Preview nhiều lần · End ×1 (đọc bằng 3 counter như spike) · kéo slider scalar → tương tự, giá trị
remap đúng [Min..Max] · gõ hex hợp lệ → committed 1 lần, picker sync · gõ hex rác → không event +
báo đỏ + text quay lại giá trị cũ.

---

## 4. T3 — `WBP_MaterialParamPanel`

**Mục tiêu:** với slot đang chọn của `TargetFurnitureActor`, dựng đúng danh sách row từ từ điển;
MI ngoài từ điển → **panel trống** (chống set param mò).

**Build rows:**
```
RefreshParamPanel(SlotName):
  ClearChildren(VB_ParamRows)
  MI = GetMaterial(FurnitureMesh, SelectedSlotIndex)        // MI/MID đang áp trên slot
  Controls = GetControlsForMaterial(MI, DT_MaterialParamMap)  // T1 helper
  Branch(Controls.Length == 0):
    True  → hiện "Vật liệu này chưa hỗ trợ chỉnh thông số" (empty state), KHÔNG dựng row
    False → ForEach Controls → Create WBP_ParamScalarRow / WBP_ParamColorRow theo ControlType
              → set LabelVI + Min/Max + ParamName → seed giá trị hiện tại (đọc từ MID) → AddChild
```

**2 nút Reset (theo Đ — reset 2 mức):**
- "Đặt lại thông số" (**mức 1**) → `ClearSlotParams` → refresh panel. **Nút MỚI** (service có sẵn).
- "Đặt lại vật liệu" (**mức 2**) → `ResetSlotToAssetDefault` — **đã nối `BTN_ResetSlot` từ G2**,
  chỉ thêm gọi `RefreshParamPanel` sau reset. KHÔNG viết lại.

**Seam refresh (hook 2 chỗ selection có sẵn, APPEND — KP3 không sửa routine cũ):**
- Trong `NotifyViewportSlotClick`: sau `HighlightSwatchByIndex(OutSlotIndex)` → thêm
  `RefreshParamPanel(OutSlotName)`.
- Trong `OnSlotSwatchClicked` (đường click swatch): sau khi SET `SelectedSlotName` → gọi
  `RefreshParamPanel(SelectedSlotName)`.

**Vị trí panel:** dưới `HB_SlotSwatches` trong Material tab (VerticalBox phải). `[VERIFY T3]`
`BTN_MaterialEdit(disabled)` hiện là placeholder — chốt: panel hiện thẳng khi chọn slot, HAY
`BTN_MaterialEdit` bật panel. Quyết bằng mắt lúc dựng, không đoán trước.

**Q9 (S-Scan nhẹ — trạng thái chọn ảnh hưởng panel):**
- S: **0 đồ chọn** → panel Collapsed/ẩn.
- S: **multi-select** → panel theo slot của **Primary** (nhất quán swatch — "swatch hiện slot của
  Primary" đã chốt G2). T3 KHÔNG ghi gì (chỉ hiển thị), ghi là T4/T5.
- S: MI slot **ngoài từ điển** → empty state.
→ Bảng Q9 đầy đủ Opus viết trong task card T3.

**R4:** Event Destruct → `ClearChildren` + SET ref (`TargetFurnitureActor`...) = None.

**Test T3:** chọn slot có MI trong từ điển → đúng số row + đúng nhãn Việt · chọn slot MI ngoài từ
điển → empty state, không row rác · đổi actor/slot → panel rebuild sạch, không dồn row cũ · "Đặt
lại thông số" xóa param nhưng giữ MI · click swatch VÀ click-vào-mesh (G6) đều làm panel refresh.

---

## 5. T4 — Nối `MaterialSlotService` + undo   ⭐ INTEGRATION GATE

**Mục tiêu:** row emit 3 event → ghi param LIVE qua service + đúng 1 snapshot mỗi lần nhả. Đây là
điểm rủi ro cao nhất còn lại của gate.

**Wiring (panel bind 3 event của mỗi row):**
```
OnEditBegin        → (không bắt buộc làm gì; MID-on-demand để service tự lo lần set đầu)
OnPreviewChanged(v)→ SetSlotScalarParam / SetSlotVectorParam(Mesh, MaterialSlots(ref),
                       SelectedSlotName, SelectedSlotIndex, ParamName, v)   // LIVE, KHÔNG snapshot
OnEditCommitted(v) → SetSlot…Param(...) lần chốt (idempotent) → CaptureSnapshot   // 1 snapshot
```

**Tại sao undo = 0 dòng code mới (điểm cốt lõi):**
- `SetSlot…Param` cập nhật `ParamsJson` NGAY trong record của `MaterialSlots`.
- `CaptureSnapshot` chụp cả `MaterialSlots` (đã có từ G2) → param nằm trong snapshot **miễn phí**.
- Undo → `RestoreMyMaterialSlots` chạy `ResetAllSlotsToAssetDefault` rồi apply lại records **kèm
  `ApplyParamsJsonToSlot`** (Đ11) → param tự khôi phục. **Không cần đường undo riêng cho param.**
- 6A (đường ngược): forward = set param; reverse = undo phục hồi `MaterialSlots` cũ. **ĐÃ đủ đôi.**

- Snapshot chỉ ở `OnEditCommitted` (1 lần nhả = 1 snapshot). Kéo wheel/slider phát Preview nhiều
  lần → chỉ ghi MID live, KHÔNG snapshot → thay `debounce 0.5s` gốc bằng tín hiệu nhả sạch của
  picker/slider (tốt hơn: không phụ thuộc timer).
- Param sai tên → service trả `false` + log `LogMaterialSlot` (đã có) → panel bỏ qua im lặng
  (nhưng từ điển đúng thì không xảy ra).

**Q9:** đụng slot của actor đang chọn → **cần Q9** (Opus viết bảng trong task card T4). Trạng thái
cần giải: 0 chọn (panel ẩn, không có đường ghi) · single (ghi Primary) · MID-on-demand khi slot
nguyên bản chưa có MID (service tự tạo — verify record sinh `PathFallback`).

**Test T4 (integration — 1 actor):** kéo wheel màu → **mesh đổi màu LIVE** trong lúc kéo · nhả →
Undo 1 phát về màu trước · Redo về lại · kéo slider Roughness slot **nguyên bản (chưa MID)** →
service tạo MID-on-demand, mesh đổi nhám, record có `PathFallback` · apply MI khác lên slot →
`ParamsJson` bị clear (Đ6) → panel rebuild rỗng param.

> **GATE DỪNG:** T4 mà live-preview + undo KHÔNG vững (nháy, sai frame, undo lệch) → **DỪNG, báo
> cuhoang, reassess TRƯỚC khi vào T5.** Không cố kéo T5 chồng lên nền T4 chưa chắc.

---

## 6. T5 — Multi-select áp param cả cụm

**Mục tiêu:** commit param trên slot của Primary → áp cùng `ParamName`+giá trị cho MỌI actor đang
chọn **có slot cùng `SlotName`**; thiếu → skip + đếm.

**Pattern (tái dùng Hướng B của G2 Việc 3):**
```
OnEditCommitted(v):
  ForEach SelectedActors (Actor):
    ok = SetSlot…Param(Actor.Mesh, Actor.MaterialSlots(ref), SelectedSlotName, HintIndex, ParamName, v)
         // service trả false nếu actor thiếu slot/param → không ăn
    ok ? SuccessCount++ : (skip)
  Completed → CaptureSnapshot (1 lần cho cả cụm) → Toast "Áp thông số cho X/Y đồ"
```
- Preview (đang kéo) chỉ áp **Primary** (live 1 mesh, tránh N mesh giật khi kéo); cả cụm chỉ áp ở
  **Committed**. Đánh đổi này chốt để mượt — ghi vào task card.
- Snapshot cả cụm = 1 CaptureSnapshot ở Completed (không phải per-actor).

**Từ điển tạm 2 dòng (nghiệm thu end-to-end trước khi G8 điền thật):** `DT_MaterialParamMap` 2 row
(1 scalar + 1 color) — đủ chứng minh cả 2 loại row + đường multi chạy suốt.

**Q9:** đường multi đầy đủ → **Q9 FULL bảng S0–S9** (Opus viết trong task card T5). Đây là task
"nặng" S-Matrix nhất của gate. Trạng thái phải giải: single · multi cùng material · **multi trộn
material khác nhau** (chỉ actor có param đó ăn — nhất quán tinh thần G2 "áp theo tên, skip + đếm")
· none · slot khóa (N/A — chưa mở).

**Test T5:** multi-select 3 ghế cùng master → chỉnh 1 màu → cả 3 đổi + Toast "3/3" · trộn 1 ghế
master khác → chỉ ghế hợp lệ đổi + Toast "X/Y" · single vẫn đúng · Undo 1 phát hoàn tác cả cụm.

---

## 7. THỨ TỰ THỰC THI + ĐIỂM DỪNG

```
T1 (C++ dict+helper)  →  T2 (2 row widget)  →  T3 (panel build)  →  T4 (service+undo) ⭐  →  T5 (multi)
   test debug            test isolation         test single-slot     INTEGRATION GATE       test multi
```
- Mỗi task nghiệm thu độc lập (đứt gãy độc lập — đúng lý do tách task ID G7).
- **T4 là gate tích hợp thật.** Qua T4 sạch thì T5 chỉ là bọc ForEach — nhẹ.
- Không cắt task card Ti+1 khi Ti chưa PASS.

---

## 8. Q9 PER TASK (tóm tắt — bảng đầy đủ nằm trong TỪNG task card, Opus viết)

| Task | Q9 |
|---|---|
| T1 | MIỄN S-Scan (C++, không `SelectedActors`) → X-Check |
| T2 | MIỄN (row standalone) → X-Check |
| T3 | S-Scan nhẹ: 0-chọn / multi→Primary / MI-ngoài-từ-điển |
| T4 | Q9: 0 / single / MID-on-demand |
| T5 | **Q9 FULL S0–S9** (multi cùng loại / trộn loại / none / khóa=N/A) |

---

## 9. DOC SẼ ĐỤNG KHI AS-BUILT (mỗi task xong)

- `Data/MaterialSlotService_Reference.md` — thêm `GetControlsForMaterial` (T1) + struct/enum mới.
- `Data/` — file mới cho `DT_MaterialParamMap` schema (T1).
- `Widgets/` — 3 file mới: `WBP_ParamScalarRow`, `WBP_ParamColorRow` (T2), `WBP_MaterialParamPanel` (T3).
- `Widgets/WBP_FurnitureInventory.md` — seam refresh + nút "Đặt lại thông số" (T3), multi-apply (T5).
- `Widgets/InteriorColorPicker.md` — bỏ mục "Việc còn treo #1" (đã copy về `Lighting_Mnger`).
- `Plans/Sprint7_MaterialEdit_Plan_v1.1.md` — Đ5 đóng dấu `[HISTORICAL]`.
- `00_Core/`: `01_Session_State.md` (bảng G7 T0→T5, current line) · `PROGRESS.md` (bar Sprint 7) ·
  `DEVIATIONS.md` (đánh đổi Preview-Primary-only ở T5, mọi deviation phát sinh).

> Handoff chuẩn: Opus cắt task card từng Ti (self-contained: trích L liên quan + node được phép
> dùng + Q8 checklist + bảng Q9) → cuhoang thực thi với Sonnet → as-built xong, Claude Code merge
> delta vào canonical. Claude Code KHÔNG sửa mô tả node/chữ ký hàm — chỉ đóng dấu + merge + báo mâu thuẫn.
