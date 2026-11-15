# Lesson tables and live Excel practice. Executed after frame.py.
# 1. Solution tables (SOL): clean tables, one card per stage of the work process, numbered as in the topic's flowchart.
#    Rows appear click by click; a click on a figure shows its calculation, in words and numbers, under the cards.
# 2. Live practice (LIVE): the Excel engine of the Excel courses. Students type the numbers and the formulas;
#    "הצעד הבא" fills one row per click with a note, and the check marks each cell.
import html as _html
import json as _json
import fin as _fin
from lib import _TOONS, _face, _t
LET = 'ABCDEFGHIJ'


def C(v='', f='', x='', o=None, hl=()):
    """A cell: value, the cells it is computed from (an Excel-style formula, used only to colour the source cells), explanation, own reveal order."""
    return dict(v=v, f=f, x=x, o=o, hl=tuple(hl))


def RW(k, cells, kind='', o=None):
    """A row: key, cells (first column first), kind ('' / 'h' title / 'prev' from an earlier stage / 'out' does not enter / 'bal' / 'plug' / 'net' / 'help'), reveal order."""
    return dict(k=k, c=cells, kind=kind, o=o)


def AR(fr, to, o, x):
    """An arrow drawn on click from cell fr to cell to ('key:B'), with its explanation."""
    return dict(fr=fr, to=to, o=o, x=x)


def _num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)): return None
    r = round(v)
    s = f'{abs(v):,.2f}' if abs(v - r) > 1e-9 else f'{abs(r):,}'
    return f'({s})' if v < 0 else s


def _orders(rows, arrows):
    seq, raws = 0, []
    for row in rows:
        if row['kind'] == 'h': continue
        cos = [c['o'] for c in row['c'] if isinstance(c, dict) and c.get('o') is not None]
        if row['o'] is None and not cos:
            seq += 1; row['_o'] = seq
        else:
            row['_o'] = row['o'] if row['o'] is not None else min(cos)
        raws.append(row['_o']); raws += cos
    raws += [a['o'] for a in arrows]
    for i, row in enumerate(rows):
        if row['kind'] == 'h':
            nxt = next((x for x in rows[i + 1:] if x['kind'] != 'h'), None)
            row['_o'] = nxt['_o'] if nxt else max(raws)
    return raws


def TBL(cols, rows, arrows=(), n0=1, widths=None, dcol=None, center=False, sid='t', order=None):
    """One clean table. Returns (html, next reveal number, notes for the summary, first reveal number).
    dcol: index of a date column (centred, left to right). center: figures centred (year tables)."""
    rn = {row['k']: i + 2 for i, row in enumerate(rows)}
    sub = lambda s: re.sub(r'#(\w+)#', lambda m: str(rn[m.group(1)]), s)
    wid = {}
    for row in rows:
        if row['kind'] == 'h': continue
        for i, c in enumerate(row['c']):
            t = _num(c['v'] if isinstance(c, dict) else c)
            if t is not None: wid[i] = max(wid.get(i, 0), len(t) + (0 if t.startswith('(') else 1))
    raws = _orders(rows, arrows)
    if order is None:
        order = {o: n0 + i for i, o in enumerate(sorted(set(raws)))}
    nend = max(order.values()) + 1 if order else n0
    notes = []
    rev = MODE == 'deck'
    stp = lambda o: f' data-n="{order[o] * 10}"'

    def cell(c, i, row):
        a = f'{LET[i]}{rn[row["k"]]}'
        if not isinstance(c, dict): c = C(c)
        v, f, x = c['v'], sub(c['f']) if c['f'] else '', sub(c['x']) if c['x'] else ''
        num = _num(v)
        txt = f'<span class="n{" pos" if not str(num).startswith("(") else ""}" style="min-width:{wid.get(i, 1) * .62:.2f}em">{num}</span>' if num is not None else (TX(str(v)) if v != '' else '')
        cls = []
        if num is not None: cls.append('nm')
        if i == dcol and v != '': cls.append('dc')
        attrs = f' data-a="{sid}-{a}"'
        inner = txt
        if x:
            cls.append('ec')
            if f: attrs += f' data-f="{_html.escape(re.sub(r"([A-J])(\d+)", lambda m: sid + "-" + m.group(0), f))}"'
            if c.get('hl'): attrs += f' data-hl="{" ".join(c["hl"])}"'
            lab = re.sub('<[^>]+>', '', str(row['c'][0] if not isinstance(row['c'][0], dict) else row['c'][0]['v']))
            if dcol == 0 and len(row['c']) > 1: lab = re.sub('<[^>]+>', '', str(row['c'][1] if not isinstance(row['c'][1], dict) else row['c'][1]['v'])) or lab
            head = f'{lab}' + (f' · {cols[i]}' if len(cols) > 2 and cols[i] and i > (1 if dcol == 0 else 0) else '')
            notes.append((head, x))
            inner = txt + f'<div class="xx"><b>{TX(head)}:</b> {TX(x)}</div>'
        if rev and c.get('o') is not None:
            inner = f'<span class="st cs{" auto" if x else ""}"{stp(c["o"])}>{inner}</span>'
        return f'<td class="{" ".join(cls)}"{attrs}>{inner}</td>', bool(x) and c.get('o') is None

    head = '<tr class="sgh">' + ''.join(f'<th{" class=dc" if i == dcol else ""}>{TX(c)}</th>' for i, c in enumerate(cols)) + '</tr>'
    body = ''
    for row in rows:
        st = 'st ' if rev else ''
        if row['kind'] == 'h':
            body += f'<tr class="{st}sgsec"{stp(row["_o"]) if rev else ""}><td colspan="{len(cols)}">{TX(row["c"][0])}</td></tr>'
            continue
        cells = list(row['c']) + [''] * (len(cols) - len(row['c']))
        tds, auto = '', False
        for i, c in enumerate(cells):
            h, ex = cell(c, i, row)
            if ex and not auto and rev:
                h = h.replace('class="', 'class="auto ', 1); auto = True
            tds += h
        body += f'<tr class="{st}{row["kind"]}"{stp(row["_o"]) if rev else ""}>{tds}</tr>'
    arr = ''
    for a in arrows:
        fr = f'{sid}-{a["fr"].split(":")[1]}{rn[a["fr"].split(":")[0]]}'
        to = f'{sid}-{a["to"].split(":")[1]}{rn[a["to"].split(":")[0]]}'
        notes.append(('המעבר', a['x']))
        if rev:
            arr += f'<div class="sga st auto"{stp(a["o"])} data-from="{fr}" data-to="{to}"><div class="xx">{TX(a["x"])}</div></div>'
    cg = '<colgroup>' + ''.join(f'<col style="width:{w}%">' for w in widths) + '</colgroup>' if widths else ''
    first = min(order[o] for o in raws) if raws else n0
    return f'<div class="sgs"><table class="sg{" ctr" if center else ""}">{cg}{head}{body}</table>{arr}</div>', nend, notes, first


