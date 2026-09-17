# DELTA — S7G7 T3·T4·T4b·T5 TASK CARDS (Material Inspector — wiring)

**Tác giả:** Sonnet (senior) | **Ngày:** 17/09/2026 | **Loại:** PLAN — chưa as-built

> ⚠️ **[T3.3+T3.4 ĐÃ AS-BUILT 18/09/2026 — 3 chỗ trong file này SAI, xem `[HISTORICAL]` inline]**
> Nguồn as-built thật: `Sprints/Sprint7/18-09-2026_S7G7_T3-T4_ASBUILT_delta.md`, merge vào
> `Widgets/WBP_FurnitureInventory.md` v3.30, `Blueprints/BP_FurnitureActor.md` v2.5. 3 chỗ plan SAI
> so với as-built thật: (1) `SetHighlight` trên `BTN_MaterialEdit` — hàm không tồn tại, as-built
> dùng `Set Background Color`; (2) `Cast → BP_FurnitureActor` trong `RefreshParamPanel` — dư, biến
> `TargetFurnitureActor` đã khai kiểu `BP_FurnitureActor_C` sẵn, UE5.5 chặn compile; (3) seam #5
> (`SwitchInventoryMode`) đặt "CUỐI nhánh Material" — plan để Ở ĐẦU hàm, gây highlight fail im lặng
> vì swatch chưa Visible. Seam #6/#7 (`EndParamSession`, T4b) trong file này **CHƯA build** — vẫn
> còn giá trị làm plan cho T4b. GIỮ nguyên nội dung gốc bên dưới để tra lý do đã từng quyết vậy.
> **rev6 (17/09):** áp review kiến trúc vòng 2 (phản biện ngoài) — 6 sửa + 1 giữ-có-bằng-chứng:
> - **#1 GIỮ suppress theo Material mode, sửa MÔ TẢ SAI của rev5.** Ground-truth verify:
>   `SwitchInventoryMode` Collapse `HB_SlotSwatches` mỗi lần đổi mode, chỉ hiện lại ở Material; nhánh
>   Material của `OnMeshSelected` (set `TargetFurnitureActor`) gate bằng `CurrentInventoryMode==Material`.
>   → `tab Material` KHÔNG phải "filter thuần" mà là **CỔNG material-context**. Rời Material = swatch
>   ẩn + không update target → suppress Inspector là ĐÚNG ràng buộc hiện có. Tách context khỏi mode
>   = refactor Polish (flag), không làm G7.
> - **#2** `RefreshParamPanel` render state SẠCH: breadcrumb + footer luôn khớp state hiển thị; reset
>   buttons **disabled** khi chưa slot; check biên `0 <= idx < SlotNames.Length`.
> - **#3** KHÔNG build param row khi Inspector hidden (guard đầu `RefreshParamPanel`) — tốt cho máy yếu.
> - **#4 (must-fix)** `Handle_ResetParamsRequested`: `ClearSlotParams`→`ok`→`Branch(ok)` mới snapshot
>   (nhất quán rule "snapshot chỉ khi service thành công").
> - **#5 (must-fix)** T5: resolve `SelectedSlotName`→`ActorSlotIndex` cho TỪNG actor TRƯỚC `GetMaterial`
>   (KHÔNG dùng index Primary đọc MI actor phụ). Guard tương thích match `ParamName + ControlType`.
> - **#6** selection-set đổi = ranh giới undo session: `OnSelectionChanged → EndParamSession`.
> - **Docking phrasing + RULE MỚI:** "move logic không rewrite"; từ T3, hàm cụm Material Controller
>   KHÔNG phát sinh dependency mới vào Library tree/card/filter ngoài seam đã định.
> - **T3.5 ra khỏi critical path**; sửa expected-result (collapse Library chỉ giải phóng chỗ TRONG
>   Inventory 512px, KHÔNG giãn viewport/Inspector).
>
> **Giữ nguyên rev5:** bỏ `WBP_MaterialSlotTab` (swatch = control canonical duy nhất) · "duplicate
> IDENTITY không duplicate CONTROL" · lifecycle `bInspectorOpen`(ý định) ≠ selection · property-surface
> 8 nguyên tắc · content ~360px · dispatcher reset ownership · `CanvasPanel_Root` bọc `Border` ·
> `SlotName:String` · `bIsRestoring` guard đầu `CaptureParamSnapshot` · snapshot chỉ khi ok=true.
> KHÔNG đóng dấu `[CHỨA AS-BUILT]`.

**Nguồn:** `15-09-2026_S7G7_T1-T5_ExecutionPlan.md` · Đ4/Đ6/Đ7/Đ11 + M2 (`Plans/Sprint7_MaterialEdit_Plan_v1.1.md`)
· T1 (`Data/MaterialSlotService_Reference.md`) · T2 (`WBP_ParamScalarRow.md`,`WBP_ParamColorRow.md`) ·
G2/G6 (`WBP_FurnitureInventory.md`) · doc UX 16/09 · đồng bộ UX 16-17/09 (memory `docking-workspace-plan.md`).

