// Whole-scene interpolation only. Each tile includes the cat, both paws and guitar.
export function validateGuitarMotionManifest(data){
  if(data?.version!==1||data.width!==640||data.height!==640||data.columns!==4||data.rows!==2||data.intermediates!==7||Object.keys(data.poses??{}).length!==18||data.edges?.length!==27)throw Error('Unexpected guitar motion manifest');
  const seen=new Set(),connected=new Set(['idle']);
  for(const edge of data.edges){if(!/^e\d{2}$/.test(edge.id)||edge.file!==edge.id+'.webp'||seen.has(edge.id)||!data.poses[edge.from]||!data.poses[edge.to]||edge.from===edge.to||!Number.isInteger(edge.bytes)||edge.bytes>2000000||!/^[a-f0-9]{64}$/.test(edge.sha256))throw Error('Invalid whole-scene transition');seen.add(edge.id);}
  for(let i=0;i<18;i++)for(const e of data.edges){if(connected.has(e.from))connected.add(e.to);if(connected.has(e.to))connected.add(e.from);}
  if(connected.size!==18)throw Error('Disconnected guitar poses');
  return data;
}

export function createGuitarMotion(config,now=()=>performance.now()){
  const graph=new Map(Object.keys(config.poses).map(id=>[id,[]]));
  for(const edge of config.edges){graph.get(edge.from).push({edge,to:edge.to});graph.get(edge.to).push({edge,to:edge.from});}
  let anchor='idle',target='idle',segments=[];
  function position(){
    const t=now();while(segments.length&&t>=segments[0].end){const s=segments.shift();if(s.to===0)anchor=s.edge.from;else if(s.to===1)anchor=s.edge.to;}
    if(!segments.length)return{pose:anchor,needsFrame:false};
    const s=segments[0],progress=Math.max(0,Math.min(1,(t-s.start)/(s.end-s.start))),phase=s.from+(s.to-s.from)*progress;
    return{edge:s.edge,phase,needsFrame:true};
  }
  // An input may use one direct transition, never a route through other notes.
  // When no reviewed direct edge exists, land at the actual target and make
  // one small recoil inside its own neighbourhood; never reach that neighbour.
  function recoil(id){
    const options=graph.get(id),edge=(options.find(s=>id.startsWith('Digit')?s.to==='idle':id.startsWith('Key')&&s.to.startsWith('Key'))??options[0]).edge;
    const end=edge.from===id?0:1,near=end===0?.25:.75;
    return[{edge,from:end,to:near},{edge,from:near,to:end}];
  }
  function schedule(to,pulse=false){
    if(!graph.has(to)||to===target&&!pulse)return;
    const p=position();let path=[];
    if(pulse){anchor=to;path=recoil(to);}
    else if(p.edge&&(p.edge.from===to||p.edge.to===to))path=[{edge:p.edge,from:p.phase,to:p.edge.from===to?0:1}];
    else{
      const direct=p.pose&&graph.get(p.pose).find(s=>s.to===to);
      if(direct)path=[{edge:direct.edge,from:direct.edge.from===p.pose?0:1,to:direct.edge.from===to?0:1}];
      else{anchor=to;if(to!=='idle')path=recoil(to);}
    }
    let time=now();
    segments=path.map(s=>{const start=time;time+=Math.max(8,Math.abs(s.to-s.from)*(to==='idle'?110:85));return{...s,start,end:time};});target=to;
  }
  return{
    go:to=>schedule(to),pulse:()=>schedule(target,true),
    reset(id='idle'){anchor=graph.has(id)?id:'idle';target=anchor;segments=[];},
    sample(){const p=position();if(p.pose)return p;const index=Math.round(p.phase*8);return index===0?{pose:p.edge.from,needsFrame:true}:index===8?{pose:p.edge.to,needsFrame:true}:{edge:p.edge.id,cell:index-1,phase:p.phase,needsFrame:true};},
    get target(){return target;},
  };
}
