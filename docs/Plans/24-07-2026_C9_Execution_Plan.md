# C9 — REPLACE COMBO — Kế hoạch thực thi

> 📌 **[CHỨA AS-BUILT]** — File này bắt đầu là plan nhưng đã được ghi thêm kết quả thực thi
> thật (test PASS / K2Node export / changelog per-gate). Phần kết quả là AS-BUILT, ưu tiên cao
> hơn doc canonical nếu mâu thuẫn. **Phần nào là as-built:** ghi chú v1.1 (sửa 2 lỗi nghiêm
> trọng sau tự audit) + §10 kết quả test case (C9 nay đã DONE 30/07 — xem `01_Session_State.md`).

**Phiên bản:** 1.1 | **Ngày:** 24/07/2026 | **Tác giả:** Opus (architect) | **Người thực thi:** Sonnet

v1.1 — sau lượt tự audit (13 điểm mù). Sửa 2 lỗi nghiêm trọng: DestroyComboCluster thiếu
DeselectAll (§5.3); bIsRestoring có thể kẹt True nếu RestoreSnapshot nhiều đường thoát (§3).
Thêm: Find References trước khi xóa biến (§4 Bước 0), guard Is Valid Index cho
RestoreCurrentSnapshot (§6.1), CLEAR Cmb_ReplaceActors đầu event (§6), clear payload ở MỌI
đường thoát replace mode không chỉ CB_Replace (§8), test orphan group (§6 TEST), Q8 cho C9.0c,
sửa test case 3 mô tả sai + thêm case 8/9/10 (§10).

**Nguồn:** 23-07-2026_C9_Handoff_Opus.md + 5 [VERIFY] cuhoang trả lời 24/07
**Trạng thái phê duyệt:** QĐ1 ✅ · QĐ2 ✅ · QĐ3 ✅ (bản làm sạch — migrate enum) · thứ tự C9.c
trước UI ✅ · fix B1 trước ✅ · 3-strike cho migration ✅

> Task card này SELF-CONTAINED. Sonnet KHÔNG cần đọc lại Post_C5_Execution_Plan_v1.md hay
> Combo_Execution.md để thực thi — mọi thứ cần thiết đã trích vào đây. Đọc 01_Session_State.md
> trước để biết trạng thái, rồi làm theo file này.

---

## 0. SỰ THẬT ĐÃ VERIFY — KHÔNG ĐƯỢC ĐOÁN LẠI

Session 23/07 dính 5 lần doc-drift. Mọi mục dưới đây đã đối chiếu K2Node export thật hoặc
cuhoang xác nhận trực tiếp. Coi đây là sự thật; nếu Blueprint khác → báo cuhoang, KHÔNG tự sửa
theo doc cũ.

| # | Sự thật | Nguồn |
|---|---|---|
| V1 | BP_ComboManager chỉ có 1 dispatcher: OnComboLibraryChanged. SpawnComboByID KHÔNG broadcast gì. Sub-step D gọi thẳng InputManagerRef.DeselectAll/SelectActors + UndoManagerRef.CaptureSnapshot("SpawnCombo") | cuhoang 24/07 |
| V2 | BTN_ChangeCombo đã tồn tại trong WBP_ComboCard → HB_Buttons, Visibility = Hidden | cuhoang 24/07 |
| V3 | RestoreSnapshot(Index) nhận tham số index, KHÔNG tự dịch con trỏ. UndoLastAction = CurrentIndex - 1 → RestoreSnapshot(CurrentIndex); RedoLastAction = SET CurrentIndex + 1 → RestoreSnapshot(output pin của SET) | BP_UndoManager.md |
| V4 | CalculateCenter(Actors) → Vector = ForEach: Sum += GetActorLocation → Completed: Return(Sum / IntToDouble(Length)). KHÔNG loại pivot/container (doc Combo_Execution.md ghi sai). CHIA CHO 0 nếu Length==0 → trả (0,0,0) | K2Node export 24/07 |
| V5 | DeleteSelected = ForEach SelectedActors → Destroy → DeselectAll → PruneEmptyGroups → CaptureSnapshot("Delete"). PruneEmptyGroups v1.8 dùng GetAllDescendantActors → cascade đúng cả cây nested trong 1 pass | BP_FurnitureInputManager.md |
| V6 | StartReplaceMode (mesh) không có EnsureExpanded; cấu trúc thật 3 nhánh (IsValid × IsInViewport), 2 khối tạo-widget gần trùng lặp | K2Node export 23/07 |
| V7 | ResolveSelectedComboRoot() ĐÃ XONG + test PASS, dùng PrimarySelectedActor | session 23/07 |
| V8 | FindGroupData chỉ có 2 output: (Group Data, Found) — KHÔNG có Index | K2Node export 23/07 |

---

## 1. QUYẾT ĐỊNH KIẾN TRÚC

**QĐ1 — Mở rộng SpawnComboByID bằng param có default, KHÔNG viết đường spawn thứ 2**

Tiền lệ K3: SpawnFurnitureCopy được thêm bAddToRecent thay vì tách hàm. Áp y hệt. Lợi ích kế
thừa: tính năng sau cần "spawn combo, hậu xử lý khác" chỉ thêm param.

**QĐ2 — Logic nằm trong Actor, widget gọi đúng 1 node**

Mesh làm SAI chỗ này (WBP_DragOverlay_FurnitureCard.BTN_ChangeMesh chứa nguyên vòng
destroy/spawn/snapshot trong widget). KHÔNG copy pattern đó. Card combo chỉ gọi 1 node.

**QĐ3 — Migrate bIsReplaceMode (Boolean) → ReplaceTarget (Enum), làm sạch ngay**

