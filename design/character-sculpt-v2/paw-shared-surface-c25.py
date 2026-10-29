"""C25: one explicit parameter-domain reduction + shared editable surface band.
Local-only; frozen C23r2 source untouched. No Hermite/strip parameter sweep.
"""
import bpy,bmesh,numpy as np,math,json,sys,time,hashlib,argparse,shutil
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=argparse.ArgumentParser();P.add_argument('--out',default='artifacts/character-paw-shared-surface-c25');P.add_argument('--size',type=int,default=768);P.add_argument('--samples',type=int,default=16);a=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];out=root/a.out;out.mkdir(parents=True,exist_ok=True);old=root/'artifacts/character-paw-plane-source-c23/r2';src=old/'miao-c23-plane-source.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source_sha=sha(src);sys.path.insert(0,str(root/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
O=np.array([-.1950536246756659,-.85,1.5567366254980208]);GU=np.array([1.0169595357706245,0,.40048756408789304]);GV=np.array([-.40048756408789304,0,1.0169595357706245]);V=GV/np.linalg.norm(GV)
def logical_v(p):return (np.array(p)-O)@GV/(GV@GV)
def mesh(name,co,faces):
 m=bpy.data.meshes.new(name);m.from_pydata(co,[],faces);m.update();ob=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(ob);return ob

def topo(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();seen=set();comps=[]
 for v in bm.verts:
  if v.index in seen:continue
  stack=[v];seen.add(v.index);n=0
  while stack:
   p=stack.pop();n+=1
   for e in p.link_edges:
    q=e.other_vert(p)
    if q.index not in seen:seen.add(q.index);stack.append(q)
  comps.append(n)
 r={'vertices':len(bm.verts),'faces':len(bm.faces),'components':len(comps),'component_sizes':sorted(comps,reverse=True),'boundary_edges':sum(e.is_boundary for e in bm.edges),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges)};bm.free();return r

def interp_perimeter(points,frac,values):
 points=np.array(points);return np.column_stack([np.interp(values,np.r_[frac,1.],np.r_[points[:,j],points[:1,j]]) for j in range(3)])
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)

