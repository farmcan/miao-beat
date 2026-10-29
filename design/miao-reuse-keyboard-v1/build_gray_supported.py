"""Bounded environment support repair. Frozen cat, keyboard and native-joint pose.
Mature CC0 table receives ONE uniform scale/translation; ground is ordinary environment.
"""
import bpy,json,hashlib,math,array
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];A=R/'artifacts/miao-reuse-keyboard-v1';S=A/'render-quality-diagnostic/native-render2-working36.blend';T=R/'artifacts/licensed-keyboard-support-2026-10-30/communal-work-table.glb';O=A/'gray-supported';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inputs={str(p):sha(p) for p in [S,T]};fit=json.load(open(A/'support-prop/render2-matched-proxy-fit.json'))
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);sc=bpy.context.scene;rig=bpy.data.objects['RIG-Cat'];pose=lambda:hashlib.sha256(json.dumps([(b.name,[list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest();ph=pose();assert ph==fit['pose_sha256'];assert not sc.render.use_simplify;assert rig.pose.bones['Properties_Character_Cat']['Quality']==1;action_before=len(bpy.data.actions)
propnames=[o['name'] for o in json.load(open(A/'prop/prop-receipt.json'))['objects']];props=[bpy.data.objects[n] for n in propnames];cat=[o for o in sc.objects if o.type=='MESH' and o not in props]
def basehash(objects):
 h=hashlib.sha256()
 for o in sorted(objects,key=lambda x:x.name):
  h.update(o.name.encode());h.update(array.array('f',[c for v in o.data.vertices for c in v.co]).tobytes());h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode())
 return h.hexdigest()
base_before=basehash(cat+props);kbdmat={o.name:[list(v) for v in o.matrix_world] for o in props};rigmatrix=[list(v) for v in rig.matrix_world]
def geom(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();p=[e.matrix_world@v.co for v in m.vertices];t=[tuple(t.vertices) for t in m.loop_triangles];e.to_mesh_clear();return p,t
def bounds(p):return {'min':[min(v[i] for v in p) for i in range(3)],'max':[max(v[i] for v in p) for i in range(3)]}
kp=[v for o in props for v in geom(o)[0]];kb=bounds(kp);floor=fit['render_aligned_floor']['z'];old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(T));table=[o for o in sc.objects if o not in old and o.type=='MESH'];raw={o.name:o.matrix_world.copy() for o in table};tp=[v for o in table for v in geom(o)[0]];tb=bounds(tp);height=tb['max'][2]-tb['min'][2];scale=(kb['min'][2]-floor)/height
M=Matrix.Scale(scale,4);M.translation=Vector(((kb['min'][0]+kb['max'][0])/2-scale*(tb['min'][0]+tb['max'][0])/2,(kb['min'][1]+kb['max'][1])/2-scale*(tb['min'][1]+tb['max'][1])/2,floor-scale*tb['min'][2]));source_names={}
for o in table:
 name=o.name;source_names['SUPPORT-'+name]=name;o.matrix_world=M@raw[name];o.name='SUPPORT-'+name;o['source_geometry_object']=name
bpy.context.view_layer.update();table_records=[];alltable=[]
for o in table:
 p,t=geom(o);alltable+=p;table_records.append({'name':o.name,'p':p,'t':t,'bbox':bounds(p),'tree':BVHTree.FromPolygons(p,t,all_triangles=True)})
supported_bb=bounds(alltable)
# Render-matched unsaved proxy for cat/table finite collision check; restore before all renders/save.
saved=[];drivers=[];gn=[]
for o in sc.objects:
 for f in o.animation_data.drivers if o.animation_data else []:
  if 'modifiers[' in f.data_path and f.data_path.endswith('].levels'):drivers.append((f,f.mute));f.mute=True
 for m in o.modifiers:
  saved.append((m,m.show_viewport,m.levels if m.type=='SUBSURF' else None));m.show_viewport=m.show_render
  if m.type=='SUBSURF':m.levels=m.render_levels
for group in bpy.data.node_groups:
 for node in list(group.nodes):
  if node.bl_idname=='GeometryNodeIsViewport':
   links=[(l.from_socket,l.to_socket) for l in list(group.links) if l.from_node==node];const=group.nodes.new('FunctionNodeInputBool');const.boolean=False
   for src,dst in links:
    for link in list(group.links):
     if link.from_socket==src and link.to_socket==dst:group.links.remove(link)
    group.links.new(const.outputs[0],dst)
   gn.append((group,const,links))
bpy.context.view_layer.update();collisions={};checked=[];catbboxes={}
for o in cat:
 if o.hide_render or not o.visible_get() or o.name.startswith('WGT'):continue
 p,t=geom(o)
 if not p or not t:continue
 bb=bounds(p);catbboxes[o.name]=bb;checked.append(o.name);tree=None;hits={}
 for rec in table_records:
  if all(bb['max'][i]>=rec['bbox']['min'][i] and rec['bbox']['max'][i]>=bb['min'][i] for i in range(3)):
   if tree is None:tree=BVHTree.FromPolygons(p,t,all_triangles=True)
   inter=tree.overlap(rec['tree'])
   if inter:hits[rec['name']]=len(inter)
 if hits:collisions[o.name]=hits
for group,const,links in gn:
 group.nodes.remove(const)
 for src,dst in links:group.links.new(src,dst)
for m,visible,levels in saved:
 m.show_viewport=visible
 if levels is not None:m.levels=levels
for f,state in drivers:f.mute=state
bpy.context.view_layer.update()
# Check the real two oak banks support the fixed keyboard bottom; source trough is preserved.
banks=[r for r in table_records if 'Shared oak worktop bank' in r['name']];support_samples=[]
for x in [kb['min'][0]+.04,(kb['min'][0]+kb['max'][0])/2,kb['max'][0]-.04]:
 for y in [(kb['min'][1]+kb['max'][1])/2-.065,(kb['min'][1]+kb['max'][1])/2+.065]:
  surfaces=[]
  for rec in banks:
   hit,_,_,_=rec['tree'].ray_cast(Vector((x,y,2)),Vector((0,0,-1)),3)
   if hit is not None:surfaces.append(hit.z)
  assert surfaces;top=max(surfaces);support_samples.append({'xy':[x,y],'table_top_z':top,'keyboard_bottom_z':kb['min'][2],'gap_m':kb['min'][2]-top})
glides=[{'name':r['name'],'floor_min_z':r['bbox']['min'][2],'gap_m':r['bbox']['min'][2]-floor} for r in table_records if 'Leveling glide' in r['name']]
assert len(glides)==6;assert max(abs(x['gap_m']) for x in glides)<1e-6;assert max(abs(x['gap_m']) for x in support_samples)<1e-6;assert not collisions
# Plain original project environment ground, no new character/prop modeling.
mesh=bpy.data.meshes.new('ENV-GROUND-MESH');mesh.from_pydata([(-5,-5,floor),(5,-5,floor),(5,5,floor),(-5,5,floor)],[],[(0,1,2,3)]);mesh.update();ground=bpy.data.objects.new('ENV-GROUND',mesh);sc.collection.objects.link(ground);mat=bpy.data.materials.new('ENV-GROUND-NEUTRAL');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.52,.52,.52,1);bs.inputs['Roughness'].default_value=.8;mesh.materials.append(mat)
sc.eevee.use_gtao=True;sc.eevee.gtao_distance=.08;sc.eevee.gtao_factor=1.05;sc.eevee.use_soft_shadows=True
for o in sc.objects:
 if o.type=='LIGHT':o.data.use_shadow=True;o.data.use_contact_shadow=True;o.data.contact_shadow_distance=.35;o.data.contact_shadow_bias=.01;o.data.contact_shadow_thickness=.02
assert pose()==ph;assert basehash(cat+props)==base_before;assert kbdmat=={o.name:[list(v) for v in o.matrix_world] for o in props};assert rigmatrix==[list(v) for v in rig.matrix_world]
receipt={'status':'GRAY_SUPPORTED_PENDING_THREE_REVIEWS','inputs':inputs,'blender':bpy.app.version_string,'pose_sha256':ph,'Quality':rig.pose.bones['Properties_Character_Cat']['Quality'],'render_use_simplify':sc.render.use_simplify,'render_subsurf_setting':2,'render_geometry_measurement':'independent render-aligned proxy, show_render/render_levels; IsViewport=False; not direct render depsgraph','render2_contact_receipt':str(A/'support-prop/render2-matched-proxy-fit.json'),'render2_target_gap_mm':{s:1000*v['target_white_vertical_gap_m'] for s,v in fit['hands'].items()},'cat_keyboard_base_geometry_sha_before':base_before,'cat_keyboard_base_geometry_sha_after':basehash(cat+props),'keyboard_matrices_unchanged':True,'rig_matrix_unchanged':True,'table_source_sha256':inputs[str(T)],'table_original_bbox':tb,'table_uniform_scale':scale,'table_matrix':[list(v) for v in M],'table_bbox':supported_bb,'table_size_m':[supported_bb['max'][i]-supported_bb['min'][i] for i in range(3)],'floor_z_m':floor,'table_six_glides':glides,'actual_keyboard_support_samples':support_samples,'cat_vs_table_finite_triangle_intersections':collisions,'cat_objects_checked':checked,'cat_render_aligned_bboxes':catbboxes,'table_meshes':len(table),'source_table_geometry_modified':False,'new_environment_geometry':'single ordinary ground plane only; mature table unchanged except common uniform transform','new_actions':len(bpy.data.actions)-action_before,'renders':[],'camera_helper_errors':[]}
cam=sc.camera;helper=bpy.data.objects['HLP-scene_camera_dummy'];sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
views=[('front',(0,-3,1.50),(0,-.13,.53),1.38,(1400,1400)),('three-quarter',(.95,-2.5,1.3),(0,-.13,.53),1.38,(1400,1400)),('face',(.30,-2.0,1.13),(0,-.08,.79),.74,(1100,1100)),('left-hand',(.40,-.85,.83),(.08,-.28,.35),.32,(1200,1000)),('right-hand',(-.40,-.85,.83),(-.08,-.28,.35),.32,(1200,1000)),('hands-top',(0,-.35,1.25),(0,-.30,.33),.48,(1400,1000)),('feet-support',(.80,-1.6,.52),(0,-.25,.12),1.10,(1400,1000)),('support-side',(1.8,-.15,.85),(0,-.30,.48),1.38,(1400,1400))]
for name,loc,target,ortho,res in views:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=ortho;sc.render.resolution_x,sc.render.resolution_y=res;bpy.context.view_layer.update();helper.rotation_euler=cam.matrix_world.to_euler();helper.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();err=max(abs(helper.rotation_euler[i]-cam.matrix_world.to_euler()[i]) for i in range(3));assert err<1e-6
 sc.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);assert pose()==ph;receipt['renders'].append(sc.render.filepath);receipt['camera_helper_errors'].append({'view':name,'max_error':err})
cam.location=views[0][1];cam.rotation_euler=(Vector(views[0][2])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=views[0][3];sc.render.resolution_x,sc.render.resolution_y=views[0][4];bpy.context.view_layer.update();helper.rotation_euler=cam.matrix_world.to_euler();bpy.context.view_layer.update();sc.render.filepath=str(O/'front.png')
for i in bpy.data.images:
 if i.type=='IMAGE' and not i.packed_file:
  try:i.pack()
  except RuntimeError:pass
native=O/'keyboard-supported-native36.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));receipt['native']=str(native);receipt['native_sha256']=sha(native);receipt['source_sha256_after']={str(p):sha(p) for p in [S,T]};assert receipt['source_sha256_after']==inputs;assert receipt['new_actions']==0;assert pose()==ph
(O/'supported-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('GRAY_SUPPORTED_READY',json.dumps({k:receipt[k] for k in ['native','pose_sha256','table_uniform_scale','table_size_m','floor_z_m','render2_target_gap_mm','cat_vs_table_finite_triangle_intersections','new_actions']}))
