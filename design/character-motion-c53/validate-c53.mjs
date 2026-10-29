import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {createContactMotion} from '../character-motion-v2/contact-motion.mjs';
import {createContactMotionC53,evaluateSegment} from './contact-motion-c53.mjs';
const oldDir=new URL('../character-motion-v2/',import.meta.url), out=new URL('./evidence/',import.meta.url);
const profile=JSON.parse(fs.readFileSync(new URL('evidence/c35-rig-profile.json',oldDir)));
const maxdiff=(a,b)=>Math.max(...a.map((x,i)=>Math.abs(x-b[i])));
const sub=(a,b)=>a.map((x,i)=>x-b[i]);
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const scale=(a,t)=>a.map(x=>x*t);
const events=Array.from({length:8},(_,noteIndex)=>({mode:'melody',noteIndex}));
for(let a=1;a<=6;a++)for(let b=a;b<=6;b++)events.push({mode:'chord',sourceStrings:Array.from({length:b-a+1},(_,i)=>a+i)});
const singleA=events[0],singleB=events[7],full={mode:'chord',sourceStrings:[1,2,3,4,5,6]},partial={mode:'chord',sourceStrings:[2,3,4]};
const traces=[],joins=[];
let maxJoinPositionError=0,maxJoinVelocityError=0,maxFiniteVelocityDifference=0,finiteChecks=0,acceptedInterrupts=0,limitedInterrupts=0;
const slim=(m,t)=>{const {right}=m.sample(t);return {timeMs:t,right};};
function planChecks(plan){
  for(let i=1;i<plan.segments.length;i++){
    const a=plan.segments[i-1],b=plan.segments[i];
    const end=evaluateSegment(a,a.b),begin=evaluateSegment(b,b.a);
    assert.equal(a.b,b.a);assert.ok(maxdiff(end.world,begin.world)<1e-14);
    assert.ok(maxdiff(end.velocityWorldPerMs,begin.velocityWorldPerMs)<1e-14);
  }
  assert.ok(maxdiff(plan.segments.at(-1).q,profile.strike.rest_world)===0);
}
function sampleTimeline(eventsWithTimes,label){
  const m=createContactMotionC53(profile), frames=[],receipts=[];
  let prior=-1;
  for(let i=0;i<eventsWithTimes.length;i++){
    const {event,timeMs}=eventsWithTimes[i];
    const end=eventsWithTimes[i+1]?.timeMs ?? timeMs+140;
    const before=m.sample(timeMs).right,receipt=m.trigger(event,timeMs),after=m.sample(timeMs).right;
    assert.equal(receipt.accepted,true);assert.equal(receipt.queued,0);
    assert.ok(maxdiff(before.world,after.world)<1e-14);assert.ok(maxdiff(before.velocityWorldPerMs,after.velocityWorldPerMs)<1e-14);
    const plan=m.inspectPlan();planChecks(plan);receipts.push({event,timeMs,...receipt});
    const ts=new Set([timeMs,end]);
    for(let t=timeMs;t<=end;t+=.25)ts.add(t);
    // Include exact knots plus local micro-samples around adaptive braking.
    for(const s of plan.segments){
      for(const t of [s.a,s.b,(s.a+s.b)/2])if(timeMs+t<=end)ts.add(timeMs+t);
      if(s.phase==='brake')for(let k=0;k<=16;k++)if(timeMs+s.b*k/16<=end)ts.add(timeMs+s.b*k/16);
    }
    for(const t of [...ts].sort((a,b)=>a-b)){
      if(i<eventsWithTimes.length-1&&t===end)continue;
      if(t<=prior)continue;
      const f=slim(m,t); frames.push(f);prior=t;
      const current=m.sample(t);assert.equal(current.queueLength,0);
      assert.deepEqual(current.left.worldAnchors,profile.left_hold.anchors.map(a=>a.world));
    }
  }
  assert.equal(frames.at(-1).right.phase,'rest');
  const trace={label,events:receipts,frames};traces.push(trace);return trace;
}

