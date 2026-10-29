"""C62 one fixed local same-topology Grab/inflate/crease study; no new mesh."""
import bpy,bmesh,numpy as np,json,hashlib,time,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/character-palm-sculpt-c62';SRC=ROOT/'artifacts/character-body-voxel-c52/miao-c52-whole-body-voxel-authoring-study.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
h=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';text=h.read_text();exec(compile(text[text.index('def smooth'):text.index('def main():')],str(h)+'#helpers','exec'),globals())
def main():
 started=time.time();assert sha(SRC)=='630c27d7de8d94f0fb85201e0a216bb7055c223bb85b6d05b704fd6ba0ad40bc';bpy.ops.wm.open_mainfile(filepath=str(SRC));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;scene=bpy.context.scene;original=arr(me).copy();P=original.astype(np.float64);bpy.context.view_layer.update();others={o.name:fingerprint(o) for o in bpy.data.objects if o!=body and o.type in {'MESH','CURVE','CURVES'} and not(o.type=='CURVES' and o.hide_render and 'plush' in o.name.lower())};mats={n:[m.name if m else None for m in bpy.data.objects[n].data.materials] for n in others};top=topo(me)
 C=np.array([-.58,-1.19,1.80]);D=np.array([.78,0,-.625]);D/=np.linalg.norm(D);T=np.array([.625,0,.78]);T/=np.linalg.norm(T);ss=(P-C)@D;tt=(P-C)@T
 mask=smooth((ss+.18)/.13)*(1-smooth((ss-.34)/.04))*smooth((tt+.29)/.09)*(1-smooth((tt-.19)/.06))*smooth((-.93-P[:,1])/.12)*smooth((P[:,2]-1.40)/.10)*(1-smooth((P[:,0]+.20)/.07))
 edit=mask>0;Q=P.copy();cap=smooth((ss-.12)/.18);front=smooth((-1.11-P[:,1])/.16)
 # Finite, author-stated low-cost brush fields. Same original shell stays intact.
 # Broad Grab tucks the pointed middle tip; inflate rounds back/edge, no tube/loft.
 ds=-.052*cap*(1-.40*smooth(np.abs(tt)/.14))*mask
 dt=.14*tt*cap*mask
 dy=-.030*np.exp(-((ss-.08)/.16)**2-((tt+.015)/.18)**2)*front*mask
 Q+=ds[:,None]*D+dt[:,None]*T;Q[:,1]+=dy
 # Four restrained weighted Laplace iterations, only the finite right-palm mask.
 edges=np.array([tuple(e.vertices) for e in me.edges],np.int32);ii=np.r_[edges[:,0],edges[:,1]];jj=np.r_[edges[:,1],edges[:,0]];counts=np.bincount(ii,minlength=len(P));fair=mask*smooth((ss-.01)/.15)
 for k in range(4):
  avg=np.stack([np.bincount(ii,weights=Q[jj,d],minlength=len(P))/counts for d in range(3)],1);Q+=.20*fair[:,None]*(avg-Q)
 # Lock the broad form first. The actual final surface normals drive detail.
 Q[~edit]=P[~edit];me.vertices.foreach_set('co',Q.astype(np.float32).ravel());me.update();bpy.context.view_layer.update()
 broad=arr(me).copy();Q=broad.astype(np.float64);N=np.empty(len(P)*3,np.float32);me.vertices.foreach_get('normal',N);N=N.reshape(-1,3).astype(np.float64);N/=np.maximum(np.linalg.norm(N,axis=1)[:,None],1e-12)
 fs=(Q-C)@D;ft=(Q-C)@T;facing=smooth((-N[:,1]-.10)/.30)
 webs=np.exp(-((ft+.063)/.030)**2)+np.exp(-((ft-.060)/.030)**2)
 axis_setback=-.030*webs*smooth((fs-.14)/.10)*mask
 crease=.028*webs*np.exp(-((fs-.215)/.100)**2)*facing*mask
 # Actual pixel budget from the saved matched camera and the authored3Q camera.
 cam=scene.camera;camera_scale=cam.data.ortho_scale;front_rotation=cam.rotation_euler.copy();projection=[]
 for view in ['front','three-quarter','palm-front','palm-three-quarter']:
  rotation=front_rotation.copy();scale=camera_scale
  if view=='three-quarter':rotation=(Vector((.09881,0,1.609))-Vector((-6,-9,3.9))).to_track_quat('-Z','Y').to_euler()
  if view=='palm-front':rotation=(Vector((-.65,-1.05,1.97))-Vector((-.65,-12,2.7))).to_track_quat('-Z','Y').to_euler();scale=1.4
  if view=='palm-three-quarter':rotation=(Vector((-.65,-1.05,1.97))-Vector((-4,-6,3.1))).to_track_quat('-Z','Y').to_euler();scale=1.4
  def px(v):
   q=rotation.to_matrix().inverted()@Vector(v);return float(np.hypot(q.x,q.y)*512/scale)
  projection.append({'view':view,'ortho_scale':scale,'web_axis_setback_030_projected_px':px(D*.030),'crease_full_width_060_projected_px':px(T*.060),'toe_center_spacing_123_projected_px':px(T*.123),'normal_depth_is_shading_not_visible_width':True})
 preflight={'order':'Broad Grab/inflate then4*.20Smooth, then these fixed final crease/web fields, no postsmooth.','source_cell':.010,'crease_radius':.030,'cells_per_radius':3,'normal_crease_peak':.028,'web_axis_setback':.030,'projection_before_detail_application':projection,'actual_crease_peak_before_apply':float(crease.max()),'no_front_y_half_depth_multiplier':True,'final_surface_normals_used':True};(OUT/'main-detail-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n');print('DETAIL_PREFLIGHT '+json.dumps(preflight),flush=True)
 Q+=axis_setback[:,None]*D-crease[:,None]*N
 # No Smooth follows the details. Every mask-zero point stays exactly fixed.
 Q[~edit]=P[~edit];me.vertices.foreach_set('co',Q.astype(np.float32).ravel());me.update();bpy.context.view_layer.update();actual=arr(me);delta=actual-original;changed=np.flatnonzero(np.any(delta!=0,1));assert np.array_equal(original[~edit],actual[~edit]);assert topo(me)==top
 a=me.attributes.new('C62 source C52 vertex index plus1','INT','POINT');a.data.foreach_set('value',np.arange(1,len(P)+1,dtype=np.int32));assert all(all(v.value==0 for v in a.data) for a in me.attributes if a.domain=='POINT' and a.data_type=='INT' and a.name!='C62 source C52 vertex index plus1')
 assert others=={n:fingerprint(bpy.data.objects[n]) for n in others};assert mats=={n:[m.name if m else None for m in bpy.data.objects[n].data.materials] for n in others}
 np.savez_compressed(OUT/'main-C52-indexed-palm-delta.npz',source_C52_index_plus1=np.arange(1,len(P)+1,dtype=np.int32),changed_C52_indices=changed,delta=delta,actual_coordinates=actual,source_coordinates=original,broad_coordinates=broad,final_surface_normals=N.astype(np.float32),final_normal_crease=crease.astype(np.float32),final_axis_setback=axis_setback.astype(np.float32),edit_mask=mask.astype(np.float32),origin=C,palm_axis=D,lateral_axis=T)
 native=OUT/'miao-c62-main-local-palm-study.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 receipt={'stage':'C62-main finite local palm fields on C52','source_sha256':sha(SRC),'script_sha256':sha(__file__),'native_sha256':sha(native),'reference_sha256':sha(ROOT/'public/character/instrument-scenes-v1/guitar/idle.jpg'),'blender':bpy.app.version_string,'topology':top,'changed_vertices':len(changed),'mask_vertices':int(edit.sum()),'max_displacement':float(np.linalg.norm(delta,axis=1).max()),'changed_bbox':[original[changed].min(0).tolist(),original[changed].max(0).tolist()],'all_body_outside_mask_bit_exact':True,'independent_objects_exact_count':len(others),'independent_materials_exact':True,'identity':'New exact C52 index+1 only; all original C35 identity attributes stay0.','parameters':{'cap_grab':.052,'cap_lateral_expansion':.14,'back_inflate':.030,'web_axis_setback':.030,'crease_depth':.028,'crease_radius':.030,'crease_centers':[-.063,.060],'crease_axis_center':.215,'crease_axis_radius':.100,'postsmooth_detail':True,'detail_preflight':preflight,'smooth_factor':.20,'smooth_iterations':4},'art_status':'Builder actual renders and independent review pending; not approved.','geometry_status':'Only basic topology/locks measured before render; actual self/wood/tube/parity fresh audit pending.','renders':[],'limits':['Head/ears/left hand and all standalone objects unchanged.','Dense voxel shell is not deformation-ready retopology or rig evidence.','No binding, animation, public assets, deployment or service fee.','Native saved before temporary same-body-clay lid render override.']};(OUT/'main-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 cam=scene.camera;cl=cam.location.copy();cr=cam.rotation_euler.copy();cs=cam.data.ortho_scale;scene.cycles.samples=16;scene.cycles.seed=17;scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.render.use_border=False;scene.render.use_crop_to_border=False
 # Equal gray skin for integrated eyelids prevents orange-to-luma fake halo.
 lidmats={};clay=body.data.materials[0]
 for n in others:
  if ' / upper lid ' in n or ' / lower lid ' in n:
   ob=bpy.data.objects[n];lidmats[n]=list(ob.data.materials);ob.data.materials.clear();ob.data.materials.append(clay)
 for view in ['front','three-quarter','palm-front','palm-three-quarter']:
  cam.location=cl;cam.rotation_euler=cr;cam.data.ortho_scale=cs
  if view=='three-quarter':cam.location=(-6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler()
  if view=='palm-front':cam.location=(-.65,-12,2.7);cam.rotation_euler=(Vector((-.65,-1.05,1.97))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.4
  if view=='palm-three-quarter':cam.location=(-4,-6,3.1);cam.rotation_euler=(Vector((-.65,-1.05,1.97))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.4
  file=OUT/('main-gray-'+view+'.png');scene.render.filepath=str(file);bpy.ops.render.render(write_still=True);receipt['renders'].append({'file':file.name,'sha256':sha(file)});(OUT/'main-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 receipt['elapsed_seconds']=time.time()-started;(OUT/'main-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('RESULT '+json.dumps({'native':sha(native),'changed':len(changed),'max_displacement':receipt['max_displacement'],'renders':receipt['renders']}),flush=True)
main()
