"""C52 fixed .010u whole-body voxel authoring-base diagnostic on frozen C49.
One native object-mode remesh + one .15 Smooth iteration. No sculpt fields this
round; all new point identities0, all inherited contact/UV/groom/rig gates invalid.
"""
import bpy,bmesh,numpy as np,json,sys,time,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/character-body-voxel-c52';SRC=ROOT/'artifacts/character-local-merge-c49/miao-c49-local-merge.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();h=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';text=h.read_text();exec(compile(text[text.index('def smooth'):text.index('def main():')],str(h)+'#pure-helpers','exec'),globals())
def basic(me):
 r=topo(me);bm=bmesh.new();bm.from_mesh(me);r['signed_volume']=bm.calc_volume(signed=True);r['euler']=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free();return r

def spacing(me):
 co=arr(me);edges=np.array([tuple(e.vertices) for e in me.edges]);length=np.linalg.norm(co[edges[:,0]]-co[edges[:,1]],axis=1);me.calc_loop_triangles();tri=np.array([tuple(t.vertices) for t in me.loop_triangles]);pp=co[tri];area=np.linalg.norm(np.cross(pp[:,1]-pp[:,0],pp[:,2]-pp[:,0]),axis=1)*.5;return {'edge_length_quantiles_0_1_50_99_100':np.percentile(length,[0,1,50,99,100]).tolist(),'edge_coefficient_of_variation':float(np.std(length)/np.mean(length)),'triangle_area_quantiles_0_1_50_99_100':np.percentile(area,[0,1,50,99,100]).tolist(),'zero_area_triangles':int((area<=1e-14).sum()),'limits':'Spacing diagnostics only; not a global self/wood/parity or animation topology audit.'}

