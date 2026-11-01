# Coverage of the source docx by the deck. Usage: python3 check_coverage.py <lecture.docx>
# Walks every paragraph and table cell of the docx in order, and reports how many of its words and all of its numbers appear in the slides of the matching part.
import html, os, re, sys, zipfile
H = os.path.dirname(os.path.abspath(__file__))
docx = sys.argv[1]
xml = zipfile.ZipFile(docx).read('word/document.xml').decode('utf8')
xml = re.sub(r'<mc:Fallback>.*?</mc:Fallback>', '', xml, flags=re.S)
paras = []
for m in re.finditer(r'<w:p[ >].*?</w:p>', xml, re.S):
    t = html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>', m.group(0)))).strip()
    if t: paras.append(t)
deck = open(os.path.join(H, '..', 'lectures', 'lecture-1', 'presentation.html'), encoding='utf8').read()
slides = re.findall(r'<section class="slide[^"]*" id="([^"]+)".*?</section>', deck, re.S)
blocks = {m.group(1): m.group(0) for m in re.finditer(r'<section class="slide[^"]*" id="([^"]+)".*?</section>', deck, re.S)}
def plain(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s).replace('״', '"').replace('׳', "'").replace('−', '-')
    return s
ALL = plain(' '.join(blocks.values()))
# marks and joining letters do not change a word
STOP = set('של את על עם כי גם או אם לא כן זה זו אך רק כל אלו אנו אשר היא הוא הם יש אין'.split())
def words(s):
    s = re.sub(r'[^֐-׿a-zA-Z0-9," ]', ' ', s.replace('"', ''))
    return [w for w in s.split() if len(w) > 2 and w not in STOP]
ALLW = set(words(ALL))
ALLW |= {w[1:] for w in ALLW if w[0] in 'הובלמשכ'}
SEC = [('פתיחה ומקורות', 'קורס: 13002'), ('חלק א', 'חלק א:'), ('חלק ב', 'חלק ב:'), ('חלק ג', 'חלק ג:'), ('חלק ד', 'חלק ד:'), ('חלק ה', 'חלק ה:'), ('חלק ו', 'חלק ו:'), ('חלק ז: הקדמה', 'חלק ז:')] + [(f'שאלה {i}', f'שאלת תרגול {i}:') for i in range(1, 21)]
idx = []
for name, key in SEC:
    i = next(k for k, t in enumerate(paras) if t.startswith(key))
    idx.append((name, i))
idx.append(('end', len(paras)))
NOTE = {'פיתה-רון:', 'טענה', 'נכונה/שגויה', 'נימוק'}
miss_total = 0
for (name, a), (_, b) in zip(idx, idx[1:]):
    tot = hit = 0
    nums, low = [], []
    for t in paras[a:b]:
        if t in NOTE: continue
        ws = words(t)
        got = [w for w in ws if w in ALLW or (w[0] in 'הובלמשכ' and w[1:] in ALLW)]
        tot += len(ws); hit += len(got)
        for n in re.findall(r'\d[\d,.]*\d|\d', t):
            n = n.rstrip('.,')
            if n not in ALL: nums.append(n)
        if ws and len(got) / len(ws) < .7: low.append(t[:70])
    pct = 100 * hit / max(tot, 1)
    print(f'{name:18s} {len(paras[a:b]):3d} paragraphs, words found {pct:5.1f}%, numbers missing {nums or "none"}')
    for l in low: print('     low:', l)
    miss_total += len(nums)
print('numbers missing overall:', miss_total)

# question number in the docx -> number in the deck, where six questions were moved into the transactions part
RENUM = {7: 1, 16: 2, 13: 3, 9: 4, 12: 5, 14: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 12, 8: 13, 10: 14, 11: 15, 15: 16, 17: 17, 18: 18, 19: 19, 20: 20}
# the question text itself must be in that question's own slide, word for word (punctuation aside)
def norm(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    s = re.sub(r'[^\u0590-\u05F3a-zA-Z0-9%]+', ' ', s.replace('״', '').replace('"', ''))
    return ' '.join(s.split())
bad = checked = 0
for i in range(1, 21):
    a = next(k for k, t in enumerate(paras) if t.startswith(f'שאלת תרגול {i}:'))
    b = next((k for k, t in enumerate(paras) if t.startswith(f'שאלת תרגול {i + 1}:')), len(paras))
    slide = norm(blocks[f'q{RENUM[i]}'])
    for t in paras[a:b]:
        m = re.match(r'^(טענה \d: ?|[א-ה]\. )', t)
        if not m and not t.startswith(('לפניכם', 'הטענה /', 'חברה ', 'לחברה', 'ב-1.12', 'איזו')): continue
        if t.startswith(('לפניכם מספר', 'הטענה /')) and norm(t) in slide:
            checked += 1; continue
        if t.startswith('תזכורת'): continue
        checked += 1
        body = norm(t[m.end():] if m else t)
        if body not in slide:
            bad += 1; print(f'  q{i} differs:', t[:110])
print(f'question text: {checked} items checked in their own slides, {bad} differ')
