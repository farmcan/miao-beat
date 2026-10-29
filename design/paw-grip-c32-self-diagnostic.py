"""Read-only exact non-neighbor self-pair attribution for the frozen C29 candidate."""
import bpy,bmesh,json,hashlib,sys,itertools,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
root=Path(__file__).resolve().parents[1];out=root/'artifacts/character-paw-grip-c32';native=out/'diagnostic-c32-infeasible-or-collision.blend';source=root/'artifacts/character-paw-shared-surface-c25/miao-c25-shared-surface-diagnostic.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nh=sha(native);sh=sha(source);O=Vector((-.1950536246756659,-.85,1.5567366254980208));GU=Vector((1.0169595357706245,0,.40048756408789304));GV=Vector((-.40048756408789304,0,1.0169595357706245))
def uv(p):return {'U':(p-O).dot(GU)/GU.length_squared,'V':(p-O).dot(GV)/GV.length_squared,'Y':p.y}
def sid(me,f):return 2 if me.attributes['C23 C11 upper face local id'].data[f].value>0 else 0 if me.attributes['C23 source face id'].data[f].value>0 else 1
bpy.ops.wm.open_mainfile(filepath=str(native));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;chosen=[f for f in me.polygons if .75<f.center.x<1.62 and f.center.y<-.60 and 1.3<f.center.z<2.35];used=sorted({i for f in chosen for i in f.vertices});mp={v:i for i,v in enumerate(used)};local=bpy.data.meshes.new('C29 read-only self witness');local.from_pydata([me.vertices[i].co[:] for i in used],[],[[mp[i] for i in f.vertices] for f in chosen]);local.update();local.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(local);bm.faces.ensure_lookup_table();tree=BVHTree.FromBMesh(bm);pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not({v.index for v in bm.faces[a].verts}&{v.index for v in bm.faces[b].verts})];tri_by_face={}
for tri in local.loop_triangles:tri_by_face.setdefault(tri.polygon_index,[]).append([local.vertices[i].co.copy() for i in tri.vertices])
rows=[];counts={}
def face_geometry(face):
 pp=np.array([me.vertices[i].co[:] for i in face.vertices]);center=pp.mean(0);_,_,vh=np.linalg.svd(pp-center);return {'vertex_count':len(pp),'best_fit_plane_max_corner_distance':float(np.max(np.abs((pp-center)@vh[-1]))),'normal':list(face.normal)}
for a,b in pairs:
 fa,fb=chosen[a],chosen[b];points=[]
 for pp,qq in itertools.product(tri_by_face[a],tri_by_face[b]):
  for edges,triangle in [(pp,qq),(qq,pp)]:
   for start,end in zip(edges,edges[1:]+edges[:1]):
    length=(end-start).length
    if length<1e-12:continue
    dr=(end-start)/length;h=intersect_ray_tri(*triangle,dr,start,True)
    if h is not None and -1e-7<=(h-start).dot(dr)<=length+1e-7 and not any((h-q).length<1e-7 for q in points):points.append(h)
 length=max(((p-q).length for p,q in itertools.combinations(points,2)),default=0);regions=[sid(me,fa.index),sid(me,fb.index)];key='-'.join(str(i) for i in sorted(regions));counts[key]=counts.get(key,0)+1;rows.append({'local_pair':[a,b],'actual_body_polygons':[fa.index,fb.index],'source_regions':regions,'actual_face_geometry':[face_geometry(fa),face_geometry(fb)],'centers':[list(fa.center),list(fb.center)],'logical_centers':[uv(fa.center),uv(fb.center)],'actual_vertices':[list(fa.vertices),list(fb.vertices)],'actual_loop_triangle_intersection_points':[list(p) for p in points],'intersection_segment_span':length,'confirmed_segment_over_1e_minus6':length>1e-6})
bm.free();bpy.data.meshes.remove(local);actual_ids=sorted({f for row in rows for f in row['actual_body_polygons']});normals={f:me.polygons[f].normal.copy() for f in actual_ids};bpy.ops.wm.open_mainfile(filepath=str(source));me=bpy.data.objects['Miao / continuous pear and rounded-square face'].data
for row in rows:row['original_C25_face_centers']=[list(me.polygons[i].center) for i in row['actual_body_polygons']];row['current_vs_original_normal_dots']=[normals[i].dot(me.polygons[i].normal) for i in row['actual_body_polygons']]
r={'stage':'C32-readonly-self-intersection-attribution-no-new-candidate','native_sha256':nh,'C25_source_sha256':sh,'native_unchanged':sha(native)==nh,'source_unchanged':sha(source)==sh,'reported_non_neighbor_face_pairs':len(rows),'pair_source_region_counts':counts,'confirmed_actual_loop_triangle_segments_gt_1e_minus6':sum(q['confirmed_segment_over_1e_minus6'] for q in rows),'unconfirmed_or_tangency_count':sum(not q['confirmed_segment_over_1e_minus6'] for q in rows),'pairs':rows,'limits':['Pair counts are face-pairs, not collision sites.','Confirmed segment spans use actual saved loop triangles; unconfirmed BVH pairs remain unresolved, never silently called zero.','No geometry, constraints or targets were changed and no image was rendered.']};(out/'self-intersection-attribution.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps({k:v for k,v in r.items() if k not in ['pairs','limits']}))
