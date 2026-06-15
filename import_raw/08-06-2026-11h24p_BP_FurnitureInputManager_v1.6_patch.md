# BP_FurnitureInputManager
**Phiên bản:** 1.6 | **Cập nhật:** 08/06/2026 — 11:24 ICT | Actor riêng — input hub + multi-select hub + box-select hub + context-menu hub

---

## Mục đích
Tách toàn bộ logic input furniture khỏi BP_FoffPlayerController (shared code).

**v1.6 (Sprint 2 — CB_ChangeMaterial + CB_Replace):** implement 2 callback stub. Thêm `MeshesToReplace (Array)` thay thế dần `MeshToReplace (single)`. Tạo `StartReplaceMode(Actors)` và `F_OpenMaterialMode` để tái dùng logic từ context menu.

*(Phần còn lại giữ nguyên từ v1.5 — xem file gốc)*

---

## Variables

### Replace (cập nhật v1.6)
```
bIsReplaceMode      : Boolean
MeshToReplace       : BP_FurnitureActor   ← single cũ, giữ tạm đến cleanup
MeshesToReplace     : Array<BP_FurnitureActor>  ← v1.6 MULTI — dùng cho CB_Replace + StartReplaceMode
```

> **VRAM:** MeshesToReplace là Array hard ref → **CLEAR ở Event End Play**.

---

## CONTEXT MENU FUNCTIONS (v1.6 — cập nhật CB_ChangeMaterial + CB_Replace)

### F_OpenMaterialMode (Function — v1.6)
```
// 1. Đóng context menu
Branch IsValid(ContextMenuRef): True → Remove from Parent → SET None

// 2. Guard
Branch IsValid(PrimarySelectedActor): False → Return

// 3. Ensure inventory open (nested Branch, KHÔNG AND)
GET GameInstance.FurnitureInventoryRef → SET LocalInvRef
Branch IsValid(LocalInvRef):
  True → Branch Is In Viewport(LocalInvRef):
    True  → [PATH A — dùng luôn]
    False → [PATH B — tạo mới]
  False → [PATH C — tạo mới]

PATH B + C (tạo mới):
  Create Widget(WBP_FurnitureInventory) → SET LocalInvRef
  Add to Viewport → Show Mouse Cursor = True
  GameInstance → SET FurnitureInventoryRef = LocalInvRef

// 4. Apply (tất cả path merge)
Cast LocalInvRef → WBP_FurnitureInventory:
  Call EnsureExpanded              ← restore nếu đang minimize
  Call OpenMaterialModeForActor(PrimarySelectedActor)
  Call SwitchInventoryMode(Material)
```

### StartReplaceMode(Actors: Array<BP_FurnitureActor>) (Function — v1.6)
```
SET MeshesToReplace = Actors
SET bIsReplaceMode = True

Branch IsValid(PrimarySelectedActor): False → Return

Cast PrimarySelectedActor → BP_FurnitureActor → GET DAPath
Load Asset Blocking(DAPath) → Cast DA_FurnitureItem → GET MeshFolderPath → SET LocalFolderPath

GET GameInstance.FurnitureInventoryRef → SET LocalInvRef
[Nested Branch ensure inventory open — giống F_OpenMaterialMode]

Cast LocalInvRef → WBP_FurnitureInventory:
  Call EnterReplaceMode
  Call FilterByFolderPathWithUI(LocalFolderPath)
```

### CB_ChangeMaterial (Custom Event — v1.6, không còn STUB)
```
Call F_OpenMaterialMode
```

### CB_Replace (Custom Event — v1.6, không còn STUB)
```
// Close context menu
Branch IsValid(ContextMenuRef): True → Remove from Parent → SET None

// TOGGLE CHECK (TRƯỚC guard — quan trọng!)
Branch bIsReplaceMode == True:
  True (đang Replace → tắt):
    SET bIsReplaceMode = False
    CLEAR MeshesToReplace
    GET GameInstance.FurnitureInventoryRef
    Branch IsValid + Is In Viewport:
      True → Cast → Call ExitReplaceMode
    Return

  False (chưa Replace → bật):
    Branch IsValid(PrimarySelectedActor): False → Return
    Branch SelectedActors.Length > 0: False → Return
    Call StartReplaceMode(SelectedActors)
```

---

## Event End Play (cập nhật v1.6)
```
[... giữ nguyên v1.5 ...]
CLEAR MeshesToReplace     ← thêm mới v1.6
```

---

## Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 21/04/2026 | Tạo mới |
| 1.1 | 19/05/2026 | Event Dispatchers OnMeshDeselected + OnMeshSelected |
| 1.2 | 21/05/2026 | UX Phase 2.1: B1 Nudge + B2 Copy/Paste/Duplicate |
| 1.3 | 22/05/2026 | PlacementSurfaceType support |
| 1.4 | 04/06/2026 | Multi-Select Sprint 1 |
| 1.5 | 07/06/2026 | Sprint 2: Box Select + Context Menu (stubs) |
| 1.6 | 08/06/2026 — 11:24 ICT | **Sprint 2: CB_ChangeMaterial + CB_Replace implement.** Thêm `MeshesToReplace (Array)`. Tạo `F_OpenMaterialMode`, `StartReplaceMode(Actors)`. CB_Replace toggle check trước guard. CLEAR MeshesToReplace ở End Play. |
