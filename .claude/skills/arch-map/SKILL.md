---
name: arch-map
description: Verify and maintain the UE5 Interior Tool architecture map from canonical documentation and K2/live Blueprint evidence. Use for C4 L3/L4 mapping, Blueprint relationships, communication flows, K2 relationship verification, and Architecture_Map updates.
disable-model-invocation: true
---

# arch-map — procedure cập nhật Architecture Map

Máy thực thi quy trình kiến trúc. KHÔNG chứa kiến thức project. Sự thật implementation ở canonical docs; luật ở CLAUDE.md; cú pháp Mermaid ở skill `mermaid`; render ở MCP `claude-mermaid`.

Chạy khi cuhoang gõ `/arch-map` + cung cấp Blueprint/K2 export cần verify.

---

## 1. Scope

**Chịu trách nhiệm:** C4 L3 component map · C4/impl L4 Blueprint map · inheritance · ownership/management · dependency · communication flow · Index Map · K2 evidence verification · Mermaid architecture source · render/validation của architecture diagram.

**KHÔNG:** coding standards · distribution workflow · changelog policy · performance rules · documentation policy · dạy cú pháp Mermaid tổng quát. → thuộc CLAUDE.md / canonical docs / skill `mermaid`.

---

## 2. Procedure

### A. Xác định working set TRƯỚC — không scan toàn repo

Với K2 của `BP_A -> BP_B`, chỉ đọc:
- CLAUDE.md
- source-of-truth file hiện tại (Session_State / tương đương)
- `Architecture_Map.md` hiện tại
- canonical doc của BP_A
- canonical doc của BP_B
- K2 export vừa được cung cấp
- file khác **chỉ khi** dependency thật dẫn tới nó

Mở rộng working set chỉ khi evidence dẫn tới component thứ ba. Xem §7.

### B. 4 loại relationship — không trộn thành 1 mũi tên

1. **INHERITANCE** — Parent Class → Child Blueprint
2. **OWNERSHIP / MANAGEMENT** — component sở hữu/quản lý lifecycle/reference của component khác
3. **DEPENDENCY** — A cần biết/reference B, chưa nhất thiết gọi trực tiếp
4. **COMMUNICATION** — A thực sự gọi Event/Function/Interface/Dispatcher sang B

### C. Evidence hierarchy

```
LIVE/K2 evidence  >  canonical as-built docs  >  verified implementation report  >  plan/design docs
```

- Plan KHÔNG được biến thành current implementation.
- Source mâu thuẫn → KHÔNG tự hòa giải bằng suy đoán. Ghi conflict. Giữ relationship unverified tới khi có evidence mạnh hơn.

### D. Evidence state

| State | Nghĩa |
|---|---|
| `VERIFIED` | đủ bằng chứng live/K2 chứng minh relationship thực tế |
| `DOCUMENTED` | canonical doc nói có, chưa live/K2 verify |
| `UNKNOWN` | chưa đủ bằng chứng |

KHÔNG đổi `UNKNOWN`/`DOCUMENTED` → `VERIFIED` chỉ vì relationship "có vẻ hợp lý".

---

## 3. K2 verification loop

Khi cuhoang paste K2 export:

1. Parse node names
2. Parse Event / Function / Variable / Interface
3. Theo `LinkedTo` reconstruct exec/data path
4. Xác định Blueprint nguồn
5. Xác định Blueprint đích
6. Xác định function/event thật sự được gọi
7. Phân loại relationship (§2B)
8. Ghi evidence (state §2D + label)
9. Update `Architecture_Map.md`
10. Update Index Map nếu cần
11. Render bằng `mermaid_preview` (§5)
12. Render fail → sửa Mermaid → preview lại
13. Chỉ báo DONE khi render PASS

Communication Flow ưu tiên format:
```
[Blueprint A] -> gọi [Event/Function X] -> tác động [Blueprint B]
```

K2 không đủ chứng minh B → **đừng đoán**. Nói chính xác cần export node/function/event nào tiếp theo.

---

## 4. Diagram contract

Quy ước node type · evidence state · line style · evidence label · source traceability:
→ đọc `references/diagram-contract.md` (đọc mỗi lần chạm phần Mermaid).

---

## 5. Mermaid strategy

Không duplicate skill `mermaid`. Cần cú pháp → dùng skill đó.

| Concern | Diagram type |
|---|---|
| System/component overview | `flowchart` + `subgraph` |
| Blueprint inheritance | `classDiagram` khi phù hợp |
| Runtime communication | `sequenceDiagram` |
| Folder/source hierarchy | `flowchart` hoặc `mindmap` |

Không ép toàn project vào 1 diagram. Một diagram quá lớn → tách nhiều diagram nhỏ theo concern trong `Architecture_Map.md`.

---

## 6. MCP verification

Dùng MCP `claude-mermaid` đã cài:

```
generate Mermaid → mermaid_preview → inspect render
  → syntax/layout fail → sửa → preview lại
  → PASS → mermaid_save chỉ khi cần artifact SVG/PNG/PDF
```

Mermaid source KHÔNG hợp lệ chỉ vì code block trông đúng. Phải render PASS.

---

## 7. Context budget

**DO NOT read the entire docs repository on every invocation.**

Progressive working set = `Architecture_Map` + source-of-truth + component A + component B + K2 evidence + dependency docs thật cần. Mở rộng chỉ khi evidence dẫn tới component thứ ba.

---

## 8. Definition of Done

Một relationship xong khi:

- [ ] relationship type xác định
- [ ] source component xác định
- [ ] target component xác định
- [ ] Event/Function/Variable quan trọng ghi lại (nếu có)
- [ ] evidence level ghi lại
- [ ] source file traceability có
- [ ] Mermaid source updated
- [ ] Index Map updated (nếu cần)
- [ ] `mermaid_preview` render PASS

Thiếu evidence → status `UNKNOWN`/`DOCUMENTED`, KHÔNG fake `VERIFIED`.
