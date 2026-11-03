import {scoreEvents} from './scores.js';
// Page boundaries never change source indices, durations or recorded input.
export function makeScorePages(song,size=6){
  size=Number.isInteger(size)&&size>=1&&size<=12?size:6;
  const events=scoreEvents(song,song.bpm),pages=[];let first=0;
  for(const [phrase,row]of song.phrases.entries()){
    for(let offset=0;offset<row.length;offset+=size)pages.push({phrase,part:Math.floor(offset/size),parts:Math.ceil(row.length/size),events:events.slice(first+offset,first+Math.min(row.length,offset+size))});
    first+=row.length;
  }
  return pages;
}
export function mountScoreReader(doc,{formatEvent,onOpen,onClose,onSong,onGuide,onLabels}={}){
  const $=id=>doc.getElementById(id),win=doc.defaultView,root=$('scoreReader');
  if(!root)return null;
  let song=null,pages=[],page=0,size=6,current=-1,practice=-1,open=false,playing=false,busy=false;
  const moved=[];
  const portrait=win.matchMedia?.('(max-width: 760px) and (orientation: portrait)');
  function applyPage(){
    if(!song||!pages.length)return;page=Math.max(0,Math.min(page,pages.length-1));const item=pages[page];
    $('readerPart').textContent=`第 ${item.phrase+1} 句${item.parts>1?' · '+(item.part+1)+'/'+item.parts:''}`;
    $('readerLyric').textContent=song.lyrics?.[item.phrase]||`${song.key} · ${song.meter}/4`;
    $('readerNotes').replaceChildren();
    for(const event of item.events){
      const n=doc.createElement('div'),f=formatEvent(event);n.className='reader-note';n.dataset.readerIndex=String(event.index);n.setAttribute('role','listitem');
      for(const [tag,text]of [['strong',f.primary],['span',f.secondary],['small',`${event.beats} 拍`]]){const child=doc.createElement(tag);child.textContent=text;n.append(child);}
      n.setAttribute('aria-label',`${f.primary}，${f.secondary}，${event.beats}拍`);$('readerNotes').append(n);
    }
    root.dataset.page=String(page);root.dataset.phrase=String(item.phrase);root.dataset.pages=String(pages.length);
    $('readerPageCount').textContent=`${page+1} / ${pages.length}`;$('readerPrev').disabled=busy||page===0;$('readerNext').disabled=busy||page===pages.length-1;
    highlight();
  }
  function highlight(){for(const n of $('readerNotes').children){const active=Number(n.dataset.readerIndex)===current;n.classList.toggle('playing',active);if(active)n.setAttribute('aria-current','true');else n.removeAttribute('aria-current');}}
  function indexPage(index){return pages.findIndex(p=>p.events.some(e=>e.index===index));}
  function practicePage(){const i=pages.findIndex(p=>p.phrase===practice);return i<0?0:i;}
  function turn(delta){if(!open||busy)return;$('readerFollow').checked=false;page=Math.max(0,Math.min(pages.length-1,page+delta));applyPage();}
  function setSize(next){if(size===next)return;const anchor=pages[page]?.events[0]?.index??0;size=next;if(song){pages=makeScorePages(song,size);page=Math.max(0,indexPage($('readerFollow').checked&&current>=0?current:anchor));applyPage();}}
  function move(id,slot){const node=$(id),placeholder=doc.createComment('score-reader:'+id);node.before(placeholder);$(slot).append(node);moved.push({node,placeholder});}
  function setOpen(value){
    if(open===value)return;open=value;root.hidden=!value;doc.body.classList.toggle('score-reading',value);
    for(const b of doc.querySelectorAll('[data-open-score]'))b.setAttribute('aria-pressed',String(value));
    $('readScoreToggle').textContent=value?'收起谱架':'看谱演奏';$('readerLabels').hidden=!value;
    if(value){
      setSize(portrait?.matches?4:6);move('catStage','readerCatSlot');move('playingSurface','readerKeysSlot');move('soundEntry','readerSoundSlot');move('guideTime','readerTiming');onOpen?.();applyPage();
    }else{for(const {node,placeholder}of moved.splice(0)){placeholder.replaceWith(node);}onClose?.();}
  }
  for(const b of doc.querySelectorAll('[data-open-score]'))b.addEventListener('click',()=>{if(!busy)setOpen(!open);});
  $('readerPrev').addEventListener('click',()=>turn(-1));$('readerNext').addEventListener('click',()=>turn(1));
  $('readerReturn').addEventListener('click',()=>{if(busy)return;page=current>=0?Math.max(0,indexPage(current)):practicePage();$('readerFollow').checked=playing;applyPage();});
  $('readerFollow').addEventListener('change',()=>{if($('readerFollow').checked&&current>=0){page=Math.max(0,indexPage(current));applyPage();}});
  $('readerGuide').addEventListener('click',()=>onGuide?.(pages[page]?.phrase??0,playing));
  $('readerSong').addEventListener('change',()=>onSong?.($('readerSong').value));$('readerLabels').addEventListener('change',()=>onLabels?.($('readerLabels').value));
  const key=event=>{if(!open||event.repeat||event.ctrlKey||event.metaKey||event.altKey||event.isComposing||event.target?.closest?.('input,select,textarea,[contenteditable]'))return;if(event.key==='PageDown'||event.key==='PageUp'){event.preventDefault();turn(event.key==='PageDown'?1:-1);}};
  doc.addEventListener('keydown',key);portrait?.addEventListener?.('change',()=>setSize(portrait.matches?4:6));
  doc.addEventListener('performance-mode-change',event=>{if(!event.detail.active&&open)setOpen(false);});
  return {
    get open(){return open;},setOpen,setSize,
    setScore(next,phrase=-1){
      const changed=song?.id!==next.id,anchor=pages[page]?.events[0]?.index??0,oldPractice=practice;song=next;practice=Number.isInteger(phrase)?phrase:-1;
      if(changed){current=-1;pages=makeScorePages(song,size);page=practicePage();}else{pages=makeScorePages(song,size);page=oldPractice!==practice?practicePage():Math.max(0,indexPage(anchor));}
      $('readerSong').replaceChildren();for(const option of $('songSelect').options){const o=doc.createElement('option');o.value=option.value;o.textContent=option.textContent;$('readerSong').append(o);}$('readerSong').value=song.id;
      applyPage();
    },
    refresh(){if(song)applyPage();$('readerLabels').value=$('keyLabels').value;},
    updateCurrent(index){if(index===current)return;current=index;if(open&&$('readerFollow').checked&&index>=0){const next=indexPage(index);if(next>=0&&next!==page){page=next;applyPage();return;}}highlight();},
    sync({locked=false,active=false,labelsLocked=false,media=false,pending=false}={}){
      busy=media;playing=active;$('readerTiming').hidden=!active;$('readerSong').disabled=locked||media;$('readerLabels').disabled=labelsLocked||media;$('readerFollow').disabled=media;
      $('readerGuide').disabled=media||pending&&!active;$('readerReturn').disabled=media;$('readerGuide').textContent=active?'停止跟弹':'跟这句';$('readerReturn').textContent=active?'回当前':'回练习句';
      for(const b of doc.querySelectorAll('[data-open-score]'))b.disabled=media;if(song){$('readerPrev').disabled=media||page===0;$('readerNext').disabled=media||page===pages.length-1;}
    },
    destroy(){setOpen(false);doc.removeEventListener('keydown',key);}
  };
}
