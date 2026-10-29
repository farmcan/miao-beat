"""Read-only cat/bone dimensions for one static guitar placement proposal."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];src=Path(args[0]).resolve();out=Path(args[1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def bbox(points):
 mi=[min(p[k] for p in points) for k in range(3)];ma=[max(p[k] for p in points) for k in range(3)];return {'min':mi,'max':ma,'dimensions':[ma[k]-mi[k] for k in range(3)]}
r={'blender':bpy.app.version_string,'source':str(src),'objects':{},'bones':{},'source_saved':False}
for name in ['GEO-head','GEO-body','GEO-arms','GEO-hands','GEO-shoes','GEO-legs','GEO-ears']:
 o=bpy.data.objects.get(name)
 if o:
  e=o.evaluated_get(dg);m=e.to_mesh();pts=[e.matrix_world@v.co for v in m.vertices];r['objects'][name]={'base_bbox':bbox([o.matrix_world@v.co for v in o.data.vertices]),'evaluated_bbox':bbox(pts)};e.to_mesh_clear()
rig=bpy.data.objects['RIG-Cat'];r['rig_matrix_world']=[list(row) for row in rig.matrix_world]
for side in ['L','R']:
 for part in ['ORG-UpperArm','ORG-Forearm','ORG-Hand']:
  name=f'{part}.{side}';pb=rig.pose.bones[name];r['bones'][name]={'head':list(rig.matrix_world@pb.head),'tail':list(rig.matrix_world@pb.tail),'length':(rig.matrix_world@pb.tail-rig.matrix_world@pb.head).length}
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
