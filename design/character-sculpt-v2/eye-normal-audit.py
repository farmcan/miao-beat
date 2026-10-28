"""Read-only orientation audit after a real mixed-winding failure."""
import bpy,bmesh,numpy as np,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'artifacts/character-eye-inset-v4';old=root/'artifacts/character-eye-inset-v3/miao-eye-inset-static.blend';new=out/'miao-eye-inset-static.blend'
def snapshot():
 d={}
 for o in bpy.context.scene.objects:
  if o.type in {'MESH','CURVES'}:
   col=o.data.vertices if o.type=='MESH' else o.data.position_data;a=np.empty(len(col)*3,np.float32);col.foreach_get('co' if o.type=='MESH' else 'vector',a);d[o.name]=hashlib.sha256(a.tobytes()).hexdigest()
 return d
bpy.ops.wm.open_mainfile(filepath=str(old));oldcoords=snapshot();bpy.ops.wm.open_mainfile(filepath=str(new));newcoords=snapshot();assert oldcoords==newcoords
results=[]
for o in bpy.context.scene.objects:
 if not o.name.startswith('C6 /'):continue
 normals=[p.normal.y for p in o.data.polygons];r={'object':o.name,'polygons':len(normals),'normal_y_min':min(normals),'normal_y_max':max(normals)}
 if 'sclera' in o.name:
  front=normals[:2304];back=normals[2304:4608];assert max(front)<0 and min(back)>0;bm=bmesh.new();bm.from_mesh(o.data);r.update({'front_all_camera_facing':True,'back_all_rear_facing':True,'boundary_edges':sum(e.is_boundary for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)});assert r['boundary_edges']==0 and r['signed_volume']>0;bm.free()
 else:assert max(normals)<0;r['all_camera_facing']=True
 results.append(r)
(out/'normal-audit.json').write_text(json.dumps({'v3_v4_coordinate_hashes_identical':True,'geometry_coordinate_sha256':newcoords,'orientation':results,'limits':['Orientation and volume proof only, not art/optics/blink acceptance.','All checks read saved actual meshes.']},indent=2)+'\n');print('NORMAL_AUDIT_OK',len(results))
