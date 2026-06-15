# Kế hoạch Multi-Select → Group Mesh → Combo Mesh
**Phiên bản:** 1.0 | **Ngày:** 26/05/2026 — 08:51 ICT
**Project:** Lighting_Mnger (UE5.5.4) — UE5 Interior Design Tool

---

## Tổng quan

Mục tiêu: xây dựng hệ thống cho phép người dùng **chọn nhiều đồ nội thất → gộp thành nhóm → lưu nhóm thành combo tái sử dụng**. Thiết kế cho người dùng bình thường (không có kiến thức chuyên môn), ưu tiên thao tác nhanh, trực quan, ít bước nhất.

**4 giai đoạn:**
1. Multi-select — chọn nhiều đồ cùng lúc
2. Group / Ungroup — gộp, tách, group lồng group
3. Combo Mesh — lưu group thành template tái sử dụng trong kho
4. Material Edit v1.2 — chỉnh sửa vật liệu nâng cao (Color, Roughness, Metallic)

---

## ═══════════════════════════════════════════════
## GIAI ĐOẠN 1 — MULTI-SELECT
## ═══════════════════════════════════════════════

### 1.1 User Story

> "Tao muốn chọn cái bàn, 4 cái ghế xung quanh, rồi kéo tất cả sang góc khác 1 lần."
> "Tao muốn xóa 5 cái cây trang trí cùng lúc thay vì xóa từng cái."

### 1.2 Cách chọn nhiều đồ (3 cách)

**Cách 1: Ctrl + Click (thêm/bỏ từng cái)**
- Click thường = chọn 1, bỏ chọn tất cả cái cũ (giữ nguyên như hiện tại)
- Ctrl + Click = thêm vào nhóm đang chọn (hoặc bỏ nếu đã chọn)
- Giống cách chọn file trong Windows Explorer

**Cách 2: Kéo khung chọn (Box Select)**
- Giữ chuột trái + kéo trên vùng trống = vẽ hình chữ nhật mờ xanh
- Tất cả đồ nằm trong khung = được chọn
- Ctrl + kéo khung = thêm vào nhóm đang chọn
- Giống cách chọn nhiều icon trên Desktop

**Cách 3: Ctrl + A (chọn tất cả)**
- Chọn tất cả đồ nội thất trong scene

### 1.3 Hiển thị khi chọn nhiều đồ

**Outline:**
- 1 đồ chọn: outline xanh dương (giữ nguyên hiện tại, Stencil = 255)
- Nhiều đồ chọn: tất cả đều có outline xanh dương
- Đồ được chọn cuối cùng (Primary): outline sáng hơn hoặc dày hơn — đây là "điểm neo" để Align/Distribute

**Thanh thông tin Selection Info (hiện trên toolbar):**
```
┌─────────────────────────────────────────────────────┐
│ ✦ 5 vật thể đã chọn  │  [Nhóm ▼]  │  [Xóa tất cả] │
└─────────────────────────────────────────────────────┘
```
- Hiện số lượng đang chọn
- Nút "Nhóm" (tạo group nhanh — Giai đoạn 2)
- Nút "Xóa tất cả" (xóa hết đồ đang chọn)
- Ẩn đi khi chỉ chọn 1 hoặc 0

### 1.4 Thao tác với nhiều đồ đã chọn

| Thao tác | Hành vi |
|----------|---------|
| Move (W) | Kéo gizmo → tất cả đồ di chuyển cùng hướng, giữ khoảng cách |
| Rotate (E) | Xoay quanh điểm trung tâm của nhóm (center of bounding box) |
| Scale (R) | Scale đều quanh center, giữ tỉ lệ khoảng cách |
| Delete | Xóa tất cả đồ đang chọn |
| Copy (Ctrl+C) | Copy tất cả đồ đang chọn (giữ vị trí tương đối) |
| Paste (Ctrl+V) | Dán tất cả tại con trỏ chuột |
| Duplicate (Ctrl+D) | Nhân đôi tại chỗ, offset nhẹ |
| Nudge (Arrow keys) | Di chuyển tất cả |
| Esc | Bỏ chọn tất cả |

### 1.5 Gizmo khi multi-select

