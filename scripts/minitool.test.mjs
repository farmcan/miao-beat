// Controlled app/bridge regressions; not native-container or physical-device proof.
import test from 'node:test';import assert from 'node:assert/strict';import {readFile}from'node:fs/promises';import {JSDOM}from'jsdom';import {SONGS}from'../public/scores.js';import {MELODY}from'../public/bindings.js';import * as recording from'../public/recording.js';
const html=await readFile(new URL('../minitool/index.html',import.meta.url),'utf8'),app=await readFile(new URL('../minitool/app.js',import.meta.url),'utf8'),bridge=await readFile(new URL('../minitool/bridge.js',import.meta.url),'utf8');
const settle=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
function setup(t,{load=async()=>null,save=async()=>{},post=async()=>{}}={}){
 const w=new JSDOM(html,{runScripts:'outside-only',pretendToBeVisual:true,url:'https://miniapp-sandbox.xiaohongshu.com/app/test/index.html'}).window,$=id=>w.document.getElementById(id),frames=new Map();let id=0,audio;const writes=[];
 w.requestAnimationFrame=fn=>{frames.set(++id,fn);return id;};w.cancelAnimationFrame=id=>frames.delete(id);
 w.MIAO_BEAT_DATA={keys:MELODY.filter(k=>!k.black).map(k=>({code:k.code,note:k.sub,number:k.label,kind:'note'})),songs:SONGS.filter(s=>['twinkle','ode-to-joy'].includes(s.id))};w.MiaoBeatRecording=recording;
 class FakeAudio{constructor(){audio=this;this.context={currentTime:0,state:'running'};this.plays=[];}async ready(){return this.context;}play(k,when){this.plays.push({code:k.code,when});}stopVoices(){}setVolume(){}}
 w.MiaoBeatPianoAudio=FakeAudio;w.MiaoBeatBridge={init:async()=>{},load,put:async value=>writes.push(JSON.parse(value)),capabilities:()=>({save:true,post:true}),save,post};
 Object.defineProperties(w.HTMLImageElement.prototype,{complete:{get:()=>true},naturalWidth:{get:()=>480}});w.HTMLElement.prototype.scrollIntoView=()=>{};
 const context=new Proxy({},{get:(o,k)=>o[k]||(o[k]=()=>{})});w.HTMLCanvasElement.prototype.getContext=()=>context;w.HTMLCanvasElement.prototype.toDataURL=()=> 'data:image/png;base64,aQ==';
 w.eval(app);t.after(()=>w.close());return{w,$,audio,writes,advance(time){audio.context.currentTime=time;const f=[...frames.values()];frames.clear();for(const fn of f)fn();}};
}
async function prepare(h){await settle();h.$('prepare').click();await settle();}
async function take(h,codes,duration){h.$('record').click();for(const code of codes)h.$(code).click();h.advance(h.audio.context.currentTime+duration);h.$('stop').click();await settle();}
test('only human keys enter a take; score pages and demo never do',async t=>{
 const h=setup(t);await prepare(h);h.$('record').click();h.$('next').click();h.$('prev').click();h.$('KeyA').click();h.advance(.2);h.$('KeyS').click();h.advance(.5);h.$('stop').click();await settle();assert.deepEqual(h.writes.at(-1).take.events,[[0,0],[200,1]]);
 const count=h.writes.length;h.$('listen').click();h.advance(.6);h.advance(1.225);assert.equal(h.writes.length,count);assert.ok(h.audio.plays.length>2);
});
test('restoring previous take invalidates the previous picture and native actions',async t=>{
 const h=setup(t);await prepare(h);await take(h,['KeyK'],.3);await take(h,['KeyA','KeyS'],.2);h.$('makeCard').click();assert.equal(h.$('cardPanel').hidden,false);assert.equal(h.$('saveCard').disabled,false);h.$('restore').click();await settle();assert.deepEqual(h.writes.at(-1).take.events.map(e=>e[1]),[7]);assert.equal(h.$('cardPanel').hidden,true);assert.equal(h.$('cardImage').hasAttribute('src'),false);assert.equal(h.$('saveCard').disabled,true);assert.equal(h.$('postCard').disabled,true);h.$('makeCard').click();assert.equal(h.$('cardPanel').hidden,false);
});
test('empty recording preserves the prior take; hiding finishes human input and stops playback',async t=>{
 const h=setup(t);await prepare(h);await take(h,['KeyA'],.2);h.$('record').click();h.advance(.3);h.$('stop').click();h.$('replay').click();h.advance(.4);assert.equal(h.audio.plays.at(-1).code,'KeyA');h.$('stop').click();h.$('record').click();h.$('KeyS').click();h.advance(.6);h.w.dispatchEvent(new h.w.Event('blur'));await settle();assert.deepEqual(h.writes.at(-1).take.events.map(e=>e[1]),[1]);assert.equal(h.$('record').getAttribute('aria-pressed'),'false');assert.equal(h.$('KeyA').disabled,true);
});
test('failed authoritative read does not overwrite unknown old drafts, native cancel preserves card',async t=>{
 const h=setup(t,{load:async()=>{throw Error('unknown');},save:async()=>{throw {errMsg:'save:fail cancel'};}});await prepare(h);await take(h,['KeyA'],.2);assert.equal(h.writes.length,0);h.$('makeCard').click();h.$('saveCard').click();await settle();assert.match(h.$('cardStatus').textContent,/已取消/);assert.equal(h.$('cardPanel').hidden,false);assert.equal(h.$('replay').disabled,false);
});
test('strict native storage acknowledgement and version gating are applied without silent browser fallback',async t=>{
 const w=new JSDOM('<body>',{runScripts:'outside-only',url:'https://miniapp-sandbox.xiaohongshu.com/test'}).window;t.after(()=>w.close());let writes=0;w.xhs={launchOptions:{miniToolEnv:{buildVersion:9460000}},miniTool:{getStorage:async()=>({errMsg:'getStorage:ok',data:null}),setStorage:async()=>{writes++;return{};},saveImageToPhotosAlbum:async()=>({errMsg:'saveImageToPhotosAlbum:ok'})}};w.eval(bridge);await w.MiaoBeatBridge.init();assert.equal(await w.MiaoBeatBridge.load(),null);await assert.rejects(w.MiaoBeatBridge.put('x'));assert.equal(writes,1);assert.equal(w.localStorage.length,0);assert.equal(w.MiaoBeatBridge.capabilities().save,true);
});


