"""Deterministic whitelist-only static review packaging; no Blender/render/network.

Original .blend/.glb/PNG/JPG bytes are retained. Portable text copies normalize
repository paths and omit credential-bearing temporary URLs. Every transform is
recorded with original/packaged SHA. Does not publish, commit or write public/.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import urllib.parse
import zipfile

ROOT=Path(__file__).resolve().parents[2]
PREVIOUS={item['path']:item for item in json.loads((ROOT/'PACKAGE_MANIFEST.json').read_text())['files']} if (ROOT/'PACKAGE_MANIFEST.json').is_file() else {}
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=ROOT/'artifacts/handoff')
parser.add_argument('--kind',choices=['keyboard','guitar','both','eight-key-prop'],default='keyboard')
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
sha=lambda data:hashlib.sha256(data).hexdigest()
SIGNED_KEYS={'token','signature','sig','expires','credential','access_token','auth','key-pair-id','policy'}
URL=re.compile(r'https?://[^\s<>"\x27]+')
SECRET=re.compile(r'(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{25,}|AKIA[0-9A-Z]{16}|Bearer [A-Za-z0-9_.-]{20,})')


def temporary_url(url):
    query=urllib.parse.parse_qs(urllib.parse.urlsplit(url.rstrip(').,;')).query)
    return any(key.lower() in SIGNED_KEYS or key.lower().startswith(('x-amz-','x-goog-')) for key in query)


def portable_text(data,destination):
    text=data.decode('utf-8')
    # Preserve working relative Markdown links when moving the repository tree.
    absolute_markdown=re.compile(r'\]\(<?'+re.escape(str(ROOT))+r'/([^)>]+)>?\)')
    text=absolute_markdown.sub(lambda match:']('+os.path.relpath(match.group(1),str(PurePosixPath(destination).parent)).replace(os.sep,'/')+')',text)
    text=text.replace(str(ROOT)+'/','')
    text=URL.sub(lambda match:'[temporary download URL omitted; see canonical author page]' if temporary_url(match.group()) else match.group(),text)
    assert str(ROOT) not in text,destination
    assert not SECRET.search(text),'Credential-like content in '+destination
    assert not any(temporary_url(match.group()) for match in URL.finditer(text)),destination
    return text.encode()


def locate(*names):
    for name in names:
        path=ROOT/name
        if path.is_file():
            return path
    raise FileNotFoundError(names)


def file_entry(payload,target,*sources):
    path=locate(*sources)
    data=path.read_bytes()
    transformed=portable_text(data,target) if path.suffix.lower() in ['.md','.txt','.json','.py','.tsv','.sha256'] else data
    assert not SECRET.search(transformed.decode('latin1')),'Credential pattern in '+target
    previous=PREVIOUS.get(target)
    if previous and previous['sha256']==sha(transformed):
        # Preserve the original provenance ledger when repacking an extracted
        # portable copy; path normalization must not create a new origin SHA.
        payload[target]={'data':transformed,'source':previous['source_repository_path'],'original_sha256':previous['source_original_sha256'],'text_transformed':previous['portable_text_transformed']}
    else:
        payload[target]={'data':transformed,'source':path.relative_to(ROOT).as_posix(),'original_sha256':sha(data),'text_transformed':data!=transformed}


def generated(payload,target,data):
    if isinstance(data,str):
        data=data.encode()
    payload[target]={'data':data,'source':None,'original_sha256':None,'text_transformed':False}


def pack(name,payload,metadata):
    assert all(not PurePosixPath(path).is_absolute() and '..' not in PurePosixPath(path).parts and '\\' not in path for path in payload)
    generated(payload,'PACKAGE.json',json.dumps(metadata,indent=2)+'\n')
    manifest={'format':'miao-static-review-pack-v1','package':name,'files':[{'path':path,'bytes':len(item['data']),'sha256':sha(item['data']),'source_repository_path':item['source'],'source_original_sha256':item['original_sha256'],'portable_text_transformed':item['text_transformed']} for path,item in sorted(payload.items())]}
    generated(payload,'PACKAGE_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    sums=''.join(sha(item['data'])+'  '+path+'\n' for path,item in sorted(payload.items()))
    generated(payload,'SHA256SUMS',sums)
    archive=args.output/(name+'.zip')
    top=name+'/'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as handle:
        for path,item in sorted(payload.items()):
            info=zipfile.ZipInfo(top+path,date_time=(2026,10,30,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            handle.writestr(info,item['data'])
    expected={top+path for path in payload}
    with zipfile.ZipFile(archive) as handle:
        assert handle.testzip() is None
        assert len(handle.namelist())==len(expected) and set(handle.namelist())==expected
        for path,item in payload.items():
            assert sha(handle.read(top+path))==sha(item['data'])
        for line in handle.read(top+'SHA256SUMS').decode().splitlines():
            digest,path=line.split('  ',1)
            assert sha(handle.read(top+path))==digest
    return {'archive':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'members':len(payload),'zip_crc_pass':True,'exact_member_whitelist_pass':True,'member_sha_pass':True,'deterministic_timestamp':'2026-10-30T00:00:00','source_files':[{'path':path,'source':item['source'],'original_sha256':item['original_sha256'],'packaged_sha256':sha(item['data']),'portable_text_transformed':item['text_transformed']} for path,item in sorted(payload.items())]}


def keyboard():
    payload={}
    base='artifacts/miao-reuse-keyboard-v1/'
    manifest=json.loads((ROOT/(base+'default-color/inspection-manifest.json')).read_text())
    assert manifest['native_sha256']=='3def58d233e39d1a97c67bc6b46edf7b0c882ba86e1b9584f23af42945f6e38b'
    # Check immutable native and all eight PNG bytes against the reviewed snapshot.
    for item in manifest['files']:
        relative=item['path'].replace(str(ROOT)+'/','')
        if '/artifacts/' in relative and not relative.startswith('artifacts/'):
            relative='artifacts/'+relative.split('/artifacts/',1)[1]
        if Path(relative).suffix.lower() not in ['.png','.blend']:
            continue
        assert sha((ROOT/relative).read_bytes())==item['sha256'],relative
    for name in ['front.png','three-quarter.png','face.png','left-hand.png','right-hand.png','hands-top.png','feet-support.png','support-side.png','keyboard-default-color-native36.blend','inspection-manifest.json','default-color-receipt.json','native-reopen-verification.json']:
        relative=base+'default-color/'+name
        file_entry(payload,relative,relative)
    for name in ['CAT-CCBY-ATTRIBUTION.md','MODIFICATIONS.md','PROJECT-CODE-MIT.txt','TABLE-SOURCE.json','TABLE-CC0-EVIDENCE.json','KEYFORTY-SOURCE.json','KEYFORTY-CC0-EVIDENCE.txt']:
        relative=base+'licenses/'+name
        file_entry(payload,relative,relative)
    for name in ['supported-receipt.json','native-reopen-verification.json','inspection-manifest.json']:
        relative=base+'gray-supported/'+name
        file_entry(payload,relative,relative)
    for name in ['render2-matched-proxy-fit.json','render-geometry-equivalence-audit.json','table-import-receipt.json']:
        relative=base+'support-prop/'+name
        file_entry(payload,relative,relative)
    reports=[f'miao-keyboard-{stage}-{role}-judge-2026-10-30.md' for stage in ['gray','color'] for role in ['identity','craft','motion']]
    reports+=['miao-keyboard-default-color-static-2026-10-30.md','miao-keyboard-gray-support-repair-2026-10-30.md','miao-reuse-keyboard-prop-and-fit-2026-10-30.md']
    for name in reports:
        file_entry(payload,'docs/research/'+name,'docs/research/'+name)
    for name in ['review_native.py','verify_review_pack.py','package_review_pack.py']:
        relative='design/miao-reuse-keyboard-v1/'+name
        file_entry(payload,relative,relative)
    file_entry(payload,'docs/character-keyboard-review-handoff.md','docs/character-keyboard-review-handoff.md')
    file_entry(payload,'README.md','docs/character-keyboard-review-handoff.md')
    for relative in ['public/character/whole-piano-v3/idle.jpg','artifacts/miao-reuse-v1/source-rest-baseline/source-rest-original-three-quarter.png','artifacts/upstream-cat-candidates/scout-a/wingit_cat.blend','artifacts/upstream-cat-candidates/scout-a/source-provenance.json','artifacts/upstream-cat-candidates/scout-a/ReadMe.txt.txt','artifacts/upstream-cat-candidates/scout-a/move-ai-README.md','artifacts/licensed-keyboard-alternative-2026-10-30/innerscene-key-forty/piano-midi-keyboard.glb','artifacts/licensed-keyboard-alternative-2026-10-30/innerscene-key-forty/SOURCE.json','artifacts/licensed-keyboard-alternative-2026-10-30/innerscene-key-forty/LICENSE-EVIDENCE.txt','artifacts/licensed-keyboard-alternative-2026-10-30/innerscene-key-forty/readonly-audit.json','artifacts/licensed-keyboard-support-2026-10-30/communal-work-table.glb','artifacts/licensed-keyboard-support-2026-10-30/source-receipt.json','artifacts/handoff/keyboard-static-native-audit/native-audit.json','LICENSE']:
        file_entry(payload,relative,relative)
    for target,choices in {
        'licenses/GPL-3.0.txt':['artifacts/miao-reuse-v1/compat/BLENDER-GPL-3.0.txt','licenses/GPL-3.0.txt'],
        'licenses/CC0-1.0-legalcode.html':['artifacts/upstream-guitar-candidates/blenderkit-classic/CC0-1.0-legalcode.html','licenses/CC0-1.0-legalcode.html'],
        'runtime/blender-3.6.23.sha256':['artifacts/runtime/blender-3.6.23.sha256','runtime/blender-3.6.23.sha256'],
        'runtime/blender-3.6.23-runtime-receipt.json':['artifacts/runtime/blender-3.6.23-runtime-receipt.json','runtime/blender-3.6.23-runtime-receipt.json'],
    }.items():
        file_entry(payload,target,*choices)
    for name in ['cloudrig.py','lighting_rig_setup.py','cat_post_gen.py','update_uv_deform_mesh.py','ReadMe.txt']:
        file_entry(payload,'source/cat-embedded-texts/'+name,'artifacts/miao-reuse-v1/compat/upstream-texts/'+name,'source/cat-embedded-texts/'+name)
    generated(payload,'licenses/EMBEDDED-CODE-AND-ASSET-NOTICE.md','''# Separate model and code rights
Cat Rig (CC-BY) Blender Foundation | studio.blender.org
Model/texture/rig asset: CC BY4.0 https://creativecommons.org/licenses/by/4.0/ .
CloudRig code has separate GPL3 terms; full text and embedded corresponding Python source are preserved. Legacy embedded files have no added/replaced per-file header. They remain unchanged as received; no upstream Python executes in this workflow.
Official CloudRig: https://extensions.blender.org/add-ons/cloudrig/ . MoveAI redistribution commit f449af53ccc71a7c66079b7a52e133a163a41fb7 separately licenses addon GPL3 and Blender Studio assets CC BY4.0. No MoveAI addon is installed or needed.
Project reference piano JPG is an owner-approved project reference, not a CC0 stock-asset claim. Project scripts are MIT; asset rights above remain separate.
''')
    assert len(payload['licenses/GPL-3.0.txt']['data'])>35000
    for path,digest in [('artifacts/upstream-cat-candidates/scout-a/wingit_cat.blend','42d5c51c758e7f5427622375381058afa8dc398bec637f4822f5636b6b9a41e1'),('artifacts/licensed-keyboard-alternative-2026-10-30/innerscene-key-forty/piano-midi-keyboard.glb','346f1f4ae12154dd7757e599abc0d3c285dc7aa61648e73c9c8bbc6c9e289a62'),('artifacts/licensed-keyboard-support-2026-10-30/communal-work-table.glb','27ba0fdfd0afde9fec6ccc6306bc0e0b2e3f6eb32d2820fa609f70c1301bceca')]:
        assert sha(payload[path]['data'])==digest
    assert not any(any(word in path.lower() for word in ['smile','guitar-fit','web-roundtrip','test_static_web','child-electric']) for path in payload)
    return pack('miao-keyboard-static-review-2026-10-30',payload,{'status':'THREE_ROLE_GRAY_AND_COLOR_STATIC_GO_ONLY','native_sha256':manifest['native_sha256'],'pose_sha256':manifest['pose_sha256'],'single_key_operation':'separate work; not included or accepted by this pack','performance_or_browser_acceptance':False,'frozen_native_format':'Blender3.6.23','runtime_included':False,'self_contained_models_images':True,'three_gray_and_three_color_reports':['docs/research/'+name for name in reports[:6]]})


def guitar():
    payload={}
    base='artifacts/miao-reuse-v1/thin-electric-clean/'
    for name in ['thin-electric-clean.blend','thin-electric-clean.glb','full.png','side.png','bridge.png','LICENSE-AND-DERIVATION.md','PROJECT-MIT-LICENSE.txt','UPSTREAM-GEOMETRY-CC0-1.0.html','verify-native-5.2.3.json','verify-glb-5.2.3.json','verify-glb-3.6.23.json','glb-structure.json']:
        file_entry(payload,base+name,base+name)
    file_entry(payload,'design/miao-reuse-keyboard-v1/verify_review_pack.py','design/miao-reuse-keyboard-v1/verify_review_pack.py')
    file_entry(payload,'docs/research/thin-guitar-clean-independent-craft-judge-2026-10-30.md','docs/research/thin-guitar-clean-independent-craft-judge-2026-10-30.md')
    metadata={'author':'Rexodus','title':'HH Guitar with stand','canonical_author_page':'https://www.blendkit.com/asset-gallery-detail/e641b80c-75ec-4888-b900-d63ef76057fe/','asset_base_id':'e641b80c-75ec-4888-b900-d63ef76057fe','asset_version_id':'73aaeeda-0e93-41de-8145-dccb68ee919f','geometry_license':'CC0 per upstream model metadata; not a relicensing of original materials','raw_original_excluded_sha256':'6a3cb4ad3124240e6d812c52b8ce25bb105e79de9a3ba1648544251f9f61a0ef','clean_native_sha256':'185a1a07704b2e778a53293a7cbd70e4598b77f12b223a3dea78b1b2a4d73ea9','clean_glb_sha256':'1e61a29480aecff87ea53ff65338bed7d20d7a24704707b5d2c68b526bc26938','old_materials_images_texts_shader_groups':'stripped; none redistributed','new_pbr':'six project Miao_* constant Principled materials; MIT recipes','mesh_objects':143,'triangles':2192095,'native_format':'5.2.3 original clean derivative; not rewritten','blender36':'verified GLB import only','distribution_role':'OFFLINE AUTHORING ONLY; no cat hold/contact/browser approval'}
    generated(payload,base+'CLEAN-SOURCE.json',json.dumps(metadata,indent=2)+'\n')
    generated(payload,'README.md','''# Clean mature thin-electric prop addon
Only the clean CC0 upstream geometry derivative and six new project PBR materials, clean preview renders, license/source and verification receipts are included. The original HH .blend, author preview and royalty_free materials/images are expressly excluded.
Native is the existing Blender5.2.3 derivative. Blender3.6 must import the standard GLB; do not open the5.2 native there. No file was rewritten by this packaging task.
143 meshes /2,192,095 triangles are offline authoring only, not default browser loading. Prop craft GO does not accept any cat hold, contact or motion. No failed WingIt/guitar integration is included.
Validate after extraction: python3 design/miao-reuse-keyboard-v1/verify_review_pack.py . See PACKAGE_MANIFEST.json and SHA256SUMS.
''')
    native=payload[base+'thin-electric-clean.blend']['data']
    glb=payload[base+'thin-electric-clean.glb']['data']
    assert sha(native)==metadata['clean_native_sha256'] and sha(glb)==metadata['clean_glb_sha256']
    assert not any('original.blend' in path or 'author-preview' in path or 'material-license-tags' in path for path in payload)
    return pack('miao-thin-electric-clean-prop-2026-10-30',payload,{'status':'CLEAN_PROP_CRAFT_GO_OFFLINE_ONLY','raw_materials_or_original_hh_included':False,'model_assets':'CC0 geometry + project PBR','no_cat_assembly':True,'native_format':'Blender5.2.3; use GLB for3.6'})


def eight_key_prop():
    payload={}
    base='artifacts/miao-eight-key-prop-probe-2026-10-30/prop-export/'
    for name in ['eight-key-cc0-prop.glb','eight-key-cc0-prop-native36.blend','note-map.json','prop-reimport-three-quarter.png','reimport-verification.json','minimal-native-verification.json']:
        file_entry(payload,'model/'+name,base+name)
    file_entry(payload,'README.md','docs/character-eight-key-prop-handoff.md')
    file_entry(payload,'model/README.md',base+'README.md')
    for name in ['KEYFORTY-SOURCE.json','KEYFORTY-CC0-EVIDENCE.txt']:
        file_entry(payload,'licenses/'+name,'artifacts/miao-reuse-keyboard-v1/licenses/'+name)
    file_entry(payload,'licenses/CC0-1.0-legalcode.html','artifacts/upstream-guitar-candidates/blenderkit-classic/CC0-1.0-legalcode.html')
    file_entry(payload,'licenses/PROJECT-MIT.txt','LICENSE')
    reports=[f'miao-eight-key-{stage}-{role}-judge-2026-10-30.md' for stage in ['gray','color'] for role in ['identity','craft','motion']]
    reports+=['miao-eight-key-prop-transport-craft-2026-10-30.md']
    for name in reports:file_entry(payload,'docs/research/'+name,'docs/research/'+name)
    file_entry(payload,'design/miao-reuse-keyboard-v1/verify_review_pack.py','design/miao-reuse-keyboard-v1/verify_review_pack.py')
    assert sha(payload['model/eight-key-cc0-prop.glb']['data'])=='d4f3ea60171f8275f02b59d9c3c8754234287f058b09cfd2fb047c6eaf6ceae6'
    assert sha(payload['model/eight-key-cc0-prop-native36.blend']['data'])=='a37df130055401bcadfb2e7096763bfd5685143235873aeb1c92e77fd44bf150'
    assert not any(path.endswith('.log') or 'cat.blend' in path for path in payload)
    return pack('miao-eight-key-cc0-instrument-2026-10-30',payload,{
        'status':'STATIC_INSTRUMENT_AUTHORING_COMPONENT_GO_ONLY',
        'model_and_maps_license':'CC0, derived from Innerscene Key Forty complete-file CC0',
        'cat_table_rig_actions_embedded_scripts_included':False,
        'complete_character_approved':False,'motion_or_mechanical_safety_approved':False,
        'production_replacement':False,'native_format':'Blender3.6.23 data-only asset library; Append the scene or import GLB',
        'mesh_count':18,'triangles':5560,'all_four_images_embedded':True,
        'glb_sha256':'d4f3ea60171f8275f02b59d9c3c8754234287f058b09cfd2fb047c6eaf6ceae6',
        'native_sha256':'a37df130055401bcadfb2e7096763bfd5685143235873aeb1c92e77fd44bf150',
        'world_fit_coordinates_retained':True,
        'scope':'Only the static instrument is handed off. Full Miao identity/craft remains HOLD. No new playing animation is authorized by this package.',
        'review_evidence':'Seven independent reports included; their full cat-scene images remain repository research evidence, not CC0 model contents.',
    })


archives=[]
if args.kind=='eight-key-prop':
    archives.append(eight_key_prop())
if args.kind in ['keyboard','both']:
    archives.append(keyboard())
if args.kind in ['guitar','both']:
    archives.append(guitar())
receipt={'status':'LOCAL_PREPARED_NOT_PUBLISHED','publish':False,'commit':False,'public_writes':False,'new_renders':0,'archives':archives}
(args.output/'review-pack-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'archives':[{k:item[k] for k in ['archive','bytes','sha256','members']} for item in archives]}))
