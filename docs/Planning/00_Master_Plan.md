# MASTER PLAN — Multi-Select / Group / Combo / Material Edit v1.2
**Phiên bản:** 3.0 | **Ngày:** 28/05/2026 | **Project:** Lighting_Mnger (UE5.5.4)
**Trước đây:** MultiSelect_Group_ComboMesh_Plan_v2.md (deprecated)

---

## CẤU TRÚC TÀI LIỆU

Kế hoạch này gồm 8 file, mỗi file có vai trò riêng:

| File | Nội dung | Đọc khi |
|---|---|---|
| **00_Master_Plan.md** | Tổng quan, roadmap, navigation | Đọc đầu tiên |
| **01_Current_Architecture_Audit.md** | Phân tích chi tiết kiến trúc hiện tại | Trước khi code |
| **02_Target_Architecture.md** | Kiến trúc đích sau khi xong | Trước khi code |
| **03_Code_Inheritance_Strategy.md** | Chiến lược tái sử dụng code | Trước khi code |
| **04_Sprint_Details.md** | Chi tiết từng sprint (1-7) | Khi bắt đầu sprint |
| **05_Data_Structures.md** | Struct, Enum, Variables đầy đủ | Tham chiếu liên tục |
| **06_Risk_Mitigation.md** | Rủi ro + cách xử lý | Khi gặp vấn đề |
| **07_Testing_Strategy.md** | Test cases per sprint | Cuối mỗi sprint |
| **08_Performance_Optimization.md** | Tối ưu máy yếu + dữ liệu lớn | TRƯỚC mỗi task — ràng buộc bắt buộc |
| **09_AI_Implementation_Rules.md** | Guardrail cho AI thực thi (Sonnet 4.6) | AI đọc ĐẦU TIÊN mỗi session |
| **10_Execution_Discipline.md** | Chống đi lạc, chống bỏ cuộc khi thực thi | Đọc cùng 09, áp dụng xuyên suốt |

---

## TRIẾT LÝ THIẾT KẾ

Ba góc nhìn định hình mọi quyết định:

**👤 Người dùng bình thường:** Không kiến thức kiến trúc/vật liệu. Cần thao tác nhanh, ít bước, ưng mắt là được. Giao diện phải trực quan — nhìn là hiểu.

**💼 Kinh doanh:** Giải pháp thay thế phần mềm thiết kế nội thất khác. Combo Mesh = bán "bộ nội thất hoàn chỉnh", không chỉ bán công cụ. Đây là tính năng tạo revenue.

**⚙️ Kỹ thuật:** Code có tính kế thừa, thêm chức năng mới ít sửa code cũ. Multi-select là nền tảng — làm đúng từ đầu để mọi code sau xây trên đó.

---

## NGUYÊN TẮC CỐT LÕI

### 1. KẾ THỪA TỐI ĐA, REWRITE TỐI THIỂU
Mỗi function mới đều phải hỏi: "Có function nào đang làm việc tương tự không?"
- `MoveMultiActors` → tận dụng pattern `NudgeMesh` (đã có ForEach surface logic)
- `PasteMultiActors` → tận dụng `SpawnFurnitureCopy` (shared spawn)
- `CaptureGroupSnapshot` → mở rộng `CaptureSnapshot` (giữ pattern Capture)

### 2. ADDITIVE, KHÔNG BREAKING
Giai đoạn refactor giữ cả 2 biến cũ + mới song song. Chỉ xóa biến cũ khi tất cả code chuyển xong.
- Sprint 1: thêm `SelectedActors` (array), giữ `SelectedFurnitureActor` (single)
- Sprint 2-7: dần dần thay đổi reference từ single sang array
- Sprint 7 cuối: xóa `SelectedFurnitureActor` nếu không còn ai dùng

### 3. R1-R5 BẮT BUỘC CHO CODE MỚI
- **R1:** Async load (Combo mesh, Material edit param load)
- **R2:** Widget không hard ref BP_FurnitureGroup
- **R3:** Widget nhận struct nhẹ (GroupID + GroupName), không nhận actor nặng
- **R4:** Event Destruct clear mọi reference
- **R5:** Lưu GroupID, không lưu actor path

