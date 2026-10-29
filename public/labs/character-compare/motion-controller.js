/** Shared geometry weights for the WebGL and Godot comparison renderers.
 * One human note starts one stroke; audio and event recording belong to the host.
 * Order matches miao-playable.glb: Pluck, FretLow, FretHigh, HeadTilt, Lift.
 */
const ATTACK_MS = 60;
const RETURN_MS = 160;
const FRET_MS = 120;
const PHRASE_GAP_MS = 600;
const clamp = (value, low = 0, high = 1) => Math.min(high, Math.max(low, value));
const ease = value => { const t = clamp(value); return t * t * (3 - 2 * t); };
const mix = (from, to, amount) => from + (to - from) * amount;
const finiteTime = value => {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new TypeError('nowMs must be a finite number');
  }
  return value;
};

export function createCompareMotion() {
  let origin;
  let stroke = null;
  let fret = { start: 0, from: 0, to: 0 };
  let phrase = null;
  let lastStrike = null;
  let nextDirection = 1;

  function initialize(now) {
    if (origin === undefined) { origin = now; fret.start = now; }
  }

  function rightAt(now) {
    if (!stroke) return [0, 0];
    const elapsed = Math.max(0, now - stroke.start);
    if (elapsed < ATTACK_MS) {
      const amount = ease(elapsed / ATTACK_MS);
      return [mix(stroke.fromPluck, stroke.peak, amount), mix(stroke.fromLift, 0, amount)];
    }
    const progress = (elapsed - ATTACK_MS) / RETURN_MS;
    if (progress >= 1) return [0, 0];
    return [stroke.peak * (1 - ease(progress)), .9 * Math.sin(Math.PI * progress)];
  }

  function fretAt(now) {
    return mix(fret.from, fret.to, ease((now - fret.start) / FRET_MS));
  }

  function phraseAt(now) {
    if (!phrase) return 0;
    const elapsed = Math.max(0, now - phrase.start);
    if (elapsed < 240) return mix(phrase.from, .16, ease(elapsed / 240));
    if (elapsed >= 1240) return 0;
    return .16 * (1 - ease((elapsed - 240) / 1000));
  }

  function sample(nowMs, { headEnabled = true } = {}) {
    const now = finiteTime(nowMs);
    initialize(now);
    const [pluck, lift] = rightAt(now);
    const position = fretAt(now);
    // The idle phase never restarts on notes. Only a phrase after a gap adds a
    // restrained response; a fast run cannot make the head jitter every note.
    const idleHead = .12 * (1 - Math.cos(Math.max(0, now - origin) * Math.PI * 2 / 4200));
    const head = headEnabled ? idleHead + phraseAt(now) : 0;
    return [pluck, Math.max(0, -position), Math.max(0, position), head, lift];
  }

  function strike(noteIndex, nowMs) {
    if (!Number.isInteger(noteIndex) || noteIndex < 0 || noteIndex > 7) {
      throw new RangeError('noteIndex must be an integer from 0 to 7');
    }
    const now = finiteTime(nowMs);
    initialize(now);
    const [fromPluck, fromLift] = rightAt(now);
    const fromFret = fretAt(now);
    const fromPhrase = phraseAt(now);
    stroke = { start: now, fromPluck, fromLift, peak: .82 * nextDirection };
    nextDirection *= -1;
    fret = { start: now, from: fromFret, to: noteIndex / 7 * 2 - 1 };
    if (lastStrike === null || now - lastStrike > PHRASE_GAP_MS) {
      phrase = { start: now, from: fromPhrase };
    }
    lastStrike = now;
  }

  function reset(nowMs) {
    const now = finiteTime(nowMs);
    origin = now;
    stroke = null;
    fret = { start: now, from: 0, to: 0 };
    phrase = null;
    lastStrike = null;
    nextDirection = 1;
  }

  return { strike, sample, reset };
}
