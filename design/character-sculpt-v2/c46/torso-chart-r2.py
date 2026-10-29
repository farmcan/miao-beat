import numpy as np,json
from pathlib import Path
from scipy.spatial import Delaunay
R=Path('/Users/levi/wrksp/miao-beat');O=R/'artifacts/character-right-arm-c46/r2';r=json.load(open(R/'artifacts/character-right-arm-c41/source-boundary-preflight.json'));p=np.load(R/'artifacts/character-right-arm-c41/source-cut-map.npz');P=p['original'];B=np.array(r['boundary_loops'][0]['coordinates']);zs=np.arange(1.46,2.41,.02);samples=[]
for z in zs:
 m=(abs(P[:,2]-z)<.014)&(P[:,0]<0)&(P[:,1]>.055)
 if m.sum()>10:samples.append([z,float(np.max(-P[m,0])),float(np.max(P[m,1])-.03)])
samples=np.array(samples);rx=np.polyfit(samples[:,0],samples[:,1],4);ry=np.polyfit(samples[:,0],samples[:,2],4);theta=np.arctan2((.03-B[:,1])/np.polyval(ry,B[:,2]),-B[:,0]/np.polyval(rx,B[:,2]));uv=np.c_[theta,B[:,2]];center=np.array([.55,2.20]);aa=uv-center;bb=np.roll(uv,-1,axis=0)-center;cross=aa[:,0]*bb[:,1]-aa[:,1]*bb[:,0];angles=np.unwrap(np.arctan2((uv-center)[:,1],(uv-center)[:,0]));inner=np.c_[.55+.29*np.cos(np.arange(64)*2*np.pi/64),2.20+.125*np.sin(np.arange(64)*2*np.pi/64)];
def inside(q,poly):
 x=q[:,0];y=q[:,1];b=np.zeros(len(q),bool)
 for a,c in zip(poly,np.roll(poly,-1,axis=0)):
  take=(a[1]>y)!=(c[1]>y);b^=take&(x<(c[0]-a[0])*(y-a[1])/(c[1]-a[1]+1e-30)+a[0])
 return b
u,z=np.meshgrid(np.arange(uv[:,0].min()+.025,uv[:,0].max(),.025),np.arange(uv[:,1].min()+.025,uv[:,1].max(),.025));grid=np.c_[u.ravel(),z.ravel()];grid=grid[inside(grid,uv)&~inside(grid,inner)];pts=np.r_[uv,inner,grid];dt=Delaunay(pts);tri=dt.simplices.copy();expected={tuple(sorted([i,(i+1)%len(uv)])) for i in range(len(uv))}|{tuple(sorted([len(uv)+i,len(uv)+(i+1)%len(inner)])) for i in range(len(inner))};flips=0
def orient(a,b,c):
 v=pts[b]-pts[a];w=pts[c]-pts[a];return v[0]*w[1]-v[1]*w[0]
for constraint in sorted(expected):
 for attempt in range(10000):
  em={}
  for j,t in enumerate(tri):
   for a,b in zip(t,np.roll(t,-1)):em.setdefault(tuple(sorted([int(a),int(b)])),[]).append(j)
  if constraint in em:break
  c,d=constraint;done=False
  for (a,b),ts in em.items():
   if len(ts)!=2 or a in constraint or b in constraint or (a,b) in expected:continue
   if orient(c,d,a)*orient(c,d,b)>=-1e-20 or orient(a,b,c)*orient(a,b,d)>=-1e-20:continue
   x=next(int(v) for v in tri[ts[0]] if v not in [a,b]);y=next(int(v) for v in tri[ts[1]] if v not in [a,b])
   if orient(x,y,a)*orient(x,y,b)>=-1e-20:continue
   tri[ts[0]]=[x,y,a];tri[ts[1]]=[y,x,b];flips+=1;done=True;break
  if not done:raise RuntimeError({'constraint_not_insertable':constraint})
 else:raise RuntimeError('finite edge insertion budget')
cent=pts[tri].mean(1);tri=tri[inside(cent,uv)&~inside(cent,inner)];ed={}
for t in tri:
 for a,b in zip(t,np.roll(t,-1)):e=tuple(sorted([int(a),int(b)]));ed[e]=ed.get(e,0)+1
