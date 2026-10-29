"""Exact source-identity head/hand assembly for a complete gray review scene.
No nearest-point matching. New hand topology and every hand vertex stay intact.
This assembler does not claim the input hand's contact or whole-character pass.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
P=argparse.ArgumentParser();P.add_argument('--hand-blend',required=True);P.add_argument('--out',required=True);P.add_argument('--render',action='store_true');P.add_argument('--size',type=int,default=768);P.add_argument('--samples',type=int,default=16)
a=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
if (out/'receipt.json').exists():raise RuntimeError('Preserve frozen output; use a fresh directory')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NAME='Miao / continuous pear and rounded-square face'
paths={'base':ROOT/'artifacts/character-fidelity-c8-r2-color/miao-c8-reference-hold.blend','head':ROOT/'artifacts/character-eye-wet-iris-c20/miao-c20-wet-iris.blend','hand':ROOT/a.hand_blend}
checks={k:sha(p) for k,p in paths.items()};records={};coords={}
def snap(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());ar=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',ar);v=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',v);n=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('loop_total',n);r={'vertices':len(me.vertices),'faces':len(me.polygons),'ordered_topology_sha256':hashlib.sha256(v.tobytes()+n.tobytes()).hexdigest(),'matrix_world':list(map(list,ob.matrix_world))};ev.to_mesh_clear();return ar.reshape(-1,3).copy(),r
for tag in ['base','head']:
 bpy.ops.wm.open_mainfile(filepath=str(paths[tag]));coords[tag],records[tag]=snap(bpy.data.objects[NAME])
assert records['base']['ordered_topology_sha256']==records['head']['ordered_topology_sha256']
assert records['base']['matrix_world']==records['head']['matrix_world']
features=[o.name for o in bpy.context.scene.objects if o.name.startswith(('Face /','C6 /','C7 /'))]
# Library-loaded objects are not linked/evaluated: their matrix_world may still
# be identity although location/rotation are populated. Snapshot the evaluated
# donor scene before opening the hand file; never infer world transforms from
# the subsequently unlinked library objects (C47's lost optical-light cause).
bpy.context.view_layer.update()
feature_world={name:bpy.data.objects[name].matrix_world.copy() for name in features}
feature_hidden={name:bpy.data.objects[name].hide_render for name in features}
transform_channels=('location','rotation_mode','rotation_euler','rotation_quaternion','rotation_axis_angle','scale','delta_location','delta_rotation_euler','delta_rotation_quaternion','delta_scale')
assert all(bpy.data.objects[name].parent is None and not bpy.data.objects[name].constraints for name in features),'This assembler requires unparented, unconstrained source face/light objects'
feature_channels={name:{key:getattr(bpy.data.objects[name],key).copy() if hasattr(getattr(bpy.data.objects[name],key),'copy') else tuple(getattr(bpy.data.objects[name],key)) if key=='rotation_axis_angle' else getattr(bpy.data.objects[name],key) for key in transform_channels} for name in features}
bpy.ops.wm.open_mainfile(filepath=str(paths['hand']));s=bpy.context.scene;body=bpy.data.objects[NAME]
assert not body.modifiers and not body.data.shape_keys,'Assembly expects saved evaluated hand mesh'
assert list(map(list,body.matrix_world))==records['base']['matrix_world']
initial=np.empty(len(body.data.vertices)*3,np.float32);body.data.vertices.foreach_get('co',initial);initial=initial.reshape(-1,3)
attr=body.data.attributes['C23 source vertex id'];ids=np.empty(len(attr.data),np.int32);attr.data.foreach_get('value',ids);keep=ids>0
assert ids[keep].max()<=len(coords['base']) and len(np.unique(ids[keep]))==int(keep.sum())
assert np.array_equal(initial[keep],coords['base'][ids[keep]-1]),'Retained body no longer matches declared base; do not silently overwrite deformation'
changed=np.linalg.norm(coords['head']-coords['base'],axis=1)>1e-7;missing=np.ones(len(coords['base']),bool);missing[ids[keep]-1]=False
assert not np.any(changed&missing),'Some head deltas have no exact retained target'
merged=initial.copy();merged[keep]=coords['head'][ids[keep]-1]
assert np.array_equal(merged[~keep],initial[~keep]);body.data.vertices.foreach_set('co',merged.ravel());body.data.update()
previous={name:list(getattr(bpy.data.objects[name].data,'materials',[])) for name in features}
with bpy.data.libraries.load(str(paths['head']),link=False) as (src,dst):
 assert set(features)<=set(src.objects);dst.objects=list(features)
for name,donor in zip(features,dst.objects):
 target=bpy.data.objects[name];target.data=donor.data;target.hide_render=feature_hidden[name]
 assert target.parent is None and not target.constraints
 # Preserve native channels rather than decompose matrix_world into float32
 # Euler channels, which measurably perturbs area-light rotation on readback.
 for key,value in feature_channels[name].items():setattr(target,key,value)
 # Preserve neutral gray slots, except the explicit C20 wet iris approximation.
 if hasattr(target.data,'materials') and not name.startswith('C7 / clear cornea '):
  target.data.materials.clear()
  for material in previous[name]:target.data.materials.append(material)
 bpy.data.objects.remove(donor,do_unlink=True)
hidden=[]
for ob in s.objects:
 if ob.type=='CURVES' and 'plush' in ob.name.lower():hidden.append(ob.name);ob.hide_render=True
bpy.context.view_layer.update();actual,records['assembled']=snap(body)
assert np.array_equal(actual,merged)
assert all(bpy.data.objects[name].matrix_world==feature_world[name] for name in features),'Face/light world transforms must match evaluated source snapshot'
records['feature_world_transform_source']='Evaluated original head scene, captured before library loading'
records['feature_world_transforms']={name:list(map(list,matrix)) for name,matrix in feature_world.items()}
s.cycles.samples=a.samples;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG'
bpy.context.preferences.filepaths.save_version=0;native=out/'miao-c31-head-hand-gray.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
r={'scope':'Exact complete gray-scene branch assembly; input grip quality not inherited as a pass','sources':{k:{'path':str(p.relative_to(ROOT)),'sha256':checks[k]} for k,p in paths.items()},'records':records,'changed_head_vertices':int(changed.sum()),'retained_source_vertices':int(keep.sum()),'head_missing_delta_vertices':0,'new_hand_vertices_bit_exact':True,'head_retained_positions_bit_exact':True,'copied_complete_face_features':features,'groom_hidden_until_rebinding':hidden,'wet_iris':'C20 original colored convex cap, not anatomical glass; retained for readable gaze','native_sha256':sha(native),'script_sha256':sha(__file__),'renders':[],'limits':['Not an independent gray/colored/motion pass.','No new hand UV/groom/shape binding claimed.','All connected hand skin remains the same body mesh, not separate limb plates.']}
(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if a.render:
 cam=s.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();scale=cam.data.ortho_scale
 views=[('front',None,None),('head',Vector((0,-6,3.05)),1.7),('hands',Vector((4,-6,3)),1.25),('three-quarter',Vector((6,-9,3.9)),scale)]
 for name,position,zoom in views:
  if position is None:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=scale
  else:
   target=Vector((0,0,3.03)) if name=='head' else Vector((1.17,-.95,1.96)) if name=='hands' else Vector((.09881,0,1.609));cam.location=position;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom
  file=out/('gray-'+name+'.png');s.render.filepath=str(file);bpy.ops.render.render(write_still=True);r['renders'].append({'file':file.name,'sha256':sha(file),'camera_matrix':list(map(list,cam.matrix_world))})
 cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=scale
for k,p in paths.items():assert sha(p)==checks[k]
(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps(r),flush=True)
