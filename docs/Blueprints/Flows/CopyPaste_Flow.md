# B2 — Copy/Paste/Duplicate Flow
**Phiên bản:** 2.2 | **Cập nhật:** 15/09/2026 | Fix `Bug-MaterialSlots-MissingInClipboard`: `S_ClipboardEntry` +field `MaterialSlots`, `CopyMesh` +GET, `SpawnFurnitureCopy` +input `MaterialSlots` +SET bên trong thân hàm, `PasteMesh`/`DuplicateMesh` nối `entry.MaterialSlots` vào lời gọi (KHÔNG SET-sau-spawn như RowName)

**Phiên bản:** 2.1 | **Cập nhật:** 07/09/2026 | S7.G3 — fix `Bug-RowName-MissingInClipboard`: `S_ClipboardEntry` +field `RowName`, `CopyMesh` +GET, `PasteMesh`/`DuplicateMesh` +SET NewActor.RowName sau spawn

**Phiên bản:** 2.0 | **Cập nhật:** 04/06/2026 — 15:30 ICT | Multi-Select (Sprint 1 T11)

> **v2.0:** chuyển từ single sang **multi**. Clipboard dùng `ClipboardActors` (Array S_ClipboardEntry) thay 5 var cũ. Giữ formation khi paste/duplicate (RelativeLocation so với center nhóm). SpawnFurnitureCopy thêm `bAutoSelect` + return `NewActor`.

---

## ⚠️ 2 BÀI HỌC TRẢ GIÁ (đọc trước)

1. **NESTING — bug lớn nhất:** trong DuplicateMesh, phần spawn (`CLEAR LocalSpawned → ForEach ClipboardActors`) phải nối vào **Completed** của ForEach MaxRightEdge, KHÔNG nối **Loop Body**. Nối Loop Body → spawn chạy N lần → spawn N×N đồ + có thể infinite loop. **Khi gặp infinite loop / số lượng nhân lên: kiểm tra nesting (Loop Body vs Completed) TRƯỚC khi nghi aliasing array.**

2. **SpawnFurnitureCopy Return Node:** cả 2 nhánh True/False của `Branch bAutoSelect` phải nối tới Return Node. Nhánh False để trống (dead-end) → trả về None → LocalSpawned rỗng → không spawn được gì.

---

## Input Actions

| Action | Path | Value Type |
|---|---|---|
| IA_FurnitureCopy | `/Game/cuong/UI/Input/IA_FurnitureCopy` | Boolean |
| IA_FurniturePaste | `/Game/cuong/UI/Input/IA_FurniturePaste` | Boolean |
| IA_FurnitureDuplicate | `/Game/cuong/UI/Input/IA_FurnitureDuplicate` | Boolean |

**LM_FurnitureInput — 6 mappings (mỗi action: Chorded Ctrl + Pressed, + 1 dòng consume block):**

| Action | Key | Triggers |
|---|---|---|
| IA_FurnitureCopy | C | Chorded(IA_Ctrl) + Pressed (Ctrl+C) |
| IA_FurniturePaste | V | Chorded(IA_Ctrl) + Pressed (Ctrl+V) |
| IA_FurnitureDuplicate | D | Chorded(IA_Ctrl) + Pressed (Ctrl+D) |

⚠️ Ctrl+Shift+C/V (material) phân biệt bằng `Branch Is Input Key Down(Shift) → True return` trong binding copy/paste.

---

## BP_FoffPlayerController — Routing
> ⚠ **LỖI THỜI (ghi nhận 25/09/2026):** từ Gate 1.5 B2 (18/08) event Input Action nằm trong `BP_FurnitureInputManager` (gọi thẳng hàm, không qua PlayerController). Khối dưới là bản cũ — xem `BP_FurnitureInputManager.md` mục "Enhanced Input Actions".
```
IA_FurnitureCopy (Started)      → Cast InputManager → Call CopyMesh
IA_FurniturePaste (Started)     → Cast InputManager → Call PasteMesh
IA_FurnitureDuplicate (Started) → Cast InputManager → Call DuplicateMesh
```

---

## Clipboard — `ClipboardActors : Array of S_ClipboardEntry` (v2.0)

