/* ===== navigation shell, reveals, multiple choice, glossary drawer ===== */
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const stage=$('#stage'), slides=$$('.slide');let cur=0;
function toast(t){const el=$('#toast');el.textContent=t;el.classList.add('show');clearTimeout(toast.t);toast.t=setTimeout(()=>el.classList.remove('show'),1600);}

/* ---------- click by click reveals: same data-n appears together ---------- */
function groups(s){const m=new Map();$$('.st',s).forEach(e=>{const n=+e.dataset.n||0;if(!m.has(n))m.set(n,[]);m.get(n).push(e);});return [...m.keys()].sort((a,b)=>a-b).map(k=>m.get(k));}
function pending(s){return groups(s).filter(g=>!g[0].classList.contains('show'));}
function shown(s){return groups(s).filter(g=>g[0].classList.contains('show'));}
function stepInfo(){const g=groups(slides[cur]),left=pending(slides[cur]).length;$('#stepn').textContent=g.length&&left?('נותרו '+left+' שלבים'):'';if(left===1)$('#stepn').textContent='נותר שלב אחד';}
function setAll(s,on){$$('.st',s).forEach(e=>e.classList.toggle('show',on));}

/* ---------- multiple choice checks ---------- */
$$('.mc').forEach(m=>{const a=+m.dataset.a;m.addEventListener('click',e=>{const o=e.target.closest('.o');if(!o||m.classList.contains('done'))return;const i=+o.dataset.i;m.classList.add('done');
 o.classList.add(i===a?'ok':'bad');if(i!==a)m.querySelectorAll('.o')[a].classList.add('ok');else toast('נכון');});});

/* ---------- answer boxes: type a number, check it ---------- */
function ansCheck(a){const i=a.querySelector('input'),raw=i.value.trim(),v=parseFloat(raw.replace(/[,\s₪]/g,'').replace('−','-')),t=+a.dataset.ans,ok=!isNaN(v)&&Math.abs(v-t)<=1;a.classList.remove('ok','bad');a.classList.add(ok?'ok':'bad');a.querySelector('em').textContent=raw===''?'הקלידו מספר':ok?'נכון!':'לא מדויק, נסו שוב';return ok;}
$$('.ansb').forEach(a=>{a.querySelector('button').onclick=e=>{e.stopPropagation();ansCheck(a);};a.querySelector('input').addEventListener('keydown',e=>{if(e.key==='Enter')ansCheck(a);});});

/* ---------- solution tables: a click on a figure shows its calculation under the cards; arrows carry a figure to the next year ---------- */
function sgClear(w){w.querySelectorAll('.sel,.ref,.asrc,.atgt').forEach(e=>e.classList.remove('sel','ref','r0','r1','r2','r3','asrc','atgt'));const sl=w.closest('.slide');if(sl)sl.querySelectorAll('.mv tr.hl').forEach(r=>r.classList.remove('hl'));if(sl)sl.querySelectorAll('.mv.hlon').forEach(t=>t.classList.remove('hlon'));if(sl)sl.querySelectorAll('.qstem .hl').forEach(r=>r.classList.remove('hl'));}
function sgRefs(w,f){let i=0;(f.match(/g\d+-[A-J]\d+(?::g\d+-[A-J]\d+)?/g)||[]).forEach(ad=>{const p=ad.split(':'),cells=[];if(p[1]){const pre=p[0].split('-')[0]+'-',A=p[0].split('-')[1],B=p[1].split('-')[1];for(let c=A.charCodeAt(0);c<=B.charCodeAt(0);c++)for(let r=+A.slice(1);r<=+B.slice(1);r++)cells.push(pre+String.fromCharCode(c)+r);}else cells.push(p[0]);cells.forEach(a=>{const t=w.querySelector('td[data-a="'+a+'"]');if(t)t.classList.add('ref','r'+(i%4));});i++;});}
function sgArrow(el){const sc=el.parentElement,f=sc.querySelector('td[data-a="'+el.dataset.from+'"]'),t=sc.querySelector('td[data-a="'+el.dataset.to+'"]');if(!f||!t||!sc.offsetWidth)return;
 const R=sc.getBoundingClientRect(),k=R.width/sc.offsetWidth,tx=e=>{const n=e.querySelector('.n')||e;return n.getBoundingClientRect();},a=tx(f),b=tx(t);
 /* from the left end of the figure in one year to the right end of the figure in the next year (the column to its left) */
 const x1=(a.left-R.left)/k-5,y1=(a.top+a.height/2-R.top)/k,x2=(b.right-R.left)/k+5,y2=(b.top+b.height/2-R.top)/k,c=Math.max(16,(x1-x2)/2);
 const head='M'+x2+' '+y2+' l10 -6 l0 12 z';
 let s=el.querySelector('svg');if(s)s.remove();el.insertAdjacentHTML('afterbegin','<svg width="'+sc.offsetWidth+'" height="'+sc.offsetHeight+'"><path class="ap" d="M'+x1+' '+y1+' C '+(x1-c)+' '+y1+', '+(x2+10+c)+' '+y2+', '+(x2+10)+' '+y2+'"/><path class="ah" d="'+head+'"/></svg>');
 f.classList.add('asrc');t.classList.add('atgt');}
