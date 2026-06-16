# Tài liệu Hệ thống — UE5 Interior Design Tool
**Phiên bản:** 3.1 | **Cập nhật:** 20/05/2026 — 16:00 ICT | **Project:** Lighting_Mnger (UE5.5.4)

---

## MỤC LỤC
1. [Tổng quan hệ thống](#1-tổng-quan)
2. [Kiến trúc code](#2-kiến-trúc-code)
3. [Layout UI](#4-layout-ui)
4. [Kế hoạch phát triển](#5-kế-hoạch)
5. [Key Learnings](#6-key-learnings)

**Chi tiết Blueprint:** Xem thư mục Blueprints/
**Inventory:** Xem WBP_FurnitureInventory.md

---

## 1. TỔNG QUAN

- Công cụ thiết kế nội thất Runtime UE5
- Duyệt kho 100k-200k sản phẩm, kéo thả, select, move, rotate, scale, undo/redo, save/load
- Engine: UE5.5.4 | IDE: Visual Studio 2022 | Plugin: RuntimeTransformer (UE4 port, đã fix UE5)

---

## 2. KIẾN TRÚC CODE

```
LEVEL BLUEPRINT BeginPlay:
  Spawn BP_UndoManager
  Spawn BP_FurnitureSceneManager
  Spawn BP_TransformerPawn → SET TransformerPawnRef (PC)
  Spawn BP_GizmoController → Cast PC → SET GizmoControllerRef
  Create WBP_MeshControls → Add to Viewport → Cast PC → SET CurrentMeshControls
  Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Initial")
  ← CaptureSnapshot("Initial") PHẢI đặt cuối cùng sau tất cả spawn/create widget
  ← KHÔNG gọi LoadFurnitureScene trong BeginPlay — EMS tự load khi game start

BP_FoffPlayerController (shared):
  ⚠️ Toàn bộ furniture variables và events đã chuyển sang BP_FurnitureInputManager
  Không thêm furniture variables vào đây nữa

BP_FurnitureInputManager (Actor riêng — thay thế BP_FoffPlayerController cho furniture):
  Variables:
    SelectedFurnitureActor : BP_FurnitureActor
    CurrentMeshControls    : WBP_MeshControls
    GizmoControllerRef     : BP_GizmoController
    TransformerPawnRef     : BP_TransformerPawn
    ActiveMode             : E_ActiveMode
    LocalWasGizmoActive    : Boolean
  Events: Mouse Left Pressed, Mouse Left Released, DeselectMesh, Event End Play
  Cách lấy reference: Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast

Foff_GameInstance (shared):
  Variable thêm: FurnitureInventoryRef (WBP_FurnitureInventory)
```

### Data Structures
```
DA_FurnitureItem (PrimaryDataAsset):
  VieName, EngName, Category, Thumbnail(Soft), Mesh(Soft)
  MeshFolderPath, Description, Link, Tags(pipe-separated)

S_FurniturePlacement:
  MeshPath, DAPath, Location, Rotation, Scale, ActorTag, UniqueID(String)
  MaterialPaths : Array of String   ← v1.1: capture MaterialOverrides cho Undo/Redo

S_SceneSnapshot:
  ActionName, Meshes(Array S_FurniturePlacement), SelectedMeshIndex, ActiveMode(E_ActiveMode)

S_MaterialInstancesData (DataTable Row — DT_MaterialInstancesCatalog):  ← v1.1
  VieName, EngName, Style, Size
  MaterialFolderPath : String   ← Python populate từ Asset Registry
  MaterialPath       : String   ← full package path MI
  ThumbnailPath      : String   ← Texture2D pre-baked
  ThumbnailMI        : Soft Object Reference Texture2D   ← lazy load swatch

E_ActiveMode: Select | Move | Rotate | Scale
E_InventoryMode: Furniture | Material   ← v1.1
```

---


---

## 4. LAYOUT UI

### WBP_FurnitureInventory (720x630) — v1.1
```
Canvas Panel
├── HB_TitleBar → BTN_Minimize, BTN_Maximize, BTN_Close
├── BackgroundBlur → VerticalBox
│   ├── HB_TabBar (v1.1) → BTN_Tab_Furniture | BTN_Tab_Material
│   └── HB_MainContent
│       ├── ScrollBox cột trái → VerticalBox_44 (WBP_TreeNode)
│       └── VerticalBox cột phải
│           ├── HB_SlotSwatches (v1.1, Collapsed mặc định)
│           │   ├── HB_SwatchList (WBP_SlotSwatch động)
│           │   ├── BTN_ResetSlot, BTN_ResetAll
│           ├── SearchBar + TB_Breadcrumb + VB_ChipTagArea
│           ├── CTV_FurnitureCard (Furniture mode)
│           └── CTV_MaterialCard  (Material mode, v1.1)
└── BTN_MinimizedIcon (Collapsed mặc định)
```

### WBP_MeshControls (Persistent Toolbar)
```
[↖Select] [✛Move] [↺Rotate] [⊡Scale] │ [🗑Delete] [ℹInfo]
          [── 10 ──]  ← ET_SnapStep (chỉ hiện khi Move mode)
```

### Selection Outline
```
- Custom Depth Stencil Pass = Enabled with Stencil
- Post Process Volume: Infinite Extent = True
- M_SelectionOutline: Domain=PostProcess, Blendable=Translucency After DOF
- Stencil Value = 255
```

---

## 4B. WBP_FURNITURE INVENTORY

---

## 5. KẾ HOẠCH PHÁT TRIỂN

### Phase 1 — Nền tảng
| Feature | Trạng thái |
|---------|-----------|
| Single click select + outline | ✅ Xong |
| BTN_Select + BTN_Move highlight | ✅ Xong |
| BTN_Move (7 trục + snap) | ✅ Xong |
| Switch mesh khi đang Move | ✅ Xong |
| Click vùng trống → Deselect | ✅ Xong |
| Undo (Alt+Z) | ✅ Xong |
| Redo (Shift+Alt+Z) | ✅ Xong |
| Save/Load (EMS) | ✅ Xong |
| BP_FurnitureActor | ✅ Xong |
| Drag & Drop spawn mesh | ✅ Xong |
| Ghost preview mesh khi drag | ✅ Xong |
| Snap to surface (sàn/tường/trần) | ✅ Xong |
| Surface rotation theo normal | ✅ Xong |
| Fix spawn khi gizmo active | ✅ Xong |
| Undo/Redo restore đúng mesh + mode | ✅ Xong |
| Deselect lưu snapshot đúng (-1) | ✅ Xong |
| Save/Load redesign | ✅ Xong |

### Phase 2 — Core features
| Feature | Trạng thái |
|---------|-----------|
| BTN_Rotate | ✅ Xong (cần polish gizmo visual) |
| BTN_Scale | ✅ Xong |
| Material Editor (Change Material v1.1) | ✅ Xong (20/05/2026) |
| Copy/Paste (Ctrl+C/V) | 🔲 Chưa làm |
| Delete key shortcut | 🔲 Chưa làm |
| Focus on selected (F) | 🔲 Chưa làm |

### Phase 3 — UX nâng cao
| Feature | Trạng thái |
|---------|-----------|
| Scene Outliner | 🔲 Chưa làm |
| Auto-save | 🔲 Chưa làm |

### Keyboard Shortcuts
| Phím | Chức năng |
|------|-----------|
| Q | Select mode |
| W | Move mode |
| E | Rotate mode |
| R | Scale mode |
| Delete | Xóa mesh |
| Alt+Z | Undo |
| Shift+Alt+Z | Redo |
| Ctrl+S | Save |
| Ctrl+O | Load |
| I | Mở/đóng Inventory |
| Esc | Deselect |

---

## 6. KEY LEARNINGS

### Deselect + CaptureSnapshot
- **DeselectMesh trước, CaptureSnapshot("Deselect") sau**
- **KHÔNG gọi CaptureSnapshot trong DeselectMesh** — gây infinite loop
- **CaptureSnapshot("Deselect")** chỉ gọi từ Mouse Left Pressed Step 5 và 6

### CaptureSnapshot — Flow nhánh tìm SelectedMeshIndex
- **SET SelectedMeshIndex = -1 ở đầu** trước mọi Branch
- **Tất cả nhánh False** nối vào `Branch(Length >= MaxSteps)` — không dừng

### Undo/Redo
- **UniqueID** = Get Display Name(Actor) → phân biệt mesh cùng MeshPath
- **RedoLastAction:** nối output pin của SET CurrentIndex vào IndexHistory
- **CaptureSnapshot("Initial")** gọi cuối Level Blueprint BeginPlay

### Thứ tự CaptureSnapshot so với action
- **Spawn:** Add Tag → CaptureSnapshot
- **Delete:** Destroy Actor → CaptureSnapshot
- **Deselect:** DeselectMesh → CaptureSnapshot

### Collision Management khi Gizmo Active
- **ActivateGizmo**: tắt collision NOT FurnitureSpawned + tắt BaseGizmo components
- **DeactivateGizmo**: restore tất cả — luôn chạy (cả True và False branch)

### Drag & Drop — Surface Snap
- **DeactivateGizmo trong On Drag Detected** — fix lỗi Line Trace không hit sàn khi đang Move mode
- **Floor/Ceiling:** Rotator 0,0,0 — giữ nguyên pivot mesh
- **Wall:** Make Rot from X(Normal) → Yaw - 90 — mesh đứng thẳng áp tường
- **bTraceComplex = True** → trace geometry thực, bắt được tường/trần không có collision box
- **ActorsToIgnore = [PreviewActorRef]** → tránh mesh ghost block trace chính nó
- **On Drop dùng PreviewActorRef** thay vì spawn mới
- **Move mode KHÔNG snap surface** — snap chỉ trong drag & drop ban đầu
- **Pivot mesh = điểm lắp đặt thực tế** → không cần offset bounds

### EMS Save/Load
- **BP_FurnitureActor** kế thừa StaticMeshActor
- **KHÔNG dùng SET Tags** sau GET→ADD — EMS dùng Tags để track state
- **MeshPath rỗng** → Destroy Actor trong ActorLoaded
- **SaveGameMenu rebind mỗi lần tạo mới** → dùng Event Tick check widget mới
- **DeselectMesh trước khi Destroy FurnitureSpawned** → OnLoadButtonClicked — nếu không, gizmo vẫn hiện sau Load vì bGizmoActive chưa được reset
- **Destroy FurnitureSpawned trước EMS load** → OnLoadButtonClicked
- **Set Input Mode Game And UI** đặt đầu Mouse Left Pressed

### Material Editor v1.1 (mới — 20/05/2026)
- **Get Static Mesh Component trả về rỗng** → Cast To BP_FurnitureActor → GET FurnitureMesh
- **Async Load**: String → MakeSoftObjectPath → ToSoftObjectReference → AsyncLoadAsset. Latent node không dùng trong Function → Custom Event
- **Broadcast OnRestoreCompleted**: KHÔNG dùng `SpawnedActors[class var SelectedMeshIndex]` — class var = last CaptureSnapshot, không phải snapshot đang restore. Dùng `RestoredBPActor` (set từ Cast output trong Branch gizmo) → single broadcast point, không bao giờ sai actor
- **SwitchInventoryMode False branch** phải gọi `FilterBySearch(CurrentSearchText, CurrentCategory)` cuối → populate CTV_FurnitureCard ngay khi switch về Furniture
- **Timer delay 0.1s** trong OnSceneRestored → ApplyRestoredActor fire SAU LeftMouseButton DeselectMesh
- **Set Background Color không work** khi Button Tint A=0 → dùng Image overlay + Set Color and Opacity
- **Tất cả nhánh Branch phải merge về cuối** — dead-end = logic sau không chạy
- **IsValid check bắt buộc** trước mọi ForEach/ForLoop dùng Object Reference


- **BP_Rotation_Gizmo_Example** kế thừa `ABaseGizmo` → Cast BaseGizmo vẫn đúng
- **Collision mặc định = NoCollision** trong BP_Rotation_Gizmo_Example → phải đổi thành Query Only
- **Get Hit Component Display Name** trả về `"ActorName.ComponentName"` → dùng **Split (From End, ".")** lấy Right S → ActiveAxis đúng
- **PreviousMousePosition phải SET trong OnMousePressed** — nếu không, frame đầu Tick tính delta = tọa độ màn hình (~885px)
- **AccumulatedRotation reset = 0 trong OnMouseReleased** — tránh giá trị cũ ảnh hưởng lần drag sau
- **RotationSpeed = 0.3** — đủ nhạy mà không quá nhanh
- **SnapAngle tách biệt SnapStep** — SnapStep cho Translation, SnapAngle cho Rotation
- **Snap logic:** tích lũy delta → khi Abs(Accumulated) >= SnapAngle → xoay Sign×SnapAngle → trừ SnapAmount khỏi Accumulated
- **Gizmo xoay theo mesh** là behavior của plugin — world axis vs local axis cần quyết định tiếp
- **ETransformationType** — enum của RuntimeTransformer plugin (None/Translation/Rotation/Scale)
- **ActivateGizmo nhận TransformType param** → BTN_Move=Translation, BTN_Rotate=Rotation, BTN_Scale=Scale
- **Mouse Left Pressed Step 11 + RestoreSnapshot** dùng **Select node** (Index=E_ActiveMode) để map sang ETransformationType


- **KHÔNG Possess TransformerPawn** → mất camera
- **SET bIsDraggingGizmo = False** phải SAU CaptureSnapshot
- **Thêm vào pin node có sẵn** — không xẻ code cũ

---

## VRAM Leak Prevention Pattern (mới — 09/05/2026)

Sau khi điều tra crash GPU sau 3-4 lần PIE (xem `Bug_GPU_VRAM_Crash.md`), pattern phát hiện:

> **Hard reference (Object Reference) đến UObject giữ chuỗi `Actor → StaticMesh → Render data (VRAM)` sống → khóa VRAM → tích lũy → crash.**

**Rule:** Mọi Blueprint có biến Object Reference đến `Actor`, `Component`, `Material Instance`, `Texture`, `Widget` — phải Clear/Set None ở:
- **Event End Play** (Actor)
- **Event Destruct** (Widget)

**Đã apply (Fix 5.1):** BP_UndoManager Event End Play clear `SpawnedActors`, `FoundActor`, `TempMeshes`, `RestoredBPActor` (v1.3).

**Đã apply (v1.1):** WBP_FurnitureInventory Event Destruct clear `TargetFurnitureActor`, `PendingRestoredActor`.

**Workaround tạm thời cho team:** Restart editor mỗi 2-3 PIE, hoặc dùng **Standalone Game** (Alt+P) thay PIE cho session dài.

---

## Trạng thái phát triển tính năng (cập nhật 20/05/2026)

### Đã hoàn thành
- Toàn bộ core furniture tool (xem các bảng Phase 1-2)
- Save/Load system với EMS
- Material catalog data infrastructure (DT_MaterialInstancesCatalog, ~3000 materials)
- **Change Material v1.1** — HOÀN THÀNH 20/05/2026 (xem `ChangeMaterial_Context_v1_1.md`)
  - Tab system Furniture/Material, SwitchInventoryMode
  - Slot Swatches (WBP_SlotSwatch, 48x48 tròn, lazy load)
  - Material Grid (WBP_MaterialCard, CTV_MaterialCard, C++ FilterMaterialItems)
  - Live Apply (Async Load → Create MID → Set Material → Debounce CaptureSnapshot)
  - Reset Slot / Reset All, Undo/Redo support, Save/Load support
  - Folder Tree + Chip Tag cho Material (BuildMaterialFolderTree)
  - Toàn bộ UX fixes: highlight slot, thumbnail update, Deselect/Select mesh, Undo/Redo SlotSwatches

### Đang phát triển
- Không có feature đang active

### Tiếp theo (theo roadmap)
1. **Refactor Phase B** — AssetService C++ Subsystem, Event Bus, async pipeline, xóa hard refs khỏi Widget
2. **glTFRuntime** — runtime asset import từ máy cá nhân
3. **Supabase** — cloud library multi-user
4. **Thumbnail Generation Pipeline** — pre-baked 3D thumbnails

### Các bug document
- `Bug_GPU_VRAM_Crash.md` — VRAM exhaustion sau 3-4 PIE (root cause + 6 tier fix)

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|-----------|------|----------|
| 2.9 | 22/04/2026 — 14:49:19 ICT | Hoàn thiện kiến trúc + Save/Load |
| 3.0 | 09/05/2026 — 10:00 ICT | Thêm VRAM Leak Prevention Pattern, reference Bug_GPU_VRAM_Crash.md, status Change Material v1.1 Stage 3 |
| 3.1 | 20/05/2026 — 16:00 ICT | Change Material v1.1 HOÀN THÀNH: update Data Structures, Layout UI, Phase 2 status, VRAM apply status, Key Learnings v1.1, roadmap tiếp theo |

---
