"""C28 single length-variable diagnostic: same C26 roots/profile, 2.5x at center.

Real root-pivot native Geometry Nodes scaling AFTER existing surface-deform and
C24 rotation nodes. No density/angle/radius/shader changes or parameter scan.
"""
import argparse,hashlib,importlib.util,json,math,sys,time,traceback
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/character-plush-coverage-c26/controlled-native-run/miao-c26-forehead-coverage-patch.blend'
SOURCE_SHA='4174110cea7294427973b7516f04cdc1da64ab5e1e8179c28611b61b32842a92'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda a:hashlib.sha256(np.asarray(a).tobytes()).hexdigest()

def load_module(path,name):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def add_native_root_scale(hair):
 """Per-point native root lookup, no baked current-pose root coordinates."""
 ng=bpy.data.node_groups.new('C28 / actual evaluated root-pivot length','GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n,l=ng.nodes,ng.links
 ni=n.new('NodeGroupInput');no=n.new('NodeGroupOutput');idx=n.new('GeometryNodeInputIndex');point=n.new('GeometryNodeCurveOfPoint');l.new(idx.outputs['Index'],point.inputs['Point Index'])
 sub=n.new('ShaderNodeMath');sub.operation='SUBTRACT';l.new(idx.outputs['Index'],sub.inputs[0]);l.new(point.outputs['Index in Curve'],sub.inputs[1])
 pos=n.new('GeometryNodeInputPosition');sample=n.new('GeometryNodeSampleIndex');sample.domain='POINT';sample.data_type='FLOAT_VECTOR';sample.clamp=False;l.new(ni.outputs['Geometry'],sample.inputs['Geometry']);l.new(pos.outputs['Position'],sample.inputs['Value']);l.new(sub.outputs['Value'],sample.inputs['Index'])
 diff=n.new('ShaderNodeVectorMath');diff.operation='SUBTRACT';l.new(pos.outputs['Position'],diff.inputs[0]);l.new(sample.outputs['Value'],diff.inputs[1])
 named=n.new('GeometryNodeInputNamedAttribute');named.data_type='FLOAT';named.inputs['Name'].default_value='c28_length_scale'
 minus=n.new('ShaderNodeMath');minus.operation='SUBTRACT';l.new(named.outputs['Attribute'],minus.inputs[0]);minus.inputs[1].default_value=1
 mul=n.new('ShaderNodeVectorMath');mul.operation='SCALE';l.new(diff.outputs['Vector'],mul.inputs[0]);l.new(minus.outputs['Value'],mul.inputs['Scale'])
 setter=n.new('GeometryNodeSetPosition');l.new(ni.outputs['Geometry'],setter.inputs['Geometry']);l.new(mul.outputs['Vector'],setter.inputs['Offset']);l.new(setter.outputs['Geometry'],no.inputs['Geometry']);assert all(x.is_valid for x in l)
 md=hair.modifiers.new('C28 / same-root length after native groom','NODES');md.node_group=ng;return md

def main():
 pa=argparse.ArgumentParser();pa.add_argument('--out',default='artifacts/character-plush-readable-c28/controlled-native-run');pa.add_argument('--render',action='store_true');a=pa.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True);assert not (out/'receipt.json').exists(),'Preserve prior run'
 (out/'executed-script.py').write_bytes(Path(__file__).read_bytes());r=dict(stage='C28-single-root-pivot-length-diagnostic',status='started',source_sha256=sha(__file__),input_sha256=sha(SOURCE),render_calls=0)
 def save(status):
  r['status']=status;(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('C28_STAGE '+status,flush=True)
 try:
  assert sha(SOURCE)==SOURCE_SHA
  H=load_module(ROOT/'design/character-sculpt-v2/plush-coverage-patch-c26.py','c26_readonly_helpers');S=load_module(ROOT/'design/character-sculpt-v2/eye-optics-diagnostic.py','miao_snapshots')
  bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;hair=bpy.data.objects['Miao / native short plush'];body=bpy.data.objects['Miao / continuous pear and rounded-square face'];hc=hair.data
  assert len(hc.curves)==186125 and len(hc.position_data)==744500
  geom,lights,mats=S.geometry_hash(),S.light_snapshot(),S.material_snapshot();bodyeval_hash=digest(H.coords(body,True))
  raw={at.name:(at.data_type,at.domain,H.attr_array(at).copy()) for at in hc.attributes}
  ev=hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data;meta={at.name:(at.data_type,at.domain,H.attr_array(at).copy()) for at in ev.attributes if at.name!='position'}
  before=H.coords(hair,True).reshape(-1,4,3);sourcepos=raw['position'][2].reshape(-1,4,3)
  # Exact disjoint cohorts, identified by the persisted original C24 angle mask
  # and the C26 append boundary. Never select all 180k original strands.
  angles=raw['c24_flow_angle'][2];oldpatch=np.flatnonzero(angles[:180000]>0);children=np.arange(180000,186125,dtype=np.int32)
  assert len(oldpatch)==549 and len(children)==6125 and np.all(angles[children]>0)
  patch=np.r_[oldpatch,children];outside=np.ones(len(sourcepos),bool);outside[patch]=False
  weights=np.zeros(len(sourcepos),np.float64);weights[patch]=np.clip(angles[patch].astype(float)/(math.pi/4),0,1)
  scales=1+1.5*weights
  # The official C24 angle field is FLOAT; values near pi/4 are not exact pi/4.
  # Treat its documented fully-interior plateau as precisely 1, not a new fade.
  weights[np.abs(weights-1)<1e-6]=1;scales=1+1.5*weights
  assert scales.min()==1 and scales.max()==2.5 and np.count_nonzero(scales>1)==6674
  # The actual original guide coordinates and all source attributes remain
  # untouched. The native modifier obtains each evaluated curve's own root.
  at=hc.attributes.new('c28_length_scale','FLOAT','CURVE');at.data.foreach_set('value',np.ones(len(sourcepos),np.float32));md=add_native_root_scale(hair)
  hc.update_tag();hair.update_tag();bpy.context.view_layer.update()
  control=H.coords(hair,True).reshape(-1,4,3);assert np.array_equal(control,before),'Zero-length-change altered evaluated geometry'
  r['zero_change_control']=dict(raw_position_bit_exact=True,evaluated_position_bit_exact=True,root_count=len(sourcepos),curves=len(hc.curves),points=len(hc.position_data))
  for name,(typ,dom,x) in raw.items():assert np.array_equal(H.attr_array(hc.attributes[name]),x)
  for name,(typ,dom,x) in meta.items():assert np.array_equal(H.attr_array(hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.attributes[name]),x)
  save('zero-length-change-control-passed')
  at=hc.attributes['c28_length_scale'];at.data.foreach_set('value',scales.astype(np.float32));hc.update_tag();hair.update_tag();bpy.context.view_layer.update()
  after=H.coords(hair,True).reshape(-1,4,3);ev=hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
  assert after.shape==before.shape and len(ev.curves)==len(sourcepos)
  for name,(typ,dom,x) in raw.items():
   assert np.array_equal(H.attr_array(hc.attributes[name]),x),'Original raw source attribute changed'
  for name,(typ,dom,x) in meta.items():assert np.array_equal(H.attr_array(ev.attributes[name]),x),'Evaluated metadata/radius changed'
  root_error=np.linalg.norm(after[:,0]-before[:,0],axis=1);assert root_error.max()<1e-7
  outside_error=np.linalg.norm(after[outside]-before[outside],axis=2);assert outside_error.max()<1e-7
  expected=before[:,0,None,:].astype(float)+(before.astype(float)-before[:,0,None,:])*scales[:,None,None]
  residual=np.linalg.norm(after-expected,axis=2);assert residual.max()<1e-6,'Not actual evaluated root-pivot scaling'
  len0=np.linalg.norm(np.diff(before.astype(float),axis=1),axis=2).sum(axis=1);len1=np.linalg.norm(np.diff(after.astype(float),axis=1),axis=2).sum(axis=1)
  length_error=np.abs(len1/len0-scales);assert length_error.max()<5e-4
  # Check actual evaluated geometry against body and eyes, including full segment
  # rays plus interior samples. Longer strands may fail; do not hide a failure.
  dg=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(body,dg);gaps=[];bodyhits=[];eyehits=[]
  eyes=[(ob,BVHTree.FromObject(ob,dg),ob.matrix_world.inverted()) for ob in s.objects if ob.type=='MESH' and not ob.hide_render and ob.name.startswith(('C6 / sclera','C6 / iris','C7 / clear cornea'))]
  for i in patch:
   curve=after[i]
   for j in range(3):
    A,B=Vector(curve[j]),Vector(curve[j+1]);D=B-A
    if D.length:
     epsilon=min(1e-6,D.length*.001);start=A+D.normalized()*epsilon;raylen=max(0,D.length-epsilon)
     if raylen and tree.ray_cast(start,D.normalized(),raylen)[0] is not None:bodyhits.append([int(i),j])
    for t in [.125,.25,.5,.75,1.]:
     P=A.lerp(B,t);hit,n,face,d=tree.find_nearest(P);assert hit is not None;gaps.append((P-hit).dot(n))
    for ob,et,iv in eyes:
     A0,B0=iv@A,iv@B;D0=B0-A0
     if D0.length and et.ray_cast(A0,D0.normalized(),D0.length)[0] is not None:eyehits.append([int(i),j,ob.name])
  r['clearance']=dict(samples=len(gaps),minimum_signed_gap=float(min(gaps)),body_segment_hits=bodyhits,eye_segment_hits=eyehits)
  save('actual-scaled-geometry-measured-before-clearance-decision')
  assert min(gaps)>=-1e-5 and not bodyhits and not eyehits,'Physical clearance loss; stop before render'
  valid,lookup=H.native_sample(body,hair);assert len(valid)==186125 and valid.all();native_root_error=np.linalg.norm(after[:,0]-lookup,axis=1);assert native_root_error.max()<1e-4
  cam0=s.camera;cam=cam0.copy();cam.data=cam0.data.copy();s.collection.objects.link(cam);packet=json.loads((ROOT/'artifacts/character-head-c14-color/receipt.json').read_text());head=next(x for x in packet['renders'] if x['name']=='color-head-front');cam.matrix_world=Matrix(head['camera_matrix']);cam.data.type=head['type'];cam.data.lens=head['lens'];bpy.context.view_layer.update()
  uv0=H.project(before,cam);uv1=H.project(after,cam)
  def projection(uv,ids):return H.stats(np.linalg.norm(np.diff(uv[ids]*1024,axis=1),axis=2).sum(axis=1))
  r['projection']=dict(original_549_before=projection(uv0,oldpatch),original_549_after=projection(uv1,oldpatch),children_6125_before=projection(uv0,children),children_6125_after=projection(uv1,children),combined_before=projection(uv0,patch),combined_after=projection(uv1,patch))
  bpy.data.objects.remove(cam,do_unlink=True);s.camera=cam0
  assert S.geometry_hash()==geom and S.light_snapshot()==lights and S.material_snapshot()==mats and digest(H.coords(body,True))==bodyeval_hash and sha(SOURCE)==SOURCE_SHA
  r.update(blender=bpy.app.version_string,method='Native GN after Deform and Rotate: actual evaluated P+(P-own_root)*(scale-1), own_root obtained by CurveOfPoint+SampleIndex. Scalar=1+1.5*same C24 smooth fade. No Python runtime dependency or baked pose-root vectors.',mask=dict(original_patch_curves=len(oldpatch),c26_added_curves=len(children),combined_patch_curves=len(patch),untouched_other_original_curves=int(outside.sum()),fully_2_5x_original=int((scales[oldpatch]==2.5).sum()),fully_2_5x_children=int((scales[children]==2.5).sum()),scale=H.stats(scales[patch]),source_c24_angle_attribute_bit_exact=True),geometry=dict(curves=len(hc.curves),points=len(hc.position_data),roots_error=H.stats(root_error),outside_patch_point_error=H.stats(outside_error),evaluated_root_pivot_scale_residual=H.stats(residual),absolute_length_ratio_error=H.stats(length_error),all_original_raw_attributes_bit_exact=True,radii_rest_uv_and_all_other_attributes_bit_exact=True,native_uv_valid=int(valid.sum()),native_uv_invalid=int((~valid).sum()),native_root_lookup_error=H.stats(native_root_error)),body_material_lights_camera_and_source_unchanged=True,limits=['Single forehead patch and one fixed2.5x central length; no density/length scan or full-body expansion.','Stored pigment rest and UV attributes unchanged; actual native surface roots verified. No motion/deformation-range quality claim.','Projected~2.3px target is a falsifiable readability hypothesis, not a promised plush result.','Technical diagnostic only; no art pass, animation, Web, fees, deployment, commit or push.'])
  np.savez_compressed(out/'patch-cohorts-and-scales.npz',original_patch=oldpatch,added_patch=children,scales=scales,weights=weights)
  save('actual-length-and-clearance-invariants-passed-before-render')
  native=out/'miao-c28-readable-fiber-patch.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);r['native_sha256']=sha(native)
  bpy.ops.wm.open_mainfile(filepath=str(native));hair=bpy.data.objects['Miao / native short plush'];assert digest(H.coords(hair,True))==digest(after.reshape(-1,3));r['native_reopen_evaluated_geometry_exact']=True
  renderer=ROOT/'artifacts/character-plush-coverage-c26/controlled-native-run/samebuffer-render.py';text=renderer.read_text();old=str(SOURCE.relative_to(ROOT));assert text.count(old)==1;text=text.replace(old,str(native.relative_to(ROOT)));script=out/'samebuffer-render.py';script.write_text(text);r['renderer_sha256']=sha(script);save('native-saved-reopened-verified-awaiting-serialized-render')
  if a.render:
   ns={'__file__':str(script),'__name__':'c28_renderer'};exec(compile(text,str(script),'exec'),ns);saved=sys.argv[:];sys.argv=[str(script),'--','--out',str(out/'render'),'--samples','128','--coverage']
   try:ns['main']()
   finally:sys.argv=saved
   r['render_calls']=1;r['render_receipt_sha256']=sha(out/'render/receipt.json');save('one-crop-rendered-awaiting-image-inspection-and-independent-reviews')
  print('RESULT '+json.dumps(r),flush=True)
 except Exception as ex:
  r.update(error=repr(ex),traceback=traceback.format_exc());save('stopped-before-further-work');raise

if __name__=='__main__':main()
