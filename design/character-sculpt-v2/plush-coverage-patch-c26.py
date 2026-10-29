"""C26: fixed 16x central root-intensity forehead diagnostic, not art delivery.

Existing C24 strands stay byte-identical. New roots are sampled on actual body
triangles and encode their own guarded BindUV/barycentric binding. A deterministic
15x added-intensity proposal is thinned by the existing smooth boundary fade.
Native surface deformation and the existing C24 rotation asset remain in use.
No scan, light/shader/profile change, resnap, full-body proliferation or network.
"""
import argparse, ast, hashlib, importlib.util, json, math, sys, time, traceback
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'artifacts/character-plush-flow-c24/controlled-native-run/miao-c24-forehead-flow-patch.blend'
SOURCE_SHA='430b5a9be23c8806bc584df9c71e9d0a6d63a8dfbea95d2db27b4f3e13c0a875'
ROI=np.array([.375,.625,.588,.644])
SEED=26
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda a:hashlib.sha256(np.asarray(a).tobytes()).hexdigest()

def stats(v):
 v=np.asarray(v);return dict(count=int(v.size),min=float(v.min()),max=float(v.max()),mean=float(v.mean()),median=float(np.median(v)),p90=float(np.quantile(v,.9)))

def attr_array(a):
 types={'FLOAT_VECTOR':('vector',3,np.float32),'FLOAT2':('vector',2,np.float32),'FLOAT':('value',1,np.float32),'INT':('value',1,np.int32),'INT8':('value',1,np.int8),'BOOLEAN':('value',1,np.bool_)}
 field,dim,dtype=types[a.data_type];v=np.empty(len(a.data)*dim,dtype);a.data.foreach_get(field,v)
 return v.reshape(-1,dim) if dim>1 else v

def coords(ob,evaluated=False):
 o=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else ob
 if o.type=='CURVES':return attr_array(o.data.attributes['position']).copy()
 v=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',v);return v.reshape(-1,3)

def project(points,cam):
 dg=bpy.context.evaluated_depsgraph_get();vp=np.asarray(cam.calc_matrix_camera(dg,x=1024,y=1024)@cam.matrix_world.inverted())
 flat=np.asarray(points).reshape(-1,3);clip=np.c_[flat,np.ones(len(flat))]@vp.T
 return ((clip[:,:2]/clip[:,3:]+1)/2).reshape(*points.shape[:-1],2)

def fade(uv):
 d=np.minimum(uv-np.array([ROI[0],ROI[2]]),np.array([ROI[1],ROI[3]])-uv)/np.array([.025,.006])
 f=np.clip(d,0,1);return np.prod(f*f*(3-2*f),axis=-1)

def native_sample(body,hair):
 """Independent Blender Sample UV Surface validity and actual position lookup."""
 group=bpy.data.node_groups.new('C26 / temporary native UV checks','GeometryNodeTree')
 group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 n,l=group.nodes,group.links;ni=n.new('NodeGroupInput');no=n.new('NodeGroupOutput');info=n.new('GeometryNodeObjectInfo');info.inputs['Object'].default_value=body
 uv=n.new('GeometryNodeInputNamedAttribute');uv.data_type='FLOAT_VECTOR';uv.inputs['Name'].default_value='BindUV'
 ruv=n.new('GeometryNodeInputNamedAttribute');ruv.data_type='FLOAT_VECTOR';ruv.inputs['Name'].default_value='surface_uv_coordinate'
 p=n.new('GeometryNodeInputPosition');sample=n.new('GeometryNodeSampleUVSurface');sample.data_type='FLOAT_VECTOR'
 l.new(info.outputs['Geometry'],sample.inputs['Mesh']);l.new(uv.outputs['Attribute'],sample.inputs['Source UV Map']);l.new(ruv.outputs['Attribute'],sample.inputs['Sample UV']);l.new(p.outputs['Position'],sample.inputs['Value'])
 prev=ni.outputs['Geometry']
 for name,typ,socket in [('c26_valid','BOOLEAN','Is Valid'),('c26_bound_position','FLOAT_VECTOR','Value')]:
  st=n.new('GeometryNodeStoreNamedAttribute');st.domain='CURVE';st.data_type=typ;st.inputs['Name'].default_value=name;l.new(prev,st.inputs['Geometry']);l.new(sample.outputs[socket],st.inputs['Value']);prev=st.outputs['Geometry']
 l.new(prev,no.inputs['Geometry']);md=hair.modifiers.new('C26 / temporary independent UV query','NODES');md.node_group=group;bpy.context.view_layer.update()
 ev=hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
 valid=attr_array(ev.attributes['c26_valid']);pos=attr_array(ev.attributes['c26_bound_position'])
 hair.modifiers.remove(md);bpy.data.node_groups.remove(group);bpy.context.view_layer.update()
 return valid,pos

