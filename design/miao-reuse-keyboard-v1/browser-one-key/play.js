import {SampledAudio} from '../../../public/sampled-audio.js';
import {MELODY} from '../../../public/bindings.js';
import {createPressMotion} from './motion.js';
import {loadOneKeyModel} from './model.js';
const $=id=>document.getElementById(id),audio=new SampledAudio({loadTimeoutMs:45000}),note=MELODY.find(key=>key.code==='KeyA'),motion=createPressMotion(),held=new Set();
let model=null,preparing=false,ready=false,raf=0,lastAmount=-1,hits=0,audioUntil=0,maxRms=0,maxRendered=0,lastInputMs=0,contactRecorded=false;
function animate(now){
  raf=0;if(!model)return;const pose=motion.sample(now);
  if(pose.amount!==lastAmount){model.setPose(pose.amount);model.render();lastAmount=pose.amount;maxRendered=Math.max(maxRendered,pose.amount);$('scene').dataset.maxRenderedAmount=maxRendered.toFixed(6);if(!contactRecorded&&pose.phase!=='retrigger'&&pose.amount>=model.meta.contactFraction){contactRecorded=true;$('scene').dataset.contactRenderLatencyMs=(Number($('scene').dataset.lastRenderedMs)-lastInputMs).toFixed(3);}}
  $('note').classList.toggle('pressed',pose.amount>.3);
  const level=audio.level();maxRms=Math.max(maxRms,level);$('meter').style.transform=`scaleX(${Math.min(1,level*18)})`;
  $('scene').dataset.peakRms=maxRms.toFixed(7);$('scene').dataset.audioState=audio.context?.state||'none';
  if(pose.needsFrame||now<audioUntil)raf=requestAnimationFrame(animate);
}
function wake(){if(!raf)raf=requestAnimationFrame(animate);}
function syncHold(){const on=held.has('latch');$('hold').setAttribute('aria-pressed',String(on));$('hold').textContent=on?'松开 C4':'按住 C4';}
function press(source){
  if(!ready||held.has(source)||(held.has('latch')&&source!=='latch'))return;
  try{audio.play(note,'piano');}catch{ready=false;stop();$('status').textContent='声音暂停了，请重新开琴。';$('gate').hidden=false;$('prepare').disabled=false;$('prepare').textContent='重新开琴';return;}
  const now=performance.now();held.add(source);motion.press(now);hits++;audioUntil=now+2200;maxRms=maxRendered=0;lastInputMs=now;contactRecorded=false;delete $('scene').dataset.contactRenderLatencyMs;
  $('scene').dataset.inputCount=String(hits);$('scene').dataset.lastInputMs=now.toFixed(3);$('status').textContent='C4';syncHold();wake();
}
function release(source){if(!held.delete(source))return;if(!held.size){motion.release(performance.now());wake();}syncHold();}
function stop(){held.clear();motion.reset(performance.now());audio.stopVoices();audioUntil=0;syncHold();if(model){model.setPose(0);model.render();lastAmount=0;}$('note').classList.remove('pressed');$('meter').style.transform='scaleX(0)';$('status').textContent=ready?'松开了，再来一声。':'先开琴，再弹一下。';if(raf){cancelAnimationFrame(raf);raf=0;}}
$('prepare').addEventListener('click',async()=>{
  if(preparing)return;preparing=true;$('prepare').disabled=true;$('status').textContent='正在准备琴声和模型…';
  try{
    // Unlock Web Audio during the human click, before waiting for the model.
    await Promise.all([audio.ready('piano'),model?Promise.resolve():loadOneKeyModel($('scene'),event=>{$('status').textContent=`模型加载中 · ${(event.loaded/1000000).toFixed(1)} MB`;}).then(value=>{model=value;})]);
    ready=true;$('gate').hidden=true;$('poster').hidden=true;for(const id of['note','hold','stop'])$(id).disabled=false;
    $('status').textContent='可以弹了，按 A。';$('scene').dataset.audioState=audio.context.state;wake();
  }catch(error){$('status').textContent='这次没准备好，可以重试。';$('scene').dataset.error=error.message;$('prepare').textContent='重试开琴';}
  finally{preparing=false;$('prepare').disabled=false;}
});
$('note').addEventListener('pointerdown',event=>{event.preventDefault();$('note').setPointerCapture(event.pointerId);press('pointer:'+event.pointerId);});
for(const type of['pointerup','pointercancel','lostpointercapture'])$('note').addEventListener(type,event=>release('pointer:'+event.pointerId));
$('note').addEventListener('click',event=>{if(event.detail===0){press('accessible');release('accessible');}});
$('hold').addEventListener('click',()=>{if(held.has('latch'))release('latch');else press('latch');});
$('stop').addEventListener('click',stop);
addEventListener('keydown',event=>{if(event.code!=='KeyA'||event.repeat||event.metaKey||event.ctrlKey||event.altKey)return;event.preventDefault();press('keyboard');});
addEventListener('keyup',event=>{if(event.code==='KeyA')release('keyboard');});
addEventListener('blur',stop);addEventListener('resize',()=>model?.render());
addEventListener('pagehide',event=>{stop();if(!event.persisted)model?.destroy();});