test('changing score while recording preserves the clock and 60 second stop; page turns stop an old demo',async t=>{
 const h=setup(t);await prepare(h);h.$('record').click();h.$('KeyA').click();h.$('song').value='ode-to-joy';h.$('song').dispatchEvent(new h.w.Event('change'));h.advance(60.01);await settle();assert.equal(h.$('record').getAttribute('aria-pressed'),'false');assert.equal(h.writes.at(-1).take.duration,60000);assert.equal(h.writes.at(-1).take.events.length,1);
 h.$('listen').click();assert.equal(h.$('replay').disabled,true);h.$('next').click();assert.equal(h.$('replay').disabled,false);assert.match(h.$('takeStatus').textContent,/停止上一页/);
});


test('a foreground stall cancels expired playback instead of bursting old notes at the current time',async t=>{
 const h=setup(t);await prepare(h);h.$('listen').click();h.advance(.1);assert.equal(h.audio.plays.length,1);h.advance(4);assert.equal(h.audio.plays.length,1);assert.match(h.$('takeStatus').textContent,/卡顿/);assert.equal(h.$('stop').disabled,true);assert.equal(h.writes.length,0);
});


test('free play during a delayed draft read does not discard the old take before the next recording',async t=>{
 let complete;const old={...recording.makeRecording('piano',96,4),duration:300,events:[[0,7]]};const h=setup(t,{load:()=>new Promise(resolve=>{complete=resolve;})});await settle();h.$('prepare').click();await settle();h.$('KeyA').click();assert.equal(h.$('record').disabled,true);complete(JSON.stringify({version:1,take:old,previous:null}));await settle();assert.equal(h.$('replay').disabled,false);await take(h,['KeyS'],.2);assert.deepEqual(h.writes.at(-1).take.events.map(e=>e[1]),[1]);assert.deepEqual(h.writes.at(-1).previous.events,[[0,7]]);
});


test('a container compatibility click after pointerdown plays and records once, while keyboard activation remains available',async t=>{
 const h=setup(t);await prepare(h);h.$('record').click();const b=h.$('KeyA');for(let i=0;i<2;i++){b.dispatchEvent(new h.w.MouseEvent('pointerdown',{button:0,bubbles:true,cancelable:true}));b.dispatchEvent(new h.w.MouseEvent('pointerup',{button:0,bubbles:true}));b.dispatchEvent(new h.w.MouseEvent('click',{detail:0,bubbles:true}));}assert.equal(h.audio.plays.length,2);b.dispatchEvent(new h.w.KeyboardEvent('keydown',{key:'Enter',code:'Enter',bubbles:true}));b.dispatchEvent(new h.w.MouseEvent('click',{detail:0,bubbles:true}));assert.equal(h.audio.plays.length,3);h.advance(.3);h.$('stop').click();await settle();assert.equal(h.writes.at(-1).take.events.length,3);assert.match(h.$('takeStatus').textContent,/3 次按键/);
});
