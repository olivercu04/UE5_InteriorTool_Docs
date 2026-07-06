# Post-C5 Execution Plan — K1 → Gate 1.5
**Version:** 1.0 | **Cập nhật:** 05/07/2026
**Phạm vi:** chuỗi chốt 03/07 sau khi C5 DONE: **K1 Toast → K3 bAddToRecent → P1 Thumbnail (plan riêng, chỉ ghi interface) → C9 Replace → C6 Fav/Recent → C7 DetailPopup → C11 Export/Import → C10 Regression → Gate 1.5 Packaged Smoke (+quyết P4)**.
**Thực thi:** Sonnet step-by-step. Mỗi gate test-and-confirm, PASS mới sang gate sau.
**Nguồn quyết định gốc:** DEVIATIONS 23/06 (K1/K3/K5/P4), Combo_Execution.md (C9/C11 mấu chốt), Open_Bugs.md (K3).

---

## 0. LUẬT THỰC THI (Sonnet ĐỌC TRƯỚC)

1. Thứ tự **K1 → K3 → P1 → C9 → C6 → C7 → C11 → C10 → G1.5**. Mỗi gate xong → dừng → "Làm xong báo tao" + test cụ thể.
2. Node flow bằng lời: `▶→` execution, `●→` data. Q8 self-check VISIBLE trước mỗi flow.
3. Print debug trên MAIN line, gate `bDebugMode`. Từ K1 trở đi: feedback user-facing = **ShowToast**, Print chỉ còn cho debug.
4. Bug fail 3 lần → STOP. Lệch plan → DEVIATIONS.md ngay.
5. **[VERIFY]** = soi Blueprint/code thật trước khi làm. Lệch → hỏi cuhoang.
6. Pattern menu action: `AddMenuItem → capture Item → Bind OnItemClicked → CB_X`; trong CB_ cache data TRƯỚC Hide (chuẩn C5).

## 0b. GIẢ ĐỊNH KP1 — cuhoang confirm trước khi chạy C9

| # | Giả định | Nếu sai |
|---|---|---|
| A1 | **P3 (xoay combo)** không nằm trong chuỗi này → backlog sau Gate 1.5 | Chèn P3 giữa P1 và C9 |
| A2 | **C9 entry** = phương án A (mục C9.1): context menu ComboCard, hiện khi selection hiện tại là cụm combo | Đổi sang phương án B (nút trên info bar) |
| A3 | **P4** chưa áp — `GetCombosDir` vẫn `ProjectSavedDir/Combos`; đổi + migrate ở Gate 1.5 **[VERIFY đầu G1.5: đọc ComboSerializer.cpp xác nhận]** | Nếu đã là LOCALAPPDATA → G1.5 bỏ bước P4, chỉ smoke |

---

# ═══════════════════════════════════════════════
# K1 — WBP_TOAST (nền feedback cho mọi gate sau)
# ═══════════════════════════════════════════════

**Mục tiêu:** 1 widget toast dùng chung — C5 folder ops, C9 replace fail, C11 import rác, M11 thiếu mesh đều trỏ vào đây. Dùng **FText** (chuẩn bị i18n).

## Quyết định thiết kế (chốt luôn, không bàn khi thực thi)
- **Single instance** — tạo 1 lần, giữ ref trong `Foff_GameInstance` (pattern FurnitureInventoryRef). Toast mới đè toast cũ + reset timer (v1 không queue).
- Vị trí: đáy giữa màn hình (anchor bottom-center, offset Y ~-120).
- Tự ẩn sau `Duration` (default 2.5s) bằng **Set Timer by Event** (KHÔNG Delay trong Function — L8; toast logic nằm trong Custom Event nên timer hợp lệ và reset được).
- Widget KHÔNG giữ ref Actor nào (R2 thỏa hiển nhiên).

## K1.1 — Widget WBP_Toast
### Q8 self-check
```
Q8: Custom Event ShowToast (timer OK) | không ref Actor | L2: nhánh timer-đang-chạy merge về SetText | latent = Set Timer by Event trong Custom Event ✓ | 6A: tự ẩn + toast mới đè cũ
```
### Layout
```
Canvas Panel (root, Not Hit-Testable — toast KHÔNG chặn chuột)
└─ Border_Toast (anchor bottom-center, padding 12/8, bo góc, nền đen alpha 0.75, Visibility=Collapsed mặc định)
   └─ TXT_Message (Text, màu trắng, Auto Wrap, max width ~480)
```
### Variables & logic
| Tên | Kiểu | Ghi chú |
|---|---|---|
| HideTimerHandle | Timer Handle | để Clear khi toast mới đè |

