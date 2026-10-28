"""C-stage optical-card size refinement. Coordinates and eye shapes stay fixed."""
import bpy,numpy as np,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];src=root/'artifacts/character-eye-cornea-v2/miao-eye-cornea-static.blend';out=root/'artifacts/character-eye-cornea-v3';out.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
hashes={}
for o in s.objects:
 if o.type in {'MESH','CURVES'}:
  c=o.data.vertices if o.type=='MESH' else o.data.position_data;a=np.empty(len(c)*3,np.float32);c.foreach_get('co' if o.type=='MESH' else 'vector',a);hashes[o.name]=hashlib.sha256(a.tobytes()).hexdigest()
changes=[]
for o in s.objects:
 if o.type=='LIGHT' and o.name.startswith('C7 / optical area'):
  changes.append({'light':o.name,'before_energy':o.data.energy,'before_size':o.data.size,'after_energy':100,'after_size':.55});o.data.energy=100;o.data.size=.55
assert len(changes)==2;s.render.resolution_x=s.render.resolution_y=1024;s.cycles.samples=64;s.cycles.seed=17;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath='//renders/eye-optics.png';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-eye-cornea-static.blend'),compress=True)
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.35;s.render.border_max_x=.63;s.render.border_min_y=.70;s.render.border_max_y=.90;s.render.filepath=str(out/'optics-authoring-crop.png');bpy.ops.render.render(write_still=True)
(out/'receipt.json').write_text(json.dumps({'stage':'C7-optical-lighting-unreviewed','input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'only_light_energy_size_changed':changes,'geometry_coordinate_sha256_unchanged':hashes,'limits':['Crop is internal diagnostic only; complete color views and independent C reviews required.','No new blink or closure proof.']},indent=2)+'\n')
