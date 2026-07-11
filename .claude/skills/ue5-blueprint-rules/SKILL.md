---
name: ue5-blueprint-rules
description: "Dùng khi viết, review, hoặc debug node flow Blueprint trong dự án UE5 Interior Design Tool / FurnitureToolkit — trước khi đưa ra bất kỳ node flow nào, khi đặt tên biến (class var / temp var), khi chọn giữa Function và Custom Event, khi tối ưu performance, hoặc khi debug Accessed None / dead-end branch / VRAM leak / aliasing qua class var dùng chung."
---

# UE5 Blueprint Rules — FurnitureToolkit

## Khi nào dùng skill này

- Trước khi đưa BẤT KỲ node flow nào (bắt buộc, không phải tùy chọn)
- Khi review Blueprint export (K2Node text paste vào chat)
- Khi đặt tên biến mới trong Actor/Widget
- Khi quyết định logic đi vào Function hay Custom Event
- Khi tối ưu performance (Tick, loop, load asset)
- Khi debug Accessed None, dead-end branch, VRAM leak, hoặc bug mesh/material set sai actor
- Khi review 1 feature có tính "cấu trúc" (group/combo/nesting) trước khi tick Done

---

## Q8 — Self-check gate (bắt buộc, viết VISIBLE)

Trước MỌI node flow, viết 1 dòng đủ 5 điểm — không được viết "đã check Q8" suông không liệt kê:

```
Q8: [Container=Function/Event] | [IsValid guards] | [L2: mọi nhánh có đích] | [No Latent] | [6A: reverse path]
```

Ví dụ đúng:
```
Q8: Custom Event → class var OK | IsValid InputManager ✓ | L2: False branch merge về CaptureSnapshot ✓ | No latent ✓ | 6A: Undo khôi phục đúng ✓
```

Checklist đầy đủ chạy TRƯỚC khi viết flow:
- Đang tạo Local Variable? → nơi chứa là FUNCTION hay EVENT? (Event/Custom Event KHÔNG có Local Variable — L9)
- Mọi Object access có IsValid trước chưa? (L1)
- Mọi Branch có merge về cuối, không dead-end nuốt logic sau? (L2)
- Class var persistent đã CLEAR ở đầu function chưa?
- Có Latent node (Async/Delay/Timer) trong Function không? → sai, phải Custom Event (L8)
- Flow có > 2 tầng Branch lồng không? → DỪNG, đề nghị tách Function/helper
- Function thao tác đúng CẤP chưa? (gom đơn vị chọn vs gom actor-lá)
- Có đường NGƯỢC chưa? (Luật 6A)

---

## 3 nguyên tắc KP (áp cho mọi task, không chỉ node flow)

- **KP1 — Giả định tường minh:** task mơ hồ hoặc ≥2 cách hiểu hợp lý → nêu rõ giả định đang dùng, hoặc trình cả 2 cách kèm khác biệt. Không tự chọn im lặng. Bí/kẹt → dừng, hỏi.
- **KP2 — Prep phải duyệt:** không tự thêm feature/param/field/"flexibility" ngoài yêu cầu task. Muốn "chuẩn bị 1 lần thay vì 2" → nêu tường minh + chờ duyệt trước khi làm. Được duyệt → ghi ceiling (giới hạn chịu được) + trigger (sự kiện buộc nâng cấp) vào DEVIATIONS.md.
- **KP3 — Surgical:** chỉ đụng đúng chỗ task yêu cầu. Không tiện tay refactor/đổi format/xóa dead code có sẵn. Thấy chỗ đáng sửa ngoài scope → báo, không tự sửa. Rác do chính thay đổi của mình tạo ra thì dọn.

---

## L1-L11 — Quy tắc logic Blueprint (bài học trả giá bằng bug thực tế)

**L1 — IsValid trước MỌI Object access.** Trước GET/Cast/gọi function trên object → IsValid check. Tránh "Accessed None" crash.

