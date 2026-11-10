from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'Tools/validate_roof_lighting.py';s=p.read_text().replace("OLD=W/'ground-hotpatch-v11'","OLD=W/'ground-hotpatch-v12'").replace("==12","==13")
s=s.replace("allowed={'Models/RW_GND_GRN.mu','Models/RW_GND_PWR.mu','Compatibility/GroundRingGeometry.cfg','RoosterWorksGroundModules.version'}","allowed={f'Models/RW_GND_{role}.mu' for role in ('HAB','LAB','CMD','LOG','GRN','AIR','PWR','TUB')}|{'RoosterWorksGroundModules.version'}")
p.write_text(s)
p=R/'Tools/validate_docking.py';s=p.read_text().replace("if not n['name'].startswith('RW_Dock_')]","if not n['name'].startswith('RW_Dock_') and n['name']!='RW_RoofRailMounts']");p.write_text(s)
p=R/'Tools/validate_endcap.py';s=p.read_text().replace("OLD=W/'ground-hotpatch-v8'","OLD=W/'ground-hotpatch-v12'")
s=s.replace("'RW_GND_ELB.mu','GroundRingGeometry.cfg'","'RW_GND_ELB.mu','RW_GND_HAB.mu','RW_GND_LAB.mu','RW_GND_CMD.mu','RW_GND_LOG.mu','RW_GND_AIR.mu','RW_GND_TUB.mu','GroundRingGeometry.cfg'")
p.write_text(s)
p=R/'README.md';s=p.read_text().replace('v0.8.0-dev.12 TEST','v0.8.0-dev.13 TEST',1).replace('## Changes in dev.12','## Retained changes in dev.12',1)
intro='''## Changes in dev.13

Added black mounting shoes and sockets beneath all 32 roof-handrail posts
on HAB, LAB, CMD, LOG, GRN, AIR, PWR and TUB. These use the same graphite
material as the elbow connections. Each mount penetrates the curved hull
and overlaps its original rail post, closing the visible gap. Original
handrails remain intact; the elbow, hub and endcap remain unchanged.

All original model nodes, textures, materials, collisions and animations are
preserved. No part configuration, runtime, docking, lighting, resource,
tether or finish/ring behavior changes. The sockets remain black with either
exterior finish. Preview: `Previews/RoosterWorks-Ground-dev13-Roof-Sockets.jpg`.

To reproduce the sockets after a clean model export and docking-frame pass,
run `Tools/collect_roof_posts.py` in Blender, then `Tools/add_roof_mounts.py`
once with Python. The collector reads the protected artist Blender files
without saving them. Run `Tools/validate_roof_mounts.py` to verify all post
and hull overlaps and exact preservation of the accepted dev.12 payload.

'''
s=s.replace('## Retained changes in dev.12',intro+'## Retained changes in dev.12',1).replace('audit protects `ground-hotpatch-v11`','audit protects `ground-hotpatch-v12`')
p.write_text(s,encoding='utf-8')
print('Updated dev.13 documentation and retained-feature validation scope')