def STG(num, title, cols, rows, arrows=(), widths=None, dcol=None, center=False, fn=None):
    """One stage of the work: its number in the topic's flowchart, a title, and its table."""
    return dict(num=num, t=title, cols=cols, rows=rows, arrows=arrows, widths=widths, dcol=dcol, center=center, fn=fn)


_SG = [0]


def SOL(stages, n0=1, flow=None, after=(), layout='', tip=None, side_panel=False, parts=False, joint=False):
    """The solution column: the flowchart strip, a card per stage, and the explanation panel. Returns (html, next n).
    flow: the names of the topic's steps; the steps of these stages are marked. layout: '' stacked, 'two' side by side."""
    n, cards, allnotes = n0, '', []
    jo = None
    if joint:
        allr = sorted(set(o for sg in stages if not sg.get('fn') for o in _orders(sg['rows'], sg['arrows'])))
        jo = {o: n0 + i for i, o in enumerate(allr)}
    for sg in stages:
        _SG[0] += 1
        if sg.get('fn'):
            h, n2, notes = sg['fn'](n); first = n
        else:
            h, n2, notes, first = TBL(sg['cols'], sg['rows'], sg['arrows'], n, sg['widths'], sg['dcol'], sg['center'], sid=f'g{_SG[0]}', order=jo)
            if sg.get('tcls'): h = h.replace('<table class="sg', f'<table class="sg {sg["tcls"]}', 1)
            if jo: n2 = max(jo.values()) + 1
        lab = f'<span class="sgn">{"שלב " + str(sg["num"]) if isinstance(sg["num"], int) else sg["num"]}</span>' if sg['num'] else ''
        card = f'<div class="sgc"><div class="sgt">{lab}<label>{TX(sg["t"])}</label></div>{h}'
        if MODE == 'pdf' and notes:
            card += '<ol class="xln">' + ''.join(f'<li><b>{TX(a)}:</b> {TX(x)}</li>' for a, x in notes) + '</ol>'
        card += '</div>'
        cards += (f'<div class="st sgcw" data-n="{first * 10}">{card}</div>' if MODE == 'deck' else card)
        n = n2
    strip = ''
    if flow:
        here = set()
        for sg in stages:
            if isinstance(sg['num'], int): here.add(sg['num'])
            elif sg['num']:
                ns = [int(v) for v in re.findall(r'\d+', sg['num'])]
                here.update(range(ns[0], ns[-1] + 1) if 'עד' in sg['num'] else ns)
        if not here and any(sg['num'] == 'התשובות' for sg in stages): here, lo = set(), len(flow) + 1
        elif not here: here = set(range(1, len(flow) + 1)); lo = 1
        else: lo = min(here)
        strip = '<div class="sgf">' + ''.join(
            (f'<span class="on"><b>{i + 1}</b><label>{TX(t)}</label></span>' if i + 1 in here and len(here) <= 2 else f'<span class="on" title="{t}"><b>{i + 1}</b></span>' if i + 1 in here else f'<span class="{"done" if i + 1 < lo else ""}" title="{t}"><b>{i + 1}</b></span>') for i, t in enumerate(flow)) + '</div>'
    aft = ''
    for kd, t in after:
        if MODE == 'deck':
            aft += ST(n, '<b>טיפ:</b> ' + TX(t), cls='band dg') if kd == 'tip' else (PUN(t, n) if kd == 'pun' else ST(n, TX(t), cls='band note'))
            n += 1
        else:
            aft += BAND('dg', '<b>טיפ:</b> ' + t) if kd == 'tip' else (PUN(t) if kd == 'pun' else BAND('note', t))
    panel = f'<div class="sgp">{TX(tip or "לחצו על מספר מסומן בטבלה: כאן יופיע החישוב שלו, במילים ובמספרים.")}</div>' if MODE == 'deck' else ''
    if parts:
        return f'<div class="sgw{" " + layout if layout else ""}">{strip}<div class="sgcs">{cards}</div></div>', panel, aft
    if 'side' in layout:
        return f'<div class="sgw xsw {layout}"><div class="xsc">{strip}<div class="sgcs">{cards}</div>{aft}</div>{panel}</div>', n
    if side_panel:
        return f'<div class="sgw{" " + layout if layout else ""}">{strip}<div class="sgcs">{cards}</div>{aft}</div>', n, panel
    return f'<div class="sgw{" " + layout if layout else ""}">{strip}<div class="sgcs">{cards}</div>{panel}{aft}</div>', n


