import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {mountFamilyReferrals,familyLanding} from '../public/family-referrals.js';
import {recordFamilyReferral} from '../public/family-referral-server.mjs';
const hosts={miaoti:'miaoti-dmv.pages.dev','miao-beat':'miao-beat.pages.dev',miaotarot:'tarot-31o.pages.dev'};
test('all six directions retain bounded source, placement and internal QA tags',async()=>{
 for(const from of Object.keys(hosts))for(const to of Object.keys(hosts))if(from!==to){
  const dom=new JSDOM(`<a href="https://${hosts[to]}/?utm_source=old" data-family-placement="result">Next</a>`,{url:`https://${hosts[from]}/?analytics=internal`});
  const sent=[];const control=mountFamilyReferrals(dom.window.document,{project:from,beacon:()=>false,fetchImpl:async(url,options)=>{sent.push({url,options});return new Response(null,{status:202});}});
  const link=dom.window.document.querySelector('a');dom.window.document.addEventListener('click',e=>e.preventDefault());link.dispatchEvent(new dom.window.MouseEvent('click',{bubbles:true,cancelable:true}));
  assert.equal(sent.length,1);const endpoint=new URL(sent[0].url,'https://example.com');assert.equal(endpoint.searchParams.get('kind'),'click');assert.equal(endpoint.searchParams.get('peer'),to);assert.equal(endpoint.searchParams.get('traffic'),'internal');assert.equal(sent[0].options.keepalive,true);assert.equal(sent[0].options.body,undefined);
  const target=new URL(link.href);assert.equal(target.searchParams.get('utm_source'),from);assert.equal(target.searchParams.get('utm_content'),'result');assert.equal(target.searchParams.get('analytics'),'internal');
  assert.deepEqual(familyLanding(link.href),{peer:from,placement:'result'});control.destroy();dom.window.close();
 }
});
test('arrivals are distinct from clicks, reloads do not create new arrivals, dynamic links work',async()=>{
 const dom=new JSDOM('<div id="root"></div>',{url:'https://tarot-31o.pages.dev/?utm_source=miaoti&utm_content=intro'}),doc=dom.window.document,sent=[];
 dom.window.performance.getEntriesByType=()=>[{type:'navigate'}];const options={project:'miaotarot',beacon:url=>{sent.push(url);return true;}};
 const control=mountFamilyReferrals(doc,options);mountFamilyReferrals(doc,options);assert.equal(sent.length,1);assert.match(sent[0],/kind=arrival/);assert.match(sent[0],/placement=intro/);
 const a=doc.createElement('a');a.href='https://miao-beat.pages.dev/';doc.body.append(a);await new Promise(setImmediate);assert.equal(new URL(a.href).searchParams.get('utm_source'),'miaotarot');
 control.destroy();dom.window.performance.getEntriesByType=()=>[{type:'reload'}];mountFamilyReferrals(doc,options);assert.equal(sent.length,1);dom.window.close();
 assert.equal(familyLanding('https://miao-beat.pages.dev/?utm_source=private-name','https://miaoti-dmv.pages.dev/'),null);
 assert.equal(familyLanding('https://miao-beat.pages.dev/','https://miaoti-dmv.pages.dev.evil.example/'),null);
});
test('unavailable analytics never cancel navigation or copy private landing parameters',()=>{
 const dom=new JSDOM('<a href="https://tarot-31o.pages.dev/">Next</a>',{url:'https://miao-beat.pages.dev/?recording=private&user=private&analytics=internal'});
 const c=mountFamilyReferrals(dom.window.document,{project:'miao-beat',beacon:()=>{throw Error('offline');}}),link=dom.window.document.querySelector('a');
 const event=new dom.window.MouseEvent('click',{bubbles:true,cancelable:true});link.dispatchEvent(event);assert.equal(event.defaultPrevented,false);assert.equal(new URL(link.href).searchParams.has('recording'),false);assert.equal(new URL(link.href).searchParams.has('user'),false);c.destroy();dom.window.close();
});
test('server infers source/target from its own fixed project for all six directions and both stages',async()=>{
 const rows=[],db={prepare(sql){assert.match(sql,/date\('now','\+8 hours'\)/);return {bind(...values){return {run:async()=>{rows.push(values);}};}};}};
 for(const from of Object.keys(hosts))for(const to of Object.keys(hosts))if(from!==to)for(const kind of ['click','arrival']){
  const project=kind==='click'?from:to,peer=kind==='click'?to:from;
  const request=new Request(`https://${hosts[project]}/api/family-referral?kind=${kind}&peer=${peer}&placement=family&traffic=internal`,{method:'POST'});
  const r=await recordFamilyReferral(request,db,project);assert.equal(r.status,202);assert.equal((await r.json()).counted,true);assert.deepEqual(rows.at(-1),[from,to,'family',kind,'internal']);
 }
 assert.equal(rows.length,12);
});
test('server rejects arbitrary labels, bodies, duplicates, cross-site requests and methods; previews/bots do not write',async()=>{
 let writes=0;const db={prepare(){return {bind(){return {run:async()=>{writes++;}};}};}};
 const base='https://miao-beat.pages.dev/api/family-referral?kind=click&peer=miaoti&placement=family';
 for(const [url,options,status]of [[base,{},405],[base,{method:'POST',body:'{}'},400],[base,{method:'POST',headers:{origin:'https://evil.example'}},403],[base+'&from=private',{method:'POST'},400],[base+'&peer=miaotarot',{method:'POST'},400],[base.replace('peer=miaoti','peer=private'),{method:'POST'},400]])assert.equal((await recordFamilyReferral(new Request(url,options),db,'miao-beat')).status,status);
 for(const req of [new Request(base.replace('miao-beat.pages.dev','preview.miao-beat.pages.dev'),{method:'POST'}),new Request(base,{method:'POST',headers:{'user-agent':'TestBot'}})])assert.equal((await (await recordFamilyReferral(req,db,'miao-beat')).json()).counted,false);
 assert.equal(writes,0);assert.equal((await recordFamilyReferral(new Request(base,{method:'POST'}),null,'miao-beat')).status,503);
 const broken={prepare(){throw Error('db');}};assert.equal((await recordFamilyReferral(new Request(base,{method:'POST'}),broken,'miao-beat')).status,503);
});
