# WBP_ComboCard
**Phiên bản:** 1.2 | **Tạo:** 24/06/2026 (C4) | Card hiển thị 1 combo trong tab 🧩 Combo (WBP_FurnitureInventory)

> **File này TẠO MỚI 15/07/2026** — widget đã tồn tại và có version history từ 24/06/2026
> (ghi rải rác trong `01_Session_State.md` mục KIẾN TRÚC HIỆN TẠI + `PROGRESS.md`), nhưng
> chưa từng có file `.md` riêng. Nội dung v1.0/v1.1 dưới đây TÁI DỰNG từ các ghi chú đó
> (không phải export node-level trực tiếp từ Blueprint) — cuhoang xác nhận nếu có sai khác
> với Blueprint thật, đặc biệt tên biến/layout chưa từng được ghi chi tiết node-by-node.
> Nội dung v1.2 (G4, DefaultThumbBrush + hiển thị Thumbnail) lấy từ delta 15/07/2026, xác nhận cao hơn.

> **Nguồn thực tế:** implement `IUserObjectListEntry`, nhận `BP_ComboItemView` từ `CTV_ComboCard`
> (TileView trong WBP_FurnitureInventory, Entry Widget Class = WBP_ComboCard).

---

## Variables

```
InventoryRef      : WBP_FurnitureInventory   ← lazy-init từ GameInstance.FurnitureInventoryRef
                                                 trong OnListItemObjectSet nếu chưa có (v1.1, 01/07)
DefaultThumbBrush : Slate Brush              ← MỚI v1.2 (G4) — chụp 1 lần ở Event Construct
                                                 (Get LazyImage_ThumbCombo.Brush), dùng làm fallback
                                                 khi combo chưa có Thumbnail
```

⚠️ `ComboID`/`ComboName`/`ItemCount`... không cần biến riêng trên card — đọc thẳng qua
`ComboItem` (kiểu `BP_ComboItemView`, field chuẩn IUserObjectListEntry) mỗi lần cần, giống
pattern `WBP_MaterialCard`.

---

## Layout (Canvas Panel, suy luận từ pattern WBP_FurnitureCard/WBP_MaterialCard)

```
Canvas Panel
├── LazyImage_ThumbCombo (CommonLazyImage — Common UI plugin)
├── TextBlock (tên combo)
├── Badge "×N" (ItemCount)
└── BTN_DeleteCombo — layout có sẵn từ C4, CHƯA bind handler (delete combo chưa implement, xem DEVIATIONS 15/07/2026)
```

---

## Event Construct (MỚI, v1.2 — G4)
```
Get LazyImage_ThumbCombo → Get .Brush → SET DefaultThumbBrush
```

---

## OnListItemObjectSet

```
Cast Item Object → BP_ComboItemView → ComboItem
→ set tên/badge (TextBlock ← ComboItem.ComboName, Badge ← ComboItem.ItemCount)

Branch IsValid(InventoryRef)?
  False:
    Get Game Instance → Cast Foff_GameInstance → GET FurnitureInventoryRef
    Branch IsValid(FurnitureInventoryRef)?
      True → SET InventoryRef = FurnitureInventoryRef

→ Branch(IsValid(ComboItem.Thumbnail)):     ← MỚI v1.2 (G4)
    True  → SetBrushFromTexture(LazyImage_ThumbCombo, ComboItem.Thumbnail)
    False → SET LazyImage_ThumbCombo.Brush = Get DefaultThumbBrush
```
⚠️ **QUAN TRỌNG (G4):** TileView/ListView tái sử dụng widget instance (virtualization) —
nhánh False KHÔNG được "để trống", phải reset tường minh về `DefaultThumbBrush`, nếu không
widget giữ brush từ lần bind TRƯỚC (bug cross-combo thumbnail — xem `DEVIATIONS.md` 15/07/2026,
gốc bug là `GetComboThumbnail` thiếu Return Node, nhưng card-side cũng phải tự guard).

`LazyImage_ThumbCombo` là `CommonLazyImage` (Common UI plugin) — dùng `Set/Get Brush`
(property trực tiếp) hoặc `SetBrushFromTexture` (nhận Texture2D* thẳng), KHÔNG dùng
`SetBrushFromLazyTexture` (chỉ cho Soft Object Reference tới UAsset thật, không áp dụng cho
texture runtime CreateTransient).

---

## On Mouse Button Down (v1.1, 01/07/2026)
```
RMB → InventoryRef.OnComboCardRightClicked(ComboItem.ComboID) → Return Handled
LMB → Return Unhandled   ← KHÔNG được Handled, phá drag-drop
```

---

## On Drag Detected (v1.0, C4 24/06/2026)
```
Spawn BP_ComboGhostActor (dùng ComboItem.BoundingBoxExtent)
Create BP_DragDropOperation_ComboCard → SET ComboID = ComboItem.ComboID, ComboExtent = ComboItem.BoundingBoxExtent
Return Operation
```
> Chi tiết ghost/surface-snap đầy đủ: xem `01_Session_State.md` mục KIẾN TRÚC HIỆN TẠI
> (BP_ComboGhostActor, WBP_DragOverlay_FurnitureCard On Drag Over/On Drop nhánh combo).

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 24/06/2026 (C4) | Tạo mới — OnListItemObjectSet, OnDragDetected → spawn BP_ComboGhostActor + BP_DragDropOperation_ComboCard. |
| 1.1 | 01/07/2026 | +InventoryRef (lazy-init từ GameInstance.FurnitureInventoryRef trong OnListItemObjectSet); +On Mouse Button Down override (RMB → InventoryRef.OnComboCardRightClicked(ComboID) → Handled; LMB → Unhandled không phá drag-drop). |
| 1.2 | 15/07/2026 (P1.G4) | File `.md` riêng TẠO MỚI (trước đó chỉ ghi rải rác). +DefaultThumbBrush (Slate Brush, chụp ở Event Construct). OnListItemObjectSet mở rộng: Branch IsValid(ComboItem.Thumbnail) → SetBrushFromTexture / else reset về DefaultThumbBrush (bắt buộc vì TileView tái sử dụng widget instance). |
