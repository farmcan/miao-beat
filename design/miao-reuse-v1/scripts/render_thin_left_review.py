"""Camera-only left review correction; frozen failed pose stays identical."""
import bpy
import hashlib
import json
import pathlib
import sys
from mathutils import Vector
args = sys.argv[sys.argv.index('--')+1:]
source = pathlib.Path(args[0]).resolve()
out = source.parent
before = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
rig = bpy.data.objects['RIG-Cat']
pose_before = [[bone.name,[list(row) for row in bone.matrix_basis]] for bone in rig.pose.bones]
scene = bpy.context.scene
camera = scene.camera
wrist = rig.matrix_world @ rig.pose.bones['ORG-Hand.L'].head
center = wrist+Vector((0,0,.025))
camera.data.ortho_scale = .38
camera.location = center+Vector((1.4,-3.6,.6)).normalized()*4
camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.data.objects['THIN-DIAGNOSTIC-LABEL'].hide_render = True
helper = bpy.data.objects['HLP-scene_camera_dummy']
bpy.context.view_layer.update()
expected = camera.matrix_world.to_euler()
helper.rotation_euler = expected
helper.update_tag(refresh={'OBJECT'})
bpy.context.view_layer.update()
errors = [abs(helper.rotation_euler[i]-expected[i]) for i in range(3)]
assert max(errors)<1e-6
image = out/'thin-electric-left-hand-front-NOT-ACCEPTED.png'
scene.render.filepath = str(image)
bpy.ops.render.render(write_still=True)
pose_after = [[bone.name,[list(row) for row in bone.matrix_basis]] for bone in rig.pose.bones]
assert pose_before==pose_after
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
receipt = {'scope':'camera-only visibility correction; original rear crop occluded by sleeve','native_unchanged_sha256':before,'pose_basis_identical':True,'helper_axis_errors':errors,'image':str(image),'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'native_saves':0,'pose_edits':0}
(out/'left-review-camera-receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
