import {KEYS,MELODY,DRUMS,CHORDS,LEGACY_KEYS} from './bindings.js';
import {SampledAudio} from './sampled-audio.js';
import {BeatClock} from './clock.js';
import {SONGS,scoreEvents} from './scores.js';
import {CODES,MAX_MS,MAX_EVENTS,makeRecording,validateRecording} from './recording.js';
const $=id=>document.getElementById(id),audio=new SampledAudio(),byCode=new Map(KEYS.map(k=>[k.code,k])),byNote=new Map(MELODY.map(k=>[k.sub,k]));
const scene=$('scene'),status=$('soundStatus'),held=new Set(),pulses=new Map();
audio.onProgress=()=>{if(!loading)return;const p=audio.getLoadProgress($('instrumentSelect').value);status.dataset.loaded=String(p.loaded);status.dataset.total=String(p.total);status.textContent=`正在准备真实采样 ${p.loaded} / ${p.total}，加载好后就可以演奏。`;};
let loading=0,presetEpoch=0;
let hits=0,frame=0,meterUntil=0,beatUntil=0,session=null,recording=null,recordStart=null,recordPending=false,importPending=false,lifecycle=0;
const clock=new BeatClock(audio,beat=>{
  for(const item of $('beatIndicator').children)item.classList.toggle('active',Number(item.dataset.beat)===beat);
  scene.classList.add('beat-pulse');beatUntil=performance.now()+160;
});
for(const key of MELODY){
  const b=document.createElement('button');b.type='button';b.className='music-key '+(key.black?'black':'white');b.dataset.code=key.code;
  if(key.black)b.style.setProperty('--key-position',key.position);
  b.setAttribute('aria-label',`${key.sub}，键盘 ${key.key}`);b.innerHTML=`<kbd>${key.key}</kbd><span class="note-label">${key.label}</span><span class="note-sub">${key.sub}</span>`;
  $('melodyKeys').append(b);
}
for(const key of DRUMS){
  const b=document.createElement('button');b.type='button';b.className='drum-pad';b.dataset.code=key.code;b.setAttribute('aria-label',`${key.label}，键盘 ${key.key}`);
  b.innerHTML=`<kbd>${key.key}</kbd><span><span class="pad-label">${key.label}</span><span class="pad-sub">${key.sub}</span></span>`;$('drumPads').append(b);
}
for(const key of CHORDS){const b=document.createElement('button');b.type='button';b.className='chord-pad';b.dataset.code=key.code;b.setAttribute('aria-label',`吉他 ${key.label} 和弦，键盘 ${key.key}`);b.innerHTML=`<kbd>${key.key}</kbd><strong>${key.label}</strong><small>轻扫</small>`;$('chordPads').append(b);}
const buttons=new Map([...document.querySelectorAll('[data-code]')].map(b=>[b.dataset.code,b]));
function paint(){
  for(const [code,b]of buttons)b.classList.toggle('active',held.has(code)||pulses.has(code));
  for(const side of ['left','right']){
    scene.classList.toggle(side+'-down',KEYS.some(k=>k.paw===side&&held.has(k.code)));
    scene.classList.toggle('hit-'+side,KEYS.some(k=>k.paw===side&&pulses.has(k.code)));
  }
}
function visual(key){
  clearTimeout(pulses.get(key.code));pulses.set(key.code,setTimeout(()=>{pulses.delete(key.code);paint();},160));paint();
  $('nowPlaying').textContent=key.kind==='note'?`${key.sub} · ${key.label}`:key.label;scene.dataset.hits=String(++hits);
}
function runFrame(){
  const now=audio.context?.currentTime??0;
  if(session){
    while(session.visuals.length&&session.visuals[0].time<=now){const e=session.visuals.shift();visual(byCode.get(e.code));if(e.index!==undefined){document.querySelector('.score-note.playing')?.classList.remove('playing');document.querySelector(`[data-score-index="${e.index}"]`)?.classList.add('playing');}}
    if(session.cursor===session.events.length&&now>session.end+.1){const kind=session.kind;stopSession(true);(kind==='score'?$('scoreStatus'):$('recordingStatus')).textContent=kind==='score'?'示范结束。现在换你随手弹一段。':'回放结束。';}
  }
  clock.render();
  if(performance.now()>beatUntil)scene.classList.remove('beat-pulse');
  const rms=audio.level();$('signal').style.setProperty('--level',Math.min(1,rms*7));$('signal').setAttribute('aria-valuenow',String(Math.round(Math.min(1,rms*7)*100)));$('signal').dataset.peak=audio.peak.toFixed(5);
  if(recordStart!==null){
    const duration=Math.min(MAX_MS,Math.round((now-recordStart)*1000));$('recordingInfo').textContent=`${(duration/1000).toFixed(1)} 秒 · ${recording.events.length} 次敲击`;
    if(duration>=MAX_MS)finishRecording();
  }
  if(clock.running||session||recordStart!==null||performance.now()<meterUntil)frame=requestAnimationFrame(runFrame);else{frame=0;$('signal').setAttribute('aria-valuenow','0');$('signal').style.setProperty('--level',0);}
}
function animate(){meterUntil=performance.now()+900;if(!frame)frame=requestAnimationFrame(runFrame);}
async function ready(preset=$('instrumentSelect').value,engine='sample-v1'){
  if(audio.context?.state==='running'&&audio.isReady(preset,engine))return true;
  const version=lifecycle,selection=presetEpoch;loading++;$('enableAudio').disabled=true;$('enableAudio').textContent='加载音色…';
  try{await audio.ready(preset,engine);if(version!==lifecycle||selection!==presetEpoch||document.hidden)return false;status.dataset.state=audio.context.state;status.classList.remove('error');status.textContent='声音已就绪。按键或点按，开始你的节奏。';return true;}
  catch{status.dataset.state='unavailable';status.classList.add('error');status.textContent='音色未能加载，请点“重试声音”。检查网络和设备静音后再试。';return false;}
  finally{loading--;if(!loading){$('enableAudio').disabled=false;$('enableAudio').textContent=audio.isReady($('instrumentSelect').value)?'声音已就绪':'重试声音';}}
}
function allows(key){const preset=$('instrumentSelect').value;return key.kind==='drum'||(key.kind==='chord'?preset==='guitar':preset!=='drums');}
function renderInstrument(){
  const preset=$('instrumentSelect').value,drums=preset==='drums';scene.dataset.instrument=preset;$('playingSurface').dataset.instrument=preset;
  $('guitarChords').hidden=preset!=='guitar';$('melodyKeys').hidden=drums;$('melodyHeading').hidden=drums;$('scoreBook').hidden=drums;$('drumGuide').hidden=!drums;
  $('drumHint').textContent=drums?'Z X C V · B N M L，自由编节奏':'Z X C V · B N M L';
  $('enableAudio').textContent=audio.isReady(preset)?'声音已就绪':'打开声音';status.textContent=audio.isReady(preset)?'音色已就绪，随手弹一段。':'点“打开声音”加载当前乐器。';
}
$('enableAudio').addEventListener('click',()=>ready());
$('instrumentSelect').addEventListener('change',()=>{presetEpoch++;lifecycle++;clearHeld();stopSession();audio.stopVoices();renderInstrument();});
async function hit(code){
  const key=byCode.get(code);if(!key||!allows(key)||loading)return;if(!audio.isReady($('instrumentSelect').value)){await ready();return;}if(session)stopSession();
  if(!await ready())return;try{audio.play(key,$('instrumentSelect').value);}catch{status.classList.add('error');status.textContent='这一声未能播放，请切换乐器或重新打开声音。';return;}visual(key);status.textContent=clock.running?'跟着节拍，继续你的旋律。':'打开节拍器，或者按自己的感觉弹。';
  if(recordStart!==null){
    const time=Math.round((audio.context.currentTime-recordStart)*1000);
    if(time<=MAX_MS&&recording.events.length<MAX_EVENTS){const recent=recording.events.filter(e=>e[0]>time-100).length;if(recent<32)recording.events.push([Math.max(0,time),CODES.indexOf(code)]);}
    if(recording.events.length>=MAX_EVENTS||time>=MAX_MS)finishRecording();
  }
  animate();
}
function clearHeld(){held.clear();for(const timer of pulses.values())clearTimeout(timer);pulses.clear();paint();}
const isControl=target=>target instanceof Element&&target.closest('input:not([type="range"]),textarea,select,[contenteditable]');
document.addEventListener('keydown',event=>{
  if(event.repeat||event.isComposing||event.ctrlKey||event.metaKey||event.altKey||isControl(event.target)||!byCode.has(event.code)||!allows(byCode.get(event.code)))return;
  event.preventDefault();if(held.has(event.code))return;held.add(event.code);paint();hit(event.code);
});
document.addEventListener('keyup',event=>{held.delete(event.code);paint();});
for(const [code,b]of buttons){
  b.addEventListener('pointerdown',event=>{if(event.button!==0)return;event.preventDefault();b.setPointerCapture(event.pointerId);held.add(code);hit(code);});
  const release=()=>{held.delete(code);paint();};for(const name of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(name,release);
  b.addEventListener('click',event=>{if(event.detail===0)hit(code);});
}
function paintClock(){
  const on=clock.running;$('metronomeToggle').setAttribute('aria-pressed',String(on));$('metronomeToggle').innerHTML=`<span class="play-icon" aria-hidden="true">${on?'■':'▶'}</span><span>${on?'停节拍':'开节拍'}</span>`;
  $('beatIndicator').dataset.running=String(on);$('beatIndicator').dataset.bpm=$('bpm').value;
  for(const item of $('beatIndicator').children){item.hidden=Number(item.dataset.beat)>=Number($('meterSelect').value);if(!on)item.classList.remove('active');}
  $('beatIndicator').setAttribute('aria-label',`${$('meterSelect').value} 拍节奏`);
}
function stopClock(){clock.stop();paintClock();scene.classList.remove('beat-pulse');}
$('metronomeToggle').addEventListener('click',async()=>{if(clock.running)stopClock();else if(await ready()){clock.start(Number($('bpm').value),Number($('meterSelect').value));paintClock();animate();}});
function changeTempo(){
  $('bpmValue').textContent=$('bpm').value;if(clock.running)clock.start(Number($('bpm').value),Number($('meterSelect').value));paintClock();
}
$('bpm').addEventListener('input',changeTempo);$('meterSelect').addEventListener('change',changeTempo);
let taps=[];
$('tapTempo').addEventListener('click',()=>{const now=performance.now();if(taps.length&&now-taps.at(-1)>2000)taps=[];taps.push(now);if(taps.length>5)taps.shift();if(taps.length>=2){$('bpm').value=String(Math.max(50,Math.min(180,Math.round(60000/((taps.at(-1)-taps[0])/(taps.length-1))))));changeTempo();}});
$('volume').addEventListener('input',event=>{audio.setVolume(Number(event.target.value)/100);$('volumeValue').textContent=event.target.value+'%';});
function stopSession(natural=false){
  if(session){clearInterval(session.timer);session=null;if(!natural)audio.stopVoices();}
  document.querySelector('.score-note.playing')?.classList.remove('playing');$('stopSong').disabled=true;$('listenSong').disabled=false;$('playRecording').textContent='▶ 回放';updateRecorder();
}
function scheduleSession(){
  if(!session)return;const now=audio.context.currentTime;
  while(session.cursor<session.events.length&&session.events[session.cursor].offset+session.start<now+.1){
    const event=session.events[session.cursor++],time=session.start+event.offset;
    if(time>=now-.05){try{audio.play(session.engine==='ui-synth-v1'?LEGACY_KEYS.find(k=>k.code===event.code):byCode.get(event.code),session.instrument,time,session.engine);}catch{stopSession();status.classList.add('error');status.textContent='回放遇到声音问题，已停止。可以重新打开声音再试。';return;}session.visuals.push({...event,time});}
  }
}
function playEvents(events,duration,kind,instrument,engine='sample-v1'){
  stopSession();stopClock();const start=audio.context.currentTime+.05;
  session={kind,events,cursor:0,start,end:start+duration,visuals:[],instrument,engine};scheduleSession();if(!session)return;session.timer=setInterval(scheduleSession,25);
  if(kind==='score'){$('stopSong').disabled=false;$('listenSong').disabled=true;}else $('playRecording').textContent='■ 停止回放';updateRecorder();animate();
}
for(const song of SONGS){const o=document.createElement('option');o.value=song.id;o.textContent=song.name;$('songSelect').append(o);}
function selectedSong(){return SONGS.find(s=>$('songSelect').value===s.id)||SONGS[0];}
function renderScore(){
  stopSession();const song=selectedSong();$('songInfo').textContent=`${song.key} · ${song.meter}/4 拍 · 建议 ${song.bpm} BPM。${song.description}`;$('scoreRows').replaceChildren();let index=0;
  for(const phrase of song.phrases){const row=document.createElement('div');row.className='score-phrase';for(const event of phrase){const k=byNote.get(event.note),n=document.createElement('div');n.className='score-note';n.dataset.scoreIndex=String(index++);n.innerHTML=`<span>${k.label}</span><kbd>${k.key}</kbd><small>${event.beats} 拍</small>`;row.append(n);}$('scoreRows').append(row);}
  $('scoreStatus').textContent='字母是键位，数字按 C 音起排列；上点表示高音。谱子只供参考，跟自己的节奏弹。';
}
$('songSelect').addEventListener('change',renderScore);
$('listenSong').addEventListener('click',async()=>{
  if(recordStart!==null||!await ready())return;const song=selectedSong(),events=scoreEvents(song,Number($('bpm').value)).map(e=>({...e,code:byNote.get(e.note).code}));
  const duration=events.at(-1).offset+events.at(-1).beats*60/Number($('bpm').value);
  $('scoreStatus').textContent=`示范以当前 ${$('bpm').value} BPM 播放。随时弹一下琴键就能接手。`;playEvents(events,duration,'score',$('instrumentSelect').value);
});
$('stopSong').addEventListener('click',()=>{stopSession();$('scoreStatus').textContent='示范已停止。';});
function updateRecorder(){
  const active=recordStart!==null||recordPending;const playing=session?.kind==='recording';
  $('recordToggle').textContent=active?'■ 结束记录':'● 开始记录';$('recordToggle').setAttribute('aria-pressed',String(active));$('recordToggle').disabled=recordPending||importPending||!!playing;
  $('instrumentSelect').disabled=active||importPending||!!session;$('songSelect').disabled=active;$('listenSong').disabled=active||session?.kind==='score';
  $('playRecording').disabled=active||importPending||!recording?.events.length;$('exportRecording').disabled=active||importPending||!recording?.events.length;$('importRecording').disabled=active||importPending||!!session;
}
function finishRecording(){
  if(recordStart===null)return;recording.duration=Math.min(MAX_MS,Math.max(0,Math.round((audio.context.currentTime-recordStart)*1000)));recordStart=null;
  $('recordingStatus').textContent=recording.events.length?'记下来了。可以回放，或导出文件留住这一段。':'还没有记下敲击，可以再试一次。';updateRecorder();
}
$('recordToggle').addEventListener('click',async()=>{
  if(recordStart!==null){finishRecording();return;}if(recordPending||importPending)return;recordPending=true;updateRecorder();
  if(!await ready()){recordPending=false;updateRecorder();return;}stopSession();$('exportPreview').hidden=true;recording=makeRecording($('instrumentSelect').value,Number($('bpm').value),Number($('meterSelect').value));recordStart=audio.context.currentTime;recordPending=false;
  $('recordingStatus').textContent='正在记下你的按键。节拍器不会录进文件；最多 5 分钟。';updateRecorder();animate();
});
$('playRecording').addEventListener('click',async()=>{
  if(session?.kind==='recording'){stopSession();$('recordingStatus').textContent='回放已停止。';return;}
  if(!recording?.events.length)return;if(recording.engine==='sample-v1'){$('instrumentSelect').value=recording.instrument;renderInstrument();}if(!await ready(recording.instrument,recording.engine))return;const events=recording.events.map(([time,code])=>({offset:time/1000,code:CODES[code]}));
  playEvents(events,recording.duration/1000,'recording',recording.instrument,recording.engine);$('recordingStatus').textContent='按原来的敲击时间回放。弹一下琴键即可接手。';
});
$('exportRecording').addEventListener('click',()=>{
  if(!recording?.events.length)return;const data=validateRecording(recording),text=JSON.stringify(data),blob=new Blob([text],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');$('exportData').value=text;$('exportPreview').hidden=false;
  a.href=url;a.download='miao-beat-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('recordingStatus').textContent=`已导出 ${blob.size} 字节，只包含按键与时间。`;
});
$('importRecording').addEventListener('change',async event=>{
  const file=event.target.files?.[0];if(!file||importPending||recordPending||recordStart!==null)return;importPending=true;updateRecorder();
  try{if(file.size>256000)throw Error('文件太大，请选择小于 256 KB 的演奏文件');const parsed=validateRecording(JSON.parse(await file.text()));stopSession();$('exportPreview').hidden=true;recording=parsed;$('recordingInfo').textContent=`${(recording.duration/1000).toFixed(1)} 秒 · ${recording.events.length} 次敲击`;$('recordingStatus').textContent='已读入本地文件，点回放即可听。';updateRecorder();}
  catch(error){$('recordingStatus').textContent='未导入：'+(error instanceof SyntaxError?'JSON 格式不正确':error.message);}
  importPending=false;event.target.value='';updateRecorder();
});
function pauseAll(){lifecycle++;recordPending=false;clearHeld();stopClock();stopSession();finishRecording();audio.stopVoices();}
window.addEventListener('blur',pauseAll);document.addEventListener('visibilitychange',()=>{if(document.hidden)pauseAll();});
renderInstrument();renderScore();paintClock();updateRecorder();
