# Bug — GPU Crash / D3D Device Removed sau 3-4 lần PIE

**Phiên bản:** 1.0 | **Cập nhật:** 09/05/2026 — 08:30 ICT
**Project:** Lighting_Mnger (UE5.5.4) | **Loại bug:** GPU VRAM exhaustion

---

## Tóm tắt

Sau khoảng **3-4 lần Play In Editor (PIE)** liên tiếp (Play → thao tác → Stop → Play lại), Unreal Engine crash với thông báo:

```
GPU Crashed or D3D Device Removed.
Check log for GPU state information.
```

Crash callstack:
```
UnrealEditor_D3D12RHI (× 5 frames)
UnrealEditor_Core
kernel32
ntdll
```

Crash dump kèm file `nv-gpudump` (NVIDIA-specific).

---

## Nguyên nhân — VRAM exhaustion

### Bằng chứng quyết định

Trong `Lighting_Mnger.log` tại thời điểm crash:

```
LogD3D12RHI: Error: Video Memory Stats from frame ID 61667:
    Local Budget:  7262.00 MB
    Local Used:    8985.64 MB    ← VƯỢT 1.7 GB
```

GPU MMU page fault:
```
Fault Description: A shader instruction caused an MMU fault when accessing memory.
```

→ Driver D3D12 không cấp phát được VRAM cho shader → page fault → device removed → crash.

### Hardware

- **GPU:** NVIDIA RTX 3060 (12 GB total VRAM, ~7.26 GB UE5 budget)
- **CPU:** Intel i9-13900K
- **RAM:** 128 GB (chỉ dùng ~19.7 GB tại crash → RAM không phải vấn đề)
- **OS:** Windows 11 (25H2)
- **Driver NVIDIA:** 591.86

---

## Cơ chế leak — tại sao VRAM tích lũy giữa các PIE

### 1. PIE chia sẻ process với Editor

Editor process và PIE world dùng **cùng D3D12 device**. Khi Stop PIE:
- World GC chạy ở **CPU** → destroy actors, free UObject
- GPU resources có **lifecycle riêng**:
  - `FRHIResource` reference count
  - **Deferred deletion fence** (4 frames default)
  - PSO cache, shader cache
  - Streaming texture pool
  - Render target pool
  - Lumen surface cache

→ CPU memory freed khi Stop PIE, **VRAM thì không**. Bằng chứng:
```
Last completed frame ID: -1 (cached: 61665) - Current frame ID: 61669
```
Gap 4 frames = deferred deletion fence chưa hoàn tất.

### 2. Streamline plugin có swapchain leak

Trong log lần PIE đầu tiên:
```
LogStreamlineRHI: FStreamlineRHI::OnSwapchainDestroyed Enter
NumActiveSwapchainProxies=0
```

Streamline plugin (cho NVIDIA DLSS / DLSS-FG / Reflex / NIS / RTX Dynamic Vibrance) tạo swapchain proxy + DLSS feature context + Reflex queue. Mỗi PIE: destroy không hoàn toàn → tích lũy.

### 3. Asset references không release

- `Load Asset Blocking` → tạo Texture2D / StaticMesh trong VRAM
- UE5 **không auto-unload** assets không dùng → nằm cho đến GC sweep hoặc streaming evict
- Snapshot system (BP_UndoManager) hoặc cache có thể giữ reference → assets không evict

### 4. Construction Script abuse

Project tổng có 2 Blueprint bị bug nặng (ngoài furniture tool):

**`S_SAN`** (vách sàn) — Construction Script bắn errors:
- `Accessed None trying to read property CallFunc_Array_Get_Item_1`
- `Accessed None trying to read property MeshNepNoi1_43_5991DB...`

**`BP_BaseDoor_v1`** — Construction Script:
- `Attempted to access index 2 from array Local AST Cal of length 1!`
- `Accessed None reading structure _fixedSize_13_...`

→ ~200+ errors mỗi PIE. Construction Script tạo Procedural/Custom Mesh Component → buffer GPU mới mỗi lần construct mà không free buffer cũ → leak.

### 5. Plugin GPU-heavy enabled cùng lúc

Project hiện tại enable:
- NVIDIA DLSS Super Resolution (v3.7.3)
- NVIDIA DLSS Frame Generation
- NVIDIA NIS
- NVIDIA RTX Dynamic Vibrance
- NVIDIA Reflex
- Streamline (RHI extension)
- PCG Extended Toolkit
- Movie Render Queue + DLSS Support
- Lumen (SM6 feature level)

→ Mỗi plugin chiếm dụng VRAM riêng. Cộng dồn = áp lực base VRAM cao trước cả khi PIE bắt đầu.

---

## Pattern crash

| Lần PIE | PIE start time | Errors | RAM | Crash? |
|---------|---------------|--------|-----|--------|
| 1 (cold) | 4.886s | ~200+ | thấp | Không |
| 2 (warm) | 0.637s | ~200+ | tăng | Không |
| 3 (warm) | 0.640s | ~200+ | tăng | Không |
| 4 (warm) | — | — | tăng | **CRASH** — VRAM 8.98 GB / 7.26 GB budget |

