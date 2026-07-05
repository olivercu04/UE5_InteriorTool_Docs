# Delta — Sprint7_MaterialEdit_Plan v1.0 → v1.1 (quyết định của Fable)
**05/07/2026 — nguồn:** Fable review delta Sonnet 04/07 + tự soi. Merge vào `Sprint7_MaterialEdit_Plan_v1.md`, bump header thành `Version: 1.1 | Cập nhật: 05/07/2026 <giờ:phút lúc commit>`.

---

## A. QUYẾT ĐỊNH MỚI — thêm vào bảng mục 1 (đánh số tiếp)

| # | Quyết định |
|---|---|
| Đ6 | `ApplyLoadedMaterialToSlot`: tìm record theo SlotName → sửa tại chỗ, không có → Add (không bao giờ Add trùng). Đổi MI → **CLEAR ParamsJson** slot đó (param cũ vô nghĩa trên MI mới) |
| Đ7 | Factory reset ("Đặt lại vật liệu") **tách khỏi PathFallback**: hàm mới `ResetSlotToAssetDefault` đọc thẳng `GetStaticMesh()->GetStaticMaterials()[idx]`, SetMaterial về gốc + **xóa record**. PathFallback chỉ còn 1 nghĩa: Đ4 + save cũ |
| Đ8 | `ResolveSlotIndex == -1` khi: tên không tồn tại trên mesh hiện tại VÀ HintIndex ngoài range. Mọi hàm ghi return **false** khi -1 |
| Đ9 | **RestoreMyMaterialSlots = chuỗi tuần tự tự gọi**, KHÔNG ForEach + Async (ForEach macro không chờ latent; event param lưu per-actor không per-lần-gọi → aliasing L11 chắc chắn). 1 load bay/1 thời điểm |
| Đ10 | **Restore bước 0 = ResetAllSlotsToAssetDefault** trước khi apply records → idempotent + vá lỗ "undo về MaterialSlots rỗng mà mesh vẫn hiện MID cũ". Đánh đổi: nháy material gốc ~1 frame lúc restore async — chấp nhận v1 |
| Đ11 | `ApplyParamsJsonToSlot` cũng MID-on-demand (case Đ4 restore: slot nguyên bản chỉ có param, chưa có MID) |
| Đ12 | Texture param restore (load texture trong ApplyParamsJsonToSlot kiểu gì) → treo, quyết ở G7 cùng Q2 |

**Trả lời 7 câu hỏi làm rõ (delta Sonnet 04/07):**
1. `MaterialRowName` String OK — FName so sánh case-insensitive, `FName(*Str)` tra DT an toàn. Giữ String cho JSON.
2. `FindMaterialRowNameByPath`: [VERIFY] signature thật đầu G1. Contract: miss → `MaterialRowName=""` + `MaterialPathFallback=path cũ` → restore đi đường fallback.
3. `MaterialSurvey` có compile vào shipping → guard đầu thân cả 3 hàm: `#if UE_BUILD_SHIPPING return false; #endif`.
4. Ngưỡng Q1 5% = số tạm; chốt thật theo report G0c + danh sách mesh dính (mesh hay vào combo quan trọng hơn %).
5. JSON casing không lẫn: JsonObjectConverter tự đổi PascalCase field → lowerCamel (kể cả struct lồng). Verify bằng mắt test G1.
6. `DT_MaterialInstancesCatalog` chưa có cột nhóm pattern → Q2 ra static thì thêm cột `PatternGroup` (hoặc derive từ họ G0a). Ghi TODO vào G7.
7. Naming §9 áp cho widget có ≥2 event dùng chung class var (WBP_MaterialParamPanel → `MPP_`); row widget nhỏ tên trần.

---

## B. SỬA S7.G0

Thêm trước "Chạy khảo sát":

### G0a-0 — Smoke test (BẮT BUỘC trước khi chạy full DT)
1. Đầu `SurveyMasterFamilies` thêm check: `AR.IsLoadingAssets()` == true → prepend cảnh báo `"[WARN] AssetRegistry chưa scan xong — Unresolved có thể là false"` vào OutSummary (không chặn, chỉ báo).
2. Chạy `SurveyMasterFamilies` trên DataTable test 1 dòng (hoặc chấp nhận chạy full nhưng CHỈ đọc kết quả 1 MI RDMtiles biết trước master) → master ra đúng tên → mới tin số liệu full run. Ra `(KHONG_LAN_DUOC)` → tag `Parent` sai/thiếu → STOP, báo Fable, chuyển Plan B load-theo-lô.

### Ghi chú G0c (thêm cuối Việc 3)
`ForceGarbageCollection(true)` trong loop chỉ cắm cờ cho frame sau — trong 1 lần gọi GC KHÔNG nổ. Memory bound thực = batch size mỗi call → giữ `Count ≤ 100`, dòng GC in-loop vô hại nhưng không được tăng batch vì tin nó.

---

## C. SỬA S7.G1 — API bổ sung TRƯỚC khi đóng băng

Thêm vào class `UMaterialSlotService`:
```cpp
  // Đ7: factory reset — đọc default từ StaticMesh asset, xóa record. KHÔNG dùng PathFallback.
  static bool ResetSlotToAssetDefault(UStaticMeshComponent* Mesh,
      UPARAM(ref) TArray<FMaterialSlotRecord>& Records,
      const FString& SlotName, int32 HintIndex);

  // Đ10: reset TOÀN BỘ slot về default asset (bước 0 của restore). Không đụng Records.
  static bool ResetAllSlotsToAssetDefault(UStaticMeshComponent* Mesh);
```

