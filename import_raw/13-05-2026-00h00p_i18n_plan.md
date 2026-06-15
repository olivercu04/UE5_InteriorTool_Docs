# Kế hoạch Đa ngôn ngữ (i18n)
**Phiên bản:** 1.0 | **Tạo:** 13/05/2026 — 00:00 ICT | **Project:** Lighting_Mnger (UE5.5.4)

---

## Bối cảnh

Phần mềm hướng tới thị trường quốc tế → cần support nhiều ngôn ngữ.
DataTable hiện tại đã có 2 cột song ngữ: `VieName` (tiếng Việt) + `EngName` (tiếng Anh).

**Danh sách ngôn ngữ mục tiêu:** *(cần xác nhận với team)*
- [ ] English (default)
- [ ] Tiếng Việt
- [ ] *(thêm sau: Nhật, Trung, Hàn, EU... tùy thị trường)*

---

## Quyết định kiến trúc

### Approach: Hybrid A + B+C

| Loại text | Approach | Ghi chú |
|---|---|---|
| **UI labels** — button, tooltip, error message, tiêu đề | **A — UE5 Localization System** | Dùng `Text` (FText), gather qua Localization Dashboard |
| **Data names** — tên material, tên furniture trong DataTable | **B+C — Multi-column + Auto-translate API** | Giữ `VieName`/`EngName`, Python batch-translate, manual review |
| **Save data** — RowName, MaterialOverrides, MeshPath... | **Không dịch** | Luôn lưu RowName (R5) — portable cross-locale |

---

## Nguyên tắc áp dụng NGAY (từ v1.1 trở đi)

> **Mọi text mới phải dùng kiểu `Text` (FText), không dùng `String`.**

- `Text` = FText — UE5 biết đây là text hiển thị → gather được vào Localization Dashboard
- `String` = FString — raw data, engine không gather
- **Không cần refactor code cũ ngay** — chỉ áp dụng cho widget/variable/DataTable field **mới tạo từ v1.1+**

---

## Wrapper function — Single Source of Truth

Mọi chỗ cần chọn ngôn ngữ hiển thị → gọi qua **1 hàm duy nhất**:

```
WBP_FurnitureInventory.BuildMaterialItem(Row : S_MaterialInstancesData) → BP_MaterialItem
  DisplayName = Row.EngName       ← v1.1 tạm thời (English default)

  [v1.2+ refactor — chỉ sửa ở đây]:
    Branch GetCurrentCulture == "vi":
      DisplayName = Row.VieName
    Default:
      DisplayName = Row.EngName
```

**Tại sao quan trọng:** Khi sprint i18n chạy, chỉ sửa **1 hàm này** thay vì lùng khắp Blueprint.
Áp dụng tương tự cho `DA_FurnitureItem` → cần function `GetFurnitureDisplayName(DA)` tương tự.

---

## Sprint i18n — Thực hiện SAU khi v1.1 Change Material xong

### Giai đoạn 1 — Setup UE5 Localization System (UI text)

1. Audit toàn bộ widget: liệt kê mọi chỗ dùng `String` thay vì `Text` cho text hiển thị
2. Đổi sang `Text` (FText)
3. Mở **Window → Localization Dashboard** → tạo Target mới (ví dụ: "Game")
4. **Gather Text** → UE5 quét toàn project, gom mọi FText literal
5. Export `.po` file cho từng ngôn ngữ
6. Translate (manual hoặc API) → import lại
7. Test `Set Current Culture("en")` / `("vi")` → UI đổi ngôn ngữ

### Giai đoạn 2 — Translate DataTable names (material + furniture)

```python
# Python script batch-translate (ví dụ concept, cần adjust)
import unreal, json
# Bước 1: Export DT ra JSON
# Bước 2: Gọi Google Translate API / DeepL API cho từng row trống
# Bước 3: Fill cột ngôn ngữ mới (JpName, ZhName...)
# Bước 4: reimport DT
# Bước 5: Manual review 10-15% row quan trọng (tên thương hiệu, thuật ngữ đặc thù)
```

**API tham khảo:**
- **Google Cloud Translation API** — free 500K ký tự/tháng, sau đó ~$20/1M ký tự
- **DeepL API** — chất lượng cao hơn cho EU/Đông Á, free 500K/tháng
- **Argos Translate** — offline, free, chất lượng trung bình (không cần internet)

⚠️ **Auto-translate không đủ tin cậy 100%** cho tên sản phẩm/vật liệu đặc thù — cần manual review trước khi ship.

### Giai đoạn 3 — Language selector trong UI

- Thêm settings menu → dropdown chọn ngôn ngữ
- Gọi `Set Current Culture` → save preference vào GameInstance hoặc SaveGame
- `BuildMaterialItem` / `GetFurnitureDisplayName` tự đọc culture hiện tại

---

## Checklist cần xác nhận với team

- [ ] Danh sách ngôn ngữ mục tiêu chính thức (ảnh hưởng số cột DataTable cần thêm)
- [ ] Có cần support RTL (Right-to-Left) không? (Ả Rập, Hebrew — ảnh hưởng lớn tới layout)
- [ ] Budget cho Translation API (Google/DeepL) hay dùng tool offline?
- [ ] Ai review bản dịch chuyên ngành (tên vật liệu, phong cách thiết kế)?

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 13/05/2026 — 00:00 ICT | Tạo mới — quyết định hybrid approach, nguyên tắc FText, wrapper function, sprint plan |
