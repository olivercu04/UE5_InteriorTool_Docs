# BP_ComboManager — Blueprint Logic
**Version:** 1.15 | **Ngày:** 04/08/2026 15:20 | **Lô A verify (T0 của T4):** `SaveComboFromSelection` re-export K2Node — xác nhận Bước 1-8 khớp doc cũ, bổ sung Bước 0 (param→class var, chưa từng ghi) + xác nhận Bước 5a/Bước 7 as-built

## Vai trò
Xử lý toàn bộ combo logic (save, spawn, replace). Nhận data qua PARAM, KHÔNG hard ref BP_FurnitureInputManager (R2). Được spawn trong Level BP sau UserPrefsManager.

## Event Dispatchers
- `OnComboLibraryChanged` — broadcast sau khi lưu/xóa combo → WBP_FurnitureInventory lắng nghe → LoadComboLibrary

## Class Variables
| Tên | Kiểu | Vai trò |
|-----|------|---------|
| SaveCombo_GroupIDs | Array String | Leaf GroupIDs từ SelectedActors (Bước 3) |
| SaveCombo_ComboGroups | Array S_GroupData | Groups đầy đủ sau LCA (Bước 3 mới) |
| SaveCombo_TokenMap | Map String→String | GroupID → token (Bước 4) |
| SaveCombo_TempParentToken | String | Buffer parentToken cho từng group |
| SaveCombo_TempGroupToken | String | Buffer groupToken cho từng actor |
| SaveCombo_OutputGroups | Array FComboGroupData | Groups output cho JSON |
| SaveCombo_OutputItems | Array FComboItemData | Items output cho JSON |
| SaveCombo_ComboID | String | ComboID hiện tại đang save |
| LeafGroupIDs_SaveCombo | Array String | Input cho CalculateLCAList_Combo (C0) |
| LCARoots_SaveCombo | Array String | Output LCA roots (C0) |
| MaterialOverrides_SaveCombo | Array String | Buffer RowName per actor (C0) |
| ItemRowName_SaveCombo | String | Buffer RowName sau fallback parse MeshPath (Bước 5d, C0) |
| SaveCombo_BoundingExtent | Vector | Buffer tạm BoundingBoxExtent tính từ CalculateComboBoundingExtent (Bước 5e, C4) |
| Cmb_ThumbnailCache | Map<String,Texture2D> | Cache thumbnail, key=ComboID (G3) |
| Cmb_CaptureHandle | SceneCapture2D | Handle tạm giữa Begin/Delay/Finish (debug + Bước 7 thật) |
| Cmb_AccumFramesLeft | Integer | Default 0. Đếm ngược frame còn lại cần accumulate — dùng ở cả Custom Event lẫn Event Tick (P2 Noise Fix, 19/07/2026) |
| Cmb_AccumTargetFrames | Integer | Default 24. Số frame cộng dồn cho temporal accumulation — tunable ở Class Defaults, không cần build lại C++ (P2 Noise Fix, 19/07/2026) |
| Cmb_StudioCamYaw | Float | Default 55.0. Yaw cố định camera Studio (khớp FixedAngle.Yaw thật trong BeginComboCapture — TRƯỚC đây doc ghi nhầm 0). Nguồn sự thật DUY NHẤT cho FixedAngle lẫn công thức DeltaYaw Bước 7 (P2 Gate F, 21/07/2026) |
| Cmb_PendingUserCamYaw | Float | Default 0.0. Bearing camera→combo, chốt lúc BẤM nút Save (trước dialog mở) (P2 Gate F, 21/07/2026) |
| Cmb_PendingCaptureComboID | String | Default "". Mang ComboID từ lúc Begin (Bước 7) sang lúc Finish (Event Tick, cách nhau N frame) (P2 Gate F, 21/07/2026) |
| Cmb_DebugLastCaptureDistance | Float | Default 0.0. Debug-only: log khoảng cách camera→Anchor (proxy fit-radius) để verify framing. Giữ lại phục vụ Sprint 6 (P2 Gate F, 21/07/2026) |

## Functions (có local variable)
### GetPathToRoot_Combo(InGroupID → Path: Array String)
Leo từ InGroupID lên root qua ForLoop 0..9, gọi FindGroupData trên InputManager. Collect từng GroupID vào Path. Return khi ParentGroupID=="" hoặc bFound=False hoặc loop hết.

### FindLCA_TwoGroups_Combo(GroupID_A, GroupID_B → LCA: String)
PathA = GetPathToRoot(A). Walk up từ B: nếu Contains(PathA, CurrentB) → return CurrentB. Nếu không tìm được → return "".

### CalculateLCAList_Combo(LeafIDs → Result: Array String)
Guard Length==0 → return []. SET CurrentLCA = LeafIDs[0]. ForEach từ index 1: FindLCA_TwoGroups(CurrentLCA, leaf) → nếu "" (khác cây) ADD CurrentLCA + SET CurrentLCA=leaf; nếu != "" SET CurrentLCA=lca. Completed: ADD CurrentLCA cuối → return Result.

### CalculateComboBoundingExtent(InActors: Array\<BP_FurnitureActor\> → ReturnVec: Vector)

**[SỬA 22/07/2026 — Dimension Fix]** Đổi công thức bounds. **Vấn đề cũ:** dùng `Get Actor Bounds`
(World AABB) — hộp bao phồng to khi actor tự XOAY tại chỗ (hộp bao world-space nở ra theo góc
xoay của mesh, dù kích thước vật lý không đổi). **Sửa:** đổi sang `Get Local Bounds` (bounds
trong không gian local mesh, KHÔNG bị Actor Rotation ảnh hưởng) × Scale + Actor Location, thay
cho `Get Actor Bounds`.

Branch(InActors.Length == 0):
- True → Make Vector(0,0,0) → Return

- False →
  SET ActorsCopy = InActors
  SET MinX=999999, MinY=999999, MinZ=999999
  SET MaxX=-999999, MaxY=-999999, MaxZ=-999999

  ForEach ActorsCopy → Loop Body:
    Branch(IsValid(actor)):
      False → dead-end (skip actor này, ForEach tự sang phần tử tiếp — HỢP LỆ, đây là Loop Body
               của ForEachLoop macro, không phải Event chain nên KHÔNG phải fatal dead-end)
      True  →
        GET FurnitureMesh(actor) → StaticMeshComponent
        StaticMeshComponent.Get Local Bounds ●→ LocalMin, LocalMax
        GET actor.GetActorScale3D() ●→ Scale
        ScaledMin = LocalMin × Scale   (Multiply_VectorVector, element-wise)
        ScaledMax = LocalMax × Scale
        GET actor.GetActorLocation() ●→ Loc
        WorldMin = Loc + ScaledMin
        WorldMax = Loc + ScaledMax
        MinX = FMin(MinX, WorldMin.X)  |  MaxX = FMax(MaxX, WorldMax.X)
        MinY = FMin(MinY, WorldMin.Y)  |  MaxY = FMax(MaxY, WorldMax.Y)
        MinZ = FMin(MinZ, WorldMin.Z)  |  MaxZ = FMax(MaxZ, WorldMax.Z)

  Completed →
    Make Vector(X=(MaxX-MinX)/2, Y=(MaxY-MinY)/2, Z=(MaxZ-MinZ)/2) → Return

**Node mới cần confirm vào bảng chính (`AI_Implementation_Rules.md`):** `Get Local Bounds`
(StaticMeshComponent → Min, Max Vector) — bounds trong không gian LOCAL của mesh (chưa nhân
Scale/Rotation), dùng khi cần đo kích thước vật lý thật của mesh, không bị Actor Rotation làm
phồng to (khác `Get Actor Bounds`, vốn là World AABB nên actor xoay 45° sẽ tự nở hộp bao).

