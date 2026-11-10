from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'Tools/package_v28.py').read_text()
start=s.index("assert 'PASS dev.28:");end=s.index('files=sorted',start)
s=s[:start]+'''assert 'PASS dev.29: 2395 ' in (R/'Reports/v29-validation.log').read_text()
assert 'PASS 3728 actual-map color assertions' in (R/'Reports/v29-color-tests.log').read_text()
render=(R/'Reports/v29-render.log').read_text()
assert 'PASS packed exact before/after command roof models' in render
for label in ('Before','After'):
 assert 'PASS rendered command roof '+label in render
 assert (R/f'Previews/dev29-Roof-{label}.png').exists()
assert (R/'Source/CommandRoof/RW_GND_CMD-dev29.blend').stat().st_size>1000000
'''+s[end:]
s=s.replace("'dev27-'","'dev27-','dev29-'").replace("'ADJUSTABLE_CREW_TUBE.md',","'ADJUSTABLE_CREW_TUBE.md','COMMAND_ROOF_FIX.md',").replace("or p.name in docs]","or p.name in docs or (p.parent.name=='Previews' and p.name.startswith('dev29-'))]").replace('v0.8.0-dev.28','v0.8.0-dev.29')
(R/'Tools/package_v29.py').write_text(s)
p=R/'Tools/package.py';s=p.read_text().replace('dev.28 adjustable crew tube','dev.29 command roof').replace('package_v28.py','package_v29.py');p.write_text(s)
p=R/'README.md';s=p.read_text();header='''# RoosterWorks Ground Modules — v0.8.0-dev.29 TEST

Closes gaps in the CMD roof skin and seats its telemetry cone, antenna mast
and two roof panels with curved mounting bases. Only command model geometry
and the version file change. All previous parts, controls, storage, prices and
VAB placement are retained, including the dev.28 adjustable FLEX crew tube.
See COMMAND_ROOF_FIX.md for details and before/after model previews.

Close KSP, replace only GameData/RoosterWorksGroundModules, and restart.
Keep Station Modules. Automated native/contact/color/archive checks pass;
live KSP visual confirmation remains pending.

Builder: Tools/build_v29.py. Validator: Tools/validate_v29.py.
Editable source: Source/CommandRoof/RW_GND_CMD-dev29.blend.

## Prior development notes

''';p.write_text(header+s)
p=R/'ROADMAP.md';p.write_text(p.read_text()+'\nGround dev.29 TEST: restored CMD outer roof skin and seated communications/roof-panel fittings. Existing runtime, models and gameplay retained. See COMMAND_ROOF_FIX.md.\n')
print('PASS prepared dev.29 metadata and package entry point')
