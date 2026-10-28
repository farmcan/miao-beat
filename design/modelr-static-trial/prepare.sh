#!/bin/zsh
set -eu
TASK_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TASK_DIR="$TASK_ROOT/artifacts/modelr-trial"
TASK_SOURCE="$TASK_DIR/source"
mkdir -p "$TASK_SOURCE/TrialCLI" "$TASK_DIR/weights/shape-small" "$TASK_DIR/output"
if [ ! -e "$TASK_DIR/modelr-source.tar.gz" ]; then
 curl --fail -L --connect-timeout 20 --max-time 180 \
  https://codeload.github.com/ZimengXiong/Modelr/tar.gz/c6a10959d2499477962aed5643fcb172dbf09457 \
  -o "$TASK_DIR/modelr-source.tar.gz"
fi
python3 - "$TASK_DIR/modelr-source.tar.gz" <<'PY'
import hashlib,sys
assert hashlib.file_digest(open(sys.argv[1],'rb'),'sha256').hexdigest()=='ae6333ffe5ac47a67a0867820133f6a47c889b8a202a75e5542749d1e9fc9544'
PY
if [ ! -e "$TASK_SOURCE/Packages/Hy3DMLX/Package.swift" ]; then
 tar -xzf "$TASK_DIR/modelr-source.tar.gz" -C "$TASK_SOURCE" --strip-components=1
fi
cp "$TASK_ROOT/design/modelr-static-trial/download-shape.py" "$TASK_DIR/download-shape.py"
if [ ! -e "$TASK_DIR/weights/shape-small/config.yaml" ]; then
 curl --fail -L --connect-timeout 20 --max-time 45 \
  https://huggingface.co/zimengxiong/hunyuan3d-mlx-shape-small/resolve/b7536809d38ad13fe6a9b7769a41fd5d42e520df/config.yaml \
  -o "$TASK_DIR/weights/shape-small/config.yaml"
fi
cp "$TASK_ROOT/design/modelr-static-trial/main.swift" "$TASK_SOURCE/TrialCLI/main.swift"
cp "$TASK_ROOT/design/modelr-static-trial/trial.yml" "$TASK_SOURCE/trial.yml"
python3 - "$TASK_SOURCE/vendor/mlx-swift/Package.swift" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text()
if '"mlx-generated/metal"' not in s:
 s=s.replace('// vendor docs\n','// Use verified matching official MLX 0.31.1 precompiled metallib.\n        "mlx-generated/metal",\n        // vendor docs\n')
p.write_text(s)
PY
if [ ! -e "$TASK_DIR/mlx-metal-0.31.1.whl" ]; then
 curl --fail -L --connect-timeout 20 --max-time 180 \
  https://files.pythonhosted.org/packages/51/bc/987cb99e3aafb296aa11ce5133838a10eae8447edd53168d0804d4fb3a14/mlx_metal-0.31.1-py3-none-macosx_26_0_arm64.whl \
  -o "$TASK_DIR/mlx-metal-0.31.1.whl"
fi
cd "$TASK_SOURCE"
xcodegen generate --spec trial.yml
xcodebuild -project MiaoShapeCLI.xcodeproj -scheme MiaoShapeCLI \
 -configuration Release -derivedDataPath ../build CODE_SIGNING_ALLOWED=NO build
python3 - "$TASK_DIR" <<'PY'
from pathlib import Path
import sys,hashlib,zipfile
p=Path(sys.argv[1]);wheel=p/'mlx-metal-0.31.1.whl'
assert hashlib.file_digest(wheel.open('rb'),'sha256').hexdigest()=='e7324b7c56b519ae67c025d3ced07e5d35bc3a9f19d4c45fe4927f385148c59e'
data=zipfile.ZipFile(wheel).read('mlx/lib/mlx.metallib')
assert hashlib.sha256(data).hexdigest()=='198488eb61359e953580a9c4530400feee1a06dd2f28a930a6ffa58aec66a597'
(p/'build/Build/Products/Release/mlx.metallib').write_bytes(data)
PY
"$TASK_DIR/build/Build/Products/Release/MiaoShapeCLI" --selftest
