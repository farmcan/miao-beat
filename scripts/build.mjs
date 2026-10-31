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
const allowed=['index.html','style.css','icon.svg','support-alipay-qr.jpg','app.js','audio.js','sampled-audio.js','bindings.js','clock.js','recording.js','scores.js','UPSTREAM-LICENSE.txt','_headers','vendor/smplr.mjs','vendor/smplr-LICENSE.txt','samples/manifest.json','samples/LICENSES.txt','samples/CC0-1.0.txt','character.js','performance.js','guidance.js','character/plush-atlas-v1.png','character/indie-atlas-v2.png','character/orange-components-v3.png','character/orange-instruments-v3.png','character/rig.css','character/manifest.json','character/README.md','labs/orange-guitar/index.html','labs/orange-guitar/pilot.js','labs/orange-guitar/style.css','labs/orange-guitar/atlas-v1.png','whole-character.js','keyboard-navigation.js','character/whole.css','character/keyboard-poses-v1.jpg','character/keyboard-motion-v1.json','character/keyboard-demo-v1.mp4','labs/keyboard-motion/index.html','labs/keyboard-motion/style.css'];
const blenderLab=JSON.parse(await fs.readFile(path.join(root,'public/labs/blender-guitar/manifest.json')));
if(blenderLab.version!==1||blenderLab.frames!==24||blenderLab.width!==640||blenderLab.height!==640||blenderLab.columns!==6||blenderLab.rows!==4||blenderLab.contactFrame!==2||blenderLab.fps!==60||!blenderLab.completeScene)throw Error('Unreviewed Blender test scene');
const blenderAtlas=await fs.readFile(path.join(root,'public/labs/blender-guitar/atlas.webp'));
if(blenderAtlas.length!==blenderLab.atlasBytes||createHash('sha256').update(blenderAtlas).digest('hex')!==blenderLab.atlasSha256)throw Error('Blender atlas differs');
if(createHash('sha256').update(await fs.readFile(path.join(root,'design/blender-guitar-v1/scene.py'))).digest('hex')!==blenderLab.sourceScriptSha256)throw Error('Blender authoring source differs');
allowed.push(...['index.html','style.css','pilot.js','motion.js','manifest.json','atlas.webp','poster.webp'].map(file=>'labs/blender-guitar/'+file));
allowed.push('media-export.js','site-counter.js','_worker.js','_routes.json','character/guitar-whole-still-v1.jpg','character/drums-whole-still-v1.jpg');
const compareFiles=['index.html','stills.html','play.css','play.js','three-renderer.js','motion-controller.js','model/miao-playable.glb','model/manifest.json','vendor/three-runtime.mjs','vendor/three-LICENSE.txt','vendor/three-provenance.json','evidence.json','images/original.jpg','images/blender-color.png','images/godot-static.png','images/blender-hand-gray.png','images/blender-gray-three-quarter.png'];
const godotFiles=['godot-page.css','godot-start.js','index.html','index.js','index.pck','index.png','index.wasm.gz','index.audio.worklet.js','index.audio.position.worklet.js','compressed-wasm.js','export-evidence.json','GODOT-LICENSE.txt','GODOT-COPYRIGHT.txt'];
const godotEvidence=JSON.parse(await fs.readFile(path.join(root,'public/labs/character-compare/godot/export-evidence.json')));
for(const file of godotEvidence.files){
 if(!godotFiles.includes(file.name))throw Error('Unexpected Godot asset');
 const bytes=await fs.readFile(path.join(root,'public/labs/character-compare/godot',file.name));
 if(bytes.length!==file.bytes||createHash('sha256').update(bytes).digest('hex')!==file.sha256)throw Error('Godot export differs: '+file.name);
}
if(godotEvidence.files.length!==godotFiles.length-1)throw Error('Incomplete Godot provenance');
compareFiles.push(...godotFiles.map(file=>'godot/'+file));
if(createHash('sha256').update(await fs.readFile(path.join(root,'public/labs/character-compare/model/miao-playable.glb'))).digest('hex')!=='1a384c0a9a13ed60710469b7d9a4de646a8599fe3dcff5ef85d1f42c825cedf9')throw Error('Playable model differs');
const compareEvidence=JSON.parse(await fs.readFile(path.join(root,'public/labs/character-compare/evidence.json')));
if(compareEvidence.images.length!==5)throw Error('Incomplete three-version comparison');
for(const image of compareEvidence.images){
 if(!compareFiles.includes(image.file))throw Error('Unexpected comparison image');
 const bytes=await fs.readFile(path.join(root,'public/labs/character-compare',image.file));
 if(createHash('sha256').update(bytes).digest('hex')!==image.sha256)throw Error('Comparison image provenance differs');
}
allowed.push(...compareFiles.map(file=>'labs/character-compare/'+file));
const reusePrefix='labs/reuse-keyboard/';
const reuseReview=JSON.parse(await fs.readFile(path.join(root,'public',reusePrefix,'review.json')));
if(reuseReview.version!==1||reuseReview.scope!=='standalone-A-C4-experiment'||reuseReview.productionCharacterReplacement!==false||reuseReview.supportedKeys?.join()!=='KeyA'||reuseReview.supportedMidi?.join()!=='60'||reuseReview.webGate!=='experimental-page-go')throw Error('Unreviewed reused-keyboard experiment');
if(reuseReview.assets.length!==3)throw Error('Unexpected reused-keyboard assets');
if(new Set(reuseReview.assets.map(asset=>asset.file)).size!==3||!reuseReview.assets.some(asset=>asset.file===reuseReview.modelFile)||!reuseReview.assets.some(asset=>asset.file===reuseReview.metadataFile))throw Error('Reused-keyboard manifest paths differ');
for(const asset of reuseReview.assets){
 if(!/^(?:model\/miao-one-key-[a-f0-9]{8}\.glb|model\/metadata-[a-f0-9]{8}\.json|poster-[a-f0-9]{8}\.png)$/.test(asset.file))throw Error('Unreviewed reused-keyboard file');
 const bytes=await fs.readFile(path.join(root,'public',reusePrefix,asset.file));
 if(bytes.length!==asset.bytes||createHash('sha256').update(bytes).digest('hex')!==asset.sha256)throw Error('Reused-keyboard provenance differs');
 if(asset.file.match(/-([a-f0-9]{8})\.(?:glb|json|png)$/)?.[1]!==asset.sha256.slice(0,8))throw Error('Reused-keyboard fingerprint differs');
 allowed.push(reusePrefix+asset.file);
}
const reuseMeta=JSON.parse(await fs.readFile(path.join(root,'public',reusePrefix,reuseReview.metadataFile)));
if(reuseMeta.modelFile!==path.basename(reuseReview.modelFile)||reuseMeta.modelSha256!=='5c20616b3f7f1cbbdff257fb10729519c84eaf940bfee467803ba29fc5e0b69a'||reuseMeta.keyNode!=='MiaoKeyC4')throw Error('Unexpected reused-keyboard model');
const reuseModel=await fs.readFile(path.join(root,'public',reusePrefix,reuseReview.modelFile));
if(createHash('sha256').update(reuseModel).digest('hex')!==reuseMeta.modelSha256)throw Error('Reused-keyboard model is not the reviewed source');
if(reuseModel.readUInt32LE(0)!==0x46546c67||reuseModel.readUInt32LE(4)!==2||reuseModel.readUInt32LE(8)!==reuseModel.length)throw Error('Invalid reused-keyboard GLB');
const reuseGltf=JSON.parse(reuseModel.subarray(20,20+reuseModel.readUInt32LE(12)).toString());
if(reuseGltf.skins?.length||reuseGltf.animations?.length||reuseGltf.buffers.some(buffer=>buffer.uri)||reuseGltf.images?.some(image=>image.uri)||reuseGltf.nodes.filter(node=>node.name==='MiaoKeyC4').length!==1)throw Error('Unexpected reused-keyboard payload');
const reuseMorphs=reuseGltf.meshes.filter(mesh=>mesh.primitives.some(primitive=>primitive.targets?.length));
if(reuseMorphs.length!==1||reuseMorphs[0].extras?.targetNames?.join()!=='Contact,Down'||reuseGltf.meshes.some(mesh=>mesh.primitives.some(primitive=>primitive.attributes.COLOR_0!==undefined)))throw Error('Unexpected reused-keyboard deformation');
allowed.push(...['index.html','style.css','play.js','motion.js','model.js','credits.txt','review.json'].map(file=>reusePrefix+file));
const wholeFrames=JSON.parse(await fs.readFile(path.join(root,'public/character/whole-piano-v3/manifest.json')));
const {validateFrameManifest,validateInstrumentManifest}=await import('../public/full-frame-character.js');validateFrameManifest(wholeFrames);
allowed.push('full-frame-character.js','character/whole-piano-v3/manifest.json',...Object.values(wholeFrames.frames).map(name=>'character/whole-piano-v3/'+name));
for(const frame of wholeFrames.provenance){const bytes=await fs.readFile(path.join(root,'public/character/whole-piano-v3',frame.file));if(createHash('sha256').update(bytes).digest('hex')!==frame.sha256)throw Error('Complete-frame provenance differs: '+frame.id);}
const instrumentScenes=validateInstrumentManifest(JSON.parse(await fs.readFile(path.join(root,'public/character/instrument-scenes-v1/manifest.json'))));
allowed.push('character/instrument-scenes-v1/manifest.json',...Object.values(instrumentScenes.modes).flatMap(mode=>Object.values(mode.frames).map(name=>'character/instrument-scenes-v1/'+name)));
if(instrumentScenes.provenance.length!==43)throw Error('Missing complete instrument provenance');
for(const frame of instrumentScenes.provenance){const bytes=await fs.readFile(path.join(root,'public/character/instrument-scenes-v1',frame.file));if(createHash('sha256').update(bytes).digest('hex')!==frame.sha256)throw Error('Instrument scene differs: '+frame.mode+':'+frame.id);}
const {validateGuitarMotionManifest}=await import('../public/guitar-motion.js');
const motion=validateGuitarMotionManifest(JSON.parse(await fs.readFile(path.join(root,'public/character/guitar-motion-v1/manifest.json'))));
allowed.push('guitar-motion.js','character/guitar-motion-v1/manifest.json','character/guitar-motion-v1/RIFE-LICENSE.txt',...motion.edges.map(e=>'character/guitar-motion-v1/'+e.file));
for(const e of motion.edges){const bytes=await fs.readFile(path.join(root,'public/character/guitar-motion-v1',e.file));if(bytes.length!==e.bytes||createHash('sha256').update(bytes).digest('hex')!==e.sha256)throw Error('Guitar transition differs: '+e.id);}
for(const p of Object.values(motion.poses)){if(createHash('sha256').update(await fs.readFile(path.join(root,'public',p.source))).digest('hex')!==p.sha256)throw Error('Guitar motion source differs');}
const {validateGuitarPluckManifest}=await import('../public/guitar-motion.js');
const plucks=validateGuitarPluckManifest(JSON.parse(await fs.readFile(path.join(root,'public/character/guitar-pluck-v1/manifest.json'))));
allowed.push('character/guitar-pluck-v1/manifest.json',...Object.values(plucks.clips).flatMap(c=>['character/guitar-pluck-v1/'+c.up.file,'character/guitar-pluck-v1/'+c.atlas.file]));
for(const c of Object.values(plucks.clips))for(const [kind,e]of Object.entries(c)){const file=kind==='down'?e.file:'character/guitar-pluck-v1/'+e.file;const bytes=await fs.readFile(path.join(root,'public',file));if(bytes.length!==e.bytes||createHash('sha256').update(bytes).digest('hex')!==e.sha256)throw Error('Guitar pluck differs: '+file);}
const art=JSON.parse(await fs.readFile(path.join(root,'public/character/manifest.json')));
for(const asset of art.assets){if(!allowed.includes(asset.filename))throw Error('Unreviewed character file');const bytes=await fs.readFile(path.join(root,'public',asset.filename));if(createHash('sha256').update(bytes).digest('hex')!==asset.sha256)throw Error('Character provenance differs: '+asset.filename);}
const manifest=JSON.parse(await fs.readFile(path.join(root,'public/samples/manifest.json')));
for(const group of Object.values(manifest.groups))for(const url of Object.values(group.noteURLs)){
 if(!/^\.\/samples\/[a-z-]+\/[A-Za-z0-9-]+\.mp3$/.test(url))throw Error('Invalid sample path');allowed.push(url.slice(2));
}
async function list(dir,prefix=''){const names=[];for(const entry of await fs.readdir(dir,{withFileTypes:true})){const name=prefix+entry.name;if(entry.isSymbolicLink())throw Error('Symlink in public');if(entry.isDirectory())names.push(...await list(path.join(dir,entry.name),name+'/'));else names.push(name);}return names;}
// The unshipped continuity timing study is intentionally excluded from production.
const actual=(await list(path.join(root,'public'))).filter(name=>!name.startsWith('labs/image-continuity/'));
if(actual.sort().join('|')!==[...allowed].sort().join('|'))throw Error('Unexpected public artifact: '+actual.filter(n=>!allowed.includes(n)).join(','));
await fs.rm(path.join(root,'dist'),{recursive:true,force:true});await fs.mkdir(path.join(root,'dist'));
const files={};for(const name of allowed){
 const content=await fs.readFile(path.join(root,'public',name));
 const text=/\.(mp3|png|jpg|mp4|webp|glb|pck|gz)$/.test(name)?'':content.toString();
 const maxBytes=/^(?:labs\/character-compare\/(?:model\/miao-playable\.glb|godot\/index\.(?:pck|wasm\.gz))|labs\/reuse-keyboard\/model\/miao-one-key-[a-f0-9]{8}\.glb)$/.test(name)?25*1024*1024:/^labs\/character-compare\/(?:vendor\/three-runtime\.mjs|godot\/index\.js)$/.test(name)?1000000:/^labs\/blender-guitar\/.*\.webp$/.test(name)?3000000:/^character\/.*\.mp4$/.test(name)?8000000:/^(?:character\/|labs\/(?:orange-guitar|character-compare|reuse-keyboard)\/).*\.(png|jpg|webp)$/.test(name)?2000000:256000;
 if(content.length>maxBytes||/\/Users\/|oauth_token|BEGIN PRIVATE KEY|farmcan(?:-seed)?\.pages\.dev/.test(text))throw Error('Invalid public file: '+name);
 await fs.mkdir(path.dirname(path.join(root,'dist',name)),{recursive:true});await fs.writeFile(path.join(root,'dist',name),content);files[name]=createHash('sha256').update(content).digest('hex');
}
let commit='local';try{commit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim();}catch{}
await fs.writeFile(path.join(root,'dist/release.json'),JSON.stringify({project:'miao-beat',version:'0.17.2-experience',commit,files},null,2)+'\n');
console.log('Built '+allowed.length+' explicit public files; whole-scene piano, guitar and drum poses, four sampled sounds and a visit counter.');
