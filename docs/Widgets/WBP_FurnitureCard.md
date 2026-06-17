# WBP_FurnitureCard
**Phiên bản:** 1.0 | **Tạo:** 17/06/2026 — Sprint D.T6 | Card hiển thị 1 mặt hàng nội thất trong inventory

> **Sprint D.T6:** File này document WBP_FurnitureCard SAU khi bỏ DA_FurnitureItem. Trước D.T6, WBP_FurnitureCard được document trong `WBP_DragOverlay_FurnitureCard.md` (vẫn còn đó cho WBP_DragOverlay). Từ D.T6 WBP_FurnitureCard có file riêng.
>
> **Nguồn thực tế:** WBP_FurnitureCard trong Blueprint — implement `IUserObjectListEntry`, nhận `BP_FurnitureItemView` từ ListView.

---

## Variables

```
CardRowName    : Name               ← RowName của item trong DT_FurnitureCatalog; SET ở OnListItemObjectSet
InventoryRef   : WBP_FurnitureInventory
PreviewActor   : BP_FurnitureActor  ← ghost actor khi drag
DragOverlayRef : WBP_DragOverlay
```

> ⚠ **Đã XÓA:** `FurnitureDA : DA_FurnitureItem` (Sprint D.T6). Pre Construct của widget này không có logic gì (confirmed).

---

## Layout (Canvas Panel)

```
Canvas Panel
├── LazyImage_Thumb
├── Button_InforItem (+ Common Lazy Image)
├── Button_ChangeMesh (+ Common Lazy Image, Visibility = Hidden mặc định)
│   ← chỉ hiện khi bIsReplaceMode = True (check trong OnListItemObjectSet)
└── Button_FavoriteFurniture (+ Common Lazy Image — heart icon, anchor top-right, 32×32)
```

---

## OnListItemObjectSet

```
Cast Item Object → BP_FurnitureItemView → SET CardRowName = ItemView.RowName
Get Data Table Row(DT_FurnitureCatalog, CardRowName) → Row Found → Break S_FurnitureData → RowData
→ Set Brush from Lazy Texture (LazyImage_Thumb, RowData.ThumbnailSoft)

Branch IsValid(InventoryRef)?
  False:
    Get Game Instance → Cast Foff_GameInstance → GET FurnitureInventoryRef
    Branch IsValid(FurnitureInventoryRef)?
      True → SET InventoryRef = FurnitureInventoryRef

Branch IsValid(InventoryRef)?
  True:
    Branch InventoryRef.bIsReplaceMode == True?
      True  → Set Visibility(Button_ChangeMesh, Visible)
      False → Set Visibility(Button_ChangeMesh, Hidden)
  False:
    Set Visibility(Button_ChangeMesh, Hidden)

→ Call UpdateFavTint
```

> ⚠ `BP_FurnitureItemView` là object wrapper truyền qua ListView (không phải DA). Struct chứa RowName. Sprint D tạo 1 BP_FurnitureItemView per filtered row khi populate grid.

---

## UpdateFavTint (Function)

```
GET All Actors of Class(BP_FurnitureUserPrefsManager) → GET [0]
→ Is Favorite Mesh(CardRowName)
→ Branch:
  T → Set Color and Opacity(Button_FavoriteFurniture, R=1, G=0.3, B=0.3, A=1)   ← hồng
  F → Set Color and Opacity(Button_FavoriteFurniture, R=1, G=1, B=1, A=0.3)     ← mờ
```

---

## Button_FavoriteFurniture OnClicked

```
GET All Actors of Class(BP_FurnitureUserPrefsManager) → GET [0]
→ Toggle Favorite Mesh(CardRowName)
→ Call UpdateFavTint
```

---

## Button_InforItem OnClicked

```
Call OnCardInfoClicked(CardRowName)
```

> `OnCardInfoClicked` là custom event trong WBP_FurnitureInventory — mở WBP_DetailPopup với RowName.

---

## BTN_ChangeMesh OnClicked

```
Call F_ExecuteReplace   ← xem WBP_DragOverlay_FurnitureCard.md § F_ExecuteReplace
```

---

## On Drag Detected

```
1. DeactivateGizmo  ← PHẢI đầu tiên
2. Create WBP_DragVisual → Not Hit-Testable
3. Create BP_DragDropOperation_FurnitureCard → SET RowName = CardRowName
4. Get Data Table Row(DT_FurnitureCatalog, CardRowName) → Row Found → Break S_FurnitureData
   → Static Mesh ●→ Load Asset Blocking .Asset → Return Value (StaticMesh)
   Spawn BP_FurnitureActor (0,0,0) → GET FurnitureMesh → Set Static Mesh
5. SET PreviewActor
6. Create WBP_DragOverlay → Add to Viewport → SET PreviewActorRef
7. Return Operation
```

---

## On Drag Cancelled

```
IsValid(DragOverlayRef) → Remove from Parent → SET None
IsValid(PreviewActor) → Destroy Actor → SET None
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 17/06/2026 — Sprint D.T6 | Tạo mới — tách từ WBP_DragOverlay_FurnitureCard.md. Implement D.T6: bỏ FurnitureDA, dùng CardRowName + BP_FurnitureItemView + DT_FurnitureCatalog. |
