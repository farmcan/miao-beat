"""Import one generated whole-scene candidate for local gray-model inspection.
No shape repair, rig, pose replacement or claim of visual acceptance.
Blender -b --python design/modelr-static-trial/import-shape.py -- --input ... --output ...
"""
import argparse, sys, json, hashlib, math
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser()
p.add_argument('--input', required=True)
p.add_argument('--output', required=True)
p.add_argument('--size', type=int, default=1024)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
src=Path(a.input).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(src))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
if not objects: raise RuntimeError('GLB contains no mesh')
# Bounds include only the imported subject, never studio planes/lights.
coords=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
center=(lo+hi)/2;span=hi-lo;diam=max(span)
mat=bpy.data.materials.new('Neutral gray inspection');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.43,.43,.43,1);bs.inputs['Roughness'].default_value=.65
for o in objects:
 o.data.materials.clear();o.data.materials.append(mat)
 for f in o.data.polygons:f.use_smooth=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.seed=17
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 scene.cycles.device='GPU'
except Exception:pass
scene.render.resolution_x=scene.render.resolution_y=a.size;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
bpy.ops.mesh.primitive_plane_add(size=diam*100,location=(center.x,center.y,lo.z-.002*diam))
floor=bpy.context.object;floor.name='Studio floor / excluded from subject bounds'
fm=bpy.data.materials.new('Studio backdrop');fm.use_nodes=True;fm.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.8,.8,.8,1);fm.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8;floor.data.materials.append(fm)
for name,offset,energy,size in [('Key',(-1.4,-2,3),450,2.5),('Fill',(2,-.8,1.8),220,2)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*diam)
 light=bpy.context.object;light.name=name;light.data.energy=energy*(diam/2)**2;light.data.shape='DISK';light.data.size=size*diam
 light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=diam*1.24;scene.camera=camera
views=[('front',(0,-4,.2)),('three-quarter',(2.8,-3,.2)),('back',(0,4,.2))]
for label,offset in views:
 camera.location=center+Vector(offset)*diam;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(out/f'gray-{label}.png')
 if label=='front':bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-shape-seed17.blend'))
 bpy.ops.render.render(write_still=True)
receipt={'status':'generated_gray_unreviewed','input_glb_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'vertices':sum(len(o.data.vertices) for o in objects),'faces':sum(len(o.data.polygons) for o in objects),'bounds_imported_only':{'min':list(lo),'max':list(hi)},'front_assumption':'glTF Y-up import; source image camera expected +Z glTF (= -Y Blender); verify manually','unverified':['identity fidelity','paws/instrument separation','hidden anatomy','animation topology','fur/materials','rig','contact','web runtime']}
(out/'blender-import-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
