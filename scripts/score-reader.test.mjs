import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';import {JSDOM} from 'jsdom';
import {makeScorePages,mountScoreReader} from '../public/score-reader.js';import {SONGS,scoreEvents} from '../public/scores.js';
const html=await readFile(new URL('../public/index.html',import.meta.url),'utf8');
test('all songs paginate without dropping, duplicating or changing score events or crossing phrase boundaries',()=>{
 for(const song of SONGS)for(const size of [4,6]){
  const pages=makeScorePages(song,size),flat=pages.flatMap(p=>p.events);assert.deepEqual(flat,scoreEvents(song,song.bpm));
  let begin=0;for(const [phrase,row]of song.phrases.entries()){const group=pages.filter(p=>p.phrase===phrase);assert.equal(group.length,Math.ceil(row.length/size));assert.ok(group.every(p=>p.events.length<=size&&p.events.every(e=>e.index>=begin&&e.index<begin+row.length)));begin+=row.length;}
 }
});
function setup(t){
 const dom=new JSDOM(html,{url:'https://miao-beat.pages.dev/'}),doc=dom.window.document,opened=[];
 const o=doc.createElement('option');o.value=SONGS[3].id;o.textContent=SONGS[3].name;doc.getElementById('songSelect').append(o);
 const reader=mountScoreReader(doc,{formatEvent:e=>({primary:e.note||'rest',secondary:'key'}),onOpen:()=>opened.push(true)});reader.setScore(SONGS[3],0);t.after(()=>{reader.destroy();dom.window.close();});return {reader,doc,w:dom.window,$:id=>doc.getElementById(id),opened};
}
test('manual paging and follow do not change practice choice; returning/resize preserves source index',t=>{
 const h=setup(t),{reader,$,w}=h;reader.setOpen(true);reader.sync({active:true});
 const index=makeScorePages(SONGS[3],6)[7].events[0].index;
 $('readerFollow').checked=true;$('readerFollow').dispatchEvent(new w.Event('change'));reader.updateCurrent(index);assert.equal(Number($('scoreReader').dataset.page),7);
 $('readerNext').click();assert.equal($('readerFollow').checked,false);const manual=Number($('scoreReader').dataset.page);reader.updateCurrent(index+1);assert.equal(Number($('scoreReader').dataset.page),manual);
 $('readerReturn').click();assert.equal($('readerFollow').checked,true);assert.equal(Number($('scoreReader').dataset.page),7);
 const source=index+1;reader.setSize(4);assert.ok([...$('readerNotes').children].some(n=>Number(n.dataset.readerIndex)===source));assert.equal($('phraseSelect').value,'all');
 const before=Number($('scoreReader').dataset.page);reader.sync({media:true});$('readerNext').click();assert.equal(Number($('scoreReader').dataset.page),before);assert.equal($('readerReturn').disabled,true);
});
test('reader moves the actual stage and keyboard, then native exit restores those exact nodes and listeners',t=>{
 const h=setup(t),{reader,$,doc,w}=h,keys=$('playingSurface'),stage=$('catStage'),sound=$('soundEntry'),parent=keys.parentNode,stageParent=stage.parentNode;let clicks=0;keys.addEventListener('click',()=>clicks++);
 reader.setOpen(true);assert.equal(keys.parentNode,$('readerKeysSlot'));assert.equal(stage.parentNode,$('readerCatSlot'));assert.equal(sound.parentNode,$('readerSoundSlot'));keys.click();assert.equal(clicks,1);
 doc.dispatchEvent(new w.CustomEvent('performance-mode-change',{detail:{active:false}}));assert.equal(reader.open,false);assert.equal(keys.parentNode,parent);assert.equal(stage.parentNode,stageParent);assert.equal(sound.parentNode,parent);keys.click();assert.equal(clicks,2);
 reader.setOpen(true);reader.setOpen(false);assert.equal(doc.querySelectorAll('#playingSurface').length,1);assert.equal(doc.querySelectorAll('#catStage').length,1);
});
test('page keys respect text controls and first/last boundaries',t=>{
 const {reader,$,doc,w}=setup(t);reader.setOpen(true);assert.equal($('readerPrev').disabled,true);
 $('readerSong').dispatchEvent(new w.KeyboardEvent('keydown',{key:'PageDown',bubbles:true,cancelable:true}));assert.equal($('scoreReader').dataset.page,'0');
 doc.dispatchEvent(new w.KeyboardEvent('keydown',{key:'PageDown',bubbles:true,cancelable:true}));assert.equal($('scoreReader').dataset.page,'1');
 for(let i=0;i<200;i++)$('readerNext').click();assert.equal($('readerNext').disabled,true);const last=$('scoreReader').dataset.page;$('readerNext').click();assert.equal($('scoreReader').dataset.page,last);
});
