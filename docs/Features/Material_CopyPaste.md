# Material Copy/Paste (Single-Slot) — v1
**Hoàn thành:** 02/06/2026 — 12:30 ICT | **Cập nhật:** 05/09/2026 — 19:55 ICT — S7.G2 Việc 4 as-built: chuyển nguồn đọc/ghi từ `MaterialOverrides` (chết từ Việc 2) sang `MaterialSlots` (qua `MaterialSlotService`), 2 bug thật fix trong phiên | Trên: master project
**Vị trí code:** WBP_FurnitureInventory

---

## MÔ TẢ

Copy vật liệu của **1 slot** trên mesh này → paste sang **1 slot** trên mesh khác (hoặc cùng mesh, slot khác). Khác với ý tưởng cũ (copy cả mảng slot theo index — vô nghĩa khi 2 mesh khác model).

**Workflow:**
1. Chọn mesh A → tab Material → chọn slot → Copy
2. Chọn mesh B → chọn slot → Paste

**Kích hoạt:** 2 nút (BTN_CopySlotMaterial/PasteSlotMaterial) + phím tắt Ctrl+Shift+C/V.

---

## VARIABLE

```
ClipboardMaterialPath : String   (WBP_FurnitureInventory)
PasteRowName : Name, default None   (WBP_FurnitureInventory)   ← [S7.G2 Việc 4, 05/09/2026]
  Không theo prefix chuẩn §9 (`Paste_RowName`) vì dùng lại ở 3 chỗ trong cùng event
  (ApplyLoadedMaterialToSlot / GetDataTableRow / AddRecentMaterial) — đặt tên trực tiếp
  cho rõ nghĩa, cuhoang đã duyệt.
```

---

## FUNCTION CopySlotMaterial (Function) — AS-BUILT 05/09/2026 (S7.G2 Việc 4)

> Bản cuối cùng, đã qua 2 lần vá trong phiên (xem "Bug thật bắt được" bên dưới). Nguồn đọc
> chuyển từ `MaterialOverrides` (chết từ Việc 2, reroute apply sang `MaterialSlots`) sang
> `MaterialSlots` qua `MaterialSlotService`. Ký hiệu: `▶→` exec, `●→` data.

```
Entry ▶→ Branch(IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0)
  True ▶→ Branch(SelectedSlotIndex < GetNumMaterials(FurnitureMesh))
     True ▶→ SET ClipboardMaterialPath = ""                          ← FIX Bug B (clear đầu hàm)
          ▶→ GET TargetFurnitureActor.MaterialSlots
          ▶→ ForEachLoopWithBreak(MaterialSlots → Record):
               Branch(Record.SlotName == SelectedSlotName):
                 True → Branch(Record.MaterialRowName != ""):
                          True  → GetDataTableRow(DT_MaterialInstancesCatalog, Record.MaterialRowName)
                                    Row Found     → MaterialPath ●→ SET ClipboardMaterialPath → Break
                                    Row Not Found → SET ClipboardMaterialPath = Record.MaterialPathFallback → Break
                          False → SET ClipboardMaterialPath = Record.MaterialPathFallback → Break
                 False → [dead-end — không phải slot đang tìm]
             Completed ▶→ Branch(ClipboardMaterialPath == "")
                            True  ▶→ SET ClipboardMaterialPath = GetPathName(GetMaterial(FurnitureMesh, SelectedSlotIndex))
                                    ▶→ Print "✅ Đã copy vật liệu slot: N"
                            False ▶→ ─────────────────────────────────────┘   ← FIX Bug A (hội tụ SAU node data)
     False → Print "Slot chưa có vật liệu để copy" (Dev Only)
```

⚠️ Luôn copy được — kể cả slot dùng vật liệu gốc (không có Record → fallback `GetPathName`).

---

## CUSTOM EVENT PasteSlotMaterial (Event — vì có Async Load) — AS-BUILT 05/09/2026 (S7.G2 Việc 4)

```
Entry ▶→ IsValid(TargetFurnitureActor) AND SelectedSlotIndex>=0 AND ClipboardMaterialPath != ""
  True ▶→ MakeSoftObjectPath(ClipboardMaterialPath) → Async Load Asset
       Completed ▶→ Cast To MaterialInterface → Branch(IsValid(MI))
          True ▶→ Branch(IsValid(TargetFurnitureActor))   [guard lặp có sẵn, giữ nguyên]
             True ▶→ ClipboardMaterialPath.ParseIntoArray(".") → LastIndex → Get → Conv_StringToName
                     ●→ SET PasteRowName
                  ▶→ ApplyLoadedMaterialToSlot(
                        Mesh = FurnitureMesh, Records = TargetFurnitureActor.MaterialSlots,
                        SlotName = SelectedSlotName, HintIndex = SelectedSlotIndex,
                        LoadedMI = MI, RowName = PasteRowName, PathFallback = ClipboardMaterialPath)
                  ▶→ GetDataTableRow(DT_MaterialInstancesCatalog, PasteRowName)
                        Row Found ▶→ UpdateThumbnail(...)
                  ▶→ ClearTimer + SetTimer("CaptureAfterPaste", 0.3s)
                  ▶→ GetAllActorsOfClass(BP_FurnitureUserPrefsManager) → Get(0) → AddRecentMaterial(PasteRowName)
             False → dead-end
          False → dead-end

CaptureAfterPaste (Event):
  Get All Actors Of Class(BP_UndoManager) → Get(0) → Cast → CaptureSnapshot("PasteMaterial")
```

