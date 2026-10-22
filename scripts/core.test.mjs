import test from 'node:test';import assert from 'node:assert/strict';
import {KEYS,MELODY} from '../public/bindings.js';
import {SONGS,scoreEvents} from '../public/scores.js';
import {CODES,makeRecording,validateRecording} from '../public/recording.js';
import {BeatClock} from '../public/clock.js';
test('every score pitch and compact code resolves to the same instrument key',()=>{
  assert.equal(new Set(KEYS.map(k=>k.code)).size,17);assert.deepEqual(new Set(CODES),new Set(KEYS.map(k=>k.code)));
  for(const song of SONGS){const events=scoreEvents(song,120);for(let i=0;i<events.length;i++){
    assert.ok(MELODY.some(k=>k.sub===events[i].note),events[i].note);assert.ok(events[i].beats>0);
    if(i)assert.ok(Math.abs(events[i].offset-events[i-1].offset-events[i-1].beats*.5)<1e-8);
  }}
  assert.equal(scoreEvents(SONGS[2],120).at(-1).offset+1,4); // two 4/4 bars at 120 BPM
});
test('recording roundtrip preserves simultaneous notes and rejects invalid or excessive data',()=>{
  const value=makeRecording('marimba',96,4);Object.assign(value,{duration:2000,events:[[0,0],[0,4],[250,14],[1900,7]]});
  assert.deepEqual(validateRecording(JSON.parse(JSON.stringify(value))),value);
  for(const patch of [{engine:'future-engine'},{duration:300001},{events:[[3000,0]]},{events:[[0,99]]},{events:[[100,0],[50,1]]},{events:Array.from({length:33},()=>[0,0])},{events:[[0,'KeyA']]}])assert.throws(()=>validateRecording({...value,...patch}));
  assert.deepEqual(Object.keys(validateRecording({...value,unknown:'ignored',url:'https://example.com'})),Object.keys(value));
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
