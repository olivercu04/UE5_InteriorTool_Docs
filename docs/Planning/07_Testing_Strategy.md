# 07 — Testing Strategy
**Mục đích:** Test cases cụ thể cho từng sprint, cách verify không phá vỡ tính năng cũ.

---

## NGUYÊN TẮC TEST

### 1. Test sau mỗi task nhỏ, không đợi cuối sprint
Mỗi task trong 04_Sprint_Details.md có dòng "Test:" — chạy ngay sau khi xong task đó. Bug phát hiện sớm dễ fix hơn nhiều.

### 2. Regression test — đảm bảo không phá tính năng cũ
Mỗi sprint mới phải chạy lại "Core Regression Suite" (bên dưới) để đảm bảo tính năng đã có vẫn hoạt động.

### 3. Debug bằng Print String
Theo phong cách dự án — chèn Print String tại điểm nghi ngờ, kiểm tra giá trị runtime. Xóa sau khi xong.

### 4. Test trên máy yếu
Ưu tiên hiệu năng máy người dùng bình thường — test với scene 50+ actors, kiểm tra FPS không tụt.

---

## CORE REGRESSION SUITE

Chạy bộ test này **đầu mỗi sprint** để xác nhận nền tảng còn nguyên vẹn:

### RS1 — Single Select cơ bản
- [ ] Click 1 đồ → outline xanh hiện
- [ ] Click đồ khác → đồ cũ tắt outline, đồ mới hiện
- [ ] Click vùng trống → deselect

### RS2 — Gizmo
- [ ] Chọn đồ → bấm Move → gizmo translation hiện
- [ ] Kéo trục X → đồ di chuyển theo X
- [ ] Bấm Rotate → xoay đúng chiều
- [ ] Bấm Scale → scale đúng

### RS3 — Undo/Redo
- [ ] Move đồ → Alt+Z → về vị trí cũ
- [ ] Shift+Alt+Z → redo về vị trí mới
- [ ] Spawn → Undo → đồ biến mất → Redo → đồ trở lại

### RS4 — Save/Load
- [ ] Bày 5 đồ → Save → restart PIE → Load → 5 đồ đúng vị trí
- [ ] Material đã đổi → Save → Load → material giữ nguyên

### RS5 — Material v1.1
- [ ] Chọn đồ → tab Material → click swatch → material apply
- [ ] Reset slot → về material gốc
- [ ] Undo material → về material trước

### RS6 — Copy/Paste/Nudge (B1/B2)
- [ ] Ctrl+C → Ctrl+V → đồ paste tại cursor
- [ ] Ctrl+D → duplicate cạnh đồ gốc
- [ ] Arrow keys → nudge theo SnapStep

⚠️ Nếu bất kỳ RS test nào fail sau khi thêm code sprint mới → STOP, đó là regression bug.

---

## SPRINT 1 — MULTI-SELECT TEST

### Functional Tests

**T1.1 — Ctrl+Click Multi-Select**
- [ ] Click đồ A → A outline đậm (Stencil 255)
- [ ] Ctrl+Click đồ B → A nhạt (254), B đậm (255)
- [ ] Ctrl+Click đồ C → A,B nhạt, C đậm
- [ ] Ctrl+Click đồ A (đã chọn) → A bỏ chọn, B,C còn lại

**T1.2 — Primary Tracking**
- [ ] Chọn A,B,C → Primary = C (đồ chọn cuối)
- [ ] Ctrl+Click bỏ C → Primary = B
- [ ] Verify outline: Primary luôn đậm hơn

**T1.3 — Multi-Move qua Pivot**
- [ ] ⚠️ TRƯỚC TIÊN (R5b): multi-select 2 đồ → gizmo CÓ hiện trên Pivot không? CÓ kéo được không?
       (Nếu không → gizmo disable collision Pivot → fix ActivateGizmo whitelist "FurniturePivot")
- [ ] Chọn 5 đồ → Move mode → gizmo hiện ở center
- [ ] Kéo gizmo → 5 đồ di chuyển giữ khoảng cách tương đối
- [ ] Kiểm tra: không đồ nào bị lệch khỏi formation

**T1.4 — Multi-Rotate**
- [ ] Chọn 3 đồ thẳng hàng → Rotate 90° → 3 đồ xoay quanh center, vẫn thẳng hàng (theo trục mới)

**T1.5 — Multi-Scale**
- [ ] Chọn 4 đồ → Scale 2x → khoảng cách giữa đồ tăng 2x, mỗi đồ to 2x

