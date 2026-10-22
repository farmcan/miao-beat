import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {mountPerformance} from '../public/performance.js';
const settle=async()=>{for(let i=0;i<8;i++)await Promise.resolve();};
function setup(t){
 const dom=new JSDOM('<button id="performanceToggle"></button><button id="performanceExit" hidden>退出演奏</button><p id="performanceStatus"></p>',{pretendToBeVisual:true});
 const doc=dom.window.document;dom.window.scrollTo=()=>{};const controller=mountPerformance(doc);t.after(()=>{controller.destroy();dom.window.close();});
 return {doc,win:dom.window,button:doc.getElementById('performanceToggle'),exitButton:doc.getElementById('performanceExit'),controller};
}
test('unsupported or rejected fullscreen keeps an accessible page mode, and exits without losing the page',async t=>{
 for(const reject of [false,true]){
  const h=setup(t);if(reject)h.doc.documentElement.requestFullscreen=async()=>{throw new Error('denied');};
  h.button.click();await settle();assert.equal(h.doc.body.dataset.performanceMode,'page');assert.equal(h.button.textContent,'退出演奏');assert.equal(h.button.disabled,false);
  h.doc.dispatchEvent(new h.win.KeyboardEvent('keydown',{key:'Escape',cancelable:true}));assert.equal(h.doc.body.dataset.performanceMode,'off');assert.equal(h.button.getAttribute('aria-pressed'),'false');
  h.button.click();await settle();h.exitButton.click();await settle();assert.equal(h.doc.body.dataset.performanceMode,'off');
 }
});
test('native request occurs in the click gesture and browser fullscreenchange synchronizes UI on escape',async t=>{
 const h=setup(t);let current=null,requested=false;
 Object.defineProperty(h.doc,'fullscreenElement',{get:()=>current});
 h.doc.documentElement.requestFullscreen=()=>{requested=true;current=h.doc.documentElement;h.doc.dispatchEvent(new h.win.Event('fullscreenchange'));return Promise.resolve();};
 h.button.click();assert.equal(requested,true);await settle();assert.equal(h.doc.body.dataset.performanceMode,'native');
 current=null;h.doc.dispatchEvent(new h.win.Event('fullscreenchange'));assert.equal(h.doc.body.dataset.performanceMode,'off');assert.equal(h.button.textContent,'全屏演奏');
});
test('exit button calls the native exit API and returns to ordinary layout',async t=>{
 const h=setup(t);let current=null,exits=0;
 Object.defineProperty(h.doc,'fullscreenElement',{get:()=>current});
 h.doc.documentElement.requestFullscreen=async()=>{current=h.doc.documentElement;h.doc.dispatchEvent(new h.win.Event('fullscreenchange'));};
 h.doc.exitFullscreen=async()=>{exits++;current=null;h.doc.dispatchEvent(new h.win.Event('fullscreenchange'));};
 h.button.click();await settle();h.exitButton.click();await settle();assert.equal(exits,1);assert.equal(h.doc.body.dataset.performanceMode,'off');
});


test('escape cancels a pending request even when native fullscreen enters late',async t=>{
 const h=setup(t);let current=null,resolve,exits=0;
 Object.defineProperty(h.doc,'fullscreenElement',{get:()=>current});
 h.doc.documentElement.requestFullscreen=()=>new Promise(r=>{resolve=r;});
 h.doc.exitFullscreen=async()=>{exits++;current=null;h.doc.dispatchEvent(new h.win.Event('fullscreenchange'));};
 h.button.click();h.doc.dispatchEvent(new h.win.KeyboardEvent('keydown',{key:'Escape',cancelable:true}));
 assert.equal(h.doc.body.dataset.performanceMode,'off');
 current=h.doc.documentElement;h.doc.dispatchEvent(new h.win.Event('fullscreenchange'));resolve();await settle();
 assert.equal(exits,1);assert.equal(current,null);assert.equal(h.doc.body.dataset.performanceMode,'off');assert.equal(h.button.disabled,false);
});
