# -*- coding: utf-8 -*-
"""Thư viện chung cho Brain/_tools (CHỈ ĐỌC, không ghi file):
đọc Architecture_Map Phần 3 (cạnh asset) + Phần 5 (sequence) · tách tên hàm / biến trong nhãn mũi tên ·
tra mục (heading) trong doc canonical để thẻ Canvas nhảy thẳng tới đúng hàm ·
đọc note luồng thao tác (Brain/Luồng/Lxx) để biết mục 5x nào thuộc luồng nào.
"""
import re, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPECIAL = {'WBP_DragOverlay': 'WBP_DragOverlay_FurnitureCard', 'UMaterialParamMap': 'MaterialSlotService_Reference',
           'MaterialSlotService': 'MaterialSlotService_Reference', 'UEntityIdLibrary': 'EntityIdLibrary_Reference',
           'UFurnitureFilterLibrary': 'FurnitureFilterLibrary_Reference', 'UComboSerializer': 'ComboSerializer_Reference'}
SKIP_DIRS = ('Brain', 'Archive', 'import_raw')
STOP = {'Get', 'IsValid', 'Branch', 'Cast', 'Make', 'Print', 'Return', 'LineTrace', 'Snap', 'Timer', 'Delay', 'Sequence', 'Select'}
LUONG_DIR = os.path.join('Brain', 'Luồng')

def canon(label):
    base = re.split(r'[\s(—]', label.strip())[0]
    return SPECIAL.get(base, base)

def load_map():
    return open(os.path.join(ROOT, '00_Core', 'Architecture_Map.md'), encoding='utf-8').read()

def p3_edges(src):
    """[(sid, A, B, label, 'K2'|'doc')] — A/B là tên doc (đã canon). Nét dày ==> = K2 (diagram-contract §2)."""
    p3 = src[src.index('## Phần 3'):src.index('## Phần 4')]
    out = []
    for sid, body in re.findall(r'### (3\w) — [^\n]*\n.*?```mermaid\n(.*?)```', p3, re.S):
        ids = {}
        for m in re.finditer(r'^\s*(\w+)\s*(\(\[|\[\[|\[|>|\(\()\s*"?([^"\]\)]*)', body, re.M):
            if m.group(1) in ('flowchart', 'subgraph', 'classDef', 'class'): continue
            ids[m.group(1)] = canon(m.group(3))
        for a, st, lab, b in re.findall(r'^\s*(\w+)\s*(-\.->|==>|-->)\|"([^"]*)"\|\s*(\w+)', body, re.M):
            if a in ids and b in ids:
                out.append((sid, ids[a], ids[b], lab, 'K2' if st == '==>' else 'doc'))
    return out

def canvas_name(sid, title):
    return f'{sid} - {re.sub(r"[/:]", "-", title)}'

def p5_flows(src):
    """Mỗi luồng 5x: sid, title, parts, steps (đánh số y hệt gen_canvas: mỗi mũi tên = 1 bước), tail (đoạn chữ sau sơ đồ)."""
    p5 = src[src.index('## Phần 5'):src.index('## Hướng dẫn điền dần')]
    flows = []
    for m in re.finditer(r'### (5\w) — ([^\n]*)\n+```mermaid\n(.*?)```(.*?)(?=\n### 5|\Z)', p5, re.S):
        sid, title, body, tail = m.groups()
        parts = {pid: l.strip() for _, pid, l in re.findall(r'^\s*(participant|actor)\s+(\w+)\s+as\s+(.+)$', body, re.M)}
        steps = []
        for a, ar, b, msg in re.findall(r'^\s*(\w+)\s*(-->>|->>)\s*(\w+)\s*:\s*(.*)$', body, re.M):
            user = parts.get(a, '') == 'User'
            vi, _, fn = msg.partition(' · ')
            steps.append(dict(n=len(steps) + 1, a=a, b=b, A=canon(parts[a]), B=canon(parts[b]), msg=msg.strip(), vi=vi, fn=fn,
                              user=user, k2=(ar == '->>' and not user), unk=('?' in msg)))
        flows.append(dict(sid=sid, title=title, parts=parts, steps=steps, tail=tail, body=body))
    return flows

def luong_notes():
    """{tên note Lxx: [sid 5x được nhúng trong note]} — nguồn: dòng ![[Architecture_Map#5x — …]] trong Brain/Luồng/*.md."""
    d = os.path.join(ROOT, LUONG_DIR); out = {}
    if not os.path.isdir(d): return out
    for f in sorted(os.listdir(d)):
        if f.endswith('.md') and re.match(r'L\d\d', f):
            txt = open(os.path.join(d, f), encoding='utf-8').read()
            out[f[:-3]] = re.findall(r'!\[\[Architecture_Map#(5\w) — ', txt)
    return out

