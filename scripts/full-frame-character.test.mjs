import test from 'node:test';import assert from 'node:assert/strict';
import {createFrameState,validateFrameManifest} from '../public/full-frame-character.js';
import fs from 'node:fs';
const plan=JSON.parse(fs.readFileSync(new URL('../design/whole-cat-frames-2026-10-25/plan.json',import.meta.url)));
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

test('a late image cannot repaint an older input, and each draw uses one whole scene',async t=>{
 const {JSDOM}=await import('jsdom');const {mountCharacter}=await import('../public/full-frame-character.js');
 const dom=new JSDOM('<div id="scene" data-instrument="piano"><svg class="cat-scene"></svg><div class="stage-readout"></div></div>');const w=dom.window;
 let now=0,serial=0,releaseA;const queue=new Map(),draws=[];
 t.mock.method(w.performance,'now',()=>now);w.requestAnimationFrame=fn=>{queue.set(++serial,fn);return serial;};w.cancelAnimationFrame=id=>queue.delete(id);
 w.HTMLCanvasElement.prototype.getContext=()=>({drawImage(...args){assert.equal(args.length,3,'no body/limb crops or independent compositing');draws.push(args[0].id);}});
 w.createImageBitmap=async blob=>({width:1254,height:1254,id:await blob.text(),close(){}});
 const deferredA=new Promise(resolve=>{releaseA=resolve;});
 t.mock.method(globalThis,'fetch',async input=>{const name=new URL(input).pathname.split('/').at(-1);if(name==='manifest.json')return Response.json(config);if(name==='KeyA.jpg')await deferredA;return new Response(name.replace('.jpg',''));});
 const controller=mountCharacter(w.document.querySelector('#scene'));t.after(()=>{controller.destroy();w.close();});
 const tick=()=>new Promise(resolve=>setImmediate(resolve));const frame=()=>{const current=[...queue.values()];queue.clear();for(const fn of current)fn(now);};
 await controller.ready;await tick();
 controller.update('piano',[key('KeyA')]);controller.strike(key('KeyA'));frame();
 now=20;controller.update('piano',[key('KeyS')]);controller.strike(key('KeyS'));frame();await tick();
 assert.equal(w.document.querySelector('#scene').dataset.wholeFrame,'KeyS');
 releaseA();await tick();assert.equal(w.document.querySelector('#scene').dataset.wholeFrame,'KeyS');assert.equal(draws.includes('KeyA'),false);
 now=200;controller.update('piano',[]);frame();await tick();assert.equal(w.document.querySelector('#scene').dataset.wholeFrame,'idle');
 assert.equal(w.document.querySelectorAll('canvas').length,1);
});
