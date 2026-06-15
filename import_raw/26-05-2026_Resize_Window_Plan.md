# Resize Window 8 hướng — WBP_FurnitureInventory
**Phiên bản:** 1.0 | **Ngày:** 26/05/2026
**Ước tính:** nửa ngày — 1 ngày

---

## Tổng quan

Thêm khả năng kéo viền cửa sổ Inventory để thay đổi kích thước,
giống cửa sổ Windows. 8 hướng: 4 cạnh + 4 góc.

---

## BƯỚC 1 — Thêm biến mới (5 phút)

Mở WBP_FurnitureInventory → My Blueprint → Variables, thêm:

| Tên biến | Kiểu | Mặc định | Ghi chú |
|----------|------|----------|---------|
| bIsResizing | Boolean | False | Đang kéo resize? |
| ResizeDirection | Integer | 0 | Hướng kéo (0=None, 1-8) |
| ResizeStartMousePos | Vector2D | (0,0) | Vị trí chuột lúc bắt đầu kéo |
| ResizeStartSize | Vector2D | (0,0) | Kích thước cửa sổ lúc bắt đầu kéo |
| ResizeStartPosition | Vector2D | (0,0) | Vị trí cửa sổ lúc bắt đầu kéo |
| CurrentWindowSize | Vector2D | (720,630) | Kích thước hiện tại |
| MinWindowSize | Vector2D | (400,300) | Kích thước tối thiểu |

Quy ước ResizeDirection:
```
1 = Top       2 = Bottom
3 = Left      4 = Right
5 = TopLeft   6 = TopRight
7 = BottomLeft  8 = BottomRight
0 = None
```

---

## BƯỚC 2 — Thêm 8 Image resize handle vào layout (20-30 phút)

Mở WBP_FurnitureInventory Designer. Thêm 8 Image widget
làm con của root Canvas Panel. Mỗi Image:
- Brush = None (trong suốt)
- Tint = hoàn toàn trong suốt (Alpha = 0)
- Visibility = Hit Test Invisible → đổi sang **Visible** (cần nhận mouse)
- Is Variable = True

### Đặt tên + vị trí

**4 cạnh (dải mỏng 6px):**

| Widget | Anchor | Vị trí trên cửa sổ |
|--------|--------|-------------------|
| IMG_ResizeTop | — | Dải ngang 6px, sát cạnh trên |
| IMG_ResizeBottom | — | Dải ngang 6px, sát cạnh dưới |
| IMG_ResizeLeft | — | Dải dọc 6px, sát cạnh trái |
| IMG_ResizeRight | — | Dải dọc 6px, sát cạnh phải |

**4 góc (ô vuông 12×12px, đè lên góc):**

| Widget | Vị trí trên cửa sổ |
|--------|-------------------|
| IMG_ResizeTL | Góc trên-trái |
| IMG_ResizeTR | Góc trên-phải |
| IMG_ResizeBL | Góc dưới-trái |
| IMG_ResizeBR | Góc dưới-phải |

⚠️ VÌ root Canvas Panel fills viewport (không phải fills cửa sổ),
KHÔNG dùng anchor. Thay vào đó, đặt position + size bằng code
trong Bước 4 (UpdateResizeHandles).

Trong Designer: đặt tạm tất cả 8 Image ở góc trên-trái,
kích thước tạm 12×12. Code sẽ reposition chúng.

**Thứ tự Z-Order:** 8 Image này phải nằm TRÊN HB_TitleBar
và BackgroundBlur (kéo xuống cuối danh sách con trong Hierarchy
panel, hoặc dùng Z Order cao hơn).

---

## BƯỚC 3 — Custom Event: StartResize (10 phút)

Tạo Custom Event `StartResize` với input:
- Direction : Integer

Logic:
```
StartResize(Direction):
  SET bIsResizing = True
  SET ResizeDirection = Direction
  GET Mouse Position → chia Get Viewport Scale → SET ResizeStartMousePos
  SET ResizeStartSize = CurrentWindowSize
  SET ResizeStartPosition = InventoryPosition
```

(InventoryPosition là biến đã có — vị trí cửa sổ hiện tại)

---

## BƯỚC 4 — Custom Event: UpdateResizeHandles (15 phút)

Tạo Custom Event `UpdateResizeHandles` — đặt lại vị trí + kích thước
8 Image handle dựa trên vị trí + kích thước cửa sổ hiện tại.

