/** C53 unbound point targets; adapted from ../character-motion-v2/contact-motion.mjs.
 * Same profile, event semantics and independent phrase/head clock. No audio,
 * mesh, rig, public adapter or frame assets. World velocity uses scene units/ms.
 */
import { createContactMotion } from '../character-motion-v2/contact-motion.mjs';
const add = (a, b) => a.map((v, i) => v + b[i]);
const sub = (a, b) => a.map((v, i) => v - b[i]);
const mul = (a, t) => a.map(v => v * t);
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
const norm = a => Math.hypot(...a);
const zero = () => [0, 0, 0];
const finite = t => { if (!Number.isFinite(t)) throw new TypeError('nowMs must be finite'); return t; };
export const DURATION_MS = 140;
export const MIN_BRAKE_MS = 1e-6;
// Fixed outward relief between actual contact knots. The source profile's
// nearest projected surface points are not a globally flat tangent rail:
// a flat traversal penetrated actual faceted tubes by up to 4.73e-6u. Keep
// those exact contact points and approach each from the outward half-space.
// This is a technical point trajectory, not a claim of natural hand motion.
export const RAIL_RELIEF_U = .007;

function segment(a, b, p, q, phase, strings, v = zero(), w = zero()) {
  return { a, b, p: [...p], q: [...q], v: [...v], w: [...w], phase, strings: [...strings] };
}

// Analytic cubic Hermite value AND derivative; velocities are never inferred
// from display frames. A zero-velocity knot is shared by the adjacent segments.
export function evaluateSegment(s, t) {
  const d = s.b - s.a;
  const u = Math.min(1, Math.max(0, (t - s.a) / d));
  if (u === 0) return { world: [...s.p], velocityWorldPerMs: [...s.v] };
  if (u === 1) return { world: [...s.q], velocityWorldPerMs: [...s.w] };
  return {
    world: s.p.map((p, i) => (2*u**3-3*u*u+1)*p + (u**3-2*u*u+u)*d*s.v[i]
      + (-2*u**3+3*u*u)*s.q[i] + (u**3-u*u)*d*s.w[i]),
    velocityWorldPerMs: s.p.map((p, i) => ((6*u*u-6*u)*p + (-6*u*u+6*u)*s.q[i])/d
      + (3*u*u-4*u+1)*s.v[i] + (3*u*u-2*u)*s.w[i]),
  };
}

