# WBP_FurnitureInventory — PATCH NOTES
**Phiên bản:** 2.3 | **Cập nhật:** 27/05/2026 — 10:30 ICT

Đây là bản ghi các thay đổi cần merge vào WBP_FurnitureInventory.md chính.

---

## 1. Cập nhật header

```
Phiên bản: 2.3 | Cập nhật: 27/05/2026 — 10:30 ICT
```

---

## 2. Thêm vào bảng Variables — nhóm Resize Window (v1.2)

Thêm sau dòng `bIsReplaceMode`:

```
| **— v1.2 Resize Window —** | | |
| `bIsResizing` | Boolean | Đang kéo resize viền cửa sổ |
| `ResizeDirection` | Integer | Hướng kéo: 0=None, 1=Top, 2=Bottom, 3=Left, 4=Right, 5=TL, 6=TR, 7=BL, 8=BR |
| `ResizeStartMousePos` | Vector2D | Vị trí chuột lúc bắt đầu kéo |
| `ResizeStartSize` | Vector2D | Kích thước cửa sổ lúc bắt đầu kéo |
| `ResizeStartPosition` | Vector2D | Vị trí cửa sổ lúc bắt đầu kéo |
```

---

## 3. Cập nhật Layout — thêm 8 BTN_Resize

Thêm sau `BTN_MinimizedIcon`:

```
Canvas Panel
├── HB_TitleBar
├── BackgroundBlur_246
├── BTN_MinimizedIcon
├── — v1.2 Resize handles (cuối cùng — Z Order cao nhất) —
├── BTN_ResizeTop      (6px dày, cạnh trên)
├── BTN_ResizeBottom   (6px dày, cạnh dưới)
├── BTN_ResizeLeft     (6px rộng, cạnh trái)
├── BTN_ResizeRight    (6px rộng, cạnh phải)
├── BTN_ResizeTL       (12×12, góc trên-trái)
├── BTN_ResizeTR       (12×12, góc trên-phải)
├── BTN_ResizeBL       (12×12, góc dưới-trái)
└── BTN_ResizeBR       (12×12, góc dưới-phải)
```

Config 8 button: Style Draw As = None (trong suốt), Visibility = Visible, Is Variable = True.

---

## 4. Cập nhật Window Controls

Thay đổi section Window Controls:

```
Drag (BTN_TitleBar) — v1.2 CẬP NHẬT:
  OnPressed: bIsDragging=True
             Slot as Canvas Slot (VerticalBox_0) → Get Position → CurrentPos
             DragOffset = MousePos on Viewport - CurrentPos
             ← v1.2: đổi từ InventoryPosition sang Get Position trực tiếp
  OnReleased: bIsDragging=False
  Tick: Get Mouse Position on Viewport → NewPos = MousePos - DragOffset
        Slot as Canvas Slot (VerticalBox_0) → Set Position (NewPos)
        ← v1.2: đổi từ Set Position in Viewport (self) sang Slot as Canvas Slot
        SET InventoryPosition = NewPos
        Call UpdateResizeHandles

Resize (8 BTN_Resize) — v1.2 MỚI:
  OnPressed: Call StartResize(Direction)
  ← OnReleased không cần SET bIsResizing — ResizeWindow tự check mouse button

Maximize: toggle
  True:  Set Position(0,0), Size=ViewportSize/Scale
         Set Visibility (8 BTN_Resize) = Collapsed
  False: restore OriginalPosition, OriginalSize
         Set Visibility (8 BTN_Resize) = Visible
         Call UpdateResizeHandles

Minimize: Collapse BackgroundBlur + HB_TitleBar → Show BTN_MinimizedIcon
          Set Visibility (8 BTN_Resize) = Collapsed

BTN_MinimizedIcon: Show HB_TitleBar + BackgroundBlur → Set Position(100,100)
                   Set Visibility (8 BTN_Resize) = Visible
                   Call UpdateResizeHandles
```

---

## 5. Thêm Functions/Events mới

```
StartResize (Custom Event, input: Direction : Integer)
  → SET bIsResizing, ResizeDirection, ResizeStartMousePos, ResizeStartSize, ResizeStartPosition

UpdateResizeHandles (Function)
  → Tính và set Position + Size cho 8 BTN_Resize dựa trên VerticalBox_0 Canvas Slot

ResizeWindow (Function)
  → Full resize logic: check mouse button, delta, 4 boolean hướng, clamp min, apply
  → Chi tiết: xem WBP_ResizeWindow.md
```

---

## 6. Thêm vào Key Learnings

```
- Slot as Canvas Slot Get Size trả về (0,0) nếu chưa Set Size explicit
  → Gọi Set Size (512, 1024) trong Event Construct
- Drag và Resize phải dùng cùng hệ tọa độ (Slot as Canvas Slot)
  → Nếu drag dùng Set Position in Viewport và resize dùng Canvas Slot → window nhảy
- Resize button nhỏ (6px) → OnReleased fire khi rời button
  → Dùng Is Mouse Button Down trong ResizeWindow thay OnReleased
- False branch trong Sequence phải để trống
  → Nếu False SET lại giá trị sẽ overwrite kết quả Then trước đó
- Tên đúng trong UE5: "Slot as Canvas Slot" (không phải "Slot as Canvas Panel Slot")
- Recent/Favorite Furniture cần SET FilteredItems + CurrentPage=0 + Call DisplayPage
  → Thay vì Add Item trực tiếp để pagination hoạt động đúng
```

---

## 7. Cập nhật Lịch sử

```
| 2.3 | 27/05/2026 — 10:30 ICT | Resize Window 8 hướng. Fix drag dùng Slot as Canvas Slot.
                                  Fix Recent/Favorite DisplayPage. Fix AddRecentMesh. |
```