def XS(cols, rows, arrows=(), n=1, widths=None, dcol=None, center=False, title=None, num=None):
    """A single table on a concept slide, revealed from step n, with its explanation panel."""
    return SOL([STG(num, title or '', cols, rows, arrows, widths, dcol, center)], n)[0] if title else _xs_plain(cols, rows, arrows, n, widths, dcol, center)


def _xs_plain(cols, rows, arrows, n, widths, dcol, center):
    _SG[0] += 1
    h, _, notes, _ = TBL(cols, rows, arrows, n, widths, dcol, center, sid=f'g{_SG[0]}')
    if MODE == 'pdf':
        return '<div class="sgw">' + h + ('<ol class="xln">' + ''.join(f'<li><b>{TX(a)}:</b> {TX(x)}</li>' for a, x in notes) + '</ol>' if notes else '') + '</div>'
    return f'<div class="sgw xsw"><div class="xsc">{h}</div><div class="sgp">{TX("לחצו על מספר מסומן בטבלה: כאן יופיע החישוב שלו, במילים ובמספרים.")}</div></div>'


KIND = {'together': 'מסבירים יחד', 'alone': 'נסו לבד', 'class': 'פתרנו בשיעור', 'excel': 'עכשיו אתם, באקסל', 'sol': 'הפתרון, שלב אחר שלב'}


def _qlines(p):
    """A story paragraph, one data item per line: numbered items split at (1), (2)..., otherwise one sentence per line."""
    if re.search(r'\(\d+\)', p):
        parts = [s.strip() for s in re.split(r'\s*(?=\(\d+\))', p) if s.strip()]
    else:
        parts, cur = [], ''
        for tok in re.split(r'(?<=[.?!])\s+', p):
            cur = (cur + ' ' + tok).strip() if cur else tok
            last = re.sub(r'<[^>]+>', '', cur).rstrip('.?!:').split()[-1:] or ['']
            # a single-letter initial (צחי פ.) or a number does not end a sentence
            if len(last[0]) > 1 and not re.match(r'^[\d(]', tok.lstrip()[:1] or 'x') or tok.endswith(('?', '!')):
                parts.append(cur); cur = ''
        if cur: parts.append(cur)
    out = ''
    for s in parts:
        m = re.match(r'\((\d+)\)\s*(.*)', s, re.S)
        if m: out += f'<p class="qi qn"><b class="qno"><span class="n">{m.group(1)}</span></b>{TX(m.group(2))}</p>'
        elif re.fullmatch(r'<b>[^<]*</b>:?', s): out += f'<p class="qh">{TX(s)}</p>'
        else: out += f'<p class="qi">{TX(s)}</p>'
    return out


