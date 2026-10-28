from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess, hashlib, json, time, os
root=Path(__file__).resolve().parent
manifest=json.loads((root/'source/model_manifest.json').read_text())['repos']['zimengxiong/hunyuan3d-mlx-shape-small']
f=manifest['files'][1]
out=root/'weights/shape-small'
part=out/'model.fp16.safetensors.part'
size=f['bytes']; step=256*1024*1024; chunks=out/'chunks'; chunks.mkdir(exist_ok=True)
# Preserve every already-downloaded prefix byte; transfer subsequent independent ranges.
offset=part.stat().st_size if part.exists() else 0
base=f"https://huggingface.co/zimengxiong/hunyuan3d-mlx-shape-small/resolve/{manifest['revision']}/{f['path']}"
ranges=[(i,a,min(a+step-1,size-1)) for i,a in enumerate(range(offset,size,step))]
def get(spec):
 i,a,b=spec; target=chunks/f'{a:012d}-{b:012d}.part'; expected=b-a+1
 for attempt in range(2):
  done=target.stat().st_size if target.exists() else 0
  if done==expected: return str(target)
  if done>expected: raise RuntimeError(f'oversize chunk {target}')
  tail=chunks/f'{a:012d}.tail'
  headers=chunks/f'{a:012d}.headers'
  with (chunks/f'{a:012d}.log').open('a') as log:
   r=subprocess.run(['curl','--http1.1','--fail','-L','--connect-timeout','20','--max-time','600','-D',str(headers),'-r',f'{a+done}-{b}',base,'-o',str(tail)],stdout=log,stderr=log)
  received=tail.stat().st_size if tail.exists() else 0
  # A CDN response must explicitly honor the requested byte range before appending.
  h=headers.read_text() if headers.exists() else ''
  expected_header=f'content-range: bytes {a+done}-'
  if expected_header in h.lower() and 0<received<=expected-done:
   with target.open('ab') as dst,tail.open('rb') as src:
    while data:=src.read(8*1024*1024): dst.write(data)
   tail.unlink()
  elif received: raise RuntimeError(f'range ignored or invalid: {a+done}-{b}')
  if target.exists() and target.stat().st_size==expected:
   print(f'chunk {i} ready {expected}',flush=True); return str(target)
  print(f'chunk {i} partial attempt {attempt} rc={r.returncode} bytes={target.stat().st_size if target.exists() else 0}',flush=True)
 raise RuntimeError(f'range {a}-{b} incomplete after bounded retries')
print(f'prefix={offset} remaining={size-offset} ranges={len(ranges)} workers=4',flush=True)
with ThreadPoolExecutor(max_workers=4) as pool: paths=list(pool.map(get,ranges))
assembled=out/'model.fp16.safetensors.assembled'
with assembled.open('wb') as dst:
 for src in [part,*map(Path,paths)]:
  if not src.exists(): continue
  with src.open('rb') as h:
   while data:=h.read(8*1024*1024): dst.write(data)
digest=hashlib.file_digest(assembled.open('rb'),'sha256').hexdigest()
assert assembled.stat().st_size==size,assembled.stat().st_size
assert digest==f['sha256'],digest
final=out/f['path']; assembled.rename(final)
(root/'weight-verification.json').write_text(json.dumps({'sha256':digest,'bytes':size,'revision':manifest['revision'],'verified':True},indent=2))
print('VERIFIED '+digest,flush=True)