def _dedupe(xs):
    out = []
    for x in xs:
        if x not in out: out.append(x)
    return out

def fn_tokens(text):
    """Tên hàm/sự kiện trong nhãn: Foo( (dính liền) · Broadcast OnBar · OnXxx · IA_Xxx. Bỏ node engine nhiều chữ (Set Actor Location()) và STOP."""
    toks = []
    for m in re.finditer(r'(?<!\w)([A-Z][A-Za-z0-9_]*)\(', text):          # Foo( dính liền — 'X (ghi chú)' không phải lời gọi
        if re.search(r'(?<!\w)[A-Z][A-Za-z0-9_]*\s+$', text[:m.start(1)]): continue
        toks.append(m.group(1))
    toks += re.findall(r'\bBroadcast (\w+)', text)
    toks += re.findall(r'(?<!\w)(On[A-Z]\w*|IA_\w+)', text)
    return [t for t in _dedupe(toks) if t not in STOP]

def fn_args(text, tok):
    """Chữ trong ngoặc của lời gọi tok: CaptureSnapshot("Move" / "Rotate") → {'Move','Rotate'} (rỗng = không ghi tham số)."""
    m = re.search(r'(?<!\w)' + re.escape(tok) + r'\(([^)]*)\)', text)
    return set(re.findall(r'[A-Za-z]\w*', m.group(1))) if m else set()

def var_tokens(text):
    """(biến được SET, biến được GET) trong nhãn."""
    res = {'SET': [], 'GET': []}
    for kw in res:
        for m in re.finditer(r'\b%s ([^→]+)' % kw, text):
            for part in re.split(r'[,·]', m.group(1)):
                mm = re.match(r'\s*(?:[A-Za-z_]\w*\.)?([A-Za-z_][A-Za-z0-9_]*)\s*(?==|\(|$)', part)
                if mm and len(mm.group(1)) > 2: res[kw].append(mm.group(1))
                elif part.strip(): break
    res['GET'] += re.findall(r'Get\(0\)\.([A-Za-z_]\w*)', text)
    return _dedupe(res['SET']), _dedupe(res['GET'])

def doc_files():
    files = {}
    for d, _, fs in os.walk(ROOT):
        if any(x in os.path.relpath(d, ROOT).split(os.sep) for x in SKIP_DIRS): continue
        for f in fs:
            if f.endswith('.md'): files[f[:-3]] = os.path.join(d, f)
    return files

_H = {}
def headings(stem, files):
    if stem not in _H:
        hs = []
        if stem in files:
            txt = open(files[stem], encoding='utf-8').read()
            if '<!-- BRAIN:START' in txt: txt = txt[:txt.index('<!-- BRAIN:START')]
            code = False
            for line in txt.replace('\r\n', '\n').split('\n'):
                if line.startswith('```'): code = not code; continue
                m = None if code else re.match(r'#{1,6}\s+(.*\S)\s*$', line)
                if m: hs.append(m.group(1))
        _H[stem] = hs
    return _H[stem]

def link_heading(h):
    """Obsidian không nhận # | ^ : [ ] % trong link tới heading → thay bằng khoảng trắng."""
    return re.sub(r'\s+', ' ', re.sub(r'[#|^:\[\]%]', ' ', h)).strip()

def find_heading(stem, cands, files):
    """(heading, token) — heading đầu tiên chứa token (ưu tiên token đứng sớm nhất trong heading)."""
    for c in cands:
        best = None
        for h in headings(stem, files):
            m = re.search(r'(?<!\w)' + re.escape(c) + r'(?!\w)', h)
            if m and (best is None or m.start() < best[0]): best = (m.start(), h)
        if best: return best[1], c
    return None

def step_link(st, files):
    """(doc, heading, token) cho 1 bước: tìm hàm ở doc bên nhận trước, rồi bên gọi; bước của User thì thử cụm chữ (vd 'Mouse Left Pressed')."""
    toks = fn_tokens(st['msg'])
    for stem in ([st['B']] if st['user'] else _dedupe([st['B'], st['A']])):
        r = find_heading(stem, toks, files) if toks else None
        if r: return stem, r[0], r[1]
    if st['user']:
        phrase = re.split(r'[(→]', st['fn'] or '')[0].strip()
        if len(phrase) > 4:
            r = find_heading(st['B'], [phrase], files)
            if r: return st['B'], r[0], r[1]
    return None
