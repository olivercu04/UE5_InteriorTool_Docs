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
**Last verified (tiếp):** 21/09/2026 (tiếp) — **U1.0→U1.4 xong, PIE PASS toàn bộ** (ID-01, ID-02, ID-03, ID-04, ID-05 đều xanh — chi tiết `Sprints/Sprint7/21-09-2026_U1_PersistentIdentity_TaskCard.md` §5, §9 V1/V4/V5/V8 CONFIRMED). `ResolveByPersistentId` verify khớp 100% qua K2Node export thật. **§11 comprehension check: CHƯA qua** — 3 câu đầu cuhoang trả lời, cả 3 đều lệch chỗ cốt lõi (đã chỉ ra chỗ sai, đang chờ trả lời lại) → **U1 CHƯA được tick**, dù U1.0-U1.4 kỹ thuật đã xong. Doc canonical (U1.7) đang được cập nhật đồng loạt cùng phiên này: `BP_FurnitureActor.md` v2.6, `BP_FurnitureInputManager.md` v3.8, `WBP_DragOverlay_FurnitureCard.md` v1.11, `BP_UndoManager.md` v1.18, `Data/EntityIdLibrary_Reference.md` (mới), `AI_Implementation_Rules.md` v2.22, `Rules/Testing.md` v1.1. Còn treo: U1.5 (EMS save/load manual, ID-06/ID-07 end-to-end), U1.6 (Functional Test — TUỲ CHỌN), §11 câu 2+3 trả lời lại.
**Last verified (tiếp):** 21/09/2026 (tiếp 2) — **§11 comprehension check PASS.** cuhoang trả lời lại qua 3 vòng hỏi dẫn dắt (Socratic, sửa tại chỗ khi lệch) — cả 3 câu đúng cốt lõi (xem task card §11 để có toàn văn). Doc as-built (U1.7) đã merge xong toàn bộ 9 file + `Data/EntityIdLibrary_Reference.md` (mới) từ phiên trước đó cùng ngày. **U1 vẫn CHƯA đóng hẳn** — còn U1.5 (EMS save/load manual, ID-06/ID-07 end-to-end) chưa chạy. Next: U1.5 → đóng U1 → U2.
**Last verified (tiếp):** 21/09/2026 (tiếp 3) — **U1 ĐÓNG.** U1.5 (EMS save/load manual) PASS cả ID-06 (spawn→Save→Load, ID giống) và ID-07 (save CŨ trước U1 → sinh ID lần đầu → Save→Load lại → ID ổn định, không sinh lại). Toàn bộ U1.0→U1.5 xanh, §11 comprehension check PASS. U1.6 (Functional Test) — TUỲ CHỌN, bỏ qua, bằng chứng manual đã đủ. Next: Opus lập task card U2 (History/Mutation Boundary), xem `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md`.
**Last verified (tiếp):** 22/09/2026 — **U2.0 + U2.1 ĐÓNG.** U2.0: backup `Lighting_Mnger_BACKUP_22-09-2026_preU2` (cuhoang, tay) + git commit `a504560` (mốc sau U1, plugin `FurnitureToolkit`). U2.1: `ParamCommandTypes.h` (`EParamCmdType`+`FMaterialParamCommand`) + `UParamCommandLibrary` (`BuildScalarCommand`/`BuildColorCommand`/`IsNoOpCommand`/`RefuseTexture`) + `MaterialSlotService` +`GetSlotScalarParam`/`GetSlotVectorParam` (reader Before, không side-effect) — compile sạch, Spec `FurnitureTool.Undo.U2_Command` 4/4 xanh, negative control PASS (đổi 1 nhánh return, không tạo dead code — lần đầu thử chèn `return true;` sớm bị build fail vì project bật warnings-as-errors, unreachable code → error). Git commit `3fd1b2a`. Merge canonical: `Data/MaterialSlotService_Reference.md`. **Next: U2.2 (struct/enum trong Blueprint Editor — CHỈ cuhoang làm được, không có bridge cho Blueprint asset).**
**Last verified (tiếp):** 22/09/2026 — **U2.2 ĐÓNG.** cuhoang (tay, Blueprint Editor): enum `E_HistoryEntryKind` (Snapshot|ParamCommand) + struct `S_SceneSnapshot` +field `EntryKind`+`ParamCmd` (kiểu `FMaterialParamCommand` hiện đúng trong Struct picker — W1 xác nhận CÓ) + Version 4→5. Compile sạch. Smoke PIE (chọn actor→Move→Undo) chạy y hệt trước giờ, không lỗi. Merge canonical: `BP_UndoManager.md` v1.19. **Next: U2.3 PARITY GATE** (tách `BuildSceneSnapshotBase`/`AppendEntry` từ `CaptureSnapshot`, thêm dispatch `EntryKind` vào `UndoLastAction`/`RedoLastAction` — vẫn là node flow Blueprint, việc tay cuhoang; Sonnet dẫn node flow + review, KHÔNG có bridge Blueprint asset). REG-01..05 phải PASS toàn bộ trước khi sang U2.4.
**Last verified (tiếp):** 24/09/2026 — **U2.3 PARITY GATE ĐÓNG — PASS.** Tách `BuildSceneSnapshotBase`/`AppendEntry` từ `CaptureSnapshot` (`CaptureSnapshot` còn 2 node gọi 2 helper, chữ ký giữ nguyên) + dispatch `EntryKind` vào `UndoLastAction`/`RedoLastAction` (nhánh command CHƯA chạy — chưa caller nào sinh command entry, đúng thiết kế PARITY). **W7 PASS** (`CurrentIndex=Len−1`, luôn trỏ entry hiện tại, không phải next-free-slot). **REG-01..05 PASS toàn bộ** (Move/Group/Combo/Select/Reset — stack thuần-snapshot y hệt v1.19) + trim MaxSteps=6 đúng số học. Lỗi phiên đã fix: Undo bản đầu đọc entry SAU khi giảm index → trượt 1 entry, sửa (đọc TRƯỚC khi giảm). §6 History-UI accessors (`GetHistoryCount`/`GetCurrentIndex`/`GetHistoryLabels`/`GetHistoryKinds`/`JumpToHistoryIndex`) build sẵn + review K2 PASS (thuộc U2.6, kéo lên sớm — CHƯA PIE test HISTUI). D-4: `ApplyParamCommand` đã review K2 export đối chiếu §5.6 task card — đúng, nợ review đầu U2.4 coi như xong. Merge canonical: `BP_UndoManager.md` v1.20 + `DEVIATIONS.md` D-1..D-4 + `Learning_System.md` (async-restore). **Next: U2.4** (Interactive Edit Session).

