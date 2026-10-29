"""Read-only geometric attribution of the75 C52 actual-BVH body self pairs."""
import bpy,numpy as np,json,hashlib,itertools,collections
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
R=Path(__file__).resolve().parents[3];O=R/'artifacts/character-body-voxel-c52';native=O/'miao-c52-whole-body-voxel-authoring-study.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nh=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));me=bpy.data.objects['Miao / continuous pear and rounded-square face'].data;me.calc_loop_triangles();co=[v.co.copy() for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];fi=[t.polygon_index for t in me.loop_triangles];tree=BVHTree.FromPolygons(co,tri,all_triangles=True);pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not(set(tri[a])&set(tri[b]))];rows=[];parent={}
def find(a):
 parent.setdefault(a,a)
 if parent[a]!=a:parent[a]=find(parent[a])
 return parent[a]
def union(a,b):parent[find(a)]=find(b)
for a,b in pairs:
 points=[];pp=[co[i] for i in tri[a]];qq=[co[i] for i in tri[b]]
 for edges,t in [(pp,qq),(qq,pp)]:
  for start,end in zip(edges,edges[1:]+edges[:1]):
   length=(end-start).length
   if length<1e-12:continue
   dr=(end-start)/length;hit=intersect_ray_tri(*t,dr,start,True)
   if hit is not None and -1e-7<=(hit-start).dot(dr)<=length+1e-7 and not any((hit-p).length<1e-7 for p in points):points.append(hit)
 span=max(((p-q).length for p,q in itertools.combinations(points,2)),default=0);vertices=sorted(set(tri[a])|set(tri[b]));p=np.array([co[i][:] for i in vertices]);
 for i in vertices[1:]:union(vertices[0],i)
 geometry=[]
 for faceid in [fi[a],fi[b]]:
  f=me.polygons[faceid];v=np.array([co[i][:] for i in f.vertices]);_,_,vh=np.linalg.svd(v-v.mean(0));geometry.append({'polygon':faceid,'corners':len(f.vertices),'max_nonplanarity':float(np.max(np.abs((v-v.mean(0))@vh[-1])))})
 rows.append({'actual_triangles':[a,b],'actual_polygons':[fi[a],fi[b]],'vertex_ids':vertices,'bbox':[p.min(0).tolist(),p.max(0).tolist()],'confirmed_edge_triangle_segment_span':span,'segment_over_1e_minus6':span>1e-6,'intersection_points':[list(p) for p in points],'face_geometry':geometry})
groups=collections.defaultdict(list)
for j,row in enumerate(rows):groups[find(row['vertex_ids'][0])].append(j)
clusters=[]
for ids in groups.values():
 vertices=sorted({v for j in ids for v in rows[j]['vertex_ids']});p=np.array([co[i][:] for i in vertices]);clusters.append({'pair_count':len(ids),'pair_indices':ids,'bbox':[p.min(0).tolist(),p.max(0).tolist()],'max_confirmed_intersection_span':max(rows[j]['confirmed_edge_triangle_segment_span'] for j in ids)})
r={'scope':'Read-only75pair attribution, no sculpt/remesh/resolution change','native_sha256_before_after':nh,'actual_body_triangle_self_pairs':len(rows),'confirmed_segment_over_1e_minus6':sum(row['segment_over_1e_minus6'] for row in rows),'unconfirmed_or_tangency_count':sum(not row['segment_over_1e_minus6'] for row in rows),'clusters':clusters,'pairs':rows,'new_candidate_applied':False,'no_native_mutation':sha(native)==nh};assert r['no_native_mutation'];(O/'self-pair-attribution.json').write_text(json.dumps(r,indent=2)+'\n');print('ATTRIBUTION '+json.dumps({k:r[k] for k in ['actual_body_triangle_self_pairs','confirmed_segment_over_1e_minus6','unconfirmed_or_tangency_count','clusters']}),flush=True)
