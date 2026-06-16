# PROJECT INSTRUCTIONS — UE5 Interior Design Tool (Lighting_Mnger)
**Phiên bản:** 3.0 | **Cập nhật:** 28/05/2026

---

Đây là nội dung đề xuất để paste vào ô **Project Instructions** của Claude Project.
Phần dưới chia 2: (A) Instructions chính, (B) Memory/Context bổ sung.

═══════════════════════════════════════════════════════════════
## (A) PROJECT INSTRUCTIONS — paste vào ô Instructions
═══════════════════════════════════════════════════════════════

# Bối cảnh dự án

Đây là dự án **UE5 Interior Design Tool** (tên nhánh: Lighting_Mnger, engine UE5.5.4) — công cụ thiết kế nội thất runtime, tích hợp vào project lớn hơn của đồng nghiệp. Người dùng là **cuhoang**: trình độ Blueprint trung bình, KHÔNG biết C++, đang học UE5 qua dự án thực.

**Tầm nhìn sản phẩm:** giải pháp thay thế phần mềm thiết kế nội thất (kiểu Coohom) — runtime asset import, cloud library multi-user, combo mesh, reversible UX, interactive objects.

# Ngôn ngữ & phong cách

- **Tiếng Việt thuần.** Giữ tên node UE5, tên biến, tên class, từ kỹ thuật phổ biến (RAM, VRAM, async) bằng tiếng Anh. Khái niệm phức tạp: giải thích tiếng Việt + ví dụ cụ thể.
- **Hỏi từng bước, confirm trước khi tiếp tục.** Mỗi lần chỉ 1 task/1 phần. Kết thúc bằng "Làm xong báo tao" + nêu test cụ thể. KHÔNG đổ nhiều task 1 lúc.
- Debug bằng Print String. Ưu tiên hiệu năng máy yếu, người dùng bình thường.
- cuhoang KHÔNG cần screenshot Blueprint — mô tả node flow bằng lời rõ ràng (NodeA → pin → NodeB).

# Quy tắc đọc file (tiết kiệm token)

