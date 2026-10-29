"""Read-only sampled effector-point validation against actual evaluated strings.

Does not animate, bind, deform or save the cat. Does not test paw volume.
"""
import bpy
import json
from pathlib import Path
from mathutils import Vector
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location("extract", HERE / "extract-c35-profile.py")
extract = module_from_spec(spec)
spec.loader.exec_module(extract)


def main():
    source = extract.SOURCE
    before = extract.sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    bpy.context.view_layer.update()
    profile = json.loads((HERE / "evidence/c35-rig-profile.json").read_text())
    assert before == profile["source_native_sha256"]
    paths = json.loads((HERE / "evidence/target-path-samples.json").read_text())
    trees = {i: extract.actual_tree(bpy.data.objects[f"Guitar / string {i}"])[0] for i in range(1, 7)}
    notes = profile["note_targets"]["melody"]
    rows = []
    for item, note in zip(paths["melody"], notes):
        frames = item["frames"]
        sweep = [f for f in frames if f["right"]["phase"] == "sweep"]
        return_frames = [f for f in frames if f["right"]["phase"] == "return"]
        contacts = []
        for index, tree in trees.items():
            ds = [tree.find_nearest(Vector(f["right"]["world"]))[3] for f in sweep]
            contacts.append({"source_string": index, "minimum_sample_distance_u": min(ds)})
        target_min = next(r["minimum_sample_distance_u"] for r in contacts if r["source_string"] == note["source_string_index"])
        others = [r["minimum_sample_distance_u"] for r in contacts if r["source_string"] != note["source_string_index"]]
        return_min = min(tree.find_nearest(Vector(f["right"]["world"]))[3] for f in return_frames for tree in trees.values())
        assert target_min < 2e-6, (note["note"], target_min)
        assert min(others) > .025, (note["note"], min(others))
        assert return_min > .07, (note["note"], return_min)
        rows.append({"note": note["note"], "actual_six_tube_sweep_distances": contacts,
                     "selected_string_surface_near_u": target_min,
                     "unselected_tube_minimum_u": min(others),
                     "lifted_return_actual_tube_minimum_u": return_min,
                     "sweep_samples": len(sweep), "return_samples": len(return_frames)})
    # The targets are on distinct actual intervals, not a single hand position.
    physical_press_targets = [n["left_target_surface_world"] for n in notes if n["press_required"]]
    assert len(set(tuple(p) for p in physical_press_targets)) == 7
    for note in notes:
        if note["fret"]:
            lo, hi = note["actual_fret_interval_u"]
            assert lo < note["target_u"] < hi
    result = {"status": "sampled-effector-point-geometry-feasible-not-skin-animation-approval",
              "source_sha256": before, "source_file_unchanged": extract.sha(source) == before,
              "melody": rows, "all_seven_fretted_note_targets_distinct": True,
              "fretted_targets_strictly_inside_actual_fret_intervals": True,
              "open_E4_uses_no_press_target": notes[2]["left_target_surface_world"] is None,
              "limits": ["Finite target samples against evaluated tube triangles, not swept paw-volume collisions or finger deformation.",
                         "Single-note point remains >.025u from other five tubes during sweep; real paw/pick size can invalidate this.",
                         "A front-surface near hit within 2e-6u is a numeric path diagnostic, not force/pressure or strict C35 contact certification.",
                         "Chord loop controller crossings validated in JS, not animated chord fingering or audio."]}
    assert result["source_file_unchanged"]
    (HERE / "evidence/path-geometry-probe.json").write_text(json.dumps(result, indent=2) + "\n")
    print("RESULT " + json.dumps(result))


if __name__ == "__main__":
    main()