```
Custom Event ShowToast(Message : Text, Duration : Float = 2.5):
  ▶→ Clear and Invalidate Timer by Handle(HideTimerHandle)     ← toast cũ đang đếm → hủy
  ▶→ SetText(TXT_Message, Message)
  ▶→ SetVisibility(Border_Toast, HitTestInvisible)
  ▶→ Set Timer by Event(HideToast, Time=Duration, Looping=False) ●→ SET HideTimerHandle

Custom Event HideToast():
  ▶→ SetVisibility(Border_Toast, Collapsed)
```
> Fade animation = polish Sprint 6, v1 hiện/ẩn cứng — không chặn tiến độ.

## K1.2 — Global access + helper
1. `Foff_GameInstance` thêm var `ToastRef : WBP_Toast (Object Ref)`.
2. Tạo toast 1 lần trong **WBP_FOFF_ToolDemo Event Construct** (nối tiếp Then có sẵn — KHÔNG chen giữa spawn order): Create Widget(WBP_Toast) → Add to Viewport (ZOrder=100, trên mọi dialog) → SET GameInstance.ToastRef.
3. **WBP_FurnitureInventory** thêm helper (để mọi flow trong inventory gọi 1 node):
```
Function ShowToastMsg(Message : Text):
  GetGameInstance → Cast Foff_GameInstance → GET ToastRef → IsValid Branch
    True  ▶→ ToastRef.ShowToast(Message, 2.5)
    False ▶→ Print String(Message)          ← fallback, không nuốt thông báo
```
> BP_ComboManager / InputManager cần toast → gọi qua GameInstance y hệt (không tạo helper trùng nếu chỉ dùng 1-2 chỗ).

## K1.3 — Thay các Print user-facing hiện có (surgical — CHỈ các dòng này)
| Chỗ | Print cũ | Thành |
|---|---|---|
| HandleNewFolderConfirmed / OnRequestNewFolder nhánh False | "Không tạo được: ..." | ShowToastMsg |
| HandleDeleteFolderConfirmed | "Đã xóa folder, N combo..." | ShowToastMsg |
| HandleMoveComboConfirmed nhánh False | "UpdateComboFolder failed..." | ShowToastMsg |
| SpawnComboByID — skip item RowName bậy (M11) | Print skip | ShowToast qua GameInstance |
> Print gated bDebugMode thuần debug → GIỮ NGUYÊN, không đụng (KP3).

## TEST K1 (5 case)
1. Gọi ShowToastMsg từ nút debug → toast hiện đáy giữa, tự ẩn sau ~2.5s.
2. Gọi 2 lần cách nhau 1s → toast 2 đè toast 1, đếm lại từ đầu (không ẩn sớm).
3. Toast hiện → click xuyên qua được (không chặn chuột).
4. Xóa folder → toast "Đã xóa folder..." thay Print.
5. Spawn combo có RowName bậy → toast skip hiện (M11).

→ **Làm xong báo tao + 5 case. Doc: WBP_Toast.md tạo mới, Foff_GameInstance ghi chú, bump Inventory.**

---

# ═══════════════════════════════════════════════
# K3 — FIX bAddToRecent (bug có sẵn, không chỉ combo)
# ═══════════════════════════════════════════════

**Root cause (Open_Bugs.md):** `SpawnFurnitureCopy` gọi `AddRecentMesh` unconditional → spawn combo nhồi N mesh lẻ vào Recent; mỗi Undo (RestoreSnapshot → SpawnFurnitureCopy) nhồi thêm.

## Q8 self-check
```
Q8: sửa Function SpawnFurnitureCopy + 2 caller | param default=True → caller cũ không đổi hành vi | L2: Branch(bAddToRecent) False merge về flow sau | No latent mới | 6A: không đổi đường ngược nào
```

## Thực thi (3 chỗ, đúng 3 chỗ — KP3)
1. **SpawnFurnitureCopy** (InputManager): thêm input param `bAddToRecent : Boolean, Default = True`. Tại chỗ gọi AddRecentMesh:
```
▶→ Branch(bAddToRecent)
     True  ▶→ AddRecentMesh(...)   ← như cũ
     False → (merge về node sau)
```
2. **SpawnComboByID Phase 3** (BP_ComboManager): pin `bAddToRecent = False` tại node gọi SpawnFurnitureCopy.
3. **RestoreSnapshot** (BP_UndoManager): pin `bAddToRecent = False` **[VERIFY: RestoreSnapshot gọi SpawnFurnitureCopy trực tiếp hay qua event trung gian — soi rồi pin đúng node]**.
> Paste/Duplicate: KHÔNG đụng — default True tự đúng.

## TEST K3 (4 case)
1. Ghi lại Recent hiện tại → spawn combo 5 món → Recent KHÔNG đổi.
2. Undo/Redo vài lần → Recent KHÔNG đổi.
3. Spawn 1 furniture từ card → Recent CÓ mesh đó (hành vi cũ nguyên).
4. Copy/paste 1 actor → Recent cập nhật như trước.