def main():
 pa=argparse.ArgumentParser();pa.add_argument('--out',default='artifacts/character-plush-coverage-c26/controlled-native-run');pa.add_argument('--render',action='store_true')
 args=pa.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True)
 assert not (out/'receipt.json').exists(),'Preserve previous run; choose fresh path'
 (out/'executed-script.py').write_bytes(Path(__file__).read_bytes())
 rec=dict(stage='C26-single-fixed-coverage-patch',status='started',source_sha256=sha(__file__),input_sha256=sha(SRC),seed=SEED,actual_render_calls=0)
 def save(status):
  rec['status']=status;(out/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print('C26_STAGE '+status,flush=True)
 try:
  assert sha(SRC)==SOURCE_SHA
  hp=ROOT/'design/character-sculpt-v2/eye-optics-diagnostic.py';sp=importlib.util.spec_from_file_location('miao_snapshots',hp);h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
  bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;hair=bpy.data.objects['Miao / native short plush'];body=bpy.data.objects['Miao / continuous pear and rounded-square face'];hc=hair.data;me=body.data
  assert np.array_equal(np.asarray(hair.matrix_world),np.eye(4)) and np.array_equal(np.asarray(body.matrix_world),np.eye(4))
  geom,lights,mats=h.geometry_hash(),h.light_snapshot(),h.material_snapshot()
  raw_attrs={a.name:(a.data_type,a.domain,attr_array(a)) for a in hc.attributes};original_eval=coords(hair,True).reshape(-1,4,3);N=len(hc.curves);assert N==180000
  eval_attrs={a.name:digest(attr_array(a)) for a in hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.attributes}
  assert hc.surface==body and hc.surface_uv_map=='BindUV'
  cam0=s.camera;cam=cam0.copy();cam.data=cam0.data.copy();s.collection.objects.link(cam)
  packet=json.loads((ROOT/'artifacts/character-head-c14-color/receipt.json').read_text());head=next(x for x in packet['renders'] if x['name']=='color-head-front');cam.matrix_world=Matrix(head['camera_matrix']);cam.data.type=head['type'];cam.data.lens=head['lens'];bpy.context.view_layer.update()
  eye=cam.matrix_world.translation.copy();dg=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(body,dg)
  screen=project(original_eval[:,0],cam);sel=np.flatnonzero((screen[:,0]>=ROI[0])&(screen[:,0]<=ROI[1])&(screen[:,1]>=ROI[2])&(screen[:,1]<=ROI[3]))
  def visible(p):
   hit=tree.ray_cast(eye,(Vector(p)-eye).normalized(),20)[0]
   return hit is not None and (hit-Vector(p)).length<1e-4
  parents=np.array([i for i in sel if visible(original_eval[i,0])],np.int32);assert len(parents)==549
  restco=coords(body);actual=coords(body,True);body_rest=attr_array(me.attributes['miao_rest_position']);me.calc_loop_triangles()
  tris=np.empty(len(me.loop_triangles)*3,np.int32);loops=np.empty_like(tris);me.loop_triangles.foreach_get('vertices',tris);me.loop_triangles.foreach_get('loops',loops);tris=tris.reshape(-1,3);loops=loops.reshape(-1,3)
  buv=np.empty(len(me.uv_layers['BindUV'].data)*2,np.float32);me.uv_layers['BindUV'].data.foreach_get('uv',buv);buv=buv.reshape(-1,2)
  vscreen=project(actual,cam);tuvscreen=vscreen[tris];lo=tuvscreen.min(axis=1);hi=tuvscreen.max(axis=1)
  candidates=np.flatnonzero((hi[:,0]>=ROI[0])&(lo[:,0]<=ROI[1])&(hi[:,1]>=ROI[2])&(lo[:,1]<=ROI[3]))
  at=actual[tris[candidates]].astype(float);area=np.linalg.norm(np.cross(at[:,1]-at[:,0],at[:,2]-at[:,0]),axis=1)/2;assert area.sum()>0
  # Fixed intensity from unchanged baseline's 549 visible roots. A single density,
  # not a sweep: 15 added roots for every baseline root before boundary thinning.
  target=15*len(parents);rng=np.random.default_rng(SEED);picks=[];barys=[];valid_proposals=0;tested=0
  while valid_proposals<target:
   batch=min(2048,(target-valid_proposals)*3);ix=rng.choice(candidates,size=batch,p=area/area.sum());r=rng.random((batch,2));sq=np.sqrt(r[:,0]);w=np.c_[1-sq,sq*(1-r[:,1]),sq*r[:,1]]
   # Exclude triangle edges before UV quantization, without repairing moved roots.
   interior=w.min(axis=1)>.02;ix,w=ix[interior],w[interior]
   points=np.einsum('ni,nij->nj',w,actual[tris[ix]].astype(float));uv=project(points,cam)
   inside=(uv[:,0]>=ROI[0])&(uv[:,0]<=ROI[1])&(uv[:,1]>=ROI[2])&(uv[:,1]<=ROI[3]);ix,w,points,uv=ix[inside],w[inside],points[inside],uv[inside]
   for ti,weights,P,U in zip(ix,w,points,uv):
    tested+=1
    if not visible(P):continue
    valid_proposals+=1
    if rng.random()<fade(U):picks.append(int(ti));barys.append(weights)
    if valid_proposals==target:break
   assert tested<100000,'Bounded root proposal budget exhausted'
  picks=np.asarray(picks,np.int32);barys=np.asarray(barys);K=len(picks);assert K>0
  # Store each new root's OWN triangle-derived UV, then decode its actual float32
  # representation before building raw/root/rest coordinates. No copied parent UV.
  tv=buv[loops[picks]].astype(float);newuv=np.einsum('ni,nij->nj',barys,tv).astype(np.float32)
  d1=tv[:,1]-tv[:,0];d2=tv[:,2]-tv[:,0];d=newuv.astype(float)-tv[:,0];den=d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0]
  b1=(d[:,0]*d2[:,1]-d[:,1]*d2[:,0])/den;b2=(d1[:,0]*d[:,1]-d1[:,1]*d[:,0])/den;barys=np.c_[1-b1-b2,b1,b2];assert barys.min()>=0
  root_raw=np.einsum('ni,nij->nj',barys,restco[tris[picks]].astype(float));root_actual=np.einsum('ni,nij->nj',barys,actual[tris[picks]].astype(float));root_pigment=np.einsum('ni,nij->nj',barys,body_rest[tris[picks]].astype(float))
  # Nearest EXISTING guide provides only shape/length/profile, never its UV or
  # pigment root. Translating its raw offsets preserves its exact short profile.
  nearest=np.empty(K,np.int32)
  for j in range(0,K,512):
   ds=((root_actual[j:j+512,None,:]-original_eval[parents,0][None,:,:])**2).sum(axis=2);nearest[j:j+512]=parents[np.argmin(ds,axis=1)]
  sourcepos=raw_attrs['position'][2].reshape(N,4,3);offs=sourcepos[nearest].astype(float)-sourcepos[nearest,0,None,:]
  newpos=(root_raw[:,None,:]+offs).astype(np.float32)
  source_rest=raw_attrs['miao_rest_position'][2].reshape(N,4,3);restoffs=source_rest[nearest].astype(float)-source_rest[nearest,0,None,:]
  newrest=(root_pigment[:,None,:]+restoffs).astype(np.float32)
  normals=np.cross(actual[tris[picks,1]]-actual[tris[picks,0]],actual[tris[picks,2]]-actual[tris[picks,0]]);normals/=np.linalg.norm(normals,axis=1)[:,None]
  tangent=np.array([1.,0.,0.])-normals[:,0,None]*normals;tangent/=np.linalg.norm(tangent,axis=1)[:,None];axes=np.cross(normals,tangent);axes/=np.linalg.norm(axes,axis=1)[:,None]
  child_uv=project(root_actual,cam);angles=(math.pi/4*fade(child_uv)).astype(np.float32)
  hc.add_curves([4]*K)
  replacements={'position':newpos.reshape(-1,3),'radius':raw_attrs['radius'][2].reshape(N,4)[nearest].reshape(-1),'miao_rest_position':newrest.reshape(-1,3),'surface_uv_coordinate':newuv,'c24_flow_axis':axes.astype(np.float32),'c24_flow_angle':angles}
  for name,(typ,domain,old) in raw_attrs.items():
   assert name in replacements,'Unaccounted source attribute';a=hc.attributes[name];new=replacements[name];full=np.concatenate([old,new]);a.data.foreach_set('vector' if typ in {'FLOAT_VECTOR','FLOAT2'} else 'value',full.ravel())
  hc.update_tag();hair.update_tag();bpy.context.view_layer.update()
  for name,(typ,domain,old) in raw_attrs.items():assert np.array_equal(attr_array(hc.attributes[name])[:len(old)],old),'Original attribute changed'
  ev=hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data;after=coords(hair,True).reshape(-1,4,3)
  original_error=np.linalg.norm(after[:N]-original_eval,axis=2);assert original_error.max()<1e-7
  for name,oldhash in eval_attrs.items():assert digest(attr_array(ev.attributes[name])[:N*4 if ev.attributes[name].domain=='POINT' else N])==oldhash,'Original evaluated attribute changed'
  actual_root_error=np.linalg.norm(after[N:,0]-root_actual,axis=1);assert actual_root_error.max()<1e-4
  valid,lookup=native_sample(body,hair);assert len(valid)==N+K and valid.all(),'Native UV validity failed'
  lookup_error=np.linalg.norm(lookup[N:]-root_actual,axis=1);assert lookup_error.max()<1e-4
  root_to_native=np.linalg.norm(after[N:,0]-lookup[N:],axis=1);assert root_to_native.max()<1e-4
  rawlen=np.linalg.norm(np.diff(sourcepos[nearest],axis=1),axis=2).sum(axis=1);newlen=np.linalg.norm(np.diff(newpos,axis=1),axis=2).sum(axis=1);assert np.max(np.abs(newlen-rawlen)/rawlen)<5e-4
  before_len=np.linalg.norm(np.diff(original_eval[nearest],axis=1),axis=2).sum(axis=1);after_len=np.linalg.norm(np.diff(after[N:],axis=1),axis=2).sum(axis=1)
  evaluated_length_error=np.abs(after_len-before_len)/before_len
  assert evaluated_length_error.max()<.01,'Native guide transfer changes evaluated strand length >1%'
  # Actual evaluated clearance and complete segment/eye intersections, not just tips.
  eyes=[(o,BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get()),o.matrix_world.inverted()) for o in s.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('C6 / sclera','C6 / iris','C7 / clear cornea'))]
  gaps=[];eye_hits=[]
  for i,curve in enumerate(after[N:]):
   for j in range(3):
    A,B=Vector(curve[j]),Vector(curve[j+1])
    for t in [.25,.5,.75,1.]:
     P=A.lerp(B,t);hit,n,face,d=tree.find_nearest(P);assert hit is not None;gap=(P-hit).dot(n);gaps.append(gap)
     assert gap>=-1e-5,'Child enters skin'
    for ob,et,iv in eyes:
     a0,b0=iv@A,iv@B;D=b0-a0
     if D.length and et.ray_cast(a0,D.normalized(),D.length)[0] is not None:eye_hits.append([i,j,ob.name])
  assert not eye_hits
  assert h.geometry_hash()==geom and h.light_snapshot()==lights and h.material_snapshot()==mats and sha(SRC)==SOURCE_SHA
  bpy.data.objects.remove(cam,do_unlink=True);s.camera=cam0
  rec.update(blender=bpy.app.version_string,proposal=dict(central_total_density_factor=16,extra_intensity_factor=15,visible_source_roots=len(parents),uniform_visible_proposals=valid_proposals,accepted_after_smooth_boundary_fade=K,tested_visibility_candidates=tested,root_roi=ROI.tolist(),fade_x=.025,fade_y=.006,seed=SEED),binding=dict(method='actual evaluated body triangle; same-index original/rest triangle; own barycentric BindUV quantization decoded before geometry construction',new_root_uv_sha256=digest(newuv),sampled_triangle_sha256=digest(picks),barycentric_sha256=digest(barys),body_rest_root_sha256=digest(root_pigment.astype(np.float32)),minimum_barycentric=float(barys.min()),native_valid_curves=int(valid.sum()),native_invalid_curves=int((~valid).sum()),native_lookup_error=stats(lookup_error),actual_evaluated_root_error=stats(actual_root_error),root_to_native_lookup_error=stats(root_to_native)),geometry_checks=dict(curves_before=N,curves_after=N+K,points_after=int(after.size/3),all_original_raw_attributes_bit_exact=True,all_original_evaluated_attributes_bit_exact=True,original_evaluated_position_error=stats(original_error),length_profile_raw_relative_error=stats(np.abs(newlen-rawlen)/rawlen),length_profile_evaluated_relative_error=stats(evaluated_length_error),radii_profile_exact=True,minimum_actual_skin_clearance=float(min(gaps)),clearance_samples=len(gaps),eye_segment_hits=eye_hits),body_material_lights_and_original_source_unchanged=True,limits=['One forehead patch only; 16x is central proposal intensity, smooth boundary thinning lowers aggregate added count.','Template offsets/short profile copied locally, each new root UV/rest pigment derived from its own actual surface triangle.','Coverage AOV is an antialiased hair response estimate, not a promised 7% outcome or a quality score.','Technical diagnosis only; no character/plush pass, full-frame art delivery, motion, Web, fees or deployment.'])
  np.savez_compressed(out/'new-root-binding.npz',triangle=picks,barycentric=barys,uv=newuv,raw_root=root_raw,actual_root=root_actual,pigment_root=root_pigment,parent_shape_only=nearest)
  save('root-attribute-and-clearance-invariants-passed-before-render')
  bpy.context.preferences.filepaths.save_version=0;native=out/'miao-c26-forehead-coverage-patch.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);rec['native_sha256']=sha(native)
  # Reopen saved file before handoff to demonstrate persistence of the actual groom.
  bpy.ops.wm.open_mainfile(filepath=str(native));rh=bpy.data.objects['Miao / native short plush'];assert len(rh.data.curves)==N+K
  assert digest(coords(rh,True))==digest(after.reshape(-1,3));rec['native_reopen_evaluated_geometry_exact']=True
  renderer=ROOT/'design/character-sculpt-v2/plush-denoise-diagnostic.py';text=renderer.read_text();old='artifacts/character-plush-short-fiber-c21-r2/miao-fiber-scattering-candidate.blend';assert text.count(old)==1;text=text.replace(old,str(native.relative_to(ROOT)));text=text.replace('ROOT = Path(__file__).resolve().parents[2]',"ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'public/sampled-audio.js').is_file())");render_script=out/'samebuffer-render.py';render_script.write_text(text);rec['renderer_sha256']=sha(render_script);save('native-saved-reopened-verified-awaiting-serialized-render')
  if args.render:
   namespace={'__file__':str(render_script),'__name__':'c26_samebuffer_reuse'};exec(compile(text,str(render_script),'exec'),namespace);saved=sys.argv[:];sys.argv=[str(render_script),'--','--out',str(out/'render'),'--samples','128','--coverage']
   try:namespace['main']()
   finally:sys.argv=saved
   rec['actual_render_calls']=1;rec['render_receipt_sha256']=sha(out/'render/receipt.json');save('one-crop-rendered-awaiting-image-inspection-and-independent-reviews')
  print('RESULT '+json.dumps(rec),flush=True)
 except Exception as ex:
  rec.update(error=repr(ex),traceback=traceback.format_exc());save('stopped-before-further-work');raise

if __name__=='__main__':main()
