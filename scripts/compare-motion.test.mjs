import test from 'node:test';
import assert from 'node:assert/strict';
import { createCompareMotion } from '../public/labs/character-compare/motion-controller.js';

const close = (actual, expected, tolerance = 1e-9) => {
  assert.equal(actual.length, expected.length);
  actual.forEach((value, index) => assert.ok(Math.abs(value - expected[index]) < tolerance,
    `weight ${index}: ${value} differs from ${expected[index]}`));
};
const right = weights => [weights[0], weights[4]];

test('one press makes one stroke and returns; no delayed replay after a long pause', () => {
  const motion = createCompareMotion();
  motion.reset(0);
  motion.strike(3, 0);
  close(right(motion.sample(0)), [0, 0]);
  assert.ok(motion.sample(60)[0] > .7, 'the picking paw reaches a visible first peak');
  assert.ok(motion.sample(140)[4] > .8, 'return stroke lifts the paw away from the strings');
  close(right(motion.sample(230)), [0, 0]);
  for (const now of [500, 1_000, 1_000_000]) close(right(motion.sample(now)), [0, 0]);
});

for (const interval of [500, 150, 80]) {
  test(`${interval} ms notes keep changing direction without snapping or an old-action queue`, () => {
    const motion = createCompareMotion();
    motion.reset(0);
    const peaks = [];
    for (let index = 0; index < 16; index++) {
      const now = index * interval;
      const before = motion.sample(now);
      motion.strike(index % 8, now);
      close(motion.sample(now), before);
      const during = motion.sample(now + 55);
      assert.ok(Math.abs(during[0] - before[0]) > .2, 'each input has perceptible travel');
      peaks.push(during[0]);
    }
    assert.ok(peaks.some(value => value > .55) && peaks.some(value => value < -.55),
      'continuous playing visits both sides instead of freezing at the same pose');
    for (const now of [16 * interval + 300, 16 * interval + 10_000]) {
      close(right(motion.sample(now)), [0, 0]);
    }
  });
}

test('a new note during a lifted return begins at the same five weights', () => {
  const motion = createCompareMotion();
  motion.reset(0);
  motion.strike(0, 0);
  const before = motion.sample(137);
  assert.ok(before[4] > .7);
  motion.strike(7, 137);
  close(motion.sample(137), before);
  assert.ok(motion.sample(138)[4] > .7, 'lift does not disappear on the input frame');
});

test('different notes smoothly choose distinct fret positions and retain the last one', () => {
  const motion = createCompareMotion();
  motion.reset(0);
  motion.strike(0, 0);
  const middle = motion.sample(60);
  assert.ok(middle[1] > 0 && middle[1] < .9, 'fretting hand travels rather than teleports');
  const low = motion.sample(200);
  assert.ok(low[1] > .9 && low[2] === 0);
  motion.strike(7, 500);
  const high = motion.sample(700);
  assert.ok(high[2] > .9 && high[1] === 0);
  close(motion.sample(50_000).slice(1, 3), high.slice(1, 3));
});

test('fast notes do not reset head response; disabling the head only changes its weight', () => {
  const busy = createCompareMotion();
  const quiet = createCompareMotion();
  busy.reset(0); quiet.reset(0);
  busy.strike(0, 0); quiet.strike(0, 0);
  for (let now = 80; now <= 560; now += 80) busy.strike(4, now);
  assert.equal(busy.sample(580)[3], quiet.sample(580)[3]);
  const before = busy.sample(1_300);
  busy.strike(5, 1_300);
  close(busy.sample(1_300), before);
  const enabled = busy.sample(1_500);
  const disabled = busy.sample(1_500, { headEnabled: false });
  assert.ok(enabled[3] > 0); assert.equal(disabled[3], 0);
  close([disabled[0], disabled[1], disabled[2], disabled[4]],
    [enabled[0], enabled[1], enabled[2], enabled[4]]);
});

test('reset clears an interrupted stroke, fret position and every old phrase response', () => {
  const motion = createCompareMotion();
  motion.strike(7, 1_000);
  assert.ok(motion.sample(1_080)[4] > 0);
  motion.reset(1_080);
  close(motion.sample(1_080), [0, 0, 0, 0, 0]);
  for (const now of [1_081, 2_000, 50_000]) {
    close(motion.sample(now, { headEnabled: false }), [0, 0, 0, 0, 0]);
  }
});

test('all output weights stay finite and bounded over interrupted playing', () => {
  const motion = createCompareMotion();
  motion.reset(0);
  for (let now = 0; now < 10_000; now += 13) {
    if (now % 39 === 0) motion.strike((now / 39) % 8, now);
    const weights = motion.sample(now);
    assert.equal(weights.length, 5);
    weights.forEach((value, index) => {
      assert.ok(Number.isFinite(value));
      assert.ok(value >= (index === 0 ? -.83 : 0) && value <= 1,
        `weight ${index} out of range: ${value}`);
    });
  }
});

test('invalid note/time is rejected without changing the active pose', () => {
  const motion = createCompareMotion();
  motion.strike(2, 0);
  const before = motion.sample(90);
  for (const index of [-1, 8, 1.5, NaN, '2']) assert.throws(() => motion.strike(index, 90), RangeError);
  for (const time of [NaN, Infinity, -Infinity, '90', undefined]) {
    assert.throws(() => motion.strike(2, time), TypeError);
    assert.throws(() => motion.sample(time), TypeError);
    assert.throws(() => motion.reset(time), TypeError);
  }
  close(motion.sample(90), before);
});