Lý do an toàn: xóa biến cũ → Blueprint compiler tự liệt kê MỌI node gãy trong Compiler Results
→ không mò tay, không sót call site. 3-strike: nếu regression mesh replace không sửa nổi sau 3
lần → revert về phương án additive (bIsReplaceMode + ComboRootGroupIDToReplace làm
discriminator), ghi DEVIATIONS, đi tiếp C9.

---

## 2. THỨ TỰ THỰC THI

```
C9.0b  Fix B1 (bIsRestoring)              → TEST B1
C9.0c  Migrate E_ReplaceTarget            → TEST regression mesh replace (5 case)
C9.b   SpawnComboByID mở rộng + DestroyComboCluster  → TEST đồng bộ A/D/B
C9.c ⭐ ReplaceCombo + phím debug          → TEST case 1,2,4  ← LÕI RỦI RO NHẤT
C9.d   StartReplaceComboMode + ExitReplaceMode mở rộng + RefreshComboCardReplaceMode
C9.e   CB_Replace route 2 nhánh
C9.f   BTN_ChangeCombo + ExecuteComboReplace  → TEST đủ 5 case, xóa phím debug
```

Mỗi bước xong → báo cuhoang + kết quả test. PASS mới đi tiếp.

---

## 3. C9.0b — FIX B1 (bIsRestoring)

Vì sao làm trước: B1 (Open_Bugs.md, 🔴 Cao, carry-over Sprint 3) = "Undo lần 2 không restore
group state". Giả thuyết H1: RestoreSnapshot → SelectActors → listener OnSelectionChanged →
CaptureSnapshot → snapshot chèn vào GIỮA lúc restore → history lệch. C9 rollback gọi thẳng
RestoreSnapshot → dính đúng bug này. Test C9 khi B1 còn mở = kết quả không đáng tin.

Q8: Custom Event (CaptureSnapshot/RestoreSnapshot đều là Custom Event, KHÔNG phải Function) |
không Object access mới | L2: nhánh True của guard là early-exit CỐ Ý (xem ghi chú) |
No Latent | 6A: bIsRestoring luôn được SET False trước Broadcast — không kẹt True vĩnh viễn

**Bước 1 — BP_UndoManager thêm biến**

```
bIsRestoring : Boolean (default False, KHÔNG SaveGame)
```

**Bước 2 — RestoreSnapshot, chèn 2 chỗ**

```
Ngay SAU Function Entry (TRƯỚC Step 1 DeselectAll):
  ▶→ SET bIsRestoring = True

Ngay TRƯỚC Step 7 (Broadcast OnRestoreCompleted):
  ▶→ SET bIsRestoring = False
```

🔴 BẮT BUỘC LÀM TRƯỚC KHI CHÈN — đếm đường thoát của RestoreSnapshot. RestoreSnapshot là
Custom Event to, có nhiều Branch (Version >= 2 vs fallback, SelectedMeshIndices.Length > 0 vs
không...). Nếu BẤT KỲ nhánh nào dead-end trước chỗ SET bIsRestoring = False thì cờ kẹt True
vĩnh viễn → CaptureSnapshot bị guard chặn mãi mãi → toàn bộ Undo im lặng ngừng ghi, và triệu
chứng sẽ lòi ra ở một test hoàn toàn khác, trông như bug khác.

Cách làm: rà mọi nhánh exec trong RestoreSnapshot. Nếu có N đường tail → đặt
SET bIsRestoring = False trên CẢ N đường, không chỉ đường chính. Nếu không chắc → paste K2Node
export của RestoreSnapshot cho cuhoang/Opus soi trước khi sửa.

Nếu TEST B1 vẫn fail sau khi fix: nghi phạm tiếp theo là listener của OnRestoreCompleted gọi
CaptureSnapshot — lúc đó cờ đã False. Thử dời SET False sang SAU Broadcast và test lại.

**Bước 3 — CaptureSnapshot, guard đầu hàm**

```
TRƯỚC Step 0 (CLEAR TempSelectedIndices):
  ▶→ Branch(bIsRestoring)
       True  ▶→ dead-end (KHÔNG capture)
       False ▶→ Step 0 như cũ
```

⚠️ Nhánh True dead-end ở đây KHÔNG vi phạm L2. L2 cấm dead-end khi "logic sau lẽ ra phải
chạy". Ở đây ý đồ chính xác là dừng hẳn, không capture gì. CaptureSnapshot là Custom Event nên
KHÔNG có Return Node — dead-end là cách duy nhất. Đừng "sửa" nó thành merge.

**Bước 4 — Diagnostic Print tạm (xóa sau khi PASS)**

```
Đầu RestoreSnapshot: "RST idx={IndexHistory} act={ActionName} hist={History.Length}"
Cuối RestoreSnapshot: "RST-END mgr.Groups={InputManager.Groups.Length} hist={History.Length} restoring={bIsRestoring}"
```

`restoring=` ở dòng cuối phải luôn in ra false. In ra true = có đường thoát chưa được gắn SET
False → quay lại rà theo cảnh báo ở Bước 2. Đặt trên MAIN execution line, KHÔNG trong loop body
(bài học v1.5).

**TEST B1**

1. Select 3 đồ → Ctrl+G → Move cả group → Undo → Undo
   → sau Undo lần 2: info bar vẫn hiện group, log "RST-END mgr.Groups" > 0
2. "hist" đầu vs cuối MỖI lần restore phải BẰNG NHAU ← chứng minh không có capture chèn giữa
3. Regression: Undo/Redo xen kẽ Select/Deselect vẫn đúng như trước

→ Báo cuhoang + log 3 dòng. Open_Bugs.md B1 → RESOLVED.

