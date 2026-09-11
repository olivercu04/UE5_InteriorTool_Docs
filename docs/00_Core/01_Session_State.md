# Session State
> RAM của project. Chỉ trả lời "ĐANG đứng đâu", KHÔNG phải "đã đi qua đâu".
> Lịch sử → Git / PROGRESS.md / DEVIATIONS.md. KHÔNG thêm chronology/changelog vào đây.
> Cập nhật khi trạng thái đổi. Giữ ~50-100 dòng. Cái gì đã có nơi khác sở hữu → cắt, không copy.

**Last verified:** 08/09/2026 (RestoreSnapshot Step 4 fix + regression Undo/Redo PASS. G3 không còn nợ nào. Next: S7.G4)
**Last verified (tiếp):** 08/09/2026 — resequence nửa sau Sprint 7 (Opus). Bản đồ gate G4-G10 thay G4-G8 gốc.
**Last verified (tiếp):** 08/09/2026 — S7.G4 ĐÓNG. Round-trip material theo tên qua save/load PASS (2 slot, reset-rồi-apply-lại đúng tên, không đè nhau). Trục-A xác nhận đứng vững.
**Last verified (tiếp):** 08/09/2026 — Opus giao task card G5 (kéo-thả material) + G6 (click-vào-mesh chọn slot). [VERIFY G5.0] trace-on-drop đã PASS 3/3 (Sonnet). Đánh đổi phạm vi kéo-thả (Hướng A — áp 1 slot dưới con trỏ, không đọc SelectedActors) đã CHỐT. Chờ Sonnet execute G5.1.

---

Current: Sprint 7 (Material v1.2) — S7.G5 ĐÓNG (G5.1-G5.4 xong, regression 8/8 PASS) — chờ G6.0
> Giữ đúng 1 dòng. Đổi trạng thái → sửa tại chỗ, không thêm dòng mới.

---

## Đang ở đâu

