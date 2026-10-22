// The audio clock is the source of truth. Rendering never accumulates frame time.
export function guidePosition(events,elapsed,duration,bpm,meter,phaseBeats=0){
  const beatSeconds=60/bpm;
  if(elapsed<0)return {index:-1,next:0,progress:0,countIn:Math.ceil(-elapsed/beatSeconds),beat:0,bar:0};
  let low=0,high=events.length;
  while(low<high){const mid=(low+high)>>>1;if(events[mid].offset<=elapsed)low=mid+1;else high=mid;}
  const index=low-1,beat=Math.floor(elapsed/beatSeconds)+phaseBeats;
  return {index,next:low<events.length?low:-1,progress:Math.min(1,elapsed/duration),countIn:0,beat:beat%meter,bar:Math.floor(beat/meter)+1};
}