**L2 — Tất cả nhánh Branch merge về cuối.** Dead-end branch = logic sau không chạy = bug.
- Ngoại lệ an toàn: Branch False dead-end TRONG Sequence.Then = OK (Sequence tự kích Then tiếp theo).
- Trong Event/Custom Event chain (KHÔNG phải Sequence) = FATAL.
- Test nhanh: "Nếu exec dừng ở đây, node nào sau Branch không chạy?" — có node quan trọng (CaptureSnapshot, RemoveFromParent, Return Node...) sau đó → phải merge.

**L3 — Thứ tự CaptureSnapshot.**
- Spawn: Add Tag → CaptureSnapshot
- Delete: Destroy Actor → CaptureSnapshot
- Deselect: DeselectMesh → CaptureSnapshot
- KHÔNG gọi CaptureSnapshot TRONG DeselectMesh (infinite loop). KHÔNG capture khi bIsRestoring=True.

**L4 — SET variable dùng output pin của SET node.** Vd RedoLastAction: nối output pin của SET CurrentIndex, KHÔNG GET lại — GET riêng = đọc giá trị cũ (pure node re-evaluate mỗi lần đọc).

**L5 — DeactivateGizmo TRƯỚC ActivateGizmo khi đổi mode.** Vd đổi Rotate → Move: Deactivate trước, Activate mode mới sau.

**L6 — Get Static Mesh Component trả rỗng trên BP_FurnitureActor.** → Cast To BP_FurnitureActor → GET FurnitureMesh.

**L7 — SET Tags cẩn thận với EMS.** KHÔNG SET Tags trực tiếp → GET Tags → ADD → SET Tags. EMS dùng Tags track state.

**L8 — Latent node không dùng trong Function.** Async Load/Delay/Timer chỉ dùng trong Custom Event/Macro. (Vì vậy CaptureSnapshot/RestoreSnapshot là Custom Event, không phải Function.)

**L9 — Local variable không sống xuyên Event.** Biến cần đọc ở nhiều event (OnPressed → Tick → OnReleased) → phải Class Variable, KHÔNG Local Variable.
- Nơi chứa là Function → Local Variable OK. Nơi chứa là Event/Custom Event → SAI, không có Local Variable panel.
- Dấu hiệu nhận biết Event: node màu đỏ, hoặc handler bind từ Dispatcher.

**L10 — Default value trước Sequence.** Nhiều Branch trong Sequence ghi cùng 1 biến → SET default TRƯỚC Sequence, False branch để TRỐNG (không ghi đè).

**L11 — Latent Load — Aliasing qua shared class var.** Latent node (Async Load Asset) đặt trong Custom Event của 1 Manager dùng chung → nhiều actor load song song, các lần Completed chia sẻ CÙNG node graph → class var trung gian (MeshAsset, MID cache...) bị đè nhau → mesh/material set sai actor.
- Fix: đặt Custom Event trong chính actor sở hữu asset (vd BP_FurnitureActor). Mỗi instance có graph riêng → Completed của actor nào set cho actor đó.
- Tổng quát: Manager gọi hộ + latent + nhiều target đồng thời = aliasing. Giải pháp: "actor tự lo asset của nó".

---

## R1-R5 — Nguyên tắc bắt buộc cho code mới (Runtime-Friendly)

Mục tiêu xa: user import asset từ máy cá nhân lên server lúc runtime. 5 nguyên tắc áp dụng từ bây giờ để codebase dễ nâng cấp sau.

**R1 — Không thêm Load Asset Blocking mới.** Blocking = game đứng chờ đến khi file load xong; file trên server hoặc file nặng → freeze 3-5 giây.
- Dùng Async Load Asset + callback cho mọi asset load mới.
- Chỗ đã có Load Asset Blocking → ghi comment `# TODO: migrate async`, không thêm mới.

**R2 — Widget không giữ hard ref đến Actor/Component.** Hard ref = Actor bị destroy nhưng RAM/VRAM không giải phóng.
- Widget chỉ giữ Soft Object Reference hoặc RowName/ID.
- Cần dùng Actor: Resolve Soft Ref → dùng → không lưu lại.
- Bắt buộc hard ref → SET None ở Event Destruct.

**R3 — Widget nhận struct data, không nhận object nặng.** Widget chỉ cần "tên gì, ảnh gì, ID gì" — không ôm cả object.
- Widget nhận struct (RowName, DisplayName, ThumbnailMI) làm input. Parent lo query data, truyền struct xuống.
- Không truyền cả DataTable row object hoặc Actor reference vào widget con.

