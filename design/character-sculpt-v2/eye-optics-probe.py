"""Authoring diagnostics only: paired crop renders and real iris/sclera gap probes."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];out=root/'artifacts/character-eye-optics-probe';out.mkdir(exist_ok=True);src=root/'artifacts/character-eye-inset-v3/miao-eye-inset-static.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.render.resolution_x=s.render.resolution_y=1024;s.cycles.samples=64;s.cycles.seed=17;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.35;s.render.border_max_x=.63;s.render.border_min_y=.70;s.render.border_max_y=.90
results=[];dg=bpy.context.evaluated_depsgraph_get()
for side in ['L','R']:
 white=bpy.data.objects['C6 / sclera '+side];iris=bpy.data.objects['C6 / iris '+side];bvh=BVHTree.FromObject(white,dg);iv=white.matrix_world.inverted();direction=(iv.to_3x3()@Vector((0,1,0))).normalized();gaps=[]
 samples=[iris.matrix_world@v.co for v in iris.data.vertices]+[iris.matrix_world@p.center for p in iris.data.polygons]
 for p in samples:
  hit=bvh.ray_cast(iv@Vector((p.x,-3,p.z)),direction,20)[0]
  if hit is not None:gaps.append(float((white.matrix_world@hit).y-p.y))
 results.append({'side':side,'sample_count':len(samples),'white_hit_count':len(gaps),'iris_front_clearance_min':min(gaps),'iris_front_clearance_max':max(gaps),'samples_behind_white':sum(x<0 for x in gaps),'iris_polygon_normal_y_range':[min(p.normal.y for p in iris.data.polygons),max(p.normal.y for p in iris.data.polygons)]})
s.render.filepath=str(out/'baseline-eye-crop.png');bpy.ops.render.render(write_still=True)
mat=bpy.data.materials['C6 / attached navy iris'];bs=mat.node_tree.nodes.get('Principled BSDF');before={x:bs.inputs[x].default_value for x in ['Roughness','Coat Weight','Coat Roughness','IOR']};bs.inputs['Roughness'].default_value=.07;bs.inputs['Coat Weight'].default_value=.85;bs.inputs['Coat Roughness'].default_value=.035;bs.inputs['IOR'].default_value=1.45
s.render.filepath=str(out/'wet-coat-eye-crop.png');bpy.ops.render.render(write_still=True)
(out/'receipt.json').write_text(json.dumps({'diagnostic_only':True,'camera_unchanged':True,'lights_geometry_unchanged':True,'gap_probes':results,'before_iris_bsdf':before,'after_iris_bsdf':{x:bs.inputs[x].default_value for x in before},'limits':['Crop is internal diagnostic, not whole-frame delivery.','Gap samples not exhaustive intersection proof.','Optics change is unreviewed, no blink expansion.']},indent=2)+'\n')
