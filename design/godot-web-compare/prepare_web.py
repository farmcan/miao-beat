"""Prepare the actual Godot export for static Pages' 25 MiB file limit.

Only the official WASM is gzip-compressed; browser decodes its exact bytes.
No engine substitution, Worker, server decompression, or art-acceptance claim.
"""
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'public/labs/character-compare/godot'
sha = lambda b: hashlib.sha256(b).hexdigest()
wasm = OUT / 'index.wasm'
raw = wasm.read_bytes()
compressed = gzip.compress(raw, compresslevel=9, mtime=0)
assert gzip.decompress(compressed) == raw
assert len(compressed) < 25 * 1024 * 1024
(OUT / 'index.wasm.gz').write_bytes(compressed)
archive = ROOT / 'artifacts/godot-web-setup/final-uncompressed-index.wasm'
archive.write_bytes(raw)
wasm.unlink()  # Generated artifact retained in local setup archive above.
html = OUT / 'index.html'
text = html.read_text()
needle = '<script src="index.js"></script>'
assert needle in text
text = text.replace(needle, '<script src="compressed-wasm.js"></script>\n\t\t' + needle)
html.write_text(text)
receipt = dict(scope='Actual Godot 4.7.2 single-thread Compatibility export; research character only',
               wasm_uncompressed_bytes=len(raw), wasm_uncompressed_sha256=sha(raw),
               wasm_gzip_bytes=len(compressed), wasm_gzip_sha256=sha(compressed),
               exact_gzip_roundtrip=True, compression='gzip level9 mtime0',
               files=[dict(name=p.name, bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
                      for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'export-evidence.json'])
(OUT / 'export-evidence.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))
