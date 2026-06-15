# DEVIATIONS — Lệch khỏi plan gốc (plan_v3)
**Cập nhật:** 12/06/2026 — 15:04 ICT

> File này ghi mọi deviation so với plan gốc (plan_v3/04_Sprint_Details.md).
> Không phải tất cả deviation đều xấu — một số là fix đúng, một số là scope cut có chủ ý.

---

## SPRINT 3 — GROUP CƠ BẢN

| # | Plan gốc nói | Thực tế | Lý do | Kết quả |
|---|---|---|---|---|
| D3-1 | Có WBP_GroupNameDialog (dialog đặt tên nhóm) | Bỏ hoàn toàn — auto-name "Nhóm N" | Đã chốt trước sprint (không cần dialog cho MVP) | ✅ Tốt hơn — ít friction, rename Sprint 6 |
| D3-2 | CaptureSnapshot gọi GetGroupsForSnapshot trực tiếp khi build Make S_SceneSnapshot | Dùng **TempGroups class var** làm buffer: SET TempGroups trước, Make đọc TempGroups | Bug impure-timing: GetGroupsForSnapshot không đảm bảo chạy xong trước Make | ✅ Fix đúng |
| D3-3 | UngroupActors: find index → remove → capture trong ForEach Loop Body | Chuyển toàn bộ sang **ForEach Completed** | Bug: trong Loop Body → 3 snapshot per ungroup + invalid-index warning | ✅ Fix đúng |
| D3-4 | Mouse Left Pressed Step 7: Branch IsCtrlDown → ToggleActor ngay | **Bỏ Branch Ctrl ở Step 7** — mọi click defer qua PendingClickActor; Ctrl phân giải ở OnLMBReleased | Ctrl+click group không cộng dồn được | ✅ Fix đúng, nhất quán hơn |
| D3-5 | Giữ dispatcher OnMeshSelected + OnMeshDeselected song song | **XÓA cả hai** — OnSelectionChanged là DUY NHẤT | Dual-dispatcher gây loạt bug khó trace | ✅ Refactor đúng |
| D3-6 | MeshToReplace : BP_FurnitureActor (single) | **XÓA** — chỉ còn MeshesToReplace (Array) | MeshToReplace dead variable, gây confusion | ✅ Dọn đúng |
| D3-7 | FoundIdx là local variable của UngroupActors | Đặt thành **class variable**, SET -1 đầu hàm | Blueprint function không có local Integer với default value dễ control | ✅ Acceptable workaround |
| D3-8 | Snapshot Version=3 trong plan | Thực tế vẫn Version=3 | Khớp plan | ✅ |
| D3-9 | Plan không nhắc PendingClickActor reset | Thêm **SET PendingClickActor = None** sau mỗi xử lý click | Bug: deselect click re-select đồ cũ vì PendingClickActor còn stale | ✅ Fix đúng |
| D3-10 | RestoreSnapshot: re-fire selection không xử lý empty case | Thêm nhánh **SelectedActors.Length==0 → DeselectAll + DeactivateGizmo** | Undo về snapshot deselect không tắt gizmo/outline | ✅ Fix đúng |

**Bug còn mở sau Sprint 3:**
- B1: Undo lần 2 không restore group state (Groups.Length=0 sau restore) → Gate 1.

---

## SPRINT 4 — EDIT MODE + NESTED GROUP (SHIPPED 12/06/2026)

