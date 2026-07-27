# Sprint 2 — Context Menu: CB_ChangeMaterial + CB_Replace (Prep để thực thi cùng Sonnet 4.6)
**Phiên bản:** 1.2 | **Cập nhật:** 24/07/2026 | §4.2 CB_Replace viết lại theo K2Node export thật (C9.0c, migrate `ReplaceTarget`) | Lighting_Mnger UE5.5.4

> **v1.1 — chốt 3 câu hỏi:**
> 1. **Replace = MULTI:** select similar (hoặc nhóm) → Replace → chọn mesh thay → **TẤT CẢ đồ đang chọn** đổi mesh. (Material vẫn single-primary cho v1.)
> 2. **Sửa luôn BTN_Replace** trong WBP_MeshControls → trỏ về function chung `StartReplaceMode`.
> 3. (giải thích câu 3 ở mục 8.)

---

## 0. TÓM TẮT

- **CB_ChangeMaterial** = mở inventory tab Material, nhắm **PrimarySelectedActor** → tái dùng Material Picker v1.1.
- **CB_Replace** = bật **Replace mode** cho **toàn bộ SelectedActors**, lọc inventory theo folder mesh primary → tái dùng logic Replace + **nâng cấp card handler thành multi**.

**Việc mới duy nhất (logic thật):** đổi handler replace ở card từ **1 đồ** → **ForEach nhóm đồ**. Phần còn lại là gọi code có sẵn.

---

## 1. LIÊN QUAN ĐẾN CHỨC NĂNG NÀO (code tái dùng)

### CB_ChangeMaterial — dựa trên Change Material v1.1 (single, không đổi)
| Có sẵn | Vai trò |
|---|---|
| `WBP_FurnitureInventory` tab Material | UI — không tạo widget mới |
| `SwitchInventoryMode(Material)` | bật tab Material |
| `TargetFurnitureActor` + `RefreshSlotSwatches` | đồ đang chỉnh + swatch slot |
| `ApplyMaterial`/`LoadAndApplyMaterial` | click card → apply (không đụng) |
| `OnMeshSelected` nhánh Material | logic cần tái dùng (gom vào `OpenMaterialModeForActor`) |

### CB_Replace — dựa trên Replace v1.1/v1.3, NÂNG CẤP MULTI
| Có sẵn | Vai trò | Đổi gì |
|---|---|---|
| `bIsReplaceMode` (InputManager) | trạng thái replace | giữ |
| `MeshToReplace` (single) | đồ cần thay | **→ migrate sang `MeshesToReplace` (Array)** |
| `EnterReplaceMode`/`ExitReplaceMode` (inventory) | bật/tắt mode | giữ |
| `FilterByFolderPathWithUI(MeshFolderPath)` | lọc card theo folder | giữ (folder của primary) |
| `BTN_Replace OnClicked` (MeshControls) | bật replace | **→ gọi `StartReplaceMode`** |
| **Card `BTN_ChangeMesh`** (WBP_DragOverlay_FurnitureCard) | **replace thật** | **→ đổi single thành ForEach multi** |

---

## 2. ĐIỀU KIỆN ĐẶC BIỆT

### 2.1 Phạm vi áp dụng
- **CB_ChangeMaterial → PrimarySelectedActor** (single). Apply-all material = future (ForEach trong LoadAndApplyMaterial).
- **CB_Replace → toàn bộ SelectedActors** (multi). Folder filter theo **PrimarySelectedActor** (select-similar đều cùng folder; nhóm hỗn hợp thì lọc theo primary — chấp nhận được).
- **Guard:** `IsValid(PrimarySelectedActor)` đầu cả 2 callback. Replace thêm guard `SelectedActors.Length > 0`.

### 2.2 Inventory đóng/mở — xử lý cả 2 (nested Branch, KHÔNG dùng AND)
Lấy `FurnitureInventoryRef` từ `Foff_GameInstance`:
- Mở (`IsValid` + `Is In Viewport`) → dùng luôn.
- Đóng → `Create WBP_FurnitureInventory → Add to Viewport → SET ref (GameInstance) → Show Mouse Cursor`.

### 2.3 Đóng context menu đầu callback
`IsValid(ContextMenuRef) → Remove from Parent → SET None` **trước** khi mở inventory.

