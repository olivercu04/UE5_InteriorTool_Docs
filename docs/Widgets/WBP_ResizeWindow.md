# WBP_ResizeWindow — Resize Window 8 hướng
**Phiên bản:** 1.0 | **Ngày:** 27/05/2026 — 10:30 ICT
**Widget:** WBP_FurnitureInventory | **Engine:** UE5.5.4

---

## Tổng quan

Tính năng cho phép kéo viền cửa sổ Inventory để thay đổi kích thước,
giống cửa sổ Windows. 8 hướng: 4 cạnh + 4 góc.

**Kích thước mặc định:** 512×1024
**Kích thước tối thiểu:** 400×300

---

## Variables (class variables — WBP_FurnitureInventory)

| Tên | Kiểu | Mặc định | Ghi chú |
|---|---|---|---|
| `bIsResizing` | Boolean | False | Đang kéo resize? |
| `ResizeDirection` | Integer | 0 | Hướng kéo (0=None, 1-8) |
| `ResizeStartMousePos` | Vector2D | (0,0) | Vị trí chuột lúc bắt đầu kéo |
| `ResizeStartSize` | Vector2D | (0,0) | Kích thước cửa sổ lúc bắt đầu kéo |
| `ResizeStartPosition` | Vector2D | (0,0) | Vị trí cửa sổ lúc bắt đầu kéo |

**Quy ước ResizeDirection:**
```
0 = None
1 = Top       2 = Bottom
3 = Left      4 = Right
5 = TopLeft   6 = TopRight
7 = BottomLeft  8 = BottomRight
```

---

## Layout — 8 Button resize handle

Thêm vào root Canvas Panel (cuối danh sách — Z Order cao nhất):

| Widget | Direction | Kích thước | Ghi chú |
|---|---|---|---|
| BTN_ResizeTop | 1 | 6px dày | Cạnh trên |
| BTN_ResizeBottom | 2 | 6px dày | Cạnh dưới |
| BTN_ResizeLeft | 3 | 6px rộng | Cạnh trái |
| BTN_ResizeRight | 4 | 6px rộng | Cạnh phải |
| BTN_ResizeTL | 5 | 12×12 | Góc trên-trái |
| BTN_ResizeTR | 6 | 12×12 | Góc trên-phải |
| BTN_ResizeBL | 7 | 12×12 | Góc dưới-trái |
| BTN_ResizeBR | 8 | 12×12 | Góc dưới-phải |

**Config mỗi Button:**
- Style Normal/Hovered/Pressed: Draw As = None, Tint Alpha = 0
- Visibility = Visible (nhận mouse event)
- Is Variable = True

---

## Event: StartResize (Custom Event)

**Input:** Direction : Integer

```
StartResize(Direction):
  SET bIsResizing = True
  SET ResizeDirection = Direction
  Get Mouse Position on Viewport → SET ResizeStartMousePos
  Slot as Canvas Slot (VerticalBox_0) → Get Position → SET ResizeStartPosition
  Slot as Canvas Slot (VerticalBox_0) → Get Size    → SET ResizeStartSize
```

**Bind OnPressed cho 8 button:**
```
On Pressed (BTN_ResizeXXX) → Call StartResize(Direction = [số tương ứng])
```

---

## Function: UpdateResizeHandles

Tính toán và set lại vị trí + kích thước 8 button dựa trên vị trí + size hiện tại của VerticalBox_0.

```
UpdateResizeHandles:
  Slot as Canvas Slot (VerticalBox_0) → Get Position → Break → PosX, PosY
  Slot as Canvas Slot (VerticalBox_0) → Get Size    → Break → W, H

  BTN_ResizeTL:     SetPos(PosX-3, PosY-3),       SetSize(12, 12)
  BTN_ResizeTR:     SetPos(PosX+W-9, PosY-3),     SetSize(12, 12)
  BTN_ResizeBL:     SetPos(PosX-3, PosY+H-9),     SetSize(12, 12)
  BTN_ResizeBR:     SetPos(PosX+W-9, PosY+H-9),   SetSize(12, 12)
  BTN_ResizeTop:    SetPos(PosX+9, PosY-3),        SetSize(W-18, 6)
  BTN_ResizeBottom: SetPos(PosX+9, PosY+H-3),      SetSize(W-18, 6)
  BTN_ResizeLeft:   SetPos(PosX-3, PosY+9),        SetSize(6, H-18)
  BTN_ResizeRight:  SetPos(PosX+W-3, PosY+9),      SetSize(6, H-18)
```

**Gọi UpdateResizeHandles từ:**
- Event Construct (cuối)
- Event Tick — cuối branch bIsDragging
- Event Tick — cuối branch bIsResizing (trong ResizeWindow)
- BTN_Maximize — cuối nhánh Restore

---

## Function: ResizeWindow

Toàn bộ logic resize. Được gọi từ Event Tick khi bIsResizing == True.

### Local Variables
| Tên | Kiểu |
|---|---|
| `NewW` | Float |
| `NewH` | Float |
| `NewX` | Float |
| `NewY` | Float |

### Flow

**Bước 1 — Check mouse button:**
```
Branch (Is Mouse Button Down — Left Mouse Button):
  False → SET bIsResizing = False, SET ResizeDirection = 0, Return
  True  → tiếp tục
```

**Bước 2 — Tính Delta:**
```
Get Mouse Position on Viewport → Break Vector2D → CurX, CurY
Break ResizeStartMousePos → StartMouseX, StartMouseY
DeltaX = CurX - StartMouseX
DeltaY = CurY - StartMouseY
```