→ **Làm xong báo tao. Open_Bugs.md: K3 → RESOLVED.**

---

# ═══════════════════════════════════════════════
# P1 — THUMBNAIL C++ (plan riêng đã có — chỉ ghi INTERFACE các gate sau phụ thuộc)
# ═══════════════════════════════════════════════

Thực thi theo **plan P1_ComboThumbnail** (không lặp lại ở đây). Sau P1 PASS, các gate sau dựa vào 3 hợp đồng:
1. File thumbnail = `<CombosDir>/<comboID>.png` (cạnh JSON, không subfolder).
2. C++ `LoadTexture2DFromFile(Path) → Texture2D` gọi được từ BP (C4 card + C7 popup dùng).
3. Capture chạy NGAY sau SaveComboFromSelection thành công (đồ còn trong scene).

**Fallback nếu P1 kẹt (M5/M6):** card + popup giữ icon 🧩 — C9/C6/C11 KHÔNG bị chặn (chỉ C7 hiển thị xấu hơn). Ghi DEVIATIONS, đi tiếp.

---

# ═══════════════════════════════════════════════
# C9 — REPLACE COMBO (verify K2 → entry → flow → rollback)
# ═══════════════════════════════════════════════

**Mục tiêu:** chọn 1 cụm combo trong scene → chọn combo khác trong library → cụm cũ biến, combo mới spawn ĐÚNG vị trí cũ. Fail → tự khôi phục, không lỗ trống.

## C9.0 — Verify K2 (BẮT BUỘC trước khi code — quyết định 23/06)
Test tay, không code:
1. Spawn combo → Save scene EMS → thoát → Load → select cụm → Print `SourceComboID` của root group → đúng ComboID gốc.
2. Spawn combo → Undo → Redo → Print SourceComboID → còn nguyên (M13).
FAIL bất kỳ → STOP, fix S_GroupData snapshot/EMS trước (không đi tiếp C9 trên nền hỏng).

## C9.1 — Entry point (giả định A2)
**Phương án A (mặc định):** right-click WBP_ComboCard → menu Combo mode hiện có (đang có 1 item "Chuyển vào folder…") thêm item thứ 2:
```
OnComboCardRightClicked: sau Item1, nối tiếp:
  ▶→ LibMenu.AddMenuItem("🔁 Thay cụm đang chọn", "") ●→ Item2
  ▶→ Bind Item2.OnItemClicked → CB_ReplaceCombo
```
Ngữ nghĩa: combo trên card = combo MỚI; cụm đang select trong scene = cụm bị thay.
**Phương án B (nếu A2 sai):** nút "Thay bằng combo khác…" trên info bar khi select cụm combo → mở tab Combo. Phức tạp hơn — chỉ làm nếu cuhoang chọn.

## C9.2 — Tìm cụm bị thay từ selection
### Q8 self-check
```
Q8: Function thuần ResolveSelectedComboRoot | IsValid từng actor + group lookup | L2: mọi nhánh return | No latent | 6A: không sửa state — chỉ đọc
```
```
Function ResolveSelectedComboRoot() → RootGroupID : String, ComboID : String, bFound : Boolean   [BP_FurnitureInputManager]
  Lấy selection hiện tại → đi lên root group (tái dùng GetPathToRoot/ResolveSelectionUnit sẵn có — [VERIFY] hàm nào trả root group của selection)
  → GET group.SourceComboID
  → Branch(SourceComboID == "") → True: return bFound=False
  → return RootGroupID, SourceComboID, bFound=True
```

