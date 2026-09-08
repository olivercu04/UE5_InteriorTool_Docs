# Session State
> RAM của project. Chỉ trả lời "ĐANG đứng đâu", KHÔNG phải "đã đi qua đâu".
> Lịch sử → Git / PROGRESS.md / DEVIATIONS.md. KHÔNG thêm chronology/changelog vào đây.
> Cập nhật khi trạng thái đổi. Giữ ~50-100 dòng. Cái gì đã có nơi khác sở hữu → cắt, không copy.

**Last verified:** 08/09/2026 (RestoreSnapshot Step 4 fix + regression Undo/Redo PASS. G3 không còn nợ nào. Next: S7.G4)
**Last verified (tiếp):** 08/09/2026 — resequence nửa sau Sprint 7 (Opus). Bản đồ gate G4-G10 thay G4-G8 gốc.
**Last verified (tiếp):** 08/09/2026 — S7.G4 ĐÓNG. Round-trip material theo tên qua save/load PASS (2 slot, reset-rồi-apply-lại đúng tên, không đè nhau). Trục-A xác nhận đứng vững.

---

Current: Sprint 7 (Material v1.2) — G4 ĐÓNG (08/09/2026, xác nhận trục-A PASS). Next: G5 — kéo-thả vật liệu (đường phối màu CHÍNH).
> Giữ đúng 1 dòng. Đổi trạng thái → sửa tại chỗ, không thêm dòng mới.

---

## Đang ở đâu

| | |
|---|---|
| **Nền làm việc** | Project tổng tháng 6 (clone MỚI của master, tích hợp 24/08). Code trực tiếp tại đây. `FurnitureTool_Standalone` chỉ còn vai trò lịch sử/đóng gói cũ. |
| **Phase** | Hướng Gate 2 (bản packaged Shipping thật) |
| **Milestone** | Sprint 7 — Material v1.2 (edit vật liệu runtime) |
| **Current Task** | S7.G4 ĐÓNG (08/09/2026). Round-trip material theo tên qua save/load PASS — xem chi tiết Mục A delta này. Không dùng re-import (lý do đã ghi ở resequence). Sang G5. |
| **Task Source** | `DELTA_Opus_S7_G4-G10_Resequence_08sep2026.md` → mục "Bản đồ gate Sprint 7 — nửa sau" bên dưới. Lịch sử G3: `07-09-2026_S7G3_Item1-4_Delta.md`. G4 ĐÓNG: delta 08/09/2026 (G4-ĐÓNG) |
| **Next** | S7.G5 = kéo-thả vật liệu (đường phối màu CHÍNH). Mở màn bằng [VERIFY G5.0] — vertical slice trace-on-drop (xem `DELTA_Opus_S7_G4-G10_Resequence_08sep2026.md` mục G5). KHÔNG dựng gì trước khi verify xong. |
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

**G4 ĐÓNG 08/09/2026 — PASS.**

---

## Việc tiếp theo (chưa làm)

1. **Next: G5** — bắt đầu bằng [VERIFY G5.0] trace-on-drop (Print tạm trong On Drop/On Drag Over
   hiện có của mesh, KHÔNG dựng gì mới trước khi có kết quả).
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

- 08/09 — RestoreSnapshot Step 4 (BP_UndoManager) gỡ Call RestoreMyMaterialSlots thừa. Test
  regression Undo/Redo material PASS. Bug-LoadMeshAsync-RestoreRace đóng hoàn toàn (cả đường
  Combo lẫn RestoreSnapshot/Undo-Redo).
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
