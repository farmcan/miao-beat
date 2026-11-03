import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {mountMediaSharing} from '../public/media-sharing.js';
function setup(t,{supported=true,share=async()=>{}}={}){
 const w=new JSDOM('<button id="shareVideo" hidden></button><button id="shareAudio" hidden></button><p id="shareStatus"></p>',{url:'https://miao-beat.pages.dev/'}).window;
 t.after(()=>w.close());if(supported){w.navigator.canShare=({files})=>files.length===1;w.navigator.share=share;}
 let busy=false;const controller=mountMediaSharing(w.document,{isBusy:()=>busy}),$=id=>w.document.getElementById(id);
 return {w,$,controller,setBusy:value=>{busy=value;controller.refresh();}};
}
const ticks=async()=>{for(let i=0;i<5;i++)await Promise.resolve();};
test('prepared file shares synchronously in a tap, preserves name/mime, and does not claim a posted note',async t=>{
 const calls=[];const h=setup(t,{share:data=>{calls.push(data);return Promise.resolve();}});h.controller.setMedia('video',{blob:new h.w.Blob(['mp4'],{type:'video/mp4;codecs=avc1'}),name:'my-song.mp4'});
 assert.equal(h.$('shareVideo').hidden,false);h.$('shareVideo').click();assert.equal(calls.length,1,'no activation-losing await before share');assert.equal(calls[0].files[0].name,'my-song.mp4');assert.equal(calls[0].files[0].type,'video/mp4');await ticks();assert.match(h.$('shareStatus').textContent,/目标应用确认/);assert.equal(h.$('shareVideo').disabled,false);
});
test('cancel preserves prepared file and allows retry while busy suppresses sharing',async t=>{
 let calls=0;const h=setup(t,{share:async()=>{calls++;throw Object.assign(new Error(),{name:'AbortError'});}});h.controller.setMedia('audio',{blob:new h.w.Blob(['audio'],{type:'audio/mp4'}),name:'take.m4a'});h.setBusy(true);h.$('shareAudio').click();assert.equal(calls,0);h.setBusy(false);h.$('shareAudio').click();await ticks();assert.match(h.$('shareStatus').textContent,/已取消/);h.$('shareAudio').click();await ticks();assert.equal(calls,2);
});
test('unsupported or rejected file types keep download guidance and hide unavailable buttons',t=>{
 const h=setup(t,{supported:false});h.controller.setMedia('video',{blob:new h.w.Blob(['v']),name:'v.mp4'});assert.equal(h.$('shareVideo').hidden,true);assert.match(h.$('shareStatus').textContent,/保存/);
 h.w.navigator.share=async()=>{};h.w.navigator.canShare=()=>{throw new Error('not permitted');};h.controller.setMedia('video',{blob:new h.w.Blob(['v']),name:'v.mp4'});assert.equal(h.$('shareVideo').hidden,true);
});
