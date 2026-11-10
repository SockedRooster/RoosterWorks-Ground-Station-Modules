from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
p=R/'Tools/TetherTests.cs';s=p.read_text()
s=s.replace('AddPart(v,"RW_GND_CMD")','AddPart(v,"RW.GND.CMD")').replace('AddPart(m.vessel,"RW_GND_"+role)','AddPart(m.vessel,"RW.GND."+role.Replace("_","."))')
s=s.replace('p.partInfo.name.StartsWith("RW_GND_")','(p.partInfo.name.StartsWith("RW_GND_")||p.partInfo.name.StartsWith("RW.GND."))')
s=s.replace('var m=FullBase();AddPart', '''// Both KSP-normalized and raw config identifiers work in one assembly.
        var mixed=FullBase();AddPart(mixed.vessel,"RW_GND_HAB");
        foreach(string name in new[]{"RW.GNDX.HAB","RW_GNDX_HAB","RW.GND","RW_GND","stockPart"})AddPart(mixed.vessel,name);
        AddPart(mixed.vessel,null);var unknown=AddPart(mixed.vessel,"unknown");unknown.partInfo=null;
        mixed.EnableTether();Tick(mixed);Held(mixed,12);Cleanup(mixed);
        var m=FullBase();AddPart''',1)
p.write_text(s)
p=R/'Tools/snapshot_inputs.py';p.write_text(p.read_text().replace("'ground-hotpatch-v12'","'ground-hotpatch-v13'"))
p=R/'Tools/package.py';p.write_text(p.read_text().replace('v0.8.0-dev.13','v0.8.0-dev.14'))
p=R/'Tools/build_configs.py';p.write_text(p.read_text().replace('"BUILD":13','"BUILD":14').replace('"BUILD": 13','"BUILD": 14'))
p=R/'GameData/RoosterWorksGroundModules/RoosterWorksGroundModules.version';v=json.loads(p.read_text());v['VERSION']['BUILD']=14;p.write_text(json.dumps(v,indent=2)+'\n')
p=R/'README.md';s=p.read_text().replace('v0.8.0-dev.13 TEST','v0.8.0-dev.14 TEST',1).replace('## Changes in dev.13','## Retained changes in dev.13',1)
s=s.replace('## Retained changes in dev.13','''## Changes in dev.14

Fixed the tether waiting indefinitely for connected ground modules. KSP
normalizes underscores in loaded part identifiers to dots (RW.GND.CMD).
The target filter now accepts both normalized and original RW_GND_ names.
Regression tests exercise the full tether lifecycle with normalized names,
mixed naming, and unrelated or missing identifiers. Existing tether physics,
deployment and docking logic remain unchanged. All models, configurations
and textures are byte-identical to dev.13; only the runtime and version change.

Close KSP, replace GameData/RoosterWorksGroundModules, restart, load the base,
lower all supports and enable Ground Tether. Confirm Engaged: X/X modules.
This is an offline-validated test build; in-game confirmation is still needed.
Run Tools/test-tether.ps1 with pwsh and Tools/validate_tether_package.py with
Python to verify this update. The accepted dev.13 package remains protected.

## Retained changes in dev.13''',1)
p.write_text(s,encoding='utf-8')
print('Prepared normalized-name regression and dev.14 package')
