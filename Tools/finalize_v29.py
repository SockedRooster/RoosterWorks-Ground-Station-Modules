from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R.parent;OUT=W/'outputs'
for version in (28,29):
 for line in (OUT/f'RoosterWorks-Ground-Modules-v0.8.0-dev.{version}-SHA256SUMS.txt').read_text().splitlines():
  digest,name=line.split('  ',1);assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest
note='''Latest ground build: **ground-hotpatch-v29 / v0.8.0-dev.29 TEST**, superseding
dev.28. Closes CMD outer roof skin cutouts and seats the telemetry radome with
a curved socket, flange and bolts; adds a mast collar and two curved panel
gaskets. Every original CMD mesh/rig/light/collider/ring map is preserved.
Only CMD.mu and the version change in GameData. Runtime, partial FLEX slider,
all other parts, nuclear prices and VAB groups are unchanged. 2,395 native/
contact/preservation checks and 3,728 actual-source color assertions pass;
both archives checked. Live KSP visual confirmation pending. Editable native
before/after models: Source/CommandRoof/RW_GND_CMD-dev29.blend. Guide:
COMMAND_ROOF_FIX.md. Preview: Previews/dev29-Roof-After.png. Complete install/
source ZIPs in outputs/. Previous dev.28 distributions retained; historical
source baselines remain build dependencies. Station dev.11 is preserved.

'''
p=W/'WORKSPACE_INDEX.md';t=p.read_text(encoding='utf-8-sig');start=t.index('Latest ground build:');end=t.index('Updated October',start);t=t[:start]+note+t[end:]
t=t.replace('| Ground Modules | 0.8.0-dev.28 | 0.8.0-dev.27 | ground-hotpatch-v28 / ground-hotpatch-v27 |','| Ground Modules | 0.8.0-dev.29 | 0.8.0-dev.28 | ground-hotpatch-v29 / ground-hotpatch-v28 |');p.write_text(t,encoding='utf-8')
p=W/'ROOSTERWORKS_DEVELOPMENT_CONTEXT.md';t=p.read_text(encoding='utf-8-sig');heading='# Current ground build — October 17, 2026: dev.29 command roof closure\n\n'
if not t.startswith(heading):p.write_text(heading+note+t,encoding='utf-8')
removed=[]
for suffix in ('HOT-PATCH.zip','HotPatch-Source.zip','SHA256SUMS.txt'):
 p=(OUT/('RoosterWorks-Ground-Modules-v0.8.0-dev.27-'+suffix)).resolve()
 assert p.parent==OUT.resolve() and p.is_relative_to(W.resolve())
 if p.exists():removed.append({'path':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});p.unlink()
(OUT/'Ground-dev29-retention.json').write_text(json.dumps({'kept':[29,28],'historical_source_baselines_retained':True,'removed':removed},indent=2)+'\n')
print('PASS verified dev.29/dev.28 archives, workspace index and two-version ground distribution retention')
