"""C12: reference-driven head volume, integrated muzzle and curved inner-ear study.
Only head z>=2.5 changes. Continuous body topology/pose/eye XZ anchors are preserved;
this is a primary-form gray candidate, not GUI surface polish or animation acceptance.
"""
import argparse,sys,json,math,hashlib,time
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'))
import bx_sculpt as S
p=argparse.ArgumentParser();p.add_argument('--input',default='artifacts/character-fidelity-c8-r2-color/miao-c8-reference-hold.blend');p.add_argument('--out',default='artifacts/character-head-c12');p.add_argument('--size',type=int,default=1024);p.add_argument('--samples',type=int,default=32);p.add_argument('--revision',type=int,default=1);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def co(o):
 v=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',v);return v.reshape(-1,3)
def world(o,v):m=np.array(o.matrix_world);return v@m[:3,:3].T+m[:3,3]
def local(o,v):m=np.array(o.matrix_world);return (v-m[:3,3])@np.linalg.inv(m[:3,:3]).T
# A common positive-Y scale field keeps the sclera/iris/cornea/lid ordering.
# Explicit X/Z preservation keeps the measured front face/ear anchors.
def field(P):
 P=np.asarray(P,float);Q=P.copy();x,y,z=P.T
 w=smooth((z-2.50)/.18)*(1-smooth((z-3.055)/.10))
 rx=np.interp(z,[2.5,2.60,2.86,3.10,3.24,3.30,3.33],[.66,.60,.575,.55,.51,.43,.001])
 rx*=1+.045*np.exp(-((z-2.70)/.20)**2)-.035*np.exp(-((z-3.22)/.12)**2)
 ratio=np.minimum(np.abs(x)/np.maximum(rx,.1),.985)
 old=(1-ratio**3.2)**(1/3.2);new=(1-ratio**2.35)**(1/2.35);factor=np.clip(new/old,.62,1)
 ry=np.interp(z,[2.50,2.60,2.86,3.10,3.24,3.30,3.33],[.43,.425,.42,.405,.38,.31,.01])
 front=smooth((.02-y)/.30)
 Q[:,1]+=ry*(old-new)*w*front
 # Integrated cheek/mouth mound, with no extra sphere/plate objects.
 front=smooth((.02-y)/.30)
 mouth=(.064*np.exp(-((x+.055)/.21)**2-((z-2.785)/.145)**2)+.064*np.exp(-((x-.210)/.21)**2-((z-2.785)/.145)**2)+.035*np.exp(-((x-.078)/.25)**2-((z-2.64)/.115)**2))
 mouth*=w*front*(1-smooth((z-2.80)/.065))
 Q[:,1]-=mouth
 # Curved inside bowls, restricted to the original inner triangle and cavity depth.
 for side in [-1,1]:
  ex=side*.43;A=np.array([ex-.105,3.18]);B=np.array([ex+.105,3.18]);C=np.array([ex+side*.065,3.43]);T=np.stack([B-A,C-A],axis=1);uv=(np.stack([x,z],axis=1)-A)@np.linalg.inv(T).T;u,v=uv.T;b0=1-u-v;inside=(u>0)&(v>0)&(b0>0)
  q=np.zeros(len(P));q[inside]=27*u[inside]*v[inside]*b0[inside]
  cavity=smooth((y+.32)/.12)*(1-smooth((y-.03)/.12))
  Q[:,1]+=.025*q**.7*cavity
 # No numerical tails may change the torso or either paw.
 Q[z<2.5]=P[z<2.5]
 return Q

