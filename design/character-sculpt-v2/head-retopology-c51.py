"""C51 lowest-cost falsification: actual source-head-only uniform remesh.
Authoring isolation is not a production mesh. Body/paws remain source exact;
new head has no inherited source IDs and must be welded/bound later if accepted.
"""
import bpy,bmesh,numpy as np,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];O=R/'artifacts/character-head-retopology-c51';O.mkdir(parents=True,exist_ok=True)
if (O/'receipt.json').exists():raise RuntimeError('Frozen output exists')
NAME='Miao / continuous pear and rounded-square face';src=R/'artifacts/character-alignment-c38/head-expression-only/miao-c38-coupled-head-gray.blend'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def co(m):
 p=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',p);return p.reshape(-1,3)
def sm(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
ANG=math.radians(7.5);C,S=math.cos(ANG),math.sin(ANG)
def local(p):
 q=np.array(p,float).copy();x=q[...,0]-.04;y=q[...,1]-.03;q[...,0]=x*C+y*S;q[...,1]=.03-x*S+y*C;return q
def world(q):
 p=np.array(q,float).copy();x=p[...,0];y=p[...,1]-.03;p[...,0]=x*C-y*S+.04;p[...,1]=.03+x*S+y*C;return p
assert sha(src)=='f481e8a0c00eb4ec5baf5d9c43a6bc250f5a28c4475d9d9cba0ea360ca1c8439';bpy.ops.wm.open_mainfile(filepath=str(src));body=bpy.data.objects[NAME];old=co(body.data);oldids=np.empty(len(old),np.int32);body.data.attributes['C23 source vertex id'].data.foreach_get('value',oldids);assert old[oldids==0,2].max()<2.50,'Neck cut would include retained C35 hand'
# Explicit data map precedes any isolation. Ear/head was source-scanned and is
# not a new sphere/primitive substitute. Materials/features remain original.
plan={'source_sha256':sha(src),'head_cut_z':2.50,'voxel_size_u':.018,'ear_size_basis':'Original ears roughly .20-.25u tall/.20u wide; voxel gives >11 cells across, not a final deformation cage','reference_shape':'Actual C38 head from body, complete ears and lower face','protected':'Original body below z2.50, C35 new hand5359, independent eyes/lids/brows/nose/mouth, guitar','authoring_head_isolation_only':True,'production_asset':False,'new_head_canonical_ids':'all0; remesh invalidates original head source-index binding','auto_remesh_animation_limit':'Uniform remesh is a sculpt starting surface, not qualified eye/mouth articulation topology'};(O/'plan.json').write_text(json.dumps(plan,indent=2))
# Extract a real closed head, save a hidden reference for closest-surface fitting.
hm=body.data.copy();head=bpy.data.objects.new('C51 Authoring / source head reference',hm);bpy.context.scene.collection.objects.link(head);head.matrix_world=body.matrix_world.copy();bm=bmesh.new();bm.from_mesh(hm);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector((0,0,2.50)),plane_no=Vector((0,0,1)),clear_inner=True,clear_outer=False);bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(hm);hm.update();bm.free();head.hide_render=True;head.hide_viewport=True
new=bpy.data.objects.new('C51 Authoring / remeshed reference head UNWELDED',hm.copy());bpy.context.scene.collection.objects.link(new);new.matrix_world=body.matrix_world.copy();bpy.context.view_layer.objects.active=new;new.select_set(True);mod=new.modifiers.new('C51 one .018u uniform voxel','REMESH');mod.mode='VOXEL';mod.voxel_size=.018;mod.use_smooth_shade=True;mod.use_remove_disconnected=False;bpy.ops.object.modifier_apply(modifier=mod.name);me=new.data;before=co(me);headlocal=local(before);earweight=sm(.27,.35,np.abs(headlocal[:,0]))*sm(3.12,3.205,headlocal[:,2]);group=new.vertex_groups.new(name='C51 original surface outside intentional ear edit')
for i,w in enumerate(1-earweight):
 if w>0:group.add([i],float(w),'REPLACE')
# Preserving shape outside the edit is geometric fitting, with no guessed source
# IDs. offset0 avoids puffed sockets. The target is this exact original head.
sw=new.modifiers.new('C51 preserve actual source face shape','SHRINKWRAP');sw.target=head;sw.wrap_method='NEAREST_SURFACEPOINT';sw.wrap_mode='ON_SURFACE';sw.offset=0;sw.vertex_group=group.name;bpy.ops.object.modifier_apply(modifier=sw.name);fit=co(me);L=local(fit);x,y,z=L.T;w=sm(.27,.35,np.abs(x))*sm(3.12,3.205,z);g=1-sm(-.12,.04,y);target=1.05*(z-3.40)-.065;L[:,1]+=(target-y)*.65*w*g;Q=world(L).astype(np.float32);Q[w*g==0]=fit[w*g==0]
# One fixed artistic soft-edge treatment on the intentional ear mask, not a
# global auto-remesh relax or an attempt to manufacture a lower topology score.
E=np.empty(len(me.edges)*2,np.int32);me.edges.foreach_get('vertices',E);E=E.reshape(-1,2);weight=sm(.29,.39,np.abs(x))*sm(3.12,3.22,z);index=np.flatnonzero(weight>0);count=np.zeros(len(Q));np.add.at(count,E[:,0],1);np.add.at(count,E[:,1],1);soft=Q.astype(float)
for _ in range(3):
 sums=np.zeros_like(soft);np.add.at(sums,E[:,0],soft[E[:,1]]);np.add.at(sums,E[:,1],soft[E[:,0]]);soft[index]+=.25*weight[index,None]*(sums[index]/count[index,None]-soft[index])