**Giới hạn đã biết (KHÔNG fix trong task này):** công thức trên fix đúng trường hợp 1 MÓN tự
xoay tại chỗ, nhưng KHÔNG fix trường hợp CẢ ĐỘI HÌNH combo xoay lệch so với trục thế giới — AABB
world-axis vẫn phồng ra theo hướng đặt combo trong phòng (bản chất toán học của AABB, không phải
bug). Đo thực tế 2 combo giống hệt nhau chỉ khác hướng đặt:
```
Combo gốc:  BoundingBoxExtent = (147.25, 101.43, 52.32) → Card: 2.9×2.0×1.0m — 6.0m²
Combo xoay: BoundingBoxExtent = (140.75, 145.81, 52.32) → Card: 2.8×2.9×1.0m — 8.2m²
```
Chấp nhận tạm — xem `Bugs/Open_Bugs.md` mục Feature-CanonicalStudioAngle để biết hướng fix triệt
để (Sprint 6, cần field `ReferenceYaw` chưa có trong schema).

**Ảnh hưởng phạm vi:** hàm này dùng ở CẢ 2 chỗ — field `BoundingBoxExtent` lưu vào combo JSON
lúc Save (Bước 5e, `SaveComboFromSelection`) VÀ gián tiếp Card đọc field đó (`WBP_ComboCard.md`
mục Field Kích thước). Combo lưu **từ giờ trở đi** dùng công thức mới; combo **đã lưu trước
22/07/2026** giữ nguyên số cũ (sai) cho tới khi user Save lại — KHÔNG có migrate hàng loạt tự
động (quyết định cuhoang, ghi backlog nếu cần sau).

**Test PASS (22/07/2026):**
1. Combo có đồ xoay lệch trục (ghế 45°, sofa 90°) → số Card khớp kích thước thật, không phồng.
2. Combo cũ Save trước khi sửa → vẫn hiện số cũ (đúng hành vi đã thống nhất, không phải bug).
3. Combo toàn đồ không xoay → số gần giống bản `Get Actor Bounds` cũ (không lệch bất thường).

## SpawnComboForThumbnail(ComboID : String, DeltaYaw : Float = 0) — MỚI P2 Gate A (17/07/2026)

Custom Event (Latent — BeginComboCapture/Delay ở Việc 4 gọi từ đây).

```
▶→ Branch(Cmb_bThumbBusy)
     True  ▶→ HẾT (guard đầu)
     False ▶→ SET Cmb_bThumbBusy = True
▶→ F_LoadComboData(ComboID) ●→ OutData, bSuccess
▶→ Branch(bSuccess)
     False ▶→ SET Cmb_bThumbBusy = False → HẾT
     True  ▶→ Break ComboData ●→ Items
▶→ ForEach(Items) LoopBody:
     Get Data Table Row(DT_FurnitureCatalog, RowName) — Row Found:
       T ▶→ MeshPath = MeshFolderPath + "/" + RowName + "." + RowName  (Concat, y hệt SpawnComboByID)
          ▶→ SpawnFurnitureCopy(
                self = InputManagerRef,
                MeshPath, DAPath="",
                SpawnLocation = Cmb_StudioAnchor + RelLocation,
                SpawnRotation = RelRotation, SpawnScale = Scale,
                MaterialOverrides, SurfaceType,
                bAutoSelect = False, bAddToRecent = False) ●→ NewActor
          ▶→ Branch(IsValid(NewActor))
               True  ▶→ GET Tags → Array Remove Item("FurnitureSpawned")
                       → SET GroupID = "" → Array Add(Cmb_StudioClones, NewActor)
               False ▶→ dead-end (hợp lệ, Loop Body)
       F (Row not found) ▶→ dead-end (item lỗi bỏ qua, không báo — ⚠️ chưa có log skip)
   Completed ▶→ [tiếp tục trong BeginThumbnailCapture — xem bên dưới, P2 Gate F 21/07/2026]
```

`DeltaYaw` khai param nhưng CHƯA dùng ở Gate A (default 0) — dành cho Gate C (xoay camera H-B).
`InputManagerRef` = class var đã cache sẵn từ BeginPlay, không Get All Actors lại.

## BeginThumbnailCapture(ComboID : String, DeltaYaw : Float) — MỚI P2 Gate F (21/07/2026)

**Chuỗi debug phím U (Việc 4) ĐÃ XÓA 21/07/2026** — Input Event "U" (Pressed) + Enable Input
phục vụ phím U ở BeginPlay bị xóa toàn bộ. Khối logic spawn→align→Begin→enable-tick tách ra
thành Custom Event `BeginThumbnailCapture` bên dưới, giờ dùng CHUNG cho Save flow thật
(`SaveComboFromSelection` Bước 7 — xem mục Custom Events). `bDebugTestThumb` xóa (chỉ phím U
dùng); `Cmb_DebugTestComboIDs`/`Cmb_DebugComboIndex` xóa (chỉ Tick tail debug dùng, xem mục
Event Tick). `bDebugMode` GIỮ NGUYÊN — còn gate nhiều Print khác.

Nguồn: export K2Node THẬT của Event U (cuhoang paste 21/07/2026) — đối chiếu trực tiếp trước
khi xóa, không suy đoán. Latent (2 Delay).

```
BeginThumbnailCapture(ComboID, DeltaYaw)
▶→ SET Cmb_PendingCaptureComboID = ComboID          ← BẮT BUỘC đầu event (Tick tail đọc lại)
▶→ SpawnComboForThumbnail(ComboID, DeltaYaw)
▶→ Delay(3.0)                                       ← Delay #1 (warm-up trước align)
▶→ ResolveThumbAlign(Clones=Cmb_StudioClones) ●→ DeltaZ, Category
▶→ Branch(bDebugMode): True→Print "ThumbAlign Category="+Category / False→(merge)
▶→ ForEach(Cmb_StudioClones):
     LoopBody ▶→ Branch(IsValid(Element)):
                  True  ▶→ Add Actor World Offset(Element, (0,0,DeltaZ), bSweep=False)
                  False ▶→ dead-end (hợp lệ, Loop Body)
     Completed ▶→
▶→ Switch on E_ThumbAlignCategory(Category) [4 pin Floor/Ceiling/Wall/Other — merge chung, STUB Nấc 1]
▶→ BeginComboCapture(ComboActors=Cmb_StudioClones, ExtraHiddenActors=[](rỗng),
     Resolution=1024, FitRatio=0.85, bIsolateCombo=false,
     bUseFixedAngle=true, FixedAngle=Split(Pitch=-15, Yaw=Get Cmb_StudioCamYaw, Roll=0))
     ●→ SET Cmb_CaptureHandle
▶→ Branch(IsValid(Cmb_CaptureHandle)):
     True  ▶→ SET ShowFlagSettings=[{"SkyLighting", Enabled=False}] (CaptureComponent2D)
          ▶→ SET Cmb_DebugLastCaptureDistance = Vector_Distance(
                 GetActorLocation(Cmb_CaptureHandle), Cmb_StudioAnchor)
          ▶→ Branch(bDebugMode): True→Print "Capture Distance="+Cmb_DebugLastCaptureDistance / False→(merge)
          ▶→ SetFieldsInStruct(PostProcessSettings):
               AutoExposureMethod=Manual, AutoExposureBias=6.0, DepthOfFieldFstop=1.0,
               DepthOfFieldFocalDistance = Get Cmb_DebugLastCaptureDistance   ← đọc lại từ biến (không tính Vector_Distance 2 lần)
          ▶→ SET PostProcessSettings (CaptureComponent2D)
          ▶→ Delay(3.0)                              ← Delay #2 (warm-up trước accumulate)
          ▶→ ResetComboAccumulation(Cmb_CaptureHandle)
          ▶→ SET Cmb_AccumFramesLeft = Cmb_AccumTargetFrames
          ▶→ SetActorTickEnabled(true)               [HẾT — Tick tail lo phần còn lại]
     False ▶→ SET Cmb_bThumbBusy = false
          ▶→ Print "ThumbCapture: Begin None" [bDebugMode]
          ▶→ Broadcast OnComboLibraryChanged         ← Begin fail vẫn broadcast, card fallback 🧩
```

⚠️ Ghi chú `FixedAngle.Yaw`: node `BeginComboCapture` phải **Split Struct Pin** trên FixedAngle →
pin Yaw con nối từ `Get Cmb_StudioCamYaw` (KHÔNG literal 55). Pitch=-15, Roll=0 giữ literal.

