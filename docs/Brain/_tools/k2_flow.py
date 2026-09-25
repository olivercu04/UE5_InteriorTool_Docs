# -*- coding: utf-8 -*-
"""Đọc K2Node export (Ctrl+C trong Blueprint) → (1) dump node/pin/dây, (2) cây exec ▶→ kèm data ●→, (3) Mermaid flowchart.
Dùng (thư mục docs):  python Brain/_tools/k2_flow.py export.txt [--dump] [--mermaid out.mmd]
Flowchart hàm (mức 4) SINH TẠI CHỖ mỗi lần verify K2 — không lưu vào doc (doc giữ bản ▶→). Nguồn đầu tiên: OnMouseReleased 24/09.
Knot (reroute) được xuyên qua, không bao giờ xuất hiện trong kết quả. Không dùng NodePosX/Y để suy luồng.
"""
import re, sys

def parse(text):
    nodes = {}
    for blk in re.findall(r'Begin Object Class=(\S+) Name="([^"]+)"(.*?)\nEnd Object', text, re.S):
        cls, name, body = blk
        cls = cls.split('.')[-1]
        n = {'cls': cls, 'name': name, 'pins': [], 'raw': body}
        for p in re.findall(r'CustomProperties Pin \((.*)\)\s*$', body, re.M):
            pin = {
                'id': (re.search(r'PinId=(\w+)', p) or [None, None])[1],
                'name': (re.search(r'PinName="([^"]*)"', p) or [None, ''])[1],
                'friendly': (re.search(r'PinFriendlyName=(?:NSLOCTEXT\([^,]*,[^,]*,\s*)?"([^"]*)"', p) or [None, ''])[1],
                'dir': 'out' if 'EGPD_Output' in p else 'in',
                'cat': (re.search(r'PinType\.PinCategory="([^"]*)"', p) or [None, ''])[1],
                'sub': (re.search(r'PinType\.PinSubCategoryObject=([^,]*)', p) or [None, ''])[1],
                'default': (re.search(r'DefaultValue="((?:[^"\\]|\\.)*)"', p) or [None, None])[1],
                'defobj': (re.search(r'DefaultObject="([^"]*)"', p) or [None, None])[1],
                'links': re.findall(r'(K2Node_\w+) (\w+)', (re.search(r'LinkedTo=\(([^)]*)\)', p) or [None, ''])[1]),
                'hidden': 'bHidden=True' in p,
            }
            n['pins'].append(pin)
        nodes[name] = n
    return nodes

def title(n):
    b, c = n['raw'], n['cls']
    mem = re.search(r'(?:FunctionReference|VariableReference|DelegateReference)=\(([^)]*)\)', b)
    mname = re.search(r'MemberName="([^"]+)"', mem.group(1)).group(1) if mem and 'MemberName' in mem.group(1) else None
    parent = re.search(r'MemberParent=\S*?\.(\w+)\'', mem.group(1)) if mem else None
    if c == 'K2Node_CustomEvent': return 'Custom Event ' + re.search(r'CustomFunctionName="([^"]+)"', b).group(1)
    if c == 'K2Node_Event': return 'Event ' + (mname or '?')
    if c == 'K2Node_FunctionEntry': return 'Entry'
    if c == 'K2Node_FunctionResult': return 'Return'
    if c == 'K2Node_IfThenElse': return 'Branch'
    if c == 'K2Node_ExecutionSequence': return 'Sequence'
    if c == 'K2Node_VariableGet': return 'GET ' + (mname or '?')
    if c == 'K2Node_VariableSet': return 'SET ' + (mname or '?')
    if c == 'K2Node_GetArrayItem': return 'Get (a copy)'
    if c == 'K2Node_EnumEquality': return '== (enum)'
    if c == 'K2Node_DynamicCast':
        t = re.search(r"TargetType=\S*?\.(\w+)'", b); return 'Cast To ' + (t.group(1) if t else '?')
    if c == 'K2Node_MacroInstance':
        m = re.search(r'MacroGraph=\S*?:(\w+)', b); return m.group(1) if m else 'Macro'
    if c in ('K2Node_CallFunction', 'K2Node_CallArrayFunction', 'K2Node_CommutativeAssociativeBinaryOperator', 'K2Node_PromotableOperator'):
        op = re.search(r'OperationName="([^"]+)"', b)
        return (op.group(1) if op else mname or c) + ('()' if not op else '')
    return c.replace('K2Node_', '') + (' ' + mname if mname else '')

