import test from 'node:test';
import assert from 'node:assert/strict';
import {MELODY,DRUMS} from '../public/bindings.js';
import {pianoKeyGeometry,pianoContact,armGuide,createPianoState} from '../public/precise-character.js';

const note=code=>MELODY.find(k=>k.code===code);
test('all thirteen physical keys have distinct in-face contacts and remain inside the fixed arm workspace',()=>{
  assert.equal(MELODY.filter(k=>!k.black).length,8);assert.equal(MELODY.filter(k=>k.black).length,5);
  const contacts=MELODY.map(k=>pianoContact(k));assert.equal(new Set(contacts.map(c=>c.point.join(','))).size,13);
  for(const key of MELODY){
    const base=pianoKeyGeometry(key.code,0),down=pianoKeyGeometry(key.code,1),contact=pianoContact(key);
    assert.ok(down.points[2][1]>base.points[2][1]);assert.ok(contact.point[1]>690&&contact.point[1]<down.points[2][1]);
    assert.ok(contact.point[0]>Math.min(...down.points.map(p=>p[0]))&&contact.point[0]<Math.max(...down.points.map(p=>p[0])));
    assert.doesNotThrow(()=>armGuide(contact.side,contact.point));
  }
  assert.equal(pianoContact(DRUMS[0]),null);
  assert.throws(()=>armGuide('left',[2000,2000]),RangeError);
});

test('held paint before successful audio never depresses a key or invents a paw strike',()=>{
  let time=0;const state=createPianoState(()=>time);state.update([note('KeyA')]);time=100;
  const pose=state.sample();assert.equal(pose.keys.KeyA,0);assert.equal(pose.hands.left.code,null);assert.deepEqual(pose.held,[]);
});

test('confirmed polyphony depresses every held key and releases only the released key',()=>{
  let time=0;const state=createPianoState(()=>time),a=note('KeyA'),f=note('KeyF'),k=note('KeyK');
  state.update([a]);state.strike(a);time=100;state.sample();
  state.update([a,f,k]);state.strike(f);state.strike(k);time=200;
  let pose=state.sample();for(const code of ['KeyA','KeyF','KeyK'])assert.equal(pose.keys[code],1);
  assert.equal(pose.hands.left.code,'KeyF');assert.equal(pose.hands.right.code,'KeyK');
  const before=pose.hands.left;state.update([a,k]);pose=state.sample();assert.equal(pose.hands.left.x,before.x);assert.equal(pose.hands.left.y,before.y,'release does not teleport to rest');
  time=360;pose=state.sample();assert.equal(pose.keys.KeyF,0);assert.equal(pose.keys.KeyA,1);assert.equal(pose.keys.KeyK,1);assert.equal(pose.hands.left.code,'KeyA');
  state.update([k]);time=550;pose=state.sample();assert.equal(pose.keys.KeyA,0);assert.equal(pose.keys.KeyK,1);assert.equal(pose.hands.left.code,null);
});

test('one-shot replay has a short contact pulse and rapid replacement continues from the visible pose',()=>{
  let time=0;const state=createPianoState(()=>time);state.strike(note('KeyA'));time=35;
  const before=state.sample().hands.left;state.strike(note('KeyF'));const after=state.sample().hands.left;
  assert.equal(after.x,before.x);assert.equal(after.y,before.y);assert.equal(after.vx,before.vx);assert.equal(after.vy,before.vy);
  time=100;let pose=state.sample();assert.equal(pose.keys.KeyF,1);assert.equal(pose.hands.left.code,'KeyF');
  time=150;state.sample();time=400;pose=state.sample();assert.equal(pose.keys.KeyF,0);assert.equal(pose.hands.left.code,null);
  state.reset();pose=state.sample();assert.deepEqual([pose.hands.left.x,pose.hands.left.y],[430,720]);assert.equal(pose.needsFrame,false);
});

test('rapid interruptions across every key stay inside the fixed workspace with the larger paw',()=>{
  for(const gap of [10,25,45,65]){
    let time=0;const state=createPianoState(()=>time);
    const sequence=[...MELODY,...MELODY.toReversed(),note('KeyA'),note('KeyF'),note('KeyA'),note('KeyF')];
    for(const key of sequence){
      state.update([key]);state.strike(key);const start=time;
      for(let delta=0;delta<gap;delta+=3){time=start+delta;const pose=state.sample();for(const hand of Object.values(pose.hands))assert.doesNotThrow(()=>armGuide(hand.side,[hand.x,hand.y]));}
      time=start+gap;
    }
  }
});