⚠️ `Cmb_DebugLastCaptureDistance` là giá trị XẤP XỈ (Vector Distance camera→Anchor), tái dùng
cho cả DOF FocalDistance (Gate E) lẫn debug framing — 1 nguồn, không tính 2 lần (pure
re-evaluate).

Q8: Custom Event (2 Delay latent OK, L8) | IsValid(Cmb_CaptureHandle) guard sau Begin | L2: cả 2
nhánh IsValid kết thúc hợp lệ (True→enable tick, False→cleanup+broadcast) | Latent trong Custom
Event | 6A: nhánh fail dọn busy+broadcast; clone destroy ở Tick tail

**Ghi chú Nấc 2 (chưa làm):** Switch stub hiện gộp cả 4 Category vào cùng
`BeginComboCapture`. Khi làm Nấc 2 (below-front key light + camera from-below cho pure
Ceiling/Wall), tách pin Ceiling/Wall ra set lại `Cmb_StudioKeyLight`/camera FixedAngle riêng
TRƯỚC khi merge vào BeginComboCapture — không đổi pin Floor/Other.

## SetPendingUserCamYaw(Yaw : Float) — MỚI P2 Gate F (21/07/2026)

1 dòng — để `WBP_FurnitureInventory` không ghi thẳng biến nội bộ ComboManager (encapsulation).

```
SetPendingUserCamYaw(Yaw)
▶→ SET Cmb_PendingUserCamYaw = Yaw
```

## Function `ResolveThumbAlign(Clones) → DeltaZ, Category` — MỚI Gate D Nấc 1 (20/07/2026)

**Container:** Function (không Custom Event — không latent, cần Local Variable + Return Node).

**Input:** `Clones : Array<BP_FurnitureActor Object Reference>`
**Output:** `DeltaZ : Float`, `Category : E_ThumbAlignCategory` (enum: Floor/Ceiling/Wall/Other)

**Local Variables:**
| Tên | Kiểu | Default |
|---|---|---|
| HasFloor | Boolean | false |
| AnyCeiling | Boolean | false |
| AnyWall | Boolean | false |
| FloorMinZ | Float | 1000000.0 |
| AllMinZ | Float | 1000000.0 |
| AllMaxZ | Float | -1000000.0 |
| WallMinZ | Float | 1000000.0 |
| stype | Name | None |
| AnchorZ | Float | 0.0 |

```
Q8: Function (no latent — Local var + Return OK, L8✓) | IsValid clone trước Get Actor
    Bounds (L1) | L2: 6 nhánh categorize đều hit Return Node — đếm đủ | No latent✓ |
    6A: pure-compute, không tạo state cần đảo✓

[Khởi tạo — SET 8 local var ngay đầu Function, trước guard]
▶→ SET HasFloor=false ▶→ SET AnyCeiling=false ▶→ SET AnyWall=false ▶→
   SET FloorMinZ=1000000.0 ▶→ SET AllMinZ=1000000.0 ▶→ SET AllMaxZ=-1000000.0 ▶→
   SET WallMinZ=1000000.0 ▶→
   SET AnchorZ = (GET Cmb_StudioAnchor → Break Vector → Z) ▶→ tiếp

[Guard rỗng]
▶→ Branch(Array Length(Clones) == 0)
     True  → SET DeltaZ(Return)=0.0 · SET Category(Return)=Floor ▶→ Return Node
     False ▶→ tiếp

[ForEach Clones — Clones đã kiểu BP_FurnitureActor, KHÔNG Cast lại (UE5 tự báo lỗi thừa)]
LoopBody ▶→ Branch(IsValid(Array Element))
   False → (bỏ qua, dead-end hợp lệ trong Loop Body)
   True  ▶→ GET Array Element.PlacementSurfaceType ●→ SET stype
           Get Actor Bounds(Target=Array Element) → Origin, BoxExtent
              _bottom = Break Vector(Origin).Z − Break Vector(BoxExtent).Z    (Subtract)
              _top    = Break Vector(Origin).Z + Break Vector(BoxExtent).Z    (Add)
           SET AllMinZ = Min(AllMinZ, _bottom)
           SET AllMaxZ = Max(AllMaxZ, _top)
           Branch(stype == "Ceiling")                     ← Equal (Name)
             True  → SET AnyCeiling=true → (hết, ForEach lặp tiếp)
             False → Branch(stype == "Wall")
                       True  → SET AnyWall=true
                               ▶→ SET WallMinZ = Min(WallMinZ, _bottom)      ← MỞ RỘNG 20/07
                               → (hết)
                       False → SET HasFloor=true          ← "Floor"/None/khác đều vào đây
                               SET FloorMinZ = Min(FloorMinZ, _bottom)
                               → (hết)
Completed ▶→ [tính kết quả]

   — Điều kiện quyết Floor thắng — MỞ RỘNG 20/07 (Wall-priority rule):
   ThangFloor = HasFloor AND (NOT AnyWall OR FloorMinZ < WallMinZ)
   ("có Floor, VÀ (không có Wall, HOẶC Floor thấp hơn đáy Wall — đứng độc lập trên sàn thật,
     không phải đồ tựa trên vật Wall như bàn thờ)")

   Branch(ThangFloor)
     True:
        SET DeltaZ(Return)  = AnchorZ − FloorMinZ
        SET Category(Return) = Floor
        ▶→ Return Node
     False:
        — Nhóm non-Floor: margin fix — MỞ RỘNG 20/07 (không center, đáy nổi trên Anchor)
        SET DeltaZ(Return) = (AnchorZ − AllMinZ) + 10.0
        Branch(AnyCeiling AND NOT AnyWall)
          True  → SET Category(Return) = Ceiling ▶→ Return Node
          False → Branch(AnyWall AND NOT AnyCeiling)
                    True  → SET Category(Return) = Wall  ▶→ Return Node
                    False → SET Category(Return) = Other ▶→ Return Node
```

**Đếm Return Node:** guard rỗng + Floor + Ceiling + Wall + Other = **5 đường** tới Return
Node — đúng L2, tránh lặp bug P1.G3 (Function trả garbage vì thiếu 1 nhánh).

**2 mở rộng phát sinh từ test thật (KP2 đã duyệt trong phiên, không nằm trong task card gốc):**
1. **Wall-priority rule** — nếu chỉ dùng `HasFloor` đơn thuần (như thiết kế Nấc 1 ban đầu), combo
   bàn thờ (`combo_C470030D...` — 1 item Wall + 14 item Floor "đồ trên kệ") sẽ luôn thắng về
   Floor, kéo cả cụm kể cả mount tường xuống sàn — sai vì các item Floor này là "floor tương đối
   của cái kệ", không phải floor tuyệt đối của phòng. Fix: so `FloorMinZ` với `WallMinZ` — Floor
   nằm cao hơn/ngang đáy Wall (đang tựa lên) → Wall thắng; Floor nằm thấp hơn hẳn (đứng độc lập,
   vd sofa+tranh tường) → Floor vẫn thắng như cũ.
2. **Margin fix** — công thức gốc `DeltaZ = AnchorZ − centerZ` (center bounds vào Anchor.Z) làm
   combo extent Z lớn (bàn thờ, extent=43.8) có nửa dưới xuyên qua mặt dome (Anchor.Z chính là
   điểm tiếp xúc vật lý đáy dome) → chìm/khuất sau mesh. Fix: đáy combo (`AllMinZ`) luôn nổi
   TRÊN Anchor.Z + 10 unit margin, không phụ thuộc center.

**Node "chờ xác nhận"** (ghi `AI_Implementation_Rules.md`, cuhoang đã confirm qua test — chuyển
vào bảng chính): `Equal (Name)`, `Switch on E_ThumbAlignCategory` (Switch on Enum).

### GetComboThumbnail(ComboID) → Texture2D — MỚI G3
Branch(Map Find(Cmb_ThumbnailCache, ComboID) → Value, bFound):
- True → Return(Value)
- False → LoadComboThumbnail(ComboID, MaxSize=256) → LoadedTex
  Branch(IsValid(LoadedTex)):
  - True  → Map Add(Cmb_ThumbnailCache, ComboID, LoadedTex) → Return(LoadedTex)
  - False → Return(None) 🔴 Return Node bắt buộc ở CẢ 2 nhánh — xem DEVIATIONS 15/07/2026.

