# Session State — Lighting_Mnger Interior Design Tool
**Cập nhật:** 08/06/2026 — 13:30 ICT
**Đọc file này ĐẦU TIÊN** khi bắt đầu session mới.

---

## TRẠNG THÁI HIỆN TẠI

**Giai đoạn:** Sprint 3 — Group cơ bản — **CHƯA BẮT ĐẦU**
**Đang làm trên:** PROJECT TỔNG (master)
**Engine:** UE5.5.4
**TIẾP THEO NGAY:** Vertical Slice Sprint 3 — T1+T2+T3+T4 (data plumbing + BP_GroupsContainer)
**Plan Sprint 3:** đọc `Sprint3_Plan_Opus.md` (trong plan_v3/) — ĐỌC TRƯỚC KHI CODE

---

## ROADMAP

```
✅ Phase 0: Material Copy/Paste (single-slot)        DONE 02/06
✅ Integration vào master                            DONE 02/06
✅ Sprint 1: Multi-select                            15/15 COMPLETE (Move+Rotate+Scale shipped)
✅ Sprint 2: Box Select + Context Menu               9/9 COMPLETE — SHIPPED 08/06
🔄 Sprint 3: Group cơ bản                           0/12 task — BẮT ĐẦU NGAY
⏭️ Sprint 4-7: Edit → Combo → Polish → Mat v1.2
   Sau đó: Refactor Phase B → glTFRuntime → Supabase
```

---

## SPRINT 2 — COMPLETE ✅ (08/06/2026)

Tất cả 9 task đã ship:
- T1-T2: Box Select (WBP_BoxSelectOverlay + logic defer/tick/release)
- T3-T6: Context Menu (WBP_ContextMenu + Select Similar + Reset Rotation + Delete)
- T7: Cut (Ctrl+X = CopyMesh + DeleteSelected, Shift guard)
- T8: Final test — pass hết
- T9: CB_ChangeMaterial + CB_Replace multi (F_OpenMaterialMode, StartReplaceMode, F_ExecuteReplace, EnsureExpanded, OpenMaterialModeForActor)

---

## SPRINT 3 — GROUP CƠ BẢN (bắt đầu 08/06/2026)

**NGUYÊN TẮC CỐT LÕI:** Một group = một multi-selection. Transform/Copy/Delete/Snapshot tái dùng 100% Sprint 1.
**Plan chi tiết:** Sprint3_Plan_Opus.md (Opus 4.8, 08/06)

### VERTICAL SLICE — LÀM ĐẦU TIÊN (kill EMS risk)
```
T1: Struct S_GroupData (GroupID, GroupName, ParentGroupID, bIsLocked)
T2: BP_FurnitureActor.GroupID (SaveGame, default "")
T3: BP_GroupsContainer (Actor, EMSActorSaveInterface, singleton guard, ActorLoaded sync)
T4: BP_FurnitureInputManager.Groups (Array) + SyncGroupsToContainer()

TEST SLICE:
1. Tạo tạm CreateGroup (gán GroupID cho SelectedActors, chưa cần Ctrl+G)
2. Save → Load
3. Verify: đúng 1 container, GroupID còn, Groups array khôi phục
```

### 12 TASKS (thứ tự thực thi)
```
VS  : T1+T2+T3+T4 → test EMS
T5  : Helpers (GetGroupChildren, FindGroupData, GenerateGroupID,
               ExpandSelectionWithGroups, PruneEmptyGroups)
T11 : Snapshot v3 (GroupID per placement + Groups array)
T6  : CreateGroup (auto-name) + Ctrl+G
T8  : Click resolution → ExpandSelectionWithGroups
T9  : Box select → ExpandSelectionWithGroups
T7  : UngroupActors + Ctrl+Shift+G
T10 : Dispatchers OnGroupCreated/Destroyed + Info Bar
T12 : Delete group + PruneEmptyGroups + Final test
```

### Quyết định kiến trúc đã chốt
- GroupID = `"g_" + GUID`
- Auto-name `"Nhóm N"` (bỏ dialog)
- BP_GroupsContainer: sync SAU group-op (không mỗi frame)
- ExpandSelectionWithGroups = keystone function (click + box + future nested)

---

## ĐÃ HOÀN THÀNH (trước Sprint 3)

Change Material v1.1 (18–20/05) | UX Phase 2.1 | Resize Window (27/05) | Plugin Migration C++ (01–02/06) | Integration master (02/06) | Phase 0 Material Copy/Paste | Sprint 1 Multi-select (15 task) | Sprint 2 Box+Context (9 task)

---

## KEY BUGS & FIXES (tích lũy)

| Bug | Fix |
|---|---|
| EnsureExpanded không expand | Thiếu HB_Main_Content — phải match BTN_MinimizedIcon OnClicked đầy đủ |
| CB_Replace không toggle off | Toggle check bIsReplaceMode TRƯỚC guard |
| Event không có local var | Tạo Function riêng (F_ExecuteReplace, F_OpenMaterialMode) |
| Undo nhảy cóc | CLEAR TempSelectedIndices đầu CaptureSnapshot |
| Delete destroy InputManager | Target = Array Element, KHÔNG để trống |
| Box: chọn lệch | DPI — chia Project World To Screen cho Get Viewport Scale |
| Box: click-drag mesh → single select ngay | Defer PendingClickActor + ngưỡng 5px |
| Ctrl+Shift+V trigger paste nhầm | Shift check trong IA binding (áp dụng luôn cho Ctrl+X) |
| Multi-select gizmo không hiện | UpdateGizmo nhánh >=2: DeactivateGizmo TRƯỚC ActivateGizmo |

---

## LEARNINGS QUAN TRỌNG

- **Event không có Local Variable** → Function (F_ExecuteReplace, F_OpenMaterialMode, F_OpenReplaceMode)
- **Toggle check TRƯỚC guard** trong callback mode (CB_Replace)
- **EnsureExpanded phải match source event chính xác** — thiếu widget nào là fail
- **CLEAR class var đầu hàm** nếu persistent (TempSelectedIndices)
- **Code 1 lần → Completed, không Loop Body** (DuplicateMesh lesson)
- **CaptureSnapshot SAU action** — gán xong mới snapshot
- **Destroy target = element đang duyệt**, không để trống
- **IsValid trước mọi Object access**
- **Tất cả nhánh Branch merge về cuối**
- **Latent node chỉ trong Custom Event**

---

## NGUYÊN TẮC

- Đầu session: đọc Session_State.md → Sprint3_Plan_Opus.md khi làm Group
- R1-R5 cho code mới. Hard ref clear ở End Play/Destruct
- Cuối session: update Session_State.md + doc liên quan (version + ngày + giờ + phút)