| | |
|---|---|
| **Nền làm việc** | Project tổng tháng 6 (clone MỚI của master, tích hợp 24/08). Code trực tiếp tại đây. `FurnitureTool_Standalone` chỉ còn vai trò lịch sử/đóng gói cũ. |
| **Phase** | Hướng Gate 2 (bản packaged Shipping thật) |
| **Milestone** | Sprint 7 — Material v1.2 (edit vật liệu runtime) |
| **Current Task** | S7.G5 (kéo-thả vật liệu) — ĐÓNG HẲN 11/09/2026. G5.4 (dọn debug scaffolding + regression) đã xong sau lần merge trước. Code sạch, không còn scaffolding debug nào trong `WBP_MaterialCard` / `BP_FurnitureActor` / `WBP_DragOverlay`. |
| **Task Source** | `11-09-2026_S7G5_G5.4_AsBuilt_Addendum.md` (as-built G5.4 + bug #5). As-built G5.1-G5.3: `11-09-2026_S7G5_G5.1-G5.3_AsBuilt_Delta.md`. Plan gốc: `DELTA_Opus_S7_G5-G6_ExecutionPlan_08sep2026.md`. G4 ĐÓNG: `DELTA_Opus_S7_G4-G10_Resequence_08sep2026.md` phần G4-ĐÓNG (08/09) |
| **Next** | G6.0 — VERIFY click resolution (K2Node export thật của `BP_FurnitureInputManager` Event Tick). Xem `DELTA_Opus_S7_G5-G6_ExecutionPlan_08sep2026.md` mục 5. |
| **Blockers** | Không |

Thứ tự tổng tới Gate 2: **Sprint 7 (Material v1.2) → Sprint 6 (Polish UX) → Gate 2**
(sau Gate 2: Backend B0→B5 — cloud, chợ combo)
Lý do S7 trước: integration sớm chính là để G0 kiểm kê material THẬT; luật riêng S7 đã chặn rủi
ro đụng đồ đồng nghiệp.

---

## Bản đồ gate Sprint 7 — nửa sau (G4-G10, resequence 08/09/2026)
> Thay bản đồ G4-G8 gốc (05/07, chưa rà) — xem `DELTA_Opus_S7_G4-G10_Resequence_08sep2026.md`.
> Đang thực thi, G4 đã đóng — xem tiến độ tại "Đang ở đâu" phía trên. Bản gốc đóng dấu
> [HISTORICAL] trong `Plans/Sprint7_MaterialEdit_Plan_v1.1.md`, không xóa.

| Gate | Tên | Rủi ro | Test bằng | Ước lượng |
|---|---|---|---|---|
| **G4** | Xác nhận trục-A (chips/swatch đã có) | Thấp | Save/Load + mắt | ~1 buổi |
| **G5** | Kéo-thả vật liệu (đường phối màu CHÍNH) | **Cao** (có [VERIFY] trace-on-drop) | Print → mắt | ~3-4 buổi |
| **G6** | Click-vào-mesh chọn slot (đường phụ "thử nhiều lần") | Trung bình (Q9 luồng click) | Print → mắt | ~2-3 buổi |
| **G7** | Động cơ panel param (slider/color) + từ điển TẠM | Trung bình | Từ điển tạm 2 dòng | ~3-4 buổi |
| **G8** | Điền từ điển thật (23 họ master) + nhãn Việt | Thấp-TB (dữ liệu, không logic) | Bộ test T7 | ~2-3 buổi |
| **G9** | Pattern gạch (texture) + đóng Đ12 texture restore | Trung bình | Mắt | ~2 buổi |
| **G10** | Regression tổng + VRAM + docs | Thấp | Chuỗi 12 bước | ~1-2 buổi |

**G4 ĐÓNG 08/09/2026 — PASS. G5 ĐÓNG 11/09/2026 — PASS (G5.1-G5.4, regression 8/8).**

---

## Việc tiếp theo (chưa làm)

1. **Next: G6.0** — VERIFY click resolution (K2Node export thật của `BP_FurnitureInputManager`
   Event Tick). Xem `DELTA_Opus_S7_G5-G6_ExecutionPlan_08sep2026.md` mục 5. G5 ĐÓNG HẲN (11/09).
2. **(Tùy chọn, không khẩn) Dọn `SaveComboFromSelection` Bước 5d** — xóa loop tính
   `MaterialOverrides_SaveCombo` (dư thừa, không ai đọc ở combo mới) — chỉ làm khi có thời gian
   rảnh, không phải ưu tiên.

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

- 11/09 (tiếp) — S7.G5.4 xong: dọn 3 chỗ debug scaffolding, regression 8/8 PASS. Phát hiện thêm
  1 gap (kéo-thả material thiếu AddRecentMaterial) — đã fix + verify. GATE G5 ĐÓNG HẲN.
- 11/09 — S7.G5.1-G5.3 ĐÓNG. Nguồn kéo (BP_DragDropOperation_Material) + engine on-actor
  (ApplyMaterialByRowName) + router (WBP_DragOverlay.On Drop nhánh material) chạy đúng end-to-end.
  4 bug thật tìm+fix trong phiên (xem DEVIATIONS.md mục SPRINT 7 11/09). Còn nợ G5.4 (dọn debug +
  regression 8 case).
- 08/09 — Opus giao task card G5+G6 (`DELTA_Opus_S7_G5-G6_ExecutionPlan_08sep2026.md`). [VERIFY
  G5.0] trace-on-drop PASS 3/3 — phát hiện deviation `TraceSlotUnderCursor` cần thêm param
  `ScreenPosition` (Slate drag giữ quyền input chuột, PC không tự deproject được). Đánh đổi phạm
  vi kéo-thả Hướng A chốt (áp 1 slot dưới con trỏ, không đọc SelectedActors). Chờ execute G5.1.
- 08/09 — S7.G4 ĐÓNG. Round-trip material theo tên qua save/load PASS (2 slot, reset-rồi-apply-lại
  đúng tên, không đè nhau). Trục-A xác nhận đứng vững. Sang G5.
- 08/09 — RestoreSnapshot Step 4 (BP_UndoManager) gỡ Call RestoreMyMaterialSlots thừa. Test
  regression Undo/Redo material PASS. Bug-LoadMeshAsync-RestoreRace đóng hoàn toàn (cả đường
  Combo lẫn RestoreSnapshot/Undo-Redo).

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
