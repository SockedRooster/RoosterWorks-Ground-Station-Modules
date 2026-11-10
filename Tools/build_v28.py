"""Version, description and preservation manifest for the partial FLEX slider."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v27';GD=R/'GameData/RoosterWorksGroundModules'
sys.path.insert(0,str(W/'rw-v075dev5/Source'))
from config_nodes import parse,dump
protected={p.relative_to(W).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for base in (B,W/'rw-v075dev10') for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
(R/'Reports/DEV28_PROTECTED_INPUTS.json').write_text(json.dumps(protected,indent=2)+'\n')
p=GD/'Parts/RW_GND_FLEX.cfg';cfg=parse((B/'GameData/RoosterWorksGroundModules/Parts/RW_GND_FLEX.cfg').read_text());part=cfg.children[0]
part.set('description',part.get('description')+' VAB Extension slider selects and saves any intermediate deployment from 0 to 100% in 0.1% steps (2.8 mm travel); live tube length is displayed in meters. Moving-end connected modules follow the adjustment.')
p.write_text(dump(cfg))
p=GD/'RoosterWorksGroundModules.version';version=json.loads(p.read_text());version['VERSION']['BUILD']=28;p.write_text(json.dumps(version,indent=2)+'\n')
for path,digest in protected.items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
(R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
print('PASS scoped FLEX editor control build; dev.27 and Station Modules preserved')
