"""Frozen known-failed C33: read-only crossing depth samples + internal gray views.
No geometry, solver, target or native save. Explicitly not a gate pass/delivery.
"""
import bpy,json,hashlib,itertools,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];out=root/'artifacts/character-paw-grip-c33';native=out/'diagnostic-c33-infeasible-or-collision.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nh=sha(native);rh=sha(out/'receipt.json');string=json.loads((out/'string3-intersection-attribution.json').read_text());selfrows=json.loads((out/'self-intersection-attribution.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.view_layer.update();s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;ob=bpy.data.objects['Guitar / string 3'];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());tube=ev.to_mesh();tube.calc_loop_triangles();tco=[ob.matrix_world@v.co for v in tube.vertices];tfs=[tuple(t.vertices) for t in tube.loop_triangles];tree=BVHTree.FromPolygons(tco,tfs,all_triangles=True);triangles=sorted({tuple(r['body_triangle_vertex_ids']) for r in string['rows']});directions=[Vector((0,1,0)),Vector((-.3664192855,0,.9304498434))];depthrows=[];tested=0
for ids in triangles:
 pp=[me.vertices[i].co.copy() for i in ids]
 for a in range(33):
  for b in range(33-a):
   weights=np.array([a/32,b/32,1-(a+b)/32]);point=sum((p*float(w) for p,w in zip(pp,weights)),Vector());tested+=1;near,n,fi,d=tree.find_nearest(point)
   if near is None or (point-near).dot(n)>=0:continue
   votes=[]
   for dr in directions:
    pos=point.copy();hits=0
    for k in range(8):
     h,nn,ff,dd=tree.ray_cast(pos,dr,2)
     if h is None:break
     hits+=1;pos=h+dr*1e-7
    votes.append(hits%2)
   if votes==[1,1]:depthrows.append({'body_triangle_vertices':list(ids),'barycentric':weights.tolist(),'actual_skin_sample_world':list(point),'actual_nearest_tube_world':list(near),'actual_nearest_tube_normal':list(n),'actual_nearest_tube_triangle':fi,'actual_distance_to_tube_surface':d,'inside_two_radial_parity_votes':votes})
ev.to_mesh_clear();depthrows.sort(key=lambda r:r['actual_distance_to_tube_surface'],reverse=True);planes=[];me.calc_loop_triangles()
for row in selfrows['pairs']:
 f1,f2=row['actual_body_polygons'];tt1=[t for t in me.loop_triangles if t.polygon_index==f1];tt2=[t for t in me.loop_triangles if t.polygon_index==f2];proxies=[]
 for ta,tb in itertools.product(tt1,tt2):
  A=np.array([me.vertices[i].co[:] for i in ta.vertices]);B=np.array([me.vertices[i].co[:] for i in tb.vertices]);nb=np.cross(B[1]-B[0],B[2]-B[0]);nb/=np.linalg.norm(nb);na=np.cross(A[1]-A[0],A[2]-A[0]);na/=np.linalg.norm(na);da=(A-B[0])@nb;db=(B-A[0])@na;proxies.append({'triangle_vertex_ids':[list(ta.vertices),list(tb.vertices)],'A_vertices_signed_distance_to_B_plane':da.tolist(),'B_vertices_signed_distance_to_A_plane':db.tolist()})
 planes.append({'actual_body_polygons':[f1,f2],'actual_intersection_span':row['intersection_segment_span'],'signed_plane_straddle_proxies':proxies,'limit':'Plane straddles are geometric signed distances, not a unique solid penetration depth for two zero-thickness self surfaces.'})
depth={'stage':'C33-readonly-actual-tube-penetration-depth-samples','native_sha256':nh,'actual_string3_evaluated_triangle_geometry':True,'skin_triangles_sampled':len(triangles),'barycentric_grid_subdivision':32,'skin_samples_tested':tested,'confirmed_inside_tube_samples':len(depthrows),'maximum_observed_inside_distance_to_actual_tube_surface':depthrows[0]['actual_distance_to_tube_surface'] if depthrows else None,'deepest_confirmed_samples':depthrows[:30],'self_plane_straddles':planes,'limits':['Maximum observed distance is sampled evidence, not an analytic global maximum.','Actual nearest tube triangle and two radial parity rays confirm sampled inside points; no primitive tube radius substitutes actual geometry.','All known gate failures remain.']};(out/'penetration-depth-diagnostic.json').write_text(json.dumps(depth,indent=2)+'\n')
# Parent authorization is diagnostic-only and explicitly preserves all failures.
s.cycles.samples=16;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;cam=s.camera;fl=cam.location.copy();fr=cam.rotation_euler.copy();scale=cam.data.ortho_scale
for view in ['front','inside']:
 if view=='inside':cam.location=(4,-6,3);cam.rotation_euler=(Vector((1.17,-.95,1.96))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25
 s.render.filepath=str(out/('internal-diagnostic-gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
cam.location=fl;cam.rotation_euler=fr;cam.data.ortho_scale=scale;assert sha(native)==nh and sha(out/'receipt.json')==rh;result={'stage':'C33-known-failed-frozen-native-internal-diagnostic-images','authorization':'Parent explicitly authorized internal front/inside views of the same last frozen C33 native after real failure attribution; no geometry/art/contact pass or public delivery.','native_sha256':nh,'native_unchanged':True,'strict_failure_receipt_sha256':rh,'strict_failure_receipt_unchanged':True,'geometry_changed':False,'model_saved':False,'geometry_gate_passed':False,'art_gate_passed':False,'contact_gate_passed':False,'known_remaining_failures':['1 non-neighbor upper polygon self pair, actual loop-triangle crossing confirmed','8 actual third-string triangle crossing pairs, all actual segment confirmed','Actual ray upper-bound overshoot ~1.6e-7u separately recorded, not the real crossing blocker'],'files':['internal-diagnostic-gray-front.png','internal-diagnostic-gray-inside.png']};(out/'internal-diagnostic-render.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT '+json.dumps({'tube_inside_samples':len(depthrows),'max_sampled_depth':depth['maximum_observed_inside_distance_to_actual_tube_surface'],'self_span':[x['actual_intersection_span'] for x in planes],'native_unchanged':True,'receipt_unchanged':True,'images_are_internal_failed_diagnostics':True}))
