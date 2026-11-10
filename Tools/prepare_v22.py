from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];W=R.parent
p=R/'Reports/READ_ONLY_INPUTS.json';hashes=json.loads(p.read_text())
for f in (W/'ground-hotpatch-v21').rglob('*'):
 if f.is_file() and '__pycache__' not in f.parts:hashes[f.relative_to(W).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
p.write_text(json.dumps(hashes,indent=2)+'\n')
p=R/'Tools/package.py';s=p.read_text().replace("'PASS dev.21: 13 models'", "'PASS dev.22: seven exact dedicated capacities'").replace('Reports/v21-validation.log','Reports/v22-validation.log').replace('v0.8.0-dev.21-','v0.8.0-dev.22-')
if '1883 ground-logistics' not in s:s=s.replace('report={};payloads=[]',"assert 'PASS 1883 ground-logistics' in (R/'Reports/ground-logistics-tests.log').read_text()\nreport={};payloads=[]")
p.write_text(s)
(R/'README.md').write_text('''# RoosterWorks Ground Modules — v0.8.0-dev.22 TEST

Requires KSP 1.12.5, ModuleManager and Station Modules v0.7.5-dev.5.
Storage selection requires Kerbalism Default profile and Community Resource Pack.
This update applies to the ground addon.

## LOG capacities

| Resource | Dedicated | Mixed supplies |
|---|---:|---:|
| Food | 1,800 | 360 |
| Water | 1,700 | 340 |
| Oxygen | 350,000 | 70,000 |
| Nitrogen | 200,000 | 20,000 |
| Ammonia | 40,000 | 4,000 |
| Carbon Dioxide | 75,000 | 7,500 |
| Hydrogen | 750,000 | 75,000 |

Mixed supplies uses 20% of each dedicated Food/Water/Oxygen capacity and 10%
of each other capacity: one total capacity budget, with 60% for priority supplies.
All seven supply choices start full. Existing dedicated Waste/WasteWater choices
remain 520 units each and start empty; mixed supplies carries the seven supplies.
Stock item inventory remains separate.

The ground LOG has its own controller/profile, adding Carbon Dioxide/Hydrogen
choices without changing orbital LOG profiles or the core plugin. Editor-only
switching removes the previous managed cargo; repeated refreshes preserve
depletion/fill fractions. Flight resources are not reconciled or refilled.

## Utility habitat removal

Ground LOG and PWR no longer have a Kerbalism Habitat, Shielding or internal
Atmosphere/WasteAtmosphere/MoistAtmosphere. The obsolete habitat-radiation sensor
is removed too. Cargo Nitrogen, other stored supplies, electrical capacity and
nuclear fuel/reactor variants are preserved. Both remain crewless.

## Install and checks

Close KSP, replace only GameData/RoosterWorksGroundModules, then restart. Keep
the core Station Modules folder. Use newly placed LOG/PWR parts to check all
storage choices and removal of Habitat/Shielding in the part menu. No existing
craft or flight-save resources are migrated. The installed game/saves were not
modified. Full in-game confirmation is pending.

All thirteen models, textures, other part configs and seven previous ground
controllers match dev.21, including strengthened FLEX joints and ring fixes.
Current geometry remains Source/Equipment/RoosterWorks-Ground-dev21.blend;
previews are unchanged dev.21 geometry. No new geometry was needed.

Current builder: Tools/build_v22.py. New runtime source:
Source/GroundLogisticsContents.cs. Compile: Tools/build-runtime.ps1. Validate:
Tools/test-ground-logistics.ps1 and Tools/validate_v22.py after refreshing the
manifest with Tools/refresh_manifest.py. The source kit requires adjacent
rw-v075dev5 developer helpers for config parsing. Historical builders/reports
remain reference material. Current runtime compiles against KSP 1.12.5.
1,883 actual-source selector assertions cover all choice pairs, cleanup,
unrelated resources, editor refresh, no refill, missing resources and flight
preservation. Scoped config validation checks capacities, mixed allocation,
fallbacks, deletion scope, unchanged assets and hashes; offline checks do not
run the full ModuleManager/game load. Both archives verify CRCs/checksums and
identical install payloads.
''',encoding='utf-8')
print('Prepared dev.22 documentation, protected dev.21 hashes and package gates')
