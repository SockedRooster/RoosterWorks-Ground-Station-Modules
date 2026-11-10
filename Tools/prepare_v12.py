from pathlib import Path
R=Path(__file__).resolve().parents[1]
for file in ('Tools/package.py','Tools/build_configs.py'):
 p=R/file;p.write_text(p.read_text().replace('v0.8.0-dev.11','v0.8.0-dev.12').replace("'BUILD':11","'BUILD':12"))
p=R/'Tools/snapshot_inputs.py';p.write_text(p.read_text().replace("'ground-hotpatch-v10'","'ground-hotpatch-v11'"))
for file in ('Tools/validate_endcap.py','Tools/validate_docking.py'):
 p=R/file;p.write_text(p.read_text().replace("['BUILD']==11","['BUILD']==12"))
p=R/'Tools/validate_roof_lighting.py';s=p.read_text().replace("OLD=W/'ground-hotpatch-v10'","OLD=W/'ground-hotpatch-v11'").replace("assert len(removed)==22","assert len(removed)==20").replace("sum(s.startswith('Roof maintenance rail') for s in removed)==2","sum(s.startswith('Roof maintenance rail') for s in removed)==0").replace("assert newfiles=={'Models/gnd_rw_safety_yellow.png'},newfiles","assert not newfiles,newfiles").replace("['BUILD']==11","['BUILD']==12");p.write_text(s)
p=R/'Tools/render_roof_lighting.py';p.write_text(p.read_text().replace('v0.8.0-dev.11','v0.8.0-dev.12').replace('Greenhouse / clear roof','Greenhouse / roof handrails restored').replace('Power module / clear roof','Power / roof handrails restored').replace('dev11-Roofs-Lighting','dev12-Roof-Handrails'))
