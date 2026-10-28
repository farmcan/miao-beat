"""Pack verified, complete Blender renders for the independent guitar test.
Usage: python scripts/prepare-blender-guitar.py --frames artifacts/.../frames
Requires Pillow. No models are downloaded and no Blender scripts are executed.
"""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frames',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('public/labs/blender-guitar'));a=p.parse_args()
root=Path(__file__).resolve().parents[1];src=a.frames.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
images=[];sources=[]
for n in range(24):
 path=src/f'frame-{n:03d}.png';raw=path.read_bytes();im=Image.open(path).convert('RGB');assert im.size==(640,640),(path,im.size)
 images.append(im);sources.append({'frame':n,'file':path.name,'sha256':hashlib.sha256(raw).hexdigest()})
seam=ImageChops.difference(images[0],images[-1]);seam_max=max(hi for lo,hi in seam.getextrema());seam_mae=max(ImageStat.Stat(seam).mean)
# Fixed-pose GPU path tracing can quantize a few channels one level apart.
assert seam_max<=1 and seam_mae<.001,'Ready pose changed; do not hide a seam in the runtime'
atlas=Image.new('RGB',(3840,2560))
for n,im in enumerate(images):atlas.paste(im,((n%6)*640,(n//6)*640))
file=out/'atlas.webp';atlas.save(file,'WEBP',quality=90,method=6);data=file.read_bytes();assert len(data)<3_000_000,'Atlas exceeds the bounded first-test budget'
images[0].save(out/'poster.webp','WEBP',quality=92,method=6)
manifest={'version':1,'width':640,'height':640,'columns':6,'rows':4,'frames':24,'contactFrame':2,'fps':60,'atlas':'atlas.webp','completeScene':True,'generator':'Blender 5.2.3 LTS','sourceScriptSha256':hashlib.sha256((root/'design/blender-guitar-v1/scene.py').read_bytes()).hexdigest(),'atlasSha256':hashlib.sha256(data).hexdigest(),'atlasBytes':len(data),'seamMaxChannelDifference':seam_max,'seamMaxChannelMean':seam_mae,'modelLicense':'Original Miao Beat scene; no external models or textures','scope':'One complete-scene right-paw strum study. Fixed left paw; no per-note fingering. Fast inputs may merge visible strokes.','sourceFrames':sources}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'frames':24,'atlasBytes':len(data),'size':atlas.size,'seamMaxChannelDifference':seam_max,'seamMaxChannelMean':seam_mae,'output':str(out)}))