// Every melody and every contiguous chord independently: one forward sweep,
// selected strings once, unselected strings zero, no return sweep or queue.
const uninterrupted=[];
for(const [i,event] of events.entries()){
  const trace=sampleTimeline([{event,timeMs:0}],`uninterrupted-${i}`);
  const sweep=trace.frames.filter(f=>f.right.phase==='sweep');
  const desired=event.mode==='melody'?[profile.note_targets.melody[event.noteIndex].source_string_index]:event.sourceStrings;
  const crossings=profile.strike.strings.map(r=>{
    let seenNegative=false,count=0;
    for(const f of sweep){const d=dot(sub(f.right.world,r.surface_world),profile.strike.cross_axis_world);
      if(d < -1e-10)seenNegative=true;
      if(d>1e-10&&seenNegative){count++;seenNegative=false;}
    }
    assert.equal(count,desired.includes(r.source_index)?1:0);
    return {sourceString:r.source_index,count};
  });
  uninterrupted.push({event,crossings});
}

const boundaryTimes=[0,10,30,45,70,85,100,139];
const pairs=[[singleA,singleB],[singleB,singleA],[full,singleA],[singleA,full]];
for(const [oldEvent,newEvent]of pairs)for(const at of boundaryTimes)
  sampleTimeline([{event:oldEvent,timeMs:0},{event:newEvent,timeMs:at}],`boundary-${pairs.indexOf(pairs.find(p=>p[0]===oldEvent&&p[1]===newEvent))}-${at}`);

// Interior interruptions at every integer millisecond, every melody and full
// chord, redirected to different string/chord choices. Exact p/v continuity is
// checked analytically; an independent finite difference probes both sides.
for(const oldEvent of [...events.slice(0,8),full])for(const newEvent of [singleA,singleB,full,partial])for(let at=0;at<140;at++){
  const m=createContactMotionC53(profile);m.trigger(oldEvent,0);
  const eps=1e-6,before=m.sample(at).right,left=m.sample(at-eps).right;
  const receipt=m.trigger(newEvent,at),after=m.sample(at).right;
  maxJoinPositionError=Math.max(maxJoinPositionError,maxdiff(before.world,after.world));
  maxJoinVelocityError=Math.max(maxJoinVelocityError,maxdiff(before.velocityWorldPerMs,after.velocityWorldPerMs));
  assert.ok(maxdiff(before.world,after.world)<1e-14);assert.ok(maxdiff(before.velocityWorldPerMs,after.velocityWorldPerMs)<1e-14);
  if(receipt.accepted){acceptedInterrupts++;planChecks(m.inspectPlan());
    const brake=m.inspectPlan().segments.find(s=>s.phase==='brake');
    if(brake){
      // Below the clearance rail the braking segment must not cross another
      // string coordinate; above it, projected crossings are harmless travel.
      const h=Math.min(dot(brake.p,profile.strike.normal_world),dot(brake.q,profile.strike.normal_world));
      const top=Math.max(...profile.strike.strings.map(r=>dot(r.surface_world,profile.strike.normal_world)));
      if(h<top+.025)for(const r of profile.strike.strings){
        const a=dot(sub(brake.p,r.surface_world),profile.strike.cross_axis_world);
        const b=dot(sub(brake.q,r.surface_world),profile.strike.cross_axis_world);
        assert.ok(!(a < -1e-10&&b > 1e-10),'Aborted braking must not add a string crossing');
      }
    }
    const right=m.sample(at+eps).right;
    const backward=scale(sub(before.world,left.world),1/eps),forward=scale(sub(right.world,after.world),1/eps);
    const error=maxdiff(backward,forward);maxFiniteVelocityDifference=Math.max(maxFiniteVelocityDifference,error);finiteChecks++;
    assert.ok(error<2e-6,JSON.stringify({at,oldEvent,newEvent,error}));
  }else limitedInterrupts++;
}
const repeatResults=[];
for(const interval of [150,70]){
  const trace=sampleTimeline(Array.from({length:16},(_,i)=>({event:events[i%8],timeMs:i*interval})),`repeat-${interval}ms`);
  const completed=new Set(trace.frames.filter(f=>f.right.phase==='rest').map(f=>f.right.strokeId));
  assert.equal(trace.events.at(-1).interruptedStrokes,interval===70?15:0);
  assert.equal(completed.size,interval===70?1:16);
  repeatResults.push({intervalMs:interval,inputs:16,accepted:trace.events.length,
    interruptedStrokes:trace.events.at(-1).interruptedStrokes,completedFullStrokes:completed.size,queued:0});
}
// Extra moving interior examples, not just zero-speed phase boundaries.
for(const at of [11,29,31,44,46,54,64,65,66,69,71,84,86,99,101,138])
  sampleTimeline([{event:full,timeMs:0},{event:singleB,timeMs:at}],`interior-${at}`);

