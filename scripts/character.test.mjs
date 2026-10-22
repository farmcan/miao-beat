import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {readFile} from 'node:fs/promises';
import {CHARACTER_LAYOUT,contactFor,pawTransform,mountCharacter} from '../public/character.js';
import {MELODY,DRUMS,CHORDS} from '../public/bindings.js';

test('all surfaces use matching instrument geometry and transforms preserve shoulder and toe',()=>{
 for(const instrument of ['piano','marimba','guitar','drums']){
  const keys=instrument==='drums'?DRUMS:instrument==='guitar'?[...MELODY,...DRUMS,...CHORDS]:[...MELODY,...DRUMS];
  for(const key of keys){const c=contactFor(key,instrument);assert.ok(c.point.every(Number.isFinite));if(c.side==='foot')continue;
   const spec=CHARACTER_LAYOUT[c.side==='left'?'leftPaw':'rightPaw'],m=pawTransform(c.side,c.point).slice(7,-1).split(',').map(Number);
   const project=([x,y])=>[m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]];
   for(const [actual,expected] of [[project(spec.root),spec.shoulder],[project(spec.tip),c.point]])actual.forEach((v,i)=>assert.ok(Math.abs(v-expected[i])<1e-8));
   if(instrument==='guitar'&&key.kind!=='drum'){assert.equal(c.surface,'strings');assert.equal(c.side,'left');assert.ok(c.fret);}
  }
 }
 assert.deepEqual(contactFor(DRUMS[2],'drums').point,contactFor(DRUMS[3],'drums').point);
 assert.equal(contactFor(DRUMS[0],'drums').side,'foot');
 assert.equal(new Set(DRUMS.map(k=>contactFor(k,'drums').point.join(','))).size,7);
 assert.equal(new Set(MELODY.map(k=>contactFor(k,'piano').point.join(','))).size,13);
});

test('contact starts immediately, retrigger cancels one hand, mode and blur clear animations',async t=>{
 const dom=new JSDOM(await readFile(new URL('../public/index.html',import.meta.url),'utf8'),{pretendToBeVisual:true});t.after(()=>dom.window.close());
 const w=dom.window,scene=w.document.getElementById('scene'),created=[];
 w.Image=class{naturalWidth=1254;naturalHeight=1254;set src(value){queueMicrotask(()=>this.onload());}};
 w.SVGElement.prototype.animate=function(frames,options){const a={node:this,frames,options,cancelled:false,cancel(){this.cancelled=true;}};created.push(a);return a;};
 const c=mountCharacter(scene);w.document.querySelector('link[href$="rig.css"]').dispatchEvent(new w.Event('load'));await c.ready;
 assert.equal(scene.dataset.character,'indie-atlas-v2');c.update('piano',[]);
 c.strike(MELODY[0],'piano');const first=created.at(-1);assert.equal(first.frames[0].transform,pawTransform('left',[194,264]));assert.equal(first.options.fill,'none');
 c.strike(MELODY[6],'piano');const right=created.at(-1);assert.equal(first.cancelled,false);
 c.strike(MELODY[1],'piano');assert.equal(first.cancelled,true);assert.equal(right.cancelled,false);
 c.update('drums',[]);assert.equal(right.cancelled,true);c.strike(DRUMS[3],'drums');assert.equal(scene.dataset.contactSurface,'open-hat');
 const stick=scene.querySelector('[data-stick=left]');assert.equal(stick.style.transform,'translate(253px,201px)','demo keeps the stick rest endpoint under its contact animation');c.update('drums',[DRUMS[3]]);c.update('drums',[]);assert.equal(stick.style.transform,'translate(253px,201px)','early release restores both paw and stick base poses');
 const last=created.at(-1);w.dispatchEvent(new w.Event('blur'));assert.equal(last.cancelled,true);
 c.destroy();assert.equal(scene.querySelectorAll('[data-character-part]').length,0);assert.equal(scene.querySelectorAll('[data-character-props]').length,0);
});
