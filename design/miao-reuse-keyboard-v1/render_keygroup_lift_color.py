"""Same frozen supported pose and original palette: bypass native gray compositor only."""
import bpy,json,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];A=R/'artifacts/miao-reuse-keyboard-v1';S=A/'v2-keygroup-lift/keygroup-lift-gray-native36.blend';O=A/'v2-keygroup-lift-color';O.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(S);assert before=='bf893762d45c3210c845c28d8c290eb7d720fc875a089bbfda109349e61be28f'
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);sc=bpy.context.scene;rig=bpy.data.objects['RIG-Cat'];quality=rig.pose.bones['Properties_Character_Cat']['Quality'];assert quality==1 and not sc.render.use_simplify
pose=lambda:hashlib.sha256(json.dumps([(b.name,[list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest();ph=pose();assert ph=='6a034f30f3f848c4cd7833da9e86834d895a636bfed170d5cd5fbd16d7b5049b';actions=len(bpy.data.actions)
def basehash():
 h=hashlib.sha256()
 for o in sorted((o for o in sc.objects if o.type=='MESH'),key=lambda o:o.name):
  h.update(o.name.encode());h.update(array.array('f',[c for v in o.data.vertices for c in v.co]).tobytes());h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode());h.update(str([m.name if m else None for m in o.data.materials]).encode())
 return h.hexdigest()
def graphhash():
 r=[]
 for m in sorted(bpy.data.materials,key=lambda m:m.name):
  if m.use_nodes:r.append((m.name,[(n.name,n.bl_idname) for n in m.node_tree.nodes],[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links]))
 return hashlib.sha256(json.dumps(r).encode()).hexdigest()
mesh_before=basehash();materials_before=graphhash();fixed=[o for o in sc.objects if o.name not in {sc.camera.name,'HLP-scene_camera_dummy'}];world_before={o.name:[list(v) for v in o.matrix_world] for o in fixed}

# Only appearance change: bypass RGBToBW and retain original material outputs.
assert sc.use_nodes;nt=sc.node_tree;rl=next(n for n in nt.nodes if n.bl_idname=='CompositorNodeRLayers');out=next(n for n in nt.nodes if n.bl_idname=='CompositorNodeComposite');before_links=[(l.from_node.bl_idname,l.to_node.bl_idname) for l in nt.links]
for l in list(nt.links):
 if l.to_node==out and l.to_socket==out.inputs['Image']:nt.links.remove(l)
nt.links.new(rl.outputs['Image'],out.inputs['Image']);after_links=[(l.from_node.bl_idname,l.to_node.bl_idname) for l in nt.links]
cam=sc.camera;helper=bpy.data.objects['HLP-scene_camera_dummy'];renders=[];errors=[]
views=[('front',(0,-3,1.5),(0,-.13,.53),1.38,(1400,1400)),('three-quarter',(.95,-2.5,1.3),(0,-.13,.53),1.38,(1400,1400)),('face',(.30,-2,1.13),(0,-.08,.79),.74,(1100,1100)),('left-hand',(.40,-.85,.83),(.08,-.28,.352),.32,(1200,1000)),('right-hand',(-.40,-.85,.83),(-.08,-.28,.352),.32,(1200,1000)),('key-rear',(.23,-.60,.48),(.057,-.413,.325),.18,(1400,1000)),('key-front-edge',(.25,-.14,.29),(.057,-.303,.316),.19,(1400,1000)),('feet-support',(.8,-1.6,.52),(0,-.25,.12),1.10,(1400,1000)),('support-side',(1.8,-.15,.85),(0,-.30,.48),1.38,(1400,1400))]
for name,loc,target,ortho,res in views:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=ortho;sc.render.resolution_x,sc.render.resolution_y=res;sc.render.resolution_percentage=100;bpy.context.view_layer.update();helper.rotation_euler=cam.matrix_world.to_euler();helper.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();err=max(abs(helper.rotation_euler[i]-cam.matrix_world.to_euler()[i]) for i in range(3));assert err<1e-6
 sc.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);assert pose()==ph;renders.append(sc.render.filepath);errors.append({'view':name,'max_error':err})
cam.location=views[0][1];cam.rotation_euler=(Vector(views[0][2])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=views[0][3];sc.render.resolution_x,sc.render.resolution_y=views[0][4];bpy.context.view_layer.update();helper.rotation_euler=cam.matrix_world.to_euler();bpy.context.view_layer.update();sc.render.filepath=str(O/'front.png')
assert basehash()==mesh_before and graphhash()==materials_before;assert world_before=={o.name:[list(v) for v in o.matrix_world] for o in fixed};assert pose()==ph and len(bpy.data.actions)==actions;assert rig.pose.bones['Properties_Character_Cat']['Quality']==quality and not sc.render.use_simplify
native=O/'keygroup-lift-color-native36.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));r={'status':'DEFAULT_COLOR_PENDING_THREE_NON_BUILDER_REVIEWS','source':str(S),'source_sha256_before':before,'source_sha256_after':sha(S),'native':str(native),'native_sha256':sha(native),'blender':bpy.app.version_string,'pose_sha256':ph,'all_mesh_material_slot_hash_before':mesh_before,'all_mesh_material_slot_hash_after':basehash(),'material_graph_hash_before':materials_before,'material_graph_hash_after':graphhash(),'all_world_matrices_except_camera_helper_unchanged':True,'key_count':len([o for o in sc.objects if o.type=='MESH' and o.name.startswith(('Ivory piano key','Raised black piano key'))]),'Quality':quality,'use_simplify':sc.render.use_simplify,'renderer':'unchanged EEVEE 3.6, original render_levels2','only_change':'compositor RGBToBW bypass; original CCBYcat + CC0keyboard/table PBR palette retained, no recolor','compositor_links_before':before_links,'compositor_links_after':after_links,'camera_helper_errors':errors,'renders':renders,'actions_before':actions,'actions_after':len(bpy.data.actions),'new_actions':0,'new_keyframes':0,'new_pose_library_applied':False,'motion_or_press':'not made or accepted','contact_audit_reference':str(A/'v2-keygroup-lift/lift-probe-receipt.json'),'direct_render_depsgraph':'unavailable; previous matched-proxy boundary unchanged'};assert r['source_sha256_before']==r['source_sha256_after'];(O/'default-color-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('DEFAULT_COLOR_READY',json.dumps({k:r[k] for k in ['native','native_sha256','pose_sha256','new_actions','only_change']}))
