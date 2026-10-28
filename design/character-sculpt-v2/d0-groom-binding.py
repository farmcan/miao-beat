"""D0.2 real C5 groom attachment and one technical local shape perturbation.
No natural strum, rig, blink or production delivery. C5 and D0.1 inputs stay read-only.
"""
import argparse,bpy,hashlib,json,math,sys,time,traceback
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--input',default='artifacts/character-sculpt-d0/miao-d0-rest-bound.blend');p.add_argument('--output',default='artifacts/character-sculpt-d0-groom');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];src=(root/a.input).resolve();out=(root/a.output).resolve();out.mkdir(parents=True,exist_ok=True)
receipt={'stage':'D0.2-groom-attachment','status':'started','actual_gpu_renders':0,'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blender':bpy.app.version_string,'started_unix':time.time()}
def save():
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def stage(name):
 receipt['status']=name;save();print('D0_GROOM_STAGE',name,flush=True)
def stats(values):
 q=np.asarray(values,dtype=np.float64);return {'count':int(q.size),'finite':bool(np.isfinite(q).all()),'max':float(q.max(initial=0)),'mean':float(q.mean()),'p50':float(np.quantile(q,.5)),'p95':float(np.quantile(q,.95)),'p99':float(np.quantile(q,.99))}
def digest(x):return hashlib.sha256(np.asarray(x).tobytes()).hexdigest()
def positions(obj,evaluated=False):
 o=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else obj
 collection=o.data.vertices if o.type=='MESH' else o.data.position_data
 values=np.empty(len(collection)*3,np.float32);collection.foreach_get('co' if o.type=='MESH' else 'vector',values);return values.reshape(-1,3)
def world(obj,coords):
 m=np.array(obj.matrix_world,dtype=np.float64);return np.asarray(coords,dtype=np.float64)@m[:3,:3].T+m[:3,3]
def rest_hash(obj,evaluated=False):
 o=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else obj
 attr=o.data.attributes['miao_rest_position'];v=np.empty(len(attr.data)*3,np.float32);attr.data.foreach_get('vector',v);return digest(v)
def geometry_hash(me):
 v=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',v)
 normal=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('normal',normal)
 loops=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',loops)
 starts=np.empty(len(me.polygons),np.int32);totals=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('loop_start',starts);me.polygons.foreach_get('loop_total',totals)
 return {'positions':digest(v),'vertex_normals':digest(normal),'loop_vertex_indices':digest(loops),'polygon_loop_starts':digest(starts),'polygon_loop_totals':digest(totals),'vertices':len(me.vertices),'polygons':len(me.polygons),'corners':len(me.loops),'has_custom_normals':me.has_custom_normals}
def native_uv_validity(body,hair):
 # Official lookup over every actual curve, in a temporary evaluation-only group.
 group=bpy.data.node_groups.new('D0 / temporary native UV validity','GeometryNodeTree');group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=group.nodes;l=group.links
 ni=n.new('NodeGroupInput');no=n.new('NodeGroupOutput');info=n.new('GeometryNodeObjectInfo');info.inputs['Object'].default_value=body
 uv=n.new('GeometryNodeInputNamedAttribute');uv.data_type='FLOAT_VECTOR';uv.inputs['Name'].default_value='BindUV';rootuv=n.new('GeometryNodeInputNamedAttribute');rootuv.data_type='FLOAT_VECTOR';rootuv.inputs['Name'].default_value='surface_uv_coordinate'
 sample=n.new('GeometryNodeSampleUVSurface');sample.data_type='FLOAT';l.new(info.outputs['Geometry'],sample.inputs['Mesh']);l.new(uv.outputs['Attribute'],sample.inputs['Source UV Map']);l.new(rootuv.outputs['Attribute'],sample.inputs['Sample UV'])
 store=n.new('GeometryNodeStoreNamedAttribute');store.domain='CURVE';store.data_type='BOOLEAN';store.inputs['Name'].default_value='d0_native_uv_valid';l.new(ni.outputs['Geometry'],store.inputs['Geometry']);l.new(sample.outputs['Is Valid'],store.inputs['Value']);l.new(store.outputs['Geometry'],no.inputs['Geometry'])
 mod=hair.modifiers.new('D0 / temporary native UV validity','NODES');mod.node_group=group;bpy.context.view_layer.update();ev=hair.evaluated_get(bpy.context.evaluated_depsgraph_get());attr=ev.data.attributes['d0_native_uv_valid'];values=np.empty(len(attr.data),np.bool_);attr.data.foreach_get('value',values);hair.modifiers.remove(mod);bpy.data.node_groups.remove(group);bpy.context.view_layer.update();return values