**T1.6 — Multi-Nudge**
- [ ] Chọn 5 đồ → Arrow Right → tất cả nudge phải cùng bước
- [ ] SnapStep = 0 → giữ Arrow → di chuyển liên tục

**T1.7 — Multi-Copy/Paste**
- [ ] Chọn 3 đồ → Ctrl+C → Ctrl+V → 3 đồ mới tại cursor, giữ formation
- [ ] Verify: material của 3 đồ copy đúng

**T1.8 — Multi-Duplicate**
- [ ] Chọn 3 đồ → Ctrl+D → 3 đồ nhân đôi cạnh nhóm gốc

**T1.9 — Multi-Delete**
- [ ] Chọn 5 đồ → Delete → confirm dialog "Xóa 5 vật thể?" → Yes → biến mất
- [ ] Chọn 2 đồ → Delete → không có dialog (≤3) → biến mất luôn

**T1.10 — Ctrl+A**
- [ ] Bày 10 đồ → Ctrl+A → tất cả outline
- [ ] Ctrl+A → Delete → scene trống

**T1.11 — Selection Info Bar**
- [ ] Chọn 1 đồ → không hiện count
- [ ] Chọn 2+ đồ → hiện "✦ N vật thể"

### Undo/Redo Tests

**T1.12 — Multi-select Undo**
- [ ] Chọn 4 đồ → Move → Alt+Z → 4 đồ về cũ + vẫn được chọn
- [ ] Chọn 4 đồ → Delete → Alt+Z → 4 đồ trở lại + reselected
- [ ] Multi-paste → Alt+Z → các đồ paste biến mất

**T1.13 — Backward Compat (Version 1 save)**
- [ ] Load save tạo từ trước Sprint 1 → vẫn hoạt động (single select restore)

### Edge Cases

**T1.14 — Pivot Cleanup**
- [ ] Multi-select → Save → Load → kiểm tra KHÔNG còn BP_PivotActor orphan
- [ ] Multi-select → Esc → Pivot bị destroy
- [ ] Multi-select → chọn xuống 1 đồ → Pivot destroy, gizmo về đồ đơn

**T1.15 — Performance**
- [ ] Ctrl+A trên scene 50 đồ → outline update < 100ms
- [ ] Multi-move 50 đồ → FPS không tụt dưới 30

---

## SPRINT 2 — BOX SELECT + CONTEXT MENU TEST

**T2.1 — Box Select cơ bản**
- [ ] Kéo khung trên vùng trống → rectangle xanh hiện
- [ ] Thả → đồ trong khung được chọn
- [ ] Đồ nằm 1 phần trong khung → vẫn chọn (hoặc theo rule center)
- [ ] ⚠️ Đồ lớn (sofa) có origin ở góc, 90% thân trong khung nhưng origin ngoài
       → kiểm tra có chọn không. Nếu KHÔNG → cân nhắc project bounding box thay vì 1 điểm Location

**T2.2 — Box Select + Ctrl**
- [ ] Đã chọn 2 đồ → Ctrl + kéo khung → thêm đồ trong khung vào selection

**T2.3 — Box vs Gizmo (R7)**
- [ ] Đang có gizmo → click chính xác trục X → move, KHÔNG trigger box select
- [ ] Click vùng trống xa gizmo → box select

**T2.4 — DPI Test (R8)**
- [ ] Test trên màn 4K (DPI 150-200%) → rectangle chính xác với cursor

**T2.5 — Context Menu trên đồ**
- [ ] Right-click đồ → menu 8 mục hiện tại cursor
- [ ] Click "Sao chép" → copy hoạt động
- [ ] Click ngoài menu → menu đóng

**T2.6 — Context Menu vùng trống**
- [ ] Right-click vùng trống → menu 5 mục (Paste, Undo, Redo, Select All...)

**T2.7 — Select Similar**
- [ ] Bày 6 ghế giống + 3 bàn → right-click ghế → Select Similar → Same Mesh → 6 ghế chọn
- [ ] Same Category → tất cả "Ghế" category chọn

**T2.8 — Invert / Cut**
- [ ] Chọn 1 đồ → Ctrl+I → tất cả trừ đồ đó chọn
- [ ] Chọn đồ → Ctrl+X → cắt → Ctrl+V → paste lại

---

## SPRINT 3 — GROUP TEST

**T3.1 — Tạo Group**
- [ ] Chọn 6 đồ → Ctrl+G → dialog hiện → nhập tên → OK
- [ ] Verify: 6 đồ giờ có GroupID giống nhau

