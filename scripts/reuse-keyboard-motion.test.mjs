// Generated from the authoring motion contract by prepare-reuse-keyboard-public.py.
import test from 'node:test';
import assert from 'node:assert/strict';
import {createPressMotion} from '../public/labs/reuse-keyboard/motion.js';
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);
test('a short click completes one contact and returns without a queued stroke',()=>{
  const m=createPressMotion();m.press(0);m.release(5);
  close(m.sample(0).amount,0);close(m.sample(60).amount,1);
  assert.ok(m.sample(100).amount>0);close(m.sample(200).amount,0);
  for(let t=201;t<1000;t+=7)close(m.sample(t).amount,0);
});
test('holding a key keeps one down state until release',()=>{
  const m=createPressMotion();m.press(0);close(m.sample(900).amount,1);
  m.release(900);close(m.sample(1040).amount,0);
});
test('a new attack during return preserves position and velocity',()=>{
  const m=createPressMotion();m.press(0);m.release(70);
  const before=m.sample(120);m.press(120);const after=m.sample(120);
  close(before.amount,after.amount);close(before.velocity,after.velocity);
  m.release(121);close(m.sample(210).amount,1);close(m.sample(350).amount,0);
});
test('dropped frames do not delay a return or produce catch-up motion',()=>{
  const a=createPressMotion(),b=createPressMotion();
  for(const m of[a,b]){m.press(0);m.release(2);}
  for(let t=0;t<=150;t+=5)a.sample(t);
  close(a.sample(160).amount,b.sample(160).amount);
  close(b.sample(1000).amount,0);assert.equal(b.sample(1000).needsFrame,false);
});
test('reset cancels a pending minimum attack',()=>{
  const m=createPressMotion();m.press(0);m.release(2);m.reset(10);
  close(m.sample(60).amount,0);assert.equal(m.sample(60).needsFrame,false);
});
test('duplicate pointer release cannot restart the return segment',()=>{
  const m=createPressMotion();m.press(0);m.release(70);m.release(150);
  close(m.sample(210).amount,0);assert.equal(m.sample(210).needsFrame,false);
});
test('a legato repeat releases the physical key once before its next contact',()=>{
  const m=createPressMotion();m.press(0);close(m.sample(60).amount,1);
  m.release(100);m.press(101);m.release(102);
  close(m.sample(131).amount,.4);close(m.sample(191).amount,1);
  close(m.sample(331).amount,0);assert.equal(m.sample(1000).needsFrame,false);
});
test('trajectory is bounded during rapid alternating physical inputs',()=>{
  const m=createPressMotion();
  for(let t=0;t<900;t+=30){m.press(t);m.release(t+4);const p=m.sample(t+5);assert.ok(p.amount>=0&&p.amount<=1);}
  close(m.sample(1200).amount,0);assert.equal(m.sample(1200).needsFrame,false);
});
