from pathlib import Path
import sys,numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R.parent/'rw-v075dev5/Tools'),str(R.parent/'rw-v075dev5/Source')]
from native_model import load,walk
from build_ring_options import components
m=load(R/'GameData/RoosterWorksGroundModules/Models/RW_GND_PWR.mu')
for path,n in walk(m.root):
 if 'mesh' not in n:continue
 tex=m.textures[m.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name']
 if tex not in ('rwm_crest','rwm_pwrlabel','rwm_bronze','rwm_graphite','rwm_steel'):continue
 v=np.array(n['mesh']['vertices']);tri=n['mesh']['submeshes'][0]
 for group in components(n['mesh']):
  indices=sorted({i for t in group for i in tri[t]});p=v[indices];center=(p.min(0)+p.max(0))/2
  if (tex=='rwm_crest' and len(indices)>=4) or (abs(center[0])<.6 and abs(center[1])<.25 and center[2]<-1.19):print(tex,len(indices),'center',center,'bounds',p.min(0),p.max(0))
