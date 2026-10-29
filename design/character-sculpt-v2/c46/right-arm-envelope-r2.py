"""C46r2 final shape candidate, complete 3D padded reference envelope skin.
All arm skin is inserted into the existing body mesh via actual shared back-root
vertices. No curve tube, palm interface ring, Boolean or component compositing.
"""
import bpy,bmesh,numpy as np,json,hashlib,sys,time,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/character-right-arm-c46/r2';SRC=ROOT/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();h=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';hs=h.read_text();exec(compile(hs[hs.index('def smooth'):hs.index('def main():')],str(h)+'#pure-helpers','exec'),globals())
def main():
 assert not (OUT/'miao-c46-envelope-r2.blend').exists(),'r2 frozen';start=time.time();plan=np.load(OUT/'envelope-r2-plan.npz');bpy.ops.wm.open_mainfile(filepath=str(ROOT/'artifacts/character-right-arm-c41/diagnostic-c41-open-source-boundary.blend'));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;P=np.load(ROOT/'artifacts/character-right-arm-c41/source-cut-map.npz')['original'];boundary=json.loads((ROOT/'artifacts/character-right-arm-c41/source-boundary-preflight.json').read_text())['boundary_loops'][0]['C35_original_indices'];protected={o.name:fingerprint(o) for o in bpy.data.objects if o.name.startswith('Guitar /')};bm=bmesh.new();bm.from_mesh(me);can=bm.verts.layers.int['Miao_C35_vertex_id'];region=bm.faces.layers.int.new('C46 construction region');oldmap={v[can]-1:v for v in bm.verts}
 def V(p):
  v=bm.verts.new(p)
  for layer in bm.verts.layers.int.values():v[layer]=0
  return v
 def face(vs,r):
  f=bm.faces.new(vs);f[region]=r;f.smooth=True
 pv=[oldmap[boundary[i]] if i<808 else V(p) for i,p in enumerate(plan['patch_co'])]
 for tri in plan['patch_tri']:face([pv[int(i)] for i in tri],1)
 # Preserve explicit canonical identity of any hidden torso point moved behind
 # the real rosewood back; no global simplification or nearest-ID restoration.
 wood,nt=actual_tree(bpy.data.objects['Guitar / rosewood body']);body_changes=[]
 for v in bm.verts:
  x,y,z=v.co
  if not(-.56<x<-.14 and 1.405<z<1.68 and -.75<y<-.50):continue
  hit,n,f,d=wood.ray_cast(Vector((x,.3,z)),Vector((0,-1,0)),2)
  if hit is not None and y<hit.y+.023:body_changes.append({'canonical_id':int(v[can]),'Y_delta':float(hit.y+.023-y)});v.co.y=hit.y+.023
 bm.normal_update();torso=BVHTree.FromBMesh(bm);uv=plan['uv'];back=plan['back_y'].copy();depth=plan['depth'];groove=plan['groove'];N=int(plan['outer_count']);up=plan['up'];cl=plan['camera_location'];cu=cl@up;dr=Vector((0,float(up[2]),float(-up[1])));dh=plan['dist_hole']
 def W(q,y):return Vector((float(cl[0]+q[0]),float(y),float((cu+q[1]-up[1]*y)/up[2])))
 obstacles={n:actual_tree(bpy.data.objects[n])[0] for n in ['Guitar / spruce soundboard','Guitar / rosewood body']};tubeY=[]
 for k in range(6):
  ob=bpy.data.objects['Guitar / string '+str(k+1)];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());tm=ev.to_mesh();tubeY.extend((ob.matrix_world@v.co).y for v in tm.vertices);ev.to_mesh_clear()
 tube_front_min=min(tubeY);tube_ceiling=tube_front_min-.023;projection_rows=[]
 for i,q in enumerate(uv):
  if N<=i<N+64:continue
  origin=W(q,-3);hit,n,f,d=torso.ray_cast(origin,dr,8)
  if hit is not None and n.dot(dr)<-.05:
   gap=.015*float(smooth(dh[i]/.08));back[i]=min(back[i],hit.y-gap*dr.y)
  for name,tree in obstacles.items():
   hit,n,f,d=tree.ray_cast(origin,dr,8)
   if hit is not None:back[i]=min(back[i],hit.y-.023*dr.y)
  # Source-ref toe/forearm zone: all six actual tube front extrema provide a
  # conservative +Y backside ceiling. This is no string press/path claim.
  px=627+q[0]*1254/s.camera.data.ortho_scale;py=627-q[1]*1254/s.camera.data.ortho_scale
  if px>330 and py>565:back[i]=min(back[i],tube_ceiling)
 root=pv[808:872];B=[];F=[]
 for i,q in enumerate(uv):
  if N<=i<N+64:b=root[i-N]
  else:b=V(W(q,back[i]))
  B.append(b)
  if i<N:f=b
  else:f=V(W(q,back[i]-max(1e-5,float(depth[i]-min(groove[i],depth[i]*.3)))))
  F.append(f)
 for tri in plan['front_tri']:face([F[int(i)] for i in tri],2)
 for tri in plan['back_tri']:face([B[int(i)] for i in tri[::-1]],3)
 loose=[v for v in bm.verts if not v.link_faces];assert all(v[can]==0 for v in loose);bmesh.ops.delete(bm,geom=loose,context='VERTS');print('REMOVED_UNUSED_VIRTUAL_BACK_POINTS '+str(len(loose)),flush=True)
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);vol=bm.calc_volume(signed=True);bm.to_mesh(me);bm.free();me.update();bpy.context.view_layer.update();actual=arr(me);ids=np.array([v.value for v in me.attributes['Miao_C35_vertex_id'].data]);old=ids>0;present=np.zeros(len(P),bool);present[ids[old]-1]=True;delta=actual[old]-P[ids[old]-1];head=P[:,2]>=2.43;left=P[:,0]>0;assert np.all(present[head|left]);assert np.array_equal(actual[old&(actual[:,2]>=2.43)],P[ids[old&(actual[:,2]>=2.43)]-1]);assert np.array_equal(actual[old&(actual[:,0]>0)],P[ids[old&(actual[:,0]>0)]-1]);assert len(np.unique(ids[old]))==int(old.sum());gexact=protected=={n:fingerprint(bpy.data.objects[n]) for n in protected};assert gexact;top=topo(me);top['euler']=top['vertices']-top['edges']+top['faces'];print('TOPO '+json.dumps(top),flush=True);assert top['components']==1 and not top['boundary_edges'] and not top['nonmanifold_edges'] and top['euler']==2
 r={'stage':'C46r2-last-reference-envelope-padded-3D-arm-appearance-gate','source_C35_sha256':sha(SRC),'script_sha256':sha(__file__),'plan_sha256':sha(OUT/'envelope-r2-plan.json'),'topology':top,'signed_volume':vol,'retained_C35_points':int(old.sum()),'new_points_source0':int((~old).sum()),'head_xpositive_leftC35_all_present_exact':True,'canonical_old_unique_new0':True,'guitar_exact':gexact,'changed_old_hidden_torso_points':int(np.count_nonzero(np.linalg.norm(delta,axis=1)>0)),'body_clearance_changes':body_changes,'actual_six_tube_global_front_minY':tube_front_min,'palm_forearm_backY_ceiling':tube_ceiling,'form':'Full reference projected S envelope front disk/back annulus, shared outer skin seam and actual64-point shoulder back opening. Entire arm/elbow/palm is one smooth depth surface, no tube or palm interface/end ring.','engineering_status':'Basic topology/identity/actual depth constraints only; full actual self/wood/tube/parity still pending. No art or contact pass.','candidate_budget':{'candidate':'r2','maximum':2,'r1':'frozen visually rejected muscle masses/deep wrist slit','no_r3':True},'limits':['Front/back are complete real 3D skin inserted into one body, not independently rendered textures/limbs.','No color/groom/rig/animation/export/public/deploy/new service or fee.']};native=OUT/'miao-c46-envelope-r2.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);r['native_sha256']=sha(native);np.savez_compressed(OUT/'source-output-map.npz',canonical=ids,output_to_original_index=ids-1,original_presence=present,changed_old_indices=ids[old][np.linalg.norm(delta,axis=1)>0]-1,changed_old_deltas=delta[np.linalg.norm(delta,axis=1)>0]);(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('BUILT '+json.dumps({'topology':top,'changed_old':r['changed_old_hidden_torso_points'],'new':r['new_points_source0'],'native':r['native_sha256']}),flush=True)
 s.cycles.samples=12;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;cam=s.camera;r['renders']=[]
 for view in ['front','three-quarter']:
  if view=='three-quarter':cam.location=(-6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler()
  file=OUT/('gray-full-'+view+'.png');s.render.filepath=str(file);bpy.ops.render.render(write_still=True);r['renders'].append({'file':file.name,'sha256':sha(file)});(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
main()
