// MIT. Local buffer adapter for the subset of smplr1.1.0 Sampler used by Miao Beat.
// Pitch interpolation and midiVelToGain convention follow smplr (bundled notice).
// No URL loading, network, effect racks or arbitrary sampler presets.
function midi(name){var m=/^([A-G])([#b]?)(-?\d+)$/.exec(name);return m?(Number(m[3])+1)*12+({C:0,D:2,E:4,F:5,G:7,A:9,B:11}[m[1]])+(m[2]==='#'?1:m[2]==='b'?-1:0):null;}
export function Sampler(context,options){
 const buffers={},voices=new Set(),timers=new Set();
 const result={ready:null,scheduler:{schedule({time},fn){const timer=setTimeout(()=>{timers.delete(timer);fn();},Math.max(0,(time-context.currentTime-.01)*1000));timers.add(timer);},stop(){for(const timer of timers)clearTimeout(timer);timers.clear();}},
 start({note,time,velocity=100,onEnded}){
  const names=Object.keys(buffers),root=typeof note==='number'?names.slice().sort((a,b)=>Math.abs(midi(a)-note)-Math.abs(midi(b)-note))[0]:note;
  if(!buffers[root])throw Error('Missing local sample');const source=context.createBufferSource(),gain=context.createGain();source.buffer=buffers[root];source.loop=false;
  const at=Math.max(context.currentTime,time);if(typeof note==='number')source.playbackRate.setValueAtTime(Math.pow(2,(note-midi(root))/12),at);
  gain.gain.setValueAtTime(velocity*velocity/16129,at);source.connect(gain);gain.connect(options.destination);
  let ended=false;const stop=(when=context.currentTime)=>{if(ended)return;try{gain.gain.cancelScheduledValues(when);gain.gain.setTargetAtTime(.00001,when,.008);source.stop(when+.035);}catch{}};
  const voice={stop};voices.add(voice);source.onended=()=>{ended=true;voices.delete(voice);source.disconnect();gain.disconnect();if(onEnded)onEnded();};source.start(at);return stop;
 },stop(){for(const voice of voices)voice.stop();},dispose(){result.scheduler.stop();result.stop();}};
 result.ready=Promise.resolve(options.buffers(context,buffers)).then(()=>result);return result;
}
