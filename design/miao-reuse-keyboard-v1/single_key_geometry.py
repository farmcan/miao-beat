"""Geometry helpers for one native FK index/key experiment; no asset reconstruction."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
class RenderMatchedProxy:
 def __enter__(self):
  self.mods=[];self.drivers=[];self.gn=[]
  assert not bpy.context.scene.render.use_simplify
  for o in bpy.context.scene.objects:
   for f in o.animation_data.drivers if o.animation_data else []:
    if 'modifiers[' in f.data_path and f.data_path.endswith('].levels'):self.drivers.append((f,f.mute));f.mute=True
   for m in o.modifiers:
    self.mods.append((m,m.show_viewport,m.levels if m.type=='SUBSURF' else None));m.show_viewport=m.show_render
    if m.type=='SUBSURF':m.levels=m.render_levels
  for g in bpy.data.node_groups:
   for n in list(g.nodes):
    if n.bl_idname=='GeometryNodeIsViewport':
     links=[(l.from_socket,l.to_socket) for l in list(g.links) if l.from_node==n];c=g.nodes.new('FunctionNodeInputBool');c.boolean=False
     for src,dst in links:
      for l in list(g.links):
       if l.from_socket==src and l.to_socket==dst:g.links.remove(l)
      g.links.new(c.outputs[0],dst)
     self.gn.append((g,c,links))
  bpy.context.view_layer.update();return self
 def __exit__(self,*args):
  for g,c,links in self.gn:
   g.nodes.remove(c)
   for src,dst in links:g.links.new(src,dst)
  for m,vis,lev in self.mods:
   m.show_viewport=vis
   if lev is not None:m.levels=lev
  for f,old in self.drivers:f.mute=old
  bpy.context.view_layer.update()
def geometry(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();p=[e.matrix_world@v.co for v in m.vertices];t=[tuple(v.vertices) for v in m.loop_triangles];w=[{g.group:g.weight for g in v.groups} for v in m.vertices];e.to_mesh_clear();return p,t,w
def bounds(p):return ([min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)])
def record(o):
 p,t,w=geometry(o);return {'name':o.name,'p':p,'t':t,'bbox':bounds(p),'tree':BVHTree.FromPolygons(p,t,all_triangles=True)}
def overlaps(p,t,records):
 bb=bounds(p);tree=None;hits={}
 for r in records:
  b=r['bbox']
  if all(bb[1][i]>=b[0][i] and b[1][i]>=bb[0][i] for i in range(3)):
   if tree is None:tree=BVHTree.FromPolygons(p,t,all_triangles=True)
   pairs=tree.overlap(r['tree'])
   if pairs:hits[r['name']]=len(pairs)
 return hits
def measure_hand(records,target_name='Ivory piano key.014',full=True):
 h=bpy.data.objects['GEO-hands'];p,t,w=geometry(h);gi=h.vertex_groups['DEF-Index2.L'].index;ids=[i for i,v in enumerate(w) if v.get(gi,0)>.6];low=min(ids,key=lambda i:p[i].z);gaps={};nearest={};normals={}
 for r in records:
  if r['name'].startswith(('Ivory piano key','Raised black piano key')):
   samples=[]
   for i in ids:
    hit,n,_,_=r['tree'].ray_cast(Vector((p[i].x,p[i].y,2)),Vector((0,0,-1)),3)
    if hit is not None and n.z>.9:samples.append((p[i].z-hit.z,i,list(p[i]),list(hit),list(n)))
   if samples:
    q=min(samples,key=lambda x:x[0]);gaps[r['name']]={'gap_m':q[0],'skin_vertex':q[1],'skin_point':q[2],'surface_point':q[3],'surface_normal':q[4],'projected_samples':len(samples)}
  if full or r['name']==target_name:nearest[r['name']]=min(r['tree'].find_nearest(p[i])[3] for i in ids)
 result={'pad_count':len(ids),'lowest_skin':list(p[low]),'target':gaps.get(target_name),'key_projected_gaps':gaps,'nearest_3d_m':dict(sorted(nearest.items(),key=lambda x:x[1])[:7]),'hand_vertices':len(p),'hand_triangles':len(t)}
 if full:
  result['whole_hands_component_triangle_intersections']=overlaps(p,t,records)
  result['other_key_minimum_projected_gap_m']=min((v['gap_m'] for n,v in gaps.items() if n!=target_name),default=None)
 return result