## C9.3 — Flow replace (BP_ComboManager — Custom Event, thứ tự BẮT BUỘC theo Combo_Execution)
### Q8 self-check
```
Q8: Custom Event (async spawn callback) | guard Cmb_bSpawnInFlight đầu event | IsValid actors trước destroy | L2: nhánh fail merge về toast | latent = đợi OnComboSpawned ✓ | 6A: fail → RestoreSnapshot tự động; thành công → CaptureSnapshot("ReplaceCombo") để Undo được
```
```
CB_ReplaceCombo (Inventory):
  ▶→ cache NewComboID = LibraryMenuRef... (pattern chuẩn: cache TRƯỚC Hide) → Hide → None
  ▶→ InputManager.ResolveSelectedComboRoot() ●→ RootGID, OldComboID, bFound
  ▶→ Branch(bFound == False) → True: ShowToastMsg("Chọn 1 cụm combo trong scene trước") → [end]
  ▶→ ComboManager.ReplaceCombo(RootGID, NewComboID)

ReplaceCombo(RootGID, NewComboID) — Custom Event [BP_ComboManager]:
  1 ▶→ Branch(Cmb_bSpawnInFlight) → True: [dead-end]
  2 ▶→ CalculateCenter( GetAllDescendantActors(RootGID) ) ●→ SET Cmb_ReplaceCenter
       ← CalculateCenter = hàm CHUNG (đã dùng gizmo/copy-paste); loại pivot dummy + container TRƯỚC khi average
       ← tính TRƯỚC destroy — sau destroy không còn gì để tính
  3 ▶→ Destroy toàn bộ actors cụm + gỡ group RootGID (tái dùng đường xóa group sẵn có — [VERIFY] tên event/function xóa cụm)
  4 ▶→ SpawnComboByID(NewComboID, Cmb_ReplaceCenter)   ← đường spawn DUY NHẤT, không nhánh riêng
  5 ▶→ (callback OnComboSpawned thành công) ▶→ CaptureSnapshot("ReplaceCombo")
  6 ▶→ (spawn fail: JSON lỗi / 0 item spawn được)
       ▶→ RestoreSnapshot(đỉnh stack)                  ← TỰ ĐỘNG, không bắt user Undo tay
       ▶→ ShowToast("Thay thế thất bại — đã khôi phục combo cũ")
       ▶→ KHÔNG CaptureSnapshot
```
- Rotation v1 reset 0 (giữ rotation = backlog, ghi DEVIATIONS nếu cuhoang muốn sau).
- KHÔNG capture "PreReplace" riêng — state cũ đã nằm ở đỉnh history trước destroy.
- **[VERIFY]** định nghĩa "spawn fail" trong SpawnComboByID hiện tại: fail toàn phần (0 item / parse fail) → rollback; fail lẻ tẻ (skip vài RowName, M11) → GIỮ kết quả + toast skip như cũ, KHÔNG rollback.

## TEST C9 (5 case)
1. Case A: spawn combo A → select cụm → replace bằng B → A biến, B đứng đúng Center cũ → Undo → A quay lại nguyên vẹn (group + SourceComboID).
2. Case B: replace bằng combo JSON hỏng → RestoreSnapshot tự chạy → A còn nguyên, không lỗ trống, toast hiện.
3. Không select gì (hoặc select đồ lẻ không SourceComboID) → toast "Chọn 1 cụm combo..." — không destroy gì.
4. Replace liên tiếp 2 lần nhanh → guard Cmb_bSpawnInFlight chặn lần 2.
5. Replace → Save EMS → Load → cụm mới + SourceComboID = NewComboID.

→ **Làm xong báo tao + 5 case + kết quả C9.0 K2 verify.**

---

# ═══════════════════════════════════════════════
# C6 — FAVORITE + RECENT COMBO (clone pattern Material)
# ═══════════════════════════════════════════════

**Nền có sẵn (C1 DONE):** `FavoriteComboIDs` + `RecentComboIDs` trong BP_UserPreferencesSave. Pattern mẫu: WBP_MaterialCard (Button_Favorite heart + UpdateFavTint + Toggle Favorite Material).

## C6.1 — Prefs API (BP_FurnitureUserPrefsManager) **[VERIFY: 4 hàm dưới đã có từ C1 chưa — có rồi thì skip]**
```
ToggleFavoriteCombo(ComboID)   — Contains? Remove : Add → SaveGame
IsFavoriteCombo(ComboID) → Bool — Pure
AddRecentCombo(ComboID)        — Remove nếu có → Insert(0) → nếu Length > 10 → Remove Index Last → SaveGame   ← cap 10, khớp cap Recent mesh [VERIFY số cap furniture, dùng CÙNG số]
GetRecentComboIDs / GetFavoriteComboIDs → Array<String>
```

## C6.2 — WBP_ComboCard: nút tim
### Q8 self-check
```
Q8: OnClicked handler đơn giản | IsValid InventoryRef (lazy-init sẵn có v1.1) | L2: merge | No latent | 6A: toggle = tự đảo ngược
```
- Designer: `BTN_FavoriteCombo` (heart, top-right 32×32 — copy layout WBP_MaterialCard).
- `UpdateFavTint`: `IsFavoriteCombo(ComboID)` → True: đỏ (1,0.3,0.3,1) / False: trắng mờ (1,1,1,0.3). Gọi ở OnListItemObjectSet + sau toggle.
- OnClicked ▶→ ToggleFavoriteCombo(ComboID) ▶→ UpdateFavTint.

## C6.3 — Recent hook
Trong listener `OnComboSpawned` của InputManager (đã có từ C2 — chỗ SelectActors + CaptureSnapshot), nối thêm:
```
▶→ PrefsManager.AddRecentCombo(SpawnedComboID)   ← [VERIFY] OnComboSpawned có mang ComboID không; không có → thêm param vào dispatcher (additive, caller cũ không vỡ vì chỉ 1 nơi broadcast)
```
> Replace (C9) đi qua SpawnComboByID → OnComboSpawned → Recent tự cập nhật, KHÔNG hook riêng.

