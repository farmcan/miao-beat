// DOM/event regression coverage. Audio is deliberately a controllable fake:
// these checks do not establish sound quality, device latency, or mobile support.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import * as bindings from '../public/bindings.js';
import * as scores from '../public/scores.js';
import * as recording from '../public/recording.js';
import {guidePosition} from '../public/guidance.js';

let domModule;
try { domModule=await import('jsdom'); }
catch(error) {
  if(!process.env.MIAO_BEAT_JSDOM_PATH)throw new Error('Install the jsdom dev dependency, or set MIAO_BEAT_JSDOM_PATH to its existing lib/api.js for a local check.',{cause:error});
  domModule=await import(pathToFileURL(process.env.MIAO_BEAT_JSDOM_PATH).href);
}
const {JSDOM}=domModule;
const html=await readFile(new URL('../public/index.html',import.meta.url),'utf8');
const app=(await readFile(new URL('../public/app.js',import.meta.url),'utf8')).replace(/^import .*;\n/gm,'');
const settle=async()=>{for(let i=0;i<8;i++)await Promise.resolve();};

function setup(t) {
  let audio,clock,exportedBlob;
  class FakeAudio {
    constructor(){audio=this;this.context={currentTime:0,state:'running'};this.plays=[];this.stops=0;this.peak=0;}
    isReady(){return !this.pending;}
    async ready(){if(this.pending)await this.pending;return this.context;}
    defer(){let resolve;this.pending=new Promise(r=>{resolve=r;});return()=>{this.pending=null;resolve();};}
    play(key,instrument,time=this.context.currentTime,engine='sample-v1'){this.plays.push({code:key.code,voice:key.voice,instrument,time,engine});}
    stopVoices(){this.stops++;}
    level(){return 0;}
    setVolume(value){this.volume=value;}
  }
  class FakeClock {
    constructor(){clock=this;this.running=false;}
    start(bpm,meter,origin){Object.assign(this,{running:true,bpm,meter,origin});}
    stop(){this.running=false;}
    render(){}
  }
  const dom=new JSDOM(html,{runScripts:'outside-only',pretendToBeVisual:true,url:'https://miao-beat.pages.dev/'});
  const w=dom.window,frames=new Map(),intervals=new Map();let next=1;
  w.requestAnimationFrame=fn=>{const id=next++;frames.set(id,fn);return id;};
  w.setInterval=fn=>{const id=next++;intervals.set(id,fn);return id;};
  w.clearInterval=id=>intervals.delete(id);
  w.Blob=Blob;
  w.URL.createObjectURL=blob=>{exportedBlob=blob;return 'blob:local-test';};
  w.URL.revokeObjectURL=()=>{};
  w.HTMLAnchorElement.prototype.click=function(){};
  w.__deps={...bindings,...scores,...recording,guidePosition,SampledAudio:FakeAudio,mountPerformance(){},mountKeyboardNavigation(){},loadSiteCounter(){},mountCharacter:()=>({ready:Promise.resolve(),strike(){}}),BeatClock:FakeClock};
  w.eval('const {KEYS,MELODY,DRUMS,CHORDS,LEGACY_KEYS,SampledAudio,mountCharacter,mountPerformance,mountKeyboardNavigation,loadSiteCounter,BeatClock,SONGS,scoreEvents,guidePosition,CODES,MAX_MS,MAX_EVENTS,makeRecording,validateRecording}=window.__deps;\n'+app);
  const $=id=>w.document.getElementById(id);
  const key=(type,code,target=w.document,options={})=>target.dispatchEvent(new w.KeyboardEvent(type,{code,bubbles:true,cancelable:true,...options}));
  const frame=time=>{audio.context.currentTime=time;const queued=[...frames.values()];frames.clear();for(const fn of queued)fn();};
  const importFile=async value=>{
    const text=JSON.stringify(value);
    Object.defineProperty($('importRecording'),'files',{value:[{size:Buffer.byteLength(text),text:async()=>text}],configurable:true});
    $('importRecording').dispatchEvent(new w.Event('change'));await settle();
  };
  t.after(()=>{w.dispatchEvent(new w.Event('blur'));dom.window.close();});
  return {w,$,audio,clock,key,frame,tick:()=>{for(const fn of intervals.values())fn();},importFile,blob:()=>exportedBlob};
}

