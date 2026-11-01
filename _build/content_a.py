# Lesson content, shared by the deck and the summary. Executed with MODE = 'deck' or 'pdf'.
import re
from lib import *

COURSE = 'חשבונאות למנהלים'
TOTAL_PARTS = 9
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


def opener(n, title, q, learn, mins, note='', hidden=False):
    """hidden: the part has a heading in the summary, but no divider slide in the deck."""
    CUR[0] = n
    SL.append(dict(id=f'p-{n}', title=f'פתיחת חלק {n}: {title}', h=title, kind='opener', part=n, q=q, learn=learn, mins=mins, note=note, cls='', kick=None, body='', hidden=hidden))


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


# ================================================================ statements of the lesson
BS_ASSETS = [('נכסים שוטפים: מזומן', '40,000', ''), ('לקוחות', '60,000', ''), ('מלאי', '50,000', ''), ('סך נכסים שוטפים', '150,000', 'subt'),
             ('נכסים לא שוטפים: רכוש קבוע, נטו', '170,000', ''), ('סך נכסים', '320,000', 'tot')]
BS_SOURCES = [('התחייבויות שוטפות: ספקים', '38,000', ''), ('זכאים (לרבות משכורות לשלם)', '10,000', ''), ('הלוואה לזמן קצר', '20,000', ''), ('סך התחייבויות שוטפות', '68,000', 'subt'),
              ('התחייבויות לא שוטפות: הלוואה לזמן ארוך', '80,000', ''), ('סך התחייבויות', '148,000', 'subt'),
              ('הון עצמי: הון מניות', '100,000', ''), ('עודפים (רווחים שנצברו וטרם חולקו)', '72,000', ''), ('סך הון עצמי', '172,000', 'subt'), ('סך התחייבויות והון עצמי', '320,000', 'tot')]
PL_YUVAL = [('הכנסות ממכירות', '500,000', ''), ('עלות המכר', '(300,000)', ''), ('רווח גולמי', '200,000', 'subt'), ('הוצאות מכירה ושיווק', '(45,000)', ''), ('הוצאות הנהלה וכלליות', '(65,000)', ''),
            ('רווח תפעולי', '90,000', 'subt'), ('הוצאות מימון', '(12,000)', ''), ('רווח לפני מסים על ההכנסה', '78,000', 'subt'), ('מסים על ההכנסה', '(18,000)', ''), ('רווח נקי', '60,000', 'tot')]

# ================================================================ opening
SL.append(dict(id='s-title', title='פתיחה', kind='title', part=None, h='מבוא לחשבונאות ודיווח כספי', body='', cls='', kick=None))

S('s-about', 'מה נותן לנו המערך הזה', 'מה נותן לנו מערך השיעור',
  '<div class="row eq2 top">'
  + '<div class="card"><b class="ct">מה יש כאן</b><p class="lg">' + TX('מערך זה מתמצת את חומר המפגש הראשון, ומקנה את כל הדרוש לפתרון [[mamman|מטלת מנחה (ממ״ן)]] 1.') + '</p><ul class="lg"><li>תפקיד החשבונאות הפיננסית</li><li>מבנה הדוחות הכספיים וההגדרות היסודיות</li><li>בסיס הצבירה והזהות החשבונאית</li><li>' + TX('20 שאלות תרגול בסגנון המטלה, שנפתור יחד במהלך המפגש') + '</li><li>שאלות הכנה לאורך הדרך, ותרגול עצמי בסוף</li></ul></div>'
  + '<div class="card"><b class="ct">מה אין כאן</b><p class="lg">' + TX('במחברת הקורס המלאה תמצאו פירוט תיאורטי נרחב ותרגילים פתורים רבים נוספים.') + '</p><p class="lg"><b>' + TX('מערך זה אינו תחליף למחברת הקורס.') + '</b></p>'
  + DEF('מטלת מנחה, ממ״ן', 'מטלה שמגישים למנחה במהלך הסמסטר.', 'ממ״ן 1 כולל שאלות על החומר של מפגש זה.', trm='mamman') + '</div></div>'
  + PUN('נתחיל מהר במבוא, כדי להגיע לשאלות עם ראש צלול.'), kick='לפני שמתחילים')

