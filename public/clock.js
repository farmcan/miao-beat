// Bounded audio-clock lookahead, as described in web.dev/audio-scheduling.
// Independent implementation; manual key hits never wait for this scheduler.
export class BeatClock {
  constructor(audio,onBeat){this.audio=audio;this.onBeat=onBeat;this.running=false;this.nodes=new Set();this.queue=[];this.history=[];}
  start(bpm=96,meter=4){
    this.stop();this.bpm=bpm;this.meter=meter;this.beat=0;this.next=this.audio.context.currentTime+.04;this.running=true;
    this.schedule();this.timer=setInterval(()=>this.schedule(),25);
  }
  schedule(){
    const now=this.audio.context.currentTime;
    if(this.next<now-.05){this.next=now+.04;this.beat=0;}
    while(this.running&&this.next<now+.1){
      this.click(this.next,this.beat===0);this.queue.push({time:this.next,beat:this.beat});
      this.history.push({time:this.next,beat:this.beat});if(this.history.length>32)this.history.shift();
      this.next+=60/this.bpm;this.beat=(this.beat+1)%this.meter;
    }
  }
  click(time,accent){
    const c=this.audio.context,o=c.createOscillator(),g=c.createGain();o.frequency.value=accent?1320:880;
    g.gain.setValueAtTime(.0001,time);g.gain.exponentialRampToValueAtTime(accent?.20:.11,time+.002);g.gain.exponentialRampToValueAtTime(.0001,time+.035);
    o.connect(g);g.connect(this.audio.master);const item={o,g};this.nodes.add(item);o.start(time);o.stop(time+.04);
    o.onended=()=>{o.disconnect();g.disconnect();this.nodes.delete(item);};
  }
  render(){const now=this.audio.context?.currentTime??0;while(this.queue.length&&this.queue[0].time<=now)this.onBeat(this.queue.shift().beat);}
  stop(){
    this.running=false;clearInterval(this.timer);this.queue=[];
    for(const {o,g}of this.nodes){try{g.gain.cancelScheduledValues(0);g.gain.value=0;o.stop();}catch{}o.disconnect();g.disconnect();}
    this.nodes.clear();
  }
}
