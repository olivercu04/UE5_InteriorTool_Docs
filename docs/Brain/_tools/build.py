# -*- coding: utf-8 -*-
"""1 LỆNH dựng lại toàn bộ "bộ não thứ 2". Chạy từ thư mục docs:
    python Brain/_tools/build.py
  1. gen_brain.py      — mục 🧠 Kết nối cuối mỗi doc + note "Kết nối 3x" (từ Phần 3) + dòng "Có mặt trong thao tác" (từ note Lxx)
  2. gen_canvas.py     — Canvas làn bơi cho mỗi luồng 5x (từ Phần 5); thẻ có link nhảy tới đúng mục hàm trong doc
  3. gen_tong_quat.py  — 3 canvas tầng Tổng quát (Brain/Tổng quát) — bố cục đặt tay, nội dung trong script
  4. Brain/Kiểm tra bản đồ.md    — lệch Phần 3 ↔ Phần 5 · ? tồn đọng · K2 đáng xin nhất · thẻ chưa có link ·
                                    mục 5x chưa thuộc note luồng nào · link gãy trong Brain/
  5. Brain/Chỉ mục hàm & biến.md — hàm / biến → luồng nào, bước nào, bằng chứng gì (điểm xuất phát cho Q10)
Mọi file trên đều TỰ SINH — sửa Architecture_Map (hoặc script tổng quát) rồi chạy lại, đừng sửa tay. Không ghi ngày/version vào
file sinh ra → chạy lại khi nguồn không đổi thì git không thấy thay đổi.
"""
import os, re, sys, json, runpy
sys.dont_write_bytecode = True   # không đẻ __pycache__ trong vault
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import brainlib as BL
os.chdir(BL.ROOT)
for s in ('gen_brain.py', 'gen_canvas.py', 'gen_tong_quat.py'):
    print('==', s); runpy.run_path(os.path.join(HERE, s), run_name='__main__')

src = BL.load_map(); E3 = BL.p3_edges(src); FL = BL.p5_flows(src); FILES = BL.doc_files(); LN = BL.luong_notes()
EV = lambda st: 'thao tác' if st['user'] else ('✓K2' if st['k2'] else 'doc') + (' ?' if st['unk'] else '')
def cv(f, n=None):  # link tới Canvas của luồng
    return f"[[{BL.canvas_name(f['sid'], f['title'])}.canvas|{f['sid']}{' b' + str(n) if n else ''}]]"
def has(lab, toks, msg):
    """Nhãn Phần 3 có nhắc đúng hàm này không. Cả 2 bên cùng ghi tham số (vd CaptureSnapshot(Move)) thì tham số phải giao nhau."""
    for t in toks:
        if re.search(r'(?<!\w)' + re.escape(t) + r'(?!\w)', lab):
            a, b = BL.fn_args(lab, t), BL.fn_args(msg, t)
            if not a or not b or a & b: return True
    return False
pair3 = {}
for sid, A, B, lab, st in E3: pair3.setdefault((A, B), []).append((sid, lab, st))

