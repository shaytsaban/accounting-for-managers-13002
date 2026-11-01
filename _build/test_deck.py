# Headless test: inject a script into a copy of the deck, read the JSON from data-test in the dumped DOM.
# Usage: python3 test_deck.py [path to presentation.html]
import json, os, re, shutil, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, '..', 'lectures', 'lecture-1', 'presentation.html')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
EXPECT = {'class': 'התחייבות שוטפת', 're': '72,000', 'bs': '320,000', 'pl': '60,000', 'svc': '15,000', 'txn': '+80,000', 'int': '3,000'}
# inputs that reproduce further answers from the lesson: calc -> ({field: value}, expected)
ALT = [('class', dict(m='36', k='l'), 'התחייבות לא שוטפת'), ('class', dict(m='12', k='a'), 'נכס שוטף'), ('class', dict(m='13', k='a'), 'נכס לא שוטף'),
       ('re', dict(o='30000', n='55000', d='25000'), '60,000'), ('re', dict(o='72000', n='-10000', d='0'), '62,000'),
       ('pl', dict(s='400000', c='250000', m='0', g='60000', f='15000', t='20000'), '55,000'),
       ('svc', dict(t='120000', n='12', d='1', side='prov'), '10,000'), ('int', dict(p='300000', r='8', m='4'), '8,000'),
       ('txn', dict(a='100000', c='0', ev='issue'), '+100,000'), ('txn', dict(a='200000', c='0', ev='loan'), '+200,000'), ('txn', dict(a='5000', c='0', ev='elec'), '0'),
       ('txn', dict(a='12000', c='0', ev='paysup'), '−12,000'), ('txn', dict(a='10000', c='5000', ev='div'), '−5,000'), ('txn', dict(a='60000', c='20000', ev='machine'), '+40,000'),
       ('txn', dict(a='60000', c='60000', ev='machine'), '0'), ('txn', dict(a='30000', c='0', ev='collect'), '0'), ('txn', dict(a='20000', c='0', ev='adv'), '+20,000'), ('txn', dict(a='12000', c='0', ev='prep'), '0')]
