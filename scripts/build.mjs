import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const root=path.dirname(path.dirname(new URL(import.meta.url).pathname));
const allowed=['index.html','style.css','icon.svg','app.js','audio.js','bindings.js','clock.js','recording.js','scores.js','UPSTREAM-LICENSE.txt','_headers'];
const actual=await fs.readdir(path.join(root,'public'));
if(actual.sort().join('|')!==[...allowed].sort().join('|'))throw Error('Unexpected public artifact');
await fs.rm(path.join(root,'dist'),{recursive:true,force:true});await fs.mkdir(path.join(root,'dist'));
const files={};for(const name of allowed){
  const content=await fs.readFile(path.join(root,'public',name));
  if(content.length>256000||/\/Users\/|oauth_token|BEGIN PRIVATE KEY/.test(content.toString()))throw Error('Invalid public file: '+name);
  await fs.writeFile(path.join(root,'dist',name),content);files[name]=createHash('sha256').update(content).digest('hex');
}
let commit='local';try{commit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim();}catch{}
await fs.writeFile(path.join(root,'dist/release.json'),JSON.stringify({project:'miao-beat',version:'0.1.0-ui',commit,files},null,2)+'\n');
console.log('Built '+allowed.length+' explicit public files; audio redesign remains pending.');
