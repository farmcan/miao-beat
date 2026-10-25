import {MELODY} from './bindings.js';

const BODY=new URL('./character/keyboard-body-v2.jpg',import.meta.url).href;
const ARM_TEXTURE=new URL('./character/whole-arm-v2.png',import.meta.url).href;
const ARM_TEXTURE_BOUNDS={x:458,y:61,width:349,height:1130,tipX:609,worldWidth:125};
const SIZE=1254,PAW_X=50,PAW_Y=45;
const NOTES=new Map(MELODY.map(key=>[key.code,key]));
const WHITES=['KeyA','KeyS','KeyD','KeyF','KeyG','KeyH','KeyJ','KeyK'];
const BLACKS=['KeyW','KeyE','KeyT','KeyY','KeyU'];
const BOUNDARIES=[1,2,4,5,6],BLACK_X=[425,504,661,740,819];
const REST={left:[430,720],right:[880,720]};
const SHOULDERS={left:[380,490],right:[860,490]};
const mounted=new WeakMap();
const clamp=value=>Math.max(0,Math.min(1,value));
const smooth=u=>{u=clamp(u);return u*u*(3-2*u);};
const mix=(a,b,u)=>a+(b-a)*u;

// All coordinates are in the source photograph's 1254-square canvas.
export function pianoKeyGeometry(code,amount=0){
  const key=NOTES.get(code);if(!key)return null;
  const white=WHITES.indexOf(code),black=BLACKS.indexOf(code),down=clamp(amount);
  if(white>=0){
    const top0=356+610*white/8,top1=356+610*(white+1)/8;
    const front0=326+672*white/8,front1=326+672*(white+1)/8;
    return {code,black:false,points:[[top0,690],[top1,690],[front1,789+10*down],[front0,789+10*down]],contact:[368+84*white,773+10*down*83/99]};
  }
  const boundary=BOUNDARIES[black],top=356+610*boundary/8;
  const lowerLeft=mix(356,326,57/99),lowerWidth=mix(610,672,57/99),front=lowerLeft+lowerWidth*boundary/8;
  return {code,black:true,points:[[top-20,690],[top+20,690],[front+23,747+7*down],[front-23,747+7*down]],contact:[BLACK_X[black],735+7*down*45/57]};
}

export function pianoContact(key,amount=1){
  const geometry=pianoKeyGeometry(key?.code,amount);
  return geometry?{code:key.code,side:NOTES.get(key.code).paw,point:geometry.contact}:null;
}

// A single closed silhouette follows a softened elbow guide. There are no
// independently rotated upper-arm/forearm images or exposed joint caps.
export function armGuide(side,tip){
  const shoulder=SHOULDERS[side],wrist=[tip[0],tip[1]-PAW_Y];
  const dx=wrist[0]-shoulder[0],dy=wrist[1]-shoulder[1],distance=Math.hypot(dx,dy);
  if(distance>399.99||distance<.01)throw new RangeError('Piano contact is outside the fixed arm workspace');
  const angle=Math.atan2(dy,dx)+(side==='left'?1:-1)*Math.acos(distance/400);
  const joint=[shoulder[0]+200*Math.cos(angle),shoulder[1]+200*Math.sin(angle)];
  const midpoint=[(shoulder[0]+wrist[0])/2,(shoulder[1]+wrist[1])/2];
  return {shoulder,wrist,elbow:joint,curve:[mix(midpoint[0],joint[0],.55),mix(midpoint[1],joint[1],.55)]};
}

function keyLevel(entry,time){return mix(entry.from,entry.to,smooth((time-entry.start)/entry.duration));}
function sampleArm(arm,time){
  const m=arm.motion;if(!m)return {...arm.point,vx:0,vy:0,moving:false};
  const u=clamp((time-m.start)/m.duration),u2=u*u,u3=u2*u;
  const value=(a,b,v)=>(2*u3-3*u2+1)*a+(u3-2*u2+u)*m.duration*v+(-2*u3+3*u2)*b;
  const velocity=(a,b,v)=>(6*u2-6*u)*(a-b)/m.duration+(3*u2-4*u+1)*v;
  return {x:value(m.from.x,m.to.x,m.from.vx),y:value(m.from.y,m.to.y,m.from.vy),vx:velocity(m.from.x,m.to.x,m.from.vx),vy:velocity(m.from.y,m.to.y,m.from.vy),moving:u<1};
}

