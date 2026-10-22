import { CatAudio } from './audio.js';
import { Sampler } from './vendor/smplr.mjs';

const PRESETS = Object.freeze({ piano: 'piano-kw', marimba: 'marimba-iowa', guitar: 'guitar-spanish', drums: 'drums-virtuosity' });
const DRUM_ALIASES = Object.freeze({
  kick: 'kick', snare: 'snare', hat: 'closed-hat', hiHat: 'closed-hat', hihat: 'closed-hat',
  closedHat: 'closed-hat', 'closed-hat': 'closed-hat', openHat: 'open-hat', 'open-hat': 'open-hat',
  shaker: 'closed-hat', bongo: 'tom-high', bongoLow: 'tom-low', bongoHigh: 'tom-high',
  tomLow: 'tom-low', 'tom-low': 'tom-low', tomHigh: 'tom-high', 'tom-high': 'tom-high',
  cymbal: 'crash', crash: 'crash', ride: 'ride',
});
const LEGACY = 'ui-synth-v1';
const SAMPLED = 'sample-v1';
const BASE = new URL('./', import.meta.url);

function engineName(engine) {
  if (engine !== LEGACY && engine !== SAMPLED) throw new Error(`Unsupported audio engine: ${engine}`);
  return engine;
}
function groupsFor(preset) {
  const group = PRESETS[preset];
  if (!group) throw new Error(`Unsupported sampled instrument: ${preset}`);
  return group === PRESETS.drums ? [group] : [group, PRESETS.drums];
}
function localSampleURL(value) {
  if (typeof value !== 'string' || !value) throw new Error('Invalid sample URL');
  const url = new URL(value, BASE);
  if (url.origin !== BASE.origin || !url.pathname.startsWith(`${BASE.pathname}samples/`) || url.username || url.password) {
    throw new Error('Samples must come from this application’s local samples directory');
  }
  return url.href;
}
function sampleMidi(name) {
  const match = /^([A-G])([#b]?)(-?\d+)$/.exec(name);
  if (!match) throw new Error(`Invalid melodic sample note: ${name}`);
  return (Number(match[3]) + 1) * 12 + ({ C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 })[match[1]] + (match[2] === '#' ? 1 : match[2] === 'b' ? -1 : 0);
}

// Initial audition calibration, not perceptual loudness normalization: measure
// the first 150ms over all channels, bound boost to +15.6dB and sample peak to
// 0.5. A quiet cymbal's long tail must not be amplified by whole-file RMS.
export function calibrateSample(buffer) {
  const frames = Math.min(buffer.length, Math.max(1, Math.round(buffer.sampleRate * 0.15)));
  let sum = 0, peak = 0;
  for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) {
    const data = buffer.getChannelData(channel);
    for (let index = 0; index < data.length; index += 1) {
      if (!Number.isFinite(data[index])) throw new Error('Sample contains non-finite PCM');
      peak = Math.max(peak, Math.abs(data[index]));
      if (index < frames) sum += data[index] ** 2;
    }
  }
  if (!peak) throw new Error('Sample is silent');
  const attackRms = Math.sqrt(sum / Math.max(1, frames * buffer.numberOfChannels));
  const gain = Math.min(6, attackRms > 0 ? 0.09 / attackRms : 1, 0.5 / peak);
  for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) {
    const data = buffer.getChannelData(channel);
    for (let index = 0; index < data.length; index += 1) data[index] *= gain;
  }
  return { attackWindowMs: 150, attackRms, sourcePeak: peak, gain, outputPeak: peak * gain };
}

// smplr 1.1.0's flat URL loader warns and swallows decode/non-200 failures.
// Its supported async buffers loader lets us reject those failures explicitly,
// while retaining Sampler's MIDI mapping, interpolation, voices and scheduler.
export class SampledAudio extends CatAudio {
  constructor({ fetchImpl = globalThis.fetch?.bind(globalThis), maxPolyphony = 48, maxPerNote = 3, loadTimeoutMs = 15000, onProgress = null } = {}) {
    super();
    this.fetchImpl = fetchImpl;
    this.maxPolyphony = Math.max(1, Math.min(96, Math.floor(maxPolyphony) || 48));
    this.maxPerNote = Math.max(1, Math.min(8, Math.floor(maxPerNote) || 3));
    this.loadTimeoutMs = Math.max(100, Number(loadTimeoutMs) || 15000);
    this.onProgress = onProgress;
    this.samplers = new Map();
    this.sampleNotes = new Map();
    this.sampleCoverage = new Map();
    this.sampleCalibration = new Map();
    this.sampleStates = new Map();
    this.pendingGroups = new Map();
    this.sampleVoices = new Set();
    this.manifestPromise = null;
    this.sampleSerial = 0;
  }