function sgShow(c){const w=c.closest('.sgw');if(!w)return;sgClear(w);const p=w.querySelector('.sgp')||w.closest('.slide').querySelector('.sgp');if(!p)return;
 if(c.classList.contains('sga')){sgArrow(c);p.innerHTML=c.querySelector('.xx').innerHTML;return;}
 c.classList.add('sel');sgRefs(w,c.dataset.f||'');p.innerHTML=c.querySelector('.xx').innerHTML;
 /* the rows of the question's movements table that this figure comes from: framed, with units × unit figure */
 if(c.dataset.hl){const sl=c.closest('.slide');c.dataset.hl.split(' ').forEach(k=>{sl.querySelectorAll('.mv tr[data-k="'+k+'"],.qstem [data-k="'+k+'"]').forEach(r=>{r.classList.add('hl');const t=r.closest('table.mv');if(t)t.classList.add('hlon');});});}}
$$('.sgw .ec').forEach(c=>c.addEventListener('click',e=>{e.stopPropagation();sgShow(c);}));
function sgReveal(e){const a=e.matches&&e.matches('.auto')?e:(e.querySelector&&e.querySelector('.auto'));if(a)sgShow(a.closest('.ec')||a);}
addEventListener('resize',()=>$$('.slide.on .sga.show').forEach(sgArrow));

/* ---------- the explanation panel and the tips go to the column that has room for them ---------- */
function placeSide(sl){const g=sl.querySelector('.xg');if(!g)return;const q=g.querySelector('.pqq'),a=g.querySelector('.pqa');if(!q||!a)return;
 const R=sl.getBoundingClientRect(),k=R.height/720,lim=R.top+(sl.querySelector('.ft')?681:713)*k;
 const items=[...sl.querySelectorAll('.xg .sgp,.xg .pqq>.band,.xg .pqq>.pun,.xg .pqa>.band,.xg .pqa>.pun')];if(!items.length)return;
 const p=sl.querySelector('.xg .sgp');let longest='';sl.querySelectorAll('.xg .ec .xx,.xg .sga .xx').forEach(x=>{if(x.innerHTML.length>longest.length)longest=x.innerHTML;});
 const keep=p?p.innerHTML:'';if(p&&longest.length>keep.length)p.innerHTML=longest;
 const bottom=col=>Math.max(0,...[...col.children].map(e=>e.getBoundingClientRect().bottom));
 /* try every split of the side items (in order) between the two columns, and keep the first one that fits; else the lowest */
 let best=null;for(let cut=items.length;cut>=0;cut--){items.forEach((e,i)=>(i<cut?q:a).appendChild(e));const m=Math.max(bottom(q),bottom(a));if(m<=lim+.5){best=cut;break;}if(best===null||m<best.m)best={cut,m};}
 const cut=typeof best==='number'?best:best.cut;items.forEach((e,i)=>(i<cut?q:a).appendChild(e));
 if(p)p.innerHTML=keep;}

