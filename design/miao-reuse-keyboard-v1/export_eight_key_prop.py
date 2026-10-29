"""Export only the 18 CC0 eight-key instrument parts; reimport and compare.

Internal authoring prop only, never a complete production cat frame or a motion
approval. The immutable shaded source and its cat/rig are not exported.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe_eight_key_layout import pose_hash, source_mesh_hash
from single_key_geometry import RenderMatchedProxy, bounds, geometry

BASE=ROOT/'artifacts/miao-eight-key-prop-probe-2026-10-30'
SOURCE=BASE/'color-gate/eight-key-color-static-native36.blend'
OUT=BASE/'prop-export'
EXPECTED='8bd535e772477f70d6ea85e208329b1aca7fff77fe6088185c442eaf5d442801'
POSE='40d5a61366db61d6149ad01d26f5ce4310dead1a7951fc5098620b5e1a7ae3fb'
PREFIX='EIGHTKEY__'
NAMES=(['Ivory piano key.'+str(i).zfill(3) for i in range(14,22)]
       +['Raised black piano key.'+str(i).zfill(3) for i in range(10,15)]
       +['Controller chassis','Top rotary control','Top rotary control.007',
         'Top control index','Top control index.007'])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_rows(mat):
    return [list(row) for row in mat]


def metric(obj):
    points,tris,_=geometry(obj)
    low,high=bounds(points)
    return {'name':obj.name,'world_matrix':matrix_rows(obj.matrix_world),
            'world_bbox':[low,high],'world_dimensions':[b-a for a,b in zip(low,high)],
            'top_z':high[2],'world_center':[(a+b)/2 for a,b in zip(low,high)],
            'triangles':len(tris),'material_slot_count':len(obj.data.materials),
            'materials':[m.name if m else None for m in obj.data.materials]},points


def nearest_max(a,b):
    tree=KDTree(len(b))
    for i,p in enumerate(b):tree.insert(p,i)
    tree.balance()
    return max(tree.find(p)[2] for p in a)


def read_glb(path):
    data=path.read_bytes()
    magic,version,length=struct.unpack_from('<III',data)
    assert magic==0x46546c67 and version==2 and length==len(data)
    json_length,json_type=struct.unpack_from('<II',data,12)
    assert json_type==0x4e4f534a
    return json.loads(data[20:20+json_length])


def write_note_map():
    receipt=json.loads((OUT/'reimport-verification.json').read_text())
    rows={item['source_name']:item for item in receipt['objects']}
    white=[]
    for i,(midi,note) in enumerate(zip([60,62,64,65,67,69,71,72],['C4','D4','E4','F4','G4','A4','B4','C5'])):
        name='Ivory piano key.'+str(14+i).zfill(3);item=rows[name]
        white.append({'playerAscendingIndex':i,'sourceName':name,'glbNodeName':item['export_name'],'midi':midi,'note':note,'blenderWorldBBoxCenterMeters':item['source']['world_center'],'blenderWorldTopZMeters':item['source']['top_z']})
    black=[]
    for name,item in rows.items():
        if not name.startswith('Raised black piano key'):continue
        x=item['source']['world_center'][0]
        pairs=[(a,b) for a,b in zip(white,white[1:]) if min(a['blenderWorldBBoxCenterMeters'][0],b['blenderWorldBBoxCenterMeters'][0])<x<max(a['blenderWorldBBoxCenterMeters'][0],b['blenderWorldBBoxCenterMeters'][0])]
        assert len(pairs)==1
        a,b=pairs[0];assert b['midi']-a['midi']==2
        midi=a['midi']+1
        black.append({'sourceName':name,'glbNodeName':item['export_name'],'midi':midi,'note':{61:'C#4',63:'D#4',66:'F#4',68:'G#4',70:'A#4'}[midi],'betweenWhiteSources':[a['sourceName'],b['sourceName']],'betweenWhiteMidi':[a['midi'],b['midi']],'blenderWorldBBoxCenterMeters':item['source']['world_center'],'blenderWorldTopZMeters':item['source']['top_z'],'derivedFromActualCenterGap':True})
    black.sort(key=lambda item:item['midi']);assert [b['midi'] for b in black]==[61,63,66,68,70]
    by_x=sorted(white,key=lambda item:item['blenderWorldBBoxCenterMeters'][0])
    assert [item['midi'] for item in by_x]==[72,71,69,67,65,64,62,60]
    result={'version':1,'purpose':'Read-only pitch semantics for the adapted instrument. No live inputs, animation or fingering instruction.',
            'sourceShadedNativeSha256':receipt['source_sha256_before'],'glbSha256':receipt['glb_sha256'],
            'coordinateSystem':'BBox centers and top values are Blender native world XYZ, meters. They are not glTF node translations.',
            'orientation':'Retains original fit Z180 orientation. Cat/player ascending C4-to-C5 is source white014-to021. Audience/front world-X ascending view is C5-to-C4; do not assign ascending pitch by world X.',
            'whitesPlayerAscending':white,'blacks':black,'audienceWorldXAscendingWhiteSources':[item['sourceName'] for item in by_x],
            'audienceWorldXAscendingWhiteMidi':[item['midi'] for item in by_x],'mapOnlyNotEightKeyActionApproval':True}
    (OUT/'note-map.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


def minimal_native():
    """Write only the verified imported Scene and its reachable CC0 dependencies."""
    receipt=json.loads((OUT/'reimport-verification.json').read_text())
    glb=ROOT/receipt['glb'];assert sha(glb)==receipt['glb_sha256'] and sha(SOURCE)==EXPECTED
    scene=bpy.data.scenes.new('EIGHTKEY_CC0_AUTHORING_PROP_ONLY')
    bpy.context.window.scene=scene
    bpy.ops.import_scene.gltf(filepath=str(glb))
    bpy.context.view_layer.update()
    assert len(scene.objects)==18 and all(o.type=='MESH' for o in scene.objects)
    assert {o.name for o in scene.objects}=={PREFIX+name for name in NAMES}
    for image in {n.image for o in scene.objects for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeTexImage' and n.image}:
        if not image.packed_file:image.pack()
    native=OUT/'eight-key-cc0-prop-native36.blend'
    # save_as_mainfile would include the original cat/hidden-key Scenes. A
    # dependency-only library write makes the artifact genuinely prop-only.
    bpy.data.libraries.write(str(native),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
    native_sha=sha(native)
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    counts={name:len(getattr(bpy.data,name)) for name in ['scenes','objects','meshes','materials','images','armatures','actions','cameras','lights','texts']}
    assert counts['scenes']==1 and counts['objects']==counts['meshes']==18 and counts['materials']==3
    assert all(counts[name]==0 for name in ['armatures','actions','cameras','lights','texts'])
    assert {o.name for o in scene.objects}=={PREFIX+name for name in NAMES}
    assert all(o.type=='MESH' and o.parent is None and not o.animation_data for o in scene.objects)
    assert len(bpy.data.images)==4 and all(i.packed_file for i in bpy.data.images)
    native_rows=[]
    references={r['export_name']:r['reimport'] for r in receipt['objects']}
    for obj in scene.objects:
        got,_=metric(obj);ref=references[obj.name]
        error={'matrix_max_abs':max(abs(got['world_matrix'][i][j]-ref['world_matrix'][i][j]) for i in range(4) for j in range(4)),
               'world_bbox_max_abs_m':max(abs(a-b) for aa,bb in zip(got['world_bbox'],ref['world_bbox']) for a,b in zip(aa,bb)),
               'top_abs_m':abs(got['top_z']-ref['top_z'])}
        assert max(error.values())<1e-6 and got['triangles']==ref['triangles']
        native_rows.append({'name':obj.name,'errors_against_verified_glb_reimport':error,'triangles':got['triangles']})
    assert sha(native)==native_sha and sha(SOURCE)==EXPECTED and sha(glb)==receipt['glb_sha256']
    result={'status':'MINIMAL_NATIVE_REOPEN_PASS','native':str(native.relative_to(ROOT)),'native_bytes':native.stat().st_size,'native_sha256':native_sha,
            'source_verified_glb_sha256':receipt['glb_sha256'],'source_shaded_native_sha256':EXPECTED,
            'counts':counts,'objects':native_rows,'all_images_packed':True,
            'world_fit_coordinates_retained':True,'only_original_cc0_instrument_components':True,
            'contains_cat_table_hidden_keys_rig_text_script_lights_camera_animation':False,
            'complete_character_or_motion_approval':False,'upstream_native_unchanged':True}
    (OUT/'minimal-native-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT '+json.dumps({k:result[k] for k in ['status','native','native_bytes','native_sha256','counts']}))


def main():
    assert bpy.app.version[:2]==(3,6) and sha(SOURCE)==EXPECTED
    OUT.mkdir(exist_ok=True)
    if '--note-map' in sys.argv:
        result=write_note_map()
        print('RESULT '+json.dumps({'status':'NOTE_MAP_ACTUAL_GAPS_PASS','white_midi':[item['midi'] for item in result['whitesPlayerAscending']],'black_midi':[item['midi'] for item in result['blacks']]}));return
    if '--native-only' in sys.argv:
        minimal_native();return
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    original=bpy.context.scene
    rig=bpy.data.objects['RIG-Cat']
    assert pose_hash(rig)==POSE
    base_hash=source_mesh_hash();actions=len(bpy.data.actions)
    sources={name:bpy.data.objects[name] for name in NAMES}
    assert len(sources)==18 and all(o.type=='MESH' and not o.hide_render and not o.hide_viewport for o in sources.values())
    assert len([o for o in original.objects if o.type=='MESH' and not o.hide_render and not o.hide_viewport and o.name.startswith(('Ivory piano key','Raised black piano key','Controller chassis','Top rotary control','Top control index'))])==18
    reference={};source_points={};snapshots=[];snapshot_meshes=[]
    snapshot=bpy.data.scenes.new('EIGHTKEY_PROP_ONLY_EXPORT')
    used_materials=set()
    with RenderMatchedProxy():
        dg=bpy.context.evaluated_depsgraph_get()
        for name,obj in sources.items():
            reference[name],source_points[name]=metric(obj)
            evaluated=obj.evaluated_get(dg)
            mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=dg)
            copy=bpy.data.objects.new(PREFIX+name,mesh)
            snapshot.collection.objects.link(copy)
            copy.matrix_world=obj.matrix_world.copy()
            snapshots.append(copy);snapshot_meshes.append(mesh)
            used_materials.update(m.name for m in mesh.materials if m)
    assert source_mesh_hash()!=base_hash # evaluated copies are new temporary datablocks
    assert pose_hash(rig)==POSE and len(bpy.data.actions)==actions
    shader_color_readers=[]
    for name in used_materials:
        mat=bpy.data.materials[name]
        if mat.use_nodes:
            shader_color_readers.extend((name,n.name) for n in mat.node_tree.nodes if n.bl_idname in {'ShaderNodeVertexColor','ShaderNodeAttribute'} and any(s.is_linked for s in n.outputs))
    assert not shader_color_readers
    bpy.context.window.scene=snapshot
    bpy.context.view_layer.update()
    assert len(snapshot.objects)==18 and all(o.type=='MESH' for o in snapshot.objects)
    destination=OUT/'eight-key-cc0-prop.glb'
    bpy.ops.export_scene.gltf(filepath=str(destination),export_format='GLB',use_active_scene=True,
                              export_animations=False,export_cameras=False,export_lights=False,
                              export_colors=False,export_extras=False,export_morph=False)
    gltf=read_glb(destination)
    assert not gltf.get('skins') and not gltf.get('animations') and not gltf.get('cameras')
    assert not gltf.get('extensions',{}).get('KHR_lights_punctual')
    assert len(gltf['nodes'])==18 and len(gltf['meshes'])==18
    assert {n['name'] for n in gltf['nodes']}=={PREFIX+name for name in NAMES}
    assert all('mesh' in n and not n.get('children') for n in gltf['nodes'])
    assert all(not b.get('uri') for b in gltf['buffers']) and all(not i.get('uri') for i in gltf.get('images',[]))
    assert all('COLOR_0' not in p['attributes'] and not p.get('targets') for m in gltf['meshes'] for p in m['primitives'])
    assert len(gltf.get('materials',[]))==len(used_materials)
    # Remove only our temporary evaluated snapshots so import names are exact.
    for obj in snapshots:bpy.data.objects.remove(obj,do_unlink=True)
    for mesh in snapshot_meshes:
        if mesh.users==0:bpy.data.meshes.remove(mesh)
    assert source_mesh_hash()==base_hash and pose_hash(rig)==POSE
    reimport=bpy.data.scenes.new('EIGHTKEY_PROP_ONLY_REIMPORT')
    bpy.context.window.scene=reimport
    bpy.ops.import_scene.gltf(filepath=str(destination))
    bpy.context.view_layer.update()
    assert len(reimport.objects)==18 and all(o.type=='MESH' for o in reimport.objects)
    imported={o.name.removeprefix(PREFIX):o for o in reimport.objects}
    assert set(imported)==set(NAMES)
    results=[]
    for name,obj in imported.items():
        got,points=metric(obj);expected=reference[name]
        errors={'matrix_max_abs':max(abs(got['world_matrix'][i][j]-expected['world_matrix'][i][j]) for i in range(4) for j in range(4)),
                'world_bbox_max_abs_m':max(abs(a-b) for aa,bb in zip(got['world_bbox'],expected['world_bbox']) for a,b in zip(aa,bb)),
                'top_abs_m':abs(got['top_z']-expected['top_z']),
                'source_to_import_nearest_max_m':nearest_max(source_points[name],points),
                'import_to_source_nearest_max_m':nearest_max(points,source_points[name])}
        assert got['triangles']==expected['triangles'] and got['material_slot_count']==expected['material_slot_count'],name
        assert errors['matrix_max_abs']<1e-5 and errors['world_bbox_max_abs_m']<1e-6 and errors['source_to_import_nearest_max_m']<1e-6 and errors['import_to_source_nearest_max_m']<1e-6,(name,errors)
        results.append({'source_name':name,'export_name':PREFIX+name,'source':expected,'reimport':got,'errors':errors})
    whites=sorted([r for r in results if r['source_name'].startswith('Ivory')],key=lambda r:r['source']['world_center'][0])
    source_pitch=[b['source']['world_center'][0]-a['source']['world_center'][0] for a,b in zip(whites,whites[1:])]
    import_pitch=[b['reimport']['world_center'][0]-a['reimport']['world_center'][0] for a,b in zip(whites,whites[1:])]
    pitch_error=max(abs(a-b) for a,b in zip(source_pitch,import_pitch));assert pitch_error<1e-6
    imported_materials={m.name for o in imported.values() for m in o.data.materials if m}
    assert len(imported_materials)==len(used_materials)
    result={'status':'PROP_ONLY_GLTF_REIMPORT_NUMERIC_PASS_PENDING_VISUAL_LOOK',
            'source_native':str(SOURCE.relative_to(ROOT)),'source_sha256_before':EXPECTED,'source_sha256_after':sha(SOURCE),
            'source_pose_sha256':POSE,'source_base_meshes_material_slots_sha256':base_hash,
            'glb':str(destination.relative_to(ROOT)),'glb_bytes':destination.stat().st_size,'glb_sha256':sha(destination),
            'blender':bpy.app.version_string,'objects':results,'mesh_count':18,'glb_node_count':len(gltf['nodes']),
            'triangle_count':sum(r['source']['triangles'] for r in results),'source_material_count':len(used_materials),'gltf_material_count':len(gltf.get('materials',[])),'reimport_material_count':len(imported_materials),
            'source_material_names':sorted(used_materials),'embedded_image_count':len(gltf.get('images',[])),
            'all_payloads_embedded':True,'source_white_pitch_m':source_pitch,'reimport_white_pitch_m':import_pitch,'pitch_max_error_m':pitch_error,
            'contains_cat_table_human_lights_camera_animation':False,'unused_source_color_readers':shader_color_readers,
            'authoring_only':True,'production_cat_frame':False,'new_authored_geometry':False,
            'source_hidden_keys_unchanged':True,'new_actions':0,'mechanical_collision_claim':'No complete mechanical or continuous safety claim; source hidden key-mount overlap/unknowns retained.',
            'geometry_method':'Original evaluated CC0 mesh copies retaining world transforms. No remodeling. Render-matched proxy, not direct RENDER depsgraph.'}
    assert sha(SOURCE)==EXPECTED and pose_hash(rig)==POSE and len(bpy.data.actions)==actions
    (OUT/'reimport-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    # Only after structural/numerical comparisons: one authoring preview. These
    # temporary camera/lights never enter the already-verified prop GLB.
    reimport.world=original.world.copy() if original.world else None
    for light in [o for o in original.objects if o.type=='LIGHT']:
        copy=light.copy();copy.data=light.data.copy();reimport.collection.objects.link(copy);copy.matrix_world=light.matrix_world.copy()
    camera_data=bpy.data.cameras.new('EIGHTKEY_DIAGNOSTIC_CAMERA')
    camera=bpy.data.objects.new('EIGHTKEY_DIAGNOSTIC_CAMERA',camera_data)
    reimport.collection.objects.link(camera);camera.location=(.80,-1.20,.90)
    camera.rotation_euler=(Vector((0,-.405,.32))-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=.75;reimport.camera=camera
    reimport.render.engine='BLENDER_EEVEE';reimport.eevee.taa_render_samples=64;reimport.eevee.use_gtao=original.eevee.use_gtao;reimport.eevee.gtao_distance=original.eevee.gtao_distance;reimport.eevee.use_soft_shadows=original.eevee.use_soft_shadows
    reimport.view_settings.view_transform=original.view_settings.view_transform;reimport.view_settings.look=original.view_settings.look;reimport.view_settings.exposure=original.view_settings.exposure;reimport.view_settings.gamma=original.view_settings.gamma
    reimport.render.resolution_x=1100;reimport.render.resolution_y=850;reimport.render.resolution_percentage=100;reimport.render.image_settings.file_format='PNG';reimport.render.filepath=str(OUT/'prop-reimport-three-quarter.png')
    bpy.ops.render.render(write_still=True)
    result.update(status='PROP_ONLY_GLTF_REIMPORT_NUMERIC_PASS_PREVIEW_READY',diagnostic_render=str(Path(reimport.render.filepath).relative_to(ROOT)),diagnostic_render_sha256=sha(Path(reimport.render.filepath)),glb_unchanged_after_preview=sha(destination)==result['glb_sha256'])
    assert result['glb_unchanged_after_preview'] and sha(SOURCE)==EXPECTED
    (OUT/'reimport-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    write_note_map()
    print('RESULT '+json.dumps({k:result[k] for k in ['status','glb','glb_bytes','glb_sha256','mesh_count','triangle_count','source_material_count','embedded_image_count','pitch_max_error_m','contains_cat_table_human_lights_camera_animation']}))


if __name__=='__main__':
    main()
