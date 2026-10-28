// Every selected tile is one complete Blender scene. The cycle only advances
// forwards: a retry never rewinds the recovery through the strings.
export function createBlenderMotion({frames=24,contactFrame=2,fps=60,holdMs=24}={},now=()=>performance.now()){
 if(!Number.isInteger(frames)||frames<4||!Number.isInteger(contactFrame)||contactFrame<1||contactFrame>=frames-1||!Number.isFinite(fps)||fps<1)throw Error('Invalid Blender motion timing');
 let value=0,segment=null,code='KeyA',speed=1,serial=0,contacts=0,merged=0,phase='ready',pending=null,urgent=false,waitingForPaint=false,cycle=0;
 const end=frames-1,smooth=t=>t*t*(3-2*t),freshMs=180;
 function begin(to,duration,next,at){segment={from:value,to,start:at,duration:Math.max(1,duration/speed),next};}
 function attack(at){phase='attack';cycle++;waitingForPaint=false;begin(contactFrame,contactFrame*1000/fps,'contact',at);}
 function update(at=now()){
  for(let i=0;segment&&i<8;i++){
   const s=segment,t=Math.max(0,Math.min(1,(at-s.start)/s.duration));value=s.from+(s.to-s.from)*smooth(t);
   if(t<1)break;
   const stop=s.start+s.duration;segment=null;
   if(s.next==='contact'){phase='contact';value=contactFrame;waitingForPaint=true;break;}
   else if(s.next==='recover'){
    phase='return';urgent=!!pending;begin(end,(end-contactFrame)*1000/fps/(urgent?3:1),'ready',stop);
   }else{
    phase='ready';value=0;urgent=false;
    // The end frame is authored identically to ready. This is the sole wrap.
    // An old request must not cause a surprise stroke after a stall.
    const next=pending;pending=null;
    if(next&&at-next.at<=freshMs/speed){code=next.code;attack(stop);}
   }
  }
  return {frame:Math.max(0,Math.min(end,Math.round(value))),position:value,phase,code,serial,contacts,merged,pending:!!pending,cycle,waitingForPaint,active:phase!=='ready'};
 }
 return {
  strike(next){const at=now();update(at);serial++;
   // Input during an unfinished attack shares its upcoming contact. Keeping a
   // second request here would turn a press burst into a delayed motion queue.
   if(phase==='attack'){code=next;merged++;return false;}
   if(phase==='ready'){code=next;attack(at);return true;}
   const replaced=!!pending;pending={code:next,at};if(replaced)merged++;
   if(phase==='return'&&!urgent){
    // Finish the existing clearance route, at most 3x its remaining speed.
    // Repeated input cannot compound that acceleration or jump to a pose.
    urgent=true;const remaining=Math.max(1,segment.start+segment.duration-at);segment={...segment,from:value,start:at,duration:remaining/3};
   }
   return !replaced;
  },
  sample:update,
  contactPainted(id){if(!waitingForPaint||phase!=='contact'||id!==cycle)return false;waitingForPaint=false;contacts++;begin(contactFrame,holdMs,'recover',now());return true;},
  setSpeed(next){if(next!==1&&next!==.5)throw Error('Invalid preview speed');const at=now();update(at);if(segment){const left=Math.max(1,segment.start+segment.duration-at)*speed/next;segment={...segment,from:value,start:at,duration:left};}speed=next;},
  reset(){segment=null;phase='ready';value=0;pending=null;urgent=false;waitingForPaint=false;},
 };
}
