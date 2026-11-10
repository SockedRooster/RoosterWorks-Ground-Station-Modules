from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parent/'ground-hotpatch-v31'
(R/'README.md').write_text('''# RoosterWorks Ground Modules — v0.8.0-dev.32 TEST

Adds command-controlled **Auto-Level Station** for connected legs and stairs.
Includes selectable SystemHeat loops/rebalanced heat for all ten drill rigs,
and repairs FLEX shape persistence and joint preload across time warp.

Close KSP, replace GameData/RoosterWorksGroundModules and restart. Keep Station
Modules installed. See TERRAIN_LEVELING_AND_WARP.md for controls and limits.
Runtime/configuration/archive checks pass; live KSP physics and final
ModuleManager acceptance remain pending.

## Prior development notes

'''+(B/'README.md').read_text())
s=(B/'Tools/package_v31.py').read_text();a=s.index("assert 'PASS dev.31");b=s.index('files=sorted',a)
s=s[:a]+'''for filename,expected in [('v32-validation.log','PASS dev.32: 366'),('v32-tube-tests.log','PASS 1833'),('v32-level-tests.log','PASS 4837'),('v32-compile.log','PASS compiled')]:
 assert expected in (R/'Reports'/filename).read_text(),filename
'''+s[b:]
s=s.replace('dev.31','dev.32').replace("'WATER_DRILL.md','CHECKSUMS", "'WATER_DRILL.md','TERRAIN_LEVELING_AND_WARP.md','CHECKSUMS")
(R/'Tools/package_v32.py').write_text(s)
(R/'Tools/package.py').write_text("from pathlib import Path\nexec(compile((Path(__file__).parent/'package_v32.py').read_text(),str(Path(__file__).parent/'package_v32.py'),'exec'))\n")
print('PASS dev.32 release notes and packaging prepared')
