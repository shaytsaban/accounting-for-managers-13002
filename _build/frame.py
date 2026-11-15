# Slide components shared by every lesson's deck and summary. Executed with MODE = 'deck' or 'pdf'.
import re
from lib import *

COURSE = 'חשבונאות למנהלים'
TOTAL_PARTS = 9    # each lesson sets its own
LESSON = globals().get('LESSON', 1)
SL = []            # every slide, in order
CUR = [None]       # current part number


def S(sid, title, h, body, kick=None, cls='', kind='slide'):
    SL.append(dict(id=sid, title=title, h=h, body=link_terms(body), kick=kick, cls=cls, kind=kind, part=CUR[0]))


def ST(n, html, tag='div', cls=''):
    return f'<{tag} class="st {cls}" data-n="{n * 10}">{html}</{tag}>'


def DEF(name, text, demo, n=0, trm=None):
    """One definition with its small numeric demonstration."""
    hd = f'[[{trm}|{name}]]' if trm else name
    inner = f'<b class="dn">{TX(hd)}</b><p>{TX(text)}</p><div class="demo"><b>דוגמה:</b> {TX(demo)}</div>'
    return ST(n, inner, cls='card def') if n else f'<div class="card def">{inner}</div>'


def BAND(kind, text, n=0):
    lab = {'dg': 'דגש', 'trap': 'טעות נפוצה', 'note': 'הערה'}.get(kind, '')
    inner = (f'<b>{lab}:</b> ' if lab else '') + TX(text)
    return ST(n, inner, cls='band ' + kind) if n else f'<div class="band {kind}">{inner}</div>'


def TABLE(head, rows, cls='', rv=0):
    """rv: reveal the rows one by one, starting at step rv."""
    h = ''.join(f'<th>{TX(x)}</th>' for x in head)
    b = ''
    for i, r in enumerate(rows):
        attr = f' class="st" data-n="{(rv + i) * 10}"' if rv else ''
        b += f'<tr{attr}>' + ''.join(f'<td>{TX(c)}</td>' for c in r) + '</tr>'
    return f'<table class="tbl2 {cls}"><tr>{h}</tr>{b}</table>'


def STMT(rows, cls='', rv=0):
    """A financial statement. rows: (label, amount, kind), kind '', 'h' section title, 'subt' subtotal, 'tot' final line.
    rv: reveal by blocks from step rv: every subtotal closes a block."""
    out, step = '', rv
    for lab, amt, kind in rows:
        attr = f' data-n="{step * 10}"' if rv else ''
        c = ' '.join(x for x in ('st' if rv else '', kind) if x)
        cl = f' class="{c}"' if c else ''
        out += f'<tr{cl}{attr}><td>{TX(lab)}</td><td class="amt"><span class="n">{amt}</span></td></tr>'
        if rv and kind in ('subt', 'tot'): step += 1
    return f'<table class="stmt {cls}">{out}</table>'


def STT(t):
    return f'<div class="stt">{TX(t)}</div>'


def FLOW(nodes, rv=0):
    """Horizontal chain, read from right to left. rv: reveal node by node, from step rv."""
    out = ''
    for i, t in enumerate(nodes):
        arr = '<div class="farr">←</div>' if i else ''
        if rv:
            if i: out += ST(rv + i, '←', cls='farr')
            out += ST(rv + i, TX(t), cls='fnode')
        else:
            out += arr + f'<div class="fnode">{TX(t)}</div>'
    return f'<div class="flowx">{out}</div>'


def IDENT(items):
    """Left to right equation of boxes: (kind css, title, small note, number) or a bare operator string."""
    out = ''
    for it in items:
        if isinstance(it, str):
            out += f'<div class="iop">{it.replace("-", "−")}</div>'
        else:
            k, t, sm, num = it
            out += f'<div class="ibox {k}"><b>{t}</b>' + (f'<small>{TX(sm)}</small>' if sm else '') + (f'<span class="n">{num}</span>' if num else '') + '</div>'
    return f'<div class="ident" dir="ltr">{out}</div>'


def EQW(words, nums=None, n=0):
    """A formula in words and, under it, in numbers. Both run left to right."""
    h = ''
    for i, x in enumerate([words] + ([nums] if nums else [])):
        h += f'<div class="eq c" dir="ltr">{M(x)}</div>'
    return ST(n, h, cls='card') if n else f'<div class="card">{h}</div>'