S_ClipboardEntry: `MeshPath, DAPath, RelativeLocation(Vector), Rotation, Scale, MaterialOverrides(Array String), SurfaceType(Name), GroupID(String), RowName(Name), MaterialSlots(Array of FMaterialSlotRecord)` ← `RowName` MỚI 07/09/2026 (S7.G3, fix `Bug-RowName-MissingInClipboard`); `MaterialSlots` MỚI 15/09/2026 (fix `Bug-MaterialSlots-MissingInClipboard`)

### Bug xác nhận CÓ THẬT — 15/09/2026 (đóng `Bug-MaterialSlots-MissingInClipboard`, phát hiện+fix cùng phiên)
`S_ClipboardEntry` không có field `MaterialSlots`. Material sau S7.G2 (05/09) ghi vào
`MaterialSlots` (`FMaterialSlotRecord`), KHÔNG còn ghi `MaterialOverrides` (đã legacy) — nhưng
`CopyMesh`/`SpawnFurnitureCopy` chỉ mang theo `MaterialOverrides` → Copy/Paste/Duplicate mesh làm
mất material đã đổi, actor mới quay về material gốc. Cùng pattern "struct migrate name-based
thiếu field khi thêm call site mới" — lần thứ 3, sau `Bug-RowNameLostOnUndo` (03/08,
`S_FurniturePlacement`) và `Bug-RowName-MissingInClipboard` (07/09, field khác — `RowName`, định
danh món đồ, không liên quan material). Test 6/6 PASS — xem `Bugs/Open_Bugs.md`.

(5 var cũ ClipboardMeshPath/DAPath/Rotation/Scale/MaterialOverrides giữ tạm, bỏ ở S7.T9)

### Bug xác nhận CÓ THẬT — 07/09/2026 (đóng `Bug-RowName-MissingInClipboard`, treo từ 04/08/2026)
`S_ClipboardEntry` không có field `RowName`; `CopyMesh` không GET field này; `PasteMesh`/
`DuplicateMesh` không SET `NewActor.RowName` sau spawn (khác `RestoreSnapshot` đã tự vá đúng lỗ
hổng tương tự từ 03/08 — `Bug-RowNameLostOnUndo`, đã fix).

**Triệu chứng thật đã verify:** Copy 1 actor → Paste/Duplicate ra bản sao → multi-select cả cụm →
đổi material cùng lúc → CHỈ actor Primary đổi màu. Nguyên nhân: thiết kế "Multi-apply Hướng B"
(`Features/ChangeMaterial.md`, đã chốt Sprint 7) so sánh `RowName` giữa các actor trong
`SelectedActors` — actor nào `RowName=None` (do bug clipboard) sẽ làm gate "tất cả hoặc không"
loại cả cụm, chỉ Primary còn `RowName` đúng được áp. **Đây là bug ở tầng dữ liệu (clipboard),
KHÔNG phải bug ở logic multi-apply — không sửa lại multi-apply.**

**Quyết định kỹ thuật:** KHÔNG đổi chữ ký `SpawnFurnitureCopy` (không thêm param `RowName` dùng
chung) — vá surgical tại 2 caller còn thiếu (`PasteMesh`/`DuplicateMesh`), vì
`RestoreSnapshot`/`SpawnComboByID` đã tự SET đúng từ trước, đổi chữ ký chung sẽ phải sửa lại cả
những chỗ đang chạy đúng, rủi ro cao hơn lợi ích. Đánh đổi đã ghi nhận: nếu tương lai có call site
MỚI quên SET RowName, bug tái diễn — chấp nhận, không phải rủi ro cấp thiết với quy mô project
hiện tại.

**Test PASS:** Copy → Paste/Duplicate → multi-select → đổi material → cả cụm đổi màu đúng, không
chỉ Primary.

---

