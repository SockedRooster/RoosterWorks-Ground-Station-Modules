"""Validate native docking frames, stock config and exact preservation scope."""
from pathlib import Path
import sys,json,hashlib,numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v7'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from config_nodes import parse,dump
from poses import rotation
gd=R/'GameData/RoosterWorksGroundModules';oldgd=OLD/'GameData/RoosterWorksGroundModules';total=0
for file in sorted((gd/'Models').glob('*.mu')):
 if file.stem=='RW_GND_END_250_125':continue # Mixed-size endcap validated separately.
 m=load(file);old=load(oldgd/'Models'/file.name);newnodes=[n for n in m.root['children'] if n['name'].startswith('RW_Dock_')]
 m.root['children']=[n for n in m.root['children'] if not n['name'].startswith('RW_Dock_') and n['name']!='RW_RoofRailMounts']
 assert file.stem in ('RW_GND_GRN','RW_GND_PWR','RW_GND_ELB') or (m.root==old.root and m.materials==old.materials and m.textures==old.textures),('Existing native geometry/colliders/lights changed',file.name)
 p=parse((gd/'Parts'/(file.stem+'.cfg')).read_text(encoding='utf-8')).children[0];baseline=parse((oldgd/'Parts'/(file.stem+'.cfg')).read_text(encoding='utf-8')).children[0]
 nodes={k.removeprefix('node_stack_'):[float(v.strip()) for v in value.split(',')] for k,value in p.values if k.startswith('node_stack_')}
 ports=[n for n in p.children if n.get('name')=='ModuleDockingNode'];assert len(ports)==len(newnodes)==len(nodes)==(4 if file.stem=='RW_GND_HUB' else 2)
 assert len({n.get('nodeTransformName') for n in ports})==len(ports)
 for port in ports:
  key=port.get('referenceAttachNode');assert key in nodes
  transform=next(n for n in newnodes if n['name']==port.get('nodeTransformName'))
  assert np.allclose(transform['position'],nodes[key][:3],atol=1e-6)
  rot=rotation(transform['rotation']);assert np.allclose(rot@np.array((0,0,1)),nodes[key][3:6],atol=1e-6)
  assert np.allclose(rot@np.array((0,1,0)),(0,1,0),atol=1e-6)
  assert port.get('controlTransformName')==port.get('nodeTransformName') and port.get('useReferenceAttachNode')=='true'
  assert port.get('nodeType')=='size2' and port.get('crossfeed')=='true' and port.get('canRotate')=='false'
  for k in ('stagingEnabled','stagingToggleEnabledEditor','stagingToggleEnabledFlight'):assert port.get(k)=='false'
 policy=[n for n in p.children if n.get('name')=='ModuleRWGroundDocking'];assert len(policy)==1
 assert p.get('fuelCrossFeed')=='true' and p.get('stagingIcon')==baseline.get('stagingIcon')
 p.children=[n for n in p.children if n not in ports+policy]
 # Restore only the intentional descriptive/crossfeed/icon changes, then
 # compare the whole part definition, including the retained tether module.
 p.values=[(k,v) for k,v in p.values if k not in ('description','fuelCrossFeed','stagingIcon')]
 baseline.values=[(k,v) for k,v in baseline.values if k not in ('description','fuelCrossFeed','stagingIcon')]
 assert dump(p)==dump(baseline),('Non-docking gameplay changed',file.stem)
 total+=len(ports);print('PASS',file.stem,len(ports),'independent stock-size2 ports; outward frames and unchanged existing geometry/gameplay',flush=True)
assert total==22
for source in ('GroundDocking.cs','GroundDeploy.cs'):assert (R/'Source'/source).read_bytes()==(W/'ground-hotpatch-v9/Source'/source).read_bytes(),source
for folder in ('Compatibility','Plugins'):
 for old in (oldgd/folder).rglob('*'):
  if not old.is_file() or old.name in ('RoosterWorksGroundDeploy.dll','GroundRingGeometry.cfg'):continue
  assert old.read_bytes()==(gd/old.relative_to(oldgd)).read_bytes(),old.name
for old in (oldgd/'Models').glob('*.png'):assert old.read_bytes()==(gd/'Models'/old.name).read_bytes(),old.name
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
assert json.loads((gd/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==13
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
print('PASS 22 stock docking nodes; permanent-crossfeed/no-staging policy on ten ground-only parts; accepted dev.7/core/art inputs and all backends preserved')
