from pathlib import Path
import sys,json,numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'rw-v075dev5/Tools'))
from native_model import load,walk
from poses import world_nodes
for role in ('HAB','CMD','AIR','HUB','GRN','ELB','TUB','LOG','PWR','LAB'):
 model=load(R/f'GameData/RoosterWorksGroundModules/Models/RW_GND_{role}.mu')
 print('\n',role)
 for path,n in walk(model.root):
  if n['name'].startswith(('RW_GroundStairs','Airlock','airlock')) or n.get('tag')=='Airlock':print(path,n.get('position'),n.get('collider'))
 for n,m in world_nodes(model):
  if 'mesh' in n and any(s in n['name'].lower() for s in ('door','roof','rail','socket')):
   v=np.array(n['mesh']['vertices'])@m[:3,:3].T+m[:3,3]
   print(n['name'],v.min(0).round(3).tolist(),v.max(0).round(3).tolist())
 print('materials',[(i,x['name'],model.textures[x['properties']['_MainTex']['index']]['name']) for i,x in enumerate(model.materials)])
 if role=='AIR':
  stair=next(n for _,n in walk(model.root) if n['name']=='RW_GroundStairs')
  print('STAIR NODES',[(path,n.get('collider')) for path,n in walk(stair) if 'collider' in n])
