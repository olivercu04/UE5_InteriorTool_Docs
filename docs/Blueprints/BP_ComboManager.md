# BP_ComboManager — Blueprint Logic
**Version:** 1.0 | **Ngày:** 21/06/2026 | **Actor class, không Tick**

## Vai trò
Xử lý toàn bộ combo logic (save, spawn, replace). Nhận data qua PARAM, KHÔNG hard ref BP_FurnitureInputManager (R2). Được spawn trong Level BP sau UserPrefsManager.

## Event Dispatchers
- `OnComboLibraryChanged` — broadcast sau khi lưu/xóa combo → WBP_FurnitureInventory lắng nghe → LoadComboLibrary

## Class Variables
| Tên | Kiểu | Vai trò |
|-----|------|---------|
| SaveCombo_GroupIDs | Array String | Leaf GroupIDs từ SelectedActors (Bước 3) |
| SaveCombo_ComboGroups | Array S_GroupData | Groups đầy đủ sau LCA (Bước 3 mới) |
| SaveCombo_TokenMap | Map String→String | GroupID → token (Bước 4) |
| SaveCombo_TempParentToken | String | Buffer parentToken cho từng group |
| SaveCombo_TempGroupToken | String | Buffer groupToken cho từng actor |
| SaveCombo_OutputGroups | Array FComboGroupData | Groups output cho JSON |
| SaveCombo_OutputItems | Array FComboItemData | Items output cho JSON |
| SaveCombo_ComboID | String | ComboID hiện tại đang save |
| LeafGroupIDs_SaveCombo | Array String | Input cho CalculateLCAList_Combo (C0) |
| LCARoots_SaveCombo | Array String | Output LCA roots (C0) |
| MaterialOverrides_SaveCombo | Array String | Buffer RowName per actor (C0) |

## Functions (có local variable)
### GetPathToRoot_Combo(InGroupID → Path: Array String)
Leo từ InGroupID lên root qua ForLoop 0..9, gọi FindGroupData trên InputManager. Collect từng GroupID vào Path. Return khi ParentGroupID=="" hoặc bFound=False hoặc loop hết.

### FindLCA_TwoGroups_Combo(GroupID_A, GroupID_B → LCA: String)
PathA = GetPathToRoot(A). Walk up từ B: nếu Contains(PathA, CurrentB) → return CurrentB. Nếu không tìm được → return "".

### CalculateLCAList_Combo(LeafIDs → Result: Array String)
Guard Length==0 → return []. SET CurrentLCA = LeafIDs[0]. ForEach từ index 1: FindLCA_TwoGroups(CurrentLCA, leaf) → nếu "" (khác cây) ADD CurrentLCA + SET CurrentLCA=leaf; nếu != "" SET CurrentLCA=lca. Completed: ADD CurrentLCA cuối → return Result.

## Custom Events
### SaveComboFromSelection(SelectedActors, Center, ComboName, Description)
**Bước 1:** Guard Length < 2 → dead-end  
**Bước 3:** CLEAR LeafGroupIDs → ForEach SelectedActors → unique GroupID != "" → ADD  
**Bước 3b (C0-LCA):** CLEAR SaveCombo_ComboGroups → CalculateLCAList → ForEach LCARoots → GetGroupsInHierarchy → ADD (unique)  
**Bước 4:** CLEAR TokenMap → ForEach ComboGroups → token = "g"+index → ADD map  
**Bước 5a:** SET SaveCombo_ComboID = "combo_"+NewGuid  
**Bước 5b:** CLEAR OutputGroups/Items  
**Bước 5c:** ForEach ComboGroups → resolve ParentToken (via TokenMap, branch "")→ Make FComboGroupData → ADD OutputGroups  
**Bước 5d:** ForEach SelectedActors → Cast → CLEAR MaterialOverrides_SaveCombo → ForEach MaterialPaths → FindMaterialRowNameByPath → ADD; Branch GroupToken → Make FComboItemData → ADD OutputItems  
**Bước 5e:** Make FComboData (tất cả fields + Items + Groups)  
**Bước 6:** GetCombosDir → MakeDirectory → ComboToJson → SaveStringToFile  
**Bước 7:** (thumbnail — pending C3)  
**Bước 8:** Broadcast OnComboLibraryChanged  

## Lịch sử cập nhật
| Ngày | Version | Nội dung |
|------|---------|----------|
| 21/06/2026 | 1.0 | Tạo mới — T2 core + C0 LCA fix + C1 material RowName |
