import test from 'node:test';import assert from 'node:assert/strict';
import {createFrameState,validateFrameManifest,validateInstrumentManifest,INSTRUMENT_FRAME_IDS} from '../public/full-frame-character.js';
import {MELODY,DRUMS,CHORDS} from '../public/bindings.js';
import fs from 'node:fs';
const plan=JSON.parse(fs.readFileSync(new URL('../design/whole-cat-frames-2026-10-25/plan.json',import.meta.url)));
const config={version:1,width:1254,height:1254,frames:Object.fromEntries(plan.frames.map(f=>[f.id,f.id+'.jpg']))};
const key=code=>({kind:'note',code});
const bandConfig={version:1,width:1254,height:1254,modes:Object.fromEntries(Object.entries(INSTRUMENT_FRAME_IDS).map(([mode,ids])=>[mode,{frames:Object.fromEntries(ids.map(id=>[id,mode+'/'+id+'.jpg']))}]))};
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

test('guitar accepts thirteen notes and four actual chord controls, showing the latest fretting target',()=>{
 assert.equal(INSTRUMENT_FRAME_IDS.guitar.length,18);validateInstrumentManifest(bandConfig);
 for(const k of [...MELODY,...CHORDS]){const p=createFrameState(()=>0,'guitar');p.update([k]);assert.equal(p.strike(k),true);assert.equal(p.sample().id,k.code);}
 let time=0;const p=createFrameState(()=>time,'guitar');p.update([CHORDS[0]]);p.strike(CHORDS[0]);time=100;p.update([CHORDS[0],MELODY[2]]);p.strike(MELODY[2]);assert.equal(p.sample().id,'KeyD');
 time=200;p.update([CHORDS[0]]);assert.equal(p.sample().id,'Digit1');assert.equal(p.strike(DRUMS[0]),false);
});

test('drums map all eight voices and sixteen two-side combinations to complete scenes',()=>{
 assert.equal(INSTRUMENT_FRAME_IDS.drums.length,25);
 for(const id of INSTRUMENT_FRAME_IDS.drums){const p=createFrameState(()=>0,'drums'),keys=id==='idle'?[]:id.split('-').map(code=>DRUMS.find(k=>k.code===code));p.update(keys);for(const k of keys)assert.equal(p.strike(k),true);assert.equal(p.sample().id,id);}
 const p=createFrameState(()=>0,'drums');p.update([DRUMS[1]]);assert.equal(p.sample().id,'idle');assert.equal(p.strike(MELODY[0]),false);
 const bad=structuredClone(bandConfig);delete bad.modes.drums.frames['KeyC-KeyV'];assert.throws(()=>validateInstrumentManifest(bad));
});

test('a late image cannot repaint an older input, and each draw uses one whole scene',async t=>{
 const {JSDOM}=await import('jsdom');const {mountCharacter}=await import('../public/full-frame-character.js');
 const dom=new JSDOM('<div id="scene" data-instrument="piano"><svg class="cat-scene"></svg><div class="stage-readout"></div></div>');const w=dom.window;
 let now=0,serial=0,releaseA,releaseGuitar;const queue=new Map(),draws=[];
 t.mock.method(w.performance,'now',()=>now);w.requestAnimationFrame=fn=>{queue.set(++serial,fn);return serial;};w.cancelAnimationFrame=id=>queue.delete(id);
 w.HTMLCanvasElement.prototype.getContext=()=>({drawImage(...args){assert.equal(args.length,3,'no body/limb crops or independent compositing');draws.push(args[0].id);}});
 w.createImageBitmap=async blob=>({width:1254,height:1254,id:await blob.text(),close(){}});
 const deferredA=new Promise(resolve=>{releaseA=resolve;});
 const deferredGuitar=new Promise(resolve=>{releaseGuitar=resolve;});
 t.mock.method(globalThis,'fetch',async input=>{const path=new URL(input).pathname,name=path.split('/').at(-1);if(name==='manifest.json')return Response.json(path.includes('instrument-scenes-v1')?bandConfig:config);if(name==='KeyA.jpg')await(path.includes('/guitar/')?deferredGuitar:deferredA);return new Response(name.replace('.jpg',''));});
 const controller=mountCharacter(w.document.querySelector('#scene'));t.after(()=>{controller.destroy();w.close();});
 const tick=()=>new Promise(resolve=>setImmediate(resolve));const frame=()=>{const current=[...queue.values()];queue.clear();for(const fn of current)fn(now);};
 await controller.ready;await tick();
 controller.update('piano',[key('KeyA')]);controller.strike(key('KeyA'));frame();
 now=20;controller.update('piano',[key('KeyS')]);controller.strike(key('KeyS'));frame();await tick();
 assert.equal(w.document.querySelector('#scene').dataset.wholeFrame,'KeyS');
 releaseA();await tick();assert.equal(w.document.querySelector('#scene').dataset.wholeFrame,'KeyS');assert.equal(draws.includes('KeyA'),false);
 now=200;controller.update('piano',[]);frame();await tick();assert.equal(w.document.querySelector('#scene').dataset.wholeFrame,'idle');
 controller.update('guitar',[MELODY[0]]);controller.strike(MELODY[0],'guitar');frame();
 assert.equal(w.document.querySelector('canvas').hidden,true);assert.equal(w.document.querySelector('.whole-frame-message').hidden,false,'a new instrument must show loading feedback while its whole image is pending');
 controller.update('drums',[DRUMS[1]]);controller.strike(DRUMS[1],'drums');frame();await tick();assert.equal(w.document.querySelector('#scene').dataset.wholeFrame,'drums:KeyX');
 releaseGuitar();await tick();assert.equal(w.document.querySelector('#scene').dataset.wholeFrame,'drums:KeyX','old guitar cannot repaint the new instrument');
 assert.equal(w.document.querySelectorAll('canvas').length,1);
});

