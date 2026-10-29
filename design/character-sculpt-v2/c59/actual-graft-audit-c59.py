"""C59 frozen post-image actual full-body self and current grip/instrument audit.
No geometry edits, inherited pass, target relocation or material/scene changes.
"""
import bpy,bmesh,numpy as np,json,hashlib,sys,time,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import interpolate_bezier,intersect_ray_tri
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/character-wrist-graft-c59';NATIVE=OUT/'miao-c59-c56-body-exact-c35-hand.blend';BODY=ROOT/'artifacts/character-ear-sculpt-c56/gray-material-consistency/miao-c56-gray-skin-consistent.blend';HAND=ROOT/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
h=ROOT/'design/character-sculpt-v2/paw-grip-contact-c27.py';s=h.read_text();exec(compile(s[s.index('O=Vector'):s.index('def main():')],str(h)+'#actual-geometry-functions','exec'),globals())
def actual_targets(body):
 rows=targets(body);tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
 for row in rows:
  if row['kind']!='support':continue
  pt=Vector(row['actual_target_world']);origin=pt+V*.08;hit,n,fi,d=tree.ray_cast(origin,-V,.8);row.update(ray_origin=list(origin),ray_origin_rule='Actual board lower edge +.08V, fixed C35 engineering target',hit=hit is not None)
  if hit is not None:row.update(face_index=fi,source=provenance(body,fi),skin=list(hit),normal=list(n),normal_condition=n.dot(V),gap=(pt-hit).dot(V))
 return rows

