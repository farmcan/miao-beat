#!/usr/bin/env python3
"""Package complete generated scenes without cropping or recomposing any limb."""
import hashlib,json,struct,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=root/'design/whole-cat-frames-2026-10-25'
plan=json.loads((source/'plan.json').read_text())['frames']
missing=[p['id'] for p in plan if not(source/'frames'/(p['id']+'.png')).is_file()]
assert not missing,'Whole-frame generation incomplete: '+','.join(missing)
out=root/'public/character/whole-piano-v3';out.mkdir(parents=True,exist_ok=True)
frames={};provenance=[]
for pose in plan:
 name=pose['id'];original=source/'frames'/(name+'.png');data=original.read_bytes()
 assert data[:8]==b'\x89PNG\r\n\x1a\n','Expected original PNG: '+name
 width,height=struct.unpack('>II',data[16:24]);assert width==height and width>=1254,'Unreviewed source dimensions: '+name
 target=out/(name+'.jpg')
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(original),'-vf','scale=1254:1254:flags=lanczos','-frames:v','1','-c:v','mjpeg','-q:v','2','-y',str(target)],check=True)
 encoded=target.read_bytes();assert len(encoded)<2000000
 frames[name]=target.name
 provenance.append({'id':name,'source':str(original.relative_to(root)),'sourceSha256':hashlib.sha256(data).hexdigest(),'file':target.name,'bytes':len(encoded),'sha256':hashlib.sha256(encoded).hexdigest(),'keys':[k['code'] for k in pose['keys']]})
manifest={'version':1,'date':'2026-10-25','width':1254,'height':1254,'frames':frames,'stills':{'guitar':{'src':'../guitar-whole-still-v1.jpg','label':'吉他完整静帧 · 动作待补'},'drums':{'src':'../drums-whole-still-v1.jpg','label':'架子鼓完整静帧 · 动作待补'}},'method':'One entire generated cat+both-paws+instrument image per state; no production limb layers or warping','provenance':provenance,'limits':['Discrete complete-pose changes, not a newly generated continuous video','Paw art can cover adjacent keys; not independent human fingers','Naturalness and physical-device acceptance remain separate']}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Packaged '+str(len(frames))+' complete-scene states; '+str(sum(p['bytes'] for p in provenance))+' total JPEG bytes')
