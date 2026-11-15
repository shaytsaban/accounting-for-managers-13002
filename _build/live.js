/* ===== live Excel practice: the engine of the Excel courses (xlengine.js), mounted beside a question ===== */
(function(){
const XLE=window.__XL;if(!XLE)return;
$$('.xlq').forEach(b=>{const cfg=JSON.parse(b.dataset.cfg),host=$('.sheet',b);
 cfg.onFb=()=>{const sl=b.closest('.slide');if(sl&&sl.classList.contains('on')&&window.__fitSheets)window.__fitSheets(sl);};
 const api=XLE.mount(host,cfg);host.__api=api;
 /* the explanation of each step and the feedback sit under the question, beside the sheet */
 const fbx=$('.xl-fb',host),side=$('.xfbs',b);if(fbx&&side)side.appendChild(fbx);b.__fb=fbx;});
/* a long question leaves no room under it: the step notes go under the sheet instead */
function placeFb(slide){slide.querySelectorAll('.xlq').forEach(b=>{const f=b.__fb;if(!f)return;const q=b.querySelector('.qr .tasktxt')||b.querySelector('.qr .card.qstem'),st=document.getElementById('stage'),k=st.getBoundingClientRect().width/1280;const qb=(q.getBoundingClientRect().bottom-st.getBoundingClientRect().top)/k;const low=qb>600;(low?b.querySelector('.xw'):b.querySelector('.xfbs')).appendChild(f);b.classList.toggle('fbu',low);
 /* a question that fills its column: the instruction line goes above the sheet */
 const t=b.querySelector('.tasktxt'),c=b.querySelector('.qr .card.qstem');if(t&&c){const cb=(c.getBoundingClientRect().bottom-st.getBoundingClientRect().top)/k;if(cb>620&&t.parentElement.classList.contains('qr'))b.querySelector('.xw').prepend(t);}});}

/* each sheet uses the free height of its slide: the scroll area reaches the bottom of the slide */
window.__fitSheets=function(slide){placeFb(slide);const st=document.getElementById('stage'),sr=st.getBoundingClientRect(),k=sr.width/1280||1,limit=(slide.querySelector('.ft')?720-40-6:706);
 slide.querySelectorAll('.xl-wrap').forEach(w=>{
  const tb=w.querySelector('table'),ths=[...tb.tHead.rows[0].cells].slice(1);ths.forEach(th=>{if(!th.dataset.w0)th.dataset.w0=parseFloat(th.style.width)||92;th.style.width=th.dataset.w0+'px';});
  const base=ths.reduce((t,th)=>t+ +th.dataset.w0,0),wroom=w.clientWidth-36-2-16;if(wroom>base+8){const f=Math.min(1.6,wroom/base);ths.forEach(th=>{th.style.width=Math.floor(th.dataset.w0*f)+'px';});}
  w.style.maxHeight='none';const top=(w.getBoundingClientRect().top-sr.top)/k,need=w.scrollHeight,under=w.closest('.fbu')?96:0,room=Math.floor(limit-top-under);
  w.style.maxHeight=Math.max(110,Math.min(need,room))+'px';});
 slide.querySelectorAll('.xfbs .xl-fb,.fbu .xw>.xl-fb').forEach(f=>{f.style.maxHeight='none';const t=(f.getBoundingClientRect().top-sr.top)/k;f.style.maxHeight=Math.max(60,Math.floor(limit-t-6))+'px';});
 slide.querySelectorAll('.sheet').forEach(h=>{if(h.__api&&h.__api.render)h.__api.render();});};
const on=$('.slide.on');if(on)window.__fitSheets(on);
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{const s=$('.slide.on');if(s)window.__fitSheets(s);});
})();