**Tiền đề PASS:** T1 · T2 · **T3.1** (`WBP_MaterialParamPanel`; `ShowEmptyState(bEmpty,Message)` PASS).

**Ground-truth verify 17/09:**
- `HB_SlotSwatches` ∈ `WBP_FurnitureInventory > VerticalBox phải` = `HB_SwatchList` + `BTN_MaterialEdit(disabled)`
  + `BTN_ResetSlot` + `BTN_ResetAll`.
- `SwitchInventoryMode`: Collapse `HB_SlotSwatches` mọi mode; Material branch → "Visible SlotSwatches
  nếu có actor". `OnMeshSelected` Material branch gate `CurrentInventoryMode==Material` → set `TargetFurnitureActor`.
- `RefreshSlotSwatches`/`HighlightSwatchByIndex`/`NotifyViewportSlotClick` = G6 PASS 6/6, đọc `HB_SwatchList`
  của chính Inventory → KHÔNG dời.
- `WBP_SlotSwatch` v1.2: `SlotIndex:Int`, `SlotName:String`, `OnSwatchClicked`, `SetSelected` (Image
  overlay), `UpdateThumbnail`.
- `WBP_DetailPopup` v1.3 = info đồ + Scale editor (không thuộc domain material).

---

## 0. ĐỌC TRƯỚC

### 0.1 Không viết C++ mới. Tái dùng
| Có sẵn | Task |
|---|---|
| `GetControlsForMaterial(MI, DT)` → Array<`FMaterialParamControlRow`> (có `ParamName`+`ControlType`) | T3 build row · **T5 guard match ParamName+ControlType per-actor** |
| `WBP_ParamScalarRow`/`WBP_ParamColorRow.Setup` + 3 dispatcher | T3 |
| `WBP_MaterialParamPanel` (T3.1) — `VB_ParamRows`, `ShowEmptyState`, `ClearRows`/`AddRow`, `Event Destruct` | T3.2 |
| `WBP_SlotSwatch`+`HB_SlotSwatches`+`RefreshSlotSwatches`/`HighlightSwatchByIndex` (G6) | control slot canonical, GIỮ NGUYÊN |
| `NotifyViewportSlotClick` (G6) chạy ngay sau `OnMeshSelected` | T3.4 resolve slot khi click-mesh |
| `SetSlotScalarParam/SetSlotVectorParam(...)`→bool · `ClearSlotParams(...)`→bool · `ResetSlotToAssetDefault` | T4/T5 (DÙNG bool trước snapshot) |
| `GetMaterialSlotNames`(StaticMeshComponent) → resolve tên→index per-actor | **T5 #5** |
| `CaptureSnapshot`/`CaptureMaterialSnapshot`; `RestoreMyMaterialSlots`+`ApplyParamsJsonToSlot` (Đ11) | T4/T4b |

### 0.2 Nguyên lý (KISS·YAGNI·SoC·Docking-prep)
- **SoC 3 tầng:** Content (`WBP_MaterialParamPanel`) · Chrome (`WBP_MaterialInspector`, phơi Function
  pass-through, không tự gọi service) · Controller (`WBP_FurnitureInventory`) · Service C++.
- **Docking-ready (diễn đạt chuẩn):** Sprint 7 làm Inspector CONTENT docking-ready + giữ Material
  orchestration thành cụm boundary rõ để **extract** sau (move logic, KHÔNG rewrite). Details tương
  lai KHÔNG được phụ thuộc `WBP_FurnitureInventory` còn sống.
- **RULE cụm Material Controller (từ T3):** các hàm material (`RefreshParamPanel`, `Open/Close/Update
  InspectorVisibility`, `Handle_*`, `RefreshSlotSwatches`, `HighlightSwatchByIndex`) trong Inventory
  KHÔNG phát sinh dependency MỚI vào Library tree/card/filter, ngoài seam UI đã định.

### 0.3 Ràng buộc thiết kế Inspector — 8 nguyên tắc property-surface
Không Apply/OK/Cancel · edit live viewport · X chỉ đóng bề mặt (không cancel) · header ngắn · footer
Reset thuộc content · không lưu state quan trọng trong floating window · content ~360px vertical stack
NGAY BÂY GIỜ · persistent+contextual+live+không tự đoán selection · luôn nói rõ "đang chỉnh gì".

### 0.4 BOUNDARY (KP2)
KHÔNG thuộc T3-T5: từ điển thật (G8) · texture (G9) · slot-khóa · combo lưu param (Đ3) · animation/
glow-hint · docking thật · dời `HB_SlotSwatches` · **tách material-context khỏi InventoryMode** (Polish).
**CÓ:** collapse Library (T3.5 — độc lập, off critical path).

### 0.5 THỨ TỰ (T3.5 OFF critical path)
```
T3.1(PASS) → T3.2 → T3.3 → T3.4 → T4 ⭐GATE → T4b → T5
T3.5 (collapse Library) = độc lập, làm khi thuận tiện, KHÔNG block T4
```

