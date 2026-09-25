# Design — Nguyên tắc thiết kế UI/UX
**Nguồn:** `import_raw/Design.md`
**Phiên bản:** 1.2 | **Cập nhật:** 25/09/2026 — đính chính "Đối tượng người dùng" theo quyết định người dùng đích (xem đầu mục đó).
**Phiên bản:** 1.1 | **Dự án:** Lighting_Mnger | **Cập nhật:** 20/05/2026 — 16:00 ICT

---

## Đối tượng người dùng

> ⚠ **Đính chính 25/09/2026 (quyết định cuhoang):** người dùng đích = **người có kỹ năng thiết kế và tư vấn nội thất tốt, dễ tiếp cận công nghệ** — không phải người mù công nghệ, không phải nhân viên FOFF. Hệ quả: chữ trên giao diện nói bằng ngôn ngữ nghề nội thất (không bằng ngôn ngữ engine); "đơn giản, ít bước, phản hồi ngay" vẫn giữ. Nguồn: `Plans/25-09-2026_Product_UX_Review_Plan_v1.md` mục 2.0 · tóm tắt: `Brain/Tư duy/Tư duy 1 · Sản phẩm và người dùng.md`. 3 dòng dưới là bản 20/05, giữ để tra lịch sử.

- **Người dùng bình thường** — không quen phần mềm kiến trúc, không quen phần mềm máy tính phức tạp
- **Ưu tiên:** đơn giản, trực quan, ít bước thao tác nhất có thể
- **Không ưu tiên:** tính năng pro/nâng cao cho người dùng kỹ thuật

---

## Nguyên tắc UX

- Mọi action phải **phản hồi ngay** — user phải thấy kết quả trong vòng 1 giây
- **Tránh modal phức tạp** — người dùng không nên phải học nhiều trước khi dùng được
- **Gizmo + nhập số** — vừa kéo trực quan, vừa nhập số chính xác
- **Snap mặc định bật** — người dùng bình thường cần snap để đặt đồ ngay ngắn
- **Reset luôn có sẵn** — mọi transform đều có nút reset về gốc
- **Undo/Redo tối đa 50 bước** — đủ dùng, không tốn RAM
- **Live preview khi apply material** — user thấy kết quả ngay, không cần nút Apply riêng (v1.1)
- **Swatch visual** — hiển thị texture/màu hiện tại của từng slot, không dùng text list (v1.1)

---

## Nguyên tắc UI

- **Toolbar luôn hiển thị** — WBP_MeshControls không ẩn khi không chọn mesh
- **Highlight mode đang active** — button đang chọn luôn có màu khác (0.2, 0.6, 1.0, 1.0)
- **Snap input luôn visible** — ET_SnapStep và ET_SnapAngle không ẩn theo mode
- **Selection outline** — Stencil 255, Custom Depth enabled
- **Ghost preview khi drag** — user thấy mesh ngay khi bắt đầu kéo từ inventory
- **Tab highlight dùng Image overlay** — Set Background Color không work khi Button Tint A=0 (v1.1)

---

## Kích thước thực tế

- Hiển thị kích thước mesh bằng **cm** (không phải Unreal Units trực tiếp)
- Lấy từ `Get Actor Bounds → BoxExtent × 2`
- Lưu kích thước gốc vào **DA_FurnitureItem** (pre-baked từ Python script) — không tính runtime
- Scale UI: nhập cm → tự tính Scale = NhapVao / KichThuocGoc

---

## Inventory UI (WBP_FurnitureInventory)

- Kích thước: 720×630
- Có thể drag, minimize, maximize, close
- Folder tree cột trái (cấp 1+2), chip tag cho cấp 3+
- Common Tile View virtualized — không WrapBox
- Pagination 48 items/trang

### Tab system (v1.1)
- **Tab Furniture:** duyệt mesh như cũ
- **Tab Material:** duyệt + apply material cho mesh đang select
  - HB_SlotSwatches (Collapsed khi chưa select mesh): swatch 48x48 tròn, lazy load thumbnail
  - Slot Swatch highlight xanh khi đang chọn (Image overlay + Set Color and Opacity)
  - Material Grid: CTV_MaterialCard, folder tree + search + pagination
  - Click card → Live Apply ngay (không cần nút Apply)
  - BTN_ResetSlot / BTN_ResetAll → về material gốc