```
UpdateResizeHandles:
  Pos = InventoryPosition
  Size = CurrentWindowSize
  Handle = 6 (độ dày cạnh, px)
  Corner = 12 (kích thước góc, px)

  === 4 CẠNH ===

  IMG_ResizeTop:
    Slot Position = (Pos.X + Corner, Pos.Y - Handle/2)
    Slot Size     = (Size.X - Corner*2, Handle)

  IMG_ResizeBottom:
    Slot Position = (Pos.X + Corner, Pos.Y + Size.Y - Handle/2)
    Slot Size     = (Size.X - Corner*2, Handle)

  IMG_ResizeLeft:
    Slot Position = (Pos.X - Handle/2, Pos.Y + Corner)
    Slot Size     = (Handle, Size.Y - Corner*2)

  IMG_ResizeRight:
    Slot Position = (Pos.X + Size.X - Handle/2, Pos.Y + Corner)
    Slot Size     = (Handle, Size.Y - Corner*2)

  === 4 GÓC ===

  IMG_ResizeTL:
    Slot Position = (Pos.X - Handle/2, Pos.Y - Handle/2)
    Slot Size     = (Corner, Corner)

  IMG_ResizeTR:
    Slot Position = (Pos.X + Size.X - Corner + Handle/2, Pos.Y - Handle/2)
    Slot Size     = (Corner, Corner)

  IMG_ResizeBL:
    Slot Position = (Pos.X - Handle/2, Pos.Y + Size.Y - Corner + Handle/2)
    Slot Size     = (Corner, Corner)

  IMG_ResizeBR:
    Slot Position = (Pos.X + Size.X - Corner + Handle/2, Pos.Y + Size.Y - Corner + Handle/2)
    Slot Size     = (Corner, Corner)
```

Cách SET Slot Position + Size trong Blueprint:
```
Slot(IMG_ResizeTop as Canvas Panel Slot)
  → Set Position → (X, Y)
  → Set Size → (Width, Height)
```

Gọi `UpdateResizeHandles` ở:
- Cuối Event Construct (sau khi set InventoryPosition)
- Cuối mỗi frame trong Event Tick nếu bIsDragging hoặc bIsResizing
- Sau Maximize/Restore

---

## BƯỚC 5 — Bind OnPressed + OnReleased cho 8 handle (20 phút)

⚠️ Image widget KHÔNG có OnPressed event.
Giải pháp: đổi 8 Image thành **Button** (BTN_ResizeTop, BTN_ResizeBottom...).
Style = hoàn toàn trong suốt:
- Normal / Hovered / Pressed: Tint Alpha = 0, Draw As = None

Hoặc: bọc mỗi Image trong 1 SizeBox + Button.

Đề xuất: dùng **Button trực tiếp** (không cần Image bên trong), đơn giản hơn.

### Bind cho mỗi Button:

**BTN_ResizeTop — OnPressed:**
```
Call StartResize(Direction = 1)
```

**BTN_ResizeTop — OnReleased:**
```
SET bIsResizing = False
SET ResizeDirection = 0
```

Tương tự cho 7 Button còn lại, chỉ đổi Direction:
```
BTN_ResizeTop    → Direction = 1
BTN_ResizeBottom → Direction = 2
BTN_ResizeLeft   → Direction = 3
BTN_ResizeRight  → Direction = 4
BTN_ResizeTL     → Direction = 5
BTN_ResizeTR     → Direction = 6
BTN_ResizeBL     → Direction = 7
BTN_ResizeBR     → Direction = 8
```

💡 Mẹo giảm lặp: tạo 1 Macro hoặc Function `BindResize(Direction)`
rồi gọi trong OnPressed. Nhưng vì UMG event binding hơi khác,
cách đơn giản nhất là copy-paste logic, chỉ đổi số Direction.

---

## BƯỚC 6 — Logic resize trong Event Tick (30-40 phút)

Đây là bước quan trọng nhất. Thêm vào Event Tick, SAU logic drag hiện có:

