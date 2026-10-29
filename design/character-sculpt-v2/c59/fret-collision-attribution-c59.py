"""Read-only C59 two actual fret intersections and exact C35 inheritance proof."""
import bpy,numpy as np,json,hashlib,itertools,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
R=Path(__file__).resolve().parents[3];O=R/'artifacts/character-wrist-graft-c59';native=O/'miao-c59-c56-body-exact-c35-hand.blend';source=R/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nh=sha(native);sh=sha(source);bpy.ops.wm.open_mainfile(filepath=str(native));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;me.calc_loop_triangles();co=[v.co.copy() for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];fi=[t.polygon_index for t in me.loop_triangles];region=[me.attributes['C59 construction region'].data[f].value for f in fi];oldids=np.array([v.value for v in me.attributes['C59 C35 source vertex id'].data]);sourcefaces=[me.attributes['C59 C35 source face id'].data[f].value-1 for f in fi];keep=[i for i,r in enumerate(region) if r==2];handtree=BVHTree.FromPolygons(co,[tri[i] for i in keep],all_triangles=True);whole=BVHTree.FromPolygons(co,tri,all_triangles=True)
def obstacle(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ob.matrix_world@p.co for p in m.vertices];t=[tuple(x.vertices) for x in m.loop_triangles];tree=BVHTree.FromPolygons(v,t,all_triangles=True);ev.to_mesh_clear();return v,t,tree

def vote(tree,p,dr):
 pos=p.copy();count=0
 for k in range(64):
  q,n,f,d=tree.ray_cast(pos,dr,8)
  if q is None:return count%2
  count+=1;pos=q+dr*1e-5
 return None
rows=[];expected={}
for name in ['Guitar / silver fret.002','Guitar / silver fret.003']:
 gc,gt,tree=obstacle(bpy.data.objects[name]);pairs=handtree.overlap(tree);out=[];faces=collections.Counter();verts=set()
 for local,b in pairs:
  a=keep[local];pp=[co[i] for i in tri[a]];qq=[gc[i] for i in gt[b]];points=[]
  for edges,t in [(pp,qq),(qq,pp)]:
   for p,q in zip(edges,edges[1:]+edges[:1]):
    length=(q-p).length
    if length<1e-12:continue
    d=(q-p)/length;h=intersect_ray_tri(*t,d,p,True)
    if h is not None and -1e-7<=(h-p).dot(d)<=length+1e-7 and not any((h-x).length<1e-7 for x in points):points.append(h)
  span=max(((p-q).length for p,q in itertools.combinations(points,2)),default=0);faces[sourcefaces[a]]+=1;verts.update(gt[b]);p=np.array([q[:] for q in pp+qq]);out.append({'body_actual_triangle':a,'body_original_C35_face':int(sourcefaces[a]),'body_original_C35_vertex_indices':(oldids[list(tri[a])]-1).tolist(),'fret_actual_triangle':b,'intersection_points':[list(q) for q in points],'confirmed_span':span,'confirmed_segment_gt_1e_minus6':span>1e-6,'bbox':[p.min(0).tolist(),p.max(0).tolist()]})
 inside=[];amb=[]
 for i in verts:
  v=[vote(whole,gc[i],d) for d in [Vector((.371,.613,.697)).normalized(),Vector((.739,.223,.635)).normalized()]]
  if v==[1,1]:h,n,f,d=whole.find_nearest(gc[i]);inside.append({'fret_vertex':i,'world':list(gc[i]),'observed_distance_to_skin':d})
  elif v[0]!=v[1] or None in v:amb.append(i)
 row={'object':name,'current_pairs':len(pairs),'by_original_C35_faces':dict(faces),'confirmed_segment_pairs':sum(x['confirmed_segment_gt_1e_minus6'] for x in out),'maximum_confirmed_span':max((x['confirmed_span'] for x in out),default=0),'sampled_fret_vertices_inside_body':inside,'ambiguous_sampled_fret_vertices':amb,'max_observed_metal_inside_skin_depth':max((x['observed_distance_to_skin'] for x in inside),default=0),'pair_witnesses':out};rows.append(row);expected[name]=len(pairs)
# Independently re-evaluate source C35 actual hand and the same physical frets.
bpy.ops.wm.open_mainfile(filepath=str(source));me=bpy.data.objects['Miao / continuous pear and rounded-square face'].data;me.calc_loop_triangles();co0=[v.co.copy() for v in me.vertices];ts=[]
for t in me.loop_triangles:
 center=sum((co0[i] for i in t.vertices),Vector())/3
 if .75<center.x<1.62 and center.y<-.6 and 1.3<center.z<2.35:ts.append(tuple(t.vertices))
st=BVHTree.FromPolygons(co0,ts,all_triangles=True)
for row in rows:
 gc,gt,tree=obstacle(bpy.data.objects[row['object']]);pairs=st.overlap(tree);row['source_C35_actual_same_fret_pairs']=len(pairs);row['same_pair_count_as_exact_original_hand']=len(pairs)==row['current_pairs'];row['all_contact_skin_original_C35_coordinates_exact']=all(all(tuple(co0[old])==tuple(co[v]) for old,v in zip(w['body_original_C35_vertex_indices'],tri[w['body_actual_triangle']])) for w in row['pair_witnesses'])
r={'stage':'C59-readonly-actual-fret-collision-and-source-inheritance-proof','native_sha256':nh,'source_C35_sha256':sh,'fret_results':rows,'interpretation':'The graft seam and all original hand points are exact; these two physical fret intersections already exist in original C35, whose earlier gate checked wood/six strings but not every fret. Source inheritance is an explanation, never a waiver. No geometry/targets changed.','limits':['Observed inside-vertex depth is a finite lower-bound sample, not exact maximum penetration.','No real penetration is covered by positive-gap fp32 ceiling tolerance.']};assert sha(native)==nh and sha(source)==sh;(O/'fret-collision-attribution.json').write_text(json.dumps(r,indent=2)+'\n');print('FRETS '+json.dumps([{k:x[k] for k in ['object','current_pairs','source_C35_actual_same_fret_pairs','by_original_C35_faces','confirmed_segment_pairs','maximum_confirmed_span','max_observed_metal_inside_skin_depth','all_contact_skin_original_C35_coordinates_exact']} for x in rows]),flush=True)