miss, lag3, lag5, nolink, unk, meta, wish = [], [], [], [], {}, [], {}
fidx, vidx = {}, {}
for f in FL:
    tail = f['tail']
    q_steps = [st for st in f['steps'] if st['unk']]
    if q_steps or '**?**' in tail: unk[f['sid']] = (len(q_steps), tail.count('**?**'))
    if '**Kiểm chứng K2:**' not in tail or 'Nguồn:' not in tail: meta.append(f['sid'])
    for st in f['steps']:
        toks = BL.fn_tokens(st['msg']); sets, gets = BL.var_tokens(st['msg'])
        # ---- chỉ mục
        for t in toks:
            owner = next((d for d in BL._dedupe([st['B'], st['A']]) if d != 'User' and BL.find_heading(d, [t], FILES)), None)
            fidx.setdefault(t, {'owner': owner, 'uses': []})
            if owner and not fidx[t]['owner']: fidx[t]['owner'] = owner
            fidx[t]['uses'].append((f, st))
        own = st['A'] if st['A'] == st['B'] else st['B']
        who_ = dict(st, A=st['B']) if st['user'] else st        # bước của User: bên SET/GET thật là handler nhận thao tác
        for v in sets: vidx.setdefault(v, {'owner': own, 'SET': [], 'GET': []})['SET'].append((f, who_))
        for v in gets: vidx.setdefault(v, {'owner': own, 'SET': [], 'GET': []})['GET'].append((f, who_))
        # ---- thẻ canvas có link chưa
        if toks and not BL.step_link(st, FILES): nolink.append((f, st, toks))
        if st['user'] or st['A'] == st['B']: continue
        # ---- lệch Phần 3 ↔ Phần 5
        es = pair3.get((st['A'], st['B']))
        if not es: miss.append((f, st)); continue
        match = [e for e in es if toks and has(e[1], toks, st['msg'])]
        pair_k2 = any(e[2] == 'K2' for e in es)
        if st['k2']:
            if (match and not any(e[2] == 'K2' for e in match)) or (not match and not pair_k2): lag3.append((f, st, match or es))
        else:
            if any(e[2] == 'K2' for e in match) and not any(e[2] == 'doc' for e in match):
                lag5.append((f, st, [e for e in match if e[2] == 'K2']))
            key = (st['A'], st['B'], (toks or sets or gets or [st['vi'][:40]])[0])
            wish.setdefault(key, set()).add(f['sid'])

# ---- mục 5x chưa thuộc note luồng nào (Brain/Luồng/Lxx nhúng ![[Architecture_Map#5x — …]])
owned = {sid for sids in LN.values() for sid in sids}
orphan = [f for f in FL if f['sid'] not in owned]

# ---- chỉ mục (ghi TRƯỚC khi soát link để soát bản mới nhất)
def uses(lst): return ' · '.join(f"{cv(f, st['n'])} {EV(st)}".replace('|', '\\|') for f, st in lst)   # trong bảng: | của alias phải escape
def who(lst):
    g = {}
    for f, st in lst: g.setdefault(st['A'], []).append((f, st))
    return '<br>'.join(f"← `{a}` " + uses(x) for a, x in g.items())
sid2ln = {sid: ln for ln, sids in LN.items() for sid in sids}
def tasks(lst):
    ls = BL._dedupe([sid2ln[f['sid']] for f, _ in lst if f['sid'] in sid2ln])
    return ' '.join(f"[[{l}\\|{l.split(' · ')[0]}]]" for l in ls) or '—'
I = ['# Chỉ mục hàm & biến (tự sinh)', '',
     '> Sinh bằng `Brain/_tools/build.py` từ [[Architecture_Map]] Phần 5 — ĐỪNG sửa tay. `5f b21` = luồng 5f, bước 21 trên Canvas. Cột "Thao tác" = note luồng `L01…L13` chứa bước đó.',
     '> Dùng cho **Q10**: sắp sửa 1 hàm / đổi 1 biến → xem nó nằm ở luồng nào để rà. ⚠ Chỉ phủ các luồng ĐÃ vẽ ở Phần 5 — Q10 vẫn phải quét toàn project.',
     '> ← [[Bản đồ não]] · [[Kiểm tra bản đồ]]', '',
     f'## Hàm / sự kiện ({len(fidx)})', '', '| Hàm | Mục trong doc | Thao tác | Xuất hiện ở |', '|---|---|---|---|']
for t in sorted(fidx, key=str.lower):
    o = fidx[t]['owner']; h = BL.find_heading(o, [t], FILES) if o else None
    I.append(f"| `{t}` | " + (f"[[{o}#{BL.link_heading(h[0])}\\|{o}]]" if h else '—') + f" | {tasks(fidx[t]['uses'])} | {uses(fidx[t]['uses'])} |")
