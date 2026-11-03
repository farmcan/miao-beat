/* Adapted from MiaoTarot xiaohongshu.ts/minitoolStorage.ts and MiaoTI bridge.js.
 * MIT Copyright (c) 2026 farmcan; full notice is bundled in NOTICES.json.
 * Modifications: dedicated take key, strict acknowledgements, bounded reads. */
(function(root){
 'use strict';var version=0,queue=Promise.resolve(),KEY='miao-beat:mini:takes:v1';
 function api(){return root.xhs&&root.xhs.miniTool;}
 function readVersion(options){return Math.floor(Number(options&&options.miniToolEnv&&options.miniToolEnv.buildVersion)/1000)||0;}
 function checked(pending){
  if(!pending||typeof pending.then!=='function')return Promise.reject(new Error('未收到平台响应'));
  return pending.then(function(result){if(!result||typeof result.errMsg!=='string'||!/:ok(?:\s|$)/.test(result.errMsg))throw result||new Error('未收到平台确认');return result;});
 }
 function readCall(pending){return new Promise(function(resolve,reject){var timer=setTimeout(function(){reject(new Error('读取超时'));},3000);checked(pending).then(function(v){clearTimeout(timer);resolve(v);},function(e){clearTimeout(timer);reject(e);});});}
 function serial(operation){var next=queue.then(operation,operation);queue=next.catch(function(){});return next;}
 async function insets(){
  var tool=api();if(version<9490||!tool||typeof tool.getWindowInfo!=='function')return;
  try{var info=await readCall(tool.getWindowInfo()),height=info.windowHeight,safe=info.safeArea,buttons=info.menuButtons||{},top=0;
   if(!Number.isFinite(height)||height<=0)return;
   [safe&&safe.top,buttons.back&&buttons.back.bottom,buttons.me&&buttons.me.bottom,buttons.share&&buttons.share.bottom].forEach(function(value){if(Number.isFinite(value)&&value>=0&&value<height)top=Math.max(top,value);});
   root.document.documentElement.style.setProperty('--native-top',top+'px');
   if(safe&&Number.isFinite(safe.bottom)&&safe.bottom>=0&&safe.bottom<=height)root.document.documentElement.style.setProperty('--native-bottom',(height-safe.bottom)+'px');
  }catch(error){/* Keep CSS safe-area fallback. */}
 }
 async function init(){var x=root.xhs,tool=api();version=readVersion(x&&x.launchOptions);if(!version&&tool&&typeof tool.getLaunchOptions==='function'){try{version=readVersion(await readCall(tool.getLaunchOptions()));}catch(error){}}
  await insets();return capabilities();
 }
 function capabilities(){var tool=api();return{save:!!tool&&version>=9420&&typeof tool.saveImageToPhotosAlbum==='function',post:!!tool&&typeof tool.postNote==='function'};}
 function load(){return serial(async function(){var tool=api();if(version>=9460){if(!tool||typeof tool.getStorage!=='function')throw new Error('平台缓存不可用');return (await readCall(tool.getStorage({key:KEY}))).data||null;}return root.localStorage.getItem(KEY);});}
 function put(value){return serial(async function(){var tool=api();if(version>=9460){if(!tool||typeof tool.setStorage!=='function')throw new Error('平台缓存不可用');await checked(tool.setStorage({key:KEY,data:value}));}else root.localStorage.setItem(KEY,value);});}
 async function imagePath(data){if(typeof data!=='string'||!/^data:image\/(?:png|jpeg);base64,[a-z\d+/=]+$/i.test(data))throw new Error('小卡图片未准备好');
  if(data.length<=1300000)return data;
  var tool=api();if(!tool||typeof tool.writeTempFile!=='function')throw new Error('图片较大，请稍后重试');
  var result=await checked(tool.writeTempFile({data:data}));if(typeof result.filePath!=='string'||!result.filePath||/^(?:https?:|data:|\/\/)/i.test(result.filePath))throw new Error('未收到本地图片');return result.filePath;
 }
 async function save(data){if(!capabilities().save)throw new Error('当前版本暂不支持保存相册');await checked(api().saveImageToPhotosAlbum({filePath:await imagePath(data)}));}
 async function post(data){if(!capabilities().post)throw new Error('当前环境暂不支持带入笔记');await checked(api().postNote({title:'和橘猫弹了一小段',content:'我的真人演奏小卡，图片不带声音。猫图由AI辅助制作。',pageType:'photo_publish',mediaInfo:{image_resources:[{url:await imagePath(data)}]}}));}
 root.MiaoBeatBridge={init:init,load:load,put:put,capabilities:capabilities,save:save,post:post};root.addEventListener('resize',function(){void insets();});
}(window));
