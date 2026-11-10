from pathlib import Path
import sys,json,numpy as np,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v12'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from config_nodes import parse
gd=R/'GameData/RoosterWorksGroundModules';old=OLD/'GameData/RoosterWorksGroundModules'
for role in ('GRN','PWR','ELB'):
 m=load(gd/f'Models/RW_GND_{role}.mu');baseline=load(old/f'Models/RW_GND_{role}.mu');report=json.loads((R/f'Reports/RW_GND_{role}.json').read_text());nodes=[n for _,n in walk(m.root)]
 def collision(model):return {path:{k:v for k,v in n.items() if k!='children'} for path,n in walk(model.root) if 'collider' in n or n['name'].startswith(('RW_GroundLeg','RW_GroundStairs','RW_Dock_'))}
 assert collision(m)==collision(baseline),('Collision, animation or docking changed',role)
 if role in ('GRN','PWR'):
  removed=report['refinements']['removed_roof_objects'];assert len(removed)==20
  assert sum(s.startswith('Radiator fin') for s in removed)==18
  assert sum(s.startswith('Roof heat exchanger') for s in removed)==2
  assert sum(s.startswith('Roof maintenance rail') for s in removed)==0
 if role=='GRN':
  lamps=[n for n in nodes if 'light' in n];assert len(lamps)==9
  for level,y in enumerate((-.68,-.12,.44)):
   tier=[n for n in lamps if abs(n['position'][1]-y-.26)<1e-5];assert len(tier)==3
   for x in (-.88,-.44,0,.44,.88):
    for z in (-.65*(.72,.89,.66)[level],0,.65*(.72,.89,.66)[level]):
     plant=np.array((x,y+.10,z));lamp=min(tier,key=lambda n:np.linalg.norm(np.array(n['position'])-plant));distance=np.linalg.norm(np.array(lamp['position'])-plant)
     assert distance<lamp['light']['range']*.55
     # Both ends of the light ray stay in this shelf cavity, below the bed above.
     if level<2:assert max(plant[1],lamp['position'][1])<(-.68,-.12,.44)[level+1]-.065
   for material in ('grnleaf','grnleaflight','grnroot'):
    assert any('CropShelf_'+str(level) in n['name'] and any(m.materials[i]['name']=='RW_Ground_'+material for i in n.get('materials',[])) for n in nodes)
  assert any(n['name']=='RW_GreenhouseLamps' for n in nodes) and any(n['name']=='RW_GreenhouseInspectionLamps' for n in nodes)
 if role=='ELB':
  paths=report['roof_handrail_paths'];assert len(paths)==2 and all(len(p)==65 for p in paths)
  assert all(abs(p[1]-1.38)<1e-6 for path in paths for p in path)
  yellow=[mat for mat in m.materials if mat['name'].endswith('rw_safety_yellow')];assert len(yellow)==1
 print('PASS',role,'requested roof/lighting/rail geometry; collision, docking and animation retained',flush=True)
allowed={f'Models/RW_GND_{role}.mu' for role in ('HAB','LAB','CMD','LOG','GRN','AIR','PWR','TUB')}|{'RoosterWorksGroundModules.version'}
changes=set()
newfiles={p.relative_to(gd).as_posix() for p in gd.rglob('*') if p.is_file()}-{p.relative_to(old).as_posix() for p in old.rglob('*') if p.is_file()}
assert not newfiles,newfiles
for p in old.rglob('*'):
 if p.is_file() and p.read_bytes()!=(gd/p.relative_to(old)).read_bytes():changes.add(p.relative_to(old).as_posix())
assert changes<=allowed,changes
for p in (gd/'Parts').glob('*.cfg'):assert p.read_bytes()==(old/'Parts'/p.name).read_bytes(),p.name
assert json.loads((gd/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==13
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
print('PASS all gameplay configs and runtime bytes unchanged; protected dev.10/core/art inputs and manifest')
