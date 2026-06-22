# Session State
**Nguồn:** `import_raw/Session_State_15jun2026.md` (bản mới nhất — 15/06/2026 20:30 ICT)
> Session_State.md (12/06/2026) là bản cũ hơn — đã merged vào đây.
**Phiên bản:** 22/06/2026 — Sprint 5 T1+T2+T3+C1+C0+C2 DONE | C3 pending | Lighting_Mnger UE5.5.4

---

## TRẠNG THÁI HIỆN TẠI

**Sprint D — HOÀN THÀNH ✅ (17/06/2026) + TreeNode/Chip Highlight ✅ (18/06/2026)**
**Sprint 5 — Combo Mesh 🔄 IN PROGRESS (21/06/2026)**

### Sprint 5 — Combo Library (21/06/2026 EOD)

| Task | Nội dung | Status |
|---|---|---|
| T1 | C++ structs FComboData/FComboGroupData/FComboItemData + ComboSerializer — schema v1, round-trip JSON PASS | ✅ DONE |
| T2 | BP_ComboManager tách riêng, SaveComboFromSelection, CB_SaveCombo context menu | ✅ DONE |
| T3 | BP_ComboItemView, LoadComboLibrary, bind OnComboLibraryChanged | ✅ DONE |
| C1 | FComboData.FolderPath (C++), FindMaterialRowNameByPath (C++), S_GroupData.SourceComboID (BP), FavoriteComboIDs/RecentComboIDs (UserPrefs) | ✅ DONE |
| C0 | SaveComboFromSelection nested — LCA (CalculateLCAList_Combo + GetGroupsInHierarchy) + MaterialOverrides → RowName | ✅ DONE (22/06) — 3 case A/B/C PASS + RowName fallback (đồ cũ parse MeshPath) |
| C2 | SpawnComboByID — Guard, F_LoadComboData, F_BuildTokenGUIDMap, F_RegisterComboGroups, F_ApplyMaterialOverrides, 4 sub-steps | ✅ DONE (22/06) — 7/7 PASS |

**C0:** 3 case A/B/C PASS (22/06). RowName fallback (đồ cũ parse MeshPath) xác nhận OK.
**C2:** 7/7 PASS (22/06). Group nesting: Case A (no groups→wrapper) / Case B (has groups→no wrapper, root nhận SourceComboID).
**Pending T2:** WBP_SaveComboDialog (dialog nhập tên) — dời sau T5, không chặn spawn
**Ghi chú kiến trúc:** BP_ComboManager đã spawn trong Level BP; InputManager guard (≥2 đồ, tính Center) → gọi ComboManager qua param (SelectedActors, Center, ComboName, Description)

---

### Sprint 4 Bug Fix (F1–F4 + A12) — ĐẦY ĐỦ PASS

| Fix | Nội dung | Status |
|---|---|---|
| F1 | Info bar hiển thị đúng unit name (GetSelectionUnitLabel) | ✅ PASS |
| F2 | Group name counter monotonic (GroupNameCounter → BP_GroupsContainer) | ✅ PASS |
| F3 | CreateGroup bottom-up nesting (ComputeSelectionUnits + rewrite) | ✅ PASS |
| F4 | Spawn auto-join edit scope (SpawnFurnitureCopy + DragOverlay On Drop) | ✅ PASS |
| A12 | Edit mode bar ẩn sau Undo (EditModeStack vào snapshot V=4) | ✅ PASS |

**Full test suite (30+ cases + Regression S1-S3) — ALL PASS ✅**

### Bugs đã giải quyết trong session này
- B3 (gizmo ẩn sau undo trong edit mode): xác nhận **pre-existing**, không phải regression Sprint 4. Ghi nhận known issue.
- A12 root cause: EditModeStack là runtime state, không nằm trong snapshot → undo không khôi phục edit state → fix bằng cách đưa EditModeStack vào S_SceneSnapshot (Version=4).

---

## BUG CÒN MỞ

| # | Bug | Ưu tiên | Xử lý |
|---|---|---|---|
| B1 | ✅ FIXED (16/06) — bIsRestoring guard + spawn merge | — | Đã đóng Gate 1, xem BP_UndoManager.md v1.9-1.10 |
| B-gizmo | Gizmo ẩn sau undo trong edit mode (pre-existing) | 🟢 Thấp | Known issue, chưa có timeline |
| B-folder | ✅ FIXED (17/06, D.T6) — Replace folder sai khi group nhiều mesh | — | OnMeshSelected RowName→DT, fallback DAPath save cũ |
| B-stale-popup | ✅ FIXED (17/06, D.T6) — Popup hiển thị đồ cũ | — | UpdateDetailPopup bound OnSelectionChanged |
| Bug-Pagination | ✅ FIXED (17/06, D.T9) — Furniture pagination dừng sớm 1 trang | — | Int to Float trước Ceil ở Next-page check |
| Bug-Maximize | ✅ FIXED (17/06, D.T9) — BTN_Maximize không nhảy về góc trên-trái | — | Set Position thêm vào Slot VerticalBox_0 |
| Fix-5.2-async | ✅ FIXED (19/06) — aliasing shared latent khi spawn nhiều actor dồn | — | LoadMeshAsync/LoadMaterialsAsync đặt trong BP_FurnitureActor thay InputManager; NewActorCopy → local var |

