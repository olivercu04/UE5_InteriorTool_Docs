# Kiến trúc tương lai — Thư viện 1 triệu Asset
**Phiên bản:** 1.0 | **Tạo:** 13/05/2026 — 22:30 ICT | Project: Lighting_Mnger (UE5.5.4)

---

## Tại sao cần kiến trúc riêng?

Khi số asset vượt ngưỡng nhất định, kiến trúc UE truyền thống (UObject + DataTable + UE asset) **chắc chắn vỡ**:

| Vấn đề | Biểu hiện |
|---|---|
| Asset Registry 1M+ UObject | Mở editor mất vài phút, crawl chậm |
| DataTable 1M rows | Parse chậm, RAM nặng |
| 1M thumbnail UE asset | 50GB+ local disk, không thể distribute |
| Load toàn bộ vào RAM | Crash VRAM/RAM ngay cả máy mạnh |

→ Phải **thoát khỏi UE asset pipeline** cho data layer, chỉ giữ UE cho rendering.

---

## Nguyên tắc cốt lõi

```
Không coi thumbnail là UE asset thông thường.
Không load bằng DataAsset trực tiếp.
Không load toàn bộ.
Dùng database metadata.
Dùng blob store hoặc image pack cho thumbnail.
Dùng virtualized UI.
Load async theo vùng nhìn thấy.
Cache LRU.
Unload liên tục.
Chỉ load asset thật khi user chọn.
```

---

## Mô hình chuẩn

```
SQLite Metadata + Blob Store Thumbnail + Async Loader + LRU Cache + Soft Reference AssetPath
```

### Vai trò từng thành phần

| Thành phần | Làm gì | Thay thế cái gì |
|---|---|---|
| **SQLite Metadata** | Lưu tên, path, tag, type, size, thumbnail_key | DataTable + DA_FurnitureItem |
| **Blob Store / Filesystem Thumbnail** | Lưu thumbnail binary ngoài UE asset | Texture2D UE asset |
| **Async Loader** | Load thumbnail theo viewport, không block | Soft Reference resolve blocking |
| **LRU Cache** | Giữ N thumbnail gần nhất trong RAM, tự giải phóng | Không có — hiện tại không unload |
| **Soft Reference AssetPath** | Chỉ giữ đường dẫn string, resolve khi user click | Không pre-register UE asset |
| **glTFRuntime / Custom Loader** | Load mesh/material từ cloud hoặc file ngoài UE | UE asset `.uasset` cứng trong project |

---

## Chi tiết từng thành phần

### 1. SQLite Metadata

**Tại sao SQLite:**
- 1 triệu rows × ~200 bytes = ~200MB — 1 file duy nhất, query nhanh
- Hỗ trợ full-text search (FTS5) → tìm tên material không cần C++ custom filter
- Cross-platform, không cần server
- Vượt 10 triệu rows → nâng lên PostgreSQL/Firestore, code query ít thay đổi

**Schema ví dụ:**
```sql
CREATE TABLE assets (
  id          TEXT PRIMARY KEY,   -- RowName / AssetID
  name_vn     TEXT,
  name_en     TEXT,
  type        TEXT,
  style       TEXT,
  folder_path TEXT,
  asset_path  TEXT,               -- /Game/... hoặc cloud URL
  thumb_key   TEXT,               -- key trong blob store
  tags        TEXT,               -- JSON array
  created_at  INTEGER
);

CREATE VIRTUAL TABLE assets_fts USING fts5(name_vn, name_en, tags);
CREATE INDEX idx_folder ON assets(folder_path);
CREATE INDEX idx_type ON assets(type);
```

**Khi nào chuyển sang SQLite:**
- Khi DataTable vượt ~50k rows và query bắt đầu chậm
- Khi cần full-text search tiếng Việt
- Khi bắt đầu sync metadata từ server

---

### 2. Blob Store cho Thumbnail

**Vấn đề với Atlas:**
- 1M thumbnail = 1000 atlas files (8192×8192 chứa ~1024 thumb 256×256)
- Khi user upload asset mới → phải pack lại atlas hoặc quản lý fragmentation
- Atlas tốt cho dataset **cố định** (game ship), không tốt cho library **mở**

**Khuyến nghị cho library mở (user upload):**

| Approach | Phù hợp khi | Nhược điểm |
|---|---|---|
| **Folder hashing** `/thumbs/ab/cd/abcdef.webp` | Local, đơn giản | Filesystem overhead nếu > 10M files |
| **LMDB / RocksDB** | Local, cần đọc nhanh, ít write | Cần C++ binding |
| **Cloud Object Storage** (S3, R2, GCS) | Multi-user, cloud library | Cần internet, latency |
| **SQLite blob column** | Prototype, đơn giản nhất | Không scale quá 10GB |

**Format thumbnail khuyến nghị:**
- WebP (chất lượng tương đương PNG, nhỏ hơn 30-50%)
- Resolution: 256×256 đủ cho card 110×110 (không cần 1024×1024)
- Không cần mipmap — thumbnail không zoom
- Màu sắc: sRGB

---

### 3. Async Loader theo viewport

**Nguyên lý:**
```
Card visible → request load thumbnail (ID)
  → check LRU cache
    → hit: return ngay
    → miss: queue async task → load từ blob store → decode → update cache → notify card
Card scroll khỏi view → cancel pending request nếu chưa xong
```