S('s-sources', 'מקורות הלמידה בקורס', 'מקורות הלמידה בקורס',
  '<p class="lead">' + TX('ברמת התוכן הכתוב עומדים לרשותכם שלושה מקורות עיקריים:') + '</p>'
  + TABLE(['המקור', 'מה יש בו', 'מתי להשתמש', 'מעמד'], [
      ['<b>1. מערכי שיעור</b>', 'סיכומים תמציתיים ומוכווני מטרה, המתפרסמים אחרי כל שיעור (כדוגמת מערך זה). <b>בפורום היחידה המתאימה.</b>', 'מיד אחרי כל מפגש וכהכנה לממ״ן', 'ליבה'],
      ['<b>2. מחברת הקורס</b>', 'הרחבות תיאורטיות, ובעיקר דוגמאות ותרגילים פתורים רבים נוספים בכל נושא.', 'לפני המטלה, ובעיקר לפני הבחינה', 'ליבה'],
      ['<b>3. מדריך הלמידה</b>', 'מעין ספר לימוד באתר הקורס: מיקוד במושגים בצורה פורמלית, פחות בתרגול. <b>נמצא באתר תחת חומרי קריאה.</b>', 'העמקה והרחבה למעוניינים', 'רשות'],
  ], 'big') + BAND('note', 'בספרי הקורס (3 כרכים אדומים בחומרי קריאה) <b>אין צורך להשתמש</b>.'), kick='לפני שמתחילים')

ROUTE = [(1, 'מהי חשבונאות פיננסית', 'התפקיד, הקהל וההבחנה מניהולית', 'כ-5 דקות'),
         (2, 'הדוחות וההגדרות', 'ארבעה דוחות וחמישה מונחים', 'כ-10 דקות'),
         (3, 'תיעוד עסקאות', 'מקור ושימוש, 20 עסקאות ו-6 שאלות', 'כ-50 דקות'),
         (4, 'המאזן', 'מעסקאות למאזן, סיווג, הון ועודפים', 'כ-25 דקות'),
         (5, 'רווח והפסד', 'מדרג הרווחים, שורה אחר שורה', 'כ-15 דקות'),
         (6, 'בסיס הצבירה', 'מתי מכירים, מקדמות וריבית', 'כ-15 דקות'),
         (7, 'תרגול 7 עד 14', 'פתרון טענה אחר טענה', 'כ-35 דקות'),
         (8, 'תרגול 15 עד 20', 'פתרון, כולל שאלת העשרה', 'כ-25 דקות'),
         (9, 'תרגול עצמי', 'וריאציות בפורמט רב ברירה, לפני המטלה', 'עבודה עצמית')]
S('s-route', 'מסלול המפגש', 'מסלול המפגש',
  '<p class="lead">' + TX('רוב המפגש הוא תרגול: עסקאות ופתרון שאלות.' + (' לחצו על חלק כדי לעבור אליו.' if MODE == 'deck' else '')) + '</p><div class="route r5">'
  + ''.join(rcard(n, t, d, m, 's-flow' if n == 3 else f'p-{n}') for n, t, d, m in ROUTE) + '</div>', kick='מסלול המפגש')

# ================================================================ part 1
opener(1, 'מהי חשבונאות פיננסית ולמי היא מיועדת', 'שאלת החלק: מה מייצרת החשבונאות הפיננסית, ועבור מי?',
       ['הגדרות במהירות', 'שרשרת הדיווח הכספי', 'ההבחנה מחשבונאות ניהולית'], 5)