## C6.4 — Tab Recent/Favorite mode Combo
`BTN_RecentCategory` / `BTN_FavoriteCategory` (đã có): thêm Branch `InventoryMode == Combo` đầu handler:
```
True  ▶→ GetRecentComboIDs (hoặc Favorite) ●→ IDs
       ▶→ Filter AllComboViews_Combo: giữ element có Array Contains(IDs, element.ComboID)
       ▶→ đổ CTV_ComboCard (Clear List Items + ForEach AddItem — pattern LoadComboLibrary)
       ▶→ Recent: giữ THỨ TỰ của IDs (loop IDs ngoài, tìm view khớp trong) — mới nhất đứng đầu
False ▶→ logic furniture/material cũ nguyên
```

## TEST C6 (6 case)
1. Tim 1 combo → đỏ → thoát PIE vào lại → vẫn đỏ (SaveGame bền).
2. Bỏ tim → trắng mờ, biến khỏi tab Favorite.
3. Spawn combo X rồi Y → tab Recent: Y đứng trước X.
4. Spawn 12 combo khác nhau → Recent giữ đúng cap (10), cũ nhất rớt.
5. Spawn combo → Recent COMBO có entry; Recent MESH không đổi (K3 canh).
6. Tab Recent/Favorite ở mode Furniture/Material → hành vi cũ nguyên (regression).

→ **Làm xong báo tao + 6 case.**

---

# ═══════════════════════════════════════════════
# C7 — WBP_ComboDetailPopup + INFO BUTTON
# ═══════════════════════════════════════════════

**Mục tiêu:** popup chi tiết combo: tên / số món / tags / mô tả / danh sách món (tên tiếng Việt) / thumbnail thật. Widget RIÊNG — KHÔNG tái dùng WBP_DetailPopup (field khác hoàn toàn).

## Q8 self-check (chung C7)
```
Q8: popup nhận data nhẹ qua InitComboPopup (R3) | IsValid trước DT lookup từng item | L2: nhánh thumbnail-fail merge về hiện icon 🧩 | No latent (LoadTexture2DFromFile sync C++ — file nhỏ, chấp nhận) | 6A: đóng popup = Remove; single instance qua CurrentPopup
```

## C7.1 — Layout WBP_ComboDetailPopup
```
Border (nền, ~360×460)
└─ VerticalBox
   ├─ IMG_Thumbnail (SizeBox 328×184)
   ├─ TXT_Name (to, đậm)
   ├─ HB_Meta: TXT_ItemCount ("×N món") | TXT_Category (Collapsed khi rỗng — chừa chỗ Phase B)
   ├─ TXT_Tags (1 dòng, join ", ")
   ├─ TXT_Description (Auto Wrap, max ~4 dòng)
   └─ ScrollBox → VB_ItemList (mỗi dòng 1 TextBlock: "• <VieName> ×<count>")
```

## C7.2 — InitComboPopup(ComboID : String)
```
▶→ UComboSerializer::LoadCombo(ComboID) ●→ ComboData, bOK    ← [VERIFY tên hàm load 1 combo trong ComboSerializer — C2 dùng F_LoadComboData phía BP]
▶→ Branch(bOK == False) → True: Remove from Parent → [end]
▶→ SetText Name/Description; TXT_ItemCount = "×" + Items.Length
▶→ Branch(Category == "") → True: Collapse TXT_Category / False: SetText + Visible
▶→ Tags: Join(Tags, ", ") → SetText (rỗng → Collapse)
▶→ Thumbnail: LoadTexture2DFromFile(CombosDir/ComboID.png) ●→ Tex, bLoaded
     Branch(bLoaded) True ▶→ Set Brush from Texture(IMG_Thumbnail, Tex)
                     False ▶→ giữ icon 🧩 mặc định (merge)
▶→ Gom item theo RowName (Map RowName→count) → ForEach:
     Get Data Table Row(DT_FurnitureCatalog, RowName) ●→ Row, bFound
     bFound ▶→ tạo TextBlock "• " + Row.VieName + " ×" + count → AddChild(VB_ItemList)
     !bFound ▶→ "• " + RowName + " (thiếu trong catalog)" → AddChild   ← không nuốt item lạ
```