TEST = r'''
(function(){
const D=window.__deckT,R={errors:[],overflow:[],small:[],mc:[],calc:[],alt:[],reveal:[],terms:[],abbr:{},chars:[],eqwide:[]};
window.addEventListener('error',e=>R.errors.push(e.message));
const st=document.createElement('style');st.textContent='*{transition:none!important;animation:none!important}';document.head.appendChild(st);
const stage=document.getElementById('stage');
function rel(e){const s=stage.getBoundingClientRect(),r=e.getBoundingClientRect(),k=s.width/1280;return{t:(r.top-s.top)/k,b:(r.bottom-s.top)/k,l:(r.left-s.left)/k,r:(r.right-s.left)/k};}
D.slides.forEach((s,i)=>{D.show(i);D.setAll(s,true);
 // reveal every multiple choice answer so that the open state is what gets measured
 s.querySelectorAll('.mc').forEach(m=>{m.classList.add('done');const a=+m.dataset.a;m.querySelectorAll('.o')[a].classList.add('ok');});
 const foot=s.querySelector('.ft');const limit=foot?720-36:716;let worst=0,who='',wl=0,wr=1280;
 s.querySelectorAll('*').forEach(e=>{if(e.closest('.ft')||e.closest('.pd-num')||e.classList.contains('orb')||e.closest('.orb'))return;const c=getComputedStyle(e);if(c.display==='none'||c.visibility==='hidden')return;const r=rel(e);if(r.b-r.t<1)return;
  if(r.b>worst){worst=r.b;who=e.tagName+'.'+(e.className.baseVal??e.className);}if(r.l<wl)wl=r.l;if(r.r>wr)wr=r.r;});
 if(worst>limit+.5||wl<-.5||wr>1280.5)R.overflow.push({i:i+1,id:s.id,bottom:Math.round(worst),limit,who,l:Math.round(wl),r:Math.round(wr)});
 // equations wider than their container
 s.querySelectorAll('.eq').forEach(e=>{const box=e.closest('.card,.solw,.cout,.fm,td,.slide');const inner=document.createRange();inner.selectNodeContents(e);const a=inner.getBoundingClientRect(),b=box.getBoundingClientRect();if(a.left<b.left-1||a.right>b.right+1)R.eqwide.push({id:s.id,t:e.textContent.slice(0,60),over:Math.round(Math.max(b.left-a.left,a.right-b.right))});});
 // text smaller than the board minimum
 const tw=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);let n;const seen={};while((n=tw.nextNode())){if(!n.nodeValue.trim())continue;const p=n.parentElement;if(p.closest('.ft,sup,sub,tspan'))continue;let fs=parseFloat(getComputedStyle(p).fontSize);const svg=p.closest('svg');if(svg){const vb=svg.viewBox.baseVal.width;fs*=svg.getBoundingClientRect().width/(stage.getBoundingClientRect().width/1280)/vb;if(fs<14.5)seen['svg '+fs.toFixed(1)]=n.nodeValue.slice(0,24);}else if(fs<16.5)seen[fs]=n.nodeValue.slice(0,24);}
 if(Object.keys(seen).length)R.small.push({id:s.id,seen});
 // forbidden characters
 const txt=s.textContent;[['em','—'],['maqaf','־'],['en','–'],['ell','…'],['arrow','→'],['arrow2','⇒'],['q1','“'],['q2','”']].forEach(([k,c])=>{if(txt.includes(c))R.chars.push({id:s.id,k});});
 // a sign written after a number, or a fraction written with a slash (per text node: separate boxes are not one string)
 {const w=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);let x;while((x=w.nextNode())){const v=x.nodeValue;if(/\d[−+-](\s|$)/.test(v))R.chars.push({id:s.id,k:'sign after number',t:v.slice(0,40)});if(/\d\s?\/\s?\d/.test(v))R.chars.push({id:s.id,k:'inline slash fraction',t:v.slice(0,40)});}}
 // abbreviations: remember the first slide of each, and whether it is explained there
 ['ממ״ן','ש״ח','בע״מ','נדל״ן'].forEach(a=>{if(!(a in R.abbr)&&txt.includes(a))R.abbr[a]=s.id;});
 s.querySelectorAll('.mc').forEach(m=>{m.classList.remove('done');m.querySelectorAll('.o').forEach(o=>o.classList.remove('ok','bad'));});
 D.setAll(s,false);
});
// reveals
D.slides.forEach((s,i)=>{const g=D.groups(s).length;D.show(i);let c=0;while(D.pending(s).length&&c<60){D.next();c++;}if(c!==g||D.cur()!==i)R.reveal.push({id:s.id,g,c,cur:D.cur()});const shownAll=[...s.querySelectorAll('.st')].every(e=>e.classList.contains('show'));if(!shownAll)R.reveal.push({id:s.id,err:'not all shown'});let b=0;while(D.groups(s).some(x=>x[0].classList.contains('show'))&&b<60){D.prev();b++;}if(b!==g||D.cur()!==i)R.reveal.push({id:s.id,back:b,g});});
D.show(0);let k=0;while(D.cur()<D.slides.length-1&&k<2000){D.next();k++;}R.walked=[k,D.cur()];
// multiple choice: wrong answer then right answer
document.querySelectorAll('.mc').forEach(m=>{const a=+m.dataset.a,os=[...m.querySelectorAll('.o')],w=m.querySelector('.w');const sl=m.closest('.slide');D.go(sl.id);
 const wrong=(a+1)%os.length;os[wrong].click();let ok=m.classList.contains('done')&&os[wrong].classList.contains('bad')&&os[a].classList.contains('ok')&&getComputedStyle(w).display!=='none'&&w.textContent.length>15;
 m.classList.remove('done');os.forEach(o=>o.classList.remove('ok','bad'));os[a].click();ok=ok&&os[a].classList.contains('ok')&&!os[wrong].classList.contains('bad');
 m.classList.remove('done');os.forEach(o=>o.classList.remove('ok','bad'));R.mc.push(ok?1:m.id);});
// calculators
const fire=e=>e.dispatchEvent(new Event('input',{bubbles:true}));
document.querySelectorAll('.calc').forEach(b=>{const id=b.dataset.calc,out=document.getElementById('out-'+id),res=()=>{const x=out.querySelector('[data-res]');return x?x.textContent:(out.textContent.slice(0,40));};
 const r0=res(),ins=[...b.querySelectorAll('input')],first=ins[0],v=first.value;first.value=String(parseFloat(v.replace(/,/g,''))*2);fire(first);const r1=res();first.value='abc';fire(first);const bad=!!out.querySelector('.err');first.value=v;fire(first);const r2=res();
 const overflow=(()=>{D.go('c-'+id);const q=rel(out),l=rel(b);return Math.round(Math.max(q.b,l.b));})();
 R.calc.push({id,r0,r1,changed:r0!==r1,bad,restored:r0===r2,bottom:overflow,inputs:ins.length});});
window.__ALT.forEach(([id,vals,exp])=>{const b=document.querySelector('.calc[data-calc="'+id+'"]'),out=document.getElementById('out-'+id);const saved=[...b.querySelectorAll('[data-k]')].map(e=>[e,e.value]);Object.entries(vals).forEach(([k,v])=>{const e=b.querySelector('[data-k="'+k+'"]');e.value=v;fire(e);});const x=out.querySelector('[data-res]');const got=x?x.textContent:out.textContent.slice(0,50);D.go('c-'+id);const rq=rel(out);R.alt.push({id,exp,got,ok:exp?got===exp:true,bottom:Math.round(rq.b)});saved.forEach(([e,v])=>{e.value=v;fire(e);});});
// every signed amount must paint its sign on the left of its digits
R.signs=0;R.signBad=[];document.querySelectorAll('.m,.it .n,.res b').forEach(e=>{const t=e.textContent;const m=/^[−+]\d/.test(t);if(!m)return;const sl=e.closest('.slide');if(!sl)return;const i=D.slides.indexOf(sl);D.show(i);D.setAll(sl,true);const a=document.createRange(),b=document.createRange();const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);const n=w.nextNode();if(!n)return;a.setStart(n,0);a.setEnd(n,1);b.setStart(n,1);b.setEnd(n,2);if(!a.getBoundingClientRect().width)return;R.signs++;if(a.getBoundingClientRect().left>=b.getBoundingClientRect().left)R.signBad.push({id:sl.id,t});});
// glossary and links
document.querySelectorAll('[data-t]').forEach(t=>{if(!D.G[t.dataset.t])R.terms.push(t.dataset.t);});
R.termsUsed=new Set([...document.querySelectorAll('.slide [data-t]')].map(t=>t.dataset.t)).size;R.termsTotal=Object.keys(D.G).length;
R.unusedTerms=Object.keys(D.G).filter(k=>!document.querySelector('.slide [data-t="'+k+'"]'));
Object.keys(D.G).forEach(k=>{D.openTerm(k);const a=document.getElementById('dp').textContent,b=document.getElementById('dex').textContent;if(a.length<8||b.length<8)R.terms.push('empty '+k);});D.closeOverlays();
R.go=[...document.querySelectorAll('[data-go]')].filter(g=>!document.getElementById(g.dataset.go)).map(g=>g.dataset.go);
// shell: contents, route cards, glossary, drawer, keys
R.shell=[];const has=(sel,c)=>document.querySelector(sel).classList.contains(c);
document.getElementById('bMenu').click();if(!has('#menu','open'))R.shell.push('menu');
if(document.querySelectorAll('.mcell').length!==D.slides.length)R.shell.push('menu cells');
document.querySelectorAll('.mcell')[5].click();if(has('#menu','open')||D.cur()!==5)R.shell.push('menu go');
document.getElementById('bGloss').click();if(!has('#gloss','open'))R.shell.push('gloss');
if(document.querySelectorAll('.gitem').length!==Object.keys(D.G).length)R.shell.push('gloss items');
document.querySelector('.gitem').click();if(!has('#drawer','open'))R.shell.push('drawer');
document.querySelector('#drawer .tabs button[data-k="f"]').click();if(!document.getElementById('dp').textContent.length)R.shell.push('drawer tab');
document.getElementById('dx').click();if(has('#drawer','open'))R.shell.push('drawer close');
D.go('s-route');const cards=[...document.querySelectorAll('.rcard')];cards.forEach(c=>{D.go('s-route');c.click();if(D.slides[D.cur()].id!==c.dataset.go)R.shell.push('route '+c.dataset.go);});
D.go('s-fin');D.setAll(D.slides[D.cur()],true);const tm=D.slides[D.cur()].querySelector('.term');tm.click();if(!has('#drawer','open'))R.shell.push('term click');D.closeOverlays();
D.show(0);document.dispatchEvent(new KeyboardEvent('keydown',{key:'End',bubbles:true}));if(D.cur()!==D.slides.length-1)R.shell.push('End key');document.dispatchEvent(new KeyboardEvent('keydown',{key:'Home',bubbles:true}));if(D.cur()!==0)R.shell.push('Home key');
['bPrint','bFull','bNext','bPrev'].forEach(i=>{if(!document.getElementById(i))R.shell.push(i);});
R.count=D.slides.length;R.opener=[...document.querySelectorAll('.pd')].length;R.st=document.querySelectorAll('.st').length;R.mcN=document.querySelectorAll('.mc').length;R.calcN=document.querySelectorAll('.calc').length;
document.documentElement.setAttribute('data-test',JSON.stringify(R));
})();
'''
html = open(SRC, encoding='utf8').read()
# expose the deck object to the test
html = html.replace('window.__deck={', 'window.__deckT={G,')
inj = '<script>window.__ALT=' + json.dumps(ALT, ensure_ascii=False) + ';' + TEST + '</script></body>'
html = html.replace('</body>', inj)
d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
p = os.path.join(d, 't.html')
open(p, 'w', encoding='utf8').write(html)
out = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/prof', '--window-size=1280,764', '--virtual-time-budget=60000', '--dump-dom', 'file://' + p], capture_output=True, text=True, timeout=300).stdout
shutil.rmtree(d, ignore_errors=True)
m = re.search(r'<html[^>]*data-test="([^"]*)"', out)
if not m:
    print('NO RESULT'); print(out[:400]); sys.exit(1)
