#!/usr/bin/env python3
"""Owner-only aggregate report; requires existing Wrangler/D1 credentials."""
import argparse, json, os, subprocess, sys
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--days',type=int,default=7)
p.add_argument('--internal',action='store_true',help='QA traffic only; default is external')
p.add_argument('--wrangler',default=os.environ.get('WRANGLER_BIN','wrangler'))
a=p.parse_args()
if not 1<=a.days<=90:p.error('--days must be 1..90')
root=Path(__file__).resolve().parents[1]
traffic='internal' if a.internal else 'external'
sql=f"SELECT event_day,source_project,target_project,placement,event_kind,count FROM miao_family_referrals WHERE traffic_type='{traffic}' AND event_day>=date('now','+8 hours','-{a.days-1} days') ORDER BY event_day,source_project,target_project,placement,event_kind"
command=['node',a.wrangler] if a.wrangler.endswith('.js') else [a.wrangler]
rows=[];errors={}
for name,config in [('miaoti-stats',root/'wrangler.jsonc'),('miaotarot-data',root.parent/'tarot/wrangler.jsonc')]:
 try:
  r=subprocess.run(command+['d1','execute',name,'--config',str(config),'--remote','--command',sql,'--json'],capture_output=True,text=True,timeout=60,check=True)
  data=json.loads(r.stdout)
  if not all(item.get('success') is True for item in data):raise ValueError('query unsuccessful')
  rows.extend(row for item in data for row in item.get('results',[]))
 except (subprocess.SubprocessError,ValueError,OSError) as e:
  errors[name]=type(e).__name__  # Never print credentials or raw diagnostic output.
projects=['miaoti','miao-beat','miaotarot'];pairs=[]
for source in projects:
 for target in projects:
  if source==target:continue
  values={}
  for kind,owner in [('click',source),('arrival',target)]:
   db='miaotarot-data' if owner=='miaotarot' else 'miaoti-stats'
   values[kind]=None if db in errors else sum(row['count'] for row in rows if row['source_project']==source and row['target_project']==target and row['event_kind']==kind)
  pairs.append({'source':source,'target':target,**values})
print(json.dumps({'timezone':'Asia/Shanghai','days_including_today':a.days,'traffic':traffic,'status':'partial' if errors else 'complete','errors':errors,'directions':pairs,'daily_placement_rows':rows,'meaning':'Event counts, not unique people or matched conversion rates. Missing event requests/stripped tags may undercount. No history before rollout.'},ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
