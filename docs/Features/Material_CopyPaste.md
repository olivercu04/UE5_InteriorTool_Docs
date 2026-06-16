# Material Copy/Paste (Single-Slot) — v0
**Hoàn thành:** 02/06/2026 — 12:30 ICT | Trên: master project
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
```

---

## FUNCTION CopySlotMaterial (Function)

```
Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0:
  True:
    Cast → BP_FurnitureActor → GET FurnitureMesh
    Branch SelectedSlotIndex < Get Num Materials(FurnitureMesh):
      True:
        GET MaterialOverrides[SelectedSlotIndex] → matPath
        Branch matPath != "":
          True  → SET ClipboardMaterialPath = matPath
          False → ← slot dùng vật liệu gốc
                   Get Material(FurnitureMesh, SelectedSlotIndex)
                   → Get Object Path Name → SET ClipboardMaterialPath
        Print "✅ Đã copy vật liệu slot N"
```

⚠️ Luôn copy được — kể cả slot dùng vật liệu gốc (lấy qua Get Object Path Name).

---

## CUSTOM EVENT PasteSlotMaterial (Event — vì có Async Load)

```
Branch IsValid(TargetFurnitureActor) AND SelectedSlotIndex >= 0
       AND ClipboardMaterialPath != "":
  True:
    Cast → BP_FurnitureActor → GET FurnitureMesh
    Make Soft Object Path(ClipboardMaterialPath) → To Soft Object Ref
    → Async Load Asset → Completed:
        Loaded Asset → Cast To Material Interface → MI_Source
        Create Dynamic Material Instance
          (Target=FurnitureMesh, Element Index=SelectedSlotIndex,
           Source Material=MI_Source)   ← node này vừa tạo DMI vừa set
        Set Array Elem (MaterialOverrides, SelectedSlotIndex, ClipboardMaterialPath)
        [Refresh slot swatch thumbnail — copy từ ApplyMaterial]
        [AddRecentMaterial: ParseIntoArray(path, ".") → last → Name → AddRecentMaterial]
        Clear Timer + Set Timer "CaptureAfterPaste" 0.3s
        Print "✅ Dán vật liệu slot N"

CaptureAfterPaste (Event):
  Get All Actors Of Class(BP_UndoManager) → Get(0) → Cast → CaptureSnapshot("PasteMaterial")
```

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
