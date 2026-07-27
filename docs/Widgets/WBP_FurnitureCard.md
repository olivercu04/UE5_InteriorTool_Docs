# WBP_FurnitureCard
**Phiên bản:** 1.1 | **Cập nhật:** 24/07/2026 — C9.0c: migrate `bIsReplaceMode`→`ReplaceTarget`, thêm `Get_Button_ChangeMesh_Visibility` (bug fix, chưa từng document) | Card hiển thị 1 mặt hàng nội thất trong inventory

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
│   ← chỉ hiện khi ReplaceTarget == E_ReplaceTarget::Mesh (check trong OnListItemObjectSet;
│     migrate C9.0c 24/07/2026, trước là bIsReplaceMode = True)
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
    Branch InventoryRef.ReplaceTarget == E_ReplaceTarget::Mesh?   ← [MIGRATE, C9.0c 24/07/2026] trước là bIsReplaceMode == True
      True  → Set Visibility(Button_ChangeMesh, Visible)
      False → Set Visibility(Button_ChangeMesh, Hidden)
  False:
    Set Visibility(Button_ChangeMesh, Hidden)

→ Call UpdateFavTint
```
> So sánh trực tiếp `== E_ReplaceTarget::Mesh` (không dùng `IsReplaceModeActive()`) — card
> furniture chỉ nên hiện nút khi đang replace đúng loại Mesh, không phải Combo.

> ⚠ `BP_FurnitureItemView` là object wrapper truyền qua ListView (không phải DA). Struct chứa RowName. Sprint D tạo 1 BP_FurnitureItemView per filtered row khi populate grid.

---

## Get_Button_ChangeMesh_Visibility — Function (property binding getter, MỚI đưa vào doc, C9.0c 24/07/2026)

⚠️ Hàm này **chưa từng được document trước đây** — không nằm trong EventGraph chính nên bị bỏ
sót lúc viết doc ban đầu. Phát hiện + fix trong phiên migrate C9.0c, verify qua K2Node export
thật.

```
FunctionEntry.then
▶→ PrintString(DevelopmentOnly) ●← Conv_BoolToString(InventoryRef.ReplaceTarget == E_ReplaceTarget::Mesh)
▶→ Branch(InventoryRef.ReplaceTarget == E_ReplaceTarget::Mesh)
     True  ▶→ Return "Visible"
     False ▶→ Return "Hidden"
```
Đây là hàm getter tự sinh cho **Property Binding** trên Designer panel (nút "fx" cạnh
Visibility) — KHÁC với Branch trong `OnListItemObjectSet` ở trên (2 cơ chế riêng biệt cùng kiểm
tra 1 điều kiện).

**Bug fix, root cause:** trước migrate, node `EqualEqual_BoolBool` so sánh `bIsReplaceMode ==
True` — sau khi biến `bIsReplaceMode` bị xóa (migrate sang `ReplaceTarget`), pin `Condition.A`
rớt về default `false` → luôn `false == true` → Button_ChangeMesh luôn `Hidden` vĩnh viễn (dù
`OnListItemObjectSet` đã set đúng qua nhánh khác — 2 cơ chế conflict, binding thắng vì chạy sau
mỗi tick). Bài học: hàm getter dạng Property Binding dễ bị bỏ sót khi audit vì không nằm trong
EventGraph chính — chỉ Compile All Blueprints mới bắt được lỗi (báo "not found" vì tham chiếu
cross-class tới `InventoryRef.bIsReplaceMode` đã xóa).

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
| 1.1 | 24/07/2026 — C9.0c | Migrate `bIsReplaceMode` (Boolean) → `ReplaceTarget` (Enum `E_ReplaceTarget`) trong `OnListItemObjectSet` (so sánh trực tiếp `== Mesh`, không dùng `IsReplaceModeActive()` — card cần phân biệt loại). Thêm `Get_Button_ChangeMesh_Visibility` (Function getter cho Property Binding, chưa từng document trước đây) — bug fix: node `EqualEqual` đọc biến `bIsReplaceMode` đã xóa → luôn Hidden vĩnh viễn, chỉ Compile All Blueprints mới bắt được. Verify qua K2Node export thật, test regression 5/5 PASS. Chi tiết: `Blueprints/BP_FurnitureInputManager.md` v2.5. |