## Custom Event `CopyMesh` — MULTI (v2.0) — SỬA 15/09/2026 (fix `Bug-MaterialSlots-MissingInClipboard`, +MaterialSlots)
```
Branch SelectedActors.LENGTH == 0: True → Return
CLEAR ClipboardActors
CalculateCenter(SelectedActors) → Center
ForEach SelectedActors (Actor):
  Cast → BP_FurnitureActor:
    GET MeshPath, DAPath, MaterialOverrides, PlacementSurfaceType
    GET RowName                                        ← THÊM 07/09/2026 (Bug-RowName-MissingInClipboard)
    [THÊM 15/09/2026] GET MaterialSlots
    GetActorRotation(Actor), GetActorScale3D(Actor)
    GetActorLocation(Actor) - Center → RelativeLocation
    Make S_ClipboardEntry(... RelativeLocation ..., GroupID="", RowName = <giá trị vừa GET>,
                           [THÊM 15/09/2026] MaterialSlots = <giá trị vừa GET>) → ADD to ClipboardActors
```
**RelativeLocation** = vị trí so với tâm nhóm → giữ formation khi paste/duplicate.

---

## Function `PasteMesh` — MULTI (v2.0) — SỬA 15/09/2026 (fix `Bug-MaterialSlots-MissingInClipboard`, +nối MaterialSlots vào lời gọi)

**Local:** `LocalSpawned : Array BP_FurnitureActor`, `PasteSurfaceType : Name`

```
Branch ClipboardActors.LENGTH == 0: True → Return    ← (đã bỏ guard cũ "Is Empty ClipboardMeshPath")

← Trace cursor → bề mặt:
Convert Mouse Location To World Space → WorldOrigin, WorldDirection
Line Trace By Channel(Camera, Start=WorldOrigin, End=+Direction×10000) → Out Hit, ReturnValue
Branch ReturnValue: T → Break Hit Result → Location → PasteCenter | F → fallback (camera forward × 300)

← Surface type từ HitNormal:
Break Hit Result → Normal.Z: >0.5 → "Floor" | <-0.5 → "Ceiling" | else → "Wall" → SET PasteSurfaceType

← Spawn từng entry, giữ formation:
Call DeselectAll
CLEAR LocalSpawned
ForEach ClipboardActors (entry):
  Break S_ClipboardEntry
  actualLocation = PasteCenter + RelativeLocation
  Call SpawnFurnitureCopy(MeshPath, DAPath, SpawnLocation=actualLocation, SpawnRotation=Rotation,
                          SpawnScale=Scale, MaterialOverrides, SurfaceType=PasteSurfaceType, bAutoSelect=False,
                          [THÊM 15/09/2026] MaterialSlots=entry.MaterialSlots) → NewActor
  [THÊM 07/09/2026] SET NewActor.RowName = entry.RowName
  Branch IsValid(NewActor): True → ADD NewActor to LocalSpawned
ForEach Completed →
  Call SelectActors(LocalSpawned)
  Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("PasteMulti")
```
**bAutoSelect=False** trong loop → select thủ công bằng SelectActors ở cuối (tránh select state bị lặp).

---

## Function `DuplicateMesh` — MULTI (v2.0) — SỬA 15/09/2026 (fix `Bug-MaterialSlots-MissingInClipboard`, +nối MaterialSlots vào lời gọi)

**Local:** `LocalSpawned : Array`, `GroupCenter : Vector`, `DuplicateOffset : Vector`, `MaxRightEdge : Float`

```
Branch SelectedActors.LENGTH == 0: True → Return
Call CopyMesh   ← fill ClipboardActors
CalculateCenter(SelectedActors) → SET GroupCenter

← Tính offset = cạnh phải xa nhất của nhóm (tránh chồng lên gốc):
SET MaxRightEdge = GroupCenter.X
ForEach SelectedActors (Actor):                       ← ⚠️ FOR-EACH NÀY
  Get Actor Bounds(Actor, OnlyColliding=False) → Origin, BoxExtent
  RightEdge = Origin.X + BoxExtent.X
  SET MaxRightEdge = Max(MaxRightEdge, RightEdge)
[Loop Body] → CHỈ tính MaxRightEdge, KHÔNG nối spawn vào đây ❌
[Completed] → ↓ ✅ phần spawn nối vào ĐÂY

  HalfWidth = MaxRightEdge - GroupCenter.X
  Make Vector(HalfWidth + 20, 0, 0) → SET DuplicateOffset

  Call DeselectAll
  CLEAR LocalSpawned
  ForEach ClipboardActors (entry):
    Break S_ClipboardEntry
    actualLocation = (GroupCenter + DuplicateOffset) + RelativeLocation
    Call SpawnFurnitureCopy(MeshPath, DAPath, SpawnLocation=actualLocation, SpawnRotation=Rotation,
                            SpawnScale=Scale, MaterialOverrides, SurfaceType, bAutoSelect=False,
                            [THÊM 15/09/2026] MaterialSlots=entry.MaterialSlots) → NewActor
    [THÊM 07/09/2026] SET NewActor.RowName = entry.RowName
    Branch IsValid(NewActor): True → ADD to LocalSpawned
  ForEach Completed →
    Call SelectActors(LocalSpawned)        ← chỉ select đồ MỚI (standard behavior)
    Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("DuplicateMulti")
```

