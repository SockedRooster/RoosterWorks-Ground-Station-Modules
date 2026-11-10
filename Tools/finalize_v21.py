from pathlib import Path
R=Path(__file__).resolve().parents[1]
logs=['runtime-build.log','validate.py.log','v21-validation.log','tube-motion-tests.log']
(R/'validation.log').write_text('\n'.join('=== '+n+' ===\n'+(R/'Reports'/n).read_text(encoding='utf-8-sig') for n in logs),encoding='utf-8')
p=R.parent/'WORKSPACE_INDEX.md';s=p.read_text(encoding='utf-8');start=s.index('Latest ground build:');end=s.index('Updated October',start)
s=s[:start]+'''Latest ground build: **ground-hotpatch-v21 / v0.8.0-dev.21 TEST**, superseding
dev.20. FLEX connections have 10x force/torque thresholds and rigid end fittings;
two end boots/bands are separated from the original caps to prevent z-fighting.
Other twelve models/configs and compatibility maps match dev.20. Install/source
ZIPs use dev.21 names in outputs/. Packed source is
Source/Equipment/RoosterWorks-Ground-dev21.blend. Native validation, actual KSP
compilation and 1,052 connected-tube assertions pass; in-game test pending.

'''+s[end:]
s=s.replace('| Ground Modules | 0.8.0-dev.20 | 0.8.0-dev.19 | ground-hotpatch-v20 / ground-hotpatch-v19 |','| Ground Modules | 0.8.0-dev.21 | 0.8.0-dev.20 | ground-hotpatch-v21 / ground-hotpatch-v20 |');p.write_text(s,encoding='utf-8')
p=R.parent/'ROOSTERWORKS_DEVELOPMENT_CONTEXT.md';s=p.read_text(encoding='utf-8');p.write_text('''Latest ground build: ground-hotpatch-v21 / v0.8.0-dev.21 TEST. User requested stronger expandable-tube connections and correction of mottled rings at both ends. Boot and cap cylinders were exactly radius 1.225 (z-fighting); boot outer radius now 1.24, bands 1.247, front annulus recessed 10 mm. Four mesh surfaces change only; ring maps/finish/end seals retained. FLEX breakingForce/Torque 350 to 3500. CollapsibleTube.FixedUpdate reinforces only direct joints touching its Rigidbody through public PartJoint.SetBreakingForces(3500,3500); locks linear/angular axes, projection .02 m/1 degree. Runs idle too and catches recreated docking joints. Moving anchors still actuate attached assemblies. Compiled with KSP 1.12.5; 1,052 connected-tube assertions including both ends/recreated joints/unrelated joint preservation; native and broad checks pass. Other twelve models/configs and all compatibility maps byte-identical to dev.20. Source packed in Source/Equipment/RoosterWorks-Ground-dev21.blend; builder Tools/build_v21.py uses bundled BaselineDev20. Install/source ZIPs in outputs/. Live game verification pending. No game/save/core/artist/skycrane writes or publication. Prior notes below.

'''+s,encoding='utf-8')
print('Finalized dev.21 notes and validation summary')