test('simultaneous keyboard notes survive record/export/import/replay; a live key takes over',async t=>{
  const h=setup(t),{$,audio,key}=h;
  $('recordToggle').click();await settle();
  for(const code of ['KeyA','KeyD','KeyG'])key('keydown',code,$('recordToggle'));
  await settle();assert.equal(audio.plays.length,3);
  key('keydown','KeyA',$('recordToggle'),{repeat:true});await settle();assert.equal(audio.plays.length,3);
  for(const code of ['KeyA','KeyD','KeyG'])key('keyup',code);
  audio.context.currentTime=.5;$('recordToggle').click();await settle();
  $('exportRecording').click();const exported=JSON.parse(await h.blob().text());
  assert.equal(exported.duration,500);assert.deepEqual(exported.events,[[0,0],[0,2],[0,4]]);
  await h.importFile(exported);assert.equal($('playRecording').disabled,false);
  $('playRecording').click();await settle();assert.equal(audio.plays.length,6);
  assert.deepEqual(audio.plays.slice(3).map(e=>e.code),['KeyA','KeyD','KeyG']);
  assert.ok(audio.plays.slice(3).every(e=>Math.abs(e.time-.55)<1e-9));
  key('keydown','KeyS');await settle();assert.equal(audio.plays.length,7);
  assert.equal($('playRecording').textContent,'▶ 回放');assert.ok(audio.stops>0);
});

test('natural replay completion preserves the final one-shot tail; explicit stop cuts it',async t=>{
  const h=setup(t),{$,audio,key}=h;
  $('recordToggle').click();await settle();key('keydown','KeyA');await settle();key('keyup','KeyA');
  audio.context.currentTime=.01;$('recordToggle').click();await settle();
  $('playRecording').click();await settle();const stops=audio.stops;
  h.frame(.171);assert.equal($('recordingStatus').textContent,'回放结束。');
  assert.equal(audio.stops,stops,'natural completion must leave the 650 ms note tail alone');
  $('playRecording').click();await settle();const beforeStop=audio.stops;
  $('playRecording').click();await settle();assert.equal(audio.stops,beforeStop+1);
});

test('blur cancels pending audio activation for recording, metronome, and live notes',async t=>{
  const h=setup(t),{$,audio,key,w}=h;
  for(const action of [()=>$('recordToggle').click(),()=>$('metronomeToggle').click(),()=>key('keydown','KeyA')]){
    const release=audio.defer();action();w.dispatchEvent(new w.Event('blur'));release();await settle();
    assert.equal($('recordToggle').getAttribute('aria-pressed'),'false');
    assert.equal($('recordToggle').disabled,false);
    assert.equal($('metronomeToggle').getAttribute('aria-pressed'),'false');
    assert.equal(audio.plays.length,0);
    assert.equal(w.document.querySelectorAll('[data-code].active').length,0);
  }
  // It must also remain usable after the cancelled request.
  $('recordToggle').click();await settle();assert.equal($('recordToggle').getAttribute('aria-pressed'),'true');
});

test('a cold first note explains loading without replaying stale taps; a fresh input plays once',async t=>{
  const h=setup(t),{$,audio,key}=h;
  const release=audio.defer();key('keydown','KeyA');await settle();key('keyup','KeyA');
  assert.equal($('soundStatus').dataset.state,'loading');assert.match($('soundStatus').textContent,/加载.*再点/);
  assert.equal($('enableAudio').disabled,true);
  key('keydown','KeyD');key('keyup','KeyD');release();await settle();
  assert.equal(audio.plays.length,0,'initial and loading-time taps must never be queued');
  assert.match($('soundStatus').textContent,/再按一下/);assert.equal($('enableAudio').disabled,false);
  key('keydown','KeyS');await settle();key('keyup','KeyS');
  assert.deepEqual(audio.plays.map(p=>p.code),['KeyS']);
});

