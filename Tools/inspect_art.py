from pathlib import Path
import sys,numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R.parent/'rw-v075dev5/Tools'),str(R.parent/'rw-v075dev5/Source')]
from native_model import load,walk
for ID in ('RW_GND_END_250_125','RW_GND_PWR','RW_GND_ELB'):
 m=load(R/'GameData/RoosterWorksGroundModules/Models'/(ID+'.mu'))
 print(ID)
 for path,n in walk(m.root):
  if 'mesh' not in n:continue
  tex=m.textures[m.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name']
  if any(s in tex for s in ('label','crest')):
   v=np.array(n['mesh']['vertices']);u=np.array(n['mesh']['uvs']);print(path,tex,len(v),'bounds',v.min(0),v.max(0),'uv',u.min(0),u.max(0))
