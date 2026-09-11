# WBP_MaterialCard
**Tạo mới:** 11/09/2026 — TÁCH RIÊNG khỏi `Blueprints/Blueprint_Logic_NodeFlow.md` mục `WBP_MaterialCard`
(nội dung cũ MIGRATE nguyên văn xuống dưới) + thêm as-built S7.G5.1 (kéo-thả material). Cùng pattern
1-widget-quan-trọng-1-file đã áp cho `WBP_FurnitureCard.md`/`WBP_ComboCard.md`.
**Phiên bản:** 1.0 | **Nguồn:** `11-09-2026_S7G5_G5.1-G5.3_AsBuilt_Delta.md` mục 4.2-4.5, 4.1.

---

## Variables
```
MaterialItem   : BP_MaterialItem            — item data cho card
InventoryRef   : WBP_FurnitureInventory     — lazy-init từ GameInstance.FurnitureInventoryRef
DragOverlayRef : WBP_DragOverlay            — MỚI (S7.G5.1, 11/09/2026), hard ref lúc đang kéo — clear ở On Drag Cancelled + Event Destruct (R2/R4)
```

---

## OnListItemObjectSet
```
Cast Object To BP_MaterialItem → SET MaterialItem
Branch IsValid(InventoryRef):
  F: GetGameInstance → Cast Foff_GameInstance → GET FurnitureInventoryRef → SET InventoryRef
SetBrushFromLazyTexture(LazyImage_ThumbMI, MaterialItem.ThumbnailMI)
```

## Button_ChangeMaterial OnClicked
```
Branch IsValid(InventoryRef) AND IsValid(MaterialItem):
  T: Call InventoryRef.ApplyMaterial(MaterialItem.RowName)
```
> Đường CŨ, vẫn sống song song với đường kéo-thả mới (`OnDragDetected` dưới) — bấm nút vẫn apply
> ngay cho `TargetFurnitureActor` đang mở panel, không cần kéo-thả.

---

## OnDragDetected — MỚI (S7.G5.1, 11/09/2026, as-built)

> Function Override (KHÔNG phải Custom Event — có tab Local Variable như Function thật, do
> `BlueprintImplementableEvent` engine expose qua nút Override). Mô phỏng
> `WBP_FurnitureCard.On Drag Detected`, BỎ phần spawn ghost actor — material không có ghost.
> Q8: `Event OnDragDetected | IsValid: N/A (chỉ tạo object + set field) | L2: không Branch | No
> latent | 6A: On Drag Cancelled dọn overlay/visual`.

```
Event OnDragDetected (MyGeometry, PointerEvent)
▶→ Create Widget
     Class = WBP_DragVisual
     Owning Player = Get Owning Player
   Return Value ●→ [dùng lại 3 chỗ dưới]

▶→ Set Brush from Lazy Texture
     Target      = (WBP_DragVisual) → GET LazyImage_ThumbVisual
     LazyTexture = MaterialItem.ThumbnailMI

▶→ Set Visibility
     Target     = WBP_DragVisual instance
     Visibility = Not Hit-Testable

▶→ Construct Object from Class
     Class = BP_DragDropOperation_Material
   Return Value ●→
     SET MaterialRowName    = MaterialItem.RowName
     SET Pivot               = Mouse Down
     SET Default Drag Visual = WBP_DragVisual instance

▶→ Create Widget
     Class = WBP_DragOverlay
     Owning Player = Get Owning Player
   Return Value ●→
     Add to Viewport
     SET DragOverlayRef (self) = Return Value
     (PreviewActorRef KHÔNG set — để None, material không có ghost actor)

▶→ Return Node
     Operation ●← Construct Object from Class (BP_DragDropOperation_Material) Return Value
```

**[THÊM MỚI] Layout `WBP_DragVisual`:** thêm 1 `Common Lazy Image`, đặt tên `LazyImage_ThumbVisual`
— widget này trước đây KHÔNG có Image widget nào (dùng cho spawn ghost actor 3D của
Furniture/Combo, không cần hiện thumbnail 2D). Material là trường hợp đầu tiên cần hiện thumbnail
trên `WBP_DragVisual`.

## On Drag Cancelled — MỚI (S7.G5.1, 11/09/2026)
```
▶→ IsValid(DragOverlayRef) → True → Remove From Parent → SET DragOverlayRef = None
```

## Event Destruct — cập nhật (S7.G5.1, 11/09/2026)
```
SET MaterialItem = None
SET InventoryRef = None
SET DragOverlayRef = None   ← MỚI, cùng nhóm hard ref clear (R4) với WBP_FurnitureCard.DragOverlayRef, WBP_ComboCard.DragOverlayRef
```

---

## BP_DragDropOperation_Material — class mới (parent `DragDropOperation`)

> Em út của bộ 3 `DragDropOperation` con (`BP_DragDropOperation_FurnitureCard`,
> `BP_DragDropOperation_ComboCard`, giờ thêm class này) — cùng pattern: 1 field payload chính
> (RowName/ComboID), tạo trong `OnDragDetected` của card nguồn tương ứng. Documented tại đây theo
> pattern `BP_DragDropOperation_ComboCard` (documented inline trong `WBP_ComboCard.md`, không có
> file class riêng).

```
Variable: MaterialRowName : Name (default None)
```
KISS — chỉ 1 field. Không thêm gì khác (YAGNI).

✅ **G5.4 (11/09/2026):** debug Print `Operation.MaterialRowName` ở đầu `WBP_DragOverlay.On Drop`
(artifact G5.1, xem `Widgets/WBP_DragOverlay_FurnitureCard.md`) đã XÓA thật — không còn tồn tại
trong code.

**Test G5.1 PASS 3/3 (11/09/2026):** thumbnail bám chuột khi kéo · RowName in đúng qua debug Print
ở On Drop · thả hụt ngoài viewport → overlay dọn sạch, kéo card khác vẫn chạy bình thường (không
leak, không kẹt input).

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 11/09/2026 | Tạo file riêng (tách khỏi `Blueprint_Logic_NodeFlow.md`). Migrate `OnListItemObjectSet`/`Button_ChangeMaterial OnClicked`/`Event Destruct` nguyên văn. Thêm as-built S7.G5.1: `DragOverlayRef`, `OnDragDetected`, `On Drag Cancelled`, `BP_DragDropOperation_Material`. Test PASS 3/3. |
