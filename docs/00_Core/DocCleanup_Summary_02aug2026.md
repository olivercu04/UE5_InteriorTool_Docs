# Doc Cleanup Summary — 02/08/2026 (Lô A → E)

**Mục đích:** Tổng kết 1 chỗ cho cả đợt dọn docs 02/08/2026, để session sau không phải lần theo
5 lô rải rác. Đây là điểm vào — chi tiết đầy đủ luôn nằm ở các file được dẫn tới.

---

## 1. ĐÃ LÀM GÌ MỖI LÔ

### Lô A — Merge delta Q9 (S-Matrix)
Merge nội dung luật Q9 (S-Matrix Gate) vào `Rules/AI_Implementation_Rules.md` (v2.14, đặt ngay
trước Q8) + 3 bug xác nhận tay (Bug-MaterialPrimaryOnly, Bug-PasteVerticalCollapse,
Bug-StaleSurfaceType) vào `Bugs/Open_Bugs.md` + entry deviation vào `DEVIATIONS.md`. Cập nhật
`01_Session_State.md` + `PROGRESS.md` (Q9 thiết lập, không đổi thứ tự ưu tiên).

### Lô B — Đóng dấu HISTORICAL + AS-BUILT lẫn trong Plans/Sprints
- Vá doc-drift PROGRESS.md (thiếu hoạt động 01-02/08 — Replace UX Fix, recount bar).
- Đóng dấu `⚠️ [HISTORICAL]` cho 8 file plan cũ (Planning/, Sprints/Sprint2-4, Sprint0_UX).
- Rà + quyết định P2/P1 (Studio/Combo Thumbnail) = DONE theo luật mới **R-DOC-DONE** — tách case
  Cao + G5 VRAM ra `Bugs/Open_Bugs.md` (Task-P2-SweepCao, Task-P1-VRAMRegression). Bar Sprint 5:
  16/22 → 18/22.
- Sửa ô `C3` gộp 3 việc (luật mới **R-DOC-ATOMIC**) — chỉ sửa text, không tách ô giữa sprint.
- Quét lan phát hiện 6 file "Plan"/"Task Card" bị lẫn as-built thật (test PASS, K2Node export)
  → đóng dấu `📌 [CHỨA AS-BUILT]` (luật mới **R-DOC-ASBUILT**), không di chuyển/đổi tên.
- `Sprints/Sprint3/Regression_DualDispatcher_Log.md` — quyết định KHÔNG đóng dấu HISTORICAL (là
  as-built phụ), thêm vào MERGE_LOG coverage.

### Lô C — Cross-check nhóm 1 (chỉ báo cáo)
Đọc + đối chiếu chéo 17 file (10 gốc + 6 `[CHỨA AS-BUILT]` + Regression log Sprint 3). Tạo
`CrossCheck_PreGate2_02aug2026.md` — 5 mục: mâu thuẫn trực tiếp, doc-drift đã ghi nhận chưa sửa,
`[?]` treo từ MERGE_LOG, hàm/biến không có doc, canonical lạc hậu. Không sửa file nào.

### Lô D — Đóng các mục CrossCheck có nguồn thật
- Viết doc `ResolveSelectedComboRoot()` đầy đủ vào `BP_FurnitureInputManager.md` (K2Node export
  thật cuhoang cung cấp).
- Đóng MERGE_LOG Q3 (`FindGroupData` không có Index) — sửa 3 file tự mâu thuẫn:
  `BP_FurnitureInputManager.md` (v2.9), `BP_UndoManager.md` (v1.13), `Blueprint_Logic_NodeFlow.md`
  (v1.15).
- Đóng MERGE_LOG Q4 (layout 512×1024) — không cần sửa gì, `WBP_FurnitureInventory.md` đã đúng.
- Ghi nhận `[DOC-DRIFT]` mới (`PrimarySelectedActor` vs `SelectedActors[0]`) — CHƯA đóng, chặn
  quyết định lúc lên task card Save As/Save đè.

### Lô E — Chốt Sprint 4 + tổng kết
- Đóng dấu thứ 3 `⚠️ [AS-BUILT TẠI THỜI ĐIỂM SPRINT 4]` cho `Sprints/Sprint4/Execution.md` +
  `Sprints/Sprint4/BugFix_Execution.md` — KHÔNG sửa chữ ký `FindGroupData` cũ bên trong (viết lại
  lịch sử = mất dấu vết).
