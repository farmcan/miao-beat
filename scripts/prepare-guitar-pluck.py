#!/usr/bin/env python3
"""Encode whole-scene raised-paw/strike pairs; interpolate only within one fret pose."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--rife',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--work',type=Path,default=root/'artifacts/guitar-pluck-2026-10-26/batch');a=p.parse_args()
work=a.work.resolve();inputs=work/'input';outputs=work/'output';inputs.mkdir(parents=True,exist_ok=True);outputs.mkdir(exist_ok=True)
plan=json.loads((root/'design/guitar-pluck-2026-10-26/generation.json').read_text());codes=[x['code'] for x in plan['frames']];assert len(codes)==17
out=root/'public/character/guitar-pluck-v1';out.mkdir(exist_ok=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return{'file':p.name,'bytes':p.stat().st_size,'sha256':digest(p)}
clips={}
for j,code in enumerate(codes):
 up=root/f'design/guitar-pluck-2026-10-26/up/{code}.png';down=root/f'public/character/instrument-scenes-v1/guitar/{code}.jpg'
 assert Image.open(up).size==(1254,1254)
 for k,source in enumerate([up,down]):Image.open(source).convert('RGB').resize((640,640),Image.Resampling.LANCZOS).save(inputs/f'{2*j+k:04d}.png')
 upfile=out/f'{code}-up.jpg';Image.open(up).convert('RGB').save(upfile,quality=95,subsampling=0)
 clips[code]={'up':{**entry(upfile),'source':str(up.relative_to(root)),'sourceSha256':digest(up)},'down':{**entry(down),'file':str(down.relative_to(root/'public'))}}
expected=len(codes)*16
if len(list(outputs.glob('*.png')))!=expected:
 with (work/'rife.log').open('w') as log:subprocess.run([str(a.rife.resolve()),'-i',str(inputs),'-o',str(outputs),'-n',str(expected),'-m',str(a.model.resolve()),'-g','0','-j','1:1:1','-f','%08d.png'],stdout=log,stderr=log,check=True,timeout=600)
assert len(list(outputs.glob('*.png')))==expected
for j,code in enumerate(codes):
 frames=[Image.open(outputs/f'{j*16+k+1:08d}.png').convert('RGB') for k in range(1,8)]
 poses=[Image.open(out/f'{code}-up.jpg').convert('RGB').resize((640,640),Image.Resampling.LANCZOS),*frames,Image.open(root/'public'/clips[code]['down']['file']).convert('RGB').resize((640,640),Image.Resampling.LANCZOS)]
 sheet=Image.new('RGB',(1920,1920))
 for k,im in enumerate(poses):sheet.paste(im,(k%3*640,k//3*640))
 path=out/f'{code}.webp';sheet.save(path,'WEBP',quality=86,method=6);clips[code]['atlas']=entry(path)
upstream=json.loads((root/'public/character/guitar-motion-v1/manifest.json').read_text())['upstream']
manifest={'version':1,'width':1254,'height':1254,'tileSize':640,'columns':3,'rows':3,'intermediates':7,'clips':clips,'method':'Each clip changes the raised strumming paw to contact while keeping the fretting hand fixed. Every frame is a complete cat, both connected paws and guitar picture.','upstream':upstream,'limits':['Cartoon pluck, not exact strings or fingering instruction','Large changes between frets select the new full scene directly; clips never tour other notes','Intermediate frames may be softer than 1254px endpoints; physical device and user naturalness remain unverified']}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for page in range(3):
 group=codes[page*6:(page+1)*6];board=Image.new('RGB',(960,340*len(group)),'#eee');d=ImageDraw.Draw(board)
 for row,code in enumerate(group):
  j=codes.index(code);images=[Image.open(out/f'{code}-up.jpg'),Image.open(outputs/f'{j*16+5:08d}.png'),Image.open(root/'public'/clips[code]['down']['file'])]
  for col,im in enumerate(images):board.paste(im.convert('RGB').resize((320,320)),(col*320,row*340+20));d.text((col*320+5,row*340+3),code+' '+['UP','MID','CONTACT'][col],fill='black')
 board.save(work/f'review-{page+1}.jpg',quality=93)
print('Packaged',len(clips),'complete-scene right-paw clips;',sum(v[k]['bytes'] for v in clips.values() for k in ['up','atlas']),'new public bytes')
