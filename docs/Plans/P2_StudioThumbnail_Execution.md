P2 — Combo Thumbnail "Studio Look" — Execution Plan
v1.2 — 17/07/2026 (cuối phiên) — Fable authored (v1.0 16/07), Gate A test kết quả thêm 17/07, Gate B+C kết quả thêm 17/07 cuối phiên. Kế thừa P1 (Begin/Finish pipeline, DONE 15/07). Plan là giả thuyết: lệch thì ghi DEVIATIONS, không tiếc plan.
0. Mục tiêu & phạm vi
Thumbnail combo chuẩn ảnh sản phẩm (tham chiếu IKEA, ảnh cuhoang gửi 15/07): nền đơn sắc liền mạch không horizon, sáng đều, bóng mềm dưới đồ, khung hình + góc + sáng đồng nhất mọi combo (cảm giác UE Content Browser).
Trong scopeNgoài scopeRemote Studio + clone pipeline sạchHướng 2 (preview/xoay tay)Dome + Key/Fill light + Manual EV100Regenerate-all combo cũ (backlog)Camera H-B turntable + DOFDọn Delay mồ côi SpawnComboByID (backlog)Thay capture in-place trong Save flow (Gate F)K3 ngoài phần hạ tầng param
1. Kiến trúc chốt

Remote Studio: XY xa (~500.000, 500.000), GIỮ Z sàn phòng (Exponential Height Fog dày khi Z thấp — không chôn dưới map; giữ Z ⇒ fog y hệt capture P1 hiện tại, không cần tắt ShowFlags).
Clone: Custom Event SpawnComboForThumbnail(ComboID, DeltaYaw=0) — nhân ruột SpawnComboByID (F_LoadComboData → ForEach → GetDataTableRow → SpawnFurnitureCopy → F_ApplyMaterialOverrides), CẮT: ExitEditModeFull / group machinery / Deselect+Select / CaptureSnapshot. Chống 3 cửa bẩn trên từng clone: REMOVE tag "FurnitureSpawned" (BeginPlay tự-tag!), SET GroupID="" (chống auto-join edit scope v1.9), bAutoSelect=False + bAddToRecent=False.
Ground-align (H1): sau spawn + mesh load → combined bounds → offset cả cụm DeltaZ = FloorZ − MinZ. Xử cả combo tường/trần (anchor center-top) lẫn M5 anchor lệch.
H-B "bục xoay": camera + đèn tĩnh tuyệt đối (pitch −15°, yaw StudioCamYaw cố định); xoay CLONE: RelLocation quay quanh Z + RelRotation.Yaw += DeltaYaw, với DeltaYaw = StudioCamYaw − UserCamYaw (chốt lúc BẤM Save). Mặt user đang nhìn = mặt lên ảnh.
Ánh sáng: Key RectLight (source 1–2m, 45°/45° theo trục camera) + Fill đối diện = 1/3 Key (ratio 3:1). Dome trắng/xám = reflector khổng lồ, Lumen bounce = fill ambient miễn phí. Không rim (nền sáng không cần). Đèn tĩnh, set theo combo to nhất — Gate D mới cân nhắc scale theo R_bao nếu combo nhỏ lệch sáng.
Nền: dome sphere engine, material Lit Two-Sided màu phẳng Roughness 0.9 (KHÔNG scale âm — lật winding dễ vỡ lighting). Đáy dome = sàn nhận bóng THẬT — không shadow catcher (UE5 raster runtime không có shading model đó, và cove thật không cần). Sphere center Z = FloorZ + R.
Exposure: Manual EV100 cố định trên PostProcessSettings camera phụ — khả thi VÌ sáng studio là hằng số. Thay thế vĩnh viễn hướng Auto-exposure lock (fail ×2).
Vòng đời (R4): studio tĩnh (dome+đèn+sàn) dựng 1 lần BeginPlay BP_ComboManager, sống suốt session, dọn End Play. Clone: spawn đầu chuỗi → destroy + Clear ngay sau FinishComboCapture, kể cả fail path + End Play.
Guard: Cmb_bThumbBusy riêng (không tái dùng Cmb_bSpawnInFlight).

