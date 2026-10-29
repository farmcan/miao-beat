"""C42 local ear reconstruction. Technical study; actual reference art review required."""
import bpy,bmesh,numpy as np,math,json,hashlib,argparse,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];NAME='Miao / continuous pear and rounded-square face'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--out',default='artifacts/character-ear-c42/preflight');a.add_argument('--render',action='store_true');a.add_argument('--build',action='store_true');args=a.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else[]);out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True)
 if (out/'receipt.json').exists():raise RuntimeError('Frozen diagnostic exists; choose a fresh explicit output directory')
 src=ROOT/'artifacts/character-alignment-c38/head-expression-only/miao-c38-coupled-head-gray.blend';assert sha(src)=='f481e8a0c00eb4ec5baf5d9c43a6bc250f5a28c4475d9d9cba0ea360ca1c8439';bpy.ops.wm.open_mainfile(filepath=str(src));body=bpy.data.objects[NAME];me=body.data;old=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',old);old=old.reshape(-1,3);ang=math.radians(7.5);c=math.cos(ang);s=math.sin(ang)
 def tolocal(p):
  q=np.array(p,float).copy();x=q[...,0]-.04;y=q[...,1]-.03;q[...,0]=x*c+y*s;q[...,1]=.03-x*s+y*c;return q
 def toworld(q):
  p=np.array(q,float).copy();x=p[...,0];y=p[...,1]-.03;p[...,0]=x*c-y*s+.04;p[...,1]=.03+x*s+y*c;return p
 bm=bmesh.new();bm.from_mesh(me);canonical=bm.verts.layers.int.get('Miao_C35_vertex_id') or bm.verts.layers.int.new('Miao_C35_vertex_id');bm.verts.ensure_lookup_table();orig=list(bm.verts);ori_index={v:i for i,v in enumerate(orig)}
 for i,v in enumerate(orig):v[canonical]=i+1
 cuts=[]
 for side in [-1,1]:
  # This plane separates only the anatomical ear above the forehead silhouette.
  n=np.array([.5*side,0,1.]);n/=np.linalg.norm(n);pl=np.array([0,0,3.42]);wn=Vector((n[0]*c,n[0]*s,n[2]));wp=Vector(toworld(pl));before=set(bm.verts);cut=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=wp,plane_no=wn,use_snap_center=False,clear_outer=True,clear_inner=False)
  boundary=[e for e in bm.edges if e.is_boundary];verts=set(v for e in boundary for v in e.verts);degrees={v:0 for v in verts}
  for e in boundary:
   for v in e.verts:degrees[v]+=1
  # Previous ear's open border remains; select the newly created border near this side.
  here=[e for e in boundary if side*tolocal(np.array(e.verts[0].co))[0]>.20 and side*tolocal(np.array(e.verts[1].co))[0]>.20];hv=set(v for e in here for v in e.verts);hd={v:0 for v in hv}
  for e in here:
   for v in e.verts:hd[v]+=1
  assert hv and all(d==2 for d in hd.values()),'Ear cut is not a simple closed contour'
  adj={v:[] for v in hv}
  for e in here:
   u,v=e.verts;adj[u].append(v);adj[v].append(u)
  start=min(hv,key=lambda v:tolocal(np.array(v.co))[1]);loop=[start];prev=None;cur=start
  for _ in range(len(hv)+1):
   nxt=adj[cur][0] if adj[cur][0]!=prev else adj[cur][1]
   if nxt==start:break
   loop.append(nxt);prev,cur=cur,nxt
  assert len(loop)==len(hv)
  P=tolocal(np.array([v.co[:] for v in loop]));np.savez_compressed(out/f'cut-{side}.npz',points=P)
  cuts.append({'side':side,'count':len(P),'local_bounds':[P.min(0).tolist(),P.max(0).tolist()],'mean':P.mean(0).tolist(),'cut_parameter':3.42,'ordered_boundary_one_loop':True})
  if args.build:
   center=P.mean(0);U=np.array([1.,0,-.5*side]);U/=np.linalg.norm(U);du=(P-center)@U;dy=P[:,1]-center[1];previous=loop;newfaces=[];height=.205
   # A connected tapered volume, with shallow front depression. Never a detached
   # triangular insert or an independently composited ear image.
   for j in range(1,25):
    t=j/25;wu=(1-t)**.8;wy=(1-t)**2.15;cc=center+n*(height*t);cc[1]+=-.115*(t*t*(3-2*t));Q=cc+du[:,None]*wu*U+dy[:,None]*wy*np.array([0,1,0]);front=np.clip(-dy/.20,0,1)**3;Q[:,1]+=.018*(math.sin(math.pi*t)**2)*front
    ring=[]
    for q in Q:
     v=bm.verts.new(toworld(q));v[canonical]=0;ring.append(v)
    for k in range(len(loop)):
     f=bm.faces.new((previous[k],previous[(k+1)%len(loop)],ring[(k+1)%len(loop)],ring[k]));f.smooth=True;newfaces.append(f)
    previous=ring
   tip=center+n*height;tip[1]-=.115;apex=bm.verts.new(toworld(tip));apex[canonical]=0
   for k in range(len(loop)):
    f=bm.faces.new((previous[k],previous[(k+1)%len(loop)],apex));f.smooth=True;newfaces.append(f)
   bmesh.ops.recalc_face_normals(bm,faces=newfaces)
   cuts[-1]['new_faces']=len(newfaces);cuts[-1]['apex_local']=tip.tolist()
  # Otherwise this is an open-cut preflight only.
 for v in bm.verts:
  if v in ori_index:assert np.array_equal(np.array(v.co,dtype=np.float32),old[ori_index[v]])
  else:v[canonical]=0
 retained=set(ori_index[v] for v in bm.verts if v in ori_index);deleted=np.array([i for i in range(len(old)) if i not in retained]);head=tolocal(old);outside=(head[:,2]+.5*np.abs(head[:,0])<=3.41);bad=sorted(set(np.flatnonzero(outside)).intersection(deleted.tolist()));print('BAD '+json.dumps([{'id':int(i),'local':head[i].tolist(),'world':old[i].tolist()} for i in bad[:12]]),flush=True);assert not bad;new=sum(v not in ori_index for v in bm.verts)
 report={'stage':'C42 two exact local ear cuts; open preflight, not completed ears','source_sha':sha(src),'cuts':cuts,'deleted_old_vertices':len(deleted),'new_boundary_vertices':new,'all_surviving_source_vertices_exact':True,'outside_cut_deleted':0};(out/'preflight.json').write_text(json.dumps(report,indent=2));
 if args.build:
  bm.normal_update();bm.verts.index_update();bm.faces.index_update();report['nonmanifold_edges']=sum(not e.is_manifold for e in bm.edges);report['signed_volume']=bm.calc_volume(signed=True);bm.to_mesh(me);me.update();bm.free();bpy.context.view_layer.update();sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A;small=bmesh.new();small.from_mesh(me);bmesh.ops.delete(small,geom=[v for v in small.verts if v.co.z<3.04],context='VERTS');small.verts.index_update();small.faces.index_update();small.faces.ensure_lookup_table();small.normal_update();report['head_ear_self_pairs']=A._self_intersections(small);small.free();report['stage']='C42 welded short ear loft diagnostic; art pending';report['new_material_UV_and_groom_binding']='not rebuilt; gray diagnostic only';scene=bpy.context.scene;scene.cycles.samples=24;scene.cycles.seed=17;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;bpy.context.preferences.filepaths.save_version=0;native=out/'miao-c42-local-ears-gray.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);report['native_sha256']=sha(native)
  if args.render:
   cam=scene.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();sc=cam.data.ortho_scale
   for name,pos,target,zoom in [('front',None,None,None),('face',Vector((0,-6,3.05)),Vector((0,0,3.03)),1.7),('three-quarter',Vector((6,-9,3.9)),Vector((.09881,0,1.609)),sc)]:
    if pos is None:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=sc
    else:cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom
    bpy.context.view_layer.update();scene.render.filepath=str(out/('gray-'+name+'.png'));bpy.ops.render.render(write_still=True)
 else:bm.free()
 (out/'receipt.json').write_text(json.dumps(report,indent=2));print('RESULT '+json.dumps(report),flush=True)
main()
