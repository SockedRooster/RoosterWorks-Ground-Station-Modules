from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R.parent/'rw-v075dev5/Source')]
from config_nodes import parse,dump,Node
GD=R/'GameData/RoosterWorksGroundModules'
settings={'acquireRange':'2.5','acquireForce':'20','acquireTorque':'12','acquireForceTweak':'100','acquireMinFwdDot':'.98','captureRange':'.08','captureMinFwdDot':'.998','captureMaxRvel':'.3','minDistanceToReEngage':'3'}
for path in (GD/'Parts').glob('*.cfg'):
 root=parse(path.read_text(encoding='utf-8'));part=root.children[0]
 for port in [n for n in part.children if n.get('name')=='ModuleDockingNode']:
  for key,value in settings.items():port.set(key,value)
 if part.get('name')=='RW_GND_END_250_125':
  part.set('description','Rounded 2.5 m-to-1.25 m endcap. Large end is a structural attachment only; the small end has one size1 docking interface. Clean planar-UV hatch, readable rooster badges, White/Grey finish and ring colors. Crossfeed always enabled; no staging.')
 path.write_text(dump(root),encoding='utf-8')
# Preserve the skycrane's original source while matching its endcap carrier to
# the sole 1.25 m port. This scoped compatibility rule only exists if installed.
patch=Node('ROOT',children=[Node('@PART[RW_SC_CARRIER_090]:NEEDS[RoosterWorksSkycrane]:AFTER[RoosterWorksSkycrane]',children=[Node('@MODULE[ModuleDockingNode]',[('@nodeType','size1')])])])
(GD/'Compatibility/SkycraneEndcapCarrier.cfg').write_text(dump(patch),encoding='utf-8')
path=GD/'RoosterWorksGroundModules.version';version=json.loads(path.read_text());version['VERSION']['BUILD']=15;path.write_text(json.dumps(version,indent=2)+'\n')
(R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
print('Finalized 23 aligned strong ports, single-port endcap, optional carrier compatibility, dev.15 version and checksums')
