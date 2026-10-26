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
  function route(from,to){
    const queue=[[from,[]]],seen=new Set([from]);
    for(const[id,path]of queue){if(id===to)return path;for(const step of graph.get(id)??[])if(!seen.has(step.to)){seen.add(step.to);queue.push([step.to,[...path,{edge:step.edge,from:step.edge.from===id?0:1,to:step.edge.from===id?1:0}]]);}}
    return[];
  }
  function schedule(to,pulse=false){
    if(!graph.has(to)||to===target&&!pulse)return;
    const p=position(),path=[];let at=p.pose,time=now();
    if(p.edge){const end=p.phase<.5?0:1;at=end===0?p.edge.from:p.edge.to;path.push({edge:p.edge,from:p.phase,to:end});}
    path.push(...route(at,to));
    if(pulse&&!path.length){const e=graph.get(to)[0].edge,end=e.from===to?0:1;path.push({edge:e,from:end,to:end===0?.25:.75},{edge:e,from:end===0?.25:.75,to:end});}
    const weight=path.reduce((sum,s)=>sum+Math.abs(s.to-s.from),0),perEdge=Math.min(to==='idle'?150:75,Math.max(15,(to==='idle'?200:170)/Math.max(weight,1)));
    segments=path.map(s=>{const start=time;time+=Math.max(8,Math.abs(s.to-s.from)*perEdge);return{...s,start,end:time};});target=to;
  }
  return{
    go:to=>schedule(to),pulse:()=>schedule(target,true),
    reset(id='idle'){anchor=graph.has(id)?id:'idle';target=anchor;segments=[];},
    sample(){const p=position();if(p.pose)return p;const index=Math.round(p.phase*8);return index===0?{pose:p.edge.from,needsFrame:true}:index===8?{pose:p.edge.to,needsFrame:true}:{edge:p.edge.id,cell:index-1,phase:p.phase,needsFrame:true};},
    get target(){return target;},
  };
}