## C7.3 — Entry: nút Info trên WBP_ComboCard
- Designer: `BTN_InfoCombo` (icon ℹ️, cạnh BTN_FavoriteCombo).
- Dispatcher hoặc gọi thẳng InventoryRef (card đã có InventoryRef v1.1) → Inventory event `OnComboCardInfoClicked(ComboID)`:
```
▶→ GET CurrentPopup → IsValid → Remove from Parent → SET CurrentPopup = None   ← pattern OnCardInfoClicked sẵn có
▶→ Create WBP_ComboDetailPopup → Add to Viewport → Set Position In Viewport(chuột + Y+10)
▶→ SET CurrentPopup = popup   ← [VERIFY] CurrentPopup kiểu gì — nếu strict WBP_DetailPopup → đổi kiểu chung UserWidget hoặc thêm var CurrentComboPopup riêng (hỏi cuhoang chọn, nghiêng var riêng cho surgical)
▶→ popup.InitComboPopup(ComboID)
```
- Đóng: click ra ngoài / mở popup khác → pattern popup furniture sẵn có.

## TEST C7 (5 case)
1. Info combo đủ metadata → popup đúng tên/×N/tags/mô tả/danh sách VieName.
2. Thumbnail thật hiện (sau P1); xóa file .png tay → icon 🧩, không crash.
3. Combo có item RowName không còn trong catalog → dòng "(thiếu trong catalog)".
4. Mở info card A rồi card B → popup A đóng, B hiện (không chồng).
5. Popup furniture cũ (Button_InforItem) vẫn chạy nguyên (regression).

→ **Làm xong báo tao + 5 case. Doc: WBP_ComboDetailPopup.md tạo mới.**

---

# ═══════════════════════════════════════════════
# C11 — EXPORT / IMPORT (K5 — cả 2 hướng graceful, nhúng thumbnail base64)
# ═══════════════════════════════════════════════

**Mục tiêu:** share combo KHÔNG cần server. Export = 1 file `.combojson` tự chứa (JSON combo + thumbnail base64). Import = validate → ComboID MỚI → vào thư viện.
**Luật kiến trúc (mục 6 Instructions):** gộp nhiều nguồn (JSON + PNG) = **1 hàm C++ mỗi chiều** trong ComboSerializer — BP không tự tổng hợp.

## C11.1 — C++ (2 hàm + helper)
### ExportCombo
```cpp
bool UComboSerializer::ExportCombo(const FString& ComboID, const FString& DestFilePath)
// 1. Load <ComboID>.json → FComboData (fail → false)
// 2. Đọc <ComboID>.png nếu có → FBase64::Encode → gắn field "thumbnailBase64" vào JSON object xuất
//    (field CHỈ tồn tại trong file export — FComboData KHÔNG thêm UPROPERTY này, tránh phình schema local)
// 3. SaveStringToFile(DestFilePath, ForceUTF8WithoutBOM)   ← M7: tiếng Việt
```
### ImportCombo
```cpp
bool UComboSerializer::ImportCombo(const FString& SrcFilePath, FString& OutNewComboID, FString& OutError)
// 1. LoadFileToString → parse JSON (fail → OutError="parse", false — M14 KHÔNG crash)
// 2. JsonObjectStringToUStruct → FComboData validate (fail → false)
// 3. SINH ComboID MỚI: "combo_" + FGuid::NewGuid() → ghi đè field (KHÔNG đè combo cũ; import 2 lần = 2 combo)
// 4. Tách "thumbnailBase64" nếu có → FBase64::Decode → ghi <NewComboID>.png
// 5. Ghi <NewComboID>.json vào CombosDir → OutNewComboID → true
```
### GetExportsDir (helper cho fallback)
```cpp
// <CombosDir>/../Exports  (cùng gốc với Combos) — MakeDirectory(true)
```
Compile plugin. Lỗi → dán nguyên error, không đoán quá 3 lần (M12).

## C11.2 — Export flow (BP)
Entry: context menu ComboCard thêm item "📤 Xuất file…" (Item3, pattern chuẩn) → `CB_ExportCombo`:
```
Q8: Custom Event | cache ComboID trước Hide | L2: 3 nhánh (dialog OK / dialog không có / export fail) đều ra toast | latent none | 6A: export không đổi state gì — an toàn
```
```
CB_ExportCombo:
  ▶→ cache ExportComboID → Hide menu → None
  // HƯỚNG 1: file-save dialog
  ▶→ [VERIFY] node dialog khả dụng runtime: thử C++ IDesktopPlatform::SaveFileDialog (module DesktopPlatform — hoạt động packaged Windows) HOẶC plugin sẵn có. Bọc thành hàm C++ OpenSaveFileDialog(DefaultName) → Path, bOK nếu dùng IDesktopPlatform.
  ▶→ Branch(bDialogAvailable AND bOK)
       True  ▶→ ExportCombo(ExportComboID, Path) → bExported
       False ▶→ // HƯỚNG 2: fallback tự động — KHÔNG hỏi user
              ▶→ DestPath = GetExportsDir() / (ComboName_sanitized + ".combojson")
              ▶→ ExportCombo(ExportComboID, DestPath) → bExported
  ▶→ Branch(bExported)
       True  ▶→ ShowToast("Đã xuất: " + path dùng thực tế)
       False ▶→ ShowToast("Xuất thất bại")
```
Ghi DEVIATIONS hướng nào thực sự chạy (quyết định K5).