### 2.4 Multi-replace: MeshesToReplace luôn = SelectedActors khi ở Replace mode
- Vào replace → `MeshesToReplace = SelectedActors` (copy).
- Đổi selection lúc đang replace (v1.3 Trigger 3) → `MeshesToReplace = SelectedActors` (cập nhật).
- Sau replace → đồ mới được select → `MeshesToReplace = đồ mới` (replace tiếp được).

### 2.5 Replace giữ transform từng đồ, reset material
Mỗi đồ mới spawn tại **Location + Rotation của đồ cũ tương ứng** (giống bản single — KHÔNG copy Scale, vì mesh khác kích thước gốc). Material reset (mesh mới có thể khác số slot). *(Nếu muốn giữ Scale → thêm GET/SET Actor Scale 3D trong loop — quyết định optional.)*

### 2.6 CaptureSnapshot 1 LẦN sau khi replace HẾT nhóm
Trong vòng ForEach **KHÔNG** CaptureSnapshot. Spawn hết + tag hết + re-select → CaptureSnapshot("Replace") **1 lần** ở Completed. (Bài học: capture trong loop = nhiều snapshot rác + index sai.)

### 2.7 Re-select sau replace dùng SelectActors (tái dùng multi-select)
Thay vì tự set stencil/gizmo từng đồ (bản single cũ), dùng `DeselectAll → SelectActors(LocalNewActors)` → tự lo outline (255/254) + gizmo (single/pivot). Chạy từ button OnClicked (input event) → không nháy gizmo.

### 2.8 VRAM
`MeshesToReplace` là Array hard ref → **clear ở Event End Play** (InputManager) + SET rỗng khi ExitReplaceMode.

---

## 3. LUỒNG THỰC THI NGƯỜI DÙNG

### CB_ChangeMaterial (single)
```
Select 1 đồ → Right-click → Change Material
→ Menu đóng, inventory mở tab Material, swatch slot hiện
→ Click slot → click material card → đồ đổi material (live) → debounce CaptureSnapshot
→ Đóng inventory, giữ material
```

### CB_Replace (MULTI — kịch bản select similar)
```
1. Select 1 ghế → Right-click → Select Similar → 5 ghế cùng model được chọn
2. Right-click → Replace
3. Menu đóng, inventory mở, lọc folder ghế, card hiện "Change Mesh"
4. Click "Change Mesh" trên ghế model khác
5. → CẢ 5 ghế đổi sang model mới, mỗi cái giữ vị trí/xoay riêng, material reset
6. → 5 đồ mới được chọn lại (outline + pivot), inventory vẫn mở (replace tiếp được)
7. Toggle off: bấm Replace lần nữa / deselect
```

---

## 4. LUỒNG THỰC THI CODE (node-level)

### 4.1 CB_ChangeMaterial (callback trong BP_FurnitureInputManager)
```
IsValid(ContextMenuRef) → Remove from Parent → SET None
Branch IsValid(PrimarySelectedActor): False → Return
[Đảm bảo inventory mở — nested Branch IsValid + Is In Viewport; đóng thì Create+AddViewport+ShowCursor+SET ref]
Cast InvRef → WBP_FurnitureInventory:
  Call SwitchInventoryMode(Material)
  Call OpenMaterialModeForActor(PrimarySelectedActor)   ← function tái dùng (mục 5.1)
```

### 4.2 CB_Replace (callback trong BP_FurnitureInputManager)

⚠️ **Cập nhật 24/07/2026 (C9.0c) — verified qua K2Node export thật** (Ctrl+A → Ctrl+C → paste,
không phải ảnh chụp). Bản dưới đây thay bản prep gốc (dùng `bIsReplaceMode` boolean đơn giản) —
as-built thật dùng `ReplaceTarget` (Enum `E_ReplaceTarget`, migrate C9.0c, xem
`Blueprints/BP_FurnitureInputManager.md` v2.4).

