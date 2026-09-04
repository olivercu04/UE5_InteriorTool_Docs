# S7.G2 — EXECUTION PLAN: Reroute đường live vào MaterialSlotService

> **⚙ FILE THỰC THI (working plan) — KHÔNG phải canonical.**
> Opus lập (27/08/2026). cuhoang + Sonnet thực thi qua nhiều phiên trên chính file này.
> Sonnet điền kết quả [VERIFY] + as-built test vào các khối chừa sẵn.
> **Claude Code đã chèn khối Việc 2B** (03/09, từ `DELTA_Opus_S7_Resequence`) **và thay mục Việc 3 sang Hướng B inline** (04/09, từ `DELTA_S7G2_Viec3_MultiApply_HuongB_04sep2026.md`). Phần as-built [VERIFY]/test vẫn do Sonnet+cuhoang điền trong phiên. Merge tổng vào canonical vẫn chờ G2 ĐÓNG.
> Nguồn plan: `Plans/Sprint7_MaterialEdit_Plan_v1.1.md` mục S7.G2 (v1.5).
> Node thật đã verify (session 27/08): `RefreshSlotSwatches` · `RefreshDisplay` · `LoadAndApplyMaterial` ·
> `OnSlotSwatchClicked` · `SelectedActors` source · `ShowToastMsg` · `CopySlotMaterial` · `PasteSlotMaterial` ·
> `BTN_ResetSlot` · `BTN_ResetAll` — **8/8 [VERIFY] đã xong, không còn câu treo.** Sẵn sàng vào Bước 0.

---

## 0. TRẠNG THÁI THỰC THI — cập nhật mỗi phiên (mở phiên mới đọc khối này TRƯỚC)

**Đang ở:** Bước 0 + Việc 1 + Việc 2 + Việc 2B (⭐ GATE undo/redo) ĐÃ PASS — sẵn sàng vào Việc 3. Resequence 03/09/2026 per `DELTA_Opus_S7_Resequence`.

