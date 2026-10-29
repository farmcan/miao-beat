"""Unbound native Blender scaffold. Never edits a source mesh or auto-weights it.

After both static gates pass: author approved landmarks/weights on ONE connected
skin, then validate deformations and contacts. This module provides the reusable
bone/constraint interface, not visual approval or a deliverable bound rig.
"""
import bpy
from mathutils import Vector


def build_unbound_scaffold(profile):
    namespace = "MiaoMotionV2 / "
    if bpy.data.objects.get(namespace + "unbound scaffold"):
        raise ValueError("Scaffold already exists; do not silently append duplicate rig")
    collection = bpy.data.collections.new(namespace + "technical only")
    bpy.context.scene.collection.children.link(collection)
    armature = bpy.data.armatures.new(namespace + "bone data")
    rig = bpy.data.objects.new(namespace + "unbound scaffold", armature)
    collection.objects.link(rig)
    rig["status"] = "UNBOUND technical scaffold, static art gates pending"
    rig.show_in_front = True
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    a = profile["rig"]
    bpy.ops.object.mode_set(mode="EDIT")
    def bone(name, head, tail, parent=None, connected=False):
        b = armature.edit_bones.new(name)
        b.head, b.tail = Vector(head), Vector(tail)
        if parent:
            b.parent = armature.edit_bones[parent]
            b.use_connect = connected
        return b
    bone("DEF-root", a["root"], a["chest"])
    bone("DEF-head", a["head_base"], a["head_tip"], "DEF-root")
    for side in ["right", "left"]:
        bone(f"DEF-{side}-upper", a[f"{side}_shoulder"], a[f"{side}_elbow"], "DEF-root")
        bone(f"DEF-{side}-forearm", a[f"{side}_elbow"], a[f"{side}_effector"], f"DEF-{side}-upper", True)
        tip = Vector(a[f"{side}_effector"]) + Vector((0, -.08, 0))
        bone(f"DEF-{side}-paw", a[f"{side}_effector"], tip, f"DEF-{side}-forearm", True)
    bpy.ops.object.mode_set(mode="OBJECT")
    targets = {}
    for side in ["right", "left"]:
        target = bpy.data.objects.new(namespace + side + " contact target", None)
        collection.objects.link(target)
        target.empty_display_type = "SPHERE"
        target.empty_display_size = .025
        target.location = a[f"{side}_effector"]
        target.rotation_mode = "QUATERNION"
        target.rotation_quaternion = rig.matrix_world.to_quaternion() @ rig.data.bones[f"DEF-{side}-paw"].matrix_local.to_quaternion()
        target["space"] = "Instrument world contact target; do not parent to breathing/head bones"
        targets[side] = target
        ik = rig.pose.bones[f"DEF-{side}-forearm"].constraints.new("IK")
        ik.name = namespace + "no-stretch two-bone IK"
        ik.target = target
        ik.chain_count = 2
        ik.use_stretch = False
        ik.iterations = 32
        rig.pose.bones[f"DEF-{side}-upper"].ik_stretch = 0
        rig.pose.bones[f"DEF-{side}-forearm"].ik_stretch = 0
        # Paw target provides orientation independently from the two-bone solve.
        rotation = rig.pose.bones[f"DEF-{side}-paw"].constraints.new("COPY_ROTATION")
        rotation.target = target
        rotation.owner_space = "WORLD"
        rotation.target_space = "WORLD"
    # World-space grip target prevents a future chest/head phrase channel from
    # dragging the fretting endpoint. Finger/skin anchors still need validation.
    hold = rig.pose.bones["DEF-left-paw"].constraints.new("COPY_LOCATION")
    hold.target = targets["left"]
    hold.owner_space = "WORLD"
    hold.target_space = "WORLD"
    bpy.context.view_layer.update()
    return rig, targets
