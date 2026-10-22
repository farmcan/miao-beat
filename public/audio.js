// Original Web Audio synthesis. No sampled audio or third-party audio runtime.
export class CatAudio {
  constructor(){this.context=null;this.volume=.55;this.peak=0;this.voices=new Set();}
  async ready(){
    if(!this.context){
      const Context=globalThis.AudioContext||globalThis.webkitAudioContext;
      if(!Context)throw new Error('unsupported');
      this.context=new Context({latencyHint:'interactive'});
      const c=this.context;
      this.master=c.createGain();this.master.gain.value=this.volume*.42;
      this.compressor=c.createDynamicsCompressor();this.compressor.threshold.value=-14;this.compressor.knee.value=15;this.compressor.ratio.value=5;
      this.analyser=c.createAnalyser();this.analyser.fftSize=512;this.samples=new Float32Array(this.analyser.fftSize);
      this.master.connect(this.compressor);this.compressor.connect(this.analyser);this.analyser.connect(c.destination);
      this.noise=c.createBuffer(1,c.sampleRate,c.sampleRate);const data=this.noise.getChannelData(0);
      for(let i=0;i<data.length;i++)data[i]=Math.random()*2-1;
    }
    if(this.context.state!=='running')await this.context.resume();
    if(this.context.state!=='running')throw new Error('suspended');
    return this.context;
  }
  track(source,gain,extra=[]){
    if(this.voices.size>=96){const oldest=this.voices.values().next().value;try{oldest.gain.gain.cancelScheduledValues(0);oldest.gain.gain.value=0;oldest.source.stop();}catch{}this.voices.delete(oldest);}
    const entry={source,gain,extra};this.voices.add(entry);
    source.onended=()=>{for(const n of [source,gain,...extra])n.disconnect();this.voices.delete(entry);};
  }
  stopVoices(){
    for(const {source,gain}of this.voices){try{gain.gain.cancelScheduledValues(0);gain.gain.value=0;source.stop();}catch{}}
  }
  setVolume(value){this.volume=value;if(this.master)this.master.gain.setTargetAtTime(value*.42,this.context.currentTime,.015);}
  level(){if(!this.analyser)return 0;this.analyser.getFloatTimeDomainData(this.samples);let sum=0;for(const n of this.samples)sum+=n*n;const rms=Math.sqrt(sum/this.samples.length);this.peak=Math.max(this.peak,rms);return rms;}
  tone(frequency,duration,amplitude,type='sine',endFrequency=null,delay=0){
    const c=this.context,t=(this.startTime??c.currentTime)+delay,o=c.createOscillator(),g=c.createGain();
    o.type=type;o.frequency.setValueAtTime(frequency,t);
    if(endFrequency)o.frequency.exponentialRampToValueAtTime(endFrequency,t+duration*.8);
    g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(Math.max(amplitude,.0002),t+.004);g.gain.exponentialRampToValueAtTime(.0001,t+duration);
    o.connect(g);g.connect(this.master);o.start(t);o.stop(t+duration+.02);this.track(o,g);
  }
  hiss(duration,amplitude,frequency,type='highpass',delay=0){
    const c=this.context,t=(this.startTime??c.currentTime)+delay,n=c.createBufferSource(),f=c.createBiquadFilter(),g=c.createGain();
    n.buffer=this.noise;f.type=type;f.frequency.value=frequency;f.Q.value=type==='bandpass'?.8:.7;
    g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(amplitude,t+.003);g.gain.exponentialRampToValueAtTime(.0001,t+duration);
    n.connect(f);f.connect(g);g.connect(this.master);n.start(t,Math.random()*.3);n.stop(t+duration+.015);this.track(n,g,[f]);
  }
  play(key,timbre='marimba',when=this.context.currentTime){
    this.startTime=Math.max(when,this.context.currentTime);
    if(key.kind==='note'){
      const f=key.frequency;
      if(timbre==='sparkle'){this.tone(f,.52,.4,'triangle');this.tone(f*2,.36,.11);this.tone(f*3,.24,.045);}
      else{this.tone(f,.65,.65);this.tone(f*4,.10,.18);this.tone(f*9,.035,.035);}
      return;
    }
    switch(key.voice){
      case 'bongoLow':this.tone(230,.24,.85,'sine',95);this.tone(410,.055,.12,'triangle',220);break;
      case 'bongoHigh':this.tone(360,.18,.75,'sine',160);this.tone(700,.04,.1,'triangle',400);break;
      case 'kick':this.tone(155,.4,.95,'sine',43);this.hiss(.025,.1,1800);break;
      case 'snare':this.hiss(.18,.55,1700,'bandpass');this.tone(180,.12,.28,'triangle',130);break;
      case 'cymbal':this.hiss(.53,.35,6000);this.tone(7200,.12,.025,'square');break;
      case 'shaker':this.hiss(.07,.4,4700,'bandpass');this.hiss(.085,.27,5400,'bandpass',.055);break;
      case 'cowbell':this.tone(540,.16,.15,'square');this.tone(800,.12,.11,'square');break;
      case 'meow':{
        const c=this.context,t=this.startTime,o=c.createOscillator(),f=c.createBiquadFilter(),g=c.createGain(),v=c.createOscillator(),vg=c.createGain();
        o.type='sawtooth';o.frequency.setValueAtTime(480,t);o.frequency.exponentialRampToValueAtTime(790,t+.09);o.frequency.exponentialRampToValueAtTime(270,t+.43);
        f.type='bandpass';f.Q.value=2.4;f.frequency.setValueAtTime(1000,t);f.frequency.linearRampToValueAtTime(1550,t+.12);f.frequency.linearRampToValueAtTime(640,t+.43);
        g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.45,t+.025);g.gain.exponentialRampToValueAtTime(.0001,t+.46);
        v.frequency.value=6;vg.gain.value=12;v.connect(vg);vg.connect(o.frequency);o.connect(f);f.connect(g);g.connect(this.master);v.start(t);o.start(t);o.stop(t+.48);v.stop(t+.48);this.track(o,g,[v,vg,f]);break;
      }
    }
  }
}
