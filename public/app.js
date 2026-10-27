import {KEYS,MELODY,DRUMS,CHORDS,LEGACY_KEYS} from './bindings.js';
import {SampledAudio} from './sampled-audio.js';
import {BeatClock,beatPattern} from './clock.js';
import {guidePosition} from './guidance.js';
import {mountCharacter} from './full-frame-character.js';
import {mountPerformance} from './performance.js';
import {mountKeyboardNavigation} from './keyboard-navigation.js';
import {loadSiteCounter} from './site-counter.js';
import {SONGS,scoreEvents} from './scores.js';
import {createMediaExport,mediaSupported} from './media-export.js';
import {CODES,MAX_MS,MAX_EVENTS,makeRecording,validateRecording} from './recording.js';
const $=id=>document.getElementById(id),audio=new SampledAudio(),byCode=new Map(KEYS.map(k=>[k.code,k])),byNote=new Map(MELODY.map(k=>[k.sub,k]));
const scene=$('scene'),status=$('soundStatus'),held=new Set(),pulses=new Map();
const touchInstructions=window.matchMedia?.('(max-width: 760px), (pointer: coarse)');
function playHint(){
  const mode=$('instrumentSelect').value,touch=touchInstructions?.matches;
  if(touch)return mode==='drums'?'点鼓垫试试。':mode==='guitar'?'点和弦，或点琴键。':'点琴键试试。';
  return mode==='drums'?'按 Z 敲底鼓，X 敲军鼓。':mode==='guitar'?'按 1—4 扫和弦，字母键弹单音。':'按 A S D F，或者点琴键。';
}
function showPlayHint(){const text=playHint();if(status.textContent!==text)status.textContent=text;}
touchInstructions?.addEventListener?.('change',()=>{
  if(!['idle','ready','running'].includes(status.dataset.state)||status.classList.contains('error'))return;
  const text=(audio.isReady($('instrumentSelect').value)?'':'先打开声音。')+playHint();if(status.textContent!==text)status.textContent=text;
});

