"""Restore original color on the approved eight-key gray assembly, same six views.

This is only the prop/ready-pose shaded gate. The complete Miao character remains
on production identity HOLD. No pose, geometry, light or animation is changed.
"""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe_eight_key_layout import pose_hash, source_mesh_hash

BASE=ROOT/'artifacts/miao-eight-key-prop-probe-2026-10-30'
SOURCE=BASE/'gray-gate/eight-key-gray-static-native36.blend'
OUT=BASE/'color-gate'
EXPECTED='42eae3f8eee59f60eeb8d1194f6d979ae55cf0e3140271eb5453be1b32c2fda8'
POSE='40d5a61366db61d6149ad01d26f5ce4310dead1a7951fc5098620b5e1a7ae3fb'
VIEWS=[
    ('front',(0,-3,1.5),(0,-.13,.53),1.38,(1000,1000)),
    ('three-quarter',(.95,-2.5,1.3),(0,-.13,.53),1.38,(1000,1000)),
    ('left-hand',(.53,-.85,.83),(.235,-.28,.352),.34,(1000,800)),
    ('right-hand',(-.53,-.85,.83),(-.235,-.28,.352),.34,(1000,800)),
    ('key-front-edge',(.70,-.12,.28),(0,-.36,.32),.70,(1000,800)),
    ('key-rear',(.40,-1.0,.48),(0,-.40,.33),.65,(1000,800)),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def world_except_camera(scene):
    ignored={scene.camera.name,'HLP-scene_camera_dummy'}
    return {o.name:[list(row) for row in o.matrix_world] for o in scene.objects if o.name not in ignored}


def lights(scene):
    return {o.name:{'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color)} for o in scene.objects if o.type=='LIGHT'}


def material_graphs():
    values=[]
    for mat in sorted(bpy.data.materials,key=lambda m:m.name):
        if mat.use_nodes:
            values.append((mat.name,[(n.name,n.bl_idname) for n in mat.node_tree.nodes],[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in mat.node_tree.links]))
    return hashlib.sha256(json.dumps(values).encode()).hexdigest()


def assert_original_color(scene):
    output=next(n for n in scene.node_tree.nodes if n.bl_idname=='CompositorNodeComposite')
    links=[l for l in scene.node_tree.links if l.to_node==output and l.to_socket==output.inputs['Image']]
    assert len(links)==1 and links[0].from_node.bl_idname=='CompositorNodeRLayers'


def main():
    assert bpy.app.version[:2]==(3,6) and sha(SOURCE)==EXPECTED
    OUT.mkdir(exist_ok=True)
    if '--verify' in sys.argv:
        manifest=json.loads((OUT/'inspection-manifest.json').read_text())
        native=ROOT/manifest['native']
        assert sha(native)==manifest['native_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        scene=bpy.context.scene;rig=bpy.data.objects['RIG-Cat']
        assert pose_hash(rig)==POSE and source_mesh_hash()==manifest['base_meshes_material_slots_sha256']
        assert material_graphs()==manifest['material_graphs_sha256']
        assert len(bpy.data.actions)==manifest['original_action_count']==27
        assert world_except_camera(scene)==manifest['fixed_world_matrices'] and lights(scene)==manifest['lights']
        assert rig.pose.bones['Properties_Character_Cat']['Quality']==1 and not scene.render.use_simplify
        assert_original_color(scene)
        assert all(sha(ROOT/item['file'])==item['sha256'] for item in manifest['renders'])
        bpy.context.view_layer.update();helper=bpy.data.objects['HLP-scene_camera_dummy']
        error=max(abs(helper.rotation_euler[i]-scene.camera.matrix_world.to_euler()[i]) for i in range(3));assert error<1e-6
        result={'status':'COLOR_NATIVE_REOPEN_PASS','native_sha256':sha(native),'pose_sha256':POSE,'base_meshes_material_slots_sha256':source_mesh_hash(),'material_graphs_sha256':material_graphs(),'same_world_except_camera_helper':True,'lights_unchanged':True,'original_color_link_restored':True,'image_hashes_verified':len(manifest['renders']),'camera_helper_axis_error':error,'new_actions':0,'source_sha256_after':sha(SOURCE),'not_an_art_or_motion_approval':True}
        (OUT/'native-reopen-verification.json').write_text(json.dumps(result,indent=2)+'\n')
        print('RESULT '+json.dumps(result));return
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;rig=bpy.data.objects['RIG-Cat']
    assert pose_hash(rig)==POSE and not scene.render.use_simplify and rig.pose.bones['Properties_Character_Cat']['Quality']==1
    base_meshes=source_mesh_hash();graphs=material_graphs();fixed=world_except_camera(scene);lighting=lights(scene);action_count=len(bpy.data.actions)
    levels={o.name:[m.render_levels for m in o.modifiers if m.type=='SUBSURF'] for o in scene.objects if o.type=='MESH'}
    assert scene.use_nodes
    tree=scene.node_tree;rl=next(n for n in tree.nodes if n.bl_idname=='CompositorNodeRLayers');output=next(n for n in tree.nodes if n.bl_idname=='CompositorNodeComposite')
    for link in list(tree.links):
        if link.to_node==output and link.to_socket==output.inputs['Image']:tree.links.remove(link)
    tree.links.new(rl.outputs['Image'],output.inputs['Image']);assert_original_color(scene)
    camera=scene.camera;helper=bpy.data.objects['HLP-scene_camera_dummy'];rendered=[]
    assert all(d.mute for d in helper.animation_data.drivers if d.data_path=='rotation_euler')
    for name,location,target,scale,resolution in VIEWS:
        camera.location=location;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=scale
        scene.render.resolution_x,scene.render.resolution_y=resolution;scene.render.resolution_percentage=100
        bpy.context.view_layer.update();helper.rotation_euler=camera.matrix_world.to_euler();helper.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
        error=max(abs(helper.rotation_euler[i]-camera.matrix_world.to_euler()[i]) for i in range(3));assert error<1e-6
        path=OUT/(name+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);assert pose_hash(rig)==POSE
        rendered.append({'view':name,'file':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size,'camera_location':list(location),'camera_target':list(target),'camera_ortho_scale':scale,'resolution':list(resolution),'camera_helper_axis_error':error})
    camera.location=VIEWS[0][1];camera.rotation_euler=(Vector(VIEWS[0][2])-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=VIEWS[0][3]
    scene.render.resolution_x,scene.render.resolution_y=VIEWS[0][4];scene.render.filepath=str(OUT/'front.png');bpy.context.view_layer.update();helper.rotation_euler=camera.matrix_world.to_euler();bpy.context.view_layer.update()
    assert source_mesh_hash()==base_meshes and material_graphs()==graphs and world_except_camera(scene)==fixed and lights(scene)==lighting and len(bpy.data.actions)==action_count
    assert levels=={o.name:[m.render_levels for m in o.modifiers if m.type=='SUBSURF'] for o in scene.objects if o.type=='MESH'}
    native=OUT/'eight-key-color-static-native36.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
    result={'status':'SHADED_PENDING_THREE_NON_BUILDER_REVIEWS','scope':'Only eight-key prop and ready-pose assembly. Entire character production identity HOLD. No animation/web expansion.',
            'source':str(SOURCE.relative_to(ROOT)),'source_sha256_before':EXPECTED,'source_sha256_after':sha(SOURCE),'native':str(native.relative_to(ROOT)),'native_sha256':sha(native),'pose_sha256':POSE,
            'blender':bpy.app.version_string,'renders':rendered,'base_meshes_material_slots_sha256':base_meshes,'material_graphs_sha256':graphs,'fixed_world_matrices':fixed,'lights':lighting,
            'render_subdivision_levels':levels,'Quality':1,'render_use_simplify':False,'new_meshes':0,'original_action_count':action_count,'new_actions':0,
            'only_appearance_change':'bypass compositor RGBToBW; original source material outputs restored','same_six_camera_contract_as_gray':True,'new_pose':False,'source_hidden_black_white_key_intersections':'inherited; previous near-boundary unknowns remain','direct_render_depsgraph':'unavailable; matched-proxy numeric boundary unchanged','animation_created_or_approved':False,'public_changed':False}
    assert result['source_sha256_before']==result['source_sha256_after']
    (OUT/'inspection-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT '+json.dumps({'status':result['status'],'native_sha256':result['native_sha256'],'pose_sha256':POSE,'views':len(rendered),'new_actions':0}))


if __name__=='__main__':
    main()