```
CB_Replace.then
▶→ Branch(IsValid ContextMenuRef)
     True ▶→ Remove from Parent(ContextMenuRef)
          ▶→ SET ContextMenuRef = None
          ▶→ Branch(IsReplaceModeActive)                ← FIX 24/07 (trước đó có Branch dư literal=true chặn đường)
               True (đang active — tắt) ▶→
                    SET ReplaceTarget = E_ReplaceTarget::None
                    ▶→ Clear Array(MeshesToReplace)
                    ▶→ Get Game Instance → Cast Foff_GameInstance
                         ▶→ Branch(IsValid FurnitureInventoryRef)
                              True ▶→ Branch(IsInViewport)
                                   True ▶→ ExitReplaceMode
                                   False ▶→ [dead-end]
                              False ▶→ [dead-end]
               False (chưa active — bật) ▶→
                    Branch(IsValid PrimarySelectedActor)
                         True ▶→ Branch(SelectedActors.Length > 0)
                              True ▶→ StartReplaceMode(Actors = SelectedActors)
                              False ▶→ [dead-end]
                         False ▶→ [dead-end]
     False ▶→ [dead-end]
```
Đã verify: mọi pin `then`/`execute` khớp `LinkedTo` 2 chiều, không còn node dư từ bug trước
(Branch dư literal=true chặn đường — đã fix cùng phiên).

> ⚠️ **Ghi chú KP3 (ngoài phạm vi cập nhật 24/07):** §5.2 bên dưới (`StartReplaceMode` trong
> planning gốc) vẫn còn mô tả `bIsReplaceMode` cũ — đây là bản PLAN gốc (đã bị as-built thật
> vượt qua từ lâu, xem `Blueprints/BP_FurnitureInputManager.md` mục StartReplaceMode cho bản
> đúng hiện tại). Không sửa §5.2 vì nằm ngoài phạm vi delta 24/07 (chỉ chỉ định §4.2).

### 4.3 Card BTN_ChangeMesh — NÂNG CẤP MULTI (WBP_DragOverlay_FurnitureCard)
```
Get InputManager → FurnitureInputRef
GET MeshesToReplace → Branch Length > 0? False → STOP

CLEAR LocalNewActors (local Array BP_FurnitureActor)

ForEach MeshesToReplace (OldActor):                      ← OUTER, multi
  Branch IsValid(OldActor):
    True →
      GET Actor Location(OldActor) → Loc
      GET Actor Rotation(OldActor) → Rot
      Cast OldActor → BP_FurnitureActor → GET PlacementSurfaceType → SurfType
      Spawn BP_FurnitureActor(Loc, Rot) → Cast → NewActor
        Load Asset Blocking(FurnitureDA.Mesh) → Cast StaticMesh → Get FurnitureMesh → Set Static Mesh
        SET MeshPath
        SET DAPath = Get Object Path(FurnitureDA)
        SET PlacementSurfaceType = SurfType
        GET Tags → ADD "FurnitureSpawned"
      ADD NewActor → LocalNewActors
      Destroy Actor(OldActor)

Completed:
  ← re-select nhóm mới (tái dùng multi-select)
  Cast FurnitureInputRef → DeselectAll → SelectActors(LocalNewActors)
  ← snapshot 1 lần
  Get All Actors Of Class(BP_UndoManager) → Get(0) → CaptureSnapshot("Replace")
  ← recent (1 lần)
  GET BP_FurnitureUserPrefsManager[0] → AddRecentMesh(String to Name(Get Object Name(FurnitureDA)))
  ← cập nhật target để replace tiếp
  Cast FurnitureInputRef → SET MeshesToReplace = LocalNewActors
  ← giữ Replace mode + inventory mở (như v1.3)
```
**So với bản single cũ:** bỏ phần tự set stencil 255 + ActivateGizmo thủ công (giờ `SelectActors` lo); CaptureSnapshot + AddRecent chuyển ra Completed (1 lần); thêm vòng ForEach.

---

## 5. FUNCTION TÁI DÙNG (chốt: làm cả 2)

### 5.1 `OpenMaterialModeForActor(Actor)` — trong WBP_FurnitureInventory
```
Branch IsValid(Actor):
  True → SET TargetFurnitureActor=Actor, Visible HB_SlotSwatches, SET SelectedSlotIndex=-1, Call RefreshSlotSwatches
  False → SET TargetFurnitureActor=None, Collapsed HB_SlotSwatches
```
→ `OnMeshSelected` (nhánh Material), `ApplyRestoredActor`, `CB_ChangeMaterial` đều gọi.

