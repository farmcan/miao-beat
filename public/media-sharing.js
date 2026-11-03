// Prepare files before a tap: share() must run inside that tap's activation.
export function mountMediaSharing(doc,{isBusy=()=>false}={}){
  const win=doc.defaultView,navigator=win.navigator,files=new Map();let pending=false;
  const status=doc.getElementById('shareStatus');
  const button=kind=>doc.getElementById(kind==='video'?'shareVideo':'shareAudio');
  function refresh(){for(const kind of ['video','audio']){const b=button(kind);b.hidden=!files.has(kind);b.disabled=pending||isBusy();}}
  function setMedia(kind,{blob,name}){
    files.delete(kind);
    try{if(win.File&&typeof navigator.share==='function'&&typeof navigator.canShare==='function'){
      const file=new win.File([blob],name,{type:blob.type.split(';')[0]});
      if(navigator.canShare({files:[file]}))files.set(kind,file);
    }}catch{/* Saving the existing file remains available. */}
    status.textContent=files.size?'可点“分享”选择手机上的应用；也可以保存文件。':'这个浏览器暂不支持文件分享，可用“保存”下载文件。';refresh();
  }
  async function share(kind){
    if(pending||isBusy()||!files.has(kind))return;
    pending=true;refresh();status.textContent='请选择分享方式；文件仍保留在此页。';
    try{await navigator.share({files:[files.get(kind)]});status.textContent='已交给系统分享，请在目标应用确认；文件仍可保存。';}
    catch(error){status.textContent=error?.name==='AbortError'?'已取消分享，文件仍在，可以重试或保存。':'没有完成分享，文件仍在，请重试或使用“保存”。';}
    finally{pending=false;refresh();}
  }
  for(const kind of ['video','audio'])button(kind).addEventListener('click',()=>{void share(kind);});
  refresh();return {setMedia,refresh};
}
