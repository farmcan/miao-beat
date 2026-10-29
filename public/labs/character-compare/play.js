import {SampledAudio} from '../../sampled-audio.js';
import {MELODY,CHORDS} from '../../bindings.js';
import {mountCharacter} from '../../full-frame-character.js';
import {createCompareMotion} from './motion-controller.js';

const $=id=>document.getElementById(id),notes=MELODY.filter(key=>!key.black),keys=[...notes,...CHORDS],byCode=new Map(keys.map(key=>[key.code,key]));
const held=new Set(),audio=new SampledAudio({loadTimeoutMs:45000}),motion=createCompareMotion();
const originalScene=$('original'),original=mountCharacter(originalScene);
let preparing=null,audioReady=false,hits=0,events=[],demoTimers=[],demoVersion=0,activeView='whole',three=null,threeLoading=null,destroyed=false,lastPose=[0,0,0,0,0];
async function loadThree(){
  if(three||threeLoading||destroyed)return;
  const button=$('loadThree'),canvas=$('threeScene');
  button.disabled=true;button.textContent='加载3D中…';delete canvas.dataset.error;delete canvas.dataset.ready;canvas.dataset.loadState='loading';
  $('threeStatus').textContent='3D下载与初始化中 · 原版可继续弹奏';
  threeLoading=(async()=>{
    let candidate;
    try{
      const {createThreeCharacter}=await import('./three-renderer.js');
      if(destroyed)return;
      candidate=createThreeCharacter(canvas,text=>{$('threeStatus').textContent=text;});
      if(!await candidate.ready)throw Error('模型或WebGL初始化未完成');
      if(destroyed){candidate.destroy();return;}
      three=candidate;three.setView(activeView);three.setOrbit(Number($('orbit').value));
      // Sample now: completed inputs are never replayed after a slow download.
      lastPose=motion.sample(performance.now(),{headEnabled:$('headMotion').checked});
      three.setPose(lastPose);canvas.hidden=false;canvas.dataset.loadState='ready';
      $('threePlaceholder').hidden=true;three.render();
      $('threeStatus').textContent='3D已就绪 · 同步当前姿态，可拖动转视角';
    }catch(error){
      candidate?.destroy();three=null;$('threePlaceholder').hidden=false;canvas.hidden=true;delete canvas.dataset.ready;canvas.dataset.loadState='failed';
      $('threeStatus').textContent='3D加载失败 · 可重试，原版与声音仍可使用';
      button.textContent='重试加载3D';
    }finally{button.disabled=false;threeLoading=null;}
  })();
  return threeLoading;
}
$('loadThree').addEventListener('click',loadThree);
function noteIndex(key){return key.kind==='note'?notes.findIndex(k=>k.code===key.code):[1,3,5,2][CHORDS.indexOf(key)];}
function message(text){$('status').textContent=text;}
function drawPressed(){for(const b of document.querySelectorAll('[data-code]'))b.classList.toggle('pressed',held.has(b.dataset.code));}
function syncHeld(){original.update('guitar',[...held].map(code=>byCode.get(code)).filter(Boolean));drawPressed();}
for(const key of keys){
  const button=document.createElement('button');button.type='button';button.dataset.code=key.code;button.setAttribute('aria-label',`${key.kind==='chord'?key.label+'和弦':key.sub}，键盘 ${key.key}`);
  if(key.kind==='note'){const letter=document.createElement('kbd'),label=document.createElement('small');letter.textContent=key.key;label.textContent=key.sub;button.append(letter,label);$('notes').append(button);}
  else{const letter=document.createElement('small');letter.textContent=key.key;button.append(letter,document.createTextNode(key.label));$('chords').append(button);}
  button.addEventListener('pointerdown',event=>{event.preventDefault();if(held.has(key.code))return;button.setPointerCapture(event.pointerId);held.add(key.code);syncHeld();play(key);});
  for(const type of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(type,()=>{held.delete(key.code);syncHeld();});
  button.addEventListener('click',event=>{if(event.detail===0)play(key);});
}
audio.onProgress=()=>{if(preparing){const progress=audio.getLoadProgress('guitar');message(`声音加载中 · ${progress.loaded}/${progress.total}`);}};
async function prepare(){
  if(preparing)return preparing;
  if(audioReady&&audio.context?.state==='running')return true;
  $('enableAudio').disabled=true;message('第一次加载吉他音色…');
  preparing=(async()=>{try{await audio.ready('guitar');audioReady=true;$('enableAudio').textContent='声音已打开';message('声音已就绪，请重新按键。两路共用这一份声音。');return true;}catch(error){audioReady=false;$('enableAudio').textContent='重试声音';message('音色未加载成功，请点重试。');return false;}finally{$('enableAudio').disabled=false;preparing=null;}})();
  return preparing;
}
function play(key,{demo=false}={}){
  if(!demo)cancelDemo();
  if(!audioReady||audio.context?.state!=='running'){prepare();message('声音正在准备，这次按键未发声；就绪后请重新按键。');return false;}
  try{
    const now=performance.now();audio.play(key,'guitar',audio.context.currentTime+.025);original.strike(key,'guitar');motion.strike(noteIndex(key),now);
    hits++;$('hits').value=String(hits);events.push({code:key.code,at:now,demo});if(events.length>500)events=events.slice(-500);
    document.body.dataset.inputs=String(hits);originalScene.dataset.compareInputs=String(hits);$('threeScene').dataset.inputs=String(hits);
    message(`${key.key} · ${key.kind==='chord'?key.label+' 和弦':key.sub}　一次输入，${three?'两路同步':'原版响应 · 3D尚未就绪'}`);return true;
  }catch(error){message('这一声没有完成：'+error.message);return false;}
}
function cancelDemo(){demoVersion++;for(const timer of demoTimers)clearTimeout(timer);demoTimers=[];}
function stop(text='已停止，没有排队动作。'){
  cancelDemo();held.clear();syncHeld();audio.stopVoices();original.reset();motion.reset(performance.now());lastPose=[0,0,0,0,0];three?.setPose(lastPose);message(text);
}
async function demo(gap){
  cancelDemo();const version=demoVersion;
  if(!await prepare()||version!==demoVersion||destroyed)return;
  stop('相同输入演示中…');
  notes.forEach((key,index)=>demoTimers.push(setTimeout(()=>play(key,{demo:true}),index*gap)));
  demoTimers.push(setTimeout(()=>{demoTimers=[];message('演示结束，换你弹。');},notes.length*gap+250));
}
$('enableAudio').addEventListener('click',prepare);$('slowDemo').addEventListener('click',()=>demo(500));$('fastDemo').addEventListener('click',()=>demo(150));$('stop').addEventListener('click',()=>stop());
const excluded=target=>target?.closest?.('input,select,textarea,a,[contenteditable=true]');
addEventListener('keydown',event=>{if(event.repeat||event.isComposing||event.altKey||event.ctrlKey||event.metaKey||excluded(event.target)||!byCode.has(event.code)||held.has(event.code))return;event.preventDefault();held.add(event.code);syncHeld();play(byCode.get(event.code));});
addEventListener('keyup',event=>{held.delete(event.code);syncHeld();});
function deactivate(text){const hadInput=hits>0||held.size>0||demoTimers.length>0,previous=$('status').textContent;stop(text);if(!hadInput)message(previous);}
addEventListener('blur',()=>deactivate('页面离开，演奏已停止。'));document.addEventListener('visibilitychange',()=>{if(document.hidden)deactivate('页面隐藏，演奏已停止。');});
function setView(name){activeView=name;three?.setView(name);const config={whole:[1,.5,.5],hands:[1.25,.5,.48],face:[2.7,.5,.22]}[name];const [z,x,y]=config;const canvas=originalScene.querySelector('canvas');if(canvas)canvas.style.transform=`translate(${(.5-x)*z*100}%,${(.5-y)*z*100}%) scale(${z})`;for(const button of document.querySelectorAll('[data-view]'))button.setAttribute('aria-pressed',String(button.dataset.view===name))}
for(const button of document.querySelectorAll('[data-view]'))button.addEventListener('click',()=>setView(button.dataset.view));
function setSolo(lane){for(const card of document.querySelectorAll('[data-lane]'))card.hidden=lane!=='all'&&card.dataset.lane!==lane;$('lanes').classList.toggle('solo',lane!=='all');}
for(const button of document.querySelectorAll('[data-solo]'))button.addEventListener('click',()=>setSolo(button.dataset.solo));$('showAll').addEventListener('click',()=>setSolo('all'));
$('orbit').addEventListener('input',()=>three?.setOrbit(Number($('orbit').value)));
originalScene.addEventListener('guitar-motion-status',event=>{$('originalStatus').textContent=event.detail==='ready'?'原版动作已就绪':event.detail==='loading'?'原版动作加载中…':'动作尚未加载，先显示完整姿态';});
original.ready.then(ok=>{if(!ok)$('originalStatus').textContent='原版图未加载，请刷新';else if(originalScene.dataset.guitarMotion!=='ready')$('originalStatus').textContent='完整画面就绪 · 动作加载中…';});
function frame(now){if(destroyed)return;lastPose=motion.sample(now,{headEnabled:$('headMotion').checked});three?.setPose(lastPose);three?.render();document.body.dataset.pose=lastPose.map(n=>n.toFixed(3)).join(',');requestAnimationFrame(frame);}
requestAnimationFrame(frame);
addEventListener('pagehide',()=>{destroyed=true;cancelDemo();audio.stopVoices();original.destroy();three?.destroy();});