Sửa comment các hàm:
- `ApplyLoadedMaterialToSlot`: thêm dòng `// Đ6: record theo SlotName — sửa tại chỗ hoặc Add, không Add trùng. Đổi MI → clear ParamsJson của slot.`
- `ResolveSlotIndex`: thêm `// Đ8: -1 khi tên không có trên mesh hiện tại VÀ HintIndex ngoài range → caller ghi phải return false.`
- `ApplyParamsJsonToSlot`: thêm `// Đ11: MID-on-demand như SetSlotXParam. Đ12: texture param — cách load chốt ở G7.`

Thêm vào TEST G1: `Apply MI lần 2 cùng slot → Records vẫn 1 record/slot (không trùng) + ParamsJson đã clear` | `ResetSlotToAssetDefault → material về gốc + record biến mất`.

---

## D. SỬA S7.G2 — mục 5

Thay: "mức 2 = apply lại material gốc qua service (PathFallback/gốc)"
Bằng: "mức 2 = `ResetSlotToAssetDefault` (Đ7 — đọc StaticMesh asset, KHÔNG đụng PathFallback), mức 1 = `ClearSlotParams`".

---

## E. SỬA S7.G3 — thay TOÀN BỘ mục 1 (RestoreMyMaterialSlots)

```
Q8: 2 Custom Event chuỗi | IsValid Mesh + IsValid loaded asset ✓ |
L2: mọi nhánh (kể cả load fail) đều tới idx++ → chain không kẹt ✓ |
Latent trong Custom Event ✓ (không Function) |
6A: reset-trước-apply → idempotent, gọi lại nhiều lần (EMS+snapshot+combo) không cộng dồn,
    undo về Records rỗng vẫn trả mesh về nguyên bản ✓
```

**1. RestoreMyMaterialSlots** (Custom Event trên BP_FurnitureActor — MỘT đường duy nhất, chuỗi TUẦN TỰ Đ9):
```
RestoreMyMaterialSlots ▶→
  Branch(MaterialSlots.Length == 0 AND MaterialOverrides cũ có dữ liệu)   ← đường LEGACY
    True ▶→ BuildRecordsFromLegacy(...) ●→ SET MaterialSlots
  (merge)
  ▶→ ResetAllSlotsToAssetDefault(FurnitureMesh)        ← Đ10, bước 0
  ▶→ SET Rst_SlotIdx = 0
  ▶→ Rst_LoadNextSlot

Rst_LoadNextSlot (Custom Event) ▶→
  Branch(Rst_SlotIdx >= MaterialSlots.Length)
    True → [xong]
    False ▶→ MaterialSlots Get(Rst_SlotIdx) ●→ SET Rst_CurRecord   ← temp var, không đọc pure 2 lần
      ▶→ RowName != "" → tra DT lấy path; rỗng → PathFallback
      ▶→ Async Load Asset → Completed
        ▶→ Branch(IsValid loaded asset)                 ← load fail KHÔNG được kẹt chain
          True ▶→ ApplyLoadedMaterialToSlot ▶→ ApplyParamsJsonToSlot
        (merge) ▶→ SET Rst_SlotIdx = Rst_SlotIdx + 1 ▶→ Rst_LoadNextSlot   ← tự gọi
```
Class var mới trên BP_FurnitureActor: `Rst_SlotIdx : int`, `Rst_CurRecord : FMaterialSlotRecord` (KHÔNG SaveGame).
Ghi chú: nếu test 6A lộ double-apply do 2 lần gọi chồng nhau giữa chừng → thêm `Rst_Generation` counter (mỗi lần gọi ++, Completed check khớp mới chạy tiếp). Chỉ thêm KHI test fail, không thêm trước (KP2).

**TEST G3 — thêm 2 case vào ma trận:**
| 8 | Apply MI → CaptureSnapshot → **Undo** | mesh về material NGUYÊN BẢN (Đ10 — lỗ đã vá) |
| 9 | Actor ≥2 slot khác material → save/load | CẢ HAI slot đúng, không slot cuối "thắng" |

---

## F. SỬA S7.G8

Thêm vào đo `stat rhi`: chuỗi undo ×5 trên actor có MID — reset-rồi-áp tạo MID mới mỗi restore, MID cũ phải được GC (không tích lũy). Ghi số vào DEVIATIONS.

---

## G. DOC UPDATES (mục cuối plan) — thêm 1 dòng DEVIATIONS soạn sẵn

(4) *RestoreMyMaterialSlots đổi từ ForEach+Async (plan v1.0) sang chuỗi tuần tự + reset bước 0 (Đ9/Đ10) — lý do: aliasing L11 + lỗ undo-về-rỗng.*

---

## H. Claude Code command block

```
Đọc file 05-07-2026_Delta_Sprint7_v1.1_FableDecisions.md rồi làm:
1. Mở docs/Plans/Sprint7_MaterialEdit_Plan_v1.md
2. Merge theo đúng mục A→G của delta:
   - A: thêm Đ6–Đ12 vào bảng QUYẾT ĐỊNH mục 1 + thêm sub-section "Trả lời 7 câu hỏi (05/07/2026)" ngay dưới bảng
   - B: chèn G0a-0 + ghi chú GC vào S7.G0
   - C: thêm 2 hàm mới + 3 dòng comment vào khối API S7.G1, thêm 2 test vào TEST G1
   - D: thay câu mục 5 của S7.G2
   - E: thay toàn bộ mục 1 của S7.G3 (kèm khối Q8) + thêm case 8, 9 vào ma trận TEST G3
   - F: thêm dòng đo MID-undo vào S7.G8
   - G: thêm dòng DEVIATIONS (4)
3. Đổi header: Version 1.1 | Cập nhật: 05/07/2026 <giờ:phút hiện tại>
4. KHÔNG sửa gì ngoài các mục trên (KP3). Xong in diff cho cuhoang review trước khi commit.
```
