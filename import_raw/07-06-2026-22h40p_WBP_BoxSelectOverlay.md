# WBP_BoxSelectOverlay
**Phiên bản:** 1.0 | **Cập nhật:** 07/06/2026 — 22:40 ICT | Widget — khung chọn (rubber-band) cho Box Select (Sprint 2 T1)

---

## Mục đích
Vẽ khung hình chữ nhật bán trong suốt khi kéo chuột để chọn nhiều đồ cùng lúc. Chỉ là phần HIỂN THỊ — toàn bộ logic chọn nằm ở BP_FurnitureInputManager (Event Tick + OnLMBReleased + FinishBoxSelect). Xem BP_FurnitureInputManager.md v1.5.

---

## Cây widget
```
Canvas Panel
└── Border  (outer — ĐIỂM ĐIỀU KHIỂN VISIBILITY; Visibility = Hidden ban đầu)
    └── Border_Box  (con — Visibility = Visible; Brush Color = (0.3, 0.6, 1.0, 0.15) xanh trong suốt)
```
**⚠️ Lưu ý:** điều khiển ẩn/hiện ở **Border ngoài** (parent), KHÔNG ở Border_Box. Set vị trí + kích thước cũng trên Border ngoài (qua Canvas Slot của nó).

---

## Functions

### ShowBox
```
Border (outer) → Set Visibility = Visible
```

### HideBox
```
Border (outer) → Set Visibility = Hidden
```

### UpdateBox(StartPos : Vector2D, EndPos : Vector2D)
```
TopLeft  = Make Vector2D( Min(Start.X, End.X), Min(Start.Y, End.Y) )
BoxSize  = Make Vector2D( Abs(End.X - Start.X), Abs(End.Y - Start.Y) )
Border (outer) → Slot as Canvas Slot:
   → Set Position(TopLeft)
   → Set Size(BoxSize)
```
**Node đúng:** `Slot as Canvas Slot` (KHÔNG phải "Slot as Canvas Panel Slot"). Dùng Min cho góc trên-trái + Abs cho kích thước → kéo được mọi hướng (lên/xuống/trái/phải).

---

## Lifecycle (do BP_FurnitureInputManager quản)
- **BeginPlay (InputManager):** Create Widget → SET BoxSelectOverlayRef → Add to Viewport (Z-Order 100) → HideBox.
- **Event Tick:** khi vượt ngưỡng 5px → ShowBox + UpdateBox mỗi frame.
- **OnLMBReleased / FinishBoxSelect xong:** HideBox.
- **End Play (InputManager):** Remove from Parent → SET ref None (chống VRAM leak).

---

## Tọa độ — DPI (quan trọng)
- `Get Mouse Position on Viewport` (dùng cho StartPos/EndPos) trả tọa độ **logical** (đã chia DPI). Khung vẽ đúng theo chuột.
- Khi FinishBoxSelect so sánh vị trí ĐỒ với khung: `Project World To Screen` trả **pixel thô** → phải chia `Get Viewport Scale` (Widget Layout Library) để về cùng hệ logical. Nếu không → chọn lệch đồ.

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 07/06/2026 — 22:40 ICT | Tạo mới (Sprint 2 T1) — cây widget, ShowBox/HideBox/UpdateBox, lifecycle, lưu ý DPI |