def mc(qid, q, opts, a, why):
    o = ''
    for i, t in enumerate(opts):
        mark = ' correct' if MODE == 'pdf' and i == a else ''
        o += f'<button class="o{mark}" data-i="{i}">{"אבגדה"[i]}. {TX(t)}</button>'
    return f'<div class="mc" data-a="{a}" id="{qid}"><div class="q">{TX(q)}</div>{o}<div class="w"><b>הסבר:</b> {TX(why)}</div></div>'


def MCS(sid, title, h, items):
    """A slide of multiple choice checks, side by side."""
    S(sid, title, h, f'<div class="mcrow n{len(items)}">' + ''.join(items) + '</div>', kick=f'חלק {CUR[0]} · בדיקת הבנה')


def opener(n, title, q, learn, mins, note='', hidden=False, selfp=False):
    """hidden: the part has a heading in the summary, but no divider slide in the deck."""
    CUR[0] = n
    SL.append(dict(id=f'p-{n}', title=f'פתיחת חלק {n}: {title}', h=title, kind='opener', part=n, q=q, learn=learn, mins=mins, note=note, cls='', kick=None, body='', hidden=hidden, selfp=selfp))


def calc(cid, title, intro, fields, pdfx, h=None):
    """Interactive calculator: fields are (key, label, default) or (key, label, default, [(value, text)...])."""
    if MODE == 'pdf':
        S('c-' + cid, title, h or title, f'<div class="calcp"><b>מחשבון במצגת.</b> {TX(intro)} <b>דוגמה:</b> {TX(pdfx)}</div>', kind='calcp')
        return
    fs = ''
    for f in fields:
        if len(f) == 4:
            opts = ''.join(f'<option value="{v}"{" selected" if v == f[2] else ""}>{t}</option>' for v, t in f[3])
            fs += f'<label class="cf"><span>{TX(f[1])}</span><select data-k="{f[0]}">{opts}</select></label>'
        else:
            fs += f'<label class="cf"><span>{TX(f[1])}</span><input data-k="{f[0]}" value="{f[2]}" dir="ltr" inputmode="decimal" autocomplete="off" spellcheck="false"></label>'
    body = (f'<div class="calc" data-calc="{cid}"><div class="cin"><p class="cint">{TX(intro)}</p><div class="cfs">{fs}</div></div>'
            f'<div class="cout" id="out-{cid}"></div></div>')
    S('c-' + cid, title, h or title, body, kick=f'חלק {CUR[0]} · מחשבון')


def CAP(t):
    return f'<p class="cap">{TX(t)}</p>'


def rcard(n, t, d, m, go):
    return f'<button class="rcard" data-go="{go}"><div class="n">{n}</div><b>{t}</b><span>{TX(d)}</span><em>{m}</em></button>'


def RULE(t, n=0):
    return ST(n, TX(t), cls='rule') if n else f'<div class="rule">{TX(t)}</div>'


def PUN(t, n=0):
    return ST(n, TX(t), cls='pun') if n else f'<div class="pun">{TX(t)}</div>'


def ILLW(svg, n=0):
    return ST(n, svg, cls='illw') if n else f'<div class="illw">{svg}</div>'


def PRIN(sid, title, items, toon=None, cap=''):
    """A closing slide: the principles of the part, each in one line, with a cartoon."""
    li = ''.join(ST(i + 1, '<span>' + TX(t) + '</span>', 'li') for i, t in enumerate(items))
    body = f'<ol class="prin">{li}</ol>'
    if toon: body = f'<div class="toonr">{body}{TOON(toon, cap)}</div>'
    S(sid, title, title, body, kick=f'חלק {CUR[0]} · עקרונות')


def _sg(x):
    return f'$+{x:,}$' if x > 0 else f'$-{-x:,}$'


def _cell(items):
    if not items: return '<span class="no">ללא שינוי</span>'
    out = ''
    for it in items:
        note = f'<small>{TX(it[2])}</small>' if len(it) > 2 else ''
        out += f'<span class="li">{TX(it[0])} {TX(_sg(it[1]))}{note}</span>'
    return out


def _chk(a, l, e):
    f = lambda x: f'({x:,})' if x < 0 else f'{x:,}'
    return M(f'{a:,} = {l:,} + {f(e)}')


def _rv(inner, n):
    """A table cell that shows a question mark until its click."""
    return ST(n, inner) + ('<span class="qm">?</span>' if MODE == 'deck' else '')


