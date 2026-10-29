"""Read-only source instrument audit. Never runs embedded scripts or saves a blend."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];src=Path(args[0]).resolve();out=Path(args[1]).resolve();sha=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def box(points):
 if not points:return None
 lo=[min(p[k] for p in points) for k in range(3)];hi=[max(p[k] for p in points) for k in range(3)];return {'min':lo,'max':hi,'dimensions':[hi[k]-lo[k] for k in range(3)]}
objects=[]
for o in bpy.data.objects:
 d={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'materials':[m.name for m in o.data.materials] if hasattr(o.data,'materials') else [],'location':list(o.location),'scale':list(o.scale),'rotation_mode':o.rotation_mode,'dimensions_world_axes':list(o.dimensions),'world_matrix':[list(r) for r in o.matrix_world],'modifiers':[{'name':m.name,'type':m.type,'show_render':m.show_render} for m in o.modifiers]}
 if o.type in ['MESH','CURVE']:
  e=o.evaluated_get(dg);m=e.to_mesh();d['evaluated_vertices']=len(m.vertices);d['evaluated_faces']=len(m.polygons);d['evaluated_world_bbox']=box([e.matrix_world@v.co for v in m.vertices]);d['evaluated_local_bbox']=box([v.co.copy() for v in m.vertices]);d['uv_layers']=list(m.uv_layers.keys());e.to_mesh_clear()
  if o.type=='MESH':d['base_vertices']=len(o.data.vertices);d['base_faces']=len(o.data.polygons)
  else:d['curve_splines']=len(o.data.splines);d['bevel_depth']=o.data.bevel_depth
 objects.append(d)
report={'source':str(src),'source_sha256_before':sha,'blender':bpy.app.version_string,'scripts_auto_execute':bpy.context.preferences.filepaths.use_scripts_auto_execute,'objects':objects,'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file),'filepath':i.filepath} for i in bpy.data.images],'materials':[{'name':m.name,'use_nodes':m.use_nodes,'image_nodes':[{'node':n.name,'image':n.image.name if n.image else None} for n in m.node_tree.nodes if n.type=='TEX_IMAGE'] if m.use_nodes else [],'node_types':sorted(set(n.bl_idname for n in m.node_tree.nodes)) if m.use_nodes else []} for m in bpy.data.materials],'texts':[{'name':t.name,'use_module':t.use_module} for t in bpy.data.texts],'source_sha256_after':hashlib.sha256(src.read_bytes()).hexdigest()};assert sha==report['source_sha256_after'];out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'output':str(out),'objects':len(objects),'images':len(report['images']),'original_sha256':sha}))