**Bước 3 — Tính 4 boolean hướng:**
```
bRight  = (Dir==4) OR (Dir==6) OR (Dir==8)
bLeft   = (Dir==3) OR (Dir==5) OR (Dir==7)
bBottom = (Dir==2) OR (Dir==7) OR (Dir==8)
bTop    = (Dir==1) OR (Dir==5) OR (Dir==6)
```
Dùng OR node có Add pin — gộp 3 điều kiện vào 1 OR node.

**Bước 4 — Khởi tạo default (TRƯỚC Sequence):**
```
Break ResizeStartSize     → StartW, StartH
Break ResizeStartPosition → StartX, StartY

SET NewW = StartW
SET NewH = StartH
SET NewX = StartX
SET NewY = StartY
```

**Bước 5 — Sequence (Then 0→7):**
```
Then 0 (bRight):  True → SET NewW = StartW + DeltaX       | False → (trống)
Then 1 (bLeft):   True → SET NewW = StartW - DeltaX        | False → (trống)
                         SET NewX = StartX + DeltaX
Then 2 (bBottom): True → SET NewH = StartH + DeltaY       | False → (trống)
Then 3 (bTop):    True → SET NewH = StartH - DeltaY        | False → (trống)
                         SET NewY = StartY + DeltaY
Then 4:  SET NewW = MAX(NewW, 400)
Then 5:  SET NewH = MAX(NewH, 300)
Then 6:  Branch (bLeft AND NewW==400):
           True → SET NewX = StartX + StartW - 400
Then 7:  Branch (bTop AND NewH==300):
           True → SET NewY = StartY + StartH - 300
```

⚠️ **False branch của Then 0-3 để TRỐNG** — default đã SET trước Sequence.
Nếu False branch SET lại giá trị sẽ overwrite kết quả của Then trước đó.

**Bước 6 — Apply:**
```
Slot as Canvas Slot (VerticalBox_0) → Set Size     (Make Vector2D: NewW, NewH)
Slot as Canvas Slot (VerticalBox_0) → Set Position (Make Vector2D: NewX, NewY)
SET InventoryPosition = Make Vector2D(NewX, NewY)
Call UpdateResizeHandles
```

---

## Event Tick (cập nhật)

```
Event Tick:
  Branch bIsDragging:
    True →
      GET Mouse Position on Viewport → MousePos
      NewPos = MousePos - DragOffset
      Slot as Canvas Slot (VerticalBox_0) → Set Position (NewPos)
      SET InventoryPosition = NewPos
      Call UpdateResizeHandles
    False ↓

  Branch bIsResizing:
    True → Call ResizeWindow
    False → (trống)
```

---

## BTN_TitleBar — Drag (cập nhật)

```
OnPressed:
  SET IsDragging = True
  GET Mouse Position on Viewport → MousePos
  Slot as Canvas Slot (VerticalBox_0) → Get Position → CurrentPos
  SET DragOffset = MousePos - CurrentPos   ← đọc từ Canvas Slot

OnReleased:
  SET IsDragging = False
```

⚠️ Drag đã đổi từ `Set Position in Viewport (self)` sang
`Slot as Canvas Slot (VerticalBox_0) → Set Position` để đồng bộ
với hệ tọa độ của resize.

---

## Maximize / Minimize (cập nhật)

**BTN_Maximize — Nhánh True (Maximize):**
```
... [code maximize] ...
Set Visibility (8 BTN_Resize) = Collapsed
```

**BTN_Maximize — Nhánh False (Restore):**
```
... [code restore] ...
Set Visibility (8 BTN_Resize) = Visible
Call UpdateResizeHandles
```

**BTN_Minimize:**
```
... [code minimize] ...
Set Visibility (8 BTN_Resize) = Collapsed
```

**BTN_MinimizedIcon (restore từ minimize):**
```
... [code restore] ...
Set Visibility (8 BTN_Resize) = Visible
Call UpdateResizeHandles
```

**OnReleased (8 BTN_Resize) — cập nhật OriginalSize:**
```
On Released (BTN_ResizeXXX):
  ← Không cần SET bIsResizing = False (ResizeWindow tự check mouse button)
  Slot as Canvas Slot (VerticalBox_0) → Get Size → SET OriginalSize
```

---

## Key Learnings

- **"Slot as Canvas Panel Slot"** → tên đúng trong UE5 là **"Slot as Canvas Slot"**
- **Drag và Resize phải dùng cùng hệ tọa độ** → đều dùng Canvas Slot position của VerticalBox_0. Nếu drag dùng `Set Position in Viewport (self)` và resize dùng Canvas Slot → window nhảy khỏi cursor khi drag sau resize.
- **False branch trong Sequence phải để trống** → nếu False SET lại giá trị sẽ overwrite kết quả của Then trước đó (ví dụ: bLeft False SET NewW = StartW → overwrite NewW đã tính bởi bRight True).
- **Default value phải SET trước Sequence** → SET NewW/NewH/NewX/NewY = Start values trước khi Sequence chạy. Sequence chỉ override khi cần.
- **Is Mouse Button Down thay OnReleased** → Button resize 6px quá nhỏ, mouse rời button ngay khi kéo → OnReleased fire sớm → resize bị tắt. Dùng `Is Mouse Button Down (Left)` trong ResizeWindow để check.
- **Slot as Canvas Slot Get Size trả về (0,0)** nếu chưa Set Size explicit → cần gọi Set Size trong Event Construct với kích thước mặc định (512, 1024).

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 27/05/2026 — 10:30 ICT | Khởi tạo — 8 hướng resize hoàn chỉnh |
