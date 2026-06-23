# BACKEND PLAN v1.0 — Từ tool thành app
**Phiên bản:** 1.0 | **Ngày:** 11/06/2026 — Fable 5 | Lighting_Mnger → App thương mại
**Đối tượng đọc:** cuhoang (quyết định) + model thực thi (khi tới phase B1+). Khớp `Future_Architecture_1M_Assets.md` (phase v2-v4) và roadmap v3.1.

---

## 0. ĐỊNH NGHĨA "APP" & NGUYÊN TẮC TỐI THƯỢNG

**App = UE5 desktop app (packaged) + backend dịch vụ.** Backend KHÔNG thay thế gì đang chạy — nó là tầng cộng thêm: tài khoản, scene trên mây, thư viện cloud, chợ combo, share.

**Nguyên tắc tối thượng — OFFLINE-FIRST:**
> App phải chạy ĐẦY ĐỦ khi không có mạng (EMS local, thư viện đóng gói sẵn). Mất mạng = mất tính năng cloud, KHÔNG mất tool. Mọi tính năng backend đều là "thêm", không bao giờ là "điều kiện để mở app".

Lý do: (1) target user máy yếu + mạng VN không ổn định; (2) backend chết (hết tiền server, provider sập) thì sản phẩm vẫn sống; (3) đơn giản hóa kiến trúc client gấp 10 lần.

**Vị trí trong roadmap (KHÔNG đổi thứ tự hiện tại):**
```
Sprint 4 → Gate 1 → Sprint D → Sprint 5 Combo → Sprint 7 → Sprint 6 → Gate 2 (packaged)
→ Refactor Phase B → [B0 có thể làm song song từ đây] → B1 → B2 → B3 → B4 → B5
```
> ⚠ KHÔNG nhảy vào backend trước Gate 2. Lý do cứng: (a) B1 cần packaged build để test thật; (b) B3 (chợ combo) cần format combo JSON từ Sprint 5; (c) B2 cần nền RowName từ Sprint D. Backend xây trên 3 viên gạch đó — gạch chưa nung xong thì chưa xây.

---

## 1. STACK CHỐT

| Tầng | Chọn | Vì sao (cho solo dev không biết backend) |
|---|---|---|
| Backend chính | **Supabase** (Postgres + Auth + Storage + Edge Functions + RLS) | Đã nằm trong lộ trình của mày. 1 dịch vụ thay 5 (DB, auth, file, API, realtime). Free tier đủ cho toàn bộ giai đoạn dev + beta. Dashboard trực quan, viết SQL là chính — KHÔNG cần dựng server. |
| Region | **Singapore (ap-southeast-1)** | Gần VN nhất, latency ~30-50ms |
| File 3D nặng (.glb) — phase B4 | **Cloudflare R2 + CDN** | Egress MIỄN PHÍ — chi phí thật của app 3D là băng thông tải mesh, không phải storage. Supabase Storage dùng cho thumbnail/scene JSON (nhỏ), R2 cho .glb (nặng). Chưa cần tới B4 thì chưa tạo. |
| Client HTTP | **C++ FHttpModule trong FurnitureToolkit**, expose BlueprintCallable async node | Plugin C++ đã có sẵn làm chỗ chứa; đây là bài học C++ bước 2 tự nhiên (sau FilterFurnitureRows). Prototype nhanh có thể dùng plugin VaRest (free, Blueprint thuần) rồi thay dần. |
| Payment | **Web checkout bên ngoài app** (mục B3) | KHÔNG BAO GIỜ xử lý thẻ trong UE app. App chỉ mở browser + verify entitlement. |
| Serialize | **JSON** (scene, combo, catalog) | Combo S5 đã chọn JSON; scene cloud dùng CÙNG schema family → 1 serializer dùng 3 nơi. |

**Những thứ CỐ TÌNH KHÔNG dùng (chống over-engineering):**
Kubernetes/Docker, microservices, GraphQL, server game riêng, realtime collab (chưa cần — B5 mới xét), tự viết auth. Solo dev + 1 backend service quản lý được. Thêm mảnh nào = thêm thứ để chết.

---

## 2. NGUYÊN TẮC AN NINH (S1-S6 — bắt buộc như R1-R5)