  async ready(preset = 'piano', engine = SAMPLED) {
    engineName(engine);
    const groups = engine === LEGACY ? [] : groupsFor(preset);
    const context = await super.ready();
    await Promise.all(groups.map(group => this.loadGroup(group)));
    return context;
  }

  isReady(preset = 'piano', engine = SAMPLED) {
    engineName(engine);
    if (!this.context || this.context.state !== 'running') return false;
    return engine === LEGACY || groupsFor(preset).every(group => this.sampleStates.get(group)?.status === 'ready');
  }

  getLoadProgress(preset = 'piano', engine = SAMPLED) {
    engineName(engine);
    const groups = (engine === LEGACY ? [] : groupsFor(preset)).map(group => ({
      group, ...(this.sampleStates.get(group) || { status: 'idle', loaded: 0, total: 0, error: null }),
    }));
    return {
      preset, engine, ready: this.isReady(preset, engine),
      loaded: groups.reduce((sum, group) => sum + group.loaded, 0),
      total: groups.reduce((sum, group) => sum + group.total, 0), groups,
    };
  }

  notify(group) {
    // Observer code must not turn a successfully decoded instrument into a load failure.
    try { this.onProgress?.({ group, ...this.sampleStates.get(group) }); } catch { /* UI observer only. */ }
  }

  async withTimeout(promise, label, controller) {
    let timer;
    try {
      return await Promise.race([
        promise,
        new Promise((_, reject) => { timer = setTimeout(() => { controller?.abort(); reject(new Error(`${label} timed out`)); }, this.loadTimeoutMs); }),
      ]);
    } finally { clearTimeout(timer); }
  }

  async fetchLocal(url) {
    if (typeof this.fetchImpl !== 'function') throw new Error('Sample loading is unavailable');
    const controller = new AbortController();
    const response = await this.withTimeout(this.fetchImpl(url, { credentials: 'same-origin', signal: controller.signal }), 'Sample request', controller);
    if (!response.ok) throw new Error(`Sample request failed (${response.status}): ${new URL(url).pathname}`);
    // Do not allow a local resource redirect to become an external sample CDN.
    if (response.url) localSampleURL(response.url);
    return response;
  }

  async getManifest() {
    if (!this.manifestPromise) {
      const request = (async () => {
        const response = await this.fetchLocal(new URL('samples/manifest.json', BASE).href);
        const manifest = await this.withTimeout(response.json(), 'Sample manifest');
        if (!manifest?.groups || typeof manifest.groups !== 'object') throw new Error('Invalid sample manifest');
        return manifest;
      })();
      this.manifestPromise = request;
      request.catch(() => { if (this.manifestPromise === request) this.manifestPromise = null; });
    }
    return this.manifestPromise;
  }

  async loadGroup(group) {
    if (this.samplers.has(group)) return this.samplers.get(group);
    if (this.pendingGroups.has(group)) return this.pendingGroups.get(group);
    let sampler;
    const state = { status: 'loading', loaded: 0, total: 0, error: null };
    this.sampleStates.set(group, state);
    const request = (async () => {
      try {
        const manifest = await this.getManifest();
        const spec = manifest.groups[group];
        if (!spec?.noteURLs || typeof spec.noteURLs !== 'object' || Array.isArray(spec.noteURLs)) throw new Error(`Missing sample group: ${group}`);
        const entries = Object.entries(spec.noteURLs);
        if (!entries.length || entries.length > 128 || spec.looping === true) throw new Error(`Invalid one-shot sample group: ${group}`);
        const sources = entries.map(([note, path]) => [note, localSampleURL(path)]);
        if (group !== PRESETS.drums) sources.sort((a, b) => sampleMidi(a[0]) - sampleMidi(b[0]));
        state.total = sources.length;
        this.notify(group);
        sampler = Sampler(this.context, {
          // 1.1.0's flat converter includes undefined defaults verbatim, which
          // otherwise overwrite detune=0 in resolveParams and yield NaN pitch.
          destination: this.master, volume: 127, velocity: 100, decayTime: 0.035,
          detune: 0, lpfCutoffHz: 20000,
          buffers: async (context, buffers) => {
            const decodedEntries = await Promise.all(sources.map(async ([note, url]) => {
              const response = await this.fetchLocal(url);
              const bytes = await this.withTimeout(response.arrayBuffer(), `Sample body ${note}`);
              const decoded = await this.withTimeout(context.decodeAudioData(bytes), `Sample decode ${note}`);
              if (!decoded || !(decoded.duration > 0)) throw new Error(`Invalid decoded sample: ${note}`);
              const calibration = calibrateSample(decoded);
              if (!this.sampleCalibration.has(group)) this.sampleCalibration.set(group, new Map());
              this.sampleCalibration.get(group).set(note, calibration);
              state.loaded += 1;
              this.notify(group);
              return [note, decoded];
            }));
            // smplr 1.1.0's spreadKeyRanges returns sorted regions but its
            // converter pairs them with input insertion order. Network decode
            // completion order must never choose an instrument's root pitches.
            for (const [note, decoded] of decodedEntries) buffers[note] = decoded;
          },
        });
        await sampler.ready;
        this.samplers.set(group, sampler);
        this.sampleNotes.set(group, new Set(entries.map(([note]) => note)));
        this.sampleCoverage.set(group, spec.coverageMidi || [0, 127]);
        state.status = 'ready';
        this.notify(group);
        return sampler;
      } catch (error) {
        sampler?.dispose?.();
        state.status = 'error';
        state.error = error instanceof Error ? error.message : String(error);
        this.notify(group);
        throw error;
      } finally { this.pendingGroups.delete(group); }
    })();
    this.pendingGroups.set(group, request);
    return request;
  }

