"""C14C: static original-coat/groom diagnostic only; no sculpt or material edits.
Read-only source, full native all-root UV/nearest/rest checks before any render.
"""
import argparse,ast,bpy,hashlib,json,sys,time,traceback
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--input',default='artifacts/character-head-c14/miao-c14-compact-head.blend');p.add_argument('--out',default='artifacts/character-head-c14-color');p.add_argument('--size',type=int,default=1024);p.add_argument('--samples',type=int,default=32);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
src=(ROOT/a.input).resolve();out=(ROOT/a.out).resolve();out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
upstream=ROOT/'design/character-sculpt-v2/d0-groom-binding.py'
# Reuse only pure helper definitions. The upstream script has an executable main;
# importing it would rebind another scene. No top-level code/arguments are run.
tree=ast.parse(upstream.read_text());wanted={'stats','digest','positions','world','rest_hash','native_uv_validity'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted],type_ignores=[]),str(upstream),'exec'))
r={'stage':'C14C-head-only-static-material-diagnostic','status':'started','input':str(src.relative_to(ROOT)),'input_sha256':sha(src),'source_sha256':sha(__file__),'helper_source_sha256':sha(upstream),'helper_functions':sorted(wanted),'blender':bpy.app.version_string,'renders':[]}
def save(): (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
def stage(v):r['status']=v;save();print('C14C_STAGE '+v,flush=True)
def rest_pair(body,hair):return {'body_raw':rest_hash(body),'body_eval':rest_hash(body,True),'hair_raw':rest_hash(hair),'hair_eval':rest_hash(hair,True)}
def uv_hashes(body,hair):
 ret={}
 for uv in body.data.uv_layers:
  v=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',v);ret[uv.name]=digest(v)
 at=hair.data.attributes['surface_uv_coordinate'];v=np.empty(len(at.data)*2,np.float32);at.data.foreach_get('vector',v);ret['hair_root_uv']=digest(v);return ret

def sample_current_uv_surface(body,hair):
 group=bpy.data.node_groups.new('C14C / temporary UV surface target','GeometryNodeTree');group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=group.nodes;l=group.links
 ni=n.new('NodeGroupInput');no=n.new('NodeGroupOutput');info=n.new('GeometryNodeObjectInfo');info.inputs['Object'].default_value=body
 uv=n.new('GeometryNodeInputNamedAttribute');uv.data_type='FLOAT_VECTOR';uv.inputs['Name'].default_value='BindUV';ruv=n.new('GeometryNodeInputNamedAttribute');ruv.data_type='FLOAT_VECTOR';ruv.inputs['Name'].default_value='surface_uv_coordinate'
 pos=n.new('GeometryNodeInputPosition');sample=n.new('GeometryNodeSampleUVSurface');sample.data_type='FLOAT_VECTOR';l.new(info.outputs['Geometry'],sample.inputs['Mesh']);l.new(uv.outputs['Attribute'],sample.inputs['Source UV Map']);l.new(ruv.outputs['Attribute'],sample.inputs['Sample UV']);l.new(pos.outputs['Position'],sample.inputs['Value'])
 store=n.new('GeometryNodeStoreNamedAttribute');store.domain='CURVE';store.data_type='FLOAT_VECTOR';store.inputs['Name'].default_value='c14c_current_uv_surface';l.new(ni.outputs['Geometry'],store.inputs['Geometry']);l.new(sample.outputs['Value'],store.inputs['Value']);l.new(store.outputs['Geometry'],no.inputs['Geometry'])
 mod=hair.modifiers.new('C14C / temporary UV target','NODES');mod.node_group=group;bpy.context.view_layer.update();ev=hair.evaluated_get(bpy.context.evaluated_depsgraph_get());at=ev.data.attributes['c14c_current_uv_surface'];v=np.empty(len(at.data)*3,np.float32);at.data.foreach_get('vector',v);v=v.reshape(-1,3).copy();hair.modifiers.remove(mod);bpy.data.node_groups.remove(group);bpy.context.view_layer.update();return world(body,v)

def lights_snapshot(s):
 return [{'name':o.name,'matrix':[list(row) for row in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':getattr(o.data,'size',None),'hide_render':o.hide_render} for o in s.objects if o.type=='LIGHT']
def main():
 # Compare retained custom rest / UV / underlying point data with original C8 input.
 ref=ROOT/'artifacts/character-fidelity-c8-r2-color/miao-c8-reference-hold.blend';refsha=sha(ref);bpy.ops.wm.open_mainfile(filepath=str(ref));b=bpy.data.objects['Miao / continuous pear and rounded-square face'];h=bpy.data.objects['Miao / native short plush'];reference_rest=rest_pair(b,h);reference_uv=uv_hashes(b,h);reference_hair=digest(positions(h));reference_body=digest(positions(b));r['original_c8_sha256']=refsha
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;b=bpy.data.objects['Miao / continuous pear and rounded-square face'];h=bpy.data.objects['Miao / native short plush'];basebody=positions(b,True);basehair=positions(h,True);original_rest=rest_pair(b,h);original_uv=uv_hashes(b,h);original_lights=lights_snapshot(s);origcam=s.camera;original_cam_matrix=origcam.matrix_world.copy();original_cam_lens=origcam.data.lens;original_cam_type=origcam.data.type;original_cam_scale=origcam.data.ortho_scale
 assert len(b.data.vertices)==609383 and len(h.data.curves)==180000 and len(h.data.position_data)==720000
 assert h.data.surface==b and h.data.surface_uv_map=='BindUV' and b.add_rest_position_attribute
 assert b.matrix_world==h.matrix_world,'UV target object info frame must match hair/body'
 assert reference_rest==original_rest,'Custom rest changed from C8';assert reference_uv==original_uv,'UV binding changed from C8';assert digest(positions(h))==reference_hair;assert digest(positions(b))==reference_body
 r['binding']={'curves':len(h.data.curves),'points':len(h.data.position_data),'surface':h.data.surface.name,'surface_uv_map':h.data.surface_uv_map,'rest_hashes':original_rest,'C8_custom_rest_and_binding_uv_unchanged':True,'body_and_hair_raw_positions_unchanged_from_C8':True,'hair_modifiers':[{'name':m.name,'type':m.type,'node_types':[n.bl_idname for n in m.node_group.nodes] if m.type=='NODES' else []} for m in h.modifiers]};stage('raw-rest-and-binding-preserved')
 valid=native_uv_validity(b,h);r['binding']['official_all_root_uv_validity']={'count':len(valid),'valid':int(valid.sum()),'invalid':np.flatnonzero(~valid).tolist()};save();assert len(valid)==180000 and valid.all(),'Native UV validity failed, stop before coat render'
 roots=world(h,positions(h,True))[::4];targets=sample_current_uv_surface(b,h);uv_err=np.linalg.norm(roots-targets,axis=1);r['binding']['all_root_to_current_uv_surface']=stats(uv_err);stage('all-root-corresponding-UV-surface-measured')
 dg=bpy.context.evaluated_depsgraph_get();bvh=BVHTree.FromObject(b,dg);iv=b.matrix_world.inverted();nearest=np.empty(len(roots),np.float64)
 for i,q in enumerate(roots):
  hit,n,face,d=bvh.find_nearest(iv@Vector(q));assert hit is not None;nearest[i]=(Vector(q)-b.matrix_world@hit).length
 r['binding']['all_root_to_current_nearest_surface']=stats(nearest);head=targets[:,2]>=2.5;r['binding']['head_root_count']=int(head.sum());r['binding']['head_root_to_UV_surface']=stats(uv_err[head]);r['binding']['head_root_to_nearest_surface']=stats(nearest[head]);save()
 assert uv_err.max()<1e-4 and nearest.max()<1e-4,'Groom detached after C14 head field; preserve breakpoint, no fake follow'
 assert rest_pair(b,h)==original_rest and uv_hashes(b,h)==original_uv
 h.hide_render=False;bpy.context.view_layer.update();assert np.array_equal(basebody,positions(b,True)) and np.array_equal(basehair,positions(h,True))
 r['materials_unchanged']=[{'object':o.name,'materials':[m.name if m else None for m in o.data.materials]} for o in s.objects if o.type in {'MESH','CURVE','CURVES'} and (o==b or o==h or o.name.startswith(('C6 /','C7 / clear','Face /')))]
 s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.samples=a.samples;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;s.render.filepath='//renders/c14-color-front.png'
 bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-c14c-head-color.blend'),compress=True);stage('binding-valid-original-coat-rendering')
 def render(name,camera):
  s.camera=camera;s.render.filepath=str(out/(name+'.png'));start=time.time();bpy.ops.render.render(write_still=True);r['renders'].append({'name':name,'seconds':time.time()-start,'sha256':sha(s.render.filepath),'camera_matrix':[list(row) for row in camera.matrix_world],'lens':camera.data.lens,'type':camera.data.type,'ortho_scale':camera.data.ortho_scale});save()
 render('color-front',origcam)
 diag=origcam.copy();diag.data=origcam.data.copy();diag.name='C14C / owned diagnostic camera';s.collection.objects.link(diag);diag.location=(6,-9,3.9);diag.rotation_euler=(Vector((.09881,0,1.609))-diag.location).to_track_quat('-Z','Y').to_euler();render('color-three-quarter',diag)
 diag.data.type='PERSP';diag.data.lens=90;diag.location=(.12,-5.5,3.08);diag.rotation_euler=(Vector((.04,0,2.97))-diag.location).to_track_quat('-Z','Y').to_euler();render('color-head-front',diag)
 diag.location=(3.25,-4.4,3.08);diag.rotation_euler=(Vector((.02,0,2.96))-diag.location).to_track_quat('-Z','Y').to_euler();render('color-head-three-quarter',diag)
 s.camera=origcam;assert lights_snapshot(s)==original_lights and origcam.matrix_world==original_cam_matrix and origcam.data.type==original_cam_type and origcam.data.lens==original_cam_lens and origcam.data.ortho_scale==original_cam_scale
 assert np.array_equal(basebody,positions(b,True)) and np.array_equal(basehair,positions(h,True)) and rest_pair(b,h)==original_rest and uv_hashes(b,h)==original_uv
 assert sha(src)==r['input_sha256'] and sha(ref)==refsha;r['source_native_unchanged']=True;r['geometry_and_original_camera_lights_unchanged']=True;r['native_output_sha256']=sha(out/'miao-c14c-head-color.blend');r['limits']=['Head-only static C diagnostic; no full character approval.','B-known ear grooves and barrel side remain P1; whole-character paw P0 remain.','No geometry/material/light edit; original optical stack and eyecards tested as-is.','All-root static attachment does not prove motion, eyelid closure, retopo or another mesh.','No animation/Godot/web/Cloudflare/API/commit/push.'];stage('rendered-awaiting-builder-view-and-three-independent-C-reviews');print('RESULT '+json.dumps(r),flush=True)
try:main()
except Exception as e:
 r['status']='failed-stop-before-unverified-follow';r['error']=repr(e);r['traceback']=traceback.format_exc();save();print(r['traceback'],flush=True);raise
