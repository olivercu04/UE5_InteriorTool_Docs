# -*- coding: utf-8 -*-
"""Chuyển các sequenceDiagram ở Architecture_Map Phần 5 thành Obsidian Canvas (swimlane) — Brain/Canvas/*.canvas.
Nguồn DUY NHẤT vẫn là Architecture_Map; chạy lại script sau khi sửa Phần 5. Chạy từ thư mục docs:
    python3 Brain/_tools/gen_canvas.py
Quy ước (giữ nghĩa diagram-contract): mũi tên liền ->> = ✓K2 (cạnh xanh lá, nhãn có ✓K2) · đứt -->> = theo doc (xám) ·
nhãn có '?' = chưa rõ (đỏ). Màu chỉ là lớp phụ — trạng thái luôn có chữ trên nhãn/thẻ.
"""
import re, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
DOC = {'MaterialSlotService': 'MaterialSlotService_Reference'}
LANE_W, GAP, CARD_W, TOP = 380, 60, 330, 170

def doc_of(label):
    base = re.split(r'[\s(]', label.strip())[0]
    return DOC.get(base, base)
def lane_color(label):
    if label.startswith('WBP_'): return '2'      # cam = Widget
    if label.startswith('BP_'): return '5'       # xanh = Blueprint
    if 'C++' in label: return '6'                # tím = C++
    return None
