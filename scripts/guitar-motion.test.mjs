import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {createGuitarMotion,validateGuitarMotionManifest} from '../public/guitar-motion.js';
import {mountCharacter} from '../public/full-frame-character.js';
const data=JSON.parse(await fs.readFile(new URL('../public/character/guitar-motion-v1/manifest.json',import.meta.url)));
test('reviewed graph connects all guitar poses without the rejected direct low-to-high warp',()=>{
 validateGuitarMotionManifest(data);assert.equal(data.edges.some(e=>[e.from,e.to].includes('KeyA')&&[e.from,e.to].includes('KeyK')),false);
 const broken=structuredClone(data);broken.edges[0].file='../limb.png';assert.throws(()=>validateGuitarMotionManifest(broken));
});
test('attack includes complete-scene intermediate frames; return reaches idle in bounded time',()=>{
 let now=0;const m=createGuitarMotion(data,()=>now);m.go('Digit4');now=35;const p=m.sample();assert.equal(p.edge,'e03');assert.ok(p.cell>=0&&p.cell<7);now=90;assert.equal(m.sample().pose,'Digit4');m.go('idle');now=120;assert.ok(m.sample().edge);now=300;assert.deepEqual(m.sample(),{pose:'idle',needsFrame:false});
});
test('one distant note never tours other notes; a new input replaces its single action',()=>{
 let now=0;const m=createGuitarMotion(data,()=>now);m.go('KeyK');const edges=new Set(),poses=new Set();
 for(now=0;now<400;now++){const p=m.sample();if(p.edge)edges.add(p.edge);if(p.pose)poses.add(p.pose);}
 assert.equal(edges.size,1,'one distant input cannot queue thirteen intermediate playing actions');assert.deepEqual([...poses],['KeyK'],'no other note endpoint is played on the way');
 now=500;m.reset();m.go('KeyK');now=512;m.go('Digit2');assert.equal(m.target,'Digit2');now=1000;assert.equal(m.sample().pose,'Digit2');now=2000;assert.equal(m.sample().pose,'Digit2');
});
test('repeated confirmed keys get a small complete-scene recoil, without changing the musical target',()=>{
 let now=0;const m=createGuitarMotion(data,()=>now);m.reset('Digit1');m.pulse();now=12;assert.ok(m.sample().edge);now=90;assert.equal(m.sample().pose,'Digit1');assert.equal(m.target,'Digit1');
});
test('real renderer selects exactly one entire scene tile and a late transition cannot repaint drums',async t=>{
 const {JSDOM}=await import('jsdom');const dom=new JSDOM('<div id="scene" data-instrument="guitar"><div class="stage-readout"></div></div>');const w=dom.window,scene=w.document.querySelector('#scene');t.after(()=>w.close());
 const piano=JSON.parse(await fs.readFile(new URL('../public/character/whole-piano-v3/manifest.json',import.meta.url))),band=JSON.parse(await fs.readFile(new URL('../public/character/instrument-scenes-v1/manifest.json',import.meta.url)));
 let now=0,n=0;const frames=new Map(),draws=[];w.performance.now=()=>now;w.requestAnimationFrame=fn=>{frames.set(++n,fn);return n;};w.cancelAnimationFrame=id=>frames.delete(id);
 let release;const blocked=new Promise(resolve=>release=resolve);let block=false;
 w.createImageBitmap=async blob=>{const id=await blob.text();if(block&&id.endsWith('.webp'))await blocked;return{width:id.endsWith('.webp')?2560:1254,height:id.endsWith('.webp')?1280:1254,id,close(){}};};
 w.HTMLCanvasElement.prototype.getContext=()=>({drawImage(...args){if(args.length===9){assert.equal(args[3],640);assert.equal(args[4],640);assert.equal(args[1]%640,0);assert.equal(args[2]%640,0);assert.equal(args[7],1254);assert.equal(args[8],1254);}else assert.equal(args.length,3);draws.push(args);}});
 t.mock.method(globalThis,'fetch',async input=>{const path=new URL(input).pathname;if(path.endsWith('manifest.json'))return Response.json(path.includes('guitar-motion-v1')?data:path.includes('instrument-scenes-v1')?band:piano);return new Response(path.split('/').at(-1));});
 const c=mountCharacter(scene);t.after(()=>c.destroy());const tick=()=>new Promise(r=>setImmediate(r));const frame=async time=>{now=time;const q=[...frames.values()];frames.clear();for(const f of q)f(now);await tick();};
 await c.ready;await tick();await frame(0);const chord={code:'Digit4',kind:'chord'};c.update('guitar',[chord]);c.strike(chord);await frame(1);await frame(37);await tick();assert.ok(draws.some(a=>a.length===9),'actual full-scene tile was drawn');assert.equal(scene.dataset.wholeFrame,'guitar:transition');
 c.update('guitar',[]);await frame(70);await frame(110);await frame(250);assert.equal(scene.dataset.wholeFrame,'guitar:Digit4','release holds the latest fret instead of inventing a return performance');
 block=true;const note={code:'KeyK',kind:'note'};c.update('guitar',[note]);c.strike(note);await frame(270);await frame(295);c.update('drums',[{code:'KeyX',kind:'drum'}]);c.strike({code:'KeyX',kind:'drum'},'drums');await frame(320);await tick();assert.equal(scene.dataset.wholeFrame,'drums:KeyX');release();await tick();assert.equal(scene.dataset.wholeFrame,'drums:KeyX');assert.equal(scene.querySelectorAll('canvas').length,1);
});
test('cold transition downloads keep original poses usable and enable smoothing only after preparation',async t=>{
 const {JSDOM}=await import('jsdom');const dom=new JSDOM('<div id="scene" data-instrument="guitar"><div class="stage-readout"></div></div>');const w=dom.window,scene=w.document.querySelector('#scene');t.after(()=>w.close());
 const piano=JSON.parse(await fs.readFile(new URL('../public/character/whole-piano-v3/manifest.json',import.meta.url))),band=JSON.parse(await fs.readFile(new URL('../public/character/instrument-scenes-v1/manifest.json',import.meta.url)));
 let now=0,n=0,release;const blocked=new Promise(r=>release=r),queue=new Map();w.performance.now=()=>now;w.requestAnimationFrame=fn=>{queue.set(++n,fn);return n;};w.cancelAnimationFrame=id=>queue.delete(id);
 const draws=[];w.HTMLCanvasElement.prototype.getContext=()=>({drawImage(...args){draws.push(args);}});w.createImageBitmap=async blob=>{const id=await blob.text();return{width:id.endsWith('.webp')?2560:1254,height:id.endsWith('.webp')?1280:1254,close(){}};};
 t.mock.method(globalThis,'fetch',async input=>{const path=new URL(input).pathname;if(path.endsWith('manifest.json'))return Response.json(path.includes('guitar-motion-v1')?data:path.includes('instrument-scenes-v1')?band:piano);if(path.endsWith('.webp'))await blocked;return new Response(path.split('/').at(-1));});
 const c=mountCharacter(scene);t.after(()=>{release();c.destroy();});const tick=()=>new Promise(r=>setImmediate(r));const frame=async time=>{now=time;const q=[...queue.values()];queue.clear();for(const f of q)f(now);await tick();};
 await c.ready;await tick();assert.equal(scene.dataset.guitarMotion,'loading');const chord={code:'Digit4',kind:'chord'};c.update('guitar',[chord]);c.strike(chord);await frame(1);assert.equal(scene.dataset.wholeFrame,'guitar:Digit4','confirmed input remains usable during the download');
 release();await tick();await tick();assert.equal(scene.dataset.guitarMotion,'ready');const next={code:'Digit1',kind:'chord'};c.update('guitar',[next]);c.strike(next);await frame(20);await frame(42);assert.equal(scene.dataset.wholeFrame,'guitar:transition');assert.ok(draws.some(a=>a.length===9));
});
