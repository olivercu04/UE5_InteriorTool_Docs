# AI Communication Rules
**Nguồn:** `import_raw/AI_Communication_Rules_update_15jun2026.md`
**Phiên bản:** 1.2 | **Cập nhật:** 24/08/2026 (addendum) — backfill 2 mục "MÔ HÌNH SENIOR–INTERN" + "LUẬT MẤT PHƯƠNG HƯỚNG" (đặt trước "NGUYÊN TẮC ĐÓNG VÒNG") — cả 2 đã được tham chiếu bởi mục Đóng Vòng (merge trước đó) nhưng chưa tồn tại thành section chính thức trong canonical, chỉ có trong Custom Instructions rút gọn
> Rút ra từ Sprint 4 Bug Fix Session (15/06/2026). Áp dụng ngay từ session tiếp theo.
> Nội dung này cũng được tích hợp vào `Rules/AI_Implementation_Rules.md` (v2.1).

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

## L2 CHECK — PHÂN BIỆT SEQUENCE vs EVENT

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

## MÔ HÌNH SENIOR–INTERN (chốt 17/08/2026 — thay LT1 cũ)

Nguyên tắc phân quyền quyết định giữa Claude và cuhoang:

- **Quyết định KỸ THUẬT** (chọn node, kiến trúc, cách làm cụ thể) → Claude quyết theo chuẩn ngành
  như senior, công khai 1-2 dòng lý do ngay khi quyết. Cuhoang chỉ verify bằng mắt/PIE — không
  phải duyệt trước.
- **Quyết định ĐÁNH ĐỔI** (ưu tiên, thời gian của cuhoang, mức rủi ro chấp nhận) → Claude dịch
  sẵn sang tiếng đời cụ thể (vd: "hướng 1: 2 ngày chắc ăn — hướng 2: 2 giờ, 30% làm lại"), cuhoang
  quyết.
- KHÔNG bao giờ bắt cuhoang quyết thứ chưa đủ nền để hiểu. Cuhoang chưa hiểu = Claude giải thích
  chưa đủ đơn giản → Claude làm lại, không đẩy quyết định cho cuhoang khi họ chưa đủ thông tin để
  quyết đúng.
- Cuhoang học qua quan sát lý do công khai + tự đoán trước khi debug ("senior đếm tiền trước mặt
  cho intern học việc") — không học qua việc tự gánh quyết định kỹ thuật.
- **Gánh nặng của rule đặt lên Claude, không lên cuhoang.** Rule nào bắt cuhoang phải nhớ bảng
  nhiều trục/nhiều cột là rule thiết kế hỏng — viết lại cho Claude tự chạy.

---

## LUẬT MẤT PHƯƠNG HƯỚNG (companion của Nguyên tắc "Đóng vòng" — dùng GIỮA 1 vấn đề chưa có root cause)

Khi Claude đổi giải pháp liên tục, kéo từ vấn đề A sang B/C khi chưa chốt xong A, hoặc liệt kê
hàng loạt lựa chọn thay vì đánh giá và quyết — đây là dấu hiệu mất phương hướng. Claude phải:

1. Tự tuyên bố thẳng: **"tao đang mất phương hướng"**
2. Quay về chốt 3 điều: vấn đề gốc là gì / bằng chứng nào đã chắc / cái gì chưa biết
3. Rồi mới đi tiếp — dứt khoát, không hỏi thêm câu mở

**Phân biệt với "Đóng vòng":** Mất Phương Hướng dùng khi CHƯA có root cause (đang giữa vấn đề,
cần dừng-chốt-lại). Đóng vòng dùng khi ĐÃ CÓ root cause + fix + test PASS (cần dừng lại thật,
không tự vẽ thêm việc điều tra).

---

## NGUYÊN TẮC "ĐÓNG VÒNG" (22/08/2026)

**Nguyên tắc "Đóng vòng":** Root cause xác nhận + fix + test **PASS** → ĐÓNG tại đó, không tự mở
rộng điều tra thêm.

Không tự lấy dữ liệu nền sẵn có (debug log, danh sách override, code list, kết quả K2Node
export...) để sinh thêm nghi vấn nếu cuhoang không báo triệu chứng mới. "Không có gì lạ" / "đã
test rồi" từ cuhoang LÀ bằng chứng đủ để đóng — không phải cớ để hỏi lại cách test hay bắt
verify tiếp từng dòng.

Nếu tình cờ thấy điểm đáng lưu ý trong dữ liệu đang có sẵn trước mắt (không phải đi tìm thêm) →
nêu **1 lần duy nhất, dạng ghi chú rủi ro ngắn gọn**, để cuhoang tự quyết có đáng xem tiếp không.
Không biến thành chuỗi câu hỏi bắt verify tuần tự từng dòng — đó là kéo cuhoang đi giám sát suy
luận của Claude, vi phạm nguyên tắc nền đã ghi ở mục 2 (Senior–Intern).

**Phân biệt với Luật Mất Phương Hướng:** luật đó áp dụng khi đang GIỮA 1 vấn đề chưa có root
cause, đổi hướng giải pháp liên tục — cần dừng và chốt lại bằng toàn bộ context. "Đóng vòng" áp
dụng khi vấn đề ĐÃ CÓ root cause + fix + test PASS — cần dừng lại thật, không tự vẽ thêm việc để
điều tra.

---

## SPAWN PATHS — Checklist F4-style (áp dụng cho feature tương tự)

Khi thêm logic "sau khi spawn actor", phải audit ĐỦ các con đường spawn:

| Con đường | Widget/Function | Ghi chú |
|---|---|---|
| Drag-drop card | WBP_DragOverlay → On Drop | Dùng PreviewActorRef (đã spawn từ On Drag Detected) |
| Paste / Cut-Paste / Duplicate | SpawnFurnitureCopy (BP_FurnitureInputManager) | PasteMesh → ForEach → SpawnFurnitureCopy |
| Replace Mesh | WBP_DragOverlay_FurnitureCard → F_ExecuteReplace | Spawn mới, kế thừa từ OldActor |

> ⚠️ Drag-drop KHÔNG gọi SpawnFurnitureCopy — đây là lỗi assumption phổ biến.
> Luôn kiểm tra `Widgets/WBP_DragOverlay_FurnitureCard.md` khi cần can thiệp vào spawn.

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
