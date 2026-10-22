// DOM/event regression coverage. Audio is deliberately a controllable fake:
// these checks do not establish sound quality, device latency, or mobile support.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import * as bindings from '../public/bindings.js';
import * as scores from '../public/scores.js';
import * as recording from '../public/recording.js';

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
    start(bpm,meter){Object.assign(this,{running:true,bpm,meter});}
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
  w.__deps={...bindings,...scores,...recording,SampledAudio:FakeAudio,BeatClock:FakeClock};
  w.eval('const {KEYS,MELODY,DRUMS,CHORDS,LEGACY_KEYS,SampledAudio,BeatClock,SONGS,scoreEvents,CODES,MAX_MS,MAX_EVENTS,makeRecording,validateRecording}=window.__deps;\n'+app);
  const $=id=>w.document.getElementById(id);
  const key=(type,code,target=w.document,options={})=>target.dispatchEvent(new w.KeyboardEvent(type,{code,bubbles:true,cancelable:true,...options}));
  const frame=time=>{audio.context.currentTime=time;const queued=[...frames.values()];frames.clear();for(const fn of queued)fn();};
  const importFile=async value=>{
    const text=JSON.stringify(value);
    Object.defineProperty($('importRecording'),'files',{value:[{size:Buffer.byteLength(text),text:async()=>text}],configurable:true});
    $('importRecording').dispatchEvent(new w.Event('change'));await settle();
  };
  t.after(()=>{w.dispatchEvent(new w.Event('blur'));dom.window.close();});
  return {w,$,audio,clock,key,frame,importFile,blob:()=>exportedBlob};
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
 assert.equal($('melodyKeys').hidden,true);assert.equal($('scoreBook').hidden,true);
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
