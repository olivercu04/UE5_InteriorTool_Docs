# AI Communication Rules — UPDATE (15/06/2026)
> Thêm vào 09_AI_Implementation_Rules.md. Áp dụng ngay từ session tiếp theo.
> Đây là các quy tắc rút ra từ Sprint 4 Bug Fix Session (15/06/2026).

---

## Q8 SELF-CHECK GATE — MỞ RỘNG (bắt buộc từ 15/06)

Trước MỌI node flow, Sonnet PHẢI viết 1 dòng self-check VISIBLE, bao gồm ĐỦ 5 điểm:

```
Q8: [Container=Function/Event] | [IsValid guards] | [L2: mọi nhánh có đích] | [No Latent] | [6A: reverse path]
```

Ví dụ viết đúng:
```
Q8: Custom Event → class var OK | IsValid InputManager ✓ | L2: False branch merge về CaptureSnapshot ✓ | No latent ✓ | 6A: Undo khôi phục đúng ✓
```

**Không được viết:** "Tao đã check Q8" mà không liệt kê cụ thể.

---

## L2 CHECK — PHÂN BIỆT SEQUENCE vs EVENT (BẮT BUỘC)

Khi viết Branch bất kỳ, xác định context trước:

### Trong Sequence.Then:
```
Branch False → dead-end → ✅ HỢP LỆ
Sequence tự kích hoạt Then tiếp theo.
```

### Trong Event/Custom Event chain (KHÔNG trong Sequence):
```
Branch False → dead-end → ❌ FATAL
Logic sau Branch (nodes tiếp theo) sẽ KHÔNG chạy.
```

**Test nhanh:** "Nếu exec dừng ở đây, node nào sau Branch sẽ không chạy?"
- Nếu có node quan trọng (CaptureSnapshot, RemoveFromParent, Return Node...) → phải merge.
- Nếu không có gì sau → dead-end OK.

**Bài học 15/06:** False dead-end trong OnDrop (Event) → OnDrop return false → UMG destroy PreviewActorRef → mesh biến mất.

---

## BLUEPRINT EXPORT METHOD (phương pháp debug mới)

**Khi nào dùng:** Debug logic phức tạp (nhiều node, wire routing không rõ từ screenshot).

**Cách làm:**
1. Mày select nodes cần debug trong Blueprint Editor
2. Edit → Copy (Ctrl+C)
3. Paste vào chat (K2Node text)
4. AI đọc pin `LinkedTo` để trace exec + data connections

**Ưu điểm phát hiện được:**
- `LinkedTo=()` (empty) = dead-end exec
- `DefaultValue="false"` trên condition = bug logic
- `LinkedTo=(WrongNode ...)` = data wire sai
- `ErrorMsg="..."` = warning/error từ compiler
- Hai nodes cùng `LinkedTo` vào 1 exec pin = merge point

**Chú ý:** AI sẽ gọi node bằng **display name** (UE5 UI), không phải internal class name:
- `K2Node_IfThenElse` → **Branch**
- `K2Node_Knot` → **Reroute node**
- `K2Node_MacroInstance (ForEachLoop)` → **For Each Loop**
- `K2Node_CallArrayFunction (Array_Add)` → **ADD (Array)**
- `K2Node_DynamicCast` → **Cast To [ClassName]**

---

## SPAWN PATHS — Checklist F4-style (áp dụng cho feature tương tự)

Khi thêm logic "sau khi spawn actor", phải audit ĐỦ các con đường spawn:

| Con đường | Widget/Function | Ghi chú |
|---|---|---|
| Drag-drop card | WBP_DragOverlay → On Drop | Dùng PreviewActorRef (đã spawn từ On Drag Detected) |
| Paste / Cut-Paste / Duplicate | SpawnFurnitureCopy (BP_FurnitureInputManager) | PasteMesh → ForEach → SpawnFurnitureCopy |
| Replace Mesh | WBP_DragOverlay_FurnitureCard → F_ExecuteReplace | Spawn mới, kế thừa từ OldActor |

> ⚠️ Drag-drop KHÔNG gọi SpawnFurnitureCopy — đây là lỗi assumption phổ biến.
> Luôn kiểm tra doc WBP_DragOverlay_FurnitureCard.md khi cần can thiệp vào spawn.

---

## RUNTIME STATE vs SNAPSHOT STATE

**Nguyên tắc (rút ra từ A12):** Mọi state cần khôi phục qua Undo phải nằm trong `S_SceneSnapshot`.

**Checklist khi thêm state mới:**
- [ ] State này có cần undo-able không?
- [ ] Nếu có → thêm field vào `S_SceneSnapshot` + CaptureSnapshot capture + RestoreSnapshot restore
- [ ] Restore TRƯỚC bất kỳ function nào đọc state đó (ví dụ: SET EditModeStack trước ValidateEditMode)
- [ ] Bump `Version` nếu field mới ảnh hưởng restore behavior

**Ví dụ:**
- `Groups` → ✅ Trong snapshot V3
- `EditModeStack` → ✅ Trong snapshot V4 (15/06/2026)
- `bIsReplaceMode` → ❌ Không cần undo (Gate 1 bIsRestoring khác)
