# Cross-Check Pre-Gate 2 — 02/08/2026

**Mục đích:** 4 việc còn lại trước Gate 2 (**Save As/Save đè → C11 → C10 → Gate 2**) sẽ phải đọc
nhóm doc dưới đây. Báo cáo này chỉ ĐỐI CHIẾU, KHÔNG SỬA — không tự "cho khớp" bất kỳ mô tả kỹ
thuật nào.

**Luật ưu tiên khi đối chiếu (R-DOC-ASBUILT):** khi phần as-built trong file `[CHỨA AS-BUILT]`
có ngày MỚI HƠN doc canonical bị đối chiếu → coi canonical là NGHI NGỜ (cần cập nhật), KHÔNG coi
file plan/as-built kia là sai. Mỗi mục mâu thuẫn ghi rõ ngày của cả 2 bên.

**Danh sách file đã đọc (17, gộp gốc + bổ sung):**
```
Blueprints/BP_ComboManager.md
Blueprints/BP_FurnitureInputManager.md          (v2.8, 02/08/2026)
Blueprints/BP_UndoManager.md                    (v1.12, 30/07/2026)
Widgets/WBP_FurnitureInventory.md               (v3.19, 02/08/2026)
Widgets/WBP_ComboCard.md                        (v1.6, 30/07/2026)
Widgets/WBP_DetailPopup.md                      (v1.3, 24/07/2026)
Widgets/WBP_DragOverlay_FurnitureCard.md        (v1.8, 25/06/2026 — chứa cả WBP_FurnitureCard)
Sprints/Sprint5/Combo_Execution.md
Data/Data_Structures.md                         (14/07/2026 — chỉ mục Combo được touch, phần
                                                    còn lại cũ hơn nhiều)
Plans/24-07-2026_C9_Execution_Plan.md           (24/07/2026 — [CHỨA AS-BUILT])
Plans/01-08-2026_Phase0_Verify_Report_ReplaceUXFix.md  (01/08/2026 — [CHỨA AS-BUILT])
Plans/P2_StudioThumbnail_Execution.md           ([CHỨA AS-BUILT])
Plans/P1_ComboThumbnail_Execution.md            ([CHỨA AS-BUILT])
Sprints/Sprint5/C5.8_TaskCard2_FixPlan_11jul2026.md    ([CHỨA AS-BUILT])
Sprints/Sprint5/C5.8_REG_TaskCard_11jul2026.md         ([CHỨA AS-BUILT])
Sprints/Sprint3/Regression_DualDispatcher_Log.md       (10/06/2026 — as-built phụ)
```

---

## MỤC 1 — MÂU THUẪN TRỰC TIẾP

Sắp theo rủi ro với **Save As/Save đè → C11 → C10 → Gate 2** (liên quan Save As/Save đè xếp trước).

### 1.1 🔴 `bIsReplaceMode` (Boolean) vs `ReplaceTarget` (Enum) — 3 chỗ lệch, kể cả NGAY TRONG file canonical
**Rủi ro:** Trung bình-Cao — Replace là hạ tầng dùng chung; Save As/Save đè không gọi trực tiếp
nhưng C10 (Regression) chắc chắn sẽ chạm lại toàn bộ luồng Replace.

- **`WBP_DragOverlay_FurnitureCard.md`** (bản ghi cả `WBP_FurnitureCard`), dòng ~53, **v1.8 —
  25/06/2026**: `OnListItemObjectSet` — `Branch InventoryRef.bIsReplaceMode == True? → Set
  Visibility(Button_ChangeMesh, ...)`.
- **`BP_FurnitureInputManager.md`**, dòng 37-38, **v2.8 — 02/08/2026 (Variables)**:
  `ReplaceTarget : E_ReplaceTarget` — chú thích rõ "[MIGRATE, C9.0c, xác nhận qua K2Node export
  **24/07/2026**] thay `bIsReplaceMode` (Boolean) cũ".
