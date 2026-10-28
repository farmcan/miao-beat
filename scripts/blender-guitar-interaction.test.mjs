// Exercises the actual draft DOM handlers with controllable platform boundaries.
// Fakes establish event/cancellation contracts, not rendering or speaker quality.
import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';
import {JSDOM} from 'jsdom';import {CHORDS,MELODY} from '../public/bindings.js';
import {createBlenderMotion} from '../public/labs/blender-guitar/motion.js';
const html=await readFile(new URL('../public/labs/blender-guitar/index.html',import.meta.url),'utf8');
const script=(await readFile(new URL('../public/labs/blender-guitar/pilot.js',import.meta.url),'utf8')).replace(/^import .*;\n/gm,'');
const settle=async()=>{for(let i=0;i<12;i++)await Promise.resolve();};
function deferred(){let resolve,reject;const promise=new Promise((r,j)=>{resolve=r;reject=j;});return{promise,resolve,reject};}
async function setup(t){
 let audio,time=0,next=1,delayCreate=null;const frames=new Map(),jobs=[],drawn=[];
 class FakeAudio{constructor(){audio=this;this.context={currentTime:0,state:'running'};this.plays=[];this.stops=0;this.wait=null;this.readyCalls=[];}isReady(){return this.context.state==='running'&&!this.wait;}async ready(preset){this.readyCalls.push(preset);if(this.wait)await this.wait.promise;this.context.state='running';return this.context;}defer(){this.wait=deferred();const gate=this.wait;return()=>{this.wait=null;gate.resolve();};}play(key,preset,when){assert.equal(this.context.state,'running');this.plays.push({key,preset,when});}stopVoices(){this.stops++;}}
 const dom=new JSDOM(html,{url:'https://miao-beat.pages.dev/labs/blender-guitar/',runScripts:'outside-only',pretendToBeVisual:true}),w=dom.window;
 Object.defineProperty(w.performance,'now',{value:()=>time});
 w.requestAnimationFrame=fn=>{const id=next++;frames.set(id,fn);return id;};w.cancelAnimationFrame=id=>frames.delete(id);
 w.HTMLCanvasElement.prototype.getContext=()=>({drawImage:(image,...rect)=>drawn.push({image,rect})});
 w.HTMLMediaElement.prototype.pause=function(){};w.URL.createObjectURL=()=>`blob:local-${next++}`;w.URL.revokeObjectURL=()=>{};
 w.Image=class {naturalWidth=3840;naturalHeight=2560;async decode(){}};
 w.fetch=async()=>({ok:true,json:async()=>({version:1,width:640,height:640,frames:24,columns:6,rows:4,contactFrame:2,fps:60,atlas:'atlas.webp'})});
 async function fakeExport(options){const done=deferred(),job={options,done:done.promise,cancels:0,stops:0,stop(){this.stops++;done.resolve({blob:new Blob(['video']),mimeType:'video/mp4',extension:'mp4'});},cancel(message){this.cancels++;done.reject(Error(message||'cancelled'));}};done.promise.catch(()=>{});jobs.push(job);if(delayCreate)await delayCreate.promise;return job;}
 w.__deps={SampledAudio:FakeAudio,CHORDS,MELODY,createMediaExport:fakeExport,mediaSupported:()=>true,createBlenderMotion:config=>createBlenderMotion(config,()=>time)};
 w.eval('const {SampledAudio,CHORDS,MELODY,createMediaExport,mediaSupported,createBlenderMotion}=window.__deps;\n'+script);
 const $=id=>w.document.getElementById(id),key=(type,code,options={})=>w.document.dispatchEvent(new w.KeyboardEvent(type,{code,bubbles:true,cancelable:true,...options}));
 function frame(ms){time=ms;if(audio.context.state==='running')audio.context.currentTime=ms/1000;const batch=[...frames.values()];frames.clear();for(const cb of batch)cb(ms);}
 function advance(ms){const target=time+ms;while(time<target)frame(Math.min(target,time+16));}
 await settle();$('enableAudio').click();await settle();frame(0);
 async function record(){ $('record').click();await settle();key('keydown','KeyA');key('keyup','KeyA');advance(100);$('record').click();await settle();}
 t.after(()=>{w.dispatchEvent(new w.Event('blur'));dom.window.close();});
 return {w,$,audio,key,frame,advance,record,jobs,drawn,deferCreate(){delayCreate=deferred();const own=delayCreate;return()=>{delayCreate=null;own.resolve();};}};
}

