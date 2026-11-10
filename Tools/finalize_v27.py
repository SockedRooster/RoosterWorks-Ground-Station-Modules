from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R.parent;OUT=W/'outputs'
for version in (26,27):
 for line in (OUT/f'RoosterWorks-Ground-Modules-v0.8.0-dev.{version}-SHA256SUMS.txt').read_text().splitlines():
  digest,name=line.split('  ',1);assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest
note='''Latest ground build: **ground-hotpatch-v27 / v0.8.0-dev.27 TEST**, superseding
dev.26. Fixes floating NST/NSM/CEN equipment using closed hull-conforming
saddles, bolted cheeks and identical equipment on both sides. Removes only
occupied exterior equipment-pad nodes; existing legs, end docks, capacities,
recipes, dry masses and plugins retained. Corrects KSP full-tank pricing so
default empty prices are NST 24,000, NSM 36,000 and CEN 68,000; no negative
empty fuel price. All ground drills are in Harvesting; NST/CEN/NSM are in
Station Utility. Native/configuration, 21-pose bilateral rack/mount clearance,
positive fuel-load price, actual-source color and package CRC/manifest checks
pass. Live KSP confirmation pending. 28 parts / 20 native models. Editable
source: Source/Nuclear/RoosterWorks-Ground-dev27.blend. Previews: dev27 names.
Complete install/source ZIPs in outputs/. Previous dev.26 distributions kept;
historical source baselines remain build dependencies.

'''
p=W/'WORKSPACE_INDEX.md';t=p.read_text(encoding='utf-8-sig');start=t.index('Latest ground build:');end=t.index('Updated October',start);t=t[:start]+note+t[end:]
t=t.replace('| Ground Modules | 0.8.0-dev.26 | 0.8.0-dev.25 | ground-hotpatch-v26 / ground-hotpatch-v25 |','| Ground Modules | 0.8.0-dev.27 | 0.8.0-dev.26 | ground-hotpatch-v27 / ground-hotpatch-v26 |').replace('Updated October 16, 2026.','Updated October 17, 2026.')
p.write_text(t,encoding='utf-8')
p=W/'ROOSTERWORKS_DEVELOPMENT_CONTEXT.md';t=p.read_text(encoding='utf-8-sig');heading='# Current ground build — October 17, 2026: dev.27 mounts, bilateral equipment and pricing\n\n'
if not t.startswith(heading):p.write_text(heading+note+t,encoding='utf-8')
removed=[]
for suffix in ('HOT-PATCH.zip','HotPatch-Source.zip','SHA256SUMS.txt'):
 p=(OUT/('RoosterWorks-Ground-Modules-v0.8.0-dev.25-'+suffix)).resolve()
 assert p.parent==OUT.resolve() and p.is_relative_to(W.resolve())
 if p.exists():removed.append({'path':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});p.unlink()
(OUT/'Ground-dev27-retention.json').write_text(json.dumps({'kept':[27,26],'historical_source_baselines_retained':True,'removed':removed},indent=2)+'\n')
print('PASS current/previous archive hashes, workspace index and two-version distribution retention')