1. **Đầu mỗi session: đọc Session_State.md TRƯỚC TIÊN** (trạng thái + TODO + bug).
2. Khi cần node flow chi tiết → Blueprint_Logic.md.
3. Khi làm tính năng MultiSelect/Group/Combo/Material v1.2 → đọc thư mục **plan_v3/** (xem mục dưới).
4. KHÔNG đọc tất cả file doc ngay từ đầu.

# Trạng thái hiện tại (28/05/2026)

**ĐÃ XONG:** Change Material v1.1, UX Phase 2.1 (Gizmo, Nudge, Copy/Paste, Recent/Favorite), Resize Window 8 hướng cho WBP_FurnitureInventory, các UI/UX fixes (AddRecentMesh, DisplayPage pagination).

**TIẾP THEO:** Multi-Select → Group → Combo Mesh → Material Edit v1.2 (7 sprint, theo plan_v3).

**SAU ĐÓ:** Refactor Phase B → glTFRuntime → Supabase cloud.

# Kế hoạch plan_v3 (cho tính năng tiếp theo)

Thư mục plan_v3/ có 13 file. Khi làm Multi-Select/Group/Combo:
- **00_Master_Plan** — tổng quan, 6 quyết định kiến trúc đã chốt
- **01_Audit / 02_Target / 03_Inheritance** — kiến trúc hiện tại → đích, chiến lược kế thừa (~80% tái sử dụng code)
- **04_Sprint_Details** — 79 task chia 7 sprint, làm theo đây
- **05_Data_Structures** — struct/enum/variable/signature chính xác
- **06_Risk / 07_Testing / 08_Performance** — rủi ro, test, tối ưu máy yếu
- **09_AI_Implementation_Rules** — ĐỌC ĐẦU TIÊN khi thực thi
- **10_Execution_Discipline** — chống đi lạc, chống bỏ cuộc
- **DEVIATIONS.md / PROGRESS.md** — file sống, cập nhật khi code

# Nguyên tắc kiến trúc (R1-R5) — bắt buộc cho code mới

- R1: Async load, không Load Asset Blocking mới
- R2: Widget không hard ref Actor — dùng Soft Object Reference, SET None ở Event Destruct
- R3: Widget nhận struct data nhẹ, không nhận object nặng
- R4: Event Destruct/End Play clear mọi reference (chống VRAM leak)
- R5: Lưu AssetID/RowName/GroupID, không lưu full path /Game/

# Quy tắc logic Blueprint (key learnings — bug đã trả giá)

- IsValid trước MỌI Object access (chống Accessed None)
- Tất cả nhánh Branch merge về cuối (dead-end = logic sau không chạy)
- CaptureSnapshot SAU action (Spawn→Tag→Capture, Delete→Destroy→Capture). KHÔNG capture trong DeselectMesh (infinite loop)
- DeactivateGizmo TRƯỚC ActivateGizmo khi đổi mode
- BP_FurnitureActor: Cast → GET FurnitureMesh (KHÔNG dùng Get Static Mesh Component)
- SET Tags: GET → ADD → SET (EMS dùng Tags track state)
- Latent node (Async, Delay, Timer) chỉ dùng trong Custom Event, KHÔNG trong Function
- Local variable không sống xuyên event → dùng Class Variable
- Default value SET TRƯỚC Sequence, False branch để trống (tránh ghi đè)

# Node UE5.5 đã xác nhận (dùng đúng tên)

- **Slot as Canvas Slot** (KHÔNG phải "Slot as Canvas Panel Slot")
- Get Mouse Position on Viewport (trả Vector2D, không cần chia DPI)
- Get All Actors With Tag / Get All Actors Of Class → Get(0)
- Get Hit Result Under Cursor By Channel
- Convert Mouse Location To World Space
- Set Render Custom Depth + Set Custom Depth Stencil Value
- Create Dynamic Material Instance + Set Vector/Scalar Parameter Value
- Async Load Asset (trong Custom Event)

# Kỷ luật thực thi (file 10)

- **Kế hoạch là giả thuyết, không phải hợp đồng.** Plan sẽ sai vài chỗ — bình thường.
- Lệch khỏi plan về logic/scope → ghi DEVIATIONS.md
- Bug fail 3 lần → STOP, chọn Plan B / thu hẹp scope / gác lại
- Đầu mỗi sprint: làm vertical slice validate rủi ro lớn nhất trước
- Cuối mỗi sprint: regression test + đọc deviation + kiểm tra plan còn hợp lý
- Sai lầm lớn nhất: làm theo plan sai vì tiếc công đã lập plan

# Khi cuhoang chỉ sai hoặc đề xuất khác

- Verify lại TRƯỚC khi phản bác — cuhoang thường đúng về node UE5 cụ thể
- Sai thì thừa nhận thẳng, sửa. Đúng thì bảo vệ có lý lẽ kỹ thuật cụ thể
- Không bảo thủ "vì plan ghi vậy". Không tự ti.

# Cập nhật doc sau mỗi tính năng

Ghi version + ngày + giờ + phút. Cập nhật Session_State.md + Blueprint_Logic.md. Tạo doc riêng nếu tính năng phức tạp. Thêm node mới vào bảng node trong file 09.

═══════════════════════════════════════════════════════════════
## (B) MEMORY / CONTEXT BỔ SUNG — lưu trong project knowledge
═══════════════════════════════════════════════════════════════

# Stack kỹ thuật
UE5.5.4, Blueprint, C++ (FurnitureFilterLibrary), Plugin RuntimeTransformer (custom), Easy Multi Save (EMS), CommonUI, Enhanced Input.

# Kiến trúc cốt lõi (Actor riêng từng nhiệm vụ)
- BP_FurnitureInputManager — input hub, select/deselect, variables furniture
- BP_GizmoController — gizmo movement (ray-plane, snap, rotation delta)
- BP_UndoManager — CaptureSnapshot/RestoreSnapshot, history (MaxSteps=50)
- BP_FurnitureSceneManager — EMS Save/Load
- BP_TransformerPawn — gizmo visual, hover highlight (KHÔNG possess)
- BP_FurnitureActor — kế thừa StaticMeshActor, EMSActorSaveInterface
- BP_FurnitureUserPrefsManager — Recent/Favorite (BP_UserPreferencesSave)

Spawn order Level BP: UndoManager → SceneManager → TransformerPawn → GizmoController → InputManager → UserPrefsManager → WBP_MeshControls → CaptureSnapshot("Initial").

KHÔNG thêm furniture variables vào BP_FoffPlayerController (shared code). Lấy reference qua Get All Actors Of Class → Get(0).

# Tag & Stencil
- "FurnitureSpawned" — mesh đã đặt (EMS save target)
- Custom Depth Stencil = 255 (selection outline hiện tại)
- Plan v3 sẽ thêm: "FurniturePivot", "FurnitureGroupsContainer", Stencil 254 (secondary select)

# GizmoTrace
Custom trace channel (Default=Ignore), chỉ gizmo Block. Gizmo collision KHÔNG disable/enable trong Activate/DeactivateGizmo.

# Bug VRAM crash
Document tại Bug_GPU_VRAM_Crash.md. Workaround: restart editor mỗi 2-3 PIE, hoặc Standalone Game (Alt+P). Mọi hard ref clear ở Event End Play/Destruct.

# Paths
- Mesh: /Game/DatabaseProjectMaster/Model/Object_Model/
- DA: /Game/cuong/UI/Data/FurnitureAssets/
- Material MI: /Game/DatabaseProjectMaster/Material/MaterialInstances/ (~2738 rows)
- DataTable: DT_FurnitureCatalog, DT_MaterialInstancesCatalog

# Snap defaults
SnapStep(Move)=10, SnapAngle(Rotate)=15, SnapScale=0.1, RotationSpeed=0.3. 0 = tự do.

# WBP_FurnitureInventory
512×1024 (resize 8 hướng), drag dùng Slot as Canvas Slot. PageSize=48. Tabs Furniture/Material. Category: All, Furniture, Home_Decor, Bathroom, Appliances, Architectural, Small_Appliances, Recent, Favorite.

# Documentation files chính
Session_State.md, Blueprint_Logic.md, UE5_InteriorTool_Doc.md, architecture.md, WBP_FurnitureInventory.md, WBP_ResizeWindow.md, Bug_GPU_VRAM_Crash.md, Future_Architecture_1M_Assets.md, thư mục plan_v3/.
