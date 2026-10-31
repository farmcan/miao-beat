#!/usr/bin/env python3
"""Summarize locally captured browser diagnostics; never infer speaker latency."""
import argparse,json,math
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('files',nargs='+',type=Path);a=p.parse_args();reports=[]
for file in a.files:
 d=json.loads(file.read_text());samples=d.get('samples',[]);values=sorted(float(x['delayMs']) for x in samples if isinstance(x.get('delayMs'),(int,float)) and math.isfinite(x['delayMs']) and x['delayMs']>=0)
 def percentile(q):return values[max(0,math.ceil(q*len(values))-1)] if values else None
 reports.append({'file':file.name,'condition':d.get('condition'),'metric':d.get('metric','legacy last contact redraw; not directly comparable to first-contact metric'),'observations':len(samples),'valid_delay_samples':len(values),'p50_ms':percentile(.5),'p95_ms':percentile(.95),'max_ms':max(values) if values else None,'serials':[x.get('strike') for x in samples]})
print(json.dumps({'scope':'Accepted audio call → canvas draw invocation only. Not physical input/speaker/compositor latency. Different metrics, cache states and small samples cannot establish improvement. Chord samples observe the latest accepted strike, not each finger.','reports':reports},ensure_ascii=False,indent=2))
