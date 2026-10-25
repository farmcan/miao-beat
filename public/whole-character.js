import {mountCharacter as mountRigCharacter} from './character.js';

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
  let rig=null,wholeFailed=false;
  const canvas=doc.createElement('canvas');canvas.className='whole-cat-canvas';canvas.hidden=true;
  canvas.setAttribute('role','img');canvas.setAttribute('aria-label','橘猫在小键盘前，随你的输入呈现完整演奏姿态');
  scene.insertBefore(canvas,scene.querySelector('.stage-readout'));
  const style=doc.createElement('link');style.rel='stylesheet';style.href=STYLE.href;doc.head.append(style);
  const cssReady=new Promise((resolve,reject)=>{style.onload=resolve;style.onerror=()=>reject(new Error('Whole-character style unavailable'));});
  cssReady.catch(()=>{});
  const reduced=win.matchMedia?.('(prefers-reduced-motion: reduce)');
  let mode=scene.dataset.instrument??'piano',keys=[],loaded=false,destroyed=false,raf=0,state,config,atlas,lastFrame=-1;
  function ensureRig(){
    if(!rig){rig=mountRigCharacter(scene);rig.update?.(mode,mode==='piano'?[]:keys);rig.ready.then(()=>{if(loaded&&!destroyed)applyMode();}).catch(()=>{});}
    return rig;
  }
  if(mode!=='piano')ensureRig();
  function draw(){
    raf=0;if(destroyed||!loaded||mode!=='piano')return;
    const pose=state.sample();scene.dataset.motionPose=pose.pose;scene.dataset.motionPhase=pose.phase;
    if(lastFrame!==pose.frame){
      const ctx=canvas.getContext('2d'),column=pose.frame%config.columns,row=Math.floor(pose.frame/config.columns);
      ctx.clearRect(0,0,canvas.width,canvas.height);
      ctx.drawImage(atlas,column*config.width,row*config.height,config.width,config.height,0,0,canvas.width,canvas.height);
      lastFrame=pose.frame;scene.dataset.motionFrame=String(pose.frame);
    }
    if(pose.needsFrame)raf=win.requestAnimationFrame(draw);
  }
  function request(){if(loaded&&mode==='piano'&&!raf)raf=win.requestAnimationFrame(draw);}
  function applyMode(){
    const active=loaded&&mode==='piano';canvas.hidden=!active;
    scene.toggleAttribute('data-whole-character',active);
    if(active){scene.dataset.character='whole-cat-poses-v1';request();}
    else if(loaded){scene.dataset.character='orange-articulated-v3';delete scene.dataset.motionPose;delete scene.dataset.motionPhase;}
  }
  function reset(){state?.reset();if(raf)win.cancelAnimationFrame(raf);raf=0;lastFrame=-1;request();}
  const visibility=()=>{if(doc.hidden)reset();};
  win.addEventListener('blur',reset);doc.addEventListener('visibilitychange',visibility);reduced?.addEventListener?.('change',reset);
  const wholeReady=(async()=>{
    const response=await fetch(MANIFEST);if(!response.ok)throw new Error('Whole-character manifest unavailable');
    config=await response.json();
    if(config.version!==1||config.width!==480||config.height!==412||config.columns!==4||config.frameCount!==13)throw new Error('Unreviewed whole-character layout');
    const url=new URL(config.atlas,MANIFEST);if(url.origin!==MANIFEST.origin)throw new Error('Character image must be local');
    atlas=new win.Image();await Promise.all([cssReady,new Promise((resolve,reject)=>{atlas.onload=resolve;atlas.onerror=()=>reject(new Error('Character image unavailable'));atlas.src=url.href;})]);
    if(destroyed)return;
    canvas.width=config.width;canvas.height=config.height;
    if(!canvas.getContext('2d'))throw new Error('Canvas unavailable');
    state=createPoseState(config,()=>win.performance.now());loaded=true;applyMode();
  })();
  wholeReady.catch(()=>{if(destroyed)return;wholeFailed=true;scene.dataset.motionStatus='original-character-fallback';canvas.hidden=true;scene.removeAttribute('data-whole-character');ensureRig();});
  // The keyboard does not download legacy character sheets until another instrument needs them.
  const ready=wholeReady.catch(()=>destroyed?undefined:ensureRig().ready);
  return {
    ready,
    update(next=mode,nextKeys=keys){
      const changed=next!==mode;mode=next;keys=nextKeys;if(mode!=='piano'||wholeFailed)ensureRig().update?.(mode,keys);else rig?.update?.(mode,[]);
      if(changed)reset();state?.update(keys);applyMode();request();
    },
    strike(key,next=mode){
      if(next!==mode){mode=next;reset();applyMode();}
      if(loaded&&mode==='piano'){
        if(state.strike(key)){state.update(keys);request();}
      }else if(mode!=='piano'||wholeFailed)ensureRig().strike?.(key,next);
    },
    destroy(){
      if(destroyed)return;destroyed=true;if(raf)win.cancelAnimationFrame(raf);
      win.removeEventListener('blur',reset);doc.removeEventListener('visibilitychange',visibility);reduced?.removeEventListener?.('change',reset);
      canvas.remove();style.remove();scene.removeAttribute('data-whole-character');rig?.destroy();
    },
  };
}