def QCARD(kind, story, asks, cur=None, data='', wide=False):
    """wide: a question above a wide table; the data table sits beside the story, so the solution gets the height."""
    lab = KIND[kind]
    ah = ''.join(f'<p class="{"cur" if cur and l in cur else ""}"><b>{l}.</b> {TX(t)}</p>' if l else f'<p class="{"cur" if cur else ""}">{TX(t)}</p>' for l, t in asks)
    st = '<div class="ql">' + ''.join(_qlines(p) for p in story) + '</div>'
    if wide and data:
        return (f'<div class="card qstem xq sm qw"><div class="qa"><span class="kd {kind}">{lab}</span>{st}<div class="asks"><b>נדרש:</b>{ah}</div></div><div class="qd">{data}</div></div>')
    return (f'<div class="card qstem xq sm"><span class="kd {kind}">{lab}</span>' + st + data
            + f'<div class="asks"><b>נדרש:</b>{ah}</div></div>')


def XQ(key, title, kind, story, asks, slides, data='', stack=False, flow=None, live=None):
    """A worked exercise. slides: dict(cur=letters of the requirement in focus, stages=[STG...], after=[...], layout).
    kind 'together' / 'class': the solution slides, then (if live) the same question in a live sheet.
    kind 'alone': the live sheet first, then the solution slides."""
    NX[0] += 1
    lab = KIND[kind]
    sid, k = 'x-' + key, f'חלק {CUR[0]} · {lab}'
    if MODE == 'pdf':
        b = QCARD(kind, story, asks, None, data)
        for sl in slides:
            b += SOL(sl['stages'], 1, None, sl.get('after', ()), joint=sl.get('joint', False))[0]
        S(sid, f'{lab}: {title}', f'{lab}: {title}', b, kind='q')
        return
    lives = live if isinstance(live, list) else ([live] if live else [])
    if kind == 'alone':
        for j, cfg in enumerate(lives):
            LIVEQ(sid + ('' if not j else f'l{j + 1}'), title + ('' if len(lives) == 1 else f' ({j + 1} מתוך {len(lives)})'), 'alone', story, asks, data, cfg, stack=stack)
    for i, sl in enumerate(slides):
        # stacked: the tip becomes the first text of the explanation panel beside the question
        tipx = ' '.join(t for kd, t in sl.get('after', ())) if stack else None
        h, pan, aft = SOL(sl['stages'], 1, flow, () if stack else sl.get('after', ()), sl.get('layout', ''), parts=True, joint=sl.get('joint', False),
                          tip=('<b>טיפ:</b> ' + tipx + ' ' + 'לחצו על מספר מסומן: כאן יופיע החישוב שלו.') if tipx else None)
        tag = '' if len(slides) == 1 else f' ({i + 1} מתוך {len(slides)})'
        kd = 'sol' if kind == 'alone' else kind
        head = f'{KIND[kd]}: {title}{tag}'
        q = QCARD(kd, story, asks, sl.get('cur'), data)
        # the explanation panel and the tips sit beside the question, where the slide has room
        body = (f'<div class="xstack"><div class="qtop">{q}<div class="qside">{pan}{aft}</div></div>{h}</div>' if stack
                else f'<div class="xg"><div class="pqq">{q}{pan}{aft}</div><div class="pqa">{h}</div></div>')
        S(sid + ('s' if kind == 'alone' else '') + ('' if not i else f'c{i + 1}'), head, head, body, kick=f'חלק {CUR[0]} · {KIND[kd]}', cls='qslide')
    # the live sheet keeps only the requirements its solution slides dealt with
    curs = ''.join(sl.get('cur', '') for sl in slides)
    lasks = [a for a in asks if not a[0] or a[0] in curs] or asks
    if kind != 'alone':
        for j, cfg in enumerate(lives):
            LIVEQ(sid + 'x' + ('' if not j else str(j + 1)), title, 'excel', story, lasks, data, cfg, stack=stack)


# ---------------------------------------------------------------- live Excel practice
def LR(k, cells, note='', kind='', ord=None, ords=None, notes=None):
    """A row of a live sheet. cells: column A first. A number is typed by the student (a figure of the question);
    a formula '=...' or ('=...', expected value) is written by the student; any other text is a fixed label. kind 'h': a title row."""
    return dict(k=k, c=cells, note=note, kind=kind, ord=ord, ords=ords or {}, notes=notes or {})


class P(float):
    """A rate the student types with the percent sign, as in Excel."""


