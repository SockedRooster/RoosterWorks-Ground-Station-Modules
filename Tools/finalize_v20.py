from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'Tools/package.py'
s=p.read_text().replace("'PASS dev.19: 13 parts'", "'PASS dev.20: 13 models'").replace('Reports/v19-validation.log','Reports/v20-validation.log').replace("'PASS 175 collapsible-tube/light'", "'PASS 1036'").replace('Reports/flex-tests.log','Reports/tube-motion-tests.log').replace('RoosterWorks-Ground-dev19.blend','RoosterWorks-Ground-dev20.blend').replace("'dev19' in p.name", "'dev20' in p.name").replace('v0.8.0-dev.19-', 'v0.8.0-dev.20-')
p.write_text(s,encoding='utf-8')
(R/'README.md').write_text('''# RoosterWorks Ground Modules — v0.8.0-dev.20 TEST

Requires KSP 1.12.5, ModuleManager and RoosterWorks Station Modules v0.7.5-dev.5.
This separate ground addon retains existing optional integrations.

## Changes

- FLEX has overlapping sleeves at both ends, sealing the bellows throughout
  its 1.2–4 m travel. Extend/Collapse works with connected modules: the editor
  moves the attached branch; flight moves the joint anchor so physics pushes
  or pulls the payload. Ground tethers release during movement. Closed loops
  must be opened before resizing. Packed vessels, incomplete docking captures
  and payloads that cannot follow pause movement.
- HAB, CMD and EVA lamps gain a solid neck between bracket and housing.
  LAB gains the same stair light, following cabin lights by default, with an
  independent override and 0.03 EC/s consumption. The working light controller
  from dev.19 is retained.
- CMD is 25% longer: 2.15 m, with three seats using the stock Mk1-3 interior.
  Dry mass is 3.2 t and cost 17,310. Habitat volume is 7.25 m³; life-support
  supplies scale for the third crew member. Electrical and data capacities stay
  unchanged. Doors, stairs, leg mounts and attachment nodes follow the new hull.
- CMD roof exchanger blocks/fins are removed. Its dish has a solid front/back
  reflector, closed rim, feed and continuous mast support. Ring-color selections
  are regenerated for the revised mesh.
- Other eight models/configs remain identical to dev.19. No integrated RCS;
  VT-90 retains 90 kN, 180 LiquidFuel, 220 Oxidizer and whole-pod separation.

## Install and test

Close KSP, replace only GameData/RoosterWorksGroundModules, then restart.
Keep the core Station Modules folder. Station Support and skycrane need no
replacement. This build has not changed the installed game or saves.

Use a test craft with newly placed CMD and FLEX parts first: CMD length/nodes
changed. Check connected expansion/retraction with a freely movable payload,
both end seals, the science stair light, command ring colors, dish and seats.
Connected motion passes controller tests; actual KSP PhysX behavior still needs
in-game confirmation. A constrained payload may pause travel. No saved craft
migration is performed.

## Source and checks

Current packed source: Source/Equipment/RoosterWorks-Ground-dev20.blend, with
thirteen native scenes. Tools/build_v20.py uses Source/BaselineDev19 and the
adjacent rw-v075dev5 developer helpers. Earlier builders, baselines and Blender
files are historical references.

Build runtime: Tools/build-runtime.ps1; refresh: Tools/refresh_manifest.py.
Validate: Tools/validate.py, Tools/validate_v20.py, Tools/test-docking.ps1,
Tools/test-tube-motion.ps1 and Tools/test-light-release.ps1. Runtime compiles
against installed KSP assemblies. Tests exercise actual controller sources
with doubles, not full game physics/rendering. Native checks cover docking
frames, seals at five lengths, light beams/treads, command interfaces, ring
maps and protected-input hashes. Packaging verifies archive CRCs, source bytes,
checksums and identical addon payloads in both archives. Previews use native
geometry with illustrative Blender lighting.
''',encoding='utf-8')
(R/'Tools/test-flex.ps1').write_text("# Current connected-motion test entry point.\n$ErrorActionPreference='Stop'\n& (Join-Path $PSScriptRoot 'test-tube-motion.ps1')\n",encoding='utf-8')
p=R/'ROADMAP.md'
s=p.read_text(encoding='utf-8')
if '## Ground dev.20 test build' not in s:
 p.write_text(s+'''\n## Ground dev.20 test build

Sealed FLEX overlap boots and connected extension/retraction; science stair
light and solid lamp mounts; 25% longer three-seat command module with solid
dish and cleaned roof. Controller/native checks pass. Connected payload motion
still needs confirmation in KSP physics. Existing orbital roadmap stands.
''',encoding='utf-8')
logs=['validate.py.log','v20-validation.log','docking-tests.log','tube-motion-tests.log','light-release-tests.log']
(R/'validation.log').write_text('\n'.join('=== '+n+' ===\n'+(R/'Reports'/n).read_text(encoding='utf-8-sig') for n in logs),encoding='utf-8')
print('Updated dev.20 documentation and packaging gates')
