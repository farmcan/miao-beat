// React to viewport/OS orientation when exposed; offer an in-page fallback for locked hosts.
export function mountLayout(doc){
 const win=doc.defaultView,body=doc.body,bench=doc.querySelector('.workbench');body.classList.add('mini-app');
 const guide=doc.createElement('div');guide.className='mini-layout-guide';guide.id='layoutGuide';const text=doc.createElement('p');text.id='orientationHint';const toggle=doc.createElement('button');toggle.id='layoutToggle';toggle.type='button';guide.append(text,toggle);bench.querySelector('.bench-topline').after(guide);
 let manual=null,frame=0;
 function paint(){frame=0;const width=win.innerWidth||doc.documentElement.clientWidth,height=win.visualViewport?win.visualViewport.height:win.innerHeight;
  const nativeTop=parseFloat(doc.documentElement.style.getPropertyValue('--native-top'))||0,available=Math.max(200,height-nativeTop);
  let angle=win.screen&&win.screen.orientation&&win.screen.orientation.angle;if(typeof angle!=='number')angle=win.orientation;
  const osWide=typeof angle==='number'&&Math.abs(angle)%180===90,rotate=width<height&&(manual===null?osWide:manual),wide=width>height||rotate;
  body.classList.toggle('mini-rotated',rotate);body.classList.toggle('mini-wide',wide);body.dataset.miniLayout=wide?'landscape':'portrait';
  doc.documentElement.style.setProperty('--mini-width',width+'px');doc.documentElement.style.setProperty('--mini-height',available+'px');
  toggle.textContent=rotate?'恢复竖屏布局':'横屏布局';toggle.hidden=width>height;toggle.setAttribute('aria-pressed',String(rotate));
  text.textContent=wide?'横屏布局 · 全部琴键同屏显示':'竖屏已显示全部琴键。推荐横过手机看谱；没有自动变化时，点“横屏布局”。';
  win.dispatchEvent(new win.Event('mini-layout-change'));
 }
 function schedule(){if(!frame)frame=win.requestAnimationFrame(paint);}
 function orientationChanged(){manual=null;schedule();}
 toggle.addEventListener('click',()=>{manual=!body.classList.contains('mini-rotated');paint();});win.addEventListener('resize',schedule);win.addEventListener('orientationchange',orientationChanged);
 if(win.visualViewport)win.visualViewport.addEventListener('resize',schedule);
 if(win.screen&&win.screen.orientation&&win.screen.orientation.addEventListener)win.screen.orientation.addEventListener('change',orientationChanged);
 paint();return{destroy(){win.removeEventListener('resize',schedule);win.removeEventListener('orientationchange',orientationChanged);if(win.visualViewport)win.visualViewport.removeEventListener('resize',schedule);if(win.screen&&win.screen.orientation&&win.screen.orientation.removeEventListener)win.screen.orientation.removeEventListener('change',orientationChanged);if(frame)win.cancelAnimationFrame(frame);guide.remove();}};
}