test('blur during first-note loading clears the loading state and never starts a late note',async t=>{
  const h=setup(t),{$,audio,key,w}=h;
  const release=audio.defer();key('keydown','KeyA');await settle();w.dispatchEvent(new w.Event('blur'));
  release();await settle();assert.equal(audio.plays.length,0);
  assert.notEqual($('soundStatus').dataset.state,'loading');assert.equal($('enableAudio').disabled,false);
  assert.equal(w.document.querySelectorAll('[data-code].active').length,0);
});

test('pending replay cannot restart after blur; regular BPM changes and blur remain usable',async t=>{
  const h=setup(t),{$,audio,clock,w,key}=h;
  const value=recording.makeRecording('marimba',96,4);Object.assign(value,{duration:100,events:[[0,0]]});
  await h.importFile(value);const release=audio.defer();$('playRecording').click();w.dispatchEvent(new w.Event('blur'));release();await settle();
  assert.equal(audio.plays.length,0);assert.equal($('playRecording').textContent,'▶ 回放');
  $('metronomeToggle').click();await settle();assert.equal(clock.running,true);
  $('bpm').value='150';$('bpm').dispatchEvent(new w.Event('input'));assert.equal(clock.bpm,150);
  key('keydown','KeyA');key('keydown','KeyS');await settle();assert.equal(w.document.querySelectorAll('[data-code].active').length,2);
  w.dispatchEvent(new w.Event('blur'));assert.equal(clock.running,false);
  assert.equal(w.document.querySelectorAll('[data-code].active').length,0);
  $('metronomeToggle').click();await settle();assert.equal(clock.running,true);
  $('metronomeToggle').click();assert.equal(clock.running,false);
});

test('recording stops at the five-minute bound and invalid imports preserve the previous clip',async t=>{
  const h=setup(t),{$,key}=h;
  $('recordToggle').click();await settle();key('keydown','KeyA');await settle();key('keyup','KeyA');
  h.frame(301);assert.equal($('recordToggle').getAttribute('aria-pressed'),'false');
  $('exportRecording').click();const saved=JSON.parse(await h.blob().text());assert.equal(saved.duration,300000);
  await h.importFile({...saved,events:Array.from({length:33},()=>[0,0])});
  assert.match($('recordingStatus').textContent,/未导入/);assert.equal($('playRecording').disabled,false);
  $('exportRecording').click();assert.deepEqual(JSON.parse(await h.blob().text()),saved);
});


test('guitar chords record as compact v2 events, and drums mode excludes melodic keys',async t=>{
 const h=setup(t),{$,key,audio,w}=h;
 $('instrumentSelect').value='guitar';$('instrumentSelect').dispatchEvent(new w.Event('change'));
 assert.equal($('guitarChords').hidden,false);$('recordToggle').click();await settle();
 key('keydown','Digit1');await settle();key('keyup','Digit1');audio.context.currentTime=.2;
 key('keydown','KeyA');await settle();key('keyup','KeyA');audio.context.currentTime=.4;
 $('recordToggle').click();$('exportRecording').click();const clip=JSON.parse(await h.blob().text());
 assert.equal(clip.version,2);assert.equal(clip.instrument,'guitar');assert.deepEqual(clip.events,[[0,21],[200,0]]);
 $('instrumentSelect').value='drums';$('instrumentSelect').dispatchEvent(new w.Event('change'));
 assert.equal($('melodyKeys').hidden,true);assert.equal($('scoreBook').hidden,false);
 const before=audio.plays.length;key('keydown','KeyA');key('keydown','Digit2');await settle();assert.equal(audio.plays.length,before);
 for(const code of ['KeyZ','KeyX','KeyC','KeyV','KeyB','KeyN','KeyM','KeyL'])key('keydown',code);
 await settle();assert.equal(audio.plays.length,before+8);
 await h.importFile(clip);$('playRecording').click();await settle();
 assert.equal($('instrumentSelect').value,'guitar');assert.equal($('guitarChords').hidden,false);
 assert.equal(audio.plays.at(-1).code,'Digit1');
});

