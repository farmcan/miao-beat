// Native, local replay capture: the complete scene canvas + the app audio output.
// No microphone, screen capture, remote upload, encoder service or external runtime.
const TYPES={video:['video/mp4;codecs=avc1.420028,mp4a.40.2','video/mp4','video/webm;codecs=vp9,opus','video/webm;codecs=vp8,opus','video/webm'],audio:['audio/mp4;codecs=mp4a.40.2','audio/mp4','audio/webm;codecs=opus','audio/webm','audio/ogg;codecs=opus']};
export function mediaExtension(type){return type.includes('mp4')?(type.startsWith('audio/')?'m4a':'mp4'):type.includes('ogg')?'ogg':'webm';}
export function mediaSupported(kind,win=globalThis){return !!TYPES[kind]&&typeof win.MediaRecorder==='function'&&typeof win.MediaStream==='function'&&TYPES[kind].some(t=>win.MediaRecorder.isTypeSupported(t));}
export async function createMediaExport({audio,source,kind,doc=document,label='钢琴',caption=()=>'',maxBytes=128*1024*1024}){
  const win=doc.defaultView??globalThis,Recorder=win.MediaRecorder;
  if(!mediaSupported(kind,win)||!audio.context?.createMediaStreamDestination||!audio.analyser)throw Error('这个浏览器暂不支持此格式，请换 Chrome、Edge 或 Safari 试试。');
  if(kind==='video'&&(!source?.width||source.hidden))throw Error('角色画面还没准备好，等图加载后再试。');
  let destination,stream,videoStream,canvas,ctx,recorder,raf=0,guard,stopped=false,cancelled=false,size=0,settled=false;
  const chunks=[];let resolveDone,rejectDone,resolveReady,rejectReady;
  const done=new Promise((r,j)=>{resolveDone=r;rejectDone=j;});done.catch(()=>{});
  const ready=new Promise((r,j)=>{resolveReady=r;rejectReady=j;});
  const cleanup=()=>{win.cancelAnimationFrame(raf);win.clearTimeout(guard);try{audio.analyser.disconnect(destination);}catch{}for(const t of new Set([...(stream?.getTracks()??[]),...(videoStream?.getTracks()??[])]))t.stop();doc.removeEventListener('visibilitychange',hidden);};
  function fail(reason){if(settled)return;settled=true;cancelled=true;try{if(recorder?.state!=='inactive')recorder?.stop();}catch{}cleanup();const error=reason instanceof Error?reason:new Error(reason);rejectReady(error);rejectDone(error);}
  function hidden(){if(doc.hidden)fail('导出已取消：请留在当前页面，重新点导出。');}
  function paint(){
    if(cancelled||settled)return;
    try{
      ctx.fillStyle='#f8f4eb';ctx.fillRect(0,0,720,880);
      ctx.fillStyle='#61412e';ctx.font='600 21px system-ui';ctx.textAlign='left';ctx.fillText('MIAO / BEAT',30,43);
      ctx.textAlign='right';ctx.font='17px system-ui';ctx.fillText(String(label).slice(0,24),690,43);
      // This is one complete cat+both-paws+instrument frame, never separate limbs.
      ctx.drawImage(source,0,70,720,720);
      ctx.fillStyle='#eadfce';ctx.fillRect(30,797,660,56);ctx.textAlign='center';ctx.fillStyle='#61412e';ctx.font='19px system-ui';ctx.fillText(String(caption()).slice(0,140),360,832,640);
    }catch{fail('画面录制中断，请重新导出。');}
  }
  function draw(){paint();if(!settled)raf=win.requestAnimationFrame(draw);}
  try{
    destination=audio.context.createMediaStreamDestination();audio.analyser.connect(destination);
    const tracks=[...destination.stream.getAudioTracks()];if(!tracks.length)throw Error('音频流没有准备好。');
    if(kind==='video'){
      canvas=doc.createElement('canvas');canvas.width=720;canvas.height=880;ctx=canvas.getContext('2d');
      if(!ctx||typeof canvas.captureStream!=='function')throw Error('这个浏览器暂不支持画面导出，仍可导出音频。');
      draw();if(settled)throw Error('画面准备失败。');videoStream=canvas.captureStream(60);tracks.push(...videoStream.getVideoTracks());
    }
    stream=new win.MediaStream(tracks);
    for(const mimeType of TYPES[kind])if(Recorder.isTypeSupported(mimeType)){try{recorder=new Recorder(stream,{mimeType,audioBitsPerSecond:192000,...(kind==='video'?{videoBitsPerSecond:2500000}:{})});break;}catch{}}
    if(!recorder)throw Error('浏览器没有可用的编码器，请尝试另一种导出或换个浏览器。');
    recorder.onstart=()=>resolveReady();
    recorder.ondataavailable=e=>{if(settled||!e.data?.size)return;size+=e.data.size;if(size>maxBytes){fail('文件超过128 MB，已取消。请缩短片段后再试。');return;}chunks.push(e.data);};
    recorder.onerror=()=>fail('编码失败，已停止。按键片段还在，可以重新导出。');
    recorder.onstop=()=>{
      if(settled)return;settled=true;cleanup();
      if(cancelled||!chunks.length){rejectDone(new Error('没有生成可保存的媒体文件。'));return;}
      const mimeType=recorder.mimeType||chunks[0].type;
      const blob=new win.Blob(chunks,{type:mimeType});resolveDone({blob,mimeType,extension:mediaExtension(mimeType),kind});
    };
    doc.addEventListener('visibilitychange',hidden);
    guard=win.setTimeout(()=>fail('导出超时，按键片段仍保留。请重新尝试。'),306000);
    recorder.start(1000);
    const startup=win.setTimeout(()=>fail('编码器启动失败，请换个浏览器。'),5000);
    try{await ready;}finally{win.clearTimeout(startup);}
    return {kind,done,stop(){if(!settled&&!stopped){stopped=true;try{recorder.stop();}catch{fail('无法完成文件，请重试。');}}},cancel(message='导出已取消，按键片段还在。'){fail(message);}};
  }catch(error){fail(error);await ready.catch(()=>{});throw error;}
}
