# BP_FurnitureUserPrefsManager — Blueprint Logic
**Version:** 1.1 | **Ngày:** 22/07/2026 (tiếp) | **+`RemoveRecentCombo` (Delete Combo)**

⚠️ File này TẠO MỚI 22/07/2026, chỉ ghi phần đã xác nhận qua export K2Node thật (đoạn bug fix
`AddRecentCombo` bên dưới). KHÔNG phải tài liệu đầy đủ của cả class — các function/variable khác
(Favorite combo, phần đầu `AddRecentCombo` thêm ComboID mới/dedup/MoveFirst trước đoạn trim cap)
CHƯA được đối chiếu, không ghi ở đây để tránh suy đoán. Bổ sung dần khi có dịp đụng lại class này.

## Vai trò
Quản lý UserPrefs (Favorite/Recent) cho combo — persist qua `SaveUserPrefs`/`LoadUserPrefs`
(EMS SaveGame). C6.1-C6.4 (API/nút tim/hook Recent/tab hiển thị) đã DONE 22/07/2026, xem
`01_Session_State.md` mục C6 — thực hiện trực tiếp trong UE5 Editor, ngoài phiên Claude Code,
không có node flow chi tiết trong doc này.

---

## `AddRecentCombo` — đoạn trim cap + save, BUG FIX 22/07/2026

**Triệu chứng:** spawn combo mới → tắt PIE → mở lại → Recent KHÔNG giữ combo vừa spawn, chỉ còn
combo cũ.

**Nguyên nhân (export K2Node thật, 22/07):** `Call SaveUserPrefs` nằm trong nhánh `True` của
`Branch(Array Length(RecentComboIDs) > 48)` (bước trim cap) — nhánh `False` (trường hợp bình
thường, < 48 combo) không nối gì cả, dead-end. RAM luôn đúng (giải thích vì sao Print tối 21/07
ra count tăng dần đúng), nhưng chỉ save xuống đĩa khi Recent vượt 48 phần tử — với mọi test thực
tế (< 48 combo), không bao giờ ghi.

**Flow SAI (trước fix):**
```
[... đầu hàm: thêm ComboID mới vào RecentComboIDs, dedup/MoveFirst — CHƯA đối chiếu, không ghi ...]
▶→ Branch(Array Length(RecentComboIDs) > 48)
     True  ▶→ Array_Remove(...)  ▶→ Call SaveUserPrefs
     False ▶→ dead-end (KHÔNG nối gì — BUG, chỉ save khi vượt cap)
```

**Flow ĐÚNG (sau fix, 22/07/2026):**
```
▶→ Branch(Array Length(RecentComboIDs) > 48)
     True  ▶→ Array_Remove(...) ▶→ ─┐
     False ▶→ ────────────────────┤→ Call SaveUserPrefs
```
Rút `Call SaveUserPrefs` ra khỏi nhánh `True`, nối merge cả 2 nhánh (`True` sau `Array_Remove`
VÀ `False` trực tiếp) cùng trỏ vào `SaveUserPrefs`.

Q8: Custom Event/Function (chưa xác nhận container) | L2: nhánh `False` trước fix dead-end SAI
(không phải trong Sequence.Then, cần merge) — đã fix | 6A: verify bằng test tắt/mở PIE, không
chỉ đọc code tĩnh

**Ghi chú phụ:** cap thật đang là **48** (không phải 20 như `UX_Phase2_Plan.md` ghi trước đây) —
sai lệch tài liệu, không phải bug.

**Test PASS (22/07/2026):** spawn combo → tắt PIE → mở lại → Recent giữ đúng combo mới.

---

## `RemoveRecentCombo(ComboID : String)` — MỚI, Delete Combo (22/07/2026)

Cùng pattern `AddRecentCombo` (thao tác lên `RecentComboIDs` trong `BP_UserPreferencesSave` nội
bộ), bỏ đoạn Insert/dedup/cap-trim, thay bằng:
```
Array_Remove(RecentComboIDs, ComboID) → SET lại vào SaveGame object → Call SaveUserPrefs
```
Gọi từ `WBP_FurnitureInventory.HandleDeleteComboConfirmed` khi xóa combo — dọn Recent để combo
đã xóa không còn xuất hiện ở tab Recent.

---

## Lịch sử cập nhật

| Ngày | Version | Nội dung |
|------|---------|----------|
| 22/07/2026 | 1.0 | Tạo mới. Bug fix `AddRecentCombo` dead-end: `Call SaveUserPrefs` rút khỏi nhánh `True` của `Branch(RecentComboIDs.Length > 48)`, merge cả 2 nhánh cùng trỏ vào — trước đó chỉ save khi Recent vượt cap 48, mọi test thực tế (< 48 combo) không bao giờ ghi xuống đĩa. Ghi chú phụ: cap thật = 48, không phải 20 như `UX_Phase2_Plan.md`. Test PASS: spawn combo → tắt PIE → mở lại → Recent giữ đúng. Bối cảnh đầy đủ: `01_Session_State.md` mục C6 (22/07/2026), `Bugs/Open_Bugs.md`. |
| 22/07/2026 (tiếp) | 1.1 | Function mới `RemoveRecentCombo(ComboID)` — cùng pattern `AddRecentCombo`, bỏ đoạn Insert/dedup/cap-trim, thay bằng `Array_Remove` + `SaveUserPrefs`. Gọi từ `WBP_FurnitureInventory.HandleDeleteComboConfirmed` (Delete Combo feature, 5/5 test PASS). |

---

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Có mặt trong thao tác:** [[L02 · Tìm đồ trong kho|L02]] · [[L03 · Kéo đồ vào phòng|L03]] · [[L08 · Thay đồ|L08]] · [[L09 · Đổi vật liệu|L09]]

**Thuộc mảng kết nối:** [[Kết nối 3b - Combo lưu spawn thay combo]] · [[Kết nối 3c - Inventory + Cây thư mục]] · [[Kết nối 3d - Save Undo khởi động]] · [[Kết nối 3e - Vật liệu Material]]

**Gọi / điều khiển →**
- [[BP_UserPreferencesSave]] — ghi/đọc danh sách combo Gần đây · RecentComboIDs (SaveGame)

**← Được gọi bởi**
- [[WBP_FurnitureInventory]] — gọi bỏ combo khỏi Gần đây · RemoveRecentCombo()
- [[WBP_FurnitureCard]] — gọi thêm Gần đây / Yêu thích · AddRecentMesh()
- [[WBP_FurnitureInventory]] — đọc danh sách Gần đây / Yêu thích · GET UserPrefs → RecentMeshes / FavoriteMeshes
- [[WBP_DragOverlay_FurnitureCard]] — thêm đồ vừa thả vào Gần đây · AddRecentMesh()
- [[WBP_FOFF_ToolDemo]] — sinh ra · Spawn
- [[WBP_FurnitureInventory]] — thêm vật liệu vào Gần đây · AddRecentMaterial() ✓K2
- [[BP_FurnitureActor]] — thêm vật liệu vào Gần đây · AddRecentMaterial()

<!-- BRAIN:END -->
