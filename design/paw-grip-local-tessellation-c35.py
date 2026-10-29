"""C35 finite local tessellation of three identified nonplanar quads.
All original vertex coordinates fixed; 8 exact diagonal combinations, no pose search.
"""
import bpy,bmesh,numpy as np,json,sys,hashlib,itertools,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import interpolate_bezier,intersect_ray_tri
root=Path(__file__).resolve().parents[1];out=root/'artifacts/character-paw-grip-c35';out.mkdir(exist_ok=True);src=root/'artifacts/character-paw-grip-c33/diagnostic-c33-infeasible-or-collision.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source_sha=sha(src);sys.path.insert(0,str(root/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
helper=root/'design/character-sculpt-v2/paw-grip-contact-c27.py';h=helper.read_text();exec(compile(h[h.index('O=Vector'):h.index('def main():')],str(helper)+'#actual-only-functions','exec'),globals());oldtargets=targets

def actual_targets(body):
 rows=oldtargets(body);tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
 for row in rows:
  if row['kind']!='support':continue
  pt=Vector(row['actual_target_world']);origin=pt+V*.08;hit,n,fi,d=tree.ray_cast(origin,-V,.8);row.update(ray_origin=list(origin),ray_origin_rule='actual board lower edge + .08u V',hit=hit is not None)
  if hit is not None:row.update(face_index=fi,source=provenance(body,fi),skin=list(hit),normal=list(n),normal_condition=n.dot(V),gap=(pt-hit).dot(V))
 return rows