I += ['', f'## Biến ({len(vidx)})', '> "Của" = actor giữ biến (bên nhận mũi tên). Ghi/Đọc = ai SET/GET, ở bước nào — chính là cột Producer/Consumer của Q10.', '',
      '| Biến | Của | Ghi (SET) | Đọc (GET) |', '|---|---|---|---|']
for v in sorted(vidx, key=str.lower):
    d = vidx[v]; I.append(f"| `{v}` | [[{d['owner']}]] | {who(d['SET']) or '—'} | {who(d['GET']) or '—'} |")
open(os.path.join('Brain', 'Chỉ mục hàm & biến.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(I) + '\n')

# ---- link gãy trong Brain/ (note + canvas) và Architecture_Map
VAULT = os.path.dirname(BL.ROOT)
names = {}
names.update({n: n for n in ('Kiểm tra bản đồ.md', 'Chỉ mục hàm & biến.md')})   # 2 file build này sắp ghi
for d, dirs, fs in os.walk(VAULT):
    dirs[:] = [x for x in dirs if not x.startswith('.')]
    for fn in fs: names.setdefault(fn, os.path.join(d, fn))
def all_headings(path):
    hs, code = [], False
    for line in open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n'):
        if line.startswith('```'): code = not code; continue
        m = None if code else re.match(r'#{1,6}\s+(.*\S)\s*$', line)
        if m: hs.append(BL.link_heading(m.group(1)))
    return hs
def resolve(target):
    t = target.replace('\\|', '|').split('|')[0].strip(); t, _, h = t.partition('#')
    if not t: return True
    base = os.path.basename(t)
    cand = [base] if os.path.splitext(base)[1].lower() in ('.canvas', '.png', '.jpg', '.jpeg', '.svg', '.md') else [base + '.md', base]
    p = next((names[c] for c in cand if c in names), None)
    if not p: return False
    if h and p.endswith('.md'): return BL.link_heading(h) in all_headings(p)
    return True
broken = []
scan = [os.path.join(BL.ROOT, '00_Core', 'Architecture_Map.md')]
for d, _, fs in os.walk(os.path.join(BL.ROOT, 'Brain')):
    if '_tools' in d: continue
    scan += [os.path.join(d, x) for x in fs if x.endswith(('.md', '.canvas'))]
for p in sorted(scan):
    txt = open(p, encoding='utf-8').read()
    if p.endswith('.canvas'):
        txt = '\n'.join(n.get('text', '') + (f"\n[[{n['file']}]]" if 'file' in n else '') for n in json.load(open(p, encoding='utf-8'))['nodes'])
    txt = re.sub(r'```.*?```', '', txt, flags=re.S)
    links = []                                          # giữ link (có thể chứa `code`) → bỏ code inline → lấy lại link nằm ngoài code
    txt = re.sub(r'!?\[\[([^\]]+)\]\]', lambda m: (links.append(m.group(1)), f'\x00{len(links) - 1}\x00')[1], txt)
    txt = re.sub(r'`[^`\n]*`', '', txt)
    for i in re.findall(r'\x00(\d+)\x00', txt):
        if not resolve(links[int(i)]): broken.append((os.path.relpath(p, BL.ROOT), links[int(i)]))

def row(f, st): return f"{cv(f, st['n'])} `{st['A']}→{st['B']}` {st['vi'].strip()} · `{st['fn'].strip()}`"
L = ['# Kiểm tra bản đồ (tự sinh)', '',
     '> Sinh bằng `Brain/_tools/build.py` từ [[Architecture_Map]] — ĐỪNG sửa tay. Mục ❌, ⚠ và 🔗 phải về 0 thì bản đồ mới khớp và dùng được.',
     '> ← [[Bản đồ não]] · [[Chỉ mục hàm & biến]]', '',
     f'**Tóm tắt:** ❌ thiếu cạnh {len(miss)} · ⚠ Phần 3 tụt bằng chứng {len(lag3)} · 🔗 link gãy {len(broken)} · ℹ Phần 5 có thể tụt {len(lag5)} · '
     f'? tồn đọng {sum(a + b for a, b in unk.values())} · thẻ chưa có link {len(nolink)} · mục 5x chưa thuộc luồng {len(orphan)} · '
     f'luồng thiếu dòng Kiểm chứng/Nguồn {len(meta)}', '']
L += [f'## ❌ Cặp gọi nhau ở Phần 5 nhưng Phần 3 không có cạnh ({len(miss)})', '> Thêm cạnh vào sơ đồ 3x phù hợp (nét đứt nếu chỉ theo doc), rồi chạy lại.', '']
L += [f'- {row(f, st)}' for f, st in miss] or ['- (không có)']
L += ['', f'## ⚠ Phần 3 tụt bằng chứng — Phần 5 đã ✓K2 mà Phần 3 còn đứt ({len(lag3)})', '> Nâng cạnh Phần 3 lên `==>` + nhãn ngày K2 (hoặc tách cạnh nếu nhãn trộn nhiều hàm).', '']
L += [f'- {row(f, st)}  ← Phần 3: ' + ' / '.join(f'{e[0]} "{e[1]}" ({e[2]})' for e in es) for f, st, es in lag3] or ['- (không có)']
L += ['', f'## 🔗 Link gãy trong Brain/ và Architecture_Map ({len(broken)})', '> Tên file / mục (heading) không còn — thường do đổi tên. Sửa link ở file nguồn (file tự sinh thì sửa script).', '']
L += [f'- `{p}` → `[[{t}]]`' for p, t in broken] or ['- (không có)']
L += ['', f'## ℹ Phần 5 có thể tụt — mũi tên đứt nhưng Phần 3 đã ✓K2 đúng hàm này ({len(lag5)})', '> Xem lại: có thể hợp lệ (Phần 3 chỉ K2 1 phần nhãn), hoặc Phần 5 quên nâng.', '']
L += [f'- {row(f, st)}  ← Phần 3: ' + ' / '.join(f'{e[0]} "{e[1]}"' for e in es) for f, st, es in lag5] or ['- (không có)']
L += ['', '## ? tồn đọng theo luồng', '']
L += [f'- {cv(next(x for x in FL if x["sid"] == s))}: {a} mũi tên có `?` · {b} dòng **?** dưới sơ đồ' for s, (a, b) in sorted(unk.items())] or ['- (không có)']
top = sorted(wish.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:10]
L += ['', '## 🎯 K2 đáng xin nhất — mũi tên đứt dùng ở nhiều luồng nhất', '> 1 export nâng được nhiều mũi tên nhất. Export đúng hàm ở cột "Hàm / biến".', '',
      '| Luồng | Từ → Tới | Hàm / biến |', '|---|---|---|']
L += [f"| {len(v)}: {', '.join(sorted(v))} | `{k[0]}` → `{k[1]}` | `{k[2]}` |" for k, v in top]
L += ['', f'## Thẻ Canvas có tên hàm nhưng chưa tìm được mục trong doc ({len(nolink)})', '> Doc chưa có heading cho hàm này (hoặc tên lệch) → thẻ không có link ↗.', '']
L += [f"- {row(f, st)} — tìm: {', '.join(toks)}" for f, st, toks in nolink] or ['- (không có)']
L += ['', f'## Mục 5x chưa thuộc note luồng nào ({len(orphan)})', '> Mỗi mục 5x phải được nhúng trong đúng 1 note `Brain/Luồng/Lxx` — không thì người đọc theo hành trình sẽ không gặp nó.', '']
L += [f'- {cv(f)} {f["title"]}' for f in orphan] or ['- (không có)']
L += ['', f'## Mục 5x thiếu dòng "Kiểm chứng K2:" hoặc "Nguồn:" ({len(meta)})', ''] + ([f'- {s}' for s in meta] or ['- (không có)'])
open(os.path.join('Brain', 'Kiểm tra bản đồ.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')

print(L[5]); print('chỉ mục:', len(fidx), 'hàm ·', len(vidx), 'biến')