S('s-fin', 'מהי חשבונאות פיננסית', 'מהי חשבונאות פיננסית',
  RULE('הדוחות מספקים <b>מידע, לא המלצות</b>. ניתוח המידע וההחלטה מוטלים על המשתמש.')
  + TABLE(['מושג', 'בפשטות', 'דוגמה במספרים'], [
      ['<b>[[finacc|חשבונאות פיננסית]]</b>', 'מערכת לניתוח, תיעוד ובקרה של מידע כספי אודות ישות מדווחת', 'מכירות של 500,000 ש״ח מתועדות ומוצגות כהכנסות'],
      ['<b>[[entity|ישות מדווחת]]</b>', 'הגוף שעליו נערך הדיווח. אצלנו: חברה', 'חברת ״יובל״ בע״מ מדווחת על הכנסות של 500,000 ש״ח'],
      ['<b>[[fs|דוחות כספיים]]</b>', 'התוצר: דיווח שיטתי על המצב הכספי ועל תוצאות הפעילות', 'נכסים 320,000 ש״ח, רווח נקי 60,000 ש״ח'],
      ['<b>[[gpr|דיווח ״למטרות כלליות״]]</b>', 'מידע מצרפי, המיועד בראש ובראשונה לגורמים חיצוניים לחברה', 'אלפי מכירות מוצגות בשורה אחת: 500,000 ש״ח'],
      ['<b>[[alloc|הקצאת משאבים]]</b>', 'ההחלטה למי להעמיד כסף, ובאיזה היקף', 'בנק שוקל הלוואה של 200,000 ש״ח'],
      ['<b>[[users|משקיעים ומלווים]]</b>', 'משקיע רוכש חלק בבעלות. מלווה נותן אשראי ומצפה להחזר', 'מניות ב-50,000 ש״ח. הלוואה של 200,000 ש״ח'],
  ], 'tight') + CAP('ש״ח הם שקלים חדשים. בע״מ הוא בערבון מוגבל, צורת ההתאגדות של החברה.'), kick='חלק 1 · הגדרות')

_ic = lambda n, t: f'<span>{ICON(n, 40)}<br>{t}</span>'
S('s-chain', 'שרשרת הדיווח', 'שרשרת הדיווח הכספי: איך נוצר המידע ואת מי הוא משרת',
  FLOW([_ic('deal', 'עסקאות ואירועים כלכליים'), _ic('book', 'תיעוד שיטתי לפי הזהות החשבונאית'), _ic('doc', 'דוחות כספיים'), _ic('bank', 'החלטות משקיעים ומלווים: השקעה / אשראי')], rv=1)
  + ST(5, '<div class="demo"><b>דוגמה:</b> ' + TX('מכירה של 500 ש״ח נרשמת, מצטרפת לשורת ההכנסות בדוח, והבנק רואה אותה כשהוא בוחן הלוואה של 200,000 ש״ח.') + '</div>', cls='mt')
  + PUN('הדוח מספר מה קרה. הוא לא אומר מה לעשות.', 6), kick='חלק 1 · שרשרת הדיווח')

S('s-fm', 'פיננסית מול ניהולית', 'חשבונאות פיננסית מול [[mgr|חשבונאות ניהולית]]',
  '<p class="lead">' + TX('בקורס זה נעסוק רק בחשבונאות הפיננסית ובתוצריה. החשבונאות הניהולית היא לצורך ניהול.') + '</p>'
  + TABLE(['', 'חשבונאות פיננסית', 'חשבונאות ניהולית'], [
      ['<b>קהל היעד</b>', 'גורמים חיצוניים: משקיעים ומלווים', 'ההנהלה: צרכים פנימיים'],
      ['<b>כפיפות לכללים</b>', '[[rules|כללי דיווח אחידים ומחייבים]]', 'אינה כפופה לכללי דיווח חיצוניים'],
      ['<b>מטרה</b>', 'החלטות הקצאת משאבים לחברה', 'תמחור, תקצוב וניהול שוטף'],
      ['<b>תוצר</b>', 'דוחות כספיים תקופתיים והשוואתיים', 'דוחות פנימיים גמישים לפי הצורך'],
      ['<b>דוגמה</b>', 'הכנסות 2025: 500,000 ש״ח, לצד הכנסות 2024: 450,000 ש״ח', 'תקציב שיווק פנימי: 30,000 ש״ח. עלות מוצר 60 ש״ח, מחירו 100 ש״ח'],
  ], rv=1)
  + ST(6, '<b>למה כללים אחידים?</b> ' + TX('כי האחידות מאפשרת להשוות בין חברות ובין תקופות: עלות מכר של 300,000 ש״ח מול 450,000 ש״ח, מדודות באותו אופן.'), cls='band note'), kick='חלק 1 · השוואה')

