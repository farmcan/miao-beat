"""C43 controlled eye receiver A/B. Does not modify geometry or claim art approval."""
import bpy, numpy as np, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/character-eye-lighting-c43/controlled-ab'
SRC=ROOT/'artifacts/character-alignment-c38/head-expression-only/miao-c38-coupled-head-gray.blend'
COLOR=ROOT/'artifacts/character-eye-wet-iris-c20/miao-c20-wet-iris.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def geom(ob):
 if ob.type=='MESH':
  p=np.empty(len(ob.data.vertices)*3,np.float32);ob.data.vertices.foreach_get('co',p)
  ix=np.empty(len(ob.data.loops),np.int32);ob.data.loops.foreach_get('vertex_index',ix)
  return hashlib.sha256(p.tobytes()+ix.tobytes()+np.asarray(ob.matrix_world,np.float32).tobytes()).hexdigest()
 if ob.type=='CURVE':
  return hashlib.sha256(repr([(list(p.co),list(p.handle_left),list(p.handle_right)) for s in ob.data.splines for p in s.bezier_points]+[list(p.co) for s in ob.data.splines for p in s.points]).encode()+np.asarray(ob.matrix_world,np.float32).tobytes()).hexdigest()
 return None

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 assert not (OUT/'receipt.json').exists(),'Preserve frozen result'
 assert sha(SRC)=='f481e8a0c00eb4ec5baf5d9c43a6bc250f5a28c4475d9d9cba0ea360ca1c8439'
 bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
 targets={o.name:o for o in s.objects};before={k:geom(o) for k,o in targets.items() if o.type in ['MESH','CURVE']}
 restored=[]
 with bpy.data.libraries.load(str(COLOR),link=False) as (src,dst):
  names=[n for n in src.objects if n in targets and hasattr(targets[n].data,'materials')];dst.objects=list(names)
 for name,donor in zip(names,dst.objects):
  target=targets[name];old=[m.name if m else None for m in target.data.materials];new=list(donor.data.materials)
  if new:
   target.data.materials.clear()
   for m in new:target.data.materials.append(m)
   restored.append({'object':name,'before':old,'restored_C20_materials':[m.name for m in new]})
  bpy.data.objects.remove(donor,do_unlink=True)
 # Hair remains hidden because it is not rebound to the new head. This is identical in A/B.
 hidden=[o.name for o in s.objects if o.type=='CURVES' and o.hide_render]
 assert before=={k:geom(targets[k]) for k in before}
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=128;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.cycles.use_denoising=True
 s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG'
 cam=s.camera;original=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale)
 caps=[targets['C7 / clear cornea '+side] for side in ['L','R']]
 lights=[o for o in s.objects if o.type=='LIGHT'];light_before={o.name:{'energy':o.data.energy,'diffuse':o.data.diffuse_factor,'specular':o.data.specular_factor,'matrix':list(map(list,o.matrix_world))} for o in lights}
 receiver=targets['Studio / broad key'].light_linking.receiver_collection
 assert receiver and receiver==targets['Studio / broad fill'].light_linking.receiver_collection
 assert all(c.name not in receiver.all_objects for c in caps)
 report={'scope':'C43 opaque C20 iris-cap receiver routing A/B, restored C20 colors on exact C38 geometry; no final art pass','sources':{'C38':{'path':str(SRC.relative_to(ROOT)),'sha256':sha(SRC)},'C20_materials':{'path':str(COLOR.relative_to(ROOT)),'sha256':sha(COLOR)}},'material_restoration':restored,'geometry_sha256_before':before,'groom_hidden_in_both':hidden,'render':{'engine':'CYCLES','device':'CPU','samples':128,'seed':17,'resolution':768},'lights':light_before,'conditions':[],'production_changed':False,'character_gate_passed':False,'limits':['No new model or animation.','C38 whole-character P0 remains.','Groom is hidden until valid rebinding; this is not final plush material acceptance.','Only two cap objects join the existing shared studio receiver collection in B.']}
 bpy.context.preferences.filepaths.save_version=0
 for variant in ['A-original-routing','B-cap-studio-receivers']:
  if variant.startswith('B'):
   for c in caps:receiver.objects.link(c)
  bpy.context.view_layer.update()
  assert before=={k:geom(targets[k]) for k in before}
  assert light_before=={o.name:{'energy':o.data.energy,'diffuse':o.data.diffuse_factor,'specular':o.data.specular_factor,'matrix':list(map(list,o.matrix_world))} for o in lights}
  cam.location=original[0];cam.rotation_euler=original[1];cam.data.ortho_scale=original[2]
  native=OUT/(variant+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
  cond={'variant':variant,'native_sha256':sha(native),'receiver_caps':[c.name for c in caps if c.name in receiver.all_objects],'renders':[]}
  for view in ['full','face']:
   if view=='face':
    cam.location=Vector((0,-6,3.05));target=Vector((0,0,3.03));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.7
   else:cam.location=original[0];cam.rotation_euler=original[1];cam.data.ortho_scale=original[2]
   bpy.context.view_layer.update();p=OUT/(variant+'-'+view+'.png');s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
   cond['renders'].append({'file':p.name,'sha256':sha(p),'camera_matrix':list(map(list,cam.matrix_world)),'ortho_scale':cam.data.ortho_scale})
  report['conditions'].append(cond);(OUT/'receipt.partial.json').write_text(json.dumps(report,indent=2)+'\n')
 cam.location=original[0];cam.rotation_euler=original[1];cam.data.ortho_scale=original[2]
 report['script_sha256']=sha(__file__);report['geometry_unchanged']=before=={k:geom(targets[k]) for k in before}
 (OUT/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+json.dumps({'output':str(OUT),'geometry_unchanged':report['geometry_unchanged'],'renders':4}),flush=True)
main()
