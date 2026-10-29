export async function loadOneKeyModel(canvas,onProgress=()=>{}) {
  const base=new URL('../../../artifacts/miao-reuse-keyboard-v1/single-key-web-morph/',import.meta.url);
  const [T,response]=await Promise.all([
    import('../../../public/labs/character-compare/vendor/three-runtime.mjs'),
    fetch(new URL('metadata.json',base)),
  ]);
  if(!response.ok)throw Error('模型清单未载入');
  const meta=await response.json();
  if(meta.version!==1||!/^[-\w]+\.glb$/.test(meta.modelFile)||!(meta.contactFraction>0&&meta.contactFraction<1)||!Array.isArray(meta.trajectory)||meta.trajectory.length<2)throw Error('模型动作清单不匹配');
  const renderer=new T.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));renderer.outputColorSpace=T.SRGBColorSpace;
  renderer.toneMapping=4;renderer.toneMappingExposure=1.1; // Pinned Three 0.186.1 ACESFilmic.
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;
  const scene=new T.Scene();scene.background=new T.Color(0xe5e4df);
  scene.add(new T.HemisphereLight(0xffffff,0xa4a7a8,2.5));
  const keyLight=new T.DirectionalLight(0xfff7ec,2.4);keyLight.position.set(-1.2,2.6,2.2);keyLight.castShadow=true;
  keyLight.shadow.mapSize.set(1024,1024);keyLight.shadow.radius=4;keyLight.shadow.intensity=.4;
  Object.assign(keyLight.shadow.camera,{left:-1.1,right:1.1,top:1.4,bottom:-.7,near:.1,far:7});
  keyLight.shadow.normalBias=.0005;keyLight.shadow.bias=-.000001;keyLight.target.position.set(0,.5,.1);scene.add(keyLight,keyLight.target);
  const fill=new T.DirectionalLight(0xe4edff,1.5);fill.position.set(1.5,1.1,1.6);scene.add(fill);
  const gltf=await new T.GLTFLoader().loadAsync(new URL(meta.modelFile,base).href,onProgress);
  const root=gltf.scene;scene.add(root);root.updateMatrixWorld(true);
  const camera=gltf.cameras[0];if(!camera?.isOrthographicCamera)throw Error('模型缺少已验相机');scene.attach(camera);
  const parts=[];root.traverse(object=>{
    if(!object.isMesh)return;object.castShadow=!object.name.startsWith('ENV-');object.receiveShadow=true;
    if(object.morphTargetDictionary?.[meta.morphNames.contact]!==undefined&&object.morphTargetDictionary?.[meta.morphNames.down]!==undefined)parts.push(object);
  });
  if(!parts.length)throw Error('模型缺少已验手部动作');
  const key=root.getObjectByName(meta.keyNode);if(!key)throw Error('模型缺少C4琴键');
  // The imported root is an identity Group. Its empty clone supplies a pivot
  // without constructing or replacing any character or instrument geometry.
  const pivot=root.clone(false);pivot.name='MiaoKeyPivotC4';pivot.position.set(...meta.pivotThree);pivot.quaternion.identity();pivot.scale.set(1,1,1);scene.add(pivot);pivot.updateMatrixWorld(true);pivot.attach(key);
  const glow=[];key.traverse(object=>{if(!object.isMesh)return;const materials=[object.material].flat().map(material=>material.clone());object.material=Array.isArray(object.material)?materials:materials[0];for(const material of materials)if(material.emissive){material.emissive.set(0xd69842);material.emissiveIntensity=0;glow.push(material);}});
  // Fit authored geometry in camera space; the large environment floor must
  // not shrink the complete character/instrument to a thumbnail.
  camera.updateMatrixWorld(true);camera.matrixWorldInverse.copy(camera.matrixWorld).invert();
  const framed=new T.Box3();const corner=new T.Vector3();
  scene.traverse(object=>{
    if(!object.isMesh||object.name.startsWith('ENV-'))return;
    object.geometry.computeBoundingBox();const box=object.geometry.boundingBox;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
      corner.set(x,y,z).applyMatrix4(object.matrixWorld).applyMatrix4(camera.matrixWorldInverse);framed.expandByPoint(corner);
    }
  });
  const center=framed.getCenter(new T.Vector3()),size=framed.getSize(new T.Vector3());
  camera.position.add(new T.Vector3(center.x,center.y,0).applyQuaternion(camera.quaternion));camera.updateMatrixWorld(true);
  let amount=0,lastWidth=0,lastHeight=0;
  function thetaAt(q) {
    const points=meta.trajectory;
    for(let i=1;i<points.length;i++)if(q<=points[i].q){const a=points[i-1],b=points[i],u=Math.max(0,Math.min(1,(q-a.q)/(b.q-a.q)));return a.theta+(b.theta-a.theta)*u;}
    return points.at(-1).theta;
  }
  function setPose(next) {
    amount=Math.max(0,Math.min(1,next));const c=meta.contactFraction;
    const contact=amount<=c?amount/c:1-(amount-c)/(1-c),down=amount<=c?0:(amount-c)/(1-c);
    for(const object of parts){object.morphTargetInfluences[object.morphTargetDictionary[meta.morphNames.contact]]=contact;object.morphTargetInfluences[object.morphTargetDictionary[meta.morphNames.down]]=down;}
    pivot.rotation.x=thetaAt(meta.q0+amount*(meta.qDown-meta.q0));
    for(const material of glow)material.emissiveIntensity=down*.35;
    canvas.dataset.amount=amount.toFixed(6);canvas.dataset.contactWeight=contact.toFixed(6);canvas.dataset.downWeight=down.toFixed(6);canvas.dataset.keyTheta=pivot.rotation.x.toFixed(9);
  }
  function render(){
    const width=canvas.clientWidth,height=canvas.clientHeight;
    if(width!==lastWidth||height!==lastHeight){lastWidth=width;lastHeight=height;renderer.setSize(width,height,false);const aspect=width/height,half=.56*Math.max(size.y,size.x/aspect);camera.left=-half*aspect;camera.right=half*aspect;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();}
    renderer.render(scene,camera);canvas.dataset.renderedAmount=amount.toFixed(6);canvas.dataset.lastRenderedMs=performance.now().toFixed(3);canvas.dataset.drawCalls=String(renderer.info.render.calls);
  }
  setPose(0);render();canvas.dataset.ready='true';canvas.dataset.morphParts=String(parts.length);
  return {setPose,render,meta,destroy(){scene.traverse(object=>{object.geometry?.dispose();for(const material of[object.material].flat().filter(Boolean))material.dispose();});renderer.dispose();}};
}