PQ('fm', 'פיננסית או ניהולית', ['לפניכם מספר טענות:'],
   ['תקציב שיווק שההנהלה בונה לשנה הבאה הוא דוח של החשבונאות הפיננסית.',
    'בנק שבוחן מתן הלוואה של 500,000 ש״ח נשען על הדוחות הכספיים של החברה.',
    'דוחות פנימיים של ההנהלה אינם חייבים לעמוד בכללי דיווח חיצוניים.'],
   ['טענה 1 בלבד', 'טענה 2 בלבד', 'טענות 1 ו-3', 'טענות 2 ו-3', 'כל הטענות שגויות'], 3, 'טענות 2 ו-3 נכונות. תקציב הוא כלי פנימי, ושייך לחשבונאות הניהולית.',
   [('טענה 1', 'bad', ['תקציב הוא צורך פנימי של ההנהלה, ולכן שייך לחשבונאות הניהולית.']),
    ('טענה 2', 'ok', ['בנק הוא מלווה, גורם חיצוני. בשבילו נערכים הדוחות הכספיים.']),
    ('טענה 3', 'ok', ['חשבונאות ניהולית אינה כפופה לכללי דיווח חיצוניים, ולכן הדוחות גמישים.'])],
   'ד. טענות 2 ו-3.', name='שאלת הכנה', pun='שאלו תמיד: מי קורא את הדוח? בחוץ פיננסית, בפנים ניהולית.')

# ================================================================ part 2
opener(2, 'סט הדוחות הכספיים וההגדרות היסודיות', 'שאלת החלק: מה כולל סט הדוחות, ועל אילו חמישה מונחים הוא בנוי?',
       ['ארבעת הדוחות ומימד הזמן', 'חמשת המונחים שעליהם בנוי כל הדיווח', 'פריטים נפוצים, במספרים'], 10)

S('s-set', 'ארבעת הדוחות', 'סט הדיווח כולל ארבעה דוחות',
  '<p class="lead">' + TX('בשיעור זה נתמקד בשניים הראשונים.') + '</p>'
  + TABLE(['הדוח', 'מה הוא מציג', 'מימד הזמן', 'בקורס'], [
      ['<b>[[pl|דוח רווח והפסד]]</b>', 'תוצאות הפעילות: הכנסות והוצאות', 'לתקופת דיווח', 'שיעור זה'],
      ['<b>[[bs|הדוח על המצב הכספי]] (״המאזן״)</b>', 'נכסים מול מקורות המימון: התחייבויות והון עצמי', 'לנקודת זמן (31.12)', 'שיעור זה'],
      ['<b>[[cf|דוח על תזרימי המזומנים]]</b>', 'תקבולים ותשלומים בפועל לפי שוטפת / השקעה / מימון. למשל: נגבו 300,000 ש״ח (שוטפת), נרכשה מכונה ב-60,000 ש״ח (השקעה), התקבלה הלוואה של 200,000 ש״ח (מימון)', 'לתקופת דיווח', 'חטיבה 5'],
      ['<b>[[soe|דוח על השינויים בהון]]</b>', 'תנועות ברכיבי ההון העצמי. למשל: 150,000 ש״ח, ועוד רווח 60,000 ש״ח, פחות דיבידנד 8,000 ש״ח: 202,000 ש״ח', 'לתקופת דיווח', 'חטיבה 4'],
  ]), kick='חלק 2 · סט הדוחות')

S('s-dim', 'מימד הזמן', 'מימד הזמן: צילום מול סרט',
  ILLW(PHOTOFILM())
  + '<div class="row eq2 top mt">'
  + DEF('נקודת זמן', 'יום אחד מסוים. כך ערוך המאזן.', 'מזומן של 40,000 ש״ח ליום 31.12.2025.', 1, trm='point')
  + DEF('תקופת דיווח', 'פרק זמן שלם, בדרך כלל שנה קלנדרית. כך ערוך דוח רווח והפסד.', 'הכנסות של 500,000 ש״ח לשנת 2025.', 2, trm='period')
  + DEF('ביאורים', 'מידע נוסף והסברים נוספים למידע שבדוחות, מילולית וכמותית. הם חלק בלתי נפרד מהדיווח הכספי.', 'רכוש קבוע 170,000 ש״ח: מכונות 120,000 ש״ח וכלי רכב 50,000 ש״ח.', 3, trm='notes') + '</div>', kick='חלק 2 · הגדרה והדגמה')

