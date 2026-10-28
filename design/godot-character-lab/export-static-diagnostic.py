"""Native-only Godot migration preflight on the unaccepted C8 source.
Bake linked diffuse colors to per-point data; keep whole cat/instrument together.
Not a replacement character, motion, realtime-material fidelity or production gate.
"""
import bpy,numpy as np,sys,json,hashlib,struct,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/godot-cat-static';OUT.mkdir(exist_ok=True)
SRC=ROOT/'artifacts/character-fidelity-c8-r2-color/miao-c8-reference-hold.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 source_sha=sha(SRC);bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();s.cycles.samples=1;s.render.engine='CYCLES'
 try:
  pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
  for d in pref.devices:d.use=d.type=='METAL'
  s.cycles.device='GPU'
 except Exception:s.cycles.device='CPU'
 original=list(s.objects);export=[];bakes=[]
 for o in original:
  if o.type=='CAMERA':export.append(o);continue
  if o.type not in {'MESH','CURVE'} or o.hide_render or o.name.startswith(('Studio /','Authoring /','Reference /','D0 /')):continue
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);new=bpy.data.objects.new('Diagnostic / '+o.name,me);s.collection.objects.link(new);new.matrix_world=o.matrix_world.copy();o.hide_render=True;o.hide_set(True);export.append(new)
  # A procedural color must be baked; retain optical transmission as a separate
  # loss-test case, rather than falsely baking a clear cornea into black diffuse.
  first=me.materials[0] if me.materials else None;bs=first.node_tree.nodes.get('Principled BSDF') if first else None
  linked=any(m and m.node_tree and any(n.type=='BSDF_PRINCIPLED' and n.inputs['Base Color'].is_linked for n in m.node_tree.nodes) for m in me.materials)
  transparent=bool(bs and bs.inputs['Transmission Weight'].default_value>.5)
  if linked and not transparent:
   for x in s.objects:x.select_set(False)
   new.hide_set(False);new.select_set(True);bpy.context.view_layer.objects.active=new
   colors=me.color_attributes.new(name='MigrationBakeCorner',type='FLOAT_COLOR',domain='CORNER');me.color_attributes.active_color=colors;me.color_attributes.render_color_index=list(me.color_attributes).index(colors)
   bake_props=bpy.ops.object.bake.get_rna_type().properties.keys();kw={'type':'DIFFUSE','pass_filter':{'COLOR'}}
   if 'target' in bake_props:kw['target']='VERTEX_COLORS'
   s.render.bake.target='VERTEX_COLORS';t=time.time();bpy.ops.object.bake(**kw)
   rgba=np.empty(len(colors.data)*4,np.float32);colors.data.foreach_get('color',rgba);rgba=rgba.reshape(-1,4);indices=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',indices);summed=np.zeros((len(me.vertices),4),np.float32);np.add.at(summed,indices,rgba);counts=np.bincount(indices,minlength=len(me.vertices));point=summed/np.maximum(counts[:,None],1);assert np.isfinite(point).all()
   me.color_attributes.remove(colors);color=me.color_attributes.new(name='MiaoMigrationAlbedo',type='FLOAT_COLOR',domain='POINT');color.data.foreach_set('color',point.astype(np.float32).ravel());me.color_attributes.active_color=color;me.color_attributes.render_color_index=list(me.color_attributes).index(color)
   material=bpy.data.materials.new('Diagnostic / point albedo / '+o.name);shader=material.node_tree.nodes.get('Principled BSDF');vertex=material.node_tree.nodes.new('ShaderNodeVertexColor');vertex.layer_name=color.name;material.node_tree.links.new(vertex.outputs['Color'],shader.inputs['Base Color'])
   shader.inputs['Roughness'].default_value=float(bs.inputs['Roughness'].default_value) if bs else .6
   shader.inputs['Metallic'].default_value=float(bs.inputs['Metallic'].default_value) if bs else 0
   me.materials.clear();me.materials.append(material)
   for polygon in me.polygons:polygon.material_index=0
   bakes.append({'object':o.name,'vertices':len(me.vertices),'seconds':time.time()-t,'rgb_min':point[:,:3].min(0).tolist(),'rgb_max':point[:,:3].max(0).tolist(),'source_corner_samples':len(indices),'point_colors':len(point)})
  # BindUV is groom-only; no generated pigment/wood shader requires a UV here.
  for uv in list(me.uv_layers):me.uv_layers.remove(uv)
  for attr in list(me.color_attributes):
   if attr.name!='MiaoMigrationAlbedo' and linked and not transparent:me.color_attributes.remove(attr)
 bpy.context.view_layer.update()
 for o in s.objects:o.select_set(False)
 for o in export:o.hide_set(False);o.select_set(True)
 path=OUT/'whole-cat-diagnostic.glb';params={'filepath':str(path),'export_format':'GLB','use_selection':True,'export_cameras':True,'export_lights':False,'export_animations':False,'export_apply':False,'export_yup':True,'export_attributes':False}
 valid=bpy.ops.export_scene.gltf.get_rna_type().properties.keys();params={k:v for k,v in params.items() if k in valid};assert params.get('export_cameras') and params.get('use_selection');bpy.ops.export_scene.gltf(**params)
 data=path.read_bytes();length,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a;gltf=json.loads(data[20:20+length]);positions=sum(gltf['accessors'][p['attributes']['POSITION']]['count'] for m in gltf.get('meshes',[]) for p in m['primitives']);triangles=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf.get('meshes',[]) for p in m['primitives'] if 'indices' in p)
 result={'input_sha256':source_sha,'input_unchanged':sha(SRC)==source_sha,'bakes':bakes,'glb_bytes':len(data),'glb_sha256':sha(path),'gltf_meshes':len(gltf.get('meshes',[])),'gltf_cameras':gltf.get('cameras',[]),'exported_position_accessors_total':positions,'exported_triangles':triangles,'bake_operator_properties':list(bpy.ops.object.bake.get_rna_type().properties.keys()),'limits':['Unaccepted C8 migration diagnostic only, not current refined art.','Native groom excluded; UV maps removed after point-color baking.','No rig/animation; native camera retained.','Corneal transmission and realtime lights still require actual Godot inspection.','Not production, browser, audio/export or performance acceptance.']};assert result['input_unchanged'];(OUT/'export-receipt.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'gltf-json.json').write_text(json.dumps(gltf,indent=2)+'\n');print('RESULT '+json.dumps(result))
main()
