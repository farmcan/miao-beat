#!/usr/bin/env python3
"""Offline RIFE interpolation of whole scenes along a short, reviewed pose graph.

Requires Pillow and the official rife-ncnn-vulkan 20221029 executable/model.
The browser receives only complete-picture frame strips, never limb layers.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--rife', type=Path, required=True)
parser.add_argument('--model', type=Path, required=True)
parser.add_argument('--work', type=Path, default=ROOT/'artifacts/guitar-motion-2026-10-26/batch')
args = parser.parse_args()
work = args.work.resolve(); work.mkdir(parents=True, exist_ok=True)
inputs = work/'input'; outputs = work/'output'
inputs.mkdir(exist_ok=True); outputs.mkdir(exist_ok=True)
notes = ['KeyA','KeyW','KeyS','KeyE','KeyD','KeyF','KeyT','KeyG','KeyY','KeyH','KeyU','KeyJ','KeyK']
rest = ['idle','Digit1','Digit2','Digit3','Digit4']
pairs = [(a,b) for i,a in enumerate(rest) for b in rest[i+1:]]
pairs += list(zip(notes,notes[1:])) + [(a,'KeyA') for a in rest]
assert len(pairs) == 27

# An Euler walk visits both directions once. Directory mode processes the walk
# in one model session; only the first visit of each undirected edge is packed.
adj = {}
for a,b in pairs:
    adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
stack=['idle']; walk=[]
while stack:
    if adj[stack[-1]]: stack.append(adj[stack[-1]].pop())
    else: walk.append(stack.pop())
walk.reverse(); assert len(walk)==55
source = ROOT/'public/character/instrument-scenes-v1/guitar'
poses={}
for i,name in enumerate(walk):
    original=(source/(name+'.jpg')).read_bytes()
    poses[name]={'source':'character/instrument-scenes-v1/guitar/'+name+'.jpg','sha256':hashlib.sha256(original).hexdigest()}
    target=inputs/(f'{i:04d}.png')
    Image.open(source/(name+'.jpg')).convert('RGB').resize((640,640),Image.Resampling.LANCZOS).save(target)
expected=len(walk)*8
if len(list(outputs.glob('*.png'))) != expected:
    command=[str(args.rife.resolve()),'-i',str(inputs),'-o',str(outputs),'-n',str(expected),'-m',str(args.model.resolve()),'-g','0','-j','1:1:1','-f','%08d.png']
    with (work/'rife.log').open('w') as log:
        subprocess.run(command,stdout=log,stderr=log,check=True,timeout=600)
assert len(list(outputs.glob('*.png'))) == expected
public=ROOT/'public/character/guitar-motion-v1'; public.mkdir(parents=True,exist_ok=True)
first={}
for i,(a,b) in enumerate(zip(walk,walk[1:])):
    first.setdefault(frozenset((a,b)),(i,a,b))
edges=[]; review=[]
for number,(a,b) in enumerate(pairs):
    index,walk_a,walk_b=first[frozenset((a,b))]
    frames=[Image.open(outputs/f'{index*8+k+1:08d}.png').convert('RGB') for k in range(1,8)]
    if walk_a!=a: frames.reverse()
    assert all(im.size==(640,640) for im in frames)
    strip=Image.new('RGB',(2560,1280),'#f8f4eb')
    for k,im in enumerate(frames): strip.paste(im,(k%4*640,k//4*640))
    strip.paste(frames[-1],(1920,640))
    filename=f'e{number:02d}.webp'; target=public/filename
    strip.save(target,'WEBP',quality=84,method=6)
    encoded=target.read_bytes()
    edges.append({'id':f'e{number:02d}','from':a,'to':b,'file':filename,'bytes':len(encoded),'sha256':hashlib.sha256(encoded).hexdigest()})
    review.append((f'{a} > {b}',frames[3]))
manifest={'version':1,'date':'2026-10-26','width':640,'height':640,'columns':4,'rows':2,'intermediates':7,
          'poses':poses,'edges':edges,
          'method':'Offline RIFE-v4.6 complete-scene interpolation; every tile is an entire cat and guitar picture',
          'upstream':{'repository':'https://github.com/nihui/rife-ncnn-vulkan','commit':'a7532fc3f9f8f008cd6eecd6f2ffe2a9698e0cf7','release':'20221029','model':'rife-v4.6',
                      'binarySha256':hashlib.sha256(args.rife.read_bytes()).hexdigest(),
                      'modelSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.model.glob('*')) if p.is_file()}},
          'limits':['Large direct fret interpolation rejected after a paw disappeared. Runtime does not tour other notes: unsupported distant changes land on the target and use one short local recoil.',
                    'Interpolation is not a fingering correction or physically authored guitar performance',
                    'No independent body/arm composition; only whole-scene tiles selected at runtime']}
(public/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for page in range(3):
    board=Image.new('RGB',(1200,1260),'#eee'); draw=ImageDraw.Draw(board)
    for j,(title,im) in enumerate(review[page*9:(page+1)*9]):
        x,y=j%3*400,j//3*420; draw.text((x+8,y+3),title,fill='black');board.paste(im.resize((400,400)),(x,y+20))
    board.save(work/f'review-midpoints-{page+1}.jpg',quality=92)
(work/'walk.json').write_text(json.dumps({'walk':walk,'pairs':pairs},indent=2)+'\n')
print(f'Packaged {len(edges)} whole-scene transition strips, {sum(e["bytes"] for e in edges)} bytes')