- Gizmo hiện tại center of group (trung bình vị trí tất cả đồ đang chọn)
- Vẫn dùng RuntimeTransformer — SelectActor cho Primary actor, còn lại move theo delta
- Hoặc: spawn 1 "pivot actor" tạm ở center, gắn gizmo vào đó

### 1.6 Tính năng bổ sung mà bạn có thể chưa biết

**① Select Similar (chọn đồ giống nhau)**
- Click phải vào 1 ghế → "Chọn tất cả ghế giống" → chọn tất cả ghế cùng MeshPath
- Rất hữu ích: "tao muốn đổi vật liệu tất cả ghế trong phòng cùng lúc"

**② Invert Selection (đảo ngược)**
- Ctrl + I = bỏ chọn cái đang chọn, chọn cái chưa chọn
- Ví dụ: chọn 1 cái bàn → Ctrl+I → chọn tất cả trừ bàn

**③ Lock (khóa đồ)**
- Click phải → "Khóa" hoặc icon ổ khóa trên toolbar
- Đồ bị khóa: không thể chọn, move, delete
- Dùng khi đã bày xong 1 khu vực, không muốn lỡ tay di chuyển
- Icon ổ khóa nhỏ hiện góc đồ bị khóa

### 1.7 Right-Click Context Menu (Menu chuột phải) ← TÍNH NĂNG MỚI

Hiện tại tool chưa có menu chuột phải. Đây là tính năng chuẩn của mọi phần mềm thiết kế.

**Click phải vào 1 đồ:**
```
┌──────────────────────┐
│  ✂ Cắt         Ctrl+X │
│  📋 Sao chép    Ctrl+C │
│  📄 Nhân đôi    Ctrl+D │
│  ──────────────────── │
│  🗑 Xóa         Delete │
│  🔒 Khóa               │
│  ──────────────────── │
│  🔍 Chọn tất cả giống  │
│  📏 Thông tin          │
│  🎨 Đổi vật liệu      │
│  ↔ Thay thế            │
│  ──────────────────── │
│  📐 Nhóm         Ctrl+G│  ← Giai đoạn 2
│  💾 Lưu combo          │  ← Giai đoạn 3
└──────────────────────┘
```

**Click phải vào vùng trống:**
```
┌──────────────────────┐
│  📋 Dán          Ctrl+V │
│  ↩ Hoàn tác     Alt+Z  │
│  ↪ Làm lại  Shift+Alt+Z│
│  ──────────────────── │
│  ✦ Chọn tất cả  Ctrl+A │
└──────────────────────┘
```

### 1.8 Shortcut tổng hợp (cập nhật)

| Phím | Chức năng | Ghi chú |
|------|-----------|---------|
| Click | Chọn 1, bỏ cũ | Giữ nguyên |
| Ctrl + Click | Thêm/bỏ chọn | MỚI |
| Kéo khung | Box select | MỚI |
| Ctrl + A | Chọn tất cả | MỚI |
| Ctrl + I | Đảo chọn | MỚI |
| Ctrl + X | Cắt | MỚI |
| Ctrl + G | Tạo group | Giai đoạn 2 |
| Ctrl + Shift + G | Tách group | Giai đoạn 2 |
| Esc | Bỏ chọn tất cả | Giữ nguyên |

---

## ═══════════════════════════════════════════════
## GIAI ĐOẠN 2 — GROUP / UNGROUP
## ═══════════════════════════════════════════════

### 2.1 User Story

> "Tao đã bày xong bộ bàn ăn (1 bàn + 6 ghế). Giờ muốn kéo cả bộ sang góc khác mà không phải chọn lại 7 cái."
> "Tao muốn mở group ra để chỉnh 1 cái ghế, xong đóng lại."

### 2.2 Tạo Group

- Chọn nhiều đồ (cách 1/2/3) → Ctrl+G hoặc nút "Nhóm" trên thanh thông tin hoặc chuột phải → "Nhóm"
- Hộp thoại nhỏ hiện ra: "Đặt tên nhóm: [Bộ bàn ăn 6 ghế]" (có tên mặc định "Nhóm 1")
- OK → tất cả đồ đã chọn gộp thành 1 group

### 2.3 Hiển thị Group

**Khi chưa chọn:**
- Không hiện gì đặc biệt — đồ trông bình thường

