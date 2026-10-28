"""C11: rounded thicker palm, tapered integrated wrist and falling short toes, welded into the complete C8 cat.
Geometry-only study. Native old groom is hidden because its UV binding is invalidated.
Owned reference-driven cage, with MIT bx_retopo bridge helper (pinned vendor).
"""
import bpy,bmesh,numpy as np,math,sys,json,hashlib,time,argparse
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/character-paw-c11');p.add_argument('--size',type=int,default=1024);p.add_argument('--samples',type=int,default=32);p.add_argument('--build-only',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_retopo as R;import bx_audit as A
out=root/a.out;out.mkdir(parents=True,exist_ok=True);src=root/'artifacts/character-fidelity-c8-r2-color/miao-c8-reference-hold.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
origin=Vector((-.1950536246756659,-.85,1.5567366254980208));gu=Vector((1.0169595357706245,0,.40048756408789304));gv=Vector((-.40048756408789304,0,1.0169595357706245));U=gu.normalized();V=gv.normalized()
def g(u,v,y):return origin+gu*u+gv*v+Vector((0,y-origin.y,0))
def mesh(name,vs,fs):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.validate(verbose=True);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);return o
def topo(o):
 bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();seen=set();sizes=[]
 for v in bm.verts:
  if v.index in seen:continue
  stack=[v];seen.add(v.index);n=0
  while stack:
   q=stack.pop();n+=1
   for e in q.link_edges:
    w=e.other_vert(q)
    if w.index not in seen:seen.add(w.index);stack.append(w)
  sizes.append(n)
 result={'vertices':len(bm.verts),'faces':len(bm.faces),'components':len(sizes),'component_vertices':sorted(sizes,reverse=True)[:8],'boundary_edges':sum(e.is_boundary for e in bm.edges),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'quads':sum(len(f.verts)==4 for f in bm.faces),'triangles':sum(len(f.verts)==3 for f in bm.faces)};bm.free();return result

