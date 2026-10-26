import test from 'node:test';import assert from 'node:assert/strict';
import {KEYS,MELODY,DRUMS,CHORDS,LEGACY_KEYS} from '../public/bindings.js';
import {SONGS,scoreEvents} from '../public/scores.js';
import {CODES,makeRecording,validateRecording} from '../public/recording.js';
import {BeatClock} from '../public/clock.js';
test('every score pitch and compact code resolves to the same instrument key',()=>{
  assert.equal(new Set(KEYS.map(k=>k.code)).size,25);assert.deepEqual(CODES,KEYS.map(k=>k.code));
  for(const song of SONGS){const events=scoreEvents(song,120);for(let i=0;i<events.length;i++){
    if(song.kind==='rhythm'){for(const code of events[i].codes||[events[i].code])assert.ok(DRUMS.some(k=>k.code===code),code);}else if(!events[i].rest)assert.ok(MELODY.some(k=>k.sub===events[i].note),events[i].note);assert.ok(events[i].beats>0);
    if(i)assert.ok(Math.abs(events[i].offset-events[i-1].offset-events[i-1].beats*.5)<1e-8);
  }}
  for(const song of SONGS){const events=scoreEvents(song,120),last=events.at(-1);assert.ok(Math.abs(last.offset+last.beats*.5-song.totalBeats*.5)<1e-8);assert.ok(song.instruments.length);}
  const painter=SONGS.find(song=>song.id==='painter'),events=scoreEvents(painter,120);
  assert.equal(painter.meter,2);assert.equal(painter.phrases.length,4);assert.equal(painter.totalBeats,32);
  assert.deepEqual(painter.phrases.map(row=>row.reduce((sum,e)=>sum+e.beats,0)),[8,8,8,8]);
  assert.equal(events.filter(e=>!e.rest).length,48);assert.deepEqual(events.at(-1),{rest:true,beats:1,index:48,offset:15.5});
  assert.equal(events.at(-2).note,'C4');assert.equal(events.at(-2).beats,1);assert.equal(events.at(-2).offset,15);
});
test('new bindings append to the immutable legacy event-code prefix and retain legacy percussion',()=>{
  const old=['KeyA','KeyS','KeyD','KeyF','KeyG','KeyH','KeyJ','KeyK','KeyW','KeyE','KeyT','KeyY','KeyU','KeyZ','KeyX','KeyC','KeyV'];
  assert.deepEqual(CODES.slice(0,17),old);assert.deepEqual(LEGACY_KEYS.map(key=>key.code),old);
  assert.deepEqual(CODES.slice(17),['KeyB','KeyN','KeyM','KeyL','Digit1','Digit2','Digit3','Digit4']);
  assert.deepEqual(DRUMS.map(key=>[key.key,key.voice]),[['Z','kick'],['X','snare'],['C','closed-hat'],['V','open-hat'],['B','tom-low'],['N','tom-high'],['M','crash'],['L','ride']]);
  assert.equal(LEGACY_KEYS[15].voice,'shaker');assert.equal(LEGACY_KEYS[16].voice,'bongoHigh');
  assert.equal(KEYS[15].voice,'closed-hat');assert.equal(KEYS[16].voice,'open-hat');
});
test('four chord keys contain only their chord tones and fit the guitar sample range',()=>{
  const pitchClasses={C:[0,4,7],Am:[9,0,4],F:[5,9,0],G:[7,11,2]};
  assert.deepEqual(CHORDS.map(key=>[key.code,key.label]),[['Digit1','C'],['Digit2','Am'],['Digit3','F'],['Digit4','G']]);
  for(const key of CHORDS){
    assert.equal(key.kind,'chord');assert.equal(key.notes.length,6);
    assert.ok(key.notes.every((midi,i)=>Number.isInteger(midi)&&midi>=48&&midi<=72&&pitchClasses[key.label].includes(midi%12)&&(!i||midi>key.notes[i-1])));
    assert.deepEqual(new Set(key.notes.map(midi=>midi%12)),new Set(pitchClasses[key.label]));
  }
  assert.equal(CHORDS[1].voicing,'Am/C');assert.equal(CHORDS[3].voicing,'G/D');
});
test('recording roundtrip preserves simultaneous notes and rejects invalid or excessive data',()=>{
  const value=makeRecording('marimba',96,4);Object.assign(value,{duration:2000,events:[[0,0],[0,4],[250,14],[1900,7]]});
  assert.deepEqual(validateRecording(JSON.parse(JSON.stringify(value))),value);
  for(const patch of [{engine:'future-engine'},{duration:300001},{events:[[3000,0]]},{events:[[0,99]]},{events:[[100,0],[50,1]]},{events:Array.from({length:33},()=>[0,0])},{events:[[0,'KeyA']]}])assert.throws(()=>validateRecording({...value,...patch}));
  assert.deepEqual(Object.keys(validateRecording({...value,unknown:'ignored',url:'https://example.com'})),Object.keys(value));
});
test('v2 sample files cover all instruments and appended codes without altering v1 files',()=>{
  for(const instrument of ['piano','marimba','guitar','drums']){
    const value=makeRecording(instrument,120,3),events=instrument==='guitar'?[[0,17],[0,20],[150,21],[900,24]]:instrument==='drums'?[[0,13],[150,17],[900,20]]:[[0,0],[150,17],[900,20]];
    Object.assign(value,{duration:1000,events});
    assert.equal(value.version,2);assert.equal(value.engine,'sample-v1');
    assert.deepEqual(validateRecording(JSON.parse(JSON.stringify(value))),value);
  }
  for(const instrument of ['marimba','sparkle']){
    const old={format:'miao-beat',version:1,engine:'ui-synth-v1',instrument,bpm:96,meter:4,duration:1000,events:[[0,0],[0,15],[900,16]]};
    assert.deepEqual(validateRecording(old),old);
    assert.throws(()=>validateRecording({...old,events:[[0,17]]}));
    assert.throws(()=>validateRecording({...old,instrument:'guitar'}));
    assert.throws(()=>validateRecording({...old,version:2}));
    assert.throws(()=>validateRecording({...old,engine:'sample-v1'}));
  }
  assert.throws(()=>validateRecording(makeRecording('sparkle',96,4)));
  assert.throws(()=>validateRecording({...makeRecording('piano',96,4),events:[[0,25]]}));
});
test('v2 rejects keys unavailable to the chosen instrument while legacy v1 remains unchanged',()=>{
  for(const instrument of ['piano','marimba'])for(const code of [21,22,23,24]){
    assert.throws(()=>validateRecording({...makeRecording(instrument,96,4),events:[[0,code]]}),/按键与所选乐器不匹配/);
  }
  for(const code of [0,12,21,24])assert.throws(()=>validateRecording({...makeRecording('drums',96,4),events:[[0,code]]}),/按键与所选乐器不匹配/);
  const guitar={...makeRecording('guitar',96,4),events:Array.from({length:25},(_,code)=>[code*100,code]),duration:2400};
  assert.deepEqual(validateRecording(guitar),guitar);
  const legacy={format:'miao-beat',version:1,engine:'ui-synth-v1',instrument:'marimba',bpm:96,meter:4,duration:1600,events:Array.from({length:17},(_,code)=>[code*100,code])};
  assert.deepEqual(validateRecording(legacy),legacy);
});
test('metronome schedules exact audio-clock intervals, stops queued nodes and skips stalled backlog',()=>{
  const nodes=[];const param=()=>({value:0,setValueAtTime(){},exponentialRampToValueAtTime(){},cancelScheduledValues(){}});
  const context={currentTime:0,createOscillator(){const n={frequency:{value:0},connect(){},disconnect(){},start(t){this.at=t},stop(){this.stopped=true}};nodes.push(n);return n;},createGain(){return {gain:param(),connect(){},disconnect(){}}}};
  const clock=new BeatClock({context,master:{}},()=>{});clock.start(120,3);
  for(let i=1;i<7;i++){context.currentTime=i*.5;clock.schedule();}
  assert.deepEqual(clock.history.map(x=>x.beat),[0,1,2,0,1,2,0]);
  for(let i=1;i<clock.history.length;i++)assert.ok(Math.abs(clock.history[i].time-clock.history[i-1].time-.5)<1e-9);
  context.currentTime=20;clock.schedule();assert.equal(clock.history.at(-1).beat,0);assert.ok(clock.history.at(-1).time>=20);
  clock.stop();assert.ok(nodes.every(n=>n.stopped));assert.equal(clock.queue.length,0);assert.equal(clock.nodes.size,0);
});