let cueCodes=[],guideIndex=-2,guideBeat=-1,lyricIndex=-1;
const reducedMotion=window.matchMedia?.('(prefers-reduced-motion: reduce)');
audio.onProgress=()=>{if(!loading)return;const p=audio.getLoadProgress($('instrumentSelect').value);status.dataset.loaded=String(p.loaded);status.dataset.total=String(p.total);status.textContent=`声音加载中（${p.loaded} / ${p.total}）`;};
mountPerformance(document);
if(new URLSearchParams(location.search).get('instrument')==='guitar'){$('instrumentSelect').value='guitar';scene.dataset.instrument='guitar';}
const character=mountCharacter(scene);
const motionToggle=$('guitarMotionToggle');if(motionToggle){scene.addEventListener('guitar-motion-status',event=>{motionToggle.disabled=event.detail!=='ready';$('guitarMotionLabel').textContent=event.detail==='loading'?'动作准备中…':event.detail==='ready'?'拨弦动作':'动作暂未加载';});motionToggle.checked=!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;let pointerMotion=false;motionToggle.closest('label').addEventListener('pointerdown',()=>{pointerMotion=true;});motionToggle.addEventListener('keydown',()=>{pointerMotion=false;});motionToggle.addEventListener('change',()=>{character.setMotionEnabled(motionToggle.checked);if(pointerMotion){pointerMotion=false;$('playingSurface').focus({preventScroll:true});}});}character.ready.catch(()=>{scene.dataset.characterStatus='whole-image-unavailable';});
let loading=0,presetEpoch=0,mediaPending=false,mediaJob=null,mediaSerial=0;const mediaURLs={};
const mediaBusy=()=>mediaPending||!!mediaJob;
let hits=0,frame=0,meterUntil=0,beatUntil=0,session=null,recording=null,recordStart=null,recordPending=false,importPending=false,sessionPending=0,sessionSerial=0,lifecycle=0;
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
mountKeyboardNavigation();
loadSiteCounter();
function paint(){
  character.update?.($('instrumentSelect').value,[...held].map(code=>byCode.get(code)).filter(Boolean));
  for(const [code,b]of buttons)b.classList.toggle('active',held.has(code)||pulses.has(code));
  for(const side of ['left','right']){
    scene.classList.toggle(side+'-down',KEYS.some(k=>k.paw===side&&held.has(k.code)));
    scene.classList.toggle('hit-'+side,KEYS.some(k=>k.paw===side&&pulses.has(k.code)));
  }
}
function visual(key){
  character.strike?.(key,$('instrumentSelect').value);
  clearTimeout(pulses.get(key.code));pulses.set(key.code,setTimeout(()=>{pulses.delete(key.code);paint();},160));paint();
  $('nowPlaying').textContent=key.kind==='note'?`${key.sub} · ${key.label}`:key.label;scene.dataset.hits=String(++hits);
}
function runFrame(){
  const now=audio.context?.currentTime??0;
  if(session){
    while(session.visuals.length&&session.visuals[0].time<=now){const e=session.visuals.shift();visual(byCode.get(e.code));}
    if(session.guide)renderGuidance(now);
    if(session.exported){const value=Math.max(0,now-session.start)/session.duration;$('mediaProgress').value=Math.min(1,value);const second=Math.max(0,Math.floor(now-session.start));if($('mediaProgress').dataset.second!==String(second)){$('mediaProgress').dataset.second=String(second);$('mediaStatus').textContent=`正在生成${mediaJob?.kind==='video'?'视频':'音频'} · ${second} / ${Math.ceil(session.duration)} 秒，请留在此页。`;}}
    if(session.cursor===session.events.length&&now>session.end+.1){const kind=session.kind,exportJob=session.exported?mediaJob:null;stopSession(true);exportJob?.stop();const message=kind==='recording'?'回放结束。':kind==='guide'?'这一遍弹完了。再来一遍？':'听完了，换你试试。';(kind==='recording'?$('recordingStatus'):$('scoreStatus')).textContent=message;if(kind!=='recording')$('practiceHint').textContent=message;}
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
  const version=lifecycle,selection=presetEpoch;loading++;status.dataset.state='loading';status.textContent='第一次要加载声音，等好了再点一下。';$('enableAudio').disabled=true;$('enableAudio').textContent='加载中…';
  try{await audio.ready(preset,engine);if(version!==lifecycle||selection!==presetEpoch||document.hidden)return false;status.dataset.state=audio.context.state;status.classList.remove('error');showPlayHint();return true;}
  catch{if(version!==lifecycle||selection!==presetEpoch)return false;status.dataset.state='unavailable';status.classList.add('error');status.textContent='声音没加载出来，点“重试声音”再试。';return false;}
  finally{loading--;if(!loading){const prepared=audio.isReady($('instrumentSelect').value);$('enableAudio').disabled=false;$('enableAudio').textContent=prepared?'可以弹了':'重试声音';if(status.dataset.state==='loading'){status.dataset.state=prepared?'ready':'idle';status.textContent=prepared?playHint():'声音加载已暂停，点“打开声音”再试。';}}}
}
function allows(key){const preset=$('instrumentSelect').value;return key.kind==='drum'||(key.kind==='chord'?preset==='guitar':preset!=='drums');}
function renderInstrument(){
  const preset=$('instrumentSelect').value,drums=preset==='drums';$('nowPlaying').textContent='点个键试试';scene.dataset.instrument=preset;$('playingSurface').dataset.instrument=preset;
  $('guitarChords').hidden=preset!=='guitar';$('melodyKeys').hidden=drums;$('melodyHeading').hidden=drums;$('scoreBook').hidden=false;$('drumGuide').hidden=!drums;
  $('drumHint').textContent=drums?'Z X C V · B N M L':'Z X C V · B N M L';
  $('enableAudio').textContent=audio.isReady(preset)?'可以弹了':'打开声音';status.dataset.state=audio.isReady(preset)?'ready':'idle';status.textContent=audio.isReady(preset)?playHint():'先打开声音。'+playHint();
}
$('enableAudio').addEventListener('click',()=>ready());
let instrumentPickedByPointer=false;
$('instrumentSelect').addEventListener('pointerdown',()=>{instrumentPickedByPointer=true;});
$('instrumentSelect').addEventListener('keydown',()=>{instrumentPickedByPointer=false;});
$('instrumentSelect').addEventListener('change',()=>{presetEpoch++;lifecycle++;clearHeld();stopSession();audio.stopVoices();renderInstrument();populateSongs();renderScore();if(instrumentPickedByPointer){instrumentPickedByPointer=false;$('playingSurface').focus({preventScroll:true});}});
async function hit(code){
  const key=byCode.get(code);if(mediaBusy()||!key||!allows(key)||loading)return;if(!audio.isReady($('instrumentSelect').value)){if(await ready())status.textContent='加载好了，再按一下试试。';return;}if(session&&session.kind!=='guide')stopSession();
  if(!await ready())return;try{audio.play(key,$('instrumentSelect').value);}catch{status.classList.add('error');status.textContent='这一下没响，试试重新打开声音。';return;}visual(key);status.classList.remove('error');showPlayHint();
  if(recordStart!==null){
    const time=Math.round((audio.context.currentTime-recordStart)*1000);
    if(time<=MAX_MS&&recording.events.length<MAX_EVENTS){const recent=recording.events.filter(e=>e[0]>time-100).length;if(recent<32)recording.events.push([Math.max(0,time),CODES.indexOf(code)]);}
    if(recording.events.length>=MAX_EVENTS||time>=MAX_MS)finishRecording();
  }
  animate();
}
function clearHeld(){held.clear();for(const timer of pulses.values())clearTimeout(timer);pulses.clear();paint();}
const isControl=target=>$('supportDialog')?.open||target instanceof Element&&target.closest('input:not([type="range"]),textarea,select,[contenteditable]');
document.addEventListener('keydown',event=>{
  if(mediaBusy()||event.repeat||event.isComposing||event.ctrlKey||event.metaKey||event.altKey||isControl(event.target)||!byCode.has(event.code)||!allows(byCode.get(event.code)))return;
  event.preventDefault();if(held.has(event.code))return;held.add(event.code);paint();hit(event.code);
});
document.addEventListener('keyup',event=>{held.delete(event.code);paint();});
for(const [code,b]of buttons){
  b.addEventListener('pointerdown',event=>{if(mediaBusy()||event.button!==0)return;event.preventDefault();b.setPointerCapture(event.pointerId);held.add(code);paint();hit(code);});
  const release=()=>{held.delete(code);paint();};for(const name of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(name,release);
  b.addEventListener('click',event=>{if(event.detail===0)hit(code);});
}
function paintClock(){
  const on=clock.running;$('metronomeToggle').setAttribute('aria-pressed',String(on));$('metronomeToggle').innerHTML=`<span class="play-icon" aria-hidden="true">${on?'■':'▶'}</span><span>${on?'停节拍':'开节拍'}</span>`;
  $('beatIndicator').dataset.running=String(on);$('beatIndicator').dataset.bpm=$('bpm').value;
  for(const item of $('beatIndicator').children){item.hidden=Number(item.dataset.beat)>=Number($('meterSelect').value);if(!on)item.classList.remove('active');}
  for(const item of $('beatIndicator').children)item.classList.toggle('accent',Number(item.dataset.beat)===($('metronomeAccent').value==='last'?Number($('meterSelect').value)-1:0));
  $('metronomePattern').textContent=beatPattern(Number($('meterSelect').value),$('metronomeSound').value,$('metronomeAccent').value);
  $('beatIndicator').setAttribute('aria-label',`${$('meterSelect').value} 拍节奏`);
}
function stopClock(){clock.stop();paintClock();scene.classList.remove('beat-pulse');}
$('metronomeToggle').addEventListener('click',async()=>{if(clock.running)stopClock();else if(await ready()){clock.start(Number($('bpm').value),Number($('meterSelect').value),session?.guide?session.origin:undefined);paintClock();animate();}});
function changeTempo(){
  if(session?.guide){stopSession();$('scoreStatus').textContent='速度或拍号改了，点“跟着弹”重新开始。';$('practiceHint').textContent=$('scoreStatus').textContent;}
  $('bpmValue').textContent=$('bpm').value;if(clock.running)clock.start(Number($('bpm').value),Number($('meterSelect').value));paintClock();
}
$('bpm').addEventListener('input',changeTempo);$('meterSelect').addEventListener('change',changeTempo);
for(const id of ['metronomeSound','metronomeAccent'])$(id).addEventListener('change',()=>{clock.setSound($('metronomeSound').value,$('metronomeAccent').value);if(clock.running)clock.start(Number($('bpm').value),Number($('meterSelect').value),session?.guide?session.origin:undefined);paintClock();});
let taps=[];
$('tapTempo').addEventListener('click',()=>{const now=performance.now();if(taps.length&&now-taps.at(-1)>2000)taps=[];taps.push(now);if(taps.length>5)taps.shift();if(taps.length>=2){$('bpm').value=String(Math.max(50,Math.min(180,Math.round(60000/((taps.at(-1)-taps[0])/(taps.length-1))))));changeTempo();}});
$('volume').addEventListener('input',event=>{audio.setVolume(Number(event.target.value)/100);$('volumeValue').textContent=event.target.value+'%';});
async function prepareSession(preset,engine='sample-v1'){
  if(sessionPending||recordPending||importPending||recordStart!==null)return false;const id=++sessionSerial,version=lifecycle;sessionPending=id;updateRecorder();
  try{return await ready(preset,engine)&&version===lifecycle;}finally{if(sessionPending===id)sessionPending=0;updateRecorder();}
}
function clearGuidance(){
  for(const code of cueCodes){buttons.get(code)?.classList.remove('due','upcoming');}cueCodes=[];
  for(const n of document.querySelectorAll('.score-note.playing'))n.classList.remove('playing');
  lyricIndex=-1;$('lyricPanel').hidden=true;$('lyricCurrent').textContent='';$('lyricNext').textContent='';$('lyricPosition').textContent='';delete $('lyricPanel').dataset.line;
  for(const line of document.querySelectorAll('.score-lyric[aria-current]'))line.removeAttribute('aria-current');
  guideIndex=-2;guideBeat=-1;delete $('guidePanel').dataset.cue;$('guidePanel').hidden=true;$('guideTrack').replaceChildren();
  $('guideProgress').setAttribute('aria-valuenow','0');$('guideProgressFill').style.width='0%';$('guideAnnounce').textContent='';
}
function stopSession(natural=false){
  if(session){if(session.exported&&!natural)mediaJob?.cancel();const guided=!!session.guide;clearInterval(session.timer);session=null;if(!natural)audio.stopVoices();if(guided)stopClock();}
  clearGuidance();$('stopSong').disabled=true;$('listenSong').disabled=false;$('guideSong').setAttribute('aria-pressed','false');$('playRecording').textContent='▶ 回放';updateRecorder();
}
function scheduleSession(){
  if(!session)return;const now=audio.context.currentTime;
  while(session.cursor<session.events.length&&session.events[session.cursor].offset+session.start<now+.1){
    const event=session.events[session.cursor++],time=session.start+event.offset;
    if(session.exported&&time<now-.15){mediaJob?.cancel('页面卡顿，已取消导出；请留在此页重试。');stopSession();$('mediaStatus').textContent='页面卡顿，已取消导出；请留在此页重试。';return;}
    if(session.kind!=='guide'&&time>=now-.05){try{audio.play(session.engine==='ui-synth-v1'?LEGACY_KEYS.find(k=>k.code===event.code):byCode.get(event.code),session.instrument,time,session.engine);}catch{stopSession();status.classList.add('error');status.textContent='回放没响，已停止。重新打开声音再试。';return;}session.visuals.push({...event,time});}
  }
}
function playEvents(events,duration,kind,instrument,engine='sample-v1',guide=null){
  stopSession();stopClock();const origin=audio.context.currentTime+(guide ? .1 : .05),start=origin+(guide?guide.countInBeats*60/guide.bpm:0);
  session={kind,events,cursor:0,origin,start,end:start+duration,visuals:[],instrument,engine,guide,duration};scheduleSession();if(!session)return;session.timer=setInterval(scheduleSession,25);
  if(guide){mountGuidance(guide);if(kind==='guide'){clock.start(guide.bpm,guide.meter,origin);paintClock();}$('stopSong').disabled=false;$('listenSong').disabled=true;$('guideSong').setAttribute('aria-pressed',String(kind==='guide'));}
  else $('playRecording').textContent='■ 停止回放';updateRecorder();animate();
}
function restHint(event){return event.beats===1?'空一拍':`空 ${event.beats} 拍`;}
function scoreKeys(event){return event.rest?[]:event.codes?event.codes.map(code=>byCode.get(code)):event.code?[byCode.get(event.code)]:[byNote.get(event.note)];}
function populateSongs(){
  const previous=$('songSelect').value,preset=$('instrumentSelect').value;$('songSelect').replaceChildren();
  const groups=new Map();
  for(const song of SONGS){
    if(song.instruments?!song.instruments.includes(preset):(preset==='drums')!==(song.kind==='rhythm'))continue;
    const title=song.kind==='rhythm'?'节奏练习':song.difficulty||'轻松入门';let group=groups.get(title);if(!group){group=document.createElement('optgroup');group.label=title;groups.set(title,group);$('songSelect').append(group);}
    const o=document.createElement('option');o.value=song.id;o.textContent=song.name;group.append(o);
  }
  if([...$('songSelect').options].some(o=>o.value===previous))$('songSelect').value=previous;
}
function selectedSong(){return SONGS.find(s=>$('songSelect').value===s.id)||SONGS[0];}
function renderScore(){
  stopSession();const song=selectedSong();$('songInfo').textContent=`${song.key} · ${song.meter}/4 拍 · 建议 ${song.bpm} BPM。${song.description}`;$('scoreRows').replaceChildren();let index=0;
  $('scoreSourceRow').hidden=!song.sourceLabel;if(song.sourceLabel){$('scoreSource').href=song.sourceUrl;$('scoreSource').textContent=song.sourceLabel;}
  for(const [lineIndex,phrase]of song.phrases.entries()){const row=document.createElement('div');row.className='score-phrase';for(const event of phrase){const keys=scoreKeys(event),n=document.createElement('div');n.className='score-note';n.dataset.scoreIndex=String(index++);n.innerHTML=`<span>${event.rest?'0':keys.map(k=>k.label).join('+')}</span><kbd>${event.rest?'休止':keys.map(k=>k.key).join('+')}</kbd><small>${event.beats} 拍</small>`;row.append(n);}if(song.lyrics){const line=document.createElement('p'),block=document.createElement('section');line.className='score-lyric';line.dataset.lyricIndex=String(lineIndex);line.textContent=song.lyrics[lineIndex];block.className='score-line';block.append(line,row);$('scoreRows').append(block);}else $('scoreRows').append(row);}
  $('practiceHint').textContent=`${song.name} · ${song.key} · ${song.meter}/4 · 建议 ${song.bpm} BPM。点“听一遍”先听。`;
  $('scoreStatus').textContent='字母是键位；数字按 C 音起排列，上点表示高音。按键时间由竖线提示，长条表示到下一音的间隔。';
}
function mountGuidance(guide){
  $('guidePanel').hidden=false;guideIndex=-2;guideBeat=-1;
  for(const event of guide.events){const n=document.createElement('div');n.className='guide-note';n.style.left=event.offset*guide.bpm/60*72+'px';n.style.width=Math.max(20,event.beats*72-5)+'px';n.innerHTML=`<kbd>${event.rest?'休止':event.keys.map(k=>k.key).join('+')}</kbd><small>${event.rest?restHint(event):event.keys.map(k=>k.label).join('+')}</small>`;$('guideTrack').append(n);}
  const totalBeats=Math.ceil(session.duration*guide.bpm/60);
  for(let beat=0;beat<=totalBeats;beat++){const line=document.createElement('i');line.className='guide-tick'+((beat+guide.phaseBeats)%guide.meter===0?' bar-tick':'');line.style.left=beat*72+'px';$('guideTrack').append(line);}
  if(guide.lyrics)renderLyrics(guide,0,true);
  $('guideAnnounce').textContent=`${guide.songName}，预备 ${guide.countInBeats} 拍。${session.kind==='guide'?'只放节拍，旋律你来弹。':'即将播放示范。'}`;
}
function renderLyrics(guide,index,countIn=false){
  if(!guide.lyrics||index===lyricIndex)return;
  lyricIndex=index;$('lyricPanel').hidden=false;$('lyricPanel').dataset.line=String(index);
  $('lyricPosition').textContent=`歌词 · ${index+1} / ${guide.lyrics.length}${countIn?' · 预备':''}`;
  $('lyricCurrent').textContent=guide.lyrics[index];$('lyricNext').textContent=guide.lyrics[index+1]||'';
  for(const line of document.querySelectorAll('.score-lyric[aria-current]'))line.removeAttribute('aria-current');
  document.querySelector(`[data-lyric-index="${index}"]`)?.setAttribute('aria-current','true');
}
function renderGuidance(now){
  const {guide}=session,elapsed=now-session.start,p=guidePosition(guide.events,elapsed,session.duration,guide.bpm,guide.meter,guide.phaseBeats);
  $('guideProgress').setAttribute('aria-valuenow',String(Math.round(p.progress*100)));$('guideProgressFill').style.width=p.progress*100+'%';
  const displayTime=reducedMotion?.matches?(p.index>=0?guide.events[p.index].offset:0):elapsed;
  $('guideTrack').style.transform=`translateX(${-displayTime*guide.bpm/60*72}px)`;
  $('guideTime').textContent=p.countIn?`预备 ${Math.min(guide.countInBeats,p.countIn)} 拍`:`${Math.min(session.duration,Math.max(0,elapsed)).toFixed(1)} / ${session.duration.toFixed(1)} 秒`;
  if(p.index!==guideIndex||p.beat!==guideBeat){
    guideIndex=p.index;guideBeat=p.beat;
    const current=p.index>=0?guide.events[p.index]:null,next=p.next>=0?guide.events[p.next]:null;
    if(current&&guide.lyrics){if($('lyricPosition').textContent.endsWith(' · 预备'))lyricIndex=-1;renderLyrics(guide,current.lyricIndex);}
    $('guideNow').textContent=current?.rest?`休止 · ${restHint(current)}`:current?`现在 ${current.keys.map(k=>k.key).join(' + ')} · ${current.keys.map(k=>k.kind==='note'?k.sub:k.label).join('+')}`:'听预备拍';
    $('guideNext').textContent=next?.rest?`接着${restHint(next)}`:next?`下一音 ${next.keys.map(k=>k.key).join(' + ')}`:current?.rest?'弹完啦': '最后一音';
    for(const n of document.querySelectorAll('.score-note.playing'))n.classList.remove('playing');
    if(current)document.querySelector(`[data-score-index="${current.index}"]`)?.classList.add('playing');
    $('guidePanel').dataset.index=String(p.index);$('guidePanel').dataset.bar=String(p.bar);$('guidePanel').dataset.beat=String(p.beat);
  }
  const cue=p.index>=0?guide.events[p.index]:guide.events[0],upcoming=elapsed<0;
  const codes=cue.keys.map(k=>k.code),signature=codes.join('|')+upcoming;
  if($('guidePanel').dataset.cue!==signature){
    for(const code of cueCodes)buttons.get(code)?.classList.remove('due','upcoming');cueCodes=codes;
    for(const code of codes)buttons.get(code)?.classList.add(upcoming?'upcoming':'due');$('guidePanel').dataset.cue=signature;
  }
}
$('songSelect').addEventListener('change',renderScore);
async function startScore(kind){
  if(!await prepareSession($('instrumentSelect').value))return;
  const song=selectedSong(),bpm=Number($('bpm').value);$('meterSelect').value=String(song.meter);paintClock();
  const guideEvents=scoreEvents(song,bpm).map(e=>({...e,keys:scoreKeys(e)}));
  const events=guideEvents.flatMap(e=>e.keys.map(k=>({...e,code:k.code}))),last=guideEvents.at(-1),duration=last.offset+last.beats*60/bpm;
  $('scoreStatus').textContent=kind==='guide'?`跟弹 ${bpm} BPM。只放节拍，旋律你来弹。`:`示范 ${bpm} BPM。点琴键就能接着弹。`;
  $('practiceHint').textContent=$('scoreStatus').textContent;
  playEvents(events,duration,kind,$('instrumentSelect').value,'sample-v1',{events:guideEvents,bpm,meter:song.meter,phaseBeats:song.pickupBeats?song.meter-song.pickupBeats:0,countInBeats:song.pickupBeats?song.meter-song.pickupBeats:song.meter,songName:song.name,lyrics:song.lyrics});
  if(kind==='guide'||song.lyrics)requestAnimationFrame(()=>$('guidePanel').scrollIntoView?.({block:'nearest',behavior:reducedMotion?.matches?'auto':'smooth'}));
}
$('listenSong').addEventListener('click',()=>startScore('score'));
$('guideSong').addEventListener('click',()=>startScore('guide'));
$('stopSong').addEventListener('click',()=>{lifecycle++;sessionPending=0;stopSession();$('scoreStatus').textContent='已停止。';$('practiceHint').textContent=$('scoreStatus').textContent;});
function updateRecorder(){
  const busy=mediaBusy(),active=recordStart!==null||recordPending;const playing=session?.kind==='recording';
  $('recordToggle').textContent=active?'■ 停止记录':'● 开始记录';$('recordToggle').setAttribute('aria-pressed',String(active));$('recordToggle').disabled=recordPending||importPending||!!sessionPending||!!playing;
  $('instrumentSelect').disabled=active||importPending||!!sessionPending||!!session;$('songSelect').disabled=active||!!sessionPending;$('listenSong').disabled=active||!!sessionPending||session?.kind==='score';$('guideSong').disabled=active||!!sessionPending||!!session?.guide;$('metronomeToggle').disabled=!!sessionPending;
  $('stopSong').disabled=!sessionPending&&!session?.guide;
  $('playRecording').disabled=active||importPending||!!sessionPending||!recording?.events.length;$('exportRecording').disabled=active||importPending||!!sessionPending||!recording?.events.length;$('importRecording').disabled=active||importPending||!!sessionPending||!!session;
  for(const id of ['recordToggle','instrumentSelect','songSelect','listenSong','guideSong','metronomeToggle','playRecording','exportRecording','importRecording','bpm','meterSelect','metronomeSound','metronomeAccent','volume'])if(busy)$(id).disabled=true;else if(['bpm','meterSelect','metronomeSound','metronomeAccent','volume'].includes(id))$(id).disabled=false;
  for(const button of buttons.values())button.disabled=busy;
  const hasMediaSource=$('exportSource').value==='score'||!!recording?.events.length;$('exportSource').disabled=busy||active||!!session||!!sessionPending;
  $('exportVideo').disabled=busy||active||!!session||!!sessionPending||!hasMediaSource||!mediaSupported('video');
  $('exportAudio').disabled=busy||active||!!session||!!sessionPending||!hasMediaSource||!mediaSupported('audio');
  $('cancelMediaExport').hidden=!busy;
  if(!busy&&!mediaSupported('video')&&!mediaSupported('audio')){$('mediaResults').hidden=false;$('mediaStatus').textContent='当前浏览器不支持媒体导出，仍可保存按键片段。';}
}
function finishRecording(){
  if(recordStart===null)return;recording.duration=Math.min(MAX_MS,Math.max(0,Math.round((audio.context.currentTime-recordStart)*1000)));recordStart=null;
  $('recordingStatus').textContent=recording.events.length?'记下了，点“回放”听听。':'没记到按键，再试一次。';updateRecorder();
}
$('recordToggle').addEventListener('click',async()=>{
  if(recordStart!==null){finishRecording();return;}if(recordPending||importPending||sessionPending)return;recordPending=true;updateRecorder();
  if(!await ready()){recordPending=false;updateRecorder();return;}if(session?.kind!=='guide')stopSession();$('exportPreview').hidden=true;recording=makeRecording($('instrumentSelect').value,Number($('bpm').value),Number($('meterSelect').value));recordStart=audio.context.currentTime;recordPending=false;
  $('recordingStatus').textContent='记录中，最长 5 分钟。只记按键，不记节拍声。';updateRecorder();animate();
});
$('playRecording').addEventListener('click',async()=>{
  if(session?.kind==='recording'){stopSession();$('recordingStatus').textContent='回放已停止。';return;}
  if(!recording?.events.length)return;if(recording.engine==='sample-v1'){$('instrumentSelect').value=recording.instrument;renderInstrument();populateSongs();renderScore();}if(!await prepareSession(recording.instrument,recording.engine))return;const events=recording.events.map(([time,code])=>({offset:time/1000,code:CODES[code]}));
  playEvents(events,recording.duration/1000,'recording',recording.instrument,recording.engine);$('recordingStatus').textContent='正在回放。点琴键就能接着弹。';
});
$('exportRecording').addEventListener('click',()=>{
  if(!recording?.events.length)return;const data=validateRecording(recording),text=JSON.stringify(data),blob=new Blob([text],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');$('exportData').value=text;$('exportPreview').hidden=false;
  a.href=url;a.download='miao-beat-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('recordingStatus').textContent=`演奏文件已生成（${blob.size} 字节），可再导入回放。`;
});
$('importRecording').addEventListener('change',async event=>{
  const file=event.target.files?.[0];if(!file||importPending||recordPending||recordStart!==null)return;importPending=true;updateRecorder();
  try{if(file.size>256000)throw Error('文件太大，请选择小于 256 KB 的演奏文件');const parsed=validateRecording(JSON.parse(await file.text()));stopSession();$('exportPreview').hidden=true;recording=parsed;$('recordingInfo').textContent=`${(recording.duration/1000).toFixed(1)} 秒 · ${recording.events.length} 次敲击`;$('recordingStatus').textContent='打开了，点“回放”就能听。';updateRecorder();}
  catch(error){$('recordingStatus').textContent='未导入：'+(error instanceof SyntaxError?'JSON 格式不正确':error.message);}
  importPending=false;event.target.value='';updateRecorder();
});
async function exportMedia(kind){
  if(mediaBusy()||session||recordStart!==null||$('exportSource').value==='recording'&&!recording?.events.length)return;
  const serial=++mediaSerial;mediaPending=true;updateRecorder();
  $('mediaResults').hidden=false;$('mediaProgress').hidden=false;$('mediaProgress').value=0;delete $('mediaProgress').dataset.second;
  $('mediaStatus').textContent='准备导出：会按原速回放一遍，请留在此页。';
  let job;
  try{
    let data,exportGuide=null;
    if($('exportSource').value==='score'){
      const song=selectedSong(),bpm=Number($('bpm').value),guideEvents=scoreEvents(song,bpm).map(e=>({...e,keys:scoreKeys(e)}));
      const last=guideEvents.at(-1),duration=last.offset+last.beats*60/bpm,countInBeats=song.pickupBeats?song.meter-song.pickupBeats:song.meter;
      if(duration+countInBeats*60/bpm+1.3>MAX_MS/1000)throw Error('这首曲子超过5分钟，请调快速度后再导出。');
      data=validateRecording({...makeRecording($('instrumentSelect').value,bpm,song.meter),duration:Math.round(duration*1000),events:guideEvents.flatMap(e=>e.keys.map(k=>[Math.round(e.offset*1000),CODES.indexOf(k.code)]))});
      exportGuide={events:guideEvents,bpm,meter:song.meter,phaseBeats:song.pickupBeats?song.meter-song.pickupBeats:0,countInBeats,songName:song.name,lyrics:song.lyrics};
    }else data=validateRecording(recording);
    $('mediaVideo').pause();$('mediaAudio').pause();
    $('instrumentSelect').value=data.engine==='ui-synth-v1'?'piano':data.instrument;renderInstrument();populateSongs();renderScore();
    if(!await ready(data.instrument,data.engine))throw Error('声音还没准备好，请重试。');
    stopSession();stopClock();clearHeld();audio.stopVoices();
    if(kind==='video'){await character.ready;await character.prepareCapture?.();}
    if(serial!==mediaSerial||document.hidden)throw Error('导出已取消。');
    job=await createMediaExport({audio,source:scene.querySelector('.full-frame-cat-canvas'),kind,doc:document,label:data.engine==='ui-synth-v1'?(data.instrument==='sparkle'?'旧版晶亮音色':'旧版马林巴'):($('instrumentSelect').selectedOptions[0]?.textContent||'Miao Beat'),caption:()=>exportGuide?.lyrics?$('lyricCurrent').textContent:$('nowPlaying').textContent});
    if(serial!==mediaSerial||document.hidden){job.cancel();await job.done;return;}
    mediaJob=job;mediaPending=false;if(kind==='video')character.setCaptureMode?.(true);updateRecorder();
    const events=data.events.map(([time,code])=>({offset:time/1000,code:CODES[code]}));
    // Preserve the actual recording duration and allow the final one-shot to decay.
    playEvents(events,data.duration/1000+1.3,exportGuide?'score':'recording',data.instrument,data.engine,exportGuide);session.exported=true;
    const result=await job.done;
    const url=URL.createObjectURL(result.blob);if(mediaURLs[kind])URL.revokeObjectURL(mediaURLs[kind]);mediaURLs[kind]=url;
    const a=$(kind==='video'?'downloadVideo':'downloadAudio'),preview=$(kind==='video'?'mediaVideo':'mediaAudio');
    a.href=url;a.download=`miao-beat-${data.instrument}-${Date.now()}.${result.extension}`;a.textContent=`保存${kind==='video'?'视频':'音频'} .${result.extension} · ${(result.blob.size/1024).toFixed(0)} KB`;a.hidden=false;preview.src=url;preview.hidden=false;
    $('mediaStatus').textContent=`${kind==='video'?'视频':'音频'}已生成，可预览或保存。`;$('mediaResults').dataset.format=result.mimeType;
  }catch(error){job?.cancel();if(serial===mediaSerial||job&&mediaJob===job){stopSession();audio.stopVoices();$('mediaStatus').textContent=error.message||'导出失败，按键片段还在，可以重试。';}}
  finally{if(serial===mediaSerial||job&&mediaJob===job){character.setCaptureMode?.(false);mediaPending=false;mediaJob=null;$('mediaProgress').hidden=true;updateRecorder();}}
}
$('exportSource').addEventListener('change',updateRecorder);
$('exportVideo').addEventListener('click',()=>exportMedia('video'));
$('exportAudio').addEventListener('click',()=>exportMedia('audio'));
$('cancelMediaExport').addEventListener('click',()=>{mediaSerial++;mediaPending=false;mediaJob?.cancel();stopSession();$('mediaStatus').textContent='导出已取消，按键片段还在。';$('mediaProgress').hidden=true;updateRecorder();});
function pauseAll(){if(mediaBusy()){mediaSerial++;mediaPending=false;mediaJob?.cancel('导出已取消：页面已离开前台。请留在此页重新导出。');$('mediaStatus').textContent='导出已取消：页面已离开前台。请留在此页重新导出。';$('mediaProgress').hidden=true;}const guided=!!session?.guide||!!sessionPending;lifecycle++;recordPending=false;sessionPending=0;clearHeld();stopClock();stopSession();finishRecording();audio.stopVoices();if(guided){$('practiceHint').textContent='已暂停。点“跟着弹”重新开始。';$('scoreStatus').textContent=$('practiceHint').textContent;}}
window.addEventListener('blur',pauseAll);document.addEventListener('visibilitychange',()=>{if(document.hidden)pauseAll();});
renderInstrument();populateSongs();renderScore();paintClock();updateRecorder();

// Reuse the owner's existing voluntary support image; no payment API or account.
const supportDialog=$('supportDialog');
for(const button of document.querySelectorAll('[data-open-support]'))button.addEventListener('click',()=>{if(!supportDialog.open){clearHeld();supportDialog.showModal();}});
$('closeSupport').addEventListener('click',()=>supportDialog.close());
supportDialog.addEventListener('click',event=>{if(event.target!==supportDialog)return;const r=supportDialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)supportDialog.close();});
