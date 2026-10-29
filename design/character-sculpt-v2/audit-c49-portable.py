"""Read-only dependency/private-runtime audit of the partial C49 authoring file."""
from pathlib import Path
import json
import hashlib
import bpy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/character-local-merge-c49/miao-c49-local-merge.blend'
OUT = ROOT / 'artifacts/character-local-merge-c49/portable-audit.json'
before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
images = [{'name': im.name, 'source': im.source, 'packed': bool(im.packed_file),
           'external_unpacked': bool(im.filepath) and not bool(im.packed_file) and im.source in {'FILE', 'SEQUENCE', 'MOVIE'}}
          for im in bpy.data.images]
libraries = [lib.name for lib in bpy.data.libraries]
texts = [{'name': t.name, 'auto_module': t.use_module} for t in bpy.data.texts]
driver_count = sum(len(o.animation_data.drivers) for o in bpy.data.objects if o.animation_data)
result = {'native_sha256': before, 'source_unchanged': hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before,
          'images': images, 'linked_libraries': libraries, 'embedded_texts': texts, 'object_driver_count': driver_count,
          'scene_camera': bpy.context.scene.camera.name if bpy.context.scene.camera else None,
          'whole_character_approved': False, 'new_animation_created': False,
          'portable_authoring_open': not any(i['external_unpacked'] for i in images) and not libraries
                                    and not any(t['auto_module'] for t in texts) and not driver_count,
          'scope': 'Asset dependencies and embedded runtime only; not a character/art/rig pass.'}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result), flush=True)
assert result['portable_authoring_open'] and result['source_unchanged']