### 0.6 Node đọc seed giá trị — ĐÃ XÁC NHẬN 17/09 (hands-on, không còn "chờ")
`Material Interface` (kiểu `MI`) KHÔNG có getter trực tiếp. Phải **Cast MI → Material Instance
Dynamic** trước, rồi gọi `Get Scalar/Vector Parameter Value` trên kết quả Cast. Cast fail (slot
chưa từng chỉnh, chưa có MID theo Đ4) → fallback: Scalar=`Ctrl.MinValue`, Color=trắng `(1,1,1,1)`.
Đã vào node flow T3.3 chính thức.

---

# ═══════════════════════════════════════
# S7G7T3 — Material Inspector (property surface)
# ═══════════════════════════════════════

## Kiến trúc
```
WBP_MaterialInspector          (top-level, edge-overlay, anchor phải ~360px)
CanvasPanel_Root                (ROOT full-viewport, Self Hit Test Invisible)
└── Border_InspectorRoot        (Anchor Min(1,0) Max(1,1) Align(1,0))
    └── VerticalBox_Root
        ├── HB_Header: TextBlock_Title (ngắn) · Spacer · BTN_Close
        ├── TextBlock_Breadcrumb   (projection chỉ-đọc, khớp state)
        ├── ScrollBox_Content → ParamPanelRef : WBP_MaterialParamPanel
        └── HB_Footer (content): BTN_ResetParams · BTN_ResetSlot
```
KHÔNG slot tabs. `BTN_ResetAll` giữ ở `HB_SlotSwatches` (Inventory).

## Dispatcher/Function
```
Inspector → Inventory (dispatcher): OnCloseRequested · OnResetParamsRequested · OnResetSlotRequested
Inventory → Inspector (Function pass-through):
  SetHeader(Breadcrumb:Text) · ClearParamRows() · AddParamRow(Row) · ShowParamEmptyState(bEmpty,Message)
  SetResetEnabled(bEnabled:bool)   ← MỚI rev6 #2: enable/disable BTN_ResetParams+BTN_ResetSlot
```

---

## T3.1 — `WBP_MaterialParamPanel` — ✅ PASS. Thêm 2 pass-through:
```
Function ClearRows():   ClearChildren(VB_ParamRows)
Function AddRow(Row):   AddChild(VB_ParamRows, Row)
```

---

## T3.2 — Chrome `WBP_MaterialInspector`
Dựng cây trên. Root `CanvasPanel_Root` (Self Hit Test Invisible), con `Border_InspectorRoot` anchor phải.
`HB_Footer` ngoài `ScrollBox_Content`. Kéo `WBP_MaterialParamPanel` vào → `ParamPanelRef`.
```
Function SetHeader(Breadcrumb:Text):  TextBlock_Breadcrumb.SetText(Breadcrumb)
Function ClearParamRows():            ParamPanelRef.ClearRows()
Function AddParamRow(Row):            ParamPanelRef.AddRow(Row)
Function ShowParamEmptyState(bEmpty,Message): ParamPanelRef.ShowEmptyState(bEmpty,Message)
Function SetResetEnabled(bEnabled):   BTN_ResetParams.SetIsEnabled(bEnabled) ; BTN_ResetSlot.SetIsEnabled(bEnabled)

BTN_Close.OnClicked:       Call OnCloseRequested()
BTN_ResetParams.OnClicked: Call OnResetParamsRequested()
BTN_ResetSlot.OnClicked:   Call OnResetSlotRequested()
```
**Q8:** Function pass-through: không object access ngoài widget con → miễn IsValid | L2 1 dòng | No latent | 6A N/A.

**TEST T3.2:** SetHeader đúng · Add/ClearParamRow đúng · ShowParamEmptyState 2 case · SetResetEnabled(false)
→ 2 nút xám không bấm được · 3 dispatcher bắn đúng · footer đứng yên khi cuộn. → PASS → T3.3.

---

## T3.3 — `RefreshParamPanel` (Function, Inventory) — STATE-RENDER SẠCH (rev6 #2/#3)

**Biến thêm Inventory:**
```
MaterialInspectorRef : WBP_MaterialInspector
DT_ParamMap          : DataTable (default DT_MaterialParamMap)
bInspectorOpen       : Boolean (F)   ← ý định (Open/Close only)
bInspectorSuppressed : Boolean (F)   ← ẩn tạm khi rời Material mode
```
**Helper:**
```
Function IsInspectorVisible() → bool:  Return AND(bInspectorOpen, NOT bInspectorSuppressed)
```

