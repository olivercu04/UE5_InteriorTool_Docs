# Performance — Nguyên tắc hiệu năng
**Phiên bản:** 1.1 | **Dự án:** Lighting_Mnger | **Cập nhật:** 20/05/2026 — 16:00 ICT

---

## Nguyên tắc cốt lõi

> **Ưu tiên hàng đầu: chạy mượt trên máy tính yếu.**
> Mọi quyết định kỹ thuật phải xét tới hiệu năng trước khi xét tới tính năng.

---

## Blueprint vs C++

- **Không loop lớn trong Blueprint** — giới hạn execution limit ~1852 iterations
- **Dùng C++ (UFurnitureFilterLibrary)** cho filter/search trên dataset lớn
- C++ nhanh hơn Blueprint ~100x với loop lớn

---

## Memory

- **KHÔNG load tất cả asset vào RAM** — dùng Soft Reference cho Thumbnail và Mesh
- **Soft Reference** = chỉ lưu đường dẫn, load thực tế khi cần
- **Load Asset Blocking** — chỉ dùng cho code cũ đã có, KHÔNG thêm mới (xem R1 trong architecture.md)
- **Async Load Asset** — bắt buộc cho mọi load mới từ v1.1 trở đi
- **Tile View virtualized** — chỉ render widget đang hiển thị, không tạo 100k widget

---

## TECHNICAL DEBT cần xử lý sau

**Vấn đề hiện tại:**
- Event Construct load toàn bộ DA_FurnitureItem vào RAM → AllFurnitureItems array
- ~200-400MB với 200k items — nặng khi mở inventory

**Giải pháp tối ưu (làm sau khi feature chính xong):**
- Dùng **Asset Registry** query trực tiếp từ disk index
- Không cần load DA_ vào RAM trước
- Chỉ load item match vào RAM khi search

---

## Data Pre-baked

- **Kích thước mesh** lưu vào DA_FurnitureItem (SizeX, SizeY, SizeZ) từ Python script
- Không tính `Get Actor Bounds` runtime mỗi lần cần
- **MeshFolderPath** populate bằng Python script quét Asset Registry — không tính runtime

---

## Event Tick

- **Chỉ làm việc nhẹ trong Tick** — không loop, không tạo object
- WBP_MeshControls Tick: chỉ Project World to Screen → Set Position
- BP_GizmoController Tick: LineTrace nhẹ cho hover highlight + movement

---

## Lazy Loading

- **Common Lazy Image** — chỉ load thumbnail khi card xuất hiện trên màn hình
- **Pagination 50 items/trang** — không add 10k item vào Tile View cùng lúc
- **Load Asset Blocking** chỉ khi drop mesh vào scene — không preload tất cả mesh

---

## Không làm

- ❌ WrapBox cho danh sách lớn — không virtualize
- ❌ Get All Widgets of Class trong OnListItemObjectSet — quá nặng
- ❌ Loop Blueprint qua 1000+ items
- ❌ Spawn nhiều actor không cần thiết

---

## Material v1.1 — Performance Patterns

- **Async Load Asset** thay Load Asset Blocking cho mọi load material mới
- **Debounce CaptureSnapshot 0.5s** — không capture sau mỗi frame hover, chỉ capture khi user dừng
- **Common Lazy Image** cho thumbnail swatch — chỉ load texture khi widget visible
- **FilterMaterialItems C++** — 2738 rows, Blueprint loop hit execution limit → bắt buộc C++
- **Soft Object Reference ThumbnailMI** — không hard load 2738 textures vào RAM

## VRAM Leak Prevention

Hard ref đến UObject giữ `Actor → StaticMesh → Render data → VRAM` sống sau Destroy.

**Pattern bắt buộc:**
- Actor Blueprint: clear hard refs ở **Event End Play**
- Widget Blueprint: clear hard refs ở **Event Destruct**

**Đã apply:**
- BP_UndoManager EndPlay: SpawnedActors, FoundActor, TempMeshes, RestoredBPActor
- WBP_FurnitureInventory Destruct: TargetFurnitureActor, PendingRestoredActor
- WBP_MaterialCard Destruct: MaterialItem, InventoryRef

**Workaround:** Restart editor mỗi 2-3 PIE, dùng Standalone (Alt+P) cho session dài.
