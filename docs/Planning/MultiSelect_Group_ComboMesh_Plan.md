# Kế hoạch Multi-Select → Group Mesh → Combo Mesh → Material Edit v1.2
**Phiên bản:** 2.0 | **Ngày:** 26/05/2026 — 09:40 ICT
**Project:** Lighting_Mnger (UE5.5.4) — UE5 Interior Design Tool

---

## MỤC LỤC

1. [Tổng quan & Triết lý thiết kế](#1-tổng-quan)
2. [Sprint 1 — Multi-select cơ bản (5-7 ngày)](#sprint-1)
3. [Sprint 2 — Box Select + Context Menu (3-5 ngày)](#sprint-2)
4. [Sprint 3 — Group cơ bản (5-7 ngày)](#sprint-3)
5. [Sprint 4 — Edit Mode + Nested Group (5-7 ngày)](#sprint-4)
6. [Sprint 5 — Combo Mesh (5-7 ngày)](#sprint-5)
7. [Sprint 6 — Polish UX (5-7 ngày)](#sprint-6)
8. [Sprint 7 — Material Edit v1.2 (3-5 ngày)](#sprint-7)
9. [Keyboard Shortcuts tổng hợp](#keyboard-shortcuts)
10. [Kiến trúc kỹ thuật tổng quan](#kiến-trúc)
11. [Câu hỏi cần thảo luận](#câu-hỏi)
12. [Timeline tổng](#timeline)

---

## 1. TỔNG QUAN

### 1.1 Mục tiêu

Xây dựng hệ thống cho phép người dùng **chọn nhiều đồ nội thất → gộp thành nhóm → lưu nhóm thành combo tái sử dụng**. Sau đó bổ sung chỉnh sửa vật liệu nâng cao (Color, Roughness, Metallic).

### 1.2 Triết lý thiết kế

Ba góc nhìn định hình mọi quyết định:

**Người dùng bình thường:** Không có kiến thức kiến trúc hay vật liệu. Chỉ cần lựa chọn và thay đổi, ưng mắt là được. Ít thao tác nhất có thể. Mọi tính năng phải trực quan — nhìn là hiểu, không cần đọc hướng dẫn.

**Kinh doanh phần mềm:** Giải pháp thay thế phần mềm thiết kế nội thất khác. Dễ dùng, thao tác nhanh, tài nguyên sẵn nhiều, chỉnh sửa linh động. Combo Mesh = bán giải pháp "bộ nội thất hoàn chỉnh", không chỉ bán công cụ.

**Kỹ thuật:** Code có tính kế thừa, thêm chức năng mới ít phải sửa code cũ. Multi-select là nền tảng — làm sớm để tất cả code sau xây đúng từ đầu. Áp dụng R1-R5 cho mọi code mới.

### 1.3 Tại sao thứ tự này?

**Group Mesh trước Material Edit v1.2** vì:
- Multi-select mở khóa workflow hàng ngày (move/delete/copy nhiều đồ cùng lúc)
- Group + Combo = giá trị kinh doanh (bán bộ nội thất combo)
- Làm multi-select sớm = tất cả code sau xây đúng cho cả single lẫn multi
- Material Edit v1.2 (Color Picker, Roughness slider) là "pro user feature" — người dùng bình thường chỉ cần browse + click material từ catalog 3000 cái (đã xong ở v1.1)

---

## SPRINT 1 — MULTI-SELECT CƠ BẢN (5-7 ngày)
### Mục tiêu: chọn nhiều đồ + thao tác cùng lúc

---

### S1.1 User Story

> "Tao muốn chọn cái bàn, 4 cái ghế xung quanh, rồi kéo tất cả sang góc khác 1 lần."
> "Tao muốn xóa 5 cái cây trang trí cùng lúc thay vì xóa từng cái."

### S1.2 Cách chọn nhiều đồ

**Cách 1: Ctrl + Click (thêm/bỏ từng cái)**
- Click thường = chọn 1, bỏ chọn tất cả cái cũ (giữ nguyên như hiện tại)
- Ctrl + Click vào đồ chưa chọn = thêm vào nhóm đang chọn
- Ctrl + Click vào đồ đã chọn = bỏ khỏi nhóm
- Giống cách chọn file trong Windows Explorer

**Cách 2: Ctrl + A (chọn tất cả)**
- Chọn tất cả đồ nội thất trong scene
- Bỏ qua đồ bị khóa (Lock — Sprint 6)

### S1.3 Hiển thị khi chọn nhiều đồ

**Outline:**
- 1 đồ chọn: outline xanh dương (giữ nguyên, Custom Depth Stencil = 255)
- Nhiều đồ chọn: tất cả đều có outline xanh dương
- Đồ được chọn cuối cùng (Primary): outline sáng hơn hoặc dày hơn — làm "điểm neo" cho Align/Distribute (Sprint 6)

**Thanh thông tin Selection Info:**
```
┌──────────────────────────────────────────────────┐
│ ✦ 5 vật thể đã chọn  │  [📐Nhóm]  │  [🗑 Xóa]  │
└──────────────────────────────────────────────────┘
```
- Chỉ hiện khi chọn từ 2 đồ trở lên
- Hiện số lượng đang chọn
- Nút "Nhóm" = tạo group nhanh (Sprint 3 mới enable)
- Nút "Xóa" = xóa tất cả đồ đang chọn
- Vị trí: phía trên viewport hoặc gắn vào WBP_MeshControls

### S1.4 Thao tác với nhiều đồ đã chọn

| Thao tác | Hành vi |
|----------|---------|
| Move (W) | Kéo gizmo → tất cả đồ di chuyển cùng hướng, giữ khoảng cách tương đối |
| Rotate (E) | Xoay quanh center of bounding box (trung tâm nhóm) |
| Scale (R) | Scale đều quanh center, giữ tỉ lệ khoảng cách |
| Delete | Xóa tất cả đồ đang chọn (hỏi xác nhận nếu > 3) |
| Nudge (Arrow keys) | Di chuyển tất cả theo SnapStep |
| Esc | Bỏ chọn tất cả |
| Copy (Ctrl+C) | Copy tất cả đồ đang chọn vào clipboard (giữ vị trí tương đối) |
| Paste (Ctrl+V) | Dán tất cả tại con trỏ chuột |
| Duplicate (Ctrl+D) | Nhân đôi tại chỗ, offset nhẹ (~10cm) |

### S1.5 Gizmo khi multi-select

- Gizmo hiện tại **center of group** = trung bình vị trí tất cả đồ đang chọn
- Cách 1 (đơn giản): Spawn "Pivot Actor" tạm ở center, gắn gizmo vào → khi move Pivot, tính delta → ForEach selected actor → AddWorldOffset(delta)
- Cách 2 (RuntimeTransformer): SelectActor cho Primary, các actor còn lại move theo delta
- **Đề xuất:** Cách 1 dễ kiểm soát hơn, không phụ thuộc RuntimeTransformer internal

### S1.6 Thay đổi kiến trúc chính

**Hiện tại:**
```
BP_FurnitureInputManager:
  SelectedFurnitureActor : BP_FurnitureActor (1 biến đơn)
```

**Sau Sprint 1:**
```
BP_FurnitureInputManager:
  SelectedActors         : Array of BP_FurnitureActor (mảng)
  PrimarySelectedActor   : BP_FurnitureActor (cái chọn cuối, dùng cho gizmo + Align)
```

**Ảnh hưởng đến code hiện tại:**
- Mouse Left Pressed (12 step hiện tại): thêm logic Ctrl check → ADD hoặc REMOVE từ mảng
- DeselectMesh → DeselectAll: clear mảng, ForEach disable outline
- OnMeshSelected dispatcher: cần broadcast Primary hoặc mảng
- WBP_FurnitureInventory.OnMeshSelected: nhận Primary actor (giữ nguyên logic)
- WBP_MeshControls: hiện/ẩn toolbar dựa trên SelectedActors.Length > 0
- BP_GizmoController: attach gizmo vào Primary hoặc Pivot actor
- BP_UndoManager: S_FurniturePlacement mảng snapshot giữ nguyên, nhưng thêm SelectedMeshIndices : Array of Integer

### S1.7 Undo/Redo cho multi-select

**S_SceneSnapshot (mở rộng):**
```
S_SceneSnapshot:
  Meshes              : Array of S_FurniturePlacement (giữ nguyên)
  SelectedMeshIndices : Array of Integer (MỚI — thay SelectedMeshIndex đơn)
```

CaptureSnapshot lưu danh sách indices → RestoreSnapshot khôi phục multi-select đúng.

### S1.8 Checklist Sprint 1

- [ ] Thêm SelectedActors array + PrimarySelectedActor vào BP_FurnitureInputManager
- [ ] Refactor Mouse Left Pressed: Ctrl check → ADD/REMOVE
- [ ] DeselectAll: clear mảng, ForEach disable Custom Depth
- [ ] Multi outline: ForEach SelectedActors → enable Custom Depth Stencil
- [ ] Gizmo Pivot Actor: spawn tạm ở center, tính delta khi move
- [ ] Move/Rotate/Scale nhiều đồ (ForEach + delta)
- [ ] Delete nhiều đồ (ForEach + DestroyActor, hỏi xác nhận nếu > 3)
- [ ] Nudge nhiều đồ (ForEach + AddWorldOffset)
- [ ] Copy/Paste/Duplicate nhiều đồ
- [ ] Thanh thông tin "N vật thể đã chọn"
- [ ] S_SceneSnapshot: SelectedMeshIndices array
- [ ] Undo/Redo restore multi-select đúng
- [ ] Ctrl+A chọn tất cả
- [ ] Test: chọn 1 (click) → chọn thêm (Ctrl+Click) → move → undo → redo

---

## SPRINT 2 — BOX SELECT + CONTEXT MENU (3-5 ngày)
### Mục tiêu: box select kéo khung + menu chuột phải

---

### S2.1 Box Select (kéo khung chọn)

**UX:**
- Giữ chuột trái + kéo trên **vùng trống** (không phải trên đồ) = vẽ hình chữ nhật mờ xanh (semi-transparent overlay)
- Tất cả đồ nằm trong khung = được chọn
- Ctrl + kéo khung = thêm vào nhóm đang chọn (không thay thế)
- Thả chuột = xác nhận selection

**Phân biệt với kéo gizmo:**
- Kéo gizmo: mouse down trên gizmo component (GizmoTrace hit) → move mode
- Box select: mouse down trên vùng trống (không có hit) → box select mode
- Điều kiện: chỉ active khi ở Select mode (Q) hoặc không có đồ nào dưới cursor

**Kỹ thuật:**
- Mouse Down trên vùng trống → ghi nhớ StartPosition (screen space)
- Event Tick: vẽ rectangle overlay từ StartPosition đến CurrentMousePosition
- Mouse Up: tính rectangle trong world space → ForEach actor check bounds overlap → thêm vào SelectedActors
- Widget overlay: tạo `WBP_BoxSelectOverlay` — Canvas Panel with Image set Tint = xanh alpha 30%

### S2.2 Right-Click Context Menu

**Click phải vào 1 đồ đang chọn:**
```
┌──────────────────────────┐
│  ✂  Cắt            Ctrl+X │
│  📋 Sao chép       Ctrl+C │
│  📄 Nhân đôi       Ctrl+D │
│  ─────────────────────── │
│  🗑  Xóa            Delete │
│  🔒 Khóa            Ctrl+L │  ← Sprint 6
│  ─────────────────────── │
│  🔍 Chọn tất cả giống  ► │  ← submenu
│  ℹ  Thông tin              │
│  🎨 Đổi vật liệu          │
│  ↔  Thay thế               │
│  ─────────────────────── │
│  📐 Tạo nhóm        Ctrl+G│  ← Sprint 3
│  💾 Lưu combo              │  ← Sprint 5
└──────────────────────────┘
```

**Click phải vào đồ bị khóa (Sprint 6):**
```
┌──────────────────────────┐
│  🔓 Mở khóa               │  ← chỉ hiện mục này
└──────────────────────────┘
```

**Click phải vào vùng trống:**
```
┌──────────────────────────┐
│  📋 Dán             Ctrl+V │
│  ↩  Hoàn tác        Alt+Z  │
│  ↪  Làm lại    Shift+Alt+Z │
│  ─────────────────────── │
│  ✦  Chọn tất cả     Ctrl+A │
│  🔓 Mở khóa tất cả        │  ← Sprint 6
└──────────────────────────┘
```

**Kỹ thuật Context Menu:**
- Widget: `WBP_ContextMenu` — VerticalBox chứa `WBP_ContextMenuItem` (Button + Text + Shortcut text)
- Spawn tại vị trí chuột (screen space)
- Click vào bất kỳ đâu ngoài menu → đóng menu (Remove From Parent)
- Dùng UMG Widget (không phải Slate) — dễ hơn cho Blueprint

### S2.3 Select Similar (chọn đồ giống nhau)

**Từ submenu context menu:**
```
🔍 Chọn tất cả giống ►
    ├── Cùng mesh (6 kết quả)         ← so sánh MeshPath
    ├── Cùng loại "Ghế" (12 kết quả)  ← so sánh Category từ DA
    ├── Cùng thư mục (8 kết quả)      ← so sánh MeshFolderPath
    └── Cùng vật liệu (3 kết quả)     ← so sánh MaterialOverrides[0]
```

**Hiện số lượng kết quả** ngay trong submenu — user biết trước chọn bao nhiêu cái.

**Kỹ thuật:**
```
RightClickedActor → Cast BP_FurnitureActor → GET MeshPath

Get All Actors With Tag("FurnitureSpawned") → AllFurniture

ForEach AllFurniture:
  Cast → GET MeshPath → Count where == RightClickedActor.MeshPath
```

Scene 20-50 đồ → ForEach rất nhanh, không cần cache.

**Kết hợp Ctrl:** Giữ Ctrl khi chọn = thêm vào selection hiện có. Không giữ = thay thế selection.

### S2.4 Invert Selection (đảo ngược chọn)

- Ctrl+I = bỏ chọn cái đang chọn, chọn cái chưa chọn
- Ví dụ: chọn 1 cái bàn → Ctrl+I → chọn tất cả trừ bàn → xóa tất cả trừ bàn

### S2.5 Checklist Sprint 2

- [ ] WBP_BoxSelectOverlay: Canvas Panel + Image semi-transparent
- [ ] Mouse Down vùng trống → start box select → Event Tick vẽ rectangle
- [ ] Mouse Up → tính world space bounds → ForEach check overlap → select
- [ ] Ctrl + box select = thêm vào selection
- [ ] WBP_ContextMenu: VerticalBox + WBP_ContextMenuItem
- [ ] Click phải vào đồ → hiện context menu tại cursor
- [ ] Click phải vào vùng trống → hiện context menu đơn giản
- [ ] Click ngoài menu → đóng menu
- [ ] Select Similar: 4 tiêu chí (mesh, category, folder, material)
- [ ] Ctrl+I đảo ngược chọn
- [ ] Test: box select 5 đồ → right-click → Select Similar → chọn thêm → delete

---

## SPRINT 3 — GROUP CƠ BẢN (5-7 ngày)
### Mục tiêu: tạo/tách group + move/rotate/scale group

---

### S3.1 User Story

> "Tao đã bày xong bộ bàn ăn (1 bàn + 6 ghế). Giờ muốn kéo cả bộ sang góc khác mà không phải chọn lại 7 cái."
> "Tao muốn tách group để chỉnh lại 1 cái ghế, xong gộp lại."

### S3.2 Tạo Group

- Chọn nhiều đồ → Ctrl+G hoặc nút "Nhóm" trên thanh thông tin hoặc chuột phải → "Tạo nhóm"
- Hộp thoại nhỏ: "Đặt tên nhóm: [Bộ bàn ăn 6 ghế]" (tên mặc định "Nhóm 1", "Nhóm 2"...)
- OK → tạo BP_FurnitureGroup actor, gán children

### S3.3 BP_FurnitureGroup — Actor mới

```
BP_FurnitureGroup (Actor):
  GroupID          : String (unique, auto-generated, SaveGame)
  GroupName        : String (user-facing, SaveGame)
  ChildActors      : Array of Actor (BP_FurnitureActor hoặc BP_FurnitureGroup, SaveGame)
  ParentGroup      : BP_FurnitureGroup (None nếu top-level, Soft Ref — R2)
  bIsLocked        : Boolean (SaveGame, default False)

  Functions:
    GetAllChildren() → Array of Actor (flatten nested)
    GetCenter() → Vector (trung bình vị trí children)
    AddChild(Actor)
    RemoveChild(Actor)
    MoveGroup(Delta : Vector)
    RotateGroup(Rotation : Rotator, Pivot : Vector)
    ScaleGroup(Scale : Vector, Pivot : Vector)
```

**KHÔNG dùng UE5 AttachToActor** → quá rigid, conflict với EMS save/load.

**Dùng logical grouping:** Group chỉ lưu danh sách children. Transform thủ công:
- MoveGroup: ForEach child → AddWorldOffset(delta)
- RotateGroup: ForEach child → tính vị trí mới quanh pivot → SetActorLocation + AddActorWorldRotation
- ScaleGroup: ForEach child → tính vị trí mới từ pivot → SetActorLocation + SetActorScale3D

### S3.4 Hiển thị Group

**Khi chưa chọn:** Không hiện gì đặc biệt — đồ trông bình thường.

**Khi click vào 1 đồ trong group:**
- Tất cả đồ trong group highlight outline xanh
- Bounding box nét đứt mờ bao quanh cả group (Draw Debug Box hoặc HUD Draw Line)
- Thanh thông tin: "📦 Bộ bàn ăn 6 ghế (7 vật thể)"
- Gizmo hiện ở center group

**Click vào đồ KHÔNG trong group → chọn đồ đơn lẻ (giữ nguyên).**

### S3.5 Thao tác Group

| Thao tác | Hành vi |
|----------|---------|
| Click 1 đồ trong group | Chọn cả group |
| Move/Rotate/Scale | Cả group di chuyển/xoay/scale |
| Delete | Xóa cả group (hỏi xác nhận) |
| Ctrl+Shift+G | Tách group → đồ thành riêng lẻ |
| Copy/Paste | Copy cả group giữ cấu trúc |

### S3.6 Ungroup (tách group)

- Chọn group → Ctrl+Shift+G hoặc chuột phải → "Tách nhóm"
- Tất cả đồ trở thành đồ riêng lẻ
- BP_FurnitureGroup bị Destroy
- Nếu group có group con: "Nhóm này chứa nhóm con. Tách tất cả hay chỉ tách lớp ngoài?"
  - "Tách lớp ngoài" → group con vẫn giữ nguyên, chỉ tách ra khỏi group cha
  - "Tách tất cả" → tất cả thành đồ riêng lẻ (recursive)

### S3.7 Save/Load Group (EMS)

BP_FurnitureGroup cần tag `"FurnitureGroup"` để EMS save.

**Rebuild hierarchy sau Load:**
- EMS respawn từng actor riêng lẻ (cả BP_FurnitureActor lẫn BP_FurnitureGroup)
- Sau respawn: ForEach BP_FurnitureGroup → GET ChildActors → re-link bằng UniqueID match
- Cần lưu children IDs (array of string) thay vì direct reference
- Timer 0.2s sau Load để đợi tất cả actors spawn xong → rồi rebuild hierarchy

### S3.8 Undo/Redo cho Group

**S_SceneSnapshot (mở rộng thêm):**
```
S_SceneSnapshot:
  Meshes              : Array of S_FurniturePlacement (giữ nguyên)
  Groups              : Array of S_GroupData (MỚI)
  SelectedMeshIndices : Array of Integer (từ Sprint 1)
```

```
S_GroupData:
  GroupID       : String (unique)
  GroupName     : String
  ChildIDs      : Array of String (UniqueID của children)
  ParentGroupID : String (rỗng nếu top-level)
  bIsLocked     : Boolean
```

### S3.9 Checklist Sprint 3

- [ ] BP_FurnitureGroup actor class
- [ ] Ctrl+G tạo group: hộp thoại tên → spawn BP_FurnitureGroup → gán children
- [ ] Ctrl+Shift+G tách group: xóa BP_FurnitureGroup, children thành riêng lẻ
- [ ] Click đồ trong group → chọn cả group (tìm ParentGroup)
- [ ] Group outline: tất cả children enable Custom Depth
- [ ] Bounding box nét đứt quanh group
- [ ] MoveGroup: ForEach child → AddWorldOffset(delta)
- [ ] RotateGroup: tính vị trí mới quanh pivot
- [ ] ScaleGroup: tính vị trí + scale mới từ pivot
- [ ] S_GroupData struct + Groups array trong snapshot
- [ ] Undo/Redo capture/restore group data
- [ ] EMS Save/Load: tag "FurnitureGroup", rebuild hierarchy sau load
- [ ] Delete group: hỏi xác nhận → DestroyActor children + group
- [ ] Test: tạo group 5 đồ → move → undo → save → load → ungroup → undo

---

## SPRINT 4 — EDIT MODE + NESTED GROUP (5-7 ngày)
### Mục tiêu: chỉnh từng đồ trong group + group lồng group

---

### S4.1 Edit Mode (Double-click vào group)

**UX Flow:**
```
Click đồ trong group → chọn CẢ group (group mode)
    ↓
Double-click → VÀO TRONG group (edit mode)
    ↓
Đồ bên ngoài group mờ đi (opacity giảm ~40%)
Chỉ đồ trong group hiện rõ
    ↓
Có thể: chọn, move, rotate, scale, delete, thay material TỪNG ĐỒ bên trong
    ↓
Esc hoặc click ngoài group → THOÁT edit mode → quay về bình thường
```

**Dimming đồ bên ngoài:**
- ForEach actor KHÔNG thuộc group → Set Render Custom Depth = False + giảm opacity material
- Hoặc đơn giản hơn: Post Process Volume với Stencil Buffer — đồ trong group giữ Stencil, đồ ngoài bị dim
- Cách đơn giản nhất: overlay widget toàn viewport, semi-transparent black (alpha 40%), group members render bình thường phía trên

**Thanh thông tin khi edit mode:**
```
┌─────────────────────────────────────────────────────────┐
│ ✏️ Đang chỉnh: Bộ bàn ăn 6 ghế  │  [Thoát nhóm ↩]    │
└─────────────────────────────────────────────────────────┘
```

### S4.2 Nested Group (group lồng group)

**Ví dụ thực tế:**
```
📦 Phòng khách                    ← Group cấp 1
├── 📦 Bộ sofa                    ← Group cấp 2 (con của Phòng khách)
│   ├── Sofa 3 chỗ               ← mesh riêng lẻ
│   ├── Ghế sofa đơn (trái)
│   └── Ghế sofa đơn (phải)
├── 📦 Kệ TV                     ← Group cấp 2
│   ├── Kệ TV
│   ├── TV 55 inch
│   └── Soundbar
├── Bàn trà                      ← mesh riêng lẻ (con trực tiếp)
├── Thảm
└── Đèn cây
```

**Điều hướng:**
- Click → chọn "Phòng khách" (cấp 1)
- Double-click → vào "Phòng khách" → thấy "Bộ sofa", "Kệ TV", Bàn trà, Thảm, Đèn cây
- Double-click "Bộ sofa" → vào cấp 2 → thấy 3 sofa riêng lẻ
- Esc → quay về cấp 1 (Phòng khách)
- Esc → quay về bình thường (thoát group)

**Giới hạn:** Cho phép tối đa 3 cấp nested. Đủ cho interior design (Phòng → Khu vực → Bộ đồ). Hơn 3 cấp gây rối.

### S4.3 Kéo đồ ra/vào group

- Trong edit mode: kéo đồ ra ngoài bounding box của group → "Bỏ ra khỏi nhóm?"
- Ngoài edit mode: kéo đồ thả vào group (thông qua Scene Outliner — Sprint 6)
- Multi-select + Ctrl+G khi đang ở edit mode = tạo sub-group

### S4.4 Checklist Sprint 4

- [ ] Double-click detection (thời gian giữa 2 click < 0.3s)
- [ ] EnterEditMode: SET CurrentEditingGroup, dim đồ bên ngoài
- [ ] ExitEditMode: restore dim, clear CurrentEditingGroup
- [ ] Thanh thông tin edit mode + nút "Thoát nhóm"
- [ ] Nested group: ChildActors chứa BP_FurnitureGroup con
- [ ] Multi-level navigate: double-click vào group con → đi sâu 1 cấp
- [ ] Esc = quay lên 1 cấp, Esc ở cấp ngoài = thoát
- [ ] Giới hạn 3 cấp nested
- [ ] Ungroup options: "Tách lớp ngoài" vs "Tách tất cả"
- [ ] Test: tạo nested group 3 cấp → navigate → chỉnh đồ → undo → save → load

---

## SPRINT 5 — COMBO MESH (5-7 ngày)
### Mục tiêu: lưu group thành template tái sử dụng + spawn từ inventory

---

### S5.1 User Story

> "Bộ bàn ăn này tao bày đẹp rồi, muốn lưu lại để dùng cho dự án khác."
> "Tao muốn kéo 1 bộ phòng khách có sẵn ra, không cần tự bày từng cái."

### S5.2 Lưu Group thành Combo

**Trigger:** Chọn group → chuột phải → "💾 Lưu thành Combo" hoặc nút trên thanh thông tin.

**Hộp thoại:**
```
┌────────────────────────────────────────┐
│         LƯU COMBO MỚI                 │
│                                        │
│  Tên:       [Bộ bàn ăn Scandinavian ] │
│  Phân loại: [Phòng ăn          ▼]     │
│  Phong cách:[Scandinavian      ▼]     │
│  Tags:      [bàn ăn, 6 ghế, gỗ sồi]  │
│                                        │
│  ☑ Giữ vật liệu đã chỉnh             │
│  ☑ Giữ tỉ lệ đã scale                │
│                                        │
│  Preview:  [ảnh auto-gen]             │
│                                        │
│        [Hủy]        [Lưu]             │
└────────────────────────────────────────┘
```

### S5.3 Data lưu Combo

```
DT_ComboMeshCatalog (DataTable mới, struct S_ComboMeshData):
  ComboName    : String
  Category     : String (Phòng khách, Phòng ăn, Phòng ngủ...)
  Style        : String (Modern, Scandinavian, Industrial...)
  Tags         : String (pipe-separated: "bàn ăn|6 ghế|gỗ sồi")
  ItemCount    : Integer
  ThumbnailPath: String (Soft Object Reference Texture2D)
  ComboJSON    : String (JSON chứa mảng S_FurniturePlacement + S_GroupData)
```

**ComboJSON format:**
```json
{
  "meshes": [
    {
      "meshPath": "/Game/.../SM_Chair",
      "relativeLocation": {"x": 0, "y": 80, "z": 0},
      "relativeRotation": {"pitch": 0, "yaw": 45, "roll": 0},
      "scale": {"x": 1, "y": 1, "z": 1},
      "materialOverrides": ["/Game/.../MI_FabricBlue"],
      "materialParams": ["{\"Tint\":[1,1,1,1]}"]
    }
  ],
  "groups": [
    {
      "groupName": "Bàn ăn",
      "childIndices": [0, 1, 2, 3, 4, 5, 6]
    }
  ]
}
```

Vị trí lưu **relative** (tương đối so với center combo) → spawn ở bất kỳ đâu.

### S5.4 Combo trong Inventory

**Category đặc biệt trong folder tree:**
```
├── Tất cả
├── Bàn
├── Ghế
├── Sofa
├── ...
├── ─────────
├── ⭐ Yêu thích
├── 🕐 Gần đây
└── 🧩 Combo         ← category đặc biệt
    ├── Phòng khách
    ├── Phòng ăn
    ├── Phòng ngủ
    └── Tự tạo
```

**Card hiển thị:**
```
┌──────────────────┐
│  [ảnh combo]     │
│                  │
│  Bộ bàn ăn 6 ghế│
│  7 vật thể       │
│  ⭐ ℹ            │
└──────────────────┘
```

### S5.5 Spawn Combo vào Scene

- Click card combo hoặc kéo thả vào viewport
- Ghost preview hiện đủ cả bộ khi đang kéo (semi-transparent tất cả mesh)
- Spawn tại vị trí cursor (center combo = cursor)
- Tự động tạo group với tên combo
- Async load tất cả mesh (R1) → spawn tuần tự

### S5.6 Combo Thumbnail tự động

- Khi lưu combo → SceneCapture2D chụp từ góc perspective (30° từ trên xuống)
- Tận dụng LV_ThumbnailStudio đã setup
- Camera orbit quanh combo center, chọn góc đẹp nhất
- Lưu thành Texture2D → assign vào ThumbnailPath

### S5.7 Combo Variants (tầm nhìn kinh doanh — phase sau)

Cùng layout nhưng đổi material theo phong cách:
- Bộ phòng khách Modern (da đen, kính, kim loại)
- Bộ phòng khách Scandinavian (gỗ sáng, vải trắng)
- Bộ phòng khách Industrial (gỗ tối, sắt, gạch)

User xem 3 variant → chọn → kéo vào. Đây là tính năng bán hàng cốt lõi.

### S5.8 Checklist Sprint 5

- [ ] S_ComboMeshData struct + DT_ComboMeshCatalog DataTable
- [ ] WBP_SaveComboDialog: UI hộp thoại lưu combo
- [ ] SerializeGroupToJSON: mảng mesh + group → JSON string
- [ ] DeserializeComboJSON: JSON → spawn actors + rebuild group
- [ ] Category "Combo" trong folder tree Inventory
- [ ] WBP_ComboCard (hoặc tái dùng WBP_FurnitureCard với badge "Combo")
- [ ] Spawn combo: async load meshes → spawn → auto group
- [ ] Ghost preview nhiều mesh khi drag combo
- [ ] Combo thumbnail: SceneCapture2D auto-gen
- [ ] Test: tạo group → lưu combo → thoát PIE → vào lại → spawn combo → chỉnh → lưu combo mới

---

## SPRINT 6 — POLISH UX (5-7 ngày)
### Mục tiêu: Lock, Align & Distribute, Scene Outliner, Smart Snap, các tiện ích

---

### S6.1 Lock/Unlock (khóa đồ)

**Mục đích:** Khóa đồ đã bày xong → không thể chọn, move, delete, đổi material. Tránh lỡ tay.

**4 cách khóa:**
1. Chọn đồ → Ctrl+L toggle khóa/mở
2. Chuột phải → "Khóa"
3. Scene Outliner: click icon ổ khóa
4. Toolbar: nút khóa trên WBP_MeshControls

**3 cách mở khóa:**
1. Click phải vào đồ đã khóa → "Mở khóa" (cách duy nhất từ viewport)
2. Scene Outliner: click icon ổ khóa
3. "Mở khóa tất cả" (Scene Outliner footer hoặc menu Edit)

**Kỹ thuật:**
```
BP_FurnitureActor:
  bIsLocked : Boolean (SaveGame, default False)

Mouse Left Pressed → Step 6 → Cast BP_FurnitureActor → GET bIsLocked
  True → STOP (coi như click vùng trống)
  False → tiếp tục chọn
```

**Khóa group:** Set bIsLocked trên BP_FurnitureGroup → ForEach children set bIsLocked.

**Hiển thị:**
- Viewport: icon ổ khóa nhỏ hiện góc đồ khi hover gần
- Scene Outliner: icon ổ khóa vàng + tên xám
- Click vào đồ bị khóa → tooltip 2s "🔒 Đồ này đã khóa — click phải để mở khóa"

**Undo:** Khóa/mở khóa ghi vào Undo history (S_FurniturePlacement thêm bIsLocked).

### S6.2 Align & Distribute (căn chỉnh & phân bố đều)

**Chỉ hiện khi chọn từ 2 đồ trở lên.** Toolbar bổ sung:

```
[⫷ Trái] [⫿ Giữa] [⫸ Phải]  │  [⫻ Trên] [⫼ Giữa] [⫽ Dưới]  │  [↔ Đều ngang] [↕ Đều dọc]
```

**6 nút Align:**
- Căn trái/giữa/phải (trục X world): dịch tất cả đồ về cạnh trái/giữa/phải của bounding box chung
- Căn trên/giữa/dưới (trục Y world): tương tự theo Y

**2 nút Distribute:**
- Phân bố đều ngang: sắp đồ từ trái→phải, khoảng cách đều. Đồ ngoài cùng giữ nguyên.
- Phân bố đều dọc: tương tự theo Y

**2 chế độ Reference:**
- "Theo vùng chọn" (mặc định): mốc là bounding box tất cả đồ chọn
- "Theo đồ chọn đầu" (Primary): mốc là Primary actor, đồ khác dịch về theo

**Kỹ thuật:**
```
ForEach SelectedActor:
  GetActorBounds() → Origin, BoxExtent (AABB — xử lý rotation)
  Left = Origin.X - BoxExtent.X
  Right = Origin.X + BoxExtent.X
  ...

Tính vị trí mới → SetActorLocation() → CaptureSnapshot("Align")
```

### S6.3 Scene Outliner (danh sách đồ trong scene)

**Widget riêng `WBP_SceneOutliner`, bên phải viewport, toggle phím O.**

```
┌─ Scene ──────────────────────┐
│ 🔍 [Tìm kiếm...]            │
│                              │
│ ▼ 📦 Phòng khách        (7)  │
│   ├── ▼ 📦 Bộ sofa      (3)  │
│   │   ├── Sofa 3 chỗ         │
│   │   ├── Sofa đơn (trái)    │
│   │   └── Sofa đơn (phải)    │
│   ├── Bàn trà                │
│   ├── Đèn cây                │
│   ├── 🔒 Thảm               │
│   └── 👁̸ Cây xanh           │
│ ▶ 📦 Phòng ăn           (8)  │
│ ─────────────────────────── │
│ Đèn trần chính               │
│ Cây cảnh lối vào             │
│                              │
│ 18 vật thể · 2 nhóm         │
└──────────────────────────────┘
```

**7 tương tác:**
1. Click = chọn đồ + camera focus
2. Double-click nhóm = vào edit mode
3. Kéo thả = đổi nhóm
4. Icon ổ khóa = toggle Lock
5. Icon con mắt = toggle Visibility (ẩn/hiện)
6. Double-click tên = đổi tên (CustomName)
7. Click phải = context menu

**Đồng bộ 2 chiều:** Chọn trong viewport → outliner highlight. Chọn trong outliner → viewport outline.

**Widget con: WBP_OutlinerRow**
```
Variables:
  TargetActor : BP_FurnitureActor (Soft Ref — R2)
  GroupRef    : BP_FurnitureGroup (Soft Ref — R2)
  IndentLevel : Integer
  bIsGroup    : Boolean
```

**Rebuild khi:** Spawn/Delete, Group/Ungroup, Undo/Redo, Load scene → Event Dispatcher OnSceneStructureChanged.

### S6.4 Toggle Visibility (ẩn/hiện tạm thời)

- Scene Outliner: icon 👁 toggle
- Chuột phải → "Ẩn tạm"
- SetActorHiddenInGame(true/false)
- Đồ vẫn tồn tại, chỉ vô hình — dùng khi cần nhìn rõ đồ bị che khuất
- "Hiện tất cả" trong outliner footer

### S6.5 Focus on Selected (phím F)

- Chọn đồ → F → camera lerp + zoom về đồ đó (SetViewTarget smooth)
- Chọn group → F → camera zoom ra vừa đủ thấy cả group bounding box
- Chọn nhiều → F → camera zoom fit tất cả đồ đang chọn

### S6.6 Smart Snap (snap thông minh giữa các đồ)

**5 loại snap:**
1. **Căn cạnh:** Cạnh đồ đang kéo thẳng hàng với cạnh đồ khác → hiện guideline nét đứt xanh
2. **Căn giữa:** Tâm đồ thẳng hàng với tâm đồ khác
3. **Cách đều:** 3+ đồ trên 1 hàng → snap cách đều, hiện "100cm = 100cm"
4. **Cách tường đều:** Snap cùng khoảng cách từ tường với đồ khác
5. **Cùng hàng:** Snap tâm vào cùng đường ngang/dọc với nhiều đồ đã đặt

**Hoạt động cùng SnapStep:** SnapStep xử lý bước di chuyển, Smart Snap xử lý hút vào vị trí thẳng hàng.

**Settings toolbar:**
```
Snap: [10cm]  │  Smart Snap: [✓ Bật]  │  Ngưỡng: [5cm]
```
- Toggle bật/tắt, ngưỡng 5cm mặc định
- Giữ Alt khi kéo = tạm tắt Smart Snap

**Kỹ thuật:**
```
Mỗi frame khi đang kéo đồ:
  ForEach OtherActor:
    So sánh 12 cặp (Left/Right/Center × X/Y)
    |delta| < Threshold → snap + hiện guideline
```

Scene 20-50 đồ → 600 phép so sánh float/frame → không đáng kể.

### S6.7 Array / Pattern (nhân đôi theo hàng/lưới)

- Chọn 1 đồ → chuột phải → "Tạo hàng" → nhập: số lượng = 6, khoảng cách = 80cm, hướng = ngang
- "Tạo lưới" → hàng × cột × khoảng cách
- Kết quả spawn copies → tự động gộp thành group
- Dùng cho: bày bàn nhà hàng, ghế hội trường, đèn trần

### S6.8 Mirror Group (phản chiếu)

- Chọn group → chuột phải → "Phản chiếu ngang/dọc"
- Tạo bản sao đối xứng qua trục
- Dùng cho: 2 bên phòng đối xứng

### S6.9 Checklist Sprint 6

- [ ] Lock/Unlock: bIsLocked variable, input filtering, 4 cách khóa, 3 cách mở
- [ ] Align toolbar: 6 nút align + 2 nút distribute + 2 chế độ reference
- [ ] WBP_SceneOutliner: widget tree, 7 tương tác, đồng bộ 2 chiều
- [ ] WBP_OutlinerRow: indent, expand/collapse, lock/eye icons
- [ ] Toggle Visibility: SetActorHiddenInGame
- [ ] Focus (F): camera lerp + zoom vào đồ/group/multi-select
- [ ] Smart Snap: guideline hiện khi align, ngưỡng 5cm, toggle on/off
- [ ] Array/Pattern: dialog nhập số lượng + khoảng cách → spawn + auto group
- [ ] Mirror Group: phản chiếu qua trục → spawn copies
- [ ] Test: toàn bộ flow tích hợp

---

## SPRINT 7 — MATERIAL EDIT v1.2 (3-5 ngày)
### Mục tiêu: Color Picker, Roughness, Metallic slider + live preview

---

### S7.1 User Story

> "Vải sofa này gần ưng rồi nhưng muốn đậm hơn 1 chút."
> "Gỗ này đẹp nhưng muốn bóng hơn."

### S7.2 Nền tảng đã có từ v1.1

- Create Dynamic Material Instance (MID) đã chạy khi apply material
- MaterialParams : Array of String đã khai báo (placeholder, SaveGame)
- Save/Load material, Undo/Redo material đã hoạt động

### S7.3 UI Panel — Material Edit

Khi chọn mesh → tab Material → chọn slot → **bên dưới grid vật liệu** hiện panel chỉnh sửa:

```
┌─ Chỉnh sửa vật liệu ─────────────────────┐
│                                             │
│  Màu tông:  [──●────────]                   │
│             🎨 [    preview swatch    ]     │
│                                             │
│  Độ nhám:   [────────●──] 0.7               │
│             (mờ) ←————————→ (bóng)          │
│                                             │
│  Độ kim loại: [●────────] 0.1               │
│             (phi kim) ←————→ (kim loại)     │
│                                             │
│  ☐ UV Scale:  [───●─────] 1.0              │
│  ☐ UV Xoay:   [●────────] 0°               │
│                                             │
│       [Đặt lại mặc định]                   │
└─────────────────────────────────────────────┘
```

**Nguyên tắc UX:**
- Tên tiếng Việt: "Độ nhám" (không phải "Roughness"), "Độ kim loại" (không phải "Metallic")
- Text giải thích 2 đầu slider: "(mờ) ←→ (bóng)" — người dùng bình thường hiểu ngay
- UV Scale/Xoay ẩn mặc định (checkbox mở ra) — ít người cần
- "Đặt lại mặc định" = quay về param gốc của material

### S7.4 Kỹ thuật

**Live preview:** Gọi `Set Vector Parameter Value` (Tint) + `Set Scalar Parameter Value` (Roughness, Metallic) trên MID đã tạo ở v1.1 → mesh update ngay lập tức, không cần SceneCapture2D.

**Serialize:**
```
MaterialParams[SlotIndex] = "{\"Tint\":[0.8,0.6,0.4,1],\"Roughness\":0.7,\"Metallic\":0.1}"
```

JSON per slot → EMS tự save/load qua SaveGame property.

**Undo/Redo:** S_FurniturePlacement thêm MaterialParams → snapshot capture param values.

### S7.5 Áp dụng cho multi-select / group

- Multi-select: chỉnh slider → ForEach selected mesh → Set Parameter trên MID (cùng slot)
- Group edit mode: chỉnh từng mesh bên trong
- Hoặc: chọn group ở group mode → chỉnh = apply tất cả children (cùng slot)

### S7.6 Color Picker

- UE5 có `Color Picker` widget built-in (FColorPicker)
- Hoặc: tự build đơn giản hơn — hue bar + saturation/value square
- Output: LinearColor → Set Vector Parameter Value("Tint", Color)

### S7.7 Checklist Sprint 7

- [ ] WBP_MaterialEditPanel: Color Picker + 2 slider + UV options + Reset button
- [ ] Color Picker: hue + saturation/value → Set Vector Parameter Value
- [ ] Roughness slider (0-1): Set Scalar Parameter Value("Roughness", Value)
- [ ] Metallic slider (0-1): Set Scalar Parameter Value("Metallic", Value)
- [ ] UV Scale/Rotation (optional): Set Scalar Parameter Value("UV_Scale/Rotation")
- [ ] Serialize MaterialParams → JSON per slot
- [ ] "Đặt lại mặc định" → restore original param values
- [ ] Undo/Redo capture MaterialParams
- [ ] Apply cho multi-select (ForEach loop)
- [ ] Test: chọn sofa → đổi material → chỉnh Tint đậm hơn → chỉnh Roughness → undo → save → load

---

## KEYBOARD SHORTCUTS TỔNG HỢP

### Giữ nguyên từ trước

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
| Esc | Deselect / Thoát group |
| Arrow keys | Nudge |

### Thêm mới

| Phím | Chức năng | Sprint |
|------|-----------|--------|
| Ctrl+Click | Thêm/bỏ chọn | Sprint 1 |
| Ctrl+A | Chọn tất cả | Sprint 1 |
| Ctrl+C | Copy | Sprint 1 |
| Ctrl+V | Paste | Sprint 1 |
| Ctrl+D | Duplicate | Sprint 1 |
| Ctrl+X | Cắt | Sprint 2 |
| Ctrl+I | Đảo chọn | Sprint 2 |
| Ctrl+G | Tạo group | Sprint 3 |
| Ctrl+Shift+G | Tách group | Sprint 3 |
| Double-click | Vào edit mode group | Sprint 4 |
| Ctrl+L | Toggle Lock | Sprint 6 |
| O | Toggle Scene Outliner | Sprint 6 |
| F | Focus on selected | Sprint 6 |
| Alt (giữ) | Tắt tạm Smart Snap | Sprint 6 |

---

## KIẾN TRÚC KỸ THUẬT TỔNG QUAN

### Biến thay đổi chính

**BP_FurnitureInputManager:**
```
TRƯỚC:  SelectedFurnitureActor : BP_FurnitureActor

SAU:    SelectedActors          : Array of BP_FurnitureActor
        PrimarySelectedActor    : BP_FurnitureActor
        CurrentEditingGroup     : BP_FurnitureGroup (None khi không edit)
```

**BP_FurnitureActor (thêm):**
```
  bIsLocked   : Boolean (SaveGame, default False)
  CustomName  : String (SaveGame, default "")
  GroupID     : String (SaveGame — ID của group chứa nó, rỗng nếu riêng lẻ)
```

### Actor mới

**BP_FurnitureGroup:**
```
  GroupID     : String (unique, auto-gen, SaveGame)
  GroupName   : String (SaveGame)
  ChildActors : Array of Actor (SaveGame)
  ParentGroup : Soft Ref BP_FurnitureGroup (R2)
  bIsLocked   : Boolean (SaveGame)
  Tag         : "FurnitureGroup"
```

### Struct mới / mở rộng

**S_FurniturePlacement (mở rộng):**
```
  + bIsLocked     : Boolean
  + CustomName    : String
  + GroupID       : String
  + MaterialParams : Array of String (JSON per slot)
```

**S_GroupData (MỚI):**
```
  GroupID       : String
  GroupName     : String
  ChildIDs      : Array of String
  ParentGroupID : String
  bIsLocked     : Boolean
```

**S_SceneSnapshot (mở rộng):**
```
  Meshes              : Array of S_FurniturePlacement
  Groups              : Array of S_GroupData (MỚI)
  SelectedMeshIndices : Array of Integer (MỚI)
```

**S_ComboMeshData (MỚI):**
```
  ComboName     : String
  Category      : String
  Style         : String
  Tags          : String
  ItemCount     : Integer
  ThumbnailPath : String
  ComboJSON     : String
```

### Widget mới

| Widget | Mô tả | Sprint |
|--------|--------|--------|
| WBP_BoxSelectOverlay | Rectangle semi-transparent khi kéo khung | Sprint 2 |
| WBP_ContextMenu | Menu chuột phải | Sprint 2 |
| WBP_ContextMenuItem | 1 dòng trong context menu | Sprint 2 |
| WBP_SelectionInfoBar | "5 vật thể đã chọn" + nút | Sprint 1 |
| WBP_GroupNameDialog | Hộp thoại đặt tên group | Sprint 3 |
| WBP_SaveComboDialog | Hộp thoại lưu combo | Sprint 5 |
| WBP_SceneOutliner | Panel danh sách scene | Sprint 6 |
| WBP_OutlinerRow | 1 hàng trong outliner | Sprint 6 |
| WBP_MaterialEditPanel | Color + sliders | Sprint 7 |

### Nguyên tắc R1-R5 áp dụng

- **R1:** Async load combo meshes, không blocking
- **R2:** Widget không giữ hard ref đến Group/Actor — dùng Soft Ref, SET None ở Event Destruct
- **R3:** Widget nhận GroupID + GroupName (struct nhẹ), không nhận actor nặng
- **R4:** Event Destruct clear mọi reference
- **R5:** Lưu GroupID/MeshPath (string), không lưu actor path /Game/...

---

## CÂU HỎI CẦN THẢO LUẬN

1. **Rotate multi-select:** Xoay quanh center nhóm hay quanh Primary?
   - Đề xuất: center nhóm (phần mềm khác thường xoay quanh center)

2. **Group pivot:** Center tự động hay cho user chọn?
   - Đề xuất: center tự động. Cho phép kéo pivot = pro feature, để phase sau.

3. **Combo lưu ở đâu:** DataTable trong project hay file JSON bên ngoài?
   - Đề xuất: DataTable trước (dễ, đã quen). Migrate sang JSON/Supabase khi làm cloud.

4. **Context menu:** Dùng UMG Widget hay Slate?
   - Đề xuất: UMG Widget (dễ hơn cho Blueprint). Slate chỉ cần khi UMG không đủ.

5. **Box select trigger:** Kéo ở đâu, phân biệt với kéo gizmo?
   - Đề xuất: chỉ active khi mouse down trên vùng trống (không hit actor/gizmo).

6. **Scene Outliner vị trí:** Panel phải cố định hay floating/toggle?
   - Đề xuất: panel phải toggle phím O, có thể kéo resize. Mặc định đóng.

---

## TIMELINE TỔNG

| Sprint | Nội dung | Thời gian | Tích lũy |
|--------|----------|-----------|----------|
| 1 | Multi-select cơ bản | 5-7 ngày | ~1 tuần |
| 2 | Box Select + Context Menu | 3-5 ngày | ~2 tuần |
| 3 | Group cơ bản | 5-7 ngày | ~3 tuần |
| 4 | Edit Mode + Nested | 5-7 ngày | ~4 tuần |
| 5 | Combo Mesh | 5-7 ngày | ~5-6 tuần |
| 6 | Polish UX (Lock, Align, Outliner, Smart Snap) | 5-7 ngày | ~6-7 tuần |
| 7 | Material Edit v1.2 | 3-5 ngày | ~7-8 tuần |
| **Tổng** | | **~30-45 ngày** | **~7-8 tuần** |

Ghi chú: thời gian ước tính dựa trên tốc độ sprint trước (~1 tính năng phức tạp / tuần). Có thể nhanh hơn nếu ít bug, chậm hơn nếu gặp vấn đề kiến trúc.

---

**Sau khi hoàn thành 7 Sprint → tiến hành:**
- Refactor Phase B (AssetService C++, Event Bus) — lúc này biết rõ cần gì
- glTFRuntime — runtime asset import
- Supabase — cloud, share, multi-user
