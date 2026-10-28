"""Render the B-reviewed C6 static anatomy with its saved color materials."""
import argparse,bpy,sys,json,hashlib,time
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--input',default='artifacts/character-eye-inset-v3/miao-eye-inset-static.blend');p.add_argument('--output',default='artifacts/character-eye-inset-v3-color');p.add_argument('--size',type=int,default=1024);p.add_argument('--samples',type=int,default=64);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];src=root/a.input;out=root/a.output;out.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();input_sha=sha(src)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.render.resolution_x=s.render.resolution_y=a.size;s.cycles.samples=a.samples;s.cycles.seed=17;s.cycles.use_animated_seed=False;frames=[]
for view in ['front','three-quarter']:
 if view=='three-quarter':
  camera=s.camera;camera.location=(6,-9,3.9);camera.rotation_euler=(Vector((.18,0,1.72))-camera.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(out/('color-'+view+'.png'));t=time.time();bpy.ops.render.render(write_still=True);frames.append({'view':view,'sha256':sha(s.render.filepath),'seconds':time.time()-t})
assert sha(src)==input_sha
(out/'receipt.json').write_text(json.dumps({'stage':'C6-eye-inset-colored-static-unreviewed','input_sha256':input_sha,'source_sha256':sha(__file__),'input_unchanged':True,'render_settings':{'resolution':a.size,'samples':a.samples,'seed':17,'blender':bpy.app.version_string},'renders':frames,'limits':['New colored static eye structure only; three independent reviews pending.','No blink keys, closure guarantee, natural strum, head movement or web acceptance.']},indent=2)+'\n')
