# -*- coding: utf-8 -*-
"""Sinh lớp 'bộ não thứ 2' cho Obsidian từ 00_Core/Architecture_Map.md (Phần 3 + mục 5x nào thuộc note luồng Lxx nào).
Chạy lại được nhiều lần (idempotent): chỉ thay đoạn giữa 2 marker BRAIN:START/END ở cuối mỗi doc,
và ghi đè các note trong docs/Brain/. KHÔNG sửa nội dung doc canonical phía trên marker.
Chạy từ thư mục docs:  python3 Brain/_tools/gen_brain.py
"""
import re, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brainlib as BL
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
START = '<!-- BRAIN:START — tự sinh từ Architecture_Map bằng Brain/_tools/gen_brain.py, ĐỪNG sửa tay đoạn này -->'
END = '<!-- BRAIN:END -->'
SPECIAL = {'WBP_DragOverlay': 'WBP_DragOverlay_FurnitureCard', 'UMaterialParamMap': 'MaterialSlotService_Reference',
           'MaterialSlotService': 'MaterialSlotService_Reference', 'UEntityIdLibrary': 'EntityIdLibrary_Reference',
           'UFurnitureFilterLibrary': 'FurnitureFilterLibrary_Reference', 'UComboSerializer': 'ComboSerializer_Reference'}
SKIP_DIRS = ('Brain', 'Archive', 'import_raw')

def load(p):
    s = open(p, 'rb').read().decode('utf-8'); crlf = s.count('\r\n') > s.count('\n') / 2
    return s.replace('\r\n', '\n'), crlf
def save(p, s, crlf):
    open(p, 'wb').write((s.replace('\n', '\r\n') if crlf else s).encode('utf-8'))

files = {}
for d, _, fs in os.walk('.'):
    if any(x in d for x in SKIP_DIRS): continue
    for f in fs:
        if f.endswith('.md'): files[f[:-3]] = os.path.join(d, f)

def canon(label):
    base = re.split(r'[\s(—]', label.strip())[0]
    return SPECIAL.get(base, base)

amap = open('00_Core/Architecture_Map.md', encoding='utf-8').read()
p3 = amap[amap.index('## Phần 3'):amap.index('## Phần 4')]
flows = []  # (sid, title, flowNoteName, nodes{name:label}, edges[(a,b,label,style)])
for sid, title, body in re.findall(r'### (3\w) — ([^\n]*)\n.*?```mermaid\n(.*?)```', p3, re.S):
    ids = {}
    for m in re.finditer(r'^\s*(\w+)\s*(\(\[|\[\[|\[|>|\(\()\s*"?([^"\]\)]*)', body, re.M):
        if m.group(1) in ('flowchart', 'subgraph', 'classDef', 'class'): continue
        ids[m.group(1)] = m.group(3).strip()
    edges = []
    for a, st, lab, b in re.findall(r'^\s*(\w+)\s*(-\.->|==>|-->)\|"([^"]*)"\|\s*(\w+)', body, re.M):
        if a in ids and b in ids and canon(ids[a]) != canon(ids[b]):
            edges.append((canon(ids[a]), canon(ids[b]), lab, 'k2' if st == '==>' else ''))
    clean = re.sub(r'[·/()]', ' ', title); clean = re.sub(r'\s+', ' ', clean).strip()
    flows.append((sid, title, f'Kết nối {sid} - {clean}', {canon(v): v for v in ids.values()}, edges))

# thành phần → note luồng thao tác (Brain/Luồng/Lxx) có nó trong sơ đồ 5x được nhúng
_p5 = {f['sid']: f for f in BL.p5_flows(amap)}
in_task = {}
for ln, sids in BL.luong_notes().items():
    for sid in sids:
        for part in (_p5[sid]['parts'].values() if sid in _p5 else []):
            if part != 'User': in_task.setdefault(canon(part), [])
            if part != 'User' and ln not in in_task[canon(part)]: in_task[canon(part)].append(ln)

def link(n):
    return f'[[{n}]]'
def is_stub(n): return n not in files

# gom cạnh theo thành phần
out, inc, member = {}, {}, {}
for sid, title, fn, nodes, edges in flows:
    for n in nodes: member.setdefault(n, []).append(fn)
    for a, b, lab, st in edges:
        if (b, lab) not in [(x[0], x[1]) for x in out.get(a, [])]:
            out.setdefault(a, []).append((b, lab, fn, st))
        if (a, lab) not in [(x[0], x[1]) for x in inc.get(b, [])]:
            inc.setdefault(b, []).append((a, lab, fn, st))

