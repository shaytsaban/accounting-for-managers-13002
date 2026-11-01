# Keeps the deck from reproducing a graded assignment. Usage: python3 check_assignment.py <assignment.pdf>
# The assignment itself stays out of this repo. Reports near-copy sentences and slides that share several of a question's figures.
import difflib, html, os, re, sys
import fitz
H = os.path.dirname(os.path.abspath(__file__))
doc = fitz.open(sys.argv[1])
raw = '\n'.join(p.get_text() for p in doc)
def norm(s):
    s = re.sub(r'[^֐-׳a-zA-Z0-9%]+', ' ', html.unescape(s).replace('״', '').replace('"', ''))
    return ' '.join(s.split())
# one item per claim, option or stem: pdf lines are joined until a line ends a sentence
items, buf = [], ''
for ln in raw.split('\n'):
    ln = ln.strip()
    if not ln: continue
    buf += ' ' + ln
    if re.search(r'^[.?:]|[.?:]$', ln) or re.match(r'^[א-ה]\. ', ln):
        t = norm(buf); buf = ''
        if len(t) > 30: items.append(t)
deck = open(os.path.join(H, '..', 'lectures', 'lecture-1', 'presentation.html'), encoding='utf8').read()
blocks = {m.group(1): m.group(0) for m in re.finditer(r'<section class="slide[^"]*" id="([^"]+)".*?</section>', deck, re.S)}
sents = []
for sid, b in blocks.items():
    for part in re.split(r'</p>|</button>|</td>|</li>|</div>', b):
        t = norm(re.sub(r'<[^>]+>', ' ', part))
        t = re.sub(r'^(טענה \d |[א-ה] )', '', t)
        if len(t) > 25: sents.append((sid, t))
hits = []
for it in items:
    body = re.sub(r'^(\d+ )?(טענה \d? ?)?', '', it)
    best = max(sents, key=lambda s: difflib.SequenceMatcher(None, body, s[1]).ratio())
    r = difflib.SequenceMatcher(None, body, best[1]).ratio()
    if r >= .72: hits.append((round(r, 2), best[0], body[:70]))
hits.sort(reverse=True)
print(f'{len(items)} assignment items against {len(sents)} deck sentences; near copies (ratio >= .72): {len(hits)}')
for h in hits: print('  ', h)
# figures: split the assignment by question and look for slides sharing 3 or more of a question's large figures
nums = re.compile(r'\d{1,3}(?:,\d{3})+')
qs = {}
for m in re.finditer(r'(?:^|\n)\s*שאלה(\d+)\s*\n(.*?)(?=\n\s*שאלה\d+\s*\n|\Z)', raw, re.S):
    qs[int(m.group(1))] = set(nums.findall(m.group(2)))
print('questions parsed:', sorted(qs))
for q, ns in sorted(qs.items()):
    for sid, b in blocks.items():
        common = ns & set(nums.findall(b))
        if len(common) >= 3: print(f'   question {q} shares {len(common)} figures with {sid}: {sorted(common)}')
# company names are read from the assignment, so that none of its content is stored here
for name in sorted(set(re.findall(r'"([^"]{2,12})"\s*בע"מ', raw))):
    print('company name from the assignment appears on slides:', sum(f'״{name}״' in b for b in blocks.values()))