test('2/4 recordings roundtrip while legacy format acceptance stays unchanged',()=>{
 const song={...makeRecording('piano',108,2),duration:500,events:[[0,4],[250,2]]};
 assert.deepEqual(validateRecording(JSON.parse(JSON.stringify(song))),song);
 assert.throws(()=>validateRecording({...song,version:1,engine:'ui-synth-v1',instrument:'marimba'}));
 for(const meter of [0,1,5])assert.throws(()=>validateRecording({...song,meter}));
});

test('Five Hundred Miles fits five white keys and keeps pickup, repeat phrases and tied ending',()=>{
 const song=SONGS.find(song=>song.id==='five-hundred-miles'),events=scoreEvents(song,120),notes=events.filter(e=>!e.rest);
 assert.deepEqual([...new Set(notes.map(e=>e.note))].sort(),['A4','C4','D4','F4','G4']);
 assert.equal(notes.length,51);assert.equal(song.pickupBeats,2);assert.equal(song.totalBeats,66);
 assert.deepEqual(song.phrases.map(row=>row.reduce((sum,e)=>sum+e.beats,0)),[18,16,16,16]);
 assert.deepEqual(song.phrases[0].slice(2),song.phrases[2]);
 assert.equal(notes.at(-1).note,'A4');assert.equal(notes.at(-1).beats,5.5);
 assert.deepEqual(events.at(-1),{rest:true,beats:2.5,index:51,offset:31.75});
});
