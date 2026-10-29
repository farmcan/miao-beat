"""Read-only solid-angle adjudication of C40's 20 ambiguous ray probes.

Formula: van Oosterom & Strackee, 1983, doi:10.1109/TBME.1983.325207.
https://pubmed.ncbi.nlm.nih.gov/6832789/
Generalized winding-number use: https://libigl.github.io/tutorial/#signed-distance
No upstream implementation is copied. This does not grant an art/motion pass.
Run in factory-startup Blender; never saves/changes the source native file.
"""
from pathlib import Path
import hashlib
import json
import math
import time

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "artifacts/character-shoulder-c40/diagnostic-c40-left-shoulder-failed.blend"
OUT = ROOT / "artifacts/character-shoulder-c44-readback"
OUT.mkdir(parents=True, exist_ok=True)


def winding(points, query):
    total = 0.0
    for start in range(0, len(points), 65536):
        a, b, c = np.moveaxis(points[start:start + 65536] - query, 1, 0)
        la, lb, lc = (np.linalg.norm(v, axis=1) for v in (a, b, c))
        determinant = np.einsum("ij,ij->i", a, np.cross(b, c))
        denominator = (la * lb * lc + np.einsum("ij,ij->i", a, b) * lc
                       + np.einsum("ij,ij->i", b, c) * la
                       + np.einsum("ij,ij->i", c, a) * lb)
        total += float(np.sum(2.0 * np.arctan2(determinant, denominator), dtype=np.float64))
    return total / (4.0 * math.pi)


# Closed outward tetrahedron: a sign/normalization check before the real mesh.
tv = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
tf = np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]])
unit = {"inside": winding(tv[tf], np.array([.1, .1, .1])),
        "outside": winding(tv[tf], np.array([2., 2., 2.]))}
assert abs(unit["inside"] - 1.) < 1e-12 and abs(unit["outside"]) < 1e-12, unit
before_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert before_sha == "6dbc4183a57117079c1479b0c1361e52995f66ff3eaef3f2d3e00e1cba8bdc00"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
body = bpy.data.objects["Miao / continuous pear and rounded-square face"]
evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = evaluated.to_mesh()
mesh.calc_loop_triangles()
vertices = np.empty(len(mesh.vertices) * 3, np.float64)
mesh.vertices.foreach_get("co", vertices)
vertices = vertices.reshape((-1, 3))
triangles = np.empty(len(mesh.loop_triangles) * 3, np.int32)
mesh.loop_triangles.foreach_get("vertices", triangles)
triangles = triangles.reshape((-1, 3))
actual_triangles = vertices[triangles]
old = json.loads((ROOT / "artifacts/character-shoulder-c40/actual-normal-side-parity.json").read_text())
ambiguous = [r for r in old["rows"] if not r.get("outward_correct", False)]
controls = [r for r in old["rows"] if r.get("outward_correct", False)][::100]
assert len(ambiguous) == 20
rows = []
started = time.monotonic()
for index, row in enumerate(ambiguous + controls):
    p = vertices[row["vertices"]]
    center = p.mean(axis=0)
    normal = np.cross(p[1] - p[0], p[2] - p[0])
    normal /= np.linalg.norm(normal)
    samples = []
    offsets = [2e-6, 1e-5, 2e-5] if index < len(ambiguous) else [2e-5]
    for offset in offsets:
        outside = winding(actual_triangles, center + normal * offset)
        inside = winding(actual_triangles, center - normal * offset)
        samples.append({"offset_u": offset, "outside_winding": outside,
                        "inside_winding": inside,
                        "outward_correct": abs(outside) < 1e-6 and abs(inside - 1.) < 1e-6})
    rows.append({"vertices": row["vertices"], "previously_ambiguous": index < 20,
                 "samples": samples, "all_offsets_correct": all(s["outward_correct"] for s in samples)})
    print(json.dumps({"probe": index + 1, "of": len(ambiguous) + len(controls),
                      "all_offsets_correct": rows[-1]["all_offsets_correct"]}), flush=True)
evaluated.to_mesh_clear()
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before_sha
result = {"status": "readonly-normal-side-adjudication", "source_sha256": before_sha,
          "source_unchanged": True, "actual_triangles": len(triangles), "tetrahedron_check": unit,
          "ambiguous_probes": len(ambiguous), "control_probes": len(controls),
          "resolved_correct": sum(r["all_offsets_correct"] for r in rows[:20]),
          "unresolved_or_counterexamples": sum(not r["all_offsets_correct"] for r in rows[:20]),
          "method": "Signed triangle solid angles, float64 sum / 4pi; three declared normal offsets; no ray stepping",
          "scope": "Only the previously sampled candidate triangles. Not a global collision, art, or animation acceptance.",
          "seconds": time.monotonic() - started, "rows": rows}
(OUT / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "rows"}), flush=True)
