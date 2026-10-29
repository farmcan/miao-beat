"""Verify the extracted review archive using Python standard library only."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'PACKAGE_MANIFEST.json').read_text())
for item in manifest['files']:
    path=ROOT/item['path']
    assert path.is_file(),item['path']
    data=path.read_bytes()
    assert len(data)==item['bytes'],item['path']
    assert hashlib.sha256(data).hexdigest()==item['sha256'],item['path']
allowed={item['path'] for item in manifest['files']}|{'PACKAGE_MANIFEST.json','SHA256SUMS'}
actual={path.relative_to(ROOT).as_posix() for path in ROOT.rglob('*') if path.is_file() and 'output' not in path.relative_to(ROOT).parts and path.relative_to(ROOT).parts[:2]!=('artifacts','handoff')}
# Output receipts/archives may be created after verification; original package
# file list is the authoritative whitelist, not a recursive source copy.
unexpected=actual-allowed
assert not unexpected,sorted(unexpected)
print(json.dumps({'status':'PACKAGE_FILES_PASS','files':len(manifest['files']),'role':'static review only'}))