def est_h(text):
    lines = sum(max(1, -(-len(l) // 40)) for l in text.split('\n'))
    return 36 + 22 * lines

src = open('00_Core/Architecture_Map.md', encoding='utf-8').read()
p5 = src[src.index('## Phần 5'):src.index('## Hướng dẫn điền dần')]
names = set(f[:-3] for d, _, fs in os.walk('.') for f in fs if f.endswith('.md'))
out = []
for sid, title, body in re.findall(r'### (5\w) — ([^\n]*)\n+```mermaid\n(.*?)```', p5, re.S):
    parts, order = {}, []
    for kind, pid, lab in re.findall(r'^\s*(participant|actor)\s+(\w+)\s+as\s+(.+)$', body, re.M):
        parts[pid] = lab.strip(); order.append(pid)
    nodes, edges = [], []
    lx = {pid: i * (LANE_W + GAP) for i, pid in enumerate(order)}
    last = {}
    # tiêu đề + chú giải
    total_w = len(order) * (LANE_W + GAP) - GAP
    nodes.append({'id': 'title', 'type': 'text', 'x': 0, 'y': -120, 'width': total_w, 'height': 170,
                  'text': f'# {sid} — {title}\nNguồn: [[Architecture_Map]] Phần 5 (tự sinh, đừng sửa tay). '
                          '**Đi theo mũi tên 1 → 2 → 3… = đi theo thời gian.** Mũi tên **xanh lá + ✓K2** = đã kiểm chứng K2 · **xám** = theo doc · **đỏ + ?** = chưa rõ. Dòng nhỏ cuối thẻ = ai gọi. Thẻ vàng = nhánh ngược lại / ghi chú.'})
    # thẻ đầu làn
    for pid in order:
        lab = parts[pid]; d = doc_of(lab)
        txt = f'### [[{d}]]' + (f'\n{lab[len(d):].strip()}' if lab[len(d):].strip() else '') if d in names else f'### {lab}'
        nodes.append({'id': f'h_{pid}', 'type': 'text', 'x': lx[pid] + (LANE_W - CARD_W) // 2, 'y': TOP - 30,
                      'width': CARD_W, 'height': 90, 'text': txt, **({'color': lane_color(lab)} if lane_color(lab) else {})})
        last[pid] = f'h_{pid}'
    y = TOP + 110; step = 0; ctx = []
    # prev = các thẻ vừa xảy ra (nhiều thẻ khi 2 nhánh alt nhập lại) · frames = khối alt/opt/loop đang mở
    prev, frames, notes_wait = [], [], []
    def link(srcs, to_id, to_lane, label, color, back=False):
        for f_id, f_lane, extra in srcs:
            if back and f_lane == to_lane: side = ('left', 'left')
            elif f_lane is None or to_lane is None or f_lane == to_lane: side = ('bottom', 'top')
            else: side = ('right', 'left') if lx[f_lane] < lx[to_lane] else ('left', 'right')
            e = {'id': f'e{len(edges)}', 'fromNode': f_id, 'fromSide': side[0], 'toNode': to_id, 'toSide': side[1]}
            lab = (label + extra).strip(' ·')
            if lab: e['label'] = lab
            if color: e['color'] = color
            edges.append(e)
    for raw in body.split('\n'):
        line = raw.strip()
        if not line or line.startswith(('---', 'title:', 'sequenceDiagram', 'participant', 'actor')): continue
        m = re.match(r'(alt|else|loop|opt)\s*(.*)', line)
        if m:
            k, cond = m.groups(); notes_wait = []
            if k == 'else':
                ctx[-1] = ('else', cond); fr = frames[-1]
                fr['ends'] += prev; prev = list(fr['start'])          # nhánh else xuất phát lại từ thẻ trước alt
            else:
                ctx.append((k, cond)); frames.append({'kind': k, 'start': list(prev), 'ends': [], 'first': None})
            continue
        if line == 'end':
            notes_wait = []
            if ctx: ctx.pop()
            if frames:
                fr = frames.pop()
                if fr['kind'] == 'alt': prev = fr['ends'] + prev     # 2 nhánh nhập lại
                elif fr['kind'] == 'opt': prev = prev + [(i, l, ' · nếu không') for i, l, _ in fr['start']]
                elif fr['kind'] == 'loop' and fr['first'] and prev and prev[0][0] != fr['first'][0]:
                    link(prev, fr['first'][0], fr['first'][1], '↻ lặp', None, back=True)
            continue
        m = re.match(r'Note over ([\w,]+):\s*(.*)', line)
        if m:
            ids = m.group(1).split(','); xs = [lx[i] for i in ids if i in lx]
            x0, x1 = min(xs), max(xs) + LANE_W; h = est_h(m.group(2)) * CARD_W // max(CARD_W, x1 - x0 - 40) + 20
            nid = f'n{len(nodes)}'
            nodes.append({'id': nid, 'type': 'text', 'x': x0 + 20, 'y': y, 'width': x1 - x0 - 40,
                          'height': max(70, h), 'text': '📝 ' + m.group(2), 'color': '3'})
            notes_wait.append(nid)                                   # chỉ nối vào chuỗi nếu còn bước theo sau
            y += max(70, h) + 40; continue
        m = re.match(r'(\w+)\s*(-->>|->>)\s*(\w+)\s*:\s*(.*)', line)
        if not m: continue
        a, arrow, b, msg = m.groups(); step += 1
        vi, _, fn = msg.partition(' · ')
        # '1. bỏ chọn…' = số Step trong doc hàm → đưa xuống dòng nhỏ, tránh 2 lớp số chồng nhau
        ms = re.match(r'(\d+[a-z]?)\.\s+(.*)', vi); dstep = ''
        if ms: dstep, vi = f'Step {ms.group(1)} doc · ', ms.group(2)
        tag = ''
        for k, cond in ctx:
            tag += {'alt': f'▸ nếu {cond}\n', 'else': f'▸ ngược lại: {cond}\n', 'loop': f'↻ lặp: {cond}\n', 'opt': f'◇ khi: {cond}\n'}[k]
        caller = re.sub(r' *[(].*', '', parts[a])
        who = 'nội bộ' if a == b else '← ' + caller
        user = parts.get(a, '') == 'User'
        k2 = arrow == '->>' and not user; unk = '?' in msg
        state = 'thao tác người dùng' if user else ('✓K2' if k2 else ('chưa rõ ?' if unk else 'theo doc'))
        text = f'{tag}**{step}.** {vi}' + (f'\n`{fn}`' if fn else '') + f'\n<small>{dstep}{who} · {state}</small>'
        h = est_h(text); nid = f's{step}'
        node = {'id': nid, 'type': 'text', 'x': lx[b] + (LANE_W - CARD_W) // 2, 'y': y, 'width': CARD_W, 'height': h, 'text': text}
        if ctx and ctx[-1][0] == 'else': node['color'] = '3'
        if unk: node['color'] = '1'
        nodes.append(node)
        # mũi tên theo THỜI GIAN: (các) thẻ vừa xảy ra → thẻ này; bước đầu xuất phát từ thẻ đầu làn của bên gọi
        if not prev: prev = [(f'h_{a}', a, '')]
        for n_id in notes_wait:                                      # ghi chú nằm giữa 2 bước = 1 nhịp thời gian
            link(prev, n_id, None, '', None); prev = [(n_id, None, '')]
        notes_wait = []
        link(prev, nid, b, f'{step}' + (' ✓K2' if k2 else '') + (' ?' if unk else ''), '1' if unk else ('4' if k2 else None))
        prev = [(nid, b, '')]
        for fr in frames:
            if fr['kind'] == 'loop' and fr['first'] is None: fr['first'] = (nid, b)
        y += h + 40
    # nền làn (group) phủ toàn chiều cao
    for pid in order:
        g = {'id': f'lane_{pid}', 'type': 'group', 'x': lx[pid], 'y': TOP - 60, 'width': LANE_W, 'height': y - TOP + 80,
             'label': parts[pid]}
        if lane_color(parts[pid]): g['color'] = lane_color(parts[pid])
        nodes.insert(0, g)
    fn = f'Brain/Canvas/{sid} - {re.sub(r"[/:]", "-", title)}.canvas'
    json.dump({'nodes': nodes, 'edges': edges}, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    out.append((fn, step))
for fn, n in out: print(n, 'bước ->', fn)
