"""C16 local volume route, zero-fee Blender-bundled OpenVDB.
First prove closed actual-mesh -> SDF -> bounded ndarray -> quads.
Candidate stages are intentionally separate from API preflight.
"""
import bpy,bmesh,numpy as np,math,sys,json,hashlib,time,argparse,gc
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import openvdb as vdb
p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/character-paw-c16');p.add_argument('--probe-only',action='store_true');p.add_argument('--sections-only',action='store_true');p.add_argument('--voxel',type=float,default=.006);p.add_argument('--samples',type=int,default=32);p.add_argument('--size',type=int,default=1024);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
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
hand_code=hand_code.replace("'C11 / reference palm and curled short toes'","'C16 / closed C11 round palm and curled toes'")
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
 result=vdb.FloatGrid(.08);result.transform=grid.transform;result.copyFromArray(data,ijk,0.0);o=mesh_from_grid(result,'C16 / bounded actual mesh SDF preflight');stats=topo(o);assert stats['components']==1 and stats['non_manifold_edges']==0
 bounds=np.array([v.co[:] for v in o.data.vertices]);report={'stage':'API-small-actual-mesh-preflight','blender':bpy.app.version_string,'module':vdb.__file__,'input':'closed cube 8 vertices / 6 authored quad faces','apis_executed':['FloatGrid.createLevelSetFromPolygons(points=float32,quads=uint32,transform=createLinearTransform(.005),halfWidth=8.)','grid.copyToArray(float32[65,65,65],ijk=(-32,-32,-32))','FloatGrid(.08).copyFromArray(data,ijk,tolerance=0.0)','FloatGrid.convertToQuads(0.0)'],'array_shape':shape,'dense_array_bytes':int(data.nbytes),'center_sdf':float(data[32,32,32]),'outside_sdf':float(data[0,0,0]),'output':stats,'bounds_min':bounds.min(0).tolist(),'bounds_max':bounds.max(0).tolist(),'seconds':time.time()-started,'verdict':'API and closed-mesh occupancy roundtrip work; no character/craft/contact acceptance'};(out/'small-mesh-preflight.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+json.dumps(report))

def array_sample(D,ijk,voxel,points):
 p=np.asarray(points,dtype=float)/voxel-np.asarray(ijk);i=np.clip(np.floor(p).astype(int),0,np.array(D.shape)-2);t=np.clip(p-i,0,1);v=np.zeros(len(p),np.float64)
 for x in [0,1]:
  for y in [0,1]:
   for z in [0,1]:v+=(t[:,0] if x else 1-t[:,0])*(t[:,1] if y else 1-t[:,1])*(t[:,2] if z else 1-t[:,2])*D[i[:,0]+x,i[:,1]+y,i[:,2]+z]
 return v

def residuals(before,after):
 dg=bpy.context.evaluated_depsgraph_get();bh=BVHTree.FromObject(after,dg);co=np.array([v.co[:] for v in before.data.vertices]);outside=~((co[:,0]>.80)&(co[:,0]<1.64)&(co[:,1]<-.74)&(co[:,2]>1.35)&(co[:,2]<2.32));head=(np.abs(co[:,0])<.80)&(co[:,2]>2.25);front_head_y=float(np.quantile(co[head,1],.20));eye=head&(co[:,1]<=front_head_y)
 report={'front_head_region_definition':{'abs_x_max':.80,'z_min':2.25,'y_max_actual_front_20pct_quantile':front_head_y}}
 for name,mask in [('non_wrist',outside),('front_head_eye_surround',eye),('preserved_C8_forearm',(co[:,0]>.7)&(co[:,1]>-.78)&(co[:,1]<-.20)&(co[:,2]>1.40)&(co[:,2]<2.30))]:
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
   coords=np.array([q.co[:] for q in vs]);faces={f for q in vs for f in q.link_faces};cen=coords.mean(0);volume=sum(float(np.cross(np.array(f.verts[0].co)-cen,np.array(f.verts[j].co)-cen).dot(np.array(f.verts[j+1].co)-cen))/6 for f in faces for j in range(1,len(f.verts)-1));lo=coords.min(0);hi=coords.max(0);inside=bool(np.all(lo>np.array([.80,-1.44,1.35])) and np.all(hi<np.array([1.64,-.70,2.32])))
   row={'vertices':len(vs),'faces':len(faces),'bounds_min':lo.tolist(),'bounds_max':hi.tolist(),'signed_volume':volume,'entirely_within_wrist_ROI':inside,'aabb_volume_upper_bound':float(np.prod(hi-lo)),'deleted':inside and float(np.prod(hi-lo))<.001}
   parts.append(row)
   if row['deleted']:delete.extend(vs)
  else:parts.append({'vertices':len(vs),'deleted':False,'main':True})
 (out/'component-cleanup.json').write_text(json.dumps(parts,indent=2)+'\n')
 assert all(p.get('main') or p['deleted'] for p in parts),{'unacceptable_nonlocal_or_large_fragment':parts}
 if delete:bmesh.ops.delete(bm,geom=delete,context='VERTS');bm.to_mesh(o.data);o.data.update()
 bm.free();return parts

def candidate():
 started=time.time();src,original=prepare_source();source_sha=sha(src);s=bpy.context.scene;bpy.context.view_layer.update();section_rows=source_sections(original)
 # Real C11 full-body mesh, not an SDF primitive replacement of the cat.
 baseline=original.copy();baseline.data=original.data.copy();baseline.name='C16 diagnostic / unchanged C11 baseline';s.collection.objects.link(baseline);baseline.hide_render=True;baseline.hide_set(True)
 hand,hand_design=make_hand();hand.name='C16 diagnostic / closed full reference palm';hand.hide_render=True
 vox=a.voxel;transform=vdb.createLinearTransform(vox);grid=sdf_from_mesh(original,vox,12);pgrid=sdf_from_mesh(hand,vox,12)
 lo=np.array([.80,-1.44,1.35]);hi=np.array([1.64,-.70,2.32]);ijk=np.floor(lo/vox).astype(int);maxijk=np.ceil(hi/vox).astype(int);shape=tuple(int(i) for i in maxijk-ijk+1);n=int(np.prod(shape));conservative_peak=n*4*18
 assert conservative_peak<1_000_000_000,{'dense_peak_estimate':conservative_peak,'shape':shape}
 D=np.empty(shape,np.float32);P=np.empty(shape,np.float32);grid.copyToArray(D,tuple(int(i) for i in ijk));pgrid.copyToArray(P,tuple(int(i) for i in ijk));del pgrid;gc.collect()
 axes=[(ijk[j]+np.arange(shape[j],dtype=np.float32))*vox for j in range(3)];X=axes[0][:,None,None];Y=axes[1][None,:,None];Z=axes[2][None,None,:]
 # Strictly distal hand-only removal. The real C8 Y=-.83 section has one
 # closed forearm loop inside this box; no flank loop or shoulder is cut.
 cut=np.maximum(np.maximum(np.abs(X-1.21)-.35,np.abs(Z-1.85)-.45),Y+.83)
 cut=np.broadcast_to(cut,shape);clipped=np.maximum(D,-cut)
 # No arbitrary fixed-X/radius loft: morph actual source cross-section fields.
 # Forearm endpoint is actual C8 SDF at Y nearest -.80. Palm endpoint is actual
 # closed C11 mesh section near -1.06, limited to lower palm-root Z<1.90.
 fidx=int(np.argmin(np.abs(axes[1]+.80)));pidx=int(np.argmin(np.abs(axes[1]+1.06)));forearm_y=float(axes[1][fidx]);palm_y=float(axes[1][pidx]);Ff=D[:,fidx,:].copy();Fp=np.maximum(P[:,pidx,:],axes[2][None,:]-1.90)
 t=sm((Y-palm_y)/(forearm_y-palm_y));morph=(1-t)*Fp[:,None,:]+t*Ff[:,None,:];loft=np.maximum(morph,np.maximum(-1.08-Y,Y+.78));del morph
 K=.040*sm((Y+1.13)/.08)*(1-sm((Y+.80)/.06))*sm((1.99-Z)/.12)
 K=np.broadcast_to(K,shape);preserved=np.minimum(clipped,P)
 # R2: replace the lower-root shape between actual 3D fields; do not add a
 # third closed volume behind the already closed palm. Source derivative and
 # original shoulder/elbow are restored at the back end by smooth weights.
 arm_weight=sm((Y+1.13)/.35);root_weight=sm((2.02-Z)/.12);transition=(1-arm_weight)*P+arm_weight*D
 result=((1-root_weight)*preserved+root_weight*transition).astype(np.float32)
 # Source identity diagnostic: nearest contributing scalar field, plus blend zone.
 # This describes volume contributors, not disconnected production components.
 contributor=np.where(P<clipped,1,0).astype(np.int8);contributor=np.where(root_weight>.5,np.where(arm_weight>.5,0,1),contributor).astype(np.int8);blend_changed=np.broadcast_to((root_weight>.001)&(arm_weight>.02)&(arm_weight<.98),shape)
 # Evaluate actual distal source-skin points, not a guessed anatomy label.
 source_co=np.array([v.co[:] for v in original.data.vertices]);old_distal=(source_co[:,0]>.86)&(source_co[:,0]<1.56)&(source_co[:,1]<-.84)&(source_co[:,2]>1.40)&(source_co[:,2]<2.30);distal_pts=source_co[old_distal][::10];cut_values=array_sample(clipped,ijk,vox,distal_pts)
 behind_pts=source_co[(source_co[:,0]>.8)&(source_co[:,0]<1.64)&(source_co[:,1]>-.80)&(source_co[:,1]<-.72)&(source_co[:,2]>1.35)&(source_co[:,2]<2.32)][::10];behind_delta=array_sample(clipped,ijk,vox,behind_pts)-array_sample(D,ijk,vox,behind_pts)
 grid.copyFromArray(result,tuple(int(i) for i in ijk),0.0);new=mesh_from_grid(grid,'C16 / single continuous local-volume reconstructed Miao');del grid;gc.collect();new.name=original.name+' C16'
 for f in new.data.polygons:f.use_smooth=True
 raw_topology=topo(new);cleanup=local_fragment_cleanup(new);final=topo(new);assert final['components']==1 and final['non_manifold_edges']==0,final
 res=residuals(baseline,new)
 # Actual mesh output is a full-body sparse iso-surface. All outside changes are
 # measured, not hidden behind an assertion that the original indices survived.
 for collection in original.users_collection:
  if new.name not in collection.objects:collection.objects.link(new)
 orig_name=original.name;bpy.data.objects.remove(original,do_unlink=True);new.name=orig_name
 for o in list(s.objects):
  if o.name.startswith('Miao / native short plush'):o.hide_render=True;o.hide_set(True);o['C16 binding status']='INVALID: full-body isosurface and local anatomy changed; UV/groom/shape bindings must be rebuilt'
 new['C16 pipeline']='R2 bounded lower-root shape replacement using full actual C8 and C11 mesh SDFs; no additive wrist volume';new['C16 old bindings']='INVALIDATED';new['C16 volume voxel']=vox
 # Temporary source colors on one connected complete-body mesh.
 palette=[(.4,.4,.4,1),(.4,.4,.4,1),(.4,.4,.4,1),(.4,.4,.4,1)]
 for i,col in enumerate(palette):
  m=bpy.data.materials.new('C16 gray / volume-source '+str(i));bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=col;bs.inputs['Roughness'].default_value=.65;new.data.materials.append(m)
 for f in new.data.polygons:
  q=np.array(f.center);p0=np.rint(q/vox-ijk).astype(int)
  if np.all(p0>=0) and np.all(p0<np.array(shape)):
   ix=tuple(p0);f.material_index=3 if blend_changed[ix] else int(contributor[ix])
  else:f.material_index=0
 # Whole output audit and restricted wrist surface audit (boundary expected from crop).
 roi_faces=[f for f in new.data.polygons if .80<f.center.x<1.64 and -1.44<f.center.y<-.70 and 1.35<f.center.z<2.32];ids=sorted({i for f in roi_faces for i in f.vertices});remap={i:j for j,i in enumerate(ids)};patch=mesh('C16 diagnostic / wrist audit patch',[new.data.vertices[i].co[:] for i in ids],[[remap[i] for i in f.vertices] for f in roi_faces]);patch_audit=A.audit(patch);(out/'wrist-audit.json').write_text(json.dumps(patch_audit,indent=2)+'\n');bpy.data.objects.remove(patch,do_unlink=True)
 bpy.data.objects.remove(hand,do_unlink=True);bpy.data.objects.remove(baseline,do_unlink=True)
 mats={}
 for key,value in [('body',.4),('white',.72),('dark',.045),('wood',.30)]:
  m=bpy.data.materials.new('C16 gray '+key);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(value,value,value,1);bs.inputs['Roughness'].default_value=.65;mats[key]=m
 for ob in list(s.objects):
  if ob==new or ob.type not in {'MESH','CURVES','CURVE'} or ob.hide_render or ob.name.startswith(('Studio /','Authoring /','D0 /','C7 / clear')):continue
  key='white' if ob.name.startswith('C6 / sclera') else 'dark' if ob.name.startswith(('C6 / iris','Face /')) else 'wood' if ob.name.startswith('Guitar /') else 'body';ob.data.materials.clear();ob.data.materials.append(mats[key])
 s.cycles.samples=a.samples;
 s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
 report={'stage':'C16-local-volume-gray-candidate-unreviewed','input_sha256':source_sha,'input_C8_unchanged':sha(src)==source_sha,'C11_builder_source_sha256':c11sha,'C11_builder_source_unchanged':sha(c11source)==c11sha,'script_sha256':sha(__file__),'blender':bpy.app.version_string,'voxel':vox,'halfwidth_voxels':12,'dense_ROI':{'lo':lo.tolist(),'hi':hi.tolist(),'ijk':ijk.tolist(),'shape':shape,'one_float32_array_bytes':n*4,'conservative_peak_18_arrays_bytes':conservative_peak,'limit_bytes':1_000_000_000,'full_body_dense_array_used':False},'cut_old_wrist':{'type':'distal-only actual C8 mesh field subtraction','x_range':[.86,1.56],'z_range':[1.40,2.30],'front_of_y':-.83,'actual_distal_surface_samples':len(cut_values),'outside_clipped_body_fraction':float(np.mean(cut_values>0)),'minimum_clipped_field':float(cut_values.min()),'max_clipping_field_change_on_source_skin_behind_minus_80':float(np.max(np.abs(behind_delta)))},'bridge':{'type':'R2 bounded lower-palm shape replacement between full actual C8 3D SDF and closed C11 palm 3D SDF; no third additive wrist volume','source_forearm_section_y':forearm_y,'source_palm_section_y':palm_y,'replacement_y_range':[-1.13,-.78],'palm_root_z_cap':1.90,'no_guessed_fixed_X_or_radius':True,'third_volume_union_used_in_R2':False,'root_weight_z_full_below':1.90,'root_weight_zero_above':2.02,'original_C8_full_field_behind_minus78':True,'globally_exact_SDF_after_morph':False,'not_Laplacian':True},'raw_isosurface_topology':raw_topology,'local_fragment_cleanup':cleanup,'full_body':final,'non_wrist_resample_residuals':res,'wrist_patch_audit':patch_audit,'old_bindings_valid':False,'limits':['Volume/voxel topology is not animation-ready retopology.','Entire body iso-surface was resampled; non-wrist/head residuals are measured, UV/groom/shape keys invalidated.','Contributor colors are authoring diagnostics on one connected model, not separate production arms.','Static character, contact and three nonbuilder reviews pending; no animation/engine/browser/deployment.']}
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-c16-distal-wrist.blend'),compress=True)
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

def source_sections(o):
 co=np.array([v.co[:] for v in o.data.vertices]);o.data.calc_loop_triangles();tri=np.array([t.vertices[:] for t in o.data.loop_triangles]);results=[]
 for y in [-.72,-.78,-.80,-.83,-.86,-.90,-.96]:
  tco=co[tri];mask=(tco[:,:,1].min(1)<y)&(tco[:,:,1].max(1)>y)&(tco[:,:,0].mean(1)>.70)&(tco[:,:,2].mean(1)>1.3)&(tco[:,:,2].mean(1)<2.35);segments=[]
  for pts in tco[mask]:
   hits=[]
   for p,q in zip(pts,np.roll(pts,-1,axis=0)):
    if (p[1]-y)*(q[1]-y)<0:hits.append(p+(q-p)*(y-p[1])/(q[1]-p[1]))
   if len(hits)==2:segments.append([hits[0].tolist(),hits[1].tolist()])
  pts=np.array([p for line in segments for p in line]);results.append({'world_y':y,'segments':segments,'bbox_min':pts.min(0).tolist() if len(pts) else None,'bbox_max':pts.max(0).tolist() if len(pts) else None,'point_mean':pts.mean(0).tolist() if len(pts) else None})
 (out/'C8-actual-sections.json').write_text(json.dumps(results,indent=2)+'\n')
 # SVG contains world X/Z true intersections, no guessed forearm circle.
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><rect width="1600" height="900" fill="white"/>']
 for j,row in enumerate(results):
  ox=(j%4)*400;oy=(j//4)*440;svg.append(f'<text x="{ox+20}" y="{oy+30}" font-size="22">C8 Y={row["world_y"]:.2f}</text>')
  for p,q in row['segments']:
   svg.append(f'<path d="M{ox+20+(p[0]-.7)*330:.2f},{oy+420-(p[2]-1.3)*330:.2f}L{ox+20+(q[0]-.7)*330:.2f},{oy+420-(q[2]-1.3)*330:.2f}" stroke="#597bbe" fill="none" stroke-width="1.5"/>')
 svg.append('</svg>');(out/'C8-actual-sections.svg').write_text(''.join(svg));return results

def prepare_source():
 src=root/'artifacts/character-fidelity-c8-r2-color/miao-c8-reference-hold.blend';bpy.ops.wm.open_mainfile(filepath=str(src));o=bpy.data.objects['Miao / continuous pear and rounded-square face'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();baked=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);o.data=baked
 for mod in list(o.modifiers):o.modifiers.remove(mod)
 return src,o

if a.sections_only:
 src,o=prepare_source();sections=source_sections(o);print('RESULT '+json.dumps([{k:v for k,v in r.items() if k!='segments'} for r in sections]))
elif a.probe_only:probe()
else:candidate()
