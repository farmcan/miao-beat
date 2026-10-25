// Browser fullscreen is optional: the large playing surface also works without it.
export function mountPerformance(doc=document){
  const button=doc.getElementById('performanceToggle'),status=doc.getElementById('performanceStatus');
  if(!button)return {destroy(){}};
  const exitButton=doc.getElementById('performanceExit');
  const win=doc.defaultView,root=doc.documentElement,body=doc.body;
  let active=false,nativeSession=false,pending=false,destroyed=false,savedScroll=0,revision=0;
  const current=()=>doc.fullscreenElement||doc.webkitFullscreenElement;
  const paint=()=>{
    body.classList.toggle('performance-mode',active);button.setAttribute('aria-pressed',String(active));
    button.textContent=active?'退出演奏':'全屏演奏';button.disabled=pending;
    if(exitButton){button.hidden=active;exitButton.hidden=!active;exitButton.disabled=pending;}
    body.dataset.performanceMode=active?(nativeSession?'native':'page'):'off';
  };
  function close(){
    active=false;nativeSession=false;pending=false;revision++;paint();
    if(status)status.textContent='';
    win.requestAnimationFrame(()=>{if(!active&&!destroyed)win.scrollTo?.(0,savedScroll);});
  }
  function changed(){
    if(destroyed)return;
    if(current()===root){const cancelled=!active;active=true;nativeSession=true;pending=false;paint();if(cancelled)void exit();}
    else if(nativeSession)close();
  }
  async function enter(){
    if(active||destroyed)return;const token=++revision;savedScroll=win.scrollY||0;active=true;paint();
    if(status)status.textContent='横过手机，琴键会大些。';
    const request=root.requestFullscreen||root.webkitRequestFullscreen;
    if(!request||doc.fullscreenEnabled===false)return;
    pending=true;paint();
    try{
      delete body.dataset.fullscreenError;
      // Called directly inside the click gesture, before any async work.
      await request.call(root,{navigationUI:'hide'});
      if(token!==revision||destroyed){if(!destroyed&&current()===root&&!active)changed();return;}
      nativeSession=current()===root;
    }catch(error){
      body.dataset.fullscreenError=error?.name||'Error';
      // iPhone/embedded browsers may reject element fullscreen. Keep the usable
      // page-filling mode rather than a disabled button or a misleading error.
      if(token===revision&&status)status.textContent='演奏区已展开，点“退出演奏”返回。';
    }finally{if(token===revision&&!destroyed){pending=false;paint();}}
  }
  async function exit(){
    if(!active||destroyed)return;const token=revision;
    const exitFullscreen=doc.exitFullscreen||doc.webkitExitFullscreen;
    pending=true;paint();
    try{
      if(current()===root&&exitFullscreen)await exitFullscreen.call(doc);
    }catch{
      if(token===revision&&current()===root&&status)status.textContent='请用浏览器的退出全屏按钮返回。';
      return;
    }finally{if(token===revision&&!destroyed){pending=false;paint();}}
    if(token!==revision||destroyed||current()===root)return;
    if(active)close();
  }
  const toggle=()=>{if(pending)return;if(active)void exit();else void enter();};
  const escape=event=>{if(event.key==='Escape'&&active&&!current()){event.preventDefault();close();}};
  button.addEventListener('click',toggle);exitButton?.addEventListener('click',toggle);doc.addEventListener('fullscreenchange',changed);doc.addEventListener('webkitfullscreenchange',changed);doc.addEventListener('keydown',escape);
  paint();
  return {destroy(){destroyed=true;revision++;button.removeEventListener('click',toggle);exitButton?.removeEventListener('click',toggle);doc.removeEventListener('fullscreenchange',changed);doc.removeEventListener('webkitfullscreenchange',changed);doc.removeEventListener('keydown',escape);body.classList.remove('performance-mode');delete body.dataset.performanceMode;button.hidden=false;button.disabled=false;button.textContent='全屏演奏';button.setAttribute('aria-pressed','false');if(exitButton){exitButton.hidden=true;exitButton.disabled=false;}if(status)status.textContent='';}};
}
