"""C30: one .35 masked native Blend Hair Curves forehead-shape diagnostic.

Exactly C28's 6,674 patch curves enter the actual Blender Essentials asset;
everything else bypasses it. Counts/roots/segment lengths/radii/rest/UV fixed.
No custom shape averager, density/parameter scan, shader change or network.
"""
import argparse,hashlib,importlib.util,json,sys,traceback
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/character-plush-readable-c28/controlled-native-run/miao-c28-readable-fiber-patch.blend'
SOURCE_SHA='2c3d90f6157d86f886965df6384907cc69e5e96a55da020d247f6c9aa8b20559'
LIB=Path('/Applications/Blender.app/Contents/Resources/5.2/datafiles/assets/nodes/procedural_hair_node_assets.blend')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda a:hashlib.sha256(np.asarray(a).tobytes()).hexdigest()

def module(path,name):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def wrapper(hair,radius):
 with bpy.data.libraries.load(str(LIB),link=False) as (source,target):
  assert 'Blend Hair Curves' in source.node_groups;target.node_groups=['Blend Hair Curves']
 asset=target.node_groups[0]
 actual={i.name:i.identifier for i in asset.interface.items_tree if i.item_type=='SOCKET' and i.in_out=='INPUT'}
 assert set(actual)=={'Geometry','Factor','Blend Radius','Blend Neighbors','Preserve Length'}
 # The native asset graph uses own-root points as target locations, then calls
 # Restore Curve Segment Length with a root pin. Do not quietly substitute one.
 restore=asset.nodes['Group'];assert restore.node_tree.name.startswith('Restore Curve Segment Length') and restore.inputs['Pin at Parameter'].default_value==0
 g=bpy.data.node_groups.new('C30 / isolated patch native shape blend','GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n,l=g.nodes,g.links
 ni=n.new('NodeGroupInput');no=n.new('NodeGroupOutput');mask=n.new('GeometryNodeInputNamedAttribute');mask.data_type='BOOLEAN';mask.inputs['Name'].default_value='c30_patch'
 sep=n.new('GeometryNodeSeparateGeometry');sep.domain='CURVE';l.new(ni.outputs['Geometry'],sep.inputs['Geometry']);l.new(mask.outputs['Attribute'],sep.inputs['Selection'])
 blend=n.new('GeometryNodeGroup');blend.node_tree=asset;l.new(sep.outputs['Selection'],blend.inputs['Geometry']);blend.inputs['Blend Radius'].default_value=radius;blend.inputs['Blend Neighbors'].default_value=10;blend.inputs['Preserve Length'].default_value=True
 strength=n.new('GeometryNodeInputNamedAttribute');strength.data_type='FLOAT';strength.inputs['Name'].default_value='c30_strength';l.new(strength.outputs['Attribute'],blend.inputs['Factor'])
 join=n.new('GeometryNodeJoinGeometry');l.new(blend.outputs['Geometry'],join.inputs['Geometry']);l.new(sep.outputs['Inverted'],join.inputs['Geometry'])
 order=n.new('GeometryNodeInputNamedAttribute');order.data_type='INT';order.inputs['Name'].default_value='c30_original_curve_index';sort=n.new('GeometryNodeSortElements');sort.domain='CURVE';l.new(join.outputs['Geometry'],sort.inputs['Geometry']);l.new(order.outputs['Attribute'],sort.inputs['Sort Weight']);l.new(sort.outputs['Geometry'],no.inputs['Geometry']);assert all(x.is_valid for x in l)
 md=hair.modifiers.new('C30 / same-root patch-only native Blend Hair Curves','NODES');md.node_group=g;return md,asset,blend

def main():
 pa=argparse.ArgumentParser();pa.add_argument('--out',default='artifacts/character-plush-coherent-c30/controlled-native-run');pa.add_argument('--render',action='store_true');args=pa.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True);assert not (out/'receipt.json').exists(),'Preserve previous experiment'
 (out/'executed-script.py').write_bytes(Path(__file__).read_bytes());r=dict(stage='C30-single-patch-native-shape-coordination',source_sha256=sha(__file__),input_sha256=sha(SOURCE),actual_render_calls=0)
 def save(status):
  r['status']=status;(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('C30_STAGE '+status,flush=True)
 try:
  assert sha(SOURCE)==SOURCE_SHA
  H=module(ROOT/'design/character-sculpt-v2/plush-coverage-patch-c26.py','c26_readonly');S=module(ROOT/'design/character-sculpt-v2/eye-optics-diagnostic.py','snapshots');sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_hair
  bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;hair=bpy.data.objects['Miao / native short plush'];body=bpy.data.objects['Miao / continuous pear and rounded-square face'];hc=hair.data;N=len(hc.curves);assert N==186125
  geom,lights,mats=S.geometry_hash(),S.light_snapshot(),S.material_snapshot();bodyhash=digest(H.coords(body,True))
  raw={a.name:(a.data_type,a.domain,H.attr_array(a).copy()) for a in hc.attributes};before=H.coords(hair,True).reshape(N,4,3);ev=hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data;meta={a.name:(a.data_type,a.domain,H.attr_array(a).copy()) for a in ev.attributes if a.name!='position'}
  cohort=np.load(ROOT/'artifacts/character-plush-readable-c28/controlled-native-run/patch-cohorts-and-scales.npz');old=cohort['original_patch'];children=cohort['added_patch'];patch=np.r_[old,children];weights=cohort['weights'];assert len(old)==549 and len(children)==6125 and len(patch)==6674
  outside=np.ones(N,bool);outside[patch]=False;mask=~outside;assert np.array_equal(weights>0,mask)
  roots=before[patch,0].astype(float);kd=KDTree(len(roots))
  for i,p in enumerate(roots):kd.insert(Vector(p),i)
  kd.balance();nn=[];neighbors=[]
  for i,p in enumerate(roots):
   hits=[(j,d) for co,j,d in kd.find_n(Vector(p),11) if j!=i];assert len(hits)>=1 and hits[0][1]>0;nn.append(hits[0][1]);neighbors.append([j for j,d in hits[:10]])
  median=float(np.median(nn));radius=2*median;neighbors=np.asarray(neighbors,np.int32);assert neighbors.shape==(6674,10)
  r['design']=dict(factor=.35,fade='exact persisted C28 weights',blend_radius=radius,root_nearest_neighbor_median=median,nearest_neighbor_stats=H.stats(nn),blend_neighbors=10,preserve_length=True,patch_curves=6674,original_patch_curves=549,c26_children=6125,nonpatch_bypass_curves=int(outside.sum()),scope='Only separated patch geometry enters native averaging; Blend Radius controls root merge distance, not a proven hard neighbor-influence cutoff.')
  for name,typ,values in [('c30_patch','BOOLEAN',mask),('c30_original_curve_index','INT',np.arange(N,dtype=np.int32)),('c30_strength','FLOAT',np.zeros(N,np.float32))]:
   a=hc.attributes.new(name,typ,'CURVE');a.data.foreach_set('value',values)
  md,asset,blend=wrapper(hair,radius);hc.update_tag();hair.update_tag();bpy.context.view_layer.update()
  zero=H.coords(hair,True).reshape(N,4,3);zero_error=np.linalg.norm(zero-before,axis=2);r['zero_control']=dict(evaluated_position_error=H.stats(zero_error),roots_error=H.stats(np.linalg.norm(zero[:,0]-before[:,0],axis=1)),actual_asset=asset.name,actual_asset_interface=[dict(name=x.name,id=x.identifier) for x in asset.interface.items_tree if x.item_type=='SOCKET'],asset_library_sha256=sha(LIB),curve_count=len(hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.curves))
  save('zero-factor-native-control-measured')
  assert zero_error.max()<1e-6,'Zero blend unexpectedly changes geometry'
  ze=hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
  for name,(typ,dom,v) in meta.items():assert np.array_equal(H.attr_array(ze.attributes[name]),v),'Zero factor changes original metadata'
  actual_strength=(.35*weights).astype(np.float32);hc.attributes['c30_strength'].data.foreach_set('value',actual_strength);hc.update_tag();hair.update_tag();bpy.context.view_layer.update()
  after=H.coords(hair,True).reshape(N,4,3);ev=hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data;assert len(ev.curves)==N
  for name,(typ,dom,v) in raw.items():assert np.array_equal(H.attr_array(hc.attributes[name]),v),'Original raw source attribute changed'
  for name,(typ,dom,v) in meta.items():assert np.array_equal(H.attr_array(ev.attributes[name]),v),'Actual blend changes original metadata'
  rooterr=np.linalg.norm(after[:,0]-before[:,0],axis=1);outerr=np.linalg.norm(after[outside]-before[outside],axis=2)
  len0=np.linalg.norm(np.diff(before.astype(float),axis=1),axis=2);len1=np.linalg.norm(np.diff(after.astype(float),axis=1),axis=2);lengtherr=np.abs(len1-len0)/len0
  r['initial_actual_checks']=dict(root_error=H.stats(rooterr),outside_patch_error=H.stats(outerr),relative_segment_length_error=H.stats(lengtherr),patch_point_movement=H.stats(np.linalg.norm(after[patch]-before[patch],axis=2)))
  save('actual-native-root-length-metadata-checks-measured')
  # The task explicitly requires stopping if the native asset changes roots.
  # Do not silently relax this to the inherited UV-binding tolerance: a tiny
  # floating-point drift must be reported rather than called exact anchoring.
  assert np.array_equal(after[:,0],before[:,0]),'Native asset roots are not bit-exact; stop before render'
  assert outerr.max()<1e-7,'Nonpatch changed; stop'
  assert lengtherr.max()<5e-4,'Preserve Length does not preserve source segment profile; stop'
  def dirs(points):
   v=points[patch,-1].astype(float)-points[patch,0];return v/np.linalg.norm(v,axis=1)[:,None]
  d0,d1=dirs(before),dirs(after);change=np.degrees(np.arccos(np.clip((d0*d1).sum(axis=1),-1,1)));assert change.max()<90,'A tip direction flipped'
  def variation(d):return np.degrees(np.arccos(np.clip((d[:,None,:]*d[neighbors]).sum(axis=2),-1,1)))
  v0,v1=variation(d0),variation(d1)
  r['direction']=dict(tip_direction_change_degrees=H.stats(change),nearest_10_tip_angle_before=H.stats(v0),nearest_10_tip_angle_after=H.stats(v1),interpretation='Same actual local root-neighbor set; smaller angle dispersion supports local shape coordination, not art quality.')
  dg=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(body,dg);eyes=[(ob,BVHTree.FromObject(ob,dg),ob.matrix_world.inverted()) for ob in s.objects if ob.type=='MESH' and not ob.hide_render and ob.name.startswith(('C6 / sclera','C6 / iris','C7 / clear cornea'))];gaps=[];bodyhits=[];eyehits=[]
  for i in patch:
   for j in range(3):
    A,B=Vector(after[i,j]),Vector(after[i,j+1]);D=B-A
    if D.length:
     eps=min(1e-6,D.length*.001);start=A+D.normalized()*eps
     if tree.ray_cast(start,D.normalized(),D.length-eps)[0] is not None:bodyhits.append([int(i),j])
    for t in [.125,.25,.5,.75,1.]:
     P=A.lerp(B,t);hit,n,f,d=tree.find_nearest(P);assert hit is not None;gaps.append((P-hit).dot(n))
    for ob,et,iv in eyes:
     A0,B0=iv@A,iv@B;D0=B0-A0
     if D0.length and et.ray_cast(A0,D0.normalized(),D0.length)[0] is not None:eyehits.append([int(i),j,ob.name])
  r['clearance']=dict(samples=len(gaps),minimum_signed_gap=float(min(gaps)),body_segment_hits=bodyhits,eye_segment_hits=eyehits);save('actual-clearance-measured')
  assert min(gaps)>=-1e-5 and not bodyhits and not eyehits,'Physical clearance loss; stop'
  valid,lookup=H.native_sample(body,hair);assert len(valid)==N and valid.all();lookup_error=np.linalg.norm(after[:,0]-lookup,axis=1);assert lookup_error.max()<1e-4
  cam0=s.camera;cam=cam0.copy();cam.data=cam0.data.copy();s.collection.objects.link(cam);pkt=json.loads((ROOT/'artifacts/character-head-c14-color/receipt.json').read_text());head=next(x for x in pkt['renders'] if x['name']=='color-head-front');cam.matrix_world=Matrix(head['camera_matrix']);cam.data.type=head['type'];cam.data.lens=head['lens'];bpy.context.view_layer.update()
  def projection(points):return H.stats(np.linalg.norm(np.diff(H.project(points,cam)[patch]*1024,axis=1),axis=2).sum(axis=1))
  r['projection']=dict(before=projection(before),after=projection(after));bpy.data.objects.remove(cam,do_unlink=True);s.camera=cam0
  assert S.geometry_hash()==geom and S.light_snapshot()==lights and S.material_snapshot()==mats and digest(H.coords(body,True))==bodyhash and sha(SOURCE)==SOURCE_SHA
  r.update(blender=bpy.app.version_string,native_uv_valid=int(valid.sum()),native_uv_invalid=int((~valid).sum()),native_root_lookup_error=H.stats(lookup_error),all_original_raw_attributes_and_evaluated_metadata_bit_exact=True,body_material_lights_camera_and_source_unchanged=True,limits=['One .35 native patch blend, same existing fade; no shape-average replacement or parameter scan.','Only isolated patch feeds native guides; radius is actual root-merge distance2xNNmedian, not hard influence cutoff.','Segment lengths and current root attachment checked; no motion/deformation-range quality claim.','Technical diagnostic only; independent3role review needed. No full-body expansion, art pass, animation, Web, fees or deployment.'])
  np.savez_compressed(out/'patch-local-neighbors.npz',patch=patch,weights=weights,nearest_neighbor_distance=np.asarray(nn),nearest_10_indices=neighbors)
  save('native-root-length-metadata-clearance-invariants-passed-before-render')
  native=out/'miao-c30-coherent-flow-patch.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);r['native_sha256']=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));hair=bpy.data.objects['Miao / native short plush'];assert digest(H.coords(hair,True))==digest(after.reshape(-1,3));r['native_reopen_evaluated_geometry_exact']=True
  renderer=ROOT/'artifacts/character-plush-readable-c28/controlled-native-run/samebuffer-render.py';text=renderer.read_text();oldpath=str(SOURCE.relative_to(ROOT));assert text.count(oldpath)==1;text=text.replace(oldpath,str(native.relative_to(ROOT)));script=out/'samebuffer-render.py';script.write_text(text);r['renderer_sha256']=sha(script);save('native-saved-reopened-verified-awaiting-serialized-render')
  if args.render:
   ns={'__file__':str(script),'__name__':'c30_renderer'};exec(compile(text,str(script),'exec'),ns);oldargv=sys.argv[:];sys.argv=[str(script),'--','--out',str(out/'render'),'--samples','128','--coverage']
   try:ns['main']()
   finally:sys.argv=oldargv
   r['actual_render_calls']=1;r['render_receipt_sha256']=sha(out/'render/receipt.json');save('one-crop-rendered-awaiting-image-inspection-and-independent-reviews')
  print('RESULT '+json.dumps(r),flush=True)
 except Exception as ex:
  r.update(error=repr(ex),traceback=traceback.format_exc());save('stopped-before-further-work');raise

if __name__=='__main__':main()
