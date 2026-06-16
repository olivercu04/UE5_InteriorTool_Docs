# 08 — Performance Optimization (Máy yếu + Dữ liệu lớn)
**Nguồn:** `import_raw/28-05-2026_08_Performance_Optimization.md`
**Phiên bản:** 1.0 | **Cập nhật:** 28/05/2026
**Mục đích:** Đảm bảo multi-select/group/combo chạy mượt trên máy yếu, scene nhiều actor.

⚠️ File này QUAN TRỌNG. Mọi task trong `Planning/04_Sprint_Details.md` phải đối chiếu với file này trước khi code.

---

## BỐI CẢNH HIỆU NĂNG

### Máy target (người dùng bình thường)
- VRAM hạn chế — `Bugs/Bug_GPU_VRAM_Crash.md` cho thấy crash ở budget ~7.26GB
- CPU tầm trung — Tick cost phải thấp
- Không có GPU rời mạnh

### Quy mô scene thực tế
| Tình huống | Số actor | Ghi chú |
|---|---|---|
| Phòng đơn | 20-50 | Typical |
| Căn hộ | 50-150 | Common |
| Nhà nhiều tầng / showroom | 150-500 | Stress |
| Library browse | 100k-200k mesh | Đã có giải pháp riêng (`Planning/Future_Architecture_1M_Assets.md`) |

⚠️ Phân biệt: **library** (duyệt asset) đã có plan scaling. **Scene** (actor đã đặt) là phần file này lo.

---

## NGUYÊN TẮC TỐI ƯU CỐT LÕI

### P1 — KHÔNG Tick khi không cần
Mọi logic Tick phải có điều kiện guard. Tick chỉ chạy khi thực sự có việc.

```
❌ SAI:
Event Tick:
  ForEach SelectedActors: do something  ← chạy mỗi frame dù không đổi

✅ ĐÚNG:
Event Tick:
  Branch bIsDraggingGizmo OR bIsResizing OR bIsBoxSelecting:
    T → do work
    F → return ngay  ← 99% thời gian return luôn
```

### P2 — Cache thay vì Query lặp lại
`Get All Actors With Tag` quét toàn scene. Gọi nhiều lần = chậm.

```
❌ SAI: gọi Get All Actors With Tag trong ForEach hoặc Tick

✅ ĐÚNG: cache 1 lần, update khi spawn/delete
  CachedFurnitureActors : Array of BP_FurnitureActor
  → Update trong: spawn, delete, load. KHÔNG query lại mỗi lần dùng.
```

### P3 — Async, KHÔNG Blocking
`Load Asset Blocking` freeze game thread. Với combo nhiều mesh = lag thấy rõ.

```
❌ SAI: ForEach combo meshes → Load Asset Blocking (freeze N lần)

✅ ĐÚNG: Async Load Asset → callback → spawn dần (R1)
```

### P4 — Batch thay vì Per-Item
Khi xử lý N actor, gom lại làm 1 lần nếu được, thay vì N lần riêng lẻ.

### P5 — Debounce mọi thao tác lặp
Snapshot, update UI, recalculate — debounce nếu user thao tác liên tục.

---

## TỐI ƯU THEO TỪNG TÍNH NĂNG

### Multi-Select Outline (Sprint 1)

**Vấn đề:** `Set Render Custom Depth = True` mỗi actor → render Custom Depth pass cho N actor. 100 actor = 100 pass = tốn GPU.

**Tối ưu:**
1. **Chỉ update outline khi selection THAY ĐỔI** — không update mỗi frame
   ```
   UpdateOutlineState chỉ gọi trong: SelectActors, ToggleActor, DeselectAll
   KHÔNG gọi trong Event Tick
   ```
