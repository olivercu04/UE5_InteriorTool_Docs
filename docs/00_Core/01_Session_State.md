# Session State
> RAM của project. Chỉ trả lời "ĐANG đứng đâu", KHÔNG phải "đã đi qua đâu".
> Lịch sử → Git / PROGRESS.md / DEVIATIONS.md. KHÔNG thêm chronology/changelog vào đây.
> Cập nhật khi trạng thái đổi. Giữ ~50-100 dòng. Cái gì đã có nơi khác sở hữu → cắt, không copy.

**Last verified:** 07/09/2026 (S7.G3 Item 1/2/4 PASS. Còn treo: RestoreSnapshot Step 4 dòng Call thừa + test regression Undo/Redo material — xem "Việc tiếp theo")

---

Current: Sprint 7 (Material v1.2) → G3 ĐÓNG (07/09/2026). Next: G4
> Giữ đúng 1 dòng. Đổi trạng thái → sửa tại chỗ, không thêm dòng mới.

---

## Đang ở đâu

| | |
|---|---|
| **Nền làm việc** | Project tổng tháng 6 (clone MỚI của master, tích hợp 24/08). Code trực tiếp tại đây. `FurnitureTool_Standalone` chỉ còn vai trò lịch sử/đóng gói cũ. |
| **Phase** | Hướng Gate 2 (bản packaged Shipping thật) |
| **Milestone** | Sprint 7 — Material v1.2 (edit vật liệu runtime) |
| **Current Task** | S7.G2 ĐÓNG (05/09/2026). S7.G3: [VERIFY] đầu G3 ✅ · Item 1 (nhánh legacy `RestoreMyMaterialSlots`) ✅ PASS · Item 2 (`ActorLoaded` reroute) ✅ PASS · Item 4 (Combo `FComboItemData`+ghi/đọc `MaterialSlots`) ✅ PASS. Item 3 (snapshot) đã dời sang G2/2B từ trước (RESEQUENCE 03/09), không thuộc G3 nữa. 3 bug phát sinh trong phiên 07/09 đều đã fix (`Bug-RowName-MissingInClipboard`, `Bug-RestoreMyMaterialSlots-DeadEndLegacy`, `Bug-LoadMeshAsync-RestoreRace` — phần Combo). |
| **Task Source** | `Plans/Sprint7_MaterialEdit_Plan_v1.1.md` mục S7.G3 (v1.9). Delta 07/09: `07-09-2026_S7G3_Item1-4_Delta.md` |
| **Next** | G3 còn lại theo plan gốc: G3.G5-G8 (EMS legacy diễn rộng hơn nếu còn trường hợp khác, panel engine, dictionary fill, tile pattern, final regression) — CHƯA bắt đầu. Xem thêm mục "Việc tiếp theo" bên dưới (việc treo từ phiên 07/09, ưu tiên cao hơn G5-G8). |
| **Blockers** | Không |

Thứ tự tổng tới Gate 2: **Sprint 7 (Material v1.2) → Sprint 6 (Polish UX) → Gate 2**
(sau Gate 2: Backend B0→B5 — cloud, chợ combo)
Lý do S7 trước: integration sớm chính là để G0 kiểm kê material THẬT; luật riêng S7 đã chặn rủi
ro đụng đồ đồng nghiệp.

---

## Việc tiếp theo (chưa làm, từ delta 07/09/2026 — PHẦN D, giữ nguyên y hệt)

1. **`RestoreSnapshot` Step 4 (`BP_UndoManager`)** — gỡ dòng `Call NewActor.RestoreMyMaterialSlots`
   thừa (chỉ giữ `SET NewActor.MaterialSlots`), đúng pattern đã áp cho Combo. Ưu tiên: TRUNG BÌNH
   — không hỏng chức năng (LoadMeshAsync giờ tự phủ), nhưng để lại 1 lần gọi sớm vô hiệu mỗi lần
   Undo/Redo material, và CHƯA test Undo/Redo material sau đợt fix hôm nay để xác nhận không hồi
   quy.
2. **Test regression Undo/Redo material** — chưa chạy trong phiên này. Kịch bản: đổi material 1
   actor → Ctrl+Z → Ctrl+Y (redo) → material phải đúng, không nháy/lỗi do double-call.
3. **Merge field `MaterialSlots` vào `S_FurniturePlacement`** trong canonical `BP_UndoManager.md`
   (nợ từ G2/2B, 03/09 — chưa merge từ trước phiên này, không phải nợ mới).