**Khi click vào 1 đồ trong group:**
- Tất cả đồ trong group highlight outline xanh
- Bounding box mờ bao quanh cả group (đường viền nét đứt mờ)
- Thanh thông tin: "📦 Bộ bàn ăn 6 ghế (7 vật thể)"
- Gizmo hiện ở center group

**Icon nhóm:**
- Góc trên-trái của bounding box hiện icon 📦 nhỏ + tên group
- Chỉ hiện khi đang chọn group đó

### 2.4 Thao tác Group

| Thao tác | Click 1 lần (group mode) | Double-click (edit mode) |
|----------|--------------------------|--------------------------|
| Ý nghĩa | Chọn cả group | Vào trong group để chỉnh từng đồ |
| Move/Rotate/Scale | Cả group di chuyển | Chỉ đồ đang chọn bên trong |
| Outline | Tất cả đồ trong group | Chỉ đồ đang chỉnh |
| Thoát | Click vùng trống / Esc | Esc (ra group mode) hoặc click ngoài group |

### 2.5 Edit Mode (vào trong group) ← TÍNH NĂNG QUAN TRỌNG

Khi double-click vào group:
- Tất cả đồ BÊN NGOÀI group bị mờ đi (opacity giảm ~40%)
- Chỉ đồ trong group hiển thị rõ
- Có thể chọn, move, rotate, scale, delete, thay material từng đồ bên trong
- Thanh thông tin: "✏️ Đang chỉnh: Bộ bàn ăn 6 ghế  [Thoát nhóm]"
- Nút "Thoát nhóm" hoặc Esc = quay về bình thường

Ví dụ thực tế: Double-click vào bộ bàn ăn → kéo 1 ghế ra xa hơn → đổi vật liệu ghế → Esc → cả bộ lại hoạt động như 1 nhóm.

### 2.6 Ungroup (tách group)

- Chọn group → Ctrl+Shift+G hoặc chuột phải → "Tách nhóm"
- Tất cả đồ trở thành đồ riêng lẻ, group biến mất
- Hỏi xác nhận nếu group có group con: "Nhóm này chứa nhóm con. Tách tất cả hay chỉ tách lớp ngoài?"
  - "Tách lớp ngoài" → group con vẫn giữ nguyên
  - "Tách tất cả" → tất cả thành đồ riêng lẻ

### 2.7 Group lồng Group (Nested Group)

Ví dụ thực tế:
```
📦 Phòng khách
├── 📦 Bộ sofa
│   ├── Sofa 3 chỗ
│   ├── Sofa 1 chỗ (trái)
│   └── Sofa 1 chỗ (phải)
├── 📦 Kệ TV
│   ├── Kệ TV
│   ├── TV 55 inch
│   └── Soundbar
├── Bàn trà
├── Thảm
└── Đèn cây
```

- Click → chọn "Phòng khách" (toàn bộ)
- Double-click → vào trong "Phòng khách" → thấy "Bộ sofa", "Kệ TV", Bàn trà, Thảm, Đèn cây
- Double-click "Bộ sofa" → vào trong → thấy 3 sofa riêng lẻ
- Esc → quay về "Phòng khách"
- Esc lần nữa → quay về bình thường

### 2.8 Tính năng bổ sung

**④ Align & Distribute (Căn chỉnh & Phân bố đều) ← RẤT HỮU ÍCH**

Khi chọn nhiều đồ (multi-select hoặc trong edit mode group):

```
Thanh Align hiện thêm trên toolbar:
┌───────────────────────────────────────────────┐
│  [⫷] [⫿] [⫸]  │  [⫻] [⫼] [⫽]  │  [⫶ Phân bố đều] │
│  Trái Giữa Phải │  Trên Giữa Dưới │                   │
└───────────────────────────────────────────────┘
```

- Trái/Giữa/Phải: căn theo bounding box của Primary (đồ chọn cuối)
- Phân bố đều: chia khoảng cách bằng nhau giữa các đồ
- Ví dụ: chọn 6 ghế → "Phân bố đều" → 6 ghế cách đều nhau thành hàng

**⑤ Spacing Tool (đặt khoảng cách chính xác)**
- Chọn 2+ đồ → nhập khoảng cách: "10cm" → tất cả cách nhau đúng 10cm
- Dùng cho: đặt 6 ghế quanh bàn, mỗi ghế cách bàn 5cm