**R4 — Event Destruct dọn sạch mọi reference.** Mọi Widget có Object Reference đến Actor/Component/Material/Texture/Widget khác → Event Destruct SET tất cả về None. Áp dụng ngay khi tạo widget mới.

**R5 — Lưu AssetID, không lưu path.** Asset path (`/Game/cuong/...`) đổi khi chuyển cloud; AssetID (RowName trong DataTable) thì không.
- Save material override, undo snapshot... → lưu RowName từ DataTable.
- Load: dùng RowName → Get Data Table Row → lấy path từ đó.
- Không hardcode full asset path `/Game/...` vào save data.

---

## Luật 6A — Forward + Backward bắt buộc

Mỗi feature, Definition of Done phải gồm cả chiều xuôi lẫn chiều ngược. Không định nghĩa được đường ngược (gỡ/hoàn tác/tháo ra) thì feature CHƯA XONG.

| Chiều xuôi | Chiều ngược phải có |
|---|---|
| Group nhiều đồ | Ungroup → đồ về đúng trạng thái trước |
| Enter edit mode | Exit edit → selection/visual phục hồi đúng |
| Spawn vào group đang edit | Xóa/undo → group không vỡ |
| Combo đóng gói nhánh cây | Mở combo → tái tạo đúng nhánh cây ban đầu |

> "Chiều ngược" rộng hơn undo/redo: là mọi cách người dùng tháo/đảo/gỡ thao tác bằng chính các nút trong tool.

## Luật 6B — Đối xứng cấu trúc (nhiều đường, cùng kết quả)

Mọi đường thao tác dẫn tới CÙNG một cấu trúc mong muốn phải cho CÙNG một kết quả.

Ví dụ bug thực tế (CreateGroup bottom-up, 14/06): top-down (enter edit → tạo 3 sub-group bên trong A) cho kết quả đúng, nhưng bottom-up (tạo A-1/A-2/A-3 trước → chọn cả 3 → Create Group) lại cho A phẳng không sub-group — vì function gom nhầm ở cấp *actor lá* thay vì cấp *đơn vị chọn*.

Khi làm feature cấu trúc (group/combo/nesting/parent-child), trước khi tick done, liệt kê MỌI đường tạo ra cấu trúc X rồi test từng đường: top-down, bottom-up, trộn (vài đơn vị đã nhóm + vài đồ rời), trong/ngoài edit scope.

## Definition of Done

1 task chỉ "xong" khi đủ 5 điều kiện:
- Test PASS
- Không vi phạm L1-L11
- Hard ref clear ở End Play/Destruct (nếu có tạo ref)
- Có đường NGƯỢC, đã test (Luật 6A)
- Nếu là feature cấu trúc: mọi đường thao tác cho cùng kết quả (Luật 6B)

Phân biệt lược bớt XẤU (cấm) vs thu hẹp scope TỐT (cho phép, phải ghi DEVIATIONS.md):
- XẤU: bỏ IsValid check "cho nhanh", skip test "chắc ổn rồi", không clear hard ref "lát nữa làm"
- TỐT: dời nested group sang v2, combo dùng icon generic thay auto-thumbnail, Smart Snap chỉ làm 2/5 loại trước

## 3-strike rule (Stuck Protocol)

Bug fail 3 lần với cùng 1 approach → STOP, không thử cách 4 ngay.
1. Ghi lại đã thử gì (tránh lặp)
2. Chọn 1 trong 3: Plan B / thu hẹp scope task (ghi DEVIATIONS.md) / tạm gác task
3. KHÔNG thử cách 4, 5, 6 liên tục

## Deviation Log

Lệch nhỏ (tên biến, thứ tự node) → không cần ghi. Lệch về logic/kiến trúc/scope → BẮT BUỘC ghi DEVIATIONS.md NGAY lúc lệch, dạng: `Ngày | Task | Plan nói | Thực tế làm | Lý do`.

## Vertical Slice trước

