"""C58 one fixed local same-topology Grab/inflate/crease study; no new mesh."""
import bpy,bmesh,numpy as np,json,hashlib,time,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/character-palm-sculpt-c58';SRC=ROOT/'artifacts/character-body-voxel-c52/miao-c52-whole-body-voxel-authoring-study.blend'
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
 # Two short, broad shallow creases: 46mm full radius at a10mm source cell.
 webs=np.exp(-((tt+.063)/.023)**2)+np.exp(-((tt-.060)/.023)**2)
 ds-=.014*webs*smooth((ss-.17)/.09)*mask
 dy+=.026*webs*np.exp(-((ss-.215)/.095)**2)*front*mask
 Q+=ds[:,None]*D+dt[:,None]*T;Q[:,1]+=dy
 # Four restrained weighted Laplace iterations, only the finite right-palm mask.
 edges=np.array([tuple(e.vertices) for e in me.edges],np.int32);ii=np.r_[edges[:,0],edges[:,1]];jj=np.r_[edges[:,1],edges[:,0]];counts=np.bincount(ii,minlength=len(P));fair=mask*smooth((ss-.01)/.15)
 for k in range(4):
  avg=np.stack([np.bincount(ii,weights=Q[jj,d],minlength=len(P))/counts for d in range(3)],1);Q+=.20*fair[:,None]*(avg-Q)
 Q[~edit]=P[~edit];me.vertices.foreach_set('co',Q.astype(np.float32).ravel());me.update();bpy.context.view_layer.update();actual=arr(me);delta=actual-original;changed=np.flatnonzero(np.any(delta!=0,1));assert np.array_equal(original[~edit],actual[~edit]);assert topo(me)==top
 a=me.attributes.new('C58 source C52 vertex index plus1','INT','POINT');a.data.foreach_set('value',np.arange(1,len(P)+1,dtype=np.int32));assert all(all(v.value==0 for v in a.data) for a in me.attributes if a.domain=='POINT' and a.data_type=='INT' and a.name!='C58 source C52 vertex index plus1')
 assert others=={n:fingerprint(bpy.data.objects[n]) for n in others};assert mats=={n:[m.name if m else None for m in bpy.data.objects[n].data.materials] for n in others}
 np.savez_compressed(OUT/'r2-C52-indexed-palm-delta.npz',source_C52_index_plus1=np.arange(1,len(P)+1,dtype=np.int32),changed_C52_indices=changed,delta=delta,edit_mask=mask.astype(np.float32),origin=C,palm_axis=D,lateral_axis=T)
 native=OUT/'miao-c58-r2-local-palm-study.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 receipt={'stage':'C58r2 finite local palm fields on C52','source_sha256':sha(SRC),'script_sha256':sha(__file__),'native_sha256':sha(native),'reference_sha256':sha(ROOT/'public/character/instrument-scenes-v1/guitar/idle.jpg'),'blender':bpy.app.version_string,'topology':top,'changed_vertices':len(changed),'mask_vertices':int(edit.sum()),'max_displacement':float(np.linalg.norm(delta,axis=1).max()),'changed_bbox':[original[changed].min(0).tolist(),original[changed].max(0).tolist()],'all_body_outside_mask_bit_exact':True,'independent_objects_exact_count':len(others),'independent_materials_exact':True,'identity':'New exact C52 index+1 only; all original C35 identity attributes stay0.','parameters':{'cap_grab':.052,'cap_lateral_expansion':.14,'back_inflate':.030,'web_axis_setback':.014,'crease_depth':.026,'crease_radius':.023,'crease_centers':[-.063,.060],'crease_axis_center':.215,'crease_axis_radius':.095,'smooth_factor':.20,'smooth_iterations':4},'art_status':'Builder actual renders and independent review pending; not approved.','geometry_status':'Only basic topology/locks measured before render; actual self/wood/tube/parity fresh audit pending.','renders':[],'limits':['Head/ears/left hand and all standalone objects unchanged.','Dense voxel shell is not deformation-ready retopology or rig evidence.','No binding, animation, public assets, deployment or service fee.','Native saved before temporary same-body-clay lid render override.']};(OUT/'r2-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
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
  file=OUT/('r2-gray-'+view+'.png');scene.render.filepath=str(file);bpy.ops.render.render(write_still=True);receipt['renders'].append({'file':file.name,'sha256':sha(file)});(OUT/'r2-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 receipt['elapsed_seconds']=time.time()-started;(OUT/'r2-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('RESULT '+json.dumps({'native':sha(native),'changed':len(changed),'max_displacement':receipt['max_displacement'],'renders':receipt['renders']}),flush=True)
main()