**Last verified (tiếp):** 24/09/2026 16:10 — **U2.4 + U2.5 ĐÓNG — PASS. Câu hỏi nhị phân U2 = XANH** (undo param đảo đúng giá trị, KHÔNG respawn, slot/Inspector/gizmo còn nguyên; redo đúng). Build: session vars + `ApplyParamCommand`/`Commit`/`Begin`/`Cancel` (thứ tự theo phụ thuộc — D-5) + 4 Cancel seam + 2 handler Begin + Commit rewire + seam #6 `OnHistoryChanged`. Dọc đường đóng thêm: **B-gizmo** (toggle), **seed/Before 0-trắng** (C++ reader đọc MI, git `c23b585`), **bánh xe màu đứng trắng** (`InteriorColorPicker.SetColor`). Merge canonical: `BP_UndoManager` v1.21, `WBP_FurnitureInventory` v3.33, 2 row v1.2, `BP_FurnitureInputManager` v3.9, `MaterialSlotService_Reference`, `InteriorColorPicker` v1.1, `Architecture_Map` v1.3, `DEVIATIONS` D-5..D-13, `Open_Bugs`, `Learning_System`, `AI_Implementation_Rules` v2.23. ⚠ Chưa soi K2 export phiên này.

**Last verified (tiếp):** 24/09/2026 17:40 — **U2 ĐÓNG HẲN.** U2.6 History-UI PASS (broadcast `OnHistoryChanged` đủ 5 chỗ; HISTUI-01/02/03 PASS; `JumpToHistoryIndex` ✓K2). U2.7: Print tạm dọn hết + smoke PASS; `CommitInteractiveEdit`/`BeginInteractiveEdit` ✓K2; doc as-built đủ (`Data_Structures`, `Testing` v1.2, W1–W7, QĐ6/hướng B/Đ12 vào DEVIATIONS); **§11 kiểm tra hiểu PASS 7/7** (`Learning_System.md`). `S7G7T4b` = absorbed by U2. Plugin `InteriorColorPicker` có git local (`ce51d9f`). Next: **Opus lập task card U3**.

--- hôm này là ngày thứ 6, sau vài ngày mưa tầm tã, hôm nay là ngày đẹp trời

Current: Sprint 7 tạm DỪNG ở G7 — đang xây **Undo Architecture Foundation** (T0→U1→U2→U3). **T0, U1, U2 ĐÓNG (U2: 24/09).** Tiếp: **U3 — Context / ChangeSet** (chưa có task card — Opus lập từ `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md` §U3). Câu hỏi nhị phân U3: *undo xong (kể cả undo Move/snapshot) slot-highlight và Inspector còn nguyên?*
> Giữ đúng 1 dòng. Đổi trạng thái → sửa tại chỗ, không thêm dòng mới.

---

## Đang ở đâu

