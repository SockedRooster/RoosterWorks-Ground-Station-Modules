from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R.parent;OUT=W/'outputs'
for version in (31,32):
 for line in (OUT/f'RoosterWorks-Ground-Modules-v0.8.0-dev.{version}-SHA256SUMS.txt').read_text().splitlines():
  digest,name=line.split('  ',1);assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest
note='''Latest ground build: **ground-hotpatch-v32 / v0.8.0-dev.32 TEST**, superseding
dev.31. Adds command Auto-Level Station: connected legs/stairs fit terrain,
limited common physics leveling, saved foot/stair trims, tether handoff and
warp/movement/FLEX guards. 8° maximum tilt with finite support/stair travel;
no per-part teleport. FLEX commits packed vessel positions before rails/save
and restores unloaded joint anchors without preload; visible pose maintained.
All ten drill rigs gain SystemHeat loop selection and 7.5 kW process heat,
350 K outlet, full efficiency through 400 K, shutdown at 650 K; stock heating
removed only when SystemHeat installed; installed Kerbalism bridge supported.
29 parts / 20 native models. 4,837 leveling, 1,833 FLEX and 366 preservation/
thermal API checks pass; runtime compiled against KSP 1.12.5; archives verified.
Live KSP physics and final ModuleManager acceptance remain pending. Guide
TERRAIN_LEVELING_AND_WARP.md. Full install/source ZIPs in outputs/. Previous
dev.31 distributions retained; source dependencies kept. Station dev.11 unchanged.

'''
p=W/'WORKSPACE_INDEX.md';t=p.read_text(encoding='utf-8-sig');a=t.index('Latest ground build:');b=t.index('Updated October',a);t=t[:a]+note+t[b:]
t=t.replace('| Ground Modules | 0.8.0-dev.31 | 0.8.0-dev.30 | ground-hotpatch-v31 / ground-hotpatch-v30 |','| Ground Modules | 0.8.0-dev.32 | 0.8.0-dev.31 | ground-hotpatch-v32 / ground-hotpatch-v31 |');p.write_text(t,encoding='utf-8')
p=W/'ROOSTERWORKS_DEVELOPMENT_CONTEXT.md';t=p.read_text(encoding='utf-8-sig');heading='# Current ground build — October 17, 2026: dev.32 leveling, heat loops and FLEX warp\n\n'
if not t.startswith(heading):p.write_text(heading+note+t,encoding='utf-8')
removed=[]
for suffix in ('HOT-PATCH.zip','HotPatch-Source.zip','SHA256SUMS.txt'):
 p=(OUT/('RoosterWorks-Ground-Modules-v0.8.0-dev.30-'+suffix)).resolve()
 assert p.parent==OUT.resolve() and p.is_relative_to(W.resolve())
 if p.exists():removed.append({'path':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});p.unlink()
(OUT/'Ground-dev32-retention.json').write_text(json.dumps({'kept':[32,31],'historical_source_baselines_retained':True,'removed':removed},indent=2)+'\n')
print('PASS verified dev.32/dev.31 archives, workspace index and two-version distribution retention')
