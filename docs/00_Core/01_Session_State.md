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
**Last verified (tiếp):** 18/09/2026 (cùng ngày) — **Đóng `Bug-MaterialEdit-EnableState`.** Root cause thật khác nghi vấn ban đầu (seam #3 chạy đúng) — 2 lỗi "entry point cũ không rà lại": `RefreshSlotSwatches` thiếu `HighlightSwatchByIndex`, `BTN_ResetSlot`/`BTN_ResetAll` thiếu `RefreshParamPanel`. Fix+test PASS cả 3 chỗ (xem `WBP_FurnitureInventory.md` v3.31). Sinh rule mới `AI_Implementation_Rules.md` Q10 — FLOW COVERAGE GATE (Cross-Flow Impact Audit), đặt trước Q9. Không còn nợ nào chặn G7 trước T4.
**Last verified (tiếp):** 18/09/2026 (tiếp 2) — **S7G7T4 GATE ĐÓNG — PASS.** 5 handler thật (`Handle_ScalarPreview`/`Commit`, `Handle_ColorPreview`/`Commit`, `Handle_ResetParamsRequested`) nối `MaterialSlotService`; live-preview + undo/redo VALUE PASS. Dispatcher 2 row nâng 2-input `(ParamName,Value)` (row v1.1). Bug B3 (sót wire ParamName → preview màu hỏng ngầm) fix. **Giới hạn Hướng 1 chốt:** undo mất slot-highlight (Undo=destroy+respawn actor) — `Bug-ParamUndo-SlotContextLost` backlog, `DEVIATIONS.md`. cuhoang chốt: **phiên sau đập-xây-lại hệ undo (Hướng 3)** — ưu tiên cao. Doc T4 đã merge canonical (WBP_FurnitureInventory v3.32, 2 row v1.1, DEVIATIONS, Open_Bugs).

**Last verified (tiếp):** 18/09/2026 (tiếp 3) — **Kiến trúc Undo mới CHỐT** sau phiên họp 3 bên (cuhoang ↔ Opus 5 ↔ ChatGPT, 5 vòng brief). 6 trụ A-F (Identity+Resolver · Typed History · Mutation Boundary · ChangeSet · Reversible Snapshot · Interaction≠Document State) + Interactive Edit Session (giải live-preview slider) + migration policy additive→parity→subtractive. Doc: `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md` (PLAN, chưa as-built). Backup toàn project + git plugin FurnitureToolkit làm trước khi đụng code (đường lùi — project chưa có git). `S7G7T4b` xác định **absorbed by architecture** (Interactive Edit Session tự sinh đúng 1 command lúc Commit, thay coalescing thủ công).
**Last verified (tiếp):** 21/09/2026 — **T0 (Automation Harness Gate) ĐÓNG — PASS.** File test đầu tiên `Plugins/FurnitureToolkit/Source/FurnitureToolkit/Private/Tests/FurnitureToolkitTests.cpp` chạy qua `Tools → Session Frontend → tab Automation` (đường bấm thật UE5.5, khác doc gốc đoán). `[UNDO-T0-01]` xanh, `[UNDO-T0-02]` (negative control) đỏ đúng ở lần chạy đầu → sửa lại → xanh lần 2. `Rules/Testing.md` MỚI TẠO (3 tầng verification + luật ngân sách PIE + protocol RED/GREEN). `AI_Implementation_Rules.md` v2.21 ghi API đã xác nhận. Next: **U1 — Persistent Identity + Resolver**.

--- hôm này là ngày thứ 6, sau vài ngày mưa tầm tã, hôm nay là ngày đẹp trời

Current: Sprint 7 tạm DỪNG ở G7 — đang xây **Undo Architecture Foundation** (T0→U1→U2→U3, xem `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md`). **T0 ĐÓNG 21/09/2026.** Next: **U1 — Persistent Identity + Resolver** (§7 trong doc kiến trúc). Sau U1→U2→U3 mới quay lại Sprint 7 G8/G9/G10.
> Giữ đúng 1 dòng. Đổi trạng thái → sửa tại chỗ, không thêm dòng mới.

---

## Đang ở đâu

| | |
|---|---|
| **Nền làm việc** | Project tổng tháng 6 (clone MỚI của master, tích hợp 24/08). Code trực tiếp tại đây. `FurnitureTool_Standalone` chỉ còn vai trò lịch sử/đóng gói cũ. |
| **Phase** | Hướng Gate 2 (bản packaged Shipping thật) — **tạm rẽ nhánh xây Undo Architecture Foundation trước khi quay lại Sprint 7** |
| **Milestone** | Undo Architecture Foundation (T0→U1→U2→U3) — chuẩn bị nền cho Sprint 7 G8-G10 + mọi continuous-edit sau này (transform gizmo...) |
| **Current Task** | **T0 (Automation Harness Gate) ĐÓNG — PASS (21/09/2026).** Harness test C++ chạy thật, xác nhận qua RED→GREEN. Xem `Rules/Testing.md` (mới), `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md` §8. |
| **Task Source** | `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md` (delta, chưa merge canonical — merge từng phần khi mỗi gate as-built). |
| **Next** | **U1 — Persistent Identity + Resolver** (doc kiến trúc §7, gate map). Câu hỏi nhị phân đóng gate: sau undo scene, `Resolve(ID cũ)` có ra đúng actor mới không? Bao gồm cả đường save cũ (`UNDO-ID-06/07`). Sau U1 mới sang U2 (History/Mutation Boundary) → U3 (Context/ChangeSet) → quay lại Sprint 7 G8-G10. |
| **Blockers** | Không. Sprint 7 G8-G10 **tạm hoãn có chủ đích** (không phải bị chặn) — chờ nền Undo mới xong để tránh xây thêm trên kiến trúc sắp thay. `Bug-ParamUndo-SlotContextLost` đóng khi U3 PASS. `S7G7T4b` đã xác định **absorbed by architecture**, không còn là task riêng. |

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
| **S7G7T3** | `WBP_MaterialParamPanel` (T3.1) + `WBP_MaterialInspector` (T3.2) + tích hợp `RefreshParamPanel`+lifecycle+5 seam (T3.3+T3.4) | **ĐÓNG HẲN — PASS (18/09).** T3.1/T3.2/T3.3/T3.4 đều PASS. `Bug-MaterialEdit-EnableState` cũng ĐÓNG cùng ngày — seam #1/#2/#3 coi như đóng hẳn. |
| **S7G7T4** | ⭐ Thân thật 4 delegate handler (Scalar/Color Preview+Commit) + `Handle_ResetParamsRequested` → `MaterialSlotService`. **INTEGRATION GATE.** | **ĐÓNG — PASS (18/09).** Live-preview + undo/redo VALUE đúng. Dispatcher 2-input `(ParamName,Value)`. Lộ giới hạn Hướng 1 (mất slot-context sau undo, chấp nhận). seam #6 DONE. seam #7 (`EndParamSession`) tách sang T4b. |
| **S7G7T4b** | Coalescing undo (gộp nhiều lần kéo→1 entry) + `EndParamSession`/`ParamSession_*` trên `BP_UndoManager` (ranh giới Undo session khi đổi selection). | Chưa bắt đầu. **LƯU Ý:** phiên redesign undo (Hướng 3) đi TRƯỚC — có thể đổi cả cách tiếp cận T4b. |
| **S7G7T5** | Multi-select áp param cả cụm theo SlotName/ParamName + test từ điển tạm 2 dòng | Chưa bắt đầu |

Plan T1-T5 (PLAN, chưa as-built): `Sprints/Sprint7/15-09-2026_S7G7_T1-T5_ExecutionPlan.md`. Task
card T3·T4·T4b·T5 (rev6, PLAN — 3 chỗ `[HISTORICAL]` sau as-built 18/09, xem banner đầu file):
`Sprints/Sprint7/17-09-2026_S7G7_T3-T5_TaskCards_v6.md`.
**T2-T5 KHÔNG viết C++ mới** — chỉ nối UMG vào `UMaterialSlotService` (14 hàm, G1 PASS) có sẵn;
undo T4 tái dùng `CaptureSnapshot`/`ApplyParamsJsonToSlot` (Đ11), không cần đường undo riêng.
T4 mà live-preview/undo không vững → **DỪNG, báo cuhoang, KHÔNG cắt sang T5.**

**Next thật sự:** **Phiên mới — redesign undo (Hướng 3)** [cuhoang chốt ưu tiên], rồi T4b + T5.
S7G7T4 GATE ĐÓNG 18/09 — 5 handler PASS, live-preview + undo VALUE đúng. Giới hạn slot-context
sau undo = lý do làm Hướng 3 trước.

---

## Việc tiếp theo (chưa làm)

1. **[ƯU TIÊN] Phiên mới — REDESIGN UNDO (Hướng 3).** Param-undo riêng (command-pattern old/new
   value per slot-param), KHÔNG đi qua full scene snapshot. Mục tiêu: undo param → đảo đúng 1 giá
   trị, giữ nguyên actor + selection + slot-highlight + Inspector. Bối cảnh phải đọc trước:
   `Bug-ParamUndo-SlotContextLost` (`Open_Bugs.md`), `DEVIATIONS.md` mục "Param-Undo slot-context",
   `BP_UndoManager.md` v1.10 (`RestoreSnapshot`=DeselectAll+destroy+respawn+reselect — đây là gốc
   vấn đề). cuhoang chốt "sẵn sàng đập xây lại" — không bị ràng giữ nguyên hệ undo hiện tại.
2. **T4b** — coalescing undo (gộp nhiều lần kéo→1 entry) + seam #7 `EndParamSession`. LƯU Ý: Hướng 3
   có thể đổi cả cách làm T4b → làm Hướng 3 trước.
3. **T5** — multi-select áp param cả cụm (resolve-by-name per-actor, xem task card rev6).
4. **G7.0b** (compat UE 5.6/5.7/5.8) — chưa chạy, backlog riêng.
5. **(Tùy chọn, không khẩn) Dọn `SaveComboFromSelection` Bước 5d** — xóa loop tính
   `MaterialOverrides_SaveCombo` (dư thừa) — chỉ làm khi rảnh.

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

- 18/09 (tiếp 2) — **S7G7T4 GATE ĐÓNG — PASS.** 5 handler thật nối `MaterialSlotService`
  (Scalar/Color Preview+Commit + ResetParams). Dispatcher 2 row nâng 2-input `(ParamName,Value)` (v1.1).
  Live-preview + undo/redo VALUE PASS. Bug B3 (sót wire ParamName → preview màu hỏng ngầm) fix. **Lộ
  giới hạn kiến trúc Hướng 1:** undo mất slot-highlight (Undo=destroy+respawn actor) — `Bug-ParamUndo-
  SlotContextLost` backlog, cuhoang chốt phiên sau **đập-xây-lại hệ undo (Hướng 3)**. Merge: `WBP_
  FurnitureInventory.md` v3.32, 2 row v1.1, `DEVIATIONS.md`, `Open_Bugs.md`. Bài học phiên: đoán sai
  giả định object-identity qua undo 3 lượt → xem `Rules/Learning_System.md`.
- 18/09 (tiếp) — **Đóng `Bug-MaterialEdit-EnableState` + sinh rule Q10.** 2 lỗi "entry point cũ không
  rà lại khi seam mới ra đời" (`RefreshSlotSwatches` thiếu `HighlightSwatchByIndex`, `BTN_ResetSlot`/
  `BTN_ResetAll` thiếu `RefreshParamPanel`). Elevate thành rule `AI_Implementation_Rules.md` Q10 —
  FLOW COVERAGE GATE, đặt TRƯỚC Q9. Merge: `WBP_FurnitureInventory.md` v3.31, `Open_Bugs.md`, `AI_Impl` v2.20.
