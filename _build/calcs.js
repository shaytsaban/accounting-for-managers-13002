/* ===== interactive calculators: type inputs, read results live ===== */
(function(){
const money=x=>{const r=Math.round(Math.abs(x)*100)/100,s=r.toLocaleString('en-US',{minimumFractionDigits:0,maximumFractionDigits:2});return (x<0&&r?'−':'')+s;};
const sgn=x=>(x>0?'+':'')+money(x);
const fr=(a,b)=>`<span class="frac"><span>${a}</span><span>${b}</span></span>`;
const eq=s=>`<div class="eq" dir="ltr">${s}</div>`;
const heb=s=>`<span class="mh" dir="rtl">${s}</span>`;
const res=(l,v,cls,main)=>`<div class="res${cls===1?' sec':cls?' '+cls:''}"><span>${l}</span><b${main?' data-res':''}>${v}</b></div>`;
const ln=s=>`<p class="ln">${s}</p>`;
const n=s=>`<span class="n">${s}</span>`;
const err=s=>`<div class="err">${s}</div>`;
function num(s){s=String(s).replace(/[,\s]/g,'').replace('−','-');return s===''?NaN:Number(s);}

const need=(v,keys)=>keys.every(k=>Number.isFinite(v[k]));
const BAD='הקלידו מספרים תקינים בכל השדות.';
const it=(lab,x)=>`<span class="it">${lab}<span class="n">${sgn(x)}</span></span>`;
/* a transaction: what happens to each line, by side of the equation */
const EV={
 service:{cash:1,f:(a,c)=>({A:[['מזומן',c],['לקוחות',a-c]],L:[],E:[['הכנסות משירותים',a]]})},
 issue:{f:a=>({A:[['מזומן',a]],L:[],E:[['הון מניות',a]]})},
 loan:{f:a=>({A:[['מזומן',a]],L:[['הלוואה',a]],E:[]})},
 elec:{f:a=>({A:[],L:[['זכאים',a]],E:[['הוצאות חשמל',-a]]})},
 paysup:{f:a=>({A:[['מזומן',-a]],L:[['ספקים',-a]],E:[]})},
 collect:{f:a=>({A:[['מזומן',a],['לקוחות',-a]],L:[],E:[]})},
 div:{cash:1,f:(a,c)=>({A:[['מזומן',-c]],L:[['דיבידנד לשלם',a-c]],E:[['עודפים',-a]]})},
 machine:{cash:1,f:(a,c)=>({A:[['מכונה',a],['מזומן',-c]],L:[['ספקים',a-c]],E:[]})},
 adv:{f:a=>({A:[['מזומן',a]],L:[['הכנסה נדחית',a]],E:[]})},
 prep:{f:a=>({A:[['הוצאות מראש',a],['מזומן',-a]],L:[],E:[]})}
};
const C={
eq(v){if(!need(v,['a','l']))return err(BAD);const e=v.a-v.l;
 return eq(`${heb('הון עצמי')} = ${heb('נכסים')} − ${heb('התחייבויות')}`)+eq(`${money(e)} = ${money(v.a)} − ${money(v.l)}`)+res('הון עצמי',money(e),'',1)+eq(`${money(v.a)} = ${money(v.l)} + ${money(e)}`)+ln(e<0?'ההתחייבויות גדולות מן הנכסים: ההון העצמי שלילי.':'השוויון נשמר תמיד, כי ההון העצמי הוא היתרה.');},
class(v){if(!need(v,['m']))return err(BAD);if(v.m<0)return err('מספר החודשים חייב להיות חיובי.');const cur=v.m<=12,isA=v.k==='a',label=isA?(cur?'נכס שוטף':'נכס לא שוטף'):(cur?'התחייבות שוטפת':'התחייבות לא שוטפת');
 return res('סיווג',label,'',1)+ln(`${n(v.m)} חודשים ממועד הדיווח ${cur?'אינם עולים על שנה':'עולים על שנה'}.`)+ln('הקו הוא פרק הזמן הצפוי ממועד הדיווח. השאלה אם כבר נעשה שימוש בנכס איננה משנה.');},
re(v){if(!need(v,['o','n','d']))return err(BAD);const c=v.o+v.n-v.d;
 return eq(`${heb('עודפים לסוף שנה')} = ${heb('לתחילת השנה')} + ${heb('רווח נקי')} − ${heb('דיבידנדים')}`)+eq(`${money(c)} = ${money(v.o)} ${v.n<0?'−':'+'} ${money(Math.abs(v.n))} − ${money(v.d)}`)+res('עודפים לסוף שנה',money(c),'',1)+ln(v.n<0?'הפסד מקטין את העודפים.':'רווח מגדיל את העודפים, ודיבידנד מקטין אותם.');},
bs(v){const k=['cash','ar','inv','ppe','ap','acc','st','lt','cap','re'];if(!need(v,k))return err(BAD);const ca=v.cash+v.ar+v.inv,ta=ca+v.ppe,cl=v.ap+v.acc+v.st,tl=cl+v.lt,e=v.cap+v.re,tle=tl+e,d=ta-tle;
 return res('סך נכסים שוטפים',money(ca),'mini')+res('סך נכסים',money(ta),'mini end',1)+res('סך התחייבויות שוטפות',money(cl),'mini')+res('סך התחייבויות',money(tl),'mini')+res('סך הון עצמי',money(e),'mini')+res('סך התחייבויות והון עצמי',money(tle),'mini')+(d?`<div class="warn">המאזן אינו מאוזן: הפרש של ${n(money(Math.abs(d)))}. עסקה מתועדת תמיד בשני מקומות לפחות.</div>`:'<div class="ok">המאזן מאוזן: סך הנכסים שווה לסך ההתחייבויות וההון העצמי.</div>');},
pl(v){if(!need(v,['s','c','m','g','f','t']))return err(BAD);const gp=v.s-v.c,op=gp-v.m-v.g,bt=op-v.f,ni=bt-v.t;
 return res('רווח גולמי',money(gp),'mini')+res('רווח תפעולי',money(op),'mini')+res('רווח לפני מסים על ההכנסה',money(bt),'mini')+res(ni<0?'הפסד נקי':'רווח נקי',money(ni),'mini end',1)+eq(`${money(gp)} = ${money(v.s)} − ${money(v.c)}`)+eq(`${money(op)} = ${money(gp)} − ${money(v.m)} − ${money(v.g)}`)+ln(ni<0?'הפסד מקטין את העודפים שבהון העצמי.':'הרווח הנקי ״זורם״ למאזן ומגדיל את העודפים.');},
svc(v){if(!need(v,['t','n','d']))return err(BAD);if(v.n<=0||v.d<0||v.d>v.n)return err('מספר החודשים שבוצעו חייב להיות בין 0 למשך החוזה.');const now=v.t*v.d/v.n,left=v.t-now,prov=v.side==='prov';
 return eq(`${money(now)} = ${fr(money(v.t),v.n)} × ${v.d}`)+res(prov?'הכנסה בדוח רווח והפסד':'הוצאה בדוח רווח והפסד',money(now),'',1)+res(prov?'הכנסה נדחית: התחייבות':'הוצאות מראש: נכס',money(left),1)+res('מזומן ששולם מראש',money(v.t),1)+ln(prov?'היתרה היא שירות שהחברה עוד חייבת לספק.':'היתרה היא שירות שהחברה עוד זכאית לקבל.');},
txn(v){if(!need(v,['a','c']))return err(BAD);const e=EV[v.ev];if(!e)return err(BAD);if(v.a<0)return err('סכום העסקה חייב להיות חיובי.');if(e.cash&&(v.c<0||v.c>v.a))return err('החלק שבמזומן חייב להיות בין 0 לסכום העסקה.');
 const r=e.f(v.a,e.cash?v.c:0),clean=x=>x.filter(p=>p[1]!==0),sum=x=>x.reduce((s,p)=>s+p[1],0),A=clean(r.A),L=clean(r.L),Q=clean(r.E),da=sum(A),dl=sum(L),dq=sum(Q);
 const col=(t,x)=>`<div class="fxc"><b>${t}</b>${x.length?x.map(p=>it(p[0],p[1])).join(''):'<span class="it">אין שינוי</span>'}</div>`;
 return `<div class="fx">${col('נכסים',A)}${col('התחייבויות',L)}${col('הון עצמי',Q)}</div>`+eq(`${sgn(da)} = ${sgn(dl)} + ${sgn(dq)}`)+res('שינוי בסך המאזן',sgn(da),'',1)+ln(!e.cash?'השדה ״מתוכו במזומן״ אינו משפיע על אירוע זה.':(da===0?'סך המאזן לא השתנה.':'לכל סעיף שהשתנה יש סעיף מקביל.'));},
int(v){if(!need(v,['p','r','m']))return err(BAD);const x=v.p*(v.r/100)*v.m/12;
 return eq(`${money(x)} = ${money(v.p)} × ${v.r}% × ${fr(v.m,12)}`)+res('הוצאת ריבית בתקופה',money(x),'',1)+res('ריבית לשלם, אם טרם שולמה',money(x),1)+ln('ההוצאה נרשמת לפי חלוף הזמן, ולא לפי מועד התשלום. הקרן עצמה מסווגת לפי מועד פירעונה.');}
};
window.__calc=C;
$$('.calc').forEach(box=>{const id=box.dataset.calc,out=$('#out-'+id),ins=$$('[data-k]',box);
 const run=()=>{const v={};ins.forEach(i=>{v[i.dataset.k]=i.tagName==='SELECT'?i.value:num(i.value);});try{out.innerHTML=C[id](v);}catch(e){out.innerHTML=err(BAD);}};
 ins.forEach(i=>{i.addEventListener('input',run);i.addEventListener('change',run);});run();});
})();