**Node flow — guard hidden đầu tiên (#3), header/footer khớp state (#2), bounds đúng:**
```
Function RefreshParamPanel()
▶→ Branch( IsInspectorVisible() )  False ▶→ Return            ← #3: hidden thì KHÔNG build gì
   True:
   ▶→ Branch( IsValid(TargetFurnitureActor) )
        False ▶→ SetHeader("") · SetResetEnabled(false)
              ▶→ ShowParamEmptyState(true, "Chọn một đối tượng để chỉnh vật liệu") ▶→ Return
        True:
          Cast → BP_FurnitureActor (bSuccess)   ← [HISTORICAL — SAI, xem banner đầu file] as-built
                                                    18/09 KHÔNG Cast (biến đã khai kiểu sẵn, Cast dư
                                                    → UE5.5 chặn compile)
          bSuccess=False ▶→ SetHeader("") · SetResetEnabled(false)
                         ▶→ ShowParamEmptyState(true, "Đối tượng này không có vật liệu chỉnh sửa được") ▶→ Return
          True:
            ActorName = Get Display Name(TargetFurnitureActor)
            GET FurnitureMesh → GetMaterialSlotNames ●→ SlotNames
            ▶→ Branch( SlotNames.Length == 0 )
                 True ▶→ SetHeader(ActorName) · SetResetEnabled(false)
                      ▶→ ShowParamEmptyState(true, "Đối tượng này không có vật liệu chỉnh sửa được") ▶→ Return
                 False:
                   ▶→ Branch( AND( SelectedSlotIndex >= 0, SelectedSlotIndex < SlotNames.Length ) )   ← #2 bounds
                        False ▶→ SetHeader(ActorName) · SetResetEnabled(false)                         ← chưa slot: header CHỈ tên actor, không nối slot cũ
                              ▶→ ShowParamEmptyState(true, "Chọn một vùng vật liệu trong thanh Material Slots để bắt đầu chỉnh sửa") ▶→ Return
                        True:                                                                          ← slot hợp lệ
                          ▶→ SetHeader( Conv_StringToText(ActorName + " · " + SelectedSlotName) )       [VERIFY hiển thị]
                          ▶→ SetResetEnabled(true)
                          ▶→ MI = GetMaterial(SelectedSlotIndex)
                          ▶→ ClearParamRows()
                          ▶→ GetControlsForMaterial(MI, DT_ParamMap) ●→ Controls
                          ▶→ Branch(Controls.Length == 0)
                               True ▶→ ShowParamEmptyState(true, "Vật liệu này chưa hỗ trợ chỉnh thông số") ▶→ Return
                               False ▶→ ShowParamEmptyState(false, "")
                                    ▶→ ForEach Controls (Ctrl):
                                         Switch Ctrl.ControlType:
                                           Scalar: Cast MI → Material Instance Dynamic (bSuccess)
                                                     True  ▶→ Get Scalar Parameter Value(Target=CastResult, Ctrl.ParamName) ●→ SeedF
                                                     False ▶→ SET SeedF = Ctrl.MinValue        ← slot chưa từng chỉnh (chưa có MID, Đ4)
                                                   Create WBP_ParamScalarRow ●→ RowS
                                                   RowS.Setup(Ctrl.LabelVI, Ctrl.ParamName, Ctrl.MinValue, Ctrl.MaxValue, SeedF)
                                                   Bind RowS.OnPreviewChanged → Handle_ScalarPreview (T4)
                                                   Bind RowS.OnEditCommitted  → Handle_ScalarCommit (T4)
                                                   AddParamRow(RowS)
                                           Color:  Cast MI → Material Instance Dynamic (bSuccess)
                                                     True  ▶→ Get Vector Parameter Value(Target=CastResult, Ctrl.ParamName) ●→ SeedV
                                                     False ▶→ SET SeedV = LinearColor(1,1,1,1)  ← trắng, slot chưa từng chỉnh
                                                   Create WBP_ParamColorRow ●→ RowC
                                                   RowC.Setup(Ctrl.LabelVI, Ctrl.ParamName, SeedV)
                                                   Bind RowC.OnPreviewChanged → Handle_ColorPreview (T4)
                                                   Bind RowC.OnEditCommitted  → Handle_ColorCommit (T4)
                                                   AddParamRow(RowC)
                                       Completed ▶→ Return
```
> **[VERIFY XÁC NHẬN 17/09 — hands-on]** `Material Interface` (kiểu của `MI`) KHÔNG có getter trực
> tiếp — chỉ `Material Instance Dynamic` mới có `Get Scalar/Vector Parameter Value` runtime-safe.
> Cast tường minh bắt buộc (Blueprint không tự downcast kiểu cha→con). Cast fail = slot CHƯA từng
> chỉnh (chưa có MID theo Đ4) → ca BÌNH THƯỜNG, không phải lỗi — dùng fallback đã định sẵn.
> **Invariant #2:** breadcrumb + footer LUÔN khớp nội dung: không actor→header trống+reset off ·
> actor 0 slot→tên actor+reset off · chưa slot→tên actor+reset off · slot hợp lệ→"actor · slot"+reset on.
> KHÔNG bao giờ để breadcrumb giữ slot cũ khi placeholder.

**Q8:** Function | IsValid Target ✓ | L2 mọi nhánh Return ✓ | No latent | 6A N/A (không đụng bInspectorOpen).

**TEST T3.3 (giả lập, Inspector visible=true):**
1. idx hợp lệ+MI trong từ điển → row+breadcrumb "actor · slot"+reset on.
2. idx=-1 → placeholder, breadcrumb CHỈ tên actor (không slot cũ), reset OFF.
3. idx vượt trần (giả lập idx=99) → coi như chưa slot (nhánh bounds False), không crash.
4. Cast fail/0 slot → "không có vật liệu", reset off.
5. `IsInspectorVisible=false` → gọi `RefreshParamPanel` KHÔNG tạo widget nào (Print đếm children=0).
→ PASS 5/5 → T3.4.

---

## T3.4 — Toggle + lifecycle + seam (Hướng 2)

**Event Construct (APPEND):** Create Inspector → SET ref → Collapsed → Add to Viewport → Bind 3
dispatcher (`OnCloseRequested`→`Handle_InspectorCloseRequested`; `OnResetParamsRequested`→stub T3.4/thân
T4; `OnResetSlotRequested`→`Handle_ResetSlotRequested`).
**Event Destruct:** `Branch(IsValid ref): True → RemoveFromParent → SET ref=None`.

**Trung tâm hiển thị:**
```
Function UpdateInspectorVisibility():   MaterialInspectorRef.SetVisibility( IsInspectorVisible() ? Visible : Collapsed )
Function OpenMaterialInspector():   SET bInspectorOpen=True · BTN_MaterialEdit.SetHighlight(true) · UpdateInspectorVisibility() · RefreshParamPanel()
Function CloseMaterialInspector():  SET bInspectorOpen=False · BTN_MaterialEdit.SetHighlight(false) · UpdateInspectorVisibility()
   ← [HISTORICAL — SAI, xem banner đầu file] `SetHighlight` KHÔNG tồn tại trên `BTN_MaterialEdit`.
     As-built 18/09 dùng `Set Background Color(BTN_MaterialEdit, ColorButtonChoose/ColorButtonDefault)`.
BTN_MaterialEdit.OnClicked:  Branch(bInspectorOpen): True→Close ; False→Open
Handle_InspectorCloseRequested():  Call CloseMaterialInspector()
Handle_ResetSlotRequested():   Branch(IsValid Target AND idx>=0): True → Cast→Mesh → ResetSlotToAssetDefault(...) → CaptureSnapshot("ResetSlot") → RefreshSlotSwatches → RefreshParamPanel
Handle_ResetParamsRequested():  STUB T3.4 (Print), thân thật T4
```

**Seam (APPEND, KP3):**
| # | Routine | APPEND rev6 |
|---|---|---|
| 1 | `OnSlotSwatchClicked` | sau SET `SelectedSlotName`: `BTN_MaterialEdit.SetIsEnabled(true)` · `RefreshParamPanel()` (tự guard hidden) |
| 2 | `NotifyViewportSlotClick` (G6) | sau `HighlightSwatchByIndex`: y hệt #1 |
| 3 | `OnMeshSelected` nhánh Material | cạnh `RefreshSlotSwatches`: enable/disable nút theo có slot · `RefreshParamPanel()` · **`UndoManagerRef.EndParamSession()`** (#6) · KHÔNG đóng Inspector |
| 4 | `LoadAndApplyMaterial` Completed | `RefreshParamPanel()` |
| 5 | `SwitchInventoryMode` | đầu hàm: **SET bInspectorSuppressed = (NewMode != Material)** · `UpdateInspectorVisibility()` · Branch(NewMode==Material AND IsInspectorVisible): True→`RefreshParamPanel()` (rebuild khi hiện lại) — ⚠️ **[HISTORICAL — SAI vị trí, xem banner đầu file]** cụm `RefreshParamPanel`/highlight PHẢI đặt CUỐI nhánh Material (sau khi `HB_SlotSwatches` đã Visible), KHÔNG phải đầu hàm — as-built 18/09 đã sửa, đặt đầu hàm gây highlight fail im lặng vì swatch chưa dựng xong |
| 6 | `OnSceneRestored` (T4) | sau SET Target: `RefreshParamPanel()` |
| 7 | `OnMeshSelected` (đầu, mọi nhánh) | **`UndoManagerRef.EndParamSession()`** (#6 — selection đổi = ranh giới session) — có thể gộp với #3 |

> #1 (suppress theo Material) đúng ground-truth: rời Material, swatch ẩn + target không update →
> Inspector "dai" cũng vô nghĩa. Suppress = ẩn tạm, KHÔNG phá `bInspectorOpen`; về Material → hiện lại.
> `[VERIFY #6]` đổi secondary selection (A+B→A+C giữ Primary A) có fire `OnMeshSelected`/`OnSelectionChanged`
> không — nếu KHÔNG, phải hook `EndParamSession` tại chỗ mutate selection-set (InputManager). Test T4b #10 kiểm.

**Q8:** Update/Open/Close: L2 có đích, No latent, 6A đóng=ẩn state giữ ở controller ✓ · Handle_ResetSlotRequested:
IsValid ✓, Undo qua snapshot ✓ · Construct/Destruct: IsValid Destruct ✓.

**Q9 S-SCAN (nhẹ):** S0 actor=None→empty-state, KHÔNG đóng · S1 chính · S2-S4/S7/S8 ⚠ Primary · S5/S6 →S1 · S9 ⚠ seam#6.
**Q9 X-CHECK:** X1 không snapshot ở hiển thị (reset-slot 1 lần) · X3 mở/đóng/ẩn không đổi tab/folder · X9 đọc MI không ghi.

**TEST T3.4:**
1. Có slot → `BTN_MaterialEdit` → hiện đúng row/breadcrumb/nút highlight.
2. Toggle lại / `X` → đóng (2 đường).
3. **Đã chọn slot TRƯỚC rồi mới mở** → mở thẳng param, không chớp placeholder.
4. Đang mở → click mesh khác (G6) → không chớp tắt, resolve slot, row ngay.
5. Đang mở → chọn actor qua đường khác → placeholder, tự pick swatch → row.
6. Đang mở → actor KHÔNG hỗ trợ material → empty-state, **KHÔNG đóng**.
7. Đang mở → click swatch → breadcrumb+row đổi ngay; reset buttons enabled.
8. Chưa chọn slot → reset buttons **disabled** (bấm không phản ứng).
9. Đang mở → kéo material từ Library → row refresh, không đóng.
10. Đang mở → tab Furniture → **ẩn**; về tab Material → **hiện lại state cũ**.
11. Xoay camera/click viewport → không đóng. `[VERIFY]` click nền deselect → empty-state, vẫn mở.
12. `BTN_ResetSlot` (có slot) → material gốc, refresh, Undo đúng.
13. Swatch selected-state **rõ tương phản** `[VERIFY]`.
→ PASS 13/13 → T4.

---

## T3.5 — Collapse Library (ĐỘC LẬP, off critical path)
`bLibraryCollapsed:bool(F)`. `[VERIFY]` tên `ScrollBox trái` + tick Is Variable. `BTN_ToggleLibrary`
đứng trước `ScrollBox_LibraryTree` trong `HB_MainContent`:
```
OnClicked: SET bLibraryCollapsed=NOT · Branch: True→Collapsed+"›" ; False→Visible+"‹"
```
**Q9:** MIỄN (layout). **TEST (expected-result sửa #):** collapse → **phần phải trong Inventory
(cards/grid/swatches) có thêm chỗ; KHÔNG giãn viewport 3D, KHÔNG giãn Inspector** (Inventory vẫn 512px,
Inspector là top-level riêng) · bấm lại → folder cũ · độc lập Inspector · resize window khi collapsed ok.

---

# ═══════════════════════════════════════
# S7G7T4 — Service + undo   ⭐ GATE
# ═══════════════════════════════════════

## 4 handler param (dùng bool)
```
Handle_ScalarPreview: Branch(IsValid Target AND idx>=0) True → Cast→Mesh → SetSlotScalarParam(...) ← LIVE
Handle_ScalarCommit:  Branch(...) True → SetSlotScalarParam(...)●→ok → Branch(ok): True→CaptureMaterialSnapshot ; False→dead-end
Handle_ColorPreview/Commit: tương tự SetSlotVectorParam.
```
**`Handle_ResetParamsRequested` — thân thật, rev6 #4 (branch ok):**
```
Branch(IsValid Target AND idx>=0):
  True → Cast→Mesh → ClearSlotParams(Mesh, TargetFurnitureActor.MaterialSlots, SelectedSlotName, SelectedSlotIndex) ●→ ok
       → Branch(ok): True → CaptureMaterialSnapshot → RefreshParamPanel() ; False → dead-end
```
Seam #6: `OnSceneRestored` → APPEND `RefreshParamPanel()`.

**Q8:** Commit/ResetParams: IsValid ✓ | L2 Branch(ok) True→snapshot False dead-end cố ý ✓ | No latent | 6A Undo qua ParamsJson ✓.

**Q9 S-SCAN:** S0 N/A · S1 chính · S2-S4/S7/S8 ⚠ chỉ Primary · S5/S6→S1 · S9 ⚠ đọc tươi.
**Q9 X-CHECK:** X1 snapshot chỉ khi ok=true; bIsRestoring sẵn · X2 Kho1(ok)+Kho2(EMS); Kho4 BÁO-không-sửa · X9 MID-on-demand+PathFallback.

**TEST T4 (GATE):**
1. Kéo màu LIVE·nhả→Undo/Redo đúng. 2. Roughness slot chưa MID→MID-on-demand, PathFallback.
3. Ép tên param SAI→mesh không đổi, `SnapshotHistory.Length` KHÔNG tăng (nhánh ok=false).
4. Apply MI khác (mở)→refresh, ParamsJson clear. 5. Save→load→param còn.
6. 1 lần giữ kéo qua lại→1 entry; nhả 2 lần→2 entry (baseline).
7. Reset Params ok → param về seed, 1 snapshot, rebuild, Undo đúng. **Reset Params khi service fail (giả
   lập)→KHÔNG snapshot** (`Length` không tăng — kiểm #4).
> GATE DỪNG: live-preview/undo lệch → DỪNG. → PASS → T4b.

---

# ═══════════════════════════════════════
# S7G7T4b — Coalescing undo   ⚠ ĐỤNG LÕI UNDO
# ═══════════════════════════════════════

**RULE G7:** history theo ý định, không theo event chuột (`DEVIATIONS.md`, Đ cũ `[HISTORICAL-OVERRIDE]`).

## BP_UndoManager
```
[Biến] ParamSession_Active:bool(F,no SaveGame) · ParamSession_Key:String

[Function MỚI] EndParamSession():                    ← nơi DUY NHẤT đóng phiên, mọi chỗ khác GỌI hàm này
  SET ParamSession_Active = False
  SET ParamSession_Key    = ""                       ← clear cả 2, không chỉ Active (dọn sạch, tránh đọc nhầm key cũ)

[End Play]         Call EndParamSession()
[CaptureSnapshot]  +1 dòng sau guard bIsRestoring: Call EndParamSession()
[RestoreSnapshot]  +1 dòng cạnh SET bIsRestoring=True: Call EndParamSession()
[Inventory]        OnMeshSelected/seam #3,#7: Call UndoManagerRef.EndParamSession()   ← #6

[Custom Event MỚI] CaptureParamSnapshot(ActionName:String, ParamKey:String)
▶→ Branch(bIsRestoring): True→Return                                      ← #9a guard đầu
     False → Branch(AND(ParamSession_Active, ParamKey==ParamSession_Key)):
              True → Is Valid Index(SnapshotHistory, Last Index):
                       True → Remove Index(Last Index) → SET CurrentIndex=CurrentIndex-1 (output pin,L4) → DoPush
                       False → DoPush
              False → DoPush
   DoPush(ActionName,ParamKey): Call CaptureSnapshot(ActionName) → SET Active=True → SET Key=ParamKey
```

## Inventory — 2 Commit (Branch ok, thay snapshot node)
```
Handle_ScalarCommit/ColorCommit:  ...SetSlotXParam(...)●→ok...
  Branch(ok): True → ParamKey = TargetFurnitureActor.UniqueID+"|"+SelectedSlotName+"|"+ParamName
                   → Label = "Đổi màu"/"Chỉnh nhám"+actor
                   → CaptureParamSnapshot(Label, ParamKey)
              False → dead-end
```

**Q8:** Custom Event | Is Valid Index trước Remove ✓ | L2 guard bIsRestoring đầu + 3 đường DoPush ✓ | No latent | 6A replace giữ 1 entry ✓.

**TEST T4b:** 1.rê nhiều lần→+1 · 2.Undo→trước,Redo→cuối · 3.màu→move→màu→**3 entry** · 4.màu→Roughness→2 ·
5.A→B→2,undo B không đụng A · 6.màu→Undo→màu→2 · 7.(sau T5)multi rê→1,undo cụm · 8.MaxSteps không rớt oan ·
9.Undo giữa phiên(bIsRestoring)→CaptureParamSnapshot Return sạch · **10.(#6) multi A+B chỉnh param→đổi
secondary thành A+C giữ Primary A→chỉnh cùng param→PHẢI 2 session/entry** (nếu fail: EndParamSession chưa
bắt được secondary-change → hook InputManager).
> GATE DỪNG: replace đè nhầm/cờ kẹt → DỪNG. → PASS → T5.

---

# ═══════════════════════════════════════
# S7G7T5 — Multi-select áp cả cụm (Q9 FULL) — rev6 #5 resolve-by-name per-actor
# ═══════════════════════════════════════

**Mục tiêu:** áp param cho mọi actor chọn **có slot cùng `SlotName` VÀ material CÓ control khớp
`ParamName`+`ControlType`**. Preview chỉ Primary.

## Node flow (#5: resolve TÊN→index per-actor TRƯỚC GetMaterial; match ParamName+ControlType)
```
Handle_ScalarCommit(ParamName, Value):        ← ControlType ngầm = Scalar
▶→ SET Cnt=0 · SET Total=SelectedActors.Length
▶→ ForEach SelectedActors (Actor):
     Cast → BP_FurnitureActor (bSuccess):
       True: GET FurnitureMesh ●→ ActorMesh
             ●→ ActorMesh.GetMaterialSlotNames → Find(SelectedSlotName) ●→ ActorSlotIndex   ← #5 resolve TÊN per-actor
             ▶→ Branch(ActorSlotIndex != -1):
                  False → (skip — actor không có slot tên này)
                  True  → GetMaterial(ActorSlotIndex) ●→ ActorMI                              ← đọc ĐÚNG slot
                        → GetControlsForMaterial(ActorMI, DT_ParamMap) ●→ ActorControls
                        → Branch( ActorControls có row: ParamName==this AND ControlType==Scalar )  ← #5b match cả loại
                             True  → SetSlotScalarParam(ActorMesh, Actor.MaterialSlots, SelectedSlotName, ActorSlotIndex, ParamName, Value) ●→ ok
                                   → Branch(ok): True→INCREMENT Cnt ; False→(trống)
                             False → (trống — material actor không có control Scalar tên này)
       False: (trống)
   Completed ▶→ Branch(Cnt > 0):
                True  → CaptureParamSnapshot(Label, ParamKey_Primary) → ShowToastMsg("Áp cho "+Cnt+"/"+Total+" đồ")
                False → ShowToastMsg("Không có đồ nào áp được thông số này")   ← không tạo history
```
`Handle_ColorCommit`: y hệt với `SetSlotVectorParam` + match `ControlType==Color`. Preview giữ Primary-only.

**Q8:** Custom Event | Cast bSuccess ✓ | L2 Branch(idx!=-1)/Branch(match)/Branch(ok) False trống hợp lệ,
snapshot ở Completed qua Branch(Cnt>0) KHÔNG Loop Body ✓ | No latent (L11 KHÔNG áp) | 6A 1 entry cả cụm ✓.

**Q9 S-SCAN FULL:** S0 N/A · S1→Primary · **S2 ⚠ CHÍNH** áp theo tên+control · S3/S4 ⚠→S2 (combo trộn master
→ chỉ actor có control khớp ăn) · S5/S6→S1/S5 · S7/S8 ⚠→S2 · S9 ⚠ đọc tươi SelectedActors.
**Q9 X-CHECK:** X1 CaptureParamSnapshot chỉ khi Cnt>0, khóa Primary→1 entry · X2 Kho2 riêng từng actor,
không aliasing · X7 Toast luôn hiện · X9 mỗi actor qua 3 guard: slot-tên + control-khớp + service-ok.

**TEST T5:**
1. 3 ghế cùng master → chỉnh màu → cả 3 + "3/3".
2. **[REGRESSION CỐ ĐỊNH — giữ lâu dài, không phải test 1 lần]** Layout slot ĐẢO: Actor A
   `[0]Seat [1]Legs`, Actor B `[0]Legs [1]Seat` (2 mesh khác thứ tự slot). Multi-select A+B, Primary=A,
   chỉnh param trên **Seat** → Actor B phải áp đúng **Seat** của nó (index 1), KHÔNG áp nhầm sang
   **Legs** (index 0) chỉ vì trùng số index với Primary. Đây là test bắt trực tiếp bug #5 (đọc MI
   actor phụ bằng index Primary) — đưa vào bộ regression test T5, chạy lại mỗi khi sửa code multi-apply.
3. Trộn ghế master khác NHƯNG có control cùng tên+loại → **vẫn đổi** (theo control).
4. Trộn ghế material không có control này (hoặc có tên nhưng khác loại: Scalar vs Color) → skip, "X/Y".
5. Tất cả skip → "Không có đồ nào...", `Length` KHÔNG tăng.
6. Undo → hoàn tác cụm đã đổi (không đụng skip).
7. Preview cụm → chỉ Primary; nhả → cả cụm.
8. Actor destroy giữa chừng → đọc tươi, Cast guard, không crash.
→ PASS → **G7 (T0-T5) đóng phần logic** (G8 điền từ điển thật).

---

## DOC SẼ ĐỤNG KHI AS-BUILT
- **T3.1:** `WBP_MaterialParamPanel.md` (`ShowEmptyState`+`ClearRows`/`AddRow`).
- **T3.2-3.4:** `WBP_MaterialInspector.md` (mới) · `WBP_FurnitureInventory.md` (Construct/Destruct,
  `IsInspectorVisible`/`Update`/`Open`/`Close`, `Handle_*`, biến `MaterialInspectorRef`/`DT_ParamMap`/
  `bInspectorOpen`/`bInspectorSuppressed`, seam #1-7, `SetResetEnabled`) · `DEVIATIONS.md` (Hướng 2;
  bỏ `WBP_MaterialSlotTab`; tab Material = context gate; RULE cụm Material Controller).
- **T3.5:** `WBP_FurnitureInventory.md` (`BTN_ToggleLibrary`, `bLibraryCollapsed`).
- **T4:** `WBP_FurnitureInventory.md` (4 handler + `Handle_ResetParamsRequested` branch ok + seam #6).
- **T4b:** `BP_UndoManager.md` (`ParamSession_*`, `EndParamSession`, `CaptureParamSnapshot`) ·
  `WBP_FurnitureInventory.md` (2 Commit + `EndParamSession` call) · `DEVIATIONS.md` (RULE G7).
- **T5:** `WBP_FurnitureInventory.md` (Commit cụm resolve-by-name + match ParamName+ControlType) ·
  `DEVIATIONS.md` (Preview Primary-only; theo control không theo master).
- Mỗi task: `01_Session_State.md` · `PROGRESS.md`. Version+ngày+giờ+phút.

## MỞ / CHỜ QUYẾT
- `[VERIFY T3.3]` node `Get Scalar/Vector Parameter Value`; breadcrumb display-name suffix.
- `[VERIFY T3.4 #11]` deselect-khi-click-nền hiện tại. `[VERIFY #13]` tương phản swatch.
- `[VERIFY T4b #10 / seam #6]` đổi secondary-selection giữ Primary có fire `OnMeshSelected`/`OnSelectionChanged`
  không — quyết chỗ hook `EndParamSession`.
- `[VERIFY T3.2]` Z-Order 2 top-level. `[VERIFY T3.5]` tên `ScrollBox trái`.
- `[BÁO-không-sửa]` X2/T4: combo save đọc `ParamsJson` chưa (Đ3).
- `[POLISH backlog]` tách material-context khỏi InventoryMode (Inspector đổi context mọi mode) ·
  glow-hint swatch · animation · đưa swatch vào Details khi Docking.