Đầu mỗi sprint, làm lát cắt dọc tối thiểu chạy end-to-end TRƯỚC (validate rủi ro lớn nhất), rồi mới hoàn thiện từng task. Không đi tuần tự 14 task hoàn hảo rồi mới phát hiện kiến trúc sai từ task 1.

## Sprint Review (checkpoint cuối sprint)

1. Regression: chạy Core Regression Suite → tính năng cũ còn nguyên?
2. Deviation review: đọc DEVIATIONS.md sprint này — >5 deviation lớn ở 1 vùng → plan vùng đó sai, cập nhật plan
3. Plan check: sprint kế tiếp còn hợp lý không?
4. Cập nhật Session_State.md + doc liên quan

---

## Bảng node UE5.5 đã xác nhận (dùng đúng display name)

- Slot as Canvas Slot (KHÔNG phải "Slot as Canvas Panel Slot")
- Get Mouse Position on Viewport (trả Vector2D, không cần chia DPI)
- Get All Actors With Tag / Get All Actors Of Class → Get(0)
- Get Hit Result Under Cursor By Channel
- Convert Mouse Location To World Space
- Set Render Custom Depth + Set Custom Depth Stencil Value
- Create Dynamic Material Instance + Set Vector/Scalar Parameter Value
- Async Load Asset (trong Custom Event)
- Make Soft Object Path
- Set Brush from Lazy Texture
- Get Data Table Row / Get Data Table Row Names
- Clear List Items / Regenerate All Entries
- Last Index → Get
- Is Valid Index
- Construct Object from Class (tạo object runtime nhẹ)

Node/class mới chưa có trong bảng trên → KHÔNG dùng trong flow chính thức. Ghi vào mục "Nodes chờ xác nhận" của `AI_Implementation_Rules.md`, chờ cuhoang confirm rồi mới coi là đã xác nhận.

## Quy ước đặt tên biến (từ Sprint 5)

- Class var dùng chung nhiều event trong 1 Actor → prefix viết tắt Actor đó. Vd `BP_ComboManager` → `Cmb_` (Cmb_PendingComboData, Cmb_SpawnedComboActors...)
- Biến tạm chỉ phục vụ 1 function/event → prefix = tên function/event đó. Vd `SaveComboFromSelection` → `SaveCombo_` (SaveCombo_GroupIDs, SaveCombo_TokenMap...)
- Param input của event/function → tên trần, không prefix (SelectedActors, ComboName, Center)

## Spawn Paths checklist

Khi thêm logic "sau khi spawn actor", audit ĐỦ các con đường spawn:
- Drag-drop card: WBP_DragOverlay → On Drop (dùng PreviewActorRef đã spawn từ On Drag Detected)
- Paste/Cut-Paste/Duplicate: SpawnFurnitureCopy (BP_FurnitureInputManager) — PasteMesh → ForEach → SpawnFurnitureCopy
- Replace Mesh: WBP_DragOverlay_FurnitureCard → F_ExecuteReplace (spawn mới, kế thừa từ OldActor)

⚠️ Drag-drop KHÔNG gọi SpawnFurnitureCopy — lỗi assumption phổ biến.

## Runtime State vs Snapshot State

Mọi state cần khôi phục qua Undo phải nằm trong `S_SceneSnapshot`.
- State này có cần undo-able không?
- Có → thêm field vào S_SceneSnapshot + CaptureSnapshot capture + RestoreSnapshot restore
- Restore TRƯỚC bất kỳ function nào đọc state đó
- Bump Version nếu field mới ảnh hưởng restore behavior

---

## Performance — máy yếu là ưu tiên (P1-P5)

- **P1 — Không Tick khi không cần.** Mọi logic Tick phải có guard, return sớm khi không có việc (99% thời gian nên return luôn).
- **P2 — Cache thay vì query lặp.** `Get All Actors With Tag` quét toàn scene — không gọi trong ForEach/Tick, cache 1 lần + update khi spawn/delete/load.
- **P3 — Async, không Blocking.** Load Asset Blocking freeze game thread — dùng Async Load Asset → callback → spawn dần (R1).
- **P4 — Batch thay vì per-item.** Xử lý N actor → gom 1 lần nếu được, thay vì N lần riêng lẻ.
- **P5 — Debounce thao tác lặp.** Snapshot, update UI, recalculate — debounce nếu user thao tác liên tục.

