// Build-only offline adapter. The normal public/ deployment stays independent.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {SONGS} from '../public/scores.js';
import {MELODY} from '../public/bindings.js';
const root=path.resolve(new URL('..',import.meta.url).pathname),out=path.join(root,'artifacts/mobile-xhs-20261103/package');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const skill=path.join(root,'.codex/skills/minitool-zip-builder');
const skillMeta=JSON.parse(await fs.readFile(path.join(skill,'skill-package.json'),'utf8'));
if(skillMeta.version!=='1.8.0')throw Error('Re-read current Creator development Skill before changing the frozen gate');
await fs.rm(out,{recursive:true,force:true});await fs.mkdir(path.join(out,'assets'),{recursive:true});
const keys=MELODY.filter(k=>!k.black).map(k=>({code:k.code,note:k.sub,number:k.label,kind:'note'}));
if(keys.length!==8||keys.map(k=>k.code).join()!=='KeyA,KeyS,KeyD,KeyF,KeyG,KeyH,KeyJ,KeyK')throw Error('Unexpected piano keys');
const songs=SONGS.filter(s=>['twinkle','ode-to-joy'].includes(s.id)).map(s=>({id:s.id,name:s.name,bpm:s.bpm,meter:s.meter,phrases:s.phrases}));
for(const s of songs)for(const row of s.phrases)for(const e of row)if(!keys.some(k=>k.note===e.note))throw Error('Unsupported score event');
const input={},assets=[];
for(const code of ['idle',...keys.map(k=>k.code)]){
 const source='public/character/whole-piano-v3/'+code+'.jpg',original=await fs.readFile(path.join(root,source));input[source]=hash(original);
 const target=path.join(out,'assets',code+'.jpg');
 execFileSync('sips',['-Z','480','-s','format','jpeg','-s','formatOptions','75',path.join(root,source),'--out',target],{stdio:'ignore'});
 const bytes=await fs.readFile(target);assets.push({file:'assets/'+code+'.jpg',source,sourceSha256:hash(original),sha256:hash(bytes),bytes:bytes.length,operation:'whole frame scaled proportionally to480px, JPEG75; no cropping or new artwork'});
}
const manifest=JSON.parse(await fs.readFile(path.join(root,'public/samples/manifest.json'),'utf8')),samples={};
for(const [note,url]of Object.entries(manifest.groups['piano-kw'].noteURLs)){
 const source='public/'+url.slice(2),bytes=await fs.readFile(path.join(root,source));if(bytes.length>100*1024)throw Error('Audio data budget');input[source]=hash(bytes);samples[note]={format:'audio/mpeg',encoding:'base64',bytes:bytes.length,base64:bytes.toString('base64')};
}
await fs.writeFile(path.join(out,'data.js'),'window.MIAO_BEAT_DATA='+JSON.stringify({keys,songs})+';\nwindow.MIAO_PIANO_BYTES='+JSON.stringify({samples})+';\n');
for(const name of ['index.html','style.css','audio-base.js','piano-audio.js','bridge.js','app.js']){const bytes=await fs.readFile(path.join(root,'minitool',name));input['minitool/'+name]=hash(bytes);await fs.writeFile(path.join(out,name),bytes);}
const recording=await fs.readFile(path.join(root,'public/recording.js'),'utf8');input['public/recording.js']=hash(recording);
await fs.writeFile(path.join(out,'recording.js'),'(function(){\n'+recording.replace(/^export /gm,'')+'\nwindow.MiaoBeatRecording={makeRecording:makeRecording,validateRecording:validateRecording};\n})();\n');
const sourceNotices=JSON.parse(await fs.readFile(path.join(root,'minitool/NOTICES.json'),'utf8'));
sourceNotices.bongoCodeNotice={source:'Externalizable/bongo.cat; inherited keyboard mapping baseline',license:'MIT',licenseText:await fs.readFile(path.join(root,'public/UPSTREAM-LICENSE.txt'),'utf8'),boundary:'Code notice only; no Bongo Cat artwork or sound samples included.'};
sourceNotices.pianoLicense=await fs.readFile(path.join(root,'public/samples/CC0-1.0.txt'),'utf8');sourceNotices.sampleProvenance=await fs.readFile(path.join(root,'public/samples/LICENSES.txt'),'utf8');sourceNotices.velocityFormulaLicense=await fs.readFile(path.join(root,'scripts/smplr-LICENSE.txt'),'utf8');await fs.writeFile(path.join(out,'NOTICES.json'),JSON.stringify(sourceNotices,null,2)+'\n');
const files={};async function walk(dir,prefix=''){for(const entry of await fs.readdir(dir,{withFileTypes:true})){const name=prefix+entry.name;if(entry.isDirectory()){await walk(path.join(dir,entry.name),name+'/');continue;}const bytes=await fs.readFile(path.join(dir,entry.name));files[name]=hash(bytes);if(/\.(js|html|css)$/.test(name)){const text=bytes.toString();if(/\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|RTCPeerConnection|eval|WebAssembly|OffscreenCanvas|Worker|SharedWorker)\s*\(|new\s+Function\b|\.download\s*=|\b(?:import|export)\s*(?:\(|\{|\*)|type=["']module|\.at\s*\(|\.flatMap\s*\(|\.finally\s*\(|Object\.hasOwn|\?\.|\?\?/.test(text))throw Error('Forbidden or unsupported runtime token: '+name);}}}
await walk(out);
const buildId=hash(JSON.stringify(files)).slice(0,12);
const entry=path.join(out,'index.html');await fs.writeFile(entry,(await fs.readFile(entry,'utf8')).replace('<body>','<body data-build="'+buildId+'">'));files['index.html']=hash(await fs.readFile(entry));
const directoryAudit=execFileSync(process.execPath,[path.join(skill,'scripts/audit_artifact.mjs'),out],{encoding:'utf8'});
const zip=path.join(path.dirname(out),'miao-beat-xhs-'+buildId+'.zip');execFileSync('python3',['-c','import sys,zipfile;from pathlib import Path;p=Path(sys.argv[1]);z=zipfile.ZipFile(sys.argv[2],"w",zipfile.ZIP_DEFLATED,compresslevel=9);[(lambda i,f:(setattr(i,"compress_type",zipfile.ZIP_DEFLATED),setattr(i,"external_attr",0o100644<<16),z.writestr(i,f.read_bytes())))(zipfile.ZipInfo(f.relative_to(p).as_posix(),(1980,1,1,0,0,0)),f)for f in sorted(p.rglob("*"))if f.is_file()];z.close()',out,zip]);
const zipAudit=execFileSync('python3',[path.join(skill,'scripts/audit_artifact.py'),zip],{encoding:'utf8'}),bytes=await fs.readFile(zip);if(bytes.length>2*1024*1024)throw Error('Exceeds2MiB candidate target');
await fs.copyFile(zip,path.join(path.dirname(out),'miao-beat-xhs.zip'));
const receipt={buildId,builtAt:new Date().toISOString(),sourceCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),skillVersion:skillMeta.version,skillSha256:hash(await fs.readFile(path.join(skill,'SKILL.md'))),out,zip,zipBytes:bytes.length,zipSha256:hash(bytes),runtimeHashes:files,inputs:input,assets,audits:{directoryAudit,zipAudit},scope:'eight-white-key piano; manual scores; real-input recording/replay; silent picture sharing',pending:['same ZIP official simulator','Android/iOS physical input/sound/save/post/return','platform review/publication']};await fs.writeFile(path.join(path.dirname(out),'build-audit.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({zip,bytes:bytes.length,sha256:receipt.zipSha256,audits:receipt.audits}));
