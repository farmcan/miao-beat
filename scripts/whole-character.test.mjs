import test from 'node:test';
import assert from 'node:assert/strict';
import {createPoseState} from '../public/whole-character.js';
import {mountCharacter} from '../public/whole-character.js';
import {JSDOM} from 'jsdom';

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

async function wholeHarness(t,{fail=false}={}){
  const dom=new JSDOM('<div id="scene"><svg class="cat-scene"></svg><div class="stage-readout"></div></div>',{pretendToBeVisual:true});
  const w=dom.window,scene=w.document.getElementById('scene'),draws=[],frames=new Map();let id=0;
  w.requestAnimationFrame=fn=>{frames.set(++id,fn);return id;};w.cancelAnimationFrame=id=>frames.delete(id);
  w.HTMLCanvasElement.prototype.getContext=()=>({clearRect(){},drawImage(...args){draws.push(args);}});
  w.Image=class{naturalWidth=1672;naturalHeight=941;set src(value){this.url=value;queueMicrotask(()=>this.onload?.());}};
  w.fetch=async()=>{if(fail)throw Error('image unavailable');return Response.json({...config,version:1,width:480,height:412,columns:4,frameCount:13,atlas:'keyboard-poses-v1.jpg'});};
  const controller=mountCharacter(scene);scene.ownerDocument.head.querySelector('link').onload();await controller.ready;
  const flush=async()=>{for(let n=0;n<5;n++)await Promise.resolve();const pending=[...frames.values()];frames.clear();for(const fn of pending)fn();};
  t.after(()=>{controller.destroy();w.close();});await flush();return {scene,controller,draws,flush};
}

test('all instrument modes use complete frames and static modes never synthesize a limb action',async t=>{
  const h=await wholeHarness(t);assert.equal(h.scene.dataset.character,'whole-cat-poses-v1');
  assert.equal(h.scene.querySelector('.cat-scene').style.display,'none');
  for(const [mode,suffix]of [['guitar','guitar-whole-still-v1.jpg'],['drums','drums-whole-still-v1.jpg'],['marimba','keyboard-poses-v1.jpg']]){
    h.controller.update(mode,[]);await h.flush();
    assert.equal(h.scene.dataset.character,'whole-cat-still-v1');assert.equal(h.scene.dataset.motionPhase,'static');
    assert.ok(h.draws.at(-1)[0].url.endsWith(suffix));assert.match(h.scene.querySelector('.whole-motion-note').textContent,/动作待补/);
    const drawn=h.draws.length;h.controller.strike(mode==='drums'?{kind:'drum',code:'KeyZ'}:low,mode);await h.flush();assert.equal(h.draws.length,drawn,'still stays whole and static on input');
  }
  h.controller.update('piano',[low]);h.controller.strike(low,'piano');await h.flush();assert.equal(h.scene.dataset.motionPose,'leftLow');
});

test('resource failure shows text and never activates a legacy vector or component rig',async t=>{
  const h=await wholeHarness(t,{fail:true});
  assert.equal(h.scene.dataset.character,'whole-image-unavailable');assert.equal(h.scene.querySelector('canvas').hidden,true);
  assert.equal(h.scene.querySelector('.cat-scene').style.display,'none');assert.match(h.scene.querySelector('.whole-motion-note').textContent,/声音仍可用/);
  h.controller.update('guitar',[]);h.controller.strike(low,'guitar');await h.flush();assert.equal(h.draws.length,0);
});
