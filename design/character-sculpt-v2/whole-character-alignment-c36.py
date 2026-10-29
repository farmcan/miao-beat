"""C36 single reference-driven whole-character gray candidate. Not production approval.
Pure smooth deformation of C31 continuous surface, no new primitive parts or topology.
Locks all C35 generated hand vertices, both existing arm/paw regions, props and root.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'))
import bx_audit as A
NAME='Miao / continuous pear and rounded-square face'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sm(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def coords(me):
 ar=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',ar);return ar.reshape(-1,3)
def topo(me):
 a=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',a);b=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('loop_total',b);return hashlib.sha256(a.tobytes()+b.tobytes()).hexdigest()
def other_snap():
 result={}
 for ob in bpy.context.scene.objects:
  if ob.name==NAME:continue
  r={'matrix':list(map(list,ob.matrix_world)),'type':ob.type}
  if ob.type=='MESH':r['coords_sha256']=hashlib.sha256(coords(ob.data).tobytes()).hexdigest();r['topology']=topo(ob.data)
  elif ob.type=='ARMATURE':r['bones']=[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in ob.data.bones]
  result[ob.name]=r
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/character-alignment-c36/repaired');p.add_argument('--render',action='store_true');p.add_argument('--samples',type=int,default=16);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
 if (out/'receipt.json').exists():raise RuntimeError('Frozen candidate exists: choose a fresh out directory')
 src=ROOT/'artifacts/character-integrated-gray-c31/miao-c31-head-hand-gray.blend';source_sha=sha(src)
 assert source_sha=='13cbb1da83dfa23c0581ccfe7c07e893b9d0bca6a63244887ad0955f7d0c9c5d'
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;ob=bpy.data.objects[NAME];me=ob.data;assert not ob.modifiers and not me.shape_keys
 before=coords(me);x,y,z=before.T;initial_other=other_snap();topology=topo(me);matrix=list(map(list,ob.matrix_world));ids=np.empty(len(me.vertices),np.int32);me.attributes['C23 source vertex id'].data.foreach_get('value',ids);id_sha=hashlib.sha256(ids.tobytes()).hexdigest()
 # Arms, all new hand skin, wrists and contact transitions are immutable. The lock
 # is deliberately broader than the C35 local region so neighboring agent work
 # can later use exact IDs without spatial re-matching.
 lock=(ids==0)|((z>1.40)&(z<2.43)&(np.abs(x)>.64)&(y<-.20))
 after=before.astype(np.float64).copy();d=np.zeros_like(after)
 # Ear: shorten the over-tall triangular peak 22%, with a smooth base transition.
 # Only the outer ear lobes, not the central skull crown, are in this mask.
 ear=sm(.30,.43,np.abs(x))*sm(3.15,3.24,z)
 d[:,2]+=-.22*np.maximum(z-3.18,0)*ear
 # Pear bulk: lift the widest belly band by .145 u, easing to zero at the hem
 # and below the arm roots. This moves the widest point up instead of uniformly
 # inflating the whole body or changing the instrument/held-paw world relation.
 belly=sm(.32,.65,z)*(1-sm(.95,1.40,z))*sm(-1.40,-1.15,x)
 d[:,2]+=.145*belly
 # Round-square lower face: a broad, shallow cheek/chin plane under the mouth.
 # The center remains near C20's established facial features; sides are raised
 # into the same plane, preventing a single hemispherical muzzle pad read.
 front=(1-sm(-.15,.08,y))
 jaw=sm(2.40,2.60,z)*(1-sm(2.68,2.86,z))*front*(1-sm(.30,.56,np.abs(x)))
 d[:,1]+=.35*jaw*(-.415-y)
 # Projection toward a shared shallow plane replaces the rejected additive pads.
 # No separate cheek or outline mass is added.
 d[lock]=0
 after=(after+d).astype(np.float32);changed=np.any(after!=before,axis=1)
 assert np.array_equal(after[lock],before[lock]);assert np.isfinite(after).all()
 me.calc_loop_triangles();tri=np.array([t.vertices[:] for t in me.loop_triangles],np.int32);touched=changed[tri].any(1);T=tri[touched]
 n0=np.cross(before[T[:,1]]-before[T[:,0]],before[T[:,2]]-before[T[:,0]]);n1=np.cross(after[T[:,1]]-after[T[:,0]],after[T[:,2]]-after[T[:,0]])
 l0=np.linalg.norm(n0,axis=1);l1=np.linalg.norm(n1,axis=1);dots=np.einsum('ij,ij->i',n0,n1)/np.maximum(l0*l1,1e-25)
 print('TRIANGLE_GATE '+json.dumps({'min_before_cross':float(l0.min()),'min_after_cross':float(l1.min()),'min_normal_dot':float(dots.min()),'bad':[{'triangle':T[i].tolist(),'before':before[T[i]].tolist(),'after':after[T[i]].tolist(),'cross_before':float(l0[i]),'cross_after':float(l1[i]),'dot':float(dots[i])} for i in np.flatnonzero((l1<=1e-13)|(dots<=.75))[:12]]}),flush=True)
 assert (l1>1e-13).all() and (dots>.75).all(),'Deformation fold or collapse'
 me.vertices.foreach_set('co',after.ravel());me.update();bpy.context.view_layer.update();bm=bmesh.new();bm.from_mesh(me);bm.normal_update()
 unseen=set(bm.verts);components=0
 while unseen:
  components+=1;stack=[unseen.pop()]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    q=e.other_vert(v)
    if q in unseen:unseen.remove(q);stack.append(q)
 basic={'vertices':len(bm.verts),'faces':len(bm.faces),'components':components,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_vertices':sum(not v.link_edges for v in bm.verts),'signed_volume':bm.calc_volume(signed=True),'changed_vertices':int(changed.sum()),'touched_triangles':len(T),'minimum_old_new_normal_dot':float(dots.min()),'minimum_triangle_area_ratio':float((l1/l0).min()),'maximum_displacement':float(np.linalg.norm(after-before,axis=1).max())}
 bm.free();assert components==1 and basic['nonmanifold_edges']==0 and basic['signed_volume']>0
 head=bmesh.new();head.from_mesh(me);bmesh.ops.delete(head,geom=[v for v in head.verts if v.co.z<2.49],context='VERTS');head.verts.index_update();head.faces.index_update();head.faces.ensure_lookup_table();head.verts.ensure_lookup_table();head.normal_update();head_self=A._self_intersections(head);basic['head_subset_self_intersections']=head_self;basic['head_self_check_skipped']=head_self is None;head.free();assert head_self==0
 assert topo(me)==topology and matrix==list(map(list,ob.matrix_world));assert other_snap()==initial_other
 after_ids=np.empty(len(me.vertices),np.int32);me.attributes['C23 source vertex id'].data.foreach_get('value',after_ids);assert np.array_equal(ids,after_ids)
 s.cycles.samples=a.samples;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';bpy.context.preferences.filepaths.save_version=0
 native=out/'miao-c36-reference-alignment-gray.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 # Reopen the saved deliverable before rendering, prove exact persisted coordinates.
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;assert np.array_equal(coords(bpy.data.objects[NAME].data),after);assert other_snap()==initial_other
 np.savez_compressed(out/'vertex-deformation-evidence.npz',source_vertex_ids=ids,changed_indices=np.flatnonzero(changed),locked_indices=np.flatnonzero(lock),before=before[changed],after=after[changed])
 receipt={'stage':'C36 single whole-character gray form candidate; independent art gate pending','blender_version':list(bpy.app.version),'source':{'path':str(src.relative_to(ROOT)),'sha256':source_sha},'reference':{'path':'public/character/instrument-scenes-v1/guitar/idle.jpg','sha256':sha(ROOT/'public/character/instrument-scenes-v1/guitar/idle.jpg')},'script_sha256':sha(__file__),'native_sha256':sha(native),'topology_sha256_unchanged':topology,'source_ids_sha256_unchanged':id_sha,'body_matrix_unchanged':matrix,'new_C35_vertex_count':int((ids==0).sum()),'new_C35_vertices_bit_exact':True,'both_arm_paw_lock_count':int(lock.sum()),'locked_vertices_bit_exact':True,'all_other_meshes_transforms_skeletons_bit_exact':True,'all_other_objects':initial_other,'basic_form_gate':basic,'changes':{'ear':'Outer ears only: height above z3.18 compressed 22%, smooth base','pear':'Torso widest-band center lifted .145u, support z.32..1.40; left tail outside x=-1.40 unchanged with continuous transition by x=-1.15; all arm/paw locks override','lower_face':'Continuous lower-face skin projects 35% toward y=-.415 shared shallow plane, smooth support z2.40..2.86, absx<=.56; no added cheek pads or face outline inflation; established face features untouched'},'renders':[],'limits':['Gray candidate only, not independent art approval, colored quality or animation pass.','Full-body self-collision and guitar-body collision not exhaustively revalidated; locked C35 hand is unchanged.','UV/groom/rest-position attributes preserved as evidence but not rebound for the changed form; no production color output.','Guitar size/placement, eye spacing/features, both hands and root are unchanged.','No public file, animation, source baseline or deployment is modified.']}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 if a.render:
  cam=s.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();scale=cam.data.ortho_scale
  for name,pos,target,zoom in [('front',None,None,None),('face',Vector((0,-6,3.05)),Vector((0,0,3.03)),1.7),('three-quarter',Vector((6,-9,3.9)),Vector((.09881,0,1.609)),scale)]:
   if pos is None:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=scale
   else:cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom
   bpy.context.view_layer.update();f=out/('gray-'+name+'.png');s.render.filepath=str(f);bpy.ops.render.render(write_still=True);receipt['renders'].append({'file':f.name,'sha256':sha(f),'camera_matrix':list(map(list,cam.matrix_world)),'orthographic_scale':cam.data.ortho_scale})
 assert sha(src)==source_sha;(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('RESULT '+json.dumps({'native':str(native),'basic_gate':basic,'renders':receipt['renders']}),flush=True)
main()
