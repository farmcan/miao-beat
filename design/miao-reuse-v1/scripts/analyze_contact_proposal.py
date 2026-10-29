"""Read-only geometry/rig measurements and algebraic contact proposal. No pose writes."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
args=sys.argv[sys.argv.index('--')+1:];source=Path(args[0]).resolve();out=Path(args[1]).resolve()
sha=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
rig=bpy.data.objects['RIG-Cat'];hand=bpy.data.objects['GEO-hands'];g=bpy.data.objects['REUSE-CLASSIC-GUITAR']
def v(v):return list(v)
def axes(m):return [v(m.to_3x3().col[k].normalized()) for k in range(3)]
def bb(points):
 mi=[min(p[k] for p in points) for k in range(3)];ma=[max(p[k] for p in points) for k in range(3)];return {'min':mi,'max':ma,'dimensions':[ma[k]-mi[k] for k in range(3)]}
report={'source':str(source),'source_sha256_before':sha,'blender':bpy.app.version_string,'scope':'Only reads existing scene; candidate transforms are algebraic matrices. Does not assign pose/object transforms, save blend, or render.','hand_bones':{},'skin_tip_proxies':{},'curl_jacobians_current':{},'fingers_constraints':{}}
e=hand.evaluated_get(dg);em=e.to_mesh();group_names={vg.index:vg.name for vg in hand.vertex_groups}
# Keep true evaluated skin weights, not bone endpoints alone. Radius is a proxy, never contact proof.
for side in ['L','R']:
 hp=rig.pose.bones[f'ORG-Hand.{side}'];hm=rig.matrix_world@hp.matrix;report['hand_bones'][side]={'matrix_world':[list(r) for r in hm],'axes_xyz_world':axes(hm),'length':hp.length,'head':v(rig.matrix_world@hp.head),'tail':v(rig.matrix_world@hp.tail)}
 for finger in ['Index','Middle','Pinky','Thumb']:
  n=f'DEF-{finger}2.{side}';p=rig.pose.bones[n];wm=rig.matrix_world@p.matrix;wi=wm.inverted();group=hand.vertex_groups.get(n);picked=[];local=[]
  for vertex in em.vertices:
   weight=next((x.weight for x in vertex.groups if group and x.group==group.index),0)
   if weight>=.35:
    wp=e.matrix_world@vertex.co;lp=wi@wp
    if lp.y>=.6*p.length:picked.append(wp);local.append(lp)
  report['skin_tip_proxies'][n]={'selected_vertices':len(picked),'method':'evaluated skin vertices, distal bone weight >= .35, bone-local Y >= .6 * bone length','bone_tail_world':v(rig.matrix_world@p.tail),'bone_length':p.length,'world_bbox':bb(picked) if picked else None,'bone_local_bbox':bb(local) if local else None,'radial_radius_90pct':None}
  if local:
   radii=sorted(math.sqrt(lp.x*lp.x+lp.z*lp.z) for lp in local);report['skin_tip_proxies'][n]['radial_radius_90pct']=radii[int(.9*(len(radii)-1))]
  for joint in [1,2]:
   bn=f'DEF-{finger}{joint}.{side}';pb=rig.pose.bones[bn];mx=rig.matrix_world@pb.matrix;x=mx.to_3x3().col[0].normalized();tip=rig.matrix_world@p.tail;pivot=rig.matrix_world@pb.head;der=x.cross(tip-pivot)
   fk=rig.pose.bones.get(f'FK-{finger}{joint}.{side}')
   report['curl_jacobians_current'][f'FK-{finger}{joint}.{side}']={'world_local_x_axis':v(x),'pivot_world':v(pivot),'d_tip_world_per_positive_radian_x':v(der),'d_tip_front_outward_m_per_radian':der.dot(Vector((0,-1,0))),'current_fk_euler_degrees':[math.degrees(a) for a in fk.rotation_euler] if fk else None,'sign_limit':'instantaneous sign at current pose only; recompute after hand frame changes'}
   if fk:report['fingers_constraints'][fk.name]=[{'name':c.name,'type':c.type} for c in fk.constraints]
e.to_mesh_clear()
# Actual source guitar points from the current object, kept in guitar local space.
pts=[p.co.copy() for p in g.data.vertices];adj=[[] for _ in pts]
for edge in g.data.edges:a,b=edge.vertices;adj[a].append(b);adj[b].append(a)
seen=set();strings=[]
for i in range(len(pts)):
 if i in seen:continue
 todo=[i];seen.add(i);idx=[]
 while todo:
  a=todo.pop();idx.append(a)
  for n in adj[a]:
   if n not in seen:seen.add(n);todo.append(n)
 dims=bb([pts[j] for j in idx])['dimensions']
 if dims[2]>.8 and dims[0]<.02:strings.append(set(idx))
def string_cross(z):
 ans=[]
 for ids in strings:
  pp=[]
  for edge in g.data.edges:
   a,b=edge.vertices
   if a not in ids or b not in ids:continue
   p,q=pts[a],pts[b]
   if (p.z-z)*(q.z-z)<=0 and abs(p.z-q.z)>1e-9:pp.append(p+(q-p)*((z-p.z)/(q.z-p.z)))
  if pp:ans.append(sum(pp,Vector())/len(pp))
 return sorted(ans,key=lambda p:p.x)
report['source_strings']={str(z):[v(p) for p in string_cross(z)] for z in [.32,.68]}
# One measured size correction: make the guitar body/hand ratio 40% larger, not modify hand scale.
s=.7;theta=math.radians(70);nx=Vector((math.cos(theta),0,-math.sin(theta)));nz=Vector((math.sin(theta),0,math.cos(theta)));front=Vector((0,-1,0));loc=Vector((-.7*math.sin(theta)*.5,-.254,.235));M=Matrix.Translation(loc)@Matrix.Rotation(theta,4,'Y')@Matrix.Diagonal((s,s,s,1));world=[M@p for p in pts]
report['guitar_candidate']={'scale':s,'neck_axis':v(nz),'cross_neck_axis':v(nx),'front_normal':v(front),'location':v(loc),'matrix_world':[list(r) for r in M],'all_bbox':bb(world),'body_bbox':bb([M@p for p in pts if p.z<.535]),'size_factor_vs_fix1':s/.5,'guitar_width_over_measured_cat_head_width':bb(world)['dimensions'][0]/.64223349}
tri=[tuple(t.vertices) for t in g.data.loop_triangles];g.data.calc_loop_triangles();tri=[tuple(t.vertices) for t in g.data.loop_triangles];tree=BVHTree.FromPolygons(world,tri,all_triangles=True)
def ray_surface(local,side):
 p=M@local;origin=p+front*(.15 if side=='front' else -.15);direction=-front if side=='front' else front;hit,n,idx,d=tree.ray_cast(origin,direction,.30);return {'point':v(hit) if hit else None,'normal':v(n) if n else None,'triangle':idx}
report['candidate_strings']={str(z):[v(M@p) for p in string_cross(z)] for z in [.32,.68]}
report['candidate_neck_surfaces']={side:ray_surface(Vector((0,0,.68)),side) for side in ['front','back']}
# Actual per-string surface rays from the guitar outward side; avoid confusing centerline with surface.
report['left_string_front_hits']=[ray_surface(p,'front') for p in string_cross(.68)]
report['right_string_front_hits']=[ray_surface(p,'front') for p in string_cross(.32)]
report['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==report['source_sha256_after'];out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'output':str(out),'skin_tip_proxies':report['skin_tip_proxies'],'candidate':report['guitar_candidate'],'neck':report['candidate_neck_surfaces']}))
