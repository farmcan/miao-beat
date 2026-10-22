// Four independently transformed bitmap components. No model/runtime service.
const SVG='http://www.w3.org/2000/svg';
const ATLAS=new URL('./character/plush-atlas-v1.png',import.meta.url).href;
const SIZE=1254;
const mounted=new WeakMap();

const STYLES=new URL('./character/rig.css',import.meta.url).href;

// Coordinates use the host SVG's 640 x 300 viewBox, not viewport pixels.
// Head/body overlap hides the neck seam; head also covers upper forearm roots.
export const CHARACTER_LAYOUT=Object.freeze({
  body:{tile:[627,0,627,627],box:[204.8,47.8,233.1,233.1],anchor:[320,277]},
  head:{tile:[0,0,627,627],box:[184.7,-25.7,249.5,249.5],anchor:[320,177]},
  leftPaw:{tile:[0,627,627,627],box:[189.9,153.6,118.8,118.8],anchor:[223,185]},
  rightPaw:{tile:[627,627,627,627],box:[331.3,153.6,118.8,118.8],anchor:[417,185]},
});

export function mountCharacter(scene){
  if(!scene?.querySelector)throw new TypeError('A scene element is required');
  if(mounted.has(scene))return mounted.get(scene);
  const svg=scene.querySelector('svg.cat-scene');
  if(!svg)throw new Error('Character needs the existing 640x300 scene SVG');
  const doc=scene.ownerDocument,win=doc.defaultView;
  const element=(name,attrs={})=>{const node=doc.createElementNS(SVG,name);for(const [key,value]of Object.entries(attrs))node.setAttribute(key,String(value));return node;};
  const stylesheet=doc.createElement('link');stylesheet.rel='stylesheet';stylesheet.href=STYLES;
  const styleReady=new Promise((resolve,reject)=>{stylesheet.onload=()=>resolve(true);stylesheet.onerror=()=>reject(new Error('Character rig styles could not load'));});
  doc.head.append(stylesheet);
  const part=(name,className)=>{
    const spec=CHARACTER_LAYOUT[name],group=element('g',{class:'plush-character-part '+className,'data-character-part':name,'aria-hidden':'true',visibility:'hidden'});
    const [x,y,width,height]=spec.box;
    const crop=element('svg',{x,y,width,height,viewBox:spec.tile.join(' '),overflow:'hidden',preserveAspectRatio:'xMidYMid meet'});
    crop.append(element('image',{href:ATLAS,width:SIZE,height:SIZE,x:0,y:0}));group.append(crop);return group;
  };
  const body=part('body','plush-body-motion');
  const head=part('head','plush-head-gaze'),nod=element('g',{class:'plush-head-nod'});
  while(head.firstChild)nod.append(head.firstChild);head.append(nod);
  const left=part('leftPaw','plush-paw-left'),right=part('rightPaw','plush-paw-right');
  const firstProp=svg.querySelector('.scene-keyboard');
  svg.insertBefore(body,firstProp);
  const props=[...svg.querySelectorAll('.scene-keyboard,.scene-guitar,.scene-drums')];
  const front=props.at(-1)?.nextSibling??null;
  for(const node of [left,right,head])svg.insertBefore(node,front);

  let destroyed=false,raf=0,look={x:0,y:0};
  const pawAnimations={left:null,right:null};
  const reduced=win.matchMedia?.('(prefers-reduced-motion: reduce)');
  const renderLook=()=>{
    raf=0;if(destroyed)return;
    head.style.setProperty('--plush-look-x',(look.x*1.7).toFixed(3)+'px');
    head.style.setProperty('--plush-look-y',(look.y*.9).toFixed(3)+'px');
    head.style.setProperty('--plush-look-turn',(look.x*.85).toFixed(3)+'deg');
  };
  const queueLook=()=>{if(!raf)raf=win.requestAnimationFrame(renderLook);};
  const follow=event=>{
    if(reduced?.matches||event.pointerType==='touch')return;
    const rect=scene.getBoundingClientRect();if(!rect.width||!rect.height)return;
    look={x:Math.max(-1,Math.min(1,(event.clientX-rect.left)/rect.width*2-1)),y:Math.max(-1,Math.min(1,(event.clientY-rect.top)/rect.height*2-1))};queueLook();
  };
  const reset=()=>{look={x:0,y:0};queueLook();};
  scene.addEventListener('pointermove',follow);scene.addEventListener('pointerleave',reset);win.addEventListener('blur',reset);
  // Old vector anatomy stays visible until the real bitmap is decoded.
  const preload=new win.Image();
  const imageReady=new Promise((resolve,reject)=>{
    preload.onload=()=>{
      if(destroyed){resolve(false);return;}
      if(preload.naturalWidth!==SIZE||preload.naturalHeight!==SIZE){reject(new Error('Unexpected character atlas dimensions'));return;}
      resolve(true);
    };
    preload.onerror=()=>reject(new Error('The character atlas could not load'));
    preload.src=ATLAS;
  });
  let cancelLoad;
  const ready=Promise.race([Promise.all([styleReady,imageReady]).then(()=>{if(destroyed)return false;scene.classList.add('plush-ready');scene.dataset.character='plush-atlas-v1';return true;}),new Promise(resolve=>{cancelLoad=()=>resolve(false);})]);
  ready.catch(()=>{});
  const strike=side=>{
    if(destroyed||reduced?.matches||!scene.classList.contains('plush-ready')||!['left','right'].includes(side))return false;
    const paw=side==='left'?left:right;if(typeof paw.animate!=='function')return false;
    pawAnimations[side]?.cancel();
    const sign=side==='left'?1:-1;
    const animation=paw.animate([
      {transform:`translateY(-3px) rotate(${sign*2}deg)`,offset:0},
      {transform:`translate(${sign*3}px,8px) rotate(${-sign*5}deg)`,offset:.35},
      {transform:'translate(0,0) rotate(0)',offset:1},
    ],{duration:190,easing:'cubic-bezier(.2,.7,.2,1)',fill:'none'});
    pawAnimations[side]=animation;
    animation.onfinish=()=>{if(pawAnimations[side]===animation)pawAnimations[side]=null;};
    return true;
  };
  const controller={ready,atlas:ATLAS,strike,destroy(){
    if(destroyed)return;destroyed=true;cancelLoad();if(raf)win.cancelAnimationFrame(raf);
    for(const animation of Object.values(pawAnimations))animation?.cancel();
    scene.removeEventListener('pointermove',follow);scene.removeEventListener('pointerleave',reset);win.removeEventListener('blur',reset);
    scene.classList.remove('plush-ready');delete scene.dataset.character;
    for(const node of [body,head,left,right,stylesheet])node.remove();mounted.delete(scene);
  }};
  mounted.set(scene,controller);return controller;
}
