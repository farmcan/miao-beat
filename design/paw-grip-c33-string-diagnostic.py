"""Read-only actual third-string crossing segments in frozen C33; no geometry writes."""
import bpy,json,hashlib,itertools,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
root=Path(__file__).resolve().parents[1];out=root/'artifacts/character-paw-grip-c33';native=out/'diagnostic-c33-infeasible-or-collision.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nh=sha(native);O=Vector((-.1950536246756659,-.85,1.5567366254980208));GU=Vector((1.0169595357706245,0,.40048756408789304));GV=Vector((-.40048756408789304,0,1.0169595357706245));bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.view_layer.update();body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;me.calc_loop_triangles();tris=[t for t in me.loop_triangles if .75<me.polygons[t.polygon_index].center.x<1.62 and me.polygons[t.polygon_index].center.y<-.60 and 1.3<me.polygons[t.polygon_index].center.z<2.35];ht=BVHTree.FromPolygons([v.co[:] for v in me.vertices],[tuple(t.vertices) for t in tris],all_triangles=True);ob=bpy.data.objects['Guitar / string 3'];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());tube=ev.to_mesh();tube.calc_loop_triangles();tco=[ob.matrix_world@v.co for v in tube.vertices];tfs=[tuple(t.vertices) for t in tube.loop_triangles];tree=BVHTree.FromPolygons(tco,tfs,all_triangles=True);over=ht.overlap(tree);rows=[]
for ti,oi in over:
 tr=tris[ti];pp=[me.vertices[i].co.copy() for i in tr.vertices];qq=[tco[i] for i in tfs[oi]];points=[]
 for edges,triangle in [(pp,qq),(qq,pp)]:
  for a,b in zip(edges,edges[1:]+edges[:1]):
   length=(b-a).length
   if length<1e-12:continue
   dr=(b-a)/length;h=intersect_ray_tri(*triangle,dr,a,True)
   if h is not None and -1e-7<=(h-a).dot(dr)<=length+1e-7 and not any((h-x).length<1e-7 for x in points):points.append(h)
 span=max(((a-b).length for a,b in itertools.combinations(points,2)),default=0);center=sum(pp,Vector())/3;rows.append({'body_polygon':tr.polygon_index,'body_triangle_vertex_ids':list(tr.vertices),'string3_actual_evaluated_triangle':oi,'body_source_region':2 if me.attributes['C23 C11 upper face local id'].data[tr.polygon_index].value>0 else 1,'skin_triangle_center_world':list(center),'logical_U':(center-O).dot(GU)/GU.length_squared,'logical_V':(center-O).dot(GV)/GV.length_squared,'actual_intersection_points':[list(p) for p in points],'actual_intersection_segment_span':span,'confirmed_segment_over_1e_minus6':span>1e-6})
ev.to_mesh_clear();result={'stage':'C33-readonly-third-string-intersection-attribution','native_sha256':nh,'native_unchanged':sha(native)==nh,'actual_triangle_intersection_pairs':len(rows),'confirmed_crossing_segments_over_1e_minus6':sum(r['confirmed_segment_over_1e_minus6'] for r in rows),'unresolved_or_tangency_pairs':sum(not r['confirmed_segment_over_1e_minus6'] for r in rows),'maximum_confirmed_segment_span':max((r['actual_intersection_segment_span'] for r in rows),default=0),'rows':rows,'limits':['Segment span is not penetration depth; BVH pairs are not unique contact sites.','No ray U/V extrapolation, geometry change, art render or second candidate.']};(out/'string3-intersection-attribution.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT '+json.dumps({k:v for k,v in result.items() if k not in ['rows','limits']}))
