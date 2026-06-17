# WBP_DetailPopup
**Phiên bản:** 1.2 | **Cập nhật:** 17/06/2026 — Sprint D.T6 | Popup thông tin sản phẩm + Scale editor

> **v1.2 (Sprint D.T6):** Bỏ `FurnitureDA : DA_FurnitureItem` — thay bằng `RowData : S_FurnitureData`. `InitPopup` nhận `RowName : Name` thay `DA`. Toàn bộ `FurnitureDA.*` → `RowData.*`. BTN_ChangeMesh đọc `RowData.MeshFolderPath`.

---

## Variables
```
RowData       : S_FurnitureData  ← v1.2 Sprint D (thay FurnitureDA đã xóa)
bIsDragging   : Boolean
DragOffset    : Vector2D
PopupPosition : Vector2D
bIsFromScene  : Boolean  ← True = mở từ scene (hiện Scale section), False = từ inventory (ẩn)
bLockRatio    : Boolean  ← True = giữ tỉ lệ khi nhập kích thước (default = True)
OriginalSize  : Vector   ← kích thước khi mở popup, dùng làm reference cho lock ratio
```

---

## Hierarchy
```
WBP_DetailPopup
└── Canvas Panel
    └── Size Box
        └── Background Blur
            └── Vertical Box
                ├── TitleBar (Horizontal Box)
                │   ├── TextBlock_Detail "Detail"
                │   └── Button_XClosePopup
                │       └── Text "x"
                ├── LazyImage_Thumbnail
                ├── TB_Name "Name"
                ├── TB_Category "Category"
                ├── VB_ScaleSection (Vertical Box, Is Variable)
                │   ├── Border
                │   ├── Spacer
                │   ├── Horizontal Box (header)
                │   │   ├── Text "Kích thước (cm)"
                │   │   └── Spacer
                │   ├── Spacer
                │   └── Horizontal Box (inputs)
                │       ├── Vertical Box (Lock)
                │       │   ├── Text "Lock"
                │       │   └── Border → Button_LockScale
                │       ├── Spacer
                │       ├── Vertical Box (L)
                │       │   ├── Text "Length (L)"
                │       │   └── Border → ET_LengthScale
                │       ├── Spacer
                │       ├── Vertical Box (W)
                │       │   ├── Text "Width (W)"
                │       │   └── Border → ET_WidthScale
                │       ├── Spacer
                │       ├── Vertical Box (H)
                │       │   ├── Text "Height (H)"
                │       │   └── Border → ET_HeightScale
                │       ├── Spacer
                │       └── Vertical Box (Reset)
                │           ├── Text "Reset"
                │           └── Border → Button_ResetScale
                ├── TB_Description "Description"
                ├── BTN_ChangeMesh  ← mở inventory filter theo MeshFolderPath
                └── BTN_BuyLink
                    └── Text "Buy Now"
```

---

## Is Variable widgets
```
VB_ScaleSection   : VerticalBox
ET_LengthScale    : EditableText (trong Border)
ET_WidthScale     : EditableText (trong Border)
ET_HeightScale    : EditableText (trong Border)
Button_LockScale  : Button (trong Border) + IMG_LockIcon (Common Lazy Image bên trong)
Button_ResetScale : Button (trong Border)
```

---

## InitPopup(RowName Name, bFromScene Boolean)  ← v1.2: thay DA DA_FurnitureItem
```
Get Data Table Row(DT_FurnitureCatalog, RowName) → Row Found → Break S_FurnitureData → SET RowData
SET bIsFromScene = bFromScene
SET bLockRatio = True  ← default lock khi mở popup
Set Brush from Lazy Texture (IMG_LockIcon, T_Lock)
SET Brush from Lazy Texture (LazyImage_Thumbnail, RowData.ThumbnailSoft)
SET Text (TB_Name, RowData.VieName)
SET Text (TB_Category, RowData.Category)
SET Text (TB_Description, RowData.Description)

Branch bFromScene == True?
  True:
    Set Visibility (VB_ScaleSection, Visible)
    Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
    → GET SelectedFurnitureActor → Get Actor Scale 3D → CurrentScale
    CurrentSize = RowData.BoundingSize × CurrentScale (Break Vector × Break Vector)
    SET OriginalSize = CurrentSize
    SET Text (ET_LengthScale, CurrentSize.X)
    SET Text (ET_WidthScale, CurrentSize.Y)
    SET Text (ET_HeightScale, CurrentSize.Z)
  False:
    Set Visibility (VB_ScaleSection, Collapsed)
```

---

## Button_LockScale OnClicked
```
SET bLockRatio = NOT bLockRatio
Branch bLockRatio == True?
  True → Set Brush from Lazy Texture (IMG_LockIcon, T_Lock)
  False → Set Brush from Lazy Texture (IMG_LockIcon, T_Unlock)
```

