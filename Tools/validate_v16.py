from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;OLD=W/'ground-hotpatch-v15';GD=R/'GameData/RoosterWorksGroundModules';OGD=OLD/'GameData/RoosterWorksGroundModules'
sys.path.insert(0,str(W/'rw-v075dev5/Source'))
from config_nodes import parse,dump
before=(OLD/'Source/GroundDocking.cs').read_text()
expected=before.replace('''// Preserve stock approach/capture states, but require close alignment
            // before the stronger attraction starts. Separate beyond the acquire
            // radius before an undocked pair can capture each other again.''','''// Let stock magnetic torque straighten a broad initial approach.
            // Keep final capture close and aligned rather than locking crooked.
            // Separation beyond the acquire radius prevents immediate recapture.''').replace('port.acquireTorque = 12f','port.acquireTorque = 30f').replace('port.acquireMinFwdDot = .98f;','port.acquireMinFwdDot = .258819f; // cos(75 degrees)').replace('strong aligned acquisition','strong pull and wide-angle alignment assistance')
assert (R/'Source/GroundDocking.cs').read_text()==expected,'Only requested angular threshold, torque, comments and info text may change'
for name in ('GroundDeploy.cs','GroundTether.cs'):assert (R/'Source'/name).read_bytes()==(OLD/'Source'/name).read_bytes()
oldfiles={p.relative_to(OGD).as_posix() for p in OGD.rglob('*') if p.is_file()};newfiles={p.relative_to(GD).as_posix() for p in GD.rglob('*') if p.is_file()}
assert oldfiles==newfiles
changed={name for name in oldfiles if (GD/name).read_bytes()!=(OGD/name).read_bytes()}
expected_changes={f'Parts/{p.name}' for p in (GD/'Parts').glob('*.cfg')}|{'RoosterWorksGroundModules.version','Plugins/RoosterWorksGroundDeploy.dll'}
assert changed==expected_changes,changed^expected_changes
total=0
for path in (GD/'Parts').glob('*.cfg'):
 a=parse(path.read_text(encoding='utf-8'));b=parse((OGD/'Parts'/path.name).read_text(encoding='utf-8'))
 for port in [n for n in a.children[0].children if n.get('name')=='ModuleDockingNode']:
  total+=1;assert port.get('acquireMinFwdDot')=='.258819' and port.get('acquireTorque')=='30'
  assert port.get('acquireRange')=='2.5' and port.get('acquireForce')=='20'
  assert port.get('captureMinFwdDot')=='.998' and port.get('captureRange')=='.08' and port.get('captureMaxRvel')=='.3'
  port.set('acquireMinFwdDot','.98');port.set('acquireTorque','12')
 assert dump(a)==dump(b),path.name
assert total==23
assert 'PASS 4959 docking/menu assertions' in (R/'Reports/docking-tests.log').read_text()
assert json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==16
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
print('PASS 23 wide-angle ports, stronger rotation assist, retained final seating, 4959 controller checks; every model, texture, resource, menu policy, endcap, tether and source input preserved')
