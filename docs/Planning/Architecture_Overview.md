# Architecture — Nguyên tắc kiến trúc code
**Phiên bản:** 1.4 | **Dự án:** Lighting_Mnger | **Cập nhật:** 11/09/2026 (G5.4) — thêm bài học chốt "side-effect phụ thuộc async phải đặt ở Engine, không đặt ở Router" (từ bug #4+#5, GATE G5 ĐÓNG HẲN). Nguồn: `11-09-2026_S7G5_G5.4_AsBuilt_Addendum.md`

**Phiên bản:** 1.3 | **Dự án:** Lighting_Mnger | **Cập nhật:** 11/09/2026 — đính chính doc debt: `FurnitureInventoryRef`/`ToastRef` đích thật là `BP_FurnitureSceneManager`, không phải `Foff_GameInstance` (K2Node export S7.G5). Thêm mục "Pattern 3 lớp tách bạch — kéo-thả material" + `BP_DragDropOperation_Material`. Nguồn: `11-09-2026_S7G5_G5.1-G5.3_AsBuilt_Delta.md`

**Phiên bản:** 1.2 | **Dự án:** Lighting_Mnger | **Cập nhật:** 23/07/2026 — thêm `ToastRef` vào Shared Code Foff_GameInstance (K1, WBP_Toast)

---

## Nguyên tắc cốt lõi

> **Mỗi tính năng = 1 Actor Blueprint riêng biệt.**
> Không nhồi logic vào shared code. Chỉ truyền reference khi cần tích hợp.

---

## Actors riêng biệt

| Actor | Nhiệm vụ |
|---|---|
| BP_FurnitureInputManager | Mouse input, select/deselect, DeselectMesh, variables furniture |
| BP_GizmoController | Ray-plane intersection, snap, rotation delta |
| BP_UndoManager | CaptureSnapshot, RestoreSnapshot, history |
| BP_FurnitureSceneManager | EMS Save/Load, bind SaveGameMenu |
| BP_TransformerPawn | Hiển thị gizmo visual, hover highlight |
| BP_FurnitureActor | Lưu MeshPath, DAPath, implement EMS interface |

---

## Shared Code — Chỉ thêm, không sửa cấu trúc

- `BP_FoffPlayerController` — **KHÔNG thêm variables furniture nữa**, đã chuyển sang BP_FurnitureInputManager
- ⚠️ **[ĐÍNH CHÍNH 11/09/2026]** `FurnitureInventoryRef` VÀ `ToastRef` — dòng cũ ghi 2 field này nằm
  trên `Foff_GameInstance`. XÁC NHẬN LẠI qua K2Node export thật (S7.G2 VERIFY #5, 27/08/2026 +
  S7.G5.1-G5.3, 11/09/2026): đích thật hiện tại là **`BP_FurnitureSceneManager`**, KHÔNG phải
  `Foff_GameInstance`. Chỉ báo cáo trạng thái ĐÍCH thật hiện tại — KHÔNG rõ ngày chuyển (refactor
  nào đó ngoài phạm vi các phiên đã soi), không suy đoán lịch sử. Mọi truy cập MỚI từ nay dùng
  `GetAllActorsOfClass(BP_FurnitureSceneManager)` cho 2 field này, không `Get Game Instance → Cast
  Foff_GameInstance`.
- **Báo đồng nghiệp** khi thêm variable vào shared code

---

## Pattern 3 lớp tách bạch — kéo-thả material (Opus chốt 08/09/2026, xác nhận qua thực thi 11/09/2026)

- `WBP_MaterialCard.OnDragDetected` = NGUỒN (đóng gói RowName vào `BP_DragDropOperation_Material`).
  Không biết apply.
- `WBP_DragOverlay.On Drop` (nhánh material) = ROUTER (trace slot + lọc loại actor + gọi engine).
  Không biết load/apply/refresh UI.
- `BP_FurnitureActor.ApplyMaterialByRowName` = ENGINE (DT lookup → async load → apply → capture →
  refresh UI nếu actor đang mở panel). Đây là nơi DUY NHẤT biết chính xác thời điểm async xong —
  mọi hệ quả phụ thuộc thời điểm apply thật (refresh swatch, tương lai: hiệu ứng particle/sound
  khi đổi material...) PHẢI đặt ở lớp này, không đặt ở Router.

**Class mới `BP_DragDropOperation_Material`** — em út của bộ 3 `DragDropOperation` con
(`BP_DragDropOperation_FurnitureCard`, `BP_DragDropOperation_ComboCard`, giờ thêm class này). Cùng
pattern: 1 field payload chính (RowName/ComboID), tạo trong `OnDragDetected` của card nguồn tương
ứng. Xem `Widgets/WBP_MaterialCard.md`.

**Tiền lệ on-actor engine cho async material** — `ApplyMaterialByRowName` nối dài danh sách Custom
Event đặt trên `BP_FurnitureActor` xử lý material async của chính actor đó
(`RestoreMyMaterialSlots` là tiền lệ đầu tiên, Sprint 7 G3). Lý do kiến trúc không đổi: actor tự lo
asset của mình, tránh aliasing khi Manager/Widget dùng chung class var cho nhiều target đồng thời.

`WBP_DragOverlay` giờ route 3 loại `DragDropOperation` (Furniture / Combo / Material) qua cùng 1
`On Drop`, phân biệt bằng chuỗi `Cast To` tuần tự — không dựng overlay riêng cho material (KISS).

**Bài học chốt (11/09/2026, từ 2 bug thật cùng gốc — bug #4 refresh swatch + bug #5 AddRecentMaterial,
xem `DEVIATIONS.md` mục SPRINT 7 11/09/2026):** mọi hệ quả phụ thuộc thời điểm apply thật xong
(refresh UI, ghi Recent, hiệu ứng tương lai như particle/sound...) PHẢI đặt trong
`ApplyMaterialByRowName` (Engine), KHÔNG đặt ở `On Drop` (Router). Cả 2 bug đều do đặt side-effect
phụ thuộc async SAI LỚP — Router gọi Engine (chứa `Async Load Asset`) rồi làm tiếp ngay, không đợi
async xong. Áp dụng cho mọi tính năng tương lai theo cùng pattern 3 lớp này (vd G6 nếu có thao tác
async nào tương tự).

---

## Level Blueprint

Chỉ làm ở đây:
1. Spawn các Actor Manager
2. Set references vào PC
3. CaptureSnapshot("Initial") — phải cuối cùng

---

## BP_FurnitureActor

- Parent: **StaticMeshActor** (không phải Actor) — EMS cần kế thừa StaticMeshActor
- Interface: **EMSActorSaveInterface**
- Variables tick SaveGame: MeshPath, DAPath, **MaterialOverrides** (v1.1), **MaterialParams** (v1.1 placeholder)
- Tags: KHÔNG dùng SET Tags trực tiếp — GET → ADD → SET TempTags → SET Tags

---

## Widget Architecture

- **WBP_FurnitureInventory** → lấy reference qua `Foff_GameInstance.FurnitureInventoryRef`
- **WBP_MeshControls** → lấy reference qua `Get Player Controller → Cast BP_FoffPlayerController`
- Không hardcode reference, không dùng Get All Widgets of Class trong OnListItemObjectSet
- **WBP_MaterialCard / WBP_SlotSwatch** → Event Destruct bắt buộc clear hard refs (v1.1). Thêm
  `WBP_MaterialCard.DragOverlayRef` (S7.G5.1, 11/09/2026) vào danh sách, cùng nhóm
  `WBP_FurnitureCard.DragOverlayRef`/`WBP_ComboCard.DragOverlayRef` đã có từ trước.

---

## Roadmap Refactor (Phase B — sau v1.1)

Hạn chế kiến trúc hiện tại cần xử lý:
- Hard refs khắp nơi (TargetFurnitureActor, SpawnedActors...)
- Load Asset Blocking nhiều → freeze khi file nặng/cloud
- DA_FurnitureItem là editor-time asset (không tạo runtime)
- Get All Actors Of Class tìm singleton chậm
- Không có event bus
- EMS local-only
- Không có async pipeline

Phase B target:
- **AssetService** (C++ Subsystem) — quản lý asset load async
- **Event Bus** — thay Get All Actors Of Class
- **SceneService** — tách scene management khỏi UndoManager
- **Command pattern Undo** — thay snapshot toàn scene
- Xóa hard refs khỏi Widget

---

## TransformerPawn

- **KHÔNG Possess** — gây mất camera
- Chỉ dùng để: SelectActor, SetTransformationType, hiển thị gizmo visual
- Movement logic tự xử lý trong BP_GizmoController

---

## Spawn Order (Level Blueprint BeginPlay)

```
1. BP_UndoManager
2. BP_FurnitureSceneManager
3. BP_TransformerPawn
4. BP_GizmoController
5. BP_FurnitureInputManager → Cast → SET GizmoControllerRef
6. WBP_MeshControls → Add to Viewport → Cast BP_FurnitureInputManager → SET CurrentMeshControls
7. CaptureSnapshot("Initial")  ← CUỐI CÙNG
```

---

## EMS Integration

- Dùng chung slot với project tổng → Get Current Save Slot trước khi Save/Load
- EMS tự respawn BP_FurnitureActor khi load — không spawn thủ công
- KHÔNG gọi LoadFurnitureScene trong BeginPlay — EMS tự load

---

## Runtime-Friendly Principles (thêm từ 09/05/2026)

> Mục tiêu xa: user import asset từ máy cá nhân lên server lúc runtime.
> 5 nguyên tắc dưới đây cần áp dụng từ bây giờ để codebase dễ nâng cấp sau.

### Quy tắc R1 — Không thêm Load Asset Blocking mới
Mỗi lần dùng `Load Asset Blocking` = game **đứng chờ** cho đến khi file load xong.
Với file nhỏ trong ổ cứng: không thấy. Với file trên server hoặc file nặng: **freeze 3-5 giây**.

- ✅ Dùng **Async Load Asset** + callback cho mọi asset load mới
- ✅ Chỗ đã có `Load Asset Blocking` → ghi comment `# TODO: migrate async`
- ❌ Không thêm `Load Asset Blocking` mới từ v1.1 trở đi

### Quy tắc R2 — Widget không giữ hard ref đến Actor/Component
Widget giữ hard ref = nắm tay Actor không buông → Actor bị destroy nhưng RAM/VRAM không giải phóng.

- ✅ Widget chỉ giữ **Soft Object Reference** hoặc **RowName/ID** (String/Integer)
- ✅ Khi cần dùng Actor: **Resolve** Soft Ref → dùng → không lưu lại
- ✅ Nếu bắt buộc hard ref (TargetFurnitureActor...) → **SET None ở Event Destruct**
- ❌ Không khai báo variable kiểu `BP_FurnitureActor (Object Reference)` trong Widget nếu không có Event Destruct clear

### Quy tắc R3 — Widget nhận struct data, không nhận object nặng
Widget chỉ cần biết "tên gì, ảnh gì, ID là gì" — không cần ôm cả object.

- ✅ Widget nhận **struct** (RowName, DisplayName, ThumbnailMI) làm input
- ✅ Parent widget lo việc query data, truyền struct xuống cho child
- ❌ Không truyền cả DataTable row object hoặc Actor reference vào widget con

### Quy tắc R4 — Event Destruct dọn sạch mọi reference
Mọi Widget có biến Object Reference đến Actor/Component/Material/Texture/Widget khác:

- ✅ **Event Destruct** → SET tất cả về None
- ✅ Áp dụng ngay khi tạo widget mới, không để sau

### Quy tắc R5 — Lưu AssetID, không lưu path
Asset path (`/Game/cuong/...`) sẽ thay đổi khi chuyển sang cloud. AssetID (RowName trong DataTable) thì không.

- ✅ Khi save material override, undo snapshot... → lưu **RowName** từ DT_MaterialInstancesCatalog
- ✅ Khi load: dùng RowName → Get Data Table Row → lấy path từ đó
- ❌ Không hardcode full asset path `/Game/...` vào save data
