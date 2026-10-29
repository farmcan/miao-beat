"""Read-only actual-geometry profile extraction and Blender constraint API probe.

Run with Blender factory-startup. Never saves or deforms the source scene.
This creates unbound diagnostic bones in memory, not a delivered character rig.
"""
import bpy
import hashlib
import json
import math
from pathlib import Path
import sys
from mathutils import Vector
from mathutils.geometry import interpolate_bezier, intersect_point_tri
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "evidence"
SOURCE = ROOT / "artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend"
EXPECTED = "3097d74a3f932d6dd61e60b7ab12bd40c5c53cd09b7c94aaf93170a03ec25cce"
O = Vector((-.1950536246756659, -.85, 1.5567366254980208))
GU = Vector((1.0169595357706245, 0, .40048756408789304))
GV = Vector((-.40048756408789304, 0, 1.0169595357706245))
NORMAL = Vector((0, -1, 0))
STRIKE_U = .05  # authoring diagnostic over sound hole, not approved paw placement


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def logical_u(p):
    return (p - O).dot(GU) / GU.length_squared


def actual_tree(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    points = [ob.matrix_world @ p.co for p in mesh.vertices]
    faces = [tuple(t.vertices) for t in mesh.loop_triangles]
    result = BVHTree.FromPolygons(points, faces, all_triangles=True)
    count = len(faces)
    ev.to_mesh_clear()
    return result, count


def curve_at_u(ob, u):
    bp = ob.data.splines[0].bezier_points
    points = []
    for i in range(len(bp) - 1):
        piece = interpolate_bezier(bp[i].co, bp[i].handle_right,
                                   bp[i + 1].handle_left, bp[i + 1].co, 1024)
        points.extend(ob.matrix_world @ p for p in piece[:-1])
    points.append(ob.matrix_world @ bp[-1].co)
    for p, q in zip(points, points[1:]):
        a, b = logical_u(p), logical_u(q)
        if a <= u <= b:
            return p.lerp(q, (u - a) / (b - a))
    raise ValueError(f"u={u} outside {ob.name}")


def bind_left(body):
    """Freeze existing C35 actual contact hits with explicit triangle bindings."""
    receipt = json.loads((SOURCE.parent / "receipt.json").read_text())
    body.data.calc_loop_triangles()
    result = []
    source_attr = body.data.attributes.get("C23 source vertex id")
    int_attrs = [a for a in body.data.attributes if a.domain == "POINT" and a.data_type == "INT"]
    import numpy as np
    provenance_arrays = {}
    for attr in int_attrs:
        arr = np.empty(len(body.data.vertices), dtype=np.int32)
        attr.data.foreach_get("value", arr)
        provenance_arrays[attr.name] = arr
    for row in receipt["after_actual_target_rays"]:
        point = Vector(row["skin"])
        choices = []
        for tri in body.data.loop_triangles:
            if tri.polygon_index != row["face_index"]:
                continue
            a, b, c = [body.matrix_world @ body.data.vertices[i].co for i in tri.vertices]
            v0, v1, v2 = b - a, c - a, point - a
            d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
            den = d00 * d11 - d01 * d01
            if abs(den) < 1e-20:
                continue
            v = (d11 * v2.dot(v0) - d01 * v2.dot(v1)) / den
            w = (d00 * v2.dot(v1) - d01 * v2.dot(v0)) / den
            weights = [1 - v - w, v, w]
            recon = sum((p * weight for p, weight in zip([a, b, c], weights)), Vector())
            score = max(0, -min(weights)) + (recon - point).length
            choices.append((score, list(tri.vertices), weights, (recon - point).length))
        score, ids, weights, error = min(choices)
        assert min(weights) >= -2e-5 and error < 5e-7
        vertex_provenance = []
        for i in ids:
            values = {name: int(arr[i]) for name, arr in provenance_arrays.items()}
            matches = np.ones(len(body.data.vertices), dtype=bool)
            for name, value in values.items():
                matches &= provenance_arrays[name] == value
            vertex_provenance.append({"source_native_vertex_index": i,
                                      "source_rest_world": list(body.matrix_world @ body.data.vertices[i].co),
                                      "all_integer_point_attributes": values,
                                      "matching_source_vertices": int(matches.sum()),
                                      "unique_tuple": bool(matches.sum() == 1)})
        result.append({"kind": row["kind"], "world": list(point),
                       "actual_target_world": row["actual_target_world"],
                       "signed_gap_u": row["gap"], "expected_source": row["expected_source"],
                       "polygon_index": row["face_index"], "triangle_vertex_indices": ids,
                       "source_vertex_ids": [int(source_attr.data[i].value) for i in ids],
                       "vertex_provenance": vertex_provenance,
                       "merge_remap_required": True,
                       "barycentric": weights, "reconstruction_error_u": error})
    return result


def main():
    OUT.mkdir(exist_ok=True)
    before_sha = sha(SOURCE)
    assert before_sha == EXPECTED
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    bpy.context.view_layer.update()
    body = bpy.data.objects["Miao / continuous pear and rounded-square face"]
    original_coordinates = [tuple(v.co) for v in body.data.vertices]
    original_modifiers = [m.name for m in body.modifiers]
    rows, trees = [], []
    for index in range(1, 7):
        ob = bpy.data.objects[f"Guitar / string {index}"]
        center = curve_at_u(ob, STRIKE_U)
        tree, triangles = actual_tree(ob)
        hit, normal, tri, distance = tree.ray_cast(center + NORMAL * .08, -NORMAL, .16)
        assert hit is not None and normal.dot(NORMAL) > .5
        ray_hit = hit.copy()
        # BVH ray accumulation can land ~1e-6u off the evaluated triangle;
        # project once to that same actual tube, preserving the measured delta.
        hit = tree.find_nearest(hit)[0]
        rows.append({"name": ob.name, "source_index": index,
                     "authored_conventional_string": 7 - index, "u": STRIKE_U,
                     "center_world": list(center), "surface_world": list(hit),
                     "surface_normal": list(normal), "radius_u": ob.data.bevel_depth,
                     "actual_evaluated_triangles": triangles, "surface_triangle_index": tri,
                     "v": (center - O).dot(GV) / GV.length_squared,
                     "surface_ray_distance_u": distance,
                     "ray_to_actual_triangle_projection_u": (hit - ray_hit).length})
        trees.append(tree)
    rows.sort(key=lambda r: r["v"])
    contacts = [Vector(row["surface_world"]) for row in rows]
    tangent = GV.normalized()
    margin, clearance = .035, .075
    start = contacts[0] - tangent * margin
    end = contacts[-1] + tangent * margin
    sweep = [start] + contacts + [end]
    # Every actual evaluated tube is included in the endpoint diagnostic.
    sweep_nearest = []
    for j, (p, q) in enumerate(zip(sweep, sweep[1:])):
        for step in range(31):
            pnt = p.lerp(q, step / 30)
            nearest = min(tree.find_nearest(pnt)[3] for tree in trees)
            sweep_nearest.append(nearest)
    return_clearance = []
    for step in range(101):
        pnt = (end + NORMAL * clearance).lerp(start + NORMAL * clearance, step / 100)
        return_clearance.append(min(tree.find_nearest(pnt)[3] for tree in trees))
    contact_errors = [trees[int(row["name"].split()[-1]) - 1].find_nearest(Vector(row["surface_world"]))[3] for row in rows]
    anchors = bind_left(body)
    profile = {
        "schema": "miao-contact-rig-v2", "status": "unbound-technical-profile-static-art-gates-pending",
        "source_native": str(SOURCE.relative_to(ROOT)), "source_native_sha256": before_sha,
        "coordinate_system": "Blender Z-up world, scene units; engine adapter must transform positions and directions",
        "whole_frame_required": True, "mesh_may_be_split": False,
        "strike": {"logical_u": STRIKE_U, "normal_world": list(NORMAL),
                   "cross_axis_world": list(tangent), "clearance_u": clearance,
                   "edge_margin_u": margin, "duration_ms": 140,
                   "sweep_surface_world": [list(p) for p in sweep],
                   "rest_world": list(start + NORMAL * clearance), "strings": rows},
        "left_hold": {"mode": "freeze_existing_world_contact", "anchors": anchors,
                      "fret_changes_enabled": False,
                      "strict_nominal_contact_band_pass": receipt_value("strict_nominal_contact_band_pass"),
                      "authorized_positive_gap_roundoff_pass": receipt_value("authorized_positive_gap_roundoff_pass")},
        "rig": {"anchors_approved": False,
                "anchors_note": "Unbound authoring landmarks only; replace shoulder/elbow/head anchors after complete static art approval, preserve contact rails in instrument space.",
                "root": [0, 0, .3], "chest": [0, 0, 2.1], "head_base": [0, 0, 2.65], "head_tip": [0, 0, 3.3],
                "right_shoulder": [-.8, -.28, 2.25], "right_elbow": [-1.25, -.64, 1.94],
                "right_effector": list(start + NORMAL * clearance),
                "left_shoulder": [.8, -.28, 2.25], "left_elbow": [1.37, -.65, 1.65],
                "left_effector": [sum(a["world"][i] for a in anchors) / len(anchors) for i in range(3)]},
        "limits": ["Surface point path only: no paw volume, skinning, deformation, string force, audio, browser or visual motion verification.",
                   "Native whole connected skin is unchanged and not bound; no arm textures or detached limb meshes created.",
                   "Left anchors are source-native-specific; remap by exact retained provenance and verify after merged body changes."]}
    profile["note_targets"] = extract_note_targets(rows)
    (OUT / "c35-rig-profile.json").write_text(json.dumps(profile, indent=2) + "\n")
    # Validate actual Blender native constraint construction; leave source mesh unbound.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from native_rig_scaffold import build_unbound_scaffold
    rig, targets = build_unbound_scaffold(profile)
    bpy.context.view_layer.update()
    ik = rig.pose.bones["DEF-right-forearm"].constraints[0]
    endpoint_errors = {side: ((rig.matrix_world @ rig.pose.bones[f"DEF-{side}-forearm"].tail) - targets[side].matrix_world.translation).length for side in ["right", "left"]}
    probe = {"blender_version": bpy.app.version_string,
             "bone_names": [b.name for b in rig.data.bones],
             "ik_type": ik.type, "ik_chain_count": ik.chain_count,
             "ik_stretch_disabled": not ik.use_stretch,
             "unbound_rest_forearm_endpoint_error_u": endpoint_errors,
             "target_objects": list(targets),
             "left_contact_copy_constraints": [c.type for c in rig.pose.bones["DEF-left-paw"].constraints],
             "skin_bound": False, "animation_created": False,
             "source_mesh_coordinates_bit_exact_in_memory": original_coordinates == [tuple(v.co) for v in body.data.vertices],
             "source_mesh_modifiers_unchanged": original_modifiers == [m.name for m in body.modifiers],
             "source_file_hash_unchanged": sha(SOURCE) == before_sha,
             "actual_six_surface_hit_error_max_u": max(contact_errors),
             "lifted_return_actual_six_tube_distance_min_u": min(return_clearance),
             "return_samples": len(return_clearance), "sweep_samples": len(sweep_nearest),
             "scope": "Point-path feasibility and bpy API construction only; not bound rig or animation quality.",
             "profile_sha256": sha(OUT / "c35-rig-profile.json")}
    assert probe["source_mesh_coordinates_bit_exact_in_memory"] and probe["source_mesh_modifiers_unchanged"] and probe["source_file_hash_unchanged"]
    print("PROBE_BEFORE_GATE " + json.dumps(probe), flush=True)
    assert max(contact_errors) < 1e-6 and min(return_clearance) > .07
    (OUT / "native-api-and-geometry-probe.json").write_text(json.dumps(probe, indent=2) + "\n")
    print("RESULT " + json.dumps(probe))


def receipt_value(key):
    return json.loads((SOURCE.parent / "receipt.json").read_text())[key]


def extract_note_targets(string_rows):
    """Real fret centers and string surface targets, NOT animated finger poses."""
    def center_world(ob):
        ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        bounds = [ob.matrix_world @ Vector(c) for c in ev.bound_box]
        return sum(bounds, Vector()) / len(bounds)
    nut = bpy.data.objects["Guitar / nut"]
    nut_center = center_world(nut)
    nut_u = logical_u(nut_center)
    frets = []
    for ob in bpy.data.objects:
        if ob.name.startswith("Guitar / silver fret"):
            # Read actual transformed curve endpoints, not name suffix or pixels.
            bp = ob.data.splines[0].bezier_points
            pts = [ob.matrix_world @ p.co for p in bp]
            center = sum(pts, Vector()) / len(pts)
            frets.append({"object": ob.name, "u": logical_u(center), "center_world": list(center)})
    frets.sort(key=lambda r: -r["u"])
    for i, row in enumerate(frets):
        row["fret_number"] = i + 1
    assert len(frets) >= 8 and nut_u > frets[0]["u"]
    notes = [("KeyA", "C4", 60, 2, 1), ("KeyS", "D4", 62, 2, 3),
             ("KeyD", "E4", 64, 1, 0), ("KeyF", "F4", 65, 1, 1),
             ("KeyG", "G4", 67, 1, 3), ("KeyH", "A4", 69, 1, 5),
             ("KeyJ", "B4", 71, 1, 7), ("KeyK", "C5", 72, 1, 8)]
    open_midi = {6: 40, 5: 45, 4: 50, 3: 55, 2: 59, 1: 64}
    output = []
    for key, name, midi, conventional, fret in notes:
        source_index = 7 - conventional
        string = bpy.data.objects[f"Guitar / string {source_index}"]
        # Fret wire is a boundary; a pad target lies just nutward of it inside
        # the actual interval. 0.18 is an authoring choice, not a measured grip.
        lower = frets[fret - 1]["u"] if fret else nut_u
        upper = nut_u if fret <= 1 else frets[fret - 2]["u"]
        target_u = lower + .18 * (upper - lower) if fret else nut_u
        center = curve_at_u(string, target_u)
        tree, _ = actual_tree(string)
        hit, normal, tri, distance = tree.ray_cast(center + NORMAL * .08, -NORMAL, .16)
        assert hit is not None
        hit = tree.find_nearest(hit)[0]
        assert open_midi[conventional] + fret == midi
        output.append({"key": key, "note": name, "midi": midi,
                       "standard_string": conventional, "source_string_index": source_index,
                       "source_object": string.name, "fret": fret,
                       "open_string": fret == 0, "press_required": fret != 0,
                       "target_u": target_u, "actual_fret_interval_u": [lower, upper],
                       "left_target_surface_world": list(hit) if fret else None,
                       "open_string_clear_target_world": list(hit + NORMAL * .03) if fret == 0 else None,
                       "right_pluck_surface_world": next(r["surface_world"] for r in string_rows if r["source_index"] == source_index),
                       "pitch_formula_verified": True, "paw_pose_verified": False})
    return {"assignment": "Authoring proposal: source indices 1..6 assigned E2,A2,D3,G3,B3,E4; source mesh stores no pitch metadata. Source 1..3 are thicker; conventional numbering is reversed (source 6 = high E/string 1).",
            "assignment_is_source_fact": False,
            "orientation_warning": "Source low-to-high index increases along +guitar-V; source thick strings occupy -V. Final instrument orientation/string semantics need review before musical visual acceptance.",
            "tuning_primary_source": "https://www.fender.com/articles/setup/standard-tuning-how-eadgbe-came-to-be",
            "nut": {"object": nut.name, "center_world": list(nut_center), "u": nut_u},
            "frets_actual_nut_to_body": frets, "melody": output,
            "left_pose_status": "Target data only; C35 existing hold stays frozen. Future fretting poses require individual contact/wood/tube/self/deformation gates."}


if __name__ == "__main__":
    main()
