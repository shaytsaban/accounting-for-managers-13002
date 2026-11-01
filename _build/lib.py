# Shared helpers for the deck and the summary PDF: inline math, text markup, timelines.
import re, html as _h

HEB = re.compile(r'[֐-׿]')


def _braces(s, i):
    """s[i] is '{'. Return (inner, index after the closing brace)."""
    d = 0
    for j in range(i, len(s)):
        if s[j] == '{': d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0: return s[i + 1:j], j + 1
    raise ValueError('unbalanced braces: ' + s)


def _minus(s):
    s = re.sub(r'(?<=\s)-(?=\s)', '−', s)
    return re.sub(r'(^|[\s(=×+])-(?=[\d(a-zA-Z])', r'\1−', s)


def M(s):
    """Math mini language: ^{x} _{x} \\f{num}{den} \\h{Hebrew}. Returns HTML."""
    out, i, buf = [], 0, ''

    def flush():
        nonlocal buf
        if buf: out.append(_minus(buf))
        buf = ''
    while i < len(s):
        c = s[i]
        if c == '^' and s[i + 1:i + 2] == '{':
            flush(); a, i = _braces(s, i + 1); out.append(f'<sup>{M(a)}</sup>')
        elif c == '_' and s[i + 1:i + 2] == '{':
            flush(); a, i = _braces(s, i + 1); out.append(f'<sub>{M(a)}</sub>')
        elif s.startswith('\\f{', i):
            flush(); a, i = _braces(s, i + 2); b, i = _braces(s, i)
            out.append(f'<span class="frac"><span>{M(a)}</span><span>{M(b)}</span></span>')
        elif s.startswith('\\h{', i):
            flush(); a, i = _braces(s, i + 2); out.append(f'<span class="mh" dir="rtl">{a}</span>')
        else:
            buf += c; i += 1
    flush()
    return ''.join(out)


NUM = re.compile(r'(?<![\w.,/])\d[\d,]*(?:\.\d+)*%?')


def _textnum(seg):
    return NUM.sub(lambda m: f'<span class="n">{m.group(0)}</span>', seg)


def TX(s):
    """Prose markup: $math$, [[key|text]] for a glossary term, and LTR isolation of every number."""
    s = re.sub(r'\[\[(\w+)\|([^\]]+)\]\]', r'<span class="term" data-t="\1">\2</span>', s)
    parts = re.split(r'(\$[^$]+\$)', s)
    out = []
    for p in parts:
        if p.startswith('$') and p.endswith('$') and len(p) > 1:
            out.append(f'<span class="m" dir="ltr">{M(p[1:-1])}</span>')
        else:
            out.append(''.join(seg if seg.startswith('<') else _textnum(seg) for seg in re.split(r'(<[^>]+>)', p)))
    return ''.join(out)


def EQ(s, cls=''):
    return f'<div class="eq {cls}" dir="ltr">{M(s)}</div>'


AUTO = [('ממ״ן', 'mamman')]
SKIP = {'button', 'svg', 'a', 'select', 'label', 'option', 'script', 'style'}


def link_terms(body):
    """First mention per slide of an abbreviation becomes a glossary link (never inside buttons or diagrams)."""
    seen = set(re.findall(r'class="term" data-t="(\w+)"', body))
    toks = re.split(r'(<[^>]+>)', body)
    depth, interm, out = 0, 0, []
    for t in toks:
        if t.startswith('<'):
            m = re.match(r'<(/?)(\w+)', t)
            if m:
                name = m.group(2).lower()
                if name in SKIP: depth += -1 if m.group(1) else 1
                if name == 'span':
                    if 'class="term"' in t: interm = 1
                    elif m.group(1) and interm: interm = 0
            out.append(t); continue
        if depth <= 0 and not interm and t:
            for ab, k in AUTO:
                if k in seen: continue
                rx = re.compile(r'(?<![A-Za-zא-ת])' + ab + r'(?![A-Za-zא-ת])')
                if rx.search(t):
                    t = rx.sub(f'<span class="term" data-t="{k}">{ab}</span>', t, count=1); seen.add(k)
                    # the abbreviation is now wrapped: stop scanning this segment for the shorter names
                    break
        out.append(t)
    return ''.join(out)


# ---------------------------------------------------------------- timeline
def _sv(t, fs):
    """SVG text from the small math language: only ^{..} is supported."""
    out, i = '', 0
    t = _minus(t)
    while i < len(t):
        if t.startswith('^{', i):
            a, i = _braces(t, i + 1)
            out += f'<tspan dy="{-fs * .38:.1f}" font-size="{fs * .72:.1f}">{_h.escape(a)}</tspan><tspan dy="{fs * .38:.1f}"> </tspan>'
        else:
            out += _h.escape(t[i]); i += 1
    return out