export function createPianoState(now=()=>performance.now()){
  let held=new Set(),serial=0;
  const confirmed=new Map(),levels=new Map(MELODY.map(k=>[k.code,{from:0,to:0,start:0,duration:1}]));
  const arms=Object.fromEntries(['left','right'].map(side=>[side,{code:null,point:{x:REST[side][0],y:REST[side][1]},motion:null}]));
  function setLevel(code,to,time){const e=levels.get(code);if(e.to===to)return;levels.set(code,{from:keyLevel(e,time),to,start:time,duration:to?34:90});}
  function sync(time){
    for(const[code,event]of confirmed)if(!held.has(code)&&time>=event.until)confirmed.delete(code);
    for(const key of MELODY)setLevel(key.code,confirmed.has(key.code)?1:0,time);
    for(const side of ['left','right']){
      const arm=arms[side],candidates=[...confirmed.values()].filter(e=>e.key.paw===side);
      const heldCandidates=candidates.filter(e=>held.has(e.key.code));
      const event=(heldCandidates.length?heldCandidates:candidates).sort((a,b)=>a.order-b.order).at(-1);
      const code=event?.key.code??null;
      if(code!==arm.code){
        const from=sampleArm(arm,time),point=event?pianoContact(event.key).point:REST[side];
        arm.point={x:from.x,y:from.y};arm.code=code;
        arm.motion={start:time,from,to:{x:point[0],y:point[1]},duration:event?68:130};
      }
    }
  }
  return {
    update(keys){
      const time=now(),next=new Set(keys.filter(k=>NOTES.has(k.code)&&k.kind==='note').map(k=>k.code));
      for(const[code,event]of confirmed)if(event.physical&&held.has(code)&&!next.has(code))event.until=Math.max(event.started+80,time);
      held=next;sync(time);
    },
    strike(key){
      const actual=NOTES.get(key?.code);if(key?.kind!=='note'||!actual)return false;
      const time=now(),physical=held.has(actual.code);
      confirmed.set(actual.code,{key:actual,order:++serial,started:time,physical,until:physical?Infinity:time+110});
      sync(time);return true;
    },
    sample(){
      const time=now();sync(time);let moving=false;
      const hands={};
      for(const side of ['left','right']){
        const arm=arms[side],p=sampleArm(arm,time);moving||=p.moving;
        if(!p.moving){arm.point={x:p.x,y:p.y};arm.motion=null;}
        hands[side]={...p,code:arm.code,side};
      }
      const keys=Object.fromEntries([...levels].map(([code,e])=>{moving||=e.from!==e.to&&time<e.start+e.duration;return[code,keyLevel(e,time)];}));
      const expiry=[...confirmed.values()].some(e=>!held.has(e.key.code)&&Number.isFinite(e.until));
      return {hands,keys,held:[...held].filter(code=>confirmed.has(code)),needsFrame:moving||expiry};
    },
    reset(){
      held.clear();confirmed.clear();
      for(const code of levels.keys())levels.set(code,{from:0,to:0,start:now(),duration:1});
      for(const side of ['left','right']){arms[side].code=null;arms[side].motion=null;arms[side].point={x:REST[side][0],y:REST[side][1]};}
    },
  };
}