/* ---------- a sparse slide is enlarged until it fills the slide: the body is scaled up, and laid out in a narrower box ---------- */
function fitZoom(sl){const g=sl.querySelector('.fitz');if(!g){placeSide(sl);return;}
 const R=sl.getBoundingClientRect(),k=R.height/720,lim=R.top+(sl.querySelector('.ft')?679:711)*k,p=sl.querySelector('.sgp');
 const meas=()=>{placeSide(sl);let longest='';sl.querySelectorAll('.ec .xx,.sga .xx').forEach(x=>{if(x.innerHTML.length>longest.length)longest=x.innerHTML;});const keep=p?p.innerHTML:'';if(p&&longest.length>keep.length)p.innerHTML=longest;
  let b=0;const G=g.getBoundingClientRect();g.querySelectorAll('*').forEach(e=>{if(e.closest('.xx,svg'))return;const r=e.getBoundingClientRect();if(!r.height)return;if(r.bottom>b)b=r.bottom;if(r.left<G.left-3*k||r.right>G.right+3*k)b=1e9;});if(p)p.innerHTML=keep;return b;};
 const zs=(g.dataset.z||'1.42,1.36,1.3,1.24,1.18,1.12,1.06').split(',').map(Number);/* a multiple choice question is measured with its explanation open */const mcs=[...sl.querySelectorAll('.mc:not(.done)')];mcs.forEach(m=>m.classList.add('done','fitm'));const unmc=()=>mcs.forEach(m=>m.classList.remove('done','fitm'));
 const set=c=>{g.style.transform=c===1?'':'scale('+c+')';g.style.width=(100/c)+'%';g.dataset.zz=c;};let z=1;
 for(const c of zs){set(c);if(meas()<=lim){z=c;break;}}
 set(z);placeSide(sl);
 /* second pass: the solution column of a question slide grows on its own while it has room under it */
 const a=sl.querySelector('.xg>.pqa');if(!a){unmc();return;}const longest=()=>{let t='';sl.querySelectorAll('.ec .xx,.sga .xx').forEach(x=>{if(x.innerHTML.length>t.length)t=x.innerHTML;});return t;};
 const pa=a.querySelector('.sgp'),colB=()=>{const keep=pa?pa.innerHTML:'',lg=longest();if(pa&&lg.length>keep.length)pa.innerHTML=lg;let b=0;const A=a.getBoundingClientRect();a.querySelectorAll('*').forEach(e=>{if(e.closest('.xx,svg'))return;const r=e.getBoundingClientRect();if(!r.height)return;if(r.bottom>b)b=r.bottom;if(r.left<A.left-3*k||r.right>A.right+3*k)b=1e9;});if(pa)pa.innerHTML=keep;return b;};
 const setA=c=>{a.style.transform=c===1?'':'scale('+c+')';a.style.width=(100/c)+'%';a.dataset.zz=c;};let za=1;
 for(const c of [1.45,1.38,1.31,1.24,1.17,1.1]){if(z*c>1.62)continue;setA(c);if(colB()<=lim){za=c;break;}}
 setA(za);unmc();}

/* ---------- glossary drawer ---------- */
const gk=Object.keys(G);const dr=$('#drawer');let dkey=null;
function openTerm(k){const g=G[k];if(!g)return;dkey=k;$('#dh').textContent=g.h;$('#den').textContent=g.en||'';$('#dex').innerHTML='<b>דוגמה: </b>'+g.ex;$('#dtr').innerHTML='<b>שימו לב: </b>'+g.tr;$('#drel').innerHTML='';setMode('p');dr.classList.add('open');closeOverlays(true);}
function setMode(m){$('#dp').innerHTML=m==='p'?G[dkey].p:G[dkey].f;$$('#drawer .tabs button').forEach(b=>b.classList.toggle('on',b.dataset.k===m));}
$$('#drawer .tabs button').forEach(b=>b.onclick=()=>setMode(b.dataset.k));$('#dx').onclick=()=>dr.classList.remove('open');
$('#gwrap').innerHTML=gk.map(k=>`<button class="gitem" data-t="${k}">${G[k].h}<div class="gen">${G[k].en}</div></button>`).join('');
$('#gpl').innerHTML=gk.map(k=>`<div class="gp"><b>${G[k].h}</b> (${G[k].en})<br>${G[k].p}<br>דוגמה: ${G[k].ex}</div>`).join('');

/* ---------- navigation ---------- */
function show(i,reveal){if(i<0||i>=slides.length)return;slides[cur].classList.remove('on');cur=i;slides[cur].classList.add('on');setAll(slides[cur],!!reveal);fitZoom(slides[cur]);
 $('#cnt').textContent=(cur+1)+' / '+slides.length;$('#progi').style.width=((cur+1)/slides.length*100)+'%';
 try{history.replaceState(null,'','#'+slides[cur].id);}catch(e){}
 $$('.mcell').forEach((c,j)=>c.classList.toggle('cur',j===cur));stepInfo();setTimeout(()=>{slides[cur].querySelectorAll('.sga.show').forEach(sgArrow);slides[cur].querySelectorAll('.asrc,.atgt').forEach(e=>e.classList.remove('asrc','atgt'));},30);if(window.__fitSheets)window.__fitSheets(slides[cur]);}