def _txt(x, y, t, fs, W, anchor='middle', fill='#16213a', weight=500):
    plain = re.sub(r'\^\{[^}]*\}', 'x', str(t))
    w = len(plain) * fs * .56
    if anchor == 'middle':
        if x - w / 2 < 3: x, anchor = 3, 'start'
        elif x + w / 2 > W - 3: x, anchor = W - 3, 'end'
    rtl = ' direction="rtl"' if HEB.search(str(t)) else ''
    if rtl: anchor = {'start': 'end', 'end': 'start'}.get(anchor, anchor)
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}"{rtl}>{_sv(str(t), fs)}</text>'


def _st(s):
    return f' class="st" data-n="{s * 10}"' if s else ''


def TL(ticks, flows=None, moves=None, brace=None, marks=None, W=560, fs=17, fh=46):
    """Timeline as inline SVG, time running left to right.
    ticks: labels in order ('...' draws dots). flows: {tick: label or ''}. moves: dicts a, b, t (caption), s (reveal step).
    brace: (from, to, label, step). marks: {tick: label}, a dotted line up to a bold label."""
    flows, moves, brace, marks = flows or {}, moves or [], brace or [], marks or {}
    n = len(ticks)
    left, right = 28, W - 40
    dx = (right - left) / max(n - 1, 1)
    X = {str(l): left + i * dx for i, l in enumerate(ticks)}
    y = 6
    has_lab = any(v for v in flows.values()) or marks
    by = None
    if brace:
        by = y + fs + 2
        y = by + 16
    ly = y + fs if has_lab else y
    if has_lab: y = ly + 5
    ay = y                        # arrow tips
    y0 = ay + fh                  # axis
    p = []
    p.append(f'<line x1="6" y1="{y0}" x2="{W - 12}" y2="{y0}" stroke="#1b2d55" stroke-width="2.6"/><polygon points="{W - 4},{y0} {W - 17},{y0 - 6} {W - 17},{y0 + 6}" fill="#1b2d55"/>')
    for l in ticks:
        x = X[str(l)]
        if str(l) in ('...', '···'):
            p.append(_txt(x, y0 - 14, '···', fs + 5, W, fill='#8a93aa', weight=700))
            p.append(_txt(x, y0 + fs + 6, '···', fs, W, fill='#8a93aa', weight=700))
            continue
        p.append(f'<line x1="{x:.1f}" y1="{y0 - 6}" x2="{x:.1f}" y2="{y0 + 6}" stroke="#1b2d55" stroke-width="2.2"/>')
        p.append(_txt(x, y0 + fs + 6, str(l), fs, W, weight=600))
    for k, lab in flows.items():
        x = X[str(k)]
        p.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{ay + 8}" stroke="#ff6a4d" stroke-width="3"/><polygon points="{x:.1f},{ay} {x - 5.5:.1f},{ay + 11} {x + 5.5:.1f},{ay + 11}" fill="#ff6a4d"/>')
        if lab: p.append(_txt(x, ly, lab, fs - 1, W, fill='#b8391f', weight=700))
    for k, lab in marks.items():
        x = X[str(k)]
        p.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{ly + 5}" stroke="#16213a" stroke-width="1.6" stroke-dasharray="2 4"/>')
        p.append(_txt(x, ly, lab, fs, W, weight=800))
    for b in brace:
        a, c, lab = b[0], b[1], b[2]
        s = b[3] if len(b) > 3 else 0
        xa, xc = X[str(a)], X[str(c)]
        yb = by + 2
        p.append(f'<g{_st(s)}><path d="M{xa:.1f} {yb + 10} V{yb + 2} H{xc:.1f} V{yb + 10}" fill="none" stroke="#5d6a86" stroke-width="1.8"/>{_txt((xa + xc) / 2, by - 2, lab, fs - 1, W, fill="#2a3858", weight=600)}</g>')
    ym = y0 + fs + 24
    for m in moves:
        xa, xb = X[str(m['a'])], X[str(m['b'])]
        fwd = xb >= xa
        if xa == xb:
            col = m.get('c') or '#0f9d90'
            g = (f'<line x1="{xa:.1f}" y1="{y0 + fs + 9}" x2="{xa:.1f}" y2="{ym}" stroke="#8a93aa" stroke-width="1.4" stroke-dasharray="2 4"/><circle cx="{xa:.1f}" cy="{ym}" r="5.5" fill="{col}"/>')
            if m.get('t'): g += _txt(xa, ym + fs + 5, m['t'], fs - 1, W, fill=col, weight=700)
            p.append(f'<g{_st(m.get("s", 0))}>{g}</g>')
            ym += fs + 26
            continue
        col = m.get('c') or ('#0f9d90' if fwd else '#6d4df2')
        sgn = 1 if fwd else -1
        g = (f'<line x1="{xa:.1f}" y1="{y0 + fs + 9}" x2="{xa:.1f}" y2="{ym}" stroke="#8a93aa" stroke-width="1.4" stroke-dasharray="2 4"/>'
             f'<line x1="{xb:.1f}" y1="{y0 + fs + 9}" x2="{xb:.1f}" y2="{ym}" stroke="#8a93aa" stroke-width="1.4" stroke-dasharray="2 4"/>'
             f'<circle cx="{xa:.1f}" cy="{ym}" r="4.5" fill="{col}"/>'
             f'<line x1="{xa:.1f}" y1="{ym}" x2="{xb - sgn * 9:.1f}" y2="{ym}" stroke="{col}" stroke-width="2.6" stroke-dasharray="7 5"/>'
             f'<polygon points="{xb:.1f},{ym} {xb - sgn * 11:.1f},{ym - 6} {xb - sgn * 11:.1f},{ym + 6}" fill="{col}"/>')
        if m.get('t'):
            g += _txt((xa + xb) / 2, ym + fs + 5, m['t'], fs - 1, W, fill=col, weight=700)
        p.append(f'<g{_st(m.get("s", 0))}>{g}</g>')
        ym += fs + 26
    H = ym - 8 if moves else y0 + fs + 16
    return f'<svg class="tl" dir="ltr" viewBox="0 0 {W} {H:.0f}" role="img">' + ''.join(p) + '</svg>'


