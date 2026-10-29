"""Frozen C46r1 analytic form plan from original-image guides; no Blender ABI."""
from pathlib import Path
import numpy as np,json,hashlib,math
from scipy.interpolate import CubicSpline,PchipInterpolator,make_interp_spline
R=Path(__file__).resolve().parents[3];O=R/'artifacts/character-right-arm-c46';d=np.load(O/'torso-chart-data.npz');co=d['co'].copy();pts=d['pts'];rx=d['rx'];ry=d['ry'];outer=808;ni=64

def surf(q):
 th=q[:,0];z=q[:,1];ex=2.4+.8*np.clip((z-2.32)/.28,0,1);a=np.cos(th);b=np.sin(th);r=(abs(a)**ex+abs(b)**ex)**(-1/ex);return np.c_[-np.polyval(rx,z)*r*a,.03-np.polyval(ry,z)*r*b,z]
eps=1e-5;da=surf(pts+[eps,0])-surf(pts-[eps,0]);db=surf(pts+[0,eps])-surf(pts-[0,eps]);normal=np.cross(da,db);normal/=np.linalg.norm(normal,axis=1)[:,None];rho=np.sqrt(((pts[:,0]-.55)/.30)**2+((pts[:,1]-2.205)/.145)**2);dist=np.maximum(0,rho-1)*.17;b=.055;lift=np.where(dist<b,b-np.sqrt(np.maximum(0,b*b-(dist-b)**2)),0);lift[:outer]=0;co+=normal*lift[:,None];root=co[outer:outer+ni];center=root.mean(0);N=normal[outer:outer+ni].mean(0);N/=np.linalg.norm(N);W0=root[0]-root[32];W0-=N*(W0@N);W0/=np.linalg.norm(W0)
cam=json.load(open(R/'artifacts/character-strum-paw-c37/baseline-inspection.json'));cl=np.array(cam['camera_location']);rot=cam['camera_rotation'][0];up=np.array([0,math.cos(rot),math.sin(rot)]);scale=cam['camera_scale'];c_up=cl@up

def world(px,py,y):return np.array([cl[0]+(px/1254-.5)*scale,y,(c_up+(.5-py/1254)*scale-up[1]*y)/up[2]])
caproot=world(433,602,-1.225);end=world(480,656,-1.083);D=end-caproot;D[1]=0;L=np.linalg.norm(D);D/=L
C=[center,center+N*.055,world(315,490,-.67),world(270,550,-1.12),world(310,575,-1.225),world(365,586,-1.225),caproot];rad=np.array([[.195,.145],[.200,.15],[.225,.17],[.230,.145],[.230,.135],[.225,.135],[.205,.13]])
C=np.array(C);tt=np.r_[0,np.cumsum(np.linalg.norm(np.diff(C,axis=0),axis=1))];spl=make_interp_spline(tt,C,k=5,bc_type=([(1,N),(2,np.zeros(3))],[(1,D),(2,np.zeros(3))]));dense=np.linspace(0,tt[-1],2001);p=spl(dense);length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];ss=np.linspace(0,length[-1],81);ts=np.interp(ss,length,dense);path=spl(ts);v=spl(ts,1);a=spl(ts,2);speed=np.linalg.norm(v,axis=1);T=v/speed[:,None];K=(a-T*np.sum(T*a,axis=1)[:,None])/(speed[:,None]**2);r=PchipInterpolator(tt,rad)(ts);regular=np.arange(64)*2*np.pi/64;eta=np.linspace(-1,1,33);gridphase=np.r_[np.arccos(eta[::-1]),2*np.pi-np.arccos(eta[1:-1])];oldT=N.copy();width=W0.copy();rings=[];metrics=[]

def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)

def rotate(v,a,b):
 c=np.clip(a@b,-1,1);axis=np.cross(a,b);s=np.linalg.norm(axis)
 if s<1e-10:return v.copy()
 axis/=s;return v*c+np.cross(axis,v)*s+axis*(axis@v)*(1-c)
