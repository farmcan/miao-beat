// Original four-part cat; artwork and instrument contact geometry are independent.
const SVG='http://www.w3.org/2000/svg';
const ATLAS=new URL('./character/indie-atlas-v2.png',import.meta.url).href;
const STYLES=new URL('./character/rig.css',import.meta.url).href;
const SIZE=1254,TILE=SIZE/2,mounted=new WeakMap();
export const CHARACTER_LAYOUT=Object.freeze({
 head:{tile:[0,0,TILE,TILE],box:[207,-14,232,232]},
 body:{tile:[TILE,0,TILE,TILE],box:[228,106,182,182]},
 leftPaw:{tile:[0,TILE,TILE,TILE],root:[.39*TILE,.19*TILE],tip:[.69*TILE,.83*TILE],shoulder:[258,184]},
 rightPaw:{tile:[TILE,TILE,TILE,TILE],root:[.63*TILE,.19*TILE],tip:[.29*TILE,.83*TILE],shoulder:[385,184]},
});
const NOTES={KeyA:[194,264],KeyS:[221,264],KeyD:[249,264],KeyF:[276,264],KeyG:[304,264],KeyH:[331,264],KeyJ:[359,264],KeyK:[388,264],KeyW:[208,252],KeyE:[235,252],KeyT:[290,252],KeyY:[317,252],KeyU:[344,252]};
const DRUMS={kick:{side:'foot',point:[320,278]},snare:{side:'right',point:[320,239]},'closed-hat':{side:'left',point:[181,223]},'open-hat':{side:'left',point:[181,223]},'tom-low':{side:'left',point:[278,221]},'tom-high':{side:'right',point:[362,221]},crash:{side:'left',point:[139,201]},ride:{side:'right',point:[451,222]}};
const VOICES=Object.keys(DRUMS);
export function contactFor(key,instrument='piano'){
 if(key.kind==='drum'){
  if(instrument==='drums')return {...DRUMS[key.voice],surface:key.voice};
  const i=Math.max(0,VOICES.indexOf(key.voice));
  return {side:'right',point:[440+(i%4)*21,246+Math.floor(i/4)*18],surface:'pad-'+key.voice};
 }
 if(instrument==='guitar')return {side:'left',point:[236,259],surface:'strings',fret:[354+(key.kind==='chord'?Number(key.key)*5:Math.max(0,(key.midi??60)-60)*2),233]};
 return {side:key.paw,point:NOTES[key.code]??[key.paw==='left'?235:365,264],surface:key.code};
}
// Maps a fixed source shoulder and toe to their corresponding stage points.
export function pawTransform(side,point){
 const spec=CHARACTER_LAYOUT[side==='left'?'leftPaw':'rightPaw'];
 const [rx,ry]=spec.root,[tx,ty]=spec.tip,[sx,sy]=spec.shoulder;
 const ux=tx-rx,uy=ty-ry,vx=point[0]-sx,vy=point[1]-sy,d=ux*ux+uy*uy;
 const a=(ux*vx+uy*vy)/d,b=(ux*vy-uy*vx)/d;
 return `matrix(${a},${b},${-b},${a},${sx-a*rx+b*ry},${sy-b*rx-a*ry})`;
}
export function mountCharacter(scene){
 if(!scene?.querySelector)throw new TypeError('A scene element is required');
 if(mounted.has(scene))return mounted.get(scene);
 const svg=scene.querySelector('svg.cat-scene');if(!svg)throw new Error('Character needs the scene SVG');
 const doc=scene.ownerDocument,win=doc.defaultView;
 const el=(name,attrs={})=>{const n=doc.createElementNS(SVG,name);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));return n;};
 const style=doc.createElement('link');style.rel='stylesheet';style.href=STYLES;
 const cssReady=new Promise((resolve,reject)=>{style.onload=()=>resolve(true);style.onerror=()=>reject(new Error('Character styles unavailable'));});doc.head.append(style);
 const part=(name,classes)=>{
  const spec=CHARACTER_LAYOUT[name],g=el('g',{class:'plush-character-part '+classes,'data-character-part':name,'aria-hidden':'true',visibility:'hidden'});
  const [x,y,w,h]=spec.box??[0,0,TILE,TILE],crop=el('svg',{x,y,width:w,height:h,viewBox:spec.tile.join(' '),overflow:'hidden'});
  crop.append(el('image',{href:ATLAS,width:SIZE,height:SIZE}));g.append(crop);return g;
 };
 const body=part('body','plush-body-motion'),head=part('head','plush-head-gaze'),nod=el('g',{class:'plush-head-nod'});
 while(head.firstChild)nod.append(head.firstChild);head.append(nod);
 const paws={left:part('leftPaw','plush-paw-left'),right:part('rightPaw','plush-paw-right')};
 svg.insertBefore(body,svg.querySelector('.scene-keyboard'));
 const drums=svg.querySelector('.scene-drums'),additions=el('g',{'data-character-props':'contact-kit'});
 additions.append(el('path',{d:'M139 203v72',stroke:'#525a62','stroke-width':3}),el('ellipse',{cx:139,cy:201,rx:30,ry:6,fill:'#d1ac67',stroke:'#333b47','stroke-width':2}),el('path',{d:'M294 239v16q26 14 52 0v-16',fill:'#566987',stroke:'#333b47','stroke-width':2}),el('ellipse',{cx:320,cy:239,rx:26,ry:8,fill:'#f1eee4',stroke:'#333b47','stroke-width':2}));
 const hatTop=drums.querySelector('ellipse[cx="181"]');hatTop.classList.add('hi-hat-top');const hatBottom=el('ellipse',{cx:181,cy:227,rx:44,ry:5,fill:'#b39252',stroke:'#333b47','stroke-width':2});drums.insertBefore(hatBottom,hatTop);
 const pedal=el('g',{class:'kick-pedal'});pedal.append(el('path',{d:'M320 296v-18m-11 19h22',stroke:'#333b47','stroke-width':4,'stroke-linecap':'round'}),el('circle',{cx:320,cy:278,r:5,fill:'#d96340'}));additions.append(pedal);drums.append(additions);
 const bank=el('g',{class:'scene-rhythm-bank','aria-hidden':'true'});
 bank.append(el('rect',{x:426,y:233,width:92,height:47,rx:7,fill:'#343d50',stroke:'#242a37','stroke-width':2}));
 VOICES.forEach((voice,i)=>bank.append(el('rect',{'data-rhythm-pad':voice,x:432+(i%4)*21,y:239+Math.floor(i/4)*18,width:16,height:14,rx:3,fill:i<4?'#b8c9c4':'#d2b37a'})));
 svg.append(bank);for(const p of Object.values(paws))svg.append(p);
 const sticks={};for(const side of ['left','right']){const g=el('g',{class:'cat-drumstick','data-stick':side,display:'none'});g.append(el('path',{d:'M0 0 17 32',stroke:'#e7bc80','stroke-width':5,'stroke-linecap':'round'}));sticks[side]=g;svg.append(g);}
 const contact=el('circle',{class:'cat-contact',opacity:0,r:7,fill:'none',stroke:'#d96340','stroke-width':2});svg.append(contact,head);
 let destroyed=false,instrument=scene.dataset.instrument??'piano',held=[],raf=0,look={x:0,y:0},contactTimer=0;
 const animations={left:null,right:null},stickAnimations={left:null,right:null},reduced=win.matchMedia?.('(prefers-reduced-motion: reduce)');
 const resting=()=>instrument==='guitar'?{left:[232,247],right:[373,231]}:instrument==='drums'?{left:[253,201],right:[370,201]}:{left:[236,254],right:[360,254]};
 const setPaw=(side,point)=>{paws[side].style.transform=pawTransform(side,point);paws[side].dataset.contact=point.join(',');};
 const placeStick=(side,point)=>{sticks[side].style.transform=`translate(${point[0]-17}px,${point[1]-32}px)`;};
 const cancel=()=>{for(const side of ['left','right']){animations[side]?.cancel();animations[side]=null;stickAnimations[side]?.cancel();stickAnimations[side]=null;}};
 function update(mode=instrument,keys=held){
  if(destroyed)return;const changed=mode!==instrument;instrument=mode;held=keys;
  if(changed){cancel();scene.classList.remove('cat-kick');delete scene.dataset.hat;}
  const targets=resting();
  for(const key of keys){const c=contactFor(key,instrument);if(c.side!=='foot')targets[c.side]=instrument==='drums'?[c.point[0]-17,c.point[1]-32]:c.point;if(c.fret)targets.right=c.fret;}
  for(const side of ['left','right']){setPaw(side,targets[side]);placeStick(side,instrument==='drums'?[targets[side][0]+17,targets[side][1]+32]:targets[side]);}
 }
 function strike(key,mode=instrument){
  if(destroyed||!scene.classList.contains('plush-ready'))return false;
  update(mode,held);const c=contactFor(key,mode);scene.dataset.contactSurface=c.surface;if(key.voice==='open-hat')scene.dataset.hat='open';if(key.voice==='closed-hat')scene.dataset.hat='closed';
  contact.setAttribute('cx',c.point[0]);contact.setAttribute('cy',c.point[1]);contact.classList.add('visible');
  win.clearTimeout(contactTimer);contactTimer=win.setTimeout(()=>contact.classList.remove('visible'),130);
  if(c.side==='foot'){scene.classList.remove('cat-kick');void pedal.getBoundingClientRect();scene.classList.add('cat-kick');return true;}
  const side=c.side,node=paws[side],drumming=mode==='drums',touch=drumming?[c.point[0]-17,c.point[1]-32]:c.point;
  const contactPose=pawTransform(side,touch),rebound=pawTransform(side,[touch[0]+(mode==='guitar'?3:0),touch[1]-(mode==='guitar'?12:10)]);
  animations[side]?.cancel();stickAnimations[side]?.cancel();if(c.fret)setPaw('right',c.fret);
  if(reduced?.matches||typeof node.animate!=='function'){setPaw(side,touch);if(drumming)placeStick(side,c.point);return true;}
  // Contact first: sound never waits for an anticipation pose. Endpoint follows live held input.
  const animation=node.animate([{transform:contactPose,offset:0},{transform:contactPose,offset:.12},{transform:rebound,offset:.55},{offset:1}],{duration:150,easing:'linear',fill:'none'});
  animations[side]=animation;
  if(drumming&&typeof sticks[side].animate==='function')stickAnimations[side]=sticks[side].animate([{transform:`translate(${touch[0]}px,${touch[1]}px)`,offset:0},{transform:`translate(${touch[0]}px,${touch[1]}px)`,offset:.12},{transform:`translate(${touch[0]}px,${touch[1]-10}px)`,offset:.55},{offset:1}],{duration:150,easing:'linear',fill:'none'});
  animation.onfinish=()=>{if(animations[side]===animation){animations[side]=null;stickAnimations[side]=null;update();}};return true;
 }
 const renderLook=()=>{raf=0;if(destroyed)return;head.style.setProperty('--plush-look-x',(look.x*1.4)+'px');head.style.setProperty('--plush-look-y',(look.y*.7)+'px');head.style.setProperty('--plush-look-turn',(look.x*.7)+'deg');};
 const queueLook=()=>{if(!raf)raf=win.requestAnimationFrame(renderLook);};
 const follow=e=>{if(reduced?.matches||e.pointerType==='touch')return;const r=scene.getBoundingClientRect();if(!r.width||!r.height)return;look={x:Math.max(-1,Math.min(1,(e.clientX-r.left)/r.width*2-1)),y:Math.max(-1,Math.min(1,(e.clientY-r.top)/r.height*2-1))};queueLook();};
 const resetLook=()=>{look={x:0,y:0};queueLook();};
 const reset=()=>{cancel();held=[];update();resetLook();scene.classList.remove('cat-kick');};
 const preference=()=>{if(reduced?.matches){cancel();look={x:0,y:0};if(raf)win.cancelAnimationFrame(raf);renderLook();update();}};
 reduced?.addEventListener?.('change',preference);scene.addEventListener('pointermove',follow);scene.addEventListener('pointerleave',resetLook);win.addEventListener('blur',reset);
 const visibility=()=>{if(doc.hidden)reset();};doc.addEventListener('visibilitychange',visibility);
 const preload=new win.Image();const imageReady=new Promise((resolve,reject)=>{preload.onload=()=>preload.naturalWidth===SIZE&&preload.naturalHeight===SIZE?resolve(true):reject(new Error('Unexpected atlas dimensions'));preload.onerror=()=>reject(new Error('Character image unavailable'));preload.src=ATLAS;});
 let cancelLoad;const ready=Promise.race([Promise.all([cssReady,imageReady]).then(()=>{if(destroyed)return false;scene.classList.add('plush-ready');scene.dataset.character='indie-atlas-v2';update();return true;}),new Promise(resolve=>{cancelLoad=()=>resolve(false);})]);ready.catch(()=>{});
 const controller={ready,atlas:ATLAS,strike,update,destroy(){if(destroyed)return;destroyed=true;cancelLoad();cancel();win.clearTimeout(contactTimer);if(raf)win.cancelAnimationFrame(raf);reduced?.removeEventListener?.('change',preference);scene.removeEventListener('pointermove',follow);scene.removeEventListener('pointerleave',resetLook);win.removeEventListener('blur',reset);doc.removeEventListener('visibilitychange',visibility);for(const n of [body,head,...Object.values(paws),...Object.values(sticks),contact,additions,hatBottom,bank,style])n.remove();scene.classList.remove('plush-ready','cat-kick');hatTop.classList.remove('hi-hat-top');delete scene.dataset.character;delete scene.dataset.hat;mounted.delete(scene);}};
 mounted.set(scene,controller);return controller;
}
