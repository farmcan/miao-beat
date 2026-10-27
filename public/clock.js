// Audio-clock scheduling; all three tones are original Web Audio synthesis.
export const METRONOME_SOUNDS={wood:'木块',bell:'钟声',electronic:'电子'};
export function beatPattern(meter,sound='bell',accent='last'){
  const normal=sound==='bell'?'当':sound==='wood'?'咚':'哒',strong=sound==='bell'?'叮':sound==='wood'?'嗒':'嘀';
  return Array.from({length:meter},(_,i)=>i===(accent==='last'?meter-1:0)?strong:normal).join(' · ');
}
export class BeatClock {
  constructor(audio,onBeat){this.audio=audio;this.onBeat=onBeat;this.running=false;this.nodes=new Set();this.queue=[];this.history=[];this.sound='bell';this.accent='last';}
  setSound(sound,accent='last'){
    if(!Object.hasOwn(METRONOME_SOUNDS,sound)||!['first','last'].includes(accent))throw Error('Unknown metronome sound');
    this.sound=sound;this.accent=accent;
  }
  start(bpm=96,meter=4,origin){
    this.stop();this.bpm=bpm;this.meter=meter;this.beat=0;this.origin=origin;this.next=origin??this.audio.context.currentTime+.04;this.running=true;
    this.schedule();this.timer=setInterval(()=>this.schedule(),25);
  }
  schedule(){
    const now=this.audio.context.currentTime;
    if(this.next<now-.05){
      if(this.origin!==undefined){const index=Math.ceil((now-this.origin)/(60/this.bpm));this.next=this.origin+index*60/this.bpm;this.beat=index%this.meter;}
      else{this.next=now+.04;this.beat=0;}
      this.queue=this.queue.filter(item=>item.time>=now-.05);
    }
    while(this.running&&this.next<now+.1){
      const accent=this.beat===(this.accent==='last'?this.meter-1:0);
      this.click(this.next,accent);this.queue.push({time:this.next,beat:this.beat,accent});
      this.history.push({time:this.next,beat:this.beat,accent,sound:this.sound});if(this.history.length>32)this.history.shift();
      this.next+=60/this.bpm;this.beat=(this.beat+1)%this.meter;
    }
  }
  click(time,accent){
    const c=this.audio.context;
    const pitch=this.sound==='bell'?(accent?1320:440):this.sound==='wood'?(accent?1450:380):(accent?1600:650);
    const duration=this.sound==='bell'?(accent?.24:.16):this.sound==='wood'?(accent?.10:.045):(accent?.075:.035);
    const partials=this.sound==='bell'?[[1,1],[2.76,.22],[4.07,.08]]:this.sound==='wood'?[[1,1],[2.6,.3]]:[[1,1]];
    for(const [ratio,level]of partials){
      const o=c.createOscillator(),g=c.createGain();o.type=this.sound==='electronic'?'square':'sine';o.frequency.value=pitch*ratio;
      const amplitude=(accent?.22:.13)*level/(this.sound==='electronic'?2:1),end=time+duration/Math.sqrt(ratio);
      g.gain.setValueAtTime(.0001,time);g.gain.exponentialRampToValueAtTime(amplitude,time+.002);g.gain.exponentialRampToValueAtTime(.0001,end);
      o.connect(g);g.connect(this.audio.master);const item={o,g};this.nodes.add(item);o.start(time);o.stop(end+.01);
      o.onended=()=>{o.disconnect();g.disconnect();this.nodes.delete(item);};
    }
  }
  render(){const now=this.audio.context?.currentTime??0;while(this.queue.length&&this.queue[0].time<=now){const e=this.queue.shift();this.onBeat(e.beat,e.accent);}}
  stop(){
    this.running=false;clearInterval(this.timer);this.queue=[];
    for(const {o,g}of this.nodes){try{g.gain.cancelScheduledValues(0);g.gain.value=0;o.stop();}catch{}o.disconnect();g.disconnect();}
    this.nodes.clear();
  }
}
