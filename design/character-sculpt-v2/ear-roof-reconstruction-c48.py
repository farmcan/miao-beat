"""C48 reconstructs a source-cut head roof and short ears as one graph patch.
No source triangle compression, detached ears, nearest source correspondence or
body remesh. A gray diagnostic remains subject to independent art review.
"""
import argparse,bpy,bmesh,numpy as np,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
R=Path(__file__).resolve().parents[2];NAME='Miao / continuous pear and rounded-square face'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sm(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
ANG=math.radians(7.5);C=math.cos(ANG);S=math.sin(ANG)
def local(p):
 q=np.array(p,float).copy();x=q[...,0]-.04;y=q[...,1]-.03;q[...,0]=x*C+y*S;q[...,1]=.03-x*S+y*C;return q
def world(q):
 p=np.array(q,float).copy();x=p[...,0];y=p[...,1]-.03;p[...,0]=x*C-y*S+.04;p[...,1]=.03+x*S+y*C;return p
def meshco(m):
 p=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',p);return p.reshape(-1,3)
def loop_boundary(bm):
 adj={}
 for e in bm.edges:
  if e.is_boundary:
   u,v=e.verts;adj.setdefault(u,[]).append(v);adj.setdefault(v,[]).append(u)
 assert adj and all(len(v)==2 for v in adj.values()),'Actual cut is not a single unbranched boundary'
 start=min(adj,key=lambda v:tuple(v.co));loop=[start];prev=None;cur=start
 for _ in range(len(adj)+1):
  nxt=adj[cur][0] if adj[cur][0]!=prev else adj[cur][1]
  if nxt==start:break
  loop.append(nxt);prev,cur=cur,nxt
 assert len(loop)==len(adj),'Source has multiple loops, do not silently bridge them'
 return loop

def main():
 pa=argparse.ArgumentParser();pa.add_argument('--out',default='artifacts/character-ear-c48/candidate-1');pa.add_argument('--render',action='store_true');pa.add_argument('--c1',action='store_true');a=pa.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else[]);O=R/a.out;O.mkdir(parents=True,exist_ok=True)
 if (O/'receipt.json').exists():raise RuntimeError('Frozen candidate exists; use a new explicit directory')
 src=R/'artifacts/character-alignment-c38/head-expression-only/miao-c38-coupled-head-gray.blend';assert sha(src)=='f481e8a0c00eb4ec5baf5d9c43a6bc250f5a28c4475d9d9cba0ea360ca1c8439';bpy.ops.wm.open_mainfile(filepath=str(src));b=bpy.data.objects[NAME];me=b.data;old=meshco(me);oldids=np.empty(len(old),np.int32);me.attributes['C23 source vertex id'].data.foreach_get('value',oldids)
 bm=bmesh.new();bm.from_mesh(me);can=bm.verts.layers.int.get('Miao_C35_vertex_id') or bm.verts.layers.int.new('Miao_C35_vertex_id');srcattr=bm.verts.layers.int.get('C23 source vertex id');bm.verts.ensure_lookup_table();original=list(bm.verts);lookup={v:i for i,v in enumerate(original)}
 for i,v in enumerate(original):v[can]=i+1
 # Below both planes is untouched connected head/body; everything above is
 # reconstructed, including the previous complete cavity and its bottom lip.
 for side in [-1,1]:
  n=np.array([.5*side,0,1]);n/=np.linalg.norm(n);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector(world(np.array([0,0,3.30]))),plane_no=Vector((n[0]*C,n[0]*S,n[2])),clear_outer=True,clear_inner=False)
 loop=loop_boundary(bm);raw_ring=len(loop)
 # Only newly introduced boundary points may be merged: never source skin.
 mergeable=[v for v in loop if v not in lookup];bmesh.ops.remove_doubles(bm,verts=mergeable,dist=2e-6);loop=loop_boundary(bm);bm.normal_update();B=local(np.array([v.co[:] for v in loop]));uv=B[:,:2];area=.5*np.cross(uv,np.roll(uv,-1,0)).sum()
 if area<0:loop.reverse();B=B[::-1].copy();uv=B[:,:2]
 normals=np.array([v.normal[:] for v in loop]);nx=normals[:,0].copy();ny=normals[:,1].copy();normals[:,0]=nx*C+ny*S;normals[:,1]=-nx*S+ny*C;grad=-normals[:,:2]/np.maximum(normals[:,2:3],.04);gn=np.linalg.norm(grad,axis=1);grad*=np.minimum(1,12/np.maximum(gn,1e-12))[:,None]
 print('CUT '+json.dumps({'ring_before_local_newpoint_weld':raw_ring,'ring_after':len(loop),'bounds':[B.min(0).tolist(),B.max(0).tolist()]}),flush=True)
 # A fresh low-density constrained XY triangulation. A height graph cannot fold
 # over its own interior. Original border coordinates are reused, not snapped.
 grid=[]
 for x in np.arange(uv[:,0].min()+.013,uv[:,0].max(),.018):
  for y in np.arange(uv[:,1].min()+.013,uv[:,1].max(),.018):
   px=np.array([x,y]);u=uv;v=np.roll(uv,-1,0);inside=bool(np.count_nonzero(((u[:,1]>y)!=(v[:,1]>y))&(x<(v[:,0]-u[:,0])*(y-u[:,1])/(v[:,1]-u[:,1]+1e-100)+u[:,0]))%2)
   if not inside:continue
   e=v-u;t=np.clip(np.sum((px-u)*e,1)/np.sum(e*e,1),0,1);d=np.linalg.norm(px-u-e*t[:,None],axis=1).min()
   if d>.007:grid.append(px)
 N=len(loop);inputuv=np.vstack([uv,np.array(grid)]);edges=[(i,(i+1)%N) for i in range(N)];coords,cedges,faces,origverts,_,_=delaunay_2d_cdt([Vector(p) for p in inputuv],edges,[list(range(N))],1,1e-10,True);V=np.array(coords,float);F=np.array(faces,np.int32);assert F.ndim==2 and F.shape[1]==3
 boundary_map={}
 for i,idxs in enumerate(origverts):
  for k in idxs:
   if k<N:
    assert k not in boundary_map,'Boundary point used twice';boundary_map[k]=i
 assert len(boundary_map)==N and len(set(boundary_map.values()))==N,'Constrained triangulation merged a real source boundary'
 # Keep exact original border XY instead of CDT's representational copy.
 for k,i in boundary_map.items():V[i]=uv[k]
 e0=V[F[:,1]]-V[F[:,0]];e1=V[F[:,2]]-V[F[:,0]];sectors=np.cross(e0,e1);assert sectors.min()>1e-13,'Invalid XY chart triangle'
 # Fit actual clean head roof data, not an ellipsoid replacement. The source
 # ear-contaminated band is excluded from this least-squares chart prototype.
 coef=np.load(R/'artifacts/character-ear-c48/roof-fit-degree4.npz')['coef'];x=V[:,0];y=V[:,1]-.03;basis=np.stack([np.ones(len(x)),x*x,x**4,y*y,y**4,x*x*y*y],axis=1);roof=basis@coef;Z=roof.copy();ear_contribution=[]
 for side in [-1,1]:
  dx=x-side*.47;dy=V[:,1]-.015;ear=3.425-1.8*(np.sqrt(dx*dx+.012**2)-.012)-18*dy*dy;delta=ear-Z;k=.018;weight=sm(-k,k,delta);smoothmax=np.maximum(Z,ear)+np.maximum(0,k-np.abs(delta))**2/(4*k);bowl=.018*np.exp(-(dx/.055)**4-((V[:,1]+.045)/.030)**2)*weight;Z=smoothmax-bowl;ear_contribution.append({'side':side,'peak_target_z':3.425,'half_width_reference_u':.11,'half_depth_reference_u':.10,'shallow_cup_max_u':.018})
 # Screened harmonic residual carries the exact curved source boundary into the
 # new fitted surface, without nearest boundary fields or a body seam plate.
 bd=np.array(list(boundary_map.values()),np.int32);boundary_value=np.zeros(len(V));
 for k,i in boundary_map.items():boundary_value[i]=B[k,2]-Z[i]
 E=np.unique(np.sort(np.vstack([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]),1),axis=0);weight=1/np.maximum(np.sum((V[E[:,1]]-V[E[:,0]])**2,1),1e-14);diag=np.zeros(len(V));np.add.at(diag,E[:,0],weight);np.add.at(diag,E[:,1],weight);lam=.06**2;corr=boundary_value.copy();free=np.ones(len(V),bool);free[bd]=False;err=1
 for it in range(2000):
  sums=np.zeros(len(V));np.add.at(sums,E[:,0],weight*corr[E[:,1]]);np.add.at(sums,E[:,1],weight*corr[E[:,0]]);new=lam*sums/(1+lam*diag);new[bd]=boundary_value[bd];err=float(np.abs(new-corr).max());corr=new
  if err<1e-10:break
 c1_receipt=None
 if a.c1:
  import subprocess
  prototype=Z.copy();pri=[];targets=[];neighbors=[[] for _ in V]
  for u,v in E:neighbors[u].append(v);neighbors[v].append(u)
  for k,i in boundary_map.items():
   ns=np.array(neighbors[i],np.int32);dp=V[ns]-V[i];gproto=np.linalg.lstsq(dp,prototype[ns]-prototype[i],rcond=None)[0]
   for j in ns:
    if free[j]:pri.append(j);targets.append(boundary_value[i]+np.dot(grad[k]-gproto,V[j]-V[i]))
  f=O/'surface-solve-input.npz';np.savez_compressed(f,xy=V,edges=E,boundary=bd,boundary_values=boundary_value[bd],prior_indices=np.array(pri,np.int32),prior_values=np.array(targets));external=R/'artifacts/c29-qp-env/bin/python';solver=R/'design/character-sculpt-v2/ear-roof-surface-solve-c48.py';run=subprocess.run([str(external),str(solver),str(f)],capture_output=True,text=True);(O/'surface-solve.log').write_text(run.stdout+run.stderr);assert run.returncode==0,'External surface solver failed';corr=np.load(O/'surface-solve-output.npz')['correction'];c1_receipt=json.loads((O/'surface-solve-receipt.json').read_text());c1_receipt['source_boundary_minimum_normal_z']=float(normals[:,2].min());c1_receipt['source_gradient_norm_max_before_limit']=float(gn.max());c1_receipt['source_gradient_norm_limited_count']=int((gn>12).sum())
 Z+=corr
 for k,i in boundary_map.items():Z[i]=B[k,2]
 floor=3.30-.5*np.abs(x);bad=(Z<floor-2e-6)&free;report={'stage':'C48 head-roof/short-ear graph candidate; independent visual review pending','source_sha256':sha(src),'actual_source_boundary_count':N,'pre_weld_boundary_count':raw_ring,'new_interior_chart_vertices':int(free.sum()),'new_patch_triangles':len(F),'minimum_chart_triangle_signed_double_area':float(sectors.min()),'screened_harmonic_iterations':it+1,'screened_harmonic_delta':err,'prototype_below_retained_cut_count':int(bad.sum()),'prototype_min_cut_clearance':float((Z[free]-floor[free]).min()),'ear_targets':ear_contribution,'source_fit':json.loads((R/'artifacts/character-ear-c48/roof-fit-degree4.json').read_text()),'c1_surface_solver':c1_receipt,'art_pass':False,'limits':['Fresh cap UV, pigment, fur bind, rig, color and animation not rebuilt or accepted.','Source eyes/brows/nose/other objects preserved. Static gray is not a character art pass.']};(O/'preflight.json').write_text(json.dumps(report,indent=2));assert not bad.any(),'New cap crosses below retained source cut'
 newverts={}
 for k,i in boundary_map.items():newverts[i]=loop[k]
 for i in range(len(V)):
  if i not in newverts:
   v=bm.verts.new(world(np.array([V[i,0],V[i,1],Z[i]])));v[can]=0;v[srcattr]=0;newverts[i]=v
 patch=[]
 for face in F:
  f=bm.faces.new(tuple(newverts[int(i)] for i in face));f.smooth=True;patch.append(f)
 bm.normal_update();bm.verts.index_update();bm.faces.index_update();kept=[]
 for v in bm.verts:
  if v in lookup:
   idx=lookup[v];assert np.array_equal(np.array(v.co,dtype=np.float32),old[idx]);v[can]=idx+1;kept.append(idx)
  else:v[can]=0;v[srcattr]=0
 kept=np.array(kept,np.int32);missing=np.ones(len(old),bool);missing[kept]=False;L=local(old);outside=(L[:,2]+.5*np.abs(L[:,0])<=3.29);assert not np.any(missing&outside),'Deleted outside declared local head-top support';assert set(np.flatnonzero(oldids==0)).issubset(set(kept.tolist())),'Lost C35 original new hand'
 report.update({'all_retained_source_positions_bit_exact':True,'protected_below_cut_margin_all_present':True,'C35_new_hand_5359_all_present':True,'deleted_source_vertices':int(missing.sum()),'new_zero_canonical_points':sum(v not in lookup for v in bm.verts),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_vertices':sum(not v.link_faces for v in bm.verts),'signed_volume':bm.calc_volume(signed=True),'minimum_new_patch_normal_z':min(f.normal.z for f in patch)})
 bm.to_mesh(me);me.update();bm.free();bpy.context.view_layer.update();sys.path.insert(0,str(R/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A;small=bmesh.new();small.from_mesh(me);bmesh.ops.delete(small,geom=[v for v in small.verts if v.co.z<2.95],context='VERTS');small.verts.index_update();small.faces.index_update();small.faces.ensure_lookup_table();small.normal_update();report['head_ear_self_pairs']=A._self_intersections(small);small.free();report['geometry_gate']=bool(report['nonmanifold_edges']==0 and report['loose_vertices']==0 and report['head_ear_self_pairs']==0 and report['signed_volume']>0 and report['minimum_new_patch_normal_z']>0)
 np.savez_compressed(O/'canonical-output-map.npz',source=old,source_retained_indices=kept,source_deleted_indices=np.flatnonzero(missing),patch_xy=V,patch_z=Z,patch_triangles=F);scene=bpy.context.scene;scene.cycles.samples=24;scene.cycles.seed=17;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;bpy.context.preferences.filepaths.save_version=0;native=O/'miao-c48-roof-ears-gray.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);report['native_sha256']=sha(native);(O/'receipt.json').write_text(json.dumps(report,indent=2));(O/'executed-build-script.py').write_text(Path(__file__).read_text());print('GATE '+json.dumps(report),flush=True)
 if a.render:
  cam=scene.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();sc=cam.data.ortho_scale
  for name,pos,target,zoom in [('front',None,None,None),('ears',Vector((0,-6,3.30)),Vector((0,0,3.28)),1.45),('three-quarter',Vector((6,-9,3.9)),Vector((.09881,0,1.609)),sc)]:
   if pos is None:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=sc
   else:cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom
   bpy.context.view_layer.update();scene.render.filepath=str(O/('gray-'+name+'.png'));bpy.ops.render.render(write_still=True)
 print('RESULT '+json.dumps({'native_sha256':report['native_sha256'],'geometry_gate':report['geometry_gate'],'art_pass':False}),flush=True)
main()