## C11.3 — Import flow (BP)
Entry: nút `BTN_ImportCombo` cạnh khu tab Combo (hoặc đầu cột tree dưới nút "+" — cuhoang chọn vị trí, logic không đổi):
```
▶→ Open-file dialog (cùng cơ chế hướng 1; không có dialog → toast "Đặt file vào <ExportsDir> rồi bấm lại" + quét file mới nhất trong ExportsDir làm fallback)
▶→ ImportCombo(Path) ●→ NewComboID, Error, bOK
▶→ Branch(bOK)
     True  ▶→ Broadcast OnComboLibraryChanged   ← tab tự refresh (bind sẵn từ C4)
            ▶→ ShowToast("Đã nhập combo")
     False ▶→ ShowToast("File combo không hợp lệ")   ← M14, không crash
```

## TEST C11 (6 case)
1. Export combo A → file xuất hiện (dialog hoặc ExportsDir), mở bằng Notepad thấy thumbnailBase64.
2. Xóa A khỏi thư viện (xóa file tay) → import file export → A quay lại, ComboID MỚI, thumbnail .png tái tạo, card có ảnh.
3. Import CÙNG file 2 lần → 2 combo, ID khác nhau.
4. Import file rác (.txt đổi đuôi) → toast lỗi, không crash, thư viện không đổi.
5. Combo tên tiếng Việt có dấu → export/import tên không vỡ (M7).
6. Import combo chứa RowName không có trong catalog máy này → import OK; spawn → skip + toast (M11) — giới hạn "cùng asset pool" ghi vào doc.

→ **Làm xong báo tao + 6 case.**

---

# ═══════════════════════════════════════════════
# C10 — REGRESSION TỔNG SPRINT 5 (không code — chỉ test + chốt nợ verify)
# ═══════════════════════════════════════════════

Chạy TRỌN trong 1 phiên PIE liên tục (trừ bước reload/packaged). Ghi bảng PASS/FAIL từng dòng.

## Khối A — Chuỗi vòng đời combo (15 bước)
```
1  Chọn 6 món (có nested group 2 cấp) → Save combo "RegA" (dialog đủ tên/folder/tags)
2  Thumbnail .png sinh ra cạnh JSON (P1)
3  Spawn RegA ×2 → 2 cụm độc lập (move cụm 1, cụm 2 yên)
4  Recent COMBO có RegA; Recent MESH không đổi (K3)
5  Favorite RegA → reload → còn tim (C6)
6  Info popup đúng dữ liệu + thumbnail (C7)
7  Replace cụm 1 bằng combo khác → đúng vị trí (C9 A)
8  Replace bằng file JSON cố tình sửa hỏng → auto-rollback + toast (C9 B)
9  Undo xuyên chuỗi (replace → spawn → save-select) từng nấc đúng; folder ops KHÔNG bị undo (UX8)
10 Save scene EMS → Load → cụm + group + SourceComboID nguyên (K2/M13)
11 Export RegA → import lại → ID mới + thumbnail (C11)
12 Nested cap: dựng group 3 cấp → save/spawn → nguyên vẹn; KHÔNG hỗ trợ >3 (K4 — thử 4 cấp: kỳ vọng chặn hoặc flatten, ghi hành vi thực tế vào doc)
13 Toast xuất hiện đúng mọi điểm lỗi ở trên, không còn Print user-facing (K1)
14 Folder REG 12 bước của C5 plan v3 chạy lại NGUYÊN (không hồi quy folder)
15 stat rhi đầu vs cuối phiên → VRAM chênh ghi số vào DEVIATIONS; chênh bất thường (>500MB) → soi R4
```

## Khối B — Chốt nợ verify treo từ Sprint 5
| Nợ | Cách chốt | Kết quả ghi vào |
|---|---|---|
| T6 pivot có thừa không | Test move/rotate group sau save/load KHÔNG có pivot → nếu đủ → lên kế hoạch gỡ (task riêng, KHÔNG gỡ trong C10) | DEVIATIONS + Session_State |
| Copy/paste cụm mất group | Xác nhận còn (known) → giữ backlog v1.1 | Open_Bugs (known limitation) |
| Scene save group persistence | Trùng bước 10 khối A | — |

## Khối C — Docs đóng Sprint 5
Session_State + PROGRESS (Sprint 5 DONE, đếm task cuối) · DEVIATIONS (VRAM số + K4 hành vi + K5 hướng export) · bump mọi widget/BP doc đã đổi · Open_Bugs dọn (K3 resolved, thêm known limitations).