- **S1:** Client CHỈ giữ `anon key` (public). `service_role key` KHÔNG BAO GIỜ vào app/repo — chỉ sống trong Edge Functions.
- **S2:** **RLS (Row Level Security) bật trên MỌI bảng** ngay khi tạo. Mặc định deny; mở từng policy. Đây là hàng rào duy nhất giữa user A và data user B — vì client gọi thẳng DB.
- **S3:** File private (scene, combo chưa mua) tải qua **signed URL có hạn** (TTL 1-24h), không public bucket.
- **S4:** **Entitlement check ở server** (RLS/Edge Function). Client nói "tao đã mua" = vô nghĩa; DB nói mới tính. Giá tiền cũng đọc từ DB, không tin số client gửi lên.
- **S5:** Không tin bất kỳ dữ liệu nào client gửi: validate kích thước file, đuôi file, JSON schema version, độ dài string ở server.
- **S6:** Mọi JSON/schema có field `version` ngay từ v1 (bài học snapshot Version=3 — mày đã làm đúng ở client, lặp lại ở server).

---

## 3. CÁC PHASE

### B0 — CHUẨN BỊ (1-2 ngày, làm được NGAY song song không đụng UE)
Mục tiêu: hạ tầng tồn tại + mày hiểu khái niệm, chưa viết dòng UE nào.
1. Tạo tài khoản + project Supabase (free), region Singapore. Lưu URL + anon key vào file riêng NGOÀI repo.
2. Bật Auth: Email OTP (magic link/mã 6 số) — KHÔNG password (đỡ quên mật khẩu, đỡ reset flow, đỡ lưu trữ nhạy cảm). Google OAuth thêm sau nếu cần.
3. Học 3 khái niệm qua dashboard (mỗi cái 30 phút, có UI trực quan): Table Editor + RLS policy, Storage bucket + signed URL, Edge Function hello-world.
4. Đăng ký domain (tên app) — cần cho email auth + web checkout sau này.
5. **Deliverable:** project sống + 1 trang note "Backend_Credentials" (ngoài repo) + quyết định tên app.

### B1 — AUTH + CLOUD SCENE SAVE (vertical slice đầu tiên, sau Gate 2; ~1-2 tuần)
Tính năng user thấy: *Đăng nhập → bấm "Lưu lên mây" → mở máy khác → "Tải về" → scene y nguyên.*
1. **UE HTTP layer (C++ FurnitureToolkit):** 3 node async đầu tiên — `SB_SignInOTP(Email)`, `SB_VerifyOTP(Email, Code) → AccessToken`, `SB_Request(Method, Path, JsonBody, AuthToken) → Response`. Token giữ trong GameInstance (RAM); refresh token lưu SaveGame riêng (chấp nhận mức bảo mật này cho v1, ghi chú nâng cấp sau).
2. **Serializer scene → JSON v1:** đi qua actor tag "FurnitureSpawned": `{version, name, placements:[{rowName, loc, rot, scale, materialOverrides, surfaceType, groupID}], groups:[S_GroupData]}` — chính là cấu trúc snapshot v3 + RowName (D.T8). **Tái dùng serializer combo của Sprint 5** — không viết bản thứ hai.
3. **DB:** bảng `scenes` + RLS owner-only (mục 4). Save = upsert row (JSON cột `data jsonb`); Load = select + spawn lại qua `SpawnFurnitureCopy` (đường spawn duy nhất từ G1.T2 — mọi mảnh ghép cũ đều dùng lại được).
4. **UI:** nút Đăng nhập + danh sách scene cloud (panel đơn giản, list view).
5. **DONE khi:** save từ máy A → load máy B đúng 100% (mesh, vị trí, material, group); mất mạng → nút cloud disabled, app vẫn chạy; logout → không thấy scene người khác (test RLS thật).

### B2 — CLOUD CATALOG (đồng bộ thư viện; khớp Future_Architecture phase v2; ~1-2 tuần)
Tính năng: cập nhật thư viện sản phẩm KHÔNG cần build lại app.
1. Bảng `assets` (catalog) trên Postgres = bản sao DT_FurnitureCatalog (nguồn gốc dữ liệu vẫn là pipeline Sheets của mày — thêm 1 bước Python push lên Supabase).
2. Client: lúc khởi động (có mạng) gọi `GET /assets?updated_after=<lastSync>` → ghi đè/merge vào nguồn local (giai đoạn đầu: file JSON local → nạp vào DT runtime hoặc cấu trúc song song; khi >50k chuyển SQLite đúng phase v2). Thumbnail mới tải từ Storage CDN, cache disk.
3. **Quy tắc:** app KHÔNG chờ sync để mở — sync chạy nền, có gì dùng nấy.
4. **DONE khi:** thêm 1 sản phẩm trên server → user mở app thấy sản phẩm mới không cần update app.