# ---------------------------------------------------------------- illustrations (inline SVG, drawn here, so they print and work offline)
_IC = {
 'cash': '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 9v0M18 15v0"/>',
 'box': '<path d="M3 8l9-5 9 5v8l-9 5-9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
 'gear': '<circle cx="12" cy="12" r="3.5"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l3 3M16 16l3 3M19 5l-3 3M8 16l-3 3"/>',
 'bldg': '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M10 21v-5h4v5"/>',
 'doc': '<path d="M6 2h9l4 4v16H6z"/><path d="M15 2v4h4M9 11h7M9 15h7M9 19h4"/>',
 'book': '<path d="M12 6c-2-2-5-2-9-2v15c4 0 7 0 9 2 2-2 5-2 9-2V4c-4 0-7 0-9 2zM12 6v15"/>',
 'bank': '<path d="M3 9l9-6 9 6zM5 9v9M10 9v9M14 9v9M19 9v9M3 21h18M4 18h16"/>',
 'deal': '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>',
}


def ICON(name, s=30):
    return f'<svg class="ic" dir="ltr" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_IC[name]}</svg>'


def _t(x, y, t, fs=18, fill='#16213a', w=700):
    rtl = ' direction="rtl"' if HEB.search(str(t)) else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" text-anchor="middle" fill="{fill}" font-weight="{w}"{rtl}>{_h.escape(str(t))}</text>'


def _money(v):
    return f'{v:,.0f}'


def WATER(items, W=1120, H=330, st=0):
    """Waterfall, read from right to left like the statement. items: (label, value, kind), kind 'tot', 'down', 'up' or 'net'."""
    top = max(v for _, v, k in items if k != 'down')
    base, peak = H - 58, 40
    sc = (base - peak) / top
    n = len(items)
    dx = (W - 20) / n
    bw = dx * .66
    cur, out = 0, [f'<line x1="6" y1="{base}" x2="{W - 6}" y2="{base}" stroke="#1b2d55" stroke-width="2"/>']
    col = {'tot': '#1b2d55', 'down': '#e0454f', 'up': '#25a65f', 'net': '#25a65f'}
    px = None
    for i, (lab, v, k) in enumerate(items):
        x = W - 10 - dx * (i + 1) + (dx - bw) / 2
        if k == 'down': t, b, cur = cur, cur - v, cur - v
        elif k == 'up': t, b, cur = cur + v, cur, cur + v
        else: t, b, cur = v, 0, v
        y1, y2 = base - t * sc, base - b * sc
        g = f'<rect x="{x:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{max(y2 - y1, 2):.1f}" rx="4" fill="{col[k]}"/>'
        g += _t(x + bw / 2, y1 - 8, f'({_money(v)})' if k == 'down' else _money(v), 18)
        for j, ln in enumerate(lab.split('\n')):
            g += _t(x + bw / 2, base + 24 + j * 21, ln, 17.5, '#2a3858', 600)
        if px is not None:
            ly = base - (t if k == 'down' else b if k == 'up' else t) * sc
            g = f'<line x1="{x + bw:.1f}" y1="{ly:.1f}" x2="{px:.1f}" y2="{ly:.1f}" stroke="#8a93aa" stroke-width="1.4" stroke-dasharray="3 3"/>' + g
        px = x
        attr = f' class="st" data-n="{(st + i) * 10}"' if st else ''
        out.append(f'<g{attr}>{g}</g>')
    return f'<svg class="ill" dir="ltr" viewBox="0 0 {W} {H}" role="img">' + ''.join(out) + '</svg>'


