import {createGuitarMotion,validateGuitarMotionManifest} from './guitar-motion.js';
// Every visible state is one complete generated cat+both-paws+instrument image.
// Never combine body/arm layers, warp limbs or draw replacement paw geometry.
const MANIFEST=new URL('./character/whole-piano-v3/manifest.json',import.meta.url);
const BAND_MANIFEST=new URL('./character/instrument-scenes-v1/manifest.json',import.meta.url);
const MOTION_MANIFEST=new URL('./character/guitar-motion-v1/manifest.json',import.meta.url);
const LEFT=['KeyA','KeyS','KeyD','KeyF','KeyW','KeyE'];
const RIGHT=['KeyG','KeyH','KeyJ','KeyK','KeyT','KeyY','KeyU'];
const ALL=new Set([...LEFT,...RIGHT]);
const expectedIds=['idle',...ALL,...LEFT.flatMap(l=>RIGHT.map(r=>l+'-'+r))];
const DRUM_LEFT=['KeyZ','KeyC','KeyB','KeyM'],DRUM_RIGHT=['KeyX','KeyV','KeyN','KeyL'];
const GUITAR=[...ALL,'Digit1','Digit2','Digit3','Digit4'];
export const INSTRUMENT_FRAME_IDS={guitar:['idle',...GUITAR],drums:['idle',...DRUM_LEFT,...DRUM_RIGHT,...DRUM_LEFT.flatMap(l=>DRUM_RIGHT.map(r=>l+'-'+r))]};

export function createFrameState(now=()=>performance.now(),instrument='piano'){
  const codes=new Set(instrument==='guitar'?GUITAR:instrument==='drums'?[...DRUM_LEFT,...DRUM_RIGHT]:instrument==='piano'?[...ALL]:[]);
  const accepts=key=>codes.has(key?.code)&&(instrument==='guitar'?key.kind==='note'||key.kind==='chord':instrument==='drums'?key.kind==='drum':key.kind==='note');
  let held=new Set(),order=0;const events=new Map();
  return {
    update(keys){
      const time=now(),next=new Set(keys.filter(accepts).map(k=>k.code));
      for(const[code,e]of events)if(e.physical&&held.has(code)&&!next.has(code))e.until=Math.max(e.started+80,time);
      held=next;
    },
    strike(key){
      if(!accepts(key))return false;
      const time=now(),physical=held.has(key.code);
      events.set(key.code,{code:key.code,started:time,order:++order,physical,until:physical?Infinity:time+(instrument==='piano'?110:180)});return true;
    },
    sample(){
      const time=now();for(const[code,e]of events)if(!held.has(code)&&time>=e.until)events.delete(code);
      const latest=side=>{const active=[...events.values()].filter(e=>side.includes(e.code)),physical=active.filter(e=>held.has(e.code));return(physical.length?physical:active).sort((a,b)=>a.order-b.order).at(-1)?.code;};
      const l=latest(instrument==='drums'?DRUM_LEFT:LEFT),r=latest(instrument==='drums'?DRUM_RIGHT:RIGHT);
      const id=instrument==='guitar'?latest(GUITAR)||'idle':l&&r?l+'-'+r:l||r||'idle';
      return{id,confirmed:[...events.keys()],held:[...held].filter(k=>events.has(k)),needsFrame:[...events.values()].some(e=>!held.has(e.code)&&Number.isFinite(e.until))};
    },
    reset(){held.clear();events.clear();},
  };
}

export function validateFrameManifest(data){
  if(data?.version!==1||data.width!==1254||data.height!==1254||!data.frames||Object.keys(data.frames).length!==56)throw new Error('Unexpected whole-frame manifest');
  for(const id of expectedIds)if(data.frames[id]!==id+'.jpg')throw new Error('Missing complete pose: '+id);
  return data;
}