def LIVE(cols, rows, widths, hints=None, remind=None, fmt='acc0', center=(), done=''):
    """The spec of a live sheet: header row 1, then the rows. Returns the engine's config, checked in Python."""
    rn = {r['k']: i + 2 for i, r in enumerate(rows)}
    sub = lambda s: re.sub(r'#(\w+)#', lambda m: str(rn[m.group(1)]), s)
    data, sol, steps, expect, fm, sty = {}, {}, [], {}, {}, {}
    for i, c in enumerate(cols):
        data[f'{LET[i]}1'] = f'שנת {c}' if re.fullmatch(r'\d{4}', str(c)) else c   # a bare year would be read as a number
        sty[f'{LET[i]}1'] = dict(b=True, al='center', fill='#1d6f42')
    groups = []
    for ri, r in enumerate(rows):
        n = rn[r['k']]
        cells = {}
        for i, c in enumerate(r['c']):
            a = f'{LET[i]}{n}'
            if c is None or c == '': continue
            if isinstance(c, tuple):
                f, want = sub(c[0]), c[1]
                sol[a] = f; cells[a] = f; expect[a] = want
            elif isinstance(c, str) and c.startswith('='):
                sol[a] = sub(c); cells[a] = sol[a]
            elif isinstance(c, P):
                sol[a] = f'{round(float(c) * 100, 10):g}%'; cells[a] = sol[a]; expect[a] = float(c); fm[a] = 'pct0'
            elif isinstance(c, (int, float)) and not isinstance(c, bool):
                sol[a] = f'{c:.15g}'; cells[a] = sol[a]; expect[a] = c
            else:
                data[a] = c
            if a in sol and a not in fm:
                w_ = expect.get(a)
                fm[a] = 'acc2' if isinstance(w_, float) and abs(w_ - round(w_)) > 1e-9 else fmt
            if LET[i] in center: sty.setdefault(a, {})['al'] = 'center'
        if r['kind'] == 'h':
            for i in range(len(cols)):
                sty[f'{LET[i]}{n}'] = dict(b=True, fill='#e8f1ea')
        elif r['kind'] in ('bal', 'net'):
            for i in range(len(cols)):
                sty.setdefault(f'{LET[i]}{n}', {})['b'] = True
        if cells:
            base = r['ord'] if r.get('ord') is not None else (ri + 1) * 10
            own = {a: v for a, v in cells.items() if a[0] not in r['ords']}
            if own:
                note = r['note'] or ('מקלידים את נתוני השאלה בשורה הזו.' if all(not str(v).startswith('=') for v in own.values()) else '')
                groups.append((base, own, note))
            for col, o in r['ords'].items():
                one = {a: v for a, v in cells.items() if a[0] == col}
                if one: groups.append((o, one, r['notes'].get(col, '')))
    for o, cells, note in sorted(groups, key=lambda g: g[0]):
        first = next((a for a in cells if str(cells[a]).startswith('=')), next(iter(cells)))
        steps.append(dict(cells=cells, note=TX(note), sel=first))
    vals, _ = _fin.evaluate({**data, **sol})
    for a, want in expect.items():
        got = vals[a]
        assert isinstance(got, (int, float)) and abs(got - want) <= 1e-6 * max(1, abs(want)), ('live sheet', a, sol[a], got, want)
    vin = [a for a in sol if not str(sol[a]).startswith('=')]
    targets = list(sol)
    nrow = len(rows) + 1
    w = list(widths) + [80] * 2
    return dict(rows=nrow + 10, cols=len(cols) + 2, widths=w, data=data, targets=targets, solution=sol, headRows=[1], inputs=[], fmt=fm, solFmt=fm,
                hints=[TX(x) for x in (hints or ['קראו את כותרת השורה, כתבו במילים מה מחשבים, ורק אז כתבו נוסחה שמפנה לתאים.'])],
                partial=vin + [a for a in targets if a not in vin][:1], values=False, done=TX(done or 'זה הפתרון המלא. השוו אותו לטבלאות הפתרון.'),
                maxh=2000, vin=vin, steps=steps, sty=sty, **({'remind': TX(remind)} if remind else {}))


NLIVE = [0]


def LIVEQ(sid, title, kind, story, asks, data, cfg, stack=False):
    """A slide: the question beside a live sheet."""
    if MODE == 'pdf': return
    NLIVE[0] += 1
    lab = KIND[kind]
    q = QCARD(kind, story, asks, None, data)
    task = 'נתונים בתאים, ונוסחאות שמפנות אליהם. ״הצעד הבא״ ממלא שורה בכל לחיצה.'
    cj = _html.escape(_json.dumps(cfg, ensure_ascii=False), quote=True)
    w = sum(cfg['widths'][:-2]) + 34 + 24
    stack = stack and w > 640   # a narrow sheet sits beside the question even when the solution slides are stacked
    body = (f'<div class="act xlq qx{" stk" if stack else (" wide" if sum(cfg["widths"][:-2]) > 520 else "")}" id="{sid}-x" data-cfg="{cj}"' + ('' if stack else f' style="grid-template-columns:minmax(0,1fr) {w}px"') + f'><div class="qr">{q}<div class="tasktxt sm">{TX(task)}</div><div class="xfbs"></div></div>'
            f'<div class="xw"><div class="sheet"></div></div></div>')
    S(sid, f'{lab}: {title}', f'{lab}: {title}', body, kick=f'חלק {CUR[0]} · {lab}', cls='qslide xslide')