**⚠️ Điểm chí mạng:** phần `CLEAR LocalSpawned → ForEach ClipboardActors` nối vào **Completed** của ForEach MaxRightEdge. Nếu nối Loop Body → spawn N×N đồ.

---

## Function `SpawnFurnitureCopy` — v2.2 (K2Node export thật, 15/09/2026 — thay pseudo-code Step 1-6 cũ)

> ✅ **[ĐÃ K2Node VERIFY]** — bản dưới dịch trực tiếp từ K2Node export thật (cuhoang, 15/09/2026),
> KHÔNG suy diễn thêm. Thay hoàn toàn bản "Step 1-6" pseudo-code trước đó (từ v2.0, 04/06/2026) —
> bản cũ SAI ở 2 chỗ (xem "Drift đã sửa" cuối mục). Notation: `▶→` = execution wire, `●→` = data
> wire (theo quy ước `L-DOC` trong `Rules/AI_Implementation_Rules.md`).

**Inputs:** `MeshPath, DAPath, SpawnLocation, SpawnScale, SpawnRotation, MaterialOverrides, SurfaceType, bAutoSelect(Bool=True), bAddToRecent(Bool=True), MaterialSlots(Array<FMaterialSlotRecord>)` ← `MaterialSlots` MỚI 15/09/2026 (fix `Bug-MaterialSlots-MissingInClipboard`), **KHÔNG có default value** (khác `bAutoSelect`/`bAddToRecent` có default `True`). ⚠️ `bAddToRecent` là input CÓ SẴN từ trước (liên quan `K3`, `Bugs/Open_Bugs.md`) nhưng doc bản cũ chưa từng liệt kê — bổ sung ở đây, không phải thay đổi mới.
**Locals:** `index, path` (không dùng trong nhánh này), `NewActorCopy : BP_FurnitureActor`
**Output:** `NewActor : BP_FurnitureActor`

```
Entry → Execution Sequence (4 nhánh, chạy TUẦN TỰ — Sequence tự kích lần lượt, không phải song song thật)

── Sequence.then_0 — Spawn chính (nhánh dài nhất) ──
SpawnActorFromClass(BP_FurnitureActor, SpawnLocation, SpawnRotation)
  ●→ ReturnValue → SET NewActorCopy
▶→ Call NewActorCopy.LoadMeshAsync(MeshPath)        ← kick off async, KHÔNG chờ ở đây
▶→ SET NewActorCopy.MeshPath = MeshPath
▶→ SET NewActorCopy.DAPath = DAPath
▶→ SetActorScale3D(NewActorCopy, SpawnScale)
▶→ [MỚI 15/09] SET NewActorCopy.MaterialSlots = MaterialSlots (param)
▶→ GET NewActorCopy.Tags → Array_Add("FurnitureSpawned") ●→ SET NewActorCopy.Tags
▶→ Branch( GetCurrentEditScope() != "" )
     True  ▶→ SET NewActorCopy.GroupID = GetCurrentEditScope()   ← dead-end (hết nhánh, hợp lệ)
     False → dead-end (hợp lệ — không có gì làm thêm nếu không trong edit scope)

── Sequence.then_1 — Material legacy (KHÔNG đụng bởi fix 15/09) ──
SET NewActorCopy.MaterialOverrides = MaterialOverrides
▶→ Call NewActorCopy.LoadMaterialsAsync(Overrides=MaterialOverrides, Index=0)   ← dead-end
  (đường legacy cho save cũ, không tham gia đường MaterialSlots mới)

── Sequence.then_2 — Surface Type + Add Recent Mesh ──
SET NewActorCopy.PlacementSurfaceType = SurfaceType
▶→ GetAllActorsOfClass(BP_FurnitureUserPrefsManager)
▶→ Branch(bAddToRecent)
     True  ▶→ Get(0) → AddRecentMesh(RowName = Conv_StringToName(
                 ParseIntoArray(MeshPath, ".") → Get(LastIndex) ))   ← dead-end
     False → dead-end

── Sequence.then_3 — Auto-select actor mới ──
Branch(bAutoSelect)
  True  ▶→ Call DeselectMesh()
       ▶→ Call SelectActors( MakeArray(NewActorCopy) )
       ▶→ (merge) ─┐
  False ─────────────┘
                     ▶→ FunctionResult(NewActor = NewActorCopy)
```

