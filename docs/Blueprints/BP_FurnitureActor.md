# BP_FurnitureActor
**Tách từ:** `BP_FurnitureActor_SceneManager.md` (phần Actor)
**Phiên bản:** 2.4 | **Cập nhật:** 11/09/2026 (G5.4) — `ApplyMaterialByRowName` +khối `AddRecentMaterial` (fix bug #5 — kéo-thả thiếu ghi Recent). Xóa thật `Debug_TestApplyMaterial` (scaffolding, dọn xong). Regression 8/8 PASS. GATE G5 ĐÓNG HẲN | Parent: StaticMeshActor | Interface: EMSActorSaveInterface

**Phiên bản:** 2.3 | **Cập nhật:** 11/09/2026 — S7.G5.2: thêm Custom Event `ApplyMaterialByRowName` (engine kéo-thả material, DT lookup → async load → apply → capture → refresh swatch) + 3 biến `Apply_Pending*`. 2 bug fix trong phiên (Branch thừa chặn nhánh Row Not Found; X3 refresh swatch sai lớp + so sánh sai kiểu). ⚠️ Code thật còn 1 chỗ debug scaffolding (`Debug_TestApplyMaterial`) CHƯA xóa, chờ G5.4 | Parent: StaticMeshActor | Interface: EMSActorSaveInterface

**Phiên bản:** 2.2 | **Cập nhật:** 07/09/2026 — S7.G3 Item 1+2: `ActorLoaded` reroute sang `RestoreMyMaterialSlots` (thay ForEachLoop MaterialOverrides cũ); `LoadMeshAsync` +Branch gọi restore đúng lúc mesh sẵn sàng (fix race); merge lần đầu `RestoreMyMaterialSlots`/`Rst_LoadNextSlot` + 2 biến `Rst_SlotIdx`/`Rst_CurRecord` vào canonical | Parent: StaticMeshActor | Interface: EMSActorSaveInterface

> **v1.2 (Sprint D.T6):** Thêm `RowName : Name (SaveGame)` — nguồn sự thật mới thay DA_FurnitureItem. DAPath giữ lại làm fallback cho save cũ chưa có RowName.

---

## Variables
```
MeshPath              : String    ← SaveGame
DAPath                : String    ← SaveGame (giữ làm fallback cho save cũ — xem Branch RowName == "" trong load path)
RowName               : Name      ← SaveGame (v1.2 Sprint D) — khóa tra DT_FurnitureCatalog; "" = chưa set (save cũ)
MaterialOverrides     : Array of String ← SaveGame (v1.1) — package path MI theo slot index
MaterialParams        : Array of String ← SaveGame (v1.1 placeholder — JSON per slot cho v1.2)
PlacementSurfaceType  : Name      ← SaveGame — "Floor" | "Wall" | "Ceiling", default="Floor"
FurnitureMesh         : StaticMeshComponent (Mobility = Movable)
GroupID               : String    ← SaveGame (xác nhận Sprint 3 T2) — ID của group chứa actor; "" = đồ rời
MaterialSlots         : Array of FMaterialSlotRecord ← SaveGame (S7.G2 Bước 0, 05/09/2026) — kho ghi material theo tên slot (name-based), qua MaterialSlotService. Xem Data/MaterialSlotService_Reference.md
Rst_SlotIdx           : Integer   ← KHÔNG SaveGame (S7.G2/2B, merge canonical 07/09/2026) — con trỏ vòng lặp Rst_LoadNextSlot
Rst_CurRecord         : FMaterialSlotRecord ← KHÔNG SaveGame (S7.G2/2B, merge canonical 07/09/2026) — temp var, tránh đọc pure MaterialSlots.Get() 2 lần trong Rst_LoadNextSlot
Apply_PendingSlotName  : String   ← KHÔNG SaveGame (S7.G5.2, 11/09/2026) — giữ qua khe async trong ApplyMaterialByRowName
Apply_PendingSlotIndex : Integer  ← KHÔNG SaveGame (S7.G5.2, 11/09/2026) — cùng lý do trên
Apply_PendingRowName   : Name     ← KHÔNG SaveGame (S7.G5.2, 11/09/2026) — cùng lý do trên
```

---

## Event BeginPlay
```
GET Tags (Self) → SET TempTags → ADD "FurnitureSpawned" → SET Tags (Self)
```
> ⚠️ KHÔNG dùng SET Tags trực tiếp — EMS dùng Tags để track state.

---

## Event ActorLoaded (EMSActorSaveInterface) — AS-BUILT 07/09/2026 (S7.G3 Item 2)

> ⚠️ **Mâu thuẫn với mô tả canonical trước đây (v2.1 trở về trước):** bản cũ ghi có bước `GET
> Tags → ADD "FurnitureSpawned" → SET Tags` ngay sau `Set Static Mesh`. Delta 07/09/2026 (K2Node
> export thật, cuhoang paste trong chat) khẳng định bước ADD Tags này **KHÔNG tồn tại** trong
> graph thật — gọi đây là lỗi doc từ trước, không phải do phiên 07/09 gây ra. Ghi nhận theo delta
> (ground truth verify qua K2Node thật), không tự đối chiếu lại được — nếu phát hiện ngược lại,
> báo lại để đối chiếu.

**Flow gốc (đã tồn tại từ trước 07/09/2026, doc cũ quên ghi đoạn restore material — bổ sung cho
đúng lịch sử; đã bị THAY bằng Flow MỚI bên dưới):**
```
Event ActorLoaded (EMSActorSaveInterface) ▶→
  AsyncWaitForOperation(CheckType=CT_Load)
  OnCompleted ▶→ Branch(MeshPath != "")
    False ▶→ Destroy Actor (Self)
    True ▶→ LoadAsset_Blocking(MakeSoftObjectPath(MeshPath)) ●→ Cast StaticMesh
           CastFailed → (dead-end — mesh load fail thì không cần restore material nữa, giữ nguyên)
           True ▶→ SetStaticMesh(FurnitureMesh, AsStaticMesh)
                ▶→ [XÓA 07/09/2026] ForEachLoop(Array=MaterialOverrides)
                     LoopBody ▶→ Branch(ArrayElement == "")
                       True  → (dead-end, skip slot rỗng)
                       False ▶→ LoadAsset_Blocking(MakeSoftObjectPath(ArrayElement)) ●→ Cast MaterialInterface
                                CastFailed → (dead-end, skip slot lỗi)
                                True ▶→ CreateDynamicMaterialInstance(Parent=AsMaterialInterface)
                                     ▶→ SetMaterial(FurnitureMesh, ElementIndex=ArrayIndex, Material=MID)
                     Completed → (dead-end — không có gì sau, kể cả ADD Tags — doc cũ ghi sai là
                                    có ADD Tags "FurnitureSpawned" ở đây, THỰC TẾ KHÔNG CÓ)
```

**Flow MỚI (07/09/2026 — S7.G3 Item 2):**
```
Event ActorLoaded (EMSActorSaveInterface) ▶→
  AsyncWaitForOperation(CheckType=CT_Load)
  OnCompleted ▶→ Branch(MeshPath != "")
    False ▶→ Destroy Actor (Self)
    True ▶→ LoadAsset_Blocking(MakeSoftObjectPath(MeshPath)) ●→ Cast StaticMesh
           CastFailed → (dead-end — giữ nguyên, xác nhận đúng ý thiết kế)
           True ▶→ SetStaticMesh(FurnitureMesh, AsStaticMesh)
                ▶→ Call RestoreMyMaterialSlots     ← [MỚI] thay toàn bộ khối ForEachLoop cũ
```

---

## Async Load Events (v2.0 — 19/06/2026)
Đặt trong BP_FurnitureActor, KHÔNG phải InputManager. Lý do: mỗi instance actor có node graph riêng → nhiều actor load song song không share class var, không aliasing.

### LoadMeshAsync(MeshPath : String) — Custom Event — SỬA 07/09/2026 (S7.G3, fix race)
```
Make Soft Object Path(MeshPath) → To Soft Object Reference → Async Load Asset

Completed:
  Cast Object → As Static Mesh
  Branch IsValid(As Static Mesh):
    True  → GET FurnitureMesh (Self) → Set Static Mesh(New Mesh = As Static Mesh)
            ▶→ [THÊM 07/09/2026] Branch(GET MaterialSlots.Length > 0)
                 True  → Call RestoreMyMaterialSlots
                 False → (không đổi — hành vi cũ nguyên vẹn cho Paste/Duplicate/drag-drop)
    False → Print "LoadMeshAsync fail: " + MeshPath  [Development Only]
```
Self = actor tự set mesh của chính nó. Không cần TargetActor.

**Lý do (root cause, chẩn đoán bởi Opus + verify bằng log thật):** `SpawnFurnitureCopy` gọi
`LoadMeshAsync` bất đồng bộ — mesh thật chỉ sẵn sàng ở `Completed`. Các caller (Combo Sub-step C,
`RestoreSnapshot`) gọi `Call RestoreMyMaterialSlots` NGAY sau `SpawnFurnitureCopy` return (cùng
frame) — mesh chưa load xong — restore chạy trên mesh rỗng, im lặng fail. Fix: dời điểm gọi vào
đúng lúc mesh CHẮC CHẮN sẵn sàng (`LoadMeshAsync.Completed`), guard bằng `MaterialSlots.Length>0`
để không đổi hành vi các caller chưa dùng hộ `MaterialSlots`.

**Bằng chứng phụ có sẵn từ trước (không phải phiên 07/09 tạo ra):** `Plans/P2_StudioThumbnail_Execution.md`
Việc 4 đã có `Delay(0.5)` với ghi chú *"chờ LoadMeshAsync (asset resident, resolve nhanh)"* —
workaround thủ công cho đúng race này, tồn tại từ trước, xác nhận đây không phải bug mới.

⚠️ **Việc còn treo (CHƯA làm, xem Session_State.md mục "Việc tiếp theo"):** `RestoreSnapshot` Step 4
(`BP_UndoManager`) vẫn còn dòng `Call NewActor.RestoreMyMaterialSlots` thừa ngay sau `SET
NewActor.MaterialSlots` — race tương tự nghi vấn dính ở đây (Opus chẩn đoán), nhưng phiên 07/09
CHỈ sửa đường Combo (mục này + `BP_ComboManager.md` Sub-step C), CHƯA đụng `RestoreSnapshot`.
KHÔNG hỏng chức năng (vì `LoadMeshAsync` giờ tự phủ), nhưng dư 1 lần gọi sớm vô hiệu mỗi lần
Undo/Redo material — CHƯA test regression Undo/Redo material sau đợt fix này.

---

### RestoreMyMaterialSlots — Custom Event — MỚI merge vào canonical 07/09/2026

> Chuỗi tuần tự trên actor instance riêng (không aliasing — mỗi actor 1 graph riêng). Thân hàm đã
> code+test PASS từ S7.G2/Việc 2B (03-04/09/2026, nhánh sạch chưa có legacy) + S7.G3 Item 1
> (07/09/2026, thêm nhánh legacy đầu hàm + fix dead-end nhánh `False`) — đây là LẦN ĐẦU hàm này
> được ghi vào canonical `BP_FurnitureActor.md` (trước đó chỉ có trong working plan
> `Sprints/Sprint7/S7G2_Reroute_ExecutionPlan_27aug2026.md`).

**Bug phát sinh 07/09/2026 (đã fix, xem `Bugs/Open_Bugs.md`):** khi wire tay nhánh legacy sáng
07/09, pin `Branch.False` (đường KHÔNG legacy — actor đã có `MaterialSlots` sẵn) bị để trống
(dead-end) thay vì merge vào cùng điểm `ResetAllSlotsToAssetDefault` như nhánh `True`. Vi phạm L2
(dead-end trong Custom Event chain = fatal). Phát hiện qua: test Combo không in Print debug nào
bên trong `Rst_LoadNextSlot` dù `RestoreMyMaterialSlots CALLED` có log — chết ngay ở Branch đầu
hàm. Xác nhận bằng ảnh chụp graph cuhoang gửi. Flow dưới đây là bản ĐÃ FIX.

```
RestoreMyMaterialSlots ▶→
  Branch(MaterialSlots.Length == 0 AND MaterialOverrides cũ có dữ liệu)   ← đường LEGACY
    True  ▶→ BuildRecordsFromLegacy(Mesh=FurnitureMesh, OldOverridesByIndex=MaterialOverrides,
                                     MaterialDT=DT_MaterialInstancesCatalog) ●→ SET MaterialSlots
    False ▶→ [FIX 07/09/2026 — trước đây dead-end] nối thẳng xuống dòng dưới
  (merge, CẢ 2 nhánh)
  ▶→ ResetAllSlotsToAssetDefault(FurnitureMesh)
  ▶→ SET Rst_SlotIdx = 0
  ▶→ Rst_LoadNextSlot
```

### Rst_LoadNextSlot — Custom Event — MỚI merge vào canonical 07/09/2026

> KHÔNG đổi trong phiên 07/09 (delta xác nhận "giữ nguyên đúng như plan gốc"). Nội dung lấy từ
> ground truth `S7G2_Reroute_ExecutionPlan_27aug2026.md` mục 2B.1, đã PASS 6 bước undo/redo từ
> 04/09/2026 — verify lại bằng log `RowFound`/`AssetValid`/`ApplyResult` chạy đúng 100% sau khi
> fix dead-end ở `RestoreMyMaterialSlots` (07/09).

```
Rst_LoadNextSlot (Custom Event) ▶→
  Branch(Rst_SlotIdx >= MaterialSlots.Length)
    True  → [xong]
    False ▶→ MaterialSlots.Get(Rst_SlotIdx) ●→ SET Rst_CurRecord      ← temp var, không đọc pure 2 lần
      ▶→ Branch(Rst_CurRecord.MaterialRowName != "")
           True  → GetDataTableRow(DT_MaterialInstancesCatalog, Rst_CurRecord.MaterialRowName) → path
           False → Rst_CurRecord.MaterialPathFallback → path
      ▶→ MakeSoftObjectPath(path) → Async Load Asset → Completed
        ▶→ Branch(IsValid loaded asset)                 ← load fail KHÔNG được kẹt chain
             True → Cast MaterialInterface →
                    ApplyLoadedMaterialToSlot(FurnitureMesh, MaterialSlots,
                       Rst_CurRecord.SlotName, Rst_CurRecord.SlotIndex,
                       MI, Rst_CurRecord.MaterialRowName, Rst_CurRecord.MaterialPathFallback)
                    ▶→ ApplyParamsJsonToSlot(FurnitureMesh, Rst_CurRecord.ParamsJson,
                       Rst_CurRecord.SlotName, Rst_CurRecord.SlotIndex)
        (merge cả 2 nhánh IsValid) ▶→ SET Rst_SlotIdx = Rst_SlotIdx + 1 ▶→ Rst_LoadNextSlot
```

**Test PASS cuối cùng (07/09):** Combo "Bàn ghế nhựa uống nước" (4 ghế `Chair_VietNhat_1925`,
2 material khác nhau) → spawn → cả 4 ghế đúng material. EMS Save/Load actor thường (không qua
Combo) → regression PASS, không hồi quy.

### ApplyMaterialByRowName(SlotName : String, SlotIndex : Integer, RowName : Name) — Custom Event MỚI (S7.G5.2, 11/09/2026)

> Engine của kiến trúc 3 lớp kéo-thả material (Opus, `DELTA_Opus_S7_G5-G6_ExecutionPlan_08sep2026.md`
> mục 1): `WBP_MaterialCard.OnDragDetected` = nguồn, `WBP_DragOverlay.On Drop` = router, hàm này =
> engine — nơi DUY NHẤT biết chính xác thời điểm async load xong. L11: đặt on-actor để mỗi instance
> có graph riêng, không aliasing khi nhiều actor được kéo-thả liên tiếp.

**Biến mới trên actor** (giữ qua khe async — Custom Event không có Local Variable, L9):
```
Apply_PendingSlotName  : String
Apply_PendingSlotIndex : Integer
Apply_PendingRowName   : Name
```

```
Event ApplyMaterialByRowName (SlotName : String, SlotIndex : Integer, RowName : Name)
▶→ SET Apply_PendingSlotName  = SlotName
▶→ SET Apply_PendingSlotIndex = SlotIndex
▶→ SET Apply_PendingRowName   = RowName
▶→ Get Data Table Row
     Data Table = DT_MaterialInstancesCatalog
     Row Name   = RowName
   [2 pin thật của node — KHÔNG qua Branch thừa, xem bug #2 DEVIATIONS.md mục SPRINT 7 11/09/2026]
     Row Found     ▶→ Break S_MaterialInstancesData ●→ MaterialPath (String)
                     ▶→ Make Soft Object Path(PathString=MaterialPath)
                       ●→ [Conv_SoftObjPathToSoftObjRef tự chèn trên dây]
                     ▶→ Async Load Asset (Asset = ...)
                          Completed ▶→ Cast To MaterialInterface (Object = Loaded Asset)
                               CastSuccess (AsMI) ▶→ ApplyLoadedMaterialToSlot(
                                   Mesh=FurnitureMesh, Records=MaterialSlots [ref],
                                   SlotName=Apply_PendingSlotName,
                                   HintIndex=Apply_PendingSlotIndex, LoadedMI=AsMI,
                                   RowName=Conv_NameToString(Apply_PendingRowName),
                                   PathFallback="" ) ●→ bOK
                                 ▶→ Branch(bOK)
                                      True  ▶→ Get All Actors Of Class(BP_UndoManager) → Get(0)
                                              ▶→ CaptureSnapshot("ApplyMaterial")
                                              ▶→ Get All Actors Of Class(BP_FurnitureUserPrefsManager) → Get(0)
                                                 ▶→ AddRecentMaterial(RowName = Apply_PendingRowName)   ← [MỚI, G5.4, 11/09/2026 — fix bug #5]
                                              ▶→ [X3 — xem dưới]
                                      False ▶→ Print (Dev) "service trả false — slot không khớp"
                               CastFailed ▶→ Print (Dev) "MI cast fail RowName=" + RowName
     Row Not Found ▶→ Print (Dev) "RowName not found: " + RowName
```

**X3 (refresh swatch panel) — nối tiếp sau `CaptureSnapshot("ApplyMaterial")`:**
```
▶→ Get All Actors Of Class(BP_FurnitureSceneManager) → Get(0)
   → IsValid(FurnitureInventoryRef)
        True  ▶→ GET TargetFurnitureActor
                → Branch(Self == TargetFurnitureActor)     [Self = chính actor đang chạy event này]
                     True  ▶→ FurnitureInventoryRef.RefreshSlotSwatches()
                     False ▶→ (dead-end — actor này không hiện panel)
        False ▶→ (dead-end)
```
> `ToastRef` VÀ `FurnitureInventoryRef` đều nằm trên `BP_FurnitureSceneManager` (xác nhận
> 11/09/2026 qua K2Node export thật — KHÔNG phải `Foff_GameInstance` như `Planning/Architecture_Overview.md`
> v1.2 ghi trước đây. Xem doc debt trong `Planning/Architecture_Overview.md`).

**Điểm chốt lỗi (xử lý lỗi nhất quán):**
- `bFound=False` / Cast MI fail → log + dead-end (cuối chain, KHÔNG có node critical sau — L2 OK). Không crash.
- Không IsValid `FurnitureMesh` riêng vì actor sống mới gọi được event của nó; nhưng THÊM `IsValid(self)` ở
  callback nếu lo actor bị destroy giữa khe async (drop rồi undo ngay) — guard nhẹ trước `ApplyLoadedMaterialToSlot`.
- `CaptureSnapshot` sau apply (capture SAU action). Không debounce (1 drop = 1 snapshot, không spam).

✅ **G5.4 (11/09/2026):** Custom Event `Debug_TestApplyMaterial` (Call In Editor, dùng test
isolated) đã XÓA thật khỏi Blueprint — không còn tồn tại trong code.

**Bug phát sinh + fix trong phiên (S7.G5.1-G5.4, 11/09/2026, xem `DEVIATIONS.md` mục SPRINT 7
11/09/2026 để biết đầy đủ 5 bug):**
- **Bug #2** — Branch thừa (condition hard-code `true`) chèn ngay sau pin `Row Found` của
  `Get Data Table Row` khiến nhánh `Row Not Found` không bao giờ chạy dù RowName sai thật. Node
  này đã tự có 2 pin exec thật, không cần Branch thêm. Đã xóa Branch thừa.
- **Bug #4** — khối X3 (refresh swatch) ban đầu đặt sai lớp (ở Router `On Drop`, refresh trước khi
  async load xong) + so sánh sai kiểu (`FurnitureMesh` Component `==` `TargetFurnitureActor` Actor
  — luôn false). Đã dời X3 sang Engine (vị trí hiện tại ở trên) + đổi vế so sánh sang node `Self`.