import html as hh
R = json.loads(hh.unescape(m.group(1)))
FAIL = 0
print('slides', R['count'], 'openers', R['opener'], 'reveal items', R['st'], 'mc', R['mcN'], 'calcs', R['calcN'], 'walk', R['walked'])
print('errors', R['errors'])
print('overflow', len(R['overflow']));[print('  ', o) for o in R['overflow']]
print('eq wider than box', len(R['eqwide']));[print('  ', o) for o in R['eqwide']]
print('small text', len(R['small']));[print('  ', o) for o in R['small'][:40]]
print('chars', R['chars'])
print('abbr first seen', R['abbr'])
print('reveal problems', R['reveal'])
print('signed amounts measured', R['signs'], 'painted wrong', R['signBad'])
bad = [x for x in R['mc'] if x != 1]
print('mc ok', len(R['mc']) - len(bad), 'bad', bad)
for c in R['calc']:
    exp = EXPECT[c['id']]
    FAIL += c['r0'] != exp or not c['changed'] or not c['bad'] or not c['restored'] or c['bottom'] > 684
    print('  calc', c['id'], 'default', c['r0'], 'OK' if c['r0'] == exp else 'EXPECTED ' + exp, 'changed' if c['changed'] else 'NOCHANGE', 'badinput' if c['bad'] else 'NOERR', 'restored' if c['restored'] else 'NOTRESTORED', 'bottom', c['bottom'])
for a in R['alt']:
    print('  alt', a['id'], a['got'], 'OK' if a['ok'] else 'EXPECTED ' + str(a['exp']), 'bottom', a['bottom'])
    FAIL += not a['ok'] or a['bottom'] > 684
print('shell problems', R['shell'])
print('terms missing', R['terms'], 'used', R['termsUsed'], 'of', R['termsTotal'], 'unused', R['unusedTerms'], 'bad go', R['go'])
FAIL += len(R['shell']) + bool(R['errors']) + len(R['overflow']) + len(R['eqwide']) + len(R['small']) + len(R['chars']) + len(R['reveal']) + len(bad) + len(R['terms']) + len(R['go']) + len(R['signBad']) + len(R['unusedTerms'])
print('RESULT', 'PASS' if not FAIL else f'FAIL ({FAIL})')
sys.exit(1 if FAIL else 0)