Return Node nối CẢ 2 nhánh True/False của Branch cuối (đúng bài học trả giá đã ghi — nhánh False
để trống mà không nối Return sẽ trả None).

**Verify Step MaterialSlots (đã build+test 15/09/2026):** SET `MaterialSlots` nằm trong `then_0`,
chạy đồng bộ, TRƯỚC khi function return — `Completed` thật của `LoadMeshAsync` là callback NỘI BỘ
bên trong `BP_FurnitureActor`, không lộ ra graph này → không chặn exec chain ở đây. An toàn, không
tái phát `Bug-LoadMeshAsync-RestoreRace`.

**Call site KHÔNG sửa (verify bằng compile + test, 15/09/2026):** `SpawnComboByID`/`RestoreSnapshot`
để pin `MaterialSlots` **không nối** — Call Function node cho Array input trống tự nhận mảng rỗng
làm default (compile xanh + test xác nhận). 2 hàm này tự `SET NewActor.MaterialSlots` bằng giá trị
riêng NGAY SAU khi `SpawnFurnitureCopy` return — ghi đè lên mảng rỗng đó, đúng thứ tự thời gian,
hành vi không đổi.

**Lưu ý kỹ thuật (khác `MaterialOverrides` cũ) — 2 quy tắc khác nhau của Array input trống:**
Array input để trống tại **điểm GỌI hàm** (call-site) thì compile được (rỗng ngầm định); nhưng
Array input để trống tại 1 node **SET biến bên trong thân hàm** (như bước `then_0` trên) thì KHÔNG
compile được — bắt buộc phải nối, kể cả `Make Array` rỗng. 2 quy tắc khác nhau, verify thật qua
lỗi compile gặp giữa phiên 15/09/2026.

### Drift đã sửa so với bản pseudo-code cũ (v2.0, 04/06/2026) — 2 chỗ
1. **Load mesh:** bản cũ ghi `Load Asset Blocking(MeshPath) → Cast Static Mesh → Set Static Mesh`
   (đồng bộ). K2Node export thật: `Call NewActorCopy.LoadMeshAsync(MeshPath)` (async, hàm riêng
   trên `BP_FurnitureActor`, không phải node engine `Load Asset Blocking`). Bản cũ SAI/lỗi thời —
   thay bằng bản K2Node ở trên.
2. **Apply MaterialOverrides:** bản cũ ghi `ForEach MaterialOverrides (Index, Path) → Branch Path
   != "" → Load Asset Blocking → Create DMI → Set Material` (viết tay từng bước). K2Node export
   thật: gọi thẳng 1 hàm có sẵn `Call NewActorCopy.LoadMaterialsAsync(Overrides=MaterialOverrides,
   Index=0)` — logic ForEach/DMI/Set Material (nếu có) nằm BÊN TRONG hàm đó, không lộ ra graph này.
   Bản cũ SAI/lỗi thời — thay bằng bản K2Node ở trên.