def TT(ev, A=(), L=(), E=(), n=0, cum=None, step=False, nochk=False):
    """One transaction in one small table: assets on one side, liabilities and equity on the other.
    A, L, E: (line item, signed amount[, note]). The equation is checked here, at build time, and printed under the table.
    n: reveal at step n. step: three clicks from n: assets, then liabilities, then equity, each behind a question mark."""
    da, dl, de = (sum(i[1] for i in x) for x in (A, L, E))
    assert da == dl + de, ev
    ca, cb, cc = (_rv(_cell(x), n + i) if step else _cell(x) for i, x in enumerate((A, L, E)))
    rc = ' rvc' if step else ''
    rows = f'<tr><td class="ta{rc}">{ca}</td><td class="op">=</td><td class="tb{rc}">{cb}</td><td class="op">+</td><td class="tc{rc}">{cc}</td></tr>'
    if cum:
        assert cum[0] == cum[1] + cum[2], ev
        cr = f'class="cum st" data-n="{(n + 2) * 10}"' if step else 'class="cum"'
        rows += f'<tr {cr}><td class="ta">{TX(f"{cum[0]:,}")}</td><td class="op">=</td><td class="tb">{TX(f"{cum[1]:,}")}</td><td class="op">+</td><td class="tc">{TX(f"{cum[2]:,}")}</td></tr>'
    chk = '' if cum or nochk else f'השוויון נשמר: <span class="m" dir="ltr">{_chk(da, dl, de)}</span>'
    if chk: chk = ST(n + 2, chk, cls='ttc') if step else f'<div class="ttc" dir="rtl">{chk}</div>'
    head = f'<div class="tth">{TX(ev)}</div>' if ev else ''
    inner = f'{head}<table class="tt"><tr><th class="ta">נכסים</th><th class="op"></th><th class="tb">התחייבויות</th><th class="op"></th><th class="tc">הון עצמי</th></tr>{rows}</table>{chk}'
    return ST(n, inner, cls='ttw') if n and not step else f'<div class="ttw">{inner}</div>'


def _su(A, L, E):
    """Source and use, worked out from the signs, so that they can never disagree with the table."""
    src = [x for x in A if x[1] < 0] + [x for x in L + E if x[1] > 0]
    use = [x for x in A if x[1] > 0] + [x for x in L + E if x[1] < 0]
    assert sum(abs(x[1]) for x in src) == sum(abs(x[1]) for x in use)
    f = lambda xs: ', '.join(f'{x[0]} {abs(x[1]):,}' for x in xs)
    return f'<b>מקור:</b> {TX(f(src))} <b class="sa">←</b> <b>שימוש:</b> {TX(f(use))}'


def TXQ(sid, head, kick, ev, A, L, E, wa, wl, we, pun=None, cum=None):
    """A slide for one transaction. The event is on screen; click 1 opens assets, click 2 liabilities, click 3 equity, each with its bullet."""
    A, L, E = list(A), list(L), list(E)
    da, dl, de = (sum(i[1] for i in x) for x in (A, L, E))
    bl = ''.join(ST(i + 1, f'<b class="{c}">{lab}:</b> {TX(w)}', 'li') for i, (c, lab, w) in enumerate((('ka', 'נכסים', wa), ('kb', 'התחייבויות', wl), ('kc', 'הון עצמי', we))))
    strip = f'<span>{_su(A, L, E)}</span><span class="txchk">השוויון נשמר: <span class="m" dir="ltr">{_chk(da, dl, de)}</span></span>'
    S(sid, re.sub(r'.*?: ', '', head, 1) if ':' in head else head, head,
      f'<div class="txev">{TX(ev)}</div>' + TT('', A, L, E, 1, cum, True, True) + f'<ul class="txb">{bl}</ul>' + ST(3, strip, cls='txsu') + (PUN(pun, 3) if pun else ''), kick=kick)


def DEC(q, branches, n=0, sm=False):
    """A flowchart step, read from right to left. branches: (label, content, 'no' or ''); content may be another DEC."""
    br = ''
    for i, (lab, c, kind) in enumerate(branches):
        cl = 'da' + (' no' if kind else '')
        if c.startswith('<div class="dec'):
            br += (f'<div class="{cl}"><span class="lab">{lab}</span></div>' if lab else '') + c
        else:
            inner = (f'<span class="lab">{lab}</span>' if lab else '') + TX(c)
            br += ST(n + i, inner, cls=cl) if n else f'<div class="{cl}">{inner}</div>'
    return f'<div class="dec{" sm" if sm else ""}"><div class="dq">{TX(q)}</div><div class="farr">←</div><div class="dbr">{br}</div></div>'


