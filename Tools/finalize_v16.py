from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'rw-v075dev5/Source'))
from config_nodes import parse,dump
GD=R/'GameData/RoosterWorksGroundModules';count=0
for path in (GD/'Parts').glob('*.cfg'):
 root=parse(path.read_text(encoding='utf-8'))
 for port in [n for n in root.children[0].children if n.get('name')=='ModuleDockingNode']:
  port.set('acquireMinFwdDot','.258819');port.set('acquireTorque','30');count+=1
 path.write_text(dump(root),encoding='utf-8')
assert count==23
p=GD/'RoosterWorksGroundModules.version';v=json.loads(p.read_text());v['VERSION']['BUILD']=16;p.write_text(json.dumps(v,indent=2)+'\n')
(R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
print('Updated 23 ground ports: 75-degree approach and stronger rotational alignment')
