# WBP_ComboCard
**Phiên bản:** 1.4 | **Tạo:** 24/06/2026 (C4) | Card hiển thị 1 combo trong tab 🧩 Combo (WBP_FurnitureInventory) — 22/07/2026: Field Kích thước + Delete Combo bind handler

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
├── VB_Info
│     ├── TextBlock_ComboName (tên combo)
│     ├── TextBlock_Badge (×N, ItemCount)
│     └── TextBlock_Dimensions ← MỚI v1.3 (22/07/2026) — "L×W×H m — S m²", font nhỏ hơn tên
│           combo, màu xám nhạt (style phụ chú)
└── BTN_DeleteCombo — layout có sẵn từ C4, bind handler DONE 22/07/2026 (xem mục
      "BTN_DeleteCombo — Delete Combo" bên dưới)
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
→ SET TextBlock_ComboName.Text ← ComboItem.ComboName
→ SET TextBlock_Badge.Text ← ComboItem.ItemCount ("×N")

→ MỚI v1.3 (22/07/2026) — Field Kích thước, nối tiếp sau SET TextBlock_Badge, TRƯỚC lazy-init InventoryRef:
ComboItem.BoundingBoxExtent ●→ Break Vector (X, Y, Z)
X ●→ × 0.02 ●→ SET Local Float "L"     (half-extent → full extent cm → m)
Y ●→ × 0.02 ●→ SET Local Float "W"
Z ●→ × 0.02 ●→ SET Local Float "H"
L ●→ × W ●→ SET Local Float "S"        (diện tích sàn)
L ●→ To Text (Float) [MinFrac=1, MaxFrac=1] ●→ LText
W ●→ To Text (Float) [MinFrac=1, MaxFrac=1] ●→ WText
H ●→ To Text (Float) [MinFrac=1, MaxFrac=1] ●→ HText
S ●→ To Text (Float) [MinFrac=1, MaxFrac=1] ●→ SText
Format Text
  Format string: "{L}×{W}×{H} m — {S} m²"
  L ← LText | W ← WText | H ← HText | S ← SText
  Return Value ●→ SET TextBlock_Dimensions.Text

Branch IsValid(InventoryRef)?
  False:
    Get Game Instance → Cast Foff_GameInstance → GET FurnitureInventoryRef
    Branch IsValid(FurnitureInventoryRef)?
      True → SET InventoryRef = FurnitureInventoryRef

→ Branch(IsValid(ComboItem.Thumbnail)):     ← MỚI v1.2 (G4)
    True  → SetBrushFromTexture(LazyImage_ThumbCombo, ComboItem.Thumbnail)
    False → SET LazyImage_ThumbCombo.Brush = Get DefaultThumbBrush
```

**Ghi chú Field Kích thước (v1.3, 22/07/2026):**
- Combo cũ hoặc lỗi data có `BoundingBoxExtent = (0,0,0)` → hiện `"0,0×0,0×0,0 m — 0,0 m²"`.
  KHÔNG phải bug — không crash, không Accessed None. Không cần fix (backlog nếu cần sau).
- Dấu phẩy thập phân (`2,3` không phải `2.3`) — do `Use Grouping`/locale hệ thống, giữ nguyên
  theo quyết định cuhoang (22/07/2026), không đổi sang locale quốc tế.
- **[SỬA 22/07/2026, xem `BP_ComboManager.md` mục Dimension Fix]** `BoundingBoxExtent` nguồn từ
  `CalculateComboBoundingExtent` — công thức đổi từ `Get Actor Bounds` (World AABB) sang
  `Get Local Bounds × Scale + Location` để tránh phồng khi 1 món tự xoay tại chỗ. Giới hạn còn
  lại (cả đội hình combo xoay lệch trục vẫn phồng) — xem `Bugs/Open_Bugs.md` mục
  Feature-CanonicalStudioAngle.

⚠️ **QUAN TRỌNG (G4):** TileView/ListView tái sử dụng widget instance (virtualization) —
nhánh False KHÔNG được "để trống", phải reset tường minh về `DefaultThumbBrush`, nếu không
widget giữ brush từ lần bind TRƯỚC (bug cross-combo thumbnail — xem `DEVIATIONS.md` 15/07/2026,
gốc bug là `GetComboThumbnail` thiếu Return Node, nhưng card-side cũng phải tự guard).

`LazyImage_ThumbCombo` là `CommonLazyImage` (Common UI plugin) — dùng `Set/Get Brush`
(property trực tiếp) hoặc `SetBrushFromTexture` (nhận Texture2D* thẳng), KHÔNG dùng
`SetBrushFromLazyTexture` (chỉ cho Soft Object Reference tới UAsset thật, không áp dụng cho
texture runtime CreateTransient).

---

## BTN_DeleteCombo — Delete Combo (MỚI, DONE 22/07/2026)

Bind ở Event Construct, nối tiếp bind sẵn có:
```
BTN_DeleteCombo.OnClicked ▶→ Branch(IsValid(InventoryRef))
     True  ▶→ InventoryRef.RequestDeleteCombo(ComboItem.ComboID, ComboItem.ComboName)
     False ▶→ dead-end
```
Logic xóa thật (confirm dialog, xóa file, dọn Favorite/Recent/thumbnail cache) nằm trong
`WBP_FurnitureInventory.RequestDeleteCombo`/`HandleDeleteComboConfirmed` — xem
`Widgets/WBP_FurnitureInventory.md`. Test 5/5 case PASS.

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
| 1.3 | 22/07/2026 | +TextBlock_Dimensions trong VB_Info (dưới TextBlock_Badge). OnListItemObjectSet mở rộng: tính L/W/H/S từ `ComboItem.BoundingBoxExtent` (×0.02 = half-extent→full extent cm→m), format qua `To Text (Float)` MinFrac=MaxFrac=1 + `Format Text` → `"{L}×{W}×{H} m — {S} m²"`. Node `To Text (Float)` mới confirm — xem `AI_Implementation_Rules.md`. Test PASS: card hiện đúng kích thước hợp lý so với combo thật. |
| 1.4 | 22/07/2026 (tiếp) | **Delete Combo DONE, 5/5 test PASS.** `BTN_DeleteCombo.OnClicked` bind ở Event Construct → `Branch(IsValid(InventoryRef))` → `InventoryRef.RequestDeleteCombo(ComboItem.ComboID, ComboItem.ComboName)`. Logic xóa thật nằm ở `WBP_FurnitureInventory`. Layout note BTN_DeleteCombo cập nhật (trước ghi "chưa bind handler"). |