def WF(steps, n=1):
    """The work process as a numbered flowchart, one step per click: (title, what to do, small example)."""
    out = ''
    for i, (t, d, ex) in enumerate(steps):
        if i: out += ST(n + i, '<span class="wfa">←</span>', cls='wfx')
        out += ST(n + i, f'<span class="wfn">{i + 1}</span><b>{TX(t)}</b><span>{TX(d)}</span>' + (f'<em>{TX(ex)}</em>' if ex else ''), cls='wfs')
    return f'<div class="wf n{len(steps)}">{out}</div>'


# ---------------------------------------------------------------- memes: an original cartoon with a caption above and below
_TOONS.update({
 # a customer running away with the money bag
 'runner': ''.join([f'<path d="M24 {y} h{w}" stroke="#8a93aa" stroke-width="4" stroke-linecap="round"/>' for y, w in ((70, 34), (90, 48), (110, 30))])
           + '<path d="M120 80 L112 118 L92 150 M112 118 L138 148" stroke="#16213a" stroke-width="6" fill="none" stroke-linecap="round"/>'
           + '<path d="M118 90 L84 102 M118 90 L156 98" stroke="#16213a" stroke-width="6" fill="none" stroke-linecap="round"/>'
           + _face(124, 56, 24, 'smile') + '<circle cx="176" cy="104" r="26" fill="#e8960c" stroke="#16213a" stroke-width="3"/>'
           + '<path d="M164 80 l12 -8 l12 8" fill="#e8960c" stroke="#16213a" stroke-width="3"/>' + _t(176, 113, '₪', 26, '#16213a', 800),
 # yesterday's milk leaves first
 'milk': '<path d="M48 54 l12 -16 h40 l12 16 v94 h-64z" fill="#fff" stroke="#16213a" stroke-width="3"/>' + _face(80, 96, 20, 'sad', '#dff5f2') + _t(80, 140, 'אתמול', 15, '#b3262f', 800)
         + '<path d="M140 54 l12 -16 h40 l12 16 v94 h-64z" fill="#fff" stroke="#16213a" stroke-width="3"/>' + _face(172, 96, 20, 'smile', '#dff5f2') + _t(172, 140, 'היום', 15, '#167a43', 800)
         + '<path d="M60 26 C 40 10, 20 20, 18 44" stroke="#ff6a4d" stroke-width="4" fill="none" marker-end="url(#mh)"/><defs><marker id="mh" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8z" fill="#ff6a4d"/></marker></defs>',
 # counting boxes in the warehouse, and missing some
 'boxes': ''.join(f'<rect x="{x}" y="{y}" width="46" height="36" rx="3" fill="#ffe0b3" stroke="#16213a" stroke-width="2.5"/>' for x, y in ((120, 118), (168, 118), (144, 82), (192, 82), (168, 46)))
          + _face(64, 84, 28, 'flat') + '<circle cx="96" cy="112" r="14" fill="none" stroke="#16213a" stroke-width="4"/><path d="M106 122 l14 14" stroke="#16213a" stroke-width="5"/>'
          + _t(64, 34, '120?', 22, '#b3262f', 800),
 # the market goes up and down every December
 'coaster': '<path d="M14 140 L60 90 L96 116 L140 52 L176 96 L236 40" stroke="#1b2d55" stroke-width="5" fill="none" stroke-linejoin="round"/>'
            + '<circle cx="140" cy="52" r="8" fill="#25a65f"/><circle cx="96" cy="116" r="8" fill="#e0454f"/>' + _face(140, 22, 18, 'smile') + _t(206, 140, 'דצמבר', 18, '#2a3858', 800),
})


def MEME(name, top, bottom):
    return f'<div class="meme"><div class="mtop">{TX(top)}</div><svg class="mimg" dir="ltr" viewBox="0 0 250 170" role="img">{_TOONS[name]}</svg><div class="mbot">{TX(bottom)}</div></div>'


def MEMES(sid, title, name, top, bottom, lesson):
    """A meme slide: the cartoon pops, then the one-line lesson."""
    S(sid, title, title, '<div class="memer">' + ST(1, MEME(name, top, bottom), cls='mpop') + ST(2, '<b>' + TX('בשורה אחת: ') + '</b>' + TX(lesson), cls='mles') + '</div>', kick=f'חלק {CUR[0]} · רגע של הומור')


def BYCOL(rows, start=0):
    """Year columns revealed one year at a time: each figure of column j gets the order 100 j + its row index."""
    out = []
    for ri, row in enumerate(rows):
        if row['kind'] == 'h':
            out.append(row); continue
        cells = []
        for j, c in enumerate(row['c']):
            if j == 0 or c == '':
                cells.append(c); continue
            c = c if isinstance(c, dict) else C(c)
            if c['o'] is None: c = dict(c, o=start + 100 * j + ri)
            cells.append(c)
        out.append(dict(row, c=cells))
    return out



