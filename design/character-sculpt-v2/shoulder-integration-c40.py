"""C40 one connected-skin shoulder-root fairing candidate; no topology change.

Research-only gray candidate. Preserves C35 generated grip, distal arms, head,
guitar, abdomen, legs and tail. Geometry passes do not confer visual approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import bpy
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "artifacts/character-integrated-gray-c31/miao-c31-head-hand-gray.blend"
NAME = "Miao / continuous pear and rounded-square face"
EXPECTED = "13cbb1da83dfa23c0581ccfe7c07e893b9d0bca6a63244887ad0955f7d0c9c5d"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def smooth(a, b, value):
    t = np.clip((value - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def coords(mesh):
    a = np.empty(len(mesh.vertices) * 3, np.float32)
    mesh.vertices.foreach_get("co", a)
    return a.reshape(-1, 3)


def topology(mesh):
    v = np.empty(len(mesh.loops), np.int32)
    mesh.loops.foreach_get("vertex_index", v)
    n = np.empty(len(mesh.polygons), np.int32)
    mesh.polygons.foreach_get("loop_total", n)
    return hashlib.sha256(v.tobytes() + n.tobytes()).hexdigest()


def int_point_attributes(mesh):
    result = {}
    for attribute in mesh.attributes:
        if attribute.domain == "POINT" and attribute.data_type == "INT":
            a = np.empty(len(attribute.data), np.int32)
            attribute.data.foreach_get("value", a)
            result[attribute.name] = a
    return result


def snapshots():
    result = {}
    for ob in bpy.context.scene.objects:
        if ob.name == NAME:
            continue
        row = {"matrix": list(map(list, ob.matrix_world)), "type": ob.type, "hide_render": ob.hide_render}
        if ob.type == "MESH":
            row["coordinates_sha256"] = hashlib.sha256(coords(ob.data).tobytes()).hexdigest()
            row["topology_sha256"] = topology(ob.data)
        elif ob.type == "CURVE":
            row["bevel_depth"] = ob.data.bevel_depth
            row["bevel_resolution"] = ob.data.bevel_resolution
            row["splines"] = [[[list(p.co), list(p.handle_left), list(p.handle_right)] for p in s.bezier_points] for s in ob.data.splines]
        result[ob.name] = row
    return result


def tree_from_arrays(points, tris):
    return BVHTree.FromPolygons([Vector(p) for p in points], [tuple(t) for t in tris], all_triangles=True)


def self_pairs(points, tris):
    tree = tree_from_arrays(points, tris)
    pairs = tree.overlap(tree)
    return {(int(a), int(b)) for a, b in pairs if a < b and not (set(tris[a]) & set(tris[b]))}


def evaluated_world_tree(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    tree = BVHTree.FromPolygons([ob.matrix_world @ v.co for v in mesh.vertices], [tuple(t.vertices) for t in mesh.loop_triangles], all_triangles=True)
    counts = [len(mesh.vertices), len(mesh.loop_triangles)]
    ev.to_mesh_clear()
    return tree, counts


def parity_vote(tree, point):
    votes = []
    for direction in [Vector((.371, .613, .697)).normalized(), Vector((.739, .223, .635)).normalized()]:
        origin = point.copy(); count = 0
        for _ in range(32):
            hit, normal, index, distance = tree.ray_cast(origin, direction, 12)
            if hit is None:
                break
            count += 1; origin = hit + direction * 2e-6
        votes.append(count % 2)
    return votes


def actual_winding_and_parity(mesh, points, triangles, probe_vertex_ids):
    """Use the actual candidate triangles and full closed surface, not old dots."""
    bm = bmesh.new(); bm.from_mesh(mesh); bm.normal_update()
    mixed = 0
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            loops = list(edge.link_loops)
            if loops[0].vert == loops[1].vert:
                mixed += 1
    remaining = set(bm.verts); components = 0
    while remaining:
        components += 1; stack = [remaining.pop()]
        while stack:
            v = stack.pop()
            for edge in v.link_edges:
                q = edge.other_vert(v)
                if q in remaining:
                    remaining.remove(q); stack.append(q)
    structural = {"components": components, "boundary_edges": sum(e.is_boundary for e in bm.edges),
                  "nonmanifold_edges": sum(not e.is_manifold for e in bm.edges),
                  "inconsistent_winding_edges": mixed, "signed_volume_u3": bm.calc_volume(signed=True)}
    bm.free()
    full_tree = tree_from_arrays(points, triangles)
    marked = np.zeros(len(points), bool); marked[probe_vertex_ids] = True
    probes = triangles[marked[triangles].any(1)]
    rows = []
    for tri in probes:
        pp = points[tri].astype(np.float64)
        normal = np.cross(pp[1] - pp[0], pp[2] - pp[0]); length = np.linalg.norm(normal)
        if length <= 1e-13:
            rows.append({"vertices": tri.tolist(), "degenerate": True}); continue
        normal /= length
        center = pp.mean(0)
        outward = parity_vote(full_tree, Vector(center + normal * 2e-5))
        inward = parity_vote(full_tree, Vector(center - normal * 2e-5))
        rows.append({"vertices": tri.tolist(), "outside_normal_votes": outward,
                     "inside_normal_votes": inward,
                     "outward_correct": outward == [0, 0] and inward == [1, 1]})
    structural["actual_candidate_normal_side_probes"] = len(rows)
    structural["normal_side_probe_failures"] = sum(not r.get("outward_correct", False) for r in rows)
    structural["normal_side_probe_examples"] = [r for r in rows if not r.get("outward_correct", False)][:20]
    structural["normal_side_probe_method"] = "Full candidate actual-triangle BVH; +/-2e-5u around triangle centroid; two independent parity directions. Finite probes, not all-point proof."
    return structural, rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="artifacts/character-shoulder-c40")
    p.add_argument("--probe", action="store_true")
    p.add_argument("--probe-renders", action="store_true")
    p.add_argument("--render", action="store_true")
    a = p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    if (out / "receipt.json").exists():
        raise RuntimeError("Frozen candidate exists; do not overwrite")
    assert sha(SOURCE) == EXPECTED
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    bpy.context.view_layer.update()
    body = bpy.data.objects[NAME]
    mesh = body.data
    assert not body.modifiers and not mesh.shape_keys
    before = coords(mesh)
    original_topology = topology(mesh)
    original_body_matrix = list(map(list, body.matrix_world))
    assert np.allclose(np.array(body.matrix_world), np.eye(4), atol=0, rtol=0)
    x, y, z = before.T
    ax = np.abs(x)
    ids = int_point_attributes(mesh)
    source_ids = ids["C23 source vertex id"]
    # These support limits are declared before the candidate. C38 may change the
    # head above z2.45; C39 owns the picking distal hand. No cross-lane averaging.
    weight = smooth(.42, .58, ax) * (1 - smooth(1.05, 1.20, ax))
    weight *= smooth(-.78, -.58, y) * (1 - smooth(0, .16, y))
    weight *= smooth(1.83, 1.98, z) * (1 - smooth(2.29, 2.40, z))
    before_lock_fade = weight.copy()
    # Implementation repair 2: the original binary lower-forearm locks cut a
    # nonzero diffusion field abruptly. Bring its coefficient smoothly to zero
    # BEFORE reaching the same hard lock; keep field steps/strength unchanged.
    weight *= smooth(-.72, -.52, y)
    weight *= 1 - smooth(.94, 1.10, ax) * (1 - smooth(-.50, -.34, y))
    distal = (x < -.22) & (y < -.88) & (z <= 2.12)
    lower_forearm = (y <= -.72) | ((ax >= 1.10) & (y <= -.50))
    # 2026-10-29 coordination correction: C39 owns ALL cat-right x<0 from
    # shoulder down, including negative-space reconstruction. C40 is LEFT ONLY.
    lock = (source_ids == 0) | (x <= 0) | (z >= 2.40) | (z <= 1.83) | distal | lower_forearm
    weight[lock] = 0
    transition = (weight != before_lock_fade) & ~lock
    selected = weight > 0
    mesh.calc_loop_triangles()
    triangles = np.array([tuple(t.vertices) for t in mesh.loop_triangles], np.int32)
    edges = np.empty(len(mesh.edges) * 2, np.int32)
    mesh.edges.foreach_get("vertices", edges)
    edges = edges.reshape(-1, 2)
    preflight = {
        "source_sha256": EXPECTED, "blender_version": bpy.app.version_string,
        "root_patch_vertex_count": int(selected.sum()), "cat_left_positive_x_count": int((selected & (x > 0)).sum()),
        "cat_right_negative_x_count": int((selected & (x < 0)).sum()), "C35_all_ID0_locked": True,
        "root_patch_bounds": {"min": before[selected].min(0).tolist(), "max": before[selected].max(0).tolist()},
        "new_hand_locked_vertices": int((source_ids == 0).sum()),
        "root_patch_maximum_weight": float(weight.max()), "head_z2_40_and_above_locked": True,
        "cat_right_all_x0_and_below_locked_for_C39": True,
        "distal_right_locked": True, "lower_forearm_locked": True,
        "proposal": "LEFT SHOULDER ONLY after C39 lane correction. Inspect collar first; apply local continuous surface fairing only if the actual left root warrants it. No new sphere, seam mesh or global remesh.",
        "candidate_count_before_probe": 0, "C1_lock_transition_vertex_count": int(transition.sum()),
    }
    (out / "preflight.json").write_text(json.dumps(preflight, indent=2) + "\n")
    print("PREFLIGHT " + json.dumps(preflight), flush=True)
    if a.probe:
        if a.probe_renders:
            scene = bpy.context.scene
            scene.cycles.samples = 16
            scene.render.resolution_x = scene.render.resolution_y = 512
            scene.render.resolution_percentage = 100
            camera = scene.camera
            target = Vector((.88, -.32, 2.12))
            for view, position in [("front", Vector((.88, -6, 2.25))), ("three-quarter", Vector((5, -7, 3.2)))]:
                camera.location = position
                camera.rotation_euler = (target - position).to_track_quat("-Z", "Y").to_euler()
                camera.data.ortho_scale = 1.45
                scene.render.filepath = str(out / f"read-only-left-shoulder-{view}.png")
                bpy.ops.render.render(write_still=True)
            assert sha(SOURCE) == EXPECTED
        return
    # One high-density diffusion solve, not parameter search: 240 fixed steps at
    # .45. Each step's spatial coefficient falls smoothly to zero at all locks.
    # This removes the tube-root curvature concentration without moving distal
    # centers or constructing a second anatomical mass.
    start = time.time()
    active_ids = np.flatnonzero(selected)
    active_edges = edges[selected[edges].any(1)]
    relevant = np.unique(active_edges.ravel())
    remap = np.full(len(before), -1, np.int32)
    remap[relevant] = np.arange(len(relevant))
    ee = remap[active_edges]
    current = before[relevant].astype(np.float64)
    original = current.copy()
    local_weight = weight[relevant].astype(np.float64)
    degree = np.bincount(ee.ravel(), minlength=len(relevant))
    degree = np.maximum(1, degree)
    for _ in range(240):
        neighbor = np.zeros_like(current)
        np.add.at(neighbor, ee[:, 0], current[ee[:, 1]])
        np.add.at(neighbor, ee[:, 1], current[ee[:, 0]])
        delta = neighbor / degree[:, None] - current
        current += .45 * local_weight[:, None] * delta
    # Keep an explicit equal-volume normal correction over this SAME continuous
    # shoulder patch. It corrects smoothing shrinkage instead of adding a ball.
    trial = before.astype(np.float64).copy()
    trial[relevant] = current
    def signed_volume(points):
        t = points[triangles]
        return np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6
    volume_before = float(signed_volume(before.astype(np.float64)))
    volume_smoothed = float(signed_volume(trial))
    normals = np.empty(len(mesh.vertices) * 3, np.float32)
    mesh.vertices.foreach_get("normal", normals)
    normals = normals.reshape(-1, 3).astype(np.float64)
    correction = normals * weight[:, None]
    unit_delta = float(signed_volume(trial + correction * .001) - volume_smoothed)
    correction_scale = (volume_before - volume_smoothed) / unit_delta * .001 if abs(unit_delta) > 1e-15 else 0
    assert abs(correction_scale) < .06, "Local volume correction exceeds declared .06u bound"
    trial += correction * correction_scale
    raw_displacement = np.linalg.norm(trial - before, axis=1)
    # Implementation repair 1: enforce the already-declared .09u trust region
    # smoothly. The original diffusion/correction could exceed that bound before
    # the candidate was applied. tanh avoids a hard clipping contour at the cap.
    factor = np.divide(.09 * np.tanh(raw_displacement / .09), raw_displacement,
                       out=np.ones_like(raw_displacement), where=raw_displacement > 0)
    trial = before + (trial - before) * factor[:, None]
    after = trial.astype(np.float32)
    after[~selected] = before[~selected]
    changed = np.any(after != before, axis=1)
    displacement = np.linalg.norm(after - before, axis=1)
    assert displacement.max() <= .09, "One-candidate bounded displacement exceeded"
    assert np.array_equal(after[lock], before[lock])
    print("BOUNDED_FIELD " + json.dumps({"raw_maximum_displacement": float(raw_displacement.max()), "bounded_maximum_displacement": float(displacement.max()), "volume_correction": float(correction_scale)}), flush=True)
    touched = changed[triangles].any(1)
    t = triangles[touched]
    n0 = np.cross(before[t[:, 1]] - before[t[:, 0]], before[t[:, 2]] - before[t[:, 0]])
    n1 = np.cross(after[t[:, 1]] - after[t[:, 0]], after[t[:, 2]] - after[t[:, 0]])
    l0, l1 = np.linalg.norm(n0, axis=1), np.linalg.norm(n1, axis=1)
    dots = np.einsum("ij,ij->i", n0, n1) / np.maximum(l0 * l1, 1e-25)
    # Fixed original triangles are only tracking proxies after deformation.
    # Recompute Blender's actual implicit tessellation on a TEMPORARY COMPLETE
    # mesh, keeping the original body untouched until all diagnostics finish.
    actual_mesh = mesh.copy()
    actual_mesh.vertices.foreach_set("co", after.ravel()); actual_mesh.update(); actual_mesh.calc_loop_triangles()
    actual_triangles = np.array([tuple(t.vertices) for t in actual_mesh.loop_triangles], np.int32)
    actual_touched = changed[actual_triangles].any(1)
    actual_t = actual_triangles[actual_touched]
    actual_cross = np.cross(after[actual_t[:, 1]] - after[actual_t[:, 0]], after[actual_t[:, 2]] - after[actual_t[:, 0]])
    actual_cross_lengths = np.linalg.norm(actual_cross, axis=1)
    proxy_bad_vertices = np.unique(t[dots <= .65])
    winding, parity_rows = actual_winding_and_parity(actual_mesh, after, actual_triangles, proxy_bad_vertices)
    # Keep a fixed original neighborhood around every edited triangle, including
    # nonedited torso/arm collar faces, so cropped-open boundaries cannot hide a
    # new self intersection against a locked neighbor.
    bounds_min = before[selected].min(0) - .12
    bounds_max = before[selected].max(0) + .12
    in_box = ((before >= bounds_min) & (before <= bounds_max)).all(1)
    neighborhood = triangles[in_box[triangles].any(1)]
    actual_neighborhood = actual_triangles[in_box[actual_triangles].any(1)]
    before_self = self_pairs(before, neighborhood)
    after_self = self_pairs(after, actual_neighborhood)
    def keyed_pairs(pairs, tri):
        return {tuple(sorted([tuple(sorted(tri[a])), tuple(sorted(tri[b]))])) for a, b in pairs}
    introduced_self = keyed_pairs(after_self, actual_neighborhood) - keyed_pairs(before_self, neighborhood)
    initial_other = snapshots()
    guitar = []
    old_tree = tree_from_arrays(before, t)
    new_tree = tree_from_arrays(after, actual_t)
    for ob in bpy.context.scene.objects:
        if not ob.name.startswith("Guitar /") or ob.type not in {"MESH", "CURVE"}:
            continue
        obstacle, counts = evaluated_world_tree(ob)
        old_pairs = set(old_tree.overlap(obstacle))
        new_pairs = set(new_tree.overlap(obstacle))
        # Baseline and candidate actual tessellations can differ. Compare the
        # triangle's source vertex key, not its transient triangle-list index.
        old_keys = {(tuple(sorted(t[i])), j) for i, j in old_pairs}
        new_keys = {(tuple(sorted(actual_t[i])), j) for i, j in new_pairs}
        introduced = new_keys - old_keys
        guitar.append({"object": ob.name, "actual_evaluated_vertices": counts[0], "actual_evaluated_triangles": counts[1],
                       "baseline_surface_pairs": len(old_pairs), "candidate_surface_pairs": len(new_pairs),
                       "introduced_surface_pairs": len(introduced), "introduced_examples": [[list(p[0]), p[1]] for p in list(introduced)[:8]]})
    gate = {"max_displacement_u": float(displacement.max()), "changed_vertices": int(changed.sum()),
            "changed_bounds": {"min": after[changed].min(0).tolist(), "max": after[changed].max(0).tolist()},
            "touched_actual_candidate_triangles": len(actual_t), "fixed_original_triangle_minimum_old_new_normal_dot": float(dots.min()),
            "fixed_original_triangle_minimum_area_ratio": float((l1 / l0).min()), "actual_candidate_collapsed_triangles": int((actual_cross_lengths <= 1e-13).sum()),
            "fixed_original_triangle_direction_reversals": int((dots <= 0).sum()), "local_neighborhood_triangles": len(actual_neighborhood),
            "local_self_pairs_before": len(before_self), "local_self_pairs_after": len(after_self),
            "introduced_local_self_pairs": len(introduced_self), "introduced_self_examples": [[list(t) for t in p] for p in list(introduced_self)[:12]],
            "actual_winding_closedness_parity": winding,
            "original_total_volume_u3": volume_before, "smoothed_total_volume_u3": volume_smoothed,
            "normal_volume_correction_u": float(correction_scale), "candidate_total_volume_u3": float(signed_volume(after.astype(np.float64))),
            "pre_trust_region_maximum_displacement_u": float(raw_displacement.max()), "smooth_trust_region_radius_u": .09,
            "guitar_actual_surfaces": guitar, "all_locks_bit_exact": bool(np.array_equal(after[lock], before[lock])),
            "non_edit_region_bit_exact": bool(np.array_equal(after[~selected], before[~selected])),
            "seconds_before_save": time.time() - start}
    passed = len(after_self) == 0 and all(r["introduced_surface_pairs"] == 0 for r in guitar) and bool((actual_cross_lengths > 1e-13).all()) and winding["components"] == 1 and winding["nonmanifold_edges"] == 0 and winding["inconsistent_winding_edges"] == 0 and winding["signed_volume_u3"] > 0 and winding["normal_side_probe_failures"] == 0
    np.savez_compressed(out / "deformation-evidence.npz", changed_indices=np.flatnonzero(changed), before=before[changed], after=after[changed], source_ids=source_ids, selected_indices=active_ids, weight=weight[selected], C1_transition_indices=np.flatnonzero(transition), C1_transition_original_weights=before_lock_fade[transition], C1_transition_final_weights=weight[transition], hard_locked_indices=np.flatnonzero(lock))
    (out / "actual-normal-side-parity.json").write_text(json.dumps({"summary": winding, "rows": parity_rows}, indent=2) + "\n")
    bpy.data.meshes.remove(actual_mesh)
    if not passed:
        (out / "failed-geometry-gate.json").write_text(json.dumps(gate, indent=2) + "\n")
        print("FAILED_GEOMETRY_GATE " + json.dumps(gate), flush=True)
        # Root explicitly authorized rendering this same failed candidate for
        # INTERNAL diagnosis. Do not promote it to an art deliverable.
        if not a.render:
            return
    mesh.vertices.foreach_set("co", after.ravel())
    mesh.update()
    bpy.context.view_layer.update()
    assert snapshots() == initial_other
    assert topology(mesh) == original_topology and list(map(list, body.matrix_world)) == original_body_matrix
    assert all(np.array_equal(value, int_point_attributes(mesh)[name]) for name, value in ids.items())
    bm = bmesh.new(); bm.from_mesh(mesh); bm.normal_update()
    unseen = set(bm.verts); components = 0
    while unseen:
        components += 1; stack = [unseen.pop()]
        while stack:
            v = stack.pop()
            for e in v.link_edges:
                q = e.other_vert(v)
                if q in unseen:
                    unseen.remove(q); stack.append(q)
    gate["components"] = components
    gate["boundary_edges"] = sum(e.is_boundary for e in bm.edges)
    gate["nonmanifold_edges"] = sum(not e.is_manifold for e in bm.edges)
    gate["actual_signed_volume_u3"] = bm.calc_volume(signed=True)
    bm.free()
    assert components == 1 and gate["nonmanifold_edges"] == 0 and gate["actual_signed_volume_u3"] > 0
    scene = bpy.context.scene
    scene.cycles.samples = 16; scene.cycles.seed = 17; scene.cycles.use_animated_seed = False
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100; scene.render.use_border = False; scene.render.use_crop_to_border = False
    scene.render.image_settings.file_format = "PNG"
    bpy.context.preferences.filepaths.save_version = 0
    native = out / ("miao-c40-shoulder-integration-gray.blend" if passed else "diagnostic-c40-left-shoulder-failed.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(native), compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    assert np.array_equal(coords(bpy.data.objects[NAME].data), after)
    assert snapshots() == initial_other
    receipt = {"stage": "C40 one left-shoulder-root fairing gray candidate; independent visual review pending" if passed else "C40 FAILED left-shoulder geometry; internal diagnostic only", "geometry_gate_passed": passed, "source_sha256": EXPECTED,
               "native_sha256": sha(native), "script_sha256": sha(__file__), "preflight": preflight, "geometry_gate": gate,
               "candidate_count": 1, "implementation_repairs": 2, "fairing": {"steps": 240, "lambda": .45, "normal_volume_correction": True, "C1_lock_transition": True},
               "all_integer_point_attributes_preserved": True, "all_other_objects_geometry_matrices_visibility_preserved": True,
               "topology_sha256_unchanged": original_topology, "body_matrix_unchanged": original_body_matrix,
               "source_unchanged": sha(SOURCE) == EXPECTED, "renders": [],
               "limits": ["Geometry diagnostic pass is not art approval; three independent roles must inspect actual renders.",
                          "No topology, detached shoulder mesh, remesh, hiding of old tubes, face/head/distal-paw/prop edits.",
                          "Local actual surface triangle checks and finite locks; not continuous solid-volume or dynamic collision proof.",
                          "UV/groom binding not revalidated for changed surface; no shaded still, rig, animation, browser or deploy."]}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    if a.render:
        scene = bpy.context.scene; camera = scene.camera
        loc = camera.location.copy(); rot = camera.rotation_euler.copy(); scale = camera.data.ortho_scale
        for name, position, target, zoom in [
            ("front", None, None, scale),
            ("shoulders", Vector((0, -6, 2.23)), Vector((0, -.2, 2.10)), 2.9),
            ("three-quarter", Vector((6, -9, 3.9)), Vector((.09881, 0, 1.609)), scale)]:
            if position is None:
                camera.location = loc; camera.rotation_euler = rot; camera.data.ortho_scale = scale
            else:
                camera.location = position; camera.rotation_euler = (target - position).to_track_quat("-Z", "Y").to_euler(); camera.data.ortho_scale = zoom
            bpy.context.view_layer.update()
            image = out / f"gray-{name}.png"
            scene.render.filepath = str(image)
            bpy.ops.render.render(write_still=True)
            receipt["renders"].append({"file": image.name, "sha256": sha(image), "camera_matrix": list(map(list, camera.matrix_world)), "ortho_scale": camera.data.ortho_scale})
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("RESULT " + json.dumps({"native": str(native), "native_sha256": sha(native), "geometry_gate": gate, "renders": receipt["renders"]}), flush=True)


if __name__ == "__main__":
    main()