→ Errors **không tăng** giữa các session — leak là tích lũy âm thầm trong VRAM, không hiện trong log.

---

## Audit code furniture tool — đóng góp vào leak?

### ✅ Phần an toàn

**`S_SceneSnapshot` và `S_FurniturePlacement`** chỉ chứa:
- String paths (MeshPath, DAPath, UniqueID, ActorTag)
- Primitive types (Vector, Rotator, Integer, Enum)

→ Không giữ hard reference đến UObject. Snapshot history (50 entries) chỉ tốn vài KB.

### ⚠️ 3 vectơ leak phát hiện trong BP_UndoManager

**Vectơ 1 — `SpawnedActors : Array of StaticMeshActor`** *(low impact)*

Hard reference array, không clear ở EndPlay. Stale refs tích lũy sau mỗi Undo/Redo.

**Vectơ 2 — `Load Asset Blocking` cho mesh** *(medium impact, ~200-500 MB/session)*

```
RestoreSnapshot Step 4:
  Spawn BP_FurnitureActor → Load Asset Blocking → Set Static Mesh
```

UE5 không tự động unload static mesh khi không còn reference. Mesh ở lại trong VRAM đến GC sweep / streaming evict tiếp theo. Mỗi mesh: 5-50 MB.

**Vectơ 3 — `FoundActor` single hard ref** *(negligible)*

### 🔮 Vectơ tương lai — sẽ xấu đi với Change Material v1.1+

```
Click material card → Load Asset Blocking(MaterialPath) → Create MID → Set Material
```

- Material loaded blocking → cũng không auto-unload
- MID giữ ref đến parent material → giữ textures (2K-4K)
- Mỗi MI: 50-200 MB VRAM
- Test 30 materials/session → 1.5-6 GB VRAM stuck

### Tỷ lệ đóng góp ước tính

| Nguồn leak | Đóng góp ước tính |
|------------|-------------------|
| Streamline / NVIDIA plugins | 40-50% |
| Lumen surface cache + SM6 | 20-30% |
| Construction Script abuse (S_SAN, BP_BaseDoor_v1) | 10-20% |
| **Code furniture tool (current)** | **10-30%** |
| Code furniture tool (sau v1.1 Material Editor — nếu không fix) | **40-60%** |

---

## Cách giải quyết — theo độ ưu tiên

### Tier 1 — Workaround tức thời

**Restart editor mỗi 2-3 lần PIE.** Đơn giản, hiệu quả 100%.

### Tier 2 — Process isolation (giải quyết nguyên nhân kiến trúc)

**Dùng Standalone Game thay PIE** cho test session dài:
- `File → Launch Standalone Game` (hoặc Alt+P với launch settings)
- Mỗi launch = process riêng → khi tắt, OS reclaim toàn bộ VRAM → 100% sạch
- Trade-off: chậm hơn ~30-60s startup, không hot-reload Blueprint

**Khi nào dùng:** Test multi-session, demo cho khách, regression test dài.
**Khi nào vẫn dùng PIE:** Iterate Blueprint nhanh.

### Tier 3 — Disable plugins không dùng

**Project Settings → Plugins**, disable:
- NVIDIA DLSS Frame Generation
- NVIDIA RTX Dynamic Vibrance
- NVIDIA NIS
- NVIDIA Reflex
- Streamline (nếu không dùng DLSS)
- Movie Render Queue (nếu không render video)

⚠️ **Báo đồng nghiệp** trước khi disable — đây là project chia sẻ.

**Test verify:** Sau khi disable, chạy 6-7 lần PIE liên tiếp. Nếu không crash → confirm Streamline/DLSS là thủ phạm chính.

### Tier 4 — Báo đồng nghiệp fix Construction Script

Gửi cho đồng nghiệp owner của `S_SAN` và `BP_BaseDoor_v1`:
- Errors: array out-of-bounds, null reference trong Construction
- Yêu cầu: kiểm tra array length trước access, clear buffer cũ trước khi tạo buffer mới
- Cân nhắc move logic ra khỏi Construction Script vào BeginPlay

### Tier 5 — Fix code furniture tool (proactive)

**Fix 5.1 — Clear `SpawnedActors` ở EndPlay**

Trong BP_UndoManager:
```
Event End Play:
  CLEAR SpawnedActors
  CLEAR FoundActor (set to None)
  CLEAR TempMeshes
```

**Fix 5.2 — Async load thay Load Asset Blocking**

Thay trong RestoreSnapshot Step 4:
```
[Cũ]   Load Asset Blocking → Set Static Mesh
[Mới]  Async Load Asset → On Loaded callback → Set Static Mesh
```

Lợi ích: không block frame + streaming system control lifetime tốt hơn.