def main():
 start=time.time();hashes={'native':sha(NATIVE),'source_body':sha(BODY),'source_hand':sha(HAND)};bpy.ops.wm.open_mainfile(filepath=str(NATIVE));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;me.calc_loop_triangles();co=[v.co.copy() for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];fid=[t.polygon_index for t in me.loop_triangles];regions=np.array([me.attributes['C59 construction region'].data[i].value for i in fid]);tree=BVHTree.FromPolygons(co,tri,all_triangles=True);selfpairs=[]
 for a,b in tree.overlap(tree):
  if a>=b or set(tri[a])&set(tri[b]):continue
  selfpairs.append({'triangles':[a,b],'polygons':[fid[a],fid[b]],'regions':[int(regions[a]),int(regions[b])]})
 print('GLOBAL_ACTUAL_SELF '+str(len(selfpairs)),flush=True);localtri=[];localindices=[]
 for i,t in enumerate(tri):
  center=sum((co[v] for v in t),Vector())/3
  if regions[i] in [2,3] or(.75<center.x<1.62 and center.y<-.60 and 1.3<center.z<2.35):localtri.append(t);localindices.append(i)
 localtree=BVHTree.FromPolygons(co,localtri,all_triangles=True);surface=[]
 for ob in bpy.data.objects:
  if not ob.name.startswith('Guitar /') or ob.type not in {'MESH','CURVE'} or ob.hide_render:continue
  gt,nv,nt=worldtree(ob);glob=tree.overlap(gt);local=localtree.overlap(gt);counts=collections.Counter(int(regions[a]) for a,b in glob);surface.append({'object':ob.name,'actual_evaluated_vertices':nv,'actual_evaluated_triangles':nt,'complete_body_surface_pairs':len(glob),'whole_pairs_by_region_1retained_2oldHand_3band':dict(counts),'left_grip_band_and_proximal_collar_surface_pairs':len(local),'left_sample_actual_body_triangles':[localindices[a] for a,b in local[:15]]})
 print('GUITAR_NONZERO '+json.dumps([r for r in surface if r['complete_body_surface_pairs'] or r['left_grip_band_and_proximal_collar_surface_pairs']]),flush=True)
 # Local left grip/band solid probes complement actual surface tests. Global
 # source-body positive wood intersections are separately reported, never waived.
 localverts=sorted({v for t in localtri for v in t});dirs=[Vector((.371,.613,.697)).normalized(),Vector((.739,.223,.635)).normalized()];parity=[]
 def vote(tree,p,dr):
  pos=p.copy();count=0
  for k in range(32):
   h,n,f,d=tree.ray_cast(pos,dr,8)
   if h is None:return count%2
   count+=1;pos=h+dr*1e-5
  return None
 for name in ['Guitar / spruce soundboard','Guitar / rosewood body','Guitar / neck','Guitar / ebony fretboard']:
  gt,nv,nt=worldtree(bpy.data.objects[name]);inside=[];amb=[]
  for i in localverts:
   votes=[vote(gt,co[i],d) for d in dirs]
   if votes==[1,1]:inside.append(i)
   elif votes[0]!=votes[1] or None in votes:amb.append(i)
  parity.append({'object':name,'left_skin_points_tested':len(localverts),'inside':len(inside),'ambiguous':len(amb),'inside_sample':inside[:20],'ambiguous_sample':amb[:20]})
 rays=actual_targets(body);source_rows=json.load(open(ROOT/'artifacts/character-paw-grip-c35/receipt.json'))['after_actual_target_rays'];fixed=all(np.array_equal(r['actual_target_world'],q['actual_target_world']) for r,q in zip(rays,source_rows));nominal=True;roundoff=True;tol=2.5e-7
 for r,old in zip(rays,source_rows):
  if r['hit']:
   r['actual_C35_input_face_index']=int(me.attributes['C59 C35 source face id'].data[r['face_index']].value)-1;r['same_source_contact_face']=r['actual_C35_input_face_index']==old['face_index'];r['gap_delta_from_actual_source_C35']=float(r['gap']-old['gap'])
  else:r['same_source_contact_face']=False
  base=r['hit'] and r.get('source')==r['expected_source'] and r.get('normal_condition',-1)>.2 and r['same_source_contact_face'];nominal&=base and 0<=r.get('gap',-1)<=.002;roundoff&=base and 0<=r.get('gap',-1)<=.002+tol
 bm=bmesh.new();bm.from_mesh(me);bad=0
 for e in bm.edges:
  if len(e.link_faces)==2:
   a,b=e.link_faces;la=next(l for l in e.link_loops if l.face==a);lb=next(l for l in e.link_loops if l.face==b)
   if la.vert==lb.vert:bad+=1
 volume=bm.calc_volume(signed=True);bm.free();top=topo(body);top['euler']=top['vertices']-len(me.edges)+top['faces'];pp=np.array([p[:] for p in co]);band=np.array([tri[i] for i in range(len(tri)) if regions[i]==3]);areas=np.linalg.norm(np.cross(pp[band[:,1]]-pp[band[:,0]],pp[band[:,2]]-pp[band[:,0]]),axis=1)*.5;leftsurfacepass=all(q['left_grip_band_and_proximal_collar_surface_pairs']==0 for q in surface);leftsolidpass=all(q['inside']==0 and q['ambiguous']==0 for q in parity);global_surface_pass=all(q['complete_body_surface_pairs']==0 for q in surface);geometry=not selfpairs and bad==0 and top['components']==1 and not top['boundary_edges'] and not top['non_manifold_edges'] and volume>0 and leftsurfacepass and leftsolidpass and roundoff and fixed and areas.min()>1e-12
 r={'stage':'C59-actual-frozen-graft-after-images-audit','native_sha256':hashes['native'],'source_hashes':hashes,'body_actual_triangles':len(tri),'actual_complete_body_non_neighbour_triangle_self_pairs':len(selfpairs),'self_pairs':selfpairs,'inconsistent_winding_edges':bad,'topology':top,'signed_volume':volume,'zipper_triangle_min_area':float(areas.min()),'actual_evaluated_instrument_surface_tests':surface,'left_grip_band_collar_wood_parity':parity,'fixed_original_world_targets_unchanged':fixed,'actual_current_five_rays':rays,'strict_nominal_gap_0_to_point002_pass':bool(nominal),'previously_authorized_C35_fixed_face_positive_fp32_ceiling_roundoff_pass':bool(roundoff),'positive_only_ceiling_tolerance':tol,'roundoff_scope':'Parent previously accepted pure fixed C35 contact face positive overflow <=2.5e-7u; all5359 hand points/source contact faces exact here, targets unchanged. This is not strict <=.002 and never authorizes real wood/string/self penetration.','left_grip_band_surface_collision_pass':leftsurfacepass,'left_grip_band_solid_probe_pass':leftsolidpass,'complete_body_all_instrument_surface_pass':global_surface_pass,'graft_self_and_current_left_contact_engineering_pass':bool(geometry),'overall_character_or_animation_pass':False,'seconds':time.time()-start,'limits':['Whole retained body instrument intersections, if nonzero, remain blockers; left-grip contact pass does not certify the right strumming side/torso.','Current source frame/actual rays remeasured; no source pass merely inherited.','Source ear/body/graft geometry accepted numerically does not replace independent visual character reviews.','No native geometry/material/target changed by this readback.']};assert sha(NATIVE)==hashes['native'] and sha(BODY)==hashes['source_body'] and sha(HAND)==hashes['source_hand'];(OUT/'actual-graft-audit.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps({k:r[k] for k in ['actual_complete_body_non_neighbour_triangle_self_pairs','inconsistent_winding_edges','strict_nominal_gap_0_to_point002_pass','previously_authorized_C35_fixed_face_positive_fp32_ceiling_roundoff_pass','left_grip_band_surface_collision_pass','left_grip_band_solid_probe_pass','complete_body_all_instrument_surface_pass','graft_self_and_current_left_contact_engineering_pass','seconds']}),flush=True)
main()
