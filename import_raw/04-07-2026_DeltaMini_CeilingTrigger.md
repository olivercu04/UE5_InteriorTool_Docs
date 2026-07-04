# DELTA MINI — Quy ước ceiling + trigger cho shortcut có chủ đích
**Ngày:** 04/07/2026 | **Nguồn:** skill `ponytail-debt` (repo DietrichGebert/ponytail) | **Người duyệt:** cuhoang

**Quyết định:** KHÔNG cài skill ponytail nào (main mode xung đột KP2 + văn hóa prep + vai mentor; audit/review không đọc được Blueprint — để dành cân nhắc lại khi viết C++ HTTP layer ở B1). Chỉ lấy 1 convention: mỗi shortcut có chủ đích phải ghi kèm **ceiling** + **upgrade trigger** để "để sau" không thành vĩnh viễn.

---

## PHẦN A — Chèn vào `docs/00_Core/DEVIATIONS.md`

> Vị trí: trong mục **"## CÁCH DÙNG"**, NGAY SAU khối "**Phân loại lý do:**". Chèn nguyên văn:

```markdown
**Quy ước ceiling + trigger (thêm 04/07/2026 — từ ponytail-debt):**

Deviation loại shortcut CÓ CHỦ ĐÍCH ([SCOPE], giải pháp tạm, fallback, scope cut) ghi thêm 2 trường:
- **ceiling:** giới hạn của giải pháp tạm — chịu được đến đâu thì gãy.
- **trigger:** sự kiện nào xảy ra thì BẮT BUỘC quay lại nâng cấp hoặc xóa.

Thiếu trigger = rot risk: "để sau" thành vĩnh viễn. Deviation loại đổi-cách-làm
([PLAN-SAI], [NODE], [BUG→FIX]) không cần 2 trường này.
KHÔNG hồi tố entry cũ — chỉ áp cho entry mới từ 04/07/2026.

Ví dụ: fallback MeshPath cho save cũ — ceiling: chỉ cover save tạo trước RowName
migration. trigger: Gate 2 packaged build → không còn save cũ cần giữ thì xóa fallback.
```

> Sau khi chèn: cập nhật header "**Cập nhật:**" với ngày giờ phút THỰC TẾ, thêm dòng vào bảng "Lịch sử cập nhật":
> `| 04/07/2026 | Thêm quy ước ceiling + trigger cho deviation loại shortcut có chủ đích (mục CÁCH DÙNG) — từ ponytail-debt |`

---

## PHẦN B — Bổ sung KP2 trong `docs/Rules/AI_Implementation_Rules.md`

> Vị trí: bullet CUỐI CÙNG của mục "### KP2 — Speculative prep phải được duyệt" (trước heading "### KP3"). Chèn nguyên văn:

```markdown
- Shortcut/giải pháp tạm ĐƯỢC DUYỆT → ghi DEVIATIONS.md kèm **ceiling** (chịu được
  đến đâu thì gãy) + **trigger** (sự kiện nào thì bắt buộc nâng cấp/xóa). Thiếu
  trigger = shortcut thành vĩnh viễn. (Quy ước từ ponytail-debt — mẫu trong DEVIATIONS.md.)
```

> Sau khi chèn: bump version **2.5 → 2.6**, header ngày giờ phút thực tế, thêm dòng changelog:
> `| 2.6 | 04/07/2026 | KP2 bổ sung quy ước ceiling + trigger cho shortcut được duyệt (từ ponytail-debt) |`

---

## PHẦN C — cuhoang TỰ paste (không qua Claude Code)

Vào Custom Instructions của project claude.ai:

1. Header: `v2.1` → **`v2.2 — 04/07/2026`**; dòng Đồng bộ: `AI_Implementation_Rules v2.5` → **`v2.6`**.
2. Mục 11, thay dòng KP2 bằng:

```
- **KP2 — Prep phải duyệt:** không tự thêm feature/param/field ngoài yêu cầu. "Chuẩn bị 1 lần thay vì 2" vẫn OK nhưng phải nêu ra + cuhoang duyệt trước. Shortcut được duyệt → DEVIATIONS kèm ceiling + trigger.
```

---

## COMMAND BLOCK — paste cho Claude Code

```
Đọc file import_raw/04-07-2026_DeltaMini_CeilingTrigger.md rồi thực hiện ĐÚNG 2 việc:

1. PHẦN A: chèn khối "Quy ước ceiling + trigger" vào docs/00_Core/DEVIATIONS.md,
   trong mục CÁCH DÙNG, ngay sau khối "Phân loại lý do". Cập nhật header ngày giờ
   phút thực tế + thêm dòng bảng "Lịch sử cập nhật" theo mẫu trong delta.
2. PHẦN B: thêm 1 bullet cuối mục KP2 trong docs/Rules/AI_Implementation_Rules.md
   (trước heading KP3). Bump 2.5 → 2.6, header giờ thực tế, thêm dòng changelog
   theo mẫu trong delta.

RÀNG BUỘC (KP3):
- KHÔNG sửa entry deviation cũ nào — quy ước không hồi tố.
- KHÔNG đụng file/section nào khác ngoài 2 chỗ trên. Không reformat phần không đụng tới.
- PHẦN C là việc của tao, bỏ qua.

Xong: xuất diff summary (file, section, ± dòng) để tao review trước khi commit.
```
