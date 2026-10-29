"""Six gray review views of the one isolated eight-key static candidate.

The cat identity remains unaccepted. No animation, new geometry or key pose is
authored here; this gate is limited to retaining/rejecting the prop adaptation.
"""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe_eight_key_layout import pose_hash, source_mesh_hash

BASE = ROOT/'artifacts/miao-eight-key-prop-probe-2026-10-30'
SOURCE = BASE/'eight-key-isolated-static-native36.blend'
OUT = BASE/'gray-gate'
EXPECTED = '7179aa5967c7d01c735e63bfb419b3f69825b9fdd944d4f0ec230f740724b70e'
POSE = '40d5a61366db61d6149ad01d26f5ce4310dead1a7951fc5098620b5e1a7ae3fb'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert bpy.app.version[:2]==(3,6)
    assert sha(SOURCE)==EXPECTED
    if '--verify' in sys.argv:
        manifest=json.loads((OUT/'inspection-manifest.json').read_text())
        native=ROOT/manifest['native']
        assert sha(native)==manifest['native_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        scene=bpy.context.scene
        rig=bpy.data.objects['RIG-Cat']
        assert pose_hash(rig)==POSE
        assert source_mesh_hash()==manifest['source_base_meshes_material_slots_hash_before']
        assert not scene.render.use_simplify
        assert rig.pose.bones['Properties_Character_Cat']['Quality']==1
        assert len(bpy.data.actions)==27
        assert all(sha(ROOT/item['file'])==item['sha256'] for item in manifest['renders'])
        gray=scene.node_tree.nodes['EightKeyGrayReview']
        assert any(l.to_node==gray and l.from_node.bl_idname=='CompositorNodeRLayers' for l in scene.node_tree.links)
        assert any(l.from_node==gray and l.to_node.bl_idname=='CompositorNodeComposite' for l in scene.node_tree.links)
        helper=bpy.data.objects['HLP-scene_camera_dummy']
        bpy.context.view_layer.update()
        error=max(abs(helper.rotation_euler[i]-scene.camera.matrix_world.to_euler()[i]) for i in range(3))
        assert error<1e-6
        result={'status':'GRAY_NATIVE_REOPEN_PASS','native_sha256':sha(native),'pose_sha256':POSE,
                'base_meshes_material_slots_sha256':source_mesh_hash(),'gray_compositor_preserved':True,
                'image_hashes_verified':len(manifest['renders']),'camera_helper_axis_error':error,
                'original_actions_count':len(bpy.data.actions),'new_actions':0,'Quality':1,
                'source_sha256_after':sha(SOURCE),'not_an_art_approval':True}
        (OUT/'native-reopen-verification.json').write_text(json.dumps(result,indent=2)+'\n')
        print('RESULT '+json.dumps(result))
        return
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    rig=bpy.data.objects['RIG-Cat']
    assert pose_hash(rig)==POSE
    assert not scene.render.use_simplify
    assert rig.pose.bones['Properties_Character_Cat']['Quality']==1
    mesh_hash=source_mesh_hash()
    actions=len(bpy.data.actions)
    material_count=len(bpy.data.materials)
    levels={o.name:[m.render_levels for m in o.modifiers if m.type=='SUBSURF'] for o in scene.objects if o.type=='MESH'}
    scene.use_nodes=True
    tree=scene.node_tree
    source=next(n for n in tree.nodes if n.bl_idname=='CompositorNodeRLayers')
    output=next(n for n in tree.nodes if n.bl_idname=='CompositorNodeComposite')
    gray=tree.nodes.get('EightKeyGrayReview') or tree.nodes.new('CompositorNodeRGBToBW')
    gray.name='EightKeyGrayReview'
    for link in list(tree.links):
        if link.to_node==output and link.to_socket==output.inputs['Image']:tree.links.remove(link)
    tree.links.new(source.outputs['Image'],gray.inputs['Image'])
    tree.links.new(gray.outputs[0],output.inputs['Image'])
    camera=scene.camera
    helper=bpy.data.objects['HLP-scene_camera_dummy']
    for driver in helper.animation_data.drivers:
        if driver.data_path=='rotation_euler':driver.mute=True
    views=[
        ('front',(0,-3,1.5),(0,-.13,.53),1.38,(1000,1000)),
        ('three-quarter',(.95,-2.5,1.3),(0,-.13,.53),1.38,(1000,1000)),
        ('left-hand',(.53,-.85,.83),(.235,-.28,.352),.34,(1000,800)),
        ('right-hand',(-.53,-.85,.83),(-.235,-.28,.352),.34,(1000,800)),
        ('key-front-edge',(.70,-.12,.28),(0,-.36,.32),.70,(1000,800)),
        ('key-rear',(.40,-1.0,.48),(0,-.40,.33),.65,(1000,800)),
    ]
    OUT.mkdir(exist_ok=True)
    rendered=[]
    for name,location,target,scale,resolution in views:
        camera.location=location
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.type='ORTHO'
        camera.data.ortho_scale=scale
        scene.render.resolution_x,scene.render.resolution_y=resolution
        scene.render.resolution_percentage=100
        bpy.context.view_layer.update()
        helper.rotation_euler=camera.matrix_world.to_euler()
        helper.update_tag(refresh={'OBJECT'})
        bpy.context.view_layer.update()
        error=max(abs(helper.rotation_euler[i]-camera.matrix_world.to_euler()[i]) for i in range(3))
        assert error<1e-6
        path=OUT/(name+'.png')
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        assert pose_hash(rig)==POSE
        rendered.append({'view':name,'file':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size,'camera_helper_axis_error':error})
    camera.location=views[0][1]
    camera.rotation_euler=(Vector(views[0][2])-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=views[0][3]
    scene.render.resolution_x,scene.render.resolution_y=views[0][4]
    bpy.context.view_layer.update()
    helper.rotation_euler=camera.matrix_world.to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath=str(OUT/'front.png')
    assert source_mesh_hash()==mesh_hash
    assert len(bpy.data.actions)==actions and len(bpy.data.materials)==material_count
    assert levels=={o.name:[m.render_levels for m in o.modifiers if m.type=='SUBSURF'] for o in scene.objects if o.type=='MESH'}
    native=OUT/'eight-key-gray-static-native36.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    report={'status':'GRAY_PENDING_THREE_NON_BUILDER_REVIEWS','scope':'Only eight-key static prop assembly. Entire character identity/production art remains HOLD. No animation or web expansion.',
            'source':str(SOURCE.relative_to(ROOT)),'source_sha256_before':EXPECTED,'source_sha256_after':sha(SOURCE),
            'native':str(native.relative_to(ROOT)),'native_sha256':sha(native),'pose_sha256':POSE,
            'blender':bpy.app.version_string,'renders':rendered,
            'source_base_meshes_material_slots_hash_before':mesh_hash,'source_base_meshes_material_slots_hash_after':source_mesh_hash(),
            'Quality':1,'render_use_simplify':False,'render_subdivision_levels':levels,
            'source_materials_retained':True,'gray_method':'native compositor RGBToBW, no material replacement',
            'new_actions':len(bpy.data.actions)-actions,'new_meshes':0,'new_pose_after_probe':False,
            'technical_probe':'artifacts/miao-eight-key-prop-probe-2026-10-30/candidate-probe.json',
            'source_hidden_black_white_key_intersections':'inherited, not reclassified or removed; previous near-boundary unknowns remain',
            'direct_render_depsgraph':'not available; matched-proxy numeric checks remain limited',
            'animation_created_or_approved':False,'public_changed':False}
    assert report['source_sha256_before']==report['source_sha256_after']
    (OUT/'inspection-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RESULT '+json.dumps({'status':report['status'],'native_sha256':report['native_sha256'],'pose_sha256':POSE,'views':len(rendered),'new_actions':0}))


if __name__=='__main__':
    main()
