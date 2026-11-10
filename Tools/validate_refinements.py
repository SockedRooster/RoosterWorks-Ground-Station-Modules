from pathlib import Path
import sys,json,numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from config_nodes import parse
gd=R/'GameData/RoosterWorksGroundModules'
for role in ('HAB','LAB','CMD','LOG','GRN','AIR','PWR','HUB','TUB','ELB'):
 report=json.loads((R/f'Reports/RW_GND_{role}.json').read_text());m=load(gd/f'Models/RW_GND_{role}.mu')
 if role not in ('HUB','ELB'):
  endpoints=sorted(v[0] for v in report['nodes'].values())
  assert len(report['refinements']['extended_pipes'])==4
  for pipe in report['refinements']['extended_pipes']:assert np.isclose(pipe['half'],max(endpoints),atol=2e-6)
 else:
  paths=report['service_paths'];assert len(paths)==(8 if role=='HUB' else 4)
  # Every port receives both sizes of pipe on both sides of its centerline.
  for port in report['nodes'].values():
   p=np.array(port[:3]);direction=np.array(port[3:6]);tangent=np.cross((0,1,0),direction)
   actual=[np.array(path['points'][i]) for path in paths for i in (0,-1) if abs(np.dot(np.array(path['points'][i])-p,direction))<1e-5]
   expected=[p+y*np.array((0,1,0))+s*.6*tangent for y in (-1.03,-1.16) for s in (-1,1)]
   assert len(actual)==4
   for point in expected:assert min(np.linalg.norm(point-q) for q in actual)<1e-5,(role,point,actual)
 if role=='HAB':
  glass=np.array([v for _,n in walk(m.root) if 'mesh' in n and any(m.materials[i]['name']=='RW_Ground_glass' for i in n.get('materials',[])) for v in n['mesh']['vertices']])
  # Heat exchanger footprint is |Z| <= .275; all window glazing must lie
  # beyond it, with at least 25 mm of lateral separation.
  assert np.abs(glass[:,2]).min()>.300,('Roof overlap',np.abs(glass[:,2]).min())
 if role=='GRN':
  assert report['replaced_greenhouse_interior_triangles']>10000
  assert report['refinements']['greenhouse_leg_shift']==.26
  lights=[n for _,n in walk(m.root) if 'light' in n];assert len(lights)==9 and all(abs(n['light']['intensity']-1.6)<1e-5 for n in lights)
  roots=np.array([v for _,n in walk(m.root) if 'mesh' in n and any(m.materials[i]['name']=='RW_Ground_grnroot' for i in n.get('materials',[])) for v in n['mesh']['vertices']])
  for y in (-.68,-.12,.44):assert np.any(np.isclose(roots[:,1],y,atol=.002))
  assert np.all(np.min(abs(roots[:,1,None]-np.array((-.68,-.668,-.12,-.108,.44,.452))),axis=1)<.002),'Soil must lie on horizontal beds'
 print('PASS refinements',role,'stack-plane service continuity / roof, crop and lighting checks where applicable',flush=True)