---

## 4. C9.0c — MIGRATE E_ReplaceTarget

Q8: chỉ đổi kiểu biến + node đọc/ghi, không thêm flow mới | không Object access mới |
L2: mọi Branch cũ giữ nguyên cấu trúc, chỉ đổi điều kiện | No Latent | 6A: đường ngược =
ExitReplaceMode (được hợp nhất ở Bước 4)

**Bước 0 — Liệt kê call site TRƯỚC khi xóa gì**

Right-click biến bIsReplaceMode → Find References ở CẢ 2 nơi (BP_FurnitureInputManager và
WBP_FurnitureInventory). Chép danh sách ra giấy/chat.

⚠️ Vì sao không chỉ dựa vào compiler: blueprint chưa được load có thể KHÔNG báo lỗi compile
ngay lúc xóa biến → sót call site → vỡ lúc runtime bằng "Accessed None" khó truy. Sau khi sửa
xong phải chạy Compile All Blueprints (không chỉ compile 2 file vừa sửa) rồi mới test.

**Bước 1 — Tạo Blueprint Enum**

```
E_ReplaceTarget : None | Mesh | Combo        (None = giá trị mặc định, index 0)
```

[VERIFY] chỗ đặt: cùng thư mục với E_InventoryMode / E_ActiveMode. [VERIFY] editor có nhận
display name "None" không — bị từ chối thì đặt NoTarget, sửa lại mọi chỗ so sánh trong file này
cho khớp.

**Bước 2 — Thêm biến mới (CHƯA xóa biến cũ)**

```
BP_FurnitureInputManager : ReplaceTarget : E_ReplaceTarget (default None)
WBP_FurnitureInventory   : ReplaceTarget : E_ReplaceTarget (default None)
```

Mỗi nơi thêm 1 Pure helper:

```
Function IsReplaceModeActive() → Boolean   [Pure]
  Return( ReplaceTarget != None )
```

**Bước 3 — Xóa bIsReplaceMode ở CẢ 2 nơi** → Compile → Compiler Results liệt kê mọi node gãy.
Sửa lần lượt theo bảng quy đổi:

| Ngữ cảnh cũ | Đổi thành |
|---|---|
| Branch(bIsReplaceMode) — hỏi "có đang replace không" | Branch(IsReplaceModeActive()) |
| SET bIsReplaceMode = True — đường vào replace MESH | SET ReplaceTarget = Mesh |
| SET bIsReplaceMode = False — đường thoát | SET ReplaceTarget = None |
| Card đọc để hiện/ẩn BTN_ChangeMesh | Branch(ReplaceTarget == Mesh) |

Call site đã biết từ doc (compiler chốt danh sách thật — dùng nó, không dùng danh sách này):
StartReplaceMode, CB_Replace, đường deselect (Branch bIsReplaceMode → exit replace),
EnterReplaceMode, ExitReplaceMode, card BTN_ChangeMesh, OnMeshSelected nhánh replace,
WBP_DetailPopup.BTN_ChangeMesh (doc ghi nó SET thẳng biến — mâu thuẫn ContextMenu_Prep; compiler
sẽ phơi ra sự thật).

**Bước 4 — Mở rộng ExitReplaceMode thành đường thoát DUY NHẤT cho cả 2 mode**

```
Function ExitReplaceMode()   [WBP_FurnitureInventory]
▶→ SET ReplaceTarget = None
▶→ Regenerate All Entries(CTV_FurnitureCard)
▶→ Regenerate All Entries(CTV_ComboCard)      ← MỚI
```

Cố ý KHÔNG tạo ExitComboReplaceMode riêng. 1 đường ngược duy nhất = 6A sạch, ít state sai.

**TEST regression mesh replace (BẮT BUỘC PASS trước khi đụng combo)**

1. Select 1 đồ → right-click → Replace → click card mesh khác → đổi mesh, giữ vị trí/xoay
2. Select 2 đồ cùng mesh → Replace → cả 2 đổi, mỗi cái giữ vị trí riêng
3. Toggle Replace lần 2 → thoát mode, card ẩn BTN_ChangeMesh
4. Đang replace → deselect → thoát mode
5. BTN_Replace (WBP_MeshControls) + BTN_ChangeMesh (WBP_DetailPopup) vẫn chạy như cũ

→ 3-strike: fail cùng chỗ 3 lần → STOP, revert additive, báo cuhoang.

---

## 5. C9.b — MỞ RỘNG SpawnComboByID + DestroyComboCluster

### 5.1 BP_ComboManager — biến mới

```
Cmb_LastSpawnSucceeded : Boolean (default False)     ← KHÔNG clear ở cuối event (caller cần đọc);
                                                        có SET False ở End Play cho nhất quán
Cmb_ReplaceCenter      : Vector                       ← cho C9.c
Cmb_ReplaceActors      : Array<BP_FurnitureActor>     ← cho C9.c; CLEAR ĐẦU event + cuối event
                                                        + End Play (R4 — hard ref actor)
```

### 5.2 SpawnComboByID — 3 chỗ sửa (additive)

**(a) Thêm input param**

```
SnapshotLabel : String
```

⚠️ GOTCHA — Custom Event input KHÔNG có Default Value (khác Function). Caller cũ sau khi thêm
pin sẽ truyền "" → CaptureSnapshot("") → history có mục trống. Xử lý: ở Sub-step D dùng node
Select (pure, không exec, không cần Local Variable — vì Custom Event không có Local Variable
theo L9):

```
(SnapshotLabel == "") ●→ Select.Index
Select.True  = "SpawnCombo"
Select.False = SnapshotLabel
Select.Return ●→ CaptureSnapshot.ActionName
```