def main():
 started=time.time();bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.view_layer.update();body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;scene=bpy.context.scene;original=np.array([v.co[:] for v in me.vertices]);beforetopo=topo(body);beforetargets=actual_targets(body);face_ids=[590434,590446,590443];quads={i:list(me.polygons[i].vertices) for i in face_ids};assert all(len(q)==4 for q in quads.values());me.calc_loop_triangles();localfaces=[f for f in me.polygons if .75<f.center.x<1.62 and f.center.y<-.60 and 1.3<f.center.z<2.35];localids={f.index for f in localfaces};other=[(tuple(t.vertices),t.polygon_index) for t in me.loop_triangles if t.polygon_index in localids and t.polygon_index not in face_ids];base_triangles={i:[tuple(t.vertices) for t in me.loop_triangles if t.polygon_index==i] for i in face_ids};patterns={}
 for i,q in quads.items():patterns[i]=[[tuple([q[0],q[1],q[2]]),tuple([q[0],q[2],q[3]])],[tuple([q[1],q[2],q[3]]),tuple([q[1],q[3],q[0]])]]
 baseline_pattern={i:next(k for k in [0,1] if {frozenset(t) for t in patterns[i][k]}=={frozenset(t) for t in base_triangles[i]}) for i in face_ids};quad_geometry={}
 for i,q in quads.items():
  pp=original[q];c=pp.mean(0);_,_,vh=np.linalg.svd(pp-c);quad_geometry[i]={'vertex_ids':q,'baseline_actual_diagonal_pattern':baseline_pattern[i],'baseline_actual_loop_triangles':[list(t) for t in base_triangles[i]],'best_fit_plane_max_corner_distance':float(np.max(np.abs((pp-c)@vh[-1]))),'source_attributes':{attr.name:int(attr.data[i].value) for attr in me.attributes if attr.domain=='FACE' and attr.data_type in {'INT','BOOLEAN'}},'material_index':me.polygons[i].material_index,'smooth':me.polygons[i].use_smooth}
 obstacles={name:worldtree(bpy.data.objects[name])[0] for name in ['Guitar / ebony fretboard','Guitar / neck']+['Guitar / string '+str(i+1) for i in range(6)]};records=[];selected=None;coords=[Vector(p) for p in original];positive_tol=2.5e-7
 def topology_targets(tree,tris):
  results=[]
  for old in beforetargets:
   pt=Vector(old['actual_target_world']);axis=Vector((0,-1,0)) if old['kind']=='toe' else -V;origin=Vector((pt.x,-.88,pt.z)) if old['kind']=='toe' else pt+V*.08;hit,n,ti,d=tree.ray_cast(origin,axis,1.5 if old['kind']=='toe' else .8);r={'kind':old['kind'],'u':old['u'],'target_world':old['actual_target_world'],'hit':hit is not None,'expected_source':old['expected_source'],'fallback_used':False}
   if hit is not None:
    fi=tris[ti][1];gap=pt.y-old['radius']-hit.y if old['kind']=='toe' else (pt-hit).dot(V);r.update(source=provenance(body,fi),source_original_polygon=fi,actual_hit_world=list(hit),normal=list(n),normal_condition=n.y if old['kind']=='toe' else n.dot(V),gap=gap)
   results.append(r)
  return results
 combos=list(itertools.product([0,1],repeat=3));combos.sort(key=lambda c:(sum(c[j]!=baseline_pattern[i] for j,i in enumerate(face_ids)),c))
 for order,combo in enumerate(combos):
  tris=other+[(t,i) for i,k in zip(face_ids,combo) for t in patterns[i][k]];legal=True;minimum_dot=1.
  for i,k in zip(face_ids,combo):
   oldnormal=np.array(me.polygons[i].normal)
   for tri in patterns[i][k]:
    pp=original[list(tri)];cross=np.cross(pp[1]-pp[0],pp[2]-pp[0]);length=np.linalg.norm(cross)
    if length<1e-12:legal=False;continue
    dot=float((cross/length)@oldnormal);minimum_dot=min(minimum_dot,dot);legal&=True
  if not legal:records.append({'order':order,'combo':list(combo),'legal':False,'minimum_triangle_vs_original_quad_normal_dot':minimum_dot});continue
  tree=BVHTree.FromPolygons(coords,[t for t,i in tris],all_triangles=True);selfpairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not(set(tris[a][0])&set(tris[b][0]))];cross={name:len(tree.overlap(gt)) for name,gt in obstacles.items()};rays=topology_targets(tree,tris);nominal=all(r['hit'] and r.get('source')==r['expected_source'] and r.get('normal_condition',-1)>.2 and 0<=r.get('gap',-1)<=.002 for r in rays);roundoff=all(r['hit'] and r.get('source')==r['expected_source'] and r.get('normal_condition',-1)>.2 and 0<=r.get('gap',-1)<=.002+positive_tol for r in rays);passed=not selfpairs and not any(cross.values()) and roundoff;rec={'order':order,'combo':list(combo),'legal':True,'diagonal_changes':sum(k!=baseline_pattern[i] for i,k in zip(face_ids,combo)),'minimum_triangle_vs_original_quad_normal_dot':minimum_dot,'actual_skin_triangle_self_pairs':len(selfpairs),'actual_guitar_triangle_intersections':cross,'actual_fixed_target_rays':rays,'strict_nominal_contact_band_pass':nominal,'authorized_positive_gap_roundoff_pass':roundoff,'eligible':passed};records.append(rec)
  if selected is None and passed:selected=rec
 (out/'finite-topology-combinations.json').write_text(json.dumps({'source_native_sha256':source_sha,'original_three_quads':quad_geometry,'ordering':'Fewest changed baseline diagonals, then lexicographic; all 8 legal combinations evaluated, one selected only if actual self/tube/wood0 and fixed ray/normal/source tests pass.','positive_gap_roundoff_authorization':{'nominal':[0,.002],'positive_only_fp32_tolerance':positive_tol,'no_real_penetration_or_self_tolerance':True},'combinations':records,'selected':selected},indent=2)+'\n');print('COMBOS '+json.dumps([{'c':r['combo'],'self':r.get('actual_skin_triangle_self_pairs'),'cross':r.get('actual_guitar_triangle_intersections'),'contact':r.get('authorized_positive_gap_roundoff_pass'),'eligible':r.get('eligible')} for r in records]),flush=True)
 if selected is None:
  receipt={'stage':'C35-three-quad-finite-tessellation-no-eligible-combination','source_native_sha256':source_sha,'source_unchanged':sha(src)==source_sha,'original_vertices_bit_exact':True,'geometry_candidate_applied':False,'render_gate_passed':False,'next':'Local bilinear subdivision required; no global deformation/target movement.'};(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('STOP no valid diagonal combination; no image');return
 # Apply explicit rendered triangles, preserving every original vertex and face data.
 bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();original_tag=bm.faces.layers.int.new('C35 original polygon id')
 for f in bm.faces:f[original_tag]=f.index+1
 face_refs={i:bm.faces[i] for i in face_ids};int_layers={name:bm.faces.layers.int.get(name) for name in bm.faces.layers.int.keys()};float_layers={name:bm.faces.layers.float.get(name) for name in bm.faces.layers.float.keys()};string_layers={name:bm.faces.layers.string.get(name) for name in bm.faces.layers.string.keys()};applied=[]
 for i,k in zip(face_ids,selected['combo']):
  f=face_refs[i];corners=list(f.verts);iv={name:f[layer] for name,layer in int_layers.items()};fv={name:f[layer] for name,layer in float_layers.items()};sv={name:f[layer] for name,layer in string_layers.items()};material=f.material_index;smooth=f.smooth;bm.faces.remove(f);local_patterns=[[(0,1,2),(0,2,3)],[(1,2,3),(1,3,0)]]
  for indices in local_patterns[k]:
   nf=bm.faces.new([corners[j] for j in indices]);nf.material_index=material;nf.smooth=smooth
   for name,layer in int_layers.items():nf[layer]=iv[name]
   for name,layer in float_layers.items():nf[layer]=fv[name]
   for name,layer in string_layers.items():nf[layer]=sv[name]
   applied.append({'source_original_polygon':i,'pattern':k,'vertex_ids':[v.index for v in nf.verts],'int_face_attributes':iv,'material_index':material,'smooth':smooth})
 bm.to_mesh(me);bm.free();me.update();actual=np.array([v.co[:] for v in me.vertices]);exact=bool(np.array_equal(actual,original));assert exact;finaltopo=topo(body);assert finaltopo['vertices']==beforetopo['vertices'] and finaltopo['faces']==beforetopo['faces']+3 and finaltopo['components']==1 and finaltopo['boundary_edges']==0 and finaltopo['non_manifold_edges']==0
 new_target=actual_targets(body);worldfixed=all(np.array_equal(r['actual_target_world'],q['actual_target_world']) for r,q in zip(beforetargets,new_target));nominal=all(r['hit'] and r['source']==r['expected_source'] and r['normal_condition']>.2 and 0<=r['gap']<=.002 for r in new_target);raypass=all(r['hit'] and r['source']==r['expected_source'] and r['normal_condition']>.2 and 0<=r['gap']<=.002+positive_tol for r in new_target);localfaces=[f for f in me.polygons if .75<f.center.x<1.62 and f.center.y<-.60 and 1.3<f.center.z<2.35];audit=collision_audit(body,localfaces);source=np.array([r.value>0 for r in me.attributes['C23 source vertex id'].data]);parity=solid_probes(body,np.flatnonzero(~source).tolist());local=audit['local_audit'];collision=all(q.get('surface_intersection_pairs',1)==0 for q in audit['guitar_surface_intersections']) and all(q['inside_by_two_independent_parity_rays']==0 and q['ambiguous_ray_votes']==0 for q in parity);attribute_checks=[]
 for i in face_ids:
  actual_faces=[f for f in me.polygons if me.attributes['C35 original polygon id'].data[f.index].value==i+1];check={'original_polygon':i,'new_triangle_count':len(actual_faces),'materials_preserved':all(f.material_index==quad_geometry[i]['material_index'] for f in actual_faces),'face_int_attributes_preserved':all(all(int(me.attributes[name].data[f.index].value)==value for name,value in quad_geometry[i]['source_attributes'].items()) for f in actual_faces)};attribute_checks.append(check)
 attrs_pass=all(c['new_triangle_count']==2 and c['materials_preserved'] and c['face_int_attributes_preserved'] for c in attribute_checks);passed=exact and worldfixed and raypass and collision and attrs_pass and local['self_intersections']==0 and local['flipped_faces']==0
 receipt={'stage':'C35-three-fixed-quads-explicit-tessellation','source_C33_native_sha256':source_sha,'source_C33_unchanged':sha(src)==source_sha,'script_sha256':sha(__file__),'selected_finite_combo':selected,'all_original_vertices_bit_exact':exact,'maximum_original_vertex_displacement':float(np.linalg.norm(actual-original,axis=1).max()),'only_three_quad_faces_replaced_by_explicit_triangles':face_ids,'applied_triangles':applied,'face_attribute_checks':attribute_checks,'before_topology':beforetopo,'final_topology':finaltopo,'fixed_world_targets_unchanged':worldfixed,'before_actual_target_rays':beforetargets,'after_actual_target_rays':new_target,'strict_nominal_contact_band_pass':nominal,'authorized_positive_gap_roundoff_pass':raypass,'positive_only_roundoff_limit':positive_tol,'roundoff_scope':'Nominal gap [0,.002] plus 2.5e-7u only for positive fp32 ceiling error, authorized parent; no wood/tube/self crossing tolerance.','actual_geometry_audit':audit,'wood_parity_probes':parity,'actual_wood_and_six_tube_collision_pass':collision,'render_gate_passed':passed,'seconds_before_render':time.time()-started,'limits':['Engineering gate and fixed-target ray pass are not independent art approval.','No changes to C33 vertices, whole-hand proportions, targets, QP weights or U bounds.','UV/groom/shape binding invalid after topology changes; no rig/animation/color/engine/deploy.']};bpy.context.preferences.filepaths.save_version=0;native=out/('miao-c35-fixed-vertex-tessellation.blend' if passed else 'diagnostic-c35-final-gate-failed.blend');bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);receipt['native_sha256']=sha(native);(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('RESULT '+json.dumps({'passed':passed,'self':local['self_intersections'],'flipped':local['flipped_faces'],'rays':[r['gap'] for r in new_target],'strict_contact':nominal,'positive_roundoff_contact':raypass,'wood_tubes':collision,'attrs':attrs_pass,'native':receipt['native_sha256']}),flush=True)
 if not passed:return
 scene.cycles.samples=16;scene.cycles.seed=17;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.use_border=False;scene.render.use_crop_to_border=False;cam=scene.camera;fl=cam.location.copy();fr=cam.rotation_euler.copy();scale=cam.data.ortho_scale
 for view in ['front','inside']:
  if view=='inside':cam.location=(4,-6,3);cam.rotation_euler=(Vector((1.17,-.95,1.96))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25
  scene.render.filepath=str(out/('gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
 cam.location=fl;cam.rotation_euler=fr;cam.data.ortho_scale=scale;assert sha(src)==source_sha
main()
