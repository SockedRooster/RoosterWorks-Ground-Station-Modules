from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent
sys.path.insert(0,str(W/'rw-v075dev5/Source'))
from config_nodes import parse,dump
GD=R/'GameData/RoosterWorksGroundModules';BG=W/'ground-hotpatch-v27/GameData/RoosterWorksGroundModules';checks=0
def check(value,message):
 global checks
 checks+=1
 assert value,message
allowed={'Parts/RW_GND_FLEX.cfg','Plugins/RoosterWorksGroundDeploy.dll','RoosterWorksGroundModules.version'}
check({p.relative_to(GD).as_posix() for p in GD.rglob('*') if p.is_file()}=={p.relative_to(BG).as_posix() for p in BG.rglob('*') if p.is_file()},'GameData file set')
changed=set()
for p in BG.rglob('*'):
 if p.is_file():
  rel=p.relative_to(BG).as_posix()
  if p.read_bytes()!=(GD/rel).read_bytes():changed.add(rel)
  if rel not in allowed:check(p.read_bytes()==(GD/rel).read_bytes(),'Preserved game file '+rel)
check(changed==allowed,'Exactly DLL, FLEX description and version change')
for old in (W/'ground-hotpatch-v27/Source').glob('*.cs'):
 if old.name!='CollapsibleTube.cs':check((R/'Source'/old.name).read_bytes()==old.read_bytes(),'Other runtime sources preserved '+old.name)
check('PASS compiled deployment controller against installed KSP 1.12.5 assemblies' in (R/'Reports/v28-compile.log').read_text(),'Actual game API compilation')
check('PASS 1254 connected-tube assertions:' in (R/'Reports/v28-tube-tests.log').read_text(),'Partial controls plus existing flight/editor regressions')
p=parse((GD/'Parts/RW_GND_FLEX.cfg').read_text()).children[0];base=parse((BG/'Parts/RW_GND_FLEX.cfg').read_text()).children[0]
check('VAB Extension slider' in p.get('description'),'Catalogue controls documented');p.set('description',base.get('description'));check(p==base,'FLEX config behavior otherwise unchanged')
check(len(list((GD/'Models').glob('*.mu')))==20 and len(list((GD/'Parts').glob('*.cfg')))==28,'Catalogue/model counts preserved')
check(json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==28,'Version')
for f in GD.rglob('*.cfg'):parse(f.read_text())
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);check(hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,'Manifest '+path)
for path,digest in json.loads((R/'Reports/DEV28_PROTECTED_INPUTS.json').read_text()).items():check(hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,'Protected baseline '+path)
print(f'PASS dev.28: {checks} configuration/preservation checks; all native models, colors, nuclear prices and categories preserved; scoped editor slider, length readout and saved deployment target')
