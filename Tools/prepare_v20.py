from pathlib import Path
import shutil,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];OLD=R.parent/'ground-hotpatch-v19';baseline=R/'Source/BaselineDev19'
for role in ('HAB','AIR','LAB','FLEX','CMD'):
 for rel in (f'GameData/RoosterWorksGroundModules/Models/RW_GND_{role}.mu',f'GameData/RoosterWorksGroundModules/Parts/RW_GND_{role}.cfg',f'Reports/RW_GND_{role}.json'):
  dest=baseline/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(OLD/rel,dest)
for name in ('CommandKerbalism.cfg','ZZZCommandStorage075.cfg','GroundRingGeometry.cfg'):
 rel='GameData/RoosterWorksGroundModules/Compatibility/'+name;dest=baseline/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(OLD/rel,dest)
p=R/'Tools/create_equipment_blend.py';p.write_text(p.read_text().replace('RoosterWorks-Ground-dev19.blend','RoosterWorks-Ground-dev20.blend'))
(R/'Source/Equipment/README.md').write_text('''# Current dev.20 native source

RoosterWorks-Ground-dev20.blend has thirteen current scenes with packed images,
native transform hierarchy and actual light-frame directions. Unity X/Y/Z maps
to Blender X/Z/Y, reversing triangle winding. Photometry is illustrative.
Tools/build_v20.py is the authoritative geometry/config builder; it uses the
five affected native model snapshots in Source/BaselineDev19 and the adjacent
rw-v075dev5 developer helpers. Runtime ground legs/stairs and connected tube
motion are implemented by the C# sources and CFG transforms. Earlier models,
builders, baselines and tests are historical references, not current gates.
''',encoding='utf-8')
print('Bundled five affected native baselines and prepared dev.20 editable scenes')