2. **Diff update thay vì rebuild toàn bộ** — chỉ thay đổi actor mới thêm/bỏ
   ```
   OnSelectionChange:
     newlyAdded = NewSelection - OldSelection → enable outline
     newlyRemoved = OldSelection - NewSelection → disable outline
     ← KHÔNG loop toàn bộ SelectedActors mỗi lần
   ```
3. **Giới hạn mềm:** nếu selection > 200 actor → cảnh báo, hoặc chỉ outline actor visible trên screen

**Mục tiêu:** Multi-select 50 actor → outline update < 30ms (1 lần, không phải mỗi frame).

---

### Pivot Actor Tick (Sprint 1)

**Tối ưu:**
1. **Chỉ Tick khi Transform đổi:**
   ```
   Event Tick (Pivot):
     Branch GetActorTransform != LastSyncedTransform:
       T → ApplyTransformToChildren, SET LastSynced
       F → return ngay
   ```
2. **Disable Tick khi không drag:**
   ```
   Khi ActivateGizmo trên Pivot → Set Actor Tick Enabled = True
   Khi DeactivateGizmo → Set Actor Tick Enabled = False
   ```

**Mục tiêu:** Move 50 actor qua pivot → < 2ms/frame.

---

### CaptureSnapshot (Sprint 1+)

**Tối ưu:**
1. **Dùng cached actor list** (P2) thay vì Get All Actors With Tag mỗi capture
2. **Debounce snapshot** cho thao tác liên tục (đã có cho Nudge)
3. **MaxSteps thích ứng theo scene size:**
   ```
   Branch ActorCount > 200:
     MaxSteps = 20  ← giảm history để tiết kiệm memory
   Else:
     MaxSteps = 50
   ```

**Mục tiêu:** CaptureSnapshot 100 actor + 10 group < 15ms.

**Memory budget:**
- 1 placement struct ~200 bytes
- 500 actors × 200 = 100KB/snapshot
- 50 snapshots × 100KB = 5MB → chấp nhận được

---

### Box Select (Sprint 2)

**Tối ưu:**
1. **Project chỉ 1 lần khi thả chuột** — không project mỗi frame khi đang kéo khung
2. **Early reject:** nếu actor's location quá xa camera (behind/too far) → skip projection
3. **Cached actor list** (P2)

**Mục tiêu:** Box select trên scene 200 actor < 50ms (chỉ khi thả chuột).

---

### Combo Spawn (Sprint 5)

**Tối ưu:**
1. **Async load tất cả mesh** (R1)
2. **Loading indicator:** hiện "Đang tải combo... 5/20" trong khi spawn
3. **Spawn theo batch:** spawn 5 mesh/frame thay vì 20 mesh cùng lúc

**Mục tiêu:** Combo 20 mesh spawn < 1.5s, không freeze game thread.

---

### Scene Outliner (Sprint 6)

**Tối ưu:**
1. **Virtualized list:** dùng `List View` / `Tree View` (virtualized)
2. **Lazy thumbnail:** chỉ load thumbnail của row visible
3. **Debounce rebuild:** scene đổi liên tục → debounce 0.2s trước khi rebuild outliner
4. **Diff update:** chỉ thêm/bớt row thay đổi, không rebuild toàn bộ

**Mục tiêu:** Outliner 200 actor → mở < 100ms, scroll mượt.

---

### Material Multi-Apply (Sprint 7)

**Tối ưu:**
1. **Async load material 1 lần** — không load lại cho mỗi actor
   ```
   Async Load(materialPath) → 1 lần → MI_Source
   ForEach SelectedActors:
     Create DMI từ MI_Source (đã load)  ← không load lại
   ```

**Mục tiêu:** Apply material cho 20 actor < 100ms.

---

## VRAM MANAGEMENT (theo `Bugs/Bug_GPU_VRAM_Crash.md`)

Mọi biến hard ref đến UObject phải clear ở **Event End Play** (Actor) / **Event Destruct** (Widget):

