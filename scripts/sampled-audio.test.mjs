import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { Sampler as ActualSampler } from '../node_modules/smplr/dist/index.mjs';

const source = await readFile(new URL('../public/sampled-audio.js', import.meta.url), 'utf8');
assert.match(source, /import \{ Sampler \} from '\.\/vendor\/smplr\.mjs';/);
assert.match(source, /import \{ CatAudio \} from '\.\/audio\.js';/);
let serial = 0;

class TestAudioBuffer {
  constructor(values) {
    this.pcm = Float32Array.from(values);
    this.duration = 0.8; this.length = this.pcm.length; this.sampleRate = 10; this.numberOfChannels = 1;
  }
  getChannelData() { return this.pcm; }
}
function buffer(values = [0.1, -0.1, 0.15, -0.2, 0.05, 0.01, 0.01, 0]) {
  return new TestAudioBuffer(values);
}

async function harness({ badDecode = false, maxPolyphony = 48, maxPerNote = 3, manifestPatch, realSampler = false } = {}) {
  const fetched = [], instances = [], progress = [];
  const manifest = { groups: {
    'piano-kw': { looping: false, coverageMidi: [60, 72], noteURLs: { C4: './samples/piano/C4.mp3', C5: './samples/piano/C5.mp3' } },
    'guitar-spanish': { looping: false, coverageMidi: [48, 72], noteURLs: { C3: './samples/guitar/C3.mp3', C5: './samples/guitar/C5.mp3' } },
    'marimba-iowa': { looping: false, coverageMidi: [60, 72], noteURLs: { C4: './samples/marimba/C4.mp3' } },
    'drums-virtuosity': { looping: false, noteURLs: { kick: './samples/drums/kick.mp3', snare: './samples/drums/snare.mp3', 'closed-hat': './samples/drums/hat.mp3', 'open-hat': './samples/drums/open.mp3', 'tom-high': './samples/drums/tom.mp3' } },
  } };
  manifestPatch?.(manifest);
  const context = { currentTime: 1, state: 'running', async decodeAudioData() {
    if (badDecode) throw new Error('Broken MP3');
    return buffer();
  } };
  const realSources = [];
  function finite(value) { assert.ok(Number.isFinite(value), `AudioParam received non-finite ${value}`); }
  function param() {
    let value = 0;
    return { get value() { return value; }, set value(next) { finite(next); value = next; },
      setValueAtTime(next, time) { finite(next); finite(time); value = next; },
      linearRampToValueAtTime(next, time) { finite(next); finite(time); },
      cancelScheduledValues(time) { finite(time); } };
  }
  const node = () => ({ connect() {}, disconnect() {} });
  context.createGain = () => ({ ...node(), gain: param() });
  context.createStereoPanner = () => ({ ...node(), pan: param() });
  context.createBufferSource = () => {
    const source = { ...node(), playbackRate: param(), detune: param(), starts: [], stops: [],
      start(time, offset) { finite(time); finite(offset); this.starts.push({ time, offset }); },
      stop(time) { finite(time); this.stops.push(time); } };
    realSources.push(source);
    return source;
  };
  class Base {
    constructor() { this.context = null; this.legacyCalls = []; this.baseStops = 0; }
    async ready() { this.context = context; this.master ||= { sharedMaster: true }; this.analyser ||= { sharedAnalyser: true }; return context; }
    play(...args) { this.legacyCalls.push(args); }
    stopVoices() { this.baseStops += 1; }
  }
  function Sampler(ctx, options) {
    const instance = { context: ctx, options, starts: [], stopCalls: 0, queueStops: 0, disposed: false,
      scheduler: { stop() { instance.queueStops += 1; }, schedule(event, callback) { callback(event); return () => {}; } },
      start(event) {
        const voice = { event, stops: [] };
        instance.starts.push(voice);
        return time => { voice.stops.push(time); };
      },
      stop() { this.stopCalls += 1; },
      dispose() { this.disposed = true; },
    };
    instance.ready = Promise.resolve().then(async () => {
      instance.buffers = {};
      await options.buffers(ctx, instance.buffers);
    });
    instances.push(instance);
    return instance;
  }
  const token = `__miaoSampleTest${++serial}`;
  globalThis[token] = { Base, Sampler: realSampler ? ActualSampler : Sampler };
  const fakeModule = source
    .replace("import { CatAudio } from './audio.js';", `const CatAudio = globalThis.${token}.Base;`)
    .replace("import { Sampler } from './vendor/smplr.mjs';", `const Sampler = globalThis.${token}.Sampler;`)
    .replace("const BASE = new URL('./', import.meta.url);", "const BASE = new URL('https://miao-beat.example/');");
  const module = await import(`data:text/javascript;base64,${Buffer.from(fakeModule).toString('base64')}`);
  delete globalThis[token];
  const audio = new module.SampledAudio({ maxPolyphony, maxPerNote, onProgress: state => progress.push(state),
    fetchImpl: async url => {
      fetched.push(url);
      assert.ok(url.startsWith('https://miao-beat.example/samples/'), 'Tests never fetch a remote sample');
      return { ok: true, status: 200, url,
        json: async () => manifest, arrayBuffer: async () => new ArrayBuffer(8) };
    },
  });
  return { audio, fetched, instances, progress, context, manifest, realSources, calibrateSample: module.calibrateSample,
    recoverDecode() { badDecode = false; } };
}