### Tối ưu theo tính năng (mục tiêu đo được)

- **Multi-select outline:** update CHỈ khi selection thay đổi (không mỗi Tick), diff update (chỉ actor mới thêm/bớt, không rebuild toàn bộ), giới hạn mềm khi selection > 200 actor. Mục tiêu: 50 actor → outline update < 30ms.
- **Pivot Actor Tick:** chỉ tick khi Transform đổi (so LastSyncedTransform), disable Tick khi không drag (Set Actor Tick Enabled theo Activate/DeactivateGizmo). Mục tiêu: 50 actor < 2ms/frame.
- **CaptureSnapshot:** dùng cached actor list (P2), debounce cho thao tác liên tục, MaxSteps thích ứng (ActorCount > 200 → MaxSteps=20, else 50). Mục tiêu: 100 actor + 10 group < 15ms.
- **Box Select:** project 1 lần khi thả chuột (không mỗi frame khi đang kéo khung), early reject actor quá xa camera, cached actor list. Mục tiêu: 200 actor < 50ms (chỉ khi thả chuột).
- **Combo Spawn:** async load tất cả mesh (R1), loading indicator ("Đang tải combo... 5/20"), spawn theo batch (5 mesh/frame thay vì 20 cùng lúc). Mục tiêu: 20 mesh < 1.5s, không freeze.
- **Scene Outliner:** virtualized list (List View/Tree View), lazy thumbnail (chỉ row visible), debounce rebuild 0.2s, diff update. Mục tiêu: 200 actor mở < 100ms, scroll mượt.
- **Material Multi-Apply:** async load material 1 lần (MI_Source), tạo DMI từ nguồn đã load cho từng actor — không load lại mỗi actor. Mục tiêu: 20 actor < 100ms.

### Checklist máy yếu

- Mọi Event Tick có guard condition (return sớm khi không cần)
- Không `Get All Actors With Tag` trong Tick hoặc ForEach
- Không `Load Asset Blocking` cho combo/material — dùng Async
- Pivot Actor disable Tick khi không drag
- Outline update chỉ khi selection đổi, không mỗi frame
- Snapshot debounce cho thao tác liên tục
- Mọi hard ref clear ở End Play/Destruct
- Scene Outliner virtualized (không spawn 500 widget)
- Loading indicator cho thao tác > 0.5s
- Test trên scene 100+ actor trước khi xem là "xong"

### VRAM Management

Mọi hard ref đến UObject phải clear ở Event End Play (Actor) / Event Destruct (Widget):
- `BP_FurnitureInputManager` End Play: CLEAR SelectedActors, SET PrimarySelectedActor=None, SET SelectedFurnitureActor=None, Destroy GizmoPivotActor (if valid), CLEAR ClipboardActors, CLEAR Groups
- `BP_PivotActor` End Play: CLEAR AttachedActors, InitialOffsets, InitialChildScales, InitialChildRotations
- `BP_GroupsContainer` End Play: CLEAR Groups
- `BP_UndoManager` End Play: SpawnedActors, FoundActor, TempMeshes, RestoredBPActor
- `WBP_FurnitureInventory` Destruct: TargetFurnitureActor, PendingRestoredActor
- `WBP_MaterialCard` Destruct: MaterialItem, InventoryRef

Workaround GPU/VRAM crash: restart editor mỗi 2-3 PIE session, dùng Standalone Game (Alt+P) cho session dài.

### Performance budget table

| Operation | Budget | Scene size |
|---|---|---|
| Click select 1 actor | < 5ms | any |
| Ctrl+Click add | < 5ms | any |
| Multi-select outline update (1 lần) | < 30ms | 50 actor |
| Multi-move per frame (pivot) | < 2ms | 50 actor |
| CaptureSnapshot | < 15ms | 100 actor |
| RestoreSnapshot | < 200ms | 100 actor |
| Box select (on release) | < 50ms | 200 actor |
| Combo spawn (async) | < 1.5s | 20 mesh |
| Outliner open | < 100ms | 200 actor |
| Material multi-apply | < 100ms | 20 actor |

⚠️ Vượt budget → STOP, optimize trước khi sang task khác.