def STACK(left, right, total, W=1120, H=340):
    """A balance sheet as two equal stacks. Each stack: (label, value, fill, text colour), top to bottom."""
    top, base = 8, H - 30
    sc = (base - top) / total
    out = []
    for stack, x0, cap in ((right, W / 2 + 30, 'הנכסים: מה יש לחברה'), (left, 30, 'המקורות: מי מימן')):
        w, y = W / 2 - 60, top
        for lab, v, fill, tc in stack:
            h = v * sc
            mid = y + h / 2 + 6
            out.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h - 2:.1f}" rx="5" fill="{fill}"/>' + _t(x0 + w * .64, mid, lab, 19, tc) + _t(x0 + w * .2, mid, _money(v), 19, tc))
            y += h
        out.append(_t(x0 + w / 2, H - 6, cap, 19, '#1b2d55', 800))
    out.append(_t(W / 2, H / 2 + 8, '=', 34, '#1b2d55', 800))
    return f'<svg class="ill" dir="ltr" viewBox="0 0 {W} {H}" role="img">' + ''.join(out) + '</svg>'


def SCALE(a, b, W=1120, H=196):
    """The accounting equation as a level balance: two equal pans."""
    cx, by = W / 2, 54
    out = [f'<path d="M{cx - 26} {H - 8} L{cx} {by} L{cx + 26} {H - 8} Z" fill="#1b2d55"/><rect x="{cx - 240}" y="{by - 5}" width="480" height="10" rx="5" fill="#1b2d55"/>']
    for x, (t, fill, tc) in ((cx - 240, a), (cx + 240, b)):
        out.append(f'<line x1="{x}" y1="{by}" x2="{x}" y2="{by + 46}" stroke="#1b2d55" stroke-width="2.4"/><rect x="{x - 170}" y="{by + 46}" width="340" height="62" rx="12" fill="{fill}"/>' + _t(x, by + 85, t, 24, tc, 800))
    return f'<svg class="ill" dir="ltr" viewBox="0 0 {W} {H}" role="img">' + ''.join(out) + '</svg>'


def PHOTOFILM(W=1120, H=150):
    """The balance sheet is a photograph of one day; the income statement is a film of a period."""
    y, o = 16, []
    # film on the left half
    for i in range(6):
        x = 110 + i * 66
        o.append(f'<rect x="{x}" y="{y}" width="60" height="74" rx="4" fill="#ece8ff" stroke="#4f33c9" stroke-width="2"/>')
        for dy in (6, 58):
            o.append(f'<rect x="{x + 8}" y="{y + dy}" width="10" height="9" fill="#4f33c9"/><rect x="{x + 42}" y="{y + dy}" width="10" height="9" fill="#4f33c9"/>')
    o.append(_t(306, y + 108, 'דוח רווח והפסד: סרט של תקופה שלמה', 21, '#4f33c9', 800))
    # camera on the right half
    x = W - 306
    o.append(f'<rect x="{x - 62}" y="{y + 14}" width="124" height="66" rx="10" fill="#dff5f2" stroke="#087469" stroke-width="2.4"/><rect x="{x - 24}" y="{y}" width="48" height="16" rx="4" fill="#087469"/><circle cx="{x}" cy="{y + 47}" r="22" fill="#fff" stroke="#087469" stroke-width="3"/><circle cx="{x}" cy="{y + 47}" r="10" fill="#087469"/>')
    o.append(_t(x, y + 108, 'המאזן: צילום של יום אחד', 21, '#087469', 800))
    return f'<svg class="ill" dir="ltr" viewBox="0 0 {W} {H}" role="img">' + ''.join(o) + '</svg>'


