"""C46r1 one reference-shaped full continuous right arm and round parameter palm.
Low-density appearance gate first. No Boolean, independent toes, animation or fee.
"""
import bpy,bmesh,numpy as np,json,sys,hashlib,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'artifacts/character-right-arm-c46';OUT=BASE/'r1';OUT.mkdir(exist_ok=True);SRC=ROOT/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();h=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';text=h.read_text();exec(compile(text[text.index('def smooth'):text.index('def main():')],str(h)+'#pure-helpers','exec'),globals())
def main():
 started=time.time();assert not (OUT/'miao-c46-reference-round-arm.blend').exists(),'r1 frozen, no overwrite';plan=np.load(BASE/'candidate-r1-geometry-plan.npz');planned=json.loads((BASE/'candidate-r1-plan.json').read_text());assert planned['minimum_analytic_local_sweep_metric']>.4;bpy.ops.wm.open_mainfile(filepath=str(ROOT/'artifacts/character-right-arm-c41/diagnostic-c41-open-source-boundary.blend'));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;original=np.load(ROOT/'artifacts/character-right-arm-c41/source-cut-map.npz')['original'];boundary=json.loads((ROOT/'artifacts/character-right-arm-c41/source-boundary-preflight.json').read_text())['boundary_loops'][0]['C35_original_indices'];protected={o.name:fingerprint(o) for o in bpy.data.objects if o.name.startswith('Guitar /')};bm=bmesh.new();bm.from_mesh(me);can=bm.verts.layers.int['Miao_C35_vertex_id'];reg=bm.faces.layers.int.new('C46 construction region');oldmap={v[can]-1:v for v in bm.verts}
 def V(p):
  v=bm.verts.new(p)
  for layer in bm.verts.layers.int.values():v[layer]=0
  return v
 def face(vs,region):
  f=bm.faces.new(vs);f[reg]=region;f.smooth=True;return f
 co=plan['patch_co'];ptri=plan['patch_tri'];pv=[oldmap[boundary[i]] if i<808 else V(p) for i,p in enumerate(co)]
 for tri in ptri:face([pv[int(i)] for i in tri],1)
 root=pv[808:872];rings=plan['rings'];last=root
 for j in range(1,len(rings)):
  ring=[V(p) for p in rings[j]]
  for k in range(64):face((last[k],last[(k+1)%64],ring[(k+1)%64],ring[k]),2)
  last=ring
 # Continuous full palm front/back grid: root64 is shared with forearm, side
 # seams share exact vertices, terminal33-point edge is welded front-to-back.
 F=[last[32-i] for i in range(33)];B=[last[32]]+last[33:64]+[last[0]];cap=plan['cap'];M=len(cap)-1
 for j in range(1,M+1):
  nf=[V(p) for p in cap[j,0]]
  if j==M:
   assert np.max(np.abs(cap[j,0]-cap[j,1]))<1e-8;nb=nf[:]
  else:
   nb=[nf[0]]+[V(p) for p in cap[j,1,1:-1]]+[nf[-1]]
  for i in range(32):face((F[i+1],F[i],nf[i],nf[i+1]),3);face((B[i],B[i+1],nb[i+1],nb[i]),3)
  F,B=nf,nb
 # Actual back-of-rosewood clearance, on the lower hidden torso/front collar.
 # This is an anatomical shallow +Y skin adjustment, never a guitar-shaped cut.
 tree,nt=actual_tree(bpy.data.objects['Guitar / rosewood body']);changed_body=[]
 for v in bm.verts:
  x,y,z=v.co
  if not(-.56<x<-.14 and 1.405<z<1.68 and -.75<y<-.50):continue
  hit,n,f,d=tree.ray_cast(Vector((x,.3,z)),Vector((0,-1,0)),2)
  if hit is None:continue
  desired=hit.y+.023
  if v.co.y<desired:
   delta=desired-v.co.y;v.co.y=desired;changed_body.append({'canonical_id':int(v[can]),'Y_delta':float(delta),'actual_wood_back_y':hit.y,'desired_rear_clearance':.023})
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);volume=bm.calc_volume(signed=True);bm.to_mesh(me);bm.free();me.update();bpy.context.view_layer.update();actual=arr(me);ids=np.array([v.value for v in me.attributes['Miao_C35_vertex_id'].data]);old=ids>0;present=np.zeros(len(original),bool);present[ids[old]-1]=True;delta=actual[old]-original[ids[old]-1];head=original[:,2]>=2.43;left=original[:,0]>0;assert np.all(present[head|left]);lockedout=np.flatnonzero(old&(actual[:,2]>=2.43));assert np.array_equal(actual[lockedout],original[ids[lockedout]-1]);assert np.array_equal(actual[old&(actual[:,0]>0)],original[ids[old&(actual[:,0]>0)]-1]);assert len(np.unique(ids[old]))==int(old.sum());gexact=protected=={n:fingerprint(bpy.data.objects[n]) for n in protected};assert gexact;top=topo(me);assert top['components']==1 and top['boundary_edges']==0 and top['nonmanifold_edges']==0;top['euler']=top['vertices']-top['edges']+top['faces'];assert top['euler']==2
 receipt={'stage':'C46r1-reference-round-arm-low-density-appearance-gate','original_C35_sha256':sha(SRC),'script_sha256':sha(__file__),'reference_guides_sha256':sha(BASE/'reference-guides.json'),'reference_guide_preview_sha256':sha(BASE/'original-reference-arm-guides.svg.png'),'analytic_plan':planned,'topology':top,'signed_volume':volume,'new_points':int((~old).sum()),'retained_points':int(old.sum()),'head_and_xpositive_left_locked_exact':True,'canonical_nonzero_unique_new0':True,'guitar_exact':gexact,'source_points_changed_for_hidden_front_wood_clearance':int(np.count_nonzero(np.linalg.norm(delta,axis=1)>0)),'actual_wood_clearance_body_adjustments':changed_body,'palm_method':'One continuous 33-column front/back parameter grid,14rows; all cap side/terminal vertices genuinely shared. Three shallow edge undulations, not independent toe volumes or a flat sleeve end.','engineering_status':'Basic closed topology and locks only; actual self/wood/tube/parity/normal/continuous contact gates still pending. Appearance must be inspected first.','art_status':'Not approved; builder actual front/3Q inspection and independent three-role gray reviews required.','candidate_budget':{'candidate':'r1','maximum_art_candidates':2},'limits':['No color/groom/UV/rig/animation/GLB/public/deploy/hosted service or fee.','Analytic curvature bound is not a global actual self-intersection test.','Body-front adjustment explicitly changes local original points but preserves canonical identity, not globally bit-exact old geometry.'],'seconds_before_render':time.time()-started};native=OUT/'miao-c46-reference-round-arm.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);receipt['native_sha256']=sha(native);np.savez_compressed(OUT/'source-output-map.npz',canonical=ids,output_to_original_index=ids-1,original_presence=present,changed_retained_original_indices=ids[old][np.linalg.norm(delta,axis=1)>0]-1,changed_retained_deltas=delta[np.linalg.norm(delta,axis=1)>0]);(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('BUILT '+json.dumps({'topology':top,'new':receipt['new_points'],'retained':receipt['retained_points'],'changed_old':receipt['source_points_changed_for_hidden_front_wood_clearance'],'native':receipt['native_sha256']}),flush=True)
 s.cycles.samples=16;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;cam=s.camera;receipt['renders']=[]
 for view in ['front','three-quarter']:
  if view=='three-quarter':cam.location=(-6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler()
  file=OUT/('gray-full-'+view+'.png');s.render.filepath=str(file);bpy.ops.render.render(write_still=True);receipt['renders'].append({'file':file.name,'sha256':sha(file)});(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
main()
