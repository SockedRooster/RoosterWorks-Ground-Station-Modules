"""Validate the precise normalized-name tether fix against accepted dev.13."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];W=R.parent;OLD=W/'ground-hotpatch-v13'
source=(R/'Source/GroundTether.cs').read_text()
before=(OLD/'Source/GroundTether.cs').read_text()
original='p.partInfo.name.StartsWith("RW_GND_", StringComparison.Ordinal)) result.Add(p);'
replacement='''// KSP normalizes underscores to dots in loaded part names.
                // Keep raw config names supported for prefabs and tooling.
                (p.partInfo.name.StartsWith("RW_GND_", StringComparison.Ordinal) ||
                 p.partInfo.name.StartsWith("RW.GND.", StringComparison.Ordinal))) result.Add(p);'''
assert source==before.replace(original,replacement),'Unexpected tether physics/lifecycle change'
for name in ('GroundDeploy.cs','GroundDocking.cs'):
 assert (R/'Source'/name).read_bytes()==(OLD/'Source'/name).read_bytes(),name
gd=R/'GameData';oldgd=OLD/'GameData'
newfiles={p.relative_to(gd).as_posix() for p in gd.rglob('*') if p.is_file()}
oldfiles={p.relative_to(oldgd).as_posix() for p in oldgd.rglob('*') if p.is_file()}
assert newfiles==oldfiles
changed={name for name in newfiles if (gd/name).read_bytes()!=(oldgd/name).read_bytes()}
assert changed=={'RoosterWorksGroundModules/Plugins/RoosterWorksGroundDeploy.dll','RoosterWorksGroundModules/RoosterWorksGroundModules.version'},changed
assert json.loads((gd/'RoosterWorksGroundModules/RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==14
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():
 assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
assert 'PASS 1667 distributed tether assertions' in (R/'Reports/tether-tests.log').read_text()
print('PASS only ground-part name recognition changed; normalized-name controller regression; all models/configs/docking/deployment retained; protected kits and manifest verified')