test('real keyboard edges, repeats and composition produce only accepted sampled guitar events',async t=>{const h=await setup(t);h.$('record').click();await settle();h.key('keydown','KeyA');h.key('keydown','KeyA',{repeat:true});h.key('keydown','KeyA');h.key('keyup','KeyA');h.key('keydown','KeyS',{isComposing:true});h.key('keydown','Digit1');h.key('keyup','Digit1');h.advance(100);h.$('record').click();await settle();assert.equal(h.audio.plays.length,2);assert.ok(h.audio.plays.every(p=>p.preset==='guitar'));assert.equal(h.audio.plays[1].key.kind,'chord');assert.match(h.$('recordInfo').textContent,/2 次按键/);});

test('demos/replay/export do not append personal input; extra input is locked during capture',async t=>{const h=await setup(t);await h.record();const before=h.$('recordInfo').textContent;h.$('exportVideo').click();await settle();assert.equal(h.jobs.length,1);assert.equal(h.jobs[0].options.source,h.$('scene'));h.key('keydown','KeyD');h.key('keyup','KeyD');h.advance(1500);await settle();assert.equal(h.audio.plays.length,2);assert.equal(h.$('recordInfo').textContent,before);assert.equal(h.$('downloadVideo').hidden,false);assert.match(h.$('mediaStatus').textContent,/已生成/);assert.ok(h.drawn.length>1);h.$('burstTest').click();await settle();h.advance(2600);await settle();assert.equal(h.$('recordInfo').textContent,before);});

test('cancelled late encoder preparation cannot stop or overwrite a newer recording',async t=>{const h=await setup(t);await h.record();const release=h.deferCreate();h.$('exportVideo').click();await settle();h.$('cancel').click();h.$('record').click();await settle();assert.equal(h.$('record').getAttribute('aria-pressed'),'true');h.key('keydown','KeyS');h.key('keyup','KeyS');const stops=h.audio.stops;release();await settle();assert.equal(h.jobs[0].cancels,1);assert.equal(h.audio.stops,stops);assert.equal(h.$('record').getAttribute('aria-pressed'),'true');assert.equal(h.$('downloadVideo').hidden,true);h.advance(80);h.$('record').click();await settle();assert.match(h.$('recordInfo').textContent,/1 次按键/);});

test('replay resumes a suspended audio context and pending activation obeys cancellation ownership',async t=>{const h=await setup(t);await h.record();h.audio.context.state='suspended';const release=h.audio.defer();h.$('replay').click();await settle();h.$('cancel').click();h.$('record').click();await settle();release();await settle();assert.equal(h.$('record').getAttribute('aria-pressed'),'true');assert.equal(h.audio.plays.length,1,'the stale replay cannot invent a note');h.key('keydown','KeyD');h.key('keyup','KeyD');h.advance(100);h.$('record').click();await settle();h.audio.context.state='suspended';h.$('replay').click();await settle();assert.equal(h.audio.context.state,'running');h.advance(1500);await settle();assert.equal(h.audio.plays.at(-1).key.code,'KeyD');assert.equal(h.$('replay').disabled,false);});

test('frame delivery stall cancels media rather than outputting a falsely complete file',async t=>{const h=await setup(t);await h.record();h.$('exportVideo').click();await settle();h.advance(50);h.frame(600);await settle();assert.equal(h.jobs[0].cancels,1);assert.equal(h.$('downloadVideo').hidden,true);assert.match(h.$('mediaStatus').textContent,/卡顿/);assert.match(h.$('recordInfo').textContent,/1 次按键/);assert.equal(h.$('replay').disabled,false);});
