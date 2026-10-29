// DOM scheduling and module-boundary checks. GPU rendering and network behavior
// still need a real browser; all audio/3D objects here are controllable doubles.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {JSDOM} from 'jsdom';
import {MELODY,CHORDS} from '../public/bindings.js';
import {createCompareMotion} from '../public/labs/character-compare/motion-controller.js';

const html=await readFile(new URL('../public/labs/character-compare/index.html',import.meta.url),'utf8');
const source=await readFile(new URL('../public/labs/character-compare/play.js',import.meta.url),'utf8');
const script=source.replace(/^import .*;\n/gm,'').replace("import('./three-renderer.js')",'window.__loadThree()');
const settle=async()=>{for(let i=0;i<12;i++)await Promise.resolve();};
function deferred(){let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});return{promise,resolve,reject};}

function setup(t){
  const dom=new JSDOM(html,{runScripts:'outside-only',pretendToBeVisual:true,url:'https://miao-beat.pages.dev/labs/character-compare/'}),w=dom.window;
  let time=0,audio,imports=0,next=1,moduleFailure=false,audioPending=null;
  const frames=new Map(),timers=new Map(),models=[],original={ready:Promise.resolve(true),strikes:[],updates:[],resets:0,destroys:0,strike(key){this.strikes.push(key);},update(mode,keys){this.updates.push(keys);},reset(){this.resets++;},destroy(){this.destroys++;}};
  class FakeAudio{
    constructor(){audio=this;this.context={state:'running',currentTime:0};this.plays=[];this.stops=0;}
    async ready(){if(audioPending)await audioPending.promise;this.context.state='running';}
    play(key){this.plays.push(key);}
    stopVoices(){this.stops++;}
    getLoadProgress(){return{loaded:0,total:8};}
  }
  Object.defineProperty(w.performance,'now',{value:()=>time});
  w.requestAnimationFrame=fn=>{const id=next++;frames.set(id,fn);return id;};
  w.setTimeout=(fn,gap)=>{const id=next++;timers.set(id,{fn,at:time+gap});return id;};
  w.clearTimeout=id=>timers.delete(id);
  w.__loadThree=async()=>{
    imports++;if(moduleFailure)throw Error('offline');
    return{createThreeCharacter(){
      const load=deferred(),model={load,ready:load.promise,poses:[],views:[],orbits:[],renders:0,destroys:0,setPose(p){this.poses.push([...p]);},setView(v){this.views.push(v);},setOrbit(v){this.orbits.push(v);},render(){this.renders++;},destroy(){this.destroys++;}};
      models.push(model);return model;
    }};
  };
  w.__deps={SampledAudio:FakeAudio,MELODY,CHORDS,createCompareMotion,mountCharacter:()=>original};
  w.eval('const {SampledAudio,MELODY,CHORDS,createCompareMotion,mountCharacter}=window.__deps;\n'+script);
  const $=id=>w.document.getElementById(id);
  const key=(type,code,options={})=>w.document.dispatchEvent(new w.KeyboardEvent(type,{code,bubbles:true,cancelable:true,...options}));
  function frame(ms){time=ms;audio.context.currentTime=ms/1000;const batch=[...frames.values()];frames.clear();for(const fn of batch)fn(ms);}
  function advance(ms){const until=time+ms;while(true){const due=[...timers].filter(([,v])=>v.at<=until).sort((a,b)=>a[1].at-b[1].at)[0];if(!due)break;time=due[1].at;timers.delete(due[0]);due[1].fn();}frame(until);}
  t.after(()=>{w.dispatchEvent(new w.Event('pagehide'));dom.window.close();});
  return{w,$,audio,original,models,key,frame,advance,timers,imports:()=>imports,setModuleFailure(value){moduleFailure=value;},deferAudio(){audioPending=deferred();return()=>{audioPending.resolve();audioPending=null;};}};
}