E0=np.cross(N,W0);initialcoords=np.stack([(root-center)@W0,(root-center)@E0,(root-center)@N],1)
for j in range(81):
 tan=T[j];width=rotate(width,oldT,tan);width-=tan*(width@tan);width/=np.linalg.norm(width);target=np.array([-tan[2],0,tan[0]]);target/=np.linalg.norm(target);blend=smooth((ss[j]/ss[-1]-.12)/.70);candidate=width*(1-blend)+target*blend;candidate-=tan*(candidate@tan)
 if np.linalg.norm(candidate)<.1:raise RuntimeError('frame alignment singularity')
 width=candidate/np.linalg.norm(candidate);depth=np.cross(tan,width);depth/=np.linalg.norm(depth);phase=regular*(1-blend)+gridphase*blend;offset=r[j,0]*np.cos(phase)[:,None]*width+r[j,1]*np.sin(phase)[:,None]*depth;k=np.linalg.norm(K[j]);inward=offset@K[j]/max(k,1e-12)
 if k>1e-8:
  limit=.60/k;positive=inward>0;compressed=limit*np.tanh(inward[positive]/limit);offset[positive]+=(compressed-inward[positive])[:,None]*(K[j]/k)
 shape=path[j]+offset;morph=smooth(ss[j]/.24);transport=path[j]+initialcoords[:,0,None]*width+initialcoords[:,1,None]*depth+initialcoords[:,2,None]*tan;shape=(1-morph)*transport+morph*shape
 if j==0:shape=root.copy()
 elif k>1e-8:
  final_offset=shape-path[j];inner=final_offset@(K[j]/k);positive=inner>0;limit=.60/k;final_offset[positive]+=(limit*np.tanh(inner[positive]/limit)-inner[positive])[:,None]*(K[j]/k);shape=path[j]+final_offset
 rings.append(shape);metrics.append({'station':j,'radius_of_curvature':float(1/k) if k>1e-8 else None,'max_inward_KdotOffset':float(np.max((shape-path[j])@K[j])),'local_sweep_metric_min':float(1-np.max((shape-path[j])@K[j])),'center':path[j].tolist(),'radii':r[j].tolist()});oldT=tan
W=np.array([-D[2],0,D[0]]);W/=np.linalg.norm(W);endW=np.array([.90,0,.436]);endW/=np.linalg.norm(endW);cap=[];M=14;L=float(L);rootF=rings[-1][np.arange(32,-1,-1)];rootB=np.r_[rings[-1][32:33],rings[-1][33:64],rings[-1][0:1]];warpF=rootF-(caproot+eta[:,None]*.205*W-np.sqrt(np.maximum(0,1-eta**2))[:,None]*np.array([0,.13,0]));warpB=rootB-(caproot+eta[:,None]*.205*W+np.sqrt(np.maximum(0,1-eta**2))[:,None]*np.array([0,.13,0]))
for j in range(M+1):
 t=j/M;ww=W*(1-smooth(t))+endW*smooth(t);ww/=np.linalg.norm(ww);width=.205*np.sqrt(1-.36*t*t);web=np.exp(-((eta-.275)/.11)**2)+np.exp(-((eta+.275)/.11)**2);endS=L*(.80+.20*np.sqrt(np.maximum(0,1-eta**2)))-.015*web;sp=t*endS;centerline=caproot+sp[:,None]*D+eta[:,None]*width*ww;back=-1.095+.012*smooth(t);half=.13*np.sqrt(np.maximum(0,1-eta**2))*np.sqrt(max(0,1-t*t))*(1-.10*web*smooth((t-.50)/.40));F=centerline.copy();B=centerline.copy();F[:,1]=back-2*half;B[:,1]=back;F+=warpF*(1-t)**2;B+=warpB*(1-t)**2
 if j==0:F=rootF.copy();B=rootB.copy()
 cap.append(np.stack([F,B]))
np.savez_compressed(O/'candidate-r1-geometry-plan.npz',patch_co=co,patch_tri=d['tri'],root=root,rings=np.array(rings),cap=np.array(cap),centers=path,curvature=K,frame_metric=np.array([q['local_sweep_metric_min'] for q in metrics]),D=D,W=W,cap_length=L)
receipt={'scope':'C46r1 frozen shape plan, source-image-guided projected widths, continuous domed cap not3extruded stubs','reference_guides_sha256':hashlib.sha256((O/'reference-guides.json').read_bytes()).hexdigest(),'spline':'C4 quintic interpolation, endpoint first derivatives root normal/cap tangent and second derivatives0; inward bound audited after root-frame blending','section_radii':rad.tolist(),'control_centers':C.tolist(),'shoulder_blend':'same body patch quarter-circle radial fillet height .055u with exact outer boundary','curvature_inner_limit':'.60R tanh inward component, preserving fuller outer elbow','minimum_analytic_local_sweep_metric':min(q['local_sweep_metric_min'] for q in metrics),'cap':'one33-column front/back grid14rows; welded end edge; 3shallow distal contour lobes; no individual finger extrusions; back skin -1.095→-1.083Y','cap_length':L,'cap_root_width_diameter':.410,'cap_root_depth_diameter':.260,'stations':metrics,'not_proved':'This bound is local analytic sweep metric, not actual global self0 or art pass.'};(O/'candidate-r1-plan.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ['minimum_analytic_local_sweep_metric','cap_length','cap_root_width_diameter','cap_root_depth_diameter']}))
