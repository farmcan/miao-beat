"""Read-only C27 failure attribution; no vertex modification, render or second candidate."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];out=root/'artifacts/character-paw-grip-c27';O=Vector((-.1950536246756659,-.85,1.5567366254980208));GU=Vector((1.0169595357706245,0,.40048756408789304));GV=Vector((-.40048756408789304,0,1.0169595357706245));V=GV.normalized();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def provenance(body,fi):return 2 if body.data.attributes['C23 C11 upper face local id'].data[fi].value>0 else 0 if body.data.attributes['C23 source face id'].data[fi].value>0 else 1
def logical_u(p):return (p-O).dot(GU)/GU.length_squared
def logical_v(p):return (p-O).dot(GV)/GV.length_squared
def worldtree(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear();return tree
sources=[('C25',root/'artifacts/character-paw-shared-surface-c25/miao-c25-shared-surface-diagnostic.blend'),('C27failed',out/'diagnostic-failed-contact-or-collision.blend')];prior=json.loads((root/'artifacts/character-paw-shared-surface-c25/contact-audit.json').read_text());rows=[]
for label,src in sources:
 before=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.view_layer.update();body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;me.calc_loop_triangles();faceids={f.index for f in me.polygons if .75<f.center.x<1.62 and f.center.y<-.60 and 1.3<f.center.z<2.35};triangles=[t for t in me.loop_triangles if t.polygon_index in faceids];ht=BVHTree.FromPolygons([v.co[:] for v in me.vertices],[tuple(t.vertices) for t in triangles],all_triangles=True);pairs=[]
 for name in ['Guitar / ebony fretboard','Guitar / neck']+['Guitar / string '+str(i+1) for i in range(6)]:
  gt=worldtree(bpy.data.objects[name]);over=ht.overlap(gt);sourcecounts={};samples=[]
  for ti,gi in over:
   tr=triangles[ti];sid=provenance(body,tr.polygon_index);sourcecounts[str(sid)]=sourcecounts.get(str(sid),0)+1
   if len(samples)<12:
    points=[me.vertices[i].co for i in tr.vertices];c=sum(points,Vector())/3;samples.append({'hand_actual_polygon':tr.polygon_index,'hand_triangle_vertices':list(tr.vertices),'source_region':sid,'triangle_centroid_world':list(c),'centroid_logical_U':logical_u(c),'centroid_logical_V':logical_v(c),'guitar_triangle':gi})
  pairs.append({'object':name,'actual_surface_triangle_intersections':len(over),'hand_face_provenance_counts':sourcecounts,'samples':samples})
 skin=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());supports=[]
 for old in prior['declared_hold_support_targets']:
  target=Vector(old['board_lower_edge_world']);origin=target+V*.08;h,n,fi,d=skin.ray_cast(origin,-V,.8);r={'u':old['u'],'same_actual_board_lower_edge_world':list(target),'old_origin_world':old['skin_ray_origin_world'],'diagnostic_origin_world':list(origin),'diagnostic_origin_rule':'Fixed actual board lower edge + .08u*V, outside expected supported skin; ray direction -V. No target changed.','hit':h is not None,'fallback_used':False}
  if h is not None:r.update(actual_skin_world=list(h),actual_normal=list(n),normal_dot_V=n.dot(V),source_region=provenance(body,fi),signed_actual_lower_edge_gap=(target-h).dot(V))
  supports.append(r)
 rows.append({'scene':label,'native_sha256':before,'native_unchanged':sha(src)==before,'actual_triangle_intersections':pairs,'support_ray_from_board_calibrated_origin':supports})
result={'stage':'C27-readonly-failure-attribution-not-new-candidate','scenes':rows,'limits':['No geometry written or second RBF candidate run.','The original strict failed receipt is preserved.','Recalibrated diagnostic ray fixes only the observer origin which became inside the deformed palm; target coordinates are unchanged.','Surface intersections and finite vertex parity probes, together, establish failure without claiming complete volume collision proof.']};(out/'readonly-failure-attribution.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT '+json.dumps([{'scene':r['scene'],'counts':[(x['object'],x['actual_surface_triangle_intersections']) for x in r['actual_triangle_intersections']],'support':[(x.get('signed_actual_lower_edge_gap'),x.get('normal_dot_V')) for x in r['support_ray_from_board_calibrated_origin']]} for r in rows]))
