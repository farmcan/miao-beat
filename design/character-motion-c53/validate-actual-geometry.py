"""Read-only C53 actual controller samples vs C35 evaluated tube/wood triangles.

Reuses v2 actual_tree/extraction source, never saves, binds, deforms or renders.
Surface-near 2e-6u diagnostic band is retained, not widened for C1. This is a
finite point-path test; it cannot certify paw volume or continuous solid safety.
"""
import bpy
import hashlib
import json
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = spec_from_file_location("c53_v2_extract", HERE.parent / "character-motion-v2/extract-c35-profile.py")
extract = module_from_spec(spec)
spec.loader.exec_module(extract)
EPS = 2e-6


def main():
    source = extract.SOURCE
    before = extract.sha(source)
    assert before == extract.EXPECTED
    bpy.ops.wm.open_mainfile(filepath=str(source))
    bpy.context.view_layer.update()
    samples_path = HERE / "evidence/target-path-samples.json"
    paths = json.loads(samples_path.read_text())
    trees = {i: extract.actual_tree(bpy.data.objects[f"Guitar / string {i}"])[0] for i in range(1, 7)}
    wood_names = ["Guitar / rosewood body", "Guitar / spruce soundboard", "Guitar / neck", "Guitar / ebony fretboard"]
    woods = {name: extract.actual_tree(bpy.data.objects[name])[0] for name in wood_names}
    failures, rows = [], []
    cache = {}
    normal = Vector((0, -1, 0))
    for trace in paths["traces"]:
        minimum_other = float("inf")
        minimum_wood = float("inf")
        minimum_return = float("inf")
        minimum_tube_signed = float("inf")
        near_boundary = 0
        segment_hits = 0
        last = None
        for frame in trace["frames"]:
            right = frame["right"]
            key = tuple(right["world"])
            p = Vector(key)
            if key not in cache:
                td, signed = {}, {}
                for i, tree in trees.items():
                    nearest, n, tri, distance = tree.find_nearest(p)
                    td[i] = distance
                    signed[i] = (p - nearest).dot(n)
                wd, ws = {}, {}
                for name, tree in woods.items():
                    nearest, n, tri, distance = tree.find_nearest(p)
                    wd[name] = distance
                    ws[name] = (p - nearest).dot(n)
                cache[key] = (td, signed, wd, ws)
            td, signed, wd, ws = cache[key]
            minimum_wood = min(minimum_wood, *wd.values())
            minimum_tube_signed = min(minimum_tube_signed, *signed.values())
            # Closest-normal sign is a local diagnostic, not a generalized
            # winding proof. All tested points are in the same short strike rail.
            if min(signed.values()) < -EPS:
                failures.append({"trace": trace["label"], "timeMs": frame["timeMs"], "kind": "tube_interior_local_normal", "signed": signed})
            if min(ws.values()) < -EPS or min(wd.values()) < EPS:
                failures.append({"trace": trace["label"], "timeMs": frame["timeMs"], "kind": "wood_interior_or_boundary", "signed": ws, "distance": wd})
            allowed = right["permittedSourceStrings"]
            other = [d for i, d in td.items() if i not in allowed]
            if other:
                minimum_other = min(minimum_other, *other)
                if min(other) <= .025:
                    failures.append({"trace": trace["label"], "timeMs": frame["timeMs"], "kind": "unpermitted_tube_clearance", "distance": min(other), "phase": right["phase"]})
            if right["phase"] == "return":
                minimum_return = min(minimum_return, *td.values())
                if min(td.values()) <= .07:
                    failures.append({"trace": trace["label"], "timeMs": frame["timeMs"], "kind": "return_clearance", "distance": min(td.values())})
            near_boundary += sum(d < EPS for d in td.values())
            if last is not None:
                delta = p - last
                length = delta.length
                if length > 1e-10:
                    for name, tree in woods.items():
                        hit, n, tri, distance = tree.ray_cast(last, delta / length, length)
                        if hit is not None:
                            segment_hits += 1
                            failures.append({"trace": trace["label"], "timeMs": frame["timeMs"], "kind": "wood_segment_surface_hit", "object": name})
            last = p
        rows.append({"trace": trace["label"], "samples": len(trace["frames"]),
                     "unpermitted_tube_minimum_u": minimum_other,
                     "wood_actual_triangle_minimum_u": minimum_wood,
                     "lifted_return_minimum_u": minimum_return,
                     "tube_minimum_signed_nearest_normal_u": minimum_tube_signed,
                     "tube_near_boundary_sample_count": near_boundary,
                     "wood_polyline_segment_hits": segment_hits})
    result = {"status": "sampled-point-path-pass" if not failures else "sampled-point-path-FAIL",
              "source_sha256": before, "source_unchanged": extract.sha(source) == before,
              "controller_samples_sha256": hashlib.sha256(samples_path.read_bytes()).hexdigest(),
              "trace_count": len(rows), "frame_count": sum(r["samples"] for r in rows),
              "unique_sample_positions": len(cache), "actual_tube_count": 6, "actual_wood_objects": wood_names,
              "surface_near_diagnostic_band_u": EPS, "unpermitted_tube_threshold_u": .025,
              "lifted_return_threshold_u": .07, "failure_count": len(failures), "failures": failures[:100],
              "traces": rows,
              "limits": ["Finite actual target samples and straight chords between them, not the full analytic Hermite swept volume.",
                         "Signed closest-normal tests are local orientation diagnostics, not full solid-angle containment proofs.",
                         "Near-boundary samples inside 2e-6u are surface-near diagnostics, not strict nonpenetration/force certification.",
                         "Only four named wooden objects, not all hardware/rosettes/guitar objects.",
                         "No cat, paw volume, skin binding, deformation, audio, browser or animation acceptance."]}
    assert result["source_unchanged"]
    (HERE / "evidence/actual-geometry-validation.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print("RESULT " + json.dumps({k: v for k, v in result.items() if k not in ["traces", "failures"]}), flush=True)
    if failures:
        print("FIRST_FAILURE " + json.dumps(failures[0]), flush=True)
        raise RuntimeError(f"C53 actual geometry finite path probe failed: {len(failures)}")


if __name__ == "__main__":
    main()