3. **Auto-select (then_3):** bản cũ mô tả chi tiết `SET SelectedFurnitureActor` + `Set Render
   Custom Depth` + `Set Custom Depth Stencil 255` + `ActivateGizmo` + `Call OnMeshSelected` viết
   tay từng bước. K2Node export thật chỉ có `Call DeselectMesh()` → `Call SelectActors(MakeArray
   (NewActorCopy))` — 2 lời gọi hàm có sẵn, không phải 5 bước tay. **Chưa xác nhận chắc chắn**
   liệu `SelectActors()` có tự làm các việc custom-depth/gizmo/OnMeshSelected bên trong nó hay
   không (hợp lý vì `SelectActors` dùng chung cho multi-select ở nơi khác) — ghi nhận theo đúng
   K2Node export, KHÔNG tự suy diễn thêm, báo cuhoang xác nhận nếu cần đào sâu `SelectActors()`.

---

## Key Notes

- **MULTI clipboard:** ClipboardActors (Array S_ClipboardEntry), RelativeLocation giữ formation.
- **bAutoSelect=False** khi gọi trong loop (Paste/Duplicate) → SelectActors thủ công ở cuối. bAutoSelect=True cho single spawn (drag-drop legacy).
- **NESTING:** spawn nối Completed của ForEach MaxRightEdge, KHÔNG Loop Body (bug N×N).
- **Return Node:** nối NewActorCopy ở cả 2 nhánh bAutoSelect (False để trống → trả None).
- **DuplicateMesh select đồ mới only** (không gốc) — standard. Gốc+mới: optional, build mảng độc lập.
- **CopyMesh không DeselectMesh** — SelectedActors vẫn valid sau Copy.
- **PasteMesh guard mới** = `ClipboardActors.LENGTH == 0` (bỏ guard cũ "Is Empty ClipboardMeshPath").
- **CaptureSnapshot SAU SelectActors** (cuối Completed), 1 lần/thao tác.
- **Collision sàn/tường** available nhờ fix ActivateGizmo (không disable collision floor/wall) → LineTrace PasteMesh hit được.

---

## Lịch sử
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 21/05/2026 | Single Copy/Paste/Duplicate + SpawnFurnitureCopy |
| 2.0 | 04/06/2026 | Multi: ClipboardActors + RelativeLocation formation; SpawnFurnitureCopy +bAutoSelect +NewActor; bài học nesting + Return Node |
| 2.1 | 07/09/2026 | Fix `Bug-RowName-MissingInClipboard`: `S_ClipboardEntry` +field `RowName`; `CopyMesh` +GET RowName; `PasteMesh`/`DuplicateMesh` +SET NewActor.RowName sau spawn. Bug ở tầng dữ liệu clipboard, không phải logic multi-apply. Test PASS. Nguồn: `07-09-2026_S7G3_Item1-4_Delta.md` mục B4. |
| 2.2 | 15/09/2026 | Fix `Bug-MaterialSlots-MissingInClipboard`: `S_ClipboardEntry` +field `MaterialSlots`; `CopyMesh` +GET MaterialSlots; `SpawnFurnitureCopy` +input `MaterialSlots` (không default) +SET bên trong thân hàm (`then_0`); `PasteMesh`/`DuplicateMesh` nối `entry.MaterialSlots` vào lời gọi (KHÁC RowName — không SET sau spawn). `SpawnComboByID`/`RestoreSnapshot` KHÔNG sửa (pin để trống, tự SET riêng sau). Lần thứ 3 của pattern "struct migrate name-based thiếu field". Test 6/6 PASS. **Cùng đợt:** viết lại toàn bộ `SpawnFurnitureCopy` theo K2Node export thật (cuhoang cung cấp) — sửa 3 chỗ drift so với pseudo-code v2.0 cũ (load mesh = `LoadMeshAsync` không phải `Load Asset Blocking`; apply material = gọi thẳng `LoadMaterialsAsync` không phải ForEach tay; auto-select = `DeselectMesh`+`SelectActors` không phải 5 bước custom-depth/gizmo tay). Nguồn: `DELTA — Fix Bug-MaterialSlots-MissingInClipboard` (Opus+cuhoang, 15/09/2026) + K2Node export xác nhận trực tiếp trong hội thoại (15/09/2026). |