- Thêm bảng "3 LOẠI DẤU DOC" vào `MERGE_LOG.md` để phân biệt `[HISTORICAL]` /
  `[CHỨA AS-BUILT]` / `[AS-BUILT TẠI THỜI ĐIỂM X]`.
- Xác nhận `BP_FurnitureInputManager_MERGED_v1.9.md` vẫn còn tồn tại (đã đánh dấu xóa từ
  17/06/2026 nhưng chưa ai xóa thật) — báo cáo. **Cập nhật ngay sau đó (quyết định cuhoang
  02/08/2026): đã XÓA THẬT** — bản backup v1.9 vs canonical v2.9 chênh 10 phiên bản, rủi ro đọc
  nhầm cao hơn giá trị lưu trữ; lịch sử đã có trong git. Đã kiểm + sửa mọi link trỏ tới file này
  (`BP_FurnitureInputManager.md`, `00_Core/MERGE_LOG.md`, `00_Core/00_INDEX.md`) sang canonical.
- Tạo file tổng kết này.

---

## 2. 4 LUẬT MỚI

| Luật | File | Tóm tắt |
|---|---|---|
| **Q9 — S-Matrix Gate** | `Rules/AI_Implementation_Rules.md` v2.14 | Trước khi cắt task card đụng `SelectedActors` → chạy bảng S-Scan (10 trạng thái S0-S9) + X-Check (10 hệ thống X1-X10). Chạy ở tầng PLAN, khác tầng Q8 (NODE FLOW). |
| **R-DOC-DONE** | `Rules/Execution_Discipline.md` v3.1 | Task tick `[x]` khi tính năng CHẠY và không ai làm tiếp — không chờ mọi nhánh nghiệm thu phụ đóng hết. Nghiệm thu còn treo → tách entry riêng `Open_Bugs.md`, không giữ task mở. |
| **R-DOC-ATOMIC** | `Rules/Execution_Discipline.md` v3.2 | 1 ô checklist = 1 việc tick độc lập. Ô gộp nhiều việc phát hiện giữa sprint → chỉ sửa TEXT, KHÔNG tách ô (tách = đổi mẫu số, phải recount toàn bộ) — chỉ tách lúc recount đầu sprint kế tiếp. |
| **R-DOC-ASBUILT** | `Rules/Execution_Discipline.md` v3.3 | Kết quả thực thi (test PASS/K2Node export/đính chính) phải về doc canonical `Blueprints/`/`Widgets/`, không chỉ ghi trong file plan. Tạm ghi ở plan → bắt buộc banner `📌 [CHỨA AS-BUILT]` ngay lúc ghi. |

(Cộng 3 luật `R-DOC-COUNT`/`R-DOC-OWNER`/`R-DOC-PASS` đã có từ trước 31/07/2026 — không đổi.)

---

## 3. 3 LOẠI DẤU DOC

Bảng đầy đủ + danh sách file: `docs/00_Core/MERGE_LOG.md` mục "3 LOẠI DẤU DOC".

| Dấu | Ý nghĩa 1 dòng |
|---|---|
| `⚠️ [HISTORICAL]` | Plan thiết kế, đã bị override — đọc để hiểu lý do quyết định, KHÔNG lấy chi tiết kỹ thuật làm sự thật hiện tại. |
| `📌 [CHỨA AS-BUILT]` | Plan + có kết quả thực thi thật trộn vào thân — phần kết quả ưu tiên cao hơn canonical nếu mâu thuẫn. |
| `⚠️ [AS-BUILT TẠI THỜI ĐIỂM X]` | Log đúng sự thật đã xảy ra tại 1 mốc, nhưng KHÔNG cập nhật sau đó — chữ ký/API có thể đã đổi, luôn tra canonical hiện hành. |

---

## 4. CÒN TREO — cần K2Node export riêng, CHƯA làm trong đợt này

### 4.1 3 mục `[?]` trong MERGE_LOG chưa đủ bằng chứng
- **Q1** — `WBP_MeshControls.md`: Then 0 của Sequence `OnSelectionChangedInfoBar` có nội dung gì?
- **Q2** — `WBP_MeshControls.md`: `BTN_Delete` còn single hay đã đổi `DeleteSelected` (multi)?
- **Q6** — `Rules/Design.md`: phần cũ pagination=50 có thông tin nào khác v1.1 không?