### B3 — COMBO MARKETPLACE 💰 (revenue; ~3-4 tuần)
> ⚠️ **23/06/2026:** B3 chợ BỊ GÁC cho đến khi ownership rõ ràng (quyết định B1 Sprint5_Plan_v1.1). Schema combo đã chừa AuthorID/Visibility — không mất công sau khi ownership chốt.

Tính năng: đăng combo lên chợ → người khác xem/mua → tải về dùng.
1. **DB:** `combos` (metadata + data jsonb + price + status draft/published), `purchases` (log giao dịch), `entitlements` (quyền dùng — nguồn sự thật khi check), `favorites`.
2. **Upload/publish:** từ app — serialize combo (S5) → insert `combos` + thumbnail lên Storage. Trạng thái `draft` → mày duyệt → `published` (moderation tay giai đoạn đầu, chợ nhỏ).
3. **Browse:** tab "🧩 Combo" trong inventory (đã dự kiến Sprint 5) thêm nguồn "Chợ" — gọi API list published, hiện card + giá.
4. **Mua — flow an toàn cho solo dev VN:**
   ```
   App → mở browser tới trang checkout (web)
   → cổng thanh toán xử lý (KHÔNG qua app)
   → webhook → Edge Function verify chữ ký → INSERT entitlements
   → app poll/refresh → thấy entitlement → cho tải combo (signed URL)
   ```
   Lựa chọn cổng: **(a)** Merchant-of-Record quốc tế (Lemon Squeezy / Paddle — họ lo thuế + thẻ, trả tiền về mày; **kiểm tra điều kiện chi trả cho cá nhân VN trước khi chốt**), **(b)** khách VN: PayOS/SePay (QR chuyển khoản, phí thấp, hợp khẩu vị VN). Có thể chạy cả hai. Đây là quyết định kinh doanh — mục 7 câu hỏi 2.
5. **Free combo trước, paid sau:** B3 chia 2 nửa — B3a (chợ free, không payment) ship trước để validate hành vi share/tải; B3b (payment) chỉ làm khi B3a có người dùng thật. Đỡ xây quầy thu ngân cho cửa hàng chưa ai vào.
6. **DONE B3a:** user A đăng combo → user B thấy + tải + spawn đúng (GroupID remap S5 chạy với combo từ mạng). **DONE B3b:** mua test 1 giao dịch thật end-to-end, entitlement cấp đúng, refund flow có quy trình tay.

### B4 — USER UPLOAD ASSET (glTFRuntime; khớp phase v3-v4; ~1-2 tháng)
Tính năng: user upload mesh riêng (.glb) → dùng trong scene/combo của họ.
1. Client: validate local (đuôi .glb/.gltf, size ≤ 50MB, tri-count trần) → upload R2 qua signed upload URL (Edge Function cấp) → row `assets` loại `user_upload`, owner = user.
2. Load: glTFRuntime tải từ CDN → spawn; disk cache LRU (theo Future_Architecture mục 5). **Test glTFRuntime với 1 mesh đơn giản TRƯỚC khi xây pipeline** (checklist v4 của chính mày).
3. Hệ quả kiến trúc client: `BP_FurnitureActor` cần phân biệt nguồn (RowName catalog vs AssetID cloud) — thêm field `SourceType`. Scene/combo JSON v2 mang được cả hai (field version cứu mày ở đây — S6).
4. Moderation + quota (vd 1GB/user free) + virus scan (Edge Function gọi dịch vụ scan hoặc tối thiểu: chỉ nhận .glb, parse validate header).
5. **DONE khi:** upload từ máy A → dùng trong combo → user B tải combo → mesh hiện đúng trên máy B.