### Đo lường — profile

Console commands trong PIE: `stat unit` (frame/game/render/GPU time), `stat fps`, `stat memory`, `stat rhi` (VRAM), `stat scenerendering` (draw calls).
Quy trình: `stat unit` → Game thread cao → optimize logic Blueprint (Tick/ForEach); Render/GPU cao → optimize outline/draw calls; Memory tăng liên tục → leak, check hard ref clear.

---

## Antipatterns — điều KHÔNG được làm

**Blueprint chung:**
- Loop lớn trong Blueprint → dùng C++ (FurnitureFilterLibrary)
- WrapBox cho danh sách lớn → Tile View/List View (virtualized)
- Get All Widgets of Class trong OnListItemObjectSet → Foff_GameInstance.FurnitureInventoryRef
- Thêm variables furniture vào BP_FoffPlayerController → dùng BP_FurnitureInputManager
- Cast To BP_FoffPlayerController lấy furniture variables → Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → Cast
- Gọi CaptureSnapshot trong DeselectMesh → gọi từ Mouse Left Pressed sau DeselectMesh
- Xẻ/tách code cũ khi thêm tính năng → thêm vào pin node có sẵn (KP3)
- SET Tags trực tiếp → GET → ADD → SET TempTags → SET Tags

**Thứ tự sai gây bug:**
- CaptureSnapshot trước Add Tag/Destroy Actor/DeselectMesh → phải SAU
- SET bIsDraggingGizmo=False trước CaptureSnapshot → CaptureSnapshot trước, rồi SET False
- CaptureSnapshot("Initial") không phải node cuối BeginPlay → phải là cuối cùng
- GET CurrentIndex riêng cho RestoreSnapshot → dùng output pin của SET CurrentIndex (L4)

**Gizmo:**
- Hardcode TransformType=Translation → truyền qua param
- Bỏ prefix actor name từ Display Name → Split (From End, ".") → Right S
- Không SET PreviousMousePosition trong OnMousePressed → delta khổng lồ frame đầu
- Không reset AccumulatedRotation khi thả chuột → SET=0 trong OnMouseReleased

**EMS Save/Load:**
- BP_FurnitureActor kế thừa Actor → phải kế thừa StaticMeshActor
- Gọi LoadFurnitureScene trong BeginPlay → EMS tự load
- Không destroy FurnitureSpawned trước EMS load → destroy trong OnLoadButtonClicked
- Bind SaveGameMenu 1 lần → Event Tick check widget mới → rebind

**Performance/Runtime-friendly:** xem mục Performance ở trên (P1-P5, R1-R5).

**Material v1.1 (bug thực tế):**
- `SpawnedActors[class var SelectedMeshIndex]` trong Broadcast → dùng `RestoredBPActor` (set từ Cast output) — class var = last CaptureSnapshot, sai snapshot
- SwitchInventoryMode False branch không gọi FilterBySearch → thêm FilterBySearch cuối False branch
- Duplicate branch để broadcast → single broadcast point với class var temp (2 nguồn đọc index = race condition)
- Set Background Color trên Button (Tint A=0) không work → Image overlay + Set Color and Opacity

**Lỗi hay gặp (nhanh):**
- SelectedFurnitureActor = None sau Delete → SET=None ngay sau Destroy Actor
- Mesh di chuyển thay vì xoay → ActiveAxis trùng tên, branch theo ActiveMode trước Switch
- Gizmo không hiện lần đầu → bGizmoActive=True từ mode cũ, cần DeactivateGizmo trước ActivateGizmo (L5)
- Collision bị disable khi drag → DeactivateGizmo trong On Drag Detected, không chờ On Drop

---

## Checklist cuối mỗi task

- Code chạy đúng theo test
- Không vi phạm L1-L11
- Đã chạy Q8 Self-Check Gate, ghi dòng kết quả
- Không hallucinate node (đối chiếu bảng node)
- Hard ref clear ở End Play/Destruct (nếu có)
- Có đường NGƯỢC, đã test (Luật 6A) — feature cấu trúc thêm Luật 6B
- Performance OK (đối chiếu budget table)
- Cập nhật doc liên quan (version, ngày, giờ, phút)
