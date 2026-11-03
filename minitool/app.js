(function(root){
 'use strict';
 var data=root.MIAO_BEAT_DATA,bridge=root.MiaoBeatBridge,audio=new root.MiaoBeatPianoAudio(),record=root.MiaoBeatRecording;
 var $=function(id){return document.getElementById(id);},keys=data.keys,images={},held={},poseTimer=0,raf=0,session=null;
 var ready=false,preparing=false,generation=0,recording=false,start=0,take=null,previous=null,backup=null,promoted=false;
 var page=0,pages=[],song=data.songs[0],revision=0,storageLoading=true,storageReadable=false,cardData='',nativeBusy=false;
 function validate(value){var t=record.validateRecording(value);if(t.instrument!=='piano'||t.version!==2||t.duration>60000||t.events.length>512||t.events.some(function(e){return e[1]>7;}))throw new Error('不是支持的短片段');return t;}
 function snapshot(value){if(!value||value.version!==1)return null;return{version:1,take:value.take?validate(value.take):null,previous:value.previous?validate(value.previous):null};}
 function paintScene(code){if(!images[code]||!images[code].complete||!images[code].naturalWidth)code='idle';Object.keys(images).forEach(function(name){images[name].hidden=name!==code;});}
 function idle(){clearTimeout(poseTimer);paintScene('idle');Object.keys(held).forEach(function(code){held[code]=false;});keys.forEach(function(k){$(k.code).setAttribute('aria-pressed','false');});}
 function strike(code){paintScene(code);clearTimeout(poseTimer);poseTimer=setTimeout(function(){paintScene('idle');},180);}
 function controls(){
  keys.forEach(function(k){$(k.code).disabled=!ready||preparing;});$('prepare').disabled=preparing;$('prepare').textContent=preparing?'准备中…':ready?'声音已准备':'准备声音';
  $('record').disabled=!ready||preparing||storageLoading||!!session;$('record').textContent=recording?'结束记录':'录一段';$('record').setAttribute('aria-pressed',String(recording));
  $('stop').disabled=!recording&&!session&&!preparing;$('replay').disabled=!ready||recording||preparing||!!session||!take||!take.events.length;
  $('makeCard').disabled=recording||!!session||!take||!take.events.length;$('listen').disabled=!ready||recording||preparing||!!session;
  $('restore').disabled=recording||!!session||storageLoading||!previous;var caps=bridge.capabilities();$('saveCard').disabled=nativeBusy||!cardData||!caps.save;$('postCard').disabled=nativeBusy||!cardData||!caps.post;
 }
 function persist(){
  if(!storageReadable){$('storageStatus').textContent='旧草稿尚未成功读取，当前片段仅留在这次打开中。';return;}
  var value=JSON.stringify({version:1,take:take,previous:previous});$('storageStatus').textContent='正在保留本机片段…';
  bridge.put(value).then(function(){$('storageStatus').textContent='片段已保留本机；清缓存或卸载可能丢失。';},function(){$('storageStatus').textContent='本机暂未保存，片段仍可回放／生成小卡。';});
 }
 function invalidateCard(){cardData='';$('cardPanel').hidden=true;$('cardImage').removeAttribute('src');}
 function info(message){$('takeStatus').textContent=message||(take&&take.events.length?take.events.length+' 次按键 · '+(take.duration/1000).toFixed(1)+' 秒':'只记录你实际弹下的音；听谱不写入录音。');}
 function finishRecord(){if(!recording)return;recording=false;revision++;take.duration=Math.min(60000,Math.max(0,Math.round((audio.context.currentTime-start)*1000)));
  if(!take.events.length){take=backup;info('没有新的按键，已保留原来的片段。');}else{take=validate(take);info();persist();}backup=null;controls();}
 function stopSession(){if(raf)cancelAnimationFrame(raf);raf=0;session=null;audio.stopVoices();idle();controls();}
 function tick(){
  if(recording){var elapsed=Math.round((audio.context.currentTime-start)*1000);take.duration=Math.min(60000,elapsed);info('正在记录 · '+take.events.length+' 次按键 · '+(take.duration/1000).toFixed(1)+' 秒');if(elapsed>=60000)finishRecord();}
  if(session){var now=audio.context.currentTime,events=session.events;
   while(session.scheduled<events.length&&session.start+events[session.scheduled][0]/1000<=now+.1){var scheduled=events[session.scheduled],when=session.start+scheduled[0]/1000;if(when<now-.15){stopSession();info('播放发生卡顿，已停止；片段仍在，请重新回放。');return;}try{audio.play(keys[scheduled[1]],when);}catch(error){stopSession();ready=false;$('soundStatus').textContent='播放已暂停，请重新准备声音。';controls();return;}session.scheduled++;}
   while(session.painted<events.length&&session.start+events[session.painted][0]/1000<=now){strike(keys[events[session.painted++][1]].code);}
   if(now>=session.end){session=null;paintScene('idle');info('这一遍播放结束，可以自己弹或再听一次。');controls();}
  }
  if(recording||session)raf=requestAnimationFrame(tick);else raf=0;
 }
 function loop(){if(!raf)raf=requestAnimationFrame(tick);}
 function human(index){if(!ready||preparing||document.hidden)return;if(session)stopSession();try{audio.play(keys[index]);}catch(error){ready=false;$('soundStatus').textContent='这一下没有发声，请重新准备声音。';controls();return;}
  strike(keys[index].code);
  if(recording){revision++;var time=Math.max(0,Math.min(60000,Math.round((audio.context.currentTime-start)*1000)));
   if(!promoted){previous=backup||previous;promoted=true;}
   take.events.push([time,index]);take.duration=time;
   if(take.events.length>=512)finishRecord();
  }
 }
 function rebuildPages(){pages=[];song.phrases.forEach(function(row,phrase){for(var at=0;at<row.length;at+=4)pages.push({phrase:phrase,events:row.slice(at,at+4)});});page=0;renderPage();}
 function renderPage(){var current=pages[page];$('notes').textContent='';current.events.forEach(function(e){var k=keys.filter(function(k){return k.note===e.note;})[0],n=document.createElement('div');n.className='score-note';n.setAttribute('role','listitem');var strong=document.createElement('strong'),small=document.createElement('small');strong.textContent=k?k.number:'休';small.textContent=(k?k.note:'休止')+' · '+e.beats+'拍';n.appendChild(strong);n.appendChild(small);$('notes').appendChild(n);});$('pageCount').textContent=(page+1)+'/'+pages.length;$('phrase').textContent='第 '+(current.phrase+1)+' 句 · C大调';$('prev').disabled=page===0;$('next').disabled=page===pages.length-1;}
 function playback(events,duration,kind){if(!ready||recording||!events.length)return;stopSession();session={kind:kind,events:events,start:audio.context.currentTime+.1,end:audio.context.currentTime+.1+duration/1000+1.3,scheduled:0,painted:0};info('正在播放，点琴键可接着自己弹。');controls();loop();}
 function newCard(){
  if(!take||!take.events.length||recording)return;try{var source=images.idle;if(!source.complete||!source.naturalWidth)throw new Error('猫图还没准备好');var c=document.createElement('canvas');c.width=600;c.height=800;var x=c.getContext('2d');if(!x)throw new Error('当前环境暂不支持小卡');
   x.fillStyle='#f8f4eb';x.fillRect(0,0,600,800);x.fillStyle='#61412e';x.font='600 29px sans-serif';x.fillText('和橘猫弹了一小段',40,63);x.font='16px sans-serif';x.fillText('真人演奏小卡 · 图片不带声音',40,98);x.drawImage(source,130,125,340,340);
   x.font='600 31px sans-serif';take.events.slice(0,24).forEach(function(e,i){x.fillText(keys[e[1]].number,48+(i%8)*65,505+Math.floor(i/8)*50);});x.font='17px sans-serif';x.fillText(take.events.length+' 次按键 · '+(take.duration/1000).toFixed(1)+' 秒',40,695);x.font='600 24px sans-serif';x.fillText('喵Beat · 猫咪弹琴',40,751);x.font='12px sans-serif';x.fillStyle='#94775e';x.fillText(take.events.length>24?'上面展示前24个音 · 猫图由AI辅助制作':'记录的是我亲手弹的音 · 猫图由AI辅助制作',40,779);
   cardData=c.toDataURL('image/png');$('cardImage').src=cardData;$('cardPanel').hidden=false;$('cardStatus').textContent='图片不带声音；是否保存／发布由你选择。';controls();$('cardPanel').scrollIntoView({block:'start'});
  }catch(error){$('takeStatus').textContent=error.message||'小卡未生成，片段仍可回放。';}
 }
 async function cardAction(kind){if(nativeBusy||!cardData)return;nativeBusy=true;controls();$('cardStatus').textContent=kind==='save'?'正在交给相册…':'正在交给小红书编辑页…';try{await bridge[kind](cardData);$('cardStatus').textContent=kind==='save'?'平台已确认保存到相册。':'已交给小红书处理，发布与审核状态以平台显示为准。';}catch(error){var cancelled=Number(error&&error.errCode)===20002||/cancel|取消/i.test(String(error&&error.errMsg||error&&error.message||''));$('cardStatus').textContent=cancelled?'已取消，小卡和片段仍在。':'没有完成操作，小卡和片段仍在，可以重试。';}finally{nativeBusy=false;controls();}}
 ['idle'].concat(keys.map(function(k){return k.code;})).forEach(function(code){var image=document.createElement('img');image.src='./assets/'+code+'.jpg';image.alt='完整橘猫、双爪与钢琴';image.hidden=code!=='idle';images[code]=image;$('catStage').appendChild(image);});
 keys.forEach(function(key,index){var b=document.createElement('button');b.type='button';b.id=key.code;b.className='key';b.setAttribute('aria-label',key.note+'，音符'+key.number);b.setAttribute('aria-pressed','false');var strong=document.createElement('strong'),small=document.createElement('small');strong.textContent=key.number;small.textContent=key.note;b.appendChild(strong);b.appendChild(small);
  // Reuse the historical official-probe fix: some containers emit detail0 after pointerdown.
  var pointerClicks=[];function freshPointerClicks(){var now=Date.now();pointerClicks=pointerClicks.filter(function(at){return now-at<1200;});}
  b.addEventListener('pointerdown',function(e){if((e.button!==0&&e.pointerType!=='touch')||held[key.code])return;e.preventDefault();freshPointerClicks();pointerClicks.push(Date.now());if(pointerClicks.length>16)pointerClicks.shift();held[key.code]=true;try{b.setPointerCapture(e.pointerId);}catch(error){}b.setAttribute('aria-pressed','true');human(index);});
  ['pointerup','pointercancel','lostpointercapture'].forEach(function(type){b.addEventListener(type,function(){held[key.code]=false;b.setAttribute('aria-pressed','false');});});b.addEventListener('click',function(){freshPointerClicks();if(pointerClicks.length){pointerClicks.shift();return;}human(index);});b.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '||e.code==='Space')pointerClicks=[];});$('keys').appendChild(b);
 });
 document.addEventListener('keydown',function(e){if(e.repeat||e.ctrlKey||e.metaKey||e.altKey||e.isComposing||(e.target&&e.target.closest&&e.target.closest('input,select,textarea,[contenteditable]')))return;var index=keys.findIndex(function(k){return k.code===e.code;});if(index<0||held[e.code])return;e.preventDefault();held[e.code]=true;$(e.code).setAttribute('aria-pressed','true');human(index);});document.addEventListener('keyup',function(e){if(held[e.code]){held[e.code]=false;$(e.code).setAttribute('aria-pressed','false');}});
 data.songs.forEach(function(s){var option=document.createElement('option');option.value=s.id;option.textContent=s.name;$('song').appendChild(option);});$('song').addEventListener('change',function(){if(session)stopSession();song=data.songs.filter(function(s){return s.id===$('song').value;})[0];rebuildPages();});$('prev').addEventListener('click',function(){if(page>0){if(session&&session.kind==='demo'){stopSession();info('已停止上一页示范。');}page--;renderPage();}});$('next').addEventListener('click',function(){if(page<pages.length-1){if(session&&session.kind==='demo'){stopSession();info('已停止上一页示范。');}page++;renderPage();}});
 $('listen').addEventListener('click',function(){var time=0,events=[];pages[page].events.forEach(function(e){var index=keys.findIndex(function(k){return k.note===e.note;});if(index>=0)events.push([time,index]);time+=e.beats*60000/song.bpm;});playback(events,time,'demo');});
 $('replay').addEventListener('click',function(){if(take)playback(take.events,take.duration,'take');});$('record').addEventListener('click',function(){if(recording){finishRecord();return;}if(!ready||storageLoading)return;stopSession();revision++;backup=take;promoted=false;take=record.makeRecording('piano',96,4);recording=true;start=audio.context.currentTime;invalidateCard();info('正在记录，只保留你亲手弹的音。');controls();loop();});
 $('stop').addEventListener('click',function(){generation++;preparing=false;finishRecord();stopSession();info(take&&take.events.length?'已停止 · '+take.events.length+' 次按键 · '+(take.duration/1000).toFixed(1)+' 秒':'已停止，没有新的按键。');});
 $('prepare').addEventListener('click',function(){if(preparing)return;var token=++generation;preparing=true;controls();$('soundStatus').textContent='正在准备5个钢琴采样…';var timer=setTimeout(function(){if(token!==generation)return;generation++;preparing=false;ready=false;audio.stopVoices();$('soundStatus').textContent='声音准备超时，可重新点准备声音。';controls();},15000);
  audio.ready().then(function(){clearTimeout(timer);if(token!==generation||document.hidden)return;preparing=false;ready=true;$('soundStatus').textContent='声音已准备，点一个音试试。';controls();},function(){clearTimeout(timer);if(token!==generation)return;preparing=false;ready=false;$('soundStatus').textContent='声音暂未准备好，请重新点准备声音。';controls();});});
 $('volume').addEventListener('input',function(){audio.setVolume(Number($('volume').value)/100);});$('makeCard').addEventListener('click',newCard);$('saveCard').addEventListener('click',function(){void cardAction('save');});$('postCard').addEventListener('click',function(){void cardAction('post');});$('closeCard').addEventListener('click',function(){$('cardPanel').hidden=true;});$('restore').addEventListener('click',function(){if(!previous)return;var swap=take;take=previous;previous=swap;revision++;invalidateCard();info();persist();controls();});
 function pause(){generation++;preparing=false;finishRecord();stopSession();ready=false;$('soundStatus').textContent='已暂停；回来后点准备声音继续。';controls();}
 root.addEventListener('blur',pause);root.addEventListener('pagehide',pause);document.addEventListener('visibilitychange',function(){if(document.hidden)pause();});
 rebuildPages();controls();bridge.init().then(function(){controls();var token=revision;return bridge.load().then(function(raw){storageReadable=true;if(raw){var saved=snapshot(JSON.parse(raw));if(!saved)throw new Error('草稿格式无效');if(token===revision&&!recording){take=saved.take;previous=saved.previous;info();}}$('storageStatus').textContent=take?'已恢复本机片段；可回放或重新录制。':'新录音会尝试保留在本机。';},function(){storageReadable=false;$('storageStatus').textContent='本机草稿暂未读到，新片段仍可在这次打开中使用。';});}).catch(function(){storageReadable=false;$('storageStatus').textContent='旧草稿无效或未读到，当前仅在本次打开中保留。';}).then(function(){storageLoading=false;controls();});
}(window));