test('legacy readiness makes no sample requests and preserves old C/V voices', async () => {
  const { audio, fetched } = await harness();
  await audio.ready('sparkle', 'ui-synth-v1');
  assert.equal(fetched.length, 0);
  assert.equal(audio.isReady('sparkle', 'ui-synth-v1'), true);
  audio.play({ code: 'KeyC', kind: 'drum', voice: 'hat' }, 'sparkle', 2, 'ui-synth-v1');
  audio.play({ code: 'KeyV', kind: 'drum', voice: 'tom-high' }, 'marimba', 3, 'ui-synth-v1');
  assert.equal(audio.legacyCalls[0][0].voice, 'shaker');
  assert.equal(audio.legacyCalls[1][0].voice, 'bongoHigh');
  assert.equal(audio.legacyCalls[0][2], 2);
  assert.throws(() => audio.play({ kind: 'note', midi: 60 }, 'piano', 2, 'unknown-engine'));
});

test('selected instruments share context/master, decode once, cache and expose real progress', async () => {
  const { audio, fetched, instances, progress, context } = await harness();
  await Promise.all([audio.ready(), audio.ready('piano')]);
  assert.equal(fetched.filter(url => url.endsWith('manifest.json')).length, 1);
  assert.equal(instances.length, 2);
  assert.ok(instances.every(instance => instance.context === context && instance.options.destination === audio.master));
  assert.ok(instances.every(instance => instance.options.volume === 127));
  assert.equal(audio.getLoadProgress().loaded, 7);
  assert.equal(audio.getLoadProgress().total, 7);
  assert.equal(audio.isReady(), true);
  assert.ok(progress.some(state => state.status === 'loading'));
  assert.ok(progress.some(state => state.status === 'ready'));
  const count = fetched.length;
  await audio.ready();
  assert.equal(fetched.length, count);
  await audio.ready('guitar');
  assert.equal(instances.length, 3, 'Switching instruments reuses decoded drums');
  assert.equal(audio.isReady('guitar'), true);
});

