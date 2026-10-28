"""C15 local volume route, zero-fee Blender-bundled OpenVDB.
First prove closed actual-mesh -> SDF -> bounded ndarray -> quads.
Candidate stages are intentionally separate from API preflight.
"""
import bpy,bmesh,numpy as np,math,sys,json,hashlib,time,argparse,gc
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import openvdb as vdb
p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/character-paw-c15');p.add_argument('--probe-only',action='store_true');p.add_argument('--voxel',type=float,default=.006);p.add_argument('--samples',type=int,default=32);p.add_argument('--size',type=int,default=1024);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];out=root/a.out;out.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(root/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_retopo as R;import bx_audit as A
origin=Vector((-.1950536246756659,-.85,1.5567366254980208));gu=Vector((1.0169595357706245,0,.40048756408789304));gv=Vector((-.40048756408789304,0,1.0169595357706245));U=gu.normalized();V=gv.normalized()
def g(u,v,y):return origin+gu*u+gv*v+Vector((0,y-origin.y,0))
# Reuse frozen C11's authored palm/toes, never C13's failed roots. Only functions,
# with collar and its rear socket removed in-memory; frozen source is never edited.
c11source=root/'design/character-sculpt-v2/paw-volume-study.py';c11sha=sha(c11source);text=c11source.read_text()
common=text[text.index('def mesh('):text.index('def make_hand():')];exec(compile(common,str(c11source)+'[helpers]','exec'),globals())
hand_code=text[text.index('def make_hand():'):text.index('def cutter_box():')]
hand_code=hand_code.replace('for strip in [2,3]:','for strip in []:')
i=hand_code.index(' # Wrist collar,');j=hand_code.index(' hand=mesh(',i);hand_code=hand_code[:i]+hand_code[j:]
hand_code=hand_code.replace("'C11 / reference palm and curled short toes'","'C15 / closed C11 round palm and curled toes'")
exec(compile(hand_code,str(c11source)+'[closed-palm-no-rear-socket]','exec'),globals())
def sm(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def smin(x,y,k):
 h=np.maximum(k-np.abs(x-y),0)/max(k,1e-9) if np.isscalar(k) else np.maximum(k-np.abs(x-y),0)/np.maximum(k,1e-9)
 return np.minimum(x,y)-h*h*k*.25

def sdf_from_mesh(o,voxel,half=12):
 dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);me=ev.to_mesh();co=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',co);co=co.reshape(-1,3);m=np.array(o.matrix_world,dtype=np.float32);co=np.ascontiguousarray(co@m[:3,:3].T+m[:3,3]);me.calc_loop_triangles();tri=np.empty(len(me.loop_triangles)*3,np.uint32);me.loop_triangles.foreach_get('vertices',tri);tri=np.ascontiguousarray(tri.reshape(-1,3));grid=vdb.FloatGrid.createLevelSetFromPolygons(co,triangles=tri,transform=vdb.createLinearTransform(voxel),halfWidth=float(half));ev.to_mesh_clear();return grid

def mesh_from_grid(grid,name):
 vs,fs=grid.convertToQuads(0.0);o=mesh(name,np.asarray(vs).tolist(),np.asarray(fs).tolist());bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(o.data);bm.free();return o

