from pathlib import Path
R=Path(__file__).resolve().parents[1]
for file in ('Tools/package.py','Tools/build_configs.py'):
 p=R/file;p.write_text(p.read_text().replace('v0.8.0-dev.12','v0.8.0-dev.13').replace("'BUILD':12","'BUILD':13"))
p=R/'Tools/snapshot_inputs.py';p.write_text(p.read_text().replace("'ground-hotpatch-v11'","'ground-hotpatch-v12'"))
for file in ('Tools/validate_endcap.py','Tools/validate_docking.py'):
 p=R/file;p.write_text(p.read_text().replace("['BUILD']==12","['BUILD']==13"))
