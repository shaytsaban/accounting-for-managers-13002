# Lesson 1 summary PDF. Run: python3 build_summary.py  ->  ../lectures/lecture-1/summary.pdf (David font, printed by headless Chrome)
import os, re, shutil, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
R = lambda f: open(os.path.join(H, f), encoding='utf8').read()
MODE = 'pdf'
for f in ('content_a.py', 'content_t.py', 'content_b.py', 'content_c.py'):
    exec(R(f))
FONTS = os.path.join(H, '..', '..', 'iit-build', 'fonts')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CSS = '''
@font-face{font-family:"David";src:url("david.ttf");font-weight:400}
@font-face{font-family:"David";src:url("davidbd.ttf");font-weight:700}
@page{size:A4;margin:15mm 15mm 15mm 15mm;@bottom-center{content:counter(page);font-family:"David";font-size:10pt;color:#5d6a86}}
@page:first{margin:0;@bottom-center{content:none}}
:root{--ink:#16213a;--navy:#1b2d55;--coral:#ff6a4d;--mut:#5d6a86;--line:#d9d2c3;--inc:#25a65f}
*{box-sizing:border-box}
html{direction:rtl}
body{font-family:"David";font-size:11.6pt;line-height:1.3;color:var(--ink);margin:0}
.cover{height:297mm;width:210mm;padding:42mm 24mm 24mm;background:linear-gradient(160deg,#0f1b33 0%,#1b2d55 60%,#27447f 100%);color:#fff;position:relative;break-after:page;text-align:right;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.c-top{font-size:17pt;color:#7fe3d6;font-weight:700}
.c-title{font-size:40pt;line-height:1.15;margin:14mm 0 4mm;font-weight:700}
.c-sub{font-size:19pt;color:#d6e0f7;line-height:1.35}
.c-line{width:60mm;height:3mm;background:var(--coral);margin:12mm 0;border-radius:2mm}
.c-meta{font-size:14pt;color:#c8d4f2;line-height:1.5}
.c-author{position:absolute;right:24mm;bottom:28mm}
.c-name{font-size:20pt;font-weight:700}
.c-mail{font-size:14pt;color:#c8d4f2;text-align:right}
.toc h1{margin-top:0}
.toc ol{columns:2;line-height:1.45;margin:0 0 3mm;padding-right:6mm}
section.part{margin-top:6mm}
h1{font-size:17pt;color:var(--navy);margin:0 0 2.5mm;padding-bottom:1.5mm;border-bottom:.8mm solid var(--coral);font-weight:700;break-after:avoid}
h1 .sn{display:inline-block;background:var(--navy);color:#fff;border-radius:50%;width:9mm;height:9mm;line-height:9mm;text-align:center;margin-left:3mm;font-size:12.5pt;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.pq{font-weight:700;color:#2a3858;margin:0 0 1mm}
.pl{margin:0 0 2mm;padding-right:6mm}
h3{font-size:12.6pt;color:var(--navy);margin:3.4mm 0 1mm;font-weight:700;break-after:avoid}
p{margin:0 0 1.2mm}
*{-webkit-print-color-adjust:exact;print-color-adjust:exact}
.n,.m{direction:ltr;unicode-bidi:isolate}
.m{white-space:nowrap;font-weight:700}
.mh{unicode-bidi:isolate;direction:rtl}
span.term{font-weight:inherit}
sup,sub{font-size:.68em;line-height:0}
.eq{direction:ltr;text-align:right;font-size:12.2pt;margin:1mm 0;white-space:nowrap}
.eq.big{font-size:13pt}.eq.fit{font-size:11.6pt}.eq.c{text-align:center}
.frac{display:inline-flex;flex-direction:column;align-items:center;vertical-align:middle;line-height:1.1;margin:0 .6mm;font-size:.92em}
.frac>span{padding:0 1.2mm;white-space:nowrap}
.frac>span:first-child{border-bottom:.3mm solid currentColor}
.row{display:flex;gap:3mm}.row.eq2>*,.row.eq3>*{flex:1 1 0;min-width:0}
.col{display:block}
.fg{display:grid;grid-template-columns:1fr 1fr;gap:2mm}
.card{border:.25mm solid var(--line);border-radius:1.6mm;padding:1.6mm 2.4mm;margin:0 0 1.6mm;break-inside:avoid;background:#fff}
.def p,.fm p{margin:.4mm 0}
.dn,.fm b,.ct{display:block;font-weight:700;color:var(--navy)}
.ct{color:#c4421f}
.demo{background:#eef7f6;border-radius:1.2mm;padding:.8mm 2mm;margin-top:.8mm}
.demo b{color:#087469}
.band{border-radius:1.2mm;padding:1.2mm 2.6mm;margin:1.2mm 0;background:#f1ece0;break-inside:avoid}
.band.dg{background:#fff7e0;border-right:1.2mm solid #f0b429}
.band.note{background:#eef2ff;border-right:1.2mm solid var(--navy)}
.band.trap{background:#fde8e6;border-right:1.2mm solid #e0454f}
.band.ans{background:#dcf5e6;border-right:1.2mm solid var(--inc);font-weight:700}
.tlw{margin:1.2mm 0;text-align:center;break-inside:avoid}
.card.tlw{padding:1mm 2mm}
.tl{display:block;margin:0 auto;width:112mm;max-width:100%;height:auto;direction:ltr;unicode-bidi:isolate;font-family:"David"}
.tl[viewBox^="0 0 1120"]{width:178mm}
.qstem{font-weight:700;margin-bottom:1mm}
.qstem p{margin:0 0 .6mm}
.sp{margin:0 0 1mm}
.cap{font-size:10pt;color:var(--mut);text-align:center;margin:.4mm 0 0}
.lead{margin:0 0 1.2mm}
.lg{margin:0}
ul.lg,.pl{padding-right:6mm}
table.tbl2{width:100%;border-collapse:collapse;margin:1mm 0 2mm;font-size:10.8pt}
.tbl2 th{background:var(--navy);color:#fff;text-align:right;padding:.9mm 2mm;font-weight:700}
.tbl2 td{padding:.8mm 2mm;border-bottom:.25mm solid var(--line);vertical-align:middle}
tr{break-inside:avoid}
.steps{margin:0 0 1.5mm;padding-right:6mm}
.steps li{margin-bottom:.6mm}
.steps li>span>b{color:#c4421f}
.steps.two{columns:2;column-gap:6mm}
.steps.two li{break-inside:avoid}
.route{display:grid;gap:1.5mm;margin-bottom:1.5mm}
.rcard{display:block;border:.25mm solid var(--line);border-radius:1.4mm;background:#fff;padding:1mm 1.6mm;text-align:right;font:inherit;font-size:10pt;color:inherit;line-height:1.2}
.rcard .n{display:inline;font-weight:700;color:#c4421f;margin-left:1mm}
.rcard b{display:inline}
.rcard span{display:block}
.rcard em{display:block;font-style:normal;color:#087469;font-weight:700}
.stt{font-weight:700;color:var(--navy);margin:1mm 0 .8mm}
.stmt{width:100%;border-collapse:collapse;font-size:10.8pt;margin:0 0 1.5mm}
.stmt td{padding:.5mm 2mm;border-bottom:.2mm solid var(--line);line-height:1.2}
.stmt td.amt{text-align:left;white-space:nowrap;width:24mm}
.stmt tr.h td{background:#f1ece0;font-weight:700}
.stmt tr.subt td{background:#e6edf8;font-weight:700}
.stmt tr.tot td{background:#dcf5e6;font-weight:700}
.ident{display:flex;direction:ltr;align-items:stretch;justify-content:center;gap:2mm;margin:1mm 0}
.ibox{flex:1 1 0;border-radius:1.4mm;padding:1mm 2mm;text-align:center;direction:rtl}
.ibox b{display:block;font-size:12pt}
.ibox small{display:block;font-size:9.6pt}
.ibox .n{display:block;font-weight:700}
.iop{align-self:center;font-size:15pt;font-weight:700}
.c-asset{background:#dff5f2;color:#087469}.c-liab{background:#ece8ff;color:#4f33c9}.c-eq{background:#fff0d2;color:#a86703}
.flowx{display:flex;align-items:stretch;gap:1.2mm;margin:1mm 0 1.5mm}
.fnode{flex:1 1 0;border:.25mm solid var(--line);border-radius:1.4mm;padding:1mm 1.4mm;text-align:center;font-size:10.6pt;line-height:1.2;display:flex;align-items:center;justify-content:center}
.farr{align-self:center;font-weight:700;color:#c4421f}
.stair{margin:0 12mm 1.5mm;text-align:center;break-inside:avoid}
.stair .sl{border:.25mm solid var(--line);border-radius:1.2mm;padding:.4mm 2mm;font-weight:700;background:#fff}
.stair .sl.net{background:#dcf5e6}.stair .sl.bs{background:#fff0d2}
.stair .sd{font-size:10.4pt;line-height:1.2;padding:.2mm 0}
.dec{display:grid;grid-template-columns:.8fr auto 1fr;gap:2mm;align-items:center;margin:1mm 0;break-inside:avoid}
.dq{background:var(--navy);color:#fff;border-radius:1.4mm;padding:2mm;text-align:center;font-weight:700}
.dbr{display:block}
.da{background:#dcf5e6;border-radius:1.2mm;padding:1mm 2mm;margin-bottom:1mm}
.da.no{background:#fde3e5}
.yr{display:grid;grid-template-columns:1fr auto 1fr;gap:2mm;align-items:center}
.yr .card b{display:block;color:var(--navy)}
.clm{display:grid;grid-template-columns:19mm 1fr;gap:2mm;border:.25mm solid var(--line);border-radius:1.4mm;padding:1mm 2mm;margin:0 0 1.2mm;break-inside:avoid}
.clm .tg{font-weight:700;color:var(--navy)}
.clm .vd{display:inline-block;font-size:9.8pt;font-weight:700;padding:0 1.6mm;border-radius:2mm;background:#eee}
.clm .vd.ok{background:#dcf5e6;color:#167a43}
.clm .vd.bad{background:#fde3e5;color:#b3262f}
.clm .bd p{margin:0 0 .5mm}
.band.ans{margin-bottom:2mm}
.route.r4{grid-template-columns:repeat(4,1fr)}
.mt{margin-top:1.4mm}
.ic{display:inline-block;vertical-align:-1mm;margin-left:1mm;width:5mm;height:5mm}
.ill{display:block;width:150mm;max-width:100%;height:auto;margin:1mm auto;font-family:"David";direction:ltr;unicode-bidi:isolate}
.illw{break-inside:avoid;margin:1mm 0}
.rule{background:var(--navy);color:#fff;border-radius:1.2mm;padding:1.1mm 2.6mm;margin:1.2mm 0;font-weight:700;break-inside:avoid}
.rule b{color:#ffb199}
.rule .m{color:#fff}
.prin{margin:0 0 1.5mm;padding-right:6mm;font-weight:700}
.prin li{margin-bottom:.5mm}
.ttw{border:.25mm solid var(--line);border-radius:1.4mm;padding:1mm 1.6mm;margin:1mm 0;break-inside:avoid}
.clm .ttw{border:0;padding:.4mm 0;margin:.5mm 0}
.tth{font-weight:700;color:var(--navy);margin-bottom:.6mm}
.tt{width:100%;border-collapse:collapse;font-size:10.6pt;table-layout:fixed}
.tt th{padding:.3mm 1mm;text-align:center;font-weight:700}
.tt th.ta{background:#dff5f2;color:#087469}.tt th.tb{background:#ece8ff;color:#4f33c9}.tt th.tc{background:#fff0d2;color:#a86703}
.tt td{padding:.4mm 1mm;text-align:center;vertical-align:top;line-height:1.2}
.tt td.ta{background:#f1fbf9}.tt td.tb{background:#f6f4ff}.tt td.tc{background:#fff9ec}
.tt .op{width:5mm;background:none;font-weight:700;vertical-align:middle}
.tt span.li{display:block}
.tt small{display:block;font-size:9.4pt;color:var(--mut)}
.tt span.no{color:var(--mut)}
.txev{font-weight:700;color:var(--navy);margin:0 0 .6mm}
.txb{margin:.6mm 0;padding-right:5mm}
.txb li{margin-bottom:.3mm}
.ka{color:#087469}.kb{color:#4f33c9}.kc{color:#a86703}
.txsu{display:flex;justify-content:space-between;gap:3mm;font-size:10.6pt;background:#f1ece0;border-radius:1.2mm;padding:.5mm 2mm;margin-bottom:1mm;break-inside:avoid}
.tt tr.cum td{border-top:.3mm solid var(--line);font-weight:700}
.ttc{font-size:10pt;color:var(--mut);text-align:center;margin-top:.5mm}
.ttg{display:grid;grid-template-columns:1fr 1fr;gap:1.5mm}
.ttg .ttw{margin:0}
.dbr>.dec{background:#f6f2ea;border-radius:1.2mm;padding:.6mm}
.dec.sm .dq{padding:1mm;font-size:10.6pt}
.dec.sm .da{padding:.6mm 1.4mm;font-size:10.6pt;margin-bottom:.6mm}
.lab{font-weight:700}
.pun{font-weight:700;color:#b8391f;margin:1mm 0;padding-right:2.4mm;border-right:1mm solid var(--coral);break-inside:avoid}
.toon{text-align:center;border:.25mm solid var(--line);border-radius:1.4mm;padding:1mm;break-inside:avoid}
.tn{display:block;width:38mm;height:auto;margin:0 auto;direction:ltr;unicode-bidi:isolate}
.toon .tc{font-weight:700;color:#b8391f;font-size:10.6pt}
.toonr{display:grid;grid-template-columns:1fr 44mm;gap:2mm;align-items:start}
.pita{display:block;width:34mm;margin:0 auto;border-radius:1mm}
.clm .hd{display:block}
.clm .hd .vd{margin-top:.5mm}
.route.r5{grid-template-columns:repeat(5,1fr)}
.mcrow{display:grid;grid-template-columns:1fr 1fr;gap:2mm}
.mcrow.n3{grid-template-columns:1fr 1fr 1fr}
.mcrow.n3 .mc{font-size:10.8pt}
.mc{border:.25mm solid var(--line);border-radius:1.6mm;padding:1.4mm 2.2mm;break-inside:avoid;margin-bottom:1.5mm}
.mc .q{font-weight:700;margin-bottom:.6mm}
.mc button.o{display:block;width:100%;border:0;background:none;font:inherit;color:inherit;text-align:right;padding:0;margin:.1mm 0}
.mc button.o.correct{font-weight:700;color:#107c41}
.mc .w{background:#eef2ff;border-radius:1.2mm;padding:.8mm 2mm;margin-top:.8mm}
.alts{list-style:none;padding:0;margin:.6mm 0;font-weight:400}
.alt .eq{text-align:center}
.calcp{background:#f4f1ff;border-right:1.2mm solid #6d4df2;border-radius:1.2mm;padding:1.2mm 2.6mm;margin:1mm 0;break-inside:avoid}
.glc{columns:2;column-gap:5mm}
.gl{border-right:1mm solid var(--coral);padding:.6mm 2.2mm;margin:0 0 1.6mm;break-inside:avoid;font-size:10.6pt;line-height:1.25}
.gl .th{font-weight:700;color:var(--navy);font-size:11.4pt}
.gl small{font-weight:400;color:var(--mut);direction:ltr;unicode-bidi:isolate;margin-right:1.5mm;font-size:9.6pt}
.gl p{margin:0 0 .3mm}
'''
parts = {}
for s in SL:
    parts.setdefault(s['part'], []).append(s)