def FIFOVIS(lots, sold, back, back_lab='חזרה לשלב 1'):
    """Stage 2 of FIFO as a picture: the units left (from stage 1), the lots in time order, the sold units taken from the old side,
    and the units left counted from the newest lot backwards, each with its calculation.
    lots: (name, date, units, unit cost), oldest first. sold: units sold. back: the slide of stage 1."""
    left, taken = sold, []
    for nm, d, q, c in lots:
        t = min(q, left); taken.append(t); left -= t
    rem = [q - t for (nm, d, q, c), t in zip(lots, taken)]
    tu = sum(q for _, _, q, _ in lots); cu = tu - sold
    picks = [(i, rem[i]) for i in range(len(lots) - 1, -1, -1) if rem[i]]
    total = sum(r * lots[i][3] for i, r in picks)
    notes = [('נשארו', f'{tu:,} יחידות עמדו למכירה, ונמכרו {sold:,}. נשארו ${tu:,} - {sold:,} = {cu:,}$ יחידות.'),
             ('נמכרו', 'ב-FIFO היחידות הישנות נמכרות ראשונות: קודם כל מלאי הפתיחה, אחר כך הרכישה הבאה, וכן הלאה.'),
             ('מה נשאר', 'מה שלא נמכר הוא החדש ביותר. לכן כדי לגלות מה נשאר, מתחילים מן הרכישה האחרונה וסופרים אחורה, עד שמגיעים למספר היחידות שנשארו.')]
    notes += [(f'מן {lots[i][0]} {lots[i][1]}', f'${r:,} × {lots[i][3]} = {r * lots[i][3]:,}$.') for i, r in picks]
    notes.append(('עלות מלאי הסגירה', ' + '.join(f'{r * lots[i][3]:,}' for i, r in picks) + f' = {total:,}'))

    def fn(n0):
        if MODE == 'pdf':
            rows = ''.join(f'<li>{TX(a)}: {TX(b)}</li>' for a, b in notes)
            return f'<ol class="xln">{rows}</ol>', n0, []
        st = lambda k, cls, inner, x='': (f'<div class="st {cls}{" ec auto" if x else ""}" data-n="{(n0 + k) * 10}">{inner}' + (f'<div class="xx"><b>{TX(x[0])}:</b> {TX(x[1])}</div>' if x else '') + '</div>')
        h = '<div class="fv">'
        h += '<div class="fvtop">' + st(0, 'fvs', f'<b>{TX(f"נשארו {cu:,} יחידות")}</b> {TX("(שלב 1). מאילו רכישות הן?")}', notes[0]) + (f'<button class="lnk" data-go="{back}">{TX(back_lab)}</button>' if MODE == 'deck' else '') + '</div>'
        boxes = ''
        for i, (nm, d, q, c) in enumerate(lots):
            seg = (f'<i class="st fvsold" data-n="{(n0 + 2) * 10}" style="flex:{taken[i]}"></i>' if taken[i] else '') + (f'<i class="st fvrem" data-n="{(n0 + 3) * 10}" style="flex:{rem[i]}"></i>' if rem[i] else '')
            boxes += (f'<div class="fvl" style="flex:{q} 1 0"><div class="fvh"><b>{TX(nm)} <span class="n">{d}</span></b><br><span class="n">{q:,}</span> {TX("יח׳ ×")} <span class="n">{c}</span></div>'
                      f'<div class="fvbar">{seg}</div></div>')
        chips = ''.join(st(4 + j, 'fvchip', f'{TX("מן " + lots[i][0] + " " + lots[i][1] + ":")} <span class="n">{r:,}</span> × <span class="n">{lots[i][3]}</span> = <b class="n">{r * lots[i][3]:,}</b>', notes[3 + j]) for j, (i, r) in enumerate(picks))
        h += st(1, 'fvlots', f'<div class="fvtime"><span>{TX("ישן")}</span><i></i><span>{TX("חדש")}</span></div><div class="fvrow">{boxes}</div>')
        h += f'<div class="fvchips">{chips}</div>'
        h += st(2, 'fvcap sold', f'<i></i><span>{TX(f"נמכרו {sold:,}: הישנות יוצאות ראשונות")}</span>', notes[1])
        h += st(3, 'fvcap rem', f'<span>{TX(f"נשארו {cu:,}: החדשות. לכן סופרים מן הסוף אחורה")}</span><i></i>', notes[2])
        h += st(4 + len(picks), 'fvtot', TX(f'עלות מלאי הסגירה ב-FIFO: ' + ' + '.join(f'{r * lots[i][3]:,}' for i, r in picks) + f' = <b>{total:,}</b> ש״ח'), notes[-1])
        return h + '</div>', n0 + 5 + len(picks), []
    return STG(2, 'עלות מלאי הסגירה ב-FIFO: מאילו רכישות נשארו היחידות?', [], [], fn=fn)



