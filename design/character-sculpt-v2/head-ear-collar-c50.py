"""C50: a genuine XYZ tangent collar from source skin into a clean ear roof.
Gray prototype only. Does not inherit rejected C48 art or replace source identity.
"""
import bpy,bmesh,numpy as np,math,json,hashlib,sys,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
R=Path(__file__).resolve().parents[2];NAME='Miao / continuous pear and rounded-square face'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sm(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
ANG=math.radians(7.5);C,S=math.cos(ANG),math.sin(ANG)
def local(p):
 q=np.array(p,float).copy();x=q[...,0]-.04;y=q[...,1]-.03;q[...,0]=x*C+y*S;q[...,1]=.03-x*S+y*C;return q
def world(q):
 p=np.array(q,float).copy();x=p[...,0];y=p[...,1]-.03;p[...,0]=x*C-y*S+.04;p[...,1]=.03+x*S+y*C;return p
def co(m):
 p=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',p);return p.reshape(-1,3)
def boundary(bm):
 adj={}
 for e in bm.edges:
  if e.is_boundary:
   u,v=e.verts;adj.setdefault(u,[]).append(v);adj.setdefault(v,[]).append(u)
 assert adj and all(len(x)==2 for x in adj.values());start=min(adj,key=lambda v:tuple(v.co));loop=[start];prev=None;cur=start
 for i in range(len(adj)+1):
  nxt=adj[cur][0] if adj[cur][0]!=prev else adj[cur][1]
  if nxt==start:break
  loop.append(nxt);prev,cur=cur,nxt
 assert len(loop)==len(adj);return loop
COEF=np.load(R/'artifacts/character-ear-c48/roof-fit-degree4.npz')['coef']
def roof(V):
 x=V[:,0];y=V[:,1]-.03;Z=np.stack([np.ones(len(x)),x*x,x**4,y*y,y**4,x*x*y*y],1)@COEF
 for side in [-1,1]:
  dx=x-side*.47;dy=V[:,1]-.015;ear=3.425-1.8*(np.sqrt(dx*dx+.012**2)-.012)-18*dy*dy;delta=ear-Z;k=.018;weight=sm(-k,k,delta);Z=np.maximum(Z,ear)+np.maximum(0,k-np.abs(delta))**2/(4*k)-.018*np.exp(-(dx/.055)**4-((V[:,1]+.045)/.030)**2)*weight
 return Z

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',default='artifacts/character-ear-c50/candidate-1');ap.add_argument('--render',action='store_true');ap.add_argument('--wide',action='store_true');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else[]);O=R/args.out;O.mkdir(parents=True,exist_ok=True)
 if (O/'receipt.json').exists():raise RuntimeError('Frozen output exists')
 src=R/'artifacts/character-alignment-c38/head-expression-only/miao-c38-coupled-head-gray.blend';assert sha(src)=='f481e8a0c00eb4ec5baf5d9c43a6bc250f5a28c4475d9d9cba0ea360ca1c8439';bpy.ops.wm.open_mainfile(filepath=str(src));b=bpy.data.objects[NAME];m=b.data;P=co(m);sourceids=np.empty(len(P),np.int32);m.attributes['C23 source vertex id'].data.foreach_get('value',sourceids);bm=bmesh.new();bm.from_mesh(m);can=bm.verts.layers.int.get('Miao_C35_vertex_id') or bm.verts.layers.int.new('Miao_C35_vertex_id');sid=bm.verts.layers.int.get('C23 source vertex id');bm.verts.ensure_lookup_table();old=list(bm.verts);lookup={v:i for i,v in enumerate(old)}
 for i,v in enumerate(old):v[can]=i+1
 for side in [-1,1]:
  n=np.array([.5*side,0,1]);n/=np.linalg.norm(n);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector(world(np.array([0,0,3.30]))),plane_no=Vector((n[0]*C,n[0]*S,n[2])),clear_outer=True,clear_inner=False)
 loop=boundary(bm);bm.normal_update();B=local(np.array([v.co[:] for v in loop]));uv=B[:,:2];area=.5*np.sum(uv[:,0]*np.roll(uv[:,1],-1)-uv[:,1]*np.roll(uv[:,0],-1))
 if area<0:loop.reverse();B=B[::-1].copy()
 normals=np.array([v.normal[:] for v in loop]);nx=normals[:,0].copy();ny=normals[:,1].copy();normals[:,0]=nx*C+ny*S;normals[:,1]=-nx*S+ny*C;tangent=np.roll(B,-1,0)-np.roll(B,1,0);tangent/=np.linalg.norm(tangent,axis=1)[:,None];T=np.cross(tangent,normals);T/=np.linalg.norm(T,axis=1)[:,None];cutn=np.c_[.5*np.sign(B[:,0]),np.zeros(len(B)),np.ones(len(B))];sgn=np.einsum('ij,ij->i',T,cutn);T[sgn<0]*=-1
 center=np.array([0,.03]);inner_ratio=.78 if args.wide else .94;Ixy=center+inner_ratio*(B[:,:2]-center);I=np.c_[Ixy,roof(Ixy)];d=I-B;length=np.linalg.norm(d,axis=1);D0=T*length[:,None];eps=1e-4;gradient=np.stack([(roof(Ixy+np.array([eps,0]))-roof(Ixy-np.array([eps,0])))/(2*eps),(roof(Ixy+np.array([0,eps]))-roof(Ixy-np.array([0,eps])))/(2*eps)],1);D1=np.c_[d[:,:2],np.sum(gradient*d[:,:2],axis=1)];D1*=((.55*length)/np.maximum(np.linalg.norm(D1,axis=1),1e-12))[:,None]
 prior=loop;collars=[];Qlist=[];newfaces=[]
 layers=[.025,.10,.25,.43,.62,.80,.95,1.] if args.wide else [.12,.28,.46,.64,.82,1.]
 for t in layers:
  Q=(2*t**3-3*t*t+1)*B+(t**3-2*t*t+t)*D0+(-2*t**3+3*t*t)*I+(t**3-t*t)*D1
  if args.wide:Q[:,2]+=(roof(Q[:,:2])-Q[:,2])*sm(.14,.72,t)
  ring=[]
  for q in Q:
   v=bm.verts.new(world(q));v[can]=v[sid]=0;ring.append(v)
  for i in range(len(loop)):
   f=bm.faces.new((prior[i],prior[(i+1)%len(loop)],ring[(i+1)%len(loop)],ring[i]));f.smooth=True;newfaces.append(f)
  prior=ring;collars.append(ring);Qlist.append(Q)
 # Inner roof uses a fresh constrained triangulation at this actual inner ring.
 U=I[:,:2];grid=[]
 for x in np.arange(U[:,0].min()+.013,U[:,0].max(),.018):
  for y in np.arange(U[:,1].min()+.013,U[:,1].max(),.018):
   u=U;v=np.roll(U,-1,0);inside=np.count_nonzero(((u[:,1]>y)!=(v[:,1]>y))&(x<(v[:,0]-u[:,0])*(y-u[:,1])/(v[:,1]-u[:,1]+1e-100)+u[:,0]))%2
   if not inside:continue
   pt=np.array([x,y]);e=v-u;t=np.clip(np.sum((pt-u)*e,1)/np.sum(e*e,1),0,1);dist=np.linalg.norm(pt-u-e*t[:,None],axis=1).min()
   if dist>.007:grid.append(pt)
 N=len(U);xy=np.vstack([U,np.array(grid)]);coords,edges,faces,ids,_,_=delaunay_2d_cdt([Vector(p) for p in xy],[(i,(i+1)%N) for i in range(N)],[list(range(N))],1,1e-10,True);V=np.array(coords,float);F=np.array(faces,np.int32);maps={}
 for i,idxs in enumerate(ids):
  for k in idxs:
   if k<N:assert k not in maps;maps[k]=i
 assert len(maps)==N and len(set(maps.values()))==N
 outv={}
 for k,i in maps.items():V[i]=U[k];outv[i]=prior[k]
 Z=roof(V)
 for i in range(len(V)):
  if i not in outv:
   v=bm.verts.new(world(np.array([*V[i],Z[i]])));v[can]=v[sid]=0;outv[i]=v
 for inds in F:
  f=bm.faces.new(tuple(outv[int(i)] for i in inds));f.smooth=True;newfaces.append(f)
 bm.normal_update();bm.verts.index_update();bm.faces.index_update();kept=[]
 for v in bm.verts:
  if v in lookup:
   i=lookup[v];assert np.array_equal(np.array(v.co,dtype=np.float32),P[i]);v[can]=i+1;kept.append(i)
  else:v[can]=v[sid]=0
 kept=np.array(kept,np.int32);missing=np.ones(len(P),bool);missing[kept]=False;L=local(P);protected=L[:,2]+.5*np.abs(L[:,0])<=3.29;assert not np.any(missing&protected);assert set(np.flatnonzero(sourceids==0)).issubset(set(kept.tolist()));report={'stage':'C50 actual XYZ Hermite collar plus fresh source-fitted short-ear roof; gray preview before self audit','source_sha256':sha(src),'cut_boundary_count':N,'collar_layers':len(layers),'inner_loop_scale':inner_ratio,'roof_unified_along_wide_collar':args.wide,'new_inner_roof_vertices':len(V)-N,'new_inner_roof_triangles':len(F),'ear_peak_target':3.425,'outer_actual_normal_z_range':[float(normals[:,2].min()),float(normals[:,2].max())],'no_normal_z_division':True,'source_tangent_conormal_dot_min':float(np.min(np.abs(np.einsum('ij,ij->i',T,normals)))),'maximum_outer_to_inner_distance':float(length.max()),'all_retained_source_positions_bit_exact':True,'deleted_source_vertices':int(missing.sum()),'new_zero_canonical_points':sum(v not in lookup for v in bm.verts),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_vertices':sum(not v.link_faces for v in bm.verts),'signed_volume':bm.calc_volume(signed=True),'self_intersection_audit':'deferred until actual large-shape image review','art_pass':False,'limits':['Gray preview only; no skin/groom/UV/rig/video acceptance.','No source triangle compression, no detached ear objects, no fake shading normals.']};bm.to_mesh(m);m.update();bm.free();bpy.context.view_layer.update();np.savez_compressed(O/'collar-evidence.npz',outer=B,outer_normals=normals,outer_conormal=T,inner=I,outer_derivative=D0,inner_derivative=D1,layers=np.array(Qlist),source_retained=kept,source_deleted=np.flatnonzero(missing));scene=bpy.context.scene;scene.cycles.samples=24;scene.cycles.seed=17;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;bpy.context.preferences.filepaths.save_version=0;native=O/'miao-c50-xyz-collar-gray.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);report['native_sha256']=sha(native);(O/'receipt.json').write_text(json.dumps(report,indent=2));(O/'executed-build-script.py').write_text(Path(__file__).read_text());print('PREVIEW '+json.dumps(report),flush=True)
 if args.render:
  cam=scene.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();sc=cam.data.ortho_scale
  for name,pos,target,zoom in [('front',None,None,None),('ears',Vector((0,-6,3.30)),Vector((0,0,3.28)),1.45),('three-quarter',Vector((6,-9,3.9)),Vector((.09881,0,1.609)),sc)]:
   if pos is None:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=sc
   else:cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom
   bpy.context.view_layer.update();scene.render.filepath=str(O/('gray-'+name+'.png'));bpy.ops.render.render(write_still=True)
 print('RESULT '+json.dumps({'native_sha256':report['native_sha256'],'art_pass':False}),flush=True)
main()
