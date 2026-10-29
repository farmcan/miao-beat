"""C23 reuse actual C11 upper palm/toes, one real cut opening plus shared wrist.
No whole-hand section guessing, closed-body union or global remesh.
"""
import bpy,bmesh,numpy as np,math,json,sys,time,hashlib,argparse
from pathlib import Path
from mathutils import Vector,Quaternion
p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/character-paw-plane-source-c23/r2');p.add_argument('--preflight-only',action='store_true');p.add_argument('--input-only',action='store_true');p.add_argument('--numeric-only',action='store_true');p.add_argument('--size',type=int,default=768);p.add_argument('--samples',type=int,default=16);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];out=root/a.out;out.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sys.path.insert(0,str(root/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_retopo as R;import bx_audit as A
src8=root/'artifacts/character-fidelity-c8-r2-color/miao-c8-reference-hold.blend';src11=root/'artifacts/character-paw-c11-r2/miao-c11-paw-volume.blend';origin=Vector((-.1950536246756659,-.85,1.5567366254980208));gu=Vector((1.0169595357706245,0,.40048756408789304));gv=Vector((-.40048756408789304,0,1.0169595357706245));U=gu.normalized();V=gv.normalized();Y=Vector((0,1,0))
def logical_u(p):return (p-origin).dot(gu)/gu.length_squared
def logical_v(p):return (p-origin).dot(gv)/gv.length_squared
def g(u,v,y):return origin+gu*u+gv*v+Vector((0,y-origin.y,0))
def av(points):
 c=sum(points,Vector())/len(points);return sum(((p-c).cross(q-c) for p,q in zip(points,points[1:]+points[:1])),Vector())*.5
s=(root/'design/character-sculpt-v2/paw-volume-study.py').read_text();exec(compile(s[s.index('def mesh('):s.index('def make_hand():')],'C11-shared-helpers','exec'),globals())
def upper_cut(level):
 bpy.ops.wm.open_mainfile(filepath=str(src11));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];co=[v.co.copy() for v in body.data.vertices];selected=[f for f in body.data.polygons if all(co[i].y<-.90 and .95<logical_u(co[i])<1.75 and -.20<logical_v(co[i])<.25 for i in f.vertices)];used=sorted({i for f in selected for i in f.vertices});mp={v:i for i,v in enumerate(used)};o=mesh('C23 / actual C11 upper palm-toes open patch',[co[i][:] for i in used],[[mp[i] for i in f.vertices] for f in selected]);source_coords={tuple(round(q,7) for q in co[i]):i for i in used};bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=g(1.35,level,-1.06),plane_no=V,clear_inner=True,clear_outer=False);loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update();state=topo(o);loops=R.boundary_loops(o);audit=A.audit(o);rows=[]
 for lp in loops:
  pts=[o.data.vertices[i].co.copy() for i in lp];area=av(pts);rows.append({'count':len(lp),'points':[list(p) for p in pts],'vertex_indices':lp,'mean_center':list(sum(pts,Vector())/len(pts)),'area_vector':list(area),'plane_v_min_max':[min(logical_v(p) for p in pts),max(logical_v(p) for p in pts)]})
 retained=[];new=[]
 for v in o.data.vertices:
  sid=source_coords.get(tuple(round(q,7) for q in v.co));(retained if sid is not None else new).append({'vertex':v.index,'source_C11_vertex':sid,'coordinate':list(v.co)})
 report={'level_v':level,'C11_source_sha256':sha(src11),'selection_description':'actual saved C11 body surface, Y<-.90, U(.95,1.75), V(-.20,.25), then actual halfspace cut; collar below V=-.07 not included','topology':state,'audit':audit,'boundary_loops':rows,'retained_C11_vertices':len(retained),'new_cut_vertices':len(new),'source_vertex_map':retained,'cut_vertex_map':new,'valid_single_open_upper_patch':state['components']==1 and len(loops)==1 and audit['self_intersections']==0 and len(loops[0])>=6};(out/'upper-preflight.json').write_text(json.dumps(report,indent=2)+'\n');print('UPPER '+json.dumps({k:report[k] for k in ['level_v','topology','retained_C11_vertices','new_cut_vertices','valid_single_open_upper_patch']}));return o,report

def coords(o):
 ar=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',ar);return ar.reshape(-1,3)
