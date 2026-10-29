import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createContactMotion } from './contact-motion.mjs';
import { remapContactBindings } from './remap-contact-bindings.mjs';

const profile = JSON.parse(fs.readFileSync(new URL('./evidence/c35-rig-profile.json', import.meta.url)));
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
const sub = (a, b) => a.map((x, i) => x - b[i]);
const axis = profile.strike.cross_axis_world;
const normal = profile.strike.normal_world;
const check = [];
const motion = createContactMotion(profile);
let totalCrossings = 0;
const timelines = [];
for (let i = 0; i < 8; ++i) {
  const start = i * 150;
  const before = motion.sample(start);
  const receipt = motion.trigger({ mode: 'melody', noteIndex: i }, start);
  assert.equal(receipt.queued, 0);
  assert.deepEqual(motion.sample(start).right.world, before.right.world);
  const frames = Array.from({ length: 141 }, (_, t) => ({ timeMs: start + t, ...motion.sample(start + t) }));
  const strings = profile.strike.strings.map(row => {
    const points = frames.filter(f => f.right.phase === 'sweep').map(f => f.right.world);
    let count = 0;
    for (let j = 1; j < points.length; ++j) {
      const a = dot(sub(points[j - 1], row.surface_world), axis);
      const b = dot(sub(points[j], row.surface_world), axis);
      if (a <= 0 && b > 0) count += 1;
    }
    return { sourceString: row.source_index, crossings: count };
  });
  assert.equal(strings.reduce((s, row) => s + row.crossings, 0), 1);
  const note = profile.note_targets.melody[i];
  assert.equal(strings.find(row => row.sourceString === note.source_string_index).crossings, 1);
  assert.equal(frames.at(-1).right.phase, 'rest');
  assert.equal(frames.at(-1).queueLength, 0);
  assert.equal(frames.at(-1).interruptedStrokes, 0);
  for (const frame of frames) assert.deepEqual(frame.left.worldAnchors, profile.left_hold.anchors.map(a => a.world));
  totalCrossings += 1;
  timelines.push({ note: note.note, frames });
  check.push({ key: note.key, note: note.note, midi: note.midi, string: note.standard_string,
    sourceString: note.source_string_index, fret: note.fret, strings, returnsAtMs: start + 140 });
}
const headReference = createContactMotion(profile);
headReference.trigger({ mode: 'melody', noteIndex: 0 }, 0);
const fast = createContactMotion(profile);
fast.trigger({ mode: 'melody', noteIndex: 0 }, 0);
for (const t of [150, 300, 450]) fast.trigger({ mode: 'melody', noteIndex: 1 }, t);
for (const t of [450, 600, 900, 1200]) assert.deepEqual(fast.sample(t).head, headReference.sample(t).head);
const interrupted = createContactMotion(profile);
interrupted.trigger({ mode: 'melody', noteIndex: 0 }, 0);
const interruptedBefore = interrupted.sample(70).right.world;
interrupted.trigger({ mode: 'melody', noteIndex: 7 }, 70);
assert.deepEqual(interrupted.sample(70).right.world, interruptedBefore);
assert.equal(interrupted.sample(70).interruptedStrokes, 1);
assert.equal(interrupted.sample(70).queueLength, 0);
assert.equal(interrupted.sample(210).right.phase, 'rest');
const chord = createContactMotion(profile);
chord.trigger({ mode: 'chord', sourceStrings: [1, 2, 3, 4, 5, 6] }, 0);
const chordFrames = Array.from({ length: 141 }, (_, t) => ({ timeMs: t, ...chord.sample(t) }));
for (const row of profile.strike.strings) {
  const sweep = chordFrames.filter(f => f.right.phase === 'sweep');
  let crossings = 0;
  for (let j = 1; j < sweep.length; ++j) {
    if (dot(sub(sweep[j - 1].right.world, row.surface_world), axis) <= 0 && dot(sub(sweep[j].right.world, row.surface_world), axis) > 0) crossings += 1;
  }
  assert.equal(crossings, 1);
}
assert.throws(() => chord.trigger({ mode: 'chord', sourceStrings: [1, 3] }, 150));
assert.throws(() => chord.trigger({ mode: 'melody', noteIndex: 8 }, 150));
assert.throws(() => chord.sample(NaN));
const indexMap = new Map();
const diagnosticVertices = [];
for (const a of profile.left_hold.anchors) for (const v of a.vertex_provenance) {
  const targetIndex = v.source_native_vertex_index + 1;
  indexMap.set(v.source_native_vertex_index, targetIndex);
  diagnosticVertices[targetIndex] = [...v.source_rest_world];
}
const remapped = remapContactBindings(profile, { sourceSha256: profile.source_native_sha256, indexMap,
  targetWorldVertices: diagnosticVertices, targetNativeSha256: 'synthetic-index-map-test-only' });
assert.ok(remapped.every(a => a.rest_contact_drift_u < 5e-7 && !a.contact_pass_inherited));
assert.throws(() => remapContactBindings(profile, { sourceSha256: profile.source_native_sha256,
  indexMap: new Map(), targetWorldVertices: diagnosticVertices, targetNativeSha256: 'test' }));
assert.throws(() => remapContactBindings(profile, { sourceSha256: 'wrong', indexMap,
  targetWorldVertices: diagnosticVertices, targetNativeSha256: 'test' }));
const receipt = { status: 'technical-data-validation-pass-not-character-animation-acceptance',
  melody: check, melodyTotalCrossings: totalCrossings,
  inputIntervalMs: 150, strokeDurationMs: 140, queueLength: 0,
  fasterInput: { testedIntervalMs: 70, positionContinuous: true, interruptedStrokes: 1,
    queueLength: 0, velocityContinuityVerified: false, fullStrokePerInputGuaranteed: false },
  chord: { oneSweep: true, sixStringsEachCrossedOnce: true, noReturnSweep: true },
  leftFrozenAnchorsInvariant: true, fastNotesDoNotResetHeadOrBlinkClock: true,
  contactRemap: { explicitIndexMapRequired: true, noNearestFallback: true,
    sixSupportVertexProvenanceTuplesAmbiguous: true, syntheticMapTestOnly: true,
    syntheticReconstructionMaxErrorU: Math.max(...remapped.map(a => a.rest_contact_drift_u)),
    mergedBodyContactPassInherited: false },
  actualTriangleValidation: 'See validate-path-geometry.py and path-geometry-probe.json; these tests inspect target points, not skin volume.' };
fs.writeFileSync(new URL('./evidence/controller-validation.json', import.meta.url), JSON.stringify(receipt, null, 2) + '\n');
const slim = frames => frames.map(({ timeMs, right }) => ({ timeMs, right }));
fs.writeFileSync(new URL('./evidence/target-path-samples.json', import.meta.url), JSON.stringify({ melody: timelines.map(t => ({ note: t.note, frames: slim(t.frames) })), chord: slim(chordFrames) }) + '\n');
console.log(JSON.stringify(receipt, null, 2));