def main():
 start=time.time();src=(ROOT/a.input).resolve();out=(ROOT/a.out).resolve();out.mkdir(parents=True,exist_ok=True);before=sha(src)
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];cam=s.camera;frontmat=cam.matrix_world.copy();oldscale=cam.data.ortho_scale
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(dg);evaluated=ev.to_mesh();v=np.empty(len(evaluated.vertices)*3,np.float32);evaluated.vertices.foreach_get('co',v);v=v.reshape(-1,3);ev.to_mesh_clear();assert len(v)==len(body.data.vertices),'Need matching evaluated topology to store head-only key'
 old=world(body,v);new=field(old);tmpme=bpy.data.meshes.new_from_object(body.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);work=bpy.data.objects.new('C12 / primary head work',tmpme);s.collection.objects.link(work);work.matrix_world=body.matrix_world.copy();tmpme.vertices.foreach_set('co',local(work,new).astype(np.float32).ravel());tmpme.update()
 # Local volume-preserving relaxation of the ear bowl/rim only.
 sc=S.Sculptor(work,symmetry_x=False);sc.mask_by(lambda c:c[:,2]<3.15)
 for side in [-1,1]:sc.smooth(sc.to_local((side*.43,-.16,3.29)),.19,strength=.16,iterations=3,preserve_volume=True)
 new=world(work,sc.co);new[old[:,2]<2.5]=old[old[:,2]<2.5]
 delta=local(body,new)-v
 if body.data.shape_keys is None:body.shape_key_add(name='Basis')
 basis=np.empty(len(body.data.vertices)*3,np.float32);body.data.shape_keys.key_blocks['Basis'].data.foreach_get('co',basis);basis=basis.reshape(-1,3);key=S.write_shape_key(body,'C12 / integrated head shell',basis+delta)
 bpy.data.objects.remove(work,do_unlink=True);bpy.data.meshes.remove(tmpme)
 # Coupled eye envelopes and brows: one map, no eyeball hiding/scale cheat.
 feature_records=[]
 for o in list(s.objects):
  if o==body:continue
  if o.type=='MESH' and o.name.startswith(('C6 /','C7 / clear')):
   oldf=world(o,co(o));nf=field(oldf);o.data.vertices.foreach_set('co',local(o,nf).astype(np.float32).ravel());o.data.update();feature_records.append({'name':o.name,'XZ_unchanged':bool(np.array_equal(oldf[:,[0,2]],nf[:,[0,2]])),'maximum_displacement':float(np.linalg.norm(nf-oldf,axis=1).max())})
  elif o.type=='CURVE' and o.name.startswith('Face / thick curved brow'):
   for sp in o.data.splines:
    for bp in sp.bezier_points:
     for attr in ['co','handle_left','handle_right']:
      w=o.matrix_world@getattr(bp,attr);setattr(bp,attr,o.matrix_world.inverted()@Vector(field(np.array([w]))[0]))
 # Groom is intentionally hidden in this gray gate, even with unchanged body topology.
 hair=bpy.data.objects.get('Miao / native short plush')
 if hair:hair.hide_render=True
 bpy.context.view_layer.update();tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());iv=body.matrix_world.inverted();direction=(iv.to_3x3()@Vector((0,1,0))).normalized();hits=[]
 def skin(x,z):
  hit,n,face,dist=tree.ray_cast(iv@Vector((float(x),-3,float(z))),direction,8)
  if hit is None:raise RuntimeError('Strict face ray missed: '+str((x,z)))
  q=body.matrix_world@hit;assert abs(q.x-x)<2e-5 and abs(q.z-z)<2e-5;hits.append([float(x),float(z),float(q.y)]);return float(q.y)
 # A truly rounded triangular nose pillow, attached all around to the new muzzle.
 oldnose=bpy.data.objects['Face / rounded triangular nose'];nosemat=oldnose.data.materials[0];oldname=oldnose.name;bpy.data.objects.remove(oldnose,do_unlink=True)
 cx=.078;cz=2.864;N=96;R=22
 # Smooth rounded-triangle contour. 8-point periodic cubic is 2D design only.
 pts=np.array([[cx-.055,cz+.031],[cx,cz+.038],[cx+.055,cz+.031],[cx+.067,cz+.010],[cx+.032,cz-.028],[cx,cz-.040],[cx-.032,cz-.028],[cx-.067,cz+.010]])
 contour=[]
 for i in range(len(pts)):
  p0,p1,p2,p3=[pts[k%len(pts)] for k in [i-1,i,i+1,i+2]]
  for j in range(N//len(pts)):
   t=j/(N//len(pts));contour.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 contour=np.array(contour)
 area=float(np.sum(contour[:,0]*np.roll(contour[:,1],-1)-np.roll(contour[:,0],-1)*contour[:,1]))
 if area<0:contour=contour[::-1].copy()
 vs=[];fs=[]
 for back in [False,True]:
  vs.append((cx,skin(cx,cz)+.012 if back else skin(cx,cz)-.055,cz))
  for j in range(1,R+1):
   r=j/R
   for xy in contour:
    x,z=np.array([cx,cz])+(xy-np.array([cx,cz]))*r;sy=skin(x,z);y=sy+.012 if back else sy+.002-.057*max(0,1-r*r)**.60;vs.append((x,y,z))
 layer=1+N*R
 for back in [False,True]:
  off=layer if back else 0
  for k in range(N):f=(off,off+1+k,off+1+(k+1)%N);fs.append(f[::-1] if back else f)
  for j in range(R-1):
   for k in range(N):u=off+1+j*N+k;w=off+1+j*N+(k+1)%N;f=(u,u+N,w+N,w);fs.append(f[::-1] if back else f)
 for k in range(N):u=1+(R-1)*N+k;w=1+(R-1)*N+(k+1)%N;fs.append((u,u+layer,w+layer,w))
 me=bpy.data.meshes.new('C12 rounded nose pillow');me.from_pydata(vs,[],fs);me.update();nose=bpy.data.objects.new(oldname,me);s.collection.objects.link(nose);me.materials.append(nosemat)
 for f in me.polygons:f.use_smooth=True
 bm=bmesh.new();bm.from_mesh(me);nose_volume=bm.calc_volume(signed=True);nose_boundary=sum(e.is_boundary for e in bm.edges);bm.free();assert nose_volume>0 and nose_boundary==0
 # Embed brows on the actual new skin; source brows floated in side view.
 for o in list(s.objects):
  if o.type=='CURVE' and o.name.startswith('Face / thick curved brow'):
   oi=o.matrix_world.inverted()
   for sp in o.data.splines:
    for bp in sp.bezier_points:
     w=o.matrix_world@bp.co;target=Vector((w.x,skin(w.x,w.z)-.003,w.z));shift=oi@target-bp.co;bp.co+=shift;bp.handle_left+=shift;bp.handle_right+=shift
 # Project actual mouth controls onto actual face, not nearest-point fallback.
 mouth=[]
 for o in list(s.objects):
  if o.type=='CURVE' and o.name.startswith('Face / smile'):
   o.data.bevel_depth=min(o.data.bevel_depth,.0055);oi=o.matrix_world.inverted()
   for sp in o.data.splines:
    for bp in sp.bezier_points:
     w=o.matrix_world@bp.co;target=Vector((w.x,skin(w.x,w.z)-.002,w.z));shift=oi@target-bp.co;bp.co+=shift;bp.handle_left+=shift;bp.handle_right+=shift;mouth.append(list(target))
  elif o.type=='CURVE' and o.name.startswith('Miao / fine whisker'):
   for sp in o.data.splines:
    bp=sp.bezier_points[0];w=o.matrix_world@bp.co;target=Vector((w.x,skin(w.x,w.z)-.001,w.z));shift=o.matrix_world.inverted()@target-bp.co;bp.co+=shift
 bpy.context.view_layer.update();assert np.array_equal(new[old[:,2]<2.5],old[old[:,2]<2.5]);assert cam.matrix_world==frontmat and cam.data.ortho_scale==oldscale
 s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.samples=a.samples;s.cycles.seed=17;s.cycles.use_animated_seed=False;bpy.context.preferences.filepaths.save_version=0;s.render.filepath='//renders/head-shell.png';bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-c12-head-shell.blend'),compress=True)
 mats={}
 for name,val in [('body',.4),('white',.72),('dark',.045),('wood',.3)]:
  m=bpy.data.materials.new('C12 gray '+name);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(val,val,val,1);bs.inputs['Roughness'].default_value=.65;mats[name]=m
 for o in list(s.objects):
  if o.type not in {'MESH','CURVE','CURVES'} or o.hide_render or o.name.startswith(('Studio /','Authoring /','D0 /','C7 / clear')):continue
  role='white' if o.name.startswith('C6 / sclera') else 'dark' if o.name.startswith(('C6 / iris','Face /')) else 'wood' if o.name.startswith('Guitar /') else 'body';o.data.materials.clear();o.data.materials.append(mats[role])
 renders=[]
 def render(name):
  s.render.filepath=str(out/(name+'.png'));t=time.time();bpy.ops.render.render(write_still=True);renders.append({'name':name,'seconds':time.time()-t,'sha256':sha(s.render.filepath)})
 render('gray-front');cam.location=(6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler();render('gray-three-quarter')
 # Actual long-lens head-only diagnosis in the same complete 3D scene, not an image edit.
 cam.data.type='PERSP';cam.data.lens=90;cam.location=(3.25,-4.4,3.08);cam.rotation_euler=(Vector((.02,0,2.96))-cam.location).to_track_quat('-Z','Y').to_euler();render('gray-head-three-quarter')
 cam.location=(5.9,-.5,3.02);cam.rotation_euler=(Vector((0,0,2.98))-cam.location).to_track_quat('-Z','Y').to_euler();render('gray-head-side')
 result={'stage':'C12-primary-head-gray-unreviewed','revision':a.revision,'input':str(src.relative_to(ROOT)),'input_sha256':before,'input_unchanged':sha(src)==before,'source_sha256':sha(__file__),'blender':bpy.app.version_string,'body_vertices_unchanged':len(v),'body_topology_unchanged':True,'below_z2_5_exactly_unchanged':True,'maximum_body_delta':float(np.linalg.norm(new-old,axis=1).max()),'feature_XZ_and_eye_envelopes':feature_records,'strict_skin_ray_hits':len(hits),'strict_ray_misses':0,'nose':{'vertices':len(vs),'closed_signed_volume':nose_volume,'boundary_edges':nose_boundary,'method':'closed smooth pillow fitted to actual new muzzle, not a thin six-vertex wedge'},'mouth_surface_controls':mouth,'renders':renders,'limits':['Gray primary-form candidate; three independent non-builder reviews required.','No live GUI surface polish, colors or animation acceptance.','Source body topology/UVs retained, but native groom hidden and large deformation attachment/closed eye/iris ordering still require independent validation.','Paws/guitar/body below head deliberately unchanged; their known P0 remain.','Side/back anatomy is reconstruction from one reference, not source-proven.']};(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT '+json.dumps(result))
main()