area_vec=av
src=src8;source_sha=sha(src8)
def source_opening():
 bpy.ops.wm.open_mainfile(filepath=str(src8));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();body.data=bpy.data.meshes.new_from_object(body.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
 for mod in list(body.modifiers):body.modifiers.remove(mod)
 initial=coords(body);body.data.attributes.new('C23 source vertex id','INT','POINT').data.foreach_set('value',np.arange(1,len(initial)+1,dtype=np.int32));body.data.attributes.new('C23 source face id','INT','FACE').data.foreach_set('value',np.arange(1,len(body.data.polygons)+1,dtype=np.int32));bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table();sid=bm.verts.layers.int['C23 source vertex id'];original=set(bm.verts);protected={v for v in bm.verts if v.co.y>-.70};roi=[f for f in bm.faces if .75<f.calc_center_median().x<1.62 and 1.30<f.calc_center_median().z<2.35 and f.calc_center_median().y<-.55];edges={e for f in roi for e in f.edges};verts={v for f in roi for v in f.verts};pred=[]
 for e in edges:
  p,q=e.verts;a0=p.co.copy();b0=q.co.copy()
  if (a0.y+.72)*(b0.y+.72)<0:
   t=(-.72-a0.y)/(b0.y-a0.y);pred.append({'original_edge':e.index,'source_vertices':[p[sid]-1,q[sid]-1],'t':t,'point':list(a0.lerp(b0,t))})
 bmesh.ops.bisect_plane(bm,geom=list(verts)+list(edges)+roi,dist=1e-8,plane_co=(0,-.72,0),plane_no=(0,1,0),clear_inner=False,clear_outer=False)
 for v in bm.verts:
  if v not in original:v[sid]=0
 delete=[f for f in bm.faces if .75<f.calc_center_median().x<1.62 and 1.3<f.calc_center_median().z<2.35 and f.calc_center_median().y<-.72-1e-7];bmesh.ops.delete(bm,geom=delete,context='FACES_ONLY');loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bm.to_mesh(body.data);bm.free();body.data.update();loops=R.boundary_loops(body);assert len(loops)==1,{'holes':[len(q) for q in loops]};n_before=len(loops[0]);parity=None
 if n_before%2:
  bm=bmesh.new();bm.from_mesh(body.data);candidates=[e for e in bm.edges if e.is_boundary];e=max(candidates,key=lambda e:e.calc_length());endpoints=[list(v.co) for v in e.verts];newedge,newvert=bmesh.utils.edge_split(e,e.verts[0],.5);newvert[bm.verts.layers.int['C23 source vertex id']]=0;parity={'type':'one explicit boundary edge split at midpoint, original geometry not displaced','endpoints':endpoints,'new_point':list(newvert.co),'new_ngons_are_recorded_in_topology':True};bm.to_mesh(body.data);bm.free();body.data.update();loops=R.boundary_loops(body)
 border=list(loops[0]);T=Vector((0,-1,0));points=[body.data.vertices[i].co.copy() for i in border]
 if av(points).dot(T)<0:border=border[::-1]
 k=min(range(len(border)),key=lambda j:body.data.vertices[border[j]].co.z);border=border[k:]+border[:k];points=[body.data.vertices[i].co.copy() for i in border];p2=np.array([[p.x,p.z] for p in points]);crossings=[]
 def det(a,b):return a[0]*b[1]-a[1]*b[0]
 for i in range(len(p2)):
  for j in range(i+1,len(p2)):
   if j==i+1 or (i==0 and j==len(p2)-1):continue
   p0=p2[i];q0=p2[j];r=p2[(i+1)%len(p2)]-p0;ss=p2[(j+1)%len(p2)]-q0;den=det(r,ss)
   if abs(den)<1e-14:continue
   t=det(q0-p0,ss)/den;u=det(q0-p0,r)/den
   if 1e-8<t<1-1e-8 and 1e-8<u<1-1e-8:crossings.append([i,j])
 attr=body.data.attributes.new('C23 source opening local id','INT','POINT');localids=np.zeros(len(body.data.vertices),np.int32)
 for i,v in enumerate(border):localids[v]=i+1
 attr.data.foreach_set('value',localids);ids=np.empty(len(body.data.vertices),np.int32);body.data.attributes['C23 source vertex id'].data.foreach_get('value',ids);co=coords(body);mask=ids>0;protected_ids=set(np.flatnonzero(initial[:,1]>-.70)+1);remaining=set(int(i) for i in ids if i>0);same=np.array_equal(co[mask],initial[ids[mask]-1]);state=topo(body)
 # Actual local advance probe: same input loop, pure -Y translation, three rings.
 pp=[p+Vector((0,-.02*j,0)) for j in range(3) for p in points];ff=[];n=len(points)
 for j in range(2):
  for i in range(n):ff.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 probe=mesh('C23 authoring / input-only three-ring advance',pp,ff);probeaudit=A.audit(probe);bpy.data.objects.remove(probe,do_unlink=True);point_err=max(abs(p.y+.72) for p in points);report={'stage':'C23-real-plane-source-opening-input-preflight','source_sha256':sha(src8),'cut_plane':{'world_y':-.72,'normal':[0,1,0],'ROI':'right-hand faces/edges/vertices only; no global body cut'},'boundary_count_before_even_split':n_before,'boundary_count':len(border),'parity_split':parity,'boundary_loops':len(loops),'boundary_points':[list(p) for p in points],'source_border_vertex_indices':border,'maximum_plane_error_y':point_err,'XZ_projected_strict_crossings':crossings,'source_edge_intersections':pred,'topology':state,'all_retained_original_vertices_bit_exact':bool(same),'retained_original_vertices':int(mask.sum()),'new_plane_intersection_and_split_vertices':int((~mask).sum()),'protected_Y_greater_minus70_count':len(protected_ids),'protected_vertices_missing':len(protected_ids-remaining),'three_ring_advance_audit':probeaudit,'source_unchanged':sha(src8)==source_sha};(out/'opening-preflight.json').write_text(json.dumps(report,indent=2)+'\n');passed=len(loops)==1 and point_err<5e-7 and not crossings and probeaudit['self_intersections']==0 and same and not(protected_ids-remaining);report['passed']=bool(passed);(out/'opening-preflight.json').write_text(json.dumps(report,indent=2)+'\n');print('INPUT '+json.dumps({k:report[k] for k in ['boundary_count_before_even_split','boundary_count','maximum_plane_error_y','XZ_projected_strict_crossings','retained_original_vertices','new_plane_intersection_and_split_vertices','protected_vertices_missing','passed']}));assert passed,report
 for o in s.objects:
  if o.name.startswith('Miao / native short plush'):o.hide_render=True;o.hide_set(True);o['C23 binding']='INVALID after local replacement'
 target=body.copy();target.data=body.data.copy();target.name='C23 authoring / exact open source';s.collection.objects.link(target);target.hide_render=True;target.hide_set(True);return s,body,target,initial,border,report

def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def polygon_center(points):
 # All upper boundary vertices lie on the real V plane, use U/Y area centroid.
 c=sum(points,Vector())/len(points);xy=np.array([[(p-c).dot(U),p.y-c.y] for p in points]);xx=xy[:,0];yy=xy[:,1];cr=xx*np.roll(yy,-1)-np.roll(xx,-1)*yy;A0=cr.sum()/2;cx=((xx+np.roll(xx,-1))*cr).sum()/(6*A0);cy=((yy+np.roll(yy,-1))*cr).sum()/(6*A0);return c+U*float(cx)+Y*float(cy)
def fractions(points):
 le=np.array([(q-p).length for p,q in zip(points,points[1:]+points[:1])]);return np.concatenate([[0],np.cumsum(le[:-1])/le.sum()])
def periodic_sample(points,f,values):
 co=np.array([p[:] for p in points]);ff=np.concatenate([f,[1.0]]);co=np.vstack([co,co[:1]]);return np.array([[np.interp(q,ff,co[:,j]) for j in range(3)] for q in values])
def numerical(s,body,initial,border,upco,upfs,uploop,upper_report):
 start=Vector((1.175495,-.72,1.726244));source_pts=[body.data.vertices[i].co.copy() for i in border];endpts=[Vector(upco[i]) for i in uploop]
 if av(endpts).dot(V)<0:uploop=list(reversed(uploop));endpts=list(reversed(endpts))
 end=polygon_center(endpts);aY=start.y-end.y;bZ=end.z-start.z;assert aY>0 and bZ>0
 # Match actual end tangent V using a Hermite X coordinate, not guessed +Z.
 deltaX=end.x-start.x;end_dx_du=bZ*(V.x/V.z)*math.pi/2
 samples=np.linspace(0,1,25);C=[];T=[];D=[];curv=[];Ncurve=[]
 for u in samples:
  th=u*math.pi/2;x=start.x+deltaX*(3*u*u-2*u*u*u)+end_dx_du*(u*u*u-u*u);c=Vector((x,start.y-aY*math.sin(th),start.z+bZ*(1-math.cos(th))));dx=(deltaX*(6*u-6*u*u)+end_dx_du*(3*u*u-2*u))*2/math.pi;ddx=(deltaX*(6-12*u)+end_dx_du*(6*u-2))*(2/math.pi)**2;vel=Vector((dx,-aY*math.cos(th),bZ*math.sin(th)));acc=Vector((ddx,aY*math.sin(th),bZ*math.cos(th)));t=vel.normalized();k=vel.cross(acc).length/vel.length**3;n=(acc-t*acc.dot(t)).normalized();C.append(c);T.append(t);curv.append(k);Ncurve.append(n)
 D=[Vector((0,0,-1))]
 for j in range(1,len(T)):d=T[j-1].rotation_difference(T[j])@D[-1];D.append((d-T[j]*d.dot(T[j])).normalized())
 desired=Vector((0,-1,0));desired=(desired-T[-1]*desired.dot(T[-1])).normalized();roll=math.atan2(T[-1].dot(D[-1].cross(desired)),D[-1].dot(desired))
 for j,u in enumerate(samples):D[j]=Quaternion(T[j],roll*float(smooth((u-.25)/.75)))@D[j]
 E=[t.cross(d).normalized() for t,d in zip(T,D)];phase=max(range(len(endpts)),key=lambda i:(endpts[i]-end).dot(D[-1]));uploop=uploop[phase:]+uploop[:phase];endpts=endpts[phase:]+endpts[:phase];sf=fractions(source_pts);tf=fractions(endpts)
 # Preserve every source vertex's phase and initial D/E/T residual. No uniform
 # first-ring sample or hidden reindexing. Target shape comes from actual cut loop.
 source_offset=np.array([(p-start)[:] for p in source_pts]);sd=source_offset@np.array(D[0]);se=source_offset@np.array(E[0]);st=source_offset@np.array(T[0]);target=periodic_sample(endpts,tf,sf)-np.array(end);td=target@np.array(D[-1]);te=target@np.array(E[-1]);grid=[];records=[]
 for j,u in enumerate(samples):
  blend=float(smooth((u-.25)/.75));fade=1-blend;dd=sd*(1-blend)+td*blend;ee=se*(1-blend)+te*blend;rr=st*fade;pts=np.array(C[j])[None,:]+dd[:,None]*np.array(D[j])+ee[:,None]*np.array(E[j])+rr[:,None]*np.array(T[j]);inner=float(((pts-np.array(C[j]))@np.array(Ncurve[j])).max());records.append({'u':float(u),'center':list(C[j]),'T':list(T[j]),'D':list(D[j]),'E':list(E[j]),'curvature_radius':1/curv[j],'inner_extent':inner,'one_minus_kappa_inner':1-curv[j]*inner});grid.append(pts)
 rails=[]
 for j in range(len(samples)-1):
  direction=(C[j+1]-C[j]).normalized();p=(grid[j+1]-grid[j])@np.array(direction);rails.append({'strip':j,'min_progress':float(p.min()),'negative_progress_count':int((p<0).sum())})
 rep={'actual_start':list(start),'actual_upper_end_area_centroid':list(end),'actual_upper_end_plane_normal':list(V),'end_curve_tangent':list(T[-1]),'end_tangent_dot_actual_normal':T[-1].dot(V),'end_loop_count':len(endpts),'end_loop_phase_original_offset':phase,'curve_parameters':{'aY':aY,'bZ':bZ,'deltaX':deltaX,'end_dx_du':end_dx_du},'final_roll_degrees':math.degrees(roll),'minimum_1_minus_kappa_inner':min(q['one_minus_kappa_inner'] for q in records),'total_reversing_rails':sum(q['negative_progress_count'] for q in rails),'minimum_rail_progress':min(q['min_progress'] for q in rails),'stations':records,'rail_steps':rails,'source_points_preserved_at_u0_max_error':float(np.abs(grid[0]-np.array(source_pts)).max()),'scope':f'Numeric variable-section loft proxy using all {len(source_pts)} inherited source correspondences and actual C11 upper boundary; no reduction strips or full combined mesh tested yet.'};(out/'numeric-preflight.json').write_text(json.dumps(rep,indent=2)+'\n');print('NUMERIC '+json.dumps({k:rep[k] for k in ['actual_upper_end_area_centroid','end_loop_count','end_tangent_dot_actual_normal','minimum_1_minus_kappa_inner','total_reversing_rails','minimum_rail_progress']}));return rep,(samples,C,T,D,E,sd,se,st,endpts,tf,sf,uploop,grid)

def bridge_mark(o,aa,bb,reduce=False):
 nf=len(o.data.polygons);ret=R.bridge_reduce(o,aa,bb,target=None) if reduce else {'faces':R.bridge(o,aa,bb,align=False),'units':0}
 for f in list(o.data.polygons)[nf:]:f.material_index=1
 return ret

def prerender_seams(body):
 bm=bmesh.new();bm.from_mesh(body.data);bm.normal_update();uf=bm.faces.layers.int['C23 C11 upper face local id'];sf=bm.faces.layers.int['C23 source face id'];groups={'source_root':[],'upper_interface':[],'wrist_internal':[]}
 def group(f):return 2 if f[uf]>0 else 0 if f[sf]>0 else 1
 for e in bm.edges:
  if len(e.link_faces)!=2:continue
  a,b=e.link_faces;ga,gb=group(a),group(b);key='upper_interface' if {ga,gb}=={1,2} else 'source_root' if {ga,gb}=={0,1} else 'wrist_internal' if ga==gb==1 else None
  if key:groups[key].append(math.degrees(math.acos(max(-1,min(1,a.normal.dot(b.normal))))))
 bm.free();r={key:{'edges':len(v),'median':float(np.median(v)),'p95':float(np.percentile(v,95)),'maximum':max(v)} for key,v in groups.items()};(out/'pre-render-seam-audit.json').write_text(json.dumps(r,indent=2)+'\n');return r

def build(s,body,target,initial,border,source_report,upco,upfs,upper_report,num,data):
 started=time.time();samples,C,T,D,E,sd,se,st,endpts,tf,sf,uploop,latent=data;upper_offset=len(border);patch=mesh('C23 authoring / open reused upper and shared wrist',[body.data.vertices[i].co[:] for i in border]+upco,[[i+upper_offset for i in f] for f in upfs]);upper_ring=[i+upper_offset for i in uploop]
 for f in patch.data.polygons:f.material_index=2;f.use_smooth=True
 # Exact source correspondence for the first rings. Reduction is confined to
 # newly authored later wrist rings; upper patch and body originals never move.
 N0=len(border);N1=2*math.ceil(N0/4);N2=2*math.ceil(N1/4);assert N0<=2*N1 and N1<=2*N2 and N2<=84 and N2%2==0
 schedule=[(0,N0)]+[(float(u),N0) for u in samples[1:17]]+[(.75,N1),(.80,N1),(.85,N2),(.90,42),(.925,42),(.95,42),(.975,42),(1.,42)]
 prev=list(range(len(border)));ring_records=[];reductions=[]
 def frame(u):
  k=min(len(samples)-2,int(np.searchsorted(samples,u,side='right')-1));k=max(k,0);f=(u-samples[k])/(samples[k+1]-samples[k]);c=C[k].lerp(C[k+1],float(f));tt=T[k].lerp(T[k+1],float(f)).normalized();dd=D[k].lerp(D[k+1],float(f));dd=(dd-tt*dd.dot(tt)).normalized();ee=tt.cross(dd).normalized();return c,tt,dd,ee
 # Source-derived end tangent, exact cutpoint identity. No nearest normal lookup.
 r1dir=root/'artifacts/character-paw-plane-source-c23/r1';r1w=json.loads((r1dir/'wire-rails.json').read_text());nsource=json.loads((out/'upper-tangent-preflight.json').read_text());assert nsource['source_C11_sha256']==sha(src11) and nsource['positive_V_all'];normal_by_uid={q['upper_local_vertex']:q for q in nsource['records']}
 assert np.array_equal(np.array(upco,dtype=np.float32),np.array(json.loads((r1dir/'upper-reused-data.json').read_text())['vertices'],dtype=np.float32))
 assert np.array_equal(np.array(source_report['boundary_points'],dtype=np.float32),np.array(json.loads((r1dir/'opening-preflight.json').read_text())['boundary_points'],dtype=np.float32))
 def ideal_points(u,fvalues):
  c,tt,dd,ee=frame(u);fvalues=np.array(fvalues);sdc=np.interp(fvalues,np.r_[sf,1.],np.r_[sd,sd[:1]]);sec=np.interp(fvalues,np.r_[sf,1.],np.r_[se,se[:1]]);stc=np.interp(fvalues,np.r_[sf,1.],np.r_[st,st[:1]]);ep=periodic_sample(endpts,tf,fvalues)-np.array(C[-1]);ed=ep@np.array(D[-1]);eec=ep@np.array(E[-1]);blend=float(smooth((u-.25)/.75));return np.array(c)+(sdc*(1-blend)+ed*blend)[:,None]*np.array(dd)+(sec*(1-blend)+eec*blend)[:,None]*np.array(ee)+(stc*(1-blend))[:,None]*np.array(tt)
 hstart=.925;Q=np.array([upco[i] for i in uploop]);Pstart=ideal_points(hstart,tf);dstart=(ideal_points(hstart+1e-5,tf)-ideal_points(hstart-1e-5,tf))/(2e-5);dend=np.array([normal_by_uid[i]['projected_rail_derivative'] for i in uploop]);nend=np.array([normal_by_uid[i]['uncut_interpolated_vertex_normal'] for i in uploop]);assert np.max(np.abs(Q-np.array([normal_by_uid[i]['actual_cut_point'] for i in uploop])))<1e-8
 def hermite(u):
  h=1-hstart;t=(u-hstart)/h;return (2*t**3-3*t*t+1)*Pstart+(t**3-2*t*t+t)*h*dstart+(-2*t**3+3*t*t)*Q+(t**3-t*t)*h*dend
 hh=[hermite(float(u)) for u in np.linspace(hstart,1,101)];progress=np.concatenate([(q-p)@np.array(V) for p,q in zip(hh,hh[1:])]);c1check={'source_normals_unique_edge_matches':nsource['unique_exact_edge_matches'],'source_normal_max_edge_residual':nsource['maximum_edge_match_residual'],'projected_end_derivative_dot_normal_max':float(np.abs((dend*nend).sum(1)).max()),'projected_end_derivative_min_V':float((dend@np.array(V)).min()),'Hermite_start_u':hstart,'Hermite_endpoint_max_displacement':float(np.abs(hermite(1)-Q).max()),'Hermite_42_rails_reverse_count':int((progress<0).sum()),'Hermite_min_rail_step_V':float(progress.min()),'base_curve_changed':False,'source_upper_moved':False};(out/'C1-numeric-before-build.json').write_text(json.dumps(c1check,indent=2)+'\n');assert c1check['projected_end_derivative_min_V']>0 and c1check['Hermite_42_rails_reverse_count']==0 and c1check['Hermite_endpoint_max_displacement']<1e-12
 def midpoint_proxy(points,ulo,uhi):
  from mathutils.bvhtree import BVHTree
  fu=np.linspace(ulo,uhi,17);ff=np.arange(512)/512;pv=np.vstack([ideal_points(float(u),ff) for u in fu]);faces=[]
  for j in range(len(fu)-1):
   for k in range(512):faces.append((j*512+k,j*512+(k+1)%512,(j+1)*512+(k+1)%512,(j+1)*512+k))
  tree=BVHTree.FromPolygons([Vector(v) for v in pv],faces,all_triangles=False);rows=[]
  for p in points:
   q,n,fi,d=tree.find_nearest(Vector(p));rows.append({'distance':d,'signed_offset':(Vector(p)-q).dot(n)})
  return {'count':len(rows),'maximum_distance':max(q['distance'] for q in rows),'minimum_signed_offset':min(q['signed_offset'] for q in rows),'records':rows,'scope':'Read-only distance to a known ideal-loft dense proxy, not asset fitting or nearest source-normal fallback'}

 for u,n in schedule[1:]:
  c,tt,dd,ee=frame(u)
  if u==1.:ids=upper_ring;pts=[Vector(upco[i]) for i in uploop];fvalues=tf.tolist()
  else:
   if n==N0:idx=np.arange(N0);fvalues=sf
   elif n==N1:idx=np.floor(np.arange(N1)*N0/N1).astype(int);fvalues=sf[idx]
   elif n==N2:idx=np.floor(np.arange(N2)*N0/N2).astype(int);fvalues=sf[idx]
   else:idx=None;fblend=float(smooth((u-.90)/.025));fvalues=(1-fblend)*np.arange(42)/42+fblend*tf
   # Interpolate the inherited source perimeter coordinates by its own arc
   # parameter. This does not reindex or move any of the 180 original root points.
   sdc=np.interp(fvalues,np.r_[sf,1.],np.r_[sd,sd[:1]]);sec=np.interp(fvalues,np.r_[sf,1.],np.r_[se,se[:1]]);stc=np.interp(fvalues,np.r_[sf,1.],np.r_[st,st[:1]]);ep=periodic_sample(endpts,tf,fvalues)-np.array(C[-1]);ed=ep@np.array(D[-1]);eec=ep@np.array(E[-1]);blend=float(smooth((u-.25)/.75));fade=1-blend;dr=sdc*(1-blend)+ed*blend;er=sec*(1-blend)+eec*blend;tr=stc*fade;pts=[c+dd*float(x)+ee*float(y)+tt*float(z) for x,y,z in zip(dr,er,tr)]
   if n==42 and u>=hstart:pts=[Vector(p) for p in hermite(u)]
   ids=R.add_ring(patch,pts)
  wind=av(pts).dot(tt);assert wind>0,{'bad_ring_winding':u,'value':wind};nv_before=len(patch.data.vertices);r=bridge_mark(patch,prev,ids,len(prev)!=len(ids));r['actual_added_midpoint_indices']=list(range(nv_before,len(patch.data.vertices)));reductions.append({'from':len(prev),'to':len(ids),'u':u,'helper_result':r});ring_records.append({'u':u,'indices':ids,'count':len(ids),'center':list(c),'T':list(tt),'D':list(dd),'E':list(ee),'winding_dot_T':wind,'source_phase_fractions':list(fvalues)});prev=ids
 for f in patch.data.polygons:f.use_smooth=True
 lastred=next(q for q in reductions if q['from']==50 and q['to']==42);midpointcheck=midpoint_proxy([patch.data.vertices[i].co[:] for i in lastred['helper_result']['actual_added_midpoint_indices']],.85,.90);(out/'actual-helper-midpoint-audit.json').write_text(json.dumps(midpointcheck,indent=2)+'\n')
 local=A.audit(patch);local_topo=topo(patch);(out/'local-combined-audit.json').write_text(json.dumps(local,indent=2)+'\n');wire={'vertices':[v.co[:] for v in patch.data.vertices],'faces':[list(f.vertices) for f in patch.data.polygons],'material_regions':[f.material_index for f in patch.data.polygons],'source_root_indices':list(range(len(border))),'upper_offset':upper_offset,'upper_count':len(upco),'upper_boundary_final_indices':upper_ring,'rings':ring_records,'reductions':reductions,'topology':local_topo};(out/'wire-rails.json').write_text(json.dumps(wire,indent=2)+'\n')
 assert local_topo['components']==1 and local_topo['boundary_edges']==len(border) and local['flipped_faces']==0,{'topology':local_topo,'audit':local}
 # Weld by exact identity, not distance. The only duplicate root vertices are
 # mapped to the original 180 source vertices; all actual C11 upper points copy.
 bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();upper_id=bm.verts.layers.int.new('C23 actual upper local id');upper_source_id=bm.verts.layers.int.new('C23 C11 source vertex id');region=bm.faces.layers.int.new('C23 construction region');upperface=bm.faces.layers.int.new('C23 C11 upper face local id');mapping={i:bm.verts[bid] for i,bid in enumerate(border)};sid11={q['vertex']:q['source_C11_vertex']+1 for q in upper_report['source_vertex_map']}
 for v in patch.data.vertices:
  if v.index>=len(border):mapping[v.index]=bm.verts.new(v.co)
  if upper_offset<=v.index<upper_offset+len(upco):mapping[v.index][upper_id]=v.index-upper_offset+1;mapping[v.index][upper_source_id]=sid11.get(v.index-upper_offset,0)
 for f in patch.data.polygons:
  nf=bm.faces.new([mapping[i] for i in f.vertices]);nf.smooth=True;nf[region]=f.material_index;nf[upperface]=f.index+1 if f.index<len(upfs) else 0
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(body.data);bm.free();body.data.update();final=topo(body);assert final['components']==1 and final['non_manifold_edges']==0,final
 ids=np.empty(len(body.data.vertices),np.int32);body.data.attributes['C23 source vertex id'].data.foreach_get('value',ids);co=coords(body);keep=ids>0;exact=bool(np.array_equal(co[keep],initial[ids[keep]-1]));assert exact
 uid=np.empty(len(body.data.vertices),np.int32);body.data.attributes['C23 actual upper local id'].data.foreach_get('value',uid);uk=uid>0;upperexact=bool(np.array_equal(co[uk],np.array(upco,dtype=np.float32)[uid[uk]-1]));assert upperexact
 oid=np.empty(len(body.data.vertices),np.int32);body.data.attributes['C23 source opening local id'].data.foreach_get('value',oid);ok=oid>0;opening_exact=bool(np.array_equal(co[ok],np.array(source_report['boundary_points'],dtype=np.float32)[oid[ok]-1]));assert opening_exact
 # Include the neighboring original C8 collar in the final local collision gate.
 faces=[f for f in body.data.polygons if .75<f.center.x<1.62 and f.center.y<-.60 and 1.3<f.center.z<2.35];vv=sorted({i for f in faces for i in f.vertices});mp={v:i for i,v in enumerate(vv)};auditmesh=mesh('C23 authoring / final local plus retained C8 collar',[body.data.vertices[i].co[:] for i in vv],[[mp[i] for i in f.vertices] for f in faces]);collar_audit=A.audit(auditmesh);(out/'final-local-collar-audit.json').write_text(json.dumps(collar_audit,indent=2)+'\n');bpy.data.objects.remove(auditmesh,do_unlink=True)
 bpy.data.objects.remove(patch,do_unlink=True);bpy.data.objects.remove(target,do_unlink=True)
 seams=prerender_seams(body)
 passed=(local['self_intersections']==0 and collar_audit['self_intersections']==0 and collar_audit['flipped_faces']==0)
 # Same exact neutral palette and original light linking receiver collections.
 mats=[]
 for name,value in [('body',.4),('white',.72),('dark',.045),('wood',.30)]:
  m=bpy.data.materials.new('C23 gray '+name);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(value,value,value,1);bs.inputs['Roughness'].default_value=.65;mats.append(m)
 for o in list(s.objects):
  if o.type not in {'MESH','CURVES','CURVE'} or o.hide_render or o.name.startswith(('Studio /','Authoring /','D0 /','C7 / clear')):continue
  o.data.materials.clear();o.data.materials.append(mats[1] if o.name.startswith('C6 / sclera') else mats[2] if o.name.startswith(('C6 / iris','Face /')) else mats[3] if o.name.startswith('Guitar /') else mats[0])
 s.cycles.samples=a.samples;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;bpy.context.preferences.filepaths.save_version=0;body['C23 pipeline']='C23r2 last reduction u.90 with uniform perimeter, source-normal Hermite C1 approach u.925+, source/upper/base curve fixed';body['C23 old bindings']='INVALID after local topology change';bpy.ops.wm.save_as_mainfile(filepath=str(out/('miao-c23-plane-source.blend' if passed else 'diagnostic-failed-local-self.blend')),compress=True)
 protection={'source_plane_opening_vertices':int(ok.sum()),'source_plane_opening_vertices_bit_exact':opening_exact,'C8_retained_vertices':int(keep.sum()),'C8_retained_vertices_bit_exact':exact,'maximum_C8_retained_displacement':float(np.linalg.norm(co[keep]-initial[ids[keep]-1],axis=1).max()),'C11_upper_vertices_including_cut':int(uk.sum()),'C11_upper_vertices_bit_exact':upperexact,'C11_original_surface_vertices':len(upper_report['source_vertex_map']),'C11_new_cut_vertices':len(upper_report['cut_vertex_map']),'maximum_upper_displacement':float(np.abs(co[uk]-np.array(upco,dtype=np.float32)[uid[uk]-1]).max()),'global_remesh_or_subdivision':False}
 report={'stage':'C23r2-one-targeted-transition-quality-candidate','C1_numeric':c1check,'pre_render_seams':seams,'actual_last_helper_midpoints':midpointcheck,'source_C8_sha256':sha(src8),'source_C11_sha256':sha(src11),'script_sha256':sha(__file__),'upper_preflight':{'cut_v':-.070,'topology':upper_report['topology']},'source_opening_preflight':source_report,'numeric_preflight':num,'local_combined_topology':local_topo,'local_combined_audit':local,'final_local_collar_audit':collar_audit,'final_body':final,'protection':protection,'render_gate_passed':passed,'render_gate':'actual combined upper+wrist and neighboring source collar must have self0/flipped0 before full gray renders','seconds_before_render':time.time()-started,'limits':['Local self0, if achieved, is an engineering gate only; independent visual/contact review still required.','No new toe guessing or guide section selection: actual C11 upper geometry is retained.','Old UV/groom/shape bindings invalid; no animation, engine, color or deployment.']};(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 if not passed:print('STOP no full renders: local mesh self/intersection gate failed');return
 cam=s.camera;frontloc=cam.location.copy();frontrot=cam.rotation_euler.copy();scale=cam.data.ortho_scale
 for view in ['front','inside','three-quarter']:
  if view=='inside':cam.location=(4,-6,3);cam.rotation_euler=(Vector((1.17,-.95,1.96))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25
  elif view=='three-quarter':cam.location=(6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
  s.render.filepath=str(out/('gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
 cam.location=frontloc;cam.rotation_euler=frontrot;cam.data.ortho_scale=scale;print('RESULT '+json.dumps({'localself':local['self_intersections'],'collarself':collar_audit['self_intersections'],'final':final,'protection':protection}))

def main():
 upper,upper_report=upper_cut(-.070)
 if not upper_report['valid_single_open_upper_patch']:print('STOP upper patch is not one valid component/opening');return
 if a.preflight_only:return
 upco=[v.co[:] for v in upper.data.vertices];upfs=[list(f.vertices) for f in upper.data.polygons];uploop=upper_report['boundary_loops'][0]['vertex_indices'];(out/'upper-reused-data.json').write_text(json.dumps({'vertices':upco,'faces':upfs,'boundary':uploop,'source_vertex_map':upper_report['source_vertex_map'],'cut_vertex_map':upper_report['cut_vertex_map']})+'\n')
 s,body,target,initial,border,source_report=source_opening()
 if a.input_only:return
 rep,data=numerical(s,body,initial,border,upco,upfs,uploop,upper_report)
 if rep['minimum_1_minus_kappa_inner']<=0 or rep['total_reversing_rails']>0:print('STOP numeric fold guard failed');return
 if a.numeric_only:return
 build(s,body,target,initial,border,source_report,upco,upfs,upper_report,rep,data)
main()
