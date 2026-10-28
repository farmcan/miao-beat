"""Compare the two actual D0.1 PNGs using Pillow and stdlib, no new dependencies."""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image, ImageChops, ImageStat
p=argparse.ArgumentParser();p.add_argument('--directory',default='artifacts/character-sculpt-d0');a=p.parse_args();out=Path(a.directory)
a=Image.open(out/'baseline-position.png').convert('RGBA');b=Image.open(out/'named-rest-position.png').convert('RGBA')
assert a.size==b.size==(512,512)
def stats(rect):
 aa,bb=a.crop(rect),b.crop(rect);d=ImageChops.difference(aa,bb);rgb=d.convert('RGB');channels=rgb.split();mx=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2]);h=mx.histogram();count=aa.width*aa.height
 def quantile(q):
  target=count*q;running=0
  for i,n in enumerate(h):
   running+=n
   if running>=target:return i
 return {'rect_xyxy':rect,'pixels':count,'mean_abs_RGBA_8bit':sum(ImageStat.Stat(d).mean)/4,'mean_abs_RGB_8bit':sum(ImageStat.Stat(rgb).mean)/3,'max_abs_RGB_8bit':max(i for i,n in enumerate(h) if n),'pixel_max_q95':quantile(.95),'pixel_max_q99':quantile(.99),'pixels_any_RGB_difference':count-h[0],'pixels_RGB_diff_gt3':sum(h[4:]),'pixels_RGB_diff_gt12':sum(h[13:]),'max_abs_alpha_8bit':d.getchannel('A').getextrema()[1]}
rois={'full':[0,0,512,512],'face_and_lids':[175,75,300,160],'picking_arm_and_wrist':[55,200,205,335],'picking_arm_stripes':[65,210,180,275],'holding_paw':[350,205,420,300],'cream_belly_and_short_fur':[220,355,335,405]}
receipt={'comparison':'same frozen evaluated scene, Geometry.Position vs named rest, fixed seed17/512px/32samples','metrics_8bit_range':[0,255],'regions':{n:stats(r) for n,r in rois.items()},'image_sha256':{n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['baseline-position.png','named-rest-position.png']},'limits':['This pair does not independently measure repeat-render noise.','Small beauty differences alone do not independently prove native-hair shader attribute lookup.','No deformation, anti-swim motion, root binding, contact, browser or export was tested.']}
(out/'pixel-difference.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