Q=soft.astype(np.float32);me.vertices.foreach_set('co',Q.ravel());me.update()
for key in ['Miao_C35_vertex_id','C23 source vertex id']:
 attr=me.attributes.get(key)
 if attr is not None:me.attributes.remove(attr)
 attr=me.attributes.new(key,'INT','POINT');attr.data.foreach_set('value',np.zeros(len(me.vertices),np.int32))
for f in me.polygons:f.use_smooth=True
# Retain source body below the horizontal neck. A separate remesh reference head
# is deliberate authoring isolation; do not export it as a connected mascot.
bm=bmesh.new();bm.from_mesh(body.data);can=bm.verts.layers.int.get('Miao_C35_vertex_id') or bm.verts.layers.int.new('Miao_C35_vertex_id');bm.verts.ensure_lookup_table();original=list(bm.verts);lookup={v:i for i,v in enumerate(original)}
for i,v in enumerate(original):v[can]=i+1
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector((0,0,2.50)),plane_no=Vector((0,0,1)),clear_outer=True,clear_inner=False);retained=[]
for v in bm.verts:
 if v in lookup:
  i=lookup[v];assert np.array_equal(np.array(v.co,dtype=np.float32),old[i]);v[can]=i+1;retained.append(i)
 else:v[can]=0
assert set(np.flatnonzero(oldids==0)).issubset(set(retained));bm.to_mesh(body.data);body.data.update();bm.free();bpy.context.view_layer.update();sys.path.insert(0,str(R/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
probe=bmesh.new();probe.from_mesh(me);probe.verts.index_update();probe.faces.index_update();probe.faces.ensure_lookup_table();probe.normal_update();selfs=A._self_intersections(probe);report={**plan,'stage':'C51 single remesh-head authoring study; not welded production geometry','source_head_vertices':len(hm.vertices),'new_head_vertices':len(me.vertices),'new_head_faces':len(me.polygons),'head_self_pairs':selfs,'head_nonmanifold_edges':sum(not e.is_manifold for e in probe.edges),'head_signed_volume':probe.calc_volume(signed=True),'source_body_retained_points':len(retained),'source_body_retained_points_bit_exact':True,'C35_new_hand_all_present_exact':True,'outside_ear_reference_fit_max_delta_from_raw_voxel':float(np.linalg.norm(fit[earweight==0]-before[earweight==0],axis=1).max()),'intentional_ear_depth_edit_max_delta':float(np.linalg.norm(Q-fit,axis=1).max()),'connected_head_to_body':False,'art_pass':False,'limits':['Temporary isolated head is explicit authoring only. No complete-skin asset claimed.','No UV/pigment/fur, articulation loops, eyelid contacts, binding or animation acceptance.','Original feature objects unchanged; geometric contact to remeshed skin still requires actual images/probes.']};probe.free();np.savez_compressed(O/'source-body-presence.npz',retained_source_indices=np.array(retained,np.int32),new_head_before_fit=before,new_head_after_fit=fit,new_head_final=Q,ear_weight=earweight);scene=bpy.context.scene;scene.cycles.samples=24;scene.cycles.seed=17;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;bpy.context.preferences.filepaths.save_version=0;native=O/'miao-c51-authoring-isolated-head.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);report['native_sha256']=sha(native);(O/'receipt.json').write_text(json.dumps(report,indent=2));(O/'executed-build-script.py').write_text(Path(__file__).read_text());print('GATE '+json.dumps(report),flush=True);cam=scene.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();sc=cam.data.ortho_scale
for name,pos,target,zoom in [('front',None,None,None),('ears',Vector((0,-6,3.30)),Vector((0,0,3.28)),1.45),('three-quarter',Vector((6,-9,3.9)),Vector((.09881,0,1.609)),sc)]:
 if pos is None:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=sc
 else:cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom
 bpy.context.view_layer.update();scene.render.filepath=str(O/('gray-'+name+'.png'));bpy.ops.render.render(write_still=True)
print('RESULT '+json.dumps({'native_sha256':report['native_sha256'],'head_self_pairs':selfs,'production_asset':False}),flush=True)
