// Original orange musician. Fixed bone lengths, independent wrists, continuous strokes.
const SVG='http://www.w3.org/2000/svg',DRAW_SIZE=1280;
const ART=new URL('./character/orange-components-v3.png',import.meta.url).href;
const PROPS=new URL('./character/orange-instruments-v3.png',import.meta.url).href;
const GUITAR=new URL('./labs/orange-guitar/atlas-v1.png',import.meta.url).href;
const STYLES=new URL('./character/rig.css',import.meta.url).href;
const mounted=new WeakMap();
export const CHARACTER_LAYOUT=Object.freeze({
 left:{upper:{crop:[125,450,245,380],root:[275,515],end:[211,760]},fore:{crop:[545,530,205,300],root:[620,585],end:[670,770]},paw:{crop:[930,545,220,270],root:[1040,595],end:[1040,777]}},
 right:{upper:{crop:[120,840,250,370],root:[200,900],end:[280,1150]},fore:{crop:[535,900,210,310],root:[655,965],end:[604,1160]},paw:{crop:[935,925,225,290],root:[1060,990],end:[1035,1168]}},
 upperLength:68,foreLength:60,pawLength:32,stickLength:54,
});
const WHITE=['KeyA','KeyS','KeyD','KeyF','KeyG','KeyH','KeyJ','KeyK'];
const BLACK=['KeyW','KeyE','KeyT','KeyY','KeyU'];
const PIANO=Object.fromEntries([...WHITE.map((c,i)=>[c,[187+i*36,443]]),...BLACK.map((c,i)=>[c,[[211,250,319,357,395][i],398]])]);
const MARIMBA=Object.fromEntries([...WHITE.map((c,i)=>[c,[[193,226,258,289,320,351,383,416][i],428]]),...BLACK.map((c,i)=>[c,[[221,264,308,349,394][i],370]])]);
const DRUMS={kick:{side:'foot',point:[312,450]},snare:{side:'right',point:[427,385],angle:18},'closed-hat':{side:'left',point:[197,367],angle:-12},'open-hat':{side:'left',point:[197,367],angle:-12},'tom-low':{side:'left',point:[277,325],angle:12},'tom-high':{side:'right',point:[357,325],angle:35},crash:{side:'left',point:[210,285],angle:-30},ride:{side:'right',point:[427,300],angle:28}};
const VOICES=Object.keys(DRUMS);
const deg=r=>r*180/Math.PI,rad=d=>d*Math.PI/180;
export function shoulderFor(side,mode){return side==='left'?[245,310]:[395,310];}
function rotate([x,y],a){const c=Math.cos(rad(a)),s=Math.sin(rad(a));return [x*c-y*s,x*s+y*c];}
export function contactFor(key,mode='piano'){
 if(key.kind==='drum'){
  if(mode==='drums')return {...DRUMS[key.voice],surface:key.voice,stick:true};
  const i=Math.max(0,VOICES.indexOf(key.voice));return {side:'right',point:[437+(i%4)*17,368+Math.floor(i/4)*17],angle:0,...(mode==='marimba'?{tool:'mallet',toolLength:42}:{}),surface:'pad-'+key.voice};
 }
 if(mode==='guitar')return {side:'left',point:[304,364],angle:22,surface:'strings',fret:[458+(key.kind==='chord'?Number(key.key)*4:Math.max(0,(key.midi??60)-60)*1.5),283]};
 return {side:key.paw,point:(mode==='marimba'?MARIMBA:PIANO)[key.code],angle:0,...(mode==='marimba'?{tool:'mallet',toolLength:42}:{}),surface:key.code};
}
export function wristFor(contact){const offset=rotate([0,contact.toolLength??(contact.stick?CHARACTER_LAYOUT.stickLength:CHARACTER_LAYOUT.pawLength)],contact.angle??0);return [contact.point[0]-offset[0],contact.point[1]-offset[1]];}
export function solveArm(side,wrist,mode='piano'){
 const shoulder=shoulderFor(side,mode),[sx,sy]=shoulder,dx=wrist[0]-sx,dy=wrist[1]-sy,d=Math.hypot(dx,dy),l1=CHARACTER_LAYOUT.upperLength,l2=CHARACTER_LAYOUT.foreLength;
 if(!Number.isFinite(d)||d<Math.abs(l1-l2)+.01||d>l1+l2-.01)throw new RangeError('Instrument target is outside fixed arm reach');
 const bend=side==='left'||mode==='guitar'?1:-1;
 const a=Math.atan2(dy,dx)+bend*Math.acos(Math.max(-1,Math.min(1,(d*d+l1*l1-l2*l2)/(2*d*l1))));
 const elbow=[sx+Math.cos(a)*l1,sy+Math.sin(a)*l1];
 return {shoulder,elbow,wrist:[...wrist],upperAngle:deg(a),foreAngle:deg(Math.atan2(wrist[1]-elbow[1],wrist[0]-elbow[0]))};
}
function sourceTransform(spec,start,angle,length){const v=[spec.end[0]-spec.root[0],spec.end[1]-spec.root[1]],scale=length/Math.hypot(...v);return `translate(${start[0]}px,${start[1]}px) rotate(${angle-deg(Math.atan2(v[1],v[0]))}deg) scale(${scale}) translate(${-spec.root[0]}px,${-spec.root[1]}px)`;}
// Cubic interpolation carries the current velocity across retriggers instead of restarting a pose.
function tween(from,to,velocity,t,duration){const u=Math.max(0,Math.min(1,t/duration)),u2=u*u,u3=u2*u;return (2*u3-3*u2+1)*from+(u3-2*u2+u)*duration*velocity+(-2*u3+3*u2)*to;}
export function mountCharacter(scene){
 if(!scene?.querySelector)throw new TypeError('A scene element is required');if(mounted.has(scene))return mounted.get(scene);
 const svg=scene.querySelector('svg.cat-scene');if(!svg)throw new Error('Character needs scene SVG');
 const doc=scene.ownerDocument,win=doc.defaultView,el=(tag,attrs={})=>{const n=doc.createElementNS(SVG,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,String(v));return n;};
 const legacy=el('g',{class:'legacy-art'});for(const n of [...svg.children])if(n.tagName.toLowerCase()!=='defs')legacy.append(n);svg.append(legacy);svg.setAttribute('viewBox','0 0 640 550');svg.setAttribute('aria-label','橘猫乐手，跟着你的输入演奏');
 const root=el('g',{class:'orange-stage','data-character-props':'orange-stage',visibility:'hidden'});svg.append(root);
 const sprite=(url,crop,part)=>{const g=el('g',{'data-character-part':part}),v=el('svg',{x:crop[0],y:crop[1],width:crop[2],height:crop[3],viewBox:crop.join(' '),overflow:'hidden'});v.append(el('image',{href:url,width:DRAW_SIZE,height:DRAW_SIZE}));g.append(v);return g;};
 const place=(node,crop,box)=>node.setAttribute('transform',`translate(${box[0]} ${box[1]}) scale(${box[2]/crop[2]} ${box[3]/crop[3]}) translate(${-crop[0]} ${-crop[1]})`);
 root.append(el('ellipse',{cx:325,cy:511,rx:180,ry:10,fill:'#cfb596',opacity:.15}));
 const body=sprite(ART,[835,40,410,410],'body');place(body,[835,40,410,410],[165,175,310,310]);root.append(body);
 const arms={};for(const side of ['left','right']){const spec=CHARACTER_LAYOUT[side];arms[side]={upper:sprite(ART,spec.upper.crop,side+'Upper'),fore:sprite(ART,spec.fore.crop,side+'Fore'),paw:sprite(ART,spec.paw.crop,side+'Paw'),hand:el('g',{'data-joint':side+'Wrist'}),motion:null,state:null};root.insertBefore(arms[side].upper,body);}
 const props={piano:sprite(PROPS,[20,190,600,320],'keyboard'),marimba:sprite(PROPS,[640,110,610,420],'marimba'),guitar:sprite(GUITAR,[635,170,630,515],'guitar'),drums:sprite(PROPS,[5,600,700,560],'kit')};
 place(props.piano,[20,190,600,320],[130,332,360,192]);place(props.marimba,[640,110,610,420],[135,300,340,234]);place(props.guitar,[635,170,630,515],[175,195,378,309]);place(props.drums,[5,600,700,560],[140,250,350,280]);for(const p of Object.values(props))root.append(p);
 const bank=sprite(PROPS,[704,774,550,330],'rhythmBank');place(bank,[704,774,550,330],[421,350,90,54]);const bankStand=el('g',{class:'orange-bank-stand'});bankStand.append(el('path',{d:'M431 400v76m68-76v76m-74 0h15m52 0h14',stroke:'#b08a60','stroke-width':5,'stroke-linecap':'round'}));root.append(bankStand,bank);
 const pedal=el('g',{class:'orange-pedal'});pedal.append(el('path',{d:'M313 493v-43m-12 46h24',stroke:'#7d5539','stroke-width':5,'stroke-linecap':'round'}),el('circle',{cx:313,cy:450,r:6,fill:'#b6794b'}));root.append(pedal);
 for(const side of ['left','right']){const arm=arms[side];root.append(arm.fore);arm.hand.append(arm.paw);arm.stick=el('path',{class:'orange-stick',d:'M0 8V54',stroke:'#c59459','stroke-width':4,'stroke-linecap':'round'});arm.hand.append(arm.stick);arm.mallet=el('g',{class:'orange-mallet'});arm.mallet.append(el('path',{d:'M0 8V42',stroke:'#b78750','stroke-width':3.5,'stroke-linecap':'round'}),el('circle',{cx:0,cy:42,r:6,fill:'#e6c79c',stroke:'#bd905b','stroke-width':1}));arm.hand.append(arm.mallet);root.append(arm.hand);arm.paw.style.transform=sourceTransform(CHARACTER_LAYOUT[side].paw,[0,0],90,CHARACTER_LAYOUT.pawLength);}
 const head=el('g',{class:'orange-head'}),open=sprite(ART,[55,110,365,290],'openHead'),closed=sprite(ART,[470,110,365,290],'closedHead');place(open,[55,110,365,290],[240,81,170,135]);place(closed,[470,110,365,290],[240,81,170,135]);const nod=el('g',{class:'orange-head-nod'});nod.append(open,closed);head.append(nod);root.append(head);
 const contact=el('ellipse',{class:'orange-contact',rx:10,ry:3,fill:'#c27336',opacity:0});root.append(contact);
 const style=doc.createElement('link');style.rel='stylesheet';style.href=STYLES;const cssReady=new Promise((r,j)=>{style.onload=r;style.onerror=()=>j(new Error('Character styles unavailable'));});doc.head.append(style);
 const reduced=win.matchMedia?.('(prefers-reduced-motion: reduce)');let destroyed=false,loaded=false,mode=scene.dataset.instrument??'guitar',held=[],raf=0,lastTime=0,lastHit=-1e9,lastContact=null,gaze={x:0,y:0},kickUntil=0;
 const now=()=>win.performance.now();
 const rest=side=>mode==='guitar'?(side==='left'?{x:316,y:327,a:10}:{x:436,y:263,a:-55}):mode==='drums'?(side==='left'?{x:220,y:320,a:-18}:{x:405,y:315,a:18}):(side==='left'?{x:236,y:386,a:0}:{x:385,y:386,a:0});
 const poseFor=c=>{const p=wristFor(c);return{x:p[0],y:p[1],a:c.angle??0};};
 function sample(arm,time){
  const m=arm.motion;if(!m)return {...arm.state,vx:0,vy:0,va:0};
  const age=time-m.start;
  let from,to,v,part,duration;
  if(age<68){from=m.from;to=m.to;v=m.velocity;part=age;duration=68;}
  else if(age<115){return {...m.to,vx:0,vy:0,va:0};}
  else{from=m.to;to=m.end;v={x:0,y:0,a:0};part=age-115;duration=150;}
  const p={x:tween(from.x,to.x,v.x,part,duration),y:tween(from.y,to.y,v.y,part,duration),a:tween(from.a,to.a,v.a,part,duration)};
  const u=Math.max(0,Math.min(1,part/duration)),velocity=(a,b,s)=>(6*u*u-6*u)*(a-b)/duration+(3*u*u-4*u+1)*s;
  p.vx=velocity(from.x,to.x,v.x);p.vy=velocity(from.y,to.y,v.y);p.va=velocity(from.a,to.a,v.a);
  if(age>=265){arm.motion=null;p.vx=p.vy=p.va=0;}return p;
 }
 function drawArm(side,time){const arm=arms[side],p=sample(arm,time);arm.state=p;let solved;try{solved=solveArm(side,[p.x,p.y],mode);}catch{scene.dataset.characterWarning='unreachable target';return;}
  arm.upper.style.transform=sourceTransform(CHARACTER_LAYOUT[side].upper,solved.shoulder,solved.upperAngle,CHARACTER_LAYOUT.upperLength);arm.fore.style.transform=sourceTransform(CHARACTER_LAYOUT[side].fore,solved.elbow,solved.foreAngle,CHARACTER_LAYOUT.foreLength);arm.hand.style.transform=`translate(${p.x}px,${p.y}px) rotate(${p.a}deg)`;arm.hand.dataset.wrist=`${p.x.toFixed(2)},${p.y.toFixed(2)}`;arm.hand.dataset.elbow=solved.elbow.map(n=>n.toFixed(2)).join(',');arm.stick.style.display=mode==='drums'?'':'none';arm.mallet.style.display=mode==='marimba'?'':'none';
 }
 function render(time){raf=0;if(destroyed||!loaded)return;for(const side of ['left','right'])drawArm(side,time);
  const playing=time-lastHit<900;closed.style.opacity=mode==='guitar'&&playing?'1':'0';open.style.opacity=mode==='guitar'&&playing?'0':'1';
  const reaction=reduced?.matches?0:Math.max(0,1-(time-lastHit)/300);head.style.transform=`rotate(${gaze.x*1.5-reaction*.9}deg) translate(${gaze.x*1.2}px,${gaze.y*.7+reaction*.7}px)`;head.style.transformOrigin='325px 205px';
  pedal.style.display=mode==='drums'?'':'none';pedal.style.transform=mode==='drums'&&time<kickUntil?'rotate(-13deg)':'';pedal.style.transformOrigin='313px 496px';
  let touching=false;if(lastContact&&time-lastHit<130&&lastContact.side!=='foot'){const a=arms[lastContact.side].state,tip=rotate([0,lastContact.toolLength??(lastContact.stick?54:32)],a.a);touching=Math.hypot(a.x+tip[0]-lastContact.point[0],a.y+tip[1]-lastContact.point[1])<5;}
  contact.setAttribute('opacity',touching ? .25 : 0);scene.dataset.characterContact=touching?'true':'false';
  if(Object.values(arms).some(a=>a.motion)||playing||time<kickUntil)raf=win.requestAnimationFrame(render);lastTime=time;
 }
 const request=()=>{if(loaded&&!raf)raf=win.requestAnimationFrame(render);};
 function travel(side,to,end=to){const arm=arms[side],time=now(),from=sample(arm,time);if(reduced?.matches){arm.motion=null;arm.state={...to};request();return;}
  arm.motion={start:time,from,to,end,velocity:{x:Math.max(-.8,Math.min(.8,from.vx??0)),y:Math.max(-.8,Math.min(.8,from.vy??0)),a:Math.max(-.15,Math.min(.15,from.va??0))}};request();
 }
 function update(next=mode,keys=held){if(destroyed)return;const changed=next!==mode,previous=held;mode=next;held=keys;
  if(changed||!arms.left.state){for(const side of ['left','right']){arms[side].motion=null;arms[side].state={...rest(side)};}lastContact=null;delete scene.dataset.characterWarning;}
  for(const [name,p]of Object.entries(props))p.style.display=name===(mode==='marimba'?'marimba':mode)?'':'none';bank.style.display=mode==='drums'?'none':'';bankStand.style.display=mode==='drums'?'none':'';
  if(!changed&&(mode==='piano'||mode==='marimba'))for(const side of ['left','right']){
   const was=previous.filter(k=>contactFor(k,mode).side===side),current=keys.filter(k=>contactFor(k,mode).side===side);
   if(was.some(k=>!current.some(n=>n.code===k.code))){const arm=arms[side],nextPose=current.length?poseFor(contactFor(current.at(-1),mode)):rest(side);
    if(arm.motion&&now()-arm.motion.start<115)arm.motion.end=nextPose;else travel(side,nextPose,nextPose);
   }
  }
  request();
 }
 function strike(key,next=mode){if(destroyed||!loaded)return false;update(next,held);const c=contactFor(key,mode);lastHit=now();lastContact=c;scene.dataset.contactSurface=c.surface;contact.setAttribute('cx',c.point[0]);contact.setAttribute('cy',c.point[1]);if(c.side==='foot'){kickUntil=lastHit+160;request();return true;}
  const target=poseFor(c);let end=rest(c.side);
  if(mode==='drums')end={x:target.x,y:target.y-15,a:target.a-12};
  else if(mode==='guitar'&&key.kind!=='drum')end={x:target.x+4,y:target.y-17,a:target.a-12};
  else if(held.some(k=>k.code===key.code))end=target;
  travel(c.side,target,end);
  if(c.fret){const targetFret=poseFor({point:c.fret,angle:-55});travel('right',targetFret,targetFret);}
  request();return true;
 }
 const follow=e=>{if(reduced?.matches||e.pointerType==='touch')return;const r=scene.getBoundingClientRect();if(r.width&&r.height){gaze={x:Math.max(-1,Math.min(1,(e.clientX-r.left)/r.width*2-1)),y:Math.max(-1,Math.min(1,(e.clientY-r.top)/r.height*2-1))};request();}};
 const neutralLook=()=>{gaze={x:0,y:0};request();};
 const reset=()=>{held=[];lastContact=null;lastHit=-1e9;kickUntil=0;for(const side of ['left','right']){arms[side].motion=null;arms[side].state={...rest(side)};}neutralLook();if(raf)win.cancelAnimationFrame(raf);raf=0;if(loaded)render(now());};
 const visibility=()=>{if(doc.hidden)reset();};scene.addEventListener('pointermove',follow);scene.addEventListener('pointerleave',neutralLook);win.addEventListener('blur',reset);doc.addEventListener('visibilitychange',visibility);reduced?.addEventListener?.('change',reset);
 const loadImage=url=>new Promise((resolve,reject)=>{const im=new win.Image();im.onload=()=>im.naturalWidth>0?resolve():reject(new Error('Invalid character image'));im.onerror=()=>reject(new Error('Character image unavailable'));im.src=url;});
 let cancelLoad;const ready=Promise.race([Promise.all([cssReady,...[ART,PROPS,GUITAR].map(loadImage)]).then(()=>{if(destroyed)return false;loaded=true;scene.classList.add('orange-ready');root.setAttribute('visibility','visible');scene.dataset.character='orange-articulated-v3';update();render(now());return true;}),new Promise(r=>{cancelLoad=()=>r(false);})]);ready.catch(()=>{});
 const controller={ready,atlas:ART,strike,update,destroy(){if(destroyed)return;destroyed=true;cancelLoad();if(raf)win.cancelAnimationFrame(raf);scene.removeEventListener('pointermove',follow);scene.removeEventListener('pointerleave',neutralLook);win.removeEventListener('blur',reset);doc.removeEventListener('visibilitychange',visibility);reduced?.removeEventListener?.('change',reset);root.remove();style.remove();while(legacy.firstChild)svg.append(legacy.firstChild);legacy.remove();scene.classList.remove('orange-ready');delete scene.dataset.character;delete scene.dataset.characterWarning;mounted.delete(scene);}};mounted.set(scene,controller);return controller;
}