export function createContactMotionC53(profile) {
  const clocks = createContactMotion(profile); // validates whole-frame profile
  const strike = structuredClone(profile.strike);
  const axis = strike.cross_axis_world, normal = strike.normal_world;
  if (Math.abs(norm(axis)-1)>1e-6 || Math.abs(norm(normal)-1)>1e-6 || Math.abs(dot(axis, normal))>1e-6)
    throw new TypeError('C53 requires orthonormal profile strike axes');
  const safeLevel = Math.max(...strike.strings.map(r => dot(r.surface_world, normal))) + strike.clearance_u;
  const lift = p => add(p, mul(normal, Math.max(0, safeLevel-dot(p, normal))));
  let active = null, lastInput = null, sequence = 0, interruptions = 0;

  function contactRail(points) {
    const out=[add(add(points[0],mul(axis,-.009)),mul(normal,RAIL_RELIEF_U))];
    points.forEach((p,i)=>{
      out.push([...p]);
      if(i<points.length-1)out.push(add(mul(add(p,points[i+1]),.5),mul(normal,RAIL_RELIEF_U)));
    });
    out.push(add(add(points.at(-1),mul(axis,.009)),mul(normal,RAIL_RELIEF_U)));
    return out;
  }

  function selection(event) {
    if (event.mode === 'melody') {
      const n = profile.note_targets.melody[event.noteIndex];
      if (!Number.isInteger(event.noteIndex) || !n) throw new RangeError('Melody noteIndex must be 0..7');
      return { mode: 'melody', strings: [n.source_string_index], path: contactRail([n.right_pluck_surface_world]) };
    }
    if (event.mode !== 'chord') throw new RangeError('mode must be melody or chord');
    const ids = [...new Set(event.sourceStrings ?? [])].sort((a,b)=>a-b);
    if (!ids.length || ids.some((n,i)=>!Number.isInteger(n)||n<1||n>6||(i&&n!==ids[i-1]+1)))
      throw new RangeError('Chord sourceStrings must be contiguous; muted-string avoidance is not implemented');
    const rows = strike.strings.filter(r=>ids.includes(r.source_index)).sort((a,b)=>a.v-b.v);
    return { mode: 'chord', strings: ids, path: contactRail(rows.map(r=>r.surface_world)) };
  }

  function rightAt(now) {
    const t = active ? Math.max(0, now-active.start) : DURATION_MS;
    if (!active || t>=DURATION_MS) return { world: [...strike.rest_world], velocityWorldPerMs: zero(),
      phase: 'rest', strokeId: active?.id ?? null, progress: 1, permittedSourceStrings: [], segmentEndWorld: [...strike.rest_world] };
    const s = active.segments.find(s=>t>=s.a&&t<s.b);
    return { ...evaluateSegment(s,t), phase:s.phase, strokeId:active.id, progress:t/DURATION_MS,
      permittedSourceStrings:[...s.strings], segmentEndWorld:[...s.q] };
  }

  function trigger(event, nowMs) {
    const now = finite(nowMs), next = selection(event);
    if (lastInput!==null && now<lastInput) throw new RangeError('Input times must be monotonic');
    const current = rightAt(now), v = current.velocityWorldPerMs, speed = norm(v);
    // Brake along the CURRENT straight segment, stopping strictly before its
    // endpoint. Every sweep segment ends at a string or its edge margin: thus
    // abort braking cannot add a later string crossing. No cross-string travel
    // to the new input starts until the point is lifted above all six tubes.
    const remaining = norm(sub(current.segmentEndWorld,current.world));
    const brakeMs = speed===0 ? 0 : Math.min(.25, remaining/speed);
    if (speed!==0 && (!Number.isFinite(brakeMs)||brakeMs<MIN_BRAKE_MS)) {
      lastInput=now;
      return { accepted:false, reason:'C1_ESCAPE_BELOW_NUMERIC_TIME_FLOOR',
        queued:0, activeStrokeUnchanged:true, minBrakeMs:MIN_BRAKE_MS };
    }
    const stopped = add(current.world,mul(v,brakeMs/2)), high = lift(stopped);
    const segments = [];
    if (brakeMs>0) segments.push(segment(0,brakeMs,current.world,stopped,'brake',current.permittedSourceStrings,v));
    segments.push(segment(brakeMs,10,stopped,high,'depart',current.permittedSourceStrings));
    segments.push(segment(10,30,high,lift(next.path[0]),'preposition',[]));
    segments.push(segment(30,45,lift(next.path[0]),next.path[0],'approach',next.strings));
    const lengths = next.path.slice(1).map((p,i)=>norm(sub(p,next.path[i])));
    const total = lengths.reduce((a,b)=>a+b,0);
    let at=45;
    lengths.forEach((len,i)=>{
      const end=i===lengths.length-1?85:at+40*len/total;
      segments.push(segment(at,end,next.path[i],next.path[i+1],'sweep',next.strings)); at=end;
    });
    segments.push(segment(85,100,next.path.at(-1),lift(next.path.at(-1)),'clear',next.strings));
    segments.push(segment(100,140,lift(next.path.at(-1)),strike.rest_world,'return',[]));
    clocks.trigger(event,now);
    if(active && now-active.start<DURATION_MS) interruptions++;
    active={...next,start:now,id:++sequence,segments}; lastInput=now;
    return {accepted:true,strokeId:sequence,startsAtMs:now,endsAtMs:now+140,brakeMs,
      queued:0,interruptedStrokes:interruptions,fullStrokePerInputGuaranteed:false};
  }

  function sample(nowMs,options={}) {
    const now=finite(nowMs), base=clocks.sample(now,options);
    return {...base,right:rightAt(now),queueLength:0,interruptedStrokes:interruptions,
      limits:{...base.limits,velocityContinuityVerified:true,
        continuityScope:'accepted triggers only; explicit numeric-floor rejection preserves prior plan',
        accelerationBoundVerified:false,pawVolumeCollisionVerified:false}};
  }
  function reset(nowMs){clocks.reset(finite(nowMs));active=null;lastInput=null;sequence=0;interruptions=0;}
  // Frozen copy for independent bench/geometry sampling, never mutable state.
  function inspectPlan(){return active?structuredClone(active):null;}
  return {trigger,sample,reset,inspectPlan};
}