### 5.2 `StartReplaceMode(TargetActors : Array BP_FurnitureActor)` — trong BP_FurnitureInputManager
```
Branch bIsReplaceMode == True (self):
  True (toggle OFF) →
    SET bIsReplaceMode=False, CLEAR MeshesToReplace
    Get GameInstance→Cast→GET FurnitureInventoryRef→IsValid→Cast→ExitReplaceMode
    Return
  False (bật ON) →
    SET MeshesToReplace = TargetActors                  (copy)
    ← folder theo PrimarySelectedActor (= TargetActors LAST, hoặc primary)
    GET PrimarySelectedActor → Cast BP_FurnitureActor → GET DAPath
    Load Asset Blocking → Cast DA_FurnitureItem → GET MeshFolderPath → FolderPath
    [Đảm bảo inventory mở — nested Branch như 2.2]
    Cast InvRef → WBP_FurnitureInventory → Call EnterReplaceMode → Call FilterByFolderPathWithUI(FolderPath)
    ← bIsReplaceMode=True nằm trong EnterReplaceMode
```
**Trỏ lại các call site (câu 2 — sửa luôn):**
- `BTN_Replace OnClicked` (WBP_MeshControls) → `Get InputManager → StartReplaceMode(SelectedActors)`
- `CB_Replace` → `StartReplaceMode(SelectedActors)`
- `BTN_ChangeMesh OnClicked` (WBP_DetailPopup, single) → `StartReplaceMode( Make Array(SelectedFurnitureActor) )`

### 5.3 Migrate biến `MeshToReplace` → `MeshesToReplace` (Array)
**Touch points (đổi hết để 1 nguồn sự thật, tránh dual-state):**
| File | Chỗ | Đổi |
|---|---|---|
| BP_FurnitureInputManager | khai báo var | `MeshToReplace : BP_FurnitureActor` → `MeshesToReplace : Array of BP_FurnitureActor` |
| BP_FurnitureInputManager | Event End Play | thêm CLEAR MeshesToReplace |
| WBP_MeshControls | BTN_Replace | dùng StartReplaceMode (không SET trực tiếp nữa) |
| WBP_DetailPopup | BTN_ChangeMesh | StartReplaceMode(Make Array(SelectedFurnitureActor)) |
| WBP_FurnitureInventory | OnMeshSelected (replace branch) | SET MeshesToReplace = SelectedActors (thay SET single) |
| WBP_FurnitureInventory | OnMeshDeselected (exit replace) | CLEAR MeshesToReplace (thay SET None) |
| WBP_DragOverlay_FurnitureCard | BTN_ChangeMesh | dùng ForEach MeshesToReplace (mục 4.3) |

---

## 6. THỨ TỰ THỰC THI (vertical slice trước — validate rủi ro lớn nhất)

```
B0. Migrate var MeshToReplace → MeshesToReplace (Array) + tất cả touch point read/write (5.3).
    (Tạm thời các call site cũ SET MeshesToReplace = Make Array(actor) để không vỡ.)
B1. ⭐ VERTICAL SLICE — đổi card BTN_ChangeMesh thành ForEach multi (4.3).
    TEST NGAY: select 2 đồ CÙNG mesh (chưa cần Select Similar) → BTN_Replace cũ → click card →
    cả 2 đổi mesh, giữ vị trí riêng, 2 đồ mới được select, Undo khôi phục cả 2.
    ← Đây là rủi ro lớn nhất (spawn N/destroy N/re-select/1 snapshot). Pass mới đi tiếp.
B2. Tạo StartReplaceMode (5.2) + trỏ BTN_Replace (MeshControls) + DetailPopup về nó. TEST replace single + multi qua BTN_Replace.
B3. (5.1) Tạo OpenMaterialModeForActor + trỏ OnMeshSelected/ApplyRestoredActor về nó. TEST material mode chạy như cũ.
B4. CB_ChangeMaterial (4.1). TEST: right-click → Change Material.
B5. CB_Replace (4.2). TEST: Select Similar → Replace → click card → tất cả đổi.
B6. Update docs (BP_FurnitureInputManager, WBP_FurnitureInventory, WBP_MeshControls, WBP_DetailPopup, WBP_DragOverlay_FurnitureCard, Session_State, PROGRESS, DEVIATIONS).
```

