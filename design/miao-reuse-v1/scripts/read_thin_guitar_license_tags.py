import bpy,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];bpy.ops.wm.open_mainfile(filepath=str(Path(args[0]).resolve()),load_ui=False,use_scripts=False);r=[]
for m in bpy.data.materials:
 a=m.get('asset_data');b=m.get('blenderkit');item={'material':m.name}
 for key,x in [('asset_data',a),('blenderkit',b)]:
  if x is None:continue
  y={}
  for k in ['id','assetBaseId','asset_base_id','name','license','source','author_id','authorId']:
   if k in x:
    v=x[k];y[k]=v if isinstance(v,(str,int,float,bool)) else str(v)
  item[key]=y
 r.append(item)
Path(args[1]).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
