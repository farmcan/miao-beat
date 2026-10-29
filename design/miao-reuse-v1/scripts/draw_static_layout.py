"""Draw an engineering layout from measured boxes; not an art/pose render."""
from pathlib import Path
import json,html
base=Path('artifacts/miao-reuse-v1/instrument');d=json.loads((base/'static-layout-proposal.json').read_text());parts=[]
def txt(x,y,t,size=14,color='#23364b'):parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-family="Arial,sans-serif">{html.escape(t)}</text>')
def panel(ox,oy,axis):
 scale=480;h0,h1=(-.57,.57) if axis==0 else(-.4,.25)
 def point(p):return ox+(p[axis]-h0)*scale,oy+(1.0-p[2])*scale
 for k in ['GEO-head','GEO-body','GEO-shoes','GEO-arms']:
  b=d['cat_objects_bbox'][k];x0,y0=point([b['min'][0],b['min'][1],b['max'][2]]);x1,y1=point([b['max'][0],b['max'][1],b['min'][2]])
  parts.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#dee5eb" fill-opacity=".45" stroke="#8293a4" stroke-width="1"/>')
  if axis==0:txt(x0+4,y0+15,k.replace('GEO-',''),11,'#6c7c8d')
 b=d['proposed_bbox'];x0,y0=point([b['min'][0],b['min'][1],b['max'][2]]);x1,y1=point([b['max'][0],b['max'][1],b['min'][2]])
 parts.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#17a1a0" fill-opacity=".15" stroke="#078882" stroke-width="2"/>')
 b=d['proposed_body_bbox'];x0,y0=point([b['min'][0],b['min'][1],b['max'][2]]);x1,y1=point([b['max'][0],b['max'][1],b['min'][2]])
 parts.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="#078882" stroke-width="1" stroke-dasharray="4 3"/>')
 for side,col in [('L','#8e45c0'),('R','#d66b11')]:
  c=d['contacts'][side];a=point(c['shoulder_world']);b=point(c['suggested_wrist_world']);p=point(c['target_world'])
  parts.append(f'<polyline points="{a[0]},{a[1]} {b[0]},{b[1]} {p[0]},{p[1]}" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="5 3"/>')
  for q,r in [(a,4),(b,4),(p,6)]:parts.append(f'<circle cx="{q[0]}" cy="{q[1]}" r="{r}" fill="{col}"/>')
  txt(p[0]+8,p[1]-9,side+' target',12,col)
 for z in [0,.2,.4,.6,.8,1.0]:
  y=oy+(1-z)*scale;parts.append(f'<line x1="{ox}" y1="{y}" x2="{ox+(h1-h0)*scale}" y2="{y}" stroke="#e5eaf0" stroke-width="1"/>');txt(ox-28,y+4,f'{z:.1f}',10)
 txt(ox,oy+scale+27,'X (m)' if axis==0 else 'Y (m); front is negative',12)
parts.append('<rect width="1100" height="770" fill="#fff"/>');txt(30,30,'Static guitar placement proposal / measured boxes, unchanged cat rest pose',21);txt(30,55,'Engineering diagram only. Dashed reach lines are targets, not posed arms or verified contact.',13,'#6c7c8d')
panel(48,87,0);panel(727,87,1);txt(60,82,'FRONT  X / Z',14);txt(730,82,'SIDE  Y / Z',14)
rows=['Guitar transform: uniform s = 0.50, Euler Y = 65 deg, location = (-0.235, -0.241, 0.235) m','Actual guitar bbox: [-0.24939, -0.27582, 0.16617] to [0.27001, -0.20618, 0.48393] m','L neck target: (0.08221, -0.27498, 0.38292); R hover: (-0.09905, -0.27729, 0.29839) m','Shoulder-to-wrist proposal: L 0.2013 m / R 0.2191 m; original upper+forearm length 0.2448 m','Reach necessary check only. Head overlap, wrist roll, finger curl and actual contact require the builder rendered pose.','Cat Rig (CC-BY) Blender Foundation | studio.blender.org | CC BY 4.0; diagram is a measured layout adaptation.','Classic Guitar by Rohma Ansari / Blendkit, CC0. No model or pose edits made by this diagram script.']
for i,r in enumerate(rows):txt(30,640+i*18,r,12)
(base/'static-layout-proposal.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="790" viewBox="0 0 1100 790">'+''.join(parts)+'</svg>')