| # | Plan gốc nói | Thực tế | Lý do | Kết quả |
|---|---|---|---|---|
| D4-1 | Trigger = nút info bar + Enter key (D3: hỏi lại khi làm T4) | **MVP: nút info bar ONLY**. Esc KHÔNG dùng (= thoát PIE). Phím tắt TBD | Esc đang là system key trong UE5 editor | 🟡 Acceptable MVP — thêm phím sau khi quyết |
| D4-2 | ExitEditModeOneLevel re-select: `GetGroupChildren(Exited)→Get(0)→ExpandSelectionWithGroups` | `GetAllDescendantActors(Exited)` **trực tiếp** → SelectActors | GetGroupChildren rỗng với nested thuần (actor ở sub-group, không có GroupID=Exited) | ✅ Fix đúng, gọn hơn |
| D4-3 | ResolveSelectionUnit: CASE 1 (đồ rời) kiểm tra trước CASE 3 (edit scope) | **Đảo thứ tự: edit scope kiểm tra TRƯỚC** | Q9a: đồ rời ngoài scope phải bị bỏ qua khi đang edit — nhất quán | ✅ Fix đúng |
| D4-4 | Click ngoài scope khi edit → behavior chưa định | **CLEAR selection, VẪN ở edit mode** (không no-op, không thoát edit) | Tránh đụng caller defer mong manh cho MVP | 🟡 Acceptable MVP |
| D4-5 | GetGroupsInHierarchy đặt trong helper list chính | Implement đầy đủ ngay T1 | Bridge cho Combo S5 — bắt buộc | ✅ |
| D4-6 | 03_Code_Inheritance_Strategy.md ghi EditingGroupID trong snapshot | **Không snapshot EditModeStack** (D6 giữ nguyên) | File 03 viết trước D6; BP_UndoManager v1.6 không có field này | ✅ File 03 là outdated reference |
| D4-7 | PruneEmptyGroups dùng GetGroupChildren.Length==0 | Đổi sang **GetAllDescendantActors.Length==0** | GetGroupChildren chỉ check direct members → prune oan group cha có sub-groups | ✅ DONE T7 |
| D4-8 | UngroupActors → deep ungroup cả cây (GetGroupRoot+GetAllDescendantActors+GetGroupsInHierarchy) | **Peel-one-level** (WalkUpUntilParent+B1+B2+B3): actor trực tiếp về cha, sub-groups đổi ParentGroupID về cha, chỉ xóa 1 group target | User demo case: ungroup Group con 2-1 → 4 actor về Group con 2; Group con 2-2 vẫn sống. Deep ungroup phá toàn bộ cây trong mọi context — sai UX. | ✅ DONE T7 — semantic đúng hơn |
| D4-9 | Spawn trong edit mode → GroupID chưa định | **GroupID="" (đồ rời)** — không auto-assign vào scope | Không đụng SpawnFurnitureCopy/Paste cho MVP | 🟡 Acceptable MVP |
| D4-10 | WBP_MeshControls T5: BTN_ExitOneLevel trong HB_EditModeBar | **Patch v1.5 không include BTN_ExitOneLevel** — thêm sau khi user phát hiện thiếu | Sót trong hướng dẫn bước 5.1 | ✅ Đã thêm (OnClicked → ExitEditModeOneLevel) |

**Bug fix trong Sprint 4:**
- Bug 2: GroupID lost sau Replace Mesh — **FIXED** (12/06): SET NewActor.GroupID = OldActor.GroupID trong BTN_ChangeMesh ForEach loop (WBP_DragOverlay_FurnitureCard)
- Bug: Branch condition nhầm ancestor === "" thành ancestor !== "" trong ResolveSelectionUnit — **FIXED**

---

## BUGS DEFERRED (ghi nhận, xử lý sprint sau)

| Bug | Mô tả | Deferred đến |
|---|---|---|
| B1 | Undo lần 2 không restore group state (Groups.Length=0) | Gate 1 (bIsRestoring guard) |
| Replace folder sai | Khi group có nhiều mesh khác folder, StartReplaceMode navigate folder của PrimarySelectedActor (last spawned) thay vì folder đại diện | Sprint 5 — revisit khi làm combo replace |

---

## QUYẾT ĐỊNH HOÃN (Decide-When-Reached)

| Mục | Lý do hoãn | Sprint/task dự kiến |
|---|---|---|
| Phím tắt Enter để vào Edit Mode | Chưa verify conflict với search box / snap inputs | Sau test UI nút stable |
| Click ngoài scope = no-op (giữ selection) | Phải đụng caller defer mong manh | Sau Slice 1 test nếu CLEAR khó chịu |
| T9 dimming (ApplyEditModeVisual body + M_SelectionOutline Stencil 200) | MVP không cần dim | Sprint 6 Polish |
| Double-click để enter edit | Cần track LastClickTime/LastClickActor | Sau phím tắt Enter stable |
| Edit Mode UX polish (breadcrumb nổi bật, dim đồ ngoài scope) | Sprint 6 Polish | S6 |

---

## NGUYÊN TẮC GHI DEVIATION

- Ghi ngay khi lệch, không đợi cuối sprint
- Ghi cả "deviation tốt" (fix đúng) lẫn "deviation tạm" (scope cut)
- Sau mỗi sprint: đọc lại, xem plan sprint sau có cần điều chỉnh không