  stopSampleVoice(entry, when = this.context?.currentTime) {
    this.sampleVoices.delete(entry);
    try { entry.stop?.(when); } catch { /* Continue stopping the other voices. */ }
  }

  startSample(group, note, time) {
    const sampler = this.samplers.get(group);
    if (!sampler || this.sampleStates.get(group)?.status !== 'ready') throw new Error(`Sample group is not ready: ${group}`);
    const matching = [...this.sampleVoices].filter(entry => entry.group === group && entry.note === note);
    while (matching.length >= this.maxPerNote) this.stopSampleVoice(matching.shift());
    while (this.sampleVoices.size >= this.maxPolyphony) this.stopSampleVoice(this.sampleVoices.values().next().value);
    const entry = { group, note, time, stop: null };
    this.sampleVoices.add(entry);
    try {
      entry.stop = sampler.start({
        note, time, loop: false, velocity: 100, ampRelease: 0.035,
        stopId: `miao-sample-${++this.sampleSerial}`,
        onEnded: () => { this.sampleVoices.delete(entry); },
      });
      if (typeof entry.stop !== 'function') throw new Error('Sampler did not return a cancellable voice');
      return entry.stop;
    } catch (error) { this.sampleVoices.delete(entry); throw error; }
  }

  play(key, preset = 'piano', when = this.context?.currentTime, engine = SAMPLED) {
    engineName(engine);
    if (!this.context || this.context.state !== 'running') throw new Error('Audio context is not running');
    const time = Math.max(Number.isFinite(when) ? when : this.context.currentTime, this.context.currentTime);
    if (engine === LEGACY) {
      // v1 event files used C=shaker and V=bongoHigh. Do not reinterpret their
      // stored key codes after the new drum labels become hat/tom.
      const voice = key.code === 'KeyC' ? 'shaker' : key.code === 'KeyV' ? 'bongoHigh' : key.voice;
      return super.play(voice === key.voice ? key : { ...key, voice }, preset, time);
    }
    groupsFor(preset);
    if (key.kind === 'drum') {
      const note = DRUM_ALIASES[key.voice];
      if (!note) throw new Error(`Unsupported sampled drum: ${key.voice}`);
      const spec = this.samplers.get(PRESETS.drums);
      if (!spec) throw new Error('Drum samples are not ready');
      // A missing manifest alias must not become smplr's default MIDI zero.
      if (!this.sampleNotes.get(PRESETS.drums)?.has(note)) throw new Error(`Drum sample is missing: ${note}`);
      if (note === 'closed-hat') {
        // Run within smplr's audio lookahead: an open hat scheduled far ahead
        // must first get to sound, rather than being cancelled when the later
        // closed-hat event is merely enqueued.
        spec.scheduler.schedule({ time }, () => {
          for (const entry of [...this.sampleVoices]) {
            if (entry.group === PRESETS.drums && entry.note === 'open-hat' && entry.time <= time) this.stopSampleVoice(entry, time);
          }
        });
      }
      return this.startSample(PRESETS.drums, note, time);
    }
    if (preset === 'drums') throw new Error('Select a melodic instrument before playing notes');
    const notes = key.kind === 'chord' ? key.notes : [key.midi];
    if (!Array.isArray(notes) || !notes.length || notes.length > 6 || notes.some(note => !Number.isInteger(note) || note < 0 || note > 127)) throw new Error('Invalid sampled MIDI note or chord');
    const group = PRESETS[preset];
    const range = this.sampleCoverage.get(group);
    if (range && notes.some(note => note < range[0] || note > range[1])) throw new Error(`Note is outside the sampled range for ${preset}`);
    return notes.map((note, index) => this.startSample(group, note, time + index * 0.015));
  }

  stopVoices() {
    for (const entry of [...this.sampleVoices]) this.stopSampleVoice(entry);
    for (const sampler of this.samplers.values()) {
      // stop() only stops active voices in smplr 1.1.0; pending scheduler events
      // must be cleared explicitly. The scheduler can be reused by start().
      sampler.scheduler?.stop();
      sampler.stop();
    }
    super.stopVoices();
  }
}