**⑥ Array / Pattern (nhân đôi theo hàng/lưới) ← TIẾT KIỆM THỜI GIAN**
- Chọn 1 đồ → "Tạo hàng" → nhập: số lượng = 6, khoảng cách = 80cm, hướng = ngang
- Kết quả: 6 bản sao xếp hàng đều
- "Tạo lưới" → nhập: hàng = 3, cột = 4, khoảng cách = 100cm
- Dùng cho: bày bàn nhà hàng, ghế hội trường
- Sau khi tạo → tự động gộp thành group

**⑦ Mirror Group (phản chiếu)**
- Chọn group → chuột phải → "Phản chiếu ngang/dọc"
- Tạo bản sao đối xứng qua trục
- Dùng cho: thiết kế đối xứng (2 bên phòng giống nhau)

---

## ═══════════════════════════════════════════════
## GIAI ĐOẠN 3 — COMBO MESH
## ═══════════════════════════════════════════════

### 3.1 User Story

> "Bộ bàn ăn này tao bày đẹp rồi, muốn lưu lại để dùng cho dự án khác."
> "Tao muốn kéo 1 bộ phòng khách có sẵn ra, không muốn tự bày từng cái."

### 3.2 Lưu Group thành Combo

- Chọn group → chuột phải → "💾 Lưu thành Combo"
- Hoặc: trong edit mode → nút "Lưu Combo" trên thanh thông tin

**Hộp thoại lưu Combo:**
```
┌────────────────────────────────────────┐
│        LƯU COMBO MỚI                  │
│                                        │
│  Tên:    [Bộ bàn ăn Scandinavian    ] │
│                                        │
│  Phân loại:  [Phòng ăn         ▼]     │
│  Phong cách: [Scandinavian     ▼]     │
│  Tags:       [bàn ăn, 6 ghế, gỗ sồi] │
│                                        │
│  ☑ Giữ vật liệu đã chỉnh             │
│  ☑ Giữ tỉ lệ đã scale                │
│                                        │
│  Preview:                              │
│  ┌──────────────┐                      │
│  │   [ảnh 3D    │                      │
│  │    auto-gen] │                      │
│  └──────────────┘                      │
│                                        │
│       [Hủy]        [Lưu]              │
└────────────────────────────────────────┘
```

### 3.3 Combo trong Inventory

**Tab mới hoặc Category mới trong WBP_FurnitureInventory:**

```
[Đồ nội thất] [Vật liệu] [🧩 Combo]    ← Tab thứ 3
```

Hoặc đơn giản hơn: Combo là 1 category đặc biệt trong tab "Đồ nội thất":
```
Folder tree bên trái:
├── Tất cả
├── Bàn
├── Ghế
├── Sofa
├── ...
├── ─────────
├── ⭐ Yêu thích
├── 🕐 Gần đây
└── 🧩 Combo        ← category đặc biệt
    ├── Phòng khách
    ├── Phòng ăn
    ├── Phòng ngủ
    └── Tự tạo
```

**Card hiển thị Combo:**
```
┌──────────────────┐
│  [ảnh 3D combo]  │
│                  │
│  Bộ bàn ăn 6 ghế│
│  7 vật thể       │
│  ⭐ ℹ            │
└──────────────────┘
```

### 3.4 Spawn Combo vào Scene

- Click card combo hoặc kéo thả vào viewport
- Tất cả đồ trong combo spawn cùng lúc, giữ đúng vị trí tương đối
- Spawn tại vị trí con trỏ (center của combo = con trỏ)
- Tự động tạo group với tên combo
- Ghost preview hiện đủ cả bộ khi đang kéo

### 3.5 Combo có sẵn từ nhà cung cấp (tầm nhìn kinh doanh)

**Đây là tính năng tạo revenue:**

- Nhà sản xuất nội thất upload combo vào library
- User browse combo theo phong cách/phòng/ngân sách
- Click 1 lần → cả bộ nội thất spawn vào phòng
- User chỉ cần chỉnh vị trí + đổi vật liệu nếu muốn

**Combo variants (biến thể):**
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  [Phòng khách    │  │  [Phòng khách    │  │  [Phòng khách    │
│   Modern]        │  │   Scandinavian]  │  │   Industrial]    │
│                  │  │                  │  │                  │
│  Cùng layout     │  │  Cùng layout     │  │  Cùng layout     │
│  Vật liệu khác  │  │  Vật liệu khác  │  │  Vật liệu khác  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