export function validateInstrumentManifest(data){
  if(data?.version!==1||data.width!==1254||data.height!==1254||!data.modes)throw new Error('Unexpected instrument-scene manifest');
  for(const[mode,ids]of Object.entries(INSTRUMENT_FRAME_IDS)){
    const frames=data.modes[mode]?.frames;
    if(!frames||Object.keys(frames).length!==ids.length)throw new Error('Unexpected complete scenes: '+mode);
    for(const id of ids)if(frames[id]!==mode+'/'+id+'.jpg')throw new Error('Missing complete '+mode+' pose: '+id);
  }
  return data;
}

export function mountCharacter(scene){
  const doc=scene.ownerDocument,win=doc.defaultView,svg=scene.querySelector('.cat-scene');
  const canvas=doc.createElement('canvas');canvas.className='full-frame-cat-canvas';canvas.hidden=true;
  Object.assign(canvas.style,{position:'absolute',inset:'0',width:'100%',height:'calc(100% - 22px)',objectFit:'contain',pointerEvents:'none'});
  canvas.setAttribute('role','img');canvas.setAttribute('aria-label','跟着按键演奏的橘猫');
  const message=doc.createElement('p');message.className='whole-frame-message';message.textContent='猫的图还在加载…';
  scene.insertBefore(canvas,scene.querySelector('.stage-readout'));scene.append(message);
  const original={display:svg?.style.display??'',aspect:scene.style.aspectRatio};if(svg)svg.style.display='none';
  const bitmaps=new Map(),encoded=new Map(),pending=new Map(),warming=new Set(),complete=new Set();
  let config,bandConfig,bandRequest,mode=scene.dataset.instrument??'piano',destroyed=false,loaded=false,raf=0,wanted='',shown='',epoch=0,ctx;
  let visualClock=0,lastMotionTick=win.performance.now();
  let motion,motionConfig,motionRequest,motionEnabled=!win.matchMedia?.('(prefers-reduced-motion: reduce)').matches,wantedAsset='';
  let state=createFrameState(()=>win.performance.now(),mode);
  async function loadBand(){
    if(bandConfig)return bandConfig;
    if(!bandRequest)bandRequest=(async()=>{const r=await fetch(BAND_MANIFEST);if(!r.ok)throw new Error('Instrument scenes unavailable');return bandConfig=validateInstrumentManifest(await r.json());})().finally(()=>{bandRequest=null;});
    return bandRequest;
  }
  function motionStatus(value){scene.dataset.guitarMotion=value;scene.dispatchEvent(new win.CustomEvent('guitar-motion-status',{detail:value}));}
  async function loadMotion(){
    if(motionConfig)return motionConfig;
    if(!motionRequest)motionRequest=(async()=>{
      motionStatus('loading');
      const r=await fetch(MOTION_MANIFEST);if(!r.ok)throw Error('Guitar transitions unavailable');
      motionConfig=validateGuitarMotionManifest(await r.json());
      // Prepare encoded whole scenes before advertising smooth playback. Audio stays usable.
      let cursor=0;const queue=motionConfig.edges.map(e=>'motion:'+e.id);
      await Promise.all([0,1,2].map(async()=>{while(!destroyed&&cursor<queue.length)await getBlob(queue[cursor++]);}));
      if(destroyed)return null;
      await getBitmap('motion:e00');
      motion=createGuitarMotion(motionConfig,()=>visualClock);
      motion.reset(shown.startsWith('guitar:')?shown.slice(7):'idle');lastMotionTick=win.performance.now();
      motionStatus('ready');
      request();return motionConfig;
    })().catch(()=>{motionStatus('unavailable');return null;}).finally(()=>{motionRequest=null;});
    return motionRequest;
  }
  const urlFor=id=>{
    if(id.startsWith('motion:')){const edge=motionConfig.edges.find(e=>e.id===id.slice(7));if(!edge)throw Error('Unknown guitar transition');return new URL(edge.file,MOTION_MANIFEST).href;}

    const[family,pose]=id.includes(':')?id.split(':'):['piano',id];
    const name=family==='piano'?config.frames[pose]:bandConfig.modes[family]?.frames[pose];
    if(!name)throw new Error('Unknown complete pose');const url=new URL(name,family==='piano'?MANIFEST:BAND_MANIFEST);if(url.origin!==MANIFEST.origin)throw new Error('Nonlocal character asset');return url.href;
  };
  async function getBlob(id){
    if(encoded.has(id))return encoded.get(id);
    const task=(async()=>{if(id.includes(':')&&!id.startsWith('motion:'))await loadBand();const r=await fetch(urlFor(id));if(!r.ok)throw new Error('Complete character image unavailable');const blob=await r.blob();if(blob.size>2000000)throw new Error('Oversized character image');if(destroyed)throw new Error('Character unmounted');return blob;})();encoded.set(id,task);
    try{const blob=await task;encoded.set(id,blob);return blob;}catch(error){encoded.delete(id);throw error;}
  }
  async function getBitmap(id){
    if(bitmaps.has(id)){const image=bitmaps.get(id);bitmaps.delete(id);bitmaps.set(id,image);return image;}
    if(pending.has(id))return pending.get(id);
    const task=(async()=>{
      const blob=await getBlob(id);let image;
      if(win.createImageBitmap)image=await win.createImageBitmap(blob);
      else image=await new Promise((resolve,reject)=>{const img=new win.Image();img.onload=()=>resolve(img);img.onerror=reject;img.src=urlFor(id);});
      if(destroyed){image.close?.();throw new Error('Character unmounted');}
      if(image.width!==(id.startsWith('motion:')?2560:1254)||image.height!==(id.startsWith('motion:')?1280:1254))throw new Error('Unexpected full-frame dimensions');
      bitmaps.set(id,image);
      for(const key of bitmaps.keys())if(bitmaps.size>4&&key!==shown&&key!==wantedAsset){bitmaps.get(key).close?.();bitmaps.delete(key);}
      return image;
    })().finally(()=>pending.delete(id));pending.set(id,task);return task;
  }
  async function show(id,ticket,signature=id,cell){
    try{
      const image=await getBitmap(id);if(destroyed||ticket!==epoch||wanted!==signature)return;
      if(canvas.width!==1254||canvas.height!==1254){canvas.width=1254;canvas.height=1254;}ctx=canvas.getContext('2d');if(!ctx)throw new Error('Canvas unavailable');
      if(cell===undefined)ctx.drawImage(image,0,0);else ctx.drawImage(image,(cell%4)*640,Math.floor(cell/4)*640,640,640,0,0,1254,1254);canvas.hidden=false;shown=id;scene.dataset.wholeFrame=id.startsWith('motion:')?'guitar:transition':id;scene.dataset.guitarTransition=cell===undefined?'':id+':'+cell;scene.dataset.character='complete-frame-scenes-v5';
      scene.style.aspectRatio='1';scene.dataset.wholeFrameStatus='ready';
      const label=mode==='marimba'?'马林巴暂用钢琴猫静图，动作还没补。':'';message.textContent=label;message.hidden=!label;
    }catch{
      if(destroyed||ticket!==epoch)return;if(id.startsWith('motion:')){motion=null;motionStatus('unavailable');wanted='';epoch++;request();return;}scene.dataset.wholeFrameStatus='unavailable';message.hidden=false;message.textContent='猫的图没加载出来，声音还能用。';
    }
  }
  function draw(){
    raf=0;if(destroyed||!loaded)return;
    const time=win.performance.now();
    // Do not spend the animation while a new complete-scene strip is decoding.
    if(mode==='guitar'&&motion&&motionEnabled&&shown===wantedAsset)visualClock+=Math.min(32,Math.max(0,time-lastMotionTick));
    lastMotionTick=time;
    const pose=state.sample();let id=mode==='piano'?pose.id:mode==='marimba'?'idle':mode+':'+pose.id,cell,moving=false;
    scene.dataset.confirmedKeys=pose.held.join(',');
    if(mode==='guitar'&&motion&&motionEnabled){const p=motion.sample();moving=p.needsFrame;if(p.edge){id='motion:'+p.edge;cell=p.cell;}else id='guitar:'+p.pose;}
    const signature=id+(cell===undefined?'':':'+cell);
    if(signature!==wanted){wanted=signature;wantedAsset=id;show(id,++epoch,signature,cell);}
    if(mode==='marimba'){message.textContent='马林巴暂用钢琴猫静图，动作还没补。';message.hidden=false;}
    if(pose.needsFrame||moving)raf=win.requestAnimationFrame(draw);
  }
  function request(){if(loaded&&!destroyed&&!raf)raf=win.requestAnimationFrame(draw);}
  function reset(){state.reset();motion?.reset();wanted='';epoch++;if(raf)win.cancelAnimationFrame(raf);raf=0;request();}
  const visibility=()=>{if(doc.hidden)reset();};win.addEventListener('blur',reset);doc.addEventListener('visibilitychange',visibility);
  async function prefetch(pairs=false){
    const family=mode,tag=family+':'+pairs;
    if(complete.has(tag)||warming.has(tag)||!loaded||family==='marimba')return;
    warming.add(tag);
    const queue=(family==='piano'?expectedIds:INSTRUMENT_FRAME_IDS[family]).filter(id=>id.includes('-')===pairs).map(id=>family==='piano'?id:family+':'+id);let cursor=0,failed=false;
    try{await Promise.all([0,1,2].map(async()=>{while(!destroyed&&mode===family&&cursor<queue.length){const id=queue[cursor++];try{await getBlob(id);}catch{failed=true;}}}));}
    finally{warming.delete(tag);if(cursor>=queue.length&&!failed)complete.add(tag);}
  }
  const ready=(async()=>{
    const r=await fetch(MANIFEST);if(!r.ok)throw new Error('Whole-frame manifest unavailable');config=validateFrameManifest(await r.json());
    await getBitmap('idle');if(destroyed)return false;loaded=true;scene.setAttribute('data-complete-character','');draw();prefetch(false);if(mode==='guitar')loadMotion();return true;
  })().catch(()=>{if(!destroyed){message.hidden=false;message.textContent='猫的图没加载出来，声音还能用。';scene.dataset.wholeFrameStatus='unavailable';}return false;});
  return{ready,
    setMotionEnabled(enabled){motionEnabled=!!enabled;motion?.reset(state.sample().id);wanted='';epoch++;request();},
    update(next=mode,keys=[]){const changed=next!==mode;mode=next;if(changed){state=createFrameState(()=>win.performance.now(),mode);wanted='';epoch++;canvas.hidden=true;message.hidden=false;message.textContent='猫的图还在加载…';}state.update(keys);request();if(changed){motion?.reset();prefetch(false);if(mode==='guitar')loadMotion();}},
    strike(key,next=mode){if(next!==mode){mode=next;state=createFrameState(()=>win.performance.now(),mode);canvas.hidden=true;message.hidden=false;message.textContent='猫的图还在加载…';reset();}const accepted=state.strike(key);if(accepted&&mode==='guitar'&&motionEnabled&&motion){if(motion.target===key.code)motion.pulse();else motion.go(key.code);}request();if(accepted)prefetch(true);return accepted;},
    destroy(){if(destroyed)return;destroyed=true;epoch++;if(raf)win.cancelAnimationFrame(raf);win.removeEventListener('blur',reset);doc.removeEventListener('visibilitychange',visibility);for(const image of bitmaps.values())image.close?.();bitmaps.clear();encoded.clear();canvas.remove();message.remove();if(svg)svg.style.display=original.display;scene.style.aspectRatio=original.aspect;scene.removeAttribute('data-complete-character');},
  };
}