### B5 — SHARE, TELEMETRY, VẬN HÀNH (~2-3 tuần, rải)
1. Share link scene/combo (`app.ten-app.com/c/<id>` → trang web preview thumbnail + nút "Mở trong app" deep link).
2. Favorites/Recent sync cloud (UserPrefsManager đã RowName-based — map thẳng lên bảng `favorites`).
3. Telemetry tối thiểu: crash report + đếm sự kiện chính (open, save, spawn combo) — bảng `events`, gửi batch, **có opt-out**. Không SDK analytics nặng.
4. Vận hành: bật Point-in-Time backup khi có user trả tiền; bảng `app_versions` cho thông báo update; trang status đơn giản.

---

## 4. SCHEMA v1 (SQL phác — chạy ở B1, mở rộng dần)

```sql
-- profiles: 1-1 với auth.users
create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text, created_at timestamptz default now()
);

create table scenes (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null references profiles(id),
  name text not null,
  data jsonb not null,            -- scene JSON {version, placements[], groups[]}
  schema_version int not null default 1,
  updated_at timestamptz default now()
);
alter table scenes enable row level security;
create policy "owner_all" on scenes for all
  using (auth.uid() = owner) with check (auth.uid() = owner);

create table assets (                 -- B2 catalog + B4 user upload
  row_name text primary key,          -- = RowName của DT (Sprint D!)
  source_type text not null default 'catalog',  -- catalog | user_upload
  owner uuid references profiles(id), -- null nếu catalog
  vie_name text, eng_name text, category text,
  mesh_folder_path text, bounding_size jsonb,
  thumbnail_url text, file_url text,  -- file_url: B4 (.glb trên R2)
  tags text, updated_at timestamptz default now()
);

create table combos (                 -- B3
  id uuid primary key default gen_random_uuid(),
  owner uuid not null references profiles(id),
  name text not null, description text,
  data jsonb not null,                -- combo JSON từ Sprint 5
  schema_version int not null default 1,
  thumbnail_url text,
  price_vnd int not null default 0,   -- 0 = free
  status text not null default 'draft',  -- draft | published | removed
  created_at timestamptz default now()
);
alter table combos enable row level security;
create policy "read_published" on combos for select
  using (status = 'published' or auth.uid() = owner);
create policy "owner_write" on combos for insert with check (auth.uid() = owner);
create policy "owner_update" on combos for update using (auth.uid() = owner);

create table entitlements (           -- nguồn sự thật quyền dùng (B3b)
  user_id uuid references profiles(id),
  combo_id uuid references combos(id),
  granted_at timestamptz default now(),
  source text,                        -- purchase | gift | promo
  primary key (user_id, combo_id)
);
alter table entitlements enable row level security;
create policy "read_own" on entitlements for select using (auth.uid() = user_id);
-- INSERT chỉ qua Edge Function (service_role) — KHÔNG có policy insert cho client

create table purchases (              -- log giao dịch, ghi bởi webhook
  id uuid primary key default gen_random_uuid(),
  user_id uuid, combo_id uuid, amount_vnd int,
  provider text, provider_ref text, created_at timestamptz default now()
);

create table favorites (
  user_id uuid references profiles(id),
  item_type text, item_key text,      -- 'mesh'|'material'|'combo' + RowName/id
  primary key (user_id, item_type, item_key)
);
alter table favorites enable row level security;
create policy "owner_all" on favorites for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
```
> Quy ước: mọi bảng mới = `enable row level security` NGAY câu lệnh sau create. Quên RLS = lộ data — lỗi backend số 1 của người mới.

**Storage buckets:** `thumbnails` (public, CDN) | `scenes-export` (private) | B4: R2 bucket `assets-glb` (private, signed URL).

---

## 5. UE5 CLIENT — TẦNG HTTP (FurnitureToolkit)

Node C++ BlueprintCallable async (latency thật → BẮT BUỘC async, đúng R1):
```
SB_SignInOTP(Email)                          → OnSent / OnError
SB_VerifyOTP(Email, Code)                    → OnSuccess(AccessToken, RefreshToken) / OnError
SB_Request(Verb, Path, JsonBody, Token)      → OnResponse(Code, JsonString) / OnError(Code, Msg)
SB_DownloadFile(SignedURL, LocalPath)        → OnProgress(Pct) / OnDone(Path) / OnError
SB_UploadFile(SignedURL, LocalPath)          → OnProgress / OnDone / OnError        ← B3+
```
Quy tắc client:
- Mọi callback về **game thread** trước khi đụng UObject/UI.
- JSON parse bằng `FJsonObjectConverter` (C++) hoặc node JSON sẵn có — KHÔNG string-split tay.
- Timeout 15s + 1 retry; lỗi mạng → toast "Không có kết nối — tính năng cloud tạm tắt", KHÔNG modal chặn.
- Token hết hạn (401) → tự refresh 1 lần → fail thì đăng xuất êm.
- **Mọi tính năng cloud nằm sau Branch `bIsSignedIn && bIsOnline`** — default False, app chạy như hiện tại.