**T3.2 — Group Selection**
- [ ] Click 1 đồ trong group → cả 6 đồ chọn
- [ ] Verify info bar: "📦 [Tên nhóm] (6 vật thể)"

**T3.3 — Group Transform**
- [ ] Move group → 6 đồ di chuyển cùng
- [ ] Rotate group → 6 đồ xoay quanh center
- [ ] Scale group → 6 đồ scale từ center

**T3.4 — Ungroup**
- [ ] Chọn group → Ctrl+Shift+G → 6 đồ thành riêng lẻ
- [ ] Verify: GroupID của 6 đồ = ""

**T3.5 — Group Save/Load (R3)**
- [ ] Tạo group → Save → restart PIE → Load → group khôi phục
- [ ] Verify: click 1 đồ → cả group chọn (group structure preserved)

**T3.6 — Group Undo/Redo**
- [ ] Create group → Alt+Z → group hủy (đồ về riêng lẻ)
- [ ] Shift+Alt+Z → group tạo lại
- [ ] Ungroup → Undo → group khôi phục

**T3.7 — Group Delete**
- [ ] Chọn group → Delete → cả group biến mất
- [ ] Undo → group + đồ trở lại

---

## SPRINT 4 — EDIT MODE + NESTED TEST

**T4.1 — Edit Mode Entry**
- [ ] Double-click group → vào edit mode → đồ ngoài mờ đi
- [ ] Info bar: "✏️ Đang chỉnh: [Tên nhóm]"

**T4.2 — Edit từng đồ trong group**
- [ ] Trong edit mode → click 1 đồ → chỉ đồ đó chọn (không phải cả group)
- [ ] Move đồ đó → chỉ đồ đó di chuyển

**T4.3 — Exit Edit Mode**
- [ ] Esc → thoát edit mode → đồ ngoài hết mờ
- [ ] Click ngoài group → thoát edit mode

**T4.4 — Nested Group**
- [ ] Tạo group A (3 đồ) → tạo group B (2 đồ) → chọn A+B → Ctrl+G → group C chứa A,B
- [ ] Click 1 đồ → chọn cả C (top level)
- [ ] Double-click → vào C → thấy A, B
- [ ] Double-click A → vào A → thấy 3 đồ

**T4.5 — Nested Navigation**
- [ ] Trong A (cấp 2) → Esc → về C (cấp 1)
- [ ] Esc → thoát hẳn

**T4.6 — Circular Prevention (R6)**
- [ ] Tạo A chứa B → cố đặt A làm con B → bị reject + toast error

---

## SPRINT 5 — COMBO MESH TEST

**T5.1 — Lưu Combo**
- [ ] Tạo group bàn ăn → right-click → "Lưu Combo" → dialog → nhập info → Lưu
- [ ] Verify: combo xuất hiện trong category Combo

**T5.2 — Combo Thumbnail**
- [ ] Sau lưu → thumbnail auto-gen hiện đúng (không đen)

**T5.3 — Spawn Combo**
- [ ] Click combo card → spawn tại viewport
- [ ] Verify: tất cả mesh + group structure spawn đúng

**T5.4 — Combo Material**
- [ ] Đổi material trong group → lưu combo → spawn → material giữ đúng

**T5.5 — Combo Group Preserved**
- [ ] Spawn combo có nested group → verify hierarchy đúng
- [ ] Combo spawn 2 lần → 2 group riêng biệt (GroupID khác nhau, không conflict)

**T5.6 — Combo Save/Load**
- [ ] Spawn combo → Save scene → Load → combo's actors + groups khôi phục

---

## SPRINT 6 — POLISH UX TEST

**T6.1 — Lock/Unlock**
- [ ] Chọn đồ → Ctrl+L → khóa → click không chọn được
- [ ] Right-click đồ khóa → "Mở khóa" → mở
- [ ] Box select bỏ qua đồ khóa
- [ ] Ctrl+A bỏ qua đồ khóa

**T6.2 — Lock Save/Load**
- [ ] Khóa đồ → Save → Load → đồ vẫn khóa

**T6.3 — Align**
- [ ] Chọn 4 đồ lệch → Căn trái → 4 đồ thẳng cạnh trái
- [ ] Căn giữa ngang/dọc → đúng
- [ ] Reference "Theo đồ chọn đầu" → căn theo Primary

**T6.4 — Distribute**
- [ ] Chọn 5 đồ khoảng cách lệch → Phân bố đều ngang → khoảng cách bằng nhau

