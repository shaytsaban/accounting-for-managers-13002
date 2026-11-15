# Lesson 1 deck. Run: python3 build_deck.py  ->  ../lectures/lecture-1/presentation.html
import os, re, json, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
R = lambda f: open(os.path.join(H, f), encoding='utf8').read()
MODE = 'deck'
LESSON = int(os.environ.get('LESSON', '1'))
FILES = {1: ('frame.py', 'content_a.py', 'content_t.py', 'content_b.py', 'content_c.py'), 2: ('frame.py', 'xl.py', 'l2_a.py', 'l2_b.py', 'l2_c.py'), 3: ('frame.py', 'xl.py', 'l3_a.py', 'l3_b.py', 'l3_c.py')}
for f in FILES[LESSON]:
    exec(R(f))

SEC = '<span class="n">2027</span>א'


def render(s, total):
    k = s['kind']
    if k == 'title':
        return (f'<section class="slide dark s1 on" id="s-title" data-title="פתיחה">'
                '<div class="orb" style="width:320px;height:320px;background:radial-gradient(circle at 30% 30%,#58e0cf,#0f9d90 60%,transparent 72%);left:-90px;top:-70px"></div>'
                '<div class="orb" style="width:180px;height:180px;background:radial-gradient(circle at 30% 30%,#ffd37a,#e8960c 60%,transparent 72%);left:230px;bottom:90px;animation-delay:-3s"></div>'
                '<div style="position:absolute;right:70px;top:84px;width:880px">'
                f'<div class="kick" style="color:#ffb199"><span>{COURSE} · האוניברסיטה הפתוחה · {TX(f"קורס 13002 · מפגש {LESSON}")}</span></div>'
                f'<h1><span>{META["h1a"]}</span> <span style="color:#7fe3d6">{META["h1b"]}</span></h1>'
                '<p class="sub" style="margin-top:20px;font-size:27px;color:#c8d4f2">' + TX(META['sub']) + '</p>'
                '<div class="chipbar" style="margin-top:24px">' + ''.join(f'<span class="chip">{TX(c.format(**CNT))}</span>' for c in META['chips']) + '</div></div>'
                f'<div style="position:absolute;right:70px;bottom:58px;font-size:22px;color:#c8d4f2"><b style="color:#fff">מרכז ההוראה: ד״ר שי צבאן</b> · סמסטר {SEC}</div></section>')
    if k == 'end':
        return ('<section class="slide dark s1" id="s-end" data-title="סיום"><div style="position:relative;max-width:980px;margin-top:110px">'
                '<div class="kick" style="color:#ffb199">' + TX(f'סוף מפגש {LESSON}') + '</div>'
                f'<h1 style="font-size:60px">{NEXT_H}</h1>'
                f'<p class="sub" style="font-size:25px;margin-top:20px;color:#c8d4f2;max-width:940px">{TX(NEXT_P)}</p>'
                '<p class="sub" style="font-size:22px;margin-top:26px;color:#c8d4f2">שאלות ותיקונים: <span dir="ltr">Shay.tsaban@gmail.com</span></p></div></section>')
    if k == 'opener':
        if s.get('hidden'): return ''
        n = s['part']
        when = f'לעבודה עצמית · כ-{s["mins"]} דקות' if s.get('selfp') else f'כ-{s["mins"]} דקות'
        note = f'<div class="pd-note">{TX(s["note"])}</div>' if s.get('note') else ''
        return (f'<section class="slide dark pd" id="{s["id"]}" data-title="{s["title"]}" style="--pc:#7fe3d6"><div class="pd-num{" w" if n >= 10 else ""}">{n}</div><div class="pd-in">'
                f'<div class="kick" style="color:#ffb199"><span>חלק <span class="n">{n}</span> מתוך <span class="n">{total}</span> · {TX(when)}</span></div><div class="pd-h">{s["h"]}</div><div class="pd-q">{TX(s["q"])}</div>{note}'
                f'<div class="pd-cols"><div class="pd-box"><b>מה נעשה בחלק הזה</b><ul>{"".join("<li>" + TX(x) + "</li>" for x in s["learn"])}</ul></div></div></div></section>')
    kick = f'<div class="kick"><span>{TX(s["kick"])}</span></div>' if s.get('kick') else ''
    return f'<section class="slide {s["cls"]}" id="{s["id"]}" data-title="{re.sub("<[^>]+>", "", s["title"])}">{kick}<h2>{TX(s["h"])}</h2>{s["body"]}</section>'


NCALC = sum(1 for s in SL if s['id'].startswith('c-'))
NPREP = sum(s['id'].startswith('h-') and 'id="pq-h-' in s['body'] for s in SL if 'c2' not in s['id'])
NSELF = sum(s['id'].startswith('h-v') and 'class="mc"' in s['body'] for s in SL)
NPREP -= NSELF
NEXT_H, NEXT_P = META['next_h'], META['next_p']
NCHK = sum(s['body'].count('class="ansb"') for s in SL)
CNT = dict(NX=globals().get('NX', [0])[0], NPREP=NPREP, NSELF=NSELF, NCALC=NCALC, NCHK=NCHK, NMC=sum(s['body'].count('class="mc"') for s in SL))
slides_html = '\n'.join(filter(None, (render(s, TOTAL_PARTS) for s in SL)))

fonts = R('shell/fonts.css')
base = R('shell/base.css')
tail = R('shell/tail.html')
gj = json.dumps(G, ensure_ascii=False)
js = f'const COURSE={json.dumps(COURSE, ensure_ascii=False)};const LESSON={LESSON};\nconst G={gj};\n' + R('deck.js') + '\n' + R('calcs.js') + ('\n' + R('xlengine.js') + '\n' + R('live.js') if LESSON >= 2 else '')
title = f'{COURSE} | שיעור {LESSON} | {META["title"]}'
html = (f'<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>{title}</title>\n<style>\n'
        + fonts + base + R('deck.css') + (R('live.css') if LESSON >= 2 else '') + '</style>\n</head>\n<body>\n<div class="stage" id="stage">\n' + slides_html + '\n' + tail
        + '<script>\n(function(){\n' + js + '\n})();\n</script>\n</body>\n</html>\n')

for bad in ('—', '־'):
    assert bad not in html, 'forbidden character ' + bad
out = os.path.join(H, '..', 'lectures', f'lecture-{LESSON}')
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'presentation.html'), 'w', encoding='utf8').write(html)

# every class used in the markup or in the scripts needs a CSS rule
css = fonts + base + R('deck.css') + R('live.css')
used = set()
for m in re.finditer(r'class="([^"]+)"', slides_html + tail + R('deck.js') + R('calcs.js') + R('live.js')):
    for c in m.group(1).split():
        if re.fullmatch(r'[\w-]+', c): used.add(c)
missing = sorted(c for c in used if not re.search(r'\.' + re.escape(c) + r'(?![\w-])', css))
print('slides', html.count('<section class="slide'), 'calcs', NCALC, 'prep', NPREP, 'self', NSELF, 'bytes', len(html))
print('classes without a rule:', missing)
