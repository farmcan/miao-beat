import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {readFile} from 'node:fs/promises';
import {CHARACTER_LAYOUT,contactFor,wristFor,solveArm,mountCharacter} from '../public/character.js';
import {MELODY,DRUMS,CHORDS} from '../public/bindings.js';

const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
test('every actual surface is reachable with fixed bones and the grip places the tip on it',()=>{
 for(const mode of ['piano','marimba','guitar','drums']){
  for(const key of mode==='drums'?DRUMS:[...MELODY,...DRUMS,...(mode==='guitar'?CHORDS:[])]){
   const c=contactFor(key,mode);assert.ok(c.point.every(Number.isFinite));if(c.side==='foot')continue;
   const w=wristFor(c),p=solveArm(c.side,w,mode);
   assert.ok(Math.abs(distance(p.shoulder,p.elbow)-CHARACTER_LAYOUT.upperLength)<1e-8);
   assert.ok(Math.abs(distance(p.elbow,p.wrist)-CHARACTER_LAYOUT.foreLength)<1e-8);
   const theta=(c.angle??0)*Math.PI/180,L=c.toolLength??(c.stick?CHARACTER_LAYOUT.stickLength:CHARACTER_LAYOUT.pawLength);
   assert.ok(distance([w[0]-Math.sin(theta)*L,w[1]+Math.cos(theta)*L],c.point)<1e-8);
   if(c.fret)assert.doesNotThrow(()=>solveArm('right',wristFor({point:c.fret,angle:-55}),mode));
  }
 }
 assert.equal(new Set(MELODY.map(k=>contactFor(k,'piano').point.join(','))).size,13);
 assert.deepEqual(contactFor(DRUMS[2],'drums').point,contactFor(DRUMS[3],'drums').point);
 assert.equal(new Set(DRUMS.map(k=>contactFor(k,'drums').point.join(','))).size,7);
 assert.throws(()=>solveArm('left',[2000,2000]),RangeError,'an impossible target is rejected, not stretched or silently clamped');
});

test('retrigger starts at the current pose, sticks share their wrist, and blur/mode clear movement',async t=>{
 const dom=new JSDOM(await readFile(new URL('../public/index.html',import.meta.url),'utf8'),{pretendToBeVisual:true});t.after(()=>dom.window.close());
 const w=dom.window,scene=w.document.getElementById('scene');let time=0,id=0;const frames=new Map();
 w.performance.now=()=>time;w.requestAnimationFrame=fn=>{frames.set(++id,fn);return id;};w.cancelAnimationFrame=i=>frames.delete(i);
 const frame=ms=>{time=ms;const q=[...frames.values()];frames.clear();for(const fn of q)fn(time);};
 w.Image=class{naturalWidth=1254;naturalHeight=1254;set src(value){queueMicrotask(()=>this.onload());}};
 const c=mountCharacter(scene);w.document.querySelector('link[href$="rig.css"]').dispatchEvent(new w.Event('load'));await c.ready;
 assert.equal(scene.dataset.character,'orange-articulated-v3');c.update('guitar',[]);c.strike(CHORDS[0],'guitar');frame(34);
 const hand=scene.querySelector('[data-joint=leftWrist]'),before=hand.style.transform;
 c.strike(CHORDS[1],'guitar');frame(34);assert.equal(hand.style.transform,before,'same-time retrigger must not snap back to a reset pose');
 c.strike(DRUMS[1],'guitar');frame(34);assert.equal(hand.style.transform,before,'the other hand must not reset the current stroke');
 frame(100);assert.notEqual(hand.style.transform,before);
 c.update('drums',[]);frame(110);c.strike(DRUMS[3],'drums');frame(180);
 assert.equal(scene.dataset.contactSurface,'open-hat');
 for(const side of ['left','right'])assert.equal(scene.querySelector(`[data-joint=${side}Wrist] .orange-stick`).parentElement.dataset.joint,side+'Wrist');
 assert.equal(scene.dataset.characterWarning,undefined);
 const moving=hand.style.transform;w.dispatchEvent(new w.Event('blur'));const resting=hand.style.transform;assert.notEqual(resting,moving);frame(400);assert.equal(hand.style.transform,resting);
 c.update('piano',[MELODY[0]]);c.strike(MELODY[0],'piano');frame(470);c.update('piano',[]);frame(780);assert.equal(hand.dataset.wrist,'236.00,386.00','releasing the last key returns the wrist instead of leaving it pressed');
 c.destroy();assert.equal(scene.querySelectorAll('[data-character-part]').length,0);assert.equal(scene.querySelectorAll('[data-character-props]').length,0);assert.equal(frames.size,0);
});
