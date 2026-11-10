from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R.parent;OUT=W/'outputs'
for version in (30,31):
 for line in (OUT/f'RoosterWorks-Ground-Modules-v0.8.0-dev.{version}-SHA256SUMS.txt').read_text().splitlines():
  digest,name=line.split('  ',1);assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest
note='''Latest ground build: **ground-hotpatch-v31 / v0.8.0-dev.31 TEST**, superseding
dev.30. Adds DRILL-H2O Water Rig in Harvesting: blue frame/label, 250 L empty
Water buffer, 150 EC, 7.5 EC/s, 0.65 t and 4,800 funds empty. Existing stock
deployable mechanism, cooling and engineer bonuses. Mines mapped crustal Water;
45 positive installed map records verified; no distributions added. Requires
Station Modules and CRP. All dev.30 parts, native models and DLLs preserved.
460 offline preservation/configuration/manifest checks and archive checks pass;
live KSP testing pending. 29 parts / 20 native models. Guide WATER_DRILL.md;
preview Previews/dev31-Drill-H2O.png; editable owned frame in Source/WaterDrill/.
Install/source ZIPs in outputs/. Previous dev.30 distributions retained;
historical source dependencies kept. Station dev.11 is unchanged.

'''
p=W/'WORKSPACE_INDEX.md';t=p.read_text(encoding='utf-8-sig');start=t.index('Latest ground build:');end=t.index('Updated October',start)
t=t[:start]+note+t[end:];t=t.replace('| Ground Modules | 0.8.0-dev.30 | 0.8.0-dev.29 | ground-hotpatch-v30 / ground-hotpatch-v29 |','| Ground Modules | 0.8.0-dev.31 | 0.8.0-dev.30 | ground-hotpatch-v31 / ground-hotpatch-v30 |');p.write_text(t,encoding='utf-8')
p=W/'ROOSTERWORKS_DEVELOPMENT_CONTEXT.md';t=p.read_text(encoding='utf-8-sig');heading='# Current ground build — October 17, 2026: dev.31 Water drill\n\n'
if not t.startswith(heading):p.write_text(heading+note+t,encoding='utf-8')
removed=[]
for suffix in ('HOT-PATCH.zip','HotPatch-Source.zip','SHA256SUMS.txt'):
 p=(OUT/('RoosterWorks-Ground-Modules-v0.8.0-dev.29-'+suffix)).resolve()
 assert p.parent==OUT.resolve() and p.is_relative_to(W.resolve())
 if p.exists():removed.append({'path':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});p.unlink()
(OUT/'Ground-dev31-retention.json').write_text(json.dumps({'kept':[31,30],'historical_source_baselines_retained':True,'removed':removed},indent=2)+'\n')
print('PASS verified dev.31/dev.30 archives, workspace index and two-version distribution retention')
