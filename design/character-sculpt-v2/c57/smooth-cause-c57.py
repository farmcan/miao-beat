"""C57 same-source/same.010 read-only before-Smooth cause decomposition.
No resolution change; C52 frozen. Only save a no-Smooth branch if actual self0.
"""
import bpy,bmesh,numpy as np,json,sys,time,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/character-body-voxel-c57';SRC=ROOT/'artifacts/character-local-merge-c49/miao-c49-local-merge.blend';FROZEN=ROOT/'artifacts/character-body-voxel-c52/miao-c52-whole-body-voxel-authoring-study.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();helper=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';h=helper.read_text();exec(compile(h[h.index('def smooth'):h.index('def main():')],str(helper)+'#pure-helpers','exec'),globals())
def actual_self(me):
 me.calc_loop_triangles();co=[v.co.copy() for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(co,tri,all_triangles=True);rows=[]
 for a,b in tree.overlap(tree):
  if a>=b or set(tri[a])&set(tri[b]):continue
  p=np.array([co[i][:] for i in set(tri[a])|set(tri[b])]);rows.append({'triangles':[a,b],'vertices':[list(tri[a]),list(tri[b])],'bbox':[p.min(0).tolist(),p.max(0).tolist()]})
 return rows

def main():
 assert not (OUT/'smooth-cause-receipt.json').exists();start=time.time();sourcehash=sha(SRC);frozenhash=sha(FROZEN);bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];clay=bpy.data.materials.new('C57 matched source body clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.4,.4,.4,1);bs.inputs['Roughness'].default_value=.68;body.data.materials.clear();body.data.materials.append(clay);dg=bpy.context.evaluated_depsgraph_get();baked=bpy.data.meshes.new_from_object(body.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);body.data=baked
 for mod in list(body.modifiers):body.modifiers.remove(mod)
 bpy.ops.object.select_all(action='DESELECT');body.hide_set(False);body.select_set(True);bpy.context.view_layer.objects.active=body
 if body.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 me=body.data;me.remesh_voxel_size=.010;me.remesh_voxel_adaptivity=0.;me.use_remesh_preserve_volume=True;me.use_remesh_fix_poles=True
 if hasattr(me,'use_remesh_preserve_attributes'):me.use_remesh_preserve_attributes=False
 bpy.ops.object.voxel_remesh();me=body.data;before=arr(me).copy();faces=[list(f.vertices) for f in me.polygons];before_topo=topo(me);pre=actual_self(me);np.savez_compressed(OUT/'same-fixed-remesh-before-smooth.npz',co=before,faces=np.array(faces,np.int32));print('BEFORE_SMOOTH_SELF '+str(len(pre)),flush=True)
 # Apply identical oneSmooth in memory solely to prove this replay matches C52.
 mod=body.modifiers.new('C57 read-only sameSmooth causal replay','SMOOTH');mod.factor=.15;mod.iterations=1;bpy.ops.object.modifier_apply(modifier=mod.name);after=arr(body.data).copy();after_faces=[list(f.vertices) for f in body.data.polygons];bpy.ops.wm.open_mainfile(filepath=str(FROZEN));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];frozen=arr(body.data);coexact=bool(np.array_equal(after,frozen));topoexact=after_faces==[list(f.vertices) for f in body.data.polygons];samecount=len(after)==len(frozen);err=float(np.max(np.abs(after-frozen))) if samecount else None;prior=json.loads((ROOT/'artifacts/character-body-voxel-c52/post-voxel-self-readback.json').read_text());r={'stage':'C57-same-source-same-voxel-beforeSmooth-readonly-cause-test','source_C49_sha256':sourcehash,'frozen_C52_sha256':frozenhash,'script_sha256':sha(__file__),'fixed_options':{'voxel':.010,'adaptivity':0,'preserve_volume':True,'fix_poles':True},'beforeSmooth_topology':before_topo,'beforeSmooth_actual_non_neighbour_triangle_self_pairs':len(pre),'beforeSmooth_pair_geometry':pre,'same_oneSmooth_replay_matches_frozen_C52_ordered_coordinates_exact':coexact,'same_oneSmooth_replay_matches_frozen_C52_ordered_topology_exact':topoexact,'maximum_replay_C52_coordinate_error':err,'frozen_C52_afterSmooth_actual_self_pairs':prior['actual_non_neighbour_body_triangle_self_pairs'],'native_remesh_already_self_intersected':bool(pre),'noSmooth_branch_saved':False,'seconds':time.time()-start}
 if pre:r['decision']='Native .010 remesh itself already has actual self; stop this fixed global-remesh parameter. No noSmooth asset and no resolution/flag scan.'
 elif not(coexact and topoexact):r['decision']='NoSmooth self0 but replay not exact; no causal pass or branch until deterministic discrepancy understood.'
 else:
  # New conditional authoring branch, original C52/C49 untouched. Topology is
  # reconstructed from exact preSmooth coordinates/faces; original identities0.
  old=body.data;me=bpy.data.meshes.new('C57 noSmooth fixed remesh');me.from_pydata(before,[],faces);me.update();me.materials.append(old.materials[0]);body.data=me
  for f in me.polygons:f.use_smooth=True
  for name in ['Miao_C35_vertex_id','C23 source vertex id','C52 source C49 vertex id']:
   a=me.attributes.new(name,'INT','POINT');a.data.foreach_set('value',np.zeros(len(me.vertices),np.int32))
  body.vertex_groups.clear();native=OUT/'miao-c57-noSmooth-authoring-study.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);r['noSmooth_branch_saved']=True;r['native_sha256']=sha(native);r['decision']='NoSmooth self0, exact sameSmooth replay reproduces C52; save conditional branch for actual512front/3Q preservation inspection. Not contact or art pass.';cam=s.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();scale=cam.data.ortho_scale;s.cycles.samples=16;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
  for view in ['front','three-quarter']:
   if view=='three-quarter':cam.location=(-6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler()
   s.render.filepath=str(OUT/('noSmooth-gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
 assert sha(SRC)==sourcehash and sha(FROZEN)==frozenhash;r['source_and_frozen_native_unchanged']=True;(OUT/'smooth-cause-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps({k:v for k,v in r.items() if k!='beforeSmooth_pair_geometry'}),flush=True)
main()
