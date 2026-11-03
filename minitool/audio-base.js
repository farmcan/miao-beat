/* MIT. Reduced from public/audio.js: master/compressor/analyser only.
 * The sampled adapter provides all notes; no synthesized sound fallback. */
(function(root){
 'use strict';
 class CatAudio{
  constructor(){this.context=null;this.volume=.55;}
  async ready(){
   if(!this.context){
    var Context=root.AudioContext||root.webkitAudioContext;
    if(!Context)throw new Error('当前环境暂不支持声音');
    this.context=new Context({latencyHint:'interactive'});var c=this.context;
    this.master=c.createGain();this.master.gain.value=this.volume*.42;
    this.compressor=c.createDynamicsCompressor();this.compressor.threshold.value=-14;this.compressor.knee.value=15;this.compressor.ratio.value=5;
    this.analyser=c.createAnalyser();this.analyser.fftSize=512;
    this.master.connect(this.compressor);this.compressor.connect(this.analyser);this.analyser.connect(c.destination);
   }
   if(this.context.state!=='running')await this.context.resume();
   if(this.context.state!=='running')throw new Error('请再次点准备声音');
   return this.context;
  }
  setVolume(value){this.volume=value;if(this.master)this.master.gain.setTargetAtTime(value*.42,this.context.currentTime,.015);}
  stopVoices(){}
 }
 root.MiaoBeatCatAudio=CatAudio;
}(window));