S('s-asset', 'נכס', 'חמשת המונחים: נכס',
  RULE('חמשת המונחים שעליהם בנוי כל הדיווח הכספי. <b>ההגדרה היא המחייבת.</b> הדוגמאות להמחשה בלבד, ואינן רשימה ממצה.')
  + DEF('נכס', 'משאב בשליטת החברה, הנובע מאירועי עבר, אשר צפוי להניב לחברה הטבות כלכליות. אין להכיר בנכסים ״עתידיים״ שהזכאות להם טרם התגבשה.', 'מכונה שנרכשה ב-60,000 ש״ח היא נכס. הזמנה חתומה על מכירה של 60,000 ש״ח בשנה הבאה עדיין אינה נכס.', trm='asset')
  + '<div class="row eq2 top mt">'
  + DEF('הטבה כלכלית', 'תועלת כספית שהחברה צפויה לקבל.', 'חוב לקוח של 50,000 ש״ח צפוי להפוך למזומן.', 1, trm='benefit')
  + DEF('אירוע עבר', 'אירוע שכבר קרה עד מועד הדיווח.', 'המכונה נרכשה ב-1.3.2025.', 2, trm='pastev') + '</div>', kick='חלק 2 · ההגדרות היסודיות')

S('s-asset-i', 'דוגמאות לנכסים', 'נכסים: דוגמאות להמחשה בלבד',
  TABLE(['פריט', 'מה זה', 'דוגמה במספרים'], [
      [f'<b>{ICON("cash")}[[cash|מזומן]]</b>', 'כסף בקופה ובחשבון הבנק', '40,000 ש״ח בחשבון הבנק'],
      [f'<b>{ICON("doc")}[[ar|לקוחות]]</b>', 'חוב של לקוחות החברה כלפיה, למועד הדיווח', 'מכירה באשראי: יתרת לקוחות 50,000 ש״ח'],
      [f'<b>{ICON("box")}[[inv|מלאי]]</b>', 'פריטים בבעלות החברה, המיועדים למכירה במהלך העסקים הרגיל', 'סחורה במחסן בעלות 50,000 ש״ח'],
      [f'<b>{ICON("gear")}מכונות, {ICON("bldg")}מבנים</b>', 'פריטים שמשמשים את החברה בפעילותה לאורך זמן', 'מכונה בעלות 60,000 ש״ח'],
      [f'<b>{ICON("bank")}פיקדונות</b>', 'כסף שהופקד בבנק לתקופה קצובה', '30,000 ש״ח לשישה חודשים'],
      ['<b>ניירות ערך</b>', 'מניות ואגרות חוב שהחברה מחזיקה', 'מניות בשווי 20,000 ש״ח'],
      ['<b>[[stinv|השקעות לזמן קצר]]</b>', 'השקעות שמוחזקות לטווח קצר, ולכן נכס שוטף', 'מניות ב-20,000 ש״ח, למכירה בתוך חודשיים'],
  ]), kick='חלק 2 · ההגדרות היסודיות')

