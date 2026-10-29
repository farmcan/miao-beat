"""C42 depth chart candidate: a monotone ear-front return, not a released asset."""
import bpy,bmesh,numpy as np,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
O=R/'artifacts/character-ear-c42/depth-r1';O.mkdir(parents=True,exist_ok=True)
if (O/'receipt.json').exists():raise RuntimeError('Frozen diagnostic exists; source is preserved')
def sm(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=math.radians(7.5);c,s=math.cos(a),math.sin(a)
def local(P):
 q=np.array(P,float).copy();x=q[:,0]-.04;y=q[:,1]-.03;q[:,0]=x*c+y*s;q[:,1]=.03-x*s+y*c;return q
def world(P):
 q=np.array(P,float).copy();x=q[:,0].copy();y=q[:,1]-.03;q[:,0]=x*c-y*s+.04;q[:,1]=.03+x*s+y*c;return q
def flow(P):
 q=local(P);x,y,z=q.T;w=sm(.27,.35,np.abs(x))*sm(3.12,3.205,z);g=1-sm(-.12,.04,y);target=1.05*(z-3.40)-.065;d=(target-y)*.65*w*g;q[:,1]+=d;result=world(q);result[(w*g)==0]=np.asarray(P)[(w*g)==0];return result
src=R/'artifacts/character-alignment-c38/head-expression-only/miao-c38-coupled-head-gray.blend';bpy.ops.wm.open_mainfile(filepath=str(src));b=bpy.data.objects['Miao / continuous pear and rounded-square face'];m=b.data;P=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',P);P=P.reshape(-1,3);Q=flow(P).astype(np.float32);changed=np.any(P!=Q,1);Q[~changed]=P[~changed];m.calc_loop_triangles();T=np.array([t.vertices[:] for t in m.loop_triangles]);T=T[changed[T].any(1)];v=P[T];v1=Q[T];n0=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);n1=np.cross(v1[:,1]-v1[:,0],v1[:,2]-v1[:,0]);C=v.mean(1).astype(float);J=np.zeros((len(T),3,3));eps=1e-5
for j in range(3):
 h=np.zeros(3);h[j]=eps;J[:,:,j]=(flow(C+h)-flow(C-h))/(2*eps)
det=np.linalg.det(J);expected=np.einsum('nij,nj->ni',np.linalg.inv(J).transpose(0,2,1),n0)*det[:,None];dots=np.einsum('ij,ij->i',expected,n1)/np.maximum(np.linalg.norm(expected,axis=1)*np.linalg.norm(n1,axis=1),1e-24);area=np.linalg.norm(n1,axis=1)/np.maximum(np.linalg.norm(n0,axis=1),1e-24)
r={'source_sha256':sha(src),'method':'Monotone Y-only head-local shallow front plane, preserving full source topology','changed_vertices':int(changed.sum()),'maximum_displacement_u':float(np.linalg.norm(P-Q,axis=1).max()),'minimum_Jacobian_det':float(det.min()),'minimum_actual_transported_normal_dot':float(dots.min()),'reversed_actual_triangles':int((dots<=0).sum()),'minimum_area_ratio':float(area.min()),'strict_geometry_gate':bool(det.min()>.2 and dots.min()>.7),'counterexamples':[{'dot':float(dots[i]),'old':P[T[i]].tolist(),'new':Q[T[i]].tolist()} for i in np.argsort(dots)[:8]],'art_pass':False}
(O/'pre-gate.json').write_text(json.dumps(r,indent=2));m.vertices.foreach_set('co',Q.ravel());m.update();bpy.context.view_layer.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<3.04],context='VERTS');bm.verts.index_update();bm.faces.index_update();bm.faces.ensure_lookup_table();bm.normal_update();r['head_self_pairs']=A._self_intersections(bm);bm.free();r['strict_geometry_gate']=r['strict_geometry_gate'] and r['head_self_pairs']==0
np.savez_compressed(O/'deformation.npz',index=np.flatnonzero(changed),before=P[changed],after=Q[changed]);scene=bpy.context.scene;scene.cycles.samples=24;scene.cycles.seed=17;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;bpy.context.preferences.filepaths.save_version=0;native=O/'miao-c42-depth-diagnostic.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);r['native_sha256']=sha(native);(O/'receipt.json').write_text(json.dumps(r,indent=2));cam=scene.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();sc=cam.data.ortho_scale
for name,pos,target,zoom in [('front',None,None,None),('face',Vector((0,-6,3.05)),Vector((0,0,3.03)),1.7),('three-quarter',Vector((6,-9,3.9)),Vector((.09881,0,1.609)),sc)]:
 if pos is None:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=sc
 else:cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom
 bpy.context.view_layer.update();scene.render.filepath=str(O/('gray-'+name+'.png'));bpy.ops.render.render(write_still=True)
print('RESULT '+json.dumps(r),flush=True)