def build(nodes):
    byid = {}
    for n in nodes.values():
        for p in n['pins']: byid[(n['name'], p['id'])] = p
    return byid

def through_knots(nodes, links, seen=None):
    """Trả danh sách (node, pin) đích thật, xuyên Knot."""
    out = []
    for nn, pid in links:
        n = nodes.get(nn)
        if n is None: out.append((nn, pid)); continue
        if n['cls'] == 'K2Node_Knot':
            opin = [p for p in n['pins'] if p['dir'] == 'out']
            out += through_knots(nodes, opin[0]['links'] if opin else [])
        else: out.append((nn, pid))
    return out

def source_of(nodes, byid, n, pin):
    """Nguồn data của 1 pin input: mô tả ngắn (đệ quy qua node pure)."""
    src = through_knots(nodes, pin['links'])
    if not src:
        if pin['defobj']: return pin['defobj'].split('.')[-1]
        if pin['default'] not in (None, ''): return repr(pin['default']) if pin['cat'] in ('string', 'name', 'text') else pin['default']
        return None
    sn, spid = src[0]; s = nodes[sn]; sp = byid.get((sn, spid))
    return expr(nodes, byid, s, sp)

def expr(nodes, byid, n, outpin, depth=0):
    t = title(n)
    if n['cls'] == 'K2Node_Knot':
        ip = [p for p in n['pins'] if p['dir'] == 'in'][0]; return source_of(nodes, byid, n, ip)
    has_exec = any(p['cat'] == 'exec' for p in n['pins'])
    if has_exec or depth > 4:        # node impure → chỉ ghi tên + pin
        return f"{t}.{outpin['name']}" if outpin and outpin['name'] not in ('ReturnValue', 'Output') else t
    args = []
    for p in n['pins']:
        if p['dir'] == 'in' and p['cat'] != 'exec' and not p['hidden'] and p['name'] != 'self':
            v = source_of(nodes, byid, n, p)
            if v is not None: args.append(f"{p['name']}={v}" if len(n['pins']) > 3 else v)
        if p['dir'] == 'in' and p['name'] == 'self' and p['links']:
            args.insert(0, 'Target=' + str(source_of(nodes, byid, n, p)))
    if n['cls'] == 'K2Node_VariableGet':
        tgt = [p for p in n['pins'] if p['name'] == 'self' and p['links']]
        return (source_of(nodes, byid, n, tgt[0]) + '.' if tgt else '') + t[4:]
    if n['cls'] == 'K2Node_EnumEquality' and len(args) == 2: return f"{args[0]} == {args[1]}"
    if n['cls'] == 'K2Node_GetArrayItem' and len(args) == 2:
        a0 = re.sub(r'^GetAllActorsOfClass\(\)\.OutActors$', 'GetAllActorsOfClass', str(args[0])); return f"{a0}[{args[1]}]"
    t = t[:-2] if t.endswith('()') else t
    return f"{t}({', '.join(str(a) for a in args)})" if args else t

def exec_outs(n):
    return [p for p in n['pins'] if p['dir'] == 'out' and p['cat'] == 'exec']

def walk(nodes, byid, start, ind=0, seen=None, lines=None, edges=None):
    seen = seen if seen is not None else set(); lines = lines if lines is not None else []; edges = edges if edges is not None else []
    n = nodes[start]
    if start in seen:
        lines.append('  ' * ind + f'↺ (nhập lại {title(n)} — đã in ở trên)'); return lines, edges
    seen.add(start)
    ins = []
    for p in n['pins']:
        if p['dir'] == 'in' and p['cat'] != 'exec' and not p['hidden']:
            v = source_of(nodes, byid, n, p)
            if v is not None: ins.append(f"{p['name']} ●← {v}")
    lines.append('  ' * ind + f"▶ {title(n)}" + (f"   [{'; '.join(ins)}]" if ins else '') + f"   ⟨{start}⟩")
    outs = exec_outs(n)
    labelled = len(outs) > 1
    for p in outs:
        dst = through_knots(nodes, p['links'])
        lab = {'then': 'True', 'else': 'False'}.get(p['name'], p['name']) if n['cls'] == 'K2Node_IfThenElse' else p['name']
        if not dst:
            if labelled:
                lines.append('  ' * (ind + 1) + f'{lab} → (dead-end)'); edges.append((start, 'DEAD', lab))
            continue
        for dn, _ in dst:
            edges.append((start, dn, lab if labelled else ''))
            if labelled: lines.append('  ' * (ind + 1) + f'{lab} ▶→')
            walk(nodes, byid, dn, ind + (2 if labelled else 0), seen, lines, edges)
    return lines, edges