def _face(cx, cy, r, mood='smile', fill='#ffd37a'):
    mouth = {'smile': f'M{cx - r * .45} {cy + r * .25} Q{cx} {cy + r * .75} {cx + r * .45} {cy + r * .25}',
             'sad': f'M{cx - r * .4} {cy + r * .55} Q{cx} {cy + r * .15} {cx + r * .4} {cy + r * .55}',
             'flat': f'M{cx - r * .35} {cy + r * .4} L{cx + r * .35} {cy + r * .4}'}[mood]
    tear = f'<path d="M{cx + r * .42} {cy} q-7 12 0 17 q7 -5 0 -17z" fill="#58a6ff"/>' if mood == 'sad' else ''
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="#16213a" stroke-width="3"/>'
            f'<circle cx="{cx - r * .36}" cy="{cy - r * .18}" r="{r * .1:.1f}" fill="#16213a"/><circle cx="{cx + r * .36}" cy="{cy - r * .18}" r="{r * .1:.1f}" fill="#16213a"/>'
            f'<path d="{mouth}" fill="none" stroke="#16213a" stroke-width="3" stroke-linecap="round"/>{tear}')


_TOONS = {
 # a balance that refuses to balance
 'tilt': '<g transform="rotate(-13 130 62)"><rect x="30" y="56" width="200" height="10" rx="5" fill="#1b2d55"/><rect x="18" y="66" width="62" height="34" rx="6" fill="#dff5f2" stroke="#087469" stroke-width="2.5"/><rect x="180" y="66" width="62" height="34" rx="6" fill="#ece8ff" stroke="#4f33c9" stroke-width="2.5"/></g><path d="M112 165 L130 62 L148 165 Z" fill="#1b2d55"/>' + _face(130, 122, 24, 'sad'),
 # coins leaving on small legs
 'div': '<rect x="24" y="84" width="92" height="66" rx="8" fill="#e8960c" stroke="#16213a" stroke-width="3"/><path d="M24 84 q46 -44 92 0" fill="#ffd37a" stroke="#16213a" stroke-width="3"/>' + _face(190, 82, 30, 'smile') + '<path d="M176 112 l-8 40 M204 112 l8 40 M160 100 l-22 16 M220 100 l22 -22" stroke="#16213a" stroke-width="4" stroke-linecap="round"/>',
 # cash arrived, income did not
 'adv': '<rect x="26" y="48" width="130" height="78" rx="8" fill="#25a65f" stroke="#16213a" stroke-width="3"/><circle cx="91" cy="87" r="24" fill="#dcf5e6" stroke="#16213a" stroke-width="3"/><path d="M84 76 v20 M98 78 v20" stroke="#167a43" stroke-width="4" stroke-linecap="round"/>' + _face(204, 96, 32, 'flat'),
 # the bulb is on, the bill is on its way
 'bulb': '<path d="M100 120 C66 96 72 40 118 38 C164 40 170 96 136 120 Z" fill="#ffd37a" stroke="#16213a" stroke-width="3"/><rect x="100" y="122" width="36" height="24" rx="5" fill="#8a93aa" stroke="#16213a" stroke-width="3"/>' + _face(118, 80, 22, 'smile', '#fff4c9') + '<path d="M60 40 l-20 -14 M176 40 l20 -14 M48 84 h-22 M188 84 h22" stroke="#e8960c" stroke-width="4" stroke-linecap="round"/>',
 # a hard working machine that is still non-current
 'mach': '<rect x="40" y="40" width="170" height="104" rx="12" fill="#c8d4f2" stroke="#16213a" stroke-width="3"/><circle cx="200" cy="34" r="20" fill="#8a93aa" stroke="#16213a" stroke-width="3"/><rect x="192" y="26" width="16" height="16" rx="3" fill="#fff"/>' + _face(125, 92, 32, 'smile', '#fff') + '<rect x="56" y="144" width="30" height="16" fill="#16213a"/><rect x="164" y="144" width="30" height="16" fill="#16213a"/>',
 # a contract signed, nobody owes anything yet
 'deal': '<rect x="60" y="20" width="110" height="136" rx="6" fill="#fff" stroke="#16213a" stroke-width="3"/><path d="M78 48 h74 M78 70 h74 M78 92 h50" stroke="#8a93aa" stroke-width="4" stroke-linecap="round"/><path d="M80 130 q14 -22 24 -2 t24 -6 t18 2" fill="none" stroke="#4f33c9" stroke-width="3" stroke-linecap="round"/>' + _face(205, 104, 28, 'flat'),
}


def TOON(name, cap=''):
    c = f'<div class="tc">{TX(cap)}</div>' if cap else ''
    return f'<div class="toon"><svg class="tn" dir="ltr" viewBox="0 0 250 170" role="img">{_TOONS[name]}</svg>{c}</div>'
