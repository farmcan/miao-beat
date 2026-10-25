#!/usr/bin/env python3
"""Encode complete generated guitar/drum scenes; never crop or combine limbs."""
import hashlib, json, struct, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / 'design/instrument-whole-scenes-2026-10-25'
plan = json.loads((source / 'plan.json').read_text())['frames']
missing = [mode + ':' + p['id'] for mode, poses in plan.items() for p in poses
           if not (source / mode / 'frames' / (p['id'] + '.png')).is_file()]
assert not missing, 'Generation incomplete: ' + ','.join(missing)
out = root / 'public/character/instrument-scenes-v1'
modes, provenance = {}, []
for mode, poses in plan.items():
    assert len(poses) == {'guitar': 18, 'drums': 25}[mode]
    (out / mode).mkdir(parents=True, exist_ok=True)
    frames = {}
    for pose in poses:
        name = pose['id']
        original = source / mode / 'frames' / (name + '.png')
        data = original.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        width, height = struct.unpack('>II', data[16:24])
        assert width == height and width >= 1254, 'Unreviewed dimensions: ' + str(original)
        filename = mode + '/' + name + '.jpg'
        target = out / filename
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(original),
                        '-vf', 'scale=1254:1254:flags=lanczos', '-frames:v', '1',
                        '-c:v', 'mjpeg', '-q:v', '2', '-y', str(target)], check=True)
        encoded = target.read_bytes()
        assert len(encoded) < 2000000
        frames[name] = filename
        provenance.append({'mode': mode, 'id': name, 'source': str(original.relative_to(root)),
                           'sourceSha256': hashlib.sha256(data).hexdigest(), 'file': filename,
                           'bytes': len(encoded), 'sha256': hashlib.sha256(encoded).hexdigest(),
                           'keys': [k['code'] for k in pose['keys']]})
    modes[mode] = {'frames': frames}
manifest = {'version': 1, 'date': '2026-10-25', 'width': 1254, 'height': 1254,
            'modes': modes, 'method': 'Each state is one complete generated cat and instrument scene',
            'provenance': provenance,
            'limits': ['Discrete poses, not generated continuous video',
                       'Guitar paw contact is a cartoon gesture, not a fingering lesson',
                       'Most recent target per available paw; all triggered sounds remain independent',
                       'Marimba motion remains unfinished; physical-device and user aesthetic acceptance pending']}
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('Packaged ' + str(len(provenance)) + ' whole instrument scenes; ' +
      str(sum(p['bytes'] for p in provenance)) + ' JPEG bytes')