def label(nodes, byid, x):
    """Nhãn node cho flowchart: tên + input chính (điều kiện Branch, tham số hàm, giá trị SET)."""
    n = nodes[x]; t = title(n)
    ins = [(p, source_of(nodes, byid, n, p)) for p in n['pins'] if p['dir'] == 'in' and p['cat'] != 'exec' and not p['hidden']]
    ins = [(p, v) for p, v in ins if v is not None]
    if n['cls'] == 'K2Node_IfThenElse' and ins: return 'Branch: ' + str(ins[0][1])
    if n['cls'] == 'K2Node_VariableSet' and ins: return f"{t} = {ins[0][1]}"
    if n['cls'] == 'K2Node_VariableSet': return t + ' = mặc định'
    args = [str(v) for p, v in ins if p['name'] != 'self']
    tgt = [str(v) for p, v in ins if p['name'] == 'self']
    return (f"{tgt[0]} → " if tgt else '') + t.rstrip('()') + (f"({', '.join(args)})" if args or t.endswith('()') else '')

def mermaid(nodes, edges, root, byid=None):
    ids = {}
    def nid(x):
        if x not in ids: ids[x] = f'N{len(ids)}'
        return ids[x]
    L = ['flowchart TD']
    used = {root} | {a for a, b, l in edges} | {b for a, b, l in edges if b != 'DEAD'}
    for x in [root] + [x for x in used if x != root]:
        t = (label(nodes, byid, x) if byid else title(nodes[x])).replace('"', "'")
        shape = ('{{"%s"}}' if nodes[x]['cls'] in ('K2Node_IfThenElse', 'K2Node_DynamicCast') else '["%s"]') % t
        L.append(f'  {nid(x)}{shape}')
    for i, (a, b, l) in enumerate(edges):
        if b == 'DEAD': L.append(f'  D{i}(["✖ dead-end"])'); b_id = f'D{i}'
        else: b_id = nid(b)
        L.append(f'  {nid(a)} -->' + (f'|{l}|' if l else '') + f' {b_id}')
    return '\n'.join(L)

if __name__ == '__main__':
    text = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    nodes = parse(text); byid = build(nodes)
    errs = [(n['name'], re.search(r'ErrorMsg="([^"]*)"', n['raw'])) for n in nodes.values() if 'bHasCompilerMessage=True' in n['raw']]
    print('LỖI COMPILE:', [(a, b.group(1) if b else '') for a, b in errs] or 'không có')
    if '--dump' in sys.argv:
        for n in nodes.values():
            print(n['name'], '|', title(n))
            for p in n['pins']:
                if p['links'] or p['default'] or p['defobj']:
                    print('   ', p['dir'], p['cat'], p['name'], '->', p['links'], p['default'] or '', p['defobj'] or '')
    roots = [k for k, n in nodes.items() if n['cls'] in ('K2Node_CustomEvent', 'K2Node_Event', 'K2Node_FunctionEntry')]
    for r in roots:
        lines, edges = walk(nodes, byid, r)
        print('\n'.join(lines))
        if '--mermaid' in sys.argv:
            open(sys.argv[sys.argv.index('--mermaid') + 1], 'w', encoding='utf-8').write(mermaid(nodes, edges, r, byid))
    # node có exec mà không ai tới được
    reach = set()
    for r in roots:
        _, e = walk(nodes, byid, r); reach |= {r} | {a for a, b, l in e} | {b for a, b, l in e}
    orphan = [title(n) + f' ⟨{k}⟩' for k, n in nodes.items() if exec_outs(n) + [p for p in n['pins'] if p['cat'] == 'exec' and p['dir'] == 'in'] and k not in reach and n['cls'] != 'K2Node_Knot']
    if orphan: print('NODE EXEC KHÔNG NỐI TỚI TỪ GỐC:', orphan)