---

## ĐÃ HOÀN THÀNH

- Change Material v1.1 (20/05/2026)
- UX Phase 2.1: Gizmo, Nudge, Copy/Paste, Recent/Favorite
- Resize Window 8 hướng
- Sprint 1 — Multi-select (15/15) ✅
- Sprint 2 — Box+Context Menu (9/9) ✅
- Sprint 3 — Group cơ bản (12/12 + 10 bug fix) ✅
- Sprint 4 — Edit Mode + Nested Group (T1-T8 + 2 bug fix) ✅
- **Sprint 4 Bug Fix Session (F1-F4 + A12, 15/06/2026) ✅**
- **Gate 1 (G1.1-G1.3, 16/06/2026) ✅**
- **Sprint D — Data Layer v2 (D.T1-D.T9, 17/06/2026) ✅**
- **TreeNode/Chip active-folder highlight (18/06/2026, tính năng bổ sung) ✅**
- **Sprint 5 T1+T2+T3+C1 (21/06/2026) ✅** — ComboTypes C++, ComboSerializer, BP_ComboItemView, LoadComboLibrary, FolderPath, FindMaterialRowNameByPath, SourceComboID, Favorite/RecentComboIDs

### VRAM Fixes (19/06/2026)
- Giai đoạn 1: Xác nhận card là RTX 3060 8GB (không phải 12GB). Budget UE = 7.26GB. Workaround: dùng Standalone Game (Alt+P) thay PIE cho session dài — mỗi lần tắt OS reclaim VRAM sạch 100%. Peak VRAM lúc chạy = 7.2/8.0GB, không cộng dồn qua nhiều lần launch. ✅ PASS
- Fix 5.3: Material dedup trong ApplyMaterial (WBP_FurnitureInventory). Branch Is Valid Index + Equal String trước khi gọi LoadAndApplyMaterial — nếu material đã áp đúng slot thì bỏ qua, không fire Async Load lại. ✅ PASS
- Việc 1: Add Recent Mesh trong SpawnFurnitureCopy đổi nguồn parse từ DAPath (rỗng với đồ Sprint D) sang MeshPath — parse theo '/' lấy phần cuối, tách '.' lấy index 0 = RowName. ✅ PASS
- Fix 5.2: Async Load mesh + material trong SpawnFurnitureCopy. Chuyển từ Load Asset Blocking sang Custom Event LoadMeshAsync + LoadMaterialsAsync đặt TRONG BP_FurnitureActor (không phải InputManager). Mỗi actor tự load asset của chính nó — tránh aliasing shared class var/latent context khi nhiều actor spawn dồn. NewActorCopy đổi từ class var → local var trong SpawnFurnitureCopy. ✅ PASS

---

## KIẾN TRÚC HIỆN TẠI

**BP_FurnitureInputManager v2.1** — SpawnFurnitureCopy async load (LoadMeshAsync/LoadMaterialsAsync); NewActorCopy local var; Add Recent Mesh parse MeshPath
**BP_UndoManager v1.10** — bIsRestoring guard + SpawnFurnitureCopy merge
**BP_FurnitureActor v1.2** — RowName : Name (SaveGame), GroupID confirmed SaveGame
**WBP_DetailPopup v1.2** — InitPopup(RowName), RowData : S_FurnitureData
**WBP_MeshControls v1.7** — BTN_Info RowName, UpdateDetailPopup bound OnSelectionChanged
**WBP_FurnitureCard v1.0** — TẠO MỚI, CardRowName, BP_FurnitureItemView, DT lookup
**WBP_DragOverlay_FurnitureCard v1.6** — PendingRowName, F_ExecuteReplace RowData
**WBP_FurnitureInventory v2.5** — OnCardInfoClicked(RowName), OnMeshSelected RowName branch
**FilterByCategory_Logic v1.3** — Recent/Favorite DT direct (bỏ inner loop AllFurnitureItems)
**FilterBySearch_Logic v1.3** — FilterFurnitureRows + AllFilteredFurnitureRows → DisplayPage
**WBP_FurnitureInventory v2.6** — IsPathActive (Pure) + UpdateFolderHighlights + Fix Bug-Pagination
**WBP_TreeNode v1.1** — RefreshDisplay + bIsActive param → SetBackgroundColor
**WBP_ChipTag v1.1** — SetHighlight(bIsActive) custom event → SetBackgroundColor
**WBP_ResizeWindow v1.1** — Fix Bug-Maximize: Set Position thêm vào Slot VerticalBox_0
**BP_ComboManager v1.3** — SaveComboFromSelection (LCA path) + SpawnComboByID; spawn trong Level BP; nhận data qua param từ InputManager. Functions: GetPathToRoot_Combo, FindLCA_TwoGroups_Combo, CalculateLCAList_Combo, F_LoadComboData, F_BuildTokenGUIDMap, F_RegisterComboGroups, F_ApplyMaterialOverrides. [C0 ✅ DONE + C2 ✅ DONE (22/06)]
**BP_ComboItemView v1.0** — TẠO MỚI, hiển thị combo card trong library
**S_GroupData** — ✅ field `SourceComboID : String` (default "") đã thêm (C1 DONE). Group cha cụm combo = ComboID gốc; group user tạo tay = "". Đã add vào snapshot capture/restore.
**C++ FurnitureToolkit** — FComboData.FolderPath (field mới), FindMaterialRowNameByPath (function mới). Compile xanh. Full rebuild (Binaries/Intermediate xóa + rebuild) ✅

