"""Verify a compatibility GLB without saving or editing the source asset."""
import bpy,json,sys,hashlib,struct
from pathlib import Path
from collections import Counter
from mathutils import Vector,kdtree
args=sys.argv[sys.argv.index('--')+1:];src=Path(args[0]).resolve();glb=Path(args[1]).resolve()
def read_stats():
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];allpts=[];alltris=[];components=[]
 for o in obs:
  m=o.data;m.calc_loop_triangles();pts=[o.matrix_world@v.co for v in m.vertices];allpts+=pts
  alltris += [tuple(sorted(tuple(round(float(x),5) for x in pts[v]) for v in t.vertices)) for t in m.loop_triangles]
  # Virtual exact-coordinate welding is audit-only; glTF legitimately splits normals/UVs.
  point_ids={};welded=[];remap=[]
  for p in pts:
   key=tuple(p)
   if key not in point_ids:point_ids[key]=len(welded);welded.append(p)
   remap.append(point_ids[key])
  adj=[[] for _ in welded]
  for e in m.edges:
   a,b=(remap[v] for v in e.vertices);adj[a].append(b);adj[b].append(a)
  seen=set()
  for vi in range(len(welded)):
   if vi in seen:continue
   todo=[vi];seen.add(vi);vs=[]
   while todo:
    u=todo.pop();vs.append(welded[u])
    for n in adj[u]:
     if n not in seen:seen.add(n);todo.append(n)
   mi=[min(p[k] for p in vs) for k in range(3)];ma=[max(p[k] for p in vs) for k in range(3)];components.append({'vertices':len(vs),'min':mi,'max':ma,'dimensions':[ma[k]-mi[k] for k in range(3)]})
 bbmin=[min(p[k] for p in allpts) for k in range(3)];bbmax=[max(p[k] for p in allpts) for k in range(3)]
 stat={'mesh_objects':len(obs),'vertices':len(allpts),'triangles':len(alltris),'bbox_min':bbmin,'bbox_max':bbmax,'dimensions_m':[bbmax[k]-bbmin[k] for k in range(3)],'connected_islands_after_exact_coordinate_weld':len(components),'string_islands':[c for c in components if c['dimensions'][2]>.8 and c['dimensions'][0]<.02],'fret_islands':[c for c in components if c['dimensions'][0]>.05 and c['dimensions'][1]<.003 and c['dimensions'][2]<.003],'materials':[m.name for m in bpy.data.materials if m.users],'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images if i.size[0]>0 and i.name not in ['Render Result','Viewer Node']]}
 return stat,allpts,Counter(alltris)
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);a,ap,at=read_stats();source_samplers=[{'node':n.name,'image':n.image.name if n.image else None,'interpolation':n.interpolation,'extension':n.extension} for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE']
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb),merge_vertices=True);b,bp,bt=read_stats()
def max_nearest(p,q):
 kd=kdtree.KDTree(len(q))
 for i,v in enumerate(q):kd.insert(v,i)
 kd.balance();return max(kd.find(v)[2] for v in p)
raw=glb.read_bytes();n,t=struct.unpack_from('<II',raw,12);g=json.loads(raw[20:20+n]);materials=g.get('materials',[])
report={'blender':bpy.app.version_string,'source':str(src),'glb':str(glb),'source_stats':a,'reimport_stats':b,'triangle_coordinate_multiset_match_1e5m':at==bt,'max_vertex_distance_m':max(max_nearest(ap,bp),max_nearest(bp,ap)),'extensions_required':g.get('extensionsRequired',[]),'extensions_used':g.get('extensionsUsed',[]),'gltf_materials':materials,'gltf_images':g.get('images',[]),'samplers':g.get('samplers',[]),'source_image_node_sampler_settings':source_samplers,'gltf_meshes':len(g.get('meshes',[])),'buffers':g.get('buffers',[]),'compatible_blender36':'pending downstream validation','original_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(raw).hexdigest()}
report['checks']={'six_strings':len(b['string_islands'])==6,'eighteen_frets':len(b['fret_islands'])==18,'same_triangle_count':a['triangles']==b['triangles'],'same_bbox_1e6m':max(abs(x-y) for x,y in zip(a['bbox_min']+a['bbox_max'],b['bbox_min']+b['bbox_max']))<1e-6,'geometry_distance_under_1e6m':report['max_vertex_distance_m']<1e-6,'three_embedded_4k_textures':len(g.get('images',[]))==3 and all(i.get('bufferView') is not None for i in g.get('images',[])) and all(i['size']==[4096,4096] for i in b['images'])}
(glb.parent/'reimport-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':report['checks'],'max_vertex_distance_m':report['max_vertex_distance_m'],'triangle_coordinate_multiset_match':at==bt,'extensions_required':report['extensions_required'],'samplers':report['samplers']}));assert all(report['checks'].values())