[VERIFY] UE5.5 có bổ sung default cho Custom Event input chưa — có rồi thì bỏ node Select.

**(b) ⚠️ CHỖ QUAN TRỌNG NHẤT — reset cờ ở ĐẦU Sub-step A**

```
Sub-step A, dòng ĐẦU TIÊN, TRƯỚC cả Branch(Cmb_bSpawnInFlight):
  ▶→ SET Cmb_LastSpawnSucceeded = False
```

Vì sao bắt buộc: Sub-step A có 2 đường thoát sớm (guard bSpawnInFlight, và F_LoadComboData
fail). Cả 2 đều KHÔNG chạy tới Sub-step D → nếu không reset đầu hàm, Cmb_LastSpawnSucceeded giữ
giá trị True cũ → ReplaceCombo tưởng thành công → không rollback → cụm cũ đã destroy, cụm mới
không spawn → LỖ TRỐNG trong scene. Đây chính là luật "CLEAR class var persistent ở ĐẦU
function".

**(c) Sub-step D — SET cờ ở CẢ 2 nhánh**

```
Branch(Cmb_SpawnedActors.Length == 0):
  True  ▶→ SET Cmb_LastSpawnSucceeded = False   ← MỚI
        ▶→ SET Cmb_bSpawnInFlight = False → dead-end
  False ▶→ SET Cmb_LastSpawnSucceeded = True    ← MỚI
        ▶→ DeselectAll → SelectActors → CaptureSnapshot(Select-node output) → ... (như cũ)
```

Định nghĩa fail đã chốt: 0 item spawn được = fail toàn phần → rollback. Skip lẻ tẻ vài RowName
(M11) vẫn tính success, KHÔNG rollback — giữ nguyên hành vi toast skip của K1.

### 5.3 BP_FurnitureInputManager — Function mới DestroyComboCluster

Q8: Function thuần (không latent) | IsValid từng actor trước Destroy | L2: Branch guard
early-return hợp lệ trong Function | No Latent | 6A: đường ngược = RestoreSnapshot của C9.c

```
Function DestroyComboCluster(RootGroupID : String)
Local: DestroyCombo_Actors : Array<BP_FurnitureActor>

Entry
▶→ Branch(RootGroupID == "") True ▶→ Return
▶→ GetAllDescendantActors(RootGroupID) ●→ SET DestroyCombo_Actors    ← SET copy local (luật array pass-by-ref)
▶→ ForEach DestroyCombo_Actors (a):
     Loop Body ▶→ Branch(IsValid(a)) True ▶→ Destroy Actor(Target = a)
     Completed ▶→ DeselectAll()            ← 🔴 BẮT BUỘC, xem ghi chú
               ▶→ PruneEmptyGroups()
▶→ Return
```

🔴 DeselectAll KHÔNG được bỏ. Cụm bị thay đang được SELECT (đó là cách ResolveSelectedComboRoot
tìm ra nó). Destroy xong mà không deselect thì SelectedActors / PrimarySelectedActor vẫn giữ
con trỏ tới đám actor vừa chết → ngay sau đó SpawnComboByID Sub-step D gọi DeselectAll +
SelectActors trên đống rác đó. DeleteSelected có sẵn cũng làm đúng thứ tự Destroy → DeselectAll
— đây là copy cho đủ vế sau.

Thứ tự DeselectAll TRƯỚC PruneEmptyGroups: deselect còn đụng gizmo/pivot, dọn xong mới tính
chuyện prune group.

Destroy Actor PHẢI nối Target = Array Element. Để trống = self = destroy chính InputManager
(bug đã trả giá ở DeleteSelected).

PruneEmptyGroups (v1.8) tự dọn group rỗng cả cây nested + gọi SyncGroupsToContainer → KHÔNG
cần viết đường xóa group riêng.

CỐ Ý KHÔNG CaptureSnapshot ở đây — ReplaceCombo kiểm soát để đảm bảo đúng 1 snapshot.

KHÔNG tái dùng DeleteSelected vì nó chạy trên SelectedActors + tự capture "Delete" → dư 1
snapshot rác.

**TEST C9.b — xác nhận đồng bộ (3 node, quyết định thiết kế C9.c)**

Tạm thêm vào chỗ gọi thử:

```
Print "A" → SpawnComboByID(...) → Print "B=" + Cmb_LastSpawnSucceeded
Sub-step D: thêm tạm Print "D"
Thứ tự A, D, B  → ĐỒNG BỘ ✅ → giữ nguyên thiết kế C9.c
Thứ tự A, B, D  → ASYNC ❌  → DỪNG, báo cuhoang (phải đổi sang bind dispatcher)
```

Xóa 3 Print sau khi xác nhận.

---

## 6. C9.c ⭐ — ReplaceCombo (LÕI — làm trước UI)

Q8: Custom Event (đồng bộ với SpawnComboByID; Custom Event → KHÔNG Local Variable, dùng class
var Cmb_) | IsValid ComboManager/UndoManager qua ref có sẵn | L2: mọi nhánh kết thúc bằng
toast/dead-end có chủ đích, 2 nhánh success/fail merge về CLEAR | No Latent (đã verify ở C9.b) |
6A: fail → RestoreSnapshot tự động; success → đúng 1 snapshot "ReplaceCombo" để Undo được

