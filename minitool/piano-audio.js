/* Bounded local-buffer adapter, reusing SampledAudio calibration/voice policy.
 * Adapted for eight white keys; not the full smplr Sampler. No URL loader, effects, network or synth fallback.
 * Code MIT; velocity gain formula credited to smplr1.1.0 in NOTICES.json.
 */
(function (root) {
  'use strict';
  function calibrateSample(buffer) {
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

  function midi(note) {
    return {C4:60,'D#4':63,'F#4':66,A4:69,C5:72}[note];
  }
  function decode(context, bytes) {
    return new Promise(function (resolve,reject) {
      var settled=false;
      function ok(value) { if (!settled) { settled=true;resolve(value); } }
      function fail(error) { if (!settled) { settled=true;reject(error || new Error('DecodeError')); } }
      try { var result=context.decodeAudioData(bytes,ok,fail); if(result && typeof result.then==='function')result.then(ok,fail); }
      catch(error){fail(error);}
    });
  }
  function unpack(sample) {
    if(!sample || sample.format!=='audio/mpeg' || sample.encoding!=='base64' || !Number.isInteger(sample.bytes) || sample.bytes<=0 || sample.bytes>100*1024)throw new Error('Invalid explicit audio bytes');
    if(typeof sample.base64!=='string' || !/^[A-Za-z0-9+/]+={0,2}$/.test(sample.base64) || sample.base64.length%4!==0)throw new Error('Invalid audio encoding');
    var binary=root.atob(sample.base64);if(binary.length!==sample.bytes)throw new Error('Audio byte count mismatch');
    var array=new Uint8Array(binary.length);for(var i=0;i<binary.length;i+=1)array[i]=binary.charCodeAt(i);
    return array.buffer;
  }
  class PianoAudio extends root.MiaoBeatCatAudio {
    constructor(){super();this.buffers=new Map();this.active=new Set();this.loadToken=0;this.state='idle';this.decoded=0;this.error='';this.lastSource='';this.onProgress=null;}
    diagnostics(){return{engine:'local-piano-buffer-v1',state:this.state,decoded:this.decoded,total:5,activeVoices:this.active.size,lastSource:this.lastSource,lastError:this.error,sourceVersion:'existing2019-small;not a new2022download'};}
    notify(){if(typeof this.onProgress==='function')this.onProgress();}
    async ready(){
      var token=++this.loadToken;
      var context=await super.ready();
      if(token!==this.loadToken)throw new Error('Preparation cancelled');
      if(this.buffers.size===5){this.state='ready';this.notify();return context;}
      this.state='decoding';this.decoded=0;this.error='';this.notify();
      var local=new Map();var notes=['C4','D#4','F#4','A4','C5'];
      try {
        for(var i=0;i<notes.length;i+=1){
          if(token!==this.loadToken)throw new Error('Preparation cancelled');
          var note=notes[i];var sample=root.MIAO_PIANO_BYTES.samples[note];
          var decoded=await decode(context,unpack(sample));
          if(token!==this.loadToken)throw new Error('Preparation cancelled');
          if(!decoded || !(decoded.duration>0) || !(decoded.length>0) || decoded.numberOfChannels<1)throw new Error('Empty decoded audio');
          calibrateSample(decoded);local.set(note,decoded);this.decoded=local.size;this.notify();
        }
        if(context.state!=='running')throw new Error('AudioContext suspended');
        this.buffers=local;this.state='ready';this.notify();return context;
      }catch(error){
        if(token===this.loadToken){this.buffers.clear();this.state='error';this.error=(notes[Math.min(this.decoded,4)]||'sample')+': '+String(error && error.name || 'DecodeError');this.notify();}
        throw error;
      }
    }
    endVoice(entry){
      if(!this.active.has(entry))return;
      this.active.delete(entry);
      try{entry.gain.gain.cancelScheduledValues(0);entry.gain.gain.value=0;entry.source.stop();}catch(_){}
      try{entry.source.disconnect();entry.gain.disconnect();}catch(_){}
    }
    stopVoices(){
      this.loadToken+=1;if(this.state==='decoding')this.state='cancelled';
      Array.from(this.active).forEach(entry=>this.endVoice(entry));super.stopVoices();
    }
    play(key,when){
      if(this.state!=='ready' || this.buffers.size!==5 || !this.context || this.context.state!=='running')throw new Error('Piano samples are not ready');
      var played={KeyA:60,KeyS:62,KeyD:64,KeyF:65,KeyG:67,KeyH:69,KeyJ:71,KeyK:72}[key.code];if(played===undefined)throw new Error('Unsupported key');
      var notes=Array.from(this.buffers.keys()).sort((a,b)=>Math.abs(midi(a)-played)-Math.abs(midi(b)-played));
      var note=notes[0];if(Math.abs(midi(note)-played)>1)throw new Error('Unreviewed pitch range');
      var matching=Array.from(this.active).filter(entry=>entry.code===key.code);
      while(matching.length>=3)this.endVoice(matching.shift());
      while(this.active.size>=12)this.endVoice(this.active.values().next().value);
      var source=this.context.createBufferSource(),gain=this.context.createGain();var now=Number.isFinite(when)?Math.max(when,this.context.currentTime):this.context.currentTime;
      source.buffer=this.buffers.get(note);source.loop=false;source.playbackRate.setValueAtTime(Math.pow(2,(played-midi(note))/12),now);
      // Same velocity100 convention as the existing smplr-backed path.
      gain.gain.setValueAtTime(100*100/16129,now);source.connect(gain);gain.connect(this.master);
      var entry={source:source,gain:gain,code:key.code};this.active.add(entry);this.lastSource=note;
      source.onended=()=>{this.active.delete(entry);try{source.disconnect();gain.disconnect();}catch(_){}};
      try{source.start(now);}catch(error){this.endVoice(entry);throw error;}
    }
  }
  root.MiaoBeatPianoAudio=PianoAudio;
}(window));