2. Biến mới (BP_ComboManager — prefix Cmb_ theo naming §9)
Cmb_StudioClones      : Array<BP_FurnitureActor>  (rỗng)
Cmb_bThumbBusy        : Bool (False)
Cmb_StudioAnchor      : Vector (500000, 500000, <FloorZ — hardcode Gate A, verify Z sàn phòng thật>)
Cmb_StudioFloor       : StaticMeshActor ref       (Gate A tạm — Gate B thay bằng dome)
Cmb_StudioDome        : StaticMeshActor ref       (Gate B)
Cmb_StudioKeyLight    : Actor ref                 (Gate C)
Cmb_StudioFillLight   : Actor ref                 (Gate C)
Cmb_PendingUserCamYaw : Float                     (Gate F — chốt lúc bấm Save, TRƯỚC dialog mở)
3. GATE A — vertical slice: clone sạch + chụp studio thô
Task card v1.1 (thay card v1.0 giao trong chat 16/07 — 2 delta: +DeltaYaw param default 0 chưa dùng, +ground-align; test 3 đổi theo).
Bài học L trích cho task
L1 IsValid mọi object access · L8 latent chỉ trong Custom Event · Loop chạy-1-lần nối Completed · KP3 không đụng SpawnComboByID · BP_FurnitureActor.BeginPlay TỰ ADD tag → strip SAU spawn từng clone · Impure call → SET local trước dùng.
Nodes chờ xác nhận (ghi AI_Implementation_Rules trước khi dùng)
Array Remove Item (trên GET Tags by-ref, KHÔNG SET Tags lại — EMS track qua Tags) · Get Actor Bounds · Add Actor World Offset · Rotate Vector Around Axis (Gate C).
Việc 1 — SpawnFurnitureCopy +param bAddToRecent : Bool = True
Bọc đúng khối Add Recent Mesh bằng Branch(bAddToRecent); False merge thẳng node kế (không dead-end). Không đụng gì khác. Test V1: drag-drop + duplicate thường → Recent vẫn cập nhật.
Việc 2 — Biến (§2) + sàn tạm
BeginPlay (sau init hiện có): Spawn StaticMeshActor tại Cmb_StudioAnchor, mesh /Engine/BasicShapes/Plane, scale (50,50,1) → SET Cmb_StudioFloor.
Việc 3 — Custom Event SpawnComboForThumbnail(ComboID : String, DeltaYaw : Float = 0)
Q8: Custom Event (L8 ✓) | IsValid từng điểm ✓ | L2 mọi nhánh merge/guard-đầu hợp lệ ✓ | Latent trong Event ✓ | 6A: destroy clones ở Finish + End Play ✓
▶→ Branch(Cmb_bThumbBusy) True → Print "Thumb busy" [bDebugMode] → HẾT (guard đầu event)
   False ▶→ SET Cmb_bThumbBusy = True
▶→ F_LoadComboData(ComboID) ●→ OutData, bSuccess
▶→ Branch(bSuccess) False → SET Cmb_bThumbBusy = False → HẾT
   True ▶→ Break ComboData ●→ Items
▶→ ForEach(Items) LoopBody:
     Get Data Table Row(DT_FurnitureCatalog, Item.RowName) — Row Found:
       SpawnFurnitureCopy(
         MeshPath = MeshFolderPath + "/" + RowName + "." + RowName  ← Concat y hệt SpawnComboByID
         SpawnLocation = Cmb_StudioAnchor + Item.RelLocation        ← Gate C thay bằng bản xoay DeltaYaw
         SpawnRotation = Item.RelRotation · SpawnScale = Item.Scale
         MaterialOverrides = Item.MaterialOverrides · SurfaceType = Item.SurfaceType
         bAutoSelect = FALSE · bAddToRecent = FALSE) ●→ NewActor
       Branch(IsValid(NewActor)) True:
         GET NewActor.Tags → Array Remove Item("FurnitureSpawned")   ← by-ref, không SET Tags
         SET NewActor.GroupID = ""
         Array Add(Cmb_StudioClones, NewActor)
   Completed ▶→ [caller nối tiếp — Việc 4]
