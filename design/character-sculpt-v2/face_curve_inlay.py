"""Project complete sampled mouth curves, rather than only Bezier control points.
Original Miao helper. Call on an owned working-copy scene after its head sculpt.
Front is -Y; preserve authored X/Z, do not use nearest-point fallback.
"""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import interpolate_bezier


def fit_mouth_inlays(body, objects=None, samples_per_segment=33, offset_ratio=.35):
    bpy.context.view_layer.update()
    tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    inverse = body.matrix_world.inverted()
    direction = (inverse.to_3x3() @ Vector((0, 1, 0))).normalized()
    objects = list(objects) if objects is not None else [
        o for o in bpy.context.scene.objects
        if o.type == 'CURVE' and o.name.startswith('Face / smile')]
    reports = []
    for ob in objects:
        old = ob.data
        scale = ob.matrix_world.to_scale()
        if max(scale) - min(scale) > 1e-5:
            raise ValueError('Inlay requires a uniformly scaled curve: ' + ob.name)
        radius = float(old.bevel_depth)
        if radius <= 0:
            raise ValueError('Inlay requires a nonzero curve radius')
        world_radius = radius * scale.x
        offset = world_radius * offset_ratio
        projected = []
        errors = []
        for spline in old.splines:
            if spline.type != 'BEZIER':
                raise ValueError('Expected authored Bezier mouth, got ' + spline.type)
            controls = spline.bezier_points
            samples = []
            count = len(controls) if spline.use_cyclic_u else len(controls) - 1
            for i in range(count):
                aa, bb = controls[i], controls[(i + 1) % len(controls)]
                segment = interpolate_bezier(aa.co, aa.handle_right,
                                            bb.handle_left, bb.co,
                                            samples_per_segment)
                samples.extend(segment if not samples else segment[1:])
            path = []
            for pt in samples:
                requested = ob.matrix_world @ pt
                hit, normal, _, _ = tree.ray_cast(
                    inverse @ Vector((requested.x, -3, requested.z)),
                    direction, 12)
                if hit is None:
                    raise RuntimeError('Strict mouth ray missed at ' + str(tuple(requested)))
                skin = body.matrix_world @ hit
                residual = max(abs(skin.x - requested.x), abs(skin.z - requested.z))
                if residual > 2e-5:
                    raise RuntimeError('Mouth projection XZ residual ' + str(residual))
                target = Vector((requested.x, skin.y - offset, requested.z))
                path.append(ob.matrix_world.inverted() @ target)
                errors.append({'xz_residual': residual,
                               'center_front_of_skin_y': skin.y - target.y})
            projected.append((path, spline.use_cyclic_u))
        # Commit only after all rays succeed; use straight short segments to avoid
        # an auto-handle passing back through the convex skin between controls.
        curve = bpy.data.curves.new(old.name + ' / sampled inlay', 'CURVE')
        curve.dimensions = '3D'
        curve.bevel_depth = radius
        curve.bevel_resolution = max(3, old.bevel_resolution)
        curve.resolution_u = 1
        curve.use_fill_caps = True
        for mat in old.materials:
            curve.materials.append(mat)
        for path, cyclic in projected:
            spline = curve.splines.new('POLY')
            spline.points.add(len(path) - 1)
            spline.use_cyclic_u = cyclic
            for point, value in zip(spline.points, path):
                point.co = (*value, 1)
        ob.data = curve
        reports.append({'object': ob.name, 'samples': len(errors),
                        'radius_world': world_radius,
                        'surface_front_offset': offset,
                        'min_center_front_of_skin_y': min(v['center_front_of_skin_y'] for v in errors),
                        'max_xz_residual': max(v['xz_residual'] for v in errors),
                        'strict_ray_misses': 0,
                        'partial_radius_embedding_intentional': True})
        if old.users == 0:
            bpy.data.curves.remove(old)
    bpy.context.view_layer.update()
    return reports
