from pathlib import Path
import bpy,hashlib,json
from mathutils import Vector
r=Path(__file__).resolve().parents[2];out=r/'artifacts/reference-progress-comparison';rows=[]
for tag,rel in [('c49','artifacts/character-local-merge-c49/miao-c49-local-merge.blend'),('c59','artifacts/character-wrist-graft-c59/miao-c59-c56-body-exact-c35-hand.blend')]:
 src=r/rel;h=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.cycles.samples=64;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.use_border=False;s.render.use_crop_to_border=False;cam=s.camera;cam.location=Vector((0,-6,2.66));cam.rotation_euler=(Vector((0,0,2.64))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.8;f=out/(tag+'-review-face-framed.png');s.render.filepath=str(f);bpy.ops.render.render(write_still=True);assert hashlib.sha256(src.read_bytes()).hexdigest()==h;rows.append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source_native_sha256':h,'source_unchanged':True})
(out/'framed-faces-receipt.json').write_text(json.dumps({'renders':rows,'new_geometry':False,'art_approved':False},indent=2)+'\n')