**Snapshot version history:**
- V1: single select (legacy)
- V2: multi-select (Sprint 1)
- V3: Groups (Sprint 3)
- V4: Groups + EditModeStackSnapshot (Sprint 4 Bug Fix, 15/06/2026)

---

## TIẾP THEO

**ĐẦU SESSION MỚI — Ưu tiên:**
1. **C3 WBP_SaveComboDialog** — dialog nhập tên/folder/tags, dời từ T2.

**Roadmap v3.2:**
```
Gate 1 (fix B1 bIsRestoring + hợp nhất spawn)   ✅ DONE (16/06)
Sprint D (D.T1-D.T9, Furniture Data Layer v2)    ✅ DONE (17/06)
TreeNode/Chip active-folder highlight            ✅ DONE (18/06, bổ sung)
Sprint 5 — COMBO LIBRARY ĐẦY ĐỦ 🔄 IN PROGRESS (21/06, v2.0)
  ⚠️ Scope mở rộng 21/06 thành Combo Library đầy đủ. Deadline 25/06 sẽ trượt — báo cuhoang re-plan.
  ✅ T1 — C++ ComboTypes + ComboSerializer (schema v1, round-trip PASS)
  ✅ T2 core — SaveComboFromSelection + CB_SaveCombo (hệ thống cơ bản)
  ✅ C0 — DONE (22/06) — 3 case A/B/C PASS + RowName fallback (đồ cũ parse MeshPath)
  ✅ C1 — FolderPath C++, FindMaterialRowNameByPath C++, SourceComboID BP, FavoriteComboIDs/RecentComboIDs (UserPrefs)
  ✅ C2 — SpawnComboByID DONE (22/06) — 7/7 PASS, group nesting Case A/B fix
  ⏳ C3 — WBP_SaveComboDialog (tên, folder, tags, mô tả)
  ⏳ C4 — WBP_ComboCard (thumbnail, badge số món, Info/Delete/Spawn)
  ⏳ C5 — Folder tree tab 🧩 Combo trong inventory
  ⏳ C6 — Favorite + Recent combo
  ⏳ C7 — WBP_ComboDetailPopup
  ⏳ C8 — Drag-drop combo (ghost 1 đại diện, spawn tại cursor)
  ⏳ C9 — Replace combo cả cụm (leo SourceComboID → destroy + respawn)
  ⏳ C10 — Regression + Docs
→ Sprint 7 Material v1.2
→ Sprint 6 Polish
→ Gate 2 (first packaged build)
```

---

## NGUYÊN TẮC ĐỌC DOC ĐẦU SESSION

1. Đọc `01_Session_State.md` TRƯỚC
2. Gate 1 → đọc `02_Current_Sprint.md` + `Rules/AI_Implementation_Rules.md`
3. Sprint D → đọc `02_Current_Sprint.md` phần Sprint D
4. Flow chi tiết → `Blueprints/BP_FurnitureInputManager.md` v2.1 + `Blueprints/BP_UndoManager.md` v1.10
5. Flow Sprint 1-3 → `Blueprints/Blueprint_Logic_NodeFlow.md`

---

## Lịch sử cập nhật

| Ngày | Nội dung |
|------|----------|
| 21/06/2026 | Sprint 5 T1+T2 DONE (sáng). |
| 21/06/2026 EOD | Sprint 5 T3+C1 DONE. C0 impl xong chưa test (LCA nested + MaterialOverrides). BP_ComboManager → v1.1 (GetPathToRoot_Combo, FindLCA_TwoGroups_Combo, CalculateLCAList_Combo, LeafGroupIDs/LCARoots/MaterialOverrides_SaveCombo). C++ FurnitureToolkit: FComboData.FolderPath + FindMaterialRowNameByPath. Full rebuild xanh. TIẾP THEO: test C0 (3 case) → C2 SpawnComboByID. |
| 22/06/2026 | C0 DONE — 3 case A/B/C PASS. RowName fallback (đồ cũ parse MeshPath) xác nhận OK. BP_ComboManager → v1.2 (thêm ItemRowName_SaveCombo). TIẾP THEO: C2 SpawnComboByID. |
| 22/06/2026 | C2 SpawnComboByID DONE — 7/7 PASS. BP_ComboManager → v1.3 (5 class var mới, 4 functions: F_LoadComboData/F_BuildTokenGUIDMap/F_RegisterComboGroups/F_ApplyMaterialOverrides, Custom Event SpawnComboByID 4 sub-steps). Group nesting fix: Case A (no groups→wrapper) / Case B (has groups→no wrapper). TIẾP THEO: C3 WBP_SaveComboDialog. |
