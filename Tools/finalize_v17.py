from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'rw-v075dev5/Source'))
from config_nodes import parse,dump
GD=R/'GameData/RoosterWorksGroundModules';ports=0
settings={'acquireRange':'2.5','acquireForce':'40','acquireTorque':'30','acquireForceTweak':'100','acquireMinFwdDot':'.258819','captureRange':'.08','captureMinFwdDot':'.998','captureMaxRvel':'.3','minDistanceToReEngage':'3'}
for p in (GD/'Parts').glob('*.cfg'):
 root=parse(p.read_text(encoding='utf-8'))
 for port in [n for n in root.children[0].children if n.get('name')=='ModuleDockingNode']:
  ports+=1
  for key,value in settings.items():port.set(key,value)
 p.write_text(dump(root),encoding='utf-8')
assert ports==25
p=GD/'RoosterWorksGroundModules.version';v=json.loads(p.read_text());v['VERSION']['BUILD']=17;p.write_text(json.dumps(v,indent=2)+'\n')
(R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
print('Finalized 12 parts / 25 ports / doubled acquire force / dev.17 checksums')