def snap(o):
 r=fingerprint(o);r['materials']=[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [];return r

def main():
 assert not (OUT/'receipt.json').exists(),'Frozen C52, no repeat candidate';start=time.time();srcsha=sha(SRC);bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];bpy.context.view_layer.update();others={o.name:snap(o) for o in bpy.data.objects if o!=body and o.type in {'MESH','CURVE','CURVES'} and not(o.type=='CURVES' and o.hide_render and 'plush' in o.name.lower())};initial=basic(body.data);original_spacing=spacing(body.data);original_modifiers=[{'name':m.name,'type':m.type} for m in body.modifiers];original_shape_keys=[k.name for k in body.data.shape_keys.key_blocks] if body.data.shape_keys else [];old_ids=[a.name for a in body.data.attributes if a.domain=='POINT' and a.data_type in {'INT','BOOLEAN'}]
 # Neutral body material, plus scene-native luminance compositor: independent
 # eye/face/guitar materials are never edited. Both baseline/result use this.
 clay=bpy.data.materials.new('C52 / neutral geometry diagnostic');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.40,.40,.40,1);bs.inputs['Roughness'].default_value=.68;body.data.materials.clear();body.data.materials.append(clay)
 tree=bpy.data.node_groups.new('C52 / matched grayscale diagnostic','CompositorNodeTree');s.compositing_node_group=tree;tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');rl=tree.nodes.new('CompositorNodeRLayers');bw=tree.nodes.new('CompositorNodeRGBToBW');out=tree.nodes.new('NodeGroupOutput');tree.links.new(rl.outputs['Image'],bw.inputs[0]);tree.links.new(bw.outputs[0],out.inputs['Image']);s.render.use_compositing=True;s.cycles.samples=16;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';cam=s.camera;frontloc=cam.location.copy();frontrot=cam.rotation_euler.copy();frontscale=cam.data.ortho_scale;renders=[]
 def render_pair(tag):
  for view in ['front','three-quarter']:
   cam.location=frontloc;cam.rotation_euler=frontrot;cam.data.ortho_scale=frontscale
   if view=='three-quarter':cam.location=(-6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler()
   file=OUT/(tag+'-gray-'+view+'.png');s.render.filepath=str(file);bpy.ops.render.render(write_still=True);renders.append({'stage':tag,'view':view,'file':file.name,'sha256':sha(file)})
  cam.location=frontloc;cam.rotation_euler=frontrot;cam.data.ortho_scale=frontscale
 render_pair('c49-before')
 # Freeze actual C49 evaluated skin only, then native object-mode voxel remesh.
 dg=bpy.context.evaluated_depsgraph_get();baked=bpy.data.meshes.new_from_object(body.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);body.data=baked
 for modifier in list(body.modifiers):body.modifiers.remove(modifier)
 bpy.ops.object.select_all(action='DESELECT');body.hide_set(False);body.select_set(True);bpy.context.view_layer.objects.active=body
 if body.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 me=body.data;me.remesh_voxel_size=.010;me.remesh_voxel_adaptivity=0.;me.use_remesh_preserve_volume=True;me.use_remesh_fix_poles=True
 if hasattr(me,'use_remesh_preserve_attributes'):me.use_remesh_preserve_attributes=False
 bpy.ops.object.voxel_remesh();after_voxel=basic(body.data);modifier=body.modifiers.new('C52 one restrained native Smooth','SMOOTH');modifier.factor=.15;modifier.iterations=1;bpy.ops.object.modifier_apply(modifier=modifier.name);me=body.data
 # Entire new branch has no original/canonical point identity. No guessing.
 for a in me.attributes:
  if a.domain in {'POINT','FACE'} and a.data_type in {'INT','BOOLEAN'}:
   values=np.zeros(len(a.data),np.int32 if a.data_type=='INT' else np.bool_);a.data.foreach_set('value',values)
 for name in set(old_ids+['Miao_C35_vertex_id','C52 source C49 vertex id']):
  a=me.attributes.get(name)
  if a is None:a=me.attributes.new(name,'INT','POINT')
  if a.data_type=='INT':a.data.foreach_set('value',np.zeros(len(me.vertices),np.int32))
 for uv in list(me.uv_layers):me.uv_layers.remove(uv)
 body.vertex_groups.clear();me.materials.clear();me.materials.append(clay)
 for face in me.polygons:face.use_smooth=True
 me.update();bpy.context.view_layer.update();final=basic(me);new_spacing=spacing(me);otherchecks={name:others[name]==snap(bpy.data.objects[name]) for name in others};allother=all(otherchecks.values());assert allother,{'changed_independent_objects':[n for n,v in otherchecks.items() if not v]};allzero=all(all(x.value==0 for x in a.data) for a in me.attributes if a.domain=='POINT' and a.data_type in {'INT','BOOLEAN'});assert allzero;render_pair('c52-after')
 native=OUT/'miao-c52-whole-body-voxel-authoring-study.blend';bpy.context.preferences.filepaths.save_version=0;cam.location=frontloc;cam.rotation_euler=frontrot;cam.data.ortho_scale=frontscale;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);np.savez_compressed(OUT/'new-topology-no-source-identity.npz',output_to_C49_vertex_index=np.full(len(me.vertices),-1,np.int32),Miao_C35_vertex_id=np.zeros(len(me.vertices),np.int32));r={'stage':'C52-one-fixed-whole-body-voxel-authoring-diagnostic','source_C49_native_sha256':srcsha,'source_C49_unchanged':sha(SRC)==srcsha,'script_sha256':sha(__file__),'blender':bpy.app.version_string,'scope':'Same C49 shape globally resampled, not a new primitive cat; complete body skin remains a single object mesh. No sculpt fields in this round.','method':{'native_object_mode_voxel_size':.010,'reason':'Thin ear rims/toe grooves need roughly2-3cells rather than .012; one fixed resolution, no scan.','adaptivity':0,'preserve_volume':True,'fix_poles':True,'native_smooth':{'factor':.15,'iterations':1,'calls':1}},'original_body_modifiers':original_modifiers,'original_shape_keys':original_shape_keys,'before':initial,'after_voxel_before_smooth':after_voxel,'after_one_native_smooth':final,'before_spacing':original_spacing,'after_spacing':new_spacing,'all_new_point_identity_attributes_zero':allzero,'no_nearest_identity_transfer':True,'all_independent_eye_face_guitar_geometry_transform_material_visibility_exact':allother,'independent_object_checks':otherchecks,'new_uv_layers':len(me.uv_layers),'body_vertex_groups':len(body.vertex_groups),'inherited_contact_art_uv_groom_rig_pass_invalidated':True,'render_method':'Neutral body clay plus native luminance compositor; independent object materials/geometry unchanged. Identical lighting/front/3Q and512px/16samples before/after.','renders':renders,'native_sha256':sha(native),'elapsed_seconds':time.time()-start,'limits':['Visual preservation and softness require actual before/after image inspection.','No C35/C49 contact pass inherited; no full actual wood/tube/parity audit.','No global self-intersection pass claimed from voxel operation alone; spacing/manifold results are separate facts.','No shallow ear or round-palm sculpt field, color/groom/UV binding, rig, animation, GLB, public output, deploy or service cost.']};(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps({'before':initial,'after':final,'independent_exact':allother,'all_new_ID0':allzero,'native':r['native_sha256']}),flush=True)
main()