def make_hand():
 # Map: palm has explicit V rings, front/back U columns; three cap cells become
 # three short curved digits. The crease is the web between actual toe volumes.
 # These are authored from the reference and guitar plane, not fitted to old hand.
 profile=[(-.425,1.19,.090,-1.035,.095,.035),(-.39,1.205,.130,-1.025,.145,.045),(-.325,1.245,.180,-1.025,.225,.050),(-.245,1.29,.200,-1.033,.250,.045),(-.165,1.335,.190,-1.050,.220,.030),(-.065,1.355,.164,-1.070,.150,.020)]
 vs=[];fs=[];rings=[];bridges=[]
 # ring order: front across U, then back returning U. Four U columns make three
 # knuckle cells with shared roots, so no detached/sphere fingers exist.
 for j,(v,cu,w,cy,df,db) in enumerate(profile):
  ur=np.linspace(-w,w,4);front=[.32,1,1,.32];back=[.30,1,1,.30];ids=[]
  for k in range(4):ids.append(len(vs));vs.append(g(cu+ur[k],v,cy-df*front[k]))
  for k in range(3,-1,-1):ids.append(len(vs));vs.append(g(cu+ur[k],v,cy+db*back[k]))
  rings.append(ids)
  if j:
   for k in range(8):u=rings[j-1][k];w0=rings[j-1][(k+1)%8];vv=rings[j][(k+1)%8];q=rings[j][k];fs.append((u,w0,vv,q))
 # A compact padded palm bottom; wrist enters through its rear-facing patch.
 fs.append(tuple(rings[0][::-1]))
 # Remove one central rear cell over two strips = 6-sided compact wrist socket.
 remove=set()
 for strip in [2,3]:
  # Only central rear k5 is removed; side panels preserve continuous palm mass.
  for k in [5]:remove.add((strip-1)*8+k)
 fs=[f for i,f in enumerate(fs) if i not in remove]
 # Boundary explicitly follows that small rear patch, no nearest fallback.
 # perimeter: lower front-of-back row 1 from right to left, left side to row3,
 # upper row3 left to right, right side back to row1.
 socket=[rings[1][5],rings[1][6],rings[2][6],rings[3][6],rings[3][5],rings[2][5]]
 # Three real toe roots share knuckle-grid edges, then leave the palm as closed
 # curved quad strips. At least centre/each-side rings around each bend.
 toe_records=[]
 top=rings[-1]
 for digit in range(3):
  root_loop=[top[digit],top[digit+1],top[6-digit],top[7-digit]]
  cu=(profile[-1][1]-profile[-1][2])+profile[-1][2]*(2*digit+1)/3
  peak=[.000,.012,-.006][digit]
  centers=[(-.040,-1.160,.062,.059),(-.005+peak,-1.175,.064,.055),(.025+peak,-1.155,.065,.050),(.043+peak,-1.125,.063,.044),(.020+peak,-1.095,.059,.039),(-.010+peak,-1.065,.048,.030),(-.032+peak,-1.066,.030,.021)]
  # The path is expressed V/Y; U widths give short broad cat toes.
  prev=root_loop;path=[]
  for k,(v,cy,ru,rd) in enumerate(centers):
   # tangent in V/Y, U is one ring axis. Other ring axis follows the path,
   # making the volume bend instead of sliding a cap on a flat long palm.
   before=Vector((centers[max(0,k-1)][0],centers[max(0,k-1)][1]));after=Vector((centers[min(len(centers)-1,k+1)][0],centers[min(len(centers)-1,k+1)][1]));dv,dy=(after-before).normalized();N=-V*float(dy)+Vector((0,1,0))*float(dv)
   # root loop winds front-left,front-right,back-right,back-left.
   c=g(cu+(.006*math.sin(k/6*math.pi)*(digit-1)),v,cy);ids=[]
   for su,sd in [(-1,-1),(1,-1),(1,1),(-1,1)]:ids.append(len(vs));vs.append(c+U*(su*ru)+N*(sd*rd))
   bridges.append((list(prev),list(ids)))
   prev=ids;path.append(list(c))
  fs.append(tuple(prev));toe_records.append({'digit':digit,'root_indices':root_loop,'centreline_world':path,'joint_support_rings':7,'ring_bridge':'pinned bx_retopo.bridge align=False','not_individual_rig':True})
 # Wrist collar, continuous with palm rear. Width/height return smoothly into
 # source forearm behind the cut; collar and all three toes are one cage.
 socket_pts=[Vector(vs[i]) for i in socket];cen=sum(socket_pts,Vector())/len(socket_pts)
 n=len(socket);last=socket
 # Match socket winding to a smooth elliptical wrist cross-section in X/Z.
 # Use its own polar phase so the collar does not twist into a bow-tie.
 angles=[math.atan2(p.z-cen.z,p.x-cen.x) for p in socket_pts]
 for t in [.25,.50,.75,1.0]:
  c=cen.lerp(Vector((1.205,-.55,1.805)),t);ids=[]
  for i,(point,an) in enumerate(zip(socket_pts,angles)):
   target=Vector((c.x+.150*math.cos(an),c.y,c.z+.160*math.sin(an)));co=point.lerp(target,t);co.y=(1-t)*point.y+t*c.y;ids.append(len(vs));vs.append(co)
  bridges.append((list(last),list(ids)))
  last=ids
 fs.append(tuple(last[::-1]))
 hand=mesh('C11 / reference palm and curled short toes',vs,fs)
 for aa,bb in bridges:R.bridge(hand,aa,bb,align=False)
 bm=bmesh.new();bm.from_mesh(hand.data);loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=bm.faces[:]);
 bm.to_mesh(hand.data);bm.free();hand.data.update()
 cage=topo(hand);assert cage['components']==1 and cage['non_manifold_edges']==0,cage
 # Apply only to the little authored cage, never globally subdivide the 609k cat.
 bpy.context.view_layer.objects.active=hand;hand.select_set(True);sub=hand.modifiers.new('C11 / planned curved surface','SUBSURF');sub.levels=2;sub.render_levels=2;bpy.ops.object.modifier_apply(modifier=sub.name);hand.select_set(False)
 # A continuous low-frequency dome in the same skin, never an added ball/plate.
 # Apply only to front-facing palm rows below the knuckles, after cage subdivision.
 co=np.empty(len(hand.data.vertices)*3,np.float32);hand.data.vertices.foreach_get('co',co);co=co.reshape(-1,3);D=co-np.array(origin);uu=D@np.array(gu)/gu.length_squared;vv=D@np.array(gv)/gv.length_squared;cu=1.29+(vv+.245)*.48;q=((uu-cu)/.18)**2+((vv+.245)/.19)**2;weight=np.maximum(0,1-q)**2;front=np.clip((-1.10-co[:,1])/.10,0,1);co[:,1]-=.032*weight*front;hand.data.vertices.foreach_set('co',co.ravel());hand.data.update()
 for f in hand.data.polygons:f.use_smooth=True
 hand_audit=A.audit(hand);(out/'hand-audit.json').write_text(json.dumps(hand_audit,indent=2)+'\n');
 return hand,{'hand_audit':hand_audit,'profile':profile,'toe_cages':toe_records,'cage':cage,'subdivided':topo(hand),'socket_indices_before_subdiv':socket,'method':'shared knuckle grid -> explicit curved quad digit rings, rear wrist socket/collar; no toe spheres, no old-hand shrinkwrap'}

def cutter_box():
 u0,u1=.88,1.90;v0,v1=-.58,.42;y0,y1=-1.8,-.70
 vs=[g(u,v,y) for y in [y0,y1] for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]]
 o=mesh('C11 / old-hand removal volume',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=bm.faces[:]);
 bm.to_mesh(o.data);bm.free();return o

def apply_bool(body,other,operation):
 bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;m=body.modifiers.new('C11 / local '+operation,'BOOLEAN');m.operation=operation;m.solver='MANIFOLD';m.object=other;bpy.ops.object.modifier_apply(modifier=m.name);body.select_set(False)


