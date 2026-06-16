# 06 — Risk Mitigation
**Mục đích:** Liệt kê rủi ro tiềm ẩn và cách xử lý từng cái.

---

## CRITICAL RISKS (có thể block sprint)

### R1 — Custom Depth Stencil Multi-Outline không phân biệt Primary/Secondary

**Vấn đề:** M_SelectionOutline hiện tại check Stencil == 255. Multi-select cần 2 màu outline khác nhau cho Primary vs Secondary. Material outline cần update.

**Severity:** HIGH
**Sprint:** 1
**Probability:** 100% (chắc chắn xảy ra)

**Mitigation:**
- Update M_SelectionOutline material:
  ```
  Stencil >= 254 → có outline
  Stencil == 255 → màu xanh đậm (rgb: 0.2, 0.6, 1.0)
  Stencil == 254 → màu xanh nhạt (rgb: 0.4, 0.8, 1.0, alpha 0.5)
  ```
- Nếu màu nhạt khó nhìn trên scene tối → đổi sang outline mỏng hơn thay vì đổi màu
- Backup plan: chỉ outline Primary, không outline Secondary (chấp nhận UX kém hơn)

**Test verification:** Sau Sprint 1, multi-select 5 đồ → 4 đồ phải có outline khác Primary.

---

### R2 — RuntimeTransformer plugin không hỗ trợ multi-actor

**Vấn đề:** Plugin chỉ làm việc với 1 SelectedActor. Không thể đơn giản pass array.

**Severity:** HIGH
**Sprint:** 1
**Probability:** 100%

**Mitigation:** Pivot Actor pattern (đã chốt trong Master Plan)
- Spawn BP_PivotActor tại center group
- Gizmo attach vào Pivot
- Pivot Tick → tính delta transform → ForEach children apply

**Risk con của Pivot Actor:**
- Pivot Tick chạy mỗi frame → overhead
- Solution: chỉ Tick khi Transform thay đổi (cache LastTransform)

**Test verification:** Multi-select 20 đồ → Move qua gizmo → tất cả move đồng bộ, không lag.

---

### R3 — EMS Save/Load không lưu Groups data

**Vấn đề:** EMS chỉ save Actors. Groups là logical concept không thuộc actor nào → không được save.

**Severity:** HIGH
**Sprint:** 3
**Probability:** 100%

**Mitigation:** BP_GroupsContainer pattern (đã chốt)
- 1 actor mang tag "FurnitureGroupsContainer"
- Variables Groups : Array of S_GroupData (SaveGame)
- EMS save actor này như actors khác

**Risk con:**
- Nếu user xóa container actor → mất hết groups
- Solution: Level Blueprint check sau load, spawn lại nếu không có
- Tags "FurnitureGroupsContainer" + check IsValid trong InputManager

**Test verification:** Tạo group → Save → Restart PIE → Load → group khôi phục đúng.

---

### R4 — Snapshot history quá lớn khi có nhiều group

**Vấn đề:** Mỗi snapshot lưu copy của Groups array. Nhiều group + nhiều history → memory grow.

**Severity:** MEDIUM
**Sprint:** 3
**Probability:** Medium

**Số liệu ước tính:**
- 50 actors × 200 bytes/placement = 10KB/snapshot
- 50 history × 10KB = 500KB
- Thêm 20 groups × 100 bytes = 2KB/snapshot
- 50 × (10KB + 2KB) = 600KB tổng → vẫn OK

**Mitigation:**
- MaxSteps = 50 (giữ nguyên)
- Theo dõi memory trong Profile khi scene có 100+ actors
- Nếu cần: reduce MaxSteps xuống 30, hoặc skip group capture cho action không liên quan

**Test verification:** Memory monitor sau 50 undo entries với 100 actors + 30 groups.

---

### R5b — Gizmo collision disable ảnh hưởng Pivot Actor

**Vấn đề:** ActivateGizmo hiện tại disable collision của actor non-"FurnitureSpawned". Pivot Actor tag "FurniturePivot" (không phải "FurnitureSpawned") → có thể bị disable collision → GizmoTrace không hit được Pivot → không kéo được gizmo khi multi-select.

**Severity:** HIGH (block multi-move)
**Sprint:** 1
**Probability:** Medium-High (chưa trace tương tác này)

**Mitigation:**
- Trong vertical slice Sprint 1, TEST NGAY: multi-select 2 đồ → gizmo có hiện trên Pivot không, có kéo được không
- Nếu Pivot bị disable collision → sửa logic ActivateGizmo: whitelist cả "FurniturePivot" (không disable)
- Hoặc: Pivot dùng Scene Component không cần collision, gizmo attach trực tiếp không qua trace
- Kiểm tra: GizmoTrace channel có Block trên Pivot's gizmo components không

**Test verification:** Vertical slice — multi-select → gizmo hiện + kéo được. Nếu fail → đây là R5b.

---