test('drums-only loads no melodic bank and aliases cannot silently resolve to MIDI zero', async () => {
  const { audio, fetched, instances } = await harness();
  await audio.ready('drums');
  assert.equal(instances.length, 1);
  assert.ok(!fetched.some(url => /\/piano\/|\/guitar\/|\/marimba\//.test(url)));
  audio.play({ kind: 'drum', voice: 'shaker' }, 'drums', 2);
  audio.play({ kind: 'drum', voice: 'bongoHigh' }, 'drums', 2.1);
  assert.deepEqual(instances[0].starts.map(voice => voice.event.note), ['closed-hat', 'tom-high']);
  assert.throws(() => audio.play({ kind: 'drum', voice: 'cowbell' }, 'drums'), /Unsupported sampled drum/);
  assert.throws(() => audio.play({ kind: 'drum', voice: 'ride' }, 'drums'), /missing/);
  assert.throws(() => audio.play({ kind: 'note', midi: 60 }, 'drums'), /melodic instrument/);
});

test('chords strum at deterministic 15ms intervals with unique stops and bounded tails', async () => {
  const { audio, instances } = await harness({ maxPolyphony: 4, maxPerNote: 2 });
  await audio.ready('guitar');
  const guitar = instances.find(instance => Object.hasOwn(instance.buffers, 'C3'));
  audio.play({ kind: 'chord', notes: [48, 55, 60] }, 'guitar', 2);
  assert.deepEqual(guitar.starts.map(voice => voice.event.time), [2, 2.015, 2.03]);
  assert.ok(guitar.starts.every(voice => voice.event.loop === false));
  for (let index = 0; index < 4; index += 1) audio.play({ kind: 'note', midi: 60 }, 'guitar', 3 + index * 0.1);
  assert.ok(audio.sampleVoices.size <= 4);
  assert.ok([...audio.sampleVoices].filter(voice => voice.note === 60).length <= 2);
  assert.ok(guitar.starts.some(voice => voice.stops.length), 'Old tails are released instead of growing without bound');
  assert.equal(new Set(guitar.starts.map(voice => voice.event.stopId)).size, guitar.starts.length);
  assert.throws(() => audio.play({ kind: 'note', midi: 47 }, 'guitar'), /outside the sampled range/);
  audio.stopVoices();
  assert.equal(audio.sampleVoices.size, 0);
  assert.equal(audio.baseStops, 1);
  assert.ok(instances.every(instance => instance.queueStops === 1 && instance.stopCalls === 1),
    'Stopping clears future sampler queues as well as active voices');
});

test('decode failure rejects without synthesis fallback, and a later explicit retry can succeed', async () => {
  const { audio, instances, recoverDecode } = await harness({ badDecode: true });
  await assert.rejects(audio.ready('piano'), /Broken MP3/);
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.equal(audio.isReady(), false);
  assert.equal(audio.legacyCalls.length, 0);
  assert.ok(instances.every(instance => instance.disposed));
  assert.ok(audio.getLoadProgress().groups.some(group => group.status === 'error'));
  recoverDecode();
  await audio.ready('piano');
  assert.equal(audio.isReady(), true);
});

test('manifest sample URLs cannot request a third-party CDN', async () => {
  const { audio, fetched } = await harness({ manifestPatch(manifest) {
    manifest.groups['piano-kw'].noteURLs.C4 = 'https://unexpected.example/C4.mp3';
  } });
  await assert.rejects(audio.ready('piano'), /local samples directory/);
  assert.ok(fetched.every(url => url.startsWith('https://miao-beat.example/')));
});

test('calibration bounds boost and full-buffer peak while using the attack window', async () => {
  const { calibrateSample } = await harness();
  const quiet = buffer([0.001, -0.001, 0.002, 0.001]);
  assert.equal(calibrateSample(quiet).gain, 6, 'Quiet sources have a finite gain cap');
  const transient = buffer([0.1, 0.1, 0, 0, 0, 2, 0, 0]);
  const result = calibrateSample(transient);
  assert.ok(result.outputPeak <= 0.5);
  assert.ok([...transient.getChannelData(0)].every(value => Math.abs(value) <= 0.5));
  assert.throws(() => calibrateSample(buffer([0, 0, 0])), /silent/);
});

test('closed hat chokes the previous open hat at its scheduled hit time', async () => {
  const { audio, instances } = await harness();
  await audio.ready('drums');
  audio.play({ kind: 'drum', voice: 'open-hat' }, 'drums', 1.03);
  audio.play({ kind: 'drum', voice: 'closed-hat' }, 'drums', 1.12);
  assert.deepEqual(instances[0].starts[0].stops, [1.12],
    'Preparing a future closed hat does not truncate the open hat at context.currentTime');
  audio.stopVoices();
});

test('actual smplr 1.1.0 receives finite pitch/envelope params for notes, chords and drums', async () => {
  const previousAudioBuffer = globalThis.AudioBuffer;
  globalThis.AudioBuffer = TestAudioBuffer;
  let audio;
  try {
    const state = await harness({ realSampler: true, manifestPatch(manifest) {
      // The library pairs sorted pitch regions with insertion order. A reversed
      // manifest must be registered in pitch order before the real conversion.
      manifest.groups['piano-kw'].noteURLs = { C5: './samples/piano/C5.mp3', C4: './samples/piano/C4.mp3' };
    } });
    audio = state.audio;
    await audio.ready('piano');
    audio.play({ kind: 'note', midi: 61 }, 'piano', 1.04);
    assert.equal(state.realSources.length, 1);
    assert.equal(state.realSources[0].detune.value, 100,
      'C-sharp is one semitone above the C4 buffer, not a misregistered C5');
    assert.equal(state.realSources[0].starts[0].time, 1.04);
    await audio.ready('guitar');
    audio.play({ kind: 'chord', notes: [48, 55, 60] }, 'guitar', 1.05);
    audio.play({ kind: 'drum', voice: 'open-hat' }, 'guitar', 1.06);
    audio.play({ kind: 'drum', voice: 'closed-hat' }, 'guitar', 1.12);
    assert.equal(state.realSources.length, 6);
    assert.ok(state.realSources.every(source => Number.isFinite(source.detune.value)));
    assert.ok(Math.abs(state.realSources[4].stops[0] - 1.155) < 1e-9,
      'Actual open-hat voice releases at the scheduled closed-hat hit plus its 35ms release');
    audio.stopVoices();
    assert.ok(state.realSources.every(source => source.stops.length > 0));
  } finally {
    audio?.stopVoices();
    if (previousAudioBuffer === undefined) delete globalThis.AudioBuffer;
    else globalThis.AudioBuffer = previousAudioBuffer;
  }
});
