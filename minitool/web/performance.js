// Container owns native fullscreen. Keep the shared CSS playing surface.
export function mountPerformance(doc){
 const body=doc.body,button=doc.getElementById('performanceToggle'),exitButton=doc.getElementById('performanceExit'),status=doc.getElementById('performanceStatus');let active=false;
 function paint(){body.classList.toggle('performance-mode',active);button.disabled=false;button.hidden=active;exitButton.hidden=!active;body.dataset.performanceMode=active?'page':'off';button.setAttribute('aria-pressed',String(active));doc.dispatchEvent(new CustomEvent('performance-mode-change',{detail:{active}}));status.textContent=active?'横过手机，可同屏看谱与弹奏。':'';}
 function enter(){active=true;paint();}function exit(){active=false;paint();}button.addEventListener('click',enter);exitButton.addEventListener('click',exit);paint();return{enter,exit,destroy:exit};
}