- **Bug #5** (G5.4, phát hiện lúc test tay ngoài ma trận 8 case) — kéo-thả material áp thành công
  nhưng không xuất hiện trong tab "Recent" của material grid. Đường apply drag-drop xây riêng,
  không đi qua `LoadAndApplyMaterial` (đường click swatch) nên không thừa hưởng `AddRecentMaterial`.
  Đã thêm khối `AddRecentMaterial(Apply_PendingRowName)` ngay sau `CaptureSnapshot` (xem node flow
  ở trên) — cùng bài học sai-lớp với bug #4: side-effect phụ thuộc thời điểm apply thật phải đặt ở
  Engine, không đặt ở Router.

**Test PASS 4/4 (G5.2, 11/09/2026):** bấm nút debug (Call In Editor) → material slot đổi đúng trên mesh ·
Undo/Redo đúng · RowName bịa → log fail sạch, không crash, material không đổi · Save→Load →
material bám đúng.

---

### LoadMaterialsAsync(Overrides : Array of String, Index : Integer) — Custom Event (đệ quy)
```
Branch: Index >= Overrides.Length → [dead-end, xong đệ quy]

False → Branch: Overrides[Index] != ""
  True  → Make Soft Object Path(Overrides[Index]) → Async Load Asset
            Completed:
              Cast → As Material Interface
              Branch IsValid(As Material Interface):
                True  → GET FurnitureMesh(Self) → Create Dynamic Material Instance(Element Index, Source=MI)
                        → Call LoadMaterialsAsync(Overrides, Index+1)
                False → Call LoadMaterialsAsync(Overrides, Index+1)
  False → Call LoadMaterialsAsync(Overrides, Index+1)
```
⚠️ Cả 2 nhánh True/False của IsValid đều phải gọi đệ quy Index+1 — không thì slot fail làm đứng đệ quy.

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 22/04/2026 | Logic gốc — BeginPlay SET FurnitureSpawned tag, ActorLoaded restore mesh |
| 1.1 | 22/05/2026 | Thêm MaterialOverrides + MaterialParams (SaveGame v1.1) |
| 1.2 | 17/06/2026 — Sprint D.T6 | Thêm RowName : Name (SaveGame) — key DT_FurnitureCatalog. DAPath giữ fallback save cũ. GroupID [?] giải quyết: String SaveGame (Sprint 3 T2). |
| 2.0 | 19/06/2026 — 19h ICT | Thêm LoadMeshAsync + LoadMaterialsAsync (async load tự quản lý trong actor, không gọi hộ từ InputManager) |
| 2.1 | 05/09/2026 | Thêm `MaterialSlots : Array<FMaterialSlotRecord>` (SaveGame) — S7.G2 Bước 0, kho ghi material mới (name-based) qua `MaterialSlotService` |
| 2.2 | 07/09/2026 | S7.G3 Item 1+2: `ActorLoaded` reroute sang `Call RestoreMyMaterialSlots` (xóa ForEachLoop MaterialOverrides cũ; sửa luôn lỗi doc "có ADD Tags" — thực tế không có). `LoadMeshAsync` +Branch gọi restore khi mesh sẵn sàng (fix race async). Merge lần đầu `RestoreMyMaterialSlots`/`Rst_LoadNextSlot` (đã PASS từ G2/2B) + fix dead-end nhánh `False` Branch legacy (bug phát sinh 07/09, đã fix) + 2 biến `Rst_SlotIdx`/`Rst_CurRecord` |
| 2.3 | 11/09/2026 | S7.G5.2 (kéo-thả material, engine on-actor): thêm Custom Event `ApplyMaterialByRowName(SlotName, SlotIndex, RowName)` + 3 biến `Apply_Pending*`. 2 bug fix trong phiên: Branch thừa chặn nhánh "Row Not Found" của `Get Data Table Row`; khối X3 (refresh swatch) sai lớp (Router thay vì Engine) + so sánh sai kiểu (`FurnitureMesh` Component thay vì `Self`). Test PASS 4/4. ⚠️ Còn 1 chỗ debug scaffolding thật trong code (`Debug_TestApplyMaterial`, Call In Editor) CHƯA xóa — chờ G5.4. Nguồn: `11-09-2026_S7G5_G5.1-G5.3_AsBuilt_Delta.md` |
| 2.4 | 11/09/2026 (G5.4) | Fix bug #5: `ApplyMaterialByRowName` +khối `AddRecentMaterial(Apply_PendingRowName)` sau `CaptureSnapshot` (kéo-thả material trước đó không ghi Recent). Xóa thật `Debug_TestApplyMaterial` (scaffolding, dọn xong theo G5.4). Regression 8/8 PASS. GATE G5 ĐÓNG HẲN. Nguồn: `11-09-2026_S7G5_G5.4_AsBuilt_Addendum.md` |
