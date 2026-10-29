"""Prepare the actual Godot export for static Pages' 25 MiB file limit.

Only the official WASM is gzip-compressed; browser decodes its exact bytes.
No engine substitution, Worker, server decompression, or art-acceptance claim.
"""
from pathlib import Path
import gzip
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'public/labs/character-compare/godot'
sha = lambda b: hashlib.sha256(b).hexdigest()
wasm = OUT / 'index.wasm'
raw = wasm.read_bytes() if wasm.exists() else gzip.decompress((OUT / 'index.wasm.gz').read_bytes())
compressed = gzip.compress(raw, compresslevel=9, mtime=0)
assert gzip.decompress(compressed) == raw
assert len(compressed) < 25 * 1024 * 1024
(OUT / 'index.wasm.gz').write_bytes(compressed)
archive = ROOT / 'artifacts/godot-web-setup/final-uncompressed-index.wasm'
archive.write_bytes(raw)
if wasm.exists():
    wasm.unlink()  # Generated artifact retained in local setup archive above.
html = OUT / 'index.html'
text = html.read_text()
needle = '<script src="index.js"></script>'
assert needle in text
if '<script src="compressed-wasm.js"></script>' not in text:
    text = text.replace(needle, '<script src="compressed-wasm.js"></script>\n\t\t' + needle)
styles = re.findall(r'<style\b[^>]*>(.*?)</style>', text, flags=re.S | re.I)
if styles:
    assert len(styles) == 1
    (OUT / 'godot-page.css').write_text(styles[0].strip()+'\n')
    text = re.sub(r'<style\b[^>]*>.*?</style>', '<link rel="stylesheet" href="godot-page.css">', text, flags=re.S | re.I)
scripts = re.findall(r'<script\s*>(.*?)</script>', text, flags=re.S | re.I)
if scripts:
    assert len(scripts) == 1
    (OUT / 'godot-start.js').write_text(scripts[0].strip()+'\n')
    text = re.sub(r'<script\s*>.*?</script>', '<script src="godot-start.js"></script>', text, flags=re.S | re.I)
assert not re.search(r'<style\b|<script\s*>', text, flags=re.I)
html.write_text(text)
receipt = dict(scope='Actual Godot 4.7.2 single-thread Compatibility export; research character only',
               wasm_uncompressed_bytes=len(raw), wasm_uncompressed_sha256=sha(raw),
               wasm_gzip_bytes=len(compressed), wasm_gzip_sha256=sha(compressed),
               exact_gzip_roundtrip=True, compression='gzip level9 mtime0',
               files=[dict(name=p.name, bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
                      for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'export-evidence.json'])
(OUT / 'export-evidence.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))
