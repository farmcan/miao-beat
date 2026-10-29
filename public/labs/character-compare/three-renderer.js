import {Scene,Color,WebGLRenderer,HemisphereLight,DirectionalLight,PlaneGeometry,Mesh,MeshStandardMaterial,PCFShadowMap,SRGBColorSpace,NoToneMapping,Vector3,GLTFLoader,OrbitControls} from './vendor/three-runtime.mjs';

const TARGETS=['Pluck','FretLow','FretHigh','HeadTilt','Lift'];
const VIEWS={whole:{target:[.1,1.61,0],zoom:1},hands:{target:[.3,1.7,1],zoom:1.25},face:{target:[.07,3.03,0],zoom:2.7}};

export function createThreeCharacter(canvas,onStatus=()=>{}){
  let renderer,root,camera,controls,lastWidth=0,lastHeight=0,ready=false;
  const morphs=[],scene=new Scene();scene.background=new Color(0xf4f0e5);
  const hemi=new HemisphereLight(0xfffaf0,0x716d63,1.25);scene.add(hemi);
  const key=new DirectionalLight(0xfff6e7,2.4);key.position.set(-3,6,7);key.castShadow=true;key.shadow.mapSize.set(1024,1024);key.shadow.camera.left=-4;key.shadow.camera.right=4;key.shadow.camera.top=5;key.shadow.camera.bottom=-2;key.shadow.normalBias=.025;key.shadow.bias=-.0002;scene.add(key);
  const fill=new DirectionalLight(0xddeaff,.65);fill.position.set(4,3,5);scene.add(fill);
  const floor=new Mesh(new PlaneGeometry(200,200),new MeshStandardMaterial({color:0xf0ece1,roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.y=-.014;floor.receiveShadow=true;scene.add(floor);
  const promise=(async()=>{
    renderer=new WebGLRenderer({canvas,antialias:true,alpha:false,preserveDrawingBuffer:true});
    renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));renderer.outputColorSpace=SRGBColorSpace;renderer.toneMapping=NoToneMapping;renderer.shadowMap.enabled=true;renderer.shadowMap.type=PCFShadowMap;
    const gltf=await new GLTFLoader().loadAsync(new URL('./model/miao-playable.glb',import.meta.url).href);
    root=gltf.scene;scene.add(root);root.updateMatrixWorld(true);camera=gltf.cameras[0];if(!camera?.isOrthographicCamera)throw Error('导出相机不匹配');scene.attach(camera);
    root.traverse(object=>{if(!object.isMesh)return;object.castShadow=true;object.receiveShadow=true;if(object.morphTargetDictionary){for(const name of TARGETS)if(object.morphTargetDictionary[name]===undefined)throw Error('模型缺少动作 '+name);morphs.push(object);}});
    if(!morphs.length)throw Error('模型没有真实形变');
    controls=new OrbitControls(camera,canvas);controls.enableDamping=true;controls.enablePan=false;controls.minZoom=.7;controls.maxZoom=3.5;controls.minPolarAngle=.25;controls.maxPolarAngle=Math.PI/2;ready=true;setView('whole');canvas.dataset.renderer='three-webgl';canvas.dataset.morphMeshes=String(morphs.length);canvas.dataset.ready='true';onStatus('可以弹了 · 可拖动转视角');return true;
  })().catch(error=>{canvas.dataset.error=error.message;onStatus('3D未加载：'+error.message);return false;});
  function resize(){const width=Math.max(1,canvas.clientWidth),height=Math.max(1,canvas.clientHeight);if(width===lastWidth&&height===lastHeight)return;lastWidth=width;lastHeight=height;renderer.setSize(width,height,false);const span=2.10013825;camera.left=-span*width/height;camera.right=span*width/height;camera.top=span;camera.bottom=-span;camera.updateProjectionMatrix();}
  function setView(name){if(!ready)return;const view=VIEWS[name]||VIEWS.whole;const target=new Vector3(...view.target);camera.position.copy(target).add(new Vector3(0,.986276,12.00859));camera.lookAt(target);camera.zoom=view.zoom;camera.updateProjectionMatrix();controls.target.copy(target);controls.update();}
  return{ready:promise,
    setPose(weights){if(!ready)return;for(const object of morphs)for(let i=0;i<TARGETS.length;i++)object.morphTargetInfluences[object.morphTargetDictionary[TARGETS[i]]]=weights[i];canvas.dataset.pose=weights.map(n=>n.toFixed(3)).join(',');},
    setView,
    setOrbit(degrees){if(root)root.rotation.y=degrees*Math.PI/180;},
    render(){if(!ready||canvas.closest('[hidden]'))return;resize();controls.update();renderer.render(scene,camera);},
    destroy(){controls?.dispose();renderer?.dispose();}
  };
}