### 4. SINGLE SOURCE OF TRUTH
Mỗi data point có đúng 1 nơi lưu canonical:
- Selection state → `BP_FurnitureInputManager.SelectedActors`
- Group membership → `BP_FurnitureActor.GroupID` (lưu trên actor, không phải trên group)
- Group metadata (tên, lock) → `BP_FurnitureGroup` (chỉ metadata, không lưu children)
- Combo template → `DT_ComboMeshCatalog` + JSON

---

## ROADMAP 7 SPRINT

```
Sprint 1: Multi-select cơ bản          (5-7 ngày)  ← FOUNDATION
Sprint 2: Box Select + Context Menu    (3-5 ngày)
Sprint 3: Group cơ bản                  (5-7 ngày)
Sprint 4: Edit Mode + Nested Group      (5-7 ngày)
Sprint 5: Combo Mesh                    (5-7 ngày)
Sprint 6: Polish UX                      (5-7 ngày)
Sprint 7: Material Edit v1.2            (3-5 ngày)

Total: ~30-45 ngày (~6-8 tuần)
```

> ⚠️ **GHI CHÚ TIMELINE THỰC TẾ:** 6-8 tuần là ước tính lạc quan (lý thuyết). Tính cả đường cong học tập + thời gian debug thực tế (Resize Window đơn giản hơn đã tốn nguyên 1 session nhiều vòng fix), **thực tế nhiều khả năng 10-12 tuần**. Đừng nản khi thấy "trễ so với plan" — đó là bình thường, không phải thất bại. Sprint 1 (đụng 3 file lõi) và S1.T7 (refactor input flow) là rủi ro lớn nhất về thời gian.
>
> 💡 **Cân nhắc ship sớm:** Không nhất thiết làm hết 7 sprint mới demo được. Sau **Sprint 3** (Multi-select + Group) đã có thứ ấn tượng để quay marketing ("kéo cả bộ sofa 1 phát"). Combo (Sprint 5) là tính năng bán hàng nhưng có thể ship sau Sprint 3, test phản hồi thị trường, rồi mới đầu tư tiếp. Tránh làm 8-12 tuần trong im lặng rồi mới biết thị trường có quan tâm không.

### Dependencies giữa các Sprint

```
Sprint 1 (Foundation)
   ↓
Sprint 2 (Box Select dùng SelectedActors)
   ↓
Sprint 3 (Group cần multi-select để chọn nhiều)
   ↓
Sprint 4 (Edit Mode cần Group)
   ↓
Sprint 5 (Combo cần Group structure)
   ↓
Sprint 6 (Polish — Align/Lock cần multi-select + group)
   ↓
Sprint 7 (Material Edit — độc lập, có thể làm sớm hơn)
```

⚠️ **Sprint 7 có thể chạy song song** với Sprint 5-6 nếu có thời gian — không có dependency hardcoded.

---

## CHANGES SO VỚI PLAN v2

### Quyết định mới:

**1. Group KHÔNG phải là Actor mới — chỉ là Data Structure**
Plan v2 đề xuất `BP_FurnitureGroup` là Actor. Plan v3 chuyển sang **data-only approach**:
- Không spawn actor mới khi tạo group
- Group data lưu trong `BP_FurnitureInputManager.Groups : Array of S_GroupData`
- Actor membership thông qua `BP_FurnitureActor.GroupID : String`

**Lý do thay đổi:**
- Tránh phức tạp Save/Load: EMS không cần handle thêm actor class mới
- Tránh phức tạp Undo/Redo: snapshot chỉ cần thêm Groups array, không cần spawn/destroy group actors
- Hiệu năng tốt hơn: 100 group = 100 entry trong array, không phải 100 actor mới
- Đơn giản hơn: group chỉ là logical concept, không cần physical presence trong world