| | |
|---|---|
| **Nền làm việc** | Project tổng tháng 6 (clone MỚI của master, tích hợp 24/08). Code trực tiếp tại đây. `FurnitureTool_Standalone` chỉ còn vai trò lịch sử/đóng gói cũ. |
| **Phase** | Hướng Gate 2 (bản packaged Shipping thật) — **tạm rẽ nhánh xây Undo Architecture Foundation trước khi quay lại Sprint 7** |
| **Milestone** | Undo Architecture Foundation (T0→U1→U2→U3) — chuẩn bị nền cho Sprint 7 G8-G10 + mọi continuous-edit sau này (transform gizmo...) |
| **Current Task** | **U2 ĐÓNG (24/09/2026).** Undo param targeted qua Resolver, không respawn; History-UI API sẵn sàng. **Chưa bắt đầu U3** — chờ task card. As-built: `BP_UndoManager.md` v1.22, `WBP_FurnitureInventory.md` v3.33. |
| **Task Source** | `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md` (delta, chưa merge canonical — merge từng phần khi mỗi gate as-built). |
| **Next** | **1. Opus lập task card U3 — Context / ChangeSet** (plan §U3: `TargetPath` + ChangeSet + Inspector giữ context; ~1 buổi). Đóng `Bug-ParamUndo-SlotContextLost` phần còn lại (undo SNAPSHOT như Move vẫn respawn → mất slot/Inspector). Trước khi đụng code: backup `_preU3` + git commit mốc (plan §bước 0). Opus nên đọc: `BP_UndoManager.md` v1.22, `WBP_FurnitureInventory.md` v3.33 (`ApplyRestoredActor`, `OnMeshSelected` Equal-guard), `DEVIATIONS.md` D-5..D-13 + D-11 (ceiling chống ghi mồ côi dựa vào RefreshParamPanel — U3 giữ slot sau undo snapshot sẽ đổi điều kiện này, phải rà lại). **2. Treo nhỏ (không chặn):** watch-item phím tắt đổi tab lúc đang giữ slider (chưa test — nếu session mồ côi → Cancel seam `SwitchInventoryMode` + guard Sess_Active); tùy chọn nối `Struct Out → AppendEntry` trong `CommitInteractiveEdit` cho dễ đọc; nợ hiểu nhẹ "undo command dùng Before của chính nó" hỏi lại ở U3. **Sau U3:** plan cho phép quay lại Sprint 7 G8–G10 (hoặc F-Migration — Opus + cuhoang quyết). |
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
| **S7G7T4b** | Coalescing undo + `EndParamSession` | **ABSORBED by U2 (24/09/2026)** — Interactive Edit Session tự sinh đúng 1 command lúc thả (100 preview → 1 entry, SESS-02/03 PASS); Cancel seam thay `EndParamSession`. Không còn là task riêng. |
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

0. **[24/09 — U2 ĐÓNG] Tiếp: task card U3** — xem ô **Next** ở bảng "Đang ở đâu". Mục 1 dưới đây là trạng thái 18/09, đã được hiện thực hóa thành Undo Architecture Foundation (T0/U1/U2 xong phần lớn) — giữ làm lịch sử.
1. **[HISTORICAL 18/09 — đang thực hiện qua T0→U3] Phiên mới — REDESIGN UNDO (Hướng 3).** Param-undo riêng (command-pattern old/new
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

- 24/09 (chiều) — **U2 ĐÓNG HẲN.** U2.6 HISTUI-01/02/03 PASS, U2.7 dọn Print + smoke PASS + ✓K2 Commit/Begin/Jump + §11 7/7. Next: task card U3.
- 24/09 — **U2.4 + U2.5 ĐÓNG — câu hỏi nhị phân U2 XANH.** Interactive Edit Session (Begin/Commit/Cancel) + 4 Cancel seam + seam #6 refresh panel. Đóng B-gizmo (toggle), seed/Before 0-trắng (C++ `c23b585`), bánh xe màu (`InteriorColorPicker` v1.1). D-5..D-13. Next: U2.6.
- 24/09 — **U2.3 PARITY GATE ĐÓNG — PASS.** Tách `CaptureSnapshot` → `BuildSceneSnapshotBase`+`AppendEntry` (CaptureSnapshot còn 2 node) + dispatch `EntryKind` vào `UndoLastAction`/`RedoLastAction` (nhánh command chưa chạy). W7 (`Idx=Len−1`) + REG-01..05 PASS toàn bộ + trim MaxSteps đúng. §6 History-UI accessors build sẵn (kéo lên sớm, chưa PIE). Lỗi Undo đọc-sau-giảm đã fix. Merge: `BP_UndoManager.md` v1.20, `DEVIATIONS.md` D-1..D-4, `Learning_System.md` (async-restore). Next: U2.4 Interactive Edit Session.
- 22/09 — **U2.2 ĐÓNG.** `E_HistoryEntryKind` (enum) + `S_SceneSnapshot` +`EntryKind`+`ParamCmd`, Version→5 (cuhoang, tay, Blueprint Editor). W1 xác nhận: `FMaterialParamCommand` hiện đúng trong Struct picker. Compile sạch, smoke PIE (Move→Undo) PASS. Struct-only, chưa đụng logic node. Merge canonical: `BP_UndoManager.md` v1.19. Next: U2.3 PARITY GATE.
- 22/09 — **U2.0 + U2.1 ĐÓNG.** Backup `preU2` + git `a504560`; `FMaterialParamCommand` + `UParamCommandLibrary` + `MaterialSlotService` +`GetSlot*Param`. Spec 4/4 xanh + negative control. Git `3fd1b2a`.

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
