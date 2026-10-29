/** Scene-independent whole-frame motion target generator; no audio/input synthesis.
 * All positions stay in the extracted Blender world frame. Host adapters convert
 * them into their own scene frame exactly once. Not connected to public product.
 */
const clamp = (x, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, x));
const smooth = x => { const t = clamp(x); return t * t * (3 - 2 * t); };
const add = (a, b) => a.map((v, i) => v + b[i]);
const sub = (a, b) => a.map((v, i) => v - b[i]);
const mul = (a, scale) => a.map(v => v * scale);
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
const mix = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
const finite = t => { if (!Number.isFinite(t)) throw new TypeError('nowMs must be finite'); return t; };
const PHRASE_GAP = 600;
const DURATION = 140;

function polyline(points, t) {
  const lengths = points.slice(1).map((p, i) => Math.hypot(...sub(p, points[i])));
  let d = clamp(t) * lengths.reduce((a, b) => a + b, 0);
  for (let i = 0; i < lengths.length; ++i) {
    if (d <= lengths[i] || i === lengths.length - 1) return mix(points[i], points[i + 1], clamp(d / lengths[i]));
    d -= lengths[i];
  }
  return [...points.at(-1)];
}

export function createContactMotion(profile) {
  if (profile.schema !== 'miao-contact-rig-v2' || !profile.whole_frame_required || profile.mesh_may_be_split !== false) {
    throw new TypeError('Expected a connected whole-frame miao-contact-rig-v2 profile');
  }
  const strike = structuredClone(profile.strike);
  const notes = structuredClone(profile.note_targets.melody);
  const fixedLeft = profile.left_hold.anchors.map(a => [...a.world]);
  const safeNormalLevel = Math.max(...strike.strings.map(r => dot(r.surface_world, strike.normal_world))) + strike.clearance_u;
  const lifted = point => add(point, mul(strike.normal_world, Math.max(0, safeNormalLevel - dot(point, strike.normal_world))));
  const axis = strike.cross_axis_world;
  let origin;
  let active = null;
  let phraseStart = null;
  let lastStrike = null;
  let sequence = 0;
  let interrupted = 0;

  function init(now) { if (origin === undefined) origin = now; }
  function rightAt(now) {
    if (!active) return { world: [...strike.rest_world], phase: 'rest', strokeId: null, progress: 1 };
    const t = Math.max(0, now - active.start);
    const s = active;
    if (t >= DURATION) return { world: [...strike.rest_world], phase: 'rest', strokeId: s.id, progress: 1 };
    const spans = [
      [0, 10, s.from, lifted(s.from), 'depart'],
      [10, 30, lifted(s.from), lifted(s.path[0]), 'preposition'],
      [30, 45, lifted(s.path[0]), s.path[0], 'approach'],
      [85, 100, s.path.at(-1), lifted(s.path.at(-1)), 'clear'],
      [100, DURATION, lifted(s.path.at(-1)), strike.rest_world, 'return'],
    ];
    if (t >= 45 && t < 85) return { world: polyline(s.path, smooth((t - 45) / 40)), phase: 'sweep', strokeId: s.id, progress: t / DURATION };
    const [begin, end, from, to, phase] = spans.find(([a, b]) => t >= a && t < b);
    return { world: mix(from, to, smooth((t - begin) / (end - begin))), phase, strokeId: s.id, progress: t / DURATION };
  }

  function selectPath(event) {
    if (event.mode === 'melody') {
      const note = notes[event.noteIndex];
      if (!Number.isInteger(event.noteIndex) || !note) throw new RangeError('Melody noteIndex must be 0..7');
      const point = note.right_pluck_surface_world;
      // Narrow local traversal crosses only the selected string. Adjacent string
      // spacing is verified from the profile, never inferred from source names.
      const margin = .009;
      return { path: [add(point, mul(axis, -margin)), [...point], add(point, mul(axis, margin))],
        strings: [note.source_string_index], requestedLeft: note, mode: 'melody' };
    }
    if (event.mode !== 'chord') throw new RangeError('mode must be melody or chord');
    const strings = [...new Set(event.sourceStrings ?? [])].sort((a, b) => a - b);
    if (!strings.length || strings.some((n, i) => !Number.isInteger(n) || n < 1 || n > 6 || (i && n !== strings[i - 1] + 1))) {
      throw new RangeError('Chord sourceStrings must be a contiguous subset of 1..6; muted-string avoidance is not implemented');
    }
    const rows = strike.strings.filter(r => strings.includes(r.source_index)).sort((a, b) => a.v - b.v);
    return { path: [add(rows[0].surface_world, mul(axis, -.009)), ...rows.map(r => [...r.surface_world]), add(rows.at(-1).surface_world, mul(axis, .009))],
      strings, requestedLeft: null, mode: 'chord' };
  }

  function trigger(event, nowMs) {
    const now = finite(nowMs);
    const selection = selectPath(event);
    if (lastStrike !== null && now < lastStrike) throw new RangeError('Input times must be monotonic');
    init(now);
    const current = rightAt(now);
    if (active && now - active.start < DURATION) interrupted += 1;
    if (lastStrike === null || now - lastStrike > PHRASE_GAP) phraseStart = now;
    active = { ...selection, start: now, from: current.world, id: ++sequence };
    lastStrike = now;
    return { strokeId: sequence, startsAtMs: now, endsAtMs: now + DURATION, queued: 0, interruptedStrokes: interrupted };
  }

  function sample(nowMs, { headEnabled = true } = {}) {
    const now = finite(nowMs);
    init(now);
    const age = Math.max(0, now - origin);
    const phraseAge = phraseStart === null ? Infinity : now - phraseStart;
    // A phrase has a single slow envelope; a run never resets this clock.
    const phrase = phraseAge >= 0 && phraseAge < 1500 ? Math.sin(Math.PI * phraseAge / 1500) ** 2 : 0;
    const idle = Math.sin(age * Math.PI * 2 / 4800);
    const blinkAge = (age + 1100) % 4700;
    const closure = blinkAge < 170 ? Math.sin(Math.PI * blinkAge / 170) ** 2 : 0;
    return {
      right: rightAt(now),
      left: { mode: 'freeze_existing_world_contact', worldAnchors: fixedLeft.map(p => [...p]),
        requestedPose: active?.requestedLeft ?? null, applyRequestedPose: false },
      head: { pitchRadians: headEnabled ? .004 * idle + .012 * phrase : 0,
        yawRadians: headEnabled ? .008 * phrase : 0,
        blinkClosure: closure, phraseStartMs: phraseStart, independentClock: true },
      body: { breathAmount: .002 * (1 - Math.cos(age * Math.PI * 2 / 4200)),
        applyToContactAnchors: false },
      mode: active?.mode ?? null, targetSourceStrings: active?.strings ?? [],
      queueLength: 0, interruptedStrokes: interrupted,
      limits: { skinBound: false, liveFrettingVerified: false, visualAnimationVerified: false },
    };
  }

  function reset(nowMs) {
    origin = finite(nowMs); active = null; phraseStart = null; lastStrike = null; sequence = 0; interrupted = 0;
  }
  return { trigger, sample, reset };
}