```
Custom Event ReplaceCombo(RootGroupID : String, NewComboID : String)   [BP_ComboManager]

0 ▶→ CLEAR Cmb_ReplaceActors          ← luật "CLEAR class var persistent ở ĐẦU function".
                                         Không clear → giữ hard ref actor của lần replace TRƯỚC
                                         suốt thời gian giữa 2 lần gọi (vi phạm R4).

1 ▶→ Branch(Cmb_bSpawnInFlight)
       True  ▶→ ToastRef.ShowToast("Đang xử lý, thử lại sau", 2.5) → dead-end
       False ▶→ (tiếp)
       ⚠️ CHỈ ĐỌC — TUYỆT ĐỐI KHÔNG SET cờ này. Sub-step A của SpawnComboByID cũng check đúng
          biến đó; nếu ReplaceCombo SET True thì SpawnComboByID sẽ tự chặn chính nó → replace
          chết câm, không lỗi, rất khó tìm.

2 ▶→ Branch(RootGroupID == "" OR NewComboID == "") True ▶→ dead-end

3 ▶→ InputManagerRef.GetAllDescendantActors(RootGroupID) ●→ SET Cmb_ReplaceActors

4 ▶→ Branch(Cmb_ReplaceActors.Length == 0)
       True  ▶→ ToastRef.ShowToast("Cụm rỗng — không thay được", 2.5) → dead-end
       False ▶→ InputManagerRef.CalculateCenter(Cmb_ReplaceActors) ●→ SET Cmb_ReplaceCenter
       ⚠️ Guard này BẮT BUỘC: CalculateCenter chia cho Length (V4). Length==0 → chia 0 →
          trả (0,0,0) → combo mới spawn ở GỐC TỌA ĐỘ THẾ GIỚI. Không crash nên rất dễ lọt.

5 ▶→ InputManagerRef.DestroyComboCluster(RootGroupID)

6 ▶→ SpawnComboByID(ComboID=NewComboID, SpawnLocation=Cmb_ReplaceCenter,
                    SnapshotLabel="ReplaceCombo")

7 ▶→ Branch(Cmb_LastSpawnSucceeded)
       True  ▶→ (không làm gì — snapshot đã capture bên trong SpawnComboByID)
       False ▶→ UndoManagerRef.RestoreCurrentSnapshot()
             ▶→ ToastRef.ShowToast("Thay thế thất bại — đã khôi phục cụm cũ", 2.5)
   [2 nhánh MERGE] ▶→ CLEAR Cmb_ReplaceActors
```

Toast trong BP_ComboManager: phải gọi thẳng Get Game Instance → Cast Foff_GameInstance →
IsValid(ToastRef) → ToastRef.ShowToast(...). KHÔNG dùng ShowToastMsg (đó là Function của
WBP_FurnitureInventory, Actor không gọi được) — đúng như K1 chỗ #6 đã làm.

### 6.1 BP_UndoManager — Custom Event mới RestoreCurrentSnapshot

```
Custom Event RestoreCurrentSnapshot()
▶→ Is Valid Index(SnapshotHistory, CurrentIndex) ●→ Branch
     True  ▶→ RestoreSnapshot(IndexHistory = CurrentIndex)
     False ▶→ dead-end (không có gì để khôi phục)
```