def probe():
 started=time.time();vs=np.array([[-.1,-.1,-.1],[.1,-.1,-.1],[.1,.1,-.1],[-.1,.1,-.1],[-.1,-.1,.1],[.1,-.1,.1],[.1,.1,.1],[-.1,.1,.1]],np.float32);faces=np.array([[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],np.uint32)
 grid=vdb.FloatGrid.createLevelSetFromPolygons(vs,quads=faces,transform=vdb.createLinearTransform(.005),halfWidth=8.);shape=(65,65,65);ijk=(-32,-32,-32);data=np.empty(shape,np.float32);grid.copyToArray(data,ijk);assert data[32,32,32]<0 and data[0,0,0]>0
 # Roundtrip no field edits: actual mesh SDF, not primitive-only smoke test.
 result=vdb.FloatGrid(.08);result.transform=grid.transform;result.copyFromArray(data,ijk,0.0);o=mesh_from_grid(result,'C15 / bounded actual mesh SDF preflight');stats=topo(o);assert stats['components']==1 and stats['non_manifold_edges']==0
 bounds=np.array([v.co[:] for v in o.data.vertices]);report={'stage':'API-small-actual-mesh-preflight','blender':bpy.app.version_string,'module':vdb.__file__,'input':'closed cube 8 vertices / 6 authored quad faces','apis_executed':['FloatGrid.createLevelSetFromPolygons(points=float32,quads=uint32,transform=createLinearTransform(.005),halfWidth=8.)','grid.copyToArray(float32[65,65,65],ijk=(-32,-32,-32))','FloatGrid(.08).copyFromArray(data,ijk,tolerance=0.0)','FloatGrid.convertToQuads(0.0)'],'array_shape':shape,'dense_array_bytes':int(data.nbytes),'center_sdf':float(data[32,32,32]),'outside_sdf':float(data[0,0,0]),'output':stats,'bounds_min':bounds.min(0).tolist(),'bounds_max':bounds.max(0).tolist(),'seconds':time.time()-started,'verdict':'API and closed-mesh occupancy roundtrip work; no character/craft/contact acceptance'};(out/'small-mesh-preflight.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+json.dumps(report))

def array_sample(D,ijk,voxel,points):
 p=np.asarray(points,dtype=float)/voxel-np.asarray(ijk);i=np.clip(np.floor(p).astype(int),0,np.array(D.shape)-2);t=np.clip(p-i,0,1);v=np.zeros(len(p),np.float64)
 for x in [0,1]:
  for y in [0,1]:
   for z in [0,1]:v+=(t[:,0] if x else 1-t[:,0])*(t[:,1] if y else 1-t[:,1])*(t[:,2] if z else 1-t[:,2])*D[i[:,0]+x,i[:,1]+y,i[:,2]+z]
 return v

def residuals(before,after):
 dg=bpy.context.evaluated_depsgraph_get();bh=BVHTree.FromObject(after,dg);co=np.array([v.co[:] for v in before.data.vertices]);outside=~((co[:,0]>.70)&(co[:,0]<1.75)&(co[:,1]<-.10)&(co[:,2]>1.30)&(co[:,2]<2.34));head=(np.abs(co[:,0])<.80)&(co[:,2]>2.25);front_head_y=float(np.quantile(co[head,1],.20));eye=head&(co[:,1]<=front_head_y)
 report={'front_head_region_definition':{'abs_x_max':.80,'z_min':2.25,'y_max_actual_front_20pct_quantile':front_head_y}}
 for name,mask in [('non_wrist',outside),('front_head_eye_surround',eye)]:
  ids=np.flatnonzero(mask);ids=ids[::max(1,len(ids)//6000)];ds=[]
  for i in ids:
   hit,n,face,d=bh.find_nearest(Vector(co[i]));ds.append(d)
  report[name]={'sample_count':len(ds),'method':'actual reference vertices to new evaluated BVH nearest distance; measurement only, not sculpt fallback','mean':float(np.mean(ds)),'p95':float(np.percentile(ds,95)),'max':float(np.max(ds)),'voxel':a.voxel}
 return report

def local_fragment_cleanup(o):
 bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();seen=set();parts=[];delete=[]
 for v in bm.verts:
  if v.index in seen:continue
  stack=[v];seen.add(v.index);vs=[]
  while stack:
   q=stack.pop();vs.append(q)
   for e in q.link_edges:
    w=e.other_vert(q)
    if w.index not in seen:seen.add(w.index);stack.append(w)
  if len(vs)<1000:
   coords=np.array([q.co[:] for q in vs]);faces={f for q in vs for f in q.link_faces};volume=sum(f.verts[0].co.cross(f.verts[j].co).dot(f.verts[j+1].co)/6 for f in faces for j in range(1,len(f.verts)-1));lo=coords.min(0);hi=coords.max(0);inside=bool(np.all(lo>np.array([.70,-1.44,1.30])) and np.all(hi<np.array([1.74,-.10,2.34])))
   row={'vertices':len(vs),'faces':len(faces),'bounds_min':lo.tolist(),'bounds_max':hi.tolist(),'signed_volume':volume,'entirely_within_wrist_ROI':inside,'deleted':inside and abs(volume)<.001}
   parts.append(row)
   if row['deleted']:delete.extend(vs)
  else:parts.append({'vertices':len(vs),'deleted':False,'main':True})
 (out/'component-cleanup.json').write_text(json.dumps(parts,indent=2)+'\n')
 assert all(p.get('main') or p['deleted'] for p in parts),{'unacceptable_nonlocal_or_large_fragment':parts}
 if delete:bmesh.ops.delete(bm,geom=delete,context='VERTS');bm.to_mesh(o.data);o.data.update()
 bm.free();return parts

def candidate():
 started=time.time();src=root/'artifacts/character-paw-c11-r2/miao-c11-paw-volume.blend';source_sha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;original=bpy.data.objects['Miao / continuous pear and rounded-square face'];s.camera.data.lens=s.camera.data.lens;bpy.context.view_layer.update()
 # Real C11 full-body mesh, not an SDF primitive replacement of the cat.
 baseline=original.copy();baseline.data=original.data.copy();baseline.name='C15 diagnostic / unchanged C11 baseline';s.collection.objects.link(baseline);baseline.hide_render=True;baseline.hide_set(True)
 hand,hand_design=make_hand();hand.name='C15 diagnostic / closed full reference palm';hand.hide_render=True
 vox=a.voxel;transform=vdb.createLinearTransform(vox);grid=sdf_from_mesh(original,vox,12);pgrid=sdf_from_mesh(hand,vox,12)
 lo=np.array([.70,-1.44,1.30]);hi=np.array([1.74,-.10,2.34]);ijk=np.floor(lo/vox).astype(int);maxijk=np.ceil(hi/vox).astype(int);shape=tuple(int(i) for i in maxijk-ijk+1);n=int(np.prod(shape));conservative_peak=n*4*18
 assert conservative_peak<1_000_000_000,{'dense_peak_estimate':conservative_peak,'shape':shape}
 D=np.empty(shape,np.float32);P=np.empty(shape,np.float32);grid.copyToArray(D,tuple(int(i) for i in ijk));pgrid.copyToArray(P,tuple(int(i) for i in ijk));del pgrid;gc.collect()
 axes=[(ijk[j]+np.arange(shape[j],dtype=np.float32))*vox for j in range(3)];X=axes[0][:,None,None];Y=axes[1][None,:,None];Z=axes[2][None,None,:]
 # Explicit old near-wrist removal: intersection with complement of an elliptic
 # cylinder in front of Y=-.37. Its exact field/coverage is persisted.
 cut=np.maximum((np.sqrt(((X-1.205)/.38)**2+((Z-1.80)/.40)**2)-1)*.38,Y+.37)
 cut=np.broadcast_to(cut,shape);clipped=np.maximum(D,-cut)
 # Continuous local elliptical loft, capped only inside the reference palm and
 # inside the source forearm. Occupancy is exact for this implicit loft; radial
 # distance is first-order ellipse distance, not claimed globally exact SDF.
 ys=np.array([-1.13,-1.02,-.84,-.62,-.40,-.16],np.float32)
 czs=np.array([1.72,1.72,1.75,1.80,1.85,1.88],np.float32);rxs=np.array([.12,.150,.177,.190,.205,.215],np.float32);rzs=np.array([.11,.125,.150,.175,.205,.225],np.float32)
 yf=axes[1];j=np.clip(np.searchsorted(ys,yf)-1,0,len(ys)-2);t=sm((yf-ys[j])/(ys[j+1]-ys[j]));interp=lambda ar:(ar[j]*(1-t)+ar[j+1]*t)[None,:,None]
 cz=interp(czs);rx=interp(rxs);rz=interp(rzs);rad=(np.sqrt(((X-1.205)/rx)**2+((Z-cz)/rz)**2)-1)*np.minimum(rx,rz);loft=np.maximum(rad,np.maximum(ys[0]-Y,Y-ys[-1]));del rad
 # Bounded smooth-min only in this wrist transition. It is not Laplacian mesh
 # relaxation, a boolean bridge or an independently delivered limb.
 K=.065*sm((Y+1.18)/.12)*(1-sm((Y+.23)/.10))*sm((2.00-Z)/.16)
 K=np.broadcast_to(K,shape);preserved=np.minimum(clipped,P);result=smin(preserved,loft,K).astype(np.float32)
 # Source identity diagnostic: nearest contributing scalar field, plus blend zone.
 # This describes volume contributors, not disconnected production components.
 contributor=np.where(P<clipped,1,0).astype(np.int8);contributor=np.where(loft<preserved,2,contributor).astype(np.int8);blend_changed=(result<np.minimum(preserved,loft)-vox*.05)
 # Verify removal against actual C11 authoring source face centres (blue collar).
 diag=root/'artifacts/character-paw-c13/diagnostic-c11/diagnostic-c11-provenance.blend'
 with bpy.data.libraries.load(str(diag),link=False) as (data_from,data_to):data_to.objects=['Miao / continuous pear and rounded-square face']
 prov=data_to.objects[0];collar_pts=np.array([f.center[:] for f in prov.data.polygons if f.material_index==3]);cut_values=array_sample(clipped,ijk,vox,collar_pts);bpy.data.objects.remove(prov,do_unlink=True)
 grid.copyFromArray(result,tuple(int(i) for i in ijk),0.0);new=mesh_from_grid(grid,'C15 / single continuous local-volume reconstructed Miao');del grid;gc.collect();new.name=original.name+' C15'
 for f in new.data.polygons:f.use_smooth=True
 raw_topology=topo(new);cleanup=local_fragment_cleanup(new);final=topo(new);assert final['components']==1 and final['non_manifold_edges']==0,final
 res=residuals(baseline,new)
 # Actual mesh output is a full-body sparse iso-surface. All outside changes are
 # measured, not hidden behind an assertion that the original indices survived.
 for collection in original.users_collection:
  if new.name not in collection.objects:collection.objects.link(new)
 orig_name=original.name;bpy.data.objects.remove(original,do_unlink=True);new.name=orig_name
 for o in list(s.objects):
  if o.name.startswith('Miao / native short plush'):o.hide_render=True;o.hide_set(True);o['C15 binding status']='INVALID: full-body isosurface and local anatomy changed; UV/groom/shape bindings must be rebuilt'
 new['C15 pipeline']='actual mesh SDF + bounded smooth union local loft, no rigid collar/mesh-Laplacian';new['C15 old bindings']='INVALIDATED';new['C15 volume voxel']=vox
 # Temporary source colors on one connected complete-body mesh.
 palette=[(.4,.4,.4,1),(.4,.4,.4,1),(.4,.4,.4,1),(.4,.4,.4,1)]
 for i,col in enumerate(palette):
  m=bpy.data.materials.new('C15 gray / volume-source '+str(i));bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=col;bs.inputs['Roughness'].default_value=.65;new.data.materials.append(m)
 for f in new.data.polygons:
  q=np.array(f.center);p0=np.rint(q/vox-ijk).astype(int)
  if np.all(p0>=0) and np.all(p0<np.array(shape)):
   ix=tuple(p0);f.material_index=3 if blend_changed[ix] else int(contributor[ix])
  else:f.material_index=0
 # Whole output audit and restricted wrist surface audit (boundary expected from crop).
 roi_faces=[f for f in new.data.polygons if .70<f.center.x<1.74 and -1.44<f.center.y<-.10 and 1.30<f.center.z<2.34];ids=sorted({i for f in roi_faces for i in f.vertices});remap={i:j for j,i in enumerate(ids)};patch=mesh('C15 diagnostic / wrist audit patch',[new.data.vertices[i].co[:] for i in ids],[[remap[i] for i in f.vertices] for f in roi_faces]);patch_audit=A.audit(patch);(out/'wrist-audit.json').write_text(json.dumps(patch_audit,indent=2)+'\n');bpy.data.objects.remove(patch,do_unlink=True)
 bpy.data.objects.remove(hand,do_unlink=True);bpy.data.objects.remove(baseline,do_unlink=True)
 s.cycles.samples=a.samples;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
 report={'stage':'C15-local-volume-gray-candidate-unreviewed','input_sha256':source_sha,'input_C11_unchanged':sha(src)==source_sha,'C11_builder_source_sha256':c11sha,'C11_builder_source_unchanged':sha(c11source)==c11sha,'script_sha256':sha(__file__),'blender':bpy.app.version_string,'voxel':vox,'halfwidth_voxels':12,'dense_ROI':{'lo':lo.tolist(),'hi':hi.tolist(),'ijk':ijk.tolist(),'shape':shape,'one_float32_array_bytes':n*4,'conservative_peak_18_arrays_bytes':conservative_peak,'limit_bytes':1_000_000_000,'full_body_dense_array_used':False},'cut_old_wrist':{'type':'bounded elliptic cylinder subtraction from actual body SDF','center_xz':[1.205,1.80],'radii_xz':[.38,.40],'front_of_y':-.37,'actual_old_connector_face_samples':len(cut_values),'outside_clipped_body_fraction':float(np.mean(cut_values>0)),'minimum_clipped_field_at_old_connector':float(cut_values.min())},'bridge':{'type':'continuous implicit elliptical loft; capped ends inside original arm/palm','Y_stations':ys.tolist(),'center_z':czs.tolist(),'radius_x':rxs.tolist(),'radius_z':rzs.tolist(),'bounded_smooth_union_radius_max':.065,'radial_field_is_globally_exact_SDF':False,'not_Laplacian':True},'raw_isosurface_topology':raw_topology,'local_fragment_cleanup':cleanup,'full_body':final,'non_wrist_resample_residuals':res,'wrist_patch_audit':patch_audit,'old_bindings_valid':False,'limits':['Volume/voxel topology is not animation-ready retopology.','Entire body iso-surface was resampled; non-wrist/head residuals are measured, UV/groom/shape keys invalidated.','Contributor colors are authoring diagnostics on one connected model, not separate production arms.','Static character, contact and three nonbuilder reviews pending; no animation/engine/browser/deployment.']}
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-c15-volume-bridge.blend'),compress=True)
 cam=s.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();scale=cam.data.ortho_scale
 for view in ['front','three-quarter','grip-inside']:
  if view=='three-quarter':cam.location=(6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
  elif view=='grip-inside':cam.location=(4,-6,3);cam.rotation_euler=(Vector((1.17,-.95,1.96))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25;s.render.resolution_x=s.render.resolution_y=768
  s.render.filepath=str(out/('gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
 diagnostic_colors=[(.4,.4,.4,1),(.75,.18,.07,1),(.12,.27,.8,1),(.75,.15,.65,1)]
 for m,col in zip(new.data.materials,diagnostic_colors):m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=col
 s.render.filepath=str(out/'diagnostic-volume-source-inside.png');bpy.ops.render.render(write_still=True)
 for m in new.data.materials:m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.4,.4,.4,1)
 cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=scale
 report['seconds']=time.time()-started;(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+json.dumps({k:report[k] for k in ['stage','full_body','non_wrist_resample_residuals','dense_ROI','seconds']}))

if a.probe_only:probe()
else:candidate()