test('entrypoint has two lanes and no eager 3D runtime, GLB, preload or Godot path',()=>{
  assert.doesNotMatch(html,/godot|iframe|\.glb|three-runtime|modulepreload|rel=["']preload/i);
  assert.doesNotMatch(source,/godot|setInterval|^import .*three-renderer/gmi);
  assert.match(source,/await import\('\.\/three-renderer\.js'\)/);
  assert.equal((html.match(/<article data-lane=/g)||[]).length,2);
});

test('background startup does not replace the first-use hint with a stopped message',async t=>{
  const h=setup(t),initial=h.$('status').textContent;
  h.w.dispatchEvent(new h.w.Event('blur'));assert.equal(h.$('status').textContent,initial);
  h.$('enableAudio').click();await settle();const ready=h.$('status').textContent;
  h.w.dispatchEvent(new h.w.Event('blur'));assert.equal(h.$('status').textContent,ready);
  h.key('keydown','KeyA');h.key('keyup','KeyA');h.w.dispatchEvent(new h.w.Event('blur'));
  assert.match(h.$('status').textContent,/演奏已停止/);assert.equal(h.audio.plays.length,1);
});

test('original accepts 8 notes and 4 chords without loading 3D; view and solo controls remain free',async t=>{
  const h=setup(t);h.$('enableAudio').click();await settle();
  assert.equal(h.$('notes').children.length,8);assert.equal(h.$('chords').children.length,4);
  for(const key of [...MELODY.filter(k=>!k.black),...CHORDS]){h.key('keydown',key.code);h.key('keyup',key.code);}
  assert.equal(h.audio.plays.length,12);assert.equal(h.original.strikes.length,12);assert.equal(h.imports(),0);
  h.w.document.querySelector('[data-view="face"]').click();h.w.document.querySelector('[data-solo="three"]').click();
  assert.equal(h.w.document.querySelector('[data-lane="original"]').hidden,true);
  h.$('showAll').click();assert.equal(h.w.document.querySelector('[data-lane="original"]').hidden,false);
  assert.equal(h.imports(),0);assert.match(h.$('status').textContent,/3D尚未就绪/);
});

test('load is deduplicated, syncs the current pose/view/orbit after download and never replays old notes',async t=>{
  const h=setup(t);h.$('enableAudio').click();await settle();h.$('loadThree').click();await settle();
  h.$('loadThree').dispatchEvent(new h.w.Event('click'));await settle();assert.equal(h.imports(),1);
  assert.equal(h.$('threeScene').hidden,true);assert.equal(h.$('threeScene').dataset.loadState,'loading');
  h.key('keydown','KeyK');h.key('keyup','KeyK');h.frame(60);
  assert.equal(h.original.strikes.length,1);assert.equal(h.models[0].poses.length,0);
  h.w.document.querySelector('[data-view="face"]').click();h.$('orbit').value='24';h.$('orbit').dispatchEvent(new h.w.Event('input'));
  h.frame(10000);h.models[0].load.resolve(true);await settle();
  const model=h.models[0];assert.equal(h.$('threeScene').dataset.loadState,'ready');assert.equal(h.$('threeScene').hidden,false);
  assert.equal(model.views.at(-1),'face');assert.equal(model.orbits.at(-1),24);
  assert.equal(model.poses[0][0],0);assert.equal(model.poses[0][4],0,'completed stroke is not queued for download completion');
  assert.equal(h.audio.plays.length,1);assert.equal(h.original.strikes.length,1);
  h.$('stop').click();assert.deepEqual(model.poses.at(-1),[0,0,0,0,0]);
});

test('module and model failures offer retry without claiming ready or stopping original input',async t=>{
  const h=setup(t);h.setModuleFailure(true);h.$('loadThree').click();await settle();
  assert.equal(h.$('threeScene').dataset.loadState,'failed');assert.equal(h.$('loadThree').disabled,false);assert.equal(h.$('threePlaceholder').hidden,false);
  assert.equal(h.$('threeScene').dataset.ready,undefined);
  h.setModuleFailure(false);h.$('loadThree').click();await settle();h.models[0].load.resolve(false);await settle();
  assert.equal(h.models[0].destroys,1);assert.equal(h.$('threeScene').dataset.loadState,'failed');
  h.$('enableAudio').click();await settle();h.key('keydown','KeyA');h.key('keyup','KeyA');assert.equal(h.audio.plays.length,1);
  h.$('loadThree').click();await settle();h.models[1].load.resolve(true);await settle();assert.equal(h.$('threeScene').dataset.loadState,'ready');assert.equal(h.imports(),3);
});

for(const [button,gap]of [['slowDemo',500],['fastDemo',150]])test(`${gap}ms demo stops scheduled input and resets held keys`,async t=>{
  const h=setup(t);h.$(button).click();await settle();h.advance(0);assert.equal(h.audio.plays.length,1);
  h.advance(gap-1);assert.equal(h.audio.plays.length,1);h.advance(1);assert.equal(h.audio.plays.length,2);
  h.key('keydown','Digit1');assert.equal(h.audio.plays.length,3);h.$('stop').click();h.advance(10000);
  assert.equal(h.audio.plays.length,3);assert.equal(h.timers.size,0);assert.equal(h.w.document.querySelectorAll('.pressed').length,0);
  const pose=h.w.document.body.dataset.pose.split(',').map(Number);assert.deepEqual([pose[0],pose[1],pose[2],pose[4]],[0,0,0,0]);assert.equal(h.imports(),0);
});

test('first key while audio loads is explicitly silent; stop cancels an awaiting demo with no later notes',async t=>{
  const h=setup(t),release=h.deferAudio();h.key('keydown','KeyA');h.key('keyup','KeyA');
  assert.equal(h.audio.plays.length,0);assert.equal(h.original.strikes.length,0);assert.match(h.$('status').textContent,/这次按键未发声/);
  h.$('fastDemo').click();await settle();h.$('stop').click();release();await settle();h.advance(10000);
  assert.equal(h.audio.plays.length,0);assert.equal(h.timers.size,0);
  h.key('keydown','KeyS');h.key('keyup','KeyS');assert.equal(h.audio.plays.length,1);
});

test('head toggle and stopping during 3D download apply to completion; pagehide cannot resurrect a renderer',async t=>{
  const h=setup(t);h.$('enableAudio').click();await settle();h.$('loadThree').click();await settle();
  h.key('keydown','KeyD');h.key('keyup','KeyD');h.frame(60);h.$('headMotion').checked=false;h.$('stop').click();h.frame(70);
  h.models[0].load.resolve(true);await settle();assert.deepEqual(h.models[0].poses.at(-1),[0,0,0,0,0]);
  h.key('keydown','KeyK');h.key('keyup','KeyK');h.frame(120);assert.equal(h.models[0].poses.at(-1)[3],0);
  h.w.dispatchEvent(new h.w.Event('blur'));assert.deepEqual(h.models[0].poses.at(-1),[0,0,0,0,0]);
  const later=setup(t);later.$('loadThree').click();await settle();later.w.dispatchEvent(new later.w.Event('pagehide'));
  later.models[0].load.resolve(true);await settle();assert.equal(later.models[0].destroys,1);assert.equal(later.$('threeScene').hidden,true);
});

test('a live key also cancels a demo waiting for audio, without queuing that key',async t=>{
  const h=setup(t),release=h.deferAudio();h.$('slowDemo').click();await settle();h.key('keydown','KeyA');h.key('keyup','KeyA');
  release();await settle();h.advance(10000);assert.equal(h.audio.plays.length,0);assert.equal(h.timers.size,0);
});