### InvalidateThumbnail(ComboID) — MỚI G3
Map Remove(Cmb_ThumbnailCache, ComboID).

---

## Custom Events
### SaveComboFromSelection(SelectedActors, Center, ComboName, Description, FolderPath, Tags) ✓K2 04/08/2026 (Lô A — verify T0 của T4)

**Bước 0 (K2Node export 04/08/2026 — chưa từng ghi trước đây):** Entry nhồi TOÀN BỘ 6 param vào
class var cùng tên NGAY ĐẦU event, TRƯỚC Bước 1: `SET Folder Path=FolderPath · Tags_0=Tags ·
Description=Description · Combo Name=ComboName · Center=Center · Selected Actors=SelectedActors`.
Mọi bước sau đọc **class var**, KHÔNG đọc lại pin param — kể cả `Make FComboData` ở Bước 5e
(Name/Description/Tags/FolderPath thật ra đọc class var, không đọc thẳng param như liệt kê ban
đầu bên dưới có thể gợi ý). Đây là lý do T4 (Save đè) can thiệp được bằng đúng 1 điểm — xem
Bước 5a.

**Bước 1:** Guard Length < 2 → dead-end  
**Bước 3:** CLEAR LeafGroupIDs → ForEach SelectedActors → unique GroupID != "" → ADD  
**Bước 3b (C0-LCA):** CLEAR SaveCombo_ComboGroups → CalculateLCAList → ForEach LCARoots → GetGroupsInHierarchy → ADD (unique)  
**Bước 4:** CLEAR TokenMap → ForEach ComboGroups → token = "g"+index → ADD map  
**Bước 5a:** SET SaveCombo_ComboID = "combo_"+NewGuid — **✓K2 04/08/2026 xác nhận: `NewGuid()`
chạy VÔ ĐIỀU KIỆN, không Branch, không nhận ID từ ngoài; `SaveCombo_ComboID` là class var SET
đúng 1 chỗ duy nhất trong cả event.** Mọi thứ phía sau khóa theo biến này (path `.json` Bước 6,
`BeginThumbnailCapture(ComboID)` Bước 7). Quyết định T4 (nới hàm này cho Save đè bằng 1 Branch
tại đúng điểm này) ghi ở `Plans/03-08-2026_SaveAsOverwrite_Execution_Plan.md` mục 4 (bổ sung) —
**CHƯA thực thi**.  
**Bước 5b:** CLEAR OutputGroups/Items  
**Bước 5c:** ForEach ComboGroups → resolve ParentToken (via TokenMap, branch "")→ Make FComboGroupData → ADD OutputGroups  
**Bước 5d:** ForEach SelectedActors → Cast → CLEAR MaterialOverrides_SaveCombo → ForEach MaterialPaths → FindMaterialRowNameByPath → ADD; SET ItemRowName_SaveCombo: Branch RowName.ToString=="None" → True: ParseIntoArray(MeshPath, ".") → Last Index → Get → SET ItemRowName_SaveCombo; False: SET ItemRowName_SaveCombo = RowName gốc; Branch GroupToken → Make FComboItemData(RowName=ItemRowName_SaveCombo) → ADD OutputItems  
**Bước 5e (C4 — trước Make FComboData):**
`CalculateComboBoundingExtent(SelectedActors) → ReturnVec → SET SaveCombo_BoundingExtent`

**Bước 5e:** Make FComboData — tất cả fields:
- ComboID ← SaveCombo_ComboID
- Name ← param ComboName
- Description ← param Description
- Tags ← param Tags (Array\<String\>)
- Category = "MyCombo" (hardcode tạm — Phase B)
- CreatedAt ← UTC Now → Convert Date Time To String
- AppVersion = "1.0.0"
- FolderPath ← param FolderPath
- Items ← SaveCombo_OutputItems
- Groups ← SaveCombo_OutputGroups
- AuthorID = "" (default)
- Visibility = "Private" (default)
- BoundingBoxExtent ← SaveCombo_BoundingExtent  ← C4
**Bước 6:** GetCombosDir → MakeDirectory → ComboToJson → SaveStringToFile  
**Bước 7 (Gate F 21/07/2026 — nối Studio pipeline, ĐÈ bản G4 15/07 chụp in-place) — ✓K2
04/08/2026 tái xác nhận:** Sau SaveStringToFile → Branch(bSaveOK):
```
True  ▶→ BeginThumbnailCapture(
           ComboID  = SaveCombo_ComboID,
           DeltaYaw = Cmb_StudioCamYaw − Cmb_PendingUserCamYaw)
        [HẾT nhánh True — KHÔNG Broadcast ở đây; Event Tick tail lo Broadcast
         sau khi Finish capture xong]
False ▶→ Broadcast OnComboLibraryChanged   ← JSON ghi fail vẫn broadcast (thiết kế P1)
```
- XÓA hẳn khối "build ExtraHiddenActors (BaseGizmo+FurniturePivot)" — camera Remote Studio ở xa
  (500000,500000), gizmo/pivot cạnh player không lọt khung → thừa.
- XÓA `BeginComboCapture` + `Delay(3.0)` + `FinishComboCapture(SelectedActors)` cũ ở Bước 7 — đã
  chuyển vào `BeginThumbnailCapture` (xem mục riêng bên trên).
- Trước Gate F, Bước 7 chụp actor THẬT tại chỗ trong phòng (P1 in-place, KHÔNG dùng Remote
  Studio, KHÔNG qua temporal accumulation N=24) → ảnh 2048² thô 1-frame (fallback path C++ vì
  buffer accumulate rỗng). Sau Gate F, Save thật chạy qua đúng pipeline Studio — bug tự đóng.

Q8: Custom Event | không Object access mới cần guard | L2: True kết thúc hợp lệ sau 1 call (Tick
broadcast), False broadcast rồi hết — không dead-end | Delay đã DỜI khỏi event này → không latent
trong SaveComboFromSelection | 6A: mọi path dẫn tới đúng 1 Broadcast (True qua Tick, False trực
tiếp)

**Bước 8:** ĐÃ GỘP vào Bước 7 — nhánh False broadcast trực tiếp, nhánh True broadcast qua Event
Tick tail (xem mục Event Tick bên dưới). Không còn bước riêng.

---

## C2 — SpawnComboByID (thêm vào v1.3 — 22/06/2026)

---

### Class Variables mới (C2)

| Tên | Kiểu | Vai trò |
|-----|------|---------|
| Cmb_bSpawnInFlight | bool (default False) | Guard chống double-spawn |
| InputManagerRef | BP_FurnitureInputManager | Set ở BeginPlay, clear End Play |
| UndoManagerRef | BP_UndoManager | Set ở BeginPlay, clear End Play |
| DT_Materials | DataTable | Hard ref DT_MaterialInstancesCatalog, gán trong defaults |
| Cmb_SpawnedActors | Array BP_FurnitureActor | Accumulate Phase 3, CLEAR đầu event + End Play |

---

### BeginPlay (update)
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → SET InputManagerRef

Get All Actors Of Class(BP_UndoManager) → Get(0) → SET UndoManagerRef

### End Play (update)
SET InputManagerRef = None

SET UndoManagerRef = None

SET Cmb_bSpawnInFlight = False

CLEAR Cmb_SpawnedActors

← C9.b/C9.c (30/07/2026):
SET Cmb_LastSpawnSucceeded = False

CLEAR Cmb_ReplaceActors   ← R4, hard ref actor

---

### F_LoadComboData(ComboID: String → OutData: FComboData, bSuccess: bool)
**Local vars:** FilePath (String), JsonString (String)

GetCombosDir → Append "/" + ComboID + ".json" → SET FilePath

LoadStringFromFile(FilePath, OutContent→SET JsonString) → bFileOK

Branch bFileOK:

- False → Return(bSuccess=False, OutData=default)
- True  → JsonToCombo(JsonString, OutCombo) → bParseOK

Branch bParseOK:

- False → Return(bSuccess=False, OutData=default)
- True  → Return(bSuccess=True, OutData=OutCombo)

---

