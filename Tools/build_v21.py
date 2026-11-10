"""Scoped FLEX fixes from protected dev.20; no changes to other models."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent
sys.path[:0]=[str(W/'rw-v075dev5/Tools'),str(W/'rw-v075dev5/Source')]
from native_model import load,walk
from native_derivatives import write
from config_nodes import parse,dump
GD=R/'GameData/RoosterWorksGroundModules'
B=R/'Source/BaselineDev20'
if not B.exists():
 for rel in ('GameData/RoosterWorksGroundModules/Models/RW_GND_FLEX.mu','GameData/RoosterWorksGroundModules/Parts/RW_GND_FLEX.cfg','Reports/RW_GND_FLEX.json'):
  target=B/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/'ground-hotpatch-v20'/rel,target)
m=load(B/'GameData/RoosterWorksGroundModules/Models/RW_GND_FLEX.mu')
changed=[]
for path,n in walk(m.root):
 if n['name'].startswith('RW_FlexOverlapBoot_'):
  mesh=n['mesh'];v=[]
  for x,y,z in mesh['vertices']:
   r=(y*y+z*z)**.5
   factor=1.24/r if r>1.20 else 1
   # Recess the sleeve's front annulus behind the cap/bolt faces too.
   if abs(x)<.000001:x=.01 if 'TubeBase' in n['name'] else -.01
   v.append((x,y*factor,z*factor))
  mesh['vertices']=v;changed.append(n['name'])
 if n['name'].startswith('RW_FlexBootBand_'):
  mesh=n['mesh'];mesh['vertices']=[(x,y*1.247/1.232,z*1.247/1.232) for x,y,z in mesh['vertices']];changed.append(n['name'])
assert len(changed)==4
write(m,GD/'Models/RW_GND_FLEX.mu')
cfg=parse((B/'GameData/RoosterWorksGroundModules/Parts/RW_GND_FLEX.cfg').read_text(encoding='utf-8'));p=cfg.children[0]
p.set('breakingForce','3500');p.set('breakingTorque','3500')
p.set('description',p.get('description')+' Reinforced rigid end fittings with 3500 force/torque connection thresholds and separated ring surfaces.')
(GD/'Parts/RW_GND_FLEX.cfg').write_text(dump(cfg),encoding='utf-8')
report=json.loads((B/'Reports/RW_GND_FLEX.json').read_text())
report['dev21_changes']={'outer_boot_radius':1.24,'band_radius':1.247,'old_cap_radius':1.225,'breakingForce':3500,'breakingTorque':3500,'rigid_end_connections':True}
report['native_sha256']=hashlib.sha256((GD/'Models/RW_GND_FLEX.mu').read_bytes()).hexdigest()
(R/'Reports/RW_GND_FLEX.json').write_text(json.dumps(report,indent=2)+'\n')
p=GD/'RoosterWorksGroundModules.version';version=json.loads(p.read_text());version['VERSION']['BUILD']=21;p.write_text(json.dumps(version,indent=2)+'\n')
print('PASS rebuilt two separated FLEX boots/bands and 10x stronger connection thresholds')
