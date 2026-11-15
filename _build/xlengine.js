/* ===== mini Excel: a small spreadsheet that behaves like Hebrew (right-to-left) Excel ===== */
const esc=t=>String(t).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const XL=(function(){
const colName=i=>{let s='';i++;while(i>0){const m=(i-1)%26;s=String.fromCharCode(65+m)+s;i=Math.floor((i-1)/26);}return s;};
const colIdx=L=>{let n=0;for(const ch of L)n=n*26+(ch.charCodeAt(0)-64);return n-1;};
const addr=(r,c)=>colName(c)+(r+1);
const parseAddr=a=>{const m=/^\$?([A-Z]+)\$?(\d+)$/.exec(a);return m?{r:+m[2]-1,c:colIdx(m[1])}:null;};
const ERR=e=>({err:e});const isErr=v=>v&&typeof v==='object'&&'err' in v;
const NUMRX=/^\s*-?(\d+(\.\d*)?|\.\d+)\s*%?\s*$/;

/* ---------- tokenizer and parser ---------- */
function tokenize(s){const T=[];let i=0;
 while(i<s.length){const ch=s[i];
  if(/\s/.test(ch)){i++;continue;}
  let m;
  if((m=/^(\d+(\.\d*)?|\.\d+)/.exec(s.slice(i)))){T.push({t:'num',v:parseFloat(m[1])});i+=m[1].length;continue;}
  if((m=/^(\$?[A-Za-z]{1,2}\$?\d+)(:\$?[A-Za-z]{1,2}\$?\d+)?/.exec(s.slice(i)))&&!/^[A-Za-z]+\(/.test(s.slice(i))){
   T.push(m[2]?{t:'range',a:m[1].toUpperCase(),b:m[2].slice(1).toUpperCase()}:{t:'ref',a:m[1].toUpperCase()});i+=m[0].length;continue;}
  if((m=/^([A-Za-z]+)\s*\(/.exec(s.slice(i)))){T.push({t:'fn',v:m[1].toUpperCase()});i+=m[0].length;continue;}
  if((m=/^(>=|<=|<>)/.exec(s.slice(i)))){T.push({t:'op',v:m[1]});i+=2;continue;}
  if('+-*/^%(),;<>='.includes(ch)){T.push({t:'op',v:ch===';'?',':ch});i++;continue;}
  if(ch==='"'){const j=s.indexOf('"',i+1);if(j<0)throw 'str';T.push({t:'str',v:s.slice(i+1,j)});i=j+1;continue;}
  throw 'bad';}
 return T;}
function parse(T){let p=0;const peek=()=>T[p],eat=v=>{if(T[p]&&T[p].t==='op'&&T[p].v===v){p++;return true;}return false;};
 function expr(){let n=add();for(const o of ['>=','<=','<>','>','<','=']){if(eat(o))return {k:'cmp',o,a:n,b:add()};}return n;}
 function add(){let n=term();for(;;){if(eat('+'))n={k:'+',a:n,b:term()};else if(eat('-'))n={k:'-',a:n,b:term()};else return n;}}
 function term(){let n=pow();for(;;){if(eat('*'))n={k:'*',a:n,b:pow()};else if(eat('/'))n={k:'/',a:n,b:pow()};else return n;}}
 function pow(){let n=unary();while(eat('^'))n={k:'^',a:n,b:unary()};return n;}
 function unary(){if(eat('-'))return {k:'neg',a:unary()};if(eat('+'))return unary();return post();}
 function post(){let n=prim();while(eat('%'))n={k:'pct',a:n};return n;}
 function prim(){const t=peek();if(!t)throw 'end';
  if(t.t==='num'){p++;return {k:'num',v:t.v};}
  if(t.t==='str'){p++;return {k:'str',v:t.v};}
  if(t.t==='ref'){p++;return {k:'ref',a:t.a};}
  if(t.t==='range'){p++;return {k:'range',a:t.a,b:t.b};}
  if(t.t==='fn'){p++;const args=[];if(!eat(')')){do{const nx=peek();if(nx&&nx.t==='op'&&(nx.v===','||nx.v===')'))args.push({k:'miss'});else args.push(expr());}while(eat(','));if(!eat(')'))throw 'paren';}return {k:'fn',f:t.v,args};}
  if(eat('(')){const n=expr();if(!eat(')'))throw 'paren';return n;}
  throw 'tok';}
 const n=expr();if(p<T.length)throw 'trail';return n;}


/* ---------- finance functions, with Excel's argument order and sign convention (money paid out is negative) ---------- */
const FIN=(function(){
 const E=e=>({err:e});
 const t01=t=>t?1:0;
 function PV(r,n,p,f,t){p=p||0;f=f||0;t=t01(t);if(r===0)return -(f+p*n);const q=Math.pow(1+r,n);return -(f+p*(1+r*t)*(q-1)/r)/q;}
 function FV(r,n,p,v,t){p=p||0;v=v||0;t=t01(t);if(r===0)return -(v+p*n);const q=Math.pow(1+r,n);return -(v*q+p*(1+r*t)*(q-1)/r);}
 function PMT(r,n,v,f,t){f=f||0;t=t01(t);if(n===0)return E('#NUM!');if(r===0)return -(v+f)/n;const q=Math.pow(1+r,n);return -(f+v*q)*r/((1+r*t)*(q-1));}
 function NPER(r,p,v,f,t){f=f||0;t=t01(t);if(r===0){if(p===0)return E('#NUM!');return -(v+f)/p;}const a=p*(1+r*t)-f*r,b=p*(1+r*t)+v*r;if(a/b<=0||r<=-1)return E('#NUM!');return Math.log(a/b)/Math.log(1+r);}
 /* a root by Newton steps, falling back to bisection on a bracket; returns null when there is no root */
 function root(F,g){let x=g;for(let i=0;i<300;i++){const fx=F(x);if(!isFinite(fx))break;const h=1e-7*Math.max(1,Math.abs(x)),d=(F(x+h)-F(x-h))/(2*h);if(!isFinite(d)||d===0)break;let nx=x-fx/d;if(nx<=-1)nx=(x-1)/2;if(Math.abs(nx-x)<1e-15*Math.max(1,Math.abs(x))){x=nx;return polish(F,x);}x=nx;}
  const xs=[-0.999999,-0.99,-0.9,-0.5,-0.2,-0.1,-0.05,0,0.01,0.02,0.05,0.1,0.2,0.5,1,2,5,10,100,1000];let lo=null,hi=null;
  for(let i=0;i+1<xs.length;i++){const a=F(xs[i]),b=F(xs[i+1]);if(isFinite(a)&&isFinite(b)&&a*b<=0){lo=xs[i];hi=xs[i+1];break;}}
  if(lo===null)return null;let flo=F(lo);for(let i=0;i<300;i++){const m=(lo+hi)/2,fm=F(m);if(fm===0||hi-lo<1e-16)return m;if(flo*fm<0)hi=m;else{lo=m;flo=fm;}}return (lo+hi)/2;}
 function polish(F,x){for(let i=0;i<3;i++){const h=1e-8*Math.max(1,Math.abs(x)),d=(F(x+h)-F(x-h))/(2*h);if(!d)break;const nx=x-F(x)/d;if(!isFinite(nx))break;x=nx;}return x;}
 function RATE(n,p,v,f,t,g){p=p||0;f=f||0;t=t01(t);const F=r=>Math.abs(r)<1e-12?v+p*n+f:v*Math.pow(1+r,n)+p*(1+r*t)*(Math.pow(1+r,n)-1)/r+f;const x=root(F,g==null?0.1:g);return x===null?E('#NUM!'):x;}
 function NPV(r,vals){if(r===-1)return E('#DIV/0!');let s=0;vals.forEach((v,i)=>{s+=v/Math.pow(1+r,i+1);});return s;}
 function IRR(vals,g){if(!vals.some(v=>v>0)||!vals.some(v=>v<0))return E('#NUM!');const F=r=>vals.reduce((s,v,i)=>s+v/Math.pow(1+r,i),0);const x=root(F,g==null?0.1:g);return x===null?E('#NUM!'):x;}
 function XNPV(r,vals,dates){if(vals.length!==dates.length||!vals.length)return E('#NUM!');const d0=dates[0];let s=0;for(let i=0;i<vals.length;i++){if(dates[i]<d0)return E('#NUM!');s+=vals[i]/Math.pow(1+r,(dates[i]-d0)/365);}return s;}
 function XIRR(vals,dates,g){if(vals.length!==dates.length||!vals.some(v=>v>0)||!vals.some(v=>v<0))return E('#NUM!');const d0=dates[0];const F=r=>vals.reduce((s,v,i)=>s+v/Math.pow(1+r,(dates[i]-d0)/365),0);const x=root(F,g==null?0.1:g);return x===null?E('#NUM!'):x;}
 /* Excel date serial: days since 30.12.1899 */
 function DATE(y,m,d){y=Math.trunc(y);if(y<1900)y+=1900;return Math.round((Date.UTC(y,Math.trunc(m)-1,Math.trunc(d))-Date.UTC(1899,11,30))/864e5);}
 function ROUND(x,d){d=Math.trunc(d||0);const k=Math.pow(10,d);const y=Math.abs(x)*k;const r=Math.round(y+1e-9*Math.max(1,y));return Math.sign(x)*r/k;}
 return {PV,FV,PMT,NPER,RATE,NPV,IRR,XNPV,XIRR,DATE,ROUND};})();

/* ---------- a sheet ---------- */
function Sheet(rows,cols){this.rows=rows;this.cols=cols;this.raw={};this.fmt={};this.sty={};this.val={};}
Sheet.prototype.set=function(a,raw){if(raw===''||raw==null)delete this.raw[a];else this.raw[a]=String(raw);};
Sheet.prototype.recalc=function(){const S=this,memo={},busy={};
 function cellv(a){if(a in memo)return memo[a];const pa=parseAddr(a);if(!pa||pa.r>=S.rows||pa.c>=S.cols&&pa.c>25)return ERR('#REF!');
  if(busy[a])return ERR('#CIRC!');busy[a]=1;let v;const raw=S.raw[a];
  if(raw==null)v=null;else if(raw[0]==='='){try{v=ev(parse(tokenize(raw.slice(1))));if(v==null)v=0;}catch(e){v=ERR(e==='bad'||e==='tok'?'#NAME?':'#ERROR!');}}
  else if(NUMRX.test(raw)){const pc=raw.includes('%');v=parseFloat(raw.replace('%',''))/(pc?100:1);}
  else v=raw;
  busy[a]=0;memo[a]=v;return v;}
 function rng(a,b){const A=parseAddr(a),B=parseAddr(b);const out=[];for(let r=Math.min(A.r,B.r);r<=Math.max(A.r,B.r);r++)for(let c=Math.min(A.c,B.c);c<=Math.max(A.c,B.c);c++)out.push(cellv(addr(r,c)));return out;}
 function num(v){if(isErr(v))return v;if(v==null)return 0;if(typeof v==='number')return v;return ERR('#VALUE!');}
 function ev(n){switch(n.k){
  case 'num':return n.v; case 'str':return n.v;
  case 'ref':return cellv(n.a.replace(/\$/g,''));
  case 'range':return ERR('#VALUE!');
  case 'neg':{const a=num(ev(n.a));return isErr(a)?a:-a;}
  case 'pct':{const a=num(ev(n.a));return isErr(a)?a:a/100;}
  case 'cmp':{const a=num(ev(n.a)),b=num(ev(n.b));if(isErr(a))return a;if(isErr(b))return b;return {'>=':a>=b,'<=':a<=b,'<>':a!==b,'>':a>b,'<':a<b,'=':a===b}[n.o];}
  case 'miss':return null;
  case 'fn':{const F=n.f,A=n.args;
   /* finance and math functions: scalar arguments, or a list of numbers from ranges */
   const sc=i=>{const x=A[i];if(!x||x.k==='miss')return undefined;if(x.k==='range')return ERR('#VALUE!');const v=ev(x);if(v===true)return 1;if(v===false)return 0;return num(v);};
   const list=(i,e)=>{const out=[];for(let j=i;j<(e==null?A.length:e);j++){const x=A[j];if(x.k==='miss')continue;if(x.k==='range'){for(const v of rng(x.a.replace(/\$/g,''),x.b.replace(/\$/g,''))){if(isErr(v))return v;if(typeof v==='number')out.push(v);}}else{const v=ev(x);if(isErr(v))return v;if(typeof v==='number')out.push(v);else if(v!=null&&v!==''&&typeof v!=='boolean')return ERR('#VALUE!');}}return out;};
   const SIG={PV:[3,5],FV:[3,5],PMT:[3,5],NPER:[3,5],RATE:[3,6],ROUND:[2,2],POWER:[2,2],SQRT:[1,1],LN:[1,1],EXP:[1,1],DATE:[3,3],EFFECT:[2,2],NOMINAL:[2,2]};
   if(SIG[F]){const [lo,hi]=SIG[F];if(A.length<lo||A.length>hi)return ERR('#N/A');const v=[];for(let i=0;i<A.length;i++){const x=sc(i);if(isErr(x))return x;v.push(x);}
    for(let i=0;i<lo;i++)if(v[i]===undefined)v[i]=0;   /* an empty argument counts as 0, as in Excel */
    let r;switch(F){case 'PV':r=FIN.PV(v[0],v[1],v[2],v[3],v[4]);break;case 'FV':r=FIN.FV(v[0],v[1],v[2],v[3],v[4]);break;case 'PMT':r=FIN.PMT(v[0],v[1],v[2],v[3],v[4]);break;
     case 'NPER':r=FIN.NPER(v[0],v[1],v[2],v[3],v[4]);break;case 'RATE':r=FIN.RATE(v[0],v[1],v[2],v[3],v[4],v[5]);break;case 'ROUND':r=FIN.ROUND(v[0],v[1]);break;
     case 'POWER':r=Math.pow(v[0],v[1]);break;case 'SQRT':r=v[0]<0?ERR('#NUM!'):Math.sqrt(v[0]);break;case 'LN':r=v[0]<=0?ERR('#NUM!'):Math.log(v[0]);break;case 'EXP':r=Math.exp(v[0]);break;
     case 'DATE':r=FIN.DATE(v[0],v[1],v[2]);break;case 'EFFECT':r=v[1]<1||v[0]<=0?ERR('#NUM!'):Math.pow(1+v[0]/Math.trunc(v[1]),Math.trunc(v[1]))-1;break;case 'NOMINAL':r=v[1]<1||v[0]<=0?ERR('#NUM!'):Math.trunc(v[1])*(Math.pow(1+v[0],1/Math.trunc(v[1]))-1);break;}
    if(typeof r==='number'&&!isFinite(r))return ERR('#NUM!');return r;}
   if(F==='NPV'){if(A.length<2)return ERR('#N/A');const r=sc(0);if(isErr(r))return r;const L=list(1);if(isErr(L))return L;return FIN.NPV(r||0,L);}
   if(F==='IRR'){if(!A.length||A.length>2)return ERR('#N/A');const L=list(0,1);if(isErr(L))return L;const g=A[1]?sc(1):undefined;if(isErr(g))return g;return FIN.IRR(L,g);}
   if(F==='XNPV'||F==='XIRR'){const x=F==='XNPV';if(A.length<(x?3:2)||A.length>3)return ERR('#N/A');const L=list(x?1:0,x?2:1),D=list(x?2:1,x?3:2);if(isErr(L))return L;if(isErr(D))return D;
    if(x){const r=sc(0);if(isErr(r))return r;return FIN.XNPV(r||0,L,D);}const g=A[2]?sc(2):undefined;return FIN.XIRR(L,D,g);}
   if(F==='SUMPRODUCT'){const ls=A.map(x=>x.k==='range'?rng(x.a.replace(/\$/g,''),x.b.replace(/\$/g,'')):[ev(x)]);if(ls.some(l=>l.length!==ls[0].length))return ERR('#VALUE!');let s=0;for(let i=0;i<ls[0].length;i++){let p=1;for(const l of ls){const v=l[i];if(isErr(v))return v;p*=typeof v==='number'?v:0;}s+=p;}return s;}
   if(n.f==='IF'){if(n.args.length<2)return ERR('#N/A');const c=ev(n.args[0]);if(isErr(c))return c;return c?ev(n.args[1]):(n.args[2]?ev(n.args[2]):false);}
   if(n.f==='ABS'){const a=num(ev(n.args[0]));return isErr(a)?a:Math.abs(a);}
   const vals=[];for(const x of n.args){if(x.k==='range')vals.push(...rng(x.a.replace(/\$/g,''),x.b.replace(/\$/g,'')).map(v=>({v,inRange:true})));else vals.push({v:ev(x),inRange:false});}
   const e=vals.find(o=>isErr(o.v));if(e&&n.f!=='COUNTA'&&n.f!=='COUNT')return e.v;
   const nums=vals.filter(o=>typeof o.v==='number'||(!o.inRange&&o.v==null)).map(o=>o.v||0);
   switch(n.f){case 'SUM':return nums.reduce((s,x)=>s+x,0);
    case 'AVERAGE':return nums.length?nums.reduce((s,x)=>s+x,0)/nums.length:ERR('#DIV/0!');
    case 'MIN':return nums.length?Math.min(...nums):0; case 'MAX':return nums.length?Math.max(...nums):0;
    case 'COUNT':return vals.filter(o=>typeof o.v==='number').length;
    case 'COUNTA':return vals.filter(o=>o.v!=null&&o.v!=='').length;
    default:return ERR('#NAME?');}}
  default:{const a=num(ev(n.a)),b=num(ev(n.b));if(isErr(a))return a;if(isErr(b))return b;
   if(n.k==='+')return a+b;if(n.k==='-')return a-b;if(n.k==='*')return a*b;if(n.k==='/')return b===0?ERR('#DIV/0!'):a/b;if(n.k==='^')return Math.pow(a,b);}}}
 for(let r=0;r<S.rows;r++)for(let c=0;c<S.cols;c++)cellv(addr(r,c));
 Object.keys(S.raw).forEach(cellv);this.val=memo;};

/* shift every relative reference in a formula by (dr,dc), the way Excel does when a formula is dragged or pasted */
function shift(raw,dr,dc){if(!raw||raw[0]!=='=')return raw;
 return '='+raw.slice(1).replace(/("[^"]*")|(\$?)([A-Za-z]{1,2})(\$?)(\d+)(?![\d(A-Za-z])/g,(m,str,d1,L,d2,R)=>{if(str)return str;
  let c=colIdx(L.toUpperCase()),r=+R-1;if(!d1)c+=dc;if(!d2)r+=dr;if(c<0||r<0)return '#REF!';return d1+colName(c)+d2+(r+1);});}

const fmtNum=(v,f)=>{if(f==='gen')f='';const ac=/^acc(\d)$/.exec(f||'');if(ac){const t=Math.abs(v).toLocaleString('en-US',{minimumFractionDigits:+ac[1],maximumFractionDigits:+ac[1]});return Math.abs(v)<1e-9?'-':(v<0?'('+t+')':t);}const cu=/^cur(\d)$/.exec(f||'');if(cu){const t=Math.abs(v).toLocaleString('en-US',{minimumFractionDigits:+cu[1],maximumFractionDigits:+cu[1]});return (v<0?'−':'')+'₪'+t;}const fd=/^(pct|num)(\d)$/.exec(f||'');if(fd){const d=+fd[2];const x=fd[1]==='pct'?v*100:v;const t=x.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d}).replace('-','−');return fd[1]==='pct'?t+'%':t;}
 if(f==='pct'){const x=Math.round(v*100*100)/100;return x+'%';}
 if(Math.abs(v)>=1e11)return v.toExponential(4);const x=Math.round(v*1e6)/1e6;
 return x.toLocaleString('en-US',{maximumFractionDigits:2}).replace('-','−');};
function display(S,a){const v=S.val[a];if(v==null)return {t:'',n:false};if(isErr(v))return {t:v.err,n:false,e:true};
 if(typeof v==='number'){const raw=S.raw[a]||'';const f=S.fmt[a]||(raw[0]!=='='&&raw.includes('%')?'pct':'');return {t:fmtNum(v,f),n:true};}
 return {t:String(v),n:false};}

/* ---------- the widget ---------- */
let CLIP=null;
function mount(host,cfg){
 const R=cfg.rows,C=cfg.cols,R0=(cfg.r0||1)-1;const S=new Sheet(R,C);
 /* a template built click by click (the first exercise): the label cells of each group appear on the deck's next key */
 const BL=cfg.build||[];let bk=0;
 const baseNow=()=>{const d={...cfg.data};BL.slice(0,bk).forEach(st=>st.cells.forEach(a=>{d[a]=cfg.bdata[a];}));return d;};
 let base=baseNow();
 const load=()=>{base=baseNow();S.raw={};S.sty=JSON.parse(JSON.stringify(cfg.sty||{}));S.fmt={...(cfg.fmt||{})};Object.entries(base).forEach(([a,v])=>S.set(a,v));S.recalc();};load();
 const W=cfg.widths||[];
 host.classList.add('xl');
 host.innerHTML=`<div class="xl-rib" role="toolbar" aria-label="רצועת הכלים: בית"><span class="xl-grp"><button data-r="undo" title="ביטול (Ctrl+Z)"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5.5 3.5 2.5 6.5l3 3M3 6.5h6.5a4 4 0 0 1 0 8H7" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button><button data-r="redo" title="ביצוע חוזר (Ctrl+Y)"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10.5 3.5l3 3-3 3M13 6.5H6.5a4 4 0 0 0 0 8H9" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button></span><span class="xl-grp"><button data-r="b" title="מודגש (Ctrl+B)"><b>B</b></button><button data-r="i" title="נטוי (Ctrl+I)"><i>I</i></button><button data-r="u" title="קו תחתון (Ctrl+U)"><u>U</u></button><button data-r="fill" title="צבע מילוי"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 9l5-5 4 4-5 5z" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M12.5 10.5c0 1.2.9 2 .9 2.6a.9.9 0 0 1-1.8 0c0-.6.9-1.4.9-2.6z" fill="currentColor"/><rect x="1.5" y="14" width="13" height="2" fill="#ffd34d"/></svg><span class="xl-dd">▾</span></button></span><span class="xl-grp"><button data-r="row+" title="הוספת שורה מעל התא">⊕ שורה</button><button data-r="row-" title="מחיקת השורה">⊖ שורה</button></span><span class="xl-grp"><button data-r="al-right" title="יישור לימין"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 3h12M6 6.5h8M2 10h12M6 13.5h8" stroke="currentColor" stroke-width="1.6"/></svg></button><button data-r="al-center" title="מרכז"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 3h12M4 6.5h8M2 10h12M4 13.5h8" stroke="currentColor" stroke-width="1.6"/></svg></button><button data-r="al-left" title="יישור לשמאל"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 3h12M2 6.5h8M2 10h12M2 13.5h8" stroke="currentColor" stroke-width="1.6"/></svg></button></span><span class="xl-grp"><select data-r="nf" title="תבנית מספר"><option value="gen">כללי</option><option value="num">מספר</option><option value="cur">מטבע</option><option value="pct">אחוזים</option><option value="acc">חשבונאי ( )</option></select><button data-r="cur" title="תבנית מטבע">₪</button><button data-r="pct" title="סגנון אחוזים (Ctrl+Shift+%)">%</button><button data-r="comma" title="סגנון פסיק">,</button><button data-r="dec+" title="הגדלת מקומות עשרוניים" class="xl-dec"><span dir="ltr">.0<svg class="xl-ar" viewBox="0 0 10 8" aria-hidden="true"><path d="M1 4h7M5.5 1.5 8 4 5.5 6.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>.00</span></button><button data-r="dec-" title="הקטנת מקומות עשרוניים" class="xl-dec"><span dir="ltr">.00<svg class="xl-ar" viewBox="0 0 10 8" aria-hidden="true"><path d="M1 4h7M5.5 1.5 8 4 5.5 6.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>.0</span></button></span></div><div class="xl-top"><div class="xl-name" title="תיבת השם">A1</div><div class="xl-fx">fx</div><input class="xl-bar" dir="ltr" spellcheck="false" autocomplete="off"></div>
  <div class="xl-tools">${cfg.tools===false?'':`<button data-x="formulas" title="הצגת נוסחאות">נוסחאות</button>`}${cfg.targets?`<button data-x="check" class="xl-go">✔ בדיקה</button>${cfg.steps?'<button data-x="step" class="xl-st">▶ הצעד הבא</button>':''}${cfg.hints?'<button data-x="hint">💡 רמז</button>':''}${cfg.remind?'<button data-x="remind">📐 תזכורת נוסחה</button>':''}${cfg.partial?'<button data-x="part">פתרון חלקי</button>':''}<button data-x="solve">פתרון מלא</button>`:''}<button data-x="reset">איפוס</button><span class="xl-msg"></span></div>
  <div class="xl-wrap"${cfg.maxh?` style="max-height:${cfg.maxh}px"`:''}><table class="xl-g" tabindex="0"><thead><tr><th class="xl-c0"></th>${Array.from({length:C},(_,c)=>`<th style="width:${W[c]||92}px">${colName(c)}</th>`).join('')}</tr></thead><tbody>${Array.from({length:R-R0},(_,k)=>k+R0).map(r=>`<tr><th class="xl-rn">${r+1}</th>${Array.from({length:C},(_,c)=>`<td data-a="${addr(r,c)}"></td>`).join('')}</tr>`).join('')}</tbody></table></div>
  ${cfg.targets?'<div class="xl-fb"></div>':''}`;
 const g=host.querySelector('.xl-g'),bar=host.querySelector('.xl-bar'),nameB=host.querySelector('.xl-name'),msg=host.querySelector('.xl-msg'),fb=host.querySelector('.xl-fb');
 /* hidden text sink: catches typing from on-screen keyboards and IMEs that send input events without a usable key */
 const sink=document.createElement('textarea');sink.className='xl-sink';sink.setAttribute('aria-hidden','true');sink.tabIndex=-1;sink.spellcheck=false;host.appendChild(sink);
 const focusG=()=>sink.focus({preventScroll:true});
 sink.addEventListener('input',()=>{const v=sink.value;sink.value='';if(!editing&&v)startEdit(v.trim()===''?'':v,false);});
 const td=a=>g.querySelector(`td[data-a="${a}"]`);
 const setFb=h=>{if(!fb)return;fb.innerHTML=h;if(cfg.onFb)cfg.onFb();};
 let sel={r:R0,c:0},sel2={r:R0,c:0},editing=null,showF=false,marks={},hintN=0;
 /* a sheet can open on a given cell (the row of the current transaction), scrolled into view */
 if(cfg.start){const p=parseAddr(cfg.start);if(p){sel={...p};sel2={...p};}}
 /* ---------- the Home ribbon, as in Excel: undo, font, fill, alignment and number format ---------- */
 const UNDO=[],REDO=[];let lastSt=null,undoing=false;
 const LAY=['data','bdata','solution','targets','zone','inputs','headRows','steps','traps','partial','vin','soft','fmt','need','build','sty'];
 const lay=()=>{const o={};LAY.forEach(k=>{if(cfg[k]!==undefined)o[k]=cfg[k];});return o;};const ORIG=JSON.stringify(lay());
 const state=()=>JSON.stringify([S.raw,S.fmt,S.sty,lay()]);
 function snap(){const st=state();if(st===lastSt)return;if(lastSt!==null&&!undoing){UNDO.push(lastSt);if(UNDO.length>100)UNDO.shift();REDO.length=0;}lastSt=st;undoing=false;}
 function restore(st){const [r,f,y,l]=JSON.parse(st);S.raw=r;S.fmt=f;S.sty=y;if(l)Object.assign(cfg,l);undoing=true;render();if(cfg.onChange)cfg.onChange();}
 function undo(){if(!UNDO.length)return;REDO.push(lastSt);const st=UNDO.pop();lastSt=st;restore(st);}
 function redo(){if(!REDO.length)return;UNDO.push(lastSt);const st=REDO.pop();lastSt=st;restore(st);}
 const eachSel=fn=>{for(let r=Math.min(sel.r,sel2.r);r<=Math.max(sel.r,sel2.r);r++)for(let c=Math.min(sel.c,sel2.c);c<=Math.max(sel.c,sel2.c);c++)fn(addr(r,c));};
 const sty=a=>S.sty[a]||(S.sty[a]={});
 function toggleSty(k,v){const a0=addr(sel.r,sel.c),on=(S.sty[a0]||{})[k]===v;eachSel(a=>{const y=sty(a);if(on)delete y[k];else y[k]=v;if(!Object.keys(y).length)delete S.sty[a];});render();}
 /* the decimals a cell shows now, read from its format or, in General, from what it displays */
 function kindDec(a){const f=S.fmt[a]||'';const m=/^(pct|num|cur|acc)(\d)$/.exec(f);if(m)return [m[1],+m[2]];
  const raw=S.raw[a]||'';const t=display(S,a).t||'';const k=(f==='pct'||(!f&&raw[0]!=='='&&raw.includes('%')))?'pct':'num';const dm=/\.(\d+)/.exec(t);return [k,dm?dm[1].length:0];}
 function numFmt(x){eachSel(a=>{const [k,d]=kindDec(a);
   if(x==='pct')S.fmt[a]='pct0';else if(x==='comma')S.fmt[a]='num2';else if(x==='cur')S.fmt[a]='cur2';
   else if(x==='dec+')S.fmt[a]=k+Math.min(6,d+1);else if(x==='dec-')S.fmt[a]=k+Math.max(0,d-1);
   else if(x==='gen')delete S.fmt[a];else if(x==='num')S.fmt[a]='num2';else if(x==='acc')S.fmt[a]='acc0';else if(x==='num0')S.fmt[a]='num0';});render();}
 function ribState(){const rb=host.querySelector('.xl-rib');if(!rb)return;const a=addr(sel.r,sel.c),y=S.sty[a]||{};
  ['b','i','u'].forEach(k=>rb.querySelector(`[data-r="${k}"]`).classList.toggle('on',!!y[k]));
  ['right','center','left'].forEach(k=>rb.querySelector(`[data-r="al-${k}"]`).classList.toggle('on',y.al===k));
  rb.querySelector('[data-r="fill"]').classList.toggle('on',!!y.fill);
  const f=S.fmt[a]||'',nf=rb.querySelector('[data-r="nf"]');nf.value=/^pct/.test(f)?'pct':/^cur/.test(f)?'cur':/^acc/.test(f)?'acc':/^num/.test(f)?'num':'gen';
  rb.querySelector('[data-r="undo"]').disabled=!UNDO.length;rb.querySelector('[data-r="redo"]').disabled=!REDO.length;}
 function ribDo(x){if(editing)commit(0,0);
  if(x==='undo')return undo();if(x==='redo')return redo();
  if(x==='b'||x==='i'||x==='u')return toggleSty(x,true);
  if(x==='fill')return pal(host.querySelector('[data-r="fill"]'));if(x==='row+')return rowOp(Math.min(sel.r,sel2.r),1);if(x==='row-')return rowOp(Math.min(sel.r,sel2.r),-1);
  if(x.startsWith('al-'))return toggleSty('al',x.slice(3));
  numFmt(x);}
 const inSel=(r,c)=>r>=Math.min(sel.r,sel2.r)&&r<=Math.max(sel.r,sel2.r)&&c>=Math.min(sel.c,sel2.c)&&c<=Math.max(sel.c,sel2.c);
 const selName=()=>sel.r===sel2.r&&sel.c===sel2.c?addr(sel.r,sel.c):addr(Math.min(sel.r,sel2.r),Math.min(sel.c,sel2.c))+':'+addr(Math.max(sel.r,sel2.r),Math.max(sel.c,sel2.c));
 /* the header rows at the top of the table stay frozen together, like Freeze Panes on two rows */
 function frzTop(row){const hs=(cfg.headRows||[]).slice().sort((a,b)=>a-b);let top=g.tHead.offsetHeight;for(let i=0;i<hs.length;i++){if(hs[i]!==hs[0]+i)return null;if(hs[i]===row)return top;const c=td(addr(hs[i]-1,0));top+=c?c.offsetHeight:0;}return null;}
 function render(){S.recalc();
  g.querySelectorAll('td').forEach(el=>{const a=el.dataset.a;if(editing&&editing.a===a)return;const p=parseAddr(a);if(el.dataset.rf){el.style.boxShadow='';el.style.backgroundColor='';delete el.dataset.rf;}
   const raw=S.raw[a];let d=display(S,a);if(showF&&raw&&raw[0]==='=')d={t:raw,n:false,f:true};
   el.className=(d.n?'n':'')+(d.f?' f':'')+(d.e?' e':'')+(inSel(p.r,p.c)?' sel':'')+(p.r===sel.r&&p.c===sel.c?' act':'')+(cfg.inputs&&cfg.inputs.includes(a)?' in':'')+((cfg.targets&&cfg.targets.includes(a))||(cfg.zone&&cfg.zone.includes(a))?' tg':'')+(marks[a]?' '+marks[a]:'')+(cfg.headRows&&cfg.headRows.includes(p.r+1)?' hd':'');
   /* freeze the table's header row in a scrolling sheet, like Freeze Panes */
   if(cfg.maxh&&cfg.headRows&&cfg.headRows.length&&frzTop(p.r+1)!==null){el.classList.add('frz');el.style.top=frzTop(p.r+1)+'px';const rn=el.parentElement.firstElementChild;rn.classList.add('frz');rn.style.top=el.style.top;}
   const sy=S.sty[a]||{};el.style.fontWeight=sy.b?'700':'';el.style.fontStyle=sy.i?'italic':'';el.style.textDecoration=sy.u?'underline':'';el.style.textAlign=sy.al||'';el.style.backgroundImage=sy.fill?`linear-gradient(${sy.fill},${sy.fill})`:'';
   el.innerHTML=(d.n||d.f?`<span dir="ltr">${esc(d.t)}</span>`:esc(d.t))+(p.r===Math.max(sel.r,sel2.r)&&p.c===Math.max(sel.c,sel2.c)&&!editing?'<i class="xl-fh"></i>':'');});
  const ae=td(addr(sel.r,sel.c));if(ae&&cfg.maxh)keepVisible(ae);
  g.querySelectorAll('th.hs').forEach(x=>x.classList.remove('hs'));const hr=g.tHead.rows[0].cells;for(let c=Math.min(sel.c,sel2.c);c<=Math.max(sel.c,sel2.c);c++)hr[c+1].classList.add('hs');
  g.querySelectorAll('tbody th.xl-rn').forEach(th=>{const r=+th.textContent-1;if(r>=Math.min(sel.r,sel2.r)&&r<=Math.max(sel.r,sel2.r))th.classList.add('hs');});
  snap();ribState();
  nameB.textContent=selName();if(!editing||editing.where!=='bar')bar.value=S.raw[addr(sel.r,sel.c)]||'';barDir();
  if(cfg.onSelect)cfg.onSelect(selName());}
 /* ---------- editing, as in Excel: Enter mode (typing) and Edit mode (F2 or double click); references are coloured while a formula is written ---------- */
 const RC=['#1a73e8','#d93025','#8e24aa','#188038','#e37400','#00838f','#c2185b'];
 const REFRX=/("[^"]*")|(\$?[A-Za-z]{1,2}\$?\d+(?::\$?[A-Za-z]{1,2}\$?\d+)?)(?![\d(A-Za-z])/g;
 function refsOf(v){const out=[],col={};if(!v||v[0]!=='=')return out;let m;REFRX.lastIndex=0;
  while((m=REFRX.exec(v))){if(m[1])continue;const t=m[2],k=t.replace(/\$/g,'').toUpperCase();if(m.index>0&&/[A-Za-z_]/.test(v[m.index-1]))continue;
   if(!(k in col))col[k]=RC[Object.keys(col).length%RC.length];out.push({i:m.index,t,k,c:col[k]});}return out;}
 const tint=c=>c+'1f';
 function paintRefs(){g.querySelectorAll('td[data-rf]').forEach(el=>{el.style.boxShadow='';el.style.backgroundColor='';el.classList.remove('ptr');delete el.dataset.rf;});
  const inp=curInput();if(!inp)return;const done={};
  refsOf(inp.value).forEach(f=>{if(done[f.k])return;done[f.k]=1;const [a,b]=f.k.split(':'),A=parseAddr(a),B=parseAddr(b||a);if(!A||!B)return;
   const r0=Math.min(A.r,B.r),r1=Math.max(A.r,B.r),c0=Math.min(A.c,B.c),c1=Math.max(A.c,B.c);
   for(let r=r0;r<=r1;r++)for(let c=c0;c<=c1;c++){const el=td(addr(r,c));if(!el||(editing&&editing.a===addr(r,c)))continue;
    /* the sheet runs right to left: the lowest column is on the right edge */
    const sh=[];if(r===r0)sh.push(`inset 0 2px 0 ${f.c}`);if(r===r1)sh.push(`inset 0 -2px 0 ${f.c}`);if(c===c0)sh.push(`inset -2px 0 0 ${f.c}`);if(c===c1)sh.push(`inset 2px 0 0 ${f.c}`);
    el.style.boxShadow=sh.join(',');el.style.backgroundColor=tint(f.c);el.dataset.rf='1';}
   if(editing&&editing.ptr&&editing.ptr.start===f.i){const el=td(addr(r0,c0));if(el)el.classList.add('ptr');}});}
 /* the coloured text: an overlay that shows the same characters as the input, which is drawn transparent */
 function colourise(inp,ov){const v=inp.value,fs=refsOf(v);
  if(!fs.length||inp.scrollWidth>inp.clientWidth+1){ov.innerHTML='';inp.classList.remove('xl-clr');return;}
  let h='',k=0;fs.forEach(f=>{h+=esc(v.slice(k,f.i))+`<span style="color:${f.c}">${esc(f.t)}</span>`;k=f.i+f.t.length;});h+=esc(v.slice(k));
  /* the coloured copy must lie exactly over the typed text: same font, size, spacing and padding, or a click lands on another character */
  const cs=getComputedStyle(inp);ov.innerHTML=h;Object.assign(ov.style,{direction:cs.direction,font:cs.font,letterSpacing:cs.letterSpacing,paddingLeft:cs.paddingLeft,paddingRight:cs.paddingRight,textAlign:cs.textAlign,justifyContent:cs.textAlign==='right'||cs.textAlign==='end'&&cs.direction==='ltr'?'flex-end':'flex-start'});inp.classList.add('xl-clr');}
 const barOv=document.createElement('div');barOv.className='xl-ov xl-bov';bar.parentNode.insertBefore(barOv,bar);
 /* a formula, a number or an empty box reads left to right; only Hebrew text reads right to left */
 function barDir(){const v=bar.value,d=/[\u0590-\u05FF]/.test(v)&&!/^\s*[=+\-]/.test(v)?'rtl':'ltr';if(bar.dir!==d)bar.dir=d;}
 function sync(){const inp=curInput();if(!inp)return;if(inp!==bar)bar.value=inp.value;else{const el=td(editing.a).querySelector('input');if(el)el.value=bar.value;}barDir();
  const ci=td(editing.a).querySelector('input');if(ci){fitEditor(ci);colourise(ci,ci.previousSibling);}Object.assign(barOv.style,{left:bar.offsetLeft+'px',top:bar.offsetTop+'px',width:bar.offsetWidth+'px',height:bar.offsetHeight+'px'});colourise(bar,barOv);barOv.scrollLeft=bar.scrollLeft;paintRefs();}
 const meas=document.createElement('canvas').getContext('2d');
 function fitEditor(inp){meas.font=getComputedStyle(inp).font;const w=Math.ceil(meas.measureText(inp.value).width)+18;const box=inp.parentNode;box.style.width=Math.max(box.parentNode.clientWidth,w)+'px';}
 /* scroll the sheet so the cell is below the frozen headers and above the bottom edge; positions are measured against the scroll area (the stage is scaled) */
 function keepVisible(el){const w=host.querySelector('.xl-wrap'),wr=w.getBoundingClientRect(),k=wr.height/w.offsetHeight||1,r=el.getBoundingClientRect();
  const frs=[...new Set([...g.querySelectorAll('td.frz')].map(x=>x.parentElement))].filter(tr=>!tr.contains(el)),hb=g.tHead.offsetHeight+frs.reduce((t,tr)=>t+tr.offsetHeight,0);
  const top=(r.top-wr.top)/k+w.scrollTop,bot=(r.bottom-wr.top)/k+w.scrollTop;
  if(top<w.scrollTop+hb)w.scrollTop=Math.max(0,top-hb);else if(bot>w.scrollTop+w.clientHeight)w.scrollTop=bot-w.clientHeight;}
 function startEdit(initial,keep,mode){const a=addr(sel.r,sel.c);sel2={...sel};editing={a,where:'cell',orig:S.raw[a]||'',mode:mode||(keep?'edit':'enter'),ptr:null};const el=td(a);
  el.className+=' ed';el.innerHTML=`<div class="xl-ed"><div class="xl-ov" aria-hidden="true"></div><input class="xl-in" dir="auto" spellcheck="false" autocomplete="off"></div>`;const inp=el.querySelector('input');inp.value=keep?(S.raw[a]||''):initial;
  inp.focus({preventScroll:true});inp.setSelectionRange(inp.value.length,inp.value.length);
  inp.oninput=()=>{if(editing){editing.ptr=null;}sync();suggest();};inp.onkeydown=keyEdit;inp.onkeyup=inp.onclick=()=>sync();
  /* a click inside the cell being typed switches to Edit mode, as in Excel: the arrows then move the caret, and the click places it */
  inp.addEventListener('pointerdown',e=>{e.stopPropagation();if(editing&&editing.mode!=='edit'){editing.mode='edit';editing.ptr=null;modeTip();}});sync();modeTip();suggest();}

 /* function suggestions, as in Excel: letters typed after = or an operator open a list; Tab (or a click) writes the name and its opening bracket, so cells can be selected next */
 const FNS=['ABS','AVERAGE','COUNT','COUNTA','EFFECT','FV','IF','IRR','MAX','MIN','NOMINAL','NPER','NPV','PMT','POWER','PV','RATE','ROUND','SQRT','SUM','SUMPRODUCT'];
 function fnToken(){const inp=curInput();if(!inp||inp.value[0]!=='=')return null;const pre=inp.value.slice(0,inp.selectionStart);const m=/(^=|[=+\-*\/^(,:;<>&]\s*)([A-Za-z]+)$/.exec(pre);
  if(!m)return null;const w=m[2].toUpperCase();const L=FNS.filter(f=>f.startsWith(w));return L.length?{start:pre.length-m[2].length,end:pre.length,list:L}:null;}
 function hideSug(){const b=host.querySelector('.xl-sug');if(b)b.remove();if(editing)editing.sug=null;}
 function suggest(){hideSug();if(!editing||editing.where!=='cell')return;const t=fnToken();if(!t)return;editing.sug=t;const box=document.createElement('div');box.className='xl-sug';
  box.innerHTML=t.list.slice(0,6).map((f,i)=>`<div class="xl-sg${i?'':' on'}" data-f="${f}">${f}</div>`).join('')+'<div class="xl-sgh">Tab: בחירה</div>';
  box.addEventListener('mousedown',e=>{const d=e.target.closest('.xl-sg');if(d){e.preventDefault();acceptSug(d.dataset.f);}});
  /* placed on the sheet itself, outside the scroll area, so a low row does not clip it; above the cell when there is no room below */
  if(getComputedStyle(host).position==='static')host.style.position='relative';host.appendChild(box);
  const hr=host.getBoundingClientRect(),k=hr.width/host.offsetWidth||1,er=td(editing.a).getBoundingClientRect();
  let top=(er.bottom-hr.top)/k;const h=box.offsetHeight;if(top+h>host.offsetHeight&&(er.top-hr.top)/k-h>0)top=(er.top-hr.top)/k-h;
  box.style.top=top+'px';box.style.left=Math.max(0,(er.left-hr.left)/k)+'px';}
 function acceptSug(f){const inp=curInput(),t=editing&&editing.sug;if(!inp||!t)return false;f=f||t.list[0];inp.value=inp.value.slice(0,t.start)+f+'('+inp.value.slice(t.end);
  const p=t.start+f.length+1;inp.setSelectionRange(p,p);inp.focus({preventScroll:true});hideSug();editing.ptr=null;sync();toastX(`נכתב \u2066${f}(\u2069. עכשיו מסמנים את התאים`);return true;}
 function modeTip(){if(editing)toastX(editing.mode==='edit'?'מצב עריכה (F2): החצים מזיזים את הסמן':'מצב הזנה: אחרי אופרטור, החצים בוחרים תא');}
 function curInput(){return editing?(editing.where==='bar'?bar:td(editing.a).querySelector('input')):null;}
 function endEdit(){const sb=host.querySelector('.xl-sug');if(sb)sb.remove();editing=null;barOv.innerHTML='';bar.classList.remove('xl-clr');g.querySelectorAll('td[data-rf]').forEach(el=>{el.style.boxShadow='';el.style.backgroundColor='';el.classList.remove('ptr');delete el.dataset.rf;});}
 function pctEntry(a,v){if(!/^pct/.test(S.fmt[a]||'')||!/^-?(\d+(\.\d*)?|\.\d+)$/.test(v))return v;const x=parseFloat(v);return Math.abs(x)>=1?v+'%':v;}
 function commit(dr,dc){if(!editing)return;const v=pctEntry(editing.a,curInput().value.trim());S.set(editing.a,v);endEdit();move(dr,dc);render();focusG();if(cfg.onChange)cfg.onChange();}
 function cancel(){endEdit();render();focusG();}
 function move(dr,dc){sel={r:Math.max(R0,Math.min(R-1,sel.r+dr)),c:Math.max(0,Math.min(C-1,sel.c+dc))};sel2={...sel};}
 const NAV={ArrowDown:[1,0],ArrowUp:[-1,0],ArrowLeft:[0,1],ArrowRight:[0,-1]};
 const refTxt=(A,B)=>!B||(A.r===B.r&&A.c===B.c)?addr(A.r,A.c):addr(Math.min(A.r,B.r),Math.min(A.c,B.c))+':'+addr(Math.max(A.r,B.r),Math.max(A.c,B.c));
 /* point mode: put or replace the reference that the arrows, a click or a drag point at */
 function pointTo(anchor,cur){const inp=curInput(),p=editing.ptr,t=refTxt(anchor,cur);let st;
  if(p){st=p.start;inp.value=inp.value.slice(0,st)+t+inp.value.slice(st+p.len);}else{st=inp.selectionStart;inp.value=inp.value.slice(0,st)+t+inp.value.slice(inp.selectionEnd);}
  editing.ptr={start:st,len:t.length,anchor,cur};inp.setSelectionRange(st+t.length,st+t.length);inp.focus({preventScroll:true});sync();}
 function keyEdit(e){e.stopPropagation();
  if(e.key==='Enter'){e.preventDefault();commit(e.shiftKey?-1:1,0);return;}
  if(e.key==='Tab'){e.preventDefault();if(!e.shiftKey&&editing.sug&&acceptSug(editing.sug.pick))return;commit(0,e.shiftKey?-1:1);return;}
  if((e.key==='ArrowDown'||e.key==='ArrowUp')&&editing.sug){e.preventDefault();const t=editing.sug,n=Math.min(t.list.length,6);t.i=((t.i||0)+(e.key==='ArrowDown'?1:-1)+n)%n;t.pick=t.list[t.i];
   host.querySelectorAll('.xl-sg').forEach((d,k)=>d.classList.toggle('on',k===t.i));return;}
  if(e.key==='Escape'){e.preventDefault();cancel();return;}
  if(e.key==='F2'){e.preventDefault();editing.mode=editing.mode==='edit'?'enter':'edit';editing.ptr=null;modeTip();return;}
  if(NAV[e.key]&&editing.mode==='enter'){e.preventDefault();const d=NAV[e.key],p=editing.ptr;
   const base=p?p.cur:parseAddr(editing.a),nx={r:Math.max(R0,Math.min(R-1,base.r+d[0])),c:Math.max(0,Math.min(C-1,base.c+d[1]))};
   if(p){pointTo(e.shiftKey?p.anchor:nx,nx);return;}
   if(pointable()){pointTo(nx,nx);return;}
   commit(d[0],d[1]);return;}
  if(e.key==='F4'){e.preventDefault();const inp=e.target,v=inp.value,p=inp.selectionStart,rx=/\$?[A-Za-z]{1,2}\$?\d+/g;let m,hit=null;
   while((m=rx.exec(v)))if(m.index<=p&&p<=m.index+m[0].length)hit=m;
   if(hit){const q=/^(\$?)([A-Za-z]{1,2})(\$?)(\d+)$/.exec(hit[0]),st=(q[1]?2:0)+(q[3]?1:0),nx={0:3,3:1,1:2,2:0}[st];
    const nr=(nx&2?'$':'')+q[2]+(nx&1?'$':'')+q[4];inp.value=v.slice(0,hit.index)+nr+v.slice(hit.index+hit[0].length);
    const np=hit.index+nr.length;inp.setSelectionRange(np,np);if(editing.ptr&&editing.ptr.start===hit.index)editing.ptr.len=nr.length;sync();}}}
 const pointable=()=>{const inp=curInput();if(!inp)return false;if(editing.ptr)return true;const v=inp.value.slice(0,inp.selectionStart).trimEnd();return v[0]==='='&&/[=+\-*/^(,:;<>&]$/.test(v);};
 function insertRef(a){const p=parseAddr(a);pointTo(p,p);toastX(`נוספה הפניה לתא ${a}`);}
 function toastX(t){msg.textContent=t;clearTimeout(toastX.t);toastX.t=setTimeout(()=>{if(msg.textContent===t)msg.textContent='';},1800);}
 /* pointer: select, drag a range, insert a reference while writing a formula, or drag the fill handle */
 let drag=null;
 let lastDown=null;
 /* typing between two presses means they are two separate clicks, not a double click */
 host.addEventListener('keydown',()=>{lastDown=null;},true);
 g.addEventListener('pointerdown',e=>{const cell=e.target.closest('td');
  const twice=k=>{const now=e.timeStamp,hit=lastDown&&lastDown.k===k&&now-lastDown.t<450&&Math.abs(e.clientX-lastDown.x)<8&&Math.abs(e.clientY-lastDown.y)<8;lastDown=hit?null:{k,t:now,x:e.clientX,y:e.clientY};return hit;};
  if(e.target.classList.contains('xl-fh')){e.preventDefault();if(twice('fh')){fillDownAuto();return;}drag={k:'fill',b:blk(),to:null};try{g.setPointerCapture(e.pointerId);}catch(_){}return;}
  if(!cell)return;const p=parseAddr(cell.dataset.a);
  if(editing&&editing.a===cell.dataset.a)return;
  if(editing&&pointable()){e.preventDefault();insertRef(cell.dataset.a);drag={k:'ptr',a:p};try{g.setPointerCapture(e.pointerId);}catch(_){}return;}
  if(editing)commit(0,0);
  if(twice(cell.dataset.a)){e.preventDefault();sel={...p};sel2={...p};render();startEdit('',true,'edit');dblAt=e.timeStamp;return;}
  e.preventDefault();sel={...p};sel2={...p};drag={k:'sel'};try{g.setPointerCapture(e.pointerId);}catch(_){}render();focusG();});
 g.addEventListener('pointermove',e=>{if(!drag)return;
  /* dragging past the top or bottom edge of a scrolling sheet scrolls it, as in Excel */
  let y=e.clientY;const w=host.querySelector('.xl-wrap'),wr=w.getBoundingClientRect(),k=wr.height/w.offsetHeight||1,top=wr.top+(g.tHead.offsetHeight+((g.querySelector('td.frz')||{}).offsetHeight||0))*k;
  if(w.scrollHeight>w.clientHeight){if(y>wr.bottom-6){w.scrollTop+=24;y=wr.bottom-8;}else if(y<top+4&&w.scrollTop>0){w.scrollTop-=24;y=top+6;}}
  const el=document.elementFromPoint(e.clientX,y);const cell=el&&el.closest&&el.closest('td');if(!cell||!g.contains(cell))return;const p=parseAddr(cell.dataset.a);
  if(drag.k==='sel'){sel2=p;render();}
  else if(drag.k==='ptr'){if(editing&&editing.ptr&&(p.r!==editing.ptr.cur.r||p.c!==editing.ptr.cur.c))pointTo(drag.a,p);}
  else{const b=drag.b;const dv=p.r>b.r1?p.r-b.r1:p.r<b.r0?b.r0-p.r:0,dh=p.c>b.c1?p.c-b.c1:p.c<b.c0?b.c0-p.c:0;
   const to=!dv&&!dh?null:dv>=dh?{r0:Math.min(b.r0,p.r),r1:Math.max(b.r1,p.r),c0:b.c0,c1:b.c1,v:1}:{r0:b.r0,r1:b.r1,c0:Math.min(b.c0,p.c),c1:Math.max(b.c1,p.c),v:0};drag.to=to;
   g.querySelectorAll('td.fillp').forEach(x=>x.classList.remove('fillp'));
   if(to)for(let r=to.r0;r<=to.r1;r++)for(let c=to.c0;c<=to.c1;c++)td(addr(r,c)).classList.add('fillp');}});
 g.addEventListener('pointerup',e=>{if(!drag)return;const d=drag;drag=null;try{g.releasePointerCapture(e.pointerId);}catch(_){}
  if(d.k==='fill'){g.querySelectorAll('td.fillp').forEach(x=>x.classList.remove('fillp'));if(d.to)fill(d.b,d.to);}});
 /* fill a selected block (one cell or several) down/up or sideways, repeating the block like Excel */
 function blk(){return{r0:Math.min(sel.r,sel2.r),r1:Math.max(sel.r,sel2.r),c0:Math.min(sel.c,sel2.c),c1:Math.max(sel.c,sel2.c)};}
 const md=(a,n)=>((a%n)+n)%n;
 const plainNum=x=>x!=null&&x!==''&&String(x)[0]!=='='&&NUMRX.test(String(x));
 function fill(b,to){const h=b.r1-b.r0+1,w=b.c1-b.c0+1;
  const series={};if(to.v&&h>1)for(let c=b.c0;c<=b.c1;c++){const vs=[];for(let r=b.r0;r<=b.r1;r++)vs.push(S.raw[addr(r,c)]);if(vs.every(plainNum)){const n=vs.map(x=>parseFloat(x));series[c]={a:n[0],st:(n[n.length-1]-n[0])/(n.length-1),pc:vs.every(x=>String(x).includes('%'))};}}
  if(!to.v&&w>1)for(let r=b.r0;r<=b.r1;r++){const vs=[];for(let c=b.c0;c<=b.c1;c++)vs.push(S.raw[addr(r,c)]);if(vs.every(plainNum)){const n=vs.map(x=>parseFloat(x));series['r'+r]={a:n[0],st:(n[n.length-1]-n[0])/(n.length-1),pc:vs.every(x=>String(x).includes('%'))};}}
  for(let r=to.r0;r<=to.r1;r++)for(let c=to.c0;c<=to.c1;c++){if(r>=b.r0&&r<=b.r1&&c>=b.c0&&c<=b.c1)continue;
   const sr=to.v?b.r0+md(r-b.r0,h):r,sc=to.v?c:b.c0+md(c-b.c0,w);const src=addr(sr,sc),raw=S.raw[src],a=addr(r,c);
   const se=to.v?series[c]:series['r'+r];if(se){const k=to.v?r-b.r0:c-b.c0;S.set(a,String(Math.round((se.a+se.st*k)*1e9)/1e9)+(se.pc?'%':''));if(S.fmt[src])S.fmt[a]=S.fmt[src];continue;}
   S.set(a,raw==null?'':shift(raw,r-sr,c-sc));if(S.fmt[src])S.fmt[a]=S.fmt[src];else delete S.fmt[a];}
  sel={r:to.r0,c:to.c0};sel2={r:to.r1,c:to.c1};render();toastX('הנוסחה שוכפלה, וההפניות התעדכנו בכל תא');if(cfg.onChange)cfg.onChange();}
 let dblAt=-1e9;
 function fillDownAuto(){const b=blk();let last=b.r1;for(let r=b.r1+1;r<R;r++){const nb=[b.c0-1,b.c1+1].some(c=>c>=0&&c<C&&S.raw[addr(r,c)]!=null);if(nb)last=r;else break;}
  if(last>b.r1)fill(b,{r0:b.r0,r1:last,c0:b.c0,c1:b.c1,v:1});dblAt=performance.now();}
 g.addEventListener('dblclick',e=>{if(Math.abs(e.timeStamp-dblAt)<700||editing)return;/* pointer capture sends the event to the table: find the cell under the pointer */const tgt=document.elementFromPoint(e.clientX,e.clientY)||e.target;if(tgt.classList&&tgt.classList.contains('xl-fh')){fillDownAuto();return;}
  const cell=(tgt.closest&&tgt.closest('td'))||e.target.closest('td');if(!cell||!g.contains(cell))return;sel=parseAddr(cell.dataset.a);sel2={...sel};startEdit('',true,'edit');});
 const gKey=e=>{if(editing)return;const k=e.key;
  const mod=e.ctrlKey||e.metaKey;
  /* by the physical key (e.code), so it works in any keyboard layout: in Hebrew the C key types ב and the V key types ה */
  const kc0=e.code||'',isC=kc0==='KeyC'||(!kc0&&/^[cCב]$/.test(k)),isX=kc0==='KeyX'||(!kc0&&/^[xXס]$/.test(k)),isV=kc0==='KeyV'||(!kc0&&/^[vVה]$/.test(k));
  if(mod&&!e.shiftKey&&(isC||isX)){e.preventDefault();e.stopPropagation();const b=blk(),cut=isX;
   /* the whole selected block is copied, cell by cell, with its formats */
   CLIP={r0:b.r0,c0:b.c0,h:b.r1-b.r0+1,w:b.c1-b.c0+1,cells:[]};
   for(let r=b.r0;r<=b.r1;r++){const row=[];for(let c=b.c0;c<=b.c1;c++){const a=addr(r,c);row.push({raw:S.raw[a],fmt:S.fmt[a]});}CLIP.cells.push(row);}
   try{navigator.clipboard&&navigator.clipboard.writeText(CLIP.cells.map(row=>row.map(x=>x.raw==null?'':x.raw).join('\t')).join('\n')).catch(()=>{});}catch(_){}
   if(cut){eachSel(a=>S.set(a,''));render();if(cfg.onChange)cfg.onChange();}
   toastX((cut?'נגזר':'הועתק')+(CLIP.h*CLIP.w>1?` (${CLIP.h*CLIP.w} תאים)`:'')+'. סמנו תא או טווח, והדביקו ב-Ctrl+V');return;}
  if(mod&&!e.shiftKey&&isV){e.preventDefault();e.stopPropagation();if(!CLIP||!CLIP.cells)return;
   /* one target cell: the block lands from it. A larger target: the block repeats over it, as in Excel */
   const b=blk(),th=Math.max(CLIP.h,b.r1-b.r0+1),tw=Math.max(CLIP.w,b.c1-b.c0+1);
   for(let i=0;i<th;i++)for(let j=0;j<tw;j++){const r=b.r0+i,c=b.c0+j;if(r>=R||c>=C)continue;const si=i%CLIP.h,sj=j%CLIP.w,src=CLIP.cells[si][sj],a=addr(r,c);
    S.set(a,src.raw==null?'':shift(src.raw,r-(CLIP.r0+si),c-(CLIP.c0+sj)));if(src.fmt)S.fmt[a]=src.fmt;}
   sel={r:b.r0,c:b.c0};sel2={r:Math.min(R-1,b.r0+th-1),c:Math.min(C-1,b.c0+tw-1)};
   render();if(cfg.onChange)cfg.onChange();return;}
  if(mod&&(k==='`'||k===';')){e.preventDefault();e.stopPropagation();toggleF();return;}
  const kc=e.code||'';
  if(mod&&!e.shiftKey&&(kc==='KeyZ'||kc==='KeyY'||kc==='KeyB'||kc==='KeyI'||kc==='KeyU'||kc==='KeyA')){e.preventDefault();e.stopPropagation();
   if(kc==='KeyZ')undo();else if(kc==='KeyY')redo();else if(kc==='KeyA'){sel={r:R0,c:0};sel2={r:R-1,c:C-1};render();}else ribDo(kc[3].toLowerCase());return;}
  if(mod&&e.shiftKey&&(kc==='Digit5'||kc==='Digit1'||kc==='Digit4')){e.preventDefault();e.stopPropagation();ribDo(kc==='Digit5'?'pct':kc==='Digit1'?'comma':'cur');return;}
  if(mod&&e.shiftKey&&kc==='KeyZ'){e.preventDefault();e.stopPropagation();redo();return;}
  /* Ctrl + arrow jumps to the edge of the data block, as in Excel */
  const jmp={ArrowDown:[1,0],ArrowUp:[-1,0],ArrowLeft:[0,1],ArrowRight:[0,-1]}[k];
  if(mod&&jmp){e.preventDefault();e.stopPropagation();const has=(r,c)=>S.raw[addr(r,c)]!=null;let r=sel.r,c=sel.c;const ok=(r,c)=>r>=R0&&r<R&&c>=0&&c<C;
   const nr=r+jmp[0],nc=c+jmp[1];if(ok(nr,nc)){if(has(r,c)&&has(nr,nc)){while(ok(r+jmp[0],c+jmp[1])&&has(r+jmp[0],c+jmp[1])){r+=jmp[0];c+=jmp[1];}}
    else{r=nr;c=nc;while(!has(r,c)&&ok(r+jmp[0],c+jmp[1])){r+=jmp[0];c+=jmp[1];}}}
   if(e.shiftKey)sel2={r,c};else{sel={r,c};sel2={r,c};}render();return;}
  if(k==='Home'&&!e.shiftKey){e.preventDefault();e.stopPropagation();sel={r:mod?R0:sel.r,c:0};sel2={...sel};render();return;}
  const nav={ArrowDown:[1,0],ArrowUp:[-1,0],ArrowLeft:[0,1],ArrowRight:[0,-1],Enter:[e.shiftKey?-1:1,0],Tab:[0,e.shiftKey?-1:1]};
  if(nav[k]){e.preventDefault();e.stopPropagation();if(e.shiftKey&&k.startsWith('Arrow')){sel2={r:Math.max(R0,Math.min(R-1,sel2.r+nav[k][0])),c:Math.max(0,Math.min(C-1,sel2.c+nav[k][1]))};}else move(...nav[k]);render();return;}
  if(k==='F2'){e.preventDefault();e.stopPropagation();startEdit('',true,'edit');return;}
  if(k==='Delete'||k==='Backspace'){e.preventDefault();e.stopPropagation();for(let r=Math.min(sel.r,sel2.r);r<=Math.max(sel.r,sel2.r);r++)for(let c=Math.min(sel.c,sel2.c);c<=Math.max(sel.c,sel2.c);c++)S.set(addr(r,c),'');render();if(cfg.onChange)cfg.onChange();return;}
  if(k===' '||k.length===1&&!mod){e.preventDefault();e.stopPropagation();startEdit(k===' '?'':k,false);return;}
  if(k==='Escape'||k==='PageDown'||k==='PageUp'||k==='Home'||k==='End')e.stopPropagation();};
 g.addEventListener('keydown',gKey);sink.addEventListener('keydown',gKey);
 bar.addEventListener('focus',()=>{if(!editing){editing={a:addr(sel.r,sel.c),where:'bar',orig:S.raw[addr(sel.r,sel.c)]||'',mode:'edit',ptr:null};}});
 bar.addEventListener('input',()=>{if(editing){editing.ptr=null;sync();}});bar.addEventListener('scroll',()=>{barOv.scrollLeft=bar.scrollLeft;});
 bar.addEventListener('keydown',keyEdit);
 bar.addEventListener('blur',()=>{if(editing&&editing.where==='bar')setTimeout(()=>{if(editing&&editing.where==='bar'&&document.activeElement!==bar)commit(0,0);},120);});
 function toggleF(){showF=!showF;host.querySelector('[data-x="formulas"]')&&host.querySelector('[data-x="formulas"]').classList.toggle('on',showF);render();}
 {const rb=host.querySelector('.xl-rib');
  rb.addEventListener('pointerdown',e=>{if(e.target.closest('button'))e.preventDefault();});
  rb.addEventListener('click',e=>{const b=e.target.closest('button');if(!b||b.disabled)return;ribDo(b.dataset.r);focusG();});
  rb.querySelector('select').addEventListener('change',e=>{ribDo(e.target.value);focusG();});}
 /* a click on a column letter or a row number selects the whole column or row */
 g.tHead.addEventListener('pointerdown',e=>{const th=e.target.closest('th');if(!th||th.classList.contains('xl-c0'))return;const c=th.cellIndex-1;if(c<0)return;e.preventDefault();if(editing)commit(0,0);
  if(e.shiftKey){sel2={r:R-1,c};}else{sel={r:R0,c};sel2={r:R-1,c};}render();focusG();});
 g.tBodies[0].addEventListener('pointerdown',e=>{const th=e.target.closest('th.xl-rn');if(!th)return;e.preventDefault();e.stopPropagation();if(editing)commit(0,0);const r=+th.textContent-1;
  if(e.shiftKey){sel2={r,c:C-1};}else{sel={r,c:0};sel2={r,c:C-1};}render();focusG();},true);
 host.querySelector('.xl-tools').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;const x=b.dataset.x;
  if(x==='pct'){for(let r=Math.min(sel.r,sel2.r);r<=Math.max(sel.r,sel2.r);r++)for(let c=Math.min(sel.c,sel2.c);c<=Math.max(sel.c,sel2.c);c++){const a=addr(r,c);S.fmt[a]=/^pct/.test(S.fmt[a]||'')?'':'pct';}render();}
  if(x==='formulas')toggleF();
  if(x==='hint'&&fb){const i=hintN%cfg.hints.length;hintN++;setFb(`<div class="xl-tip"><b>רמז ${i+1} מתוך ${cfg.hints.length}:</b> ${cfg.hints[i]}</div>`);}
  if(x==='remind'&&fb){setFb(`<div class="xl-tip">${cfg.remind}</div>`);}
  if(x==='part'){cfg.partial.forEach(a=>{S.set(a,cfg.solution[a]);});render();if(fb)setFb('<div class="xl-tip">השורה הראשונה מולאה. המשיכו מכאן: גררו את ידית המילוי או כתבו לבד.</div>');if(cfg.onChange)cfg.onChange();}
  if(x==='reset'){Object.assign(cfg,JSON.parse(ORIG));load();marks={};hintN=0;stepK=0;{const b=host.querySelector('[data-x="step"]');if(b)b.textContent='▶ הצעד הבא';}if(fb)setFb('');sel={r:R0,c:0};sel2={...sel};render();if(cfg.onChange)cfg.onChange();}
  if(x==='solve'){Object.entries(cfg.solution).forEach(([a,v])=>S.set(a,v));Object.assign(S.fmt,cfg.solFmt||{});render();check(true);if(cfg.onChange)cfg.onChange();}
  if(x==='check')check(false);
  if(x==='step')stepNext();});
 /* step by step demonstration: each step writes its formulas into the sheet and explains them; the lecturer can go on with the deck's next key */
 function buildTo(k,note){bk=Math.max(0,Math.min(BL.length,k));const keep={};Object.keys(S.raw).forEach(a=>{if(!(a in cfg.data)&&!(cfg.bdata&&a in cfg.bdata))keep[a]=S.raw[a];});load();Object.entries(keep).forEach(([a,v])=>S.set(a,v));
  marks={};if(note&&bk>0)BL[bk-1].cells.forEach(a=>marks[a]='bld');render();
  if(note&&bk>0)setFb(`<div class="xl-step"><b>בניית התבנית, שלב ${bk} מתוך ${BL.length}:</b> ${BL[bk-1].note}${bk===BL.length?' <b>התבנית מוכנה. עכשיו ממלאים.</b>':''}</div>`);else if(!note)setFb('');}
 let stepK=0;
 function stepNext(){if(!cfg.steps)return;if(bk<BL.length)buildTo(BL.length,false);if(stepK>=cfg.steps.length){stepK=0;load();}const st=cfg.steps[stepK];if(editing)cancel();
  Object.entries(st.cells).forEach(([a,f])=>S.set(a,f));marks={};Object.keys(st.cells).forEach(a=>marks[a]='stp');
  const ks=Object.keys(st.cells);sel=parseAddr(st.sel||ks[0]);sel2=parseAddr(st.sel2||st.sel||ks[0]);render();
  stepK++;const last=stepK===cfg.steps.length;
  if(fb)setFb(`<div class="xl-step"><b>צעד ${stepK} מתוך ${cfg.steps.length}:</b> ${st.note}${last?' <b>זה הפתרון המלא.</b>':''}</div>`);
  const b=host.querySelector('[data-x="step"]');if(b)b.textContent=last?'↺ מההתחלה':'▶ הצעד הבא';if(cfg.onChange)cfg.onChange();}
 /* checking: the value must match, the cell must hold a formula with references (unless the solution has none: =14*12 converts years to months), and no number from the table may be typed in */
 const needOf=a=>cfg.need?(typeof cfg.need==='object'?cfg.need[a]:cfg.need):null;
 function check(silent){const sol=new Sheet(R,C);Object.entries({...cfg.data,...(cfg.bdata||{})}).forEach(([a,v])=>sol.set(a,v));Object.entries(cfg.solution).forEach(([a,v])=>sol.set(a,v));sol.recalc();
  S.recalc();marks={};const notes=[];let ok=0;
  cfg.targets.forEach(a=>{const raw=S.raw[a]||'',want=sol.val[a],got=S.val[a];const sf=cfg.solution[a]||'';
   const lits=s=>(s.replace(/\$?[A-Za-z]{1,2}\$?\d+/g,' ').match(/\d+(\.\d+)?/g)||[]).map(Number);
   const allowed=new Set([...lits(sf),...(cfg.allow||[0,1])]);let why='';
   const tol=w=>cfg.tol!=null?cfg.tol:Math.max(1e-6,1e-9*Math.abs(w));const near=(x,w)=>typeof x==='number'&&typeof w==='number'&&Math.abs(x-w)<=tol(w);
   /* the period column is a label (0, 1, 2 or the payment date): whatever is written there, it is never an error, and it counts as done */
   if(cfg.soft&&cfg.soft.includes(a)){marks[a]=raw?'ok':'';ok++;return;}
   if(cfg.vin&&cfg.vin.includes(a)){const pc=/^pct/.test(cfg.fmt&&cfg.fmt[a]||'');let w='';
    if(!raw)w='ריק: הזינו את הנתון מהשאלה';else if(isErr(got))w=`שגיאה ${got.err}`;
    else if(!near(got,want))w=pc&&near(got/100,want)?'זה אחוז: כתבו אותו עם סימן האחוז, למשל 5%':pc&&near(got*100,want)?'האחוז קטן פי 100 מהנדרש. כתבו את האחוז כפי שהוא בשאלה, למשל 5%':'הערך אינו תואם את הנתון בשאלה. קראו שוב את השאלה';
    if(w){marks[a]='bad';notes.push(`<b>${a}:</b> ${w}`);}else{marks[a]='ok';ok++;}return;}
   const nf=x=>String(x).toUpperCase().replace(/\s+/g,'').replace(/;/g,',');const exact=((cfg.traps&&cfg.traps[a])||[]).find(([f])=>nf(f)===nf(raw));
   if(exact&&!(typeof want==='number'&&near(got,want)))why=exact[1];
   else if(!raw)why='ריק';else if(raw[0]!=='='&&cfg.values){if(!near(got,want))why='המספר אינו נכון. חשבו שוב לפי ההסבר';}else if(raw[0]!=='=')why='הוקלד ערך ולא נוסחה. נוסחה מתחילה בסימן =';
   else if(isErr(got))why=`שגיאה ${got.err}: בדקו את הכתיב ואת הסוגריים`;
   else if(raw[0]==='='&&!/[A-Za-z]{1,2}\d/.test(raw.replace(/\$/g,'').replace(/[A-Z]+\(/g,''))&&/[A-Za-z]{1,2}\d/.test(sf.replace(/\$/g,'').replace(/[A-Z]+\(/g,''))&&!cfg.values)why='אין בנוסחה הפניה לתאים. השתמשו בכתובות התאים במקום במספרים';
   else if(raw[0]==='='&&!cfg.values&&lits(raw).some(x=>!allowed.has(x)))why='הוקלד בנוסחה מספר. כשהנתון קיים בטבלה, מפנים לתא שלו';
   else if(needOf(a)&&!new RegExp(needOf(a),'i').test(raw))why=(/^קבעו/.test(cfg.needMsg||'')?'קיבוע: ':'עבודה יעילה: ')+(cfg.needMsg||'יש פונקציה מתאימה לפעולה הזו');
   else if(typeof want==='number'&&!near(got,want)){why=cfg.wrongMsg||'התוצאה אינה נכונה. בדקו את סדר הפעולות ואת התאים שבחרתם';
    /* a known mistake gets its own explanation: the trap formula is evaluated on the solved sheet and compared with the student's value */
    const tr=(cfg.traps&&cfg.traps[a])||[];for(const [f,m] of tr){const T=new Sheet(R,C);Object.entries({...cfg.data,...(cfg.bdata||{})}).forEach(([k,v])=>T.set(k,v));Object.entries(cfg.solution).forEach(([k,v])=>T.set(k,v));T.set(a,f);T.recalc();if(near(got,T.val[a])){why=m;break;}}
    if(why===(cfg.wrongMsg||'התוצאה אינה נכונה. בדקו את סדר הפעולות ואת התאים שבחרתם')&&near(-got,want)&&want!==0)why=cfg.signMsg||'הסימן הפוך. פונקציות המימון באקסל מחזירות תשלום כמספר שלילי. הוסיפו מינוס לפני הפונקציה, או הפכו את סימן התזרים';}
   if(why){marks[a]='bad';notes.push(`<b>${a}:</b> ${why}`);}else{marks[a]='ok';ok++;}});
  render();const all=ok===cfg.targets.length;
  if(fb)setFb(all?`<div class="xl-ok">✔ כל ${ok} התאים נכונים${silent?' (פתרון לדוגמה)':''}.${cfg.done?' '+cfg.done:''}</div>`:`<div class="xl-no">נכונים ${ok} מתוך ${cfg.targets.length}.</div><div class="xl-notes">${notes.slice(0,2).join('<br>')}${notes.length>2?' ועוד '+(notes.length-2)+' תאים.':''}</div>`);
  if(all&&!silent)host.dataset.solved='1';if(cfg.onChange)cfg.onChange();}
 render();

 /* ---------- right-click menu, fill colours, inserting and deleting rows (Shay, 2026-11-12) ---------- */
 const FILLS=[['#fff2cc','צהוב'],['#ffd966','זהב'],['#c6efce','ירוק'],['#ddebf7','תכלת'],['#bdd7ee','כחול'],['#fce4d6','אפרסק'],['#f8cbad','כתום'],['#e4dfec','סגול'],['#d9d9d9','אפור']];
 function setFill(c){eachSel(a=>{const y=sty(a);if(c)y.fill=c;else delete y.fill;if(!Object.keys(y).length)delete S.sty[a];});render();focusG();}
 const swatches=()=>'<div class="xl-sw">'+FILLS.map(([c,n])=>`<button data-fill="${c}" title="${n}" style="background:${c}"></button>`).join('')+'<button data-fill="" class="xl-nofill" title="ללא מילוי">✕</button></div>';
 let POPS=[];function closePop(){POPS.forEach(x=>x.remove());POPS=[];}
 /* menus live on the slide itself, so the edge of the sheet never clips them; they stay inside the slide */
 function placePop(el,x,y){const L=host.closest('.slide')||host;if(getComputedStyle(L).position==='static')L.style.position='relative';L.appendChild(el);POPS.push(el);el.addEventListener('click',popClick);el.addEventListener('pointerdown',e=>{e.stopPropagation();e.preventDefault();});
  const hr=L.getBoundingClientRect(),k=hr.width/L.offsetWidth||1;let left=(x-hr.left)/k,top=(y-hr.top)/k;const w=el.offsetWidth,h=el.offsetHeight,W=L.offsetWidth,H=L.offsetHeight;
  if(left+w>W-6)left=Math.max(6,left-w);if(top+h>H-6)top=Math.max(6,H-6-h);el.style.left=left+'px';el.style.top=top+'px';}
 function pal(btn){closePop();const p=document.createElement('div');p.className='xl-pal';p.innerHTML='<div class="xl-palh">צבע מילוי</div>'+swatches();const r=btn.getBoundingClientRect();placePop(p,r.left,r.bottom);}
 /* a row inserted at index i moves every row from i down by one; a row deleted at i moves the rows below it up. Formulas, the
    solution, the checked cells and every explanation step move with the cells, as in Excel. */
 function mapRow(r,i,d){if(d>0)return r>=i?r+1:r;if(r===i)return null;return r>i?r-1:r;}
 function mapA(a,i,d){const p=parseAddr(a);if(!p)return a;const r=mapRow(p.r,i,d);return r===null?null:addr(r,p.c);}
 function mapF(raw,i,d){if(typeof raw!=='string'||raw[0]!=='=')return raw;
  return '='+raw.slice(1).replace(/("[^"]*")|(\$?)([A-Za-z]{1,2})(\$?)(\d+)(?::(\$?)([A-Za-z]{1,2})(\$?)(\d+))?(?![\d(A-Za-z])/g,(m,str,d1,L,d2,R1,e1,L2,e2,R2)=>{if(str)return str;
   const r1=+R1-1;if(R2===undefined){const r=mapRow(r1,i,d);return r===null?'#REF!':d1+L+d2+(r+1);}
   let a=r1,b=+R2-1;if(d>0){if(a>=i)a++;if(b>=i)b++;}else{if(a===i&&b===i)return '#REF!';if(a>i)a--;if(b>=i)b--;}
   return d1+L+d2+(a+1)+':'+e1+L2+e2+(b+1);});}
 const mapObj=(o,i,d,vf)=>{if(!o||typeof o!=='object'||Array.isArray(o))return o;const n={};Object.entries(o).forEach(([a,v])=>{const k=mapA(a,i,d);if(k)n[k]=vf?vf(v):v;});return n;};
 const mapArr=(L,i,d)=>Array.isArray(L)?L.map(a=>mapA(a,i,d)).filter(Boolean):L;
 function rowOp(i,d){if(editing)commit(0,0);closePop();
  if(d>0){for(let c=0;c<C;c++)if(S.raw[addr(R-1,c)]!=null){toastX('אין מקום: השורה האחרונה של הגיליון אינה ריקה');return;}}
  const f=v=>mapF(v,i,d);
  S.raw=mapObj(S.raw,i,d,f);S.fmt=mapObj(S.fmt,i,d);S.sty=mapObj(S.sty,i,d);if(cfg.sty)cfg.sty=mapObj(cfg.sty,i,d);
  ['data','bdata','solution'].forEach(k=>{if(cfg[k])cfg[k]=mapObj(cfg[k],i,d,f);});cfg.fmt=mapObj(cfg.fmt,i,d);
  ['targets','zone','inputs','partial','vin','soft'].forEach(k=>{if(cfg[k])cfg[k]=mapArr(cfg[k],i,d);});
  if(cfg.need&&typeof cfg.need==='object')cfg.need=mapObj(cfg.need,i,d);
  if(cfg.traps)cfg.traps=mapObj(cfg.traps,i,d,L=>L.map(([x,m])=>[f(x),m]));
  if(cfg.headRows)cfg.headRows=cfg.headRows.map(h=>{const r=mapRow(h-1,i,d);return r===null?null:r+1;}).filter(x=>x!==null);
  if(cfg.steps)cfg.steps=cfg.steps.map(st=>({...st,cells:mapObj(st.cells,i,d,f),...(st.sel?{sel:mapA(st.sel,i,d)||st.sel}:{}),...(st.sel2?{sel2:mapA(st.sel2,i,d)||st.sel2}:{})}));
  if(cfg.build)cfg.build=cfg.build.map(st=>({...st,cells:mapArr(st.cells,i,d)}));
  marks={};render();toastX(d>0?'נוספה שורה. הנוסחאות שמתחת עודכנו':'השורה נמחקה. הנוסחאות עודכנו');if(cfg.onChange)cfg.onChange();focusG();}
 function clearSel(){if(editing)commit(0,0);eachSel(a=>S.set(a,''));render();if(cfg.onChange)cfg.onChange();focusG();}
 function keyTo(code,shift){gKey(new KeyboardEvent('keydown',{key:code.slice(-1).toLowerCase(),code,ctrlKey:true,metaKey:false,shiftKey:!!shift,bubbles:true}));}
 function ctxMenu(x,y){closePop();const m=document.createElement('div');m.className='xl-cm';m.setAttribute('role','menu');
  const it=(k,t,kb)=>`<button data-cm="${k}" role="menuitem"><span>${t}</span>${kb?`<kbd dir="ltr">${kb}</kbd>`:''}</button>`;
  m.innerHTML=it('cut','גזירה','Ctrl+X')+it('copy','העתקה','Ctrl+C')+it('paste','הדבקה','Ctrl+V')+'<hr>'+it('ins','הוספת שורה מעל')+it('insb','הוספת שורה מתחת')+it('del','מחיקת השורה')+it('clr','ניקוי תוכן','Delete')
   +'<hr>'+it('b','מודגש','Ctrl+B')+'<div class="xl-cmh">צבע מילוי</div>'+swatches()+'<hr><div class="xl-cmh">עיצוב תאים</div><div class="xl-cmf">'
   +[['gen','כללי'],['num0','מספר 1,000'],['acc','חשבונאי (1,000)'],['pct','אחוזים'],['cur','₪']].map(([k,t])=>`<button data-cmf="${k}">${t}</button>`).join('')+'</div><hr>'+it('undo','ביטול','Ctrl+Z');
  placePop(m,x,y);}
 function popClick(e){e.stopPropagation();const sw=e.target.closest('[data-fill]');if(sw){setFill(sw.dataset.fill);closePop();return;}
  const f=e.target.closest('[data-cmf]');if(f){closePop();if(editing)commit(0,0);numFmt(f.dataset.cmf);focusG();return;}
  const b=e.target.closest('[data-cm]');if(b){const k=b.dataset.cm;closePop();
   if(k==='cut')keyTo('KeyX');else if(k==='copy')keyTo('KeyC');else if(k==='paste')keyTo('KeyV');else if(k==='ins')rowOp(Math.min(sel.r,sel2.r),1);
   else if(k==='insb')rowOp(Math.max(sel.r,sel2.r)+1,1);else if(k==='del')rowOp(Math.min(sel.r,sel2.r),-1);else if(k==='clr')clearSel();else if(k==='b')ribDo('b');else if(k==='undo')undo();focusG();return;}}
 document.addEventListener('pointerdown',e=>{if(POPS.length&&!e.target.closest('.xl-pal,.xl-cm,[data-r="fill"]'))closePop();},true);
 g.addEventListener('contextmenu',e=>{const cell=e.target.closest('td');if(!cell)return;e.preventDefault();e.stopPropagation();if(editing)commit(0,0);const p=parseAddr(cell.dataset.a);
  if(!inSel(p.r,p.c)){sel={...p};sel2={...p};render();}ctxMenu(e.clientX,e.clientY);});
 return {sheet:S,render,select:(a)=>{sel=parseAddr(a);sel2={...sel};render();},put:(a,v)=>{S.set(a,v);render();if(cfg.onChange)cfg.onChange();},stepNext:()=>stepNext(),buildPending:()=>bk<BL.length,buildNext:()=>buildTo(bk+1,true),buildBack:()=>buildTo(bk-1,true),buildAll:()=>{if(bk<BL.length)buildTo(BL.length,false);},buildBackAll:()=>buildTo(0,false),buildCount:()=>BL.length,built:()=>bk,stepActive:()=>!!cfg.steps&&stepK>0&&stepK<cfg.steps.length,stepCount:()=>stepK,putMany:o=>{Object.entries(o).forEach(([a,v])=>S.set(a,v));render();if(cfg.onChange)cfg.onChange();},get:a=>S.val[a],raw:a=>S.raw[a],check,reset:()=>host.querySelector('[data-x="reset"]').click(),showFormulas:v=>{if(showF!==!!v)toggleF();},
  fmtSel:fn=>{for(let r=Math.min(sel.r,sel2.r);r<=Math.max(sel.r,sel2.r);r++)for(let c=Math.min(sel.c,sel2.c);c<=Math.max(sel.c,sel2.c);c++){const a=addr(r,c),f=fn(S.fmt[a]||'',S.val[a],display(S,a).t);if(f)S.fmt[a]=f;else delete S.fmt[a];}render();},
  fmtAt:a=>S.fmt[a]||'',active:()=>addr(sel.r,sel.c),onSel:fn=>{cfg.onSelect=fn;}};}
const api={mount,shift,Sheet,addr,parseAddr,colName,tokenize,parse,FIN};if(typeof window!=='undefined')window.__XL=api;return api;
})();