- 18/09 — **S7G7T3.3 + T3.4 PASS.** `RefreshParamPanel()` build đầy đủ (Scalar+Color, fallback MID,
  empty-state, bounds) + lifecycle Inspector (dùng `Set Background Color` — rev6 ghi nhầm `SetHighlight`)
  + 5 seam APPEND (seam #5 CUỐI nhánh Material) + vá lỗ hổng kéo-thả material. Xem `WBP_FurnitureInventory.md` "S7G7T3".
- 17/09 — **S7G7T3 ĐANG DỞ.** T3.1 `WBP_MaterialParamPanel` PASS + T3.2 `WBP_MaterialInspector` PASS 7/7 (2 widget mới).
- 15/09 (tiếp 2) — **S7G7T2 ĐÓNG — PASS.** `WBP_ParamScalarRow`+`WBP_ParamColorRow` + `HexToLinearColor` (C++).
  3 quyết định kiến trúc (`CurrentColor` single-source, bỏ preset, hex-error chỉ revert). `Bug-MaterialSlots-MissingInClipboard` đóng.

---

## Canonical pointers (giai đoạn hiện tại)

| Cần gì | Đọc |
|---|---|
| **Kiến trúc Undo mới (T0→U1→U2→U3)** | `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md` |
| **Luật test tự động (Spec/Functional/luật PIE)** | `Rules/Testing.md` |
| Plan Sprint 7 (tạm hoãn, chờ Undo Architecture) | `Plans/Sprint7_MaterialEdit_Plan_v1.1.md` |
| Material v1.1 nền (đổi vật liệu đã chạy) | `Features/ChangeMaterial.md` |
| Rule Blueprint (Q8/Q9/Q10/L1-L14/bảng node) | `Rules/AI_Implementation_Rules.md` |
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