def block(n):
    L = [START, '', '## 🧠 Kết nối (bản đồ não)', '',
         '> Nguồn: [[Architecture_Map]] Phần 3. ✓K2 = đã kiểm chứng K2, không dấu = theo doc. Mở **Local graph** của file này để thấy hàng xóm trực tiếp.', '']
    fl = sorted(set(member.get(n, [])))
    tk = in_task.get(n, [])
    if tk: L += ['**Có mặt trong thao tác:** ' + ' · '.join(f'[[{t}|{t.split(" · ")[0]}]]' for t in tk), '']
    if fl: L += ['**Thuộc mảng kết nối:** ' + ' · '.join(link(f) for f in fl), '']
    if out.get(n):
        L += ['**Gọi / điều khiển →**']
        L += [f'- {link(b)} — {lab}' + (' ✓K2' if st else '') for b, lab, f, st in out[n]]
        L += ['']
    if inc.get(n):
        L += ['**← Được gọi bởi**']
        L += [f'- {link(a)} — {lab}' + (' ✓K2' if st else '') for a, lab, f, st in inc[n]]
        L += ['']
    L += [END]
    return '\n'.join(L)

touched, stubs = [], []
allnames = set(member)
for n in sorted(allnames):
    b = block(n)
    if is_stub(n):
        p = os.path.join('Brain', 'Chưa có doc', n + '.md'); stubs.append(n)
        s = (f'# {n}\n\n> ⚠ Thành phần CÓ trong Architecture_Map nhưng CHƯA có doc canonical. '
             f'Note này chỉ để graph đủ mắt xích — xem các luồng bên dưới.\n\n#chua-co-doc\n\n' + b + '\n')
        save(p, s, False); continue
    p = files[n]; s, crlf = load(p)
    if START in s:
        s = s[:s.index(START)].rstrip('\n') + '\n\n' + b + '\n' + s[s.index(END) + len(END):].lstrip('\n')
    else:
        s = s.rstrip('\n') + '\n\n---\n\n' + b + '\n'
    save(p, s, crlf); touched.append(p)

# doc từng có mục 🧠 nhưng nay không còn cạnh nào ở Phần 3 → thay bằng dòng báo, không để cạnh cũ nằm lại
for n, p in sorted(files.items()):
    if n in allnames: continue
    s, crlf = load(p)
    if START not in s: continue
    b = '\n'.join([START, '', '## 🧠 Kết nối (bản đồ não)', '',
                   '> Thành phần này KHÔNG còn cạnh nào trong [[Architecture_Map]] Phần 3 (vd chức năng đã chuyển sang BP khác). Xem changelog của bản đồ.', '', END])
    s = s[:s.index(START)].rstrip('\n') + '\n\n' + b + '\n' + s[s.index(END) + len(END):].lstrip('\n')
    save(p, s, crlf); touched.append(p)

# note luồng
for sid, title, fn, nodes, edges in flows:
    L = [f'# {fn}', '', f'> Tự sinh từ [[Architecture_Map]] mục **{sid} — {title}**. '
         'Dấu ✓K2 = cạnh nét dày `==>` trên sơ đồ gốc (đã kiểm chứng K2, diagram-contract §2); không dấu = theo doc. Sửa bản đồ gốc rồi chạy lại script.', '',
         '← [[Bản đồ não]] · Mức asset (ai nói chuyện với ai). Theo từng THAO TÁC của người dùng → note `L01…L13` trong `Brain/Luồng/`.', '', '## Thành phần', '']
    L += [f'- {link(n)}' + (' *(chưa có doc)*' if is_stub(n) else '') for n in sorted(nodes)]
    L += ['', '## Ai gọi ai', '']
    L += [f'- {link(a)} → {link(b)} — {lab}' + (' ✓K2' if st else '') for a, b, lab, st in edges]
    os.makedirs(os.path.join('Brain', 'Kết nối'), exist_ok=True)
    save(os.path.join('Brain', 'Kết nối', fn + '.md'), '\n'.join(L) + '\n', False)

print('flows', len(flows), '| docs gắn link', len(touched), '| stub', len(stubs))
print('STUBS:', ', '.join(stubs))
