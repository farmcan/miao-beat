import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const root=path.dirname(path.dirname(new URL(import.meta.url).pathname));
const pkg=JSON.parse(await fs.readFile(path.join(root,'node_modules/smplr/package.json')));
if(pkg.version!=='1.1.0'||pkg.license!=='MIT')throw Error('Unreviewed audio runtime');
await fs.mkdir(path.join(root,'public/vendor'),{recursive:true});
const vendor=(await fs.readFile(path.join(root,'node_modules/smplr/dist/index.mjs'),'utf8')).replace(/\/\/# sourceMappingURL=.*$/m,'');
await fs.writeFile(path.join(root,'public/vendor/smplr.mjs'),vendor);
await fs.copyFile(path.join(root,'scripts/smplr-LICENSE.txt'),path.join(root,'public/vendor/smplr-LICENSE.txt'));
const allowed=['index.html','style.css','icon.svg','app.js','audio.js','sampled-audio.js','bindings.js','clock.js','recording.js','scores.js','UPSTREAM-LICENSE.txt','_headers','vendor/smplr.mjs','vendor/smplr-LICENSE.txt','samples/manifest.json','samples/LICENSES.txt','samples/CC0-1.0.txt','character.js','performance.js','guidance.js','character/plush-atlas-v1.png','character/rig.css','character/manifest.json','character/README.md'];
const art=JSON.parse(await fs.readFile(path.join(root,'public/character/manifest.json')));
for(const asset of art.assets){if(!allowed.includes(asset.filename))throw Error('Unreviewed character file');const bytes=await fs.readFile(path.join(root,'public',asset.filename));if(createHash('sha256').update(bytes).digest('hex')!==asset.sha256)throw Error('Character provenance differs: '+asset.filename);}
const manifest=JSON.parse(await fs.readFile(path.join(root,'public/samples/manifest.json')));
for(const group of Object.values(manifest.groups))for(const url of Object.values(group.noteURLs)){
 if(!/^\.\/samples\/[a-z-]+\/[A-Za-z0-9-]+\.mp3$/.test(url))throw Error('Invalid sample path');allowed.push(url.slice(2));
}
async function list(dir,prefix=''){const names=[];for(const entry of await fs.readdir(dir,{withFileTypes:true})){const name=prefix+entry.name;if(entry.isSymbolicLink())throw Error('Symlink in public');if(entry.isDirectory())names.push(...await list(path.join(dir,entry.name),name+'/'));else names.push(name);}return names;}
const actual=await list(path.join(root,'public'));
if(actual.sort().join('|')!==[...allowed].sort().join('|'))throw Error('Unexpected public artifact: '+actual.filter(n=>!allowed.includes(n)).join(','));
await fs.rm(path.join(root,'dist'),{recursive:true,force:true});await fs.mkdir(path.join(root,'dist'));
const files={};for(const name of allowed){
 const content=await fs.readFile(path.join(root,'public',name));
 const text=/\.(mp3|png)$/.test(name)?'':content.toString();
 const maxBytes=name==='character/plush-atlas-v1.png'?2000000:256000;
 if(content.length>maxBytes||/\/Users\/|oauth_token|BEGIN PRIVATE KEY|farmcan(?:-seed)?\.pages\.dev/.test(text))throw Error('Invalid public file: '+name);
 await fs.mkdir(path.dirname(path.join(root,'dist',name)),{recursive:true});await fs.writeFile(path.join(root,'dist',name),content);files[name]=createHash('sha256').update(content).digest('hex');
}
let commit='local';try{commit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim();}catch{}
await fs.writeFile(path.join(root,'dist/release.json'),JSON.stringify({project:'miao-beat',version:'0.5.0-v2',commit,files},null,2)+'\n');
console.log('Built '+allowed.length+' explicit public files; four sampled instruments and a component-based plush character.');
