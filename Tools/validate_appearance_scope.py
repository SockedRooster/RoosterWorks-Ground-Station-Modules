"""Check current core swatch eligibility for actual ground model/controller IDs."""
from pathlib import Path
import sys,copy,fnmatch
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5'
sys.path.insert(0,str(CORE/'Source'))
from config_nodes import parse,dump
from selector_scope import FINISH,MENU,SWATCH
gd=CORE/'GameData/RoosterWorksStationModules'
finish=parse((gd/'Compatibility/ExteriorFinish.cfg').read_text()).children[0]
ui=parse((gd/'Compatibility/EditorAppearance.cfg').read_text()).children
assert finish.header==FINISH and [n.header for n in ui]==[MENU,SWATCH]
def modules(p):return [n.get('name') for n in p.children if n.header=='MODULE']
for path in (R/'GameData/RoosterWorksGroundModules/Parts').glob('*.cfg'):
 p=parse(path.read_text()).children[0]
 assert all(modules(p).count(k)==1 for k in ('ModuleRWStationFinish','ModuleRWRingColor','ModuleRWEditorMenu'))
 assert not any(n.header=='MODEL' and fnmatch.fnmatch(n.get('model',''),'RoosterWorksStationModules/Models/*') for n in p.children)
 # Core AFTER stage adds both optional B9 controls to explicitly equipped ground parts.
 p.children+=copy.deepcopy(ui[1].children)
 assert {n.get('moduleID') for n in p.children if n.get('name')=='ModuleB9PartSwitch'}=={'RWFinishSwatch','RWRingSwatch'}
 print('PASS core appearance controls',p.get('name'))
support=R.parent/'work/RoosterWorks-Station-Support-v1.0.5/GameData/RoosterWorksStationSupport/Parts'
if support.is_dir():
 for path in support.glob('*.cfg'):
  p=parse(path.read_text()).children[0]
  assert not any(n.header=='MODEL' and fnmatch.fnmatch(n.get('model',''),'RoosterWorksStationModules/Models/*') for n in p.children)
  assert 'ModuleRWRingColor' not in modules(p)
 print('PASS Support remains outside station appearance selectors; no support hotfix required')