```
Event Tick:
  Branch bIsDragging → [drag logic hiện tại, giữ nguyên]

  Branch bIsResizing:              ← THÊM MỚI
    True →
      GET Mouse Position → chia Get Viewport Scale → CurrentMouse
      DeltaX = CurrentMouse.X - ResizeStartMousePos.X
      DeltaY = CurrentMouse.Y - ResizeStartMousePos.Y

      NewWidth  = ResizeStartSize.X
      NewHeight = ResizeStartSize.Y
      NewPosX   = ResizeStartPosition.X
      NewPosY   = ResizeStartPosition.Y

      === XỬ LÝ THEO HƯỚNG ===

      Branch ResizeDirection:

      --- Cạnh phải (4) hoặc góc phải (6, 8): ---
        NewWidth = ResizeStartSize.X + DeltaX

      --- Cạnh trái (3) hoặc góc trái (5, 7): ---
        NewWidth = ResizeStartSize.X - DeltaX
        NewPosX  = ResizeStartPosition.X + DeltaX

      --- Cạnh dưới (2) hoặc góc dưới (7, 8): ---
        NewHeight = ResizeStartSize.Y + DeltaY

      --- Cạnh trên (1) hoặc góc trên (5, 6): ---
        NewHeight = ResizeStartSize.Y - DeltaY
        NewPosY   = ResizeStartPosition.Y + DeltaY

      === CHI TIẾT TỪNG DIRECTION ===

      Direction 1 (Top):
        NewHeight = ResizeStartSize.Y - DeltaY
        NewPosY   = ResizeStartPosition.Y + DeltaY

      Direction 2 (Bottom):
        NewHeight = ResizeStartSize.Y + DeltaY

      Direction 3 (Left):
        NewWidth  = ResizeStartSize.X - DeltaX
        NewPosX   = ResizeStartPosition.X + DeltaX

      Direction 4 (Right):
        NewWidth  = ResizeStartSize.X + DeltaX

      Direction 5 (TopLeft):
        NewWidth  = ResizeStartSize.X - DeltaX
        NewPosX   = ResizeStartPosition.X + DeltaX
        NewHeight = ResizeStartSize.Y - DeltaY
        NewPosY   = ResizeStartPosition.Y + DeltaY

      Direction 6 (TopRight):
        NewWidth  = ResizeStartSize.X + DeltaX
        NewHeight = ResizeStartSize.Y - DeltaY
        NewPosY   = ResizeStartPosition.Y + DeltaY

      Direction 7 (BottomLeft):
        NewWidth  = ResizeStartSize.X - DeltaX
        NewPosX   = ResizeStartPosition.X + DeltaX
        NewHeight = ResizeStartSize.Y + DeltaY

      Direction 8 (BottomRight):
        NewWidth  = ResizeStartSize.X + DeltaX
        NewHeight = ResizeStartSize.Y + DeltaY

      === CLAMP MIN/MAX ===

      Clamp NewWidth:  Min = MinWindowSize.X,  Max = ViewportSize.X
      Clamp NewHeight: Min = MinWindowSize.Y,  Max = ViewportSize.Y

      ← Khi kéo cạnh trái/trên, nếu chạm min thì phải fix lại position:
      Branch Direction có Left (3, 5, 7):
        IF NewWidth == MinWindowSize.X:
          NewPosX = ResizeStartPosition.X + ResizeStartSize.X - MinWindowSize.X

      Branch Direction có Top (1, 5, 6):
        IF NewHeight == MinWindowSize.Y:
          NewPosY = ResizeStartPosition.Y + ResizeStartSize.Y - MinWindowSize.Y

      === ÁP DỤNG ===

      SET CurrentWindowSize = (NewWidth, NewHeight)
      SET InventoryPosition = (NewPosX, NewPosY)

      ← Cập nhật vị trí cửa sổ:
      Set Position In Viewport = InventoryPosition

      ← Cập nhật kích thước cửa sổ:
      (Cách cụ thể tùy widget dùng SizeBox hay Canvas Slot — xem Bước 7)

      ← Cập nhật vị trí 8 handle:
      Call UpdateResizeHandles
```

### Cách implement trong Blueprint (tránh 8 nhánh Branch):

Tạo Function `CalcResizeDelta(Direction, DeltaX, DeltaY)` trả về
struct {NewWidth, NewHeight, NewPosX, NewPosY}. Dùng Select node
hoặc Switch on Int (0-8) để gọn hơn.

Hoặc đơn giản nhất: dùng 4 biến Boolean:

```
bResizeRight  = Direction == 4 OR Direction == 6 OR Direction == 8
bResizeLeft   = Direction == 3 OR Direction == 5 OR Direction == 7
bResizeBottom = Direction == 2 OR Direction == 7 OR Direction == 8
bResizeTop    = Direction == 1 OR Direction == 5 OR Direction == 6

Branch bResizeRight: NewWidth  = Start.X + DeltaX
Branch bResizeLeft:  NewWidth  = Start.X - DeltaX,  NewPosX = Start.PosX + DeltaX
Branch bResizeBottom: NewHeight = Start.Y + DeltaY
Branch bResizeTop:    NewHeight = Start.Y - DeltaY,  NewPosY = Start.PosY + DeltaY
```

Cách này chỉ cần 4 Branch thay vì 8 — gọn hơn nhiều.

---

## BƯỚC 7 — Cập nhật kích thước cửa sổ thực tế (15 phút)

Cách cập nhật kích thước phụ thuộc cấu trúc widget hiện tại.
Cần xác nhận: kích thước 720×630 được set ở đâu?

