# B2 — Copy/Paste/Duplicate Flow
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
```
IA_FurnitureCopy (Started)      → Cast InputManager → Call CopyMesh
IA_FurniturePaste (Started)     → Cast InputManager → Call PasteMesh
IA_FurnitureDuplicate (Started) → Cast InputManager → Call DuplicateMesh
```

---

## Clipboard — `ClipboardActors : Array of S_ClipboardEntry` (v2.0)

S_ClipboardEntry: `MeshPath, DAPath, RelativeLocation(Vector), Rotation, Scale, MaterialOverrides(Array String), SurfaceType(Name), GroupID(String)`

(5 var cũ ClipboardMeshPath/DAPath/Rotation/Scale/MaterialOverrides giữ tạm, bỏ ở S7.T9)

---

## Custom Event `CopyMesh` — MULTI (v2.0)
```
Branch SelectedActors.LENGTH == 0: True → Return
CLEAR ClipboardActors
CalculateCenter(SelectedActors) → Center
ForEach SelectedActors (Actor):
  Cast → BP_FurnitureActor:
    GET MeshPath, DAPath, MaterialOverrides, PlacementSurfaceType
    GetActorRotation(Actor), GetActorScale3D(Actor)
    GetActorLocation(Actor) - Center → RelativeLocation
    Make S_ClipboardEntry(... RelativeLocation ..., GroupID="") → ADD to ClipboardActors
```
**RelativeLocation** = vị trí so với tâm nhóm → giữ formation khi paste/duplicate.

---

## Function `PasteMesh` — MULTI (v2.0)

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
                          SpawnScale=Scale, MaterialOverrides, SurfaceType=PasteSurfaceType, bAutoSelect=False) → NewActor
  Branch IsValid(NewActor): True → ADD NewActor to LocalSpawned
ForEach Completed →
  Call SelectActors(LocalSpawned)
  Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("PasteMulti")
```
**bAutoSelect=False** trong loop → select thủ công bằng SelectActors ở cuối (tránh select state bị lặp).

---

## Function `DuplicateMesh` — MULTI (v2.0)

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
                            SpawnScale=Scale, MaterialOverrides, SurfaceType, bAutoSelect=False) → NewActor
    Branch IsValid(NewActor): True → ADD to LocalSpawned
  ForEach Completed →
    Call SelectActors(LocalSpawned)        ← chỉ select đồ MỚI (standard behavior)
    Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("DuplicateMulti")
```

**⚠️ Điểm chí mạng:** phần `CLEAR LocalSpawned → ForEach ClipboardActors` nối vào **Completed** của ForEach MaxRightEdge. Nếu nối Loop Body → spawn N×N đồ.

---

## Function `SpawnFurnitureCopy` — v2.0 (+bAutoSelect, +NewActor)

**Inputs:** `MeshPath, DAPath, SpawnLocation, SpawnRotation, SpawnScale, MaterialOverrides, SurfaceType, bAutoSelect(Bool=True)`
**Output:** `NewActor : BP_FurnitureActor`
**Local:** `NewActorCopy : BP_FurnitureActor`

```
Step 1: Spawn Actor from Class(BP_FurnitureActor, SpawnLocation, SpawnRotation) → SET NewActorCopy
Step 2: Load Asset Blocking(MeshPath) → Cast Static Mesh → Set Static Mesh(GET FurnitureMesh)
        SET MeshPath, SET DAPath, Set Actor Scale 3D(SpawnScale), SET PlacementSurfaceType = SurfaceType
Step 3: GET Tags → ADD "FurnitureSpawned" → SET Tags
Step 4: ForEach MaterialOverrides (Index, Path):
          Branch Path != "": T → Load Asset Blocking → Create DMI(GET FurnitureMesh, Index) → Set Material
        SET MaterialOverrides = MaterialOverrides
Step 5: Branch bAutoSelect:                                    ← v2.0
          True  → DeselectMesh → SET SelectedFurnitureActor=NewActorCopy → Set Render Custom Depth=True
                  → Set Custom Depth Stencil 255 → (ActivateGizmo nếu ActiveMode != Select)
          False → (skip — select thủ công bởi caller)
Step 6: Branch bAutoSelect:
          True  → Call OnMeshSelected(NewActorCopy)
          False → (skip)
Return: NewActor = GET NewActorCopy    ← ⚠️ nối ở CẢ True và False branch của Branch bAutoSelect
```

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
