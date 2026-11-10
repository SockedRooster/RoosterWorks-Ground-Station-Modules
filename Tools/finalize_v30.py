from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R.parent;OUT=W/'outputs'
for version in (29,30):
 for line in (OUT/f'RoosterWorks-Ground-Modules-v0.8.0-dev.{version}-SHA256SUMS.txt').read_text().splitlines():
  digest,name=line.split('  ',1);assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest
note='''Latest ground build: **ground-hotpatch-v30 / v0.8.0-dev.30 TEST**, superseding
dev.29. PWR now has matching three-accumulator banks on both sides with original
straps/valves; removes the console overlapping the middle unit, including its
screen, LEDs and lettering. Original front accumulators retained; opposite bank
is an exact 180-degree native copy. Only PWR.mu and version change in GameData.
Power variants/storage/generation, mass/cost, docking, legs, lights, ring maps
and all other assets preserved (including CMD roof repair and FLEX slider).
1,825 native/selection/preservation checks and 3,728 actual-source color
assertions pass; archives verified. Live KSP visual confirmation pending.
Editable source: Source/PowerSides/RW_GND_PWR-dev30.blend. Guide:
POWER_SIDE_EQUIPMENT.md; previews dev30-Power-After/Opposite.png. Complete
install/source ZIPs in outputs/. Previous dev.29 distributions retained;
historical source dependencies kept. Station dev.11 is unchanged.

'''
p=W/'WORKSPACE_INDEX.md';t=p.read_text(encoding='utf-8-sig');start=t.index('Latest ground build:');end=t.index('Updated October',start);t=t[:start]+note+t[end:]
t=t.replace('| Ground Modules | 0.8.0-dev.29 | 0.8.0-dev.28 | ground-hotpatch-v29 / ground-hotpatch-v28 |','| Ground Modules | 0.8.0-dev.30 | 0.8.0-dev.29 | ground-hotpatch-v30 / ground-hotpatch-v29 |');p.write_text(t,encoding='utf-8')
p=W/'ROOSTERWORKS_DEVELOPMENT_CONTEXT.md';t=p.read_text(encoding='utf-8-sig');heading='# Current ground build — October 17, 2026: dev.30 bilateral PWR equipment\n\n'
if not t.startswith(heading):p.write_text(heading+note+t,encoding='utf-8')
removed=[]
for suffix in ('HOT-PATCH.zip','HotPatch-Source.zip','SHA256SUMS.txt'):
 p=(OUT/('RoosterWorks-Ground-Modules-v0.8.0-dev.28-'+suffix)).resolve()
 assert p.parent==OUT.resolve() and p.is_relative_to(W.resolve())
 if p.exists():removed.append({'path':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});p.unlink()
(OUT/'Ground-dev30-retention.json').write_text(json.dumps({'kept':[30,29],'historical_source_baselines_retained':True,'removed':removed},indent=2)+'\n')
print('PASS verified dev.30/dev.29 archives, workspace index and two-version ground distribution retention')
