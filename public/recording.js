// Compact, versioned one-shot event format. Imports are data, never executable.
export const ENGINE='sample-v1',MAX_MS=300000,MAX_EVENTS=5000;
const keys=['A','S','D','F','G','H','J','K','W','E','T','Y','U','Z','X','C','V'];
// Never reorder the v1 prefix: persisted recordings encode keys by array index.
export const CODES=Object.freeze([...keys.map(key=>'Key'+key),'KeyB','KeyN','KeyM','KeyL','Digit1','Digit2','Digit3','Digit4']);
export function makeRecording(instrument,bpm,meter){return {format:'miao-beat',version:2,engine:ENGINE,instrument,bpm,meter,duration:0,events:[]};}
export function validateRecording(value){
  if(!value||Array.isArray(value)||value.format!=='miao-beat')throw Error('不是支持的 Miao Beat 演奏文件');
  const legacy=value.version===1&&value.engine==='ui-synth-v1';
  if(!legacy&&!(value.version===2&&value.engine===ENGINE))throw Error('不是支持的 Miao Beat v1/v2 文件');
  const instruments=legacy?['marimba','sparkle']:['piano','marimba','guitar','drums'];
  if(!instruments.includes(value.instrument)||!Number.isInteger(value.bpm)||value.bpm<50||value.bpm>180||!(legacy?[3,4]:[2,3,4]).includes(value.meter))throw Error('音色或节拍信息不正确');
  if(!Number.isInteger(value.duration)||value.duration<0||value.duration>MAX_MS||!Array.isArray(value.events)||value.events.length>MAX_EVENTS)throw Error('文件超过 5 分钟或 5000 次敲击上限');
  let previous=-1,left=0;
  const events=value.events.map((event,index)=>{
    if(!Array.isArray(event)||event.length!==2)throw Error('敲击记录格式不正确');
    const [time,code]=event;
    if(!Number.isInteger(time)||time<previous||time<0||time>value.duration||!Number.isInteger(code)||code<0||code>=(legacy?keys.length:CODES.length))throw Error('敲击时间或编码不正确');
    if(!legacy&&((value.instrument==='drums'&&(code<13||code>20))||(['piano','marimba'].includes(value.instrument)&&code>=21)))throw Error('按键与所选乐器不匹配');
    while(left<index&&value.events[left][0]<=time-100)left++;if(index-left>=32)throw Error('短时间内敲击过密，无法安全回放');
    previous=time;return [time,code];
  });
  return {format:'miao-beat',version:value.version,engine:value.engine,instrument:value.instrument,bpm:value.bpm,meter:value.meter,duration:value.duration,events};
}