*(Q3, Q4, Q5, Q7, Q8 đã đóng — xem `MERGE_LOG.md`.)*

### 4.2 MỤC 5 CrossCheck — canonical lạc hậu (chưa sửa nội dung, chỉ mới đóng dấu/ghi nhận)
Đứng đầu theo rủi ro (xem đầy đủ `CrossCheck_PreGate2_02aug2026.md` MỤC 5):
1. 🔴 **`Data/Data_Structures.md` — `GetCombosDir()`** mô tả theo quyết định P4 (LOCALAPPDATA),
   KHÔNG khớp code thật (`ProjectSavedDir`) — **ảnh hưởng trực tiếp C11** (Export/Import cần biết
   đúng thư mục nguồn).
2. 🟡 `Widgets/WBP_DragOverlay_FurnitureCard.md` — `Button_ChangeMesh` visibility vẫn gate theo
   `bIsReplaceMode` (Boolean) cũ, hệ đã chuyển `ReplaceTarget` (Enum).
3. 🟡 `Sprints/Sprint5/Combo_Execution.md` dòng 913 — `CalculateCenter` mô tả sai (claim loại
   pivot/container).
4. 🟡 `Data/Data_Structures.md` — `S_SceneSnapshot` thiếu Version 4 + field `EditModeStackSnapshot`.
5. 🟢 `Data/Data_Structures.md` — dispatcher `OnMeshSelected`/`OnMeshDeselected` ghi nhầm
   "Deprecated" thay vì đã xóa.
6. 🟢 `Widgets/WBP_DetailPopup.md` — ghi chú `MeshToReplace` "vẫn tồn tại" đã lỗi thời (đã xóa
   thật 02/08).

### 4.3 3 open item C9 (chưa có K2Node export riêng để xác nhận)
- `RowNotFound` dead-end trong `StartReplaceMode`.
- Guard `Length(Actors)==0` biến mất khỏi export (cần verify còn/mất thật).
- `bIsReplaceMode` còn sót ở `BP_FurnitureInputManager.md` dòng 276 (mục `OnLMBReleased —
  FULL FLOW v1.5`) — KHÔNG đụng trong đợt này (đã cố ý loại trừ ở Lô C/D).

### 4.4 Quyết định CHƯA CHỐT — chặn Save As/Save đè
`ResolveSelectedComboRoot()` dùng `SelectedActors[0]` (as-built thật) hay `PrimarySelectedActor`
(mô tả trong `Plans/24-07-2026_C9_Execution_Plan.md` §V7) khi selection là MIX (combo + mesh
rời)? Chưa gây lỗi ở C9 (chỉ chạy selection 1 cụm) nhưng **PHẢI chốt trước khi viết task card
Save As/Save đè**. Xem `DEVIATIONS.md` mục "[DOC-DRIFT] ResolveSelectedComboRoot".

---

## 5. KHÔNG CÁI NÀO Ở MỤC 4 CHẶN GATE 2

Toàn bộ danh sách "CÒN TREO" ở mục 4 là nợ tài liệu (doc lạc hậu, `[?]` chưa xác minh, quyết định
UX chưa chốt cho tính năng CHƯA BẮT ĐẦU) — không phải bug chặn build hay tính năng. Thứ tự ưu
tiên hiện tại **không đổi: Save As/Save đè → C11 → C10 → Gate 2.** Riêng mục 4.4
(`ResolveSelectedComboRoot`) cần chốt TRƯỚC khi bắt tay Save As/Save đè cụ thể — không phải trước
Gate 2 nói chung.

---

## 6. FILE THAM CHIẾU NHANH

| Việc | File |
|---|---|
| Luật Q9 | `Rules/AI_Implementation_Rules.md` |
| Luật R-DOC-* | `Rules/Execution_Discipline.md` |
| Bug mới + tách từ checklist | `Bugs/Open_Bugs.md` |
| Toàn bộ deviation/doc-drift/doc-debt | `00_Core/DEVIATIONS.md` |
| Coverage + 3 loại dấu + [?] | `00_Core/MERGE_LOG.md` |
| Báo cáo cross-check gốc | `00_Core/CrossCheck_PreGate2_02aug2026.md` |
| Trạng thái Sprint 5 + bar đếm | `00_Core/PROGRESS.md` |
