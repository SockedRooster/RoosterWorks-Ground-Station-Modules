from pathlib import Path
import sys,numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5';sys.path[:0]=[str(CORE/'Tools')]
from native_model import load,walk
from poses import rotation
for ID,foldername in (('RW_GND_FLEX','Flex'),('RW_GND_END_250_125','Endcap')):
 model=load(R/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu');folder=R/'Source'/foldername;folder.mkdir(exist_ok=True);lines=['mtllib '+ID+'.mtl'];mtl=[];offset=1
 def recurse(n,parent):
  t=np.eye(4);t[:3,:3]=rotation(n['rotation'])@np.diag(n['scale']);t[:3,3]=n['position'];t=parent@t
  if 'mesh' in n:yield n,t
  for c in n['children']:yield from recurse(c,t)
 for n,t in recurse(model.root,np.eye(4)):
  mesh=n['mesh'];mat=model.materials[n['materials'][0]];lines += ['o '+n['name'],'usemtl '+mat['name']]
  v=np.array(mesh['vertices'])@t[:3,:3].T+t[:3,3];norm=np.array(mesh['normals'])@np.linalg.inv(t[:3,:3]);norm/=np.linalg.norm(norm,axis=1)[:,None]
  lines+=['v %.8f %.8f %.8f'%(x,-z,y) for x,y,z in v];lines+=['vt %.8f %.8f'%uv for uv in mesh['uvs']];lines+=['vn %.8f %.8f %.8f'%(x,-z,y) for x,y,z in norm]
  lines+=['f '+' '.join(f'{i+offset}/{i+offset}/{i+offset}' for i in tri) for tri in mesh['submeshes'][0]];offset+=len(v)
 for mat in model.materials:
  tex=model.textures[mat['properties']['_MainTex']['index']]['name'];mtl+=['newmtl '+mat['name'],'Kd 1 1 1','map_Kd ../../GameData/RoosterWorksGroundModules/Models/'+tex+'.png','']
 (folder/(ID+'.obj')).write_text('\n'.join(lines)+'\n');(folder/(ID+'.mtl')).write_text('\n'.join(mtl)+'\n');print('Exported exact current native OBJ/MTL:',ID)
