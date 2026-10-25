#!/usr/bin/env python3
"""Export reviewed whole-character frames; preserve one shared crop/scale."""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[1]
source = root / 'assets-source/motion/keyboard-take-20261025/source.mp4'
expected = '17a223bc41021898f120d2660b4c0787660a07ff157d1910d8f2f6f2572bd8a5'
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected, 'Unreviewed motion source'
frames = [234, 230, 232, 152, 154, 156, 84, 86, 88, 108, 110, 112, 228]
temporary = root / 'artifacts/keyboard-motion-export'
temporary.mkdir(exist_ok=True)
output = root / 'public/character'
for index, frame in enumerate(frames):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(source),
                    '-vf', f'select=eq(n\\,{frame}),crop=840:720:220:0,scale=480:412:flags=lanczos,setsar=1',
                    '-frames:v', '1', '-y', str(temporary / f'frame-{index:02d}.png')], check=True)
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-framerate', '1',
                '-i', str(temporary / 'frame-%02d.png'), '-vf', 'tile=4x4', '-frames:v', '1',
                '-c:v', 'mjpeg', '-q:v', '2', '-y', str(output / 'keyboard-poses-v1.jpg')], check=True)
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(source),
                '-map', '0:v:0', '-c:v', 'copy', '-an', '-map_metadata', '-1', '-movflags', '+faststart',
                '-y', str(output / 'keyboard-demo-v1.mp4')], check=True)
manifest = {
    'version': 1, 'date': '2026-10-25', 'atlas': 'keyboard-poses-v1.jpg',
    'width': 480, 'height': 412, 'columns': 4, 'frameCount': len(frames), 'idle': 0,
    'source': {'sha256': expected, 'fps': 24, 'durationSeconds': 10.041667,
               'inputBytes': source.stat().st_size, 'hasAudio': False,
               'provenance': 'User-supplied generated video based on original project orange-cat artwork',
               'sourceURLSaved': False},
    'export': {'crop': [220, 0, 840, 720], 'sourceFrames': frames,
               'method': 'Complete captured cat and keyboard per frame; shared crop/scale, no limb compositing'},
    'actions': {'leftLow': {'contact': 1, 'release': [2, 0]},
                'leftMid': {'contact': 3, 'release': [4, 5]},
                'rightOuter': {'contact': 6, 'release': [7, 8]},
                'rightMid': {'contact': 9, 'release': [10, 11]},
                'both': {'contact': 12, 'release': [1, 0]}},
    'limits': ['Representative pitch-region poses, not thirteen distinct physical key contacts',
               'Whole poses include coupled body and opposite-paw changes; not independent limb control',
               'Browser input timing and human naturalness require separate verification'],
}
(output / 'keyboard-motion-v1.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('Exported 13 complete poses and a self-hosted silent source preview; no signed URL published')