test('old v1 imports retain their engine and shaker/bongo voices on replay',async t=>{
 const h=setup(t),{$,audio}=h;
 await h.importFile({format:'miao-beat',version:1,engine:'ui-synth-v1',instrument:'sparkle',bpm:96,meter:4,duration:10,events:[[0,15],[0,16]]});
 $('playRecording').click();await settle();
 assert.deepEqual(audio.plays.map(p=>[p.code,p.voice,p.engine]),[['KeyC','shaker','ui-synth-v1'],['KeyV','bongoHigh','ui-synth-v1']]);
});


test('a pending file import cannot overwrite an active newly recorded clip',async t=>{
 const h=setup(t),{$,w,key,audio}=h;let release;
 const read=new Promise(resolve=>{release=resolve;});
 const old={format:'miao-beat',version:2,engine:'sample-v1',instrument:'piano',bpm:96,meter:4,duration:900,events:[[900,0]]};
 Object.defineProperty($('importRecording'),'files',{value:[{size:100,text:()=>read}],configurable:true});
 $('importRecording').dispatchEvent(new w.Event('change'));await settle();
 assert.equal($('recordToggle').disabled,true);$('recordToggle').click();await settle();
 assert.equal($('recordToggle').getAttribute('aria-pressed'),'false');
 release(JSON.stringify(old));await settle();assert.equal($('recordToggle').disabled,false);
 $('recordToggle').click();await settle();audio.context.currentTime=.5;key('keydown','KeyS');await settle();key('keyup','KeyS');
 audio.context.currentTime=.7;$('recordToggle').click();$('exportRecording').click();
 const saved=JSON.parse(await h.blob().text());assert.deepEqual(saved.events,[[500,1]]);assert.equal(saved.duration,700);
});


test('pending sample load for playback locks recording until playback readiness resolves',async t=>{
 const h=setup(t),{$,audio}=h;
 const clip={...recording.makeRecording('guitar',96,4),duration:100,events:[[0,21]]};await h.importFile(clip);
 const release=audio.defer();$('playRecording').click();await settle();
 assert.equal($('recordToggle').disabled,true);assert.equal($('importRecording').disabled,true);
 $('recordToggle').click();await settle();assert.equal($('recordToggle').getAttribute('aria-pressed'),'false');
 release();await settle();assert.equal(audio.plays.length,1);assert.equal(audio.plays[0].instrument,'guitar');
});

test('guided practice advances from audio time, live hits continue it, and recording contains only real input',async t=>{
 const h=setup(t),{$,audio,key,clock,w}=h;
 $('guideSong').click();await settle();
 assert.equal(clock.running,true);assert.equal(audio.plays.length,0,'guide must never play the melody');
 h.frame(.5);assert.match($('guideTime').textContent,/预备/);assert.equal($('guidePanel').dataset.index,'-1');
 h.frame(2.6);assert.equal($('guidePanel').dataset.index,'0');assert.ok(w.document.querySelector('[data-code="KeyA"]').classList.contains('due'));
 $('recordToggle').click();await settle();assert.equal($('guidePanel').hidden,false);
 for(const [time,code]of [[2.65,'KeyA'],[2.8,'KeyS'],[2.95,'KeyG']]){audio.context.currentTime=time;key('keydown',code);await settle();key('keyup',code);}
 assert.equal(audio.plays.length,3);assert.equal(clock.running,true);assert.equal($('guidePanel').hidden,false);
 audio.context.currentTime=3.1;$('recordToggle').click();$('exportRecording').click();const saved=JSON.parse(await h.blob().text());
 assert.deepEqual(saved.events,[[50,0],[200,1],[350,4]]);assert.equal(saved.duration,500);
 h.frame(5.2);assert.equal($('guidePanel').dataset.index,'4','a stalled frame jumps directly to the right note');
 assert.equal(audio.plays.length,3,'a stalled frame must not add pretend notes');
 $('stopSong').click();assert.equal(clock.running,false);assert.equal($('guidePanel').hidden,true);
 assert.equal(w.document.querySelectorAll('.due,.upcoming').length,0);
});

