# Excel-like sheets for worked exercises: rows revealed click by click, and a click on a cell shows its formula and the arithmetic under the sheet.
# Practice sheets: the computed cells are empty boxes; a click gives a hint, and the calculation only on request. Executed after frame.py.
import html as _html
from lib import _TOONS, _face, _t
LET = 'ABCDEFGHIJ'


def C(v='', f='', x='', h='', o=None):
    """A cell: value, Excel formula, explanation (the arithmetic, in words and numbers), hint for practice, own reveal order."""
    return dict(v=v, f=f, x=x, h=h, o=o)


def RW(k, cells, kind='', o=None):
    """A row: key, cells (column A first), kind ('' / 'h' title / 'prev' last year / 'out' does not enter / 'bal' / 'plug' / 'net' / 'help'), reveal order."""
    return dict(k=k, c=cells, kind=kind, o=o)


def AR(fr, to, o, x):
    """An arrow drawn on click from cell fr to cell to ('key:B'), with its explanation."""
    return dict(fr=fr, to=to, o=o, x=x)


def _num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)): return None
    r = round(v)
    s = f'{abs(v):,.2f}' if abs(v - r) > 1e-9 else f'{abs(r):,}'
    return f'({s})' if v < 0 else s


def XL(cols, rows, arrows=(), n0=1, practice=False, widths=None):
    """Returns (html, next reveal number). Formulas and explanations may name a row as #key#; it becomes its row number."""
    rn = {row['k']: i + 2 for i, row in enumerate(rows)}
    sub = lambda s: re.sub(r'#(\w+)#', lambda m: str(rn[m.group(1)]), s)
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
    order = {o: n0 + i for i, o in enumerate(sorted(set(raws)))}
    nend = n0 + len(order)
    notes = []
    stp = lambda o: f' data-n="{order[o] * 10}"'
    rev = MODE == 'deck' and not practice

    def cell(c, col, row):
        a = f'{col}{rn[row["k"]]}'
        if not isinstance(c, dict): c = C(c)
        v, f, x = c['v'], sub(c['f']) if c['f'] else '', sub(c['x']) if c['x'] else ''
        if f and not x: x = 'מחושב מן התאים המסומנים בצבע, לפי הנוסחה שבשורת הנוסחאות.'
        num = _num(v)
        txt = f'<span class="n">{num}</span>' if num is not None else (TX(str(v)) if v != '' else '')
        cls = ['nm'] if num is not None else []
        attrs = f' data-a="{a}"'
        inner = txt
        if x or f:
            cls.append('xc')
            attrs += f' data-f="{_html.escape(f)}"'
            notes.append((a, f, x))
            inner = txt + f'<div class="xx">{TX(x)}</div>'
            if practice and num is not None and MODE == 'deck':
                cls.append('pr')
                hint = c['h'] or 'התאים הצבעוניים בגיליון הם חומרי הגלם של התא הזה. בנו ממנו את החישוב.'
                inner = (f'<input class="xin" dir="ltr" data-ans="{v}" data-fmt="{num}" inputmode="decimal" autocomplete="off" spellcheck="false" aria-label="{a}">'
                         f'<div class="xx">{TX(x)}</div><div class="xh2">{TX(hint)}</div>')
        if rev and c.get('o') is not None:
            inner = f'<span class="st cs{" auto" if x or f else ""}"{stp(c["o"])}>{inner}</span>'
        return f'<td class="{" ".join(cls)}"{attrs}>{inner}</td>', bool(x or f) and c.get('o') is None

    head = '<tr class="xcol"><th class="rh"></th>' + ''.join(f'<th>{LET[i]}</th>' for i in range(len(cols))) + '</tr>'
    head += '<tr class="xhd"><td class="rh">1</td>' + ''.join(f'<td data-a="{LET[i]}1">{TX(c)}</td>' for i, c in enumerate(cols)) + '</tr>'
    body = ''
    for row in rows:
        r = rn[row['k']]
        st = (f'st ' if rev else '')
        if row['kind'] == 'h':
            body += f'<tr class="{st}xsec"{stp(row["_o"]) if rev else ""}><td class="rh">{r}</td><td colspan="{len(cols)}" data-a="A{r}">{TX(row["c"][0])}</td></tr>'
            continue
        cells = list(row['c']) + [''] * (len(cols) - len(row['c']))
        tds, auto = '', False
        for i, c in enumerate(cells):
            h, ex = cell(c, LET[i], row)
            if ex and not auto and rev:
                h = h.replace('class="', 'class="auto ', 1); auto = True
            tds += h
        body += f'<tr class="{st}{row["kind"]}"{stp(row["_o"]) if rev else ""}><td class="rh">{r}</td>{tds}</tr>'
    rnk = lambda s: f'{s.split(":")[1]}{rn[s.split(":")[0]]}'
    arr = ''
    if rev:
        for a in arrows:
            arr += f'<div class="xarr st auto"{stp(a["o"])} data-from="{rnk(a["fr"])}" data-to="{rnk(a["to"])}"><div class="xx">{TX(a["x"])}</div></div>'
            notes.append(('←', '', a['x']))
    else:
        notes += [('←', '', a['x']) for a in arrows]
    cg = ''
    if widths:
        cg = '<colgroup>' + ('<col class="rhc">' if MODE == 'deck' else '') + ''.join(f'<col style="width:{w}%">' for w in widths) + '</colgroup>'
    table = f'<table class="xl">{cg}{head}{body}</table>'
    if MODE == 'pdf':
        nl = ''.join(f'<li><b>{_html.escape(a)}</b> ' + (f'<span class="n" dir="ltr">{_html.escape(f)}</span> ' if f else '') + f'{TX(x)}</li>' for a, f, x in notes if x)
        return f'<div class="xlw">{table}' + (f'<ol class="xln">{nl}</ol>' if nl else '') + '</div>', nend
    tip = ('לחצו על תא ריק: יופיע רמז. כדי לראות את החישוב, לחצו ״הצגת החישוב״.' if practice else 'לחצו על תא צבעוני: כאן יופיעו הנוסחה והחישוב, צעד אחר צעד.')
    btn = '<div class="xbt"><button class="xchk" type="button">בדיקת כל התאים</button><span class="xres"></span></div>' if practice else ''
    return (f'<div class="xlw{" prc" if practice else ""}"><div class="xfb"><span class="xa"></span><span class="fx">fx</span><span class="xf" dir="ltr"></span></div>'
            f'<div class="xsc">{table}{arr}</div><div class="xlp">{TX(tip)}</div>{btn}</div>'), nend


