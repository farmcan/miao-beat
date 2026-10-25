import test from 'node:test';import assert from 'node:assert/strict';
import {createFrameState,validateFrameManifest} from './full-frame-character.js';
import fs from 'node:fs';
const plan=JSON.parse(fs.readFileSync(new URL('../plan.json',import.meta.url)));
const config={version:1,width:1254,height:1254,frames:Object.fromEntries(plan.frames.map(f=>[f.id,f.id+'.jpg']))};
const key=code=>({kind:'note',code});
test('manifest covers idle, thirteen single keys and every 6 by 7 two-paw whole scene',()=>{
 assert.equal(plan.frames.length,56);assert.equal(Object.keys(validateFrameManifest(config).frames).length,56);
 for(const frame of plan.frames){const p=createFrameState(()=>0);p.update(frame.keys);for(const k of frame.keys)p.strike(k);assert.equal(p.sample().id,frame.id);}
 const bad=structuredClone(config);delete bad.frames['KeyF-KeyT'];bad.frames.other='other.jpg';assert.throws(()=>validateFrameManifest(bad));
});
test('raw held controls before audio confirmation do not produce a pose',()=>{
 const p=createFrameState(()=>0);p.update([key('KeyA')]);assert.equal(p.sample().id,'idle');assert.deepEqual(p.sample().confirmed,[]);
 assert.equal(p.strike({kind:'drum',code:'KeyZ'}),false);assert.equal(p.sample().id,'idle');
});
test('newest held note per paw chooses one complete frame, releasing restores the remaining note',()=>{
 let time=0;const p=createFrameState(()=>time),a=key('KeyA'),f=key('KeyF'),g=key('KeyG');
 p.update([a]);p.strike(a);time=100;p.update([a,f,g]);p.strike(f);p.strike(g);assert.equal(p.sample().id,'KeyF-KeyG');
 time=200;p.update([a,g]);assert.equal(p.sample().id,'KeyA-KeyG');assert.deepEqual(p.sample().held,['KeyA','KeyG']);
 p.update([g]);assert.equal(p.sample().id,'KeyG');p.update([]);assert.equal(p.sample().id,'idle');
});
test('fast pulses are interruptible and expire without replaying a stale whole-frame queue',()=>{
 let time=0;const p=createFrameState(()=>time);p.strike(key('KeyA'));time=40;p.strike(key('KeyS'));assert.equal(p.sample().id,'KeyS');
 time=111;assert.equal(p.sample().id,'KeyS');time=151;assert.equal(p.sample().id,'idle');
 p.strike(key('KeyG'));p.reset();assert.equal(p.sample().id,'idle');assert.equal(p.sample().needsFrame,false);
});
