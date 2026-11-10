from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'Tools/create_mineral_drill_blend.py').read_text()
s=s.replace("specs=json.loads((R/'Reports/DEV25_MINERAL_DRILLS.json').read_text())", "specs=[json.loads((R/'Reports/DEV31_WATER_DRILL.json').read_text())]")
s=s.replace("Source/MiningVariants", "Source/WaterDrill").replace('RW_MineralDrillFrames.blend','RW_WaterDrillFrame.blend').replace('packed eight editable specialist frames','packed editable water drill frame').replace('Previews/dev25-Drill-', 'Previews/dev31-Drill-')
(R/'Tools/create_water_drill_blend.py').write_text(s)
s=(R/'Tools/package_v30.py').read_text();start=s.index("assert 'PASS dev.30:");end=s.index('files=sorted',start)
s=s[:start]+"assert 'PASS dev.31 Water drill' in (R/'Reports/v31-validation.log').read_text()\nassert 'PASS rendered specialist Water' in (R/'Reports/v31-render.log').read_text()\n"+s[end:]
s=s.replace("'dev30-'))", "'dev30-','dev31-'))").replace("'POWER_SIDE_EQUIPMENT.md','CHECKSUMS", "'POWER_SIDE_EQUIPMENT.md','WATER_DRILL.md','CHECKSUMS")
s=s.replace("startswith('dev30-','dev31-')", "startswith('dev31-')").replace("startswith('dev30-')", "startswith('dev31-')").replace('dev.30','dev.31').replace('==28','==29').replace('28 parts','29 parts')
(R/'Tools/package_v31.py').write_text(s)
(R/'Tools/package.py').write_text("from pathlib import Path\nexec(compile((Path(__file__).parent/'package_v31.py').read_text(),str(Path(__file__).parent/'package_v31.py'),'exec'))\n")
doc='''# RoosterWorks Water Drill — dev.31

DRILL-H2O is a separate crewless rig in Harvesting alongside the other drills.
It mines underground Water using existing Community Resource Pack crustal maps.
Scan for Water and choose a site with nonzero abundance; water availability
depends on the installed planet maps. Ocean and atmospheric water are separate.

The rig has the existing half-scale deployable drill, 2.71 m contact reach,
engineer bonuses and core heat. Provide 7.5 EC/s, radiator cooling and ground
contact. Onboard storage: 150 EC and 250 units / 250 L of Water, initially empty.
Connect external Water storage for sustained extraction. Dry mass: 0.65 t;
empty price: 4,800 funds. Output varies with abundance, engineer and temperature.

Requires Station Modules and Community Resource Pack, as with the other CRP
mineral drills. No resource distribution or conversion recipe is added.
No extra plugin is needed. Existing parts and runtime binaries are preserved.

Close KSP, replace GameData/RoosterWorksGroundModules with this complete package,
then restart. Do not install a second copy alongside the previous version.
Offline configuration, preservation and archive checks pass; live KSP testing
remains pending. Preview: Previews/dev31-Drill-H2O.png. Editable owned frame:
Source/WaterDrill/RW_WaterDrillFrame.blend. Stock drill assets are referenced
from KSP and are not redistributed or embedded in the saved source scene.
'''
(R/'WATER_DRILL.md').write_text(doc)
p=R/'README.md';p.write_text('# RoosterWorks Ground Modules — v0.8.0-dev.31 TEST\n\nAdds the DRILL-H2O Water Rig in Harvesting, with blue frame/label, existing\ndeployable drill and a 250 L empty Water buffer. Uses installed crustal Water\nmaps; 7.5 EC/s, cooling and ground contact required. See WATER_DRILL.md.\n\nClose KSP, replace GameData/RoosterWorksGroundModules and restart.\nOffline checks pass; in-game testing remains pending.\n\n## Prior development notes\n\n'+p.read_text())
print('PASS prepared water documentation, renderer and packaging')