### F_BuildTokenGUIDMap(InGroups: Array FComboGroupData → OutMap: Map String→String)
**Local vars:** ResultMap (Map String→String), NewGUID (String)
*(Local var reset mỗi lần call — không cần CLEAR)*

ForEach InGroups:

Loop Body:

- New Guid → Guid To String → SET NewGUID
- Break FComboGroupData → Token
- Map Add(ResultMap, Key=Token, Value=NewGUID)

Completed:

- Return(OutMap = ResultMap)

---

### F_RegisterComboGroups(InGroups: Array FComboGroupData, TokenMap: Map String→String, ParentGroupGUID: String, ComboID: String)
**Local vars:** LocalGroups (Array S_GroupData), ParentGD (S_GroupData), ChildGD (S_GroupData), ResolvedParentID (String), ResolvedSourceComboID (String), ChildGroupID (String), CurToken (String), CurParentToken (String), CurGroupName (String)

GET InputManagerRef.Groups → SET LocalGroups

Branch (InGroups.Length == 0):

// Case A: combo không có group → tạo wrapper

- True: Make S_GroupData(GroupID=ParentGroupGUID, GroupName="ComboGroup", ParentGroupID="", bIsLocked=False, SourceComboID=ComboID) → SET ParentGD → Array ADD(LocalGroups, ParentGD) → merge về SET+Sync

// Case B: combo có group → không tạo wrapper, dùng structure gốc

- False: ForEach InGroups:

  Loop Body:

  - Break FComboGroupData → SET CurToken, CurGroupName, CurParentToken
  - Map Find(TokenMap, CurToken) → SET ChildGroupID
  - Branch (CurParentToken == ""):
    - True (root group): SET ResolvedParentID = ""; SET ResolvedSourceComboID = ComboID
    - False (non-root group): Map Find(TokenMap, CurParentToken) → SET ResolvedParentID; SET ResolvedSourceComboID = ""
    - (merge)
  - Make S_GroupData(GroupID=ChildGroupID, GroupName=CurGroupName, ParentGroupID=ResolvedParentID, bIsLocked=False, SourceComboID=ResolvedSourceComboID) → SET ChildGD → Array ADD(LocalGroups, ChildGD)

  Completed → merge về SET+Sync

// Both cases merge here:

SET InputManagerRef.Groups = LocalGroups

InputManagerRef → SyncGroupsToContainer

**Logic group nesting:**
- Case A (InGroups rỗng): tạo 1 wrapper group bọc toàn bộ combo. SourceComboID trên wrapper.
- Case B (có groups): root groups (ParentToken=="") nhận SourceComboID=ComboID, ParentGroupID="". Non-root nhận ParentGroupID=TokenMap[ParentToken], SourceComboID="". Không tạo wrapper thêm → tránh double nesting.

---

### F_ApplyMaterialOverrides(TargetActor: BP_FurnitureActor, MaterialRowNames: Array String)
**Local vars:** ConvertedPaths (Array String), bFound (bool)

ForEach MaterialRowNames:

Loop Body:

- Branch (Array Element == ""):
  - True  → Array ADD(ConvertedPaths, "")
  - False → Get Data Table Row(DT_Materials, String to Name(Array Element))
    - Row Found: Break S_MaterialInstancesData → MaterialPath → Array ADD(ConvertedPaths, MaterialPath)
    - Row Not Found: Array ADD(ConvertedPaths, "") ← giữ slot alignment
  - (merge, loop tiếp)

Completed:

SET TargetActor.MaterialOverrides = ConvertedPaths

TargetActor → LoadMaterialsAsync(Overrides=ConvertedPaths, Index=0)

⚠️ Row Not Found ADD "" để giữ slot index alignment cho LoadMaterialsAsync.

---

### Custom Event SpawnComboByID(ComboID: String, SpawnLocation: Vector, SnapshotLabel: String) — v1.14: +SnapshotLabel (C9.b, 30/07/2026)

⚠️ **GOTCHA — Custom Event input KHÔNG có Default Value** (khác Function). Caller cũ sau khi
thêm pin sẽ truyền `""` → `CaptureSnapshot("")` → history có mục trống. Xử lý ở Sub-step D bằng
node `Select` (pure, không cần Local Variable — Custom Event không có Local Variable theo L9):
`(SnapshotLabel == "") ●→ Select.Index`, `Select.True = "SpawnCombo"`, `Select.False =
SnapshotLabel`, `Select.Return ●→ CaptureSnapshot.ActionName`.

#### Sub-step A — Guard + Load
Dòng ĐẦU TIÊN, TRƯỚC cả Branch(Cmb_bSpawnInFlight):
```
▶→ SET Cmb_LastSpawnSucceeded = False   ← v1.14 (C9.b) — BẮT BUỘC ở đây
```
Vì sao bắt buộc: Sub-step A có 2 đường thoát sớm (guard `Cmb_bSpawnInFlight`, và
`F_LoadComboData` fail) — cả 2 KHÔNG chạy tới Sub-step D. Không reset đầu hàm →
`Cmb_LastSpawnSucceeded` giữ giá trị `True` cũ từ lần gọi trước → `ReplaceCombo` tưởng lần này
thành công → không rollback → cụm cũ đã destroy, cụm mới không spawn → LỖ TRỐNG trong scene.

Branch(Cmb_bSpawnInFlight):

- True  → dead-end
- False → SET Cmb_bSpawnInFlight=True; CLEAR Cmb_SpawnedActors

GET InputManagerRef.EditModeStack → Length > 0 → Branch:

- True  → ExitEditModeFull → (merge)
- False → (merge)

F_LoadComboData(ComboID) → FComboData, bSuccess

Branch(bSuccess):

- False → SET Cmb_bSpawnInFlight=False → dead-end
- True  → (Sub-step B)

#### Sub-step B — Build maps + Register groups
Break FComboData → Groups, Items

F_BuildTokenGUIDMap(InGroups=Groups) → TokenToNewGUID

New Guid → Guid To String → ParentGroupGUID

F_RegisterComboGroups(InGroups=Groups, TokenMap=TokenToNewGUID, ParentGroupGUID=ParentGroupGUID, ComboID=ComboID)

→ (Sub-step C)

*Data pins từ Break FComboData, TokenToNewGUID, ParentGroupGUID được wire trực tiếp vào Sub-step C — stable vì computed 1 lần qua execution wire.*

#### Sub-step C — Phase 3: ForEach spawn actors
ForEach (Array = Items từ Break FComboData):

Loop Body:

- Break FComboItemData(Array Element) → RowName(String), RelLocation, RelRotation, Scale, SurfaceType(String), MaterialOverrides(Array String), GroupToken(String)
- Get Data Table Row(DT_FurnitureCatalog, String to Name(RowName)) → bFound
- Branch(bFound):
  - False → **[MỚI, K1, 23/07/2026]** Get Game Instance → Cast Foff_GameInstance →
    IsValid(ToastRef) → True: `ToastRef.ShowToast("Bỏ qua món: RowName '" + RowName + "' không
    tồn tại", 2.5)` / False: dead-end → sau đó dead-end (skip item, ForEach lặp tiếp) —
    ⚠️ doc cũ ghi nhầm "Print skip" ở đây, thực tế TRƯỚC 23/07 không có gì (dead-end trần trụi,
    item lỗi bỏ qua âm thầm). Gọi thẳng `GameInstance.ToastRef.ShowToast` (không qua
    `ShowToastMsg` của `WBP_FurnitureInventory`) vì `BP_ComboManager` là Actor, không có đường
    gọi Function riêng của Widget đó.
  - True  → Break S_FurnitureData → MeshFolderPath
  - Construct MeshPath: Append(MeshFolderPath, "/", RowName, ".", RowName) → MeshPath
  - InputManagerRef → SpawnFurnitureCopy(MeshPath=MeshPath, DAPath="", SpawnLocation=Vector Add(SpawnLocation input, RelLocation), SpawnRotation=RelRotation, SpawnScale=Scale, MaterialOverrides=Make Array(rỗng), SurfaceType=String to Name(SurfaceType), bAutoSelect=False, bAddToRecent=False ← K3, 21/07/2026, checkbox "Add to Recent" trước đó có tick/chưa pin) → NewActor
  - IsValid(NewActor): False → dead-end; True → continue
  - SET NewActor.RowName = String to Name(RowName)
  - Branch(GroupToken == ""):
    - True  → Branch(FComboData.Groups.Length == 0):
      - True  → SET NewActor.GroupID = ParentGroupGUID ← Case A wrapper
      - False → SET NewActor.GroupID = ""              ← Case B ungrouped
    - False → Map Find(TokenToNewGUID, Key=GroupToken) → Value → SET NewActor.GroupID
    - (merge)
  - F_ApplyMaterialOverrides(TargetActor=NewActor, MaterialRowNames=MaterialOverrides từ Break FComboItemData)
  - Array ADD(Cmb_SpawnedActors, NewActor)