body = ''
for s in parts[None]:
    pass
front = ''.join(f'<h3>{TX(s["h"])}</h3>{s["body"]}' for s in SL if s['kind'] == 'slide' and s['part'] is None)
body += f'<section class="part"><h1>לפני שמתחילים</h1>{front}</section>'
for n in range(1, TOTAL_PARTS + 1):
    op = next(s for s in parts[n] if s['kind'] == 'opener')
    inner = f'<p class="pq">{TX(op["q"])}</p>' + (f'<p>{TX(op["note"])}</p>' if op.get('note') else '') + '<ul class="pl">' + ''.join(f'<li>{TX(x)}</li>' for x in op['learn']) + '</ul>'
    for s in parts[n]:
        if s['kind'] == 'opener': continue
        h = f'<h3>{TX(s["h"])}</h3>'
        inner += h + s['body']
    body += f'<section class="part"><h1><span class="sn">{n}</span>{op["h"]}</h1>{inner}</section>'
gl = ''.join(f'<div class="gl"><div class="th">{g["h"]}<small>{g["en"]}</small></div><p><b>בפשטות:</b> {g["p"]}</p><p><b>בלשון מקצועית:</b> {g["f"]}</p><p><b>דוגמה:</b> {g["ex"]}</p><p><b>שימו לב:</b> {g["tr"]}</p></div>' for g in G.values())
body += f'<section class="part"><h1>מילון מושגים</h1><div class="glc">{gl}</div></section>'
body += '<section class="part"><h1>במפגש הבא: נכסים שוטפים</h1><p>' + TX('לקוחות, מלאי והשקעות למסחר: שלושה נכסים שוטפים, מהותם והשפעתם על הדיווח.') + '</p></section>'
cover = (f'<div class="cover"><div class="c-top">{COURSE} · האוניברסיטה הפתוחה · {TX("קורס 13002 · מפגש 1")}</div><div class="c-title">מבוא לחשבונאות ודיווח כספי</div>'
         '<div class="c-sub">סיכום מלא של השיעור: תפקיד החשבונאות הפיננסית, הדוחות הכספיים, בסיס הצבירה והזהות החשבונאית.</div><div class="c-line"></div>'
         '<div class="c-meta">' + TX('20 שאלות תרגול, שאלות הכנה ותרגול עצמי, עם פתרונות מלאים, דוחות כספיים במספרים ומילון מושגים.') + '<br>סמסטר <span dir="ltr">2027</span>א</div>'
         '<div class="c-author"><div class="c-name">מרכז ההוראה: ד״ר שי צבאן</div><div class="c-mail" dir="ltr">Shay.tsaban@gmail.com</div></div></div>')
