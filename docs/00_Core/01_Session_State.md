# Session State
> RAM của project. Chỉ trả lời "ĐANG đứng đâu", KHÔNG phải "đã đi qua đâu".
> Lịch sử → Git / PROGRESS.md / DEVIATIONS.md. KHÔNG thêm chronology/changelog vào đây.
> Cập nhật khi trạng thái đổi. Giữ ~50-100 dòng. Cái gì đã có nơi khác sở hữu → cắt, không copy.

**Last verified:** 27/08/2026 (S7.G1 ĐÓNG — 5/5 Việc PASS, không deviation. Sang G2)

---

Current: Sprint 7 (Material v1.2) → G2 (reroute UI → MaterialSlotService) → Phase VERIFY | Active task: viết Blueprint node G2 đầu tiên — RefreshSlotSwatches (thêm SET SlotName vào từng swatch) | Status: mid-VERIFY, 8 vòng K2 cross-check xong, CHƯA viết node
> Giữ đúng 1 dòng. Đổi trạng thái → sửa tại chỗ, không thêm dòng mới.

---

## Đang ở đâu

| | |
|---|---|
| **Nền làm việc** | Project tổng tháng 6 (clone MỚI của master, tích hợp 24/08). Code trực tiếp tại đây. `FurnitureTool_Standalone` chỉ còn vai trò lịch sử/đóng gói cũ. |
| **Phase** | Hướng Gate 2 (bản packaged Shipping thật) |
| **Milestone** | Sprint 7 — Material v1.2 (edit vật liệu runtime) |
| **Current Task** | S7.G1 ĐÓNG (5/5 Việc PASS, không deviation). Sang S7.G2 — reroute UI vào MaterialSlotService: RefreshSlotSwatches (SET SlotName/SelectedSlotName/SelectedSlotIndex), LoadAndApplyMaterial (gọi ApplyLoadedMaterialToSlot, bỏ CreateDMI/SetArrayElem rời rạc), Multi-apply E1 (fix Bug-MaterialPrimaryOnly), Copy/Paste material, Reset Slot/Reset All (ClearSlotParams mức 1 / ResetSlotToAssetDefault mức 2) |
| **Task Source** | `Plans/Sprint7_MaterialEdit_Plan_v1.1.md` mục S7.G2 (nội dung bump v1.5) |
| **Next** | S7.G2 — [VERIFY] WBP_SlotSwatch variables hiện có + LoadAndApplyMaterial bản mới nhất trước khi sửa (plan đã ghi rõ) |
| **Blockers** | Không |

Thứ tự tổng tới Gate 2: **Sprint 7 (Material v1.2) → Sprint 6 (Polish UX) → Gate 2**
(sau Gate 2: Backend B0→B5 — cloud, chợ combo)
Lý do S7 trước: integration sớm chính là để G0 kiểm kê material THẬT; luật riêng S7 đã chặn rủi
ro đụng đồ đồng nghiệp.

---

## Active bugs relevant now
> Chỉ bug đang CHẶN việc hiện tại. Danh sách đầy đủ → `Bugs/Open_Bugs.md`.

- **Bug-MaterialPrimaryOnly** 🟡 — CHẶN THẲNG Sprint 7: đổi vật liệu khi chọn cả cụm combo chỉ áp
  cho 1 mesh (Primary), không toast. Vá thật = chính phần multi-apply (E1) của Sprint 7 Material
  Edit — fix TRONG Sprint 7, không làm lẻ. `Bugs/Open_Bugs.md`.
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

- 27/08 (tiếp) — G0 DONE toàn phần (a/b/c/d, kể cả collision). G5 hướng chốt: hybrid
  click-to-select (trace FaceIndex) + chips phụ (Fable duyệt). G1 task card đã phát hành.
- 27/08 — S7.G0 ĐÓNG: Q1="ÍT nhưng CÓ Ý NGHĨA" (1,56% mesh trùng slot, review tay xác nhận
  có thật), Q2=DYNAMIC (texture picker, không cần Plan B). MaterialSurvey.h/.cpp compile PASS.
- 25/08 — Bug-MaterialSkip-Cook FIXED + Bug-CookFail-10Errors FIXED → cook BUILD SUCCESSFUL,
  apply material Stone/Concrete/Fabric verify PASS trên `.exe`.
- 24/08 (integration) — Bug-CameraSpeed-ShiftConsumed FIXED (`IA_Shift` tắt Consume Lower
  Priority); RMB flow verified qua K2Node export.
- 24/08 — Integration project tổng tháng 6 hoàn tất (thay `FurnitureTool_Standalone` làm nền
  làm việc chính).

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
