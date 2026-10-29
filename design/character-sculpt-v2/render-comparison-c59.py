from pathlib import Path
import bpy,hashlib,json
from mathutils import Vector
r=Path(__file__).resolve().parents[2];out=r/'artifacts/reference-progress-comparison';src=r/'artifacts/character-wrist-graft-c59/miao-c59-c56-body-exact-c35-hand.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.cycles.samples=64;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=1024;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.use_border=False;s.render.use_crop_to_border=False;cam=s.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();scale=cam.data.ortho_scale;rows=[]
for view in ['full','face']:
 if view=='face':cam.location=Vector((0,-6,3.05));cam.rotation_euler=(Vector((0,0,3.03))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.7
 else:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=scale
 f=out/('c59-review-'+view+'.png');s.render.filepath=str(f);bpy.ops.render.render(write_still=True);rows.append({'file':f.name,'sha256':sha(f),'camera_matrix':list(map(list,cam.matrix_world))})
assert sha(src)==h
(out/'render-c59-review-receipt.json').write_text(json.dumps({'source_native_sha256':h,'source_unchanged':True,'new_geometry':False,'new_animation':False,'art_approved':False,'renders':rows},indent=2)+'\n')
