"""C34: one real CC0 Poly Haven velour substrate treatment, C28 hair unchanged.

Official preset non-color reflection nodes/inputs remain unchanged. Base Color
uses existing Miao pigment and Sheen Tint is neutral white to remove red-fabric
color inheritance; explicit independent planar UV routes data maps.
One fixed forehead treatment, no displacement or parameter scan.
"""
import argparse,hashlib,importlib.util,json,sys,traceback
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/character-plush-readable-c28/controlled-native-run/miao-c28-readable-fiber-patch.blend'
SOURCE_SHA='2c3d90f6157d86f886965df6384907cc69e5e96a55da020d247f6c9aa8b20559'
ASSETS=ROOT/'artifacts/polyhaven-velour';LIB=ASSETS/'material/velour_velvet_1k.blend';UV='C34_CoatXZ_3u';MASK='c34_forehead_substrate_mask'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();digest=lambda a:hashlib.sha256(np.asarray(a).tobytes()).hexdigest()
def module(path,name):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def value(v):
 if isinstance(v,(str,int,float,bool)):return v
 try:return list(v)
 except:return str(v)
def schema(mat):
 return dict(name=mat.name,nodes=[dict(name=n.name,type=n.bl_idname,inputs=[dict(name=x.name,id=x.identifier,default=value(x.default_value) if hasattr(x,'default_value') else None) for x in n.inputs],image=dict(path=n.image.filepath,space=n.image.colorspace_settings.name,size=list(n.image.size)) if n.type=='TEX_IMAGE' and n.image else None,uv_map=getattr(n,'uv_map',None)) for n in mat.node_tree.nodes],links=[dict(source=[l.from_node.name,l.from_socket.identifier],target=[l.to_node.name,l.to_socket.identifier]) for l in mat.node_tree.links])
def socket_defaults(node):return {x.identifier:value(x.default_value) for x in node.inputs if hasattr(x,'default_value')}
def clone_author_to_group(author):
 g=bpy.data.node_groups.new('C34 / CC0 official velour original reflection','ShaderNodeTree');g.interface.new_socket(name='Miao Pigment',in_out='INPUT',socket_type='NodeSocketColor');g.interface.new_socket(name='BSDF',in_out='OUTPUT',socket_type='NodeSocketShader');n,l=g.nodes,g.links;copied={}
 for src in author.node_tree.nodes:
  if src.type in {'OUTPUT_MATERIAL','FRAME'}:continue
  dst=n.new(src.bl_idname);dst.name=src.name;copied[src.name]=dst
  # Copy actual writable node properties. Geometry/links/parent UI plumbing are
  # handled separately; image pointers are preserved from the verified preset.
  for prop in src.bl_rna.properties:
   key=prop.identifier
   if prop.is_readonly or key in {'rna_type','type','name','parent','inputs','outputs','internal_links','image','texture_mapping','color_mapping'}:continue
   try:setattr(dst,key,getattr(src,key))
   except (TypeError,AttributeError,ValueError):pass
  if src.type=='TEX_IMAGE':dst.image=src.image
  for inp in src.inputs:
   if hasattr(inp,'default_value'):
    target=next((x for x in dst.inputs if x.identifier==inp.identifier),None)
    if target and hasattr(target,'default_value'):
     try:target.default_value=inp.default_value
     except (TypeError,ValueError):pass
 for link in author.node_tree.links:
  if link.from_node.name not in copied or link.to_node.name not in copied:continue
  if link.to_node.type=='BSDF_PRINCIPLED' and link.to_socket.name=='Base Color':continue
  if link.to_node.type=='MAPPING' and link.to_socket.name=='Vector':continue
  a=copied[link.from_node.name];b=copied[link.to_node.name];aa=next(x for x in a.outputs if x.identifier==link.from_socket.identifier);bb=next(x for x in b.inputs if x.identifier==link.to_socket.identifier);l.new(aa,bb)
 original_bsdf=next(x for x in author.node_tree.nodes if x.type=='BSDF_PRINCIPLED');bsdf=copied[original_bsdf.name];inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');l.new(inp.outputs['Miao Pigment'],bsdf.inputs['Base Color']);l.new(bsdf.outputs['BSDF'],out.inputs['BSDF'])
 uv=n.new('ShaderNodeUVMap');uv.name='C34 / explicit independent coat UV';uv.uv_map=UV;l.new(uv.outputs['UV'],copied['Mapping'].inputs['Vector'])
 copied['Normal Map.001'].uv_map=UV;copied['Tangent'].direction_type='UV_MAP';copied['Tangent'].uv_map=UV
 bsdf.inputs['Sheen Tint'].default_value=(1,1,1,1)
 expected=socket_defaults(original_bsdf);expected['Sheen Tint']=[1.,1.,1.,1.]
 assert socket_defaults(bsdf)==expected,'Unexpected author BSDF parameter change beyond neutral SheenTint'
 # Every non-BaseColor Principled incoming link is still the source preset link.
 def reflection_links(tree,node):return sorted((x.from_node.name,x.from_socket.identifier,x.to_socket.identifier) for x in tree.links if x.to_node==node and x.to_socket.name!='Base Color')
 assert reflection_links(g,bsdf)==reflection_links(author.node_tree,original_bsdf)
 assert all(x.is_valid for x in l)
 return g,copied,original_bsdf,bsdf