test('changing targets cannot reset capture stall detection while all contact decodes are blocked',async t=>{
 const {JSDOM}=await import('jsdom');const {mountCharacter}=await import('../public/full-frame-character.js');
 const dom=new JSDOM('<div id="scene" data-instrument="piano"><svg class="cat-scene"></svg><div class="stage-readout"></div></div>'),w=dom.window;
 let now=0,serial=0,release;const queue=new Map(),draws=[],blocked=new Promise(resolve=>{release=resolve;});
 t.mock.method(w.performance,'now',()=>now);w.requestAnimationFrame=fn=>{queue.set(++serial,fn);return serial;};w.cancelAnimationFrame=id=>queue.delete(id);
 w.HTMLCanvasElement.prototype.getContext=()=>({drawImage(image){draws.push(image.id);}});
 w.createImageBitmap=async blob=>{const id=await blob.text();if(id!=='idle')await blocked;return {width:1254,height:1254,id,close(){}};};
 t.mock.method(globalThis,'fetch',async input=>{const name=new URL(input).pathname.split('/').at(-1);return name==='manifest.json'?Response.json(config):new Response(name.replace('.jpg',''));});
 const scene=w.document.querySelector('#scene'),controller=mountCharacter(scene),tick=()=>new Promise(resolve=>setImmediate(resolve));
 t.after(()=>{controller.destroy();release();w.close();});
 const frame=async time=>{now=time;const callbacks=[...queue.values()];queue.clear();for(const fn of callbacks)fn(now);await tick();};
 await controller.ready;await tick();controller.setCaptureMode(true);
 for(let i=1;i<=12;i++){
   now=i*100;const target=key(i%2?'KeyA':'KeyS');controller.update('piano',[target]);controller.strike(target);await frame(now);
   if(i<=3)assert.equal(controller.captureHealthy(),true,'allow a bounded initial decode window');
   if(i>=4)assert.equal(controller.captureHealthy(),false,'new targets must not extend the first unresolved paint deadline');
 }
 assert.deepEqual(draws,['idle'],'the stalled capture still contains only its original idle scene');
 release();await tick();await tick();
 assert.equal(scene.dataset.wholeFrame,'KeyS','only the latest target may recover after late decodes');
 assert.equal(draws.includes('KeyA'),false,'an obsolete decoded target cannot paint');
 assert.equal(controller.captureHealthy(),true,'actual current-frame paint restores health');
 const contactDelay=scene.dataset.contactPaintDelayMs;
 controller.update('piano',[]);await frame(1400);
 assert.equal(scene.dataset.contactPaintDelayMs,contactDelay,'idle recovery cannot overwrite contact latency');
});

test('capture cleanup clears a prior draw failure before the next exporter startup health check',async t=>{
 const {JSDOM}=await import('jsdom');const {mountCharacter}=await import('../public/full-frame-character.js');
 const dom=new JSDOM('<div id="scene" data-instrument="piano"><svg class="cat-scene"></svg><div class="stage-readout"></div></div>'),w=dom.window;
 let now=0,serial=0,failPaint=false;const queue=new Map();
 t.mock.method(w.performance,'now',()=>now);w.requestAnimationFrame=fn=>{queue.set(++serial,fn);return serial;};w.cancelAnimationFrame=id=>queue.delete(id);
 w.HTMLCanvasElement.prototype.getContext=()=>({drawImage(){if(failPaint)throw Error('temporary canvas draw failure');}});
 w.createImageBitmap=async()=>({width:1254,height:1254,close(){}});
 t.mock.method(globalThis,'fetch',async input=>new URL(input).pathname.endsWith('manifest.json')?Response.json(config):new Response('frame'));
 const scene=w.document.querySelector('#scene'),controller=mountCharacter(scene),tick=()=>new Promise(resolve=>setImmediate(resolve));
 t.after(()=>{controller.destroy();w.close();});
 const frame=async time=>{now=time;const callbacks=[...queue.values()];queue.clear();for(const fn of callbacks)fn(now);await tick();};
 await controller.ready;await tick();controller.setCaptureMode(true);
 failPaint=true;controller.update('piano',[key('KeyA')]);controller.strike(key('KeyA'));await frame(100);
 assert.equal(scene.dataset.wholeFrameStatus,'unavailable');assert.equal(controller.captureHealthy(),false);
 failPaint=false;controller.update('piano',[]);await frame(300);
 assert.equal(scene.dataset.wholeFrameStatus,'ready');
 assert.equal(controller.captureHealthy(),false,'recovery must not turn an already failed in-progress capture into a success');
 controller.setCaptureMode(false);
 assert.equal(controller.captureHealthy(),true,'the next exporter paints before enabling capture mode; a cleaned-up job must not poison that startup check');
});