Completed → (Sub-step D)

#### Sub-step D — Post-spawn
Branch(Cmb_SpawnedActors.Length == 0):

- True  → SET Cmb_LastSpawnSucceeded=False ← v1.14 (C9.b) → SET Cmb_bSpawnInFlight=False → dead-end
- False →
  - SET Cmb_LastSpawnSucceeded = True ← v1.14 (C9.b)
  - InputManagerRef → DeselectAll
  - InputManagerRef → SelectActors(Cmb_SpawnedActors)
  - UndoManagerRef  → CaptureSnapshot( (SnapshotLabel=="") ? "SpawnCombo" : SnapshotLabel )  ← v1.14: qua node Select, xem ghi chú GOTCHA trên
  - SET Cmb_bSpawnInFlight = False
  - CLEAR Cmb_SpawnedActors

Định nghĩa fail đã chốt: 0 item spawn được = fail toàn phần → `Cmb_LastSpawnSucceeded=False` →
caller (`ReplaceCombo`) rollback. Skip lẻ tẻ vài `RowName` (K1 toast) vẫn tính success, KHÔNG
rollback.

**Test C2 (7/7 PASS — 22/06/2026):**
1. Spawn nested 2 cấp → group cha tồn tại, SourceComboID đúng ✅
2. Spawn lần 2 → 2 cụm độc lập, GroupID khác nhau ✅
3. Undo → cả cụm biến 1 lần; Redo → quay lại đủ ✅
4. Spawn khi Edit Mode → tự thoát rồi spawn ✅
5. RowName bậy → skip item, không crash ✅
6. Save EMS → Load → combo + group + SourceComboID nguyên vẹn ✅
7. Spawn 20 món → không khựng quá 0.5s ✅

---

## C9.b/C9.c — Replace Combo (30/07/2026)

### Class Variables mới (C9.b/C9.c)

| Tên | Kiểu | Vai trò |
|-----|------|---------|
| Cmb_LastSpawnSucceeded | bool (default False) | Đọc bởi `ReplaceCombo` sau `SpawnComboByID` để quyết định rollback. KHÔNG clear ở cuối event (caller cần đọc) — chỉ SET False ở End Play cho nhất quán |
| Cmb_ReplaceAnchor | Vector | Anchor cụm hiện tại trước khi destroy, dùng làm `SpawnLocation` cho cụm mới. Dùng cho C9.c |
| Cmb_ReplaceActors | Array BP_FurnitureActor | Actor của cụm sắp bị thay, CLEAR đầu event + cuối event + End Play (R4 — hard ref actor) |

⚠️ **Deviation so với `docs/Plans/24-07-2026_C9_Execution_Plan.md` §6:** plan gốc đặt tên
`Cmb_ReplaceCenter` (tính bằng `CalculateCenter`, centroid thuần) — as-built đổi thành
`Cmb_ReplaceAnchor` (tính bằng `CalculateComboAnchor`, xem `Blueprints/BP_FurnitureInputManager.md`
— center XY + anchorZ theo Floor/Ceiling). Lý do: sửa bug positioning anchor-vs-center mismatch
(combo mới spawn lệch cao độ so với cụm cũ nếu dùng centroid thuần). Xem `DEVIATIONS.md` mục
"C9 Replace — 30/07/2026".

### Custom Event ReplaceCombo(RootGroupID: String, NewComboID: String)

```
0 ▶→ CLEAR Cmb_ReplaceActors          ← CLEAR class var persistent ở ĐẦU function. Không clear →
                                          giữ hard ref actor của lần replace TRƯỚC (vi phạm R4).

1 ▶→ Branch(Cmb_bSpawnInFlight)
       True  ▶→ ToastRef.ShowToast("Đang xử lý, thử lại sau", 2.5) → dead-end
       False ▶→ (tiếp)
       ⚠️ CHỈ ĐỌC — TUYỆT ĐỐI KHÔNG SET cờ này (Sub-step A của SpawnComboByID cũng check đúng
          biến đó; SET True ở đây sẽ tự chặn chính lệnh spawn phía sau).

2 ▶→ Branch(RootGroupID == "" OR NewComboID == "") True ▶→ dead-end

3 ▶→ InputManagerRef.GetAllDescendantActors(RootGroupID) ●→ SET Cmb_ReplaceActors

4 ▶→ Branch(Cmb_ReplaceActors.Length == 0)
       True  ▶→ ToastRef.ShowToast("Cụm rỗng — không thay được", 2.5) → dead-end
       False ▶→ InputManagerRef.CalculateComboAnchor(Cmb_ReplaceActors) ●→ SET Cmb_ReplaceAnchor
       ⚠️ Guard bắt buộc — `CalculateComboAnchor`/`CalculateCenter` đều chia cho Length actor;
          Length==0 → spawn combo mới ở gốc tọa độ thế giới. Không crash nên rất dễ lọt.

5 ▶→ InputManagerRef.DestroyComboCluster(RootGroupID)

6 ▶→ SpawnComboByID(ComboID=NewComboID, SpawnLocation=Cmb_ReplaceAnchor, SnapshotLabel="ReplaceCombo")

7 ▶→ Branch(Cmb_LastSpawnSucceeded)
       True  ▶→ (không làm gì — snapshot đã capture bên trong SpawnComboByID)
       False ▶→ UndoManagerRef.RestoreCurrentSnapshot()   ← xem Blueprints/BP_UndoManager.md
             ▶→ ToastRef.ShowToast("Thay thế thất bại — đã khôi phục cụm cũ", 2.5)
   [2 nhánh MERGE] ▶→ CLEAR Cmb_ReplaceActors
```
Toast gọi thẳng `Get Game Instance → Cast Foff_GameInstance → IsValid(ToastRef) →
ToastRef.ShowToast(...)`. KHÔNG dùng `ShowToastMsg` (Function của `WBP_FurnitureInventory` —
Actor không gọi được), giống pattern K1 ở `SpawnComboByID` Sub-step C.

**Test (nguồn: Execution Plan §6 + delta 30/07):**
1. Spawn combo A → chọn cụm → replace bằng B → cụm A biến, B đứng đúng chỗ cũ → Ctrl+Z → A quay
   lại nguyên vẹn (group + SourceComboID)
2. Replace bằng combo JSON hỏng/ID không tồn tại → `RestoreCurrentSnapshot` tự chạy → A còn
   nguyên, scene KHÔNG lỗ trống, toast hiện
3. Replace 2 lần liên tiếp thật nhanh → lần 2 bị guard `Cmb_bSpawnInFlight` chặn
4. Replace 3 lần liên tiếp → `InputManagerRef.Groups.Length` ổn định, KHÔNG tăng dần (orphan group)

---

## P2 Gate D — Noise + Aliasing Fix (19/07/2026)

⚠️ Mục này mô tả theo hướng dẫn đưa trong session, cuhoang xác nhận test PASS (mịn hơn, không
giật) — nhưng CHƯA có export K2Node để đối chiếu node-by-node ở phần accumulate đầu Tick (phần
Finish tail CUỐI đã đối chiếu export K2Node thật 21/07/2026, xem mục "SỬA 3 điểm" bên dưới). Coi
graph accumulate là mô tả dự kiến, không phải sự thật tuyệt đối; nếu khác graph thật, sửa lại
theo graph thật. Đè lên chuỗi build Function/Event nối vào sau `Delay(3.0)` warmup (nay là
`Delay #2` trong `BeginThumbnailCapture`, xem mục riêng), TRƯỚC khi gọi `FinishComboCapture`
(trước đây gọi thẳng ngay sau Delay).

