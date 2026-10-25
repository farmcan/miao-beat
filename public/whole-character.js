const MANIFEST=new URL('./character/keyboard-motion-v1.json',import.meta.url);
const STYLE=new URL('./character/whole.css',import.meta.url);

// Complete captured poses: no separated arm layers, video seeking or queued clips.
export function createPoseState(config,now=()=>performance.now()){
  let held=new Set(),events=new Map(),frame=config.idle,release=null,rest=config.idle;
  const contactFor=key=>key.midi<66?(key.midi<=62?'leftLow':'leftMid'):(key.midi>=70?'rightOuter':'rightMid');
  function reset(){held.clear();events.clear();frame=rest=config.idle;release=null;}
  return {
    update(keys){held=new Set(keys.filter(k=>k.kind==='note').map(k=>k.code));},
    strike(key){
      if(key.kind!=='note')return false;
      const time=now();events.set(key.code,{code:key.code,side:key.midi<66?'left':'right',pose:contactFor(key),time,until:time+110});
      release=null;return true;
    },
    sample(){
      const time=now();for(const[code,event]of events)if(!held.has(code)&&time>=event.until)events.delete(code);
      const active=[...events.values()].sort((a,b)=>a.time-b.time);
      if(active.length){
        const sides=new Set(active.map(e=>e.side)),pose=sides.size>1?'both':active.at(-1).pose;
        const action=config.actions[pose];frame=action.contact;rest=action.release.at(-1)??config.idle;
        release={pose,frames:action.release,start:null};
        return {frame,pose,phase:'contact',needsFrame:active.some(e=>!held.has(e.code)&&time<e.until)};
      }
      if(release?.frames.length){
        release.start??=time;const index=Math.floor((time-release.start)/70);
        if(index<release.frames.length)return {frame:release.frames[index],pose:release.pose,phase:'release',needsFrame:true};
        release=null;frame=rest;
      }
      return {frame,pose:'rest',phase:'idle',needsFrame:false};
    },
    reset,
  };
}

