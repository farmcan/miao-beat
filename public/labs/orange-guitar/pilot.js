import {SampledAudio} from '../../sampled-audio.js';
import {CHORDS} from '../../bindings.js';
const strum=document.querySelector('#strum'),fret=document.querySelector('#fret'),ensemble=document.querySelector('#ensemble'),status=document.querySelector('#ready');
const audio=new SampledAudio(),buttons=[...document.querySelectorAll('[data-key]')],reduced=matchMedia('(prefers-reduced-motion: reduce)');
let motion=null,bodyMotion=null,load=null,ready=false,angle=-6,currentKey=null,startTime=0,epoch=0,hits=0;
const root=[223,255],source=[212,875],scale=.46;
const pose=a=>`translate(${root[0]}px,${root[1]}px) rotate(${a}deg) scale(${scale}) translate(${-source[0]}px,${-source[1]}px)`;
// Fret arm is a fixed supporting silhouette. Chords never invent finger articulation.
strum.style.transform=pose(angle);fret.style.transform='translate(428px,346px) rotate(0deg) scale(.27) translate(-805px,-1042px)';
const pressed=new Set();
const paintPressed=()=>buttons.forEach(b=>b.classList.toggle('active',pressed.has(b.dataset.key)));
const now=()=>performance.now();
function sampleAngle(){
 if(!motion)return angle;
 const t=Math.min(1,(now()-startTime)/230);
 if(t<.26)return angle+(9-angle)*t/.26;
 if(t<.5)return 9;
 return 9+(-6-9)*(t-.5)/.5;
}
function move(){
 const from=sampleAngle();motion?.cancel();angle=from;startTime=now();
 if(reduced.matches){strum.style.transform=pose(3);return;}
 motion=strum.animate([{transform:pose(from),offset:0},{transform:pose(9),offset:.26},{transform:pose(9),offset:.5},{transform:pose(-6),offset:1}],{duration:230,easing:'linear'});
 if(!bodyMotion||bodyMotion.playState==='finished')bodyMotion=ensemble.animate([{transform:'rotate(0deg)'},{transform:'rotate(.55deg)',offset:.35},{transform:'rotate(0deg)'}],{duration:310,easing:'ease-out'});ensemble.style.transformOrigin='325px 480px';
 const own=motion;own.onfinish=()=>{if(motion===own){motion=null;angle=-6;strum.style.transform=pose(-6);}};
}
async function trigger(key){
 if(!ready){
  if(load)return;
  status.textContent='准备吉他音色…';
  load=audio.ready('guitar').then(()=>{ready=true;status.textContent='声音准备好了，再按一下和弦。';}).catch(()=>{status.textContent='音色准备失败，点一下重试。';status.classList.add('error');}).finally(()=>{load=null;});
  return;
 }
 const chord=CHORDS.find(c=>String(c.key)===key);if(!chord)return;
 const ownEpoch=epoch;
 try{await audio.ready('guitar');if(ownEpoch!==epoch||document.hidden)return;audio.play(chord,'guitar');}
 catch{status.textContent='声音暂时无法播放，请再按一次。';return;}
 move();currentKey=key;status.dataset.hits=String(++hits);
 paintPressed();status.textContent=chord.label+' · 轻扫';
}
function release(key){pressed.delete(key);paintPressed();if(currentKey===key)currentKey=null;if(reduced.matches&&!pressed.size)strum.style.transform=pose(-6);}
for(const b of buttons){b.addEventListener('pointerdown',e=>{e.preventDefault();b.setPointerCapture(e.pointerId);pressed.add(b.dataset.key);paintPressed();trigger(b.dataset.key);});b.addEventListener('pointerup',()=>release(b.dataset.key));b.addEventListener('pointercancel',()=>release(b.dataset.key));b.addEventListener('click',e=>{if(e.detail===0)trigger(b.dataset.key);});}
addEventListener('keydown',e=>{if(!['1','2','3','4'].includes(e.key)||e.repeat||e.altKey||e.ctrlKey||e.metaKey)return;e.preventDefault();pressed.add(e.key);paintPressed();trigger(e.key);});addEventListener('keyup',e=>release(e.key));
function reset(){epoch++;motion?.cancel();motion=null;bodyMotion?.cancel();bodyMotion=null;angle=-6;strum.style.transform=pose(-6);pressed.clear();release(currentKey);}
addEventListener('blur',reset);document.addEventListener('visibilitychange',()=>{if(document.hidden)reset();});reduced.addEventListener('change',reset);
function meter(){status.dataset.peak=audio.peak.toFixed(5);audio.level();requestAnimationFrame(meter);}meter();