DeltaYaw Gate A = 0, chưa nối vào toán — chỉ khai param để Gate C khỏi đổi signature.
Việc 4 — Chuỗi chụp debug (phím U, pattern phím T P1; Enable Input theo bDebugMode)
▶→ SpawnComboForThumbnail("<GUID combo test từ Saved/Combos>", 0)   [nối từ Completed Việc 3]
▶→ Delay(0.5)                                  ← chờ LoadMeshAsync (asset resident, resolve nhanh)
▶→ Get Actor Bounds gộp cả Cmb_StudioClones ●→ Origin, Extent
   → Print "Bounds=" + Extent [bDebugMode]     ← test M1-residual
   → DeltaZ = Cmb_StudioAnchor.Z − (Origin.Z − Extent.Z)
   → ForEach(Cmb_StudioClones) → Add Actor World Offset(0,0,DeltaZ) — Completed ▶→   ← GROUND-ALIGN (H1)
▶→ BeginComboCapture(ComboActors=Cmb_StudioClones, ExtraHidden=rỗng, 1024, FitRatio=0.85) ●→ SET Cmb_CaptureHandle
▶→ Delay(3.0)
▶→ FinishComboCapture(Cmb_CaptureHandle, "<GUID>_studio", Cmb_StudioClones) ●→ Print
▶→ ForEach(Cmb_StudioClones) → Destroy Actor — Completed → Array Clear(Cmb_StudioClones)
▶→ SET Cmb_CaptureHandle = None → SET Cmb_bThumbBusy = False
Suffix _studio → PNG mới nằm cạnh PNG cũ, so trước/sau bằng mắt.
Việc 5 — End Play nối thêm (M7)
ForEach Cmb_StudioClones → IsValid → Destroy — Completed → Clear; IsValid(Cmb_StudioFloor) → Destroy. Chuỗi dọn Cmb_CaptureHandle P1 giữ nguyên.
TEST Gate A (báo bảng)

Phím U → <GUID>_studio.png: ĐỦ đồ, KHÔNG chữ đỏ, KHÔNG bếp/tường/kệ
Print Bounds ×3 lần chụp → 3 số trùng (lệch → STOP, thêm dispatcher OnMeshLoaded vào BP_FurnitureActor)
Ground-align: đáy cụm chạm sàn plane; thử thêm 1 combo TRẦN nếu có → không chôn dưới sàn
Ctrl+Z không bước lạ · Recent không đồ mới · EMS Save→Load → không đồ ma ở studio
U ×2 trong 3s → lần 2 "Thumb busy", không chồng clone
Đang Edit Mode group → U → group KHÔNG dính clone
Tắt PIE giữa Delay → mở lại → Outliner sạch
Fail ×3 cùng chỗ → STOP leo thang Fable.

### Kết quả TEST Gate A — 17/07/2026
| # | Case | Kết quả |
|---|---|---|
| 1 | Đủ đồ, không chữ đỏ, không dính đồ thật | ✅ PASS |
| 2 | Print Bounds ×3 trùng | ✅ PASS |
| 3 | Ground-align chạm sàn | ✅ PASS |
| 4 | Undo/Recent/EMS sạch | ✅ PASS |
| 5 | Double-U trong 3s → "Thumb busy" | ✅ PASS |
| 6 | Edit Mode group không dính clone | ✅ PASS |
| 7 | Tắt PIE giữa Delay | ⏳ Dời Gate F |

**Gate A: DONE.** Sang Gate B.

4. GATE B — dome

