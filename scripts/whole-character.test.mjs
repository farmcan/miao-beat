import test from 'node:test';
import assert from 'node:assert/strict';
import {createPoseState} from '../public/whole-character.js';

const config={idle:0,actions:{leftLow:{contact:1,release:[2,0]},leftMid:{contact:3,release:[4,5]},rightOuter:{contact:6,release:[7,8]},rightMid:{contact:9,release:[10,11]},both:{contact:12,release:[1,0]}}};
const low={code:'KeyA',kind:'note',midi:60},high={code:'KeyK',kind:'note',midi:72};
test('real notes select complete left/right/both poses; release preserves remaining held side',()=>{
  let time=0;const p=createPoseState(config,()=>time);
  p.update([low]);p.strike(low);assert.equal(p.sample().pose,'leftLow');
  time=10;p.update([low,high]);p.strike(high);assert.equal(p.sample().pose,'both');
  time=150;p.update([low]);assert.equal(p.sample().pose,'leftLow');
  p.update([]);assert.equal(p.sample().phase,'release');
  time=300;assert.equal(p.sample().phase,'idle');
});
test('rapid repeats do not rewind a whole clip or queue actions; interruption is immediate',()=>{
  let time=0;const p=createPoseState(config,()=>time);p.strike(low);
  time=80;p.strike(low);assert.equal(p.sample().frame,1);
  time=191;assert.equal(p.sample().phase,'release');
  time=215;p.strike(high);assert.equal(p.sample().frame,6);
  time=500;p.sample();time=700;assert.equal(p.sample().phase,'idle');
});
test('mode/blur reset clears active notes, and percussion is not painted as a piano press',()=>{
  const p=createPoseState(config,()=>0);p.update([low]);p.strike(low);p.reset();
  assert.equal(p.sample().frame,0);assert.equal(p.sample().phase,'idle');
  assert.equal(p.strike({code:'KeyZ',kind:'drum',voice:'kick'}),false);
  assert.equal(p.sample().phase,'idle');
});
