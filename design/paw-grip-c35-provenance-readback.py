"""Read-only saved native point/source provenance check for C35 handoff."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'artifacts/character-paw-grip-c35';old=root/'artifacts/character-paw-grip-c33/diagnostic-c33-infeasible-or-collision.blend';new=out/'miao-c35-fixed-vertex-tessellation.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();oh=sha(old);nh=sha(new);data=[]
for label,p in [('C33',old),('C35',new)]:
 bpy.ops.wm.open_mainfile(filepath=str(p));me=bpy.data.objects['Miao / continuous pear and rounded-square face'].data;attrs={}
 for attr in me.attributes:
  if attr.domain=='POINT' and attr.data_type in {'INT','BOOLEAN'}:
   ar=np.array([int(q.value) for q in attr.data],dtype=np.int64);attrs[attr.name]={'count':len(ar),'sha256_integer_values':hashlib.sha256(ar.tobytes()).hexdigest(),'positive_count':int((ar>0).sum())}
 coords=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',coords);data.append({'scene':label,'body_vertex_count':len(me.vertices),'ordered_float32_coordinate_sha256':hashlib.sha256(coords.tobytes()).hexdigest(),'point_integer_attributes':attrs})
checks={name:data[0]['point_integer_attributes'][name]==data[1]['point_integer_attributes'].get(name) for name in data[0]['point_integer_attributes']};r={'stage':'C35-readonly-saved-native-point-provenance','source_C33_native_sha256':oh,'C35_native_sha256':nh,'old_unchanged':sha(old)==oh,'new_unchanged':sha(new)==nh,'ordered_all_vertex_coordinates_bit_exact':data[0]['ordered_float32_coordinate_sha256']==data[1]['ordered_float32_coordinate_sha256'],'point_integer_attribute_checks':checks,'all_point_int_source_ids_preserved':all(checks.values()),'source_head_merge_key':'C23 source vertex id remains integer-value exact; no nearest mapping needed.','scenes':data};(out/'vertex-provenance-readback.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps({k:v for k,v in r.items() if k!='scenes'}))
