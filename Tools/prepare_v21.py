from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
for name in ('create_equipment_blend.py','render_v20.py'):
 p=R/'Tools'/name;s=p.read_text().replace('dev20','dev21')
 if name=='render_v20.py':
  s=s.replace("if '--command-only' in sys.argv:views=views[:1]", "views=[v for v in views if v[0]=='FLEX']")
  (R/'Tools/render_v21.py').write_text(s)
 else:p.write_text(s)
p=R/'Tools/package.py';s=p.read_text().replace("'PASS dev.20: 13 models'", "'PASS dev.21: 13 models'").replace('v20-validation.log','v21-validation.log').replace('PASS 1036','PASS 1052').replace('dev20','dev21').replace('dev.20-','dev.21-');p.write_text(s)
p=R/'Reports/READ_ONLY_INPUTS.json';hashes=json.loads(p.read_text())
for f in (R.parent/'ground-hotpatch-v20').rglob('*'):
 if f.is_file() and '__pycache__' not in f.parts:hashes[f.relative_to(R.parent).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
p.write_text(json.dumps(hashes,indent=2)+'\n')
p=R/'README.md';s=p.read_text(encoding='utf-8');s=s.replace('v0.8.0-dev.20 TEST','v0.8.0-dev.21 TEST').replace('RoosterWorks-Ground-dev20.blend','RoosterWorks-Ground-dev21.blend').replace('Tools/build_v20.py uses Source/BaselineDev19','Tools/build_v21.py uses Source/BaselineDev20').replace('Tools/validate_v20.py','Tools/validate_v21.py')
s=s.replace('## Changes\n','''## Changes in dev.21

- FLEX connection force/torque thresholds increase from 350 to 3500. Both end
  fittings use rigid linear/angular constraints with positional projection,
  reapplied to new docking joints and after loading. The moving anchor still
  actuates connected extension/retraction. Only joints touching FLEX change.
- Each end boot is now 15 mm outside the old steel cap radius, with bands a
  further 7 mm out. The front annulus is recessed 10 mm behind the cap face.
  This removes the overlapping surfaces responsible for the mottled rings.
  White/Grey finish, ring controls, docking, lights and tube travel are retained.
- Other twelve native models/configs and all compatibility maps match dev.20.

## Retained dev.20 changes
''')
s=s.replace('Other eight models/configs remain identical to dev.19.', 'The other eight models/configs remain identical to dev.19.')
p.write_text(s,encoding='utf-8')
p=R/'ROADMAP.md';s=p.read_text(encoding='utf-8')
if '## Ground dev.21' not in s:p.write_text(s+'\n## Ground dev.21\n\nFLEX connection reinforcement and end-ring overlap correction. No roadmap scope change.\n',encoding='utf-8')
p=R/'Source/Equipment/README.md';p.write_text('Current packed source: RoosterWorks-Ground-dev21.blend, thirteen native-equivalent scenes. Built by Tools/create_equipment_blend.py after Tools/build_v21.py. Prior files are historical.\n')
print('Prepared dev.21 sources, protected dev.20 hashes and package gates')