def XS(cols, rows, arrows=(), n=1, widths=None):
    """A sheet on a concept slide, revealed from step n."""
    return XL(cols, rows, arrows, n, widths=widths)[0]


def QCARD(kind, story, asks, cur=None, data=''):
    lab = {'together': 'מסבירים יחד', 'alone': 'נסו לבד', 'class': 'פתרנו בשיעור'}[kind]
    ah = ''.join(f'<p class="{"cur" if cur and l in cur else ""}"><b>{l}.</b> {TX(t)}</p>' if l else f'<p class="{"cur" if cur else ""}">{TX(t)}</p>' for l, t in asks)
    return (f'<div class="card qstem xq sm"><span class="kd {kind}">{lab}</span>' + ''.join(f'<p>{TX(p)}</p>' for p in story) + data
            + f'<div class="asks"><b>נדרש:</b>{ah}</div></div>')


def XQ(key, title, kind, story, asks, sheets, data='', stack=False):
    """A worked exercise on one or more slides: the question on the side, an Excel sheet beside it.
    sheets: dict(cur=letters of the requirement in focus, t=sheet title, cols, rows, arrows, after=[('tip'|'pun'|'band', text)], widths)."""
    NX[0] += 1
    lab = {'together': 'מסבירים יחד', 'alone': 'נסו לבד', 'class': 'פתרנו בשיעור'}[kind]
    sid, k = 'x-' + key, f'חלק {CUR[0]} · {lab}'
    prc = kind == 'alone'
    if MODE == 'pdf':
        b = QCARD(kind, story, asks, None, data)
        for sh in sheets:
            h, _ = XL(sh['cols'], sh['rows'], sh.get('arrows', ()), 1, widths=sh.get('widths'))
            b += f'<div class="xst">{TX(sh["t"])}</div>' + h + ''.join(BAND('dg', '<b>טיפ:</b> ' + t) if kd == 'tip' else (PUN(t) if kd == 'pun' else BAND('note', t)) for kd, t in sh.get('after', ()))
        S(sid, f'{lab}: {title}', f'{lab}: {title}', b, kind='q')
        return
    for i, sh in enumerate(sheets):
        h, n = XL(sh['cols'], sh['rows'], sh.get('arrows', ()), 1, practice=prc, widths=sh.get('widths'))
        aft = ''
        for kd, t in sh.get('after', ()):
            aft += ST(n, '<b>טיפ:</b> ' + TX(t), cls='band dg') if kd == 'tip' else (PUN(t, n) if kd == 'pun' else ST(n, TX(t), cls='band note'))
            n += 1
        tag = '' if len(sheets) == 1 else f' ({i + 1} מתוך {len(sheets)})'
        head = f'{lab}: {title}{tag}'
        sheet = f'<div class="xst">{TX(sh["t"])}</div>{h}{aft}'
        q = QCARD(kind, story, asks, sh.get('cur'), data)
        body = f'<div class="xstack">{q}{sheet}</div>' if stack else f'<div class="xg"><div class="pqq">{q}</div><div class="pqa">{sheet}</div></div>'
        S(sid + ('' if not i else f'c{i + 1}'), head, head, body, kick=k, cls='qslide')


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