function polygon(ctx,points){ctx.beginPath();ctx.moveTo(...points[0]);for(const p of points.slice(1))ctx.lineTo(...p);ctx.closePath();}
function drawKey(ctx,geometry,amount){
  const p=geometry.points,gradient=ctx.createLinearGradient(0,690,0,p[2][1]);
  if(geometry.black){gradient.addColorStop(0,'#403a32');gradient.addColorStop(1,amount>.1?'#25231f':'#35312a');}
  else{gradient.addColorStop(0,'#f6edda');gradient.addColorStop(1,amount>.1?'#e4d4b5':'#eee3ca');}
  polygon(ctx,p);ctx.fillStyle=gradient;ctx.fill();ctx.strokeStyle=geometry.black?'#24221d':'#a99a80';ctx.lineWidth=geometry.black?2:1.7;ctx.stroke();
  ctx.beginPath();ctx.moveTo(...p[3]);ctx.lineTo(...p[2]);ctx.strokeStyle=geometry.black?'#60554a':'#fff6e5';ctx.lineWidth=geometry.black?3:2;ctx.stroke();
}

function makeGrain(doc){
  const tile=doc.createElement('canvas');tile.width=tile.height=72;const ctx=tile.getContext('2d');if(!ctx)return null;
  let seed=7121;for(let n=0;n<170;n++){seed=(seed*16807)%2147483647;const x=seed%72;seed=(seed*16807)%2147483647;const y=seed%72;ctx.fillStyle=n%2?'rgba(255,230,180,.12)':'rgba(119,58,16,.08)';ctx.fillRect(x,y,1,n%3?1:2);}
  return tile;
}
function drawArm(ctx,side,tip,grain){
  const {shoulder:s,wrist:c,curve:e}=armGuide(side,tip);
  ctx.save();ctx.lineCap='round';ctx.lineJoin='round';
  // One rounded quadratic stroke cannot form the intersecting ribbon edges of
  // the first contour experiment. The guide only controls its gentle bend.
  const path=()=>{ctx.beginPath();ctx.moveTo(...s);ctx.quadraticCurveTo(...e,c[0],c[1]-12);};
  const shade=ctx.createLinearGradient(s[0]-65,s[1]+15,s[0]+80,s[1]-15);
  shade.addColorStop(0,'#d9772c');shade.addColorStop(.38,'#f6a04b');shade.addColorStop(.70,'#f3913b');shade.addColorStop(1,'#db7428');
  ctx.shadowColor='rgba(112,55,20,.20)';ctx.shadowBlur=15;ctx.shadowOffsetY=8;
  path();ctx.strokeStyle=shade;ctx.lineWidth=106;ctx.stroke();ctx.shadowColor='transparent';ctx.shadowBlur=0;ctx.shadowOffsetY=0;
  if(grain&&ctx.createPattern){path();ctx.strokeStyle=ctx.createPattern(grain,'repeat');ctx.stroke();}
  const pawShade=ctx.createRadialGradient(c[0]-18,c[1]-22,5,c[0]+12,c[1]+15,72);pawShade.addColorStop(0,'#ffaf52');pawShade.addColorStop(.53,'#f79b42');pawShade.addColorStop(1,'#dd762a');
  ctx.beginPath();ctx.ellipse(c[0],c[1],PAW_X,PAW_Y,0,0,Math.PI*2);ctx.fillStyle=pawShade;ctx.fill();
  if(grain&&ctx.createPattern){ctx.fillStyle=ctx.createPattern(grain,'repeat');ctx.fill();}
  // The marks are short feline toe creases, not individually articulated fingers.
  ctx.strokeStyle='rgba(132,63,22,.66)';ctx.lineWidth=2.6;ctx.lineCap='round';
  for(const x of [-16,16]){ctx.beginPath();ctx.moveTo(c[0]+x,c[1]+24);ctx.quadraticCurveTo(c[0]+x+2,c[1]+32,c[0]+x,c[1]+38);ctx.stroke();}
  ctx.restore();
}