Cùng 1 bố cục (bàn + ghế + sofa + kệ TV), nhưng đổi vật liệu theo phong cách. User xem 3 biến thể → chọn cái ưng → kéo vào scene. Đây là cách Coohom và nhiều tool chuyên nghiệp hoạt động.

### 3.6 Tính năng bổ sung Combo

**⑧ Combo Thumbnail tự động**
- Khi lưu combo → SceneCapture2D chụp từ góc perspective → tạo thumbnail tự động
- Giống pipeline thumbnail material đã setup (LV_ThumbnailStudio)
- Camera orbit quanh combo center, góc 30° từ trên xuống

**⑨ Edit Combo sau khi spawn**
- Combo spawn vào scene = 1 group bình thường
- User tự do chỉnh sửa (thêm/xóa/đổi đồ bên trong)
- Không "link" về template gốc — mỗi instance độc lập
- Nếu muốn update template → lưu lại combo mới

**⑩ Share Combo (tầm nhìn cloud — sau Supabase)**
- Lưu combo lên server → chia sẻ link cho khách hàng
- Khách click link → mở tool với combo đã bày sẵn
- Đây là use case kinh doanh chính

---

## ═══════════════════════════════════════════════
## GIAI ĐOẠN 4 — MATERIAL EDIT v1.2
## ═══════════════════════════════════════════════

### 4.1 User Story

> "Vải sofa này gần ưng rồi nhưng muốn đậm hơn 1 chút."
> "Gỗ này đẹp nhưng muốn bóng hơn."

### 4.2 UI — Material Edit Panel

Khi chọn 1 mesh → tab Material → chọn slot → bên dưới grid vật liệu hiện thêm panel chỉnh sửa:

```
┌─ Chỉnh sửa vật liệu ─────────────────────┐
│                                             │
│  Màu tông:  [──●────────] ← Color tint     │
│             🎨 [    màu     ]               │
│                                             │
│  Độ nhám:   [────────●──] 0.7   ← Roughness│
│             (mờ) ←————→ (bóng)              │
│                                             │
│  Độ kim loại: [●────────] 0.1   ← Metallic │
│             (phi kim) ←——→ (kim loại)       │
│                                             │
│  ☐ UV Scale:  [───●─────] 1.0              │
│  ☐ UV Xoay:   [●────────] 0°               │
│                                             │
│       [Đặt lại mặc định]                   │
└─────────────────────────────────────────────┘
```

**Nguyên tắc UX:**
- Dùng tên tiếng Việt dễ hiểu: "Độ nhám" thay vì "Roughness"
- Mỗi slider có text giải thích 2 đầu: "(mờ) ←→ (bóng)"
- Thay đổi = preview live ngay trên mesh (đã có MID từ v1.1)
- Nút "Đặt lại mặc định" = quay về thông số gốc của material
- UV Scale/Xoay ẩn mặc định (checkbox mở ra) — người dùng thường không cần

### 4.3 Áp dụng cho multi-select / group

- Nếu chọn nhiều mesh → chỉnh slider → apply cho tất cả mesh đang chọn (cùng slot index)
- Nếu chọn group → vào edit mode → chỉnh từng mesh bên trong
- Hoặc: chọn group → chỉnh = apply cho tất cả mesh trong group (cùng slot)

### 4.4 Save/Load Material Params

- Serialize param values vào MaterialParams (đã có placeholder từ v1.1)
- Format: JSON per slot, ví dụ: `{"Tint":[0.8,0.6,0.4,1],"Roughness":0.7,"Metallic":0.1}`
- EMS tự save/load qua SaveGame property

---

## ═══════════════════════════════════════════════
## TÍNH NĂNG BỔ SUNG (ĐỀ XUẤT THÊM)
## ═══════════════════════════════════════════════

### ⑪ Scene Outliner (Danh sách đồ trong scene)

Panel bên phải hiện cây thư mục tất cả đồ trong scene:
```
┌─ Scene ──────────────────────┐
│ 🔍 [Tìm kiếm...]            │
│                              │
│ ▼ 📦 Phòng khách             │
│   ├── ▼ 📦 Bộ sofa           │
│   │   ├── Sofa 3 chỗ         │
│   │   ├── Sofa 1 chỗ (trái)  │
│   │   └── Sofa 1 chỗ (phải)  │
│   ├── Bàn trà                │
│   └── Đèn cây                │
│ ▶ 📦 Phòng ăn                │
│ 🔒 Tủ kệ góc                 │
│ Cây xanh                     │
└──────────────────────────────┘
```

