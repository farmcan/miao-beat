import bpy,json,sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];bpy.ops.wm.open_mainfile(filepath=str(Path(args[0]).resolve()),load_ui=False,use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();body=bpy.data.objects['Body'];n=body.matrix_world.to_3x3().col[2].normalized();depths=[]
for o in bpy.data.objects:
 if o.type not in ['MESH','CURVE','FONT'] or o.name=='Stand' or o.hide_render:continue
 e=o.evaluated_get(dg);m=e.to_mesh()
 if len(m.polygons):
  z=[(e.matrix_world@v.co).dot(n) for v in m.vertices];depths.append({'name':o.name,'normal_min_m':min(z),'normal_max_m':max(z)})
 e.to_mesh_clear()
r={'stand':'Stand','root':'HH Guitar with stand','brands_font_objects':[{'object':o.name,'text':o.data.body,'materials':[m.name for m in o.data.materials]} for o in bpy.data.objects if o.type=='FONT'],'body_normal_range':next(x for x in depths if x['name']=='Body'),'farthest_front_objects':sorted(depths,key=lambda x:x['normal_max_m'],reverse=True)[:8],'farthest_back_objects':sorted(depths,key=lambda x:x['normal_min_m'])[:8],'separate_curve_objects':[o.name for o in bpy.data.objects if o.type=='CURVE'],'notes':['Inventory only; did not remove, hide, change materials, or export any object.']}
Path(args[1]).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
