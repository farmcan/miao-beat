import bpy,numpy as np,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/character-palm-sculpt-c58'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'artifacts/character-body-voxel-c52/miao-c52-whole-body-voxel-authoring-study.blend'))
o=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=o.data
p=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',p);p=p.reshape(-1,3)
C=np.array([-.58,-1.19,1.80]);D=np.array([.78,0,-.625]);D/=np.linalg.norm(D);T=np.array([.625,0,.78]);T/=np.linalg.norm(T);s=(p-C)@D;t=(p-C)@T
region=(p[:,0]<-.15)&(p[:,0]>-1.1)&(p[:,1]<-.88)&(p[:,2]>1.4)&(p[:,2]<2.15)
sections=[]
for v in np.arange(-.3,.351,.025):
 m=region&(abs(s-v)<.008)
 if m.any():sections.append({'s':float(v),'n':int(m.sum()),'xyz_min':p[m].min(0).tolist(),'xyz_max':p[m].max(0).tolist(),'t_quantiles':np.percentile(t[m],[0,5,25,50,75,95,100]).tolist(),'y_quantiles':np.percentile(p[m,1],[0,5,25,50,75,95,100]).tolist()})
r={'version':bpy.app.version_string,'body_matrix':list(map(list,o.matrix_world)),'sections':sections,'objects':[x.name for x in bpy.data.objects if x.type in {'MESH','CURVE','CURVES'}]};(OUT/'palm-sections.json').write_text(json.dumps(r,indent=2))
np.savez_compressed(OUT/'source-palm-readback.npz',co=p,region=region,s=s,t=t)
print(json.dumps(r),flush=True)