**Đánh đổi:** Mất khả năng giữ Z-Order hoặc Transform cấp group (không quan trọng cho interior design vì group transform được tính từ children).

**2. Multi-Outline dùng Custom Depth Stencil value khác nhau**
- Primary selected actor: Stencil = 255 (giữ nguyên outline xanh hiện tại)
- Secondary selected actors: Stencil = 254 (outline khác màu nhẹ hơn, ví dụ xanh nhạt)
- Material outline cần update để hỗ trợ 2 stencil values

**3. Pivot Actor cho Gizmo Multi-select**
Plan v2 đề xuất 2 cách. Plan v3 chốt **Cách 1 — Pivot Actor**:
- Spawn 1 BP_PivotActor (tag "FurniturePivot", không tag "FurnitureSpawned") ở center group
- Gizmo attach vào Pivot Actor
- Khi Pivot move/rotate/scale → tính delta → ForEach SelectedActors apply delta
- Pivot Actor không xuất hiện trong Save/Load, không xuất hiện trong Undo
- Destroy Pivot khi deselect all

**Lý do:** RuntimeTransformer plugin chỉ hoạt động với 1 SelectActor. Không cần modify plugin.

**4. Snapshot mở rộng có versioning**
S_SceneSnapshot thêm field `Version : Integer` để forward-compatible. Hiện tại = 2 (multi-select). Save cũ load lại tự upgrade.

**5. Sprint 2 thêm Context Menu = Required, không Optional**
Plan v2 ghi context menu là tính năng "thêm vào". Plan v3 đẩy lên required vì:
- Là chuẩn UX phổ thông
- Right-click cũng là cách mở Group/Ungroup/Lock — không có context menu sẽ phải dùng phím tắt
- Implementation đơn giản (1 widget Vertical Box)

---

## NAVIGATION

Đọc theo thứ tự:

1. **01_Current_Architecture_Audit.md** — hiểu rõ tool đang là gì
2. **02_Target_Architecture.md** — hiểu rõ tool sẽ là gì
3. **03_Code_Inheritance_Strategy.md** — kế hoạch tận dụng code
4. **05_Data_Structures.md** — tham chiếu khi viết code
5. **04_Sprint_Details.md** — bắt đầu code từ Sprint 1
6. **06_Risk_Mitigation.md** — khi gặp vấn đề
7. **07_Testing_Strategy.md** — sau mỗi sprint

---

## CRITICAL DECISIONS LOG

Mỗi quyết định kiến trúc lớn ghi lại ở đây. Tránh quay lại tranh luận trong khi code.

| # | Quyết định | Lý do | Ngày |
|---|---|---|---|
| 1 | Group là data structure, không phải Actor | Tránh phức tạp Save/Load + Undo | 28/05/2026 |
| 2 | Pivot Actor cho gizmo multi-select | Không modify RuntimeTransformer | 28/05/2026 |
| 3 | Multi-Outline dùng 2 Stencil values | Phân biệt Primary vs Secondary | 28/05/2026 |
| 4 | Snapshot Version field | Forward-compatible với save cũ | 28/05/2026 |
| 5 | Context Menu = Required từ Sprint 2 | Chuẩn UX, dependency cho Group ops | 28/05/2026 |
| 6 | Material Edit v1.2 có thể chạy song song | Không depend Group | 28/05/2026 |
| 7 | Sprint 1 Move-first, Rotate/Scale làm cuối (S1.T15) | Toán Pivot rotate/scale khó, không để block sprint | 28/05/2026 |
| 8 | Combo JSON include materialParams ngay từ Sprint 5 | Tránh sửa schema khi Sprint 7 xong | 28/05/2026 |

---

## SAU 7 SPRINT — ROADMAP TIẾP

Sau khi xong toàn bộ:
1. **Refactor Phase B** — AssetService C++, Event Bus (đã biết exact needs từ thực tế)
2. **glTFRuntime** — runtime asset import
3. **Supabase** — cloud + share + multi-user
4. **Interactive Objects** — switch điện, TV, quạt (Phase 5+)