---

## 6. CHI PHÍ & NGƯỠNG

| Giai đoạn | Hạ tầng | Chi phí/tháng |
|---|---|---|
| B0-B2 (dev, beta nhỏ) | Supabase Free | $0 |
| B3 (chợ chạy, <vài nghìn user) | Supabase Pro | ~$25 |
| B4 (file .glb, băng thông tăng) | + R2 | ~$5-20 (storage rẻ, egress $0) |
| Payment | MoR/cổng VN | % theo giao dịch (LS ~5%+phí; PayOS ~thấp hơn nhiều cho QR) |
**Ngưỡng hành động:** Supabase Storage egress > ~100GB/tháng → chuyển file nặng sang R2 (kế hoạch B4 đã làm sẵn). DB > vài chục GB hoặc query catalog chậm → đúng lúc SQLite-sync phase v2 phát huy (client không query thẳng catalog nữa).

---

## 7. CÂU HỎI CẦN CUHOANG CHỐT (trước B1/B3)

1. **Mô hình tiền:** bán combo lẻ? subscription thư viện? app trả phí 1 lần + chợ? → quyết định B3b xây gì. Đề xuất khởi điểm: app free + combo trả phí lẻ (đúng "combo = revenue chính").
2. **Pháp lý nhận tiền:** cá nhân hay lập hộ KD/công ty? Quyết định cổng thanh toán dùng được. Kiểm tra điều kiện Lemon Squeezy/Paddle cho cá nhân VN TRƯỚC khi code B3b.
3. **Ownership với đồng nghiệp** (nhắc lần 3 + quyết định 23/06): **B1 ownership — DEFAULT chốt: combo CHỈ local trong Sprint 5, KHÔNG bật chợ tới khi rõ ownership**. Schema đã chừa AuthorID/Visibility (Private default). KHÔNG thêm GlobalAssetID bây giờ (serializer đã tolerant với field mới). Giới hạn cross-catalog (combo chỉ dùng được khi máy đích cùng asset pool) = giới hạn Phase B, ghi rõ trong UI C11. Chốt phân chia doanh thu TRƯỚC khi làm B3a.
4. **Tên app + domain** — cần từ B0 (email auth + checkout page).
5. **Quy mô beta:** bao nhiêu người dùng thử đầu tiên, lấy từ đâu (cộng đồng nội thất VN? đồng nghiệp ngành?) — quyết định B3a có ý nghĩa hay không.

---

## 8. RỦI RO RIÊNG CỦA BACKEND (biết trước, đỡ đau sau)

1. **Lộ service key** → S1, kiểm repo trước mọi commit. 2. **Quên RLS** → quy ước mục 4. 3. **Schema JSON đổi làm hỏng scene cũ** → S6 + converter mỗi lần bump version (như snapshot v1→v3 mày đã làm). 4. **Phụ thuộc 1 provider** → mọi data export được (Postgres dump + JSON), không dùng tính năng độc quyền khó thay. 5. **Backend ngốn thời gian vô hạn** → mỗi phase có DONE cứng; không polish server khi client còn bug. 6. **Combo lậu (tải rồi share file)** → chấp nhận ở quy mô nhỏ; signed URL + entitlement đủ chặn casual; DRM thật không đáng công solo dev.

---

## Lịch sử
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 11/06/2026 | Tạo mới — stack Supabase+R2, nguyên tắc S1-S6, phase B0-B5, schema v1, HTTP layer, chi phí, câu hỏi mở. |
| 1.1 | 23/06/2026 | Ghi nhận quyết định B1 (23/06): combo chỉ local Sprint 5, chợ B3 gác đến khi rõ ownership. KHÔNG thêm GlobalAssetID. Cross-catalog giới hạn là Phase B. Cập nhật câu hỏi 3 + note đầu mục B3. |