# ---------------------------------------------------------------- a practice question, with its solution on the same slide
Q_ASK = 'הטענה / הטענות הנכונה / הנכונות:'
VD = {'ok': 'נכונה', 'bad': 'שגויה', 'na': 'לא רלוונטי'}


def CLM(tag, v, paras, n=0, big=''):
    if ':' in v: v, lab = v.split(':', 1)
    else: lab = VD.get(v, '')
    pill = f'<span class="vd {v}">{lab}</span>' if v else ''
    body = ''.join(p if p.startswith('<') else f'<p>{TX(p)}</p>' for p in paras)
    inner = f'<div class="hd"><div class="tg">{TX(tag)}</div>{pill}</div><div class="bd">{body}</div>'
    cl = f'clm {big}' if big else 'clm'
    return ST(n, inner, cls=cl) if n else f'<div class="{cl}">{inner}</div>'


def _est(e, fs=46):
    """Rough height of one solution block in the answer column, used to decide where a long solution continues."""
    h = 42
    for p in e[2]:
        if p.startswith('<div class="ttw'):
            h += 112 + 13 * p.count('class="li"') + (24 if 'class="tth"' in p else 0)
        else:
            h += (len(re.sub(r'\\\\f\\{|\\$', '', p)) // fs + 1) * 30 + 4
    return h


def PQ(key, title, stem, claims, opts, a, why, sols, ans, ask=Q_ASK, name='שאלת תרגול', pun=None, sm=False):
    """The question stays on screen, in the right column, on every slide of its solution.
    stem: paragraphs. claims: claim sentences, or None when the options themselves are the claims.
    sols: (tag, verdict, paragraphs); paragraphs may hold TT tables. Long solutions continue on a further slide, with the question repeated."""
    sid = f'q{key}' if isinstance(key, int) else f'h-{key}'
    full = f'{name} {key}' if isinstance(key, int) else name
    head = f'{full}: {title}'
    k = f'חלק {CUR[0]} · {full}'
    one = not claims and len(stem) == 1
    stem_h = '' if one else ''.join(f'<p>{TX(x)}</p>' for x in stem)
    claim_h = ''.join(f'<p><b>טענה {i + 1}:</b> {TX(c)}</p>' for i, c in enumerate(claims or []))
    qtext = stem[0] if one else ask
    q_mc = mc(f'pq-{sid}', qtext, opts, a, why)
    flat = [e for sl in sols for e in (sl if isinstance(sl, list) else [sl])]
    if MODE == 'pdf':
        b = (f'<div class="qstem">{stem_h}{claim_h}</div>' if stem_h or claim_h else '') + q_mc
        for tag, v, ps in flat: b += CLM(tag, v, ps)
        b += f'<div class="band ans"><b>תשובה:</b> {TX(ans)}</div>' + (PUN(pun) if pun else '')
        S(sid, head, head, b, kind='q')
        return
    card = f'<div class="card qstem{" sm" if sm else ""}">{stem_h}{claim_h}</div>' if stem_h or claim_h else ''
    static = '<div class="sopts">' + f'<div class="q">{TX(qtext)}</div>' + ''.join(f'<p>{"אבגדה"[i]}. {TX(t)}</p>' for i, t in enumerate(opts)) + '</div>'
    chunks, cur, used = [], [], 0
    for e in flat:
        h = _est(e)
        if cur and used + h > 470: chunks.append(cur); cur, used = [], 0
        cur.append(e); used += h
    chunks.append(cur)
    for i, ch in enumerate(chunks):
        last = i == len(chunks) - 1
        chars = sum(len(p) for _, _, ps in ch for p in ps if not p.startswith('<'))
        tb = any(p.startswith('<') for _, _, ps in ch for p in ps)
        big = 'big' if not tb and chars < 500 else ''
        h = ''.join(CLM(t, v, ps, j + 1, big) for j, (t, v, ps) in enumerate(ch))
        if last:
            h += ST(len(ch) + 1, f'<b>תשובה:</b> {TX(ans)}', cls='band ans') + (PUN(pun, len(ch) + 2) if pun else '')
        qchars = sum(len(x) for x in stem) + sum(len(c) for c in (claims or [])) + sum(len(o) for o in opts)
        body = f'<div class="pq2"><div class="pqq{" lg" if qchars < 300 and not claims else ""}">{card}{q_mc if i == 0 else static}</div><div class="pqa">{h}</div></div>'
        tag = '' if len(chunks) == 1 else f' ({i + 1} מתוך {len(chunks)})'
        S(sid + ('' if not i else f'c{i + 1}'), head + tag, head + tag, body, kick=k, cls='qslide')