expected={tuple(sorted([i,(i+1)%len(uv)])) for i in range(len(uv))}|{tuple(sorted([len(uv)+i,len(uv)+(i+1)%len(inner)])) for i in range(len(inner))};actual={e for e,n in ed.items() if n==1};missing=expected-actual;extra=actual-expected;result={'torso_fit_unpolluted_back_samples':samples.tolist(),'rx_polynomial':rx.tolist(),'ry_polynomial':ry.tolist(),'uv_bbox':[uv.min(0).tolist(),uv.max(0).tolist()],'chart_sector_sign_counts':[int((cross>0).sum()),int((cross<0).sum()),int((cross==0).sum())],'boundary_radial_turns':float(abs(angles[-1]-angles[0])/(2*np.pi)),'explicit_constraint_edge_flips':flips,'Delaunay_kept_triangles':len(tri),'Delaunay_expected_boundary_edges':len(expected),'Delaunay_missing_boundary_edges':len(missing),'Delaunay_extra_boundary_edges':len(extra),'Delaunay_missing_samples':[list(e) for e in list(missing)[:20]],'Delaunay_safe_to_use_as_annulus':not missing and not extra,'no_forced_bridge':True};(O/'torso-chart-preflight.json').write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(O/'torso-chart-data.npz',uv=uv,inner=inner,pts=pts,tri=tri,rx=rx,ry=ry);print(json.dumps({k:v for k,v in result.items() if k!='torso_fit_unpolluted_back_samples'}))
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import spsolve

def surf(q):
 th=q[:,0];zz=q[:,1];ex=2.4+.8*np.clip((zz-2.32)/.28,0,1);ct=np.cos(th);st=np.sin(th);rad=(np.abs(ct)**ex+np.abs(st)**ex)**(-1/ex);return np.c_[-np.polyval(rx,zz)*rad*ct,.03-np.polyval(ry,zz)*rad*st,zz]
base=surf(pts);errors=np.zeros_like(base);errors[:len(uv)]=B-base[:len(uv)];edlist=np.array(list(ed));weights=1/np.maximum(1e-8,np.linalg.norm(pts[edlist[:,0]]-pts[edlist[:,1]],axis=1));ii=np.r_[edlist[:,0],edlist[:,1]];jj=np.r_[edlist[:,1],edlist[:,0]];ww=np.r_[weights,weights];L=diags(np.bincount(ii,weights=ww,minlength=len(pts)))-coo_matrix((ww,(ii,jj)),shape=(len(pts),len(pts))).tocsr();nb=len(uv)+len(inner);free=np.arange(nb,len(pts));boundary=np.arange(nb);errors[free]=spsolve(L[free][:,free],-L[free][:,boundary]@errors[boundary]);co=base+errors;co[:len(uv)]=B
vv=pts[tri[:,1]]-pts[tri[:,0]];ww=pts[tri[:,2]]-pts[tri[:,0]];det=vv[:,0]*ww[:,1]-vv[:,1]*ww[:,0];tri[det<0]=tri[det<0][:,[0,2,1]];norm=np.cross(co[tri[:,1]]-co[tri[:,0]],co[tri[:,2]]-co[tri[:,0]]);cc=pts[tri].mean(1);dth=(surf(cc+np.array([1e-5,0]))-surf(cc-np.array([1e-5,0])))/2e-5;dz=(surf(cc+np.array([0,1e-5]))-surf(cc-np.array([0,1e-5])))/2e-5;expectednorm=np.cross(dth,dz);signed=(norm*expectednorm).sum(1);result['actual_3d_patch_positive_orientation']=bool(np.all(signed>0));result['patch_nonpositive_triangles']=int((signed<=0).sum());result['patch_minimum_signed_cross_dot']=float(signed.min());result['harmonic_boundary_max_correction']=float(np.linalg.norm(errors[:len(uv)],axis=1).max());result['patch_analytic_to_actual_max_correction']=float(np.linalg.norm(errors,axis=1).max());(O/'torso-chart-preflight.json').write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(O/'torso-chart-data.npz',uv=uv,inner=inner,pts=pts,tri=tri,rx=rx,ry=ry,co=co,harmonic_correction=errors);print('PATCH '+json.dumps({k:result[k] for k in ['actual_3d_patch_positive_orientation','patch_nonpositive_triangles','patch_minimum_signed_cross_dot','harmonic_boundary_max_correction']}))
