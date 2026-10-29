"""Read-only render-aligned evaluated proxy; source viewport settings restored before exit.
Direct render depsgraph unavailable; no exact-render capture claim.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];O=R/'artifacts/miao-reuse-keyboard-v1';S=O/'render-quality-diagnostic/native-render2-working36.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(S);bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);sc=bpy.context.scene;assert not sc.render.use_simplify
rig=bpy.data.objects['RIG-Cat'];pose=lambda:hashlib.sha256(json.dumps([(b.name,[list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest();ph=pose();saved=[];drivers=[]
for o in sc.objects:
 for f in o.animation_data.drivers if o.animation_data else []:
  if 'modifiers[' in f.data_path and f.data_path.endswith('].levels'):
   drivers.append((f,f.mute));f.mute=True
 for m in o.modifiers:
  saved.append((m,m.show_viewport,m.levels if m.type=='SUBSURF' else None));m.show_viewport=m.show_render
  if m.type=='SUBSURF':m.levels=m.render_levels
# Render context Is Viewport=False; temporary constants only in the unsaved proxy.
viewport_substitutions=[]
for group in bpy.data.node_groups:
 for node in list(group.nodes):
  if node.bl_idname=='GeometryNodeIsViewport':
   links=[(l.from_socket,l.to_socket) for l in list(group.links) if l.from_node==node]
   constant=group.nodes.new('FunctionNodeInputBool');constant.boolean=False
   for src,dst in links:
    for link in list(group.links):
     if link.from_socket==src and link.to_socket==dst:group.links.remove(link)
    group.links.new(constant.outputs[0],dst)
   viewport_substitutions.append((group,constant,links))
bpy.context.view_layer.update()
def geo(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();p=[e.matrix_world@v.co for v in m.vertices];t=[tuple(v.vertices) for v in m.loop_triangles];w=[{g.group:g.weight for g in v.groups} for v in m.vertices];e.to_mesh_clear();return p,t,w
def bounds(p):return {'min':[min(v[i] for v in p) for i in range(3)],'max':[max(v[i] for v in p) for i in range(3)]}
propnames=[r['name'] for r in json.load(open(O/'prop/prop-receipt.json'))['objects']];props=[]
for name in propnames:
 p,t,_=geo(bpy.data.objects[name]);props.append({'name':name,'p':p,'t':t,'bbox':bounds(p),'tree':BVHTree.FromPolygons(p,t,all_triangles=True)})
h=bpy.data.objects['GEO-hands'];p,t,w=geo(h);result={'source_native':str(S),'source_sha256':before,'pose_sha256':ph,'method':'VIEWPORT depsgraph with snapshot show_viewport=show_render and each Subsurf levels=render_levels (2), all level drivers temporarily muted; use_simplify=False; GeometryNodeIsViewport outputs temporarily False to match render context. Independent matched proxy, not directly captured render depsgraph. No native save.','hands':{},'cat_vs_keyboard':{},'render_aligned_floor':{},'geometry_node_is_viewport_nodes':[]}
for group in bpy.data.node_groups:
 for node in group.nodes:
  if node.bl_idname=='GeometryNodeIsViewport':result['geometry_node_is_viewport_nodes'].append({'group':group.name,'node':node.name})
def overlaps(p,t,parts):
 bb=bounds(p);tree=BVHTree.FromPolygons(p,t,all_triangles=True);out={}
 for r in parts:
  if all(bb['max'][i]>=r['bbox']['min'][i] and r['bbox']['max'][i]>=bb['min'][i] for i in range(3)):
   x=tree.overlap(r['tree'])
   if x:out[r['name']]=len(x)
 return out
for side in ['L','R']:
 gi=h.vertex_groups['DEF-Index2.'+side].index;ids=[i for i,v in enumerate(w) if v.get(gi,0)>.6];low=min(ids,key=lambda i:p[i].z);sidegroups={g.index for g in h.vertex_groups if g.name.endswith('.'+side)};whole={i for i,v in enumerate(w) if sum(ww for g,ww in v.items() if g in sidegroups)>.5};tris=[tr for tr in t if all(i in whole for i in tr)];near=[];clear={}
 for part in props:
  near.append({'name':part['name'],'minimum_3d_distance_m':min(part['tree'].find_nearest(p[i])[3] for i in ids)})
  if part['name'].startswith(('Ivory piano key','Raised black piano key')):
   gaps=[]
   for i in ids:
    hit,_,_,_=part['tree'].ray_cast(Vector((p[i].x,p[i].y,2)),Vector((0,0,-1)),3)
    if hit is not None:gaps.append(p[i].z-hit.z)
   if gaps:clear[part['name']]={'projected_pad_vertices':len(gaps),'minimum_vertical_gap_m':min(gaps)}
 near.sort(key=lambda v:v['minimum_3d_distance_m']);result['hands'][side]={'hand_total_vertices':len(p),'hand_total_tris':len(t),'pad_vertices':len(ids),'lowest_point':list(p[low]),'target_white_vertical_gap_m':p[low].z-.3280000107,'nearest_components':near[:5],'projected_key_clearances':clear,'whole_side_triangle_intersections':overlaps(p,tris,props)}
for name in ['GEO-body','GEO-head','GEO-arms','GEO-legs','GEO-shoes']:
 cp,ct,_=geo(bpy.data.objects[name]);result['cat_vs_keyboard'][name]=overlaps(cp,ct,props)
 if name=='GEO-shoes':
  result['render_aligned_floor']={'z':min(v.z for v in cp),'L_min':min(v.z for v in cp if v.x>0),'R_min':min(v.z for v in cp if v.x<0),'vertices':len(cp),'tris':len(ct),'bbox':bounds(cp)}
# Restore all temporary proxy settings and original driver states; never save proxy into authoring native.
for group,constant,links in viewport_substitutions:
 group.nodes.remove(constant)
 for src,dst in links:group.links.new(src,dst)
for m,visible,levels in saved:
 m.show_viewport=visible
 if levels is not None:m.levels=levels
for f,state in drivers:f.mute=state
bpy.context.view_layer.update();assert pose()==ph;assert sha(S)==before
result['native_sha256_after']=sha(S);result['settings_restored']=True;(O/'support-prop/render2-matched-proxy-fit.json').write_text(json.dumps(result,indent=2)+'\n');print('RENDER2_PROXY',json.dumps(result))
