"""C46r2 last form candidate: full reference envelope front/back 3D skin.
No tube, centerline bend, independent palm or toe extrusion. Shared shoulder-back
hole; smooth padded front disk/back annulus, both welded at whole arm outline.
"""
from pathlib import Path
import numpy as np,json,math
from scipy.interpolate import CubicSpline,RBFInterpolator
from scipy.spatial import Delaunay
from scipy.sparse import diags,coo_matrix
from scipy.sparse.linalg import spsolve
R=Path(__file__).resolve().parents[3];O=R/'artifacts/character-right-arm-c46/r2';d=np.load(O/'torso-chart-data.npz');patch=d['co'];patch_triangles=d['tri'].copy();root=patch[808:872];cam=json.load(open(R/'artifacts/character-strum-paw-c37/baseline-inspection.json'));cl=np.array(cam['camera_location']);rotation=cam['camera_rotation'][0];up=np.array([0,math.cos(rotation),math.sin(rotation)]);ppu=1254/cam['camera_scale']
def uv_pixels(p):
 p=np.asarray(p);return np.c_[(p[:,0]-627)/ppu,(627-p[:,1])/ppu]
def uv_world(p):return np.c_[p[:,0]-cl[0],(p-cl)@up]
def inside(q,poly):
 x=q[:,0];y=q[:,1];v=np.zeros(len(q),bool)
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):v^=((a[1]>y)!=(b[1]>y))&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1]+1e-30)+a[0])
 return v
control=np.array([[417,425],[366,412],[320,440],[270,476],[232,515],[211,546],[205,565],[211,586],[229,607],[265,623],[316,630],[366,642],[410,659],[438,672],[456,674],[466,670],[476,665],[484,660],[491,654],[500,649],[507,644],[514,625],[508,607],[488,585],[458,565],[427,547],[393,529],[360,516],[332,507],[313,507],[357,495],[390,497],[420,516],[433,490],[434,454],[417,425]],float);tt=np.r_[0,np.cumsum(np.linalg.norm(np.diff(control,axis=0),axis=1))];spl=CubicSpline(tt,control,bc_type='periodic');t=np.linspace(0,tt[-1],193)[:-1];outerpx=spl(t);outer=uv_pixels(outerpx);N=len(outer);hole=uv_world(root);assert np.all(inside(hole,outer)),{'hole_outside_root':np.flatnonzero(~inside(hole,outer)).tolist()}
u,v=np.meshgrid(np.arange(outer[:,0].min()+.024,outer[:,0].max(),.024),np.arange(outer[:,1].min()+.024,outer[:,1].max(),.024));grid=np.c_[u.ravel(),v.ravel()];grid=grid[inside(grid,outer)];pts=np.r_[outer,hole,grid];tri=Delaunay(pts).simplices.copy();constraints={tuple(sorted([i,(i+1)%N])) for i in range(N)}|{tuple(sorted([N+i,N+(i+1)%64])) for i in range(64)}
def det(a,b,c):
 q=pts[b]-pts[a];r=pts[c]-pts[a];return q[0]*r[1]-q[1]*r[0]
def edges(tri):
 e={}
 for j,t in enumerate(tri):
  for a,b in zip(t,np.roll(t,-1)):e.setdefault(tuple(sorted([int(a),int(b)])),[]).append(j)
 return e
em=edges(tri);flips=0
for c,d in sorted(constraints):
 for attempt in range(1000):
  if (c,d) in em:break
  done=False
  for (a,b),ts in em.items():
   if len(ts)!=2 or a in [c,d] or b in [c,d] or (a,b) in constraints:continue
   if det(c,d,a)*det(c,d,b)>=-1e-20 or det(a,b,c)*det(a,b,d)>=-1e-20:continue
   x=next(int(v) for v in tri[ts[0]] if v not in [a,b]);y=next(int(v) for v in tri[ts[1]] if v not in [a,b])
   if det(x,y,a)*det(x,y,b)>=-1e-20:continue
   tri[ts[0]]=[x,y,a];tri[ts[1]]=[y,x,b];flips+=1;em=edges(tri);done=True;break
  if not done:raise RuntimeError({'uninsertable_constraint':[c,d]})
 else:raise RuntimeError('fixed constraint insertion limit')