function go(id){const i=slides.findIndex(s=>s.id===id);if(i>=0){closeOverlays();show(i);}}
function next(){/* a step by step demonstration in a live sheet goes on with the same key */
 const sh=$$('.sheet',slides[cur]).map(x=>x.__api).find(a=>a&&a.stepActive&&a.stepActive());if(sh){sh.stepNext();return;}
 const p=pending(slides[cur]);if(p.length){p[0].forEach(e=>{e.classList.add('show');sgReveal(e);});stepInfo();return;}show(cur+1);}
function prev(){const s=shown(slides[cur]);if(s.length){s[s.length-1].forEach(e=>e.classList.remove('show'));stepInfo();return;}show(cur-1,true);}
$('#bNext').onclick=next;$('#bPrev').onclick=prev;
$('#prog').onclick=e=>{const r=e.currentTarget.getBoundingClientRect();const f=(r.right-e.clientX)/r.width;show(Math.min(slides.length-1,Math.floor(f*slides.length)));};
function closeOverlays(keepDrawer){$('#menu').classList.remove('open');$('#gloss').classList.remove('open');if(!keepDrawer)dr.classList.remove('open');}
$('#closex').onclick=()=>closeOverlays();
$('#bMenu').onclick=()=>{closeOverlays();$('#menu').classList.add('open');};
$('#bGloss').onclick=()=>{closeOverlays();$('#gloss').classList.add('open');};
$('#mgrid').innerHTML=slides.map((s,i)=>`<button class="mcell" data-go="${s.id}"><small>${i+1}</small>${s.dataset.title}</button>`).join('');
$('#bPrint').onclick=()=>{closeOverlays();setTimeout(()=>window.print(),150);};
$('#bFull').onclick=()=>{if(!document.fullscreenElement)document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen();else document.exitFullscreen();};
const typing=e=>{const t=e.target;return t&&(t.tagName==='INPUT'||t.tagName==='SELECT'||t.tagName==='TEXTAREA');};
document.addEventListener('keydown',e=>{if(typing(e)){if(e.key==='Escape')e.target.blur();return;}
 if(e.key==='ArrowLeft'||e.key==='PageDown'||e.key===' '){if(e.target.tagName==='BUTTON'&&e.key===' ')return;e.preventDefault();next();}
 else if(e.key==='ArrowRight'||e.key==='PageUp'){e.preventDefault();prev();}
 else if(e.key==='Escape'){closeOverlays();}
 else if(e.key==='Home'){show(0);}else if(e.key==='End'){show(slides.length-1);}});
function fit(){const s=Math.min(innerWidth/1280,(innerHeight-44-14)/720);stage.style.setProperty('--sc',s);}
addEventListener('resize',()=>{fit();fitZoom(slides[cur]);if(window.__fitSheets)window.__fitSheets(slides[cur]);});fit();
document.addEventListener('click',e=>{const t=e.target.closest('[data-t]');if(t&&G[t.dataset.t]){e.stopPropagation();openTerm(t.dataset.t);return;}
 const g=e.target.closest('[data-go]');if(g){go(g.dataset.go);return;}
 if(!e.target.closest('#drawer'))dr.classList.remove('open');
 /* a click on the empty part of a slide advances, as on a classroom board */
 if(e.target.closest('#stage')&&!e.target.closest('button,a,input,select,label,textarea,.mc,.calc,.term,.sgw,.xlq')&&!document.getSelection().toString())next();});

/* ---------- footers and boot ---------- */
slides.forEach((s,i)=>{if(s.id==='s-title'||s.id==='s-end'||s.classList.contains('pd'))return;const f=document.createElement('div');f.className='ft';f.innerHTML='<span>'+COURSE+' · שיעור '+LESSON+'</span><span><b>ד״ר שי צבאן</b> · <span class="n">'+(i+1)+'</span></span>';s.appendChild(f);});
(function(){const h=location.hash.slice(1);const hi=slides.findIndex(s=>s.id===h);show(hi>=0?hi:0);})();
if(document.fonts){if(document.fonts.ready)document.fonts.ready.then(()=>fitZoom(slides[cur]));if(document.fonts.addEventListener)document.fonts.addEventListener('loadingdone',()=>fitZoom(slides[cur]));}
window.__deck={ansCheck,sgShow,placeSide,fitZoom,show,next,prev,go,slides,groups,pending,setAll,openTerm,closeOverlays,cur:()=>cur};
