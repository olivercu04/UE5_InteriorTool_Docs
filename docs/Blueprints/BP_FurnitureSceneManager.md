# BP_FurnitureSceneManager
**Tách từ:** `BP_FurnitureActor_SceneManager.md` (phần SceneManager)
**Cập nhật:** 24/08/2026 | Actor riêng — quản lý EMS Save/Load

---

## Variables
```
SaveGameMenuRef        : SaveGameMenu (Object Reference)
FurnitureInventoryRef  : WBP_FurnitureInventory (Object Reference)
ToastRef               : WBP_Toast (Object Reference)
```
> **[ĐÍNH CHÍNH 21/09/2026 — doc-drift]** `FurnitureInventoryRef` thực tế nằm ở đây, không phải
> thiếu trong BP thật — doc này trước giờ chỉ chưa liệt kê. Đích đã xác nhận 2 lần độc lập qua
> K2Node export thật (11/09/2026 S7.G5, 12/09/2026 G6.1) — KHÔNG phải `Foff_GameInstance` như
> `Planning/Architecture_Overview.md` v1.2 ghi trước đây (xem doc debt ở đó + `DEVIATIONS.md` #2).
> Widget/Actor khác lấy ref này qua `GetAllActorsOfClass(BP_FurnitureSceneManager)`, không qua
> GameInstance. Dùng ở: `RefreshSlotSwatches/HighlightSwatchByIndex/RefreshParamPanel` (từ
> `BP_FurnitureActor`), `ExitReplaceMode` (từ `BP_FurnitureInputManager`, `WBP_MeshControls`),
> Copy/Paste material (`Features/Material_CopyPaste.md`). `ToastRef` cùng đợt đính chính, cùng
> đích — `WBP_Toast` gọi qua `.ShowToast()` (doc gốc `Widgets/WBP_Toast.md` ghi trên
> `Foff_GameInstance`, cũng là doc debt tương tự).

---

## Components

- **PostProcess** (Post Process Component)
  - Unbound = True
  - Post Process Materials: [M_SelectionOutline]
  - Mục đích: thay thế PostProcessVolume actor không còn được đặt sẵn trong level của project tổng.
    Component gắn cứng qua Class Defaults, không cần node runtime nào set thêm.

---

## Event Tick
```
Get All Widgets Of Class(SaveGameMenu) → FoundWidgets
Branch Length(FoundWidgets) > 0:   ← PHẢI check trước GET(0)
  True → GET(0) → IsValid:
    True:
      Branch SaveGameMenuRef != Get(0):
        True:
          SET SaveGameMenuRef = Get(0)
          Bind OnLoadButtonClicked
```

---

## OnLoadButtonClicked
```
Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast → DeselectMesh
← PHẢI trước Destroy — deactivate gizmo trước khi actors bị destroy

Get All Actors With Tag("FurnitureSpawned") → For Each → Destroy Actor
```

---

## SaveFurnitureScene
```
Get Current Save Slot → Set Current Save Slot → Save Game Actors (Level Only)
```

---

## LoadFurnitureScene
```
Get Current Save Slot → Set Current Save Slot → Load Game Actors (Level Only, Full Reload = True)
```

---

## ResolveByPersistentId(Id : String) → (OutActor : BP_FurnitureActor, bFound : Bool)
**[✓K2 export 21/09/2026]** — verify từ K2Node export thật, khớp 100% spec thiết kế (U1.4).

```
Entry(Id)
▶→ Branch(Id == "")                          [EqualEqual_StrStr(A=Id, B="")]
     True  ▶→ SET OutActorLocalVar = None    (unconnected → default)
           ▶→ SET bFoundLocalVar = false     (literal)
           ▶→ Return(OutActor=OutActorLocalVar, bFound=bFoundLocalVar)

     False ▶→ Get All Actors With Tag("FurnitureSpawned")
           ▶→ ForEachLoopWithBreak(Array=OutActors)
                LoopBody ▶→ Cast To BP_FurnitureActor(ArrayElement)
                    Success ▶→ SET AsActor = AsBPFurnitureActor
                              ▶→ Branch(AsActor.PersistentID == Id)   [EqualEqual_StrStr]
                                   True  ▶→ SET OutActorLocalVar = AsActor
                                         ▶→ SET bFoundLocalVar = true (literal)
                                         ▶→ (exec → pin Break của macro)
                                   False → (dead-end, hợp lệ — nằm trong LoopBody, macro tự next)
                    Failed  → (dead-end, hợp lệ — tương tự)
                Completed ▶→ Return(OutActor=OutActorLocalVar, bFound=bFoundLocalVar)
```
Q8: Function (pure resolver) | Cast tự guard AsActor (không cần IsValid riêng) | L2: cả 2 Return
đều có đích, dead-end trong LoopBody hợp lệ vì macro tự resume | No Latent | 6A: N/A (đọc thuần).

---

## Lịch sử cập nhật
| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 05/05/2026 | Logic gốc — Event Tick rebind SaveGameMenu, OnLoadButtonClicked destroy + reload, Save/Load functions |
| 1.1 | 24/08/2026 | +mục Components — Post Process Component (Unbound=True, M_SelectionOutline) thay PostProcessVolume actor (không còn đặt sẵn trong level project tổng, Volume actor cần brush). Verify PASS trong Editor. |
| 1.2 | 21/09/2026 | +Function `ResolveByPersistentId` (U1.4, PersistentIdentity) — full node flow, verify từ K2 export thật. |

---

<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->

## 🧠 Kết nối (bản đồ não)

> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.

**Có mặt trong thao tác:** [[L09 · Đổi vật liệu|L09]] · [[L10 · Chỉnh thông số vật liệu|L10]] · [[L12 · Lưu và mở cảnh|L12]] · [[L13 · Hoàn tác và làm lại|L13]]

**Thuộc mảng kết nối:** [[Kết nối 3a - Chọn đồ Gizmo Nhóm]] · [[Kết nối 3d - Save Undo khởi động]] · [[Kết nối 3e - Vật liệu Material]]

**Gọi / điều khiển →**
- [[WBP_FurnitureInventory]] — gọi thoát Replace Mode · .FurnitureInventoryRef.ExitReplaceMode() ✓K2
- [[BP_FurnitureInputManager]] — yêu cầu bỏ chọn · DeselectMesh()
- [[BP_FurnitureActor]] — sinh / xoá đồ theo danh mục · Spawn / Destroy
- [[SaveGameMenu]] — giữ tham chiếu menu Save · SaveGameMenuRef

**← Được gọi bởi**
- [[BP_FurnitureInputManager]] — tìm singleton, đọc tham chiếu inventory · GetAllActorsOfClass, GET FurnitureInventoryRef ✓K2
- [[WBP_FOFF_ToolDemo]] — sinh ra · Spawn
- [[BP_UndoManager]] — tìm lại đồ theo ID khi undo/chốt param — caller đầu tiên của Resolver · ResolveByPersistentId() ✓K2
- [[SaveGameMenu]] — báo tin bấm Load · OnLoadButtonClicked
- [[WBP_DragOverlay_FurnitureCard]] — báo thả trúng kiến trúc · ToastRef.ShowToast() ✓K2

<!-- BRAIN:END -->
