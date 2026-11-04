// Build the actual web workbench into the offline XHS container. No production web mutation.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {build,transform} from 'esbuild';
import {JSDOM} from 'jsdom';
const root=path.resolve(new URL('..',import.meta.url).pathname),out=path.join(root,'artifacts/xhs-av-20261104/package'),stage=path.dirname(out),skill=path.join(root,'.codex/skills/minitool-zip-builder');
const sha=b=>createHash('sha256').update(b).digest('hex'),read=n=>fs.readFile(path.join(root,n),'utf8');
const input={},assets=[],json={};
for(const file of ['scripts/build-xhs-web.mjs',...(await fs.readdir(path.join(root,'minitool/web'))).map(f=>'minitool/web/'+f)])input[file]=sha(await fs.readFile(path.join(root,file)));
await fs.rm(out,{recursive:true,force:true});await fs.mkdir(out,{recursive:true});
async function put(name,bytes){await fs.mkdir(path.dirname(path.join(out,name)),{recursive:true});await fs.writeFile(path.join(out,name),bytes);}
async function image(name,size,targetName=name){const bytes=await fs.readFile(path.join(root,'public',name));input['public/'+name]=sha(bytes);const target=path.join(out,targetName);await fs.mkdir(path.dirname(target),{recursive:true});execFileSync('sips',['-Z',String(size),'-s','format','jpeg','-s','formatOptions','60',path.join(root,'public',name),'--out',target],{stdio:'ignore'});const result=await fs.readFile(target);assets.push({file:targetName,sourceSha256:sha(bytes),sha256:sha(result),bytes:result.length,operation:'proportional whole-frame resize; no crop, separate paws or new art'});}
// 56 piano poses, 18 guitar poses and 25 drum poses retain all original input mappings.
for(const dir of ['character/whole-piano-v3','character/instrument-scenes-v1']){
 const manifest=JSON.parse(await read('public/'+dir+'/manifest.json'));json[dir+'/manifest.json']=manifest;
 const frames=manifest.frames?Object.values(manifest.frames):Object.values(manifest.modes).flatMap(m=>Object.values(m.frames));
 for(const file of frames)await image(dir+'/'+file,480);
}
const motion=JSON.parse(await read('public/character/guitar-pluck-v1/manifest.json'));motion.tileSize=320;json['character/guitar-pluck-v1/manifest.json']=motion;
// Atlas cell geometry remains 640px; preserve author-approved contact timing and tiles.
for(const clip of Object.values(motion.clips)){
 await image('character/guitar-pluck-v1/'+clip.up.file,480);
 const file='character/guitar-pluck-v1/'+clip.atlas.file,targetName=file.replace(/\.webp$/,'.jpg');await image(file,960,targetName);clip.atlas.file=clip.atlas.file.replace(/\.webp$/,'.jpg');const resized=await fs.readFile(path.join(out,targetName));clip.atlas.bytes=resized.length;clip.atlas.sha256=sha(resized);
}
const manifest=JSON.parse(await read('public/samples/manifest.json')),audioBytes={};json['samples/manifest.json']=manifest;
for(const group of Object.values(manifest.groups))for(const url of Object.values(group.noteURLs)){
 const name=url.replace(/^\.\//,''),bytes=await fs.readFile(path.join(root,'public',name));if(bytes.length>1024*1024)throw Error('Review large sample '+name);input['public/'+name]=sha(bytes);audioBytes[name]=bytes.toString('base64');
}
const resourceCode='export const manifests='+JSON.stringify(json)+';\nexport const samples='+JSON.stringify(audioBytes)+';\n';
// Shared DOM, with only container-incompatible delivery/account/external links removed.
const dom=new JSDOM(await read('public/index.html')),doc=dom.window.document;
for(const selector of ['.header-actions','.miao-family','.support-note','#supportDialog','.site-visits','script','noscript'])for(const n of doc.querySelectorAll(selector))n.remove();
for(const n of doc.querySelectorAll('a')){n.removeAttribute('target');n.removeAttribute('download');if(!String(n.getAttribute('href')).startsWith('#'))n.removeAttribute('href');}
const sound=doc.getElementById('soundEntry'),test=doc.createElement('button');test.id='testSound';test.textContent='测试声音';test.type='button';sound.append(test);
const help=doc.createElement('p');help.id='soundHelp';help.hidden=true;help.className='sound-status';help.textContent='没有声音？请关闭 iPhone 静音模式（切到响铃），再调高媒体音量。';sound.append(help);const heard=doc.createElement('button');heard.id='heardSound';heard.textContent='听到了，收起提示';heard.type='button';heard.hidden=true;sound.append(heard);
const auto=doc.createElement('button');auto.id='publishResult';auto.type='button';auto.textContent='生成并发布到小红书';doc.getElementById('exportVideo').after(auto);
doc.getElementById('exportBrand').checked=true;doc.querySelector('.outro-choice').lastChild.textContent=' 片尾附打开同款的二维码（2秒）';
doc.getElementById('exportVideo').textContent='生成带声视频';doc.getElementById('performanceToggle').textContent='展开演奏';doc.getElementById('exportAudio').hidden=true;
doc.querySelector('.import-recording').hidden=true;doc.getElementById('exportRecording').textContent='保存按键内容';
const textImport=doc.createElement('button');textImport.id='importText';textImport.type='button';textImport.textContent='导入按键内容';doc.getElementById('exportRecording').after(textImport);
const meta=doc.querySelector('.recording-meta');if(meta)meta.firstElementChild.textContent='片段保留本机；视频包含完整猫动作、演奏声音与可扫码打开的片尾。';
const script=doc.createElement('script');script.src='./app.js';script.defer=true;doc.head.append(script);
await put('index.html',dom.serialize());dom.window.close();
await put('icon.svg',await fs.readFile(path.join(root,'public/icon.svg')));await image('share/page-preview.jpg',720);
const css=(await read('public/style.css'))+'\n'+(await read('minitool/web/container.css'))+'\n/* Container and Chrome61 baseline additions */\n[hidden]{display:none!important}body{padding-top:var(--native-top,0px)}.workbench{min-width:0}#soundHelp{padding:8px 12px;background:#fff0d5;border-radius:8px;color:#61412e}.sound-ready{flex-wrap:wrap}#testSound{min-height:40px}#exportAudio{display:none!important}#publishResult{background:#bd793f;color:#fff}.hero{padding-top:16px}.support-trigger{display:none}.instrument-tabs{display:flex;flex-wrap:wrap}.instrument-tabs button{margin:3px}.recording-actions button{margin:3px}.music-key{touch-action:none}@media(orientation:landscape){.site-shell{max-width:1100px}.hero{display:none}.workbench{max-width:1100px;margin:auto}.melody-keys{min-width:0}.melody-scroll{overflow-x:auto}}';
await put('style.css',(await transform(css,{loader:'css',target:['chrome61','safari18.4'],minify:false})).code);
function replaceOnce(s,from,to,file){if(!s.includes(from))throw Error('Source drift '+file+': '+from.slice(0,65));return s.replace(from,to);}
const plugin={name:'xhs-offline',setup(b){
 b.onResolve({filter:/^xhs-resources$/},()=>({path:'resources',namespace:'xhs'}));b.onLoad({filter:/.*/,namespace:'xhs'},()=>({contents:resourceCode,loader:'js'}));
 b.onResolve({filter:/vendor\/smplr\.mjs$/},()=>({path:path.join(root,'minitool/web/sampler.js')}));
 b.onResolve({filter:/media-sharing\.js$/},()=>({path:path.join(root,'minitool/web/sharing.js')}));
 b.onResolve({filter:/performance\.js$/},()=>({path:path.join(root,'minitool/web/performance.js')}));
 b.onLoad({filter:/\/public\/.*\.js$/},async args=>{
 const name=path.basename(args.path);let s=await fs.readFile(args.path,'utf8');input['public/'+path.relative(path.join(root,'public'),args.path)]=sha(s);
 s=s.replaceAll('import.meta.url','new URL("./app.js", document.baseURI).href');
 if(name==='audio.js')s=replaceOnce(s,'    if(!this.context){',"    try{if(globalThis.navigator.audioSession)globalThis.navigator.audioSession.type='playback';}catch{}\n    if(!this.context){",name);
 if(name==='sampled-audio.js'){
  s="import {manifests,samples} from 'xhs-resources';\n"+s;
  s=s.replace('fetchImpl = globalThis.fetch?.bind(globalThis)','fetchImpl = null');
  const start=s.indexOf('  async fetchLocal(url) {'),end=s.indexOf('\n  async getManifest()',start);
  s=s.slice(0,start)+`  async fetchLocal(url){const key=new URL(url).pathname.slice(BASE.pathname.length);if(key==='samples/manifest.json')return{ok:true,json:async()=>manifests[key]};const bytes=samples[key];if(!bytes)throw Error('Missing offline sample');return{ok:true,arrayBuffer:async()=>{const binary=atob(bytes),out=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)out[i]=binary.charCodeAt(i);return out.buffer;}};}\n`+s.slice(end);
 }
 if(name==='full-frame-character.js'){
  s="import {manifests} from 'xhs-resources';\n"+s;
  s=s.replaceAll('fetch(BAND_MANIFEST)',"Promise.resolve({ok:true,json:async()=>manifests['character/instrument-scenes-v1/manifest.json']})").replaceAll('fetch(MOTION_MANIFEST)',"Promise.resolve({ok:true,json:async()=>manifests['character/guitar-pluck-v1/manifest.json']})").replaceAll('fetch(MANIFEST)',"Promise.resolve({ok:true,json:async()=>manifests['character/whole-piano-v3/manifest.json']})");
  const start=s.indexOf('  async function getBlob(id){'),end=s.indexOf('  async function getBitmap(id)',start);
  s=s.slice(0,start)+`  async function getBlob(id){if(id.includes(':')&&!id.startsWith('pluck:')&&!id.startsWith('up:'))await loadBand();return{size:0};}\n`+s.slice(end);
  s=replaceOnce(s,"if(win.createImageBitmap)image=await win.createImageBitmap(blob);\n      else image=await new Promise",'image=await new Promise',name);
  s=s.replaceAll("(id.startsWith('pluck:')?1920:1254)","(id.startsWith('pluck:')?960:480)").replace('(cell%3)*640,Math.floor(cell/3)*640,640,640','(cell%3)*320,Math.floor(cell/3)*320,320,320');
  s=replaceOnce(s,'ctx.drawImage(image,0,0);','ctx.drawImage(image,0,0,1254,1254);',name);
 }
 if(name==='guitar-motion.js')s=s.replace('data.tileSize!==640','data.tileSize!==320').replace("code+'.webp'","code+'.jpg'");
 if(name==='media-export.js'){
  s=s.replace("'video/webm;codecs=vp9,opus','video/webm;codecs=vp8,opus','video/webm'",'');
  s=s.replaceAll('maxBytes=128*1024*1024','maxBytes=24*1024*1024').replace('文件超过128 MB','文件超过24 MB').replace('canvas.captureStream(60)','canvas.captureStream(30)').replace('videoBitsPerSecond:2500000','videoBitsPerSecond:1500000');
  s=s.replace('new URL(\'./share/page-preview.jpg\', new URL("./app.js", document.baseURI).href).href',"'./share/page-preview.jpg'");
 }
 if(name==='app.js'){
  s=s.replace("import './family-referrals.js';",'').replace("import {loadSiteCounter} from './site-counter.js';",'').replace('loadSiteCounter();','').replaceAll('localStorage.','window.MiaoMiniStore.').replaceAll('已保存在此浏览器','片段已保留本机');
  s=s.slice(0,s.indexOf('// Reuse the owner’s existing voluntary support image')>=0?s.indexOf('// Reuse the owner’s existing voluntary support image'):s.length);
  const support=s.indexOf('// Reuse the owner\'s existing voluntary support image');if(support>=0)s=s.slice(0,support);
  s=s.replace("$('scoreSource').href=song.sourceUrl;",'');
  s=s.replace('for(const [code,b]of buttons){',"for(const [code,b]of buttons){let pointerClicks=[];const fresh=()=>{pointerClicks=pointerClicks.filter(t=>Date.now()-t<1200);};b.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' ')pointerClicks=[];});");
  s=s.replace("event.preventDefault();b.setPointerCapture(event.pointerId);held.add(code);", "event.preventDefault();fresh();pointerClicks.push(Date.now());if(pointerClicks.length>16)pointerClicks.shift();try{b.setPointerCapture(event.pointerId);}catch{}held.add(code);");
  s=s.replace("b.addEventListener('click',event=>{if(event.detail===0)hit(code);});", "b.addEventListener('click',event=>{fresh();if(pointerClicks.length){pointerClicks.shift();return;}if(event.detail===0)hit(code);});");

  const from=s.indexOf("  a.href=url;a.download='miao-beat-"),to=s.indexOf("\n});",from);
  if(from<0)throw Error('Missing recording download');s=s.slice(0,from)+"  URL.revokeObjectURL(url);$('recordingStatus').textContent='按键内容已准备，可在下方选中复制保存。';"+s.slice(to);
  s=s.replace('async function exportMedia(kind){','async function exportMedia(kind,publish=false){');
  s=s.replace("!mediaSupported('video')&&!mediaSupported('audio')","!mediaSupported('video')").replace('当前浏览器不支持媒体导出，仍可保存按键片段。','当前客户端不支持MP4视频编码，仍可演奏和回放；请更新客户端后重试视频。');
  const from2=s.indexOf('    const url=URL.createObjectURL(result.blob);'),to2=s.indexOf('\n  }catch(error){job?.cancel()',from2);
  if(from2<0||to2<0)throw Error('Missing media result');s=s.slice(0,from2)+`    mediaSharing.setMedia(kind,{blob:result.blob,name:'miao-beat-'+data.instrument+'.mp4'});\n    $('mediaStatus').textContent='带声视频已生成 · '+result.width+' × '+result.height+'，可发布到小红书。';$('mediaResults').dataset.format=result.mimeType;\n    if(publish)await mediaSharing.publish();`+s.slice(to2);
  s=s.replace("$('exportAudio').disabled=busy", "$('publishResult').disabled=$('exportVideo').disabled; $('testSound').disabled=busy||active; $('importText').disabled=busy||active||!!session;\n  $('exportAudio').disabled=busy");
  s+=`\n$('publishResult').addEventListener('click',()=>exportMedia('video',true));\n$('testSound').addEventListener('click',async()=>{if(mediaBusy()||recordStart!==null)return;$('soundHelp').hidden=false;$('heardSound').hidden=false;$('soundEntry').classList.add('sound-help-open');if(await ready()){const preset=$('instrumentSelect').value;audio.play(preset==='drums'?DRUMS[0]:MELODY[0],preset);status.textContent='已播放测试音。若没听到，请按下面提示检查静音和媒体音量。';}});\n$('heardSound').addEventListener('click',()=>{$('soundHelp').hidden=true;$('heardSound').hidden=true;$('soundEntry').classList.remove('sound-help-open');});\n$('importText').addEventListener('click',()=>{if(mediaBusy()||recordStart!==null)return;$('exportPreview').hidden=false;$('exportPreview').open=true;$('exportData').readOnly=false;$('exportData').value='';$('recordingStatus').textContent='在下方粘贴按键JSON，失去焦点时导入；内容保留在本机。';});\n$('exportData').addEventListener('change',()=>{if($('exportData').readOnly||mediaBusy()||recordStart!==null)return;try{if($('exportData').value.length>256000)throw Error('内容太长');const parsed=validateRecording(JSON.parse($('exportData').value));stopSession();previousTake=recording;recording=parsed;takeBackup=null;persistDraft();$('recordingInfo').textContent=(recording.duration/1000).toFixed(1)+'秒 · '+recording.events.length+'次按键';$('recordingStatus').textContent='已导入，可回放或导出视频';updateRecorder();}catch(e){$('recordingStatus').textContent='未导入：'+e.message;}});\n`;
 }
 return{contents:s,loader:'js'};
 });
}};
await build({entryPoints:[path.join(root,'minitool/web/entry.js')],outfile:path.join(out,'app.js'),bundle:true,format:'iife',platform:'browser',target:['chrome61','safari18.4'],plugins:[plugin],legalComments:'inline',minify:false});
const notices=JSON.parse(await read('minitool/NOTICES.json'));notices.artwork='Existing approved whole-frame piano, guitar and drum scenes. Still/up frames resized proportionally; pluck atlases resized with the complete nine-cell grid preserved. No new cat artwork or detached limb compositing.';notices.runtimeBoundary='Shared web workbench adapted to offline JS and native MP4 postNote. No network, microphone, external navigation or browser downloads. QR opens the public independent game.';notices.audioAdapter.modifications='2026-11-04: Shared SampledAudio calibration/voice/range logic with local-buffer Sampler subset, explicitly not the full smplr runtime.';
notices.bongoCodeLicense=await read('public/UPSTREAM-LICENSE.txt');notices.velocityFormulaLicense=await read('scripts/smplr-LICENSE.txt');notices.sampleLicenses=await read('public/samples/LICENSES.txt');notices.cc0=await read('public/samples/CC0-1.0.txt');notices.qrLicense=await read('public/vendor/qrcode-LICENSE.txt');await put('NOTICES.json',JSON.stringify(notices,null,2));
const files={};async function walk(dir,prefix=''){for(const e of await fs.readdir(dir,{withFileTypes:true})){const name=prefix+e.name;if(e.isDirectory())await walk(path.join(dir,e.name),name+'/');else files[name]=sha(await fs.readFile(path.join(dir,e.name)));}}await walk(out);
const id=sha(JSON.stringify(files)).slice(0,12);await put('index.html',(await fs.readFile(path.join(out,'index.html'),'utf8')).replace('<body','<body data-build="'+id+'"'));files['index.html']=sha(await fs.readFile(path.join(out,'index.html')));
const runtime=await fs.readFile(path.join(out,'app.js'),'utf8');if(/\bfetch\s*\(|XMLHttpRequest|new Worker\(|WebAssembly|requestFullscreen|\.download\s*=|type="module"/.test(runtime))throw Error('Unsupported runtime capability retained');
const directoryAudit=execFileSync('python3',[path.join(skill,'scripts/audit_artifact.py'),out],{encoding:'utf8'});
const zip=path.join(stage,'miao-beat-web-xhs-'+id+'.zip');execFileSync('python3',['-c','import sys,zipfile;from pathlib import Path;p=Path(sys.argv[1]);z=zipfile.ZipFile(sys.argv[2],"w",zipfile.ZIP_DEFLATED,compresslevel=9);[(lambda i,f:(setattr(i,"compress_type",zipfile.ZIP_DEFLATED),setattr(i,"external_attr",0o100644<<16),z.writestr(i,f.read_bytes())))(zipfile.ZipInfo(f.relative_to(p).as_posix(),(1980,1,1,0,0,0)),f)for f in sorted(p.rglob("*"))if f.is_file()];z.close()',out,zip]);
const zipAudit=execFileSync('python3',[path.join(skill,'scripts/audit_artifact.py'),zip],{encoding:'utf8'}),bytes=await fs.readFile(zip);if(bytes.length>10*1024*1024)throw Error('Package exceeds platform limit');
await fs.writeFile(path.join(stage,'build-audit.json'),JSON.stringify({buildId:id,builtAt:new Date().toISOString(),sourceCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),zip,zipSha256:sha(bytes),zipBytes:bytes.length,files,input,assets,directoryAudit,zipAudit,validation:{physicalDevice:'not requested; user explicitly declined device QA',container:'pending',videoHandoff:'pending'}},null,2));console.log(JSON.stringify({buildId:id,zip,bytes:bytes.length,directoryAudit,zipAudit}));