→ **PASS hết khối A + chốt khối B + xong khối C = Sprint 5 CHÍNH THỨC DONE. Báo tao bảng tổng.**

---

# ═══════════════════════════════════════════════
# GATE 1.5 — PACKAGED SMOKE (+ QUYẾT P4)
# ═══════════════════════════════════════════════

**Mục tiêu:** lần đầu chạy tool NGOÀI editor — bắt mìn deploy sớm trước khi Sprint 7 chồng thêm. Không thêm feature nào ở gate này.

## G1.5.1 — Quyết + áp P4 (LÀM TRƯỚC khi package)
0. **[VERIFY A3]** đọc `GetCombosDir()` hiện tại trong ComboSerializer.cpp. Đã LOCALAPPDATA → skip sang G1.5.2.
1. Dán thay:
```cpp
FString UComboSerializer::GetCombosDir()
{
    // P4 (23/06): combo phải sống qua update app — ProjectSaved bị xóa khi rebuild packaged
    FString Base = FPlatformMisc::GetEnvironmentVariable(TEXT("LOCALAPPDATA"));
    if (Base.IsEmpty()) { Base = FPaths::ProjectSavedDir(); }   // fallback — báo cuhoang nếu rơi vào đây
    FString Dir = Base / TEXT("InteriorFOFFTool") / TEXT("Combos");
    IFileManager::Get().MakeDirectory(*Dir, true);
    return Dir;
}
```
`#include "HAL/PlatformMisc.h"` nếu thiếu. Exports dir (C11) tự theo vì tính từ CombosDir.
2. **Migrate tay 1 lần:** copy toàn bộ `<Project>/Saved/Combos/*` (json + png + Folders.json) → `%LOCALAPPDATA%\InteriorFOFFTool\Combos\`.
3. Test trong editor: tab Combo hiện đủ combo cũ + folder cũ + thumbnail (đường mới đọc đúng).

## G1.5.2 — Chuẩn bị build
- `bDebugMode = False` mọi manager (Print gate tắt — KHÔNG xóa node).
- **[VERIFY]** plugin Streamline/NVIDIA trong build config — mìn GPU crash: nếu có mặt → loại khỏi packaged build lần này (bật lại sau nếu vô can).
- Package **Development** (giữ log) — Shipping để Gate 2.

## G1.5.3 — Smoke checklist (chạy trên bản packaged)
```
1  App mở được, level load, không crash 5 phút đầu
2  Spawn/move/rotate/scale furniture + Undo/Redo
3  Save scene EMS → thoát app → mở lại → Load → nguyên vẹn
4  Selection/highlight: Custom Depth Stencil hoạt động (255/254) — packaged hay rụng post-process
5  UniqueID/GetDisplayName: spawn → save → load → identity đúng (MÌN #1 — sai → chuyển ActorGUID, task riêng)
6  Combo: save mới → file vào %LOCALAPPDATA% ✓ → spawn ✓ → replace ✓ → export/import ✓
7  Folders.json + Favorite/Recent (SaveGame) sống qua tắt/mở app
8  Thumbnail capture chạy trong packaged (SceneCapture2D + PNG write — hay khác editor)
9  F8 không bị bind gì (mìn #4); mọi phím tắt tool chạy
10 Log: không Error/Warning lạ lặp; VRAM ổn định sau 10 phút thao tác
```
Mỗi dòng FAIL → ghi Open_Bugs với repro; KHÔNG fix tại chỗ trừ chặn-smoke (3-strike rule vẫn áp).

→ **PASS ≥ 9/10 (dòng fail có ticket) = Gate 1.5 DONE → mở Sprint 7 Material v1.2. Báo tao bảng 10 dòng.**

---

## DOC UPDATES XUYÊN SUỐT (version + ngày giờ phút mỗi lần)
- Sau MỖI gate: Session_State + PROGRESS + doc widget/BP liên quan (đã ghi cuối từng gate).
- Doc mới: `WBP_Toast.md`, `WBP_ComboDetailPopup.md`, cập nhật `ComboSerializer` reference (ExportCombo/ImportCombo/GetExportsDir/GetCombosDir-P4).
- File 09 nodes chờ xác nhận khi gặp: `Set Timer by Event` + `Clear and Invalidate Timer by Handle`, `Set Brush from Texture`, `Join String Array`, node dialog file (C11 [VERIFY]).
- Plan này → Archive khi Gate 1.5 DONE.

## RỦI RO MANG SANG TỪ SỔ M (tra khi gặp)
M2 double-fire (guard Cmb_bSpawnInFlight — C9) · M5/M6 thumbnail fail (icon 🧩) · M7 UTF8 (C11) · M11 thiếu mesh (skip+toast) · M13 SourceComboID (C9.0/C10) · M14 import rác (validate + ID mới) · M12 kẹt C++ (gom hỏi Opus 1 lần).
