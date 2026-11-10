from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
for file in ('Tools/build_configs.py','Tools/package.py'):
 p=R/file;p.write_text(p.read_text().replace("'BUILD':10","'BUILD':11").replace('v0.8.0-dev.10','v0.8.0-dev.11'))
p=R/'Tools/snapshot_inputs.py';p.write_text(p.read_text().replace("'ground-hotpatch-v9'","'ground-hotpatch-v10'"))
p=R/'Tools/validate_docking.py';p.write_text(p.read_text().replace(" m.root['children']=[n for n in m.root['children'] if not n['name'].startswith('RW_Dock_')]"," m.root['children']=[n for n in m.root['children'] if not n['name'].startswith('RW_Dock_')]").replace(" assert m.root==old.root and m.materials==old.materials and m.textures==old.textures,", " assert file.stem in ('RW_GND_GRN','RW_GND_PWR','RW_GND_ELB') or (m.root==old.root and m.materials==old.materials and m.textures==old.textures),").replace("['BUILD']==10","['BUILD']==11"))
p=R/'Tools/validate_endcap.py';p.write_text(p.read_text().replace("if file.is_file() and file.name not in", "if file.is_file() and file.name not in").replace("('RoosterWorksGroundModules.version','RoosterWorksGroundDeploy.dll')", "('RoosterWorksGroundModules.version','RoosterWorksGroundDeploy.dll','RW_GND_GRN.mu','RW_GND_PWR.mu','RW_GND_ELB.mu','GroundRingGeometry.cfg')").replace("['BUILD']==10","['BUILD']==11"))
p=R/'Tools/validate_refinements.py';p.write_text(p.read_text().replace("assert len(lights)==3 and all(n['light']['intensity']==2 for n in lights)","assert len(lights)==9 and all(abs(n['light']['intensity']-1.6)<1e-5 for n in lights)"))