**Khả năng 1: Canvas Panel Slot Size**
HB_TitleBar và BackgroundBlur_246 dùng Canvas Panel Slot.
→ Thay đổi kích thước bằng:
```
Slot(BackgroundBlur_246 as Canvas Panel Slot) → Set Size(NewWidth, NewHeight - TitleBarHeight)
Slot(HB_TitleBar as Canvas Panel Slot) → Set Size(NewWidth, TitleBarHeight)
```

**Khả năng 2: SizeBox wrapper**
Nếu có SizeBox bọc ngoài → Set Width Override + Set Height Override.

**Khả năng 3: Widget root kích thước cố định**
Trong Designer, widget root (Canvas Panel) có Size set = 720×630.
→ Không thay đổi runtime bằng Blueprint thông thường.
→ Cần wrap trong SizeBox hoặc dùng Set Render Transform Scale
   (nhưng Scale không phải resize thật).

⚠️ Cần Cuhoang xác nhận cách nào đang dùng để set size 720×630,
và cách Maximize thay đổi size (node nào?).

---

## BƯỚC 8 — Tích hợp với Drag + Maximize (10 phút)

**Drag:** Sau khi drag kết thúc (OnReleased), gọi UpdateResizeHandles.
(Hoặc: đã gọi trong Tick khi bIsDragging → tự động update)

**Maximize:**
- Khi Maximize: SET CurrentWindowSize = ViewportSize, ẩn 8 handle (Collapsed)
- Khi Restore: SET CurrentWindowSize = OriginalSize, hiện 8 handle (Visible),
  gọi UpdateResizeHandles

**Minimize:**
- Khi Minimize: ẩn 8 handle (Collapsed)
- Khi Restore từ Minimize: hiện 8 handle, gọi UpdateResizeHandles

**OriginalSize update:**
- Khi resize xong (OnReleased), SET OriginalSize = CurrentWindowSize
- Để Maximize → Restore trả về kích thước resize mới nhất (không phải 720×630 gốc)

---

## BƯỚC 9 — Cursor feedback (TÙY CHỌN, 15 phút)

Khi hover vào vùng resize, đổi hình con trỏ chuột:
- Cạnh trái/phải: ↔ (EW resize)
- Cạnh trên/dưới: ↕ (NS resize)
- Góc TL/BR: ↖↘ (NWSE resize)
- Góc TR/BL: ↗↙ (NESW resize)

Cách làm trong UMG:
- Mỗi Button handle: Override `On Mouse Enter` → Set Mouse Cursor (EMouseCursor)
- Override `On Mouse Leave` → Set Mouse Cursor = Default

Cursor enum trong UE5:
```
EMouseCursor::ResizeLeftRight    (cạnh trái/phải)
EMouseCursor::ResizeUpDown       (cạnh trên/dưới)
EMouseCursor::ResizeSouthEast    (góc BR/TL)
EMouseCursor::ResizeSouthWest    (góc BL/TR)
```

Hoặc đơn giản: bỏ qua bước này, thêm sau khi logic resize chạy ổn.

---

## BƯỚC 10 — Test (15 phút)

Checklist test:
- [ ] Kéo cạnh phải → cửa sổ rộng ra
- [ ] Kéo cạnh trái → cửa sổ rộng ra + dịch trái
- [ ] Kéo cạnh dưới → cửa sổ cao thêm
- [ ] Kéo cạnh trên → cửa sổ cao thêm + dịch lên
- [ ] Kéo góc dưới-phải → resize cả 2 chiều
- [ ] Kéo góc trên-trái → resize + dịch 2 chiều
- [ ] Co nhỏ hơn MinWindowSize → dừng lại, không nhỏ hơn
- [ ] Drag title bar sau resize → handle đi theo đúng
- [ ] Maximize → handle ẩn → Restore → handle hiện đúng vị trí
- [ ] Minimize → handle ẩn → Restore → handle hiện đúng
- [ ] Nội dung bên trong (grid, folder tree) co giãn theo kích thước mới

---

## Tóm tắt thời gian

| Bước | Nội dung | Thời gian |
|------|----------|-----------|
| 1 | Thêm biến | 5 phút |
| 2 | Thêm 8 Button vào layout | 20-30 phút |
| 3 | StartResize event | 10 phút |
| 4 | UpdateResizeHandles event | 15 phút |
| 5 | Bind OnPressed/OnReleased ×8 | 20 phút |
| 6 | Logic resize trong Event Tick | 30-40 phút |
| 7 | Cập nhật kích thước thực tế | 15 phút |
| 8 | Tích hợp Drag + Maximize | 10 phút |
| 9 | Cursor feedback (tùy chọn) | 15 phút |
| 10 | Test | 15 phút |
| **Tổng** | | **~2.5-3 giờ** |
