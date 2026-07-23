# Architecture — Nguyên tắc kiến trúc code
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
- `Foff_GameInstance` — chỉ thêm `FurnitureInventoryRef`, `ToastRef` (WBP_Toast, K1 23/07/2026 — global toast access), không thay đổi gì khác
- **Báo đồng nghiệp** khi thêm variable vào shared code

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
- **WBP_MaterialCard / WBP_SlotSwatch** → Event Destruct bắt buộc clear hard refs (v1.1)

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
