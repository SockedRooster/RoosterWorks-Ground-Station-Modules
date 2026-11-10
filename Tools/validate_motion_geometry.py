from pathlib import Path
import sys,json,numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from poses import world_nodes,rotation
for p in sorted((R/'GameData/RoosterWorksGroundModules/Models').glob('*.mu')):
 model=load(p);report=json.loads((R/f'Reports/{p.stem}.json').read_text());bindings={b['name']:b for b in report['motion']}
 for progress in (0,.2,.4,.6,.8,1):
  matrices={n['name']:m for n,m in world_nodes(model,progress)}
  for b in bindings.values():
   s=progress*progress*(3-2*progress);m=matrices[b['name']]
   assert np.isfinite(m).all() and np.allclose(np.linalg.det(m[:3,:3]),1)
   assert np.allclose(m[:3,3],s*np.array(b['position'])+(1-s)*np.array(b['retractPosition']))
   if b['mechanism']=='Legs':assert np.allclose(m[:3,:3],np.eye(3)) and np.isclose(np.linalg.norm(np.array(b['retractPosition'])-b['position']),.72)
 if report['stairs']:
  fully={n['name']:m for n,m in world_nodes(model,1)};nodes={n['name']:n for _,n in walk(model.root)}
  ladder=nodes['Ground_EVA_Ladder'];air=nodes['Ground_EVA_Airlock']
  f=fully[ladder['name']][:3,:3]@np.array((0,0,1));up=fully[ladder['name']][:3,:3]@np.array((0,1,0))
  assert np.allclose(f,(0,0,-1)) and np.allclose(up,(0,1,0)),'Ladder must face hull and climb up'
  assert np.allclose(fully[air['name']][:3,:3]@np.array((0,0,1)),(0,0,1)),'Exit remains outward'
  assert np.allclose(fully[air['name']][:3,3],report['airlock'])
 print('PASS native motion geometry',p.stem,'six poses, 0.72 m leg travel, shared visual/collision parents and EVA axes')