test('tempo changes clear old guidance; restart restores its cue, and demo still yields to live input',async t=>{
 const h=setup(t),{$,audio,key,w}=h;
 $('guideSong').click();await settle();h.frame(2.6);
 $('bpm').value='120';$('bpm').dispatchEvent(new w.Event('input'));
 assert.equal($('guidePanel').hidden,true);assert.equal(w.document.querySelectorAll('.due,.upcoming').length,0);assert.match($('practiceHint').textContent,/重新/);
 $('guideSong').click();await settle();h.frame(4.7);assert.equal($('guidePanel').hidden,false);assert.ok(w.document.querySelector('[data-code="KeyA"]').classList.contains('due'));
 $('stopSong').click();$('listenSong').click();await settle();key('keydown','KeyD');await settle();key('keyup','KeyD');
 assert.equal($('guidePanel').hidden,true);assert.equal(audio.plays.at(-1).code,'KeyD');
});

test('pending guidance is cancelled by explicit stop or blur and cannot start late',async t=>{
 const h=setup(t),{$,audio,w}=h;
 for(const cancel of [()=>$('stopSong').click(),()=>w.dispatchEvent(new w.Event('blur'))]){
  const release=audio.defer();$('guideSong').click();await settle();assert.equal($('stopSong').disabled,false);cancel();release();await settle();
  assert.equal($('guidePanel').hidden,true);assert.equal($('guideSong').disabled,false);assert.equal($('stopSong').disabled,true);assert.equal(audio.plays.length,0);
 }
});


test('enabling the metronome during a demo uses the same count-in origin',async t=>{
 const h=setup(t),{$,audio,clock}=h;
 $('listenSong').click();await settle();audio.context.currentTime=1;
 $('metronomeToggle').click();await settle();assert.equal(clock.origin,.1);assert.equal(clock.bpm,96);
 $('stopSong').click();assert.equal(clock.running,false);
});

test('drum scores filter by instrument and simultaneous cues remain two genuine human hits',async t=>{
 const h=setup(t),{$,audio,w,key}=h;
 $('instrumentSelect').value='drums';$('instrumentSelect').dispatchEvent(new w.Event('change'));
 assert.deepEqual([...$('songSelect').options].map(x=>x.value),['drum-first-bar','drum-hat-pulse']);
 $('songSelect').value='drum-hat-pulse';$('songSelect').dispatchEvent(new w.Event('change'));
 $('guideSong').click();await settle();h.frame(2.6);assert.equal(w.document.querySelectorAll('.drum-pad.due').length,2);assert.equal(audio.plays.length,0);
 for(const code of ['KeyZ','KeyC']){key('keydown',code);await settle();key('keyup',code);}assert.equal(audio.plays.length,2);assert.equal($('guidePanel').hidden,false);
 $('stopSong').click();const clip={...recording.makeRecording('piano',96,4),duration:100,events:[[0,0]]};await h.importFile(clip);$('playRecording').click();await settle();
 assert.equal($('instrumentSelect').value,'piano');assert.ok([...$('songSelect').options].every(x=>!x.value.startsWith('drum-')));
});

test('birthday pickup starts after two preparatory beats and its downbeat follows the first combined beat',async t=>{
 const h=setup(t),{$,w}=h;
 $('bpm').value='120';$('bpm').dispatchEvent(new w.Event('input'));$('songSelect').value='birthday';$('songSelect').dispatchEvent(new w.Event('change'));
 $('guideSong').click();await settle();h.frame(.2);assert.match($('guideTime').textContent,/预备 2 拍/);
 h.frame(1.1);assert.equal($('guidePanel').dataset.index,'0');assert.equal($('guidePanel').dataset.beat,'2');
 h.frame(1.6);assert.equal($('guidePanel').dataset.index,'2');assert.equal($('guidePanel').dataset.beat,'0');
 assert.equal(w.document.querySelector('[data-code="KeyS"]').classList.contains('due'),true);
});

test('voluntary support dialog blocks performance keys and closing restores free play',async t=>{
 const h=setup(t),{$,audio,key,w}=h;
 w.HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','');};
 w.HTMLDialogElement.prototype.close=function(){this.removeAttribute('open');};
 w.document.querySelector('[data-open-support]').click();assert.equal($('supportDialog').open,true);
 key('keydown','KeyA');await settle();assert.equal(audio.plays.length,0);
 $('closeSupport').click();assert.equal($('supportDialog').open,false);
 key('keydown','KeyA');await settle();assert.equal(audio.plays.length,1);key('keyup','KeyA');
});