const reference=createContactMotion(profile);reference.trigger(singleA,0);
const clocks=createContactMotionC53(profile);clocks.trigger(singleA,0);
for(const t of [70,140,210,280,350,420])clocks.trigger(singleB,t);
for(const t of [420,600,900,1200])assert.deepEqual(clocks.sample(t).head,reference.sample(t).head);
assert.equal(clocks.sample(1200,{headEnabled:false}).head.pitchRadians,0);
assert.equal(clocks.sample(1200,{headEnabled:false}).head.yawRadians,0);
clocks.trigger(singleA,1200);assert.equal(clocks.sample(1200).head.phraseStartMs,1200);
assert.throws(()=>clocks.trigger(singleA,1199));assert.throws(()=>clocks.trigger({mode:'chord',sourceStrings:[1,3]},1300));
assert.throws(()=>clocks.sample(NaN));assert.throws(()=>clocks.trigger({mode:'melody',noteIndex:8},1300));
clocks.reset(0);assert.equal(clocks.sample(0).right.phase,'rest');

// A near-knot machine-precision case must fail explicitly, leaving the existing
// C1 plan in place. It must not turn off the floor or zero an incoming velocity.
const edge=createContactMotionC53(profile);edge.trigger(singleA,0);
const edgeTime=65-1e-8;const edgeBefore=edge.sample(edgeTime).right;
const edgeReceipt=edge.trigger(singleB,edgeTime);
assert.equal(edgeReceipt.accepted,false);assert.equal(edgeReceipt.activeStrokeUnchanged,true);
assert.deepEqual(edge.sample(edgeTime).right,edgeBefore);
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const receipt={status:'C53-analytic-and-sampled-controller-bench-not-character-animation',
  profileSha256:hash(new URL('evidence/c35-rig-profile.json',oldDir)),
  reusedClockSourceSha256:hash(new URL('contact-motion.mjs',oldDir)),
  C53SourceSha256:hash(new URL('./contact-motion-c53.mjs',import.meta.url)),
  boundaryTimesMs:boundaryTimes,uninterrupted,analyticInterruptions:{accepted:acceptedInterrupts,limited:limitedInterrupts,
    maxJoinPositionErrorU:maxJoinPositionError,maxJoinVelocityErrorUPerMs:maxJoinVelocityError,
    finiteDifferenceChecks:finiteChecks,maxFiniteDifferenceVelocityMismatchUPerMs:maxFiniteVelocityDifference},
  nearKnotLimit:edgeReceipt,repeatIntervalsMs:[150,70],traces:traces.length,
  repeatResults,abortedBrakeAddsNoStringCrossing:true,
  traceSamples:traces.reduce((s,t)=>s+t.frames.length,0),queueLength:0,durationMs:140,
  headBlinkPhraseClockUnchanged:true,leftFrozen:true,accelerationBoundVerified:false,
  geometryStatus:'pending-native-actual-triangle-probe',skinBound:false,audio:false,modelAnimation:false,publicChanged:false};
fs.writeFileSync(new URL('controller-validation.json',out),JSON.stringify(receipt,null,2)+'\n');
fs.writeFileSync(new URL('target-path-samples.json',out),JSON.stringify({schema:'c53-real-controller-target-samples',traces})+'\n');
console.log(JSON.stringify({...receipt,uninterrupted:`${uninterrupted.length} cases`},null,2));