def main():
 started=time.time();inp_sha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];hair=bpy.data.objects['Miao / native short plush'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();original_counts={'vertices':len(body.data.vertices),'faces':len(body.data.polygons),'shape_keys':[k.name for k in body.data.shape_keys.key_blocks]}
 # Freeze accepted C8 hold as construction rest; parent file and geometry untouched.
 baked=bpy.data.meshes.new_from_object(body.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);body.data=baked
 for mod in list(body.modifiers):body.modifiers.remove(mod)
 # Taper the existing connected wrist before the old distal hand is removed.
 # This replaces the broad sliced backing tray with a gradual forearm-to-wrist.
 co=np.empty(len(body.data.vertices)*3,np.float32);body.data.vertices.foreach_get('co',co);co=co.reshape(-1,3);oldco=co.copy();dx=co[:,0]-1.205;dz=co[:,2]-1.805;r=np.sqrt(dx*dx+dz*dz)
 def sm(t):t=np.clip(t,0,1);return t*t*(3-2*t)
 wy=sm((-.25-co[:,1])/.23);wr=1-sm((r-.285)/.115);w=wy*wr;factor=1-.38*w;co[:,0]=1.205+dx*factor;co[:,2]=1.805+dz*factor;body.data.vertices.foreach_set('co',co.ravel());body.data.update();taper_record={'changed_vertices':int((w>1e-6).sum()),'max_displacement':float(np.linalg.norm(co-oldco,axis=1).max()),'maximum_radial_shrink':.38,'Y_falloff':[-.25,-.48],'axis_xz':[1.205,1.805]}
 hair.hide_render=True;hair.hide_set(True);hair['C11 binding status']='INVALIDATED by local topology replacement; must rebuild/rebind after gray acceptance'
 hand,design=make_hand();before=topo(body);cut=cutter_box();apply_bool(body,cut,'DIFFERENCE');bpy.data.objects.remove(cut,do_unlink=True);after_cut=topo(body)
 apply_bool(body,hand,'UNION');bpy.data.objects.remove(hand,do_unlink=True)
 bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(body.data);bm.free();body.data.update();final=topo(body)
 assert final['components']==1 and final['non_manifold_edges']==0,final
 for f in body.data.polygons:f.use_smooth=True
 def neutral(name,value):
  m=bpy.data.materials.new('C11 gray '+name);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(value,value,value,1);bs.inputs['Roughness'].default_value=.65;return m
 mats={k:neutral(k,v) for k,v in [('body',.4),('white',.72),('dark',.045),('wood',.3)]}
 for o in list(s.objects):
  if o.type not in {'MESH','CURVES','CURVE'} or o.hide_render or o.name.startswith(('Studio /','Authoring /','D0 /','C7 / clear')):continue
  key='white' if o.name.startswith('C6 / sclera') else 'dark' if o.name.startswith(('C6 / iris','Face /')) else 'wood' if o.name.startswith('Guitar /') else 'body';o.data.materials.clear();o.data.materials.append(mats[key])
 s.cycles.samples=a.samples;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
 source_data={'stage':'C11-gray-candidate-unreviewed','input_sha256':inp_sha,'script_sha256':sha(__file__),'helper_repository':'https://github.com/scenario-labs/skills','helper_commit':'d44410f058991f677ccf733a8e86ce95110857eb','helper_sha256':sha(R.__file__),'design':design,'original_counts':original_counts,'wrist_taper':taper_record,'frozen_before':before,'after_old_hand_cut':after_cut,'final_body':final,'groom_hidden_because_binding_invalid':True,'old_shape_keys_not_animation_rest':True,'contact_status':'Not yet audited: run paw-volume-contact-audit.py against the saved scene; no legacy extrapolation table','limitations':['This is one fretting-paw structural gray candidate, not overall character acceptance.','Old picking-paw, head/muzzle/ear P0/P1 remain from C8.','Old groom/root/UV/shape-key evidence does not transfer after this local topology change.','No colors, animation, rig, Godot asset, browser, audio or export acceptance.','Boolean junction near wrist still needs deforming retopology/weights; toe cage is planned, whole cat is not a finished low-poly rig.','Three nonbuilder reviews pending; topology metrics do not certify natural grip.']}
 s.render.filepath='//renders/c10-gray.png';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-c11-paw-volume.blend'),compress=True)
 if not a.build_only:
  cam=s.camera;frontloc=cam.location.copy();frontrot=cam.rotation_euler.copy();frontscale=cam.data.ortho_scale
  for view in ['front','three-quarter','grip-inside']:
   if view=='three-quarter':cam.location=(6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=frontscale
   elif view=='grip-inside':cam.location=(4,-6,3.0);cam.rotation_euler=(Vector((1.17,-.95,1.96))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25;s.render.resolution_x=s.render.resolution_y=768
   s.render.filepath=str(out/('gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
  cam.location=frontloc;cam.rotation_euler=frontrot;cam.data.ortho_scale=frontscale
 assert sha(src)==inp_sha;source_data['input_unchanged']=True;source_data['seconds']=time.time()-started;(out/'receipt.json').write_text(json.dumps(source_data,indent=2)+'\n');print('RESULT '+json.dumps(source_data))
main()