S('s-liab', 'התחייבות', 'חמשת המונחים: התחייבות',
  DEF('התחייבות', 'מחויבות קיימת של החברה, הנובעת מאירועי עבר שכבר התגבשו, אשר סילוקה צפוי להוביל ליציאה של הטבות כלכליות מהחברה.', 'חשמל של 5,000 ש״ח נצרך בדצמבר ולא שולם: התחייבות של 5,000 ש״ח.', trm='liab')
  + TABLE(['פריט', 'מה זה', 'דוגמה במספרים'], [
      ['<b>[[ap|ספקים]]</b>', 'חוב לספקים בגין סחורה או ציוד שנרכשו באשראי', 'רכישה באשראי: ספקים 38,000 ש״ח'],
      ['<b>[[accr|זכאים]]</b>', 'חובות שוטפים בגין שירותים שנצרכו', 'חשמל שטרם שולם: זכאים 5,000 ש״ח'],
      ['<b>[[wages|משכורות לשלם]]</b>', 'העובדים עבדו, והשכר טרם שולם', 'שכר דצמבר ישולם בינואר: 10,000 ש״ח'],
      ['<b>הלוואות</b>', 'כסף שהחברה קיבלה ועליה להחזיר', 'הלוואה מהבנק: 80,000 ש״ח'],
  ]).replace('class="tbl2 "', 'class="tbl2 " style="margin-top:12px"')
  + PUN('החתימה על חוזה היא רק דייט. ההתחייבות מתחילה כשהסחורה מגיעה.', 1), kick='חלק 2 · ההגדרות היסודיות')

S('s-eqty', 'הון עצמי', 'חמשת המונחים: הון עצמי',
  DEF('הון עצמי', 'הזכות השיורית בנכסי החברה לאחר ניכוי כל התחייבויותיה. <b>תמיד ולעולם סך ההון העצמי שווה לסך הנכסים בניכוי סך ההתחייבויות.</b>', '$172,000 = 320,000 - 148,000$: נכסים 320,000 ש״ח, התחייבויות 148,000 ש״ח.', trm='equity')
  + TABLE(['פריט', 'מה זה', 'דוגמה במספרים'], [
      ['<b>[[capital|הון מניות]]</b>', 'השקעת הבעלים: הערך הנקוב של המניות שהונפקו', '1,000 מניות בערך נקוב 1 ש״ח: 1,000 ש״ח'],
      ['<b>[[premium|פרמיה]]</b>', 'השקעת הבעלים: הסכום ששולם מעבר לערך הנקוב', 'מניה בערך נקוב 1 ש״ח נמכרה ב-3 ש״ח: פרמיה 2 ש״ח'],
      ['<b>[[re|עודפים]]</b>', 'רווח מצטבר: רווחים שנצברו וטרם חולקו', 'נצברו 90,000 ש״ח, חולקו 18,000 ש״ח: עודפים 72,000 ש״ח'],
  ]).replace('class="tbl2 "', 'class="tbl2 " style="margin-top:12px"'), kick='חלק 2 · ההגדרות היסודיות')

S('s-ie', 'הכנסה והוצאה', 'חמשת המונחים: הכנסה והוצאה',
  '<div class="row eq2 top">'
  + DEF('הכנסה', 'הערך הכספי של פעילות עסקית יוצרת ערך, מכר או מתן שירות, במועד ביצועה, ללא תלות בעיתוי קבלת המזומן.', 'שירות של 80,000 ש״ח ניתן השנה, ונגבו 30,000 ש״ח. ההכנסה: 80,000 ש״ח.', trm='rev')
  + DEF('הוצאה', 'הערך הכספי של משאבים או שירותים שנצרכו בתקופה, במועד צריכתם, ללא תלות בעיתוי התשלום בפועל.', 'חשמל של 5,000 ש״ח נצרך בדצמבר 2025 וישולם בינואר 2026. ההוצאה ב-2025.', trm='exp') + '</div>'
  + TABLE(['פריט', 'דוגמה במספרים'], [
      ['<b>הכנסות ממכירות, הכנסות משירותים</b>', 'נמכרו מוצרים ב-500,000 ש״ח. ניתן ייעוץ ב-80,000 ש״ח'],
      ['<b>הוצאות שכר, חשמל, שכירות</b>', 'שכר 120,000 ש״ח. שכירות 3,000 ש״ח לחודש: 36,000 ש״ח לשנה'],
      ['<b>[[dep|פחת]]</b>: הקטנה שיטתית של עלות נכס על פני שנות השימוש בו', 'מכונה ב-100,000 ש״ח ל-10 שנים: 10,000 ש״ח לשנה'],
  ]).replace('class="tbl2 "', 'class="tbl2 " style="margin-top:12px"'), kick='חלק 2 · ההגדרות היסודיות')
