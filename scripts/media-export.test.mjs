import test from 'node:test';import assert from 'node:assert/strict';
import {createMediaExport,mediaExtension,mediaSupported} from '../public/media-export.js';
function fixture(){
 const nodes=[],links=[],stops=[],frames=new Map();let next=1;
 const audioTrack={kind:'audio',stop(){stops.push('audio');}},videoTrack={kind:'video',stop(){stops.push('video');}};
 class Stream{constructor(tracks){this.tracks=tracks;}getTracks(){return this.tracks;}getAudioTracks(){return this.tracks.filter(t=>t.kind==='audio');}getVideoTracks(){return this.tracks.filter(t=>t.kind==='video');}}
 class Recorder{
  static isTypeSupported(type){return type.includes('webm');}
  constructor(stream,options){this.stream=stream;this.mimeType=options.mimeType;this.state='inactive';nodes.push(this);}
  start(){this.state='recording';queueMicrotask(()=>this.onstart?.());}
  stop(){if(this.state==='inactive')return;this.state='inactive';queueMicrotask(()=>{this.ondataavailable?.({data:new Blob(['sample'],{type:this.mimeType})});this.onstop?.();});}
 }
 const ctx={fillRect(){},fillText(){},drawImage(source){assert.equal(source.completeScene,true);}};
 const canvas={getContext:()=>ctx,captureStream:()=>new Stream([videoTrack])};
 const doc=new EventTarget();doc.hidden=false;doc.createElement=()=>canvas;
 const win={performance:{now:()=>0},MediaRecorder:Recorder,MediaStream:Stream,Blob,setTimeout,clearTimeout,requestAnimationFrame:fn=>{const id=next++;frames.set(id,fn);return id;},cancelAnimationFrame:id=>frames.delete(id)};doc.defaultView=win;
 const destination={stream:new Stream([audioTrack])};
 const audio={context:{createMediaStreamDestination:()=>destination},analyser:{connect:node=>links.push(['add',node]),disconnect:node=>{assert.ok(node,'never disconnect speaker output');links.push(['remove',node]);}}};
 return {canvas,ctx,doc,win,audio,source:{width:1254,height:1254,hidden:false,completeScene:true},nodes,links,stops,frames};
}
test('video contains one complete-scene video track and app audio, with correct MIME and cleanup',async()=>{
 const h=fixture(),job=await createMediaExport({...h,kind:'video'});
 assert.deepEqual(h.nodes[0].stream.getTracks().map(t=>t.kind),['audio','video']);assert.ok(h.frames.size);
 job.stop();const result=await job.done;assert.equal(result.extension,'webm');assert.ok(result.blob.size);assert.match(result.mimeType,/video\/webm/);
 assert.deepEqual(h.stops.sort(),['audio','video']);assert.equal(h.frames.size,0);assert.equal(h.links[0][1],h.links[1][1]);
});
test('audio-only export never creates a video track and cancel never produces a partial success',async()=>{
 const h=fixture(),job=await createMediaExport({...h,kind:'audio'});
 assert.deepEqual(h.nodes[0].stream.getTracks().map(t=>t.kind),['audio']);
 job.cancel('cancelled');await assert.rejects(job.done,/cancelled/);assert.deepEqual(h.stops,['audio']);
});
test('size limit and backgrounding reject files and release capture tracks',async()=>{
 for(const reason of ['size','hidden']){
  const h=fixture(),job=await createMediaExport({...h,kind:'video',maxBytes:8});
  if(reason==='size')h.nodes[0].ondataavailable({data:new Blob(['too-large-payload'])});else{h.doc.hidden=true;h.doc.dispatchEvent(new Event('visibilitychange'));}
  await assert.rejects(job.done);assert.deepEqual(h.stops.sort(),['audio','video']);assert.equal(h.frames.size,0);
 }
});
test('unsupported browsers and actual extensions are reported without microphone access',()=>{
 assert.equal(mediaSupported('video',{}),false);assert.equal(mediaExtension('video/mp4;codecs=avc1.42E01E'),'mp4');assert.equal(mediaExtension('audio/mp4'),'m4a');assert.equal(mediaExtension('audio/ogg;codecs=opus'),'ogg');
});


test('square and portrait exports fit the entire scene and return actual dimensions',async()=>{
 for(const [layout,width,height]of [['square',720,720],['portrait',720,1280]]){
  const h=fixture();let fit;h.ctx.drawImage=(...args)=>{fit=args.slice(1);};
  const job=await createMediaExport({...h,kind:'video',layout,title:'A short take'});assert.equal(h.canvas.width,width);assert.equal(h.canvas.height,height);
  const [x,y,w,hgt]=fit;assert.equal(w,hgt);assert.ok(x>=0&&y>=0&&x+w<=width&&y+hgt<=height,'no character cropping');job.stop();const result=await job.done;assert.equal(result.height,height);
 }
});

test('failed or stalled character output aborts capture instead of reporting success',async()=>{
 const h=fixture();let healthy=true;const job=await createMediaExport({...h,kind:'video',visualHealth:()=>healthy});healthy=false;
 for(const fn of [...h.frames.values()])fn();await assert.rejects(job.done,/画面录制中断/);assert.deepEqual(h.stops.sort(),['audio','video']);
});