Spawn 1 lần BeginPlay (thay plane Gate A — bỏ Việc 2 plane, giữ ref dome): sphere engine /Engine/BasicShapes/Sphere, R cố định bao combo to nhất (ước lượng từ BoundingBoxExtent lớn nhất trong library ×~5, hardcode + [VERIFY] bằng mắt), center Z = FloorZ + R (đáy trong = sàn).
Material: cuhoang tạo tay trong editor M_StudioBackdrop — Lit, Two-Sided (không scale âm), BaseColor = param, Roughness 0.9. 3 tông chụp thử: #F5F5F5 / #EAE8E4 / #E8EDF2 → cuhoang duyệt S1 bằng ảnh thật tại gate này.
Verify: không horizon line mọi hướng chụp · không faceting sphere lộ (lộ → Plan B: custom cove mesh nhờ đồng nghiệp DCC ~30') · PP volume phòng thật không rò màu (rò → xử ở Gate C cùng PostProcessSettings).

### Kết quả Gate B — 17/07/2026
**DONE.** R hardcode = `Cmb_StudioDomeRadius` = 2000.0 (biến, không phải literal ước lượng ×~5 như plan). **[ARCH] Cast Shadow=False trên dome** — quyết định quan trọng nhất gate này: dome đặc chặn hoàn toàn ánh sáng nếu đèn đứng ngoài bán kính R, tắt Cast Shadow biến dome thành "chỉ nhận bóng, không chặn sáng" (đúng bản chất backdrop vải/giấy thật). Receive Shadow giữ nguyên. Màu dome S1 (3 tông #F5F5F5/#EAE8E4/#E8EDF2) **CHƯA chốt** — dời sang đợt "tối ưu cuối" (gộp cùng sofa/mesh/màu), quyết định cuhoang vì lúc Gate B chưa có đèn để soi màu đúng. Faceting/horizon line sphere — quan sát ban đầu nghi có vấn đề nhưng chưa xác nhận (chưa test Wireframe), dời cùng đợt tối ưu cuối. Chi tiết: `DEVIATIONS.md` mục "P2 — 17/07/2026 (cuối phiên)".

5. GATE C — đèn + Manual EV100 + camera H-B (gate nặng nhất)
[VERIFY] trước khi làm — 2 điểm quyết có đụng C++ không:

V-C1: thân .cpp của Begin có implement bUseFixedAngle/FixedAngle thật chưa (doc ghi "chuẩn bị, chưa dùng")? Stub → viết thân (C++).
V-C2: BP set được PostProcessSettings (ExposureMethod=Manual, EV100, DOF) qua handle GetCaptureComponent2D không? Không → thêm param vào Begin (C++, .h chạm lần 3 — ghi DEVIATIONS như tiền lệ 14/07).
Đèn: 2 RectLight spawn/hoặc đặt sẵn cạnh dome theo 45/45 quanh trục camera cố định; Key intensity tune tại chỗ, Fill = 1/3; source size 1–2m.
Camera H-B: bUseFixedAngle=True, FixedAngle=(Pitch −15, Yaw = StudioCamYaw hằng); toán xoay clone trong SpawnComboForThumbnail dùng DeltaYaw thật: RotatedRel = Rotate Vector Around Axis(Item.RelLocation, DeltaYaw, Z-up) + RelRotation.Yaw += DeltaYaw (xoay CẢ FORMATION quanh anchor, không phải từng món tự quay tại chỗ). Debug phím U: DeltaYaw = StudioCamYaw − yaw camera hiện tại.
EV100: tune 1 lần với tông màu S1 đã chốt.
Verify — exposure bug CHẾT: chụp lại đúng 4 combo cũ (gồm case ngược sáng) → 4 ảnh cùng độ sáng; combo user xoay 180° trong phòng → ảnh vẫn ra mặt user đang nhìn. Plan B: dome kín tối hơn kỳ vọng → tăng Fill/thêm top light + bù EV — tune, không đổi kiến trúc.

### Kết quả Gate C — 17/07/2026
**DONE.** V-C1: `bUseFixedAngle`/`FixedAngle` đã implement sẵn trong .cpp (không cần đụng C++) — bug thật là node `Begin Combo Capture` trong chuỗi debug U chưa từng tick `Use Fixed Angle=True` (bỏ sót giữa các lượt làm), không phải thiếu thân hàm. V-C2: BP set được PostProcessSettings qua `Get/Set members in Post Process Settings` (đọc struct hiện có từ Capture Component, sửa tại chỗ) — KHÔNG cần thêm param C++ mới, nhưng phải dùng đúng node "Set members in Struct", không phải `Make Post Process Settings` (Make tạo struct mới, xoá mất 2 field Lumen override C++ đã set — bug #11 xem DEVIATIONS).

Function mới `SpawnStudioLight(AngleOffsetDeg, Intensity) → RectLight` thay 2 khối node lặp Key/Fill: `RotateAngleAxis((1500,0,1500), AngleOffsetDeg, Z-up)` → LightOffset, WorldLoc = `Cmb_StudioAnchor + LightOffset`, Mobility=Movable (bắt buộc — Stationary phụ thuộc Lightmass bake, Remote Studio runtime chưa bake), FindLookAtRotation về anchor, Source Width/Height=150, Attenuation Radius=8000 (4000 mặc định hụt tầm với Distance~1920). Gọi: `SpawnStudioLight(45.0, 5000000.0)` → Cmb_StudioKeyLight, `SpawnStudioLight(-45.0, 1666667.0)` → Cmb_StudioFillLight (ratio 3:1 đúng plan).

12 bug/quyết định trong lúc làm gate này (lịch sử đầy đủ: `DEVIATIONS.md` mục "P2 — 17/07/2026 (cuối phiên)") — đáng chú ý: `Cmb_StudioAnchor` Default Value từng là (0,0,0) thay vì (500000,500000,Z) như plan gốc định (biến khai đúng nhưng số thật chưa gõ); 5 vòng đoán sai liên tiếp quanh vị trí đèn trước khi leo thang Fable, Fable chỉ ra Cast Shadow=False (Gate B) là root cause thật; thêm `IsValid(Cmb_CaptureHandle)` guard sau Begin (thiếu → kẹt "Thumb busy" vĩnh viễn nếu Begin fail).

Verify PASS: bấm U với 2 Combo ID khác nhau (sofa trắng, bàn trang điểm gỗ tối) → cùng góc camera, cùng mức sáng nền.

6. GATE D — bóng + sweep hình dáng
Source Size Key tune bóng mềm khớp ảnh IKEA. Sweep: combo nhỏ (1 ghế) / to (sofa L+bàn) / dẹt (thảm) / cao (kệ) / tường (known-limitation H1: ground-align đặt đồ tường xuống sàn — duyệt chấp nhận được hay cần xử riêng, quyết tại đây). Combo nhỏ lệch sáng → nâng cấp vị trí đèn scale theo R_bao (công thức Center + Dir×m×R_bao).
7. GATE E — DOF
FocalDistance = Distance auto-fit (số có sẵn trong Begin), aperture f/2.8–f/4, cuhoang duyệt mức mờ bằng mắt. DOF ăn không đều trong capture → giảm aperture hoặc bỏ (S5 nice-to-have, không chặn F).
8. GATE F — nối dây thật + closure

SaveComboFromSelection Bước 7: THAY chuỗi capture in-place P1 (chụp actor thật) bằng SpawnComboForThumbnail(GUID thật, DeltaYaw từ Cmb_PendingUserCamYaw) → chuỗi chụp → Broadcast OnComboLibraryChanged giữ nguyên vị trí (sau Finish; capture fail vẫn broadcast — thiết kế P1).
Cmb_PendingUserCamYaw SET tại handler BẤM Save (trước dialog mở — user xoay camera trong lúc gõ tên).
Bỏ suffix _studio; ComboID thật; save đè (C9 sau này) nhớ InvalidateThumbnail.
Guard giao Save: bấm Save 2 combo liên tiếp < 4s → quyết queue hay chờ tại đây theo UX thật (debug skip là đủ, Save thật thì không được mất ảnh). Độ trễ tổng ~4s khó chịu → chen K1 WBP_Toast trước khi đóng F ("Đang tạo ảnh…").
Xóa chuỗi debug phím U + Enable Input.
Verify end-to-end: 6 case kiểu P1.G4 (save → card ảnh mới ngay · combo cũ 🧩 êm · cache ăn · restart PIE OK) + undo/EMS/Recent sạch lần cuối + stat rhi 4 mốc kiểu G5 (dome+đèn thường trú: kỳ vọng baseline nhích cố định 1 lần, KHÔNG tăng theo số lần chụp).

9. Điểm treo chờ quyết (Decide-When-Reached)
MụcQuyết tạiS1 tông màu (3 ứng viên)Gate B, ảnh thậtEV100 value + intensity đènGate CCombo tường: chấp nhận ground-align hay xử riêngGate DMức DOF / bỏ DOFGate EQueue vs chờ khi Save dồn dập · chen K1 trước FGate F
10. Sau P2
K1 (nếu chưa chen ở F) → K3 còn lại (hạ tầng param từ A.Việc-1 đã sẵn) → C9 → C6 → C7 → C11 → C10 → Gate 2.