tri=tri[inside(pts[tri].mean(1),outer)];aa=pts[tri[:,1]]-pts[tri[:,0]];bb=pts[tri[:,2]]-pts[tri[:,0]];ar=aa[:,0]*bb[:,1]-aa[:,1]*bb[:,0];tri[ar<0]=tri[ar<0][:,[0,2,1]];backmask=~inside(pts[tri].mean(1),hole);eback=edges(tri[backmask]);expected=constraints;actual={e for e,v in eback.items() if len(v)==1};assert actual==expected,{'missing':list(expected-actual),'extra':list(actual-expected)}
# Positive-weight harmonic back depth interpolates only source/root and outer
# silhouette conditions. Full common 2D mesh gives one-to-one front/back graphs.
controlxy=np.array([[375,430],[315,490],[240,550],[260,590],[350,580],[450,620],[480,656]],float);controly=np.array([-.25,-.60,-1.00,-1.09,-1.09,-1.083,-1.083]);rbf=RBFInterpolator(uv_pixels(controlxy),controly,kernel='thin_plate_spline',degree=1,smoothing=1e-5);back=np.clip(rbf(pts),-1.12,-.20);boundary=np.arange(N+64);back[N:N+64]=root[:,1];ed=np.array(list(edges(tri)));weights=1/np.maximum(1e-8,np.linalg.norm(pts[ed[:,0]]-pts[ed[:,1]],axis=1));ii=np.r_[ed[:,0],ed[:,1]];jj=np.r_[ed[:,1],ed[:,0]];ww=np.r_[weights,weights];L=diags(np.bincount(ii,weights=ww,minlength=len(pts)))-coo_matrix((ww,(ii,jj)),shape=(len(pts),len(pts))).tocsr();free=np.arange(N+64,len(pts));back[free]=spsolve(L[free][:,free],-L[free][:,boundary]@back[boundary]);dist=np.full(len(pts),1e9);dh=np.full(len(pts),1e9)
for poly,target in [(outer,dist),(hole,dh)]:
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  v=b-a;t=np.clip((pts-a)@v/(v@v),0,1);target[:]=np.minimum(target,np.linalg.norm(pts-(a+t[:,None]*v),axis=1))
dist[:N]=0;maxdepth=RBFInterpolator(uv_pixels(np.array([[390,425],[307,501],[258,561],[358,582],[463,627]],float)),np.array([.32,.34,.29,.27,.26]),kernel='thin_plate_spline',degree=1,smoothing=1e-4)(pts);maxdepth=np.clip(maxdepth,.25,.34);depth=maxdepth*np.sqrt(np.maximum(0,1-(1-np.clip(dist/.18,0,1))**2));depth[:N]=0
# Shallow source-observed toe separations displace the same front surface,
# fade at both ends; no Boolean, finger cylinder or independently closed toe.
groove=np.zeros(len(pts))
for line in [[[458,639],[466,665]],[[490,616],[501,642]]]:
 a,b=uv_pixels(line);v=b-a;t=np.clip((pts-a)@v/(v@v),0,1);dd=np.linalg.norm(pts-(a+t[:,None]*v),axis=1);groove+=.008*np.exp(-(dd/.014)**2)*np.sin(np.pi*t)**.7
np.savez_compressed(O/'envelope-r2-plan.npz',patch_co=patch,patch_tri=patch_triangles,uv=pts,front_tri=tri,back_tri=tri[backmask],back_y=back,depth=depth,groove=groove,dist_hole=dh,root=root,outer_count=N,up=up,camera_location=cl);result={'scope':'Last C46 shape candidate, complete projected-envelope padded front/back surfaces','no_tube_or_bend_clamp':True,'no_separate_palm_root_ring':True,'contour_control_original_pixels':control.tolist(),'outer_sample_count':N,'shared_shoulder_back_hole_count':64,'root_hole_all_inside_original_arm_envelope':True,'triangles_front':len(tri),'triangles_back_annulus':int(backmask.sum()),'all_boundary_edges_exact':True,'constraint_edge_flips':flips,'depth_boundary':'Frozen reference width data; unseen side depth is explicit .25..34u plush-volume assumption. Actual body/wood depth inequalities audited after assembly.','groove_max_u':float(groove.max()),'reference_shape_revision_reason':'r1 rejected for four muscle masses/V elbow and wrist black slit. r2 replaces entire tube/frame interface by single graph surfaces and original projected S envelope.'};(O/'envelope-r2-plan.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
