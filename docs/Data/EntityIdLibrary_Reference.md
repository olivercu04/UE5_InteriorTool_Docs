# EntityIdLibrary — C++ Blueprint Function Library Reference
**Nguồn:** `Plugins/FurnitureToolkit/Source/FurnitureToolkit/Public/EntityIdLibrary.h` + `Private/EntityIdLibrary.cpp` (viết mới 21/09/2026, U1.1 PersistentIdentity)
**Cập nhật:** 21/09/2026

> File này là TÀI LIỆU THAM KHẢO — liệt kê function signature + hành vi thật, đã Spec-test PASS
> (Automation Spec, xem mục Test bên dưới). Task card gốc: `Sprints/Sprint7/21-09-2026_U1_PersistentIdentity_TaskCard.md`.

---

## Class: UEntityIdLibrary
**Plugin:** FurnitureToolkit | Base: `UBlueprintFunctionLibrary`
**Files:** `EntityIdLibrary.h` / `EntityIdLibrary.cpp`
**Macro API:** `FURNITURETOOLKIT_API` (khớp `MaterialParamMap.h`, V8 xác nhận compile sạch)

**Mục đích:** cấp GUID-string ổn định cho actor (PersistentID) — sinh 1 lần, giữ nguyên qua
Undo/Redo respawn + EMS Save/Load. Xem toàn bộ kiến trúc dùng ở `Blueprints/BP_FurnitureActor.md`
(Event ActorLoaded), `Blueprints/BP_FurnitureInputManager.md` (SpawnFurnitureCopy), `Widgets/WBP_DragOverlay_FurnitureCard.md`
(On Drop), `Blueprints/BP_UndoManager.md` (CaptureSnapshot/RestoreSnapshot), `Blueprints/BP_FurnitureSceneManager.md`
(ResolveByPersistentId — đọc lại các ID này).

---

## Hàm 1 — EnsurePersistentId

```cpp
UFUNCTION(BlueprintCallable, Category = "Undo|Identity")
static FString EnsurePersistentId(const FString& Current);
```

**Blueprint node:** `Ensure Persistent Id`

**Params:**
| Param | Kiểu | Mô tả |
|---|---|---|
| Current | String | Giá trị `PersistentID` hiện tại của actor (có thể rỗng) |

**Return:** String — GUID mới (nếu Current rỗng) hoặc chính Current (nếu đã có)

**Logic:**
```cpp
FString UEntityIdLibrary::EnsurePersistentId(const FString& Current)
{
    if (!Current.IsEmpty()) { return Current; }        // ID-07: đã có → giữ, KHÔNG sinh lại
    return FGuid::NewGuid().ToString(EGuidFormats::Digits);  // ID-01: sinh mới
}
```

**Idempotent theo thiết kế** — gọi lại nhiều lần với Current đã có giá trị luôn trả về y hệt,
an toàn để gọi ở nhiều điểm (4 producer: `ActorLoaded`, `SpawnFurnitureCopy`, `On Drop` card-drag,
và gián tiếp qua `RestoreSnapshot`→`SpawnFurnitureCopy`).

**⚠️ Vì sao KHÔNG gọi trong `Event BeginPlay`:** BeginPlay chạy TRƯỚC khi EMS restore xong
SaveGame field — gọi Ensure ở đó có thể sinh ID mới đè lên ID cũ chưa kịp nạp (vi phạm ID-08).
Gọi ở `Event ActorLoaded` (event riêng của EMS, đảm bảo chạy SAU khi SaveGame field đã restore)
mới an toàn về thứ tự.

---

## Hàm 2 — IsValidPersistentId

```cpp
UFUNCTION(BlueprintPure, Category = "Undo|Identity")
static bool IsValidPersistentId(const FString& Id);
```

**Blueprint node:** `Is Valid Persistent Id`

**Params:**
| Param | Kiểu | Mô tả |
|---|---|---|
| Id | String | Chuỗi cần kiểm |

**Return:** Boolean — `true` nếu không rỗng

**Logic:**
```cpp
bool UEntityIdLibrary::IsValidPersistentId(const FString& Id)
{
    return !Id.IsEmpty();
}
```

Helper thuần, hiện chưa có call site chính thức trong U1 (dự phòng cho U2/U3 khi UI cần check
nhanh mà không phải so `!= ""` thủ công).

---

## Test — Automation Spec `FurnitureTool.Undo.U1_Identity`

**File:** `Plugins/FurnitureToolkit/Source/FurnitureToolkit/Private/Tests/EntityIdTests.cpp`
**Chạy:** Session Frontend → Automation → filter `FurnitureTool.Undo.U1` (không cần PIE)

| Test | Kiểm | Kết quả |
|---|---|---|
| `[UNDO-ID-01]` | Input rỗng → sinh GUID không rỗng | ✓ PASS |
| `[UNDO-ID-07]` | Input đã có giá trị → trả nguyên, KHÔNG sinh lại | ✓ PASS |
| `[UNDO-ID-01b]` | 2 lần gọi với input rỗng → 2 GUID KHÁC NHAU | ✓ PASS |

**Negative control (21/09/2026):** sửa tạm `EnsurePersistentId` thành `return Current;` (bỏ nhánh
sinh) → chạy lại → `[UNDO-ID-01]` ĐỎ đúng như kỳ vọng (input rỗng ra rỗng, test biết kêu) → khôi
phục code gốc → 3/3 xanh lại. Test protocol 5-bước (Contract → Red → Green → Negative Control →
Restore) hoàn tất đầy đủ.

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 21/09/2026 | Tạo mới (U1.1, PersistentIdentity). `EnsurePersistentId` + `IsValidPersistentId`. Spec test 3/3 PASS + negative control xác nhận test biết kêu. |

---

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Có mặt trong thao tác:** [[L03 · Kéo đồ vào phòng|L03]] · [[L12 · Lưu và mở cảnh|L12]]

**Thuộc mảng kết nối:** [[Kết nối 3c - Inventory + Cây thư mục]] · [[Kết nối 3d - Save Undo khởi động]]

**← Được gọi bởi**
- [[WBP_DragOverlay_FurnitureCard]] — sinh ID cho đồ kéo-thả (producer thứ 4, U1.2 21/09) · EnsurePersistentId()
- [[BP_FurnitureActor]] — sinh/giữ ID lúc actor tải xong (Event ActorLoaded) · EnsurePersistentId()
- [[BP_FurnitureInputManager]] — sinh ID cho đồ mới (Duplicate/Paste) · SpawnFurnitureCopy: EnsurePersistentId()

<!-- BRAIN:END -->
