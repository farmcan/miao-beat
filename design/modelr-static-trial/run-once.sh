#!/bin/zsh
set -eu
TASK_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TASK_DIR="$TASK_ROOT/artifacts/modelr-trial"
python3 - "$TASK_DIR" <<'PY'
from pathlib import Path
import sys,json,hashlib
p=Path(sys.argv[1]);repo='zimengxiong/hunyuan3d-mlx-shape-small'
spec=json.loads((p/'source/model_manifest.json').read_text())['repos'][repo]
assert spec['revision']=='b7536809d38ad13fe6a9b7769a41fd5d42e520df'
for f in spec['files']:
 path=p/'weights/shape-small'/f['path']
 assert path.stat().st_size==f['bytes'],path
 assert hashlib.file_digest(path.open('rb'),'sha256').hexdigest()==f['sha256'],path
source=p.parent.parent/'public/character/instrument-scenes-v1/guitar/idle.jpg'
assert hashlib.file_digest(source.open('rb'),'sha256').hexdigest()=='4418fd737891283f42568306cb427b1f7604a86cae5513b1d6c49b3c31f338d1'
sentinel=p/'output/shape-attempt-started.json'
# Exclusive claim prevents accidental second generation or duplicate live process.
with sentinel.open('x') as h:
 import datetime
 json.dump({'seed':17,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'started'},h)
PY
cd "$TASK_ROOT"
/usr/bin/time -l "$TASK_DIR/build/Build/Products/Release/MiaoShapeCLI" \
 "$TASK_ROOT/public/character/instrument-scenes-v1/guitar/idle.jpg" \
 "$TASK_DIR/weights/shape-small/model.fp16.safetensors" \
 "$TASK_DIR/output/miao-shape-seed17.glb"