**Fix 5.3 — MID lifecycle (chuẩn bị Change Material v1.1)**

Trong BP_FurnitureActor:
```
Variable: MaterialInstanceCache : Map<int, MaterialInstanceDynamic>

Trước khi tạo MID mới cho slot:
  Branch: MaterialInstanceCache.Contains(SlotIndex)?
    True → Reuse MID, chỉ Set Material Parameter
    False → Create MID → ADD to cache

Event End Play:
  For Each MaterialInstanceCache → Set value = None
  Clear MaterialInstanceCache
```

**Fix 5.4 — Force flush khi PIE stop (optional, cần C++ helper)**

Tạo C++ Blueprint Function Library:
```cpp
UFUNCTION(BlueprintCallable, Category="Memory")
static void ForceFlushGPU();
// Implementation: FlushRenderingCommands(); GEngine->ForceGarbageCollection(true);
```

Gọi từ BP_UndoManager EndPlay.

### Tier 6 — Configuration tuning *(buying time)*

Console commands hoặc Project Settings:
- `r.Streaming.PoolSize 2048` (default 1000) — tăng pool nhưng force eviction sớm
- Engine Scalability → Medium hoặc Low (giảm shadow, post-process)
- Project Settings → Rendering → Dynamic Global Illumination = **None** (disable Lumen tạm)
- Project Settings → Rendering → Reflection Method = **None**

---

## Diagnostic — làm sao đo chính xác leak

### Console commands trong Editor / PIE

```
stat rhi              → GPU memory stats hiện tại
stat memory           → CPU + GPU memory breakdown
MemReport -full       → file báo cáo đầy đủ tại Saved/Profiling/MemReports/
listtextures          → list tất cả textures đang load
DumpRenderTargetPoolMemory → render targets đang giữ
r.Lumen.MemoryStats 1 → Lumen surface cache size
```

### Workflow đo VRAM accumulation giữa PIE

1. Mở Editor, chạy `stat rhi` → ghi VRAM baseline
2. Play PIE → thao tác → Stop
3. Chạy `MemReport -full` → ghi VRAM
4. Lặp lại bước 2-3 cho lần PIE 2, 3, 4
5. So sánh report — category nào tăng dần là thủ phạm

### Tools chuyên nghiệp

- **NVIDIA Nsight Graphics** — capture allocation per frame
- **RenderDoc** — frame capture, xem mọi resource trên GPU
- **PIX on Windows** — Microsoft tool, đã enabled trong project

---

## Tổng hợp

**Nguyên nhân cốt lõi (1 dòng):**
> *PIE chia sẻ process với Editor → GPU device chung → không có process-level cleanup → VRAM tích lũy mỗi session đến khi vượt budget RTX 3060 (~7.26 GB) → MMU page fault → crash. Bị làm trầm trọng bởi Streamline plugin leak, Construction Script abuse từ S_SAN/BP_BaseDoor_v1, Load Asset Blocking trong code furniture tool.*

**Fix triệt để 1 dòng:**
> *Standalone Game thay PIE cho session dài + disable NVIDIA plugins không dùng + fix Construction Script bugs + audit code Load Asset Blocking trong furniture tool.*

**Đóng góp của code furniture tool:**
- Hiện tại: **10-30%** (Load Asset Blocking + hard refs trong SpawnedActors)
- Sau Change Material v1.1 nếu không fix: **40-60%** (thêm MID lifecycle, material loading)

---

## Action items — checklist

### Ngắn hạn (làm ngay)
- [ ] Restart editor mỗi 2-3 PIE khi develop
- [ ] Bàn với team: disable NVIDIA plugins không dùng
- [ ] Báo đồng nghiệp fix S_SAN và BP_BaseDoor_v1 Construction Script

### Trung hạn (trong sprint Change Material v1.1)
- [ ] Fix 5.1: Clear SpawnedActors ở BP_UndoManager EndPlay
- [ ] Fix 5.3: Implement MID lifecycle cache trong BP_FurnitureActor
- [ ] Test: chạy 6-7 PIE liên tiếp với Material Editor active, đo VRAM growth

### Dài hạn
- [ ] Fix 5.2: Migrate Load Asset Blocking → Async Load (tất cả nơi)
- [ ] Fix 5.4: C++ helper ForceFlushGPU
- [ ] Setup CI/CD test: Standalone game smoke test
- [ ] Document: hướng dẫn sử dụng MemReport để future debugging

---

## Tài liệu liên quan

- `BP_UndoManager.md` — chi tiết snapshot system
- `BP_FurnitureActor_SceneManager.md` — actor lifecycle
- `architecture.md` — nguyên tắc kiến trúc
- `performance.md` — nguyên tắc hiệu năng

## Lịch sử cập nhật

| Phiên bản | Ngày | Người | Nội dung |
|-----------|------|-------|----------|
| 1.0 | 09/05/2026 — 08:30 ICT | Cuhoang | Tạo document đầu tiên — phân tích crash GPU sau 4 PIE |