### R5 — Pivot Actor không bị destroy khi Load Scene

**Vấn đề:** EMS load destroy tất cả "FurnitureSpawned" actors. Pivot Actor có tag riêng → không bị destroy → orphan.

**Severity:** MEDIUM
**Sprint:** 1
**Probability:** 100%

**Mitigation:**
- BP_FurnitureSceneManager.OnLoadButtonClicked thêm:
  ```
  Get All Actors With Tag("FurniturePivot") → ForEach Destroy
  ```
- Hoặc: DeselectAll trước Load (đã có) → DestroyPivot tự chạy
- DOUBLE protection: cả 2 cách trên

**Test verification:** Save → tạo multi-select → Load → kiểm tra không còn Pivot Actor.

---

### R6 — Group circular reference

**Vấn đề:** Nếu Group A.ParentGroupID = "g_b" và Group B.ParentGroupID = "g_a" → infinite loop khi traverse.

**Severity:** HIGH (crash)
**Sprint:** 4 (Nested Group)
**Probability:** Low (user phải cố tình tạo)

**Mitigation:**
- Validate trước khi SET ParentGroupID:
  ```
  function CanSetParent(GroupID, NewParentID):
    Branch NewParentID == "": return True
    current = NewParentID
    While current != "":
      Branch current == GroupID: return False  ← would create cycle
      current = FindGroup(current).ParentGroupID
    return True
  ```
- Nếu CanSetParent → False, hiện error toast "Không thể nhóm vào nhóm con của chính nó"

**Test verification:** Tạo Group A chứa Group B → cố gắng đặt A làm con của B → bị reject.

---

## MEDIUM RISKS

### R7 — Box Select trigger conflict với drag gizmo

**Vấn đề:** Mouse Left Pressed trên vùng trống vs trên gizmo handle vs trên mesh body — phải phân biệt chính xác.

**Severity:** MEDIUM
**Sprint:** 2
**Probability:** Medium

**Mitigation:**
- Step 4 hit trace ưu tiên:
  1. Trace GizmoTrace channel → nếu hit gizmo, OnMousePressed của Gizmo xử lý
  2. Trace CAMERA channel → nếu hit actor, vào select flow
  3. Nếu KHÔNG hit gì → box select
- BoxSelect chỉ start khi cả 2 trace đều miss

**Test verification:** Click chính xác trên gizmo X axis → move, không trigger box select.

---

### R8 — DPI Scale làm Box Select rectangle bị lệch

**Vấn đề:** Mouse position scaled by DPI vs widget canvas position có thể khác nhau.

**Severity:** MEDIUM
**Sprint:** 2
**Probability:** Medium

**Mitigation:**
- Dùng `Get Mouse Position on Viewport` (đã scaled)
- Hoặc dùng `Get Mouse Position Scaled by DPI`
- TEST trên cả Windows DPI 100% và 150% (4K)

**Test verification:** Box select trên monitor 4K (200% DPI) → rectangle chính xác.

---

### R9 — Multi-select 100+ actors lag

**Vấn đề:** UpdateOutlineState gọi Set Custom Depth 100 lần → có thể chậm.

**Severity:** LOW (cho scene typical 20-50 actors)
**Sprint:** 1
**Probability:** Low

**Mitigation:**
- Nếu chậm: only update outline cho actors visible trên screen
- Hoặc: dùng Render Custom Depth Pass = Default cho tất cả, chỉ thay đổi Stencil value
- Profile với 100 actors trước khi optimize prematurely

**Test verification:** Ctrl+A trên scene 100 actors → chấp nhận < 200ms.

---

### R10 — Drag combo từ Inventory phức tạp

**Vấn đề:** WBP_DragOverlay hiện chỉ drag 1 mesh. Combo drag cần preview nhiều mesh.

**Severity:** MEDIUM
**Sprint:** 5
**Probability:** Medium

**Mitigation:**
- Phase 1: Combo spawn chỉ qua click (không drag)
- Phase 2 (sau): implement multi-mesh preview ghost

**Fallback UX:**
- Click combo card → spawn tại center viewport
- User di chuyển combo sau khi spawn (như group bình thường)

---

## LOW RISKS

### R11 — Context Menu z-order conflict với widget khác

**Mitigation:** Always Add to Viewport với Z Order = 99999 → cao hơn tất cả.

### R12 — Group name có ký tự đặc biệt phá vỡ JSON serialization

**Mitigation:** Escape ký tự khi serialize JSON. Hoặc whitelist chỉ alphanumeric + space + Vietnamese.

### R13 — Combo JSON file quá lớn (>1MB)

**Mitigation:** Limit combo size = 100 meshes max. Hiện cảnh báo nếu vượt.

### R14 — User tạo nhiều group nested 10+ cấp

**Mitigation:** Soft limit 5 cấp nested. Hiện warning nếu vượt.

### R15 — Select Similar tìm 1000+ matches lag UI

