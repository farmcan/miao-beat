"""Read-only body-axis depth + string/fret inventory and embedded provenance."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];src=Path(args[0]).resolve();out=Path(args[1]).resolve();sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();body=bpy.data.objects['Body'];R=body.matrix_world.to_3x3();axes=[R.col[k].normalized() for k in range(3)]
def projected_bounds(objs):
 vals=[[],[],[]]
 for o in objs:
  e=o.evaluated_get(dg);m=e.to_mesh()
  for v in m.vertices:
   p=e.matrix_world@v.co
   for k in range(3):vals[k].append(p.dot(axes[k]))
  e.to_mesh_clear()
 return {'min':[min(v) for v in vals],'max':[max(v) for v in vals],'dimensions_m':[max(v)-min(v) for v in vals]}
strings=[o for o in bpy.data.objects if o.name.startswith('Spiral') and o.type=='CURVE'];bodybounds=projected_bounds([body]);frets=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('Cylinder'):continue
 b=projected_bounds([o]);dims=sorted(b['dimensions_m'])
 if dims[0]<.003 and dims[1]<.004 and .04<dims[2]<.08:frets.append({'name':o.name,'dimensions_in_body_axes':b['dimensions_m']})
# Whole visible instrument, excluding its single named Stand object. Helpers with no faces are excluded.
instrument=[];world_points=[]
for o in bpy.data.objects:
 if o.name=='Stand' or o.type not in ['MESH','CURVE','FONT'] or o.hide_render:continue
 e=o.evaluated_get(dg);m=e.to_mesh()
 if len(m.polygons):instrument.append(o);world_points += [e.matrix_world@v.co for v in m.vertices]
 e.to_mesh_clear()
def worldbox(ps):
 lo=[min(p[k] for p in ps) for k in range(3)];hi=[max(p[k] for p in ps) for k in range(3)];return {'min':lo,'max':hi,'dimensions_m':[hi[k]-lo[k] for k in range(3)]}
instrument_world=worldbox(world_points);instrument_oriented=projected_bounds(instrument)
prop=[]
for m in bpy.data.materials:
 item={'material':m.name,'custom_properties':{k:str(m[k])[:3000] for k in m.keys()},'image_links':[]}
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image:item['image_links'].append({'image':n.image.name,'filepath':n.image.filepath,'packed':bool(n.image.packed_file)})
 prop.append(item)
r={'source':str(src),'source_sha256_before':sha,'body_axes_world':[list(a) for a in axes],'body_axis_roles':['width','body length','surface normal / thickness'],'body_surface_normal_thickness_m':bodybounds['dimensions_m'][2],'body_projected_bbox':bodybounds,'body_thickness_at_scale_070_m':bodybounds['dimensions_m'][2]*.7,'strings':[{'name':o.name,'splines':len(o.data.splines),'type':o.type,'material':[m.name for m in o.data.materials]} for o in strings],'string_count':len(strings),'frets_geometric_candidates':frets,'frets_count':len(frets),'instrument_without_stand_world_bbox':instrument_world,'instrument_without_stand_projected_body_axes_bbox':instrument_oriented,'included_instrument_object_names':[o.name for o in instrument],'excluded_object_names':['Stand'],'material_provenance':prop,'source_sha256_after':hashlib.sha256(src.read_bytes()).hexdigest(),'notes':['Body world Y bbox includes author stand-lean angle and is not its thickness.','Stand and other hardware are not included in Body slab thickness.','No geometry / material edits, no pose, no rig, no render.']};assert sha==r['source_sha256_after'];out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'body_thickness_m':r['body_surface_normal_thickness_m'],'scaled070':r['body_thickness_at_scale_070_m'],'strings':r['strings'],'frets':r['frets_count'],'instrument_bbox':instrument_world,'instrument_body_axes_bbox':instrument_oriented,'output':str(out)}))