### Bug thật bắt được trong phiên (05/09/2026, cả 2 do sửa sai lúc hướng dẫn, không phải lỗi thao tác)

**Bug A — Branch hội tụ SAI VỊ TRÍ (trước node data thay vì sau).** Hướng dẫn ban đầu nối cả 2
nhánh của `Branch(ClipboardMaterialPath == "")` vào chung 1 điểm TRƯỚC node
`SET...GetPathName(...)` → node đó chạy vô điều kiện, ghi đè luôn giá trị đúng vừa tìm từ Record
bằng material đọc thẳng từ mesh. Fix: dời điểm hội tụ ra SAU node đó, tại `Print`. Nguyên tắc:
khi 2 nhánh Branch cần tới cùng 1 đích nhưng chỉ 1 nhánh có node xử lý data ở giữa, điểm hội tụ
PHẢI đặt SAU node đó.

**Bug B — Class var persistent không CLEAR đầu hàm.** `ClipboardMaterialPath` không được reset
ở đầu `CopySlotMaterial` → copy slot chưa từng đổi (không có Record) rơi vào nhánh
`Branch(ClipboardMaterialPath == "") = False` (vì biến còn mang rác từ lần Copy trước) → giữ
nguyên giá trị cũ, báo "✅ Đã copy" giả. Fix: thêm `SET ClipboardMaterialPath = ""` đầu hàm.
Đây là vi phạm rule ĐÃ CÓ SẴN "CLEAR class var persistent ở đầu function", không phải phát hiện
mới. Chi tiết đầy đủ 2 bug: `DEVIATIONS.md`, nguồn `DELTA_S7G2_Viec4_CopyPaste_AsBuilt_05sep2026`.

Test PASS 05/09/2026: copy slot nguyên bản → paste mesh khác; copy slot đã đổi (qua Việc 2/3) →
paste mesh khác, đối chiếu `MaterialSlots`/JSON; thumbnail + Recent Material cập nhật đúng; copy
slot 1 (đã đổi) → paste → copy slot 5 (chưa đổi) → paste → đúng theo lần copy mới nhất (sau fix
Bug B); nhiều đường thao tác tự do không phát hiện lỗi mới.

---

## INPUT

```
IA_CopySlotMaterial  (Digital bool) — Ctrl+Shift+C
IA_PasteSlotMaterial (Digital bool) — Ctrl+Shift+V
```

LM_FurnitureInput mapping: C/V + Chord IA_Ctrl + Chord IA_Shift.

BP_FoffPlayerController binding:
```
IA_CopySlotMaterial (Started):
  GameInstance → FurnitureInventoryRef → IsValid → Cast → CopySlotMaterial

IA_PasteSlotMaterial (Started):
  GameInstance → FurnitureInventoryRef → IsValid → Cast → PasteSlotMaterial
```

---

## XUNG ĐỘT PHÍM — Fix quan trọng

Ctrl+Shift+V ban đầu trigger CẢ IA_FurniturePaste (mesh) lẫn IA_PasteSlotMaterial.

**Fix:** trong binding IA_FurnitureCopy + IA_FurniturePaste (paste/copy MESH), thêm Shift check:
```
IA_FurniturePaste (Started):
  Branch Is Input Key Down(Shift):
    True  → return  ← Shift = material, bỏ qua mesh
    False → PasteMesh
```

⚠️ **Learning:** dùng Shift check trong binding, KHÔNG cần block mapping (dòng phím không trigger). Pattern giống Ctrl+Z vs Ctrl+Shift+Z.

---

## NODE MỚI GHI NHẬN

- **Get Object Path Name** — lấy path asset dạng `/Game/.../MI.MI` từ object (dùng cho material gốc)
- **Create Dynamic Material Instance** (Target = Primitive Component) — vừa tạo DMI vừa set vào element, KHÔNG cần Set Material riêng
- **ParseIntoArray** — tách string bằng delimiter (lấy tên asset từ path)

---

## BACKLOG LIÊN QUAN

**Slot Material Highlight trên mesh:** chọn slot → phần mesh sáng lên. Swap M_SlotHighlight tạm, restore khi bỏ chọn. Bẫy: không lọt save/undo. Làm sau Phase 2.
