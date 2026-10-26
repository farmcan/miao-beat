import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {createGuitarMotion,validateGuitarMotionManifest,validateGuitarPluckManifest,GUITAR_PLUCK_IDS} from '../public/guitar-motion.js';
import {mountCharacter} from '../public/full-frame-character.js';
const read=async path=>JSON.parse(await fs.readFile(new URL('../public/'+path,import.meta.url)));
const legacy=await read('character/guitar-motion-v1/manifest.json'),data=await read('character/guitar-pluck-v1/manifest.json');
test('historical public strips retain their reviewed manifest; active plucks cover every actual note/chord',()=>{
 validateGuitarMotionManifest(legacy);validateGuitarPluckManifest(data);assert.equal(GUITAR_PLUCK_IDS.length,17);
 const broken=structuredClone(data);broken.clips.KeyA.up.file='../arm.png';assert.throws(()=>validateGuitarPluckManifest(broken));
});
test('one strike goes through a visible right-paw contact and recovers while retaining its fret',()=>{
 let now=0;const m=createGuitarMotion(data,()=>now);m.strike('KeyK');assert.equal(m.sample().pose,'down');now=16;assert.equal(m.sample().pose,'down');now=32;assert.equal(m.sample().pose,'down');now=48;assert.equal(m.sample().pose,'down');now=90;assert.equal(m.sample().phase,'return');now=170;assert.equal(m.sample().pose,'up');assert.equal(m.sample().code,'KeyK');now=10000;assert.equal(m.sample().needsFrame,false);assert.equal(m.sample().serial,1);
});
test('same-note repetitions and changed notes each get their own full contact, without visiting other frets',()=>{
 let now=0;const m=createGuitarMotion(data,()=>now);let serial=0;
 for(const code of ['KeyA','KeyA','KeyA',...GUITAR_PLUCK_IDS]){assert.equal(m.strike(code),true);const start=now;now+=40;assert.equal(m.sample().pose,'down');assert.equal(m.sample().code,code);assert.equal(m.sample().serial,++serial);now=start+180;assert.equal(m.sample().pose,'up');assert.equal(m.sample().code,code);}
 assert.equal(m.strike('KeyZ'),false);
});
test('a new confirmation interrupts an old recovery and reset cancels all remaining movement',()=>{
 let now=0;const m=createGuitarMotion(data,()=>now);m.strike('KeyA');now=80;m.strike('KeyK');assert.equal(m.sample().code,'KeyK');now=120;assert.equal(m.sample().pose,'down');now=1000;assert.equal(m.sample().code,'KeyK');m.reset();assert.equal(m.sample().pose,'up');assert.equal(m.sample().needsFrame,false);
});
async function harness(t,{cold=false,blockDecode}={}){
 const {JSDOM}=await import('jsdom');const dom=new JSDOM('<div id="scene" data-instrument="guitar"><div class="stage-readout"></div></div>');const w=dom.window,scene=w.document.querySelector('#scene');t.after(()=>w.close());
 const piano=await read('character/whole-piano-v3/manifest.json'),band=await read('character/instrument-scenes-v1/manifest.json');let now=0,n=0,release;const blocked=new Promise(r=>release=r),queue=new Map(),draws=[];
 w.performance.now=()=>now;w.requestAnimationFrame=fn=>{queue.set(++n,fn);return n;};w.cancelAnimationFrame=id=>queue.delete(id);
 w.HTMLCanvasElement.prototype.getContext=()=>({drawImage(...args){if(args.length===9){assert.equal(args[3],640);assert.equal(args[4],640);assert.equal(args[1]%640,0);assert.equal(args[2]%640,0);assert.equal(args[7],1254);assert.equal(args[8],1254);}else assert.equal(args.length,3);draws.push(args);}});
 w.createImageBitmap=async blob=>{const id=await blob.text();if(blockDecode&&id===blockDecode+'.webp')await blocked;return{width:id.endsWith('.webp')?2560:1254,height:id.endsWith('.webp')?1280:1254,id,close(){}};};
 t.mock.method(globalThis,'fetch',async input=>{const path=new URL(input).pathname;if(path.endsWith('manifest.json'))return Response.json(path.includes('guitar-pluck-v1')?data:path.includes('instrument-scenes-v1')?band:piano);if(cold&&path.endsWith('.webp'))await blocked;return new Response(path.split('/').at(-1));});
 const c=mountCharacter(scene);t.after(()=>{release();c.destroy();});const tick=()=>new Promise(r=>setImmediate(r));const frame=async time=>{now=time;const q=[...queue.values()];queue.clear();for(const f of q)f(now);await tick();};const prepared=async()=>{for(let i=0;i<30&&scene.dataset.guitarMotion!=='ready';i++)await tick();assert.equal(scene.dataset.guitarMotion,'ready');};await c.ready;await tick();if(!cold)await prepared();return{c,scene,draws,frame,tick,release,prepared};
}
test('actual renderer paints a contact for every repeated/changed input, then rests with no extra hits',async t=>{
 const h=await harness(t);let time=0;await h.frame(time);
 for(const code of ['KeyA','KeyA','KeyS','KeyK']){
  const key={code,kind:'note'};h.c.update('guitar',[key]);h.c.strike(key);for(let i=0;i<12;i++)await h.frame(time+=16);h.c.update('guitar',[]);await h.frame(time+=16);assert.equal(h.scene.dataset.wholeFrame,'guitar-up:'+code);
 }
 assert.equal(h.scene.dataset.guitarStrikeCount,'4');assert.equal(h.scene.dataset.guitarContactCount,'4','count only contacts actually drawn, not planned frames');assert.ok(h.draws.some(a=>a.length===9));for(let i=0;i<12;i++)await h.frame(time+=16);assert.equal(h.scene.dataset.guitarContactCount,'4');assert.equal(h.scene.querySelectorAll('canvas').length,1);
});
test('late pluck frames cannot paint over a newly selected drum instrument',async t=>{
 const h=await harness(t,{blockDecode:'KeyK'});await h.frame(0);const note={code:'KeyK',kind:'note'};h.c.update('guitar',[note]);h.c.strike(note);await h.frame(16);await h.frame(32);h.c.update('drums',[{code:'KeyX',kind:'drum'}]);h.c.strike({code:'KeyX',kind:'drum'},'drums');await h.frame(48);await h.tick();assert.equal(h.scene.dataset.wholeFrame,'drums:KeyX');h.release();await h.tick();assert.equal(h.scene.dataset.wholeFrame,'drums:KeyX');
});
test('cold preparation leaves original poses usable and never replays an old pre-load input',async t=>{
 const h=await harness(t,{cold:true});assert.equal(h.scene.dataset.guitarMotion,'loading');const chord={code:'Digit4',kind:'chord'};h.c.update('guitar',[chord]);h.c.strike(chord);await h.frame(1);assert.equal(h.scene.dataset.wholeFrame,'guitar:Digit4');h.release();await h.prepared();assert.equal(h.scene.dataset.guitarStrikeCount,'0');const key={code:'KeyS',kind:'note'};h.c.update('guitar',[key]);h.c.strike(key);for(let time=17;time<210;time+=16)await h.frame(time);assert.equal(h.scene.dataset.guitarContactCount,'1');assert.equal(h.scene.dataset.wholeFrame,'guitar-up:KeyS');
});
