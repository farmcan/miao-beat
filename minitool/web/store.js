// Hydrate synchronous shared-web storage before mounting; native writes serialize.
const values=new Map(),blocked=new Set();let tool,version=0,queue=Promise.resolve();
const keys=['miao-beat:takes:v1','miao-beat:practice:v1','miao-beat:key-labels'];
function check(result,name){if(!result||result.errMsg!==name+':ok')throw result||Error('平台缓存未确认');return result;}
async function read(key){if(version>=9460){if(!tool||!tool.getStorage)throw Error('缓存不可用');return check(await tool.getStorage({key}), 'getStorage').data||null;}return localStorage.getItem(key);}
function write(key,value){if(blocked.has(key))throw Error('旧缓存未读到，禁止覆盖');values.set(key,value);queue=queue.then(async()=>{if(version>=9460){if(!tool||!tool.setStorage)throw Error('缓存不可用');if(value===null)check(await tool.removeStorage({key}),'removeStorage');else check(await tool.setStorage({key,data:value}),'setStorage');}else if(value===null)localStorage.removeItem(key);else localStorage.setItem(key,value);}).catch(()=>{const n=document.getElementById('draftStatus');if(n)n.textContent='本机保存未获确认；当前片段仍可回放和导出视频。';});}
export async function boot(){
 tool=window.xhs&&window.xhs.miniTool;let options=window.xhs&&window.xhs.launchOptions;
 if(!options&&tool&&tool.getLaunchOptions)try{options=await Promise.race([tool.getLaunchOptions(),new Promise((_,reject)=>setTimeout(()=>reject(Error('平台响应超时')),3000))]);}catch{}
 version=Math.floor(Number(options&&options.miniToolEnv&&options.miniToolEnv.buildVersion)/1000)||0;
 await Promise.all(keys.map(async key=>{try{const raw=await Promise.race([read(key),new Promise((_,reject)=>setTimeout(()=>reject(Error('缓存读取超时')),3000))]);if(raw)values.set(key,raw);}catch{blocked.add(key);}}));
 // The former eight-key draft uses the same first eight CODES. Migrate only after successful reads.
 if(!values.has(keys[0])&&!blocked.has(keys[0]))try{const raw=await Promise.race([read('miao-beat:mini:takes:v1'),new Promise((_,reject)=>setTimeout(()=>reject(Error('旧草稿读取超时')),3000))]);if(raw){const old=JSON.parse(raw);if(old.version===1)values.set(keys[0],JSON.stringify({version:1,current:old.take,previous:old.previous}));}}catch{}
 window.MiaoMiniStore={getItem:key=>values.get(key)||null,setItem:write,removeItem:key=>write(key,null)};
 if(version>=9490&&tool&&tool.getWindowInfo)try{const i=check(await tool.getWindowInfo(),'getWindowInfo');if(i.safeArea&&Number.isFinite(i.safeArea.top))document.documentElement.style.setProperty('--native-top',i.safeArea.top+'px');}catch{}
}
