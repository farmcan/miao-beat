import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
out=Path(__file__).resolve().parents[2]/'artifacts/character-sculpt-d0-blink';bpy.ops.wm.open_mainfile(filepath=str(out/'miao-d0-blink-study.blend'));c=bpy.data.objects['D0 / Blink control'];eyes=[o for o in bpy.data.objects if o.name.startswith(('Face / ivory eye','Face / sideward iris'))];skins=[o for o in bpy.data.objects if o.name.startswith(('Face / integrated upper eyelid','Face / D0 lower eyelid'))];body=bpy.data.objects['Miao / continuous pear and rounded-square face'];dg=bpy.context.evaluated_depsgraph_get();report={}
for b in [0,.125,.25,.375,.5,.625,.75,.875,1]:
 c['Blink']=b;c.update_tag();bpy.context.view_layer.update();trees=[(o,BVHTree.FromObject(o,dg)) for o in eyes+skins+[body]];visible={o.name:0 for o in eyes};skin_hits=0
 for eye in [o for o in eyes if o.name.startswith('Face / ivory eye')]:
  x,y,z=eye.location
  for px in np.linspace(x-.13,x+.13,81):
   for pz in np.linspace(z-.115,z+.115,81):
    hits=[]
    for o,t in trees:
     inv=o.matrix_world.inverted();hit=t.ray_cast(inv@Vector((px,-3,pz)),inv.to_3x3()@Vector((0,1,0)),6)[0]
     if hit is not None:hit=o.matrix_world@hit
     if hit is not None:hits.append((hit.y,o.name))
    if hits:
     nearest=min(hits)[1]
     if nearest in visible:visible[nearest]+=1
     if nearest.startswith(('Face / integrated upper eyelid','Face / D0 lower eyelid')):skin_hits+=1
 report[str(b)]={'visible_eye_front_grid_rays':visible,'skin_hits':skin_hits,'grid_per_eye':81*81,'ray_direction':'world +Y; fixed frontal orthographic geometric sample, not all camera viewpoints'}
(out/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