def MOVES(rows, cls='sm'):
    """The movements table of an inventory question: date, movement, units, unit cost or price. Each row carries its date as a key,
    and a hidden product (units × unit figure) that appears when a figure of the solution that uses this row is clicked."""
    h = '<tr><th>תאריך</th><th>תנועה</th><th>יחידות</th><th>ש״ח ליחידה</th><th class="dtx"></th></tr>'
    b = ''
    for d, kind, q, lab, p in rows:
        b += (f'<tr data-k="{d}"><td><span class="n">{d}</span></td><td>{TX(kind)}</td><td><span class="n">{q:,}</span></td><td>{TX(lab)} <span class="n">{p}</span></td>'
              f'<td class="dtx"><span class="n">{q:,}</span> × <span class="n">{p}</span> = <b class="n">{q * p:,}</b></td></tr>')
    return f'<table class="dt {cls} mv">{h}{b}</table>'


# ---------------------------------------------------------------- shared small helpers (lesson 2 defines the same)
def DT(head, rows, cls=''):
    h = ''.join(f'<th>{TX(x)}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{TX(str(c))}</td>' for c in r) + '</tr>' for r in rows)
    return f'<table class="dt {cls}"><tr>{h}</tr>{b}</table>'


def LINK(go, text):
    return f'<button class="lnk" data-go="{go}">{TX(text)}</button>' if MODE == 'deck' else f'<span class="lnk">{TX(text)}</span>'


def BADGE():
    return '<span class="kd class">' + TX('פתרנו בשיעור') + '</span>'


def f0(v):
    return f'{v:,.0f}'


def f2(v):
    s = f'{v:,.2f}'
    return s[:-3] if s.endswith('.00') else s


def MONTHS(start, end):
    """Months from the first day of start (y, m) to the first day of end (y, m)."""
    return (end[0] - start[0]) * 12 + end[1] - start[1]


def TLINE(start, end, annual, end_lab, title, num=None, back=None, back_lab=''):
    """Depreciation along time: one box per calendar year from the date the asset is available (start, first of month)
    to end (first of month; 31.12.Y is (Y + 1, 1)); each box shows its months and its depreciation, revealed year by year."""
    yrs = []
    for y in range(start[0], end[0] + 1):
        a = start[1] if y == start[0] else 1
        b = end[1] if y == end[0] else 13
        if b > a: yrs.append((y, b - a))
    tot = sum(m for _, m in yrs)
    notes = [(f'{y}', f'{m} חודשים: ${f2(annual)} × {m} ÷ 12 = {f2(annual * m / 12)}$.' + (' שנה ראשונה: רק מן המועד שבו הנכס זמין לשימוש.' if i == 0 and m < 12 else '')) for i, (y, m) in enumerate(yrs)]
    whole, rest = divmod(tot, 12)
    span = (f'{whole} שנים' if whole != 1 else 'שנה אחת') + (f' ו-{rest} חודשים' if rest else '')
    notes.append(('סך הכול', f'{tot} חודשים, כלומר {span}: ${f2(annual)} × {tot} ÷ 12 = {f2(annual * tot / 12)}$.'))

    def fn(n0):
        if MODE == 'pdf':
            return '<ol class="xln">' + ''.join(f'<li>{TX(a)}: {TX(b)}</li>' for a, b in notes) + '</ol>', n0, []
        st = lambda k, cls, inner, x=None: (f'<div class="st {cls}{" ec auto" if x else ""}" data-n="{(n0 + k) * 10}">{inner}'
                                            + (f'<div class="xx"><b>{TX(x[0])}:</b> {TX(x[1])}</div>' if x else '') + '</div>')
        h = '<div class="dtl">'
        top = f'<b>{TX("פחת לשנה מלאה: " + f2(annual) + " ש״ח")}</b> {TX("מתחילים מן המועד שבו הנכס זמין לשימוש, ולא מיום הרכישה.")}'
        h += '<div class="fvtop">' + st(0, 'fvs', top) + (f'<button class="lnk" data-go="{back}">{TX(back_lab)}</button>' if back and MODE == 'deck' else '') + '</div>'
        boxes = ''.join(st(1 + i, 'tly', f'<b class="n">{y}</b><span>{TX(f"{m} חודשים")}</span><em>{TX(f2(annual * m / 12))}</em>', notes[i]) .replace('class="st tly', f'style="flex:{m} 1 0" class="st tly') for i, (y, m) in enumerate(yrs))
        h += f'<div class="tltime"><span>{TX("זמין לשימוש")}</span><i></i><span>{TX(end_lab)}</span></div><div class="tlrow">{boxes}</div>'
        h += st(1 + len(yrs), 'fvtot', TX(f'{tot} חודשים ({span}): פחת נצבר <b>{f2(annual * tot / 12)}</b> ש״ח'), notes[-1])
        return h + '</div>', n0 + 2 + len(yrs), []
    return STG(num, title, [], [], fn=fn)