Bối cảnh đầy đủ (7 giả thuyết đã loại, quyết định temporal accumulation thủ công thay Viewport
Capture, root cause SceneCapture2D không có temporal thật): xem `DEVIATIONS.md` mục
"SPRINT 5 — 19/07/2026 — P2 Noise + Aliasing Fix". Signature C++ mới (`AccumulateComboFrame`,
`ResetComboAccumulation`) + hành vi đổi của `BeginComboCapture`/`FinishComboCapture` (SSAA 2×,
temporal N=24, linear-space accumulate): xem `Data/ComboSerializer_Reference.md` mục
"Class: UComboThumbnail".

### Sửa chuỗi sau Delay(3.0) warmup
`FinishComboCapture` (giữ nguyên dây `ComboID`/`ComboActors`) tách khỏi `Delay`, nối lại ở cuối
Event Tick thay vì gọi thẳng. Chèn giữa:
```
Delay(3.0) hoàn tất
▶→ ResetComboAccumulation(Cmb_CaptureHandle)
▶→ SET Cmb_AccumFramesLeft = Cmb_AccumTargetFrames
▶→ Set Actor Tick Enabled(Target=self, bEnabled=true)
```

### Event Tick (self) — mới 19/07, Finish tail SỬA 21/07/2026 (Gate F, đối chiếu export K2Node thật)
```
Event Tick
▶→ Branch(Cmb_AccumFramesLeft <= 0)
     True  ▶→ dead-end (không accumulate → không làm gì, rẻ)
     False ▶→ AccumulateComboFrame(Cmb_CaptureHandle)
           ▶→ SET Cmb_AccumFramesLeft = Cmb_AccumFramesLeft − 1
           ▶→ Branch(Cmb_AccumFramesLeft <= 0):
                True ▶→ SetActorTickEnabled(false)
                     ▶→ FinishComboCapture(
                           CaptureHandle = Cmb_CaptureHandle,
                           ComboID       = Get Cmb_PendingCaptureComboID,   ← [SỬA 21/07] trước là Concat(DebugTestComboIDs[idx],"_studio")
                           ComboActors   = Cmb_StudioClones)
                     ▶→ Branch(bDebugMode): True→Print "Capture "+(OK/FAIL) / False→(merge)
                     ▶→ ForEach(Cmb_StudioClones): IsValid→True→DestroyActor / False→dead-end
                     ▶→ Array Clear(Cmb_StudioClones)
                     ▶→ SET Cmb_CaptureHandle = None
                     ▶→ SET Cmb_bThumbBusy = false
                     ▶→ Broadcast OnComboLibraryChanged   ← [THÊM 21/07] cuối cùng, sau SET
                          bThumbBusy; chạy MỌI lần Finish (kể cả capture fail — card fallback 🧩)
                False ▶→ dead-end (chờ frame sau — hợp lệ)
```
3 thay đổi so với bản 19/07 (Gate F 21/07/2026, đối chiếu export K2Node thật của Event U trước
khi xóa):
1. `ComboID` pin Finish: đổi từ `Concat(Cmb_DebugTestComboIDs[Cmb_DebugComboIndex], "_studio")`
   → `Get Cmb_PendingCaptureComboID`.
2. THÊM `Broadcast OnComboLibraryChanged` sau node cuối (`SET Cmb_bThumbBusy=false`).
3. XÓA orphan sau khi rút dây: node Concat "_studio", GetArrayItem, Get
   Cmb_DebugTestComboIDs, Get Cmb_DebugComboIndex. 2 biến class `Cmb_DebugTestComboIDs`/
   `Cmb_DebugComboIndex` orphan hoàn toàn sau khi debug phím U bị xóa (1f) — đã xóa.

Q8: Event Tick (self) — không phải Custom Event/Function nên dead-end tính khác | IsValid:
`AccumulateComboFrame`/`ResetComboAccumulation` tự IsValid(CaptureHandle) trong C++, Finish tự
IsValid nội bộ (C++) | L2: dead-end nhánh "chưa đủ frame" HỢP LỆ — giống Sequence.Then, Tick tự
gọi lại mỗi frame | No Latent ✓ | 6A: Broadcast chạy sau MỌI Finish kể cả fail (thiết kế P1);
EndPlay đã mở rộng (xem dưới) ✓

### Event End Play — mở rộng bắt buộc
EndPlay hiện có (dọn `Cmb_CaptureHandle` nếu tắt PIE giữa Delay, R4 — xem Gate A Việc 5) —
thêm:
```
▶→ Set Actor Tick Enabled(self, false)
▶→ ResetComboAccumulation(Cmb_CaptureHandle)
```
Không thêm = leak buffer C++ nếu PIE tắt giữa lúc accumulate (con trỏ key chết, không ai dọn)
— cùng loại bug với `Bugs/Bug_GPU_VRAM_Crash.md`, lần này RAM chứ không VRAM.

**Test:** noise (temporal accumulation N=24) ✅ CONFIRM — mịn hơn rõ, không giật lúc chụp.
Aliasing/SSAA ✅ CONFIRM DONE — cuhoang tự chạy lại checklist test đầy đủ (kích thước ảnh đúng,
không giật thêm dù RT giờ 2048²).

---

