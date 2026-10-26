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
 let now=0;const m=createGuitarMotion(data,()=>now);m.go('Digit4');now=35;const p=m.sample();assert.equal(p.edge,'e03');assert.ok(p.cell>=0&&p.cell<7);now=80;assert.equal(m.sample().pose,'Digit4');m.go('idle');now=120;assert.ok(m.sample().edge);now=300;assert.deepEqual(m.sample(),{pose:'idle',needsFrame:false});
});
test('a new target interrupts the current interpolation continuously and drops stale actions',()=>{
 let now=0;const m=createGuitarMotion(data,()=>now);m.go('KeyK');now=31;const p=m.sample();m.go('Digit2');assert.deepEqual(m.sample(),p,'same-time interruption retains the actual in-between picture');now=400;assert.equal(m.sample().pose,'Digit2');now=700;assert.equal(m.sample().pose,'Digit2');m.reset();assert.equal(m.sample().pose,'idle');
});
test('repeated confirmed keys get a small complete-scene recoil, without changing the musical target',()=>{
 let now=0;const m=createGuitarMotion(data,()=>now);m.reset('Digit1');m.pulse();now=12;assert.ok(m.sample().edge);now=80;assert.equal(m.sample().pose,'Digit1');assert.equal(m.target,'Digit1');
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
 block=true;const note={code:'KeyK',kind:'note'};c.update('guitar',[note]);c.strike(note);await frame(45);await frame(71);c.update('drums',[{code:'KeyX',kind:'drum'}]);c.strike({code:'KeyX',kind:'drum'},'drums');await frame(80);await tick();assert.equal(scene.dataset.wholeFrame,'drums:KeyX');release();await tick();assert.equal(scene.dataset.wholeFrame,'drums:KeyX');assert.equal(scene.querySelectorAll('canvas').length,1);
});