| Mốc | Trạng thái | Ghi chú ngắn |
|---|---|---|
| Gom 8 [VERIFY] | ✅ | điền kết quả ở mục 3 — không còn câu treo |
| Bước 0 — 3 biến nền | ✅ | 3 biến thêm xong, build xanh |
| Việc 1 — swatch tên + selection | ✅ | PASS full — swatch tên, click-select, reset (xem deviation #9) |
| Việc 2 — reroute apply (⭐ slice) | ✅ | Test 1-4 PASS (đường GHI đúng). Test 5 (Undo) tách sang Việc 2B — không phải lỗi Việc 2 |
| Việc 2B — đường khôi phục snapshot | ✅ | PASS full 6 bước + bonus redo-stack case (04/09) |
| Việc 3 — multi-apply E1 | ☐ | Hướng B inline (chỉ multi khi cùng RowName; trộn loại → chỉ Primary + Toast). Spec DELTA 04/09, chưa code |
| Việc 4 — copy/paste | ☐ | KP1 ĐÃ CHỐT bản C (xem dưới) — không còn A/B |
| Việc 5 — reset slot/all | ☐ | Node thật khớp gần đúng dự đoán, 2 điều chỉnh nhỏ đã ghi |
| Test tổng G2 | ☐ | |

Ký hiệu: ☐ chưa · 🔄 đang làm · ✅ PASS · ⛔ chặn (ghi lý do)

**Quyết định đã chốt:**
- **KP1 (Việc 4) — CHỐT bản C, không còn A/B:** `PasteSlotMaterial` production đã có sẵn cách suy RowName từ path (`ClipboardMaterialPath.ParseIntoArray(".") → LastIndex → Conv_StringToName`), đang chạy đúng (thumbnail + AddRecentMaterial dùng cách này). G2 dùng lại NGUYÊN chuỗi có sẵn, tính 1 lần vào biến tạm `PasteRowName`, dùng chung cho Apply/GetDataTableRow/AddRecentMaterial (dọn trùng lặp tính 2 lần trong code cũ — KP3, rác do chính chỗ đang sửa). Không cần tra `FindMaterialRowNameByPath`.
- **Option B (Việc 1, RefreshSlotSwatches) — CHỐT:** không thêm class var cache tên slot. Gọi `GetMaterialSlotNames` trực tiếp 2 lần (1 lần lấy `.Length`, 1 lần `.Get(Index)` trong LoopBody) thay vì SET vào 1 biến rồi dùng lại. Lý do: N nhỏ (≤10 slot/mesh theo G0), phí gọi thêm không đáng kể; giữ đúng 3 biến Bước 0 đã chốt, không phình field ngoài kế hoạch (KP2).
- **[SỬA LỖI DOC] `RefreshSlotSwatches` là Custom Event, không phải Function** như Q8 gốc ghi nhầm — sửa ở Q8 Việc 1 bên dưới. Vì là Custom Event nên áp L9 (không Local Variable) — đây chính là lý do chọn Option B thay vì cache bằng local var.
- **[DEVIATION #9 — VERIFY #3 SAI]** Plan gốc ghi "1 chỗ reset SelectedSlotIndex duy nhất là `OpenMaterialModeForActor`" — SAI, đó là mô tả từ doc Sprint 2 cũ. `OnMeshSelected` bản v2.4 (Dispatcher Refactor, canonical hiện hành) làm reset INLINE, không gọi `OpenMaterialModeForActor` — có ở CẢ 2 nhánh (T và F). Đã sửa `SET SelectedSlotName=""` ở đúng 2 chỗ này, test PASS. Cờ treo: `OpenMaterialModeForActor` có thể vẫn còn sống ở `ApplyRestoredActor`/`CB_ChangeMaterial` (Sprint 2 doc) — CHƯA verify, không chặn G2, kiểm khi 2 call site đó bị đụng.

---

## 1. NGUYÊN TẮC ĐỌC FILE NÀY

Mỗi việc chia **2 khối tách bạch** (điểm dễ làm rối):
- **[THÊM MỚI]** = biến/node chưa tồn tại → tạo mới.
- **[SỬA]** = node đã có → chèn/thay ĐÚNG chỗ ghi, KHÔNG động phần còn lại.

⛔ **[VERIFY]** = soi K2Node / Details panel THẬT trước, lệch mô tả → DỪNG, báo cuhoang. Không code đè giả định.

Notation: `▶→` exec wire · `●→` data wire · `NodeA.Pin ●→ NodeB.Pin`.

Luật thực thi (kế thừa Custom Instructions + plan mục 0):
- Tuần tự, mỗi việc PASS test riêng mới sang việc sau.
- C++ không đụng ở gate này (service đã xong G1) — toàn bộ là Blueprint.
- Node mới ngoài bảng xác nhận → hỏi cuhoang trước.
- 3-strike cùng chỗ → STOP, báo.

---

## 2. BỨC TRANH: G2 ĐỔI KHO GHI

```
TRƯỚC G2 (v1.1):
  apply → CreateDMI + SetMaterial + SetArrayElem(MaterialOverrides[idx] = path)
  kho ghi = MaterialOverrides : Array<String>   (index-based)

SAU G2:
  apply → ApplyLoadedMaterialToSlot(...)         [1 hàm C++ lo hết]
  kho ghi = MaterialSlots : Array<FMaterialSlotRecord>   (name-based, Records)
  MaterialOverrides KHÔNG còn được ghi bởi apply
   → mọi chỗ ĐỌC MaterialOverrides phải chuyển nguồn (Copy: Việc 4 · Reset: Việc 5)
```

**14 hàm service (G1 as-built) dùng ở gate này:**
| Hàm | Chữ ký rút gọn | Dùng ở |
|---|---|---|
| `ApplyLoadedMaterialToSlot` | `(Mesh, Records&, SlotName, HintIndex, LoadedMI, RowName, PathFallback) → bool` | Việc 2,3,4 |
| `ResetSlotToAssetDefault` | `(Mesh, Records&, SlotName, HintIndex) → bool` — đọc asset gốc, **XÓA record** | Việc 5 |
| `ResetAllSlotsToAssetDefault` | `(Mesh) → bool` — reset mesh, **KHÔNG đụng Records** | Việc 5 |
| `SerializeSlotRecords` | `(Records) → String` — để Print JSON debug | test mọi việc |

`Records` truyền **UPARAM(ref)** → C++ sửa tại chỗ trên biến thật của actor.

**FMaterialSlotRecord** (5 field, SaveGame): `SlotName` · `SlotIndex` · `MaterialRowName` · `MaterialPathFallback` · `ParamsJson`.

---

## 3. KHỐI GHI KẾT QUẢ [VERIFY] — ĐÃ ĐIỀN ĐỦ 8/8 (session 27/08)

| # | Cần verify | Kết quả |
|---|---|---|
| 1 | `BP_FurnitureActor` có biến `MaterialSlots` chưa? | **CHƯA có.** Bước 0 thêm mới `Array<FMaterialSlotRecord>`, SaveGame ✓. |
| 2 | `OnSlotSwatchClicked` SET gì + guard | Chỉ `SET SelectedSlotIndex = ClickedSlotIndex` rồi `ForEachLoop(HB_SwatchList.GetAllChildren())` → `SetSelected(bSelected = Array Index == SelectedSlotIndex)` để tô sáng. **Không có `IsValid` guard nào** (an toàn vì chỉ đụng `HB_SwatchList`, không đụng `TargetFurnitureActor`). Tô sáng dựa `Array Index` của loop, không dựa `SlotIndex` lưu trên swatch — giả định ngầm thứ tự children khớp lúc dựng, không đổi ở G2. |
| 3 | Chỗ reset selection | Đúng 1 chỗ duy nhất: `OpenMaterialModeForActor` SET `SelectedSlotIndex = -1` (gọi từ `OnMeshSelected` khi chọn actor mới). Xác nhận qua Find-in-Blueprint toàn graph, không sót chỗ khác. |
| 4 | Nguồn `SelectedActors` | `GetAllActorsOfClass(BP_FurnitureInputManager) → Get(0)` **gọi tươi mỗi lần dùng**, KHÔNG có `InputManagerRef` cached trên inventory — pattern quán xuyến toàn widget (xác nhận qua đoạn Replace routing trong `OnMeshSelected`, cùng cơ chế lấy `SelectedActors`). |
| 5 | Toast | Đã có sẵn Function `ShowToastMsg(Message : Text)` trong `WBP_FurnitureInventory`: `GetAllActorsOfClass(BP_FurnitureSceneManager)[0].ToastRef` → `IsValid?` → `True: ShowToast(Message, Duration=5.0)` / `False: PrintString(Message)` (Dev Only fallback có sẵn). **`ToastRef` nằm trên `BP_FurnitureSceneManager`, không phải GameInstance.** Gọi thẳng `ShowToastMsg(...)`, không cần tự dựng IsValid/GetAllActorsOfClass. |
| 6 | Tên clipboard + Copy/Paste K2Node | Biến thật: **`ClipboardMaterialPath`** (khớp 1 trong 2 giả thuyết ban đầu). `CopySlotMaterial` **đã có bounds check** `idx < GetNumMaterials(FurnitureMesh)` (plan cũ bỏ sót) VÀ đã tự rẽ nhánh theo `IsEmpty(MaterialOverrides[idx])`: rỗng → đọc material sống (`GetPathName`); không rỗng → đọc thẳng `MaterialOverrides[idx]` (né đọc MID). Đây là bằng chứng cứng cho bug GetObjectName/MID đã nêu ở phiên trước — code production đã tự vá bằng cách rẽ nhánh này. `PasteSlotMaterial` **đã có sẵn** `ClipboardMaterialPath.ParseIntoArray(".") → Array_LastIndex → Get → Conv_StringToName` để suy RowName từ path, dùng ngay cho `GetDataTableRow` (thumbnail) và lặp lại y hệt lần 2 cho `AddRecentMaterial` (chỗ trùng lặp — dọn khi sửa). |
| 7 | `FindMaterialRowNameByPath` | **Không cần tra nữa** — Phát hiện #6 (ParseIntoArray có sẵn) đã cung cấp cách suy RowName production-tested, thay thế hoàn toàn nhu cầu gọi hàm này. KP1 chốt bản C (xem mục 0). |
| 8 | K2Node Reset | `BTN_ResetSlot`: đọc **`StaticMesh.GetMaterial(idx)`** (hàm trên UStaticMesh ASSET, không phải PrimitiveComponent) → `SetMaterial` → `Array_Set(MaterialOverrides[idx]="")` (xóa override) → `CaptureSnapshot("ResetSlot")` → update 1 swatch qua `GetObjectName→Conv_StringToName→GetDataTableRow→UpdateThumbnail`. **Không gọi `RefreshSlotSwatches()`.** `BTN_ResetAll`: ForLoop `StaticMesh.GetMaterial(i)→SetMaterial` mọi slot → `Array_Clear(MaterialOverrides)` → `CaptureSnapshot("ResetAll")` → **ĐÃ CÓ SẴN `RefreshSlotSwatches()`** (không phải thêm mới như dự thảo cũ). Cách đọc `StaticMesh.GetMaterial()` (asset gốc) khớp đúng triết lý `ResetSlotToAssetDefault`/`ResetAllSlotsToAssetDefault` (Đ7/Đ10) — không phải suy đoán, code cũ và service C++ mới cùng 1 nguyên lý đọc. |

---

## BƯỚC 0 — NỀN DỮ LIỆU (thuần THÊM MỚI, KHÔNG logic)

Làm trước mọi việc. Không node flow, chỉ khai báo biến.

✅ **[VERIFY #1] đã xong** — `BP_FurnitureActor` CHƯA có biến `MaterialSlots`. → THÊM MỚI `MaterialSlots : Array<FMaterialSlotRecord>`, **SaveGame ✓**.

**[THÊM MỚI] cả 3 biến:**

| Nơi | Biến | Kiểu | Ghi chú |
|---|---|---|---|
| `BP_FurnitureActor` | `MaterialSlots` | Array<FMaterialSlotRecord> | **SaveGame ✓** — xem [VERIFY #1] |
| `WBP_FurnitureInventory` | `SelectedSlotName` | String | song hành `SelectedSlotIndex` sẵn có |
| `WBP_SlotSwatch` | `SlotName` | String | Instance Editable = false |

**Vì sao `MaterialSlots` phải là biến TRÊN actor (không local):** `ApplyLoadedMaterialToSlot` nhận `UPARAM(ref) TArray<FMaterialSlotRecord>& Records` → C++ sửa tại chỗ trên biến thật. Truyền local → sửa xong mất → save/undo/restore (G3) đọc rỗng. Đây là xương sống cả Sprint 7.

**TEST Bước 0:** compile actor + inventory + swatch → build xanh. Chưa chạy gì.

**As-built Bước 0** _(điền):_
```
#1 kết quả: _____
Đã thêm biến nào: _____
Build: _____
```

---

## VIỆC 1 — Swatch biết tên slot + selection theo tên

**Mục tiêu:** mỗi swatch cầm `SlotName`; click swatch → inventory nhớ cả tên lẫn index.

### K2Node hiện tại (đã verify — Sonnet đối chiếu)
```
RefreshSlotSwatches:
  ClearChildren(HB_SwatchList)
  ForLoop(0 → GetMaterialSlotNames(TargetFurnitureActor.FurnitureMesh).Length - 1)   ← chỉ lấy .Length, BỎ mảng tên
    LoopBody:
      Create WBP_SlotSwatch → SET SlotIndex = Index → SET MeshComp = (soft)FurnitureMesh
      → RefreshDisplay() → AddChild(HB_SwatchList) → Bind OnSwatchClicked → OnSlotSwatchClicked
```

### [SỬA] `RefreshSlotSwatches` — chèn 2 chỗ, GIỮ phần còn lại
```
Ngay sau GetMaterialSlotNames:
  KHÔNG chỉ lấy .Length → SET LocalSlotNames (local Array<Name>) = mảng tên đó
  (.Length lấy từ LocalSlotNames.Length để chạy ForLoop như cũ)

Trong LoopBody, chèn NGAY SAU "SET NewSwatch.SlotIndex = Index":
  ▶→ LocalSlotNames.Get(Index) ●→ (To String) ●→ SET NewSwatch.SlotName
```
KHÔNG đụng: `MeshComp`, `RefreshDisplay()`, `AddChild`, `Bind`, thumbnail.

### ✅ [VERIFY #2] `OnSlotSwatchClicked` — K2Node thật đã đọc
```
OnSlotSwatchClicked(ClickedSlotIndex):
  SET SelectedSlotIndex = ClickedSlotIndex
  ▶→ ForEachLoop(HB_SwatchList.GetAllChildren()):
       LoopBody: Cast(Array Element) → WBP_SlotSwatch
         then ▶→ SetSelected(bSelected = (Array Index == SelectedSlotIndex))   ← tô sáng
         CastFailed → dead-end
     Completed → dead-end
```
Không có `IsValid` guard nào (an toàn — chỉ đụng `HB_SwatchList`, không đụng `TargetFurnitureActor`). Tô sáng dựa `Array Index` của ForEachLoop, không dựa `SlotIndex` lưu trên swatch — giả định ngầm thứ tự children khớp lúc dựng (đúng, không đổi, không đụng ở G2).

### [THÊM] `OnSlotSwatchClicked` — thêm tra tên từ index, bọc guard MỚI riêng
```
SET SelectedSlotIndex = ClickedSlotIndex        ← giữ nguyên
▶→ [THÊM] Branch IsValid(TargetFurnitureActor):        ← guard MỚI, chỉ bọc phần mới thêm
      True ▶→ GET FurnitureMesh → GetMaterialSlotNames → Get(ClickedSlotIndex) → (To String)
             ●→ SET SelectedSlotName
      (merge, cả 2 nhánh) ▶→ ForEachLoop(HB_SwatchList...)  ← y nguyên như cũ, không đổi
```
IsValid chỉ bọc đoạn tra tên (mới) — KHÔNG bọc `ForEachLoop` cũ, giữ đúng nguyên tắc surgical, không đụng phần đang chạy tốt. Đọc lại `GetMaterialSlotNames` tại điểm click (không cache) — an toàn, mesh không đổi.

### ✅ [VERIFY #3] Reset selection — chốt
Đúng 1 chỗ: `OpenMaterialModeForActor` (gọi từ `OnMeshSelected`) SET `SelectedSlotIndex = -1`. Xác nhận qua Find-in-Blueprint toàn graph, không sót. → **[SỬA]** thêm `SET SelectedSlotName = ""` ngay cạnh dòng đó.

### Q8
```
RefreshSlotSwatches: Custom Event (SỬA — không phải Function như ghi nhầm) → KHÔNG Local Var (L9) — Option B: gọi GetMaterialSlotNames trực tiếp 2 lần | IsValid TargetFurnitureActor ở caller | L2: ForLoop không nhánh chết | No latent | 6A: N/A (đọc-hiển-thị)
OnSlotSwatchClicked: Event → không tạo local ✓ | IsValid TargetFurnitureActor bọc riêng đoạn tra tên (MỚI); ForEachLoop tô sáng giữ nguyên không guard | L2: chuỗi thẳng, merge trước ForEachLoop | No latent | 6A: N/A
OnMeshSelected (nhánh Material, reset đường click-select — SỬA thêm SET SelectedSlotName="" cả 2 nhánh T/F): Event → guard IsValid(SelectedActor) có sẵn | L2: 2 nhánh đều có đích | No latent | 6A: N/A
```

**TEST Việc 1:** chọn actor N slot → tab Material → click từng swatch → Print `SelectedSlotName`+`SelectedSlotIndex` (Dev Only) → đối chiếu tên slot thật Static Mesh Editor. Đúng tên + đúng index = PASS.

**As-built Việc 1** — ✅ PASS (điền 29/08→03/09/2026):
```
#2 kết quả: ForEachLoop tô sáng theo Array Index, không IsValid guard — xem chi tiết trên
#3 kết quả: SAI (xem DEVIATION #9 ở mục 0) — thực tế 2 chỗ, cả hai trong OnMeshSelected (nhánh T/F), KHÔNG phải OpenMaterialModeForActor
Test RefreshSlotSwatches: PASS 8/8 slot đúng tên+thứ tự (Bed_SplitHeadboard_Soft_17236) — Print String đối chiếu Static Mesh Editor
Test OnSlotSwatchClicked: PASS — Index/Name đúng theo swatch click
Test reset khi đổi actor: PASS cả 2 nhánh — Reset(T) và Reset(F) đều Index=-1 | Name="" khi chuyển actor khác
```

---

## VIỆC 2 — Reroute `LoadAndApplyMaterial` (⭐ VERTICAL SLICE)

**Mục tiêu:** apply qua `ApplyLoadedMaterialToSlot`, ghi vào `MaterialSlots`, bỏ 3 node CreateDMI/SetMaterial/SetArrayElem.

⭐ **Rủi ro lớn nhất gate** — cơ chế `UPARAM(ref) Records` ghi vào biến actor chưa test qua UI bao giờ. PASS Việc 2 = xương sống đứng vững, 3/4/5 chỉ lặp pattern. **Việc 2 fail → STOP, không làm 3/4/5.**

### K2Node hiện tại (đã verify)
```
LoadAndApplyMaterial (Custom Event):
  MakeSoftObjectPath(PendingMaterialPath) → SoftRef → LoadAsset(async) → Completed
  → Cast MaterialInterface → IsValid(MI)?
    True → IsValid(TargetFurnitureActor)?
      True → ┌ CreateDynamicMaterialInstance(FurnitureMesh, idx=SelectedSlotIndex, src=MI, OptionalName="None")  ┐
             │ SetMaterial(FurnitureMesh, idx=SelectedSlotIndex, MID)                                            │ BỎ 3 node
             │ SetArrayElem(TargetFurnitureActor.MaterialOverrides, idx=SelectedSlotIndex, PendingMaterialPath)  ┘
             → GetDataTableRow(PendingRowName) Row Found → cast children[SelectedSlotIndex]→WBP_SlotSwatch→UpdateThumbnail(ThumbnailMI)
             → ClearTimer + SetTimer("CaptureMaterialSnapshot", 0.5s) → SET ApplyMaterialTimerHandle
             → GetAllActorsOfClass(BP_FurnitureUserPrefsManager)[0] → AddRecentMaterial(PendingRowName)
```
(Ghi chú: `OptionalName="None"` không nối gì → MID mang tên tự động. Không liên quan G2, để nguyên khái niệm.)

### [SỬA] Thay đúng 3 node giữa — GIỮ đầu (async + 2 IsValid) và đuôi (thumbnail + timer + recent)
```
... IsValid(TargetFurnitureActor) True ▶→
  [BỎ: CreateDynamicMaterialInstance, SetMaterial, SetArrayElem]
  [THAY bằng 1 node]:
    ApplyLoadedMaterialToSlot(
       Mesh         = TargetFurnitureActor.FurnitureMesh,
       Records      = TargetFurnitureActor.MaterialSlots,    ← pin ref, cắm THẲNG biến actor
       SlotName     = SelectedSlotName,
       HintIndex    = SelectedSlotIndex,
       LoadedMI     = MI (AsMaterialInterface),
       RowName      = PendingRowName,
       PathFallback = "" )
  ▶→ [Việc 3 chèn vào đây — multi-apply]
  ▶→ GetDataTableRow(PendingRowName) ... UpdateThumbnail ...   ← GIỮ NGUYÊN toàn bộ đuôi
```

**Vì sao GIỮ UpdateThumbnail:** set thumbnail đúng NGAY lúc apply, dùng `PendingRowName` trực tiếp (nguồn tin cậy, không qua GetObjectName). Không thuộc scope reroute-ghi. Đừng đụng.

**⚠ Bug thumbnail-khi-reselect (KHÔNG thuộc G2 — đọc để khỏi hiểu nhầm test):**
`RefreshDisplay()` no-param dùng `GetObjectName` tra ngược → SAI với slot đã áp MID (MID tên `MaterialInstanceDynamic_N`). Reselect actor đã đổi material → swatch thumbnail không hiện đúng. **Bug này ĐÃ có từ trước Sprint 7, G2 không làm tệ hơn cũng không sửa.** `GetPanelSlots` (G1, trả `RowNameResolved`) để dành vá ở **G5** lúc redesign panel. → Test G2 chỉ kiểm thumbnail lúc APPLY, KHÔNG kiểm reselect.

### Q8
```
Custom Event (Latent async hợp lệ, không Function) | IsValid MI + IsValid TargetFurnitureActor (guard sẵn có, giữ) | L2: False của 2 IsValid dead-end hợp lệ (không logic sau cần chạy), True chuỗi thẳng tới timer | No latent thêm | 6A: Reset (Việc 5) lo đường ngược; undo qua CaptureSnapshot có sẵn
```

**TEST Việc 2 (kỹ):**
1. Chọn 1 actor → click 1 slot → đổi 1 material → mesh đổi đúng vật liệu.
2. **Print JSON `MaterialSlots`** (SerializeSlotRecords → Print, Dev Only) → đúng 1 record: SlotName khớp, MaterialRowName khớp, ParamsJson rỗng.
3. Apply material KHÁC cùng slot → vẫn 1 record (không nhân đôi), RowName cập nhật.
4. Apply slot KHÁC → 2 record, đúng 2 slot.
5. Undo → material về trước đó.

**PASS bước 2-3 = cơ chế UPARAM(ref) ghi đúng biến actor → gate đứng vững.**

**As-built Việc 2** _(điền 03/09/2026):_
```
Print JSON sau apply đơn: PASS — 1 record đúng SlotName/RowName, ParamsJson rỗng
Apply lại cùng slot (dedupe): PASS — vẫn 1 record, RowName cập nhật
Apply slot khác: PASS — 2 record đúng 2 slot
Undo: TÁCH sang Việc 2B (đường khôi phục chưa có ở Việc 2 — đúng thiết kế resequence)
```

---

## VIỆC 2B — Đường khôi phục snapshot cho MaterialSlots (MỚI — chèn từ DELTA_Opus_S7_Resequence 03/09/2026)

**Mục tiêu:** undo/redo material chạy đúng qua đường records mới. Bản SẠCH — chưa nhánh legacy (legacy để G3, vì nó chỉ cần khi load save CŨ; snapshot trong phiên luôn format mới).

**Gate:** Việc 2B PASS mới được sang Việc 3. 2B fail → vẫn STOP như Việc 2.

> **Tên struct snapshot (cuhoang xác nhận 03/09):** **`S_FurniturePlacement`** (trong `BP_UndoManager`, đã có sẵn `MaterialPaths`, `RowName`...). Tên `S_ActorSnapshotData` trong plan G3 cũ là sai — đã sửa. Việc 2B thao tác trên `S_FurniturePlacement`, không tạo struct mới.

### 2B.0 — [THÊM MỚI] field + class vars (thuần khai báo)

| Nơi | Thêm | Kiểu | Ghi chú |
|---|---|---|---|
| `S_FurniturePlacement` (struct trong BP_UndoManager) | `MaterialSlots` | `Array<FMaterialSlotRecord>` | song hành `MaterialPaths` cũ; bump Version struct nếu file đang đánh version |
| `BP_FurnitureActor` | `Rst_SlotIdx` | `int` | **KHÔNG** SaveGame |
| `BP_FurnitureActor` | `Rst_CurRecord` | `FMaterialSlotRecord` | **KHÔNG** SaveGame |

`MaterialSlots` (biến chính trên actor, SaveGame) đã thêm ở Bước 0 — không làm lại.

### 2B.1 — [THÊM MỚI] `RestoreMyMaterialSlots` (Custom Event trên BP_FurnitureActor)

Bản sạch, chưa legacy. Async tuần tự — vì trên **actor instance riêng** nên KHÔNG aliasing (L11 tôn trọng sẵn theo thiết kế).

```
RestoreMyMaterialSlots (Custom Event) ▶→
  ResetAllSlotsToAssetDefault(FurnitureMesh)      ← Đ10, bước 0: mesh về gốc trước khi áp lại
  ▶→ SET Rst_SlotIdx = 0
  ▶→ Rst_LoadNextSlot

Rst_LoadNextSlot (Custom Event) ▶→
  Branch(Rst_SlotIdx >= MaterialSlots.Length)
    True  → [xong]
    False ▶→ MaterialSlots.Get(Rst_SlotIdx) ●→ SET Rst_CurRecord      ← temp var, không đọc pure 2 lần
      ▶→ Branch(Rst_CurRecord.MaterialRowName != "")
           True  → GetDataTableRow(DT_Material, Rst_CurRecord.MaterialRowName) → path
           False → Rst_CurRecord.MaterialPathFallback → path
      ▶→ MakeSoftObjectPath(path) → Async Load Asset → Completed
        ▶→ Branch(IsValid loaded asset)
             True → Cast MaterialInterface →
                    ApplyLoadedMaterialToSlot(FurnitureMesh, MaterialSlots,
                       Rst_CurRecord.SlotName, Rst_CurRecord.SlotIndex,
                       MI, Rst_CurRecord.MaterialRowName, Rst_CurRecord.MaterialPathFallback)
                    ▶→ ApplyParamsJsonToSlot(FurnitureMesh, Rst_CurRecord.ParamsJson,
                       Rst_CurRecord.SlotName, Rst_CurRecord.SlotIndex)
        (merge cả 2 nhánh IsValid) ▶→ SET Rst_SlotIdx = Rst_SlotIdx + 1 ▶→ Rst_LoadNextSlot
```

**Q8:**
```
RestoreMyMaterialSlots / Rst_LoadNextSlot: Custom Event (latent async hợp lệ) | IsValid loaded asset guard (load fail KHÔNG kẹt chain — vẫn idx++) | L2: mọi nhánh (kể cả load fail, kể cả IsValid=False) đều tới idx++ → Rst_LoadNextSlot, không dead-end fatal | Latent trong Custom Event ✓ (KHÔNG Function) | 6A: đây CHÍNH LÀ đường ngược — reset-trước-áp (Đ10) đảm bảo gọi lại nhiều lần không cộng dồn
```

> Ghi chú L11/aliasing: event nằm trên BP_FurnitureActor (mỗi actor 1 graph instance riêng) → nhiều actor restore song song không đè `Rst_SlotIdx`/`Rst_CurRecord` của nhau. Đây là lý do G3 đã thiết kế restore On-Actor, không On-Manager.
> Ghi chú KP2: KHÔNG thêm `Rst_Generation` guard bây giờ. Chỉ thêm nếu test 2B lộ double-apply do gọi chồng (giữ đúng luật "không thêm trước khi fail").

### 2B.2 — [SỬA] `CaptureSnapshot` (BP_UndoManager) — chụp thêm MaterialSlots

Trong đoạn build `S_FurniturePlacement` mỗi actor (chỗ đang GET `RowName`, `MaterialPaths` — Step 3):
```
[THÊM] GET actor(cast BP_FurnitureActor).MaterialSlots ●→ SET placement.MaterialSlots
```
Song hành node GET RowName có sẵn (v1.15). KHÔNG đụng phần còn lại.

### 2B.3 — [SỬA] `RestoreSnapshot` (BP_UndoManager) — trả MaterialSlots + gọi restore

Trong Step 4 (sau khi Spawn actor + Set Static Mesh + SET RowName — actor đã có mesh):
```
[THÊM, sau SET NewActor.RowName]
  SET NewActor.MaterialSlots = placement.MaterialSlots      ← trả records vào actor TRƯỚC khi restore
  ▶→ Call NewActor.RestoreMyMaterialSlots                    ← áp lại lên mesh (async, tự chạy)
```
Thứ tự bắt buộc: SET mesh → SET MaterialSlots → Call RestoreMyMaterialSlots (event đọc cả FurnitureMesh lẫn MaterialSlots).

**Q8 (2B.2 + 2B.3):**
```
CaptureSnapshot: giữ Custom Event cũ | không guard mới cần (đọc actor đã IsValid trong loop cũ) | L2: chuỗi thẳng thêm 1 GET/SET | No latent thêm | 6A: cặp với RestoreSnapshot
RestoreSnapshot: giữ | SET trước Call (thứ tự) | L2: thẳng | Call event latent nằm trên actor (hợp lệ) | 6A: đây là đường ngược
```

### TEST Việc 2B (đây là test undo/redo THẬT — cái Việc 2 fail)
```
1. Apply slot2 (gray) → đợi 1-2s → apply slot3 (yellow) → đợi 1-2s
2. Undo 1 lần → CHỈ slot3 về gốc, slot2 GIỮ gray | Print JSON: đúng 1 record (slot2)
3. Undo lần nữa → slot2 về gốc | Print JSON: rỗng
4. Redo → slot2 về lại gray | Print JSON: 1 record
5. Redo → slot3 về lại yellow | Print JSON: 2 record
6. Đổi material rồi Undo→Redo xen kẽ vài lần → không lệch, không cộng dồn record
```
PASS 1-6 = đường ghi + đường ngược khớp nhau → **xương sống G2 đứng vững thật** → sang Việc 3.

**As-built Việc 2B** _(điền 04/09/2026):_
```
2B.0 field/class var đã thêm: ✅ (S_FurniturePlacement.MaterialSlots, Rst_SlotIdx, Rst_CurRecord)
Test 1-2 (undo tách slot): PASS — JSON record giảm đúng thứ tự apply ngược (4→3→2→1)
Test 3 (undo về rỗng): PASS
Test 4-5 (redo): PASS — bonus: apply nhánh MỚI sau Undo → Redo đúng nhánh mới, không lẫn state nhánh cũ đã cắt (xác nhận CaptureSnapshot resize redo-stack đúng)
Test 6 (xen kẽ, không cộng dồn): PASS
Ghi chú rủi ro (không chặn): Warning "ResetAllSlotsToAssetDefault Mesh không hợp lệ" mỗi lần restore — race LoadMeshAsync vs RestoreMyMaterialSlots, vô hại ở luồng hiện tại (actor luôn spawn mới, không tái dùng). Để G3 test #10 (stress restore chồng nhau) soi lại.
```

---

## VIỆC 3 — Multi-Apply Material (Hướng B, inline) — fix Bug-MaterialPrimaryOnly

`[SỬA 04/09 — Hướng A → Hướng B inline; xem DELTA_S7G2_Viec3_MultiApply_HuongB_04sep2026.md]`
**Trạng thái:** PLAN — chưa code, chưa test. As-built khung ở cuối, Sonnet điền sau.

**Mục tiêu:** vá `Bug-MaterialPrimaryOnly` theo hướng an toàn. Multi-apply CHỈ chạy khi tất cả actor đang chọn **cùng RowName** (cùng model y hệt — case "N gối giống hệt"). Chọn trộn loại → giữ single-Primary + Toast cảnh báo rõ "N món khác loại chưa đổi". Dùng lại `MI` đã load ở Việc 2, KHÔNG load lại N lần.

### 0. Bối cảnh quyết định (vì sao Hướng B, vì sao inline)

**Bug đang vá:** `Bug-MaterialPrimaryOnly` (02/08). Chọn cả cụm → đổi material → chỉ Primary đổi, N actor còn lại im lặng không đổi, KHÔNG cảnh báo. User tưởng cả cụm đã đổi.

**Hướng A (cũ, bỏ):** apply theo tên slot cho MỌI actor đang chọn, không phân biệt loại mesh.
- Rủi ro: combo dị chủng (sofa + bàn trà + ghế) tình cờ trùng tên slot → áp nhầm material vào món user không chủ ý đổi. Toast chỉ đếm số, không nêu tên → sai ÂM THẦM, nguy cho combo thương mại.

**Hướng B (chốt):** multi-apply chỉ khi tất cả actor **cùng RowName**. Chọn trộn loại → single-Primary + Toast cảnh báo.
- Fail-safe: sai an toàn (kém tiện) thay vì sai tiện lợi (áp nhầm). Vá đúng phần gây hại nhất của bug gốc (silent), không mở rủi ro áp nhầm liên loại.
- YAGNI: KHÔNG làm "multi-apply liên loại có xác nhận từng món" — chưa có bằng chứng cần, rủi ro cao.

**Inline thay C++ (chốt 04/09):** logic "cùng loại?" = 1 phép so `RowName` (FName) trong ForEach. Đủ nhỏ để làm thẳng trong widget bằng Blueprint, KHÔNG cần hàm C++ mới.
- KISS/YAGNI thắng SoC ở quy mô này: không thêm hàm C++, không compile lại `FurnitureToolkit`, không đụng file C++.
- Đánh đổi đã cân: logic so sánh nằm ở widget (hơi lệch "widget mỏng") — chấp nhận, vì phép so 1 field quá nhỏ để tách service.

### 1. Verify đã chốt (đọc K2Node/doc thật trong phiên Opus)

| # | Điều verify | Kết quả | Nguồn |
|---|---|---|---|
| V1 | `LoadAndApplyMaterial` đã reroute sang `MaterialSlotService.ApplyLoadedMaterialToSlot`, ghi `MaterialSlots` (KHÔNG phải `MaterialOverrides` cũ) | ✅ ĐÃ reroute (Việc 2) | K2Node `LoadAndApplyMaterial` |
| V2 | Điểm chèn multi-loop | Giữa `ApplyLoadedMaterialToSlot.then` và `SerializeSlotRecords` | K2Node (đuôi: Apply→Serialize→PrintDev→GetDataTableRow→UpdateThumbnail→ClearTimer→SetTimer→AddRecentMaterial) |
| V3 | `MI` (material đã load) tái dùng, KHÔNG load lại N lần | Lấy pin `AsMaterial Interface` của Cast (qua Knot_34/35 — cùng nguồn Primary dùng) | K2Node |
| V4 | `RowName` trên `BP_FurnitureActor` kiểu gì | **FName** (SaveGame) | `BP_FurnitureActor.md` Variables + `Data_Structures.md` |
| V5 | Nguồn `SelectedActors` | `GetAllActorsOfClass(BP_FurnitureInputManager)[0] → SelectedActors`, gọi tươi mỗi lần (KHÔNG cache InputManagerRef trên widget) | S7G2 plan VERIFY#4 + K2Node pattern |
| V6 | Đường gọi Toast | Function `ShowToastMsg(Message : Text)` có sẵn trên `WBP_FurnitureInventory` — tự lo `ToastRef` (trên `BP_FurnitureSceneManager`) + IsValid + fallback PrintString. Tham số **Text** → phải `Conv_StringToText` chuỗi nối | S7G2 plan VERIFY#5 |

**Hệ quả V1:** cả Primary lẫn actor phụ đều ghi cùng format `MaterialSlots` → KHÔNG có case 2 format lẫn nhau trong 1 lần apply. Multi-loop chèn thẳng sau Primary, không cần bước reroute single.

### 2. Biến mới (3 Class Variable trên `WBP_FurnitureInventory`, prefix `LoadApply_`)

| Tên | Kiểu | Default | Lý do |
|---|---|---|---|
| `LoadApply_Selected` | Array of Actor | — | copy `SelectedActors` (L: array pass-by-ref → SET vào class var trước khi loop) |
| `LoadApply_AllSame` | Boolean | **true** | cờ "tất cả cùng RowName"; vòng 1 chỉ SET false, không SET true |
| `LoadApply_SuccessCount` | Integer | 0 | đếm actor phụ áp OK (vòng 2) |

> ⚠ `LoadAndApplyMaterial` là **Custom Event** (K2Node xác nhận: `K2Node_CustomEvent CustomFunctionName="LoadAndApplyMaterial"`) → Event KHÔNG có Local Variable panel (L9). 3 biến trên **phải là Class Variable** với prefix `LoadApply_` (naming §9 — biến tạm phục vụ 1 event → prefix tên event). CLEAR `LoadApply_Selected` + reset `LoadApply_AllSame=true` + `LoadApply_SuccessCount=0` ở ĐẦU đoạn multi (trước vòng 1), vì là class var persistent.

> _[04/09 — bản delta đầu ghi nhầm "Local Variable" ở tiêu đề mục này; cuhoang sửa tại nguồn → chốt **Class Variable** (đúng L9). Đã khớp.]_

### 3. Node flow — chèn giữa `ApplyLoadedMaterialToSlot.then` và `SerializeSlotRecords`

Ký hiệu: `▶→` exec, `●→` data.

```
[ApplyLoadedMaterialToSlot.then — Primary vừa áp xong]
▶→ SET LoadApply_AllSame = true                       ← reset class var đầu đoạn
▶→ SET LoadApply_SuccessCount = 0
▶→ GetAllActorsOfClass(BP_FurnitureInputManager) → Get(0) → GET SelectedActors
   → SET LoadApply_Selected                            ← copy (L: pass-by-ref)
▶→ Branch(LoadApply_Selected.Length > 1)
     False ▶→──────────────────────────────────┐       ← single thật: bỏ qua multi, không Toast
     True  ▶→ ForEach(LoadApply_Selected → A):          ← ══ VÒNG 1: KIỂM CÙNG LOẠI ══
                Cast A → BP_FurnitureActor  [dùng bSuccess pin, KHÔNG rẽ exec CastFailed]
                  Branch(Cast bSuccess?)
                    False → SET LoadApply_AllSame = false    ← actor lạ → khác loại (fail-safe)
                    True  → Branch(CastedA.RowName != TargetFurnitureActor.RowName)
                              True  → SET LoadApply_AllSame = false
                              False → [dead-end hợp lệ — cùng RowName, không làm gì]
              Completed ▶→ Branch(LoadApply_AllSame)
                   True ▶→ ForEach(LoadApply_Selected → A2):   ← ══ VÒNG 2: APPLY ══
                            Branch(A2 != TargetFurnitureActor)
                              True → Cast A2 → BP_FurnitureActor
                                   → ApplyLoadedMaterialToSlot(
                                       Mesh      = CastedA2.FurnitureMesh,
                                       Records   = CastedA2.MaterialSlots,   [ref]
                                       SlotName  = SelectedSlotName,
                                       HintIndex = SelectedSlotIndex,
                                       LoadedMI  = MI,                        [từ Cast pin, không load lại]
                                       RowName   = Conv_NameToString(PendingRowName),
                                       PathFallback = "" ) ●→ bOK
                                   → Branch(bOK)
                                       True  → SET LoadApply_SuccessCount = LoadApply_SuccessCount + 1
                                       False → [dead-end hợp lệ — actor thiếu slot tên đó]
                              False → [dead-end hợp lệ — Primary đã áp ở đầu event]
                          Completed ▶→ ShowToastMsg( Conv_StringToText(
                                         "Áp cho " + (LoadApply_SuccessCount + 1) + "/"
                                         + LoadApply_Selected.Length + " đồ" ) ) ──────────┐
                   False ▶→ ShowToastMsg( Conv_StringToText(
                                "Chỉ áp cho món đang chọn — " + (LoadApply_Selected.Length - 1)
                                + " món khác loại chưa đổi" ) ) ─────────────────────────────┤
     (mọi nhánh merge về đây) ◄─────────────────────────────────────────────────────────────┘
▶→ SerializeSlotRecords → PrintString(Dev) → GetDataTableRow → UpdateThumbnail
   → ClearTimer → SetTimer("CaptureMaterialSnapshot", 0.5s) → AddRecentMaterial   [đuôi cũ GIỮ NGUYÊN]
```

**Chi tiết wiring quan trọng:**
- `MI` = pin `AsMaterial Interface` của node `Cast MaterialInterface` (đã tồn tại, K2Node Knot_34→35). Kéo thêm 1 nhánh data từ pin đó vào ô `LoadedMI` của service node trong VÒNG 2. KHÔNG thêm Async Load mới.
- `Cast A → BP_FurnitureActor` trong VÒNG 1: dùng **pin `bSuccess`** (bool output) cho Branch, KHÔNG rẽ execution qua `CastFailed`. Lý do: giữ chuỗi exec thẳng trong ForEach, tránh dead-end nhánh CastFailed (L2).
- `+ (số)` với chuỗi: các phép `+1`, `Length`, `Length-1` là Integer → phải `Conv_IntToString` (hoặc dùng thẳng Append/Concat với auto-convert) trước khi nối chuỗi. Kết quả chuỗi → `Conv_StringToText` cho `ShowToastMsg`.

### 4. Vì sao 2 vòng loop riêng (không gộp — ghi để không ai "tối ưu" thành bug)

Vòng 1 kiểm cùng loại, vòng 2 apply — **tách biệt CÓ CHỦ ĐÍCH**, KHÔNG phải trùng lặp thừa.

Nếu gộp 1 vòng (vừa duyệt vừa apply): lỡ actor thứ 3 khác loại → 2 actor đầu ĐÃ bị đổi material rồi mới phát hiện phải dừng → sai (fail-unsafe). Phải biết TẤT CẢ cùng loại TRƯỚC khi chạm actor phụ đầu tiên. Ràng buộc "all-or-nothing" → 2 vòng là cách đúng.

**Nguyên lý:** Design for Change — nếu sau này đổi chính sách (cho phép apply một phần), sửa vòng 2 độc lập, không đụng vòng 1.

### 5. Q9 — S-MATRIX (RE-RUN cho Hướng B; hành vi rẽ nhánh theo RowName-match)

**Tầng 1 — S-Scan:**
| ID | Trạng thái | Ô | Ghi chú |
|---|---|---|---|
| S1 | 1 mesh chọn | `→` single | Length=1, không vào multi. Y hành vi cũ |
| S2 | N mesh rời **cùng RowName** | `→` multi-apply | Case bug gốc THẬT (N gối giống hệt) → apply cả cụm |
| S2' | N mesh rời **khác RowName** | `⚠ chỉ Primary + Toast cảnh báo` | MỚI ở B — chặn áp nhầm liên loại |
| S3 | 1 group cùng loại | `→S2` | leaf cùng RowName |
| S3' | 1 group trộn loại | `→S2'` | cảnh báo |
| S4 | combo cả cụm (thường trộn loại) | `⚠ →S2'` | ĐÚNG ví dụ sofa+bàn+ghế: chỉ Primary đổi + báo rõ |
| S5 | không có actor nào (Length=0) | `N/A: SelectedSlotIndex<0 hoặc TargetFurnitureActor invalid → nhánh trên đã chặn ở Branch IsValid trước LoadAndApplyMaterial` | multi không tới được |
| S6 | actor bị destroy giữa chừng | `N/A: SelectedActors đọc tươi tại thời điểm apply; Cast bSuccess guard actor null` | — |
| S7 | slot index lệch giữa actor | `→` service `ResolveSlotIndex` theo tên (Q1 ít trùng) tự lo; actor phụ chỉ chạy khi cùng RowName → slot names khớp | an toàn |
| S8 | mixed lock state | `N/A: multi-apply không đụng lock; apply material không bị chặn bởi bIsLocked (v1)` | — |
| S9 | selection máy sinh | `→` đọc tươi `SelectedActors` → an toàn actor mới spawn | y A |

**Ô đổi hành vi ở B: S2', S3', S4** → đều rẽ về "chỉ Primary + Toast", KHÔNG loop apply. An toàn hơn A.

**Tầng 2 — X-Check (chỉ ô ⚠: S2'/S3'/S4):**
- **X1 Undo:** VÒNG 2 reset debounce timer `CaptureMaterialSnapshot` (0.5s) mỗi lần — 1 CaptureSnapshot cả batch (kiến trúc capture đã ver' ở Việc 2B). Nhánh dị-loại chỉ Primary → 1 snapshot 1 actor, cũng đúng.
- **X2 Persistence:** multi chỉ chạy khi cùng RowName → mọi actor cùng slot names → KHÔNG có case ghi record vào slot không tồn tại trên actor phụ.
- **X7 Toast/Feedback:** CẢ 2 nhánh (multi lẫn dị-loại) đều Toast khi Length>1 → KHÔNG im lặng → vá đúng phần gây hại nhất của bug gốc.

### 6. Q8 (viết VISIBLE trước node flow khi execute)

```
Q8: Container = Custom Event (nối tiếp LoadAndApplyMaterial, Latent Async ở đầu chain — hợp lệ)
  | IsValid: Cast bSuccess pin guard mọi actor trong cả 2 ForEach; service tự trả false không crash
  | L2: mọi nhánh False trong 2 ForEach + 2 nhánh Toast đều merge về SerializeSlotRecords — KHÔNG dead-end fatal
  | No latent thêm (2 ForEach macro + service call, KHÔNG async mới)
  | 6A: 1 CaptureSnapshot sau batch → undo phục hồi cả cụm (nhánh dị-loại chỉ Primary → undo 1 actor, đúng)
```

### 7. TEST Việc 3 (chạy khi code xong)

| # | Setup | Kỳ vọng |
|---|---|---|
| 1 | Chọn 3 mesh **CÙNG RowName** (3 gối giống hệt), ≥1 cái thiếu slot tên đó | Cái có slot đổi đúng, cái thiếu skip → Toast "Áp cho X/3 đồ" |
| 2 | Chọn combo **TRỘN loại** (sofa+bàn+ghế, khác RowName) | **Chỉ Primary đổi**, Toast "Chỉ áp cho món đang chọn — 2 món khác loại chưa đổi". Bàn/ghế KHÔNG đổi màu |
| 3 | Chọn 1 mesh (single) | Đổi đúng, KHÔNG Toast (Length=1) |
| 4 | Sau case 1 → Undo | Cả cụm về nguyên trạng (1 snapshot) |
| 5 | Sau case 2 → Undo | Chỉ Primary về (đúng — chỉ nó đổi) |

PASS 1-5 = `Bug-MaterialPrimaryOnly` đóng theo hướng an toàn (B). Case 2 = bằng chứng B chặn đúng rủi ro áp nhầm sofa+bàn.

**As-built Việc 3** _(Sonnet điền sau test — KHÔNG điền sẵn):_
```
2 (biến class var LoadApply_*) đã thêm: _____
Node flow chèn (V2 điểm chèn): _____
Test 1 (multi cùng loại, skip actor thiếu slot): _____
Test 2 (dị loại → chỉ Primary + Toast cảnh báo): _____
Test 3 (single, không Toast): _____
Test 4-5 (undo): _____
```

---

## VIỆC 4 — Copy/Paste chuyển nguồn sang Records

**Mục tiêu:** Copy đọc từ `MaterialSlots` (không đọc `MaterialOverrides` đã chết); Paste gọi service.

### ✅ [VERIFY #6 + #7] đã xong — 2 phát hiện quan trọng làm plan tốt hơn bản cũ

**Phát hiện 1 — `CopySlotMaterial` ĐÃ CÓ SẴN cơ chế né bug GetObjectName/MID (K2Node thật):**
```
Entry ▶→ IsValid(TargetFurnitureActor) AND SelectedSlotIndex>=0
  True ▶→ SelectedSlotIndex < GetNumMaterials(FurnitureMesh)      ← bounds check, plan cũ BỎ SÓT
     True ▶→ IsEmpty(MaterialOverrides[SelectedSlotIndex])?
        True  (slot NGUYÊN BẢN) → ClipboardMaterialPath = GetPathName(GetMaterial(FurnitureMesh, idx))
        False (slot ĐÃ ĐỔI)     → ClipboardMaterialPath = MaterialOverrides[idx]   ← né đọc material sống (MID)
     False → Print "Slot chưa có vật liệu để copy" (Dev Only) → return
```
Code production **cố tình** không đọc material sống khi slot đã bị MID hoá — bằng chứng cứng cho bug GetObjectName/MID đã nêu ở phiên trước. Sau G2, apply không còn ghi `MaterialOverrides` → nhánh `False` **vĩnh viễn sai** (đọc rỗng) nếu không sửa → xác nhận sửa Copy là BẮT BUỘC, không phải tuỳ chọn.

**Phát hiện 2 — `PasteSlotMaterial` ĐÃ CÓ SẴN cách suy RowName từ path (đóng KP1):**
```
... sau Async Load, IsValid(MI):
  [3 node CreateDMI+SetMaterial+Array_Set(MaterialOverrides) — BỎ]
  ▶→ ClipboardMaterialPath.ParseIntoArray(Delimiter=".") → Array_LastIndex → Get → Conv_StringToName → RowName
     → GetDataTableRow(DT, RowName) → Row Found → UpdateThumbnail(...)
  ▶→ [lặp lại Y HỆT chuỗi ParseIntoArray lần 2] → AddRecentMaterial(RowName)   ← trùng lặp, dọn khi sửa
```
Tách path theo `.` lấy phần tử CUỐI (`/Game/.../MI_X.MI_X` → `MI_X`) làm RowName — cách này đã chạy production, đã đúng (thumbnail + recent material đang hoạt động). **→ KP1 chốt bản C: dùng lại nguyên chuỗi này, tính 1 lần vào `PasteRowName`, dùng chung cho cả 3 chỗ** thay vì tính 2 lần trùng lặp như hiện tại.

### [SỬA] `CopySlotMaterial` (Function) — giữ nguyên khung, chỉ thay ĐÚNG 1 khối
```
Entry ▶→ IsValid(TargetFurnitureActor) AND SelectedSlotIndex>=0
  True ▶→ SelectedSlotIndex < GetNumMaterials(FurnitureMesh)        ← GIỮ, không đụng
     True ▶→ [THAY toàn bộ khối IsEmpty(MaterialOverrides)/2-nhánh bằng:]
             GET TargetFurnitureActor.MaterialSlots
             ForEach MaterialSlots WITH BREAK (Record):             ← L-NEW-7: KHÔNG Array Find (không so 1 field struct)
               Branch(Record.SlotName == SelectedSlotName):
                 True → Branch(Record.MaterialRowName != ""):
                          True  → GetDataTableRow(Record.MaterialRowName) → MaterialPath → SET ClipboardMaterialPath
                          False → SET ClipboardMaterialPath = Record.MaterialPathFallback
                        → Break
             Branch(ClipboardMaterialPath == ""):                   ← không có record → slot nguyên bản
               True → Get Material(FurnitureMesh, SelectedSlotIndex) → Get Object Path Name → SET ClipboardMaterialPath   ← GIỮ NGUYÊN, không đổi
     ▶→ Print "✅ Đã copy vật liệu slot: " + idx (Dev Only)          ← GIỮ, không đụng
     False → Print "Slot chưa có vật liệu để copy" (Dev Only)       ← GIỮ, không đụng
```

### [SỬA] `PasteSlotMaterial` (Custom Event) — giữ nguyên khung, chỉ thay 2 khối
```
Entry ▶→ IsValid(TargetFurnitureActor) AND SelectedSlotIndex>=0 AND ClipboardMaterialPath != ""   ← GIỮ
  True ▶→ MakeSoftObjectPath → LoadAsset(async) → Completed → Cast MaterialInterface → IsValid(MI)?
     True ▶→ IsValid(TargetFurnitureActor)? (guard lặp có sẵn, GIỮ không dọn — ngoài scope)
        True ▶→ [THÊM, tính 1 LẦN, dùng lại y hệt chuỗi có sẵn]:
                 ClipboardMaterialPath.ParseIntoArray(".") → LastIndex → Get → Conv_StringToName
                 → SET PasteRowName
               [THAY CreateDynamicMaterialInstance+SetMaterial+Array_Set(MaterialOverrides) bằng:]
                 ApplyLoadedMaterialToSlot(
                    Mesh=FurnitureMesh, Records=TargetFurnitureActor.MaterialSlots,
                    SlotName=SelectedSlotName, HintIndex=SelectedSlotIndex,
                    LoadedMI=MI, RowName=PasteRowName, PathFallback=ClipboardMaterialPath)
               ▶→ GetDataTableRow(DT, PasteRowName) → Row Found → UpdateThumbnail(...)   ← GIỮ, đổi input dùng PasteRowName thay vì tính lại
               ▶→ ClearTimer + SetTimer("CaptureAfterPaste", 0.3s)                        ← GIỮ
               ▶→ GetAllActorsOfClass(...)[0] → AddRecentMaterial(PasteRowName)           ← GIỮ, dùng lại PasteRowName thay vì tính lại lần 2
           False → dead-end
```
`PathFallback=ClipboardMaterialPath` luôn truyền kèm (an toàn kép, đúng pattern Đ4 đã dùng ở Việc 2/3).

### Q8
```
Copy: Function | IsValid TargetFurnitureActor + idx>=0 + idx<NumMaterials (3 tầng, GIỮ nguyên) | L2: ForEachWithBreak + 2 Branch không nhánh chết còn logic sau | No latent | 6A: N/A
Paste: Custom Event (Latent async hợp lệ) | IsValid MI + IsValid TargetFurnitureActor (2 tầng, GIỮ) | L2: else/CastFailed dead-end hợp lệ | Latent trong Event ✓ | 6A: Reset lo đường ngược
```

**TEST Việc 4:** copy slot **NGUYÊN BẢN** (chưa đổi) → paste sang mesh khác → PASS (đường live vẫn hoạt động). Copy slot **ĐÃ ĐỔI** (qua Việc 2) → paste sang mesh khác → PASS + `MaterialSlots` bên nhận có record đúng RowName (đối chiếu `PasteRowName` khớp tên thật DT, Print JSON). Case thứ 2 là case sẽ FAIL âm thầm nếu Copy không sửa.

**As-built Việc 4** _(#6, #7 đã điền từ VERIFY — Sonnet điền phần Test khi code xong):_
```
#6 tên clipboard thật: ClipboardMaterialPath (đúng dự đoán A) — Copy có bounds check + rẽ nhánh IsEmpty(MaterialOverrides)
#7 KP1 chốt: bản C — dùng lại ParseIntoArray có sẵn trong Paste, không cần FindMaterialRowNameByPath
Test copy slot nguyên bản → paste: _____
Test copy slot đã đổi (qua Việc 2) → paste: _____
```

---

## VIỆC 5 — Reset Slot / Reset All qua service

**Mục tiêu:** Reset đọc/ghi qua hàm service, xóa record đúng, không đụng `MaterialOverrides`.

### ✅ [VERIFY #8] K2Node `BTN_ResetSlot` + `BTN_ResetAll` — đã đọc

```
BTN_ResetSlot:
  IsValid(TargetFurnitureActor) AND SelectedSlotIndex>=0
    True → SetMaterial(FurnitureMesh, idx, StaticMesh.GetMaterial(idx))   ← đọc từ ASSET static mesh, KHÔNG phải FurnitureMesh runtime
           → Array_Set(MaterialOverrides[idx] = "")                       ← xóa override
           → CaptureSnapshot("ResetSlot")
           → GetObjectName(OriginalMat)→Conv_StringToName→GetDataTableRow→Cast(1 swatch)→UpdateThumbnail   ← CHỈ 1 swatch
                                                                             KHÔNG gọi RefreshSlotSwatches()

BTN_ResetAll:
  IsValid(TargetFurnitureActor)
    True → ForLoop(0→NumMaterials-1): SetMaterial(FurnitureMesh, i, StaticMesh.GetMaterial(i))
           Completed → Array_Clear(MaterialOverrides) → CaptureSnapshot("ResetAll") → RefreshSlotSwatches()   ← ĐÃ CÓ SẴN
```

2 điều chỉnh so với dự thảo cũ:
1. **`BTN_ResetSlot` đọc `StaticMesh.GetMaterial()`** (hàm trên UStaticMesh ASSET) — khớp đúng triết lý `ResetSlotToAssetDefault`/`ResetAllSlotsToAssetDefault` (Đ7/Đ10), không phải suy đoán — code cũ và service C++ mới cùng 1 nguyên lý đọc.
2. **`BTN_ResetAll` đã có sẵn `RefreshSlotSwatches()`** ở cuối — GIỮ nguyên, không phải thêm mới. **`BTN_ResetSlot` thì NGƯỢC LẠI — chưa có**, chỉ update 1 swatch qua chuỗi cũ. Đây đúng là chỗ cần đổi (đưa ResetSlot lên ngang hàng ResetAll).

### [SỬA] `BTN_ResetSlot` — `ResetSlotToAssetDefault` (Đ7, mức 2)
```
IsValid(TargetFurnitureActor) AND SelectedSlotIndex>=0     ← GIỮ nguyên guard
  True → Cast → GET FurnitureMesh
         [THAY: SetMaterial + Array_Set(MaterialOverrides) + GetObjectName→Conv_StringToName→GetDataTableRow→Cast(1 swatch)→UpdateThumbnail
          — TOÀN BỘ chuỗi tra-tên-qua-object-name cũ BỎ, không cần nữa]
         ResetSlotToAssetDefault(FurnitureMesh, TargetFurnitureActor.MaterialSlots,
                                  SelectedSlotName, SelectedSlotIndex)
         ▶→ CaptureSnapshot("ResetSlot")           ← GIỮ, thứ tự y hệt cũ (capture TRƯỚC update UI)
         ▶→ Call RefreshSlotSwatches()              ← THÊM, thay cho update-1-swatch cũ
```

### [SỬA] `BTN_ResetAll` — `ResetAllSlotsToAssetDefault` (Đ10) + CLEAR thủ công
```
IsValid(TargetFurnitureActor)                       ← GIỮ nguyên guard
  True → Cast → GET FurnitureMesh
         [THAY: ForLoop(SetMaterial mỗi slot) bằng 1 hàm]
         ResetAllSlotsToAssetDefault(FurnitureMesh)
         ▶→ CLEAR TargetFurnitureActor.MaterialSlots  ← THÊM (Đ10 không tự xóa Records, thay cho Array_Clear(MaterialOverrides) cũ)
         ▶→ CaptureSnapshot("ResetAll")                ← GIỮ, y hệt cũ
         ▶→ Call RefreshSlotSwatches()                 ← GIỮ, ĐÃ có sẵn, không đổi
```

⚠ **Điểm bẫy (từ signature):** `ResetAllSlotsToAssetDefault` **KHÔNG nhận Records** → không tự xóa `MaterialSlots`. Quên CLEAR → record cũ sống sau "Reset All", restore sau (G3) áp nhầm material cũ. Bắt buộc CLEAR tay. `ResetSlotToAssetDefault` CÓ nhận Records nên tự xóa record slot đó — không cần CLEAR tay.

Thứ tự exec cả 2 nút giữ nguyên bản gốc (chỉ thay nội dung node, không đảo trình tự).

### Q8
```
ResetSlot: Event (nút bấm) | IsValid TargetFurnitureActor + idx>=0 (GIỮ) | L2: chuỗi thẳng | No latent | 6A: Undo qua snapshot có sẵn
ResetAll:  Event (nút bấm) | IsValid TargetFurnitureActor (GIỮ) | L2: chuỗi thẳng, ForLoop cũ thay 1 hàm | No latent | 6A: Undo qua snapshot
```

**TEST Việc 5:** đổi 2 slot → BTN_ResetSlot 1 slot → slot đó về gốc, record slot đó biến mất, slot kia giữ (Print JSON còn 1 record). Đổi lại → BTN_ResetAll → cả 2 về gốc, `MaterialSlots` rỗng hoàn toàn. Undo mỗi bước → về trước reset. PASS.

**As-built Việc 5** _(#8 đã điền từ VERIFY — Sonnet điền phần Test khi code xong):_
```
#8 K2Node reset: ResetSlot đọc StaticMesh.GetMaterial() (asset), KHÔNG gọi RefreshSlotSwatches (thêm mới);
                 ResetAll ForLoop tương tự, ĐÃ CÓ SẴN RefreshSlotSwatches (giữ nguyên)
Test ResetSlot (record slot mất, slot kia giữ): _____
Test ResetAll (MaterialSlots rỗng): _____
Undo: _____
```

---

## TEST TỔNG G2 (chạy sau khi 1→5 đều PASS)

| # | Case | Kỳ vọng | Kết quả |
|---|---|---|---|
| 1 | Apply đơn 1 slot | mesh đúng + 1 record đúng | ☐ |
| 2 | Swatch thumbnail **lúc apply** | hiện đúng (KHÔNG test reselect) | ☐ |
| 3 | Multi 3 đồ (1 đồ thiếu slot) | Toast đúng + skip đúng | ☐ |
| 4 | Copy → Paste sang mesh khác cùng tên slot | đúng + record đúng | ☐ |
| 5 | Reset Slot / Reset All | về gốc + record khớp (1 còn / rỗng hết) | ☐ |
| 6 | Undo mỗi thao tác trên | phục hồi đúng | ☐ |
| 7 | `MaterialSlots` Print JSON sau mỗi bước | record khớp, không rác | ☐ |

PASS toàn bộ → **G2 ĐÓNG.** `MaterialOverrides` thành legacy (G3 migration đọc nó cho save cũ).

---

## THỨ TỰ THỰC THI & VÌ SAO

```
Bước 0 (nền: 3 biến)
Việc 1 (swatch tên + selection)          ← Việc 2 cần SelectedSlotName từ đây
Việc 2 (⭐ reroute apply — VALIDATE Records ghi)  ← làm sớm; FAIL → STOP
Việc 2B (⭐ đường khôi phục snapshot — VALIDATE undo/redo)  ← GATE, PASS mới sang Việc 3; resequence 03/09
Việc 3 (multi-apply — lặp pattern Việc 2)
Việc 4 (copy/paste — lặp pattern)
Việc 5 (reset — lặp pattern)
Test tổng G2
```
Mỗi việc PASS test riêng mới sang việc sau. Rủi ro lớn nhất gate = cặp **Việc 2 + 2B** (đường ghi + đường ngược).

---

## SAU KHI G2 ĐÓNG — bàn giao Claude Code (chưa làm bây giờ)

Khi 7/7 test tổng PASS, gom vào command block giao Claude Code merge canonical:
- `01_Session_State.md`: Current Task → S7.G2 ĐÓNG, sang G3.
- `Plans/Sprint7_MaterialEdit_Plan_v1.1.md`: thêm section "ĐẦU RA S7.G2" (bảng việc + test + deviation nếu có).
- `Widgets/WBP_FurnitureInventory.md`: cập nhật as-built `RefreshSlotSwatches`, `LoadAndApplyMaterial`, Copy/Paste, Reset (banner as-built + K2Node date).
- `Widgets/WBP_SlotSwatch.md`: thêm biến `SlotName`.
- `Blueprints/BP_FurnitureActor.md`: thêm biến `MaterialSlots` (nếu Bước 0 thêm mới).
- `PROGRESS.md` + `DEVIATIONS.md`: ghi "Replace giữ material slot trùng tên" nếu chạm ở đây (thực ra thuộc G4 — chỉ ghi nếu phát sinh).
- Bug-MaterialPrimaryOnly → chuyển trạng thái đóng trong `Bugs/Open_Bugs.md`.

Giới hạn Claude Code: chỉ merge as-built Sonnet đã điền trong file này — KHÔNG tự sửa node flow / chữ ký / tên biến "cho khớp". Không ground truth thì BÁO, không SỬA.