- **NGAY TRONG CÙNG FILE `BP_FurnitureInputManager.md`**: dòng 233-236 (nhánh Tick, ghi chú "THÊM
  vào doc 24/07") dùng đúng `ReplaceTarget`; nhưng dòng 276, mục "OnLMBReleased — FULL FLOW
  (**v1.5**)" vẫn viết `Branch bIsReplaceMode → (exit replace mode chain nếu đang replace)` —
  **KHÔNG được cập nhật khi migrate C9.0c**.
- **`WBP_ComboCard.md`** v1.6 (30/07/2026) và **`WBP_FurnitureInventory.md`** v3.19 (02/08/2026)
  đều dùng đúng `ReplaceTarget` (enum) — xác nhận đây là chuẩn hệ thống hiện hành.

**Ngày 2 bên:** as-built mới nhất xác nhận migrate = **24/07/2026** (K2Node export). Canonical bị
nghi ngờ = `WBP_DragOverlay_FurnitureCard.md` (25/06/2026, cũ hơn) + đoạn "v1.5" còn sót trong
chính `BP_FurnitureInputManager.md` (gốc từ ~25/05/2026, chưa từng cập nhật qua nhiều lần migrate).

### 1.2 🟡 `CalculateCenter` có loại pivot/container hay không
**Rủi ro:** Trung bình — không chặn Save As (dùng `CalculateComboAnchor` riêng), nhưng
`CalculateCenter` vẫn dùng cho gizmo pivot + Copy/Paste, C10 sẽ test lại các luồng này.

- **`Sprints/Sprint5/Combo_Execution.md`**, dòng 913 (phần kế hoạch "### C9 — Replace combo",
  không có timestamp riêng, thuộc mảng plan gốc — cũ hơn 24/07): *"**CalculateCenter** = hàm
  CHUNG dùng cả C3 (save) lẫn C9 (replace). Input: mảng actors của group; **loại trừ pivot dummy
  và container actor** trước khi tính average."*
- **`Plans/24-07-2026_C9_Execution_Plan.md`**, dòng 38 (§V4) và dòng 663 (bảng rủi ro), **as-built
  xác nhận 24/07/2026 qua K2Node export**: *"CalculateCenter(Actors) → Vector = ForEach: Sum +=
  GetActorLocation → Return(Sum/Length). **KHÔNG loại pivot/container** (doc Combo_Execution.md
  ghi sai)."*

**Ngày 2 bên:** Combo_Execution.md (plan gốc, không rõ ngày dòng 913, chắc chắn trước 24/07) vs
`24-07-2026_C9_Execution_Plan.md` (as-built xác nhận **24/07/2026**) → theo R-DOC-ASBUILT,
**Combo_Execution.md là bên nghi ngờ**, cần sửa dòng 913.

### 1.3 🟡 `S_SceneSnapshot` — field `EditingGroupID` (String) vs `EditModeStackSnapshot` (Array\<String\>)
**Rủi ro:** Trung bình cho C10 (Regression Undo) — không liên quan Save As/C11 trực tiếp.

- **`Data/Data_Structures.md`**, dòng 37-48 (mục `S_SceneSnapshot`, không thấy dấu hiệu được touch
  bởi lần sửa 14/07 — header file ghi rõ 14/07 "chỉ sửa mảng Combo lỗi thời"): liệt kê field
  `EditingGroupID : String | Mới Sprint 4`, KHÔNG có `Version 4`, KHÔNG có
  `EditModeStackSnapshot`.
- **`Blueprints/BP_UndoManager.md`** v1.8+ (canonical, thêm **15/06/2026** — Sprint 4 Bug Fix A12):
  field thật là `EditModeStackSnapshot : Array of String` (Version 4), KHÔNG có field tên
  `EditingGroupID` ở đâu cả.
- Đây không phải phát hiện mới hoàn toàn — `00_Core/DEVIATIONS.md` (mục Sprint 4, D4-6) đã từng
  ghi nhận tên `EditingGroupID` chỉ là tên DỰ KIẾN trong `03_Code_Inheritance_Strategy.md` (nay đã
  đóng dấu `[HISTORICAL]`), chưa từng implement — nhưng **fix đó chưa lan sang
  `Data_Structures.md`**.

**Ngày 2 bên:** BP_UndoManager.md field thật có từ **15/06/2026**; Data_Structures.md mục này
chưa từng được sync kể từ đó (kể cả sau lần sửa 14/07/2026 — lần đó chỉ đụng mục Combo).

### 1.4 🟢 `MeshToReplace` (số ít) — "vẫn tồn tại (dead code)" vs "XÓA HOÀN TOÀN"
**Rủi ro:** Thấp — chỉ là ghi chú lịch sử, biến đã bị xóa thật, không ảnh hưởng code mới.

- **`Widgets/WBP_DetailPopup.md`** v1.3 (**24/07/2026**): *"bản cũ SET nhầm biến `MeshToReplace`
  (số ít, dead code — **vẫn tồn tại** trên `BP_FurnitureInputManager`, không bị xóa dù changelog
  cũ từng ghi đã xóa)..."*
- **`Blueprints/BP_FurnitureInputManager.md`** v2.8 (**02/08/2026**, Variables): *"`MeshToReplace`
  (single) — **XÓA HOÀN TOÀN 02/08/2026**..."*

**Ngày 2 bên:** WBP_DetailPopup.md (24/07) cũ hơn BP_FurnitureInputManager.md (02/08) — theo
R-DOC-ASBUILT, phần "vẫn tồn tại" trong WBP_DetailPopup.md nay lạc hậu, biến đã bị xóa thật sự.

### 1.5 🟢 `OnMeshSelected`/`OnMeshDeselected` — "Deprecated (vẫn fire)" vs "ĐÃ XÓA"
**Rủi ro:** Thấp cho 4 việc còn lại, nhưng dễ gây đoán mò nếu ai đó bind theo Data_Structures.md.

- **`Data/Data_Structures.md`**, mục EVENT DISPATCHERS: *"Deprecated (vẫn fire để compat):
  `OnMeshSelected`, `OnMeshDeselected`"*.
- **`Sprints/Sprint3/Regression_DualDispatcher_Log.md`** (as-built, **10/06/2026**): *"Dispatcher
  XÓA: `OnMeshSelected`, `OnMeshDeselected`"* — khớp `00_Core/DEVIATIONS.md` mục Sprint 3 (D3-5):
  *"XÓA cả hai — OnSelectionChanged là DUY NHẤT"*.

**Ngày 2 bên:** as-built xác nhận xóa từ **10/06/2026**; mục này trong Data_Structures.md rõ ràng
chưa từng cập nhật kể từ trước đó (không nằm trong phạm vi sửa 14/07).

---

## MỤC 2 — DOC-DRIFT ĐÃ GHI NHẬN NHƯNG CHƯA SỬA

### 2.1 ⚠️ Đã kiểm lại: 1/3 mục "biết trước" KHÔNG còn tái hiện — báo cáo trung thực
- **"WBP_DetailPopup.BTN_ChangeMesh — doc ghi gọi StartReplaceMode, thực tế inline logic":**
  Đã đọc trực tiếp `WBP_DetailPopup.md` v1.3 (24/07/2026) — **mục này ĐÃ ĐƯỢC SỬA từ C9.0c**:
  `BTN_ChangeMesh.OnClicked` nay gọi thẳng `StartReplaceMode(...)`, không còn inline logic. Đây
  KHÔNG còn là doc-drift đang mở — có khả năng danh sách "biết trước" được viết trước khi C9.0c
  chạy (24/07). Không ép buộc tìm cho khớp; ghi nhận đã đóng.
- **"MeshToReplace (số ít) — changelog ghi đã xóa, thực tế còn dead code":** xem MỤC 1.4 — đã
  ĐÓNG THẬT (02/08), chỉ còn 1 dòng ghi chú cũ (24/07) trong WBP_DetailPopup.md chưa cập nhật.
- **"CalculateCenter — doc mô tả có loại pivot/container, as-built KHÔNG loại":** xem MỤC 1.2 —
  **VẪN CÒN MỞ**, đã tự ghi nhận trong `24-07-2026_C9_Execution_Plan.md` (dòng 663: *"doc cũ mô tả
  sai"*) nhưng `Combo_Execution.md` (nguồn gốc mô tả sai) chưa được sửa.

### 2.2 🔴 Tự ghi nhận nhưng chưa xác định nguồn — `ReplaceTarget` migration source
`Blueprints/BP_FurnitureInputManager.md`, dòng 40-42 (ngay trong định nghĩa biến `ReplaceTarget`):
*"...delta 24/07 dẫn 'DEVIATIONS.md §11', nhưng **KHÔNG tìm thấy mục này trong file canonical
hiện tại**, có thể nằm ở doc khác chưa phân phối vào đây — **cần cuhoang xác nhận nguồn thật**."*
— tự ghi nhận `[?]` ngay trong file canonical, CHƯA có câu trả lời ở đâu trong 17 file đã đọc.

### 2.3 🟡 `GetCombosDir()` thật vs quyết định P4 (LOCALAPPDATA)
`Data/Data_Structures.md`, dòng 120 (tự ghi nhận **14/07/2026**): *"`GetCombosDir()` thật trả về
`FPaths::ProjectSavedDir()/Combos` — KHÁC quyết định P4 đã ghi trong DEVIATIONS.md 23/06/2026
(đổi sang `%LOCALAPPDATA%`)... Không rõ P4 bị revert hay chưa từng merge."* — khớp trực tiếp với
phát hiện của Lô B (PROGRESS.md, ô `C3`: *"P4 — LOCALAPPDATA → CHƯA LÀM"*). Cùng 1 sự thật, ghi ở
2 nơi độc lập, cả 2 đều CHƯA được đóng — rủi ro cho C11 (Export/Import) vì đường dẫn combo library
ảnh hưởng trực tiếp cách export/import đọc file.

**Rủi ro:** Cao cho C11 (Export/Import cần biết đúng thư mục combo) — xếp gần đầu.

---

## MỤC 3 — [?] TREO TỪ MERGE_LOG CHƯA ĐÓNG

Đối chiếu bảng "Mục [?] cần Opus/cuhoang xác minh" trong `MERGE_LOG.md` (Q1-Q8) với 17 file vừa
đọc:

| # | Mục | Trạng thái sau đối chiếu |
|---|---|---|
| Q3 | `FindGroupData` output pins có Index không? | **✅ CÓ THỂ ĐÓNG** — `Plans/24-07-2026_C9_Execution_Plan.md` dòng 40 (V6) + dòng 689, as-built xác nhận qua K2Node export 24/07/2026: *"FindGroupData không có Index"*. Khớp `Data/Data_Structures.md` dòng 442 (`FindGroupData(GroupID) → S_GroupData`, không có Index). MERGE_LOG.md chưa được cập nhật để đóng mục này. |
| Q4 | Layout `WBP_FurnitureInventory`: 512×1024 hay 720×630? | **✅ CÓ THỂ ĐÓNG** — `Widgets/WBP_FurnitureInventory.md` dòng 144 + dòng 1734 xác nhận nhất quán **512×1024** (`Set Size(512,1024)` ở Event Construct). Không tìm thấy chỗ nào trong 17 file nhắc "720×630" — có thể là giá trị cũ/nhầm từ nguồn khác đã hết hiệu lực. MERGE_LOG.md chưa đóng mục này. |
| Q1 | `WBP_MeshControls.md` — Then 0 của Sequence `OnSelectionChangedInfoBar` | ⏳ **VẪN TREO** — `WBP_MeshControls.md` không nằm trong 17 file phạm vi Lô C, không thể xác minh. |
| Q2 | `WBP_MeshControls.md` — `BTN_Delete` single hay `DeleteSelected` (multi)? | ⏳ **VẪN TREO** — cùng lý do Q1, ngoài phạm vi đọc lần này. |
| Q6 | `Rules/Design.md` — phần pagination=50 có thông tin gì khác v1.1 không? | ⏳ **VẪN TREO** — `Rules/Design.md` không nằm trong phạm vi Lô C. |

**Khuyến nghị:** Q3 và Q4 nên được đóng chính thức trong `MERGE_LOG.md` ở lần rà kế tiếp — đã có
đủ bằng chứng as-built, không cần hỏi cuhoang thêm.

---

## MỤC 4 — HÀM/BIẾN ĐƯỢC NHẮC NHƯNG KHÔNG CÓ DOC

### 4.1 🔴 `ResolveSelectedComboRoot()` — GỌI NHIỀU NƠI, KHÔNG CÓ ĐỊNH NGHĨA trong 17 file
**Rủi ro:** CAO NHẤT cho **Save As/Save đè** — `01_Session_State.md` (30/07/2026) ghi rõ tính năng
Save As/Save đè sẽ **"tái dùng `ResolveSelectedComboRoot()` viết trong C9"**. Đây là điểm Sonnet
dễ đoán mò nhất nếu bắt tay làm Save As/Save đè mà không có node flow thật của hàm này.

- **Gọi tại** `Blueprints/BP_FurnitureInputManager.md` dòng 1035 (chú thích), dòng 1110
  (`ResolveSelectedComboRoot() ●→ ECR_RootGID2, ECR_ComboID2, ECR_bFound2` — 3 output).
- **Gọi tại** `Widgets/WBP_FurnitureInventory.md` dòng 368 (`InputManagerRef.ResolveSelectedComboRoot()`),
  dòng 402 (mô tả dùng route 2 chiều Mesh↔Combo).
- **KHÔNG có** header định nghĩa (`## ResolveSelectedComboRoot` hay tương đương) trong bất kỳ file
  nào trong 17 file đã đọc — kể cả `BP_FurnitureInputManager.md` (nơi nó được gọi nhiều nhất) hay
  `BP_ComboManager.md`.
- Đối chiếu toàn repo (ngoài phạm vi 17 file): chỉ thấy nhắc ở `Plans/Post_C5_Execution_Plan_v1.md`
  (không thuộc danh sách Lô C, và cũng không nằm trong 6 file `[CHỨA AS-BUILT]`) — chưa xác nhận
  file đó có thân hàm đầy đủ hay chỉ nhắc tên.

**Khuyến nghị:** TRƯỚC khi bắt tay Save As/Save đè, phải tìm/xác nhận thân hàm thật của
`ResolveSelectedComboRoot()` (K2Node export hoặc hỏi cuhoang) — không suy đoán chữ ký/logic.

### 4.2 Không phát hiện thêm hàm/biến "mồ côi" nào khác đáng kể
Các hàm khác được kiểm tra đều có định nghĩa trong phạm vi 17 file: `ExecuteComboReplace`,
`ReplaceCombo`, `DestroyComboCluster`, `ComboRootGroupIDToReplace` (đều trong
`BP_FurnitureInputManager.md`/`BP_ComboManager.md`); `RestoreCurrentSnapshot()` (trong
`BP_UndoManager.md`); `CalculateComboAnchor` (trong `BP_FurnitureInputManager.md`).

---

## MỤC 5 — CANONICAL LẠC HẬU (chỉ liệt kê, KHÔNG sửa)

Sắp theo rủi ro với **Save As/Save đè → C11 → C10 → Gate 2**.

| # | Canonical lạc hậu | File `[CHỨA AS-BUILT]` có info mới hơn | Rủi ro |
|---|---|---|---|
| 1 | `Data/Data_Structures.md` — `GetCombosDir()` mô tả theo quyết định P4 (LOCALAPPDATA), không khớp code thật (`ProjectSavedDir`) | Tự phát hiện trong chính file (14/07) + xác nhận chéo qua `PROGRESS.md` (ô C3, Lô B) | 🔴 **Cao — C11** (Export/Import cần biết đúng thư mục nguồn combo) |
| 2 | `Widgets/WBP_DragOverlay_FurnitureCard.md` (v1.8, 25/06/2026) — `Button_ChangeMesh` visibility vẫn gate theo `bIsReplaceMode` (Boolean) | `Blueprints/BP_FurnitureInputManager.md` (24/07, C9.0c) + `Widgets/WBP_FurnitureInventory.md` (v3.19) — hệ thống đã chuyển hẳn sang `ReplaceTarget` (Enum) | 🟡 **Trung bình — C10** (Regression sẽ chạm lại toàn bộ Replace, dễ nhầm nếu đọc file này trước) |
| 3 | `Sprints/Sprint5/Combo_Execution.md` dòng 913 — `CalculateCenter` mô tả sai (claim loại pivot/container) | `Plans/24-07-2026_C9_Execution_Plan.md` (24/07, K2Node export xác nhận không loại) | 🟡 **Trung bình — C10** (test Copy/Paste, gizmo pivot dùng chung hàm này) |
| 4 | `Data/Data_Structures.md` — `S_SceneSnapshot` thiếu Version 4 + field `EditModeStackSnapshot`, còn ghi `EditingGroupID` (chưa từng tồn tại thật) | `Blueprints/BP_UndoManager.md` (v1.8+, 15/06/2026) | 🟡 **Trung bình — C10** (Regression Undo cần đúng schema snapshot) |
| 5 | `Data/Data_Structures.md` — dispatcher `OnMeshSelected`/`OnMeshDeselected` ghi "Deprecated (vẫn fire)" thay vì đã xóa | `Sprints/Sprint3/Regression_DualDispatcher_Log.md` (10/06/2026, as-built phụ) + `DEVIATIONS.md` D3-5 | 🟢 **Thấp** |
| 6 | `Widgets/WBP_DetailPopup.md` (v1.3, 24/07) — ghi chú `MeshToReplace` "vẫn tồn tại (dead code)" | `Blueprints/BP_FurnitureInputManager.md` (v2.8, 02/08) — đã XÓA HOÀN TOÀN | 🟢 **Thấp** (chỉ 1 dòng ghi chú lịch sử) |

---

## TÓM TẮT — thứ tự nên đọc/sửa trước khi làm 4 việc còn lại

1. **Trước Save As/Save đè:** xác nhận thân hàm thật `ResolveSelectedComboRoot()` (MỤC 4.1) —
   bắt buộc, không suy đoán.
2. **Trước C11:** làm rõ `GetCombosDir()` — LOCALAPPDATA hay ProjectSavedDir (MỤC 2.3 / MỤC 5.1) —
   ảnh hưởng trực tiếp đường dẫn export/import.
3. **Trước C10:** dọn 3 chỗ Replace/Undo lạc hậu (MỤC 5.2/5.3/5.4) trước khi chạy regression, để
   không lấy nhầm mô tả cũ làm chuẩn so sánh.
4. Phần còn lại (MỤC 5.5/5.6, các [?] Q1/Q2/Q6 ngoài phạm vi) — rủi ro thấp, có thể dọn sau Gate 2.

**Không có file nào bị sửa trong quá trình tạo báo cáo này — chỉ tạo đúng 1 file
`docs/00_Core/CrossCheck_PreGate2_02aug2026.md`.**
