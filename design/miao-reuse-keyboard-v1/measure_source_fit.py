import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];S=R/'artifacts/miao-reuse-v1/source-rest-baseline/source-rest-native36.blend';O=R/'artifacts/miao-reuse-keyboard-v1';before=hashlib.sha256(S.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);bpy.context.view_layer.update();rig=bpy.data.objects['RIG-Cat'];hand=bpy.data.objects['GEO-hands'];ev=hand.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();bones={};tips={}
for p in rig.pose.bones:
 if p.name.startswith(('ORG-UpperArm','ORG-Forearm','ORG-Hand','DEF-Index','FK-Index','DEF-Middle','DEF-Thumb','FK-Thumb','IK-MSTR-Hand','IK-POLE-UpperArm','P-ROOT-UpperArm')):
  bones[p.name]={'head':list(rig.matrix_world@p.head),'tail':list(rig.matrix_world@p.tail),'length':p.length,'matrix':[list(v) for v in rig.matrix_world@p.matrix],'parent':p.parent.name if p.parent else None,'locks':list(p.lock_rotation),'rotation_mode':p.rotation_mode,'props':{k:repr(p[k]) for k in p.keys()}}
for side in ['L','R']:
 for group in hand.vertex_groups:
  if 'Index' not in group.name or not group.name.endswith('.'+side):continue
  ids=[v.index for v in m.vertices if sum(g.weight for g in v.groups if g.group==group.index)>.6]
  if not ids:continue
  pts=[ev.matrix_world@m.vertices[i].co for i in ids];tips[group.name]={'vertices':len(ids),'bbox':{'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}}
report={'source':str(S),'source_sha256':before,'bones':bones,'index_skin_groups':tips,'hand_groups':[g.name for g in hand.vertex_groups],'actions_before':len(bpy.data.actions)};ev.to_mesh_clear();assert before==hashlib.sha256(S.read_bytes()).hexdigest();(O/'source-fit-measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'bones':bones,'tips':tips}))