**Mitigation:** Limit max select = 500. Hiện confirmation "Sẽ chọn 500/1234 đồ. Tiếp tục?".

---

## RISK MATRIX

| Risk | Severity | Probability | Sprint | Status |
|---|---|---|---|---|
| R1 — Outline material | HIGH | 100% | 1 | Planned |
| R2 — Gizmo multi-actor | HIGH | 100% | 1 | Planned (Pivot) |
| R3 — EMS Groups save | HIGH | 100% | 3 | Planned (Container) |
| R4 — Snapshot size | MEDIUM | 30% | 3 | Monitor |
| R5 — Pivot orphan | MEDIUM | 100% | 1 | Planned |
| R5b — Gizmo disable Pivot collision | HIGH | 60% | 1 | Test vertical slice |
| R6 — Circular group | HIGH | 5% | 4 | Validate |
| R7 — Box vs gizmo | MEDIUM | 50% | 2 | Trace priority |
| R8 — DPI Box | MEDIUM | 30% | 2 | Test DPI |
| R9 — 100+ actors lag | LOW | 10% | 1 | Profile first |
| R10 — Combo drag | MEDIUM | 60% | 5 | Phase 2 |
| R11 — Z order | LOW | 20% | 2 | Z Order 99999 |
| R12 — JSON special chars | LOW | 30% | 5 | Escape |
| R13 — Combo size | LOW | 10% | 5 | 100 max limit |
| R14 — Deep nested | LOW | 5% | 4 | 5 levels soft |
| R15 — Select Similar 1000+ | LOW | 20% | 2 | 500 limit |

---

## CONTINGENCY PLANS

### Nếu Sprint 1 (Multi-select) gặp vấn đề lớn:

**Plan B:** Implement chỉ "shift+click range select" thay vì full multi-select.
- User click đồ A, shift+click đồ B → chọn A và B (không phải range)
- Move/Delete vẫn hỗ trợ array
- Bỏ qua Pivot Actor — chỉ apply transform vào Primary

**Trade-off:** UX kém hơn, nhưng tránh refactor sâu BP_GizmoController.

### Nếu Pivot Actor không stable:

**Plan B:** Multi-select chỉ hỗ trợ Move (không Rotate/Scale).
- Move: tính delta dễ, ForEach apply
- Rotate/Scale: khó tính delta đúng → tạm thời disable cho multi-select
- Show error message: "Rotate/Scale chỉ hoạt động với 1 đồ. Tách selection trước."

### Nếu Group Edit Mode (Sprint 4) phức tạp:

**Plan B:** Bỏ Edit Mode trong v1. Chỉ hỗ trợ flat group (no nested).
- Single-level group: tạo, ungroup, move, delete
- Edit từng đồ trong group: ungroup trước → edit → group lại
- UX kém hơn nhưng đơn giản code

### Nếu Combo Mesh phức tạp:

**Plan B:** Combo = saved group, không thumbnail auto-gen.
- Lưu combo vào DataTable
- Thumbnail = generic icon "🧩"
- Skip ThumbnailStudio integration
- Phase 2 thêm thumbnail sau

---

## EARLY WARNING SIGNS

Trong khi code, nếu thấy các dấu hiệu sau → STOP, đánh giá lại:

1. **Performance Tick** > 5ms → optimize trước khi tiếp tục
2. **Memory tăng** > 100MB sau 20 undo → check leak
3. **Bug retry** > 3 lần fix không xong → consider Plan B
4. **Sprint trễ** > 50% estimate → giảm scope, dời sang sprint sau

---

## SUPPORT RESOURCES

- **UE5 Documentation:** [docs.unrealengine.com](https://docs.unrealengine.com)
- **RuntimeTransformer source:** check `Plugins/RuntimeTransformer/`
- **EMS Documentation:** check `Plugins/EasyMultiSave/`
- **Stack Overflow tag:** unreal-engine, unreal-blueprint
- **Anthropic Claude:** liên hệ khi gặp vấn đề khó

---

## FAILURE PLAYBOOK

### Khi gặp crash không rõ nguyên nhân:
1. Kiểm tra Output Log → tìm dòng "Access None"
2. IsValid check trước mọi Object access (đã là rule)
3. Profile GC (Garbage Collector) bằng `stat memory`
4. Disable plugins một-một để tìm conflict

### Khi gizmo bị stuck (không thoát):
1. Kiểm tra DeactivateGizmo có nối đúng cả True/False branch không
2. SET bIsDraggingGizmo = False ngay đầu Event Tick nếu Mouse Left Button Up
3. Restart PIE (workaround tạm thời)

### Khi Save/Load mất data:
1. Check tags actor đúng ("FurnitureSpawned", "FurnitureGroupsContainer")
2. Check Variables có tick SaveGame
3. Implement EMSActorSaveInterface đầy đủ
4. Test save → quit → restart → load (full cycle)