// UV mapping for one triangle. Source coordinates stay in the original image;
// the destination is the logical 1254-square stage, including its alpha edge.
export function triangleTransform(source,destination){
  const [[x0,y0],[x1,y1],[x2,y2]]=source;
  const denominator=x0*(y1-y2)+x1*(y2-y0)+x2*(y0-y1);
  if(Math.abs(denominator)<1e-8)return null;
  const coefficients=values=>[
    (values[0]*(y1-y2)+values[1]*(y2-y0)+values[2]*(y0-y1))/denominator,
    (values[0]*(x2-x1)+values[1]*(x0-x2)+values[2]*(x1-x0))/denominator,
    (values[0]*(x1*y2-x2*y1)+values[1]*(x2*y0-x0*y2)+values[2]*(x0*y1-x1*y0))/denominator,
  ];
  const [a,c,e]=coefficients(destination.map(p=>p[0])),[b,d,f]=coefficients(destination.map(p=>p[1]));
  return [a,b,c,d,e,f];
}

export function drawTexturedArm(ctx,side,tip,image,bounds){
  if(!image||!(image.naturalWidth??image.width))return false;
  const box=Array.isArray(bounds)?{x:bounds[0],y:bounds[1],width:bounds[2],height:bounds[3]}:bounds;
  if(!box||box.width<=0||box.height<=0)return false;
  const {shoulder,curve}=armGuide(side,tip),strips=24,width=box.worldWidth??125;
  const p0=shoulder,p1=[mix(shoulder[0],curve[0],.75),mix(shoulder[1],curve[1],.75)];
  // A vertical terminal tangent keeps the whole original paw pointing at its
  // actual key instead of rotating it sideways with the forearm.
  const p2=[tip[0],tip[1]-Math.min(95,Math.max(65,(tip[1]-shoulder[1])*.35))],p3=tip;
  function cubic(t){
    const u=1-t;
    return {point:[0,1].map(i=>u*u*u*p0[i]+3*u*u*t*p1[i]+3*u*t*t*p2[i]+t*t*t*p3[i]),tangent:[0,1].map(i=>3*u*u*(p1[i]-p0[i])+6*u*t*(p2[i]-p1[i])+3*t*t*(p3[i]-p2[i]))};
  }
  // Equal arc-length rows distribute a single image continuously along the
  // curve; nothing repeats and there is no upper/fore/paw image boundary.
  const arc=[{t:0,length:0}],steps=64;let previous=cubic(0).point,total=0;
  for(let n=1;n<=steps;n++){const p=cubic(n/steps).point;total+=Math.hypot(p[0]-previous[0],p[1]-previous[1]);arc.push({t:n/steps,length:total});previous=p;}
  const flip=box.flipX??side==='right',sign=flip?-1:1;
  const sourceLeft=box.x+(flip?box.width:0),sourceRight=box.x+(flip?0:box.width);
  const rootX=box.rootX??box.x+box.width/2,tipX=box.tipX??rootX;
  const rows=[];let segment=1;
  for(let n=0;n<=strips;n++){
    const fraction=n/strips,length=fraction*total;
    while(segment<steps&&arc[segment].length<length)segment++;
    const before=arc[segment-1],after=arc[segment];
    const t=length===0?0:mix(before.t,after.t,(length-before.length)/Math.max(1e-8,after.length-before.length));
    const {point,tangent}=cubic(t),norm=Math.hypot(...tangent),normal=[tangent[1]/norm,-tangent[0]/norm];
    const axis=mix(rootX,tipX,fraction),sourceY=box.y+fraction*box.height;
    const edge=x=>{const offset=(x-axis)*width/box.width*sign;return[point[0]+normal[0]*offset,point[1]+normal[1]*offset];};
    rows.push({source:[[sourceLeft,sourceY],[sourceRight,sourceY]],destination:[edge(sourceLeft),edge(sourceRight)]});
  }
  function triangle(source,destination){
    const transform=triangleTransform(source,destination);if(!transform)return;
    const center=[0,1].map(i=>(destination[0][i]+destination[1][i]+destination[2][i])/3);
    // Subpixel overlap hides AA hairlines between adjacent triangles. Only the
    // image's own RGBA is drawn, so the original silhouette remains transparent.
    const clip=destination.map(p=>{const distance=Math.hypot(p[0]-center[0],p[1]-center[1]);const expand=1+.35/Math.max(1,distance);return[center[0]+(p[0]-center[0])*expand,center[1]+(p[1]-center[1])*expand];});
    ctx.save();ctx.beginPath();ctx.moveTo(...clip[0]);ctx.lineTo(...clip[1]);ctx.lineTo(...clip[2]);ctx.closePath();ctx.clip();
    ctx.transform(...transform);ctx.drawImage(image,box.x,box.y,box.width,box.height,box.x,box.y,box.width,box.height);ctx.restore();
  }
  ctx.save();ctx.imageSmoothingEnabled=true;
  for(let n=0;n<strips;n++){
    const a=rows[n],b=rows[n+1];
    triangle([a.source[0],a.source[1],b.source[0]],[a.destination[0],a.destination[1],b.destination[0]]);
    triangle([a.source[1],b.source[1],b.source[0]],[a.destination[1],b.destination[1],b.destination[0]]);
  }
  ctx.restore();return true;
}