test('full Painter demo schedules all 48 notes and leaves the closing rest silent',async t=>{
 const h=setup(t),{$,audio,w}=h;
 $('songSelect').value='painter';$('songSelect').dispatchEvent(new w.Event('change'));
 assert.equal(w.document.querySelectorAll('.score-phrase').length,4);
 assert.equal(w.document.querySelectorAll('.score-note').length,49);
 assert.equal(w.document.querySelector('.score-phrase:last-child .score-note:last-child kbd').textContent,'休止');
 $('bpm').value='120';$('listenSong').click();await settle();
 assert.equal($('meterSelect').value,'2');
 for(let i=0;i<=431;i++){audio.context.currentTime=i*.04;h.tick();h.frame(audio.context.currentTime);}
 assert.equal(audio.plays.length,48);assert.equal(audio.plays.at(-1).code,'KeyA');
 assert.ok(Math.abs(audio.plays.at(-1).time-16.1)<1e-8);
 assert.equal($('scoreStatus').textContent,'听完了，换你试试。');
});

test('Painter rest clears key cues, 2/4 guide never records automatic melody',async t=>{
 const h=setup(t),{$,audio,w,key,clock}=h;
 $('songSelect').value='painter';$('songSelect').dispatchEvent(new w.Event('change'));
 $('bpm').value='120';$('guideSong').click();await settle();assert.equal(clock.meter,2);
 h.frame(16.2);assert.equal($('guidePanel').dataset.index,'47');
 assert.equal(w.document.querySelectorAll('.due').length,1);
 h.frame(16.7);assert.equal($('guidePanel').dataset.index,'48');
 assert.equal($('guideNow').textContent,'休止 · 空一拍');
 assert.equal(w.document.querySelectorAll('.due,.upcoming').length,0);assert.equal(audio.plays.length,0);
 $('recordToggle').click();await settle();audio.context.currentTime=16.8;key('keydown','KeyD');await settle();key('keyup','KeyD');
 audio.context.currentTime=16.9;$('recordToggle').click();$('exportRecording').click();
 const saved=JSON.parse(await h.blob().text());assert.equal(saved.meter,2);assert.deepEqual(saved.events,[[100,2]]);
 assert.deepEqual(recording.validateRecording(saved),saved);
});

test('five-key Miles demo plays one complete round, never repeats a tied note and leaves a silent ending',async t=>{
 const h=setup(t),{$,audio,w}=h;
 $('songSelect').value='five-hundred-miles';$('songSelect').dispatchEvent(new w.Event('change'));
 assert.equal(w.document.querySelectorAll('.score-phrase').length,4);
 assert.equal(w.document.querySelectorAll('.score-note').length,52);
 $('bpm').value='120';$('listenSong').click();await settle();
 h.frame(.5);assert.match($('guideTime').textContent,/预备/);
 for(let i=13;i<=862;i++){audio.context.currentTime=i*.04;h.tick();h.frame(audio.context.currentTime);}
 assert.equal(audio.plays.length,51);assert.equal(audio.plays[0].code,'KeyF');
 assert.equal(audio.plays.at(-1).code,'KeyH');assert.ok(Math.abs(audio.plays.at(-1).time-30.1)<1e-8);
 assert.equal($('scoreStatus').textContent,'听完了，换你试试。');
 assert.equal($('recordingInfo').textContent,'0:00 · 0 次按键');
});

test('Miles guidance uses actual multi-beat rest and clears the final key cue',async t=>{
 const h=setup(t),{$,w}=h;
 $('songSelect').value='five-hundred-miles';$('songSelect').dispatchEvent(new w.Event('change'));
 $('bpm').value='120';$('guideSong').click();await settle();
 h.frame(31);assert.equal($('guidePanel').dataset.index,'50');
 assert.equal($('guideNext').textContent,'接着空 2.5 拍');
 h.frame(33);assert.equal($('guidePanel').dataset.index,'51');
 assert.equal($('guideNow').textContent,'休止 · 空 2.5 拍');
 assert.equal(w.document.querySelectorAll('.due,.upcoming').length,0);
});
