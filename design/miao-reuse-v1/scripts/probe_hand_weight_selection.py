import bpy,json,pathlib,sys
args=sys.argv[sys.argv.index('--')+1:]
bpy.context.preferences.filepaths.use_scripts_auto_execute=False
bpy.ops.wm.open_mainfile(filepath=str(pathlib.Path(args[0]).resolve()),load_ui=False,use_scripts=False)
bpy.context.view_layer.update()
rig=bpy.data.objects['RIG-Cat'];hand=bpy.data.objects['GEO-hands'];ev=hand.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
result={'vertices':len(mesh.vertices),'group_summary':[],'side_geometry':{}}
for group in hand.vertex_groups:
 vals=[next((item.weight for item in v.groups if item.group==group.index),0.0) for v in mesh.vertices]
 if max(vals,default=0)>0.01:result['group_summary'].append({'name':group.name,'max':max(vals),'positive':sum(x>.01 for x in vals)})
for side in ['L','R']:
 inv=(rig.matrix_world@rig.pose.bones[f'DEF-Hand.{side}'].matrix).inverted();indices={g.index for g in hand.vertex_groups if g.name.endswith('.'+side)};locals=[];selected=[]
 for v in mesh.vertices:
  total=sum(item.weight for item in v.groups if item.group in indices)
  if total<.5:continue
  local=inv@(ev.matrix_world@v.co);locals.append(local)
  if -.025<=local.y<=.8*rig.pose.bones[f'DEF-Hand.{side}'].length:selected.append(v.index)
 result['side_geometry'][side]={'side_vertices':len(locals),'local_bbox_min':[min(v[k] for v in locals) for k in range(3)],'local_bbox_max':[max(v[k] for v in locals) for k in range(3)],'geometric_core_selected':len(selected),'sample_ids':selected[:20]}
ev.to_mesh_clear();pathlib.Path(args[1]).write_text(json.dumps(result,indent=2));print(json.dumps(result))
