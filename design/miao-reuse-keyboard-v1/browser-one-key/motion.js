// One held note, with a minimum complete attack for short clicks.
// Reversals start at the current position/velocity; no stroke queue or timers.
const time = value => {
  if (!Number.isFinite(value)) throw new TypeError('A finite time is required');
  return value;
};
export function createPressMotion({attackMs=60,returnMs=140,retriggerMs=30,retriggerAt=.67,releaseNotch=.4}={}) {
  let segment=null,held=false,value=0,velocity=0;
  function start(target,now,duration,phase) {
    segment={target,start:now,duration,phase,from:value,velocity};
  }
  function advance(now) {
    time(now);
    while(segment) {
      const s=segment,end=s.start+s.duration;
      if(now>=end) {
        value=s.target;velocity=0;segment=null;
        if(s.phase==='retrigger'){start(1,end,attackMs,'attack');continue;}
        if(s.phase==='attack'&&!held){start(0,end,returnMs,'return');continue;}
        break;
      }
      const t=Math.max(0,(now-s.start)/s.duration),t2=t*t,t3=t2*t;
      const raw=(2*t3-3*t2+1)*s.from+(t3-2*t2+t)*s.duration*s.velocity+(-2*t3+3*t2)*s.target;
      value=Math.max(0,Math.min(1,raw));
      velocity=((6*t2-6*t)*s.from+(3*t2-4*t+1)*s.duration*s.velocity+(-6*t2+6*t)*s.target)/s.duration;
      if(raw<0||raw>1)velocity=0;
      break;
    }
    return {amount:value,velocity,held,phase:segment?.phase||(held?'held':'ready'),needsFrame:!!segment};
  }
  return {
    press(now){advance(now);held=true;if(value>=retriggerAt)start(releaseNotch,now,retriggerMs,'retrigger');else start(1,now,attackMs,'attack');},
    release(now){advance(now);const wasHeld=held;held=false;if(wasHeld&&!['attack','retrigger'].includes(segment?.phase)&&value>0)start(0,now,returnMs,'return');},
    sample:advance,
    reset(now){time(now);held=false;value=velocity=0;segment=null;},
  };
}
