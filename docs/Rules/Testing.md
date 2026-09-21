# Rules — Testing (Automated)

**Phiên bản:** 1.0 | **Tạo:** 21/09/2026 (T0 PASS) | **Nguồn thiết kế:** `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md` §6

> File này chỉ được tạo SAU KHI T0 (Automation Harness Gate) PASS — đúng luật đã ghi trong task
> card (§8.8). Từ đây, mọi test C++ mới trong dự án tuân theo file này thay vì lặp lại lý luận
> từ đầu.

---

## 1. Ba tầng verification — cố ý rất nhỏ

```
                 MANUAL                    visual · UX feel · Shipping smoke
                    ▲
              FUNCTIONAL TEST              World + Actor + BP integration
                    ▲
           C++ AUTOMATION SPEC             domain / core — KHÔNG cần World
```

| Tầng | Dùng cho | Chạy ở |
|---|---|---|
| **Automation Spec** | ID lifecycle · history cursor · branch-after-undo · transaction state machine · command Before/After · snapshot entry semantics · ChangeSet contents · Resolver rules — bất cứ logic thuần nào không cần World | Editor, **không cần PIE** |
| **Functional Test** | seam mà Spec không chứng minh được: actor lifecycle thật, spawn/destroy/restore end-to-end | **cần PIE** |
| **Manual** | highlight có đúng không · panel có nhảy không · drag có cảm giác đúng không · bản Shipping | mắt |

## 2. ⚠️ LUẬT NGÂN SÁCH PIE — ràng buộc môi trường, KHÔNG phải sở thích

Máy cuhoang có workaround đang hiệu lực (`ways-of-working.md` §GPU): **GPU crash Streamline →
dùng Standalone Game thay PIE cho session dài, restart editor mỗi 2–3 PIE.**

Automation Spec chạy trong editor, **không tốn PIE**. Functional Test **tốn 1 PIE mỗi lần chạy**.

```
LUẬT:  ① Cái gì Spec test được thì KHÔNG được đẩy xuống Functional Test.
       ② Toàn bộ Functional Test nằm trong MỘT map duy nhất:
             L_Test_UndoArchitecture
          Chạy một lượt, không rải nhiều map.
```

Vi phạm luật này biến suite regression thành một buổi restart editor liên tục.

## 3. Protocol 5 bước cho MỌI test mới

```
1. CONTRACT           viết behavior bằng câu tiếng người + gán mã UNDO-* (hoặc mã hệ tương ứng)
2. RED                test FAIL vì behavior chưa tồn tại (hoặc bug cũ còn đó)
3. GREEN              implement tối thiểu → test PASS
4. NEGATIVE CONTROL   cố ý phá ĐÚNG behavior test bảo vệ → test phải ĐỎ vì ĐÚNG assertion
5. RESTORE            khôi phục implementation → test XANH lại
```

> **Test nào chưa từng ĐỎ thì chưa được tính là test.**

Với bug có sẵn, thứ tự đẹp nhất: bug xuất hiện → viết regression test → RED trên code hiện tại →
fix → GREEN. Mạnh hơn viết fix rồi mới viết test.

## 4. Bốn kỷ luật — vì chủ dự án không tự đọc code test

| | Kỷ luật |
|---|---|
| **A** | Mỗi invariant có mã (`UNDO-*` hoặc hệ mã phù hợp domain), và mã đó xuất hiện trong tên test: `It "[UNDO-ID-02] giữ nguyên ID qua snapshot restore"` |
| **B** | Test **observable behavior**, không test implementation |
| **C** | Test chứng minh cả **"đổi đúng"** lẫn **"không phá thứ khác"** |
| **D** | Test **độc lập**: không giả định thứ tự chạy, dọn state sau mỗi test |

## 5. Ba thứ kiểm nhau — test KHÔNG thay documentation

```
Docs   =  Intent            ← vì sao muốn thế này
Tests  =  Executable Contract
Code   =  Implementation
```

Test vẫn drift được: nếu code và test cùng hiểu sai một yêu cầu thì cả hai cùng xanh. Doc kiến
trúc là cái neo thứ ba.

## 6. Release gate (dùng từ Gate 2)

```
CORE      Automation Spec                    →  PASS
RUNTIME   Functional Test / cooked Dev       →  PASS
RELEASE   Shipping smoke test                →  PASS       ← KHÔNG bỏ
```

Dự án này đã có tiền sử `"works PIE" ≠ "works packaged Shipping"`. **Automation xanh trong
editor không phải bằng chứng cho Shipping.**

---

## 7. Đường bấm thật — UE 5.5.4 (xác nhận T0, 21/09/2026)

```
Tools → Session Frontend → tab Automation
     (KHÔNG phải Window → Developer Tools — Epic đã dời chỗ này ở 5.5)

Trong tab Automation:
  Filter (ô search test)  →  gõ đúng namespace, vd:  FurnitureTool.Undo
  Tick nhóm/test          →  Start Tests (nút ▶ góc trên trái)
  Kết quả hiện ở panel "Automation Test Graphical Results" phía dưới
```

## 8. File test đầu tiên — mẫu tham chiếu

```
Plugins/FurnitureToolkit/Source/FurnitureToolkit/Private/Tests/FurnitureToolkitTests.cpp
```

`Build.cs` KHÔNG cần sửa — `Core`/`Misc/AutomationTest.h` đã là dependency sẵn có.

```cpp
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS        // macro = 0 trong Shipping → test KHÔNG lọt bản ship

BEGIN_DEFINE_SPEC(FUndoArchHarnessSpec,
    "FurnitureTool.Undo.T0_Harness",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
END_DEFINE_SPEC(FUndoArchHarnessSpec)

void FUndoArchHarnessSpec::Define()
{
    Describe(TEXT("Test harness"), [this]()
    {
        It(TEXT("[UNDO-T0-01] chay duoc mot assertion dung"), [this]()
        {
            TestEqual(TEXT("1 + 1"), 1 + 1, 2);
        });
    });
}

#endif
```

`EAutomationTestFlags::EditorContext` compile sạch trên UE 5.5.4 — KHÔNG cần fallback
`ApplicationContextMask`.

**Không dấu tiếng Việt trong chuỗi test** — tên hiển thị trong Session Frontend, an toàn nhất
là ASCII. Mã invariant `[UNDO-xx-nn]` đặt đầu chuỗi để dễ tra ngược ra doc.

---

## 9. Lịch sử

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 21/09/2026 | Tạo file — T0 (Undo Architecture Harness Gate) PASS. `[UNDO-T0-01]` xanh, `[UNDO-T0-02]` (negative control) đỏ đúng ở lần chạy đầu rồi sửa xanh ở lần 2 — cuhoang tự chạy được không cần hỏi đường bấm. Nguồn: `Plans/18-09-2026_UndoArchitecture_Foundation_v1.md` §6, §8. |