---

## ET_LengthScale OnTextCommitted (OnEnter only)
```
Text To Float → NewL
Branch bLockRatio == True?
  True:
    Ratio = NewL / OriginalSize.X
    NewW = OriginalSize.Y × Ratio → SET Text (ET_WidthScale)
    NewH = OriginalSize.Z × Ratio → SET Text (ET_HeightScale)
  False: (chỉ đổi L)

↓ Cả 2 nhánh gặp nhau:
NewScaleX = NewL / RowData.BoundingSize.X
NewScaleY = Float(ET_WidthScale) / RowData.BoundingSize.Y
NewScaleZ = Float(ET_HeightScale) / RowData.BoundingSize.Z
Clamp min = 0.01 cho cả 3
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
→ GET SelectedFurnitureActor → Branch IsValid?
  True → Set Actor Scale3D
Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Scale")
```
← ET_WidthScale và ET_HeightScale OnTextCommitted tương tự, đổi axis tương ứng

---

## Button_ResetScale OnClicked
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
→ GET SelectedFurnitureActor → Branch IsValid?
  True:
    Set Actor Scale3D (1, 1, 1)
    SET Text (ET_LengthScale, RowData.BoundingSize.X)
    SET Text (ET_WidthScale, RowData.BoundingSize.Y)
    SET Text (ET_HeightScale, RowData.BoundingSize.Z)
    SET OriginalSize = RowData.BoundingSize
    Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Scale")
```

---

## BTN_ChangeMesh OnClicked — v1.1
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → FurnitureInputRef
SET bIsReplaceMode = True (FurnitureInputRef)
SET MeshToReplace = GET SelectedFurnitureActor (FurnitureInputRef)

GET RowData.MeshFolderPath

Get Game Instance → Cast Foff_GameInstance → GET FurnitureInventoryRef
Branch IsValid(FurnitureInventoryRef)?
  True:
    Branch IsValid(FurnitureInventoryRef)?  ← double check
      True → Cast WBP_FurnitureInventory
             → SET bIsReplaceMode = True   ← SET trực tiếp (không gọi EnterReplaceMode)
             → FilterByFolderPathWithUI(MeshFolderPath)
             → Call RefreshCardReplaceMode  ← v1.1: Regenerate SAU khi cards đã populate
  False:
    Create WBP_FurnitureInventory → Add to Viewport
    Cast Foff_GameInstance → SET FurnitureInventoryRef
    Cast WBP_FurnitureInventory
    → SET bIsReplaceMode = True
    → FilterByFolderPathWithUI(MeshFolderPath)
    → Call RefreshCardReplaceMode   ← v1.1

← Cả 2 nhánh:
Remove from Parent (DetailPopup)
```

⚠️ **Lý do dùng SET trực tiếp thay EnterReplaceMode:** `EnterReplaceMode` gọi `Regenerate All Entries` ngay lập tức, nhưng `FilterByFolderPathWithUI` sau đó xóa và tạo lại toàn bộ cards → Regenerate bị vô hiệu. Phải gọi `RefreshCardReplaceMode` SAU `FilterByFolderPathWithUI`.

---

## Button_XClosePopup OnClicked
```
Remove from Parent
```

---

## BTN_BuyLink OnClicked
```
Launch URL (RowData.Link)
```

---

## Drag (TitleBar)
```
OnPressed: bIsDragging=True, DragOffset = MousePos - PopupPosition
OnReleased: bIsDragging=False
Event Tick: Branch bIsDragging → Set Position = MousePos - DragOffset / ViewportScale
```

---

## Lưu ý
- OriginalSize SET 1 lần khi mở popup — không update sau mỗi lần Enter
- Lock ratio dùng OriginalSize làm reference cố định
- Clamp min scale = 0.01 để tránh mesh biến mất
- bIsFromScene = False khi mở từ WBP_FurnitureCard inventory → VB_ScaleSection ẩn
- bIsFromScene = True khi mở từ BTN_Info trong WBP_MeshControls
- BTN_ChangeMesh luôn hiện — dùng để mở inventory filter theo MeshFolderPath để replace mesh

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 22/04/2026 | Logic gốc |
| 1.1 | 25/05/2026 — 17:29 ICT | BTN_ChangeMesh: thêm RefreshCardReplaceMode sau FilterByFolderPathWithUI. Fix: Regenerate phải chạy SAU populate cards |
| 1.2 | 17/06/2026 — Sprint D.T6 | Bỏ FurnitureDA → RowData : S_FurnitureData. InitPopup(RowName, bFromScene): DT lookup thay DA load. Toàn bộ DA.* → RowData.*. BTN_BuyLink: RowData.Link. BTN_ChangeMesh: RowData.MeshFolderPath. |