export function mountCharacter(scene){
  const doc=scene.ownerDocument,win=doc.defaultView;
  const legacy=scene.querySelector('.cat-scene'),legacyDisplay=legacy?.style.display;
  if(legacy)legacy.style.display='none';
  const canvas=doc.createElement('canvas');canvas.className='whole-cat-canvas';canvas.hidden=true;
  canvas.setAttribute('role','img');canvas.setAttribute('aria-label','完整橘猫与乐器画面');
  const notice=doc.createElement('p');notice.className='whole-motion-note';notice.setAttribute('role','status');notice.textContent='猫猫的整图准备中…';
  scene.insertBefore(canvas,scene.querySelector('.stage-readout'));
  scene.append(notice);scene.setAttribute('data-whole-character','');
  const style=doc.createElement('link');style.rel='stylesheet';style.href=STYLE.href;doc.head.append(style);
  const cssReady=new Promise((resolve,reject)=>{style.onload=resolve;style.onerror=()=>reject(new Error('Whole-character style unavailable'));});
  cssReady.catch(()=>{});
  const reduced=win.matchMedia?.('(prefers-reduced-motion: reduce)');
  const stillSources={guitar:new URL('./character/guitar-whole-still-v1.jpg',import.meta.url),drums:new URL('./character/drums-whole-still-v1.jpg',import.meta.url)};
  const labels={guitar:'吉他整图静帧 · 动作待补',drums:'架子鼓整图静帧 · 动作待补',marimba:'马林巴音色 · 暂用完整键盘猫静帧，动作待补'};
  const images=new Map(),pending=new Map(),failed=new Set();
  let mode=scene.dataset.instrument??'piano',keys=[],loaded=false,destroyed=false,raf=0,state,config,atlas,lastFrame=-1;
  const loadImage=url=>new Promise((resolve,reject)=>{const image=new win.Image();image.onload=()=>resolve(image);image.onerror=()=>reject(new Error('Whole image unavailable'));image.src=url.href;});
  function loadStill(next){
    if(!stillSources[next]||images.has(next)||pending.has(next)||failed.has(next))return;
    pending.set(next,loadImage(stillSources[next]).then(image=>{images.set(next,image);if(!destroyed&&mode===next)applyMode();}).catch(()=>{failed.add(next);if(!destroyed&&mode===next)applyMode();}));
  }
  function draw(){
    raf=0;if(destroyed||!loaded||canvas.hidden)return;
    if(mode!=='piano'){
      const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);
      const image=images.get(mode);
      if(image){const scale=Math.min(canvas.width/image.naturalWidth,canvas.height/image.naturalHeight),w=image.naturalWidth*scale,h=image.naturalHeight*scale;ctx.drawImage(image,0,0,image.naturalWidth,image.naturalHeight,(canvas.width-w)/2,(canvas.height-h)/2,w,h);}
      else{const frame=config.idle;ctx.drawImage(atlas,(frame%config.columns)*config.width,Math.floor(frame/config.columns)*config.height,config.width,config.height,0,0,canvas.width,canvas.height);}
      scene.dataset.motionPose='static';scene.dataset.motionPhase='static';scene.dataset.motionFrame=String(config.idle);lastFrame=-1;return;
    }
    const pose=state.sample();scene.dataset.motionPose=pose.pose;scene.dataset.motionPhase=pose.phase;
    if(lastFrame!==pose.frame){
      const ctx=canvas.getContext('2d'),column=pose.frame%config.columns,row=Math.floor(pose.frame/config.columns);
      ctx.clearRect(0,0,canvas.width,canvas.height);
      ctx.drawImage(atlas,column*config.width,row*config.height,config.width,config.height,0,0,canvas.width,canvas.height);
      lastFrame=pose.frame;scene.dataset.motionFrame=String(pose.frame);
    }
    if(pose.needsFrame)raf=win.requestAnimationFrame(draw);
  }
  function request(){if(loaded&&!destroyed&&!raf)raf=win.requestAnimationFrame(draw);}
  function applyMode(){
    if(!loaded||destroyed)return;
    const needsStill=Boolean(stillSources[mode]);loadStill(mode);
    const unavailable=failed.has(mode),waiting=needsStill&&!images.has(mode)&&!unavailable;
    canvas.hidden=unavailable||waiting;notice.hidden=mode==='piano'&&!unavailable;
    notice.textContent=unavailable?'这张完整猫图暂时没加载，声音仍可用。':waiting?'完整乐器静帧准备中…':labels[mode]||'完整静帧 · 对应动作待补';
    canvas.setAttribute('aria-label',mode==='piano'?'完整橘猫与键盘，按音域显示原片姿态':labels[mode]||'完整橘猫静帧');
    scene.dataset.character=unavailable?'whole-image-unavailable':mode==='piano'?'whole-cat-poses-v1':'whole-cat-still-v1';
    scene.dataset.motionStatus=unavailable?'unavailable':mode==='piano'?'region-preview':'static-preview';request();
  }
  function reset(){state?.reset();if(raf)win.cancelAnimationFrame(raf);raf=0;lastFrame=-1;request();}
  const visibility=()=>{if(doc.hidden)reset();};
  win.addEventListener('blur',reset);doc.addEventListener('visibilitychange',visibility);reduced?.addEventListener?.('change',reset);
  const wholeReady=(async()=>{
    const response=await win.fetch(MANIFEST);if(!response.ok)throw new Error('Whole-character manifest unavailable');
    config=await response.json();
    if(config.version!==1||config.width!==480||config.height!==412||config.columns!==4||config.frameCount!==13)throw new Error('Unreviewed whole-character layout');
    const url=new URL(config.atlas,MANIFEST);if(url.origin!==MANIFEST.origin)throw new Error('Character image must be local');
    [atlas]=await Promise.all([loadImage(url),cssReady]);
    if(destroyed)return;
    canvas.width=config.width;canvas.height=config.height;
    if(!canvas.getContext('2d'))throw new Error('Canvas unavailable');
    state=createPoseState(config,()=>win.performance.now());loaded=true;applyMode();
  })();
  const ready=wholeReady.catch(()=>{if(destroyed)return;canvas.hidden=true;notice.hidden=false;notice.textContent='猫猫的整图暂时没加载，声音仍可用。';scene.dataset.character='whole-image-unavailable';scene.dataset.motionStatus='unavailable';});
  return {
    ready,
    update(next=mode,nextKeys=keys){
      const changed=next!==mode;mode=next;keys=nextKeys;
      if(changed)reset();state?.update(mode==='piano'?keys:[]);applyMode();request();
    },
    strike(key,next=mode){
      if(next!==mode){mode=next;reset();applyMode();}
      if(loaded&&mode==='piano'){
        if(state.strike(key)){state.update(keys);request();}
      }
    },
    destroy(){
      if(destroyed)return;destroyed=true;if(raf)win.cancelAnimationFrame(raf);
      win.removeEventListener('blur',reset);doc.removeEventListener('visibilitychange',visibility);reduced?.removeEventListener?.('change',reset);
      canvas.remove();notice.remove();style.remove();scene.removeAttribute('data-whole-character');if(legacy)legacy.style.display=legacyDisplay;
    },
  };
}
