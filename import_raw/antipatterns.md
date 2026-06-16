# Antipatterns — Những gì KHÔNG được làm
**Phiên bản:** 1.1 | **Dự án:** Lighting_Mnger | **Cập nhật:** 20/05/2026 — 16:00 ICT

---

## Blueprint

| ❌ Không làm | ✅ Thay bằng |
|---|---|
| Loop lớn trong Blueprint | C++ UFurnitureFilterLibrary |
| WrapBox cho danh sách lớn | Tile View / List View (virtualized) |
| Get All Widgets of Class trong OnListItemObjectSet | Foff_GameInstance.FurnitureInventoryRef |
| Thêm variables furniture vào BP_FoffPlayerController | Dùng BP_FurnitureInputManager thay thế |
| Cast To BP_FoffPlayerController để lấy furniture variables | Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast |
| Gọi CaptureSnapshot trong DeselectMesh | Gọi từ Mouse Left Pressed sau DeselectMesh |
| Xẻ/tách code cũ khi thêm tính năng | Thêm vào pin node có sẵn |
| SET Tags trực tiếp sau GET→ADD | GET → ADD → SET TempTags → SET Tags |

---

## Thứ tự sai gây bug

| ❌ Sai | ✅ Đúng |
|---|---|
| CaptureSnapshot trước Add Tag | Add Tag → CaptureSnapshot("Spawn") |
| CaptureSnapshot trước Destroy Actor | Destroy Actor → CaptureSnapshot("Delete") |
| CaptureSnapshot trước DeselectMesh | DeselectMesh → CaptureSnapshot("Deselect") |
| SET bIsDraggingGizmo=False trước CaptureSnapshot | CaptureSnapshot → SET bIsDraggingGizmo=False |
| CaptureSnapshot("Initial") không phải cuối BeginPlay | Phải là node cuối cùng |
| GET CurrentIndex riêng cho RestoreSnapshot | Dùng output pin của SET CurrentIndex |

---

## Gizmo

| ❌ Không làm | ✅ Thay bằng |
|---|---|
| Hardcode TransformType=Translation | Truyền TransformType qua param |
| Bỏ prefix actor name từ Display Name | Split (From End, ".") → Right S |
| Không SET PreviousMousePosition trong OnMousePressed | SET trong OnMousePressed — tránh delta khổng lồ frame đầu |
| Không reset AccumulatedRotation khi thả chuột | SET = 0 trong OnMouseReleased |

---

## EMS Save/Load

| ❌ Không làm | ✅ Thay bằng |
|---|---|
| BP_FurnitureActor kế thừa Actor | Kế thừa StaticMeshActor |
| Gọi LoadFurnitureScene trong BeginPlay | EMS tự load |
| Không destroy FurnitureSpawned trước EMS load | Destroy trong OnLoadButtonClicked |
| Bind SaveGameMenu 1 lần | Event Tick check widget mới → rebind |

---

## Performance

| ❌ Không làm | Lý do |
|---|---|
| Load tất cả asset (không Soft Reference) | Tốn RAM, lag khi mở |
| Add 10k+ item vào Tile View cùng lúc | Lag UI |
| Get Actor Bounds runtime mỗi lần | Tốn CPU tick — pre-bake vào DA_ thay thế |
| Loop Blueprint qua dataset lớn | Hit execution limit |

---

## Runtime-Friendly (thêm từ 09/05/2026)

| ❌ Không làm | ✅ Thay bằng | Lý do |
|---|---|---|
| Thêm `Load Asset Blocking` mới | `Async Load Asset` + callback | Blocking = game freeze khi file nặng hoặc trên server |
| Widget giữ hard ref Actor/Component không có Event Destruct | Soft Object Reference + SET None ở Event Destruct | Hard ref giữ VRAM không giải phóng |
| Truyền cả DataTable row object vào widget con | Truyền struct nhẹ (RowName, DisplayName, ThumbnailMI) | Widget không cần biết nguồn data |
| Lưu full asset path `/Game/...` vào save data | Lưu RowName (AssetID) từ DataTable | Path thay đổi khi chuyển cloud, ID thì không |
| Widget con tự query DataTable/Actor | Parent query → truyền struct xuống | Tách data khỏi display, dễ test và refactor |

---

## Các lỗi hay gặp

- **SelectedFurnitureActor = None sau Delete** → SET = None ngay sau Destroy Actor
- **Mesh di chuyển thay vì xoay** → ActiveAxis trùng tên, cần branch theo ActiveMode trước Switch
- **Gizmo không hiện lần đầu BTN_Rotate** → bGizmoActive=True từ mode cũ, cần DeactivateGizmo trước ActivateGizmo
- **Delta khổng lồ frame đầu drag** → SET PreviousMousePosition trong OnMousePressed
- **Collision bị disable khi drag** → DeactivateGizmo trong On Drag Detected, không chờ On Drop

---

## Material v1.1 — Antipatterns mới

| ❌ Không làm | ✅ Thay bằng | Lý do |
|---|---|---|
| `SpawnedActors[class var SelectedMeshIndex]` trong Broadcast | `RestoredBPActor` (set từ Cast output) | Class var = last CaptureSnapshot, sai snapshot |
| SwitchInventoryMode False branch không gọi FilterBySearch | Thêm `FilterBySearch` cuối False branch | Furniture card trống khi switch về |
| Branch dead-end không merge | Tất cả nhánh merge về cuối | Logic sau branch không chạy |
| ForEach/ForLoop không IsValid check Object | IsValid check trước mọi Object access | Accessed None crash |
| Async Load trong Function | Custom Event (async/latent node) | Latent node không dùng được trong Function |
| Set Background Color trên Button (Tint A=0) | Image overlay + Set Color and Opacity | Set Background Color không work khi Tint A=0 |
| Duplicate branch để broadcast | Single broadcast point với class var temp | Hai nguồn đọc index → race condition |