def main():
 started=time.time();bpy.ops.wm.open_mainfile(filepath=str(src));w=json.loads((old/'wire-rails.json').read_text());numeric=json.loads((old/'numeric-preflight.json').read_text());opening=json.loads((old/'opening-preflight.json').read_text());contacts=json.loads((old/'contact-audit.json').read_text());co=np.array(w['vertices']);fs=w['faces'];regions=w['material_regions'];rings=w['rings'];source_ids=w['source_root_indices'];upper_range=set(range(w['upper_offset'],w['upper_offset']+w['upper_count']));upper_loop=w['upper_boundary_final_indices'];ring50=next(r for r in rings if r['u']==.85);big=ring50['indices'];bigf=np.array(ring50['source_phase_fractions']);sf=np.r_[0.,np.cumsum(np.linalg.norm(np.roll(co[source_ids],-1,axis=0)-co[source_ids],axis=1))[:-1]/np.linalg.norm(np.roll(co[source_ids],-1,axis=0)-co[source_ids],axis=1).sum()];end=Vector(numeric['actual_upper_end_area_centroid']);endpts=co[upper_loop];tf=np.r_[0.,np.cumsum(np.linalg.norm(np.roll(endpts,-1,axis=0)-endpts,axis=1))[:-1]/np.linalg.norm(np.roll(endpts,-1,axis=0)-endpts,axis=1).sum()];stations=numeric['stations'];us=np.array([r['u'] for r in stations]);C=np.array([r['center'] for r in stations]);T=np.array([r['T'] for r in stations]);D=np.array([r['D'] for r in stations]);E=np.array([r['E'] for r in stations]);source_offset=co[source_ids]-C[0];sd=source_offset@D[0];se=source_offset@E[0];st=source_offset@T[0]
 def surface(u,fvalues):
  k=min(len(us)-2,max(0,int(np.searchsorted(us,u,side='right')-1)));b=(u-us[k])/(us[k+1]-us[k]);c=C[k]*(1-b)+C[k+1]*b;t=T[k]*(1-b)+T[k+1]*b;t/=np.linalg.norm(t);d=D[k]*(1-b)+D[k+1]*b;d-=t*(d@t);d/=np.linalg.norm(d);e=np.cross(t,d);ff=np.mod(np.array(fvalues),1);sdc=np.interp(ff,np.r_[sf,1],np.r_[sd,sd[:1]]);sec=np.interp(ff,np.r_[sf,1],np.r_[se,se[:1]]);stc=np.interp(ff,np.r_[sf,1],np.r_[st,st[:1]]);ep=interp_perimeter(endpts,tf,ff)-C[-1];ed=ep@D[-1];ee=ep@E[-1];b=float(smooth((u-.25)/.75));return c+(sdc*(1-b)+ed*b)[:,None]*d+(sec*(1-b)+ee*b)[:,None]*e+(stc*(1-b))[:,None]*t
 # Remove last reduction and four later rings, retaining lower forearm and actual
 # upper topology. Rebuild one monotonic 50->42 annulus; no closest-spoke phase search.
 removed=set()
 for r in rings:
  if .9<=r['u']<1:removed.update(r['indices'])
 for r in w['reductions']:
  if r['u']==.9:removed.update(r['helper_result']['actual_added_midpoint_indices'])
 kept_faces=[(f,m) for f,m in zip(fs,regions) if not(set(f)&removed)];used=sorted({i for f,m in kept_faces for i in f}|set(big));old2new={v:i for i,v in enumerate(used)};verts=[co[i].tolist() for i in used];faces=[[old2new[i] for i in f] for f,m in kept_faces];mats=[m for f,m in kept_faces];param={};old_new_upper={old2new[i]:i-w['upper_offset'] for i in upper_range};lockroot={old2new[i] for i in source_ids};root_lookup=[old2new[i] for i in source_ids];upper_boundary=[old2new[i] for i in upper_loop];B=[old2new[i] for i in big]
 for i,f in zip(B,bigf):param[i]=(.85,float(f))
 # Four disjoint 3-to-1 units: explicit correspondence in perimeter parameter.
 units={5,15,26,36};consume=[3 if j in units else 1 for j in range(42)];aa=[0]
 for n in consume[:-1]:aa.append(aa[-1]+n)
 assert sum(consume)==50 and len(aa)==42
 anchorf=bigf[aa];newrings=[];newmid=[]
 def add(positions,u,fvals):
  ids=list(range(len(verts),len(verts)+len(positions)));verts.extend(np.asarray(positions).tolist())
  for i,f in zip(ids,fvals):param[i]=(float(u),float(f))
  return ids
 small=add(surface(.90,anchorf),.90,anchorf);newrings.append({'u':.90,'indices':small,'fractions':anchorf.tolist()})
 for j in range(42):
  b0,b1=small[j],small[(j+1)%42];i=aa[j];ai=[B[(i+k)%50] for k in range(consume[j]+1)]
  if j not in units:faces.append([ai[0],ai[1],b1,b0]);mats.append(1);continue
  # The topology helper's chord arithmetic is replaced by exact known (u,f).
  fa=[float(bigf[(i+k)%50]) for k in range(4)];fb0=float(anchorf[j]);fb1=float(anchorf[(j+1)%42]);fb1+=int(fb1<fb0)
  for k in range(4):fa[k]+=int(fa[k]<fb0)
  ff=[(fa[1]+(2*fb0+fb1)/3)/2,(fa[2]+(fb0+2*fb1)/3)/2];mi=add(surface(.875,ff),.875,ff);newmid.extend(mi);m1,m2=mi;faces.extend([[ai[0],ai[1],m1,b0],[ai[1],ai[2],m2,m1],[ai[2],ai[3],b1,m2],[m1,m2,b1,b0]]);mats.extend([1]*4)
 prev=small
 for u in [.925,.95,.975,1.]:
  fvalues=anchorf*(1-(u-.90)/.10)+tf*((u-.90)/.10)
  ids=upper_boundary if u==1 else add(surface(u,fvalues),u,fvalues)
  for j in range(42):faces.append([prev[j],prev[(j+1)%42],ids[(j+1)%42],ids[j]]);mats.append(1)
  newrings.append({'u':u,'indices':ids,'fractions':fvalues.tolist()});prev=ids
 verts=np.array(verts,dtype=np.float64);original=verts.copy();assert np.max(np.abs(surface(.85,bigf)-co[big]))<5e-7
 # Editable band crosses the old plane and includes the actual C11 base surface.
 # Toe endpoints and explicit three toe-pad neighborhoods remain fixed.
 vv=np.array([logical_v(p) for p in verts]);editable=np.zeros(len(verts),bool)
 for i,(u,f) in param.items():editable[i]=u>.85
 for i in old_new_upper:editable[i]=vv[i]<.005
 editable[list(lockroot)]=False
 locks=[];actualbody=bpy.data.objects['Miao / continuous pear and rounded-square face'];bpy.context.view_layer.update();oldtree=BVHTree.FromObject(actualbody,bpy.context.evaluated_depsgraph_get());upper_to_new={v:k for k,v in old_new_upper.items()}
 for row in contacts['declared_toe_pad_targets']:
  pt=np.array(row['hit_world']);near=set(np.flatnonzero(np.linalg.norm(verts-pt,axis=1)<.023).tolist());target=Vector(row['target_world']);oh,on,ofi,od=oldtree.ray_cast(Vector((target.x,-.88,target.z)),Vector((0,-1,0)),1.5);assert oh is not None and (oh-Vector(row['hit_world'])).length<1e-6;facepins=[upper_to_new[actualbody.data.attributes['C23 actual upper local id'].data[i].value-1] for i in actualbody.data.polygons[ofi].vertices];near.update(facepins);near=sorted(near);editable[near]=False;locks.append({'digit':row['digit'],'exact_old_hit_face_vertices':facepins,'target_world':row['target_world'],'actual_r2_skin_hit':row['hit_world'],'locked_vertex_ids':near,'radius':.023})
 # Tips are all upper vertices V>=.005, not only the three extrema.
 tiplocks=[i for i in old_new_upper if vv[i]>=.005];editable[tiplocks]=False
 adjacency=[set() for _ in verts]
 for f in faces:
  for p,q in zip(f,f[1:]+f[:1]):adjacency[p].add(q);adjacency[q].add(p)
 editids=np.flatnonzero(editable);maxmove=.024;fair_trace=[]
 # One fixed Taubin fairing solve over shared topology, not a parameter search.
 # The displacement envelope prevents palm elongation or collapse; all locks exact.
 for iteration in range(40):
  for strength in [.45,-.47]:
   delta=np.zeros_like(verts)
   for i in editids:
    nb=list(adjacency[i]);delta[i]=verts[nb].mean(axis=0)-verts[i]
   verts[editids]+=strength*delta[editids];dv=verts-original;dl=np.linalg.norm(dv,axis=1);clamp=dl>maxmove;verts[clamp]=original[clamp]+dv[clamp]*(maxmove/dl[clamp])[:,None]
  if iteration in [0,9,39]:fair_trace.append({'iteration':iteration+1,'max_displacement':float(np.linalg.norm(verts-original,axis=1).max())})
 assert np.array_equal(verts[~editable],original[~editable]);patch=mesh('C25 authoring / shared quad surface band',verts.tolist(),faces)
 for f,m in zip(patch.data.polygons,mats):f.material_index=m;f.use_smooth=True
 bm=bmesh.new();bm.from_mesh(patch.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(patch.data);bm.free();patch.data.update();local=A.audit(patch);state=topo(patch)
 # Finite contact targets remain the same board/string world targets. Ray data is
 # explicit; misses are never replaced by nearest-surface distances.
 tree=BVHTree.FromPolygons([Vector(p) for p in verts],faces,all_triangles=False);targetcheck=[]
 for row in contacts['declared_toe_pad_targets']:
  pt=Vector(row['target_world']);h,n,fi,d=tree.ray_cast(Vector((pt.x,-.88,pt.z)),Vector((0,-1,0)),1.5);q={'digit':row['digit'],'target_world_unchanged':True,'hit':h is not None,'locked_r2_hit_world':row['hit_world']}
  if h is not None:q.update(hit_world=list(h),normal=list(n),r2_hit_displacement=(h-Vector(row['hit_world'])).length,signed_near_string_y_gap=pt.y-.0028-h.y)
  targetcheck.append(q)
 tip_drift=float(np.linalg.norm(verts[tiplocks]-original[tiplocks],axis=1).max());midparams=[{'vertex':i,'u':param[i][0],'f':param[i][1],'exact_parameter_surface_before_fair':original[i].tolist(),'after_shared_band_fair':verts[i].tolist(),'fair_displacement':float(np.linalg.norm(verts[i]-original[i]))} for i in newmid]
 mapping={'large_count':50,'small_count':42,'unit_edges':sorted(units),'explicit_consumption':consume,'large_anchor_indices':aa,'root50_fractions':bigf.tolist(),'small42_initial_fractions':anchorf.tolist(),'all_42_equal_count_ring_maps':newrings,'new_midpoint_parameter_evaluations':midparams,'source50_positions_bit_exact':bool(np.array_equal(verts[B],original[B])),'no_nearest_projection':True}
 plan={'edit_zone':'new wrist band after existing u=.85 plus C11 base surface logical V<.005; crosses old artificial V=-.07 cut','lock_zone':'all retained C8 body/root, wrist through u=.85, all C11 upper V>=.005, explicit three toe-pad neighborhoods radius .023u','contact_targets':'guitar and declared target world coordinates fixed; toe-pad neighborhoods lock prior skin hits, failed support locations remain diagnostic','same_count_mapping':mapping,'editable_vertices':len(editids),'locked_upper_tip_vertices':len(tiplocks),'toe_locks':locks,'fairing':'one fixed 40-iteration Taubin .45/-.47 solve on shared topology; displacement clamp .024u; no candidate sweep','fair_trace':fair_trace,'maximum_displacement':float(np.linalg.norm(verts-original,axis=1).max()),'tip_drift':tip_drift,'band_V_extent_before_after':[[float(np.min((original-O)@GV/(GV@GV))),float(np.max((original-O)@GV/(GV@GV)))],[float(np.min((verts-O)@GV/(GV@GV))),float(np.max((verts-O)@GV/(GV@GV)))]],'source_native_sha256':source_sha,'script_sha256':sha(__file__),'upstream_MIT_helpers_commit':'d44410f058991f677ccf733a8e86ce95110857eb'}
 report={'stage':'C25-one-shared-surface-band-geometric-preflight','plan':plan,'local_audit':local,'local_topology':state,'declared_toe_target_checks':targetcheck,'source_unchanged':sha(src)==source_sha,'limits':['Numerical gates do not constitute visual approval.','The retained earlier reductions and original whole body are not rebuilt.','40-step local fairing is a new band geometry candidate, not animation-ready topology proof.','No hair/color/animation/engine/export/deploy; previous UV/groom/shape binding invalid.']}
 (out/'mapping-and-lock-plan.json').write_text(json.dumps(plan,indent=2)+'\n');(out/'local-preflight.json').write_text(json.dumps(report,indent=2)+'\n');(out/'local-band-data.json').write_text(json.dumps({'vertices':verts.tolist(),'faces':faces,'regions':mats,'root_indices':root_lookup,'upper_local_ids':old_new_upper,'editable_indices':editids.tolist()})+'\n');print('LOCAL '+json.dumps({'self':local['self_intersections'],'flipped':local['flipped_faces'],'topology':state,'maxmove':plan['maximum_displacement'],'toe_hits':targetcheck}));passed=local['self_intersections']==0 and local['flipped_faces']==0 and state['components']==1 and state['boundary_edges']==198 and all(q.get('r2_hit_displacement',1)<1e-6 for q in targetcheck)
 if not passed:
  report['render_gate_passed']=False;(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'diagnostic-failed-local.blend'),compress=True);print('STOP one C25 preflight failed, no gray renders');return
 # Identity stitch into saved complete scene; all original body source vertices stay fixed.
 pco=[v.co[:] for v in patch.data.vertices];pfs=[list(f.vertices) for f in patch.data.polygons];bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];bm=bmesh.new();bm.from_mesh(body.data);sfac=bm.faces.layers.int['C23 source face id'];rootid=bm.verts.layers.int['C23 source opening local id'];upperid=bm.verts.layers.int['C23 actual upper local id'];upperface=bm.faces.layers.int['C23 C11 upper face local id'];region=bm.faces.layers.int['C23 construction region'];sourceverts={v for f in bm.faces if f[sfac]>0 for v in f.verts};sourcepositions={v:tuple(v.co) for v in sourceverts};rmap={v[rootid]-1:v for v in bm.verts if v[rootid]>0};assert len(rmap)==198
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if f[sfac]==0],context='FACES_ONLY');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces and v not in sourceverts],context='VERTS');mapping2={root_lookup[j]:rmap[j] for j in range(198)}
 for i,p in enumerate(pco):
  if i not in mapping2:mapping2[i]=bm.verts.new(p)
  if i in old_new_upper:mapping2[i][upperid]=old_new_upper[i]+1
 for i,f in enumerate(pfs):
  nf=bm.faces.new([mapping2[j] for j in f]);nf.smooth=True;nf[region]=mats[i];nf[upperface]=i+1 if mats[i]==2 else 0
 assert all(tuple(v.co)==p for v,p in sourcepositions.items());bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(body.data);bm.free();body.data.update();final=topo(body);assert final['components']==1 and final['boundary_edges']==0 and final['non_manifold_edges']==0
 # Audit local plus actual retained collar before any image.
 select=[f for f in body.data.polygons if .75<f.center.x<1.62 and f.center.y<-.60 and 1.3<f.center.z<2.35];ids=sorted({i for f in select for i in f.vertices});idmap={v:i for i,v in enumerate(ids)};probe=mesh('C25 authoring / actual shared band plus retained collar',[body.data.vertices[i].co[:] for i in ids],[[idmap[i] for i in f.vertices] for f in select]);collar=A.audit(probe);bpy.data.objects.remove(probe,do_unlink=True);passed=collar['self_intersections']==0 and collar['flipped_faces']==0;report.update(final_body=final,retained_C8_source_vertices_bit_exact=True,final_local_collar_audit=collar,render_gate_passed=passed,native_source_unchanged=sha(src)==source_sha,seconds_before_render=time.time()-started)
 # Preserve exact neutral C23 palette/lights; no look-dev changes.
 s.cycles.samples=a.samples;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;bpy.context.preferences.filepaths.save_version=0;body['C25']='One explicit parameter-domain annulus plus shared two-sided base-of-toes fairing; art gate pending';body['C25 old bindings']='INVALID after local geometry/topology reconstruction';native=out/('miao-c25-shared-surface.blend' if passed else 'diagnostic-failed-collar.blend');bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);report['native_sha256']=sha(native);(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 if not passed:print('STOP one C25 collar preflight failed, no gray renders');return
 cam=s.camera;frontloc=cam.location.copy();frontrot=cam.rotation_euler.copy();scale=cam.data.ortho_scale
 for view in ['front','inside']:
  if view=='inside':cam.location=(4,-6,3);cam.rotation_euler=(Vector((1.17,-.95,1.96))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25
  s.render.filepath=str(out/('gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
 cam.location=frontloc;cam.rotation_euler=frontrot;cam.data.ortho_scale=scale;print('RESULT '+json.dumps({'localself':local['self_intersections'],'collarself':collar['self_intersections'],'final':final,'source_unchanged':sha(src)==source_sha,'native_sha256':report['native_sha256']}))
main()