- Click tên = chọn đồ trong scene (camera focus vào)
- Kéo thả trong danh sách = đổi group
- Icon 🔒 = đồ bị khóa
- Icon 👁 (toggle ẩn/hiện) = ẩn tạm đồ (không xóa)

### ⑫ Ẩn/Hiện tạm thời (Toggle Visibility)

- Chuột phải → "Ẩn tạm" hoặc icon 👁 trong Scene Outliner
- Đồ biến mất khỏi viewport nhưng vẫn tồn tại
- Dùng khi: cần nhìn rõ đồ bị che khuất (ví dụ: thảm dưới bàn)
- "Hiện tất cả" = bật lại

### ⑬ Focus on Selected (phím F)

- Chọn đồ → nhấn F → camera zoom + xoay về đồ đó
- Chọn group → F → camera zoom ra vừa đủ thấy cả group
- Đã có trong roadmap nhưng chưa làm — nên làm cùng multi-select

### ⑭ Snap giữa các đồ (Smart Snap)

Khi kéo đồ gần đồ khác:
- Hiện đường dẫn mờ (guideline) khi cạnh 2 đồ thẳng hàng
- Snap tự động khi gần (trong khoảng 5cm)
- Giống Figma: kéo element → hiện đường hồng khi align với element khác
- Rất hữu ích cho người dùng bình thường — không cần nhập số chính xác

---

## ═══════════════════════════════════════════════
## KIẾN TRÚC KỸ THUẬT (TÓM TẮT)
## ═══════════════════════════════════════════════

### Thay đổi chính — single-select → multi-select

**Hiện tại:**
```
BP_FurnitureInputManager:
  SelectedFurnitureActor : BP_FurnitureActor (1 biến đơn)
```

**Sau khi refactor:**
```
BP_FurnitureInputManager:
  SelectedActors         : Array of BP_FurnitureActor (mảng)
  PrimarySelectedActor   : BP_FurnitureActor (cái chọn cuối, dùng cho Align)
```

### Actor mới — BP_FurnitureGroup

```
BP_FurnitureGroup (Actor):
  GroupName        : String (tên group)
  GroupID          : String (unique ID)
  ChildActors      : Array of Actor (BP_FurnitureActor hoặc BP_FurnitureGroup)
  ParentGroup      : BP_FurnitureGroup (None nếu top-level) — Soft Ref
  bIsLocked        : Boolean
```

- KHÔNG dùng UE5 Attachment (AttachToActor) → quá rigid
- Dùng logical grouping: group chỉ lưu danh sách children, transform thủ công qua delta
- Khi move group: tính delta → ForEach child → AddWorldOffset(delta)

### Data mới cho Undo/Redo

```
S_SceneSnapshot (mở rộng):
  Meshes             : Array of S_FurniturePlacement (giữ nguyên)
  Groups             : Array of S_GroupData (MỚI)
  SelectedMeshIndices : Array of Integer (MỚI — thay SelectedMeshIndex đơn)
```

```
S_GroupData:
  GroupID      : String
  GroupName    : String
  ChildIDs     : Array of String (UniqueID của children)
  ParentGroupID : String (rỗng nếu top-level)
```

### Data mới cho Combo

```
DT_ComboMeshCatalog (DataTable mới):
  ComboName    : String
  Category     : String
  Style        : String
  Tags         : String (pipe-separated)
  Thumbnail    : Soft Object Reference Texture2D
  ComboData    : String (JSON — mảng S_FurniturePlacement + S_GroupData serialized)
```

### Nguyên tắc R1-R5 áp dụng

- R1: Async load combo data, không blocking
- R2: Widget không giữ hard ref đến Group Actor
- R3: Widget nhận GroupID + GroupName (struct nhẹ)
- R4: Event Destruct clear mọi reference
- R5: Lưu GroupID, không lưu actor path

---

## ═══════════════════════════════════════════════
## THỨ TỰ TRIỂN KHAI CHI TIẾT
## ═══════════════════════════════════════════════