def main():
 pa=argparse.ArgumentParser();pa.add_argument('--out',default='artifacts/character-plush-substrate-c34/controlled-native-run');pa.add_argument('--render',action='store_true');a=pa.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True);assert not (out/'receipt.json').exists(),'Preserve old candidate';(out/'executed-script.py').write_bytes(Path(__file__).read_bytes())
 r=dict(stage='C34-single-real-CC0-velour-substrate-treatment',source_sha256=sha(__file__),input_sha256=sha(SOURCE),actual_render_calls=0)
 def save(status):r['status']=status;(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('C34_STAGE '+status,flush=True)
 try:
  assert sha(SOURCE)==SOURCE_SHA;provenance=json.loads((ASSETS/'provenance.json').read_text());verified=[]
  for rec in provenance['files']:
   p=ASSETS/'material'/rec['file'];assert p.is_file() and p.stat().st_size==rec['bytes'] and sha(p)==rec['sha256'] and hashlib.md5(p.read_bytes()).hexdigest()==rec['upstream_md5'];verified.append(rec)
  H=module(ROOT/'design/character-sculpt-v2/plush-coverage-patch-c26.py','helpers');S=module(ROOT/'design/character-sculpt-v2/eye-optics-diagnostic.py','snapshots')
  bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];hair=bpy.data.objects['Miao / native short plush'];me=body.data;geom,lights,mats=S.geometry_hash(),S.light_snapshot(),S.material_snapshot();bodypos=H.coords(body,True);hairpos=H.coords(hair,True);hairraw={x.name:H.attr_array(x).copy() for x in hair.data.attributes};hairev={x.name:H.attr_array(x).copy() for x in hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.attributes};hairmat=hair.data.materials[0]
  original_coat=me.materials[0];assert original_coat.name=='Miao / warm short plush';assert len(hair.data.curves)==186125
  original_bodyattrs={x.name:H.attr_array(x).copy() for x in me.attributes if x.data_type in {'FLOAT_VECTOR','FLOAT2','FLOAT','INT','INT8','BOOLEAN'}}
  uv_before={u.name:dict(data=digest(np.asarray([v.uv[:] for v in u.data],np.float32)),active_render=u.active_render) for u in me.uv_layers};active_uv=me.uv_layers.active.name
  with bpy.data.libraries.load(str(LIB),link=False) as (source,target):assert 'velour_velvet' in source.materials;target.materials=['velour_velvet']
  author=target.materials[0];author_schema=schema(author);(out/'author-original-schema.json').write_text(json.dumps(author_schema,indent=2)+'\n')
  images=[]
  for node in author.node_tree.nodes:
   if node.type!='TEX_IMAGE':continue
   img=node.image;name=Path(img.filepath).name;path=ASSETS/'material/textures'/name;assert path.is_file(),str(path);img.filepath=str(path);img.colorspace_settings.name='sRGB' if node.name=='diff' else 'Non-Color';img.reload();pixel=float(img.pixels[0]);assert min(img.size)>0 and img.has_data and np.isfinite(pixel)
   images.append(dict(node=node.name,path=str(path),sha256=sha(path),colorspace=img.colorspace_settings.name,size=list(img.size)))
  group,copied,author_bsdf,copy_bsdf=clone_author_to_group(author)
  mapping=copied['Mapping'];scale=np.asarray(mapping.inputs['Scale'].default_value,float);assert np.allclose(mapping.inputs['Location'].default_value,[0,0,0]) and np.allclose(mapping.inputs['Rotation'].default_value,[0,0,0]) and np.all(scale>0)
  # Preserve author's Mapping unchanged; precompensate only the independent UV
  # so its final image coordinates are exactly(X/3,Z/3): one tile=.3m at.1m/u.
  assert me.uv_layers.get(UV) is None;loopids=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',loopids);uv_values=(bodypos[loopids][:,[0,2]]/(3*scale[:2])).astype(np.float32);coat_uv=me.uv_layers.new(name=UV);coat_uv.data.foreach_set('uv',uv_values.ravel());me.uv_layers.active=me.uv_layers[active_uv]
  for name,state in uv_before.items():me.uv_layers[name].active_render=state['active_render']
  # Material mask uses the same matched-camera forehead ROI/fade and a front
  # surface visibility test; it does not wrap around to hidden back-of-head skin.
  cam0=s.camera;cam=cam0.copy();cam.data=cam0.data.copy();s.collection.objects.link(cam);pkt=json.loads((ROOT/'artifacts/character-head-c14-color/receipt.json').read_text());head=next(x for x in pkt['renders'] if x['name']=='color-head-front');cam.matrix_world=Matrix(head['camera_matrix']);cam.data.type=head['type'];cam.data.lens=head['lens'];bpy.context.view_layer.update();screen=H.project(bodypos,cam);roi=H.ROI;selected=np.flatnonzero((screen[:,0]>=roi[0])&(screen[:,0]<=roi[1])&(screen[:,1]>=roi[2])&(screen[:,1]<=roi[3]));tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());eye=cam.matrix_world.translation.copy();weights=np.zeros(len(bodypos),np.float32)
  for i in selected:
   P=Vector(bodypos[i]);hit=tree.ray_cast(eye,(P-eye).normalized(),20)[0]
   if hit is not None and (hit-P).length<1e-4:weights[i]=H.fade(screen[i])
  assert weights.max()==1 and np.count_nonzero(weights)>0;ma=me.attributes.new(MASK,'FLOAT','POINT');ma.data.foreach_set('value',weights);bpy.data.objects.remove(cam,do_unlink=True);s.camera=cam0
  coat=original_coat.copy();coat.name='C34 / Miao pigment with official CC0 velour substrate';nt=coat.node_tree;nodes,links=nt.nodes,nt.links;oldbsdf=nodes['Principled BSDF'];output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output);oldsurface=next(x.from_socket for x in links if x.to_node==output and x.to_socket.name=='Surface');pigment=next(x.from_socket for x in links if x.to_node==oldbsdf and x.to_socket.name=='Base Color');assert pigment.node.name=='Mix (Legacy).001'
  velour=nodes.new('ShaderNodeGroup');velour.node_tree=group;velour.name='C34 / authored velour BaseColor=Miao pigment';links.new(pigment,velour.inputs['Miao Pigment']);attr=nodes.new('ShaderNodeAttribute');attr.attribute_name=MASK;factor=nodes.new('ShaderNodeValue');factor.name='C34 / treatment factor';factor.outputs[0].default_value=0;mul=nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';links.new(attr.outputs['Fac'],mul.inputs[0]);links.new(factor.outputs[0],mul.inputs[1]);mix=nodes.new('ShaderNodeMixShader');links.new(mul.outputs[0],mix.inputs[0]);links.new(oldsurface,mix.inputs[1]);links.new(velour.outputs['BSDF'],mix.inputs[2]);links.new(mix.outputs[0],output.inputs['Surface']);me.materials[0]=coat;body.update_tag();bpy.context.view_layer.update()
  # Factor0 structural shader identity, not an unperformed pixel-match claim.
  assert factor.outputs[0].default_value==0 and np.all(weights*factor.outputs[0].default_value==0);assert next(x.from_socket for x in links if x.to_socket==mix.inputs[1])==oldsurface
  assert not output.inputs['Displacement'].is_linked
  def invariants():
   assert S.geometry_hash()==geom and S.light_snapshot()==lights and np.array_equal(H.coords(body,True),bodypos) and np.array_equal(H.coords(hair,True),hairpos)
   for name,v in hairraw.items():assert np.array_equal(H.attr_array(hair.data.attributes[name]),v)
   ev=hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
   for name,v in hairev.items():assert np.array_equal(H.attr_array(ev.attributes[name]),v)
   assert len(ev.curves)==186125 and len(ev.materials)==1 and ev.materials[0].original==hairmat
   for name,v in original_bodyattrs.items():assert np.array_equal(H.attr_array(me.attributes[name]),v),'Old body attribute changed'
   assert me.uv_layers.active.name==active_uv and hair.data.surface==body and hair.data.surface_uv_map=='BindUV'
   for name,state in uv_before.items():assert digest(np.asarray([v.uv[:] for v in me.uv_layers[name].data],np.float32))==state['data'] and me.uv_layers[name].active_render==state['active_render']
   now=S.material_snapshot()
   for name,v in mats.items():assert now[name]==v,'Original material changed'
   expected=socket_defaults(author_bsdf);expected['Sheen Tint']=[1.,1.,1.,1.]
   assert socket_defaults(copy_bsdf)==expected and sha(SOURCE)==SOURCE_SHA
   evbody=body.evaluated_get(bpy.context.evaluated_depsgraph_get()).data;assert evbody.materials[0].original==coat
  invariants();r['zero_factor_control']=dict(structural_original_surface_identity=True,effective_mask_all_zero=True,pixel_identity_rendered=False,eval_body_and_groom_geometry_bit_exact=True,all_groom_raw_and_evaluated_attributes_bit_exact=True,BindUV_and_active_UV_bit_exact=True,evaluated_hair_material_original_id_exact=True)
  save('factor-zero-shader-identity-and-geometry-binding-invariants-passed')
  factor.outputs[0].default_value=1;body.update_tag();bpy.context.view_layer.update();invariants()
  adaptations=['BSDF Base Color receives original Miao Mix(Legacy).001 Color instead of the source red diffuse image','BSDF Sheen Tint changed from source pink to neutral white(1,1,1,1), preserving all non-color reflection inputs']
  r.update(blender=bpy.app.version_string,source_preset_sha256=sha(LIB),source_preset_schema_sha256=sha(out/'author-original-schema.json'),author_original_bsdf_inputs=socket_defaults(author_bsdf),copied_bsdf_inputs=socket_defaults(copy_bsdf),author_reflection_structure_and_noncolor_inputs_unchanged=True,color_adaptations=adaptations,only_bsdf_link_change='Base Color now receives original Miao Mix(Legacy).001 Color; original diffuse image disconnected from BSDF',author_sheen_tint_before=value(author_bsdf.inputs['Sheen Tint'].default_value),adapted_sheen_tint=value(copy_bsdf.inputs['Sheen Tint'].default_value),author_sheen_weight=float(author_bsdf.inputs['Sheen Weight'].default_value),images=images,uv=dict(name=UV,method='planar actual C28 body XZ; UV=(X/(3*authorMappingScaleX),Z/(3*authorMappingScaleY)); unchanged authorMapping gives final image(X/3,Z/3)',assumed_meters_per_scene_unit=.1,texture_physical_tile_meters=.3,final_tile_scene_units=3,author_mapping_scale=scale.tolist(),normal_map_uv=copied['Normal Map.001'].uv_map,tangent_uv=copied['Tangent'].uv_map,old_maps_and_active_binding_unchanged=True),mask=dict(roi=roi.tolist(),fade_x=.025,fade_y=.006,visible_vertices=int(np.count_nonzero(weights)),full_vertices=int((weights==1).sum()),definition='actual front body visibility; same projected forehead ROI and fade as C24/C26/C28'),groom=dict(curves=186125,points=len(hairpos),eval_geometry_sha256=digest(hairpos),all_positions_roots_length_radius_rest_uv_and_hair_material_exact=True),body_geometry_displacement_unchanged=True,source_unchanged=True,limits=['One author velour substrate treatment; no sheen/scale/normal sweep.','Two explicit color adaptations only: original Miao BaseColor and neutral SheenTint; non-color reflection parameters and textures unchanged.','Planar UV and NormalMap/Tangent binding are explicit; BindUV unchanged.','Factor0 is structural shader identity, not a rendered pixel-identity claim.','Single fixed forehead substrate still, no whole-character/animation/production pass, fees or publication.'])
  new_provenance=dict(**provenance,verified_files=verified,experiment='C34 forehead substrate only, original Miao pigment replaces source diffuse color and neutral SheenTint, no displacement',color_adaptations=adaptations,powered_by='Powered by Poly Haven',authors=['colormass (photography)','Rico Cilliers (processing)'],upstream_provenance_sha256=sha(ASSETS/'provenance.json'))
  (out/'provenance.json').write_text(json.dumps(new_provenance,indent=2)+'\n');save('actual-preset-color-uv-groom-material-invariants-passed-before-render')
  native=out/'miao-c34-velour-substrate-patch.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);r['native_sha256']=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));hair=bpy.data.objects['Miao / native short plush'];assert digest(H.coords(hair,True))==r['groom']['eval_geometry_sha256'];r['native_reopen_groom_exact']=True
  renderer=ROOT/'artifacts/character-plush-readable-c28/controlled-native-run/samebuffer-render.py';text=renderer.read_text();old=str(SOURCE.relative_to(ROOT));assert text.count(old)==1;text=text.replace(old,str(native.relative_to(ROOT)));script=out/'samebuffer-render.py';script.write_text(text);r['renderer_sha256']=sha(script);save('native-saved-reopened-verified-awaiting-matched-render')
  if a.render:
   ns={'__file__':str(script),'__name__':'c34_renderer'};exec(compile(text,str(script),'exec'),ns);oldargv=sys.argv[:];sys.argv=[str(script),'--','--out',str(out/'render'),'--samples','128','--coverage']
   try:ns['main']()
   finally:sys.argv=oldargv
   rr=json.loads((out/'render/receipt.json').read_text());r.update(actual_render_calls=1,render_receipt_sha256=sha(out/'render/receipt.json'),fiber_aov=rr['fiber_aov'],render_seconds=rr['seconds']);save('matched-render-completed-awaiting-actual-image-and-independent-review')
  assert sha(SOURCE)==SOURCE_SHA and sha(native)==r['native_sha256'];print('RESULT '+json.dumps(r),flush=True)
 except Exception as ex:r.update(error=repr(ex),traceback=traceback.format_exc());save('stopped-before-further-work');raise
if __name__=='__main__':main()