export function mountCharacter(scene){
  if(!scene?.ownerDocument)throw new TypeError('A scene element is required');if(mounted.has(scene))return mounted.get(scene);
  const doc=scene.ownerDocument,win=doc.defaultView,svg=scene.querySelector('svg.cat-scene');if(!svg)throw new Error('Character needs scene SVG');
  const canvas=doc.createElement('canvas');canvas.className='precise-cat-canvas';canvas.width=canvas.height=SIZE;canvas.hidden=true;
  canvas.setAttribute('role','img');canvas.setAttribute('aria-label','橘猫在八个白键和五个黑键前，随真实按键下压琴键');
  Object.assign(canvas.style,{position:'absolute',inset:'0',width:'100%',height:'calc(100% - 22px)',objectFit:'contain',pointerEvents:'none'});
  scene.insertBefore(canvas,scene.querySelector('.stage-readout'));
  const previous={display:svg.style.display,aspect:scene.style.aspectRatio};
  const reduced=win.matchMedia?.('(prefers-reduced-motion: reduce)');
  const state=createPianoState(()=>win.performance.now());
  let mode=scene.dataset.instrument??'piano',keys=[],loaded=false,destroyed=false,raf=0,rig=null,rigPromise=null,failed=false;
  const image=new win.Image(),armTexture=new win.Image();let context=null,grain=null,armLayers=null,textureAvailable=false;
  const textureReady=new Promise(resolve=>{armTexture.onload=()=>{textureAvailable=armTexture.naturalWidth>0;resolve(textureAvailable);};armTexture.onerror=()=>resolve(false);armTexture.src=ARM_TEXTURE;});
  function ensureRig(){
    if(!rigPromise)rigPromise=import('./character.js').then(module=>{if(destroyed)return null;rig=module.mountCharacter(scene);rig.update(mode,keys);return rig.ready.then(()=>{if(!destroyed)applyMode();return rig;});});
    return rigPromise;
  }
  function applyMode(){
    if(destroyed)return;const active=loaded&&mode==='piano'&&!failed;
    canvas.hidden=!active;svg.style.display=active?'none':previous.display;scene.style.aspectRatio=active?'1 / 1':previous.aspect;
    scene.toggleAttribute('data-precise-character',active);
    if(active){scene.dataset.character='precise-orange-piano-v2';request();}
    else{delete scene.dataset.pianoLeft;delete scene.dataset.pianoRight;delete scene.dataset.pianoHeld;}
  }
  function draw(){
    raf=0;if(destroyed||!loaded||mode!=='piano'||failed)return;
    const pose=state.sample();context.clearRect(0,0,SIZE,SIZE);context.drawImage(image,0,0,SIZE,SIZE);
    for(const code of WHITES)drawKey(context,pianoKeyGeometry(code,pose.keys[code]),pose.keys[code]);
    for(const code of BLACKS)drawKey(context,pianoKeyGeometry(code,pose.keys[code]),pose.keys[code]);
    try{for(const side of ['left','right']){const hand=pose.hands[side];const layer=armLayers[side],paint=layer.getContext('2d');paint.clearRect(0,0,SIZE,SIZE);if(!textureAvailable||!drawTexturedArm(paint,side,[hand.x,hand.y],armTexture,ARM_TEXTURE_BOUNDS))drawArm(paint,side,[hand.x,hand.y],grain);
      const shoulder=SHOULDERS[side],fade=paint.createRadialGradient(...shoulder,10,...shoulder,70);fade.addColorStop(0,'rgba(0,0,0,1)');fade.addColorStop(1,'rgba(0,0,0,0)');paint.save();paint.globalCompositeOperation='destination-out';paint.fillStyle=fade;paint.beginPath();paint.arc(...shoulder,70,0,Math.PI*2);paint.fill();paint.restore();context.drawImage(layer,0,0);scene.dataset[side==='left'?'pianoLeft':'pianoRight']=`${hand.code??'rest'}:${hand.x.toFixed(1)},${hand.y.toFixed(1)}`;}delete scene.dataset.characterWarning;}
    catch{scene.dataset.characterWarning='precise arm target unreachable';}
    scene.dataset.pianoHeld=pose.held.join(',');
    if(pose.needsFrame)raf=win.requestAnimationFrame(draw);
  }
  function request(){if(loaded&&mode==='piano'&&!failed&&!raf)raf=win.requestAnimationFrame(draw);}
  function reset(){state.reset();if(raf)win.cancelAnimationFrame(raf);raf=0;request();}
  const visibility=()=>{if(doc.hidden)reset();};
  win.addEventListener('blur',reset);doc.addEventListener('visibilitychange',visibility);reduced?.addEventListener?.('change',reset);
  const ready=new Promise((resolve,reject)=>{
    image.onload=async()=>{if(destroyed){resolve(false);return;}if(image.naturalWidth!==SIZE||image.naturalHeight!==SIZE){reject(new Error('Unexpected piano body dimensions'));return;}await textureReady;if(destroyed){resolve(false);return;}
      context=canvas.getContext('2d');if(!context){reject(new Error('Canvas unavailable'));return;}
      grain=makeGrain(doc);armLayers=Object.fromEntries(['left','right'].map(side=>{const layer=doc.createElement('canvas');layer.width=layer.height=SIZE;return[side,layer];}));loaded=true;applyMode();draw();resolve(true);
    };image.onerror=()=>reject(new Error('Piano body unavailable'));image.src=BODY;
  }).catch(async()=>{if(destroyed)return false;failed=true;scene.dataset.characterStatus='precise-piano-fallback';applyMode();await ensureRig();return false;});
  if(mode!=='piano')ensureRig().catch(()=>{});
  const controller={ready,atlas:BODY,
    update(next=mode,nextKeys=keys){
      if(destroyed)return;const changed=next!==mode;mode=next;keys=nextKeys;
      if(changed)reset();if(mode==='piano'&&!failed){state.update(keys);applyMode();request();}
      else{ensureRig().then(c=>c?.update(mode,keys)).catch(()=>{});applyMode();}
    },
    strike(key,next=mode){
      if(destroyed)return false;if(next!==mode){mode=next;reset();applyMode();}
      if(mode==='piano'&&!failed){if(!loaded)return false;const accepted=state.strike(key);request();return accepted;}
      // Loading a fallback instrument must never replay an old visual strike.
      if(rig)return rig.strike?.(key,next)??false;
      ensureRig().catch(()=>{});return false;
    },
    destroy(){if(destroyed)return;destroyed=true;if(raf)win.cancelAnimationFrame(raf);win.removeEventListener('blur',reset);doc.removeEventListener('visibilitychange',visibility);reduced?.removeEventListener?.('change',reset);rig?.destroy();canvas.remove();svg.style.display=previous.display;scene.style.aspectRatio=previous.aspect;scene.removeAttribute('data-precise-character');for(const name of ['pianoLeft','pianoRight','pianoHeld','characterWarning'])delete scene.dataset[name];if(scene.dataset.character==='precise-orange-piano-v2')delete scene.dataset.character;mounted.delete(scene);},
  };
  mounted.set(scene,controller);return controller;
}