**T6.5 — Scene Outliner**
- [ ] Bấm O → outliner hiện danh sách scene
- [ ] Click item → đồ chọn + camera focus
- [ ] Icon ổ khóa → toggle lock
- [ ] Icon mắt → toggle visibility
- [ ] Đồng bộ 2 chiều: chọn viewport → outliner highlight

**T6.6 — Focus (F)**
- [ ] Chọn đồ → F → camera zoom về đồ
- [ ] Chọn group → F → camera fit cả group

**T6.7 — Smart Snap**
- [ ] Kéo đồ gần cạnh đồ khác → guideline xanh hiện → snap thẳng hàng
- [ ] Giữ Alt → tắt smart snap tạm thời

**T6.8 — Array/Pattern**
- [ ] Chọn 1 đồ → "Tạo hàng" → 6 cái, cách 80cm → spawn + auto group

---

## SPRINT 7 — MATERIAL EDIT v1.2 TEST

**T7.1 — Color Picker**
- [ ] Chọn đồ → tab Material → chọn slot → Color picker → đổi màu → mesh đổi màu live

**T7.2 — Roughness/Metallic**
- [ ] Slider Độ nhám → mesh bóng/mờ thay đổi live
- [ ] Slider Độ kim loại → hiệu ứng kim loại thay đổi

**T7.3 — Multi-apply**
- [ ] Chọn 3 đồ → đổi màu → cả 3 đổi cùng màu

**T7.4 — Reset**
- [ ] Đổi màu/roughness → "Đặt lại mặc định" → về param gốc

**T7.5 — Material Param Save/Load/Undo**
- [ ] Đổi màu → Save → Load → màu giữ đúng
- [ ] Đổi roughness → Undo → về giá trị trước

---

## INTEGRATION TEST (Cuối toàn bộ)

Test kịch bản thực tế phức hợp:

**IT1 — Workflow đầy đủ**
1. Bày phòng khách: sofa, bàn trà, 2 ghế, đèn, cây
2. Multi-select sofa + 2 ghế → Group "Bộ sofa"
3. Đổi material vải sofa → màu xanh navy
4. Align bàn trà giữa sofa
5. Group tất cả → "Phòng khách"
6. Lưu Combo "Phòng khách Modern"
7. Save scene → Load → verify mọi thứ đúng
8. Spawn combo "Phòng khách Modern" lần 2 ở vị trí khác
9. Undo 5 bước → Redo 5 bước → verify ổn định

**IT2 — Stress Test**
- [ ] Scene 100 actors, 10 groups, 5 nested → tất cả thao tác mượt
- [ ] 50 lần undo/redo liên tục → không crash, không leak

**IT3 — VRAM Test (theo Bug_GPU_VRAM_Crash.md)**
- [ ] PIE 3 lần liên tục với multi-select + group + combo → monitor VRAM
- [ ] Verify Event End Play clear refs (Pivot, Groups, Selection arrays)

---

## TEST AUTOMATION (tương lai)

Hiện tại test manual. Khi có thời gian, automation:

**Functional Test Blueprint:**
- Tạo BP_TestRunner actor
- Spawn N actors → multi-select → assert SelectedActors.Length == N
- Move → assert positions changed
- Undo → assert positions reverted

**Không ưu tiên** — manual test đủ cho giai đoạn này. Automation chỉ đáng làm khi codebase ổn định và team lớn hơn.

---

## DEBUG CHECKLIST KHI TEST FAIL

### Multi-select không hoạt động:
1. Print String SelectedActors.Length sau mỗi click
2. Check IsCtrlDown đọc đúng không
3. Check Contains() so sánh actor reference đúng không

### Pivot transform sai:
1. Print String Pivot.Location, các InitialOffsets
2. Check RefreshOffsets gọi sau khi set AttachedActors chưa
3. Check Tick compare LastTransform đúng không

### Group không save:
1. Check BP_GroupsContainer tag đúng "FurnitureGroupsContainer"
2. Check Groups variable tick SaveGame
3. Check SyncGroupsToContainer gọi sau mỗi thay đổi
4. Check ActorLoaded sync ngược về InputManager

### Undo restore sai selection:
1. Print SelectedMeshIndices trong CaptureSnapshot
2. Check UniqueID matching trong RestoreSnapshot
3. Check Version field đúng (2 hoặc 3)

### Outline không phân biệt Primary:
1. Check M_SelectionOutline support 2 stencil values
2. Print Stencil value của Primary vs Secondary
3. Check UpdateOutlineState gọi sau mỗi selection change