**UE5 implementation:**
- `FAsyncTask` hoặc `UE::Tasks::Launch` cho background load
- `AsyncLoadTexture2D` với callback
- `FTickerDelegate` để update UI từ game thread sau khi load xong

---

### 4. LRU Cache

**Nguyên lý:** Giữ N thumbnail gần nhất trong RAM. Khi đầy → xóa cái ít dùng nhất.

**Budget hợp lý:**
- 256×256 WebP decoded ~256KB (RGBA)
- Cache 500 thumbnails = ~128MB RAM — OK
- Cache 2000 thumbnails = ~512MB — cần check với memory budget máy

**UE5 implementation:**
```cpp
TMap<FString, TWeakObjectPtr<UTexture2D>> LRUCache;
TArray<FString> AccessOrder; // front = most recent
const int32 MaxCacheSize = 500;

// Khi access:
// 1. Move key lên đầu AccessOrder
// 2. Nếu cache đầy → remove key ở cuối → GC collect texture
```

---

### 5. Asset thật từ Cloud (glTFRuntime)

Đây là bước thoát hoàn toàn khỏi UE asset pipeline:

```
User click asset → download .glb / .gltf từ CDN
→ glTFRuntime load runtime → spawn StaticMesh trong scene
→ Cache file .glb local (LRU theo disk space)
→ Lần sau load từ cache, không download lại
```

**Plugin:** `glTFRuntime` (đã có trong roadmap dự án)

**Lợi ích:**
- Asset không cần bake/cook vào UE project
- User upload mesh từ máy cá nhân → convert .glb → upload CDN → available cho tất cả
- Không giới hạn số asset (cloud storage gần như vô hạn)

---

## Roadmap triển khai từng phase

### Hiện tại — v1.x
**Số asset:** ~3k material + ~200k mesh
**Kiến trúc:** UE DataTable + UE Texture2D asset + settings tối ưu
**Việc cần làm ngay:**
- ✅ Texture Group = UI, LOD Bias = 2 cho thumbnail
- ✅ Common Lazy Image (lazy load)
- ✅ Common Tile View (virtualized rendering)

### Phase v2 — Cloud Library
**Số asset:** 10k-100k
**Thay đổi:**
- Tách metadata sang SQLite (giữ thumbnail UE asset tạm thời)
- Sync metadata từ server → client download SQLite file
- Bắt đầu dùng cloud Object Storage cho thumbnail mới

**Effort:** 2-3 tuần

### Phase v3 — User Upload + Share
**Số asset:** 100k-1M
**Thay đổi:**
- Toàn bộ thumbnail ra khỏi UE asset → blob store
- Async Loader + LRU Cache C++ implementation
- SQLite full-text search thay C++ Filter Library
- Soft Reference chỉ giữ cloud URL/path

**Effort:** 1-2 tháng

### Phase v4 — Asset thật từ Cloud
**Số asset:** 1M+
**Thay đổi:**
- glTFRuntime cho mesh/material load runtime
- CDN cho .glb files
- Download manager + disk cache (LRU by disk space)
- Không còn `.uasset` trong UE project cho asset thư viện

**Effort:** 1-2 tháng

---

## So sánh với industry

| Tool | Thumbnail | Metadata | Asset load |
|---|---|---|---|
| Quixel Megascans | CDN WebP | Cloud DB | Download .uasset |
| SketchFab | CDN WebP | Cloud API | Download .glb |
| Substance Source | CDN | Cloud API | Download .sbsar |
| Coohom | CDN | Cloud DB | Cloud render |
| **v1.x hiện tại** | UE Texture2D local | DataTable | UE asset local |
| **v4 target** | Cloud CDN WebP | SQLite + Cloud DB | glTFRuntime |

---

## Checklist khi bắt đầu từng phase

### Trước khi làm v2:
- [ ] Xác nhận format SQLite wrapper C++ (có thể dùng `sqlite3.h` trực tiếp)
- [ ] Chọn cloud provider (AWS S3 / Cloudflare R2 / Google Cloud)
- [ ] Thiết kế schema SQLite final (tránh migrate nhiều lần)

### Trước khi làm v3:
- [ ] Implement LRU Cache C++ (bắt đầu nhỏ: 200 items)
- [ ] Test async loader không block game thread
- [ ] Xác nhận memory budget thumbnail cache (tùy máy target)

### Trước khi làm v4:
- [ ] Test glTFRuntime với 1 mesh đơn giản
- [ ] Thiết kế download manager (queue, retry, priority)
- [ ] Định nghĩa disk cache size (vd: 2GB local cache)

---

## Ghi chú

- **Không làm hết 1 lần** — triển khai từng phase khi thực sự cần
- **v1.x chạy ổn** với kiến trúc hiện tại cho vài nghìn asset
- **Atlas thumbnail** tốt cho dataset cố định (game), không tốt cho library mở (user upload)
- **glTFRuntime** là mắt xích quan trọng nhất cho tương lai cloud — nên làm quen sớm
- **SQLite** có thể làm ngay trong v2 mà không phá v1.x (chạy song song)

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 13/05/2026 — 22:30 ICT | Tạo mới — kiến trúc 1M asset, roadmap v1→v4, so sánh industry |
