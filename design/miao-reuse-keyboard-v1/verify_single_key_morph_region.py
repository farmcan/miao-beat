"""Finite final-GLB key/black010 local-region check; never a component exemption.

Read-only geometry checks in official 3.6.23. No frame/action/render/native save.
This complements (does not replace) the complete hand/sleeve morph checks in
export_single_key_morph.py. Boundary and ray disagreement remain explicit.
"""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_single_key_morph import mesh_record, sha

OUT = ROOT / 'artifacts/miao-reuse-keyboard-v1/single-key-web-morph'


def segment_triangle(p0, p1, a, b, c):
    direction = p1 - p0
    edge1, edge2 = b - a, c - a
    h = direction.cross(edge2)
    determinant = edge1.dot(h)
    if abs(determinant) < 1e-15:
        return None
    s = p0 - a
    u = s.dot(h) / determinant
    if not -1e-7 <= u <= 1 + 1e-7:
        return None
    q = s.cross(edge1)
    v = direction.dot(q) / determinant
    if v < -1e-7 or u + v > 1 + 1e-7:
        return None
    distance = edge2.dot(q) / determinant
    return p0 + direction * distance if -1e-7 <= distance <= 1 + 1e-7 else None


DIRECTIONS = [Vector(v).normalized() for v in [(1, .314159, .1729), (-.247, 1, .413), (.271, -.381, 1)]]


def member(record, point):
    nearest = record['tree'].find_nearest(point)
    distance = nearest[3]
    if distance is not None and distance < 5e-7:
        return 'boundary', distance
    votes = []
    for direction in DIRECTIONS:
        origin = point + direction * 1e-8
        count = 0
        for _ in range(30):
            hit, _, _, _ = record['tree'].ray_cast(origin, direction, 3)
            if hit is None:
                break
            count += 1
            origin = hit + direction * 1e-7
        votes.append(count % 2)
    return ('inside' if all(votes) else 'outside' if not any(votes) else 'unknown'), distance


def main():
    assert bpy.app.version == (3, 6, 23)
    metadata = json.loads((OUT / 'metadata.json').read_text())
    model = OUT / metadata['modelFile']
    before = sha(model)
    assert before == metadata['modelSha256']
    bpy.ops.import_scene.gltf(filepath=str(model))
    key = bpy.data.objects['MiaoKeyC4']
    black = mesh_record(bpy.data.objects['Raised black piano key.010_WEB'])
    initial = mesh_record(key)
    key0 = key.matrix_world.copy()
    p = metadata['pivotThree']
    pivot = Vector((p[0], -p[2], p[1]))
    rows = []
    for theta in sorted({row['theta'] for row in metadata['trajectory']}):
        key.matrix_world = Matrix.Translation(pivot) @ Matrix.Rotation(theta, 4, 'X') @ Matrix.Translation(-pivot) @ key0
        bpy.context.view_layer.update()
        current = mesh_record(key)
        pairs = current['tree'].overlap(black['tree'])
        points = []
        for a, b in pairs:
            va = [current['p'][i] for i in current['t'][a]]
            vb = [black['p'][i] for i in black['t'][b]]
            for triangle, other in [(va, vb), (vb, va)]:
                for i in range(3):
                    hit = segment_triangle(triangle[i], triangle[(i + 1) % 3], *other)
                    if hit is not None:
                        points.append(hit)
        for point in current['p']:
            if member(black, point)[0] == 'inside':
                points.append(point)
        for point in black['p']:
            if member(current, point)[0] == 'inside':
                points.append(point)
        unique = {tuple(round(c, 8) for c in point): point for point in points}
        counts = {'inside': 0, 'boundary': 0, 'outside': 0, 'unknown': 0}
        unresolved = []
        for point in unique.values():
            state, distance = member(initial, point)
            counts[state] += 1
            if state in {'outside', 'unknown'}:
                unresolved.append({'point': list(point), 'membership': state, 'nearest_source_white_m': distance})
        row = {'theta': theta, 'actual_final_glb_triangle_pairs': len(pairs),
               'actual_local_intersection_samples': len(unique),
               'membership_in_original_white014_solid': counts,
               'outside_or_unknown_points': unresolved}
        rows.append(row)
        print('FINAL_GLB_LOCAL_REGION', json.dumps(row), flush=True)
    assert before == sha(model)
    outside = sum(row['membership_in_original_white014_solid']['outside'] for row in rows)
    unknown = sum(row['membership_in_original_white014_solid']['unknown'] for row in rows)
    result = {'status': 'FINITE_LOCAL_SAMPLES_NO_CONFIRMED_EXTENSION' if not outside else 'STOP_CONFIRMED_LOCAL_EXTENSION',
              'model_sha256': before, 'rows': rows, 'confirmed_outside': outside,
              'ray_disagreement_unknown': unknown,
              'scope': 'Every actual key014/black010 triangle intersection edge-crossing and strict-inside mesh-vertex sample tested against original key014 solid; no whole-black or whole-white component exemption.',
              'remaining_unknown': 'near-boundary/subtriangle/continuous-volume behavior not proven. Ray disagreements and boundary counts are explicit; not a complete mechanical piano model.',
              'rendered': False, 'new_geometry': False, 'model_unchanged': True}
    (OUT / 'final-glb-local-region-check.json').write_text(json.dumps(result, indent=2) + '\n')
    summary = {'receipt': 'final-glb-local-region-check.json', 'status': result['status'],
               'confirmedOutside': outside, 'rayDisagreementUnknown': unknown,
               'sampledKeyAngles': len(rows), 'scope': result['scope'],
               'remainingUnknown': result['remaining_unknown']}
    metadata['validation']['finalGlbLocalRegionCheck'] = summary
    (OUT / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    receipt = json.loads((OUT / 'receipt.json').read_text())
    receipt['final_glb_local_region_check'] = summary
    (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    assert not outside, 'Confirmed extension beyond original finite key/black overlap region'


if __name__ == '__main__':
    main()
