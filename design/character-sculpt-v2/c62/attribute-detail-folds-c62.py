"""Read-only phase ablation: no candidate, shape file, render or parameter scan."""
import bpy,numpy as np,json,hashlib,itertools
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'artifacts/character-palm-sculpt-c62';N=O/'miao-c62-main-local-palm-study.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before_sha=sha(N);d=np.load(O/'main-C52-indexed-palm-delta.npz');bpy.ops.wm.open_mainfile(filepath=str(N));me=bpy.data.objects['Miao / continuous pear and rounded-square face'].data;me.calc_loop_triangles();tri=np.array([tuple(t.vertices) for t in me.loop_triangles],np.int32);P=d['source_coordinates'];B=d['broad_coordinates'];A=d['actual_coordinates'];D=d['palm_axis'];NN=d['final_surface_normals'];web=d['final_axis_setback'];crease=d['final_normal_crease'];C=d['origin'];T=d['lateral_axis'];mask=d['edit_mask']>0;affected=mask[tri].any(1)
def pairs(co):
 t=BVHTree.FromPolygons(co,[tuple(x) for x in tri],all_triangles=True);return {(a,b) for a,b in t.overlap(t) if a<b and not(set(tri[a])&set(tri[b]))}
base=pairs(P);pb=P[tri[affected]];n0=np.cross(pb[:,1]-pb[:,0],pb[:,2]-pb[:,0]);rows=[];sets={}
for name,co in [('source',P),('broad_after4smooth',B),('broad_plus_web_only_readonly',B+web[:,None]*D),('broad_plus_crease_only_readonly',B-crease[:,None]*NN),('actual_main_web_and_crease',A)]:
 pp=pairs(co);sets[name]=pp;v=co[tri[affected]];n1=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);dots=(n0*n1).sum(1)/(np.linalg.norm(n0,axis=1)*np.linalg.norm(n1,axis=1));new=pp-base;ids=sorted({i for a,b in new for tr in [a,b] for i in tri[tr]});r={'phase':name,'self_pairs':len(pp),'new_vs_source':len(new),'normal_reversal_vs_source':int((dots<=0).sum()),'min_normal_dot':float(dots.min())}
 if ids:
  v=co[ids];r.update(fold_vertex_source_C52_indices=[int(x) for x in ids],bbox=[v.min(0).tolist(),v.max(0).tolist()],palm_axis_range=[float(((v-C)@D).min()),float(((v-C)@D).max())],lateral_range=[float(((v-C)@T).min()),float(((v-C)@T).max())])
 rows.append(r)
confirmed=[]
for a,b in sorted(sets['actual_main_web_and_crease']-base):
 points=[];p=[Vector(A[i]) for i in tri[a]];q=[Vector(A[i]) for i in tri[b]]
 for es,tt in [(p,q),(q,p)]:
  for s,e in zip(es,es[1:]+es[:1]):
   l=(e-s).length
   if l<1e-12:continue
   dr=(e-s)/l;hit=intersect_ray_tri(*tt,dr,s,True)
   if hit is not None and -1e-7<=(hit-s).dot(dr)<=l+1e-7 and not any((hit-x).length<1e-7 for x in points):points.append(hit)
 span=max(((x-y).length for x,y in itertools.combinations(points,2)),default=0);confirmed.append({'triangles':[int(a),int(b)],'intersection_span':span,'confirmed_gt1e_minus6':span>1e-6})
r={'scope':'Read-only stored-phase ablation of the one frozen C62 candidate. No new authoring mesh, render, candidate or parameter choice.','native_sha256':before_sha,'phases':rows,'actual_new_pair_segment_confirmation':confirmed,'new_pairs_confirmed_over1e_minus6':sum(x['confirmed_gt1e_minus6'] for x in confirmed),'no_native_mutation':sha(N)==before_sha};(O/'detail-fold-causal-attribution.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps({'phases':[{k:v for k,v in x.items() if k in ['phase','self_pairs','new_vs_source','normal_reversal_vs_source','min_normal_dot','palm_axis_range','lateral_range']} for x in rows],'new_pairs_confirmed_over1e_minus6':r['new_pairs_confirmed_over1e_minus6']}),flush=True)
