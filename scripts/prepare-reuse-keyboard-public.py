"""Copy an explicit licensed single-note experiment into public; never deploy."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'design/miao-reuse-keyboard-v1/browser-one-key'
ART=ROOT/'artifacts/miao-reuse-keyboard-v1'
MODEL=ART/'single-key-web-morph/miao-one-key.glb'
META=ART/'single-key-web-morph/metadata.json'
POSTER=ART/'v2-keygroup-lift-color/front.png'
OUT=ROOT/'public/labs/reuse-keyboard'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--web-gate',choices=['pending independent experimental-page review','experimental-page-go'],default='pending independent experimental-page review',help='Set GO only after actual independent webpage reviews.')
    options=parser.parse_args()
    assert sha(MODEL)=='5c20616b3f7f1cbbdff257fb10729519c84eaf940bfee467803ba29fc5e0b69a'
    original=json.loads(META.read_text())
    assert original['keyNode']=='MiaoKeyC4' and original['morphNames']=={'contact':'Contact','down':'Down'}
    model_name='miao-one-key-'+sha(MODEL)[:8]+'.glb'
    poster_name='poster-'+sha(POSTER)[:8]+'.png'
    fields=['version','keyNode','morphNames','q0','qContact','qDown','contactFraction','keyMaxRadians','pivotThree','trajectory']
    meta={key:original[key] for key in fields}
    meta.update(modelFile=model_name,modelSha256=sha(MODEL),modelBytes=MODEL.stat().st_size)
    meta['attribution']={'cat':'Cat Rig (CC-BY) Blender Foundation | studio.blender.org','catLicense':'https://creativecommons.org/licenses/by/4.0/','keyboardAndTable':'Innerscene, complete-file CC0','codeAndRuntime':'Project and Three.js MIT'}
    meta['scope']='Only A/C4 controlled experiment. Native static gates passed; source hidden key-mount boundary unknowns remain. Not the completed Miao redesign or an eight-key instrument.'
    meta_bytes=(json.dumps(meta,ensure_ascii=False,indent=2)+'\n').encode()
    meta_name='metadata-'+hashlib.sha256(meta_bytes).hexdigest()[:8]+'.json'
    (OUT/'model').mkdir(parents=True,exist_ok=True)
    # Refuse to silently accumulate stale/unreviewed model variants.
    existing={p.name for p in (OUT/'model').iterdir()}
    assert existing <= {model_name,meta_name},existing
    shutil.copyfile(MODEL,OUT/'model'/model_name)
    (OUT/'model'/meta_name).write_bytes(meta_bytes)
    shutil.copyfile(POSTER,OUT/poster_name)
    replacements={
      '../../../public/sampled-audio.js':'../../sampled-audio.js',
      '../../../public/bindings.js':'../../bindings.js',
      '../../../public/labs/character-compare/vendor/three-runtime.mjs':'../character-compare/vendor/three-runtime.mjs',
      '../../../artifacts/miao-reuse-keyboard-v1/single-key-web-morph/':'./model/',
      "'metadata.json'":repr(meta_name),
      '../../../artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift-color/front.png':'./'+poster_name,
      '../../../public/UPSTREAM-LICENSE.txt':'../../UPSTREAM-LICENSE.txt',
    }
    for name in ['index.html','style.css','play.js','motion.js','model.js']:
        text=(SOURCE/name).read_text()
        for before,after in replacements.items():text=text.replace(before,after)
        assert not any(term in text for term in ['/Users/','artifacts/','../../../public/','<style>'])
        (OUT/name).write_text(text)
    credits='''Miao Beat — licensed single-note model experiment

Cat Rig (CC-BY) Blender Foundation | studio.blender.org
Original: https://studio.blender.org/characters/cat/v1/
License: https://creativecommons.org/licenses/by/4.0/
Received optimized variant: https://github.com/move-ai/Move_API_and_retargeting_Blender_addon
Fixed upstream commit: f449af53ccc71a7c66079b7a52e133a163a41fb7
Modifications: original native IK/finger controls posed in Blender3.6.23;
evaluated whole-scene geometry exported, Contact/Down hand morphs derived from
the same complete connected source scene. Source base mesh retained. Unused
authoring Color layers omitted because source shaders did not read them.
No upstream Python is embedded in or executed by this browser model.

Key Forty MIDI Keyboard and COMMON280 table: Innerscene, complete-file CC0.
https://www.innerscene.com/tools/library/3d-parts/key-forty-midi-keyboard-0d9952a4
https://www.innerscene.com/tools/library/3d-parts/common-280-communal-work-table-0e45ba93
Adaptation: original key bank and wrist controls shifted 2mm for a fixed 1.5mm
key stroke. No new character or instrument geometry.

Three.js 0.186.1, MIT; vendor notice at ../character-compare/vendor/three-LICENSE.txt
Project scripts: MIT. Piano samples retain the main product's original credits
at ../../UPSTREAM-LICENSE.txt and ../../samples/LICENSES.txt.

Scope: single-note controlled prototype, not the completed Miao appearance or
an eight-key release. Original hidden black/white key-mount intersections retain
boundary classification unknowns; no complete mechanical-simulation claim.
'''
    (OUT/'credits.txt').write_text(credits)
    assets=[]
    for name in [model_name,meta_name]:
        p=OUT/'model'/name;assets.append({'file':'model/'+name,'bytes':p.stat().st_size,'sha256':sha(p)})
    assets.append({'file':poster_name,'bytes':POSTER.stat().st_size,'sha256':sha(POSTER)})
    review={'version':1,'scope':'standalone-A-C4-experiment','productionCharacterReplacement':False,'supportedKeys':['KeyA'],'supportedMidi':[60],'modelFile':'model/'+model_name,'metadataFile':'model/'+meta_name,'assets':assets,'sourceNativeSha256':'ca5f9095d31badc8c4e0266ba969ec127bf3e2f4a90b7f7e7c532d8bf4f5abb6','sourcePoseSha256':'6a034f30f3f848c4cd7833da9e86834d895a636bfed170d5cd5fbd16d7b5049b','nativeStaticGate':'gray and same-pose color: three independent roles GO for one-note test','nativeMotionGate':'one press/contact/key/release/return GO for controlled web trial','webGate':options.web_gate,'mobileSpeakerTested':False}
    (OUT/'review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
    tests=(SOURCE/'motion.test.mjs').read_text().replace("from './motion.js'","from '../public/labs/reuse-keyboard/motion.js'")
    (ROOT/'scripts/reuse-keyboard-motion.test.mjs').write_text('// Generated from the authoring motion contract by prepare-reuse-keyboard-public.py.\n'+tests)
    print(json.dumps({'prepared':str(OUT.relative_to(ROOT)),'model':model_name,'metadata':meta_name,'poster':poster_name,'deployed':False}))

if __name__=='__main__':main()