---

## 7. TEST CASES

| # | Case | Kỳ vọng |
|---|---|---|
| 1 | Material: select 1 → Change Material (inv đóng) | Inv mở tab Material, swatch đúng |
| 2 | Material: inv đang mở tab Furniture → Change Material | Chuyển tab, không tạo widget mới |
| 3 | Material: đổi + Undo | Apply live + Undo về cũ |
| 4 | **Replace multi (slice B1):** 2 đồ cùng mesh → Replace → click card | Cả 2 đổi, giữ vị trí riêng, 2 mới được select |
| 5 | **Replace multi Undo** | Undo khôi phục cả 2 đồ cũ |
| 6 | **Select Similar → Replace → card** | TẤT CẢ đồ similar đổi mesh |
| 7 | Replace single (1 đồ) qua CB_Replace | Đổi 1 đồ như cũ |
| 8 | Replace nhóm hỗn hợp (box select khác mesh) → card | Tất cả đổi sang mesh mới (folder theo primary) |
| 9 | Toggle Replace lần 2 | Thoát mode, card ẩn Change Mesh, CLEAR MeshesToReplace |
| 10 | Đang Replace → deselect | Thoát mode (ExitReplaceMode + CLEAR) |
| 11 | Right-click khi 0 đồ chọn | Guard return, không crash |
| 12 | BTN_Replace (MeshControls) sau refactor | Vẫn chạy (single + multi) |
| 13 | BTN_ChangeMesh (DetailPopup) sau refactor | Vẫn chạy (single) |

---

## 8. GIẢI THÍCH CÂU HỎI 3 (mày bảo chưa hiểu)

**Câu hỏi gốc:** *Khi user right-click mà KHÔNG có đồ nào đang chọn — 2 item "Change Material" và "Replace" nên xử lý sao?*

2 lựa chọn:
- **(a) Ẩn/disable item:** khi 0 đồ chọn thì 2 dòng này không hiện trong menu (hoặc xám, bấm không được). Cần thêm logic dựng menu động.
- **(b) Guard return:** item vẫn hiện bình thường, nhưng nếu bấm lúc 0 đồ chọn thì callback kiểm tra `IsValid(PrimarySelectedActor)` → không hợp lệ → **return, không làm gì** (không crash, không mở inventory).

**Đề xuất của tao: (b) guard return** — đơn giản hơn, không phải code dựng menu động. Thực tế right-click thường nhằm vào đồ đang chọn nên hiếm khi gặp. Mày OK (b) hay muốn (a)?

---

## 9. FILE LIÊN QUAN
- `BP_FurnitureInputManager.md` v1.5 — context menu, ContextMenuRef, PrimarySelectedActor, MeshesToReplace (mới)
- `WBP_FurnitureInventory.md` — SwitchInventoryMode, OnMeshSelected/Deselected (replace+material branch), RefreshSlotSwatches, EnterReplaceMode/ExitReplaceMode, FilterByFolderPathWithUI, ApplyRestoredActor
- `WBP_MeshControls.md` v1.1 — BTN_Replace (→ StartReplaceMode)
- `WBP_DetailPopup.md` — BTN_ChangeMesh (→ StartReplaceMode single)
- `WBP_DragOverlay_FurnitureCard.md` — BTN_ChangeMesh (→ ForEach multi)
- `ChangeMaterial_Context_v1_1.md` — Material Picker, edge case reset material

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 07/06/2026 — 23:10 ICT | Spec ban đầu (Replace single) |
| 1.1 | 07/06/2026 — 23:30 ICT | **Chốt 3 câu:** Replace MULTI (ForEach SelectedActors, dùng cho Select Similar); sửa luôn BTN_Replace → StartReplaceMode; migrate MeshToReplace→MeshesToReplace (Array); card BTN_ChangeMesh nâng cấp multi (spawn N/destroy N/re-select via SelectActors/1 snapshot); vertical slice B1 validate trước; giải thích câu hỏi 3 (guard return) |