4. **S7.G3 còn lại theo plan gốc:** G3.G5-G8 (EMS legacy diễn rộng hơn nếu còn trường hợp khác,
   panel engine, dictionary fill, tile pattern, final regression) — CHƯA bắt đầu.
5. **(Tùy chọn, không khẩn) Dọn `SaveComboFromSelection` Bước 5d** — xóa loop tính
   `MaterialOverrides_SaveCombo` (dư thừa, không ai đọc ở combo mới) — chỉ làm khi có thời gian
   rảnh, không phải ưu tiên.

> ⚠️ Ghi chú Claude Code (không thuộc PHẦN D gốc): mục 3 ở trên (merge field `MaterialSlots` vào
> `S_FurniturePlacement`) đã được xử lý NGAY TRONG lần merge delta này (xem `Blueprints/BP_UndoManager.md`
> v1.16) — giữ nguyên PHẦN D theo đúng yêu cầu "không rút gọn/diễn giải khác đi", chỉ ghi chú thêm
> ở đây để tránh nhầm là việc còn treo. Đề xuất: khi đóng dấu việc này lần sau, xóa mục 3 khỏi
> danh sách trên.

---

## Active bugs relevant now
> Chỉ bug đang CHẶN việc hiện tại. Danh sách đầy đủ → `Bugs/Open_Bugs.md`.

- **Bug-ComboRoot-MixedLooseGroup** 🔴 — chặn ĐẦU SPRINT 6 (không phải Sprint 7). Chạm kiến trúc
  combo: `SaveComboFromSelection` nên LUÔN tạo 1 wrapper root group. Ghi ở đây để không quên khi
  Sprint 7 xong chuyển sang Sprint 6. `Bugs/Open_Bugs.md`.

---

## Active ceilings / constraints
> Shortcut có chủ ý còn hiệu lực + điều kiện buộc refactor. Đầy đủ → `DEVIATIONS.md`.

- **2 ceiling item khi migrate standalone:** `BP_Lib_ArchvizPCG_Camera` (Geometry Script),
  `BP_UnTest_Lib` (debug plugin) — chấp nhận, không chặn.