def main():
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];hair=bpy.data.objects['Miao / native short plush'];me=body.data;hc=hair.data
 assert len(me.vertices)==609383 and len(hc.curves)==180000 and len(hc.position_data)==720000
 assert not body.modifiers and not hair.modifiers and body.data.shape_keys is None
 before_mesh=geometry_hash(me);original=positions(hair).copy();original_world=world(hair,original);roots0=original_world[::4].copy();rest_before=rest_hash(hair);body_rest_before=rest_hash(body)
 existing_uv={}
 for layer in me.uv_layers:
  data=np.empty(len(layer.data)*2,np.float32);layer.data.foreach_get('uv',data);existing_uv[layer.name]=digest(data)
 receipt['existing_uv_layers_preserved']=existing_uv
 assert me.uv_layers.get('BindUV') is None,'Do not silently replace an existing BindUV'
 starts=np.empty(len(me.polygons),np.int32);totals=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('loop_start',starts);me.polygons.foreach_get('loop_total',totals)
 side=math.ceil(math.sqrt(len(me.polygons)));ids=np.repeat(np.arange(len(me.polygons),dtype=np.int32),totals);corner=np.arange(len(me.loops),dtype=np.int32)-starts[ids]
 # Put the highest-valence polygons near UV zero: float32 ULP is smaller there.
 # This preserves one guarded unique tile per polygon without relaxing coverage.
 tile_to_poly=np.argsort(-totals.astype(np.int64),kind='stable');poly_to_tile=np.empty(len(me.polygons),np.int32);poly_to_tile[tile_to_poly]=np.arange(len(me.polygons),dtype=np.int32);tile_ids=poly_to_tile[ids]
 angles=2*np.pi*corner/totals[ids]+np.pi/4
 uv_values=np.column_stack(((tile_ids%side+.5+.39*np.cos(angles))/side,(tile_ids//side+.5+.39*np.sin(angles))/side)).astype(np.float32)
 uv=me.uv_layers.new(name='BindUV');uv.data.foreach_set('uv',uv_values.ravel());me.update()
 assert geometry_hash(me)==before_mesh,'BindUV must not change positions, normals or topology'
 for name,previous_hash in existing_uv.items():
  data=np.empty(len(me.uv_layers[name].data)*2,np.float32);me.uv_layers[name].data.foreach_get('uv',data);assert digest(data)==previous_hash
 me.calc_loop_triangles();tris=np.empty(len(me.loop_triangles)*3,np.int32);tloops=np.empty_like(tris);poly=np.empty(len(me.loop_triangles),np.int32);me.loop_triangles.foreach_get('vertices',tris);me.loop_triangles.foreach_get('loops',tloops);me.loop_triangles.foreach_get('polygon_index',poly);tris=tris.reshape(-1,3);tloops=tloops.reshape(-1,3)
 tuv=uv_values[tloops].astype(np.float64);d1=tuv[:,1]-tuv[:,0];d2=tuv[:,2]-tuv[:,0];det=d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0]
 receipt['bind_uv']={'name':'BindUV','domain':me.attributes['BindUV'].domain,'data_type':me.attributes['BindUV'].data_type,'grid_side':side,'polygon_count':len(me.polygons),'max_polygon_corners':int(totals.max()),'corners':len(me.loops),'padding_cell_fraction_min':.11,'uv_sha256':digest(uv_values),'tile_order':'descending polygon corner count, most complex near UV origin','tile_to_poly_sha256':digest(tile_to_poly),'uv_min':uv_values.min(axis=0).tolist(),'uv_max':uv_values.max(axis=0).tolist(),'triangle_count':len(tris),'degenerate_uv_triangles':int(np.count_nonzero(np.abs(det)<1e-18)),'min_abs_uv_triangle_determinant':float(np.abs(det).min())}
 receipt['geometry_before_and_after_uv_identical']=before_mesh
 stage('uv-created-geometry-identical')
 assert np.all(np.abs(det)>1e-18),'Degenerate UV triangle; stop before attachment'
 # Each loop stays inside its own polygon tile. Distinct polygon IDs have disjoint tiles.
 loop_tiles=np.floor(uv_values.astype(np.float64)*side).astype(np.int64);assert np.all(loop_tiles[:,0]+side*loop_tiles[:,1]==tile_ids)
 hc.surface=body;hc.surface_uv_map='BindUV';body.add_rest_position_attribute=True
 bpy.ops.object.select_all(action='DESELECT');hair.select_set(True);bpy.context.view_layer.objects.active=hair
 snap=bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST');assert 'FINISHED' in snap
 attached=positions(hair).copy();attached_world=world(hair,attached);root_shift=np.linalg.norm(attached_world[::4]-roots0,axis=1);all_shift=np.linalg.norm(attached_world-original_world,axis=1)
 attr=hc.attributes['surface_uv_coordinate'];assert attr.data_type=='FLOAT2' and attr.domain=='CURVE' and len(attr.data)==180000
 roots_uv=np.empty(len(attr.data)*2,np.float32);attr.data.foreach_get('vector',roots_uv);roots_uv=roots_uv.reshape(-1,2)
 receipt['snap']={'result':sorted(snap),'root_shift':stats(root_shift),'all_point_shift':stats(all_shift),'root_uv_count':len(roots_uv),'root_uv_type':attr.data_type,'root_uv_domain':attr.domain,'root_uv_sha256':digest(roots_uv),'miao_rest_position_unchanged':rest_hash(hair)==rest_before}
 stage('native-nearest-attached')
 assert root_shift.max()<1e-4 and all_shift.max()<1e-4,'Unexpected initial snap jump; stop'
 assert rest_hash(hair)==rest_before
 # O(points + triangles + roots*triangles_on_that_polygon), never roots*all_faces.
 tiles=np.floor(roots_uv.astype(np.float64)*side).astype(np.int64);root_tile=tiles[:,0]+tiles[:,1]*side
 assert np.isfinite(roots_uv).all() and np.all(root_tile>=0) and np.all(root_tile<len(me.polygons))
 root_poly=tile_to_poly[root_tile]
 np.save(out/'native-root-uv.npy',roots_uv);np.save(out/'tile-to-polygon.npy',tile_to_poly)
 order=np.argsort(poly,kind='stable');counts=np.bincount(poly,minlength=len(me.polygons));offset=np.r_[0,np.cumsum(counts)];best_min=np.full(len(roots_uv),-np.inf);best_tri=np.full(len(roots_uv),-1,np.int32);best_bary=np.zeros((len(roots_uv),3),np.float64)
 for j in range(int(counts[root_poly].max())):
  active=np.flatnonzero(counts[root_poly]>j);ti=order[offset[root_poly[active]]+j];r=roots_uv[active].astype(np.float64)-tuv[ti,0];den=det[ti]
  b1=(r[:,0]*d2[ti,1]-r[:,1]*d2[ti,0])/den;b2=(d1[ti,0]*r[:,1]-d1[ti,1]*r[:,0])/den;weights=np.column_stack((1-b1-b2,b1,b2));minimum=weights.min(axis=1);take=minimum>best_min[active];idx=active[take];best_min[idx]=minimum[take];best_tri[idx]=ti[take];best_bary[idx]=weights[take]
 receipt['root_uv_decode']={'roots':len(roots_uv),'assigned_triangles':int(np.count_nonzero(best_tri>=0)),'worst_min_barycentric':float(best_min.min()),'root_poly_triangles_max':int(counts[root_poly].max()),'outside_tolerance_0_005':int(np.count_nonzero(best_min<-.005))}
 np.savez_compressed(out/'root-uv-decode.npz',polygon=root_poly,triangle=best_tri,barycentric=best_bary,min_barycentric=best_min)
 stage('all-root-uvs-decoded')
 assert np.all(best_tri>=0) and np.all(best_min>=-.005),'UV precision/coverage failed; stop'
 np.save(out/'native-root-uv.raw.npy',roots_uv)
 valid=native_uv_validity(body,hair);invalid=np.flatnonzero(~valid);receipt['native_uv_validation_raw']={'curves':len(valid),'valid':int(valid.sum()),'invalid_indices':invalid.tolist()};save()
 assert len(invalid)<=8,'Too many native invalid roots; do not hide a bad atlas'
 if len(invalid):
  raw=roots_uv.copy();old_coords_hash=digest(positions(hair));repair=[]
  for i in invalid:
   triangle=best_tri[i];w=np.maximum(best_bary[i],.002);w/=w.sum();roots_uv[i]=(w@tuv[triangle]).astype(np.float32)
   r=roots_uv[i].astype(np.float64)-tuv[triangle,0];b1=(r[0]*d2[triangle,1]-r[1]*d2[triangle,0])/det[triangle];b2=(d1[triangle,0]*r[1]-d1[triangle,1]*r[0])/det[triangle];best_bary[i]=[1-b1-b2,b1,b2];best_min[i]=best_bary[i].min()
   repair.append({'curve':int(i),'polygon':int(root_poly[i]),'triangle':int(triangle),'raw_uv':raw[i].tolist(),'interior_uv':roots_uv[i].tolist(),'uv_delta':float(np.linalg.norm(roots_uv[i].astype(np.float64)-raw[i])),'actual_min_barycentric':float(best_min[i])})
  attr.data.foreach_set('vector',roots_uv.ravel());assert digest(positions(hair))==old_coords_hash and rest_hash(hair)==rest_before
  receipt['native_uv_interior_repair']={'count':len(repair),'barycentric_floor_before_normalize':.002,'same_original_polygon_and_triangle':True,'geometry_points_and_custom_rest_unchanged':True,'roots':repair}
 valid=native_uv_validity(body,hair);receipt['native_uv_validation_final']={'curves':len(valid),'valid':int(valid.sum()),'invalid_indices':np.flatnonzero(~valid).tolist()};stage('all-native-root-uvs-valid')
 assert len(valid)==180000 and valid.all(),'Native UV validity must cover every curve'
 np.save(out/'native-root-uv.npy',roots_uv);np.savez_compressed(out/'root-uv-decode.npz',polygon=root_poly,triangle=best_tri,barycentric=best_bary,min_barycentric=best_min);receipt['root_uv_decode']['final_root_uv_sha256']=digest(roots_uv)
 def expected_roots(surface_positions):
  return world(body,np.einsum('ni,nij->nj',best_bary,np.asarray(surface_positions)[tris[best_tri]]))
 bind_expected=expected_roots(positions(body));bind_error=np.linalg.norm(attached_world[::4]-bind_expected,axis=1);receipt['root_uv_decode']['bind_surface_target_error']=stats(bind_error)
 assert bind_error.max()<1e-4,'Root UV does not reconstruct the same actual body surface'
 ng=bpy.data.node_groups.new('D0 / official groom surface deformation','GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');ni=ng.nodes.new('NodeGroupInput');no=ng.nodes.new('NodeGroupOutput');deform=ng.nodes.new('GeometryNodeDeformCurvesOnSurface');ng.links.new(ni.outputs['Geometry'],deform.inputs['Curves']);ng.links.new(deform.outputs['Curves'],no.inputs['Geometry']);mod=hair.modifiers.new('D0 / official surface attachment','NODES');mod.node_group=ng
 bpy.context.view_layer.update();static=positions(hair,True);static_world=world(hair,static);static_error=np.linalg.norm(static_world-attached_world,axis=1)
 receipt['rest_evaluation']={'all_point_error':stats(static_error),'root_error':stats(np.linalg.norm(static_world[::4]-attached_world[::4],axis=1)),'evaluated_rest_attribute_unchanged':rest_hash(hair,True)==rest_before}
 stage('official-deform-rest-evaluated')
 assert static_error.max()<1e-4 and rest_hash(hair,True)==rest_before,'Static binding not identity'
 base=positions(body).copy();basis=body.shape_key_add(name='Basis');key=body.shape_key_add(name='D0 technical only / local paw +0.02Z')
 q=((base[:,0]+.62)/.42)**2+((base[:,1]+1.16)/.32)**2+((base[:,2]-1.50)/.43)**2;weight=np.maximum(0,1-q)**3;warped=base.copy();warped[:,2]+=.02*weight;key.data.foreach_set('co',warped.ravel());key.value=0
 receipt['technical_shape']={'name':key.name,'requested_max_Z':.02,'actual_max_Z':float((warped-base)[:,2].max()),'vertices_nonzero':int(np.count_nonzero(weight)),'definition':'compact ellipsoid smooth cubic falloff; no natural strum claim','coordinate_sha256':digest(warped)}
 def nearest_errors(roots_world):
  dg=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(body,dg);inverse=body.matrix_world.inverted();values=np.empty(len(roots_world),np.float64)
  for i,point in enumerate(roots_world):
   hit,normal,face,distance=tree.find_nearest(inverse@Vector(point))
   assert hit is not None
   values[i]=(Vector(point)-body.matrix_world@hit).length
  return stats(values)
 bpy.context.view_layer.update();baseline_points=positions(hair,True);baseline_world=world(hair,baseline_points)
 receipt['rest_evaluation']['all_180k_root_nearest_surface_error']=nearest_errors(baseline_world[::4])
 key.value=1;bpy.context.view_layer.update();deformed_surface=positions(body,True);moved=positions(hair,True);moved_world=world(hair,moved);expected=expected_roots(deformed_surface);root_error=np.linalg.norm(moved_world[::4]-expected,axis=1);root_movement=np.linalg.norm(moved_world[::4]-baseline_world[::4],axis=1)
 receipt['deformed_evaluation']={'root_to_corresponding_uv_surface_error':stats(root_error),'all_180k_root_nearest_surface_error':nearest_errors(moved_world[::4]),'root_movement':stats(root_movement),'roots_moved_gt_1e_6':int(np.count_nonzero(root_movement>1e-6)),'all_point_movement':stats(np.linalg.norm(moved_world-baseline_world,axis=1)),'evaluated_hair_rest_attribute_unchanged':rest_hash(hair,True)==rest_before,'body_rest_attribute_unchanged':rest_hash(body,True)==body_rest_before,'curve_count':len(hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.curves),'point_count':len(moved)}
 stage('technical-local-shape-evaluated')
 assert root_error.max()<1e-4 and receipt['deformed_evaluation']['all_180k_root_nearest_surface_error']['max']<1e-4,'Detached/wrong root after deformation'
 assert receipt['deformed_evaluation']['roots_moved_gt_1e_6']>0 and root_movement.max()>.005,'Node may have silently passed undeformed hair'
 assert rest_hash(hair,True)==rest_before and rest_hash(body,True)==body_rest_before
 s.render.resolution_x=s.render.resolution_y=512;s.render.resolution_percentage=100;s.cycles.seed=17;s.cycles.samples=32;s.cycles.use_animated_seed=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';receipt['renders']=[]
 for tag,value in [('baseline-attached',0),('local-paw-perturbation',1)]:
  key.value=value;bpy.context.view_layer.update();s.render.filepath=str(out/(tag+'.png'));bpy.ops.wm.save_as_mainfile(filepath=str(out/(tag+'.blend')),compress=True);t=time.time();bpy.ops.render.render(write_still=True);receipt['actual_gpu_renders']+=1;receipt['renders'].append({'tag':tag,'seconds':time.time()-t,'sha256':hashlib.sha256((out/(tag+'.png')).read_bytes()).hexdigest()});save()
 assert hashlib.sha256(src.read_bytes()).hexdigest()==receipt['input_sha256'];receipt['input_unchanged']=True;receipt['hair_rest_sha256']=rest_before;receipt['body_rest_sha256']=body_rest_before;receipt['limitations']=['One small technical local shape key, not natural strumming or a rig.','No blink, head movement, phrase behavior, browser, audio sync or export.','High-density frozen mesh only; no claim for retopology or another model.','Custom hair shader lookup still lacks separate AOV proof from D0.1.'];receipt['elapsed_seconds']=time.time()-receipt['started_unix'];stage('small_technical_loop_recorded_pending_independent_review')
try:main()
except Exception as e:
 receipt['status']='failed';receipt['error']=repr(e);receipt['traceback']=traceback.format_exc();save();print(receipt['traceback'],flush=True);raise
