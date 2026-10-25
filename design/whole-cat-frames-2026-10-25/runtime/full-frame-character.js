// Every visible state is one complete generated cat+both-paws+instrument image.
// Never combine body/arm layers, warp limbs or draw replacement paw geometry.
const MANIFEST=new URL('./character/whole-piano-v3/manifest.json',import.meta.url);
const LEFT=['KeyA','KeyS','KeyD','KeyF','KeyW','KeyE'];
const RIGHT=['KeyG','KeyH','KeyJ','KeyK','KeyT','KeyY','KeyU'];
const ALL=new Set([...LEFT,...RIGHT]);
const expectedIds=['idle',...ALL,...LEFT.flatMap(l=>RIGHT.map(r=>l+'-'+r))];

export function createFrameState(now=()=>performance.now()){
  let held=new Set(),order=0;const events=new Map();
  return {
    update(keys){
      const time=now(),next=new Set(keys.filter(k=>k.kind==='note'&&ALL.has(k.code)).map(k=>k.code));
      for(const[code,e]of events)if(e.physical&&held.has(code)&&!next.has(code))e.until=Math.max(e.started+80,time);
      held=next;
    },
    strike(key){
      if(key?.kind!=='note'||!ALL.has(key.code))return false;
      const time=now(),physical=held.has(key.code);
      events.set(key.code,{code:key.code,started:time,order:++order,physical,until:physical?Infinity:time+110});return true;
    },
    sample(){
      const time=now();for(const[code,e]of events)if(!held.has(code)&&time>=e.until)events.delete(code);
      const latest=side=>{const active=[...events.values()].filter(e=>side.includes(e.code)),physical=active.filter(e=>held.has(e.code));return(physical.length?physical:active).sort((a,b)=>a.order-b.order).at(-1)?.code;};
      const l=latest(LEFT),r=latest(RIGHT),id=l&&r?l+'-'+r:l||r||'idle';
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

export function mountCharacter(scene){
  const doc=scene.ownerDocument,win=doc.defaultView,svg=scene.querySelector('.cat-scene');
  const canvas=doc.createElement('canvas');canvas.className='full-frame-cat-canvas';canvas.hidden=true;
  Object.assign(canvas.style,{position:'absolute',inset:'0',width:'100%',height:'calc(100% - 22px)',objectFit:'contain',pointerEvents:'none'});
  canvas.setAttribute('role','img');canvas.setAttribute('aria-label','完整橘猫与琴，同一张画面回应你的按键');
  const message=doc.createElement('p');message.className='whole-frame-message';message.textContent='猫猫画面准备中…';
  scene.insertBefore(canvas,scene.querySelector('.stage-readout'));scene.append(message);
  const original={display:svg?.style.display??'',aspect:scene.style.aspectRatio};if(svg)svg.style.display='none';
  const state=createFrameState(()=>win.performance.now()),bitmaps=new Map(),encoded=new Map(),pending=new Map();
  let coreWarming=false,pairWarming=false,coreComplete=false,pairsComplete=false;
  let config,mode=scene.dataset.instrument??'piano',destroyed=false,loaded=false,raf=0,wanted='',shown='',epoch=0,ctx;
  const urlFor=id=>{
    const name=id.startsWith('still:')?config.stills[id.slice(6)]?.src:config.frames[id];
    if(!name)throw new Error('Unknown complete pose');const url=new URL(name,MANIFEST);if(url.origin!==MANIFEST.origin)throw new Error('Nonlocal character asset');return url.href;
  };
  async function getBlob(id){
    if(encoded.has(id))return encoded.get(id);
    const task=(async()=>{const r=await fetch(urlFor(id));if(!r.ok)throw new Error('Complete character image unavailable');const blob=await r.blob();if(blob.size>2000000)throw new Error('Oversized character image');if(destroyed)throw new Error('Character unmounted');return blob;})();encoded.set(id,task);
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
      if(!id.startsWith('still:')&&(image.width!==1254||image.height!==1254))throw new Error('Unexpected full-frame dimensions');
      bitmaps.set(id,image);
      for(const key of bitmaps.keys())if(bitmaps.size>4&&key!==shown&&key!==wanted){bitmaps.get(key).close?.();bitmaps.delete(key);}
      return image;
    })().finally(()=>pending.delete(id));pending.set(id,task);return task;
  }
  async function show(id,ticket){
    try{
      const image=await getBitmap(id);if(destroyed||ticket!==epoch||wanted!==id)return;
      canvas.width=image.width;canvas.height=image.height;ctx=canvas.getContext('2d');if(!ctx)throw new Error('Canvas unavailable');
      ctx.drawImage(image,0,0);canvas.hidden=false;shown=id;scene.dataset.wholeFrame=id;scene.dataset.character='complete-frame-piano-v3';
      scene.style.aspectRatio=String(image.width/image.height);scene.dataset.wholeFrameStatus='ready';
      const label=mode==='marimba'?'完整静帧 · 马林巴动作待补':id.startsWith('still:')?config.stills[id.slice(6)].label:'';message.textContent=label;message.hidden=!label;
    }catch{
      if(destroyed||ticket!==epoch)return;scene.dataset.wholeFrameStatus='unavailable';message.hidden=false;message.textContent='猫猫画面暂未载入，声音仍可演奏。';
    }
  }
  function draw(){
    raf=0;if(destroyed||!loaded)return;
    const pose=state.sample(),id=mode==='piano'?pose.id:mode==='marimba'?'idle':'still:'+mode;
    scene.dataset.confirmedKeys=pose.held.join(',');
    if(id!==wanted){wanted=id;scene.dataset.wholeFrameStatus='loading';show(id,++epoch);}
    if(mode==='marimba'){message.textContent='完整静帧 · 马林巴动作待补';message.hidden=false;}
    if(pose.needsFrame&&mode==='piano')raf=win.requestAnimationFrame(draw);
  }
  function request(){if(loaded&&!destroyed&&!raf)raf=win.requestAnimationFrame(draw);}
  function reset(){state.reset();wanted='';epoch++;if(raf)win.cancelAnimationFrame(raf);raf=0;request();}
  const visibility=()=>{if(doc.hidden)reset();};win.addEventListener('blur',reset);doc.addEventListener('visibilitychange',visibility);
  async function prefetch(pairs=false){
    if((pairs?pairsComplete:coreComplete)||(pairs?pairWarming:coreWarming)||!loaded||mode!=='piano')return;
    if(pairs)pairWarming=true;else coreWarming=true;
    const queue=expectedIds.filter(id=>id.includes('-')===pairs);let cursor=0;
    try{await Promise.all([0,1,2].map(async()=>{while(!destroyed&&mode==='piano'&&cursor<queue.length){const id=queue[cursor++];try{await getBlob(id);}catch{}}}));}
    finally{if(pairs){pairWarming=false;pairsComplete=cursor>=queue.length;}else{coreWarming=false;coreComplete=cursor>=queue.length;}}
  }
  const ready=(async()=>{
    const r=await fetch(MANIFEST);if(!r.ok)throw new Error('Whole-frame manifest unavailable');config=validateFrameManifest(await r.json());
    await getBitmap('idle');if(destroyed)return false;loaded=true;scene.setAttribute('data-complete-character','');draw();prefetch(false);return true;
  })().catch(()=>{if(!destroyed){message.hidden=false;message.textContent='猫猫画面暂未载入，声音仍可演奏。';scene.dataset.wholeFrameStatus='unavailable';}return false;});
  return{ready,
    update(next=mode,keys=[]){const changed=next!==mode;mode=next;if(changed){state.reset();wanted='';epoch++;}state.update(mode==='piano'?keys:[]);request();if(changed&&mode==='piano')prefetch(false);},
    strike(key,next=mode){if(next!==mode){mode=next;reset();}if(mode!=='piano')return false;const accepted=state.strike(key);request();if(accepted)prefetch(true);return accepted;},
    destroy(){if(destroyed)return;destroyed=true;epoch++;if(raf)win.cancelAnimationFrame(raf);win.removeEventListener('blur',reset);doc.removeEventListener('visibilitychange',visibility);for(const image of bitmaps.values())image.close?.();bitmaps.clear();encoded.clear();canvas.remove();message.remove();if(svg)svg.style.display=original.display;scene.style.aspectRatio=original.aspect;scene.removeAttribute('data-complete-character');},
  };
}