## Lịch sử cập nhật
| Ngày | Version | Nội dung |
|------|---------|----------|
| 21/06/2026 | 1.0 | Tạo mới — T2 core + C0 LCA fix + C1 material RowName |
| 22/06/2026 8:56 AM | 1.2 | C0 DONE — thêm class var ItemRowName_SaveCombo, Bước 5d: Branch RowName=="None" → fallback parse MeshPath (ParseIntoArray "."/LastIndex). 3 case A/B/C PASS. |
| 22/06/2026 | 1.3 | C2 SpawnComboByID DONE — 5 class var mới, 4 functions (F_LoadComboData, F_BuildTokenGUIDMap, F_RegisterComboGroups, F_ApplyMaterialOverrides), Custom Event SpawnComboByID (4 sub-steps). 7/7 test PASS. Group nesting fix: Case A (no groups→wrapper) / Case B (has groups→no wrapper, root groups nhận SourceComboID). |
| 23/06/2026 | 1.4 | C3a: SaveComboFromSelection mở rộng signature (thêm FolderPath, Tags). Bước 5e: Make FComboData đầy đủ tất cả fields (Category hardcode "MyCombo" tạm, CreatedAt UTC Now, AppVersion 1.0.0, AuthorID/Visibility default, FolderPath+Tags từ param). |
| 24/06/2026 | 1.5 | C4: thêm CalculateComboBoundingExtent function; class var SaveCombo_BoundingExtent; Bước 5e tính BoundingBoxExtent trước Make FComboData + gán vào field. |
| 15/07/2026 | 1.6 | G2+G3+G4: class var Cmb_ThumbnailCache + Cmb_CaptureHandle. Function GetComboThumbnail (🔴 Return Node bắt buộc cả 2 nhánh — bug fix, xem DEVIATIONS) + InvalidateThumbnail. Bước 7 SaveComboFromSelection hoàn chỉnh (capture thật, nối vào bSaveOK Branch, merge về Broadcast). |
| 17/07/2026 | 1.7 | P2 Gate A DONE: Custom Event `SpawnComboForThumbnail(ComboID, DeltaYaw=0)` mới (guard Cmb_bThumbBusy → F_LoadComboData → ForEach spawn clone sạch → Cmb_StudioClones) + chuỗi debug phím U (ground-align, BeginComboCapture/FinishComboCapture, Delay 0.5→3.0 ceiling tạm). Bug fix aliasing `Add Actor World Offset` dùng nhầm Array Element giữa 2 For Each Loop liên tiếp. Test PASS 6/7 case. |
| 19/07/2026 | 1.8 | P2 Gate D — Noise + Aliasing Fix: class var mới `Cmb_AccumFramesLeft`/`Cmb_AccumTargetFrames` (default 24); `FinishComboCapture` tách khỏi `Delay(3.0)`, nối lại cuối Event Tick mới (mượn Tick cho temporal accumulation N frame — `AccumulateComboFrame` mỗi frame, `Set Actor Tick Enabled` bật/tắt); Event End Play mở rộng thêm `Set Actor Tick Enabled(false)` + `ResetComboAccumulation`. ⚠️ Chưa có export K2Node đối chiếu — mô tả theo hướng dẫn session, cuhoang xác nhận test PASS. Chi tiết C++: `Data/ComboSerializer_Reference.md`, `DEVIATIONS.md` 19/07/2026. |
| 20/07/2026 | 1.9 | P2 Gate D Nấc 1 — Surface-Aware Ground-Align, Bug-CeilingGroundAlign FIXED: Function mới `ResolveThumbAlign(Clones) → DeltaZ, Category` (Enum `E_ThumbAlignCategory`) thay khối align inline đơn nhất (2 ForEach dùng `Cmb_ThumbMinZ`, đã xóa) trong chuỗi debug phím U. Phân loại Floor/Ceiling/Wall/Other theo `PlacementSurfaceType`, gồm 2 mở rộng phát sinh từ test thật (KP2 đã duyệt): Wall-priority rule (so `FloorMinZ` với `WallMinZ`) + margin fix (đáy nhóm non-Floor nổi trên Anchor.Z +10, không center). Switch on Category hiện là STUB (4 pin gộp chung BeginComboCapture) — tách rig riêng Ceiling/Wall là Nấc 2, backlog. Test 6/6 case PASS. Chi tiết: `DEVIATIONS.md` mục "P2 — 20/07/2026 (Nấc 1)". |
| 21/07/2026 | 1.10 | P2 Gate F — nối Studio pipeline vào Save flow thật (DONE). Class var mới: `Cmb_StudioCamYaw`(55.0), `Cmb_PendingUserCamYaw`, `Cmb_PendingCaptureComboID`, `Cmb_DebugLastCaptureDistance`. Custom Event mới `BeginThumbnailCapture(ComboID, DeltaYaw)` (tách khối spawn→align→Begin→enable-tick từ debug U cũ, dùng chung Save flow) + `SetPendingUserCamYaw(Yaw)`. Bước 7 SaveComboFromSelection: THAY capture in-place P1 (chụp actor thật) bằng `BeginThumbnailCapture(SaveCombo_ComboID, DeltaYaw=Cmb_StudioCamYaw−Cmb_PendingUserCamYaw)`; Broadcast nhánh True dời xuống Event Tick tail. Event Tick tail: `ComboID` Finish đổi `Cmb_DebugTestComboIDs[idx]+"_studio"` → `Cmb_PendingCaptureComboID`; THÊM Broadcast cuối. FixedAngle.Yaw split-pin đọc `Cmb_StudioCamYaw` (giá trị thật=55, doc cũ ghi nhầm 0). XÓA debug phím U + Enable Input + `bDebugTestThumb`/`Cmb_DebugTestComboIDs`/`Cmb_DebugComboIndex`. Hệ quả phụ: Save thật hết bug 2048² thô 1-frame (giờ qua đúng N=24+SSAA). Bug framing rotation-variant Radius phát hiện+fix (C++, xem `Data/ComboSerializer_Reference.md` + `DEVIATIONS.md`). Feature-CanonicalStudioAngle ghi backlog Sprint 6 (`Bugs/Open_Bugs.md`). |
| 21/07/2026 | 1.11 | K3 (bAddToRecent) DONE — `SpawnComboByID` Phase 3 (Sub-step C): pin `bAddToRecent=False` tại node `SpawnFurnitureCopy` (trước đó checkbox "Add to Recent" có tick, chưa pin — cùng loại thiếu sót đã fix ở `RestoreSnapshot`/BP_UndoManager). Verify qua Blueprint Export Method (K2Node text) + screenshot thật, không đoán qua doc. Test 4 case PASS (spawn combo, Undo/Redo, spawn furniture từ card, copy/paste). Chi tiết: `Bugs/Open_Bugs.md` mục K3, `Blueprints/BP_UndoManager.md` v1.11. |
| 23/07/2026 | 1.13 | K1 (WBP_Toast) DONE — `SpawnComboByID` Sub-step C, nhánh `Get Data Table Row` → `Row Not Found`: THÊM toast "Bỏ qua món: RowName '...' không tồn tại" (gọi thẳng `GameInstance.ToastRef.ShowToast`, không qua `ShowToastMsg` — Actor không có đường Function Widget). Trước đây dead-end trần trụi (doc cũ ghi nhầm "Print skip", thực tế chưa từng có). Test K1 5/5 case PASS (case 5 = chỗ này). Chi tiết: `Widgets/WBP_Toast.md` (mới), `Widgets/WBP_FurnitureInventory.md` v3.14. |
| 22/07/2026 | 1.12 | Dimension Fix — `CalculateComboBoundingExtent` đổi `Get Actor Bounds` (World AABB, phồng khi actor tự xoay tại chỗ) → `Get Local Bounds`×Scale+Location (bounds local mesh, không bị Actor Rotation ảnh hưởng). Node mới `Get Local Bounds` chờ xác nhận (`AI_Implementation_Rules.md`). Giới hạn còn lại: cả đội hình combo xoay lệch trục vẫn phồng theo World AABB — merge backlog `Feature-CanonicalStudioAngle` (Sprint 6, cần field `ReferenceYaw`). Combo lưu trước 22/07/2026 giữ số cũ, không migrate hàng loạt. Test 3 case PASS. Ảnh hưởng: `WBP_ComboCard.md` mục Field Kích thước đọc field này. |
| 30/07/2026 | 1.14 | **C9.b/C9.c DONE (delta "C9 Replace: Folder Highlight + Chip Fix & C9.b–C9.f").** `SpawnComboByID` +param `SnapshotLabel` (qua node `Select`, Custom Event input không có Default Value); Sub-step A reset `Cmb_LastSpawnSucceeded=False` đầu tiên (bắt buộc — 2 đường thoát sớm không chạy tới Sub-step D); Sub-step D SET cờ ở cả 2 nhánh. Custom Event mới `ReplaceCombo(RootGroupID, NewComboID)` — destroy cụm cũ (`DestroyComboCluster`) → spawn cụm mới tại `Cmb_ReplaceAnchor` → rollback qua `UndoManagerRef.RestoreCurrentSnapshot()` nếu fail. 3 class var mới: `Cmb_LastSpawnSucceeded`, `Cmb_ReplaceAnchor`, `Cmb_ReplaceActors` (CLEAR đầu event + End Play, R4). **Deviation:** đổi tên `Cmb_ReplaceCenter`→`Cmb_ReplaceAnchor` + `CalculateCenter`→`CalculateComboAnchor` so với `docs/Plans/24-07-2026_C9_Execution_Plan.md` §6 — fix bug anchor-vs-center mismatch. Chi tiết: `Blueprints/BP_FurnitureInputManager.md` (`DestroyComboCluster`), `Blueprints/BP_UndoManager.md` (`RestoreCurrentSnapshot`), `DEVIATIONS.md`. |
| 04/08/2026 15:20 | 1.15 | **Lô A — Verify đường ghi combo (T0 của T4, Save As/Save đè).** `SaveComboFromSelection` re-export K2Node — Bước 1-8 khớp doc cũ 1:1 (không mâu thuẫn), bổ sung **Bước 0** chưa từng ghi (6 param nhồi vào class var ngay Entry, mọi bước sau đọc class var chứ không đọc lại pin param). Xác nhận Bước 5a (`NewGuid()` vô điều kiện, `SaveCombo_ComboID` set đúng 1 chỗ) và Bước 7 (Broadcast `OnComboLibraryChanged` CHỈ ở nhánh `bSaveOK=False`; nhánh True broadcast qua Event Tick tail, không đổi so với doc 1.10). Nguồn: `DELTA_04-08-2026_LoA_SaveCombo_Verify.md`. Xem thêm `Bugs/Open_Bugs.md` mục `Bug-ComboCategoryHardcode` (Category hardcode "MyCombo" — đã ghi nhận từ v1.4, nay lên bug tracking chính thức) + `DEVIATIONS.md` mục "[AS-BUILT] Broadcast OnComboLibraryChanged..." và "[DOC-DRIFT] Plan C7 dựa vào LoadCombo...". |
