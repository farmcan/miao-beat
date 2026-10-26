// Whole-scene interpolation only. Each tile includes the cat, both paws and guitar.
export function validateGuitarMotionManifest(data){
  if(data?.version!==1||data.width!==640||data.height!==640||data.columns!==4||data.rows!==2||data.intermediates!==7||Object.keys(data.poses??{}).length!==18||data.edges?.length!==27)throw Error('Unexpected guitar motion manifest');
  const seen=new Set(),connected=new Set(['idle']);
  for(const edge of data.edges){if(!/^e\d{2}$/.test(edge.id)||edge.file!==edge.id+'.webp'||seen.has(edge.id)||!data.poses[edge.from]||!data.poses[edge.to]||edge.from===edge.to||!Number.isInteger(edge.bytes)||edge.bytes>2000000||!/^[a-f0-9]{64}$/.test(edge.sha256))throw Error('Invalid whole-scene transition');seen.add(edge.id);}
  for(let i=0;i<18;i++)for(const e of data.edges){if(connected.has(e.from))connected.add(e.to);if(connected.has(e.to))connected.add(e.from);}
  if(connected.size!==18)throw Error('Disconnected guitar poses');
  return data;
}

export const GUITAR_PLUCK_IDS=['KeyA','KeyS','KeyD','KeyF','KeyW','KeyE','KeyG','KeyH','KeyJ','KeyK','KeyT','KeyY','KeyU','Digit1','Digit2','Digit3','Digit4'];
export function validateGuitarPluckManifest(data){
  if(data?.version!==1||data.width!==1254||data.height!==1254||data.tileSize!==640||data.columns!==4||data.rows!==2||data.intermediates!==7||Object.keys(data.clips??{}).length!==17)throw Error('Unexpected guitar pluck manifest');
  for(const code of GUITAR_PLUCK_IDS){const c=data.clips[code];if(c?.up?.file!==code+'-up.jpg'||c?.atlas?.file!==code+'.webp'||c?.down?.file!=='character/instrument-scenes-v1/guitar/'+code+'.jpg')throw Error('Missing complete pluck pair: '+code);for(const e of [c.up,c.down,c.atlas])if(!Number.isInteger(e.bytes)||e.bytes<=0||e.bytes>2000000||!/^[a-f0-9]{64}$/.test(e.sha256))throw Error('Invalid pluck provenance');}
  return data;
}

// A confirmed sound starts one right-paw cycle at the selected, fixed fret.
// No change of target/held state can silently replace that cycle with a fret tour.
export function createGuitarMotion(config,now=()=>performance.now()){
  let code='KeyA',started=null,serial=0;
  return{
    strike(next){if(!config.clips[next])return false;code=next;started=now();serial++;return true;},
    reset(next){code=config.clips[next]?next:'KeyA';started=null;},
    sample(){
      if(!code)return{pose:'idle',code:null,serial,phase:'rest',needsFrame:false};
      const elapsed=started===null?Infinity:Math.max(0,now()-started);
      // Put the contact on the first paint; recovery supplies the smooth visible lift.
      const amount=elapsed<48?1:elapsed<152?1-(elapsed-48)/104:0;
      const frame=Math.round(amount*8),phase=frame===8?'contact':elapsed>=152?'ready':'return';
      const p={code,serial,phase,needsFrame:elapsed<152};
      return frame===0?{...p,pose:'up'}:frame===8?{...p,pose:'down'}:{...p,cell:frame-1};
    },
    get target(){return code??'idle';},
  };
}
