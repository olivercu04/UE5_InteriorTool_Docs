# Session State
> RAM của project. Chỉ trả lời "ĐANG đứng đâu", KHÔNG phải "đã đi qua đâu".
> Lịch sử → Git / PROGRESS.md / DEVIATIONS.md. KHÔNG thêm chronology/changelog vào đây.
> Cập nhật khi trạng thái đổi. Giữ ~50-100 dòng. Cái gì đã có nơi khác sở hữu → cắt, không copy.

**Last verified:** 05/09/2026 (S7.G2 — Bước 0 → Việc 4 PASS. Việc 4 copy/paste: 2 bug thật fix trong phiên. Sẵn sàng Việc 5 reset slot/all)

---

Current: Sprint 7 (Material v1.2) → G2 → Phase EXECUTE | Active task: Việc 5 — Reset Slot/Reset All qua service | Status: chưa bắt đầu
> Giữ đúng 1 dòng. Đổi trạng thái → sửa tại chỗ, không thêm dòng mới.

---

## Đang ở đâu

| | |
|---|---|
| **Nền làm việc** | Project tổng tháng 6 (clone MỚI của master, tích hợp 24/08). Code trực tiếp tại đây. `FurnitureTool_Standalone` chỉ còn vai trò lịch sử/đóng gói cũ. |
| **Phase** | Hướng Gate 2 (bản packaged Shipping thật) |
| **Milestone** | Sprint 7 — Material v1.2 (edit vật liệu runtime) |
| **Current Task** | S7.G2 đang chạy. Bước 0 ✅ · Việc 1 (swatch tên + selection) ✅ · Việc 2 (reroute apply — đường GHI Records) ✅ · Việc 2B (đường khôi phục snapshot — RestoreMyMaterialSlots on-actor + Capture/Restore chụp MaterialSlots trên `S_FurniturePlacement`) ✅ PASS 6 bước undo/redo + bonus redo-stack (04/09) · Việc 3 multi-apply **Hướng B inline** ✅ PASS 5/5 (05/09), đóng `Bug-MaterialPrimaryOnly` · Việc 4 copy/paste ✅ PASS full, 2 bug thật bắt được và fix trong phiên (xem DELTA_S7G2_Viec4). **Resequence per `DELTA_Opus_S7_Resequence`.** Còn lại: Việc 5 reset slot/all → Test tổng G2 |
| **Task Source** | `Sprints/Sprint7/S7G2_Reroute_ExecutionPlan_27aug2026.md` (working plan — mục 0 = trạng thái từng Việc). Plan gốc: `Plans/Sprint7_MaterialEdit_Plan_v1.1.md` mục S7.G2 (v1.8) |
| **Next** | Việc 5 — Reset Slot/Reset All qua service. Chưa bắt đầu. |
| **Blockers** | Không |

Thứ tự tổng tới Gate 2: **Sprint 7 (Material v1.2) → Sprint 6 (Polish UX) → Gate 2**
(sau Gate 2: Backend B0→B5 — cloud, chợ combo)
Lý do S7 trước: integration sớm chính là để G0 kiểm kê material THẬT; luật riêng S7 đã chặn rủi
ro đụng đồ đồng nghiệp.

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
- 03/09 — S7.G2: Việc 1 + Việc 2 (đường ghi Records) PASS. Resequence G2↔G3
  (`DELTA_Opus_S7_Resequence`): đường khôi phục snapshot kéo lên G2 = Việc 2B (GATE undo/redo);
  G3 co lại còn legacy + EMS + Combo. Struct snapshot: `S_FurniturePlacement` (trong
  `BP_UndoManager`) — cuhoang xác nhận 03/09, tên `S_ActorSnapshotData` cũ đã sửa toàn doc.
- 27/08 — S7.G0 ĐÓNG: Q1="ÍT nhưng CÓ Ý NGHĨA" (1,56% mesh trùng slot, review tay xác nhận
  có thật), Q2=DYNAMIC (texture picker, không cần Plan B). MaterialSurvey.h/.cpp compile PASS.

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