- **Standalone chưa có git repo** — risk quy trình đã ghi nhận (backup dựa Git chưa áp cho
  `I:\FurnitureTool_Standalone\`).
- **Còn lỗi runtime trong bản packaged Development** (Gate 1.5 C5, chưa fix) — thuộc phần soi ở
  Gate 2 smoke, KHÔNG chặn Sprint 7.
- **2 bug Surface dời sau Gate 2** (Sprint Surface): Bug-PasteVerticalCollapse 🔴,
  Bug-StaleSurfaceType 🟡 — cùng gốc "chọn sai điểm neo". (Bug-MaterialPrimaryOnly cũng cùng nhóm
  nhưng đã đưa lên active bugs vì fix trong Sprint 7.) `Bugs/Open_Bugs.md`.
- **Nợ Gate 2:** `SelectedGeometryMaterial_Blue` (TextureObjectParameter thiếu texture — root
  cause đã biết, KHÔNG chặn Sprint 7).
- **Chưa chốt (Sprint 7):** cơ chế đánh dấu slot khóa (hướng LockedSlots blacklist trong DT là
  ứng viên, cuhoang chưa duyệt). Chốt chặn `GetEditableSlots` (G1) cô lập quyết định này — KHÔNG
  chặn G1-G4.

---

## Recent changes (tối đa 5, mới nhất trên cùng)
> Chỉ để định vị "vừa xong gì". Lịch sử đầy đủ → PROGRESS.md + Git.

- 07/09 — S7.G3 Item 1/2/4 PASS (nhánh legacy `RestoreMyMaterialSlots` + `ActorLoaded` reroute +
  Combo `FComboItemData`/`MaterialSlots`). Merge lần đầu `RestoreMyMaterialSlots`/`Rst_LoadNextSlot`
  vào canonical `BP_FurnitureActor.md`. Fix race `LoadMeshAsync` vs restore (đường Combo — đường
  `RestoreSnapshot`/Undo-Redo còn treo). 3 bug fix trong phiên: `Bug-RowName-MissingInClipboard`,
  `Bug-RestoreMyMaterialSlots-DeadEndLegacy`, `Bug-LoadMeshAsync-RestoreRace`. Xem
  `07-09-2026_S7G3_Item1-4_Delta.md`.
- 05/09 — S7.G2 ĐÓNG. Việc 5 (Reset Slot/Reset All qua service) PASS. Test tổng G2 7/7 PASS.
  Test 3 đào sâu thêm phát hiện backlog UX (multi-apply tất-cả-hoặc-không), ghi nhận không sửa.
  Sang G3.
- 05/09 — S7.G2 Việc 4 (Copy/Paste chuyển sang Records) PASS. 2 bug thật bắt được: (A) Branch hội
  tụ sai vị trí — ghi đè giá trị đúng; (B) ClipboardMaterialPath không clear đầu hàm — vi phạm
  rule CLEAR class var persistent có sẵn. Xem DELTA_S7G2_Viec4_CopyPaste_AsBuilt_05sep2026.
- 05/09 — S7.G2 Việc 3 (multi-apply Hướng B) PASS 5/5. As-built khớp spec, 1 lệch nhỏ (Cast dùng
  CastFailed thay bSuccess — chấp nhận, xem DELTA_S7G2_Viec2_Viec3_AsBuilt_05sep2026).
  Bug-MaterialPrimaryOnly ĐÓNG.
- 04/09 — S7.G2 Việc 2B (đường khôi phục snapshot) PASS full: 6 bước undo/redo + bonus
  redo-stack case (apply nhánh MỚI sau Undo → Redo đúng nhánh mới, không lẫn state nhánh cũ đã
  cắt). Cặp Việc 2 + 2B (đường ghi + đường ngược) = xương sống G2 đứng vững. Race warning
  `ResetAllSlotsToAssetDefault Mesh không hợp lệ` — vô hại, dời G3 #10.

---

## Canonical pointers (giai đoạn hiện tại)

| Cần gì | Đọc |
|---|---|
| Plan Sprint 7 | `Plans/Sprint7_MaterialEdit_Plan_v1.1.md` |
| Material v1.1 nền (đổi vật liệu đã chạy) | `Features/ChangeMaterial.md` |
| Rule Blueprint (Q8/Q9/L1-L11/bảng node) | `Rules/AI_Implementation_Rules.md` |
| Kỷ luật thực thi + luật doc | `Rules/Execution_Discipline.md` |
| Bug đang mở | `Bugs/Open_Bugs.md` |
| Deviation + ceiling | `DEVIATIONS.md` |

---

## Nguyên tắc đọc doc đầu session (authority-by-question)
> KHÔNG xếp mọi doc trên 1 thang. Xác định LOẠI câu hỏi trước → chọn nguồn:

| AI cần biết | Nguồn thắng |
|---|---|
| Project đang ở đâu? | file này (Session State) |
| Code HIỆN TẠI chạy thế nào? | canonical `Blueprints/` `Widgets/` `Data/` |
| Task đang muốn ĐỔI thành gì? | Task Source (Plan/Delta/Open_Bugs/Feature doc) |
| Constraint/quyết định nào còn phải tuân? | `Rules/` + `DEVIATIONS.md` |
| Vì sao trước đây thành thế này? | `DEVIATIONS.md` / Git |
| Bug nào hiện còn mở? | `Bugs/Open_Bugs.md` |

**Lưu ý authority:** Plan KHÔNG override canonical về *reality hiện tại* — chỉ override về
*intended future work*. Hỏi "code chạy sao" → canonical thắng; hỏi "task định sửa gì" → Plan thắng.

---

## ROUTE ĐỌC TỐI THIỂU KHI NHẬN TASK — [ĐANG PILOT — chưa thành rule chính thức]

Session_State → core Rules + rule của loại task → Architecture_Map → scoped DEVIATIONS/Open_Bugs + rule của vùng → canonical → sprint doc → K2 (chỉ khi doc mờ)

- Architecture_Map = BẢN LỀ: trước Map chỉ nạp global context/ràng buộc vừa đủ để không đi sai; sau Map mới nạp mọi knowledge theo component.
- Đọc-trước (Rules, sau này DEVIATIONS) chỉ QUÉT phần liên quan — không nuốt cả file.
- Map giải RIÊNG bài định tuyến. Không giải: current state (file này lo), ràng buộc (Rules lo), resolution ở đích (canonical/K2 lo). Đủ 4 chân mới ra plan tốt.

Nghiệm thu pilot — chạy 1 task thật rồi soi 3 câu:
(a) AI đọc thừa doc không?
(b) thiếu doc nào khiến plan sai không?
(c) có chỗ nào AI đứng hình, không biết route tiếp đi đâu không?
→ Pilot PASS mới nâng route này thành rule trong `Rules/`. Chưa PASS thì KHÔNG formalize.
