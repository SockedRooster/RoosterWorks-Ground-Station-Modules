"""Check the new endcap and preserve the complete accepted dev.8 payload."""
from pathlib import Path
import sys,json,hashlib
from collections import Counter
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v12'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from config_nodes import parse
from poses import rotation
ID='RW_GND_END_250_125';gd=R/'GameData/RoosterWorksGroundModules';model=load(gd/'Models'/(ID+'.mu'));report=json.loads((R/'Reports'/(ID+'.json')).read_text());lookup={n['name']:n for _,n in walk(model.root)}
triangles=0
for n in lookup.values():
 if 'mesh' in n:
  mesh=n['mesh'];v=np.array(mesh['vertices']);norm=np.array(mesh['normals']);t=np.array(mesh['submeshes'][0]);triangles+=len(t)
  assert len(v)<65535 and np.isfinite(v).all() and np.isfinite(norm).all()
  assert np.allclose(np.linalg.norm(norm,axis=1),1,atol=2e-5)
  dots=np.sum(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]])*norm[t].mean(1),axis=1);assert np.all(dots>=-1e-6),(n['name'],dots.min())
  assert v[:,0].min()>=-.45001 and v[:,0].max()<=.45001,('Detail intrudes past mating plane',n['name'],v[:,0].min(),v[:,0].max())
 if 'collider' in n:
  c=n['collider'];assert c['convex']==1 and not c['trigger'];mesh=c['mesh'];assert sum(map(len,mesh['submeshes']))<=255
  edges=Counter()
  for t in mesh['submeshes'][0]:
   points=[tuple(round(x,5) for x in mesh['vertices'][i]) for i in t]
   for a,b in zip(points,points[1:]+points[:1]):edges[tuple(sorted((a,b)))]+=1
  assert set(edges.values())=={2},('Open hull',n['name'])
assert triangles==report['triangles'] and report['length']==.9 and report['legs']==report['stairs']==0
for texture in model.textures:Image.open(gd/'Models'/(texture['name']+'.png')).verify()
part=parse((gd/'Parts'/(ID+'.cfg')).read_text()).children[0];assert part.get('CrewCapacity')=='0' and part.get('mass')=='.35'
ports=[n for n in part.children if n.get('name')=='ModuleDockingNode'];assert len(ports)==2
for port in ports:
 end=port.get('referenceAttachNode');frame=lookup[port.get('nodeTransformName')];v=[float(x) for x in part.get('node_stack_'+end).split(',')]
 assert np.allclose(frame['position'],v[:3]) and np.allclose(rotation(frame['rotation'])@np.array((0,0,1)),v[3:6],atol=1e-6)
 assert port.get('nodeType')==('size1' if end=='top' else 'size2')
 for key in ('stagingEnabled','stagingToggleEnabledEditor','stagingToggleEnabledFlight'):assert port.get(key)=='false'
 assert port.get('crossfeed')=='true'
assert all(any(n.get('name')==name for n in part.children) for name in ('ModuleRWStationFinish','ModuleRWRingColor','ModuleRWEditorMenu','ModuleRWGroundDocking'))
assert part.get('fuelCrossFeed')=='true' and not any(n.get('name') in ('ModuleCommand','ModuleRWGroundDeploy','ModuleRWGroundTether') for n in part.children)
maps=parse((gd/'Compatibility/EndcapRingGeometry.cfg').read_text()).children;assert len(maps)==1 and maps[0].get('model')==ID and maps[0].children
for spec in maps[0].children:
 n=dict(walk(model.root))[spec.get('path')];assert len(n['mesh']['vertices'])==int(spec.get('vertices'))
 for color in ('steel','white','charcoal','blue','green','red','gold'):assert (CORE/'GameData/RoosterWorksStationModules/Models'/('rwm_ring_'+spec.get('texture')+'_'+color+'.png')).is_file()
for file in (OLD/'GameData').rglob('*'):
 if file.is_file() and file.name not in ('RoosterWorksGroundModules.version','RoosterWorksGroundDeploy.dll','RW_GND_GRN.mu','RW_GND_PWR.mu','RW_GND_ELB.mu','RW_GND_HAB.mu','RW_GND_LAB.mu','RW_GND_CMD.mu','RW_GND_LOG.mu','RW_GND_AIR.mu','RW_GND_TUB.mu','GroundRingGeometry.cfg'):assert file.read_bytes()==(R/file.relative_to(OLD)).read_bytes(),('Existing payload changed',file)
assert json.loads((gd/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==13
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
assert (R/'Source/Endcap'/(ID+'.blend')).is_file() and (R/'Source/Endcap'/(ID+'.obj')).is_file()
print('PASS new .9 m endcap: native normals/winding, 16-bit meshes, closed convex collision, clear mating planes, size2/size1 frames, finish/rings, no staging and permanent crossfeed')
print('PASS retained endcap and existing dev.8 model/config bytes unchanged; core and artist inputs protected; Blender/OBJ source and manifest present')
