# Session State
> RAM của project. Chỉ trả lời "ĐANG đứng đâu", KHÔNG phải "đã đi qua đâu".
> Lịch sử → Git / PROGRESS.md / DEVIATIONS.md. KHÔNG thêm chronology/changelog vào đây.
> Cập nhật khi trạng thái đổi. Giữ ~50-100 dòng. Cái gì đã có nơi khác sở hữu → cắt, không copy.

**Last verified:** 08/09/2026 (RestoreSnapshot Step 4 fix + regression Undo/Redo PASS. G3 không còn nợ nào. Next: S7.G4)
**Last verified (tiếp):** 08/09/2026 — resequence nửa sau Sprint 7 (Opus). Bản đồ gate G4-G10 thay G4-G8 gốc.
**Last verified (tiếp):** 08/09/2026 — S7.G4 ĐÓNG. Round-trip material theo tên qua save/load PASS (2 slot, reset-rồi-apply-lại đúng tên, không đè nhau). Trục-A xác nhận đứng vững.
**Last verified (tiếp):** 08/09/2026 — Opus giao task card G5 (kéo-thả material) + G6 (click-vào-mesh chọn slot). [VERIFY G5.0] trace-on-drop đã PASS 3/3 (Sonnet). Đánh đổi phạm vi kéo-thả (Hướng A — áp 1 slot dưới con trỏ, không đọc SelectedActors) đã CHỐT. Chờ Sonnet execute G5.1.
**Last verified (tiếp):** 12/09/2026 — S7.G6 ĐÓNG HẲN. G6.1 (`NotifyViewportSlotClick` + `HighlightSwatchByIndex`) 6/6 PASS. G6.2 regression 8/8 PASS. Hook đặt ở `OnLMBReleased` (không phải Event Tick như plan gốc).
**Last verified (tiếp):** 14/09/2026 — S7.G7.0a (SpikeGate InteriorColorPicker) ĐÓNG — **GO (PASS)**. 3 primitive Slate (`SColorWheel`+`SSimpleGradient`+`SSlider`) sống trong packaged Shipping, 10/10 case PASS, build ExitCode=0. Fallback Đ5 (preset swatch) không dùng tới. Mở G7.1.
**Last verified (tiếp):** 15/09/2026 — Plugin copy về `Lighting_Mnger` DONE, build sạch, PIE chạy được. Opus giao execution plan S7G7T1-T5 (chỉ T1 có C++ mới). Đ5 đóng dấu `[HISTORICAL — OVERRIDE]`.
**Last verified (tiếp):** 15/09/2026 — S7G7T1 ĐÓNG — PASS 4/4. `GetControlsForMaterial`+`DT_MaterialParamMap` chạy đúng, so CON TRỎ base material (không path string, FAIL với MID).
**Last verified (tiếp):** 15/09/2026 — S7G7T2 ĐÓNG — PASS. `WBP_ParamScalarRow`+`WBP_ParamColorRow` xong, +`HexToLinearColor` (C++). `Bug-MaterialSlots-MissingInClipboard` cũng đóng trong ngày (ngoài Sprint 7).
**Last verified (tiếp):** 17/09/2026 — S7G7T3 **ĐANG DỞ**, KHÔNG ĐÓNG. T3.1 (`WBP_MaterialParamPanel`) PASS, T3.2 (`WBP_MaterialInspector`) PASS. T3.3 (`RefreshParamPanel`, tích hợp vào `WBP_FurnitureInventory`) đang xây: nhánh Scalar built-chưa-verify-test, nhánh Color chưa build, phần đầu hàm chưa as-built.
**Last verified (tiếp):** 18/09/2026 — **S7G7T3.3 + T3.4 PASS.** `RefreshParamPanel()` build đầy đủ + lifecycle Inspector + 5 seam APPEND (seam #5 sửa vị trí so với task card rev6) + vá lỗ hổng đường kéo-thả material. Treo mới: `Bug-MaterialEdit-EnableState` [OPEN].

---

Current: Sprint 7 (Material v1.2, 6/10 gate) — S7G7T3.3+T3.4 PASS (18/09/2026). Next: T4 (4 delegate handler thật) + seam #6/#7 (T4b) + fix Bug-MaterialEdit-EnableState
> Giữ đúng 1 dòng. Đổi trạng thái → sửa tại chỗ, không thêm dòng mới.

---

## Đang ở đâu

| | |
|---|---|
| **Nền làm việc** | Project tổng tháng 6 (clone MỚI của master, tích hợp 24/08). Code trực tiếp tại đây. `FurnitureTool_Standalone` chỉ còn vai trò lịch sử/đóng gói cũ. |
| **Phase** | Hướng Gate 2 (bản packaged Shipping thật) |
| **Milestone** | Sprint 7 — Material v1.2 (edit vật liệu runtime) |
| **Current Task** | **S7G7T3.3 + T3.4 PASS (18/09/2026).** `RefreshParamPanel()` build đầy đủ (nhánh Scalar+Color, fallback MID, empty-state, bounds) + lifecycle Inspector (Construct/Destruct/Open/Close) + 5 seam APPEND + vá lỗ hổng đường kéo-thả material (`BP_FurnitureActor.ApplyMaterialByRowName`). Xem `Widgets/WBP_FurnitureInventory.md` mục "S7G7T3", `Blueprints/BP_FurnitureActor.md` v2.5. |
| **Task Source** | `Sprints/Sprint7/18-09-2026_S7G7_T3-T4_ASBUILT_delta.md` (Sonnet, 18/09/2026). Task card gốc: `Sprints/Sprint7/17-09-2026_S7G7_T3-T5_TaskCards_v6.md` (3 chỗ `[HISTORICAL]` — SAI so với as-built, xem banner đầu file đó). |
| **Next** | **T4** — thân thật cho 4 delegate handler rỗng (`Handle_ScalarPreview`/`Handle_ScalarCommit`/2 handler Color) + `Handle_ResetParamsRequested` thật (đang stub). **T4b** — seam #6 (`OnSceneRestored`)/#7 (`EndParamSession`, hàm chưa tồn tại). Song song: debug `Bug-MaterialEdit-EnableState` (Print A đầu phiên, xem `Bugs/Open_Bugs.md`). |
| **Blockers** | `Bug-MaterialEdit-EnableState` [OPEN, 🟡] — nghi seam #3 không chạy khi actor chọn trước lúc đổi tab Material. Không chặn merge doc, nhưng chặn coi seam #1/#2/#3 là đóng hẳn. (S7G7T0 sub-phần G7.0b compat 5.6/5.7/5.8 chưa chạy — KHÔNG chặn T4, tách backlog riêng) |

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

**G4 ĐÓNG 08/09/2026 — PASS. G5 ĐÓNG 11/09/2026 — PASS (G5.1-G5.4, regression 8/8). G6 ĐÓNG 12/09/2026 — PASS (G6.1 6/6, G6.2 regression 8/8). G7.0a (SpikeGate) ĐÓNG 14/09/2026 — GO (10/10 case, PIE+Dev+Shipping). G7.1 (integration) chưa chạy.**

### G7 — breakdown task (chuẩn `S{sprint}G{gate}T{task}`, thêm 14/09/2026)
> Sprint 7 = 10 gate (G1-G10; G1-G3 đã ĐÓNG trước 08/09, không lặp ở bảng trên). G7 tự nó có
> nhiều bước con, cần track riêng — dùng ID `S7G7T0`..`S7G7T5`. Xem `Rules/Execution_Discipline.md`
> mục R-DOC-TASKID. Nguồn G7.1-G7.5: `Sprints/Sprint7/14-09-2026_G7.0_SpikeGate_TaskCard.md` mục 9.

| Task ID | Tên | Trạng thái |
|---|---|---|
| **S7G7T0** | SpikeGate `InteriorColorPicker` (viability 3 primitive Slate) | ĐÓNG — GO (14/09). Plugin copy về `Lighting_Mnger` DONE (15/09). Sub G7.0b (compat 5.6/5.7/5.8) chưa chạy — backlog, không chặn T1. |
| **S7G7T1** | `DT_MaterialParamMap` (row struct C++) + `GetControlsForMaterial` helper — **task DUY NHẤT có C++ mới trong T1-T5** | ĐÓNG — PASS 4/4 (15/09). So con trỏ base material (không path). |
| **S7G7T2** | `WBP_ParamScalarRow` + `WBP_ParamColorRow` (nhúng `UInteriorColorPickerWidget`) | ĐÓNG — PASS toàn bộ (15/09). +`HexToLinearColor` (C++). |
| **S7G7T3** | `WBP_MaterialParamPanel` (T3.1) + `WBP_MaterialInspector` (T3.2) + tích hợp `RefreshParamPanel`+lifecycle+5 seam (T3.3+T3.4) | **ĐÓNG — PASS (18/09).** T3.1/T3.2/T3.3/T3.4 đều PASS. Treo: `Bug-MaterialEdit-EnableState` [OPEN] không chặn merge doc nhưng chặn coi seam #1/#2/#3 đóng hẳn. |
| **S7G7T4** | ⭐ Thân thật 4 delegate handler (Scalar/Color Preview+Commit) → `MaterialSlotService` (SetSlotParam, MID-on-demand, debounce 1 snapshot/lần nhả) — **INTEGRATION GATE**, rủi ro cao nhất còn lại. Gồm **T4b** con (seam #6/#7, `EndParamSession`/`ParamSession_*` trên `BP_UndoManager` — ranh giới Undo session khi đổi selection). | Chưa bắt đầu |
| **S7G7T5** | Multi-select áp param cả cụm theo SlotName/ParamName + test từ điển tạm 2 dòng | Chưa bắt đầu |

Plan T1-T5 (PLAN, chưa as-built): `Sprints/Sprint7/15-09-2026_S7G7_T1-T5_ExecutionPlan.md`. Task
card T3·T4·T4b·T5 (rev6, PLAN — 3 chỗ `[HISTORICAL]` sau as-built 18/09, xem banner đầu file):
`Sprints/Sprint7/17-09-2026_S7G7_T3-T5_TaskCards_v6.md`.
**T2-T5 KHÔNG viết C++ mới** — chỉ nối UMG vào `UMaterialSlotService` (14 hàm, G1 PASS) có sẵn;
undo T4 tái dùng `CaptureSnapshot`/`ApplyParamsJsonToSlot` (Đ11), không cần đường undo riêng.
T4 mà live-preview/undo không vững → **DỪNG, báo cuhoang, KHÔNG cắt sang T5.**

**Next thật sự:** **T4** (thân thật 4 delegate handler) song song debug `Bug-MaterialEdit-EnableState`.
S7G7T3 ĐÓNG 18/09 — PASS toàn bộ T3.1-T3.4.

---

## Việc tiếp theo (chưa làm)

1. **Next: T4** — thân thật cho 4 delegate handler rỗng (`Handle_ScalarPreview`/`Handle_ScalarCommit`/
   2 handler Color) → nối `MaterialSlotService` (SetSlotParam, MID-on-demand, debounce). S7G7T3
   (T3.1-T3.4) ĐÓNG 18/09.
2. **Debug `Bug-MaterialEdit-EnableState`** [OPEN, 🟡] song song T4 — Print A tại
   `SwitchInventoryMode` để xác định seam #3 có chạy không. Xem `Bugs/Open_Bugs.md`.
3. **T4b** (seam #6/#7 — `OnSceneRestored`/`EndParamSession`) sau T4. **T4** là integration gate
   rủi ro cao nhất còn lại của G7 — dừng báo cuhoang nếu live-preview/undo không vững, không cắt
   sang T5.
4. **G7.0b** (compat UE 5.6/5.7/5.8) — chưa chạy, backlog riêng, không chặn T4.
5. **(Tùy chọn, không khẩn) Dọn `SaveComboFromSelection` Bước 5d** — xóa loop tính
   `MaterialOverrides_SaveCombo` (dư thừa, không ai đọc ở combo mới) — chỉ làm khi có thời gian
   rảnh, không phải ưu tiên.

---

## Active bugs relevant now
> Chỉ bug đang CHẶN việc hiện tại. Danh sách đầy đủ → `Bugs/Open_Bugs.md`.

- **Bug-ComboRoot-MixedLooseGroup** 🔴 — chặn ĐẦU SPRINT 6 (không phải Sprint 7). Chạm kiến trúc
  combo: `SaveComboFromSelection` nên LUÔN tạo 1 wrapper root group. Ghi ở đây để không quên khi
  Sprint 7 xong chuyển sang Sprint 6. `Bugs/Open_Bugs.md`.
- **Bug-MaterialEdit-EnableState** 🟡 — `BTN_MaterialEdit` vẫn bấm được dù chưa chọn slot. Nghi
  seam #3 (`OnMeshSelected`) không chạy khi actor chọn trước lúc đổi tab Material. Không chặn T4,
  nhưng chặn coi seam #1/#2/#3 đóng hẳn. Bước tiếp theo: Print A. `Bugs/Open_Bugs.md`.

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

- 18/09 — **S7G7T3.3 + T3.4 PASS.** `RefreshParamPanel()` build đầy đủ (Scalar+Color, fallback MID,
  empty-state, bounds) + lifecycle Inspector (Construct/Destruct/Open/Close, dùng `Set Background
  Color` — task card rev6 ghi nhầm `SetHighlight`) + 5 seam APPEND (seam #5 sửa vị trí: CUỐI nhánh
  Material, không phải ĐẦU hàm như rev6) + vá lỗ hổng đường kéo-thả material
  (`BP_FurnitureActor.ApplyMaterialByRowName` X3). Bug mới `Bug-MaterialEdit-EnableState` [OPEN].
  Next: T4 (4 delegate handler thật). Xem `Widgets/WBP_FurnitureInventory.md` mục "S7G7T3".
- 17/09 — **S7G7T3 ĐANG DỞ, KHÔNG ĐÓNG.** T3.1 `WBP_MaterialParamPanel` (tạo mới, cuhoang xác
  nhận chưa từng build trước đó) PASS + T3.2 `WBP_MaterialInspector` PASS 7/7 (2 widget mới).
- 15/09 (tiếp 2) — **S7G7T2 ĐÓNG — PASS toàn bộ.** `WBP_ParamScalarRow`+`WBP_ParamColorRow` +
  `HexToLinearColor` (C++). 2 bug fix (SpinBox init, dead-end OnPreviewChanged) + 3 quyết định
  kiến trúc (`CurrentColor` single-source-of-truth, bỏ preset tĩnh, hex-error chỉ revert). Cùng
  ngày: `Bug-MaterialSlots-MissingInClipboard` đóng (ngoài Sprint 7), `SpawnFurnitureCopy` viết lại
  theo K2Node thật.
- 15/09 (tiếp) — **S7G7T1 ĐÓNG — PASS 4/4.** `GetControlsForMaterial`+`DT_MaterialParamMap` (class
  riêng `UMaterialParamMap`, KHÔNG nhét vào `MaterialSlotService`). Chốt so CON TRỎ base material
  (path string FAIL với MID). Xem `Data/MaterialSlotService_Reference.md`.
- 15/09 — Plugin `InteriorColorPicker` copy về `Lighting_Mnger` xong (build sạch, PIE chạy được).
  Opus giao execution plan **S7G7T1-T5** (Material Param Panel) — chỉ T1 có C++ mới
  (`DT_MaterialParamMap`+`GetControlsForMaterial`), T2-T5 thuần wiring UMG vào
  `UMaterialSlotService` có sẵn. Đ5 (fallback preset swatch) đóng dấu `[HISTORICAL — OVERRIDE]` —
  bánh xe màu là control chính. Xem `Sprints/Sprint7/15-09-2026_S7G7_T1-T5_ExecutionPlan.md`.
  ở project standalone riêng (né precompiled-manifest lỗi kiểu Gate 1.5). Xem
  `Widgets/InteriorColorPicker.md`, `DEVIATIONS.md`.

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
