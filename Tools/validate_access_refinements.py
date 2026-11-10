"""Check hose attachment, rail clearance, boarding volume and gameplay scope."""
from pathlib import Path
import sys,json,numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v4'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from config_nodes import parse,dump
from poses import world_nodes
gd=R/'GameData/RoosterWorksGroundModules';oldgd=OLD/'GameData/RoosterWorksGroundModules'
for p in sorted((gd/'Models').glob('*.mu')):
 if p.stem=='RW_GND_END_250_125':continue # Endcap has no legs, stairs or EVA.
 m=load(p);report=json.loads((R/f'Reports/{p.stem}.json').read_text());nodes={n['name']:n for _,n in walk(m.root)}
 assert report['legs']==4
 part=parse((gd/f'Parts/{p.stem}.cfg').read_text()).children[0];oldpart=parse((oldgd/f'Parts/{p.stem}.cfg').read_text()).children[0]
 for k in ('mass','cost','entryCost','CrewCapacity'):assert part.get(k)==oldpart.get(k)
 for heading in ('RESOURCE','INTERNAL'):
  assert [dump(n) for n in part.children if n.header==heading]==[dump(n) for n in oldpart.children if n.header==heading]
 assert {k:v for k,v in part.values if k.startswith('node_stack_')}=={k:v for k,v in oldpart.values if k.startswith('node_stack_')}
 hoses={k:v for k,v in report['rig_members'].items() if k.startswith('Hydraulic hose')}
 assert len(hoses)==4 and set(hoses.values())=={b['name'] for b in report['motion'] if b['mechanism']=='Legs'}
 for progress in (0,.2,.4,.6,.8,1):
  mats={n['name']:matrix for n,matrix in world_nodes(m,progress)}
  for name,bounds in report['hose_bounds'].items():
   root=hoses[name];matrix=mats[root];lo=np.array(bounds[0]);assert lo[1]+matrix[1,3] >= report['foot_bounds'][root][0][1]+matrix[1,3]-.01
 if report['stairs']:
  clearance=report['stair_clearance'];cx=report['airlock'][0]
  assert clearance['width']==1.21
  assert clearance['rail_inner_half_width']-clearance['door_mount_half_width']>=.10
  for progress in np.linspace(0,1,27):
   mats={n['name']:matrix for n,matrix in world_nodes(m,float(progress))};assert np.allclose(mats['RW_GroundStairs'][0,:3],(1,0,0))
  full={n['name']:matrix for n,matrix in world_nodes(m,1)};hatch=nodes['Ground_EVA_Airlock'];matrix=full[hatch['name']];collider=hatch['collider'];center=matrix[:3,3]+matrix[:3,:3]@np.array(collider['center']);size=np.array(collider['size']);lo=center-size/2;hi=center+size/2
  top=clearance['landing_top']
  for x in (cx-.25,cx,cx+.25):
   for y in (top+.05,top+.45,top+.95):
    point=np.array((x,y,1.65));assert np.all(point>=lo) and np.all(point<=hi),('Landing boarding overlap missing',p.stem,point,lo,hi)
  assert np.allclose(matrix[:3,3],report['airlock']) and report['airlock']==json.loads((OLD/f'Reports/{p.stem}.json').read_text())['airlock'],'Exit spawn location changed'
 print('PASS',p.stem,'four attached hoses; unchanged gameplay; rail clearance and landing boarding' if report['stairs'] else 'four attached hoses; unchanged gameplay')
for path in (gd/'Compatibility').glob('*.cfg'):
 if path.name=='GroundRingGeometry.cfg' or path.name.startswith('Endcap'):continue
 assert path.read_bytes()==(oldgd/'Compatibility'/path.name).read_bytes(),path.name
print('PASS existing role backends unchanged; no orbital/support mutation')