Guard Is Valid Index bắt buộc: CurrentIndex sai (history rỗng, hoặc bị trừ quá tay ở nhánh
Length >= MaxSteps trong CaptureSnapshot) → truy cập mảng ngoài phạm vi. Vì sao tách hàm 1 node:
không phải mở public biến CurrentIndex ra ngoài; ngữ nghĩa rõ ("khôi phục trạng thái hiện tại,
KHÔNG dịch con trỏ history") — khác hẳn Undo/Redo vốn dịch con trỏ TRƯỚC khi gọi (V3). Dùng lại
được cho mọi rollback sau này.

### 6.2 Phím debug tạm (xóa ở C9.f)

```
BP_ComboManager: + Cmb_DebugTargetComboID : String   ← gõ 1 ComboID thật vào Defaults
Key Event "8" (tránh F8 = eject PIE):
  ▶→ InputManagerRef.ResolveSelectedComboRoot() ●→ RootGID, OldComboID, bFound
  ▶→ Branch(bFound)
       True  ▶→ ReplaceCombo(RootGID, Cmb_DebugTargetComboID)
       False ▶→ Print "Chưa chọn cụm combo"
```

Dùng luôn ResolveSelectedComboRoot (đã xong ở C9.2) → test đúng đường thật, không giả lập.

**TEST C9.c (3 case — PASS mới sang C9.d)**

1. Spawn combo A → click chọn cụm → phím 8 → cụm A biến, combo B spawn ĐÚNG chỗ cũ
   → Ctrl+Z → cụm A quay lại nguyên vẹn (group + SourceComboID)
2. Đổi Cmb_DebugTargetComboID thành ID không tồn tại (hoặc JSON hỏng) → phím 8
   → cụm A CÒN NGUYÊN, scene KHÔNG có lỗ trống, toast "Thay thế thất bại…" hiện
3. Bấm phím 8 hai lần thật nhanh → lần 2 bị guard chặn, toast "Đang xử lý…"
4. ⚠️ **Kiểm orphan group (im lặng, dễ lọt):** thêm tạm Print `InputManagerRef.Groups.Length`
   ngay TRƯỚC bước 5 và ngay SAU bước 6 trong ReplaceCombo. Replace 3 lần liên tiếp.
   → Số group SAU mỗi lần replace phải ỔN ĐỊNH, KHÔNG tăng dần.
   → Tăng dần = `PruneEmptyGroups` chạy quá sớm (actor vừa Destroy chưa biến khỏi
     `Get All Actors With Tag` trong cùng frame) → group rỗng không được dọn → mỗi lần replace
     đẻ thêm 1 entry rác. Không có triệu chứng ngay, chỉ lộ sau này ở EMS save phình / selection
     kỳ quặc. Nếu gặp: báo cuhoang, KHÔNG tự vá — cần bàn (có thể phải Delay 1 tick trước Prune).

---

## 7. C9.d — MODE COMBO (inventory)

Q8: StartReplaceComboMode = Function (không latent) → có Local Variable | IsValid InvRef +
ComboManager | L2: nhánh load-fail merge về đường mở inventory, không dead-end giữa chừng |
No Latent | 6A: đường ngược = ExitReplaceMode (đã mở rộng ở C9.0c)

### 7.1 BP_FurnitureInputManager — biến mới

```
ComboRootGroupIDToReplace : String (default "")
```

### 7.2 BP_FurnitureInputManager — Function StartReplaceComboMode

Mirror y hệt cấu trúc 3 nhánh của StartReplaceMode (V6). KHÔNG gộp helper (KP3).

```
Function StartReplaceComboMode(RootGroupID : String, ComboID : String)
Local: SRC_FolderPath (String), SRC_InvRef (WBP_FurnitureInventory),
       SRC_ComboData (FComboData), SRC_bOK (Boolean)

▶→ Branch(RootGroupID == "" OR ComboID == "") True ▶→ Return
▶→ SET ComboRootGroupIDToReplace = RootGroupID
▶→ CLEAR MeshesToReplace                    ← kỷ luật: mode này xóa payload của mode kia
▶→ SET ReplaceTarget = Combo

← đọc FolderPath của combo GỐC để navigate tới đúng thư mục
▶→ Get All Actors Of Class(BP_ComboManager) → Get(0) → IsValid
     True  ▶→ F_LoadComboData(ComboID) → (OutData, bSuccess) ●→ SET SRC_ComboData, SRC_bOK
     False ▶→ SET SRC_bOK = False
▶→ Branch(SRC_bOK)
     True  ▶→ Break FComboData → FolderPath ●→ SET SRC_FolderPath
     False ▶→ SET SRC_FolderPath = "__ALL__"     ← vẫn mở inventory, không chết giữa chừng
   [merge]

← khối 3 nhánh inventory — COPY cấu trúc StartReplaceMode (V6)
▶→ Get Game Instance → Cast Foff_GameInstance → GET FurnitureInventoryRef ●→ SET SRC_InvRef
▶→ Branch(IsValid(SRC_InvRef))
     True  ▶→ Branch(SRC_InvRef.IsInViewport())
                True  ▶→ [KHỐI CUỐI]
                False ▶→ [KHỐI TẠO WIDGET] ▶→ [KHỐI CUỐI]
     False ▶→ [KHỐI TẠO WIDGET] ▶→ [KHỐI CUỐI]

[KHỐI TẠO WIDGET]  (copy từ StartReplaceMode)
  Create Widget(WBP_FurnitureInventory) → AddToViewport(ZOrder=0)
  → SET PlayerController.bShowMouseCursor = True
  → GameInstance.FurnitureInventoryRef = widget mới → SET SRC_InvRef

[KHỐI CUỐI]  ← THỨ TỰ BẮT BUỘC, không đảo
  SRC_InvRef.SwitchInventoryMode(Combo)
  → SET SRC_InvRef.ReplaceTarget = Combo
  → SRC_InvRef.FilterComboByFolder(SRC_FolderPath)
  → SRC_InvRef.RefreshComboCardReplaceMode()
```

[VERIFY] F_LoadComboData là Function trong BP_ComboManager — xác nhận gọi được từ ngoài
(Blueprint Function mặc định public, nhưng kiểm cho chắc). Nếu private → đổi sang public, KHÔNG
viết hàm load thứ 2.

⚠️ Thứ tự Filter TRƯỚC Refresh là bắt buộc — bài học từ mesh: FilterComboByFolder dựng lại toàn
bộ card, nếu Regenerate chạy trước thì bị xóa sạch, nút không hiện.

ℹ️ RefreshComboCardReplaceMode ở đây có thể thừa: FilterComboByFolder kết thúc bằng
Set List Items → TileView tạo entry mới → OnListItemObjectSet tự chạy → nút tự hiện đúng. Giữ
lại cho chắc; nếu thấy card nháy/giật thì bỏ dòng này (hàm vẫn cần cho ExitReplaceMode).

⚠️ SwitchInventoryMode(Combo) bên trong nó đã gọi FilterComboByFolder("__ALL__") → mình gọi lần
2 với FolderPath thật → build 2 lần trong 1 frame. Chấp nhận (kết quả cuối đúng), ghi
DEVIATIONS. KHÔNG sửa SwitchInventoryMode (hàm dùng chung — KP3).

⚠️ FolderPath == "" là giá trị HỢP LỆ (= "Chưa phân loại"), KHÔNG đổi thành "__ALL__". Chỉ dùng
"__ALL__" khi load combo gốc THẤT BẠI.

### 7.3 WBP_FurnitureInventory — Function mới

```
Function RefreshComboCardReplaceMode()
▶→ Regenerate All Entries(CTV_ComboCard)
```

---

## 8. C9.e — CB_Replace ROUTE 2 NHÁNH

Q8: Custom Event có sẵn, chỉ thêm/đổi node | IsValid ContextMenuRef giữ nguyên | L2: nhánh
toggle-off giờ KHÔNG cần Branch mesh/combo (1 đường duy nhất) | No Latent | 6A: toggle-off =
đường ngược, đã hợp nhất ở ExitReplaceMode

Đường thoát (nhánh IsReplaceModeActive() == True) — hợp nhất, KHÔNG branch mesh/combo:

```
▶→ SET ReplaceTarget = None
▶→ CLEAR MeshesToReplace
▶→ SET ComboRootGroupIDToReplace = ""
▶→ [đường lấy InvRef có sẵn] → InvRef.ExitReplaceMode()
```

🟠 CB_Replace KHÔNG phải đường thoát duy nhất. Ít nhất còn đường deselect (OnLMBReleased:
DeselectAll + CaptureSnapshot("Deselect") → Branch bIsReplaceMode → exit replace). Compiler sẽ
bắt sửa chỗ đó vì nó đọc biến vừa xóa — nhưng nó KHÔNG tự biết phải clear thêm
ComboRootGroupIDToReplace.

Việc phải làm: dùng danh sách Find References từ C9.0c Bước 0, rà MỌI chỗ thoát replace mode,
đảm bảo chỗ nào cũng làm đủ 4 dòng như trên. Bỏ sót → mode thoát trên màn hình nhưng
ComboRootGroupIDToReplace còn giữ GroupID của cụm đã chết. Hiện tại vô hại (vì
ExecuteComboReplace guard ReplaceTarget != Combo trước), nhưng là mìn cho tính năng sau.

Đường vào (nhánh False) — tại chỗ đang nối thẳng StartReplaceMode(SelectedActors):

```
▶→ ResolveSelectedComboRoot() ●→ RootGID, OldComboID, bFound
▶→ Branch(bFound)
     True  ▶→ StartReplaceComboMode(RootGID, OldComboID)      ← NHÁNH MỚI
     False ▶→ StartReplaceMode(SelectedActors)                 ← node CŨ, giữ nguyên
```

Giữ nguyên 2 guard có sẵn phía trước (IsValid(PrimarySelectedActor) và
SelectedActors.Length > 0) — KHÔNG đụng.

---

## 9. C9.f — CARD + ExecuteComboReplace

Q8: ExecuteComboReplace = Function (không latent) | IsValid ComboManager + guard ReplaceTarget |
L2: mọi nhánh guard đều Return | No Latent | 6A: replace xong re-resolve để replace tiếp được
(đối xứng mesh — Luật 6B)

### 9.1 BP_FurnitureInputManager — Function ExecuteComboReplace

```
Function ExecuteComboReplace(NewComboID : String)
Local: ECR_RootGID2 (String), ECR_ComboID2 (String), ECR_bFound2 (Boolean)

▶→ Branch(ReplaceTarget != Combo) True ▶→ Return
▶→ Branch(ComboRootGroupIDToReplace == "") True ▶→ Return
▶→ Branch(NewComboID == "") True ▶→ Return
▶→ Get All Actors Of Class(BP_ComboManager) → Get(0) → IsValid
     False ▶→ Return
     True  ▶→ ReplaceCombo(ComboRootGroupIDToReplace, NewComboID)

← cập nhật target để replace TIẾP được (mesh cũng làm vậy — Luật 6B)
▶→ ResolveSelectedComboRoot() ●→ ECR_RootGID2, ECR_ComboID2, ECR_bFound2
▶→ Branch(ECR_bFound2)
     True  ▶→ SET ComboRootGroupIDToReplace = ECR_RootGID2
     False ▶→ SET ComboRootGroupIDToReplace = ""
▶→ Return
```

Đoạn re-resolve chạy đúng cho CẢ 2 kết cục: success → cụm mới đang được select
(SpawnComboByID tự SelectActors) → lấy RootGID mới; fail → RestoreSnapshot đã khôi phục cụm cũ
với đúng GroupID cũ → lấy lại chính nó. Phụ thuộc kết quả TEST C9.b (đồng bộ). Nếu hóa ra async
→ bỏ đoạn re-resolve, thay bằng ExitReplaceMode() sau replace (đơn giản hơn, ghi DEVIATIONS).

### 9.2 WBP_ComboCard — BTN_ChangeCombo (nút ĐÃ TỒN TẠI, Visibility=Hidden — V2)

OnListItemObjectSet — nối thêm vào CUỐI chuỗi hiện có:

```
▶→ Branch(IsValid(InventoryRef))
     True  ▶→ Branch(InventoryRef.ReplaceTarget == Combo)
                True  ▶→ SetVisibility(BTN_ChangeCombo, Visible)
                False ▶→ SetVisibility(BTN_ChangeCombo, Hidden)
     False ▶→ SetVisibility(BTN_ChangeCombo, Hidden)
```

Dùng Hidden (không phải Collapsed) làm trạng thái tắt → 3 nút còn lại trong HB_Buttons không xê
dịch khi bật/tắt. Giữ đúng như thiết kế gốc. InventoryRef đã có lazy-init sẵn trong
OnListItemObjectSet từ v1.1 — không thêm mới.

BTN_ChangeCombo — OnClicked:

```
▶→ Get All Actors Of Class(BP_FurnitureInputManager) → Get(0) → IsValid
     True ▶→ ExecuteComboReplace(NewComboID = ComboItem.ComboID)
```

Card gọi đúng 1 node (QĐ2). KHÔNG copy pattern inline destroy/spawn của
WBP_DragOverlay_FurnitureCard. Pattern Get All Actors Of Class(InputManager) đã được chính card
này dùng ở OnDragDetected — không phải plumbing mới.

### 9.3 Dọn dẹp

Xóa phím debug 8, Cmb_DebugTargetComboID, và mọi Print tạm của C9.b/C9.c.

---

## 10. TEST C9 ĐẦY ĐỦ (5 + 2 case)

1. Spawn A → chọn cụm → right-click → Replace → inventory mở tab Combo, đúng folder của A,
   card hiện nút thay → click combo B → A biến, B đứng ĐÚNG Center cũ
   → Ctrl+Z → A quay lại nguyên vẹn (group + SourceComboID)
2. Replace bằng combo JSON hỏng / ID không tồn tại → RestoreSnapshot tự chạy → A còn nguyên,
   scene KHÔNG lỗ trống, toast hiện. KHÔNG có snapshot rác thêm vào history.
3a. KHÔNG select gì → right-click → Replace → **không có gì xảy ra** (guard
    `IsValid(PrimarySelectedActor)` có sẵn chặn TRƯỚC nhánh mới — không tới
    ResolveSelectedComboRoot, không toast). Đây là hành vi ĐÚNG, không phải bug.
3b. Select 1 đồ LẺ (không thuộc combo) → Replace → rơi nhánh mesh cũ, inventory mở tab Furniture
    như trước. KHÔNG destroy gì, KHÔNG toast combo.
4. Replace liên tiếp 2 lần thật nhanh → lần 2 bị guard Cmb_bSpawnInFlight chặn
5. Replace → Save EMS → thoát → Load → cụm mới còn nguyên, SourceComboID = NewComboID
6. Toggle Replace lần 2 khi đang ở combo mode → thoát sạch, BTN_ChangeCombo ẩn lại,
   ComboRootGroupIDToReplace = ""
7. Regression: replace MESH vẫn chạy đủ 5 case của C9.0c
8. **Replace khi đang trong Edit Mode của chính cụm đó** → `SpawnComboByID` Sub-step A tự
   `ExitEditModeFull` → edit bar tắt, replace chạy bình thường, Undo sau đó không kẹt edit mode
   (snapshot V4 có `EditModeStackSnapshot`).
9. **Combo gốc đã bị xóa khỏi thư viện** (dùng Delete Combo xóa combo A, cụm A vẫn còn trong
   scene) → chọn cụm → Replace → `F_LoadComboData` fail → inventory vẫn mở tab Combo ở
   `__ALL__`, KHÔNG crash, replace bằng combo khác vẫn được.
10. **Replace bằng CHÍNH combo đang dùng** (NewComboID == OldComboID) → destroy rồi spawn lại
    cùng combo tại đúng Center. Chấp nhận được (coi như refresh), không cần guard riêng.

---

## 11. GHI DEVIATIONS (ceiling + trigger)

| Lệch | Ceiling | Upgrade trigger |
|---|---|---|
| StartReplaceComboMode mirror 3 nhánh trùng lặp của StartReplaceMode | 2 replace target | Thêm target thứ 3 → tách helper EnsureInventoryOpen() dùng chung |
| FilterComboByFolder chạy 2 lần trong 1 frame (SwitchInventoryMode + explicit) | Không thấy nháy UI | Thấy nháy/giật → thêm param bSkipInitialFilter cho SwitchInventoryMode |
| SnapshotLabel phải qua node Select vì Custom Event không có default param | UE5.5 | UE bản mới hỗ trợ default → bỏ node Select |
| CalculateCenter không loại pivot/container (as-built, doc cũ mô tả sai) | Mọi caller đều truyền mảng đã lọc theo tag FurnitureSpawned | Có caller truyền mảng lẫn actor khác → thêm bước lọc trong hàm |

---

## 12. KHÔNG ĐƯỢC LÀM (KP3 — surgical only)

- ❌ KHÔNG sửa Phát hiện A (StartReplaceMode guard bằng PrimarySelectedActor nhưng đọc
  RowName/DAPath từ SelectedFurnitureActor). Ghi nhận vào doc, ngoài scope C9.
- ❌ KHÔNG refactor 3 nhánh trùng lặp của StartReplaceMode thành helper.
- ❌ KHÔNG đụng logic inline destroy/spawn trong WBP_DragOverlay_FurnitureCard.BTN_ChangeMesh.
- ❌ KHÔNG thêm field mới vào FComboData / S_GroupData.
- ❌ KHÔNG sửa SwitchInventoryMode (hàm dùng chung 3 mode).
- ❌ KHÔNG chuẩn bị trước gì cho C9.5 / C11 (KP2). ResolveSelectedComboRoot đã là tất cả những
  gì C9.5 cần kế thừa.

---

## 13. DOC CẦN CẬP NHẬT KHI MERGE (Claude Code)

- `Blueprints/BP_UndoManager.md` — bIsRestoring (B1 fix), RestoreCurrentSnapshot, ghi rõ
  RestoreSnapshot(Index) không tự dịch con trỏ.
- `Blueprints/BP_ComboManager.md` — SpawnComboByID +SnapshotLabel +Cmb_LastSpawnSucceeded (reset
  đầu Sub-step A!), ReplaceCombo, 3 class var mới.
- `Blueprints/BP_FurnitureInputManager.md` — ReplaceTarget (thay bIsReplaceMode),
  IsReplaceModeActive, ComboRootGroupIDToReplace, DestroyComboCluster, StartReplaceComboMode,
  ExecuteComboReplace, CB_Replace 2 nhánh. Sửa mô tả sai: CalculateCenter không loại
  pivot/container; FindGroupData không có Index; StartReplaceMode không có EnsureExpanded + ghi
  chú Phát hiện A.
- `Widgets/WBP_FurnitureInventory.md` — ReplaceTarget, ExitReplaceMode mở rộng 2 CTV,
  RefreshComboCardReplaceMode.
- `Widgets/WBP_ComboCard.md` — BTN_ChangeCombo handler + gate Visibility.
- `Data/Data_Structures.md` — enum E_ReplaceTarget.
- `Bugs/Open_Bugs.md` — B1 → RESOLVED.
- `00_Core/DEVIATIONS.md` — 4 mục ở §11.
- `00_Core/01_Session_State.md` + `PROGRESS.md` — C9 DONE, tiếp theo C9.5 Save As/Save đè (UX
  vẫn CHƯA CHỐT — bàn trước khi lên task card).
