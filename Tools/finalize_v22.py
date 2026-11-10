from pathlib import Path
R=Path(__file__).resolve().parents[1];W=R.parent
logs=['runtime-build.log','ground-logistics-tests.log','v22-validation.log']
(R/'validation.log').write_text('\n'.join('=== '+n+' ===\n'+(R/'Reports'/n).read_text(encoding='utf-8-sig') for n in logs),encoding='utf-8')
p=R/'ROADMAP.md';s=p.read_text(encoding='utf-8')
if '## Ground dev.22' not in s:p.write_text(s+'\n## Ground dev.22\n\nGround LOG dedicated capacities rebalanced; mixed supplies prioritize Food/Water/Oxygen. Added CO2/Hydrogen choices. Ground LOG/PWR have no habitat or shielding. No geometry/roadmap scope change.\n',encoding='utf-8')
p=W/'WORKSPACE_INDEX.md';s=p.read_text(encoding='utf-8');start=s.index('Latest ground build:');end=s.index('Updated October',start)
s=s[:start]+'''Latest ground build: **ground-hotpatch-v22 / v0.8.0-dev.22 TEST**, superseding
dev.21. Ground LOG has seven revised dedicated capacities, 60% mixed allocation
to Food/Water/Oxygen, and CO2/Hydrogen selector choices. Ground LOG/PWR have no
habitat or shielding. All thirteen models and seven existing controllers match
dev.21. New ground-only selector compiles with KSP 1.12.5; 1,883 source assertions
and scoped configuration/hash checks pass. Install/source ZIPs use dev.22 names
in outputs/. Current geometry remains the dev21 packed Blender source.

'''+s[end:];s=s.replace('| Ground Modules | 0.8.0-dev.21 | 0.8.0-dev.20 | ground-hotpatch-v21 / ground-hotpatch-v20 |','| Ground Modules | 0.8.0-dev.22 | 0.8.0-dev.21 | ground-hotpatch-v22 / ground-hotpatch-v21 |');p.write_text(s,encoding='utf-8')
p=W/'ROOSTERWORKS_DEVELOPMENT_CONTEXT.md';s=p.read_text(encoding='utf-8');p.write_text('''Latest ground build: ground-hotpatch-v22 / v0.8.0-dev.22 TEST. Ground LOG dedicated capacities: Food1800, Water1700, Oxygen350000, Nitrogen200000, Ammonia40000, CarbonDioxide75000, Hydrogen750000. Mixed supplies 20% of each priority Food/Water/Oxygen, 10% each remaining four: 360/340/70000/20000/4000/7500/75000. Waste/WasteWater remain dedicated empty520, excluded from mixed. Added unique ModuleRWGroundLogisticsContents and profile RW_GND_LOG, compiled into ground DLL, 10 selector choices including CO2/Hydrogen; no changes to core selector/profiles. Seven older ground controllers and all 13 models/textures/part configs byte-identical21. Removed own LOG Habitat-creation patch and added exact late LOG/PWR cleanup of all Habitat, Shielding, Atmosphere/WasteAtmosphere/MoistAtmosphere, habitat_radiation sensor. Cargo Nitrogen, reactor resources and EC retained. No flight inventory migrations/refills; existing editor/save parts may need replacement to drop persisted resources. Actual-source1883 assertions and scoped config/hash checks pass, runtime compiles KSP1.12.5. In-game confirmation pending. Source geometry remains dev21 Blender. Current builder Tools/build_v22.py. Both archives under outputs dev.22. No core/game/save/artist/skycrane modifications or publication. Prior notes below.

'''+s,encoding='utf-8')
print('Finalized dev.22 validation summary and workspace notes')
