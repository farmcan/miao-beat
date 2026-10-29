// Local authoring QA only. Main product/public files are not changed.
const $=id=>document.getElementById(id);
let renderer,scene,camera,controls,loaded=false,initialPosition,initialQuaternion;
function draw(){
  if(!loaded)return;
  const canvas=$('scene'),width=canvas.clientWidth,height=canvas.clientHeight;
  renderer.setSize(width,height,false);
  camera.left=-.69*width/height;camera.right=.69*width/height;camera.top=.69;camera.bottom=-.69;camera.updateProjectionMatrix();
  renderer.render(scene,camera);
  canvas.dataset.triangles=String(renderer.info.render.triangles);
  canvas.dataset.drawCalls=String(renderer.info.render.calls);
}
$('load').addEventListener('click',async()=>{
  $('load').disabled=true;$('status').textContent='正在下载模型…';
  try{
    const T=await import('../../../public/labs/character-compare/vendor/three-runtime.mjs');
    renderer=new T.WebGLRenderer({canvas:$('scene'),antialias:true,preserveDrawingBuffer:true});
    renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));renderer.outputColorSpace=T.SRGBColorSpace;
    // Pinned Three 0.186.1 maps enum 4 to ACESFilmic in this vendor bundle.
    // This display lighting approximates bpy and needs separate visual review.
    renderer.toneMapping=4;renderer.toneMappingExposure=.8;
    renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;
    scene=new T.Scene();scene.background=new T.Color(0xe5e4df);
    scene.add(new T.HemisphereLight(0xffffff,0xa4a7a8,2.2));
    const key=new T.DirectionalLight(0xfff7ec,2.8);key.position.set(-1.2,2.6,2.2);key.castShadow=true;
    key.shadow.mapSize.set(1024,1024);key.shadow.radius=4;Object.assign(key.shadow.camera,{left:-1.1,right:1.1,top:1.4,bottom:-.7,near:.1,far:7});
    key.shadow.normalBias=.0005;key.shadow.bias=-.000001;key.target.position.set(0,.5,.1);scene.add(key,key.target);
    const fill=new T.DirectionalLight(0xe4edff,1.1);fill.position.set(1.5,1.1,1.6);scene.add(fill);
    const url=new URL('../../../artifacts/miao-reuse-keyboard-v1/static-web-roundtrip-no-unused-colors/keyboard-static-test.glb',import.meta.url);
    const asset=await new T.GLTFLoader().loadAsync(url.href,event=>{
      $('status').textContent=`正在下载模型 · ${(event.loaded/1000000).toFixed(1)} MB`;
    });
    scene.add(asset.scene);asset.scene.updateMatrixWorld(true);camera=asset.cameras[0];
    if(!camera?.isOrthographicCamera)throw Error('缺少原生正交相机');
    scene.attach(camera);initialPosition=camera.position.clone();initialQuaternion=camera.quaternion.clone();
    asset.scene.traverse(object=>{if(object.isMesh){object.castShadow=!object.name.startsWith('ENV-');object.receiveShadow=true;}});
    controls=new T.OrbitControls(camera,$('scene'));controls.target.set(0,.53,.13);controls.enablePan=false;controls.enableZoom=false;controls.enableDamping=false;
    // Authoring diagnostic only: source face GN was baked for the front camera.
    controls.minAzimuthAngle=-Math.PI/8;controls.maxAzimuthAngle=Math.PI/8;
    controls.minPolarAngle=1.1;controls.maxPolarAngle=1.35;controls.addEventListener('change',draw);
    loaded=true;controls.update();draw();$('placeholder').hidden=true;$('reset').disabled=false;
    $('scene').dataset.ready='true';$('status').textContent='模型已加载 · 可轻拖查看，弹奏尚未接入';
  }catch(error){
    renderer?.dispose();$('status').textContent='加载失败：'+error.message;$('load').disabled=false;$('load').textContent='重试加载';
    $('scene').dataset.error=error.message;
  }
});
$('reset').addEventListener('click',()=>{if(!loaded)return;camera.position.copy(initialPosition);camera.quaternion.copy(initialQuaternion);controls.target.set(0,.53,.13);controls.update();draw();});
addEventListener('resize',draw);
addEventListener('pagehide',()=>{controls?.dispose();renderer?.dispose();});
