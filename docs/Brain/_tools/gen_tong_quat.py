# -*- coding: utf-8 -*-
"""Tầng TỔNG QUÁT — 3 canvas trong Brain/Tổng quát, đọc theo thứ tự 1 → 2 → 3 (mỗi canvas có thẻ "Đọc tiếp →").
Bố cục ĐẶT TAY theo tâm lý trình bày (xem [[Tư duy 4 · Cách viết tài liệu trong bộ não]]): tiêu đề = thông điệp ·
1 hướng đọc đánh số · chính to/xanh, phụ nhỏ/xám · neo vào ảnh màn hình thật · ít đường, không cắt nhau ·
cùng màu = cùng nghĩa ở cả 3 canvas (xanh 5 = đường chính · cam 2 = màn hình · vàng 3 = điểm hay nhầm · đỏ 1 = số trên ảnh).
Sửa NỘI DUNG ở đây rồi chạy build.py — không sửa trong canvas (bị ghi đè). Chạy riêng: python Brain/_tools/gen_tong_quat.py (thư mục docs).
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'Brain', 'Tổng quát'); os.makedirs(OUT, exist_ok=True)
DIR = 'docs/Brain/Tổng quát'                                   # đường dẫn trong vault (vault = gốc repo)
N1, N2, N3 = '1 · Một buổi dựng phòng', '2 · Phía sau màn hình', '3 · Khuôn 4 bước'
L = {k: v for k, v in [l.split('|') for l in (
    'L01|L01 · Mở tool và kho đồ', 'L02|L02 · Tìm đồ trong kho', 'L03|L03 · Kéo đồ vào phòng', 'L04|L04 · Chọn đồ',
    'L05|L05 · Di chuyển và xoay đồ', 'L06|L06 · Nhóm đồ và sửa nhóm', 'L07|L07 · Menu chuột phải và phím tắt', 'L08|L08 · Thay đồ',
    'L09|L09 · Đổi vật liệu', 'L10|L10 · Chỉnh thông số vật liệu', 'L11|L11 · Combo', 'L12|L12 · Lưu và mở cảnh',
    'L13|L13 · Hoàn tác và làm lại')]}
def ln(*ks): return ' · '.join(f'[[{L[k]}|{k}]]' for k in ks)

class C:
    def __init__(s): s.nodes, s.edges = [], []
    def card(s, id, x, y, w, h, text, color=None):
        n = {'id': id, 'type': 'text', 'x': x, 'y': y, 'width': w, 'height': h, 'text': text}
        if color: n['color'] = color
        s.nodes.append(n)
    def file(s, id, x, y, w, h, f):
        s.nodes.append({'id': id, 'type': 'file', 'file': f'{DIR}/ảnh/{f}', 'x': x, 'y': y, 'width': w, 'height': h})
    def group(s, id, x, y, w, h, label, color=None):
        g = {'id': id, 'type': 'group', 'x': x, 'y': y, 'width': w, 'height': h, 'label': label}
        if color: g['color'] = color
        s.nodes.insert(0, g)                                    # group vẽ dưới cùng
    def edge(s, a, fs, b, ts, label=None, color=None):
        e = {'id': f'e{len(s.edges)}', 'fromNode': a, 'fromSide': fs, 'toNode': b, 'toSide': ts}
        if label: e['label'] = label
        if color: e['color'] = color
        s.edges.append(e)
    def save(s, name):
        p = os.path.join(OUT, name + '.canvas')
        json.dump({'nodes': s.nodes, 'edges': s.edges}, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1); return p

MAIN, UI, NOTE, MARK = '5', '2', '3', '1'
FOOT = '<small>Bản tóm tắt để HIỂU — không phân ✓K2 / theo doc. Từng hàm + bằng chứng: note luồng L01…L13 → sơ đồ Phần 5 → canvas làn bơi.</small>'
def nxt(name, why): return f'### Đọc tiếp →\n[[{DIR}/{name}.canvas|{name}]]\n<small>{why}</small>'

# ═════════════ 1 · Một buổi dựng phòng (User + Screen flow) — bắt đầu từ cái người đọc đã biết: màn hình ═════════════
c = C()
c.card('t', 0, 0, 1610, 110, '# 1 · Một buổi dựng phòng — người dùng đi qua đâu\n'
       'Nhìn ảnh → số đỏ ① … ⑥ ứng với các bước bên phải, đọc từ trên xuống. <small>Mỗi bước có link ↗ tới note luồng (L01…L13).</small>')
IX, IY, IW = 0, 150, 980; K = IW / 1919
c.file('shot', IX, IY, IW, round(1079 * K), 'tq_UI_tong_quan.png')
for i, (ox, oy, t) in enumerate([(1275, 85, '①'), (235, 700, '②'), (1000, 760, '③'), (1330, 570, '④'), (1400, 85, '④'),
                                 (663, 540, '⑤'), (1495, 285, '⑤'), (375, 583, '⑥')]):
    c.card(f'm{i}', round(IX + ox * K) - 24, round(IY + oy * K) - 24, 48, 48, f'## {t}', MARK)
st = [('①', 'Mở kho đồ', 'bấm **Inventory** trên thanh công cụ', ln('L01'), 90),
      ('②', 'Tìm đồ', 'tab FURNITURE · danh mục bên trái · Search · Recent / Favorite', ln('L02'), 90),
      ('③', 'Đặt đồ vào phòng', 'kéo thẻ ra khỏi kho, thả vào phòng — có bóng xem trước, tự bám sàn / tường', ln('L03'), 110),
      ('④', 'Chọn và sắp xếp', 'click chọn (viền trắng) · quét khung · Move / Rotate / Scale · kéo gizmo · snap · Ctrl+G nhóm',
       ln('L04', 'L05', 'L06'), 130),
      ('⑤', 'Đổi vật liệu', 'tab MATERIAL: chọn slot (quả cầu) · bấm hoặc kéo vật liệu vào đồ · MATERIAL EDIT → bảng bên phải: độ nhám, màu',
       ln('L09', 'L10'), 130),
      ('⑥', 'Lưu / dùng lại cả cụm', 'tab COMBO: lưu cụm đồ thành combo · kéo combo có sẵn vào phòng · thay cả combo', ln('L11'), 100),
      ('⑦', 'Lưu cảnh', 'bấm **M** → menu Save/Load của project → Save / Load (lưu cả phòng để mở lại)', ln('L12'), 100)]
y = 150
for i, (n, name, txt, lk, h) in enumerate(st):
    c.card(f's{i}', 1040, y, 570, h, f'### {n} {name}\n{txt}\n<small>↗ {lk}</small>', MAIN)
    if i: c.edge(f's{i-1}', 'bottom', f's{i}', 'top', None, MAIN)
    y += h + 26
c.card('any', 0, 720, 980, 110, '### Bất cứ lúc nào\nCtrl+Z / Ctrl+Shift+Z hoàn tác / làm lại · chuột phải lên đồ: copy, dán, nhân bản, xoá, thay · ℹ thông tin · ♡ yêu thích\n'
       f'<small>↗ {ln("L07", "L08", "L13")}</small>')
c.card('next', 1040, y + 10, 570, 120, nxt(N2, 'mỗi vùng màn hình ở trên nối với khối nào phía sau'))
c.card('f', 0, 850, 980, 50, FOOT)
p1 = c.save(N1)

# ═════════════ 2 · Phía sau màn hình (Architecture) ═════════════
a = C()
a.card('t', 0, 0, 1720, 110, '# 2 · Phía sau màn hình có gì\n'
       '**Mọi thao tác đều đổi CẢNH · mọi thay đổi được SỔ LỊCH SỬ chụp lại để Ctrl+Z.** Đọc trái → phải: ① → ② → ③ → ④')
a.group('g1', 0, 170, 440, 900, '① Người dùng thấy — màn hình', UI)
a.card('r1', 20, 195, 400, 105, '**Thanh công cụ**\n![[tq_toolbar.png|360]]\n<small>chọn Move / Rotate / Scale · xoá · snap</small>', UI)
a.card('r2', 20, 320, 400, 235, '**Phòng 3D**\n![[tq_phong_ban_gizmo.png|170]]\n<small>click chọn đồ · kéo trục gizmo</small>', UI)
a.card('r3', 20, 575, 400, 245, '**Cửa sổ Furniture Warehouse**\n![[tq_warehouse.png|300]]\n<small>kho đồ · vật liệu · combo — kéo thẻ vào phòng</small>', UI)
a.card('r4', 20, 840, 400, 215, '**Bảng Material**\n![[tq_bang_material_tren.png|120]]\n<small>chỉnh độ nhám, màu của 1 slot</small>', UI)
a.card('dk', 560, 330, 300, 170, '## ② ĐIỀU KHIỂN\nnhận click, kéo gizmo, phím tắt → quyết định làm gì\n<small>↗ [[BP_FurnitureInputManager|InputManager]] · [[BP_GizmoController|Gizmo]] · [[BP_PivotActor|Pivot]]</small>', MAIN)
a.card('canh', 990, 520, 360, 230, '# ③ CẢNH\ncác món đồ đang đặt trong phòng: vị trí, nhóm, vật liệu từng slot\n\n→ màn hình tự cập nhật theo (viền trắng, gizmo, bảng Material)\n'
       '<small>↗ [[BP_FurnitureActor|FurnitureActor]] · [[BP_FurnitureSceneManager|SceneManager]]</small>', MAIN)
a.card('so', 1460, 540, 260, 190, f'## ④ SỔ LỊCH SỬ\nmỗi thao tác xong = **1 mốc** · Ctrl+Z = về mốc trước\n<small>↗ [[BP_UndoManager|UndoManager]] · {ln("L13")}</small>', MAIN)
a.group('gn', 900, 900, 860, 170, 'Nền — ít khi phải nghĩ tới')
a.card('n1', 915, 925, 265, 130, f'**Combo** — lưu / đặt cả cụm đồ (tab COMBO), đặt vào CẢNH\n<small>↗ [[BP_ComboManager]] · {ln("L11")}</small>')
a.card('n2', 1195, 925, 265, 130, '**Dịch vụ C++** — lọc danh sách, đọc/ghi vật liệu theo slot, ID bền vững, file combo\n<small>↗ [[MaterialSlotService_Reference|MaterialSlot]] · [[FurnitureFilterLibrary_Reference|Filter]]</small>')
a.card('n3', 1475, 925, 265, 130, f'**Lưu trữ** — Save / Load cảnh · Gần đây / Yêu thích\n<small>↗ [[BP_FurnitureSceneManager|Save/Load]] · [[BP_FurnitureUserPrefsManager|Prefs]] · {ln("L12")}</small>')
a.edge('r1', 'right', 'dk', 'left', 'chọn chế độ', MAIN)
a.edge('r2', 'right', 'dk', 'left', 'click · kéo gizmo', MAIN)
a.edge('dk', 'right', 'canh', 'left', 'chọn · dời · xoay · nhóm', MAIN)
a.edge('r3', 'right', 'canh', 'left', 'kéo-thả đồ / vật liệu', MAIN)
a.edge('r4', 'right', 'canh', 'left', 'chỉnh độ nhám · màu', MAIN)
a.edge('canh', 'right', 'so', 'left', 'chụp lại', MAIN)
a.edge('so', 'top', 'canh', 'top', 'Ctrl+Z: dựng lại')
a.card('next', 1460, 760, 300, 110, nxt(N3, '4 bước mà mọi thao tác ở đây đều đi qua'))
a.card('f', 0, 1100, 1760, 50, FOOT)
p2 = a.save(N2)

# ═════════════ 3 · Khuôn 4 bước (Logic flow) ═════════════
b = C()
b.card('t', 0, 0, 1730, 110, '# 3 · Mọi thao tác chỉnh đồ đều đi đúng 4 bước\n**Hiểu 1 thao tác là hiểu cả tool.** Đọc hàng KHUÔN trước → rồi 2 ví dụ thật bên dưới.')
X = [260, 640, 1020, 1400]; W = 330
b.card('k0', 0, 230, 220, 120, '### KHUÔN\n<small>đúng cho mọi thao tác chỉnh đồ</small>')
steps = ['## ① Ra lệnh\nclick · kéo gizmo · kéo slider · kéo thẻ', '## ② Đổi cảnh\nđồ dời / đổi màu ngay trước mắt',
         '## ③ Ghi 1 mốc\nvào Sổ lịch sử — **chỉ khi buông tay**', '## ④ Màn hình cập nhật\nviền · gizmo · bảng Material']
for i, t in enumerate(steps): b.card(f's{i}', X[i], 230, W, 120, t, MAIN)
for i in range(3): b.edge(f's{i}', 'right', f's{i+1}', 'left', None, MAIN)
b.edge('s2', 'top', 's1', 'top', 'Ctrl+Z: lấy mốc trước, dựng lại cảnh')
b.card('warn', X[1], 370, X[2] + W - X[1], 90, '⚠ **Điểm hay nhầm:** đang kéo thì ② lặp liên tục (chỉ xem trước), ③ chạy **đúng 1 lần** khi buông tay → **1 lần Ctrl+Z hoàn tác cả cú kéo.**', NOTE)
ex = [('Ví dụ 1', 'Đổi màu mặt bàn', '5b - Chỉnh 1 thông số vật liệu (U2 Interactive Edit Session).canvas', '5b', 'L10', 140,
       ['![[tq_vong_mau.png|120]]\nkéo vòng màu trong bảng Material', 'mặt bàn đổi màu theo tay kéo — **chưa ghi sổ**', 'buông chuột → sổ ghi **1 mốc**', 'bảng Material làm mới theo sổ']),
      ('Ví dụ 2', 'Kéo bàn bằng gizmo', '5f - Kéo gizmo Move (1 món · nhiều món qua Pivot).canvas', '5f', 'L05', 150,
       ['![[tq_gizmo_nho.png|90]]\nnhấn giữ 1 trục gizmo', 'bàn dời theo chuột mỗi khung hình, bám lưới snap', 'thả chuột → mốc **"Move"**', 'viền + gizmo nằm đúng chỗ mới'])]
y = 500
for r, (lab, name, cv, sid, lk, h, cells) in enumerate(ex):
    b.card(f'l{r}', 0, y, 220, h, f'### {lab}\n**{name}**\n<small>↗ {ln(lk)} · [[{cv}|canvas {sid}]]</small>')
    for i, t in enumerate(cells): b.card(f'x{r}{i}', X[i], y, W, h, t)
    y += h + 20
b.card('ex', 0, y + 10, 1730, 60, 'Ngoại lệ: kéo-thả từ Warehouse thì lớp kéo-thả tự làm ② ③ (không qua Điều khiển) · Lưu combo và Lưu cảnh KHÔNG ghi sổ (không đổi cảnh / không thuộc lịch sử).')
b.card('back', 1400, y + 90, 330, 90, '### Hết tầng tổng quát\n<small>↩ [[Bản đồ não]] · tiếp theo: bộ Tư duy, rồi các note luồng L01…L13</small>')
b.card('f', 0, y + 90, 1370, 50, FOOT)
p3 = b.save(N3)
print('tổng quát:', ', '.join(os.path.basename(p) for p in (p1, p2, p3)))