**BP_FurnitureInputManager — Event End Play:**
```
CLEAR SelectedActors
SET PrimarySelectedActor = None
SET SelectedFurnitureActor = None
Destroy GizmoPivotActor (if valid)
CLEAR ClipboardActors
CLEAR Groups
```

**BP_PivotActor — Event End Play:**
```
CLEAR AttachedActors
CLEAR InitialOffsets, InitialChildScales, InitialChildRotations
```

**BP_GroupsContainer — Event End Play:**
```
CLEAR Groups
```

**Đã apply (từ `import_raw/performance.md` v1.1):**
- `BP_UndoManager` EndPlay: `SpawnedActors`, `FoundActor`, `TempMeshes`, `RestoredBPActor`
- `WBP_FurnitureInventory` Destruct: `TargetFurnitureActor`, `PendingRestoredActor`
- `WBP_MaterialCard` Destruct: `MaterialItem`, `InventoryRef`

**Workaround:** Restart editor mỗi 2-3 PIE session, dùng Standalone (Alt+P) cho session dài.

---

## PERFORMANCE BUDGET TABLE

| Operation | Budget | Scene size | Đo bằng |
|---|---|---|---|
| Click select 1 actor | < 5ms | any | stat unit |
| Ctrl+Click add | < 5ms | any | |
| Multi-select outline update (1 lần) | < 30ms | 50 actor | |
| Multi-move per frame (pivot) | < 2ms | 50 actor | stat unit |
| CaptureSnapshot | < 15ms | 100 actor | |
| RestoreSnapshot | < 200ms | 100 actor | (existing baseline) |
| Box select (on release) | < 50ms | 200 actor | |
| Combo spawn (async) | < 1.5s | 20 mesh | không freeze |
| Outliner open | < 100ms | 200 actor | |
| Material multi-apply | < 100ms | 20 actor | |

⚠️ Nếu vượt budget → STOP, optimize trước khi tiếp tục sang task khác.

---

## TỐI ƯU CHO MÁY YẾU — CHECKLIST

- [ ] Mọi Event Tick có guard condition (return sớm khi không cần)
- [ ] Không `Get All Actors With Tag` trong Tick hoặc ForEach
- [ ] Không `Load Asset Blocking` cho combo/material — dùng Async
- [ ] Pivot Actor disable Tick khi không drag
- [ ] Outline update chỉ khi selection đổi, không mỗi frame
- [ ] Snapshot debounce cho thao tác liên tục
- [ ] Mọi hard ref clear ở End Play / Destruct
- [ ] Scene Outliner virtualized (không spawn 500 widget)
- [ ] Loading indicator cho thao tác > 0.5s
- [ ] Test trên scene 100+ actor trước khi xem là "xong"

---

## SCALABILITY ROADMAP (khi scene vượt 500 actor)

1. **Spatial partitioning:** chia scene thành grid → query actor theo vùng nhìn
2. **Outline culling:** chỉ outline actor trong frustum camera
3. **Hierarchical LOD groups:** group xa camera → render 1 proxy mesh
4. **Delta snapshot:** undo lưu thay đổi, không toàn scene
5. **C++ migration:** chuyển hot path (snapshot, selection) sang C++ (Phase B)

⚠️ KHÔNG làm sớm. Chỉ làm khi đo được bottleneck thực tế.

---

## ĐO LƯỜNG — CÁCH PROFILE

Console commands trong PIE:
```
stat unit         ← Frame time, Game thread, Render thread, GPU
stat fps          ← FPS
stat memory       ← Memory usage
stat rhi          ← VRAM (render hardware interface)
stat scenerendering ← Draw calls, primitives
```

Quy trình khi nghi ngờ chậm:
1. `stat unit` → xem Game hay Render hay GPU là bottleneck
2. Game thread cao → logic Blueprint (Tick, ForEach) → optimize logic
3. Render/GPU cao → outline, draw calls → optimize render
4. Memory tăng liên tục → leak → check hard ref clear