toc = '<div class="toc"><h1>תוכן העניינים</h1><ol>' + ''.join(f'<li>{parts[n][0]["h"]}</li>' for n in range(1, TOTAL_PARTS + 1)) + '</ol></div>'
page = f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>{COURSE} | שיעור 1 | סיכום</title><style>{CSS}</style></head><body>{cover}{toc}{body}</body></html>'
for bad in ('—', '־'):
    assert bad not in page, bad
d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
for f in ('david.ttf', 'davidbd.ttf'):
    shutil.copy(os.path.join(FONTS, f), d)
p = os.path.join(d, 'summary.html')
open(p, 'w', encoding='utf8').write(page)
out = os.path.abspath(os.path.join(H, '..', 'lectures', 'lecture-1', 'summary.pdf'))
subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/p', '--no-pdf-header-footer', '--virtual-time-budget=8000', f'--print-to-pdf={out}', 'file://' + p], capture_output=True, timeout=180)
shutil.rmtree(d, ignore_errors=True)
import fitz
doc = fitz.open(out)
txt = ''.join(pg.get_text() for pg in doc)
print('pages', len(doc), 'bytes', os.path.getsize(out), 'fonts', sorted({f[3].split('+')[-1] for pg in doc for f in pg.get_fonts()}))
print('em dash', '—' in txt, 'maqaf', '־' in txt)
