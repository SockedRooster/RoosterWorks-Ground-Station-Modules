from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'Tools/snapshot_inputs.py';p.write_text(p.read_text().replace("'ground-hotpatch-v14'","'ground-hotpatch-v15'"))
p=R/'Tools/package.py';p.write_text(p.read_text().replace('v0.8.0-dev.15','v0.8.0-dev.16'))
p=R/'Tools/build_configs.py';p.write_text(p.read_text().replace("'BUILD':15","'BUILD':16"))
p=R/'Tools/DockingTests.cs';s=p.read_text().replace('n.acquireTorque==12','n.acquireTorque==30').replace('n.acquireMinFwdDot==.98f','n.acquireMinFwdDot==.258819f')
s=s.replace('m.OnLoad(new ConfigNode());Validate(p);Dirty(p);m.OnStart', '''m.OnLoad(new ConfigNode());Validate(p);
   var acquisition=p.FindModulesImplementing<ModuleDockingNode>()[0];
   foreach(int degrees in new[]{0,15,30,45,60,74,75,76,90,120,180}){
    bool admitted=Math.Cos(degrees*Math.PI/180.0)>=acquisition.acquireMinFwdDot;
    Check(admitted==(degrees<=75),"wide approach admits modest/crooked angles and excludes backward faces: "+degrees);
   }
   Dirty(p);m.OnStart''',1)
p.write_text(s)
p=R/'README.md';s=p.read_text(encoding='utf-8').replace('v0.8.0-dev.15 TEST','v0.8.0-dev.16 TEST',1).replace('## Changes in dev.15','## Retained changes in dev.15',1)
intro='''## Changes in dev.16

Ground docking now accepts initial angular errors up to approximately 75 degrees,
instead of dev.15's 11.5 degrees. The acquire forward-dot threshold is 0.258819.
Rotational alignment assistance increases from acquireTorque 12 to 30, letting
the stock docking mechanism turn a crooked approach toward alignment while
pulling the ports together. Initial ports must still face broadly toward one
another; this does not capture backwards-facing ports through module hulls.

The 2.5 m acquisition range and acquireForce 20 remain. Final docking still
requires close, aligned seating (0.08 m, about 3.6 degrees, 0.3 m/s maximum
relative capture speed); attraction and rotational assistance operate before
that point. This is assistance, not teleportation or a simulated guarantee of
alignment against terrain, collision, tethers or excessive approach speed.
Release the ground tether while positioning modules for docking.

All models, textures, menus, port counts, endcap changes, resource values,
deployment, distributed tether and roadmap remain as dev.15. New behavior is
applied to existing ground ports as well as newly placed parts. Close KSP,
replace GameData/RoosterWorksGroundModules and restart before testing.

Rebuild and validate with Tools/finalize_v16.py after the earlier builders,
Tools/build-runtime.ps1, Tools/refresh_manifest.py, Tools/test-docking.ps1,
Tools/validate.py and Tools/validate_v16.py. Stock API compilation and controller
checks are offline; capture/rotation behavior requires an in-game trial.

'''
s=s.replace('## Retained changes in dev.15',intro+'## Retained changes in dev.15',1);p.write_text(s,encoding='utf-8')
print('Prepared dev.16 wide-angle regression, source tools and documentation')