### Sprint 1 — Multi-select cơ bản (5-7 ngày)
- [ ] Đổi SelectedFurnitureActor → SelectedActors array
- [ ] Ctrl+Click thêm/bỏ
- [ ] Multi outline (Custom Depth cho mảng)
- [ ] Move/Delete/Copy/Nudge nhiều đồ
- [ ] Thanh thông tin "N vật thể đã chọn"
- [ ] Undo/Redo cho multi-select

### Sprint 2 — Box Select + Context Menu (3-5 ngày)
- [ ] Box select (kéo khung chọn)
- [ ] Right-click context menu
- [ ] Ctrl+A chọn tất cả
- [ ] Select Similar

### Sprint 3 — Group cơ bản (5-7 ngày)
- [ ] BP_FurnitureGroup actor
- [ ] Ctrl+G tạo group, Ctrl+Shift+G tách group
- [ ] Click group = chọn cả group
- [ ] Move/Rotate/Scale group
- [ ] Group visual (bounding box nét đứt)
- [ ] Undo/Redo cho group
- [ ] Save/Load group (EMS)

### Sprint 4 — Edit Mode + Nested Group (5-7 ngày)
- [ ] Double-click vào group mode
- [ ] Dimming đồ bên ngoài group
- [ ] Nested group (group trong group)
- [ ] Ungroup options (tách lớp ngoài / tách tất cả)

### Sprint 5 — Combo Mesh (5-7 ngày)
- [ ] Lưu group thành combo (DataTable/JSON)
- [ ] Tab/Category "Combo" trong Inventory
- [ ] Spawn combo vào scene
- [ ] Auto-generate thumbnail cho combo
- [ ] Ghost preview khi kéo combo

### Sprint 6 — Polish UX (3-5 ngày)
- [ ] Lock/Unlock
- [ ] Align & Distribute
- [ ] Focus on Selected (F)
- [ ] Scene Outliner cơ bản
- [ ] Toggle Visibility (ẩn/hiện tạm)

### Sprint 7 — Material Edit v1.2 (3-5 ngày)
- [ ] Color Picker (Tint)
- [ ] Roughness / Metallic slider
- [ ] UV Scale / Rotation (optional)
- [ ] Serialize MaterialParams (JSON)
- [ ] Apply cho multi-select

---

## ═══════════════════════════════════════════════
## TỔNG THỜI GIAN ƯỚC TÍNH
## ═══════════════════════════════════════════════

| Sprint | Nội dung | Thời gian |
|--------|----------|-----------|
| 1 | Multi-select cơ bản | 5-7 ngày |
| 2 | Box Select + Context Menu | 3-5 ngày |
| 3 | Group cơ bản | 5-7 ngày |
| 4 | Edit Mode + Nested | 5-7 ngày |
| 5 | Combo Mesh | 5-7 ngày |
| 6 | Polish UX | 3-5 ngày |
| 7 | Material Edit v1.2 | 3-5 ngày |
| **Tổng** | | **~30-43 ngày** |

Ghi chú: thời gian ước tính dựa trên tốc độ làm việc các sprint trước (~1 tính năng phức tạp / tuần). Có thể nhanh hơn nếu ít bug, chậm hơn nếu gặp vấn đề kiến trúc.

---

## ═══════════════════════════════════════════════
## CÂU HỎI CẦN THẢO LUẬN
## ═══════════════════════════════════════════════

1. **Rotate multi-select:** xoay quanh center nhóm hay quanh Primary? Phần mềm khác thường xoay quanh center.
2. **Group pivot:** center tự động hay cho user chọn? Đề xuất: center tự động, cho phép kéo pivot sau (pro feature).
3. **Combo lưu ở đâu:** DataTable trong project (dùng riêng) hay file JSON bên ngoài (dễ share)? Đề xuất: DataTable trước, migrate sang JSON/Supabase khi làm cloud.
4. **Context menu:** dùng UMG Widget hay dùng Slate? UMG dễ hơn cho Blueprint.
5. **Box select:** kéo ở đâu? Trên viewport (cần phân biệt với kéo gizmo) — chỉ active khi ở Select mode (Q).
6. **Scene Outliner:** làm cùng sprint nào? Đề xuất: sprint 6 (polish), vì cần Group system xong trước.
