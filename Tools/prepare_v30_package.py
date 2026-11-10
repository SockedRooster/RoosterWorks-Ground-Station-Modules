from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'Tools/package_v29.py').read_text();a=s.index("assert 'PASS dev.29:");b=s.index('files=sorted',a)
s=s[:a]+'''assert 'PASS dev.30: 1825 ' in (R/'Reports/v30-validation.log').read_text()
assert 'PASS 3728 actual-map color assertions' in (R/'Reports/v30-color-tests.log').read_text()
render=(R/'Reports/v30-render.log').read_text()
assert 'PASS packed exact before/after power modules' in render
for label in ('Before','After','Opposite'):
 assert 'PASS rendered power '+label in render
 assert (R/f'Previews/dev30-Power-{label}.png').exists()
assert (R/'Source/PowerSides/RW_GND_PWR-dev30.blend').stat().st_size>1000000
'''+s[b:]
s=s.replace("'dev29-'","'dev29-','dev30-'",1).replace("'COMMAND_ROOF_FIX.md',","'COMMAND_ROOF_FIX.md','POWER_SIDE_EQUIPMENT.md',").replace("p.name.startswith('dev29-')","p.name.startswith('dev30-')").replace('v0.8.0-dev.29','v0.8.0-dev.30')
(R/'Tools/package_v30.py').write_text(s)
p=R/'Tools/package.py';p.write_text(p.read_text().replace('dev.29 command roof','dev.30 power side equipment').replace('package_v29.py','package_v30.py'))
p=R/'README.md';p.write_text('''# RoosterWorks Ground Modules — v0.8.0-dev.30 TEST

Ground PWR now has matching three-accumulator banks, straps and valves on both
sides. Removes the decorative service console overlapping its middle unit,
including the screen, LEDs and console lettering. Battery/reactor behavior,
power storage, mass, cost, docking, legs, lights and colors are unchanged.
Only PWR.mu and the version change in GameData. All other parts and runtime
binaries are retained, including the CMD roof fix and adjustable FLEX tube.

Close KSP, replace only GameData/RoosterWorksGroundModules and restart.
Keep Station Modules. Automated native/selection/color/archive checks pass;
live KSP visual confirmation remains pending. See POWER_SIDE_EQUIPMENT.md.
Editable scenes: Source/PowerSides/RW_GND_PWR-dev30.blend.

## Prior development notes

'''+p.read_text())
p=R/'ROADMAP.md';p.write_text(p.read_text()+'\nGround dev.30 TEST: matching three-unit PWR side equipment on both sides; removed overlapping decorative service console. See POWER_SIDE_EQUIPMENT.md.\n')
print('PASS prepared dev.30 documentation and package entry point')
