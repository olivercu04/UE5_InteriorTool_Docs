# WBP_DetailPopup
**Phiên bản:** 1.1 | **Cập nhật:** 25/05/2026 — 17:29 ICT | Popup thông tin sản phẩm + Scale editor

---

## Variables
```
FurnitureDA   : DA_FurnitureItem
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

## InitPopup(DA DA_FurnitureItem, bFromScene Boolean)
```
SET FurnitureDA = DA
SET bIsFromScene = bFromScene
SET bLockRatio = True  ← default lock khi mở popup
Set Brush from Lazy Texture (IMG_LockIcon, T_Lock)
SET Brush from Lazy Texture (LazyImage_Thumbnail, DA.Thumbnail)
SET Text (TB_Name, DA.VieName)
SET Text (TB_Category, DA.Category)
SET Text (TB_Description, DA.Description)

Branch bFromScene == True?
  True:
    Set Visibility (VB_ScaleSection, Visible)
    Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
    → GET SelectedFurnitureActor → Get Actor Scale 3D → CurrentScale
    CurrentSize = DA.BoundingSize × CurrentScale (Break Vector × Break Vector)
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
NewScaleX = NewL / FurnitureDA.BoundingSize.X
NewScaleY = Float(ET_WidthScale) / FurnitureDA.BoundingSize.Y
NewScaleZ = Float(ET_HeightScale) / FurnitureDA.BoundingSize.Z
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
    SET Text (ET_LengthScale, FurnitureDA.BoundingSize.X)
    SET Text (ET_WidthScale, FurnitureDA.BoundingSize.Y)
    SET Text (ET_HeightScale, FurnitureDA.BoundingSize.Z)
    SET OriginalSize = FurnitureDA.BoundingSize
    Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Scale")
```

---

## BTN_ChangeMesh OnClicked — v1.1
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → FurnitureInputRef
SET bIsReplaceMode = True (FurnitureInputRef)
SET MeshToReplace = GET SelectedFurnitureActor (FurnitureInputRef)

GET FurnitureDA.MeshFolderPath

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
Launch URL (FurnitureDA.Link)
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
