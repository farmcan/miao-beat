"""C56 separate material-only gray QA: skin lids share body clay.
No shape, eye layer, lighting, visibility, pose or torso edit.
"""
import bpy,numpy as np,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];O=R/'artifacts/character-ear-sculpt-c56/gray-material-consistency';O.mkdir(parents=True,exist_ok=True)
if (O/'receipt.json').exists():raise RuntimeError('Frozen diagnostic exists')
SRC=O.parent/'soft-edge/miao-c56-soft-ear-edge.blend';assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='0ece323eadabc18f7d7f28a58b41d21f709fc3bbaeef15976e868c0bbb80f727';bpy.ops.wm.open_mainfile(filepath=str(SRC));clay=bpy.data.objects['Miao / continuous pear and rounded-square face'].data.materials[0]
def snapshot():
 r={}
 for o in bpy.data.objects:
  h=hashlib.sha256();h.update(np.array(o.matrix_world,np.float64).tobytes())
  if o.type=='MESH':
   p=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',p);h.update(p.tobytes());h.update(repr([tuple(f.vertices) for f in o.data.polygons]).encode())
  elif o.type=='CURVE':
   for sp in o.data.splines:
    for p in sp.points:h.update(np.array(p.co[:],np.float64).tobytes())
    for p in sp.bezier_points:
     for k in ['co','handle_left','handle_right']:h.update(np.array(getattr(p,k)[:],np.float64).tobytes())
  r[o.name]=h.hexdigest()
 return r
before=snapshot();materials={o.name:[m.name if m else None for m in o.data.materials] for o in bpy.data.objects if hasattr(o.data,'materials')};changes=[]
for side in ['L','R']:
 for part in ['upper lid','lower lid']:
  o=bpy.data.objects[f'C6 / {part} {side}'];old=[m.name for m in o.data.materials];assert not o.hide_render;o.data.materials.clear();o.data.materials.append(clay);changes.append({'object':o.name,'old_materials':old,'new_materials':[clay.name],'visible':not o.hide_render})
changed={v['object'] for v in changes};assert before==snapshot();assert all([m.name if m else None for m in bpy.data.objects[n].data.materials]==v for n,v in materials.items() if n not in changed);r={'scope':'Separate geometry-identical gray-material QA; only four skin lid slots match body clay','source_native_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'body_clay_material':clay.name,'changed_skin_lids':changes,'all_mesh_curve_geometry_topology_and_world_exact':True,'all_non_lid_material_slots_exact':True,'no_mesh_hidden_or_eye_geometry_edited':True,'all_ear_self_and_body_topology_results_geometry_identical_to_soft_stage':True,'art_pass':False,'limits':['Material consistency fixes a diagnostic mismatch, not a new eyelid design or automatic identity approval.','Actual images still decide whether any halo/depth mismatch persists.']};s=bpy.context.scene;s.cycles.samples=24;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;bpy.context.preferences.filepaths.save_version=0;native=O/'miao-c56-gray-skin-consistent.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);r['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest();(O/'receipt.json').write_text(json.dumps(r,indent=2));(O/'executed-build-script.py').write_text(Path(__file__).read_text());print('MATERIAL_ONLY '+json.dumps(r),flush=True);cam=s.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();scale=cam.data.ortho_scale
for view,pos,target,zoom in [('front',None,None,None),('ears',Vector((0,-6,3.30)),Vector((0,0,3.28)),1.45),('three-quarter',Vector((-6,-9,3.9)),Vector((.09881,0,1.609)),scale)]:
 if pos is None:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=scale
 else:cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom
 bpy.context.view_layer.update();s.render.filepath=str(O/('gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
print('RESULT all geometry fixed; skin-lid material consistency only',flush=True)
