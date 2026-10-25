import concurrent.futures, hashlib, json, subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
local=json.loads((root/'dist/release.json').read_text())
def get(name):
 return subprocess.check_output(['curl','--fail','--silent','--show-error','--max-time','25','https://miao-beat.pages.dev/'+name+'?v='+local['commit'][:12]])
assert json.loads(get('release.json'))==local,'Production commit/manifest differs'
def check(item):
 name,digest=item
 if name in ('_headers','_worker.js','_routes.json'):return # deployment configuration, not public routes
 route=name[:-10] if name.endswith('index.html') else name
 assert hashlib.sha256(get(route)).hexdigest()==digest,'Production bytes differ: '+name
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(check,local['files'].items()))
config_files={'_headers','_worker.js','_routes.json'}
print('Verified canonical Miao Beat commit '+local['commit']+' and '+str(sum(name not in config_files for name in local['files']))+' public source files')
