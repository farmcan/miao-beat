"""C20 -> shared browser/Godot research GLB. Geometry deformation, not final art.
Run Blender -b --factory-startup --python-exit-code 1 -P this-file.
"""
import bpy, numpy as np, json, hashlib, struct, time, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'artifacts/character-eye-wet-iris-c20/miao-c20-wet-iris.blend'
OUT=ROOT/'public/labs/character-compare/model'; OUT.mkdir(parents=True,exist_ok=True)
EVID=ROOT/'artifacts/interactive-compare'; EVID.mkdir(parents=True,exist_ok=True)
TARGETS=['Pluck','FretLow','FretHigh','HeadTilt','Lift']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
def rotate_y(p,pivot,angle):
 q=p-np.array(pivot); c=math.cos(angle); s=math.sin(angle)
 return np.column_stack((c*q[:,0]+s*q[:,2],q[:,1],-s*q[:,0]+c*q[:,2]))+pivot
def main():
 started=time.time();source_sha=sha(SRC);assert source_sha=='5f66fb066a49dff3d856e70a70d374e58eb1b1cca76fc42404d2b9246c2116c2','Frozen C20 mismatch';bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene
 scene.render.engine='CYCLES';scene.cycles.samples=1;scene.cycles.device='CPU'
 # No paid/external render services. Bake the existing procedural color locally.
 try:
  pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
  for d in pref.devices:d.use=d.type=='METAL'
  scene.cycles.device='GPU' if any(d.use for d in pref.devices) else 'CPU'
 except Exception:pass
 original=list(scene.objects);export=[];records=[];morphs=[];bakes=[]
 for o in original:
  if o.type=='CURVE':
   o.data.resolution_u=min(o.data.resolution_u,4);o.data.render_resolution_u=4;o.data.bevel_resolution=min(o.data.bevel_resolution,1)
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for o in original:
  if o.type=='CAMERA':export.append(o);continue
  if o.type not in {'MESH','CURVE'} or o.hide_render or o.name.startswith(('Studio /','Authoring /','Reference /','D0 /')):continue
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
  new=bpy.data.objects.new(o.name,me);scene.collection.objects.link(new);me.transform(o.matrix_world)
  o.hide_render=True;o.hide_set(True);export.append(new)
  for ob in scene.objects:ob.select_set(False)
  new.select_set(True);bpy.context.view_layer.objects.active=new
  before=len(me.vertices)
  if o.name.startswith('Miao / continuous'):
   mod=new.modifiers.new('Research LOD 12 percent, not art refinement','DECIMATE');mod.ratio=.12;mod.use_collapse_triangulate=True
   bpy.ops.object.modifier_apply(modifier=mod.name);me=new.data
  records.append({'object':o.name,'vertices_before':before,'vertices_after':len(me.vertices),'triangles':sum(len(p.vertices)-2 for p in me.polygons)})
  for p in me.polygons:p.use_smooth=True
  linked=any(m and m.node_tree and any(n.type=='BSDF_PRINCIPLED' and n.inputs['Base Color'].is_linked for n in m.node_tree.nodes) for m in me.materials)
  bs=next((n for m in me.materials if m and m.node_tree for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if linked:
   col=me.color_attributes.new(name='BakeCorner',type='FLOAT_COLOR',domain='CORNER');me.color_attributes.active_color=col;me.color_attributes.render_color_index=list(me.color_attributes).index(col)
   scene.render.bake.target='VERTEX_COLORS';bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},target='VERTEX_COLORS')
   rgba=np.empty(len(col.data)*4,np.float32);col.data.foreach_get('color',rgba);rgba=rgba.reshape(-1,4)
   inds=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',inds);summed=np.zeros((len(me.vertices),4),np.float32);np.add.at(summed,inds,rgba)
   point=summed/np.maximum(np.bincount(inds,minlength=len(me.vertices))[:,None],1);assert np.isfinite(point).all()
   # Keep exactly one exported COLOR_0 attribute; glTF uses linear vertex colors.
   for attr in list(me.color_attributes):me.color_attributes.remove(attr)
   col=me.color_attributes.new(name='MiaoAlbedo',type='FLOAT_COLOR',domain='POINT');col.data.foreach_set('color',point.astype(np.float32).ravel());me.color_attributes.active_color=col;me.color_attributes.render_color_index=0
   mat=bpy.data.materials.new('Playable / '+o.name);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');vc=mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name=col.name;mat.node_tree.links.new(vc.outputs['Color'],shader.inputs['Base Color'])
   for socket in ['Roughness','Metallic','Coat Weight','Coat Roughness','IOR','Specular IOR Level']:
    if bs and socket in bs.inputs and socket in shader.inputs:shader.inputs[socket].default_value=bs.inputs[socket].default_value
   # C20 wet convex iris is OPAQUE with clearcoat, not the old C7 transmitting cornea.
   shader.inputs['Transmission Weight'].default_value=0
   me.materials.clear();me.materials.append(mat)
   for p in me.polygons:p.material_index=0
   bakes.append({'object':o.name,'point_colors':len(point),'rgb_min':point[:,:3].min(0).tolist(),'rgb_max':point[:,:3].max(0).tolist()})
  for uv in list(me.uv_layers):me.uv_layers.remove(uv)
  # Derive targets only after the topology modifier is applied.
  is_body=o.name.startswith('Miao / continuous')
  is_face=o.name.startswith(('Face /','C6 /','C7 /','Miao / fine whisker'))
  if is_body or is_face:
   co=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',co);co=co.reshape(-1,3)
   new.shape_key_add(name='Basis');deltas={name:np.zeros_like(co) for name in TARGETS}
   if is_body:
    # Viewer-left picking paw, connected forearm fades to zero before shoulder.
    # front mask excludes the root torso behind the guitar.
    x,y,z=co.T
    pick=(1-smooth(-.62,-.27,x))*smooth(-1.60,-1.20,x)*(1-smooth(-.92,-.58,y))*smooth(1.12,1.40,z)*(1-smooth(2.12,2.38,z))
    moved=rotate_y(co,[-1.03,-.91,1.98],-.23)
    deltas['Pluck']=(moved-co)*pick[:,None]
    deltas['Lift'][:,1]=-.06*pick
    fret=smooth(.63,.99,x)*(1-smooth(-.93,-.68,y))*smooth(1.38,1.63,z)*(1-smooth(2.29,2.45,z))
    u=np.array([1.0169595357706245,0,.40048756408789304]);u/=np.linalg.norm(u)
    deltas['FretLow']=fret[:,None]*u[None,:]*-.105
    deltas['FretHigh']=fret[:,None]*u[None,:]*.105
    head=smooth(2.49,2.70,z)
   else:head=np.ones(len(co),np.float32)
   headmoved=rotate_y(co,[.06,0,2.62],.052)
   deltas['HeadTilt']=(headmoved-co)*head[:,None]
   for name in TARGETS:
    k=new.shape_key_add(name=name);k.slider_min=-1 if name=='Pluck' else 0;k.slider_max=1;k.data.foreach_set('co',(co+deltas[name]).astype(np.float32).ravel())
   morphs.append({'object':o.name,'vertices':len(co),'targets':{n:{'nonzero_vertices':int(np.count_nonzero(np.linalg.norm(d,axis=1)>1e-7)),'max_displacement':float(np.linalg.norm(d,axis=1).max())} for n,d in deltas.items()}})
  print('CONVERTED '+o.name+' '+str(len(me.vertices)),flush=True)
 # Exclude unsupported native hair entirely, not just from GLB selection.
 for o in original:
  if o.type=='CURVES':o.hide_render=True;o.hide_set(True)
 for o in scene.objects:o.select_set(False)
 for o in export:o.hide_set(False);o.select_set(True)
 path=OUT/'miao-playable.glb'
 params={'filepath':str(path),'export_format':'GLB','use_selection':True,'export_cameras':True,'export_lights':False,'export_animations':False,'export_apply':False,'export_yup':True,'export_attributes':False,'export_morph':True,'export_morph_normal':False,'export_morph_tangent':False,'export_materials':'EXPORT','export_all_vertex_colors':False}
 valid=bpy.ops.export_scene.gltf.get_rna_type().properties.keys();params={k:v for k,v in params.items() if k in valid};bpy.ops.export_scene.gltf(**params)
 raw=path.read_bytes();size,typ=struct.unpack_from('<II',raw,12);gltf=json.loads(raw[20:20+size]);assert len(raw)<20_000_000,len(raw)
 exported_targets=[{'name':m.get('name'),'targetNames':m.get('extras',{}).get('targetNames'),'primitive_target_counts':[len(p.get('targets',[])) for p in m['primitives']]} for m in gltf['meshes'] if any(p.get('targets') for p in m['primitives'])]
 assert exported_targets and all(m['targetNames']==TARGETS for m in exported_targets),exported_targets
 report={'stage':'interactive-research-LOD-not-art-pass','source':str(SRC.relative_to(ROOT)),'source_sha256':source_sha,'source_unchanged':sha(SRC)==source_sha,'blender':bpy.app.version_string,'script_sha256':sha(__file__),'glb_sha256':sha(path),'bytes':len(raw),'targetNames':TARGETS,'geometry':records,'morphs':morphs,'exported_morphs':exported_targets,'bakes':bakes,'triangles':sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives'] if 'indices'in p),'license':{'source_art':'Miao project original scene; no third-party stock model imported','exporter':'Project original conversion script, follows local vertex-color bake workflow','runtime_attribution':'Three/Godot runtime licenses must be maintained separately by renderer adapters'},'limits':['Research LOD 12 percent is an export budget conversion, not accepted model refinement.','Native hair excluded; procedural diffuse color baked to POINT COLOR_0, surface shader not fully equivalent.','Paws/head use localized continuous-skin morph deformations, no collision solver, finger rig or physical string validation.','Old silhouette/paw/fur P0 visual issues remain; not production character art acceptance.','GLB contains geometry and targets only, no audio or authored action clip. Browser/Godot runtime acceptance is separate.'],'seconds_before_renders':time.time()-started}
 assert report['source_unchanged'];(OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');(EVID/'gltf-json.json').write_text(json.dumps(gltf,indent=2)+'\n')
 # Saved copy only; frozen source is never overwritten.
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(EVID/'miao-playable-study.blend'),compress=True)
 scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=768;scene.render.resolution_y=768;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'
 frames=[('start',[0,0,0,0,0]),('contact',[1,.45,0,.55,0]),('end',[0,0,0,0,0])]
 for label,weights in frames:
  for o in export:
   if o.type=='MESH' and o.data.shape_keys:
    for name,w in zip(TARGETS,weights):o.data.shape_keys.key_blocks[name].value=w
  bpy.context.view_layer.update();scene.render.filepath=str(EVID/(label+'.png'));bpy.ops.render.render(write_still=True)
 report['render_evidence']=[{'file':'artifacts/interactive-compare/'+label+'.png','weights':weights,'sha256':sha(EVID/(label+'.png'))} for label,weights in frames]
 report['seconds']=time.time()-started;(OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+json.dumps({'bytes':len(raw),'triangles':report['triangles'],'morph_meshes':len(exported_targets),'seconds':report['seconds'],'source_unchanged':report['source_unchanged']}),flush=True)
main()
