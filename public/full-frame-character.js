// Every visible state is one complete generated cat+both-paws+instrument image.
// Never combine body/arm layers, warp limbs or draw replacement paw geometry.
const MANIFEST=new URL('./character/whole-piano-v3/manifest.json',import.meta.url);
const BAND_MANIFEST=new URL('./character/instrument-scenes-v1/manifest.json',import.meta.url);
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
  let state=createFrameState(()=>win.performance.now(),mode);
  async function loadBand(){
    if(bandConfig)return bandConfig;
    if(!bandRequest)bandRequest=(async()=>{const r=await fetch(BAND_MANIFEST);if(!r.ok)throw new Error('Instrument scenes unavailable');return bandConfig=validateInstrumentManifest(await r.json());})().finally(()=>{bandRequest=null;});
    return bandRequest;
  }
  const urlFor=id=>{
    const[family,pose]=id.includes(':')?id.split(':'):['piano',id];
    const name=family==='piano'?config.frames[pose]:bandConfig.modes[family]?.frames[pose];
    if(!name)throw new Error('Unknown complete pose');const url=new URL(name,family==='piano'?MANIFEST:BAND_MANIFEST);if(url.origin!==MANIFEST.origin)throw new Error('Nonlocal character asset');return url.href;
  };
  async function getBlob(id){
    if(encoded.has(id))return encoded.get(id);
    const task=(async()=>{if(id.includes(':'))await loadBand();const r=await fetch(urlFor(id));if(!r.ok)throw new Error('Complete character image unavailable');const blob=await r.blob();if(blob.size>2000000)throw new Error('Oversized character image');if(destroyed)throw new Error('Character unmounted');return blob;})();encoded.set(id,task);
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
      if(image.width!==1254||image.height!==1254)throw new Error('Unexpected full-frame dimensions');
      bitmaps.set(id,image);
      for(const key of bitmaps.keys())if(bitmaps.size>4&&key!==shown&&key!==wanted){bitmaps.get(key).close?.();bitmaps.delete(key);}
      return image;
    })().finally(()=>pending.delete(id));pending.set(id,task);return task;
  }
  async function show(id,ticket){
    try{
      const image=await getBitmap(id);if(destroyed||ticket!==epoch||wanted!==id)return;
      canvas.width=image.width;canvas.height=image.height;ctx=canvas.getContext('2d');if(!ctx)throw new Error('Canvas unavailable');
      ctx.drawImage(image,0,0);canvas.hidden=false;shown=id;scene.dataset.wholeFrame=id;scene.dataset.character='complete-frame-scenes-v4';
      scene.style.aspectRatio=String(image.width/image.height);scene.dataset.wholeFrameStatus='ready';
      const label=mode==='marimba'?'马林巴暂用钢琴猫静图，动作还没补。':'';message.textContent=label;message.hidden=!label;
    }catch{
      if(destroyed||ticket!==epoch)return;scene.dataset.wholeFrameStatus='unavailable';message.hidden=false;message.textContent='猫的图没加载出来，声音还能用。';
    }
  }
  function draw(){
    raf=0;if(destroyed||!loaded)return;
    const pose=state.sample(),id=mode==='piano'?pose.id:mode==='marimba'?'idle':mode+':'+pose.id;
    scene.dataset.confirmedKeys=pose.held.join(',');
    if(id!==wanted){wanted=id;scene.dataset.wholeFrameStatus='loading';show(id,++epoch);}
    if(mode==='marimba'){message.textContent='马林巴暂用钢琴猫静图，动作还没补。';message.hidden=false;}
    if(pose.needsFrame)raf=win.requestAnimationFrame(draw);
  }
  function request(){if(loaded&&!destroyed&&!raf)raf=win.requestAnimationFrame(draw);}
  function reset(){state.reset();wanted='';epoch++;if(raf)win.cancelAnimationFrame(raf);raf=0;request();}
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
    await getBitmap('idle');if(destroyed)return false;loaded=true;scene.setAttribute('data-complete-character','');draw();prefetch(false);return true;
  })().catch(()=>{if(!destroyed){message.hidden=false;message.textContent='猫的图没加载出来，声音还能用。';scene.dataset.wholeFrameStatus='unavailable';}return false;});
  return{ready,
    update(next=mode,keys=[]){const changed=next!==mode;mode=next;if(changed){state=createFrameState(()=>win.performance.now(),mode);wanted='';epoch++;canvas.hidden=true;message.hidden=false;message.textContent='猫的图还在加载…';}state.update(keys);request();if(changed)prefetch(false);},
    strike(key,next=mode){if(next!==mode){mode=next;state=createFrameState(()=>win.performance.now(),mode);canvas.hidden=true;message.hidden=false;message.textContent='猫的图还在加载…';reset();}const accepted=state.strike(key);request();if(accepted)prefetch(true);return accepted;},
    destroy(){if(destroyed)return;destroyed=true;epoch++;if(raf)win.cancelAnimationFrame(raf);win.removeEventListener('blur',reset);doc.removeEventListener('visibilitychange',visibility);for(const image of bitmaps.values())image.close?.();bitmaps.clear();encoded.clear();canvas.remove();message.remove();if(svg)svg.style.display=original.display;scene.style.aspectRatio=original.aspect;scene.removeAttribute('data-complete-character');},
  };
}
